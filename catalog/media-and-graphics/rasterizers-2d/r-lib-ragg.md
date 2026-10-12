# ragg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `R (C++ core on AGG 2.4)` · `MIT; bundled AGG 2.4 sources under a BSD-style license (LICENSE.note)` · 🟢 active

> R raster graphics devices (PNG/JPEG/TIFF/WebP) on AGG 2.4; about 1.3x faster than R's anti-aliased cairo png() on a composite ggplot2.

| | |
|---|---|
| **Beats** | Cairo (R grDevices png(type = 'cairo') anti-aliased raster device) |
| **Claimed result** | README: 'Faster (up to 40% faster than anti-aliased cairo device)'; no number in the vignette backs the 40%. Vignette conclusion: 'a general speed gain of around \~33% compared to cairo' among anti-aliased devices. Rendered plots (pkgdown build of 2026-04-08), read approximately: complex ggplot2 composite ragg about 245 ms vs anti-aliased cairo (gray and subpixel) about 320-325 ms, about 1.3x (derived from page data, plot readings), with the void_dev() non-rendering baseline at about 130 ms; unfilled circles about 5.5 ms vs about 7.3 ms; filled complex polygon about 38 ms vs about 48 ms. Non-anti-aliased cairo beats ragg on single primitives (about 3.1 ms unfilled circles, about 6.5 ms filled polygon) but is slower on the composite (about 265 ms). Cairo is about twice as fast to open and close a device, slightly faster for non-rotated rasters, and about on par for gradients; ragg is clearly faster for clipping paths, masks and patterns. |
| **Workload** | R graphics primitives (1000 random points with pch 1, 19, 4, 0, 15, 2 and '#', lines with and without dash patterns, polygons, even-odd paths, rotated and interpolated rasters, text strings), a prebuilt layered ggplot2 plot (hexbin, points, smooth, facets) and grid clipping paths, masks, gradients and patterns, rendered to PNG and timed with bench::mark (min_iterations 10) per device: agg_png() vs png(type = 'cairo') with antialias none, gray and subpixel; void_dev() time marks non-rendering overhead; Xlib omitted on the build machine. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-24.04 x86_64 runner (pkgdown article build of 2026-04-08: Ubuntu 24.04.4 LTS, R 4.5.3, ragg 1.5.2 per session info); CPU model not stated |
| **Compiler and flags** | not stated (package built on the CI runner with R's default toolchain and flags; session info lists no compiler) |
| **Adoption** | 184 stars, 30 forks; on CRAN; README documents use as a knitr device (dev = 'ragg_png') and as the RStudio AGG graphics backend |
| **Last commit** | 2026-05-13 |
| **Links** | [repository](https://github.com/r-lib/ragg) · [benchmark](https://github.com/r-lib/ragg/blob/main/vignettes/ragg_performance.Rmd) |

## Verdict

First-party bench::mark runs (min 10 iterations) in the pkgdown-rendered vignette, built 2026-04-08 on a GitHub Actions ubuntu-24.04 x86_64 runner with R 4.5.3 and ragg 1.5.2 (CPU model and compiler flags not stated), timing agg_png() against png(type = 'cairo') with antialias none, gray and subpixel: the layered ggplot2 composite takes about 245 ms with ragg vs about 320-325 ms with anti-aliased cairo and about 265 ms with non-anti-aliased cairo, where a void_dev() run of the same plot (about 130 ms, single system.time call) marks the non-rendering share, so ragg's rendering part is roughly 1.6x faster (derived from page data, plot readings). R's cairo device turns anti-aliasing off for every solid fill (cairoFill sets CAIRO_ANTIALIAS_NONE), so the anti-aliased cairo settings only anti-alias strokes and text; ragg does more work on fills, not less.

## Use it when

- You render R plots to raster files (PNG/JPEG/TIFF/WebP) with anti-aliasing and want them faster than png(type = 'cairo'): about 245 ms vs about 320 ms for the vignette's layered ggplot2 composite.
- Text-heavy plots: in the 2026-04-08 build 1000 text strings took about 19 ms with ragg vs about 81 ms with every cairo setting (about 4x, read from the plot).
- Plots using grid masks or pattern fills (R &gt;= 4.1): about 8 ms vs 37 ms for the mask test and about 94 ms vs 410 ms for the pattern test against anti-aliased cairo (read from the plots).
- Headless servers, CI and knitr/pkgdown builds that need system fonts, right-to-left text, emoji and identical output across Linux, macOS and Windows without X11.
- RStudio (&gt;= 1.4) or Positron users who want the AGG backend as the interactive graphics device.

## Skip it when

- You need a 2D rasterizer callable from C++: ragg's C++ core needs R's graphics engine and Rinternals; use AGG 2.6 or Blend2D directly.
- Plots that clip many primitives with a complex grid clipping path: in the 2026-04-08 build ragg took about 87 ms vs about 55 ms for cairo on the vignette's clip-path test (cairo about 1.6x faster), because ragg re-rasterizes the whole clip path for every primitive.
- Many small, nearly empty images: opening and closing a device costs about 7.3 ms vs about 3 ms for png(type = 'cairo') (mostly PNG encoding and file size, per the vignette).
- Fill-only output where non-anti-aliased edges are acceptable: cairo skips anti-aliasing on fills and wins on filled rectangles (about 0.85 ms vs 1.1 ms per 1000) and other single fill-heavy primitives.
- Vector output (PDF, SVG): ragg is raster-only; use cairo_pdf, svglite or the pdf device.

## How it is fast

Every primitive goes through AGG's scanline anti-aliasing rasterizer (rasterizer_scanline_aa: exact-area coverage cells, sorted and swept per scanline) and is blended as spans straight into a premultiplied RGB/RGBA buffer by renderer_scanline_aa_solid; fills use packed scanlines (scanline_p8), strokes and dashes are turned into polygons by conv_stroke/conv_dash and rasterized the same way. Text goes through FreeType with a process-wide static agg::font_cache_manager, so repeated glyphs come from a cache; shaping is done by the textshaping package (HarfBuzz/FriBidi). Masks are applied at scanline level through masked-scanline adaptors over an alpha or luminance buffer, whereas R's cairo device pushes and pops a cairo group and calls cairo_mask for every masked primitive (cairoBegin/cairoEnd in grDevices cairoFns.c), which is why the mask and pattern tests show the largest gaps.

## Compared with alternatives

Pick ragg when the caller is R code and you want a faster anti-aliased replacement for png(type = 'cairo'); from C++ use the rasterizer underneath it (Anti-Grain Geometry, catalogued as AGG 2.6) or Blend2D, which beats AGG and Cairo in the catalogued third-party thesis and has a JIT pipeline that ragg does not.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | R with the systemfonts and textshaping packages (HarfBuzz, FriBidi via textshaping); system FreeType, libpng, libtiff, libjpeg, libwebp and libwebpmux; AGG 2.4 sources are bundled and built as a static library inside the package |
| **Minimum toolchain** | Built by R CMD INSTALL with R's configured C/C++ compiler; src/Makevars.in sets no CXX_STD, so R's default C++ standard applies (code uses C++11 features such as unique_ptr and unordered_map). pkg-config is used to find system libraries; Windows builds use Rtools. |
| **Platforms** | Linux, macOS, Windows (Rtools, Arm Windows prepared in 1.2.6); big-endian handled through separate raster pixel formats (WORDS_BIGENDIAN) |
| **Thread safety** | not documented; R graphics devices are driven from R's main thread, and the FreeType font engine and glyph cache are function-local statics shared by all ragg devices in the process |
| **Drop-in for the baseline** | partial — agg_png()/agg_jpeg()/agg_tiff() mirror the png()/jpeg()/tiff() arguments and knitr accepts dev = 'ragg_png', but there is no type or antialias argument (ragg always anti-aliases), fonts are resolved through systemfonts, and pixels will not match cairo output |

## Gotchas

- Fills are always anti-aliased, so adjacent filled shapes can show faint seams; open issue #103 (geom_tile banding on Windows) and #131 (striping between spplot polygons) report this, and 1.3.0 added rectangle snapping to the pixel grid (on by default) for fill-only rectangles.
- The vignette prose is older than its plots: it calls ragg 'much better' on clipping paths and only 'slightly faster' on text, while the 2026-04-08 rendered plots show ragg slower on clipping paths and about 4x faster on text.
- Loading the package can be slow when the user's local font directory is large, because systemfonts rescans it on every load (issue #210, open as of 2026-10).
- Gradient stops placed very close together (e.g. 0.0001 apart) lose the flanking colours, while cairo renders them (issue #154, open).

## Known shortcomings

- R graphics device with a C++ core on AGG 2.4 (language-filter mismatch; the C++ needs Rinternals and the R graphics engine). Benchmark is the R script vignettes/ragg_performance.Rmd run on a GitHub Actions ubuntu-24.04 runner (rendered 2026-04-08; no CPU or flags): composite about 245 vs 320 ms against the anti-aliased cairo device (about 1.3x); the README's 40% has no backing figure, the vignette says about 33%.
- The rendered 2026-04-08 plots contradict the vignette prose: on clip paths cairo is about 1.6x faster (ragg about 87 ms vs about 55 ms, because drawShape re-rasterises the whole clip path per primitive via sbool_intersect_shapes_aa); text is about 4x faster in ragg (about 19 vs 81 ms), gradients about 140 vs 167 ms (not on par), masks about 8 vs 37 ms, patterns about 94 vs 410 ms, device open/close about 7.3 vs 3 ms. R's cairoFns.c confirms CAIRO_ANTIALIAS_NONE on fills for the non-anti-aliased cairo rows. The void_dev baseline is a single system.time run and the raster baseline draws 100 rasters against the 1 benchmarked; the composite advantage with the baseline removed is about 1.6x (derived from page data).

## Caveats and trade-offs

Language mismatch with the C++ filter: ragg is an R package. Its C++ core (src/ragg.h includes Rinternals.h and R_ext/GraphicsEngine.h) implements R's graphics-device API and cannot be called from plain C++ without R; the reusable C++ piece is the bundled AGG 2.4 rasterizer. Baseline is R's cairo device (grDevices png(type = 'cairo')), not Cairo called from C++, and both sides include R graphics-engine overhead. Numbers are first-party and shown only as ridge plots from a CI runner (no CPU model, no compiler flags); the README's 'up to 40%' has no backing figure and the vignette's '\~33%' is summary prose. Gains are smallest on fills because grDevices cairo does not anti-alias fills; non-anti-aliased cairo is faster on single primitives, and cairo is about twice as fast to open/close a device and slightly faster on non-rotated rasters. The vignette is excluded from the CRAN tarball (.Rbuildignore) and rendered only on the pkgdown site; the rendered copy is on the gh-pages branch.

R graphics-device package, not a standalone C++ API; the rasterizer is the AGG library (already catalogued as AGG 2.6) wrapped with FreeType/HarfBuzz text and libpng/libjpeg/libtiff output. Always anti-aliases fills, so the win is partly a quality difference.

## Maintenance

Actively maintained by Posit (ragg 1.5.2 on CRAN, last commit 2026-05-13, 184 stars), MIT-licensed with AGG 2.4 under a BSD licence, and safe to adopt for R graphics; its C++ is not reusable outside R.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark code is public (vignettes/ragg_performance.Rmd, bench::mark per device against png(type='cairo') with antialias none/gray/subpixel), but results exist only as ridge plots in the rendered article, built on a GitHub Actions ubuntu-24.04 x86_64 runner with no CPU model or compiler flags stated, and the \~33%/40% figures are first-party summary prose; C.
- **Verifier notes:** Benchmark code is the R script in vignettes/ragg_performance.Rmd; the machine is a GitHub Actions ubuntu-24.04 runner per the rendered article's session info (raw.githubusercontent.com gh-pages copy, since ragg.r-lib.org is blocked), CPU model unstated. Language should be 'R (C++ core on AGG 2.4)' via a decisions.json override, since 'language' is not a correctable field; the C++ filter mismatch is in caveats. CRAN was blocked (403), so CRAN usage figures were not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `license`, `stars_or_usage`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/r-lib/ragg/main/vignettes/ragg_performance.Rmd>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance.html>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-5-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-14-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-24-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/README.md>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/DESCRIPTION>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/LICENSE>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/LICENSE.note>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/.Rbuildignore>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/ragg.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/agg/include/agg_basics.h>
  - <https://github.com/r-lib/ragg>
  - <https://github.com/r-lib/ragg/commits/main>
- **Sources the enricher read:**
  - <https://github.com/r-lib/ragg>
  - <https://github.com/r-lib/ragg/commits/main>
  - <https://github.com/r-lib/ragg/issues?q=is%3Aissue+performance+OR+slow+OR+speed>
  - <https://github.com/r-lib/ragg/issues/210>
  - <https://github.com/r-lib/ragg/issues/154>
  - <https://github.com/r-lib/ragg/issues/131>
  - <https://github.com/r-lib/ragg/issues/103>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/README.md>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/DESCRIPTION>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/NEWS.md>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/vignettes/ragg_performance.Rmd>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/vignettes/ragg_quality.Rmd>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/ragg.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/AggDevice.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/rendering.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/text_renderer.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/init_device.h>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/Makevars.in>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/src/Makevars.win>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/configure>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/LICENSE.note>
  - <https://raw.githubusercontent.com/r-lib/ragg/main/.Rbuildignore>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance.html>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-3-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-11-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-22-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-24-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-25-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-26-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-27-1.png>
  - <https://raw.githubusercontent.com/r-lib/ragg/gh-pages/articles/ragg_performance_files/figure-html/unnamed-chunk-28-1.png>
  - <https://raw.githubusercontent.com/wch/r-source/trunk/src/library/grDevices/src/cairo/cairoFns.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/r-lib/ragg`) · [data/wave10/enrich/raw/github_com_r_lib_ragg.json](../../../data/wave10/enrich/raw/github_com_r_lib_ragg.json) (enrichment confidence 0.75)

</details>
