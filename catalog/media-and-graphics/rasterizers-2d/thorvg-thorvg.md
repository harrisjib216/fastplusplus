# ThorVG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> MIT C++ SVG/Lottie vector engine; its CPU renderer averaged 2.9x Skia raster fps on 5k-shape scenes (4 threads vs 1).

| | |
|---|---|
| **Beats** | Skia (CPU raster backend, Skia v148) |
| **Claimed result** | README: 'an average of \~2.9x faster' than 'a widely-used vector graphics engine' (Skia v148 in the test conditions), CPU backend, 2560x1440, 5k primitives. Chart table (fps, ThorVG vs Skia): Rects 76.0 vs 17.2 (4.4x), Rotated Rects 36.0 vs 10.1 (3.6x), Stroke 55.7 vs 17.2 (3.2x), Rects+Stroke 41.8 vs 10.5 (4.0x), Rotated Rects+Stroke 25.0 vs 4.5 (5.6x), Circles 38.5 vs 10.4 (3.7x), Images (PNG) 6.4 vs 6.0 (1.1x), Rotated Images 4.4 vs 4.4 (1.0x), Linear Gradient 9.0 vs 8.5 (1.1x), Radial Gradient 6.9 vs 6.0 (1.2x). The 2.9x is the arithmetic mean of the ten per-test ratios (2.89, derived from page data); image and gradient cases are roughly at parity. |
| **Workload** | thorvg.benchmark CPU backend at 2560x1440: 5,000 retained shapes per frame (rects with alpha 240-255, rotated rects, strokes, circles, PNG images with bilinear filtering, linear/radial gradients), per-frame translate/scale (and rotation in rotation mode), 120 warmup + 1000 measured frames, frame time includes SDL_UpdateWindowSurface for both engines. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Pro (macOS 26) per README test conditions |
| **Compiler and flags** | Compiler not stated (macOS build, presumably Apple Clang). thorvg.benchmark README: harness built with CMake -DCMAKE_BUILD_TYPE=Release; ThorVG built with meson using project defaults (buildtype=debugoptimized, optimization=3); Skia installed from vcpkg (arm64-osx triplet), its build flags not stated. |
| **Adoption** | 1.9k stars; used by Canva (Lottie), SEGGER, Lottie Creator per README |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/thorvg/thorvg) · [benchmark](https://github.com/thorvg/thorvg) |

## Verdict

First-party chart from ThorVG's own public harness (thorvg/thorvg.benchmark): 5,000 shapes per frame at 2560x1440 on an Apple M2 Pro (macOS 26), ThorVG v1.1 with 4 worker threads against Skia v148 from vcpkg drawing single-threaded into a raster surface, frame time including clear and SDL_UpdateWindowSurface; per-test ratios run from 1.0x (rotated images) to 5.6x (rotated rects plus stroke), and the headline 2.9x is their arithmetic mean. No compiler or Skia build flags are named, and no independent measurement exists.

## Use it when

- Lottie playback or SVG icon/UI rendering on the CPU in a C++ app on embedded, mobile or desktop targets, where a core of about 170KB and no mandatory dependencies matter (README lists LVGL, an Espressif ESP-IDF component, Godot, Tizen and Canva iOS as users).
- Frames with thousands of retained geometric shapes that move every frame and spare cores to run the worker pool: the README chart gives 3.6x on rotated rectangles and 3.7x on circles over single-threaded Skia v148 raster on an Apple M2 Pro, both anti-aliased on both sides, with ThorVG on 4 worker threads.
- Mostly static UIs where only small regions change, since SmartRender partial rendering repaints only dirty regions (the benchmark turns it off, so this gain is not in the chart).
- Projects that want one scene-graph API across CPU, OpenGL/ES, WebGL and WebGPU backends, including WebAssembly builds.

## Skip it when

- Image- or gradient-heavy content: the chart shows parity with Skia for PNG images (6.4 vs 6.0 fps), rotated images (4.4 vs 4.4) and linear/radial gradients (1.1x and 1.2x), so switching buys little there.
- Single-core or core-limited deployments: the published 2.9x mean pits ThorVG with 4 worker threads (and OpenMP if linked) against single-threaded Skia raster, and no single-threaded ThorVG figure is published.
- When you need exact anti-aliased edges on axis-aligned rectangles at fractional coordinates or on fills under thick opaque strokes: the fast track snaps such rectangles to whole pixels, and a TODO in _axisAlignedRect admits it hurts smooth rectangle movement.
- When you want the fastest CPU rasterizer: Blend2D and Vello CPU have independent thesis measurements against Skia, ThorVG has none, and in discussion #1815 (December 2023) the maintainer said accurate data including Blend2D was still needed.
- Full SVG 1.1/2 documents (only the SVG Tiny subset; no SVG animation, interactivity or multimedia), PDF output, or Skia's breadth in text shaping and colour management.

## How it is fast

Per-shape preparation (outline transform, stroking and scan conversion into RLE coverage spans, using a rasterizer derived from FreeType's anti-aliased 'gray' rasterizer) runs as tasks on a worker pool sized by tvg::Initializer::init(n), while the calling thread composites the spans with NEON or AVX2 span blenders. Retained shapes are re-prepared only when their path, transform or colour flags change. Two quality shortcuts save work: axis-aligned unclipped rectangles take a 'fast track' that skips scan conversion and fills a pixel-rounded box without anti-aliasing, and fills under an opaque stroke at least 2 px wide are scan-converted without anti-aliasing. Optional OpenMP row-parallel loops (image scaling, premultiply) and dirty-region partial rendering (SmartRender) add further gains in some scenes.

## Compared with alternatives

Pick ThorVG over Blend2D, Vello CPU or AGG when you need SVG and Lottie loading, text, a retained scene graph and optional GPU backends in one small C++14 library for embedded or mobile targets; pick Blend2D when raw single-threaded CPU fill speed is the goal (independent thesis data, about 4x Skia), and LunaSVG when you only rasterize static SVG files.

## Integration

| | |
|---|---|
| **Form** | shared lib by default via meson (static with -Ddefault_library=static); packaged in vcpkg, Conan, Homebrew, Debian, Fedora, MSYS2 and others |
| **Dependencies** | none required; optional OpenMP for the CPU engine (meson option extra=openmp is on by default), libpng/libjpeg-turbo/libwebp for external image loaders (built-in static loaders exist), OpenGL 3.3/ES 3.0 or wgpu-native v29 for the GPU backends |
| **Minimum toolchain** | C++14 (meson default cpp_std=c++14), meson and ninja; GCC/Clang builds use -fno-exceptions -fno-rtti |
| **Platforms** | Windows, macOS, Linux, Android, iOS, web (WASM), Tizen and RTOS/ESP32 per README; CPU SIMD is AVX2 on x86/x86-64 and NEON on ARM/AArch64 (meson simd option, on by default), with a scalar C fallback |
| **Thread safety** | Worker count is fixed by the first successful tvg::Initializer::init(n) (0 means main thread only); update() and draw() may run asynchronously and sync() must follow draw(). Concurrent use of one canvas from several threads is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Axis-aligned, unclipped rectangles are filled as pixel-rounded boxes without anti-aliasing (tvgSwShape.cpp _axisAlignedRect, tvgSwUtil.cpp utilBBox, tvgSwRaster.cpp _rasterRect), and fills under an opaque stroke of 2 px or more are scan-converted aliased (SwShapeTask::antialiasing). Output therefore differs from Skia or Blend2D on such shapes, and slowly moving rectangles step in whole pixels.
- SwCanvas::gen() with the default option turns on SmartRender partial rendering, which has an open 'cpu: partial rendering bug' (#4751) and, per the README, can add overhead when nearly everything changes each frame; pass EngineOption::None for full redraws, as the benchmark does. EngineOption::Aliased (turn AA off everywhere) is marked experimental.
- With OpenMP built in (the default meson option), the first SwRenderer calls omp_set_num_threads(threads), which also changes the default team size for the host program's own OpenMP regions on that thread.
- The scan converter is derived from FreeType code and tvgSwRle.cpp carries the FreeType Project License text, which asks for a FreeType credit in your documentation in addition to the MIT notice.

## Known shortcomings

- README chart (2.9x mean of 10 per-test ratios vs Skia v148, Apple M2 Pro) runs ThorVG with 4 worker threads (default since commit 2f87860, 2026-08-31, the day the chart was updated) against single-threaded Skia raster, which the README does not say; compiler unnamed. Image and gradient cases are only about 1.0-1.2x. Maintainer discussion #1815: no Blend2D comparison exists.
- Beyond the 4-thread versus 1-thread asymmetry, the compared work differs: every Skia paint has setAntiAlias(true) while ThorVG fills axis-aligned rectangles as pixel-rounded boxes without anti-aliasing (_axisAlignedRect, utilBBox, _rasterRect) and skips AA on fills under opaque strokes of 2 px or more (SwShapeTask::antialiasing), so the 4.4x Rects, 4.0x Rects+Stroke and 5.6x Rotated Rects+Stroke rows render less work; the like-for-like anti-aliased rows are Rotated Rects 3.6x and Circles 3.7x, still on 4 threads, and the default meson extra=openmp also row-parallelises the scaled-image loops. tvgSwRle.cpp carries FreeType License text (credit needed beyond MIT); open bug #4751 (CPU partial rendering); --help says threads default to the maximum while the code says 4.

## Caveats and trade-offs

First-party benchmark (thorvg/thorvg.benchmark, MIT, 6 stars). Thread asymmetry: the harness initialises ThorVG with opts.threads worker threads, default 4 since commit 2f87860 'thorvg: fine-tuned options' (2026-08-31; before that the default was hardware_concurrency), while Skia renders through a single-threaded raster surface (SkSurfaces::WrapPixels). The README chart was last updated the same day (2026-08-31) and the README does not state the thread count, so the \~2.9x compares multi-threaded ThorVG with single-threaded Skia; the gains are largest in geometry-heavy tests and near 1x for images and gradients. Compiler not named; Skia's vcpkg build flags unverified. The headline sentence does not name Skia (only the test conditions do). The stroke workload was replaced on 2026-09-21 (designer stroked paths) and the harness says new stroke results are not comparable with earlier runs, so the chart's Stroke row predates the current code. Per-test numbers exist only as an image.

Smaller feature set than Skia (core binary about 170KB per README); focused on SVG and Lottie, with software, OpenGL and WebGPU backends. Per the VGCPU-Benchmark README its CPU rasterizer uses a sum-then-saturate coverage model (not exact union), so self-overlapping paths can differ from Skia and Cairo. The gain is large for rect, stroke and circle workloads but only 1.0x to 1.2x for images and gradients.

## Maintenance

Actively maintained (last commit 2026-10-03, release v1.1.2 on 18 September 2026, about 1.9k stars, dev version 1.2.0 in meson.build) under MIT with FreeType-licensed portions, so it is copyable and widely packaged.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party: the README chart (thorvg.site readme/example_performance.png) gives ThorVG vs Skia v148 CPU fps per test and the harness is public (thorvg/thorvg.benchmark src/thorvg/\*_thorvg_sdl.cpp, src/skia/\*_skia_sdl.cpp, src/common/benchmark_runner.hpp) with Apple M2 Pro stated, but no compiler is named and flags are only implied by build instructions (CMake Release harness, ThorVG meson defaults, Skia from vcpkg), so not A; no independent measurement, so not B.
- **Verifier notes:** Numbers match the README chart exactly; 2.9x is the mean of per-test ratios. Main issue is fairness: ThorVG runs with 4 worker threads against single-threaded Skia raster in the benchmark harness, and the README omits this; consider a shortcoming. Metadata confirmed: MIT, 1.9k stars, not archived, last commit 2026-10-03.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/thorvg/thorvg.site/main/readme/example_performance.png>
  - <https://raw.githubusercontent.com/thorvg/thorvg.site/main/readme/example_stress.png>
  - <https://github.com/thorvg/thorvg.site/commits/main/readme/example_performance.png>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/LICENSE>
  - <https://github.com/thorvg/thorvg>
  - <https://github.com/thorvg/thorvg/commits/main>
  - <https://github.com/thorvg/thorvg/commits/main/README.md>
  - <https://github.com/thorvg/thorvg.benchmark>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/CMakeLists.txt>
  - <https://github.com/thorvg/thorvg.benchmark/tree/main/src>
  - <https://github.com/thorvg/thorvg.benchmark/tree/main/src/thorvg>
  - <https://github.com/thorvg/thorvg.benchmark/tree/main/src/skia>
  - <https://github.com/thorvg/thorvg.benchmark/tree/main/src/common>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/tvg_sdl_example.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/rectbench_thorvg_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/skia_sdl_example.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/rectbench_skia_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/benchmark_runner.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/cli_parser.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/rect_generator.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/tools/run_all.py>
  - <https://github.com/thorvg/thorvg.benchmark/commits/main>
  - <https://github.com/thorvg/thorvg.benchmark/commits/main/src/common/cli_parser.hpp>
  - <https://github.com/thorvg/thorvg.benchmark/commit/2f87860507e4c2fc65a6186fb9b402d8a6ee381f>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/meson.build>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/inc/thorvg.h>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/tvgTaskScheduler.cpp>
  - <https://github.com/thorvg/thorvg/tree/main/src/renderer>
  - <https://github.com/thorvg/thorvg/tree/main/src/renderer/cpu_engine>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/meson.build>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwRenderer.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwShape.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwUtil.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwCommon.h>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwRaster.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwRasterNeon.h>
  - <https://raw.githubusercontent.com/thorvg/thorvg/HEAD/src/renderer/cpu_engine/tvgSwRle.cpp>
  - <https://github.com/thorvg/thorvg/releases>
  - <https://github.com/thorvg/thorvg/releases/latest>
  - <https://github.com/thorvg/thorvg/issues?q=is%3Aissue%20state%3Aopen%20label%3Abug>
  - <https://github.com/orgs/thorvg/discussions/1815>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/benchmark_runner.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/cli_parser.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/rect_generator.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/common/transform.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/tvg_sdl_example.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/rectbench_thorvg_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/strokerectbench_thorvg_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/circlebench_thorvg_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/thorvg/imagebench_thorvg_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/skia_sdl_example.hpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/rectbench_skia_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/strokerectbench_skia_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/circlebench_skia_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/src/skia/imagebench_skia_sdl.cpp>
  - <https://raw.githubusercontent.com/thorvg/thorvg.benchmark/HEAD/tools/run_all.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/thorvg/thorvg`) · [data/wave10/enrich/raw/github_com_thorvg_thorvg.json](../../../data/wave10/enrich/raw/github_com_thorvg_thorvg.json) (enrichment confidence 0.8)

</details>
