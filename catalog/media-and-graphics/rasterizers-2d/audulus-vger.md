# vger (Audulus)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Objective-C++ and Metal (C API)` · `MIT` · 🟢 active

> Small Metal GPU renderer for immediate-mode UIs (Apple only); its author reports 120 fps where nanovg managed 30 fps.

| | |
|---|---|
| **Beats** | nanovg |
| **Claimed result** | 'vger maintains 120fps while nanovg falls to 30fps on my 120Hz iPad because of CPU-side path tessellation, and other overhead' (4x frame rate, derived from page data). |
| **Workload** | Rendering the Audulus immediate-mode UI on a 120Hz iPad; frame rate with vger versus with nanovg. |
| **Metric** | throughput |
| **Hardware** | 120Hz iPad (model not stated) |
| **Adoption** | 323 stars; renders the Audulus app |
| **Last commit** | 2026-06-08 |
| **Links** | [repository](https://github.com/audulus/vger) · [benchmark](https://github.com/audulus/vger) |

## Verdict

The only number is the author's README anecdote: in the Audulus UI on an unnamed 120 Hz iPad, vger holds 120 fps while nanovg (which nanovg build, presumably Metal, is not stated) drops to 30 fps. The author attributes this to CPU-side tessellation in nanovg. 120 fps is the display cap, so vger's real headroom and the GPU cost are unknown, and there is no scene description, compiler or frame-time data. The commented-out testNanovgPerf in Tests/vgerTests/vgerTests.mm would not be a like-for-like check either. It calls a stale API that no longer exists (vgerColorPaint without a context, a vgerPrim aggregate), strokes 5.12 px wide where testBezierPerf strokes 1 px, and does not wait for nanovg's GPU work, while the vger test waits with waitUntilCompleted and also times its rand() calls.

## Use it when

- iOS 14+ or macOS 11+ app whose UI redraws every frame (audio and synth UIs, node editors, plotting) and is CPU-bound in nanovg or CoreGraphics because of path tessellation.
- Scenes made mostly of simple shapes (knobs, rounded rects, wires, short quadratic strokes, short text labels), where one instanced draw replaces thousands of tessellated meshes.
- You want a small, vendorable MIT renderer with a C drawing API that you can call from C++ or Swift, and you can write a little Objective-C++ or Swift glue for context creation and command-buffer encoding.
- Prototyping a GPU UI on Apple hardware that you may later port with the same design via the Rust/wgpu port audulus/vger-rs.

## Skip it when

- Any non-Apple target or headless CPU rendering: it needs Metal, and text depends on CoreText and CoreGraphics; use vger-rs or a CPU rasterizer instead.
- SVG or PDF-grade vector output: cubics are approximated by two quadratics ('crude approximation' per vger.h, 'lousy method' per the README), fills are even-odd only, and there are no path strokes with joins, caps or dashes, and vger.h has no clipping, scissor or blend-mode API.
- Large or complex paths: vgerQuadTo silently drops segments beyond 1024 per path, and vgerFill gives up (returns false) after 2048 slabs. Per-pixel cost grows with the number of segments active in a slab.
- Pixel-exact anti-aliasing: coverage is an SDF smoothstep across about one pixel, not exact area coverage. Open issues report different stroke widths for line and Bezier segments (#7) and propose better AA (#18).
- Workloads that need a measured advantage: the only comparison with nanovg is an anecdote, and nothing compares vger with Skia, Rive, Vello or other GPU renderers.

## How it is fast

Each primitive becomes one instanced quad, and the fragment shader evaluates the shape's signed distance analytically (SDF, anti-aliased with smoothstep over fwidth), so the CPU does no path tessellation. The CPU only appends primitive records into shared-storage MTLBuffers. A compute pass then computes bounds, and a single instanced draw per layer covers everything, split only when the texture changes. Path fills are cut on the CPU into horizontal slabs (vgerPathScanner), and each slab's quad tests a pixel against only the segments active in that band. The inside test is even-odd: it counts crossings with each segment's chord and flips again inside the region between the curve and its chord, a 'reverse Loop-Blinn' that avoids solving quadratics. Text layouts are cached per string and glyphs go into a CoreGraphics-rasterized atlas.

## Compared with alternatives

Pick vger over the Rive Renderer, TGFX or vkvg when the app is Apple-only, the scene uses vger's simple primitive set, and you want a few thousand lines of MIT code with a C API rather than a full engine. Pick those siblings (or Vello) when you need cross-platform GPUs, full path semantics or published comparative numbers. It is not comparable to the CPU rasterizers in this category (Blend2D, AGG, Blaze, tiny-skia), which produce exact-coverage pixels without a GPU.

## Integration

| | |
|---|---|
| **Form** | Swift Package (Objective-C++ and Metal sources, built as a library; also source-drop into an Xcode project) |
| **Dependencies** | Apple frameworks only (Metal, MetalKit, CoreText, CoreGraphics); bundles stb_rect_pack; the test target alone depends on wtholliday/MetalNanoVG (branch spm) |
| **Minimum toolchain** | Swift tools 5.9 and C++20 (Package.swift); Xcode with the Metal compiler. Command-line `swift build` fails ('Bundle has no member module', missing default.metallib), open issue #15. |
| **Platforms** | macOS 11+ and iOS 14+ on Metal GPUs only |
| **Thread safety** | Not documented. A vgerContext is a mutable struct (transform stack, path scanner, text cache, scene buffers) with no locking, so use one context per thread. |
| **Drop-in for the baseline** | partial: it replaces nanovg's role as an immediate-mode GPU UI renderer, but the API, paint model and feature set differ (no nonzero fill, joins, dashes or scissor; cubics approximated), so call sites must be rewritten |

## Gotchas

- Default is single-buffered: unless you pass VGER_DOUBLE_BUFFER or VGER_TRIPLE_BUFFER to vgerNew, vgerBegin reuses the same shared MTLBuffers the GPU may still be reading (vger.mm), so wait for the previous command buffer to finish or turn buffering on.
- Overflow can go unreported: vgerQuadTo ignores segments beyond 1024 per path, and GPUVec::append stops adding primitives once a buffer would exceed 256 MB (vgerScene.h). Check vgerFill's return value and vgerPrimCount.
- Lines are stored as degenerate quadratics, and cubics are split into two quadratics with no error control, so SVG-style cubic art can visibly deviate. Text is not affected because glyphs are rasterized into an atlas by CoreGraphics.
- Paints are per frame: paint indices from vgerColorPaint and the gradient calls become invalid after the next vgerBegin, and invalid indices make vgerFill return false.

## Known shortcomings

- The '120fps vs 30fps' claim against nanovg appears only in the README's 'Why?' section: unnamed 120 Hz iPad, Metal only, no scene or frame times; testNanovgPerf in Tests/vgerTests/vgerTests.mm is commented out and no results are published. Implementation is Objective-C++ plus Metal with a C API (Apple-only).
- Metal GPU UI renderer, Apple only (macOS 11+, iOS 14+): comparable to GPU renderers (nanovg Metal, Rive, TGFX, vkvg, Vello), not to CPU rasterizers. Even-odd fill only; cubics approximated by two quadratics; no joins, dashes or scissor. vgerQuadTo silently drops segments past 1024 and GPUVec drops primitives past 256 MB; single-buffered by default; swift build fails (issue #15). The commented-out testNanovgPerf is itself flawed (stale API, 5.12 px versus 1 px strokes, no GPU wait on the nanovg side, rand() inside the vger timing), so the README anecdote stays the sole evidence.

## Caveats and trade-offs

Single anecdotal first-party figure from the README 'Why?' section for one app (the Audulus UI) on one unnamed 120Hz iPad; no nanovg version, scene description or frame-time numbers, and 120 fps is the display cap, so vger's headroom is unknown. Tests/vgerTests/vgerTests.mm has an XCTest testNanovgPerf (10,000 random quadratic bezier strokes at 512x512 through nanovg's Metal backend), but it is commented out and no results are published; the active testBezierPerf and testTigerPerf time vger alone. GPU (Metal fragment-shader) renderer vs nanovg, whose slowdown the README attributes to CPU-side path tessellation; Apple-only (iOS/macOS, Metal), with a Rust/wgpu port in audulus/vger-rs for other platforms; not a CPU rasterizer. Baseline nanovg is not Skia, Cairo or Blend2D.

Apple platforms only (iOS and macOS, Metal); limited primitive set drawn as instanced quads with analytic fragment-shader evaluation (quadratic Bezier strokes, round rectangles, circles, arcs, text, path fills); C interface usable from C, C++, Objective-C and Swift, but vgerEncode must be called from Objective-C or Swift because it takes an MTLCommandBuffer; non-Apple users are pointed to the Rust port vger-rs.

## Maintenance

Active (commits through 2026-06-08, including a layer-specific encode API, clipped stroke prims and pixel-diff tests) and MIT-licensed (the header carries a zlib-style notice). It ships in the Audulus app, so it is copyable for Apple-only projects, but it is a single-maintainer library with 10 open issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Why?' section says verbatim that 'for Audulus, vger maintains 120fps while nanovg falls to 30fps on my 120Hz iPad because of CPU-side path tessellation, and other overhead'; this is a single first-party anecdote with no scene, iPad model, nanovg version or frame-time data, so C. The only comparison code in the repo (testNanovgPerf in Tests/vgerTests/vgerTests.mm) is commented out and no results are published.
- **Verifier notes:** The number lives only in README.md 'Why?' (raw README read); hardware is just '120Hz iPad'. Implementation is Objective-C++ (.mm) plus Metal shaders with a plain C API header and C++20 in Package.swift, so the record's language field ('C') would be better as 'Objective-C++ with a C API' (not a correctable field here). Metadata checked: MIT, 323 stars, not a fork, not archived, last commit 2026-06-08 (active).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/audulus/vger>
  - <https://github.com/audulus/vger/commits/main>
  - <https://github.com/audulus/vger/tree/main/Sources/vger>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/README.md>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Package.swift>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Tests/vgerTests/vgerTests.mm>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/README.md>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Package.swift>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/include/vger.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Tests/vgerTests/vgerTests.mm>
  - <https://github.com/audulus/vger/tree/main/Sources/vger>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vger.mm>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vger_private.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vgerScene.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vgerPathScanner.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vgerPathScanner.mm>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vger.metal>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/path.metal>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/sdf.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/prim.h>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vgerRenderer.mm>
  - <https://raw.githubusercontent.com/audulus/vger/HEAD/Sources/vger/vgerGlyphCache.mm>
  - <https://github.com/audulus/vger/issues?q=is%3Aissue>
  - <https://github.com/audulus/vger/issues/15>
  - <https://github.com/audulus/vger/commits/main>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/audulus/vger`) · [data/wave10/enrich/raw/github_com_audulus_vger.json](../../../data/wave10/enrich/raw/github_com_audulus_vger.json) (enrichment confidence 0.75)

</details>
