# KVell

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> SOSP'19 research key-value store for NVMe/Optane SSDs that has no LSM compaction; 2-8x RocksDB throughput on YCSB point workloads.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Abstract: throughput at least 2x the closest competitor (RocksDB 6.2, PebblesDB, TokuMX, WiredTiger) on read-dominated workloads and 5x on write-dominated workloads; on mostly-scan workloads comparable or better; maximum latencies an order of magnitude lower than the best competitor, even on scan-based workloads. Body (Config-Optane, 100M 1KB items): YCSB A 8x RocksDB and 5.8x PebblesDB (next best); YCSB B/C 2.2x/2.7x over existing KVs; Nutanix production workloads \~4x RocksDB (the next best); uniform YCSB E roughly equal to RocksDB (13.9K vs 14.4K scans/s). |
| **Workload** | YCSB core workloads (uniform and Zipfian key distributions), 1024B items, 100GB(100M keys)/5TB(5B keys) synthetic datasets, plus two Nutanix write-heavy (57:41:2 write:read:scan) production workloads, 250B-1KB items. |
| **Metric** | throughput |
| **Hardware** | Config-SSD: 32-core 2.4GHz Intel Xeon, 128GB RAM, 480GB Intel DC S3500 SSD; Config-Amazon-8NVMe: AWS i3.metal, 36x2 (72) cores at 2.3GHz, 488GB RAM, 8x1.9TB NVMe SSDs; Config-Optane: 4-core 4.2GHz Intel i7, 60GB RAM, 480GB Intel Optane 905P |
| **Compiler and flags** | Paper states none. Repo Makefile defaults: clang with CFLAGS=-O2 -ggdb3 -Wall (clang++ -std=c++11 for index code); README recommends TCMalloc (gperftools). Not confirmed as the build used for the paper runs. |
| **Adoption** | 293 stars |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/BLepers/KVell) · [benchmark](https://github.com/BLepers/KVell/blob/master/sosp19-final40.pdf) |

## Verdict

In the SOSP'19 paper, on a 4-core 4.2 GHz i7 with an Optane 905P (memory capped by cgroups to 1/3 of a 100 GB, 100M x 1 KB dataset), KVell sustained about 420K req/s on YCSB A. That is 8x RocksDB 6.2 and 5.8x PebblesDB, with 2.2-2.7x on YCSB B/C, about 4x on Nutanix production traces, rough parity on uniform YCSB E, and 3.9 ms max latency versus RocksDB's 9.6 s. RocksDB was run through a modified db_bench (SILK fork; the author's issue-tracker command uses --sync=0 and no compression). The paper names no compiler; the repo builds with clang -O2 and TCMalloc, and only the KVell side of the harness is published.

## Use it when

- Point-read and update-heavy workloads (YCSB A/B/C/F style) on NVMe or Optane drives where RocksDB is CPU-bound on compaction and cannot saturate the device.
- Items of roughly 100 B to 4 KB where you need bounded worst-case latency: the paper reports 3.9 ms max versus 9.6 s for RocksDB, because nothing runs in the background.
- Write-heavy mixes with medium values, such as the Nutanix 57:41:2 write:read:scan workloads (250 B-1 KB items), where KVell was about 4x RocksDB.
- Machines with several NVMe drives and many cores. Each worker is tied to one disk, and the design scaled to 8 drives and 5 B keys on i3.metal.
- As a design reference or starting point for your own NVMe store (for example, porting it to io_uring or SPDK) when your keys are naturally unique 8-byte integers.

## Skip it when

- Keys whose first 8 bytes are not unique (for example, string keys with a common prefix like 'user0000'). The index and worker routing use only an 8-byte prefix, and the code dies on 'Adding item that is already in the database' or on key mismatch during updates.
- Values above about 4 KB including the 24-byte header (it dies with 'Item is too big'), or values that grow past their slab class on update (assert). The paper describes multi-block items and slab migration, but the released code does not implement them.
- Scan-heavy workloads with small items, or older SATA SSDs. Each scanned item costs one random 4 KB read, so RocksDB wins with 64 B items, uniform YCSB E is only about even (13.9K vs 14.4K scans/s), and on a SATA S3500 KVell managed 3K scans/s against RocksDB's 15K.
- Datasets whose index does not fit in RAM. Index lookups fall from 15M/s to 109K/s when the index is 5x RAM. The page cache is also reserved up front from a compile-time size (30 GB by default).
- Anything production-grade. The author says 'don't use it in production'. There are no transactions (those are in the KVell+ osdi branch), no snapshot-consistent scans, no checksums, no fsync, slab files never shrink, and it relies on the drive writing 4 KB pages atomically on power failure.

## How it is fast

It is shared-nothing: keys are split across worker threads by their first 8 bytes, and each worker owns its own in-memory B-tree index (Google cpp-btree, about 19 B per key), its own LRU page cache and free lists, and slab files on a single disk. Items are not sorted on disk. They sit in size-class slab files (100 B to 4 KB) and are updated in place, so there is no compaction, no commit log and no write amplification beyond the 4 KB page. Each worker batches up to 64 requests per Linux AIO io_submit/io_getevents call with O_DIRECT, which amortizes syscall cost and keeps the device queue deep without overfilling it. The bet is that random I/O on modern NVMe is as cheap as sequential I/O, so CPU cycles spent keeping data sorted are wasted.

## Compared with alternatives

Pick KVell over the LSM siblings (PebblesDB, MatrixKV, TerarkDB, Titan) when you run a point-operation-heavy workload on fast NVMe and care most about worst-case latency. It has no compaction, and its paper measured PebblesDB directly on YCSB A (KVell 5.8x faster). Pick SplinterDB, an LSM sibling or NuDB instead when you need a real embeddable library, arbitrary keys, values above 4 KB or small-item range scans. KVell is a prototype you would have to finish yourself.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libc, pthreads, libm, libstdc++ (the Google cpp-btree is vendored). Linux AIO is called through raw syscalls, so libaio is not needed. gperftools TCMalloc is optional but recommended (the run script LD_PRELOADs it). |
| **Minimum toolchain** | Makefile defaults to clang/clang++ with -std=c++11 for the B-tree index code. GCC needs -fno-strict-aliasing (per a Makefile comment). README targets Ubuntu 18.04. No minimum compiler version is documented. |
| **Platforms** | Linux only (linux/aio_abi.h, io_setup/io_submit syscalls, O_DIRECT, fallocate, pthread_setaffinity_np). In practice x86-64 only, because the timing code uses rdtsc inline asm. It assumes SSDs whose 4 KB writes are atomic on power failure. |
| **Thread safety** | Any number of client threads can call the kv_\*_async functions (an atomic-counter enqueue into each worker's ring that spin-waits when the ring is full). Each key partition is served by exactly one worker thread, and callbacks run on that thread, so they must not block. Scans take a spinlock on each worker's index in turn. kv_read_sync is marked unsafe and is only used during startup. |
| **Drop-in for the baseline** | no |

## Gotchas

- On master, kv_add_or_update_async is broken: the ADD_OR_UPDATE case in slabworker.c has no 'break' and falls through into DELETE, so an existing key is updated and then deleted. The bundled benchmarks never call it (they use add, update and read), so the paper numbers are unaffected.
- All configuration is compile-time #defines in options.h: the data path pattern /scratch%lu/kvell/..., PAGE_CACHE_SIZE, queue depth and PINNING. With PINNING=1, workers are pinned to cores 0..W-1 and busy-spin even when idle. You need a core for every worker and injector, or you must turn pinning off.
- Data is split statically by key prefix modulo the worker count. Changing the number of disks or workers means deleting the database, and every start rebuilds all indexes by scanning every slab (the paper measured 6.6 s for 100 GB on 8 NVMe drives).
- Scans are not snapshots: they return each key's latest value. Keys are ordered by their first 8 bytes read as a native uint64, which on little-endian x86 is not lexicographic byte order. The caller's thread does the merge across workers, so the scan benchmark uses 12 injector threads instead of 4.

## Known shortcomings

- Research prototype (author: don't use in production), dormant since 2020, source drop that builds a bench binary, async callback C API, no RocksDB drop-in. Index and worker routing use only the first 8 key bytes (keys sharing that prefix abort; scans are uint64 order, not lexicographic). Items over 4 KB abort and growing past a slab class asserts; the paper's multi-block/migration never shipped. Bug on master: ADD_OR_UPDATE falls through into DELETE (benchmarks don't call it). No fsync, checksums, transactions or snapshot scans; slabs never shrink; needs 4 KB power-atomic SSDs; Linux AIO + x86 rdtsc only; compile-time config, 30 GB page cache reserved at start, pinned busy-spinning workers. Weak on small-item and SATA scans (3K vs RocksDB 15K) and when the index exceeds RAM (15M to 109K lookups/s). RocksDB baseline via the SILK db_bench fork with --sync=0 and no compression.

## Caveats and trade-offs

Peer-reviewed SOSP'19 paper. The paper states no compiler or flags, and the repo Makefile defaults to clang -O2. CPU models are not named. The repo reproduces only the KVell side (scripts/run-aws.sh, sample_results); the RocksDB/PebblesDB/TokuMX/WiredTiger runs have no published harness. Scans are weaker: RocksDB wins with small items, and uniform YCSB E is about equal (13.9K vs 14.4K scans/s). The latest commit (2025-12-15) only fixes random-number generation in a workload generator; before that the last commit was 2020-11, and the 'osdi' branch holds KVell+ (OSDI'20).

Shared-nothing architecture can suffer load imbalance; no in-memory sorted global index so scans are relatively weaker; designed around 4KB-atomic-write SSDs.

## Maintenance

The repo is effectively dormant: master has only an initial 2019 commit, a 2020 README update and a December 2025 fix to a workload random-number generator, and the 8 open issues are mostly user questions the author answered in 2020. It is an MIT-licensed C prototype, with a core engine of about 1.8K lines, that is easy to vendor and study, but you would own every fix (including the ADD_OR_UPDATE fall-through), and the author explicitly says not to use it in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SOSP'19 paper compares KVell against RocksDB 6.2 (plus PebblesDB, TokuMX, WiredTiger) on YCSB and Nutanix workloads. Not A: the repo has only KVell-side YCSB code and scripts (workload-ycsb.c, scripts/run-aws.sh), with no RocksDB or competitor harness; the paper names no CPU models ('2.4GHz Intel Xeon', '4.2GHz Intel i7') and gives no compiler or flags.
- **Verifier notes:** The claim matches the paper abstract. I made the latency wording precise ('maximum', not 'tail') and added per-workload RocksDB numbers from the body. The metadata checked out: MIT, 293 stars, not a fork, last commit 2025-12-15 (active). I opened the benchmark PDF through raw.githubusercontent (same file as the blob URL).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/BLepers/KVell>
  - <https://raw.githubusercontent.com/BLepers/KVell/master/sosp19-final40.pdf>
  - <https://github.com/BLepers/KVell/blob/master/Makefile>
  - <https://github.com/BLepers/KVell/blob/master/README.md>
  - <https://github.com/BLepers/KVell/tree/master/scripts>
- **Sources the enricher read:**
  - <https://github.com/BLepers/KVell>
  - <https://github.com/BLepers/KVell/blob/master/README.md>
  - <https://github.com/BLepers/KVell/blob/master/OVERVIEW.md>
  - <https://github.com/BLepers/KVell/blob/master/Makefile>
  - <https://github.com/BLepers/KVell/blob/master/options.h>
  - <https://github.com/BLepers/KVell/blob/master/headers.h>
  - <https://github.com/BLepers/KVell/blob/master/main.c>
  - <https://github.com/BLepers/KVell/blob/master/items.h>
  - <https://github.com/BLepers/KVell/blob/master/slab.h>
  - <https://github.com/BLepers/KVell/blob/master/slab.c>
  - <https://github.com/BLepers/KVell/blob/master/slabworker.h>
  - <https://github.com/BLepers/KVell/blob/master/slabworker.c>
  - <https://github.com/BLepers/KVell/blob/master/ioengine.h>
  - <https://github.com/BLepers/KVell/blob/master/ioengine.c>
  - <https://github.com/BLepers/KVell/blob/master/pagecache.c>
  - <https://github.com/BLepers/KVell/blob/master/utils.h>
  - <https://github.com/BLepers/KVell/blob/master/utils.c>
  - <https://github.com/BLepers/KVell/blob/master/stats.c>
  - <https://github.com/BLepers/KVell/blob/master/random.c>
  - <https://github.com/BLepers/KVell/blob/master/microbench.c>
  - <https://github.com/BLepers/KVell/blob/master/benchcomponents.c>
  - <https://github.com/BLepers/KVell/blob/master/in-memory-index-btree.c>
  - <https://github.com/BLepers/KVell/blob/master/in-memory-index-generic.h>
  - <https://github.com/BLepers/KVell/blob/master/indexes/memory-item.h>
  - <https://github.com/BLepers/KVell/blob/master/indexes/btree.cc>
  - <https://github.com/BLepers/KVell/blob/master/indexes/btree.h>
  - <https://github.com/BLepers/KVell/blob/master/workload-common.h>
  - <https://github.com/BLepers/KVell/blob/master/workload-common.c>
  - <https://github.com/BLepers/KVell/blob/master/workload-ycsb.c>
  - <https://github.com/BLepers/KVell/blob/master/workload-production.c>
  - <https://github.com/BLepers/KVell/blob/master/scripts/run-aws.sh>
  - <https://github.com/BLepers/KVell/blob/master/scripts/sample_results/README>
  - <https://raw.githubusercontent.com/BLepers/KVell/master/sosp19-final40.pdf>
  - <https://github.com/BLepers/KVell/commits/master>
  - <https://github.com/BLepers/KVell/branches>
  - <https://github.com/BLepers/KVell/blob/osdi/README.md>
  - <https://github.com/BLepers/KVell/blob/osdi/slabworker.c>
  - <https://github.com/BLepers/KVell/issues/1>
  - <https://github.com/BLepers/KVell/issues/2>
  - <https://github.com/BLepers/KVell/issues/3>
  - <https://github.com/BLepers/KVell/issues/4>
  - <https://github.com/BLepers/KVell/issues/5>
  - <https://github.com/BLepers/KVell/issues/6>
  - <https://github.com/BLepers/KVell/issues/8>
  - <https://github.com/BLepers/KVell/issues/9>
  - <https://github.com/BLepers/KVell/issues/10>
  - <https://github.com/BLepers/KVell/issues/11>
  - <https://github.com/BLepers/KVell/issues/12>
  - <https://hn.algolia.com/api/v1/search?query=KVell&tags=story>
  - <https://export.arxiv.org/api/query?search_query=abs:KVell&max_results=10>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/blepers/kvell`) · [data/wave6/enrich/raw/github_com_blepers_kvell.json](../../../data/wave6/enrich/raw/github_com_blepers_kvell.json) (enrichment confidence 0.85)

</details>
