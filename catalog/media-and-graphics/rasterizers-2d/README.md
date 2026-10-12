# 2D rasterizers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md)</sub>

**What these beat:** Skia, Cairo, Blend2D  
**40 entries:** 3 tier A · 9 tier B · 22 tier C · 6 tier D · 33 copyable, 7 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**tiny-skia**](linebender-tiny-skia.md) | Pure-Rust port of Skia's CPU raster pipeline; about 1.7-2.3x faster than cairo on x86 overall, slower on solid rect fills. | **A** | Rust | BSD-3-Clause | 🟢 active |
| 2 | [**Marlin renderer (Java 2D)**](bourgesl-marlin-renderer.md) | Pure-Java antialiasing shape rasterizer for Java 2D that replaced Pisces and Ductus; OpenJDK's default renderer since JDK 9. | **A** | Java | GPL-2.0-only WITH… | 🟢 active |
| 3 | [**pixman (SIMD bilinear fast paths: SSE2, NEON, RVV)**](gitlab-freedesktop-org-pixman-pixman.md) | Pixman's hand-written SIMD bilinear fetchers (SSE2, NEON, RISC-V RVV) beat its own scalar C paths by 1.5x to 11x. | **A** | C | MIT | 🟢 active |
| 4 | [**JUCE software renderer (juce_graphics)**](juce-framework-juce.md) | JUCE's CPU path rasterizer (EdgeTable + SWAR pixel blending); about 1.7x Skia and 2.9x Cairo single-threaded on M1 Pro. | **B** | C++ | AGPL-3.0 | 🟢 active |
| 5 | [**MuPDF**](artifexsoftware-mupdf.md) | Artifex's C PDF/XPS/EPUB engine; about 2.5x faster text extraction than poppler's pdftotext and 2x faster image extraction than PDFium. | **B** | C | AGPL-3.0 | 🟢 active |
| 6 | [**Blend2D**](blend2d-blend2d.md) | Zlib-licensed C/C++ CPU 2D vector renderer with JIT-compiled pipelines; about 4x Skia's and 7x Cairo's raster throughput. | **B** | C++ | Zlib | 🟢 active |
| 7 | [**PDFium**](pdfium-googlesource-com-pdfium.md) | Google's C++ PDF engine behind Chromium's viewer; about 2.5x faster text extraction than Poppler's pdftotext. | **B** | C++ | BSD-3-Clause AND Apache-2.0 | 🟢 active |
| 8 | [**Poppler**](poppler-freedesktop-org.md) | xpdf-derived C++ PDF library and pdftotext tool; about 19x faster text extraction than pure-Python pdfminer.six. | **B** | C++ | GPL-2.0-or-later | 🟢 active |
| 9 | [**raqote**](jrmuizel-raqote.md) | Small pure-Rust CPU 2D rasterizer built on Skia-style 4x4 supersampling. Its path fills beat Cairo's image surface on an M1 Pro; overall it does not beat Skia. | **B** | Rust | BSD-3-Clause | 🟡 stale |
| 10 | [**muSkia Skia optimizer (Semantics for 2D Rasterization)**](paper-muskia-skia-optimizer-semantics-for-2d-rasterization.md) | Lean-verified peephole optimizer for Skia command streams; 1.12x geomean raster speedup over Skia Graphite on Chrome-generated pictures. | **B** | Lean | no license (study only) | ⚪ unknown |
| 11 | [**NV_path_rendering (NVpr)**](paper-nv-path-rendering-nvpr.md) | NVIDIA OpenGL extension for GPU path rendering; its peer-reviewed figure shows about 2-40x over Cairo and Skia's CPU rasterizer. | **B** | C | no license (study only) | ⚪ unknown |
| 12 | [**Anti-Grain Geometry (AGG 2.6)**](ghaerr-agg-2-6.md) | Classic scalar C++ template 2D rasterizer; an independent bl_bench run puts it \~1.2x Skia and \~2.3x Cairo single-threaded. | **B** | C++ | BSD-3-Clause (study only) | 🔴 abandoned |
| 13 | [**SFML**](sfml-sfml.md) | C++ window, input, audio and sprite library; one hobby benchmark draws static sprites 1.29x faster than raylib, slower than SDL2. | **C** | C++ | Zlib | 🟢 active |
| 14 | [**TFT_eSPI**](bodmer-tft-espi.md) | Arduino TFT driver plus drawing library for ESP32, RP2040, ESP8266 and STM32; 1.3x to 4.7x faster than Adafruit_GFX on an ILI9341 at 40 MHz. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 15 | [**Vello CPU (sparse strips renderer)**](linebender-vello.md) | Rust CPU 2D vector renderer (sparse strips, SIMD, optional threads); about 2.4x Skia and 4x Cairo raster speed on M1. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 16 | [**resvg**](linebender-resvg.md) | Pure-Rust static-SVG renderer with a C API; benchmarks faster than librsvg on icon sets, much slower on clip-path-heavy files. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 17 | [**ThorVG**](thorvg-thorvg.md) | MIT C++ SVG/Lottie vector engine; its CPU renderer averaged 2.9x Skia raster fps on 5k-shape scenes (4 threads vs 1). | **C** | C++ | MIT | 🟢 active |
| 18 | [**LovyanGFX**](lovyan03-lovyangfx.md) | Embedded display driver and drawing library for ESP32-class MCUs; 1.3x to 4.6x faster than Adafruit_GFX on an ILI9341 at 40 MHz SPI. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 19 | [**LunaSVG**](sammycage-lunasvg.md) | Small C++17 SVG 1.1/Tiny 1.2 renderer on the plutovg rasterizer; converts icons to PNG about 2x faster than cairosvg through Python. | **C** | C++ | MIT | 🟢 active |
| 20 | [**Rive Renderer (rive-runtime)**](rive-app-rive-runtime.md) | Rive's C++ runtime and GPU vector renderer (Metal, Vulkan, D3D, GL); vendor claims 66x Skia on animated tiles. | **C** | C++ | MIT | 🟢 active |
| 21 | [**Arduino_GFX (GFX Library for Arduino)**](moononournation-arduino-gfx.md) | Arduino display library for about 40 panel controllers and many buses; 1.2x-5.2x faster than Adafruit_GFX on an ESP32 SPI ILI9341. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 22 | [**vkvg**](jpbruyere-vkvg.md) | Cairo-style 2D vector library in C on Vulkan; the author's chart shows it beating Cairo's GL ES3 backend on lines, circles and stars. | **C** | C | MIT | 🟢 active |
| 23 | [**libRSVG**](gnome-librsvg.md) | GNOME's Rust SVG renderer onto Cairo; beat resvg 0.8.0 on blur- and clip-heavy icons, lost on simple ones. | **C** | Rust | LGPL-2.1-or-later | 🟢 active |
| 24 | [**vger (Audulus)**](audulus-vger.md) | Small Metal GPU renderer for immediate-mode UIs (Apple only); its author reports 120 fps where nanovg managed 30 fps. | **C** | Objective-C++ and Metal | MIT | 🟢 active |
| 25 | [**ragg**](r-lib-ragg.md) | R raster graphics devices (PNG/JPEG/TIFF/WebP) on AGG 2.4; about 1.3x faster than R's anti-aliased cairo png() on a composite ggplot2. | **C** | R | MIT; bundled AGG 2.4… | 🟢 active |
| 26 | [**tiny-skia-cpp**](jwmcglynn-tiny-skia-cpp.md) | C++20 port of Rust tiny-skia (Skia-subset CPU rasterizer) with AVX2/NEON backends; first-party 1.2-1.9x faster than the Rust original. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 27 | [**NanoSVG2 (RudjiGames fork)**](rudjigames-nanosvg2.md) | Copy of the two-header NanoSVG parser and rasterizer with SSE2 blending and span-delta coverage, 2.5-3.7x faster than its own previous rasterizer. | **C** | C | Zlib | 🟢 active |
| 28 | [**stilus**](timzifer-stilus.md) | Pure-Go sparse 2D rasterizer; 2.0x x/image/vector on 20k short strokes (first-party); 477x hatch figure is harness-inflated. | **C** | Go | MIT | 🟢 active |
| 29 | [**Blaze (aurimasg/blaze)**](aurimasg-blaze.md) | Research-grade multi-threaded CPU rasterizer for solid-color path fills; the author reports 2.6x faster than multi-threaded Blend2D (2023 version) on an M1 Max. | **C** | C++ | MIT | 🟡 stale |
| 30 | [**ctx (2D vector rasterizer and terminal by Oyvind Kolas)**](facsimiles-ctx.md) | Portable C 2D vector rasterizer (HTML5-canvas-style API, one generated header) that wins many heats against cairo and Qt6 but loses most to Blend2D. | **C** | C | LGPL-3.0-or-later… | 🟡 stale |
| 31 | [**Fast UI Draw (FastUIDraw)**](intel-fastuidraw.md) | Intel's archived GPU-only C++ canvas (OpenGL/GLES); author's clip-heavy demo ran about 5-8x Skia GL's frame rate in 2016. | **C** | C++ | MPL-2.0 | 🔴 abandoned |
| 32 | [**GPU scanline path rendering (Li, Hou, Zhou 2016)**](mochimazui-gpu-scanline-path-rendering.md) | Research code for the SIGGRAPH Asia 2016 CUDA and OpenGL scanline path renderer; the abstract claims about 2.5x over prior GPU path renderers. | **C** | C++ | MIT | 🔴 abandoned |
| 33 | [**ImageSharp.Drawing**](sixlabors-imagesharp-drawing.md) | Managed C# 2D vector drawing on ImageSharp with a band-parallel CPU rasterizer and an optional WebGPU backend; the vendor reports 2.4x faster than single-threaded… | **C** | C# | Six Labors Split License… (study only) | 🟢 active |
| 34 | [**scanx**](srwiley-scanx.md) | Pure-Go anti-aliasing scanner for rasterx/oksvg that writes spans straight into image.RGBA; 1.7-3.2x faster than scanFT on the author's icon benchmark. | **C** | Go | FTL OR GPL-2.0-or-later on… (study only) | 🔴 abandoned |
| 35 | [**Pathfinder 3**](servo-pathfinder.md) | Rust GPU rasterizer for glyphs and vector paths (OpenGL, Metal, WebGL 2); claims to match or beat CPU rasterizers, with no numbers. | **D** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 36 | [**tdewolff/canvas**](tdewolff-canvas.md) | Pure-Go vector drawing library (paths, booleans, text, raster/PDF/SVG/EPS output); claims 2x over Inkscape/Cairo, no published numbers. | **D** | Go | MIT (Fribidi component is… | 🟢 active |
| 37 | [**TGFX (Tencent Graphics)**](tencent-tgfx.md) | Tencent's GPU-only C++17 2D renderer (PAG's engine), claimed 10-16x more animated rectangles per frame than Skia Ganesh m136. | **D** | C++ | BSD-3-Clause | 🟢 active |
| 38 | [**scany (multi-threaded scanner, srwiley)**](srwiley-scany.md) | Pure-Go CL-AA antialiasing scanner for rasterx/oksvg; single-thread parity with ScanFT claimed, multi-thread speedup claimed, nothing measured. | **D** | Go | MIT | 🔴 abandoned |
| 39 | [**plutovg**](sammycage-plutovg.md) | Small MIT C 2D vector library with a Cairo-like canvas API; no published speed comparison against Cairo, Skia or Blend2D. | **D** | C | MIT (study only) | 🟢 active |
| 40 | [**Rasterizer (mindbrix)**](mindbrix-rasterizer.md) | Metal GPU 2D vector renderer (paths, strokes, gradients, clips, SVG/PDF) for macOS and iOS; claims 'up to 60x faster than the CPU', unmeasured. | **D** | C++ | Custom 'personal use zlib… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
