# redb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust embedded ACID key-value store on copy-on-write B+trees; beats RocksDB/SQLite on durable single-key commits and reads; LMDB still reads faster.

| | |
|---|---|
| **Beats** | RocksDB and SQLite (also benchmarked against LMDB and fjall, with mixed results) |
| **Claimed result** | Individual writes: redb 920ms vs RocksDB 2432ms and SQLite 7040ms (\~2.6x/7.7x faster, derived from page data; redb also beats LMDB's 1598ms on this row). Random reads: redb 1138ms vs RocksDB 2911ms and SQLite 4283ms (\~2.6x/3.8x faster, derived from page data). LMDB beats redb on every read row, including 4/8/16/32-thread reads. |
| **Workload** | Embedded KV benchmark: bulk load, individual/batch writes, len(), random reads/range reads at 1/4/8/16/32 threads, removals, on-disk size; redb vs lmdb, rocksdb, fjall, sqlite |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9950X3D CPU, Samsung 9100 PRO NVMe SSD |
| **Adoption** | 4.8k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/cberner/redb) · [benchmark](https://github.com/cberner/redb#benchmarks) |

## Verdict

On the author's redb-bench-compare harness (Ryzen 9950X3D, Samsung 9100 PRO NVMe, 5M random entries with 24-byte keys and 150-byte values, 4 GiB cache, all engines driven from Rust), 1,000 fsync'd single-key commits took 920 ms for redb, against 2,432 ms for RocksDB (rust-rocksdb 0.24 OptimisticTransactionDB, lz4) and 7,040 ms for SQLite (rusqlite 0.38 bundled, synchronous=FULL and otherwise default journal and cache), and 1M in-cache random reads took 1,138 ms against 2,911 ms and 4,283 ms. LMDB (heed 0.22) won every read row, the rustc version and flags are not stated (the repo pins toolchain 1.90), and the current harness emits rows the README table lacks, so the table may predate it.

## Use it when

- Rust services that make many small durable transactions (one or a few keys per fsync'd commit). The README run shows about 0.92 ms per single-key commit, against 1.6 ms for LMDB, 2.4 ms for RocksDB and 7.0 ms for SQLite.
- Point and short-range reads on a working set that fits the cache, when you need an ordered store in memory-safe Rust. In-cache random reads ran about 2.6x faster than RocksDB and 3.8x faster than SQLite, and readers scale across threads without blocking the writer.
- Apps that need O(1) len(), savepoints and rollback, typed tables or zero-copy value access (AccessGuard borrows from the page cache) in one self-contained file.
- Builds that must avoid a C/C++ toolchain, or that target Windows, macOS, Linux (x86-64 and aarch64), WASI, or experimental no_std embedded targets (Cortex-M3 and up).
- Custom storage, such as an in-memory database or block-level encryption, done by implementing StorageBackend. The maintainer suggests this route for encryption in issue #1091.

## Skip it when

- When read throughput matters most: LMDB beat redb on every read row, by about 1.5-3.3x (for example 125 ms vs 410 ms for 32-thread random reads). libmdbx or LMDB are the better picks there.
- Batch, bulk and delete-heavy workloads. RocksDB and fjall wrote 1,000-key batches 3.5-4.5x faster, removals took 23.3 s against 6.0-6.9 s for RocksDB and fjall, and LMDB bulk-loaded in 9.2 s against redb's 17.1 s.
- Tight disk budgets. redb has no built-in compression, and its file was the largest in the run: 4.00 GiB uncompacted (RocksDB 893 MiB) and 1.69 GiB compacted (RocksDB 455 MiB). Long-running read transactions also make the file grow further.
- Many concurrent writers or multi-process sharing. There is one writer per database, and multi-process single-writer or multi-writer modes exist only behind the experimental-multiprocess feature.
- C++ codebases (you need your own FFI layer) and rotational disks. Open issue #1507 reports that since 4.2 each durable commit also writes a low-offset system page, costing about +26% commit time on an HDD. The reporter saw no cost on SSD or NVMe.

## How it is fast

LMDB-style copy-on-write B+trees with MVCC: readers pin a root snapshot and never block the writer, and freed pages are recycled by epoch-based reclamation once no reader can see them. Durable commits default to '1-phase + checksum' (1PC+C): the tree is a Merkle tree of XXH3-128 page checksums, so a commit writes the new pages, flips one 'god byte' commit-slot bit and issues a single fsync with no separate WAL, which is where the single-key-commit win comes from. Unlike LMDB it does not use mmap; pages go through pread/pwrite and a userspace LRU page cache with a lock-striped read cache and write buffer (1 GiB by default). Fixed-width keys and values are stored without offset arrays, variable-length keys get shortest-separator prefixes in branch pages (4.3), and a stored tree length makes len() O(1).

## Compared with alternatives

Pick redb over libmdbx when you are in Rust and want a pure-Rust, memory-safe dependency with fast small durable commits; libmdbx (C, LMDB-derived) is the better choice when raw read speed or a native C/C++ API matters. TerarkDB is a RocksDB-compatible LSM fork for write-heavy, compression-sensitive workloads, which are exactly redb's weak spots (batch writes, removals, file size).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none with default features; optional log, chrono and uuid features; libc on Linux, Apple and WASI targets for pread/pwrite and byte-range file locks |
| **Minimum toolchain** | Rust 1.90 (edition 2024) |
| **Platforms** | Linux, macOS and Windows (CI on x86-64 plus Linux aarch64), WASI, wasm32-unknown-unknown (compile-checked), and no_std targets with atomic CAS under experimental-api-5 |
| **Thread safety** | Database is shared across threads. Any number of read transactions can run concurrently with each other and with the one active write transaction; begin_write() waits for the previous writer. Across processes, the default is one exclusive writer holding a file lock; single-writer and multi-writer sharing is experimental. |
| **Drop-in for the baseline** | false — different API (typed Rust tables with no SQL, column families or merge operators) and its own file format; C++ callers must write an FFI shim |

## Gotchas

- Default durable commits (1PC+C) rely on non-cryptographic XXH3 checksums. The design doc recommends set_two_phase_commit(true) when attacker-controlled data is stored.
- Recovery after a crash is a full repair by default: redb walks the whole file to verify checksums and rebuild the allocator state, which the docs call 'very slow' for large databases. set_quick_repair(true) makes commits slower but recovery almost instant.
- Durability::None commits are atomic but are lost on a crash until a later Durability::Immediate commit. compact() needs &mut Database and refuses to run while transactions or savepoints are live, and long-lived readers stop pages from being reused.
- The 4.2 and 4.3 releases fixed several correctness bugs, including a commit that could be silently rolled back during recovery after check_integrity() had repaired the database, iterators that skipped entries after an error, and pages leaked by panics caught with catch_unwind. Run a current release.

## Known shortcomings

- LMDB wins every read row in redb's own table; RocksDB/fjall win batch writes and removals; redb uses the most disk. No rustc version or flags. The README's benchmark link is stale (real path crates/redb-bench-compare/benches/lmdb_benchmark.rs).
- LMDB wins every read row (1.5-3.3x); batch writes 3.5-4.5x slower than RocksDB/fjall, removals \~3.4-3.9x slower, bulk load 1.85x slower than LMDB. No compression, so the largest file (4.00 GiB vs RocksDB 893 MiB), and long-lived readers grow it further. The SQLite baseline sets only synchronous=FULL (default journal and cache). Full repair after a crash by default (slow on big databases); +26% commit time on HDD since 4.2 (#1507). No C API; C++ needs FFI.

## Caveats and trade-offs

The README itself says redb has 'similar' performance to top embedded KV stores such as lmdb and rocksdb. LMDB wins every read and range-read row, and RocksDB/fjall win batch writes and removals by roughly 3.5-4.5x. redb's on-disk size is also the largest (4.00 GiB uncompacted vs RocksDB 893 MiB). The clear wins are individual writes and reads against RocksDB and SQLite. Hardware is stated, but the compiler version and flags are not. The baselines run through Rust bindings: rust-rocksdb 0.24 (lz4 only, OptimisticTransactionDB), rusqlite 0.38 with bundled SQLite, and heed 0.22 for LMDB. The README's benchmark source link is stale: it points to crates/redb-bench/benches/lmdb_benchmark.rs, and the file now lives at crates/redb-bench-compare/benches/lmdb_benchmark.rs.

Rust, only usable from C++ via FFI; consistently slower than LMDB on random/range reads and on removals; larger on-disk size than RocksDB/SQLite in this benchmark

## Maintenance

Actively maintained (last commit 2026-09-24, 4.3.0 released 2026-09-14, about 11.9M crates.io downloads and 478 reverse dependencies), with a file format declared stable and a dual MIT/Apache-2.0 license; it is easy to add as a crate, but C++ can use it only through an FFI layer you write.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table is first-party and compares redb with lmdb, rocksdb, fjall and sqlite. The benchmark code is public (crates/redb-bench-compare/benches/lmdb_benchmark.rs) and the CPU is named (Ryzen 9950X3D), but no rustc version or build flags are given (the Cargo [profile.bench] only adds debug=true), so it falls short of A.
- **Verifier notes:** All cited numbers match the current README table exactly. Metadata checks out: gh reports spdx Apache-2.0 while the README License section makes it dual Apache-2.0 OR MIT, with 4,808 stars, last commit 2026-09-24, and not archived or a fork. The only corrections are adding derivation markers to claimed_speedup and extending the caveats.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cberner/redb>
  - <https://github.com/cberner/redb#benchmarks>
  - <https://raw.githubusercontent.com/cberner/redb/master/README.md>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench-compare/benches/lmdb_benchmark.rs>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench-compare/Cargo.toml>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench/Cargo.toml>
  - <https://github.com/cberner/redb/blob/master/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/cberner/redb>
  - <https://github.com/cberner/redb#benchmarks>
  - <https://github.com/cberner/redb/blob/master/README.md>
  - <https://github.com/cberner/redb/blob/master/docs/design.md>
  - <https://github.com/cberner/redb/blob/master/Cargo.toml>
  - <https://github.com/cberner/redb/blob/master/rust-toolchain>
  - <https://github.com/cberner/redb/blob/master/CHANGELOG.md>
  - <https://github.com/cberner/redb/blob/master/.github/workflows/ci.yml>
  - <https://github.com/cberner/redb/blob/master/src/lib.rs>
  - <https://github.com/cberner/redb/blob/master/src/db.rs>
  - <https://github.com/cberner/redb/blob/master/src/transactions.rs>
  - <https://github.com/cberner/redb/blob/master/src/backends.rs>
  - <https://github.com/cberner/redb/blob/master/src/tree_store/page_store/cached_file.rs>
  - <https://github.com/cberner/redb/blob/master/src/tree_store/page_store/file_backend/mod.rs>
  - <https://github.com/cberner/redb/blob/master/src/tree_store/page_store/file_backend/optimized.rs>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench-compare/benches/lmdb_benchmark.rs>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench-compare/benches/common/mod.rs>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench-compare/Cargo.toml>
  - <https://github.com/cberner/redb/blob/master/crates/redb-bench/src/lib.rs>
  - <https://github.com/cberner/redb/issues/1098>
  - <https://github.com/cberner/redb/issues/1066>
  - <https://github.com/cberner/redb/issues/1094>
  - <https://github.com/cberner/redb/issues/1317>
  - <https://github.com/cberner/redb/issues/1091>
  - <https://github.com/cberner/redb/issues/1507>
  - <https://github.com/cberner/redb/issues?q=is%3Aopen>
  - <https://crates.io/api/v1/crates/redb>
  - <https://crates.io/api/v1/crates/redb/reverse_dependencies>
  - <https://www.redb.org/post/2023/06/16/1-0-stable-release/>
  - <https://hn.algolia.com/api/v1/search?query=redb&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cberner/redb`) · [data/wave6/enrich/raw/github_com_cberner_redb.json](../../../data/wave6/enrich/raw/github_com_cberner_redb.json) (enrichment confidence 0.8)

</details>
