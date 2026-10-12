# FastGaussianBlur

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 template approximating Gaussian blur with repeated box passes and blocked transposes; beats only a naive 2D convolution.

| | |
|---|---|
| **Beats** | author's own naive non-separable 2D Gaussian convolution ((2k+1)^2 taps, k = ceil(2.57 sigma), gaussian_blur in the 2021 fast_gaussian_blur.h at commit 84e5f2d, since removed); no OpenCV or ImageMagick comparison |
| **Claimed result** | No numeric speedup against a named library. README: 'blurs 2000k pixels in \~7ms on all cores of a Ryzen 7 2700X CPU with OpenMP'. The README graph (data/time.png, log-log, 'Average execution time RGB 24 bits images') annotates the template multi-core version at FHD \~7 ms, 4K \~50 ms and 8K \~200 ms and plots the author's own true Gaussian blur (single core and OpenMP) roughly two orders of magnitude slower at every size; the baseline values are only readable off the plot, not stated. |
| **Workload** | README graph of average execution time versus pixel count on a Ryzen 7 2700X comparing box-blur-pass variants of the repo against a 'true Gaussian blur'; README text gives one absolute figure for the template version. |
| **Metric** | latency |
| **Hardware** | Ryzen 7 2700X, all cores with OpenMP |
| **Compiler and flags** | Makefile default target: g++ -O3 -fopenmp -std=c++17 (README does not say which compiler produced the timings) |
| **Adoption** | 128 stars |
| **Last commit** | 2024-08-18 |
| **Links** | [repository](https://github.com/bfraboni/FastGaussianBlur) · [benchmark](https://github.com/bfraboni/FastGaussianBlur) |

## Verdict

The only numbers are the project's own absolute times for 8-bit RGB, 3 passes, all cores of a Ryzen 7 2700X with OpenMP (Makefile: g++ -O3 -fopenmp): about 7 ms for FHD (2 MP), about 50 ms at 4K and about 200 ms at 8K, from a plot last updated 2021-02-09 (commit 84e5f2d). That plot predates the 2023-2024 rewrites (v1.0 to v1.2), the README's own TODO says 'redo timings', and its harness and sigma are not in the repo. The plot's 'true Gaussian blur' baseline, as it existed in the repo's 2021 header (gaussian_blur in fast_gaussian_blur.h, since removed), is a naive non-separable 2D convolution with (2k+1)^2 taps per pixel (k = ceil(2.57 sigma)) and a bounds check per tap, so the roughly 100x gap is against a straw man, not against a separable or library Gaussian such as OpenCV's.

## Use it when

- Medium to large sigma (roughly 5 and up) on 8-bit RGB or RGBA frames where the cost must not grow with radius: UI backdrop blur, bloom, depth-of-field previews, video at FHD to 4K.
- You want one dependency-free header and can accept an approximate Gaussian (box passes, approximate sigma, inexact borders).
- Multi-core CPUs with OpenMP available: every pass is an embarrassingly parallel loop over rows.
- As a readable starting point to fork; michelerenzullo/FastBoxBlur was derived from this code.

## Skip it when

- Small sigma: the README says a separable Gaussian is as fast and more accurate at sigma &lt;= 2, and with 3 passes any sigma below about 0.58 yields zero-radius boxes, so the output equals the input.
- You need a true Gaussian (scale-space features, scientific or medical imaging, golden-image tests): the sigma oscillates around the target and the borders lose signal because no padding is added between passes.
- You already link OpenCV or a SIMD library: nothing in the repo measures this against cv::GaussianBlur, cv::blur or IPP, and the only published baseline is a naive O(sigma^2) 2D convolution.
- More than 4 channels, more than 10 passes, planar or strided layouts, const or in-place input (it needs two full-size scratch-able buffers), or buffers above 2^31-1 elements (all indexing is int).
- Tiny images, or sigma comparable to the image size, with the mirror border: see the edge-case memory bugs under gotchas.

## How it is fast

Sigma is converted to box widths with Kovesi's 'Fast Almost-Gaussian Filtering' formula (sigma_to_box_radius). Each 1D box pass is a sliding running sum (one add, one subtract and one multiply per sample), so the cost is O(1) per pixel whatever the radius. Vertical passes run as horizontal passes over a transposed copy: N row passes, a cache-blocked transpose (flip_block, 256/C-element tiles), N more row passes and a transpose back, so every filter loop walks memory row-major. Rows and tiles are split across cores with OpenMP parallel for; channel count, pass count, border policy and kernel-size regime are template parameters so the inner loops are specialised; integer images accumulate in int (issue #5 measured int about 15% faster than float on a 6000x8000 horizontal pass). There is no explicit SIMD, and the README says an ISPC port did not beat it.

## Compared with alternatives

Pick it when you want a single dependency-free C++ header with four border policies and a cost that stays flat as sigma grows, and an approximate Gaussian is acceptable. libblur has published multithreaded numbers against OpenCV's Gaussian blur, zanazakaryaie/fastGaussianBlur and LibGaussianBlur (FFT) aim at an exact Gaussian, and FastBoxBlur (derived from this code) is the better fit when you want an accurate mirrored box blur with a cv::blur comparison.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at run time; OpenMP is optional (without -fopenmp the pragmas are ignored and it runs on one core). The header has no #include lines of its own, so the includer must first include &lt;algorithm&gt;, &lt;cmath&gt;, &lt;cstdio&gt;, &lt;cstdint&gt;, &lt;cstdlib&gt; and &lt;type_traits&gt; (the demo gets them through &lt;iostream&gt; and the bundled stb_image/stb_image_write). |
| **Minimum toolchain** | C++17 (if constexpr, std::is_integral_v, std::conditional_t); the Makefile builds with g++ -O3 -fopenmp -std=c++17. Clang and MSVC are not documented; issue #9 says OpenMP linking is awkward on WebAssembly, Android and macOS. |
| **Platforms** | any (portable scalar C++, no intrinsics); timings exist only for a Ryzen 7 2700X |
| **Thread safety** | Not documented. There is no global state, so concurrent calls on distinct buffers are safe, but each call opens its own OpenMP parallel regions (one per pass and per transpose), so calling it from several threads at once oversubscribes the cores. |
| **Drop-in for the baseline** | no |

## Gotchas

- Both buffers are overwritten and the pointer variables are swapped: after the call, `out` may point at the memory you passed as `in`. Pass pointer variables, not array names or pointers you must keep. The 8-argument overload defaults to kExtend, while the README demo defaults to mirror.
- Unsupported arguments do not fail: c &gt; 4 or n = 0 or n &gt; 10 only printf a message and return, leaving `out` as the untouched input (the 3-pass path still swaps pointers) or as whatever the buffer held before.
- Edge-case memory bugs in the current code (commit 49f0128, read and checked with a Python port of the index arithmetic): with the mirror border, a box radius of exactly w-1 takes the kMid branch, which reads one element past the row, and past the allocation on the last row of the buffer. The value is added and then subtracted, so integer results are unaffected, but a NaN or Inf in that garbage would poison a float row. Also with the mirror border, a 1-pixel-wide or 1-pixel-tall image divides by zero in remap_index (slength = 0). Issue #3 (2022, before the 2023 rework) reported an access violation at sigma 250.
- Type handling: every integral T accumulates in int (uint32 or int64 data can overflow; negative signed results are truncated toward zero after the +0.5 rounding), and double data accumulates in float. Float running sums drift slightly along long rows.

## Known shortcomings

- Tier D: only its own timings (FHD about 7 ms, 4K about 50 ms, 8K about 200 ms on time.png) against an unpublished in-house true Gaussian with sigma unstated; no incumbent compared.
- Enricher (e101, 2026-10-05): the plot's 'true Gaussian' baseline is the author's own naive non-separable 2D convolution ((2k+1)^2 taps, k = ceil(2.57 sigma); gaussian_blur in the 2021 header at 84e5f2d, since removed), so the roughly 100x gap is against a straw man; data/time.png dates from 2021-02-09, before the v1.0-v1.2 rewrites, and harness and sigma are absent (README TODO 'redo timings'). Current code (49f0128) edge-case bugs, not behind the numbers: mirror border with box radius == w-1 reads one element past the row (past the allocation on the last row); mirror on a 1-px-wide or 1-px-tall image divides by zero in remap_index; unsupported c&gt;4 or n&gt;10 silently no-op; sigma below about 0.58 gives zero-radius boxes (output = input); the header has no #includes. Open PR #12 (AVX2, claims 1.5-2x, CPU unstated) is broken (int16 row sums overflow at radius &gt;= 64, main reads the second-pass buffer, t.sh runs sigma 0) and is not evidence. Tier D stands.

## Caveats and trade-offs

No comparison against OpenCV GaussianBlur, ImageMagick or any library in the README, the ten issues (none mention OpenCV or benchmarks against libraries) or main.cpp. The true Gaussian baseline in the graph is not in the repo and its sigma is not stated; the box-blur method is independent of sigma, so the gap depends on the sigma chosen. main.cpp times a single call with std::chrono::system_clock truncated to whole milliseconds, with no warm-up. README TODO lists 'redo timings', and the README says the method is not well suited to small sigmas (&lt;=2) and is inaccurate near borders and in the exact sigma. Issue #4 reported slightly darker output with uchar arrays due to a non-rounded multiply (round_v added in v1.2). Lead for the orchestrator: the derivative michelerenzullo/FastBoxBlur (box blur only, based on this code) states in its own README about 2x-3x faster than cv::blur on an i7-10750H; that is a different project and not evidence for this one. Last commit 2024-08-18, so stale.

Header-only C++ template (fast_gaussian_blur_template.h), up to 4 channels and 10 box passes, border policies extend, mirror, crop and wrap. Approximation of a Gaussian: inaccurate near borders and for sigma &lt;= 2 per README; modifies the input buffers; no SIMD (README notes an ISPC attempt did not beat it).

## Maintenance

Stale since 2024-08-18 (v1.2), with 3 open issues; MIT, a single 865-line header that is easy to vendor. The open AVX2 PR #12 (April 2026, unreviewed, claiming 1.5x to 2x on an unstated CPU) should not be merged as is: its int16 row sums overflow for box radius 64 and up on 8-bit data, its 3-pass loop leaves main.cpp reading the second-pass buffer, and its t.sh test runs at sigma 0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README states only the project's own absolute times (\~7 ms for 2000k pixels; the data/time.png plot annotates FHD \~7 ms, 4K \~50 ms, 8K \~200 ms); the comparison is against the author's unpublished true Gaussian blur with unstated sigma, whose values exist only as points on a log-log plot, and no OpenCV or other incumbent is measured.
- **Verifier notes:** Tier D kept per the orchestrator: own absolute times plus a plot against an in-house, unpublished true Gaussian; no incumbent. 128 stars (&lt;1k), kept under the keep-and-document rule rather than rejected as not notable.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `baseline`
- **Shortcomings recorded by:** none (self-plot against own naive convolution)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/data/time.png>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/main.cpp>
  - <https://github.com/bfraboni/FastGaussianBlur>
  - <https://github.com/bfraboni/FastGaussianBlur/commits/main>
  - <https://github.com/bfraboni/FastGaussianBlur/issues?q=is%3Aissue>
  - <https://github.com/bfraboni/FastGaussianBlur/issues/5>
  - <https://github.com/bfraboni/FastGaussianBlur/issues/9>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/README.md>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/fast_gaussian_blur_template.h>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/HEAD/data/time.pdf>
  - <https://github.com/bfraboni/FastGaussianBlur>
  - <https://github.com/bfraboni/FastGaussianBlur/tree/main/data>
  - <https://github.com/bfraboni/FastGaussianBlur/commits/main>
  - <https://github.com/bfraboni/FastGaussianBlur/commits/main/data/time.png>
  - <https://github.com/bfraboni/FastGaussianBlur/commit/183b015>
  - <https://github.com/bfraboni/FastGaussianBlur/tree/84e5f2d/>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/fast_gaussian_blur.h>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/fast_gaussian_blur_template.h>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/blur_uchar_rgb.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/blur_float.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/blur_float_rgb.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/blur_int.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/blur_int_rgb.cpp>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/Makefile>
  - <https://raw.githubusercontent.com/bfraboni/FastGaussianBlur/84e5f2db75af3da8b9068c7f551e88feec67d5fb/README.md>
  - <https://github.com/bfraboni/FastGaussianBlur/issues?q=is%3Aissue>
  - <https://github.com/bfraboni/FastGaussianBlur/issues/3>
  - <https://github.com/bfraboni/FastGaussianBlur/issues/5>
  - <https://github.com/bfraboni/FastGaussianBlur/issues/9>
  - <https://github.com/bfraboni/FastGaussianBlur/pulls?q=is%3Apr>
  - <https://github.com/bfraboni/FastGaussianBlur/pull/12>
  - <https://github.com/bfraboni/FastGaussianBlur/pull/12/files>
  - <https://github.com/bfraboni/FastGaussianBlur/pull/12/commits>
  - <https://raw.githubusercontent.com/Toiabzahoor/FastGaussianBlur/main/t.sh>
  - <https://raw.githubusercontent.com/Toiabzahoor/FastGaussianBlur/main/main.cpp>
  - <https://raw.githubusercontent.com/Toiabzahoor/FastGaussianBlur/main/Makefile>
  - <https://raw.githubusercontent.com/Toiabzahoor/FastGaussianBlur/main/avx2_blur.h>
  - <https://raw.githubusercontent.com/michelerenzullo/FastBoxBlur/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bfraboni/fastgaussianblur`) · [data/wave10/enrich/raw/github_com_bfraboni_fastgaussianblur.json](../../../data/wave10/enrich/raw/github_com_bfraboni_fastgaussianblur.json) (enrichment confidence 0.85)

</details>
