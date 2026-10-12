# Media and graphics

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Image and video codecs, 2D rasterizers, color conversion, resampling and text shaping measured against libjpeg-turbo, FFmpeg, Skia and HarfBuzz.

**270 entries in 6 categories:** 30 tier A · 29 tier B · 178 tier C · 33 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [2D rasterizers](rasterizers-2d/README.md) | 40 | 3 | 9 | 22 | 6 | Skia, Cairo, Blend2D |
| [Color conversion and resampling](color-and-resampling/README.md) | 62 | 4 | 5 | 45 | 8 | ImageMagick, stb_image_resize |
| [Computer vision](computer-vision/README.md) | 1 | 0 | 0 | 1 | 0 | OpenCV default frontal face detector (Haar cascade, default… |
| [Font shaping and text layout](font-shaping-text-layout/README.md) | 26 | 1 | 3 | 20 | 2 | HarfBuzz, FreeType |
| [Image codecs](image-codecs/README.md) | 78 | 19 | 8 | 42 | 9 | libjpeg-turbo, libpng, libwebp, libavif |
| [Video and audio](video-audio/README.md) | 63 | 3 | 4 | 48 | 8 | FFmpeg components, x264/x265, Opus |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**meshoptimizer (vertex codec used as a lossless float-image…**](image-codecs/zeux-meshoptimizer.md) | Mesh library whose lossless vertex codec, misused on float pixels, beat OpenEXR ZIP: 1.4x encode, 3.1x decode, 7% smaller. | [Image codecs](image-codecs/README.md) | **A** | C++ | MIT | 🟢 active |
| 2 | [**QOI (Quite OK Image format)**](image-codecs/phoboslab-qoi.md) | Reference C header for the QOI lossless RGB/RGBA format: about 27x faster encode and 3.4x faster decode than libpng, with files about 17% larger. | [Image codecs](image-codecs/README.md) | **A** | C | MIT | 🟢 active |
| 3 | [**oxipng**](image-codecs/oxipng-oxipng.md) | Multithreaded Rust lossless PNG/APNG optimizer; 2.2x (default) to 5x (-o4) faster than OptiPNG 0.7.7 wall-clock on one test image. | [Image codecs](image-codecs/README.md) | **A** | Rust | MIT | 🟢 active |
| 4 | [**LodePNG**](image-codecs/lvandeve-lodepng.md) | Two-file, dependency-free PNG encoder/decoder; decodes small PNGs about 1.1x faster than libpng+zlib 1.2.11, larger ones slower. | [Image codecs](image-codecs/README.md) | **A** | C++ | Zlib | 🟢 active |
| 5 | [**tiny-skia**](rasterizers-2d/linebender-tiny-skia.md) | Pure-Rust port of Skia's CPU raster pipeline; about 1.7-2.3x faster than cairo on x86 overall, slower on solid rect fills. | [2D rasterizers](rasterizers-2d/README.md) | **A** | Rust | BSD-3-Clause | 🟢 active |
| 6 | [**Fontations (skrifa / read-fonts)**](font-shaping-text-layout/googlefonts-fontations.md) | Google's memory-safe Rust OpenType stack (read-fonts, skrifa); mostly 1.1-1.6x slower than HarfBuzz's own OT font functions. | [Font shaping and text layout](font-shaping-text-layout/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 7 | [**image-png (Rust png crate)**](image-codecs/image-rs-image-png.md) | Pure-safe-Rust PNG/APNG decoder and encoder that decodes faster than libpng on most images; Chromium's default PNG decoder. | [Image codecs](image-codecs/README.md) | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 8 | [**fast_image_resize**](color-and-resampling/cykooz-fast-image-resize.md) | Rust SIMD image-resize crate (SSE4.1/AVX2/NEON/wasm); with AVX2 it is 1.3-1.6x faster than libvips and about 10x faster than the image/resize crates. | [Color conversion and resampling](color-and-resampling/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 9 | [**Marlin renderer (Java 2D)**](rasterizers-2d/bourgesl-marlin-renderer.md) | Pure-Java antialiasing shape rasterizer for Java 2D that replaced Pisces and Ductus; OpenJDK's default renderer since JDK 9. | [2D rasterizers](rasterizers-2d/README.md) | **A** | Java | GPL-2.0-only WITH… | 🟢 active |
| 10 | [**QOIR**](image-codecs/nigeltao-qoir.md) | Single-header C codec for a new lossless image format; encodes about 30x and decodes about 4.9x faster than libpng. | [Image codecs](image-codecs/README.md) | **A** | C | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
