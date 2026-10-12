# tickdb (DerekNest)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Rust tick-trade store: delta-of-delta/varint+zstd segments \~20% smaller than Parquet+zstd, but slower than DuckDB on ingest and all queries.

| | |
|---|---|
| **Beats** | Parquet (zstd-compressed) |
| **Claimed result** | Not faster on any speed axis. Storage: 6.50 bytes/trade vs 8.13 for Parquet+zstd, which the page itself calls 'genuinely 20% smaller'. Ingest: 7.32M rows/s (1 run) vs DuckDB CSV load at 20.05-20.67M rows/s, about 2.7x slower (the page notes tickdb's path includes WAL/durability). Queries: DuckDB wins OHLCV by \~1.5-1.6x, VWAP by \~190-240x and top-10-by-volume by \~55-115x. Polars also beats tickdb on VWAP. |
| **Workload** | 2,000,000 synthetic trade rows. Measures on-disk bytes per trade (delta-of-delta timestamps, delta/zigzag prices, RLE, zstd) against Parquet written by DuckDB COPY ... (FORMAT PARQUET, COMPRESSION ZSTD); ingest vs DuckDB CSV load (1 run); and OHLCV/VWAP/top-10 query time vs DuckDB over Parquet (Polars on VWAP only). 2 runs on the author's machine, July 2026. |
| **Metric** | memory |
| **Hardware** | unstated ("this machine") |
| **Adoption** | 0 stars (self-described systems-engineering portfolio project, not for production quant use) |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/DerekNest/tickdb) · [benchmark](https://github.com/DerekNest/tickdb/blob/main/docs/BENCHMARKS.md) |

## Verdict

The author's BENCHMARKS.md (2 runs on 2M synthetic Binance-style trades, hardware not stated, release profile with opt-level 3 and thin LTO) reports 6.50 bytes/trade vs 8.13 for Parquet written by DuckDB COPY with ZSTD, about 20% smaller. DuckDB reading that Parquet wins every query (OHLCV \~1.5x, VWAP \~190-240x, top-10 \~55-115x), and DuckDB's CSV load is \~2.7x faster at ingest. Neither side is tuned: each query is timed once, the Parquet file sets only COMPRESSION ZSTD and leaves column types to read_csv_auto, and the synthetic data (i.i.d. sides, uniform qty, 950-1050 ms between trades despite a '\~1ms' comment) was never replaced with the real Binance run the docs describe.

## Use it when

- As readable reference code for a trade-specific block codec (DoD timestamps, decimal-mantissa delta prices, RLE side, zstd) that reached 6.50 bytes/trade on the author's 2M-row synthetic set, vs 8.13 for Parquet+zstd written by DuckDB.
- To study a small end-to-end storage engine in Rust: CRC-framed WAL with EveryWrite/EveryNMs/Never fsync policies, a manifest updated by atomic rename, immutable segments with zone maps, size-tiered compaction and crash-recovery tests.
- To learn Raft testing: an I/O-free RaftNode::step state machine driven by a seeded fault-injection simulator (drop, delay, duplicate, partition, crash). The README reports 1,000 seeds with zero invariant violations.
- As design input only, when bytes per trade in cold storage matter more than query or ingest speed and you will write your own implementation. The code has no license.

## Skip it when

- Any query-speed goal. DuckDB over the same Parquet file was about 1.5x faster on 1-minute OHLCV, 190-240x faster on VWAP and 55-115x faster on top-10. Polars also beat it on VWAP.
- Ingest-bound pipelines: 7.32M rows/s (one run) vs 20.05-20.67M rows/s for DuckDB's CSV load. BENCHMARKS.md excuses this by saying tickdb pays for durability, but both tickdb bench paths open the engine with FsyncPolicy::Never.
- Production use or code reuse: no license, 2 commits (both 2026-07-04), 0 stars, no releases, not on crates.io, and the author calls it a portfolio project. The Dockerfile says it has never been built.
- Data outside the fixed trade schema. There are no dynamic or optional columns, the CLI's CSV parser expects Binance aggTrades columns, qty is stored as 8-decimal fixed point (extra digits are truncated), and there is no Parquet or Arrow file import.
- Concurrent readers or writers. Engine is documented as single-threaded, so callers must serialize access (the server wraps it in a Mutex), and queries run on one thread.

## How it is fast

It is not faster; its only win is size, from how each 65,536-row block is encoded: it stores timestamps as delta-of-delta + zigzag + LEB128 varints (a byte-aligned simplification of Gorilla), rescales prices to a common decimal exponent and delta + zigzag varint-codes the mantissas, stores sizes and trade_ids as plain varints and side as run-length pairs, then zstd-compresses the block at level 3. Reads are slow by construction: every query decompresses and decodes all five columns of each block (no projection pushdown), the 'mmap' reader copies each whole segment into a heap Vec, and the kernels are single-threaded scalar loops (OHLCV does one BTreeMap insert per row). The author credits DuckDB's vectorized engine for the gap.

## Compared with alternatives

Practically never for real workloads. Among catalogued Parquet alternatives, Vortex, BtrBlocks and FastLanes report faster writing or decoding than Parquet, and QuestDB is a real time-series engine for tick data. Pick tickdb only as a compact, readable Rust example of a trade-specific codec together with a WAL, compaction and Raft simulation.

## Integration

| | |
|---|---|
| **Form** | Cargo workspace of path-dependency crates (format, storage, query, raft, sim, server, cli) plus the tickdb and tickdb-server binaries. Not published; the crates.io 'tickdb' crate is an unrelated project (fractal69/cursor-db). |
| **Dependencies** | format: zstd 0.13, crc32fast, thiserror, serde. storage adds memmap2 0.9, serde_json and tracing. server adds tokio, axum 0.7, arrow/arrow-ipc 52 and clap 4.5.37 (pinned). |
| **Minimum toolchain** | Declares Rust 1.75, edition 2021 (clap is pinned for 1.75). The Dockerfile uses rust:1.96, CI uses stable, and fuzzing needs nightly plus cargo-fuzz. |
| **Platforms** | Not documented. CI runs only on ubuntu-latest. Compaction relies on the Linux/macOS rule that a file stays readable after it is deleted while still mapped. Benchmark hardware is not stated. |
| **Thread safety** | Engine is documented as single-threaded; the caller serializes access, and the server holds a Mutex&lt;Engine&gt;. MmapSegment uses unsafe impl Send + Sync. |
| **Drop-in for the baseline** | no |

## Gotchas

- Segments are not really zero-copy mmap. MmapSegment::open copies the whole mapped file into a Vec (mmap.to_vec()), and Engine::scan collects each segment's decoded batches into a Vec before yielding them, so RAM use grows with segment size.
- FORMAT.md says checksums are CRC-32C (Castagnoli), but the code uses crc32fast, which computes standard CRC-32 (IEEE). An independent reader built from FORMAT.md would reject every block.
- The docs contradict each other. DESIGN.md Phase 4 still says tickdb is \~3x faster than DuckDB on OHLCV and only 3-4x slower on VWAP and top-N, and agg.rs says the kernels hit a &gt;=100M rows/s/core target. The later BENCHMARKS.md withdraws the OHLCV win and measures 15-34M rows/s.
- The repo has about 24.5k build-artifact files committed under target/ and no .gitignore, and GitHub reports about 0.8 GB of disk usage, so a clone is heavy.

## Known shortcomings

- NOT FASTER: the only win is storage (6.50 vs 8.13 B/trade, \~20% smaller than Parquet+zstd); ingest is \~2.7x slower and every query is slower than DuckDB (the author's own doc says 1.5-240x). No license.
- The 'includes durability' excuse is false (both tickdb bench paths use FsyncPolicy::Never); mmap is not zero-copy (segments are copied to the heap); FORMAT.md says CRC-32C but the code computes IEEE CRC-32; DESIGN.md still claims a \~3x OHLCV win withdrawn by BENCHMARKS.md. Synthetic data only; Parquet side untuned; each query timed once; single-threaded; two commits, 0 stars, \~0.8 GB repo of committed build files.

## Caveats and trade-offs

No license file (GitHub reports no license), so the code cannot legally be reused and usability is reference. The only win is storage footprint, \~20% smaller than DuckDB-written Parquet+zstd on synthetic data; tickdb is slower on ingest (\~2.7x) and on every benchmarked query (1.5x to over 200x). The README calls it a systems-engineering portfolio project, not for production. No hardware is stated.

Explicitly a learning/portfolio project, not production-ready; the only genuine performance win documented is on-disk compactness, not query speed -- author's own doc states DuckDB's vectorized execution engine beats tickdb on every benchmarked query shape.

## Maintenance

Dormant single-drop portfolio repo (2 commits on 2026-07-04, none since) with no license, so the code is reference-only and cannot legally be reused.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** docs/BENCHMARKS.md gives first-party numbers from 2 runs on 2M synthetic rows (6.50 vs 8.13 bytes/trade against Parquet+zstd, plus query timings against DuckDB and Polars). The harness is public (bench/compare_duckdb_parquet.py, bench/tickdb_bench_rs), but no hardware, CPU, compiler or flags are stated, so the tier is C.
- **Verifier notes:** The numbers are accurate and candidly reported, but the project is slower than its baselines on every speed axis and its only advantage is a \~20% smaller on-disk size. That makes it a not-faster scope reject, like the jsonbinpack precedent; keep it flagged with the shortcoming if policy says so. Metadata is verified: no license, 0 stars, last commit 2026-07-04, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DerekNest/tickdb>
  - <https://github.com/DerekNest/tickdb/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/DerekNest/tickdb/blob/main/README.md>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/compare_duckdb_parquet.py>
- **Sources the enricher read:**
  - <https://github.com/DerekNest/tickdb>
  - <https://github.com/DerekNest/tickdb/blob/main/README.md>
  - <https://github.com/DerekNest/tickdb/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/DerekNest/tickdb/blob/main/docs/DESIGN.md>
  - <https://github.com/DerekNest/tickdb/blob/main/docs/FORMAT.md>
  - <https://github.com/DerekNest/tickdb/blob/main/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/storage/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/query/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/server/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/cli/Cargo.toml>
  - <https://github.com/DerekNest/tickdb/blob/main/Dockerfile>
  - <https://github.com/DerekNest/tickdb/blob/main/.github/workflows/ci.yml>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/compare_duckdb_parquet.py>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/gen_synthetic.py>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/run_benchmarks.sh>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/tickdb_bench_rs/src/main.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/bench/tickdb_bench_rs/src/query_only.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/lib.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/types.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/compress.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/size_col.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/segment.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/format/src/dict.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/query/src/agg.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/query/src/scan.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/query/src/batch.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/query/src/builder.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/storage/src/engine.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/storage/src/mmap.rs>
  - <https://github.com/DerekNest/tickdb/blob/main/crates/cli/src/csv.rs>
  - <https://hn.algolia.com/api/v1/search?query=tickdb&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=DerekNest>
  - <https://crates.io/api/v1/crates/tickdb>
  - <https://crates.io/api/v1/crates/crc32fast>
  - <https://raw.githubusercontent.com/srijs/rust-crc32fast/master/README.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dereknest/tickdb`) · [data/wave6/enrich/raw/github_com_dereknest_tickdb.json](../../../data/wave6/enrich/raw/github_com_dereknest_tickdb.json) (enrichment confidence 0.85)

</details>
