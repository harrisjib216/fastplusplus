# Databend

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Rust` · `Apache-2.0 (core) + Elastic-2.0 (enterprise code: src/query/ee, src/meta/ee, src/bendsave, ee_main.rs binaries), per the repo LICENSE file` · 🟢 active

> Rust SQL data warehouse over object storage; \~1.6x faster than DuckDB on ClickBench hot runs on 192-vCPU hardware.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | \~1.6x faster than DuckDB on ClickBench hot-run total on c7a.metal-48xl: Databend 9.91s vs DuckDB native storage 15.70s (vs DuckDB on single Parquet 15.28s); sum of best-of-3 per query; Databend is faster on 35/43 queries, \~1.75x by geometric mean (derived from page data). Also \~1.63x on c6a.metal (10.65s vs 17.32s). On c6a.4xlarge Databend is slower in total (41.93s vs 26.25s), with roughly equal geomean. |
| **Workload** | ClickBench (43 queries, 100M-row hits table) run head-to-head on the same AWS instance type as part of ClickHouse's public ClickBench suite. |
| **Metric** | throughput |
| **Hardware** | AWS c7a.metal-48xl (AMD EPYC 9R14, 192 vCPU) - ClickBench standard hardware |
| **Compiler and flags** | Databend: prebuilt release binary databend-v0.9.53-nightly (x86_64-unknown-linux-musl) downloaded by ClickBench databend/install. DuckDB: official prebuilt CLI from install.duckdb.org. No compiler or flags stated for either. |
| **Adoption** | 9.5k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/databendlabs/databend) · [benchmark](<https://github.com/ClickHouse/ClickBench (data.generated.js: databend/results/20260926/c7a.metal-48xl.json vs duckdb/results/20260511/c7a.metal-48xl.json)>) |

## Verdict

ClickBench runs 43 queries on the 100M-row hits table, both engines on the same AWS c7a.metal-48xl (AMD EPYC 9R14, 192 vCPU). Databend v0.9.53-nightly (a prebuilt musl binary from Feb 2023, run 2026-09-26) sums best-of-3 per query to 9.91s, against 15.70s for the official prebuilt DuckDB CLI on its native .db file (run 2026-05-11, version not recorded): \~1.6x, faster on 35/43 queries, \~1.75x geomean using ClickBench's +10ms shift. c6a.metal looks similar (10.65s vs 17.32s), but c6a.4xlarge reverses (41.93s vs 26.25s), cold sums favour DuckDB everywhere, and neither side states compiler or flags.

## Use it when

- You want a shared, multi-user SQL warehouse over S3/GCS/Azure, with storage separate from compute, rather than an in-process library.
- Repeated (hot) analytic queries on very large machines: ClickBench hot totals beat DuckDB \~1.6x on c7a.metal-48xl (192 vCPU) and c6a.metal.
- Selective queries on large fact tables: point lookups on high-cardinality columns (bloom index), tenant/date range filters that match a CLUSTER BY key, and top-N ORDER BY ... LIMIT.
- You need concurrent query serving from one process: ClickBench's concurrent test recorded 11.99 QPS over 10 connections with 0 errors (DuckDB's CLI entry skips this test).
- You want Snowflake-style features self-hosted: snapshot-based time travel, stages/COPY loading, and external Parquet/ORC/Iceberg/Paimon tables (the repo has storage crates for each).

## Skip it when

- Mid-size machines: on c6a.4xlarge (16 vCPU) Databend's hot total is 41.93s vs DuckDB's 26.25s, and 9 queries are more than 1.5x slower (for example the REGEXP_REPLACE query Q29: 11.9s vs 6.5s).
- Cold or first-touch queries: DuckDB wins the cold-run sums on every machine checked (162.8s vs 184.9s on c7a.metal-48xl, 115.2s vs 182.7s on c6a.4xlarge).
- Embedded analytics inside a C/C++/Rust app or notebook where DuckDB's library and extension ecosystem is the point. Databend only embeds via Python, and the full product needs two daemons.
- Joins or NOT IN subqueries that spill under memory pressure. Open bugs as of Sept 2026: #20512 (a spilling hash join fails once max_hash_join_spill_level &gt;= 2), #20511 (NOT IN returns rows when a NULL is present and the mark join spills) and #20568 (duplicate rows from predicate pushdown into a RIGHT JOIN anti-join). There are 45 open C-bug issues.
- You need everything under an OSI license: VACUUM, streams, materialized views, data masking, row access policies, storage encryption, attach table and workload groups are enterprise features that need a license key and fall under the Elastic-2.0 code paths.

## How it is fast

Fuse storage prunes before reading. A snapshot points to segments, segments point to Parquet blocks, and multi-level min/max statistics prune segments and then blocks; per-block bloom indexes (xor8 by default, binary fuse32 as an option, from the xorf crate) skip blocks on equality predicates, and CLUSTER BY keys keep data sorted so range filters touch few blocks. Execution is a multi-threaded processor-graph pipeline (processors signal NeedData, NeedConsume, Sync or Async events to an executor), with GROUP BY and joins on a linear-probing hash table ported from ClickHouse's C++ implementation. On ClickBench the biggest gaps over DuckDB (5-9x on Q20-Q22 and Q28, 3-5x on the ORDER BY ... LIMIT queries Q24-Q27) are on point-lookup, LIKE and top-N queries, which fits pruning; that link is my inference. The heavy GROUP BY queries are close to even.

## Compared with alternatives

Apache DataFusion shows the same \~1.6x over DuckDB on ClickBench c7a.metal-48xl, but it is an embeddable Apache-2.0 Rust library for building an engine. Pick Databend when you want a finished multi-user warehouse on object storage with time travel. For in-app embedding, DataFusion or chDB fit better, and Doris or StarRocks are the MPP-warehouse alternatives whose catalogued evidence is against ClickHouse, not DuckDB.

## Integration

| | |
|---|---|
| **Form** | server binaries (databend-query + databend-meta) as tarballs, .deb packages or a Docker image; Python wheel for embedded local mode |
| **Dependencies** | At runtime, the databend-meta service plus object storage (S3/Azure/GCS) or a local fs. Building from source needs nightly Rust, build-essential, OpenSSL, protobuf, clang/LLVM and Python 3 (scripts/setup/dev_setup.sh). |
| **Minimum toolchain** | Rust nightly (rust-toolchain.toml pins nightly-2026-08-28); local mode needs Python 3.12 or 3.13 with databend-driver &gt;= 0.34.0 |
| **Platforms** | Linux x86-64 and aarch64 (gnu tarballs and .deb in v1.2.948-nightly). The README badge says Linux, macOS and ARM, but no macOS binaries are among the release assets. |
| **Thread safety** | Multi-session server that runs concurrent queries (ClickBench: 11.99 QPS at 10 connections, 0% errors on c7a.metal-48xl). Thread safety of the Python local mode is not documented. |
| **Drop-in for the baseline** | false — different deployment model (a client/server HTTP service instead of DuckDB's in-process library), a different SQL dialect, and data must be loaded into Fuse tables or read from stages/external files |

## Gotchas

- The ClickBench result comes from v0.9.53-nightly (Feb 2023), which ClickBench's install script pins. Current v1.2.9xx builds are not in that comparison, so today's numbers could be higher or lower.
- The benchmark setups differ. Databend is a long-lived server that keeps its in-process caches between the 3 tries, and its hits table is CLUSTER BY (CounterID, EventDate, UserID, EventTime, WatchID). DuckDB's entry starts a fresh `duckdb hits.db` process for every try (BENCH_RESTARTABLE=no), so its hot runs only get a warm OS page cache, and its table has no sort key. Against that, Databend's times include a curl HTTP round-trip.
- Releases are almost all -nightly tags (about daily). The last non-nightly release is v1.2.881 (2026-04-17), so pin exact versions.
- Changing bloom_index_type with ALTER TABLE affects only new writes, so old and new filter types coexist until the data is rewritten. binary_fuse32 is about 4x larger than xor8.

## Known shortcomings

- ClickBench still pins a v0.9.53-nightly build from 2023-02; loses on c6a.4xlarge and on cold runs. Enterprise directories are Elastic-2.0 (mixed license).
- ClickBench pins v0.9.53-nightly (2023-02); current v1.2.x was never tested vs DuckDB. Setups are unequal (the Databend daemon keeps caches across tries and the table is CLUSTER BY sorted, while DuckDB runs a fresh CLI per try on an unsorted table); the 1.75x geomean includes ClickBench's +10 ms shift. Open wrong-result/spill bugs (#20512, #20511, #20568); VACUUM, streams, MVs, masking and encryption are Elastic-2.0 licensed features; nightly-only releases, Linux binaries only.

## Caveats and trade-offs

ClickBench's Databend entry pins databend v0.9.53-nightly, released 2023-02-26, even for the 2026-09-26 run, so the number reflects a \~3.5-year-old build, not current v1.2.x. Run dates differ (Databend 2026-09-26 vs DuckDB 2026-05-11). The win only shows on hot runs on large machines. Cold-run sums favour DuckDB (184.9s vs 162.8s on c7a.metal-48xl), and on c6a.4xlarge Databend loses in total (41.93s vs 26.25s). No compiler, flags or CPU model are published. Enterprise features are under Elastic-2.0 (non-OSI), hence usability 'mixed'. The separate Databend-vs-Snowflake TPC-H claim (baseline not in list) is weaker than the '3x' marketing headline.

Core engine is Apache-2.0 but enterprise/EE binaries (ee_main.rs paths) are under the Elastic-2.0 license, so a full build mixes licenses; separately, Databend's own marketing benchmark (docs.databend.com/guides/benchmark/tpch, Databend Cloud vs Snowflake, SF100) shows only \~1.1-1.25x on hot/cold query time despite a '3x faster' headline claim - treat the headline figure skeptically.

## Maintenance

Actively developed (default-branch commits daily, last push 2026-09-26, 9.45k stars) but shipped almost entirely as nightlies, and an Apache-2.0 core with Elastic-2.0 enterprise directories makes usability 'mixed'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** ClickBench is a well-known independent public suite. Its harness (ClickHouse/ClickBench databend/, duckdb/, lib/benchmark-common.sh) runs Databend and DuckDB on the same c7a.metal-48xl, and the raw result JSONs re-derive to exactly 9.91s vs 15.70s hot-run sums. It is not A: both engines are prebuilt binaries with no compiler or flags stated, and no CPU model is given.
- **Verifier notes:** The hot-run sums verify exactly. The notable find is that ClickBench's Databend install script pins a Feb 2023 nightly (v0.9.53), which should be a tag. GitHub reports license NOASSERTION because the LICENSE splits Apache-2.0 core from Elastic-2.0 enterprise directories, so 'mixed' usability is correct. Stars 9,452; last default-branch commit 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/load>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/install>
  - <https://github.com/databendlabs/databend>
  - <https://raw.githubusercontent.com/databendlabs/databend/main/LICENSE>
  - <https://github.com/databendlabs/databend/releases/tag/v0.9.53-nightly>
- **Sources the enricher read:**
  - <https://github.com/databendlabs/databend>
  - <https://github.com/databendlabs/databend/blob/main/README.md>
  - <https://github.com/databendlabs/databend/blob/main/LICENSE>
  - <https://github.com/databendlabs/databend/blob/main/rust-toolchain.toml>
  - <https://github.com/databendlabs/databend/blob/main/src/query/README.md>
  - <https://github.com/databendlabs/databend/blob/main/src/common/README.md>
  - <https://github.com/databendlabs/databend/blob/main/src/binaries/README.md>
  - <https://github.com/databendlabs/databend/blob/main/src/common/hashtable/src/README.md>
  - <https://github.com/databendlabs/databend/blob/main/src/query/storages/common/index/src/filters/xor8/block_filter.rs>
  - <https://github.com/databendlabs/databend/blob/main/src/query/storages/common/index/src/filters/xor8/binary_fuse32_filter.rs>
  - <https://github.com/databendlabs/databend/blob/main/src/query/storages/common/index/src/filters/mod.rs>
  - <https://github.com/databendlabs/databend/blob/main/src/query/storages/common/index/cpp/avx2.c>
  - <https://github.com/databendlabs/databend/blob/main/src/query/pipeline/src/core/processor.rs>
  - <https://github.com/databendlabs/databend/blob/main/src/common/license/src/license.rs>
  - <https://github.com/databendlabs/databend/blob/main/src/bendpy/README.md>
  - <https://github.com/databendlabs/databend/blob/main/scripts/setup/dev_setup.sh>
  - <https://github.com/databendlabs/databend/blob/main/benchmark/README.md>
  - <https://github.com/databendlabs/databend/blob/main/benchmark/hits/create_local.sql>
  - <https://github.com/databendlabs/databend/releases/tag/v1.2.948-nightly>
  - <https://github.com/databendlabs/databend/releases/tag/v0.9.53-nightly>
  - <https://github.com/databendlabs/databend/issues/20512>
  - <https://github.com/databendlabs/databend/issues/20511>
  - <https://github.com/databendlabs/databend/issues/20568>
  - <https://github.com/databendlabs/databend/issues?q=is:issue+is:open+label:C-bug>
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/load>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/create.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/queries.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/start>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/query>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/databend/results/20260926/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/query>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/create.sql>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/load>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/lib/benchmark-common.sh>
  - <https://docs.databend.com/sql/sql-reference/table-engines/fuse>
  - <https://docs.databend.com/guides/>
  - <https://docs.databend.com/guides/how-databend-works>
  - <https://docs.databend.com/guides/how-databend-works/how-databend-fuse-engine-works>
  - <https://hn.algolia.com/api/v1/search?query=databend&tags=story>
  - https://docs.databend.com/guides/products/dee/license (returned empty)
  - https://docs.databend.com/guides/overview/ (404)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/databendlabs/databend`) · [data/wave6/enrich/raw/github_com_databendlabs_databend.json](../../../data/wave6/enrich/raw/github_com_databendlabs_databend.json) (enrichment confidence 0.72)

</details>
