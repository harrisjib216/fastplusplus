# TokuDB / PerconaFT Fractal Tree Index

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0 and AGPL-3.0 per README (GitHub reports AGPL-3.0); locktree and omt portions also Apache-2.0; separate PATENTS file` · 🟡 stale

> Fractal Tree (Bε-tree) transactional key-value library behind TokuDB/TokuMX; beat MongoDB 2.2's B-tree indexes on out-of-RAM inserts.

| | |
|---|---|
| **Beats** | MongoDB's default B-tree index (MMAPv1 storage engine) |
| **Claimed result** | Over 532x 'exit velocity', i.e. the instantaneous insert rate at 3.5M documents: 2.11 inserts/sec for stock MongoDB vs 1,124.36 inserts/sec for MongoDB with Fractal Tree indexes. |
| **Workload** | Multikey index insertion benchmark: 3.5M documents inserted into MongoDB v2.2.RC0, each document with a 100-entry array field (URI), forcing 100 index operations per insert |
| **Metric** | throughput |
| **Hardware** | Sun x4150, 2x Xeon 5460, 16GB RAM, StorageTek RAID controller (256MB write-back cache), 4x10K RPM SAS drives in RAID 0, Ubuntu 10.04 Server 64-bit, ext4 |
| **Adoption** | 562 stars; formerly shipped as TokuDB/TokuMX, now maintained by Percona as PerconaFT |
| **Last commit** | 2023-11-28 |
| **Links** | [repository](https://github.com/percona/PerconaFT) · [benchmark](http://web.archive.org/web/20150725021440/http://www.tokutek.com:80/2012/11/532x-multikey-index-insertion-performance-increase-for-mongodb-with-fractal-tree-indexes/) |

## Verdict

In Tokutek's 2012 vendor blog, MongoDB v2.2.RC0 loaded documents that each carried a 100-element array under a multikey index, so each insert meant 100 index operations. After 3.5M documents, stock MMAPv1 B-tree indexes had dropped to 2.11 inserts/s against 1,124.36 inserts/s for Tokutek's Fractal-Tree-indexed build. The machine was a Sun x4150 (2x Xeon 5460, 16 GB RAM, 4x10K SAS in RAID 0 behind a 256 MB write-back cache, Ubuntu 10.04, ext4). The figure is a single end-of-run 'exit velocity' point in a disk-bound regime, not an average, and no compiler flags are given. On HN a commenter noted that the stock curve had decayed to near zero, so the ratio depends on where the run stopped.

## Use it when

- Insert, delete or update-heavy workloads with several secondary indexes whose combined size is far beyond RAM on HDDs or bandwidth-limited SSDs, with random, high-cardinality keys. That is the regime of the 532x run and of Percona's 'up to two orders of magnitude' claim.
- Blind updates such as counters, timestamps or balance deltas, written as DB-&gt;update upsert callbacks so no read-before-write is needed. The Bε-tree authors say upserts can speed updates up by one to two orders of magnitude.
- An embedded transactional C/C++ key-value store with a Berkeley DB-like API, compressed on-disk nodes (QuickLZ, zlib, LZMA or Snappy) and hot index builds, on 64-bit Linux, where GPLv2/AGPLv3 is acceptable.
- Keeping an existing TokuDB, TokuMX or Percona-FT deployment running, or studying a production-grade Bε-tree with checkpointing, logging and a range-lock manager.

## Skip it when

- Data or indexes that fit in RAM, or mostly sequential keys. Percona's docs say fractal trees only 'match B-trees' on sequential data. In Percona's own 2015 iiBench run (1B rows, 3 indexes, one SSD), WiredTiger's B-tree was fastest while data fit in memory, and RocksDB was 'overall better' than PerconaFT as data grew.
- Read-before-write patterns such as unique-key checks and query-modify-insert. These run at point-query speed, which is no better than a B-tree, and every lookup must also apply pending messages buffered along the root-to-leaf path.
- New projects that need an active upstream. The last commit was 2023-11-28 and GitHub issues are disabled. 28 PRs sit unmerged, including fsync error handling (#410, 2018), a crash when out of locks (#443), ThreadSanitizer-found data races (#396) and filesystems with non-512-byte sectors (#385). Percona dropped TokuDB as of Percona Server for MySQL 8.0.28-19 (2022-05-12).
- Targets other than 64-bit Linux. 32-bit is unsupported, macOS and FreeBSD only 'may work' (macOS CI jobs were allowed to fail), and the cycle timer has #error for anything but x86, aarch64 and POWER. The s390x/RISC-V port PR is unmerged, and the TSan PR notes an x86 memory-model bias in the code.
- Projects that need a permissive license. The core is GPLv2/AGPLv3 (only locktree and omt are Apache-2.0), and the PATENTS grant can be terminated if you challenge the patents.

## How it is fast

Every dictionary is a Fractal Tree, which is Tokutek's industrial Bε-tree (the buffered B-tree / cache-oblivious streaming B-tree family from Bender, Farach-Colton and Kuszmaul). Each internal node keeps one message buffer per child, ordered by key and message sequence number. Inserts, deletes (as tombstones) and upserts enter as messages near the root and are flushed down in batches to the fullest child, so one node I/O moves many updates instead of one random leaf read-modify-write per key. Nodes are large and compressed (4 MB default, fanout 16, leaves split into 128 KB basement nodes for partial reads, QuickLZ by default), and a promotion heuristic sends runs of sequential inserts straight to the rightmost leaf. In the benchmark, the 100-entry multikey index most likely outgrew 16 GB RAM, which forced MongoDB's B-tree into random disk reads per index entry. The fractal tree avoids those reads, though the blog post itself gives no cause.

## Compared with alternatives

Pick it over MyRocks, the LSM engine for MySQL that is still maintained, or over TidesDB and redb only if you specifically want an embeddable Berkeley DB-style transactional library with upsert messages for index-heavy, far-larger-than-RAM random writes, and you accept inheriting maintenance. The in-memory siblings (ALEX, HOT, Wormhole, the learned indexes) target a different, RAM-resident regime and are not substitutes.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | zlib (system). Bundled in third_party: xz 4.999.9beta (LZMA), Snappy 1.1.2 and QuickLZ source. CMake &gt;= 2.8.12. Valgrind is optional for tests. |
| **Minimum toolchain** | C++11 (-std=c++11) and C99. CI covered GCC 4.8-10 and Clang 4-10 on Ubuntu 18.04 (Travis). CMake 2.8.12+. |
| **Platforms** | 64-bit Linux (CentOS, Debian, Ubuntu supported). macOS 10.8 and FreeBSD 'may work'. No 32-bit. Timer code exists only for x86-64, aarch64 and POWER. |
| **Thread safety** | Built for multi-threaded use: DB_THREAD handles, background cachetable, flusher and checkpoint thread pools, and a per-dictionary locktree with range row locks, wait-for-graph deadlock detection and lock timeouts. Caveat: an open PR (#396) reports about 100 unique ThreadSanitizer data-race and lock-order findings, and #447 reports a race on writing_rollback. |
| **Drop-in for the baseline** | no |

## Gotchas

- It refuses to start when Linux transparent huge pages are enabled, because they break its memory accounting and can overcommit. TOKU_HUGE_PAGES_OK=1 overrides this, but the README says to use it only for testing with a small cache.
- Under lock-memory pressure, DB-&gt;put can return TOKUDB_OUT_OF_LOCKS, and callers must handle it. The pending-lock retry path crashes in that case (PS-4328), and the fix is still an unmerged PR (#443).
- Deletes are tombstone messages, so deleted rows and their space linger until the messages are flushed to the leaves. Compression failures assert instead of returning error codes (compress.h). The bundled xz is a 2009 beta.
- The README build steps are stale (a jemalloc checkout, CMake 2.8.9, gcc47): CMakeLists.txt now requires 2.8.12 and no longer references jemalloc. The core is built with -fno-exceptions -fno-rtti, while the ftcxx wrapper throws ft_exception. TokuDB on-disk formats differ across MySQL variants, so moving between them takes a dump and reload.

## Known shortcomings

- The 532x is an end-of-run 'exit velocity' point from a 2012 Tokutek MongoDB prototype vs the old MMAP B-tree; licensing is GPL-2.0 plus AGPL-3.0 with Apache-2.0 parts and a PATENTS file.
- The stock MongoDB curve decayed to near zero, so the 532x depends on where the run stopped (one disk-bound end point, no flags). Not a MongoDB drop-in: a Berkeley-DB-style C API, with the MongoDB side needing the dead TokuMX fork or the old PSMDB engine. Stale since 2023-11 with issues off and 28 unmerged PRs (fsync errors #410, out-of-locks crash #443, TSan races #396, 4K sectors #385); TokuDB was dropped from Percona Server 8.0.28. Loses in RAM, on sequential keys and on read-before-write; Percona's 2015 iiBench found RocksDB 'overall better'. 64-bit Linux only; refuses to start with transparent huge pages on; bundled xz is a 2009 beta; the patent grant ends if you challenge the patents.

## Caveats and trade-offs

This is a first-party vendor blog post (Tokutek, later acquired by Percona) testing Tokutek's 2012 Fractal-Tree-indexed MongoDB prototype (the TokuMX precursor), not PerconaFT or TokuDB as packaged today. The baseline is stock MongoDB v2.2.RC0 (MMAPv1 B-tree indexes) on 16GB RAM and 4x10K RPM SAS disks. The post gives no cause for the gap, and the record's global-write-lock explanation is not from the source; the 100-entry multikey index outgrowing RAM (random B-tree I/O) is the likelier driver, so the ratio reflects a disk-bound, out-of-memory regime. The 532x is an end-of-run point measurement, not an average. No compiler flags are stated. tokutek.com is dead; the page was recovered via web.archive.org.

Write-optimized Fractal Tree (buffered B-tree family) index trades some point-lookup latency and extra CPU/memory for message buffering in exchange for much higher sustained insert throughput on write- and index-heavy workloads; requires the TokuDB/PerconaFT storage engine rather than being a drop-in library; different compression/crash-recovery model than a plain B-tree

## Maintenance

Stale: the last commit (2023-11-28) was a license fix, issues go to Percona's Jira rather than GitHub, and Percona dropped TokuDB from Percona Server 8.0.28-19 in 2022. The source can still be vendored and builds with CMake under GPLv2/AGPLv3 plus a patent grant, but you own all maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** This is a first-party Tokutek blog post against stock MongoDB v2.2.RC0 indexes. It gives hardware and links a benchmark client, but states no compiler or flags and reports a single end-of-run 'exit velocity' point. A &gt;50x gain with unstated flags is capped at C anyway.
- **Verifier notes:** All numbers, hardware, OS and MongoDB version match the archived page (posted 2012-11-13 by Tim Callaghan). Metadata matches: 562 stars, not archived or a fork, last commit 2023-11-28, so stale is correct. I only refined the license wording from README/COPYING.\* files.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <http://web.archive.org/web/20150725021440/http://www.tokutek.com:80/2012/11/532x-multikey-index-insertion-performance-increase-for-mongodb-with-fractal-tree-indexes/>
  - <https://github.com/percona/PerconaFT>
  - <https://github.com/percona/PerconaFT/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/percona/PerconaFT>
  - <https://github.com/percona/PerconaFT/blob/master/README.md>
  - <https://github.com/percona/PerconaFT/blob/master/ft/node.h>
  - <https://github.com/percona/PerconaFT/blob/master/ft/ft-internal.h>
  - <https://github.com/percona/PerconaFT/blob/master/ft/ft-ops.h>
  - <https://github.com/percona/PerconaFT/blob/master/ft/serialize/compress.h>
  - <https://github.com/percona/PerconaFT/blob/master/ft/serialize/compress.cc>
  - <https://github.com/percona/PerconaFT/blob/master/buildheader/make_tdb.cc>
  - <https://github.com/percona/PerconaFT/blob/master/CMakeLists.txt>
  - <https://github.com/percona/PerconaFT/blob/master/cmake_modules/TokuSetupCompiler.cmake>
  - <https://github.com/percona/PerconaFT/blob/master/cmake_modules/TokuThirdParty.cmake>
  - <https://github.com/percona/PerconaFT/blob/master/.travis.yml>
  - <https://github.com/percona/PerconaFT/blob/master/PATENTS>
  - <https://github.com/percona/PerconaFT/blob/master/portability/huge_page_detection.cc>
  - <https://github.com/percona/PerconaFT/blob/master/portability/toku_time.h>
  - <https://github.com/percona/PerconaFT/blob/master/locktree/locktree.h>
  - <https://github.com/percona/PerconaFT/blob/master/ftcxx/exceptions.hpp>
  - <https://github.com/percona/PerconaFT/blob/master/ftcxx/CMakeLists.txt>
  - <https://github.com/percona/PerconaFT/commits/master>
  - <https://github.com/percona/PerconaFT/commit/6739029d>
  - <https://github.com/percona/PerconaFT/pulls>
  - <https://github.com/percona/PerconaFT/pull/410>
  - <https://github.com/percona/PerconaFT/pull/396>
  - <https://github.com/percona/PerconaFT/pull/385>
  - <https://github.com/percona/PerconaFT/pull/443>
  - <https://github.com/percona/PerconaFT/pull/447>
  - <https://github.com/percona/PerconaFT/pull/461>
  - <https://github.com/Tokutek/mongo>
  - <http://web.archive.org/web/20150725021440/http://www.tokutek.com:80/2012/11/532x-multikey-index-insertion-performance-increase-for-mongodb-with-fractal-tree-indexes/>
  - <https://news.ycombinator.com/item?id=4799479>
  - <https://www.usenix.org/publications/login/oct15/bender>
  - <https://www.usenix.org/system/files/login/articles/login_oct15_05_bender.pdf>
  - <https://docs.percona.com/percona-server/8.0/tokudb-intro.html>
  - <https://www.percona.com/blog/2015/12/23/percona-server-for-mongodb-storage-engines-in-iibench-insert-workload/>
  - <https://www.percona.com/blog/percona-server-for-mongodb-3-4-product-bundle-release-is-a-valentines-day-gift-to-the-open-source-community/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/percona/perconaft`) · [data/wave6/enrich/raw/github_com_percona_perconaft.json](../../../data/wave6/enrich/raw/github_com_percona_perconaft.json) (enrichment confidence 0.8)

</details>
