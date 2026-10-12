# Columnar analytics

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md)</sub>

**What these beat:** Apache Arrow, DuckDB, ClickHouse, pandas, polars  
**36 entries:** 4 tier A · 12 tier B · 20 tier C · 0 tier D · 30 copyable, 6 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**ALP (Adaptive Lossless Floating-Point Compression)**](cwida-alp.md) | Reference C++ primitives for ALP, a lossless double/float column encoding that decodes 17-66x faster than Zstd, Gorilla, Chimp and Patas. | **A** | C++ | MIT | 🟢 active |
| 2 | [**Minarrow**](spacecell-minarrow.md) | Lean Rust Apache Arrow implementation with enum-dispatched typed arrays; about 1.7x faster than arrow-rs on a 1,000-element sum microbenchmark. | **A** | Rust | Apache-2.0 | 🟢 active |
| 3 | [**GenDB**](solidlao-gendb.md) | LLM-agent pipeline that writes a custom C++ executable per SQL query; 2.8x faster than DuckDB on 5 TPC-H queries. | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**Bespoke OLAP**](datamanagementlab-bespokeolap.md) | LLM agent that writes an in-memory C++ OLAP engine per fixed SQL workload; beats DuckDB and Umbra. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 5 | [**Apache DataFusion**](apache-datafusion.md) | Embeddable Rust/Arrow SQL query engine; on ClickBench hot runs over Parquet on a 192-vCPU box, 1.56x faster than DuckDB. | **B** | Rust | Apache-2.0 | 🟢 active |
| 6 | [**Velox**](facebookincubator-velox.md) | Meta's C++ vectorized execution-engine library; as Presto's C++ worker it ran 3TB TPC-H queries 2-9x faster than Presto Java. | **B** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**data.table (R)**](rdatatable-data-table.md) | R's in-memory data.frame replacement with C/OpenMP radix grouping and joins; \~3-4x faster than pandas on db-benchmark groupby. | **B** | C | MPL-2.0 | 🟢 active |
| 8 | [**chDB**](chdb-io-chdb.md) | In-process ClickHouse SQL engine for Python that queries pandas DataFrames directly; median \~166x faster than pandas on ClickBench. | **B** | C++ | Apache-2.0 | 🟢 active |
| 9 | [**FastLanes**](cwida-fastlanes.md) | CWI's columnar file format with SIMD-friendly lightweight encodings; decodes 7-44x faster than Parquet, DuckDB and BtrBlocks in its paper. | **B** | C++ | MIT | 🟢 active |
| 10 | [**Cylon**](cylondata-cylon.md) | C++/Arrow distributed-memory dataframe engine on MPI/UCX/Gloo that scales join, groupby and aggregation past serial pandas. | **B** | C++ | Apache-2.0 | 🟢 active |
| 11 | [**Xorbits**](xorbitsai-xorbits.md) | Distributed pandas/NumPy-API engine built on Mars. On 100 GB-1 TB TPC-H it beats Dask DataFrame, Modin and pandas-on-Spark. | **B** | Python | Apache-2.0 | 🟡 stale |
| 12 | [**BtrBlocks**](maxi-k-btrblocks.md) | C++ columnar compression library: sampled cascades of lightweight encodings; authors measured 2.6-3.8x faster decompression than Parquet. | **B** | C++ | MIT | 🟡 stale |
| 13 | [**Crystal (GPU query-processing library)**](anilshanbhag-crystal.md) | Header-only CUDA library of block-wide device functions for hand-writing fused SQL query kernels; about 16x faster than OmniSci on SSB. | **B** | C++ | MIT | 🔴 abandoned |
| 14 | [**Databend**](databendlabs-databend.md) | Rust SQL data warehouse over object storage; \~1.6x faster than DuckDB on ClickBench hot runs on 192-vCPU hardware. | **B** | Rust | Apache-2.0 (core) +… (study only) | 🟢 active |
| 15 | [**Firebolt Core**](firebolt-db-firebolt-core.md) | Firebolt's free self-hosted distributed SQL engine (ClickHouse-derived runtime); beats DuckDB on ClickBench hot runs, roughly ties ClickHouse. | **B** | C++ | Elastic License 2.0 (study only) | 🟢 active |
| 16 | [**Umbra**](paper-umbra.md) | Closed-source TU Munich research SQL database (HyPer successor) that runs ClickBench about 2.4x faster than ClickHouse on one node. | **B** | C++ | proprietary (study only) | 🟢 active |
| 17 | [**TDengine**](taosdata-tdengine.md) | Clustered C time-series database for IoT; about 8.5x InfluxDB 2.0 and 5.6x TimescaleDB ingest in one rival-run shootout. | **C** | C | AGPL-3.0-only | 🟢 active |
| 18 | [**QuestDB**](questdb-questdb.md) | Java/C++/Rust time-series database whose QWP protocol streams query results into Arrow 1.55x faster than ClickHouse's fastest client path. | **C** | Java | Apache-2.0 | 🟢 active |
| 19 | [**Apache Doris**](apache-doris.md) | MPP SQL analytics database (Java FE, C++ vectorized BE); vendor sf1000 runs show 5-11x faster than ClickHouse on join-heavy benchmarks. | **C** | C++ | Apache-2.0 | 🟢 active |
| 20 | [**StarRocks**](starrocks-starrocks.md) | Distributed MPP SQL OLAP database with C++ vectorized engine; vendor SSB-Flat test shows 1.87x over ClickHouse, ClickBench shows the reverse. | **C** | C++ | Apache-2.0 | 🟢 active |
| 21 | [**Modin**](modin-project-modin.md) | Parallel, partitioned pandas API on Ray, Dask or MPI; wins over pandas on heavy single ops, loses on small ones. | **C** | Python | Apache-2.0 | 🟢 active |
| 22 | [**cuDF (cudf.pandas)**](rapidsai-cudf.md) | NVIDIA GPU DataFrame library; cudf.pandas runs unmodified pandas code on NVIDIA GPUs, 50-290x faster in vendor join/groupby benchmarks. | **C** | C++ | Apache-2.0 | 🟢 active |
| 23 | [**Lance**](lance-format-lance.md) | Rust columnar file and table format for AI/ML data, built for random row access where default-configured Parquet is slow. | **C** | Rust | Apache-2.0 | 🟢 active |
| 24 | [**Vortex**](vortex-data-vortex.md) | Rust columnar file format and compressed-array toolkit that aims to replace Parquet for scans, writes and random access. | **C** | Rust | Apache-2.0 | 🟢 active |
| 25 | [**Ladybug**](ladybugdb-ladybug.md) | Embedded columnar Cypher graph database (the continuation of Kuzu), about 2x lower geomean read-query latency than a server Neo4j. | **C** | C++ | MIT | 🟢 active |
| 26 | [**Sirius**](sirius-db-sirius.md) | DuckDB extension that runs DuckDB's SQL plans on NVIDIA GPUs via libcudf; vendor TPC-H hot runs 2.7-5.7x faster than DuckDB. | **C** | C++ | Apache-2.0 | 🟢 active |
| 27 | [**clickhouse-cpp**](clickhouse-clickhouse-cpp.md) | Official C++17 native-protocol ClickHouse client; reads columnar blocks far faster than HTTP, JDBC, Python or reflection-based Go clients. | **C** | C++ | Apache-2.0 | 🟢 active |
| 28 | [**Bodo DataFrames**](bodo-ai-bodo.md) | Pandas-API DataFrame library and Numba-based JIT compiling pandas code to MPI-parallel native code; beats Polars on a UDF-heavy vendor benchmark. | **C** | Python | Apache-2.0 | 🟢 active |
| 29 | [**csvql**](melihbirim-csvql.md) | Zig CLI and MCP server that runs read-only SQL on raw CSV files, about 3x faster than DuckDB's raw-CSV path. | **C** | Zig | MIT | 🟢 active |
| 30 | [**Tessera**](bpmcginley-tessera.md) | Small .NET 9 columnar library whose sorted merge-sweep as-of join is about 14x faster than pandas.merge_asof on 1M x 1M rows. | **C** | C# | MIT | 🟢 active |
| 31 | [**Hydra Columnar (Postgres columnar extension)**](hydradatabase-columnar.md) | Postgres table-access-method extension (Citus Columnar fork) adding compressed columnar storage, parallel scans, vectorized filters; \~23x vs heap on ClickBench. | **C** | C | AGPL-3.0 (the columnar… | 🟡 stale |
| 32 | [**Parquet Sort (Earnix)**](earnix-parquet-sort.md) | Java CLI that sorts a flat Parquet file by one column; 1.12-1.26x faster than DuckDB on TPC-H lineitem. | **C** | Java | Apache-2.0 | 🟡 stale |
| 33 | [**TensorBase**](tensorbase-tensorbase.md) | Abandoned Rust ClickHouse-protocol server on forked DataFusion; 3.1x faster than ClickHouse on plain sum, 6.7x slower on group-by. | **C** | Rust | Apache-2.0 | 🔴 abandoned |
| 34 | [**FireDucks**](fireducks-dev-fireducks.md) | NEC's closed-source drop-in for pandas: lazy IR optimization plus multithreaded Arrow kernels; first-party TPC-H SF10 claims 141x. | **C** | Python | BSD-3-Clause (study only) | 🟢 active |
| 35 | [**tickdb (DerekNest)**](dereknest-tickdb.md) | Rust tick-trade store: delta-of-delta/varint+zstd segments \~20% smaller than Parquet+zstd, but slower than DuckDB on ingest and all queries. | **C** | Rust | no license (study only) | 🟢 active |
| 36 | [**JetStream**](paper-jetstream.md) | MIT research prototype: LLM agents generate query-specific accelerators that plug into DuckDB or PostgreSQL; claims 833x geomean over single-threaded DuckDB. | **C** | C++ | no license (study only) | ⚪ unknown |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
