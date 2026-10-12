# golang-fifo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Go generic in-process cache implementing SIEVE and S3-FIFO eviction; about 16-18% fewer misses than hashicorp LRU, but no higher ops/sec.

| | |
|---|---|
| **Beats** | lru-hashicorp / lru-groupcache |
| **Claimed result** | README table (added 2023-12-12; itemSize=500000, 7.5M ops, cacheSize=0.10%, Zipf 0.99, concurrency=16): SIEVE 47.66% hit rate at 2,508,361 QPS vs lru-hashicorp 36.57% at 2,055,358 QPS and lru-groupcache 36.59% at 2,206,841 QPS (\~1.30x hit rate and \~1.22x QPS vs lru-hashicorp, derived from page data). The README says SIEVE 'approximately improves 30% for efficiency than a simple LRU cache'. But the linked go-cache-benchmark README (results refreshed 2024-03-12) puts SIEVE's QPS BELOW both LRU baselines at concurrency 2-16. At concurrency=16 and 0.10% cache, sieve does 2,644,570 QPS vs lru-hashicorp 3,052,503 and lru-groupcache 3,135,452. SIEVE is ahead only at concurrency=1 (5,053,908 vs 4,649,721, \~1.09x, derived from page data). The lasting win is hit rate: about +11 points at 0.1% cache, +8 at 1% and +4 at 10% vs lru-hashicorp at concurrency=16 (derived from page data). |
| **Workload** | go-cache-benchmark harness: itemSize=500000, workloads=7500000 ops, cacheSize=0.10% of item space, Zipf alpha=0.99, concurrency=16, comparing sieve/s3-fifo/tinylfu/slru/s4lru/two-queue/clock against lru-groupcache and lru-hashicorp. |
| **Metric** | throughput |
| **Adoption** | 172 stars |
| **Last commit** | 2025-05-10 |
| **Links** | [repository](https://github.com/scalalang2/golang-fifo) · [benchmark](https://github.com/scalalang2/golang-fifo#benchmark-result) |

## Verdict

The author's go-cache-benchmark harness runs a Get-then-Set-on-miss loop over 7.5M Zipf(0.99) string keys drawn from 500K items. Results are single runs on an unnamed desktop, with go.mod at Go 1.22 and golang-fifo v0.1.3. They show SIEVE with 16-18% fewer misses than hashicorp/golang-lru v2 at 0.1%, 1% and 10% cache sizes, but lower QPS at 2-16 goroutines (for example 2.64M vs 3.05M ops/s at 16 goroutines with a 0.1% cache) and higher QPS only single-threaded (5.05M vs 4.65M). The README's headline 2.51M vs 2.06M QPS row comes from an older (2023-12-12) run of the same harness, which the later tables contradict. No CPU model, compiler flags or repeat runs are reported for any of these comparisons.

## Use it when

- Go services with read-heavy, power-law (Zipf-like) key popularity, such as web or API response caching, where each miss costs a database or network round trip. In the author's harness SIEVE's hit rate beat hashicorp LRU's by about 11 points at a 0.1% cache and about 4 points at 10%.
- Caches that are small relative to the key space (roughly 0.1-1% of distinct items), where the hit-ratio gap over LRU is widest.
- Code already using hashicorp/golang-lru or groupcache/lru that wants a better eviction policy with little API churn and no runtime dependencies (standard library only).
- Single-goroutine or low-contention callers. At concurrency=1 the harness had SIEVE at about 1.09x lru-hashicorp's QPS.
- Cases needing one TTL for the whole cache plus an eviction callback that tells capacity evictions, expirations and explicit removals apart.

## Skip it when

- Throughput-bound, highly concurrent hot paths. Each cache uses one global mutex. In the author's harness SIEVE trailed both LRU baselines at 2-16 goroutines (0.66-0.87x lru-hashicorp QPS at 16 goroutines), golang-fifo's own S3-FIFO ran at about 0.6x, and otter and sharded freelru were much faster.
- Scan-heavy or looping access patterns. The README says SIEVE is not scan-resistant; S3-FIFO or TinyLFU-style admission handles these better.
- Workloads close to a 100% hit ratio. Both policies have O(n) worst-case eviction when every entry has been touched (issue #18, open since January 2024).
- Large or GC-sensitive caches. Every entry is a heap object plus a container/list element holding a boxed key (the README appendix shows 4 allocs/op), and the README says the library does not try to compete with bigcache or freecache.
- Cases needing Keys/Values iteration, Resize, GetOldest/RemoveOldest, per-entry TTL, cost- or byte-based sizing, or sharding. A sharded variant is still an open request (issue #24).

## How it is fast

The gain is fewer misses, not cheaper operations. SIEVE (NSDI'24) keeps one FIFO list plus a 'visited' bit per entry. A hit only sets the bit, and eviction walks a hand from the tail toward the head, clearing bits until it finds an unvisited entry. On Zipf-like traffic this keeps popular items and drops one-hit wonders quickly. S3-FIFO (SOSP'23) uses a small FIFO holding 10% of capacity, a main FIFO with a 2-bit frequency counter, and a ghost list of recently evicted keys, so one-hit wonders are filtered out before they reach the main queue. The README's claim that SIEVE hits need only a reader lock is out of date. v0.1.5 (January 2024) moved every call to an exclusive sync.Mutex after a data-race report (issue #21), so hits now serialize just as hashicorp's LRU Get does.

## Compared with alternatives

The catalogued SIEVE and S3-FIFO entries are libCacheSim simulators and CacheLib prototypes, and Caffeine and W-TinyLFU target the JVM and C++. Pick this one when you need those eviction policies as an importable Go package with an LRU-like API. If your Go hot path is limited by lock contention rather than misses, the author's own harness points to otter or sharded freelru (not catalogued) instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (standard library container/list, sync, context, time); fortio.org/assert is used only by tests |
| **Minimum toolchain** | Go 1.24 (go.mod 'go 1.24'; CI tests on 1.24.x). The code needs generics and the Go 1.21 min builtin. |
| **Platforms** | any Go target (pure Go, no unsafe or assembly) |
| **Thread safety** | Safe for concurrent use. Every SIEVE method, and every S3FIFO method except Len, takes one exclusive sync.Mutex, including Get. S3FIFO.Len reads its lists without the lock. A TTL &gt; 0 starts one background goroutine per cache, which runs until Close is called. |
| **Drop-in for the baseline** | partial — the shape matches hashicorp/golang-lru v2 (generic K/V, Get/Peek/Contains/Remove/Len/Purge), but Add becomes Set with no evicted return, New returns no error (SIEVE panics if size &lt;= 0), the callback gains an EvictReason argument, and Keys, Values, Resize, Cap, GetOldest, RemoveOldest, ContainsOrAdd and PeekOrAdd are missing. Unlike groupcache/lru it is generic and already locked. |

## Gotchas

- No published throughput number measures the shipping code. The README table (2023-12-12) and the harness tables (March 2024, pinned to golang-fifo v0.1.3) both come from before v0.1.5 replaced the RWMutex with a Mutex. The harness was bumped to v1.2.0 in July 2025, but its README results were not re-run. Hit rates depend only on the algorithm and should carry over; QPS should not be assumed to.
- S3FIFO with TTL &gt; 0 looks unsafe. Its addToBucket still computes the bucket index in int8 arithmetic, the same expression PR #32 fixed in SIEVE after an 'index out of range [-28]' panic, and no S3FIFO test calls Set after the cleanup counter passes 28. S3FIFO.New also skips SIEVE's size check, and S3FIFO.Purge leaves TTL bucket entries behind.
- Expiry is enforced only by the background sweeper, which cycles through 100 time buckets and ticks every ttl/100. Get does not check an entry's expiry time, so an expired value can be returned until its bucket is swept. TTL caches that are never Closed leak their sweeper goroutine.
- The eviction callback runs while the cache mutex is held, so calling the same cache from inside it will deadlock (sync.Mutex is not reentrant). SIEVE's Close/Purge fires the callback with EvictReasonRemoved for every remaining entry, while S3FIFO's Purge fires none.

## Known shortcomings

- The win is hit ratio (+11 points at a 0.1% cache), not speed: the linked benchmark's newer 2024-03 results show SIEVE QPS below lru-hashicorp/groupcache at concurrency 2-16 (at 16: 2.64M vs 3.05M), faster only at concurrency 1 (\~1.09x).
- v0.1.5 replaced the reader lock with an exclusive Mutex on Get (race #21), and every QPS table predates it (the harness pins v0.1.3), so none measures shipping code. The repo ships only SIEVE and S3-FIFO (the other policies in the harness are third-party). S3-FIFO TTL likely keeps an int8 bucket overflow fixed only in SIEVE (PR #32, untested); Get ignores expiry until the sweeper runs; callbacks run under the mutex (re-entry deadlocks); no sharding (#24); O(n) worst-case eviction (#18); stale since 2025-05.

## Caveats and trade-offs

The comparison harness is the author's separate go-cache-benchmark repo (no LICENSE file; runs done 'on my desktop'; no CPU model stated; go.mod now pins Go 1.24). The README's headline table dates from 2023-12-12. Its claim that SIEVE has the highest QPS is contradicted by the harness's own newer results from 2024-03-12: there SIEVE's throughput trails lru-hashicorp and lru-groupcache at concurrency&gt;=2, and trails tinylfu, s4lru, otter and freelru at most settings. The real advantage is hit ratio (fewer misses reaching the backend), not raw ops/sec. The README also warns that SIEVE is not scan-resistant and that the library does not aim to beat bigcache or freecache.

Library packages SIEVE, S3-FIFO, TinyLFU, SLRU, S4LRU, Clock, 2Q as separate importable cache implementations; SIEVE specifically trades LRU's move-to-head on hit for a cheaper single-bit visited flag under a reader lock.

## Maintenance

Stale: the last release, v1.2.0 on 2025-05-10, only bumped Go to 1.24, and sharding (#24), O(n) worst-case eviction (#18) and concurrency tests (#22) remain open. Still, it is MIT-licensed, about 700 lines with no runtime dependencies and easy to vendor, and pkg.go.dev lists a handful of importers, including redpanda-operator.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers. The README table comes from the author's own public harness (scalalang2/go-cache-benchmark: benchmark.go, main.go), but the comparison run states no CPU model or flags beyond 'my desktop', so it cannot be A. The README's only CPU-stated run (i5-10600KF appendix) benchmarks SIEVE alone, with no baseline.
- **Verifier notes:** Numbers in the record match the README exactly, but the 'faster' part of the claim does not hold. On throughput the linked benchmark repo's current tables show SIEVE slower than the LRU baselines under concurrency. Only the hit-rate win is solid, so the orchestrator may want to change metric from throughput to hit ratio. License MIT, 172 stars, not a fork, last commit 2025-05-10 (stale); all confirmed via gh.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scalalang2/golang-fifo>
  - <https://github.com/scalalang2/golang-fifo#benchmark-result>
  - <https://raw.githubusercontent.com/scalalang2/golang-fifo/main/README.md>
  - <https://github.com/scalalang2/go-cache-benchmark>
  - <https://raw.githubusercontent.com/scalalang2/go-cache-benchmark/main/README.md>
  - <https://raw.githubusercontent.com/scalalang2/go-cache-benchmark/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/scalalang2/golang-fifo>
  - <https://github.com/scalalang2/golang-fifo#benchmark-result>
  - <https://github.com/scalalang2/golang-fifo/blob/main/sieve/sieve.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/s3fifo/s3fifo.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/s3fifo/ghost.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/types/types.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/go.mod>
  - <https://github.com/scalalang2/golang-fifo/blob/main/CHANGELOG.md>
  - <https://github.com/scalalang2/golang-fifo/blob/main/.github/workflows/ci.yml>
  - <https://github.com/scalalang2/golang-fifo/blob/main/bench_test.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/bench.sh>
  - <https://github.com/scalalang2/golang-fifo/blob/main/s3fifo/s3fifo_test.go>
  - <https://github.com/scalalang2/golang-fifo/blob/main/sieve/sieve_test.go>
  - <https://github.com/scalalang2/golang-fifo/blob/v0.1.3/sieve/sieve.go>
  - <https://github.com/scalalang2/golang-fifo/blob/v0.1.5/sieve/sieve.go>
  - <https://github.com/scalalang2/golang-fifo/blob/v1.0.0/sieve/sieve.go>
  - <https://github.com/scalalang2/golang-fifo/tags>
  - <https://github.com/scalalang2/golang-fifo/releases>
  - <https://github.com/scalalang2/golang-fifo/commits/main/README.md>
  - <https://github.com/scalalang2/golang-fifo/issues?q=is%3Aissue>
  - <https://github.com/scalalang2/golang-fifo/pulls?q=is%3Apr>
  - <https://github.com/scalalang2/golang-fifo/issues/11>
  - <https://github.com/scalalang2/golang-fifo/issues/12>
  - <https://github.com/scalalang2/golang-fifo/issues/16>
  - <https://github.com/scalalang2/golang-fifo/issues/18>
  - <https://github.com/scalalang2/golang-fifo/issues/21>
  - <https://github.com/scalalang2/golang-fifo/issues/24>
  - <https://github.com/scalalang2/golang-fifo/issues/36>
  - <https://github.com/scalalang2/golang-fifo/issues/38>
  - <https://github.com/scalalang2/golang-fifo/pull/23>
  - <https://github.com/scalalang2/golang-fifo/pull/32>
  - <https://github.com/scalalang2/golang-fifo/pull/35>
  - <https://github.com/scalalang2/go-cache-benchmark>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/README.md>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/go.mod>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/a3bdf84/go.mod>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/benchmark.go>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/main.go>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/cache/sieve.go>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/cache/lru.go>
  - <https://github.com/scalalang2/go-cache-benchmark/blob/main/cache/lru_groupcache.go>
  - <https://github.com/scalalang2/go-cache-benchmark/commits/main>
  - <https://github.com/scalalang2/go-cache-benchmark/commit/1439604>
  - <https://github.com/hashicorp/golang-lru/blob/main/lru.go>
  - <https://github.com/golang/groupcache/blob/master/lru/lru.go>
  - https://hn.algolia.com/api/v1/search?query=golang-fifo&tags=(story,comment)
  - <https://news.ycombinator.com/item?id=38753417>
  - <https://news.ycombinator.com/item?id=38753657>
  - <https://pkg.go.dev/github.com/scalalang2/golang-fifo/sieve?tab=importedby>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/scalalang2/golang-fifo`) · [data/wave6/enrich/raw/github_com_scalalang2_golang_fifo.json](../../../data/wave6/enrich/raw/github_com_scalalang2_golang_fifo.json) (enrichment confidence 0.8)

</details>
