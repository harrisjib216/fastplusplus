# RobinHood (tail-latency-aware cache repartitioning)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `BSD-3-Clause` · 🔴 abandoned

> Research controller that resizes per-backend memcached partitions by request-blocking count, cutting request P99 versus one shared cache.

| | |
|---|---|
| **Beats** | OneRFpolicy: a single shared off-the-shelf memcached cache per application server, matching Microsoft OneRF's production configuration. Also compared: TAO++ (static per-backend allocation) and emulated LAMA++, Cliffhanger++ and FAIR++. |
| **Claimed result** | Under backend load spikes on the OneRF-modeled testbed, RobinHood meets a 150ms P99 request-latency goal 99.7% of the time, whereas the next best policy meets it only 70% of the time. Sec. 5.2 names the next best policy as OneRFpolicy, a single shared memcached cache matching Microsoft OneRF's production setup: it violates the 150ms P99 SLO 30% of the time vs &lt;0.3% for RobinHood. |
| **Workload** | Testbed of 16 application servers and 34 backend servers across 50 Azure VMs. The servers host 20 backend services (KV store, MySQL cluster, matrix-multiply recommender) modeled on OneRF's 20 most-queried backends. Each application server has a local 32GB memcached. Traffic comes from OneRF production statistics, averaging \~200k queries/s (500k peak), with injected backend load and latency spikes. The metric is the fraction of time a 150ms P99 request-latency SLO is met. |
| **Metric** | latency |
| **Hardware** | 50 Microsoft Azure D16 v3 VMs: 2.4 GHz Intel E5-2673v3 (8 cores), 64GB memory, 400GB SSD, 8Gbit/s network |
| **Adoption** | 95 stars |
| **Last commit** | 2019-07-08 |
| **Links** | [repository](https://github.com/dasebe/robinhoodcache) · [benchmark](https://www.usenix.org/system/files/osdi18-berger.pdf) |

## Verdict

On a 50-VM Azure D16 v3 testbed (2.4 GHz E5-2673v3, 16 app servers with 32 GB local memcached, 34 backend servers across 20 services, \~200k queries/s replaying Microsoft OneRF statistics with injected backend load spikes), RobinHood broke a 150 ms P99 request SLO under 0.3% of the time versus 30% for the next best policy, OneRFpolicy (one shared memcached cache per app server). The result is SLO attainment, not a speed ratio, and no compiler matters (Go + Python, versions not given); in other runs it was under 1.5% vs 38% (LAMA++) for fast load ramps and 5% vs 24% (TAO++) for random multi-backend spikes.

## Use it when

- Application-layer caches in front of many heterogeneous backends (databases, recommenders, KV stores) where each user request fans out into dozens of queries and you have a request-level P99 SLO.
- Backend latency spikes caused by other tenants' load, not correlated with your own query rate, so hit-ratio-maximizing or static per-backend allocations do not react to them.
- OneRF-style layouts where each app server queries only its local cache, and the cache can be resized online per partition (memcached with `cache_memlimit` and slab reassignment, or a cache you control).
- You already log each request's latency and which backend's query was slowest, so computing the RBC is nearly free (paper: under 8 KB/s of stats per app server at 1000 requests/s).
- As a reference design for tail-latency-driven cache allocation: the paper reports the best clairvoyant static split needs 73% more cache to give every backend its peak RobinHood allocation.

## Skip it when

- You need a faster cache server or a better eviction policy. RobinHood only changes partition sizes; per-op throughput is memcached's, and hit P99 goes up 13-28% on partitions being resized.
- Single-backend or low-fan-out workloads (nothing to rebalance), or backends that share one underlying storage bottleneck, which the paper says breaks its assumption of independent query latencies.
- Production use as-is. The author says it is not production-ready and not running in production. The controller is Python 2, and the Dockerfiles use golang:1.8/1.9 with the removed go-wrapper script, the deprecated base/archlinux image and GOPATH builds with no go.mod.
- Latency spikes shorter than a few seconds. Reallocation runs in 5 s windows, and moving 1% of a 32 GB cache (up to 327 1 MB pages) can take up to 5 s because of memcached lock contention.
- When cache-rich backends cannot absorb extra misses: RobinHood raised query latency on the least-queried backend by up to 2.55x and by up to 61% on the top 5 backends.

## How it is fast

Every window (5 s in the paper) it 'taxes' 1% of every partition and hands the pooled space out in proportion to each backend's request blocking count (RBC): how often that backend produced the slowest query among requests whose latency lies between P98.5 and P99.5. A backend whose allocated space exceeds its used space by more than 30% has its RBC ignored, so space is not wasted on backends that already have high hit ratios. Since request P99 is almost entirely made of cache misses on whichever backend is overloaded at the moment, shifting cache from cache-rich to cache-poor backends lowers the miss load where it hurts. No cache operation gets faster; P99 hit latency actually rose 13-28% on the partitions being resized.

## Compared with alternatives

S3-FIFO, SIEVE, LHD, AdaptSize and Hyperbolic Caching improve one cache's eviction or admission, and Pelikan/Segcache, Garnet and Dragonfly are faster cache servers. RobinHood leaves the cache alone and decides how much memory each backend's partition gets so that request P99 drops across a fan-out. Pick its approach when the tail comes from whichever backend is overloaded right now, not from cache speed or overall hit ratio; it can run on top of any resizable cache, including one of those.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | memcached (needs the cache_memlimit and slabs reassign commands; version not pinned, installed from Arch packages); Python 2 with a fork of pymemcache (bsb20/pymemcache: 1 commit adding slabs/cache_memlimit calls, 316 behind upstream) and requests; Go with bradfitz/gomemcache and go-sql-driver/mysql; MySQL and Docker Swarm plus a container registry for the full testbed |
| **Minimum toolchain** | Python 2 (controller); Go 1.8/1.9 GOPATH-era builds (golang:1.8/1.9 images); authors used Docker 18.03 on Ubuntu 17.10 |
| **Platforms** | Linux x86-64 in Docker Swarm (repo ships linux_amd64 prebuilt Go archives and a 9.6 MB appserver binary); other platforms not documented |
| **Thread safety** | Controller holds a per-memcached-client lock and resizes partitions from parallel threads; the Go stats server reads its latency ring without a lock while another goroutine writes it. Nothing else is documented. |
| **Drop-in for the baseline** | partial — runs on unmodified memcached, but replaces the single shared cache with one memcached partition per backend, needs the app server to report per-request latency and slowest-backend ID to a stats server, and adds a controller process per app server |

## Gotchas

- The algorithm named "robinhood" in controller.py is a simple latency-sort heuristic (even split, double share to the highest-P99 backend), not the paper's algorithm. The RBC-proportional policies are the crit_path\* variants: crit_path_window uses the paper's P98.5-P99.5 window, but the shipped example config selects crit_path (P99-P100) with a 1 s interval instead of 5 s.
- Only a 2-backend example config and a small trace are published. The 20-backend configs and traces behind the paper are not (issue #4, unanswered), the simulator was never released (issue #3), and the Cliffhgr++/FAIR++/LAMA++ baselines are not labelled in the repo (issue #2, unanswered).
- The controller disables memcached slab automove and shrinks partitions by randomly reassigning slab pages. memcached does not free pages immediately (multi-MB memory bursts, paper Sec. 5.6), and shrinking blocks some concurrent cache operations.
- Each partition keeps a 30 MB floor and moves in 1 MB steps. The stats server keeps a fixed 10M-entry ring of queries plus requests (the paper says the last 1M requests) and copies and sorts all of it every 3 s.

## Known shortcomings

- The metric is SLO attainment (99.7% vs 70% of requests within the P99 target), not speed; the 'next best' is a single shared memcached cache (OneRF), not static partitioning. Go research prototype.
- Research testbed, not drop-in; the author says it is not production-ready. controller.py's algorithm named 'robinhood' is not the paper's (the paper's RBC is crit_path_window, P98.5-P99.5); the example config uses crit_path at a 1 s interval, not 5 s. The paper's 20-backend configs and traces, simulator and baseline labels are unpublished (issues #2-#4, no reply).
- Dead stack: Python 2, a pymemcache fork 316 commits behind, golang 1.8/1.9 images, GOPATH. Costs: hit P99 +13-28% on resized partitions; miss latency on cache-rich backends up to 2.55x; 5 s windows miss sub-5 s spikes.

## Caveats and trade-offs

The metric is SLO attainment (share of time meeting a 150ms P99), not a throughput or speed ratio. The next-best baseline is a caching policy (one shared memcached cache without partitioning), not a slower memcached. RobinHood repartitions off-the-shelf memcached, so it is a cache resource-allocation system, not a new eviction algorithm. The testbed is Go plus a Python controller, last touched in 2019. No compiler or flags are stated.

Optimizes cross-backend cache-space allocation, not the per-cache eviction policy itself; requires a central resource-allocation (RBC) controller polling all backend caches, adding a coordination layer on top of plain memcached; reallocation decisions are rate-limited to avoid thrashing (ignores reallocations faster than 5s)

## Maintenance

Abandoned research testbed (last commit 2019-07-08, 53 commits, three open issues with no author reply), BSD-3-Clause; the core idea sits in \~600 lines of Python 2 that are easier to port than to run, because the full testbed needs Docker Swarm, a registry and dozens of VMs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed OSDI'18 paper. It states the 99.7% vs 70% result for meeting a 150ms P99 goal (abstract, Fig. 3) and compares against two production policies (OneRFpolicy, which is a single shared off-the-shelf memcached cache, and TAO++) plus emulated LAMA, Cliffhanger and FAIR. The testbed code is public in the repo and the CPU is given (Azure D16 v3, E5-2673v3), but no compiler or flags are stated, so it is not A.
- **Verifier notes:** All metadata matched gh (BSD-3-Clause, 95 stars, last commit 2019-07-08, not archived, not a fork). The main fix is that the 70% 'next best' policy is OneRFpolicy (single shared cache), not a static-partitioning policy. Static partitioning is TAO++.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/osdi18-berger.pdf>
  - <https://github.com/dasebe/robinhoodcache>
  - <https://raw.githubusercontent.com/dasebe/robinhoodcache/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/dasebe/robinhoodcache>
  - <https://github.com/dasebe/robinhoodcache/blob/master/README.md>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/controller.py>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/subquery/subquery.go>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/appserver/app.go>
  - <https://github.com/dasebe/robinhoodcache/blob/master/go/src/statserver/statserver.go>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/statquery/statquery.go>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/parseCacheConfig.py>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/Dockerfile>
  - <https://github.com/dasebe/robinhoodcache/blob/master/nuapp/src/requirements.txt>
  - <https://github.com/dasebe/robinhoodcache/blob/master/configs/example_config.tar.gz>
  - <https://github.com/dasebe/robinhoodcache/blob/master/docker_env.sh>
  - <https://github.com/dasebe/robinhoodcache/blob/master/push_images.sh>
  - <https://github.com/dasebe/robinhoodcache/blob/master/go/Dockerfile_requestor>
  - <https://github.com/dasebe/robinhoodcache/blob/master/go/Dockerfile_fback>
  - <https://github.com/dasebe/robinhoodcache/blob/master/swarm/robinhood-compose.yml>
  - <https://github.com/dasebe/robinhoodcache/issues/1>
  - <https://github.com/dasebe/robinhoodcache/issues/2>
  - <https://github.com/dasebe/robinhoodcache/issues/3>
  - <https://github.com/dasebe/robinhoodcache/issues/4>
  - <https://github.com/bsb20/pymemcache>
  - <https://www.usenix.org/system/files/osdi18-berger.pdf>
  - <https://news.ycombinator.com/item?id=18307077>
  - <https://news.ycombinator.com/item?id=32985096>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dasebe/robinhoodcache`) · [data/wave6/enrich/raw/github_com_dasebe_robinhoodcache.json](../../../data/wave6/enrich/raw/github_com_dasebe_robinhoodcache.json) (enrichment confidence 0.8)

</details>
