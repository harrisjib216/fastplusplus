# Nova-LSM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> LevelDB-based LSM KV server split into RDMA-linked compute and storage parts; beats LevelDB/RocksDB under skewed access.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 2.3x to 18x higher throughput than LevelDB and RocksDB with a skewed (Zipfian) access pattern and a 2 TB database on 10 nodes (paper's contribution list), with comparable throughput under Uniform access. The 105x figure is not a distributed result. It comes from a single server with a 10 GB database on SW50 (50% scan/50% write) Zipfian, measured relative to ONE LevelDB instance (omega=1), and the paper gives 8x against LevelDB with 64 instances. The Figure 18a bar labels (LevelDB=1) put RocksDB at 6, RocksDB-tuned at 36 and RocksDB\* (64 instances) at 73 against Nova-LSM's 105. That is roughly 17.5x, 2.9x and 1.4x over those RocksDB configurations (derived from page data). |
| **Workload** | YCSB RW50/SW50/W100 workloads (R100 also used for response times), 1 KB records, 10 GB to 2 TB databases, Uniform and Zipfian access, on 1 server and on 10 servers, with logging disabled for all systems. Nova-LSM (disaggregated LTC/StoC components over RDMA) is compared with LevelDB and RocksDB in single-instance, 64-instance and tuned-knob configurations on CloudLab APT c6220 nodes. |
| **Metric** | throughput |
| **Hardware** | CloudLab APT c6220 nodes: 64GB RAM, two 8-core Xeon E5-2650v2 CPUs (32 vCPUs w/ hyperthreading), 1TB HDD, Mellanox FDR CX3 InfiniBand (56Gbps) + 10Gbps Ethernet |
| **Compiler and flags** | Not stated in the paper. The repo's CMakeLists.txt hard-codes /usr/bin/g++ (version unstated) with -std=c++11 -fexceptions -g, and the README build is a plain 'cmake . && make -j4' with no CMAKE_BUILD_TYPE. Build flags for the LevelDB/RocksDB baselines are unstated. |
| **Adoption** | 52 stars |
| **Last commit** | 2021-12-15 |
| **Links** | [repository](https://github.com/HaoyuHuang/NovaLSM) · [benchmark](https://arxiv.org/abs/2104.01305) |

## Verdict

With YCSB 1 KB records on CloudLab c6220 nodes (2x Xeon E5-2650v2, 64 GB, one 1 TB HDD, 56 Gbps InfiniBand), logging off for all systems and compiler and RocksDB version unstated, Nova-LSM beat LevelDB/RocksDB by 2.3x to 18x under Zipfian access on a 2 TB, 10-node database, and on one node reached 105x over a single LevelDB instance on SW50 Zipfian but only about 1.4x over 64-instance RocksDB\*. Under Uniform access throughput was roughly equal or lower, and the RocksDB/LevelDB wrapper binaries (rocksdb_main, leveldb_main) are not in the repo, whose checked-in RocksDB script sets block_cache_mb=0.

## Use it when

- You have a multi-node RDMA/InfiniBand cluster and want to reproduce or extend the SIGMOD 2021 disaggregated-LSM results. The repo ships CloudLab profiles, configs and experiment scripts.
- Range-partitioned data with heavily skewed (Zipfian 0.99) access, where in a shared-nothing setup the node holding the hot range saturates its own disk. Pooling StoCs gave 9x or more over shared-nothing on a 1 TB, 10-node setup.
- Write-heavy ingest with large memtable memory that stalls on Level0 compaction. With 10 StoCs, raising LTC memtable memory from 32 MB to 2 GB took W100 Uniform from 8.9K to 246K ops/s.
- Scan-plus-write workloads on skewed keys (SW50 Zipfian), where LevelDB/RocksDB iterate every version of a hot key and Nova's range index skips them.
- As a design reference for ideas you want to port into your own LSM engine: Dranges/Tranges, the memtable lookup index, power-of-d SSTable placement.

## Skip it when

- As an embedded RocksDB/LevelDB replacement inside an application process. It is a server with a static partition config, integer-only keys, and no atomic write batches (listed as future work in the paper).
- Uniform-access, CPU-bound workloads. The paper reports a 15% range-index overhead on single-node SW50 Uniform and 20-30% lower throughput on CPU-intensive uniform workloads. On tmpfs it is 10-30% slower under Uniform, and RocksDB\* (64 instances) beats it on SW50.
- Clusters without RDMA, or with newer NICs. The setup scripts target mlx4 (ConnectX-3) packages. Open issue #3 reports an IBV_WC_RETRY_EXC_ERR segfault on ConnectX-5 CloudLab nodes, and open issue #2 asks how to run it on one local machine. Neither has an answer.
- Anything that needs durability, deletes or ongoing support. Log replication is off by default (--log_record_mode=none), Delete does not write a tombstone, and the project has no releases or tags and no activity since 2021.

## How it is fast

It builds dynamic ranges (Dranges) inside each range, each with its own active memtables; writes are load-balanced across them, and Level0 SSTables from different Dranges do not overlap, so Level0-to-Level1 compaction runs in parallel and write stalls shrink. Hot keys stay in memory because memtables with fewer than 100 unique keys are merged rather than flushed, giving 65% less data written under skew. A lookup index sends each get to the single memtable or L0 SSTable that holds the latest version, and a range index lets scans skip stale versions of hot keys. SSTable blocks are scattered across rho StoCs, picked by power-of-d on disk-queue length, and compaction can be offloaded to StoCs.

## Compared with alternatives

Pick it only when the bottleneck is one node's disk under skewed, range-partitioned load and you have an RDMA cluster to pool disks across nodes. Otherwise KVell, SplinterDB, PebblesDB, MatrixKV and Titan are far easier single-node engines to adopt (Titan loads as a RocksDB plugin; MatrixKV attacks the same write-stall problem with an NVM tier instead of Dranges).

## Integration

| | |
|---|---|
| **Form** | static lib + server binary (CMake builds libleveldb plus nova_server_main); used in practice as a standalone server |
| **Dependencies** | libibverbs (RDMA verbs; linked unconditionally), libevent, gflags (static .a required), fmt (script installs 6.1.2 from source), pthreads; optional crc32c and snappy. Clients use the separate Java NovaLSM-YCSB-Client binding. |
| **Minimum toolchain** | C++11 (-std=c++11), CMake 3.9+; compiler hard-coded to /usr/bin/g++, version not documented |
| **Platforms** | Linux only (tested on CloudLab R320 and c6220 x86-64 nodes); multi-node mode needs an RDMA NIC (scripts load mlx4/ConnectX-3 drivers) |
| **Thread safety** | db.h keeps LevelDB's statement that a DB is safe for concurrent access from multiple threads. The server runs hundreds of worker threads per LTC. The paper says scans that span two ranges run at read-committed isolation. |
| **Drop-in for the baseline** | no |

## Gotchas

- Keys must be decimal-integer strings. The comparator (YCSBKeyComparator) and the Drange code parse keys with str_to_int. The server routes keys by numeric range from a static config file and asserts the key is within it. The lookup index is a dense array with one 4-byte slot for every integer in [lower_key, upper_key), allocated when the DB opens.
- Delete is not a real delete. DB::Delete calls WriteMemTablePool(key, Slice()), and every write path adds kTypeValue, so a deleted key reads back as an empty value rather than NotFound. The socket protocol has no DELETE at all.
- The paper's features are off by default. --enable_lookup_index, --enable_range_index and --enable_subrange all default to false, and logging defaults to none. The paper's comparison ran with logging disabled for every system. A failed Put hits NOVA_ASSERT and aborts the server.
- The default build is unoptimized: CMakeLists sets -g with no -O level and no CMAKE_BUILD_TYPE, and also builds -pg profiling binaries. nova_server_main multiplies --max_stoc_file_size_mb by 1024 only once; open issue #3 asks whether that is a bug, with no answer.

## Known shortcomings

- The 105x outlier is one server with 10 GB under a skewed Zipfian workload against a single LevelDB instance; in the same cell it is \~1.4x vs the tuned RocksDB\* and \~17.5x vs RocksDB (derived, Fig. 18a). The 2.3-18x headline is 2 TB across 10 nodes with RDMA. Repo builds with -g and no optimization level; stale since 2021.
- Not embeddable: an RDMA server exposing only GET/PUT/SCAN over a socket with a Java YCSB client. Keys must be decimal integers (the lookup index is a dense array sized upper_key-lower_key). Delete writes an empty value (no tombstone); no write batches. Logging is off by default, the paper's index/Drange flags default to false, and the build uses -g without -O.
- On uniform/CPU-bound workloads it is equal or 10-30% slower; RocksDB\* beats it on SW50 on tmpfs; the 105x vs one LevelDB is about 1.4x vs RocksDB\*. Abandoned 2021 with unanswered issues (ConnectX-5 segfault, local run); the RocksDB harness is not in the repo and ran with block_cache_mb=0.

## Caveats and trade-offs

Peer-reviewed (SIGMOD 2021, DOI 10.1145/3448016.3457297), but the compiler version and flags are unstated, and the repo's default build adds -g without an optimization level. The 105x figure is single-node and measured against a single untuned LevelDB instance; against 64-instance RocksDB\* the same scenario is only about 1.4x (derived from page data). The abstract's 'several orders of magnitude' is not borne out by the figures. With Uniform access, throughput is comparable or lower: there is a 15% range-index overhead on SW50 single-node, and the paper reports 20-30% degradation on CPU-intensive uniform workloads. On tmpfs, RocksDB\* beats Nova-LSM on SW50. The system needs RDMA/InfiniBand and was evaluated on dated HDD-based nodes with logging disabled. The code is an extension of LevelDB 1.22 (its CMake project is named leveldb), although it is not a GitHub fork.

Disaggregates storage from compute across networked components (RDMA), which requires a multi-node RDMA cluster (InfiniBand) rather than the single-node embedded deployment RocksDB/LevelDB target; large speedups are specific to skewed multi-tenant access patterns that a disaggregated design can load-balance, not representative of typical single-node embedded use.

## Maintenance

Abandoned research prototype (last master commit 2021-06-20, a contributed db_bench branch merged 2021-12-15, no releases, two open issues unanswered) under BSD-3-Clause, so it can legally be copied, but it is tied to CloudLab/mlx4 scripts and is not realistically usable as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. The arXiv page carries DOI 10.1145/3448016.3457297, and the paper states 'a shorter version of this paper appeared in ACM-SIGMOD 2021', so it is peer-reviewed. It shows the win against RocksDB and LevelDB. It is not A because the compiler version and flags are unstated, even though the code and experiment scripts are public (scripts/exp/nova_rocksdb_comparison.sh, nova_rocksdb_10servers.sh, plus the NovaLSM-YCSB-Client repo) and the CPU (Xeon E5-2650v2) is named. The &gt;50x cap does not apply: against the named RocksDB baseline the reported gains are at most about 18x, and the 105x figure is against a single LevelDB instance, with an architectural explanation given.
- **Verifier notes:** The prompt flagged the 105x figure. It is a single-server (10 GB, SW50 Zipfian) throughput ratio against one LevelDB instance, not a distributed result and not against RocksDB. The best RocksDB configuration in that cell (RocksDB\*) is only about 1.4x behind, so claimed_speedup was rewritten. The last commit on the default branch (master) is 2021-06-20; the record's 2021-12-15 is the latest commit on the 'dbbench' branch (repo pushed_at), so I left it unchanged. Both dates mean abandoned. License BSD-3-Clause, 52 stars, not archived and not a fork: all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2104.01305>
  - <https://arxiv.org/pdf/2104.01305>
  - <https://github.com/HaoyuHuang/NovaLSM>
  - <https://raw.githubusercontent.com/HaoyuHuang/NovaLSM/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/HaoyuHuang/NovaLSM/master/build.sh>
  - <https://raw.githubusercontent.com/HaoyuHuang/NovaLSM/master/scripts/exp/nova_rocksdb_comparison.sh>
- **Sources the enricher read:**
  - <https://github.com/HaoyuHuang/NovaLSM>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/README.md>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/CMakeLists.txt>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/build.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/LICENSE>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/include/leveldb/db.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/include/leveldb/options.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/db/db_impl.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/db/db_impl.cc>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/db/lookup_index.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/db/lookup_index.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/db/subrange_manager.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/ltc/db_helper.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/ltc/db_helper.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/novalsm/nova_server_main.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/novalsm/client_req_worker.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/novalsm/rdma_server.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/common/nova_common.cpp>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/common/nova_config.h>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/util/comparator.cc>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/config/nova-tutorial-config>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/scripts/bootstrap/env/install-deps.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/scripts/bootstrap/env/setup-rdma.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/scripts/tutorial/nova_lsm_tutorial.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/scripts/exp/nova_rocksdb_comparison.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/blob/master/scripts/exp/nova_rocksdb_bench.sh>
  - <https://github.com/HaoyuHuang/NovaLSM/issues/2>
  - <https://github.com/HaoyuHuang/NovaLSM/issues/3>
  - <https://github.com/HaoyuHuang/NovaLSM/pull/1>
  - <https://github.com/HaoyuHuang/NovaLSM/commits/master>
  - <https://github.com/HaoyuHuang/NovaLSM/commits/dbbench>
  - <https://github.com/HaoyuHuang/NovaLSM-YCSB-Client>
  - <https://arxiv.org/abs/2104.01305>
  - <https://arxiv.org/pdf/2104.01305>
  - <https://hn.algolia.com/api/v1/search?query=Nova-LSM&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/haoyuhuang/novalsm`) · [data/wave6/enrich/raw/github_com_haoyuhuang_novalsm.json](../../../data/wave6/enrich/raw/github_com_haoyuhuang_novalsm.json) (enrichment confidence 0.8)

</details>
