# Anti-Grain Geometry (AGG 2.6)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Classic scalar C++ template 2D rasterizer; an independent bl_bench run puts it \~1.2x Skia and \~2.3x Cairo single-threaded.

| | |
|---|---|
| **Beats** | Skia (CPU pipeline) and Cairo 1.18.4 |
| **Claimed result** | Apple M1 Pro, 2026-06-08 run, single-threaded, geometric mean of per-cell rcpms ratios over the 522 cells AGG shares with each baseline (29 tests x Solid/Linear/Radial x 6 sizes; derived from page data): 1.21x Skia (faster in 66% of cells; strokes 1.39x, fills 1.08x; 1.03x at 8x8, 1.02x at 16x16, 1.22x at 32x32, 1.39x at 64x64, 1.34x at 128x128, 1.28x at 256x256) and 2.29x Cairo 1.18.4 (faster in 94% of cells). The three earlier M1 runs (2025-09-24, 2026-01-22, 2026-05-17) give 1.20-1.21x Skia and 2.27-2.30x Cairo. Intel Core i9-14900K Windows run of 2026-01-22 (no Skia in that dataset): 1.87x Cairo 1.18.2 (1.89x on 2025-09-14). Slower than Blend2D 0.12.0 single-threaded (0.30x). All ratios derived from page data. |
| **Workload** | Blend2D bl_bench suite as run by LaurenzV (vello_chart): 29 tests (FillRectA/U/Rot, FillRoundU/Rot, FillTriangle, FillPoly NZ/EO with 10/20/40 vertices, Fill/Stroke Butterfly, Fish, Dragon, World, and the matching stroke tests) x paint styles x 6 sizes 8x8 to 256x256, SrcOver, 512x600 PRGB32 target, single thread, best of repeated runs reported as render calls per ms. The AGG backend supports only Solid, Linear and Radial styles (87 of 174 test/style rows). It fills integer-aligned solid rectangles through Agg2D::fillRectangleI (a direct span blend with no rasterizer) and draws radial gradients as centred radials, while Skia and Cairo draw a two-point conical gradient with a focal point. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (aarch64, macOS); second dataset Intel Core i9-14900K (x86_64, Windows) |
| **Compiler and flags** | Not stated in the result files. Harness: Blend2D bl_bench from LaurenzV/blend2d-apps built with CMake -DCMAKE_BUILD_TYPE=Release (C++17); AGG compiled from source as the copy bundled in blend2d-apps/3rdparty/agg plus the Agg2D wrapper in 3rdparty/agg2d; Skia linked from the vcpkg unofficial-skia package and Cairo from pkg-config, both prebuilt with unrecorded build flags; compiler and version unstated. The exact harness commit used for the 2026 runs is not recorded. |
| **Adoption** | 367 stars, 92 forks (GitHub copy of the SourceForge AGG SVN); AGG 2.4 itself is widely vendored, e.g. by matplotlib's Agg backend |
| **Last commit** | 2023-08-21 |
| **Links** | [repository](https://github.com/ghaerr/agg-2.6) · [benchmark](https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json) |

## Verdict

LaurenzV's independent run of the Blend2D bl_bench harness on an Apple M1 Pro (2026-06-08, macOS, 512x600 PRGB32 target, SrcOver, single thread, options.repeat 15; compiler and flags unrecorded, Skia from vcpkg's unofficial-skia, Cairo 1.18.4 from pkg-config) gives AGG a 1.21x geometric-mean speedup over Skia and 2.29x over Cairo across the 522 cells they share (29 tests x Solid/Linear/Radial x 6 sizes), which I recomputed from the rcpms values; the same file puts AGG at 0.30x Blend2D ST, 0.48x Vello CPU ST, 0.70x JUCE 8.0.8, 1.10x raqote and 2.42x tiny-skia. The measured code is blend2d-apps' bundled AGG 2.4-line copy with its own modified Agg2D wrapper, whose core rasterizer headers match this repository.

## Use it when

- Single-threaded CPU rendering of complex anti-aliased paths and strokes (charts, maps, plotting backends) where Cairo is the incumbent: 2.29x Cairo 1.18.4 by geometric mean on an M1 Pro, faster in 94% of cells.
- Stroke-heavy scenes: 1.39x Skia on strokes overall (StrokeWorld 1.92x, StrokeFish 1.82x, StrokeButterfly 1.67x).
- Portable or embedded targets where Skia's build or a SIMD- or JIT-dependent renderer is not an option: scalar C++, no dependencies for the core, renders into any custom pixel format.
- When you want a small, permissively licensed (Modified BSD or AGG Public License) renderer you can vendor and modify, or you already maintain an AGG-based stack.

## Skip it when

- When raw CPU throughput is the goal: in the same M1 Pro dataset Blend2D 0.12.0 is about 3.3x faster single-threaded and scales with threads, Vello CPU is about 2.1x faster single-threaded and JUCE 8.0.8's software renderer about 1.43x faster (derived from page data).
- Many small simple shapes: at 8x8 and 16x16 it is only at parity with Skia, and it loses FillRectA (0.84x except solid), FillRoundU (0.80x) and StrokeRectA (0.52x).
- Untrusted vector input without hardening: CVE-2019-6245 (unbounded recursion in the cell rasterizer) and CVE-2019-6247 (heap overflow via blend_hline) were filed against AGG 2.4 as used in svgpp, and the default integer clipper overflows on huge coordinates.
- When you need a maintained dependency: this GitHub copy last changed 2023-08-21 and has open build failures (issue #13: GCC 14.2.1 with FreeType 2.13.3 in agg_font_freetype.cpp); the SourceForge SVN fixed that and C++23 warnings in r140-r145 (2024).
- When you need modern features out of the box: no text shaping, colour management, GPU backend or multi-threading; the bench backend only supports Solid, Linear and Radial paints, with Agg2D's gradients limited to pad linear and centred radial (core AGG has gradient_radial_focus and repeat/reflect adaptors in agg_span_gradient.h).

## How it is fast

The core is an exact-area-coverage scanline rasterizer in the lineage of FreeType's gray rasterizer: edges are converted to 24.8 fixed point and walked into per-pixel cells holding signed area and cover, the cells are bucketed by row and sorted by x (qsort_cells), and sweep_scanline accumulates cover into 8-bit coverage spans with an optional gamma table and non-zero or even-odd fill. Every stage (vertex converters, span generators, blenders, pixel formats) is a template, so the whole pipeline inlines into one specialised loop with no virtual calls or per-pixel dispatch, and cell blocks (4096 cells each) and scanline buffers are reused between paths. It is plain scalar C++ with no SIMD and no threading; its lead over Skia in this benchmark comes from polygon, path and stroke work at 32 px and larger, while Skia wins simple rectangle and rounded-rect fills.

## Compared with alternatives

Pick Blend2D (about 3.3x faster single-threaded, multi-threaded) or JUCE's software renderer (about 1.43x faster) when speed is the main goal; pick AGG over them when you want a dependency-free, portable scalar renderer with a fully pluggable template pipeline (custom pixel formats, gamma, subpixel-accurate strokes) or already run on an AGG-based stack. Against tiny-skia and raqote AGG is faster in the same data (2.42x and 1.10x geomean, derived).

## Integration

| | |
|---|---|
| **Form** | mostly header-only templates (agg-src/include) plus a small static library (agg-src/src/\*.cpp: curves, strokes, dashes, affine transforms, arcs; built as libagg.a); commonly source-dropped |
| **Dependencies** | none for the core; FreeType or Win32 TrueType optional for fonts; X11, SDL2, Win32 or Nano-X only for the demos; GPC only for boolean polygon operations |
| **Minimum toolchain** | no minimum C++ standard documented (pre-C++11 style code); MSVC 2019 fixes merged in 2022; GCC 14 fails on agg_font_freetype.cpp with FreeType 2.13.3 in this copy (issue #13) |
| **Platforms** | any (portable scalar C++, no SIMD); demo platform layers for X11, SDL2, Win32, Nano-X and macOS |
| **Thread safety** | not documented; the rasterizer, scanline and renderer classes keep their state in members, so use one set per thread and do not share an object across threads |
| **Drop-in for the baseline** | no |

## Gotchas

- The default rasterizer_scanline_aa&lt;&gt; uses rasterizer_sl_clip_int, which converts coordinates with a plain iround(v \* 256) to 24.8 fixed point before clipping, so coordinates beyond about +/-8.4 million px overflow; use rasterizer_sl_clip_int_sat or rasterizer_sl_clip_dbl and a clip box for untrusted input.
- Cell storage is capped (cell_block_limit, default 1024 blocks x 4096 cells = 4,194,304 cells) and add_curr_cell() simply returns once the cap is hit, so a huge or very detailed path renders incomplete with no error; raise the limit through the rasterizer constructor.
- As read in this copy, rasterizer_cells_aa::line() splits a segment spanning 16384 px or more horizontally into two recursive calls but has no return afterwards, so such a segment is also rasterized whole; keep geometry clipped to the canvas so segments never get that long.
- The benchmarked Agg2D is blend2d-apps' modified copy (fillRectangleI fast path for integer solid rectangles, three-colour gradients), which this repo's agg-src/agg2d lacks; this repo's Agg2D instantiates pixfmt_custom_blend_rgba, whose copy_pixel() does not compile when used (issue #14: pixel_type\* passed to make_pix(int8u\*)). Do not copy agg-src/gpc (non-commercial licence here; SourceForge r144 has it under MIT).

## Known shortcomings

- Tier B on the Vello CPU author's vello_chart data (arm 2026-06-08, Apple M1 Pro: 1.21x Skia winning 66% of cells, 2.29x Cairo 1.18.4; x86 2026-01-22: 1.87x Cairo 1.18.2; compiler, flags and Skia version unrecorded): wins polygon and path fills and strokes, loses simple rectangle, round and triangle fills and StrokeRectA (0.52x). The measured code is blend2d-apps/3rdparty/agg plus Agg2D, whose hot-path headers match ghaerr/agg-2.6 except std:: qualifiers and cell_block_limit. AGG's radial gradient is centred while Skia's is focal two-point. ghaerr/agg-2.6 is not the canonical tree: the SourceForge SVN is ahead (r145, 2024-09-28; GPC moved to MIT), and this copy still carries the non-commercial GPC clipper, so usability is mixed.
- Recomputed from the vello_chart data over 522 cells: 1.206x Skia and 2.286x Cairo, but 0.70x JUCE, 0.30x Blend2D single-threaded and 0.48x Vello CPU single-threaded. The measured Agg2D is the blend2d-apps modified wrapper (fillRectangleI, 3-colour gradients), not code in the ghaerr copy. CVE-2019-6245 and CVE-2019-6247 (AGG 2.4 via svgpp); the default integer clipper overflows beyond about 8.4M px; the cell limit drops cells silently; line() splitting of 16384+ px segments has no return; issues #13 (GCC 14 build failure) and #14 (pixfmt_custom_blend_rgba compile error) open; SourceForge r145 is ahead of this copy.

## Caveats and trade-offs

Measured code is not this repository but the AGG 2.4-line copy bundled in blend2d-apps/3rdparty/agg, driven through the Agg2D wrapper; its hot-path headers (agg_basics.h, agg_rasterizer_scanline_aa.h, agg_rasterizer_cells_aa.h, agg_pixfmt_rgba.h) match ghaerr/agg-2.6 except for std:: qualifiers and a configurable cell_block_limit, so the result transfers. Against Skia (rows = test x style, geomean over sizes) AGG wins 67 of 87 rows: the polygon and path fills (FillPoly 1.06-1.35x by test, only FillPolyNZi10/Radial slightly behind at 0.98x; FillFish 1.54x, FillDragon 1.30x, FillWorld 1.27x, FillButterfly 1.21x) and every stroke except StrokeRectA (StrokeWorld 1.92x, StrokeFish 1.82x, StrokeButterfly 1.67x, StrokeRectU 1.60x); it loses the simple-shape fills FillRectA (0.84x, except solid), FillRectU (0.90x), FillRectRot (0.85x), FillRoundU (0.80x), FillRoundRot (0.94x), FillTriangle (0.94x) and StrokeRectA (0.52x). At 8x8 and 16x16 it is only at parity overall. Against Cairo it wins 84 of 87 rows, losing StrokeRectA/Solid (0.33x), FillRectU/Solid (0.46x) and FillRectA/Linear (0.91x). Both libraries run single-threaded and anti-aliased; AGG's radial gradient is the simpler centred form (radial rows 1.13x vs linear 1.25x against Skia), and output equivalence is not checked in the published data. This GitHub copy was cloned from the SourceForge SVN at r132 (2019-05-06) and last changed on 2023-08-21; the SourceForge SVN continued to r145 (2024-09-28: C++20/23 warning fixes, and r144 moved the bundled General Polygon Clipper to MIT). In this copy GPC is still under its non-commercial licence, so do not copy agg-src/gpc (the core is BSD-3-Clause or the AGG Public License). Skia's version is not recorded in the data.

Header-heavy C++ template library, CPU only, run single-threaded in this harness. Older, lower-level API than Skia or Cairo. The upstream SourceForge AGG 2.4 and this 2.6 mirror are dual licensed under a Modified BSD License or the Anti-Grain Geometry Public License.

## Maintenance

This GitHub mirror (367 stars, 92 forks, 6 open issues, 2 stale PRs) has been unchanged since 2023-08-21 while the upstream SourceForge SVN reached r145 on 2024-09-28 with C++23, FreeType 2.13.3 and fallthrough fixes and MIT-licensed GPC, so vendor from SourceForge; the core is BSD-3-Clause or AGG Public License and copyable, and usability is mixed only because of agg-src/gpc here (issue #10 also flags a GPL-licensed SDL2 demo platform file).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party run (Vello CPU author, unaffiliated with AGG, Skia or Cairo) of the public Blend2D bl_bench harness (LaurenzV/blend2d-apps bl_bench/backend_agg.cpp, backend_skia.cpp, backend_cairo.cpp; CMakeLists.txt) with the CPU model in the result file; compiler, compiler version and flags are not recorded and Skia/Cairo were prebuilt packages, so not A. I recomputed every ratio from the rcpms values and they match the record.
- **Verifier notes:** Ratios reproduce exactly and are stable across all four M1 runs. Do not treat ghaerr/agg-2.6 as the canonical AGG: it is a 2019 clone of the official SourceForge SVN with a few merged PRs and a 2023-08-21 last commit, while SourceForge (https://sourceforge.net/projects/agg/, svn r145, 2024-09-28) is upstream and ahead (and has GPC under MIT); keep ghaerr as the convenient GitHub link with is_fork_of pointing to SourceForge. Usability is mixed only because of the non-commercial GPC files in this copy.
- **Fields the verifier corrected:** `is_fork_of`, `usability`, `stars_or_usage`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
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
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_agg.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/3rdparty/agg/include/agg_basics.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/3rdparty/agg/include/agg_rasterizer_scanline_aa.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/3rdparty/agg/include/agg_rasterizer_cells_aa.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/3rdparty/agg/include/agg_pixfmt_rgba.h>
  - <https://github.com/ghaerr/agg-2.6>
  - <https://github.com/ghaerr/agg-2.6/commits>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/README.md>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-web/license/index.html>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/copying>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_basics.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_rasterizer_scanline_aa.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_rasterizer_cells_aa.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_pixfmt_rgba.h>
  - <https://sourceforge.net/projects/agg/>
  - <https://sourceforge.net/p/agg/svn/HEAD/log/>
- **Sources the enricher read:**
  - <https://github.com/ghaerr/agg-2.6>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/README.md>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/copying>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/Makefile>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_basics.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_config.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_array.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_rasterizer_scanline_aa.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_rasterizer_cells_aa.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_rasterizer_sl_clip.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_pixfmt_rgba.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_scanline_u.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_renderer_scanline.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/include/agg_span_gradient.h>
  - <https://raw.githubusercontent.com/ghaerr/agg-2.6/HEAD/agg-src/agg2d/agg2d.h>
  - <https://github.com/ghaerr/agg-2.6/tree/master/agg-src>
  - <https://github.com/ghaerr/agg-2.6/tree/master/agg-src/src>
  - <https://github.com/ghaerr/agg-2.6/commits/master>
  - <https://github.com/ghaerr/agg-2.6/issues?q=is%3Aissue>
  - <https://github.com/ghaerr/agg-2.6/issues/13>
  - <https://github.com/ghaerr/agg-2.6/issues/14>
  - <https://github.com/ghaerr/agg-2.6/pulls>
  - <https://sourceforge.net/p/agg/svn/HEAD/log/>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_agg.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/3rdparty/agg2d/agg2d.h>
  - https://www.cvedetails.com/cve/CVE-2019-6245/ (WebSearch snippet only)
  - https://cyberstrike.io/cve/CVE-2019-6247/ (WebSearch snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ghaerr/agg-2.6`) · [data/wave10/enrich/raw/github_com_ghaerr_agg_2_6.json](../../../data/wave10/enrich/raw/github_com_ghaerr_agg_2_6.json) (enrichment confidence 0.8)

</details>
