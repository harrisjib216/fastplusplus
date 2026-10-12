# Indexes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md)</sub>

**What these beat:** B-tree/LSM in the above; learned index baselines  
**34 entries:** 3 tier A · 20 tier B · 11 tier C · 0 tier D · 31 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**TidesDB**](tidesdb-tidesdb.md) | Embeddable transactional LSM key-value engine in C; the author's benchmark shows 4-5x RocksDB's iterator-seek throughput at about 3.5x the memory. | **A** | C | MPL-2.0 | 🟢 active |
| 2 | [**indexset**](lucidarium-systems-indexset.md) | Rust two-level B-tree (sorted Vec leaves) with positional indexing; beats std BTreeMap/BTreeSet on scans and Mutex-wrapped std under contention. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 3 | [**Cuckoo Trie**](cuckoo-trie-cuckoo-trie-code.md) | Research C ordered index storing a trie in a cuckoo hash table; faster DRAM-bound lookups than HOT, ARTOLC, STX B-tree. | **A** | C | Unlicense | 🔴 abandoned |
| 4 | [**Bf-Tree**](xiangpenghao-bf-tree-docs.md) | Microsoft Research's larger-than-memory concurrent B-Tree for small records, with record-level caching; beats RocksDB and page-cached B-Trees. | **B** | Rust | MIT | 🟢 active |
| 5 | [**RMI (Recursive Model Index, reference implementation)**](learnedsystems-rmi.md) | Rust generator emitting a C++ two-stage learned index for static sorted arrays; beats STX B+Tree latency and size. | **B** | Rust | MIT | 🟢 active |
| 6 | [**ART Synchronized (Optimistic Lock Coupling / ROWEX for…**](flode-artsynchronized.md) | In-memory concurrent Adaptive Radix Tree (OLC and ROWEX variants); roughly 1.5-3x Masstree's throughput on 8-byte integer keys. | **B** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**PGM-index (Piecewise Geometric Model index)**](gvinciguerra-pgm-index.md) | Header-only learned index over sorted integer arrays that matches B+-tree lookup latency with an index orders of magnitude smaller. | **B** | C++ | Apache-2.0 | 🟡 stale |
| 8 | [**ALEX (Adaptive Learned indEX)**](microsoft-alex.md) | Header-only C++ learned ordered index for numeric keys; beats STX B+Tree up to 4x on in-memory lookups and inserts. | **B** | C++ | MIT | 🟡 stale |
| 9 | [**MyRocks (RocksDB storage engine for MySQL)**](facebook-mysql-5-6.md) | Meta's RocksDB (LSM-tree) storage engine for MySQL: \~4x smaller on disk, \~5x InnoDB's TPC-C tps when cache is tiny. | **B** | C++ | GPL-2.0-only | 🔴 abandoned |
| 10 | [**IBTree (Interpolating B-Tree, SOSD implementation)**](paper-ibtree.md) | Static B-tree using interpolation search inside nodes, from the SOSD benchmark; about 8% faster lookups than STX B+-tree. | **B** | C++ | GPL-3.0 | 🔴 abandoned |
| 11 | [**HOT (Height Optimized Trie)**](speedskater-hot.md) | Header-only C++14 order-preserving trie for in-memory indexes. Beats STX B+-tree, ART and Masstree on string-key lookups, scans and memory. | **B** | C++ | ISC | 🔴 abandoned |
| 12 | [**RadixSpline**](learnedsystems-radixspline.md) | Single-pass, read-only learned index (spline + radix table) for sorted uint32/uint64 arrays; beats STX B+Tree lookups at \~1/40th the size. | **B** | C++ | MIT | 🔴 abandoned |
| 13 | [**FAST+FAIR (Failure-Atomic ShifT + Failure-Atomic In-place…**](dicl-fast-fair.md) | Crash-consistent persistent-memory B+-tree using failure-atomic in-place shifts; range scans 6-33% faster than FP-tree/wB+-tree (emulated PM). | **B** | C++ | GPL-3.0 | 🔴 abandoned |
| 14 | [**Wormhole (fast ordered index)**](wuxb45-wormhole.md) | Concurrent in-memory ordered KV index in C fusing hash table, trie and B+-tree; lookups beat B+-tree, skip list, ART, Masstree. | **B** | C | GPL-3.0 | 🔴 abandoned |
| 15 | [**LIPP (Updatable Learned Index with Precise Positions)**](jiacheng-wu-lipp.md) | Header-only, single-threaded learned index for numeric keys; beats STX B+Tree, ART and ALEX on point-lookup and insert throughput. | **B** | C++ | MIT | 🔴 abandoned |
| 16 | [**DPTree (Differential Indexing for Persistent Memory)**](zxjcarrot-dptree-code.md) | Research persistent-memory index that buffers writes in DRAM; up to 1.82x faster point lookups than FAST+FAIR on Optane. | **B** | C++ | MIT | 🔴 abandoned |
| 17 | [**APEX (learned index on persistent memory)**](baotonglu-apex.md) | Persistent, concurrent learned index for Intel Optane PM; up to 3.8x faster inserts than FAST+FAIR and other PM B+-trees. | **B** | C++ | MIT | 🔴 abandoned |
| 18 | [**Bourbon (learned index for LSM-trees, OSDI'20 artifact)**](edydfang-bourbon.md) | LevelDB/WiscKey-based LSM key-value store that swaps SSTable index search for per-file linear models; 1.23-1.78x faster lookups than WiscKey. | **B** | C++ | BSD-3-Clause | 🔴 abandoned |
| 19 | [**PLEX / TrieSpline**](stoianmihail-plex.md) | Read-only learned index for sorted integer keys: error-bounded spline plus auto-tuned radix tree; \~2x faster lookups than B-tree. | **B** | C++ | MIT | 🔴 abandoned |
| 20 | [**CARMI (Cache-Aware RMI)**](embryo-labs-carmi.md) | Header-only, updatable learned index (a cost-model-built RMI) for numeric keys that beats STX B+ Tree and ALEX on in-memory lookups. | **B** | C++ | MIT | 🔴 abandoned |
| 21 | [**CHT (Compact Hist-Tree)**](stoianmihail-cht.md) | Header-only C++ compact Hist-Tree: a flattened radix-histogram table over sorted integer keys, beating RMI/PGM/RadixSpline lookup latency. | **B** | C++ | MIT | 🔴 abandoned |
| 22 | [**fast64 (FAST: Fast Architecture Sensitive Tree, 64-bit)**](ryanmarcus-fast64.md) | Rust/C AVX-512 static search tree for sorted u32/u64 keys; about 10% faster lookups than STX B-Tree in SOSD. | **B** | Rust | GPL-3.0 | 🔴 abandoned |
| 23 | [**LB+-Trees (persistent B+-Tree optimized for 3D XPoint…**](schencoding-lbtree.md) | Persistent B+-Tree for Intel Optane PM; 1.12-2.92x faster inserts than WB+-Tree and FP-Tree, similar lookups. | **B** | C++ | no license (study only) | 🔴 abandoned |
| 24 | [**Zvec**](alibaba-zvec.md) | Embedded (in-process) C++ vector database with HNSW and int8 quantization; about 2x Zilliz Cloud QPS at matched recall in its own VectorDBBench run. | **C** | C++ | Apache-2.0 | 🟢 active |
| 25 | [**redb**](cberner-redb.md) | Pure-Rust embedded ACID key-value store on copy-on-write B+trees; beats RocksDB/SQLite on durable single-key commits and reads; LMDB still reads faster. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 26 | [**TerarkDB**](bytedance-terarkdb.md) | ByteDance's RocksDB 5.18 fork with no-writeback key-value separation and lazy compaction; \~1.7x db_bench QPS vs RocksDB 6.12. | **C** | C++ | Apache-2.0 | 🟢 active |
| 27 | [**libmdbx**](mithril-mine-libmdbx.md) | LMDB fork: embedded memory-mapped ACID B+tree KV store; author reports 10-30% faster in-tmpfs CRUD than LMDB. | **C** | C | Apache-2.0 | 🟢 active |
| 28 | [**Adaptive Radix Tree (rafaelkallis/adaptive-radix-tree)**](rafaelkallis-adaptive-radix-tree.md) | Header-only C++11 adaptive radix tree for C-string keys; 1.5-2.4x faster than std::map&lt;std::string&gt; in author's microbenchmark. | **C** | C++ | GPL-3.0 | 🟢 active |
| 29 | [**PGM Extra (pgm-extra-rs)**](itsfoxstudio-pgm-extra-rs.md) | Pure-Rust PGM learned index with BTreeSet/BTreeMap-style Set and Map; beats BTreeSet on u64 lookups, loses to binary search. | **C** | Rust | MIT | 🟢 active |
| 30 | [**SNKV**](hash-anu-snkv.md) | C key-value API on SQLite's B-tree, pager and WAL minus the SQL layer; 1.6-2x SQLite in first-party KV microbenchmarks. | **C** | C | Apache-2.0 | 🟢 active |
| 31 | [**TokuDB / PerconaFT Fractal Tree Index**](percona-perconaft.md) | Fractal Tree (Bε-tree) transactional key-value library behind TokuDB/TokuMX; beat MongoDB 2.2's B-tree indexes on out-of-RAM inserts. | **C** | C++ | GPL-2.0 and AGPL-3.0 per… | 🟡 stale |
| 32 | [**Bw-Tree (Open BwTree, wangziqi2013)**](wangziqi2013-bwtree.md) | Open-source lock-free Bw-Tree (concurrent B+-tree multimap) from CMU; its own benchmarks show it slower than std::map and stx::btree. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 33 | [**PGM++ (adaptive search-strategy PGM-index)**](paper-pgm-adaptive-search-strategy-pgm-index.md) | Research patch to PGM-index static lookups: hybrid branchless/linear segment search plus cost-model epsilon tuning, up to 2.31x faster. | **C** | C++ | no license (study only) | 🟡 stale |
| 34 | [**MountDB (learned indexing integrated into RocksDB)**](paper-mountdb-learned-indexing-integrated-into-rocksdb.md) | Paper-only RocksDB v8.10 extension replacing SkipList memtable and fence-pointer index with learned indexes; up to 1.77x reads. | **C** | C++ | no license (study only) | ⚪ unknown |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
