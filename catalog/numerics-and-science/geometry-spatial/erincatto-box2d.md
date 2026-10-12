# Box2D (v3.2 development, main branch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> 2D rigid-body physics engine in C17; the unreleased v3.2 steps the same scenes about 2x faster than v3.1.1.

| | |
|---|---|
| **Beats** | Box2D v3.1.1 (previous release of the same library) |
| **Claimed result** | v3.2 vs v3.1.1 self-comparison: 1.83x/2.03x ISA-matched (derived), 2.04x/2.19x as published with v3.1.1's AVX2 path disabled; no other engine compared. |
| **Workload** | Whole-scene simulation step time (ms, lower is better) on the 14 benchmark scenes in shared/benchmarks.c (compounds, joint_grid, junkyard, large_pyramid, many_pyramids, rain, smash, spinner, tumbler, washer, queries, tree_cast, tile_world, sleep) at 60 Hz with 4 substeps, 1 thread and 8 threads, all steps after the first, world creation excluded. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D, Windows 11; threads pinned to one hardware thread on each of eight cores (start /affinity 0x5555); each value is the minimum of four runs in two interleaved rounds, spread under 4% in nearly every cell |
| **Compiler and flags** | MSVC 19.51, Release, default CMake options for each version; AVX2 kernels chosen at runtime; turbo disabled via power plan (processor state pinned at 99%) |
| **Adoption** | 10.4k stars; widely embedded 2D engine |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/erincatto/box2d) · [benchmark](https://github.com/erincatto/box2d/blob/main/benchmark/performance_v320.md) |

## Verdict

A first-party self-comparison: on the 14 scenes in shared/benchmarks.c (60 Hz, 4 sub-steps, summed time of all steps after the first, minimum of four runs), main-branch v3.2 built with MSVC 19.51 Release took 2.04x less time than v3.1.1 on one thread and 2.19x less on eight, in geometric mean. The run was on a Ryzen 9 9950X3D under Windows 11 with turbo disabled, pinned one thread per core. The baseline was a default (SSE2-only) v3.1.1 build running an unpublished port of the scenes; with both versions on SSE2 the gain is 1.83x and 2.03x.

## Use it when

- 2D games or simulations with large stacks and piles of bodies, where v3.2 gained about 2.7-3.0x over v3.1.1 (large_pyramid, many_pyramids, sleep, junkyard).
- Multicore desktops: set b2WorldDef::workerCount (up to B2_MAX_WORKERS) to use the built-in scheduler, or plug in your own job system through enqueueTask/finishTask.
- x86-64 machines with AVX2, where the 8-wide contact solver is picked at runtime with no build flag.
- Rollback or lockstep networking: b2World_GetStateHash is documented to reproduce across worker counts, and snapshot/recording APIs exist for save games and replays.
- Existing v3.0/v3.1 users who can take main-branch code and some API changes.

## Skip it when

- 3D physics: Box2D is 2D only; use Jolt, Bullet or PhysX.
- Query-bound workloads (heavy ray casts, shape casts, overlap queries): queries and tree_cast gained only 1.17-1.31x, and those calls run on the calling thread, so they do not scale with threads.
- Projects that need a tagged, stable release: v3.2 is unreleased (latest tag v3.1.1, 2025-06-04), and the v3.2 API differs enough that the benchmark scenes had to be ported to v3.1.1.
- Projects on v2.4 that depend on its behaviour or C++ API: v3 is a rewrite whose behaviour changed, and the migration guide recommends v3 for new projects.
- Very stiff or unstable joint assemblies: open bug #984 (crash with prismatic joints) is, per the author, a setup the solver cannot handle.

## How it is fast

Data-oriented storage with a sub-stepping 'Soft Step' solver over graph-colored constraint batches, solved several bodies wide with SIMD: SSE2, Neon or WASM simd128, plus an 8-wide AVX2 contact solver that v3.2 compiles by default and picks at runtime from the CPU id. Multithreading runs on a built-in task scheduler (or user task callbacks) across collision, solver stages and island splitting. Per performance_v320.md, the v3.2 gains come mostly from engine work visible even on SSE2 (faster SAT, cache and broad-phase work, faster island splitting, contact recycling, a size-relative AABB margin that creates fewer contacts, lower scheduler overhead), with about 10% more from AVX2.

## Compared with alternatives

Among the catalogued physics siblings, Jolt, Bullet, ODE, PhysX and Simbody are 3D engines, so Box2D v3 is the pick for 2D. PlayRho's catalogued wins were measured against Box2D 2.4.1, not v3, so for new 2D work on a maintained, multithreaded SIMD engine choose Box2D v3.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake; shared builds through BUILD_SHARED_LIBS), C API; also consumable from Zig and Swift Package Manager |
| **Dependencies** | none for the library (v3.2 has a built-in task scheduler; v3.1.1 needed enkiTS or your own scheduler for multithreading); samples need a C++20 compiler plus the bundled GLFW/imgui |
| **Minimum toolchain** | C17 compiler, CMake 3.22+ (MSVC, GCC, Clang; the measured build was MSVC 19.51) |
| **Platforms** | Windows, Linux, macOS; x86-64 (SSE2 baseline, AVX2 picked at runtime), AArch64 Neon, WebAssembly (simd128); BOX2D_DISABLE_SIMD gives a scalar build and BOX2D_DOUBLE_PRECISION a large-world build |
| **Thread safety** | A world is not safe for concurrent writes; the engine multithreads internally per world through workerCount or user task callbacks. Custom allocator (b2SetAllocator) and assert callbacks must be thread-safe. |
| **Drop-in for the baseline** | partial — same v3 C API family as v3.1.1, but v3.2 changed some API (the scenes needed porting), moved multithreading to the built-in scheduler, and creates fewer contacts, so contact events and behaviour can differ |

## Gotchas

- Harness finding: the v3.1.1 baseline column used 'default CMake options for each version', and in v3.1.1 the default leaves BOX2D_AVX2 OFF (an optional compile-time 8-wide AVX2 contact solver). So v3.2's runtime AVX2 kernels were compared against a 4-wide SSE2 build of v3.1.1, and the ISA-matched figures are the page's SSE2-forced row: 1.83x on 1 thread and 2.03x on 8. In the v3.1-era 7950X CSVs (commit d5935a7), the AVX2 build was 1.18x (large_pyramid), 1.11x (many_pyramids) and 1.13x (tumbler) faster than SSE2 on one thread (derived from page data), so the 2.85-2.96x per-scene headlines overstate the like-for-like gain on AVX2 machines.
- Harness finding: the headline column is labelled 'world capacity set from b2World_GetMaxCapacity', but the public benchmark/main.c never sets b2WorldDef::capacity. It reproduces the 2.03x/2.18x 'default' row rather than 2.04x/2.19x (the difference is negligible). The v3.1.1 port of the 14 scenes is not published, so the baseline column cannot be rerun from public code.
- v3.2 sizes the broad-phase AABB margin relative to shape size, so it creates fewer contacts (washer 29k against 42k, tumbler 8.6k against 11k). The per-step work differs from v3.1.1, and so can contact begin/end event timing.
- Soft Step sub-stepping applies velocity or impulse changes only on the first sub-step, so control bodies with forces or make them kinematic. b2World_EnableSSE2Fallback is documented as a testing switch; use the CMake option BOX2D_AVX2=OFF in production.

## Known shortcomings

- Downgraded A to C: performance_v320.md compares unreleased v3.2 with an unpublished port of v3.1.1 (the v3.1.1 tag benchmark has only 7 of 14 scenes and spinner runs 1400 steps, not 500); self-comparison against its own previous release, no other engine. Godot third-party numbers in caveats checked against REPORT-2D.md.
- Enricher: the v3.1.1 baseline was built with v3.1.1's default CMake, which leaves BOX2D_AVX2 OFF although v3.1.1 has a compile-time 8-wide AVX2 path, so v3.2 AVX2 vs v3.1.1 SSE2 is an ISA mismatch; ISA-matched figures are 1.83x/2.03x, not 2.04x/2.19x (the v3.1-era 7950X CSVs at commit d5935a7 show the AVX2 build 1.11-1.18x over SSE2 at 1 thread, derived). benchmark/main.c never sets b2WorldDef::capacity, so the headline 'with capacity' row is not reproducible from the public harness.

## Caveats and trade-offs

SELF-COMPARISON: the baseline is the project's own previous release (v3.1.1), not another engine; Box2D is 2D only, so ODE and Bullet (3D) are not comparable and the repo contains no comparison against any other engine. v3.2 is unreleased (latest tag v3.1.1, 2025-06-04); the numbers come from the main branch, and performance_v320.md was added in commit ac7c751 on 2026-10-04. The baseline column is not reproducible from public code: the page says v3.1.1 ran the v3.2 scenes 'ported to the v3.1.1 API without changing them', but that port is not published, and the v3.1.1 tag's own benchmark app has only 7 of the 14 scenes (joint_grid, large_pyramid, many_pyramids, rain, smash, spinner, tumbler) with spinner at 1400 steps versus 500 on main. The page says 'These are relative numbers from one machine. Read the ratios, not the milliseconds.' v3.1.1 used enkiTS for threading while v3.2 uses its built-in scheduler, and v3.2 creates fewer contacts because of a tighter broad-phase AABB margin (washer 29k vs 42k contacts, tumbler 8.6k vs 11k), so the work per step is not identical (the page counts that as an engine improvement). Single machine (Windows 11, MSVC); the per-machine CSV folders (amd7950x_avx2, amd7950x_sse2, amd7950x_float, m2air_float, m2air_neon, n100_sse2) were not opened. Independent but weak extra evidence (not used for the tier): Ughuuu/benchmarks-repo docs/REPORT-2D.md (Godot 4.7-stable, 300 timed steps, 60 Hz, single run, step p50, no CPU model stated) measures Box2D through a Godot addon against GodotPhysics2D and Rapier2D: pyramid 24.06 ms vs 151.83 ms (GodotPhysics2D) and 19.47 ms (Rapier2D wins); mixed_pile 5.91 vs 64.78 and 8.77 ms; joint_grid 3.83 ms vs 7.99 ms (Rapier2D; GodotPhysics2D failed) but Box2D's displacement_max is inf; smash 11.52 vs 12.42 (Rapier2D) and 50.63 ms; query_storm 4.28 vs 7.11 and 63.39 ms; drop 21.10 vs 17.81 ms (Rapier2D wins) and 117.37 ms. That run includes Godot addon overhead and is not a clean engine comparison. [retier] Unpublished v3.1.1 scene port (7 of 14 scenes at the tag, spinner 1400 vs 500 steps); benchmark/main.c never sets b2WorldDef::capacity so the 'with capacity' row is not reproducible; v3.2 unreleased at measurement.

2D only, portable C17 with a C API; v3 is a rewrite whose behaviour differs from v2.4 (see docs/migration.md); world is not thread-safe for writes (read-only queries may be called from several threads); multithreading uses the built-in task scheduler via b2WorldDef::workerCount; AVX2 and SSE2/Neon kernels selected at runtime.

## Maintenance

Actively developed (benchmark page and AVX2 runtime dispatch landed 2026-10-04) and MIT-licensed, but v3.2 is main-branch code with no release tag yet. The evidence is a first-party self-comparison whose baseline was built without v3.1.1's optional AVX2 path, so read the ISA-matched 1.83x/2.03x rather than the 2.04x/2.19x headline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** benchmark/performance_v320.md gives compiler (MSVC 19.51, Release, default CMake options), CPU (Ryzen 9 9950X3D) and method, and the v3.2 side runs public code (benchmark/main.c, shared/benchmarks.c), but the v3.1.1 baseline column ran an unpublished port of the v3.2 scenes: v3.1.1's own shared/benchmarks.c and benchmark/main.c contain only 7 of the 14 scenes (no compounds, junkyard, washer, queries, tree_cast, tile_world or sleep) and run spinner for 1400 steps instead of 500, so the baseline cannot be reproduced from public code; first-party partial methodology is C.
- **Verifier notes:** Every quoted number (14-scene table, 2.04x/2.19x geometric means, SSE2-forced 1.83x/2.03x, AVX2 about 10%) matches performance_v320.md, and the third-party Godot numbers in caveats match REPORT-2D.md. Downgraded A to C because half the scenes in the v3.1.1 baseline column come from an unpublished port; the main shortcoming to record is the self-comparison against the project's own previous release (off-baseline, no other engine). Metadata checked: MIT, 10.4k stars, last commit 2026-10-04, active, not a fork.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-174 (wave 8); enricher w8 pair-028
- **Pages the verifier opened:**
  - <https://github.com/erincatto/box2d/blob/main/benchmark/performance_v320.md>
  - <https://github.com/erincatto/box2d>
  - <https://github.com/erincatto/box2d/commits/main>
  - <https://github.com/erincatto/box2d/tree/main/benchmark>
  - <https://github.com/erincatto/box2d/tags>
  - <https://github.com/erincatto/box2d/commits/main/benchmark/performance_v320.md>
  - <https://github.com/erincatto/box2d/blob/main/benchmark/main.c>
  - <https://github.com/erincatto/box2d/blob/main/benchmark/CMakeLists.txt>
  - <https://github.com/erincatto/box2d/blob/main/CMakeLists.txt>
  - <https://github.com/erincatto/box2d/blob/main/shared/benchmarks.c>
  - <https://github.com/erincatto/box2d/blob/v3.1.1/shared/benchmarks.c>
  - <https://github.com/erincatto/box2d/blob/v3.1.1/benchmark/main.c>
  - <https://github.com/Ughuuu/benchmarks-repo/blob/HEAD/docs/REPORT-2D.md>
- **Sources the enricher read:**
  - <https://github.com/erincatto/box2d>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/README.md>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/performance_v320.md>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/main.c>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/shared/benchmarks.c>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/shared/benchmarks.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/src/core.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/include/box2d/box2d.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/include/box2d/types.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/include/box2d/base.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/docs/migration.md>
  - <https://raw.githubusercontent.com/erincatto/box2d/v3.1.1/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/v3.1.1/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/v3.1.1/src/core.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/v3.1.1/include/box2d/base.h>
  - <https://raw.githubusercontent.com/erincatto/box2d/v3.1.1/src/contact_solver.h>
  - <https://github.com/erincatto/box2d/tree/main/benchmark>
  - <https://github.com/erincatto/box2d/tree/main/benchmark/amd7950x_avx2>
  - <https://github.com/erincatto/box2d/commits/main/benchmark/amd7950x_avx2/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_avx2/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_avx2/many_pyramids.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_avx2/washer.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_sse2/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_sse2/many_pyramids.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_sse2/washer.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_float/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_float/many_pyramids.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/main/benchmark/amd7950x_float/washer.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_avx2/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_avx2/many_pyramids.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_avx2/tumbler.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_sse2/large_pyramid.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_sse2/many_pyramids.csv>
  - <https://raw.githubusercontent.com/erincatto/box2d/d5935a7/benchmark/amd7950x_sse2/tumbler.csv>
  - <https://github.com/erincatto/box2d/issues>
  - <https://github.com/erincatto/box2d/issues/839>
  - <https://github.com/erincatto/box2d/issues/984>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/erincatto/box2d`) · [data/wave8/enrich/raw/github_com_erincatto_box2d.json](../../../data/wave8/enrich/raw/github_com_erincatto_box2d.json) (enrichment confidence 0.8)

</details>
