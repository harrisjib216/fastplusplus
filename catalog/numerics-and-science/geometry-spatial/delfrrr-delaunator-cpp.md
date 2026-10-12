# delaunator-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header C++14 port of mapbox/delaunator for 2D Delaunay; about 10% faster than JS at 1M points, roughly matches Triangle.

| | |
|---|---|
| **Beats** | mapbox/delaunator (JavaScript original), in its own README and PR #8; the repo has no C++ baseline (bench/run.cpp times delaunator-cpp only). A third-party table in the Delaunay32 README compares it with Triangle 1.6, CDT 1.4.5 and Fade2D 2.17.3. |
| **Claimed result** | README: 'Probably the fastest C++ open source 2D Delaunay implementation' and 'Library is \~10% faster then JS version for 1M uniform points' (links PR #8). Own Google Benchmark run dated 2018-09-29: 45K geojson nodes 22 ms; 2,000 uniform points 1 ms; 100,000 63 ms; 200,000 140 ms; 500,000 400 ms; 1,000,000 994 ms. In PR #8 the author's first claim, 'Roughly 6 times faster then JS version', was challenged by mourner (benchmarks showed \~20-30%; the JS script had no JIT warmup); after both benchmarks were reworked the author reported \~30 ms of JS overhead on small inputs and a \~10% difference at 1M points. Third-party: the Delaunay32 README table (1M unique integer points, Apple M1, 1 thread, triangle-only output) lists delaunator-cpp c1521f6 at 542.0 ms vs Triangle 1.6 at 584.0 ms and CDT 1.4.5 at 988.7 ms, i.e. about 1.08x faster than Triangle and 1.8x faster than CDT, but 4.1x slower than single-thread Delaunay32 (131.6 ms) and 1.7x slower than single-thread Fade2D 2.17.3 (314.1 ms) (ratios derived from page data). |
| **Workload** | 2D Delaunay triangulation of uniform random points (2,000 to 1,000,000) and 45K GeoJSON nodes. |
| **Metric** | latency |
| **Hardware** | 4 X 2300 MHz CPU (model not stated), run dated 2018-09-29 |
| **Compiler and flags** | Not stated for the README run; CMakeLists.txt release build sets -O3 -DNDEBUG with C++14 (compiler unspecified). |
| **Adoption** | 602 stars |
| **Last commit** | 2018-10-07 |
| **Links** | [repository](https://github.com/delfrrr/delaunator-cpp) · [benchmark](https://github.com/delfrrr/delaunator-cpp) |

## Verdict

First-party only: a 2018-09-29 Google Benchmark run in the README (unnamed '4 X 2300 MHz' CPU, compiler unstated, CMake release flags -O3) triangulates 1M uniform random points in 994 ms. PR #8 settles on about 10% faster than the JS original at 1M points, with no hardware or Node version stated, after the author's '6 times faster' claim was challenged as JIT warmup. The only C++ comparison is the competitor-run Delaunay32 README table (1M unique integer points, Apple M1, one thread, flags not stated): 542.0 ms vs Triangle 1.6 at 584.0 ms (about 1.08x) and CDT 1.4.5 at 988.7 ms, but behind Delaunay32 (131.6 ms) and Fade2D 2.17.3 (314.1 ms).

## Use it when

- Unconstrained 2D Delaunay of well-spread double-precision points (GIS nodes, random samples, projected point clouds) up to a few million points, single-threaded
- You want one small MIT-licensed header instead of pulling in CGAL or Triangle, and can patch it locally
- You need the triangles/halfedges array layout of mapbox/delaunator to share code or data with the JS original
- Inputs that should stay as doubles rather than being quantised to int32 as Delaunay32 requires

## Skip it when

- Degenerate or near-degenerate input (many collinear or cocircular points, snapped grids, huge coordinate ranges): predicates are plain double arithmetic, and open issues report an infinite loop in legalize() (#16, fix PR #32 unmerged), an orient robustness bug (#43) and division by zero when choosing the third seed point (#46)
- Constrained edges, polygons with holes or quality meshing: not supported (issue #35); use detria, CDT or Triangle
- Raw speed on large sets: in the Delaunay32 table (1M points, Apple M1) it takes 542.0 ms against 131.6 ms for single-thread Delaunay32 and 314.1 ms for single-thread Fade2D, and it has no parallel mode
- Projects that need an upstream that takes fixes: no commits since 2018-10-07, 24 open issues, fix PRs #28, #30 and #32 unmerged
- 3D or higher-dimensional triangulation: 2D only

## How it is fast

It uses the sweep-hull incremental scheme (as in S-hull). It seeds a triangle near the bounding-box centre, sorts all points by distance from that triangle's circumcentre and inserts them in order, so each new point lies outside the current convex hull. A visible hull edge is found through a hash of hull vertices keyed by pseudo-angle (about sqrt(n) buckets). The new fan of triangles is fixed up by Lawson edge flips (legalize), using an explicit stack instead of recursion (PR #12). Everything lives in flat, pre-reserved index vectors (2n-5 triangles), so there is no per-triangle allocation or pointer-based mesh.

## Compared with alternatives

Delaunay32 (already catalogued) is 4.1x faster single-threaded on 1M points, uses exact integer predicates and supports constraints, so prefer it unless you need double input without int32 quantisation or a C++14-only toolchain. Pick delaunator-cpp over detria or CDT only for unconstrained point sets, where it is simpler and, per the Delaunay32 table, 1.8x faster than CDT 1.4.5.

## Integration

| | |
|---|---|
| **Form** | source-drop (single header include/delaunator.hpp; not safe to include from more than one translation unit as shipped) |
| **Dependencies** | none beyond the C++ standard library; the repo's tests and benchmarks pull Catch 2.4.0, RapidJSON 1.1.0 and Google Benchmark 1.2.0 through mason |
| **Minimum toolchain** | C++14 (CMakeLists sets CMAKE_CXX_STANDARD 14); some toolchains (MSVC, newer GCC) need #include &lt;tuple&gt; added because std::tie is used without it (issues #26, #39, PR #37) |
| **Platforms** | any (portable scalar C++ on doubles, no SIMD) |
| **Thread safety** | not documented; there is no global or static mutable state, so separate Delaunator objects can be built on separate threads, but each triangulation is single-threaded |
| **Drop-in for the baseline** | partial: same algorithm and output arrays as mapbox/delaunator (JS), but a C++ API; not a drop-in for Triangle or CGAL |

## Gotchas

- The out-of-class member definitions (constructor, legalize, add_triangle, link, get_hull_area) are not marked inline, so including delaunator.hpp from two .cpp files fails to link with duplicate symbols (issue #33, LNK2005; PR #30 'inline Delaunator methods' unmerged). Include it from one translation unit or add inline yourself.
- The object stores `std::vector<double> const& coords`, a reference to your input. Passing a temporary leaves a dangling reference, and the input vector must outlive the Delaunator.
- max_x/max_y start at std::numeric_limits&lt;double&gt;::min() (the smallest positive double, not the lowest value), so the bounding box is wrong when all x or all y coordinates are negative. This shifts the seed-point choice (issue #27; PR #28 'Use lowest instead of min' unmerged).
- Collinear input throws std::runtime_error("not triangulation"), but with fewer than two distinct points the seed indices stay INVALID_INDEX and coords is read out of bounds before that check. Validate the input size and distinctness first. Near-duplicate points (within DBL_EPSILON) are silently skipped.

## Known shortcomings

- Compared only against the JS original (PR #8 retracted the 6x claim; \~10% at 1M points); bench/run.cpp times itself only; no CGAL/Triangle/poly2tri comparison in the repo. Third-party Delaunay32 README: 542.0 ms vs Triangle 1.6 at 584.0 ms (\~1.08x), and 4.1x slower than Delaunay32 single-threaded. Correctness: open #16 infinite loop in legalize(), plus open division-by-zero, orientation-robustness and unsigned-overflow (ASan) issues. Abandoned since 2018.
- The header is not ODR-safe: non-inline members give LNK2005 in two or more translation units (issue #33, PR #30 unmerged). The bounding box starts at numeric_limits&lt;double&gt;::min(), wrong when all coordinates are negative (issue #27, PR #28 unmerged). Fewer than 2 distinct points read out of bounds before the 'not triangulation' throw; it stores a reference to the input vector (dangles for a temporary); missing &lt;tuple&gt; include (#26, #39); infinite loop #16 and robustness issues #43/#46. abellgithub/delaunator-cpp is the maintained fork (213 stars, last commit 2025-04-18) with the lowest() fix and a tolerance-based collinear check, but no exact predicates and no speed numbers.

## Caveats and trade-offs

Its own evidence compares only against the JS original of the same algorithm (\~10% at 1M points after the 6x claim was retracted in PR #8); bench/run.cpp benchmarks delaunator-cpp alone, and CGAL, Triangle and poly2tri are never measured in the repo (issue #34 'Comparison with CGAL?' got no numbers). Numbers are first-party from 2018 with no compiler and no CPU model ('4 X 2300 MHz CPU'). The only C++ comparison is a competitor's table (Delaunay32 README, Apple M1, compiler and flags not stated): delaunator-cpp is about 1.08x faster than Triangle 1.6 but 4.1x slower than single-thread Delaunay32 and 1.7x slower than single-thread Fade2D, which contradicts the hedged 'probably the fastest' claim; Delaunay32 is already catalogued. Correctness: open issue #16 reports an infinite loop in legalize() on a 136-point input (opened 2019-04-19 and still open; the issue page links PR #32 as a proposed fix), and the open-issue list also has 'Division by zero when finding third point', 'orient function robustness issue' and 'Unsigned integer overflow detected by AddressSanitizer'; predicates are plain floating point. Abandoned since 2018-10-07.

2D unconstrained Delaunay only; plain std::vector&lt;double&gt; coordinate input (x0,y0,x1,y1,...); header-style port of the JS algorithm, not robust-predicate based.

## Maintenance

Abandoned since 2018-10-07 (88 commits, 24 open issues including an infinite loop), but MIT-licensed and about 600 lines in one header, so it is easy to vendor and patch. The abellgithub/delaunator-cpp fork (last commit 2025-04-18) carries the lowest() fix, header-only and compiled build modes, and collinear and degenerate-case handling.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark timings in the README (bench/run.cpp, which times delaunator-cpp only) with no compiler, no CPU model and a JS-only baseline whose \~10% figure lives in PR #8; a third-party table in the Delaunay32 README (competitor-run, compiler and flags not stated) adds Triangle/CDT numbers but is not a well-known independent suite, so C.
- **Verifier notes:** Measures itself only against the JS original (delaunator), not against CGAL, Triangle or poly2tri; a C++ comparison exists only in the third-party Delaunay32 README (barely ahead of Triangle, well behind Delaunay32 and Fade2D). Record the open infinite-loop and division-by-zero issues as correctness shortcomings. The HN-snippet figures in the input caveats were replaced with the Delaunay32 README numbers I opened.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/README.md>
  - <https://github.com/delfrrr/delaunator-cpp>
  - <https://github.com/delfrrr/delaunator-cpp/commits>
  - <https://github.com/delfrrr/delaunator-cpp/pull/8>
  - <https://github.com/delfrrr/delaunator-cpp/tree/master/bench>
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/bench/run.cpp>
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/CMakeLists.txt>
  - <https://github.com/delfrrr/delaunator-cpp/issues>
  - <https://github.com/delfrrr/delaunator-cpp/issues?q=is%3Aissue+CGAL>
  - <https://github.com/delfrrr/delaunator-cpp/issues/34>
  - <https://github.com/delfrrr/delaunator-cpp/issues/16>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/include/delaunator.hpp>
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/delfrrr/delaunator-cpp/HEAD/bench/run.cpp>
  - <https://github.com/delfrrr/delaunator-cpp>
  - <https://github.com/delfrrr/delaunator-cpp/issues?q=is%3Aissue>
  - <https://github.com/delfrrr/delaunator-cpp/pulls?q=is%3Apr>
  - <https://github.com/delfrrr/delaunator-cpp/issues/16>
  - <https://github.com/delfrrr/delaunator-cpp/issues/31>
  - <https://github.com/delfrrr/delaunator-cpp/issues/33>
  - <https://github.com/delfrrr/delaunator-cpp/pull/8>
  - <https://raw.githubusercontent.com/morishuz/delaunay32/HEAD/README.md>
  - <https://github.com/abellgithub/delaunator-cpp>
  - <https://github.com/abellgithub/delaunator-cpp/commits>
  - <https://raw.githubusercontent.com/abellgithub/delaunator-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/abellgithub/delaunator-cpp/HEAD/include/delaunator.hpp>
  - <https://raw.githubusercontent.com/abellgithub/delaunator-cpp/HEAD/include/delaunator.cpp>
  - <https://raw.githubusercontent.com/abellgithub/delaunator-cpp/HEAD/include/delaunator-header-only.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/delfrrr/delaunator-cpp`) · [data/wave8/enrich/raw/github_com_delfrrr_delaunator_cpp.json](../../../data/wave8/enrich/raw/github_com_delfrrr_delaunator_cpp.json) (enrichment confidence 0.75)

</details>
