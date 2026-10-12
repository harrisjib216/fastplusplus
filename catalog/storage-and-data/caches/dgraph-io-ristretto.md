# Ristretto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Concurrent in-process Go cache with TinyLFU admission and cost-based eviction; \~3x a mutex-wrapped groupcache LRU's throughput in its own benchmarks.

| | |
|---|---|
| **Beats** | The groupcache LRU (golang/groupcache/lru behind a sync.Mutex). The charts label it 'groupcache'; it is presumably the suite's 'base-mutex' entry. |
| **Claimed result** | Approximate values read off the README charts (derived from page data). The SVG axes are labeled; the text is drawn as outlines. Mixed workload (25% writes, 75% reads): Ristretto \~60M ops/s vs groupcache \~20M at 16 goroutines, and \~57M vs \~18M at 64 (\~3x). At 4 goroutines it is \~22.6M vs \~11M, and freecache (\~25.6M) beats Ristretto there. Read (Zipfian): \~64.5M vs \~19.8M at 64 goroutines (\~3.3x). Write (Zipfian): \~53.5M vs \~16.2M at 64 goroutines (\~3.3x); fastcache beats Ristretto at 4-12 goroutines. Hit ratio, Search ARC-S3: 48% vs groupcache 23% at 500k capacity and 68% vs 57% at 800k (optimal \~72%). Hit ratio, Database ARC-DS1: 44% vs 21% at 5M and 55% vs 43% at 8M, but goburrow beats Ristretto at 3M and 6-8M. The blog says Ristretto 'suffers in comparison to the others' on the CODASYL trace. |
| **Workload** | Concurrent throughput in the dgraph-io/dgraph-benchmarks cachebench suite at 4-64 goroutines: Mixed (25% writes, 75% reads), Read (100% Zipfian) and Write (100% Zipfian). Hit ratios on the ARC-S3 search, ARC-DS1 database, LIRS-GLI looping and ARC-OLTP CODASYL traces. Compared against the groupcache LRU with a mutex, BigCache, FreeCache, FastCache and goburrow/cache, plus a clairvoyant 'optimal' policy on the hit-ratio charts. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700K (3.7 GHz), 16 GB RAM. The Ristretto blog post states this for its throughput runs; the README charts, added 2020-06-29, are not confirmed to come from the same run. |
| **Adoption** | 6,994 stars; used in Dgraph and Badger |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/dgraph-io/ristretto) · [benchmark](https://github.com/dgraph-io/ristretto#benchmarks) |

## Verdict

Dgraph's own cachebench compared Ristretto with golang/groupcache/lru behind a sync.Mutex (plus BigCache, FreeCache, FastCache and goburrow). The 2020 README charts show \~3x the LRU's throughput at 16-64 goroutines on Mixed 25% writes/75% reads (\~57M vs \~18M ops/s at 64) and \~3.3x on Zipfian read-only and write-only runs, while freecache wins Mixed at 4 goroutines and fastcache wins writes at 4-12. The only hardware named is an Intel Core i7-8700K with 16 GB, in the 2019 blog; the Go version, build flags and Ristretto version are not stated (cachebench has no go.mod), and the charts predate the September 2020 change that charges internal per-item cost by default.

## Use it when

- A Go service where many goroutines hit a skewed (Zipf-like) key set and a single mutex around an LRU (groupcache/lru, hashicorp/golang-lru) is the bottleneck: the project's charts show that baseline flat at about 16-20M ops/s while Ristretto reaches about 55-65M at 16-64 goroutines.
- Byte-budgeted caches with variable-size values: Set takes a per-item cost, one large valuable item can evict several small ones, and a Cost func can compute cost lazily only for sets that are not dropped.
- Frequency-biased workloads (search, database page caches, analytics), where TinyLFU admission keeps one-hit wonders out; the README Search (ARC-S3) chart shows 48% vs 23% for the LRU at 500k capacity.
- Cache-aside use where losing an occasional insert is acceptable, because hot items are Set repeatedly and eventually get admitted.
- You want per-item TTL, eviction/rejection callbacks for manual memory management, and a small per-entry footprint (keys are not stored, only hashes).

## Skip it when

- You need every Set to land, or read-your-writes: new items can be dropped at the set buffer or rejected by TinyLFU, and a Get straight after Set can miss unless you call Wait().
- Recency-biased or loop/LRU-friendly workloads: the 2019 blog says Ristretto 'suffers' on the CODASYL (ARC-OLTP) trace because LFU fits it badly, and otter's hit-ratio page says it may struggle on recency-biased workloads.
- You size the cache by item count (cost=1) and leave IgnoreInternalCost false: every item is also charged unsafe.Sizeof(storeItem[V]), so the cache holds far fewer items than MaxCost. A user running the project's own ARC-S3 bench at MaxCost 500000 got a 1.05% hit ratio vs \~50% on the README chart (issue #336), and issue #363 reports near-zero hit ratios in third-party benchmarks.
- You need the highest read throughput among Go caches: in otter's third-party benchmark (Apple M1, 8 goroutines, cost configuration corrected) Ristretto did about 32.8M ops/s on 100% reads vs otter's 195M, and fell behind ccache on the 75%-read and 75%-write mixes.
- You need to list keys, exact key equality or a networked/distributed cache: only a 64-bit hash plus a 64-bit xxhash conflict hash is stored, iteration gives values only, and the library is single-process.

## How it is fast

Values live in 256 RWMutex-sharded Go maps keyed by a 64-bit hash (runtime memhash via go:linkname for strings and []byte, the integer itself otherwise). Gets record accesses into striped, lossy sync.Pool ring buffers (BP-Wrapper-style batching), and those batches reach the policy through a non-blocking channel that drops them when full. New Sets go into a 32K-slot buffered channel drained by one goroutine and are dropped rather than block when it is full, so no caller waits on the policy lock. The policy is TinyLFU admission (a 4-row count-min sketch of 4-bit counters, a bloom-filter doorkeeper and periodic halving) paired with SampledLFU eviction (sample 5 resident keys, evict the lowest estimated frequency); the README FAQ credits the throughput to batching and eventual consistency.

## Compared with alternatives

Otter's own benchmarks put it well ahead of Ristretto on read throughput and on hit ratio for recency-biased traces (W-TinyLFU), so otter is the better general-purpose Go default. Pick Ristretto for a byte-cost budget with minimal per-entry memory, or for insert-heavy traffic where dropped sets are acceptable (otter measured Ristretto at 15-22M inserts/s vs its own 2.4-3.3M and attributes the gap to dropped inserts); over go-sieve or golang-fifo, which are count-bounded SIEVE/FIFO caches, it adds cost-weighted eviction, TTL and eviction callbacks.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | cespare/xxhash/v2, dgryski/go-farm, dustin/go-humanize, golang.org/x/sys (testify for tests); optional jemalloc via cgo behind the 'jemalloc' build tag, used only by the z package |
| **Minimum toolchain** | go.mod declares go 1.24.0 (toolchain go1.25.0); the README still says Go 1.21+ |
| **Platforms** | Any Go target in principle: pure Go plus go:linkname into runtime internals (memhash, fastrand, nanotime). The z package has per-OS mmap files (linux, darwin, windows, plan9, js, wasip1) and amd64 assembly with a generic fallback, and recent releases fixed 32-bit, s390x and riscv64 builds. CI runs only on ubuntu-latest. |
| **Thread safety** | Documented as safe to use one Cache from any number of goroutines. Internally it uses 256 RWMutex-sharded maps plus one global policy mutex. Clear is documented as non-atomic and assumes no concurrent Get/Set. |
| **Drop-in for the baseline** | partial — it fills the same role as groupcache/lru but has a different API: a Config with NumCounters, MaxCost and BufferItems, a cost argument on Set, sets that may be dropped, eventually consistent visibility (Wait), and a required Close. Existing call sites need rewriting. |

## Gotchas

- MaxCost includes internal per-item overhead unless IgnoreInternalCost is true. This default arrived in PR #195 (Sep 2020), after the README charts were made; the project's own cachebench adapter still calls Set(key, v, 1) without that flag.
- Set returning true does not mean the item was admitted: TinyLFU can still reject it later. Updates to existing keys are applied immediately, but new keys only appear after the background goroutine processes them.
- Each cache starts background goroutines and a TTL ticker, so always call Close. Del does a blocking send into the set buffer, so under heavy load it can wait for the drainer. Expired entries are swept in 5 s buckets by default but are also filtered out on Get.
- Collision handling depends on key type: integer keys are their own hash with no conflict check, string/[]byte keys add an xxhash conflict hash, and a custom KeyToHash that returns 0 as the second value disables the check. The memhash seed changes per process, so hashes are not persistent.

## Known shortcomings

- The \~3x vs groupcache's LRU is read off blog charts (i7-8700K); a Go library whose win includes hit ratio from TinyLFU admission.
- The 2020 charts predate PR #195 (internal cost on by default); its own cachebench still calls Set(k,v,1) without IgnoreInternalCost and the hit ratio collapses (#336: 1.05% vs \~50% on the README chart; #363 open). Lossy by design (sets dropped at the buffer or by TinyLFU; Get right after Set can miss without Wait()); weak on recency-heavy traces. A third-party otter bench shows \~32.8M vs otter's 195M reads/s, and its insert speed comes from dropping sets. One global policy mutex (#483); keys are not stored (hash + conflict hash only); go.mod needs Go 1.24 while the README says 1.21.

## Caveats and trade-offs

This is the project's own benchmark suite (dgraph-io/dgraph-benchmarks cachebench), so it stays at Tier C. The CPU (i7-8700K) is stated only in the 2019 blog post, and nothing gives the Go version or build flags. The only numbers are chart images: the README SVGs date from 2020 and the blog charts from 2019. Ristretto is not the fastest everywhere: freecache wins the Mixed workload at 4 goroutines and fastcache wins writes at 4-12. Its hit ratio is not best on every trace either: goburrow is higher on the Database trace at several capacities, and Ristretto is weak on CODASYL. The blog.dgraph.io URL is dead, but the post is mirrored at discuss.dgraph.io/t/5102, which the README links.

Ristretto is an embedded in-process Go library, not a networked cache server, so it is not directly comparable to Redis/memcached on a fair basis (no network I/O); SampledLFU/TinyLFU admission adds CPU overhead per operation in exchange for hit-ratio gains; benchmark 'ratio' figures (e.g. 0.18%-98.99% hit rate rows in the README example output) vary hugely by trace and are workload-dependent.

## Maintenance

Actively maintained (v2.4.2 on 2026-07-07, last commit 2026-09-21) and an Apache-2.0 `go get` module, though third-party reports of low hit ratio (#363) and policy-lock contention (#483, with fix PR #489 still open) remain unresolved.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party results. The code is public: dgraph-io/dgraph-benchmarks cachebench/ristretto (cache.go 'base-mutex' = golang/groupcache/lru wrapped in a sync.Mutex) and cachebench/cache_bench_test.go. The blog states the CPU (Intel Core i7-8700K), but neither the blog nor the README gives the Go version or build flags. That makes it the project's own benchmark with partial methodology, which is C.
- **Verifier notes:** The record said the charts were unlabeled; the SVGs render with full axes, legends and values, so approximate numbers were read off them. The original benchmark_url (dgraph-benchmarks cachebench/ristretto) holds only code plus a Ristretto-only example output, so benchmark_url now points to the README charts. Metadata was confirmed: Apache-2.0, 6,994 stars, last commit 2026-09-21, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dgraph-io/dgraph-benchmarks/tree/main/cachebench/ristretto>
  - <https://github.com/dgraph-io/dgraph-benchmarks/blob/main/cachebench/ristretto/cache.go>
  - <https://github.com/dgraph-io/dgraph-benchmarks/blob/main/cachebench/ristretto/bench.go>
  - <https://github.com/dgraph-io/dgraph-benchmarks/blob/main/cachebench/cache_bench_test.go>
  - <https://github.com/dgraph-io/ristretto>
  - <https://raw.githubusercontent.com/dgraph-io/ristretto/main/benchmarks/Throughput%20-%20Mixed.svg>
  - https://raw.githubusercontent.com/dgraph-io/ristretto/main/benchmarks/Throughput%20-%20Read%20(Zipfian).svg
  - https://raw.githubusercontent.com/dgraph-io/ristretto/main/benchmarks/Throughput%20-%20Write%20(Zipfian).svg
  - https://raw.githubusercontent.com/dgraph-io/ristretto/main/benchmarks/Hit%20Ratios%20-%20Search%20(ARC-S3).svg
  - https://raw.githubusercontent.com/dgraph-io/ristretto/main/benchmarks/Hit%20Ratios%20-%20Database%20(ARC-DS1).svg
  - <https://discuss.dgraph.io/t/introducing-ristretto-a-high-performance-go-cache-dgraph-blog/5102>
  - <https://discuss.dgraph.io/raw/5102>
- **Sources the enricher read:**
  - <https://github.com/dgraph-io/ristretto>
  - <https://github.com/dgraph-io/ristretto/blob/main/README.md>
  - <https://github.com/dgraph-io/ristretto/blob/main/go.mod>
  - <https://github.com/dgraph-io/ristretto/blob/main/cache.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/policy.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/store.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/ring.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/sketch.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/ttl.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/z/z.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/z/rtutil.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/z/calloc_jemalloc.go>
  - <https://github.com/dgraph-io/ristretto/blob/main/CHANGELOG.md>
  - <https://github.com/dgraph-io/ristretto/blob/main/.github/workflows/ci-ristretto-tests.yml>
  - <https://github.com/dgraph-io/ristretto/issues/363>
  - <https://github.com/dgraph-io/ristretto/issues/336>
  - <https://github.com/dgraph-io/ristretto/issues/483>
  - <https://github.com/dgraph-io/ristretto/issues/369>
  - <https://github.com/dgraph-io/ristretto/issues/431>
  - <https://github.com/dgraph-io/ristretto/issues/380>
  - <https://github.com/dgraph-io/ristretto/pull/195>
  - <https://github.com/dgraph-io/ristretto/pull/318>
  - <https://github.com/dgraph-io/ristretto/releases>
  - <https://github.com/dgraph-io/dgraph-benchmarks/blob/main/cachebench/ristretto/cache.go>
  - <https://discuss.dgraph.io/raw/5102>
  - <https://maypok86.github.io/otter/performance/throughput/>
  - <https://maypok86.github.io/otter/performance/hit-ratio/>
  - <https://maypok86.github.io/otter/performance/memory-consumption/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dgraph-io/ristretto`) · [data/wave6/enrich/raw/github_com_dgraph_io_ristretto.json](../../../data/wave6/enrich/raw/github_com_dgraph_io_ristretto.json) (enrichment confidence 0.75)

</details>
