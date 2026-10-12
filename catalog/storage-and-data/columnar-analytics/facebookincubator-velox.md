# Velox

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Meta's C++ vectorized execution-engine library; as Presto's C++ worker it ran 3TB TPC-H queries 2-9x faster than Presto Java.

| | |
|---|---|
| **Beats** | Presto Java execution engine (stock Presto vs Prestissimo, i.e. Presto with Velox C++ workers) |
| **Claimed result** | VLDB 2022 Table 2, 3TB TPC-H, Prestissimo (Velox) vs Presto Java wall time: Q1 5s vs 42s (8.4x), Q6 1s vs 9s (9x), Q13 15s vs 31s (2x), Q19 6s vs 13s (2.1x); CPU time 6.5x / 3.7x / 2.1x / 2.5x. Replay of production interactive-analytics traffic on two identical clusters: average speedup about 6-7x, with many queries above 10x. Prestissimo also served the same shadowed production workload with 3x fewer servers. |
| **Workload** | TPC-H at 3TB (ORC, no zstd compression, lineitem/orders co-partitioned), hand-written query formulations, selected queries Q1, Q6 (CPU-bound) and Q13, Q19 (shuffle/IO-heavy), warm local cache; plus a replay of Meta production interactive-analytics traffic on two clusters with identical hardware |
| **Metric** | throughput |
| **Hardware** | 80-node cluster, each node with 64GB RAM and 2x2TB SSD; CPU model not stated in the paper |
| **Adoption** | 4.2k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/facebookincubator/velox) · [benchmark](https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf) |

## Verdict

Meta's own VLDB 2022 paper ran Prestissimo (Java coordinator with Velox C++ workers) against stock Presto Java on an 80-node cluster (64 GB RAM and 2x2TB SSD per node; CPU model and compiler not stated), using 3TB TPC-H in uncompressed ORC with a warm cache and hand-written join orders, and reports wall times of 5s vs 42s (Q1), 1s vs 9s (Q6), 15s vs 31s (Q13) and 6s vs 13s (Q19), with 2.1-6.5x less CPU time; a production-traffic replay averaged 6-7x, and the same shadowed workload ran on 3x fewer servers. Only 4 of the 22 TPC-H queries are reported and no harness is public, Meta's 2023 blog claims 3-6x on shuffle-bound queries against the paper's 2.0-2.1x, and the earlier claim that it beats ClickHouse fails on ClickBench (214.09s vs 124.35s).

## Use it when

- You run prestodb with Java workers on Hive or Iceberg tables in ORC, DWRF or Parquet and want to cut worker CPU and server count. Presto C++ swaps the workers and keeps the Java coordinator; Meta's paper reports 8-9x lower wall time on CPU-bound TPC-H Q1 and Q6, about 2x on shuffle-heavy Q13 and Q19, and the same production load served with 3x fewer servers.
- Spark SQL batch or ETL jobs, through Apache Gluten's Velox backend. Gluten's README reports a 2.71x overall speedup over vanilla Spark on its 22-query TPC-H-style suite, and notes that the figure does not reflect the latest performance.
- You are building your own engine in C++ (streaming, ML preprocessing, a domain-specific SQL service) and need production-grade operators, Presto- or Spark-compatible function semantics, spilling and memory arbitration without writing them yourself.
- Queries dominated by string functions, regexes, array/map manipulation and dictionary-encoded columns. The paper says peeling, memoization and the simple-function framework pay off most there, and much less on plain arithmetic over primitives.
- Interactive queries over small-to-mid tables on disaggregated storage (S3, HDFS, GCS) that are read again and again, so the RAM+SSD cache and column prefetch can serve most IO locally.

## Skip it when

- You want a fast single-node analytical database. On ClickBench (c6a.xlarge, Parquet queried in place through Axiom), the best-of-3 total is 214.09s for Velox against 124.35s for ClickHouse, and Velox wins only 4 of 43 queries. Trivial queries have a floor of about 0.7-0.8s, against 2-3 ms for ClickHouse on Q0, Q1 and Q19, and Q29 (90 SUM expressions) takes 18.85s against 0.149s.
- Your users need SQL and you have no host engine. Velox has no parser, optimizer or catalog, and Axiom, the standalone SQL layer, is young (84 stars).
- Your Presto workloads depend on features Presto C++ lacks. It loads no Java plugins (no PageSourceProvider, RecordSetProvider or PageSinkProvider, and no user-supplied functions or types). CHAR, TIME, IPADDRESS, IPPREFIX, QDIGEST, TDIGEST, GEOMETRY and BINGTILE are unsupported, varchar(n) lengths are ignored, only some connectors are supported, and any unimplemented function fails the query.
- You need hard per-query memory caps. The Presto C++ docs say there is no OOM killer or reserved pool, and that queries may use more memory than they are allowed through memory arbitration.
- Small teams without build infrastructure. Velox is source-only (weekly version tags, no binary releases) and pulls in folly, fbthrift, boost, arrow, protobuf, ICU and more. Its Presto function translation units peak at about 4 GB of RAM each while compiling, and Windows is not a supported platform.

## How it is fast

Execution is vectorized and works on encoded data directly: dictionary 'peeling' runs a function once per distinct value, results are memoized across batches that share a dictionary, and Lazy Vectors defer loading columns until they are used. Expressions get common-subexpression elimination and constant folding at compile time, and at run time conjuncts and pushed-down scan filters are reordered adaptively by time/(1 + rows_in - rows_out); simple filters use SIMD through xsimd (the paper cites about one integer hit per clock on AVX2). Joins and aggregations share an F14-style hash table (128-byte buckets of 16 slots with 7-bit tags, vectorized inserts and lookups, interleaved probes that keep several cache misses in flight), and a VectorHasher maps keys to a flat array or a single 64-bit normalized key where it can. There is no JVM or GC, a mmap/madvise allocator keeps large buffers unfragmented, and a RAM+SSD cache with coalesced reads and adaptive prefetch keeps remote IO off the critical path.

## Compared with alternatives

Pick Velox when you are building or accelerating a distributed engine in C++ (Presto workers, Spark through Gluten, or your own engine) and need an embeddable execution library rather than a finished product. Umbra (a closed Docker-only database) and chDB (embedded ClickHouse for Python) are ready-to-query SQL engines, Bodo and cuDF target Python dataframe code, and Sirius is a GPU accelerator for DuckDB, so each fits better if you just want to run queries.

## Integration

| | |
|---|---|
| **Form** | static lib by default (CMake, one unified 'mono' library; VELOX_BUILD_SHARED=ON builds it shared), built from source only |
| **Dependencies** | folly, fbthrift/fizz/wangle/mvfst (all pinned to v2026.09.07.00), boost &gt;= 1.77, glog, gflags, fmt &gt;= 11.2, re2, xsimd &gt;= 10, simdjson &gt;= 4.1, protobuf 21.x, arrow &gt;= 15, ICU, double-conversion, geos, s2geometry, fast_float, xxhash, openssl, libevent, libsodium, zstd/lz4/snappy/xz, flex/bison; optional faiss, AWS/GCS/Azure SDKs, cuDF. Many can be bundled through VELOX_DEPENDENCY_SOURCE=BUNDLED, and setup scripts exist for Ubuntu, CentOS 9 and macOS. |
| **Minimum toolchain** | C++20; GCC 11+ or Clang 15+ (recommended GCC 12 on CentOS 9, GCC 11 on Ubuntu 22.04, Clang 16 on macOS); CMake 3.28+ |
| **Platforms** | Linux x86-64 (SSE4.2 minimum; the default CPU_TARGET=avx build needs AVX2, FMA, F16C, LZCNT and BMI2; AVX-512 is not used), Linux AArch64 (neoverse-n1 target; SVE not used), macOS on Intel and Apple silicon. Windows is not documented. |
| **Thread safety** | A Task runs each pipeline on several Drivers, one thread each. The application supplies the driver executor and IO thread pools, and peer operators coordinate through Task-owned bridges and barriers (for example, hash build to probe). Thread-safety guarantees for individual Vector or expression objects are not documented. |
| **Drop-in for the baseline** | partial: Velox itself is a C++ library with a different interface. Presto C++, built on it, is a drop-in replacement for Presto Java workers (same REST and exchange protocol, Java coordinator kept), but with the function, type, plugin and memory-management gaps listed in its Limitations page. |

## Gotchas

- The default build targets AVX2 (CPU_TARGET=avx), and binaries built that way will not run on SSE-only x86 hosts; set CPU_TARGET=sse for portable builds. Compiling is memory-hungry: limit BUILD_THREADS, since ClickBench's installer caps jobs at one per 5 GB of RAM and adds 16 GB of swap.
- Open correctness bugs remain. Issue #10338: TIMESTAMP WITH TIME ZONE values are compared by their packed physical value, so equal instants in different zones form separate GROUP BY groups. Issue #17115: a CASE with a non-deterministic operand returns wrong results. Issue #19100 reports latent strict-aliasing UB in BigintIdMap.h that GCC 16 exposes.
- Through Axiom, ClickBench found that a filter on the only unsigned Parquet column (UINT16 EventDate) segfaults the scan, and that the CLI's default of 4 in-process workers routes every stage through the shuffle path, making single-machine runs 10-50x slower (Q23: 0.7s with one worker, 37s with four). Pass --num_workers 1.
- The spread of speedups is wide and not all in Velox's favor. The paper's production-replay histogram (Figure 4) has a bucket for queries where Presto Java was faster, and the paper says that once workers are native, CPU-bound queries become bottlenecked on the Java coordinator's dispatch and shuffle-heavy ones on shuffle latency.

## Known shortcomings

- Loses to ClickHouse (a listed baseline) on ClickBench (214.09 s vs 124.35 s, wins 4 of 43 queries); the headline is now vs Presto Java per the VLDB'22 paper (TPC-H 3 TB 2-9x wall time, production average 6-7x). The record's 2.27x is Q32, not Q33 (1.67x) (verifier downgrade from A).
- The Presto Java claim is first-party (Meta VLDB'22): 4 of 22 TPC-H queries, harness not public, CPU and compiler unnamed (Q1/Q6 8-9x, Q13/Q19 \~2x; Meta's 2023 blog says 3-6x on shuffle queries while the paper table says 2.0-2.1x). On ClickBench it has a fixed \~0.7 s per-query cost and Q29 is 126x slower than ClickHouse. A library only (no parser, optimizer or catalog); Presto C++ replaces only Presto Java workers, with gaps (no Java plugins/UDFs, missing CHAR/TIME/QDIGEST/GEOMETRY types, no hard memory caps). Source-only build: C++20, GCC 11+/Clang 15+, heavy dependencies (folly, fbthrift, boost, arrow), \~4 GB RAM per compile unit, AVX2 by default, no Windows. Open wrong-result bugs: GROUP BY on TIMESTAMP WITH TIME ZONE (#10338), CASE (#17115); strict-aliasing UB (#19100).

## Caveats and trade-offs

The original ClickHouse claim does not hold. On ClickBench (c6a.xlarge, hits Parquet queried in place through Meta's Axiom SQL CLI; https://github.com/ClickHouse/ClickBench/blob/main/velox/results/20260831/c6a.xlarge.json), the sum of best-of-3 times is 214.09s for Velox/Axiom against 124.35s for ClickHouse MergeTree (clickhouse/results/20260926/c6a.xlarge.json). Velox wins only 4 of 43 queries (0-based numbering): Q32 10.67s vs 24.23s (2.27x), Q18 12.18s vs 21.84s (1.79x), Q33 10.49s vs 17.57s (1.67x) and Q34 11.13s vs 17.06s (1.53x). It is more than 100x slower on Q0, Q1 and Q19. Against the same-format entry, ClickHouse (Parquet, single) on 2026-09-26, the totals are 214.09s vs 123.75s: Velox wins 5 of 43 queries by 1.08-1.95x, loses 37, and is about 100x slower on Q29 (18.85s vs 0.187s). All of these figures are derived from page data. The 'dishonest academic paper' remark is in ClickBench's velox/README.md, not the top-level README. The paper's numbers are first-party Meta results for a distributed Presto deployment, so the benchmark code is not public and no compiler or CPU model is given. Presto Java is not in the wave's baseline list.

Velox itself is only a C++ execution-engine library with no SQL parser/optimizer/catalog; this result actually benchmarks facebookincubator/axiom (a thin SQL layer built on Velox); must be built from source (no release binaries), which is memory- and time-intensive

## Maintenance

Very active: daily commits (last 2026-09-26), weekly version tags such as v2026.09.18.00, 4.2k stars and about 1,600 open issues, Apache-2.0 licensed. There are no binary releases, and API breaks are flagged per PR with a 'BREAKING CHANGE' footer rather than by semantic versioning, so pin a commit or tag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The ClickBench benchmark_url holds only Velox/Axiom timings. Set against ClickHouse's own ClickBench files, Velox is about 1.7x slower overall, so the ClickHouse claim fails; in any case the compiler is not named and no CPU model is stated, so it could not be A. The re-pointed evidence is the peer-reviewed VLDB 2022 Velox paper (Table 2 and the Figure 4 text): Prestissimo (Presto running on Velox) against Presto Java, with no public benchmark code, compiler or CPU model, so B.
- **Verifier notes:** The record's own baseline claim (faster than ClickHouse on ClickBench) fails: Velox is slower in aggregate against both ClickHouse MergeTree and ClickHouse-on-Parquet, and the record also misattributed the 2.3x to Q33 (it is Q32; Q33 is 1.67x). I kept it as a downgrade by re-pointing it to the peer-reviewed VLDB 2022 comparison against Presto Java. If the orchestrator requires a list baseline, reject it as not-faster. Metadata checks out: Apache-2.0, 4,217 stars, last commit 2026-09-26, not a fork.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/results/20260831/c6a.xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/tree/main/velox>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/query>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260831/c6a.xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse-parquet/results/20260926/c6a.xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/README.md>
  - <https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf>
  - <https://github.com/facebookincubator/velox>
- **Sources the enricher read:**
  - <https://github.com/facebookincubator/velox>
  - <https://github.com/facebookincubator/velox/blob/main/CMakeLists.txt>
  - <https://github.com/facebookincubator/velox/blob/main/CMake/resolve_dependency_modules/README.md>
  - <https://github.com/facebookincubator/velox/blob/main/CONTRIBUTING.md>
  - <https://github.com/facebookincubator/velox/blob/main/velox/docs/develop/task.rst>
  - <https://github.com/facebookincubator/velox/blob/main/velox/docs/develop/hash-table.rst>
  - <https://github.com/facebookincubator/velox/blob/main/velox/docs/develop/simd.rst>
  - <https://github.com/facebookincubator/velox/blob/main/velox/docs/develop/TpchBenchmark.rst>
  - <https://github.com/facebookincubator/velox/blob/main/velox/docs/velox-in-10-min.rst>
  - <https://github.com/facebookincubator/velox/tags>
  - <https://github.com/facebookincubator/velox/issues/19100>
  - <https://github.com/facebookincubator/velox/issues/10338>
  - <https://github.com/facebookincubator/velox/issues?q=is%3Aopen+label%3Acorrectness>
  - <https://github.com/facebookincubator/velox/issues?q=segfault>
  - <https://github.com/facebookincubator/velox/issues?q=performance+regression>
  - <https://github.com/facebookincubator/velox/issues?q=label%3Asecurity>
  - <https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf>
  - <https://engineering.fb.com/2023/03/09/open-source/velox-open-source-execution-engine/>
  - <https://github.com/prestodb/presto/blob/master/presto-docs/src/main/sphinx/presto-cpp.rst>
  - <https://github.com/prestodb/presto/blob/master/presto-docs/src/main/sphinx/presto_cpp/limitations.rst>
  - <https://github.com/facebookincubator/axiom>
  - <https://github.com/apache/gluten>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/velox/results/20260831/c6a.xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse-parquet/results/20260926/c6a.xlarge.json>
  - <https://news.ycombinator.com/item?id=39805021>
  - <https://hn.algolia.com/api/v1/search?query=Prestissimo&tags=story>
  - <https://arxiv.org/abs/2606.24647>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/facebookincubator/velox`) · [data/wave6/enrich/raw/github_com_facebookincubator_velox.json](../../../data/wave6/enrich/raw/github_com_facebookincubator_velox.json) (enrichment confidence 0.7)

</details>
