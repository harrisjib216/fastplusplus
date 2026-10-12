# CacheLib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Meta's in-process C++ caching engine with an optional SSD tier; the authors report up to 60% more throughput than Memcached.

| | |
|---|---|
| **Beats** | Memcached |
| **Claimed result** | "Across all cache sizes, CacheLib achieves higher throughputs than Memcached, processing up to 60% more requests per second than Memcached" (hit ratios similar, Memcached slightly higher at small sizes, CacheLib higher at large sizes) |
| **Workload** | CacheBench synthetic look-aside cache workload (Facebook's application look-aside pattern): 100 million objects, cache sizes 8-144GB, 32 threads each, both systems configured with LRU eviction; small caches stress eviction (set-heavy), large caches stress LRU-head updates (get-heavy) |
| **Metric** | throughput |
| **Adoption** | 1.6k stars; used to power look-aside, CDN, and flash caches at Facebook (replacing internal Memcached deployments) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/facebook/CacheLib) · [benchmark](https://www.usenix.org/system/files/osdi20-berg.pdf) |

## Verdict

In the authors' OSDI 2020 paper, CacheBench drove CacheLib and an in-process, minimally modified Memcached 1.6.6. Both used LRU eviction and 32 threads, with a 100M-object working set and caches of 8-144 GB. CacheLib served up to 60% more requests per second at similar hit ratios; Figure 12's throughput axis spans 0-2 M ops/s. The run used the 60 s promotion delay, and the paper gives no CPU, compiler or build flags; no independent reproduction was found.

## Use it when

- A many-threaded C++ service (Rust bindings also exist) that needs a large in-process look-aside cache, tens to hundreds of GB, with many cores reading the same hot keys. This is where a Memcached-style global LRU lock becomes the bottleneck. The 60% gain was measured at 32 threads.
- Working sets bigger than DRAM, where an SSD is cheaper capacity. Navy stores objects under 2 KB in a set-associative Small Object Cache and larger objects in a region-based Large Object Cache. Flash admission is probabilistic to limit write wear.
- Services that deploy often and cannot afford a cold cache. Warm restart keeps the DRAM cache in POSIX shared memory across process restarts on the same host.
- Multi-tenant caches that need per-workload memory isolation (pools), automatic slab rebalancing and OOM-aware memory release, rather than one global LRU.
- Evaluating cache hardware or eviction policies against production-like or trace-driven workloads. The CacheBench tool ships in the repo.

## Skip it when

- You want a networked, protocol-compatible replacement for Memcached or Redis. CacheLib has no server, protocol, sharding or replication.
- You are not on Linux, or you want a light build. getdeps.py builds folly, fbthrift, fizz, wangle, boost and more. The build needs C++20 and libnuma, CI runs only on Ubuntu, and a vcpkg port is Linux-only. folly has no stable API, so the whole stack has to be upgraded at matching versions.
- Your values are pointer-rich or not memcpy-safe, or your code base is C. The core allocator stores flat bytes, and the paper says ad-serving teams (nested data) and RocksDB (C-style code versus RAII handles) could not adopt it. The newer ObjectCache only partly addresses this.
- The cache is small or single-threaded. Pools, allocation classes, hash-table sizing and the rebalancer are overkill there, and there is about 32 B of overhead per item plus the bucket array (256 MB for up to 32M items at the recommended bucketsPower 26).
- Your bottleneck is how well the eviction policy scales. The S3-FIFO and SIEVE sibling entries report prototypes that beat CacheLib's own optimized LRU, S3-FIFO by more than 6x at 16 threads.

## How it is fast

The paper credits most of the gain over Memcached to lower lock contention. Each slab class keeps its own LRU, protected by a folly::DistributedMutex. Its lock_combine() does flat combining: the thread holding the lock runs the critical sections that waiting threads have queued. A promotion delay (lruRefreshTime, 60 s by default) moves a hot item to the LRU head at most once per window. An optional tryLockUpdate setting skips the promotion when the lock is busy. The DRAM index is a chained hash table with compressed pointers and lock striping (locksPower). Memory comes from a custom slab allocator with 4 MB slabs and size classes set per workload, and each item carries about 32 B of intrusive metadata (hash-chain hook, LRU hooks, refcount, timestamps).

## Compared with alternatives

Pick CacheLib over Pelikan/Segcache, Dragonfly or Pogocache when the cache lives inside your own C++ service and you need an SSD tier, warm restarts or per-tenant pools. Those siblings are ready-to-run network servers, and Segcache, MemC3 and MICA report much larger multiples over Memcached (close to 8x, almost 3x) for DRAM-only small-object serving. Look at S3-FIFO or SIEVE, or CacheLib's own 2Q/TinyLFU traits, when scaling the eviction policy matters more than features.

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake, built through getdeps.py; installs libcachelib_allocator.so etc. plus headers; templates instantiated per eviction trait) |
| **Dependencies** | folly, fbthrift, fizz, wangle, fmt, glog, gflags, boost, googletest, zlib, zstd, libnuma, sparse-map, xxHash, magic_enum; liburing optional |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20); GCC 10+ or Clang 10+; CMake 3.14+; Python 3.6+ for getdeps.py |
| **Platforms** | Linux only in practice. CI runs Ubuntu on x86-64, and the docs list Ubuntu 18.04-22.04, CentOS 8 and Debian 10/11. macOS and Windows are not supported, and aarch64 is not documented. |
| **Thread safety** | The cache API is thread-safe (README). A handle keeps its item from being evicted, but it does not synchronize concurrent reads and writes to the item's memory, so the user must add a lock (docs). |
| **Drop-in for the baseline** | no |

## Gotchas

- The default hash-table settings are deliberately unoptimized. Call setAccessConfig(expectedItems) or set bucketsPower to about 2x the item count, or find() and insert slow down. This is the FAQ's first answer to 'why is my cache so slow'.
- Warm restart only works if you drain accesses and call shutDown() before the allocator is destroyed. Otherwise the shared-memory segments are deleted. Any RAM or NVM format-version bump drops the cache on upgrade (kCachelibVersion is now 19, but CHANGELOG.md stops at V17).
- With the SSD tier on, find() can return a not-ready handle that blocks when you touch it (use toSemiFuture() to avoid blocking). findToWrite() is always synchronous and invalidates the flash copy. allocate() returns a null handle instead of throwing when it finds no evictable item, for example when items are pinned by outstanding handles.
- Performance depends on configuration and version. The paper notes that dropping the promotion delay from 60 s to 10 s raised the hit ratio but lowered throughput. One user measured 22.2M to 12.7M gets/s between a Dec-2022 commit and v2023.08.21.00 on a 48-thread CacheBench config (issue #257, closed without a public explanation). ThreadSanitizer reports false races because DistributedMutex is not TSAN-annotated (issue #148).

## Known shortcomings

- The 'up to 60% more req/s than Memcached 1.6.6' ran Memcached in-process via CacheBench for 60 s; no CPU/compiler given.
- A library only (no server, no Memcached protocol), so not a drop-in. Heavy build: getdeps pulls folly, fbthrift, fizz and wangle; C++20 and libnuma required; CI Ubuntu only; the unstable folly API means upgrading the whole stack in lockstep. The only evidence is the authors' own paper with no third-party reproduction.
- The hash table is untuned by default; warm restart needs a clean shutDown() and is lost on any format-version bump; flash-tier handles can block. A user reported get throughput dropping from 22.2M to 12.7M ops/s between versions (#257), closed without public explanation. The S3-FIFO and SIEVE papers report beating CacheLib's own LRU.

## Caveats and trade-offs

The benchmark comes from the CacheLib design paper by its own authors (Berg et al., OSDI 2020). CacheBench was extended to drive an in-process version of a minimally changed Memcached v1.6.6, not the networked Memcached server, and both systems used LRU eviction with 32 threads. The comparison uses CacheLib's default T = 60 s, and the paper notes that T = 10 s raises hit ratio at the cost of lower throughput. CacheBench is public in the CacheLib repo, but the evaluation does not state the CPU model or compiler/build flags, so it falls short of tier A. No independent third-party reproduction was found.

Embedded in-process C++ library, not a standalone network server like Memcached (must be linked into the application or wrapped in one); larger API surface (DRAM+flash hybrid tiers, pools, warm restart); higher throughput attributed to reduced lock contention (flat combining on the LRU list head) rather than a fundamentally different algorithm

## Maintenance

Actively maintained by Meta, with weekly vYYYY.MM.DD tags (latest v2026.09.21.00, last commit 2026-09-26) and Apache-2.0 licensing. Using it in practice means building with Meta's getdeps toolchain and upgrading in lockstep with folly/fbthrift, not vendoring a few files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed OSDI 2020 paper (Berg et al.), Section 5.1 and Figure 12, compares CacheLib against Memcached v1.6.6 using CacheBench (which ships in the CacheLib repo) and states 'up to 60% more requests per second than Memcached'. The paper gives no CPU model, compiler or flags for this experiment, so it cannot be A.
- **Verifier notes:** The quoted claim, workload (100M objects, 8-144GB caches, 32 threads, LRU on both) and 'minimally changed Memcached v1.6.6' all match the paper text verbatim. Metadata checked via gh: Apache-2.0, 1,595 stars, not a fork, not archived, last commit 2026-09-26. I only expanded the caveats to cover the in-process Memcached target and the T = 60 s setting.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/osdi20-berg.pdf>
  - <https://github.com/facebook/CacheLib>
- **Sources the enricher read:**
  - <https://github.com/facebook/CacheLib>
  - <https://github.com/facebook/CacheLib/blob/main/README.md>
  - <https://github.com/facebook/CacheLib/blob/main/BENCHMARKS.md>
  - <https://github.com/facebook/CacheLib/blob/main/BUILD.md>
  - <https://github.com/facebook/CacheLib/blob/main/CHANGELOG.md>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/CMakeLists.txt>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/allocator/MMLru.h>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/allocator/CacheAllocator.h>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/allocator/CacheVersion.h>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/allocator/Refcount.h>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/object_cache/ObjectCache.h>
  - <https://github.com/facebook/CacheLib/blob/main/cachelib/rust/Cargo.toml>
  - <https://github.com/facebook/CacheLib/blob/main/.github/workflows/getdeps_linux.yml>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/faq.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/eviction_policy.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/Set_up_a_simple_cache.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/Item_and_Handle.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/Cache_persistence.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/Configure_HashTable.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/HybridCache.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_User_Guides/Configure_HybridCache.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_Architecture_Guide/RAM_cache_indexing_and_eviction.md>
  - <https://github.com/facebook/CacheLib/blob/main/website/docs/installation/installation.md>
  - <https://github.com/facebook/CacheLib/releases>
  - <https://github.com/facebook/CacheLib/issues/90>
  - <https://github.com/facebook/CacheLib/issues/108>
  - <https://github.com/facebook/CacheLib/issues/112>
  - <https://github.com/facebook/CacheLib/issues/148>
  - <https://github.com/facebook/CacheLib/issues/257>
  - <https://www.usenix.org/system/files/osdi20-berg.pdf>
  - <https://hn.algolia.com/api/v1/search?query=cachelib&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/facebook/cachelib`) · [data/wave6/enrich/raw/github_com_facebook_cachelib.json](../../../data/wave6/enrich/raw/github_com_facebook_cachelib.json) (enrichment confidence 0.8)

</details>
