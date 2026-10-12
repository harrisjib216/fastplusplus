# OpenCV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Computer-vision library whose cv::resize upscaling and cv::GaussianBlur ran 3-17x faster than ImageMagick 6.9, single-threaded.

| | |
|---|---|
| **Beats** | ImageMagick (6.9 via the Wand binding, single-threaded, in pillow-perf; magick and convert 7.1.1 in the libvips Speed-and-memory-use table) |
| **Claimed result** | pillow-perf i5-4430 (Core i5-4430, Ubuntu 18.04.3; both libraries single-threaded via cv2.setNumThreads(1) and MAGICK_THREAD_LIMIT=1; median of 5 runs, 3 for ImageMagick blur) on a 2560x1600 RGB image, like-for-like rows (derived from page data): 2.14x upscale to 5478x3424, OpenCV INTER_LINEAR 57.74 ms vs ImageMagick 6.9 triangle 1007.63 ms (17.5x) and INTER_CUBIC 115.25 ms vs Catmull-Rom 1256.13 ms (10.9x); Gaussian blur radius 1 px 69.39 vs 675.34 ms (9.7x), 10 px 445.67 vs 1768.07 ms (4.0x), 30 px 1399.39 vs 4090.08 ms (2.9x). The downscale rows the record called bicubic (320x200: 5.41 vs 89.20 ms; 2048x1280: 48.20 vs 222.93 ms) are OpenCV INTER_AREA supersampling (the raw i5-4430.txt labels them 'sup'; the JSON files them under 'bic') against ImageMagick Catmull-Rom convolution, so they are not like for like. libvips wiki (Threadripper PRO 3955WX, Ubuntu 25.04): opencv 4.10 3.15 s vs magick 7.1.1 4.41 s and convert 7.1.1 4.44 s (1.4x, derived from page data). pillow-perf also shows OpenCV slower than ImageMagick at JPEG load (47.89 vs 27.38 ms) and save (56.70 vs 48.04 ms). The speedtest-resize opencv row (0.110 s vs ImageMagick_resize 0.568 s) uses go-opencv Resize with interpolation 0 (CV_INTER_NN, nearest neighbour) and is not comparable; ImageMagick_thumbnail (0.057 s) is faster there. |
| **Workload** | pillow-perf testsuite (run.py default 2560x1600 RGB; cv2_scale.py vs wand_scale.py, cv2_blur.py vs wand_blur.py): in-memory resampling and Gaussian blur, single-threaded, no file I/O; OpenCV downscales use INTER_AREA and upscales (2.14x) use INTER_LINEAR, INTER_CUBIC and INTER_LANCZOS4, while ImageMagick uses triangle, catrom and lanczos at every size; blur uses the same window (1 + 2\*ceil(2.5r)) and sigma r. libvips wiki (vips-bench opencv.cc vs im7.sh): load a 10000x10000 8-bit RGB tiled TIFF, crop 100 px per edge, resize to 90 percent (OpenCV's default INTER_LINEAR 4-point bilinear vs ImageMagick -filter triangle convolution), 3x3 sharpen, save. |
| **Metric** | throughput |
| **Hardware** | pillow-perf: Intel Core i5-4430 @ 3.00GHz, Ubuntu 18.04.3 (also Xeon 8124M, EPYC 7571 and Core i5-8279U files in the same directory). libvips wiki: AMD Ryzen Threadripper PRO 3955WX 16-core, Ubuntu 25.04. |
| **Compiler and flags** | Not stated: pillow-perf installs the opencv-python binary wheel (the data file says 'Opencv 4.1'; auto/run.sh pinned opencv-python 4.1.2.30 from Nov 2019 to Feb 2020) and ImageMagick from the system; the libvips wiki used the Ubuntu 25.04 opencv 4.10 package, with the driver compiled as 'g++ -g -Wall opencv.cc'. |
| **Adoption** | 91.1k stars; ubiquitous computer-vision library |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/opencv/opencv) · [benchmark](https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json) |

## Verdict

pillow-perf (run by the Pillow-SIMD authors) timed the opencv-python 4.1 binary wheel against ImageMagick 6.9 through Wand on one Core i5-4430 core (Ubuntu 18.04.3, both libraries forced single-threaded, compiler and flags not stated) on a 2560x1600 RGB image: like-for-like upscale to 5478x3424 is 17.5x faster bilinear and 10.9x faster bicubic, and Gaussian blur is 9.7x, 4.0x and 2.9x faster at sigma 1, 10 and 30. Reading the 4.1.2 source shows the sigma 10 and 30 blur rows ran a kernel whose 8-bit fixed-point taps summed to 254/256 and 243/256 per pass (computed from getFixedpointGaussianKernel, matching issue #9863's 10 percent darkening at ksize 151, sigma 30), a bug fixed in 4.2.0 by error-diffusion quantisation; the fix changes coefficients, not the code path, so the timings are probably still representative, but the measured output was wrong. Separately, the libvips wiki pipeline (crop, 0.9x resize, sharpen, TIFF load and save on a 16-core Threadripper PRO 3955WX, Ubuntu 25.04 packages) has OpenCV 4.10 at 3.15 s against multi-threaded ImageMagick 7.1.1 at 4.41 s (1.4x).

## Use it when

- Upscaling 8-bit RGB images in-process where bilinear or bicubic quality is enough: pillow-perf measured 57.7 ms (bilinear) and 115.3 ms (bicubic) for 2560x1600 to 5478x3424 on one Haswell core, versus 1007.6 and 1256.1 ms for ImageMagick 6.9.
- Small-sigma Gaussian blur on 8-bit images (sigma about 1, 7-tap window): 69 ms vs 675 ms for ImageMagick on a 4 MP frame, single-threaded.
- Integer-factor downscales with INTER_AREA (box averaging), e.g. 2560x1600 to 320x200 in 5.4 ms, when a box filter is an acceptable shrink filter.
- Pipelines that already link OpenCV for vision work, where adding ImageMagick only for resize or blur would add a second heavy dependency.
- Multi-core servers: resize and GaussianBlur split rows across threads with parallel_for_ (pthreads by default); the catalogued numbers were taken with cv2.setNumThreads(1), so default runs can be faster.

## Skip it when

- Quality downscaling with bilinear or bicubic: cv::resize does no antialiasing, and the OpenCV docs advise INTER_AREA for shrinking; an antialiased resize is still an open feature request (#25620). Convolution resamplers such as Pillow-SIMD, libvips or fast_image_resize are the like-for-like choice.
- Large-sigma Gaussian blur: the separable filter costs O(window) per pixel, so sigma 30 (151 taps) took 1.40 s, while Pillow 7.0.0 in the same pillow-perf file stays at about 0.19 s at every radius and Pillow-SIMD AVX2 bicubic upscale (76.6 ms) also beats OpenCV's 115.3 ms.
- OpenCV builds older than 4.2.0 for 8-bit GaussianBlur with large windows: the fixed-point kernel was rounded tap by tap without renormalising, so output came out darker (issue #9863: ksize 151, sigma 30, about 10 percent darker).
- JPEG-heavy pipelines judged on codec speed: pillow-perf shows OpenCV slower than ImageMagick at JPEG load (47.9 vs 27.4 ms) and save (56.7 vs 48.0 ms).
- Projects that need a small dependency, colour management, or the format breadth of ImageMagick.

## How it is fast

8-bit INTER_LINEAR resize is a separable two-pass filter with precomputed integer coefficient tables (INTER_RESIZE_COEF_BITS = 11), a horizontal pass into an int row buffer and a SIMD vertical pass (VResizeLinearVec_32s8u), and it always reads only 2x2 source pixels, which is also why it does not antialias on shrinking. INTER_AREA has a SIMD box-average fast path for integer factors (ResizeAreaFastVec_SIMD_8u) and precomputed overlap weights otherwise. 8-bit GaussianBlur runs a bit-exact separable fixed-point filter (ufixedpoint16, 8 fractional bits) with symmetric-kernel folding and special 3- and 5-tap kernels, split over rows with parallel_for_ and compiled for several ISAs with runtime CPU dispatch (CV_CPU_DISPATCH). In the measured 4.1.2 build, cv::resize first tried Intel IPP's iwiResize when OpenCV was built with IPP (WITH_IPP defaults to ON on x86), which IPP accepts for 8-bit INTER_CUBIC and INTER_LANCZOS4 but not for 8-bit bilinear, area or nearest, so the bicubic and Lanczos rows may be IPP code rather than OpenCV's own kernels. Current 4.x routes this through hal/ipp (ipp_hal_resize).

## Compared with alternatives

Pick OpenCV over Pillow-SIMD, libvips or fast_image_resize when you already depend on it or need fast bilinear upscaling and small-kernel blurs inside a vision pipeline; pick those convolution resamplers when downscale quality matters, and pick a box-blur approximation (FastBoxBlur, LibGaussianBlur, Pillow) for large-radius blurs. For a whole load-resize-save pipeline, libvips (0.57 s) is far ahead of OpenCV (3.15 s) in the same libvips wiki table.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake build of opencv_core + opencv_imgproc; prebuilt opencv-python wheels and distro packages) |
| **Dependencies** | imgproc needs only opencv_core; optional Intel IPP ICV on x86 (WITH_IPP on by default except MinGW), TBB or OpenMP (off by default; pthreads parallel_for is on), Carotene and KleidiCV HALs on ARM, image codec libraries for imgcodecs |
| **Minimum toolchain** | C++11 for the 4.x line, C++17 for the 5.x line (default branch); CMake 3.7+ for 4.x |
| **Platforms** | x86-64 with runtime dispatch up to AVX2/AVX-512, AArch64 (NEON, Carotene, KleidiCV), RISC-V and others |
| **Thread safety** | Not documented in the files read. Functions work on caller-owned Mats; the internal parallel_for_ pool is a process-wide setting changed with cv::setNumThreads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Different filters under the same names: OpenCV INTER_CUBIC uses a = -0.75 (and the 4.1.2 IPP path is configured to match), while ImageMagick's catrom is a = -0.5; INTER_LANCZOS4 is an 8x8 Lanczos-4 kernel, not ImageMagick's Lanczos-3; INTER_AREA acts like nearest neighbour when enlarging.
- 8-bit results come from fixed-point arithmetic (11-bit resize coefficients, 8-bit-fraction Gaussian taps): at large sigma each Gaussian tap is only a few 1/256 steps, and plain INTER_LINEAR is not the bit-exact mode (INTER_LINEAR_EXACT is).
- When ksize is 0, GaussianBlur derives it from sigma with 3 sigma per side for 8-bit images but 4 sigma for float images, so 8-bit and float blurs of the same sigma use different windows.
- imread returns BGR channel order, and resize with interpolation code 0 is nearest neighbour; third-party benchmarks that pass 0 (as the speedtest-resize go-opencv row does) are not measuring bilinear.

## Known shortcomings

- Claim overstated: the pillow-perf 'bic' downscale cells (16.5x, 4.6x) are really INTER_AREA supersampling (the raw i5-4430.txt labels them 'sup') against ImageMagick's Catmull-Rom, not like for like. Like-for-like single-threaded rows: upscale 17.5x bilinear and 10.9x bicubic, blur 9.7x/4.0x/2.9x vs ImageMagick 6.9; the libvips wiki run gives 3.15 vs 4.41 s (1.4x). The speedtest-resize OpenCV row uses nearest neighbour (interpolation 0) and is not comparable, and OpenCV is slower than ImageMagick at JPEG load and save.
- The Pillow-comparison blur rows were measured on OpenCV 4.1.x whose 8-bit GaussianBlur rounded each fixed-point tap without renormalisation (getFixedpointGaussianKernel, 8 fraction bits): at the 30 px case (151 taps, sigma 30) the taps sum to 243/256 per pass, about 10% darker (issue #9863), fixed in 4.2.0; the timing is probably unchanged since the code path is the same. In 4.1.2 cv::resize tries Intel IPP first and IPP accepts 8-bit INTER_CUBIC and LANCZOS4, so those rows may be IPP code rather than OpenCV's own. Large-sigma blur is O(window): Pillow 7.0 stays near 0.19 s at every radius against OpenCV's 1.40 s at 30 px, and Pillow-SIMD AVX2 bicubic upscale (76.6 ms) beats OpenCV (115.3 ms).

## Caveats and trade-offs

The pillow-perf downscale cells filed as bicubic for OpenCV (26x16, 320x200, 2048x1280) are INTER_AREA supersampling runs (cv2_scale.py; the raw i5-4430.txt labels them 'sup') compared against ImageMagick Catmull-Rom convolution; pillow-perf's own page says comparing OpenCV's bicubic with correct convolution implementations is meaningless and that supersampling is a different method, so those 16.5x and 4.6x ratios are not like for like. The like-for-like pillow-perf rows are the 2.14x upscale (INTER_LINEAR vs triangle; INTER_CUBIC with a=-0.75 vs Catmull-Rom, both 4x4 support) and the Gaussian blur (same window and sigma), all single-threaded. The Lanczos row is OpenCV Lanczos4 (439.03 ms) against ImageMagick Lanczos3 (1495.61 ms), not like for like. OpenCV is slower than ImageMagick at JPEG load and save in the same file. The baseline is ImageMagick 6.9 from Ubuntu 18.04 (2020 run), and the suite is maintained by the Pillow-SIMD authors. In the libvips pipeline OpenCV's default 4-point bilinear does slightly less filtering than ImageMagick's triangle convolution at 0.9 scale; the test is I/O dominated, the wiki says it flatters libvips, and OpenCV is listed among systems that do not thread automatically. The speedtest-resize opencv row (go-opencv Resize with interpolation 0, nearest neighbour) is not comparable to ImageMagick_resize.

Large dependency; BGR channel order; cv::resize with bilinear or bicubic does not apply an anti-aliasing filter on strong downscales (per the pillow-resize README), so output differs from convolution-based resamplers such as Pillow, libvips or ImageMagick; JPEG load is slower than ImageMagick in pillow-perf (47.89 vs 27.38 ms on the i5-4430).

## Maintenance

Very active (last commit 2026-10-02 on 4.x, default branch 5.x, 91.1k stars) and Apache-2.0; usable directly from wheels or distro packages, but the catalogued pillow-perf numbers come from a 2019-2020 opencv-python 4.1 wheel.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now B.
- **Tier reason:** pillow-perf is a well-known suite independent of OpenCV and ImageMagick (run by the Pillow-SIMD authors) with public code (testsuite/cases/cv2_scale.py, cv2_blur.py, wand_scale.py, wand_blur.py, run.py, auto/run.sh) and a named CPU (Core i5-4430), and the libvips wiki row (vips-bench opencv.cc vs im7.sh, Threadripper PRO 3955WX) is also independent; both use binary wheels or distro packages with no compiler or flags, so B, not A. Tier unchanged; the verdict is downgrade because part of the claim was overstated.
- **Verifier notes:** Downgrade is for the overstated claim, not the tier: the upscale and blur rows and the libvips wiki row still support B. ImageMagick 6.9.7-4 and 6.8.9-9 do not appear in the data I opened (it says 'ImageMagick 6.9' and 'Opencv 4.1'); OpenCV 4.1.2 is consistent with the auto/run.sh pin history. Metadata checked on github.com: Apache-2.0, 91.1k stars, default branch 5.x, last commit 2026-10-02 on 4.x (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/i5-4430.txt>
  - <https://github.com/python-pillow/pillow-perf>
  - <https://github.com/python-pillow/pillow-perf/tree/main/testsuite/cases>
  - <https://github.com/python-pillow/pillow-perf/tree/main/docs/src/data>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2_full_cycle.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand_full_cycle.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/auto/run.sh>
  - <https://github.com/python-pillow/pillow-perf/commits/main/auto/run.sh>
  - <https://github.com/python-pillow/pillow-perf/commits/main/testsuite/cases/cv2_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/index.html>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/c5.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/m5a.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/macbook.2019.json>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/opencv.cc>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://github.com/libvips/vips-bench/issues/8>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/opencv.go>
  - <https://raw.githubusercontent.com/lazywei/go-opencv/master/opencv/imgproc.go>
  - <https://github.com/opencv/opencv>
  - <https://github.com/opencv/opencv/commits/4.x>
- **Sources the enricher read:**
  - <https://github.com/opencv/opencv/releases>
  - <https://github.com/opencv/opencv/issues?q=is%3Aissue%20resize%20antialias>
  - <https://github.com/opencv/opencv/issues?q=is%3Aissue%20GaussianBlur%20performance>
  - <https://github.com/opencv/opencv/issues/9863>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/README.md>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/CMakeLists.txt>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/CMakeLists.txt>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/resize.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/include/opencv2/imgproc.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/hal/ipp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/hal/ipp/include/ipp_hal_imgproc.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/cmake/OpenCVDetectCXXCompiler.cmake>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/cmake/OpenCVMinDepVersions.cmake>
  - <https://raw.githubusercontent.com/opencv/opencv/5.x/cmake/OpenCVDetectCXXCompiler.cmake>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/imgproc/src/resize.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/imgproc/src/smooth.simd.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/imgproc/src/fixedpoint.inl.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/imgproc/src/precomp.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.1.2/modules/core/include/opencv2/core/private.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.2.0/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.3.0/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/i5-4430.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/docs/src/data/i5-4430.txt>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/cv2_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/wand_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/main/auto/run.sh>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/opencv.cc>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/opencv/opencv`) · [data/wave10/enrich/raw/github_com_opencv_opencv.json](../../../data/wave10/enrich/raw/github_com_opencv_opencv.json) (enrichment confidence 0.8)

</details>
