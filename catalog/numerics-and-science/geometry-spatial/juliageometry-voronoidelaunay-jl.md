# VoronoiDelaunay.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🔴 abandoned

> Julia package for incremental 2D Delaunay/Voronoi tessellation; its author's 2014 benchmark had it about 20% faster than CGAL 4.4.

| | |
|---|---|
| **Beats** | CGAL 4.4 2D Delaunay triangulation |
| **Claimed result** | Approximately 20% faster than CGAL (gist); README: 'Benchmarks suggest this package is a bit faster than CGAL'. Julia version used about 2-3x the memory of CGAL. |
| **Workload** | Delaunay construction by inserting 10K, 100K, 1M and 10M uniformly distributed points, 5 runs each. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4800MQ @ 2.7GHz, 16 GB RAM, Windows 8 64-bit |
| **Compiler and flags** | CGAL v4.4 built with Visual Studio 2013, 64-bit release mode; Julia 0.3.0 (2014-08-20) |
| **Adoption** | 125 stars, 25 forks |
| **Last commit** | 2023-06-28 |
| **Links** | [repository](https://github.com/JuliaGeometry/VoronoiDelaunay.jl) · [benchmark](https://gist.github.com/skariel/3d2018f9341a058e00fc) |

## Verdict

In 2014 the package author inserted 10K to 10M uniform points (5 runs each) on an Intel Core i7-4800MQ under Windows 8, with Julia 0.3.0 against CGAL 4.4 built with VS2013 64-bit release, and reported about 20% faster construction at 2-3x CGAL's memory. The timings exist only as a graph image. CGAL's time includes memory allocation while Julia's storage was preallocated, so the margin is partly an allocation effect.

## Use it when

- You work in Julia and need a 2D Delaunay or Voronoi tessellation of thousands to millions of points without depending on CGAL.
- Points are roughly uniform and can be affinely rescaled into [1,2]^2 without any loss of meaning.
- You insert points incrementally and need point location plus neighbour walking on a live tessellation.
- You want Voronoi edges for plotting or mesh generation from images (from_image), and approximate results on degenerate inputs are acceptable.

## Skip it when

- Your project is C or C++. This is Julia-only, and the C++ siblings (pgl, Delaunay32, detria) can be linked directly.
- You need weighted (power) diagrams, constrained edges, 3D tessellations or Lloyd relaxation. The README lists all of these as unimplemented.
- Inputs are small or degenerate. Open issues report no triangles or edges for 3-4 points or collinear points (#55, #51), a triangle union that does not match the convex hull (#34), and an indefinite hang in push! on an 81-point set (#38).
- Memory is tight. The author's gist measured about 2-3x CGAL's memory use.
- You need an actively maintained library. The README itself recommends DelaunayTriangulation.jl instead.

## How it is fast

It does incremental insertion with Lawson edge flips to restore the Delaunay property, following the Arepo paper (arXiv 0901.4107). Bulk push! shuffles the input and then applies a multiscale Hilbert sort (mssort!), so each point lands near the previous one and the walk to its triangle stays short. Predicates come from GeometricalPredicates.jl, which filters in Float64 with bounded error and falls back to exact BigInt arithmetic. The fixed [1,2) coordinate range gives a constant exponent, so each mantissa maps one-to-one onto an integer. Triangles are mutable structs in one preallocated vector (sizehint!), and they cache their predicate terms.

## Compared with alternatives

Pick it only inside a Julia codebase. For C++, pgl (measured against CGAL 6.1.2 Delaunay_triangulation_2), Delaunay32 (multithreaded, beats Triangle and Fade2D) or detria (constrained) are callable directly and have more recent evidence, and jc_voronoi covers plain 2D Voronoi in C.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | GeometricalPredicates.jl (0.2-0.4), Colors.jl, Random (stdlib) |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat) |
| **Platforms** | any platform Julia runs on (pure Julia, no native code) |
| **Thread safety** | not documented; push! mutates the tessellation, so build it from one task |
| **Drop-in for the baseline** | no |

## Gotchas

- Coordinates outside [1.0+eps, 2.0-2eps] are not checked by push!. Out-of-range points break the predicates, and inserting (0.0, 0.0) hung forever in closed issue #36.
- push!(tess, array) shuffles and Hilbert-sorts the caller's array in place, so the input order is lost.
- Duplicate points are not handled. GeometricalPredicates assumes vertices never overlap, so callers must deduplicate.
- Iteration skips every triangle that touches the four auxiliary corner points. This is the likely reason small or collinear inputs yield no triangles or edges (issues #55, #51) and hull triangles can go missing (#34).

## Known shortcomings

- Evidence is a 2014 gist with code shown only as screenshots; Julia, off-scope for a C++ catalog; the record's 'used in Illustris' misread the README (it means Arepo's algorithms, not this package).
- Julia, not callable from C++. Open correctness bugs: push! hang (#38), missing triangles or edges for 3-4 or collinear points (#55, #51), triangle union not matching the convex hull (#34). Bulk push! reorders the caller's array in place; out-of-range or duplicate points are not checked ((0,0) hung, #36). README recommends successor DelaunayTriangulation.jl.

## Caveats and trade-offs

2014 measurement on Julia 0.3 and CGAL 4.4 by the package author; timings appear only as a graph image and the Julia and CGAL benchmark code only as screenshots (the Delaunay code itself is linked as a separate gist). The gist notes the CGAL timing includes memory allocation while Julia pre-allocates, and Julia used about 2-3x CGAL's memory. README says the gist measured an older, slower version. Package is in maintenance mode and the README points to DelaunayTriangulation.jl. The README's Illustris mention refers to the Arepo algorithms it follows, not to use of this package. Julia is outside the C++-callable scope.

Julia package, not directly callable from C++; point coordinates restricted to 1.0+eps to 2.0-2eps; no weighted or 3D tessellations; higher memory use.

## Maintenance

In maintenance mode, with the last commit on 2023-06-28 and the README pointing users to DelaunayTriangulation.jl. It is MIT-licensed, about 760 lines and easy to read, but several correctness issues remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's 2014 gist compares the Julia code with CGAL 4.4 (VS2013 64-bit release) on an Intel Core i7-4800MQ, stating '\~20% faster than CGAL' and 2-3x CGAL's memory, but the timings are only in a graph image and the benchmark code is shown as screenshots, so it is first-party C.
- **Verifier notes:** Record's 'used in the Illustris simulation' misreads the README (the Arepo-paper algorithms are used in Illustris), so stars_or_usage is corrected. Metadata: MIT (LICENSE.md), 125 stars, not archived or a fork, last commit 2023-06-28 (abandoned, over 3 years). Julia-only, so the orchestrator may want an off-scope flag.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://gist.github.com/skariel/3d2018f9341a058e00fc>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/commits>
  - <https://raw.githubusercontent.com/JuliaGeometry/VoronoiDelaunay.jl/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/JuliaGeometry/VoronoiDelaunay.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaGeometry/VoronoiDelaunay.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaGeometry/VoronoiDelaunay.jl/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaGeometry/VoronoiDelaunay.jl/HEAD/src/VoronoiDelaunay.jl>
  - <https://raw.githubusercontent.com/JuliaGeometry/GeometricalPredicates.jl/HEAD/README.md>
  - <https://gist.github.com/skariel/3d2018f9341a058e00fc>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/issues/38>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/issues/34>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/issues/51>
  - <https://github.com/JuliaGeometry/VoronoiDelaunay.jl/issues/55>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/juliageometry/voronoidelaunay.jl`) · [data/wave8/enrich/raw/github_com_juliageometry_voronoidelaunay_jl.json](../../../data/wave8/enrich/raw/github_com_juliageometry_voronoidelaunay_jl.json) (enrichment confidence 0.8)

</details>
