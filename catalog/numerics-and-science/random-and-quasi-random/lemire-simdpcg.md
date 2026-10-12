# simdpcg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Vectorized PCG32 (pcg32 XSH-RR) in AVX2 and AVX-512 C intrinsics; 1.8x to 3.7x faster than scalar PCG32 at filling arrays.

| | |
|---|---|
| **Beats** | PCG32 (scalar reference by O'Neill) |
| **Claimed result** | scalar pcg32 4.25 cycles/op vs AVX-512 variants 2.37, 1.21 and 1.14 cycles/op |
| **Workload** | Filling an array of 50,000 32-bit random numbers (195 kB), cycles per element |
| **Metric** | throughput |
| **Compiler and flags** | compiler unstated; Makefile uses -std=c99 -O3 -march=native |
| **Adoption** | 88 stars |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/lemire/simdpcg) · [benchmark](https://github.com/lemire/simdpcg) |

## Verdict

The README sample, from benchmark/fillarray.c (RDTSC, best of 500 runs, 50,000 32-bit values in a 195 kB array, -O3 -march=native with an unstated compiler and CPU), shows scalar O'Neill pcg32_random_r at 4.25 cycles/value. The AVX-512 one-, two- and four-key variants run at 2.37, 1.21 and 1.14 cycles/value, which is 1.8x to 3.7x (derived from page data). The multi-key variants interleave independent streams, and nothing was compared with std::mt19937.

## Use it when

- You already depend on PCG32 output (seeds, reproducibility) and want the same stream generated 8 values at a time, e.g. filling arrays of 32-bit randoms
- AVX-512 servers (Skylake-X or newer with AVX512DQ), where the four-key variant reaches 1.14 cycles per value against 4.25 for scalar
- Throughput-bound Monte Carlo or simulation code that can consume values in 8- or 16-wide vectors
- C or C++ projects that want an Apache-2.0 header with no dependencies

## Skip it when

- Portable or ARM code: there are only x86 AVX2 and AVX-512 paths and no scalar fallback in simdpcg32.h, and the types disappear when __AVX2__ / __AVX512DQ__ are not defined
- Code that needs a std::uniform_random_bit_generator engine or one value per call: you must buffer the vector output yourself
- Peak bulk throughput regardless of algorithm: SHISHUA reports about 0.05 cycles per byte, against roughly 0.29 cycles per byte here (1.14 cycles per 4-byte value)
- Any cryptographic use (PCG32 is not a CSPRNG)
- Older AVX-512 chips where heavy 512-bit use can lower clocks: not measured in the repo, so benchmark on your own hardware

## How it is fast

It runs the scalar PCG32 step (an LCG multiply-add, then an xorshift and a data-dependent rotate) across 64-bit SIMD lanes. On AVX-512 it uses _mm512_mullo_epi64 (AVX512DQ) and _mm512_rorv_epi32. The AVX2 path builds the 64-bit multiply from 32-bit partial products (_mm256_mul_epu32) and emulates the rotate with variable shifts (code credited to Wenzel Jakob's pcg32_8.h). Leapfrog seeding (multiplier^k per lane) keeps the scalar sequence. The benchmark's 'two' and 'four' variants interleave 2 or 4 independent generator keys to hide multiply latency.

## Compared with alternatives

Pick simdpcg over SHISHUA, SIMDxorshift or xoshiro8x256pp when you need the exact PCG32 stream (reproducibility with existing scalar PCG32 code) rather than the fastest new generator. Pick testingRNG's lehmer64/aesctr or SHISHUA when raw throughput matters more than matching PCG32.

## Integration

| | |
|---|---|
| **Form** | header-only (include/simdpcg32.h; include/pcg32.h holds the scalar reference) |
| **Dependencies** | none |
| **Minimum toolchain** | C99 (Makefile uses -std=c99 -march=native); the compiler must support AVX2 or AVX512F+AVX512DQ intrinsics |
| **Platforms** | x86-64 with AVX2 (avx2_/avx256_ paths) or AVX-512F+DQ (avx512_/avx512bis_ paths); no ARM or scalar fallback |
| **Thread safety** | not documented; state is a plain struct with no globals, so use one key per thread |
| **Drop-in for the baseline** | partial: avx2/avx256/avx512 \*_initialize reproduce the scalar PCG32 stream bit-for-bit (unit test check_identity), but the API returns SIMD vectors, not one uint32_t per call |

## Gotchas

- Each feature path is compiled only when its macro (AVX2PCG / AVX512PCG) is set by __AVX2__ or __AVX512F__ && __AVX512DQ__. Without -mavx2/-mavx512dq or -march=native the types are silently missing.
- If you fill the struct by hand (as the benchmark and older README code do) instead of calling \*_initialize, every inc lane must be odd. That was a 2025 bug fix (PR #3). Hand-filled lanes also give independent streams, not the scalar sequence.
- Two helpers in the AVX2 path (hacked_mm256_rorv_epi32, hacked_mm256_mullo_epi64) are marked '// untested' in the source, although the 2026 check_identity unit test now exercises the avx256 path.
- The README 'Sample result' shows only the scalar and three AVX-512 variants. The current benchmark/fillarray.c also times AVX2, avx256 and avx512bis variants that have no published numbers.

## Known shortcomings

- Flags from Makefile (-O3 -march=native) but no compiler or CPU model; needs AVX-512; baselines are scalar PCG32 only.
- Correction: AVX-512 not required (AVX2 paths exist) and 2026 \*_initialize helpers reproduce the scalar PCG32 stream; published numbers predate AVX2/avx512bis variants; 1.14 cycles/value interleaves 4 generators; two AVX2 helpers marked 'untested'.

## Caveats and trade-offs

README gives no CPU model, compiler or flags. Compared only against scalar PCG32, not std::mt19937.

Requires AVX-512 (AVX512DQ, Skylake-X or newer); changes stream layout versus scalar PCG32.

## Maintenance

Small but active (merges in January 2026 for an AVX-512 packing speedup and August 2026 for scalar-identical initialize helpers), Apache-2.0, and easy to vendor as one header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Sample result' shows scalar populateRandom_pcg32 at 4.25 cycles/op against AVX-512 variants at 2.37, 1.21 and 1.14 cycles/op. The benchmark code (benchmark/fillarray.c) and flags (Makefile: -O3 -march=native) are public, but no CPU model or compiler is stated, so it is not A.
- **Verifier notes:** Requires AVX-512 (AVX512DQ, Skylake-X or later). The numbers match the README exactly; the speedup is 3.7x for the four-stream variant (derived from page data).
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/lemire/simdpcg>
  - <https://raw.githubusercontent.com/lemire/simdpcg/master/README.md>
  - <https://raw.githubusercontent.com/lemire/simdpcg/master/Makefile>
  - <https://raw.githubusercontent.com/lemire/simdpcg/master/LICENSE>
  - <https://github.com/lemire/simdpcg/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/include/simdpcg32.h>
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/include/pcg32.h>
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/tests/unit.c>
  - <https://raw.githubusercontent.com/lemire/simdpcg/HEAD/benchmark/fillarray.c>
  - <https://github.com/lemire/simdpcg/commits>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lemire/simdpcg`) · [data/wave8/enrich/raw/github_com_lemire_simdpcg.json](../../../data/wave8/enrich/raw/github_com_lemire_simdpcg.json) (enrichment confidence 0.85)

</details>
