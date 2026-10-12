# MemC3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> NSDI'13 research fork of Memcached 1.4.13: optimistic cuckoo hashing plus CLOCK eviction; \~3x read-heavy throughput, incomplete protocol.

| | |
|---|---|
| **Beats** | memcached |
| **Claimed result** | Full-system throughput over the network: MemC3 peaks at 4.4 MOPS vs 1.5 MOPS for original Memcached, 'almost 3x' (Fig. 9, 95% GET/5% SET YCSB Zipf workload). The paper says it uses 30% less memory for small key-value pairs, or stores 30% more objects; Table 3 shows cuckoo+CLOCK holding about 40% more 16B-key/32B-value items than Memcached's default chaining+LRU. The core cuckoo hash table alone does 5M lookups/sec per thread and 35M lookups/sec at 12 threads. |
| **Workload** | End-to-end test: 95% GET/5% SET YCSB-generated Zipf workload, pre-generated as traces. It is sent from 50 client nodes over 10Gb Ethernet using libmemcached 1.0.7 multi-get (batches of 100 GETs) to MemC3 vs original Memcached 1.4.13, optimized Memcached, and sharded optimized Memcached. Each system gets 1GB of cache space. Separate local tests cover hash-table lookup throughput (single thread and multi-thread) and cache space efficiency and miss ratio (Table 3). |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon L5640 @2.27GHz (2x6 cores), 2x12MB L3 cache, 2x16GB DDR SDRAM, 10Gb Ethernet |
| **Adoption** | 156 stars |
| **Last commit** | 2014-06-28 |
| **Links** | [repository](https://github.com/efficient/memc3) · [benchmark](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final197.pdf) |

## Verdict

The server was a 2x6-core Xeon L5640 with 1GB of item memory. 50 client machines on 10GbE replayed a pre-generated YCSB Zipf trace (95% GET / 5% SET) using 100-key libmemcached multi-gets. MemC3 peaked at 4.4 MOPS vs 1.5 MOPS for stock Memcached 1.4.13, almost 3x. Local microbenchmarks showed cuckoo+CLOCK holding \~40% more 16B/32B items than chaining+LRU and \~5M lookups/s per thread. The server compiler and flags are not stated. The baseline predates Memcached 1.4.15 (Sept 2012), which already reworked read scalability, and Memcached's maintainer argues the stock-Memcached number may have been handicapped by benchmark setup.

## Use it when

- Studying or re-implementing a read-mostly (90%+ GET), many-threaded cache index: it is a compact working reference for optimistic cuckoo hashing and CLOCK wired into a real memcached-shaped server.
- Reproducing the NSDI'13 numbers or using MemC3 as a historical baseline in a paper. The repo ships the YCSB trace settings, a trace generator and a libmemcached multi-get bench client.
- Controlled experiments with tiny, fixed-size objects (the paper used 16B keys and 32B values), where per-item header overhead dominates and roughly 40% more items per GB of item memory is the point.
- Pure GET/SET traffic on Linux x86-64 hardware with more than 6 cores, when you don't need delete, CAS, incr/decr or add/replace semantics.

## Skip it when

- Any production cache. Memcached's maintainer showed (2020 review, with a repro script) that MemC3 can return wrong or corrupt data. Refcounts were removed, yet GET responses are still sent zero-copy from slab memory, so a concurrent overwrite can change a value while it is being sent.
- Workloads that need delete, CAS/gets, incr/decr, add/replace/append/prepend or slab rebalancing. These are stubbed, broken (the review reports that delete leaks the item's memory) or removed outright.
- Write-heavy or miss-heavy caches, because inserts and evictions are single-writer. The paper's own 1GB cache with \~15% misses peaks at 6 MOPS at about 6 threads and falls off after that. With 10% inserts the hash table peaks at 20 MOPS at 10 threads.
- Caches that are small relative to the working set. Table 3 shows LRU beating CLOCK on miss ratio at 256MB and below (e.g. 64MB: cuckoo+LRU 35.87% vs cuckoo+CLOCK 36.46%).
- Growing datasets, or non-Linux / non-x86 / little-core hosts. The cuckoo index never resizes, worker threads are hard-pinned to CPU cores 6+i, x86 intrinsic headers are included, and key comparison assumes little-endian.

## How it is fast

The index uses optimistic concurrent cuckoo hashing, a form of partial-key cuckoo hashing: each key has two 4-slot buckets, the alternate bucket is b XOR hash(tag) so moving an entry never requires reading its key, and lookups compare 1-byte tags before following a pointer (about 2 cacheline reads per lookup). Readers take no locks; they read one of 8192 striped version counters before and after scanning the buckets and retry if it changed. A writer first finds the whole cuckoo path and then moves keys backward along it, so no key is ever missing from the table mid-insert. CLOCK only sets a recency bit on a hit instead of relinking an LRU list, which removes the LRU mutex, the two LRU pointers and the 2-byte refcount from each item; integer-cast key comparison and optional 2MB hugepages add smaller gains.

## Compared with alternatives

Pick MemC3 only to study or reproduce the optimistic-cuckoo-plus-CLOCK design inside a memcached-shaped server. For a running cache, Pelikan/Segcache (maintained, about 8x Memcached at 24 threads per NSDI'21) or current Memcached is the safer choice, and MICA (same efficient/ GitHub org) goes much further on tiny items (65.6-76.9 Mops) with a different design. If you only want the concurrent cuckoo table, the README points to its maintained successor, libcuckoo.

## Integration

| | |
|---|---|
| **Form** | source-drop — an autotools build of a standalone server binary (memc3), not a library. The cuckoo table (assoc_cuckoo.c) is tied to memcached's item and slab code. |
| **Dependencies** | libevent for the server. The bench tools also need libmemcached, YCSB (to pre-generate traces), and OpenSSL/zlib for the trace generator. |
| **Minimum toolchain** | C99 (AC_PROG_CC_C99) with GCC __sync builtins and autoconf/automake. Under GCC, configure adds -Wall -Werror -pedantic, and GCC 10+ needs -fcommon because memcached.h defines globals without extern. The last known-good compiler is not documented. |
| **Platforms** | Linux x86-64 in practice: the code includes xmmintrin.h/immintrin.h, uses pthread_attr_setaffinity_np/sched_getcpu, pins worker i to core 6+i, and has a little-endian-only integer key compare. Hugepage support is Linux-only (SHM_HUGETLB). |
| **Thread safety** | Designed as multi-reader/single-writer: lookups are lock-free and retry on a version change, while inserts and evictions are meant to be serialized (paper, Algorithm 1). In the released code, item_lock() compiles to a no-op in cuckoo builds, and the SET path (store_item -&gt; do_item_link_nolock -&gt; assoc2_insert) holds no lock, even though assoc2_insert is commented 'need to be protected by cache_lock' and uses global cuckoo-path scratch arrays. So concurrent writers look unserialized, and value bytes are not protected after the lookup. |
| **Drop-in for the baseline** | partial — it speaks the memcached protocol, so plain GET/SET clients work unchanged, but delete, CAS, incr/decr, add/replace semantics, slab rebalancing and several stats commands are missing or broken, and the index has a fixed size. |

## Gotchas

- The index is allocated at full size at startup. The default hashpower of 25 means 2^25 packed 40-byte buckets (\~1.25 GiB), whatever -m is set to. There is no expansion: when a 500-displacement cuckoo search fails, assoc2_insert prints 'hash table is full ... need to increase hashpower' and do_item_link_nolock hits assert(false). Size the table up front with -o hashpower=N.
- The lookup's version check covers only the index read. GET builds iovecs that point into slab memory, and the refcounts are commented out. The memcached.org repro shows a 200KB value turning from '1's into '2's partway through a large multiget.
- Configuration is compile-time #defines in memc3_config.h: cuckoo vs chaining, CLOCK vs LRU, lock mode, hugepages. The shipped config leaves hugepages off, although the paper's full-system run used MemC3 'with all optimizations enabled'.
- It may not start or build as-is. Creating worker thread i fails on hosts without a core 6+i (the memcached.org reviewers had to comment out the affinity line). Globals such as keyver_array and hashpower are defined in a header, which breaks linking under GCC 10's default -fno-common.

## Known shortcomings

- The 3x is 4.4 vs 1.5 MOPS against stock Memcached 1.4.13 (2013); abandoned since 2014-06.
- Can return wrong or corrupt data: refcounts were removed and GET sends zero-copy from slab memory (the Memcached maintainer's 2020 review includes a repro script); delete leaks memory; CAS/incr/decr/add/replace are stubbed and slab rebalancing removed. The SET path takes no lock (item_lock is a no-op for cuckoo) although the paper assumes a single writer.
- Fixed-size index (default \~1.25 GiB), no resize, assert(false) when full. Linux x86 only, workers pinned to core 6+i, GCC 10+ link failure without -fcommon. The Memcached 1.4.13 baseline predates the 1.4.15 read-scaling work; libcuckoo is the maintained successor.

## Caveats and trade-offs

The paper does not state the compiler or build flags for the MemC3/Memcached server builds; only the bench client Makefile shows gcc -std=gnu99 -O2. The end-to-end numbers use pre-generated YCSB traces, not live YCSB (the scripts are bench/ycsb_workload_gen.sh and bench/ycsb_workload_settings), with clients batching 100 GETs per multi-get. The server CPU is a low-power L5640. The only branch was last committed 2014-06-28 (repo pushed_at is 2017-04-28), and the project is unmaintained.

CLOCK-based eviction only approximates strict LRU, trading eviction precision for space/concurrency; cuckoo hashing needs load-factor headroom and can hit rare high-latency insert paths near capacity; the repo's own README says the successor project, libcuckoo, is the actively maintained re-engineering of MemC3's hash table

## Maintenance

Abandoned: the last commit was 2014-06-28, it sits on a 2012 Memcached base, and an issue from 2021 is still unanswered. It is BSD-3-Clause and readable as a reference but unsafe to deploy, and its authors point to libcuckoo as the maintained re-engineering of its hash table.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'13 paper compares MemC3 against stock Memcached 1.4.13: full-system throughput 4.4 MOPS vs 1.5 MOPS (almost 3x, Fig. 9), 30% less memory for small key-value pairs, and a 5M/35M lookups/sec hash table. The CPU is stated (2x Xeon L5640), but the compiler and flags for the server builds are not, so it falls short of A.
- **Verifier notes:** The numbers in the record match the paper. The only fixes are that 'up to 3x' is 4.4 vs 1.5 MOPS ('almost 3x'), the paper lists DRAM as DDR SDRAM, not DDR3, and last_commit was the pushed_at date rather than the last commit on master (2014-06-28). License BSD-3-Clause, 156 stars, not archived, not a fork: all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final197.pdf>
  - <https://github.com/efficient/memc3>
  - <https://github.com/efficient/memc3/tree/master/bench>
- **Sources the enricher read:**
  - <https://github.com/efficient/memc3>
  - <https://github.com/efficient/memc3/blob/master/README.md>
  - <https://github.com/efficient/memc3/blob/master/memc3_config.h>
  - <https://github.com/efficient/memc3/blob/master/assoc_cuckoo.c>
  - <https://github.com/efficient/memc3/blob/master/assoc_cuckoo.h>
  - <https://github.com/efficient/memc3/blob/master/memcached.h>
  - <https://github.com/efficient/memc3/blob/master/memcached.c>
  - <https://github.com/efficient/memc3/blob/master/items.c>
  - <https://github.com/efficient/memc3/blob/master/thread.c>
  - <https://github.com/efficient/memc3/blob/master/slabs.c>
  - <https://github.com/efficient/memc3/blob/master/memc3_util.h>
  - <https://github.com/efficient/memc3/blob/master/memc3_util.c>
  - <https://github.com/efficient/memc3/blob/master/configure.ac>
  - <https://github.com/efficient/memc3/blob/master/Makefile.am>
  - <https://github.com/efficient/memc3/blob/master/bench/Makefile>
  - <https://github.com/efficient/memc3/commits/master>
  - <https://github.com/efficient/memc3/issues/2>
  - <https://github.com/efficient/memc3/issues/3>
  - <https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final197.pdf>
  - <https://memcached.org/blog/paper-review-memc3/>
  - <https://github.com/memcached/memcached/wiki/ReleaseNotes1415>
  - <https://github.com/efficient/libcuckoo>
  - <https://gcc.gnu.org/gcc-10/porting_to.html>
  - <https://hn.algolia.com/api/v1/search?query=MemC3&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/efficient/memc3`) · [data/wave6/enrich/raw/github_com_efficient_memc3.json](../../../data/wave6/enrich/raw/github_com_efficient_memc3.json) (enrichment confidence 0.85)

</details>
