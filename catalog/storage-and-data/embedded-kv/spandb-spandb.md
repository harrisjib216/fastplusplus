# SpanDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0` · 🔴 abandoned

> Modified RocksDB 6.x that writes WAL and top LSM levels to raw SPDK NVMe; up to 8.8x write throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 'improves RocksDB's throughput by up to 8.8x and reduces its latency by 9.5-58.3%' (FAST'21 abstract). The 8.8x peak comes from the YCSB all-write workload (20M Zipfian writes: 7.6-8.8x across device pairs). The read-heavy YCSB-B/E gains are only 1.03-1.66x in throughput. |
| **Workload** | LSM-tree KV store on hybrid storage, SpanDB vs vanilla RocksDB v6.5.1: YCSB all-write, A, B, E and F (Zipfian and uniform) on a 512 GB database, plus LinkBench, across three capacity-disk/speed-disk pairs (S-N2, S-O, N1-O). SpanDB writes its WAL via SPDK to the fast NVMe disk; RocksDB writes WAL to the same disk via ext4. |
| **Metric** | throughput |
| **Hardware** | 2x 20-core Intel Xeon Gold 6248, 256 GB DRAM, CentOS 7.7; Intel Optane P4800X, P4510 and P4610 NVMe SSDs, plus S4510 SATA SSDs in 4+1 RAID5, tested as capacity-disk/speed-disk pairs |
| **Adoption** | 214 stars |
| **Last commit** | 2023-08-02 |
| **Links** | [repository](https://github.com/SpanDB/SpanDB) · [benchmark](https://www.usenix.org/conference/fast21/presentation/chen-hao) |

## Verdict

Per the FAST'21 paper, on a 2x20-core Xeon Gold 6248 server (CentOS 7.7) using SATA RAID5, P4510, P4610 and Optane P4800X drives as capacity/speed pairs, SpanDB beat vanilla RocksDB v6.5.1, which also wrote its WAL to the fast disk but through ext4. On a 512GB database of 1KB values with 20M Zipfian operations it was 7.6-8.8x faster on all-write YCSB, 2.6-4.0x on YCSB-A (1.7-2.4x uniform) and 1.03-1.66x on read-heavy B/E, with up to 50.3% more on LinkBench. Tests used sync WAL and no compression; compiler and flags are not stated, and the LinkBench driver is not in the repo.

## Use it when

- Write-heavy workloads that need a synchronous WAL (sync=true), where RocksDB's group commit through ext4 is the bottleneck. The paper measured 7.6-8.8x on all-write YCSB and 2.6-4.0x on Zipfian YCSB-A.
- Large databases (the paper tested 512GB-2TB) on cheap SATA or high-capacity NVMe drives, where you can add one small Optane-class or fast NVMe SSD owned by the KV process.
- Transactional or graph OLTP work that cannot drop the WAL, which is KVell's approach. On LinkBench (206GB, about 70% reads) the paper reports up to 50.3% more throughput and up to 41% lower latency.
- Research, or as a reference implementation of parallel WAL logging and a minimal file system over SPDK that you plan to port into your own RocksDB-based engine.
- Applications that can be rewritten around an issue-then-poll async loop and can give SpanDB dedicated pinned cores.

## Skip it when

- Read-dominated workloads. Read-heavy YCSB-B/E gained only 1.03-1.66x, and the paper says all-read workloads see little speedup plus slight overhead from asynchronous processing.
- Hosts where you cannot give one process a whole NVMe device. SPDK unbinds the drive from the kernel, so no other process or file system can use it, and the maintainer says one process cannot open two SpanDB databases (use column families; issue #14).
- CPU-constrained or shared machines. Server threads spin on pinned cores (94.5% CPU vs 63.7% for RocksDB on a 50%-write test) and the TopFS cache must sit in hugepages.
- Production use. The code is frozen on RocksDB 6.x and SPDK v20.01 with no upstreaming (issue #3). Issue reports include hangs at warmup with 100% CPU (#6, open), memory growth until the OOM killer (#13, closed without a reply), a compaction read-ahead overflow (#7) and link failures against SPDK/ISA-L (#9).
- Non-Linux platforms, or anyone who needs current RocksDB features and fixes. Setup is documented only for CentOS and Ubuntu, and SATA drives cannot be the SPDK speed disk.

## How it is fast

WAL writes skip ext4 and use SPDK user-space polled NVMe I/O. The paper measured ext4 small-write latency at 6.8-12.4x SPDK's. RocksDB's single-leader group commit is replaced by 1-3 dedicated logger threads that write batched WAL entries into 4KB pages in parallel, allocating pages with CAS; the paper reports about 10x more logging bandwidth. Requests are handled in stages, SEDA-style: client threads drop requests into queues (ProLog/Log/EpiLog/Read), and core-pinned worker threads that spin instead of sleeping handle memtable work, flush and compaction, so no thread sleep/wakeup sits on the critical path. The top levels live in TopFS, a minimal file system over raw SPDK pages with its own hugepage cache. Which levels go there is decided at runtime by monitoring device bandwidth. Flush/compaction I/O is cut to 64KB and kept on separate NVMe queues so WAL writes keep priority.

## Compared with alternatives

Pick SpanDB over KVell when you need WAL durability and RocksDB transactions: KVell has no commit log, and the paper puts SpanDB at 96-140% of KVell's throughput with 2.3-21.6x lower latency. Pick it over MatrixKV when your fast tier is an NVMe SSD rather than byte-addressable NVM. For a production RocksDB replacement, maintained drop-ins such as Speedb or ToplingDB are safer bets.

## Integration

| | |
|---|---|
| **Form** | shared lib (a patched librocksdb.so built from the full RocksDB tree with CMake; SPDK/DPDK are linked into the shared target) |
| **Dependencies** | SPDK v20.01.x built with --with-shared, plus its bundled DPDK (CMake fails unless the DPDK_LIB and DPDK_INCLUDE env vars are set); libnuma and TBB, both linked unconditionally; gflags, snappy, zlib, bzip2, lz4, zstd. At runtime: hugepages and an NVMe device bound to SPDK via scripts/setup.sh (root). |
| **Minimum toolchain** | C++11 (README: GCC &gt;= 4.8), CMake &gt;= 3.5.1. The maintainers recommend CMake 3.5 for the YCSB harness because newer CMake fails (issue #10). |
| **Platforms** | Linux x86-64 as tested (2x Xeon Gold 6248, CentOS 7.7) with Intel NVMe SSDs as the speed disk. ARM support is not documented beyond RocksDB's inherited build flags. |
| **Thread safety** | Sync calls follow RocksDB's DB-handle rules. In the YCSB harness, many client threads each keep their own array of std::atomic&lt;Status\*&gt; slots for async requests. Beyond that, not documented. |
| **Drop-in for the baseline** | partial — same RocksDB 6.x C++ API and on-disk format, and it opens and migrates an existing RocksDB database. But the speedups need the new Async\* calls, SPDK-specific Options and a dedicated NVMe device, and the bundled harness can load data only in plain RocksDB mode (issue #5). |

## Gotchas

- The YCSB driver runs system("rm &lt;data_dir&gt;/\*") and, in rocksdb mode, empties the log dir. The SpanDB run must be done as root with ulimit -n 100000. SST files migrated to the raw SPDK device disappear from the file system, which is expected (maintainer reply in issue #6).
- The harness hardcodes 40 cores and sets spandb_worker_num = cores - background cores - clients. With too many client threads this goes negative and aborts with std::bad_array_new_length (issue #12).
- Async calls can return Status::Busy when internal queues are full, and the caller must resubmit. On completion SpanDB stores a heap-allocated Status\* into the caller's atomic slot, and the caller must delete it.
- HUGEMEM must be larger than topfs_cache_size (the harness sets 90), and the WAL device is addressed by PCIe address (traddr:0000:xx:00.0), not a path.

## Known shortcomings

- The 8.8x is YCSB all-write only; read-heavy workloads gain 1.03-1.66x. Baseline RocksDB 6.5.1 on 2x Xeon Gold 6248; no compiler/flags.
- Gains need the new Async\* API, SPDK, root, hugepages and a whole NVMe drive per process, so it is only a partial drop-in. Spinning pinned cores use 94.5% vs 63.7% CPU. Frozen on RocksDB 6.x and SPDK v20.01 (5 commits, last 2023-08); open issues: warmup hang (#6), SPDK link failure (#9), core-count abort (#12); OOM report closed without reply (#13). The LinkBench driver is not in the repo.

## Caveats and trade-offs

The baseline is RocksDB v6.5.1 (2019). The paper does not state the compiler version or flags. SpanDB needs SPDK, hugepages and a dedicated NVMe device for the WAL, and its gains are largest on write-intensive workloads (read-heavy YCSB-B/E gives 1.03-1.66x). The repo has had no commits since August 2023, so it is an unmaintained research prototype.

Requires SPDK plus manual NVMe setup (hugepages, unbinding devices from the kernel driver), a much heavier deployment than plain RocksDB. Built by adapting the RocksDB codebase (not flagged as a GitHub fork, but derived from it) to place WAL and top LSM levels on faster NVMe.

## Maintenance

Abandoned research prototype: 5 commits, code dropped in January 2021, last touched 2023-08-02. GitHub labels it GPL-2.0, and the RocksDB-derived files keep RocksDB's GPLv2/Apache-2.0 header. The SPDK WAL and TopFS code is worth studying or copying, but it is pinned to RocksDB 6.x and SPDK v20.01, with open build and hang reports.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX FAST'21 paper. Its abstract states the 8.8x throughput and 9.5-58.3% latency gains against vanilla RocksDB v6.5.1, and the code and YCSB harness are public at SpanDB/SpanDB (ycsb/, test binary with dbname=rocksdb|spandb). The paper names the CPU (2x Xeon Gold 6248) but not the compiler version or flags, and the README gives only 'gcc &gt;= 4.8' and CMAKE_BUILD_TYPE=Release, so not A.
- **Verifier notes:** I opened the full paper PDF. The numbers match the abstract, and section 5.1 names the hardware and the RocksDB v6.5.1 baseline. Metadata checks out: GPL-2.0, 214 stars, last commit 2023-08-02, abandoned (over 3 years).
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/fast21/presentation/chen-hao>
  - <https://www.usenix.org/system/files/fast21-chen-hao.pdf>
  - <https://github.com/SpanDB/SpanDB>
- **Sources the enricher read:**
  - <https://github.com/SpanDB/SpanDB>
  - <https://github.com/SpanDB/SpanDB/blob/master/README.md>
  - <https://github.com/SpanDB/SpanDB/blob/master/CMakeLists.txt>
  - <https://github.com/SpanDB/SpanDB/blob/master/include/rocksdb/version.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/include/rocksdb/db.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/include/rocksdb/options.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/include/rocksdb/status.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/include/rocksdb/utilities/transaction.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/env/spandb_options.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/env/spdk_env.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/env/topfs_cache.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/db/db_impl/spandb_task_que.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/db/db_impl/db_impl_async.cc>
  - <https://github.com/SpanDB/SpanDB/blob/master/db/db_impl/db_impl_write.cc>
  - <https://github.com/SpanDB/SpanDB/blob/master/db/db_impl/db_impl.cc>
  - <https://github.com/SpanDB/SpanDB/blob/master/db/db_impl/request_scheduler.h>
  - <https://github.com/SpanDB/SpanDB/blob/master/ycsb/src/test.cc>
  - <https://github.com/SpanDB/SpanDB/blob/master/ycsb/src/rocksdb_client.cc>
  - <https://github.com/SpanDB/SpanDB/commits/master>
  - <https://github.com/SpanDB/SpanDB/issues?q=is%3Aissue>
  - <https://github.com/SpanDB/SpanDB/issues/3>
  - <https://github.com/SpanDB/SpanDB/issues/5>
  - <https://github.com/SpanDB/SpanDB/issues/6>
  - <https://github.com/SpanDB/SpanDB/issues/7>
  - <https://github.com/SpanDB/SpanDB/issues/9>
  - <https://github.com/SpanDB/SpanDB/issues/10>
  - <https://github.com/SpanDB/SpanDB/issues/12>
  - <https://github.com/SpanDB/SpanDB/issues/13>
  - <https://github.com/SpanDB/SpanDB/issues/14>
  - <https://www.usenix.org/system/files/fast21-chen-hao.pdf>
  - <https://hn.algolia.com/api/v1/search?query=SpanDB&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/spandb/spandb`) · [data/wave6/enrich/raw/github_com_spandb_spandb.json](../../../data/wave6/enrich/raw/github_com_spandb_spandb.json) (enrichment confidence 0.8)

</details>
