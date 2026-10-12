# Arctern

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Abandoned (2020) Arrow-columnar C++ GIS engine with GeoPandas-style Python API; claims 7x single-thread and 24x multi-thread over 2020 GeoPandas.

| | |
|---|---|
| **Beats** | GeoPandas (Python geometry operations over Shapely/GEOS) |
| **Claimed result** | README: 'In the latest version 0.2.0, Arctern achieves 24x speedup against GeoPandas. Even under single-thread execution, Arctern outperforms GeoPandas 7x on average.' Also up to 36x for GPU-accelerated spatial-relation operations over CPU counterparts. The README bar chart (read by eye, per-operation) shows multi-thread bars from about 2x (geom_equals) to about 60x (is_simple) and a single-thread bar for geom_equals below GeoPandas. |
| **Workload** | Vectorised GeoSeries operations (within, contains, intersects, intersection, area, distance, simplify, convex_hull, is_valid, is_simple and others) on a geometry dataset, comparing GeoPandas with Arctern single-thread and multi-thread (v0.2.0). |
| **Metric** | throughput |
| **Adoption** | 103 stars |
| **Last commit** | 2020-06-23 |
| **Links** | [repository](https://github.com/arctern-io/arctern) · [benchmark](https://github.com/arctern-io/arctern/blob/master/README.md) |

## Verdict

First-party README claim for v0.2.0: 24x average speedup over GeoPandas with multi-threading and 7x single-threaded across GeoSeries operations; the per-operation bar chart spans about 2.3x (geom_equals) to about 61x (is_simple) multi-threaded, and single-threaded geom_equals is slower than GeoPandas (about 0.6x). Dataset, hardware, thread count, compiler and GeoPandas version are not stated; given the June 2020 timing, the baseline was GeoPandas before 0.8 (June 24, 2020) added optional PyGEOS vectorisation, so it looped over Shapely 1.x objects in Python.

## Use it when

- Studying or reviving a columnar, Arrow-native design for batch spatial predicates over millions of WKB geometries; the C++ is Apache-2.0 and can be mined for ideas
- Legacy 2020-era stacks pinned to pre-vectorised GeoPandas (before 0.8 added PyGEOS) where per-row Python loops over Shapely dominate run time
- Experiments with CUDA spatial predicates (st_within.cu, st_intersects.cu, st_distance.cu) on Arrow data, if you can still build against CUDA 10-era toolchains
- Point-in-polygon joins via ST_IndexedWithin (GEOS STRtree or Quadtree) in a pipeline that already speaks Arrow

## Skip it when

- Any new project: the repo has had no commits since 2020-06-23, the roadmap (distributed GeoSeries, KNN, trajectories) was never finished here, and open bug reports from 2020-2021 are unanswered
- As a replacement for current GeoPandas: GeoPandas 1.0 (June 2024) runs on Shapely 2's vectorised C core, so the 2020 baseline that produced the 24x claim no longer exists and no newer comparison is published
- When you want faster geometry algorithms rather than less Python overhead: the CPU predicates are GEOS via GDAL/OGR, so per-geometry cost is roughly GEOS's; TG or GeoRepair target that directly
- Environments without conda: the build expects CONDA_PREFIX for GDAL, Arrow and GEOS headers, compiles with -Werror, and the render module needs OSMesa/GLU (CPU) or EGL/GL plus CUDA (GPU)
- Windows or aarch64: CMake recognises only x86_64 and ppc64le; other targets fall through as 'unknown'

## How it is fast

On the CPU path the geometry work is still GDAL/OGR (createFromWkb, then OGRGeometry::Within/Contains/Intersects/IsValid, which call GEOS), so the speedup comes from running whole columns through C++ over Arrow WKB buffers instead of looping over Shapely objects in Python, plus a few shortcuts (for example a closed-form point-in-circle test for Within against a circular CurvePolygon). ST_IndexedWithin builds a GEOS STRtree or Quadtree for point-in-polygon joins. The optional GPU path implements Within, Intersects, Distance, Area and similar predicates as CUDA functors over decoded Arrow buffers. How the multi-thread mode is achieved is not documented; I found no thread pool or OpenMP in the C++ GIS code, the Cython layer or the GeoSeries Python I read.

## Compared with alternatives

Rarely. TG beats GEOS on point-in-polygon throughput itself and is a small, maintained C library; GeoRepair and qdgeo target GEOS's slow validity and overlay operations directly. Arctern is only relevant if you want an Arrow-columnar, GeoPandas-shaped batch layer (or its CUDA predicates) and accept an abandoned GDAL/GEOS-based codebase.

## Integration

| | |
|---|---|
| **Form** | shared lib (libarctern; static with STATIC_LIB_SWITCH) plus Cython Python package and PySpark module |
| **Dependencies** | GDAL/OGR (with GEOS), Apache Arrow, GEOS C++ index headers, miniz, stb; OSMesa and GLU for CPU rendering; CUDA 10+, GL and EGL for the GPU build; conda environment for headers and libs |
| **Minimum toolchain** | C++14 (CMake sets CMAKE_CXX_STANDARD 14; Cython extension built with -std=c++11), CMake 3.12+, CUDA 10 for GPU |
| **Platforms** | Linux x86_64 and ppc64le (ppc64le adds -mfloat128); macOS detected in CMake but not documented as supported; no Windows or aarch64 path |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the Python GeoSeries copies GeoPandas's interface for the supported operations, but it is a separate package with its own WKB-in-Arrow storage, and GeoDataFrame, sjoin and many GeoPandas features are missing |

## Gotchas

- The CPU kernels round-trip every geometry WKB -&gt; OGRGeometry -&gt; (GEOS) per call, so chained operations pay parse and serialise costs each time; the speedup is from batching, not from a new algorithm
- index_builder.cpp includes GEOS's C++ headers (geos/indexStrtree.h, geos::index::strtree::STRtree) rather than the GEOS C API, which ties it to the GEOS version of 2020 conda builds
- Release builds add -O3 and -D_ARROW_ARRAY_SIZE=1073741824; Debug builds cap Arrow chunks at 16M, so behaviour around very large columns differs between build types
- The README's headline 36x GPU figure is GPU vs Arctern's own CPU code, not vs GeoPandas or GEOS

## Known shortcomings

- CPU path is built on GDAL/OGR (GEOS), so the gain is mostly batching and threads over Python; single-thread geom_equals is slower than GeoPandas.
- CPU path is GDAL/OGR calling GEOS, so the gain comes from batching, not a faster algorithm. Baseline is pre-0.8 GeoPandas (June 2020) looping over Shapely objects in Python; GeoPandas 1.0 on vectorised Shapely 2 makes the 24x claim outdated. Multi-thread mode undocumented. Uses GEOS C++ headers instead of the stable C API.

## Caveats and trade-offs

The baseline is GeoPandas, a Python wrapper over Shapely/GEOS. Arctern's CPU path is built on GDAL/OGR (cpp/src/gis/gdal), which itself relies on GEOS for most predicates, so much of the gain is probably batch processing without per-geometry Python overhead plus multi-threading rather than a faster geometry algorithm. Dataset, hardware, thread count, compiler and flags are not stated (CMake Release uses -O3), and per-operation numbers exist only in a chart image: multi-thread bars range from about 2.3x (geom_equals) and 3.9x (geometry_type) to about 61x (is_simple), single-thread geom_equals is about 0.6x (slower than GeoPandas), and multi-thread intersection is slightly below single-thread. The 36x GPU figure is against Arctern's own CPU code. No comparison with GEOS called directly from C++. Dormant since 2020-06-23 (v0.2.0).

C++ core in cpp/ plus Python, Spark and GUI parts; conda-based build; the GPU path needs CUDA; the repo has seen no commits since June 2020 and the roadmap items (distributed GeoSeries, KNN) were never finished in this repo.

## Maintenance

Abandoned since 2020-06-23 (v0.2.0, 103 stars, 8 open issues) but Apache-2.0; heavy conda/GDAL/Arrow build makes it a source of ideas rather than something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README headline (24x multi-thread, 7x single-thread vs GeoPandas) and a per-operation speedup chart image, with no dataset, hardware, thread count, compiler or benchmark script.
- **Verifier notes:** README quotes and chart readings match (average bars about 23.9x multi-thread and 7.2x single-thread). Metadata confirmed on github.com: Apache-2.0, 103 stars, 49 forks, not archived, last commit 2020-06-23.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/README.md>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/doc/img/v0.2.0_intro/performance_geopandas_vs_arctern.png>
  - <https://github.com/arctern-io/arctern>
  - <https://github.com/arctern-io/arctern/commits>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/cmake/ThirdParty.cmake>
  - <https://github.com/arctern-io/arctern/tree/master/cpp/src/gis>
- **Sources the enricher read:**
  - <https://github.com/arctern-io/arctern>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/README.md>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/cmake/ThirdParty.cmake>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/thirdparty/versions.txt>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/gis/api.h>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/gis/gis_functions.cpp>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/gis/gdal/gis_functions.cpp>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/gis/gdal/arctern_geos.h>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/gis/spatial_join/st_indexed_within.cpp>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/cpp/src/index/index_builder.cpp>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/ci/scripts/cpp_build.sh>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/setup.py>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/arctern/_wrapper_func.py>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/arctern/geoseries/geoseries.py>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/arctern/geoseries/geoarray.py>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/arctern/cython/arctern_core_.pyx>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/python/arctern/cython/arctern_core__.pxd>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/tests/perf_regression.py>
  - <https://raw.githubusercontent.com/arctern-io/arctern/master/tests/test_vectory_impl.py>
  - <https://github.com/arctern-io/arctern/tree/master/cpp/src/gis>
  - <https://github.com/arctern-io/arctern/tree/master/python/arctern>
  - <https://github.com/arctern-io/arctern/tree/master/doc>
  - <https://github.com/arctern-io/arctern/tree/master/tests>
  - <https://github.com/arctern-io/arctern/issues>
  - <https://github.com/arctern-io/arctern/issues?q=is%3Aissue+benchmark>
  - <https://raw.githubusercontent.com/geopandas/geopandas/HEAD/CHANGELOG.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arctern-io/arctern`) · [data/wave8/enrich/raw/github_com_arctern_io_arctern.json](../../../data/wave8/enrich/raw/github_com_arctern_io_arctern.json) (enrichment confidence 0.65)

</details>
