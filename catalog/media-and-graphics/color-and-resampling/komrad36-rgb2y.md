# RGB2Y

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only AVX2 BGR-to-grayscale for 8-bit images; README claims roughly 3x faster than OpenCV cv::cvtColor.

| | |
|---|---|
| **Beats** | OpenCV cv::cvtColor (CV_BGR2GRAY) |
| **Claimed result** | README (dating from the February 2017 kernel, never re-measured after the 2018 Q15 rewrite): 'roughly 3x faster than OpenCV with AVX2, 2x with SSE only'; the SSE path no longer exists. The only public run (issue #1, Debug build) has OpenCV 3.4.3 at 2592.71 us versus RGB2Y 15139.5 us. |
| **Workload** | RGB (BGR) image to 8-bit grayscale conversion with OpenCV's default weights; main.cpp runs 50 warmups and 100 timed runs against cv::cvtColor and prints microseconds. |
| **Metric** | throughput |
| **Compiler and flags** | Repo Makefile: g++ -Ofast -std=gnu++17 -fomit-frame-pointer -mavx2 -march=native -mfma -flto -funroll-all-loops -fpeel-loops -ftracer -ftree-vectorize (no compiler version; no published run). |
| **Adoption** | 92 stars |
| **Last commit** | 2021-03-23 |
| **Links** | [repository](https://github.com/komrad36/RGB2Y) · [benchmark](https://github.com/komrad36/RGB2Y) |

## Verdict

The only claim is the README's 'roughly 3x faster than OpenCV with AVX2, or 2x with SSE only', with no CPU, timings or OpenCV version; that sentence was already in the README at commit e67dffa (Feb 2017), when the kernel used 6-bit weights with truncation (up to 3 grey levels off OpenCV, 57.4% of colours different), and it was not re-measured after the 30 Sep 2018 rewrite to the current Q15 kernel, which also dropped the SSE path. main.cpp times both sides (50 warm-ups, 100 runs, RGB2Y multithreaded, OpenCV with its own parallel_for_) on the repo's test.jpg, but publishes no output; the only posted run (issue #1, OpenCV 3.4.3, a Debug build) had RGB2Y at 15139.5 us against OpenCV's 2592.71 us.

## Use it when

- BGR8 frames in OpenCV layout converted to gray on x86-64 with AVX2, where a 1-level difference from OpenCV on some colours is acceptable and an OpenCV dependency is not wanted.
- Large frames processed multithreaded on machines with 16 or fewer hardware threads, where thread start-up is amortised and the row-split bug cannot trigger.
- Equal-weight channel averaging (weighted=false), which is exact for all inputs.
- As a compact example of pshufb-based deinterleaving of 3-channel pixels with AVX2.

## Skip it when

- When you need OpenCV's exact output: an exhaustive check of all 16,777,216 BGR triples against OpenCV 4.x's 15-bit BGR2GRAY formula gives 33.2% differing by one grey level (16.4% lower, 16.8% higher), never by more.
- RGB-ordered, 4-channel, 16-bit or float input: weights are global constants in the header (swap B_WEIGHT and R_WEIGHT for RGB), and only 3-byte pixels are handled.
- CPUs without AVX2 or non-x86 targets: the SSE path the README advertises was removed on 30 Sep 2018 (commit 6a822b7, open issue #5), and NO_AVX_PLEASE now does nothing.
- Unpadded input buffers: the final 10-pixel block of the last row loads 31 bytes and reads 1 to 28 bytes past the end, depending on width mod 10.
- Multithreaded calls on machines with 24 or more hardware threads: the row split overruns the image for some heights (see gotchas).

## How it is fast

Each step converts 10 pixels (30 bytes): two overlapping 16-byte loads widened to 16 bits, one _mm256_mulhrs_epi16 against a repeating B,G,R Q15 weight vector, packus back to bytes, then three pshufb masks gather each pixel's three products and saturating byte adds sum them, so no 32-bit dot products are needed. Rows are split across up to min(height/16, hardware_concurrency()) std::async tasks. The unweighted path sums channels in 16 bits and divides by 3 with mulhrs by 10923, which equals round(sum/3) for every possible sum.

## Compared with alternatives

CompV (RGB24 to gray 449 ms vs OpenCV 3086 ms) and DeltaCV publish measured BGR/RGB-to-gray results against OpenCV, and H264Sharp measures cvtColor-style conversion by thread count; choose RGB2Y only when a single dependency-free AVX2 header for BGR8 to gray matters more than evidence, bit-exactness or maintenance.

## Integration

| | |
|---|---|
| **Form** | header-only (RGB2Y.h, all functions are templates) |
| **Dependencies** | none for RGB2Y.h beyond the C++ standard library and &lt;immintrin.h&gt; (it uses std::vector and std::thread without including &lt;vector&gt; or &lt;thread&gt;); the main.cpp demo needs OpenCV 3.x for the CV_BGR2GRAY constant |
| **Minimum toolchain** | Written for MSVC: it uses __forceinline, which g++ and clang++ on Linux do not predefine (checked with g++ 13.3 macro dump), and an unannotated switch fallthrough that -Wextra flags (-Wimplicit-fallthrough since GCC 7) under the Makefile's -Werror; Makefile otherwise asks for g++ -std=gnu++17 -mavx2 -march=native -Ofast |
| **Platforms** | x86-64 with AVX2 (also SSE4.1 _mm_extract_epi8); no SSE-only, NEON or scalar fast path |
| **Thread safety** | Reentrant: no shared mutable state (per-call vector of futures; the weight vector is a per-translation-unit static const) |
| **Drop-in for the baseline** | partial: raw-pointer API for 3-channel 8-bit BGR only, stride in pixels rather than bytes, packed output, and results differ from cv::cvtColor by one grey level on about a third of colours |

## Gotchas

- Out-of-bounds rows in the multithreaded split: thread_stride = ceil(height / threads) and threads-1 full chunks are launched before the remainder, and the final call always processes at least one row, so whenever (threads-1)\*thread_stride &gt; height the tasks read past the input and write past the output. Because threads is capped at height/16 this needs 18 or more hardware threads: a simulation finds 49 affected heights up to 4096 on 24 threads (for example 385 rows, 7 rows out of bounds), 225 on 32 threads (520 rows) and 1713 on 64 threads (721 rows: 28 out of bounds; 1000 rows: 38).
- The input stride is in pixels (row i starts at data + 3\*i\*stride) while the output is written packed at out + i\*width; RGB2Y_ref instead writes out[i\*stride + j], so with padded rows the fast path and the reference disagree on output layout. Divide cv::Mat::step by 3, and only if it is a multiple of 3.
- main.cpp's 'N pixels disagree' line compares RGB2Y with its own RGB2Y_ref, which reproduces the per-term rounding exactly (0 mismatches over all colours), not with OpenCV's output.
- Each multithreaded call starts new tasks with std::async(std::launch::async); libstdc++ and libc++ create a thread per task (MSVC pools them), so small images pay thread start-up on every call.

## Known shortcomings

- README states a ratio with no measurement behind it (no result table, machine or baseline version); Makefile builds g++ -Ofast -march=native. The SSE claim has no code behind it (NO_AVX_PLEASE is unused). Per-term rounding can differ from cv::cvtColor by 1 grey level and is checked only against its own reference. The last block reads at least 1 byte past the end of the input buffer (out-of-bounds read).
- Retiered C to D (retier-15): the README's 3x AVX2 / 2x SSE line dates from the February 2017 kernel (6-bit weights, 57.4% of colours differing from OpenCV) and was never re-measured after the 2018 Q15 rewrite; the SSE path was removed (issue #5); the only public run (issue #1, Debug build) shows RGB2Y slower than OpenCV. Exhaustive check against OpenCV 4.x: 33.2% of outputs off by 1; the multithreaded row split overruns the destination at 18 or more threads; tail over-read of 1-28 bytes; the g++ -Werror Makefile breaks on __forceinline and an unannotated fallthrough; the function is really BGR2Y (issue #4).

## Caveats and trade-offs

Claim is a README ratio with no CPU or measured timings; the harness (main.cpp: 50 warmups, 100 timed runs, both sides multithreaded) is public but its output is not published. Output is not bit-identical to the baseline: RGB2Y rounds each weighted channel term separately (_mm256_mulhrs_epi16 in Q15, then saturating adds), while OpenCV's 8-bit BGR2GRAY rounds the weighted sum once, so some pixels can differ by one grey level; main.cpp checks RGB2Y only against its own scalar reference (RGB2Y_ref, which uses the same per-term rounding), never against cv::cvtColor's output. Each 10-pixel block loads 31 bytes, so the final block of the last row reads at least 1 byte past the end of an unpadded input buffer (main.cpp's synthetic-image path pads by 128 bytes). AVX2 only in the current code; uses the MSVC keyword __forceinline (GCC/Clang portability not checked). The harness uses the OpenCV 3-era CV_BGR2GRAY constant, so it needs changes to build against OpenCV 4, and modern OpenCV may be closer. Code last updated 29 Sep 2018; last commit 23 Mar 2021 only added the MIT LICENSE file. [retier] No measured number for the current code. Exhaustive check of all 16,777,216 BGR triples against OpenCV 4.x: 33.2% of outputs differ by 1 (max 1). The multithreaded row split overruns the destination at 18 or more threads (385 rows on 24 threads, 721 or 1000 on 64); the tail over-reads 1-28 bytes; stride is in pixels with packed output while the reference writes strided; __forceinline and an unannotated fallthrough break the g++ -Werror Makefile; the function is really BGR2Y (issue #4).

Header-only (RGB2Y.h), AVX2 or SSE only, no NEON; single operation (RGB to gray) with equal or OpenCV-default weights; the author says SSE is about 50% slower than AVX2.

## Maintenance

Abandoned: the kernel last changed on 30 Sep 2018 and the only later commit (23 Mar 2021) added the MIT license; four open issues (missing SSE path, BGR naming, an unexplained 'A bug?' report with an error image) have no replies. Vendorable after fixing the row split and padding the input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README ratio ('roughly 3x faster than OpenCV's implementation with AVX2') with a public harness (main.cpp, timing RGB2Y against cv::cvtColor) and a Makefile giving g++ and flags, but no CPU model, no compiler version and no published run output. First-party claim without measured results is C.
- **Retiered** C to D: Lowered C to D: the README's '3x AVX2 / 2x SSE' line dates from the February 2017 kernel e67dffa (6-bit weights, up to 3 levels off OpenCV, 57.4% of colours differing) and was never re-measured after the 30 September 2018 Q15 rewrite; the SSE path was removed (issue #5), so the 2x figure has no code behind it, and the only public run (issue #1, a Debug build) shows OpenCV 3.4.3 at 2592.71 us against RGB2Y at 15139.5 us. No measured number describes the current code.
- **Verifier notes:** README and repo description match the record. Metadata on github.com: MIT, 92 stars, 23 forks, not archived or forked, last commit 2021-03-23 (Create LICENSE), so abandoned is correct. The per-term rounding difference from OpenCV and the 1+ byte input over-read are worth carrying into the entry's shortcomings.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/komrad36/RGB2Y>
  - <https://github.com/komrad36/RGB2Y/commits>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/RGB2Y.h>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/komrad36/RGB2Y>
  - <https://github.com/komrad36/RGB2Y/commits/master>
  - <https://github.com/komrad36/RGB2Y/commit/6a822b7>
  - <https://github.com/komrad36/RGB2Y/commit/838d21e>
  - <https://github.com/komrad36/RGB2Y/commit/e8b4019>
  - <https://github.com/komrad36/RGB2Y/issues?q=is%3Aissue>
  - <https://github.com/komrad36/RGB2Y/issues/1>
  - <https://github.com/komrad36/RGB2Y/issues/2>
  - <https://github.com/komrad36/RGB2Y/issues/3>
  - <https://github.com/komrad36/RGB2Y/issues/4>
  - <https://github.com/komrad36/RGB2Y/issues/5>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/RGB2Y.h>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/705f112/README.md>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/e67dffa/README.md>
  - <https://raw.githubusercontent.com/komrad36/RGB2Y/e67dffa/RGB2Y.h>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color_rgb.simd.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color.simd_helpers.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/core/include/opencv2/core/cvdef.h>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4/modules/core/include/opencv2/core/cvdef.h>
  - <https://github.com/komrad36?tab=repositories>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/komrad36/rgb2y`) · [data/wave10/enrich/raw/github_com_komrad36_rgb2y.json](../../../data/wave10/enrich/raw/github_com_komrad36_rgb2y.json) (enrichment confidence 0.75)

</details>
