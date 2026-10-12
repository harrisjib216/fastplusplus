# PlayRho

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟡 stale

> C++17 2-D rigid-body physics engine derived from Box2D 2.3.2; first-party microbenchmarks show 1.2-4.9x faster steps than Box2D 2.4.1, with losses.

| | |
|---|---|
| **Beats** | Box2D 2.4.1 |
| **Claimed result** | Latest wiki run (commit ef285b19a, 2021-05-25), PlayRho vs Box2D time per iteration: WorldStepWithStatsStatic/10000 67,606 ns vs 329,934 ns (4.9x, derived from page data); DropDisks/1000 384,976 ns vs 874,668 ns (2.3x, derived from page data); DropDisks/10000 3,837,606 ns vs 6,266,863 ns (1.6x, derived from page data); AddPairStressTest400/18 48,679,814 ns vs 106,326,260 ns (2.2x, derived from page data); TilesRestOneGround/36 1,195,594,385 ns vs 1,445,217,889 ns (1.2x, derived from page data). PlayRho is slower on TilesRestComboGround/36 (1,418,653,021 ns vs 1,329,953,352 ns) and /12 (22,889,731 ns vs 18,891,740 ns). Author comment on the page: 'PlayRho often faster than Box2D and in tests I'd expect PlayRho to be faster in'. |
| **Workload** | Google Benchmark microbenchmarks in the project's Benchmark/BenchmarkMain.cpp, built with BENCHMARK_BOX2D defined: one world step with N static bodies, N non-colliding falling disks, a 400-count broad-phase pair stress test and a tile-dropping scene, PlayRho vs Box2D. |
| **Metric** | throughput |
| **Hardware** | '2.6 GHz Intel Core i7' (wiki page title), 8 X 2600 MHz CPUs per Google Benchmark header; exact CPU model not stated |
| **Adoption** | 151 stars |
| **Last commit** | 2024-04-30 |
| **Links** | [repository](https://github.com/louis-langholtz/PlayRho) · [benchmark](https://github.com/louis-langholtz/PlayRho/wiki/Benchmark-Data:-2.6-GHz-Intel-Core-i7) |

## Verdict

These are the author's own Google Benchmark runs on the project wiki (commit ef285b19a, 2021-05-25, '8 X 2600 MHz' Core i7, compiler, flags and Box2D build unstated) of PlayRho vs Box2D 2.4.1 built into the same binary. PlayRho was 4.9x faster stepping 10,000 shapeless static bodies, 1.6-2.3x faster on 1,000-10,000 non-colliding falling disks, 2.2x faster on step 18 of a 400-disk pair stress test and 1.2x faster on TilesRestOneGround/36, but 1.07-1.2x slower on TilesRestComboGround.

## Use it when

- 2-D games or simulations that want a Box2D-v2-style engine with a value-semantic, pointer-free C++17 API and IDs instead of b2Body\*.
- Worlds with many static or sleeping bodies, or many contact-free movers, where per-step bookkeeping dominates (4.9x on 10,000 static bodies, 1.6-2.3x on 1,000-10,000 non-touching falling disks).
- Projects that need a configurable Real type (double, long double or a fixed-point type from the author's realnumb project) or compile-time unit checking, which Box2D v2 does not offer.
- Codebases that must avoid mutable global state (PlayRho removed Box2D's globals and preprocessor settings).

## Skip it when

- Contact-heavy stacking or piles: the project's own TilesRestComboGround rows have PlayRho slower than Box2D 2.4.1 (22.9 ms vs 18.9 ms at 12, 1.42 s vs 1.33 s at 36).
- New projects that can use Box2D v3: it is the actively developed successor (the catalogue entry reports one- and eight-thread runs), and no PlayRho comparison against v3 exists.
- If you need a stable API: master (the 2.0 line that the benchmark ran on) is documented as unstable and not for use, and the latest tag v1.1.2 still has the older Fixture-based API.
- If you want maintenance or multithreading: last commit 2024-04-30, threaded island solving is compiled out (DO_THREADED is commented out), and issue #477 about an unexplained 11-38x AddPairStressTest slowdown has been open since 2023-03-19.
- 3-D physics: PlayRho is 2-D only.

## How it is fast

From reading the source: the world implementation (AabbTreeWorld) keeps bodies, shapes, contacts and manifolds in contiguous ObjectPool arrays indexed by ID, tracks island membership in std::vector&lt;bool&gt; bitsets, and serves per-step allocations (islands, constraints, proxy keys) from pmr pool memory resources. Box2D 2.4.1, by contrast, walks its intrusive linked list of heap bodies at least four times per Step (island-flag reset, island seeding, fixture synchronization, TOI reset) and always runs five b2Timer profiling scopes (10 gettimeofday calls) per Step. That explains most of the static-world and contact-free wins; on contact-heavy scenes the solvers are near parity (PlayRho keeps Box2D's 8 velocity and 3 position iteration Gauss-Seidel solver).

## Compared with alternatives

Pick PlayRho over Box2D v3.2 only if you specifically want a Box2D-v2-style engine with a pointer-free C++17 value-semantic API, a pluggable Real type or typed units; Box2D v3 is maintained and multithreaded. Jolt Physics, Bullet, ODE and PhysX are 3-D engines and not substitutes for a 2-D game engine.

## Integration

| | |
|---|---|
| **Form** | static lib (or shared lib with PLAYRHO_BUILD_SHARED), built with CMake |
| **Dependencies** | none for the library (C++17 standard library only); optional Boost for experimental units; the benchmark uses the googlebench git submodule; Box2D only if you edit the BENCHMARK_BOX2D define |
| **Minimum toolchain** | C++17 compiler, CMake 3.16.3+ |
| **Platforms** | any; CI builds and tests on Linux, macOS and Windows |
| **Thread safety** | not documented; one World is stepped single-threaded, and calling Step or mutators while the world is locked (for example from a contact listener during Step) throws WrongState |
| **Drop-in for the baseline** | no |

## Gotchas

- Small-N rows are dominated by a fixed Box2D overhead: Box2D 2.4.1's World::Step runs five b2Timer profiling scopes on every non-zero step (10 gettimeofday calls on Linux/macOS), which PlayRho does not have. An empty world steps in 74 ns (PlayRho) vs 404 ns (Box2D), so ratios like DropDisks/1 (2.7x) or WorldStepWithStatsStatic/0 (5x) say little; only the N=1000 and N=10000 rows measure engine work.
- AddPairStressTest numbers swing by an order of magnitude across commits. Issue #477 (open) reports that commit 8082f1c (the Fixture-to-pair&lt;BodyID,ShapeID&gt; transition, which also enabled the Box2D benchmarks) made steps 16-20 of AddPairStressTestPlayRho400 11-38x slower. The author cannot tell whether this is a regression or the fix of an earlier bug that did less TOI work. The wiki's 100x row (00991d1ec) predates that commit; the cited 2.2x row (ef285b19a) follows it. Step 0 of the same test has PlayRho 1.6x slower (2.36 ms vs 1.46 ms).
- The TilesRest benchmarks time world construction plus however many steps it takes for every body to fall asleep. They mix per-step cost with each engine's settling and sleep behaviour, so they are not a per-step throughput comparison.
- The Box2D build is unstated, and Box2D 2.4.1's CMakeLists sets no default build type, so a plain single-config build is unoptimized, whereas PlayRho's CMake defaults to Release with -O3. Box2D winning the contact-heavy TilesRestComboGround rows suggests it was optimized in the wiki run, but this is not documented.

## Known shortcomings

- First-party Google Benchmark output on the wiki (not linked from README): toy scenes (static-only world, contact-free disks), Box2D build unstated, loses TilesRestComboGround, compared only with Box2D v2. Stale since 2024-04-30.
- Enricher: Box2D 2.4.1's Step runs 5 b2Timer scopes (10 gettimeofday calls) per step (empty world 74 ns vs 404 ns), so small-N ratios are meaningless (DropDisks/1 2.7x, WorldStepWithStatsStatic/0 5x); TilesRest times world build plus steps until all bodies sleep, mixing settling with per-step cost; open issue #477: commit 8082f1c made AddPairStressTest steps 16-20 11-38x slower (the cited 2.2x row comes after it, the 100x row before it; at step 0 PlayRho is 1.6x slower, 2.36 vs 1.46 ms); Box2D 2.4.1 CMake has no default build type (unoptimized by default) vs PlayRho Release -O3, Box2D build undocumented; measured code is the unreleased master line, not v1.1.2.

## Caveats and trade-offs

First-party numbers from the project's GitHub wiki page; neither the README (which says only that the project is 'benchmark assessed', linking to Wikipedia) nor Benchmark/README.md links to it. Compiler, flags and build type are not stated for the run (Benchmark/README.md recommends -DCMAKE_BUILD_TYPE=Release and warns 'Don't put much weight into these results unless you're clear on the code that's being timed'); the hardware is only '2.6 GHz Intel Core i7', 8 X 2600 MHz CPUs. The Box2D rows exist only if BENCHMARK_BOX2D is defined by editing Benchmark/BenchmarkMain.cpp (the define is commented out at line 85) and Box2D is linked by hand with an unstated build; Box2D 2.4.1 is named for the earlier 00991d1ec run, not for the ef285b19a run. The scenes are small microbenchmarks: WorldStepWithStatsStatic steps a world of shapeless static bodies only, and in DropDisks the disks are spaced 2 m apart with radius 0.5 so no contacts form (measures integration and broad phase, not contact solving). PlayRho's default StepConf uses 8 velocity and 3 position iterations, matching Box2D's Step(1/60, 8, 3). The same page's earlier run (commit 00991d1ec) showed PlayRho about 100x faster on AddPairStressTest400/18 (1,120,420 ns vs 104,630,145 ns), which the author called surprising and not trustworthy; the later run gives 2.2x. Wins are mixed: PlayRho loses both TilesRestComboGround rows (/12 by about 1.2x, /36 by about 1.07x). The only comparison is against Box2D v2, its own ancestor (PlayRho began as a port of Box2D 2.3.2); no comparison with Box2D v3 exists. Last commit 2024-04-30, so stale. [retier] Box2D 2.4.1 Step has 10 gettimeofday calls per step (empty world 74 vs 404 ns); Box2D build type undocumented (CMake default unoptimized) vs PlayRho Release -O3; TilesRest times build plus settling; issue #477 commit 8082f1c made AddPairStressTest steps 16-20 11-38x slower, PlayRho 1.6x slower at step 0; measured code is unreleased master, not v1.1.2; stale since 2024-04-30.

2-D only; began as a port of Box2D 2.3.2 and is now a derivative with a different API (value semantics, no pointers, strongly typed units optional, configurable Real type including double and fixed point). Master branch interface is not stable (use tagged releases or release branches). Needs a C++17 compiler.

## Maintenance

Stale since 2024-04-30 with an unreleased, API-breaking 2.0 master line (latest tag v1.1.2); Zlib-licensed and self-contained, so vendoring a tagged release is easy, but no published benchmark covers a tagged release or Box2D v3.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark output on the project wiki (benchmark code public in Benchmark/BenchmarkMain.cpp, Box2D rows behind the commented-out BENCHMARK_BOX2D define), but no compiler, flags, build type or exact CPU model, so C.
- **Verifier notes:** All claimed rows match the wiki's ef285b19a run exactly; tier C holds (first-party, no compiler, flags, build type or CPU model). Shortcomings: degenerate microbenchmark scenes (static-only world, contact-free disks), Box2D build and version unstated for the cited run, mixed results (loses TilesRestComboGround), only compared with the older Box2D v2 line, stale since 2024-04-30. Fixed caveat: the README does not point to the wiki benchmark page.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-175 (wave 8); enricher w8 pair-032
- **Pages the verifier opened:**
  - <https://github.com/louis-langholtz/PlayRho/wiki/Benchmark-Data:-2.6-GHz-Intel-Core-i7>
  - <https://github.com/louis-langholtz/PlayRho>
  - <https://github.com/louis-langholtz/PlayRho/commits>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/README.md>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Benchmark/BenchmarkMain.cpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Benchmark/README.md>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/StepConf.hpp>
- **Sources the enricher read:**
  - <https://github.com/louis-langholtz/PlayRho>
  - <https://github.com/louis-langholtz/PlayRho/wiki/Benchmark-Data:-2.6-GHz-Intel-Core-i7>
  - <https://github.com/louis-langholtz/PlayRho/commits/master>
  - <https://github.com/louis-langholtz/PlayRho/releases>
  - <https://github.com/louis-langholtz/PlayRho/issues>
  - <https://github.com/louis-langholtz/PlayRho/issues/477>
  - <https://github.com/louis-langholtz/PlayRho/commit/8082f1c>
  - <https://github.com/louis-langholtz/PlayRho/commit/ef285b19a>
  - <https://github.com/louis-langholtz/PlayRho/tree/master/Library/include/playrho>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/README.md>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Benchmark/README.md>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Benchmark/BenchmarkMain.cpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/CMakeLists.txt>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/StepConf.hpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/Real.hpp.in>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/Settings.hpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/ObjectPool.hpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/d2/AabbTreeWorld.hpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/source/playrho/d2/AabbTreeWorld.cpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Library/include/playrho/d2/World.hpp>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/louis-langholtz/PlayRho/HEAD/Changes.md>
  - <https://raw.githubusercontent.com/erincatto/box2d/v2.4.1/src/dynamics/b2_world.cpp>
  - <https://raw.githubusercontent.com/erincatto/box2d/v2.4.1/src/common/b2_timer.cpp>
  - <https://raw.githubusercontent.com/erincatto/box2d/v2.4.1/CMakeLists.txt>
  - <https://raw.githubusercontent.com/erincatto/box2d/v2.4.1/src/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/louis-langholtz/playrho`) · [data/wave8/enrich/raw/github_com_louis_langholtz_playrho.json](../../../data/wave8/enrich/raw/github_com_louis_langholtz_playrho.json) (enrichment confidence 0.7)

</details>
