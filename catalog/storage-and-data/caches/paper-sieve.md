# SIEVE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Parameter-free FIFO-plus-moving-hand eviction policy that beats LRU on miss ratio and multi-thread throughput for web caches.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | Cachelib-based prototype: SIEVE is 16% faster than Cachelib's optimized LRU (17% vs TwoQ) at 1 thread on both the Meta and Twitter KV traces. At 16 threads it has more than 2x the throughput of optimized LRU and TwoQ on the Meta trace (the contributions list says 125% higher than optimized LRU). Optimized LRU itself scales about 6x from 1 to 16 threads on Twitter; only the unoptimized LRU plateaus at 4 threads. Miss ratio in libCacheSim: on CDN1 at the large cache size, SIEVE reduces FIFO's miss ratio by a mean of 21%, and by more than 42% on 10% of traces (p90 whisker). Over 1559 traces it reduces ARC's miss ratio by up to 63.2% (mean 1.5%). The paper frames that 1.5% mean as significant next to ARC's own mean 6.3% reduction over LRU; the 1.5% is smaller than the 6.3%, not larger. |
| **Workload** | 1559 traces from 7 datasets (247,017 million requests, 14,852 million objects; Twitter, Meta, Wikimedia, TencentPhoto and two proprietary CDNs) replayed in libCacheSim for miss ratio. Separately, a Cachelib (C++) prototype replays two production KV traces (Meta, Twitter) with 1-16 threads, with cache size 4 x nthreads GB, to measure throughput. |
| **Metric** | throughput |
| **Hardware** | Dual-socket Intel Xeon Gold 6142 @ 2.6GHz, 384GB DDR4 DRAM (CloudLab c6420 node), turbo boost off, threads pinned within one NUMA node |
| **Adoption** | 347 stars (libCacheSim); sievecache.com (redirects to cachemon.github.io/SIEVE-website) lists adopters including Immudb, TiDB, Pelikan, DragonFly, DNSCrypt-proxy, PostgREST and Ceph |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/1a1a11a/libCacheSim) · [benchmark](https://junchengyang.com/publication/nsdi24-SIEVE.pdf) |

## Verdict

Throughput: a CacheLib-based C++ prototype (Thesys-lab/cachelib-sosp23) ran on a CloudLab c6420 (dual Xeon Gold 6142 @ 2.6 GHz, 384 GB DDR4, turbo off, threads pinned to one NUMA node; compiler and flags not stated). It replayed Meta and Twitter KV traces with a cache of 4 GB × threads (miss ratios 7% and 2%), and SIEVE beat CacheLib's optimized LRU by 16% (TwoQ by 17%) at 1 thread and more than 2x at 16 threads on the Meta trace. Miss ratio was measured separately in the libCacheSim simulator over 1559 traces: a mean 21% lower than FIFO on CDN1 at the large cache size, and up to 63.2% (mean 1.5%) lower than ARC.

## Use it when

- Object, CDN or key-value caches with skewed (Zipf/power-law) popularity and few scans. This is the paper's domain: 1559 traces from Twitter, Meta, Wikimedia, Tencent and two CDNs, where SIEVE had the lowest miss ratio of 10 algorithms on more than 45% of traces.
- Swapping out a doubly-linked-list LRU in an in-process cache when you want no tuning parameters and a change of about 20 lines (12-21 lines in the paper's four library ports).
- Multi-threaded caches where LRU's move-to-head on every hit causes lock contention. The CacheLib prototype was 16% faster than CacheLib's optimized LRU at 1 thread and more than 2x faster at 16 threads on the Meta KV trace.
- Mid-to-large caches, around 10% of the trace footprint, where the gains are largest: a mean 21% lower miss ratio than FIFO on the CDN1 dataset, against 15% for CLOCK.
- As a building block that replaces the LRU queue inside ARC, TwoQ or LeCaR. ARC-SIEVE cut ARC's miss ratio by a mean of 3.7% (up to 62.5%) over the 1559 traces.

## Skip it when

- Block, page or file caches with scans or loops, such as database buffer pools or backup reads. The paper's §7 says SIEVE is not scan-resistant (it has no ghost queue) and sometimes has a higher miss ratio than LRU on block workloads. A co-author wrote on HN that when the hand sits near the head it evicts new objects in an MRU-like way and 'may not be robust'.
- Very small caches (0.1% of footprint): TwoQ and LHD sometimes beat it because new objects are evicted before they can show popularity. On two Wiki CDN traces, LRB beat it on byte miss ratio at 1-2% cache sizes.
- Workloads whose popular set changes abruptly. When the paper switched between two Zipf workloads, SIEVE had a larger transient miss-ratio spike than LRU or ARC because the hand has to travel back to the tail before old objects can go.
- When you need a ready-made C/C++ cache library. libCacheSim is a simulator, the CacheLib prototype is a research fork last pushed in December 2023, and SIEVE is not in upstream facebook/CacheLib (its tree has no MMSieve).
- Ring-buffer or log-structured stores. SIEVE evicts from the middle of the queue, so it needs a linked list (17 B of per-object metadata in the paper's Table 3), and a co-author called circular-buffer or log-structured implementations 'not trivial'.

## How it is fast

A hit only sets the object's visited bit. Nothing moves in the queue, so the hit path takes no list lock. In the CacheLib prototype a hit is a flag write, inserts use a CAS on the list head, and only eviction and removal take a folly::DistributedMutex. On a miss the hand walks from the tail toward the head, clearing visited bits and evicting the first unvisited object; objects that survive keep their position instead of being reinserted at the head as in CLOCK/FIFO-Reinsertion. The paper calls the result 'lazy promotion' plus 'quick demotion': new objects sit between the head and the hand and get examined soon after insertion, so one-hit wonders leave quickly, and in the simulator SIEVE ran up to 40% fewer instructions per request than LRU.

## Compared with alternatives

Pick SIEVE over LHD or W-TinyLFU/Caffeine when you are patching an existing C/C++ linked-list LRU for web or KV traffic and want a parameter-free change of about 20 lines with a lock-free hit path. LHD has tuning parameters and far more code (192/81/64 lines for hit/evict/insert against SIEVE's 4/9/3) but wins at very small caches. Caffeine is a complete concurrent JVM library, and W-TinyLFU is the safer choice when scans or an unknown workload mix are likely.

## Integration

| | |
|---|---|
| **Form** | source-drop (the algorithm). In the catalogued repo, Sieve.c is one policy inside libCacheSim, a CMake/Ninja-built C library and cachesim binary, and it holds no values. The CacheLib prototype is a full CacheLib fork. Third-party ports include kassane/sieve-cache-cpp (header-only, C++17, MIT). |
| **Dependencies** | The algorithm has none. libCacheSim needs glib-2.0 and zstd (zstd trace support is on by default); tcmalloc is optional. The CacheLib prototype needs CacheLib's full dependency set (folly, etc.), installed through contrib/build.sh. |
| **Minimum toolchain** | libCacheSim: CMake 3.12+ with CMAKE_CXX_STANDARD 17 for its C++ parts; the minimum C standard and compiler versions are not documented. CacheLib prototype: CacheLib's 2023 build script, tested on CentOS 8, Ubuntu 18.04 and Debian 10. kassane/sieve-cache-cpp: C++17 (uses std::pmr). |
| **Platforms** | The algorithm runs anywhere. libCacheSim documents installation on Ubuntu and macOS; the Node binding ships a prebuilt binary for Linux x64 only; Windows is not documented. The throughput results were measured on x86-64 (Xeon Gold 6142). |
| **Thread safety** | libCacheSim: Sieve.c takes no locks and each cache_t is single-threaded; the simulator parallelizes across independent cache instances and sizes. CacheLib prototype: hits set an access flag without the container lock, head inserts are lock-free (CAS), and eviction and removal hold a folly::DistributedMutex. kassane/sieve-cache-cpp has no locking. |
| **Drop-in for the baseline** | partial: SIEVE replaces LRU's hit and evict logic inside an existing linked-list cache with about 12-21 lines, and the get/put API stays the same. libCacheSim's Sieve.c itself is a simulator policy, not a cache you can store data in. |

## Gotchas

- Because eviction happens in the middle of the queue, deleting an object the hand points at must move the hand to its neighbour (libCacheSim's Sieve_remove_obj sets hand = prev). Ports that skip this leave a dangling hand. Eviction is also worst-case O(N) when most objects have their visited bit set.
- The CacheLib prototype is research-grade code. SieveList::getEvictionCandidate printf's and abort()s after more than two full sweeps, and unlink() calls try_lock() then abort() as its lock-held check. A null-tail race between lock-free linkAtHead and unlink was reported and fixed only in the sibling AtomicDList (PR #1, Dec 2023); SieveList still inserts at the head lock-free.
- Third-party ports vary in quality. kassane/sieve-cache-cpp's get() allocates and returns a shared_ptr copy of the value on every hit, its constructor calls std::pmr::set_default_resource (a process-wide side effect), and it has no mutex.
- Most of the headline miss-ratio results ignore object size (the paper assumes slab-style caches). Byte miss ratio is shown only for the CDN traces, and the paper's mean ARC-over-LRU reduction appears as both 6.7% and 6.3%.

## Known shortcomings

- The '&gt;2x LRU throughput at 16 threads' compares with an unoptimized LRU (optimized CacheLib LRU scales 6x to 16 threads); SIEVE's &gt;2x holds only on the Meta trace (125% per the paper) and it is 16% faster at 1 thread. Its miss-ratio edge over ARC (1.5% mean) is smaller than ARC's over LRU. Throughput came from a CacheLib prototype (Thesys-lab/cachelib-sosp23), not libCacheSim; no compiler/flags (verifier downgrade).
- libCacheSim is a simulator only (stores no values). SIEVE is not scan-resistant (paper section 7) and on block/page workloads is sometimes worse than LRU. At tiny caches (0.1%) TwoQ/LHD win; LRB wins byte miss ratio at 1-2% cache; bigger miss spike than LRU/ARC on popularity shift.
- The CacheLib prototype is a research fork, stale since 2023-12, with abort()/printf paths; the head-insert race is fixed only in AtomicDList, SieveList still inserts lock-free; not in upstream CacheLib. Compiler/flags unstated; the &gt;2x at 16 threads is on the Meta trace only. Third-party ports vary (the kassane C++ port copies a shared_ptr on every get, sets the global pmr default resource and has no lock).

## Caveats and trade-offs

The paper states the CPU model, NUMA pinning and turbo-boost setting for the throughput prototype but not the compiler or optimization flags, so it is capped at tier B. The miss-ratio numbers come from the libCacheSim simulator. The throughput numbers come from a separate Cachelib-based C++ prototype (Thesys-lab/cachelib-sosp23), not from libCacheSim. The &gt;2x throughput result at 16 threads is reported for the Meta trace only. The paper is internally inconsistent about ARC's mean reduction over LRU: the introduction says 6.7% (up to 33.7%) and Section 4.2 says 6.3%. libCacheSim's Sieve.c is a simulator policy, not a drop-in production cache.

Needs a per-object 'visited' bit like CLOCK; underperforms TwoQ/LHD/ARC at very small cache sizes because new objects can't demonstrate popularity before being evicted

## Maintenance

libCacheSim is actively maintained (last commit 2026-09-26, Apache-2.0, 347 stars), but Sieve.c has had only cosmetic edits since January 2024, and the CacheLib throughput prototype (Apache-2.0, 11 stars) has not been pushed since 2023-12-13. The algorithm is small enough to copy into your own cache, which is how the listed adopters (TiDB, Ceph, DragonFly, PostgREST, DNSCrypt-proxy, Immudb and others) use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'24 paper compares SIEVE against LRU (Cachelib's optimized LRU for throughput) plus FIFO, ARC and 7 other policies for miss ratio. The code is public (cacheMon/NSDI24-SIEVE simulator snapshot; Thesys-lab/cachelib-sosp23 prototype) and the CPU model is stated (c6420, Intel Gold 6142 @ 2.6 GHz, turbo off, one NUMA node), but the compiler and flags are not, so it cannot be A.
- **Verifier notes:** The original claim misattributed the 4-thread plateau to the optimized LRU; in the paper it applies only to the unoptimized LRU. The claim also inverted the 1.5% vs 6.3% comparison. The core &gt;2x-at-16-threads and 63.2%-vs-ARC numbers are on the page. The metadata checks out: Apache-2.0, 347 stars, not archived or a fork, last commit 2026-09-26 (active). The phrase 'production-ready' does not appear on sievecache.com; the site lists adopters, so stars_or_usage was reworded.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://junchengyang.com/publication/nsdi24-SIEVE.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/cacheMon/NSDI24-SIEVE>
  - <https://sievecache.com/>
  - <https://cachemon.github.io/SIEVE-website/>
- **Sources the enricher read:**
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/Sieve.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/include/libCacheSim/cacheObj.h>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/doc/API.md>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/doc/install.md>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/CMakeLists.txt>
  - <https://github.com/1a1a11a/libCacheSim/commits/develop/libCacheSim/cache/eviction/Sieve.c>
  - <https://github.com/1a1a11a/libCacheSim/issues?q=sieve>
  - <https://junchengyang.com/publication/nsdi24-SIEVE.pdf>
  - <https://github.com/Thesys-lab/cachelib-sosp23>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/MMSieve.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/MMSieve-inl.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/datastruct/SieveList.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/datastruct/SieveList-inl.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/pull/1>
  - <https://github.com/cacheMon/NSDI24-SIEVE>
  - <https://sievecache.com/>
  - <https://cachemon.github.io/SIEVE-website/>
  - <https://github.com/kassane/sieve-cache-cpp>
  - <https://github.com/kassane/sieve-cache-cpp/blob/main/include/sieve.hpp>
  - <https://github.com/facebook/CacheLib>
  - <https://github.com/facebook/CacheLib/issues?q=sieve>
  - <https://hn.algolia.com/api/v1/search?query=SIEVE%20cache%20eviction&tags=story>
  - <https://hn.algolia.com/api/v1/items/38850202>
  - <https://news.ycombinator.com/item?id=38850202>
  - <https://brooker.co.za/blog/2023/12/15/sieve.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:sieve`) · [data/wave6/enrich/raw/paper_sieve.json](../../../data/wave6/enrich/raw/paper_sieve.json) (enrichment confidence 0.85)

</details>
