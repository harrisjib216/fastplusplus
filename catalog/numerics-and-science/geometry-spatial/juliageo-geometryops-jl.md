# GeometryOps.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia 2D/spherical geometry ops; beats GEOS-through-GeoPandas/R on simple point tasks, but trails GEOS called directly.

| | |
|---|---|
| **Beats** | GEOS (through GeoPandas/Shapely in Python and the 'geos' package in R) |
| **Claimed result** | Median seconds in timings.csv, GeometryOps.jl vs GEOS-backed packages, on tasks where GeometryOps runs its own pure-Julia code: distance 0.11 vs 0.9 (GeoPandas) and 5.37 (R geos); intersects 0.04 vs 0.12 (GeoPandas) and 0.08 (R geos, prepared geometry); sample 0.04 vs 0.9 (GeoPandas). Derived ratios (derived from page data): distance about 8x vs GeoPandas and about 49x vs R geos; intersects 3x vs GeoPandas and 2x vs R geos; sample about 22x vs GeoPandas. The other tasks are not GeometryOps-vs-GEOS comparisons: buffer is 5.75 vs 4.07 (GeoPandas) and 5.65 (R geos), but the GeometryOps buffer script calls GEOS itself through LibGEOS (GO.GEOS backend), so it is GEOS vs GEOS; transform 0.08 vs 0.23 (GeoPandas) runs PROJ through Proj.jl on both sides, and R sf-project also takes 0.08; load 0.36 vs 0.45 (GeoPandas) and write 1.38 vs 1.28 are GDAL file I/O, and terra loads faster (0.33). |
| **Workload** | kadyb/vector-benchmark: a synthetic set of 500,000 planar points plus one polygon. The distance task uses only the first 5,000 points (a 5,000 x 5,000 pairwise distance matrix). intersects tests all 500,000 points against the polygon. The other tasks are buffer, sampling points in the polygon, CRS transform, and GeoPackage load/write. Each value is the median seconds per task. Julia is timed with Chairmarks for 15 s (60 s for buffer) after warm-up; R uses system.time and Python uses timeit, 10 runs each. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X @ 3.7 GHz, 64 GB RAM, Ubuntu 22.04.5 LTS |
| **Compiler and flags** | Interpreted/JIT packages (Julia, Python, R); no Julia, R or Python version stated. geometryops/Project.toml sets compat GeometryOps = 0.1.26; pixi.toml pins geopandas &gt;=1.1.1,&lt;2, pandas &gt;=2.3.2, numpy &gt;=2.3.2 and pyogrio &gt;=0.11.1,&lt;0.12; R package versions are not pinned. |
| **Adoption** | 84 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/JuliaGeo/GeometryOps.jl) · [benchmark](https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/timings.csv) |

## Verdict

Third-party kadyb/vector-benchmark (Ryzen 9 5900X, Ubuntu 22.04, median of runs; no Julia/R/Python versions) shows GeometryOps ahead of GEOS-through-wrappers on three point tasks: distance on a 5,000 x 5,000 point matrix 0.11 s vs 0.9 s (GeoPandas) and 5.37 s (R geos, row-wise sapply), 500,000 points-in-polygon intersects 0.04 s vs 0.12 s / 0.08 s, and sampling 0.04 s vs 0.9 s. The project's own direct comparison against LibGEOS (GEOS 3.14.1, Apple M4 Pro) shows it slower than GEOS on predicates and overlays except points x area unions.

## Use it when

- You already work in Julia and want generic geometry operations over GeoInterface types (GeoDataFrames, Shapefile, GeoJSON, ArchGDAL objects) without converting to GEOS.
- Bulk simple point workloads (pairwise point distances, many points against one polygon, rejection sampling inside a polygon) where kadyb/vector-benchmark measured 0.11 s vs 0.9 s (GeoPandas) and 0.04 s vs 0.12 s / 0.08 s (GeoPandas / R geos).
- Many repeated point-in-polygon queries against one large polygon, using GO.prepare (1.2 us per query on Canada vs 62.6 us unprepared in its own benchmark).
- Spherical-manifold predicates and overlays (great-circle edges) that GEOS does not offer, accepting about 5-11x the planar cost.
- Points x area overlays (union/symdifference of a MultiPoint with a polygon), the one case its own benchmark shows ahead of LibGEOS (2.4 ms vs 20.6 ms).

## Skip it when

- From C++: it is Julia-only and needs an embedded Julia runtime, so for a C++ project call GEOS, TG or Boost.Geometry directly.
- Polygon overlay throughput: its own benchmark (Apple M4 Pro, Julia 1.12.6, GEOS 3.14.1) has OverlayNG 2-4x slower than LibGEOS on country pairs and about 30x slower on river x country intersection; issue #129 reports Foster-Hormann clipping more than 10x slower than LibGEOS above about 100 vertices.
- Pairwise predicate filtering of mostly disjoint polygons: RelateNG takes 1.6 us per pair vs 115.7 ns for LibGEOS (about 14x behind).
- Union/difference on MultiPolygon inputs with the default Foster-Hormann engine, which raises MethodError per the project's benchmark notes; the OverlayNG alternative is marked experimental and has a known ring-assembly defect cluster.
- Production code that needs a stable API: the README warns it is 'still under heavy development', the version is 0.1.x, and open bug issues cover clipping on barely touching or coverage-like polygons (#281, #337), difference (#335) and touches (#155).

## How it is fast

Julia compiles each call specialised to the concrete geometry and coordinate types (plain tuples after GO.tuples), so tight loops such as point-to-point distance or point-in-polygon have no per-row interpreter or wrapper marshalling cost. Clipping uses Foster-Hormann with selectable edge-intersection accelerators (NestedLoop, single/dual STRtree, natural-index trees, AutoAccelerator), and the newer OverlayNG/RelateNG ports of the JTS algorithms use exact adaptive predicates plus a prepared, indexed point-in-area locator (GO.prepare). There is no GEOS-beating kernel algorithm: the third-party wins come from avoiding Python/R per-row overhead on simple point tasks.

## Compared with alternatives

Pick it over TG or qdgeo only when you are in Julia and want GeoInterface-generic, planar plus spherical operations in one package; for raw predicate speed TG is faster than GEOS prepared, and GeometryOps can even call it through GO.TG(). Arctern and qdgeo target the same GeoPandas/Shapely baseline from C++/GPU or Rust/WASM and are the better fit outside Julia.

## Integration

| | |
|---|---|
| **Form** | module (Julia package, registered as GeometryOps; core types in the GeometryOpsCore subpackage) |
| **Dependencies** | GeoInterface, GeometryOpsCore, ExactPredicates, AdaptivePredicates, DelaunayTriangulation, SortTileRecursiveTree, StaticArrays, Tables, DataAPI, Extents, GeoFormatTypes, CoordinateTransformations, AbstractTrees, PrecompileTools; optional extensions for LibGEOS (buffer and GEOS backend), Proj (reprojection), TGGeometry (libtg predicates), DataFrames, DimensionalData, FlexiJoins, Makie |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat) |
| **Platforms** | any platform Julia supports (pure Julia); buffer needs LibGEOS.jl and reprojection needs Proj.jl, both binary artifacts |
| **Thread safety** | apply/applyreduce-based operations take a `threaded` keyword (default false) to parallelise over sub-geometries or table rows; thread safety of concurrent calls is not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- GO.buffer always delegates to GEOS (LibGEOS must be loaded), so its vector-benchmark buffer time (5.75 s vs 4.07 s GeoPandas) is GEOS against GEOS.
- The third-party wins compare different strategies: GeoPandas distance runs a Python-level apply loop over 5,000 rows and GeoPandas intersects uses a cached STRtree sindex query, while GeometryOps brute-forces a Julia comprehension/broadcast after JIT warm-up.
- Unprepared predicates recompute extents on every call; GO.tuples(x; calc_extent = true) or GO.prepare change point-in-area cost from 62.6 us to 21.9 us or 1.2 us per query.
- Foster-Hormann returns a list of geometries, while OverlayNG returns a single most-specific geometry (possibly mixed-dimension), so switching engines changes result shapes.

## Known shortcomings

- Julia, not callable from C++. In kadyb/vector-benchmark, buffer uses GEOS via LibGEOS inside GeometryOps, transform uses PROJ on both sides and load/write uses GDAL, so real GEOS-vs-native comparisons are only distance, intersects and sample. Distance uses 5,000 points, not 500k. Julia is timed warm (Chairmarks) while R/Python are timed cold.
- The win holds only against GEOS called through Python/R wrappers. Its own benchmarks (overlayng_realdata.jl, relateng_realdata.jl; M4 Pro, Julia 1.12.6, GEOS 3.14.1) show it slower than LibGEOS called directly: overlay 2-4x slower, river x country intersection 30x, pairwise intersects 14x, prepared point-in-polygon \~2x; the only win is points x area union (8.6x). The default Foster-Hormann union/difference on MultiPolygons raises MethodError.

## Caveats and trade-offs

Only distance, intersects and sample compare GeometryOps' own pure-Julia code against GEOS. In buffer, GeometryOps calls GEOS itself via LibGEOS. Transform is PROJ on both sides, and load/write are GDAL I/O, so none of those are GEOS comparisons. GEOS is reached through wrappers (GeoPandas/Shapely, R 'geos'), so per-call marshalling overhead is part of the baseline. The R geos distance time (5.37 s) comes from an sapply loop over geos_distance, one row at a time. The script's commented-out alternatives (a matrix loop and a fully vectorised call) are noted at about 11 s, so the R wrapper itself, not just the loop style, looks like the bottleneck. Julia is timed after JIT warm-up with Chairmarks, while R/Python take the median of 10 cold-start-inclusive runs. Each package's scripts were written by that package's developers: the Julia side by GeometryOps lead asinghvi17 (PR #12, 2024) and JuliaGeo's evetion (PRs #15-#17, 2025), and the GeoPandas side updated by GeoPandas maintainer martinfleis (PR #18). The suite owner kadyb re-ran everything on one machine. Suite repo: 23 stars, MIT. Its detailed report is on github.io and was not reachable. GeometryOps' README points at this suite and says 'More benchmarks coming soon', and the package warns it is under heavy development. Julia is outside the 'usable from C++' scope.

Pure Julia, GeoInterface.jl-based, mostly 2D/2.5D geometry; not callable from C++ without embedding Julia. README warns the package is under heavy development. Includes OGC predicates, clipping (intersection, union, difference), simplification and more.

## Maintenance

Actively developed (last commit 2026-09-20, 488 commits, about 135 open issues and 44 open PRs) and MIT-licensed, but explicitly in-development 0.1.x software usable only from Julia.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** timings.csv in the third-party kadyb/vector-benchmark repo has every quoted median (e.g. distance 0.11 GeometryOps vs 0.9 GeoPandas vs 5.37 R geos; intersects 0.04 vs 0.12 vs 0.08), and the suite owner (kadyb) re-ran all packages himself ('update benchmark results', 2025-09-24), so this is an independent measurement. It is not A: the scripts are public and the CPU (Ryzen 9 5900X) is stated, but no Julia/R/Python versions are given and the package versions are only partly pinned.
- **Verifier notes:** Numbers verified against timings.csv; benchmark scripts read. Main fix: buffer (GEOS via LibGEOS), transform (PROJ vs PROJ) and load/write (GDAL) are not GeometryOps-vs-GEOS wins or losses, and the distance task uses 5,000 points rather than 500,000. Metadata matches: MIT, 84 stars, not archived, last commit 2026-09-20.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/timings.csv>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/pixi.toml>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/Project.toml>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/distance.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/intersects.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/sample.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/transform.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/buffer.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geos/distance.R>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geos/intersects.R>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geopandas/distance.py>
  - <https://github.com/kadyb/vector-benchmark>
  - <https://github.com/kadyb/vector-benchmark/tree/main/geometryops>
  - <https://github.com/kadyb/vector-benchmark/commits/main>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/README.md>
  - <https://github.com/JuliaGeo/GeometryOps.jl>
  - <https://github.com/JuliaGeo/GeometryOps.jl/commits/main>
- **Sources the enricher read:**
  - <https://github.com/JuliaGeo/GeometryOps.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/GeometryOps.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/types.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/clipping/intersection.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/clipping/clipping_processor.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/clipping/overlayng/api.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/distance.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/geom_relations/intersects.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/src/methods/buffer.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/GeometryOpsCore/src/keyword_docs.jl>
  - <https://github.com/JuliaGeo/GeometryOps.jl/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/benchmarks/benchmarks.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/benchmarks/overlayng_realdata.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/benchmarks/relateng_realdata.jl>
  - <https://github.com/JuliaGeo/GeometryOps.jl/tree/main/ext>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/ext/GeometryOpsTGGeometryExt/GeometryOpsTGGeometryExt.jl>
  - <https://raw.githubusercontent.com/JuliaGeo/GeometryOps.jl/HEAD/ext/GeometryOpsLibGEOSExt/GeometryOpsLibGEOSExt.jl>
  - <https://github.com/JuliaGeo/GeometryOps.jl/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/JuliaGeo/GeometryOps.jl/issues/129>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/timings.csv>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/distance.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/intersects.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/sample.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geometryops/buffer.jl>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geopandas/distance.py>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geopandas/intersects.py>
  - <https://raw.githubusercontent.com/kadyb/vector-benchmark/HEAD/geopandas/sample.py>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/juliageo/geometryops.jl`) · [data/wave8/enrich/raw/github_com_juliageo_geometryops_jl.json](../../../data/wave8/enrich/raw/github_com_juliageo_geometryops_jl.json) (enrichment confidence 0.8)

</details>
