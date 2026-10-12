# Apache Doris

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> MPP SQL analytics database (Java FE, C++ vectorized BE); vendor sf1000 runs show 5-11x faster than ClickHouse on join-heavy benchmarks.

| | |
|---|---|
| **Beats** | ClickHouse |
| **Claimed result** | sf1000 total run time on the internal-table-format tab: SSB (13 queries) Doris 11.6s vs ClickHouse 82.2s (\~7.1x), TPC-H (22 queries) 53.8s vs 279.0s (\~5.2x), TPC-DS (99 queries) 173.8s vs 1913.9s (\~11.0x) (ratios derived from page data). Redshift and Snowflake are also slower on the page, e.g. SSB 30.1s / 32.9s. Agent-observability tab (100M rows): Analytics Rollups Doris 4.3s vs DuckDB 13485.7s (\~3,136x) and Semi-Structured Payload 2.5s vs 17795.2s (\~7,118x) (derived from page data). On the same tab ClickHouse takes 42.1s / 42.3s / 24.3s vs Doris 2.3s / 4.3s / 2.5s. |
| **Workload** | SSB, TPC-H, and TPC-DS analytical benchmarks at sf1000 scale (13/22/99 queries respectively); also cites 100M-row agent-observability workloads vs DuckDB |
| **Metric** | throughput |
| **Adoption** | 16k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/apache/doris) · [benchmark](https://doris.apache.org/why-doris/benchmarks/) |

## Verdict

On the vendor's own page at sf1000, Doris's total run times were 11.6 s vs ClickHouse 82.2 s on SSB (13 queries, joined schema), 53.8 s vs 279.0 s on TPC-H and 173.8 s vs 1913.9 s on TPC-DS (about 7.1x, 5.2x and 11.0x), with no hardware, cluster size, versions, compiler or tuning disclosed. The agent-observability numbers come from VeloDB's own AgentLogsBench on an AWS m6i.8xlarge with 100M rows (Doris 2.3/4.3/2.5 s vs ClickHouse 42.1/42.3/24.3 s; the DuckDB gaps come from DuckDB's JSON handling collapsing on specific queries), while on independent single-table ClickBench, ClickHouse is about 1.7-2.3x faster by geomean.

## Use it when

- Star/snowflake schemas and TPC-DS-style ad-hoc SQL with many large joins, where ClickHouse would need denormalized flat tables or hand-ordered joins.
- Customer-facing dashboards that need many concurrent sub-second queries over data that is ingested continuously and upserted (Unique-key tables).
- Log, trace and agent-observability data that mixes full-text search, dynamic-JSON filters and aggregations in one SQL engine, as an alternative to Elasticsearch/OpenSearch plus a separate OLAP store.
- Speeding up SQL over existing Iceberg/Hudi/Delta/Paimon lakehouse tables without copying the data.
- Teams whose BI and tooling already speak the MySQL protocol.

## Skip it when

- Single wide-table scan/filter/aggregate workloads (ClickBench shape). In the date-matched ClickBench results (both 2026-05-10, both untuned), ClickHouse was faster: on c6a.4xlarge the hot-run sum was 33.0 s vs Doris 48.4 s, with Doris winning only 5 of 43 queries; on c6a.metal it was 8.25 s vs 11.0 s. Doris's stored data was also larger (13.8 GB vs 9.4 GB).
- Embedded or in-process analytics. Doris needs a JVM frontend (JDK 17 for 3.0+) and C++ backend servers. The documented production minimum is 16 cores and 64 GB per node, with 3+ backends recommended; for embedded use pick DuckDB or chDB.
- OLTP or row-at-a-time transactional workloads. Doris is an analytical MPP store.
- Decisions that need independently reproducible numbers. The SQL-benchmark report is marked 'Coming Soon', and the page gives no hardware, cluster size, versions or configuration.

## How it is fast

The backend is a vectorized columnar engine using SIMD (SSE4.2 always, AVX2 by default, NEON on ARM); its column, PODArray and aggregation hash-table code is copied from ClickHouse and modified, and join hash tables are bucket-chained first/next uint32 arrays over the build-side block. Queries run on a pipeline engine modelled on HyPer's morsel-driven paper, which splits plans into PipelineTasks on a thread pool and uses local shuffle against skew. Most of the margin over ClickHouse on multi-join benchmarks likely comes from the Cascades-based cost optimizer (Nereids, rules plus statistics-driven CBO), runtime join filters (IN, Bloom, Min-Max, IN_OR_BLOOM) pushed into scans, and colocated/bucketed joins. Storage adds sorted compound-key prefix, min/max zone-map, Bloom and inverted indexes.

## Compared with alternatives

StarRocks (started as a fork of Doris) is the closest sibling and also claims to beat ClickHouse, though on SSB-flat with a smaller 1.87x margin; pick Doris for ASF governance and its built-in inverted-index, VARIANT and lakehouse-catalog feature set, and benchmark both on your own joins. Pick it over Umbra (no public repo) or Velox (an execution library for building engines) when you want a ready-made distributed open-source database rather than a component.

## Integration

| | |
|---|---|
| **Form** | Standalone server, not a library: FE (Java) plus doris_be (C++) binaries, shipped as release tarballs, Docker images or a Kubernetes operator. There is no embeddable C++ API. |
| **Dependencies** | FE needs a JDK: Java 17 for Doris 3.0+, Java 8 for 2.1 and earlier. A BE source build pulls about 90 bundled third-party packages (thirdparty/vars.sh lists Arrow, brpc, Thrift, Protobuf, RocksDB, jemalloc, simdjson, Hyperscan, parallel-hashmap, the AWS/Azure/GCS SDKs and more). BE Java extensions (JDBC/Hudi scanners, Java UDFs) are on by default and can be turned off with DISABLE_BE_JAVA_EXTENSIONS=ON. |
| **Minimum toolchain** | BE: C++20, GCC 11.1+ or Clang 16+ (both enforced in be/CMakeLists.txt). FE: JDK 17 and Maven. |
| **Platforms** | Linux x86-64 needs AVX2 by default; a no-AVX2 package or a USE_AVX2=0 build is available. Linux aarch64 builds with -march=armv8-a+crc by default. Documented file systems are ext4 and xfs. CMake also has macOS build paths, but macOS is not documented as a production platform. |
| **Thread safety** | Not applicable as a library. Clients open concurrent sessions over the MySQL protocol, and the BE runs each query multi-threaded (pipeline tasks on a shared thread pool). |
| **Drop-in for the baseline** | partial — It replaces ClickHouse as an analytics server, but the SQL dialect (MySQL-compatible, not ClickHouse SQL), table models, DDL and ingestion paths all differ, so schemas, queries and loaders have to be ported. |

## Gotchas

- The repo's TPC-H sf1000 DDL puts lineitem and orders in a colocate group on orderkey (768 buckets) and part and partsupp in one on partkey, with replication_num=1. Join speed depends on this kind of physical design. The benchmark page does not say whether its runs used these scripts or this layout.
- Security fixes have come in quickly in 2026. FE REST admin APIs were reachable without authentication before 3.1.0 (CVE-2026-58319). Privilege-check bypasses were fixed only in 4.0.8/4.1.4 (CVE-2026-68570, CVE-2026-72524). There is also an FE meta-service authentication bypass (CVE-2026-31377) and a JDBC-driver-URL RCE (CVE-2026-96443). Keep the FE off untrusted networks and stay on the latest patch line.
- Operational stability issues are open, e.g. #67619 (BE SIGSEGV during merge-on-write bulk load on 4.0.8) and #67898 (scanner-thread leak on every external-catalog query). Queries under memory pressure are cancelled with MEM_LIMIT_EXCEEDED or workload-group overcommit errors, so size memory and workload groups deliberately.
- The README warns that some third-party licenses are not compatible with Apache-2.0, so some features have to be disabled for a strictly Apache-2.0 build. tools/tpch-tools/README still says some TPC-H queries were rewritten for an old optimizer, but the current q9/q18/q21 files carry no such markers or hints, so that note looks stale.

## Known shortcomings

- Vendor benchmarks: the DuckDB multiples (3,136x/7,118x) are derived from the vendor's own AgentLogsBench, and no hardware is given for the SSB/TPC runs.
- Wins appear only on the vendor's side (sf1000 page with no hardware/config; report 'coming soon'). On date-matched untuned ClickBench (2026-05-10) ClickHouse is faster: c6a.4xlarge hot 33.0 s vs 48.4 s, Doris wins 5 of 43 queries. Its edge likely comes from the Nereids optimizer, runtime filters and colocated joins rather than raw scan speed.
- SECURITY: 2026 CVEs include an unauthenticated FE admin API before 3.1.0, a privilege bypass fixed in 4.0.8/4.1.4, a meta-service auth bypass and a JDBC RCE; stay on patched versions. A server, not a library (Java 17 FE + C++20 BE, \~90 third-party dependencies, AVX2 by default); open crash/leak bugs #67619 and #67898.

## Caveats and trade-offs

This is a vendor page. The SSB/TPC-H/TPC-DS report is 'Coming Soon', and no CPU or instance type, compiler, or engine configuration is stated for those runs. The Doris repo's tools/\*-tools scripts cover only Doris, not ClickHouse. The agent-observability numbers come from AgentLogsBench (github.com/velodb/agentlogsbench), published by VeloDB, the company behind Doris, and run on AWS m6i.8xlarge (32 vCPU, 128 GiB) per its blog. Its 3,136x and 7,118x DuckDB multipliers reflect DuckDB's JSON handling collapsing on specific queries, not engine-wide speed. That comparison is also not the ClickHouse baseline this record is about.

MPP distributed OLAP database (Java query planner/FE + C++ vectorized backend/BE), not an embeddable C++ library; heavier operational footprint than DuckDB; same architectural lineage as StarRocks

## Maintenance

Very active Apache top-level project (graduated 2022, about 16k stars) shipping two maintained lines (4.1.4 on 2026-09-07, 4.0.8 on 2026-08-14) under Apache-2.0, usable as prebuilt binaries, Docker images or a K8s operator, though building the BE from source needs a large third-party toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The vendor benchmark page shows sf1000 total run times for Doris vs ClickHouse (SSB 11.6s vs 82.2s, TPC-H 53.8s vs 279.0s, TPC-DS 173.8s vs 1913.9s), but the SQL-analytics report is marked 'Coming Soon'. No CPU or instance, compiler, or configuration is given, and the repo's tools/ssb-tools, tpch-tools and tpcds-tools scripts run only Doris. That is first-party with partial methodology, so C.
- **Verifier notes:** The headline ClickHouse numbers match the page exactly. The record's '3,135x' is 13485.7/4.3 ≈ 3,136x, and both DuckDB multipliers are derived, not printed on the page. Metadata checks out: Apache-2.0, 16,005 stars, not archived, last commit 2026-09-26. The Iceberg-format tab is rendered by JS and was not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://doris.apache.org/why-doris/benchmarks/>
  - <https://www.velodb.io/blog/agentlogsbench-apache-doris-in-ai-observability>
  - <https://github.com/apache/doris>
  - <https://github.com/apache/doris/tree/master/tools>
  - <https://github.com/velodb/agentlogsbench>
- **Sources the enricher read:**
  - <https://github.com/apache/doris>
  - <https://github.com/apache/doris/blob/master/be/CMakeLists.txt>
  - <https://github.com/apache/doris/blob/master/build.sh>
  - <https://github.com/apache/doris/blob/master/env.sh>
  - <https://github.com/apache/doris/blob/master/thirdparty/vars.sh>
  - <https://github.com/apache/doris/blob/master/be/src/core/pod_array.h>
  - <https://github.com/apache/doris/blob/master/be/src/exec/common/hash_table/join_hash_table.h>
  - <https://github.com/apache/doris/blob/master/be/src/exec/common/hash_table/hash_table.h>
  - <https://github.com/apache/doris/blob/master/tools/tpch-tools/README.md>
  - <https://github.com/apache/doris/blob/master/tools/tpch-tools/ddl/create-tpch-tables-sf1000.sql>
  - <https://github.com/apache/doris/blob/master/tools/tpch-tools/queries/q9.sql>
  - <https://github.com/apache/doris/releases>
  - <https://github.com/apache/doris/issues/67619>
  - <https://github.com/apache/doris/issues/67898>
  - <https://github.com/apache/doris/issues/36677>
  - <https://doris.apache.org/why-doris/benchmarks/>
  - <https://doris.apache.org/docs/dev/getting-started/what-is-apache-doris>
  - <https://doris.apache.org/docs/dev/install/preparation/env-checking>
  - <https://doris.apache.org/docs/dev/query-acceleration/optimization-technology-principle/pipeline-execution-engine>
  - <https://doris.apache.org/docs/dev/query-acceleration/optimization-technology-principle/query-optimizer>
  - <https://doris.apache.org/docs/dev/query-acceleration/optimization-technology-principle/runtime-filter>
  - <https://www.velodb.io/blog/agentlogsbench-apache-doris-in-ai-observability>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/doris/results/20260510/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/doris/results/20260510/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260510/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260510/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.4xlarge.json>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Apache%20Doris>
  - <https://hn.algolia.com/api/v1/search?query=Apache%20Doris&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/apache/doris`) · [data/wave6/enrich/raw/github_com_apache_doris.json](../../../data/wave6/enrich/raw/github_com_apache_doris.json) (enrichment confidence 0.7)

</details>
