# LMDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `OLDAP-2.8` · 🟢 active

> Memory-mapped copy-on-write B+tree key-value store in C; 4.6-8.8x faster reads than RocksDB in redb's harness.

| | |
|---|---|
| **Beats** | RocksDB (rust-rocksdb 0.22.0 with LZ4, 4 GiB LRU block cache, bloom filters, OptimisticTransactionDB snapshot reads); SQLite (rusqlite 0.37 bundled, default settings, BLOB PRIMARY KEY table) is also in the table, but its adapter re-prepared every SQL statement per operation (see caveats) |
| **Claimed result** | Times in ms, lower is better, from the redb README table (last regenerated 2025-08-08); all ratios derived from page data. Against RocksDB: random reads 637 vs 2911 (4.6x); random range reads 565 vs 2734 (4.8x); random reads with 4, 8, 16 and 32 threads 840 vs 3995 (4.8x), 427 vs 2147 (5.0x), 216 vs 1478 (6.8x) and 125 vs 1100 (8.8x); individual sync writes 1598 vs 2432 (1.5x); bulk load 9232 vs 13969 (1.5x). LMDB loses to RocksDB on batch writes (942 vs 451, 2.1x slower) and removals (10435 vs 6900, 1.5x slower), and its uncompacted file is 2.61 GiB vs 893.18 MiB (3.0x larger). Against SQLite (handicapped adapter, see caveats): random reads 637 vs 4283 (6.7x); random range reads 565 vs 8431 (14.9x); 16 and 32 threads 216 vs 23022 (107x) and 125 vs 26536 (212x); individual writes 1598 vs 7040 (4.4x); batch writes 942 vs 2625 (2.8x); bulk load 9232 vs 15341 (1.7x); removals 10435 vs 10323 (parity, LMDB 1% slower); uncompacted size 2.61 GiB vs 1.09 GiB (LMDB 2.4x larger). |
| **Workload** | redb author's comparison harness as of commit d6773ef (2025-08-08): 5M random pairs (24-byte keys, 150-byte values) bulk-loaded in one transaction, 1,000 individual synchronous write transactions, 100 batches of 1,000 writes, 1M random point reads and 500k random 10-element range scans (each run twice and printed as two rows), random reads with 4, 8, 16 and 32 threads (about 5.1M lookups split across the threads), then removal of about 2.55M keys in one transaction; 4 GiB cache for the engines that take one (4 GiB map size for LMDB, no cache pragma for SQLite); LMDB driven through the Rust heed 0.22 binding. |
| **Metric** | throughput |
| **Hardware** | Ryzen 9950X3D with Samsung 9100 PRO NVMe (per README) |
| **Compiler and flags** | cargo bench (the bench profile inherits release optimisation; the workspace Cargo.toml adds debug = true); rustc version not stated (workspace MSRV 1.89). C compiler and flags for the bundled LMDB (heed 0.22), RocksDB (rust-rocksdb 0.22.0, lz4 feature) and SQLite (rusqlite 0.37 bundled) come from those crates' build scripts and are not stated. |
| **Adoption** | about 3.0k stars on the GitHub mirror; embedded in OpenLDAP and widely bound from other languages |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/LMDB/lmdb) · [benchmark](https://raw.githubusercontent.com/cberner/redb/master/README.md) |

## Verdict

redb's author ran his public Rust harness (commit d6773ef, 2025-08-08; LMDB driven through heed 0.22) on a Ryzen 9950X3D with a Samsung 9100 PRO NVMe drive, with the OS and compilers unstated, on 5.1M random 24/150-byte pairs held in RAM. LMDB was 4.6x faster than RocksDB 0.22 (LZ4, 4 GiB block cache, bloom filters, snapshot reads) on random point reads, 4.8x faster on range scans, 4.8-8.8x faster with 4 to 32 reader threads, and 1.5x faster on bulk load and on single-put synced commits, but 2.1x slower on 1,000-put batch commits, 1.5x slower on bulk removals, and its file was 3x larger. The SQLite ratios in the same table (up to 212x) come from an adapter that re-prepared every statement and ran SQLite untuned, so they should not be used.

## Use it when

- Read-dominated workloads whose data or hot set fits in RAM: in redb's harness (5.1M random 24-byte keys with 150-byte values, about a 2.6 GiB LMDB file) LMDB did 1M random point reads in 637 ms vs RocksDB's 2911 ms and 500k ten-element range scans in 565 ms vs 2734 ms.
- Many concurrent reader threads or processes on one database: lock-free readers did 5.1M lookups in 125 ms with 32 threads, about 40.8M lookups/s vs about 4.6M/s for RocksDB (derived from page data).
- Embedded metadata, configuration, index or directory stores that need ACID commits with no recovery step, background threads or tuning knobs; with default sync settings a single-put durable commit cost about 1.6 ms vs 2.4 ms for RocksDB with sync=true on an NVMe drive.
- Code that benefits from zero-copy values (pointers into the map, valid until the transaction ends), or bulk loads of pre-sorted keys with MDB_APPEND, which skips key comparisons.
- C or C++ projects that want a small, permissively licensed dependency: two C files (mdb.c, midl.c) and one header, callable from C++ through extern "C".

## Skip it when

- Write-heavy random workloads with batched commits: 100 commits of 1,000 random puts took 942 ms vs 451 ms for RocksDB (2.1x slower) and 353 ms for fjall, and deleting 2.55M keys took 10435 ms vs 6900 ms, because every random update copies whole 4 KiB pages up to the root.
- Disk-space or SSD-wear sensitive deployments: there is no compression and the file never shrinks; the same table shows 2.61 GiB vs 893 MiB for RocksDB before compaction and 1.26 GiB vs 455 MiB after, and compaction is only available as a copy to a new file (mdb_env_copy2 with MDB_CP_COMPACT).
- Multiple concurrent writers (one write transaction at a time per environment, across all processes) or long-lived read transactions, which pin freed pages and make the file grow quickly.
- Data sets far larger than RAM or random reads on slow storage: the cited benchmark is fully memory-resident, and beyond RAM every miss is a synchronous page fault; the header suggests MDB_NORDAHEAD for that case and it is not implemented on Windows.
- Network or remote filesystems (explicitly unsupported in lmdb.h), or applications that cannot choose a maximum database size up front.

## How it is fast

The whole data file is mapped read-only into memory, and reads walk the B+tree in the map and return pointers into it, so a lookup does no malloc, memcpy or user-space cache lookup (the header: 'no malloc's or memcpy's occur during data fetches'); the OS page cache is the only cache. Concurrency is MVCC by shadow paging: a writer copies the touched leaf-to-root path and commits by updating one of two alternating meta pages, while readers only record their snapshot txnid in a cache-line-padded slot of a shared reader table and take no locks, which is why its lead over RocksDB grows with reader threads (4.8x at 4 threads, 8.8x at 32). Pages freed by old versions are tracked in an internal free-list database and reused once no reader can see them, so there is no write-ahead log, checkpointing or compaction work. The price is a single serialized writer and whole-page copy-on-write for every random update.

## Compared with alternatives

Pick LMDB over the RocksDB-family siblings (Badger, Pebble, Speedb, ToplingDB) when reads dominate, the working set fits in RAM, many threads or processes read at once, and you want zero tuning; pick those LSM engines when writes, deletes or disk footprint dominate. UnisonDB claims about 3x LMDB's SET throughput (tier C), and the catalogue also lists libmdbx (an LMDB fork claiming 10-30% gains, first-party) and redb (pure Rust, faster than LMDB on single durable commits but slower on every read row of the same table).

## Integration

| | |
|---|---|
| **Form** | source-drop (mdb.c, midl.c, lmdb.h); the Makefile also builds liblmdb.a and liblmdb.so |
| **Dependencies** | none beyond the C library, mmap and pthreads |
| **Minimum toolchain** | Any C compiler with pthreads (Makefile default: gcc -pthread -O2 -g); a minimum C standard is not documented |
| **Platforms** | Linux, BSDs, macOS, Windows and Android; 0.9.34 added NetBSD and Haiku. Needs mmap and working file locks, so not on network filesystems. LMDB 0.9 and 1.0 on-disk formats are mutually incompatible. |
| **Thread safety** | An environment can be shared by threads and processes. A transaction and its cursors belong to one thread, and a thread may hold one transaction at a time (MDB_NOTLS lifts this for read-only transactions). Writes are serialized env-wide; readers never block writers or each other. Do not open the same environment twice in one process or use it after fork(). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetries in the cited redb table (commit d6773ef; the code is unchanged in the current crates/redb-bench-compare): the RocksDB adapter splits the 5M-key bulk load and the 2.55M-key removal into transactions of about 100,000 operations (the ROCKSDB_MAX_WRITES_PER_TXN 'awful hack'), and every chunk after the first is committed through db.transaction(), which uses default WriteOptions and therefore does not sync. RocksDB's removal win (6900 vs 10435 ms) and its bulk-load time are therefore neither atomic nor durable, while LMDB's are single fsynced transactions. In the other direction, RocksDB reads return a heap-allocated Vec copy (snapshot.get) and range iterators return boxed key and value copies, whereas LMDB returns pointers into the map and the harness touches only the first byte, which slightly favours zero-copy engines. The OS, rustc version and C compiler are not stated.
- The benchmarked LMDB is not a release: heed 0.22 bundles lmdb-master-sys 0.2.5, which builds the mdb.master development branch at commit f20e41d (version string 0.9.70) with NDEBUG and MDB_IDL_LOGN=16. LMDB 1.0.0 (2026-06-30) and 1.0.1 (2026-08-06) changed the on-disk format (page headers now carry txn IDs; optional page checksums and encryption; page sizes up to 64 KB) and cannot open 0.9 files, so migrating needs mdb_dump with 0.9 and mdb_load with 1.0. LMDB 1.0's performance has not been measured by this harness. A FreeBSD ports search snippet (page blocked here, snippet only) says some applications compiled against 1.0 headers failed silently at run time.
- The map size is the hard maximum database size, and the compiled default is only 1 MiB (mdb.c DEFAULT_MAPSIZE; the header comment says 10 MiB). Writes fail with MDB_MAP_FULL when it is exceeded, and it can only be raised with mdb_env_set_mapsize while the process has no active transactions. The harness used 4 GiB for a 2.61 GiB file. Keys are limited to 511 bytes in 0.9 builds, and in 1.0 the limit depends on the page size.
- Durability and maintenance traps: MDB_NOSYNC and MDB_WRITEMAP trade crash safety or corruption protection for speed. On macOS older versions did not fully sync commits: redb's harness fsyncs every file after each LMDB commit on macOS, and upstream fixed fdatasync (ITS#10296, 0.9.34) and metapage sync (ITS#10454, 0.9.36) there. Reader slots left by crashed processes block page reuse until mdb_reader_check runs. The GitHub repository is a read-only mirror; bugs go to the OpenLDAP ITS.

## Known shortcomings

- The redb README table (regenerated 2025-08-08) re-prepared every SQLite statement per call and ran SQLite untuned (no WAL, default cache, autocommit threaded reads), so the 107x/212x threaded ratios are harness artifacts; rebased to RocksDB: reads 4.6-8.8x faster, but LMDB loses batch writes and removals and uses 3.0x the disk. Compiler unstated.
- Enricher: the redb adapter splits RocksDB bulk load (5M) and removals (2.55M) into \~100k-op transactions (ROCKSDB_MAX_WRITES_PER_TXN hack) whose later chunks commit with default WriteOptions (no sync, not atomic), so the RocksDB removal win (6900 vs 10435 ms) is not like-for-like; RocksDB get and range return copies while LMDB is zero-copy and the harness reads only byte 0; dataset in RAM, OS unstated. The benchmarked LMDB is heed 0.22's bundled mdb.master f20e41d (0.9.70 dev), not a release; LMDB 1.0.0/1.0.1 (2026) change the on-disk format and are unmeasured. Default map size is 1 MiB (header says 10 MiB), MDB_MAP_FULL; macOS sync fixes ITS#10296/10454.

## Caveats and trade-offs

The numbers come from a competing project's (redb) README, not from the LMDB authors, and LMDB is reached through the heed 0.22 Rust wrapper. The table was last regenerated on 2025-08-08 (commit d6773ef; the 2026-07-15 commit only removed the sled column), so it reflects that commit's harness and crate versions (rusqlite 0.37, rust-rocksdb 0.22.0), not the current crates/redb-bench-compare harness (rusqlite 0.38, rocksdb 0.24, median of 3 runs) that the README now links. At that commit the SQLite adapter called conn.prepare or execute inside every get, range scan, insert and delete, so each SQLite operation recompiled its SQL statement; SQLite also ran with no tuning pragmas (rollback journal, no WAL, default page cache of about 2 MB versus 4 GiB for redb, RocksDB and fjall), and in the threaded rows each lookup is its own autocommit statement on a per-thread connection, which likely explains why SQLite slows down as threads are added (7000 ms with 4 threads, 26536 ms with 32 threads for the same 5.1M lookups). The SQLite ratios, above all the 107x and 212x threaded ones, therefore overstate LMDB's lead over a normally used SQLite; current master prepares the read statements once per reader, but the README was not re-run. RocksDB was configured sensibly (4 GiB block cache, bloom filters, snapshot reads), and against it LMDB wins reads by 4.6-8.8x but loses batch writes and removals and uses about 3x more disk. Compiler version and flags are not stated. The primary LMDB claim, the Symas/lmdb.tech microbench against SQLite, BerkeleyDB, Kyoto Cabinet and LevelDB, could not be opened (host blocked). A second, weaker data point from Mozilla's kvbench (mykmelez/kvbench README, Rust bindings, hardware not stated) shows LMDB opening a database about 8x faster than LevelDB (166.70 us vs 1.3895 ms, derived from page data) but slower on a single synchronous 1-byte put (114.74 us vs 58.691 us). [retier] The numbers come from a competing project's (redb) README, not from the LMDB authors, and LMDB is reached through the heed 0.22 Rust wrapper. The table was last regenerated on 2025-08-08 (commit d6773ef; the 2026-07-15 commit only removed the sled column), so it reflects that commit's harness and crate versions (rusqlite 0.37, rust-rocksdb 0.22.0), not the current crates/redb-bench-compare harness (rusqlite 0.38, rocksdb 0.24, median of 3 runs) that the README now links. At that commit the SQLite adapter called conn.prepare or execute inside every get, range scan, insert and delete, so each SQLite operation recompiled its SQL statement; SQLite also ran with no tuning pragmas (rollback journal, no WAL, default page cache of about 2 MB versus 4 GiB for redb, RocksDB and fjall), and in the threaded rows each lookup is its own autocommit statement on a per-thread connection, which likely explains why SQLite slows down as threads are added (7000 ms with 4 threads, 26536 ms with 32 threads for the same 5.1M lookups). The SQLite ratios, above all the 107x and 212x threaded ones, therefore overstate LMDB's lead over a normally used SQLite; current master prepares the read statements once per reader, but the README was not re-run. RocksDB was configured sensibly (4 GiB block cache, bloom filters, snapshot reads), and against it LMDB wins reads by 4.6-8.8x but loses batch writes and removals and uses about 3x more disk. Compiler version and flags are not stated. The primary LMDB claim, the Symas/lmdb.tech microbench against SQLite, BerkeleyDB, Kyoto Cabinet and LevelDB, could not be opened (host blocked). A second, weaker data point from Mozilla's kvbench (mykmelez/kvbench README, Rust bindings, hardware not stated) shows LMDB opening a database about 8x faster than LevelDB (166.70 us vs 1.3895 ms, derived from page data) but slower on a single synchronous 1-byte put (114.74 us vs 58.691 us). Enricher (2026-10-07): the redb adapter splits RocksDB bulk load (5M) and removals (2.55M) into \~100k-op transactions (ROCKSDB_MAX_WRITES_PER_TXN) whose later chunks commit with default WriteOptions, no sync and not atomic, so the RocksDB removal win (6900 vs 10435 ms) is not like-for-like; RocksDB get/range return copies while LMDB is zero-copy and the harness reads only byte 0. The benchmarked LMDB is heed 0.22's bundled mdb.master f20e41d (0.9.70 dev), not a release; LMDB 1.0.x (2026) changes the on-disk format and is unmeasured.

Single writer at a time (readers never block); copy-on-write B+tree with no compaction or compression, so the file is larger than compacting engines (the same table shows 2.61 GiB uncompacted vs 893 MiB for RocksDB and 1.09 GiB for SQLite); fixed maximum map size must be chosen up front; no SQL layer or secondary indexes; removals and mixed workloads are less favourable (loses removals to RocksDB and fjall in the same table).

## Maintenance

Actively maintained: mdb.master3 had commits on 2026-08-19, and 0.9.36 and 1.0.1 were released on 2026-08-06. The OpenLDAP Public License 2.8 is permissive and the library is two C files, so it is easy to vendor, but choose the 0.9 (mdb.RE/0.9) or 1.0 (mdb.RE/1.0) line deliberately because their file formats are incompatible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement: redb's author ran a public harness (crates/redb-bench/benches/lmdb_benchmark.rs and common.rs at commit d6773ef, the 2025-08-08 commit that last regenerated the README table) on a stated CPU (Ryzen 9950X3D), but the rustc version and the C compiler and flags for the bundled LMDB, RocksDB and SQLite are not stated, so it falls short of A. Tier B rests on the RocksDB comparison; the SQLite rows come from a handicapped adapter and include &gt;50x ratios that on their own would cap the entry at C.
- **Verifier notes:** README numbers match the record, but the SQLite comparison is handicapped: the harness that produced them (commit d6773ef) re-prepared every SQL statement per call, ran SQLite untuned, and the 107x/212x threaded ratios are harness artifacts, so I rebased the baseline on RocksDB (also a category baseline, same table, sensible config: 4.6-8.8x on reads, LMDB slower on batch writes and removals) and kept SQLite rows with the flaw spelled out; tier stays B. Record shortcoming: SQLite baseline handicapped (per-call statement preparation, default cache, no WAL), README table from 2025-08 harness not current one, compiler and flags unstated. Metadata: OLDAP-2.8 (libraries/liblmdb/LICENSE), about 3.0k stars, read-only mirror of openldap.org (not a GitHub fork), last commit 2026-08-19 on default branch mdb.master3 (record said 2026-06-24), active.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Shortcomings recorded by:** redb README (verifier downgrade, claim overstated); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cberner/redb/master/README.md>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench-compare/benches/lmdb_benchmark.rs>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench-compare/benches/common/mod.rs>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench-compare/Cargo.toml>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench/src/lib.rs>
  - <https://raw.githubusercontent.com/cberner/redb/master/Cargo.toml>
  - <https://github.com/cberner/redb/commits/master/README.md.atom>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/README.md>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/Cargo.toml>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/benches/lmdb_benchmark.rs>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/benches/common.rs>
  - <https://github.com/LMDB/lmdb>
  - <https://github.com/LMDB/lmdb/commits/mdb.master3.atom>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/LICENSE>
  - <https://raw.githubusercontent.com/mykmelez/kvbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/LMDB/lmdb>
  - <https://github.com/LMDB/lmdb/tags>
  - <https://github.com/LMDB/lmdb/branches/all>
  - <https://github.com/LMDB/lmdb/commits/mdb.master3>
  - <https://github.com/LMDB/lmdb/commit/f20e41d>
  - <https://github.com/LMDB/lmdb/tree/mdb.RE/1.0/libraries/liblmdb>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/lmdb.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/mdb.c>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/Makefile>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/LICENSE>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/COPYRIGHT>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master3/libraries/liblmdb/intro.doc>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master/libraries/liblmdb/lmdb.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.master/libraries/liblmdb/midl.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/f20e41d/libraries/liblmdb/lmdb.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/f20e41d/libraries/liblmdb/mdb.c>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/1.0/libraries/liblmdb/CHANGES>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/1.0/libraries/liblmdb/lmdb.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/1.0/libraries/liblmdb/upgrading.doc>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/1.0/libraries/liblmdb/midl.h>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/1.0/libraries/liblmdb/intro.doc>
  - <https://raw.githubusercontent.com/LMDB/lmdb/mdb.RE/0.9/libraries/liblmdb/CHANGES>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/README.md>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/Cargo.toml>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/benches/lmdb_benchmark.rs>
  - <https://raw.githubusercontent.com/cberner/redb/d6773ef554d059e3f8ca357fe4931f2c5995c340/crates/redb-bench/benches/common.rs>
  - <https://raw.githubusercontent.com/cberner/redb/master/README.md>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench-compare/benches/common/mod.rs>
  - <https://raw.githubusercontent.com/cberner/redb/master/crates/redb-bench-compare/benches/lmdb_benchmark.rs>
  - <https://github.com/cberner/redb/pull/928>
  - <https://raw.githubusercontent.com/meilisearch/heed/v0.22.0/lmdb-master-sys/build.rs>
  - <https://raw.githubusercontent.com/meilisearch/heed/v0.22.0/lmdb-master-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/meilisearch/heed/v0.22.0/.gitmodules>
  - <https://github.com/meilisearch/heed/tree/v0.22.0/lmdb-master-sys>
  - <https://crates.io/api/v1/crates/heed/versions>
  - <https://crates.io/api/v1/crates/heed/0.22.0/dependencies>
  - <https://crates.io/api/v1/crates/lmdb-master-sys/versions>
  - <https://raw.githubusercontent.com/rust-rocksdb/rust-rocksdb/v0.22.0/src/transactions/optimistic_transaction_db.rs>
  - <https://raw.githubusercontent.com/rust-rocksdb/rust-rocksdb/v0.22.0/src/snapshot.rs>
  - <https://github.com/fjall-rs/fjall>
  - WebSearch: LMDB 1.0 released 2026 Howard Chu file format incompatible performance (snippets from freshports.org and lists.openldap.org; both pages EGRESS_BLOCKED)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/lmdb/lmdb`) · [data/wave6/enrich/raw/github_com_lmdb_lmdb.json](../../../data/wave6/enrich/raw/github_com_lmdb_lmdb.json) (enrichment confidence 0.8)

</details>
