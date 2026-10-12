# QuestDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java/C++/Rust time-series database whose QWP protocol streams query results into Arrow 1.55x faster than ClickHouse's fastest client path.

| | |
|---|---|
| **Beats** | ClickHouse |
| **Claimed result** | 1.55x faster than ClickHouse's fastest configuration of any kind (QuestDB \~220M rows/s at 8 readers vs ClickHouse native TCP 141.9M rows/s at 8 readers) and 2.35x faster than ClickHouse's fastest streaming configuration (Arrow over HTTP, 93.8M rows/s), on 500M rows; on the 2B-row run QuestDB peaked at 291.9M rows/s (12 readers) vs ClickHouse Arrow HTTP 173.8M and native 165.5M rows/s (16 readers), about 1.68x (derived from page data) |
| **Workload** | Streaming the last 500 million rows of a byte-identical trades table (symbol, side, price, amount, timestamp) out of the database across a 100 Gbps network into Apache Arrow batches in a Python client process, with N parallel reader connections, comparing QuestDB's QWP WebSocket egress (QuestDB 10.0.x) against ClickHouse native TCP (clickhouse-driver execute) and Arrow-over-HTTP (clickhouse-connect query_arrow_stream), with TimescaleDB as a further reference; engines on default settings. |
| **Metric** | throughput |
| **Hardware** | AWS m8gn.8xlarge (32 vCPU, 123GB RAM, 100Gbps) server, c8gn.8xlarge (32 vCPU, 61GB RAM, 100Gbps) client |
| **Adoption** | 17.3k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/questdb/questdb) · [benchmark](https://questdb.com/blog/streaming-500-million-rows-into-apache-arrow/) |

## Verdict

The test streamed the last 500M rows of a 5-column trades table from an m8gn.8xlarge server to a Python client on a c8gn.8xlarge over 100 Gbps, with 8 parallel readers. QuestDB 10.0.0 over QWP reached 220.4M rows/s. The ClickHouse baseline was the unversioned latest Docker image on defaults, with LowCardinality-as-Arrow-dictionary off. Its native TCP path via clickhouse-driver execute() across 8 processes reached 141.9M rows/s (1.55x slower, and it buffers the whole result), and Arrow-over-HTTP reached 93.8M (2.35x). A rebuilt 2B-row rig gave 291.9M vs 173.8M rows/s peak against peak (1.68x). This is a first-party informal test: no CPU model or JVM flags, one schema.

## Use it when

- Pulling tens of millions to billions of raw or downsampled time-series rows into Python (polars, pandas, pyarrow, DuckDB) for model training or feature pipelines, where moving the result set is the bottleneck rather than computing it.
- Streaming consumers that need the first batch fast and flat client memory: 32 ms to the first Arrow batch, against 15.3 s and about 18 GB of client RAM for ClickHouse's buffered native execute() path.
- Tables whose string columns are low-cardinality and can be stored as SYMBOL (tickers, order side, device or sensor IDs). Dictionary encoding brought the wire cost to 18.8 bytes/row, against 27.0 for ClickHouse native and 21.4 for ClickHouse Arrow.
- Client and server on separate hosts on a fast network, with several parallel reader connections (the peak was about 12) and a working set that fits in the server's page cache.
- Workloads that also need high-rate ordered or out-of-order ingestion and time-series SQL in the same engine. The vendor README reports TSBS ingestion of 8.59M rows/s against 1.75M for ClickHouse 26.7.

## Skip it when

- General analytical query speed. On ClickBench (c7a.metal-48xl, both runs dated 2026-09-26), ClickHouse's hot-run total is 3.29 s against QuestDB's 5.40 s, and its cold-run total is 82.2 s against 502.2 s. The egress win does not carry over to query execution.
- Storage- or RAM-constrained hosts. The native format is uncompressed: 15 GiB against ClickHouse's 6.0 GiB for the 500M-row trades table, and 72.9 GB against 9.5 GB on ClickBench. When the working set spilled out of page cache on a 16 GB box, egress fell to 41M rows/s, bound by EBS.
- High-cardinality strings or wide tables. Most of the byte advantage comes from SYMBOL dictionaries, the post says the gap would narrow or disappear without them, and only one 5-column schema was tested.
- Consumers that cannot speak QWP: Node.js (not yet supported), Go and .NET (beta), and Grafana, BI tools or Postgres drivers, which use PGWire and so get none of this speedup.
- Crash-sensitive production egress on 10.0.x today. QWP egress is weeks old, and issue #7667 (open) reports a SIGSEGV in QwpResultBatchBuffer.emitColumnSlice on 10.0.1 that kills the whole JVM on a large 62-column read.

## How it is fast

On the server, QwpResultBatchBuffer copies whole columns out of QuestDB's memory-mapped, time-partitioned native column pages into per-column native scratch buffers, then memcpys them into the wire buffer. The WebSocket header is patched in place afterwards, so the hot path makes no JVM heap allocations. SYMBOL columns go out as a connection-scoped delta dictionary: each string is sent once and each row carries only a varint id (4 bytes/row decoded, against 11.6 bytes for ClickHouse's plain UTF-8). Timestamps use Gorilla delta-of-delta encoding, zstd is optional, and batches hold up to 16,384 rows under credit-based flow control. On the client, the Python decoder releases the GIL and hands wide numeric buffers to Arrow by reference, so parallel reader threads scale as well as processes do (1.00x difference).

## Compared with alternatives

Apache Doris, StarRocks and Umbra also beat ClickHouse, but on query-execution benchmarks (SSB, TPC-H, ClickBench). Pick QuestDB when the bottleneck is time-ordered ingestion plus shipping large result sets into Python/Arrow, not multi-table joins or aggregation throughput; for in-process SQL over dataframes, chDB fits better.

## Integration

| | |
|---|---|
| **Form** | standalone database server (Docker image, Homebrew, JAR/binaries), used through QWP client libraries |
| **Dependencies** | Server: none on the data path (native C++/Rust libraries are bundled in the JAR). Python client: questdb&gt;=5.0 with numpy required; pyarrow and pandas are optional for to_arrow/iter_arrow/to_pandas, and polars/DuckDB read the result through the Arrow PyCapsule interface. |
| **Minimum toolchain** | QuestDB server 10.0+ for QWP egress; building from source needs Java 25 and Maven 3; Python client 5.0 on Python &gt;= 3.10 (the harness used 3.12). |
| **Platforms** | Bundled native libraries for linux x86-64, linux aarch64, macOS aarch64 and windows x86-64. On Intel Macs, Docker only. The benchmark ran on AWS m8gn.8xlarge/c8gn.8xlarge instances; the CPU model is not stated. |
| **Thread safety** | Server handles many concurrent QWP connections. Python client: a reader lease has thread affinity (one lease per thread), and a QueryResult may be handed to another thread but used by only one thread at a time; concurrent consumption, cancel and close are unsupported. Network I/O and decoding release the GIL. |
| **Drop-in for the baseline** | partial — not drop-in for ClickHouse. Different SQL dialect and storage engine, and QWP needs QuestDB's own clients. For Python code that already consumes Arrow batches, the change is limited to the connect/query calls. |

## Gotchas

- iter_arrow()/to_arrow() give each batch its own compacted SYMBOL dictionary, which a generic Arrow consumer then has to reconcile. When the destination is a dataframe, use to_polars()/to_pandas(), which intern the connection's dictionary once.
- A QueryResult is single-use. Closing one before it is drained drops the pooled connection, so to stop early and keep the connection, call cancel() (which blocks while it drains) and then close().
- Parquet-format partitions fall back to a per-row encode path with no columnar memcpy, so the published speed applies to QuestDB's native format. That path also has an open bug (#7507): IPv4 column-tops come back as 128.0.0.0 instead of NULL.
- Several client-side decode steps are not zero-copy: nullable fixed-width columns, booleans, Gorilla timestamps, null bitmaps and zstd batches each take an extra pass. Only wide non-null numeric and VARCHAR buffers are adopted by reference.

## Known shortcomings

- Vendor blog whose own post and harness say it is 'not a benchmark'; the ClickHouse image was unpinned ('latest') and the harness has no license. On ClickBench QuestDB wins only hot runs (5.40 vs 15.70); cold it takes 502 s vs DuckDB's 163 s.
- The win is Arrow egress only; on the same box/date ClickBench has ClickHouse hot 3.29 s vs QuestDB 5.40 s and cold 82.2 s vs 502.2 s. Native storage is uncompressed (15 vs 6.0 GiB for 500M rows; 72.9 vs 9.5 GB on ClickBench); out of page cache it drops to 41M rows/s. The egress win comes mostly from SYMBOL dictionary encoding (one schema tested; high-cardinality strings shrink the gap); ClickHouse ran with LowCardinality-as-dictionary off.
- Open bugs: a 10.0.1 SIGSEGV in QWP emitColumnSlice kills the JVM (#7667); Parquet partitions fall back per row with an IPv4 NULL bug (#7507). The speedup needs QWP clients (none for Node, Go/.NET beta); PGWire tools see no gain.

## Caveats and trade-offs

First-party QuestDB blog (Javier Ramirez); both the post and the harness README say it is 'not a benchmark' but an informal, directional test of the client egress path (Python client, engines on defaults), not an engine ranking. The harness is public but has no license file, pins questdb/questdb:10.0.0 while ClickHouse runs the unversioned clickhouse-server:latest image, and states no CPU model (only m8gn.8xlarge/c8gn.8xlarge instance types) or build flags, so it is capped at C. Separate corroboration: on ClickBench c7a.metal-48xl, QuestDB's hot-run total is 5.40s (2026-09-26 result) vs DuckDB's 15.70s (2026-05-11), but QuestDB is much slower on cold runs (502.2s vs 162.8s) and load (327s vs 98s). These figures are derived from the raw ClickBench JSON.

Result is specific to result-set egress/streaming into Arrow, not general query execution speed; QuestDB is JVM-based (GC pauses, JIT warm-up) vs ClickHouse's native C++; benchmark measures a narrow protocol (QWP) QuestDB just introduced, so it is inherently favorable framing.

## Maintenance

Actively developed and Apache-2.0: 10.0.1 was released 2026-08-24, the last push was 2026-09-26, and the repo has 17.3k stars. QWP egress is new in 10.0, and replication/HA, RBAC, TLS and automatic cold tiering are in the paid Enterprise edition.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party QuestDB blog with a public harness (github.com/javier/questdb_qwp_egress_to_arrow_perf: read_bench_questdb.py, read_bench_clickhouse.py, bench.sh) and stated AWS instance types, but no CPU model, no compiler/JVM flags, and ClickHouse pinned only as the unversioned 'latest' Docker image; the post itself calls it 'not a benchmark... an informal test', so C, not A/B.
- **Verifier notes:** The numbers match the blog exactly. The only field that was wrong was compared_against_cpp_std_directly: the baseline is ClickHouse, not a C++ std library. The ClickBench aside checks out for hot runs only, so I added the cold-run and load gaps to the caveats.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://questdb.com/blog/streaming-500-million-rows-into-apache-arrow/>
  - <https://github.com/questdb/questdb>
  - <https://github.com/javier/questdb_qwp_egress_to_arrow_perf>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/questdb/results/20260926/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
- **Sources the enricher read:**
  - <https://github.com/questdb/questdb>
  - <https://github.com/questdb/questdb/blob/master/core/README.md>
  - <https://github.com/questdb/questdb/releases>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/codec/QwpResultBatchBuffer.java>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/codec/QwpEgressFrameWriter.java>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/codec/QwpEgressConnSymbolDict.java>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/server/egress/QwpEgressUpgradeProcessor.java>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/server/egress/QwpEgressCompressionNegotiator.java>
  - <https://github.com/questdb/questdb/blob/master/core/src/main/java/io/questdb/cutlass/qwp/server/egress/QwpRowExceedsBufferException.java>
  - <https://github.com/questdb/questdb/blob/master/core/rust/qdbr/src/qwp_zstd.rs>
  - <https://github.com/questdb/questdb/issues/7667>
  - <https://github.com/questdb/questdb/issues/7507>
  - <https://github.com/questdb/questdb/issues/7556>
  - <https://questdb.com/blog/streaming-500-million-rows-into-apache-arrow/>
  - <https://questdb.com/blog/questdb-qwp-binary-wire-protocol/>
  - <https://questdb.com/blog/questdb-10-release/>
  - <https://github.com/javier/questdb_qwp_egress_to_arrow_perf>
  - <https://github.com/javier/questdb_qwp_egress_to_arrow_perf/blob/main/read_bench_questdb.py>
  - <https://github.com/javier/questdb_qwp_egress_to_arrow_perf/blob/main/docker-compose.yml>
  - <https://github.com/javier/questdb_qwp_egress_to_arrow_perf/blob/main/requirements.txt>
  - <https://github.com/questdb/py-questdb-client/blob/main/docs/sender.rst>
  - <https://github.com/questdb/py-questdb-client/blob/main/docs/installation.rst>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/questdb/results/20260926/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c7a.metal-48xl.json>
  - <https://api.github.com/advisories?ecosystem=maven&affects=org.questdb:questdb>
  - <https://hn.algolia.com/api/v1/search?query=questdb%20arrow%20500%20million&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/questdb/questdb`) · [data/wave6/enrich/raw/github_com_questdb_questdb.json](../../../data/wave6/enrich/raw/github_com_questdb_questdb.json) (enrichment confidence 0.8)

</details>
