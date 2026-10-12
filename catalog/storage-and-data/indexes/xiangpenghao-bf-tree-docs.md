# Bf-Tree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust (prototype, code not released)` · `MIT` · 🟢 active

> Microsoft Research's larger-than-memory concurrent B-Tree for small records, with record-level caching; beats RocksDB and page-cached B-Trees.

| | |
|---|---|
| **Beats** | RocksDB (commit 54d6286); the authors' own conventional B-Tree and Bδ-Tree in Rust; Leanstore (commit 677126c); TwoTree |
| **Claimed result** | 2.5x faster than RocksDB for scan operations, 6x faster than a B-Tree for write operations, 2x faster than both B-Trees and LSM-Trees for point lookup, for \~100-byte records (verbatim from repo README / VLDB 2024 abstract) |
| **Workload** | YCSB-like: 200M initial records of 32 bytes (16 B key, 16 B value), Zipf 0.9. Default mix is 50% reads / 50% writes with a 2 GB memory cache, larger-than-memory on NVMe. Scan, write and point-lookup workloads are compared against RocksDB, B-Trees and LSM-Trees; best of 5 runs. |
| **Metric** | throughput |
| **Hardware** | CloudLab 'sm110p' node: 32 hyper-threads at 2.4 GHz, 128 GB RAM, 1 TB NVMe PCIe 4.0 SSD (&gt;600k IOPS), Ubuntu 22.04, kernel 5.15, ext4 (CPU model not named) |
| **Compiler and flags** | Paper: Rust, version not stated; io_uring kernel-polling direct IO. The current microsoft/bf-tree benchmark/Cargo.toml release profile uses opt-level=3, lto=fat, codegen-units=16, panic=abort, and rust-toolchain.toml sets channel=stable (unpinned). |
| **Adoption** | 1073 stars (microsoft/bf-tree); \~313k crates.io downloads (bf-tree crate); the docs repo XiangpengHao/bf-tree-docs has 93 stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/microsoft/bf-tree) · [benchmark](https://www.vldb.org/pvldb/vol17/p3442-hao.pdf) |

## Verdict

In the peer-reviewed VLDB 2024 paper, run with 31 threads on a CloudLab sm110p node (32 hyper-threads at 2.4 GHz, CPU model not named; 128 GB RAM; PCIe 4.0 NVMe; Ubuntu 22.04, kernel 5.15), with 200M 32-byte records, Zipf 0.9 and a 2 GB cache, Bf-Tree was about 2.5x RocksDB (commit 54d6286, direct I/O, WAL and fsync off) on scans, about 6x the authors' own Rust B-Tree (Bf-Tree minus mini-pages) on writes, and about 2x both on point lookups. Its p99 read latency was 70 us against RocksDB's 131 us. On scans all the B-Tree variants performed about the same, and in memory it roughly matched Leanstore. The Rust version was not stated, logging was disabled for every system, and the released benchmark crate has not been shown to reproduce these figures.

## Use it when

- Skewed (Zipf-like) point-lookup plus update workloads on small records (the paper uses 16 B keys and 16 B values; the README targets about 100 B) where the dataset is several times larger than the RAM you can give the cache.
- Mixed read/write/scan workloads where an LSM (RocksDB) hurts scans and a page-cached B-Tree hurts random small writes. The paper shows it as the only system strong on all three.
- Linux servers with modern NVMe SSDs whose parallel random 4 KB writes run close to sequential throughput, where you can opt into the IoUringPolling/IoUringBlocking or StdDirect backends.
- High-thread-count embedded use from Rust: BfTree is Send + Sync, all operations take &self, and throughput scaled up to 31 threads until the SSD saturated.
- Secondary-index-style data with keys of 16 bytes or less by default (configurable up to 2020 B) where record-level caching beats caching whole 4 KB pages.

## Skip it when

- Large records: the authors' own README says large records perform like ordinary B-Trees or LSM-Trees, so the advantage disappears.
- Uniformly random access: in the paper every system does poorly because caching cannot help, and the gap narrows when most of the data fits in memory.
- When you need a production-grade durable store with transactions or crash-safe reopen: the WAL is off by default, and state survives restarts only through explicit snapshots (issue #9). An HN tester reported deadlocks with the WAL enabled (Jan 2026), and an open PR (#38, Aug 2026) fixes a panic when inserting after recovering from a CPR snapshot.
- Deletion-heavy workloads with long range scans: open issue #39 (v0.5.6) says ScanIter::next recurses once per tombstone or empty leaf and can overflow the stack. The fix (PR #40) is not merged.
- Older or consumer SSDs where random 4 KB writes are much slower than sequential ones. Leaf pages are written in place, and the docs flag possible SSD garbage-collection burden as future work.

## How it is fast

The core idea is 'mini-pages': variable-size in-memory buffers of 64 B to 4 KB that sit in front of each 4 KB on-disk leaf. Each one holds only the hot records for that leaf plus buffered dirty writes, and it grows, shrinks and is merged back in a batch on eviction. This gives record-level caching and write buffering in one structure, so a buffer pool of whole pages holding a few hot rows each is not needed. The mini-pages live in a circular-buffer allocator inspired by FASTER's hybrid log, which approximates LRU with a 10% 'second-chance' copy-on-access region. Other techniques are phantom records that cache negative lookups, inner nodes pinned in memory with optimistic latch coupling, prefix compression and look-ahead bytes, and, in the paper's setup, io_uring kernel-polling direct I/O with zero syscalls.

## Compared with alternatives

Pick it over redb when the working set is much larger than RAM, records are small and access is skewed, and you can live without redb's ACID transactions and crash-safe reopen. Pick it over in-memory ordered indexes like indexset or the ART variants when the data does not fit in memory. Stay with RocksDB-derived siblings (TerarkDB, MountDB) if you need RocksDB's API and operational tooling.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rand, serde, serde_json, toml, thread_local, cfg-if; Linux adds io-uring and libc; Windows adds windows-sys; optional tracing, hdrhistogram, chrono, auto_ops and variant_count behind the metrics/tracing features |
| **Minimum toolchain** | Stable Rust, edition 2021. No rust-version is declared and rust-toolchain.toml says only channel=stable. The source uses usize::is_multiple_of, which was stabilized in Rust 1.87. |
| **Platforms** | Linux is the only platform the README calls rigorously tested (CI runs only on ubuntu-22.04 x86-64). Windows and macOS are said to be supported, but the io_uring and direct-I/O backends are Linux-only and the benchmarks run only on Linux. CPU architecture support is not documented (issue #6 is open). SPDK support is experimental and for developers only. |
| **Thread safety** | BfTree has manual unsafe impl Send and Sync. Every operation takes &self, so share one tree across threads, e.g. via Arc. It is lock-based: optimistic latch coupling on inner nodes and a reader lock on the mapping table. It is tested with shuttle interleaving exploration, ASAN, fuzzing and Miri litmus tests for the CPR snapshot handshake. A missing SeqCst barrier in that handshake (issue #34) was fixed in July 2026. |
| **Drop-in for the baseline** | no |

## Gotchas

- By default keys over 16 bytes are rejected: cb_max_key_len defaults to 16 and insert returns LeafInsertResult::InvalidKV. Records must also be between cb_min_record_size (default 4 B) and cb_max_record_size (default 1952 B), with hard caps of 2020 B per key and 16332 B per value. Raise these limits in Config before loading data.
- read() copies into a caller buffer and, per its own doc comment, panics if the buffer is too small. Invalid Config values also trigger assert! panics while the tree is built, not only Result errors.
- The default storage backend is plain std::fs::File (StorageBackend::Std) with a 32 MB circular buffer. The paper's numbers used io_uring kernel polling with direct I/O and a 2 GB cache, so you must pick the backend and size explicitly to get comparable results.
- Snapshot files write BfTreeMeta as a raw repr(C) struct with no serialization, so portability across architectures or versions is not documented. Only one snapshot can run at a time, and scan_mut_\* is refused in cache-only mode.

## Known shortcomings

- The 6x write gain is vs the authors' own B-tree; code is now public at microsoft/bf-tree (MIT).
- The 2.5x scan gain is vs RocksDB only (WAL and fsync off); B-tree variants tie on scans. Keys over 16 B are rejected by default; read() panics if the buffer is too small; the default backend is std::fs, not the paper's io_uring. Open bugs: scan stack overflow on tombstones (#39), panic after snapshot recovery (PR #38), deadlocks reported with WAL on. Durable only via explicit snapshots; tested on Linux only; needs Rust &gt;=1.87.

## Caveats and trade-offs

The code is now public at https://github.com/microsoft/bf-tree (MIT, bf-tree crate; repo created 2025-12-19). The record's repo_url is the docs/paper-only repo (no license, last commit 2024-09-25), which still says the code is 'internal to Microsoft'. The '6x faster than a B-Tree' figure is against the authors' own in-house conventional B-Tree (Bf-Tree minus mini-pages), not a shipped library; only RocksDB and Leanstore are external baselines. The numbers are from the 2024 prototype, and no CPU model or rustc version is stated. The released benchmark/ crate (optional rocksdb/sled/redb/lmdb features) has not been shown to reproduce them. The design targets modern SSDs and small records; per the author's README, large records perform like B-Trees/LSM-Trees.

Optimized specifically for modern SSDs where parallel random 4KB writes approach sequential throughput; heavily tuned for small (\~100B) records -- large records perform like plain B-Trees/LSM-Trees; buffer-pool design is more complex than either baseline to implement correctly.

## Maintenance

The code at microsoft/bf-tree (MIT, crate bf-tree 0.5.6, about 313k downloads, about 1.07k stars) has been actively maintained since its public release in December 2025, with the last commit on 2026-08-19. It is usable as a crate but still research-grade: open bugs cover scan stack overflow and panics after snapshot recovery, and the record's repo_url points at the docs-only repo, which still calls the code internal.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B. The numbers come from the peer-reviewed VLDB 2024 paper (PVLDB 17(11) 3442-3455), which benchmarks against RocksDB (commit 54d6286) and Leanstore, and the code is now public at microsoft/bf-tree (MIT), so the no-code cap no longer applies. It is not A: the paper names no CPU model (only a CloudLab 'sm110p' node, 32 HT at 2.4 GHz) and no rustc version, and the repo pins only an unpinned 'stable' toolchain.
- **Verifier notes:** The repo_url should be repointed to https://github.com/microsoft/bf-tree, and the language is now plain Rust (code released). Neither field is correctable here. The docs repo is in known_list.txt, but microsoft/bf-tree is not, so this is not a known-project duplicate. The claimed_speedup wording matches the README and the paper abstract verbatim, but the paper's default records are 32 B rather than \~100 B.
- **Fields the verifier corrected:** `benchmark_url`, `license`, `usability`, `last_commit`, `maintenance_status`, `stars_or_usage`, `baseline`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/XiangpengHao/bf-tree-docs>
  - <https://www.vldb.org/pvldb/vol17/p3442-hao.pdf>
  - <https://github.com/microsoft/bf-tree>
  - <https://github.com/microsoft/bf-tree/tree/main/benchmark>
  - <https://github.com/microsoft/bf-tree/blob/main/benchmark/README.md>
  - <https://github.com/microsoft/bf-tree/blob/main/benchmark/Cargo.toml>
  - <https://github.com/microsoft/bf-tree/blob/main/rust-toolchain.toml>
  - <https://crates.io/api/v1/crates/bf-tree>
- **Sources the enricher read:**
  - <https://github.com/microsoft/bf-tree>
  - <https://github.com/microsoft/bf-tree/blob/main/Cargo.toml>
  - <https://github.com/microsoft/bf-tree/blob/main/rust-toolchain.toml>
  - <https://github.com/microsoft/bf-tree/blob/main/doc/README.md>
  - <https://github.com/microsoft/bf-tree/blob/main/doc/snapshot-recovery.md>
  - <https://github.com/microsoft/bf-tree/blob/main/doc/spdk-support.md>
  - <https://github.com/microsoft/bf-tree/blob/main/src/lib.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/src/config.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/src/tree.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/src/nodes/mod.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/src/fs/mod.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/src/range_scan.rs>
  - <https://github.com/microsoft/bf-tree/blob/main/benchmark/README.md>
  - <https://github.com/microsoft/bf-tree/blob/main/benchmark/Cargo.toml>
  - <https://github.com/microsoft/bf-tree/blob/main/.github/workflows/ci.yaml>
  - <https://github.com/microsoft/bf-tree/issues>
  - <https://github.com/microsoft/bf-tree/issues/39>
  - <https://github.com/microsoft/bf-tree/issues/34>
  - <https://github.com/microsoft/bf-tree/issues/9>
  - <https://github.com/microsoft/bf-tree/issues/7>
  - <https://github.com/microsoft/bf-tree/issues/6>
  - <https://github.com/microsoft/bf-tree/pull/38>
  - <https://github.com/microsoft/bf-tree/pull/30>
  - <https://github.com/microsoft/bf-tree/pull/16>
  - <https://www.vldb.org/pvldb/vol17/p3442-hao.pdf>
  - <https://crates.io/api/v1/crates/bf-tree>
  - <https://github.com/XiangpengHao/bf-tree-docs>
  - <https://hn.algolia.com/api/v1/search?query=bf-tree&tags=story>
  - <https://news.ycombinator.com/item?id=46802210>
  - <https://zhihanz.github.io/posts/bf-tree-rust-implementation/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/xiangpenghao/bf-tree-docs`) · [data/wave6/enrich/raw/github_com_xiangpenghao_bf_tree_docs.json](../../../data/wave6/enrich/raw/github_com_xiangpenghao_bf_tree_docs.json) (enrichment confidence 0.8)

</details>
