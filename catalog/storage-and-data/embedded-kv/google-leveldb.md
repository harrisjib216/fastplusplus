# LevelDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's embedded ordered key-value LSM store; 10-17x SQLite3's write and scan rates in its 2011 benchmark.

| | |
|---|---|
| **Beats** | SQLite3 3.7.6.3 (also Kyoto Cabinet 1.2.67 TreeDB) |
| **Claimed result** | Baseline run, ops/sec LevelDB vs SQLite3: sequential reads 4,030,000 vs 383,000 (10.5x, derived from page data); sequential writes 779,000 vs 48,600 (16.0x, derived); random writes 164,000 vs 9,860 (16.6x, derived); batch random writes 221,000 vs 22,000 entries/s (10x, derived). Not faster everywhere: random reads 129,000 vs 134,000 for SQLite3 and 151,000 for Kyoto TreeDB; 100,000-byte values 1,100 vs 1,600 ops/sec sequential writes and 480 vs 1,600 random writes. |
| **Workload** | Google's July 2011 db_bench-derived suite: 1 million entries with 16-byte keys and 100-byte values (about 50% compressible), sequential and random reads and writes, 4 MB cache, asynchronous writes, plus batch, synchronous, large-value, no-compression and larger-cache variants. |
| **Metric** | throughput |
| **Hardware** | Six-core Intel Xeon X5650 @ 2.67GHz, 12 MB L3, 12 GB DDR3-1333, SATA 7200 RPM disks, ext3 and ext4 machines |
| **Compiler and flags** | Partly stated: LevelDB built with tcmalloc and Snappy (revision 33), assertions disabled; SQLite3 tuned with exclusive locking mode and write-ahead logging; TreeDB built with LZO 2.03 and TSMALL/TLINEAR options. Compiler and optimization level not stated. |
| **Adoption** | about 39.5k stars; used by Chromium (IndexedDB) and many bindings |
| **Last commit** | 2026-03-11 |
| **Links** | [repository](https://github.com/google/leveldb) · [benchmark](https://raw.githubusercontent.com/google/leveldb/HEAD/doc/benchmark.html) |

## Verdict

Google's July 2011 page ran single-threaded db_bench ports on a six-core Xeon X5650 with 7200 RPM SATA disks (ext3), 1M entries of 16-byte keys and 100-byte values, 4 MB of cache and asynchronous writes, comparing LevelDB revision 39 (tcmalloc, Snappy) against SQLite 3.7.6.3 (WAL, exclusive locking, 1 KB pages) and Kyoto Cabinet 1.2.67 TreeDB; LevelDB was 10.5x SQLite3 on sequential reads, 16x on sequential writes and 16.6x on random writes, but lost random reads and large-value writes. Compiler and flags are not stated and the numbers are 15 years old.

## Use it when

- Write-heavy or ingest-heavy local storage of small records (about 100-byte values) where asynchronous writes are acceptable; the 2011 page shows 164,000 random writes/s vs 9,860 for SQLite3.
- Ordered range scans and prefix iteration over sorted keys: 4.03M sequential reads/s vs 383,000 for SQLite3 and 1.01M for Kyoto TreeDB on the same page.
- Applications that want a small, stable-API C++ library with no mandatory dependencies, such as browser or desktop storage (the record lists Chromium's IndexedDB as a user).
- Batched atomic updates through WriteBatch, including group commits with sync=true to amortise fsync cost.

## Skip it when

- Read-dominated random point lookups: LevelDB lost random reads to both SQLite3 (129,000 vs 134,000 ops/s) and Kyoto TreeDB (151,000), and with a 128 MB cache TreeDB reached 463,000 vs LevelDB's 190,000.
- Large values: at 100,000-byte values LevelDB managed 1,100 sequential and 480 random writes/s vs 1,600 for SQLite3, because every value is written at least twice (log, then compaction).
- Multi-process access, SQL queries, secondary indexes or transactions beyond single WriteBatches; only one process can open a database.
- Synchronous-durable writes on ext4: the page reports LevelDB dropping to about 31 sync writes/s while SQLite3 did not noticeably drop.
- Projects that need active development or new features: the README says only critical fixes and changes needed by Google's internal clients are reviewed, and build-system contributions are unlikely to be accepted.

## How it is fast

It is a log-structured merge tree: each write is appended to a log and inserted into an in-memory skiplist memtable, which is flushed (about every 4 MB) into immutable sorted tables that background compaction merges level by level (10 MB for level 1, 100 MB for level 2, and so on). Writes therefore turn into sequential appends and bulk merges instead of in-place B-tree page updates, and sequential scans read sorted, Snappy-compressed 4 KB blocks. An LRU block cache and optional Bloom filters cut random-read cost.

## Compared with alternatives

Pick LevelDB over LMDB when the workload is write-heavy with small values and asynchronous writes, and LMDB (B+tree, mmap, multi-process readers) when reads dominate or several processes share the store; pick it over HyperLevelDB or the RocksDB-derived siblings (Speedb, ToplingDB, Pebble) when a small, stable, dependency-free library matters more than multi-threaded write throughput and tuning knobs.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, BUILD_SHARED_LIBS) |
| **Dependencies** | none required; optional Snappy, Zstd, crc32c and tcmalloc are linked when found; googletest and google benchmark submodules only for tests and benchmarks |
| **Minimum toolchain** | C++17 and CMake 3.22 (raised in the 2026-03-11 commit); built with -fno-exceptions and -fno-rtti |
| **Platforms** | POSIX (Linux, macOS) and Windows are the tested platforms; other OSes via a custom Env |
| **Thread safety** | One DB object may be shared by many threads in one process without external locking; Iterator and WriteBatch objects need external synchronisation; an OS file lock stops a second process from opening the same database. |
| **Drop-in for the baseline** | no |

## Gotchas

- Bloom filters are off by default (Options::filter_policy is null, db_bench uses --bloom_bits=-1), so a missing-key Get can probe every level; set NewBloomFilterPolicy(10) for random-read workloads that do not fit in memory.
- Writes default to sync=false: a Put survives a process crash but recent writes can be lost on a machine crash; the 2011 headline numbers all use asynchronous mode, and the page notes the disks had write caching enabled.
- Deleted data is reclaimed only by compaction: open issue #603 reports disk use growing without bound under a write-then-batch-delete cycle with 9 KB-500 KB values, and the reporter had to consider manual CompactRange calls.
- Harness note: the 2011 SQLite3 numbers come from a table with a rowid plus a separate primary-key index (two B-trees per row); the repo only made WITHOUT ROWID the default in the 2019-12-02 commit 'Add WITHOUT ROWID to SQLite benchmark', so today's benchmarks/db_bench_sqlite3.cc does not reproduce the measured SQLite setup and part of the 10-17x write gap reflects that schema. The SQLite readseq byte counter also reads result columns 1 and 2 (0-based, column 2 does not exist), so its MB/s figure is wrong; ops/s is unaffected.

## Known shortcomings

- First-party 2011 benchmark page with compiler and flags unstated; loses random reads and 100 KB values, and ext4 sync writes go to SQLite.
- Enricher: the 2011 SQLite numbers used a rowid table plus a separate key index (two B-trees); WITHOUT ROWID became the benchmark default only in the 2019-12-02 commit, so today's db_bench_sqlite3.cc cannot reproduce that setup and part of the 10-17x write gap reflects the old schema. The SQLite readseq byte counter reads columns 1 and 2 (column 2 does not exist), so its MB/s is wrong (ops/s unaffected). Bloom filters are off by default; issue #603 (disk grows without bound) is open; C++17 and CMake 3.22 minimum since 2026-03-11.

## Caveats and trade-offs

Numbers are from Google's July 2011 page (LevelDB revision 39 vs SQLite 3.7.6.3 and Kyoto Cabinet 1.2.67 TreeDB), first-party, with the benchmark code in the repo; compiler and optimisation flags are not stated, so the tier is C. The SQLite side was reasonably tuned (WAL, exclusive locking mode, reused prepared statements, a 4 MB cache of 1024-byte pages) but is a 2011 release, and the baseline runs have synchronous writes off for every engine. LevelDB loses on random reads (129,000 ops/s vs 134,000 for SQLite3 and 151,000 for Kyoto TreeDB) and with 100,000-byte values (1,100 vs 1,600 ops/s sequential and 480 vs 1,600 random writes). Synchronous writes are near parity on ext3 (100 vs 88 ops/s), and the page says ext4 drops LevelDB to about 31 sync writes per second while SQLite3 does not noticeably drop, so on ext4 SQLite3 wins synchronous writes. RocksDB and LMDB, the other category baselines, are not in this benchmark. The README says the repository receives very limited maintenance (only critical fixes and changes needed by internal clients are reviewed). Mozilla's kvbench (mykmelez/kvbench, Rust bindings) measured LMDB opening a database about 8x faster than LevelDB, while LevelDB was faster on a single synchronous 1-byte put (58.691 us vs 114.74 us).

LSM tree with ordered keys, no transactions (WriteBatch only), single process access, compaction pauses and write amplification (large values written twice, 1,100 vs 1,600 SQLite ops/sec at 100 KB); only a single process may open a database at a time; no SQL, relational model or indexes and no client-server layer (per its README Limitations).

## Maintenance

Active only for critical fixes and Google-internal needs (last commits 2026-03-11 moved it to C++17 and CMake 3.22); BSD-3-Clause, about 39.5k stars, 263 open issues and 153 open PRs, so it is safe to vendor but do not expect new features.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google page (July 2011) with public benchmark code (benchmarks/db_bench.cc, db_bench_sqlite3.cc, db_bench_tree_db.cc, all still in the repo) and a stated CPU (Xeon X5650), but no compiler or optimisation flags, so it falls short of A; first-party with partial methodology is C.
- **Verifier notes:** All claimed numbers and derived ratios match doc/benchmark.html (seq reads 10.5x, seq writes 16.0x, random writes 16.6x, batch random writes 10x vs SQLite3), and the losses (random reads, large values) are recorded. Fixed baseline_in_list to true (SQLite is in the embedded-kv baseline list) and replaced a caveat sentence that named std::map as a suggested baseline. Metadata checks out: BSD-3-Clause, about 39.5k stars, last commit 2026-03-11, active but README declares very limited maintenance; record shortcomings: 2011 numbers, compiler and flags unstated, loses random reads and large values, ext4 sync writes slower than SQLite.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** first-party 2011 page (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/doc/benchmark.html>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench_sqlite3.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench_tree_db.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/LICENSE>
  - <https://github.com/google/leveldb>
  - <https://github.com/google/leveldb/commits/main.atom>
  - <https://raw.githubusercontent.com/mykmelez/kvbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/google/leveldb>
  - <https://github.com/google/leveldb/commits/main.atom>
  - <https://github.com/google/leveldb/commits/main/benchmarks/db_bench_sqlite3.cc.atom>
  - <https://github.com/google/leveldb/issues?q=is%3Aissue+label%3Abug+>
  - <https://github.com/google/leveldb/issues/603>
  - <https://github.com/google/leveldb/issues/693>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/doc/benchmark.html>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/doc/index.md>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/doc/impl.md>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench_sqlite3.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/benchmarks/db_bench_tree_db.cc>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/include/leveldb/db.h>
  - <https://raw.githubusercontent.com/google/leveldb/HEAD/include/leveldb/options.h>
  - <https://raw.githubusercontent.com/mykmelez/kvbench/HEAD/README.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/google/leveldb`) · [data/wave6/enrich/raw/github_com_google_leveldb.json](../../../data/wave6/enrich/raw/github_com_google_leveldb.json) (enrichment confidence 0.85)

</details>
