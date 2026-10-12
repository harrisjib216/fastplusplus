# SurrealKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> SurrealDB's pure-Rust async LSM key-value engine with OCC transactions; vendor benchmark shows \~3x RocksDB fsync'd write throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 3.31x faster creates (105,072 vs 31,777 OPS), 3.08x faster updates, 2.84x faster deletes, 2.31x faster point reads (1,602,668 vs 692,597 OPS) and 3.47x faster range scans (8,361 vs 2,406 OPS) vs RocksDB. It also beats Fjall and SlateDB. LMDB (27,446 OPS) and Libmdbx (16,005 OPS) beat it on range scans, and RocksDB has the lowest peak memory (393 MB vs SurrealKV's 1.35 GB). |
| **Workload** | 50,000 keys, 48 concurrent worker threads, 128 clients, synchronous durability (--sync) via the crud-bench cross-engine harness; point read, create, update, delete and scan operations. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 9970X (32-core/64-thread) @5.48GHz, 128GB DDR5 RAM, 4TB PCIe 4.0 NVMe SSD, bare metal |
| **Compiler and flags** | Not stated in the SurrealKV README. The crud-bench Cargo.toml release profile uses lto=true, opt-level=3, codegen-units=1 and panic=abort, with rust-version &gt;= 1.91.0. The toolchain actually used is not stated. |
| **Adoption** | 554 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/surrealdb/surrealkv) · [benchmark](https://github.com/surrealdb/surrealkv#performance) |

## Verdict

On SurrealDB's own crud-bench harness (Threadripper 9970X, 128 GB DDR5, PCIe 4.0 NVMe, bare metal; 50K keys, 48 Tokio workers, 128 clients, --sync), SurrealKV reached 105,072 creates/s vs 31,777 for RocksDB (SurrealDB's surrealdb-rocksdb 0.24.0-surreal.5 fork, as an OptimisticTransactionDB), a 3.31x gap. It also reached 1.60M vs 693K point reads/s (2.31x) and 8,361 vs 2,406 scans/s (3.47x). The Rust toolchain is not stated; crud-bench's release profile uses LTO, opt-level 3 and codegen-units 1. README git history shows the SurrealKV row re-measured at least three times on 2026-09-24/25 (point reads 901K -&gt; 1.18M -&gt; 1.60M, creates 88K -&gt; 105K), while RocksDB's create and scan figures never changed. The build measured is unreleased main, while crud-bench main pins surrealkv 0.21.2.

## Use it when

- Rust services on Tokio with many concurrent small transactions that each need fsync-before-ack durability. This is where group commit pays off: 105K synced creates/s at 128 clients vs RocksDB's 31.8K in the vendor run.
- You need multi-key snapshot-isolation transactions with savepoints, or built-in versioned/time-travel reads (with_versioning, get_at, history), without layering MVCC on top of a plain KV store.
- One storage engine must also run in the browser: wasm32-unknown-unknown in a Web Worker, persisting to OPFS, with a migrator for existing IndexedDB stores.
- You want a Rust-native build and don't want to compile librocksdb-sys. Remaining native code is small C codecs such as zstd.
- Point-read-heavy workloads whose working set fits in memtable plus block cache. The vendor run shows 1.60M reads/s on a 50K-key dataset.

## Skip it when

- Range-scan-dominated workloads: in the same table LMDB (27,446 ops/s) and libmdbx (16,005) beat SurrealKV's 8,361 scans/s. An mmap B+tree is the better fit.
- Tight RAM budgets. Peak memory was 1.35 GB vs RocksDB's 393 MB in the vendor run. Issue #397 measured compactions needing 16-22 GiB, with an OOM restart loop on a \~16 GB store; the fix merged on 2026-09-25 is not in any crates.io release yet.
- Datasets much larger than RAM or long-running write-heavy stores. The only published benchmark uses 50K keys, which fit in memory. Compaction is leveled-only, and a maintainer agreed in issue #309 that leveled is a poor fit for versioned data.
- Code that needs the RocksDB API or ecosystem: C/C++ callers, RocksDB-specific tuning, or features the README does not document, such as column families or merge operators.
- Anything that needs a settled, well-tested release. It is 0.x, and the benchmarked 'V2' engine is 120 commits past the latest crates.io release (0.21.4). 2026 fixed several correctness bugs: broken first-committer-wins (#376), no fsync after compaction (#390), UB in the memtable arena (#393) and range-iterator boundary defects (#395). One anecdotal HN report (June 2026, older version) also found SQLite 15-60x faster per op for a single client.

## How it is fast

Writes use a group-commit pipeline modeled on Pebble's. Each committing transaction claims a slot in a 1024-slot lock-free MPSC ring with one atomic fetch_add, checks for conflicts against recent commits (Bloom-filter-assisted), and publishes the slot. A single background flusher drains every contiguous ready slot, writes them as one WAL append with one fsync, applies them to the arena-skiplist memtable, and advances the visible sequence number. Because commit() is an awaitable future, far more transactions than worker threads can share one fsync. In contrast, crud-bench's RocksDB adapter calls RocksDB's blocking commit() directly inside async tasks, which probably limits how many commits RocksDB can group per fsync at 48 workers; that is our reading of the adapter code, not a measured cause. Reads are lock-free MVCC snapshot lookups through the memtables and then leveled SSTables (64 KB prefix-compressed blocks, 10-bit/key Bloom filters, sharded block cache), and large values can move to a WiscKey-style value log.

## Compared with alternatives

Pick it over Badger when you are in Rust/Tokio or need browser OPFS support; both offer WiscKey value separation and snapshot-isolated transactions, but Badger is Go. Pick Speedb, ToplingDB or PsiTri instead when you need the RocksDB API as a drop-in or a C++ consumer, since SurrealKV only offers its own Rust API and a one-way RocksDB data import.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio (runtime required), affinitypool, arenaskiplist, byteslice, quick_cache, parking_lot, bytes, snap, zstd, lz4_flex, crc32fast, xxhash-rust, aes-gcm, chacha20poly1305, chacha20, blake3, subtle, tracing, async-trait, rand. Also rustix on Unix, windows-sys on Windows, wasm-bindgen/web-sys/getrandom on wasm. Three in-workspace migration crates (RocksDB, SurrealKV v1 and IndexedDB readers) are always compiled in. |
| **Minimum toolchain** | Rust 1.86 (rust-version in Cargo.toml, edition 2021), plus a Tokio runtime. |
| **Platforms** | README lists Linux x86-64/aarch64, macOS x86-64/aarch64, Windows x86-64, and wasm32-unknown-unknown (browser Web Workers with OPFS). CI also builds Apple and Android targets. The README's claim of io_uring on Linux does not match main, where WAL and SSTable I/O use the affinitypool thread pool on every platform. |
| **Thread safety** | One Tree is shared across tasks (crud-bench shares it through an Arc across 128 clients). Each Transaction belongs to one task. Concurrency control is optimistic, first-committer-wins, with snapshot isolation (not serializable). |
| **Drop-in for the baseline** | partial — not API-compatible with RocksDB (Rust-only Tree/Transaction API with async commit). It can import existing RocksDB BlockBasedTable v2-v7 data on startup or with `skv migrate`, but only as a one-way migration. |

## Gotchas

- Default durability is Durability::Eventual, which writes to the OS page cache without fsync. The benchmark figures use Durability::Immediate, set per transaction. Set it yourself if you need the durability the benchmark measured.
- Needs Tokio. build() spawns background tasks with tokio::spawn and commit() is async. Call tree.close().await before exit: Drop only schedules an async close when a runtime is current, and otherwise just logs a warning.
- A commit that loses a write-write conflict returns TransactionWriteConflict and closes the transaction, so retry with a new transaction. Isolation is snapshot, so write skew is possible, and get_for_update does not stop it between transactions that only read a key.
- The benchmark config differs from the defaults. crud-bench turns on the value log (off by default), sets a 256 MB memtable (default 100 MB) and sizes the block cache in GB (default 32 MB). docs/ARCHITECTURE.md is marked WIP and still describes the older mutex-based commit path (src/commit.rs and src/oracle.rs no longer exist on main).

## Known shortcomings

- Evidence is crud-bench from the same organization (SurrealDB) with toolchain/flags unstated, and its RocksDB is SurrealDB's fork crate.
- Benchmark rows are mixed: the SurrealKV row was rerun 3+ times (901K to 1.18M to 1.60M reads) while RocksDB's create/scan numbers never changed; the benchmarked code is unreleased (main is 120 commits past crates.io 0.21.4). Default durability is Eventual (no fsync) while the bench forces Immediate with vlog, a 256 MB memtable and a GB-sized cache; peak memory 1.35 GB vs RocksDB 393 MB; 50K keys fit in RAM; LMDB/libmdbx win scans.
- A compaction OOM (#397, 16-22 GiB) is fixed on main but unreleased; recent correctness bugs #376, #390, #393, #395; the README's io_uring claim is absent from the code; needs Tokio. The crud-bench RocksDB adapter calls blocking commit() inside async tasks, which likely shrinks its fsync groups (inferred from code).

## Caveats and trade-offs

crud-bench is maintained by SurrealDB, the same org as SurrealKV, so despite covering many engines it is not independent. Its RocksDB adapter uses SurrealDB's own fork crate (surrealdb-rocksdb 0.24.0-surreal.5), with configuration chosen by SurrealDB. The README does not record the crud-bench commit, SurrealKV version or Rust toolchain behind its numbers: crud-bench main pins surrealkv 0.21.2, while the workspace is at 0.21.4. SurrealKV's peak memory (1.35 GB) is well above RocksDB's (393 MB).

Higher resting memory than RocksDB (\~328MB vs \~356MB is comparable, but peak differs); versioned/MVCC design trades some write-path complexity for read/write concurrency.

## Maintenance

Very active: 120 commits since v0.21.4 (2026-08-26), most of the V2 engine landed 2026-09-24..26, and the memtable was swapped on 2026-09-26. It is Apache-2.0, has 555 stars and \~1.06M crates.io downloads (mostly via SurrealDB), but it is pre-1.0 and the benchmarked code is not on crates.io yet, so pin a git revision or wait for the next release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README table compares SurrealKV directly with RocksDB on a named CPU (Threadripper 9970X), and every quoted ratio matches. The harness, crud-bench, is SurrealDB's own tool, not an independent third-party suite, so B does not apply. It is not A either, because the README gives no Rust toolchain or build flags, and no crud-bench commit or engine versions for the run.
- **Verifier notes:** All README numbers and ratios check out. The downgrade is only a tier fix: the record rated first-party crud-bench as B, but same-org harness numbers with unstated toolchain and flags are C. Metadata checks out: Apache-2.0, 554 stars, last commit 2026-09-26, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/surrealdb/surrealkv>
  - <https://raw.githubusercontent.com/surrealdb/surrealkv/main/README.md>
  - <https://raw.githubusercontent.com/surrealdb/surrealkv/main/Cargo.toml>
  - <https://github.com/surrealdb/crud-bench>
  - <https://raw.githubusercontent.com/surrealdb/crud-bench/main/Cargo.toml>
  - <https://raw.githubusercontent.com/surrealdb/crud-bench/main/.cargo/config.toml>
  - <https://raw.githubusercontent.com/surrealdb/crud-bench/main/README.md>
  - <https://raw.githubusercontent.com/surrealdb/crud-bench/main/Dockerfile>
- **Sources the enricher read:**
  - <https://github.com/surrealdb/surrealkv>
  - <https://github.com/surrealdb/surrealkv/blob/main/README.md>
  - <https://github.com/surrealdb/surrealkv/blob/main/docs/ARCHITECTURE.md>
  - <https://github.com/surrealdb/surrealkv/blob/main/Cargo.toml>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/lib.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/ring/mod.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/ring/pipeline.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/ring/slot.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/transaction.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/lsm.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/storage/mod.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/wal/writer.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/vfs.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/autotune.rs>
  - <https://github.com/surrealdb/surrealkv/blob/main/src/task.rs>
  - <https://github.com/surrealdb/surrealkv/tree/v0.21.4>
  - <https://github.com/surrealdb/surrealkv/compare/v0.21.4...main>
  - <https://github.com/surrealdb/surrealkv/commits/main>
  - <https://github.com/surrealdb/surrealkv/releases>
  - <https://github.com/surrealdb/surrealkv/commit/68b240e>
  - <https://github.com/surrealdb/surrealkv/commit/f167fc7>
  - <https://github.com/surrealdb/surrealkv/commit/02e2ba3>
  - <https://github.com/surrealdb/surrealkv/commit/3d09b37>
  - <https://github.com/surrealdb/surrealkv/issues?q=is%3Aissue>
  - <https://github.com/surrealdb/surrealkv/issues/397>
  - <https://github.com/surrealdb/surrealkv/issues/390>
  - <https://github.com/surrealdb/surrealkv/issues/393>
  - <https://github.com/surrealdb/surrealkv/issues/376>
  - <https://github.com/surrealdb/surrealkv/issues/377>
  - <https://github.com/surrealdb/surrealkv/issues/309>
  - <https://crates.io/api/v1/crates/surrealkv>
  - <https://github.com/surrealdb/crud-bench>
  - <https://github.com/surrealdb/crud-bench/blob/main/README.md>
  - <https://github.com/surrealdb/crud-bench/blob/main/Cargo.toml>
  - <https://github.com/surrealdb/crud-bench/blob/main/config/bench.toml>
  - <https://github.com/surrealdb/crud-bench/blob/main/src/adapters/surrealkv.rs>
  - <https://github.com/surrealdb/crud-bench/blob/main/src/adapters/rocksdb.rs>
  - <https://hn.algolia.com/api/v1/search?query=surrealkv>
  - <https://news.ycombinator.com/item?id=48363832>
  - <https://news.ycombinator.com/item?id=48363429>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/surrealdb/surrealkv`) · [data/wave6/enrich/raw/github_com_surrealdb_surrealkv.json](../../../data/wave6/enrich/raw/github_com_surrealdb_surrealkv.json) (enrichment confidence 0.8)

</details>
