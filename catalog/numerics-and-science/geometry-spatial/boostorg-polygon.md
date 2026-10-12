# Boost.Polygon (Voronoi diagram builder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only Boost sweep-line Voronoi builder for integer points and segments; beats CGAL's segment Delaunay graph, loses on points.

| | |
|---|---|
| **Beats** | CGAL (Delaunay triangulation of points / segment Delaunay graph; CGAL-4.3-beta1 in the benchmark) |
| **Claimed result** | Random segments, average construction time in seconds, Boost.Polygon vs CGAL: 100 segments 0.002284 vs 0.002985; 10,000 segments 0.2377 vs 0.3374; 1,000,000 segments 25.0 vs 39.09 (about 1.56x faster at 1M, derived from page data). Random points: Boost.Polygon is slower than CGAL (1,000,000 points 3.47 s vs 0.9023 s; S-Hull 6.603814 s). A second page in the repo (doc/analysis.htm) says Boost.Polygon's arbitrary-angle Booleans are 'roughly as fast as GPC at small scales, while algorithmically faster at large scales' and that a 2010 divide-and-conquer change gave 10X over its own older algorithm at 200,000+ rectangles; it gives no GPC numbers. |
| **Workload** | Average construction time of the Voronoi diagram (Boost.Polygon) versus the Delaunay triangulation (CGAL, S-Hull) of random points and of random non-intersecting segments, uniformly distributed on a 32-bit integer grid, from 100 to 1,000,000 inputs. |
| **Metric** | throughput |
| **Hardware** | Intel i5-7600 2.8 GHz, 16 GiB RAM, Ubuntu 13.04 64-bit (as printed on the page) |
| **Compiler and flags** | GCC 4.7.3 with Boost 1.54.0, CGAL-4.3-beta1, GMP 5.1.4, MPFR 3.1.2; optimization flags are not stated (benchmark/Jamfile.v2 sets none) |
| **Adoption** | 70 stars; part of the Boost libraries |
| **Last commit** | 2025-05-02 |
| **Links** | [repository](https://github.com/boostorg/polygon) · [benchmark](https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_benchmark.htm) |

## Verdict

The library author's 2013 benchmark (GCC 4.7.3, Boost 1.54, CGAL 4.3-beta1, CPU printed as 'Intel i5-7600 2.8 GHz', optimization level unstated) timed Boost.Polygon's Voronoi construction against CGAL's segment Delaunay graph and Delaunay triangulation: on random non-intersecting segments it was 25.0 s vs 39.1 s at 1M (about 1.56x) and 1.3x to 1.5x at smaller sizes, but on random points CGAL was about 3.8x faster (0.90 s vs 3.47 s at 1M). The two libraries produce different outputs (Voronoi with coordinates vs Delaunay topology), and segment-generation time is subtracted from the measured segment runs.

## Use it when

- Voronoi diagrams or medial axes of line segments (polylines, discretized curves, polygon outlines): the only case where the author's benchmark shows it beating CGAL, about 1.3x to 1.56x on 100 to 1,000,000 random non-intersecting segments.
- You need Voronoi vertex coordinates with a guaranteed relative error bound (64 machine epsilons per the Voronoi main page; vertices within 128 epsilons are merged) rather than only a Delaunay topology.
- You already depend on Boost and want no GMP/MPFR/CGAL build: the Voronoi headers need only the STL and boost/cstdint.hpp.
- Inputs are, or can be snapped to, 32-bit signed integer coordinates; 64-bit or wider integers work after writing custom coordinate type traits.
- Integer-grid polygon Booleans in VLSI/CAD-style workloads (Manhattan and 45-degree fast paths), where the separate polygon-set code applies.

## Skip it when

- Point-only Voronoi/Delaunay: CGAL's Delaunay_triangulation_2 was about 3.8x faster at 1,000,000 random points in this same benchmark (3.47 s vs 0.90 s), and the catalogued jc_voronoi reports about 3.65x over Boost.Polygon at 1k random sites.
- Floating-point input: coordinates must be integral; you have to scale and snap, and the Voronoi builder rejects overlapping inputs (a point inside a segment, or segments crossing anywhere but at endpoints) unless you split them first with the segment utils.
- Workloads that cannot tolerate open robustness bugs: open issues report an infinite loop in voronoi_diagram::_build on one 1,912-segment input (#49), missing edges with coordinates up to 10,000,000 (#43), empty cells (#47) and a bug in robust_sqrt_expr::eval2 (#41), none with a linked fix.
- You need edge clipping to a bounding box, custom allocators or Delaunay output directly: none are provided (jc_voronoi's own feature table lists clipping and custom allocators as missing from Boost).
- Arbitrary-angle polygon Booleans on adversarial input: the polygon-set intersection uses a divide-and-conquer heuristic that the analysis page says can go quadratic on specific inputs that defeat 1-D decomposition.

## How it is fast

It runs Fortune's sweep-line algorithm: site events sorted once with std::sort, a beach line held in a std::map, and circle events in an ordered priority queue, O(N log N) time and O(N) memory. Robustness comes from lazy arithmetic: predicates are first evaluated in double with relative-error tracking (robust_fpt, ULP comparisons), and only when the result falls in the uncertain range do they fall back to fixed-size, stack-allocated multiprecision integers (extended_int&lt;128&gt; and up). The docs say this avoids multiprecision work in about 95% of cases. There is no heap new in the algorithm itself (pure STL containers).

## Compared with alternatives

Pick it over jc_voronoi when sites include line segments or you need exact-predicate robustness on an integer grid; jc_voronoi is a point-only float Fortune implementation that is about 3.65x faster on 1k random points. For point-set Delaunay, pgl, Delaunay32 or CGAL itself are faster choices.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Voronoi part: STL and boost/cstdint.hpp only (Boost::config in CMake); polygon-set Booleans optionally use GMP via boost/polygon/gmp_override.hpp |
| **Minimum toolchain** | not documented; pre-C++11 era Boost code. Open issues report C++20 warnings (#79) and a build error with a then-recent MSVC (#40) |
| **Platforms** | any (portable C++; 80-bit long double fpt types work on GCC but not MSVC, per the builder docs) |
| **Thread safety** | not documented; voronoi_builder holds all state in member containers, so separate builder/diagram instances per thread are the safe assumption (inferred from voronoi_builder.hpp) |
| **Drop-in for the baseline** | no |

## Gotchas

- Default traits support int32 input only; int64 or wider needs custom voronoi_ctype_traits, including big-int and extended-exponent float types sized per the builder page's table.
- Vertices whose coordinates agree within 128 machine epsilons are merged and the edges between them dropped during finalization, so output topology can differ slightly from the exact diagram.
- Segment inputs must not intersect except at endpoints, and a point must not lie inside a segment; the builder does not check this for you.
- The diagram includes infinite edges (no vertex at one end); you clip them yourself for drawing or medial-axis use.

## Known shortcomings

- Voronoi builder only. Flags and b2 variant unstated (default is debug). Points are 3.8x slower than CGAL; only segments are 1.3-1.56x faster. CPU label (i5-7600) predates the benchmark's era, likely a typo.
- Open Voronoi correctness bugs with no fix: infinite loop in voronoi_diagram::_build on a 1,912-segment input (#49), missing edges at coordinates up to 1e7 (#43), empty cells (#47), a robust_sqrt_expr::eval2 bug (#41). Docs disagree on output precision (64 vs 128 epsilons).

## Caveats and trade-offs

Mixed result: only segment input wins (about 1.3x to 1.56x vs CGAL's Segment_Delaunay_graph_2, derived from page data). For points, CGAL's Delaunay_triangulation_2 (Exact_predicates_inexact_constructions kernel) is about 3.8x faster at 1M points (derived from page data). Voronoi and Delaunay are different outputs; the page notes the Voronoi diagram carries more information. In the segments test, the time for generating segments and removing intersections is measured in a separate pass and subtracted, and timing is CPU time (user+system) from boost::timer::cpu_timer. benchmark/Jamfile.v2 hard-codes the author's local library paths and sets no optimization flags. b2's default variant is debug unless variant=release is passed, and the page does not say which was used. This is a first-party benchmark by the library author with an old setup (GCC 4.7.3, Boost 1.54, CGAL 4.3-beta1, Ubuntu 13.04). The page was last edited 2013-10-06 ('rerunning benchmarks'), so its CPU label 'Intel i5-7600 2.8 GHz' predates that CPU's 2017 release and is likely a typo; reported as printed. A WebSearch snippet of the boost.org copy summarised the result as complete dominance over the CGAL Delaunay graph, which the points table does not support. boost.org was EGRESS_BLOCKED, so the repo copy was read. doc/analysis.htm separately says the 2010 divide-and-conquer Booleans are 'roughly as fast as GPC at small scales, while algorithmically faster at large scales', with no GPC numbers.

Builds a Voronoi diagram (points and segments) with output coordinates at '128 machine epsilon' precision per the page, whereas the compared CGAL and S-Hull routines build a Delaunay triangulation with no output coordinates. No external dependencies (CGAL needs Boost, GMP, MPFR). The benchmark uses 32-bit integer input coordinates.

## Maintenance

Stale: Boost-maintained build-system commits only (last 2025-05-02), Voronoi core unchanged since about 2013 with 41 open issues, but BSL-1.0, header-only and shipped in every Boost release, so it is easy to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/voronoi_benchmark.htm has the quoted tables, and the benchmark code is public (benchmark/voronoi_benchmark_points.cpp, benchmark/voronoi_benchmark_segments.cpp). It names the compiler (GCC 4.7.3) and CPU, but the optimization flags and b2 build variant are not stated and Jamfile.v2 sets none, so it is not A. The library author ran it, so first-party C.
- **Verifier notes:** All table values were checked against the repo copy of voronoi_benchmark.htm and the benchmark sources were read. Metadata matches: BSL-1.0 in the file headers, 70 stars, not archived, last commit 2025-05-02, so stale. The 1.56x segment win stands; the points loss is documented.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_benchmark.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/analysis.htm>
  - <https://github.com/boostorg/polygon>
  - <https://github.com/boostorg/polygon/commits/develop>
  - <https://github.com/boostorg/polygon/commits/develop/doc/voronoi_benchmark.htm>
  - <https://github.com/boostorg/polygon/tree/develop/benchmark>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/benchmark/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/benchmark/voronoi_benchmark_points.cpp>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/benchmark/voronoi_benchmark_segments.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_benchmark.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_main.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_builder.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/voronoi_diagram.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/analysis.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/index.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/doc/gtl_polygon_set_concept.htm>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/include/boost/polygon/voronoi_builder.hpp>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/include/boost/polygon/voronoi.hpp>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/include/boost/polygon/detail/voronoi_predicates.hpp>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/benchmark/voronoi_benchmark_segments.cpp>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/benchmark/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/polygon/HEAD/meta/libraries.json>
  - <https://github.com/boostorg/polygon>
  - <https://github.com/boostorg/polygon/commits/develop>
  - <https://github.com/boostorg/polygon/issues?q=is%3Aissue+voronoi>
  - <https://github.com/boostorg/polygon/issues/49>
  - <https://github.com/boostorg/polygon/issues/43>
  - <https://raw.githubusercontent.com/JCash/voronoi/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/boostorg/polygon`) · [data/wave8/enrich/raw/github_com_boostorg_polygon.json](../../../data/wave8/enrich/raw/github_com_boostorg_polygon.json) (enrichment confidence 0.75)

</details>
