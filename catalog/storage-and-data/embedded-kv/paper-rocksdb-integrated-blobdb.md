# RocksDB integrated BlobDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 OR GPL-2.0` · 🟢 active

> RocksDB's built-in key-value separation: large values go to blob files, cutting compaction write amp versus stock leveled RocksDB.

| | |
|---|---|
| **Beats** | stock RocksDB (leveled compaction, no blob files) |
| **Claimed result** | Initial load 2.3x-4.7x faster with write amp near the theoretical minimum (1.0-1.02 vs 1.6); overwrite workload 2.1x-3.5x higher throughput and 75-78% lower write amp vs leveled; point-lookup/write mix 83-88% lower write amp; range-scan/write mix 88-90% lower write amp; up to 1.4x higher read throughput vs leveled (5.6x vs universal) for larger values; new BlobDB implementation 4.6x faster than legacy StackableDB BlobDB without WAL, 2.3x with WAL, on single-threaded random writes with 1KB values |
| **Workload** | Customized version of RocksDB's standard benchmark suite cycling through six phases (initial load with 1 TB of raw values, 16-thread overwrite, point-lookup/write mix, range-scan/write mix, read-only point lookups, read-only range scans) at six value sizes from 1KB to 1MB. It compares enable_blob_files=true (integrated BlobDB with leveled compaction) against leveled and universal compaction without blob files, on a RocksDB build equivalent to v6.18.1. |
| **Metric** | throughput |
| **Hardware** | 18-core Skylake DE CPU @ 1.6GHz (hyperthreading enabled), 64GB RAM, 512GB boot SSD, two 1.88TB M.2 SSDs in RAID0 for data |
| **Adoption** | 32.1k stars; used in production at Meta, MySQL/MyRocks, CockroachDB, TiKV, and others |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/facebook/rocksdb) · [benchmark](http://rocksdb.org/blog/2021/05/26/integrated-blob-db.html) |

## Verdict

RocksDB's own 2021 blog post ran a customized version of its standard benchmark suite: 1 TB of raw values, 1KB-1MB values, six load/overwrite/read phases, on a build equivalent to 6.18.1 and an 18-core Skylake DE @ 1.6GHz with 64GB RAM and two M.2 SSDs in RAID0; the compiler and flags are not stated. Against stock leveled compaction it reported 2.3-4.7x faster initial load, 2.1-3.5x higher overwrite throughput with 75-78% less write amp, and up to 1.4x faster reads for large values, but it lost on range scans at 1KB and 4KB; an independent 2025 paper (BVLSM: RocksDB 9.7.3, Xeon Gold 5218, NVMe, authors of a competing design) implies about 4x over stock RocksDB for 64KB random writes with async WAL, but only about 0.4-0.6x on sequential writes.

## Use it when

- Write-heavy or overwrite-heavy workloads with large values, where leveled compaction's write amp or write stalls cap throughput. The 2021 tests saw write-side wins at every value size from 1KB to 1MB.
- Flash-endurance- or bandwidth-sensitive deployments. The blog measured 75-90% lower write amp than leveled across its overwrite and mixed read/write phases.
- Point lookups on large values. The blog found BlobDB matched or beat leveled (up to 1.4x) for larger values, because the LSM holding only keys and pointers stays small.
- Cases where you would otherwise switch to universal compaction only for lower write amp. The RocksDB team recommends BlobDB with leveled compaction instead, which read up to 5.6x faster than universal in their tests.
- Large-value TTL or size-budget workloads on FIFO compaction. Since 11.0, FIFO can trim by combined SST and blob bytes, and a KV-ratio intra-L0 picker is built specifically for BlobDB.

## Skip it when

- Small values (1KB-4KB) with range scans. The blog's own results show BlobDB behind leveled on scan workloads at those two sizes, since each value costs an extra indirection into a blob file.
- Tight disk budgets. Overwritten or deleted blobs stay on disk until GC relocates them. GC is off by default, space comes back only in whole-blob-file increments (blob_file_size), and lowering space amp costs extra write amp.
- Insert-only or sequential-key loads. With GC on, the default 0.25 age cutoff kept relocating blobs in a pure-insert test, giving write amp of 7+ (issue #11570; the maintainer's advice is to disable GC). An independent 2025 paper (BVLSM, RocksDB 9.7.3) also found BlobDB slower than stock RocksDB on sequential writes and on sustained 4KB random writes.
- Deployments relying on multiple cf_paths/db_paths, RepairDB/ldb repair, or secondary instances. Blob files always go to the first cf path (open issue #8535, confirmed in blob_file_builder.cc). Repair drops blob files from the MANIFEST, so the next open deletes them and loses the data (open issues #13884 and #13090). The wiki lists secondary instances and blob-file ingestion as unsupported.
- Very large values under sustained overwrite. The blog's own overwrite runs were stall-free at every size except the largest, 1MB.

## How it is fast

It uses WiscKey-style key-value separation. Compactions sort and rewrite keys plus small pointers instead of the large values, so write amplification drops and compaction keeps up with ingest, which removes the write stalls that throttle stock leveled compaction under heavy overwrites. Blob files are written by the background flush and compaction threads, one writer per file, using large I/Os and doing compression off the foreground path; they are also tracked in the MANIFEST as part of the Version, so the read path is mostly lock-free. Garbage collection piggybacks on compaction: live blobs in the oldest blob_garbage_collection_age_cutoff fraction of blob files are relocated as their keys pass through compaction, and files holding nothing but garbage are dropped whole. This avoids WiscKey's GC, which issues a Get plus a Put for every blob it checks.

## Compared with alternatives

No siblings catalogued yet. Compared with the baseline, pick it over stock leveled RocksDB when values are large and writes or overwrites dominate, and over universal compaction when you wanted universal only for its lower write amp.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (part of librocksdb itself; turned on per column family through options, not a separate component) |
| **Dependencies** | None required. zlib, bzip2, lz4, snappy and zstd are optional, for blob_compression_type; gflags is needed only for the tools (db_bench, ldb). |
| **Minimum toolchain** | C++20: GCC 11+ or Clang 10+, per INSTALL.md (which still lists Visual Studio 2017+ for Windows) |
| **Platforms** | Per INSTALL.md: Linux, macOS, FreeBSD, OpenBSD, Windows (CMake/vcpkg), iOS, AIX and Solaris SPARC. No BlobDB-specific platform limits are documented. The published benchmark ran on x86-64 (Skylake DE). |
| **Thread safety** | Same as RocksDB: one process per DB, enforced by an OS file lock. A rocksdb::DB can be shared across threads without external locking, but Iterator and WriteBatch objects need external synchronization. A custom BlobFilePartitionStrategy (used by blob direct write) must be thread-safe and must not throw. |
| **Drop-in for the baseline** | partial — same rocksdb::DB API and database. Setting enable_blob_files (plus min_blob_size) on an existing column family moves values out as later flushes and compactions rewrite them. It is not a drop-in for the legacy rocksdb::blob_db::BlobDB (the release notes said at launch there was no migration path), and repair, multi-path storage and secondary instances do not handle blob files. |

## Gotchas

- min_blob_size defaults to 0, so enable_blob_files=true on its own sends every non-empty value to a blob file. Set a threshold.
- enable_blob_garbage_collection defaults to false. blob_garbage_collection_force_threshold=0.0 passes validation but makes an idle DB compact forever (open issue #15256, Sept 2026). blob_cache cannot be changed through SetOptions.
- Recent open bugs: MultiGet with value_size_soft_limit keeps returning Aborted when the first key's value is in a blob file, so the documented retry loop never ends (#15247). Another open issue reports FIFO max_data_files_size dropping far more data than its budget (#15252). A blob GC compaction failure (#14897) is fixed per the HISTORY.md 11.9.0 entry, but the newest tagged GitHub release is 11.8.1.
- Blob direct write (experimental, 2026) writes large values straight to blob files on the write path. Its v1 cannot recover still-active direct-write blob files by WAL replay after a crash, and it requires the ordered single-memtable-writer path, so no allow_concurrent_memtable_write, pipelined, unordered or two_write_queues writes.

## Known shortcomings

- A feature of RocksDB itself (enable_blob_files), listed separately from RocksDB's other features; range scans lose at 1-4 KB values; evidence is RocksDB's 2021 blog (v6.18.1) with no compiler/flags.
- DATA-LOSS RISK: RepairDB/ldb repair drops blob files (#13884, #13090, open). Blob GC is off by default (space amplification); insert-only with GC gives write amplification of 7+ (#11570); blobs always go to the first cf_path (#8535). Open bugs: force_threshold=0 causes endless compaction (#15256); MultiGet soft-limit never ends (#15247); the last tag 11.8.1 lacks the #14897 fix.

## Caveats and trade-offs

This is RocksDB's own engineering blog post, not an independent benchmark. It is a RocksDB feature measured against RocksDB's default (non-blob) configuration in the same repo. The CPU model and RocksDB version are stated, but exact benchmark command lines and compiler/build flags are not: the tool is described only as 'a customized version of our standard benchmark suite'. That caps it at tier C. BlobDB does not win everywhere: it falls behind leveled compaction on workloads involving range scans at the two smallest value sizes (1KB and 4KB), and at 1MB values it is not stall-free. The numbers are from 2021 (RocksDB \~6.18.1) and may not reflect current defaults.

Blob files add space amplification and require separate blob garbage collection; best suited to workloads with large values (key-value separation); overhead is not worthwhile for small values.

## Maintenance

Actively developed inside RocksDB: HISTORY.md shows 11.11.0 on 2026-09-21 with blob and wide-column work, and blob direct write and FIFO KV-ratio compaction landed in 2026. It is in production use and dual-licensed Apache-2.0/GPLv2, but you adopt it as a RocksDB configuration, not as a component you can vendor on its own.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** RocksDB's own engineering blog post (May 26, 2021) compares integrated BlobDB with leveled and universal compaction without blob files, and with legacy BlobDB. It states the CPU (18-core Skylake DE @ 1.6 GHz) and RocksDB version (\~6.18.1), but the benchmark is described only as 'a customized version of our standard benchmark suite', with no command lines, compiler or flags. First-party with partial methodology, so tier C.
- **Verifier notes:** Every number in claimed_speedup appears verbatim on the blog post: 2.3x-4.7x initial load, 1.0-1.02 vs 1.6 write amp, 2.1x-3.5x overwrite throughput, 75-78%/83-88%/88-90% write-amp cuts, up to 1.4x/5.6x reads, and 4.6x/2.3x vs legacy BlobDB. The page says 'M.2 SSDs', not NVMe, so I fixed the hardware field. repo_url facebook/rocksdb is also the known-list RocksDB entry, so the orchestrator may want to dedupe it as a feature-of-RocksDB record. The license was verified from the README (dual GPLv2 / Apache 2.0), even though GitHub's spdx_id reports only GPL-2.0.
- **Fields the verifier corrected:** `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** BVLSM paper (2025, competitor authors, RocksDB 9.7.3): \~4x vs stock RocksDB on 64 KB random writes but only \~0.4-0.6x on sequential writes, and below stock on sustained 4 KB random writes.
- **Pages the verifier opened:**
  - <http://rocksdb.org/blog/2021/05/26/integrated-blob-db.html>
  - <https://github.com/facebook/rocksdb>
- **Sources the enricher read:**
  - <http://rocksdb.org/blog/2021/05/26/integrated-blob-db.html>
  - <https://github.com/facebook/rocksdb/wiki/BlobDB>
  - <https://github.com/facebook/rocksdb>
  - <https://github.com/facebook/rocksdb/blob/main/include/rocksdb/advanced_options.h>
  - <https://github.com/facebook/rocksdb/blob/main/INSTALL.md>
  - <https://github.com/facebook/rocksdb/blob/main/HISTORY.md>
  - <https://github.com/facebook/rocksdb/blob/main/db/blob/blob_index.h>
  - <https://github.com/facebook/rocksdb/blob/main/db/blob/blob_file_builder.cc>
  - <https://github.com/facebook/rocksdb/blob/main/db/compaction/compaction_iterator.cc>
  - <https://github.com/facebook/rocksdb/wiki/Basic-Operations>
  - <https://github.com/facebook/rocksdb/releases>
  - <http://rocksdb.org/blog/2026/06/20/blob-direct-write-partitioned-blob-files.html>
  - <http://rocksdb.org/blog/2026/06/20/fifo-kv-ratio-compaction.html>
  - <https://github.com/facebook/rocksdb/issues/13884>
  - <https://github.com/facebook/rocksdb/issues/15256>
  - <https://github.com/facebook/rocksdb/issues/15247>
  - <https://github.com/facebook/rocksdb/issues/14897>
  - <https://github.com/facebook/rocksdb/issues/11570>
  - <https://github.com/facebook/rocksdb/issues/12208>
  - <https://github.com/facebook/rocksdb/issues/8535>
  - <https://github.com/facebook/rocksdb/issues/13090>
  - <https://github.com/facebook/rocksdb/issues/12503>
  - <https://github.com/facebook/rocksdb/issues/13590>
  - <https://arxiv.org/abs/2506.04678>
  - <https://arxiv.org/pdf/2506.04678v2>
  - <https://hn.algolia.com/api/v1/search?query=integrated%20blobdb>
  - <https://export.arxiv.org/api/query?search_query=abs:%22key-value%20separation%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:rocksdb-integrated-blobdb`) · [data/wave6/enrich/raw/paper_rocksdb_integrated_blobdb.json](../../../data/wave6/enrich/raw/paper_rocksdb_integrated_blobdb.json) (enrichment confidence 0.8)

</details>
