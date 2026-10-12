# KFAST

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header AVX2, multithreaded FAST-9 corner detector matching Rosten's output; 5.1x faster than single-threaded OpenCV cv::FAST (2016).

| | |
|---|---|
| **Beats** | Edward Rosten's reference FAST-9 C code (fast9_detect / fast9_detect_nonmax in the repo's Rosten folder) and OpenCV's cv::FAST, both timed in main.cpp |
| **Claimed result** | README: 'outperforms the next-fastest implementation by 60% single-threaded or 500% multi-threaded (!) while exactly matching its output'. results.jpg is a console screenshot of the main.cpp driver (not a bar chart): KFAST 646.711 us, OpenCV 3299.35 us ('5.102x slower than KFAST'), Dr. Rosten 13750.4 us ('21.26x slower than KFAST'), all 8361 keypoints agreeing. With the driver's default KFAST_multithread = true this is multi-threaded KFAST against single-threaded OpenCV and Rosten code. No single-threaded measurement is shown for the 60% figure; the main.cpp header instead says '40-60% single-threaded or 500% multi-threaded' over 'the reference implementation'. |
| **Workload** | FAST-9 corner detection with non-maximal suppression (threshold 50) on one grayscale image (test.jpg); 150 warm-ups then the mean of 1000 timed calls per implementation, with a keypoint-equality check across all three. results.jpg is the screenshot of the output, not a test image. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: g++ (version not stated) with -Ofast -std=gnu++17 -march=native -mavx2 -mfma -flto -funroll-all-loops -fpeel-loops -ftracer -ftree-vectorize -fomit-frame-pointer; Rosten's C is built with gcc and the same flags; OpenCV is the system library (version and build flags not stated). The screenshot looks like a Windows console, so the measured build may have been MSVC; this is not stated. |
| **Adoption** | 85 stars |
| **Last commit** | 2021-03-23 |
| **Links** | [repository](https://github.com/komrad36/KFAST) · [benchmark](https://github.com/komrad36/KFAST) |

## Verdict

The only first-party run (results.jpg, a 2016 console screenshot of main.cpp; one test image, threshold 50, non-max on, mean of 1000 calls after 150 warm-ups) shows multi-threaded KFAST at 646.711 us per call against single-threaded cv::FAST at 3299.35 us (5.1x) and Rosten's scalar fast9_detect_nonmax at 13750.4 us (21.3x), all 8361 keypoints identical; CPU, compiler and OpenCV version are not stated. A third-party run on an unspecified Mac, posted in the PR #4 thread in July 2019 with that PR's branch, gave 717.865 us against 2918.54 us (4.07x) and 13099.9 us (18.25x).

## Use it when

- FAST-9 corner detection on 8-bit grayscale frames on x86-64 with AVX2, where you control the input allocation (ORB-style front ends, visual odometry, feature tracking).
- Large images and spare cores: the default multithreaded mode is where the 5x figure comes from.
- When output must be identical to Rosten's reference FAST-9 with non-maximal suppression; the driver checks equality against both Rosten's code and cv::FAST.
- Projects that want FAST without linking OpenCV: KFAST.h has no dependencies beyond the C++ standard library and immintrin.h.

## Skip it when

- Input buffers you cannot pad: tail columns are read with full 32-byte loads, so the last rows read up to about 30 bytes past the end of the image (issue #3, Valgrind 'Invalid read of size 32'); the maintainer says this crashes if the over-read reaches unmapped memory and recommends over-allocating by at least 32 bytes. Master is unfixed.
- Non-AVX2 targets (ARM/NEON, older x86): there is no fallback, whereas current OpenCV cv::FAST has universal-intrinsic SIMD and a runtime-dispatched AVX2 path and runs everywhere.
- Small images, per-frame latency budgets or already-threaded pipelines: multithreaded mode launches fresh std::async threads on every call; use the single-threaded template there, for which no measurement is published.
- Other FAST variants (FAST-10, 11 or 12, which the bundled Rosten folder does provide) or ROI masks: only the 9-of-16 test is implemented.
- Anything needing maintenance: last code change January 2019, and PR #4 (memcpy tail that removes the over-read) has been open since July 2019.

## How it is fast

Each AVX2 iteration tests 32 candidate pixels: saturating add and subtract of the threshold, an XOR with 0x80 so signed byte compares act as unsigned, and the classic four-point (circle points 1, 5, 9, 13) rejection test whose movemask lets the loop skip 32 or 16 pixels at once. Surviving lanes run a branch-free 24-step consecutive-run count over the circle plus 8 wrap-around points with byte max accumulators. Corner scores use 16-bit min/max over all 16 nine-pixel arcs and a PHMINPOSUW horizontal reduction; non-max suppression works on a rolling three-row score buffer. The multithreaded mode splits the image into row bands with overlapping halo rows, one std::async thread per hardware thread (capped at rows/16).

## Compared with alternatives

No other FAST detector is catalogued; the listed siblings (bilinear_filter_simd, SIMD_TriangleAABB, the author's Leftpack and FastArrayOps) are unrelated SIMD kernels. Against the real incumbent, cv::FAST, pick KFAST only when you have AVX2, can pad input buffers, and want multithreaded FAST without OpenCV.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for KFAST.h; the test driver main.cpp needs OpenCV (core, features2d, highgui, imgcodecs) and pthreads, and uses legacy OpenCV C-API constants (CV_LOAD_IMAGE_GRAYSCALE, CV_WINDOW_NORMAL) |
| **Minimum toolchain** | C++11 per README (Makefile builds with g++ -std=gnu++17 -march=native); MSVC also stated as supported; GCC/Clang need -mavx2 plus BMI1 (_tzcnt_u32, _blsr_u32); KFAST.h calls memset without including &lt;cstring&gt; |
| **Platforms** | x86-64 with AVX2 and BMI1; Linux (g++) and Windows (MSVC) per README; no runtime dispatch or scalar fallback |
| **Thread safety** | not documented; by inspection there is no global state, each call allocates its own scratch buffer with _mm_malloc and writes only the caller's vector, so concurrent calls on different outputs are safe |
| **Drop-in for the baseline** | partial — same keypoints as cv::FAST(img, kps, thresh, true) with the 9/16 pattern and as Rosten's fast9_detect_nonmax, but a different signature and Keypoint struct, and the input buffer must be padded by 32 bytes |

## Gotchas

- Out-of-bounds read: for most image widths the last processCols call on the last processed row loads 32 bytes from the bottom image row starting a few columns before its end; results are masked so output is unaffected, but ASan/Valgrind flag it and an image ending at a page boundary can segfault (issue #3, closed in April 2019 with the advice to over-allocate, no code change).
- The headline is multi-threaded against single-threaded: main.cpp defaults to KFAST_multithread = true while cv::FAST and Rosten's code run on one thread. The README's single-threaded '60%' and main.cpp's '40-60% over the reference implementation' have no published run; 'reference' cannot mean Rosten's code, because in the same screenshot OpenCV is already 4.2x faster than Rosten (derived from page data). A KFAST.h comment ('2000 -&gt; 2600 microseconds without forced inlining') hints at about 2 ms per call on the test image, roughly 1.6x faster than OpenCV's 3.3 ms (derived), but it does not say which threading mode.
- The only first-party numbers (results.jpg) were captured on 2016-09-12, before the October 2016 'horizontal AVX shuffle' performance commit and the January 2019 PR #2 fix, against an OpenCV build of unknown version; OpenCV's cv::FAST has since gained a runtime-dispatched AVX2 path (fast.avx2.cpp, split out of fast.cpp in October 2017), so the gap to a current OpenCV is unmeasured.
- Before PR #2 (January 2019) the tail mask could evaluate 1 &lt;&lt; 32 (undefined behaviour), which the maintainer said misses corners in the last 32 columns for affected widths; in current master the shift amount is at most 31 for any width of 6 columns or more, and narrower images give a negative shift (also undefined).

## Known shortcomings

- results.jpg is a console screenshot (5.102x over OpenCV, 21.26x over Rosten) of multi-threaded KFAST against single-threaded baselines, no CPU, and the "60% single-threaded" figure is unmeasured; PR #2 (2019) fixed an undefined shift that dropped corners in the last 32 columns, so the screenshot predates a correctness fix.
- Library bug: tail loads read up to about 30 bytes past the image end (issue #3, Valgrind; the maintainer says pad by 32 bytes; master unfixed, memcpy fix PR #4 open since 2019); output is masked so the numbers are unaffected. Harness: the 5.1x is multi-threaded KFAST against single-threaded OpenCV and Rosten; the single-threaded 60% was never shown, and '40-60% over the reference' cannot mean Rosten since OpenCV is already 4.2x faster than Rosten in the same screenshot. OpenCV has had an AVX2 FAST path since October 2017 (fast.avx2.cpp), so the gap to current OpenCV is unmeasured. A third-party Mac rerun in the PR #4 thread gave 717.865 vs 2918.54 us (4.07x).

## Caveats and trade-offs

The headline 5.1x ('500%') compares multi-threaded KFAST with single-threaded cv::FAST and single-threaded scalar Rosten code; the single-threaded 60% claim has no published measurement. One image, one threshold, no CPU model, no compiler version, OpenCV version unknown. The screenshot was added on Sep 12, 2016, before the Oct 2016 'horizontal AVX shuffle' performance commit and before PR #2 (Jan 2019), which fixed an off-by-one in the main column loop (j &lt; cols - 35 instead of cols - 34) that let last_cols_mask = (1 &lt;&lt; 32) - 1 overflow; the maintainer said this undefined shift fails to catch any corners in the last 32 columns for affected image widths. The measured image passed the driver's equality check, so the shown run was not affected. Requires AVX2 with no fallback. Last code changes 2016 to January 2019; the 2021 commit only adds the MIT LICENSE; the Rosten folder is BSD-3-Clause. It is a computer-vision kernel rather than a general SIMD library.

Single header KFAST.h with no dependencies; needs AVX2; multithreaded; output claimed bit-identical to the reference. The test driver needs OpenCV for the comparison and image loading. Bundles Rosten's BSD-licensed reference code.

## Maintenance

Abandoned since January 2019 (the 2021 commit only adds the MIT LICENSE; the bundled Rosten folder is BSD-3-Clause; PR #4 unmerged), but a single MIT header that is easy to vendor if you pad input buffers by 32 bytes or apply PR #4's memcpy tail; evidence stays first-party and mixes thread counts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: main.cpp times KFAST, OpenCV cv::FAST and Rosten's fast9 on one image and the Makefile gives g++ flags, but no CPU model or compiler version is stated, and the only shown run (results.jpg screenshot, Sep 2016) predates a 2019 correctness fix in the column loop.
- **Verifier notes:** Keep at C. The screenshot gives the real numbers: 5.102x over OpenCV and 21.26x over Rosten, both for multi-threaded KFAST against single-threaded baselines. No like-for-like single-thread figure is published. A 2019 merged fix corrected undefined-shift behaviour that dropped corners in the last 32 columns for some widths; the timed image was unaffected. One WebSearch found no independent measurement.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `baseline_in_list`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/KFAST>
  - <https://github.com/komrad36/KFAST/commits>
  - <https://github.com/komrad36/KFAST/commit/15e4536>
  - <https://github.com/komrad36/KFAST/pull/2>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/KFAST.h>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/results.jpg>
- **Sources the enricher read:**
  - <https://github.com/komrad36/KFAST>
  - <https://github.com/komrad36/KFAST/commits>
  - <https://github.com/komrad36/KFAST/tree/master/Rosten>
  - <https://github.com/komrad36/KFAST/issues?q=is%3Aissue>
  - <https://github.com/komrad36/KFAST/issues/3>
  - <https://github.com/komrad36/KFAST/pulls>
  - <https://github.com/komrad36/KFAST/pull/2>
  - <https://github.com/komrad36/KFAST/pull/4>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/KFAST.h>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/komrad36/KFAST/HEAD/results.jpg>
  - <https://raw.githubusercontent.com/kudanowen/KFAST/patch-1/KFAST.h>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/features2d/src/fast.cpp>
  - <https://github.com/opencv/opencv/commits/4.x/modules/features2d/src/fast.avx2.cpp>
  - <https://github.com/opencv/opencv/commit/2eb61a4>
  - <https://github.com/komrad36?tab=repositories>
  - WebSearch: komrad36 KFAST AVX2 FAST corner detector speed compared OpenCV (no independent benchmark found)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/komrad36/kfast`) · [data/wave13/enrich/raw/github_com_komrad36_kfast.json](../../../data/wave13/enrich/raw/github_com_komrad36_kfast.json) (enrichment confidence 0.7)

</details>
