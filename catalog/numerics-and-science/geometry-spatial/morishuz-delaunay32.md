# Delaunay32

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Parallel exact-integer 2D (constrained) Delaunay triangulator for int32 points; about 4.4x faster than Triangle single-threaded on 1M points.

| | |
|---|---|
| **Beats** | Triangle 1.6 (also CDT 1.4.5, delaunator-cpp c1521f6 and Fade2D 2.17.3; CGAL not compared) |
| **Claimed result** | Delaunay32 45.4 ms at 8 threads and 131.6 ms single-threaded vs Fade2D 235.2 ms (automatic threads) / 314.1 ms (1 thread), delaunator-cpp 542.0 ms, Triangle 1.6 584.0 ms, CDT 1.4.5 988.7 ms; README relative runtimes 1.0x, 2.9x, 5.2x, 6.9x, 11.9x, 12.9x, 21.8x. Single-thread Delaunay32 vs Triangle about 4.4x and vs CDT about 7.5x (derived from page data). |
| **Workload** | 2D Delaunay triangulation of one million unique, unconstrained signed 32-bit integer points, triangle-only output. |
| **Metric** | latency |
| **Hardware** | Apple M1 (8 cores, 16 GB RAM) |
| **Compiler and flags** | Not stated. The repo's top-level CMake defaults to a Release build when no build type is given; the competitors' build settings are not stated. |
| **Adoption** | 191 stars |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/morishuz/delaunay32) · [benchmark](https://github.com/morishuz/delaunay32) |

## Verdict

The README table (first-party, Apple M1, 8 cores, 16 GB) times 1M unique uniform integer points with triangle-only output: Delaunay32 131.6 ms single-threaded and 45.4 ms on 8 threads, versus Fade2D 2.17.3 314.1 ms (1 thread) / 235.2 ms (auto), delaunator-cpp 542.0 ms, Triangle 1.6 584.0 ms and CDT 1.4.5 988.7 ms, so about 4.4x over Triangle and 7.5x over CDT single-threaded (derived from page data). Compiler, flags and how competitors were fed (floats or ints, conversion timed or not) are not stated, and the competitor harness was removed from the repo in 0.6.0; the remaining benchmark times only Delaunay32, end to end including input ingestion and triangle output, on a [0, 100,000) square domain.

## Use it when

- Large unconstrained 2D point sets (around 10^5-10^6+ points) already on, or easily snapped to, an integer grid, such as GIS coordinates in fixed units, pixel/voxel positions or quantized CAD data, where you want exact robustness without floating-point predicate filters
- Multicore machines where a parallel 2D Delaunay helps: the README reports 45.4 ms on 8 threads versus 131.6 ms single-threaded for 1M points on an Apple M1
- Constrained Delaunay of polygon domains with holes, or several disjoint domains at once, when you need a permissive (MIT) dependency-free library instead of commercial Fade2D or Triangle's non-commercial licence
- Repeated triangulations in a loop: a Triangulator keeps its allocations and worker threads across set_points() calls
- Browser use via the separate delaunay32-wasm package

## Skip it when

- Floating-point data that must be triangulated at its native precision: input is quantized to int32, which can merge distinct points (collisions are reported) and moves vertices by the reported coordinate error
- Quality mesh generation (minimum-angle refinement, area constraints, Steiner points, intersecting constraints): Triangle or CGAL's mesher still fit; Delaunay32 rejects crossing constraints and inserts no Steiner points
- Coordinates spanning nearly the full int32 range on both axes: certified spans top out around 1.94e9 per axis for a square domain with __int128 (derived from the source bounds), and inputs outside the certified range throw
- MSVC or other compilers without __int128: the certified span drops to 65,535 (about 29,600 for a square domain, derived from the source), and the repo's own benchmark shrinks its domain from 100,000 to 20,000 there
- Dynamic insertion/deletion, 3D, or anything needing a stable ABI: it is a batch 2D triangulator, pre-1.0, and 0.7.0 changed the Triangulator binary layout

## How it is fast

The core is a Guibas-Stolfi style divide-and-conquer Delaunay over a quad-edge-like dart structure (connect/splice/sym with in-circle-driven hull merges), with points ordered by a radix-sorted Morton (Z-order) key so splits alternate direction and subproblems stay spatially compact. Leaves of up to 16 points are built directly, and leaves whose local span is small use 64-bit lifted predicates even when the global span needs 128-bit ones. Parallelism splits the Morton tree into about four jobs per thread (minimum 16,384 points per job, parallel path only above 50,000 points), builds subtrees on a persistent worker team with a pre-sized edge arena, and merges level by level; arena exhaustion falls back to the growable serial path. Predicates are exact integer arithmetic with the width (int64 or __int128) chosen from the input's coordinate spans, so no floating-point filters or adaptive expansions are needed.

## Compared with alternatives

Pick Delaunay32 over detria when you have large point clouds and can use integer coordinates and multiple threads; detria takes floating-point input, is header-only and targets polygon/outline triangulation against CDT and poly2tri. Pick pgl when you need CGAL-like 2D kernels (exact rationals, arrangements, hulls) rather than a dedicated parallel triangulator, and jc_voronoi when you need the Voronoi diagram itself.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none beyond the C++ standard library and platform threads (Threads::Threads); the optional delaunay32::extras target adds JSON, sampling and SVG helpers with no third-party code |
| **Minimum toolchain** | C++17, CMake 3.16+; __int128 support (GCC/Clang) is needed for the wide coordinate range |
| **Platforms** | Portable C++17; CI builds on ubuntu-latest, macos-latest and windows-latest (MSVC) with ASan/UBSan and TSan jobs; WebAssembly build in a separate repo; no SIMD intrinsics |
| **Thread safety** | One Triangulator must not be called concurrently; use one instance per concurrent problem. Internally multithreaded when thread_count is 0 (hardware threads) or above 1; the default is serial. |
| **Drop-in for the baseline** | no |

## Gotchas

- triangulate() consumes the configured problem even when it throws; you must call set_points() again (and resubmit constraints and polygons) before the next run
- thread_count defaults to 1 (serial); set 0 to use all hardware threads, and inputs below 50,000 points stay serial regardless
- Coincident points collapse to the lowest input index; three or more collinear points return no triangles; cocircular inputs have more than one valid answer, so do not compare outputs edge-for-edge against another library
- Pre-1.0 API churn: 0.3.0 and 0.6.0 removed whole entry-point families without compatibility wrappers, and 0.7.0 requires consumers to rebuild

## Known shortcomings

- Competitor harness not public (CHANGELOG 0.6.0 removed it); the 'input conversion excluded' claim is not on the page.
- Without __int128 (MSVC) the certified span drops to 65,535 (\~29.6k for a square domain, derived from source) and the repo's own bench shrinks its domain to 20,000 there. Full int32 span not accepted even with int128 (max \~1.94e9 per axis, derived). Competitor harness removed in 0.6.0, so the claim is not reproducible from the current repo.

## Caveats and trade-offs

First-party README table for one distribution and size (1M uniform unique integer points, triangle-only output). The harness that ran Fade2D, delaunator-cpp, Triangle and CDT is not in the repo: benchmarks/benchmark.cpp times only Delaunay32, and CHANGELOG 0.6.0 removed the Delaunator adapter and the competitor benchmark columns. Compiler, flags and competitor build settings are not stated. Delaunay32 accepts only int32 coordinates (floats go through quantize()); the README does not say how the competitors were fed or whether conversion was timed. Fade2D is commercial. CGAL, the named incumbent, is not in the comparison. Very new repo (oldest visible commit 2026-08-02, 48 commits).

Signed 32-bit integer coordinates only (floats go through an explicit quantize step); exact integer predicates; serial or shared-memory parallel; constraints and polygon domains with holes; MIT, no third-party source dependencies; WebAssembly build exists.

## Maintenance

Very young but active (48 commits since August 2026, 0.7.0 released 2026-09-14, 191 stars, no issues filed), MIT-licensed with no third-party code, and small enough to vendor; expect breaking changes until 1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README performance table (Apple M1, 1M unique integer points) matches the record exactly, including Triangle 1.6 at 584.0 ms vs 131.6 ms single-thread. The repo's benchmarks/benchmark.cpp measures only Delaunay32 (CHANGELOG 0.6.0 removed the embedded competitor baseline), so the competitor code, compiler and flags are not public. First-party, so C.
- **Verifier notes:** All README numbers and the single-thread ratios vs Triangle (4.4x) and CDT (7.5x) check out. Metadata from the repo page: MIT, 191 stars, 8 forks, not a fork, last commit 2026-09-14 (Release 0.7.0). The record's claim that 'input conversion is excluded' is not on the current README, so it was dropped from caveats.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/morishuz/delaunay32>
  - <https://github.com/morishuz/delaunay32/commits>
  - <https://github.com/morishuz/delaunay32/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/README.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/benchmarks/benchmark.cpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/THIRD_PARTY.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/CHANGELOG.md>
- **Sources the enricher read:**
  - <https://github.com/morishuz/delaunay32>
  - <https://github.com/morishuz/delaunay32/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/README.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/THIRD_PARTY.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/docs/usage.md>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/benchmarks/benchmark.cpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/topology.cpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/delaunay.cpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/internal.hpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/triangulator_impl.hpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/edge_arena.hpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/src/worker_team.cpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/include/delaunay32/delaunay.hpp>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/.github/workflows/ci.yml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/morishuz/delaunay32`) · [data/wave8/enrich/raw/github_com_morishuz_delaunay32.json](../../../data/wave8/enrich/raw/github_com_morishuz_delaunay32.json) (enrichment confidence 0.75)

</details>
