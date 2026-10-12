# MatrixKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0 OR Apache-2.0` · 🔴 abandoned

> RocksDB 5.18 fork that moves L0 into Optane persistent memory with fine-grained column compaction; 3.6x NVM-assisted RocksDB random-write throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Abstract: 3.6x higher random-write throughput and 5x lower 99th-percentile latency than RocksDB (2.6x / 1.9x vs NoveLSM). Paper body: random-write throughput (db_bench, 80GB, 4KB values) is 3.6x RocksDB-L0-NVM (RocksDB with an 8GB L0 in NVM; 1.86x-3.61x across 64B-64KB values) and 2.6x NoveLSM; YCSB load 3.29x RocksDB-L0-NVM. YCSB-A p99 latency (Table 2: 405us vs 786/2080/11055us) is 1.9x lower than RocksDB-L0-NVM, 5x lower than NoveLSM, and 27x lower than stock RocksDB-SSD, so the abstract's latency pairing is swapped relative to the body. |
| **Workload** | db_bench micro-benchmarks: 80GB of KV pairs (16B keys, 4KB default values, 64B-64KB sweep) inserted in uniform random order, then sequential writes and random/sequential reads; YCSB load plus workloads A-F (80GB load, 1M ops each); tail latency from YCSB-A at \~20K req/s. Each hybrid store limited to 8GB NVM, with RocksDB defaults (64MB memtable, 256MB L1, AF 10). |
| **Metric** | throughput |
| **Hardware** | Two Intel 2.20GHz 24-core processors (model not named), 32GB DRAM, 800GB Intel SSDSC2BB800G7 SSD, 2x128GB Intel Optane DC PMM (8GB NVM used per store); Fedora 27, Linux 4.13.9 |
| **Adoption** | 76 stars |
| **Last commit** | 2020-08-07 |
| **Links** | [repository](https://github.com/PDS-Lab/MatrixKV) · [benchmark](https://www.usenix.org/system/files/atc20-yao.pdf) |

## Verdict

In the USENIX ATC'20 paper's db_bench test (80 GB of 16 B-key / 4 KB-value inserts in uniform random order, RocksDB defaults, 8 GB of NVM per store), MatrixKV reached 3.6x the random-write throughput of RocksDB with an 8 GB L0 placed in Optane (1.86-3.61x across 64 B-64 KB values) and 2.6x NoveLSM, and 3.29x on YCSB load. YCSB-A p99 at about 20K req/s was 405 us, against 786 us for RocksDB-L0-NVM, 2,080 us for NoveLSM and 11,055 us for stock RocksDB on SSD, and SSD write amplification was 3.43x versus 8.78x for stock RocksDB. Hardware: two unnamed 24-core 2.2 GHz Intel CPUs, 32 GB DRAM, an Intel SSDSC2BB800G7 SSD and Optane DC PMM on Fedora 27 / Linux 4.13.9; compiler, flags and client thread count are not stated.

## Use it when

- Sustained random-insert or update-heavy workloads (bulk load, YCSB load/A/F-like) where RocksDB's L0-L1 compaction stalls cause throughput troughs and p99/p99.9 spikes.
- You already have Optane DC PMM (or equivalent byte-addressable persistent memory mounted for PMDK), several GB of it free, and a comparatively slow SSD for the lower levels (the paper's SSD managed 68 MB/s for 4 KB random writes).
- Any value size from 64 B to 64 KB, since the paper's random-write gain over RocksDB with L0 on NVM was 1.86-3.61x across that whole range (3.6x at 4 KB).
- Research or prototyping: reproducing the ATC'20 results, or as a reference design for column compaction and cross-row L0 search when adding a persistent-memory tier to an LSM engine.

## Skip it when

- Machines without persistent memory. Intel wound down Optane in July 2022, so new deployments need other hardware, and pmem_map_file's msync fallback on an ordinary file is not the configuration that was measured.
- Read- or scan-dominated workloads. In the paper, random and sequential reads roughly matched RocksDB and YCSB B-E were only 'adequate'. An open issue (#3) reports high read latency under YCSB-C++.
- Sequential-insert workloads. In the paper, stock RocksDB on SSD beat every NVM variant, MatrixKV included, on sequential writes.
- Production systems. The code is frozen at RocksDB 5.18.3 with none of RocksDB's later fixes. Issues about NVM overuse and a crash when freed L0 space was not reclaimed (#2) have had no answer since 2021, and debug logging is compiled in.
- Many column families on a small NVM device, because each named column family maps its own pool file sized from the L0 stop threshold.

## How it is fast

Flushed MemTables are written to NVM as sorted 'RowTables' in a matrix container. When the receiver half fills up it becomes the compactor, and its data is merged into L1 by column compaction: one small key range at a time, taken across all RowTables and matched with the overlapping L1 SSTables, rather than all of L0 against all of L1. In the paper this meant 467 compactions of about 0.33 GB each, versus RocksDB's 52 compactions averaging 3.1 GB. Because a column's cost does not grow with level width, L1 is widened to 8 GB, which flattens the tree from 5 levels to 3 and lowers write amplification. Cross-row hint search stores a forward pointer from each key into the previous RowTable, in the style of fractional cascading, so point lookups in the large unsorted L0 need no Bloom filters.

## Compared with alternatives

Pick MatrixKV only when you have Optane-class persistent memory and the problem is RocksDB write stalls and tail latency under random inserts. It is the only sibling built for a DRAM/NVM/SSD hierarchy, and in the paper's all-NVM comparison it led while PebblesDB gained little over RocksDB. On plain SSDs, SplinterDB, KVell or PebblesDB are the write-throughput alternatives, and Titan is the maintained plug-in choice if your problem is large values.

## Integration

| | |
|---|---|
| **Form** | static lib (the whole RocksDB v5.18.3 tree plus utilities/nvm_mod, built with the Makefile; the README says CMake is not supported) |
| **Dependencies** | PMDK libpmem (Makefile links -lpmem), pthread; RocksDB's usual optional compression libraries (snappy, lz4, zstd) if present |
| **Minimum toolchain** | C++11 (build_detect_platform and the Makefile force -std=c++11); the paper used Fedora 27 / Linux 4.13.9; the compiler version is not documented |
| **Platforms** | Linux with PMDK and a DAX-mounted persistent-memory path (tested on x86-64 with Optane DC PMM); other platforms not documented |
| **Thread safety** | Follows RocksDB 5.18's DB-handle model. MatrixKV's NVM flush jobs assert the DB mutex is held, and sstable_meta.h notes that its compaction file list is used by only one thread; nothing further is documented. Neither the paper nor the issues state the benchmark thread count (issue #4), and the shipped db_bench script uses threads=1. |
| **Drop-in for the baseline** | partial: same RocksDB 5.18 C++ API and db_bench, but you must replace your RocksDB build with this fork (it is not a plugin), give up every RocksDB feature and fix after 5.18.3, and configure nvm_setup plus a pmem path; L0 data lives in a pool file outside the DB directory |

## Gotchas

- NVM footprint is much larger than the 8 GB L0 budget. Master pre-allocates (L0_stop_size / write_buffer_size + 1) \* 2 slots of write_buffer_size + 8 MB each, about 18.6 GB with the defaults (8 GB stop, 64 MB memtables), which fits issue #2's report of nearly 20 GB. The page-granular space management described in the paper exists only on the unmerged MatrixKV-Pager branch, which uses 256 KB pages rather than 4 KB.
- The paper's full speedup depends on also flattening the tree. The shipped script sets max_bytes_for_level_base to 8 GB; with RocksDB's default 256 MB L1 you get only the write-stall reduction, and the paper reports 25% more throughput with the 8 GB L1. L0 thresholds are byte sizes (7 GB trigger, 7.5 GB slowdown, 8 GB stop by default) instead of RocksDB's file counts.
- Recovery is fragile. If the pmem pool file is missing while the manifest still lists L0 files, RecoverFromStorageInfo prints 'can't recover' and carries on. It also copies each L0 table's key metadata into a stack variable-length array, which could overflow the thread stack for small-value tables. A RowTable flush returns IOError if its data plus about 52 bytes of metadata per key (with 16 B keys) exceeds its fixed slot.
- Debug logging is hard-wired: my_log.h defines LZW_DEBUG and LZW_INFO, so the library appends to NVM_LOG in the working directory, opening and closing the file for every line, on each L0 table add or delete and each column-compaction pick. The paper says the WAL lives on NVM, but the shipped script puts --wal_dir on the SSD, and utilities/nvm_mod contains no WAL code.

## Known shortcomings

- Needs Optane-class persistent memory, which Intel wound down in 2022; frozen at RocksDB 5.18.3, not a plugin. Uses \~18.6 GB of NVM, not 8 GB (master preallocates 2x slots; issue #2 reports \~20 GB plus a crash when freed L0 space isn't reclaimed, unanswered); the paper's 4 KB paging exists only on an unmerged branch with 256 KB pages. Speedup is write-only: reads roughly equal RocksDB, sequential writes lose to stock RocksDB on SSD, full gain needs an 8 GB L1. Fragile recovery (a missing pmem pool only prints and continues). Debug logging always on in the working directory; the shipped script puts the WAL on SSD (paper: NVM) and uses threads=1; the paper gives no compiler, flags, CPU model or thread count (#4).

## Caveats and trade-offs

Code is a diff against RocksDB v5.18.3 (the README gives the RocksDB commit to reset against); it is not a GitHub fork. The main RocksDB baseline in the paper is RocksDB-L0-NVM, i.e. RocksDB given the same 8GB NVM for L0; stock RocksDB-SSD is slower still. The abstract's 5x/1.9x p99 figures are paired with the wrong baselines relative to Table 2. Reads and sequential writes are roughly equal to RocksDB, not faster. No compiler, flags or CPU model given. Needs Optane DC PMM and PMDK. License: GitHub detects GPL-2.0, but the repo keeps RocksDB's COPYING (GPLv2) and LICENSE.Apache, and RocksDB-derived files carry dual GPLv2/Apache-2.0 headers; MatrixKV-added files (e.g. include/rocksdb/nvm_option.h) have no header. Unmaintained since 2020.

Requires Intel Optane/PMDK-class NVM hardware to realize the reported gains; not a plain-SSD design.

## Maintenance

Abandoned since August 2020 (3 open issues with no maintainer replies) and tied to discontinued Optane hardware. The code inherits RocksDB's GPLv2 / Apache-2.0 dual license and is best treated as a vendorable research reference for its column-compaction and L0-search design, not as a production engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC'20 paper measures MatrixKV against RocksDB (RocksDB-SSD and RocksDB-L0-NVM) with db_bench and YCSB. The repo ships db_bench scripts (test_sh/). Not A: the CPU is only 'two Genuine Intel(R) 2.20GHz 24-core processors' with no model, and no compiler or flags are stated.
- **Verifier notes:** The record faithfully reflects the USENIX abstract, but the body shows 3.6x is against RocksDB-L0-NVM and the p99 multipliers are swapped (1.9x vs RocksDB-L0-NVM, 27x vs stock RocksDB). I corrected the claim and pointed benchmark_url at the full paper PDF. Metadata verified: 76 stars, not a fork, not archived, last commit on every branch 2020-08-07 (abandoned). License corrected to RocksDB's dual license.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/atc20/presentation/yao>
  - <https://www.usenix.org/system/files/atc20-yao.pdf>
  - <https://github.com/PDS-Lab/MatrixKV>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/README.md>
  - <https://raw.githubusercontent.com/PDS-Lab/MatrixKV/master/db/db_impl.cc>
  - <https://raw.githubusercontent.com/PDS-Lab/MatrixKV/master/include/rocksdb/nvm_option.h>
  - <https://raw.githubusercontent.com/PDS-Lab/MatrixKV/master/test_sh/rocksdb_test.sh>
- **Sources the enricher read:**
  - <https://github.com/PDS-Lab/MatrixKV>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/README.md>
  - <https://github.com/PDS-Lab/MatrixKV/issues/2>
  - <https://github.com/PDS-Lab/MatrixKV/issues/3>
  - <https://github.com/PDS-Lab/MatrixKV/issues/4>
  - <https://github.com/PDS-Lab/MatrixKV/pull/1>
  - <https://github.com/PDS-Lab/MatrixKV/compare/master...MatrixKV-Pager>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/include/rocksdb/nvm_option.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/include/rocksdb/options.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/persistent_sstable.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/nvm_cf_mod.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/nvm_cf_mod.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/l0_table_builder.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/sstable_meta.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/nvm_option.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/nvm_flush_job.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/my_log.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/my_log.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/utilities/nvm_mod/common.h>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/db/column_family.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/db/db_impl_open.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/tools/db_bench_tool.cc>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/Makefile>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/build_tools/build_detect_platform>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/src.mk>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/test_sh/matrixkv_test_4value.sh>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/test_sh/fedora_recover.sh>
  - <https://github.com/PDS-Lab/MatrixKV/blob/master/test_sh/rocksdb_test.sh>
  - <https://raw.githubusercontent.com/PDS-Lab/MatrixKV/MatrixKV-Pager/utilities/nvm_mod/nvm_pager.h>
  - <https://www.usenix.org/system/files/atc20-yao.pdf>
  - <https://en.wikipedia.org/wiki/3D_XPoint>
  - <https://hn.algolia.com/api/v1/search?query=MatrixKV>
  - <http://export.arxiv.org/api/query?search_query=all:MatrixKV>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/pds-lab/matrixkv`) · [data/wave6/enrich/raw/github_com_pds_lab_matrixkv.json](../../../data/wave6/enrich/raw/github_com_pds_lab_matrixkv.json) (enrichment confidence 0.8)

</details>
