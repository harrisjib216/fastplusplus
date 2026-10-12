# randp (AES-CTR Random Pool)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MPL-2.0` · 🟢 active

> Linux C library with arc4random-style API backed by a thread-local 3-round-AES pool; 2-21x faster than glibc arc4random.

| | |
|---|---|
| **Beats** | glibc arc4random / arc4random_buf / arc4random_uniform (glibc 2.36+ getrandom-based); also getentropy, RDRAND, RDSEED |
| **Claimed result** | 2026-09-22 run: randp_bytes 247 ms vs arc4random_buf 5211 ms for 4 GiB (page says 21.1x faster); randp_u32 7.00 ns vs arc4random 14.0 ns (2.0x); randp_lt_u32 7.19 ns vs arc4random_uniform 23.6 ns (3.3x); rdrand32 291 ns and rdseed32 1825 ns are much slower than randp_u32. |
| **Workload** | Median Google Benchmark time to fill a 4 GiB buffer with random bytes, and median time per call for one uniform uint32_t and one uniform uint32_t below a bound in [1..0x100000]. |
| **Metric** | throughput |
| **Hardware** | 13th Gen Intel(R) Core(TM) i9-13980HX, Linux 7.2.6-arch2-1 x86_64 |
| **Compiler and flags** | gcc (GCC) 16.2.1 20260810, glibc 2.44, libbenchmark 1.9.5. Results page does not print flags; repo build files set -O3 -flto=auto -march=x86-64-v2 -maes (config.mk) and benchmarks/Makefile adds -march=x86-64-v3 -maes -mvaes -mrdrnd -mrdseed. |
| **Adoption** | 1 star, 499 commits |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/planet36/randp) · [benchmark](https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/README.md) |

## Verdict

In the author's Google Benchmark run of 2026-09-22 (i9-13980HX, Linux 7.2.6, glibc 2.44 with the getrandom vDSO, gcc 16.2.1, one thread, median of 5), filling 4 GiB in 256-byte calls took 247 ms with randp_bytes against 5211 ms with arc4random_buf (21.1x). One uint32 took 7.00 ns against 14.0 ns for arc4random, and a bounded uint32 (bounds cycling over 1..0x100000) took 7.19 ns against 23.6 ns for arc4random_uniform. Runs on glibc 2.40, before the vDSO, showed 27-43x; randp_bytes itself slowed from 199 ms (librandp 4.5, February 2026) to 247 ms (7.0), and the cause is not documented.

## Use it when

- Linux x86-64 code that calls arc4random or arc4random_uniform in hot loops (shuffles, sampling, randomized algorithms, jitter, non-secret IDs): 7.0 ns versus 14.0 ns per uint32 and 7.19 ns versus 23.6 ns per bounded draw on the author's machine.
- Bulk filling of buffers with unpredictable-looking bytes where secrecy does not matter (test data, fuzz inputs, randomized padding): about 16 GiB/s on one thread versus about 0.8 GiB/s for arc4random_buf in 256-byte calls (both derived from page data).
- Multi-threaded or forking servers that want per-thread, lock-free randomness with no seeding code: the pool is thread_local and MADV_WIPEONFORK makes a forked child reseed before its first output.
- You want periodic automatic reseeding from the OS, which plain xoshiro/PCG-style generators do not do.

## Skip it when

- Keys, nonces, session tokens, salts, or anything an attacker gains from predicting: three AES rounds are not a cipher, there is no security proof, and the README makes no CSPRNG claim. Use getrandom/arc4random, or Randen if you need speed with a stated security argument.
- Reproducible simulations: there is no seed or stream API; it is always seeded from getentropy and reseeds every 256 KiB per thread.
- Anything other than Linux x86-64 with GCC 14+ and glibc 2.34+: non-x86-64 hits #error "Architecture not supported", clang is explicitly unsupported, and MADV_WIPEONFORK needs Linux 4.14+.
- Maximum raw throughput for statistics or Monte Carlo: the pool copy and wiping cost time, and the same author's raw aes_ctr_128 generator (prng-test-bench) is listed at 37.22 GiB/s per thread versus about 16 GiB/s for randp_bytes (different benchmarks).
- Long-lived production dependencies: 1 star, single author, the soname went from 4.5 (February 2026) to 7.0 (September 2026), and parameters and build options change frequently.

## How it is fast

The generator transforms a counter with three AESENC instructions under three independent random 128-bit round keys: no key schedule, no initial key whitening, no AESENCLAST, so far less work than the kernel getrandom path that glibc's arc4random wraps. The counter advances as two 64-bit Weyl sequences with odd per-lane increments. Output is produced 256 bytes at a time into a lock-free thread_local pool, so randp_u32 is a memcpy plus explicit_bzero with no syscall or vDSO call; bounded integers use Lemire's nearly divisionless multiply-and-reject method. A VAES/AVX2 path that generates two blocks per instruction exists, but the default config.mk build (-march=x86-64-v2 -maes) compiles the 128-bit AES-NI path.

## Compared with alternatives

Pick randp over Randen when you want arc4random's seedless, per-thread, fork-safe API on Linux and can accept a reduced-round generator with no proof; pick Randen when you need its stated indistinguishability and backtracking resistance. For seeded simulation streams or raw speed, the same author's prng-test-bench aes_ctr_128 or testingRNG's aesctr skip randp's pool copy and wiping.

## Integration

| | |
|---|---|
| **Form** | static lib, shared lib, or header-only (make randp-single.h amalgamation) |
| **Dependencies** | none beyond glibc 2.34+ (getentropy, explicit_bzero, C11 threads in libc) and Linux 4.14+ (mmap, MADV_DONTDUMP, MADV_WIPEONFORK); python3 to generate the single header; Google Benchmark for the benchmarks |
| **Minimum toolchain** | GCC 14+ in C23 mode (clang and clang++ not supported); the C++ benchmarks use g++ -std=c++23 |
| **Platforms** | Linux x86-64 only, AES-NI plus SSE4.1 required (optional VAES + AVX2 path) |
| **Thread safety** | Thread-safe without locks: each thread gets its own lazily mmapped pool (thread_local), released by a tss destructor at thread exit. Fork-safe via MADV_WIPEONFORK (tests/README.md: 'fork-safe, just like arc4random'). Async-signal safety not documented. |
| **Drop-in for the baseline** | partial: same semantics as arc4random, arc4random_buf and arc4random_uniform (no seeding, unbiased bounded integers, 0 for bound &lt;= 1), but different function names, Linux x86-64 GCC only, and not cryptographically equivalent |

## Gotchas

- Despite the name, the defaults (3 keys x 1 round in src/aes_ctr_128_prng-defaults.h and aes_ctr_256_prng-defaults.h) give 3 AESENC rounds on a Weyl-sequence counter, not AES-128 in CTR mode. The parameters are compile-time constexpr values; the build-time override was removed on 2026-09-24, so changing them means editing the headers.
- Failures are fatal: an error from mmap, madvise (for example a kernel without MADV_WIPEONFORK), getentropy or tss_create calls err/errx and exits the process.
- The keys and counter sit in the per-thread page between reseeds, so a memory disclosure exposes outputs both before and after it up to the next reseed (256 KiB); wiping handed-out pool bytes does not prevent that. Each thread that calls randp also holds a 4 KiB mapping until it exits.
- There is no LICENSE file at the root (raw LICENSE returns 404); MPL-2.0 comes only from SPDX headers in each source file. The published numbers cover the 128-bit AES-NI path: benchmarks/Makefile adds -march=x86-64-v3 -mvaes only to the C++ benchmark file, while librandp.a is built with config.mk's -march=x86-64-v2 -maes.

## Known shortcomings

- Security: the 'AES-CTR' generator runs only 3 AES rounds (3 keys x 1 aesenc), not AES-128, yet the README calls the output practically unpredictable; the comparison against ChaCha20-backed glibc arc4random is not like for like. No LICENSE file (MPL-2.0 SPDX headers only).
- Published numbers cover the 128-bit AES-NI path only: librandp.a is built with config.mk -march=x86-64-v2 -maes, and -mvaes applies only to the benchmark C++ file, so the record's flags line is misleading. The 4 GiB test calls each function in 256-byte chunks. randp_bytes regressed from 199 ms (4.5) to 247 ms (7.0) with no documented cause. Keys and counter stay in memory, so a disclosure exposes outputs before and after up to the next reseed (256 KiB); fatal exit on mmap/madvise/getentropy failure; x86-64 Linux with GCC 14+ only; soname went 4.5 to 7.0 in 2026; the GitHub topic says CSPRNG while the README disclaims it.

## Caveats and trade-offs

Despite the name, randp's PRNG is not AES-128-CTR: src/aes_ctr_128_prng-defaults.h sets 3 keys x 1 round, and aes_enc_128 in src/aes-128-utils.h applies one _mm_aesenc_si128 per key, so each 16-byte block gets 3 AES rounds with independent random round keys (no key schedule, 3 rounds instead of 10). The README's FAQ disclaims CSPRNG status but still calls the output 'practically unpredictable', which 3-round AES does not support; glibc arc4random is backed by the kernel's ChaCha20 getrandom, so the 21x/2x/3.3x gaps compare a reduced-round generator against a cryptographic one, not like for like. Baseline is glibc arc4random (a getrandom() wrapper, sped up by the getrandom vDSO since glibc 2.41), not std::mt19937, PCG or xoshiro. First-party benchmark on one laptop CPU; flags come from the HEAD Makefiles, not printed with the results. Older runs on the same page (2024-10-04, glibc 2.40 before the vDSO) showed 27x-43x; the current figures are the 2026-09-22 ones. No LICENSE file at the root (raw LICENSE returns 404); MPL-2.0 comes from SPDX headers in every source file, so confirm before copying. Very young project, 1 star, changing daily.

Linux-only (MADV_WIPEONFORK, getentropy), needs a CPU with AES instructions (VAES variant for 256-bit), GCC 14+ for C23 thread_local (clang explicitly unsupported), glibc 2.34+. Thread-local pool of at most one page, reseeded from getentropy every 1024 refills by default. Author states it makes no CSPRNG claim. C API with a generated single header (make randp-single.h), usable from C++.

## Maintenance

Very active (last commit 2026-10-02, commits almost daily) but a 1-star single-author project. MPL-2.0 by SPDX headers only, and small enough to vendor through randp-single.h if you accept its Linux/x86-64/GCC-only scope.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/README.md (2026-09-22 run) prints the exact numbers against glibc 2.44 arc4random/arc4random_buf/arc4random_uniform with gcc 16.2.1 and CPU i9-13980HX; the benchmark code is public (benchmarks/benchmark-others.cpp, run by `make others` single-threaded, 5 reps, random interleaving) and its flags are fixed in the public benchmarks/Makefile plus config.mk (-O3 -flto=auto, -march=x86-64-v3 -maes -mvaes -mrdrnd -mrdseed for the benchmark, -march=x86-64-v2 -maes for librandp.a).
- **Verifier notes:** All three claimed ratios (21.1x, 2.0x, 3.3x) and the rdrand/rdseed timings appear verbatim on the 2026-09-22 section. Record as a shortcoming that the 'AES-CTR' generator is 3 AES rounds only, so the speed win over arc4random comes partly from doing a fraction of a cipher's work and should not be read as a faster drop-in for a cryptographic arc4random.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/README.md>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/config.mk>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/benchmark-others.cpp>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes_ctr_128_prng-defaults.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/randp-defaults.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes_ctr_128_prng.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes-128-utils.h>
  - <https://github.com/planet36/randp>
  - <https://github.com/planet36/randp/commits>
- **Sources the enricher read:**
  - <https://github.com/planet36/randp>
  - <https://github.com/planet36/randp/commits>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/README.md>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/benchmarks/benchmark-others.cpp>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/tests/README.md>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/config.mk>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/randp.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/randp.c>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/randp-defaults.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes_ctr_128_prng.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes_ctr_128_prng-defaults.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes_ctr_256_prng-defaults.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/aes-128-utils.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/nearlydivisionless.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/src/allocate.h>
  - <https://raw.githubusercontent.com/planet36/randp/HEAD/LICENSE>
  - <https://github.com/google/randen>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/planet36/randp`) · [data/wave8/enrich/raw/github_com_planet36_randp.json](../../../data/wave8/enrich/raw/github_com_planet36_randp.json) (enrichment confidence 0.75)

</details>
