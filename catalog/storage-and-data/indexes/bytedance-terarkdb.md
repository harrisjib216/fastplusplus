# TerarkDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> ByteDance's RocksDB 5.18 fork with no-writeback key-value separation and lazy compaction; \~1.7x db_bench QPS vs RocksDB 6.12.

| | |
|---|---|
| **Beats** | RocksDB v6.12 (TerarkDB is a fork/drop-in replacement of RocksDB v5.18.3) |
| **Claimed result** | README table image compare_rocksdb.png (db_bench, TerarkDB vs RocksDB v6.12): QPS heavy_read 695.2K vs 398.1K (\~1.75x), heavy_write 215.6K vs 127.1K (\~1.70x), fillrandom 204.4K vs 118.8K (\~1.72x), fillseq 215.7K vs 208.4K (\~1.04x) (ratios derived from page data); P99 read latency heavy_write 73.10us vs 573.68us, P99 write latency heavy_write 75.81us vs 1,029.90us |
| **Workload** | db_bench with 10 client threads, 20GB requests/thread, 24-byte keys and 2000-byte values; 'heavy_read' (90% read), 'heavy_write' (90% write), fillrandom and fillseq. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon Gold 5218 CPU @ 2.30GHz (32 cores/64 threads), 376GB DRAM, NVMe TLC SSD (3.5TB) |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-05-31 |
| **Links** | [repository](https://github.com/bytedance/terarkdb) · [benchmark](https://github.com/bytedance/terarkdb#performance-overview) |

## Verdict

The vendor's db_bench table compares TerarkDB with RocksDB v6.12 on a 2-socket Xeon Gold 5218 (32 cores/64 threads) with 376 GB DRAM and a 3.5 TB NVMe TLC SSD, using 10 threads x 20 GB, 24-byte keys and 2000-byte values. It shows about 1.7x QPS on heavy_read, heavy_write and fillrandom and 1.04x on fillseq, with P99 write latency on heavy_write of 75.8 us vs 1,029.9 us. The numbers exist only as a PNG. The repo's bench.py matches this workload and runs TerarkDB with separation at blob_size=128, TerarkZipTable off, no compression and sync=1, but the RocksDB-side options and the compiler and flags are not stated.

## Use it when

- Write-heavy or mixed read/write workloads with values of roughly 0.5 KB and up (the published benchmark uses 2000-byte values), where RocksDB compaction write amplification and write stalls limit throughput.
- Online services on Linux with NVMe SSDs that care about P99 latency: the vendor table shows heavy_write P99 write latency of 75.8 us vs 1,029.9 us on RocksDB 6.12.
- Update-heavy workloads where the index write-back done by value GC in Titan or BlobDB hurts foreground writes.
- Existing C++ code written against the RocksDB 5.x API that you can move one-way and then keep on a pinned fork.
- Experiments on zoned (ZNS) SSDs through the bundled ZenFS option (WITH_ZNS, marked experimental).

## Skip it when

- Small values, or key-value separation left off: the gain comes mostly from separation. An independent continuous benchmark (benchplus, issue #177) found results roughly equal to RocksDB except full iteration, and the vendor's own fillseq gain is only 1.04x.
- Disk-space-constrained deployments: the Scavenger paper measured key-value-separated engines, TerarkDB included, using 2.42x-2.97x more space than RocksDB on an 8 KB update workload.
- You need RocksDB APIs, fixes or features added after v5.18.3; the fork only back-ports selected upstream fixes.
- macOS, Windows or non-x86 targets: the README says only Linux is tested and production-ready, macOS builds have been reported broken (#26, #163), and aarch64 is not documented.
- You need an actively developed engine: the last functional code change was mid-2023, the terark-zip core-algorithm submodule is archived, and issues about failing unit tests, broken CI and an Ubuntu 22.04 build error remain open.

## How it is fast

Values at or above `blob_size` (default 512 B) are split into sorted value SSTs while the key LSM stores (key, value-file number), a WiscKey-style key-value separation that removes most compaction write amplification for large values. Its value GC does not write new addresses back into the key index; it records an inheritance chain from each new value file to the files it replaced, so GC does not slow foreground writes (the ICDE 2024 Scavenger paper calls this a 'no-writeback GC strategy'). Optional lazy compaction writes 'map SSTs' that reference key ranges of existing files so rewrites can wait until after write bursts. The maintainers also credit moving work out of the DB mutex and pre-created, pipelined WAL files, and TerarkZipTable adds a succinct Nested LOUDS Trie index with global-dictionary compression.

## Compared with alternatives

Pick TerarkDB over Titan when you want a full engine whose value GC never rewrites the key index (the Scavenger paper puts Titan's index write-back at about 38% of its GC cost) plus lazy compaction, and you accept a Linux-only fork pinned at RocksDB 5.18. Pick Titan to keep key-value separation as a plugin on top of RocksDB instead of replacing the engine.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_subdirectory, or build.sh producing libterarkdb.a plus separate dependency .a files that you must link yourself) |
| **Dependencies** | Git submodules zstd, zlib, snappy, lz4, bzip2, jemalloc (on by default) and gflags; libaio, boost and terark-zip when WITH_TERARK_ZIP=ON; ZenFS/libzbd when WITH_ZNS=ON; links pthread, gomp, rt, dl and aio |
| **Minimum toolchain** | C++14 (-std=c++14), CMake 3.4+; minimum GCC/Clang version not documented |
| **Platforms** | Linux x86-64 is the only tested platform; default build uses -march=native (PORTABLE=ON uses -march=haswell), and SSE4.2/PCLMUL are used for CRC32C when available; macOS builds reported broken; aarch64 not documented |
| **Thread safety** | Inherits RocksDB's model of one shared DB handle used by many threads (the benchmarks run 10-16 client threads with concurrent memtable writes); no TerarkDB-specific guarantees are documented, and a PatriciaTrie memtable crash under concurrent writes was fixed in v1.4.0 |
| **Drop-in for the baseline** | partial — it uses the same rocksdb/\*.h headers and core DB API as RocksDB 5.18.3, but symbols default to namespace terarkdb (set -DWITH_TERARKDB_NAMESPACE=rocksdb or add an alias), PinnableSlice and BlobDB are gone, code using MergeOperator or CompactionFilter may need edits, and data migration from RocksDB is one-way |

## Gotchas

- Defaults disagree: Options::blob_size defaults to 512 (separation on), but db_bench defaults blob_size to size_t(-1) (off). The repo's bench.py passes --blob_size=128, so a benchmark that skips this flag measures a different engine configuration.
- The README code samples use rocksdb::, but the CMake default namespace is terarkdb, and examples/simple_example.cc still uses the removed PinnableSlice (#268). Neither compiles out of the box.
- Value files rewritten by GC are found through the inheritance chain, which adds lookups. In a maintainer's 1-hour readrandomwriterandom run, 7.5% of value reads hit an outdated file number, and after 10 hours 99% of value-file references in key SSTs were outdated (#199).
- TerarkZipTable needs a separate localTempDir, libaio and boost, and the README advises starting with it off. CMakeLists.txt defaults WITH_TERARK_ZIP=ON while build.sh sets it OFF, and hugepage warnings are reported in db_bench (#236).

## Known shortcomings

- Maintenance only: last functional change 2023-06; the terark-zip submodule was archived in 2022; failing tests (#194-196), broken CI (#83), Ubuntu 22.04 build error (#260). The bench config likely favours TerarkDB (key-value separation at blob_size=128, sync=1, no compression; RocksDB options not given). A third-party benchplus run (#177) found it about equal to RocksDB without separation; the Scavenger paper (ICDE'24) measured key-value-separated engines including TerarkDB at 2.42-2.97x RocksDB's space. Not a drop-in (namespace terarkdb; README samples don't compile; PinnableSlice removed, #268); migration from RocksDB is one-way. Linux x86-64 only.

## Caveats and trade-offs

TerarkDB is itself forked from RocksDB v5.18.3 but benchmarked against a newer RocksDB v6.12 (different vintages); results appear only as a table image (compare_rocksdb.png), not in text; exact db_bench command lines, engine options (e.g. whether TerarkZipTable was enabled), compiler and flags are unstated; fillseq gain is only \~1.04x. Latest default-branch commit (2026-05-31) is a README update; last code change 2025-08-25.

Linux-only / production-ready claim is Linux-specific; non-C/C++ language bindings not fully tested; migration back to plain RocksDB from TerarkDB is not supported; optional TerarkZipTable adds a libaio dependency

## Maintenance

Apache-2.0 and buildable as a static library on Linux, but effectively in maintenance only: 2025-2026 commits touch CI, Java test jars, a 2-line console fix and the README, the last functional change was June 2023, and the bundled terark-zip library was archived in 2022.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Performance Overview' gives first-party db_bench results vs RocksDB v6.12 with CPU/DRAM/SSD stated, but the numbers are only in a table image (docs/images/compare_rocksdb.png) and exact db_bench command lines, engine options, compiler and flags are not given, so it falls short of A.
- **Verifier notes:** The 'graph' is actually a numeric table image; claimed_speedup rewritten with its QPS and P99 figures (ratios marked derived). last_commit corrected from pushed_at (2026-07-13, another branch) to the default branch dev.1.4 head; still active. GitHub does not flag it as a fork, but README says forked from RocksDB v5.18.3, so is_fork_of kept.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytedance/terarkdb>
  - <https://github.com/bytedance/terarkdb#performance-overview>
  - <https://raw.githubusercontent.com/bytedance/terarkdb/dev.1.4/docs/images/compare_rocksdb.png>
- **Sources the enricher read:**
  - <https://github.com/bytedance/terarkdb>
  - <https://github.com/bytedance/terarkdb#performance-overview>
  - <https://raw.githubusercontent.com/bytedance/terarkdb/dev.1.4/docs/images/compare_rocksdb.png>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/CHANGELOG.md>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/CMakeLists.txt>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/build.sh>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/bench.py>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/db_bench_zns.sh>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/.gitmodules>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/options.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/advanced_options.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/db.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/lazy_buffer.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/terark_namespace.h.in>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/include/rocksdb/version.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/db/version_edit.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/db/map_builder.h>
  - <https://github.com/bytedance/terarkdb/blob/dev.1.4/examples/simple_example.cc>
  - <https://github.com/bytedance/terarkdb/commits/dev.1.4>
  - <https://github.com/bytedance/terarkdb/commit/539dcfa6>
  - <https://github.com/bytedance/terarkdb/commit/73321b70>
  - <https://github.com/bytedance/terarkdb/commit/9ee7e1c8>
  - <https://github.com/bytedance/terarkdb/commit/308ef7f6>
  - <https://github.com/bytedance/terarkdb/commit/7257b545>
  - <https://github.com/bytedance/terarkdb/issues>
  - <https://github.com/bytedance/terarkdb/issues/261>
  - <https://github.com/bytedance/terarkdb/issues/260>
  - <https://github.com/bytedance/terarkdb/issues/233>
  - <https://github.com/bytedance/terarkdb/issues/254>
  - <https://github.com/bytedance/terarkdb/issues/270>
  - <https://github.com/bytedance/terarkdb/issues/268>
  - <https://github.com/bytedance/terarkdb/issues/177>
  - <https://github.com/bytedance/terarkdb/issues/163>
  - <https://github.com/bytedance/terarkdb/issues/112>
  - <https://github.com/bytedance/terarkdb/issues/199>
  - <https://github.com/bytedance/terark-zip>
  - <https://github.com/benchplus/terarkdb>
  - <https://export.arxiv.org/api/query?search_query=abs:TerarkDB&max_results=10>
  - <https://arxiv.org/abs/2508.13909>
  - <https://arxiv.org/html/2508.13909v1>
  - <https://arxiv.org/abs/2508.13935>
  - <https://hn.algolia.com/api/v1/search?query=terarkdb&tags=story>
  - <https://news.ycombinator.com/item?id=25514419>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bytedance/terarkdb`) · [data/wave6/enrich/raw/github_com_bytedance_terarkdb.json](../../../data/wave6/enrich/raw/github_com_bytedance_terarkdb.json) (enrichment confidence 0.55)

</details>
