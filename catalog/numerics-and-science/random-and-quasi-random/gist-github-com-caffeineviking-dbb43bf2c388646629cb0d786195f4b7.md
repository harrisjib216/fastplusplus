# xoshiro8x256pp (8-way SIMD xoshiro256++ gist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🔴 abandoned

> A 15-line C function running eight xoshiro256++ streams in lockstep for compiler auto-vectorization; \~1.9x scalar xoshiro256++, \~3x PCG64.

| | |
|---|---|
| **Beats** | xoshiro256++ (also PCG64) |
| **Claimed result** | xoshiro8x256pp 4,922.28 MB/s vs xoshiro256pp 2,619.20 MB/s and PCG64 1,576.86 MB/s (about 1.9x and 3.1x, derived from page data) |
| **Workload** | prng64-shootout throughput, MB/s |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-8250U |
| **Compiler and flags** | not stated in gist; prng64-shootout Makefile default is cc -std=c99 -O3 -g3 -march=native (unconfirmed for this run) |
| **Adoption** | gist |
| **Last commit** | 2020-12-22 |
| **Links** | [repository](https://gist.github.com/CaffeineViking/dbb43bf2c388646629cb0d786195f4b7) · [benchmark](https://gist.github.com/CaffeineViking/dbb43bf2c388646629cb0d786195f4b7) |

## Verdict

The gist author added the function to skeeto/prng64-shootout and ran it on an Intel Core i5-8250U (compiler and flags not stated; the shootout Makefile defaults to -O3 -march=native). It reached 4,922 MB/s vs 2,619 MB/s for scalar xoshiro256++ and 1,577 MB/s for PCG64, about 1.9x and 3.1x (derived from page data).

## Use it when

- Bulk filling of uint64 buffers (Monte Carlo, noise, test data) on x86-64 with AVX2 or AVX-512, or aarch64 NEON, where the compiler can vectorize simple loops
- When you want xoshiro256++ quality at roughly twice the scalar rate and can consume randoms in blocks of 8
- As a small, readable template to copy into your own code base, after you clear its licensing (see when_not_to_use)

## Skip it when

- Without a license you cannot legally copy it as-is. Vigna's public-domain xoshiro256++-vect-speed.c gives the same technique with clear terms.
- One-at-a-time draws: you must buffer 8 outputs, and the gain disappears if each call yields only one value
- Builds without -O3 or -march flags that enable vectorization (e.g. -O2 on older GCC, or MSVC): the loops may stay scalar and gain nothing
- When you need jump/long-jump to separate the 8 lanes: the gist leaves seeding to the user, and poorly seeded lanes may be correlated
- Peak bulk throughput: SHISHUA reports far higher GB/s with explicit SIMD

## How it is fast

It is Vigna's xoshiro256++-vect-speed.c idea fixed at an unroll of 8. Every step of xoshiro256++ (add, rotl 23, shift 17, four XORs, rotl 45) is a separate loop over 8 lanes, so GCC/Clang at -O3 with AVX2 turn each loop into 256-bit vector ops (two registers per word). There are no intrinsics, so the speedup depends entirely on the compiler vectorizing the loops. Eight independent dependency chains also hide latency.

## Compared with alternatives

Pick it over Xoshiro256PlusSIMD when you want xoshiro256++ (better low bits than xoshiro256+), 8 lanes and portable C with no intrinsics. Pick SHISHUA for maximum bulk throughput, and Sirius64 or wyrand for scalar one-at-a-time draws.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdint.h) |
| **Minimum toolchain** | C99; needs an auto-vectorizing compiler (GCC/Clang -O3, e.g. -march=native) to get the speedup |
| **Platforms** | any in principle (portable C); measured only on x86-64 (Intel Core i5-8250U, AVX2) |
| **Thread safety** | Reentrant: state is caller-owned; use one s[4][8] per thread |
| **Drop-in for the baseline** | partial: produces the same per-lane sequence as scalar xoshiro256++ for each lane's state, but returns 8 values per call through a different signature |

## Gotchas

- No license is stated on the gist, so the default copyright applies.
- The 8 lanes need 8 distinct, well-mixed seeds (e.g. from SplitMix64, or xoshiro jump() between lanes); seeding is not provided.
- The benchmark used skeeto/prng64-shootout, which stores each value into a volatile 512 MB buffer one at a time. That likely caps the measured gain below the generator's raw rate; the shootout's own non-PRNG baseline_simd was 12,078 MB/s on the same page.
- Before relying on the speedup, check that the compiler vectorized the loops (e.g. -fopt-info-vec).

## Known shortcomings

- Gist has no license (reference only); compiler/flags not named (run inside skeeto/prng64-shootout, whose Makefile defaults to cc -std=c99 -O3 -march=native, unconfirmed); one laptop CPU (i5-8250U); reproducing needs adding it to prng64-shootout; abandoned (2020-12-22).
- No seeding or jump code; no intrinsics, speedup depends on compiler auto-vectorization; shootout harness stores into a volatile buffer.

## Caveats and trade-offs

No license stated; compiler/flags not stated in gist (shootout Makefile default -O3 -march=native); single laptop CPU; requires adding the generator to skeeto/prng64-shootout to reproduce. Same page lists the shootout's baseline_simd at 12078 MB/s (an upper-bound reference, not a PRNG). Gist, not a repo.

Gist based on Vigna's xoshiro256++-vect-speed.c; eight interleaved streams; needs AVX2.

## Maintenance

A one-off gist last active 2020-12-22 with no license, so it is reference only. Vigna's CC0 vect-speed.c gives the same technique under copyable terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Gist author's own run on an i5-8250U via skeeto/prng64-shootout: xoshiro8x256pp 4922.28 MB/s vs xoshiro256pp 2619.20 and pcg64 1576.86 MB/s. Harness is public and its Makefile defaults to cc -std=c99 -O3 -march=native, but the gist does not state the compiler or the flags it used, so this is not A.
- **Verifier notes:** Numbers match the page exactly; the author says "\~3x faster than PCG64". The vectorized design follows Vigna's xoshiro256++-vect-speed.c. No license, so it stays reference.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://gist.github.com/CaffeineViking/dbb43bf2c388646629cb0d786195f4b7>
  - <https://gist.githubusercontent.com/CaffeineViking/dbb43bf2c388646629cb0d786195f4b7/raw>
  - <https://raw.githubusercontent.com/skeeto/prng64-shootout/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://gist.github.com/CaffeineViking/dbb43bf2c388646629cb0d786195f4b7>
  - <https://prng.di.unimi.it/xoshiro256++-vect-speed.c>
  - <https://github.com/skeeto/prng64-shootout>
  - <https://raw.githubusercontent.com/skeeto/prng64-shootout/HEAD/README.md>
  - <https://raw.githubusercontent.com/skeeto/prng64-shootout/HEAD/shootout.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://gist.github.com/caffeineviking/dbb43bf2c388646629cb0d786195f4b7`) · [data/wave8/enrich/raw/gist_github_com_caffeineviking_dbb43bf2c388646629cb0d786195f4b7.json](../../../data/wave8/enrich/raw/gist_github_com_caffeineviking_dbb43bf2c388646629cb0d786195f4b7.json) (enrichment confidence 0.75)

</details>
