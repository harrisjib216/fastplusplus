# go-sieve

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `BSD-2-Clause` · 🟢 active

> Fixed-capacity generic Go SIEVE cache whose mutex-free Get path out-scales hashicorp/golang-lru LRU/ARC under concurrent reads.

| | |
|---|---|
| **Beats** | hashicorp/golang-lru (LRU and ARC) |
| **Claimed result** | "13x-55x faster than the better of LRU/ARC per trace" for warm parallel Get (SIEVE k=1: 2.24-12.20 ns/op across 18 MSR/Meta traces, GOMAXPROCS=10). "2.0x-6.1x faster" for cold parallel mixed read+write replay (37.4-274.7 ns/op). In the synthetic micro-benchmark medians, Get_Parallel is 5.76 ns/op (Sieve) vs 144.2 (LRU) vs 144.9 (ARC), and Mixed_Parallel (60/30/10) is 70.99 vs 162.2 vs 211.8 ns/op. In the core-scaling sweep for Get_Parallel, Sieve goes from 14.93 ns/op (GOMAXPROCS=1) to 5.52 (4) and 7.53 (10), while LRU goes from 31.35 to 121.1 (4) and 182.1 (10). |
| **Workload** | Go benchmark suite (bench/) comparing SIEVE vs hashicorp/golang-lru v2.0.7 (LRU and ARC): parallel Get/Add/Probe/Delete/Mixed micro-benchmarks, Zipfian-distribution read benchmarks, core-scaling sweep (1-10 GOMAXPROCS), and real-world trace replay (MSR Cambridge, Meta Storage, \~300M requests) for hit-ratio and memory. |
| **Metric** | throughput |
| **Hardware** | Apple M4, 10 cores (4 performance + 6 efficiency), macOS Darwin 25.5.0, arm64 |
| **Compiler and flags** | go1.26.3 darwin/arm64. bench/Makefile runs `go test -bench=. -benchmem -count=3` for the synthetic set (make bench), `go test -tags=trace -bench=. -benchmem -count=1 -v` for trace replay (make trace), and a GOMAXPROCS sweep over 1 2 4 8 10 (make sweep). Run date 2026-06-10. |
| **Adoption** | 41 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/opencoff/go-sieve) · [benchmark](https://github.com/opencoff/go-sieve/blob/main/bench-results.md) |

## Verdict

The author ran these on an Apple M4 (10 cores, 4P+6E) with go1.26.3 darwin/arm64 at GOMAXPROCS=10, from a pre-v0.6.5 working tree, and nobody has reproduced them independently. Warm-cache parallel Gets replayed from 18 MSR Cambridge and Meta storage traces took 2.24-12.20 ns/op versus 105.7-384.9 ns/op for hashicorp/golang-lru v2.0.7 LRU/ARC (13-55x faster than the better of the two). Cold mixed replay (Probe vs Get+Add) was 2.0-6.1x faster, and the synthetic 8192-entry uniform-int Get_Parallel was 5.76 vs 144.2 ns/op. All of these are aggregate throughput (wall time divided by b.N across goroutines), not per-call latency.

## Use it when

- Read-dominated in-process caches hit by many goroutines at once, where golang-lru's single mutex is the bottleneck. The author's examples are HTTP response, DNS resolver and authz decision caches. The gap grows with cores: Get_Parallel is 14.9 vs 31.4 ns/op (LRU) at GOMAXPROCS=1 and 7.5 vs 182.1 at 10.
- Warm caches with high hit rates. The big win is on the hit path (13-55x on trace-replayed parallel Gets); on cold mixed read/write replay it drops to 2-6x.
- Large entry counts with scalar or fixed-size keys and values (ints, [16]byte, small structs), where GC scan cost matters. At 1M entries the heap is 78.4 MB vs 112.4 MB for LRU, and the GC-impact benchmark is 4.37 vs 9.46 ms/iter.
- Get-or-insert code paths. Probe/ProbeFunc do check-then-insert in one TOCTOU-safe call and return the evicted entry synchronously, so the caller can clean it up without channels or callbacks.
- Teams that want a small BSD-2 library with one dependency (the core is sieve.go + slotstate.go) that they can read or vendor, rather than a full caching framework.

## Skip it when

- Write-, miss- or delete-heavy workloads. Every insert of a new key, every eviction and every Delete takes one global mutex. In the Mixed_Parallel sweep (60% Get/30% Add/10% Delete), SIEVE's own aggregate time gets worse as cores are added, from 33.3 ns/op at 1 core to 92.3 at 10 (LRU goes to 222.8). Delete_Parallel is slower than LRU (81.2 vs 69.5 ns/op).
- When hit ratio matters more than CPU. With the cache at 10% of unique keys, ARC had the lowest miss ratio on 11 of 18 traces and LRU on 5 (all Meta storage traces). SIEVE k=1 beat LRU on only 10 of 18 traces and was never best in its row.
- Very hot-key read skew. Readers spin on the same slot word: at Zipf s=1.50 the lead over LRU shrinks to about 6% (94.2 vs 100.4 ns/op), and at s=1.01 SIEVE's own ns/op rises from 8.2 at 2 cores to 26.6 at 10.
- When you need TTL/expiry, cost- or weight-based capacity, eviction callbacks, Resize, statistics, or loading/refresh. None of these exist, and capacity is a fixed entry count. New() also allocates the full node array, 8 bytes of slot state per entry and a presized map up front, even if the cache never fills.
- Risk-averse production use. It is pre-1.0 (v0.6.6) with 41 stars and one known importer on pkg.go.dev. The repo has no CI workflow directory, and the API has changed between 0.x releases (v0.5.0 replaced the eviction channel with synchronous return values).

## How it is fast

SIEVE only sets a visited bit on a hit, so reads never reorder a list and never take the global mutex. `Get` does one load from a concurrent puzpuzpuz/xsync map (key to int32 slot index), then one atomic OR on a per-slot uint64 that packs a bit-63 spinlock with the visited counter, then an atomic AND to unlock. Nodes live in a pre-allocated array linked by int32 indices, with a bump allocator and freelist, so steady state makes no per-entry heap allocations and, for scalar K/V, gives the GC no pointers to trace. Misses (insert), eviction (the SIEVE 'hand' walks the FIFO clearing visited bits until it finds an unvisited node) and Delete all go through one global sync.Mutex.

## Compared with alternatives

Against otter (the other catalogued golang-lru beater, with adaptive W-TinyLFU, TTL, loading, refresh and stats), pick go-sieve when you only need a fixed-count, read-heavy cache and want a tiny single-dependency codebase with zero steady-state allocations; pick otter when hit ratio or expiry matters. Against golang-fifo (also SIEVE in Go, with TTL and a reader-lock hit path per its README, backed only by a README table), go-sieve has the mutex-free hit path and stronger reproducible evidence: raw results are committed and there is a trace-replay harness.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/puzpuzpuz/xsync/v4 (v4.5.0 at v0.6.6). The benchmarks are a separate bench/ module that also pulls in hashicorp/golang-lru v2.0.7 and opencoff/go-mmap. |
| **Minimum toolchain** | go.mod on main/v0.6.6 declares go 1.27.1, the current Go release (v0.6.4-v0.6.5 declare go 1.26.3, and v0.6.3 declares go 1.26.1). All() needs Go 1.23+ iterators. |
| **Platforms** | Pure Go plus one go:linkname to runtime.procyield, so any Go target in principle. It was benchmarked only on Apple M4 darwin/arm64; x86-64 performance is not documented. |
| **Thread safety** | All methods are safe for concurrent use. Get takes only a per-slot spinlock (atomic OR/AND on a uint64). Add/Probe on a miss, eviction, Delete and Purge take one global mutex. All() is weakly consistent: it holds no lock across the loop body and may rarely yield the same key twice during a concurrent map resize. |
| **Drop-in for the baseline** | partial — Get(k) (V, bool), Len and Purge match golang-lru v2, and New also returns (cache, error). Add returns (Evicted, CacheResult) instead of a bool, Remove becomes Delete, and Contains/Peek/Keys/Values/Resize/RemoveOldest/GetOldest and NewWithEvict callbacks are missing. There is no equivalent of the ARC variant. |

## Gotchas

- The zero value of K is reserved ("" for strings, 0 for ints, the zero struct) and is not checked. Freed slots have their key zeroed, so a Get racing with the eviction of a zero key can return a spurious hit with a zero value. Offset or wrap such keys.
- The README calls Get 'lock-free', but it takes a per-slot test-and-set spinlock that backs off with runtime.procyield (via go:linkname) and then Gosched. Every attempt sets the visited bit, even a failed one or one on a stale index, so an unrelated entry can get an undeserved mark. The source comment also says the eviction scan is not strictly bounded under adversarial read load, and that scan runs while holding the global mutex.
- ProbeFunc is not singleflight: concurrent misses on the same key can each run the constructor. Only one value is stored, and the other callers get it back flagged as CacheHit.
- Purge does not zero old key/value slots, so the objects they point to stay reachable until the slots are reused. String and pointer K/V still leave GC-traced pointers in the node array; the GC savings are mainly for scalar types.

## Known shortcomings

- The 13-55x is vs golang-lru under contention (at 10 cores 7.53 vs 182.1 ns); on hit ratio ARC is best on 11 of 18 traces.
- Misses, Add, Delete and eviction all take one global mutex, so the author's Mixed_Parallel time worsens with cores (33 to 92 ns/op from 1 to 10 cores) and Delete loses to LRU (81 vs 69.5 ns). 'Lock-free Get' is really a per-slot spinlock; under Zipf 1.5 hot-key skew the lead is \~6%; the eviction scan is unbounded under adversarial reads. Hit ratio trails ARC (best on 11 of 18 traces).
- The zero key is reserved and unchecked (spurious zero-value hit); ProbeFunc is not singleflight; full capacity is preallocated; no TTL/callback/Peek/Resize. Pre-1.0 (v0.6.6), 41 stars, no CI; the latest tag needs Go 1.27.1; benchmarks are author-run on an M4 only from a dirty v0.6.4 tree.

## Caveats and trade-offs

All benchmarks were run by the repo author on one machine (Apple M4), with no independent confirmation, and the project is new with 41 stars. The speed win is about concurrent throughput, not hit ratio: at 10% cache size, ARC has the lowest miss ratio on 11 of 18 traces and LRU on 5, and SIEVE k=1 beats LRU on only 10 of 18. Single-threaded sequential replay is faster for LRU on 3 traces (block_traces_1, block_traces_2, msr_src1_0). Delete_Parallel is faster for LRU (69.54 vs 81.18 ns/op). At Zipf s=1.50 the Get advantage narrows to about 6% (94.19 vs 100.4 ns/op).

Lock-free reads only work with the columnar slot-state design (extra bookkeeping array); Delete_Parallel is the one micro-benchmark where SIEVE loses to LRU's simpler single-lock unlink (81.2 vs 69.5 ns/op); at extreme Zipf skew (s=1.50) SIEVE's advantage narrows to \~6%.

## Maintenance

Actively maintained by a single author (v0.6.6, last commit 2026-09-08), BSD-2-Clause, and small enough to vendor, but still pre-1.0 with API changes between 0.x releases and the latest tag requiring Go 1.27.1.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** bench-results.md compares go-sieve with hashicorp/golang-lru v2.0.7 LRU and ARC (pinned in bench/go.mod). The public harness is bench/bench_test.go and bench/replay_test.go, driven by bench/Makefile (`go test -bench=. -benchmem -count=3`, plus `-tags=trace` for replay). The page states go1.26.3 darwin/arm64 and an Apple M4 (4P+6E, GOMAXPROCS=10), so code, compiler, flags and CPU are all present.
- **Verifier notes:** The headline 13-55x and 2-6x numbers match the page. The record's core-scaling sentence was wrong: 5.5 and 121.1 ns/op are the GOMAXPROCS=4 values, and at 10 cores the numbers are 7.53 (Sieve) vs 182.1 (LRU). The metadata (BSD-2-Clause, 41 stars, last commit 2026-09-08, not a fork) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/opencoff/go-sieve>
  - <https://github.com/opencoff/go-sieve/blob/main/bench-results.md>
  - <https://raw.githubusercontent.com/opencoff/go-sieve/main/README.md>
  - <https://raw.githubusercontent.com/opencoff/go-sieve/main/bench/Makefile>
  - <https://raw.githubusercontent.com/opencoff/go-sieve/main/bench/go.mod>
  - <https://raw.githubusercontent.com/opencoff/go-sieve/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/opencoff/go-sieve>
  - <https://github.com/opencoff/go-sieve/blob/main/README.md>
  - <https://github.com/opencoff/go-sieve/blob/main/sieve.go>
  - <https://github.com/opencoff/go-sieve/blob/main/slotstate.go>
  - <https://github.com/opencoff/go-sieve/blob/main/options.go>
  - <https://github.com/opencoff/go-sieve/blob/main/pause.go>
  - <https://github.com/opencoff/go-sieve/blob/main/go.mod>
  - <https://github.com/opencoff/go-sieve/blob/v0.6.5/go.mod>
  - <https://github.com/opencoff/go-sieve/blob/v0.6.3/go.mod>
  - <https://github.com/opencoff/go-sieve/blob/main/Makefile>
  - <https://github.com/opencoff/go-sieve/blob/main/bench-results.md>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/README.md>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/Makefile>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/go.mod>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/bench_test.go>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/results/synthetic.txt>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/results/sweep.txt>
  - <https://github.com/opencoff/go-sieve/blob/main/bench/results/trace.txt>
  - <https://github.com/opencoff/go-sieve/commits/main>
  - <https://github.com/opencoff/go-sieve/tags>
  - <https://github.com/opencoff/go-sieve/issues?q=is%3Aissue>
  - <https://github.com/opencoff/go-sieve/issues/2>
  - <https://pkg.go.dev/github.com/opencoff/go-sieve?tab=importedby>
  - <https://github.com/search?q=opencoff%2Fgo-sieve+path%3Ago.mod&type=code>
  - <https://raw.githubusercontent.com/DNSCrypt/dnscrypt-proxy/master/go.mod>
  - <https://raw.githubusercontent.com/puzpuzpuz/xsync/v4.5.0/go.mod>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/stubs.go>
  - <https://raw.githubusercontent.com/hashicorp/golang-lru/v2.0.7/lru.go>
  - <https://go.dev/dl/?mode=json>
  - <https://github.com/maypok86/otter>
  - <https://github.com/scalalang2/golang-fifo>
  - <https://hn.algolia.com/api/v1/search?query=%22go-sieve%22>
  - https://hn.algolia.com/api/v1/search?query=opencoff%20go-sieve&tags=(story,comment)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/opencoff/go-sieve`) · [data/wave6/enrich/raw/github_com_opencoff_go_sieve.json](../../../data/wave6/enrich/raw/github_com_opencoff_go_sieve.json) (enrichment confidence 0.85)

</details>
