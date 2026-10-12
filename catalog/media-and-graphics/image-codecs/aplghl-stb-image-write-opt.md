# stb-image-write-opt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR Unlicense` · 🟢 active

> Byte-identical stb_image_write.h v1.16 fork with an SSE2 deflate match scan; PNG encode about 1.7-1.9x upstream -O2.

| | |
|---|---|
| **Beats** | upstream stb_image_write.h v1.16 (nothings/stb at 2c980bb), compiled the way consumers compile it (-O2) |
| **Claimed result** | Fork build (-O3 -march=x86-64-v2 -ffp-contract=off plus held-out PGO) against upstream stb_image_write v1.16 built at -O2: 17-row geomean 1.627x (results/summary.csv). The only source changes are in the DEFLATE path used by PNG: the SSE2 stbiw__zlib_countm, precomputed fixed-Huffman codes and binary-searched length and distance codes (diff of src/stb_image_write.h against upstream/stb_image_write.h). PNG rows run 1.07x to 2.15x (gen:random 1.072x; the README's 1.62-2.15x leaves that row out), with a geomean of 1.725x over 9 rows (derived from page data). The JPEG (1.63x to 2.04x), BMP (1.56x), TGA (1.07x, 1.74x) and HDR (0.948x) rows run byte-identical source, so their gains come only from -O3, -march=x86-64-v2, PGO and code layout; those 8 rows give a geomean of 1.524x (derived from page data). Downstream consumer (results/consumer.csv, stock built at -O2 against the fork's prebuilt PGO library): PNG 1.90x, JPEG 1.17x (flags only), geomean 1.49x. Same-flag source evidence: whole stbi_zlib_compress on a synthetic, highly compressible 256 KiB input (3192 compressed bytes), SSE2 0.428 against 1.466 ns/byte for the fork's own scalar fallback, 3.4x (results/kernels.csv). The README's countm \~3.3x row (1.41 against 4.6 ns/call) is not a valid measurement: the SSE2 time is flat at 1.41 ns from a 3-byte to a 258-byte match, and the scalar time at 258 bytes (3.54 ns) is below its 3-byte time, which a byte loop over 258 bytes cannot reach; bench/kernbench.c calls the inlinable kernel on constant static buffers in a loop, so the compiler can hoist the work. The \~+50% no-PGO figure appears only in README and docs/MEASUREMENT.md text. |
| **Workload** | Image encode time in ns per pixel (minimum of several repeats, pinned with taskset) over 17 rows: PNG (1-4 components, several quality/filter settings, palette and random inputs), JPEG (quality 50/75/90), BMP, TGA and HDR output, from deterministic synthetic 512x512 plasma, 640x480 gradient and generated pixel inputs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-14700F (Raptor Lake), 28 threads, WSL2, Ubuntu 24.04, benchmark pinned with taskset |
| **Compiler and flags** | clang 23.1.2. Baseline: upstream header at -O2. Fork: -O3 -march=x86-64-v2 -ffp-contract=off plus held-out PGO. The exact build is also verified at -march=x86-64-v3, scalar (-DSTBIW_NO_SIMD), gcc 13.3 and zig cc. |
| **Adoption** | 0 stars, 0 forks, 0 watchers; 2 commits, both dated 2026-09-29; release v1.0.0 |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/aplghl/stb-image-write-opt) · [benchmark](https://github.com/aplghl/stb-image-write-opt) |

## Verdict

On an Intel i7-14700F under WSL2 with clang 23.1.2, the fork at -O3 -march=x86-64-v2 -ffp-contract=off with held-out PGO encoded 17 synthetic rows 1.627x faster (geomean) than upstream stb_image_write v1.16 at -O2. The 9 PNG rows, the only ones that touch changed code, give 1.725x (1.07x on random data, up to 2.15x on gradients), the 8 JPEG, BMP, TGA and HDR rows give 1.524x from flags and PGO alone, and a separate consumer program linking the PGO library measured PNG 1.90x and JPEG 1.17x.

## Use it when

- You vendor stb_image_write and write PNGs with its builtin compressor (screenshots, debug dumps, tools) and want faster encodes with unchanged files: PNG rows 1.62x-2.15x, and 1.90x in the downstream consumer test.
- Smooth or highly compressible images such as gradients, UI captures and flat regions, where long matches make the SSE2 scan pay off (gradient PNG rows 1.89x-2.15x against 1.07x on incompressible random data).
- You rely on byte-for-byte identical output with upstream, for golden-file tests or content hashes: the differential matrix runs about 9,600 checks, and a non-vacuous test confirms that corrupted output fails it.
- x86-64 builds with GCC or Clang, where the SSE2 kernel is on by default with no runtime dispatch.

## Skip it when

- You need fast or small PNGs in absolute terms: the fork still spends about 50-70 ns per pixel on plasma_512 PNG (results/fork.csv), and upstream says its PNGs are 20-50% larger than an optimizing encoder's; fpng, fpnge or a better compressor plugged in through STBIW_ZLIB_COMPRESS are the tools for that (none is compared here).
- You already define STBIW_ZLIB_COMPRESS: every source change is in the builtin compressor, so only compiler flags would differ.
- JPEG, BMP, TGA or HDR output: that code is byte-identical to upstream; the bench's 1.63x-2.04x JPEG rows dropped to 1.17x in the downstream consumer test, and compiling upstream with the same flags would give the same effect.
- MSVC or non-x86 targets: the SSE2 kernel needs __SSE2__ with GCC or Clang, so MSVC and aarch64 builds use the scalar loop and get only the table changes, which docs/REJECTED.md measured as roughly neutral overall.
- Prebuilt release tarballs on older x86 CPUs: build.zig hard-codes -march=x86-64-v2 for x86-64, so they need SSE4.2-class CPUs, and release.yml builds them without PGO.

## How it is fast

The DEFLATE match-length scan (stbiw__zlib_countm), which the author profiled at about 30% of PNG encode time, compares 16 bytes per step with baseline SSE2 and finds the first mismatch with movemask plus count-trailing-zeros. Fixed-Huffman codes come from precomputed, already bit-reversed tables instead of a per-symbol bit-reverse loop, and length and distance codes are found by binary search instead of linear scans. Nothing else in the writer changes, so the JPEG, BMP, TGA and HDR gains in the headline come only from building at -O3 -march=x86-64-v2 with PGO against upstream at -O2 (docs/REJECTED.md: -march=x86-64-v3 alone takes plasma_512 JPEG from 5.47 to 4.06 ns/px).

## Compared with alternatives

Pick it only when you need stb_image_write's API and upstream-identical bytes; for PNG encode speed, fpnge (QOIR: 312.59 MPixels/s) and fpng are in another class from this fork's 16.78 MPixels/s on plasma_512 (results/fork.csv; different machines and images, so only indicative), at the cost of different output bytes. Pair it with stb-image-opt, the decode-side fork by the same author.

## Integration

| | |
|---|---|
| **Form** | header-only (single-header drop-in), or static lib via scripts/build_opt.sh or build.zig |
| **Dependencies** | none beyond libc and libm (emmintrin.h on x86-64) |
| **Minimum toolchain** | Same C dialect as upstream stb_image_write (compiles as C and C++ per README); the SSE2 kernel needs GCC or Clang (__builtin_ctz); verified with clang 23.1.2, gcc 13.3 and zig cc |
| **Platforms** | x86-64 with baseline SSE2 and no runtime dispatch; aarch64 and other targets use the scalar fallback; cross-compiles to aarch64-linux-musl, x86_64-windows-gnu and aarch64-macos |
| **Thread safety** | Unchanged from upstream: each encode call keeps its own state, but stbi_write_png_compression_level, stbi_write_force_png_filter, stbi_write_tga_with_rle and the flip-on-write flag are process-wide globals. |
| **Drop-in for the baseline** | partial — API, ABI and output bytes match upstream; only the builtin PNG/zlib path is faster at any flags, while the JPEG, BMP and TGA gains need -O3 -march=x86-64-v2 (and PGO) and would apply equally to upstream built that way |

## Gotchas

- The 1.627x headline mixes source and flags, and the JPEG rows probably overstate real use: the bench compiles the writer, a no-op sink callback and the timing loop into one translation unit at -O3 with PGO, and the JPEG writer emits every byte through the s-&gt;func callback (stbiw__putc), which that setup can devirtualize or inline. JPEG rows reach 1.80x geomean there (derived from page data) but only 1.17x in results/consumer.csv, where the encoder is a separately built PGO library; no committed run isolates the cause.
- The countm \~3.3x (1.41 vs 4.6 ns/call) is not evidence: kernbench calls the inlinable kernel on constant static buffers with limit 2048, the SSE2 time is flat from a 3-byte to a 258-byte match, and the scalar 258-byte call (3.54 ns) beats its own 3-byte call. The deflate kernel 3.4x (0.43 vs 1.47 ns/byte) is a valid same-flag comparison, but on a synthetic input that compresses 82:1 (3192 bytes from 256 KiB), a best case for long matches.
- The 'held-out' PGO set is not fully disjoint: HELDOUT trains on corpus/grad_640_480.png and grad_640_480_gray.png, which are also measured (with other channel counts or formats), and docs/MEASUREMENT.md reports held-out +62.7% above in-sample +58.5%, so the PGO share is within run-to-run noise.
- BMP, TGA and HDR rows are plumbing-bound and layout-sensitive (the same build measured 1.19 and 1.76 ns/px for BMP), so their 0.948x-1.74x ratios are noise, yet they stay in the geomean.

## Known shortcomings

- Claim overstated: the fork changes only the DEFLATE and PNG code, yet 8 of 17 rows (JPEG, BMP, TGA, HDR) with byte-identical source still gain a 1.524x geomean from -O3, -march and PGO against upstream's -O2; the PNG rows run 1.07-2.15x (geomean 1.725x), not 1.62-2.15x; the countm microbenchmark's about 3.3x is invalid (a flat 1.41 ns from L3 to L258 points to a hoisted call); the 3.4x deflate same-flag figure is on synthetic data. Baseline is upstream stb_image_write, not libpng.
- Enricher (2026-10-04): the 1.627x headline mixes source and flags; only the 9 PNG rows touch changed code (1.725x, 1.07x on random data to 2.15x on gradients), the JPEG/BMP/TGA/HDR rows (1.524x) come from flags and PGO alone, and the JPEG rows are probably inflated by the writer, a no-op sink callback and the timing loop being compiled in one -O3 PGO translation unit (1.80x there vs 1.17x in results/consumer.csv with a separately built library). The countm 3.3x is not evidence (inlinable kernel on constant static buffers, flat SSE2 time from 3- to 258-byte matches). The deflate kernel 3.4x is a valid same-flag comparison but on input compressing 82:1. The 'held-out' PGO set overlaps the measured corpus (grad_640_480 variants). BMP/TGA/HDR rows are layout-sensitive noise (0.948x-1.74x) yet stay in the geomean. One author, 2 commits on 2026-09-29, 0 stars; unofficial fork.

## Caveats and trade-offs

The baseline is upstream stb_image_write, not libpng, zlib, libjpeg-turbo or libwebp; stb's PNG writer is a slow, low-effort zlib (upstream takes about 100 ns per pixel on plasma_512 PNG), so these ratios do not rank it against the listed incumbents. The headline mixes source changes with compiler flags and PGO. The fork changes only the DEFLATE/PNG path, yet the JPEG, BMP, TGA and HDR rows (8 of 17, geomean 1.524x, derived) also speed up, with no source change, because the fork is built with -O3 -march=x86-64-v2 and PGO and upstream with -O2. A consumer compiling upstream with the same flags would get those gains. The harness commits no same-flag fork-versus-upstream run, so the PNG source-only gain cannot be recomputed. docs/MEASUREMENT.md and results/README.md call the BMP, TGA and HDR rows plumbing-bound and layout-sensitive (the same build measured 1.19 and 1.76 ns/px for BMP), yet they stay in the geomean. The countm kernel microbenchmark appears to time a hoisted loop-invariant call (flat 1.41 ns from L=3 to L=258), so its \~3.3x is not evidence. The deflate kernel 3.4x compares SSE2 against the fork's own scalar fallback on a synthetic run-heavy input, so it is a best case. On incompressible input (gen:random) PNG gains only 1.07x. Synthetic and generated inputs, single machine under WSL2, run-to-run variation of a few percent. Unofficial fork not endorsed by the upstream author, single author, two commits.

Only src/stb_image_write.h changes; public API and ABI unchanged (16 exported symbols checked by make abi). Output is byte-identical to upstream across about 9,600 differential checks (5 formats x 1-4 components x quality/filter/stride/RLE/flip toggles), with a make nonvacuous test that deliberately corrupted output must fail the suite. Changes: SSE2 DEFLATE match-length kernel (baseline x86-64, no runtime dispatch, scalar fallback on other targets), precomputed bit-reversed fixed-Huffman codes, and binary search over length/distance code tables. Recommended flags -march=x86-64-v2 need SSE4.2-class CPUs. Encode side only.

## Maintenance

Active but new: one author, 2 commits on 2026-09-29, release v1.0.0, 0 stars and no issues or PRs; MIT OR Unlicense and a single header, so easy to vendor, but an unofficial fork not endorsed by the stb author.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now A.
- **Tier reason:** Public harness (bench/bench.c, harness/bench.sh, harness/bench_vs_upstream.sh, harness/consumer/run.sh) builds upstream stb_image_write v1.16 at -O2 against the fork at -O3 -march=x86-64-v2 -ffp-contract=off with held-out PGO, with clang 23.1.2 on an Intel i7-14700F stated, and results/summary.csv gives the 1.627x geomean, so the build-versus-build comparison stays A. The claim is overstated: 8 of the 17 rows exercise code the fork never changed, and the countm microbenchmark cannot have timed the scan.
- **Verifier notes:** Tier A stays for the reproducible build-versus-build harness, but the claim is overstated: diffing the headers shows the JPEG/BMP/TGA/HDR code is untouched, so about half the rows measure only -O3, -march and PGO against -O2, and the countm 3.3x microbenchmark appears to time a hoisted call. claimed_speedup is restated with the PNG-only and flag-only geomeans.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness
- **Pages the verifier opened:**
  - <https://github.com/aplghl/stb-image-write-opt>
  - <https://github.com/aplghl/stb-image-write-opt/commits>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/docs/MEASUREMENT.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/docs/REJECTED.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/consumer/run.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/scripts/build_opt.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/bench/kernbench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/upstream_o2.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/fork.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/consumer.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/src/stb_image_write.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/upstream/stb_image_write.h>
- **Sources the enricher read:**
  - <https://github.com/aplghl/stb-image-write-opt>
  - <https://github.com/aplghl/stb-image-write-opt/issues?q=is%3Aissue>
  - <https://github.com/aplghl/stb-image-write-opt/releases>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/build.zig>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/docs/MEASUREMENT.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/docs/REJECTED.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/consumer/run.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/harness/consumer/consumer.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/scripts/build_opt.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/bench/kernbench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/upstream_o2.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/fork.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/results/consumer.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/src/stb_image_write.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-write-opt/HEAD/upstream/stb_image_write.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aplghl/stb-image-write-opt`) · [data/wave10/enrich/raw/github_com_aplghl_stb_image_write_opt.json](../../../data/wave10/enrich/raw/github_com_aplghl_stb_image_write_opt.json) (enrichment confidence 0.8)

</details>
