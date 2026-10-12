# TreeLine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Update-in-place key-value store for NVMe SSDs with record caching and page grouping; beats RocksDB on read-heavy, skewed, scan YCSB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | On YCSB, TreeLine outperforms RocksDB by 2.20x on average (geometric mean) across the 1024-byte-record point workloads, and by up to 10.95x overall. On uniformly distributed scan-heavy workloads (YCSB E) with 16 request threads it wins 2.50x (1024 B) and 2.21x (64 B), averaged across three datasets; on Zipfian scans it wins 1.88x (1024 B) and 1.74x (64 B). On Zipfian point workloads (Amazon dataset) it wins 1.62x (64 B) and 2.99x (1024 B). On uniform point workloads the average speedup over RocksDB is only 1.45x. |
| **Workload** | YCSB point workloads (A, B, C, D, F) and scan-heavy workload E, run with the authors' own C++ YCSB implementation. Records are 64 bytes and 1024 bytes (8-byte keys), with Zipfian (theta 0.99) and uniform request distributions. Datasets are synthetic (20M keys), Amazon reviews (33M keys) and OpenStreetMap (23M keys). Each system gets memory for up to 33% of the dataset and 4 background threads. RocksDB 6.14.6 runs with block compression and SSTable checksums disabled. All runs on an NVMe SSD. |
| **Metric** | throughput |
| **Hardware** | 20-core 2.10GHz Intel Xeon Gold 6230, 128GiB RAM, 1TB Intel DC P4510 NVMe SSD, Linux 5.12.5, ext4 |
| **Compiler and flags** | Compiler is not stated in the paper or the repo. The repo README builds with CMAKE_BUILD_TYPE=Release, and CMakeLists.txt sets C++17 and adds -march=native. |
| **Adoption** | 147 stars |
| **Last commit** | 2024-01-02 |
| **Links** | [repository](https://github.com/mitdbg/treeline) · [benchmark](https://www.vldb.org/pvldb/vol16/p99-yu.pdf) |

## Verdict

In the authors' own PVLDB 16(1) paper (their C++ YCSB runner; 20-core Xeon Gold 6230, 128 GiB RAM, 1 TB Intel DC P4510 NVMe, Linux 5.12.5/ext4; memory for 33% of the data; compiler not named, build uses -march=native), TreeLine averaged 2.20x RocksDB's throughput (geometric mean) on 1024 B point workloads, up to 10.95x, but only 1.45x on uniform point workloads. RocksDB 6.14.6 ran with block compression and checksums off and Bloom filters on, and write-ahead logging was disabled on every system.

## Use it when

- Larger-than-memory datasets on NVMe SSDs with skewed (Zipfian) read/update point traffic: the paper averages 1.62x (64 B records) and 2.99x (1024 B) over RocksDB on YCSB A/B/C/D/F.
- Short range-scan-heavy workloads (YCSB E: 95% scans of up to 100 records) with many request threads: 2.21x (64 B) and 2.50x (1024 B) over RocksDB on uniform scans, because it reads at least 1.9x less data from disk.
- Hot records scattered across the key space (for example user IDs whose activity has nothing to do with their key order): caching records instead of pages kept TreeLine's writes at 3.09 GiB against LeanStore's 23.1 GiB on YCSB A with 64 B records.
- Fixed-size records with 64-bit integer keys whose distribution is locally near-linear: page grouping cut index entries 1.8-4.8x on the Amazon, OSM and synthetic datasets, which leaves more memory for the cache.
- As a reference implementation or starting point for research on update-in-place engines versus LSMs, not as a production store.

## Skip it when

- Anything that needs durability: the primary pg_treeline path has no write-ahead log, dirty writes reach disk only on eviction or clean shutdown, and the paper only sketches crash recovery and leaves it for future work (the code still has TODOs for logging reorganizations).
- Pure write or insert-heavy workloads: the paper says TreeLine 'currently cannot compete with RocksDB on pure write workloads', because every insert still needs a page read-modify-write.
- String or variable-length keys, deletes, or variable-size values: the pg API takes only uint64 keys, has no Delete (the code carries 'TODO: Support deletes'), and the page-grouping models assume fixed-size records.
- HDDs, SATA SSDs, or setups with little I/O parallelism: the design depends on random writes approaching sequential throughput on NVMe, which the paper shows only as concurrent writer threads increase. Scans also get no help from the record cache, whereas RocksDB's block cache can serve hot scan ranges.
- Production use in general: stale since January 2024, Linux-only I/O, one DB instance per process, and users have hit build problems (issue #112: Masstree config.h not generated, dl not linked).

## How it is fast

Each record lives in exactly one 4 KiB on-disk page, so a point read that misses the cache costs at most two page reads (base page plus at most one overflow page), whereas RocksDB may probe SSTables on several levels and spends reads on compaction. A Masstree-indexed record cache with clock-style priority eviction buffers every write, keeps hot records rather than hot pages, and batches dirty records bound for the same page when one is evicted. Page grouping runs the PGM-index's optimal piecewise linear regression during reorganization, writes key-adjacent pages as contiguous 1-16 page segments, and indexes only segment boundaries plus a linear model in an in-memory TLX B+tree, so scans become long sequential reads. Insert forecasting uses a per-epoch equi-depth histogram of inserts to decide how much free space each page keeps, cutting reorganizations.

## Compared with alternatives

Pick TreeLine over KVell when you need range scans and a small in-memory index (the paper notes KVell indexes every key and does random I/O on scans), and over F2/FASTER when ordered range scans matter, since the paper says FASTER does not support them efficiently. Prefer SplinterDB or RocksDB itself for insert-heavy or durability-critical workloads.

## Integration

| | |
|---|---|
| **Form** | static lib (pg_treeline CMake target; shared lib with TL_BUILD_SHARED=ON) |
| **Dependencies** | System packages libtbb-dev, libjemalloc-dev and autoconf (for Masstree's configure). CMake FetchContent pulls google/crc32c 1.1.1 and libcuckoo. Masstree, TLX and PGM are vendored in third_party. Benchmarks additionally fetch gflags, Google Benchmark, RocksDB 6.14.6, ycsbr, libaio and LeanStore. |
| **Minimum toolchain** | C++17 (needs std::filesystem), CMake 3.17+. Compiler versions are not documented. CI builds Debug on ubuntu-latest. |
| **Platforms** | Linux only in practice: storage I/O uses O_DIRECT\|O_SYNC with pread/pwrite and fallocate(). Built with -march=native, so binaries are tied to the build CPU. Only Ubuntu x86-64 appears in CI and the paper. |
| **Thread safety** | Contradictory documentation. The pg_db.h header says concurrent access is not supported, yet Get/Put/GetRange set up per-thread Masstree state, the engine uses segment and page locks, and the paper benchmarks up to 16 request threads. FlattenRange is documented as thread-safe. Experimental scan prefetching must not run alongside writes. Only one DB instance may exist per process. |
| **Drop-in for the baseline** | no |

## Gotchas

- No WAL on the pg_treeline path: Put only marks a record dirty in the in-memory record cache. The RecordCache destructor writes dirty entries out on clean close, so a crash loses every unflushed write. The paper's benchmarks disabled write-ahead logging on all three systems, RocksDB included.
- You must BulkLoad a non-empty, sorted, distinct record set into a fresh DB before any write; Put on an unloaded DB returns NotSupported. Keys 0 and 2^64-1 are reserved.
- Only one DB per process: the record cache keeps its entries in a static vector and the page manager uses a static thread_local workspace. PutBatchParallel (used by the optional parallel final flush) has a known deadlock TODO if a reorganization is needed.
- The repo contains two engines. pg_treeline (pg_db.h) is the primary, supported artifact. The older treeline target (db.h, which takes Slice keys and has Delete) is no longer supported, and a user hit a 2-thread segfault in it (issue #113). The default options also write debug CSVs (write_debug_info=true) and start 16 background I/O threads.

## Known shortcomings

- The original record misattributed its numbers: 2.20x is the 1024 B point-read average, 2.50x is uniform YCSB-E scans (not Zipfian), 1.62x is Zipfian 64 B; up to 10.95x in the best case. No compiler named.
- pg_treeline has no WAL or recovery (dirty writes live only in cache and are lost on crash), and the paper benchmarked with WAL off everywhere. API: uint64 keys only, no Delete, must BulkLoad before any Put, fixed-size records; not a RocksDB drop-in. Loses to RocksDB on pure writes (the paper says so); needs NVMe with high I/O parallelism.
- Linux only (O_DIRECT/fallocate), -march=native, one DB per process, and the header says no concurrency although the paper used 16 threads. Stale since 2024-01 with build issues (#112); the old 'treeline' target is unsupported and segfaults (#113).

## Caveats and trade-offs

Peer-reviewed PVLDB 16(1) (2022) paper, but no compiler is named anywhere (the repo builds Release with -march=native), which caps the tier at B. RocksDB was run with block compression and SSTable checksums disabled. Gains vary a lot by workload: uniform point workloads average only 1.45x over RocksDB, and LeanStore beats TreeLine on some 64 B Zipfian scan cases. This is prototype research code with no commits since January 2024.

Update-in-place B+tree design targets modern NVMe SSDs specifically (random writes there approach sequential-write throughput); benefit is smaller or absent on HDD/SATA-SSD; RocksDB was run with compression and SSTable checksums disabled to match TreeLine's feature set, so this is not an out-of-the-box RocksDB comparison

## Maintenance

A stale research prototype (last commit 2024-01-02, a README tweak; the 8 open issues are mostly unfinished cleanup) that is MIT-licensed and copyable, but expect to fix the build and add durability and deletes yourself before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 16(1) paper compares against RocksDB 6.14.6 (and LeanStore) and states the CPU (Xeon Gold 6230). The artifact repo has benchmark code (bench/, scripts/ycsb_v2, scripts/e2e_perf), but neither the paper nor the repo names the compiler, so it falls short of A.
- **Verifier notes:** The numbers in the record are all in the paper but attached to the wrong conditions. 2.20x is the 1024 B point-workload average, not '16 threads, uniform'. 2.50x is the uniform YCSB E scan result, not a skewed one. 1.62x is the Zipfian 64 B point result, not a real-world-only figure. I rewrote the claim. Metadata checked out: MIT, 147 stars, not a fork, not archived, last commit 2024-01-02, so stale is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.vldb.org/pvldb/vol16/p99-yu.pdf>
  - <https://github.com/mitdbg/treeline>
  - <https://github.com/mitdbg/treeline/blob/master/README.md>
  - <https://github.com/mitdbg/treeline/blob/master/CMakeLists.txt>
  - <https://github.com/mitdbg/treeline/tree/master/bench>
  - <https://github.com/mitdbg/treeline/tree/master/scripts>
- **Sources the enricher read:**
  - <https://www.vldb.org/pvldb/vol16/p99-yu.pdf>
  - <https://github.com/mitdbg/treeline>
  - <https://github.com/mitdbg/treeline/blob/master/README.md>
  - <https://github.com/mitdbg/treeline/blob/master/include/treeline/pg_db.h>
  - <https://github.com/mitdbg/treeline/blob/master/include/treeline/pg_options.h>
  - <https://github.com/mitdbg/treeline/blob/master/include/treeline/db.h>
  - <https://github.com/mitdbg/treeline/blob/master/CMakeLists.txt>
  - <https://github.com/mitdbg/treeline/blob/master/third_party/CMakeLists.txt>
  - <https://github.com/mitdbg/treeline/blob/master/.gitmodules>
  - <https://github.com/mitdbg/treeline/blob/master/.github/workflows/ci.yml>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/CMakeLists.txt>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/pg_db_impl.h>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/pg_db_impl.cc>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/pg_interface.h>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/manager.h>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/manager.cc>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/manager_rewrite.cc>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/manager_load.cc>
  - <https://github.com/mitdbg/treeline/blob/master/page_grouping/persist/segment_file.h>
  - <https://github.com/mitdbg/treeline/blob/master/record_cache/record_cache.h>
  - <https://github.com/mitdbg/treeline/blob/master/record_cache/record_cache.cc>
  - <https://github.com/mitdbg/treeline/blob/master/wal/CMakeLists.txt>
  - <https://github.com/mitdbg/treeline/commits/master>
  - <https://github.com/mitdbg/treeline/issues>
  - <https://github.com/mitdbg/treeline/issues/112>
  - <https://github.com/mitdbg/treeline/issues/113>
  - <https://github.com/mitdbg/treeline/issues/117>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mitdbg/treeline`) · [data/wave6/enrich/raw/github_com_mitdbg_treeline.json](../../../data/wave6/enrich/raw/github_com_mitdbg_treeline.json) (enrichment confidence 0.8)

</details>
