# valyala/fastrand (Go scalable per-CPU pseudorandom generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Tiny Go xorshift32 PRNG with a sync.Pool of generators; out-scaled the mutex-locked global math/rand under parallel load.

| | |
|---|---|
| **Beats** | Go math/rand (global rand.Int31n and rand.New(...) instances) |
| **Claimed result** | README: fastrand.Uint32n 29.7, 17.6 and 14.2 ns/op versus math/rand Int31n 31.8, 51.2 and 145 ns/op at GOMAXPROCS=1, 2, 4; per-goroutine RNG.Uint32n 6.50 ns/op versus rand.New(...).Int31n 17.9 ns/op at GOMAXPROCS=1. README text: comparable at one CPU, 3x faster at two CPUs and 10x faster at four CPUs. |
| **Workload** | go test -bench ns/op for Uint32n, per-goroutine RNG.Uint32n and math/rand Int31n at GOMAXPROCS=1, 2 and 4. |
| **Metric** | latency |
| **Compiler and flags** | go test -bench=. with GOMAXPROCS=1, 2 and 4 (goos linux, goarch amd64); Go version not stated; benchmarks in fastrand_timing_test.go |
| **Adoption** | 206 stars |
| **Last commit** | 2021-09-15 |
| **Links** | [repository](https://github.com/valyala/fastrand) · [benchmark](https://github.com/valyala/fastrand) |

## Verdict

The README's go test -bench output (goos linux, goarch amd64; CPU and Go version not stated; results committed in April 2017) uses b.RunParallel loops drawing bounded values below 1e6: fastrand.Uint32n took 29.7, 17.6 and 14.2 ns/op versus math/rand's global Int31n at 31.8, 51.2 and 145 ns/op at GOMAXPROCS=1, 2 and 4, and a per-goroutine RNG.Uint32n took 6.50, 3.36 and 3.30 ns/op versus a per-goroutine rand.New(rand.NewSource(42)).Int31n at 17.9, 11.0 and 8.35 ns/op. The global-function gap measured lock contention in pre-Go 1.21 math/rand, which Go 1.21 removed for unseeded programs.

## Use it when

- Legacy Go code pinned to Go 1.20 or older that calls top-level math/rand functions from many goroutines and spends measurable time contending on the global generator's lock.
- Hot loops needing cheap bounded uint32 values for non-security decisions: random load-balancer or shard selection, sampling, jitter, test data.
- Single-goroutine or per-worker code that can own a fastrand.RNG value, where a 4-byte xorshift state and a multiply-shift bound are good enough.
- As a reference for the pool-of-generators pattern if you must vendor something very small (about 80 lines, MIT).

## Skip it when

- Go 1.21 and later: unseeded top-level math/rand functions already use a lock-free fastSource that calls the runtime's per-M wyrand (fastrand64), so the multi-CPU contention this package fixes is gone; prefer the standard library or math/rand/v2 there. No benchmark of fastrand against Go 1.21+ math/rand exists.
- Anything security-related: the package doc says to use crypto/rand for cryptographically secure numbers, and seeds come from the wall clock.
- Simulation or statistics work: a 32-bit xorshift on 4 bytes of state has period at most 2^32-1, small next to the 64-bit and larger generators in this category; Uint32n's multiply-shift without rejection is slightly biased whenever maxN is not a power of two.
- Reproducible streams from the global functions: pooled generators are created and reseeded from the clock whenever the pool is empty (sync.Pool can drop objects at garbage collection), so sequences cannot be replayed.
- Code needing floats, 64-bit integers, shuffles or other distributions; only uint32 output is offered.

## How it is fast

The generator is Marsaglia's 32-bit xorshift (shifts 13, 17, 5) on a 4-byte state, and bounded values use Lemire's multiply-shift reduction ((x \* maxN) &gt;&gt; 32) with no division or rejection loop. The scaling comes from the sync.Pool: each P tends to reuse its own pooled RNG, avoiding the single mutex that guarded the global math/rand source in Go versions before 1.21. The per-goroutine RNG path (6.50 ns/op at GOMAXPROCS=1) is cheaper again because it skips the pool Get/Put.

## Compared with alternatives

Among Go siblings, pgregory.net/rand (flyingmutant/rand) is maintained, offers the full math/rand-style API on sfc64 and benchmarks against math/rand/v2, and vpxyz/xorshift offers stronger 64-bit xorshift/xoroshiro sources; pick valyala/fastrand only when you need a tiny vendored uint32 helper on an old Go toolchain, and lukechampine/frand when you need cryptographic strength.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (standard library sync and time only) |
| **Minimum toolchain** | not documented; go.mod declares only the module path with no go directive (Go modules support was added in 2019) |
| **Platforms** | any platform Go supports (pure Go, no assembly) |
| **Thread safety** | Package-level Uint32 and Uint32n are documented as safe from concurrent goroutines; RNG methods are documented as unsafe for concurrent use. |
| **Drop-in for the baseline** | partial — Uint32n(n) can replace rand.Int31n(n) call sites for non-negative bounds, but the function names, uint32 types and missing methods (Int63, Float64, Intn, Shuffle, Seed on the global stream) mean it is not a drop-in replacement for math/rand. |

## Gotchas

- Seeds come from time.Now().UnixNano() folded to 32 bits when a pooled RNG is first used; open issue #4 (2021) notes that many goroutines starting together can get identically seeded generators on systems with coarse clock resolution, and that the pool holds one RNG per concurrent caller rather than strictly one per CPU.
- RNG.Seed(0) does not give a fixed stream: a zero state is treated as unseeded and is replaced by a clock-derived seed on the next call.
- Uint32n has no argument check: Uint32n(0) silently returns 0.
- The README benchmark at GOMAXPROCS=1 shows only a small gain for the global function (29.7 vs 31.8 ns/op); most of the single-thread gain is from owning an RNG (6.50 ns/op), which you could equally get by owning a rand.New(...) source (17.9 ns/op) or a faster per-goroutine generator.

## Known shortcomings

- Tier C: README numbers from the public fastrand_timing_test.go with no Go version or CPU stated. Since Go 1.20 the global math/rand uses a per-thread wyrand source without the mutex (seen as a search snippet; go.dev blocked), so the scaling gap it was built to avoid is likely gone. Last commit 2021-09-15, abandoned.
- Correction to the verifier's caveat: Go 1.20's math/rand global source is still a lockedSource (only auto-seeded); the lock-free per-M wyrand fastSource arrived in Go 1.21 (checked golang/go at go1.20 and go1.21.0), so the contention gap is gone on Go 1.21+ but was never re-measured. xorshift32 state; Uint32n is multiply-shift with no rejection, so biased; pool RNGs are seeded from the clock (issue #4 open since 2021, same seed possible) and Seed(0) falls back to a clock seed; uint32-only API; 4 PRs closed unmerged on 2024-04-04.

## Caveats and trade-offs

Go package, not callable from C++. README benchmark output has no CPU model or Go version. The win is about lock contention in Go's global math/rand of that era: per a WebSearch snippet of the Go blog post 'Evolving the Go Standard Library with math/rand/v2' (go.dev blocked here), Go 1.20 replaced the mutex-protected global generator with a per-thread wyrand generator for programs that do not call rand.Seed, so the multi-CPU scaling gap is likely gone on current Go. Single-CPU gain over math/rand Int31n is small (29.7 vs 31.8 ns/op); the larger single-CPU gain is per-goroutine RNG.Uint32n 6.50 vs rand.New(...).Int31n 17.9 ns/op.

Not cryptographically secure. Scaling comes from a sync.Pool of per-P generators, so the global functions are not a single reproducible stream; the README's own TODO says real per-CPU generators are still to be done.

## Maintenance

Abandoned: last commit 2021-09-15 (RNG.Seed), issue #4 open since 2021 with no reply, and four contributor PRs (crypto/rand seeding, go.mod version, sync.Pool New, test fix) closed unmerged in April 2024; MIT and small enough to vendor, but on Go 1.21+ the standard library makes it largely unnecessary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows go test -bench output for fastrand.Uint32n and RNG.Uint32n against math/rand Int31n and rand.New(...).Int31n at GOMAXPROCS=1/2/4; the benchmark code (fastrand_timing_test.go) is public, but no Go version or CPU model is given (only goos linux / goarch amd64), so first-party with partial methodology.
- **Verifier notes:** Numbers match README exactly. Metadata checked on github.com: MIT, 206 stars, 17 forks, not archived or a fork, last commit 2021-09-15 (abandoned). The Go 1.20 math/rand change comes from a search snippet, not an opened page.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/valyala/fastrand>
  - <https://github.com/valyala/fastrand/commits>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/fastrand_timing_test.go>
- **Sources the enricher read:**
  - <https://github.com/valyala/fastrand>
  - <https://github.com/valyala/fastrand/commits>
  - <https://github.com/valyala/fastrand/issues?q=is%3Aissue>
  - <https://github.com/valyala/fastrand/issues/4>
  - <https://github.com/valyala/fastrand/pulls?q=is%3Apr>
  - <https://github.com/valyala/fastrand/pull/6>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/fastrand.go>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/fastrand_timing_test.go>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/fastrand_test.go>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/go.mod>
  - <https://raw.githubusercontent.com/valyala/fastrand/HEAD/LICENSE>
  - <https://github.com/golang/go/blob/go1.20/src/math/rand/rand.go>
  - <https://github.com/golang/go/blob/go1.21.0/src/math/rand/rand.go>
  - <https://github.com/golang/go/blob/go1.21.0/src/runtime/stubs.go>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/valyala/fastrand`) · [data/wave8/enrich/raw/github_com_valyala_fastrand.json](../../../data/wave8/enrich/raw/github_com_valyala_fastrand.json) (enrichment confidence 0.8)

</details>
