# earcut.hpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `ISC` · 🟢 active

> Header-only C++ ear-slicing polygon triangulator (port of Mapbox earcut.js); about 1.6x faster than the JS original on tile polygons.

| | |
|---|---|
| **Beats** | earcut.js, the original JavaScript implementation (\~445 ms for the same set in its README); test/bench.cpp also times libtess2 v1.0.2 on 9 small fixtures but publishes no results; CGAL and libtess2 are called 'slower and larger' in the README without numbers. |
| **Claimed result** | README: 119,680 real-world MVT polygons (1.9M vertices, map-tile window at zooms 4-16) triangulated in \~276 ms on a MacBook Pro M1 Pro (2021), 'noticeably faster than the JS original'; optional Delaunay refinement adds \~98 ms. The earcut.js README states \~445 ms (refinement \~168 ms) for the same 119,680-polygon set on the same MacBook Pro M1 Pro (2021), so earcut.hpp is about 1.6x faster than earcut.js (refinement about 1.7x) (derived from page data across the two READMEs; Node version and C++ compiler/flags not stated). |
| **Workload** | Triangulating 119,680 real-world polygons (1.9M vertices) cut from Mapbox Vector Tile windows at zooms 4-16, whole set timed. |
| **Metric** | latency |
| **Hardware** | MacBook Pro M1 Pro (2021) |
| **Compiler and flags** | Not stated for the 276 ms figure; CMakeLists.txt defaults to CMAKE_BUILD_TYPE=Release with C++17 for the bench and no -march (compiler unspecified). |
| **Adoption** | 1.0k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/mapbox/earcut.hpp) · [benchmark](https://github.com/mapbox/earcut.hpp) |

## Verdict

The only quantified comparison is against its own JavaScript original: 119,680 real-world Mapbox Vector Tile polygons (1.9M vertices) triangulate in about 276 ms in C++ against about 445 ms in earcut.js on the same MacBook Pro M1 Pro (2021), about 1.6x (refine pass 98 vs 168 ms, about 1.7x), derived across the two READMEs; the compiler, flags and Node version are not stated. No C++ baseline (libtess2, CGAL, poly2tri) has published numbers.

## Use it when

- Real-time triangulation of map or vector-tile polygons (buildings, water, land use) for GPU rendering, the workload it is tuned for: about 120k MVT polygons with 1.9M vertices in about 276 ms on an M1 Pro.
- You need a dependency-free, ISC-licensed single header that builds as C++14 and takes your own point and container types without copying.
- Input is already valid (no self-crossing rings, holes inside the outer ring, no duplicate or zero-length edges) and small or medium polygons dominate.
- You want the C++ output to match earcut.js: PR #132 reports bit-identical results against the JS fixtures, so the same data triangulates the same way in browser and native code.
- Rendering can accept slivers, or you can pay roughly 35% more time (98 ms on top of 276 ms in the README) for the opt-in Delaunay-style refine pass.

## Skip it when

- Correctness on dirty input matters: on self-intersecting or overlapping rings the README warns of overlapping triangles, gaps or triangles outside the polygon. Clean the input first, or use a robust tessellator such as libtess2 or CGAL.
- Meshing for FEM, navmeshes or simulation: the output is not conforming (T-junctions), and refine() only approximates a constrained Delaunay triangulation with non-robust predicates.
- You need a conforming constrained Delaunay triangulation or point-set Delaunay: use a CDT library (detria, CDT) or delaunator-cpp instead.
- 3D or non-planar input: only x and y are read, so you must project to a plane first.
- You chose it for a measured C++-vs-C++ speedup: none is published. bench.cpp times libtess2 v1.0.2 on 9 small fixtures but reports no results, so benchmark your own data.

## How it is fast

Modified ear slicing (after Held's FIST and Eberly's ear clipping) on an intrusive doubly linked vertex list taken from a block object pool. Once the input exceeds 80 vertices, vertices are hashed onto a z-order (Morton) curve over a 32767-unit grid, so the point-in-ear test only visits nearby vertices. Hole bridging (eliminateHoles/findHoleBridge) skips whole blocks using one bounding box per 16 ring edges, a fix for slowdowns on polygons with many holes (issue #124, PR #132). refine() runs Lawson edge flips with non-robust orient/inCircle predicates on thread-local scratch buffers.

## Compared with alternatives

Pick earcut.hpp over detria or Delaunay32 when you triangulate many small, already-valid polygons for rendering and want a single dependency-free header whose output matches earcut.js. Pick detria when you need a robust constrained Delaunay result, and delaunator-cpp or Delaunay32 for point-set Delaunay.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (the C++ standard library only; GoogleTest, Google Benchmark, libtess2 and GLFW are fetched only for tests, the bench and the visualizer) |
| **Minimum toolchain** | C++14 for the shipping header (per a CMakeLists.txt comment); the tests, bench and visualizer need C++17 (GCC 9+, Clang 10+, MSVC 2019+) and CMake 3.16+ |
| **Platforms** | any (portable C++, no SIMD or intrinsics); CI status for non-x86 is not documented, and older issues #97 and #103 reported test failures on aarch64, ppc64le and s390x (closed 2025-09-18) |
| **Thread safety** | Not documented explicitly. From the source: each mapbox::earcut() call builds its own detail::Earcut object with no shared state, so concurrent calls are safe; refine() keeps its scratch buffers in a static thread_local object. |
| **Drop-in for the baseline** | no |

## Gotchas

- Output indices refer to all input vertices concatenated ring after ring. refine() needs a flat coords container in that same order, so you must flatten nested rings yourself; the PR #132 discussion measured nested-ring lookups as 2.7x to 5.2x slower than flat coordinates in refine.
- N defaults to uint32_t. Pass uint16_t only if the total vertex count stays within 65536; there is no documented overflow check.
- The free function allocates a new node pool and index vector on every call. Buffer reuse across calls exists only on mapbox::detail::Earcut, which is not a public API.
- The README promises bit-identical output across compilers for earcut but not for refine(). The project's own tests are built with -ffp-contract=off, so use that flag if you need identical indices across platforms.

## Known shortcomings

- README only says 'noticeably faster than JS' (\~1.6x vs earcut.js on the same M1 Pro, derived). bench.cpp compares libtess2 on 9 small fixtures with unpublished results; no CGAL/poly2tri/Triangle comparison. Compiler not stated. Correctness is not guaranteed on invalid input by design (T-junctions possible).
- The only measured speedup is against its own JS original, about 1.6x (276 vs 445 ms on an M1 Pro); bench.cpp times libtess2 v1.0.2 on 9 small fixtures but publishes no results. The header builds as C++14 while tests and bench need C++17. Not correct on invalid input and the output is not conforming. Issue #124 (slowdown with many holes) fixed by PR #132.

## Caveats and trade-offs

The only quantified baseline is the same-algorithm JS original (about 1.6x, derived across two READMEs on the same machine), a weak result. test/bench.cpp registers BM_LibtessTriangulation (libtess2 v1.0.2 fetched by CMake) only on 9 whitelisted fixtures (building, dude, water, water2, water3, water3b, water4, water_huge, water_huge2); the 119,680-polygon tile benchmark (BM_EarcutTiles) has no libtess2 or other C++ counterpart, and no libtess2 results are published, so the C++ comparison needs a local run. No CGAL, poly2tri or Triangle measurement. Compiler and flags for the 276 ms figure are not stated. By design earcut does not guarantee a correct triangulation: the README says that on invalid input (self-crossing or overlapping rings, holes outside the outer ring, duplicate or zero-length edges) the output can contain overlapping triangles, gaps or triangles outside the polygon; the output is not conforming (T-junctions), and refine() uses non-robust predicates.

Header-only C++14 polygon triangulator (ear slicing with z-order curve and spatial hashing). Trades quality and guaranteed correctness for speed: assumes valid polygons, output is not conforming (T-junctions) and not Delaunay unless the opt-in mapbox::refine pass is used (that pass uses non-robust predicates). README points to CGAL or libtess2 when correctness on bad input is needed.

## Maintenance

Actively maintained (last commit 2026-09-28, synced to earcut 3.2.4, 0 open issues). ISC-licensed single header, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party: the benchmark code is public (test/bench.cpp BM_EarcutTiles) and the CPU is stated (M1 Pro), but compiler and flags for the 276 ms figure are not, and the README gives the JS comparison only qualitatively (the JS number sits in the earcut.js README), so C.
- **Verifier notes:** Measures its own speed only against the JS original (earcut.js; \~276 vs \~445 ms on the same M1 Pro, ratio derived across READMEs); bench.cpp has an unpublished libtess2 comparison on small fixtures only; no CGAL/Triangle/poly2tri numbers. Metadata checked: ISC, 1.0k stars, last commit 2026-09-28, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/README.md>
  - <https://github.com/mapbox/earcut.hpp>
  - <https://github.com/mapbox/earcut.hpp/commits>
  - <https://github.com/mapbox/earcut.hpp/tree/master/test>
  - <https://github.com/mapbox/earcut.hpp/tree/master/test/comparison>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/test/bench.cpp>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/test/fixtures/geometries.hpp>
  - <https://raw.githubusercontent.com/mapbox/earcut/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/include/mapbox/earcut.hpp>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/test/bench.cpp>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mapbox/earcut.hpp/v2.2.4/README.md>
  - <https://raw.githubusercontent.com/mapbox/earcut/HEAD/README.md>
  - <https://github.com/mapbox/earcut.hpp>
  - <https://github.com/mapbox/earcut.hpp/issues?q=is%3Aissue>
  - <https://github.com/mapbox/earcut.hpp/issues/124>
  - <https://github.com/mapbox/earcut.hpp/issues/116>
  - <https://github.com/mapbox/earcut.hpp/pull/132>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mapbox/earcut.hpp`) · [data/wave8/enrich/raw/github_com_mapbox_earcut_hpp.json](../../../data/wave8/enrich/raw/github_com_mapbox_earcut_hpp.json) (enrichment confidence 0.8)

</details>
