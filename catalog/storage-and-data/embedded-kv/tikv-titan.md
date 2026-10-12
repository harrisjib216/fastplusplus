# Titan (RocksDB plugin)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> RocksDB plugin that moves large values into separate blob files (WiscKey-style) to cut write amplification versus plain RocksDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | About 70% higher than RocksDB in data-loading (write) scenarios, with the gap growing as value size increases, and 180% higher in update scenarios; also better point-query performance, but underperforms RocksDB on range queries and has slightly higher space amplification |
| **Workload** | go-ycsb against TiKV in transaction mode, TiKV-on-Titan vs TiKV-on-RocksDB; 64GB raw dataset with TiKV memory capped at 32GB via cgroup; 16-byte keys, 1KB values (64M keys) and 16KB values (4M keys); data loading, update, point-query, range-iteration and output-size tests. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2630 v4 (40 cores), 128GB RAM, 1.5TB SATA SSD |
| **Adoption** | 514 stars; used as a key-value-separation plugin inside TiKV |
| **Last commit** | 2026-04-29 |
| **Links** | [repository](https://github.com/tikv/titan) · [benchmark](https://pingcap.com/blog/titan-storage-engine-design-and-implementation/) |

## Verdict

PingCAP's April 2019 blog ran go-ycsb against TiKV on Titan versus TiKV on RocksDB (64 GB dataset, TiKV capped at 32 GB RAM, 1 KB and 16 KB values) on a 40-core Xeon E5-2630 v4 with 128 GB RAM and a SATA SSD. It reports about 70% higher load throughput and 180% higher update throughput, better point gets, worse range scans and slightly higher space use; compiler, flags, versions and go-ycsb settings are not given, and the Raft log write in front of the engine dilutes the gain.

## Use it when

- Write- or update-heavy workloads with values of about 1 KB and up; PingCAP reports the gap over RocksDB widens as values grow, and its 16 KB tests gained most.
- RocksDB deployments limited by compaction I/O, write stalls or SSD wear from write amplification.
- Point-lookup-heavy reads on large values, where an LSM tree of only keys and blob indexes fits better in block cache.
- Mixed value sizes: values below min_blob_size stay inline in the SST, so only large values pay the extra blob-file read.
- You already run TiKV or can build against TiKV's RocksDB fork (tikv/rocksdb branch 8.10.tikv).

## Skip it when

- Range-scan-heavy workloads: PingCAP says Titan underperforms RocksDB on range queries and TiDB docs put the drop at 40% to a few times slower, because each scanned value is a separate blob-file read.
- Disk-space-limited deployments: space amplification is higher than RocksDB (TiDB docs say it can reach about twice RocksDB), and per-record blob compression compresses worse than RocksDB's per-block compression.
- Small values (well under 1 KB): they stay inline, so you take on the plugin's complexity for no gain.
- Code that needs Merge operators, SingleDelete or batched MultiGet: Titan rejects the first two, and its MultiGet is a loop of single Gets.
- Projects on upstream facebook/rocksdb: master uses the TiKV-fork-only kTypeTitanBlobIndex value type, so it does not build against upstream; RocksDB's own integrated BlobDB (enable_blob_files) gives the same key-value separation and supports Merge, SingleDelete and batched MultiGet.

## How it is fast

It uses key-value separation from the WiscKey paper: compaction rewrites only keys and small blob indexes, not the large values, so write amplification and compaction I/O drop for big values. TitanTableBuilder does the separation during flush and compaction, so the foreground write path (WAL plus memtable) stays RocksDB's. Blob garbage collection is driven by table-property collectors and flush/compaction listeners that track each blob file's discardable ratio (GC at 0.5 by default); optional Level Merge rewrites blobs while the last two LSM levels compact, which keeps them sorted for scans. The smaller LSM tree also leaves more block cache for index, filter and data blocks, which PingCAP credits for faster point reads.

## Compared with alternatives

Pick Titan over TerarkDB when values are large (1 KB and up) and the bottleneck is write/compaction amplification rather than read QPS or compression ratio, and when you want a plugin tracking a recent RocksDB (the TiKV 8.10 fork) rather than a full engine forked from RocksDB v5.18.3.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | RocksDB source tree (CMake clones tikv/rocksdb branch 8.10.tikv by default; each Titan branch pins a TiKV RocksDB fork branch); optional snappy, lz4, zstd, zlib, bzip2, jemalloc; gflags for the bench/stress tools |
| **Minimum toolchain** | C++17, CMake 3.10+ (legacy CI config used g++-9 and clang) |
| **Platforms** | Not documented in README; build flags cover x86-64 (SSE4.2), aarch64 (armv8 CRC) and ppc64le, the legacy Travis config targeted Linux x86-64, Linux arm64 and macOS, and production use is Linux through TiKV |
| **Thread safety** | Not separately documented; follows the rocksdb::DB model (one handle shared across threads), and thread_safety_test runs concurrent Put/Get/iteration with CompactRange and GC across column families |
| **Drop-in for the baseline** | partial — same rocksdb::DB interface through StackableDB, but it needs TiKV's RocksDB fork, rejects Merge and SingleDelete, and a Titan data directory cannot be opened by plain RocksDB until blob_run_mode kFallback has rewritten the values back into SSTs through compaction |

## Gotchas

- Space is reclaimed only when blob GC runs; blob_file_discardable_ratio and max_background_gc (default 1 thread) set how far disk use lags behind deletes and overwrites.
- Point reads take several more mutexes than plain RocksDB (issue #139 counts 7 against 2), and a Get without a snapshot creates a ManagedSnapshot; the issue flags this as overhead in CPU-bound, in-memory workloads.
- There is no direct rollback: switch blob_run_mode to kReadOnly or kFallback and let compaction inline values before you drop Titan.
- Open issues report crashes or failed restarts from missing or double-deleted blob files (#328, #186), and the repo has no running public CI (only a legacy Travis config), so pin a branch that matches a TiKV release.

## Known shortcomings

- Needs TiKV's RocksDB fork (kTypeTitanBlobIndex exists only in tikv/rocksdb 8.10.tikv), so it is not a drop-in for upstream RocksDB. Merge, SingleDelete and DisableFileDeletions return NotSupported; MultiGet is a loop of Gets; rollback requires kFallback mode and a compaction pass. Upstream RocksDB's integrated BlobDB (enable_blob_files) does the same key-value separation with fuller API support. Range scans 40% to several times slower and up to \~2x disk space (TiDB docs); weaker per-record blob compression; 7 mutexes per point read vs 2 (#139). Open crash in the compaction filter from a missing blob file (#328) and a critical double-deleted blob file that prevents restart (#186). No running CI (only old Travis); last master commit 2026-04-29. Evidence is one 2019 PingCAP blog measured end to end through TiKV with Raft in front, no compiler/flags/versions.

## Caveats and trade-offs

First-party vendor (PingCAP) blog from 2019 rather than an independent or peer-reviewed source; measured end-to-end through TiKV (writes go through the Raft log first, which the post says dilutes Titan's gain), not Titan vs RocksDB standalone; go-ycsb configs, versions, compiler and flags not stated; percentages read from charts/text with no raw tables.

Key-value separation (WiscKey-style) trades range-query performance and space amplification for write/update throughput, especially with large values.

## Maintenance

Maintained by the TiKV team at a slow pace (last master commit 2026-04-29) under Apache-2.0, and enabled by default for new TiKV clusters since v7.6.0, but usable outside TiKV only if you adopt TiKV's RocksDB fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party PingCAP blog (Apr 25, 2019) states 70% higher write and 180% higher update performance vs RocksDB with CPU/RAM/disk and dataset described, but benchmark configs, compiler and flags are not published, so it is C.
- **Verifier notes:** Numbers on the page match the record. last_commit corrected from pushed_at (2026-09-14, bot branches) to the master head 2026-04-29; still active. URL redirects to www.pingcap.com with the same article.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tikv/titan>
  - <https://pingcap.com/blog/titan-storage-engine-design-and-implementation/>
  - <https://www.pingcap.com/blog/titan-storage-engine-design-and-implementation/>
- **Sources the enricher read:**
  - <https://github.com/tikv/titan>
  - <https://github.com/tikv/titan/blob/master/include/titan/db.h>
  - <https://github.com/tikv/titan/blob/master/include/titan/options.h>
  - <https://github.com/tikv/titan/blob/master/CMakeLists.txt>
  - <https://github.com/tikv/titan/blob/master/cmake/rocksdb_flags.cmake>
  - <https://github.com/tikv/titan/blob/master/.travis.yml>
  - <https://github.com/tikv/titan/blob/master/src/db_impl.cc>
  - <https://github.com/tikv/titan/blob/master/src/table_builder.cc>
  - <https://github.com/tikv/titan/blob/master/src/blob_file_reader.cc>
  - <https://github.com/tikv/titan/blob/master/src/db_iter.h>
  - <https://github.com/tikv/titan/blob/master/src/thread_safety_test.cc>
  - <https://github.com/tikv/titan/issues>
  - <https://github.com/tikv/titan/issues/328>
  - <https://github.com/tikv/titan/issues/186>
  - <https://github.com/tikv/titan/issues/203>
  - <https://github.com/tikv/titan/issues/321>
  - <https://github.com/tikv/titan/issues/139>
  - <https://github.com/tikv/titan/commits/master>
  - <https://pingcap.com/blog/titan-storage-engine-design-and-implementation/>
  - <https://www.pingcap.com/blog/titan-storage-engine-design-and-implementation/>
  - <https://docs.pingcap.com/tidb/stable/titan-overview/>
  - <https://raw.githubusercontent.com/tikv/rocksdb/8.10.tikv/db/dbformat.h>
  - <https://raw.githubusercontent.com/facebook/rocksdb/main/db/dbformat.h>
  - <https://github.com/facebook/rocksdb/wiki/BlobDB>
  - <https://github.com/bytedance/terarkdb>
  - <https://hn.algolia.com/api/v1/search?query=titan%20rocksdb&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tikv/titan`) · [data/wave6/enrich/raw/github_com_tikv_titan.json](../../../data/wave6/enrich/raw/github_com_tikv_titan.json) (enrichment confidence 0.75)

</details>
