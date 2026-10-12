# Vortex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust columnar file format and compressed-array toolkit that aims to replace Parquet for scans, writes and random access.

| | |
|---|---|
| **Beats** | Apache Parquet |
| **Claimed result** | bench.vortex.dev (live page, build 737386b as of 2026-09-26). Two figures are geomean throughput ratios to Parquet: write throughput 2.97x (1,756 vs 605 MB/s) and scan throughput 30.73x (84.14 vs 3.20 GB/s). The page's other summary ratios are geomean time ratios to the fastest entry (lower is better), not speedups over Parquet. Random access, hot: Vortex 1.15x (1.85 ms) vs Parquet 627.08x (65.32 s), about 545x (derived from page data). Random access, cold: Vortex 1.35x (3.31 ms) vs Parquet 432.76x (67.10 s), about 321x (derived from page data). ClickBench: DataFusion+Vortex 3.99 s vs DataFusion+Parquet 6.08 s, about 1.52x (derived from page data); DuckDB+Vortex 4.65 s vs DuckDB+Parquet 5.45 s, about 1.17x (derived from page data). TPC-H SF1 NVMe: DuckDB+Vortex 450.40 ms vs DuckDB+Parquet 1.51 s, about 3.35x (derived from page data). |
| **Workload** | First-party CI benchmark dashboard (bench.vortex.dev) covering write and scan throughput (compress-bench), hot and cold random-access take latency over taxi, feature-vectors, nested-lists and nested-structs datasets, ClickBench, TPC-H SF1/10/100 on NVMe and S3, TPC-DS SF1 and others. Each workload runs with both DataFusion and DuckDB as the query engine, against Parquet, Lance, Arrow IPC and DuckDB native formats. |
| **Metric** | throughput |
| **Hardware** | Not stated on the page. The repo's CI workflows (.github/workflows/develop-bench.yml, sql-bench-matrix.yml) run benchmarks on an AWS EC2 c8gd.metal-24xl (ARM64); no CPU model is named. |
| **Compiler and flags** | Not stated on the page. Per the repo's CI workflow: rustc 1.98.0 (rust-toolchain.toml), RUSTFLAGS='-C target-cpu=native -C force-frame-pointers=yes', cargo --profile release_debug. |
| **Adoption** | 3,225 stars; LF AI & Data incubation-stage project |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/vortex-data/vortex) · [benchmark](https://bench.vortex.dev) |

## Verdict

Vortex's own CI dashboard (bench.vortex.dev build 737386b; AWS c8gd.metal-24xl ARM64 per the workflows; rustc 1.98 with target-cpu=native) reports geomean write throughput of 1,756 vs 605 MB/s and scan throughput of 84.1 vs 3.2 GB/s against parquet-rs 59 with default ZSTD, plus hot take latency of 1.85 ms vs 65 s. These are not per-core comparisons: the Vortex side runs on a multi-threaded Tokio runtime with a writer that compresses on all cores, while the Parquet side uses parquet-rs's synchronous ArrowWriter and reader. End-to-end query gains are smaller and mixed: ClickBench on NVMe is 3.99 vs 6.08 s with DataFusion and 4.65 vs 5.45 s with DuckDB, TPC-H S3 SF100 is 6.7x slower with DuckDB, and independent ClickBench runs on c6a.4xlarge are mixed to negative.

## Use it when

- Write-once, scan-many analytics tables that you query through DuckDB or DataFusion on local NVMe. On the dashboard, TPC-H SF1 on NVMe takes 450 ms with DuckDB+Vortex vs 1.51 s with DuckDB+Parquet.
- Point lookups and sparse row fetches (take) over columnar data such as feature vectors, taxi trips or nested lists/structs, where Parquet's lack of row-level random access hurts. Hot take is 1.85 ms vs 65 s for Parquet and 3.57 ms for Lance.
- Rust data systems or custom storage engines that want Arrow-compatible arrays with compressed-domain compute, plus pluggable encodings, layouts and storage backends (local disk, object stores).
- Bulk ingest or conversion on many-core machines, where the parallel writer can use every core. The dashboard shows 1,756 MB/s vs 605 MB/s for parquet-rs, with the threading caveat below.
- GPU decode pipelines on Linux, using the optional CUDA feature that decodes Vortex files on the device.

## Skip it when

- As an interchange format for arbitrary consumers. Parquet is readable almost everywhere, while Vortex needs its own library or extension. Iceberg support is still 'coming soon', and DuckDB extension updates need DuckDB maintainers to redeploy, so they can lag Vortex releases by days.
- Large queries over S3 with DuckDB. On the same dashboard, TPC-H S3 SF100 takes 488.6 s with DuckDB+Vortex vs 73.5 s with DuckDB+Parquet, and at S3 SF1 DataFusion+Parquet is fastest. Independent ClickBench runs are mixed to negative (DataFusion+Vortex 91.3 s vs 45.6 s for Parquet, Aug 2026). The project's own epic #7716 lists ClickBench, TPC-H and TPC-DS queries where it still loses to Parquet.
- Memory-constrained ingest through DuckDB. In #10046, COPY ... (FORMAT vortex) of ClickBench hits was OOM-killed on a 7.6 GiB host regardless of memory_limit, because Vortex allocations are invisible to DuckDB's accounting. The C, C++ and DuckDB write paths are effectively single-threaded (#8760). An independent May 2026 test also hit OOM reading directories of Vortex files through the DuckDB extension.
- Many small writes. In #5861, writing RecordBatches under about 1,000 rows was 20-30x slower than Parquet, although that test used uncompressed Parquet.
- When smallest file size is the goal. The dashboard's geomean Vortex file size is 1.07x Parquet-zstd (range 0.55x to 1.43x); the 'compact' strategy trades read speed for size. Also, the Rust and C++ APIs still change between 0.x releases, and the Scan API is marked as under development.

## How it is fast

Each chunk gets its own chain of lightweight encodings, chosen by a BtrBlocks-style sampling compressor. Integers use FastLanes SIMD bit-packing, frame-of-reference, delta and RLE; floats use ALP/ALPrd; strings use FSST. Dictionary, run-end and sparse encodings apply across types, and zstd/PCodec are kept for the size-oriented 'compact' strategy. Arrays are lazy trees of encodings, so filters, takes and comparisons run directly on compressed data when a kernel exists, and data is fully decoded only when no kernel does. The DuckDB integration can hand FSST strings to DuckDB without decompressing them. The default file layout keeps min/max/null-count zone maps every 8k rows for pruning and targets segments of about 1 MB, a size chosen for S3 request sizing. The writer compresses chunks in parallel across all available cores, and footer metadata is zero-copy and zero-parse.

## Compared with alternatives

Pick Vortex over Lance for SQL analytics through DuckDB or DataFusion when file size matters. On Vortex's own dashboard, Lance files are 2.11x Parquet size vs 1.07x for Vortex, and Lance trails on write, scan and take (first-party numbers). Velox, StarRocks, Umbra and Sirius are query engines, not formats: Vortex sits underneath an engine such as DuckDB, DataFusion or Spark rather than replacing one.

## Integration

| | |
|---|---|
| **Form** | crate (vortex on crates.io). Also a PyPI module (vortex-data), a Maven Spark package, a DuckDB extension, and C/C++ libraries built from source with CMake as static or shared libs. |
| **Dependencies** | The workspace pins arrow-rs 59.x, flatbuffers, fastlanes, fsst-rs, zstd, pco, object_store and tokio. Engine integrations use DataFusion 55 or DuckDB 1.5. The C/C++ bindings need CMake 3.25+ and Cargo/rustc on PATH; nanoarrow provides optional Arrow interop. The README recommends mimalloc as the global allocator. |
| **Minimum toolchain** | Rust 1.95 MSRV (edition 2024), with CI building on 1.98. The C++ bindings need a C++20 compiler and CMake 3.25+. |
| **Platforms** | Rust crate platforms are not documented. The C/C++ bindings build natively only on Linux x86-64/aarch64 and macOS arm64; Windows, musl, cross-compilation and universal binaries are unsupported. The CUDA path is Linux-only. |
| **Thread safety** | Scans produce independent splits/partitions meant for parallel consumption, and arrays, dtypes and expressions are reference-counted and cheap to clone. The FFI runs on caller threads unless you set vx_runtime_set_worker_threads. Open bug #9817: a Vortex CurrentThreadRuntime driven inside tokio block_on can stall forever. |
| **Drop-in for the baseline** | partial — it is Arrow-compatible in memory and plugs into DuckDB, DataFusion, Spark and Polars, but data must be converted from Parquet, there is no Parquet API compatibility, and every reader needs Vortex support. |

## Gotchas

- Backward compatibility covers only files written by 0.36.0 or later. The default session writes the newest frozen edition, so a library upgrade can produce files that older readers cannot open. Pin an edition when readers lag behind writers.
- Open correctness bugs: #9205 (null children of a nullable struct leak into zone maps, so is_null filters can prune valid zones and return wrong results) and #9836 (sum overflow handled incorrectly in the DuckDB integration). Fuzzing has found panics on malformed files (#8848, #8823), so isolate untrusted inputs.
- Memory: take on an FSST string array grew 19 MB into 2 GB (#4784), and buffer allocations bypass host-engine memory limits until the BufferAllocator work (#9674) lands.
- C++ API: the Writer must call finish() or the file is corrupt. Literals need an explicit type, as in lit&lt;uint16_t&gt;(180), because there is no type coercion; a plain lit(180) fails at runtime.

## Known shortcomings

- The vendor's 1.13x/1.32x/627x are ratios to the fastest entry, not vs Parquet; derived vs Parquet: DataFusion 1.52x, DuckDB 1.17x, TPC-H SF1 3.35x, hot random access \~545x. Write 2.97x and scan 30.73x hold. Official ClickBench contradicts it: DataFusion+Vortex 91.3 s vs DataFusion+Parquet 45.6 s; DuckDB+Vortex is slower summed and only \~5% faster by geomean.
- Write/scan ratios are not per-core: the Vortex writer compresses on all cores while the parquet-rs side is single-threaded. On S3 at SF100, DuckDB+Vortex took 488.6 s vs 73.5 s for Parquet; epic #7716 lists losing queries. Files are \~1.07x Parquet-zstd size (0.55-1.43x), not smaller.
- Open correctness bugs: a zone-map null leak can prune valid zones (#9205), DuckDB sum overflow (#9836), panics on malformed files. DuckDB COPY OOM (#10046); C/C++/DuckDB writers are single-threaded (#8760); small-batch writes 20-30x slower (#5861). The default session writes the newest file edition, so a library upgrade can break older readers; 0.x API churn; C++ bindings are source-only on Linux/macOS-arm64.

## Caveats and trade-offs

First-party dashboard whose numbers change with every commit. Most summary 'x' figures are geomean ratios to the fastest entry, not speedups over Parquet, so only the write and scan throughput ratios are direct Parquet comparisons. On the same page, results on S3 are mixed. At TPC-H S3 SF1, DataFusion+Parquet is fastest (6.54 s vs DataFusion+Vortex 8.86 s). At TPC-H S3 SF100, DuckDB+Vortex takes 488.62 s vs 73.45 s for DuckDB+Parquet. The independent ClickHouse/ClickBench results (c6a.4xlarge, sum of best-of-3 over 43 queries, derived from the result JSONs) are also mixed. On 2026-05-11, duckdb-vortex took 40.99 s vs 32.48 s for duckdb-parquet: slower in total because one query is about 20x slower, though it was faster on 26 of 43 queries and about 5% faster by geomean. A 'tuned' duckdb-vortex run on 2026-09-26 took 29.69 s but loaded in 762 s. On 2026-08-20, DataFusion+Vortex took 91.30 s vs 45.57 s for DataFusion+Parquet and was about 1.37x slower by geomean. That contradicts the dashboard's DataFusion ClickBench win, although the engine versions differ (Vortex CLI on DataFusion 53.1.0, Parquet run on 54.0.0). The huge random-access ratios mostly reflect Parquet having no row-level random access.

Rust-native (needs FFI/bindings for direct C++ use, though it advertises zero-copy Arrow compatibility); file format only reached 'stable' status from v0.36.0 onward; young ecosystem versus Parquet's universal tooling support.

## Maintenance

Very active: commits land daily, 0.86.1 shipped on 2026-09-11, and 0.x releases come every two to three weeks. It is Apache-2.0 and an LF AI & Data incubation project; the file format has been stable since 0.36.0, but library APIs still change between releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** bench.vortex.dev is Vortex's own CI dashboard. It compares against Parquet, and the benchmark code is public (benchmarks/compress-bench, random-access-bench, datafusion-bench, duckdb-bench). The page names no hardware or flags. The CI workflows give an AWS instance type (c8gd.metal-24xl), RUSTFLAGS and rustc 1.98.0, but no CPU model, so per precedent this is first-party C.
- **Verifier notes:** The record misread the dashboard. Its 1.13x (ClickBench) and 1.32x (TPC-H) figures are ratio-to-fastest scores, not speedups over Parquet, and the Parquet 65.32 s random-access figure is from the hot panel, not a cold/hot mix. I rewrote claimed_speedup with the direct comparisons, marked as derived. I downgraded because the query-engine wins over Parquet are contested by independent ClickBench results, including a new DataFusion+Vortex result that is 2x slower in total. The write and scan throughput wins stand, first-party only.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://bench.vortex.dev>
  - <https://github.com/vortex-data/vortex>
  - <https://raw.githubusercontent.com/vortex-data/vortex/develop/benchmarks/random-access-bench/README.md>
  - <https://raw.githubusercontent.com/vortex-data/vortex/develop/.github/workflows/develop-bench.yml>
  - <https://raw.githubusercontent.com/vortex-data/vortex/develop/.github/workflows/sql-bench-matrix.yml>
  - <https://raw.githubusercontent.com/vortex-data/vortex/develop/.github/workflows/nightly-bench.yml>
  - <https://raw.githubusercontent.com/vortex-data/vortex/develop/rust-toolchain.toml>
  - <https://github.com/ClickHouse/ClickBench>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-vortex/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-parquet/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb-vortex-tuned/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion-vortex/results/20260820/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/results/20260820/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion-vortex/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion-vortex/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/datafusion/install>
- **Sources the enricher read:**
  - <https://github.com/vortex-data/vortex>
  - <https://github.com/vortex-data/vortex/releases>
  - <https://github.com/vortex-data/vortex/blob/develop/Cargo.toml>
  - <https://github.com/vortex-data/vortex/blob/develop/lang/cpp/README.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/getting-started/cpp.rst>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-ffi/README.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/concepts/file-format.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/concepts/layouts.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/concepts/scanning.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/concepts/arrays.md>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-btrblocks/README.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/specs/editions.md>
  - <https://github.com/vortex-data/vortex/blob/develop/docs/specs/versioning.md>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-duckdb/README.md>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-file/src/strategy.rs>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-layout/src/layouts/compressed.rs>
  - <https://github.com/vortex-data/vortex/blob/develop/benchmarks/compress-bench/README.md>
  - <https://github.com/vortex-data/vortex/blob/develop/benchmarks/compress-bench/src/parquet.rs>
  - <https://github.com/vortex-data/vortex/blob/develop/benchmarks/compress-bench/src/vortex.rs>
  - <https://github.com/vortex-data/vortex/blob/develop/benchmarks/compress-bench/src/main.rs>
  - <https://github.com/vortex-data/vortex/blob/develop/vortex-bench/src/lib.rs>
  - <https://github.com/vortex-data/vortex/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/vortex-data/vortex/issues/5861>
  - <https://github.com/vortex-data/vortex/issues/7716>
  - <https://github.com/vortex-data/vortex/issues/10046>
  - <https://github.com/vortex-data/vortex/issues/8760>
  - <https://github.com/vortex-data/vortex/issues/7735>
  - <https://github.com/vortex-data/vortex/issues/9674>
  - <https://github.com/vortex-data/vortex/issues/9205>
  - <https://github.com/vortex-data/vortex/issues/9836>
  - <https://github.com/vortex-data/vortex/issues/9817>
  - <https://github.com/vortex-data/vortex/issues/4784>
  - <https://github.com/vortex-data/vortex/issues/8848>
  - <https://bench.vortex.dev>
  - <https://hn.algolia.com/api/v1/search?query=vortex%20file%20format&tags=story>
  - <https://dataengineeringcentral.substack.com/p/benchmarking-vortex-file-format-vs>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/vortex-data/vortex`) · [data/wave6/enrich/raw/github_com_vortex_data_vortex.json](../../../data/wave6/enrich/raw/github_com_vortex_data_vortex.json) (enrichment confidence 0.78)

</details>
