# colortwist

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Small BSD-2 C++ library for 3x4 colour-matrix transforms on interleaved RGB24/RGB48; 2.6-4.9x faster than IPP's ColorTwist32f.

| | |
|---|---|
| **Beats** | Intel IPP ippiColorTwist (and a plain C reference loop) |
| **Claimed result** | RGB48 on i7-8700K, MSVC 19.27: IPP 1720.98 MB/s vs AVX 3291.02, AVX2 4297.74, AVX3 5175.55 MB/s (3.0x IPP for AVX3, derived from page data); RGB24: IPP 892.93 vs AVX3 2966.55 MB/s (3.3x, derived from page data). Ryzen 7 4700U, MSVC: RGB48 IPP 1836.64 vs AVX3 5572.38 MB/s (3.0x, derived from page data). i9-12900K, MSVC 19.31: RGB48 IPP 2203.86 vs AVX3 9091.08 MB/s (4.1x), RGB24 IPP 1116.93 vs AVX3 5441.54 MB/s (4.9x) (both derived from page data). Single-threaded on both sides. |
| **Workload** | Colour twist (3x4 matrix times RGB triple) on a 2048x2048 RGB48 and RGB24 bitmap, MB/s, repeated 100 times by test/testcolortwist.cpp, outputs compared against the C and IPP results. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700K @ 3.70GHz, AMD Ryzen 7 4700U, Intel Core m3-6Y30 and Intel Core i9-12900K for the IPP comparisons (Windows, MSVC/icl). Linux gcc, Raspberry Pi 3b/4, Snapdragon 7c, Apple M2 and OrangePi RV2 (RISC-V) rows compare only against the plain C version. |
| **Compiler and flags** | MSVC 19.27.29112 and 19.31.31106.2, Intel icl 19.1.3.311, gcc 10.2.0 / 7.5.0 (no IPP rows for gcc). The README build steps use cmake --build . --config Release (CMake's default MSVC Release flags). /arch:AVX2 on colortwist_avx.cpp under MSVC, -mfma -mavx2 (AVX file) and -msse4.1 (SSE file) under GCC/Clang (lib/CMakeLists.txt). Static MSVC runtime (CMAKE_MSVC_RUNTIME_LIBRARY MultiThreaded). IPP is linked statically from ippccmt.lib and ippcoremt.lib (test/CMakeLists.txt); the IPP version is not stated. |
| **Adoption** | 2 stars |
| **Last commit** | 2025-12-28 |
| **Links** | [repository](https://github.com/ptahmose/colortwist) · [benchmark](https://github.com/ptahmose/colortwist) |

## Verdict

In the author's test/testcolortwist.cpp (100 repeats, MB/s counted on source bytes, every output checked within 1 LSB of the float C loop), the single-threaded AVX2+FMA path beat statically linked IPP ippiColorTwist32f_16u_C3R on 2048x2048 RGB48 by 3.0x on an i7-8700K (5176 vs 1721 MB/s, MSVC 19.27), 2.9x with icl 19.1.3.311, 3.0x on a Ryzen 7 4700U, 3.2x on a Core m3-6Y30 and 4.1x on an i9-12900K (9091 vs 2204 MB/s, MSVC 19.31); on RGB24 the margin was 2.6-4.9x (e.g. 2967 vs 893 MB/s on the i7-8700K). Ratios are derived from the page data, and the IPP version is not stated. The missing ippInit() call should not matter for IPP 9.0 or later, which auto-initialises its dispatcher on the first call (Intel documentation, seen as a search snippet). Note that the RGB48 test matrix (rows 1,2,3,4 / 5,6,7,8 / 1.1,1.2,1.3,1.4) on full-range random 16-bit input saturates about 96% of output samples (derived), so the 1-LSB check on RGB48 mostly compares clamped values; this does not change the throughput comparison, since both sides process the same data, but the unsaturated arithmetic is checked on only about 4% of samples (the RGB24 matrix leaves about 57% unsaturated).

## Use it when

- You apply a fixed 3x4 colour matrix (white balance, channel mixing, YCbCr-like affine transforms, camera colour correction) to large interleaved RGB24 or RGB48 frames and IPP's ColorTwist or a scalar loop is a hotspot.
- 16-bit microscopy or scientific RGB48 images on x86-64 with AVX2+FMA, where the README shows 2.9-4.1x over IPP and roughly 4-5x over the plain C loop on one core.
- You want to drop IPP as a dependency for this one operation and need a BSD-2 source drop of about a dozen files with no third-party runtime dependencies.
- Mixed fleets: the same API has NEON (ARM32/ARM64, including Windows on ARM and Apple M-series), SSE4.1 and RISC-V RVV (rv64gcv) back ends with numbers in the README for each.

## Skip it when

- Anything beyond an affine matrix: no transfer curves, gamma, ICC profiles, LUTs or chromatic adaptation; use a CMS for those.
- Other pixel layouts or types: no 4-channel (RGBA/AC4), planar, BGR-specific, signed 16-bit or float images, and in-place operation is not documented; IPP covers all of these.
- Multi-core throughput: it is single-threaded, so you must tile the image across threads yourself.
- You need a maintained, widely used dependency: the README calls it a finger exercise in SIMD optimisation, it has 2 stars, no releases, no CI, and every PR is by the author.
- Bit-exact reproducibility with a scalar reference: the SIMD paths round to nearest-even via cvtps (and NEON adds 0.5 then truncates on older GCC), so they can differ from the C path by 1 LSB.

## How it is fast

Each x86 iteration handles 8 pixels: pshufb shuffles and 16-bit blends deinterleave the packed RGB into planar R, G and B vectors, which are widened to int32, converted to float, and run through three FMA chains per channel (_mm256_fmadd_ps). The results are converted with _mm256_cvtps_epi32, saturated with packus, re-interleaved with pshufb plus OR, and written as exactly 48 bytes (RGB48) or 24 bytes (RGB24, via a masked store). The ARM path uses vld3/vst3 structure loads and stores with vmlaq_f32, and the RISC-V path uses vlseg3/vsseg3 segment loads with vfmacc and vnclipu. Nothing is threaded; the gain is purely SIMD width with no per-pixel branches.

## Compared with alternatives

Pick colortwist over moxcms or the Little-CMS fast_float plugin when all you need is a fixed affine 3x4 matrix on 8- or 16-bit RGB with no profiles or curves, and over OpenCV's cv::transform (or the FastOpenCV kernels) when you want a tiny dependency-free BSD-2 kernel rather than a CV framework. For YUV/RGB conversion, yuv2rgb, sparkyuv or libyuv are the right tools instead.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (IPP is optional and used only for the comparison path); the unittests subdirectory fetches googletest v1.12.0 with FetchContent at configure time |
| **Minimum toolchain** | C++11, CMake 3.15; MSVC needs /arch:AVX2 on colortwist_avx.cpp (the file #errors without it); GCC/Clang get -mfma -mavx2 / -msse4.1 per file; RISC-V needs a GCC with riscv_vector.h (13.3 and 14.2 shown) |
| **Platforms** | x86 and x86-64 (fast path needs AVX2+FMA, runtime-checked via CPUID; SSE4.1 fallback), ARM32/ARM64 NEON (no runtime detection), RISC-V 64 with V extension (detected via getauxval) |
| **Thread safety** | not documented; the functions keep no state apart from a lazily cached CPU-feature flag in plain static ints, so concurrent calls on separate buffers look safe |
| **Drop-in for the baseline** | partial: same matrix layout, stride semantics and saturation as ippiColorTwist32f_8u_C3R/_16u_C3R, but a different signature, only C3 8u/16u, and the caller must pick the implementation enum (there is no automatic best-ISA dispatch) |

## Gotchas

- 'AVX3' in the README is the author's third AVX2+FMA variant, not AVX-512. HEAD keeps only one x86 path (X64_AVX, implemented by colorTwistRGB48_AVX3_Generic), so the README's AVX and AVX2 rows cannot be rebuilt.
- No automatic dispatch: you must call isOperationalRgb48/24 and pass the right ImplementationType yourself. CanNeon() always returns true, so an ARM32 build on a core without NEON will fault.
- The SIMD paths convert with cvtps_epi32, which honours the current MXCSR rounding mode, and any result at or above 2^31 (only with absurd coefficients, e.g. above about 10,900 on 16-bit input) becomes the integer-indefinite value and packs to 0 instead of saturating to the maximum the way the C path does.
- The RGB24 remainder handler (widths not divisible by 8) writes each tail pixel with _mm_maskmoveu_si128, a non-temporal masked store that is slow; the benchmark's 2048-wide RGB24 image never exercises it.

## Known shortcomings

- Tier A on test/testcolortwist.cpp (MSVC 19.27 Release with /arch:AVX2, i7-8700K; i9-12900K rows 4.1-4.9x added later) against IPP ippiColorTwist32f with a float matrix, static ippccmt, single-threaded on both sides, outputs within 1 LSB of the C reference; IPP version unstated. Baseline Intel IPP is not on the category list. AVX/AVX2 README rows were removed 2023-09.
- The RGB48 test matrix saturates about 96% of outputs (derived), so the 1-LSB check mostly compares clamped values (throughput unaffected); the README's 'AVX3' is a third AVX2+FMA variant, not AVX-512; the missing ippInit() is harmless on IPP 9.0+ (self-initialising, per an Intel doc snippet). No automatic dispatch; CanNeon() always returns true; results at or above 2^31 pack to 0 rather than the maximum; the RGB24 tail uses the slow _mm_maskmoveu_si128 (never hit by the benchmark); single author, no CI. Ryzen RGB24 gains are 2.63-2.77x against the 2.6-4.9x IPP range.

## Caveats and trade-offs

1. IPP rows appear only in the Windows MSVC/icl tables. The IPP version is not stated: FindIPP.cmake searches the Parallel Studio and oneAPI install paths. 2. The harness never calls ippInit(). 3. IPP is linked from the default static libraries (ippccmt.lib, ippcoremt.lib); colortwist is also single-threaded, so the threading modes match. 4. Precision matches: the baseline is ippiColorTwist32f_16u_C3R / 32f_8u_C3R, IPP's float-matrix variant rather than a fixed-point path. colortwist computes in float with FMA, and the harness checks both outputs against the float C loop within 1 LSB. 5. The README's AVX, AVX2 and AVX3 rows predate the 2023-09-21 commit '(start to) remove older and slower implementations'. HEAD keeps one X64_AVX path, implemented by colorTwistRGB48_AVX3_Generic, so the AVX and AVX2 rows cannot be reproduced at HEAD. HEAD's RGB48 harness uses width 2049, not the README's 2048. 6. The README calls the project a finger exercise in SIMD optimization; 2 stars.

Does one operation (colour matrix transform on RGB24/RGB48, plus RISC-V and NEON versions); not a general colour management engine; the IPP comparison is Windows-oriented and needs IPP to reproduce.

## Maintenance

One-author hobby project (195 commits, last commit 2025-12-28 adding RISC-V RVV) under BSD-2-Clause; small enough to vendor the two or three source files you need, but there are no releases, no CI, and only Visual Studio build steps in the README.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The README tables put colortwist next to IPP's ippiColorTwist32f in the same run. The harness is public (test/testcolortwist.cpp: 100 repeats, MB/s, every output checked against the C reference within 1 LSB), and the README names the compiler (MSVC 19.27.29112, icl 19.1.3.311) and CPU (i7-8700K, Ryzen 7 4700U, m3-6Y30, i9-12900K). Flags are public: Release config in the README build steps, /arch:AVX2 on colortwist_avx.cpp in lib/CMakeLists.txt, static CRT in the top-level CMakeLists.txt.
- **Verifier notes:** Harness, flags, compiler and CPU are all public, so A holds. The comparison is like for like: float matrix on both sides, single-threaded on both sides, outputs checked within 1 LSB. Only the IPP version is missing. Removed the record's 'build type not stated' (the README build steps say Release) and added the i9-12900K IPP table (4.1-4.9x).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ptahmose/colortwist>
  - <https://github.com/ptahmose/colortwist/commits>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/README.md>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/test/testcolortwist.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_ipp.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist.h>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_avx.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_c.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_config.h.in>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/cmakemodules/FindIPP.cmake>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/ptahmose/colortwist>
  - <https://github.com/ptahmose/colortwist/commits>
  - <https://github.com/ptahmose/colortwist/issues?q=is%3Aissue>
  - <https://github.com/ptahmose/colortwist/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/README.md>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/test/testcolortwist.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/unittests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/unittests/colortwist_tests.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist.h>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_c.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_c.h>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_ipp.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_avx.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_sse.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_neon.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_riscv.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/colortwist_config.h.in>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/utils.h>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/lib/utils.cpp>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/cmakemodules/FindIPP.cmake>
  - <https://raw.githubusercontent.com/ptahmose/colortwist/HEAD/LICENSE>
  - https://www.intel.com/content/www/us/en/developer/articles/guide/intel-integrated-performance-primitives-intel-ipp-intel-ipp-linkage-models-quick-reference-guide.html (search snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ptahmose/colortwist`) · [data/wave10/enrich/raw/github_com_ptahmose_colortwist.json](../../../data/wave10/enrich/raw/github_com_ptahmose_colortwist.json) (enrichment confidence 0.8)

</details>
