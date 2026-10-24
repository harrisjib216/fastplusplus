# ScyllaDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `LicenseRef-ScyllaDB-Source-Available-1.1` · 🟢 active

> C++ rewrite of Apache Cassandra (CQL, plus a DynamoDB API) on a thread-per-core engine; vendor claims 3-8x Cassandra 4.0 throughput.

| | |
|---|---|
| **Beats** | Apache Cassandra 4.0 (Java; cassandra-stress, CL=QUORUM) |
| **Claimed result** | Vendor claim (search-result text only, page not opened): 3x-8x the throughput of Cassandra 4.0 on identical 3-node i3.4xlarge clusters at P99 under 10 ms (white-paper table: about 3x at P90 under 10 ms, 2.66x-8x at P99 under 10 ms); in the '4 vs 40' test, 4 ScyllaDB i3.metal nodes give 33% more throughput than 40 Cassandra i3.4xlarge nodes at P99 under 10 ms in one vendor statement and 42% more for a 40 TB cluster that costs 2.5x less in another; the vendor's '80% to 2,200% higher Cassandra P99' figure was not seen again in this check; a New Stack summary of the same tests gives 2x to 4.5x (not re-checked). The repository README only claims 'order-of-magnitude performance improvements' with no figures. |
| **Workload** | ScyllaDB's own cassandra-stress comparison of ScyllaDB 4.4.3 against Apache Cassandra 4.0: equal 3-node clusters of AWS i3.4xlarge, maximum throughput while P99 latency stays under 10 ms, plus a '4 vs 40' test of 4 i3.metal ScyllaDB nodes against 40 i3.4xlarge Cassandra nodes with fifteen loader machines. |
| **Metric** | throughput |
| **Hardware** | AWS i3.4xlarge (3-node clusters, 48 vCPUs in total) and i3.metal (4 ScyllaDB nodes, 288 vCPUs) against 40 x i3.4xlarge for Cassandra (640 vCPUs, about 2.22x the ScyllaDB vCPUs, derived from page data); the vendor's '2.5x' refers to hardware cost, not vCPUs. ScyllaDB ran CentOS 7.9 and Cassandra Ubuntu 20.04, single availability zone, per search-result text. |
| **Adoption** | 15.8k stars, 1.5k forks |
| **Last commit** | 2026-10-23 |
| **Links** | [repository](https://github.com/scylladb/scylladb) · [benchmark](https://www.scylladb.com/2021/08/24/scylladb-vs-cassandra-performance-results/) |

## Verdict

ScyllaDB's own 2021 cassandra-stress tests (ScyllaDB 4.4.3 vs Apache Cassandra 4.0 on equal 3-node AWS i3.4xlarge clusters) report 3x-8x Cassandra's throughput at P99 under 10 ms (white-paper table 2.66x-8x), and in a 4 i3.metal vs 40 i3.4xlarge test, comparable or higher throughput plus 11x faster node addition and 32x faster major compaction; all vendor-run, seen only through search-result text, with no compiler, CPU-model or harness published and no independent replication found (a 2025 Applied Computer Systems YCSB study's abstract favours ScyllaDB on several features but its numbers were not seen).

## Use it when

- You run Cassandra (CQL) or DynamoDB-style key-value/wide-column workloads and want higher throughput per node or fewer nodes at a P99 latency target.
- Dedicated Linux machines or large cloud instances with local NVMe (the vendor tests used AWS i3.4xlarge and i3.metal) where the database may own every core and nearly all memory.
- Read-heavy workloads whose hot set fits in the row cache, or write-heavy time-series data with TWCS/ICS compaction.
- Small deployments that stay within the source-available licence's caps (10 TB total storage, 50 vCPUs) and are not run as a SaaS/DBaaS, or teams prepared to buy a commercial licence.

## Skip it when

- Analytical scans, joins or ad hoc SQL: it is an OLTP wide-column store with lightweight transactions only, despite this catalog's columnar-analytics category; pick a column-store engine instead.
- You need an open-source (OSI) licence, a large self-hosted cluster, or a managed offering of your own: the ScyllaDB Software License Agreement v1.1 limits use to 'Never Customers', caps storage at 10 TB and 50 vCPUs, bans SaaS/DBaaS and competing use, and assigns your modifications to the licensor.
- Cassandra features it lacks: Triggers, SAI (except for vector search), Incremental Repair, super columns, Thrift (dropped in 6.0), dynamic snitching and non-Murmur3 partitioners; User Defined Functions are marked unavailable for Cassandra compatibility and only experimental.
- Shared or overcommitted hosts (laptops, busy Kubernetes nodes): by default it pins threads and claims all memory; --smp/--memory/--overprovisioned reduce that, at a performance cost.
- Clusters with frequent topology changes under tight P99 budgets: open issues report P99 spikes during node add/decommission, tablet split/merge, repair and compaction (e.g. #20895, #23441, #24025, #3615).

## How it is fast

Built on the Seastar framework: one pinned thread per core (shard-per-core, shared-nothing), futures-based asynchronous code with no locks between cores, and every partition owned by exactly one shard; shard-aware drivers can connect straight to the owning shard via the SCYLLA_SHARD_AWARE_PORT protocol extension. It claims all RAM at start-up and keeps its own row cache (row-granular LRU eviction) and memtables in a log-structured allocator (LSA, 128 KiB segments with memory compaction) instead of relying on the OS page cache and a JVM heap, so there are no GC pauses. Seastar CPU and I/O schedulers with share-based scheduling groups and a backlog-driven compaction controller keep compaction, streaming and repair from starving foreground queries.

## Compared with alternatives

Pick it over YugabyteDB when you need Cassandra/DynamoDB-API throughput rather than SQL and distributed ACID transactions, and over TDengine or QuestDB when the data is general wide-column key-value rather than time series; for analytics use a sibling such as Apache Doris, StarRocks or DuckDB-class engines instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Server binary; built from source with Seastar (git submodule), Ninja and a recent C++23 toolchain, ideally via the frozen 'dbuild' Docker/Podman toolchain; clients use any CQL or DynamoDB driver (shard-aware drivers recommended). |
| **Minimum toolchain** | C++23 compiler (HACKING.md also says GCC &gt;= 10, an older note; the frozen toolchain is the supported path); about 2 GB RAM per build thread, 3 GB when linking. |
| **Platforms** | 64-bit Linux only; x86-64 with SSE4.2 required (will not boot without it) and AArch64 including AWS Graviton. |
| **Thread safety** | N/A as a server; internally one thread per core with data partitioned by shard; clients connect concurrently over CQL. |
| **Drop-in for the baseline** | partial — the project documents itself as a drop-in replacement for Cassandra 3.11 (CQL and SSTable compatible), but some Cassandra features (Triggers, SAI, Incremental Repair, Cassandra-compatible UDFs) are missing, and configuration and operations tooling differ. |

## Gotchas

- The performance claims are vendor-run (2021, ScyllaDB 4.4.3 vs Cassandra 4.0) with no public harness; the '4 vs 40' test pits 4 i3.metal nodes (288 vCPUs) on CentOS 7.9 against 40 i3.4xlarge nodes (640 vCPUs, about 2.2x, derived from page data) on Ubuntu 20.04, and the vendor concedes Cassandra has lower latency at low throughput there.
- Today's licence is not the one the benchmarked 'Scylla Open Source 4.4' shipped under; the current repository is source-available only, so you cannot copy code from it into your project.
- Startup checks expect a tuned machine; --developer-mode 1 disables them, and the setup scripts tune IRQs and disks, so untuned installs can underperform the published numbers.
- Compaction needs headroom: the docs recommend keeping 50% (LCS/TWCS) to 70% (ICS) disk utilisation at most, and a 30:1 disk-to-RAM ratio (100:1 maximum).

## Known shortcomings

- Verifier: vendor-only evidence seen only as search snippets (scylladb.com and the white paper unreachable); the 4-vs-40 result appears as both 33% and 42% more throughput; the 80%-2200% P99 figure was not found again; columnar-analytics fits poorly.
- 4 vs 40 test: Cassandra had 2.22x the vCPUs (not 2.5x) on a different OS; P99 spikes during topology changes, repair and compaction in open issues

## Caveats and trade-offs

Snippet only: scylladb.com, resources.scylladb.com, thenewstack.io and planetcassandra.org did not resolve from this container (ENOTFOUND), so no benchmark page was opened; the figures come from WebSearch result text that repeated them consistently across two queries, and they could not be checked against the pages. Vendor-run (first-party), 2021, ScyllaDB 4.4.3 against Cassandra 4.0; the benchmarked 'Scylla Open Source 4.4' predates the current source-available licence (its licence was not checked). The harness is not in the scylladb/scylladb repo (only the cassandra-stress parameters are described in the vendor text, not seen); no compiler or flags apply to the Java baseline; no independent replication found. The '4 vs 40' test mixes cluster sizes and instance types, and the vendor itself says Cassandra 4.0 on 40 i3.4xlarge nodes has better latency at low throughput. The 3x-8x headline rounds up the table's 2.66x lower bound. Nothing in the repo (README, docs/ listing, issue #649 which only links a 2016 YCSB post) carries numbers. Category 'columnar-analytics' is the assigned guess; ScyllaDB is a distributed wide-column OLTP store, so the category fits poorly. [retier] Enricher: in the '4 vs 40' test Cassandra had 640 vCPUs against ScyllaDB's 288 (2.22x, derived), not 2.5x (that is the vendor's cost ratio); the two sides ran different OSes (CentOS 7.9 against Ubuntu 20.04) in one availability zone. Only lead for independent evidence: a 2025 Applied Computer Systems YCSB study, abstract only (reference-global.com and doaj.org unreachable). Open issues report P99 spikes during topology changes, tablet split, repair and compaction (#20895, #23441, #24025, #3615). Category: a distributed wide-column OLTP store filed under columnar-analytics for lack of an OLTP category.

Shared-nothing, thread-per-core design on the Seastar framework (C++23) that wants whole machines and shard-aware clients; Cassandra (CQL) and DynamoDB (Alternator) API-compatible, so a wide-column/NoSQL store with no joins and only lightweight transactions. Current licence is source-available (ScyllaDB Software License Agreement v1.1, last updated April 12 2026): limited to 'Never Customers', capped at 10 TB storage and 50 vCPUs in total, no SaaS/DBaaS use and no competing use, modifications are assigned to the licensor. Not an OSI licence, so the code is a reference, not copyable.

## Maintenance

Very actively developed (commits through 2026-10-23, 15.8k stars), but the current source-available licence (v1.1, April 2026) makes it a reference implementation rather than copyable code, and free use is capped at 10 TB and 50 vCPUs for non-customers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor-run cassandra-stress comparison (ScyllaDB 4.4 vs Cassandra 4.0) with no public harness, compiler or CPU model; the vendor page and white paper did not resolve (ENOTFOUND), but a fresh WebSearch repeated the 3x-8x and 2.66x-8x figures, so first-party, snippet-only C.
- **Verifier notes:** scylladb.com, www.scylladb.com and the white-paper PDF all ENOTFOUND; numbers rest on search snippets that agree across two independent queries. Seed assignment baseline is Apache Cassandra, so baseline_in_list true stands; category columnar-analytics fits poorly (wide-column OLTP store). License file confirmed as ScyllaDB Software License Agreement v1.1 (non-OSI), so 'reference' stands.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 6 book seed pass, 2026-10-24); enrichment (wave 6 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/scylladb/scylladb>
  - <https://github.com/scylladb/scylladb/commits>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/LICENSE-ScyllaDB-Source-Available.md>
- **Sources the enricher read:**
  - <https://github.com/scylladb/scylladb>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/README.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/HACKING.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/README.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/building.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/repository_layout.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/row_cache.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/isolation.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/compaction_controller.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/dev/protocol-extensions.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/architecture/index.rst>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/getting-started/system-requirements.rst>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/getting-started/scylla-in-a-shared-environment.rst>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/docs/using-scylla/cassandra-compatibility.rst>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/utils/logalloc.hh>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/LICENSE-ScyllaDB-Source-Available.md>
  - <https://raw.githubusercontent.com/scylladb/scylladb/HEAD/NOTICE.txt>
  - <https://raw.githubusercontent.com/scylladb/seastar/HEAD/README.md>
  - <https://github.com/scylladb/scylladb/tree/master/docs/getting-started>
  - <https://github.com/scylladb/scylladb/tree/master/docs/dev>
  - <https://github.com/scylladb/scylladb/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://github.com/scylladb/scylladb/issues?q=is%3Aissue+is%3Aopen+latency+spike>
  - WebSearch: ScyllaDB vs Cassandra independent benchmark benchANT throughput results (snippets incl. reference-global.com acss-2025-0019, not openable: ENOTFOUND)
  - WebSearch: ScyllaDB 4 vs 40 i3.metal Cassandra 4.0 (snippets of thenewstack.io, scylladb.com, resources.scylladb.com; pages not opened)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/scylladb/scylladb`) · [data/wave6/enrich/raw/github_com_scylladb_scylladb.json](../../../data/wave6/enrich/raw/github_com_scylladb_scylladb.json) (enrichment confidence 0.6)

</details>
