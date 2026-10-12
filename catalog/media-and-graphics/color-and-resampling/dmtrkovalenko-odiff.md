# odiff

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig (formerly OCaml) CLI and Node tool that diffs screenshots pixel by pixel with a YIQ threshold; README times it 4.8-7.6x faster than ImageMagick compare and pixelmatch.

| | |
|---|---|
| **Beats** | ImageMagick compare (and pixelmatch) |
| **Claimed result** | cypress.io screenshots: odiff 1.168 s +/- 0.008 vs ImageMagick compare 8.881 s (README relative 7.65) vs pixelmatch 7.712 s (README relative 6.67). Water image pair: odiff 1.951 s +/- 0.014 vs ImageMagick compare 9.326 s (README relative 5.24) vs pixelmatch 10.614 s (README relative 5.50). The means give 7.60x, 6.60x, 4.78x and 5.44x (derived from page data). README text: 'Odiff is 6 times faster than imagemagick and pixelmatch'. |
| **Workload** | Pixel-by-pixel visual diff of two full-page cypress.io screenshots and of the water-4k.png / water-4k-2.png pair (README calls it 8k; 8400 x 4725 per imgdiff's README), writing a diff PNG, timed end to end as separate processes with hyperfine -i (commands in images/README.md). |
| **Metric** | latency |
| **Hardware** | MacBook Pro 16, macOS 11 Big Sur beta (stated in images/README.md); CPU model not stated |
| **Adoption** | 3.2k stars; used by the Argos visual testing platform (README) |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/dmtrKovalenko/odiff) · [benchmark](https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/README.md) |

## Verdict

Only first-party hyperfine wall-clock runs exist (MacBook Pro 16 on macOS 11 beta, CPU and tool versions unstated; images/README.md invokes the OCaml-era binary 'ODiffBin'), timing whole processes including PNG decode and encode: on the cypress.io screenshot pair 1.168 s vs ImageMagick compare -compose src 8.881 s (7.6x) and pixelmatch 7.712 s (6.6x), and on the water pair 1.951 s vs 9.326 s (4.8x) and 10.614 s (5.4x), with ratios derived from the means. The tools do different work (pixelmatch runs anti-aliasing detection by default, and odiff does not), so the README's claim that all three produce the same difference is wrong.

## Use it when

- Screenshot-based visual regression in CI (Playwright via playwright-odiff, Cypress via cypress-odiff; Argos, Lost Pixel and Visual Regression Tracker use it) where most pixels are identical between baseline and candidate.
- Large full-page captures (tens of megapixels) where a JavaScript pixelmatch run takes seconds and you want a native single binary.
- High comparison counts from Node: keep one ODiffServer alive to avoid per-call process start-up and initialization.
- Pipelines that compare across formats (PNG baseline vs JPEG or WebP capture) or need ignore regions and the bounding rows/columns of the change.

## Skip it when

- When you need ImageMagick compare's metrics (AE with fuzz, RMSE, PSNR, SSIM) or a perceptual metric such as SSIM or CIEDE2000: odiff only reports a count and percentage over a YIQ threshold.
- When diff counts must match pixelmatch: anti-aliasing detection is off by default in odiff (--antialiasing to enable) but on by default in pixelmatch, JPEGs decode with libjpeg-turbo's fast DCT, and the delta is fixed-point (discussion #82 reports 1.07% vs pixelmatch's 0.75% at threshold 0.1).
- Small images compared in-process from JavaScript: a third-party benchmark by Vizzly (vendor of the competing Honeydiff; blog read from a search snippet only, method unknown) timed odiff at 240 ms vs pixelmatch 80 ms on 2.1-2.5 MP images and 710 ms vs 450 ms at 18 MP, so process and decode overhead can erase the advantage.
- Saturating many cores on one huge image pair: the per-pixel loop is single-threaded; only the two image decodes run in parallel.
- Relying on the README's 6x figure for the current Zig build: it was measured in 2021 on the OCaml version and has not been re-run against ImageMagick or pixelmatch since.

## How it is fast

compareSameLayouts loads std.simd.suggestVectorLength(u32) packed RGBA pixels at a time and tests base != comp as whole vectors; the YIQ NTSC color delta (the Kotsarenko-Ramos metric pixelmatch also uses) is computed only for lanes that differ, so mostly identical screenshots cost little more than a memory compare. The delta itself uses 12-bit fixed-point integer arithmetic (calculatePixelColorDeltaSimd) instead of doubles. The two input images are decoded in parallel on two threads with bundled libspng, libjpeg-turbo (TJFLAG_FASTDCT unless threshold is 0), libtiff and libwebp. Optional extras: a hand-written AVX-512 NASM kernel (vxdiff.asm) for count-only runs and an RVV C kernel on riscv64; server mode removes process spawn cost.

## Compared with alternatives

Pick odiff over imgdiff (Go), which its own README times at 1.442 s vs 6.475 s for an older odiff on the same cypress pair, when you want the Node, Playwright and Cypress integrations, server mode, ignore regions and anti-aliasing detection; pick libvips or OpenCV only if you are scripting a custom absdiff-and-threshold pipeline rather than running a turnkey visual-regression comparator.

## Integration

| | |
|---|---|
| **Form** | CLI executable plus npm package (odiff-bin) and server mode; the Zig sources build a static odiff_lib library |
| **Dependencies** | libspng, libjpeg-turbo, libtiff, libwebp (fetched and built through the imgz Zig package, or system libspng/libjpeg/libtiff with -Ddynamic=true outside Windows); nasm for x86_64 Linux and macOS builds; Node.js for the npm API |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version) plus nasm on x86_64 Linux/macOS; prebuilt binaries need no toolchain |
| **Platforms** | Prebuilt for macOS, Linux and Windows on x86_64 and aarch64, plus Linux riscv64 (generic and RVA23 builds); SIMD width is fixed at compile time (SSE2/AVX2/AVX-512/NEON/RVV); the AVX-512 asm kernel is x86_64 Linux/macOS only |
| **Thread safety** | Process-level tool: each CLI call or server process handles one comparison at a time; ODiffServer spawns one server process per core for parallel test workers; the Zig library's compare() has no documented thread-safety guarantees |
| **Drop-in for the baseline** | partial: the CLI argument order matches pixelmatch's (img1 img2 diff), but defaults differ (no anti-aliasing detection, threshold semantics), and it does not replace ImageMagick compare's metric options |

## Gotchas

- The fast AVX-512 kernel almost never runs: it needs a build targeting AVX-512BW/VL (the release targets in build.zig set only arch and OS, so they get Zig's baseline CPU), the --enable-asm flag, threshold exactly 0.1, no diff image, no anti-aliasing, no ignore regions and identical dimensions.
- Any threshold other than 0 switches JPEG decoding to libjpeg-turbo TJFLAG_FASTDCT, so JPEG inputs can show small decode-dependent differences that other tools would not report; use -t 0 for the accurate DCT.
- Correctness fixes to know about: before PR #185 (merged 2026-08-24, after v4.5.0) the fixed-point YIQ constants were truncated, which under-counted near the threshold (3 extra pixels out of 2.27 million on a test image after the fix); versions 4.1.1-4.1.2 could write incomplete diff PNGs for large files (issue #153, fixed in PR #155).
- The diff PNG is written only when pixels differ; with --fail-on-layout (CLI, off by default) or failOnLayoutDiff (Node), images of different sizes return reason 'layout-diff' without being compared, and otherwise extra non-transparent pixels count as differences.

## Known shortcomings

- Tables last changed 2021-01-27 (OCaml era) on a MacBook Pro 16 with no CPU model, versions or flags; the relative column mismatches the stated means (water 4.78/5.44 against 5.24/5.50); outputs differ (ImageMagick has no YIQ threshold, pixelmatch does anti-aliasing detection; discussion #82 shows 1.07% against 0.75%); bench.sh compares odiff commits only. Image diffing is a weak fit for colour-and-resampling.
- Enricher (e103, 2026-10-04): the README comparison does unequal work: pixelmatch runs with anti-aliasing detection on by default while odiff runs with it off; the AVX-512 path is opt-in only (--enable-asm, threshold 0.1, no diff image) and release binaries target a baseline CPU; JPEG decode uses TJFLAG_FASTDCT unless -t 0. A vendor blog (Vizzly, which sells the rival Honeydiff) reports the opposite ordering, pixelmatch faster (80 vs 240 ms at 2.1-2.5 MP; 450 vs 710 ms at 18 MP), seen in search snippets only. The images/README.md harness runs ODiffBin, confirming the OCaml build was measured.

## Caveats and trade-offs

The README tables were last changed on 2021-01-27 (GitHub blame) and were run on macOS 11 Big Sur beta. They therefore measure the OCaml-era odiff, not the current Zig/SIMD code. bench.sh only compares odiff commits with each other and does not rerun ImageMagick or pixelmatch. The README relative column does not match its own means. For the water pair, 9.326/1.951 = 4.78 and 10.614/1.951 = 5.44 against the stated 5.24 and 5.50. For cypress, 8.881/1.168 = 7.60 and 7.712/1.168 = 6.60 against 7.65 and 6.67 (derived from page data). This suggests the rows come from different runs. The README says 'the produced difference will be the same for all 3 commands', but the tools do different work. ImageMagick compare -compose src flags every differing pixel with no YIQ threshold. pixelmatch is a Node.js CLI that runs anti-aliasing detection by default, while odiff leaves it off by default. Discussion #82 (2023) reports 1.07% different pixels from odiff vs 0.75% from pixelmatch and jimp at threshold 0.1. A 2026-08-24 commit (#185) fixes YIQ coefficient rounding that caused systematic under-counting in the current code. The ImageMagick thread count and the CPU model are not stated. Hyperfine wall time includes process start-up, PNG decode and encode. Image comparison is only loosely in color-and-resampling (a color-distance task); consider the image category.

Command-line tool plus Node bindings (odiff-bin); YIQ NTSC perceptual metric with anti-aliasing detection, region ignoring, cross-format compare (png, jpeg, webp, tiff); single-thread; Zig toolchain with SSE2, AVX2, AVX512 and NEON paths.

## Maintenance

Actively maintained (v4.5.0 released in July 2026, fixes merged 2026-08-24), MIT-licensed, 3.2k stars and used by several visual-testing services; the speed claim is first-party, five years old and was measured on the OCaml version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine tables in README.md, with the exact commands in images/README.md and the test images in images/. The machine is named only as a 'MacBook Pro 16' with no CPU model, and the odiff, ImageMagick and pixelmatch versions, compiler and flags are not stated, so C.
- **Verifier notes:** Numbers and the benchmarks.png chart (1.168 s vs 8.881 s) match the record. The record's language is Zig (current code), but the benchmarked build was OCaml. imgdiff (same batch) measured odiff independently at 6.475 s on the cypress pair, but only against imgdiff and on different hardware, so it does not lift odiff to B against ImageMagick. Metadata confirmed: MIT (LICENSE.txt), 3.2k stars, 115 forks, not a fork, last commit 2026-08-24, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party hyperfine comparison; contrary vendor blog (snippet)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/images/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/build.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/main/images/benchmarks.png>
  - <https://github.com/dmtrKovalenko/odiff>
  - <https://github.com/dmtrKovalenko/odiff/commits>
  - <https://github.com/dmtrKovalenko/odiff/blame/main/README.md>
  - <https://github.com/dmtrKovalenko/odiff/discussions/82>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/images/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/build.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/package.json>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/diff.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/color_delta.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/antialiasing.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/vxdiff.asm>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/rvv.c>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/cli.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/io.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/io/io.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/io/jpeg.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/test_avx.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/test_color_delta.zig>
  - <https://raw.githubusercontent.com/dmtrKovalenko/odiff/HEAD/src/root.zig>
  - <https://github.com/dmtrKovalenko/odiff/tree/main/src>
  - <https://github.com/dmtrKovalenko/odiff/pull/185>
  - <https://github.com/dmtrKovalenko/odiff/releases>
  - <https://github.com/dmtrKovalenko/odiff/issues?q=is%3Aissue+slow+OR+performance+OR+wrong+OR+incorrect>
  - <https://github.com/dmtrKovalenko/odiff/issues/101>
  - <https://github.com/dmtrKovalenko/odiff/issues/153>
  - <https://github.com/vizzly-testing/honeydiff>
  - <https://github.com/vizzly-testing/honeydiff/tree/main>
  - WebSearch snippet: https://vizzly.dev/blog/honeydiff-vs-odiff-pixelmatch-benchmarks/ (page not opened; blogs blocked)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/dmtrkovalenko/odiff`) · [data/wave10/enrich/raw/github_com_dmtrkovalenko_odiff.json](../../../data/wave10/enrich/raw/github_com_dmtrkovalenko_odiff.json) (enrichment confidence 0.8)

</details>
