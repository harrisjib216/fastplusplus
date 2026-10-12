# UStore (UDisk engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Apache-2.0` · 🔴 abandoned

> Closed-source NVMe KV engine (UDisk) behind UStore's open C API; vendor numbers show 2-7x RocksDB throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | As of December 2022 (first-party table, ops/sec, RocksDB -&gt; UDisk): Batch Read 650K -&gt; 4.5M (\~6.9x, derived from page data); Batch Upsert 57K -&gt; 260K (\~4.6x, derived); Read 420K -&gt; 1M (\~2.4x, derived); Read & Update 1:1 64K -&gt; 173K (\~2.7x, derived); Read & Upsert 19:1 128K -&gt; 270K (\~2.1x, derived); Remove 420K -&gt; 874K (\~2.1x, derived); Scan 17M vs 17M (no gain). |
| **Workload** | Binary KV operations (scan, batch read, read, read & update 1:1, read & upsert 19:1, batch upsert, remove) via the UCSB harness, UDisk vs RocksDB. The table does not give the collection size; the page links separate UCSB result posts for 1 TB and 10 TB collections. |
| **Metric** | throughput |
| **Adoption** | 639 stars |
| **Last commit** | 2023-08-18 |
| **Links** | [repository](https://github.com/unum-cloud/UStore) · [benchmark](https://github.com/unum-cloud/UStore/blob/main/benchmarks/README.md) |

## Verdict

These are vendor-run UCSB numbers: apart from Batch Upsert, the README rows match Unum's September 2022 10 TB run of RocksDB 6.29.3 against UDisk (then 'UnumDB'), with 8-byte integer keys, 1 KB values, compression off, no flushing, 64 client threads and 256-key batches on an AMD Threadripper PRO 3995WX with 1 TB RAM, 8x Samsung PM1733 NVMe and Ubuntu 22.04 (kernel 5.15, ext4); no compiler is stated, and the README table gives no setup at all. Under those conditions batch reads ran \~6.9x and point reads \~2.4x faster, scans tied, and RocksDB won range selects \~2.5x.

## Use it when

- You have, or can negotiate, a UDisk binary from Unum and run Linux servers with several NVMe drives, where batched random reads and upserts of values around 1 KB dominate.
- Keys are naturally 64-bit integers (row IDs, graph vertex IDs) and you can send batches of hundreds of keys per call instead of single Gets; batch read is the vendor's largest win (650K vs 4.5M ops/s).
- You want one transactional C API over blobs, documents and graphs, with NetworkX- and Pandas-style Python front ends. You can start on the open UCSet or RocksDB engines and swap in UDisk later without changing application code.

## Skip it when

- You need an engine you can build, audit or patch: UDisk is binary-only, and UStore's own engine table marks it as not open source.
- Range-select-heavy workloads: in the vendor's own 10 TB run RocksDB did 5M ops/s against 2M for UDisk (then called UnumDB), and the README table leaves that row out.
- Non-Linux targets, or code that relies on RocksDB features such as string keys with custom comparators, prefix seeks and column-family options. UDisk is Linux-only and links liburing, libnuma and libexplain.
- You need durable writes by default. UStore turns durability off unless you pass ustore_option_write_flush_k, and its RocksDB adapter sets disableWAL whenever that flag is missing.
- Production systems that need a live upstream: main was last committed 2023-08-18, and open bugs include the README's rocksdb.DataBase('/path') example failing to open (#434).

## How it is fast

Unum describes UDisk as a modified LSM tree built for NVMe block devices, with io_uring for partial kernel bypass, SPDK for full bypass, a custom internal filesystem and optional CUDA offload of background compactions. Its config offers posix, 'pulling' and 'polling' IO mechanisms with queue depths up to 4096, native fixed-size integer keys and optional fixed-size values. Batch reads go in as a group so the engine can reorder them and issue them asynchronously, which is where the widest gap over RocksDB's MultiGet shows up; none of this can be checked, because the source is closed.

## Compared with alternatives

Pick UDisk only if you have a commercial path to the binary and a batch-heavy, integer-keyed workload on Linux machines with several NVMe drives; for an engine you can build and audit, SplinterDB (6-10x faster inserts and 2-2.6x faster point queries than RocksDB), KVell or F2 (FASTER) have open code and better evidence. UStore's open parts only beat them if you want its multi-modal API over RocksDB or UCSet, not for speed.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake builds ustore_embedded_&lt;engine&gt; static libraries; UDisk is a prebuilt static archive passed in through USTORE_ENGINE_UDISK_PATH) |
| **Dependencies** | UStore: Apache Arrow (plus Flight and Parquet), simdjson, yyjson, mongo-c-driver (BSON), PCRE2, fmt, mpack, nlohmann/json; optional jemalloc, oneTBB, Boost, OpenSSL. UDisk adds liburing, libnuma, libexplain, libdl and pthread. |
| **Minimum toolchain** | C++17 and CMake 3.16+ (C99 for the C headers); no minimum compiler version documented |
| **Platforms** | UDisk: Linux only. UStore: Linux; the roadmap lists Arm and macOS builds as done. x86 builds hard-code -msse4.2 -mavx2 in CMake. PyPI 'ukv' 0.12.1 ships only manylinux x86_64 wheels for CPython 3.9 and 3.10. |
| **Thread safety** | Per db.h, a database handle can be shared across threads between open and free. Transaction handles are not thread-safe and use optimistic concurrency control, and only one process may open an embedded database directory. UDisk caps concurrent accessor threads with its concurrency_limit setting. |
| **Drop-in for the baseline** | partial — UStore can wrap RocksDB itself (as an OptimisticTransactionDB) behind its own API. Moving to UDisk still means adopting the ustore_\* C API with integer keys; there is no RocksDB-compatible API and no support for RocksDB options files. |

## Gotchas

- The December 2022 table matches Unum's September 2022 10 TB post row for row except Batch Upsert. The post gives UDisk 117K ops/s on CPU and 182K with a GPU, not 260K, so no published run backs the \~4.6x upsert figure. The table also leaves out Initialization (603K vs 60M) and Range Select, where RocksDB won.
- The setup favored UDisk. In the post each engine got 8 SSD partitions, but RocksDB can take at most 4 db_paths and ingested SSTs land on the first disk. The UCSB RocksDB adapter runs with the WAL disabled. In the earlier single-threaded 1 TB run the gaps were much smaller: random reads 175.7K vs 160.7K (\~1.1x), batch insert 813K vs 690K (\~1.2x).
- Reproduction is blocked even with a binary. UCSB's cmake/ustore.cmake clones a 'main-dev' branch that no longer exists and passes -DUSTORE_ENGINE_NAME_UDISK_PATH, while UStore's CMake reads USTORE_ENGINE_UDISK_PATH. UCSB also has no license, and its committed RocksDB 10TB.cfg says 7.2.9 while the post says 6.29.3.
- The PyPI package is 'ukv' (imported as ustore.\*), not 'ustore'; issue #383 shows users confused by the ukv/ustore/ucset naming. Per #434, opening RocksDB works only when you pass a JSON config with create_if_missing, not a bare path.

## Known shortcomings

- The UDisk engine behind the numbers is closed source and binary-only; the table does not state the dataset size.
- The README table comes from a 2022-09 10 TB post (Threadripper 3995WX, 8x PM1733, RocksDB 6.29.3 without WAL, 64 threads); the 260K batch-upsert figure matches no run (the post says 117K CPU, 182K GPU). The table omits Range Select, where RocksDB wins 5M vs 2M; RocksDB was capped at 4 db_paths; a 1 TB single-thread run shows reads only \~1.1x.
- Cannot be reproduced: the UCSB benchmark's cmake clones a deleted main-dev branch and passes the wrong UDisk path variable, and UCSB has no license. UDisk has no public download; Linux only. Durability is off by default and the RocksDB adapter disables WAL. Abandoned since 2023-08; bug #434 (README RocksDB open fails).

## Caveats and trade-offs

The benchmarked engine, UDisk, is closed source. UStore's own engines table marks it Open-Source ✗, UStore's CMake only links a prebuilt UDisk static library through USTORE_ENGINE_UDISK_PATH, and the unum-cloud/UDisk repo holds only a README, docs and assets. The Apache-2.0 UStore repo covers the bindings plus the UCSet, LevelDB and RocksDB adapters, not the engine being measured. The table is labeled 'typical results ... as of December 2022', with no hardware, compiler or dataset size; the UCSB harness repo has no LICENSE file. The default branch (main, the only branch) was last committed 2023-08-18 even though the repo's pushed_at is 2026-09-15.

UDisk is Unum's own default embedded engine inside UStore (distinct from the pure in-memory UCSet backend); the companion low-level harness, unum-cloud/ucsb, also benchmarks LMDB, LevelDB, and WiredTiger natively but that harness repo carries no license (license: null), so treat it as reference-only even though UStore itself is Apache-2.0.

## Maintenance

Abandoned: main (the only branch) was last committed 2023-08-18 at v0.13.12, and neither UStore nor the placeholder UDisk repo links a public UDisk download, so the Apache-2.0 bindings still work with RocksDB, LevelDB and UCSet but the engine this entry measures is out of reach.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party table ('As of December 2022, typical results can look like') comparing UDisk with RocksDB, with no hardware, compiler, flags or dataset size given for the table. The harness (unum-cloud/ucsb) is public, but the engine under test (UDisk) is a closed-source binary, so the result cannot be reproduced.
- **Verifier notes:** The table numbers match the record. '1 TB' is not stated for this table, and the old caveat about 'more recent pushes to other branches' is wrong, since main is the only branch. The measured engine UDisk is proprietary and binary-only, so the orchestrator may want to retag or rename the entry: nothing benchmarked here can be copied.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/unum-cloud/UStore/blob/main/benchmarks/README.md>
  - <https://github.com/unum-cloud/UStore>
  - <https://github.com/unum-cloud/UStore/blob/main/README.md>
  - <https://github.com/unum-cloud/UStore/blob/main/CMakeLists.txt>
  - <https://github.com/unum-cloud/UDisk>
  - <https://github.com/unum-cloud/ucsb>
  - <https://unum.cloud/post/2021-11-25-ycsb>
  - <https://unum.cloud/post/2022-03-22-ucsb>
- **Sources the enricher read:**
  - <https://github.com/unum-cloud/UStore>
  - <https://github.com/unum-cloud/UStore/blob/main/README.md>
  - <https://github.com/unum-cloud/UStore/blob/main/benchmarks/README.md>
  - <https://github.com/unum-cloud/UStore/blob/main/CMakeLists.txt>
  - <https://github.com/unum-cloud/UStore/blob/main/VERSION>
  - <https://github.com/unum-cloud/UStore/blob/main/CHANGELOG.md>
  - <https://github.com/unum-cloud/UStore/blob/main/src/README.md>
  - <https://github.com/unum-cloud/UStore/blob/main/src/engine_rocksdb.cpp>
  - <https://github.com/unum-cloud/UStore/blob/main/docs/related.md>
  - <https://github.com/unum-cloud/UStore/blob/main/docs/architecture.rst>
  - <https://github.com/unum-cloud/UStore/blob/main/include/ustore/db.h>
  - <https://github.com/unum-cloud/UStore/blob/main/include/ustore/README.md>
  - <https://github.com/unum-cloud/UStore/commits/main>
  - <https://github.com/unum-cloud/UStore/releases>
  - <https://github.com/unum-cloud/UStore/issues>
  - <https://github.com/unum-cloud/UStore/issues/434>
  - <https://github.com/unum-cloud/UStore/issues/383>
  - <https://github.com/unum-cloud/UStore/issues/359>
  - <https://github.com/unum-cloud/UDisk>
  - <https://github.com/unum-cloud/UDisk/blob/main/README.md>
  - <https://github.com/unum-cloud/ucsb>
  - <https://github.com/unum-cloud/ucsb/blob/main/README.md>
  - <https://github.com/unum-cloud/ucsb/blob/main/bench/configs/rocksdb/10TB.cfg>
  - <https://github.com/unum-cloud/ucsb/blob/main/bench/configs/ustore/10TB.cfg>
  - <https://github.com/unum-cloud/ucsb/blob/main/cmake/ustore.cmake>
  - <https://github.com/unum-cloud/ucsb/blob/main/src/rocksdb/rocksdb.hpp>
  - <https://pypi.org/pypi/ukv/json>
  - <https://unum.cloud/post/2022-09-13-ucsb-10tb/>
  - <https://unum.cloud/post/2022-03-22-ucsb/>
  - <https://unum.cloud/post/2021-11-25-ycsb/>
  - <http://web.archive.org/web/20221228164250/https://unum.cloud/post/2022-09-13-ucsb-10tb/>
  - <http://web.archive.org/web/20230204190848/https://unum.cloud/post/2022-03-22-ucsb/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/unum-cloud/ustore`) · [data/wave6/enrich/raw/github_com_unum_cloud_ustore.json](../../../data/wave6/enrich/raw/github_com_unum_cloud_ustore.json) (enrichment confidence 0.8)

</details>
