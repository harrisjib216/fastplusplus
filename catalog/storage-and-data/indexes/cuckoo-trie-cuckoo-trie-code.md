# Cuckoo Trie

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Unlicense` · 🔴 abandoned

> Research C ordered index storing a trie in a cuckoo hash table; faster DRAM-bound lookups than HOT, ARTOLC, STX B-tree.

| | |
|---|---|
| **Beats** | B-tree (STX B-Tree), ART, HOT, Wormhole |
| **Claimed result** | "the Cuckoo Trie outperforms the other indexes—by up to 35% (HOT), 20% (ARTOLC), 50% (Wormhole) and 360% (STX) on YCSB-C with osm." |
| **Workload** | YCSB-C (100% lookup, uniform distribution) on the osm dataset (real-world key distribution, &gt;=1GB index, exceeding LLC capacity), single-threaded, comparing the Cuckoo Trie against STX B-Tree, ARTOLC, HOT, and Wormhole. |
| **Metric** | throughput |
| **Hardware** | Dual-socket Intel Xeon Gold 6132 (Skylake), 14 cores @ 2.6GHz per socket, 96GB DDR4-2666 per NUMA node, hyper-threading/Turbo-Boost disabled |
| **Compiler and flags** | GCC 7.5.0 (paper). Cuckoo Trie: -O3 -fvisibility=hidden -flto -fno-strict-aliasing -march=haswell -DNDEBUG (Makefile). Baselines in other-benchmarked-indexes: STX and HOT -O3 -march=native, ARTOLC -O3, Wormhole driver -O2. |
| **Adoption** | 57 stars |
| **Last commit** | 2021-10-23 |
| **Links** | [repository](https://github.com/cuckoo-trie/cuckoo-trie-code) · [benchmark](https://arxiv.org/pdf/2201.09331) |

## Verdict

In the SOSP'21 paper (arXiv 2201.09331, Sec. 6.2), single-threaded YCSB-C with uniform lookups on 200M osm keys ran up to 35%, 20%, 50% and 360% faster than HOT, ARTOLC, Wormhole and the TLX STX B+-tree respectively (not std::map), on a dual-socket Xeon Gold 6132 (Skylake, 2.6 GHz, Turbo and hyper-threading off, NUMA-interleaved) with GCC 7.5.0, jemalloc and 2 MB huge pages. Growing from 10M to 640M random 8-byte keys slowed HOT, ARTOLC and STX lookups by about 1.7x but the Cuckoo Trie by only 1.23x.

## Use it when

- Read-heavy point lookups (YCSB-B/C style) on a large in-memory ordered index that is far bigger than the LLC. The paper's datasets were 1 GB or more, and the lead over HOT, ARTOLC and STX grows with index size.
- Keys that diverge early, i.e. short unique prefixes: random 8- or 16-byte keys, 64-bit encoded integers like the osm dataset, or short strings like the reddit usernames.
- Linux x86-64 servers (Haswell or newer) where you can reserve 2 MB huge pages, run jemalloc with THP, and size the table ahead of time from a known key count.
- Multi-threaded lookup-heavy services (lookups take no locks and scaled almost linearly on 28 cores), or systems like a Redis sorted set whose per-element work hides the leaf-list latency during scans.
- As an MLP-aware research baseline or a design to port, not as a production dependency.

## Skip it when

- Keys with long common prefixes, such as composite IDs or URLs. On az (average unique prefix 138 bits) it is slower than HOT and ARTOLC, because jump nodes save memory but not DRAM round trips.
- Scan-heavy standalone workloads. On YCSB-E its scan throughput was the lowest of all indexes tested.
- Workloads that need deletes, automatic growth, or top insert speed. Deletion and resizing are not implemented. ARTOLC inserts faster, and ARTOLC also wins YCSB-D, where recently inserted keys are served from cache.
- Memory-constrained deployments. It uses up to 156% more memory than HOT and STX, although up to 28% less than ARTOLC and Wormhole.
- Production use, non-Linux or non-x86 platforms, pre-Haswell CPUs, or keys over 256 bytes. The README says the code 'is not robust enough to be used as an index in your program'.

## How it is fast

It stores the nodes of a path-compressed trie in a bucketized cuckoo hash table keyed by key prefix, so every node on a search path can be located from the key alone, with no pointer-chasing. A lookup therefore computes the prefix hashes up front and prefetches both candidate buckets for the next D=5 levels, keeping several DRAM misses in flight at once (memory-level parallelism). Each bucket is one 64-byte cache line holding four 15-byte entries that store no keys: a small tag, a 'color' and the parent's color identify each node, using peelable hashing. Keys are split into 5-bit symbols with BMI2 PDEP, and sorted iteration walks a linked list of leaves, prefetching the next leaf.

## Compared with alternatives

Pick it over HOT or ART Synchronized (OLC) for DRAM-resident, lookup-dominated work on keys with short unique prefixes (the paper measured +35% over HOT and +20% over ARTOLC on osm YCSB-C), and over the learned-index siblings (ALEX, LIPP, PGM, RMI), which were benchmarked on numeric keys, when you need variable-length byte keys. Stay with HOT for lower memory, long-common-prefix keys or scans, and with ART OLC for insert-heavy work or deletes.

## Integration

| | |
|---|---|
| **Form** | shared lib (libcuckoo_trie.so from a plain Makefile; about 25 C files, small enough to vendor as a source-drop) |
| **Dependencies** | pthreads and Linux MAP_HUGETLB with 2 MB huge pages reserved in advance via nr_hugepages. jemalloc with MALLOC_CONF=thp:always is recommended for the caller's key/value memory (it is not linked by the library). |
| **Minimum toolchain** | GCC 5.4+ (the authors tested GCC 5.4.0 and 7.5.0; GCC 4.8.5 fails because it lacks -march=haswell). Needs GNU C extensions (__uint128_t, x86 BMI builtins). Clang support is not documented. |
| **Platforms** | Linux x86-64 only, Haswell or newer (uses BEXTR, PDEP and BZHI via -march=haswell). |
| **Thread safety** | The default build (#define MULTITHREADING in config.h) is thread-safe. Inserts, updates and lookups are linearizable, readers are lock-free using seqlock validation, and writers lock buckets. Each thread needs its own iterator, and range iteration is not atomic with respect to concurrent inserts. Removing MULTITHREADING builds a faster single-threaded version. |
| **Drop-in for the baseline** | no |

## Gotchas

- Capacity is fixed at ct_alloc and there is no resize. After an insert returns S_OVERFLOW, the result of every later operation except ct_free is undefined. Size the table up front: the API suggests 1.5N to 2N cells, the benchmark defaults to 2.5N, and the paper ran at 85% load.
- ct_insert stores a pointer to your ct_kv without copying it. The record must not be freed or modified while it is in the trie, and ct_free does not free records. There is also no ct_iter_free; iterators are plain malloc'd.
- ct_alloc returns NULL (and prints a message) if not enough 2 MB huge pages are reserved. Separately, jemalloc's THP silently falls back to 4 KB pages, costing throughput. Watch thp_fault_fallback in /proc/vmstat.
- API.md says ct_insert aborts on a duplicate key, but the code returns S_ALREADYIN. The bucket-mix table uses a fixed seed (rand_seed(1)), so the table layout is not keyed per instance.

## Known shortcomings

- Slower than ARTOLC on the az dataset, on scans and on inserts. Abandoned (last main commit 2021-10).
- Research code (the README says it is not robust enough for real programs); abandoned since 2021-10 with only student forks. No delete and no resize: fixed capacity, and after S_OVERFLOW every later operation is undefined. Stores the caller's record by pointer (no copy); max key 256 B.
- Linux x86-64 Haswell+ only (BEXTR/PDEP/BZHI), GCC 5.4+; needs reserved 2 MB huge pages (ct_alloc returns NULL when short). Slowest of all tested on scan-heavy YCSB-E; loses on long-common-prefix keys; up to 156% more memory than HOT/STX. The 360% win is vs the TLX STX B+-tree.

## Caveats and trade-offs

Research code: the README says it 'was created to run the experiments in the paper' and 'is not robust enough to be used as an index in your program'. It runs on Linux x86_64 only and needs 2MB huge pages plus a huge-page allocator (jemalloc, THP) for paper-level numbers. The Cuckoo Trie is slower on the az dataset (long common prefixes), on scan-heavy YCSB-E, and on inserts vs ARTOLC. The 360% win is over the STX B+-tree (tlx), not std::map. Optimization flags differ slightly across the compared indexes. Unlicense is a public-domain dedication with no patent grant. The baselines' benchmark repo (other-benchmarked-indexes) has no license.

Exploits memory-level parallelism via a cuckoo hash table layout; requires 2MB huge pages and a huge-page-aware allocator (e.g. jemalloc) to hit reported numbers, x86_64/Linux only; performs worse than other tries on keys with long common prefixes (its worst case, the 'az' dataset) and on scan-heavy workloads where its DRAM-access overlap trick doesn't help.

## Maintenance

Abandoned research code. There are three commits, all from the October 2021 public release, no maintained fork (only 0-star student forks from 2024-2026, whose epoch/resize PRs were closed unmerged), and the authors warn it is not production-robust; it is Unlicense (public domain) and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The SOSP'21 paper (Sec. 6.1) states the Intel Xeon Gold 6132 and GCC 7.5.0. Flags are set in public Makefiles: cuckoo-trie-code/Makefile (-O3 -fvisibility=hidden -flto -fno-strict-aliasing -march=haswell) and the baselines' in cuckoo-trie/other-benchmarked-indexes (stx, hot: -O3 -march=native; artolc: -O3; wormhole driver: -O2). Benchmark code is public: benchmark.c plus stx/test_stx.cpp, hot, artolc/test_artolc.cpp, wormhole/test_wormhole.c.
- **Verifier notes:** The quote is verbatim from the SOSP'21 paper (arXiv 2201.09331, Sec. 6.2); the abstract gives the 20%-360% range. The last default-branch commit is 2021-10-23 ('Add short summary and full paper citation to readme'). gh's pushed_at of 2024-05-14 is not a commit on main, so maintenance moves from stale to abandoned. Other metadata matches gh: Unlicense, 57 stars, not a fork or archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2201.09331>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/Makefile>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes/blob/main/stx/Makefile>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes/blob/main/hot/Makefile>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes/blob/main/artolc/Makefile>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes/blob/main/wormhole/Makefile>
- **Sources the enricher read:**
  - <https://github.com/cuckoo-trie/cuckoo-trie-code>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/README.md>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/API.md>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/Makefile>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/config.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/cuckoo_trie.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/cuckoo_trie_internal.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/key_object.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/main.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/main.c>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/atomics.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/util.c>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/util.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/compiler.h>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/main/benchmark.c>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/commits/main>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/issues/1>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/pull/5>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/pull/7>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/forks>
  - <https://github.com/cuckoo-trie/other-benchmarked-indexes>
  - <https://arxiv.org/pdf/2201.09331>
  - <https://hn.algolia.com/api/v1/search?query=%22cuckoo%20trie%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cuckoo-trie/cuckoo-trie-code`) · [data/wave6/enrich/raw/github_com_cuckoo_trie_cuckoo_trie_code.json](../../../data/wave6/enrich/raw/github_com_cuckoo_trie_cuckoo_trie_code.json) (enrichment confidence 0.86)

</details>
