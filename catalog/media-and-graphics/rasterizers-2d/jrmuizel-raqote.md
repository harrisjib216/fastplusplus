# raqote

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `BSD-3-Clause` · 🟡 stale

> Small pure-Rust CPU 2D rasterizer built on Skia-style 4x4 supersampling. Its path fills beat Cairo's image surface on an M1 Pro; overall it does not beat Skia.

| | |
|---|---|
| **Beats** | Cairo (image surface; 1.18.4 on the M1 Pro run, 1.18.2 on the Windows x86 run); not faster than Skia once the broken rotated tests are excluded |
| **Claimed result** | Apple M1 Pro, 2026-06-08 run, single-threaded. As published, geometric means of per-cell rcpms ratios are 1.08x Skia (1044 cells, faster in 57%) and 1.84x Cairo 1.18.4 (870 cells), but the four rotated tests are inflated by a harness bug. Excluding FillRectRot, FillRoundRot, StrokeRectRot and StrokeRoundRot: 0.93x Skia (900 cells, faster in 51%; fills 1.08x, strokes 0.77x), i.e. not faster than Skia, and 1.48x Cairo (750 cells, faster in 76%; fills 1.86x, strokes 1.11x). The earlier M1 runs give the same picture (0.92-0.93x Skia, 1.46-1.49x Cairo). Intel Core i9-14900K Windows run of 2026-01-22 (no Skia): 1.09x Cairo 1.18.2 as published, 0.89x with the rotated tests excluded (fills 1.19x, strokes 0.61x). Slower than Blend2D 0.12.0 single-threaded (0.26x as published). All ratios derived from page data. |
| **Workload** | Blend2D bl_bench suite with the raqote backend from LaurenzV/blend2d-apps (benching branch, bl_bench/backend_raqote.cpp) calling raqote 0.8.5 through the LaurenzV/raqote_c C bindings: 29 fill/stroke tests x six paint styles (Solid, Linear, Radial, Conic, Pattern_NN, Pattern_BI) x six sizes 8x8 to 256x256, SrcOver, 512x600 target, single thread, render calls per ms. In the rotated tests the raqote backend uses a random angle about each shape's own centre (as intended), unlike the incrementing angle about the screen centre used by the other backends, and its transform composition is wrong (see caveats). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (aarch64, macOS); second dataset Intel Core i9-14900K (x86_64, Windows) |
| **Compiler and flags** | Rust crates (raqote 0.8.5 through the raqote_c staticlib, cargo build --release) built with target-feature=+avx2 on x86 and default NEON on ARM (LaurenzV master thesis Section 5.2); C++ harness CMake Release; Skia from the vcpkg unofficial-skia package and Cairo from pkg-config, both prebuilt with unrecorded flags; rustc and C++ compiler versions are not stated. |
| **Adoption** | 1.2k stars, 65 forks; README lists resvg, Servo and orbtk as users (the list may be dated) |
| **Last commit** | 2025-02-11 |
| **Links** | [repository](https://github.com/jrmuizel/raqote) · [benchmark](https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json) |

## Verdict

An independent run by the Vello CPU author of Blend2D's bl_bench (29 tests x 6 paint styles x 6 sizes, SrcOver, 512x600 target, single thread), calling raqote 0.8.5 through the unofficial raqote_c FFI shim on an Apple M1 Pro (2026-06-08) and an Intel i9-14900K on Windows (2026-01-22); compiler versions and the Skia and Cairo build flags are unrecorded. As published, raqote is 1.08x Skia and 1.84x Cairo 1.18.4. The four rotated tests are inflated by the backend's transform-order bug, and without them raqote is 0.93x Skia and 1.48x Cairo on the M1 Pro and 0.89x Cairo 1.18.2 on x86 (all derived). Its wins are path fills; its losses are strokes and rectangle fills.

## Use it when

- A Rust program needs a small CPU canvas (UI widgets, charts, thumbnails, generated images) with pure-Rust dependencies. With default-features = false, no C toolchain or system library is needed.
- Path-fill-heavy scenes such as maps, complex polygons and outlines. In the 2026-06-08 M1 Pro run those were raqote's wins over Skia (FillWorld 1.77x, FillPolyEOi40 1.44x, FillFish 1.43x), and fills were 1.86x Cairo 1.18.4 by geometric mean (derived).
- Replacing Cairo's image surface in a Rust codebase on ARM: 1.48x Cairo overall on the M1 Pro with the broken rotated tests excluded (derived).
- You need the full Porter-Duff set plus separable and non-separable blend modes, layers and clips in a code base small enough to read and patch.

## Skip it when

- Stroke-heavy or rectangle-heavy work. Strokes were 0.77x Skia and 1.11x Cairo on the M1 Pro and 0.61x Cairo on the i9-14900K, and FillRectA was 0.68x Skia (rotated tests excluded, derived). The stroker emits separate overlapping subpaths for each segment, join and cap and then fills them.
- x86-64 desktops, or whenever peak throughput matters: raqote was 0.89x Cairo 1.18.2 on the i9-14900K, and Blend2D 0.12 was about 3.8x faster single-threaded (raqote 0.26x as published). tiny-skia and Vello CPU are maintained Rust alternatives.
- Anti-aliasing quality close to analytic coverage. 4x4 supersampling gives at most 17 coverage levels per pixel, and the only modes are Gray and None.
- Multi-threaded rendering: DrawTarget is neither Send nor Sync (issue #185), and there is no internal parallelism (issue #155). Non-separable blend modes are about 10x slower than Skia (issue #156: Hue and Saturation about 13.7 ms versus 1.4 ms).
- Projects that need an active upstream or a C/C++ API. The last commit was 2025-02-11, with 60 open issues and 10 open PRs. Servo's canvas crate now uses vello_cpu, resvg dropped its raqote backend (#214), and C++ access is only through unofficial shims.

## How it is fast

DESIGN.md calls the design 'very conservative' and says it 'borrows heavily from Skia'. The rasterizer is an active-edge-list scanline rasterizer with 4x4 supersampling and 30.2 fixed-point coordinates. Edges are kept sorted with a bubble sort, because the list is almost always nearly sorted. Quadratic curves are split into y-monotonic pieces and stepped directly as curve edges, and cubics are first approximated by quadratics (lyon_geom, tolerance 0.01). Coverage goes into an 8-bit mask over the path's bounding box, which is then composited one scanline at a time through sw-composite shaders. Those shaders use SWAR arithmetic (two 8-bit channels per u32 with 0xff00ff masks) and gradient lookup tables, with no SIMD intrinsics and no threads. An integer-aligned fill_rect with an identity transform and no clip skips the mask entirely.

## Compared with alternatives

Pick raqote over tiny-skia only if you need its wider blend-mode set or already depend on it: tiny-skia's README says it is faster than raqote in many cases, and tiny-skia is maintained under linebender. For throughput, Blend2D (C++) and Vello CPU (Rust) beat it in the same bl_bench runs. raqote's remaining advantage is a small, readable pure-Rust code base with Cairo-beating path fills on ARM.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | euclid 0.22, lyon_geom 1.0, typed-arena 2.0, sw-composite 0.7.15. Default features add font-kit 0.14 and pathfinder_geometry 0.5 (text, which uses platform font libraries; see build-failure issue #176) and png 0.17. |
| **Minimum toolchain** | Rust 2018 edition; Cargo.toml declares no rust-version (MSRV) |
| **Platforms** | Any target with Rust std (the rasterizer and compositor are portable scalar Rust, so speed depends on autovectorization and target features). Benchmarked on aarch64 macOS (Apple M1 Pro) and x86-64 Windows built with +avx2. |
| **Thread safety** | DrawTarget is not Send or Sync, because the rasterizer's active-edge list holds NonNull pointers and there is no unsafe impl (issue #185 open). Create and use each DrawTarget on a single thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Default features pull in font-kit and png. Set default-features = false for the pure-Rust core. Text rendering has open panics on a missing glyph (#150) and on '\n' (#196), and transform bugs (#145, #179).
- BlendMode::Src overwrites pixels across the whole canvas row outside the drawn rectangle, because the temporary row buffer is canvas-wide (#193; open, with a proposed fix unmerged). Clips ignore the current transform (#187).
- Validate untrusted geometry: arc() loops forever on NaN or inf (#177), drawing an image with alpha can panic (#202), and the rasterizer uses 30.2 fixed-point endpoints with 16.16 intermediates, which the source comments say limits coordinates to a 16.16 space.
- Each fill allocates a coverage mask the size of the path's clipped bounding box and shades all of it, including zero-coverage pixels. DESIGN.md and #158 describe the run-length alternative as future work. Large sparse paths such as long diagonals or big outlines therefore cost their whole bounding-box area. Only integer-aligned fill_rect with an identity transform and no clip avoids the mask.

## Known shortcomings

- Rust (language-filter mismatch; reached only through the unofficial raqote_c shim). Claim overstated: backend_raqote.cpp in the harness multiplies transforms in the wrong order, rotating shapes about the canvas origin so most are clipped, which made raqote's rotated tests 3-4.8x faster than its own unrotated ones. Without those rows raqote 0.8.5 is 0.93x Skia (not faster), 1.48x Cairo on the Apple M1 Pro and 0.89x Cairo on x86; the baseline is cut to Cairo. The runner (Vello CPU author) is independent of raqote but wrote the buggy backend; compiler and flags unrecorded.
- The transform-order bug is confirmed in raqote_c (rq_transform_multiply uses euclid's then order). crates.io 0.8.5 dates from 2024-09-11 (release commit 2024-07-24); the README's user list is stale (Servo canvas now uses vello_cpu, resvg dropped raqote, #214). DrawTarget is not Send or Sync (#185); BlendMode::Src has a row-overwrite bug (#193); non-separable blend modes are about 10x slower than Skia (#156).

## Caveats and trade-offs

Harness bug: backend_raqote.cpp builds the rotation as rq_transform_multiply(rq_transform_multiply(translate_to_centre, rotate), translate_back), and raqote_c implements rq_transform_multiply(a, b) as euclid a.then(b). Each shape is therefore rotated about the canvas origin by a random angle in [0, 6.28), so most rotated shapes land off the 512x600 canvas and are clipped. The data shows it: raqote's FillRectRot at 256x256 (29.4 calls/ms) is 4.3x faster than its own FillRectU (6.82), and FillRoundRot (32.2) is 4.8x faster than FillRoundU (6.76), while every other single-threaded renderer is slower on the rotated variants at 64x64 and 256x256. That is where the published 3.16x/3.09x/2.59x/2.12x wins over Skia on FillRectRot/FillRoundRot/StrokeRectRot/StrokeRoundRot (and 9.49x on FillRectRot over Cairo) come from. With those tests excluded raqote wins only 75 of 150 test x style rows against Skia (99 of 125 against Cairo): path and complex-polygon fills (FillWorld 1.77x, FillPolyEOi40 1.44x, FillFish 1.43x, FillButterfly and FillDragon 1.35x). It loses StrokeRectA (0.28x), FillRectA (0.68x), StrokeWorld (0.55x), StrokeRoundU (0.65x), StrokeRectU (0.69x), StrokeTriangle (0.71x), FillRoundU (0.79x) and FillRectU (0.86x), and is 0.90x at 256x256. Against Cairo the wins are fills; it loses rectangle fills (FillRectA 0.57x, FillRectU 0.61x), StrokeRectA (0.37x), StrokeRectU (0.71x) and StrokeWorld (0.64x), and on the x86 run it is slower overall. raqote anti-aliases with 4x4 multisampling (thesis Section 4.1, coarser coverage than analytic rasterizers) and has no SIMD code or threading; output equivalence is not checked in the data. Language is Rust: it falls outside the C++ filter, and from C++ it is reachable only through the unofficial raqote_c shim ('not meant for production'). raqote 0.8.5 (2024-07-24) was measured; the last commit was 2025-02-11. The runner (Vello CPU author) wrote both the raqote backend and the bindings; the Skia version is not recorded.

Rust crate (needs the raqote_c bindings or FFI from C++); no explicit SIMD, 4x4 multi-sampled anti-aliasing (lower quality than analytic coverage), single-threaded.

## Maintenance

Stale: the last commit was 2025-02-11 ('Allow writing png to memory'), the last release is 0.8.5 (release commit 2024-07-24, published on crates.io 2024-09-11), and there are 60 open issues and 10 open PRs. It is BSD-3-Clause and small enough to vendor, with 711k all-time crates.io downloads and 32 reverse dependencies, but two of the three 'notable users' in the README (Servo, resvg) no longer use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now B.
- **Tier reason:** Independent third-party run of the public bl_bench harness (LaurenzV/blend2d-apps benching branch bl_bench/backend_raqote.cpp via LaurenzV/raqote_c, raqote 0.8.5 per Cargo.lock) on named CPUs, with compiler and C++ flags unrecorded, so B at most. The claim is overstated: the raqote backend's rotated tests are broken (see caveats), and with them removed raqote is slower than Skia and wins against Cairo only on the M1.
- **Verifier notes:** Downgraded because the claim is overstated. A transform-order bug in the runner's raqote backend inflates the four rotated tests, and with them removed raqote is 0.93x Skia (slower), 1.48x Cairo on M1 and 0.89x Cairo on x86 (all derived). The record already has language Rust; the orchestrator should keep that as an override and flag the C++ filter mismatch. Consider a retier to C or reference status if the catalog wants only clean C++-callable entries; license BSD-3-Clause, stale status and 2025-02-11 last commit are correct.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-06-08.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/manifest.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-05-17.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2026-01-22.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/arm/2025-09-24.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/x86/2026-01-22.json>
  - <https://raw.githubusercontent.com/LaurenzV/vello_chart/HEAD/data/x86/2025-09-14.json>
  - <https://github.com/LaurenzV/vello_chart>
  - <https://github.com/LaurenzV/vello_chart/tree/main/data>
  - <https://github.com/LaurenzV/blend2d-apps>
  - <https://github.com/LaurenzV/blend2d-apps/tree/master/bl_bench>
  - <https://github.com/LaurenzV/blend2d-apps/branches/all>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/README.md>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/app.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend.h>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_skia.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/HEAD/bl_bench/backend_cairo.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/master-thesis/HEAD/main.pdf>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/benching/bl_bench/backend_raqote.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/benching/bl_bench/backend_vello_cpu.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/benching/bl_bench/backend_tiny_skia.cpp>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/benching/CMakeLists.txt>
  - <https://github.com/LaurenzV/raqote_c>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/run.sh>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/src/lib.rs>
  - <https://github.com/jrmuizel/raqote>
  - <https://github.com/jrmuizel/raqote/commits>
- **Sources the enricher read:**
  - <https://github.com/jrmuizel/raqote>
  - <https://github.com/jrmuizel/raqote/commits/master>
  - <https://github.com/jrmuizel/raqote/issues>
  - <https://github.com/jrmuizel/raqote/issues/156>
  - <https://github.com/jrmuizel/raqote/issues/173>
  - <https://github.com/jrmuizel/raqote/issues/193>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/README.md>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/DESIGN.md>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/draw_target.rs>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/rasterizer.rs>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/blitter.rs>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/stroke.rs>
  - <https://raw.githubusercontent.com/jrmuizel/raqote/HEAD/src/path_builder.rs>
  - <https://raw.githubusercontent.com/jrmuizel/sw-composite/HEAD/src/lib.rs>
  - <https://crates.io/api/v1/crates/raqote>
  - <https://crates.io/api/v1/crates/raqote/reverse_dependencies?per_page=20>
  - <https://raw.githubusercontent.com/servo/servo/main/components/canvas/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/servo/main/components/canvas/raqote_backend.rs>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/LaurenzV/raqote_c/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LaurenzV/blend2d-apps/benching/bl_bench/backend_raqote.cpp>
  - <https://github.com/mfabbri77/VGCPU-Benchmark>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jrmuizel/raqote`) · [data/wave10/enrich/raw/github_com_jrmuizel_raqote.json](../../../data/wave10/enrich/raw/github_com_jrmuizel_raqote.json) (enrichment confidence 0.8)

</details>
