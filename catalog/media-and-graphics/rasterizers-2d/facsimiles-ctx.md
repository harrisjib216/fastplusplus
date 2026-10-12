# ctx (2D vector rasterizer and terminal by Oyvind Kolas)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0-or-later (renderer, ctx.h); GPL-3.0-or-later (ctx terminal), per COPYING on the mirror's dev branch` · 🟡 stale

> Portable C 2D vector rasterizer (HTML5-canvas-style API, one generated header) that wins many heats against cairo and Qt6 but loses most to Blend2D.

| | |
|---|---|
| **Beats** | Cairo (with pixman); Qt6 also compared; Blend2D is faster than ctx in the same tournament |
| **Claimed result** | Snippet only (page blocked, numbers unverified). Tournament page 'ctx.graphics/performance/' (Blend2D, ctx, Qt6, cairo across pixel formats and operations): first-place counts Blend2D 259, ctx 61, Qt6 1, cairo 3, so ctx wins far more heats than cairo but loses most to Blend2D; one snippet cites FillRectU-256x256-SrcCopy-Pattern_NN with ctx 52.1 versus Blend2D 16.7 (units not given). Separate older snippets (attributed to pippin.gimp.org/ctx and a Patreon post, not to the tournament page) say that in 8-bit mode ctx is comparable to cairo/pixman: cairo still faster for opaque fills, ctx 1.25x faster for partially transparent color fills and 5x faster for gradient fills. No per-test ratio against cairo was seen. |
| **Workload** | The ctx.graphics 'rasterizer tournament' (Blend2D bl_bench style tests such as FillRectA-256x256-SrcOver-Solid, stroke and gradient tests) comparing ctx, Blend2D, cairo and Qt6. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI 7 445, core locked at 2.0 GHz (per snippet) |
| **Compiler and flags** | clang; cairo and qt6 from Debian packages; Blend2D linked statically (per snippet) |
| **Adoption** | 8 stars, 0 forks on the unofficial GitHub mirror facsimiles/ctx (4,531 commits on dev); canonical repository is git https://ctx.graphics/.git/ |
| **Last commit** | 2024-10-01 |
| **Links** | [repository](https://github.com/facsimiles/ctx) · [benchmark](https://ctx.graphics/performance/) |

## Verdict

Snippet only: the ctx.graphics/performance/ 'rasterizer tournament' (blocked here) runs Blend2D-style tests (FillRectU, FillRectRot, StrokeButterfly, StrokeLine and others at 8x8-256x256, SrcOver/SrcCopy, Solid/Pattern) for ctx, Blend2D (static), cairo and Qt6 (Debian packages), built with clang on an AMD Ryzen AI 7 445 locked at 2.0 GHz. Quoted heats, where higher appears to be better because the snippet calls Blend2D's 33.3 the better FillRectRot result: FillRectU-256x256-SrcCopy-Pattern_NN ctx 52.1, Blend2D 16.7, Qt6 14.9, cairo 5.6; StrokeButterfly-8x8-SrcOver-Solid ctx 17.1, Blend2D 10.5, cairo 6.5, Qt6 5.2; FillRectRot-256x256-SrcOver-Solid Blend2D 33.3, ctx 31.9, Qt6 7.4, cairo 6.7. Units, run counts and the ctx benchmark backend are not readable from here.

## Use it when

- Embedded or microcontroller UIs that need anti-aliased vector drawing straight into RGB565, RGB332 or 1-8 bit gray framebuffers from one C source drop, with compile-time knobs (config.h) that trade features for ROM and RAM.
- Desktop or server C code that today renders with cairo's image surface and spends most of its time on gradient, pattern or partially transparent fills. Older author posts (snippet only) claim 1.25x on partially transparent and 5x on gradient fills versus cairo/pixman in 8-bit mode, and in the tournament ctx won FillRectU-256x256-SrcCopy-Pattern_NN at 52.1 versus cairo's 5.6 (snippet only).
- Pipelines that need CMYK or 32-bit float, colour-managed rendering (babl-backed CTX_ENABLE_CM) rather than only 8-bit RGBA.
- Record-and-replay or remote rendering: the drawlist and text protocol let one process record and another render, with tile hashing (CTX_HASH_ROWS x CTX_HASH_COLS) so the cb/fb backends redraw only changed tiles across up to CTX_MAX_THREADS (8) render threads.

## Skip it when

- Maximum CPU raster throughput is the goal. Blend2D took 259 first places in the same tournament (snippet only), and its JIT pipelines beat ctx in most heats.
- Opaque solid fills against cairo/pixman. The older author posts (snippet only) say cairo is still faster for opaque fills in 8-bit mode.
- Very complex paths or wide canvases. A path's edge list is capped at CTX_MAX_EDGE_LIST_SIZE (defaults to 4096 segments, 16384 in the stock ctx.c), and ctx_drawlist_add_single() silently returns 0 for segments past the cap. Active edges per scanline stop at CTX_MAX_EDGES-2 (253). config.h says CTX_SUBDIV 8 limits framebuffer width to 4095 px.
- You need analytic (area-coverage) anti-aliasing like the AGG-derived rasterizer in Blend2D. ctx approximates complex scanlines with 3, 5 or 15 vertical samples (CTX_ANTIALIAS_FAST/GOOD/FULL), so steep crossings get coarser coverage.
- Proprietary static linking or a stable, versioned API. The renderer is LGPL-3.0-or-later and the terminal GPL-3.0-or-later. The mirror has no releases (CTX_VERSION=0.0.0 in the Makefile) and no README, and the only reachable copy is an unofficial mirror last updated 2024-10-01.

## How it is fast

The rasterizer is a scanline active-edge-list design in fixed point (edge multiplier 2048, CTX_SUBDIV 8). Its anti-aliasing is adaptive: a scanline where no edge starts, ends or crosses gets each edge as a linear coverage ramp in one pass, and coverage can be applied straight to the destination row ('allow_direct' via ctx_rasterizer_apply_grads). Only complex scanlines are vertically oversampled, with 3, 5 or 15 sub-scanlines chosen from the steepest edge slope. Compositing is specialized per pixel format, paint type and full-coverage case (for example ctx_RGBA8_source_over_normal_full_cov_fragment), with fast fill_rect and stroke_rect paths (config.h credits CTX_FAST_FILL_RECT with a 15-20% win on larger rectangles) and a 256-entry gradient cache. There are no hand-written intrinsics. The Makefile compiles the same C three times (generic, x86-64-v2 with SSE4.2, x86-64-v3 with AVX2/FMA, all with -ftree-vectorize) and picks one at runtime with CPUID. ARMv7 gets a NEON build checked through /proc/self/auxv.

## Compared with alternatives

Pick ctx over Blend2D when you need plain C, CMYK or float/colour-managed targets, tiny-framebuffer formats (RGB565, GRAY1) or a record/replay protocol and can accept the LGPL. Blend2D is faster in most tournament heats and Zlib-licensed, so it wins for pure x86-64/AArch64 throughput. Pick ThorVG for SVG/Lottie loading, and AGG if you want exact-area coverage in a small permissive codebase.

## Integration

| | |
|---|---|
| **Form** | source-drop: single header ctx.h (define CTX_IMPLEMENTATION in one file). The mirror holds the split sources in src/, and `make ctx.h` concatenates them in src/index order. The upstream site is where the Makefile's updateweb target copies a prebuilt ctx.h. The Makefile also builds libctx.so/libctx.a with the multi-pass SIMD objects. |
| **Dependencies** | None for the core renderer beyond libm and pthreads. Optional: SDL2, babl (colour management), HarfBuzz, libcurl, ALSA, libdrm, plus vendored stb_truetype/stb_image in deps/. |
| **Minimum toolchain** | C compiler with GNU extensions (inline-asm cpuid, __restrict__, #pragma GCC optimize). No minimum version is documented. The build is configure.sh + GNU make, and the tournament used clang (snippet). |
| **Platforms** | x86-64 (runtime pick of generic, x86-64-v2 or x86-64-v3 builds), ARMv7 (NEON build when auxv reports it), AArch64 and other CPUs as a generic auto-vectorized build (configure.sh sets HAVE_SIMD=0 for aarch64), WebAssembly (with or without simd128, single-threaded), and microcontrollers via config.h. Linux is the main host. Other OSes are not documented. |
| **Thread safety** | Not documented for sharing one Ctx between threads. Multi-threaded rendering is internal to the fb/sdl/cb backends (ctx_set_render_threads, default cap CTX_MAX_THREADS 8). A header comment warns that ctx_identity() currently breaks multi-threaded rendering. |
| **Drop-in for the baseline** | no |

## Gotchas

- CPU dispatch bug in src/x86-64-level.c (mirror, 2024-10-01): after checking that the maximum CPUID leaf is at least 7, ctx_x86_64_level() runs cpuid(2, 0) and tests the AVX2, BMI1 and BMI2 bits in EBX. Leaf 2 holds cache/TLB descriptors on Intel and is reserved on AMD; those bits belong to leaf 7 subleaf 0. Selection of the x86-64-v3 (AVX2/FMA) build is therefore accidental, and CPUs where those bits read zero fall back to the x86-64-v2 build. This can only slow ctx down. Whether the newer upstream code used in the tournament fixes it is unknown.
- The whole library is compiled with -ffinite-math-only, -fno-signed-zeros, -fno-trapping-math and -fno-math-errno (top-level Makefile CFLAGS), and the ARMv7 NEON object adds -ffast-math. NaN or infinite coordinates and colours are undefined behaviour under these flags, so validate input from untrusted drawings.
- Over-limit geometry fails silently. Segments past the edge-list cap are dropped and edges past 253 active per scanline wait, which gives missing or wrong coverage rather than an error. Raise CTX_MIN_EDGE_LIST_SIZE/CTX_MAX_EDGE_LIST_SIZE before including ctx.h if you draw big paths.
- ctx_new_for_framebuffer() renders on the calling thread. The threaded, tile-hashed rendering is in the cb/fb/sdl backends, so pick the backend before comparing speed with Blend2D's multi-threaded mode.

## Known shortcomings

- Numbers are snippet-only: the tournament page https://ctx.graphics/performance/ is blocked (snippets confirm 259/61/1/3 wins against Blend2D, Qt6, Cairo and AGG with clang, Debian cairo and qt6 packages, Ryzen AI 7 445 at 2.0 GHz), and the 1.25x/5x-over-Cairo figures come from older author posts (pippin.gimp.org, Patreon), not the tournament. The GitHub mirror has no benchmark code (tests/test-size measures binary size) and was last updated 2024-10-01; the canonical repo is git at https://ctx.graphics/.git/. Licence LGPL-3.0-or-later for the renderer, GPL-3.0-or-later for the terminal.
- src/x86-64-level.c checks AVX2 and BMI on cpuid leaf 2 instead of leaf 7, so the x86-64-v3 code path is picked by accident and probably never on AMD (slows ctx; no inflation). Segments past the edge-list cap (4096 or 16384) and beyond 253 active edges are silently dropped; -ffinite-math-only is global; the test target ends in '; true'; aarch64 builds generic only. Search snippets of the blocked tournament page give conflicting win counts (259/61/1/3 versus 259/226/154/130), and blend2d-testing/bench has no ctx backend, so the harness cannot be verified.

## Caveats and trade-offs

SNIPPET ONLY: ctx.graphics/performance/, pippin.gimp.org and Patreon are blocked here, so no number was checked on a page, and the mirror carries no benchmark harness or results. The 1.25x and 5x cairo figures come from older author posts, not the current tournament, and the tournament compares ctx versions newer than this mirror. Canonical source is git https://ctx.graphics/.git/ by Oyvind Kolas; facsimiles/ctx is an unofficial mirror whose last commit is 2024-10-01 (default branch dev), so upstream is probably more recent. Mixed claim against Cairo (cairo wins opaque fills) and ctx loses most heats to Blend2D. Terminal code is GPL-3.0-or-later; copy only the LGPL renderer (ctx.h) into non-GPL projects. Re-check from an environment that reaches ctx.graphics.

Portable C with auto-vectorization, single header ctx.h, aimed at microcontrollers up to threaded colour-managed float rendering; HTML5-canvas-like API. LGPLv3+ renderer (the ctx terminal is GPLv3+).

## Maintenance

The facsimiles/ctx mirror is stale (last commit 2024-10-01, 8 stars, no releases) while upstream at ctx.graphics is evidently newer. The renderer is LGPL-3.0-or-later and vendorable as one header; the terminal is GPL-3.0-or-later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The tournament page https://ctx.graphics/performance/ is blocked here, so its numbers are known only from search snippets; the facsimiles/ctx mirror carries no benchmark code or result files (tests/ holds .ctx rendering tests and a binary-size suite in tests/test-size, tools/ holds font tools and fuzzers), so first-party, snippet-only numbers stay at C.
- **Verifier notes:** Search snippets confirm the tournament setup in the record (clang; cairo and qt6 from Debian; Blend2D linked statically; AMD Ryzen AI 7 445 locked at 2.0 GHz) and the 259/61/1/3 win counts. Mirror metadata checked: COPYING gives LGPL-3.0-or-later for the renderer and GPL-3.0-or-later for the terminal, last commit 2024-10-01 (stale), 8 stars, not a GitHub fork. Canonical repo per ctx.graphics/log.html search title: git clone https://ctx.graphics/.git/; consider switching repo_url once that host is reachable.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `license`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facsimiles/ctx>
  - <https://github.com/facsimiles/ctx/commits/dev>
  - <https://github.com/facsimiles/ctx/tree/dev/tests>
  - <https://github.com/facsimiles/ctx/tree/dev/tests/test-size>
  - <https://github.com/facsimiles/ctx/tree/dev/tools>
  - <https://github.com/facsimiles/ctx/tree/dev/docs>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/COPYING>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/Makefile>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/tests/Makefile>
- **Sources the enricher read:**
  - <https://github.com/facsimiles/ctx>
  - <https://github.com/facsimiles/ctx/tree/dev/src>
  - <https://github.com/facsimiles/ctx/tree/dev/docs>
  - <https://github.com/facsimiles/ctx/tree/dev/tests>
  - https://raw.githubusercontent.com/facsimiles/ctx/dev/README.md (404, no README in the mirror)
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/Makefile>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/COPYING>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/configure.sh>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/ctx.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/ctx.h>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/config.h>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/backend-rasterizer.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/composite.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/x86-64-level.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/arm-neon.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/backend-thread.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/backend-cb.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/ctx-internal.h>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/drawlist.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/ctx.c>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/src/index>
  - <https://raw.githubusercontent.com/facsimiles/ctx/dev/tests/Makefile>
  - <https://github.com/blend2d/blend2d/tree/master/blend2d-testing/bench>
  - WebSearch: ctx.graphics performance rasterizer tournament ctx Blend2D cairo Qt6 results (snippets of https://ctx.graphics/performance/, pippin.gimp.org/ctx, Patreon post 53188476)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/facsimiles/ctx`) · [data/wave10/enrich/raw/github_com_facsimiles_ctx.json](../../../data/wave10/enrich/raw/github_com_facsimiles_ctx.json) (enrichment confidence 0.5)

</details>
