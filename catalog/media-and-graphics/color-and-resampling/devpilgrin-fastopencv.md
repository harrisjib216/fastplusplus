# FastOpenCV (fastcv kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Threaded cv::Mat kernels that replace OpenCV 4.14 resize (cubic downscale, integer INTER_AREA), transform and general-exponent pow.

| | |
|---|---|
| **Beats** | OpenCV 4.14.0 cv::resize (INTER_CUBIC, INTER_AREA), cv::transform and cv::pow, built from source by the repo's scripts with IPP disabled (WITH_IPP=OFF in every variant) and TBB threading at the default thread count; libfastcv is compiled against the linux-dispatch install, so the cv:: column is most likely that build, not a distribution build. |
| **Claimed result** | README table: resize INTER_CUBIC 3.4 -&gt; 0.8 ms (4.1x, bit-exact), but the 3.4 ms OpenCV time is the first kernel-audit figure, which PLAN.md stage 5e says was taken with setNumThreads(0), a mode that slowed OpenCV+TBB about 4x; re-measured in default threading OpenCV takes 0.88 ms, and the author's own header (fastcv/include/fastcv/fastcv.hpp) and PLAN.md give fastcv::resizeCubic8u as 1.5-1.9x for downscaling (bit-exact) and 0.7-0.9x, i.e. slower than OpenCV, for upscaling. resize INTER_AREA integer factor x4: 18.7x (8UC1) and 3.5x (8UC3), maxDiff 1 on 0.2% of pixels; for x2 cv::resize is faster (README row: 0.92 -&gt; 0.02-0.25 ms). transform 32FC3 with a 4x4 matrix: 7.9 ms (PLAN.md says 8.8 ms) -&gt; 0.74 ms (10.7x, bit-exact). pow 32F with a general exponent (gamma): 19-22x, relative error about 1e-5, positive inputs only. |
| **Workload** | bench/resize_cubic_bench.cpp: random 8UC1 and 8UC3 images, 1920x1080 down to 960x540 and 1280x720, 960x540 up to 1920x1080, and 1920x1080 to 640x480 (C3), cv::resize INTER_CUBIC versus fastcv::resizeCubic8u, 20 timed runs after 2 warm-ups, with maxDiff and non-zero-difference counts. bench/area_hist_bench.cpp: 1080p 8UC1 and 8UC3, INTER_AREA integer factors 2 and 4 versus fastcv::resizeAreaInt8u. bench/transform_bench.cpp: 1080p 32FC3 with a 4x4 affine matrix (so the output is 32FC4) versus fastcv::transform32f. bench/pow_bench.cpp: 1080p 32FC1 with values in [0.01, 10], exponents 1.7 and -0.3, versus fastcv::pow32f. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 9950X3D (Zen 5, AVX-512 + VBMI, 32 threads), 128 GB RAM, NVIDIA RTX 4090; Arch Linux (CPU model named in PLAN.md stage 0) |
| **Compiler and flags** | g++ (version not stated); fastcv built with -O3 -march=native -fPIC against the repo's linux-dispatch OpenCV install (scripts/build-fastcv.sh). OpenCV 4.14.0 built by scripts/build-linux-opt.sh: Release, gcc/g++, LTO, TBB on, OpenMP off, WITH_IPP=OFF, LAPACK via OpenBLAS, CUDA 13.3; the dispatch variant uses an AVX2 baseline with AVX512_SKX dispatch and ENABLE_FASTMATH, while the stock variant keeps OpenCV's default CPU baseline and dispatch. Compile flags for the bench/\*.cpp drivers are not given. |
| **Adoption** | 0 stars, 0 forks (repo created September 2026, 6 commits) |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/devpilgrin/FastOpenCV) · [benchmark](https://github.com/devpilgrin/FastOpenCV) |

## Verdict

The author measured on a Ryzen 9 9950X3D (32 threads, Arch Linux) against OpenCV 4.14.0 built from source with IPP off and TBB at default threads, using 1080p random images and 20-50 timed runs: cubic downscale 1.5-1.9x bit-exact (upscale 0.7-0.9x, slower), INTER_AREA x4 18.7x C1 and 3.5x C3, transform 32FC3 with a 4x4 matrix 10.7x, pow 19-22x on inputs in [0.01, 10]. No result files back these numbers, and every baseline except upscale cubic runs on far fewer threads than fastcv.

## Use it when

- You already link OpenCV and do 8UC1/8UC3 INTER_CUBIC downscaling of 1080p-class frames on a many-core x86 box: the author's corrected figure is 1.5-1.9x with bit-exact output.
- Integer-factor INTER_AREA decimation by 4 (or 3, 5, ...) on 8UC1/8UC3 where OpenCV's area-fast path only gets a couple of threads; x4 measured 18.7x (C1) and 3.5x (C3) with +/-1 differences.
- Per-pixel 3-in/4-out float colour transforms (cv::transform with a 4x4 matrix on 32FC3), where OpenCV falls back to a single-threaded scalar loop.
- Gamma curves on strictly positive CV_32FC1 data (for example after adding an epsilon), when about 1e-5 relative error is acceptable.
- As a reference for how much of OpenCV's latency on a 32-thread CPU is threading policy rather than arithmetic.

## Skip it when

- Upscaling with INTER_CUBIC: the author's own log measures fastcv at 0.7-0.9x of OpenCV (slower) and says to keep cv::resize there.
- INTER_AREA by 2: OpenCV's SIMD 2x2 path is faster (README and header both say use cv::resize for x2).
- pow on data that can contain 0, negative values, NaN/Inf or results outside the float exponent range: pow32f returns garbage there, while cv::pow returns 0/inf/NaN.
- Single-core, latency-bound or already-parallel pipelines (or calls from inside another cv::parallel_for_, where the nested loop runs serially): the speedups come largely from using all 32 threads of a Ryzen 9 9950X3D.
- Production use that needs maintenance or review: 0 stars, no issues or third-party reports, one v1.0.0 release, comments and logs in Russian, and the README's headline cubic 4.1x is stale.

## How it is fast

Mostly parallelism: every kernel runs a plain cv::parallel_for_ over rows with no stripe hint, while OpenCV 4.14.0 runs cv::transform and the general cv::pow single-threaded (NAryMatIterator) and runs resize with nstripes = dst.total()/65536. That OpenCV heuristic gives about 2 stripes for a 480x270 INTER_AREA x4 output, about 8 for a 960x540 cubic downscale and about 32 for a 1920x1080 upscale (derived from OpenCV's resize.cpp), which fits fastcv winning on downscale and losing on upscale. resizeCubic8u also does a two-phase separable pass (horizontal 11-bit fixed-point into an int buffer, with an AVX-512 32-bit gather of 4 taps for C1 interior pixels, then a float SIMD vertical pass), so each source row is filtered once. pow32f replaces OpenCV's SIMD log32f/exp32f plus its zero/negative fix-up loop with fused exp2(p\*log2(x)) polynomials (atanh series for log2, degree-6 Taylor for exp2).

## Compared with alternatives

Pick it over KLERP, CompV or FlyCV when you want to keep cv::Mat and OpenCV's exact cubic coefficients and only fix the specific OpenCV calls that leave cores idle (cubic downscale, area x4, 3-to-4-channel transform); pick fast_image_resize or stb-image-resize-opt for a standalone, maintained resizer with many filters and published per-case results.

## Integration

| | |
|---|---|
| **Form** | static lib (libfastcv.a via scripts/build-fastcv.sh); single kernels can also be copied as one .cpp each |
| **Dependencies** | OpenCV core headers and library (built and tested against the repo's OpenCV 4.14.0 linux-dispatch install); the library build also passes -I/usr/include/openblas, and other kernels need OpenBLAS and FFTW (-lopenblas -lfftw3f -lfftw3f_threads); the four resampling/colour kernels need only opencv_core |
| **Minimum toolchain** | C++17 (README badge); g++ with -O3 -march=native (version not documented); OpenCV 4.x function-style universal intrinsics (v_add/v_mul/v_muladd) |
| **Platforms** | Linux x86-64 tested (Zen 5, AVX-512 + VBMI); resizeCubic8u's gather path needs AVX-512F at compile time and otherwise falls back to scalar; Windows MinGW and aarch64 builds are documented but not verified |
| **Thread safety** | not documented; by code reading resizeCubic8u, resizeAreaInt8u, transform32f and pow32f keep no shared state and are reentrant, and they use OpenCV's thread pool (cv::setNumThreads applies) |
| **Drop-in for the baseline** | partial — same cv::Mat arguments, but you call fastcv:: per site and each kernel covers a subset of cv:: cases (no interpolation flag, no x2 area win, positive-only pow, no in-place resize) |

## Gotchas

- pow32f's x &lt;= 0 mask is computed and discarded, and exp2 has no range clamp: zero inputs (black pixels in a gamma curve) give garbage instead of 0, and the repo's own test adds +0.001 to the image to avoid it.
- cv::pow's general-exponent baseline in OpenCV 4.14.0 is vectorized (hal::log32f/exp32f in blocks, single-threaded), not scalar powf as the fastcv source comment says; the 19-22x is 32 threads plus cheaper polynomials, against a baseline that also does the zero/negative handling fastcv skips.
- resizeAreaInt8u rounds ties up with (sum+8)&gt;&gt;4, while OpenCV's area-fast loop for x4 does saturate_cast(sum\*(1/16.f)), which rounds half to even; by code reading about 1 in 32 output values should differ by 1 on uniform random input, more than the README's 0.2%, and the regression test's bound (img3.total()\*3/100 = 62,208 of 388,800 output values) is far looser than its '&lt;1% px' label. Its header comment promises SIMD, but the code is plain scalar loops left to the compiler.
- The resize kernels call dst.create() before reading src and keep no copy of the src header, so passing the same Mat as src and dst breaks; resizeCubic8u also allocates a fresh sh x dw\*cn int32 buffer every call (about 12 MB for 1080p C3 to 960x540). resizeCubic8u and transform32f have no regression tests, and transform32f's SIMD 3x3 path (FMA chain in a different order from OpenCV's v_matmuladd) was never benchmarked or checked for bit-exactness.

## Known shortcomings

- Headline 4.1x INTER_CUBIC resize is overstated: the 3.4 ms OpenCV time was taken under setNumThreads(0), the trap the repo's own PLAN.md 5e calls a 4x artefact; re-measured OpenCV takes 0.88 ms, and the author's fastcv.hpp states downscale 1.5-1.9x and upscale 0.7-0.9x (slower), which the README never reflects. Own universal-intrinsics plus AVX-512 code (no Qualcomm FastCV), same resize algorithm (A=-0.75, 11-bit fixed point, clamped borders); area x4 18.7x on C1 and 3.5x on C3, integer factors only. Every build has WITH_IPP=OFF, TBB with 32 threads; the transform bench's 10.7x is threading only (OpenCV's generic single-thread scalar loop), pow32f's x&lt;=0 mask is dead code so zero or negative inputs give garbage. Ryzen 9 9950X3D per PLAN.md, g++ version unstated; no result files for the 1080p numbers; 6 commits, 0 stars.
- Verifier caveat corrected by the enricher: OpenCV 4.14.0 cv::pow with a general exponent runs SIMD hal::log32f/exp32f single-threaded, not scalar powf, so the 19-22x is 32 threads plus cheaper polynomials, and pow32f skips cv::pow's zero and negative fix-up (zero input gives garbage). OpenCV resize uses parallel_for_ with nstripes = dst.total()/65536 (about 2 stripes for area x4 at 480x270, 8 for cubic to 960x540, 32 for the 1080p upscale) while fastcv uses all threads, so the wins are mostly threading policy, matching the upscale loss; transform 10.7x is the 3-to-4-channel scalar path only (OpenCV has its own SIMD 3x3 path). Accuracy: area x4 rounds ties up where OpenCV rounds half-even, predicting about 3% of values off by one, not the README's 0.2%; the test bound is 62,208 of 388,800 values despite the '&lt;1% px' label; no tests for resizeCubic8u or transform32f; the area kernel's header comment promises SIMD but the code is scalar.

## Caveats and trade-offs

This is the author's own kernel library: the code in fastcv/src uses OpenCV universal intrinsics and AVX-512 intrinsics. It is not a wrapper over Qualcomm's proprietary FastCV SDK, nor OpenCV's Qualcomm FastCV HAL; only the name is shared. The headline resize INTER_CUBIC 4.1x compares a fastcv time against an OpenCV time taken with setNumThreads(0), a mode that PLAN.md stage 5e calls a trap that slowed OpenCV+TBB about 4x and then re-measured at 0.88 ms. The author's corrected figures are 1.5-1.9x for downscaling and 0.7-0.9x (slower) for upscaling, and the README was never updated. The resize kernel follows OpenCV's algorithm (bicubic A=-0.75, 11-bit fixed-point horizontal pass, float vertical pass, clamp-to-edge borders), so the bit-exact claim is plausible. resizeAreaInt8u handles only integer factors that divide the image size, on C1 and C3. It rounds ties up with a shift, while OpenCV's area-fast path rounds sum\*(1/area) with cvRound, which explains the +/-1 differences. The README's 0.02-0.25 ms range does not match 0.92/18.7 = 0.05 ms (derived from page data). The transform benchmark uses a 4x4 matrix on 3 channels, so it produces a 4-channel output, which takes OpenCV's generic single-threaded scalar loop. fastcv's dcn=4 path is also scalar, so the 10.7x comes from running that loop on 32 threads; the SIMD 3x3 path is not what was benchmarked. pow32f uses exp2(p\*log2(x)) polynomials with a mask for x &lt;= 0 that is computed but never applied. Zero or negative inputs (black pixels in gamma) therefore produce garbage values instead of 0 or NaN, and there is no overflow or underflow clamping. The benchmark avoids this by using inputs in [0.01, 10]; it is also multi-threaded against cv::pow's scalar powf. Every OpenCV build in the repo disables IPP, so the results do not speak for IPPICV-enabled distribution builds. No result files for the 1080p numbers are checked in: bench/lena_fastcv.txt holds only an assertion crash in sortIdxRows32f, and only bench/lena_stock.txt has timings. The repo has 0 stars and no third-party reproduction, and resize is only a small part of a roughly 30-kernel library.

Drop-in kernels that need OpenCV headers plus an OpenCV build with the repo's patches for best results; -march=native build so the library is machine specific; requires AVX-512 VBMI for some kernels; Rust FFI crate included.

## Maintenance

Created September 2026 (6 commits, v1.0.0 on 2026-09-08, last commit 2026-09-10, 0 stars, no issues); Apache-2.0 and the resampling kernels are single files depending only on opencv_core, so they are easy to vendor, but treat them as unreviewed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party only: the README table and the author's PLAN.md/QUEUE.md give before/after times, and the benchmark drivers are public (bench/resize_cubic_bench.cpp, bench/area_hist_bench.cpp, bench/transform_bench.cpp, bench/pow_bench.cpp), the CPU is named (Ryzen 9 9950X3D in PLAN.md) and the fastcv flags are in scripts/build-fastcv.sh, but no result file backs the 1080p numbers, the g++ version and bench-driver flags are not given, and the headline resize INTER_CUBIC 4.1x is contradicted by the repo's own corrected measurements, so it cannot be A.
- **Verifier notes:** The repo is real and public (Apache-2.0, last commit 2026-09-10), with its own SIMD/threaded kernels that do the same work as OpenCV's for resize, area x4 and transform. I kept tier C but marked the claim as overstated: the 4.1x INTER_CUBIC row uses a baseline the author's own log says ran about 4x slow; the corrected figure is 1.5-1.9x for downscaling and slower than OpenCV for upscaling. Enrichers should treat pow32f as unsafe for zero or negative inputs: its x &lt;= 0 fallback is dead code.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/devpilgrin/FastOpenCV>
  - <https://github.com/devpilgrin/FastOpenCV/tree/main/bench>
  - <https://github.com/devpilgrin/FastOpenCV/tree/main/fastcv>
  - <https://github.com/devpilgrin/FastOpenCV/tree/main/fastcv/src>
  - <https://github.com/devpilgrin/FastOpenCV/commits/main>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/README.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/QUEUE.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/resize_cubic_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/area_hist_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/transform_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/pow_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/kernel_audit.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/lena_all.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/lena_fastcv.txt>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/lena_stock.txt>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/test_imgproc_stock.txt>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/build-fastcv.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/build-linux-opt.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/run-bench.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/include/fastcv/fastcv.hpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/resize_cubic_8u.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/resize_area_int_8u.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/transform_32f.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/pow_32f.cpp>
- **Sources the enricher read:**
  - <https://github.com/devpilgrin/FastOpenCV>
  - <https://github.com/devpilgrin/FastOpenCV/commits/main>
  - <https://github.com/devpilgrin/FastOpenCV/issues>
  - <https://github.com/devpilgrin/FastOpenCV/releases>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/README.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/QUEUE.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/CROSSBUILD.md>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/resize_cubic_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/area_hist_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/transform_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/pow_bench.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/kernel_audit.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/lena_fastcv.txt>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/bench/lena_stock.txt>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/build-fastcv.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/build-linux-opt.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/run-bench.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/scripts/run-fastcv-tests.sh>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/include/fastcv/fastcv.hpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/include/fastcv/fastcv_c.h>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/resize_cubic_8u.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/resize_area_int_8u.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/transform_32f.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/src/pow_32f.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/fastcv/tests/fastcv_test.cpp>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/rust/fastcv-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/devpilgrin/FastOpenCV/HEAD/rust/fastcv-sys/build.rs>
  - <https://raw.githubusercontent.com/opencv/opencv/4.14.0/modules/core/src/mathfuncs.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/src/mathfuncs.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.14.0/modules/core/src/mathfuncs_core.simd.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.14.0/modules/imgproc/src/resize.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.14.0/modules/core/src/matmul.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.14.0/modules/core/src/matmul.simd.hpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/devpilgrin/fastopencv`) · [data/wave10/enrich/raw/github_com_devpilgrin_fastopencv.json](../../../data/wave10/enrich/raw/github_com_devpilgrin_fastopencv.json) (enrichment confidence 0.75)

</details>
