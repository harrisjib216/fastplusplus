# FLINT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0-or-later` · 🟢 active

> C number-theory library on top of GMP; FLINT 3 (with Arb) computes pi about 2x faster than GMP and does integer matmul far faster.

| | |
|---|---|
| **Beats** | GMP (Chudnovsky pi, mpz matrix multiplication) |
| **Claimed result** | pi (100M digits): GMP 62.1 s vs FLINT 31.6 s single-thread (\~2.0x, derived from page data), 9.34 s on 8 threads (\~6.6x, derived from page data); 100x100 matmul vs GMP naive (0.0122/0.0172/0.159 s at 10/100/1000 bits): FLINT optimized 0.0000678/0.00235/0.0456 s single-thread, 0.0000675/0.000800/0.0142 s 8-thread; FLINT naive 0.00395/0.0213/0.163 s |
| **Workload** | 100 million digits of pi; 100x100 integer matrix multiplication at 10/100/1000-bit entries |
| **Metric** | throughput |
| **Hardware** | 8-core AMD Ryzen 7 PRO 5850U (Zen 3) |
| **Adoption** | 629 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/flintlib/flint) · [benchmark](https://flintlib.org/applications.html) |

## Verdict

On an 8-core Ryzen 7 PRO 5850U (Zen 3), FLINT's arb_const_pi computed 100 million digits of pi in 31.6 s versus 62.1 s for GMP-chudnovsky (about 2x), and in 9.34 s on 8 threads (about 6.6x). A 100x100 fmpz_mat_mul took 0.0000678/0.00235/0.0456 s at 10/100/1000-bit entries versus 0.0122/0.0172/0.159 s for naive GMP mpz loops. The numbers are first-party and no compiler or flags are given.

## Use it when

- Integer matrices and polynomials with small to medium entries, where fmpz_mat_mul is roughly 180x (10-bit) to 3.5x (1000-bit) faster than naive GMP loops
- Huge single multiplications or constants (pi, e, special functions) at millions of digits, especially with flint_set_num_threads
- Computer algebra and number theory: factorization, finite fields, number fields, rigorous ball arithmetic (Arb)
- x86-64 with AVX2 or ARM64 with NEON, where fft_small is enabled

## Skip it when

- Element-by-element mpz-style code: FLINT's own naive fmpz matmul is no faster than GMP at 100/1000 bits (0.0213 vs 0.0172 s, 0.163 vs 0.159 s)
- When you need a drop-in mpz_t/mpz_class replacement; the API is fmpz_t and you must rewrite calls
- Projects that cannot accept LGPL-3.0-or-later (dynamic linking or relinkable objects required)
- Platforms without AVX2/NEON, where fft_small is unavailable and large multiplies fall back to slower paths
- Header-only or no-dependency setups: it needs GMP 6.2.1+ and MPFR 4.1.0+ plus an autotools build

## How it is fast

Large integer and polynomial multiplication goes through fft_small, a truncated number-theoretic transform over several word-size primes in double precision with Chinese remaindering (van der Hoeven's approach), vectorised for AVX2 or NEON and multithreaded. Matrix multiplication (fmpz_mat_mul) uses multimodular reduction with BLAS-backed modular products instead of naive mpz loops. arb_const_pi uses binary splitting with FLINT's multiplication. The inline small-integer fmpz form avoids heap allocation for word-size entries.

## Compared with alternatives

Pick FLINT over mp++ or ctbignum when operands are large or the work is matrix, polynomial or constant computation; those two win on fixed small limb counts and per-operation overhead. Pick it over DoT or the AVX-512 Montgomery code when you need a maintained, licensed library instead of research kernels.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | GMP &gt;= 6.2.1, MPFR &gt;= 4.1.0; optional BLAS for matrix multiplication |
| **Minimum toolchain** | C compiler (GCC/Clang); autotools on Unix, CMake on Windows |
| **Platforms** | Linux/Unix, macOS, Windows (CMake, MinGW64); fft_small needs x86-64 AVX2 (--enable-avx2) or aarch64 NEON |
| **Thread safety** | Thread-safe by default (thread-local caches via --enable-tls); internal parallelism is opt-in with flint_set_num_threads (default 1); call flint_cleanup_master before exit to free all caches |
| **Drop-in for the baseline** | partial — it uses GMP underneath and converts to and from mpz_t, but the speedups come only through FLINT's fmpz/arb/mat APIs |

## Gotchas

- Build with optimisation: issue #2852 reported fft_small 10x slower than GMP on Zen 5, but the cause was CFLAGS=-g0 overriding configure's -O flags; with -O3 it was about 3x faster than GMP
- AVX2 is not on by default; pass --enable-avx2 on x86-64 to get fft_small
- fmpz_t is an array-of-one type; index arrays with pointer arithmetic, and pair fmpz_init with fmpz_clear (memory from flint_malloc must be freed with flint_free)
- Multithreading is off until you call flint_set_num_threads(n); the 8-thread pi and matmul figures need it

## Known shortcomings

- First-party numbers only, compiler and flags not given; naive matmul slower than GMP at 100 and 1000 bits. License LGPL-3.0-or-later confirmed from README.
- API is fmpz_t, not a drop-in for mpz_t; AVX2 must be enabled at build time (--enable-avx2). Note: issue #2852 slowdown was a -g0 unoptimised build, not a real regression (at -O3 fft_small \~3x faster than GMP on Zen 5).

## Caveats and trade-offs

First-party; compiler/flags not given; FLINT naive matmul is not faster than GMP at 100/1000 bits; github issue 2852 reports fft_small slower than GMP on a Zen 5 EPYC (not opened).

Uses GMP/MPIR underneath; FLINT 3 absorbs Arb, Calcium; fft_small is AVX2/NEON tuned.

## Maintenance

Actively developed (3.7.0-dev, commits in late September 2026) under LGPL-3.0-or-later by Fredrik Johansson and Albin Ahlbäck; mature and production-grade.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party flintlib.org applications page gives GMP vs FLINT timings (pi 62.1 s vs 31.6 s / 9.34 s 8-thread; 100x100 matmul table) on a Ryzen 7 PRO 5850U, but there is no compiler/flags and no linked benchmark code.
- **Verifier notes:** Numbers match. The license is LGPL v3+ (the repo ships COPYING for the GPL text that the LGPL references); revert if the orchestrator has evidence of a GPL-or option. Shortcomings: first-party, no flags; naive matmul slower than GMP at 100/1000 bits; issue 2852 not opened.
- **Fields the verifier corrected:** `claimed_speedup`, `license`
- **Shortcomings recorded by:** Arb (merged into FLINT) ARITH 2019 peer-reviewed paper: dot product/matmul vs MPFR fma, Table I
- **Pages the verifier opened:**
  - <https://flintlib.org/applications.html>
  - <https://github.com/flintlib/flint>
  - <https://github.com/flintlib/flint/commits>
- **Sources the enricher read:**
  - <https://flintlib.org/applications.html>
  - <https://raw.githubusercontent.com/flintlib/flint/HEAD/README.md>
  - <https://github.com/flintlib/flint/issues/2852>
  - <https://flintlib.org/doc/building.html>
  - <https://flintlib.org/doc/threading.html>
  - <https://flintlib.org/doc/memory.html>
  - <https://flintlib.org/doc/fmpz.html>
  - <https://flintlib.org/doc/fft_small.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flintlib/flint`) · [data/wave8/enrich/raw/github_com_flintlib_flint.json](../../../data/wave8/enrich/raw/github_com_flintlib_flint.json) (enrichment confidence 0.8)

</details>
