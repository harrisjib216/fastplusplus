# SFML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> C++ window, input, audio and sprite library; one hobby benchmark draws static sprites 1.29x faster than raylib, slower than SDL2.

| | |
|---|---|
| **Beats** | raylib (DrawTexture, C) |
| **Claimed result** | SFML 12.4 mbunnies/s versus raylib (C) 9.6 mbunnies/s, about 1.29x (derived from page data). The same table shows SDL2 with the OpenGL renderer at 21.9, so SFML is about 0.57x of SDL2 (derived from page data). |
| **Workload** | Megabunny: draw one million identical static 32x32 bunny sprites per frame (one per pixel position of a 1000x1000 window) for 100 frames, reported as millions of bunnies per second (gettimeofday around the whole draw loop, including clear and present). |
| **Metric** | throughput |
| **Compiler and flags** | From the benchmark's run.sh scripts: g++ -O3 for the SFML program (pkg-config sfml-all), gcc -O3 for the raylib and SDL2 programs; compiler versions, the SFML 2.x / raylib / SDL2 versions and their own build flags are not stated (setup.sh prints gcc --version but no output is recorded). |
| **Adoption** | 12.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/SFML/SFML) · [benchmark](https://github.com/electronstudio/megabunny) |

## Verdict

In electronstudio/megabunny, a third-party hobby benchmark run once per program, an SFML 2.x build (g++ -O3 via pkg-config) drew one million static 32x32 sprites per frame for 100 frames at 12.4M sprites/s against raylib's C DrawTexture at 9.6 (1.29x, derived from page data) and SDL2's OpenGL renderer at 21.9 (SFML 0.57x, derived). No CPU, GPU, driver, compiler or library versions are given.

## Use it when

- You want an object-oriented C++ layer for a window, input, audio, networking and textured 2D sprites under the Zlib licence, on Windows (x86, x64, ARM64), Linux, the BSDs, macOS, iOS or Android.
- Games or tools that draw thousands to low hundreds of thousands of sprites per frame one draw() at a time; megabunny measured 12.4M sprite draws per second (roughly 200k per 60 Hz frame, derived) on an unstated machine.
- Large sprite counts where you are willing to batch by hand: put all quads sharing a texture into one std::vector&lt;sf::Vertex&gt; or sf::VertexBuffer and issue a single draw call.
- Teaching or prototyping in C++ where SFML's tutorials and RAII resource classes matter more than peak draw-call throughput.

## Skip it when

- Vector graphics work (antialiased paths, strokes, gradients, SVG): SFML only draws convex shapes and textured triangles; use Blend2D, ThorVG or another rasterizer from this category.
- Maximum sprite throughput without hand batching: SDL2's batched OpenGL renderer was 1.77x faster in the same megabunny table (21.9 vs 12.4 Mbunnies/s, derived from page data).
- Projects that need a modern GPU API: rendering uses legacy OpenGL (glVertexPointer, client-side arrays, fixed-function matrices) or OpenGL ES; the issue to move away from legacy OpenGL (#2423) is open and milestoned for SFML 4.0.0, and Vulkan support is limited to creating window surfaces (2.6.0).
- Multithreaded rendering: a render target's OpenGL context is active on one thread at a time, and moving a render target between threads crashes per the RenderTarget docs.
- Code written against SFML 2.x, like the benchmark itself, needs porting to 3.x (sf::Sprite must be constructed with a texture, sf::VideoMode takes a Vector2u).

## How it is fast

sf::RenderTarget keeps a render-state cache (last texture id, blend mode, stencil mode, view, client-array pointers) and skips redundant OpenGL state calls between draws. Any draw of 4 or fewer vertices, which covers every sf::Sprite (a 4-vertex triangle strip), is pre-transformed on the CPU into a 4-entry vertex cache so the modelview matrix stays identity and no per-sprite matrix load is issued. Each sprite is still one glDrawArrays from client-side vertex arrays on the legacy fixed-function pipeline; there is no automatic batching (issue #3470, a raylib-style batching request, was closed as a duplicate). In megabunny this cheap per-draw path beat raylib's default rlgl path, which emits per-vertex rlVertex2f/rlTexCoord2f calls into a single 8192-quad batch buffer (about 123 flushes per 1M-sprite frame, derived from rlgl.h defaults), but lost to SDL2's batched OpenGL renderer.

## Compared with alternatives

The catalogued siblings (Blend2D, ThorVG, tiny-skia, vkvg, AGG and others) are vector path rasterizers; pick SFML only when you need a windowed GPU sprite and game layer with input and audio rather than antialiased path rendering, and reach for Blend2D or ThorVG for path fills.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; optional macOS frameworks) |
| **Dependencies** | OpenGL or OpenGL ES; Graphics: FreeType, HarfBuzz, SheenBidi, cpp-unicodelib, stb_image/stb_image_write, qoi; Audio: miniaudio, libogg, libvorbis, libflac, dr_mp3; Network: Mbed TLS, libssh2, wepoll (Windows). Bundled or system copies via SFML_USE_SYSTEM_DEPS. |
| **Minimum toolchain** | C++17 (3.x); master CMakeLists requires CMake 3.28; minimum compiler versions not documented in the files read |
| **Platforms** | Windows (x86, x64, ARM64), Linux, FreeBSD, OpenBSD, NetBSD, macOS, iOS, Android (cmake/Config.cmake); Cygwin unsupported |
| **Thread safety** | Render targets are bound to an OpenGL context that is current on one thread at a time (setActive); moving a render target between threads is documented to crash. No concurrent drawing. |
| **Drop-in for the baseline** | no |

## Gotchas

- No automatic batching: every window.draw(sprite) becomes one glDrawArrays with client-side arrays, so throughput depends on the driver's per-call cost; batching is manual through vertex arrays or sf::VertexBuffer.
- Harness flaw in the only benchmark: each megabunny frame alpha-blends about 0.99 billion pixels (1M overlapping 32x32 sprites after edge clipping, derived), so with no GPU stated the number mixes fill rate with API overhead; the raylib baseline runs at default rlgl settings (one 8192-quad buffer) and also draws an FPS counter; each program ran once, timing includes first-frame setup, and the SFML row is labelled 'C' because main.cpp hard-codes the printf string.
- The measured program uses the SFML 2.x API (default-constructed sf::Sprite, two-argument sf::VideoMode) and does not compile against 3.x; the 3.x draw path read here is the same per-sprite design (4-vertex cache, one glDrawArrays), but 3.x was not measured.
- In 3.x, Drawable::draw takes RenderStates by value, a copy per draw call; issue #3073 asking to change it was closed as not planned.

## Known shortcomings

- Megabunny README (3-star hobby benchmark, no CPU, GPU or versions): 12.4 vs raylib 9.6 mbunnies (1.29x derived) but 0.57x of SDL2's 21.9, measured on the SFML 2.x API; the baseline is off-category (raylib, not Skia, Cairo or Blend2D) and the fit for rasterizers-2d is weak. The 2007 SFML-vs-SDL 1.2 forum numbers are a snippet only and compare software SDL against hardware SFML.
- Enricher: each megabunny frame alpha-blends about 0.99 Gpx (1M overlapping 32x32 sprites, derived) with no GPU stated, so the number mixes fill rate with API overhead; the raylib baseline ran at default rlgl settings (one 8192-quad buffer, about 123 flushes per frame) plus DrawFPS, one run per program, SFML 2.x. SFML's speed comes from its state cache and 4-vertex CPU pre-transform cache but it still issues one glDrawArrays per sprite on legacy fixed-function OpenGL; no auto batching (#3470), legacy-GL removal (#2423) open for 4.0.0, RenderStates copied per draw (#3073). Lead: VRSFML fork (modern GL, instanced batches, no numbers).

## Caveats and trade-offs

Third-party hobby benchmark (electronstudio/megabunny, 3 stars, GPL-3.0, 6 commits; SFML added 2024-05-12, last commit 2024-11-05) with no CPU or GPU model, no driver, no compiler version and no library versions; one run per program, no repetitions. The README itself says the benchmark is not a good reason to choose a framework. The baseline is off-category: raylib and SDL2 are GPU sprite/game frameworks, not the rasterizers-2d baselines (Skia, Cairo, Blend2D), and SFML itself is a multimedia framework whose 2D drawing is GPU sprite submission rather than vector rasterization, so the category fit is weak. The measured code uses the SFML 2.x API (two-argument sf::VideoMode, default-constructed sf::Sprite with setTexture), which does not compile against the current SFML 3.x, so the numbers describe an unstated SFML 2.x release. Workload differences: SFML calls window.draw once per sprite, raylib batches DrawTexture internally and also calls DrawFPS each frame, SDL2 sets SDL_HINT_RENDER_BATCHING and fills its 1M-entry rect array inside the timed region; the bunny texture is 32x32, so SDL2's 32x32 destination rects match the texture size the other two draw (draw sizes are equivalent). Vsync is not requested by any program and is immaterial at roughly 10-22 frames per second. The timer includes first-frame costs. The table labels SFML as language 'C' because the printf string in main.cpp hard-codes it. SFML loses to SDL2 in the same table (about 0.57x, derived from page data), so this is only a win over raylib. No SFML-owned benchmark exists in the SFML repo (README, no benchmark directory). An old first-party SFML forum benchmark (2007, topic 43 on en.sfml-dev.org) reported SFML 3366% faster than SDL 1.2 on 2000 static sprites and 9233% on rotating sprites; that page is blocked here (WebSearch snippet only), SDL 1.2 is obsolete, and critics noted it compared SDL's software rendering against hardware-accelerated SFML, so it is not usable evidence.

Object-oriented C++ multimedia API (window, 2D graphics, audio, network) on top of OpenGL, with bindings for C, .NET, Ruby and Python. Per-sprite draw calls through sf::RenderWindow; the project is mid-move to version 3 and 2.x no longer gets features.

## Maintenance

Actively maintained (last commit 2026-10-06, master at 3.2.0, 3.1.0 latest release, 2.x feature-frozen) and Zlib-licensed, so copyable, but the only speed evidence is a single hobby run of an old 2.x build against an off-category baseline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The megabunny README 'My results' table lists SFML 12.4, Raylib (C) 9.6 and SDL2 opengl 21.9 mbunnies/s, and the code is public (sfml/main.cpp, raylib/main.c, sdl2/main.c with run.sh using g++/gcc -O3), but no CPU, GPU, driver, compiler version or library version is stated and the suite is a 3-star hobby repo, so it is neither A nor B.
- **Verifier notes:** Numbers and the 1.29x (12.4/9.6) and 0.57x (12.4/21.9) ratios are correct and derived from page data; metadata checked (Zlib, 12.1k stars, not archived or a fork, last commit 2026-10-06 'Add a debug postfix to libssh2'). Shortcomings to record: off-category baseline (raylib, not Skia/Cairo/Blend2D) and weak rasterizers-2d fit, hobby benchmark without hardware or versions, measured SFML 2.x not current 3.x, slower than SDL2 in the same table. Corrected the record's caveat that SDL2 draws a different size: bunny.png is 32x32, so the draw sizes match.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`, `workload`
- **Shortcomings recorded by:** Megabunny README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/electronstudio/megabunny>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/README.md>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/run_all.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/setup.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sfml/run.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sfml/main.cpp>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/raylib/run.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/raylib/main.c>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sdl2/run.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sdl2/main.c>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/bunny.png>
  - <https://github.com/electronstudio/megabunny/commits>
  - <https://github.com/SFML/SFML>
  - <https://github.com/SFML/SFML/commits>
  - <https://github.com/SFML/SFML/commits/master>
- **Sources the enricher read:**
  - <https://github.com/SFML/SFML>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/readme.md>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/cmake/Config.cmake>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/changelog.md>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/include/SFML/Graphics/RenderTarget.hpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/src/SFML/Graphics/RenderTarget.cpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/include/SFML/Graphics/Sprite.hpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/src/SFML/Graphics/Sprite.cpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/include/SFML/Graphics/VertexArray.hpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/include/SFML/Graphics/VertexBuffer.hpp>
  - <https://raw.githubusercontent.com/SFML/SFML/HEAD/include/SFML/Window/VideoMode.hpp>
  - <https://raw.githubusercontent.com/SFML/SFML/2.6.x/src/SFML/Graphics/RenderTarget.cpp>
  - <https://raw.githubusercontent.com/SFML/SFML/2.6.x/include/SFML/Graphics/RenderTarget.hpp>
  - <https://github.com/SFML/SFML/releases>
  - <https://github.com/SFML/SFML/issues?q=is%3Aissue+batching>
  - <https://github.com/SFML/SFML/issues/3470>
  - <https://github.com/SFML/SFML/issues/2423>
  - <https://github.com/SFML/SFML/issues?q=is%3Aissue+performance+label%3Abug>
  - <https://github.com/SFML/SFML/issues/3073>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/README.md>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/run_all.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/setup.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sfml/main.cpp>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sfml/run.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/raylib/main.c>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/raylib/run.sh>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sdl2/main.c>
  - <https://raw.githubusercontent.com/electronstudio/megabunny/HEAD/sdl2/run.sh>
  - <https://raw.githubusercontent.com/raysan5/raylib/HEAD/src/rtextures.c>
  - <https://raw.githubusercontent.com/raysan5/raylib/HEAD/src/rlgl.h>
  - <https://github.com/vittorioromeo/VRSFML>
  - <https://raw.githubusercontent.com/vittorioromeo/VRSFML/HEAD/readme.md>
  - <https://raw.githubusercontent.com/vittorioromeo/VRSFML/HEAD/DESIGN.md>
  - <https://github.com/vittorioromeo/VRSFML/tree/master/include/SFML/Graphics>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sfml/sfml`) · [data/wave10/enrich/raw/github_com_sfml_sfml.json](../../../data/wave10/enrich/raw/github_com_sfml_sfml.json) (enrichment confidence 0.55)

</details>
