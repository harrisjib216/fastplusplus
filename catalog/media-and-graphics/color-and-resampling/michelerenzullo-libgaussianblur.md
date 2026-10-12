# LibGaussianBlur (FFT Gaussian blur, from Blur_algorithms)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> C++20 FFT (pffft) separable Gaussian blur for 8-bit RGB/RGBA; 9-20x faster than cv::GaussianBlur at very large sigma.

| | |
|---|---|
| **Beats** | OpenCV cv::GaussianBlur |
| **Claimed result** | Blur_algorithms README (repo archived 2024-12-26): 'how surprisingly fast is the 1D implementation in pffft compared to OpenCV that is the standard market reference', with linear versus exponential growth as size rises. py/performance.ipynb cell 0 holds hard-coded arrays in ms (pffft vs cv::GaussianBlur): 2000x1300 11.52 vs 107.43; 6500x4000 114.97 vs 1604.24; 12000x7300 433.94 vs 6317.43; 24000x14500 1728.56 vs 33509.56; at 1500x1000 OpenCV was faster, 24.97 vs 32.05. Derived from page data: pffft takes 9.0x (2500x1600) to 20.0x (23000x13900) less time at 45 of 46 sizes, and 0.78x at 1500x1000. |
| **Workload** | True Gaussian blur of 3-channel 24-bit images with sigma = sqrt(image dimension), using pffft 1D separable FFT convolution in float32 tiles with reflect-101 padding, versus cv::GaussianBlur(image, image, Size(0,0), sigma) on 8-bit data. The notebook labels 46 sizes from 1500x1000 to 24000x14500; the commented-out loop in Source.cpp describes 45 sizes from 1500x1000 to 11400x7600. Apple M3 Pro, 12 cores. |
| **Metric** | latency |
| **Hardware** | Apple M3 Pro, 12 cores, 16 MB cache setting for PocketFFT |
| **Adoption** | 5 stars (LibGaussianBlur); 4 stars on archived Blur_algorithms; published on PyPI as gaussianblur 1.1.2 (2025-03-29) |
| **Last commit** | 2025-03-29 |
| **Links** | [repository](https://github.com/michelerenzullo/LibGaussianBlur) · [benchmark](https://github.com/michelerenzullo/Blur_algorithms) |

## Verdict

Blur_algorithms' notebook (hard-coded single runs, Apple M3 Pro, 12 cores) shows the pffft path taking 9.0x to 20.0x less time than cv::GaussianBlur(img, img, Size(0,0), sigma=sqrt(x)) at 45 of 46 sizes, and 0.78x at 1500x1000 (derived from page data). The timed pffft_ includes deinterleave, kernel FFT and setup, so it is end-to-end. Current OpenCV 4.x runs 8-bit GaussianBlur as a bit-exact fixed-point direct convolution (233 taps at sigma 38.7) under parallel_for_, so both sides were probably multi-threaded, but the OpenCV version, build, compiler and thread settings are not stated.

## Use it when

- Very large sigma (roughly 30 px and up) on multi-megapixel photos, where direct separable convolution needs hundreds of taps per pixel.
- 8-bit RGB/RGBA in apps that cannot ship OpenCV: mobile (Android/iOS), browser (WASM with threads and SIMD), or a small native dependency.
- Python 3.11 on macOS arm64 or Linux x86-64 where a pip wheel without OpenCV is convenient.
- Smooth photographic content, where the Nyquist-bin defect below stays under about 1 level.

## Skip it when

- Small or moderate sigma: OpenCV was faster at the smallest benchmark size (1500x1000, sigma 38.7: 24.97 ms vs 32.05 ms), and FFT padding overhead dominates small kernels.
- Content with pixel-level texture, noise, dithering or halftones: the highest-frequency component is not blurred (gotcha 1), so stripes survive and leak across whole rows.
- Elongated images with sigma above about one third of the short side: the reflect padding then overruns the row buffer (gotcha 2).
- Grayscale, 16-bit, float or planar data (only 3- or 4-channel uint8 is accepted; other channel counts print an error and return unchanged), or when bit-exact parity with cv::GaussianBlur is needed.

## How it is fast

Separable FFT convolution: each row is reflect-101 padded and zero-padded to a 2^a\*3^b\*5^c length, transformed with pffft (Pommier's SIMD real FFT), multiplied by the precomputed spectrum of a centred, symmetric Gaussian (real-valued, so only real parts are used), and inverse transformed. Columns get the same treatment after a cache-blocked transpose. Cost per pixel grows with log(FFT length) instead of with the kernel width, which is what beats direct convolution once sigma reaches tens of pixels. Rows and columns are split across std::thread workers (hybrid_loop) when built with ENABLE_MULTITHREADING.

## Compared with alternatives

No other catalogued color-and-resampling entry does large-sigma Gaussian blur; FastBoxBlur (same author) is the cheaper option when a box-blur approximation is acceptable. Use LibGaussianBlur when you need a true Gaussian at huge sigma without OpenCV, and stay with OpenCV for small kernels or bit-exact output.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | pffft (Pommier, git submodule, built as an object library); pybind11 for the Python module; googletest for tests |
| **Minimum toolchain** | C++20 (std::numbers), CMake 3.14+ |
| **Platforms** | Linux, macOS, Android, iOS, WebAssembly (Emscripten, -msimd128); pffft SIMD on SSE/NEON/WASM; Windows not supported yet (on roadmap) |
| **Thread safety** | not documented; no global state, but each call spawns hardware_concurrency std::threads per stage when ENABLE_MULTITHREADING is on (it is OFF by default in CMakeLists.txt) |
| **Drop-in for the baseline** | partial: replaces cv::GaussianBlur(src, dst, Size(0,0), sigma) for interleaved 8-bit RGB/RGBA only, with a different kernel width (radius sigma\*sqrt(2 ln 255)-1, about +-3.33 sigma, vs OpenCV's +-3 sigma for 8-bit) and float, not bit-exact, arithmetic |

## Gotchas

- Nyquist-bin bug (in LibGaussianBlur's src/gaussianblur.cpp and in the benchmarked Blur_algorithms pffft_ path): pffft_transform_ordered packs F(0) and F(N/2) into elements 0 and 1, but pffft_sorted_optimized_convolution scales element 1 by the kernel's DC gain (1) instead of its Nyquist response (about 1e-4). The alternating component therefore passes unblurred across the whole row. In a Python transliteration (n=200, sigma=sqrt(n)), 1-px stripes came out 243.8/11.2 instead of 127.5, uniform noise was off by up to 11.9 levels, and a half-striped/half-black row gave +-58 in the black half. With the index fixed, the output matched direct convolution exactly. The fix costs nothing, so timings are unaffected.
- The kernel width is clamped to the larger image side, but the reflect-pad copy needs pad &lt;= tile length - 1. For aspect ratio above 2 and sigma above about short side/3.33 (e.g. 500x2000 at sigma 200: pad 665 vs 499), std::copy_n reads outside the column buffer (heap over- and under-read). The benchmark's pads (128-514) were well inside, and the tests use only 3x3 and 10240x10240 square images.
- Float to uint8 conversion adds 0.5 with no clamp, so negative or &gt;255.5 results (which the Nyquist leak can produce) are undefined conversions in C++.
- Performance knobs are hard-coded for the author's Apple M3 Pro: L2_CACHE_SIZE is 16 MB (2048x2048-float transpose blocks, far larger than typical x86 L2), threads are created per stage rather than pooled, and every row and column task copies three aligned buffers.

## Known shortcomings

- Correctness bug behind the numbers: pffft_sorted_optimized_convolution scales the packed Nyquist element by the kernel DC instead of the kernel Nyquist (same code in the benchmarked Blur_algorithms pffft_ path), so 1-pixel stripes give 243.8/11.2 instead of 127.5, noise is off by plus or minus 11.9 and a half-stripe row by plus or minus 58 in its black half; with the index fixed the output matches direct convolution exactly, so the README's 'indistinguishable from direct convolution' is false while the timing (same operation count) stands. Heap out-of-bounds read when the kernel is clamped to the long side and the pad exceeds the short side minus 1 (aspect over 2 with sigma above about short/3.33; the benchmark pads of 128-514 are safe); float to uint8 without clamping; ENABLE_MULTITHREADING off by default; the OpenCV version is unknown and its 8U GaussianBlur is fixed-point with parallel_for_.

## Caveats and trade-offs

The numbers live in the archived predecessor Blur_algorithms (no LICENSE file), not in LibGaussianBlur. LibGaussianBlur's src/gaussianblur.cpp keeps the same pffft ordered-transform tile convolution (pffft_sorted_optimized_convolution) but has never been benchmarked against OpenCV in its own repo. Each size was timed once (std::chrono printf in Source.cpp, no repetitions or warm-up). The pffft time at 1500x1000 (32 ms) is higher than at 2000x1300 (11.5 ms), which points to a cold-start cost in the first run. The size axis cannot be matched to the code. The commented-out benchmark loop in Source.cpp covers 45 sizes in 225x150 steps up to 11400x7600, calls cv::Size(y, x) so each image is 1000 wide by 1500 tall, and sets sigma = sqrt(x). The notebook labels 46 sizes in 500x300 steps up to 24000x14500, and the README says 45 images up to 11400x7600. The repo states no compiler, flags, OpenCV version or OpenCV build (IPP, NEON, threading backend). The FFT path is multi-threaded through hybrid_loop (OpenMP or std::thread, chosen by build macros), and nothing records which was used or how many threads OpenCV ran. The two sides compute different things. The FFT side convolves in float32, truncates the kernel at radius sigma\*sqrt(2 ln 255) - 1 and clamps it to the largest image dimension. OpenCV runs its own direct separable 8-bit convolution with its own kernel-size rule. No accuracy comparison against OpenCV output is published. sigma = sqrt(width) gives kernels of hundreds of taps, the worst case for direct convolution. The result does not transfer to small sigma, and OpenCV won at the smallest size. A Gaussian blur is a filter, not resampling or colour conversion, so the fit to this category is borderline. The last commit is an automated coverage-badge update.

C++20 library using FFT tiles and pffft (a bundled FFT library); pads images to FFT-friendly sizes, so more memory than direct convolution; Python wheels, WebAssembly and mobile builds provided. The FFT approach pays off only for large sigma; small kernels are the OpenCV regime.

## Maintenance

Stale: 23 commits, 5 stars, no issues or PRs, PyPI 1.1.2 on 2025-03-29, and the last commit is a coverage-badge update. It is Apache-2.0 with a LICENSE file, so it is copyable, but fix the Nyquist index and guard the pad length before production use. The benchmark itself lives in the archived Blur_algorithms repo, which has no LICENSE file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party timings hard-coded in cell 0 of Blur_algorithms py/performance.ipynb (arrays plotted to bench.png), produced by Source.cpp's Test() (cv::GaussianBlur vs pffft_, single-shot std::chrono). CPU is stated (Apple M3 Pro) but there is no build file, compiler, flags, OpenCV version or build, or thread count, so the tier is C.
- **Verifier notes:** Notebook numbers and the 9x-20x range are confirmed exactly (cell 0). The weak points are single-shot timing, unknown OpenCV build and threads, and a size axis that disagrees with the benchmark loop in Source.cpp. The measured algorithm is the same one LibGaussianBlur ships.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/michelerenzullo/Blur_algorithms>
  - <https://github.com/michelerenzullo/Blur_algorithms/commits/master>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/py/performance.ipynb>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/Source.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/Utils.hpp>
  - <https://github.com/michelerenzullo/LibGaussianBlur>
  - <https://github.com/michelerenzullo/LibGaussianBlur/commits/main>
  - <https://github.com/michelerenzullo/LibGaussianBlur/tree/main/src>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/src/gaussianblur.cpp>
  - <https://pypi.org/pypi/gaussianblur/json>
- **Sources the enricher read:**
  - <https://github.com/michelerenzullo/LibGaussianBlur>
  - <https://github.com/michelerenzullo/LibGaussianBlur/tree/main/tests>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/src/gaussianblur.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/include/gaussianblur/gaussianblur.h>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/include/gaussianblur/helpers.hpp>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/tests/test_gaussianblur.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/LibGaussianBlur/HEAD/tests/test_helpers.hpp>
  - <https://pypi.org/pypi/gaussianblur/json>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/README.md>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/Source.cpp>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/Utils.hpp>
  - <https://raw.githubusercontent.com/michelerenzullo/Blur_algorithms/HEAD/py/performance.ipynb>
  - <https://raw.githubusercontent.com/marton78/pffft/master/include/pffft/pffft.h>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.simd.hpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/michelerenzullo/libgaussianblur`) · [data/wave10/enrich/raw/github_com_michelerenzullo_libgaussianblur.json](../../../data/wave10/enrich/raw/github_com_michelerenzullo_libgaussianblur.json) (enrichment confidence 0.75)

</details>
