# HyperLevelDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> HyperDex's LevelDB 1.17 fork with parallel writers and cheaper compaction; about 3.4x faster bulk writes than LevelDB, but slower reads.

| | |
|---|---|
| **Beats** | LevelDB |
| **Claimed result** | Writing 100M values took 10m45.41s with HyperLevelDB vs 36m8.29s with LevelDB (\~3.36x faster, derived from page data) and 21m18.60s with RocksDB. HyperLevelDB lost the other steps: querying 100M values took 13m49.01s vs 2m55.37s for LevelDB (\~4.7x slower, derived from page data), and it was also slower than LevelDB on delete (6m0.38s vs 3m47.64s) and compaction (6m33.36s vs 3m59.87s). |
| **Workload** | InfluxDB storage-engine shootout: 100 million key-value pairs across 500,000 series columns, 24-byte (3-int) keys, protobuf-serialized values, batches of 1,000 writes; write N, query N, delete N/2, compact, query remaining N/2, write N/2 more. |
| **Metric** | throughput |
| **Hardware** | DigitalOcean droplet: 4GB RAM, 2 CPU cores, 60GB SSD (exact CPU model not stated) |
| **Adoption** | 464 stars |
| **Last commit** | 2016-02-16 |
| **Links** | [repository](https://github.com/rescrv/HyperLevelDB) · [benchmark](https://www.influxdata.com/blog/2014/06/20/leveldb_vs_rocksdb_vs_hyperleveldb_vs_lmdb_performance.html) |

## Verdict

InfluxData, which is independent of HyperLevelDB, ran a 2014 test on a 2-core, 4 GB DigitalOcean SSD droplet with default, untuned settings; compiler, flags and engine versions are not stated. It wrote 100M 24-byte keys with small protobuf values in 1,000-item batches. HyperLevelDB wrote them in 10m45s vs 36m08s for LevelDB (\~3.4x) and 21m19s for RocksDB, but range-queried them \~4.7x slower than LevelDB (13m49s vs 2m55s) and lost on delete and compaction. In the same gist, the 3M-point SSD run had HyperLevelDB writing slower than LevelDB (21.0s vs 18.0s), and only the magnetic-disk 3M run showed a write win (30.4s vs 46.1s).

## Use it when

- An existing LevelDB C++ codebase on x86-64 Linux where ingest throughput is the bottleneck and a move to RocksDB is not on the table.
- Write-once, read-later bulk loads such as time-series or event logs written in batches. In InfluxData's 2014 test, 100M small points loaded in 10m45s vs 36m08s for LevelDB.
- Many application threads writing at once. The authors' own 4-thread, 128-byte-value test showed 2-4x the throughput of LevelDB, RocksDB and Basho's fork (first-party graphs only).
- You need a cheap live backup (hard links) or a change feed (ReplayIterator from a timestamp) on a LevelDB-style store, as HyperDex did.
- As a research or reference baseline: PebblesDB is built by modifying HyperLevelDB and stays API-compatible with it.

## Skip it when

- Read- or scan-heavy workloads. In the same InfluxData run, range-querying 100M values took 13m49s vs 2m55s for LevelDB (\~4.7x slower), and delete and compaction were also slower (6m00s vs 3m48s, 6m33s vs 4m00s).
- Non-x86 hardware or Windows. util/atomic.h is hand-written x86 inline assembly (mfence, lock cmpxchg, MMX for 32-bit). The maintainer declined std::atomic and arm64 ports (issues #19, #21), and Windows support was never planned (#18).
- Anything that needs a maintained engine. The last commit (2016-02-16) fixed a memory leak. In 2018 the maintainer declined to tag a release because he could not vouch for its quality (#22). The code is frozen at LevelDB 1.17.
- Processes that open and close the DB often. Background threads start at Open and are never joined, so each open/close cycle leaks thread stacks. In #4 that was about 24 MB of virtual memory per cycle, and the fix was 'keep it open'.
- Small or single-threaded workloads and tight disk budgets. In the gist's 3M-point SSD run, writes were slower than LevelDB's (21.0s vs 18.0s), and the DB was 206 MB vs 78 MB after the load.

## How it is fast

Writes: in LevelDB, the writer at the head of a FIFO does all the work behind one mutex. Here each writer reserves a sequence-number range with an atomic fetch-add, appends to an mmap-backed log that hands out non-overlapping regions, and inserts into a concurrent skip list that traverses without the lock and only validates under it. Only visibility (last sequence) and ordering are serialized. Compaction: the picker chooses the contiguous run of level-N files with the highest bytes(N)/bytes(N+1 overlap) ratio, capped at 16x the level's file size, so each compaction rewrites as few bytes as possible; it does trivial moves first. Memtable flush and level compaction run on two separate background threads, using per-level locks. Level sizes are hard-coded larger than LevelDB's: L0 64 MB, L1 128 MB, L2 512 MB, then 8x per level, with SSTs of up to 64 MB.

## Compared with alternatives

PebblesDB is HyperLevelDB plus FLSM guards, with the same API, reports higher write throughput, and was updated as recently as 2024, so it is usually the better pick in this lineage. Choose HyperLevelDB only when you want the smallest, simplest step from LevelDB (no guard layer), or to match an existing HyperDex deployment. For a new project, a RocksDB-based sibling (Speedb, Titan, ToplingDB) avoids being stuck on a 2014 LevelDB codebase.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools/libtool build of libhyperleveldb; a static archive is also produced) |
| **Dependencies** | pthread; Snappy is optional and auto-detected by configure. Building from git needs autoconf 2.62+ and libtool 2.2+. The optional 'benchmark' tool also needs libe, popt and ygor. |
| **Minimum toolchain** | Pre-C++11 code: it uses std::tr1::shared_ptr unless built against libc++, plus GCC __sync builtins and GCC-style inline asm, and configure sets no -std flag. Last fixed for GCC/Clang in 2014 (OS X Mavericks, FreeBSD commits). Whether it builds on current compilers is not documented. |
| **Platforms** | x86-64 (and 32-bit x86) on Linux. There are 2014 build fixes for FreeBSD and OS X, but the maintainer said in 2016 he had not tested macOS. No Windows, ARM/aarch64 or PowerPC support. |
| **Thread safety** | db.h: a DB is safe for concurrent access from multiple threads without external synchronization, and snapshots are immutable and shareable. Writers insert into the log and memtable in parallel. Iterator and WriteBatch thread safety is not documented. |
| **Drop-in for the baseline** | partial — same leveldb namespace, classes and C API names, and the authors claim on-disk format compatibility. But includes change from leveldb/ to hyperleveldb/, you link libhyperleveldb instead, the API is frozen at LevelDB 1.17, and the identical C++/C symbols mean it cannot be linked into the same binary as LevelDB. |

## Gotchas

- L0 is only soft-throttled: a writer sleeps one microsecond per L0 file above 8, and db_impl.cc never uses kL0_StopWritesTrigger. A long ingest can therefore pile up overlapping L0 files that later reads must check, which fits the slow queries seen right after the bulk load.
- Seek-triggered compaction only kicks in after more than 10 consecutive reads with no write in between (kStraightReads), so mixed read/write workloads rarely get read-driven cleanup.
- With manual_garbage_collection=true, compaction keeps deleted and overwritten data until the application calls AllowGarbageCollectBeforeTimestamp. Forgetting that call makes disk usage grow without bound.
- Known build snags: linking against Ubuntu's Snappy fails with 'DSO missing from command line' until -lsnappy is added to LIBS (#15/#16). Level sizes, file sizes and triggers are compile-time constants in version_set.cc/dbformat.h, not Options.

## Known shortcomings

- The win is writes (\~3.36x load); queries are \~4.7x slower than LevelDB and deletes/compaction are slower too.
- Reads lose badly (100M range query 13m49s vs LevelDB 2m55s) and the write win is inconsistent (a 3M SSD run took 21.0 s vs LevelDB 18.0 s; DB 206 MB vs 78 MB after load). x86-only inline-asm atomics (maintainer declined std::atomic/arm64, #19/#21); no Windows (#18).
- Abandoned since 2016, frozen at LevelDB 1.17, pre-C++11 (tr1). Background threads are never joined, so each open/close leaks \~24 MB of virtual memory (#4); only a soft L0 throttle; shares LevelDB's namespace and C symbols, so both cannot be linked into one binary. PebblesDB (built on it, active 2024) is usually the better choice.

## Caveats and trade-offs

This is a 2014 benchmark on a 2-core, 4GB DigitalOcean droplet. The author says settings were not tuned per engine, and the page gives no compiler, flags or CPU model. HyperLevelDB wins only on writes and is the slowest engine for range queries. The last three rows of the results image (Query 50M, Write 50M, DB size) match the 30M run in the linked gist, not the 100M run. In the gist's 3M-value SSD run, HyperLevelDB writes were slower than LevelDB's (21.0s vs 18.0s).

Fork of LevelDB by the now-defunct HyperDex team, adds multi-threaded compaction; abandoned since 2016 so it lacks a decade of LevelDB/RocksDB fixes.

## Maintenance

Abandoned since 2016 and never re-released (the maintainer declined in 2018). It is BSD-3-Clause and small enough to vendor, but it is x86-only, frozen at LevelDB 1.17, and has no known-good modern compiler documented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** InfluxData, which is independent of HyperLevelDB, published this benchmark. It compares HyperLevelDB with LevelDB, RocksDB and LMDB, describes the method, and gives numbers in a results-table image, with raw logs in a linked gist. The page gives no compiler, flags, CPU model or benchmark-code link, so it falls short of A.
- **Verifier notes:** The record said the page gives no numbers, but they are in the results image (grid.png). I replaced the claim with the numbers and recorded the losses on reads, deletes and compaction. Metadata checks out: BSD-3-Clause, 464 stars, last commit 2016-02-16, abandoned; not a GitHub fork, but conceptually derived from google/leveldb.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://www.influxdata.com/blog/2014/06/20/leveldb_vs_rocksdb_vs_hyperleveldb_vs_lmdb_performance.html>
  - <https://www.influxdata.com/images/legacy-uploads/grid.png>
  - <https://gist.github.com/pauldix/db7dca9595e5c359ceb8>
  - <https://github.com/rescrv/HyperLevelDB>
- **Sources the enricher read:**
  - <https://github.com/rescrv/HyperLevelDB>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/README>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/configure.ac>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/Makefile.am>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/NEWS>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/TODO>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/AUTHORS>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/include/hyperleveldb/db.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/include/hyperleveldb/options.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/include/hyperleveldb/c.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/db/db_impl.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/db/db_impl.cc>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/db/version_set.cc>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/db/dbformat.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/db/skiplist.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/util/atomic.h>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/util/crc32c.cc>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/util/env_posix.cc>
  - <https://github.com/rescrv/HyperLevelDB/blob/master/port/atomic_pointer.h>
  - <https://github.com/rescrv/HyperLevelDB/commits/master>
  - <https://github.com/rescrv/HyperLevelDB/issues?q=is%3Aissue>
  - <https://github.com/rescrv/HyperLevelDB/issues/4>
  - <https://github.com/rescrv/HyperLevelDB/issues/6>
  - <https://github.com/rescrv/HyperLevelDB/issues/15>
  - <https://github.com/rescrv/HyperLevelDB/issues/18>
  - <https://github.com/rescrv/HyperLevelDB/issues/19>
  - <https://github.com/rescrv/HyperLevelDB/issues/20>
  - <https://github.com/rescrv/HyperLevelDB/issues/21>
  - <https://github.com/rescrv/HyperLevelDB/issues/22>
  - <https://github.com/rescrv/HyperLevelDB/issues/23>
  - <https://www.influxdata.com/blog/2014/06/20/leveldb_vs_rocksdb_vs_hyperleveldb_vs_lmdb_performance.html>
  - <https://gist.github.com/pauldix/db7dca9595e5c359ceb8>
  - <https://web.archive.org/web/2016/http://hackingdistributed.com/2013/06/17/hyperleveldb/>
  - <https://web.archive.org/web/2015/http://hackingdistributed.com/2014/06/18/hyperleveldb-improvements/>
  - <https://hn.algolia.com/api/v1/search?query=hyperleveldb&tags=story>
  - <https://github.com/utsaslab/pebblesdb>
  - <https://github.com/utsaslab/pebblesdb/blob/master/benchmark.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/rescrv/hyperleveldb`) · [data/wave6/enrich/raw/github_com_rescrv_hyperleveldb.json](../../../data/wave6/enrich/raw/github_com_rescrv_hyperleveldb.json) (enrichment confidence 0.7)

</details>
