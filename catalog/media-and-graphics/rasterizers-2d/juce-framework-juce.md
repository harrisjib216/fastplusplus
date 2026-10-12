# JUCE software renderer (juce_graphics)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> JUCE's CPU path rasterizer (EdgeTable + SWAR pixel blending); about 1.7x Skia and 2.9x Cairo single-threaded on M1 Pro.

| | |
|---|---|
| **Beats** | Skia (CPU pipeline) and Cairo 1.18.4 |
| **Claimed result** | Apple M1 Pro, 2026-06-08 run, JUCE 8.0.8 software renderer, single-threaded, geometric mean of per-cell rcpms ratios over 870 cells (29 tests x Solid/Linear/Radial/Pattern_NN/Pattern_BI x 6 sizes; derived from page data): 1.68x Skia (faster in 84% of cells; strokes 2.10x, fills 1.40x; 1.26x at 8x8, 1.32x at 16x16, 1.69x at 32x32, 2.02x at 64x64 and 128x128, 1.97x at 256x256) and 2.93x Cairo 1.18.4 (faster in 95% of cells). Excluding the three StrokeRect tests, which JUCE draws as four filled rectangles instead of a stroked path: 1.64x Skia and 2.90x Cairo. Earlier M1 runs give 1.61-1.70x Skia and 2.79-2.94x Cairo. Slower than Blend2D 0.12.0 single-threaded (0.41x). No JUCE run in the x86 data. All ratios derived from page data. |
| **Workload** | Same bl_bench suite as above (JUCE 8.0.8 through juce::Graphics on a juce::SoftwareImageType image): 29 fill/stroke shape tests x five paint styles (solid, linear, radial, two image-pattern filters; no conic) x six sizes 8x8 to 256x256, SrcOver, 512x600 target, render calls per ms. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (aarch64, macOS) |
| **Compiler and flags** | Not stated in the result files. Harness: Blend2D bl_bench from LaurenzV/blend2d-apps, CMake -DCMAKE_BUILD_TYPE=Release (C++17); JUCE 8.0.8 compiled from source via JUCE_DIR/add_subdirectory with -DJUCE_USE_CURL=0 -DUSE_COREGRAPHICS_RENDERING=0 and a juce::SoftwareImageType surface; Skia from the vcpkg unofficial-skia package and Cairo from pkg-config, both prebuilt with unrecorded flags; compiler and version unstated. |
| **Adoption** | 8.9k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/juce-framework/JUCE) · [benchmark](https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json) |

## Verdict

An independent run (Vello CPU author) of the Blend2D bl_bench harness on an Apple M1 Pro, single-threaded, SrcOver, 29 shape tests x 5 paint styles x 6 sizes (8x8 to 256x256), gives JUCE 8.0.8 a geometric-mean 1.68x Skia (1.64x without the non-equivalent StrokeRect tests) and 2.93x Cairo 1.18.4; my recomputation of the 2026-06-08 file matches (per style vs Skia: solid 1.48x, linear 1.94x, radial 1.78x, patterns 1.61-1.63x). Compiler, flags and the Skia version are not recorded, there is no x86 run, and output equivalence is not checked.

## Use it when

- You already ship a JUCE app or audio plug-in and need CPU rendering (Linux, embedded, offscreen images) that is faster than Skia or Cairo would be.
- Stroke-heavy vector UI and charts: on the M1 Pro run strokes averaged 2.10x Skia (StrokeWorld 3.08x, StrokeFish 2.47x).
- Complex polygon and path fills at 32-256 px (FillPolyNZi40 solid 1.4-2.2x Skia at 32x32 and above) and gradient-filled shapes (linear-gradient cells 1.94x Skia, derived from page data).
- Your project is AGPLv3 or you hold a commercial JUCE licence.

## Skip it when

- Large solid or image rectangle fills and blits: JUCE 8.0.8 runs FillRectA solid at 0.31x Skia at 128x128 and 256x256, and aligned pattern blits at about 0.71x Skia (derived from page data).
- You want the fastest CPU rasterizer: Blend2D single-threaded is about 2.4x faster (JUCE 0.41x Blend2D) and Vello CPU single-threaded about 1.5x faster (JUCE 0.68x, faster in only 20% of cells), both derived from the same M1 Pro file.
- You need pixel parity with Skia or Cairo: coverage is approximate, 8.0.8 blends with a divide-by-256 shortcut, radial gradients in 8.0.8 have no focal point, and drawRect draws inside the bounds.
- Closed-source products without a commercial JUCE licence, or projects that want a small standalone library: juce_graphics pulls in juce_events and juce_core, plus freetype2 and fontconfig on Linux.
- Multi-threaded rendering: the renderer is single-threaded with no tiling or worker pool.

## How it is fast

Paths are flattened (PathFlatteningIterator) into an EdgeTable: per-scanline lists of (x in 1/256 pixel, winding step) points, sampled at an adaptive number of sub-scanlines (256 / (1 + |dx/dy|) sub-steps, so steep edges cost one sample per scanline), then sorted and converted to 8-bit coverage spans. Spans are handed to templated per-fill callbacks (SolidColour, Gradient, ImageFill, TransformedImageFill) that write whole runs at once, with full-coverage runs taking a plain replace/blend loop. Pixels are blended SWAR-style, two 8-bit channels per 32-bit word (0x00ff00ff masks); gradients read a precomputed colour lookup table (up to 256 entries per colour stop, capped at 3x the gradient extent) indexed in fixed point. Translation-only transforms take separate fast paths (TranslationOrTransform, ImageFill vs TransformedImageFill).

## Compared with alternatives

Pick it over Blend2D or Vello CPU only when you are already inside JUCE: both are faster on the same M1 Pro harness and are standalone, permissively licensed libraries. Against AGG (1.43x AGG, derived from page data) and Skia or Cairo it is the faster option for strokes and complex paths, but it loses to Skia on large rectangle and image fills.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | juce_events and juce_core (JUCE modules); freetype2 and fontconfig on Linux; Cocoa and QuartzCore frameworks on macOS |
| **Minimum toolchain** | C++17, CMake 3.22+; Xcode 12.4, Visual Studio 2019, g++ 7 or Clang 6 |
| **Platforms** | macOS, Windows, Linux, iOS, Android (x86_64, x86, arm64; 32-bit Arm not regularly tested); portable C++ with no ISA requirement |
| **Thread safety** | Not documented in juce_GraphicsContext.h; the renderer is single-threaded, so use one Graphics context per thread and image. |
| **Drop-in for the baseline** | no |

## Gotchas

- Graphics::drawRect fills four rectangles inside the shape bounds instead of stroking a centred path, so stroked rectangles look and cost differently from Skia or Cairo strokes (StrokeRectU measured 3.44x Skia for this reason).
- JUCE 8.0.8 PixelARGB::blend uses (0x100 - alpha) and &gt;&gt; 8 with clamping, a divide-by-256 approximation; JUCE 9 (HEAD) switched to a rounded divide-by-255 SWAR blend, so 8.0.8 output and speed are not those of the current release.
- The benchmark forces juce::SoftwareImageType and builds with USE_COREGRAPHICS_RENDERING=0; JUCE's native image types and window peers can use CoreGraphics or Direct2D instead, so in a normal macOS or Windows app you get this renderer only if you ask for it.
- EdgeTable sampling cost grows as edges get flatter (up to 256 sub-scanline samples per scanline for near-horizontal edges, since the step is clamped to 1-256), and coverage within a scanline is taken from one x sample per sub-step, not exact area.

## Known shortcomings

- JUCE 8.0.8 software renderer at B on the same vello_chart data (1.68x Skia winning 84% of cells, 2.93x Cairo; 1.64x/2.90x without the StrokeRect tests, where JUCE's drawRect is four inner fills rather than a path stroke); its radial gradient has no focal point. Losses are the large solid and pattern rectangle fills (down to 0.31x). Licence AGPLv3 or commercial.
- Recomputed from the vello_chart data: 1.68x Skia and 2.93x Cairo, but 0.41x Blend2D and 0.68x Vello CPU single-threaded (1.43x AGG, 3.09x Rust tiny-skia; derived from page data); JUCE loses on big rectangle and image fills. The measured 8.0.8 renderer takes precision shortcuts (blend divides by 256, gradient lookup table, sampled EdgeTable coverage), so the test is not output-equivalent, and JUCE 9.0.0 since reworked the software renderer (divide-by-255 blend, vectorised fills, image fills 2-4x faster per a search snippet), so the measured version is stale.

## Caveats and trade-offs

Some tests do different work from the baselines. JUCE's Graphics::drawRect fills four rectangles inside the shape bounds (LowLevelGraphicsContext::drawRect) instead of stroking a centred mitred path, so StrokeRectA/U/Rot are not like-for-like (StrokeRectU 3.44x Skia). JUCE's radial paint is a centred radial with no focal point, while Skia and Cairo draw a two-point conical gradient. JUCE's EdgeTable rasterizer is anti-aliased but uses its own approximate coverage (8-bit fixed-point x with adaptive vertical sub-steps), and output equivalence is not checked in the published data. All renderers here run single-threaded. Against Skia (rows = test x style, geomean over sizes) JUCE wins 134 of 145 rows, with the largest gains on strokes (StrokeWorld 3.08x, StrokeFish 2.47x, StrokeDragon 2.33x) and complex polygon fills (FillPolyEOi40 2.03x). It loses large solid and pattern rectangle fills (FillRectA/Solid 0.56x, down to 0.31x at 128x128 and 256x256), rotated nearest-neighbour pattern fills (FillRectRot 0.61x, FillRoundRot 0.72x) and FillRoundU/FillRectRot/FillTriangle solid (0.74-0.81x). Against Cairo it wins 138 of 145 rows, losing FillRectA (0.43-0.45x), FillRectU (0.59-0.68x) and StrokeRectA/Solid (0.71x). Only one machine (M1 Pro). JUCE 8.0.8 was measured; the repository is now at 9.0.3 (2026-09-28). The harness's AGG/Cairo/Skia/JUCE backends come from the Blend2D author and the runs from the Vello CPU author, both competitors but independent of JUCE; the Skia version is not recorded. Licence: the JUCE modules, juce_graphics included, are dual-licensed AGPLv3 / commercial JUCE licence, so closed-source or non-AGPL use needs the commercial licence (the README asks tools to tell users this).

The renderer is part of the large JUCE application framework (juce_graphics, juce_core, juce_events), not a standalone library; it is single-threaded and CPU only. Dual licensed: AGPLv3 or a paid commercial JUCE licence, so closed-source use needs the commercial licence.

## Maintenance

Actively developed (JUCE 9.0.3, last commit 2026-09-28, 8.9k stars); JUCE 9.0.0 lists 'Improved the performance of the software renderer' and, per search-result text from the JUCE 9 forum announcement (forum page not opened), refactored PixelARGB for vectorised fills with 2-4x faster image fills, so the 8.0.8 numbers, especially the losing image and rectangle fills, are likely out of date; copyable under AGPLv3 or the commercial JUCE licence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party run (Vello CPU author, unaffiliated with JUCE, Skia or Cairo) of the public Blend2D bl_bench harness (LaurenzV/blend2d-apps bl_bench/backend_juce.cpp, backend_skia.cpp, backend_cairo.cpp; JUCE 8.0.8 recorded in the result file) on a named CPU; compiler, version and flags are not recorded, so not A. My recomputation of the ratios matches the record.
- **Verifier notes:** Ratios reproduce exactly and hold across all four M1 runs. The claim stands at 1.64x Skia even after dropping the StrokeRect tests JUCE does differently. The record's caveat that JUCE trails Skia on small fills was wrong: its losses are on large solid and pattern rectangle fills, so I rewrote the caveat. Metadata (AGPL-3.0, 8.9k stars, last commit 2026-09-28) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/manifest.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-05-17.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-01-22.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/x86/2026-01-22.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/x86/2025-09-14.json>
  - <https://github.com/LaurenzV/vello_chart>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data>
  - <https://github.com/LaurenzV/blend2d-apps>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://github.com/LaurenzV/blend2d-apps/branches/all>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/README.md>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_skia.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_cairo.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/HEAD/main.pdf>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_juce.cpp>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/8.0.8/modules/juce_graphics/contexts/juce_GraphicsContext.cpp>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/8.0.8/modules/juce_graphics/contexts/juce_LowLevelGraphicsContext.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/8.0.8/modules/juce_graphics/geometry/juce_EdgeTable.cpp>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/8.0.8/modules/juce_graphics/native/juce_RenderingHelpers.h>
  - <https://github.com/juce-framework/JUCE>
  - <https://github.com/juce-framework/JUCE/commits/master/>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/CHANGE_LIST.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_core/system/juce_StandardHeader.h>
- **Sources the enricher read:**
  - <https://github.com/juce-framework/JUCE>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/README.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/CHANGE_LIST.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/BREAKING_CHANGES.md>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/juce_graphics.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/contexts/juce_GraphicsContext.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/native/juce_RenderingHelpers.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/geometry/juce_EdgeTable.cpp>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/geometry/juce_EdgeTable.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/colour/juce_PixelFormats.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/8.0.8/modules/juce_graphics/colour/juce_PixelFormats.h>
  - <https://raw.githubusercontent.com/juce-framework/JUCE/HEAD/modules/juce_graphics/colour/juce_ColourGradient.cpp>
  - <https://github.com/juce-framework/JUCE/issues?q=is%3Aissue%20software%20renderer>
  - <https://github.com/juce-framework/JUCE/issues?q=is%3Aissue%20EdgeTable%20OR%20antialiasing%20OR%20fillPath>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_juce.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_skia.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_blend2d.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json>
  - WebSearch: JUCE 9 "software renderer" performance improved EdgeTable forum (snippets from forum.juce.com/t/juce-9-is-available-now/69175, not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/juce-framework/juce`) · [data/wave10/enrich/raw/github_com_juce_framework_juce.json](../../../data/wave10/enrich/raw/github_com_juce_framework_juce.json) (enrichment confidence 0.75)

</details>
