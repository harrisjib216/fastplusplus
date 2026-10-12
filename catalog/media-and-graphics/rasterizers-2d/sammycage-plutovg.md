# plutovg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C` · `MIT` · 🟢 active

> Small MIT C 2D vector library with a Cairo-like canvas API; no published speed comparison against Cairo, Skia or Blend2D.

| | |
|---|---|
| **Beats** | Cairo, Skia, Blend2D (category baselines; no comparison found) |
| **Claimed result** | none: no numeric comparison found |
| **Workload** | No speed comparison found. The README and repo page have no benchmark. The independent suite mfabbri77/VGCPU-Benchmark lists plutovg 0.0.4 beside Cairo 1.18.2, Skia m124, Blend2D, AGG, ThorVG, Qt and Vello CPU, but commits no result numbers. |
| **Metric** | throughput |
| **Adoption** | 527 stars; rasteriser behind LunaSVG and PlutoSVG; v1.3.3 released 2026-05-18 |
| **Last commit** | 2026-07-16 |
| **Links** | [repository](https://github.com/sammycage/plutovg) |

## Verdict

No speed claim exists to verify: the README, release notes and issue tracker carry no numbers, and the only independent suite that includes plutovg (mfabbri77/VGCPU-Benchmark, with Cairo 1.18.2, Skia m124 and Blend2D) commits its harness but no results.

## Use it when

- You need a dependency-free C library (vendored stb_truetype, stb_image, stb_image_write) to draw anti-aliased paths, gradients and text into an ARGB32 buffer, for example on embedded, homebrew or game targets.
- You want Cairo-like drawing semantics without pulling in Cairo, pixman, FreeType and fontconfig, and footprint matters more than peak throughput.
- You already render SVG with LunaSVG or PlutoSVG and want direct access to the same backend.
- MIT licensing with a small codebase (about a dozen C files) that is easy to audit or vendor.

## Skip it when

- You need proven speed over Cairo or Skia: no benchmark exists, and VGCPU-Benchmark wires up a plutovg backend (labelled 0.0.4) but commits no results.
- Throughput-critical rendering of large or complex scenes: compositing is scalar apart from an SSE2 fill and rendering is single-threaded; Blend2D, Vello CPU and ThorVG are the measured options in this catalog.
- You need separable blend modes (multiply, screen, overlay and so on): only the 12 Porter-Duff operators exist.
- Real text layout: glyphs come from stb_truetype outlines with no shaping, kerning or hinting.
- Pixel formats other than premultiplied ARGB32 (RGB565 and similar were requested in issues #33 and #41).

## How it is fast

Nothing in the repository claims or measures speed; the design is simply lean. Coverage comes from a vendored copy of FreeType's ftgrays cell/area scanline rasteriser (8-bit anti-aliased spans, 8 KB stack pool with band splitting) and FreeType's stroker, clipping is done by intersecting span lists, and compositing uses Qt-style SWAR pixel arithmetic (BYTE_MUL, INTERPOLATE_PIXEL_255 on two channels per 32-bit word) with 1024-entry gradient lookup tables. The only SIMD is an SSE2 memfill for opaque solid spans; there is no JIT, tiling, sparse-strip or multithreaded pipeline of the kind Blend2D or Vello CPU use.

## Compared with alternatives

Pick it over Blend2D, ThorVG or tiny-skia when a small, dependency-free C library with a Cairo-like API matters more than measured speed; for throughput Blend2D (and Vello CPU) have independent numbers beating Skia and Cairo, while plutovg has none.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Meson or CMake), or source-drop of the source/ directory |
| **Dependencies** | libm; optional C11 threads.h or pthreads for font-cache locks; stb_truetype, stb_image and stb_image_write are vendored |
| **Minimum toolchain** | C11 compiler (Meson default gnu11; CMake C_STANDARD 11); Meson 1.0+ or CMake 3.15+ |
| **Platforms** | Portable C; CI builds on Linux, macOS and Windows; SSE2 path only for memfill, scalar elsewhere |
| **Thread safety** | Canvas and surface objects are not synchronised (one thread per canvas). Reference counts are atomic (C11 stdatomic or Interlocked). Font faces and the font-face cache lock a mutex, but that mutex compiles to a no-op when neither Win32 nor C11 threads.h is available. |
| **Drop-in for the baseline** | partial: Cairo-like concepts and the same premultiplied ARGB32 layout as CAIRO_FORMAT_ARGB32, but a different API (plutovg_canvas_\*), no PDF/SVG/PS backends and no blend modes beyond Porter-Duff |

## Gotchas

- Transformed non-tiled images are sampled nearest-neighbour (blend_transformed_argb); bilinear sampling exists only for tiled textures under rotation or shear, and PR #72 to extend it is still open.
- Strokes are built after the transform with one width scaled by hypot(sx, sy)/sqrt(2), so non-uniform scale or skew gives a uniform-width stroke instead of the elliptical pen Cairo produces.
- If a single scanline needs more cells than the 8 KB stack pool, PVG_FT_Raster_Render restarts the whole path with a doubled heap pool (up to 8 MB), skipping spans already emitted; beyond 8 MB the path is silently left partly drawn, since the call returns void.
- Vendored FreeType-derived files (plutovg-ft-raster.c, plutovg-ft-stroker.c, plutovg-ft-math.c) carry the FreeType Project License, which asks for credit in documentation; the rest is MIT.

## Known shortcomings

- Tier D: no number anywhere (README, releases v0.0.11 to v1.3.3, issues #65 and #43); VGCPU-Benchmark lists a plutovg backend labelled 0.0.4 but commits no results, and the listed LunaSVG entry's pipeline bench gives no render-only Cairo figure. Three vendored FreeType files (plutovg-ft-raster.c, plutovg-ft-stroker.c, plutovg-ft-math.c) carry the FTL header, so usability is mixed.
- Enricher (e120, 2026-10-05): still no speed numbers, D stands. The code is FreeType's ftgrays rasterizer plus stroker with Qt-style scalar blending; the only SIMD is an SSE2 memfill. Transformed plain images are sampled nearest-neighbour (PR #72 open); strokes use uniform width under non-uniform scale or skew; a scanline overflowing the 8 KB pool restarts the whole path with a doubled heap pool and the path is silently left partly drawn past 8 MB; Porter-Duff operators only; text has no shaping or kerning; the font mutex becomes a no-op without threads.h. Issue #50 is a false alarm. VGCPU-Benchmark still has no committed results.

## Caveats and trade-offs

No speed number in the README, repo page, release notes, the issue tracker (a 'performance' search returns only #65 and #43, neither about speed), the LunaSVG README, or WebSearch. Lead: run mfabbri77/VGCPU-Benchmark (0 stars, MIT, last commit 2026-08-31, has a report generator and pre-baked versus full-lifecycle modes, but commits no results; perf/ holds only a scene list) to obtain numbers against Cairo, Skia and Blend2D; its README labels the plutovg backend version 0.0.4, older than the current v1.3.3. Indirect only: the listed LunaSVG entry (which renders through plutovg) has a third-party pipeline benchmark against cairosvg and resvg-py (pillow-lunasvg benchmarks/results.md), but it times Python parse, render and PNG encode, gives no render-only figure for Cairo, and so is not a plutovg-versus-Cairo rasteriser comparison. Usability mixed: the project licence is MIT, but the vendored FreeType-derived files source/plutovg-ft-raster.c (ftgrays), plutovg-ft-stroker.c and plutovg-ft-math.c carry the FreeType Project License header (source/FTL.TXT is included; permissive with an attribution/credits requirement, not OSI-approved).

Small standalone C library built with Meson or CMake; path fill, stroke and dash, gradients, textures, text, clipping, compositing; single-thread software rendering. Sum-then-saturate coverage model (per VGCPU-Benchmark README), so self-overlapping subpaths inside one path composite differently from the exact-union model of Cairo and Skia. Rasteriser descends from FreeType ftgrays.

## Maintenance

Actively maintained (last commit 2026-07-16, v1.3.3 released 2026-05-18; May 2026 fixes for allocation-failure handling and surface-size overflow); MIT plus FreeType-licensed rasteriser files, so usability is mixed but practical to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark_url and no speed number anywhere: the README, repo page, releases notes (v0.0.11 to v1.3.3) and issue search for 'performance' carry none, and mfabbri77/VGCPU-Benchmark lists a plutovg backend (labelled 0.0.4) beside Cairo 1.18.2, Skia m124 and Blend2D but commits no results (perf/ holds only perf_suite_scenes.txt; docs/ has no reports). With no numbers it cannot rise above D.
- **Verifier notes:** Metadata matches the record (MIT, 527 stars, 69 forks, not a fork, not archived, last commit 2026-07-16, v1.3.3 latest release dated May 18). Kept rather than rejected as not-notable: it is the rasteriser behind the already-listed LunaSVG and PlutoSVG and is a distinct library, not a wrapper or port, so it is not a duplicate. VGCPU-Benchmark remains the route to real numbers.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://github.com/sammycage/plutovg>
  - <https://github.com/sammycage/plutovg/commits>
  - <https://github.com/sammycage/plutovg/releases>
  - <https://github.com/sammycage/plutovg/issues?q=is%3Aissue+performance>
  - <https://github.com/sammycage/plutovg/tree/main/source>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/README.md>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-ft-raster.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-ft-stroker.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-ft-math.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/FTL.TXT>
  - <https://github.com/mfabbri77/VGCPU-Benchmark>
  - <https://github.com/mfabbri77/VGCPU-Benchmark/tree/main/perf>
  - <https://github.com/mfabbri77/VGCPU-Benchmark/tree/main/docs>
  - <https://github.com/mfabbri77/VGCPU-Benchmark/commits>
  - <https://raw.githubusercontent.com/mfabbri77/VGCPU-Benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/README.md>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/include/plutovg.h>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-private.h>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-utils.h>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-rasterize.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-blend.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-canvas.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-path.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-font.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-paint.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-surface.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-matrix.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-ft-raster.c>
  - <https://github.com/sammycage/plutovg/issues?q=is%3Aissue>
  - <https://github.com/sammycage/plutovg/issues/86>
  - <https://github.com/sammycage/plutovg/issues/50>
  - <https://github.com/sammycage/plutovg/commits/main>
  - <https://github.com/sammycage/plutovg/pulls?q=is%3Apr>
  - <https://github.com/mfabbri77/VGCPU-Benchmark>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sammycage/plutovg`) · [data/wave10/enrich/raw/github_com_sammycage_plutovg.json](../../../data/wave10/enrich/raw/github_com_sammycage_plutovg.json) (enrichment confidence 0.75)

</details>
