# Hydra Columnar (Postgres columnar extension)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `AGPL-3.0 (the columnar engine in columnar/, per README and columnar/LICENSE) + Apache-2.0 (the rest of the repo; GitHub reports Apache-2.0 from the root LICENSE)` · 🟡 stale

> Postgres table-access-method extension (Citus Columnar fork) adding compressed columnar storage, parallel scans, vectorized filters; \~23x vs heap on ClickBench.

| | |
|---|---|
| **Beats** | PostgreSQL (native heap/row storage) |
| **Claimed result** | The README chart 'Query Speed, X Faster than Postgres' puts Hydra at about 23x vanilla PostgreSQL. This is read off an unlabelled bar on a 0-25 axis; the same chart shows TimescaleDB \~10x, Citus Columnar \~4x and AWS Aurora \~2x. A second README chart (c6a.4xlarge, seconds) labels three ClickBench queries, Postgres vs Hydra: Count (Q0) 282.02s vs 0.55s, Sum (Q2) 263.07s vs 0.93s, Filtered count (Q1) 254.24s vs 0.18s. That is about 513x, 283x and 1412x (derived from page data). In the ClickBench raw results on c6a.4xlarge, Hydra 2022-12-09 vs PostgreSQL 2022-07-01 gives a geometric mean of \~23x, and Hydra 2023-09-19 gives \~25x, faster on all 43 queries (derived from ClickBench data). Against ClickBench's newer PostgreSQL 2025-02-26 result, the geometric mean is \~1.0x and Hydra 2023 is slower on 19 of 43 queries (derived from ClickBench data). |
| **Workload** | ClickBench queries over the 100M-row hits dataset on AWS c6a.4xlarge, comparing Hydra columnar tables with vanilla PostgreSQL heap tables (README charts). The README says 42 queries; the ClickBench result files hold 43. The clickbench-100M and warehouse-10G suites in BENCHMARKS.md only track Hydra's own query times across releases and commits on Bencher. |
| **Metric** | throughput |
| **Hardware** | AWS c6a.4xlarge (16 vCPU, 32 GiB RAM) with 500 GiB GP2 storage for release benchmarks; GitHub-hosted 4-core runners for continuous benchmarks |
| **Adoption** | 3043 stars |
| **Last commit** | 2025-02-10 |
| **Links** | [repository](https://github.com/hydradatabase/columnar) · [benchmark](https://github.com/hydradatabase/columnar/blob/main/README.md) |

## Verdict

The benchmark is ClickBench on the 100M-row hits table on AWS c6a.4xlarge (16 vCPU, 32 GB, 500 GB gp2), with no compiler or flags stated. The README chart puts Hydra about 23x ahead of stock PostgreSQL heap overall, and three labelled queries go from 282.02 s to 0.55 s (COUNT), 263.07 s to 0.93 s (SUM/AVG) and 254.24 s to 0.18 s (filtered COUNT). ClickBench's raw files give roughly 25x geometric mean for Hydra 2023-09-19 over the 2022-07-01 PostgreSQL run (faster on all 43 queries). Against the newer 2025-02-26 PostgreSQL run the result is roughly parity on ClickBench's +10 ms geometric mean: Hydra is slower on 19 of 43 queries, though its summed hot time of about 479 s is still about 7.7x lower than PostgreSQL's 3,675 s (derived).

## Use it when

- You already run PostgreSQL 13-16 and have append-mostly event, log or clickstream tables of tens to hundreds of millions of rows, queried by dashboards with COUNT/SUM/AVG and simple column-vs-constant filters.
- Wide, denormalized tables where queries touch only a few columns, so projection pushdown and chunk-group min/max skipping avoid most of the I/O.
- You must keep analytics inside the same Postgres as the OLTP heap tables (same SQL, transactions, joins, pg_dump) rather than run a separate engine. A common layout is a partitioned table with heap partitions for recent, hot data and columnar partitions for older data.
- Cutting disk footprint of cold data with zstd-compressed columnar storage: the inherited Citus microbenchmark reports 5.4x smaller than heap on a contrived dataset.
- Self-hosted analytics replica or sandbox where you can pin to the last release (v1.1.2) and accept an unmaintained engine.

## Skip it when

- Point lookups and 'find by ID' queries, small latency-sensitive transactions, or frequent large UPDATEs. The project FAQ says these are slower than on heap. UPDATE is implemented as delete plus re-insert, and UPDATE/DELETE lock the table, so they run one at a time.
- Trickle ingestion (a few rows per transaction). Each insert transaction writes a new stripe, so you end up with many tiny stripes (issue #239), and planning time grows linearly with stripe count (#188) unless you run columnar.vacuum regularly.
- You need PostgreSQL 17+ (configure accepts only 13-16), logical replication, foreign keys, or Citus installed in the same cluster (package file conflicts, #154).
- High-concurrency analytics. Queries fan out to parallel workers (columnar.min_parallel_processes defaults to 8), and the FAQ warns that this limits concurrent queries.
- Anything needing an active upstream. There have been no code commits since 2024-10. An open wrong-results bug (#282: columnar table returns no or incorrect rows when filtered by values from a joined heap table) and a read error (#247) have no fix, and issue comments say the team moved on to pg_duckdb.

## How it is fast

Storage comes from Citus Columnar. Rows are written in stripes of up to 150k rows, and each stripe is split into chunk groups of 10k rows. Each column is stored separately and compressed with zstd by default (lz4 and pglz are also available). Only the projected columns are read, and per-chunk min/max 'skip lists' let WHERE clauses skip whole chunk groups. Hydra adds a parallel-aware CustomScan in which worker processes claim whole stripes through an atomic fetch-and-add counter in dynamic shared memory. It also adds vectorized execution: batches of up to 10,000 column values go through typed comparison functions for column-vs-constant predicates, and there are vectorized COUNT/SUM/AVG aggregates (PG14+). These are plain C loops with no explicit SIMD intrinsics. An optional per-backend cache of decompressed chunks also exists (off by default).

## Compared with alternatives

Pick it over DataFusion, Databend or chDB when the data must stay inside a running Postgres (same transactions, joins with heap tables, existing tooling) and you only need a few-to-25x speedup on scan-and-aggregate queries. If you can move analytics to a separate engine, those siblings are actively maintained, purpose-built columnar engines. Their catalogued ClickBench totals are single-digit to tens of seconds, though on larger hardware, whereas Hydra totals about 479 s on c6a.4xlarge.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | PostgreSQL 13-16 server with PGXS dev headers, liblz4 and libzstd (both on by default; --without-lz4/--without-zstd). configure also requires libcurl by default, left over from Citus's anonymous-statistics option; no columnar C source uses it, and --without-libcurl turns the check off. safestringlib is vendored. |
| **Minimum toolchain** | Autoconf plus the C compiler PostgreSQL was built with (pg_config --cc); the builder image is Ubuntu 22.04 with gcc. PostgreSQL 13, 14, 15 or 16 only. Vectorized aggregates need PG14+. |
| **Platforms** | Linux. The Docker images are built for linux/amd64 and linux/arm64. The code uses no explicit SIMD intrinsics; macOS and Windows builds are not documented. |
| **Thread safety** | Uses the Postgres process model with no threads. Intra-query parallelism uses parallel worker processes that coordinate through a shared-memory atomic stripe counter. The column cache is per-backend memory. UPDATE/DELETE take a table lock, so concurrent writers serialize. Hydra's docs recommend REPEATABLE READ for stronger isolation; the inherited Citus README lists SERIALIZABLE as unsupported. |
| **Drop-in for the baseline** | partial — same SQL and access-method API: switch a table with USING columnar or alter_table_set_access_method, and the Docker image replaces the postgres image. But only columnar tables get faster. Logical replication, foreign keys and some index or constraint types are unsupported, and write-heavy or point-lookup workloads get slower. |

## Gotchas

- The Docker image makes columnar the database-wide default table access method, so lookup and reference tables silently become columnar and slow unless created USING heap. With that default, a large INSERT ... SELECT or CREATE TABLE can still fail with a parallel-operation error (#267, open).
- Stripes are fixed at write time. The chunk_group_row_limit and stripe_row_limit options apply only to newly written data. Small transactions fragment the table, and columnar.vacuum reportedly fails to release space from fully deleted stripes (#285). One corrupted stripe raises an error that aborts reads, VACUUM and index builds for the whole table (#284).
- Vectorization only fires for column-vs-constant comparisons on basic types (int2/4/8, char, date, time, timestamp[tz]). An OR with any non-vectorizable branch disables it for that branch, and FILTER aggregates are not vectorized. -O3 is opt-in (make COLUMNAR_O3=1) in the current Makefile, and the in-tree src/backend/columnar/README.md is the stale Citus text ('append-only', 'no parallel scans').
- The extension is named `columnar`, the same name as Citus Columnar. The two cannot be installed side by side, and there is no supported physical migration from Citus Columnar (#154). The planner may also skip useful indexes on columnar tables; the maintainers suggest pg_hint_plan (#155).

## Known shortcomings

- The \~23x vs Postgres comes from README charts and a 2022 ClickBench run; against the 2025 ClickBench Postgres run it is \~1.0x geomean (slower on 19 of 43 queries). A fork of Citus Columnar; the engine is AGPL-3.0; stale.
- Stale: no code commits since 2024-10 (last release v1.1.2, 2024-04), PG 13-16 only, and the team moved to pg_duckdb. Open bugs: wrong/no rows when filtered by a joined heap table (#282), one bad stripe blocks reading the whole table (#284), parallel CREATE TABLE error (#267), vacuum leaves deleted stripes' space (#285). The Docker image makes every table columnar; small inserts create tiny stripes and planning slows; updates are slow and lock the table; the 'columnar' extension name clashes with Citus (#154).

## Caveats and trade-offs

BENCHMARKS.md, the original benchmark_url, has no Postgres comparison: it only tracks Hydra's own timings through Bencher images. The Postgres win appears only in first-party README chart images, with no compiler or flags and no CPU model beyond c6a.4xlarge. Per-query README ratios exceed 50x. The \~23x aggregate matches ClickBench against its 2022 PostgreSQL run, but ClickBench's 2025-02-26 PostgreSQL result is roughly at parity with Hydra 2023 (geometric mean \~1.0, Hydra slower on 19 of 43 queries; derived). The current ClickBench 'hydra' entry (2025-03-04) is Hydra's serverless OLAP service, not this extension. The columnar engine is AGPL-3.0 (copyleft), and the code is a fork of Citus Columnar. The last commit was 2025-02-10, so the repo is stale.

It is a Postgres extension, not a standalone embeddable library; speed gains apply only to tables explicitly created with Hydra's columnar access method, not to Postgres workloads generally. The project (originally 'hydradatabase/hydra') has since been renamed/consolidated into 'hydradatabase/columnar' with no commits in over a year.

## Maintenance

Stale and effectively abandoned. The last code change was 2024-10-07, the last commit (README) 2025-02-10 and the last release v1.1.2 (2024-04-01), with no PG17 support and open correctness bugs. The engine under columnar/ is AGPL-3.0, whose network-use copyleft matters for hosted products, and the rest of the repo is Apache-2.0. It is buildable from source or usable via the published Docker images.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Postgres comparison exists only as first-party README chart images: roughly 23x in 'Query Speed, X Faster than Postgres', plus three labelled ClickBench queries. Hardware is c6a.4xlarge with no CPU model, and no compiler or flags are given. The per-query gains are over 50x (about 283-1412x, derived) with flags unstated, which keeps it capped at C. ClickBench raw results corroborate the win against the 2022 PostgreSQL run but show parity against the 2025 run, so this was not upgraded to B.
- **Verifier notes:** The record's benchmark_url, BENCHMARKS.md, only charts Hydra's own timings; the Postgres comparison lives in the README charts, so the URL was repointed. hydradatabase/hydra now redirects to hydradatabase/columnar. Stars (3043), last commit 2025-02-10 (stale), not archived and not a GitHub fork were all verified. The license was misreported as plain Apache-2.0; the engine itself is AGPL-3.0, which is still OSI-approved, so usability stays copyable.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `license`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hydradatabase/columnar>
  - <https://github.com/hydradatabase/hydra>
  - <https://raw.githubusercontent.com/hydradatabase/hydra/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/README.md>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/.images/FasterthanPG.png>
  - <https://raw.githubusercontent.com/hydradatabase/hydra/main/.images/ReadmeBenchmarks.png>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/columnar/LICENSE>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/LICENSE>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/columnar/README.md>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/columnar/NOTICE>
  - <https://github.com/hydradatabase/benchmarks>
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/hydra/results/20221209/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/hydra/results/20230919/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/postgresql/results/20220701/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/postgresql/results/20250226/c6a.4xlarge.json>
- **Sources the enricher read:**
  - <https://github.com/hydradatabase/columnar>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/README.md>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/README.md>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/README.md>
  - <https://github.com/hydradatabase/columnar/blob/main/CHANGELOG.md>
  - <https://github.com/hydradatabase/columnar/blob/main/DEVELOPERS.md>
  - <https://github.com/hydradatabase/columnar/blob/main/BENCHMARKS.md>
  - <https://github.com/hydradatabase/columnar/blob/main/Dockerfile>
  - <https://github.com/hydradatabase/columnar/blob/main/Makefile>
  - <https://github.com/hydradatabase/columnar/blob/main/docker-bake.hcl>
  - <https://github.com/hydradatabase/columnar/blob/main/.github/workflows/ci.yaml>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/Dockerfile>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/configure.in>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/Makefile.global.in>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/Makefile>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar.control>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/mod.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar_customscan.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar_reader.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar_cache.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar_compression.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/columnar_tableam.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/vectorization/columnar_vector_execution.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/vectorization/types/int.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/backend/columnar/vectorization/types/aggregates.c>
  - <https://github.com/hydradatabase/columnar/blob/main/columnar/src/include/columnar/vectorization/columnar_vector_types.h>
  - <https://github.com/hydradatabase/columnar/blob/main/files/postgres/docker-entrypoint-initdb.d/columnar.sh>
  - <https://github.com/hydradatabase/columnar/blob/main/files/postgres/postgresql.conf>
  - <https://github.com/hydradatabase/columnar/blob/main/third-party/pgxman/pgxman_16.yaml>
  - <https://raw.githubusercontent.com/hydradatabase/columnar/main/.images/FasterthanPG.png>
  - <https://raw.githubusercontent.com/hydradatabase/hydra/main/.images/ReadmeBenchmarks.png>
  - <https://github.com/hydradatabase/columnar/issues>
  - <https://github.com/hydradatabase/columnar/issues/154>
  - <https://github.com/hydradatabase/columnar/issues/155>
  - <https://github.com/hydradatabase/columnar/issues/188>
  - <https://github.com/hydradatabase/columnar/issues/219>
  - <https://github.com/hydradatabase/columnar/issues/239>
  - <https://github.com/hydradatabase/columnar/issues/247>
  - <https://github.com/hydradatabase/columnar/issues/267>
  - <https://github.com/hydradatabase/columnar/issues/281>
  - <https://github.com/hydradatabase/columnar/issues/282>
  - <https://github.com/hydradatabase/columnar/issues/284>
  - <https://github.com/hydradatabase/columnar/issues/285>
  - <https://github.com/hydradatabase/columnar/releases>
  - <https://web.archive.org/web/2023id_/https://blog.hydra.so/blog/2022-12-13-how-we-built-fastest-postgres-db-for-analytics>
  - <https://web.archive.org/web/2024id_/https://columnar.docs.hydra.so/concepts/faqs>
  - <https://web.archive.org/web/2024id_/https://columnar.docs.hydra.so/concepts/updates-and-deletes>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/hydra/results/20221209/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/hydra/results/20230919/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/postgresql/results/20220701/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/postgresql/results/20250226/c6a.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/tree/main/postgresql>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/hydradatabase/columnar`) · [data/wave6/enrich/raw/github_com_hydradatabase_columnar.json](../../../data/wave6/enrich/raw/github_com_hydradatabase_columnar.json) (enrichment confidence 0.7)

</details>
