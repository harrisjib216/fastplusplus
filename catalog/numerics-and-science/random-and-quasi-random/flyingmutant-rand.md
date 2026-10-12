# pgregory.net/rand (sfc64-based replacement for Go math/rand)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MPL-2.0 AND BSD-3-Clause` · 🟡 stale

> Go package pgregory.net/rand: sfc64-based \*Rand whose draw methods run about 1.5-3.3x faster than math/rand/v2's PCG-backed \*Rand.

| | |
|---|---|
| **Beats** | Go math/rand/v2 (PCG source and top-level functions), math/rand, golang.org/x/exp/rand |
| **Claimed result** | Versus math/rand/v2 on i7-10510U: Rand_Float32 7.67 ns to 3.61 ns (-52.93%), Rand_Int31n 10.2 to 4.2 ns (-59.15%), Rand_Uint64 6.86 to 3.93 ns (-42.64%), Rand_Shuffle 711 to 412 ns (-42.12%), but top-level Uint64 3.06 to 3.20 ns (+4.75%, slower) and Float64 3.29 to 3.55 ns (+7.92%, slower). Versus math/rand on Xeon E5-2680 v3 with 48 threads: top-level Uint64 193 ns to 1 ns (-99.72%), Rand_Uint32 7.82 to 1.72 ns (-77.98%). |
| **Workload** | Go benchmark suite (benchstat output) of Float64, Intn, Uint64, Shuffle, Perm, NormFloat64, ExpFloat64 and constructor cost, versus math/rand/v2 on a laptop and versus math/rand and x/exp/rand on a 48-thread Xeon. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10510U @ 1.80GHz (versus math/rand/v2) and Intel Xeon E5-2680 v3 @ 2.50GHz (versus math/rand and x/exp/rand) |
| **Compiler and flags** | Go toolchain, linux/amd64; Go version and flags not stated |
| **Adoption** | 240 stars |
| **Last commit** | 2024-11-05 |
| **Links** | [repository](https://github.com/flyingmutant/rand) · [benchmark](https://raw.githubusercontent.com/flyingmutant/rand/HEAD/README.md) |

## Verdict

The author's benchstat tables (n=8-10, public rand_bench_\*_test.go files, linux/amd64, Go version and flags not stated) show \*Rand draw methods 31-69 percent faster than math/rand/v2's \*Rand over a PCG source on an Intel Core i7-10510U, while top-level functions are 2.6-15 percent slower and Seed is about 80x slower; against legacy math/rand and x/exp/rand on a 48-thread Xeon E5-2680 v3, \*Rand draw methods are 39-87 percent faster and parallel top-level calls about 99 percent faster because of lock contention in the old packages.

## Use it when

- Hot Go loops on a per-goroutine \*Rand that draw floats, bounded ints, shuffles or permutations: Rand_Float32 7.67 to 3.61 ns, Rand_Int31n 10.2 to 4.2 ns, Rand_Intn_Big 28.7 to 8.8 ns and Rand_Shuffle 711 to 412 ns versus math/rand/v2 with its PCG source on an i7-10510U.
- Code still on legacy math/rand or golang.org/x/exp/rand, especially calling top-level functions from many goroutines: on a 48-thread Xeon E5-2680 v3, top-level Uint64 drops from 193 ns to about 1 ns because there is no global lock.
- Simulations that need a seeded generator whose output is identical on 32/64-bit and little/big-endian targets (stated in the README) and whose state can be serialized cheaply (MarshalBinary 30.5 to 3.8 ns versus x/exp/rand).
- Constructing many generators: rand.New allocates 48 bytes once versus 5.42 kB for math/rand.

## Skip it when

- You only call top-level functions on Go 1.22+: they are a thin wrapper over math/rand/v2's runtime generator, and the README shows them 2.6-15 percent slower than math/rand/v2 (Uint64 3.06 to 3.20 ns, Float64 3.29 to 3.55 ns, Intn_Big 6.46 to 7.45 ns).
- Frequent reseeding: Rand.Seed runs 12 warm-up rounds and costs 46.09 ns versus 0.57 ns for math/rand/v2's PCG.
- Code that depends on the Source interface, a custom Source, or a global Seed() for reproducibility: they are deliberately absent.
- Security-sensitive randomness: the package doc says outputs may be predictable regardless of seeding; use crypto/rand.
- C or C++ projects: not callable without cgo; copy the 10-line sfc64 step function instead.

## How it is fast

\*Rand embeds a concrete SFC64 generator (Chris Doty-Humphrey's small fast chaotic generator: 256-bit state, add/xor/shift/rotate, no multiply) instead of calling through the Source interface, and the code is written to fit Go's inlining budget. Floats come from masking 24 or 53 bits and multiplying by 2^-24 or 2^-53; bounded integers use a single 64x64-to-128 fixed-point multiply for n below 2^32 and Stephen Canon's two-multiply method above that, with no division or rejection loop. Normals and exponentials reuse Go's ziggurat tables. Top-level functions draw from Go's goroutine-local runtime generator, so they avoid math/rand's global mutex.

## Compared with alternatives

Pick it in Go services and simulations that use a \*Rand per goroutine; the catalogued siblings are C, C++, Python or R (NumPy and randomgen expose the same SFC64 algorithm to Python, fastrand speeds up Python's random, testingRNG and Romu cover C). For C++ use the SFC64 or Romu entries directly.

## Integration

| | |
|---|---|
| **Form** | module (Go module pgregory.net/rand) |
| **Dependencies** | none at runtime (go.mod lists valyala/fastrand, golang.org/x/exp and pgregory.net/rapid for tests and benchmarks) |
| **Minimum toolchain** | Go 1.18 (go.mod); CI tests Go 1.18, 1.19, 1.22 and 1.23 |
| **Platforms** | any Go target; CI runs Linux, Windows and macOS; README states identical deterministic output on 32/64-bit and big/little-endian |
| **Thread safety** | Top-level functions are safe for concurrent use (goroutine-local runtime sources); \*Rand methods are not safe for concurrent use, per the package doc. |
| **Drop-in for the baseline** | partial: same \*Rand methods and top-level functions as math/rand, but no Source interface, no top-level Seed(), New takes uint64 seeds instead of a Source, and seeded streams differ from math/rand and math/rand/v2 |

## Gotchas

- Uint32n (and so Intn, Int31n, Shuffle and Perm for n below 2^32) uses one multiply with no rejection step; the code comment says the result is unbiased with probability 1 - 2^-32 and argues detecting the bias needs at least 2^64 samples.
- The top-level source depends on Go version and build tags: math/rand/v2's ChaCha8-based runtime generator on Go 1.22+, maphash on 1.18-1.21, or a go:linkname to runtime.fastrand64/runtime.rand with -tags unsafe; issue #8 notes the maphash path on Go 1.19-1.21 can never return 0.
- rand.New() with no seed skips the warm-up rounds and takes its three state words straight from the runtime generator; pass explicit seeds for reproducible runs.
- Licensing is split: MPL-2.0 for most files and BSD-3-Clause (LICENSE-go) for the ziggurat files copied from Go's standard library.

## Known shortcomings

- Pure Go, not callable from C++ (cross-language scope); against math/rand/v2 several results are slower (Intn_Big +15%, top-level Uint64 and Float64, Seed 0.57 to 46 ns); the \~99% gains vs math/rand come from lock contention.
- Go only, not callable from C++. On Go 1.22+ the top-level functions wrap math/rand/v2 rand.Uint64 (runtime ChaCha8) and the README shows them 2.6-15% slower than v2; only \*Rand methods win. The wyrand top-level note applies only to Go &lt;1.22 or -tags unsafe.

## Caveats and trade-offs

README benchmarks run by the author (benchstat, n=8-10) with CPU stated but no Go version or flags; the benchmark code is public in rand_bench_\*_test.go. The win over math/rand/v2 is mixed: top-level Uint64 (+4.75%), Float64 (+7.92%), Intn (+2.58%) and Intn_Big (+15.35%) are slower than v2, and Rand_Seed goes from 0.57 ns to 46.09 ns (+7995%). The headline gains are in \*Rand methods (float conversion, bounded ints, shuffle, perm) and against the legacy math/rand package. The roughly 99% gains against math/rand and x/exp/rand top-level functions on 48 threads come from lock contention on the global source; this package's top-level functions use goroutine-local runtime generators (wyrand via runtime.fastrand64 on most platforms), not sfc64. Go's own PCG source in math/rand/v2 is the closest named baseline. Go-only: not callable from C++. Files derived from Go's standard library are under BSD-3-Clause (LICENSE-go); the rest is MPL-2.0.

Go-only; deliberately omits the Source interface and top-level Seed(); generator is sfc64; Rand_New costs 48 bytes and seeding (Rand_Seed 46.09 ns versus 0.57 ns) is much slower than in math/rand/v2.

## Maintenance

Stale since 2024-11-05 but declared stable by its README, with 240 stars, CI across three OSes and four Go versions, and a permissive MPL-2.0/BSD-3-Clause license; it is a Go library, outside the C++ list unless cross-language entries are pulled forward.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchstat tables run by the author against math/rand/v2, math/rand and x/exp/rand with CPU model stated and public benchmark code (rand_bench_test.go, rand_bench_std_pcg_test.go, rand_bench_std_test.go, rand_bench_x_test.go), but no Go version or build flags, so C.
- **Verifier notes:** All quoted numbers match the README rows. Scope flag: pure Go library, not C/C++-callable, so it may belong with the queued cross-language entries rather than the C++ list. Metadata (240 stars, MPL-2.0 plus BSD-3-Clause LICENSE-go, last commit 2024-11-05, stale) checked and correct.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/README.md>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/LICENSE-go>
  - <https://github.com/flyingmutant/rand>
  - <https://github.com/flyingmutant/rand/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/README.md>
  - <https://github.com/flyingmutant/rand>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/go.mod>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/rand.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/sfc64.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global_go118.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global_go119.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global_go122.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global_unsafe.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/global_unsafe_go122.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/rand_generic.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/std_normal.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/std_exp.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/rand_bench_test.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/rand_bench_std_pcg_test.go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/LICENSE-go>
  - <https://raw.githubusercontent.com/flyingmutant/rand/HEAD/.github/workflows/ci.yml>
  - <https://github.com/flyingmutant/rand/issues?q=is%3Aissue>
  - <https://github.com/flyingmutant/rand/issues/8>
  - <https://github.com/flyingmutant/rand/issues/6>
  - https://go.dev/blog/chacha8rand (WebSearch snippet only: Go 1.22 runtime and math/rand/v2 top-level functions use per-core ChaCha8)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flyingmutant/rand`) · [data/wave8/enrich/raw/github_com_flyingmutant_rand.json](../../../data/wave8/enrich/raw/github_com_flyingmutant_rand.json) (enrichment confidence 0.85)

</details>
