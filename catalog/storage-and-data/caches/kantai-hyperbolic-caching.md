# Hyperbolic Caching

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Research Redis 3.0 fork plus simulator whose cost-aware 'hits over time-in-cache' eviction beats Redis's sampled LRU on miss rate.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | Hyperbolic caching improves end-to-end application throughput by \~5-10% over default Redis (abstract) and lowers miss rates by 10-37% on the NodeJS synthetic workloads, with throughput up to \~14% higher. Example, Fig. 11 (NodeJS over Redis, Dynamic Intro, 5k-object cache): 10.0 vs 11.3 kreq/s and miss rate 0.33 vs 0.27 for default vs HC Redis (+11.6%). Fig. 7 (Django-Wiki, Wikipedia Jan 2008 trace): 21.1 vs 23.7 req/s (+12.3%) for default vs HC. |
| **Workload** | Django-Wiki and NodeJS web applications using a modified Redis (forked at 3.0) as a look-aside cache, replaying Wikipedia (Jan 2008) and synthetic cost-aware workloads; also Memcachier-style trace-driven miss-rate simulation |
| **Metric** | throughput |
| **Hardware** | Rack of servers with Intel Xeon E5620 @ 2.40GHz CPUs |
| **Adoption** | 20 stars |
| **Last commit** | 2017-07-14 |
| **Links** | [repository](https://github.com/kantai/hyperbolic-caching) · [benchmark](https://www.usenix.org/system/files/conference/atc17/atc17-blankstein.pdf) |

## Verdict

Setup: a rack of Intel Xeon E5620 2.40 GHz Ubuntu 14.04 servers, PostgreSQL 9.3 backends, no compiler or flags given. Django-Wiki replaying a 600k Wikipedia trace against a 1 GB cache: HC Redis reached 23.7 vs 21.1 req/s (+12.3%, miss rate 0.637 vs 0.681). A NodeJS look-aside app (5M requests, 10 runs): +3.2% to +13.5% (e.g. Dynamic Intro, 5k objects: 11.3 vs 10.0 kreq/s, miss rate 0.27 vs 0.33). The baseline is 'default' Redis sampled LRU; the runner scripts start it from a 'redis-default' build of the same fork, not stock Redis and not Redis 4.0+ LFU.

## Use it when

- Look-aside web caches where miss cost varies a lot by item and the app can measure it. In the paper's NodeJS lookup-vs-join app, HC-Cost reached 9.4 kreq/s vs 5.0 for plain HC, despite a 57% higher miss rate.
- Backends whose cost shifts for a whole group of keys, e.g. one overloaded replica. HC-Class updates a class's EWMA cost and reprioritizes all its cached items at once.
- Zipf-like, frequency-driven key-value workloads sized for roughly 70-90% hit rates, where Redis's LRU approximation leaves misses behind. NodeJS tests gained 3.2-13.5% throughput.
- Caches with very uneven object sizes (the HC-Size mode). In simulation on Memcachier app traces it 'drastically outperforms LRU'.
- Trying out a new eviction priority function offline. The Python simulator replays Zipf, ARC/SPC, Wikipedia and Memcachier workloads against many policies.

## Skip it when

- Any production Redis deployment. This is an archived fork of Redis 3.0.3 (2015) with none of the later Redis releases, fixes or policies. Redis 4.0+ ships its own allkeys-lfu with counter decay.
- Items read about once before they expire, as in the MSN Decision Service trace. Plain HC missed 0.60 vs 0.55 for LRU. The expiration-aware HC-Expire exists only in the simulator; the Redis patch has no TTL term.
- Noisy per-item costs. On Django-Wiki, HC-Cost gave +0.0% throughput vs +12.3% for plain HC, because render times varied (570 ms mean, 180 ms deviation on one page).
- Cost-free traces where ARC or LFU are options. In simulation HC trailed ARC on the P1-P4 traces and LFU on Viral Search.
- Memory-tight caches. The code adds a uint32 cost to every redisObject, plus a double hit counter in hyperbolic builds; the paper cites two doubles per item.

## How it is fast

Hyperbolic caching (Blankstein, Sen, Freedman, USENIX ATC'17) gives each item the priority n_i / t_i: hits since insertion divided by time since insertion. The priority is computed lazily, only for keys that Redis's existing random-sampling eviction pool draws, so no ordering structure is kept even though priorities decay at per-item rates. Extensions multiply by the per-item cost (HC-Cost), use a per-class exponentially weighted moving average (EWMA) of cost (HC-Class, weight 0.2 in code), divide by byte size (HC-Size), and seed a new item's count from the last evicted priority (beta = 0.1). The throughput gain comes from fewer backend (PostgreSQL) fetches, not faster cache operations.

## Compared with alternatives

Pick it over LHD, SIEVE or LRB when misses differ in backend cost and you want the app to tell a Redis-protocol cache that cost, per item or per class; those policies are cost-oblivious miss-rate optimizers. Garnet, Dragonfly, KeyDB and Pogocache make the server itself faster, while this only changes which keys get evicted. It helps only when backend misses, not cache CPU, limit throughput, and in practice you would port the roughly 380-line priority function rather than run this fork.

## Integration

| | |
|---|---|
| **Form** | source-drop — a patched Redis 3.0.3 server tree (branch cost-cache) built with make.sh; there is no library. The simulator is plain Python scripts. |
| **Dependencies** | Redis 3.0's bundled deps (hiredis, linenoise, Lua) plus libstdc++ (a C++ std::set wrapper is compiled and linked). The benchmarks also need PyPy/NumPy, NodeJS 4.x and PostgreSQL 9.3. |
| **Minimum toolchain** | C99 (-std=c99 -pedantic) plus a C++ compiler; the patch adds -Werror. No compiler version is documented (the paper's servers ran Ubuntu 14.04). |
| **Platforms** | Linux (evaluated on Intel Xeon E5620); other platforms not documented |
| **Thread safety** | Inherits Redis 3.0's single-threaded command loop; the patch adds no threads or locks |
| **Drop-in for the baseline** | partial — plain GET/SET clients work unchanged, but it is a 2015-era Redis 3.0.3. The eviction policy is fixed at compile time and hides behind the allkeys-lru/volatile-lru names. Cost-awareness needs the non-standard SET CX/CC options or SETCOST. |

## Gotchas

- REDIS_LRU_CLOCK_LOGICAL is hard-wired to 1. 'Time' is the count of key lookups, kept in a 24-bit field that wraps every \~16.8M lookups, after which the age of long-resident keys aliases. The same clock applies to the make.sh 'default' build.
- The policy is chosen by make.sh flags (hyper | size-aware | classes). CONFIG still reports allkeys-lru; only `INFO`'s priority_func line shows the real policy. volatile-ttl and random policies are unchanged.
- Costs are uint32 integers; the Django backend sends int(100\*seconds). In class builds, CX without CC is rejected, and class ids must be 1-31.
- Eviction internals change: the pool shrinks from 16 to 4 entries and the shipped confs use maxmemory-samples 32 (the paper says it samples 64). Size-aware builds call rdbSavedObjectLen (rdbSaveObject with a NULL target) on every sampled key, which can be costly for large values.

## Known shortcomings

- This repo is the Python simulator and runners; the Redis C patch lives in kantai/redis-hyperbolic-caching. Last commit 2017-07.
- A 2015 fork of Redis 3.0.3; both repos archived; not production. The priority clock is a 24-bit lookup count that wraps every \~16.8M lookups. Policy is fixed at compile time and still named allkeys-lru; costs need nonstandard SET CX/CC or SETCOST commands.
- Plain HC loses to LRU on an expire-once trace (0.60 vs 0.55 miss rate); HC-Expire exists only in the simulator. Noisy per-item cost gives HC-Cost +0% on Django-Wiki. Baseline is likely the same fork's default build, not stock Redis or Redis 4.0+ LFU; no compiler/flags. Shipped configs use 32 samples (paper says 64); size-aware mode computes object size per sampled key.

## Caveats and trade-offs

This repo is archived. It holds the Python simulator plus the NodeJS and Django benchmark runners (GitHub language: Python), not the Redis patch itself. The paper's 380-line C Redis change (forked at Redis 3.0) lives in a separate repo, github.com/kantai/redis-hyperbolic-caching (BSD-3-Clause, archived, 6 stars, last commit 2017-05-18). Default Redis eviction here means Redis's sampled approximate LRU. The 2021-12-09 date is the archive push, not a commit.

Priority function needs periodic re-scaling/rebalancing as cost or popularity distributions shift; implemented as a \~380-line patch to Redis's existing random-sampling eviction rather than a new data structure, so gains are workload-dependent (competitive with, not always better than, ARC on cost-free workloads)

## Maintenance

Both repos are archived. The simulator was last committed 2017-07-14 and the Redis 3.0.3 fork 2017-05-18. The simulator is MIT; the Redis changes are MIT per their README, while GitHub tags the Redis repo BSD-3-Clause. Treat it as reference code to port into a modern Redis eviction path, not as a deployable server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC'17 paper compares HC Redis against default Redis. Fig. 11 (NodeJS, Dynamic Intro, 5k objects) shows 10.0 vs 11.3 kreq/s, miss rate 0.33 vs 0.27, +11.6%; Fig. 7 (Django-Wiki) shows 21.1 vs 23.7 req/s (+12.3%). The CPU (Xeon E5620) is stated and the runner code is public, but no compiler or flags are given, so it is not A.
- **Verifier notes:** The claim numbers match the paper; 10.0 vs 11.3 is kreq/s on the page, so 'req/ms' was numerically equivalent but not the page's unit. Last commit on the default branch is 2017-07-14, and the repo is not a GitHub fork. The record's language 'C' fits only the separate Redis-prototype repo, since this repo is Python. That field is not correctable here.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/atc17/atc17-blankstein.pdf>
  - <https://github.com/kantai/hyperbolic-caching>
  - <https://github.com/kantai/redis-hyperbolic-caching>
- **Sources the enricher read:**
  - <https://github.com/kantai/hyperbolic-caching>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/README.md>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/LICENSE>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/node-sim/spawn_redis.sh>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/node-sim/run_multiple>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/node-sim/run_web_sim.sh>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/django-middleware/hyperbolic_cache.py>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/django-middleware/readme.md>
  - <https://github.com/kantai/hyperbolic-caching/blob/master/simulation/strategies/sampling.py>
  - <https://github.com/kantai/hyperbolic-caching/issues>
  - <https://github.com/kantai/redis-hyperbolic-caching>
  - <https://github.com/kantai/redis-hyperbolic-caching/blob/cost-cache/README>
  - <https://github.com/kantai/redis-hyperbolic-caching/blob/cost-cache/make.sh>
  - <https://github.com/kantai/redis-hyperbolic-caching/commits/cost-cache>
  - <https://github.com/kantai/redis-hyperbolic-caching/compare/3cfca5afdc...f405a50df6>
  - <https://github.com/kantai/redis-hyperbolic-caching/blob/cost-cache/src/version.h>
  - <https://github.com/kantai/redis-hyperbolic-caching/blob/cost-cache/src/redis.h>
  - <https://github.com/kantai/redis-hyperbolic-caching/blob/cost-cache/src/rdb.c>
  - <https://github.com/kantai/redis-hyperbolic-caching/issues>
  - <https://www.usenix.org/system/files/conference/atc17/atc17-blankstein.pdf>
  - <https://hn.algolia.com/api/v1/search?query=hyperbolic%20caching&tags=story>
  - <https://raw.githubusercontent.com/redis/redis-doc/master/docs/reference/eviction/index.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/kantai/hyperbolic-caching`) · [data/wave6/enrich/raw/github_com_kantai_hyperbolic_caching.json](../../../data/wave6/enrich/raw/github_com_kantai_hyperbolic_caching.json) (enrichment confidence 0.82)

</details>
