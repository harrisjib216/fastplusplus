# GL-Cache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Learned eviction (XGBoost over write-time object groups): higher hit ratio than LRU, slower than LRU, 228x faster than LRB.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | Against LRU the win is hit ratio, not throughput. In the Segcache-based prototype, GL-Cache has the highest hit ratio, up to 40% above the best baseline, while Cachelib's throughput-optimized LRU has the lowest hit ratio of all baselines, at throughput similar to Cachelib and Segcache. In the micro-implementation, LRU improves FIFO's hit ratio only by single-digit percent for the median trace, while GL-Cache improves it much more. On throughput, GL-Cache-E is 228x faster than LRB on average (GL-Cache-T 586x) at the small cache size, and 64% faster than the fastest other learned cache (GL-Cache-T 3x). GL-Cache is not faster than LRU itself: the paper says LRU runs close to FIFO throughput, and GL-Cache-E reaches almost half of FIFO's throughput on the Wikimedia trace. |
| **Workload** | 118 production traces (103 CloudPhysics block I/O, 14 MSR block I/O, 1 Wikimedia CDN) replayed in a closed loop against a local cache, measuring hit ratio and throughput. Two setups: a prototype built on Pelikan's Segcache, compared against Cachelib (LRU), Segcache, TinyLFU and LHD; and a storage-oblivious C micro-implementation on libCacheSim, compared against FIFO, LRU, size-aware Belady, LHD, LRB and Cacheus. |
| **Metric** | throughput |
| **Hardware** | Micro-implementation: CloudLab Utah m510 nodes, Intel Xeon D-1548, 64GB ECC DDR4. Prototype: CloudLab Clemson c6420 nodes, Intel Xeon Gold 6142, 384GB DRAM. |
| **Adoption** | 347 stars (libCacheSim; requires build flag -DENABLE_GLCACHE=ON) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/1a1a11a/libCacheSim) · [benchmark](https://junchengyang.com/publication/fast23-glcache.pdf) |

## Verdict

The FAST'23 paper replays 118 production traces (103 CloudPhysics and 14 MSR block-I/O traces, plus 1 Wikimedia CDN trace) in a closed loop. In the libCacheSim micro-implementation (CloudLab m510, Xeon D-1548; compiler and flags not stated), GL-Cache raises hit ratio well above LRU's single-digit gain over FIFO but runs slower than LRU, and its throughput wins (228x/586x over LRB, 64% over the fastest other learned cache) are against learned caches, not LRU. In the Segcache-based Rust prototype (CloudLab c6420, Xeon Gold 6142, one CloudPhysics trace, release profile opt-level 3 with LTO), it gets up to 40% higher hit ratio than the best baseline, at throughput similar to Cachelib's throughput-optimized LRU and to Segcache.

## Use it when

- Simulating or evaluating eviction policies on block-I/O or CDN traces in libCacheSim, where hit ratio matters more than CPU per request (in the paper, LRU and Cacheus gained only single-digit % over FIFO on the median trace; GL-Cache gained much more)
- You want a learned eviction policy but cannot afford LRB: GL-Cache-E is 228x faster than LRB on average at the small cache size, GL-Cache-T 586x, with a 7% higher mean hit ratio
- Segment or log-structured caches (Segcache-style) where evicting whole segments is natural: on one CloudPhysics trace the prototype raised hit ratio by 60% over plain Segcache at 8 GB
- Variable-size objects and workloads whose mix of recency, frequency and size changes with cache size (the model re-weights features per trace and per cache size)
- Traces with real timestamps covering several days, since training uses wall-clock intervals (first model after one day of trace time, then daily retraining)

## Skip it when

- If you need more requests per second than LRU gives: in the micro-implementation LRU runs close to FIFO, while GL-Cache runs at 0.3-0.8x FIFO (paper Table 1), and GL-Cache-E reaches only 2.55-4.20 MQPS against FIFO's 7.62-9.68 on the Wikimedia trace
- Short traces or ones without meaningful timestamps: until the first model is trained (one day of trace time) it evicts segments in plain FIFO order
- As a production in-process cache: the libCacheSim module is a metadata-only simulator policy with no locking and no value storage, and the Rust prototype is a research benchmark frozen since May 2023
- Builds that cannot take on an XGBoost dependency or an opt-in build flag: GLCache compiles only with -DENABLE_GLCACHE=ON, CI never builds or tests it, and XGBoost installs have broken on macOS (issue #180)
- Latency-sensitive paths: libCacheSim calls train() synchronously inside get() (10-50 ms per training in the paper) and runs inference inside eviction (0.4-3 ms), and each group eviction removes hundreds to thousands of objects at once

## How it is fast

It uses group-level learning. Objects are grouped by write time into fixed-size segments, laid out like a log as in Segcache. A gradient-boosted tree model (XGBoost, regression with squared-error loss, retrained from scratch once a day) predicts each group's utility, defined as the sum over its objects of 1/(time to next access x size), from 6-7 cheap group features: age, mean object size, hits, active objects, and the request rate, miss ratio and write rate when the group was created. One inference ranks all groups and is reused until a fraction F_eviction (2-10%) of them has been evicted. Each eviction merges the lowest-utility group with its N_merge-1 neighbours in write time and keeps only the best objects, scored by 1/(size x age). Per-object metadata is about 5 bytes (a 4-byte last-access time plus under 1 byte of amortized group features), against 16 for LRU's list pointers and 189-192 for LRB. A hit only updates the access time, plus the utility for groups sampled for training.

## Compared with alternatives

Pick GL-Cache over LRB when you want learned eviction without LRB's per-object cost: it is 228-586x faster with a similar or higher hit ratio. Pick it over LHD or Cacheus when hit ratio on diverse block traces matters: up to 37.8% above LHD, and 60% higher on the median MSR trace at the small cache size. Pick S3-FIFO or SIEVE (same repo) instead when you need throughput and multi-threaded scaling beyond LRU and no ML dependency.

## Integration

| | |
|---|---|
| **Form** | shared lib (the glcache C module inside libCacheSim, built only with -DENABLE_GLCACHE=ON; BUILD_SHARED_LIBS defaults to ON) |
| **Dependencies** | XGBoost C API (find_package(xgboost) REQUIRED when enabled), glib, zstd, tcmalloc (per README), CMake; the Rust prototype uses a fork of rust-xgboost (1a1a11a/rust-xgboost) and forks of Twitter's rustcommon |
| **Minimum toolchain** | CMake 3.12+ with a C compiler (C standard not stated; C++17 set for libCacheSim's C++ parts); prototype: Rust 2021 edition |
| **Platforms** | Linux and macOS (libCacheSim CI builds both, but without GLCache; PR #280 in July 2025 fixed compiling GL-Cache on macOS) |
| **Thread safety** | Not documented. The GLCache sources have no locks, keep some static state, and train XGBoost with nthread=1 inside the request path, so use one cache instance per thread. |
| **Drop-in for the baseline** | partial — inside libCacheSim it swaps for the `lru` policy by name through the same cache_t interface, but it is a simulator policy with no value storage, so no library can replace an application's LRU cache with it |

## Gotchas

- libCacheSim's defaults (segment-size=100, n-merge=2, rank-intvl=0.02, retrain-intvl=86400) match neither paper configuration (GL-Cache-E: 60 objects/2/0.02; GL-Cache-T: 200/5/0.1). Set parameters explicitly to reproduce the paper.
- The code has drifted from the paper: the GLCache README says it retrains every two days but the code default is one day, and libCacheSim uses 6 features, dropping write rate as redundant, where the paper lists 7. It runs 20 boosting rounds; the Rust prototype runs 8.
- Bad parameters: an unknown key makes the parser call exit(1), and the range checks are assert() calls, which disappear in NDEBUG builds.
- The artifact's license is unclear: GitHub detects no license for Thesys-lab/fast23-GLCache, its README says Apache-2.0, and micro-implementation/LICENSE is GPL-3.0. Use the libCacheSim copy, which is Apache-2.0 (relicensed in PR #324 on 2026-09-13).

## Known shortcomings

- The 64% throughput gain is over the fastest other learned cache (vs LRB it is 228x); against LRU it wins hit ratio only and is slower on throughput; not better than Belady. Split hardware across two testbeds; the paper artifact repo (Thesys-lab/fast23-GLCache) has no licence (verifier downgrade).
- Beats LRU on hit ratio only; throughput is below LRU (0.3-0.8x FIFO; Wikimedia 2.5-4.2 vs FIFO 7.6-9.7 MQPS). Speed wins are only against other learned caches (228x/586x vs LRB). The libCacheSim module is a metadata-only simulation policy, opt-in (-DENABLE_GLCACHE=ON, needs XGBoost), never built in CI, no locks.
- Training runs synchronously inside get() (10-50 ms) and inference inside evict; behaves as plain FIFO until the first model (needs one day of trace timestamps). Defaults differ from the paper's configurations; README says retrain every 2 days, code every 1; 6 features vs the paper's 7. Artifact license is muddled (none detected, README says Apache-2.0, micro-impl/LICENSE is GPL-3.0); the libCacheSim copy was relicensed Apache-2.0 on 2026-09-13. Bad parameters exit(1); range checks are asserts.

## Caveats and trade-offs

Against LRU, GL-Cache wins on hit ratio and is not faster: it runs below LRU/FIFO throughput, so the record's metric 'throughput' does not describe the LRU comparison. The 64% throughput figure is against the fastest other learned cache, not LRB, and the LRB gap is 228x/586x. GL-Cache does not beat size-aware Belady, which is an oracle. The paper's own artifact is github.com/Thesys-lab/fast23-GLCache, which has no license file and was last committed 2023-05-12. The libCacheSim copy is Apache-2.0 but opt-in (-DENABLE_GLCACHE=ON) and depends on XGBoost. Compiler and flags are not stated.

Batches evictions over object groups instead of single objects, trading some eviction precision for far lower learning/inference overhead than object-level learned caches (e.g. LRB)

## Maintenance

libCacheSim is actively maintained (last commit 2026-09-26, Apache-2.0, 347 stars), and the GLCache sources were last touched 2026-09-13. The module is still opt-in, untested in CI and simulator-only, and the paper's Thesys-lab artifact has been frozen since 2023-05-12.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed FAST'23 paper that evaluates GL-Cache against LRU (plain LRU in the libCacheSim micro-implementation, Cachelib's LRU in the prototype) on 118 production traces. The code is public and CPU models are stated, but compiler and flags are not, so it falls short of A.
- **Verifier notes:** The record misattributed the 64% throughput gain to LRB (the paper says 228x vs LRB) and wrongly said GL-Cache beats size-aware Belady. 'metric' should arguably be hit ratio (other), but that field is not correctable here. Metadata confirmed via gh: libCacheSim Apache-2.0, 347 stars, last commit 2026-09-26, GLCache sources present under libCacheSim/cache/eviction/GLCache with the ENABLE_GLCACHE CMake option. The orchestrator may prefer the Thesys-lab/fast23-GLCache artifact repo as a secondary link.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://junchengyang.com/publication/fast23-glcache.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/Thesys-lab/fast23-glcache>
- **Sources the enricher read:**
  - <https://junchengyang.com/publication/fast23-glcache.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/README.md>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/CMakeLists.txt>
  - <https://github.com/1a1a11a/libCacheSim/tree/develop/libCacheSim/cache/eviction/GLCache>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/README>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/GLCache.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/GLCacheInternal.h>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/const.h>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/init.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/train.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/inference.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/eviction.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/segSel.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/GLCache/dataPrep.c>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/test/test_glcache.c>
  - <https://github.com/1a1a11a/libCacheSim/tree/develop/.github/workflows>
  - <https://github.com/1a1a11a/libCacheSim/commits/develop/libCacheSim/cache/eviction/GLCache>
  - <https://github.com/1a1a11a/libCacheSim/issues/41>
  - <https://github.com/1a1a11a/libCacheSim/issues/42>
  - <https://github.com/1a1a11a/libCacheSim/issues/180>
  - <https://github.com/Thesys-lab/fast23-GLCache>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/micro-implementation/README.md>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/micro-implementation/LICENSE>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/prototype/README.md>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/prototype/Cargo.toml>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/prototype/src/l2cache/Cargo.toml>
  - <https://github.com/Thesys-lab/fast23-GLCache/blob/master/prototype/src/l2cache/src/learning/learner.rs>
  - <https://hn.algolia.com/api/v1/search?query=GL-Cache%20group-level%20learning&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:gl-cache`) · [data/wave6/enrich/raw/paper_gl_cache.json](../../../data/wave6/enrich/raw/paper_gl_cache.json) (enrichment confidence 0.8)

</details>
