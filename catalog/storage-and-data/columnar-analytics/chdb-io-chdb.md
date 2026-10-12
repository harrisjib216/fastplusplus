# chDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> In-process ClickHouse SQL engine for Python that queries pandas DataFrames directly; median \~166x faster than pandas on ClickBench.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | The README screenshot (committed 2024-10-17) of the ClickBench DataFrame view on c6a.metal shows relative time chDB x1.35, DuckDB x1.40, Polars x9.99 and Pandas x71.18, i.e. \~53x vs Pandas and \~7.4x vs Polars. Current ClickBench raw results on c6a.metal, as the sum of hot-run times (min of runs 2-3) over 43 queries: chDB (DataFrame, 2026-08-16) 6.00s vs pandas (2026-08-24) 2430.31s (\~405x) and Polars (DataFrame, 2026-08-24) 11.92s (\~2.0x). The latest DuckDB (DataFrame) c6a.metal run (2025-10-09) totals 9.57s (derived from page data). |
| **Workload** | ClickBench 'DataFrame' comparison view (43 analytical queries over the hits dataset), chDB vs Pandas vs Polars vs DuckDB, all run in DataFrame mode on AWS c6a.metal (500GB gp2) |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c6a.metal, 500GB gp2 storage |
| **Adoption** | 2.9k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/chdb-io/chdb) · [benchmark](<https://github.com/ClickHouse/ClickBench/tree/main/chdb-dataframe (current raw results: chdb-dataframe/results/20260816/c6a.metal.json vs pandas/results/20260824/c6a.metal.json and polars-dataframe/results/20260824/c6a.metal.json; the README image https://github.com/chdb-io/chdb/raw/main/docs/_static/df_bench.png is an Oct-2024 snapshot)>) |

## Verdict

In ClickBench's DataFrame mode (43 queries against the hits data preloaded into an \~82 GB pandas DataFrame, the same FastAPI harness for every system, AWS c6a.metal, prebuilt pip wheels, no compiler flags stated), chDB's hot total (best of runs 2-3) was 6.00 s on 2026-08-16, against 2,430 s for pandas and 11.92 s for Polars on 2026-08-24. Per query, chDB's median speedup is \~166x over pandas (range 2.9x to 5,058x; three lambda-heavy pandas queries make up \~71% of the pandas total) and 1.77x over Polars; cold runs include reloading the DataFrame (\~71 s per query for chDB), and the README's Oct-2024 chart (x1.35 vs pandas x71.18) is out of date.

## Use it when

- Analytical SQL (group-by, top-N, count distinct, string LIKE filters) over multi-GB pandas DataFrames or Parquet files on one many-core Linux or macOS machine, where pandas runs single-threaded.
- Replacing lambda-heavy pandas pipelines: the ClickBench pandas queries built on groupby().filter(lambda ...) took 536 s and 1,005 s hot, against 0.11 s and 0.31 s in chDB on the same DataFrame.
- Notebooks or ETL scripts that want ClickHouse's SQL dialect and functions, plus file, S3, MySQL and Postgres table functions, without running a ClickHouse server.
- Embedding an OLAP engine in C, C++, Go, Rust or Node through the libchdb C ABI (shared or static tarballs are published with each chdb-core release) when your team already standardizes on ClickHouse SQL.
- ARM servers: on Graviton c8g.metal-48xl the chDB DataFrame hot total was 3.53 s, against 4.96 s for Polars and 1,418 s for pandas (Aug 2026 ClickBench).

## Skip it when

- Tiny DataFrames or tight per-call loops. Open issue #442 measures over 1 ms per simple query on a 1,000-row frame (pandas 0.1 ms, DuckDB 0.6 ms), mostly from building the query plan and pipeline. Open issue #254 reports short ClickBench queries running slower on c6a.metal than on the smaller c6a.4xlarge.
- If you already use Polars, the gain is modest. On c6a.metal the median per-query speedup is 1.77x (geomean 1.52x), and Polars is faster on 9 of 43 queries, mostly the cheap ones.
- Windows has no native build (ClickHouse does not compile there, per issue #368), so it runs only through WSL.
- Size-constrained deployments: the chdb-core wheel that holds the engine is 104-175 MB, against 2 MB for the pure-Python chdb wheel.
- Code that needs exact pandas semantics. The engine does not support category or timedelta dtypes, the Python() source adds the local timezone offset to dates (an open xfail as of Jan 2026), and DataStore returns nullable integer dtypes where pandas returns float64 or object.

## How it is fast

The speed comes from ClickHouse's vectorized, block-at-a-time columnar execution: typed column vectors run through tight batch loops in a multi-threaded pipeline that uses every core. pandas is mostly single-threaded, and the ClickBench pandas versions of several queries depend on Python lambdas. chDB's Python() table source (PythonSource.cpp) maps contiguous numpy numeric buffers without copying them, splits the frame into blocks that N parallel streams read round-robin, and applies filters before it builds the other columns (at 1/8 selectivity or lower it copies out only the selected rows), and some string predicates run directly on Arrow string buffers. A per-session PythonTableCache keeps schema inference, column sizes and Arrow chunk tables between queries, which cuts the fixed per-query overhead on repeated runs.

## Compared with alternatives

Pick chDB over Bodo DataFrames when you want SQL over DataFrames already in memory, inside one pip-installed process, with no JIT compilation step (Bodo's catalogued win comes from its JIT path, not its pandas API). Pick it over Umbra when you need something open-source and embeddable: Umbra has no public repo in the catalog, and its 7.41 s ClickBench total comes from its own loaded tables, not DataFrame mode, so it cannot be compared directly with chDB's 6.00 s.

## Integration

| | |
|---|---|
| **Form** | module (Python abi3 wheels: chdb on top of chdb-core); the engine also ships as a prebuilt shared lib and a static lib (libchdb, C header chdb.h) |
| **Dependencies** | chdb needs chdb-core&gt;=26.7.0, pandas&gt;=2.1.0 and pyarrow&gt;=13.0.0. chdb-core bundles the whole ClickHouse engine in one binary wheel. |
| **Minimum toolchain** | Python 3.9+ with prebuilt wheels. Building from source needs Clang 21+ and C++23 (the ClickHouse toolchain; GCC is rejected). |
| **Platforms** | Linux x86-64 and aarch64 (manylinux2014), macOS x86-64 (10.15+) and arm64 (11+). No Windows. Separate WebAssembly and Cloudflare builds exist, and a free-threaded Python 3.14t build is published as a GitHub release asset. |
| **Thread safety** | Sessions are documented as thread-safe. Queries from different connections or threads run in parallel safely. Each connection supports only one cursor, and an open streaming query must be serialized per connection. A process hosts a single engine bound to one database path, so connect() to a different path raises while other connections are open. |
| **Drop-in for the baseline** | partial — the benchmarked path is SQL over Python(df), not the pandas API. DataStore imitates pandas (209 DataFrame methods listed) but documents gaps: no inplace=True, groupby returns pandas objects, category and timedelta dtypes are unsupported, and some dtype and timezone results differ. |

## Gotchas

- The repo was split. The catalogued chdb-io/chdb is now pure Python (DataStore, agents, durable storage), and the C++ engine lives in chdb-io/chdb-core (a GitHub fork with 22 stars). Engine bugs and releases are tracked there, and ClickBench installs the chdb-core release wheel directly.
- Python(df) finds the DataFrame by variable name at query time (ClickBench's server.py depends on a module-level global named hits). Numeric numpy columns are mapped without copying, but object-dtype string columns are converted element by element from Python str objects on every scan, and they exclude the frame from the session metadata cache. Arrow-backed strings avoid that conversion.
- The embedded ClickHouse version trails upstream, and engine bugs can return silently wrong results. In issue #587, chDB 4.1.8 (ClickHouse 26.3) undercounted = filters on Parquet files with Bloom filters and many row groups. The fix was bumping to ClickHouse 26.5 in chDB 4.1.9, so pin and upgrade chdb-core deliberately.
- If chdb is imported in a parent process, queries in forked child processes hang (issue #355). Use the multiprocessing 'spawn' start method.

## Known shortcomings

- The 7.4x over Polars comes from an Oct 2024 ClickBench snapshot; the live Aug 2026 raw results give chDB 6.00 s vs Polars 11.92 s (\~2x) and pandas 2430 s (\~405x). ClickBench is ClickHouse Inc's suite and chDB is a ClickHouse derivative (verifier downgrade).
- Repo split in 2026-01: chdb-io/chdb is now pure Python and the C++ engine lives in chdb-io/chdb-core (22 stars). The \~405x over pandas is skewed by three lambda-heavy pandas queries (\~71% of pandas time); per query the median is \~166x (range 2.9-5058x). Against Polars the median is only 1.77x and Polars wins 9 of 43 queries. The DuckDB comparison is stale/broken in current ClickBench runs. Tiny queries take &gt;1 ms (#442); no Windows; 104-175 MB wheels; an engine bug gave silently wrong Parquet counts until 4.1.9 (#587); forked child processes hang (#355). Not a pandas drop-in (the benchmark path is SQL over Python dataframes; DataStore lacks category/timedelta and has dtype/timezone gaps).

## Caveats and trade-offs

The README image is an Oct-2024 snapshot. Current ClickBench raw results (Aug 2026) show the Polars gap shrinking from \~7.4x to \~2x, while the pandas gap has widened. ClickBench is maintained by ClickHouse Inc. and chDB is built on ClickHouse (its result JSON is tagged 'ClickHouse derivative'), although all DataFrame runs come from the same public CI harness (github-actions). DataFrame mode times queries over an already-loaded in-memory DataFrame, and load time is excluded from the relative score. No compiler/flags are given (prebuilt wheels), and the CPU is identified only by instance type. The ClickBench README says to take cross-system results with a grain of salt.

chDB embeds ClickHouse's own vectorized engine as an in-process library (no server, no network round-trip), so the win over Pandas/Polars mainly reflects ClickHouse's engine rather than a new algorithm; heavier binary/startup footprint than a pure-Python library

## Maintenance

Actively developed (chdb 4.4.0 and chdb-core 26.7.3 were both released on 2026-09-11, last commit 2026-09-23), Apache-2.0 and maintained by ClickHouse Inc. since chDB joined ClickHouse in 2024; it installs with pip, but engine issues and source are in the separate chdb-io/chdb-core repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** ClickBench is a well-known public suite. Its harness (ClickHouse/ClickBench chdb-dataframe/, pandas/, polars-dataframe/) runs every system through the same CI on c6a.metal and publishes raw per-query JSON, and chDB beats pandas there by a wide margin. It is not A because no CPU model, compiler or flags are stated (prebuilt pip wheels). Independence is also only partial, since ClickBench is maintained by ClickHouse Inc. and chDB is a ClickHouse derivative.
- **Verifier notes:** The screenshot numbers (1.35/1.40/9.99/71.18) match the record exactly, and the latest raw ClickBench JSONs confirm chDB still wins clearly against pandas and Polars. I downgraded from A to B (no compiler/flags/CPU model; the suite is not fully independent of chDB), and replaced the stale screenshot URL with the live raw-results location. The repo is Apache-2.0 with 2,908 stars, last commit 2026-09-23, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chdb-io/chdb>
  - <https://github.com/chdb-io/chdb/raw/main/docs/_static/df_bench.png>
  - <https://raw.githubusercontent.com/chdb-io/chdb/main/README.md>
  - <https://github.com/ClickHouse/ClickBench/tree/main/chdb-dataframe>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/chdb-dataframe/results/20260816/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/pandas/results/20260824/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/pandas/results/20240909/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/polars-dataframe/results/20260824/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-dataframe/results/20251009/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/chdb-io/chdb>
  - <https://raw.githubusercontent.com/chdb-io/chdb/main/README.md>
  - <https://api.github.com/repos/chdb-io/chdb>
  - <https://github.com/chdb-io/chdb/blob/main/pyproject.toml>
  - <https://github.com/chdb-io/chdb/blob/main/requirements.txt>
  - <https://github.com/chdb-io/chdb/blob/main/VERSION-GUIDE.md>
  - <https://github.com/chdb-io/chdb/blob/main/dev-docs/PANDAS_COMPATIBILITY.md>
  - <https://github.com/chdb-io/chdb/blob/main/dev-docs/XFAIL_ANALYSIS.md>
  - <https://github.com/chdb-io/chdb/issues/442>
  - <https://github.com/chdb-io/chdb/issues/391>
  - <https://github.com/chdb-io/chdb/issues/368>
  - <https://github.com/chdb-io/chdb/issues/254>
  - <https://github.com/chdb-io/chdb/issues/587>
  - <https://github.com/chdb-io/chdb/issues/355>
  - <https://github.com/chdb-io/chdb/issues/426>
  - <https://github.com/chdb-io/chdb/issues/197>
  - <https://github.com/chdb-io/chdb/issues/363>
  - <https://github.com/chdb-io/chdb-core>
  - <https://github.com/chdb-io/chdb-core/releases>
  - <https://github.com/chdb-io/chdb-core/blob/main/programs/local/PythonSource.cpp>
  - <https://github.com/chdb-io/chdb-core/blob/main/programs/local/PythonTableCache.h>
  - <https://github.com/chdb-io/chdb-core/blob/main/programs/local/PythonTableCache.cpp>
  - <https://github.com/chdb-io/chdb-core/blob/main/programs/local/chdb.h>
  - <https://github.com/chdb-io/chdb-core/blob/main/chdb/state/sqlitelike.py>
  - <https://github.com/chdb-io/chdb-core/blob/main/chdb/session/state.py>
  - <https://github.com/chdb-io/chdb-core/blob/main/chdb/__init__.py>
  - <https://github.com/chdb-io/chdb-core/blob/main/CMakeLists.txt>
  - <https://github.com/chdb-io/chdb-core/blob/main/cmake/tools.cmake>
  - <https://pypi.org/pypi/chdb/json>
  - <https://pypi.org/pypi/chdb-core/json>
  - <https://github.com/ClickHouse/ClickBench/tree/main/chdb-dataframe>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/benchmark.sh>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/server.py>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/install>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/load>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/query>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/start>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/template.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/chdb-dataframe/data-size>
  - <https://github.com/ClickHouse/ClickBench/blob/main/lib/benchmark-common.sh>
  - <https://github.com/ClickHouse/ClickBench/blob/main/pandas/server.py>
  - <https://github.com/ClickHouse/ClickBench/blob/main/pandas/queries.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/chdb-dataframe/results/20260816/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/chdb-dataframe/results/20260816/c8g.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/pandas/results/20260824/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/pandas/results/20260824/c8g.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/polars-dataframe/results/20260824/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/polars-dataframe/results/20260824/c8g.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-dataframe/results/20251009/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-dataframe/results/20251215/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-dataframe/results/20260511/c8g.metal-48xl.json>
  - <https://hn.algolia.com/api/v1/search?query=chdb&tags=story>
  - <https://auxten.com/the-birth-of-chdb/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/chdb-io/chdb`) · [data/wave6/enrich/raw/github_com_chdb_io_chdb.json](../../../data/wave6/enrich/raw/github_com_chdb_io_chdb.json) (enrichment confidence 0.8)

</details>
