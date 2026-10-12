# frand (lukechampine/frand, Go userspace CSPRNG)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Go userspace CSPRNG: a sync.Pool of crypto/rand-seeded ChaCha8 generators, far faster than crypto/rand for bulk and parallel reads.

| | |
|---|---|
| **Beats** | Go crypto/rand (and math/rand in parallel benchmarks) |
| **Claimed result** | README prose: 20x faster than crypto/rand when generating large amounts of random data, and over 100x faster when generating data in parallel; as fast and convenient as math/rand. No table or numbers beyond these ratios. |
| **Workload** | Generating large amounts of random data, sequentially and in parallel. |
| **Metric** | throughput |
| **Adoption** | 93 stars |
| **Last commit** | 2024-10-07 |
| **Links** | [repository](https://github.com/lukechampine/frand) · [benchmark](https://github.com/lukechampine/frand) |

## Verdict

The current README claims 20x faster than crypto/rand for large reads and over 100x in parallel, but gives no hardware, Go version or results. The only published numbers are in the pre-2024 README for the ChaCha12 fast-key-erasure version: Read of 512 KB 5094 vs 239 MB/s (about 21x, derived from page data), and with 64 goroutines 19665 vs 191 MB/s (about 103x, derived from page data); math/rand was faster for Intn and Perm. For the ChaCha8 generator frand now wraps, a 2025 Lemire benchmark (search snippet only; code in lemire/Code-used-on-Daniel-Lemire-s-blog 2025/10/15) reports 2.6 ns vs 51 ns per uint64 for ChaCha8 vs crypto/rand on an Apple M4. That supports the order of magnitude for the generator but does not measure frand itself.

## Use it when

- Go services that need lots of unpredictable bytes (tokens, nonces, salts, test data) and are bottlenecked on crypto/rand.Read, especially from many goroutines at once.
- Replacing math/rand in Go code where predictability is a bug: hash-table salts, randomized test cases that must differ run to run, load-balancer jitter.
- Bulk fills of hundreds of KB per call, where the old README measured 5094 MB/s vs 239 MB/s for crypto/rand on 512 KB reads.
- Code that wants Intn/Perm/Shuffle helpers on a secure source without handling errors on every call.

## Skip it when

- C or C++ projects: this is a pure Go module with no C ABI; for a C userspace random pool see randp or the aesctr generator in testingRNG.
- Long-lived key material where you want the kernel to hold the state: the generator state lives in process memory and no new entropy is mixed in after the one-time seed (README).
- Small-integer hot loops (Intn, Perm) where an insecure PRNG is acceptable: the old README table had math/rand faster (Intn 20 vs 45 ns/op, Perm(32) 789 vs 954 ns/op), and Uint64n still uses modulo with rejection rather than Lemire's nearly divisionless method (issue #3, open since 2020).
- Reproducible seeded streams across versions: NewCustom output changed when the backend moved from ChaCha12 to ChaCha8, and the bufsize and rounds arguments are now ignored.
- Go 1.22 and older toolchains: go.mod requires Go 1.23.1 because it depends on math/rand/v2.ChaCha8.

## How it is fast

Random bytes come from the ChaCha8 stream cipher keystream in userspace (Go's math/rand/v2 ChaCha8, partly in assembly) instead of a getrandom syscall per call, so large reads run at keystream speed. The sync.Pool gives each concurrently running goroutine its own derived generator, so there is no shared lock and throughput scales with cores. Since the 2024-10-07 commit 'switch to stdlib ChaCha8 generator', the generator itself is Go's stdlib code; frand's own contribution is the seeding, pooling and helper API (before that it was a hand-written ChaCha12 fast-key-erasure design).

## Compared with alternatives

Pick frand when a Go program needs a secure source that is fast and scales across goroutines; valyala/fastrand and pgregory.net/rand (sfc64) report lower per-call times in their own benchmarks but are not cryptographic, and vpxyz/xorshift is a set of plain non-crypto generators. For C/C++, randp (AES-CTR pool beating glibc arc4random) is the closest catalogued analogue.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go standard library only) |
| **Minimum toolchain** | Go 1.23.1 (go.mod; needs math/rand/v2 ChaCha8) |
| **Platforms** | any platform Go supports |
| **Thread safety** | Package-level functions, frand.Reader and Source (mutex-guarded) are safe for concurrent use; an \*RNG from New() or NewCustom() has no internal lock, so use one per goroutine. |
| **Drop-in for the baseline** | partial: frand.Reader can replace crypto/rand.Reader as an io.Reader, and NewSource() plugs into math/rand v1, but the helper functions have different signatures (no error return) and there is no math/rand/v2 Source adapter. |

## Gotchas

- Since 2024-10-07 the package is a thin wrapper over Go's math/rand/v2 ChaCha8; on Go 1.23+ you get most of the speed by using rand.NewChaCha8 with a crypto/rand seed yourself, and frand adds the pool and helpers.
- NewCustom(seed, bufsize, rounds) silently ignores bufsize and rounds and panics unless the seed is exactly 32 bytes; the old README described the default as ChaCha12, the current code is ChaCha8.
- Source.Uint64 calls Uint64n(math.MaxUint64), so it can never return 2^64-1; Source.Seed makes the stream deterministic, which removes the security property for that Source.
- The README's 20x and 100x figures were measured on the pre-2024 implementation against the crypto/rand of that time; Linux's vDSO getrandom (LWN reports about 15x faster small reads than the syscall) narrows the gap on new kernels, so re-measure on your Go version and kernel.

## Known shortcomings

- Tier C, Go only: frand_test.go does hold crypto/rand benchmarks, but the 21x and 103x figures (derived from page data) come from the old README table at 3f951cc for a previous implementation with no hardware stated.
- The 20x and 100x figures come from the pre-2024 ChaCha12 build; no results are published for the current ChaCha8 wrapper (frand_test.go has benchmarks), and the speed now comes mostly from Go stdlib ChaCha8. NewCustom ignores bufsize and rounds, and its seeded output changed at the 2024-10-07 switch; Source.Uint64 never returns 2^64-1. Go only, 22 commits, stale.

## Caveats and trade-offs

Go package, not callable from C++. The repo does carry benchmark code (frand_test.go: Read at 32 B and 512 KB, sequential, 4 and 64 goroutines, against crypto/rand and math/rand), but the current README gives only ratios with no hardware or Go version. The older README (commit 3f951cc, pre-2024 FKE-CSPRNG implementation) had a table: Read 512kb 5094 MB/s vs crypto/rand 239 MB/s (about 21x, derived from page data) and Read 512kb with 64 goroutines 19665 vs 191 MB/s (about 103x, derived from page data); math/rand was faster for Intn (20 vs 45 ns/op) and Perm(32) (789 vs 954 ns/op); no hardware stated. Since commit 'switch to stdlib ChaCha8 generator' (2024-10-07) frand is a thin wrapper over Go's math/rand/v2 ChaCha8 plus a sync.Pool, so the speedup now belongs mostly to Go's stdlib ChaCha8 over crypto/rand rather than to this package's own code. Not a like-for-like comparison with PCG or xoshiro.

Userspace CSPRNG seeded once from the kernel CSPRNG with no new entropy mixed in afterwards (README); the state lives in process memory, which the README acknowledges is easier for an attacker with memory access to read. Scales across cores through a sync.Pool of derived generators.

## Maintenance

Stale since the 2024-10-07 ChaCha8 switch (22 commits, 1 open issue, 93 stars), but MIT-licensed, a single 270-line file using only the stdlib, so it is easy to vendor; usable from Go only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README prose (20x faster than crypto/rand for large data, over 100x in parallel); benchmark code exists in frand_test.go (BenchmarkRead\*/BenchmarkReadCrypto\*/BenchmarkReadMath\* at 1, 4 and 64 goroutines) but no hardware, Go version or results for the current implementation are given.
- **Verifier notes:** MIT license, 93 stars, 13 forks, 22 commits, last commit 2024-10-07 confirmed on github.com; stale (about two years old) is correct. The record's caveat that there is no benchmark code was wrong and is corrected.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; independent context: Lemire's 2025/10/15 Go post (snippet) has math/rand/v2 ChaCha8 at 2.6 ns vs crypto/rand 51 ns per uint64 on an Apple M4, measuring the generator frand wraps rather than frand itself
- **Pages the verifier opened:**
  - <https://github.com/lukechampine/frand>
  - <https://github.com/lukechampine/frand/commits>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/frand_test.go>
  - <https://raw.githubusercontent.com/lukechampine/frand/3f951cc7c03d029aba12f89106666489fd8c769b/README.md>
- **Sources the enricher read:**
  - <https://github.com/lukechampine/frand>
  - <https://github.com/lukechampine/frand/commits>
  - <https://github.com/lukechampine/frand/issues?q=is%3Aissue>
  - <https://github.com/lukechampine/frand/issues/3>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/frand.go>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/frand_test.go>
  - <https://raw.githubusercontent.com/lukechampine/frand/HEAD/go.mod>
  - <https://raw.githubusercontent.com/lukechampine/frand/3f951cc7c03d029aba12f89106666489fd8c769b/README.md>
  - <https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2025/10/15>
  - <https://raw.githubusercontent.com/lemire/Code-used-on-Daniel-Lemire-s-blog/master/2025/10/15/README.md>
  - <https://raw.githubusercontent.com/lemire/Code-used-on-Daniel-Lemire-s-blog/master/2025/10/15/benchmark_test.go>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lukechampine/frand`) · [data/wave8/enrich/raw/github_com_lukechampine_frand.json](../../../data/wave8/enrich/raw/github_com_lukechampine_frand.json) (enrichment confidence 0.75)

</details>
