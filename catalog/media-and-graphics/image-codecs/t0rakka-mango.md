# MANGO image codecs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> C++20 graphics library whose multi-threaded PNG/JPEG codecs beat single-threaded libpng and libjpeg, mostly on mango-encoded files.

| | |
|---|---|
| **Beats** | libpng (via find_module(PNG), version and zlib build not stated); 'libjpeg' is whatever jpeglib.h find_module(JPEG) linked, used through the libjpeg API one scanline at a time. Every current install path in docs/installation/setup.md and vcpkg.json installs libjpeg-turbo, but the library used for the i9-8950HK table run is not recorded. |
| **Claimed result** | README tables: PNG decode 3.2 ms vs libpng 57.3 ms (2560x1600) and 53.7 ms vs 379.5 ms (4833x5875); PNG encode 57.2 ms vs 820.5 ms and 287.0 ms vs 14051.3 ms; JPEG decode 23.3 ms vs libjpeg 197.8 ms (5184x3456) and 3.2 ms vs 32.9 ms (2560x1600); JPEG encode 18.5 ms vs 70.1 ms and 4.3 ms vs 16.3 ms. That is about 18x PNG decode and 8.5x JPEG decode on the first image of each pair (derived from page data). Mango ran its default multi-threaded path; the baselines ran single-threaded. |
| **Workload** | One timed run per library on one image each: PNG decode from memory and RGBA8 encode to a file (2560x1600 and 4833x5875 PNGs on an i7-11800H); JPEG decode from file and encode to file (5184x3456 and 2560x1600 JPEGs on an i9-8950HK). Milliseconds per image plus output size. |
| **Metric** | latency |
| **Hardware** | 11th Gen Intel Core i7-11800H @ 2.30GHz (PNG tables); Intel Core i9-8950HK @ 2.90GHz (JPEG tables) |
| **Compiler and flags** | Not stated for the README runs. Repository defaults: CMake Release build, ENABLE_SSE4 on and AVX/AVX2 off for the mango library, and png_benchmark adds -mavx2 -mpclmul on x86. |
| **Adoption** | 130 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/t0rakka/mango) · [benchmark](https://raw.githubusercontent.com/t0rakka/mango/HEAD/README.md) |

## Verdict

These are first-party README tables, present by October 2023 and never re-measured, with compiler and flags unstated. PNG on an i7-11800H: on 2560x1600, mango decoded in 3.2 ms against 57.3 ms for libpng, 37.7 for spng and 23.9 for wuffs, and encoded in 57.2 ms against 820.5 for libpng and 46.0 for fpng; on 4833x5875, decode 53.7 vs 379.5 ms and encode 287.0 vs 14051.3 ms. JPEG on an i9-8950HK: on 5184x3456, decode 23.3 vs 197.8 ms for 'libjpeg' (wuffs 185.9) and encode 18.5 vs 70.1 ms. Mango ran multi-threaded against single-threaded baselines, each library was timed once, and both PNG test files are byte-for-byte the size of mango's own output, which means they carry pLLD. The author's own 2023 README text said the JPEG decoder is 'up to three times the speed of jpeglib-turbo' in the best case and about equal in the worst, so the 8.5x table result implies either restart markers in the test file or a baseline other than libjpeg-turbo (not recorded).

## Use it when

- You control both ends of the pipeline (game or app assets, caches, screenshots) and can store PNGs and JPEGs written by mango, so later decodes take the parallel pLLD / Mango1 paths
- Interactive single-image latency on a many-core desktop, such as opening one large photo or texture, where using every core for one image matters more than total throughput
- Camera JPEGs that carry a DRI restart interval of exactly one MCU row, which mango's decoder splits across threads
- Projects already on mango (or wanting one C++ API for PNG, JPEG, DDS/KTX, EXR, HEIF, WebP and more) that need fast encode of RGB/RGBA PNGs and accept slightly larger files

## Skip it when

- Decoding arbitrary third-party PNGs: they lack the pLLD chunk, take the single-stream inflate path, and have no published mango numbers, so the 18x decode lead does not carry over
- Throughput servers that already decode many images at once on separate threads: the gain comes from per-image threading, not faster single-core code, and no single-threaded mango numbers exist
- Untrusted or integrity-sensitive input: the PNG parser skips every chunk CRC, the ISA-L and parallel paths inflate raw deflate after skipping the zlib header (no Adler-32 check), and decode_plld ignores per-segment decompression errors, so corrupt data can decode silently
- Smallest files: mango's PNGs were 24% and 19% larger than libpng's in its own tables (SUB filter only, zlib level 4, parallel segments), and its JPEG encoder always writes 4:4:4 with fixed standard Huffman tables
- Any build from before commit 2a974fb (2026-09-29) on x86, or before 17c019c on ARM: the default SIMD JPEG decode produced wrong pixels (issue #48), so pin to a fixed commit

## How it is fast

Most of the gap comes from splitting one image across cores. The PNG encoder (ImageEncodeOptions::parallel = true by default) writes a private pLLD chunk and up to 128 independently deflated segments, filtered with SUB only and compressed with ISA-L on x86; the decoder sees pLLD and inflates the segments in parallel on a ConcurrentQueue. The JPEG encoder emits a restart marker per MCU row plus a private APP14 'Mango1' offset table, so its own files, or standard files whose DRI equals one MCU row, get parallel Huffman decoding; other JPEGs decode Huffman serially and only hand iDCT and colour conversion to worker threads. Kernels are SSE2/SSE4.1/AVX2/AVX-512/NEON iDCT, PNG unfilter and colour conversion, chosen at compile time (the default CMake build enables SSE4 only).

## Compared with alternatives

For single-threaded PNG encode, pick fpng or fpnge: in mango's own table fpng (46.0 ms) beat multi-threaded mango (57.2 ms) on the 2560x1600 image. For arbitrary PNGs, pick wuffs, libspng or image-png; for parallel JPEG decode measured against a pinned libjpeg-turbo, pick jpeg-nitro. Pick mango when you write the files yourself and want one image decoded on many cores, or when you already use its C++20 framework.

## Integration

| | |
|---|---|
| **Form** | shared lib (BUILD_SHARED_LIBS ON by default) or static lib, built with CMake |
| **Dependencies** | fmt, zlib, libdeflate, zstd, lcms2, ISA-L, LZ4, bzip2 and simdjson per the vcpkg 'base' feature and the apt/brew lines; optional codec libraries (libjxl, OpenJPEG, libwebp, libavif, libheif, LibRaw, jxrlib) and Vulkan/FreeType/HarfBuzz; the benchmark examples also need libjpeg-turbo, libpng and blend2d |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20), CMake 3.19+; documented builds use g++ (apt/pacman), Xcode command-line tools (macOS) and MSVC with vcpkg (Windows); libjxl 0.9+ if JPEG XL is enabled |
| **Platforms** | x86-64 (default build compiles with SSE4.1/4.2; AVX, AVX2, AVX-512 opt-in), ARM/AArch64 NEON, Linux, macOS, Windows, Emscripten/wasm |
| **Thread safety** | not documented; decode and encode default to multithread = true and parallel = true and run work on mango's internal ConcurrentQueue thread pool |
| **Drop-in for the baseline** | no |

## Gotchas

- x86 SIMD JPEG iDCT bug: commit b1061f2 ('Optimize SSE2 iDCT', 2023-10-06) dropped 'r_xmm2 = row5', so the column pass subtracted from a leftover register. The 2026-08-15 refactor copied it into the AVX2 and AVX-512 kernels, and it was fixed in 2a974fb on 2026-09-29 (NEON in 17c019c). Issue #48 reports 254 decoding as 126, with up to 122-128 levels of error on 9-29% of pixels. The README JPEG tables were already in README.md before b1061f2, so the published timings predate the bug.
- In png_benchmark, --nomt only clears ImageDecodeOptions::multithread. decode_plld runs whenever a pLLD chunk is present, whatever that flag says, and the mango encode path always uses parallel = true, so the harness cannot produce a single-threaded mango row for its own files.
- The JPEG encode rows differ in settings, not only in speed: mango ran at quality 0.70, which scales its quant tables to about 14% of base (roughly libjpeg quality 93, derived from jpeg_encode.cpp), with 4:4:4 sampling. libjpeg ran at quality 95 with jpeg_set_defaults' 4:2:0 sampling and was fed one scanline per call.
- Mango's PNGs stay valid for other decoders (segment Adler-32s are combined), but pLLD is a private chunk. Its JPEGs carry RST markers every MCU row and an APP14 'Mango1' table; other decoders ignore both.

## Known shortcomings

- Table numbers come from examples/image/{png,jpeg}_benchmark/\*.cpp with the CPU named but compiler unstated; mango runs multithreaded by default against single-threaded baselines. The PNG test files are likely mango-encoded (pLLD parallel segments; input size equals mango output size), so the 18x decode is not general, and mango's PNG output is 19-24% larger. JPEG encode quality differs (95 vs 0.70) and the baseline 'libjpeg' is most likely libjpeg-turbo per the build docs, version unrecorded. An iDCT wrong-output bug was fixed 2026-09-29 (2a974fb).
- The README JPEG and PNG tables are about three years stale and predate the iDCT bug (b1061f2 of 2023-10-06 dropped 'r_xmm2 = row5', copied into the AVX2 and AVX-512 paths by c655646, fixed by 2a974fb on 2026-09-29; issue #48: 254 decoded as 126, up to 122-128 levels wrong on 9-29% of pixels), so the published numbers are from pre-bug code and were never re-measured. --nomt cannot disable pLLD parallel decode or parallel encode, so no single-thread mango number exists; the PNG parser skips chunk CRCs, the ISA-L and pLLD paths skip Adler-32 and per-segment decompress errors are ignored; JPEG encode is 4:4:4 at about libjpeg quality 93 (derived) against libjpeg q95 4:2:0; parallel Huffman decode needs a Mango1 APP14 marker or DRI equal to one MCU row. The author's 2023 README said 'up to three times' libjpeg-turbo while the table shows 8.5x, so the baseline or test file is unclear; fpng single-thread encode (46.0 ms) beats mango multithreaded (57.2 ms) in mango's own table.

## Caveats and trade-offs

Both benchmark programs run mango multi-threaded by default (g_option_multithread / args.multithread = true, --nomt to disable) against single-threaded libpng and libjpeg, and no single-threaded mango numbers are published. The PNG decode figures most likely apply to mango-written files: mango's encoder by default (ImageEncodeOptions::parallel = true) writes a custom pLLD chunk with independently compressed segments, its decoder then takes the parallel decode_plld path, and both test images have an input size equal to mango's own encoded size (3531 KB and 33598 KB). Ordinary PNGs go through the single-stream decode_std path, so the 18x decode lead does not carry over to arbitrary PNGs. In PNG encode mango uses zlib level 4 with parallel segments against libpng defaults, and its output is about 24% larger on the first image (3531 vs 2843 KB) and 19% larger on the second (33598 vs 28180 KB) (derived from page data). In JPEG encode libjpeg runs at quality 95 and mango at quality 0.70. Each library is timed once, including file I/O. png_benchmark prints the fractional digit as microseconds mod 10 rather than tenths of a millisecond (cosmetic, under 0.1 ms). Commit 2a974fb (2026-09-29) fixed a wrong-operand bug in the SSE/AVX2/AVX-512 JPEG iDCT that produced incorrect output, and 17c019c fixed the NEON iDCT; whether that bug was present when the JPEG tables were measured is not established (jpeg_idct.cpp was refactored on 2026-08-15). The two table pairs use different CPUs, and the README itself quotes randy408 (the libspng author's handle): 'I'm skeptical of those benchmarks.' The license is the standard zlib text under a 'MANGO' header; bundled third-party code was not audited.

Large C++20 graphics library (vector math, SIMD abstraction, virtual filesystem, Vulkan text) with image codecs inside, not a standalone codec. Mango's PNG encode output is larger than libpng's (3531 KB vs 2843 KB on the first image) and its JPEG output is slightly larger than libjpeg's.

## Maintenance

Actively maintained (last commit 2026-09-29, vcpkg version 3.8.2) under the zlib license, so copyable, but it is a large framework with many package-manager dependencies rather than a vendorable codec, and its benchmark tables are about three years older than the current code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** All README table numbers match the record and come from public first-party programs examples/image/png_benchmark/png_benchmark.cpp and examples/image/jpeg_benchmark/jpeg_benchmark.cpp with the CPU named, but the compiler and the exact flags used for the README runs are not stated, so it falls short of A and stays C.
- **Verifier notes:** Numbers are real and code-backed, but the headline gaps come mostly from multi-threading plus mango's own parallel-segment PNG layout (the test PNGs appear to be mango-encoded), and JPEG encode compares different quality settings; the enricher should say so. The JPEG baseline is most likely libjpeg-turbo going by the current build docs, but the README run's library is unrecorded. Recent iDCT correctness fixes (2026-09-29) should be noted; no evidence ties them to the 8950HK numbers.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/README.md>
  - <https://github.com/t0rakka/mango>
  - <https://github.com/t0rakka/mango/commits/main>
  - <https://github.com/t0rakka/mango/tree/main/examples>
  - <https://github.com/t0rakka/mango/tree/main/examples/image>
  - <https://github.com/t0rakka/mango/tree/main/examples/image/png_benchmark>
  - <https://github.com/t0rakka/mango/tree/main/examples/image/jpeg_benchmark>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/png_benchmark/png_benchmark.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/jpeg_benchmark/jpeg_benchmark.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/CMakeLists.txt>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/docs/installation/setup.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/source/mango/image/image_png.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/include/mango/image/encoder.hpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/include/mango/image/decoder.hpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/license>
  - <https://github.com/t0rakka/mango/commit/2a974fb4bef5337a766bb99ff76f14976cdf774e>
  - <https://github.com/t0rakka/mango/commits/main/source/mango/jpeg/jpeg_idct.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/README.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/png_benchmark/png_benchmark.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/jpeg_benchmark/jpeg_benchmark.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/examples/image/CMakeLists.txt>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/docs/installation/setup.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/source/mango/image/image_png.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/source/mango/jpeg/jpeg_decode.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/source/mango/jpeg/jpeg_encode.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/source/mango/jpeg/jpeg.hpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/include/mango/image/encoder.hpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/include/mango/image/decoder.hpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/HEAD/license>
  - <https://raw.githubusercontent.com/t0rakka/mango/54fe59e/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/5f72952/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/c8e30d9/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/b1061f2/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/f14b1d2/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/5e6fe84/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/95b0613/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/5972c66/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/cfa51e4/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/c655646/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/2a974fb/source/mango/jpeg/jpeg_idct.cpp>
  - <https://raw.githubusercontent.com/t0rakka/mango/c8e30d9/README.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/b1061f2/README.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/5972c66/README.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/cfa51e4/README.md>
  - <https://raw.githubusercontent.com/t0rakka/mango/c655646/README.md>
  - <https://github.com/t0rakka/mango/tree/main/source/mango/jpeg>
  - <https://github.com/t0rakka/mango/commits/main>
  - <https://github.com/t0rakka/mango/commits/main/README.md>
  - <https://github.com/t0rakka/mango/commits/main/source/mango/jpeg/jpeg_idct.cpp>
  - <https://github.com/t0rakka/mango/commit/2a974fb4bef5337a766bb99ff76f14976cdf774e>
  - <https://github.com/t0rakka/mango/commit/b1061f2>
  - <https://github.com/t0rakka/mango/commit/17c019c>
  - <https://github.com/t0rakka/mango/issues?q=is%3Aissue>
  - <https://github.com/t0rakka/mango/issues/48>
  - <https://github.com/t0rakka/mango/issues/3>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/t0rakka/mango`) · [data/wave10/enrich/raw/github_com_t0rakka_mango.json](../../../data/wave10/enrich/raw/github_com_t0rakka_mango.json) (enrichment confidence 0.8)

</details>
