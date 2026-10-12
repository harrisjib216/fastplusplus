# jpeg-nitro (nitrojpeg and nitropng parallel decoders)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Parallel single-image baseline JPEG and 8-bit PNG decoders in C; one-thread speed equals libjpeg-turbo, all-core latency \~9x lower.

| | |
|---|---|
| **Beats** | libjpeg-turbo 3.1.2 (TurboJPEG 3 API, SIMD, one thread) for JPEG; Wuffs (unpinned wuffs-unsupported-snapshot.c, decoding to BGRA) for PNG; libpng is not measured |
| **Claimed result** | Intel i9 13th gen, 50 private camera JPEGs, bench/bench decode-only from memory (bench/results/results.txt). Like-for-like on one thread: nitrojpeg to YUV planes 103.0 ms/image versus libjpeg-turbo 3.1.2 to YUV planes 107.4 ms (1.04x, derived from page data). All 16 threads versus libjpeg-turbo on one thread: nitrojpeg to YUV 11.7 ms versus 107.4 ms (9.2x, derived). The BGRX row (24.7 ms versus 124.1 ms, 5.0x) times an unshipped NJ_REFERENCE path built on libjpeg-turbo and is not a figure for the public API, which outputs YUV planes only. Apple M1 (43 photos, bench/results/m1.txt): one thread 153.8 versus 168.1 ms (1.09x, derived), 8 threads 30.4 versus 168.1 ms (5.5x). PNG: nitropng parallel versus Wuffs to BGRA on 34 PNGs, with unsupported files counted near 0 ms for nitropng. |
| **Workload** | Decode-only time per image from memory, one image decoded on all cores: 50 camera JPEGs (mostly 6000x4000, 17 MB average) and 34 real PNGs (938 MB, 805 Mpixel). |
| **Metric** | latency |
| **Hardware** | Intel i9 13th gen, 8 cores / 16 threads, 48 KB L1D, 4 to 5.5 GHz, AMD RX 580, macOS (exact SKU not stated); Apple M1 MacBook Air 2020 (4+4 cores); Xeon E3-1245 v5 (Linux, nitro-only nbench numbers); Core i7-1260P (Arch Linux, different image set) |
| **Compiler and flags** | clang (Xcode Command Line Tools on macOS; version not stated) -O3 -march=native, plus -mbranches-within-32B-boundaries on x86 in the current Makefile and -fblocks off macOS; bench/bench is built with -DNJ_REFERENCE against a static libjpeg-turbo 3.1.2 that scripts/get-deps.sh builds with nasm SIMD, CMAKE_BUILD_TYPE=Release and -O3 -march=x86-64-v3 on macOS x86_64 (-mcpu=apple-m1 on arm64); Wuffs and pngbench are compiled -O3 with the same CPU flags. |
| **Adoption** | 0 stars, 1 fork; 82 commits, oldest visible commits dated 2026-09-27 |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/gereoffy/jpeg-nitro) · [benchmark](https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/README.md) |

## Verdict

On the author's macOS 'Intel i9 13th gen' (16 threads, SKU and clang version not stated) with 50 private 24 MP camera JPEGs, bench/bench (one timed pass per decoder, from memory) measured nitrojpeg 103.0 ms on one thread vs libjpeg-turbo 3.1.2 107.4 ms to YUV planes (parity) and 11.7 ms on 16 threads (9.2x); on an M1 Air 153.8 vs 168.1 ms and 30.4 ms on 8 threads; for 34 PNGs nitropng took 45.5 ms in parallel vs Wuffs to BGRA 180.1 ms, but 222.6 ms on one thread. The '5.0x to BGRX' row (24.7 ms) is not the shipped decoder: nj_decode_bgrx exists only under -DNJ_REFERENCE and calls the old engine in which libjpeg-turbo decodes re-emitted bands and does the upsampling and colour conversion; also, bench/pngbench divides nitropng's total by every file, including any it rejects as unsupported (palette, 16-bit, interlaced) in near-zero time while Wuffs decodes them, so such a file in the private PNG set would flatter nitropng's average.

## Use it when

- Image viewers, editors or on-demand previews where the latency of one large (12-50 MP) camera JPEG matters and cores are idle: about 11.7 ms instead of 107 ms per 24 MP photo on the author's 16-thread i9.
- Pipelines that consume planar YCbCr directly (GPU shader colour conversion, video or ML preprocessing that does its own conversion), since that is the library's native output.
- Camera and phone JPEGs without restart markers (the common case), which libjpeg-turbo cannot split across threads at all.
- Large 8-bit truecolour PNGs (screenshots, scans, AI-generated images) when raw unfiltered rows are enough: about 4x lower latency than Wuffs to BGRA on all 16 threads of the author's i9.
- Parallel inflate of one big zlib stream of known output size (np_zlib_decompress), as the repo does for PSD ZIP data.

## Skip it when

- Batch or server workloads that decode many images at once: on one thread nitrojpeg is at parity with libjpeg-turbo (1.04x i9, 1.09x M1) and nitropng is about 1.24x slower than Wuffs, so decoding images in parallel with libjpeg-turbo gives the same or better total throughput; on Linux the shared pthread pool makes concurrent calls take turns.
- Progressive, arithmetic-coded, 12-bit, lossless, CMYK, RGB-coded or multi-scan JPEGs and images over 16384 px; palette, 16-bit, sub-8-bit and interlaced PNGs (palette PNGs are common on the web). All return 'unsupported'; issue #3 (the reporter's first JPEG was progressive) was closed as not planned.
- When you need RGB/RGBA pixels or a libjpeg/TurboJPEG/libpng-compatible API: the shipped library outputs planar YCbCr or filtered-byte-prefixed rows only; the BGRX path exists only in the -DNJ_REFERENCE test build and uses libjpeg-turbo.
- GCC- or MSVC-only toolchains: the loop bodies are clang blocks, so it needs clang with -fblocks (issue #3 also reports no MSYS GCC build).
- Code that needs a mature dependency: single-author repository first committed 2026-09-27, 0 stars, no releases, README numbers revised daily, and a nitropng bug (incomplete fixed-Huffman distance table, so every fixed block with a match failed and fell back) was only fixed on 2026-09-30.

## How it is fast

nitrojpeg strips byte stuffing in parallel, cuts the entropy-coded data into about 32 x CPU chunks and decodes each speculatively from an arbitrary bit offset; Huffman codes self-synchronise (2.4 garbage MCUs on average over the author's 10,240 measured sync points), and an in-order stitching pass finds where each chunk meets the true decoding path, which fixes its MCU index and DC predictors. Coefficients are Huffman-decoded once, and each stitched chunk is dequantised and run through libjpeg's ISLOW IDCT (AVX2 or NEON, same constants and rounding as jidctint.c) by the thread that decoded it while it is still in cache; restart-marker files are decoded per interval in parallel. nitropng is a pugz-style speculative parallel inflate (each thread finds a valid dynamic-block header in its chunk, writes 16-bit placeholders for back-references into the unknown 32 KB window, resolves them after chaining, and combines per-chunk Adler-32 sums) followed by a wavefront filter reversal where row r trails row r-1 in 1 KB segments. Per-core speed is about libjpeg-turbo's (single 11-bit lookup Huffman decoder), so the whole gain is intra-image parallelism.

## Compared with alternatives

libjpeg-turbo-rs and zenjpeg compete with libjpeg-turbo on single-thread speed and give RGB output; pick nitrojpeg only when wall-clock latency of one image on many idle cores matters and planar YCbCr is acceptable. For PNG, libspng, zune-png and ptpng give complete pixel output, checksum handling and wider format coverage; nitropng wins only on latency for a large 8-bit truecolour PNG with spare cores.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/nitrojpeg.c/.h, src/nitropng.c/.h, src/nitropsd.c/.h, src/nitro_os.h); on Linux `make linux` also builds libnitro.so / libnitro.a |
| **Dependencies** | none at runtime beyond pthreads (Grand Central Dispatch on macOS); libjpeg-turbo 3 (TurboJPEG 3 API), Wuffs, stb_image and zlib only for the benchmarks, verify tools and the viewer's fallback |
| **Minimum toolchain** | clang with -fblocks (GCC unsupported; no blocks runtime library needed); C standard not documented; Windows via llvm-mingw or MSYS2 CLANG64 |
| **Platforms** | x86-64 (AVX2 IDCT and Adler-32 when compiled with -march=x86-64-v3 or native, otherwise scalar), aarch64 (NEON); macOS, Linux, Windows (MinGW) |
| **Thread safety** | Concurrent calls allowed (global buffer pool behind a mutex; the author ran ThreadSanitizer with four threads decoding at once), but on non-macOS the single pthread pool serialises parallel loops of concurrent calls; nj_set_max_workers / nj_set_chunks / nj_set_bands are process-wide globals. |
| **Drop-in for the baseline** | partial: decodes the same baseline JPEGs bit-exactly to libjpeg-turbo's ISLOW planes (verified on the author's 50 photos), but through its own API, YCbCr-planes-only output and a required fallback decoder for unsupported files |

## Gotchas

- SIMD is chosen at compile time (#ifdef __AVX2__ / __ARM_NEON), with no runtime dispatch: a generic x86-64 build silently uses the scalar IDCT, whose speed is not documented.
- Large internal buffers (unstuffed bit stream, per-chunk coefficient buffers sized at about twice the image's coefficient count) go into a process-global pool of up to 4096 buffers that is never freed and has no release API, so after one 24 MP decode on the order of 100-200 MB stays resident (estimated from the pool_take sizes in nitrojpeg.c).
- The 'nthreads' argument is the number of work pieces, not threads (&lt;= 0 means 4 x CPUs; 1 means truly single-threaded); the thread count is set globally with nj_set_max_workers.
- Output planes are padded to whole MCUs and the padding differs from libjpeg-turbo (the verify tool compares only the visible region); EXIF orientation is parsed but not applied; nitropng verifies the zlib Adler-32 but not PNG chunk CRC-32s.

## Known shortcomings

- Downgraded A to C: the i9 SKU and clang version are unstated and the 50 test photos are private. Single-thread like-for-like decode is only 1.04x libjpeg-turbo (103.0 vs 107.4 ms; 1.09x on Apple M1); the 9.2x (to YUV) and 5.0x (to BGRX) are parallel decode against one-thread libjpeg-turbo (built with get-deps.sh -O3 -march=x86-64-v3). nitropng's baseline is Wuffs, not libpng, and single-thread nitropng is 1.24x slower than Wuffs.
- The '5.0x to BGRX' row times an unshipped path: nj_decode_bgrx exists only under -DNJ_REFERENCE, calls the old libjpeg-turbo-based engine and is not exported in libnitro.map; the public API outputs YUV planes only, so the valid figures are 1.04x on one thread and 9.2x on 16 threads (retier-11). bench/pngbench divides by all files, so unsupported PNGs (palette, 16-bit, interlaced) count near 0 ms for nitropng while Wuffs decodes them. SIMD is compile-time only with undocumented scalar fallback speed; the global buffer pool is never freed (about 100-200 MB resident after a 24 MP image, estimate); needs clang -fblocks; the Linux pthread pool makes concurrent calls take turns; no CRC-32 check; issue #3 (progressive JPEG, GCC) closed as not planned.

## Caveats and trade-offs

The headline 9x to 11x compares nitrojpeg on all 16 threads with libjpeg-turbo on one thread and mixes output formats (11.7 ms is YUV planes, 124 ms is BGRX); the like-for-like figures are 1.04x on one thread (YUV versus YUV), 9.2x multi-threaded to YUV and 5.0x multi-threaded to BGRX. libjpeg-turbo gets no intra-image parallelism because camera JPEGs lack restart markers. The 50 test photos are private, the i9 SKU is not named and the clang version is not stated, so the numbers cannot be reproduced exactly; the machine's clock swings between 4 and 5.5 GHz (the author reports about 10 percent noise on single runs). The PNG baseline is Wuffs decoding to BGRA with checksums ignored, while nitropng outputs unfiltered rows (colour conversion is left to the GPU) and verifies Adler-32, so the work differs; on one thread nitropng is slower than Wuffs, and libpng is not in any table. Very new single-author repository (first commits 2026-09-27, 0 stars) whose README numbers change from day to day. nitrojpeg output is reported bit-identical to libjpeg-turbo's ISLOW IDCT on the 50 test images (bench/verify).

Baseline sequential JPEG only (progressive JPEG is left to libjpeg-turbo or the OS decoder); 8-bit non-interlaced PNG only; plain C with pthreads and AVX2 or NEON, but the loop bodies are clang blocks so it needs clang with -fblocks (GCC is not supported); uses every core for a single image, which helps latency but not total throughput of a batch; output is claimed bit-identical to libjpeg-turbo (checked by the author's bench/verify).

## Maintenance

Very active (82 commits between 2026-09-27 and 2026-10-01, two merged PRs from a second contributor adding the GNOME viewer and the Linux shared library) and MIT-licensed C that is small enough to vendor, but it is a weeks-old single-author project with 0 stars, no releases and commits co-authored with an AI coding assistant; treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness (bench/bench.m, bench/pngbench.m, bench/nbench.c), raw output (bench/results/results.txt, bench/results/m1.txt) and flags (Makefile: clang -O3 -march=native; libjpeg-turbo 3.1.2 built by scripts/get-deps.sh with -O3 -march=x86-64-v3) are public, but the main machine is only 'Intel i9 13th gen' with no SKU, the clang version is not stated, and the README says the 50 test photos are private and not in the repo, so the run cannot be reproduced; single-author first-party numbers are tier C, not A.
- **Verifier notes:** Downgraded from A to C: CPU SKU missing, compiler version missing, private test set. The like-for-like single-thread result is parity (1.04x i9, 1.09x M1); the gain is intra-image parallelism, which the caveats now say plainly. The README PNG headline (38 PNGs, \~43 ms vs Wuffs \~171 ms) differs from the 34-PNG table still in the README and in m1.txt.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/README.md>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/results/results.txt>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/results/m1.txt>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/bench.m>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/pngbench.m>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/nbench.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/scripts/get-deps.sh>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/LICENSE>
  - <https://github.com/gereoffy/jpeg-nitro>
  - <https://github.com/gereoffy/jpeg-nitro/commits>
  - <https://github.com/gereoffy/jpeg-nitro/tree/main/bench/results>
- **Sources the enricher read:**
  - <https://github.com/gereoffy/jpeg-nitro>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/README.md>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/scripts/get-deps.sh>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/bench.m>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/pngbench.m>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/nbench.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/verify.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/pngverify.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/results/results.txt>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/results/m1.txt>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/bench/results/ab_results.txt>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/nitrojpeg.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/nitrojpeg.h>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/nitro_os.h>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/nitropng.c>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/nitropng.h>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/src/libnitro.map>
  - <https://github.com/gereoffy/jpeg-nitro/tree/main/bench/results>
  - <https://github.com/gereoffy/jpeg-nitro/commits/main>
  - <https://github.com/gereoffy/jpeg-nitro/commit/29ba3122c7e84a37c79ffcc8ea9903c598cffdf0>
  - <https://github.com/gereoffy/jpeg-nitro/commit/21b7ac614f6303802ccc0b0227f0918ccee31812>
  - <https://github.com/gereoffy/jpeg-nitro/issues?q=is%3Aissue>
  - <https://github.com/gereoffy/jpeg-nitro/issues/3>
  - <https://github.com/gereoffy/jpeg-nitro/pulls?q=is%3Apr>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/gereoffy/jpeg-nitro`) · [data/wave10/enrich/raw/github_com_gereoffy_jpeg_nitro.json](../../../data/wave10/enrich/raw/github_com_gereoffy_jpeg_nitro.json) (enrichment confidence 0.8)

</details>
