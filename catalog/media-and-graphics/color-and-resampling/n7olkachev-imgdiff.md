# imgdiff (n7olkachev)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Multi-threaded Go pixel-diff CLI and package with pixelmatch-style YIQ threshold; README says 3-4.5x faster than 2020 odiff, but odiff v2 matched it.

| | |
|---|---|
| **Beats** | odiff v1 (2020); PR #5 re-measured against odiff v2 |
| **Claimed result** | Obsolete: README (2020-2021) cypress image imgdiff 1.442 s vs odiff v1 6.475 s (4.49x), water image 1.908 s vs 6.016 s (3.15x), '3X faster'. imgdiff PR #5 (odiff author, January 2021) on the same cypress pair: odiff v2 1.194 s vs imgdiff 1.146 s (parity, imgdiff on all cores) and imgdiff single-thread 2.616 s, so odiff v2 is about 2.19x faster per thread (derived from page data). No measurement against the current Zig/SIMD odiff. |
| **Workload** | Pixel-by-pixel diff of a Cypress screenshot pair (3446 x 10728) and a water image pair (8400 x 4725) from the odiff repo, writing an output image, on an 8-core Linux laptop. |
| **Metric** | latency |
| **Hardware** | Linux, Intel Core i7-4700HQ @ 2.40GHz (README says '8 cores'; the i7-4700HQ has 4 cores and 8 hardware threads, and imgdiff starts runtime.NumCPU() goroutines) |
| **Compiler and flags** | Go (go.mod says go 1.14); toolchain version and build flags not stated |
| **Adoption** | 1.7k stars |
| **Last commit** | 2021-03-25 |
| **Links** | [repository](https://github.com/n7olkachev/imgdiff) · [benchmark](https://raw.githubusercontent.com/n7olkachev/imgdiff/master/readme.md) |

## Verdict

The README's hyperfine runs on a Linux Core i7-4700HQ (4 cores, 8 threads) time multi-threaded imgdiff against an unversioned late-2020 odiff (v1). On the 3446x10728 cypress pair imgdiff took 1.442 s against odiff's 6.475 s (4.49x); on the 8400x4725 water pair, 1.908 s against 6.016 s (3.15x). The Go version, flags and harness are not given, the two tools did different output work, and the benchmark-era binary wrote truncated PNGs. All four odiff test PNGs are 8-bit RGBA and fully opaque (alpha channels decoded during enrichment: minimum alpha 255), so the color bug does not change these counts. The gap did not last: odiff's author re-ran the cypress pair in PR #5 after odiff v2 removed a dependency's 'massive data copying' and measured odiff 1.194 s against imgdiff 1.146 s, with imgdiff at 2.616 s when single-threaded.

## Use it when

- Go test suites that want a small MIT, pure-Go image comparison (about 70 lines in pkg/imgdiff plus a 40-line YIQ helper) instead of shelling out to a native binary.
- Opaque 8-bit PNG screenshots of identical size (the case it handles correctly), when you need only a differing-pixel count and a red mask.
- Multi-core CI runners diffing very large screenshots, where spreading rows across cores lowers wall time compared with a one-thread tool.

## Skip it when

- Picking it as faster than odiff: in imgdiff PR #5 (January 2021), odiff's author timed odiff v2 at 1.194 s and imgdiff at 1.146 s on the same cypress pair (parity). With imgdiff limited to one thread, it took 2.616 s, so odiff was 2.19x faster per core. odiff has since been rewritten in Zig with SSE2/AVX2/AVX512/NEON.
- JPEG, 16-bit PNG or semi-transparent images: the color delta reads the wrong byte of Go's 16-bit RGBA() values (see gotchas), so differences there are miscounted.
- Images that can differ in size: it only iterates image1's bounds. A larger compare image with an identical overlap reports 'equal' unless --fail-on-layout is passed (issue #13, open since 2024-12-06).
- Anti-aliasing-tolerant comparisons, ignore regions, or diffs rendered over the base image the way odiff and pixelmatch do: none of these are implemented.
- Single-core containers or anything needing a maintained dependency: the speed comes from goroutines, and the project has been dormant since 2021-03-25 with 2024 bug reports unanswered.

## How it is fast

Mostly by using all cores. cmd/main.go decodes both images in parallel goroutines with Go's standard image/png and image/jpeg. Diff() then interleaves rows over runtime.NumCPU() goroutines (row y goes to goroutine y mod NumCPU) and counts with an atomic add. Per pixel it compares the two color.Color interface values and runs the pixelmatch YIQ delta (0.5053 y^2 + 0.299 i^2 + 0.1957 q^2 against 35215 \* threshold^2) only when they differ. The mostly transparent mask is written with png.BestSpeed. Nothing is SIMD: pixels go through the generic image.At interface, and the author writes that it 'isn't as fast as a tool like this should be' and that image decoding and encoding take most of the time.

## Compared with alternatives

Against odiff, the only catalogued sibling doing the same job, pick imgdiff only if you need an in-process pure-Go call on opaque 8-bit PNGs and can use several cores. odiff matched it in v2, has anti-aliasing detection, ignore regions and cross-format input, and is maintained, so it is the default choice.

## Integration

| | |
|---|---|
| **Form** | module (Go package github.com/n7olkachev/imgdiff/pkg/imgdiff) plus a CLI binary (prebuilt binaries on GitHub releases) |
| **Dependencies** | Go standard library (image, image/png, image/jpeg) for the package; the CLI adds alexflint/go-arg v1.3.0 and logrusorgru/aurora v2.0.3 |
| **Minimum toolchain** | Go 1.14 per go.mod; the Go toolchain used for the README benchmark is not stated |
| **Platforms** | any Go target; scripts/build.sh cross-compiles windows, linux and darwin for amd64 and 386 only (no arm64 builds) |
| **Thread safety** | not documented; each Diff call starts its own NumCPU goroutines, writes to disjoint rows of a fresh output image and shares no package state |
| **Drop-in for the baseline** | no |

## Gotchas

- Color bug: pkg/yiq/delta.go normalize() turns color.RGBA()'s 16-bit channels into bytes with uint8(r), which keeps the low byte instead of r &gt;&gt; 8. The result is right only for opaque 8-bit pixels, where RGBA() returns v\*0x101. It is wrong for JPEG: Go's own ycbcr.go comment shows YCbCr{0x7f,0x7f,0x7f}.RGBA() = 0x7e18 0x808d 0x7db9, so imgdiff sees 0x18, 0x8d, 0xb9 instead of 0x7e, 0x80, 0x7d. It is also wrong for 16-bit PNGs and for partially transparent pixels, whose values come back premultiplied.
- The README's Download link points to v1.0.0. In that build main.go defers writer.Flush() and f.Close() and then calls os.Exit(1), which skips deferred calls. Diff PNGs therefore came out truncated, or zero bytes when the whole file fit in bufio's buffer (issue #8: about 1-2 in 100 diffs). The fix is in v1.0.2 (commit 3eef05c, 2021-03-25). os.Create and png.Encode errors are still ignored, so a bad output path gives exit 1 and no file.
- --diff-image copies base pixels only where the two pixel values are exactly equal. Pixels that differ but fall under the threshold stay transparent, so the 'diff image' has holes.
- The loops use &lt;= on Bounds().Max, so they run one row and one column past the image (issue #12, open). It is harmless today because image.At returns zero outside the bounds, but it adds an extra out-of-range row of work to every goroutine pass.

## Known shortcomings

- Multi-core (NumCPU goroutines on an i7-4700HQ, 4 cores and 8 threads; the README says 8 cores) against single-threaded odiff, with a different default output (transparent mask, png.BestSpeed); the benchmark-era main.go (1be7ce7) skipped the deferred Flush through os.Exit(1), so the diff PNG was truncated until the 2021-03-25 fix; the odiff compared is old and unversioned (6.475 s against odiff's own 1.168 s on the same pair). Image diffing is a weak fit for colour-and-resampling.
- Enricher (e116, 2026-10-05): speed claim obsolete. The README's 4.49x/3.15x was against odiff v1 (whose dependency did 'massive data copying'); imgdiff PR #5 by the odiff author (January 2021) shows odiff v2 1.194 s vs imgdiff 1.146 s on the cypress pair (parity, imgdiff multi-threaded) and imgdiff single-thread 2.616 s (odiff 2.19x faster). Correctness bug: pkg/yiq/delta.go applies uint8(r) to 16-bit RGBA() values, keeping the low byte, wrong for JPEG, 16-bit and semi-transparent pixels (the four benchmark PNGs are 8-bit RGBA with alpha 255, so the README numbers are unaffected). A larger compare image with a matching overlap reports equal (#13); --diff-image leaves holes; the README download link points to the buggy v1.0.0 (truncated or zero-byte output, #8; fixed in v1.0.2). Corrections in retier-35; C stands.

## Caveats and trade-offs

Multi-core vs single-thread: pkg/imgdiff/imgdiff.go splits rows over runtime.NumCPU() goroutines and cmd/main.go decodes both PNGs concurrently, while odiff bills itself as the fastest one-thread tool. The two tools also did different output work. imgdiff's default output is a transparent mask with red pixels written with png.BestSpeed, while odiff's default writes the base image with the diff overlaid. In the benchmark-era build (commit 1be7ce7, 2020-12-14), main.go deferred writer.Flush() and f.Close() and then left through os.Exit(1), which skips deferred calls, so the last buffered bytes of every diff PNG were never written. The output was truncated until the 'fix writing output' commit on 2021-03-25. imgdiff has no anti-aliasing detection, reads pixels through the generic image.At interface, and its loops run one row and column past the bounds (harmless). The odiff build is unversioned: imgdiff measured odiff at 6.475 s on the cypress pair, while odiff's own README reports 1.168 s for the same pair on a different machine, so imgdiff probably tested an older odiff. odiff has since been rewritten in Zig with SIMD, so the gap is probably gone. The author writes that imgdiff 'isn't as fast as a tool like this should be'. Benchmark code is not in the repo (only the tables), and the toolchain and flags are not stated. Last commit 2021-03-25. Image comparison is only loosely in color-and-resampling; consider the image category. [retier] Speed claim obsolete: the README's 4.49x/3.15x was against odiff v1, whose dependency did 'massive data copying'; imgdiff PR #5 by the odiff author (January 2021) shows parity against odiff v2 on the cypress pair (1.194 s vs 1.146 s) with imgdiff single-thread at 2.616 s, and odiff has since been rewritten in Zig with SIMD. Multi-core vs single-thread: pkg/imgdiff/imgdiff.go splits rows over runtime.NumCPU() goroutines and decodes both PNGs concurrently, while odiff is single-threaded. Different output work (imgdiff writes a transparent red mask with png.BestSpeed; odiff overlays the base image). In the benchmark-era build (1be7ce7) main.go left through os.Exit(1), skipping deferred Flush/Close, so every diff PNG was truncated until 2021-03-25 (the README download link still points to the buggy v1.0.0; fix in v1.0.2, issue #8). Correctness bug: pkg/yiq/delta.go applies uint8(r) to 16-bit RGBA() values, keeping the low byte, which is wrong for JPEG, 16-bit and semi-transparent pixels (the four benchmark PNGs are 8-bit RGBA with alpha 255, so the README numbers are unaffected); a larger compare image with a matching overlap reports equal (#13); --diff-image leaves holes. No anti-aliasing detection; generic image.At pixel access. Benchmark code is not in the repo; toolchain and flags unstated. Last commit 2021-03-25.

Go command-line tool and package; uses a YIQ color-difference threshold; README claims it can do everything odiff can (not verified).

## Maintenance

Abandoned: 7 commits, last release v1.0.2 on 2021-03-25, and 2024 bug reports (#12, #13) unanswered. It is MIT-licensed and small enough to vendor, but fix the low-byte color conversion, the size check and the loop bounds first, and do not rely on its speed claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine tables in readme.md with the CPU model (i7-4700HQ) but no benchmark script in the repo (scripts/ holds only build.sh), no Go toolchain version or flags and no odiff version, so C.
- **Verifier notes:** README numbers match the record, and its relative column matches its own means (6.475/1.442 = 4.49, 6.016/1.908 = 3.15, derived from page data); the mismatching relative column belongs to odiff, not imgdiff. The output-truncation bug is confirmed by comparing raw cmd/main.go at 1be7ce7 with HEAD. Metadata confirmed: MIT, 1.7k stars, 69 forks, 7 commits, release v1.0.0, last commit 2021-03-25.
- **Fields the verifier corrected:** `hardware`, `caveats`, `claimed_speedup`, `baseline`
- **Shortcomings recorded by:** first-party README; PR #5 by odiff author
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/master/readme.md>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/go.mod>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/pkg/imgdiff/imgdiff.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/cmd/main.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/1be7ce7/cmd/main.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/f009fa8/cmd/main.go>
  - <https://github.com/n7olkachev/imgdiff>
  - <https://github.com/n7olkachev/imgdiff/commits>
  - <https://github.com/n7olkachev/imgdiff/commit/3eef05c>
  - <https://github.com/n7olkachev/imgdiff/tree/master/scripts>
  - <https://github.com/n7olkachev/imgdiff/tree/master/cmd>
- **Sources the enricher read:**
  - <https://github.com/n7olkachev/imgdiff>
  - <https://github.com/n7olkachev/imgdiff/commits>
  - <https://github.com/n7olkachev/imgdiff/releases>
  - <https://github.com/n7olkachev/imgdiff/tree/master/pkg>
  - <https://github.com/n7olkachev/imgdiff/tree/master/pkg/yiq>
  - <https://github.com/n7olkachev/imgdiff/issues?q=is%3Aissue>
  - <https://github.com/n7olkachev/imgdiff/issues/8>
  - <https://github.com/n7olkachev/imgdiff/issues/9>
  - <https://github.com/n7olkachev/imgdiff/issues/12>
  - <https://github.com/n7olkachev/imgdiff/issues/13>
  - <https://github.com/n7olkachev/imgdiff/pulls?q=is%3Apr>
  - <https://github.com/n7olkachev/imgdiff/pull/5>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/readme.md>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/go.mod>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/go.sum>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/pkg/imgdiff/imgdiff.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/pkg/yiq/delta.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/cmd/main.go>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/n7olkachev/imgdiff/1be7ce7/cmd/main.go>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/main/images/www.cypress.io.png>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/main/images/www.cypress.io-1.png>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/main/images/water-4k.png>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/main/images/water-4k-2.png>
  - <https://raw.githubusercontent.com/golang/go/master/src/image/color/ycbcr.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/n7olkachev/imgdiff`) · [data/wave10/enrich/raw/github_com_n7olkachev_imgdiff.json](../../../data/wave10/enrich/raw/github_com_n7olkachev_imgdiff.json) (enrichment confidence 0.85)

</details>
