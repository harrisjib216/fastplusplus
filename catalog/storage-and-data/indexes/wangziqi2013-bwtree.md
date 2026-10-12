# Bw-Tree (Open BwTree, wangziqi2013)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Open-source lock-free Bw-Tree (concurrent B+-tree multimap) from CMU; its own benchmarks show it slower than std::map and stx::btree.

| | |
|---|---|
| **Beats** | BerkeleyDB (B-tree mode) |
| **Claimed result** | This repo has no numbers against BerkeleyDB. SIGMOD'18 (OpenBw-Tree paper): 1.1-2.5x faster than the original Bw-Tree design on insert-heavy workloads and 1.1-1.4x on read-heavy ones, and faster than a lock-free SkipList. It is 'still slower than its competitors except the SkipList': ART is more than 4x faster for point lookups, and Masstree and a B+Tree with optimistic lock coupling are faster, often by about 2x. The repo's own benchmark-all screenshot (result/result-2016-07-30-2.png) gives BwTree 4.65M insert/s and 9.58M read/s vs std::map 5.91M/17.85M, std::unordered_map 15.36M/81.65M and stx::btree 10.60M/21.50M. The 18.7x (Xbox LIVE) and 5.8x (synthetic) speedups over BerkeleyDB in ICDE'13 are Microsoft's own closed-source implementation. |
| **Workload** | ICDE'13 (Microsoft implementation, 8 worker threads, 8K pages): the Xbox LIVE trace is 27M get-set operations with \~94-byte alphanumeric keys, \~1200-byte payloads and a read:write ratio of about 7.5:1 (not read-only, not 8-byte integer keys); the synthetic workload uses 8-byte integer keys and payloads, a 1M-entry initial index, 42M operations and 5:1 read:write; a deduplication trace gave 8.6x. SIGMOD'18 (this code): YCSB-style Insert-only, Read-only, Read/Update and Scan/Insert workloads on random, monotonic integer and email keys, run on 2x Xeon E5-2680 v2 with g++ 5.4 and tcmalloc. |
| **Metric** | throughput |
| **Hardware** | ICDE'13 (Microsoft implementation): Intel Xeon W3550 @ 3.07GHz, 4 cores / 8 hyperthreads, 24GB RAM. SIGMOD'18 (this code): 2x Intel Xeon E5-2680 v2, 128GB RAM. |
| **Compiler and flags** | ICDE'13 states none. SIGMOD'18: g++ 5.4 with tcmalloc. Repo result screenshots: g++ -std=c++11 -O3 (-mcx16, jemalloc via LD_PRELOAD). |
| **Adoption** | 531 stars; the Bw-Tree algorithm itself is used in SQL Server Hekaton, Azure DocumentDB and Bing per the original Microsoft Research work; this repo is an independent C++ reimplementation built for CMU's Peloton DBMS |
| **Last commit** | 2018-11-14 |
| **Links** | [repository](https://github.com/wangziqi2013/BwTree) · [benchmark](https://db.cs.cmu.edu/papers/2018/mod342-wangA.pdf) |

## Verdict

The BerkeleyDB wins are not this code: ICDE'13's 10.40M vs 0.56M ops/s (about 18.7x, Xbox LIVE trace), 3.83M vs 0.66M (5.8x, synthetic) and 8.6x (deduplication) were measured on Microsoft's unreleased implementation on a Xeon W3550 with 8 threads. This repo's own numbers put it behind the incumbents: a single-threaded benchmark-all screenshot (g++ -O3, jemalloc, sequential long keys, a ThinkPad T440s per the shell prompt, libstdc++ inferred) shows it slower than std::map, std::unordered_map and stx::btree, and the authors' SIGMOD'18 evaluation (2x Xeon E5-2680 v2, g++ 5.4, tcmalloc) finds it 1.1-2.5x faster than a reimplemented original Bw-Tree but slower than B+Tree-OLC, Masstree and ART, ahead only of a lock-free SkipList.

## Use it when

- Research or teaching where you need a working lock-free Bw-Tree (mapping table, delta chains, help-along SMOs, epoch GC) to study, instrument or port to another language.
- As a baseline in an index benchmark, or to reproduce or extend the SIGMOD'18 'Building a Bw-Tree Takes More Than Just Buzz Words' results (YCSB-style Insert-only, Read-only, Read/Update and Scan/Insert on integer or email keys).
- A prototype that specifically requires a latch-free, comparator-based, non-unique (multimap) ordered index over small trivially-copyable keys such as 64-bit integers, where you run a fixed thread pool registered up front and stay well under the \~1M-node mapping-table cap.

## Skip it when

- Whenever speed is the reason. The repo's own single-threaded benchmark-all screenshot shows 4.65M inserts/s and 9.58M reads/s, against 5.91M/17.85M for std::map and 10.60M/21.50M for stx::btree. With 20 threads in SIGMOD'18, ART with optimistic lock coupling was more than 4x faster on point lookups, and a B+Tree with optimistic lock coupling and Masstree were often about 2x faster (3.7x for B+Tree on monotonic insert-only).
- High-contention appends such as monotonic keys from many threads: in SIGMOD'18 it saw more than 10 CAS aborts per insert, and lock-based Masstree, ART and B+Tree held up better.
- Large or growing indexes: the mapping table is a fixed std::array of 2^20 node IDs with no resizing (a README 'Known Problem'; issue #45 still open). That caps the tree at roughly tens of millions of keys at 32-128 entries per leaf. The SIGMOD'18 paper describes lazily-backed virtual-memory expansion, but that is not what master ships.
- std::string or other non-POD keys and values: issue #62 (a segfault during the first GC cycle with std::string keys) was never fixed, and the author notes that the tree moves keys and values often, so non-POD types are slow.
- Production systems. Delete is not wait-free: a thread that dies between posting and removing its ABORT delta blocks all writes under that parent (#40). There is an unfixed use-after-free race in epoch cleanup (#69), and a question about Microsoft's Bw-Tree patents (#71) was never answered. It is in-memory only, with no persistence (#72), unlike the BerkeleyDB baseline.

## How it is fast

Nodes are addressed through a mapping table of logical node IDs. Writers prepend delta records (insert, delete, split, merge) to a node's delta chain and publish them with one compare-and-swap on that node's slot, and threads 'help along' unfinished structure modifications instead of waiting on latches. A chain is consolidated into a new base node after 8 deltas, and nodes split above 128 entries and merge below 32. On top of Microsoft's design, the SIGMOD'18 paper adds delta records pre-allocated inside the base node's memory chunk, decentralized per-thread epoch GC, fast consolidation, node-search shortcuts using delta offsets, and non-unique key support; together these give 1.1-2.5x over a good-faith original Bw-Tree, but the indirection and delta-chain traversal still cost more instructions and cache misses than a latch-based B+Tree.

## Compared with alternatives

For real concurrent in-memory indexing, pick ART Synchronized: the SIGMOD'18 authors measured ART with optimistic lock coupling more than 4x faster than this tree on point lookups, and LIPP's evaluation also lists BwTree among the indexes it beats. Choose Open BwTree only when the requirement is specifically a latch-free, comparator-based B+-tree multimap, or a reference implementation of the Bw-Tree/Hekaton design.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the index itself (C++11 STL plus pthreads; bwtree.h also includes sorted_small_set.h, bloom_filter.h and atomic_stack.h). The test/benchmark harness uses PAPI (disable with -DNO_USE_PAPI) and jemalloc via LD_PRELOAD, and the full-speed make target links boost_system and boost_thread. |
| **Minimum toolchain** | C++11. Only g++-5 is used in the Makefile and Travis. clang++ fails on private nested-class access unless patched (#64). The 'register' keyword in bloom_filter.h is invalid in C++17 (#70). Needs -mcx16 for the 16-byte CAS. |
| **Platforms** | x86-64 Linux is the only tested platform (Travis on Ubuntu). It relies on a 16-byte std::atomic CAS (LOCK CMPXCHG16B) and GCC builtins and attributes. Other architectures, macOS/Windows and MSVC are not documented. |
| **Thread safety** | Insert, Delete, GetValue and iterator creation are lock-free and safe from many threads. Each thread needs a GC slot, either via RegisterThread() before the tree is constructed or via UpdateThreadLocal(n) plus AssignGCID(id). A single iterator object must not be shared between threads. Operations are atomic, not isolated. |
| **Drop-in for the baseline** | no |

## Gotchas

- Debug mode is the default. Unless you compile with -DBWTREE_NODEBUG, BWTREE_DEBUG enables assertions and per-operation atomic counters, and bwt_printf logs every call to stderr while print_flag is true, which is its initial value in bwtree.cpp. ALL_PUBLIC is also hard-defined, so internal members are public.
- A BwTree object is about 16 MB, because the mapping table and the free NodeID stack are in-object arrays. Declaring one on the stack crashes (#65), so always allocate it with new. The constructor also starts a background epoch/GC thread unless you pass start_gc_thread = false.
- Not header-only: you must compile src/bwtree.cpp (it defines print_flag, the thread_local gc_id and the thread counter). A thread with no assigned GC ID (gc_id = -1) trips an assert or causes undefined behavior. The GC slot count is captured when the tree is constructed.
- Multimap semantics: Insert only fails if that exact (key, value) pair already exists, so repeated keys accumulate values, and there is no update, so 'replace' means a non-atomic Delete + Insert. Iterators copy one leaf page at a time and give no snapshot across pages.

## Known shortcomings

- NOT FASTER: the 18.7x/5.8x vs BerkeleyDB are Microsoft's closed Bw-Tree numbers; this open implementation's own benchmarks show it slower than std::map and stx::btree, and the SIGMOD'18 evaluation found it slower than B+Tree, Masstree and ART.
- The repo's own single-thread numbers (4.65M inserts / 9.58M reads per s) trail std::map (5.91/17.85) and stx::btree (10.60/21.50); in SIGMOD'18 ART-OLC is &gt;4x faster on lookups and B+Tree-OLC/Masstree \~2x; it beats only a skip list. Fixed 2^20-node mapping table with no resize (#45). Open bugs: epoch-GC use-after-free (#69), std::string segfault (#62), clang build failure (#64), C++17 'register' (#70).
- Delete is not wait-free (ABORT delta; a dead thread blocks writes, #40); &gt;10 aborts per insert under high contention. Debug and stderr logging on by default (-DBWTREE_NODEBUG needed); \~16 MB object can crash the stack (#65); multimap with no update/size. Abandoned 2018-11; x86-64 g++-5 era (16-byte CAS, -mcx16); in-memory only; Microsoft patent question unanswered (#71).

## Caveats and trade-offs

The Bw-Tree speedups over BerkeleyDB in ICDE'13 come from Microsoft's unreleased implementation, not this repo. The repo's README says its benchmark is 'unavailable' during a redesign. Its own first-party numbers are single-threaded, where it is slower than std::map and stx::btree. Its authors' SIGMOD'18 evaluation concludes the Bw-Tree 'still does not perform as well as other concurrent data structures that use locks'. The std::map comparison ran with g++ on Ubuntu, so libstdc++ is inferred, not explicitly stated.

Lock-free via delta-chain updates and epoch-based reclamation; not wait-free (an ABORT delta can stall a locked parent node if the posting thread dies); fixed-size mapping table with no dynamic resize

## Maintenance

Abandoned since 2018-11-14, with 14 open issues (use-after-free race, std::string segfault, clang build failure) unanswered; it is Apache-2.0 and small enough to vendor (CMU's now-archived NoisePage vendored it under third_party/bwtree), and the last known-good toolchain is g++-5 on Ubuntu.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification B, tier now C.
- **Tier reason:** The ICDE'13 page does show 10.4M vs 555K ops/s (18.7x) and 5.8x against BerkeleyDB, but those numbers belong to Microsoft's unreleased Win32 implementation, not this repository. The only benchmarks of this code against a recognizable incumbent are first-party screenshots in the repo's result/ folder (g++ -O3, CPU unstated), which show it slower than std::map, std::unordered_map and stx::btree. Its authors' peer-reviewed SIGMOD'18 paper likewise reports it slower than B+Tree, Masstree and ART.
- **Verifier notes:** Reject as not-faster: the only speedup against a recognizable baseline (BerkeleyDB) belongs to different, closed code, and every benchmark of this repo's own code puts it behind std::map, stx::btree, B+Tree (OLC), Masstree and ART, ahead only of a lock-free SkipList. Metadata checks out: Apache-2.0, 531 stars, last commit 2018-11-14, abandoned, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compared_against_cpp_std_directly`, `baseline_stdlib`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bw-tree-icde2013-final.pdf>
  - <https://github.com/wangziqi2013/BwTree>
  - <https://db.cs.cmu.edu/papers/2018/mod342-wangA.pdf>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-07-30-2.png>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-07-30.png>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-07-19.png>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-06-18.jpg>
- **Sources the enricher read:**
  - <https://github.com/wangziqi2013/BwTree>
  - <https://github.com/wangziqi2013/BwTree/blob/master/README.md>
  - <https://github.com/wangziqi2013/BwTree/blob/master/src/bwtree.h>
  - <https://github.com/wangziqi2013/BwTree/blob/master/src/bwtree.cpp>
  - <https://github.com/wangziqi2013/BwTree/blob/master/src/atomic_stack.h>
  - <https://github.com/wangziqi2013/BwTree/blob/master/Makefile>
  - <https://github.com/wangziqi2013/BwTree/blob/master/.travis.yml>
  - <https://github.com/wangziqi2013/BwTree/blob/master/result/README.md>
  - <https://github.com/wangziqi2013/BwTree/blob/master/benchmark/README.md>
  - <https://github.com/wangziqi2013/BwTree/blob/master/test/main.cpp>
  - <https://github.com/wangziqi2013/BwTree/blob/master/test/test_suite.h>
  - <https://github.com/wangziqi2013/BwTree/blob/master/test/test_suite.cpp>
  - <https://github.com/wangziqi2013/BwTree/blob/master/test/performance_test.cpp>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-07-30-2.png>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-07-30.png>
  - <https://raw.githubusercontent.com/wangziqi2013/BwTree/master/result/result-2016-06-18.jpg>
  - <https://github.com/wangziqi2013/BwTree/issues>
  - <https://github.com/wangziqi2013/BwTree/issues/40>
  - <https://github.com/wangziqi2013/BwTree/issues/61>
  - <https://github.com/wangziqi2013/BwTree/issues/62>
  - <https://github.com/wangziqi2013/BwTree/issues/64>
  - <https://github.com/wangziqi2013/BwTree/issues/65>
  - <https://github.com/wangziqi2013/BwTree/issues/67>
  - <https://github.com/wangziqi2013/BwTree/issues/69>
  - <https://github.com/wangziqi2013/BwTree/issues/70>
  - <https://github.com/wangziqi2013/BwTree/issues/71>
  - <https://github.com/cmu-db/noisepage/tree/master/third_party/bwtree>
  - <https://db.cs.cmu.edu/papers/2018/mod342-wangA.pdf>
  - <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bw-tree-icde2013-final.pdf>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/wangziqi2013/bwtree`) · [data/wave6/enrich/raw/github_com_wangziqi2013_bwtree.json](../../../data/wave6/enrich/raw/github_com_wangziqi2013_bwtree.json) (enrichment confidence 0.8)

</details>
