# vpxyz/xorshift (Go xorshift\*, xorshift+, xoroshiro and splitmix64 generators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go ports of Vigna's xorshift/xoroshiro/xoshiro and SplitMix64 generators; raw calls 2-3x faster than math/rand's default source.

| | |
|---|---|
| **Beats** | Go math/rand (rand.NewSource Int63 source, and rand.New(source).ExpFloat64()) |
| **Claimed result** | Raw source ns/op: math/rand BenchmarkRandSource 4.93 versus XorShift128Plus 2.42, XorShift1024Star 2.40, Xoroshiro128Plus 2.66, Xoroshiro256PlusPlus 3.86, Xoroshiro256StarStar 3.93, Xoroshiro512Plus 6.15, Xoroshiro512StarStar 6.34, SplitMix64 1.61. Wrapped in rand.Rand (ExpFloat64): BenchmarkRand 10.2 versus XorShift128Plus 8.42, Xoroshiro128Plus 8.10, SplitMix64 8.66, but Xoroshiro256PlusPlus and Xoroshiro256StarStar 11.7, XorShift1024Star 9.61, Xoroshiro512Plus 13.2 and Xoroshiro512StarStar 13.6. Raw speedup is about 2.0x for XorShift128Plus and 3.1x for SplitMix64; once wrapped it is only about 1.2x, and the 256- and 512-bit-state xoroshiro variants are slower than math/rand (derived from page data). |
| **Workload** | go test -bench: nanoseconds per call of a raw Uint64 from each source versus rand.NewSource(...).Int63, and per rand.New(source).ExpFloat64() call for the wrapped variants. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-3840QM, Fedora 31, Linux 5.6.9 |
| **Compiler and flags** | Go 1.14, go test -bench=. with default flags; benchmark code is xorshift_test.go in the repo (includes the math/rand baseline) |
| **Adoption** | 16 stars |
| **Last commit** | 2020-05-02 |
| **Links** | [repository](https://github.com/vpxyz/xorshift) · [benchmark](https://github.com/vpxyz/xorshift) |

## Verdict

The author's go test -bench run (Go 1.14, default flags, i7-3840QM, Fedora 31, 2020) measured raw Uint64 calls at 1.61 ns (SplitMix64) to 2.66 ns (128-bit-state generators) versus 4.93 ns for math/rand.NewSource(...).Int63 called through the Source interface, so about 2-3x, partly from static versus interface dispatch; wrapped in rand.Rand for ExpFloat64 the best variants are about 1.2x faster (8.10-8.66 ns versus 10.2 ns) and the 256/512-bit variants are slower. math/rand/v2 was not measured.

## Use it when

- Go code (not C++) that calls Uint64() directly on a concrete generator in a hot loop, e.g. Monte Carlo or simulation inner loops, where the README shows 1.6-2.7 ns/op versus 4.93 ns/op for math/rand's source on an i7-3840QM.
- Go programs pinned to an older toolchain (go 1.9+ per go.mod) that lack math/rand/v2 and want a small MIT-licensed SplitMix64 or xoshiro256\*\* source.
- Single-goroutine code, or one generator per goroutine, since nothing is locked.
- As readable reference code for porting Vigna's generators, after checking each one against the reference outputs (see gotchas).

## Skip it when

- From C or C++: it is a Go package; use Vigna's reference C code or a catalogued C/C++ generator instead.
- Through rand.Rand (rand.New(src).Float64/ExpFloat64 etc.): the README's wrapped rows gain only about 1.2x (8.1-8.7 ns versus 10.2 ns), and the 256- and 512-bit variants are slower than math/rand (11.7-13.6 ns).
- When you need Jump() to create non-overlapping parallel streams with xoroshiro128plus or xoroshiro512starstar: both have defects (see gotchas).
- Concurrent use of one generator: README says it is not concurrency-safe.
- Security-sensitive randomness: none of these generators is cryptographic.

## How it is fast

The generators are linear xorshift / xor-rotate-shift-rotate recurrences over a few 64-bit words, costing a handful of shifts, xors and one add or multiply per output; the benchmark compares them with math/rand's default source called through the rand.Source interface (its internals were not inspected here). The 2020 rewrite switched to math/bits.RotateLeft64, which Vigna suggested in issue #3 because the standard function can be intrinsified by the compiler, and the 256/512-bit variants copy the state into locals because, per a source comment, the Go compiler generated slower code for array indexing.

## Compared with alternatives

Among Go siblings, pick pgregory.net/rand (flyingmutant/rand, sfc64, maintained, measured against math/rand/v2) for a modern faster rand.Rand replacement and valyala/fastrand for many goroutines sharing an RNG; pick this only if you specifically want a Vigna generator family in pure Go on an old toolchain and can audit the variant you use. C++ users should take the C/C++ siblings (e.g. simdrng, Xoshiro256PlusSIMD, testingRNG's lehmer64/aesctr) instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go standard library math/bits only) |
| **Minimum toolchain** | Go 1.9 (go.mod 'go 1.9'; math/bits.RotateLeft64 needs 1.9); benchmarked on Go 1.14 |
| **Platforms** | any platform Go supports (pure Go, no assembly) |
| **Thread safety** | not concurrency-safe; the README says to wrap a generator with a monitor goroutine |
| **Drop-in for the baseline** | partial: every generator implements rand.Source64, so rand.New(xorshift128plus.NewSource(seed)) replaces rand.New(rand.NewSource(seed)), but the output stream differs and the wrapped speedup is small |

## Gotchas

- xoroshiro512starstar's state update is written 's6 ^ ^s7 ^ s3'; in Go the second '^' is unary bitwise NOT, so it complements s7, unlike the repo's own xoroshiro512plus ('s6 ^ s7 ^ s3') which shares the same xoshiro512 engine. The 512\*\* generator therefore does not reproduce Vigna's xoshiro512\*\* sequence and its Jump polynomial no longer applies (read in source; not run).
- xoroshiro128plus uses the original 2016 parameters (rotl 55, shift 14, rotl 36, as in sysbench's copy of Vigna's code) but its Jump() uses internal.Jump128 = {0x8a5cd789635d2dff, 0x121fd2155c472f96}, the xorshift128+ jump constants that XorShift128Plus.Jump also uses; Vigna's jump for this xoroshiro128+ is {0xbeac0467eba5facb, 0xd86b048b86aa9922}, so Jump() is not the advertised 2^64-step jump. The repo's xoroshiro128starstar uses the newer 24/16/37 parameters and the matching jump constants.
- The packages are named 'xoroshiro256\*' and 'xoroshiro512\*' but implement Vigna's xoshiro256/xoshiro512 engines (the 256-bit update and jump constants match xoshiro256); look them up under xoshiro. Package docs also call 256++ a 'floating-point' generator although ++ and \*\* are Vigna's all-purpose scramblers.
- Int63() masks off the top bit (keeping the weak low bits) for most generators; only the + scramblers xoroshiro128plus/256plus/512plus were changed in 2020 to return the upper 63 bits after Vigna's issue #1. Vigna also reported a jump operator-precedence bug (issue #2, fixed 2020-02-27) and recommended reference-output unit tests, which the repo still lacks (xorshift_test.go has only benchmarks). The README example code does not compile as written (xorshift256plus.NewSource, unqualified XorShiftExt, rand not imported).

## Known shortcomings

- Tier A on xorshift_test.go (Go 1.14, i7-3840QM), but once wrapped in rand.Rand, Xoroshiro256 (11.7 ns/op) and Xoroshiro512 (13.2/13.6 ns/op) are slower than math/rand (10.2 ns/op); the raw rows compare a concrete-type Uint64 call against Int63 through the rand.Source interface. Last commit 2020-05-02.
- Capped A to C (retier-11): xoroshiro512starstar's update is 's6 ^ ^s7 ^ s3' (unary NOT complements s7; the package's own 512plus has 's6 ^ s7'), so it is not Vigna's xoshiro512\*\* and its Jump is invalid; xoroshiro128plus (2016 parameters 55/14/36) Jump uses the xorshift128+ constants {0x8a5cd789635d2dff, 0x121fd2155c472f96} instead of {0xbeac0467eba5facb, 0xd86b048b86aa9922}. Packages named xoroshiro256/512 are actually xoshiro; most Int63 implementations keep the weak low bits; no reference-output tests (Vigna asked in issue #2); the README example does not compile.

## Caveats and trade-offs

Go package, not callable from C++. Numbers are from 2020 on a 2012-era laptop CPU with Go 1.14, run by the repo author. The raw rows are asymmetric: the generators' Uint64() is called on the concrete type returned by NewSource (static dispatch, inlinable), while the baseline calls Int63() through the rand.Source interface (dynamic dispatch), so part of the raw 2-3x gap is call overhead. The wrapped rows go through rand.Rand on both sides and show only about 1.2x, with the 256/512-bit-state variants slower than math/rand. The baseline is Go's default math/rand source, not a C++ standard facility. Go's standard library has since added math/rand/v2 (PCG, ChaCha8), so the gap against current Go is likely smaller (background knowledge, not tested). [retier] xoroshiro512starstar's update complements s7 ('s6 ^ ^s7 ^ s3'), so it is not Vigna's xoshiro512\*\* and its Jump is invalid; xoroshiro128plus Jump uses xorshift128+ constants; packages named xoroshiro256/512 are actually xoshiro; most Int63 implementations keep the weak low bits; no reference-output tests (issue #2); the README example does not compile. Once wrapped in rand.Rand, Xoroshiro256 (11.7 ns/op) and Xoroshiro512 (13.2/13.6) are slower than math/rand (10.2); the raw rows compare a concrete-type Uint64 call against Int63 through the rand.Source interface. Last commit 2020-05-02.

Generators are not concurrency-safe (README says to wrap with a monitor goroutine). Generators with state larger than 64 bits are seeded via SplitMix64 as Vigna suggests. Implements Vigna's generators, so it carries their known linearity weaknesses in low bits for the + scramblers.

## Maintenance

Abandoned since 2020-05-02 (44 commits; the only three issues, filed by Vigna on 2020-01-30, were fixed 2020-02-27) but MIT-licensed, dependency-free and tiny; vendor only the generator you need and test it against Vigna's reference outputs first, avoiding xoroshiro512starstar and xoroshiro128plus.Jump as written.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** The README benchmark block comes from public benchmark code (xorshift_test.go, which includes BenchmarkRandSource on math/rand.NewSource Int63 and BenchmarkRand on rand.New(...).ExpFloat64). It states the toolchain and flags (Go 1.14, go test -bench=., defaults) and the CPU (i7-3840QM, Fedora 31, Linux 5.6.9), so A.
- **Retiered** A to C: Capped A to C under the correctness-bug rule: the enricher found the xoroshiro512starstar update uses 's6 ^ ^s7 ^ s3' (unary NOT complements s7; the package's own 512plus has 's6 ^ s7'), so it is not Vigna's xoshiro512\*\* and its Jump is invalid, and xoroshiro128plus Jump uses xorshift128+ constants {0x8a5cd789635d2dff, 0x121fd2155c472f96} instead of {0xbeac0467eba5facb, 0xd86b048b86aa9922}. The timed generators therefore include ones that do not compute the algorithms they are named for, and the repo has no reference-output tests (Vigna asked for them in issue #2). The benchmark itself (xorshift_test.go, Go 1.14, i7-3840QM) is unchanged.
- **Verifier notes:** All quoted ns/op values match the README; the record omitted that several wrapped variants lose to math/rand, which I added. Metadata confirmed on github.com and the LICENSE file: MIT, 16 stars, 1 fork, not a fork or archived, last commit 2020-05-02 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/vpxyz/xorshift>
  - <https://github.com/vpxyz/xorshift/commits>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/README.md>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift_test.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/splitmix64/splitmix64.go>
- **Sources the enricher read:**
  - <https://github.com/vpxyz/xorshift>
  - <https://github.com/vpxyz/xorshift/commits>
  - <https://github.com/vpxyz/xorshift/issues?q=is%3Aissue>
  - <https://github.com/vpxyz/xorshift/issues/1>
  - <https://github.com/vpxyz/xorshift/issues/2>
  - <https://github.com/vpxyz/xorshift/issues/3>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/README.md>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift_test.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/go.mod>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/doc.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/internal/internal.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/splitmix64/splitmix64.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift64star/xorshift64star.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift128plus/xorshift128plus.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift1024star/xorshift1024star.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift1024starphi/xorshift1024starphi.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xorshift4096star/xorshift4096star.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro128plus/xoroshiro128plus.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro128starstar/xoroshiro128starstar.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro256plus/xoroshiro256plus.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro256plusplus/xoroshiro256plusplus.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro256starstar/xoroshiro256starstar.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro512plus/xoroshiro512plus.go>
  - <https://raw.githubusercontent.com/vpxyz/xorshift/HEAD/xoroshiro512starstar/xoroshiro512starstar.go>
  - <https://raw.githubusercontent.com/akopytov/sysbench/master/src/xoroshiro128plus.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/vpxyz/xorshift`) · [data/wave8/enrich/raw/github_com_vpxyz_xorshift.json](../../../data/wave8/enrich/raw/github_com_vpxyz_xorshift.json) (enrichment confidence 0.75)

</details>
