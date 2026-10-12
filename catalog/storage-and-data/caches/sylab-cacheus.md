# Cacheus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Python` · `reference (no LICENSE file found in repo)` · 🟡 stale

> Research Python simulator of Cacheus (FAST'21), a learned two-expert page-cache eviction policy that competes with ARC/LIRS/DLIRS on hit rate.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | In paired t-tests over 17,766 simulations, Cacheus C3 (SR-LRU + CR-LFU experts) is distinctly the best algorithm in 47% of workload/cache-size combinations, statistically indistinguishable from the best state-of-the-art algorithm in about 40%, and worse in the remaining 13%. The comparison set is LRU, LFU, ARC, LIRS, LeCaR and DLIRS. The best case is a 38.32% absolute hit-rate difference over ARC (CloudPhysics, cache at 10% of footprint). The worst case is a 15.12% degradation vs DLIRS (MSR, cache at 5% of footprint). |
| **Workload** | 17,766 trace-driven simulations over 329 single-day production block-storage workloads from 5 datasets (FIU, MSR, CloudPhysics, CloudVPS, CloudCache) at 6 cache sizes (0.05%-10% of workload footprint), comparing hit rate against LRU, LFU, ARC, LIRS, LeCaR and DLIRS |
| **Metric** | other |
| **Adoption** | 68 stars |
| **Last commit** | 2023-10-05 |
| **Links** | [repository](https://github.com/sylab/cacheus) · [benchmark](https://www.usenix.org/system/files/fast21-rodriguez.pdf) |

## Verdict

Only simulated hit rate was measured, in Python, with no compiler, hardware or throughput numbers. The study ran 17,766 simulations on 329 one-day block-I/O traces from 5 datasets at 6 cache sizes (0.05%-10% of footprint). In paired t-tests over the paper's 30 workload/cache-size combinations, Cacheus C3 is distinctly best in 47%, indistinguishable from the best of ARC/LIRS/DLIRS/LeCaR in about 40%, and worse in 13%. The extremes are +38.32 absolute hit-rate points vs ARC (CloudPhysics, 10%) and -15.12 vs DLIRS (MSR, 5%). The paper gives no isolated Cacheus-vs-LRU number; LRU appears only in the compared set and the ranking study.

## Use it when

- Reproducing the FAST'21 results, or using Cacheus as a baseline in cache-policy research on block-storage traces (FIU and MSR readers are built in)
- Estimating, before any native implementation, whether a fixed-size page or block cache (buffer cache, SSD or flash cache tier) would gain hit rate from an adaptive recency/frequency policy
- Workloads that shift between scan, churn, LRU-friendly and LFU-friendly phases, with caches small relative to footprint (the paper tests 0.05%-10%)
- When you want LeCaR-style learned eviction without hand-tuning the learning or discount rate
- As a readable reference to port; for reusable code, use libCacheSim's Apache-2.0 C port (Cacheus.c, SR_LRU.c, CR_LFU.c)

## Skip it when

- Any throughput- or latency-sensitive path: it is pure Python with an O(log N) LFU heap update on every hit and no concurrency, and no throughput numbers are published
- Variable-size objects (web, CDN, key-value caches): the simulator counts unit-size 4 KiB pages and the cache size is in pages
- Memory-constrained caches: the paper states about 2N metadata entries (N resident plus N history), and the SIEVE paper (NSDI'24) puts Cacheus per-object metadata at 3.3x LRU's
- Workloads where most objects are requested exactly twice with a gap: the S3-FIFO paper (SOSP'23) names Cacheus among partitioned policies that handle this badly at small cache sizes, and found Cacheus often less competitive than traditional algorithms such as ARC in its broad simulations
- Code reuse in products: the repo has no LICENSE file

## How it is fast

The gain is hit rate, not speed. Following LeCaR, it uses online regret minimization: on each eviction it samples one of two experts by weight, and when a missed key is found in an expert's eviction history (each N/2 entries), that expert's weight is multiplied by exp(-learning_rate). Expert one is SR-LRU (scan-resistant LRU): the cache is split into a reuse partition R and a small scan-resistant partition SR that new keys enter, evictions come only from SR, and the partition sizes adapt when demoted or new items are re-referenced. Expert two is CR-LFU (churn-resistant LFU), an LFU heap that breaks frequency ties by evicting the most recently used key, which pins a stable subset during churn. The learning rate itself is tuned every N requests by stochastic hill climbing and resets after 10 degrading windows, so no hyperparameters are hand-set.

## Compared with alternatives

Pick Cacheus over SIEVE, S3-FIFO and GL-Cache (all in libCacheSim, which also carries a Cacheus port) only when the target is a unit-size block or page storage cache with mixed scan and churn phases, and hit rate matters more than CPU and metadata cost. For throughput, simplicity or web/KV traces, use SIEVE or S3-FIFO. For a production in-process cache, use Caffeine or W-TinyLFU. For variable-size objects, use LHD, AdaptSize or LRB.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | numpy and matplotlib (matplotlib is imported at module level by the Visualizinator that every policy loads); no requirements file or packaging |
| **Minimum toolchain** | Python 3 (README uses python3; exact version not documented) |
| **Platforms** | any (pure Python) |
| **Thread safety** | not documented; single-threaded simulator objects with no locking |
| **Drop-in for the baseline** | partial — within this simulator it exposes the same request(key, ts) interface as the repo's LRU class, so swapping is a config change; it holds no values and is not a drop-in for a real LRU cache |

## Gotchas

- Won't run out of the box: example.config is invalid JSON (trailing comma in the alecar6 block) and doesn't list cacheus, and run_alg.py still calls the constructor and request() with one argument, which raises TypeError for Cacheus
- The code differs from the paper. It starts the learning rate deterministically at sqrt(2 ln 2 / N) rather than a random value in [0.001, 1], and the constructor calls np.random.seed(123), which resets numpy's global RNG for anything else in the process. libCacheSim's port says it follows the paper instead, so results from the two can differ.
- Memory grows with trace length: the learning-rate updater appends to a list on every request, even with visualization turned off
- SR-LRU and CR-LFU are not separate modules. They are inlined in cacheus.py (s = R, q = SR, and the heap's tie-break in Cacheus_Entry.__lt__). Open issue #16 (June 2025, no reply) asks where they are, so readers can mistake the code for plain LRU+LFU.

## Known shortcomings

- 'Best on the majority of workloads' is overstated: the paper has it distinctly best on 47%, tied on \~40% and worse on 13%; the 38.32% is an absolute hit-rate difference vs ARC; Python simulator (verifier downgrade).
- Hit rate only, from a pure-Python simulator; no throughput or hardware, no isolated vs-LRU number. Does not run as shipped (example.config is invalid JSON; run_alg.py raises TypeError for Cacheus). Code differs from the paper (fixed learning-rate init, global np.random.seed(123)); per-request list append grows memory with trace length.
- Metadata is 3.3x LRU's (SIEVE paper); the S3-FIFO paper finds Cacheus often trails ARC-class algorithms. No LICENSE; reuse via the libCacheSim C port (Apache-2.0 since 2026-09). Issue #16 unanswered.

## Caveats and trade-offs

This is a pure trace-driven Python simulation with no throughput, latency or hardware numbers, and the win is in hit rate. The paper isolates no Cacheus-vs-LRU number: its headline statistics are against the stronger ARC/LIRS/DLIRS/LeCaR baselines, and LRU appears only in the compared-algorithm set and the ranking study. The repo has no LICENSE file, so it is reference-only for reuse.

Not uniformly better than every competitor (worst case is a real hit-rate loss vs DLIRS); adaptive combination of multiple experts (ARC/LIRS/LFU-style) adds bookkeeping overhead vs plain LRU; reference Python implementation is a research prototype, not built for production throughput (a C port exists inside libCacheSim)

## Maintenance

Stale research code: cacheus.py last changed in April 2021 (bug fixes) and the repo last changed in October 2023. With no LICENSE it is reference-only; the maintained, Apache-2.0 route is libCacheSim's C port (relicensed September 2026), though that port has open TODOs such as 'this function may not work' in Cacheus_to_evict.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed FAST'21 paper with 17,766 trace-driven simulations. LRU is one of the six algorithms compared, and the quantified Cacheus results are against ARC, LIRS, DLIRS and LeCaR. It is a Python simulation with no compiler or hardware stated, so it cannot reach A.
- **Verifier notes:** The numbers 17,766 / 38.32% / 15.12% are on the page. The record's 'majority of paired t-tests' is overstated: the paper says 47% distinctly best, about 40% tie, 13% worse. The workload was also missing 2 of the 5 datasets. Metadata confirmed: no license (null, and the repo root has no LICENSE file), 68 stars, last commit 2023-10-05 (stale, just under 3 years), Python.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/fast21-rodriguez.pdf>
  - <https://github.com/sylab/cacheus>
- **Sources the enricher read:**
  - <https://github.com/sylab/cacheus>
  - <https://github.com/sylab/cacheus/blob/main/README.md>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/cacheus.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/dequedict.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/heapdict.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/visualizinator.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/pollutionator.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/traces.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/optional_args.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lib/cacheop.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/get_algorithm.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lru.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lfu.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/alecar6.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/arcalecar.py>
  - <https://github.com/sylab/cacheus/blob/main/code/algs/lirsalecar.py>
  - <https://github.com/sylab/cacheus/blob/main/code/run.py>
  - <https://github.com/sylab/cacheus/blob/main/code/run_alg.py>
  - <https://github.com/sylab/cacheus/blob/main/code/example.config>
  - <https://github.com/sylab/cacheus/blob/main/code/visual.config>
  - <https://github.com/sylab/cacheus/commits/main>
  - <https://github.com/sylab/cacheus/issues/16>
  - <https://github.com/sylab/cacheus/issues/11>
  - <https://github.com/sylab/cacheus/issues/9>
  - <https://github.com/sylab/cacheus/issues/6>
  - <https://github.com/sylab/cacheus/issues/5>
  - <https://github.com/sylab/cacheus/issues/13>
  - <https://github.com/sylab/cacheus/issues/15>
  - <https://github.com/sylab/cacheus/pulls?q=is%3Apr>
  - <https://www.usenix.org/system/files/fast21-rodriguez.pdf>
  - <https://github.com/1a1a11a/libCacheSim/blob/HEAD/libCacheSim/cache/eviction/Cacheus.c>
  - <https://jasony.me/publication/sosp23-s3fifo.pdf>
  - <https://www.usenix.org/system/files/nsdi24-zhang-yazhuo.pdf>
  - <https://hn.algolia.com/api/v1/search?query=cacheus&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/sylab/cacheus`) · [data/wave6/enrich/raw/github_com_sylab_cacheus.json](../../../data/wave6/enrich/raw/github_com_sylab_cacheus.json) (enrichment confidence 0.8)

</details>
