# YugabyteDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Apache-2.0 (core database: src/, java/, python/ and build tooling) AND LicenseRef-PolyForm-Free-Trial-1.0.0 (YugabyteDB Anywhere: managed/, troubleshoot/)` · 🟢 active

> Distributed SQL database (PostgreSQL-compatible YSQL plus Cassandra-style YCQL) over a C++ Raft/RocksDB store; not faster than single-node PostgreSQL.

| | |
|---|---|
| **Beats** | Apache Cassandra 3.11.1 (YCQL API against CQL, YCSB); not the assigned single-node PostgreSQL |
| **Claimed result** | Not faster than the assigned baseline. Independent public-code benchmark (MaibornWolff/database-performance-comparison, YugabyteDB 2.15.0 on 3 x i3.8xlarge, 8 cores and 10 GB per database node): YSQL 295,000 inserts/s vs single-instance PostgreSQL 428,000 (0.69x, derived from page data); YCQL 288,000 vs Cassandra 389,000 sync and 410,000 async (0.74x and 0.70x, derived from page data); YSQL query times 160 s vs 39 s (count-events) and 1700 s vs 119 s (temperature-stats-per-device), newest-per-device failed on YSQL. Vendor claim against Cassandra 3.11.1 (2017, search-result text only, page not opened, per-workload figures not corroborated by a second search): workload A about 74,710 ops/s for Cassandra vs 90,520 for YugaByte DB (1.21x) and workload C about 72,873 vs 103,484 (1.42x); on the 100% read workload about 42% faster at 1 million keys and 95% faster at 10 million keys; a later vendor post says YugabyteDB 1.1 averages more than 2.5x Cassandra 3.11 at 10M keys. |
| **Workload** | Vendor 2017 YCSB comparison of YugaByte DB's Cassandra-compatible YCQL API against Apache Cassandra 3.11.1 on identical 3-node clusters (replication factor 3, consistency levels chosen so both are strongly consistent) at 1, 5 and 10 million keys, using a YCSB fork with an enhanced prepared-statement Cassandra binding. |
| **Metric** | throughput |
| **Hardware** | Vendor 2017 test: 3 Google Compute n1-standard-16 nodes (16 vCPUs, 60 GB RAM, 2 x 375 GB SSD each), replication factor 3, per search-result text; CPU model not seen. |
| **Adoption** | 10.6k stars, 1.4k forks |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/yugabyte/yugabyte-db) · [benchmark](https://forum.yugabyte.com/t/ycsb-benchmark-results-for-yugabyte-and-apache-cassandra/59) |

## Verdict

No speedup over the assigned baseline: in MaibornWolff's public-code IoT benchmark (YugabyteDB 2.15.0, 3 pods of 8 cores and 10 GB on AWS i3.8xlarge hosts, 16 client workers, COPY/batch inserts of 1,000), YSQL inserted 295,000 rows/s against single-instance PostgreSQL's 428,000 and YCQL 288,000 against Cassandra's 389,000-410,000, with YSQL queries about 3x-14x slower than PostgreSQL (derived from page data; 160 s vs 39 s for count-events, 1,700 s vs 119 s for temperature-stats-per-device). The only win is a 2017 vendor YCSB test against Cassandra 3.11.1 on three GCP n1-standard-16 nodes (about 1.2x-1.4x on workloads A and C, 42%-95% on 100% reads), seen only as search-result text and not corroborated per workload.

## Use it when

- You need PostgreSQL-compatible SQL with strong consistency, automatic sharding and zero-RPO failover across zones or regions, and can accept higher per-query latency than a single PostgreSQL node.
- You run Cassandra-style key-value or wide-column workloads but need linearizable single-key writes, multi-key ACID transactions or strongly consistent global secondary indexes, which Cassandra does not provide.
- Write-heavy OLTP whose data or throughput outgrows one machine, on Linux x86-64 or ARM nodes with SSDs (the docs suggest 16+ cores and 32-64 GB RAM per node for production).
- You want the core database under Apache-2.0 (the default build produces only Apache-2.0 binaries).

## Skip it when

- Single-node or small workloads where plain PostgreSQL fits: the only opened independent benchmark (MaibornWolff, YugabyteDB 2.15) shows 3-node YSQL inserting at 0.69x single-instance PostgreSQL and its queries about 3x-14x slower (derived from page data).
- Analytics, large scans and aggregations: YugabyteDB's own benchmarking tracking issue #15858 lists aggregates up to 16x and DISTINCT up to 130x slower than PostgreSQL on colocated tables, index scans slower than sequential scans and missing aggregate push-downs; this catalog's columnar-analytics category does not fit.
- Raw Cassandra-API throughput: in the same independent test YCQL batch inserts reached 288,000/s against Cassandra's 389,000 (sync) and 410,000 (async); YCQL also lacks materialized views, triggers and UDFs.
- Clusters with very many tables or tablets on small nodes: each 1,000 tablet replicas cost about 0.4 vCPU for Raft heartbeats and 800 MiB (7,000 MiB recommended when active).
- Environments without reliable clock synchronisation: the deployment checklist requires chrony, since hybrid logical clocks underpin consistency.

## How it is fast

DocDB, the storage engine, is a heavily customised RocksDB LSM store: RocksDB's WAL is disabled because the Raft log already journals writes, MVCC uses hybrid-logical-clock timestamps in the key instead of RocksDB sequence numbers, and it adds data-model-aware bloom filters, per-SST min/max hints for range pruning, a server-wide scan-resistant block cache and global memstore limits. Against Cassandra, its documented advantages are architectural: Raft leader reads are served from one replica rather than a quorum, conditional writes cost one consensus round trip instead of Paxos lightweight transactions' four, secondary indexes are global (point reads, no fan-out), and C++ avoids JVM garbage-collection pauses. Distributed ACID transactions follow the Google Spanner design with an enhanced two-phase commit.

## Compared with alternatives

Pick it over ScyllaDB when you need SQL, distributed ACID transactions or strongly consistent secondary indexes rather than maximum Cassandra-API throughput, and over analytics siblings such as Apache Doris, StarRocks or DuckDB-class engines only when the workload is transactional; for scans and aggregations those siblings are the right tools.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Server binaries (yb-master, yb-tserver, a forked postgres); building from source needs CMake 3.31+, the yb_build.sh scripts and prebuilt third-party dependencies (the reference build image ships Clang, JDK 17, Go, Python 3.11, Rust, Ninja); clients use standard PostgreSQL drivers for YSQL or Cassandra drivers for YCQL, or YugabyteDB smart drivers. |
| **Minimum toolchain** | C++23 (CMAKE_CXX_STANDARD 23) with Clang or GCC; CPU must support SSE2 and SSE4.2 on x86. |
| **Platforms** | Linux only for production: AlmaLinux 8/9, RHEL 8/9, Amazon Linux 2023 and Ubuntu 20/22/24 on x86-64 and ARM (aarch64); Oracle Linux 8 on x86 only; SSDs required. |
| **Thread safety** | N/A as a server; clients connect concurrently; transactions support snapshot, serializable and read committed isolation. |
| **Drop-in for the baseline** | partial — YSQL speaks the PostgreSQL wire protocol and reuses its query layer, so most applications connect unchanged, but performance characteristics differ sharply (distributed scans, missing push-downs) and some queries need rewrites; YCQL is Cassandra-API compatible only at roughly CQL 3.4 level, without materialized views, triggers or UDFs. |

## Gotchas

- The vendor's Cassandra win (2017, YugaByte DB vs Cassandra 3.11.1, 3 x GCP n1-standard-16, RF 3) used Yugabyte's own YCSB fork with a modified Cassandra binding and a vendor-chosen Cassandra GC setup (G1GC, 12 GB heap in the follow-up); the forum posts could not be opened and only a directional lead that grows with key count was seen again.
- The independent MaibornWolff benchmark is itself uneven: PostgreSQL ran as one unreplicated instance against a 3-node replicated YugabyteDB, databases were tested at different times with whatever version was newest, YugabyteDB's temperature-stats query only performed after rewriting avg() as sum()/count() (avg was not pushed down), and newest-per-device failed with temp_file_limit unless rewritten as a loose index scan (then 0.08 s).
- use_memory_defaults_optimized_for_ysql reserves a large share of memory for PostgreSQL backends; set it to false when only YCQL is used, and YSQL connections each cost substantial memory (tracked regressions to 300 MB+ per connection in 2.15).
- The repository is dual-licensed: managed/ and troubleshoot/ (YugabyteDB Anywhere) are under the non-OSI PolyForm Free Trial License 1.0.0, so do not copy from those directories.

## Known shortcomings

- Not faster (verifier reject not-faster overridden to keep): the MaibornWolff benchmark (public code) has it slower than single-node PostgreSQL (0.69x inserts, queries 4-14x slower) and slower than Cassandra (0.70-0.74x); the 2017 vendor YCSB Cassandra numbers are search-snippet only and unconfirmed. Licence is Apache-2.0 plus the PolyForm Free Trial licence for managed/.
- independent benchmark compares against single unreplicated PostgreSQL across runs, with a YB-only query rewrite; YSQL queries 3x-14x slower

## Caveats and trade-offs

Snippet only: forum.yugabyte.com, yugabyte.com and docs.yugabyte.com did not resolve from this container (ENOTFOUND), so the vendor figures come from one WebSearch result summary and were not corroborated; a second verifier search confirmed only the setup (3 x n1-standard-16, RF 3, Cassandra 3.11.1, 1/5/10 million keys) and a throughput and p99 lead that grows with key count. Vendor-run, 2017, Cassandra 3.11.1, with a YCSB fork whose Cassandra binding the vendor modified, and a Cassandra configuration retuned by the vendor (G1GC, 12 GB heap) in the follow-up post. Opposite independent evidence was opened: MaibornWolff/database-performance-comparison (Apache-2.0, YugabyteDB 2.15.0 on 3 x i3.8xlarge, IoT insert workload) reports YSQL 295,000 inserts/s against single-instance PostgreSQL 428,000, YCQL 288,000 against Cassandra 389,000 (sync) and 410,000 (async), and YSQL query times 160 s vs 39 s (count-events), 1700 s vs 119 s (temperature-stats-per-device), with newest-per-device failing; so YugabyteDB is slower than both assigned and Cassandra baselines there (3-node YugabyteDB against single-instance PostgreSQL, which also carries replication cost). The repo's own docs (docs/content/stable/benchmark/, faq/comparisons/cassandra.md and postgresql.md) give YugabyteDB-only numbers or qualitative comparisons, with no head-to-head figures; README says only 'high-performance' and 'PostgreSQL-like performance' for the cost-based optimizer. The repository is dual-licensed: the database is Apache-2.0 but YugabyteDB Anywhere (managed/) is under the non-OSI PolyForm Free Trial License 1.0.0. Search snippets also mention user issues reporting YSQL far slower than PostgreSQL on single-node workloads (snippet only). [retier] Enricher: MaibornWolff harness flaws: single unreplicated PostgreSQL against a 3-node replicated YugabyteDB; databases tested at different times on whatever version was newest (cross-run); the temperature-stats query was rewritten from avg() to sum()/count() for YugabyteDB only; the newest-per-device query failed. YSQL queries ran 3x-14x slower (derived from page data). Tracking issue #15858 reports colocated aggregates up to 16x and DISTINCT up to 130x slower than PostgreSQL. The vendor's per-workload numbers against Cassandra remain uncorroborated (D defensible if corroboration is required). Category: distributed OLTP filed under columnar-analytics for lack of an OLTP category.

Distributed SQL database: DocDB storage layer in C++ with Raft replication, a forked PostgreSQL query layer (YSQL) and a Cassandra-style API (YCQL). Pays for strong consistency and horizontal scale with extra network round trips, so single-node latency and throughput trail plain PostgreSQL and Cassandra in independent tests. The default build produces only Apache-2.0 binaries; the managed/ directory (YugabyteDB Anywhere) is under the Polyform Free Trial licence 1.0.0 and is not OSI. The assigned category columnar-analytics fits poorly: this is a distributed OLTP database.

## Maintenance

Very actively maintained (commits through 2026-10-24, v2025.2 stable, 10.6k stars) and the core database is Apache-2.0, but it is a full distributed database to deploy and operate, not code to embed or copy into a C++ project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** The vendor forum post (2017 YCSB vs Cassandra 3.11.1) did not resolve, and a fresh search confirmed only its setup and a directional throughput lead, not the per-workload figures; the only opened, public-code benchmark (MaibornWolff/database-performance-comparison) shows YugabyteDB slower than the assigned single-node PostgreSQL baseline and slower than Cassandra.
- **Verifier notes:** Rejected as not-faster against the assigned single-node PostgreSQL baseline (and against Cassandra in the only opened independent benchmark); the 2017 vendor Cassandra win stays snippet-only. Keep with a 'not faster' shortcoming if policy keeps it; license corrected to dual Apache-2.0 / PolyForm Free Trial, usability mixed.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 6 book seed pass, 2026-10-24); enrichment (wave 6 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/yugabyte/yugabyte-db>
  - <https://github.com/yugabyte/yugabyte-db/commits>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/LICENSE.md>
  - <https://github.com/MaibornWolff/database-performance-comparison>
- **Sources the enricher read:**
  - <https://github.com/yugabyte/yugabyte-db>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/README.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/src/AGENTS.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/CMakeLists.txt>
  - <https://github.com/yugabyte/yugabyte-db/tree/master/docs/content/stable/architecture/docdb>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/architecture/docdb/_index.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/architecture/docdb/performance.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/architecture/docdb/lsm-sst.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/architecture/docdb/packed-rows.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/faq/comparisons/cassandra.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/faq/comparisons/postgresql.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/deploy/checklist.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/reference/configuration/operating-systems.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/explore/ycql-language/cassandra-feature-support.md>
  - <https://github.com/yugabyte/yugabyte-db/tree/master/docs/content/stable/benchmark>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/benchmark/ycsb-ycql.md>
  - <https://raw.githubusercontent.com/yugabyte/yugabyte-db/HEAD/docs/content/stable/benchmark/key-value-workload-ycql.md>
  - <https://github.com/yugabyte/yugabyte-db/issues?q=is%3Aissue+is%3Aopen+slower+than+postgres>
  - <https://github.com/yugabyte/yugabyte-db/issues/15858>
  - <https://raw.githubusercontent.com/MaibornWolff/database-performance-comparison/HEAD/README.md>
  - WebSearch: YugaByte DB vs Apache Cassandra 3.11 YCSB benchmark results workload A ops/sec forum (snippets of forum.yugabyte.com threads 59 and 99 and the yugabyte.com blog; pages not opened)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/yugabyte/yugabyte-db`) · [data/wave6/enrich/raw/github_com_yugabyte_yugabyte_db.json](../../../data/wave6/enrich/raw/github_com_yugabyte_yugabyte_db.json) (enrichment confidence 0.65)

</details>
