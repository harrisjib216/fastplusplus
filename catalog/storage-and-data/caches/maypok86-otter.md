# otter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Caffeine-style concurrent Go cache (adaptive W-TinyLFU): 10-34x hashicorp/golang-lru throughput at 25-100% reads; slower on pure writes.

| | |
|---|---|
| **Beats** | hashicorp/golang-lru |
| **Claimed result** | Zipf GetPutBenchmark port at -cpu=8 on an Apple M1 Pro. Reads=100%: otter 106,390,749 ops/s (9.399 ns/op) vs golang-lru 3,138,739 ops/s (318.6 ns/op), about 34x (derived from page data). Reads=75%/writes=25%: otter 78,478,946 vs golang-lru 2,906,471 ops/s, about 27x (derived from page data), with theine at 31,585,616 and ristretto at 24,927,336 (otter about 2.5-3.1x ahead). Reads=50%: otter 58,504,159 vs golang-lru 2,832,079 ops/s. Reads=25%: otter 30,237,769 vs 2,941,043. Writes=100%: otter 2,315,752 ops/s (431.8 ns/op) vs golang-lru 3,230,908 ops/s (309.5 ns/op), so golang-lru is about 1.4x faster on pure writes (derived from page data). |
| **Workload** | Go port of the Caffeine JMH GetPutBenchmark: 8 goroutines against a pre-populated, max-size-bounded cache under a Zipf access distribution, at read/write ratios of 100/0, 75/25, 50/50, 25/75 and 0/100, comparing otter, theine, ristretto, sturdyc, ccache, gcache, ttlcache and golang-lru. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro, goos=darwin, goarch=arm64 |
| **Compiler and flags** | Go toolchain version not stated (benchmarks/go.mod declares only minimum go 1.24.0). Command per benchmarks/throughput/bench.sh: `go test -run='^$' -cpu=8 -bench . -timeout=0`. |
| **Adoption** | 2,684 stars; README lists users Grafana, Centrifugo, FrankenPHP, Unkey, Nuclei |
| **Last commit** | 2025-12-23 |
| **Links** | [repository](https://github.com/maypok86/otter) · [benchmark](https://raw.githubusercontent.com/maypok86/otter/main/benchmarks/throughput/results/throughput.txt) |

## Verdict

The numbers come from the project's own Go port of Caffeine's GetPutBenchmark: 8 goroutines (-cpu=8), with a 32,768-entry cache pre-filled from a scrambled Zipf over about 10.9K string keys, so every Get hits and every Set is an update with no eviction. Run once on an Apple M1 Pro (darwin/arm64) with an unrecorded Go toolchain, otter reached 106.4M ops/s at 100% reads vs 3.14M for hashicorp/golang-lru v2 (about 34x), about 27x at 75/25, 21x at 50/50 and 10x at 25/75, while golang-lru was about 1.4x faster at 100% writes (3.23M vs 2.32M ops/s).

## Use it when

- Read-heavy in-process caches shared by many goroutines on multi-core machines, where golang-lru's global lock on Get is the bottleneck (first-party: 34x at 100% reads, 27x at 75/25, 21x at 50/50).
- Bounded caches whose access pattern is unknown or shifts between recency- and frequency-biased, where the adaptive W-TinyLFU window beats plain LRU hit rates on the project's trace simulations (S3, DS1, P8, OLTP, Glimpse, mixed).
- When you want Caffeine's feature set in Go: per-entry variable TTL, loader dedupe to limit stampedes, background refresh-ahead, weight-based bounds, stats counters, and deletion callbacks.
- Generic keys of any comparable type (hashed with maphash.Comparable) and any value type, from hundreds to millions of entries (the eviction benchmark covers capacities from 100 to 1,000,000).

## Skip it when

- Pure-write or update-heavy workloads: at 100% writes otter measured 2.32M ops/s vs golang-lru's 3.23M, behind theine, ristretto, sturdyc, gcache and ttlcache too; the docs themselves list extreme write-heavy loads as the exception.
- When the size cap must hold at every instant (tiny caches, or entries that pin scarce resources): with the default async Executor, a tight Set loop pushed a MaximumSize=2 cache to 1,027 entries (issue #171). The maintainer's fix is a synchronous Executor, which moves the eviction work back onto the caller.
- Low-contention or single-goroutine use, or small insert-only caches. The gains come from contention; in the insert-only eviction benchmark golang-lru was faster at capacity 100 (266.6 vs 307.5 ns/op), though otter was faster at 10K and 1M.
- Hot paths built on Compute with slow callbacks: Compute holds a hash-table bucket lock while the function runs, and open issue #177 reports heavy mutex delay in drainBuffers under frequent Compute (v2.2.1, root cause not yet found).
- Toolchains older than Go 1.24, or projects that cannot track new Go releases: the README says only the two most recent Go minor versions are supported.

## How it is fast

The hash table is a fork of puzpuzpuz/xsync's MapOf, a CLHT-style (Cache-Line Hash Table) design with 64-byte buckets of 5 entries and SWAR meta-byte probing, so Get does no memory writes and takes no locks. Policy bookkeeping follows BP-Wrapper: reads go into a lossy striped ring buffer (the stripe count grows when contention is detected) and writes into a bounded growable MPSC queue, and both are replayed in batches under one eviction mutex taken with TryLock, so readers never wait on the policy lock. By contrast, golang-lru takes an exclusive sync.RWMutex Lock on every Get to move the entry to the front. Eviction is adaptive W-TinyLFU (admission window plus segmented main space, a 4-bit count-min sketch and hill-climbing window sizing), expiry uses a hierarchical timing wheel, and node structs are code-generated per feature set so options you don't use add no per-entry memory.

## Compared with alternatives

go-sieve and golang-fifo also report large wins over golang-lru with SIEVE-style policies; pick otter when you also need Caffeine-style features (variable TTL, loader dedupe, refresh-ahead, weights, stats) and an adaptive policy that holds up on both recency- and frequency-biased traces. Caffeine itself is the JVM original that otter's design and benchmark are ported from.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime beyond the Go standard library (the only direct requirement in go.mod is stretchr/testify, for tests); the slog logger plugin is a separate module (plugin/pslog) |
| **Minimum toolchain** | Go 1.24 (go.mod `go 1.24.0`; uses maphash.Comparable and runtime.AddCleanup). Only the two newest Go minor versions are supported; CI runs Go 1.25.x, plus a 32-bit job on 1.24.x. |
| **Platforms** | pure Go, so any GOOS/GOARCH in principle. CI runs Linux (ubuntu-latest) plus a 32-bit build; the GOARCH=wasm build was fixed in v2.3.0. Published benchmarks exist only for darwin/arm64 (Apple M1 Pro). |
| **Thread safety** | Safe for concurrent use. Hash-table reads are lock-free, writes lock one bucket, and policy updates are applied in batches under a single eviction mutex. Compute\* holds a bucket lock during the callback, and loaders must not modify the cache. |
| **Drop-in for the baseline** | partial: both are generic in-process caches, but the API differs (Add becomes Set returning (V, bool), Get becomes GetIfPresent, Peek becomes GetEntryQuietly, Remove becomes Invalidate, Purge becomes InvalidateAll, Len becomes EstimatedSize). Keys() is an iterator in unspecified order, not oldest-to-newest. Eviction is W-TinyLFU rather than LRU, and the size bound is soft by default. |

## Gotchas

- Policy state is only eventually consistent with the map: eviction and expiry reordering run in batches on a goroutine started through the Executor (default `go fn()`), so EstimatedSize can exceed MaximumSize for a while. Pass a synchronous Executor if you need strict bounds, as the project's own hit-ratio simulator does.
- Get(ctx, key, loader) works like singleflight: under a burst of concurrent Gets the loader can still run more than once for the same key (issue #152). A fix PR (#184) has been open since 2026-06-25.
- Weights are computed once, on write, and never recomputed; they only decide whether the cache is over capacity, not which entry is evicted. Zero weight or an expiry of math.MaxInt64 is the documented way to pin an entry.
- When expiry is enabled, a cleanup goroutine ticks once per second. It is stopped by a runtime.AddCleanup finalizer or by an explicit StopAllGoroutines (needed under synctest, issue #158). SaveCacheTo/LoadCacheFrom use encoding/gob, so K and V must be gob-encodable.

## Known shortcomings

- No Go toolchain version stated (go.mod minimum only). The \~27x read-throughput lead shrinks with writes, and at 100% writes golang-lru is \~1.4x faster.
- The benchmark flatters it: a 32,768-slot cache over \~10.9K Zipf keys means every Get hits, every Set updates and nothing is evicted; one M1 Pro run. Pure writes lose (2.32M vs golang-lru 3.23M ops/s; second-slowest of 8 caches). MaximumSize is soft with the async executor (#171 shows 1,027 entries at max 2; use the sync executor). Open bugs: drainBuffers mutex contention under Compute (#177); the loader runs more than once per key (#152, fix PR #184 open). Not a drop-in (renamed API, W-TinyLFU not LRU); Go 1.24+; no commits since 2025-12.

## Caveats and trade-offs

These are first-party numbers from a single Apple M1 Pro run, committed 2025-06-13, and the Go toolchain version is not recorded. The win is read-heavy only: in the same throughput file, at writes=100% otter (2.32M ops/s) is slower than golang-lru (3.23M ops/s) and several other caches, so the 'faster than LRU' claim depends on the workload.

Otter's sophisticated TinyLFU-based admission/eviction policy costs more per-eviction CPU time than simple mutex-protected LRU under 100%-insert/eviction-heavy workloads — the project's own eviction benchmark shows golang-lru (266-461 ns/op) beating otter (307-417 ns/op) in that specific worst-case scenario, even though otter wins decisively on read-heavy throughput.

## Maintenance

v2.3.0 was released 2025-12-22 and main's last commit is 2025-12-23, but the maintainer was still answering issues in 2026 and bug reports and a fix PR (#184) are open; Apache-2.0, pure Go with no runtime dependencies, and the README lists users including Grafana, Centrifugo and FrankenPHP.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** throughput.txt is raw `go test` output (code: benchmarks/throughput/bench_test.go, command in bench.sh: `go test -run='^$' -cpu=8 -bench . -timeout=0`) that names the CPU (Apple M1 Pro) and includes golang-lru rows. No Go toolchain version is recorded anywhere; benchmarks/go.mod gives only the minimum `go 1.24.0` and has no toolchain line. Under the orchestrator's Go rule (goccy/go-json, constmap, libjson), a missing toolchain version means first-party partial methodology, so C.
- **Verifier notes:** The record said golang-lru was not in the 75/25 excerpt, but it is (2,906,471 ops/s). The record also put theine/ristretto at 1.2-3x behind otter at 75/25, but the file gives 2.5-3.1x. The pure-write inversion is on the same benchmark page, not only in the eviction benchmark. License Apache-2.0, last commit 2025-12-23 and not archived all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/maypok86/otter>
  - <https://raw.githubusercontent.com/maypok86/otter/main/benchmarks/throughput/results/throughput.txt>
  - <https://raw.githubusercontent.com/maypok86/otter/main/benchmarks/throughput/bench.sh>
  - <https://raw.githubusercontent.com/maypok86/otter/main/benchmarks/go.mod>
  - <https://raw.githubusercontent.com/maypok86/otter/main/go.mod>
  - <https://raw.githubusercontent.com/maypok86/otter/main/README.md>
  - <https://raw.githubusercontent.com/maypok86/otter/main/LICENSE>
  - <https://maypok86.github.io/otter/performance/throughput/>
- **Sources the enricher read:**
  - <https://github.com/maypok86/otter>
  - <https://github.com/maypok86/otter/blob/main/README.md>
  - <https://github.com/maypok86/otter/blob/main/docs/performance/design.md>
  - <https://github.com/maypok86/otter/blob/main/docs/performance/throughput.md>
  - <https://github.com/maypok86/otter/blob/main/docs/performance/hit-ratio.md>
  - <https://github.com/maypok86/otter/blob/main/docs/performance/memory-consumption.md>
  - <https://github.com/maypok86/otter/blob/main/docs/user-guide/v2/features/eviction.md>
  - <https://raw.githubusercontent.com/maypok86/otter/main/benchmarks/throughput/results/throughput.txt>
  - <https://github.com/maypok86/otter/blob/main/benchmarks/throughput/bench_test.go>
  - <https://github.com/maypok86/otter/blob/main/benchmarks/throughput/bench.sh>
  - <https://github.com/maypok86/otter/blob/main/benchmarks/eviction/bench_test.go>
  - <https://github.com/maypok86/otter/blob/main/benchmarks/client/golanglru.go>
  - <https://github.com/maypok86/otter/blob/main/benchmarks/client/otter.go>
  - <https://github.com/maypok86/otter/blob/main/go.mod>
  - <https://github.com/maypok86/otter/blob/main/options.go>
  - <https://github.com/maypok86/otter/blob/main/cache.go>
  - <https://github.com/maypok86/otter/blob/main/cache_impl.go>
  - <https://github.com/maypok86/otter/blob/main/policy.go>
  - <https://github.com/maypok86/otter/blob/main/sketch.go>
  - <https://github.com/maypok86/otter/blob/main/persistence.go>
  - <https://github.com/maypok86/otter/blob/main/internal/hashmap/map.go>
  - <https://github.com/maypok86/otter/blob/main/internal/lossy/striped.go>
  - <https://github.com/maypok86/otter/blob/main/internal/xruntime/hasher.go>
  - <https://github.com/maypok86/otter/blob/main/internal/xruntime/xruntime.go>
  - <https://github.com/maypok86/otter/blob/main/CHANGELOG.md>
  - <https://github.com/maypok86/otter/blob/main/.github/workflows/test.yml>
  - <https://github.com/maypok86/otter/blob/main/.github/workflows/test-32-bit.yml>
  - <https://github.com/maypok86/otter/issues>
  - <https://github.com/maypok86/otter/issues/152>
  - <https://github.com/maypok86/otter/issues/171>
  - <https://github.com/maypok86/otter/issues/177>
  - <https://github.com/maypok86/otter/pull/184>
  - <https://github.com/maypok86/otter/commits/main>
  - <https://github.com/maypok86/otter/releases>
  - <https://raw.githubusercontent.com/hashicorp/golang-lru/main/lru.go>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/maypok86/otter`) · [data/wave6/enrich/raw/github_com_maypok86_otter.json](../../../data/wave6/enrich/raw/github_com_maypok86_otter.json) (enrichment confidence 0.85)

</details>
