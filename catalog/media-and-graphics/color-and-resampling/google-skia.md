# Skia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's 2D graphics library; its 2016 convolution scaler (Skia 53) resized 4.2x to 9.7x faster than single-threaded ImageMagick 6.8.

| | |
|---|---|
| **Beats** | ImageMagick 6.8.9-9 |
| **Claimed result** | Xeon E5-2666 v3 (c4.large), 2560x1600 to 320x200: Lanczos 18.1 ms for Skia vs 127.67 ms for ImageMagick (7.1x) and bilinear 6.41 vs 46.15 ms (7.2x). To 2048x1280, Lanczos 39.8 vs 276.76 ms (7.0x). Core i5-4258U, Lanczos to 320x200: 24.8 vs 156.8 ms (6.3x). Across all 12 size and filter cases Skia is 6.4x to 9.5x faster on c4.large and 4.2x to 9.7x faster on the macbook. All ratios are derived from page data. |
| **Workload** | pillow-perf resample-4k-rgb, single core: a 2560x1600 source resized to 26x16, 320x200, 2048x1280 and 5478x3424 with bilinear (triangle), bicubic (Mitchell in Skia, Catmull-Rom in ImageMagick) and Lanczos-3 filters. Skia 53 'SSE2' was timed with a nanobench BitmapScaleBench.cpp gist calling SkBitmapScaler::Resize on a white-filled N32 bitmap. ImageMagick 6.8.9-9 was timed through Wand (Python) with MAGICK_THREAD_LIMIT=1 on a resized color_circle.png in RGB truecolor. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2666 v3 @ 2.90GHz on Amazon EC2 c4.large, Ubuntu 16.04.1 (macbook.json: Intel Core i5-4258U @ 2.40GHz) |
| **Compiler and flags** | Not stated. The only label is 'Skia 53 SSE2' in docs/src/data/index.js; Skia was timed with nanobench and no build flags are given. |
| **Adoption** | 11k stars (GitHub mirror of skia.googlesource.com); used in Chrome and Android |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/google/skia) · [benchmark](https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c4.large.json) |

## Verdict

pillow-perf (python-pillow) timed Skia 53's SSE2 SkBitmapScaler in a C++ nanobench loop on a white 2560x1600 N32 bitmap against ImageMagick 6.8.9-9 through Python Wand with MAGICK_THREAD_LIMIT=1 on an RGB image, on a Xeon E5-2666 v3 (c4.large, Ubuntu 16.04.1) and a Core i5-4258U; Skia was 6.4x to 9.5x and 4.2x to 9.7x faster across 12 size/filter cases (derived from page data), with no compiler or flags recorded. The harnesses are not symmetric: the Skia loop reuses a destination preallocated outside the timed loop, while each ImageMagick run includes a clone, a fresh result image and Python call overhead.

## Use it when

- You already link Skia (Chrome-, Android- or Flutter-style apps, PDF/vector renderers) and need decent-quality thumbnails without adding another imaging library.
- Moderate downscales or upscales of 8-bit RGBA/BGRA images where bilinear or Mitchell/Catmull-Rom cubic quality is enough.
- Workloads that already draw images to a canvas or GPU surface, where scaling is fused into the draw instead of being a separate pass.
- Large-ratio downscales on the CPU using mipmapped linear sampling or SkImage::asyncRescaleAndReadPixels with RescaleMode::kRepeatedLinear / kRepeatedCubic.

## Skip it when

- You want the speed measured here: the SkBitmapScaler code that produced the 4.2x to 9.7x numbers no longer exists in Skia, and no benchmark of current scalePixels against ImageMagick was found.
- You need Lanczos or other scale-adaptive convolution filters: current SkSamplingOptions offers only nearest, linear (plus mipmaps) and cubic B/C, and cubic cannot be combined with mipmaps.
- You only need a resize kernel: in the same pillow-perf data Pillow-SIMD 4.3 AVX2 needs 0.32x to 0.54x of Skia 53's time (Lanczos 320x200: 6.23 ms vs 18.1 ms on c4.large), so dedicated resizers are faster and much smaller to integrate.
- 16-bit, float or high-precision resizing pipelines (the measured scaler worked on 8-bit pixels with 14-bit fixed-point weights).
- Projects that cannot take a GN/Ninja build with Python-driven dependency sync, Clang and C++20.

## How it is fast

The measured Skia 53 scaler is a two-pass separable convolution over 8-bit BGRA pixels with precomputed per-output-pixel filter taps stored as int16 fixed point (kShiftBits = 14), with SSE2 (x86) and NEON kernels for the horizontal, four-rows-at-once horizontal and vertical passes; that matches the 'Skia 53 SSE2' label in pillow-perf. Current Skia instead resamples by drawing through its raster pipeline: bilinear (2x2 taps) or cubic B/C (fixed 4x4 taps, bicubic_n3x..p3x stages) per output pixel, optional mipmaps for linear filtering, plus a dedicated bicubic_clamp_8888 fast stage.

## Compared with alternatives

Pick Skia when it is already in the binary and you also need drawing or GPU compositing; for a standalone fast resizer, Pillow-SIMD's resample code (faster than Skia 53 in the same dataset), libvips or OpenCV are better choices, and stb-image-resize-opt is the lightweight single-header option.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (GN + Ninja; is_component_build for shared) |
| **Dependencies** | Python 3 for tools/git-sync-deps and bin/fetch-gn; GN and Ninja; third-party codecs and fonts (libpng, libjpeg-turbo, libwebp, FreeType, ICU, etc.) are optional per skia_use_\* flags; Bazel for some Rust third-party code; CMake 3.30+ only for Dawn |
| **Minimum toolchain** | C++20 (site/docs/user/build.md); Clang strongly preferred, since software-rasterizer and color-conversion paths are documented to be 'dramatically' slower with GCC or MSVC |
| **Platforms** | Linux, macOS, Windows, Android, iOS, ChromeOS; x86-64 and arm64 CPU paths, plus GPU backends |
| **Thread safety** | SkBitmap is not thread-safe (each thread needs its own SkBitmap, pixel memory may be shared); SkPixelRef is thread-safe; one surface/canvas per thread |
| **Drop-in for the baseline** | partial — a library call (SkPixmap::scalePixels) rather than ImageMagick's CLI/MagickWand API, with no codec-to-codec pipeline, no Lanczos and no 16-bit quantum depth |

## Gotchas

- The measured API (SkBitmapScaler, SkConvolver, SkResizeFilter) was removed on 2017-07-20; nanobench numbers for Skia 53 do not describe any Skia release after that.
- Current cubic sampling uses a fixed 4x4 footprint per output pixel, so very large downscales with cubic alias unless you downscale in steps (asyncRescaleAndReadPixels kRepeatedCubic) or use mipmapped linear sampling.
- Skia has no stable API: RELEASE_NOTES.md lists removals and signature changes almost every milestone, so pin a milestone branch (chrome/mNNN).
- Chromium still carries the old convolution resizer (skia::ImageOperations::Resize in skia/ext, Lanczos-3/box/Hamming with SSE2, NEON and LSX), but it lives in the Chromium tree, not in Skia.

## Known shortcomings

- Skia 53 resize at B on the pillow-perf data (c4.large.json, Xeon E5-2666 v3; macbook.json, i5-4258U; rows added by the Pillow-SIMD author on 2016-11-02 via a nanobench BitmapScaleBench.cpp gist, white N32 2560x1600 source) against ImageMagick 6.8.9-9 through Wand with MAGICK_THREAD_LIMIT=1: 6.4-9.5x and 4.2-9.7x (derived), same sizes and filter families (bicubic Mitchell vs Catmull-Rom). The Skia section is commented out of the pillow-perf docs/index.html, SkBitmapScaler.h no longer exists on Skia main, and no flags are recorded; 2016 numbers.
- Stale evidence (retier-11 corrects the caveats): the gist times SkBitmapScaler from Skia m53, deleted on 2017-07-20; current scalePixels is raster-pipeline linear or 4x4 cubic with no Lanczos, so the numbers describe no Skia since 2017. The harness preallocates Skia's destination outside the timed loop on a white source while ImageMagick pays clone, new-image and Python Wand overhead per call; Pillow-SIMD 4.3 AVX2 needed 0.32-0.54x of Skia's time on the same data. Skia now requires C++20 and strongly prefers Clang.

## Caveats and trade-offs

This is old evidence: Skia 53 (2016) against ImageMagick 6.8.9-9. The SkBitmapScaler API the gist measures is no longer at src/core/SkBitmapScaler.h on Skia main (404), so current Skia resampling differs from what was timed. The Skia section and the Skia library description are commented out of the published docs/index.html; only the data files keep the rows, and only c4.large.json and macbook.json have Skia results. The commented-out prose says ImageMagick is 'about 20 times slower than Skia', but the data show 4.2x to 9.7x (derived from page data). Skia was timed with a separate C++ nanobench harness on a constant white 4-channel bitmap, while ImageMagick ran through Python Wand on a 3-channel image. Both are single-threaded convolution resamplers with matching filter families, except that bicubic is Mitchell in Skia and Catmull-Rom in ImageMagick. The suite is maintained by the Pillow-SIMD authors, who report Pillow-SIMD faster than Skia (4.3 AVX2 Lanczos 320x200 6.23 ms and 3.4 AVX2 7.38 ms vs Skia 18.1 ms on c4.large). [retier] Stale: the timed SkBitmapScaler (Skia m53, 2016, SSE2-only fixed-point convolver) was deleted from Skia on 2017-07-20; current Skia resampling is raster-pipeline linear or 4x4 cubic with no Lanczos, so these numbers describe no Skia built since 2017. Baseline is ImageMagick 6.8.9-9. Harness asymmetry favours Skia: destination preallocated outside the timed loop and a white N32 source, while ImageMagick pays clone, new image and Python Wand overhead per call. Pillow-SIMD 4.3 AVX2 needed 0.32-0.54x of Skia's time on the same data. Skia now needs C++20 and strongly prefers Clang.

Graphics library, not an image-processing toolbox; heavy build; the resize path measured is one SkBitmap scale call among many APIs.

## Maintenance

Very actively developed (last commit 2026-10-03; RELEASE_NOTES.md already has a Milestone 156 section) and BSD-3-Clause, so copyable, but the benchmarked scaler was deleted in 2017 and today's equivalent is an unbenchmarked raster-pipeline path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** pillow-perf (python-pillow org) data files c4.large.json (Xeon E5-2666 v3, Ubuntu 16.04.1) and macbook.json (Core i5-4258U, Ubuntu 16.04.2) carry skia-53 and imagemagick-6.8 (6.8.9-9) rows for the same resample-4k-rgb cases. Homm (the Pillow-SIMD author, independent of both Skia and ImageMagick) added the Skia rows on 2016-11-02. Both harnesses are public: the nanobench gist BitmapScaleBench.cpp for Skia and testsuite/cases/wand_scale.py for ImageMagick. No compiler or flags are given, so it is B, not A.
- **Verifier notes:** Every cited number is in this project's rows of c4.large.json and macbook.json (cross-checked with c4.large.txt for ImageMagick). Metadata is confirmed: BSD-3-Clause, 11.0k stars, mirror of skia.googlesource.com, last commit 2026-10-03. fawick/speedtest-resize (opened) has no Skia rows.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c4.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/macbook.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c4.large.txt>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/index.js>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/amd.a10.7800.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c3.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c5.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/m5a.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/macbook.2019.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_scale.py>
  - <https://github.com/python-pillow/pillow-perf>
  - <https://github.com/python-pillow/pillow-perf/tree/main/testsuite>
  - <https://github.com/python-pillow/pillow-perf/tree/main/testsuite/cases>
  - <https://github.com/python-pillow/pillow-perf/tree/main/docs/src/data>
  - <https://github.com/python-pillow/pillow-perf/commits/main/docs/src/data/c4.large.json>
  - <https://gist.github.com/homm/6e048cb0dad135b6db63b924458730e8>
  - <https://raw.githubusercontent.com/google/skia/main/src/core/SkBitmapScaler.h>
  - <https://github.com/google/skia>
  - <https://github.com/google/skia/commits/main>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c4.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/macbook.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/index.js>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/base.py>
  - <https://gist.github.com/homm/6e048cb0dad135b6db63b924458730e8>
  - <https://raw.githubusercontent.com/google/skia/main/README>
  - <https://raw.githubusercontent.com/google/skia/main/include/core/SkPixmap.h>
  - <https://raw.githubusercontent.com/google/skia/main/include/core/SkSamplingOptions.h>
  - <https://raw.githubusercontent.com/google/skia/main/include/core/SkImage.h>
  - <https://raw.githubusercontent.com/google/skia/main/include/core/SkBitmap.h>
  - <https://raw.githubusercontent.com/google/skia/main/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/google/skia/main/site/docs/user/build.md>
  - <https://raw.githubusercontent.com/google/skia/main/BUILD.gn>
  - <https://raw.githubusercontent.com/google/skia/main/gn/skia.gni>
  - <https://raw.githubusercontent.com/google/skia/main/src/core/SkPixmap.cpp>
  - <https://raw.githubusercontent.com/google/skia/main/src/core/SkPixmapDraw.cpp>
  - <https://raw.githubusercontent.com/google/skia/main/src/shaders/SkImageShader.cpp>
  - <https://raw.githubusercontent.com/google/skia/main/src/core/SkBitmapScaler.cpp>
  - <https://raw.githubusercontent.com/google/skia/main/src/core/SkConvolver.h>
  - <https://github.com/google/skia/commits/main/src/core/SkBitmapScaler.cpp>
  - <https://raw.githubusercontent.com/google/skia/chrome/m53/src/core/SkBitmapScaler.h>
  - <https://raw.githubusercontent.com/google/skia/chrome/m53/src/core/SkBitmapScaler.cpp>
  - <https://raw.githubusercontent.com/google/skia/chrome/m53/src/core/SkConvolver.h>
  - <https://raw.githubusercontent.com/google/skia/chrome/m53/src/core/SkConvolver.cpp>
  - <https://raw.githubusercontent.com/google/skia/chrome/m53/src/opts/opts_check_x86.cpp>
  - <https://raw.githubusercontent.com/chromium/chromium/main/skia/ext/image_operations.h>
  - <https://raw.githubusercontent.com/chromium/chromium/main/skia/ext/convolver.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/google/skia`) · [data/wave10/enrich/raw/github_com_google_skia.json](../../../data/wave10/enrich/raw/github_com_google_skia.json) (enrichment confidence 0.75)

</details>
