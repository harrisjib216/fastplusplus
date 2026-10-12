# Font shaping and text layout

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md)</sub>

**What these beat:** HarfBuzz, FreeType  
**26 entries:** 1 tier A · 3 tier B · 20 tier C · 2 tier D · 24 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Fontations (skrifa / read-fonts)**](googlefonts-fontations.md) | Google's memory-safe Rust OpenType stack (read-fonts, skrifa); mostly 1.1-1.6x slower than HarfBuzz's own OT font functions. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**Typst**](typst-typst.md) | Rust typesetting system (markup language, compiler, CLI) that built mail-merge PDFs 3-5x faster than pdfLaTeX in one shootout. | **B** | Rust | Apache-2.0 | 🟢 active |
| 3 | [**harfbuzz**](harfbuzz-harfbuzz.md) | The standard OpenType/AAT text shaping engine (C++11, no C++ standard library); 1.76x geomean faster than its Rust port rustybuzz. | **B** | C++ | MIT-Modern-Variant | 🟢 active |
| 4 | [**Parley**](linebender-parley.md) | Pure-Rust rich-text layout (fallback, bidi, shaping, line breaking); 2.4-9x faster than cosmic-text on paragraph-per-layout workloads. | **B** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 5 | [**fontdue**](mooman219-fontdue.md) | Pure-Rust, no_std TrueType/OpenType glyph rasterizer and simple layout; first-party plots show 2.3x-11x lower per-glyph latency than FreeType. | **C** | Rust | MIT OR Apache-2.0 OR Zlib | 🟢 active |
| 6 | [**kb_text_shape**](jimmylefevre-kb.md) | Single-header C library for Unicode segmentation and OpenType shaping; claimed faster than HarfBuzz, measured 2-160x slower independently. | **C** | C | Zlib | 🟢 active |
| 7 | [**ttf-parser**](harfbuzz-ttf-parser.md) | Safe, zero-allocation Rust font parser with a C API; extracts unscaled glyph outlines 1.3-5x faster than FreeType's FT_Load_Glyph path. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 8 | [**Canvas-Txt v5**](geongeorge-canvas-txt.md) | Canvas 2D text-box layout for JavaScript that wraps text about 9-11x faster than canvas-hypertxt's measuring mode by caching word widths. | **C** | TypeScript | MIT | 🟢 active |
| 9 | [**ab_glyph**](alexheretic-ab-glyph.md) | Pure-Rust glyph loading, scaling, positioning and rasterization crate; rewrite of rusttype with cheaper per-glyph layout, especially for CFF fonts. | **C** | Rust | Apache-2.0 | 🟢 active |
| 10 | [**hypher**](typst-hypher.md) | Allocation-free Rust Knuth-Liang hyphenator with patterns embedded as automata; about 2x faster per word than the hyphenation crate. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 11 | [**text-shaper**](wiedymi-text-shaper.md) | Pure-TypeScript OpenType shaper and rasterizer; about 1.2-1.5x harfbuzzjs (WASM) on simple-script shaping under Bun. | **C** | TypeScript | MIT | 🟢 active |
| 12 | [**displaywidth**](clipperhouse-displaywidth.md) | Go monospace display-width and truncation library; 1.6-3.3x faster than go-runewidth v0.0.23 in its own benchmarks, zero allocations. | **C** | Go | MIT | 🟢 active |
| 13 | [**uniwidth**](unilibs-uniwidth.md) | Pure-Go terminal cell-width library; CI shows 1.1-52x faster StringWidth than go-runewidth v0.0.19, with width bugs on symbols. | **C** | Go | MIT | 🟢 active |
| 14 | [**TiTanF**](hoteira-titanf.md) | Zero-dependency no_std Rust TrueType rasterizer; 1.5-3.5x faster than RustType and ab_glyph, slower than Fontdue below 200px. | **C** | Rust | MIT | 🟢 active |
| 15 | [**sigilbuzz**](oneiriq-sigilbuzz.md) | Pure-Rust, no_std HarfBuzz-API text shaper with an hb_\* C library; faster than rustybuzz on Latin/Hebrew only, slower on complex scripts. | **C** | Rust | Apache-2.0 | 🟢 active |
| 16 | [**Typr.js**](photopea-typr-js.md) | Small browser JavaScript font parser (TTF/OTF/TTC/WOFF) that claims 2x-5x faster parsing than opentype.js, largely by parsing less up front. | **C** | JavaScript | MIT | 🟡 stale |
| 17 | [**uWrap**](leeoniya-uwrap.md) | Sub-2KB TypeScript Canvas2D line-wrap counter for virtualized lists; 7.7-18x faster than canvas-hypertxt in the author's browser runs. | **C** | TypeScript | MIT | 🟡 stale |
| 18 | [**msdfgl**](nyymanni-msdfgl.md) | OpenGL shader port of Chlumsky's MSDF glyph generator; first-party chart shows 60x-132x faster than single-threaded msdfgen on one laptop. | **C** | C | MIT | 🟡 stale |
| 19 | [**canvas-hypertxt**](glideapps-canvas-hypertxt.md) | Zero-dependency JavaScript line breaker for HTML5 canvas text; up to 9.8x faster than canvas-txt 3.x (19x with HyperWrapping). | **C** | JavaScript | MIT | 🟡 stale |
| 20 | [**uwcwidth**](z4jc-uwcwidth.md) | Cython wcwidth/wcswidth for Python with Unicode 16 emoji rules; beats pure-Python wcwidth 0.2.13 by 18-42x on short strings. | **C** | Cython | MIT | 🟡 stale |
| 21 | [**font-rs**](raphlinus-font-rs.md) | Small Rust TrueType glyph rasterizer (dense accumulation buffer plus prefix sum); 2016 author numbers claim 4-7.6x over FreeType 2.6.5. | **C** | Rust | Apache-2.0 | 🔴 abandoned |
| 22 | [**otfcc**](caryll-otfcc.md) | Archived C library and CLI pair that dumps OpenType fonts to JSON and builds them back, claimed far faster than ttx and makeotf. | **C** | C | Apache-2.0 | 🔴 abandoned |
| 23 | [**SixLabors.Fonts**](sixlabors-fonts.md) | Pure managed C# OpenType shaper and text layout engine; on .NET 10 it is within about 8% of native HarfBuzz overall, beating it on four of ten scripts. | **C** | C# | Six Labors Split License… (study only) | 🟢 active |
| 24 | [**rustybuzz-wasm**](loveencounterflow-rustybuzz-wasm.md) | Abandoned wasm-bindgen wrapper around rustybuzz 0.4 for Node.js; claims about 1.5x harfbuzzjs 0.1.5 on Latin text shaping. | **C** | Rust | unclear: Cargo.toml… (study only) | 🔴 abandoned |
| 25 | [**Pretext**](chenglou-pretext.md) | TypeScript library that predicts the browser's line breaks and paragraph heights from cached Canvas widths, so apps skip DOM reflow reads. | **D** | TypeScript | MIT | 🟢 active |
| 26 | [**libmsdf**](tmzt-libmsdf.md) | Rust/wgpu SDF and MSDF text renderer whose WGSL compute shader generates MSDF glyphs at runtime; no speed data versus msdfgen. | **D** | Rust | MIT OR Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
