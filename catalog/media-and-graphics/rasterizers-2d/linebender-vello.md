# Vello CPU (sparse strips renderer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust CPU 2D vector renderer (sparse strips, SIMD, optional threads); about 2.4x Skia and 4x Cairo raster speed on M1.

| | |
|---|---|
| **Beats** | Skia (CPU pipeline) and Cairo; also Rust tiny-skia, raqote, AGG, JUCE |
| **Claimed result** | Thesis: Vello CPU 'outperforms nearly all other renderers, including Skia or Cairo, as the shape size increases'; Blend2D still wins in 'the vast majority of cases'. Fill-Solid-RectU 256x256 single-threaded: Vello CPU 14.2 ms vs Skia 50.3 ms (about 3.5x faster, derived from page data) and Cairo 21.9 ms (about 1.5x faster, derived from page data) per 1000 renders; Blend2D 10.8 ms. Across the thesis data set (vello_chart data/arm/2025-09-24.json), vello-cpu ST is faster than Skia in 954 of 1044 test x size cells (geometric mean about 2.4x) and faster than Cairo in 822 of 870 cells (geometric mean about 4.0x) (derived from page data). At small sizes (8x8, 16x16) Skia, AGG and JUCE are faster in some tests. Multi-threaded: the 8-thread mode reaches up to 5.3x over Vello CPU's own single-thread time (Fill-Solid-PolyNZi40, 5.1x at 256x256), 4.6x on Fish and 4.1x on Linear RectA at 256x256, but only 3.4x on Fill-Solid-RectA 256x256. |
| **Workload** | Time for 1000 render calls of a single shape (rectangles, many-segment polygons, curves, strokes; solid/gradient/image paints) at sizes 8x8 to 256x256 on a 512x600 pixmap, single-threaded and 8-thread, in a fork of the Blend2D benchmark harness. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (8 cores: 6 performance + 2 efficiency, 16 GB, macOS) for the thesis results; an Intel Core i9-14900K (Windows) run in vello_chart data/x86 has no Skia or JUCE column |
| **Compiler and flags** | Rust crates built with target-feature=+avx2 on x86 (no extra flags on ARM); build flags of the C++ baselines (Skia, Cairo, Blend2D) not stated in the thesis |
| **Adoption** | 4.4k stars (linebender/vello) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/linebender/vello) · [benchmark](https://github.com/LaurenzV/master-thesis/blob/main/main.pdf) |

## Verdict

In the author's ETH Zurich master's thesis (first-party, not independently reproduced), a Blend2D bl_bench fork on an Apple M1 Pro rendered 1000 unaligned 256x256 solid rectangles in 14.2 ms with vello-cpu ST, against 50.3 ms for Skia (CPU, version unstated), 21.9 ms for Cairo 1.18.4 and 10.8 ms for Blend2D 0.12.0. Rust crates were built with target-feature=+avx2 on x86 and no extra flags on ARM, and the C++ compilers and flags are not stated. Across the published result JSON it was faster than Skia in 954 of 1044 cells and Cairo in 822 of 870 (derived from page data).

## Use it when

- Pure-Rust CPU rendering of GUI, document or SVG content where tiny-skia or raqote is the bottleneck. In the author's Blend2D-harness data on an Apple M1 Pro (2025-09-24) vello-cpu ST was faster than tiny-skia in 843 of 870 cells (geometric mean about 4.2x) and raqote in 881 of 1044 (about 2.2x) (derived from page data).
- Medium to large shapes (32x32 and up) on AArch64, especially many-edge polygons and curve-heavy paths. On the M1 Pro its geometric-mean lead over Skia grows from about 1.5x at 8x8 to 3.3x at 256x256, and over Cairo from 3.2x to 4.5x (derived from page data).
- Curve-heavy small shapes: on 8x8 FillFish Solid it was 2.2x faster than Blend2D in 2025-09 and 2.9x in the 2026-06-08 run (derived from page data), thanks to the curve-flattening shortcut.
- Software rendering that must scale across cores: the 8-thread mode gave a geometric mean of about 4.0x over its own single-thread time on the M1 Pro (2025-09-24) and 5.3x on an i9-14900K (2026-01-22) (derived from page data).
- no_std/WASM targets that need a safe, dependency-light rasteriser: the crate is #![no_std] (with alloc) and #![forbid(unsafe_code)], with a libm feature and WASM SIMD paths.

## Skip it when

- You want the fastest CPU rasteriser regardless of language: Blend2D was faster in about 95% of cells (vello-cpu ST geometric mean about 0.57x of Blend2D on M1, 0.43x on i9-14900K), and Blend2D 8T beat vello-cpu 8T in 174 of 174 cells at 256x256 in the 2026-06-08 run (derived from page data).
- x86 workloads dominated by rectangles or image patterns. In the i9-14900K run Cairo 1.18.2 beat it at 256x256 on 16 tests, for example StrokeRectA Solid by about 8x, FillRectA Pattern_NN by about 3.7x and FillRectU Solid by about 1.2x (derived from page data). The README itself says x86 still has 'more room for performance improvements'.
- Very small simple shapes such as icons and UI glyph-sized rectangles: the fixed 4x4 tile adds overhead, and at 8x8 AGG and JUCE beat it on aligned solid rectangles in the thesis (Figure 39).
- C or C++ projects that need a supported API: the only C bindings (vello_cpu_c) say they are 'not meant for production' and exist only for the benchmark harness.
- Scenes with complex filter graphs (they panic) or any filter in multi-threaded mode (unsupported), per the crate docs.

## How it is fast

Paths are flattened (kurbo's analytic quadratic subdivision, with an early exit that emits one line when a curve cannot exceed the 0.25 px tolerance and a lookup table instead of powf when estimating quad counts) and binned into 4x4 tiles. The tiles become sparse strips, a run-length encoding that keeps per-pixel coverage only along path edges and marks interior spans as cheap solid fills, so cost grows with edge length more than with area. A coarse rasterizer then builds per-wide-tile command lists, and fine rasterization composites them with SIMD code written once over the fearless_simd abstraction and dispatched at runtime (NEON, SSE4.2/AVX2/AVX-512, WASM SIMD128, scalar fallback), by default on a u8 pipeline. With the multithreading feature, path rendering and fine rasterization run on a rayon pool while the main thread does coarse rasterization.

## Compared with alternatives

Pick Vello CPU over tiny-skia or raqote when you want the fastest maintained pure-Rust CPU renderer: it beat both in most cells, tiny-skia by about 4x. Pick Blend2D instead when C/C++ is fine and peak single-thread or 8-thread speed matters, and AGG or JUCE only for very small shapes.

## Integration

| | |
|---|---|
| **Form** | crate (vello_cpu 0.3.0 on crates.io; Rust library, no official C API) |
| **Dependencies** | vello_common (kurbo/peniko geometry and paint types, fearless_simd, smallvec, guillotiere), bytemuck, hashbrown; optional png, glifo (text, default on), and rayon, crossbeam-channel, ordered-channel, thread_local for the multithreading feature |
| **Minimum toolchain** | Rust 1.89 (MSRV), edition 2024 |
| **Platforms** | Any Rust target with alloc; runtime SIMD dispatch for x86/x86-64 (SSE2 baseline, SSE4.2, AVX2, AVX-512) and AArch64 NEON; WASM SIMD128 (and relaxed SIMD) chosen at compile time; scalar fallback elsewhere; big-endian rendering fixed in 0.3.0 |
| **Thread safety** | A RenderContext is driven from one thread. With the multithreading feature, RenderContext::new spawns its own rayon pool of min(cores - 1, 8) worker threads plus the calling thread, and flush() must be called before render() or the program panics; issue #1798 asks to share one pool across contexts. |
| **Drop-in for the baseline** | no |

## Gotchas

- The API is pre-1.0 and churns: 0.3.0 (2026-10-02) replaced CompositeMode with TargetInit, renamed pop_clip_path to pop_clip and changed glyph-run return types, and 0.1.0 replaced render_to_pixmap with render/render_with. The C bindings still call render_to_pixmap and pin a git revision (35a4279).
- Turning on the multithreading feature changes the default: RenderContext::new then uses up to 8 worker threads. Create contexts with RenderSettings { num_threads: 0, .. } for single-threaded rendering, and do not create many contexts, because each one owns a thread pool.
- Default rendering uses the u8 pipeline (RenderMode::OptimizeSpeed). Enable the f32_pipeline feature and OptimizeQuality when you need accuracy, for example for snapshot tests. Canvas width and height are u16, so the maximum is 65535 px.
- Open sparse-strips issues include FunkyPathsScene rendering incorrectly (#1240), zero-length paths with round caps not following the SVG spec (#1450), image quality loss when downscaling more than 2x (#1289), and slow image-heavy scenes (#1427 bunnymark: 70 ms ST, 26 ms MT, versus 273 ms for Skia CPU and 8.3 ms for Skia Ganesh). Version 0.0.9 widened a winding histogram from i8 to i16 after high winding counts overflowed (PR #1673).

## Known shortcomings

- Downgraded B to C: the ETH thesis is by the Vello CPU author (first-party, no peer review), and the vello-cpu harness backend is not in the public fork LaurenzV/blend2d-apps. Rust library (language-filter mismatch; C++ use needs FFI). Multi-thread gain is up to 5.3x, not about 4x. Newer 2026-06-08 chart data has Vello CPU at 9.26 ms vs Blend2D 10.8 ms on RectU 256.
- The vello-cpu backend used in the thesis harness is not public code, only the vello_cpu_c bindings (OptimizeSpeed u8 pipeline; strokes use bevel joins while the other backends keep their default joins). On the x86 i9-14900K run Cairo 1.18.2 wins 16 tests at 256x256 (StrokeRectA Solid 8.2x, FillRectA Pattern_NN 3.7x, FillRectU Solid 1.2x); on the 2026-06-08 M1 run 8-thread scaling fell from 3.96x to 3.02x and image-pattern rectangles are up to 37% slower; Blend2D with 8 threads wins all 174 cells at 256x256. Complex filters panic.

## Caveats and trade-offs

Evidence is an ETH Zurich master's thesis (PDF checked into LaurenzV/master-thesis, read via raw.githubusercontent.com) by the Vello CPU author, so the benchmark is first-party for Vello CPU even though the harness is a fork of Blend2D's; the vello-cpu harness backend is not in the public fork, only the C binding crates (vello_cpu_c, which its README says is not meant for production). Blend2D is faster in nearly all tests, so this is not a win over the category's best. Thread counts are not like for like: Vello CPU's nT mode uses n worker threads plus a main thread, Blend2D's uses the main thread as one of n. Raw results for M1 Pro and i9-14900K are in the public LaurenzV/vello_chart data/ JSON files; the 2026-06-08 M1 Pro run shows vello-cpu ST at 9.26 ms on Fill-Solid-RectU 256x256, ahead of Blend2D 0.12.0 at 10.8 ms, so later Vello versions improved. The Vello repo README has no numbers. Rust library; C++ use only through C bindings.

Rust crate (vello_cpu); C bindings exist in a separate repo (LaurenzV/vello_cpu_c) so C++ use needs FFI. Weak for very small shapes because of the fixed 4x4 tile size. Supports multi-threading and NEON/AVX2 SIMD.

## Maintenance

Very active (vello_cpu 0.3.0 released 2026-10-02, about 5.1M crates.io downloads, 3.8M of them recent) and dual-licensed Apache-2.0 OR MIT, so it is copyable. It is still 0.x with breaking releases every few weeks, so pin the version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers are real (thesis Figure 40: vello-cpu ST 14.2 ms vs Skia 50.3 ms and Cairo 21.9 ms at 256x256; same values in vello_chart data/arm/2025-09-24.json), but they were measured and published by the Vello CPU author in a master's thesis, which is first-party and not peer reviewed. The vello-cpu backend of the forked harness is not in the public LaurenzV/blend2d-apps master (only the C binding crates are public), and the C++ renderers' compiler and flags are unstated, so neither A nor B.
- **Verifier notes:** Language is Rust (record already says so), a mismatch with the C++ language filter. Downgraded because the record's own caveats concede first-party measurement and no peer review; if the orchestrator treats an examined master's thesis as reviewed, B would be defensible, but no independent run exists. The 'up to about 4x' multi-thread claim understated the thesis (up to 5.3x).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/LaurenzV/master-thesis/blob/main/main.pdf>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/main/main.pdf>
  - <https://github.com/linebender/vello>
  - <https://github.com/linebender/vello/commits>
  - <https://github.com/LaurenzV/vello_chart>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data/arm>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/manifest.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/x86/2026-01-22.json>
  - <https://github.com/LaurenzV/vello_cpu_c>
  - <https://github.com/LaurenzV/blend2d-apps>
  - <https://github.com/LaurenzV/blend2d-apps/branches>
  - <https://github.com/LaurenzV/blend2d-apps/commits/master>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/linebender/vello>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/README.md>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/CHANGELOG.md>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/src/lib.rs>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/src/render.rs>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/src/dispatch/mod.rs>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_cpu/src/dispatch/multi_threaded.rs>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_common/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_bench/README.md>
  - <https://raw.githubusercontent.com/linebender/vello/HEAD/vello_bench/Cargo.toml>
  - <https://github.com/linebender/vello/tree/main/vello_cpu/src>
  - <https://github.com/linebender/vello/issues?q=is%3Aissue%20state%3Aopen%20label%3Avello_cpu>
  - <https://github.com/linebender/vello/issues?q=is%3Aissue%20state%3Aopen%20cpu>
  - <https://github.com/linebender/vello/issues?q=is%3Aissue%20state%3Aopen%20label%3AC-sparse-strips>
  - <https://github.com/linebender/vello/issues/1240>
  - <https://github.com/linebender/vello/issues/1427>
  - <https://github.com/linebender/vello/issues/1798>
  - <https://github.com/linebender/vello/pull/1673>
  - <https://raw.githubusercontent.com/linebender/fearless_simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/fearless_simd/HEAD/fearless_simd/README.md>
  - <https://raw.githubusercontent.com/linebender/fearless_simd/HEAD/fearless_simd/Cargo.toml>
  - <https://crates.io/api/v1/crates/vello_cpu>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/main/main.pdf>
  - <https://github.com/LaurenzV/vello_cpu_c>
  - <https://raw.githubusercontent.com/LaurenzV/vello_cpu_c/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LaurenzV/vello_cpu_c/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/LaurenzV/vello_cpu_c/HEAD/run.sh>
  - <https://raw.githubusercontent.com/LaurenzV/vello_cpu_c/HEAD/cbindgen.toml>
  - <https://raw.githubusercontent.com/LaurenzV/vello_cpu_c/HEAD/src/lib.rs>
  - <https://github.com/LaurenzV/blend2d-apps/branches>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend_blend2d.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/master/bl_bench/backend_skia.cpp>
  - <https://github.com/blend2d/blend2d/tree/master/blend2d-testing/bench>
  - <https://github.com/LaurenzV/vello_chart>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/manifest.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/x86/2025-09-14.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/main/data/x86/2026-01-22.json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/linebender/vello`) · [data/wave10/enrich/raw/github_com_linebender_vello.json](../../../data/wave10/enrich/raw/github_com_linebender_vello.json) (enrichment confidence 0.85)

</details>
