# pgl (Pangolin plane geometry library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only, exact 2D geometry library (MIT) that beats CGAL on segment intersection, arrangements and unions, loses on Delaunay.

| | |
|---|---|
| **Beats** | CGAL 6.1.2 (Delaunay_triangulation_2, convex_hull_2, Kd_tree, AABB_tree, Arrangement_2, General_polygon_set_2, minkowski_sum_2; EPECK and EPICK kernels) |
| **Claimed result** | Ratios are pgl time / CGAL time (below 1 = pgl faster), median over input sizes, range in parentheses, averaged over two machines. ERational vs EPECK, pgl faster: regularized union of triangles 0.23x (0.20-0.59), arrangement point-location query 0.46x (0.32-0.84), segment intersection 0.55x (0.19-1.8), arrangement point-location build 0.61x (0.46-0.87), segment search count in Rectangle 0.68x (0.55-0.91); near parity: nearest-neighbour query 0.82x (0.63-1.1), kd-tree build 0.88x (0.63-1.4), visibility 0.90x, two-polygon union 0.93x. int vs EPICK, pgl faster: point search count in Triangle 0.21x and segment search count in Triangle 0.21x, segment intersection 0.35x (CGAL's EPICK sweep is not exact; pgl's exact int version is 0.20x against EPECK), segment search count in Rectangle 0.51x, convex hull 0.51x, visibility 0.73x. CGAL faster: Delaunay triangulation (pgl 2.6x slower ERational/EPECK, 1.7x slower int/EPICK), point search count in Triangle with ERational (2.4x), convex hull with ERational (1.8x), Minkowski sum (1.7x), triangulation point location with ERational (1.7x), and with int/EPICK the kd-tree build (1.7x), nearest-neighbour query (1.8x), segment search build (1.8x) and triangulation point-location build (1.4x). Overall ERational/EPECK spans CGAL 2.6x faster to pgl 4.4x faster; int/EPICK spans CGAL 1.8x faster to pgl 4.8x faster. |
| **Workload** | Wall-clock time of 2D computational-geometry problems (triangulation, convex hull, kd-tree/AABB search, segment intersection, arrangements, polygon unions, Minkowski sum, visibility) on identical integer-coordinate inputs, pgl number type vs the comparable CGAL kernel, across input sizes up to the dataset limits (random data plus Salzburg polygon database). |
| **Metric** | throughput |
| **Hardware** | Two machines, one run each: AMD Ryzen 9 9900X 12-Core Processor and Intel Xeon w5-3433 (named in the meta block of gfonsecabr/pgl-benchmarks history/asymptotic-baseline/\*.json; doc/cgal.md itself does not name them). Ratios are per-machine pgl/CGAL, then averaged over the two machines. |
| **Compiler and flags** | GCC 16.2.1 (g++), -std=c++23 -O2 -DNDEBUG, CGAL 6.1.2 |
| **Adoption** | 6 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/gfonsecabr/pgl) · [benchmark](https://github.com/gfonsecabr/pgl/blob/main/doc/cgal.md#speed) |

## Verdict

doc/cgal.md times 18 2D problems on identical integer inputs (random data plus the Salzburg polygon database, about 32 sizes), pgl ERational vs CGAL 6.1.2 EPECK and pgl int vs EPICK, built with g++ 16.2.1 -std=c++23 -O2 -DNDEBUG on an AMD Ryzen 9 9900X and an Intel Xeon w5-3433, one run each, ratios averaged over the two machines. Medians range from CGAL 2.6x faster (Delaunay) to pgl about 4.4x faster (union of many triangles, 0.23x) with ERational, and from CGAL 1.8x faster to pgl about 4.8x faster (count in Triangle, 0.21x) with int.

## Use it when

- 2D problems on integer-coordinate input (GIS rasters, lattice/polyomino work, competitive-programming-style geometry) where you want exact answers without paying for CGAL's EPECK lazy-exact machinery
- Segment intersection, arrangement point location, unions of many triangles/polygons and range counting in a Rectangle, the rows where doc/cgal.md shows pgl at 0.2x-0.7x of CGAL's time
- Projects that cannot take CGAL's GPL/LGPL licence or its Boost/GMP/MPFR dependencies: pgl is MIT, header-only and dependency-free on GCC/Clang
- Teaching, prototyping and research code where a readable predicate API (polygon.contains(segment)) matters more than CGAL's breadth; built-in Canvas exports SVG/PDF/Ipe for figures
- Exact Voronoi/power diagrams of order k or farthest-point diagrams, visibility graphs and Minkowski erosion, which CGAL does not offer directly

## Skip it when

- Delaunay triangulation throughput: CGAL is 2.6x faster (ERational vs EPECK) and 1.7x faster (int vs EPICK); also slower for Minkowski sum (1.7x), convex hull with ERational (1.8x) and, with int, kd-tree build and nearest-neighbour queries (1.7-1.8x)
- Anything beyond the plane: no 3D, curved geometry, alpha shapes, straight skeletons/offsets, snap rounding, polygon repair, mesh processing or file formats (WKT, DXF, OFF, STL)
- Floating-point input: types.md says double coordinates are accepted 'at your own risk' and robustness to rounding is untested; use int or rationals
- Production code that needs a long track record: v1.0.0 was tagged 2026-09-20, the repo has 6 stars and 0 forks, and its own README rates maturity 'Very low'
- Huge or adversarial integer coordinates without checking types.md's overflow table: plain int32 predicates are exact only up to about 1.5e9 with promotion (23,170 without), and Rational&lt;int64_t&gt; can overflow on long construction chains

## How it is fast

Predicates on integer coordinates run in plain integer arithmetic with width promotion (int32 to int64, int64 to __int128, int128 to its own BigInt), so no filter or lazy-exact layer is needed on integer input; lines through integer points stay integral because they are stored as two points. Its own Rational&lt;T&gt; defers gcd reduction, and its BigInt stays inline below 2^127; types.md measures Rational&lt;BigInt&gt; at about 38 ns per segment-crossing test vs 1,062 ns for GMP mpq and 1,804 ns for boost::rational&lt;cpp_int&gt;. For arbitrary-precision types the orientation/incircle predicates first try a floating-point evaluation with an error bound. Algorithms are chosen adaptively, e.g. findIntersections prices a bounding-box scan against a Bentley-Ottmann sweep from a sample and switches once the scan exceeds the sweep's cost.

## Compared with alternatives

Pick pgl over detria or Delaunay32 when you need a whole exact 2D toolkit (sweeps, arrangements, booleans, visibility) rather than only a fast triangulator, since those siblings beat CGAL-class triangulation and pgl does not; pick it over GeoToolbox KdBoxTree or nanoflann only when queries are arbitrary shapes (triangles, polygons) on integer data rather than point kNN.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none on GCC/Clang; on MSVC the Boost.Multiprecision headers (no native __int128). Bundled doctest, PDFGen and plf_nanotimer are for tests, PDF export and benchmarks only. |
| **Minimum toolchain** | C++20 (C++23 and C++26 also work); CI runs GCC 13, Clang 18 and MSVC |
| **Platforms** | any platform with a C++20 compiler; 128-bit integers native on GCC/Clang, emulated via Boost on MSVC |
| **Thread safety** | not documented; note that Triangulation::locate walks from where the previous query ended, so queries carry per-object state |
| **Drop-in for the baseline** | partial — covers CGAL's 2D overlap (hull, Delaunay/CDT, arrangements, Boolean_set_operations_2, minkowski_sum_2, Kd_tree/AABB_tree, visibility, Partition_2), but with a different value-based API, unoriented shapes, bool predicates instead of CGAL's three-way bounded_side, and a fixed short list of number types |

## Gotchas

- Constructions from integral shapes return ERational (Rational&lt;BigInt&gt;) by default, which types.md puts at about 8x the cost of int; pick a smaller result type explicitly when bounds allow
- Some integer-typed constructions truncate: smallestEnclosingDisk divides by two, so integral coordinates should be even, and requesting an integral ResultNumber from Arrangement::halfplaneIntersection can truncate split coordinates
- ShapeTree::insert does no rebalancing, so repeated inserts can drive height to Theta(n) until rebuild(); Triangulation point-location indices are not updated after modification
- The benchmark page says pgl is tuned against this very benchmark and some rows (count in Triangle) race a CGAL query the benchmark authors wrote themselves; Range_tree_2 is deliberately not run

## Known shortcomings

- Tuned against its own benchmark, and some rows favour pgl by construction; CGAL wins Delaunay, Minkowski and integer kNN.
- Floating-point coordinates are untested ('at your own risk' per docs); some integer constructions truncate (smallestEnclosingDisk needs even coordinates).

## Caveats and trade-offs

First-party comparison, but fully reproducible (code, compiler, flags and CPU models public), so tier A. doc/cgal.md says pgl is tuned against this very benchmark, so the comparison favours pgl. Some rows favour pgl by construction: CGAL Kd_tree has no triangle query, so the benchmark wrote one for the 'count in Triangle' rows, which is where pgl's int column looks best; CGAL's Range_tree_2 is deliberately not run. Mixed result: CGAL wins Delaunay triangulation, Minkowski sum, triangulation point location, and with int/EPICK the kd-tree build and nearest-neighbour query. Ratios are averaged over two machines, one run each. The table changes often (it was refreshed 2026-09-23 and re-averaged 2026-09-26), so re-read before quoting. Very young project (6 stars). Do not read it as a blanket CGAL replacement.

Plane-only (2D) library; no higher dimensions, curved geometry, straight skeletons/offsets, alpha shapes or file formats. Header-only, needs C++20 or newer (tested GCC 13, Clang 18, MSVC). Fixed short list of number types, no filtered-kernel layer.

## Maintenance

Very actively developed (916 commits, last commit 2026-10-01, v1.0.0 tagged 2026-09-20, no issues filed) by one academic author with a student contributor and AI-assisted code; MIT-licensed and header-only, so easy to vendor, but young and unproven outside its own benchmarks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the CGAL comparison code is public (tests/benchmark/asymptotic/\*.cpp for pgl, tests/benchmark/asymptotic/baseline/\*.cpp for CGAL 6.1.2), doc/cgal.md states g++ -std=c++23 -O2 -DNDEBUG, and the linked data repo gfonsecabr/pgl-benchmarks records the CPU models (AMD Ryzen 9 9900X, Intel Xeon w5-3433) and GCC 16.2.1 in each machine's CGAL baseline file. Every table ratio in the record matches doc/cgal.md.
- **Verifier notes:** Every ratio quoted in the record matches the doc/cgal.md table; I only added rows it left out (for example CGAL 1.8x faster on the int/EPICK nearest-neighbour query, which the record listed as a pgl win under ERational only). Upgraded to A after finding the CPU models in the linked data repo. The dashboard at gfonsecabr.github.io is blocked from this container. Metadata: MIT (LICENSE read), 6 stars, not a fork, last commit 2026-10-01.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/gfonsecabr/pgl>
  - <https://github.com/gfonsecabr/pgl/commits/main>
  - <https://github.com/gfonsecabr/pgl/tree/main/doc>
  - <https://github.com/gfonsecabr/pgl/tree/main/tests/benchmark>
  - <https://github.com/gfonsecabr/pgl/tree/main/tests/benchmark/asymptotic>
  - <https://github.com/gfonsecabr/pgl/tree/main/tests/benchmark/asymptotic/baseline>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/README.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/doc/cgal.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/tests/benchmark/README.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/tests/benchmark/bench_paths.py>
  - <https://github.com/gfonsecabr/pgl-benchmarks/tree/main/history/asymptotic-baseline>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl-benchmarks/HEAD/history/asymptotic-baseline/amd-ryzen-9-9900x-12-core-processor-g%2B%2B.json>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl-benchmarks/HEAD/history/asymptotic-baseline/intel-r-xeon-r-w5-3433-g%2B%2B.json>
- **Sources the enricher read:**
  - <https://github.com/gfonsecabr/pgl>
  - <https://github.com/gfonsecabr/pgl/issues?q=is%3Aissue>
  - <https://github.com/gfonsecabr/pgl/tags>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/README.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/doc/cgal.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/doc/types.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/doc/data_structures.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/doc/algorithms.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/tests/benchmark/README.md>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gfonsecabr/pgl/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gfonsecabr/pgl`) · [data/wave8/enrich/raw/github_com_gfonsecabr_pgl.json](../../../data/wave8/enrich/raw/github_com_gfonsecabr_pgl.json) (enrichment confidence 0.8)

</details>
