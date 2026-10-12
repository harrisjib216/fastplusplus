# Apache DataFusion

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Embeddable Rust/Arrow SQL query engine; on ClickBench hot runs over Parquet on a 192-vCPU box, 1.56x faster than DuckDB.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | \~1.6x faster than DuckDB on ClickBench hot-run total on c7a.metal-48xl: DataFusion 54.0.0 (single Parquet file) 9.78s vs DuckDB native storage 15.70s, or vs DuckDB querying the same single Parquet file 15.28s (\~1.56x); sum of best-of-3 per query; DataFusion is faster on 36/43 queries vs DuckDB-Parquet (derived from page data). Machine-specific: on c6a.metal it is \~1.17x (14.79s vs 17.32s), and on c6a.4xlarge DataFusion is slower (45.57s vs DuckDB 26.25s). |
| **Workload** | ClickBench (43 queries, 100M-row hits table, Parquet single-file) run head-to-head on the same AWS instance type as part of ClickHouse's public ClickBench suite. |
| **Metric** | throughput |
| **Hardware** | AWS c7a.metal-48xl (AMD EPYC 9R14, 192 vCPU) - ClickBench standard hardware; CPU model implied by instance type, not stated verbatim on the results page |
| **Compiler and flags** | DataFusion: datafusion-cli 54.0.0 built from source with cargo build --release, CARGO_PROFILE_RELEASE_LTO=true and RUSTFLAGS='-C codegen-units=1'; rustc is whatever stable version rustup installs (not pinned) (ClickBench datafusion/install). DuckDB: official prebuilt CLI from install.duckdb.org; version and flags not stated. |
| **Adoption** | 9.4k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/apache/datafusion) · [benchmark](<https://github.com/ClickHouse/ClickBench (data.generated.js: datafusion/results/20260820/c7a.metal-48xl.json vs duckdb/results/20260511/c7a.metal-48xl.json)>) |

## Verdict

ClickBench ran its 43 queries over the 100M-row hits table as a single Parquet file on AWS c7a.metal-48xl (AMD EPYC 9R14, 192 vCPU, implied by the instance type), comparing datafusion-cli 54.0.0 (built with LTO, codegen-units=1 and an unpinned stable rustc; run 2026-08-20) with DuckDB's prebuilt CLI (version not recorded; run 2026-05-11). Summed best-of-3 hot times were 9.78s for DataFusion against 15.28s for DuckDB on the same file (1.56x; geometric mean per query 1.78x) and 15.70s for DuckDB's native format. That result reverses on cold runs and on the 16-vCPU c6a.4xlarge. Per ClickBench's harness, datafusion-cli is single-user only, so the concurrency test was skipped, and DataFusion's own 55.0 release notes say ClickBench files have no page index and only integer and string columns.

## Use it when

- You are building a database, query service, SQL front end or data pipeline in Rust and want a complete planner, optimizer and executor that you extend through traits (TableProvider, UDFs, optimizer rules, custom ExecutionPlans) instead of writing your own.
- Repeated analytical queries over Parquet files in place on machines with many cores. On c7a.metal-48xl (192 vCPU), the ClickBench hot-run total was 9.78s against 15.28s for DuckDB on the same file, DataFusion won 36 of 43 queries, and on the 100-file partitioned layout it was 7.42s against 14.72s.
- Aggregation-heavy dashboards with high-cardinality or multi-column GROUP BY, and ORDER BY ... LIMIT (TopK) queries. Its largest ClickBench gains are on these: Q32 (GROUP BY WatchID, ClientIP) took 0.54s against 1.42s for DuckDB.
- Arrow-native systems that want to pass RecordBatches in and out without conversion, including Python via datafusion-python, or Spark offload via Comet.

## Skip it when

- Small or mid-size machines. On c6a.4xlarge (16 vCPU, 32 GB) the hot total is 45.57s, against 32.48s for DuckDB on the same Parquet file and 26.25s for DuckDB native storage. DataFusion wins 13 of 43 queries against the first and 5 of 43 against the second, and the partitioned layout is also slower (41.87s vs 30.95s).
- Cold or one-shot queries over files that are not in cache. Even on c7a.metal-48xl the first-run sum is 173.8s, against 122.4s for DuckDB on Parquet, and 55.9s of it is Q23 alone.
- You want a self-contained database file with its own storage, like DuckDB's .duckdb. DataFusion only reads files or whatever your TableProvider supplies (ClickBench tags it 'stateless').
- Correlated subqueries you cannot test yourself. September 2026 brought a batch of open wrong-result bugs: NOT IN ignoring NULLs (#25347, #25473, #25474), EXISTS with OFFSET (#25283), and correlation lost or misplaced (#25480, #25507, #24960).
- Teams that need a stable library API. A major release ships every 2-3 months (52 in January, 53 in March, 54 in June, 55 in August 2026), each with breaking changes (the 55.0.0 upgrade guide lists about 28), and 55.0.0 raised the MSRV from 1.88 to 1.94.

## How it is fast

Execution is vectorized over Arrow columnar batches (8,192 rows by default) using arrow-rs kernels. Each plan is split into target_partitions streams (one per core by default), connected by Volcano-style exchange operators (RepartitionExec) and run on Tokio's work-stealing thread pool with cooperative yielding. The Parquet reader pushes projections and limits down, prunes with row-group statistics, the page index and bloom filters, and answers COUNT(\*)/MIN/MAX from exact file statistics without scanning (the AggregateStatistics rule). This is why ClickBench Q0 and Q6 take 1 ms hot. Strings use Arrow StringView (German-style strings) to avoid copies, and hash aggregation is two-phase with a runtime switch that skips the partial phase once groups exceed 80% of input rows. Multi-column GROUP BY keys are stored column-wise (GroupValuesColumn), so each value is copied once, and TopK, join and aggregate operators push dynamic filters down into the scan.

## Compared with alternatives

Databend is essentially tied on the same c7a.metal-48xl ClickBench run (9.91s vs 9.78s) but is a full warehouse server with its own storage. Velox is a C++ execution library with no SQL parser or optimizer, and chDB is embedded ClickHouse for Python. Pick DataFusion when you want to embed and customize a complete SQL engine (parser, optimizer and executor) in a Rust or Arrow-native system.

## Integration

| | |
|---|---|
| **Form** | crate (datafusion on crates.io, a workspace of about 40 sub-crates); also the datafusion-cli binary and Python/Java bindings |
| **Dependencies** | arrow-rs and parquet 60.x, object_store 0.14, sqlparser 0.63, tokio 1.52 (an async runtime is required), futures. Default features pull in compression codecs (xz2, bzip2, flate2, zstd), crypto, regex and unicode function crates; optional features add avro, backtrace, parquet_encryption and serde. |
| **Minimum toolchain** | Rust 1.94.0 for 55.x (rust-version in Cargo.toml); 54.x, the version benchmarked, needs 1.88.0 |
| **Platforms** | Pure Rust. CI runs the full suite only on Linux x86-64; macOS aarch64 CI covers only the FFI crate, and Windows CI has been commented out since issue #13726 because builds were too slow. wasm32-unknown-unknown builds are tested with wasm-pack. ClickBench's harness also lists an ARM64 instance (c8g.4xlarge). |
| **Thread safety** | SessionContext is Clone and wraps Arc&lt;RwLock&lt;SessionState&gt;&gt;, and a test shares it across threads for concurrent planning. Plans run as Send async streams on a Tokio runtime. By default CPU work and I/O share one runtime, and the docs recommend separate runtimes for network sources such as S3 under load. |
| **Drop-in for the baseline** | partial — it does the same job as DuckDB for SQL over Parquet, CSV and JSON files from a CLI, Python or an embedded library, but its API, dialect and file format are different. The dialect is Postgres-like, unquoted identifiers are lowercased, some function names differ (to_timestamp_seconds), and it cannot open DuckDB database files. |

## Gotchas

- Parquet late materialization (pushdown_filters) is still off by default; issue #3463 has been open since 2022. A 'SELECT \* ... WHERE URL LIKE ... ORDER BY ... LIMIT 10' query therefore decodes all 105 columns: issue #23263 measured 97M rows and 137.8 GB decoded. That query (ClickBench Q23) takes 9.65s hot on c6a.4xlarge against 0.43s for DuckDB. Turning pushdown on can also slow other queries (#22883), so benchmark both settings.
- Unquoted identifiers are lowercased, so mixed-case Parquet columns must be double-quoted. Some legacy Parquet writers do not flag strings as UTF-8, and those columns come back as Binary unless binary_as_string is set. ClickBench's harness sets it and also casts the UInt16 EventDate column to DATE through a view.
- Memory is unbounded by default (runtime.memory_limit is NULL), and operators spill only once you configure a limit. With FairSpillPool the memory is split evenly across partitions, so a high target_partitions makes spilling more frequent.
- Q0 and Q6 run in 1 ms because they are answered from Parquet metadata and statistics. That shortcut accounts for 2 of the 36 per-query wins but almost none of the total time.

## Known shortcomings

- The 9.78 s vs 15.70 s holds on c7a only; vs DuckDB on the same Parquet file it is 15.28 s (\~1.56x). DuckDB wins on c6a.4xlarge (26.3 s vs 45.6 s) and on cold runs.
- On ClickBench c6a.4xlarge (16 vCPU) it loses: 45.57 s vs DuckDB 32.48 s on the same Parquet (26.25 s native), winning 13/43 and 5/43 queries; cold runs lose even on c7a (173.8 s vs 122.4 s). Q23 is pathological because late materialization is off by default (#3463; 9.65 s vs 0.43 s). Open wrong-result bugs for correlated NOT IN/EXISTS subqueries (2026-09; 393 open bugs); API breaks every major (\~2-3 months); no default memory limit; Windows CI off.

## Caveats and trade-offs

The ratio is our derivation from separate ClickBench result files (DataFusion 2026-08-20, DuckDB 2026-05-11), not a single stated figure. The record's 15.70s DuckDB figure is DuckDB's native storage format, while DataFusion reads Parquet; the like-for-like DuckDB-on-single-Parquet run is 15.28s (still \~1.56x). The win only shows on hot runs and many-core machines. Cold-run (first-run) sums favour DuckDB even on c7a.metal-48xl: 173.8s for DataFusion vs 162.8s for DuckDB native and 122.4s for DuckDB-Parquet. On ClickBench's c6a.4xlarge (16 vCPU), DataFusion is \~1.7x slower than DuckDB in total and wins only 5/43 queries. No CPU model is stated, and no compiler or flags are given for DuckDB.

Rust ecosystem, not a drop-in SQL client for existing DuckDB/ClickHouse users; embeddable query engine rather than a full DBMS; result run dates for DataFusion (2026-08-20) and DuckDB (2026-05-11) are not the same day, so versions differ slightly.

## Maintenance

Very active Apache-2.0 project: commits daily (last 2026-09-26), 55.1.0 published 2026-09-11, about 9.4k stars, 175 contributors to 55.0, about 2,300 open issues and PRs (393 open bugs), and no published security advisories. It is easy to adopt through cargo, Homebrew or pip, but pin the major version, because each one ships breaking API changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** ClickBench is a well-known independent public suite. Its harness (ClickHouse/ClickBench datafusion/, duckdb/, duckdb-parquet/, lib/benchmark-common.sh) runs DataFusion and DuckDB on the same c7a.metal-48xl, and the raw result JSONs re-derive to exactly 9.78s vs 15.70s hot-run sums. It is not A: the harness states DataFusion's build flags but no CPU model, no rustc version and nothing about DuckDB's build.
- **Verifier notes:** All three sums re-derive exactly from the raw ClickBench JSONs. The claim is accurate as scoped to c7a.metal-48xl, but the original caveat badly understated the reversal: DuckDB wins on the smaller c6a.4xlarge and on cold runs. I added the DataFusion build flags from ClickBench's install script.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/install>
  - <https://github.com/apache/datafusion>
- **Sources the enricher read:**
  - <https://github.com/apache/datafusion>
  - <https://github.com/apache/datafusion/blob/main/Cargo.toml>
  - <https://github.com/apache/datafusion/blob/main/datafusion/core/src/lib.rs>
  - <https://github.com/apache/datafusion/blob/main/datafusion/core/src/execution/context/mod.rs>
  - <https://github.com/apache/datafusion/blob/main/datafusion/physical-optimizer/src/aggregate_statistics.rs>
  - <https://github.com/apache/datafusion/blob/main/docs/source/user-guide/configs.md>
  - <https://github.com/apache/datafusion/blob/main/docs/source/user-guide/cli/installation.md>
  - <https://github.com/apache/datafusion/blob/main/docs/source/library-user-guide/upgrading/55.0.0.md>
  - <https://github.com/apache/datafusion/blob/main/.github/workflows/rust.yml>
  - <https://github.com/apache/datafusion/issues/3463>
  - <https://github.com/apache/datafusion/issues/22883>
  - <https://github.com/apache/datafusion/issues/15177>
  - <https://github.com/apache/datafusion/issues/23263>
  - <https://github.com/apache/datafusion/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/apache/datafusion/issues?q=is%3Aopen+%22wrong+results%22>
  - <https://github.com/apache/datafusion/issues?q=%22ClickBench+Q23%22>
  - <https://github.com/apache/datafusion/security/advisories>
  - https://api.osv.dev/v1/query (crates.io/datafusion)
  - <https://crates.io/api/v1/crates/datafusion>
  - <https://github.com/apache/datafusion-site/blob/main/content/blog/2024-11-18-datafusion-fastest-single-node-parquet-clickbench.md>
  - <https://github.com/apache/datafusion-site/blob/main/content/blog/2026-08-25-datafusion-55.0.0.md>
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/create.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/queries.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion-partitioned/results/20260820/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion-partitioned/results/20260820/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet-partitioned/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet-partitioned/results/20260511/c6a.4xlarge.json>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/apache/datafusion`) · [data/wave6/enrich/raw/github_com_apache_datafusion.json](../../../data/wave6/enrich/raw/github_com_apache_datafusion.json) (enrichment confidence 0.8)

</details>
