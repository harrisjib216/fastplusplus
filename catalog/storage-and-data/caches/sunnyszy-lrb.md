# LRB (Learning Relaxed Belady) / webcachesim2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> ML (LightGBM) CDN cache-eviction policy approximating relaxed Belady; cuts simulated WAN traffic 4-25% vs Bloom-filter LRU.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | Simulations on 6 production CDN traces: LRB reduces WAN traffic by 4-25% vs B-LRU (the LRU-with-Bloom-filter-admission production CDN design), and by over 13% on average across cache sizes. It is robust across traces where LRU4, LFUDA, TinyLFU and LeCaR each win only on some. Prototype, Wikipedia trace, 1TB flash cache, days 12-14: LRB cuts average WAN bandwidth by 44% and p95 bandwidth by 43% vs unmodified Apache Traffic Server 8.0.3, which the paper says approximates FIFO eviction, not LRU. |
| **Workload** | Simulation (webcachesim2) replaying 6 production CDN traces (Wikipedia 14-day plus 5 from two other CDNs) at a range of cache sizes vs B-LRU, LRU, LRU4, LFUDA, TinyLFU, LeCaR and others. Also a CDN flash-cache prototype built on Apache Traffic Server 8.0.3, replaying the Wikipedia trace with a 1TB cache. |
| **Metric** | other |
| **Hardware** | 3x Google Cloud n1-standard-64 VMs (64 vCPUs, 240GB DRAM each) acting as client/proxy/origin, 8x375GB local NVMe combined via software RAID |
| **Adoption** | 85 stars (companion prototype repo sunnyszy/lrb-prototype has 11 stars) |
| **Last commit** | 2023-01-20 |
| **Links** | [repository](https://github.com/sunnyszy/lrb) · [benchmark](https://www.usenix.org/system/files/nsdi20-paper-song.pdf) |

## Verdict

In the authors' webcachesim2 simulations of six production CDN traces (Wikipedia plus five from two anonymous CDNs, 64 GB-4 TB caches, metadata subtracted from cache size), LRB cut WAN traffic 4-25% vs B-LRU (LRU with Bloom-filter admission), by over 13% on average. The 44% average and 43% p95 bandwidth cuts come from the ATS 8.0.3 prototype with a 1 TB NVMe cache on three GCP n1-standard-64 VMs, compared with unmodified ATS, which the paper says approximates FIFO rather than LRU; throughput was tied (11.72 vs 11.66 Gbps), peak CPU rose from 9% to 16%, and the CPU model, compiler and flags are not stated.

## Use it when

- Large flash CDN or object caches (the paper evaluates 64 GB to 4 TB, with mean object sizes of 33-644 KB) where WAN egress or byte miss ratio costs more than CPU. The prototype's peak CPU rose from 9% to 16%.
- Workloads where the best heuristic changes from trace to trace. In the paper, LRU4 wins on Wikipedia but is among the worst elsewhere, and TinyLFU and LFUDA each win only on some traces. LRB had the lowest byte miss ratio in all 33 trace/size combinations.
- Moderate eviction rates. Each eviction runs a LightGBM batch prediction: the paper puts it at 30 us for 64 candidates, and GL-Cache measured about 200 us per eviction on one core, which caps it near 5,000 evictions/s.
- Research: comparing a new eviction policy against LRB and around 20 baselines (B-LRU, LFUDA, S4LRU, LeCaR, LHD, AdaptSize, Belady) in the paper's own simulator, on the released 14-day Wikipedia trace (2.8B requests).
- You can spare a validation prefix of the trace (the paper uses the first 20%) plus a MongoDB-backed parallel search to tune memory_window for each cache size.

## Skip it when

- DRAM or key-value caches with high request rates. On the Wikimedia trace, GL-Cache (FAST'23) measured LRB at 0.01-0.07 MQPS against 7.6-9.7 MQPS for FIFO, and reported a 775x slowdown vs LRU.
- Small objects or tight metadata budgets. Per-object metadata grows with request history, from 25 B for single-request objects up to 214 B (paper Table 3), against 16 B of pointers for LRU. It stayed under 3% of cache size only because CDN objects are large.
- Block-I/O-style workloads. Across 118 traces, GL-Cache found LRB gave the smallest hit-ratio gain over FIFO among LRB, LHD and GL-Cache-E, and GL-Cache improved on LRB's hit ratio by 7% on average, up to 87%.
- When you need a library replacement for an LRU container. There are no values and no get/put API, the dependency stack is heavy (LightGBM, Boost, mongo-c/cxx drivers, libbf, libprocps), and the install targets Ubuntu 18.04.
- When you need a maintained dependency. The last commit was 2023-01-20, known simulator bugs are still open (#12 S4LRU size accounting, #25 LHD oversized request), and the latest issue (#29, March 2024) has no reply.

## How it is fast

It does not make eviction cheaper in CPU terms; it lowers the miss ratio, and that cuts WAN bandwidth. The relaxed-Belady idea: instead of finding the object requested farthest in the future (Belady's MIN), evict any object whose next request falls beyond a 'Belady boundary'. So LRB samples 64 cached objects at random and predicts log(time-to-next-request) for each with a LightGBM gradient-boosted-tree regressor (32 iterations, 32 leaves, L2 loss), then evicts the one predicted farthest. Features are 32 inter-request deltas, 10 exponentially decayed counters, object size and optional categorical fields. Labels come from sampled objects inside a sliding memory window, and the model retrains every 128K labeled samples.

## Compared with alternatives

Pick LRB over LHD, SIEVE or W-TinyLFU only for large flash CDN caches, where the bytes it saves on the WAN outweigh roughly 100x lower eviction throughput and up to about 200 B of metadata per object. GL-Cache measured TinyLFU and LHD far faster than LRB, and those simple policies suit DRAM caches better. To simulate LRB alongside those policies, libCacheSim (the SIEVE entry) ships a maintained LRB port (-DENABLE_LRB=ON) that is easier to build than this repo.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | LightGBM, sparsepp, libbf, mongo-c-driver and mongo-cxx-driver (all pinned as sunnyszy fork submodules), fast-cpp-csv-parser, Boost and libprocps. OpenJDK 8 is needed only for the Adaptive-TinyLFU baseline. Memory-window tuning also needs pywebcachesim (Python), GNU parallel and MongoDB. |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17) and CMake 3.2.2+. Documented only on Ubuntu 18 and the ubuntu:18.04 Docker image; the GCC version is not documented. LRBCache::rank() uses variable-length stack arrays, a GCC/Clang extension that is not standard C++. |
| **Platforms** | Linux x86-64 (Ubuntu 18.04 per INSTALL.md and the Dockerfile; it links libprocps). Other OSes and architectures are not documented. |
| **Thread safety** | The simulator class LRBCache is single-threaded and keeps its state (current_seq, memory_window, EDC tables) in namespace-level globals, so two instances in one process share state. The ParallelLRB wrapper behind Interface allows concurrent admit/lookup through a 64-shard shared_mutex size map. A 4096-slot Boost lock-free op queue is drained by one background thread, and training runs on a separate thread. Callers busy-spin when the queue is full. |
| **Drop-in for the baseline** | partial: it replaces the eviction and index policy of an existing cache through key/size admit/lookup (the paper's ATS changes outside the library are under 100 lines). It is not a drop-in for an LRU container: it stores no values and needs memory_window tuned per trace and cache size. |

## Gotchas

- memory_window matters a lot and has to be tuned for each trace and cache size. The code default is 67,108,864; the README's Wikipedia values run from 58.7M at 64 GB to 671M at 1 TB. Tuning on the full trace (LRB-OPT) gained another 1-4%.
- Logical time is a uint32 request counter (`uint32_t current_seq = -1`) and metadata positions are 31-bit bitfields, so traces longer than about 4.29B requests wrap. The paper's largest trace is 2.8B requests.
- It evicts plain LRU until the first model is trained (128K labeled samples) and whenever the LRU tail is older than memory_window. LightGBM inference defaults to 4 threads per prediction; a code comment says 1 thread is 2-3x slower.
- The default objective is byte miss ratio; object miss ratio needs --objective=object_miss_ratio. The trace sanity check aborts if a key's size changes (issue #15). The paper subtracts metadata from cache size, which the simulator exposes as the is_metadata_in_cache_size flag.

## Known shortcomings

- The 44%/43% WAN-bandwidth gains are against Apache Traffic Server's FIFO-like cache, not LRU; against LRU-family policies the gain is 4-25% in simulation. Fork of dasebe/webcachesim; last commit 2023-01 (verifier downgrade).
- The win is miss ratio (WAN bytes), not CPU: the 44% cut is vs ATS (about FIFO); vs the LRU family it is 4-25% in simulation. GL-Cache (FAST'23) measured LRB at 0.01-0.07 MQPS vs FIFO's 7.6-9.7 on a Wikimedia trace (about 775x slower than LRU, \~200 us per eviction) with the smallest hit gain across 118 traces.
- Metadata is 25-214 B per object; memory_window must be tuned per trace and cache size; the uint32 request clock wraps after 4.29B requests. Heavy dependencies (LightGBM, MongoDB drivers, Boost, libprocps), Ubuntu 18 only, uses VLAs, globals shared across LRBCache instances. Abandoned since 2023-01; libCacheSim has a maintained port (-DENABLE_LRB=ON).

## Caveats and trade-offs

The paper's prototype baseline, unmodified ATS, approximates FIFO eviction, not LRU. Against LRU-family baselines the win is the simulated 4-25% WAN-traffic reduction vs B-LRU. Raw throughput is essentially tied (LRB 11.72 vs ATS 11.66 Gbps), and LRB uses more peak CPU (16% vs 9%); the win is in bandwidth and miss ratio. The CPU model and compiler/flags are not stated. The repo is a GitHub fork of dasebe/webcachesim; the ATS prototype is in a separate repo, sunnyszy/lrb-prototype (Apache-2.0).

Uses an online-trained ML model (\~30us per inference) for eviction scoring, adding CPU overhead versus plain LRU (paper measures peak CPU 16% for LRB vs 9% for ATS at max throughput); needs a validation/warmup trace section to tune hyperparameters

## Maintenance

Abandoned BSD-2-Clause research code (last default-branch commit 2023-01-20). It works as a simulator through the sunnyszy/webcachesim Docker image, but embedding it means carrying LightGBM and the MongoDB drivers; libCacheSim's actively maintained port is the easier way to use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'20 paper. The simulations compare LRB against B-LRU, LRU, LFUDA, TinyLFU, LeCaR and others, and the prototype is compared with unmodified ATS. Code is public (webcachesim2 plus lrb-prototype), but only the VM type is given (no CPU model, compiler or flags), so it is not A. Tier stays B; the verdict is a downgrade because the claim misattributes the 44% win to an LRU baseline.
- **Verifier notes:** The 44%/43% and 11.72/11.66 Gbps numbers are on the page, but the record wrongly calls ATS LRU-based (the paper says it approximates FIFO). The default branch's last commit is 2023-01-20; 2023-12-18 is only pushed_at. That is more than 3 years ago, so the repo is abandoned. is_fork_of is set to dasebe/webcachesim.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `maintenance_status`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/nsdi20-paper-song.pdf>
  - <https://github.com/sunnyszy/lrb>
  - <https://github.com/sunnyszy/lrb-prototype>
- **Sources the enricher read:**
  - <https://github.com/sunnyszy/lrb>
  - <https://github.com/sunnyszy/lrb/blob/master/INSTALL.md>
  - <https://github.com/sunnyszy/lrb/blob/master/LRB_WINDOW_TUNING.md>
  - <https://github.com/sunnyszy/lrb/blob/master/CMakeLists.txt>
  - <https://github.com/sunnyszy/lrb/blob/master/src/CMakeLists.txt>
  - <https://github.com/sunnyszy/lrb/blob/master/scripts/install.sh>
  - <https://github.com/sunnyszy/lrb/blob/master/.gitmodules>
  - <https://github.com/sunnyszy/lrb/blob/master/docker/Dockerfile>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/caches/lrb.h>
  - <https://github.com/sunnyszy/lrb/blob/master/src/caches/lrb.cpp>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/cache.h>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/api.h>
  - <https://github.com/sunnyszy/lrb/blob/master/src/api.cpp>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/request.h>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/parallel_cache.h>
  - <https://github.com/sunnyszy/lrb/blob/master/include/webcachesim/caches/parallel_lrb.h>
  - <https://github.com/sunnyszy/lrb/issues>
  - <https://github.com/sunnyszy/lrb/issues/5>
  - <https://github.com/sunnyszy/lrb/issues/12>
  - <https://github.com/sunnyszy/lrb/issues/15>
  - <https://github.com/sunnyszy/lrb/issues/17>
  - <https://github.com/sunnyszy/lrb/issues/21>
  - <https://github.com/sunnyszy/lrb/issues/24>
  - <https://github.com/sunnyszy/lrb/issues/25>
  - <https://github.com/sunnyszy/lrb/commits/master>
  - <https://github.com/sunnyszy/lrb-prototype>
  - <https://github.com/sunnyszy/lrb-prototype/blob/master/INSTALL.md>
  - <https://www.usenix.org/system/files/nsdi20-paper-song.pdf>
  - <https://www.usenix.org/system/files/fast23-yang.pdf>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/LRB/lrb.h>
  - <https://hn.algolia.com/api/v1/search?query=%22Learning%20Relaxed%20Belady%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/sunnyszy/lrb`) · [data/wave6/enrich/raw/github_com_sunnyszy_lrb.json](../../../data/wave6/enrich/raw/github_com_sunnyszy_lrb.json) (enrichment confidence 0.8)

</details>
