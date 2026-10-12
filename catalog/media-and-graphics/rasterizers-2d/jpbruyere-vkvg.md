# vkvg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Cairo-style 2D vector library in C on Vulkan; the author's chart shows it beating Cairo's GL ES3 backend on lines, circles and stars.

| | |
|---|---|
| **Beats** | Cairo (GL ES3 backend) and Skia (Vulkan backend) |
| **Claimed result** | Chart only. Per vgperf src/main.c the bars are median wall-clock seconds per iteration (gettimeofday, lower is better; each iteration draws opt.count shapes, default 100, on a default 512x512 surface; the options used for the chart are not stated). Approximate readings from the PNG: lines stroke vkvg \~0.00013, cairo es3 \~0.0031, skia \~0.0004; rectangles \~0.00026, \~0.00026, \~0.00022; circles \~0.00065, \~0.0035, \~0.00016; stars \~0.00058, \~0.0019, \~0.00062. So vkvg is about 24x, 5x and 3x faster than Cairo GL ES3 on lines, circles and stars and ties on rectangles; against Skia Vulkan it is about 3x faster on lines, roughly ties on stars, is slightly slower on rectangles and about 4x slower on circles (derived from page data). |
| **Workload** | vgperf, a caskbench-style C harness, timing four tests (lines stroke, rectangles, circles, stars) with vkvg (Vulkan), Cairo (GL ES3/EGL surface) and Skia (Vulkan backend via a patched experimental C API); each timed iteration draws a batch of random shapes and, when on-screen presentation is enabled, flushes and presents the surface. |
| **Metric** | other |
| **Compiler and flags** | Skia built with gn args is_official_build=true is_component_build=true skia_use_vulkan=true (vgperf README); vgperf's own CMakeLists.txt defaults to a Debug build when no build type is given (harness driver only); vkvg and Cairo builds, compilers and flags not stated. |
| **Adoption** | 819 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/jpbruyere/vkvg) · [benchmark](https://github.com/jpbruyere/vgperf) |

## Verdict

The only evidence is the author's vgperf chart from 2022-01. It shows median wall-clock seconds per iteration of 100 random shapes on a 512x512 window for vkvg, Cairo's GL ES3 backend and a patched Skia Vulkan build, with GPU, CPU, versions and options unstated. Derived readings: vkvg about 24x faster than Cairo ES3 on lines, 5x on circles and 3x on stars, tied on rectangles; against Skia about 3x faster on lines, tied on stars, slightly slower on rectangles and about 4x slower on circles. With the harness defaults the anti-aliasing is unequal (Cairo anti-aliases, vkvg and Skia do not), Skia's rectangle test uses different placement, and the harness no longer builds against current vkvg.

## Use it when

- A Vulkan application on Linux or Windows (engine, tool UI, HUD, plotting overlay) that needs Cairo-style 2D drawing rendered into a VkImage on its own VkDevice and queue, with no CPU raster and upload step.
- Porting existing Cairo drawing code to the GPU: call names and semantics (paths, line caps and joins, dashes, gradients, save/restore) mostly map one to one.
- Frames with many thin strokes or simple polygons, batched in one context per frame. Lines were vkvg's largest margin in the author's chart: about 0.00013 s versus about 0.0031 s for Cairo GL ES3 per 100 random 1 px lines.
- You can accept MSAA anti-aliasing (2x to 8x samples) instead of exact-coverage anti-aliasing.

## Skip it when

- You need exact-coverage anti-aliasing or output that matches Cairo pixel for pixel. A 1-sample device (the default) draws aliased edges, and higher quality costs MSAA memory and bandwidth.
- macOS or iOS through MoltenVK: vkvg enables the logicOp device feature (vkvg_device.c), and device creation fails on an Apple M2 with VK_ERROR_FEATURE_NOT_PRESENT (issue #141, open since 2023-07).
- You need Cairo's full compositing model: only CLEAR, SOURCE, OVER and DIFFERENCE are enabled, the other operators are commented out of vkvg.h, and 'Operators' is still unchecked in the README to-do list.
- Production use where robustness matters. The README calls the project alpha, and open bugs include a save/restore segfault (#165), test crashes and validation errors (#121), first dashes with an offset not drawn (#50), and premultiplied-alpha problems on image load and save (#115, #156) and on unclipped paint (#157).
- Circle- or arc-heavy scenes, or targets without a Vulkan 1.1 GPU. In the author's own chart Skia's Vulkan backend was about 4x faster on circles, because vkvg tessellates every arc on the CPU. A CPU fallback exists only as an open idea (#149).

## How it is fast

Path geometry is tessellated on the CPU and appended to per-context vertex and index caches, which are drawn as batched indexed draws in one command buffer per flush, so many shapes share a pipeline and a submit. Strokes become triangle geometry with joins and caps, and curves are flattened with AGG's recursive Bezier subdivision (README credit). Non-zero fills are triangulated with the bundled GLU tessellator (VKVG_USE_GLUTESS, on by default) or ear clipping. Even-odd fills and clips use the stencil buffer: the path is drawn into the stencil, then a quad over the path bounds is covered. Anti-aliasing comes only from hardware MSAA chosen at device creation, and destroyed contexts are cached per thread so that recreating one is cheap.

## Compared with alternatives

Pick vkvg over Blend2D, AGG or tiny-skia when the frame is already on a Vulkan GPU and you want Cairo-style calls that render straight into a VkImage. Pick vger for Apple-only Metal UIs, and the Rive Renderer or TGFX for a more mature GPU renderer with more backends. For exact anti-aliased output or CPU-only targets, Blend2D is the better-measured choice in this category.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake, BUILD_SHARED_LIBS); AUR and MPR packages exist |
| **Dependencies** | Vulkan 1.1 loader and driver; git submodules vkh (jpbruyere/vkhelpers), glutess and vkvg-svg; bundled vk_mem_alloc; optional FontConfig, FreeType (stb_truetype otherwise) and HarfBuzz; GLFW for tests; glslc and xxd only to rebuild the shaders (precompiled SPIR-V headers are in the tree) |
| **Minimum toolchain** | C11 (C_STANDARD 11 required), CMake 3.16+, Vulkan 1.1+ |
| **Platforms** | Linux and Windows with a Vulkan 1.1 GPU driver. CI builds on Windows, Ubuntu and macOS, and CMake has an Android branch, but MoltenVK on Apple M2 fails at device creation (logicOp, #141). |
| **Thread safety** | Partial. A device created with threadAware=true guards the queue and font cache with mutexes, and contexts are cached per thread. The README says only 'Context should be thread safe, extensive tests required'. Use one context per thread. |
| **Drop-in for the baseline** | partial: the drawing API mirrors Cairo with a vkvg_ prefix and float arguments, but device and surface setup is Vulkan-specific, only 4 operators exist and anti-aliasing is MSAA-only, so call sites and setup must be ported |

## Gotchas

- Anti-aliasing is fixed when the device is created. vkvg.h says a 1-sample device is non-antialiased, so set info.samples above 1 for smooth edges. With deferredResolve the multisampled image is resolved only on vkvg_surface_get_vk_image or an explicit resolve call.
- vkvg_flush submits and then blocks the CPU on the context's fence until the GPU finishes (_flush_cmd_buff then _wait_ctx_flush_end). A full vertex buffer also forces a submit-and-wait in the middle of a path (_poly_fill). Flush once per frame, not per shape. Issue #163 (2026-06) reports long CPU waits in this function.
- The MSVC branch of the stock CMakeLists adds '/O2 /TC /W0 /Od' to non-Debug builds. cl lets the later /Od override /O2, so Windows builds are probably unoptimized unless you edit the flags. Unix Release builds use CMake's defaults.
- Clone with --recursive (forks need the submodule fallback URLs given in the README). The older entry points vkvg_device_create_from_vk and vkvg_device_create_from_vk_multisample are gone from include/vkvg.h (only vkvg_device_create(info) remains), so older code, including the vgperf harness, must be ported. With VKVG_USE_GLUTESS=OFF, ear clipping puts a stack VLA sized by the path's point count, so very large paths risk stack overflow.

## Known shortcomings

- Chart dated 2022-01-19 (vgperf main.c, median seconds per iteration); the Cairo baseline is Cairo's GL ES3 backend, not its image backend; the stars test against Skia is a near tie, not a win. Ratios derived from chart readings.
- The vgperf harness is not like-for-like at its defaults: with -a vkvg runs at 1 sample (non-antialiased per vkvg.h) and Skia has sk_paint_set_antialias(false) while Cairo uses CAIRO_ANTIALIAS_DEFAULT (antialiased), and the chart's options are unstated, so the 24x lines and 5x circles against Cairo are probably aliased against anti-aliased; the Skia rectangles are placed in [0, 0.2w) against [0, w) for the others; the chart omits Cairo's default image (CPU) backend. The harness calls vkvg_device_create_from_vk\*, which no longer exists in include/vkvg.h, so the chart is not reproducible against current vkvg. logicOp is required (MoltenVK fails, #141); the MSVC Release flags are '/O2 /TC /W0 /Od' (probably unoptimised); only 4 compositing operators; open segfault #165; vkvg_flush blocks on a fence (#163).

## Caveats and trade-offs

First-party chart with no axis label, unit, GPU or CPU model, run count or Cairo/vkvg versions; the unit (median seconds per iteration) is inferred from vgperf src/main.c. The chart was last updated on 2022-01-19 (vgperf commit 'update perf chart with latest vkvg'), so it predates more than four years of vkvg changes. vgperf (5 stars, 22 commits, MIT) has no numeric results, only the chart. Cairo is measured through its GL ES3 backend, not its default image (CPU) backend; Skia was built from a patched experimental C API branch. Only 4 simple drawing tests. Mixed result against Skia: clearly slower on circles, slightly slower on rectangles.

Needs Vulkan; GPU-only; Cairo-like C API; alpha-stage per README; fill (stencil even-odd and non-zero), stroke, gradients, dashes and a font system with caching are implemented.

## Maintenance

Actively developed by a single maintainer (639 commits, last 2026-10-01, version 0.3.0, self-described alpha, 35 open issues). MIT-licensed and copyable, but its only performance evidence is a 2022 chart made against an older API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party chart (vgperf.png, embedded in both READMEs) produced by the author's public harness (vgperf src/main.c, src/vkvg, src/cairo, src/skia). No GPU or CPU model, vkvg or Cairo build flags, versions or harness options are stated, and no numeric results file exists, so C.
- **Verifier notes:** Chart readings in the record are accurate apart from stars versus Skia, which is a near tie rather than a loss; ratios now labelled as derived. Harness code was read: vkvg's timed present path calls vkvg_flush, which in current vkvg source waits for the flush fence, while vkDeviceWaitIdle is commented out. Metadata checked: MIT, 819 stars, last commit 2026-10-01, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/README.md>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/vgperf.png>
  - <https://github.com/jpbruyere/vgperf>
  - <https://github.com/jpbruyere/vgperf/commits/master>
  - <https://github.com/jpbruyere/vgperf/tree/master/src>
  - <https://github.com/jpbruyere/vgperf/tree/master/src/vkvg>
  - <https://github.com/jpbruyere/vgperf/tree/master/src/cairo>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/main.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/vgperf.h>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/vkvg/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/vkvg/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/cairo/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/cairo/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/skia/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/src/skia/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/master/src/vkvg_context.c>
  - <https://github.com/jpbruyere/vkvg>
  - <https://github.com/jpbruyere/vkvg/commits/master>
- **Sources the enricher read:**
  - <https://github.com/jpbruyere/vkvg>
  - <https://github.com/jpbruyere/vkvg/commits/master>
  - <https://github.com/jpbruyere/vkvg/issues>
  - <https://github.com/jpbruyere/vkvg/issues?page=2&q=is%3Aissue+is%3Aopen>
  - <https://github.com/jpbruyere/vkvg/issues/163>
  - <https://github.com/jpbruyere/vkvg/issues/141>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/include/vkvg.h>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/src/vkvg_device.c>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/src/vkvg_device_internal.c>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/src/vkvg_context.c>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/src/vkvg_context_internal.c>
  - <https://raw.githubusercontent.com/jpbruyere/vkvg/HEAD/.github/workflows/cmake.yml>
  - <https://raw.githubusercontent.com/jpbruyere/vkhelpers/HEAD/src/vkh_presenter.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/README.md>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/vgperf.h>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/vkvg/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/vkvg/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/cairo/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/cairo/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/skia/common.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/HEAD/src/skia/shapes.c>
  - <https://raw.githubusercontent.com/jpbruyere/vgperf/master/vgperf.png>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jpbruyere/vkvg`) · [data/wave10/enrich/raw/github_com_jpbruyere_vkvg.json](../../../data/wave10/enrich/raw/github_com_jpbruyere_vkvg.json) (enrichment confidence 0.75)

</details>
