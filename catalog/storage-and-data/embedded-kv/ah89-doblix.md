# DobLIX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause (RocksDB 5.x-era 'BSD License For rocksdb software' LICENSE text; GitHub reports NOASSERTION) plus Facebook PATENTS file (Additional Grant of Patent Rights Version 2)` · 🟡 stale

> Research RocksDB fork replacing the SST index with a block-aware learned string index; paper: 2.21x read-only throughput vs RocksDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Average throughput vs stock RocksDB indexing: 2.21x on read-only (RO), 1.22x read-heavy, 1.31x balanced, 1.04x write-heavy; vs TridentKV/Bourbon on RO: 1.41x/1.57x. YCSB B/C/D average 2.02x vs RocksDB; YCSB-E +42.8%. +81% vs RocksDB at 512MB cache (RO, Zipfian, AMZN). RO tail latency 2.13x better than RocksDB. Abstract: 1.19x-2.21x vs state-of-the-art methods within RocksDB. The '2.67x' figure is TridentKV's tail latency relative to DobLIX, not a throughput gain over RocksDB. |
| **Workload** | SOSD real-world (WIKI, AMZN, FB, OSM) and synthetic (LOGN, UNI) datasets, 64M pairs with 8-byte keys and 64-byte values; RO/RH/BA/WH read-write mixes plus YCSB A-F macrobenchmarks on RocksDB 8.1.1 (per paper), 4 background threads |
| **Metric** | throughput |
| **Hardware** | 64-core AMD Ryzen Threadripter Pro 5995WX (2.7GHz), 256GB DDR4 RAM, Samsung 980 Pro 2TB NVMe SSD, Ubuntu 20.04 |
| **Compiler and flags** | C++17, GCC 9.4.0 (paper); optimization flags not stated in paper (repo README uses cmake -DCMAKE_BUILD_TYPE=Release; repo CMakeLists sets -std=c++11) |
| **Adoption** | 8 stars |
| **Last commit** | 2025-09-17 |
| **Links** | [repository](https://github.com/ah89/DobLIX) · [benchmark](<https://arxiv.org/abs/2502.05369 (PVLDB 18(11): 3965-3978, 2025, DOI 10.14778/3749646.3749667)>) |

## Verdict

The PVLDB 2025 paper ran RocksDB 8.1.1 built with GCC 9.4.0 (C++17, flags not stated) and 4 background threads on a 64-core Threadripper Pro 5995WX with 256GB RAM and a Samsung 980 Pro NVMe, using SOSD datasets (64M 8-byte keys, 64-byte values) and 10M-operation Zipfian workloads; against RocksDB's default index it averaged 2.21x throughput on RO, 1.22x RH, 1.31x BA, 1.04x WH, 2.02x on YCSB B/C/D and +42.8% on YCSB-E. These numbers come from the unreleased paper build with the tuner and RocksDB 8.1.1, not the public repo.

## Use it when

- Studying or prototyping learned indexes inside an LSM SST. learned_index/ is a compact header-only RadixSpline and Radix String Spline already wired into RocksDB's table builder and reader.
- Read-only or read-mostly point-lookup workloads on small fixed-size keys where index lookup plus block load dominate Get latency. The paper reports 2.21x average RO throughput and 2.02x on YCSB B/C/D vs RocksDB's default index.
- Read workloads with a larger block cache. The paper measured +81% over RocksDB at 512MB cache (RO, Zipfian, AMZN), where index cost is a larger share of each lookup.
- Long string keys with shared prefixes. Prefix stripping per trie node gave a 25.9% smaller index at 64-byte keys and 1.32x-1.62x throughput on variable-size KV mixes modeled on UDB, ZippyDB and UP2X.
- Only as a starting point you will port to a current RocksDB and complete yourself (the PRA model and RL tuner are missing).

## Skip it when

- Production use. The base is RocksDB 5.1.2, years behind current releases in fixes and features. The authors state in issue #2 that the public code is not the version used in the paper.
- Write-heavy workloads. The paper's own WH gain over RocksDB is only 1.04x, and the builder buffers each whole SST in RAM before writing it (see gotchas).
- Range-scan-heavy workloads. Iterators still use the regular binary-search index block. The paper's YCSB-E gain is 42.8%, and it notes all systems perform alike during the scan phase.
- Existing RocksDB databases. The SST footer gains a third block handle and Get() always goes through the learned index. Reading SSTs written by stock RocksDB, and migrating them, is not documented.
- Expecting workload-adaptive tuning. The RL tuner and PRA model are withheld, and the public builder hardcodes error bound 128 and a 4KB max block.

## How it is fast

The index is a Radix String Spline: a trie of RadixSpline models, each built with Neumann and Michel's GreedySplineCorridor PLA over 8-byte big-endian key chunks, with common prefixes stripped at each node. The 'dual objective' is that a spline segment is also cut when its bytes would exceed a max block size. Each spline segment then becomes its own data block, so the model predicts the block directly and a Get reads one small block instead of searching an index block and then a possibly large data block. The paper also adds a Q-learning agent that picks PLA or piecewise regression (PRA), the error bound and the max block size, plus model-guided last-mile search inside the block, but none of these three are in the public code.

## Compared with alternatives

Pick DobLIX over write-focused siblings (PebblesDB, MatrixKV, Titan) only when the bottleneck is point-lookup index and block reads in a read-mostly RocksDB workload and you want to study learned SST indexes. For anything deployable, Titan is a maintained RocksDB plugin, and SplinterDB claims 2-2.6x faster point queries plus 6-10x faster inserts in a maintained codebase.

## Integration

| | |
|---|---|
| **Form** | static lib (the whole RocksDB 5.1.2 fork, built with CMake or Make; not a plugin or separable patch) |
| **Dependencies** | RocksDB 5.1.2 build deps per README: gflags, snappy, zlib, bzip2, lz4, zstd. No ML/RL libraries, since the tuner is not included. |
| **Minimum toolchain** | CMakeLists sets -std=c++11. The paper used C++17 with GCC 9.4.0. Issue #1 reports the README build failing and was closed without a reply. |
| **Platforms** | Paper tested Linux x86-64 (Ubuntu 20.04). learned_index/ uses GCC/Clang builtins (__builtin_clz/__builtin_clzl), so MSVC is not supported as written. Other platforms are not documented. |
| **Thread safety** | Inherits RocksDB's model (the DB handle is thread-safe). The per-SST model is built once in the table builder and only read after the table opens. Nothing DobLIX-specific is documented. |
| **Drop-in for the baseline** | partial — same RocksDB C++ API, but it is a RocksDB 5.1.2 fork with a modified SST footer and an always-on learned-index Get path, not a patch or plugin for current RocksDB (the paper used 8.1.1) |

## Gotchas

- BlockBasedTableBuilder::Add copies every key and value of the output SST into a std::vector&lt;pair&lt;string,string&gt;&gt;, plus another copy of each user key for training. Data blocks are only written in Finish(), so flush/compaction memory grows with SST size.
- Data-block boundaries come from spline segments via a hardcoded FinalizeRSSModel(128, 4\*1024), not from BlockBasedTableOptions::block_size. The only tuning is editing and recompiling.
- The paper's last-mile optimizations are inactive in the public reader. GetKeyFromBlock computes a model search bound and prefix length, then ignores both and calls the standard BlockIter::Seek. The table-open loop that fills per-block key counts also never increments block_num, so those counts are wrong; this is harmless today only because nothing uses them.
- Every RadixStringSplineNode constructor calls srand(time(NULL)), which reseeds the process-global C RNG on each SST build. The table reader also frees a new char[] buffer through std::unique_ptr&lt;char&gt;, a mismatched delete.

## Known shortcomings

- The repo is a RocksDB 5.1.2 tree while the paper says 8.1.1, and it has no DobLIX benchmark harness. The listed 2.67x is TridentKV tail latency; against RocksDB it is 2.21x read-only and 1.04-1.31x on mixed workloads. BSD-3 plus Facebook's PATENTS file.
- The public repo is not the paper's build: the authors say (issue #2) the tuner and PRA were withheld for confidentiality. It is a RocksDB 5.1.2 fork with a changed SST footer and Get() always going through the learned index, so it is no drop-in for modern RocksDB. Error bound 128 and 4 KB blocks are hard-coded; the paper's last-mile/prefix optimisations are computed but unused.
- The builder copies the whole SST into RAM before Finish; srand() reseeds the global RNG; mismatched delete[] in the reader; the README build is reported broken (issue #1, no reply). Gains: 2.21x read-only but 1.04x write-heavy and only +42.8% on YCSB-E (scans use the normal index).

## Caveats and trade-offs

GitHub shows NOASSERTION. The LICENSE is RocksDB's old BSD-3-Clause text, shipped with Facebook's PATENTS grant (v2) and its termination clause. The public repo is a RocksDB 5.1.2 tree (include/rocksdb/version.h) with a learned_index/ directory, but the paper evaluates on RocksDB 8.1.1. It has no DobLIX-specific SOSD/YCSB benchmark scripts, and the README's './doblix' binary has no matching CMake target. Several headline ratios (1.19x, 1.41x, 1.57x) are vs other learned-index variants (Bourbon, TridentKV). The direct stock-RocksDB gains are large on read-only work (2.21x) but only 1.04x-1.31x on write-containing mixes.

Adds a dual-objective learned index (RadixSpline-based) plus an RL agent for tuning block size/error bound on top of RocksDB; extra training/tuning overhead; RL agent adds runtime complexity vs stock RocksDB.

## Maintenance

Stale research code drop (one code commit in Feb 2025, README edits to Sep 2025) whose Huawei authors say the tuner and PRA are withheld for confidentiality; it is BSD-3 with Facebook's old PATENTS grant, so read or copy learned_index/ but do not deploy it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 18(11):3965-3978 paper that states GCC 9.4.0, C++17 and the Threadripper Pro 5995WX, but it gives no optimization flags. The public repo contains no DobLIX benchmark harness (only stock RocksDB tools) and is a RocksDB 5.1.2 tree, while the paper says RocksDB 8.1.1, so it cannot be A.
- **Verifier notes:** The paper is real, peer-reviewed and compares directly against stock RocksDB, so the 2.21x and 81% figures check out. The '2.67x throughput' claim was a misreading of a tail-latency comparison vs TridentKV. The tier drops from A to B: no flags are stated, and the public code does not match the RocksDB version the paper evaluated.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2502.05369>
  - <https://github.com/ah89/DobLIX>
- **Sources the enricher read:**
  - <https://github.com/ah89/DobLIX>
  - <https://github.com/ah89/DobLIX/blob/main/README.md>
  - <https://github.com/ah89/DobLIX/tree/main/learned_index>
  - <https://github.com/ah89/DobLIX/blob/main/learned_index/rss.h>
  - <https://github.com/ah89/DobLIX/blob/main/learned_index/builder.h>
  - <https://github.com/ah89/DobLIX/blob/main/learned_index/radix_spline.h>
  - <https://github.com/ah89/DobLIX/blob/main/learned_index/string_serializer.h>
  - <https://github.com/ah89/DobLIX/blob/main/table/block_based_table_builder.cc>
  - <https://github.com/ah89/DobLIX/blob/main/table/block_based_table_reader.cc>
  - <https://github.com/ah89/DobLIX/blob/main/table/block_based_table_reader.h>
  - <https://github.com/ah89/DobLIX/blob/main/table/format.cc>
  - <https://github.com/ah89/DobLIX/blob/main/table/format.h>
  - <https://github.com/ah89/DobLIX/blob/main/include/rocksdb/version.h>
  - <https://github.com/ah89/DobLIX/blob/main/include/rocksdb/table.h>
  - <https://github.com/ah89/DobLIX/blob/main/CMakeLists.txt>
  - <https://github.com/ah89/DobLIX/issues/1>
  - <https://github.com/ah89/DobLIX/issues/2>
  - <https://arxiv.org/pdf/2502.05369>
  - <https://api.crossref.org/works/10.14778/3749646.3749667>
  - <https://hn.algolia.com/api/v1/search?query=DobLIX>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ah89/doblix`) · [data/wave6/enrich/raw/github_com_ah89_doblix.json](../../../data/wave6/enrich/raw/github_com_ah89_doblix.json) (enrichment confidence 0.85)

</details>
