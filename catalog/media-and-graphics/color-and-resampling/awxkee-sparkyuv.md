# sparkyuv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Archived C++20 Highway-SIMD YUV/RGB converter; ties or beats libyuv on 8-bit decode on Apple M3, loses on encode.

| | |
|---|---|
| **Beats** | libyuv |
| **Claimed result** | Valid like-for-like rows (README, Apple M3 Pro, ns per call, derived from page data): 8-bit decode 4:2:2 346,422 vs libyuv 458,754 (1.32x); 4:2:0 347,903 vs 458,823 (1.32x); 4:4:4 332,122 vs 365,939 (1.10x); NV21 and NV12 tie. Invalid rows: the 10-bit decodes (1.92-2.12x) pass element counts as byte strides so sparkyuv reads half-size planes and writes a different output depth; unpremultiply 1.54x is NEON vs libyuv's C fallback. Slower than libyuv: RGBA8 to YCbCr420 (libyuv 2.0x faster), RGBA8 to YCbCr422 (1.37x), premultiply (1.21x). |
| **Workload** | Google Benchmark timings (one conversion per iteration; the YCbCr paths are single-threaded, threading is only used by FastGaussian) of 8-bit and 10-bit YCbCr 4:4:4/4:2:2/4:2:0 to RGBA decode, RGBA8 to YCbCr 4:2:0/4:2:2 encode, NV12/NV21 to RGBA decode, and RGBA premultiply/unpremultiply, sparkyuv vs libyuv (I444/I422/I420ToABGR, I410/I210/I010ToARGBMatrix, NV12/NV21 conversions, ARGBAttenuate/ARGBUnattenuate) on one JPEG test image (filirovska.jpeg, not in the repo, dimensions not stated) expanded to opaque RGBA; libyuv is linked from a prebuilt libyuv.a of unstated version and build flags. |
| **Metric** | throughput |
| **Hardware** | Apple M3 Pro (12 cores; Google Benchmark header shows 24 MHz nominal clock) |
| **Compiler and flags** | Not stated for the published run; the repository CMakeLists.txt builds C++20, adds -O3 to Release builds on non-MSVC compilers and uses Highway static dispatch on Apple (HWY_COMPILE_ONLY_STATIC). Compiler and libyuv build flags unknown. |
| **Adoption** | 9 stars |
| **Last commit** | 2024-07-14 |
| **Links** | [repository](https://github.com/awxkee/sparkyuv) · [benchmark](https://github.com/awxkee/sparkyuv) |

## Verdict

Only valid on Apple M3 Pro, as Google Benchmark output from the author against a prebuilt libyuv.a of unknown version and flags, on one JPEG (filirovska.jpeg, not in the repo, size unstated) with no compiler named. 8-bit 4:2:0/4:2:2 decode to RGBA is about 1.32x libyuv (347.9 vs 458.8 us), 4:4:4 is 1.10x, NV12/NV21 tie, and libyuv is 1.37-2.0x faster at encode and 1.21x faster at premultiply. Three claims are not like-for-like: the 1.92-2.12x 10-bit decode lead (different output depth, and byte strides passed as element counts so sparkyuv reads overlapping half-size planes while libyuv reads full ones), and the 1.54x unpremultiply lead, where libyuv has no NEON ARGBUnattenuate row ('TODO(fbarchard): Neon version' in libyuv 1974 planar_functions.cc), so it races libyuv's C fallback.

## Use it when

- C++ code that needs YUV matrices libyuv lacks (YCgCo-Re/Ro, YIQ, YDbDr, YDzDx, BT.2020 CL) or 10/12-bit YUV to 16-bit-per-channel RGBA.
- 8-bit YCbCr 4:2:0/4:2:2 to RGBA decode on arm64 (NEON), where the README shows about 1.3x over libyuv I420/I422ToABGR on an M3 Pro.
- Targets Highway covers (SVE/SVE2, RVV, POWER, Z, WASM) where you want one portable SIMD codebase rather than per-ISA assembly.
- Projects that will vendor and freeze the code, since upstream is archived.

## Skip it when

- 8-bit RGBA to YUV encode: libyuv is 2.0x faster to 4:2:0 and 1.37x faster to 4:2:2 in the project's own table, and libyuv also wins premultiply (1.21x).
- x86: there are no x86 numbers, and the README says 8-bit decode 'should be considered same' as libyuv off arm64.
- When you need output that matches libyuv bit for bit or a tested library: the repo has no tests (CI runs ctest, but CMakeLists.txt defines none), and nothing compares output with libyuv.
- When chroma downsampling quality or siting matters: the subsampling filter is fixed and cannot be turned off, and the 8-bit 4:2:0 SIMD encoder skips vertical averaging (see gotchas).
- When you need maintenance or bug fixes: archived 10 Feb 2025, last commit 14 Jul 2024, 0 issues ever filed.

## How it is fast

The kernels are written once against Google Highway (pinned to the author's fork, branch widen_mul) and compiled per SIMD target. 8-bit decode follows libyuv's approach: 6-bit fixed-point coefficients, 16-bit saturating multiply-add, interleaved RGBA stores. 8-bit encode uses 8-bit fixed point with 32-bit WidenMulAccumulate and averages chroma pairs in registers (SumsOf2). The 10/12-bit paths widen to 32-bit lanes and narrow back to 16-bit RGBA, so they skip libyuv's reduction to 8-bit ARGB.

## Compared with alternatives

Pick it over yuvutils-rs (same author, Rust, active, with Fast/Balanced/Professional precision modes) only if you must stay in C++ and want its unusual matrices or 16-bit RGBA output. For plain 8-bit BT.601/709 conversion, libyuv (faster encode, maintained) or the tiny xxYUV are safer choices.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Google Highway, cloned by deps.sh from the author's fork (github.com/awxkee/highway, branch widen_mul) into ./highway; the benchmark/tools targets also need libjpeg, Google Benchmark and a prebuilt libyuv.a placed in the repo root (not shipped) |
| **Minimum toolchain** | C++20, CMake 3.22 |
| **Platforms** | Highway targets: x86 SSE2 to AVX-512 (AVX3/AVX3_DL/ZEN4/SPR), Arm NEON/SVE/SVE2, POWER8-10, IBM Z14/Z15, RISC-V RVV, WASM. HWY_SCALAR is disabled. Apple builds use static dispatch only (HWY_COMPILE_ONLY_STATIC); other platforms use runtime dispatch. |
| **Thread safety** | Not documented. The conversion functions are stateless and work only on caller buffers (from reading the source); FastGaussian spawns threads when THREADS_SUPPORTED is set. |
| **Drop-in for the baseline** | no |

## Gotchas

- Strides are in bytes even for uint16_t planes: the YCbCrP16 kernels advance a uint8_t pointer by yStride/uStride/vStride. The project's own 10-bit benchmark passes element counts (yPlaneStride = inWidth), so it runs on overlapping rows.
- Correctness bug in the 8-bit 4:2:0 SIMD encoder (src/YCbCr420-inl.h): its 'next row' load calls LoadRGBA(du8, mSrc, ...) on the same row, so vertical chroma averaging does nothing and chroma comes from even rows only. The scalar tail does average 2x2, so the two paths disagree. This contradicts the README's 'bi-linear scaling is automatically applied'.
- The Release-only -O3 is the sole optimisation flag. The Dockerfile runs plain 'cmake -G Ninja .' with no build type, which gives an unoptimised build, and it does not run deps.sh.
- YCgCo-Re/Ro 8-bit needs 16-bit storage and is always full range. 4:2:0/4:2:2/NV inputs reject null U/V planes.

## Known shortcomings

- README numbers (Apple M3 Pro) match, but the 1.9-2.1x 10-bit wins compare sparkyuv's 10-bit RGBA output against libyuv's 8-bit ARGB path; libyuv is faster on 8-bit encode (2.0x at 4:2:0) and premultiply. The prebuilt libyuv.a version and the test image size are unknown.
- Headline 10-bit decode wins (1.92-2.12x) are a harness bug: the benchmark passes element counts as byte strides on uint16 planes, so sparkyuv reads overlapping half-size planes while libyuv reads full planes, and the output depth differs; unpremultiply 1.54x is NEON against libyuv's C fallback. Valid wins are the 8-bit decodes only (4:2:0 and 4:2:2 1.32x, 4:4:4 1.10x, NV ties); libyuv wins the encodes. Correctness bug in src/YCbCr420-inl.h: the 8-bit 4:2:0 SIMD encoder reloads mSrc instead of the next row, so vertical chroma averaging is a no-op and disagrees with the scalar tail. No tests (CI runs ctest with none defined), no libyuv equality check, NV12/NV21 libyuv calls swapped, libyuv 4:2:2 decode fed 4:2:0 chroma, J422 full range against TV range; depends on the author's Highway fork (widen_mul). Retier-02 corrects the record.

## Caveats and trade-offs

Mixed result: the README says 8-bit decode is 'very close to libyuv', faster only on arm64 NEON and 'should be considered same' elsewhere, and libyuv is faster at 8-bit YCbCr encode (2.0x at 4:2:0, 1.37x at 4:2:2) and premultiply. The 10-bit wins compare different outputs (sparkyuv 10-bit RGBA in 16-bit storage vs libyuv 8-bit ARGB). Only arm64 numbers; no x86 results. Test image is not in the repo and its size is not stated; premultiply/unpremultiply run on fully opaque pixels from an RGB JPEG. libyuv comes from a prebuilt libyuv.a of unknown version and flags. Repo archived by owner 10 Feb 2025; last commit 14 Jul 2024. Licence files: LICENSE.md (Apache-2.0) and LICENSE-BSD.md (BSD-3-Clause, same author); source headers cite Apache-2.0. [retier] Headline 10-bit wins are a harness bug (element counts passed as byte strides) and compare different output depths; the valid wins are 8-bit decodes at 1.10-1.32x on NEON only. No tests (CI runs ctest with none defined), no libyuv equality check; the NV12 and NV21 libyuv calls are swapped, the libyuv 4:2:2 decode is fed 4:2:0 chroma, and J422 full range is compared against TV range. The 8-bit 4:2:0 SIMD encoder has a vertical chroma averaging bug (src/YCbCr420-inl.h). Depends on the author's Highway fork (awxkee/highway, widen_mul). libyuv is a prebuilt libyuv.a of unknown version and flags; arm64 numbers only; repo archived by its owner.

Supports many YUV matrices (YCgCo, YIQ, YDbDr, constant-luminance), 8/10/12-bit, 22 SIMD targets. Chroma-subsampled encode uses a fixed bilinear downscale that cannot be turned off.

## Maintenance

Abandoned: archived 10 Feb 2025, last commit 14 Jul 2024, 9 stars. Apache-2.0 (BSD-3-Clause file from the same author also present), so it is copyable, but vendoring also means carrying the author's Highway fork and fixing the 4:2:0 encoder bug yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark output in the README (Apple M3 Pro) with public harness code (tools/YuvBenchmarkMain.cpp, tools/bench/YuvBenchmark10.cpp, tools/bench/YuvSupport.cpp, tools/bench/YuvBenchmarkNV.cpp), but no compiler, no flags for the published run, no test-image size and an unversioned prebuilt libyuv.a, so not A; no independent measurement, so not B.
- **Verifier notes:** Every number in the record matches the README benchmark block; I added the 10-bit 4:4:4/4:2:2, 8-bit 4:2:0, NV21 and RGBA8-to-YCbCr422 rows and labelled ratios as derived. The headline 10-bit 1.9-2.1x gains are not like-for-like (10-bit RGBA output vs libyuv's 8-bit ARGB output), which the enricher should keep visible. Metadata (9 stars, archived 2025-02-10, last commit 2024-07-14) checked on github.com.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/awxkee/sparkyuv>
  - <https://github.com/awxkee/sparkyuv/commits>
  - <https://github.com/awxkee/sparkyuv/tree/main>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/YuvBenchmarkMain.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmark10.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmarkBase.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmarkNV.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvSupport.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/YCbCrP16.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/YCbCrP16-inl.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/yuv-inl.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/sparkyuv.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/NV12Flyer.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/FastGaussian.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/LICENSE-BSD.md>
- **Sources the enricher read:**
  - <https://github.com/awxkee/sparkyuv>
  - <https://github.com/awxkee/sparkyuv/issues?q=is%3Aissue>
  - <https://github.com/awxkee/sparkyuv/tree/main/.github/workflows>
  - <https://github.com/awxkee/highway/tree/widen_mul>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/DOC.md>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/deps.sh>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/Dockerfile.msvc>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/.github/workflows/multiarch.yml>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/.github/workflows/graviton.yml>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/YuvBenchmarkMain.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmark10.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmarkBase.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvBenchmarkNV.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/tools/bench/YuvSupport.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/include/sparkyuv.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/include/sparkyuv-def.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/sparkyuv.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/yuv-inl.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/YCbCr420-inl.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/YCbCrP16-inl.h>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/YCbCrP16.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/NV12Flyer.cpp>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/src/ChannelsReformat.cpp>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/planar_functions.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/convert_argb.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/convert_argb.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/row.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/version.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/awxkee/sparkyuv`) · [data/wave10/enrich/raw/github_com_awxkee_sparkyuv.json](../../../data/wave10/enrich/raw/github_com_awxkee_sparkyuv.json) (enrichment confidence 0.8)

</details>
