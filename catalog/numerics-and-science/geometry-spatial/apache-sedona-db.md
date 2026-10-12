# SedonaDB (Apache Sedona DB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust single-node spatial SQL/DataFrame engine on DataFusion; beats DuckDB Spatial and GeoPandas on spatial and KNN joins.

| | |
|---|---|
| **Beats** | GeoPandas 1.1.1 and DuckDB 1.4.0 (SpatialBench single-node comparison); neither is one of the listed C++ baselines |
| **Claimed result** | SpatialBench raw table (seconds, SedonaDB / DuckDB / GeoPandas). SF1: q1 0.66/0.96/12.78; q2 8.07/9.95/20.74; q3 0.80/1.17/13.59; q4 8.41/9.83/25.24; q5 5.10/1.80/47.08; q6 8.59/9.36/24.43; q7 1.66/1.82/137.00; q8 1.10/1.08/16.08; q9 0.23/50.15/0.28; q10 18.79/207.84/46.13; q11 32.98/TIMEOUT/51.01; q12 14.55/ERROR/TIMEOUT. SF10: q1 3.04/4.58/ERROR; q2 8.89/8.26/ERROR; q3 4.09/5.17/TIMEOUT; q4 7.52/8.51/ERROR; q5 50.81/14.40/ERROR; q6 9.11/10.67/ERROR; q7 14.44/14.03/ERROR; q8 7.24/7.57/TIMEOUT; q9 0.38/942.98/0.49; q10 42.02/ERROR/ERROR; q11 97.52/ERROR/ERROR; q12 145.66/ERROR/TIMEOUT. Versus DuckDB, SedonaDB is 1.05-1.5x faster on most of q1-q8, about 11x faster on SF1 q10 and 218x (SF1) / 2,480x (SF10) faster on q9, but 2.8x (SF1) and 3.5x (SF10) slower on q5 and marginally slower on SF1 q8 and SF10 q2 and q7. Versus GeoPandas at SF1 it is 1.2x (q9) to 82x (q7) faster on q1-q11 (ratios derived from page data). ERROR/TIMEOUT cells are failures, not ratios. The page itself calls Q5 spatial aggregation a known SedonaDB weakness. |
| **Workload** | SpatialBench v0.1.0 pre-release (commit 9094be8) queries 1-12 at scale factors 1 and 10, run 2025-09-22: spatial filters, geometric computations, spatial joins and KNN joins over dbgen-generated Parquet (WKB geometry) read directly from S3; runtime includes data loading, each result is COUNTed, 1200 s timeout; GeoPandas runs a hand-written single-threaded Python mirror of the SQL. |
| **Metric** | latency |
| **Hardware** | AWS EC2 m7i.2xlarge (8 CPUs, 32 GB RAM); CPU model not named on the page |
| **Compiler and flags** | Released packages with default settings: SedonaDB 0.1.0, DuckDB 1.4.0 (enable_external_file_cache=false), GeoPandas 1.1.1 with Shapely 2.1.1 and NumPy 2.3.3; build flags not stated. |
| **Adoption** | 509 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/apache/sedona-db) · [benchmark](https://github.com/apache/sedona-spatialbench/blob/main/docs/single-node-benchmarks.md) |

## Verdict

Apache Sedona's own SpatialBench (v0.1.0 pre-release, run 2025-09-22) timed SedonaDB 0.1.0, DuckDB 1.4.0 and GeoPandas 1.1.1 with Shapely 2.1.1 on 12 queries at SF1 and SF10, on an AWS m7i.2xlarge (8 vCPU, 32 GB; CPU model not named), from cold S3 Parquet reads, with default settings and no build flags stated. Against DuckDB, SedonaDB was 1.05-1.5x faster on most filter queries, 11x faster on SF1 q10 and 218x/2,480x faster on q9, finished q11-q12 where DuckDB timed out or errored, and was 2.8-3.5x slower on q5 (ratios derived from page data).

## Use it when

- Spatial joins (point-in-polygon, intersects, ST_DWithin) and KNN joins over millions of rows in Parquet/GeoParquet on one machine: the largest wins on the page are q9-q12, where DuckDB 1.4.0 timed out or errored
- Replacing single-threaded GeoPandas pipelines: SF1 queries ran 1.2x to 82x faster than a hand-written GeoPandas mirror, and SedonaDB finished SF10 queries where GeoPandas errored or timed out
- Python or R analytics that already use Arrow, DuckDB or Polars and want a spatial engine with CRS tracking and zero-copy Arrow exchange
- Joins bigger than RAM: the spatial join can partition the build side and spill it to disk
- Optional GPU spatial joins (libgpuspatial, added in 0.4.0) for heavy joins, if you can build and run that path

## Skip it when

- Inside a C++ program that needs geometry predicates, overlays or an index: it is a Rust query engine, not a C++ library; use GEOS, TG or Boost.Geometry directly
- Spatial aggregation queries: SpatialBench q5 ran 2.8x (SF1) and 3.5x (SF10) slower than DuckDB, and the project calls this a known weakness
- Simple spatial filters where DuckDB Spatial is already in the stack: q1-q8 are roughly even (1.0-1.5x either way)
- Projects that need a stable API: the engine is pre-1.0 (0.1.0 in September 2025, 0.4.1 in August 2026, workspace at 0.5.0) and adds features each release
- Transactional or multi-node workloads: it is a single-node analytical engine; the project points to PostGIS-style databases and SedonaSpark/SedonaFlink for those

## How it is fast

Spatial joins are two-phase: a filter phase on a packed Hilbert-sorted R-tree (geo-index RTree&lt;f32&gt; over bounding boxes) and a refine phase that checks exact predicates with tidwall's TG library (y-stripes index, the default), GEOS or the Rust geo crate. A speculative execution mode samples the first 1,000 geometries and then decides whether to build prepared geometries on the build side, the probe side or neither. KNN joins have their own operator. The engine is columnar and vectorized on Arrow and DataFusion, runs multi-threaded with probe-side repartitioning, and can spatially partition and spill the build side to disk for joins larger than memory.

## Compared with alternatives

Pick SedonaDB when the job is a whole spatial query over tables (joins, KNN joins, filters on Parquet) and you are in Python, R or SQL. Use TG or geo-index directly from C or Rust when you only need predicates or an index; SedonaDB uses both inside its join. Arctern targets the same GeoPandas-replacement niche but publishes only its own 24x claim.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python wheel (pip install "apache-sedona[db]" or sedonadb; conda-forge sedonadb); R package on R-multiverse; from source: Rust workspace on Apache Arrow 58 and DataFusion 54, with C libraries GEOS, TG, PROJ, s2geography, GDAL and an optional GPU library behind wrapper crates |
| **Minimum toolchain** | Rust 1.88 (rust-version in Cargo.toml); Python &gt;= 3.9 |
| **Platforms** | PyPI wheels for Linux x86-64 and aarch64 (manylinux_2_28), macOS arm64 and x86-64 (macOS 12+), and Windows x86-64 |
| **Thread safety** | not documented for the Python/R connection objects; queries run multi-threaded inside the engine |
| **Drop-in for the baseline** | partial: SQL with ST_\* functions similar to DuckDB Spatial and PostGIS, plus an experimental GeoPandas-compatible API in 0.4.1; not drop-in for any C++ geometry library |

## Gotchas

- The join's R-tree stores f32 bounding boxes; exact predicates are evaluated in the refine phase, and which library does that (TG by default, then GEOS or geo) depends on sedona.spatial_join options. TG falls back to geo for predicates it does not support
- KNN joins drop tied-distance rows by default (knn_include_tie_breakers = false)
- The published SpatialBench numbers are for 0.1.0 with cold reads from S3 and DuckDB's external file cache turned off; later releases have no published re-run on the same hardware
- For C/C++ hosts the only native entry point is the ADBC driver (AdbcSedonadbDriverInit in rust/sedona-adbc), which you build from source

## Known shortcomings

- Rust spatial SQL engine, not a C++ library (wrong language, arguably wrong category). First-party SpatialBench (m7i.2xlarge, no CPU model, v0.1.0, a year old); 2.8-3.5x slower than DuckDB on q5; the q9 218x/2,480x wins and ERROR/TIMEOUT cells reflect DuckDB/GeoPandas plans and missing KNN-join support.
- A Rust SQL engine, not a C++ library: the only native entry point is the ADBC driver (AdbcSedonadbDriverInit). SpatialBench is first-party and was run on 0.1.0 only; q5 spatial aggregation is 2.8-3.5x slower than DuckDB. Releases are at 0.4.1 (2026-08-22) with main at 0.5.0. Internally it uses tidwall/tg as the default refiner and geo-index's Hilbert RTree, both already catalogued. The spatialists.ch 130-million-point join post (SedonaDB 0.3.0 6 s vs DuckDB 13 s / 1m30s on an M4) is by a Wherobots engineer and SedonaDB contributor, so not independent; the 0.4.0 GPU-join blog (Q11 7.51 s CPU vs 1.61 s on an RTX 3090) is first-party. Both seen only as snippets.

## Caveats and trade-offs

First-party: SpatialBench is the Apache Sedona project's own suite and the results page was written by the same project (datasets sit in a 'wherobots-examples' S3 bucket). The numbers are a year old (SedonaDB 0.1.0, run 2025-09-22) and come from one instance type with no CPU model, no build flags and no stated run count. Baselines are other spatial engines (DuckDB 1.4.0 spatial, GeoPandas 1.1.1/Shapely 2.1.1), not GEOS/CGAL/Boost.Geometry directly. Results are mixed against DuckDB: SedonaDB is 2.8-3.5x slower on q5 and about even on several filter queries; the very large q9/q10 wins and the DuckDB/GeoPandas ERROR and TIMEOUT cells reflect missing native KNN joins or poor plans in the other engines (the page says DuckDB and GeoPandas lack KNN join support and needed hand-written code), not raw geometry speed. GeoPandas is a single-threaded hand-written port. SedonaDB is a Rust engine on DataFusion/Arrow with Python/R bindings, not a C++ library, and is a spatial SQL engine rather than a geometry kernel.

Rust engine with Python (PyPI apache-sedona[db]), SQL and R APIs, not a C++ library; it is a spatial DataFrame/SQL analytics engine rather than a geometry kernel or index, so it does not replace Boost.Geometry, CGAL or GEOS inside C++ code. Version 0.1.0 benchmarked, an early release.

## Maintenance

Very active Apache project (509 stars, 1,084 commits, five PyPI releases from 0.1.0 in September 2025 to 0.4.1 on 2026-08-22, main at 0.5.0); Apache-2.0 and pip/conda installable, but it is a Rust engine and not something you vendor into C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party suite and run (Apache Sedona's own SpatialBench, docs/single-node-benchmarks.md) with public benchmark code, pinned versions and an instance type (m7i.2xlarge) but no CPU model and no build flags, and some gains exceed 50x, so it stays C.
- **Verifier notes:** The README charts point to sedona.apache.org (blocked), but the same results page is checked into apache/sedona-spatialbench docs/single-node-benchmarks.md with an exact raw table, hardware (m7i.2xlarge) and versions; benchmark_url corrected to it and bar readings replaced with the table values. Off-language (Rust) and arguably a database engine rather than a geometry library; record as shortcoming.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/README.md>
  - <https://github.com/apache/sedona-db>
  - <https://github.com/apache/sedona-db/commits>
  - <https://raw.githubusercontent.com/apache/sedona-db/refs/heads/main/docs/image/sf1-09242025.png>
  - <https://raw.githubusercontent.com/apache/sedona-db/refs/heads/main/docs/image/sf10-09242025.png>
  - <https://github.com/apache/sedona-spatialbench>
  - <https://raw.githubusercontent.com/apache/sedona-spatialbench/HEAD/docs/single-node-benchmarks.md>
  - <https://github.com/apache/sedona-spatialbench/blob/main/docs/single-node-benchmarks.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/README.md>
  - <https://raw.githubusercontent.com/apache/sedona-spatialbench/HEAD/docs/single-node-benchmarks.md>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/Cargo.toml>
  - <https://github.com/apache/sedona-db>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/src/lib.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/python/sedonadb/pyproject.toml>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/r/sedonadb/DESCRIPTION>
  - <https://github.com/apache/sedona-db/tree/main/rust/sedona-spatial-join/src>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/src/index.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/src/refine.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/src/partitioning.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-common/src/option.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-spatial-join/src/index/default_spatial_index_builder.rs>
  - <https://github.com/apache/sedona-db/releases>
  - <https://pypi.org/pypi/sedonadb/json>
  - <https://github.com/apache/sedona-db/issues?q=is%3Aissue%20state%3Aopen%20performance>
  - <https://github.com/apache/sedona-db/issues?q=is%3Aissue%20state%3Aopen%20label%3Abug>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-adbc/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/rust/sedona-adbc/src/lib.rs>
  - <https://raw.githubusercontent.com/apache/sedona-db/HEAD/sedona-cli/Cargo.toml>
  - <https://github.com/paleolimbot>
  - https://spatialists.ch/posts/2026/05/07-joining-130-million-points/ (egress-blocked; WebSearch snippet only: SedonaDB 0.3.0 joined 130M points to 33,000 postal-code polygons in 6 s on an Apple M4 laptop vs DuckDB Spatial ST_Contains \~1 m 30 s and ST_DWithin(..., 0) 13 s; author Dewey Dunnington is a Wherobots engineer and SedonaDB contributor, so not independent)
  - https://forrest.nyc/sedonadb-vs-duckdb-vs-postgis-which-spatial-sql-engine-is-fastest/ (egress-blocked; title only)
  - https://sedona.apache.org/latest/blog/2026/06/26/sedonadb-04-gpu-accelerated-spatial-joins/ (not opened; WebSearch snippet only: up to 5.93x on heavy joins, Q11 7.51 s CPU vs 1.61 s on an RTX 3090)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/apache/sedona-db`) · [data/wave8/enrich/raw/github_com_apache_sedona_db.json](../../../data/wave8/enrich/raw/github_com_apache_sedona_db.json) (enrichment confidence 0.7)

</details>
