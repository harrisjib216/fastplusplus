# libjxl fast_lossless (fjxl) encoder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> libjxl effort-1 lossless JPEG XL encoder (fjxl): about 19x faster than libpng, 43x faster than libwebp lossless.

| | |
|---|---|
| **Beats** | libpng and libwebp (lossless encoders) |
| **Claimed result** | QOIR benchmark: JXL_Lossless/f encode 106.48 MPixels/s vs libpng 5.49 (about 19x, derived from page data) and libwebp lossless 2.49 (about 43x, derived), with smaller files than libpng (CmpRatio 0.2171 vs 0.2423, about 10% smaller, derived). Decode is slower: 33.16 MPixels/s vs libpng 56.18 and libwebp 89.94. WangXuan95 CLIC2021 shootout (cjxl v0.9.0 -q 100 -e 1): 42.993 s compress, 57.650 s decompress, 1,648,242,164 bytes vs Pillow PNG (optimize=False) 334.791 s, 33.677 s, 2,003,016,524 bytes (derived: 7.8x faster encode, 18% smaller, 1.7x slower decode). |
| **Workload** | Lossless encode of the QOI benchmark suite with libjxl's experimental fast_lossless encoder (regular libjxl decoder) in the QOIR harness, single-threaded, vs libpng and libwebp lossless; WangXuan95's CLIC2021 shootout with cjxl -e 1. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults to CFLAGS '-Wall -O3'; adapter/jxl_adapter.cpp #includes libjxl's experimental/fast_lossless/fast_lossless.cc, so the FJXL encoder is built with -Wall -O3 -march=native -DFASTLL_ENABLE_AVX2_INTRINSICS=1 at fast_lossless's default effort 2; the libjxl library used for decoding (and the l3/l7 rows) is built separately per libjxl's README (commit and flags not stated); libpng and libwebp are Debian Bullseye system packages (build flags not stated) at default settings |
| **Adoption** | 3.7k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/libjxl/libjxl) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

Third-party run (nigeltao/qoir doc/full_benchmarks.txt, about 2022): the then-experimental fast_lossless.cc, compiled into the harness with gcc 10.2.1 -O3 -march=native and AVX2 intrinsics on one core of an Intel i5-10210U, encoded the QOI benchmark images at 106.48 MP/s versus 5.49 for Debian Bullseye libpng and 2.49 for libwebp lossless, at compression ratio 0.2171 versus 0.2423 and 0.1651. Measurement caveats: the harness never compares decoded pixels with the source, and the measured snapshot predates the PR #4291 palette fix (the same check-then-insert code is in v0.7.0 of July 2022 and was still reported in v0.11.1), so a few RGBA images with few colors may have been encoded lossily. That could flatter the ratio slightly but should not change the speed. The JXL decode rows also carry the adapter's inverted channel count. WangXuan95's single-threaded CLIC2021 run (i7-12700H, Windows 10, cjxl v0.9.0 -q 100 -e 1 launched once per image, so process start and PNM I/O are included) took 42.993 s versus 334.791 s for in-process Pillow PNG (zlib, optimize=False), with 18% smaller output.

## Use it when

- Lossless archiving or export of 8-bit RGB/RGBA screenshots, renders and photos when encoder time dominates and readers support JPEG XL: about 106 MP/s on one i5-10210U core with AVX2, versus 5.49 MP/s for default libpng, with smaller files.
- High-bit-depth lossless capture (up to 16-bit integer, or float16 input through libjxl) where PNG encoders are slow; the fast path handles 1-4 channels, alpha included.
- Large single images on many cores: groups are independent, so libjxl's thread pool (or your own FJxlParallelRunner in standalone mode) parallelizes the encode.
- A quick first-pass lossless JXL that a background job can later re-encode at effort 7+ (0.1548 versus 0.2171 compression ratio in the same QOIR run) without leaving the format.
- Embedding a JXL writer without libjxl: the standalone build of enc_fast_lossless.cc needs no libjxl, highway or brotli.

## Skip it when

- Consumers that need PNG or WebP, or that lack a JPEG XL decoder: the output is JXL only.
- Read-heavy workloads: in the same QOIR run libjxl decoded fjxl files at 33.16 MP/s versus 56.18 for libpng and 89.94 for WebP lossless (single-threaded), and in WangXuan95's CLIC2021 run djxl -e 1 output took 57.650 s to decode versus 33.677 s for Pillow PNG.
- Best ratio: WebP lossless (0.1651) and libjxl at effort 7 (0.1548) are 24-29% smaller than fjxl's 0.2171, if encode time allows.
- Raw encode speed whatever the format: in the same run fpnge (312.59 MP/s, PNG), fpng (192.16), QOIR (168.90), QOI (146.87) and Zpng (126.21) all encoded faster; fpnge and fpng still emit ordinary PNG.
- Frames that miss the fast path: CanDoFastLossless in lib/jxl/encode.cc rejects animation, cropped layers, frame names, frame-index boxes, extra channels other than one alpha, more than 16 bits, stripped alpha and LSB-padded bit depths, and those inputs silently fall back to the much slower general modular encoder at effort 1.

## How it is fast

It runs a fixed pipeline with no search (doc/encode_effort.md, e1 row): fixed YCoCg color transform, fixed ClampedGradient predictor, one entropy context with no MA tree, Huffman prefix codes instead of ANS, run-length-only LZ77 for zero runs, and a simple palette path (up to 512 colors found through a 64K-entry hash, 8-bit one-shot input only). Huffman tables come from a histogram sampled from only 2 x effort rows per 256-row group. The hot loop tokenizes and bit-packs 16 residuals at a time with SIMD (AVX2, AVX-512 or NEON: pshufb nibble lookups compute tokens, then bit fields merge from 16- to 32- to 64-bit lanes before one scalar flush). 256x256 groups are encoded independently, so a parallel runner can spread them across threads.

## Compared with alternatives

Pick fjxl over fpnge, fpng, QOI, QOIR or Zpng when you want a standardized, widely packaged format (JPEG XL) with files smaller than libpng's and can afford slower decode; pick fpnge or fpng when the output must stay PNG, and QOIR or Zpng when you control both ends and need faster decode.

## Integration

| | |
|---|---|
| **Form** | shared or static lib (libjxl via CMake), or source-drop of lib/jxl/enc_fast_lossless.cc built with -DFJXL_STANDALONE |
| **Dependencies** | libjxl: brotli, highway, and skcms or lcms2 (git submodules or system packages); standalone fjxl: none beyond the C++ standard library |
| **Minimum toolchain** | CMake 3.16+; C++17 when available (CMake falls back to C++14/11); Clang 7+ recommended; fjxl's AVX-512 path needs GCC 11+ or Clang 8+ |
| **Platforms** | Any; fjxl SIMD on x86-64 (AVX2, AVX-512 with runtime CPUID dispatch) only with compilers that do not define _MSC_VER (GCC, Clang; not MSVC or clang-cl), NEON on aarch64, scalar elsewhere |
| **Thread safety** | Use one JxlEncoder per thread; parallelism is internal through a JxlParallelRunner set with JxlEncoderSetParallelRunner (NULL means single-threaded). Standalone JxlFastLosslessEncode takes an FJxlParallelRunner callback or nullptr for sequential encoding. |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness bugs in this path were fixed late: before 0.12.0, palette detection checked all 8 pixels of an unrolled block before inserting any, so two colors in one block with the same hash slot could slip through and produce lossy output from 'lossless' -e 1 (issue #4287 on an emoji PNG, fixed by PR #4291 in June 2025); PR #4027 (December 2024) fixed a shift-by-64 in BitWriter::WriteMultiple behind issue #4026, 'Lossless images are not actually lossless'. Use 0.12.0 or later (the README also urges 0.12 for security fixes) and round-trip check critical archives.
- Default CMake builds compile out fjxl's AVX-512 code: the AVX3 highway target is off by default, and CMakeLists.txt then adds -DFJXL_ENABLE_AVX512=0. Pass -DJPEGXL_ENABLE_HWY_AVX3=ON to get it. The x86 SIMD block is enabled only when _MSC_VER is undefined, which rules out MSVC and also clang-cl (it defines _MSC_VER), the compiler of the official Windows release builds since 0.12, so Windows builds likely run fjxl's scalar path (inferred from the preprocessor guards, not measured).
- Effort numbers do not line up: libjxl e1 calls fjxl with effort=2, while the standalone API takes 0-127 (more rows sampled for the Huffman histogram, slower). Below effort 2, with streaming input, or above 8 bits, palette detection is skipped.
- Decode is the weak side: there is no fast decoder for the fast encoder (libjxl 0.12 notes a fix to its 'specialized decoding path for fast lossless', #4836), so measure decode on your target before switching an image store.

## Known shortcomings

- FJXL (lib/jxl/enc_fast_lossless.cc, effort 1; experimental/fast_lossless is gone) writes JPEG XL, not PNG: qoir full_benchmarks.txt rows 55/65/73 give 106.48 vs 5.49 MB/s libpng and 2.49 WebP lossless on encode, while its decode (33.16 MB/s) is slower than libpng's 56.18. Harness bug in adapter/jxl_adapter.cpp: decode num_channels is inverted (alpha_bits==0 ? 4 : 3), affecting the JXL decode rows only; the harness never checks round-trip pixels.
- Retiered A to C (retier-15): the 2022 QOIR run timed fast_lossless effort 1 whose palette detection could emit lossy output on RGBA few-colour images (issue #4287, present from v0.7.0 to v0.11.1, fixed PR #4291 in June 2025), and QOIR never round-trip checks, so the 0.2171 ratio may be slightly flattered. Default CMake disables the fjxl AVX-512 path; x86 SIMD is gated on !_MSC_VER so MSVC and clang-cl Windows builds are probably scalar; the fast path falls back on animation, crop and extra channels; the WangXuan95 timing includes cjxl.exe process start against in-process Pillow.

## Caveats and trade-offs

Different format: FJXL writes JPEG XL, not PNG, so readers need a JPEG XL decoder, and in the same run libjxl decodes at 33.16 MP/s vs libpng 56.18 and WebP lossless 89.94. Files are about 10% smaller than libpng's but about 31% larger than WebP lossless (CmpRatio 0.2171 vs 0.2423 and 0.1651, derived from page data). The table is a third party's (nigeltao/qoir, Nov 2022) and measured the then experimental/fast_lossless/fast_lossless.cc; that directory no longer exists, and the code now lives in lib/jxl/enc_fast_lossless.cc behind libjxl's effort-1 lossless mode (doc/encode_effort.md), which this run did not measure. libjxl's own README has no speed numbers. Regular libjxl lossless at effort 3 (5.35 MP/s) and effort 7 (0.57 MP/s) is not faster than libpng at encode. Baselines are Debian system builds with unstated flags at default settings; the libjxl commit and build flags are unstated. qoir's JXL decode adapter requests 4 output channels for images without alpha and 3 for images with alpha (inverted) and the harness never checks decoded pixels, so the JXL decode figures are approximate; the encode figure is unaffected. Measured with AVX2 intrinsics enabled. No libavif comparison (qoir excluded AVIF). [retier] Measured on code later fixed for a correctness bug: the 2022 fast_lossless effort-1 palette detection could emit lossy output on RGBA few-colour images (issue #4287, fixed PR #4291 in June 2025), and QOIR does no round-trip check, so the 0.2171 ratio may be slightly flattered. Different format: FJXL writes JPEG XL, so readers need a JPEG XL decoder, and libjxl decodes at 33.16 MP/s against libpng 56.18 and WebP lossless 89.94 in the same run; files are about 10% smaller than libpng's but about 31% larger than WebP lossless. Default CMake disables the fjxl AVX-512 path; x86 SIMD is gated on !_MSC_VER so MSVC and clang-cl builds are probably scalar; the fast path falls back on animation, crop and extra channels. The WangXuan95 timing includes cjxl.exe process start.

The fast-lossless mode trades ratio for speed (libjxl effort 7 compresses to CmpRatio 0.1548 but encodes at 0.57 MPixels/s). Needs JPEG XL support on the consumer side. The fast encoder uses AVX2 intrinsics. Single-threaded decode is slower than libpng and libwebp in that table.

## Maintenance

Actively maintained under the libjxl/Google JPEG XL project (0.12.0 released 2026-07-01, last commit 2026-09-29), BSD-3-Clause with a patent grant, packaged by major Linux distributions and Homebrew; copyable as part of libjxl or as one standalone .cc file, but use 0.12.0+ because of the e1 lossless corruption fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now C.
- **Tier reason:** The images/ aggregate rows 'JXL_Lossless/f' (0.2171, 106.48 Enc, 33.16 Dec MPixels/s), 'PNG/libpng' (0.2423, 5.49, 56.18) and 'WebP_Lossless' (0.1651, 2.49, 89.94) in nigeltao/qoir doc/full_benchmarks.txt match the record; adapter/jxl_adapter.cpp #includes the fast_lossless.cc encoder and script/run_full_benchmarks.sh builds it with gcc 10.2.1 -Wall -O3 -march=native -DFASTLL_ENABLE_AVX2_INTRINSICS=1 on a stated i5-10210U, against Debian Bullseye libpng and libwebp packages, so A holds for the encode claim.
- **Retiered** A to C: Lowered A to C under the rule that numbers measured on code later fixed for a correctness bug go to C: the QOIR run (November 2022) timed the fast_lossless encoder at effort 1 whose palette detection checked 8 pixels then inserted, missing hash collisions and producing lossy output from a lossless encode on RGBA few-colour images (issue #4287); the pattern is present from v0.7.0 (July 2022) through v0.11.1 and was fixed in PR #4291 (June 2025). QOIR never round-trip checks, so the 0.2171 compression ratio may be slightly flattered; encode speed is probably unaffected, but the measured code was not a correct lossless encoder on part of the corpus. The WangXuan95 shootout timing also includes cjxl.exe process start against in-process Pillow.
- **Verifier notes:** Numbers match lines 55, 65 and 73 (images/ aggregate) of full_benchmarks.txt; the file's Notes say PNG/libpng and WebP_Lossless are Debian Bullseye's packages. Harness bug: my_decode_jxl_lib in adapter/jxl_adapter.cpp sets num_channels = (info.alpha_bits == 0) ? 4 : 3, which mislabels output for all JXL decode rows but does not touch the encode number the record leads with. Metadata confirmed: BSD-3-Clause plus PATENTS grant, 3.7k stars, last commit 2026-09-29.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://github.com/nigeltao/qoir/commits/main/doc/full_benchmarks.txt>
  - <https://github.com/nigeltao/qoir/tree/main/third_party>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/jxl_adapter.cpp>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/enc_fast_lossless.cc>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/experimental/fast_lossless/fast_lossless.cc>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/doc/encode_effort.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/enc_frame.cc>
  - <https://github.com/libjxl/libjxl>
  - <https://github.com/libjxl/libjxl/commits>
- **Sources the enricher read:**
  - <https://github.com/libjxl/libjxl>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/tools/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/doc/encode_effort.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/doc/building_and_testing.md>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/enc_fast_lossless.cc>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/enc_fast_lossless.h>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/encode.cc>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/jxl/enc_frame.cc>
  - <https://raw.githubusercontent.com/libjxl/libjxl/HEAD/lib/include/jxl/encode.h>
  - <https://raw.githubusercontent.com/libjxl/libjxl/v0.7.0/experimental/fast_lossless/fast_lossless.cc>
  - <https://github.com/libjxl/libjxl/issues/4026>
  - <https://github.com/libjxl/libjxl/pull/4027/files>
  - <https://github.com/libjxl/libjxl/issues/4287>
  - <https://github.com/libjxl/libjxl/pull/4291>
  - <https://github.com/libjxl/libjxl/pull/4291/files>
  - <https://github.com/libjxl/libjxl/commit/986561b.diff>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/jxl_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://github.com/google/jpegli>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libjxl/libjxl`) · [data/wave10/enrich/raw/github_com_libjxl_libjxl.json](../../../data/wave10/enrich/raw/github_com_libjxl_libjxl.json) (enrichment confidence 0.8)

</details>
