# Blend2D

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Zlib` · 🟢 active

> Zlib-licensed C/C++ CPU 2D vector renderer with JIT-compiled pipelines; about 4x Skia's and 7x Cairo's raster throughput.

| | |
|---|---|
| **Beats** | Skia (CPU pipeline) and Cairo; also AGG, JUCE, Qt6, CoreGraphics |
| **Claimed result** | Third-party thesis (ETH Zurich, Vello CPU author): Blend2D is 'the clear winner', needing the shortest time 'for nearly all configurations' versus the C++ and Rust renderers. Fill-Solid-RectU 256x256 single-threaded: Blend2D 10.8 ms vs Skia 50.3 ms (about 4.7x faster, derived from page data) and Cairo 21.9 ms (about 2.0x faster, derived from page data) per 1000 renders. Across the thesis data set (vello_chart data/arm/2025-09-24.json, M1 Pro), Blend2D ST is faster than Skia in 1032 of 1044 test x size cells (geometric mean about 4.1x) and faster than Cairo in 863 of 870 cells (geometric mean about 7.2x) (derived from page data). Blend2D 8-thread mode reaches 4.7x over its own single-thread time at 256x256 in Fill-Solid-RectA. |
| **Workload** | Time for 1000 render calls of a single shape (rectangles, polygons, curves, strokes; solid/gradient/image paints) at sizes 8x8 to 256x256 on a 512x600 pixmap, single-threaded and 8-thread. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (8 cores: 6 performance + 2 efficiency, 16 GB, macOS) for the thesis figures; an Intel Core i9-14900K (Windows) run in vello_chart data/x86 has no Skia or JUCE column |
| **Compiler and flags** | Not stated in the thesis. The harness README builds with CMake -DCMAKE_BUILD_TYPE=Release and Blend2D's CMakeLists adds -O2 for release builds; the compiler is not named, Skia comes from vcpkg's unofficial-skia package with unstated version and flags, and Cairo is found via pkg-config (version 1.18.4 per the result JSON). |
| **Adoption** | 2.0k stars |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/blend2d/blend2d) · [benchmark](https://github.com/LaurenzV/master-thesis/blob/main/main.pdf) |

## Verdict

Laurenz Stampfl's ETH Zurich master's thesis (Vello CPU author, advised by Raph Levien) ran Blend2D 0.12.0, Skia (vcpkg unofficial-skia, version unstated) and Cairo 1.18.4 in Blend2D's own bl_bench harness on an Apple M1 Pro. Rendering 1000 unaligned 256x256 solid rectangles took 10.8 ms for Blend2D single-threaded, 50.3 ms for Skia and 21.9 ms for Cairo (about 4.7x and 2.0x). Across the published result JSON it was faster than Skia in 1032 of 1044 cells and Cairo in 863 of 870 (derived from page data). The compiler and the Skia/Cairo build flags are not stated, and Blend2D used its CMake release flags (-O2).

## Use it when

- Server-side or headless CPU rendering in C or C++ (charts, maps, thumbnails, PDF-to-image style rasterisation) where Skia's or Cairo's raster backend is the bottleneck. In the thesis data it was faster than Skia in 1032 of 1044 test cells (geometric mean about 4.1x) and faster than Cairo in 863 of 870 (about 7.2x) on an Apple M1 Pro (derived from page data).
- Large shapes with gradient or pattern paints where you can spare cores. With 8 threads the geometric-mean speedup over its own single-threaded mode at 256x256 was 3.95x on the M1 Pro and 4.65x on an i9-14900K (derived from page data).
- Replacing AGG, JUCE's software renderer or tiny-skia in a CPU-only stack. Single-threaded it was faster than AGG in 513 of 522 cells (about 3.3x), JUCE 8.0.8 in 838 of 870 (about 2.4x) and tiny-skia in 870 of 870 (about 7.5x) on the same M1 Pro run (derived from page data).
- x86-64 or AArch64 targets where runtime code generation is allowed, so the JIT pipelines that produced these numbers are actually used.

## Skip it when

- You need GPU rendering or GPU compositing for an interactive UI. Blend2D rasterises every frame on the CPU, and open issue #264 asks exactly this question with no answer yet. Look at Skia's GPU backends, ThorVG or vkvg.
- Mostly tiny, curve-heavy paths. At 8x8-32x32 on the Fish, Butterfly and Dragon shapes, Vello CPU single-threaded was up to 2.9x faster in the 2026-06-08 M1 Pro run, and Skia beat it by up to 1.13x on 8x8 Butterfly and Dragon (derived from page data).
- Workloads dominated by large axis-aligned solid rectangle strokes. Cairo was faster on StrokeRectA Solid at 32x32-256x256, by up to 1.35x on the M1 Pro and 3.0x on the i9-14900K (derived from page data).
- Targets without the JIT (32-bit ARM, RISC-V and other non-x86/AArch64 targets, BLEND2D_NO_JIT builds, sandboxes that forbid executable memory). These fall back to the reference pipelines, and none of the published numbers covers that configuration.
- Projects that need PDF, SVG or print output surfaces, SVG/Lottie parsing, or a frozen API. The source tree contains only the raster (CPU image) rendering context, and the library is still pre-1.0 (0.21.3) with recent renames.

## How it is fast

Fill and composition pipelines are generated at runtime with AsmJit, so each combination of pixel format, composition operator, fill type and fetch type gets specialised SIMD machine code for the host CPU. The analytic rasterizer is AGG-derived but renders strictly top to bottom so it can work in bands. It uses a dense cell buffer plus a per-scanline bit vector in which one bit covers N cells, which lets the compositor skip empty pixels in large steps. The thesis also points to fixed-point math where possible and a dedicated filler for unaligned rectangles. Multi-threaded mode queues commands and gives each worker horizontal bands, with the calling thread acting as one of the workers.

## Compared with alternatives

Pick Blend2D over Vello CPU, AGG, JUCE, tiny-skia or raqote when you want the fastest single-threaded CPU rasteriser in C or C++. In the same harness it beat all of them in most cells, and Vello CPU wins mainly on tiny curved shapes and in some 4-8 thread configurations. Pick ThorVG instead if you need SVG or Lottie loading, or Vello CPU if you want a Rust-native library.

## Integration

| | |
|---|---|
| **Form** | shared lib by default, static lib with BLEND2D_STATIC=ON (CMake) |
| **Dependencies** | AsmJit, cloned into 3rdparty/asmjit and embedded (required unless BLEND2D_NO_JIT=ON); nothing else for the library. The shared build avoids linking the C++ standard library by default (BLEND2D_NO_STDCXX). Qt and the comparison libraries are needed only for demos and bl_bench backends. |
| **Minimum toolchain** | C++20 compiler (cxx_std_20 is a PUBLIC compile feature on the CMake target), CMake 3.24; the C API is usable from C (the repo builds .c samples) |
| **Platforms** | x86 and x86-64 (runtime dispatch from SSE2 to AVX2/AVX-512 plus JIT), AArch64 (JIT plus ASIMD), AArch32 (ASIMD, no JIT); other CPUs use the reference pipelines; Windows, Linux and macOS (Windows threads or POSIX threads) |
| **Thread safety** | One BLContext, including its weak copies, must not be used by several threads at once. Objects are atomically reference-counted, so images, paths and fonts can be shared between threads. Multi-threaded rendering is internal (thread_count in BLContextCreateInfo), and results are visible only after flush(BL_CONTEXT_FLUSH_SYNC) or end(). |
| **Drop-in for the baseline** | no |

## Gotchas

- The API was renamed between the measured version and HEAD. The thesis harness (Blend2D 0.12.0) calls setCompOp, threadCount and BLRuntime::queryBuildInfo, while 0.21.3 headers use snake_case (set_comp_op, thread_count, bl_context_\* C functions). The GitHub repo publishes no releases or tags, and the vcpkg port lags (issue #249 asks for 0.21.2), so pin a commit.
- There are no exceptions (built with -fno-exceptions -fno-rtti). Errors come back as BLResult, and convenience constructors such as BLContext(BLImage&) swallow errors, so use begin() and check its result.
- Threads hurt very small shapes. In the M1 Pro data, 8-thread mode was slower than single-threaded in 24 of 174 cells at 8x8 (derived from page data), and the thesis notes a slowdown 'for very small sizes' in Fill-Linear-RectA. Use the threaded context for large or numerous shapes, not for UI glyph-sized work.
- Open robustness issues: #252 (ASan READ in the edge builder when stroking a path with a subnormal move_to and a huge control point), #255 and #256 (integer overflow in BLString and BLPath reserve, fixes staged), and #265 (stroke coverage gap when a segment is shorter than the pen width). Separately, the CMake error for a missing AsmJit uses message(FATAL ...), which CMake does not treat as an error, so the build fails later at add_subdirectory.

## Known shortcomings

- Tier B on the independent ETH master thesis (LaurenzV/master-thesis main.pdf, Fig. 40: 10.8/50.3/21.9 ms, Apple M1 Pro, Blend2D 0.12.0) and its vello_chart data (data/arm/2025-09-24.json); compiler and Skia/Cairo build flags are unstated, so not A. The thesis author is the Vello CPU author, so the comparison is independent of Blend2D but first-party for Vello. Blend2D is also a listed baseline of this category; it is kept because it beats the other incumbents (Skia, Cairo).
- The bl_bench harness (LaurenzV/blend2d-apps) is fair (same RNG sequence, anti-aliasing on, Blend2D timed including flush SYNC, best of 10), but the measured version is 0.12.0 and the API was renamed to snake_case by 0.21.3; no GitHub releases or tags. Blend2D loses to Vello CPU on tiny curved paths (up to 2.9x) and to Cairo on StrokeRectA Solid (1.35x on M1, 3.0x on i9, derived from page data); the 8-thread mode is slower than single-threaded in 24 of 174 8x8 cells; open issues #252, #255, #256, #265; JIT only on x86 and AArch64.

## Caveats and trade-offs

Blend2D is itself one of the category's baselines; the entry records it as the strongest CPU rasterizer measured against Skia and Cairo. Numbers come from a third-party thesis whose harness is Blend2D's own benchmark (bl_bench, fork LaurenzV/blend2d-apps; the harness now lives at blend2d-testing/bench in the blend2d repo), so the workload design is first-party even though the run is not. The result JSON records Blend2D version 0.12.0, older than the current v0.21.3. Skia version and the build flags of Skia and Cairo are not stated. blend2d.com/performance.html (the author's own charts) was not reachable.

Optional JIT through AsmJit (a dependency only when JIT is enabled); C and C++ API; CPU-only; multi-threaded rendering context available.

## Maintenance

Actively developed (last commit 2026-09-05, version 0.21.3 in core/api.h, about 2.0k stars, 37 open issues) under the Zlib licence, so it is copyable. It is pre-1.0 with API renames between versions and no GitHub releases, so vendor a pinned commit together with its AsmJit checkout.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement: the ETH master's thesis by the Vello CPU author (not a Blend2D developer) runs Blend2D, Skia and Cairo in the Blend2D benchmark harness on an Apple M1 Pro; Figure 40 (Fill-Solid-RectU) shows Blend2D ST 10.8 ms, Skia 50.3 ms, Cairo 21.9 ms at 256x256, and the raw result file LaurenzV/vello_chart data/arm/2025-09-24.json gives the same values (92.8 renders/ms for Blend2D). Harness code is public (blend2d/blend2d blend2d-testing/bench, LaurenzV/blend2d-apps bl_bench) but the compiler and the Skia/Cairo build flags are not stated, so not A.
- **Verifier notes:** All four headline numbers and the 4.7x multi-thread figure are in the thesis PDF (Figures 40 and 50 and section 5.4 text) and in the public result JSON. Blend2D is a category baseline, not yet in the rendered lists; orchestrator may decide whether an incumbent belongs as an entry. On the i9-14900K data (data/x86/2026-01-22.json) Blend2D ST is the fastest single-threaded renderer in 973 of 1044 cells (derived from page data).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/LaurenzV/master-thesis/blob/main/main.pdf>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/main/main.pdf>
  - <https://github.com/blend2d/blend2d>
  - <https://github.com/blend2d/blend2d/commits>
  - <https://github.com/blend2d/blend2d/tree/master>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/configure_demos.sh>
  - <https://github.com/orgs/blend2d/repositories>
  - <https://github.com/LaurenzV/vello_chart>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data/arm>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/manifest.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/x86/2026-01-22.json>
  - <https://github.com/LaurenzV/blend2d-apps>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/blend2d/blend2d>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/README.md>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/blend2d/core/api.h>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/blend2d/core/context.h>
  - <https://raw.githubusercontent.com/blend2d/blend2d/HEAD/blend2d/raster/analyticrasterizer_p.h>
  - <https://github.com/blend2d/blend2d/tree/master/blend2d-testing/bench>
  - <https://github.com/blend2d/blend2d/tree/master/blend2d/raster>
  - <https://github.com/blend2d/blend2d/tree/master/blend2d/pipeline>
  - <https://github.com/blend2d/blend2d/issues>
  - <https://github.com/blend2d/blend2d/issues/252>
  - <https://github.com/blend2d/blend2d/issues/264>
  - <https://github.com/blend2d/blend2d/issues/265>
  - <https://github.com/blend2d/blend2d/releases>
  - <https://github.com/blend2d/blend2d/tags>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/main/main.pdf>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/README.md>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend_blend2d.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend_skia.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend_cairo.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/x86/2026-01-22.json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/blend2d/blend2d`) · [data/wave10/enrich/raw/github_com_blend2d_blend2d.json](../../../data/wave10/enrich/raw/github_com_blend2d_blend2d.json) (enrichment confidence 0.85)

</details>
