# fpnge

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Two-file AVX2/SSE4.1 PNG encoder; about 57x libpng's default encode speed on the QOI corpus, files about 15% larger.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | QOIR benchmark: PNG/fpnge encode 312.59 MPixels/s vs PNG/libpng 5.49 (about 57x, derived from page data) at CmpRatio 0.2798 vs libpng 0.2423 (about 15% larger files, derived). fpnge README: speed on a single core is anywhere from 180 to 800 MP/s on a Threadripper 3970x (no libpng comparison on that page). |
| **Workload** | Lossless PNG encode speed (encoder only) on the QOI benchmark suite in the QOIR harness; fpnge README quotes 180 to 800 MP/s per core on a Threadripper 3970x. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded; fpnge README: Threadripper 3970x |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults to CFLAGS '-Wall -O3' and compiles each codec adapter with -march=native; fpnge.cc is vendored in qoir third_party/fpnge (a 2022 snapshot) and #included into adapter/png_fpnge_adapter.cpp, so fpnge is built with -Wall -O3 -march=native (AVX2 on the i5-10210U); libpng is Debian Bullseye's system package (build flags not stated) driven through its simplified API at default settings |
| **Adoption** | 113 stars; measured as a comparator in nigeltao/qoir's benchmarks |
| **Last commit** | 2025-10-09 |
| **Links** | [repository](https://github.com/veluca93/fpnge) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

In Nigel Tao's QOIR harness (gcc 10.2.1, -O3 -march=native, Intel i5-10210U, one thread, 5 repetitions per image, totals over the QOI benchmark corpus), a 2022 fpnge snapshot at its default level encoded 312.59 MP/s against 5.49 MP/s for Debian Bullseye's libpng through png_image_write_to_memory at default zlib settings (about 57x), with CmpRatio 0.2798 vs 0.2423 (about 15% larger files). The harness has no fpnge decoder, so it never checks fpnge's output; correctness rests on upstream's round-trip test.sh.

## Use it when

- Screenshot, screen-recording, game-capture or render-output pipelines on x86 where PNG encode time is the bottleneck and files 7-60% larger than libpng's are acceptable.
- Photographic or textured RGB/RGBA images: in the QOIR data the speedup over libpng is largest there (84x on Kodak, 95x on Tecnick) and the size penalty smallest (7-10%).
- Large frames encoded on one core per image, where it stayed around 280-360 MP/s across the QOIR subsets on an i5-10210U.
- When you need real .png output (unlike QOI, QOIR or Zpng), including 16-bit or HDR (cICP PQ) PNGs.

## Skip it when

- ARM or any non-x86 target: fpnge.cc stops with '#error Requires SSE4.1 support minium' (Apple Silicon request #29 closed with no port).
- Size-sensitive storage or web delivery: on flat synthetic content its LZ77 finds only zero-residual runs, so files were 59% larger than libpng's on icon_512 and 33% larger on screenshot_web; run an optimiser such as oxipng afterwards or use libpng/zlib-ng at a higher level.
- Many tiny images: on 64x64 icons it fell to 82.45 MP/s, 2.3x slower than fpng (193.31 MP/s) and with larger files than fpng, because table construction and buffer setup are per call.
- Indexed-colour, 1/2/4-bit, interlaced or palette PNGs: only 8/16-bit gray, gray+alpha, RGB and RGBA are written.
- Decoding: it is encoder only; pair it with libspng, Wuffs or image-png for reads.

## How it is fast

It replaces zlib's general LZ77 search with a single dynamic-Huffman deflate block whose only matches are distance-1 runs over whole SIMD vectors of zero filter residuals. The Huffman code is built from symbol counts of a few centre rows and constrained so residual bytes 16-239 share one code length, letting pshufb lookups on 16-entry tables (first16/last16/mid) produce code lengths and bits for 32 bytes at a time, with BMI2 PEXT (skipped when tuning for Zen 1/2) to pack them. Per-row PNG filter choice is made by costing all four predictors with those same SIMD tables (exact at the default level, approximate at level 3), Adler-32 is accumulated with psadbw, and the chunk CRC uses PCLMULQDQ folding.

## Compared with alternatives

Pick fpnge over fpng when you only encode and run on AVX2 machines: in the same QOIR run it encoded 1.63x faster (312.59 vs 192.16 MP/s) with 10% smaller output, though fpng is portable C++ with a decoder and wins on tiny images. Pick it over QOI, QOIR or Zpng when the output must be a standard .png; pick libjxl's fast_lossless (106.48 MP/s, 22% smaller files) when JPEG XL output is acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (the fpnge CLI in fpnge_main.cc uses lodepng only to read input) |
| **Minimum toolchain** | C++14 (std::index_sequence, constexpr lookup tables); GCC, Clang, or MSVC since the November 2023 forceinline fix; must be compiled with at least -msse4.1, and -mavx2 -mbmi2 -mpclmul (or -march=native as build.sh does) for the fast path |
| **Platforms** | x86 and x86-64 only; SSE4.1 required, AVX2 for full speed; instruction set fixed at compile time, no runtime dispatch |
| **Thread safety** | Reentrant: fpnge.cc has no mutable global state (only constexpr tables), so separate FPNGEEncode calls can run on separate threads; each call is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- No output capacity is passed to FPNGEEncode; it trusts the caller's buffer. FPNGEOutputAllocSize (1024 + (2\*bytes\*width\*channels + 1)\*height) ignores additional_chunks, so adding an ICC or EXIF chunk larger than the slack can overflow the heap unless you add the chunk sizes yourself. Issue #25 (fixed 2023-05-22) was an underestimate of this kind, and issue #31 (heap corruption on one 4-channel image, 2024) was closed without a documented cause.
- The whole image goes into one IDAT chunk and one deflate block, and the chunk length is written as 32 bits, so outputs above PNG's 2^31-1 chunk limit (multi-gigapixel 16-bit images) would be invalid.
- A binary built with -march=native or -mavx2 dies with an illegal instruction on CPUs without AVX2/BMI2; the default x86-64 target (SSE2 only) does not compile at all. Upstream CI (test.sh) round-trips the libjxl test PNGs through ImageMagick compare for all four speed levels, but only for the -march=native build on a GitHub runner, so the SSE4.1 and MSVC paths are untested.
- fpnge.h defines FPNGEOutputAllocSize and FPNGEFillOptions as plain inline functions inside extern "C"; a C caller built without optimisation may get an undefined reference to FPNGEOutputAllocSize, since under C99 inline rules no external definition is emitted.

## Known shortcomings

- Tier A on qoir full_benchmarks.txt rows 64/65 (312.59 vs 5.49 MB/s, 57x; same harness, 2022 snapshot). Encoder only; files about 15% larger than libpng's. The baseline libpng is the Debian package build, so the ratio sits above the 50x unstated-baseline-flags threshold; kept A because the encoder flags and the distro baseline are reproducible. Open issues #25 and #31 report memory bugs.
- FPNGEEncode takes no output capacity and FPNGEOutputAllocSize ignores additional_chunks, so large custom chunks can overflow the heap (API hazard outside the benchmark path); #31 (heap corruption) was closed without a documented fix; output is a single IDAT with a 32-bit length. Size penalty is 7-10% on photos but 33-59% on screenshot_web and icon_512, and on icon_64 fpnge (82.45 MP/s) is 2.3x slower than fpng; x86 only (#error without SSE4.1). QOIR never decodes fpnge's output (upstream test.sh round-trips libjxl PNGs through ImageMagick compare, -march=native build only).

## Caveats and trade-offs

Encoder only (no decoder); output is standard PNG that any decoder reads. The speed-up comes from a third party's harness (nigeltao/qoir, Nov 2022), not from fpnge's README, which has no libpng comparison. Trade-off: fpnge's files are about 15% larger than libpng's in that run (CmpRatio 0.2798 vs 0.2423, derived from page data). Baseline is Debian Bullseye's libpng at the simplified API's default zlib settings with unstated distro build flags; faster libpng settings were not tried, and the 57x ratio is above the 50x level at which unstated baseline flags usually cap a tier. One laptop-class CPU (i5-10210U), gcc 10.2.1, and a 2022 fpnge snapshot; upstream has changed since (BGR input, custom chunks, a simpler predictor in 2025), so current speed may differ. SIMD code is x86-only (AVX2 or SSE4.1) and the author calls it a proof of concept. Robustness: issue #25 (FPNGEOutputAllocSize underestimate causing a heap overflow on a 1x64000 grayscale image, fixed 2023-05-22; qoir's vendored copy uses a generous 1024 + 2\*bytes\*channels\*w\*h estimate) and issue #31 (memory corruption on one 4-channel image, opened 2024-09-29, closed). The harness never checks the encoded output.

Encoder only, no decoder. AVX2 (x86 only); QOIR notes no ARM SIMD. Supports 8 and 16 bit content, 1 to 4 channels, optional cICP chunk for HDR. Uses a fixed special Huffman table so files are larger than libpng's.

## Maintenance

Maintained at low intensity by its author (last commit 2025-10-09, a simpler Paeth predictor in February 2025, BGR input and custom chunks in March 2024); Apache-2.0, two source files, easy to vendor, but the README still calls it a proof of concept and there is no NEON port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The images/ aggregate rows 'PNG/fpnge' (0.2798 CmpRatio, 312.59 Enc MPixels/s, nan Dec) and 'PNG/libpng' (0.2423, 5.49) in nigeltao/qoir doc/full_benchmarks.txt match the record; the harness is public (script/run_full_benchmarks.sh, test/benchmarks.c, adapter/png_fpnge_adapter.cpp) with gcc 10.2.1, -O3 -march=native and an i5-10210U stated, against Debian Bullseye's libpng package. The 57x ratio exceeds 50x, but the encoder's flags are stated, the baseline is a reproducible distro build, the qoir README's normalized table gives the same ratio, and the gap is explained by libpng's default deflate versus a single-pass AVX2 Huffman/RLE encoder that writes larger files, so the implausibility cap was not applied.
- **Verifier notes:** Numbers match lines 64 and 65 (images/ aggregate) of full_benchmarks.txt; the file's Notes say PNG/libpng is Debian Bullseye's libpng (the distro package). Kept A although 312.59/5.49 = 57x is above the 50x threshold of the unstated-flags cap; a strict reading of that rule would cap it at C. last_commit 2025-10-09 keeps it 'active' only until 2026-10-09.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://github.com/nigeltao/qoir/commits/main/doc/full_benchmarks.txt>
  - <https://github.com/nigeltao/qoir/tree/main/third_party>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_fpnge_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/fpnge/fpnge.cc>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/fpnge/fpnge.h>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/README.md>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/fpnge.cc>
  - <https://github.com/veluca93/fpnge>
  - <https://github.com/veluca93/fpnge/commits>
  - <https://github.com/veluca93/fpnge/commits/main>
  - <https://github.com/veluca93/fpnge/issues?q=is%3Aissue>
  - <https://github.com/veluca93/fpnge/issues/25>
  - <https://github.com/veluca93/fpnge/issues/31>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/README.md>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/fpnge.cc>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/fpnge.h>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/fpnge_main.cc>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/build.sh>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/test.sh>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/.github/workflows/test.yml>
  - <https://raw.githubusercontent.com/veluca93/fpnge/HEAD/LICENSE>
  - <https://github.com/veluca93/fpnge>
  - <https://github.com/veluca93/fpnge/commits/main>
  - <https://github.com/veluca93/fpnge/issues?q=is%3Aissue>
  - <https://github.com/veluca93/fpnge/issues/23>
  - <https://github.com/veluca93/fpnge/issues/26>
  - <https://github.com/veluca93/fpnge/issues/29>
  - <https://github.com/veluca93/fpnge/issues/31>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_fpnge_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/fpnge/fpnge.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/veluca93/fpnge`) · [data/wave10/enrich/raw/github_com_veluca93_fpnge.json](../../../data/wave10/enrich/raw/github_com_veluca93_fpnge.json) (enrichment confidence 0.85)

</details>
