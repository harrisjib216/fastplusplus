# TidesDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MPL-2.0` · 🟢 active

> Embeddable transactional LSM key-value engine in C; the author's benchmark shows 4-5x RocksDB's iterator-seek throughput at about 3.5x the memory.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Random seeks 4.17x faster (3.73M vs 893K ops/sec); sequential seeks 4.74x faster (8.87M vs 1.87M ops/sec); Zipfian seeks 5.25x faster (3.56M vs 679K ops/sec); small (100-key) range queries 2.41x faster; large (1000-key) range queries 1.11x faster |
| **Workload** | benchtool tidesdb_rocksdb.sh: 8 threads, 16-byte keys / 100-byte values, sync disabled. Random and sequential seeks are 5M ops after populating 5M keys; Zipfian seeks run over \~650K unique keys; range queries of 100 and 1000 keys (random) and 100 keys (sequential). TidesDB v6.1.0 vs RocksDB v10.7.5. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-11700K (8 cores/16 threads @ 4.9GHz), 48GB DDR4, WD 500GB SATA SSD, Ubuntu 23.04 x86_64 (kernel 6.2.0-39-generic) |
| **Compiler and flags** | GCC with -O3 optimization |
| **Adoption** | 567 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/tidesdb/tidesdb) · [benchmark](https://tidesdb.com/articles/benchmark-design-range-seek-tidesdb610-rocksdb1075/) |

## Verdict

The TidesDB author's Dec 2025 benchtool run compared TidesDB v6.1.0 with RocksDB v10.7.5, both C libraries built with GCC -O3, on an i7-11700K with 48 GB RAM and a SATA SSD under Ubuntu 23.04: 8 threads, 16 B keys / 100 B values, no fsync. It measured iterator Seek() on 5M keys at 3.73M vs 893K ops/s random (4.17x), 8.87M vs 1.87M sequential (4.74x) and 3.56M vs 679K Zipfian (5.25x); 100-key scans were 2.41x faster and 1000-key scans 1.11x (a tie). Caveats: this is a first-party vendor result, the article's own conclusion quotes different figures (4.11x/4.58x/6.31x), and no C++ std baseline is involved.

## Use it when

- Seek-heavy or point-lookup-heavy workloads over small keys and values (16 B / 100 B in the benchmark) with a hot working set that fits in RAM: iterator Seek ran 4.2x (random), 4.7x (sequential) and 5.3x (Zipfian) faster than RocksDB 10.7.5 at 8 threads.
- Short range scans (about 100 keys) where positioning the iterator dominates the cost (2.41x faster than RocksDB at 100 random keys).
- Write-heavy ingest of values of 1 KiB and up where key/value separation pays: the author's v10.0.0 vs RocksDB 11.8.1 defaults run reports 2-10x faster seeding of a 10 GiB dataset and 2.5-5.4x lower write amplification.
- Embedded C/C++ services that want multi-column-family atomic transactions, MVCC snapshots, isolation levels up to serializable and XA two-phase commit in one library with no mandatory dependencies.
- Slow SATA-class storage under default RocksDB settings, where RocksDB's L0 write stalls dominate (the author's small-server median advantage was 3.8x, against 1.82x on NVMe).

## Skip it when

- Memory-constrained deployments (containers with \~2 GB limits, many instances per host). Peak RSS was 851 MB vs RocksDB's 246 MB in the seek benchmark, and 2.4-4.4x RocksDB's raw peak on three of four v10 keybench workloads. Filter directories are held outside the block-cache budget.
- Long range scans that need values. 1000-key ranges were a tie (1.11x, within variance per the author), there is no parallel value-log prefetch, and every separated value costs an extra read per entry.
- When you need RocksDB API compatibility, its tooling and ecosystem, or custom comparators. v10 removed comparators, so keys must be encoded to sort correctly by memcmp.
- When you need a stable on-disk format or a long-proven engine. Four major versions shipped between Dec 2025 (v6.1.0) and Sep 2026 (v10.0.0); 10.x cannot read 9.x files and migration is dump-and-reload. About 97% of commits come from one maintainer.
- Tight disk budgets. In the v10 keybench the store averaged about 2x its live data because of value-log retention, and the author says to size disks for the peak.

## How it is fast

The benchmarked v6.1.0 kept SSTable metadata resident until it was provably safe to free: sparse block indices, per-SSTable bloom filters (\~10 bits/key), min/max keys and open file handles. Its partitioned CLOCK block cache (2 shards per core, lock-free hits, atomic refcounts) held already-deserialized key-log blocks, so a seek to hot data needed no syscall, decompression or parsing. The current v10 line changes the structure. Each SSTable's key log is a B+tree whose parsed nodes are cached and whose root stays pinned, whole-file blooms are replaced by partitioned range filters, and WiscKey-style key/value separation keeps values of 1 KiB and up out of the tree, which shortens it. Compaction follows Spooky (partitioned merges on the largest level's boundaries, Dynamic Capacity Adaptation).

## Compared with alternatives

Pick TidesDB over TerarkDB (a RocksDB 5.18 fork that is drop-in for RocksDB) when you can adopt a new C API and want an actively maintained engine with MVCC transactions and key/value separation. Pick it over libmdbx or redb (B-tree engines) for write-heavy or large-value ingest and multi-column-family LSM workloads, accepting more RAM and format churn. Bourbon is a research artifact, not a library you would ship.

## Integration

| | |
|---|---|
| **Form** | shared lib (static by default on Windows); CMake package TidesDB::tidesdb, public header &lt;tidesdb/db.h&gt; |
| **Dependencies** | none mandatory (C standard library + threads; xxHash bundled); optional Snappy, LZ4, Zstd, and optionally mimalloc/tcmalloc/jemalloc |
| **Minimum toolchain** | C11 with atomics; CMake 3.12+; GCC 7+, Clang 6+, MSVC 2019 16.8+ (/experimental:c11atomics) |
| **Platforms** | Linux (x86, x64, ARM64, PowerPC32, RISC-V64), macOS (x64, Apple Silicon), Windows (x86/x64, MSVC and MinGW), FreeBSD/OpenBSD/NetBSD/DragonFlyBSD/Illumos/Solaris x64; 32-bit and PowerPC targets need libatomic |
| **Thread safety** | The tidesdb_t handle is thread-safe and meant to be shared by every thread. Transaction handles are not thread-safe (one thread per transaction; only tidesdb_txn_request_abort may cross threads). A directory can be opened by only one handle at a time, enforced by an OFD/flock/LockFileEx lock. |
| **Drop-in for the baseline** | false — different C API (transaction-scoped get/put/iterators, column families), no RocksDB API shim, and incompatible file formats |

## Gotchas

- Durability is off by default (memtable_sync_mode = TDB_SYNC_NONE). Set TDB_SYNC_FULL or TDB_SYNC_INTERVAL if acknowledged commits must survive a crash. The headline benchmark also ran with sync disabled on both engines.
- TDB_ERR_LOCKED from a read means a source was busy (memtable rotation, file-descriptor budget exhausted) and you must retry. The docs call treating it as not-found a correctness bug. TDB_ERR_CONFLICT likewise needs a retry loop.
- Buffers the library returns must be freed with tidesdb_free, never free(). With a non-default allocator build, calling free() crashes.
- The benchmarked seek path belongs to an architecture that no longer exists (block-format key logs, whole-file bloom filters). An iterator-seek correctness bug (issue #490: seek returned too few keys after reopen, due to a wrong early exit) was found against v7.0.2 and fixed in Dec 2025, so re-benchmark your own workload on v10.

## Known shortcomings

- Uses \~3.46x more RSS than RocksDB in the benchmark (851 vs 246 MB). The original benchtool repo now 404s; its code survives in a mirror (dhoard/tidesdb-benchtool).
- Speedups were measured on v6.1.0 (2025-12); v10 changed the read path (B+tree key logs, whole-file Bloom removed, custom comparators removed) and cannot read 9.x files (upgrade means dump and reload); v10 keybench shows 2.4-4.4x RSS on 3 of 4 workloads. The article contradicts itself (body 4.17/4.74/5.25x vs conclusion 4.11/4.58/6.31x); vendor-run with fsync off (also the default). 1000-key scans tie; \~97% of commits from one maintainer; own C API, not a RocksDB drop-in.

## Caveats and trade-offs

First-party vendor benchmark by the TidesDB author. The official benchtool repo (github.com/tidesdb/benchtool) now returns 404, and the code survives only in the mirror dhoard/tidesdb-benchtool. TidesDB uses 3.46x more memory (851 MB vs 246 MB peak RSS) because it keeps SSTable metadata resident. Large 1000-key ranges are essentially a tie (1.11x, within variance per the author). In the raw report the seek phase logs 'tidesdb (v6.0.2)' and RocksDB 'vunknown'. TidesDB is an LSM key-value storage engine rather than an index structure.

Gains attributed to aggressive caching design; large (1000-key) range queries show only a marginal 1.11x edge, so the advantage narrows for big scans; single-machine, single-hardware-config benchmark

## Maintenance

Very active (v10.0.2 released 2026-09-24, pushed 2026-09-26) and MPL-2.0 (file-level copyleft, fine to link from proprietary code), but effectively a one-maintainer project that breaks its on-disk format at each major release; the v6.1.0 design the headline numbers come from has since been replaced.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The Dec 17 2025 article states GCC -O3, an Intel Core i7-11700K, the OS/kernel and RocksDB v10.7.5, and links a raw report (benchmark_results_tdb610_rdb1075_range_seek1.txt) whose SEEK throughputs (3729450 vs 893870; 8867103 vs 1869637 ops/sec) match. The linked code, github.com/tidesdb/benchtool, is now 404. Its full history survives in the mirror dhoard/tidesdb-benchtool (commits by the TidesDB author, including 2e0d4b9d of 2025-12-16), so the code is public: tidesdb_rocksdb.sh test 11 'Seek Performance' plus engine_rocksdb.c / engine_tidesdb.c.
- **Verifier notes:** All claimed ratios and throughputs appear verbatim on the article (sequential 100-key ranges are an extra 1.14x). Metadata checked: MPL-2.0, 567 stars, not archived, not a fork; default-branch last commit 2026-09-25 (pushed_at 2026-09-26). Category 'indexes' is a loose fit for an LSM KV engine, but it cannot be corrected via this schema.
- **Fields the verifier corrected:** `last_commit`, `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://tidesdb.com/articles/benchmark-design-range-seek-tidesdb610-rocksdb1075/>
  - <https://tidesdb.com/benchmark_results_tdb610_rdb1075_range_seek1.txt>
  - <https://github.com/tidesdb/tidesdb>
  - <https://github.com/tidesdb/tidesdb/tree/master/bench>
  - <https://github.com/tidesdb/benchtool>
  - <https://github.com/dhoard/tidesdb-benchtool>
  - <https://github.com/dhoard/tidesdb-benchtool/blob/master/tidesdb_rocksdb.sh>
- **Sources the enricher read:**
  - <https://github.com/tidesdb/tidesdb>
  - <https://github.com/tidesdb/tidesdb/blob/master/README.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/VERSIONING.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/include/db.h>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/05-internals/architecture.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/05-internals/design-lineage.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/05-internals/life-of-a-read.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/05-internals/block-cache.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/05-internals/iterators.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/03-administration/building.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/04-reference/database.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/04-reference/transaction.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/06-appendix/configuration.md>
  - <https://github.com/tidesdb/tidesdb/blob/master/doc/02-concepts/transactions.md>
  - <https://github.com/tidesdb/tidesdb/releases/tag/v10.0.0>
  - <https://github.com/tidesdb/tidesdb/releases/tag/v6.1.0>
  - <https://github.com/tidesdb/tidesdb/issues/490>
  - <https://github.com/tidesdb/tidesdb/issues?q=label%3Abug>
  - <https://github.com/tidesdb/tidesdb/graphs/contributors>
  - <https://tidesdb.com/articles/benchmark-design-range-seek-tidesdb610-rocksdb1075/>
  - <https://tidesdb.com/blog>
  - <https://tidesdb.com/articles/keybench-analysis-tidesdb-10-0-0-rocksdb-11-8-1/>
  - <https://tidesdb.com/getting-started/>
  - <https://github.com/dhoard/tidesdb-benchtool>
  - <https://github.com/dhoard/tidesdb-benchtool/blob/master/engine_rocksdb.c>
  - <https://github.com/dhoard/tidesdb-benchtool/blob/master/benchmark.c>
  - <https://hn.algolia.com/api/v1/search?query=tidesdb&tags=story>
  - <https://news.ycombinator.com/item?id=46143861>
  - <https://news.ycombinator.com/item?id=46990959>
  - <https://news.ycombinator.com/item?id=43433420>
  - <https://news.ycombinator.com/item?id=49568059>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tidesdb/tidesdb`) · [data/wave6/enrich/raw/github_com_tidesdb_tidesdb.json](../../../data/wave6/enrich/raw/github_com_tidesdb_tidesdb.json) (enrichment confidence 0.8)

</details>
