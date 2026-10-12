# S3-FIFO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> SOSP'23 three-FIFO-queue eviction policy: lower miss ratios than LRU, and over 6x CacheLib LRU's throughput at 16 threads.

| | |
|---|---|
| **Beats** | LRU (Meta CacheLib's optimized LRU; also CacheLib's optimized 2Q and TinyLFU, plus Segcache) |
| **Claimed result** | S3-FIFO achieves more than 6x higher throughput than the highly-optimized LRU in Meta's CacheLib with 16 threads, at both small and large cache sizes (synthetic Zipf trace). The throughput gap is larger still vs CacheLib's optimized 2Q and TinyLFU. Separately, in libCacheSim simulation over 6594 traces from 14 datasets, S3-FIFO has lower miss ratios than state-of-the-art algorithms and the lowest mean miss ratio on 10 of the 14 datasets. |
| **Workload** | Throughput: an S3-FIFO prototype in Meta CacheLib replays only a synthetic Zipf (alpha=1.0) trace. The trace is 100\*n million requests over n million 4KB objects (n = thread count), run at 1-16 threads with a large cache (LRU miss ratio 0.02) and a small one (0.21). Miss ratio: libCacheSim simulation over 6594 production traces from 14 datasets (MSR, FIU, CloudPhysics, CDN1/2, Tencent, Wikimedia, Alibaba, Twitter, Meta KV/CDN, ...). |
| **Metric** | throughput |
| **Hardware** | CloudLab Clemson c6420 nodes for the prototype (the paper does not name the CPU model). Turbo boost off, one thread pinned per core, all memory allocated on the same NUMA node with numactl. |
| **Compiler and flags** | Artifact build script (Thesys-lab/cachelib-sosp23 mybench/build.sh) uses CMake build type RelWithDebInfo with Ninja; compiler not named |
| **Adoption** | 347 stars (1a1a11a/libCacheSim, simulator home of S3FIFO.c); artifact repo Thesys-lab/sosp23-s3fifo 145 stars; CacheLib prototype in Thesys-lab/cachelib-sosp23 |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/1a1a11a/libCacheSim) · [benchmark](https://junchengyang.com/publication/sosp23-s3fifo.pdf) |

## Verdict

Throughput was measured with the authors' S3-FIFO container in a 2023 CacheLib fork (linked lists for S and M, hash table for the ghost). It replayed a synthetic Zipf(1.0) trace of 100·n million requests over n million 4 KB objects in a closed loop, filling misses from pre-generated values. On CloudLab c6420 nodes (two 16-core Xeon Gold 6142 at 2.6 GHz per CloudLab's docs; turbo off, threads pinned, memory bound to one NUMA node) it exceeded 6x the throughput of CacheLib's optimized LRU at 16 threads, at LRU miss ratios of both 0.02 and 0.21. The build was RelWithDebInfo; the compiler is not named. Miss ratios come from libCacheSim simulation over 6594 traces, ignoring object size, against the lab's own reimplementations of the baselines (for example, W-TinyLFU without a doorkeeper or hill climbing). There S3-FIFO had the best mean on 10 of 14 datasets at a cache of 10% of the footprint and on 7 of 14 at 0.1%.

## Use it when

- Web, key-value and CDN object caches with skewed (Zipf-like) popularity and many one-hit wonders. At a cache size of 10% of the footprint, the paper finds S3-FIFO best by mean miss ratio on 10 of 14 datasets, and the author says it suits web workloads best.
- Read-heavy, many-core in-memory caches where LRU's promote-on-hit lock is the bottleneck. A hit writes only a 2-bit counter, and the CacheLib prototype beat CacheLib's optimized LRU by more than 6x at 16 threads.
- Flash caches that need an admission filter: keep S and the ghost in DRAM and write only objects hit twice to a FIFO flash tier. On the Wikimedia and Tencent Photo CDN traces this gave both fewer flash writes and a lower miss ratio than probabilistic admission or Flashield, even with DRAM at 0.1% of the cache size.
- Replacing LRU in a slab-based cache when you want one static knob. Per the paper, miss ratios change little for most traces with S anywhere from 5% to 20% of the cache.
- Evaluating candidate policies on your own traces first: libCacheSim runs s3fifo next to about 30 other policies (LRU, ARC, LIRS, W-TinyLFU, SIEVE...) in one command.

## Skip it when

- Database, search, analytics or old block workloads with loops or large scans. On the ARC DS1 and S3 traces, the author concedes that W-TinyLFU beats S3-FIFO. The Otter maintainer measured a 'quite serious' loss on DS1, and Caffeine's author calls its results across broader workloads 'great, good, bad, awful'.
- Workloads where most objects are requested exactly twice, with the second request arriving after the object has left S. The paper names this as its adversarial pattern: the second request becomes a miss, which matters most for small caches (thousands of objects).
- When you need a ready library from the authors. libCacheSim's version is simulation-only (ids and sizes, no values, glib dependency), and the CacheLib prototype is a research fork last pushed in December 2023. Upstream facebook/CacheLib ships no S3-FIFO container.
- When multi-core speed is the main goal of a general-purpose library. Otter's author found that the paper's lock-free-queue design lost to BP-Wrapper caches (Ristretto, Theine) and rewrote Otter around BP-Wrapper. Otter v2.0.0 (June 2025) then replaced S3-FIFO with adaptive W-TinyLFU, and Caffeine's author reports close to 1B reads/s at 16 threads with a W-TinyLFU design.
- Variable-size objects without slab classes: the paper's evaluation ignored object size. A ring-buffer implementation also wastes space under delete-heavy workloads, because deleted slots are not reused until eviction (paper, Sec. 4.2).

## How it is fast

The algorithm rests on 'quick demotion'. Across 6594 production traces, a median 72% of objects in a window holding 10% of the trace's objects are one-hit wonders, so new objects go into a small FIFO S that takes 10% of the space. When an object reaches the tail of S, it moves to the main FIFO M if it was hit (threshold 2 in libCacheSim); otherwise it is evicted and its id goes into a ghost FIFO G, and a later miss that finds the id in G inserts straight into M. M works like CLOCK/FIFO-reinsertion with a 2-bit counter capped at 3. A cache hit only increments that counter atomically, so it moves no list node and takes no lock, whereas LRU promotion serializes on a lock. Insertion and eviction are queue-tail operations that can be done lock-free. The CacheLib prototype uses atomic doubly-linked lists and an atomic FIFO hash table for the ghost, which the paper says can hold 4-byte fingerprints.

## Compared with alternatives

Pick S3-FIFO over SIEVE (same repo, one queue) when the workload has scans or block-style access: its small queue plus ghost gives scan resistance, which the S3-FIFO paper says SIEVE lacks. Pick it over Caffeine or the W-TinyLFU C++ port when building a web/CDN/KV cache that needs lock-free hits and a single static knob, but keep adaptive W-TinyLFU for mixed database and analytics workloads, where S3-FIFO loses on loop-heavy traces such as DS1.

## Integration

| | |
|---|---|
| **Form** | source-drop (an algorithm; the reference C module is compiled into libCacheSim's CMake library and cachesim binary, and the CacheLib prototype is a templated MM container header inside a CacheLib fork) |
| **Dependencies** | libCacheSim: glib-2.0, argp, Threads, zstd (on by default for compressed traces), optional tcmalloc. CacheLib prototype: CacheLib's full stack, including folly (MPMCQueue, DistributedMutex). |
| **Minimum toolchain** | libCacheSim: CMake 3.12+, a C compiler plus C++17 for its C++ parts, Ninja recommended, Release build by default. CacheLib prototype: CacheLib's contrib/build.sh toolchain, built RelWithDebInfo with Ninja; compiler not stated. |
| **Platforms** | libCacheSim CI runs on ubuntu-latest and macos-latest (clang); Windows not documented. The algorithm itself is portable C. The prototype's build.sh uses apt, so Debian/Ubuntu. |
| **Thread safety** | libCacheSim: not documented. Each S3FIFO cache_t keeps per-call state in its struct (hit_on_ghost, req_local), so use one instance per thread; cachesim parallelizes by running separate caches. The CacheLib prototype records hits by setting a flag with no lock and links and unlinks nodes through atomic lists. |
| **Drop-in for the baseline** | partial — in libCacheSim, 's3fifo' replaces 'lru' by name. In CacheLib, the prototype plugs in where MMLru goes (the MM container interface), but only in the 2023 fork. There is no drop-in LRU-cache library from the authors. |

## Gotchas

- Two versions exist. libCacheSim's 's3fifo' changed in October 2024 to insert new objects into M once S fills, before the first eviction. The SOSP'23 numbers come from the original, now 's3fifov0' (S3FIFOv0.c), so use that name to reproduce the paper.
- Implementations differ from the paper. Algorithm 1 uses a 10% S, a 2-bit counter, promotion when freq &gt; 1, and a ghost as large as M. libCacheSim sizes the ghost in bytes (0.9x cache size). The CacheLib prototype behind the 6x number uses a 5% S (pRatio_ = 0.05) and a single accessed bit, and sizes the ghost to half the object count at first eviction. Otter traced its hit-ratio jumps to ghost sizing.
- libCacheSim will not cache an object whose size is at least the small queue's size (10% of cache bytes): insert returns NULL and can_insert returns false. Tiny caches or very large objects silently get no caching.
- Evicting from M reinserts every tail object with a nonzero counter until it finds one at zero, so an eviction can walk a long run of recently hit objects (worst case O(n); counters capped at 3). Otter v1 advertised an O(1) worst case as a change from the paper's O(n).

## Known shortcomings

- The &gt;6x throughput over CacheLib's optimized LRU at 16 threads comes from a synthetic Zipf 1.0 run only (not the CDN/Twitter/Meta traces); CloudLab c6420 with the CPU unnamed; benchmark code is Thesys-lab/cachelib-sosp23 (RelWithDebInfo). The paper evaluates 6594 traces from 14 datasets (the record's '1559' was wrong).
- Algorithm only: the libCacheSim code is a simulator that stores no values, and the CacheLib prototype is a fork stale since 2023-12 that was never upstreamed. The paper's 6x prototype differs from the paper's algorithm (5% small queue, one access bit, ghost sized to half the object count). libCacheSim's 's3fifo' changed in 2024-10; the paper's numbers correspond to 's3fifov0'.
- Loses on loop/block traces (DS1, S3), where the author concedes W-TinyLFU is better. Otter's lock-free S3-FIFO design lost to BP-Wrapper caches and Otter v2 dropped S3-FIFO; the s3fifo.com adoption list is stale. libCacheSim never caches objects &gt;=10% of the cache; worst-case eviction is O(n).

## Caveats and trade-offs

The throughput numbers come from a single synthetic Zipf(1.0) workload in a modified CacheLib, not from production traces. The miss-ratio results come from simulation. The paper names no CPU model (only CloudLab c6420 nodes) and no compiler, so this stays at tier B. The S3-FIFO simulator code is in libCacheSim (libCacheSim/cache/eviction/S3FIFO.c). The throughput prototype is in a separate CacheLib fork snapshot (Thesys-lab/cachelib-sosp23, Apache-2.0).

Uses three FIFO queues (small, main, ghost) instead of one list; ghost-queue metadata adds memory overhead; small-queue size ratio (S) needs tuning per workload

## Maintenance

libCacheSim is actively maintained (Apache-2.0, 347 stars, pushed 2026-09-26), but it is a simulator, so production use means porting the roughly 500-line policy or adopting a third-party implementation such as quick_cache or TinyUFO. The CacheLib prototype fork has not been updated since December 2023 and never reached upstream, and s3fifo.com's adoption list still names Otter, which dropped S3-FIFO in v2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SOSP'23 paper. It states S3-FIFO in CacheLib reaches &gt;6x the throughput of CacheLib's optimized LRU at 16 threads, with a larger gap vs 2Q and TinyLFU (Sec. 1, Sec. 5.3, Fig. 8). The prototype benchmark code is public (Thesys-lab/cachelib-sosp23 mybench/, CMake RelWithDebInfo), but the paper names only CloudLab c6420 nodes, not a CPU model or compiler, so it is not A.
- **Verifier notes:** The record's '1559 evaluated traces' does not appear in the paper, which says 6594 traces from 14 datasets. The record also said the throughput test replayed CDN/Twitter/Meta traces, but the paper says it used only a synthetic Zipf trace. Both are fixed. gh metadata matches the record: Apache-2.0, 347 stars, last commit 2026-09-26, active (GitHub lists the repo language as C++, while S3FIFO.c is C).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://junchengyang.com/publication/sosp23-s3fifo.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/Thesys-lab/sosp23-s3fifo>
  - <https://raw.githubusercontent.com/Thesys-lab/sosp23-s3fifo/HEAD/README.md>
  - <https://github.com/Thesys-lab/cachelib-sosp23>
  - <https://raw.githubusercontent.com/Thesys-lab/cachelib-sosp23/HEAD/mybench/build.sh>
- **Sources the enricher read:**
  - <https://junchengyang.com/publication/sosp23-s3fifo.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/S3FIFO.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/S3FIFOv0.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/cacheAlgoRegistry.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/bin/cachesim/cache_init.h>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/CMakeLists.txt>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/.github/workflows/build.yml>
  - <https://github.com/1a1a11a/libCacheSim/discussions/20>
  - <https://github.com/1a1a11a/libCacheSim/issues/137>
  - <https://github.com/1a1a11a/libCacheSim/issues/300>
  - <https://github.com/Thesys-lab/sosp23-s3fifo>
  - <https://github.com/Thesys-lab/cachelib-sosp23>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/datastruct/S3FIFOList.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/datastruct/S3FIFOList-inl.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/MMS3FIFO.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/cachelib/allocator/MMS3FIFO-inl.h>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/mybench/build.sh>
  - <https://github.com/Thesys-lab/cachelib-sosp23/blob/main/mybench/run.sh>
  - <https://github.com/facebook/CacheLib>
  - <https://s3fifo.com/>
  - <https://hn.algolia.com/api/v1/search?query=S3-FIFO&tags=story>
  - <https://news.ycombinator.com/item?id=38745070>
  - <https://news.ycombinator.com/item?id=37288320>
  - <https://github.com/Yiling-J/theine-go/issues/29>
  - <https://github.com/maypok86/otter>
  - <https://github.com/maypok86/otter/releases/tag/v2.0.0>
  - <https://github.com/maypok86/otter/releases/tag/v1.0.0>
  - <https://github.com/cloudflare/pingora/tree/main/tinyufo>
  - <https://github.com/arthurprs/quick-cache>
  - <https://github.com/foyer-rs/foyer>
  - <https://docs.cloudlab.us/hardware.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:s3-fifo`) · [data/wave6/enrich/raw/paper_s3_fifo.json](../../../data/wave6/enrich/raw/paper_s3_fifo.json) (enrichment confidence 0.8)

</details>
