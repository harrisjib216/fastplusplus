# zanazakaryaie/fastGaussianBlur (step-by-step optimised Gaussian blur)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Unlicensed three-step tutorial for a fixed 5x5 float Gaussian blur; it beats OpenCV only on a Raspberry Pi 3B+, and only when using 4 threads.

| | |
|---|---|
| **Beats** | OpenCV cv::GaussianBlur |
| **Claimed result** | Not faster on a desktop CPU. First-party chart (Comparison.jpg, values read off bars): final stage (memory management + SIMD + OpenMP, 4 threads) about 3.4 ms vs OpenCV about 8.9 ms at 720x720, 7.9 vs 19.8 ms at 1080x1080, 13.7 vs 35 ms at 1440x1440, roughly 2.5x (derived from page data) on a Raspberry Pi 3B+; the project's own single-thread stages are slower than OpenCV at every size (about 10.0-11.6 vs 8.9 ms at 720x720). Independent (issue #3, Ryzen 7 5800H, OpenCV 4.8, 720x720): OpenCV 0.23 ms vs the project's best stage 0.63 ms, OpenCV about 2.7x faster (derived from page data). |
| **Workload** | 5x5 Gaussian blur (sigma 1.0, BORDER_REPLICATE) of a single-channel CV_32F image: the repo's 720x720 image.jpg, with 1080x1080 and 1440x1440 obtained by enabling the commented-out resize line in main.cpp; mean of 100 back-to-back iterations per variant timed with std::chrono, no warm-up, on a Raspberry Pi 3B+. |
| **Metric** | latency |
| **Hardware** | Raspberry Pi 3B+ (4 cores) |
| **Compiler and flags** | GCC 6.3 on 32-bit Raspbian; optimisation flags not stated |
| **Adoption** | 25 stars |
| **Last commit** | 2021-03-25 |
| **Links** | [repository](https://github.com/zanazakaryaie/fastGaussianBlur) · [benchmark](https://github.com/zanazakaryaie/fastGaussianBlur) |

## Verdict

Comparison.jpg (bar chart, values read by eye) times 100 back-to-back calls on a Raspberry Pi 3B+ (32-bit OS, GCC 6.3, OpenCV version unstated): cv::GaussianBlur about 8.9/19.8/35 ms against the 4-thread OpenMP stage at about 3.4/7.9/13.7 ms for 720/1080/1440-pixel squares, roughly 2.5x. The best single-thread stage (about 10.0/23.3/41.5 ms) is about 1.12-1.19x slower than OpenCV (derived from page data). A third-party x86 run (issue #3, Ryzen 7 5800H, OpenCV 4.8) reverses the result: OpenCV 0.23 ms against 0.63 ms for the best tutorial stage.

## Use it when

- As reading material on row-buffer separable convolution, symmetric-kernel folding, universal intrinsics and OpenMP row splitting, for a small ARM board.
- As a starting point for a hand-written fixed-kernel 5x5 float blur on a 4-core ARM board, where OpenCV's float Gaussian runs on one thread and you can spend all cores on this one filter.
- When you will rewrite the code anyway: there is no license, so it can only be studied, not copied.

## Skip it when

- On x86 desktops: a third-party report (issue #3, 2024-09-09, Ryzen 7 5800H, OpenCV 4.8, 720x720) measured OpenCV at 0.23 ms against 0.63 ms for the best tutorial stage (SIMD) and 0.74 ms for the OpenMP stage. That makes OpenCV about 2.7x faster than the tutorial's best stage (derived from page data), and the parallel stage was slower than the single-thread SIMD stage. The author has not replied.
- For any kernel other than 5x5 at sigma 1.0 with replicate borders, or any input other than one-channel 32-bit float: the weights are hard-coded constants.
- For image widths that are not a multiple of 4 in the SIMD and OpenMP stages: the vector loops run `for (; j<cols; j+=4)` with no tail guard, so they write up to 3 floats past the stack row buffer and read past the last image row. The scalar 'leftovers' loop then never runs. The benchmarked widths (720, 1080, 1440) are all multiples of 4.
- With current OpenCV: the SIMD and OpenMP stages use `+` and `*` on cv::v_float32x4, and OpenCV's own intrin_legacy_ops.h says these operators were removed in 4.11, so the code needs an older OpenCV or that header included by hand. Issue #2 (OpenCV 3.3.0) reports a CV_CPU_HAS_SUPPORT_SSE2 / CV_CPU_HAS_SUPPORT_NEON compile error at the other end of the version range.
- In shipping code: no license file, no tests, no output check against OpenCV, and no commits since 2021-03-25.

## How it is fast

Stage 1 runs the separable filter in a single pass per output row. A vertical 5-tap sum goes into a one-row stack buffer, then a horizontal 5-tap pass writes the output row. This avoids a full-size intermediate image, and the symmetric weights are folded as (a+e)\*w2 + (b+d)\*w1 + c\*w0. Stage 2 vectorises only the vertical pass, four floats at a time, with OpenCV universal intrinsics (cv::v_float32x4); the horizontal pass stays scalar. Stage 3 adds `#pragma omp parallel for` over the middle rows. Its win over OpenCV comes from spreading those rows across the Pi's four cores: in the author's chart both single-thread stages are slower than OpenCV at every size.

## Compared with alternatives

Pick it only to learn the three optimisation steps. For production Gaussian blur faster than OpenCV, the catalogued siblings are better choices: libblur (arbitrary kernels, multithreaded), bfraboni/FastGaussianBlur (box-blur approximation for large sigma) and LibGaussianBlur (FFT); for box filters there is FastBoxBlur. All of them carry licenses and take more than one fixed kernel.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenCV (core universal intrinsics; imgcodecs/highgui for the demo harness), OpenMP for the parallel stage |
| **Minimum toolchain** | GCC with C++11 plus GNU extensions (variable-length stack array `float buffer[cols]` with __attribute__((aligned(16))), privatised in an OpenMP clause); author used GCC 6.3 on 32-bit Raspbian; OpenCV newer than 3.3 (issue #2) and older than 4.11, or 4.11+ with intrin_legacy_ops.h included |
| **Platforms** | measured only on a Raspberry Pi 3B+ (32-bit OS); the intrinsics compile for x86 SSE2 and ARM NEON, and fall back to OpenCV's scalar C++ emulation when neither is enabled |
| **Thread safety** | not documented; the functions use no globals, and the stage-3 function starts its own OpenMP team |
| **Drop-in for the baseline** | no |

## Gotchas

- Unequal threading behind the headline: the final stage uses the OpenMP default thread count (all 4 cores on a Pi 3B+). In current OpenCV 4.x source, a 32F GaussianBlur without IPP goes through the HAL hook and then sepFilter2D, and filter.dispatch.cpp has no parallel_for_. So the roughly 2.5x chart win is most likely 4 threads against 1. The OpenCV version the author used is not stated.
- The CMakeLists add -O3 -Ofast -funroll-loops but no -mfpu=neon. OpenCV's cv_cpu_dispatch.h sets CV_NEON only when the compiler defines __ARM_NEON; otherwise the universal intrinsics compile to the scalar emulation in intrin_cpp.hpp, whose v_load_aligned asserts 16-byte alignment. The repo never says whether its 'SIMD' stage ran as NEON, and it was only about 14% faster than the scalar stage on the chart. Matrix.h allocates rows with plain malloc and requests no alignment, yet every vector load and store uses the aligned variants.
- The top-row vector loop computes row 1 with the wrong replicated neighbour (row 1 instead of row 0). A scalar loop that redeclares j and recomputes the whole row overwrites the result, so the output is right but the vector work is wasted.
- Every call does output.resize(), which frees and mallocs the output matrix, and cv::Mat input is first copied element by element into Matrixf. Images with fewer than 4 rows or columns underflow the unsigned `rows-2`/`cols-2` bounds.

## Known shortcomings

- Chart-only numbers from a Raspberry Pi 3B+: the final OpenMP stage is about 2.5x OpenCV while the single-thread SIMD stage is slower than OpenCV at every size; OpenCV version, build and thread count unstated, no output check, no -mfpu=neon. No licence file (reference). Weak category fit (a filter tutorial, not resampling).
- Enricher (e126, 2026-10-05): the win is 4 OpenMP threads against OpenCV's 32F GaussianBlur (current 4.x non-IPP path is sepFilter2D without parallel_for_; author's OpenCV version unstated), so threads are unequal; the independent issue #3 (Ryzen 7 5800H, OpenCV 4.8, 720x720) has OpenCV 0.23 ms vs the project's best stage 0.63 ms, about 2.7x in OpenCV's favour. Flagged not faster (retier-38, C). Bugs: SIMD and OpenMP loops lack a tail guard and overrun a stack buffer when width % 4 != 0 (benchmarked widths fine); no -mfpu=neon, so NEON use unproven; uses operators removed in OpenCV 4.11, so it will not compile against current OpenCV; issue #2 compile error on OpenCV 3.3.

## Caveats and trade-offs

Tutorial rather than a library (About: 'Step-by-step tutorial for optimizing a Gaussian image smoothing function'). The win comes only from the OpenMP stage spreading middle rows across the Pi's cores; the project's own single-thread SIMD stage is slower than OpenCV at all three sizes, and the OpenCV version, build options and thread count are not stated. The harness never checks the output against OpenCV's (it only shows the result with imshow). CMakeLists sets -O3 -Ofast -funroll-loops (-fopenmp for the parallel stage) but no -mfpu=neon on a 32-bit OS, so whether the cv::v_float32x4 code, and the OpenCV baseline, actually ran NEON is not stated. Minor code issues: the top-row 'leftovers' loop redeclares j and recomputes the whole row in scalar, and the vector loops assume a width divisible by 4. Kernel weights are hard-coded for sigma 1.0 and a 5x5 kernel only. No license file (raw LICENSE and LICENSE.md are 404), so reference only. Last commit 2021-03-25. Gaussian blur is an image filter, only loosely in color-and-resampling. [retier] Tutorial rather than a library (About: 'Step-by-step tutorial for optimizing a Gaussian image smoothing function'). The win comes only from the OpenMP stage spreading rows across the Pi's four cores against a single-threaded OpenCV path (the current 4.x non-IPP GaussianBlur 32F path is sepFilter2D without parallel_for_; the author's OpenCV version, build options and thread count are not stated); the project's own single-thread SIMD stage is slower than OpenCV at all three sizes, and the independent issue #3 run on a Ryzen 7 5800H with OpenCV 4.8 has OpenCV 2.7x faster. The harness never checks the output against OpenCV's. CMakeLists sets -O3 -Ofast -funroll-loops (-fopenmp for the parallel stage) but no -mfpu=neon on a 32-bit OS, so NEON use is unproven. Bugs: the SIMD and OpenMP loops lack a tail guard and overrun a stack buffer when the width is not divisible by 4; the top-row 'leftovers' loop redeclares j and recomputes the whole row in scalar. Kernel weights are hard-coded for sigma 1.0 and a 5x5 kernel. Uses operators removed in OpenCV 4.11, so it will not compile against current OpenCV (issue #2: compile error on OpenCV 3.3). No license file, so reference only. Last commit 2021-03-25.

Teaching repo in three folders (memory_management, simd, parallel_processing) using OpenCV universal intrinsics and threads; target is small ARM boards; no library packaging.

## Maintenance

Abandoned since 2021-03-25, with issues #1 and #3 unanswered. It has no license, so it is reference-only, and the SIMD stages need an OpenCV from before 4.11 (or the legacy-operators header) to compile.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Comparison.jpg is a bar chart (y-axis scale, no value labels) of OpenCV GaussianBlur vs three tutorial stages, produced by the public harness parallel_processing/main.cpp with flags in parallel_processing/CMakeLists.txt, GCC 6.3 and a Raspberry Pi 3B+; it falls short of A because the OpenCV version, build options and thread count are not stated and the numbers exist only as chart bars read by eye.
- **Verifier notes:** Chart values match the record; harness and flags read in parallel_processing/main.cpp, Gaussian_refinement5.hpp and the three CMakeLists. imrid.net blog posts not opened (blogs blocked). Metadata confirmed: 25 stars, 6 forks, not a fork, not archived, last commit 2021-03-25, no license.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** independent user measurement (issue #3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/Comparison.jpg>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/Gaussian_refinement5.hpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/Gaussian_refinement4.hpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/Gaussian_refinement3.hpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/Matrix.h>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/image.jpg>
  - <https://github.com/zanazakaryaie/fastGaussianBlur>
  - <https://github.com/zanazakaryaie/fastGaussianBlur/commits>
- **Sources the enricher read:**
  - <https://github.com/zanazakaryaie/fastGaussianBlur/issues?q=is%3Aissue>
  - <https://github.com/zanazakaryaie/fastGaussianBlur/issues/1>
  - <https://github.com/zanazakaryaie/fastGaussianBlur/issues/2>
  - <https://github.com/zanazakaryaie/fastGaussianBlur/issues/3>
  - <https://github.com/zanazakaryaie/fastGaussianBlur/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/Comparison.jpg>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/Matrix.h>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/memory_management/Gaussian_refinement3.hpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/simd/Gaussian_refinement4.hpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/main.cpp>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zanazakaryaie/fastGaussianBlur/HEAD/parallel_processing/Gaussian_refinement5.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/filter.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/cv_cpu_dispatch.h>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/hal/intrin.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/hal/intrin_cpp.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/hal/intrin_neon.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/hal/intrin_legacy_ops.h>
  - WebSearch snippets for http://imrid.net/?p=4173 and http://imrid.net/?p=4192 (blog pages themselves not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/zanazakaryaie/fastgaussianblur`) · [data/wave10/enrich/raw/github_com_zanazakaryaie_fastgaussianblur.json](../../../data/wave10/enrich/raw/github_com_zanazakaryaie_fastgaussianblur.json) (enrichment confidence 0.8)

</details>
