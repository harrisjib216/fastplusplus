# FastBoxBlur

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++ sliding-sum box blur with reflect-101 borders; claims 2-3x over OpenCV cv::blur on huge kernels.

| | |
|---|---|
| **Beats** | OpenCV cv::blur (box filter) |
| **Claimed result** | README Performance: 'designed to be a portable, easy, and faster replacement of cv::blur, using an i7-10750H, it's around 2x - 3x time faster'. The chart data (py/performance.ipynb, times in ms for 45 RGB 8-bit images from 1500x1000 to 11400x7600, box size 2\*width-1): 1 pass cv::blur 20.2 to 1900.6 ms vs fastboxblur 15.9 to 650.8 ms; 2 passes cv::blur 39.3 to 3970.2 ms vs fastboxblur 23.6 to 1180.7 ms. Speedups (derived from page data): 1 pass 1.27x to 2.92x (median 2.62x), 2 passes 1.49x to 3.36x (median 2.90x), rising with image size. |
| **Workload** | Box blur with reflect-101 style mirror padding (edge sample not repeated, like OpenCV's default BORDER_REFLECT_101) on 45 synthetic-size RGB 8-bit images from 1500x1000 to 11400x7600, box size 2\*width-1, 1 and 2 passes; FastBoxBlur does horizontal sliding-sum passes, a blocked transpose, vertical passes as horizontal passes, and a transpose back (timings listed in py/performance.ipynb, plot in data/bench.png). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10750H |
| **Compiler and flags** | Repo Makefile (the only build in the repo; the benchmark build is not stated): g++ fastboxblur.cpp -O3 -fopenmp -std=c++17. The OpenCV side's version, compiler and build options are not stated. |
| **Adoption** | 5 stars |
| **Last commit** | 2022-11-01 |
| **Links** | [repository](https://github.com/michelerenzullo/FastBoxBlur) · [benchmark](https://github.com/michelerenzullo/FastBoxBlur#performance) |

## Verdict

The README claims 2-3x over cv::blur on an i7-10750H. The hard-coded notebook timings (45 RGB 8-bit images, 1500x1000 to 11400x7600, ksize = 2\*width-1) give 1.27x to 2.92x for 1 pass and 1.49x to 3.36x for 2 passes (derived from page data), rising with size. The cv::blur driver, OpenCV version and build (IPP or HAL), and thread settings are not in the repo, and FastBoxBlur most likely ran OpenMP on 12 threads against single-threaded FilterEngine code, so per-core it may not be faster.

## Use it when

- You need a cv::blur-like box filter with reflect-101 borders and want no OpenCV dependency (one \~250-line header).
- Large odd kernels that stay below the image's smaller dimension (ksize &lt;= min(w,h) - 1), where the O(1)-per-pixel sliding sum pays off.
- Repeated box passes (passes = 2-3) as a cheap Gaussian approximation on 8-bit, 16-bit or float buffers with 1-4 channels.
- Multi-core x86 or ARM builds with OpenMP, where the parallel row loops supply the speed (the code is scalar).

## Skip it when

- Kernels wider than about half an image dimension: the large-radius path in horizontal_blur_kernel_reflect computes wrong sums (see gotchas); up to 59/255 off in a transliteration test.
- Small kernels (3x3, 5x5) or single-threaded builds: no SIMD, and the only published numbers use kernels thousands of pixels wide.
- Even ksize, non-square kernels, an anchor, or border modes other than reflect-101: r = (ksize-1)/2 is truncated, so ksize 4 becomes a 3-tap box.
- More than 4 channels, strided or ROI buffers, or images above about 715 MP RGB: other channel counts only print a message and leave garbage, and w\*h\*channels is computed in int.

## How it is fast

Each 1D pass is a running-sum (sliding accumulator) box filter, O(1) per pixel regardless of kernel size, with the mirrored border folded into the initial sum instead of padding the row. Vertical passes are run as horizontal passes on a transposed image, with a cache-blocked transpose (flip_block, blocks sized for 256 KB). Every row loop and the transpose are '#pragma omp parallel for', so with -fopenmp (the repo Makefile's flag) it uses all cores; there is no SIMD.

## Compared with alternatives

Among catalogued entries only go-images/images also does box blur, in Go, and loses to OpenCV there. Pick FastBoxBlur when you want a dependency-free C++ header and can keep kernels below the image size. For SIMD-tuned general image kernels, FlyCV or OpenCV itself (with IPP) is the safer choice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stb_image only in the demo); OpenMP optional |
| **Minimum toolchain** | C++17 (std::is_integral_v, if constexpr per commit history); repo Makefile uses g++ -O3 -fopenmp -std=c++17 |
| **Platforms** | any (portable scalar C++) |
| **Thread safety** | not documented; no global state and each call allocates its own temporary image, but the call itself spawns OpenMP parallel loops |
| **Drop-in for the baseline** | partial: same reflect-101 box average as cv::blur for odd ksize below the image size, but a raw-pointer, in-place API with square odd kernels only |

## Gotchas

- Correctness bug for big kernels: when 2r+2 exceeds the row length (ksize above about the dimension minus 1), the middle loop is skipped and the tail loop restarts at position w-r-1 &lt;= r, so the running sum is out of step with the output position. The mirror index 'max_end - ri % max_end' uses absolute buffer indices, so later rows can read the previous row's last pixel and row 0 mirrors differently. A Python transliteration of the loop gave wrong sums at every pixel for w=20, r=10..19, and up to 59/255 error on a 150x100 test image at ksize 151. At the benchmark's own setting (ksize 2\*width-1, radius clamped to dimension-1 on both axes) the 2D error was at most 1 level.
- The radius is clamped per axis (r = min(r, w-1)), so ksize larger than the smaller side silently gives a non-square kernel that cv::blur would not use.
- The header includes only &lt;vector&gt; but calls sqrt, std::min, printf and std::conditional_t, so add &lt;cmath&gt;, &lt;algorithm&gt;, &lt;cstdio&gt; and &lt;type_traits&gt; before including it on stricter toolchains. The demo driver parses ksize as 'sigma', defaults passes to 3 (README says 1), and its USE_FLOAT path writes back a buffer that is never filled.
- Benchmark provenance is unclear. The only published cv::blur-vs-fastboxblur driver is in the same author's Blur_algorithms Source.cpp (Test flag 4 and -Dboxblur, commented-out loop over the same 45 sizes, which are actually 1000 wide by 1500 tall via cv::Size(y, x)). It passes ksize = x (the image height, e.g. 1500) to fastboxblur but (int)sqrt(x)^2 (e.g. 1444) to cv::blur, with 2 passes each. That is not the chart's '2\*width-1', and on 1000-wide rows radius 749 falls in the wrong-output range above. Which driver produced the chart is not documented.

## Known shortcomings

- Borderline category (box blur, a convolution, not resampling). Timings live in py/performance.ipynb (1-pass 1.27-2.92x, 2-pass 1.49-3.36x vs cv::blur, derived from page data); the cv::blur driver is not in the repo, OpenCV version, build and thread count unstated, and FastBoxBlur runs OpenMP on every pass while OpenCV 4.x's CPU boxFilter has no parallel_for_, so likely 12 threads against 1. Kernel width 2\*width-1 is extreme; radius clamped per axis. MIT stated only in the README.
- Correctness bug in horizontal_blur_kernel_reflect: when 2r+2 exceeds the row width the middle loop is skipped and the tail loop restarts at w-r-1 with wrong sums, and the mirror index (max_end - ri % max_end) uses absolute indices so rows after the first read the previous row's last pixel (Python transliteration: up to 59/255 off at ksize 151 on a 150x100 image). At the chart's ksize of 2\*width-1 (radius clamped to dim-1) the error is at most 1 level and the bug path does about 2w steps per row, so the chart is not inflated. The only published cv::blur-versus-fastboxblur driver (Blur_algorithms Source.cpp, same 45 sizes) gives fastboxblur ksize 1500 against cv::blur 1444 with 2 passes, radius 749 on 1000-wide rows inside the bug range; the chart driver is undocumented. No SIMD, OpenMP; header not self-contained; even ksize rounded down.

## Caveats and trade-offs

Likely threads-versus-one-thread: fast_box_blur.h parallelises every horizontal pass and the transpose with '#pragma omp parallel for' and the Makefile builds with -fopenmp, so on the 6-core/12-thread i7-10750H FastBoxBlur probably ran on all hardware threads, while OpenCV 4.x's CPU cv::blur goes through boxFilter's single-threaded FilterEngine (no parallel_for_ in box_filter.dispatch.cpp or filter.dispatch.cpp) unless a HAL intercepts it; the 1.3-3.4x lead is smaller than the thread count, so per-core FastBoxBlur may not be faster. The cv::blur driver is not in the repo, so the OpenCV version, IPP/HAL build, setNumThreads value and exact cv::blur arguments cannot be checked. The kernel size 2\*width-1 is extreme (thousands of pixels); OpenCV's FilterEngine pads each row by the kernel radius, so this size inflates OpenCV's border work, and typical small kernels were not measured. FastBoxBlur clamps the radius to dimension-1 per axis (r = min(r, w-1)), so on landscape images its vertical kernel is smaller than a cv::blur call given the same square ksize would use; whether the benchmark matched that is unknown. Integer accumulation with float normalisation and +0.5 rounding; output equivalence with cv::blur is not tested in the repo. Borderline for color-and-resampling (a convolution filter, not a resampler). MIT is stated only in the README; there is no LICENSE file. Last commit 2022-11-01; 5 stars.

Header-only (fast_box_blur.h), templated on pixel type and channel count, sliding-accumulator box blur plus cache-blocked transposition, N passes. Emulates mirrored border padding without extra memory, but the radius must stay below the image width. No SIMD (the README says SIMD could be faster); OpenMP in the demo build. Box blur only, and README says it is based on bfraboni/FastGaussianBlur.

## Maintenance

Abandoned since 2022-11-01 (5 stars, no issues or PRs); MIT is stated in the README only (no LICENSE file). The header is small enough to vendor, but fix or guard the large-kernel path first. The chart was last updated on 2022-09-28, before the 2022-10-11 flip_block block-size change, so HEAD differs slightly from the timed code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: README states '2x - 3x' on an i7-10750H and the chart's raw timings are hard-coded in py/performance.ipynb, but the C++ driver that timed cv::blur is not in the repo and the OpenCV version, build (IPP, threads) and benchmark flags are not stated.
- **Verifier notes:** The per-size chart data is readable as text in py/performance.ipynb (hard-coded timings), which supports the README's 2x-3x on large images but shows only 1.27x at 1500x1000. The OpenMP-versus-single-threaded-OpenCV concern is strong enough that the orchestrator may want to note it as the main shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/michelerenzullo/FastBoxBlur>
  - <https://github.com/michelerenzullo/FastBoxBlur/commits/main>
  - <https://github.com/michelerenzullo/FastBoxBlur/tree/main/py>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/Makefile>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/fastboxblur.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/fast_box_blur.h>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/py/performance.ipynb>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/box_filter.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/filter.dispatch.cpp>
- **Sources the enricher read:**
  - <https://github.com/michelerenzullo/FastBoxBlur>
  - <https://github.com/michelerenzullo/FastBoxBlur/issues?q=is%3Aissue>
  - <https://github.com/michelerenzullo/FastBoxBlur/pulls?q=is%3Apr>
  - <https://github.com/michelerenzullo/FastBoxBlur/commits/main>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/Makefile>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/fast_box_blur.h>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/fastboxblur.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/py/performance.ipynb>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/box_filter.dispatch.cpp>
  - <https://github.com/bfraboni/FastGaussianBlur>
  - <https://github.com/awxkee/libblur>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/Source.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/michelerenzullo/fastboxblur`) · [data/wave10/enrich/raw/github_com_michelerenzullo_fastboxblur.json](../../../data/wave10/enrich/raw/github_com_michelerenzullo_fastboxblur.json) (enrichment confidence 0.7)

</details>
