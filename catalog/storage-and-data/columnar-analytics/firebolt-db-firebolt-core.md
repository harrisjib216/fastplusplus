# Firebolt Core

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `Elastic License 2.0` · 🟢 active

> Firebolt's free self-hosted distributed SQL engine (ClickHouse-derived runtime); beats DuckDB on ClickBench hot runs, roughly ties ClickHouse.

| | |
|---|---|
| **Beats** | DuckDB and ClickHouse via the ClickBench leaderboard (Firebolt wins vs DuckDB on hot runs; roughly ties ClickHouse hot and trails it cold and on Combined) |
| **Claimed result** | The '#1 on ClickBench' claim is Firebolt's own launch statement (Show HN and company blog, 2025-06-25: 'instantly took the top spot'); the leaderboard does not show it today. On the current leaderboard (Firebolt rows dated 2026-08-29), all figures derived from page data: vs DuckDB (native), hot-run geomean ratio is 0.64 on c6a.4xlarge (\~1.6x faster) and 0.27-0.33 on c6a.metal, c7a.metal-48xl and c8g.metal-48xl (\~3-3.8x faster). Cold runs are 1.6-2.3x slower than DuckDB, and Combined is \~10% better on c6a.4xlarge. vs ClickHouse (2026-09-26 rows): hot is roughly parity (0.85-1.04), cold is 1.25-1.8x slower, and ClickHouse leads on Combined on every machine except c6a.large. Approximate Combined rank is \~9th of \~133 entries on c6a.4xlarge and \~6th of \~85 on c8g.4xlarge. |
| **Workload** | ClickBench (43 standard analytical SQL queries over the hits.parquet web-analytics dataset), cold and hot single-instance runs on the leaderboard's standard hardware |
| **Metric** | throughput |
| **Hardware** | ClickBench AWS instances: c6a.large/xlarge/2xlarge/4xlarge/metal (AMD EPYC, 3rd gen), c7a.metal-48xl (AMD EPYC, 4th gen), c8g.4xlarge and c8g.metal-48xl (Graviton4). Single node, 500 GB gp2 per ClickBench convention. |
| **Adoption** | 252 stars |
| **Last commit** | 2026-08-13 |
| **Links** | [repository](https://github.com/firebolt-db/firebolt-core) · [benchmark](https://benchmark.clickhouse.com/) |

## Verdict

ClickBench's 43 queries, run on single AWS instances (c6a, c7a and Graviton4 c8g families) with the hits dataset ingested into a managed table (PRIMARY INDEX CounterID, EventDate, UserID, EventTime, WatchID) and result, subresult and scan caches disabled (2026-08-29 image engine:dev, compiler and flags undisclosed). Hot runs beat native DuckDB by about 1.6x (geomean) on c6a.4xlarge (hot sums 15.6 s vs 26.3 s; ClickHouse 18.0 s) and about 3-3.8x on metal-class machines. They roughly tie ClickHouse, while cold runs trail both, so the June 2025 '#1 on ClickBench' claim no longer holds.

## Use it when

- Repeated, dashboard-style aggregations over one large fact table on a big-RAM machine where hot-cache latency matters: its ClickBench hot-run sum on c8g.metal-48xl is 2.66 s, vs 3.14 s for ClickHouse and 11.29 s for DuckDB.
- Queries that filter or join on a sort key, where the sparse primary index, data-skipping, inverted and aggregating indexes can prune most granules before any column data is read.
- You want one engine that runs as a single Docker container on a laptop and scales to a multi-node cluster with shuffle joins and distributed aggregations, all in a Postgres-style SQL dialect.
- Ad-hoc SQL over Parquet or Iceberg in S3/GCS (or S3-compatible stores such as MinIO or R2) without a separate load pipeline.
- Self-hosting inside your own product is acceptable under Elastic License 2.0, which bars only offering it as a competing hosted service.

## Skip it when

- Cold or first-touch latency matters: after a restart, each ClickBench query except Q1 took at least \~0.47 s (vs \~0.001 s minimum for ClickHouse and 0.04-0.09 s for DuckDB), which makes the cold geomean 1.6-2.3x slower than DuckDB's.
- Machines with 32 GB of RAM or less under concurrent load. In ClickBench's 10-connection concurrency test, 30% (c6a.4xlarge) and 57% (c8g.4xlarge) of queries errored, vs 0.1% for ClickHouse. 18 of 43 queries returned no result on c6a.large (4 GB) and 7 on c6a.xlarge (8 GB). The README recommends at least 16 GB.
- You need an embeddable in-process library (DuckDB, DataFusion), or you must build, audit, patch or vendor the engine: it is a closed binary under a non-OSI license.
- Write-concurrent workloads: only one write transaction can be active per engine at a time, and a second concurrent write returns an error.
- Networks you don't trust, or restricted hosts. The engine's HTTP endpoint has no built-in authentication or TLS, and a large-DDL bug (issue #59) left metadata unusable after the fix. It needs Linux 6.1+ io_uring, seccomp=unconfined and an 8 GiB memlock ulimit, and Docker Desktop for Mac 4.42.1-4.43.1 cannot run it.

## How it is fast

Per Firebolt's CDMS 2022 paper ('Assembling a Query Engine From Spare Parts'), the runtime is a hard fork of ClickHouse's vectorized execution engine. The planner, forked from HPI's Hyrise, does cost-based join reordering, and a custom shuffle-based distributed executor replaced ClickHouse's distributed layer so that large-large joins and high-cardinality GROUP BYs scale out. Managed tables are immutable tablets sorted on a PRIMARY INDEX, with a sparse index of one mark per 8,192-row granule (found by binary search), per-tablet min/max statistics, min/max data-skipping indexes, Roaring-bitmap inverted indexes and aggregating indexes, and the scan refines a selection vector one predicate at a time so wide columns are decoded only for rows that survive. I/O goes through io_uring, and tablets are cached on local SSD with prefetching; none of this can be checked in source, because only the binary is published.

## Compared with alternatives

Pick it over Apache DataFusion or Databend when you want a ready-made scale-out server with a Postgres dialect and index-driven pruning, and closed source is acceptable. Its c7a.metal-48xl hot-run sum (3.11 s, 2026-08-29) is about a third of the catalogued DataFusion (9.78 s) and Databend (9.91 s) figures for that machine, though from different run dates. Choose DataFusion if you need Apache-licensed code you can embed or modify, and note that Umbra and ClickHouse still lead it on the ClickBench Combined score.

## Integration

| | |
|---|---|
| **Form** | prebuilt server binary in a Docker image (ghcr.io/firebolt-db/engine); no library, headers or source |
| **Dependencies** | Docker Engine (plus the Compose plugin for multi-node); any HTTP client, or the fb CLI, JDBC or SQLAlchemy drivers; metadata is kept in SQLite on a single node and in PostgreSQL in cluster deployments |
| **Minimum toolchain** | not applicable (no source). Host needs Linux kernel 6.1+ for io_uring, or Docker Desktop 4.43.2+ on macOS |
| **Platforms** | amd64 with at least SSE 4.2, or arm64 (multi-arch images); Linux host (macOS via Docker Desktop with socket-on-tmpfs workaround) |
| **Thread safety** | Server process; any number of concurrent read transactions, but only one write transaction per engine at a time (concurrent writes error out) |
| **Drop-in for the baseline** | no |

## Gotchas

- Errors come back as a JSON body with an 'errors' key, even with HTTP 200. During startup the port answers 'Cluster not yet healthy' at HTTP 200, so readiness checks must inspect the result body rather than the status code.
- The response's statistics.elapsed understates query time by up to 3.6x on high-core machines, because the trailing statistics chunk is sent tens of milliseconds after the rows. ClickBench measures client wall-clock time for this reason.
- ClickBench runs with enable_result_cache, enable_subresult_cache and enable_scan_cache set to false 'so timings are real'. Set these explicitly in your own benchmarks, or repeated queries may measure cache hits.
- The HTTP protocol is stateless: the current database and explicit transactions are carried by echoing the Firebolt-Update-Parameters / Firebolt-Remove-Parameters response headers back as query-string parameters, so naive clients silently lose that state.

## Known shortcomings

- '#1 on ClickBench' is a vendor June-2025 claim that no longer holds: hot runs are \~1.6-3.8x faster than DuckDB but cold runs 1.6-2.3x slower; about parity hot vs ClickHouse and behind it cold and combined. Closed ELv2 binary (ClickBench tags it a ClickHouse derivative).
- SECURITY: the engine HTTP endpoint has no auth or TLS. Closed binary only (Docker image, ELv2, non-OSI; the repo holds deploy scripts and notices). A \~0.47 s/query cold floor (vs ClickHouse \~1 ms); on machines with 32 GB or less, ClickBench's concurrency test errors 30-57% (vs ClickHouse 0.1%) and 7-18 of 43 queries return no result on small instances. One write transaction per engine; a DoS fix (#59) left metadata broken. Needs Linux 6.1+ io_uring, seccomp=unconfined and 8 GiB memlock; releases are 'preview RC'; stats.elapsed understates by up to 3.6x; errors come back as HTTP 200.

## Caveats and trade-offs

The '#1 on ClickBench' claim is a June 2025 vendor statement; the current leaderboard shows Umbra, CedarDB, Salesforce Hyper and ClickHouse ahead on Combined. Firebolt's wins are hot-run only; its cold-run times are much worse than DuckDB's and ClickHouse's, and its data size is larger than ClickHouse's (15.8 vs \~9.5 GB). ClickBench tags the entry 'ClickHouse derivative' and 'proprietary'. The engine ships as a closed Docker image (ghcr.io/firebolt-db/engine) under Elastic License 2.0 (non-OSI), and the GitHub repo holds only deployment scripts and docs. No compiler or flags are disclosed, so the specific optimizations cannot be inspected.

Elastic License 2.0 is source-available but not OSI-approved (forbids offering it as a competing hosted service); the firebolt-core GitHub repo only contains deployment scripts, Docker/Helm configs and docs, not the query-engine source, which ships solely as a prebuilt Docker image (ghcr.io/firebolt-db/engine)

## Maintenance

Actively maintained by Firebolt (repo commits through 2026-08-13; engine releases labelled 'preview release candidate', default tag :dev). Free to self-host under Elastic License 2.0, but the GitHub repo holds only deployment scripts, examples and license notices; the engine is a closed binary you cannot build, patch or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** ClickBench is a well-known independent third-party suite. Its run scripts are public (ClickHouse/ClickBench firebolt/, with result, subresult and scan caches disabled) and it shows Firebolt beating DuckDB on hot runs across AWS instance types. The engine is a closed Docker binary with no compiler or flags, so it cannot be A.
- **Verifier notes:** Real entry with genuine independent-suite evidence, but the record overstated the result as '#1, ahead of ClickHouse, DuckDB and \~100+ engines'. Only the hot-run win over DuckDB is robust on current data. Leaderboard ratios and ranks were computed by replicating the page's own scoring JS over data.generated.js. License confirmed as Elastic License 2.0 from LICENSE.md (API spdx NOASSERTION).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/firebolt-db/firebolt-core>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/LICENSE.md>
  - <https://github.com/firebolt-db/firebolt-core#readme>
  - <https://benchmark.clickhouse.com/>
  - <https://benchmark.clickhouse.com/data.generated.js>
  - <https://github.com/ClickHouse/ClickBench>
  - <https://github.com/ClickHouse/ClickBench/tree/main/firebolt>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/query>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/results/20260829/c6a.4xlarge.json>
  - <https://hn.algolia.com/api/v1/items/44377439>
  - <https://www.firebolt.io/blog/introducing-firebolt-core>
- **Sources the enricher read:**
  - <https://github.com/firebolt-db/firebolt-core>
  - <https://github.com/firebolt-db/firebolt-core#readme>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/LICENSE.md>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/NOTICE.md>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/CHANGELOG.md>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/compose.yaml>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/config.json>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/SECURITY.md>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/get-core.sh>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/examples/README.md>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/licenses/NOTICE.clickhouse>
  - <https://github.com/firebolt-db/firebolt-core/blob/main/licenses/LICENSE.hyrise>
  - <https://github.com/firebolt-db/firebolt-core/commits/main>
  - <https://github.com/firebolt-db/firebolt-core/issues>
  - <https://github.com/firebolt-db/firebolt-core/issues/59>
  - <https://github.com/firebolt-db/firebolt-core/issues/12>
  - <https://github.com/firebolt-db/firebolt-core/issues/11>
  - <https://github.com/firebolt-db/firebolt-core/issues/9>
  - <https://www.firebolt.io/blog/introducing-firebolt-core>
  - <https://hn.algolia.com/api/v1/items/44377439>
  - <https://docs.firebolt.io/firebolt-core/firebolt-core-differences>
  - <https://docs.firebolt.io/llms.txt>
  - <https://docs.firebolt.io/overview/architecture-overview.md>
  - <https://docs.firebolt.io/self-managed/connecting-over-http.md>
  - <https://docs.firebolt.io/performance-and-observability/storage-and-indexing.md>
  - <https://cdmsworkshop.github.io/2022/>
  - <https://cdmsworkshop.github.io/2022/proceedings.html>
  - <https://cdmsworkshop.github.io/2022/Proceedings/ShortPapers/Paper1_MoshaPasumansky.pdf>
  - <https://github.com/ClickHouse/ClickBench#readme>
  - <https://github.com/ClickHouse/ClickBench/blob/main/lib/benchmark-common.sh>
  - <https://github.com/ClickHouse/ClickBench/tree/main/firebolt>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/benchmark.sh>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/create.sql>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/query>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/install>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/load>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/start>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/check>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/data-size>
  - <https://github.com/ClickHouse/ClickBench/blob/main/firebolt/template.json>
  - <https://github.com/ClickHouse/ClickBench/tree/main/firebolt/results/20260829>
  - <https://github.com/ClickHouse/ClickBench/tree/main/clickhouse/results/20260926>
  - <https://github.com/ClickHouse/ClickBench/tree/main/duckdb/results/20260511>
  - <https://api.crossref.org/works?query.bibliographic=Assembling+a+Query+Engine+From+Spare+Parts+Firebolt>
  - <http://export.arxiv.org/api/query?search_query=all:Firebolt+AND+all:query>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/firebolt-db/firebolt-core`) · [data/wave6/enrich/raw/github_com_firebolt_db_firebolt_core.json](../../../data/wave6/enrich/raw/github_com_firebolt_db_firebolt_core.json) (enrichment confidence 0.72)

</details>
