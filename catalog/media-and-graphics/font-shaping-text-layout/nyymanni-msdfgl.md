# msdfgl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> OpenGL shader port of Chlumsky's MSDF glyph generator; first-party chart shows 60x-132x faster than single-threaded msdfgen on one laptop.

| | |
|---|---|
| **Beats** | msdfgen (Chlumsky's CPU multi-channel signed distance field generator, single-threaded and OpenMP builds); incumbent for MSDF font atlas generation, not one of HarfBuzz or FreeType |
| **Claimed result** | Chart numbers in README image (msdfgl vs msdfgen vs msdfgen with OpenMP): scale 1.0 0.0081 s vs 0.4890 s vs 0.1334 s; scale 2.0 0.0164 s vs 1.9390 s vs 0.5182 s; scale 4.0 0.0645 s vs 7.7407 s vs 1.9939 s; scale 8.0 0.2345 s vs 31.0000 s vs 8.0000 s (the two msdfgen values at 8.0 were extrapolated by the author). Ratios (derived from page data): about 60x, 118x, 120x and 132x faster than single-threaded msdfgen, and about 16x, 32x, 31x and 34x faster than OpenMP msdfgen. |
| **Workload** | Generating an MSDF texture for ASCII characters 0-127 of the font DejaVu Sans at four scale factors (1.0, 2.0, 4.0, 8.0), mean of 100 runs, OpenGL context creation and destruction time and shader compilation excluded. |
| **Metric** | latency |
| **Hardware** | Core i7 8550m (as written in README) with Intel UHD Graphics 620, Debian Linux |
| **Adoption** | 313 stars |
| **Last commit** | 2024-10-13 |
| **Links** | [repository](https://github.com/nyyManni/msdfgl) · [benchmark](https://github.com/nyyManni/msdfgl) |

## Verdict

The only evidence is the first-party README chart; there is no benchmark code, no compiler or flags, and no msdfgen version. Setup: ASCII 0-127 of DejaVu Sans, mean of 100 runs, Core i7 '8550m' with Intel UHD Graphics 620 on Debian. msdfgl takes 0.0081 s to 0.2345 s across scales 1 to 8, against 0.4890 s to 31 s for msdfgen (60x to 132x) and 0.1334 s to 8 s for OpenMP msdfgen (16x to 34x); both msdfgen values at scale 8 are extrapolated. The comparison is not like-for-like in three ways. msdfgl's time includes having the result in a texture while msdfgen's excludes the upload. msdfgl skips the roughly one-second shader compile. In msdfgen v1.6 (April 2019), generateMSDF also runs msdfErrorCorrection by default, a step msdfgl lacks; whether the benchmark called generateMSDF is not stated.

## Use it when

- An application already rendering with OpenGL 3.3 core or OpenGL ES 3.2 that wants MSDF text built at runtime, including on-demand glyphs through msdfgl_set_missing_glyph_callback, instead of shipping a prebaked atlas.
- Large glyph scales or big glyph sets, where CPU msdfgen takes seconds (README: 7.74 s at scale 4 against 0.0645 s for msdfgl).
- TrueType fonts with quadratic outlines for Latin-like scripts (the benchmark font is DejaVu Sans).
- C code bases that want a small MIT library whose only external dependency is FreeType (glad is vendored).

## Skip it when

- OpenType/CFF fonts with cubic outlines are unsupported, and the failure is unsafe. From the code: msdfgl_serialize_glyph sets FreeType's cubic_to callback to NULL, and FT_Outline_Decompose calls it without a check, so generating a cubic glyph should crash. The size pass's error is ignored first, so serialization also writes into a zero-size buffer slot. Convert fonts to quadratic first (cu2qu is suggested in issue #8).
- Real text layout: there is no shaping (no HarfBuzz), only optional FreeType kerning, so no ligatures, bidi or complex scripts. Multiline printf is only an open PR (#15).
- Offline atlas baking, headless or CPU-only pipelines, WebGL, Metal or Vulkan-only renderers. A GL context is required, and the text renderer uses a geometry shader (issue #3, open).
- Ornamental, symbol or CJK glyphs with long contours. From the code: corner indices go into a fixed int corners[30] stack array with no bounds check, and per-contour segment and contour counts are stored in a char. char is signed on x86, so counts over 127 skip CPU coloring, while the GPU reads the same bytes as unsigned 8-bit.
- When output must match msdfgen quality. There is no error-correction pass. Teardrop contours with 1 or 2 segments print 'Non-supported shape' and are left uncoloured, and wrong-winding detection is a README TODO. The shader math is declared precision mediump float, which GLES drivers that honour it may run at reduced precision.

## How it is fast

msdfgen's per-pixel stage runs as a fragment shader, one fragment per atlas texel, with one two-triangle draw call per glyph. That stage covers true and pseudo distance to every edge, the overlapping-contour inner/outer combine, and the median. Outlines are serialized on the CPU into an R8UI metadata buffer and an R32F point buffer that the shader reads with texelFetch. The CPU only decomposes outlines with FreeType, computes contour winding and runs msdfgen-style corner-based edge coloring. The shader also does less work than the baseline: it computes in 32-bit float rather than msdfgen's double, and it has no error-correction pass.

## Compared with alternatives

fontdue, font-rs and TiTanF rasterize coverage bitmaps on the CPU at a fixed pixel size, and Pathfinder 3 is a general Rust GPU vector rasterizer. Pick msdfgl for a C program on OpenGL 3.3 or ES 3.2 that wants one runtime-built atlas that stays sharp at any text size.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake, BUILD_SHARED_LIBS defaults to ON) |
| **Dependencies** | FreeType 2.9.1+ (CMake downloads 2.10.1 if none is found), glad (vendored), an OpenGL 3.3 core or OpenGL ES 3.2 context; glfw only for the example |
| **Minimum toolchain** | C11 (c_std_11), CMake 3.11; README reports a 32-bit MSVC 2019 build on Windows |
| **Platforms** | Linux (Wayland EGL with GLES 3.2, or GL 3.3 core with glfw3), macOS Mojave (deprecated OpenGL), Windows 10; README says it was tested only on Intel GPUs |
| **Thread safety** | Not documented. Every call needs the caller's current GL context, and msdfgl_printf and msdfgl_geometry use a function-static wchar_t[255] buffer for MSDFGL_WCHAR strings, so they are not reentrant. |
| **Drop-in for the baseline** | no |

## Gotchas

- Shader compilation takes close to a second (README) and happens in msdfgl_create_context. Create the context once; the benchmark excludes this time.
- msdfgl_generate_\* only queues GL commands; there is no glFinish. A CPU timer around the call measures submission rather than GPU completion. The README says it averaged 100 runs and subtracted context creation and destruction time, but the benchmark code is not published.
- Likely edge-colouring bug (found by reading msdfgl_serializer.c, not tested): when detecting corners, the start-of-contour tangent takes its point count from the second-to-last segment (meta_index + 2 \* (nsegments - 2) + 1) while the pointer sits on the last segment. When those two segments differ in type (line and quad), the tangent is wrong, and it can read the next contour's first point. That can misplace a colour switch and produce corner artifacts. It affects output quality, not the timings.
- The atlas texture is GL_RGBA32F (16 bytes per texel), and its height doubles as glyphs are added. Generation fails once the height passes GL_MAX_TEXTURE_SIZE.

## Known shortcomings

- README chart labels only, no benchmark code or flags; a GPU (Intel UHD 620) against CPU msdfgen (i7) on one laptop SoC, so a different machine class. No cubic segments supported; the msdfgen 8.0 points are extrapolated. Baseline msdfgen is not a listed incumbent.
- Not like-for-like with msdfgen: msdfgen 1.6's generateMSDF runs msdfErrorCorrection by default while msdfgl skips it, generate has no glFinish, and the benchmark code is unpublished. Likely edge-colouring off-by-one in msdfgl_serializer.c (prev_npoints indexed at nsegments-2 with the pointer on the last segment), affecting quality rather than timings; crashes on CFF and cubic fonts (cubic_to NULL, unchecked FreeType calls); a corners[30] stack overflow is unchecked; glyphs with more than 127 segments break on x86.

## Caveats and trade-offs

First-party benchmark with no benchmark code in the repo; compiler, flags and the msdfgen version (2019 era) are not stated. GPU versus CPU: the msdfgl timings run on the laptop's integrated Intel UHD Graphics 620 and the msdfgen timings on the same laptop's 4-core CPU (README writes 'Core i7 8550m'), so it is the same SoC rather than a discrete GPU, but the win comes from moving the per-pixel step to the GPU, not from a faster CPU algorithm, and it needs an OpenGL 3.3 or ES 3.2 context. msdfgen's timing excludes uploading the bitmaps to a texture while msdfgl's includes it (favors msdfgen); shader compilation (close to a second) and GL context creation are excluded. The scale 8.0 msdfgen values (8.0000 s and 31.0000 s) are extrapolated, not measured. msdfgl drops cubic segments (README TODO: needed for OpenType/CFF fonts) and lacks edge-coloring for teardrop contours with 1 or 2 segments; the test font DejaVu Sans is TrueType (quadratic only), so the benchmark avoids the missing paths. Output quality parity with msdfgen, including its error correction, is not evaluated. Baseline is msdfgen, not a listed incumbent (HarfBuzz, FreeType). Numbers read from bar labels in img/benchmarks.png.

GPU implementation written from scratch in C; needs an OpenGL 3.3 core or OpenGL ES 3.2 context. The algorithm was reworked to run in shaders: no cubic Bezier segments (so CFF/PostScript-flavoured OpenType outlines are not handled), constant memory, no pointers. Shader compilation takes about one second once. Output is a ready-to-use GPU atlas and index texture, so no upload step.

## Maintenance

Stale: the last commit is 2024-10-13 (a warning fix), the core code dates from 2019-2020, and 5 issues are open. It is MIT-licensed and small (about 1,550 lines of C plus shaders), so it can be vendored, but it needs fixes before it is safe on untrusted or CFF fonts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section and img/benchmarks.png show msdfgl against msdfgen and msdfgen with OpenMP, and every number in the record matches the bar labels; the repo has no benchmark code (top level is example/, img/, include/, src/, third_party/glad, CMakeLists.txt) and no compiler or flags are given, so first-party C. The 60x to 132x gains with unstated flags would cap at C anyway.
- **Verifier notes:** Confirmed at C; chart labels match the record exactly and the derived ratios check out (0.4890/0.0081 = 60x, 31.0/0.2345 = 132x vs single-threaded; 16x to 34x vs OpenMP). The GPU-vs-CPU comparison runs on one laptop SoC (integrated GPU vs its own CPU), which makes it fairer than a discrete-GPU comparison, but it is still a port to a different processor type with a reduced feature set (no cubic segments). baseline_in_list false is already correct; last commit 2024-10-13 (stale) and MIT confirmed.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nyyManni/msdfgl>
  - <https://github.com/nyyManni/msdfgl/commits/master>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/README.md>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/img/benchmarks.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/README.md>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/CMakeLists.txt>
  - <https://github.com/nyyManni/msdfgl/tree/master/src>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdfgl.c>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdfgl_serializer.c>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdfgl_serializer.h>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdf_fragment.glsl>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdf_vertex.glsl>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/font_fragment.glsl>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdfgl_map.c>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/src/msdfgl_shaders.cmake>
  - <https://raw.githubusercontent.com/nyyManni/msdfgl/HEAD/include/msdfgl.h.in>
  - <https://github.com/nyyManni/msdfgl/issues?q=is%3Aissue>
  - <https://github.com/nyyManni/msdfgl/pulls?q=is%3Apr>
  - <https://github.com/nyyManni/msdfgl/issues/3>
  - <https://github.com/nyyManni/msdfgl/issues/4>
  - <https://github.com/nyyManni/msdfgl/issues/8>
  - <https://github.com/nyyManni/msdfgl/commits/master>
  - <https://raw.githubusercontent.com/Chlumsky/msdfgen/v1.6/msdfgen.h>
  - <https://raw.githubusercontent.com/Chlumsky/msdfgen/v1.6/core/msdfgen.cpp>
  - <https://raw.githubusercontent.com/freetype/freetype/master/src/base/ftoutln.c>
  - <https://github.com/tmzt/libmsdf>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/nyymanni/msdfgl`) · [data/wave10/enrich/raw/github_com_nyymanni_msdfgl.json](../../../data/wave10/enrich/raw/github_com_nyymanni_msdfgl.json) (enrichment confidence 0.75)

</details>
