# Fast UI Draw (FastUIDraw)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🔴 abandoned

> Intel's archived GPU-only C++ canvas (OpenGL/GLES); author's clip-heavy demo ran about 5-8x Skia GL's frame rate in 2016.

| | |
|---|---|
| **Beats** | Skia (OpenGL backend), Cairo (CPU renderer and OpenGL backend), Qt |
| **Claimed result** | Snippet only (XDC 2016 slides on x.org, egress-blocked, not opened). painter-cells frame rate normalized to Cairo's CPU renderer (1.00): at 600 cells FastUIDraw 9.33, Skia GL 1.91, Cairo Xlib 1.60, Qt Raster 1.01, Qt GL 0.76, Qt Native 0.29, Cairo GL 0.27; at 1250 cells FastUIDraw 11.11, Qt Raster 1.50, Skia GL 1.36, Cairo Xlib 1.25, Qt GL 0.45, Cairo GL 0.15, Qt Native 0.14. The XDC 2016 abstract page (also blocked) gives a second set: FastUIDraw 9.20, Skia GL 1.68, Cairo Xlib 1.60, Qt Raster 0.98, Qt GL 0.66, Qt Native 0.26, Cairo GL 0.25. Against Skia's GL backend that is about 4.9x at 600 cells, 8.2x at 1250 cells and 5.5x in the abstract's set (derived from snippet data); the 9x figure is against Cairo's CPU renderer. |
| **Workload** | painter-cells demo (demos/painter_cells in the repo): a table of cells, each with a background, a rotating and moving image and a rotating and moving line of text clipped to the cell, with anti-aliased stroked cell boundaries; the author ported it to Qt (Raster, GL, Native), Cairo (CPU, GL, Xlib) and Skia GL and compared frame rates at 600 and 1250 cells, normalized to Cairo CPU. |
| **Metric** | throughput |
| **Hardware** | Unnamed laptop with an Intel GPU, described as 3+ years old in 2016 (search snippet of the blocked XDC 2016 abstract page); GPU model, driver, OS and build flags not given. |
| **Adoption** | 617 stars |
| **Last commit** | 2023-01-07 |
| **Links** | [repository](https://github.com/intel/fastuidraw) · [benchmark](https://www.x.org/wiki/Events/XDC2016/Program/fast_ui_draw.pdf) |

## Verdict

The only numbers are first-party and known only from search snippets of Kevin Rogovin's XDC 2016 slides. In the painter-cells demo, frame rate normalized to Cairo's CPU image surface was FastUIDraw 9.33 vs Skia GL 1.91 at 25x12 cells and 11.11 vs 1.36 at 50x25 cells, on an unnamed Intel-GPU laptop, which is about 4.9x and 8.2x over Skia GL (derived from snippet data). Contrary to the record's caveat, the Qt, Cairo (xlib, image, GL) and Skia GL ports and the run scripts are public on the repo's with_ports_of_painter-cells branch (last updated 2018-12-20). The scripts ran 1920x1080 or 1920x1200 fullscreen, swap_interval 0, 25x12 cells, a 4000x2000 table, table and cells rotating and clipped, and images from /usr/share/games/blobwars/gfx. The Skia port's Makefile gives gn args (is_official_build=true, clang) and a tested Skia commit, 01979132133e. Two limits remain: the hardware is unnamed, and the branch's 2018-era Skia API (GrContext::MakeGL) is newer than the 2016 runs. The ports are also not fully equivalent. The Skia port calls SkCanvas::drawText on UTF-8 strings every frame, while FastUIDraw draws pre-formatted GlyphSequences. The Cairo port pre-lays out cairo_glyph_t arrays, and the Qt port was given QGlyphRun 'to make the comparison more fair'. That makes the Skia GL ratio somewhat favorable to FastUIDraw.

## Use it when

- UI or canvas scenes on desktop-class GPUs that change clip and transform state very often (many nested, clipped, rotating widgets per frame), which is the painter-cells workload behind the published numbers.
- Linux or Windows (MinGW) apps that already own a GL 3.3 or GLES 3.0 context and want a 2D layer that issues very few draw calls.
- Intel GPUs from Ivy Bridge on with recent Mesa or Intel Windows drivers, which the README says have every extension needed for all blend modes at full speed.
- Studying or forking a GPU canvas design: uber-shader with packed data store, depth-buffer clipping, and custom shader chaining, all MPL-2.0.

## Skip it when

- Anything needing support or security fixes: Intel archived the repo on 2023-01-07 and accepts no patches. The last code commit is 2019-12-20, and questions about maintenance and Chromium integration (#61, #50) were never answered.
- Machines without a real GPU driver: issue #19 measured 1.9 fps with Mesa's SWR software rasterizer against 32.7 fps for Cairo on an i3-4160 at 1280x1280.
- Many short-lived or freshly built paths per frame. Issue #49 reported about 7x the CPU load of nanovg (around 29% CPU) on a line-drawing test at gcc 7.4 -O3, and it was closed without a recorded fix. The fast path assumes geometry is tessellated once and reused.
- macOS (system GL headers unusable and the GL there is deprecated), WebGPU, Vulkan or Metal targets: there are only GL and GLES backends.
- When you need Skia-level text shaping, color management, PDF or SVG output, or a CPU fallback: none of these is provided.

## How it is fast

Everything is drawn by one uber-shader. Per-item state (transform, clip equations, brush, shader IDs) is packed into a data store, a texture buffer object by default, and each vertex reads a header from it. Canvas state changes therefore do not become GL state changes, and the README says only a blend-mode change forces a new pipeline state, so a frame needs only a handful of draw calls. Rectangle clip-in uses hardware clip planes (gl_ClipDistance by default). Clip-out and path clips use the depth buffer as an occluder (depth test GL_GEQUAL, z incremented per item), so changing the clip costs little more than drawing one occluding shape. Path tessellation, stroking geometry and glyph data are built once and reused, and images and glyphs live in GPU atlases so they cause no draw breaks.

## Compared with alternatives

Pick it over Pathfinder 3 or vger only if you need a full canvas feature set (clip-out by path, advanced blend modes, custom shaders) on GL and can live with an archived C++ codebase. For CPU rendering or maintained projects, Blend2D, Skia or ThorVG are the safer choices, and Rive Renderer and Vello are the maintained GPU-side options.

## Integration

| | |
|---|---|
| **Form** | shared lib (libFastUIDraw plus libFastUIDrawGL or libFastUIDrawGLES, release and debug variants, pkg-config files and a fastuidraw-config script) |
| **Dependencies** | FreeType; Khronos GL/GLES headers (glcorearb.h, khrplatform.h) supplied by the user; flex and perl at build time; SDL2 and SDL2_image for demos only; doxygen for docs |
| **Minimum toolchain** | C++11 (-std=c++11), GNU Make, g++ (clang said to work); release libraries build at -O3 -fstrict-aliasing |
| **Platforms** | Linux and MinGW32/64 under MSYS2 per README; macOS only with copied Khronos headers ('Yes, this is a hack'); needs GL 3.3 or GLES 3.0, and blend modes beyond Porter-Duff need framebuffer fetch or fragment-shader interlock or ordering |
| **Thread safety** | Not documented beyond notes: a Painter is a heavy, reference-counted object bound to a GL context, and shaders registered from a thread are not usable in that thread until the next begin(). Treat one Painter as single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- Debug and release libraries must not be mixed; the README tells you to take matching flags from pkg-config or fastuidraw-config.
- Benchmark mode (num_frames) times the gap between draw_frame calls, which includes buffer swap. Vsync is only disabled if you pass swap_interval 0 or set vblank_mode=0 on Mesa. The ports branch's bench.sh echoes vblank_mode=0 but actually runs with a misspelled 'vlank_mode=0'.
- Images not on the atlas become bound textures when bindless texturing is missing, which breaks batching. The demo itself warns 'large performance impact expected'.
- The first frames compile the uber-shader in the GL driver. Skip them (num_skip_frames) before timing anything.

## Known shortcomings

- Numbers exist only in search snippets of the blocked x.org XDC 2016 slides and abstract (normalised to Cairo CPU: FastUIDraw 9.33 against Skia GL 1.91 at 600 cells and 11.11 against 1.36 at 1250 cells, 4.9-8.2x over Skia GL derived from snippet data) on an unnamed Intel-GPU laptop; the Qt, Cairo and Skia ports used are not public. Archived 2023-01-07 with the last code commit on 2019-12-20.
- Enricher (e109, 2026-10-05): the Qt, Cairo and Skia painter-cells ports are public on branch with_ports_of_painter-cells (2018-12-20) with example-benchmark.sh, bench.sh (typo 'vlank_mode=0'), Skia gn args and Skia commit 01979132133e, correcting the verifier; still C because CPU and GPU are unnamed, the numbers are snippet-only and the ports postdate the 2016 runs. Fairness flaw: the Skia port calls drawText every frame while FastUIDraw, Cairo and Qt pre-lay glyphs, so the Skia GL ratio favours FastUIDraw. Issue #19: Mesa SWR 1.9 fps vs Cairo 32.7; issue #49: about 7x nanovg's CPU load, no fix. Archived 2023-01-07.

## Caveats and trade-offs

Snippet only: the numbers come from search-result text of Kevin Rogovin's XDC 2016 slides (x.org/wiki/Events/XDC2016/Program/fast_ui_draw.pdf) and the XDC 2016 abstract page; x.org, Phoronix, mail-archive (webkit-dev thread) and the Chromium graphics-dev post are all egress-blocked here, so nothing was read in full. First-party, single clipping-heavy demo, ten years old (Skia, Cairo and Qt of 2016). The repo's demos/painter_cells has a benchmark mode (num_frames, num_skip_frames), but the Qt, Cairo and Skia ports used for comparison are not in the repo or in the author's public forks (krogueintel lists skia.fastuidraw and qtwebkit.fastuidraw forks with no painter-cells code shown). The headline 9x compares GPU rendering against Cairo's CPU renderer; against Skia GL the win is about 4.9x to 8.2x depending on cell count (derived from snippet data). A search summary of a Hacker News thread says the benchmarks were not representative. Intel archived the repository on 2023-01-07 with a discontinuation notice (no maintenance, bug fixes or patches accepted); the last code commit is 2019-12-20. Requires GL 3.3 or GLES 3.0 and, for non-Porter-Duff blend modes, framebuffer-fetch or fragment-shader-interlock extensions. [retier] Snippet only: the numbers come from search-result text of Kevin Rogovin's XDC 2016 slides and the XDC 2016 abstract page (x.org, Phoronix, mail-archive and the Chromium graphics-dev post are egress-blocked here). First-party, single clipping-heavy demo, ten years old (Skia, Cairo and Qt of 2016). The Qt, Cairo and Skia painter-cells ports are public on the repo branch with_ports_of_painter-cells (2018-12-20: qt_painter_cells, cairo_painter_cells, skia_painter_cells, example-benchmark.sh, bench.sh, Skia gn args, Skia commit 01979132133e), but they postdate the 2016 runs and bench.sh has a typo ('vlank_mode=0'). Fairness flaw: the Skia port calls drawText every frame while FastUIDraw, Cairo and Qt pre-lay glyphs, so the Skia GL ratio favours FastUIDraw. The headline 9x compares GPU rendering against Cairo's CPU renderer; against Skia GL the win is about 4.9x to 8.2x (derived from snippet data). Issue #19: Mesa SWR 1.9 fps vs Cairo 32.7; issue #49: about 7x the CPU load of nanovg, never fixed. Intel archived the repository on 2023-01-07; last code commit 2019-12-20. Requires GL 3.3 or GLES 3.0 and, for non-Porter-Duff blends, framebuffer-fetch or fragment-shader-interlock.

GPU-only canvas renderer: requires OpenGL 3.3 (optional OpenGL 4 extensions give better performance). Clipping and most state handling are left to the GPU, which is the source of the win on clip-heavy scenes. Repository is archived and Intel states it has ceased development.

## Maintenance

Abandoned: archived by Intel on 2023-01-07 with a discontinuation notice (last code change 2019-12-20). It is MPL-2.0 and copyable, but it is a large GL-specific codebase you would have to own outright.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers that exist only in search snippets of the author's blocked XDC 2016 pages (x.org slides PDF and abstract page): painter-cells frame rates normalized to Cairo CPU, FastUIDraw 9.33 vs Skia GL 1.91 at 600 cells and 11.11 vs 1.36 at 1250 cells, on an unnamed laptop with an Intel GPU. The repo's demos/painter_cells/main.cpp has a benchmark mode (num_frames, num_skip_frames, per-frame times), but the Qt, Cairo and Skia ports, GPU model, driver and build flags are not public here, so C is the cap.
- **Verifier notes:** Kept at C on the blaze/ctx precedent (two consistent snippet sources, x.org slides and abstract page); if the orchestrator applies the reachable-page rule used for resvg and muSkia in this batch, it would drop to D. Metadata checked on github.com: MPL-2.0, 617 stars, 54 forks, archived 2023-01-07 (that commit is the archive notice; last code commit 2019-12-20), abandoned is right. The x.org PDF in benchmark_url was found by WebSearch and was not opened (EGRESS_BLOCKED), so it is not in urls_opened.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party XDC 2016 slides (snippet)
- **Pages the verifier opened:**
  - <https://github.com/intel/fastuidraw>
  - <https://raw.githubusercontent.com/intel/fastuidraw/HEAD/README.md>
  - <https://github.com/intel/fastuidraw/commits/master>
  - <https://github.com/intel/fastuidraw/tree/master/demos>
  - <https://github.com/intel/fastuidraw/tree/master/docs>
  - <https://github.com/intel/fastuidraw/tree/master/demos/painter_cells>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/main.cpp>
  - <https://github.com/krogueintel?tab=repositories>
  - <https://github.com/krogueintel/skia.fastuidraw>
- **Sources the enricher read:**
  - <https://github.com/intel/fastuidraw>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/README.md>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/main.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/cell.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/cell.hpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/table.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/painter_cells/cell_group.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/common/sdl_demo.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/common/sdl_painter_demo.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/demos/common/PainterWidget.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/docs/documentation/main.doxy>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/inc/fastuidraw/gl_backend/painter_engine_gl.hpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/inc/fastuidraw/painter/painter.hpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/Makefile>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/make/Makefile.settings.mk>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/make/Makefile.base.pre.mk>
  - <https://raw.githubusercontent.com/intel/fastuidraw/master/make/Makefile.base.lib.mk>
  - <https://github.com/intel/fastuidraw/tree/master/docs>
  - <https://github.com/intel/fastuidraw/tree/master/docs/documentation>
  - <https://github.com/intel/fastuidraw/issues?q=is%3Aissue>
  - <https://github.com/intel/fastuidraw/issues/19>
  - <https://github.com/intel/fastuidraw/issues/49>
  - <https://github.com/intel/fastuidraw/issues/50>
  - <https://github.com/intel/fastuidraw/issues/61>
  - <https://github.com/intel/fastuidraw/branches/all>
  - <https://github.com/intel/fastuidraw/tree/with_ports_of_painter-cells>
  - <https://github.com/intel/fastuidraw/tree/with_ports_of_painter-cells/demos>
  - <https://github.com/intel/fastuidraw/tree/with_ports_of_painter-cells/skia_painter_cells>
  - <https://github.com/intel/fastuidraw/tree/with_ports_of_painter-cells/cairo_painter_cells>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/README.painter_cells.ports.txt>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/bench.sh>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/benchmark-switch.sh>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/example-benchmark.sh>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/example-benchmark-many-options-seperate.sh>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/CLIPPING.txt>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/skia_painter_cells/Makefile>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/skia_painter_cells/sdl_skia_demo.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/skia_painter_cells/cell.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/skia_painter_cells/main.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/skia_painter_cells/PainterWidget.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/cairo_painter_cells/Makefile>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/cairo_painter_cells/sdl_cairo_demo.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/cairo_painter_cells/cell.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/cairo_painter_cells/main.cpp>
  - <https://raw.githubusercontent.com/intel/fastuidraw/with_ports_of_painter-cells/cairo_painter_cells/text.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/intel/fastuidraw`) · [data/wave10/enrich/raw/github_com_intel_fastuidraw.json](../../../data/wave10/enrich/raw/github_com_intel_fastuidraw.json) (enrichment confidence 0.7)

</details>
