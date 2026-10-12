# TDengine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `AGPL-3.0-only` · 🟢 active

> Clustered C time-series database for IoT; about 8.5x InfluxDB 2.0 and 5.6x TimescaleDB ingest in one rival-run shootout.

| | |
|---|---|
| **Beats** | InfluxDB 2.0 and TimescaleDB 2.6.0 (PostgreSQL 12) |
| **Claimed result** | Write throughput (datapoint/s): TDengine 629,904 vs InfluxDB 74,534 (about 8.5x, derived from page data) and vs TimescaleDB 112,494 (about 5.6x, derived from page data). Read throughput table (Precise_point / Time_range / Agg_range / Group_by / Latest_point): TDengine 59 / 3035 / 60 / 805 / 140 vs InfluxDB 17 / 829 / 17 / 17 / 17 vs TimescaleDB 1 / 63 / 1 / 16 / 1. Memory: TDengine used the smallest RSS, about 500 MB, vs about 1 GB for InfluxDB and nearly the full 4 GB for TimescaleDB. |
| **Workload** | IoTDB-benchmark (Tsinghua THULAB harness, forked by the TickTock author) wind-farm IoT workload, mixed 9:1 write:read, 300 clients x 300 devices x 10 sensors (TimescaleDB 10 clients x 10 devices x 100 sensors), each database in a Docker container pinned to 2 vCPU and 4 GB. |
| **Metric** | throughput |
| **Hardware** | Ideapad gaming laptop: AMD Ryzen 5 5600H (6 cores / 12 threads), 20 GB DDR4-3200, 1 TB 5400 RPM HDD, Ubuntu 20.04.3; benchmark client on the same machine. |
| **Compiler and flags** | Prebuilt Docker images, no compilation: tdengine/tdengine:2.0.22.0, influxdb:2.0, timescale/timescaledb:latest-pg12 (reported as 2.6.0-pg12); docker run --cpuset-cpus 0-1 -m 4g; TimescaleDB max_connections raised. |
| **Adoption** | 25.2k stars; README cites over 730k running instances |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/taosdata/TDengine) · [benchmark](https://raw.githubusercontent.com/wiki/ytyou/ticktock/Performance-comparison:-InfluxDB,-TimescaleDB,-IoTDB,-TDEngine,-OpenTSDB-v.s.-TickTock.md) |

## Verdict

In a one-off wiki shootout by the author of the rival TickTock (its fork of THULAB's IoTDB-benchmark, 9:1 write:read mix, each database in a 2-vCPU / 4 GB Docker container on a Ryzen 5 5600H laptop with a 5400 RPM HDD and the client on the same machine), TDengine 2.0.22.0 ingested 629,904 points/s against InfluxDB 2.0's 74,534 (about 8.5x) and TimescaleDB 2.6.0-pg12's 112,494 (about 5.6x, though TimescaleDB ran 10 clients with 100-sensor batches), using about 500 MB RSS; its average write latency per 100-point batch was 45.4 ms against InfluxDB's 380.95 ms. On query latency TDengine beat InfluxDB clearly (precise-point average 13.35 ms vs 165.15 ms) but trailed TimescaleDB (5.71 ms), and the read-throughput rows mostly mirror the write rate under the fixed operation mix.

## Use it when

- IoT or industrial telemetry: many devices (high cardinality) each emitting a fixed set of metrics at regular intervals, which maps directly onto supertables and per-device subtables.
- High ingest on small machines: in the rival-run shootout TDengine 2.0 took about 630K points/s inside a 2-vCPU, 4 GB container with about 500 MB RSS, the lowest memory of the six databases tested.
- Dashboards that mostly read the current value of each device (LAST/LAST_ROW cache via CACHEMODEL) or downsample with INTERVAL windows.
- You want clustering with Raft-replicated vgroups, stream processing and subscriptions in the open-source edition instead of adding Kafka, Redis or a stream processor.
- Storage cost matters for slowly changing sensor values, where delta, zigzag and delta-of-delta encoding plus a second general-purpose codec compress well.

## Skip it when

- Low-latency point and range queries matter more than ingest: in the same shootout TimescaleDB answered precise-point queries in 5.71 ms on average (median 1.45 ms) against TDengine's 13.35 ms (median 7.94 ms), and agg-range in 7.05 ms against 12.34 ms.
- You need the highest write rate among TSDBs: Apache IoTDB (1.50M points/s) and TickTock (3.20M points/s) both beat TDengine (0.63M) in that run.
- AGPL-3.0 is not acceptable, for example a closed-source product that exposes the database to users over a network.
- Relational or ad hoc analytical workloads (wide joins, arbitrary schemas, PostgreSQL extensions and tooling); TDengine SQL is shaped around per-device tables with a fixed schema.
- Windows production deployments or embedding as an in-process library: the README calls Windows support in the open-source tree limited, and building as a library (BUILD_AS_LIB) is off by default.

## How it is fast

Each device's rows go to its own subtable, and subtables are hashed onto vnodes; each vnode has its own worker thread, WAL, memory pool and storage, so writes for different devices do not contend. Ingest goes WAL then an in-memory MemTable (red-black tree across tables, skip list per table) that is flushed in time-partitioned file groups (an LSM layout), so a block holds one table's data for one time range and the head file acts as a block-range (BRIN) index. Blocks are stored column by column with type-specific primary encoding (delta timestamps, bit-packed booleans, zigzag integers, delta-of-delta floats, dictionary strings) followed by LZ4, zlib, zstd or xz, and an sma file keeps per-block sum/min/max so some aggregates skip the data. An optional last/last_row cache answers current-value queries from memory.

## Compared with alternatives

QuestDB is the other time-series database in this category (Apache-2.0, catalogued for scan throughput against ClickHouse); pick TDengine when the data is per-device IoT telemetry with tags and you want open-source clustering, stream processing and last-value caching, and pick QuestDB when licence or SQL analytics over a few large tables matter more. The other siblings (DuckDB-class engines, Doris, StarRocks, ClickHouse challengers) suit ad hoc analytical SQL rather than continuous device ingest.

## Integration

| | |
|---|---|
| **Form** | server (taosd) plus client shared library libtaos.so (C API) and language connectors; Docker images and installer packages |
| **Dependencies** | bundled external libraries built with -DBUILD_CONTRIB=ON (xxhash, zstd, lz4 and others into .externals/), libuv, RocksDB (prebuilt from deps/ on Linux), GEOS, PCRE2, LZMA2, lemon parser; Go 1.23+ for taosAdapter/taosKeeper; Rust bindings on by default |
| **Minimum toolchain** | CMake &gt;= 3.21 with a GCC/Clang build-essential toolchain; C language standard not documented in the README; note CMAKE_BUILD_TYPE defaults to Debug, so pass -DCMAKE_BUILD_TYPE=Release |
| **Platforms** | Linux (Ubuntu 18.04+, CentOS 7+) on x86-64 and ARM64 as the primary platform; macOS 10.15+ for local development; Windows limited in the open-source tree |
| **Thread safety** | Server is multi-threaded with one worker thread per vnode; client-library thread-safety rules are not documented in the pages read here. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the shootout's per-query read 'throughput' is not an independent measure of query speed. Clients run a closed loop with a fixed 9:1 write:read mix split over five query types, so each query type gets about 1/50 of all operations and its throughput follows the write rate: InfluxDB shows 17 for four query types, and TDengine's latest-point 140 equals its write rate (629,904 points/s over 100 points per batch, times 10/9, over 50; the 100-point batch is consistent with 300 clients at the 45.4 ms average write latency; derived from page data). The 3.5x to 140x read ratios over InfluxDB and TimescaleDB therefore restate the write gap (and TimescaleDB's 10-client setup), while the wiki's own latency tables show TimescaleDB faster than TDengine on precise-point and agg-range queries.
- TDengine's precise-point and agg-range throughput (59 and 60) is well below its latest-point 140, while every other database shows equal values for those three types (InfluxDB 17/17/17, IoTDB 332/332/332, TickTock 712/712/712), which suggests roughly 58% of TDengine's precise-point and agg-range queries returned no rows (derived from page data). A plausible cause is in the fork's TDengine adaptor: inserts format timestamps as second-resolution 'yyyy-MM-dd HH:mm:ss' strings in the JVM's default time zone while the JDBC URL sets timezone=UTC and queries use epoch-millisecond literals; the wiki does not report empty results.
- Second-resolution insert strings also collide when the step between rows is under one second, and TDengine 2.x's default UPDATE 0 discards later rows with an existing timestamp without error while still counting them as affected (2.0 FAQ, search snippet only). The wiki does not publish POINT_STEP (the fork's default config uses 5000 ms, which is safe), but TDengine's reported write I/O of 100-300 KB/s at 630K points/s works out to under 0.5 bytes per point, against about 6.7 for InfluxDB (derived from page data), which is unexplained.
- The adaptor sends an extra 'use &lt;db&gt;' statement before every insert and every query (an extra round trip that penalizes TDengine), runs through taos-jdbcdriver 2.0.32 with HikariCP, and the wiki notes TDengine still had 10-20% CPU headroom; all figures are for the 2.0.22.0 image, while the current line is 3.4.x with a different storage engine and cluster design.

## Known shortcomings

- TickTock wiki shootout by a rival's author (one-off, old TDengine 2.0.22.0 on an HDD laptop) in which TickTock and IoTDB both beat TDengine; workloads unequal (TimescaleDB batch 100, TDengine 1M loops vs 100K). The arXiv 2301.12561 claim is unconfirmed (the snippet says the paper tested ClickHouse, InfluxDB, kdb+ and TimescaleDB only); vendor TSBS reports on tdengine.com were blocked.
- Enricher: the TickTock wiki's read 'throughput' rows are a closed-loop artifact (9:1 mix with each query type about 1/50 of operations), so they restate the write rate, and the wiki's own latency tables show TimescaleDB faster than TDengine (precise-point avg 5.71 vs 13.35 ms; agg-range 7.05 vs 12.34 ms); TDengine's precise-point/agg-range counts (59/60 vs latest-point 140) suggest about 58% of those queries returned empty (derived), plausibly from second-resolution timestamps in the JVM default timezone against JDBC timezone=UTC; 2.x UPDATE 0 silently drops duplicate timestamps; the adaptor adds a 'use db' round trip per operation. Lead: TickTock (ytyou/ticktock).

## Caveats and trade-offs

Numbers come from a third-party wiki written by the author of a rival time-series database (TickTock), who wins the same chart; Apache IoTDB (1,495,065 datapoint/s) also beats TDengine there, so TDengine is only faster than InfluxDB, TimescaleDB and OpenTSDB. The TDengine, InfluxDB and TimescaleDB figures are read from the wiki's result images (througput_w.jpg and througput_tbl.jpg in the ylin30/ticktock-wiki repo, both opened and matching); the table header is cropped ('Throughput(Da...'), so the read rows' unit is not certain. Old versions (TDengine 2.0.22.0 from the 2.x line, InfluxDB 2.0, TimescaleDB latest-pg12 reported as 2.6.0) on a laptop with a 5400 RPM HDD, each database in a 2-vCPU, 4 GB Docker container with the benchmark client on the same machine. Workloads were not equal: TimescaleDB ran 10 clients x 10 devices x 100 sensors (write batch 100 instead of 10, which the wiki itself calls unfair to the others), and TDengine ran 1M loops versus 100K for InfluxDB and TimescaleDB. The harness is the TickTock author's fork of IoTDB-benchmark (github.com/ytyou/iotdb-benchmark, public) with connection pools added to the InfluxDB 2.0, TDengine and OpenTSDB clients; its README lists a TDengine 2.2.0.2 adaptor while the run used the 2.0.22.0 image. TDengine's own TSBS reports on tdengine.com (blocked here, search snippet only) claim ingestion 1.5x to 6.7x faster than TimescaleDB and 3.0x to 10.6x faster than InfluxDB, using the public taosdata/tsbs fork (scripts/tsdbComp); these are vendor numbers. The arXiv paper 'Benchmarking Specialized Databases for High-frequency Data' (2301.12561) is, per search snippets, a benchmark of ClickHouse, InfluxDB, kdb+ and TimescaleDB, so the earlier claim that it reports TDengine at 1.63M rows/s could not be confirmed and should not be relied on. [retier] TickTock wiki shootout by a rival's author (one-off, TDengine 2.0.22.0 on an HDD laptop, IoTDB-benchmark fork) in which TickTock and IoTDB both beat TDengine; workloads unequal (TimescaleDB batch 100, TDengine 1M loops vs 100K). The read 'throughput' rows are a closed-loop artifact (9:1 mix, each query type about 1/50 of operations) and restate the write rate; the wiki's own latency tables show TimescaleDB faster than TDengine (precise-point avg 5.71 vs 13.35 ms, agg-range 7.05 vs 12.34 ms), and TDengine's precise-point/agg-range counts (59/60 vs latest-point 140) suggest about 58% of those queries returned empty (derived), plausibly from second-resolution timestamps in the JVM default timezone against JDBC timezone=UTC; the adaptor adds a 'use db' round trip per operation. The arXiv 2301.12561 claim is unconfirmed (its snippet lists ClickHouse, InfluxDB, kdb+ and TimescaleDB only); vendor TSBS reports on tdengine.com were blocked.

AGPL-3.0 copyleft (network-use clause) for the open-source tree. Time-series specific data model (super tables and sub-tables per device) and TDengine SQL rather than a general SQL engine. README says Linux is the primary platform, with limited Windows support in the open-source tree.

## Maintenance

Actively developed (25.2k stars, about 87k commits on main, last commit 2026-09-02, releases in the 3.4.x line) by TDengine's vendor under AGPL-3.0; the only numbers here are from a 2.x-era rival shootout, so re-benchmark the 3.x engine on your own workload, or use the vendor's public TSBS fork (taosdata/tsbs), before relying on the ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The only opened numbers come from a rival TSDB author's one-off wiki shootout (TickTock wins it, IoTDB also beats TDengine) on a modified fork of IoTDB-benchmark (ytyou/iotdb-benchmark, public), with the CPU model and Docker image versions stated but prebuilt images and unequal per-database workloads; per the xan, winnow and FEX precedents a competitor's shootout is not a well-known independent suite, so C rather than B. TDengine's own TSBS reports on tdengine.com are vendor evidence (C) and could not be opened (EGRESS_BLOCKED).
- **Verifier notes:** All claimed write, read and memory figures match the wiki text and its images exactly; downgraded B to C because the measurement is a competitor's one-off shootout with unequal workloads (TimescaleDB batch 100, TDengine 10x more loops), old versions and prebuilt images. Shortcomings to record: rival-run shootout where TickTock and IoTDB beat TDengine; unequal per-database workload shapes; 2.x-era versions on an HDD laptop; vendor TSBS reports unopened. Category columnar-analytics is a better fit than the assignment's message-queues-logs; metadata (25.2k stars, AGPL-3.0, last commit 2026-09-02 on main, 730k running instances in README) confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** rival TickTock wiki (verifier downgrade B to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/ytyou/ticktock/Performance-comparison:-InfluxDB,-TimescaleDB,-IoTDB,-TDEngine,-OpenTSDB-v.s.-TickTock.md>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/througput_w.jpg>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/througput_tbl.jpg>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/througput_r.jpg>
  - <https://github.com/taosdata/TDengine>
  - <https://github.com/taosdata/TDengine/commits>
  - <https://github.com/ytyou/iotdb-benchmark>
  - <https://github.com/taosdata/tsbs>
  - <https://github.com/taosdata/tsbs/tree/master/scripts/tsdbComp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/taosdata/TDengine/HEAD/README.md>
  - <https://github.com/taosdata/TDengine>
  - <https://github.com/taosdata/TDengine/releases>
  - <https://github.com/taosdata/TDengine/tree/main/docs/en>
  - <https://github.com/taosdata/TDengine/tree/main/docs/en/15-internals>
  - <https://raw.githubusercontent.com/taosdata/TDengine/main/docs/en/15-internals/01-arch.md>
  - <https://raw.githubusercontent.com/taosdata/TDengine/main/docs/en/15-internals/02-storage.md>
  - <https://raw.githubusercontent.com/taosdata/TDengine/main/docs/en/15-internals/07-cache.md>
  - <https://raw.githubusercontent.com/taosdata/TDengine/main/docs/en/15-internals/08-compress.md>
  - <https://github.com/taosdata/TDengine/issues?q=is%3Aissue+is%3Aopen+memory+leak>
  - <https://raw.githubusercontent.com/wiki/ytyou/ticktock/Performance-comparison:-InfluxDB,-TimescaleDB,-IoTDB,-TDEngine,-OpenTSDB-v.s.-TickTock.md>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/througput_tbl.jpg>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/resptime_precise_point_tbl.jpg>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/resptime_agg_range_tbl.jpg>
  - <https://raw.githubusercontent.com/ylin30/ticktock-wiki/master/perf/x86-iotdb/rw1_9/resptime_w_tbl.jpg>
  - <https://github.com/ytyou/iotdb-benchmark>
  - <https://github.com/ytyou/iotdb-benchmark/tree/master/tdengine>
  - <https://raw.githubusercontent.com/ytyou/iotdb-benchmark/master/tdengine/pom.xml>
  - <https://github.com/ytyou/iotdb-benchmark/tree/master/tdengine/src/main/java/cn/edu/tsinghua/iotdb/benchmark/tdengine>
  - <https://raw.githubusercontent.com/ytyou/iotdb-benchmark/master/tdengine/src/main/java/cn/edu/tsinghua/iotdb/benchmark/tdengine/TDengine.java>
  - <https://github.com/ytyou/iotdb-benchmark/tree/master/configuration/conf>
  - <https://raw.githubusercontent.com/ytyou/iotdb-benchmark/master/configuration/conf/config.properties>
  - <https://github.com/ytyou/ticktock>
  - WebSearch snippet: TDengine 2.0 FAQ (docs.tdengine.com/2.0/faq, not opened) says with UPDATE 0 later rows with the same timestamp are discarded without error and still counted in affected rows
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/taosdata/tdengine`) · [data/wave6/enrich/raw/github_com_taosdata_tdengine.json](../../../data/wave6/enrich/raw/github_com_taosdata_tdengine.json) (enrichment confidence 0.7)

</details>
