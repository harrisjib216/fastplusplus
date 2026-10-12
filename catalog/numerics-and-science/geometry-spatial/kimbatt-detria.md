# detria

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT OR WTFPL` · 🟡 stale

> Single-header C++17 constrained Delaunay triangulator with exact predicates; about 1.5-3x faster than CDT on polygon outlines, close to Triangle.

| | |
|---|---|
| **Beats** | CDT (artem-ogre/CDT) and poly2tri; Triangle (CMU) is also in the comparison but is faster on random point sets |
| **Claimed result** | Medians from the 23 per-case SVG result files embedded in BENCHMARKS.md (images/benchmark/\*.svg), detria vs CDT vs Triangle in ms: world land outline (407,072 vertices) 502 vs 1431 vs 441; United States outline 24.4 vs 58.8 vs 27.2; Afghanistan (1,532 vertices) 0.74 vs 2.17 vs 0.87; 10,000-vertex debug2.dat 11.6 vs 28.7 vs 12.5. Over the 23 files, detria is faster than CDT in 21 (about 1.5x to 3.2x, derived from page data) and faster than poly2tri in all 14 cases poly2tri supports (about 1.05x to 2.2x, derived from page data). It is faster than Triangle in 16 of 23: the 13 country outlines, city.dat, debug2.dat and the depth-4 fractal (1.66 vs 1.73 ms), by about 1.04x to 1.3x (derived from page data). It is slower than Triangle on all four random-point sets (1,000,000 points: 1798 vs 946 ms) and on the world land outline (502 vs 441 ms). It is slower than both Triangle and CDT on the depth-6 and depth-8 cocircular fractals (depth 8: 3091 vs 1407 CDT vs 857 Triangle). |
| **Workload** | Constrained Delaunay triangulation timing (set-up and result retrieval excluded) on Natural Earth country outlines, poly2tri test files, a cocircular fractal, and 1,000 to 1,000,000 random points inside a square; box plots of repeated runs. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3900X, Windows 10 |
| **Compiler and flags** | Clang 17.0.3 (MSVC-like command line), release build with default compiler flags |
| **Adoption** | 13 stars |
| **Last commit** | 2025-03-02 |
| **Links** | [repository](https://github.com/Kimbatt/detria) · [benchmark](https://raw.githubusercontent.com/Kimbatt/detria/HEAD/BENCHMARKS.md) |

## Verdict

BENCHMARKS.md box plots (Clang 17.0.3 clang-cl, CMake Release defaults, Ryzen 9 3900X, Windows 10; CDT 58f34da, poly2tri 13d64e7, vendored Triangle with 'pzQ') time constrained triangulation of 13 Natural Earth outlines, poly2tri test files, cocircular fractals and random points. Medians: world land outline 502 ms vs CDT 1431 and Triangle 441; United States 24.4 vs 58.8 and 27.2; 1M random points 1798 vs Triangle 946. detria's timed region also includes copying out the result triangles, which the other three exclude, so this part is conservative against detria. The images were committed 2024-05-03, six days before a correctness fix (b15d5e2, 'last triangle around a constrained edge not always being delaunay'), so the published numbers predate that fix.

## Use it when

- Triangulating polygon outlines with holes from GIS or vector data (country borders, map tiles): detria beat CDT on 21 of 23 benchmark inputs (about 1.5-3.2x) and Triangle on all 13 country outlines by 4-30%
- Replacing poly2tri: it was faster on all 14 inputs poly2tri could run (about 1.05-2.2x) and also handles multiple outlines, which poly2tri cannot
- Projects that want a permissively licensed (MIT or WTFPL) drop-in single header instead of Triangle, whose license forbids commercial use without permission
- Engines and tools that need exact results on degenerate input (collinear and cocircular points) and custom allocators or point types without copying data
- C#/Unity projects that want the same algorithm via the bundled detria.cs port

## Skip it when

- Unconstrained Delaunay of large random point sets: Triangle was about 1.9x faster at 1,000,000 points (946 vs 1798 ms) and faster at every random-set size tested
- Inputs with many cocircular points: on the depth-8 fractal detria took 3091 ms vs CDT 1407 ms and Triangle 857 ms
- Mesh generation needing refinement, quality constraints, conforming Delaunay or automatic Steiner insertion: adding new points is a stated non-goal
- Dirty input with intersecting or overlapping constraint edges, or points lying exactly on a constraint: triangulate() fails (ConstrainedEdgeIntersection, PointOnConstrainedEdge) instead of splitting edges, and duplicate points are also an error
- Workloads needing incremental updates (insert or remove points after triangulation) or multi-threaded construction: neither is offered

## How it is fast

Points are sorted by x then y with a non-recursive quicksort, then inserted left to right in a sweep: each new point is joined to the visible part of the current convex hull, and Lawson edge flips restore the Delaunay property. Each constrained edge is inserted by walking the triangles it crosses, deleting them and re-triangulating the two cavity polygons on either side, followed by more flips. Inside/outside/hole classification is a pass over a compact half-edge topology. Shewchuk's adaptive robust orient2d and incircle predicates keep it exact without exact-arithmetic kernels.

## Compared with alternatives

Pick detria for constrained triangulation of polygons with holes under a permissive license in one header. For plain point-set Delaunay, Delaunay32 (beats Triangle 1.6, CDT and Fade2D, multi-threaded) or Triangle itself are faster. pgl targets CGAL-style kernels with a broader geometry API.

## Integration

| | |
|---|---|
| **Form** | header-only (include/detria.hpp; optional C++20 module detria.cppm) |
| **Dependencies** | none (C++ standard library only); Shewchuk's public-domain robust predicates are embedded |
| **Minimum toolchain** | C++17 (C++20 for the module build; the repo's CMake asks for 3.30 but only the tests and benchmarks need it) |
| **Platforms** | any (portable C++; the benchmarks ran on Windows with clang-cl, the repo has Linux compile-test scripts, and an Emscripten build path exists for the benchmark) |
| **Thread safety** | Documented: no global state, so separate Triangulation objects can run on separate threads; one object allows many concurrent const calls or exactly one mutating call (e.g. triangulate). |
| **Drop-in for the baseline** | no |

## Gotchas

- setPoints and addOutline store pointers, not copies: the vectors must stay alive and unreallocated until triangulate() returns (DOCS.md shows both crash patterns)
- Robust predicates break under -ffast-math or /fp:fast; the docs say to disable those flags. With integer coordinates, overflow is only checked in debug builds
- Errors are reported by triangulate() returning false plus getError()/getErrorMessage(), not exceptions. Index and NaN checks can be disabled in the config, after which bad input is undefined behaviour
- The default Idx is uint32_t, and the half-edge structure needs the edge count below half of Idx's maximum (e.g. 32767 edges with 16-bit indices)

## Known shortcomings

- Loses to Triangle on random points, the world outline and deep fractals (wins listed in the record omitted the depth-4 fractal, now fixed).
- Benchmark images were committed 2024-05-03, six days before correctness fix b15d5e2 (last triangle around a constrained edge not always Delaunay), so the numbers were measured on code later fixed for correctness (retiered to C). Detria's timed region includes copying out result triangles while CDT/Triangle/poly2tri exclude it (conservative for detria, opposite of BENCHMARKS.md). README supports manual Steiner points; only auto-insertion/refinement is a non-goal.

## Caveats and trade-offs

Mixed result. The library beats CDT and poly2tri on most inputs. Against Triangle it wins only by 4-30% on country outlines, poly2tri test files and the small fractal, and it loses on random points (up to about 1.9x slower at 1M points), the world land outline and the deeper fractals (3.6x slower than Triangle at depth 8). 'Default compiler flags' means the CMake Release defaults for clang-cl, not explicit flags. Baseline versions are pinned in src/benchmark/CMakeLists.txt (CDT 58f34da, poly2tri 13d64e7, Triangle vendored), but no release numbers are given. The machine is a single 2019 Windows desktop. Neither CDT nor poly2tri is the category's incumbent, and CGAL, Boost.Geometry and GEOS are not compared. Triangle's own license is non-commercial; detria is MIT or WTFPL, so this does not affect detria. The benchmark images date from 2024 (last benchmark-image commit 2024-05-03), and later commits changed the code.

Single-header CDT with a C# port; no point insertion after triangulation, no Steiner or refinement (stated non-goal). CDT and poly2tri versions are not stated. Triangle is still faster for generic point sets.

## Maintenance

Stale but recently touched: the last commit (2025-03-02) added the C# port, and the algorithm itself last changed in June 2024 (February 2025 only added C++20 module support). Only two issues are open (CI setup, a feature request). MIT/WTFPL single header that is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** BENCHMARKS.md states the compiler (Clang 17.0.3, MSVC-like command line), the build (release with default compiler flags, i.e. the CMake Release defaults) and the CPU (AMD Ryzen 9 3900X, Windows 10). The benchmark code is public in src/benchmark (main.cpp, triangulator_benchmark.cpp, impl/detria.cpp, impl/cdt.cpp, impl/poly2tri.cpp, impl/triangle.cpp). src/benchmark/CMakeLists.txt pins CDT and poly2tri by git commit, and Triangle is vendored in src/benchmark/3rdParty/triangle.
- **Retiered** A to C: Published benchmark images (2024-05-03) predate correctness fix b15d5e2 (2024-05-09: last triangle around a constrained edge not always Delaunay); project rule puts numbers measured on code later fixed for correctness at C until re-measured.
- **Verifier notes:** I parsed all 23 SVG result files from raw.githubusercontent.com and re-tallied the medians. Every number in the record matches. The only error was the list of Triangle wins, which left out the depth-4 fractal. License, stars (13), last commit (2025-03-02) and stale status all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/images/benchmark/ne_10m_land.txt.svg>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/images/benchmark/1000000%20random%20points.svg>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/images/benchmark/fractal,%208%20depth.svg>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/CMakeLists.txt>
  - <https://github.com/Kimbatt/detria>
  - <https://github.com/Kimbatt/detria/commits>
  - <https://github.com/Kimbatt/detria/tree/master/src/benchmark>
- **Sources the enricher read:**
  - <https://github.com/Kimbatt/detria>
  - <https://github.com/Kimbatt/detria/commits>
  - <https://github.com/Kimbatt/detria/commits/master?since=2024-05-04&until=2024-06-02>
  - <https://github.com/Kimbatt/detria/commit/b15d5e2af0fba6eca552fe7b49f59b5bdd961625>
  - <https://github.com/Kimbatt/detria/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/DOCS.md>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/LICENSE-MIT.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/include/detria.hpp>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/impl/detria.cpp>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/impl/cdt.cpp>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/impl/triangle.cpp>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/src/benchmark/impl/poly2tri.cpp>
  - <https://raw.githubusercontent.com/Kimbatt/detria/HEAD/csharp/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kimbatt/detria`) · [data/wave8/enrich/raw/github_com_kimbatt_detria.json](../../../data/wave8/enrich/raw/github_com_kimbatt_detria.json) (enrichment confidence 0.8)

</details>
