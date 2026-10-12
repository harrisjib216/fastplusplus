# pngenc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟡 stale

> Small OpenMP-parallel C PNG encoder with stored, Huffman-only and RLE deflate paths; about 11x faster than libpng single-threaded in those modes.

| | |
|---|---|
| **Beats** | libpng 1.6 (with zlib) |
| **Claimed result** | README table (ms, libpng 1.6 vs pngenc 1 thread vs pngenc multi-threaded, 1920x1080x24-bit image, Ryzen 7 3700X): Uncompressed 9 vs 0.8 vs 0.2; Huffman Only 82 vs 7.3 vs 1.2; RLE 84 vs 30 vs 4; Full LZ77 \~150 vs N/A vs N/A. That is about 11x (uncompressed), 11x (Huffman only) and 2.8x (RLE) single-threaded, and 45x, 68x and 21x multi-threaded (derived from page data). README says 'up to an order of magnitude faster' at 'the same compression rates' as libpng/zlib. |
| **Workload** | Encode one 1920x1080 24-bit image to PNG in three low-compression modes (uncompressed, Huffman-only, RLE). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 3700X |
| **Compiler and flags** | Not stated for the README table. The repo's CMakeLists.txt builds pngenc with -march=native -mtune=native -O3 -fopenmp (GCC/Clang) or /openmp /arch:AVX2 (MSVC); how libpng was built is not stated. |
| **Adoption** | 3 stars |
| **Last commit** | 2024-08-10 |
| **Links** | [repository](https://github.com/GregorBudweiser/pngenc) · [benchmark](https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/readme.md) |

## Verdict

The author's README table (one unpublished 1920x1080 8-bit RGB image, Ryzen 7 3700X) gives Huffman-only 7.3 ms single-threaded vs 82 ms for libpng 1.6 (about 11x), RLE 30 vs 84 ms (2.8x) and uncompressed 0.8 vs 9 ms, and 1.2, 4 and 0.2 ms multi-threaded (ratios derived from page data). No compiler, flags, libpng filter or zlib settings, or libpng harness are published, and the repo's perf_mt.c only times pngenc 20 times into a null callback on a data.bin that is not in the repo. The bugs found affect 16-bit images and short chunks, not the 8-bit 1080p numbers.

## Use it when

- Dumping screenshots, frame captures, render or debug outputs to valid 8-bit PNG where latency matters more than file size.
- Multi-core x86-64 machines that can put all cores on one image: the README reports 1.2 ms for a Huffman-only 1080p RGB frame with OpenMP vs 82 ms for libpng.
- Streaming output: the callback API hands out each IDAT chunk as soon as its turn comes, so no full compressed buffer is needed.
- Vendoring a zlib-licensed C encoder (about ten source files) that does not depend on zlib or libpng.

## Skip it when

- Size-competitive PNGs: there is no LZ77 mode, the README's Full LZ77 row has no pngenc number, and the 'same compression rates as libpng/zlib' claim comes with no file sizes.
- 16-bit images in Huffman-only, RLE or AUTO mode: a byte-swap bug makes them decode to wrong pixel values (see gotchas). In the uncompressed mode 16-bit samples are copied in host order with no big-endian swap.
- Small or highly compressible images: a compressed chunk of roughly 64 to 103 bytes can get a wrong IDAT CRC (see gotchas), which strict decoders such as libpng reject.
- Portable binaries or big-endian targets: x86 builds use -march=native or /arch:AVX2, and the chunk and stored-block headers are written by copying little-endian structs.
- Projects that need maintenance: it is a self-described hobby project with 3 stars and its last commit was on 2024-08-10.

## How it is fast

It skips LZ77 match search entirely: every row gets the fixed Sub filter (no per-row filter heuristic), then either literal-only Huffman coding (like zlib Z_HUFFMAN_ONLY) or distance-1 run-length matches (like Z_RLE), with length-limited canonical codes built from a 4-way 16-bit-counter histogram and an encoder that packs three codes per 64-bit window with unaligned stores. The image is cut into row chunks (default 512 KiB of filtered data); OpenMP threads encode the chunks in parallel as independent byte-aligned deflate blocks (each ended with an empty stored block, as a zlib sync flush does), emit them in order as separate IDAT chunks, and merge per-chunk checksums with adler32_combine. Checksums use AVX2 Adler-32 (adapted from a fork of fpng) and PCLMULQDQ CRC-32 folding (Intel white-paper method).

## Compared with alternatives

fpnge and fpng are faster per core and compress better (in the QOIR benchmark fpnge encodes about 57x faster than libpng with files about 15% larger), and mtpng parallelizes full deflate; pick pngenc only if you specifically want OpenMP-parallel Huffman-only or RLE encoding of 8-bit images from a tiny zlib-licensed C codebase and can accept those file sizes.

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake add_library SHARED) or source-drop of the source/pngenc/\*.c files |
| **Dependencies** | libc and OpenMP (libgomp, libomp or MSVC /openmp) |
| **Minimum toolchain** | C99 (-std=gnu99), CMake 3.0; README says tested with GCC/MinGW, Clang and MSVC |
| **Platforms** | little-endian x86-64 (AVX2 Adler-32 and PCLMUL CRC-32 chosen at run time, but the intrinsics are compiled in unconditionally, so a GCC/Clang build needs an AVX2/PCLMUL build host for -march=native to accept them); ARM via scalar paths plus -mfpu=neon on armv7l (commit 'Fix non-x86 builds', 2022-12-07) |
| **Thread safety** | Not documented. An encoder owns per-thread scratch buffers, so share one encoder only serially. Each encode is internally parallel and calls omp_set_num_threads, which changes the calling thread's OpenMP setting. |
| **Drop-in for the baseline** | partial — different API (descriptor plus callback) and encoder only; it matches libpng only when libpng is run with the Z_HUFFMAN_ONLY or Z_RLE strategies or at level 0 |

## Gotchas

- 16-bit correctness bug (splitter.c, prepare_data_filtered): after the Sub filter, the byte-swap loop stores dst[i+1] = src[i] (the raw low byte) instead of the filtered byte, so for every pixel after the first in a row, low bytes accumulate on decode (reproduced with a Python re-implementation of the loop: 0x1234 0x5678 0x9ABC decodes as 0x1268 0x56f0 0x9a78 in the second pixel). The 16-bit integration test only checks the return code and uses byte-symmetric values (0x0000, 0x8888, 0xFFFF), so it cannot catch this.
- CRC bug (crc32.c, crc32_hw): when len &gt;= 64 but fewer than 64 bytes remain after aligning to 64 bytes, crc32_pclmul still folds a full 64-byte block (aligned_len = 0 is not checked), so those bytes are counted twice and the IDAT CRC is wrong. Chunk data starts 8 bytes into a 16-byte-aligned buffer, so short compressed chunks (about 64 to 103 bytes with glibc's mmap alignment) are affected. Large 1080p chunks are not, so the README numbers stand.
- MSVC x64 only: the SSE2 Sub-filter loop tests i &lt; bytes_per_row - 32 in uint64_t, which wraps around for rows narrower than 32 bytes and reads and writes out of bounds; rows of exactly 32 bytes read src[-c].
- pngenc_create_encoder does not check its malloc results, pngenc_write_file leaks the encoder when encoding fails, and every encoder creation rewrites a global CRC table and CPU-feature flags.

## Known shortcomings

- README numbers only: no libpng timing code in the repo (tests/perf_mt.c times pngenc alone on an unpublished data.bin). The speed comes from skipping LZ77 (stored, Huffman-only or RLE blocks with a fixed Sub filter), so output is much larger than libpng's; the table gives no sizes.
- Correctness bugs (not behind the 8-bit 1080p numbers): splitter.c's 16-bit path stores dst[i+1]=src[i] raw rather than filtered, so Huffman, RLE and AUTO 16-bit output decodes wrong (confirmed with a Python re-implementation of the loop) while the uncompressed 16-bit path never byte-swaps, and the test uses byte-symmetric values and checks only the return code; crc32_hw calls crc32_pclmul when aligned_len is 0, folding 64 bytes twice, so compressed IDAT chunks of about 64-103 bytes (small or flat images) get a wrong CRC; MSVC x64 uint64 underflow for rows under 32 bytes. Builds with -march=native or /arch:AVX2 and compiles AVX2 and PCLMUL intrinsics unconditionally; little-endian only; omp_set_num_threads side effect; no libpng harness or output sizes.

## Caveats and trade-offs

Single first-party table, one unpublished image and one CPU; compiler, flags and the libpng timing harness are not published (tests/perf_mt.c times pngenc only, on a data.bin file that is not in the repo). PNG trade-off: pngenc only implements stored, Huffman-only (Z_HUFFMAN_ONLY) and RLE deflate with a fixed horizontal (Sub) row filter (no filter for the uncompressed mode), so its output is much larger than libpng at its default LZ77 level; the README's Full LZ77 row (libpng \~150 ms) has no pngenc counterpart, and the table gives no file sizes to back the 'same compression rates' claim. The comparison is against libpng's low-effort strategies, which the README itself calls a valid trade-off. The multi-threaded column uses OpenMP across the image, while libpng is single-threaded. A later mode (PNGENC_AUTO, Huffman-only falling back to RLE) is not in the README table. Hobby project for learning, per the README.

Encoder only. Supports only uncompressed, Huffman-only and RLE modes (full LZ77 is 'N/A'), so it does not replace libpng at default compression levels. Needs OpenMP for the multi-threaded numbers; tested with gcc/mingw, clang and MSVC. Author calls it a hobby project; the CRC32 code is adapted from Mark Adler under a zlib-compatible license.

## Maintenance

Stale (last commit 2024-08-10, which added PNGENC_AUTO; 3 stars; one issue, a closed 2022 ASan odr-violation report) but zlib-licensed and small enough to vendor, provided you fix the 16-bit swap and the short-buffer CRC path, or keep to 8-bit images.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (1920x1080x24-bit image, AMD Ryzen 7 3700X) compares libpng 1.6 with pngenc single- and multi-threaded and the numbers match the record, but it is first-party and states no compiler, flags or harness. The repo has pngenc-only timing tests (tests/perf_mt.c, tests/perf_huffman.c, which read an unpublished data.bin image) and no libpng timing code, so it cannot be A.
- **Verifier notes:** Numbers, hardware, license (zlib license; crc32 code by Mark Adler under a zlib-compatible license), 3 stars and last commit 2024-08-10 (stale) all check out. The speed comes from skipping LZ77 entirely, so it suits fast snapshot or screenshot dumps rather than size-competitive PNGs.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/readme.md>
  - <https://github.com/GregorBudweiser/pngenc>
  - <https://github.com/GregorBudweiser/pngenc/commits>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/CMakeLists.txt>
  - <https://github.com/GregorBudweiser/pngenc/tree/master/tests>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/perf_mt.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/perf_huffman.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/pngenc.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/readme.md>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/CMakeLists.txt>
  - <https://github.com/GregorBudweiser/pngenc/tree/master/source/pngenc>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/pngenc.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/pngenc.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/splitter.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/splitter.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/deflate.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/deflate.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/huffman.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/huffman.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/crc32.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/crc32.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/adler32.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/adler32.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/png.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/png.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/image_descriptor.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/image_descriptor.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/utils.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/utils.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/callback.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/source/pngenc/main.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/perf_mt.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/perf_huffman.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/integration_save_png16.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/integration_save_png.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/integration_pipeline.c>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/common.h>
  - <https://raw.githubusercontent.com/GregorBudweiser/pngenc/HEAD/tests/unit_deflate.c>
  - <https://github.com/GregorBudweiser/pngenc/issues?q=is%3Aissue>
  - <https://github.com/GregorBudweiser/pngenc/commits>
  - <https://github.com/wooosh/fpng>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/gregorbudweiser/pngenc`) · [data/wave10/enrich/raw/github_com_gregorbudweiser_pngenc.json](../../../data/wave10/enrich/raw/github_com_gregorbudweiser_pngenc.json) (enrichment confidence 0.7)

</details>
