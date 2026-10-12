# Bodo DataFrames

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (JIT-compiled to native code via an MPI-based C++ runtime)` · `Apache-2.0` · 🟢 active

> Pandas-API DataFrame library and Numba-based JIT compiling pandas code to MPI-parallel native code; beats Polars on a UDF-heavy vendor benchmark.

| | |
|---|---|
| **Beats** | polars |
| **Claimed result** | Measured with the Bodo JIT path (run_bodo.py --use_jit), not the Bodo DataFrames pandas API. Single r6i.16xlarge (Mar 2025): Bodo 27.71s vs Polars 282.34s (\~10.2x) and vs Daft 69.59s (\~2.5x). 4x r6i.16xlarge (Dec 2024): Bodo 17s vs PySpark 389s, Dask 915s and Modin+Ray 4155s; the chart labels these 20x / 50x / 250x, while the README text says '20-240x'. 4 nodes vs Daft (Mar 2025): 17.54s vs 37.78s (\~2x). The same README's laptop-scale table shows the Bodo DataFrames API slower than Polars: 5.63s vs 1.244s, and 10.221s vs 4.744s on \~20M rows (derived from page data). |
| **Workload** | NYC Taxi FHVHV 'monthly trips with precipitation': the 1,036,465,968-row / 24-column Parquet dataset (24.7 GiB, read from S3) is joined with the 5,538-row Central Park weather CSV. A per-row Python UDF assigns hour-of-day buckets, then the job groups by count and mean trip_miles, sorts, and writes Parquet. The README says 'average trip duration', but the code aggregates trip distance. Single-node run on one AWS r6i.16xlarge (32 physical cores, 512 GiB RAM). |
| **Metric** | throughput |
| **Hardware** | AWS EC2 r6i.16xlarge (32 physical cores, 512 GiB RAM); cluster variant uses 4x r6i.16xlarge |
| **Adoption** | 380 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/bodo-ai/Bodo) · [benchmark](<https://github.com/bodo-ai/Bodo/tree/main/benchmarks/nyc_taxi (README plus benchmarks/img/single-node-bodo-daft-polars.png and benchmarks/img/nyc-taxi-benchmark.png)>) |

## Verdict

Bodo's own taxi benchmark reads 1.04B FHVHV rows from S3 Parquet, joins them with a weather CSV, applies a Python hour-bucket UDF, runs groupby count/mean, sorts and writes Parquet. On one AWS r6i.16xlarge (32 physical cores, 512 GiB) the Bodo JIT path took 27.71s against 282.34s for Polars 1.25.2, about 10x (March 2025), with Polars running the UDF via map_elements. No CPU model, compiler or flags are given, results exist only as PNG charts, the repo's laptop tables show Bodo DataFrames slower than Polars, and a later vendor blog puts Bodo at 39-40.5s on the same single node (about 7x).

## Use it when

- Existing pandas pipelines over tens of millions to billions of rows that you want to speed up without porting them to Polars expressions. Bodo's own guide says to measure at more than 10M rows.
- Jobs dominated by type-stable Python UDFs (Series.map, DataFrame.apply, groupby.agg with custom functions). Bodo compiles these to native code, while Polars would run them in Python via map_elements.
- Multi-node scale-out in place of PySpark, Dask or Modin. On 4x r6i.16xlarge the vendor measured 17s for the taxi job, against 389s for PySpark and 915s for Dask.
- Joins and group-bys larger than memory on one big machine, handled by streaming operators that spill to disk.
- S3 Parquet, Iceberg or Snowflake ETL that benefits from filter pushdown and column pruning, or mixing SQL (BodoSQL) and pandas in one Python process.

## Skip it when

- Small or laptop-scale data. In the repo's own table, Bodo DataFrames takes 10.2s on about 20M rows where Polars takes 4.7s, and 5.63s where Polars takes 1.24s on the smaller set. Spawning workers and loading JIT modules add a fixed cost.
- Code already written as idiomatic Polars expressions. No published run compares Bodo with Polars without map_elements, so the 7-10x single-node gap is not established against native Polars.
- Code that leans on pandas features Bodo lacks. An unsupported call falls back to pandas: the plan is executed, all data is gathered onto one core, and out-of-memory errors become a risk. Columns also cannot hold arbitrary Python objects or mixed types.
- Dynamic Python on the JIT path. try/except, with, comprehensions, class definitions, \*\*kwargs and heterogeneous lists or dicts are unsupported, and DataFrame schemas and groupby, merge or sort keys must be compile-time constants, or compilation fails.
- Environments that need a conservative dependency set. pyarrow is pinned to 25.0.x and numba to &lt;0.66, and the docs label the Bodo DataFrames API experimental. Decimal support in it arrived only in 2026.8 and is described as initial.

## How it is fast

The JIT path is built on Numba. After type inference, a distributed-analysis pass splits arrays and DataFrames into 1D blocks and emits SPMD code in which every MPI rank runs the same compiled function on its own chunk. Python UDFs such as the benchmark's hour-bucket function become native loops. The DataFrames API instead records a lazy plan, optimizes it with a vendored DuckDB optimizer (filter pushdown into Parquet, column pruning, join reordering), and runs it on C++ streaming operators, JIT-compiling UDFs where it can. Joins and group-bys are streaming hash operators: ankerl::unordered_dense tables, recursive hash partitioning with spill to disk, SIMD blocked Bloom filters as runtime join filters, and MPI shuffles between ranks. Against Polars, much of the gap comes from Polars running the same UDF row by row in Python through map_elements, which Polars' own docs call much slower than native expressions.

## Compared with alternatives

Pick Bodo over chDB when you want to keep pandas code, including Python UDFs, and scale it across MPI nodes. Pick chDB when writing SQL against DataFrames in a single process is acceptable: it leads the ClickBench DataFrame view (x1.35 vs Polars x9.99). Umbra is a SQL DBMS, not a Python DataFrame library, so it competes only if the workload can move into a database.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | pyarrow &gt;=25.0,&lt;25.1 (pinned), numba &gt;=0.62,&lt;0.66, pandas &gt;=2.2, numpy &gt;=1.24, mpi4py &gt;=4.1, fsspec, cloudpickle, psutil, requests, pytz; an MPI runtime (MPICH vendored in the Linux build, openmpi on macOS, Intel MPI runtime on Windows); optional extras include s3fs, pyiceberg, snowflake-connector-python and sqlalchemy |
| **Minimum toolchain** | Python 3.10+ (wheels for 3.10-3.14); Linux wheels are manylinux_2_27/2_28 (glibc 2.27+); macOS wheels target macOS 12+ on arm64 |
| **Platforms** | PyPI 2026.8 wheels: Linux x86-64 and aarch64, macOS arm64, Windows x86-64. There is no macOS x86-64 wheel on PyPI for 2026.8, though the README still lists Mac x86 and calls Linux ARM 'coming soon'; conda-forge builds not checked. GPU execution for Bodo DataFrames is under development. |
| **Thread safety** | not documented for Python threads; parallelism is multi-process MPI SPMD, with workers spawned on demand (count set by BODO_NUM_WORKERS) |
| **Drop-in for the baseline** | no |

## Gotchas

- In the benchmark, time.time() is taken inside the function compiled with bodo.jit(cache=True), so JIT compilation time is not in Bodo's 27.71s. Bodo's caching doc shows compilation can dominate a first call: 4.6s uncached vs 0.5s cached in its example.
- The two scripts read different S3 copies: Polars reads fhvhv_tripdata_rewrite/ (rewritten 'for consistent schema') and Bodo reads fhvhv_tripdata/. Bodo also ran on the Bodo Platform with a forked Arrow for faster Parquet reads. The vendor's Sept 2025 blog reports 39s for JIT and 40.5s for Bodo DataFrames against the same 282s Polars figure, not the chart's 27.71s.
- Fallbacks only warn. A UDF that fails to compile raises BodoCompilationFailedWarning and runs in Python mode, and an unsupported API raises BodoLibFallbackWarning and collects data to one core. Watch logs for these warnings, or performance quietly degrades.
- JIT scalar access on nullable data (S.iloc[i]) assumes the value is not NA and returns a neutral value ("" for strings) unless you check pd.isna first. Open issue #297 reports a wrong kmeans result because Numba does not recognize a prange array reduction.

## Known shortcomings

- The headline numbers are Bodo's JIT, not the Bodo DataFrames API; the repo's own table has the DataFrames API slower than Polars (5.63 vs 1.24 s). The Polars side uses a row-by-row Python UDF, skewing the comparison \~10x. First-party, no compiler/flags (verifier downgrade).
- The JIT timer sits inside a bodo.jit(cache=True) function, so compile time is excluded; the two sides read different S3 copies and the Bodo side ran a forked Arrow on the Bodo Platform. The vendor's own 2025-09 blog gives \~7x (JIT 39 s, DataFrames 40.5 s vs Polars 282 s), not the chart's 27.71 s. The DataFrames API is experimental; unsupported calls fall back by gathering all data onto one core (OOM risk); pyarrow pinned to 25.0.x; README platform list stale.

## Caveats and trade-offs

First-party benchmark (Bodo's own repo), not an independent suite, and numbers are read from bar-chart PNGs rather than a raw results table. The charts measure the Bodo JIT path: the main README carries a 'TODO: updated graph with Taxi benchmark including Bodo DataFrames Pandas API', and the benchmark README's laptop table shows the Bodo DataFrames API slower than Polars (5.63s vs 1.244s; 10.221s vs 4.744s). The Polars implementation buckets hours with map_elements and a Python UDF (row-by-row Python over \~1B rows), which Bodo JIT compiles to native code, so the \~10x single-node gap largely reflects a non-idiomatic Polars baseline. Bodo ran on the Bodo Platform with a forked Arrow for faster Parquet reads. The package table lists bodo 2025.8.2 while the charts date from Dec 2024 / Mar 2025. No compiler/flags are given, and the CPU is identified only by instance type. The single-node comparison excludes pandas.

Drop-in pandas-API replacement but relies on JIT compilation and MPI for parallelism; the Bodo Platform build used for the cluster run links a forked version of Arrow for faster Parquet reads (bodo-ai/arrow-cpp-feedstock), a deviation from stock Apache Arrow

## Maintenance

Actively maintained: last commit 2026-09-25, roughly monthly releases, latest PyPI release 2026.8 on 2026-08-17. Apache-2.0 and installable with pip or conda, but the DataFrames API is still marked experimental; the JIT is the more mature path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** These are first-party numbers from Bodo's own repo. The per-system scripts are public (benchmarks/nyc_taxi/bodo/, benchmarks/nyc_taxi/polars/, benchmarks/nyc_taxi/daft/), and the README gives the instance type (r6i.16xlarge) and package versions. But results appear only as PNG bar charts, and no CPU model, compiler or flags are stated, so this falls short of A. It is not an independent suite, so it is C.
- **Verifier notes:** The numbers match the PNGs exactly, but they belong to Bodo JIT, not the 'Bodo DataFrames' API the record is named after. The repo's own small-scale table has Bodo DataFrames losing to Polars. Consider renaming the entry to Bodo (JIT) or at least keeping the caveat. The last commit is 2026-09-25T18:10Z (pushed_at is 2026-09-26). License is Apache-2.0, 380 stars, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bodo-ai/Bodo>
  - <https://github.com/bodo-ai/Bodo/tree/main/benchmarks/nyc_taxi>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/README.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/img/single-node-bodo-daft-polars.png>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/img/nyc-taxi-benchmark.png>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/img/bodo-daft-comparison.png>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/README.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/polars/nyc_taxi_precipitation.py>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/polars/polars-cluster.yaml>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/polars/run_polars.sh>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/bodo/nyc_taxi_precipitation.py>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/benchmarks/nyc_taxi/bodo/run_bodo.py>
- **Sources the enricher read:**
  - <https://github.com/bodo-ai/Bodo>
  - <https://github.com/bodo-ai/Bodo/blob/main/README.md>
  - <https://github.com/bodo-ai/Bodo/tree/main/benchmarks/nyc_taxi>
  - <https://github.com/bodo-ai/Bodo/blob/main/benchmarks/nyc_taxi/README.md>
  - <https://github.com/bodo-ai/Bodo/blob/main/benchmarks/nyc_taxi/bodo/nyc_taxi_precipitation.py>
  - <https://github.com/bodo-ai/Bodo/blob/main/benchmarks/nyc_taxi/bodo/run_bodo.py>
  - <https://github.com/bodo-ai/Bodo/blob/main/benchmarks/nyc_taxi/polars/nyc_taxi_precipitation.py>
  - <https://github.com/bodo-ai/Bodo/blob/main/pyproject.toml>
  - <https://github.com/bodo-ai/Bodo/blob/main/docs/docs/api_docs/dataframe_lib/index.md>
  - <https://github.com/bodo-ai/Bodo/blob/main/docs/docs/about_bodo.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/docs/docs/guides/dataframes/dataframes_intro.md>
  - <https://github.com/bodo-ai/Bodo/blob/main/docs/docs/guides/jit_development/bodo_parallelism/not_supported.md>
  - <https://github.com/bodo-ai/Bodo/blob/main/docs/docs/guides/jit_development/diagnostics_and_troubleshooting/compilation.md>
  - <https://github.com/bodo-ai/Bodo/blob/main/docs/docs/guides/jit_development/performance/caching.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/docs/docs/guides/jit_development/bodo_parallelism/bodo_parallelism_basics.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/docs/docs/guides/installation_and_setup/install.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/docs/docs/release_notes/2026.08.md>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/bodo/libs/_join_hashing.h>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/bodo/libs/streaming/_join.h>
  - <https://raw.githubusercontent.com/bodo-ai/Bodo/main/bodo/libs/_stl.h>
  - <https://github.com/bodo-ai/Bodo/issues>
  - <https://github.com/bodo-ai/Bodo/issues/957>
  - <https://github.com/bodo-ai/Bodo/issues/326>
  - <https://github.com/bodo-ai/Bodo/issues/438>
  - <https://github.com/bodo-ai/Bodo/issues/297>
  - <https://pypi.org/pypi/bodo/json>
  - <https://www.bodo.ai/blog/python-dataframes-bodo-daft-polars-pyspark-dask-modin-ray-compete-for-your-nyc-taxi-fare>
  - <https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.map_elements.html>
  - <https://hn.algolia.com/api/v1/search?query=bodo%20polars&tags=comment>
  - <https://hn.algolia.com/api/v1/search?query=bodo.ai&restrictSearchableAttributes=url>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bodo-ai/bodo`) · [data/wave6/enrich/raw/github_com_bodo_ai_bodo.json](../../../data/wave6/enrich/raw/github_com_bodo_ai_bodo.json) (enrichment confidence 0.72)

</details>
