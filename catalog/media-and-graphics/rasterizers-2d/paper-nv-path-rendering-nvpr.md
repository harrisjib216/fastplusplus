# NV_path_rendering (NVpr)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C (OpenGL extension in the NVIDIA driver)` · `no license` · ⚪ unknown

> NVIDIA OpenGL extension for GPU path rendering; its peer-reviewed figure shows about 2-40x over Cairo and Skia's CPU rasterizer.

| | |
|---|---|
| **Beats** | Cairo 1.9.6, Skia (circa May 2010, CPU raster backend), Qt 4.5.x, Direct2D and the OpenVG 1.1 reference implementation (the nvpr_svg comparison backends in the NVprSDK) |
| **Claimed result** | Paper chart data (ACM TOG 2012, LaTeX and EPS in markkilgard/gpupathrender; GeForce 650, 'fast Core i7', 16 samples per pixel, SVG scenes at 100x100 to 1100x1100; derived from chart vector data): NV_path_rendering 2.7-40x faster than Cairo 1.9.6, 2.1-34x than Skia CPU, 1.6-78x than Skia Ganesh, 0.95-29x than Direct2D and 4.4-31x than WARP, ratios falling with window size; the clipped scene is 6.3-22x versus Cairo. The 105x figure (8.69 ms versus Cairo 909 ms at 1000x1000) is a separate GeForce 560M showcase. No Qt row in the chart; OpenVG compiled out of -xbenchmark. |
| **Workload** | GPU stencil-then-cover path rendering of SVG-like scenes, compared in the NVprSDK nvpr_svg demo and the SIGGRAPH Asia 2012 paper 'GPU-accelerated Path Rendering' (Kilgard and Bolz). |
| **Metric** | throughput |
| **Hardware** | GeForce 650 GPU and an unnamed 'fast Core i7' CPU for the ratio benchmarks; a GeForce 560M laptop for the Snail Bob (5 ms) and SIGGRAPH web page (4.8 ms) frame timings (all per search snippets of the paper) |
| **Links** | [benchmark](https://github.com/markkilgard/gpupathrender) |

## Verdict

The paper's performance figure was read from the authors' LaTeX source and its vector EPS on github.com/markkilgard/gpupathrender; the values are derived from the chart's vector data, so they are approximate. Setup: NV_path_rendering at 16 samples per pixel on a GeForce 650 with an unnamed 'fast Core i7', 12 SVG scenes, windows from 100x100 to 1100x1100. NVPR beats Cairo by 2.7x (Spikes, 100x100) to 40x (Cougar, 200x200), Skia's CPU raster by 2.1x to 34x, Skia Ganesh (GPU) by 1.6x to 78x, Direct2D hardware by 0.95x to 29x, and Direct2D WARP by 4.4x to 31x. Most ratios fall as the window grows: Tiger versus Cairo goes from 17x at 200x200 to 6.3x at 1100x1100. The 105x clipping showcase (8.69 ms versus Cairo's 909 ms at 1000x1000) is a separate figure from a Core i7 with a GeForce 560M laptop GPU; the chart's own clipped-tiger scene shows 6.3x to 22x versus Cairo.

## Use it when

- Static or retained vector content (SVG art, maps, UI, glyph runs) redrawn many times under changing transforms (zoom, rotation, projective warps) on NVIDIA GPUs, so the one-time bake is amortised
- Compositing 2D paths with 3D: depth-tested paths, paths in perspective, stencil-clipping 3D against paths, or custom fragment shaders on fills
- Content with exactly shared edges (Flash-style art) where coverage-to-alpha renderers show background bleeding: per-sample colour avoids conflation
- Desktop Windows or Linux apps that already own a compatibility-profile OpenGL context and target NVIDIA hardware only

## Skip it when

- Anything that must run on AMD, Intel, Apple or mobile GPUs, or under Vulkan, Direct3D or Metal: this is an NVIDIA OpenGL extension (the 2011 SDK deck lists no Mac support)
- Immediate-mode drawing that re-specifies paths every frame (browser canvas, dynamic charts): baking time is linear in path commands and is excluded from the benchmark loops, and the paper itself notes that browsers re-specify paths on every redraw
- Simple line-segment scenes at large window sizes against Direct2D hardware: in the paper's figure the Spikes scene falls to about 0.95x at 1100x1100 (Direct2D slightly faster), and on the GeForce 650 most ratios shrink as the window grows
- Memory-tight GPUs: quality depends on a multisampled colour plus stencil framebuffer. The 2011 deck calls 4 samples the bare minimum and 16x 'extremely memory intensive', and the paper's future work targets the memory footprint.
- New projects that need ecosystem support: Qt deprecated Shape.NvprRenderer in 5.12 and Qt 6 has no NVPR backend; Skia has dropped its NVPR backend (per the verifier)

## How it is fast

The technique is 'stencil, then cover'. Each path is baked once into resolution-independent GPU geometry: triangle-fan anchor geometry, Loop-Blinn quadratic and cubic discard triangles (cubics are subdivided into convex hulls), and conservative cover geometry. The stencil step accumulates per-sample winding numbers in the stencil buffer. The cover step rasterizes the cover geometry, shades the samples whose stencil value is non-zero and resets the stencil as it goes. Strokes use a quadratic Bezier stroke discard shader. Antialiasing comes from multisampling (16 samples per pixel in the benchmarks), and each sample keeps its own colour, which avoids conflation artifacts. The paper credits three hardware features: coarse stencil culling that rejects hundreds of pixels per clock, 8-bit stencil traffic that runs near memory-bus saturation, and a GPU front-end processor that switches between stencil and cover without driver revalidation, so many small paths stay GPU-bound.

## Compared with alternatives

Choose it only for an NVIDIA-only OpenGL application that needs paths composited with 3D, depth or custom shaders. For portable CPU rendering Blend2D wins nearly all configurations in the ETH thesis comparison, and Vello or Pathfinder are portable GPU options. NVPR's speedups were measured against 2010-2012 Cairo and Skia builds and a 2012 GPU, so they say little about today's Blend2D, Vello CPU or Skia Graphite.

## Integration

| | |
|---|---|
| **Form** | driver extension (OpenGL; nothing to link or vendor); SDK samples are a source-drop under NVIDIA's SDK licence |
| **Dependencies** | NVIDIA proprietary driver 275.33+ on GeForce 8 or later; a stencil-capable, multisampled OpenGL framebuffer; the SDK samples use GLEW and GLUT, and nvpr_svg bundles Cairo, Qt 4, Skia, FreeType, TinyXML and Boost 1.50 |
| **Minimum toolchain** | OpenGL 1.1+ (spec version 1 requires ARB_compatibility on OpenGL 3.x); SDK projects for Visual Studio 2008, 2010 and 2012 plus GNU make on Linux |
| **Platforms** | NVIDIA GPUs on Windows and Linux (the 2011 deck also lists FreeBSD and Solaris; no macOS) |
| **Thread safety** | Follows OpenGL context rules (calls go to the context current on the calling thread); nothing further documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The comparisons are not at identical output: NVPR runs at 16 samples per pixel while Cairo, Skia, Qt and Direct2D use coverage-to-alpha antialiasing, and the 2011 deck's numbers pit the GPU against a single CPU core
- The SDK sample code is under NVIDIA's SDK agreement (derivatives allowed with an attribution statement; NVIDIA may terminate the licence), not an OSI licence, and the renderer itself is closed
- The spec copy in the SDK (version 1, June 2011) is written against the OpenGL 3.2 compatibility profile and requires ARB_compatibility on 3.x; core-profile use relies on later spec revisions not read here
- nvpr_svg's benchmark.bat is stale (it runs gs_bezier.exe). The paper's 12-scene, 11-resolution sweep is the undocumented -xbenchmark mode in nvpr_svg.cpp, where OpenVG is compiled out as 'too slow to benchmark'.

## Known shortcomings

- Reference only: the NV_path_rendering driver is closed source; the nvpr_svg comparison harness (Cairo, Qt, Skia, Direct2D, OpenVG backends) survives only in SDK mirrors. The TOG 31(6) 2012 paper PDF is blocked here, so the numbers (GeForce 650 + Core i7, 8.69 ms vs Cairo 909 ms on the clipping scene) are snippet-only; Skia has since dropped its NVPR backend, so the comparison is historical.
- Retiered C to B (retier-27) on the paper's LaTeX and chart data in markkilgard/gpupathrender. The 105x clipping figure is a separate GeForce 560M showcase; the chart's clipped scene is 6.3-22x versus Cairo; the chart has no Qt row and OpenVG was compiled out of -xbenchmark. The nvpr_svg.cpp harness times CPU backends without the blit while the GPU time includes swap plus glFinish (vsync off); benchmark.bat is stale (runs gs_bezier.exe); Cairo 1.9.6 had a path-clipping bug per the SDK ReadMe; Qt 5.12 deprecated and Qt 6 removed the NvprRenderer; the renderer lives in NVIDIA's proprietary driver.

## Caveats and trade-offs

Paper-only entry for the research section. The paper PDF (developer.download.nvidia.com), the GTC 2012 slides and ResearchGate are blocked, so all numbers are from search-result snippets. NV_path_rendering is implemented inside NVIDIA's proprietary driver, so the renderer itself cannot be copied; only the SDK example code is public. An unofficial mirror of the July 2011 NVprSDK (github.com/victusfate/nvpr_demo, 1 star, no license file seen) carries nvpr_svg with -benchmark (best frames/second over 6-second intervals) and a key to benchmark the Qt/Cairo/Skia software renderer, but no recorded results. The CPU baselines are 2009-2010 versions (Skia's CPU raster path, not Ganesh/Graphite), the README notes Cairo 1.9.6 had a path-clipping bug, and the hardware is 2012-era. NVIDIA-only (GeForce 8 or later, driver 275.33+). [retier] Peer-reviewed but first-party (NVIDIA authors) and the renderer is inside NVIDIA's proprietary driver, so only the SDK example code is public (reference). Harness nvpr_svg.cpp: CPU timing excludes the blit (favours the baselines), GPU timing includes swap and glFinish with vsync off, baking excluded on both sides; benchmark.bat is stale. Cairo 1.9.6 had a path-clipping bug per the SDK ReadMe. Qt 5.12 deprecated and Qt 6 removed the NvprRenderer. 2012 hardware and library versions.

Needs an NVIDIA GPU and driver exposing GL_NV_path_rendering; vendor-specific extension, not usable on AMD or Intel; the NVprSDK samples are NVIDIA-distributed, not an OSI-licensed repo that was opened here.

## Maintenance

Shipped in NVIDIA drivers since 275.33 (June 2011); NVprSDK's last commit was February 2020. Qt deprecated its NVPR backend in 5.12 and removed it in Qt 6, and Skia dropped its backend, so treat it as a vendor-locked historical reference, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** The peer-reviewed paper (Kilgard and Bolz, 'GPU-accelerated Path Rendering', ACM TOG 31(6), SIGGRAPH Asia 2012) exists (ACM DOI 10.1145/2366145.2366191 and NVIDIA PDF in search results), and the comparison harness is real (nvpr_svg in an NVprSDK mirror has Cairo, Qt, Skia, Direct2D and OpenVG backends and a -benchmark mode), but the paper PDF is blocked and its numbers were seen only as search snippets, so C at most.
- **Retiered** C to B: Raised C to B: the enricher reached the paper itself (ACM TOG 31(6), 2012) as LaTeX source with vector EPS figures in github.com/markkilgard/gpupathrender and derived the ratio tables from the chart data, so the measurement is peer-reviewed and no longer snippet-only. At 16 samples per pixel on a GeForce 650 with a 'fast Core i7', NV_path_rendering is 2.7-40x faster than Cairo, 2.1-34x than Skia's CPU backend, 1.6-78x than Skia Ganesh, 0.95-29x than Direct2D and 4.4-31x than WARP, with ratios falling as the window grows. Corrections: the 105x clipping figure is a separate GeForce 560M showcase, the chart's clipped scene is only 6.3-22x versus Cairo, the chart has no Qt row and OpenVG was compiled out of -xbenchmark. The nvpr_svg.cpp harness times CPU backends without the blit (favouring them) and the GPU with swap plus glFinish, vsync off; baking is excluded on both sides; benchmark.bat is stale (runs gs_bezier.exe). Not A: the renderer lives in NVIDIA's proprietary driver.
- **Verifier notes:** Paper and comparison harness confirmed as real; numbers remain snippet-only, so C. A paper-access retier could move it to B. Skia has since dropped its NVPR backend, so the incumbent comparison is historical.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** paper tables (blocked)
- **Pages the verifier opened:**
  - <https://github.com/victusfate/nvpr_demo>
  - <https://github.com/victusfate/nvpr_demo/tree/master/nvpr_whitepaper>
  - <https://raw.githubusercontent.com/victusfate/nvpr_demo/HEAD/ReadMe.txt>
  - <https://raw.githubusercontent.com/victusfate/nvpr_demo/HEAD/nvpr_svg/ReadMe.txt>
- **Sources the enricher read:**
  - <https://github.com/markkilgard/NVprSDK>
  - <https://github.com/markkilgard/NVprSDK/commits>
  - <https://github.com/markkilgard/NVprSDK/tree/master/docs>
  - <https://github.com/markkilgard/NVprSDK/tree/master/nvpr_examples/nvpr_svg>
  - <https://github.com/markkilgard/NVprSDK/tree/master/nvpr_examples/nvpr_svg/skia>
  - <https://github.com/markkilgard/NVprSDK/tree/master/nvpr_examples/nvpr_svg/cairo>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/README.md>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/docs/An%20Introduction%20to%20NV_path_rendering.pdf>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/docs/NV_path_rendering%20FAQ.pdf>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/docs/Getting%20Started%20with%20NV_path_rendering.pdf>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/docs/GL_NV_path_rendering.txt>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/nvpr_svg.cpp>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/ReadMe.txt>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/benchmark.bat>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/skia/renderer_skia.cpp>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/cairo/renderer_cairo.cpp>
  - <https://raw.githubusercontent.com/markkilgard/NVprSDK/HEAD/nvpr_examples/nvpr_svg/cairo/scene_cairo.cpp>
  - <https://github.com/markkilgard/gpupathrender>
  - <https://github.com/markkilgard/gpupathrender/tree/master/paper>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/gpupathrender.tex>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/abstract.tex>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/approach.tex>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/discuss.tex>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/future.tex>
  - <https://raw.githubusercontent.com/markkilgard/gpupathrender/HEAD/paper/nvpr_performance.eps>
  - <https://raw.githubusercontent.com/qt/qtdeclarative/5.15/src/quickshapes/qquickshape.cpp>
  - <https://raw.githubusercontent.com/qt/qtdeclarative/5.15/src/quickshapes/qquickshapenvprrenderer.cpp>
  - <https://raw.githubusercontent.com/qt/qtdeclarative/dev/src/quickshapes/qquickshape.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `paper:nv-path-rendering-nvpr`) · [data/wave10/enrich/raw/paper_nv_path_rendering_nvpr.json](../../../data/wave10/enrich/raw/paper_nv_path_rendering_nvpr.json) (enrichment confidence 0.7)

</details>
