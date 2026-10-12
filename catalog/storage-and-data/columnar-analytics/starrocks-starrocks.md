# StarRocks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Distributed MPP SQL OLAP database with C++ vectorized engine; vendor SSB-Flat test shows 1.87x over ClickHouse, ClickBench shows the reverse.

| | |
|---|---|
| **Beats** | ClickHouse |
| **Claimed result** | StarRocks docs (SSB Flat-table Benchmarking): on 13 queries over the 100 GB SSB-Flat dataset, 'StarRocks has an overall query performance 1.87x that of ClickHouse' (sum of average latencies 992 ms vs 1,858 ms; per-query ratios 1.12x-2.63x). The earlier StarRocks blog post (Aug 21, 2023; https://www.starrocks.io/blog/benchmark-test) claimed 'ClickHouse has a response time 2.2x slower than that of StarRocks' on the same 13 SSB flat-table queries, with no hardware stated. |
| **Workload** | Star Schema Benchmark flattened into a single wide table (SSB-Flat, 100 GB; the ClickHouse-style denormalized SSB, so no joins), 13 queries, 1 warm-up plus the average of 3 runs. StarRocks 3.5.0 vs ClickHouse 25.3.3.42 (and Apache Druid 33.0.0), all with default configurations. |
| **Metric** | latency |
| **Hardware** | AWS m7i.4xlarge hosts (16 vCPU, 64 GiB each; 5 instances listed). StarRocks runs 1 FE + 3 BEs and ClickHouse 3 nodes. CPU model and OS not stated. |
| **Adoption** | 12.1k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/StarRocks/starrocks) · [benchmark](https://docs.starrocks.io/docs/benchmarking/SSB_Benchmarking/) |

## Verdict

The vendor docs ran 13 SSB-Flat queries (one denormalized table, so no joins) at 100 GB, with 1 warm-up and the mean of 3 runs. StarRocks 3.5.0 (1 FE + 3 BEs) faced ClickHouse 25.3.3.42 (3 nodes) on AWS m7i.4xlarge with default configs, and the summed latency was 992 ms vs 1,858 ms (1.87x; 1.12x-2.63x per query); no CPU model, compiler flags, DDL or scripts are published. Independent ClickBench on a single c6a.4xlarge reverses the result: hot sums of 44.47 s for StarRocks 4.0.14 (2026-09-07) vs 18.03 s for ClickHouse (2026-09-26).

## Use it when

- Interactive queries over normalized star or snowflake schemas where you would rather not flatten everything into one wide table, which is the usual ClickHouse approach. The CBO and runtime filters target this case, but the vendor's join benchmarks (TPC-DS 1 TB, TPC-H 100 GB) compare against Trino, not ClickHouse.
- One SQL engine over lakehouse tables (Iceberg/Hive/Hudi/Delta on S3 or HDFS) with a local cache on compute nodes, instead of moving data into a separate OLAP store.
- Real-time upsert/delete ingestion into Primary Key tables while concurrent analytical queries run.
- Multi-node x86 clusters with AVX2 (vendor guidance: 16 cores / 64 GB per BE, at least 3 BEs and 3 FEs) serving MySQL-protocol BI tools or dashboards at high concurrency, with resource groups for tenant isolation.
- The vendor SSB-Flat setup (13 queries, 100 GB, m7i.4xlarge) is small enough to reproduce against your own ClickHouse deployment before you commit.

## Skip it when

- Single-node, single-wide-table scan-and-aggregate work, which is ClickHouse's home turf. On ClickBench (c6a.4xlarge, 43 queries, hot best-of-3), StarRocks 4.0.14 sums to 44.47 s against ClickHouse's 18.03 s and wins only 3 of 43 queries (geomean about 3x slower, computed from the published result JSONs).
- Workloads dominated by very short queries. On ClickBench, the two queries ClickHouse answers in about 1 ms take 35-59 ms on StarRocks, which suggests a fixed per-query overhead (likely FE planning plus the MySQL-protocol round trip; the cause is not documented).
- Embedded or in-process analytics. It needs a JDK 17+ FE process plus BE/CN processes, and production guidance is 3+ FEs and 3+ BEs; chDB or DuckDB fit this case better.
- Production on aarch64 or on x86 without AVX2. The docs 'highly recommend' x86 with AVX2, and aarch64 builds exist but the vectorization is AVX2-oriented. v4.2+ binaries need glibc 2.34+, which rules out EL7/EL8, CentOS 8 and Amazon Linux 2.
- Storage- or ingest-constrained setups. On the same ClickBench run, StarRocks took 489 s to load versus 182 s for ClickHouse and used 17.9 GB on disk versus 9.4 GB.

## How it is fast

Columnar storage feeds a chunk-at-a-time vectorized engine with SIMD kernels (filter, gather, RLE/delta decode in be/src/base/simd; x86 builds use -mavx2 by default, AVX-512 opt-in), a morsel-driven pipeline scheduler, and a low-cardinality global dictionary that runs operators directly on dictionary-encoded strings ('operation on encoded data'). For joins, a Cascades-style cost-based optimizer (join reorder, CTE reuse, subquery rewrite, broadcast/shuffle/colocate choice, histograms) plans the query, runtime filters from hash-join build sides are pushed into scans, join hash tables are bucket-chained or linear-probing with 8-bit fingerprints, and expressions can optionally be LLVM JIT-compiled. The vendor SSB-Flat test has no joins, so its win comes from the scan/filter/aggregate path plus MPP spread across 3 BEs; the docs give no finer attribution.

## Compared with alternatives

Umbra beats ClickHouse on ClickBench by a far wider margin but has no public source; chDB is in-process ClickHouse for single-node file/dataframe queries; Velox is an execution library you embed in your own engine. Pick StarRocks when you need an open-source (Apache-2.0), self-hosted distributed SQL server for join-heavy normalized schemas, lakehouse catalogs and real-time upserts.

## Integration

| | |
|---|---|
| **Form** | standalone server (prebuilt Linux tarballs, Docker, Helm/Kubernetes operator); not a linkable library |
| **Dependencies** | JDK 17+ for the FE on v3.5+ (JRE not supported); a supported Linux (RHEL/CentOS 7.9 or Ubuntu 22.04/24.04 through v4.1, glibc 2.34+ for v4.2+ binaries); the BE statically links its bundled third-party libraries (per be/CMakeLists.txt); optional object storage or HDFS for shared-data mode; SSD required for Primary Key tables with a persistent index. |
| **Minimum toolchain** | Building from source needs C++23 (-std=gnu++23). The official toolchain image pins GCC 14.3.0, though the Ubuntu build doc still says GCC 10.3+. Also CMake 3.20.1+ and JDK 17; Clang works via STARROCKS_LLVM_HOME. Most users run release binaries instead. |
| **Platforms** | Linux x86-64 with AVX2 is the recommended production target (-mavx2 by default, AVX-512 optional). Linux aarch64 builds with -march=armv8-a+crc. macOS ARM64 is a documented developer build only. |
| **Thread safety** | Not applicable as a library. The server handles concurrent sessions, each data load is an ACID transaction, and resource groups isolate tenants. |
| **Drop-in for the baseline** | no |

## Gotchas

- Migrating from ClickHouse means rewriting schema and queries. Tables use DUPLICATE/PRIMARY KEY plus DISTRIBUTED BY HASH(col) BUCKETS n instead of MergeTree ORDER BY, and the bucket count and distribution key fixed at CREATE time drive scan parallelism (ClickBench uses 192 buckets on UserID).
- The CBO depends on collected statistics. Histograms for skewed columns must be requested explicitly, and without good statistics the multi-join advantage the vendor advertises can disappear.
- The published comparisons are not setup-equal. The vendor SSB-Flat test gives StarRocks 1 FE + 3 BEs (4 hosts) against a 3-node ClickHouse, with default configs and no ClickHouse table-engine or sharding details. ClickBench's StarRocks script turns off the BE page cache and data cache (disable_storage_page_cache=true, datacache_enable=false), which also affects its hot runs.
- Stability: open issues report BE SIGSEGV crashes on recent releases (#79321 filter_range on 4.0.12, #73415 use-after-free on 3.5.16, #78100 CONCAT(COALESCE) on 3.5.16, #79494 JNI scanner close). BE MemTracker can over-report memory inside containers (#67607).

## Known shortcomings

- Vendor benchmark on flat SSB (no joins): 1.87x vs ClickHouse 25.3 (StarRocks 3.5.0, m7i.4xlarge). ClickBench shows the reverse (ClickHouse 18.03 s vs StarRocks 44.47 s), so the claim is contested.
- Unequal setups: the vendor gave StarRocks 1 FE + 3 BE (4 hosts) vs 3 ClickHouse nodes, with no DDL/scripts/CPU model published. On ClickBench StarRocks wins 3 of 43 queries (geomean \~3x slower); short queries take \~35-59 ms vs \~1 ms for ClickHouse; loading takes 489 s vs 182 s and disk 17.9 GB vs 9.4 GB.
- A server, not a library (JDK 17 frontend plus C++ backend); not a drop-in (different DDL/dialect, MySQL protocol). v4.2+ needs glibc 2.34+; source builds need C++23 (GCC 14.3 toolchain image). Open backend SIGSEGV issues (#79321, #73415, #78100); MemTracker over-reports memory in containers (#67607).

## Caveats and trade-offs

These are vendor-run numbers: default configs, no CPU model, no compiler flags and no linked benchmark scripts. The 2023 blog gave 2.2x; the current docs give 1.87x (StarRocks 3.5.0 vs ClickHouse 25.3.3.42). The claim is contradicted by the independent ClickBench suite on identical single-node c6a.4xlarge hardware. There, ClickHouse's 2026-09-26 run sums to 18.03 s (best of 3 across 43 queries) versus 44.47 s for StarRocks' 2026-09-07 run, so ClickHouse is about 2.5x faster (derived from page data: ClickHouse/ClickBench clickhouse/results/20260926/c6a.4xlarge.json vs starrocks/results/20260907/c6a.4xlarge.json). Both the vendor SSB-Flat test and ClickBench are single-flat-table workloads, not star-schema joins, so the gap cannot be put down to join handling. It more likely reflects cluster vs single-node setup, dataset and query mix, and tuning. The win should be treated as workload- and setup-specific.

MPP architecture with a separate Java frontend (FE, planner/metadata) and C++ backend (BE, vectorized execution engine) -- heavier operational footprint than embedded engines like DuckDB; MySQL-wire compatible.

## Maintenance

Very actively maintained (pushed 2026-09-26; 4.0.14 released 2026-08-27, 3.5.21 on 2026-08-31; 12.1k stars; Linux Foundation project, Apache-2.0); usable via prebuilt binaries, Docker or Kubernetes, while building from source is heavy (C++23 with a GCC 14 toolchain image, plus JDK 17 for the FE).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party vendor numbers. The 2023 blog verbatim says 'ClickHouse has a response time 2.2x slower than that of StarRocks' on 13 SSB flat-table queries, with no hardware. The current StarRocks docs page reports 1.87x with instance types, versions and per-query latencies, but gives no CPU model, compiler/flags or public benchmark script, so it is C, not A/B.
- **Verifier notes:** Both the 2023 blog's 2.2x and the ClickBench 18.03 s vs 44.47 s figures were verified. The record's caveat wrongly calls the vendor test 'star-schema joins': it is SSB flat tables. benchmark_url was switched to the current docs page, which states instance type, versions and per-query data (1.87x); the old blog is kept in claimed_speedup/caveats. The orchestrator may want to flag this as contested given the independent ClickBench reversal.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://www.starrocks.io/blog/benchmark-test>
  - <https://docs.starrocks.io/docs/benchmarking/SSB_Benchmarking/>
  - <https://github.com/StarRocks/starrocks>
  - <https://github.com/ClickHouse/ClickBench/tree/main/clickhouse/results/20260926>
  - <https://github.com/ClickHouse/ClickBench/tree/main/starrocks/results/20260907>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/starrocks/results/20260907/c6a.4xlarge.json>
- **Sources the enricher read:**
  - <https://github.com/StarRocks/starrocks>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/benchmarking/SSB_Benchmarking.md>
  - <https://docs.starrocks.io/docs/benchmarking/SSB_Benchmarking/>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/benchmarking/TPC_DS_Benchmark.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/benchmarking/TPC-H_Benchmarking.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/introduction/Architecture.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/introduction/Features.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/deployment/preparation/deployment_prerequisites.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/deployment/preparation/plan_cluster.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/using_starrocks/Cost_based_optimizer.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/developers/build-starrocks/build_starrocks_on_ubuntu.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docs/en/developers/mac-compile-run-test.md>
  - <https://github.com/StarRocks/starrocks/blob/main/docker/dockerfiles/toolchains/toolchains-rocky9.Dockerfile>
  - <https://github.com/StarRocks/starrocks/blob/main/be/CMakeLists.txt>
  - <https://github.com/StarRocks/starrocks/blob/main/be/src/exec/pipeline/README.md>
  - <https://github.com/StarRocks/starrocks/blob/main/be/src/exec/join/join_hash_map_method.h>
  - <https://github.com/StarRocks/starrocks/blob/main/be/src/base/simd/filter.h>
  - <https://github.com/StarRocks/starrocks/releases>
  - <https://github.com/StarRocks/starrocks/issues/79321>
  - <https://github.com/StarRocks/starrocks/issues/73415>
  - <https://github.com/StarRocks/starrocks/issues/78100>
  - <https://github.com/StarRocks/starrocks/issues/79494>
  - <https://github.com/StarRocks/starrocks/issues/67607>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/starrocks/results/20260907/c6a.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/starrocks/install>
  - <https://github.com/ClickHouse/ClickBench/blob/main/starrocks/create.sql>
  - <https://github.com/ClickHouse/ClickBench/blob/main/starrocks/query>
  - <https://github.com/ClickHouse/ClickBench/blob/main/clickhouse/install>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/starrocks/starrocks`) · [data/wave6/enrich/raw/github_com_starrocks_starrocks.json](../../../data/wave6/enrich/raw/github_com_starrocks_starrocks.json) (enrichment confidence 0.75)

</details>
