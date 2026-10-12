# Rive Renderer (rive-runtime)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Rive's C++ runtime and GPU vector renderer (Metal, Vulkan, D3D, GL); vendor claims 66x Skia on animated tiles.

| | |
|---|---|
| **Beats** | Skia (and Flutter Impeller, per the same post); Skia backend and configuration unstated |
| **Claimed result** | Snippet only (LinkedIn post by Rive's Guido Rosso, not opened): on an 'iPhone 12 Max', Skia renders 9 animated tiles in about 100 ms (10 fps) while the Rive Renderer renders 100 tiles in about 16 ms (60 fps), stated as '66x faster here, 6000 tiles/sec vs 90 tiles/sec'; the post adds that two tiles with Skia/Impeller already exceed 16 ms per frame. |
| **Workload** | Animated vector tiles drawn on an iPhone 12 (many path-heavy tiles per frame), Rive Renderer vs Skia/Impeller. |
| **Metric** | throughput |
| **Hardware** | iPhone 12 (per snippet) |
| **Adoption** | 1.2k stars, 122 forks; renderer used across Rive's Apple, Android, Flutter, Unity, Unreal and web runtimes |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/rive-app/rive-runtime) · [benchmark](https://www.linkedin.com/posts/guidorosso_the-rive-renderer-is-66x-faster-here-activity-7060336385030819841-QkSZ) |

## Verdict

The only speed number is Rive's own LinkedIn post (dated 2023-05-05, derived from its activity ID, so about ten months before the renderer was open-sourced): on an 'iPhone 12 Max', Skia drew 9 animated Rive tiles in about 100 ms while the Rive Renderer drew 100 tiles in about 16 ms (and 36 tiles in about 5 ms), stated as 66x or 6000 vs 90 tiles/sec. The Skia backend and settings, the measured code version and the harness are not published (the post is snippet-only here), and no third-party measurement was found.

## Use it when

- Shipping Rive (.riv) animations in a C++ app, game engine or embedded UI: this is the reference renderer behind Rive's Apple, Android, Flutter, Unity, Unreal and web runtimes.
- Many animated, path-heavy vector layers per frame on Apple GPUs (iOS and Apple Silicon Macs), where Metal raster order groups give the fully featured rasterOrdering mode.
- GPU vector rendering on Android GL ES devices exposing EXT_shader_pixel_local_storage or framebuffer fetch, or on Vulkan/D3D12 desktops, when CPU rasterization (Blend2D, Skia CPU) is the frame-time bottleneck.
- You already render through Rive's abstract Renderer and want to swap a Skia or CoreGraphics backend for the native GPU one without changing scene code.

## Skip it when

- You need a drop-in SkCanvas replacement, PDF/SVG output, text shaping APIs outside Rive's text system, or CPU-only/headless rendering: there is no CPU rasterizer backend (RenderContextNULL only counts work for benchmarks).
- Hardware without PLS-class features: WebGL and many GL drivers fall back to atomics or the MSAA depthStencil mode, and open issue #83 (Feb 2026, unanswered) asks how to get PLS on WebGL at all; the 66x claim came from an iPhone, the best case.
- Build-system constraints: it builds with premake via build/build_rive.sh, which clones a pinned premake and fetches Vulkan-Headers, VulkanMemoryAllocator, DirectX-Headers, harfbuzz (Rive fork) and python ply from GitHub at configure time, then compiles shaders with a make + Python minifier step; there is no CMake package and issue #69 asks for prebuilt libraries.
- Mature D3D11 or Linux GL deployments without testing: open issues include #99 (D3D11 access violation in makeImageTexture), #57 (invalid DX resource flags fail renderer init) and #92 (OpenGL context fails on Linux).
- Many identical sprites: issue #81 (open) notes each Rive instance is its own draw, with no GPU instancing across artboards.

## How it is fast

Paths are not stenciled or CPU-rasterized: curves are tessellated on the GPU (Wang's formula picks segment counts; TessVertexSpan rows are rendered into a tessellation texture) and drawn as 'midpoint fan' triangle patches with analytic anti-aliased coverage, or, for large filled paths, through a cached interior triangulation (a Skia-derived GrInnerFanTriangulator) gated by a TriangulationController. Coverage and per-path 16-bit IDs live in pixel local storage, so many paths batch into one pass without clearing a coverage buffer; overlapping fragments are synchronized per platform by an InterlockMode (rasterOrdering via Metal raster order groups or GL framebuffer fetch / EXT/ANGLE PLS, atomics, clockwise, clockwiseAtomic, or an MSAA depthStencil fallback). A SIMD IntersectionBoard (255x255 tiles, int16x8 lanes) groups non-overlapping draws so they can share a batch, and GPU buffers are ring-allocated (3 frames) so CPU preparation overlaps GPU rendering.

## Compared with alternatives

Pick it over ThorVG or TGFX when your content is Rive animation or you want a renderer whose hot path is GPU PLS coverage rather than a CPU raster backend; pick vkvg or vger only for simpler Vulkan/Metal UI drawing, and Blend2D when you need fast, portable CPU rendering with an independent benchmark behind it.

## Integration

| | |
|---|---|
| **Form** | static lib (librive.a plus librive_pls_renderer.a, built with premake) |
| **Dependencies** | Platform GPU SDK (Metal/Xcode, Vulkan SDK, Windows SDK for D3D, GL/WebGL); configure-time GitHub downloads of Vulkan-Headers, VulkanMemoryAllocator, DirectX-Headers, python ply (shader minifier) and Rive's forks or pins of harfbuzz (rive-app/harfbuzz rive_13.1.1), SheenBidi, yoga and miniaudio for text, layout and audio; optional rive decoders for images |
| **Minimum toolchain** | C++17; clang (Xcode CLI tools on macOS, distro clang on Linux), clang-cl or MSVC with Visual Studio 2022 on Windows; bash, git and Python 3 for the build |
| **Platforms** | iOS, macOS, tvOS, visionOS (Metal), Android (GL ES, Vulkan), Windows (D3D11, D3D12, GL, Vulkan), Linux (GL, Vulkan), WebAssembly (WebGL2, WebGPU) |
| **Thread safety** | A RenderContext is driven from one render thread per frame; render_context.hpp comments describe a recording session (DeferredSession) on a producer thread while the render thread is inside a frame, and an atomic added to fix a data race there. Broader guarantees not documented. |
| **Drop-in for the baseline** | partial — scene code written against rive::Renderer can swap the Skia backend (skia/) for RiveRenderer, but there is no SkCanvas-compatible API for general Skia users |

## Gotchas

- Feature set depends on InterlockMode: atomics mode masks out nested clipping and modulated images, and clockwise/clockwiseAtomic modes override every path's fill rule (no even-odd), per ShaderFeaturesMaskFor in gpu.hpp.
- Per-device quirks are handled in code: pre-Apple-Silicon iOS PowerVR GPUs drop the low 3 bits of path IDs for fp16 precision, the iOS simulator has no framebuffer reads and falls back to atomics, and ANGLE devices run a runtime test before trusting KHR_blend_equation_advanced.
- The build fetches pinned third-party repos from GitHub and runs a shader make step during premake configuration, so offline or hermetic builds need those mirrored.
- tests/bench micro-benchmarks run against RenderContextNULL (CPU-side draw preparation only) and print the minimum time over a 5 s loop; they measure no GPU time and no Skia baseline.

## Known shortcomings

- Only numbers are a vendor marketing claim seen in search snippets (LinkedIn post and Rive announcement: Skia 9 tiles at about 100 ms vs Rive 100 tiles at about 16 ms on an iPhone, '66x faster, 6000 vs 90 tiles/sec'); tests/bench holds internal micro-benchmarks with no Skia or Impeller baseline. Tier C.
- The only number remains a vendor LinkedIn snippet from a post dated 2023-05-05 (about 10 months before the open-source release), so the measured code, Skia configuration and harness are unpublished. iPhone is the best case (Metal raster order groups); WebGL and GL fall back to atomics or MSAA depth-stencil (issue #83 unanswered). tests/bench uses RenderContextNULL (CPU side only, no Skia). The build fetches dependencies from GitHub at configure time; open issues #99 (D3D11 crash), #57 (DX init) and #92 (Linux GL).

## Caveats and trade-offs

Vendor claim by the company selling the product (C), snippet only: the LinkedIn post and Rive's blog are blocked or unopened. The rive-runtime README and renderer/README.md contain no benchmark numbers, and tests/bench holds only internal micro-benchmarks without a Skia baseline. The test is animation-heavy tile grids on one mobile GPU, not a general path-rendering benchmark; Skia configuration (Ganesh or Graphite, GPU or CPU) is unstated, and 'iPhone 12 Max' is not a real model name (probably iPhone 12 Pro Max). Search-snippet discussion in the March 2024 open-source announcement thread on HN says performance depends on hardware pixel-local-storage support, with Apple Silicon the best case, so the gap on other GPUs may be smaller.

GPU renderer (Metal, Vulkan, D3D12, D3D11, OpenGL/WebGL, per the README) built around a geometric reduction of anti-aliased paths into triangle patches and best with pixel local storage support; not a CPU rasterizer. Designed for Rive content and its runtime, with an abstract renderer interface (a Skia integration layer and a CoreGraphics renderer also exist in the repo).

## Maintenance

Actively developed (last commit 2026-10-03, about 3,300 commits) and MIT-licensed, so copyable, but it is a large engine with its own build system rather than a vendorable library, and the speed claim is first-party marketing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are a vendor claim (LinkedIn post by Rive's Guido Rosso and Rive's announcement), seen as search snippets: Skia 9 tiles at about 100 ms versus Rive 100 tiles at about 16 ms on an iPhone, '66x faster, 6000 tiles/sec vs 90 tiles/sec'. The repo's tests/bench directory holds only internal micro-benchmarks (path building, intersection board, artboard frame) with no Skia or Impeller baseline and no results, so first-party snippet evidence stays C.
- **Verifier notes:** License MIT, 1.2k stars, last commit 2026-10-03 (active) confirmed on github.com. Real, widely shipped renderer; evidence is a first-party marketing number, so C is right.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rive-app/rive-runtime>
  - <https://github.com/rive-app/rive-runtime/commits>
  - <https://github.com/rive-app/rive-runtime/tree/main/tests>
  - <https://github.com/rive-app/rive-runtime/tree/main/tests/bench>
  - <https://github.com/rive-app/rive-runtime/tree/main/renderer>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/README.md>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/rive-app/rive-runtime>
  - <https://github.com/rive-app/rive-runtime/tree/main/renderer/src>
  - <https://github.com/rive-app/rive-runtime/tree/main/tests/bench>
  - <https://github.com/rive-app/rive-runtime/issues>
  - <https://github.com/rive-app/rive-runtime/issues?q=is%3Aissue+performance>
  - <https://github.com/rive-app/rive-runtime/issues/83>
  - <https://github.com/rive-app/rive-runtime/issues/81>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/README.md>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/premake5_v2.lua>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/premake5_pls_renderer.lua>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/draw.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/intersection_board.hpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/render_context.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/rive_renderer.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/gl/render_context_gl_impl.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/src/metal/render_context_metal_impl.mm>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/include/rive/renderer/gpu.hpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/renderer/include/rive/renderer/render_context.hpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/tests/bench/bench.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/tests/bench/bench.hpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/tests/bench/draw_pls_path.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/tests/bench/intersection_board_bench.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/tests/bench/artboard_frame_bench.cpp>
  - <https://raw.githubusercontent.com/rive-app/rive-runtime/HEAD/dependencies/premake5_harfbuzz_v2.lua>
  - WebSearch: Rive Renderer vs Skia Impeller benchmark frame time measured (snippet of https://www.linkedin.com/posts/guidorosso_the-rive-renderer-is-66x-faster-here-activity-7060336385030819841-QkSZ)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/rive-app/rive-runtime`) · [data/wave10/enrich/raw/github_com_rive_app_rive_runtime.json](../../../data/wave10/enrich/raw/github_com_rive_app_rive_runtime.json) (enrichment confidence 0.6)

</details>
