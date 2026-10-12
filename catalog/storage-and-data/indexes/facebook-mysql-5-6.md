# MyRocks (RocksDB storage engine for MySQL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0-only` · 🔴 abandoned

> Meta's RocksDB (LSM-tree) storage engine for MySQL: \~4x smaller on disk, \~5x InnoDB's TPC-C tps when cache is tiny.

| | |
|---|---|
| **Beats** | InnoDB B-tree storage engine (MySQL / Percona Server 5.7) |
| **Claimed result** | Almost 5x higher average tps at a 5GB cache (4205.714 vs 849.0664 tps; the page says MyRocks outperforms InnoDB 'by almost five times'). The lead shrinks as memory grows, and InnoDB overtakes from 60GB (4756.551 vs 4571.163 tps). At 100GB InnoDB is about 1.30x faster (5961.2 vs 4599.143 tps; ratio derived from page data). |
| **Workload** | sysbench-tpcc, 100 warehouses / 10 tables (\~90GB dataset under InnoDB, 21GB under MyRocks with LZ4), varying buffer pool / block cache size from 5GB to 100GB, binlog enabled, READ-COMMITTED isolation |
| **Metric** | throughput |
| **Hardware** | Supermicro server, Intel Xeon E5-2683 v3 @2.00GHz (2 sockets / 28 cores / 56 threads), 256GB RAM, Samsung SM863 1.9TB SSD, ext4, Ubuntu 16.04.4 (kernel 4.13.0-36), Percona Server 5.7.21-20 |
| **Adoption** | 2.6k stars; used in production at Facebook/Meta and shipped by Percona Server and MariaDB |
| **Last commit** | 2025-01-27 |
| **Links** | [repository](https://github.com/facebook/mysql-5.6) · [benchmark](https://www.percona.com/blog/2018/04/30/a-look-at-myrocks-performance/) |

## Verdict

Percona's Vadim Tkachenko ran sysbench-tpcc (100 warehouses x 10 tables, 56 threads, 1-hour runs averaged over the last 1600 s, READ-COMMITTED, no FKs, ROW binlog with sync_binlog=10000, direct I/O on both engines) on packaged Percona Server 5.7.21-20. The box had 2x Xeon E5-2683 v3 (28 cores), 256GB RAM and a Samsung SM863 SSD, and the cache was swept from 5GB to 100GB. MyRocks averaged 4206 tps vs InnoDB's 849 at 5GB (\~5x), the gap closed to 1.16x at 50GB, and InnoDB led from 60GB (\~1.30x at 80-100GB). No compiler or build flags were given, and the binary was not built from this repo.

## Use it when

- OLTP on SSD where the dataset is several times larger than RAM. With a 90GB (InnoDB-sized) TPC-C dataset, MyRocks delivered 4.95x InnoDB's tps at 5GB of cache, 2.4x at 20GB and 1.16x at 50GB (ratios derived from the page's table).
- Storage cost or flash wear is the constraint. Meta's user database (UDB) migration cut instance size by 62.3% vs compressed InnoDB and bytes written by 75% (one replica set: 2187.4GB vs 824.4GB, 13.34 vs 3.42 MB/s written), at slightly lower CPU.
- Insert- or update-heavy tables with several non-unique secondary indexes, or loading new tables. rocksdb_bulk_load ingests SST files straight into the bottom level; Meta measured 2.2x (1 table) to 5.7x (20 parallel tables) InnoDB's load rate.
- Cloud instances where memory and IOPS are billed. Throughput barely changes from a 5GB to a 100GB cache (4206 to 4599 tps), so you can run small-memory instances.
- Your application already runs under READ-COMMITTED with row-based binlog, no foreign keys, and mostly PK or prefix lookups with forward range scans (Meta's social-graph pattern).

## Skip it when

- The working set fits in the buffer pool. InnoDB overtakes at 60GB (4757 vs 4571 tps) and is \~1.30x faster at 80-100GB (5985 vs 4617, 5961 vs 4599). MyRocks still reads \~13.7 KB per transaction at 100GB vs \~0.3 KB for InnoDB (derived), which is LSM read amplification.
- You need InnoDB features it lacks: FOREIGN KEY, fulltext and spatial indexes, SAVEPOINT, EXCHANGE PARTITION, transportable tablespaces, gap/next-key locks, statement or mixed binlog format, Group Replication, the Clone plugin, multi-valued indexes or table encryption (per the Meta wiki and Percona's current docs). Only READ-COMMITTED and REPEATABLE-READ are accepted (the source rejects the other levels).
- Big single transactions. All uncommitted changes stay in memory, and a transaction is capped by rocksdb_max_row_locks (default 1,048,576). Open issue #194 measures many-row statements at 7-10x InnoDB's time (for example, updating an indexed column on 1M rows took 99.5 s vs 12.4 s), and Percona warns that a large ALTER ... ENGINE=RocksDB can be OOM-killed unless you use bulk-load mode.
- You are sensitive to latency jitter. Percona saw periodic 1-second throughput drops it could not explain, the data directory swung from 20GB to 31GB between compactions, and the tuning wiki says compaction without a rate limiter can write 300-500MB/s and cause short stalls.
- You want an upstream that answers bugs. This repo is archived with 237 open issues and PRs, so you depend on Percona Server or MariaDB builds and their tuning expertise. Tuning also takes expertise: the wiki calls the defaults (4MB SST files, 4KB blocks) too small, and Percona's benchmark used settings supplied by Meta's MyRocks team.

## How it is fast

Every index is a key range in RocksDB, prefixed by a 4-byte index id. Keys are encoded in a memcmp-comparable ('mem-comparable') form, so the bytewise comparator orders them. The primary key maps to the full row (a clustered layout), and each secondary key embeds the PK. Writes go to a WAL and an in-memory MemTable and are later flushed and compacted into sorted, block-compressed SST files (leveled compaction; LZ4 on upper levels, ZSTD recommended at the bottom). That means no in-place page rewrites, no doublewrite buffer and no padding of compressed pages to 8KB. Non-unique secondary indexes are maintained with blind Put/SingleDelete and no read-before-write, and prefix bloom filters plus the block cache limit read amplification. In Percona's run this showed up as I/O. At a 5GB cache InnoDB wrote \~245k KB/s and spent 57% of its time in iowait, while MyRocks wrote \~87k KB/s and was CPU-bound (56% us + 11% sy). Derived from the page's tables, that is \~21 KB written per transaction for MyRocks at every cache size, vs \~288 KB for InnoDB at 5GB.

## Compared with alternatives

Pick MyRocks when you need a MySQL-compatible transactional SQL engine with replication, not an embedded store: TerarkDB and TidesDB are RocksDB-class key-value libraries, and redb and libmdbx are embedded B-tree KV stores, so each would need its own SQL layer. The only sibling that is also a write-optimized MySQL engine is TokuDB/PerconaFT; MyRocks is the one proven at Meta's UDB scale, and Percona's current docs (9.7 branch) still cover it.

## Integration

| | |
|---|---|
| **Form** | module — a MySQL storage-engine plugin compiled into Meta's MySQL server fork (a static, mandatory rocksdb_se plugin by default; ROCKSDB_DYNAMIC_PLUGIN builds a loadable module). You deploy the whole server, or use the MyRocks packaged in Percona Server / MariaDB. |
| **Dependencies** | RocksDB (git submodule), Boost (submodule) and zlib. Optional: LZ4, ZSTD, Snappy, BZip2, jemalloc, liburing, TBB, folly/glog, and Faiss (submodule, only with WITH_FB_VECTORDB). Plus the usual MySQL build dependencies (OpenSSL, bison, ncurses, libaio). |
| **Minimum toolchain** | fb-mysql-8.0.32: GCC 7.1+ or Clang 5+ (enforced in cmake/os/Linux.cmake), CMake 3.5.1+ (higher minimums on some platforms). The 5.6-era wiki lists gcc 4.9/5.4/6.1 and Clang 3.9 as internally verified. |
| **Platforms** | POSIX only (the CMake hard-codes ROCKSDB_PLATFORM_POSIX; no Windows). Linux x86-64 is the tested target: the wiki officially supports CentOS 6.8/7.2 and Ubuntu 14.04-16.04 on a best-effort basis. Darwin build paths exist, and big-endian test failures are an open issue (#600). |
| **Thread safety** | Handled by the server. Concurrent sessions go through RocksDB's TransactionDB with pessimistic row locks (per-session rocksdb_lock_wait_timeout, WRITE_COMMITTED write policy by default). Jan 2025 commits made parts of Rdb_transaction safe to access from other threads. There is no library-level API. |
| **Drop-in for the baseline** | partial — same SQL, protocol and replication, and you switch per table with ENGINE=RocksDB or ALTER TABLE. But foreign keys, fulltext/spatial indexes, savepoints and gap locks are missing, REPEATABLE-READ means snapshot isolation, row-based binlog is required, and the wiki calls mixing InnoDB and MyRocks in one instance 'not really transactional' and not for production. |

## Gotchas

- REPEATABLE-READ is PostgreSQL-style snapshot isolation, not InnoDB's gap-lock RR. Locking reads do not block phantoms, and statement-based binlog on a source can diverge replicas. Percona Server 5.7 rejected SELECT ... FOR UPDATE under RR, which is why the benchmark ran READ-COMMITTED (the tuning wiki recommends RC anyway).
- rocksdb_bulk_load disables unique checks and enables commit-in-the-middle, so a bulk load is neither atomic nor duplicate-checked, and ingested key ranges must not overlap existing data. Open issue #1249 reports ALTER TABLE ... ENGINE=RocksDB from MyISAM finishing 'successfully' with an empty table when the merge buffer was too small (Percona 5.7). The fix was raising rocksdb_merge_buf_size.
- Scan direction is fixed per column family when the table is created. Forward scans are fast and backward scans are slow, unless you put the index in a 'rev:' family, which reverses the trade-off.
- Memory can exceed block cache plus memtables. Issue #1269 saw RSS grow from 95G to 120G after mass TTL compactions (resolved via TCMALLOC_RELEASE_RATE or by disabling TTL compaction). In issue #814 the server could not reopen RocksDB after an OOM kill. A maintainer blames a partially written WAL under rocksdb_wal_recovery_mode=1, and the tuning wiki sets it to 2.

## Known shortcomings

- Wins only at low memory: InnoDB wins from 60 GB up and is \~30% faster at 100 GB (Percona tpcc); tested Percona Server 5.7.21's MyRocks build, not the facebook repo binary.
- Wins only when data greatly exceeds RAM (4.95x at 5 GB cache down to 1.16x at 50 GB; InnoDB wins from 60 GB, \~1.30x at 80-100 GB). Missing foreign keys, fulltext/spatial, savepoints and gap locks (RR is snapshot isolation; row binlog only). Big transactions live in RAM (1M row-lock cap); many-row statements 7-10x slower than InnoDB (#194); large ALTER can OOM and the bulk_load workaround is non-atomic and skips unique checks; an ALTER to RocksDB can silently leave an empty table when the merge buffer is too small (Percona #1249). Periodic 1 s tps drops; RSS can outgrow the cache (#1269). The facebook repo is archived; real use is via Percona/MariaDB builds.

## Caveats and trade-offs

This is an independent Percona benchmark, not one by Facebook/Meta. The scripts and raw results are public (Percona-Lab-results/201803-sysbench-tpcc-myrocks) and hardware and software versions are fully stated, but there are no compiler or build flags (server-level benchmark on packaged binaries). The engine tested was the MyRocks build shipped in Percona Server 5.7.21-20, not a binary built from the facebook/mysql-5.6 repo. The run used READ-COMMITTED (MyRocks lacks SELECT..FOR UPDATE under REPEATABLE-READ in Percona Server) and no foreign keys. The page reports periodic 1-second throughput drops for MyRocks. The win depends on memory: it holds only while the dataset-to-memory ratio is high, and InnoDB wins at 60GB and above. The repo is archived. GitHub reports the license as NOASSERTION, but the LICENSE file is MySQL 8.0's GPLv2 with Oracle's additional linking permission (copyleft).

LSM-tree write-optimized engine achieves much better compression (21GB vs 90GB dataset here) and far higher tps under constrained memory, but unlike a B-tree it does not keep improving as more cache/RAM is added, so InnoDB overtakes it once the working set fits in the buffer pool; at benchmark time MyRocks lacked FOREIGN KEY support and SELECT..FOR UPDATE under REPEATABLE-READ in this Percona Server version

## Maintenance

The public repo is archived (last commit 2025-01-27 on fb-mysql-8.0.32, 237 open issues and PRs), though Meta presented new MyRocks features at FOSDEM 2025 (Faiss vectors, Thrift NoSQL access, user-defined timestamps). It is a GPLv2 MySQL server fork with Oracle's linking exception, so in practice you consume it through Percona Server or MariaDB rather than vendoring code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent Percona sysbench-tpcc run (author Vadim Tkachenko explicitly uses InnoDB as the baseline) with full hardware/software versions and public scripts, configs and raw results (github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks). No compiler or build flags are stated (packaged Percona Server 5.7.21-20 binaries), so it falls short of A.
- **Verifier notes:** All 11 memory-point averages were checked against the page table, and hardware matches the page's 'Hardware spec' section. The benchmark_url now redirects to https://www.percona.com/blog/a-look-at-myrocks-performance/ (same content). I read the LICENSE file on the fb-mysql-8.0.32 default branch; its last commit (2025-01-27), archived status and 2,574 stars match the record.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** Meta's UDB migration paper: 62.3% smaller and 75% fewer bytes written vs compressed InnoDB.
- **Pages the verifier opened:**
  - <https://www.percona.com/blog/2018/04/30/a-look-at-myrocks-performance/>
  - <https://www.percona.com/blog/a-look-at-myrocks-performance/>
  - <https://github.com/facebook/mysql-5.6>
  - <https://github.com/facebook/mysql-5.6/blob/fb-mysql-8.0.32/LICENSE>
  - <https://github.com/facebook/mysql-5.6/blob/fb-mysql-8.0.32/README>
  - <https://github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks>
- **Sources the enricher read:**
  - <https://github.com/facebook/mysql-5.6>
  - <https://github.com/facebook/mysql-5.6/blob/fb-mysql-8.0.32/README>
  - <https://github.com/facebook/mysql-5.6/tree/fb-mysql-8.0.32>
  - <https://github.com/facebook/mysql-5.6/blob/fb-mysql-8.0.32/.gitmodules>
  - <https://github.com/facebook/mysql-5.6/blob/fb-mysql-8.0.32/storage/rocksdb/README>
  - <https://github.com/facebook/mysql-5.6/branches>
  - <https://github.com/facebook/mysql-5.6/commits/fb-mysql-8.0.32>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/storage/rocksdb/ha_rocksdb.cc>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/storage/rocksdb/ha_rocksdb.h>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/storage/rocksdb/rdb_datadic.h>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/storage/rocksdb/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/cmake/os/Linux.cmake>
  - <https://raw.githubusercontent.com/facebook/mysql-5.6/fb-mysql-8.0.32/LICENSE>
  - <https://raw.githubusercontent.com/wiki/facebook/mysql-5.6/Home.md>
  - <https://raw.githubusercontent.com/wiki/facebook/mysql-5.6/MyRocks-limitations.md>
  - <https://raw.githubusercontent.com/wiki/facebook/mysql-5.6/Getting-Started-with-MyRocks.md>
  - <https://raw.githubusercontent.com/wiki/facebook/mysql-5.6/my.cnf-tuning.md>
  - <https://raw.githubusercontent.com/wiki/facebook/mysql-5.6/Build-Steps.md>
  - <https://github.com/facebook/mysql-5.6/issues/194>
  - <https://github.com/facebook/mysql-5.6/issues/1249>
  - <https://github.com/facebook/mysql-5.6/issues/1269>
  - <https://github.com/facebook/mysql-5.6/issues/814>
  - <https://github.com/facebook/mysql-5.6/issues/1406>
  - <https://github.com/facebook/mysql-5.6/issues?q=crash>
  - <https://www.percona.com/blog/a-look-at-myrocks-performance/>
  - <https://github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks>
  - <https://github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks/blob/master/res-tpcc-LZ4-minbinlog-sync10000-cgroup-2018-03-14-21-13/mysql57.BP5/thr56/my-rocks.cnf>
  - <https://github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks/blob/master/res-tpcc-LZ4-minbinlog-sync10000-cgroup-2018-03-14-21-13/mysql57.BP5/thr56/run_tpcc.sh>
  - <https://github.com/Percona-Lab-results/201803-sysbench-tpcc-myrocks/blob/master/MyRocks-no-direct/readme.md>
  - <https://www.vldb.org/pvldb/vol13/p3217-matsunobu.pdf>
  - <https://github.com/percona/psmysql-docs/blob/9.7/docs/myrocks-limitations.md>
  - <https://archive.fosdem.org/2025/schedule/event/fosdem-2025-5168-what-is-new-in-myrocks-rocksdb-storage-engine-for-mysql/>
  - <https://hn.algolia.com/api/v1/search?query=MyRocks&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/facebook/mysql-5.6`) · [data/wave6/enrich/raw/github_com_facebook_mysql_5_6.json](../../../data/wave6/enrich/raw/github_com_facebook_mysql_5_6.json) (enrichment confidence 0.8)

</details>
