# Large integer multiplication with Intel AVX-512 on Knights Landing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Study only · `unknown` · `no license` · ⚪ unknown

> Peer-reviewed AVX-512F reduced-radix large-integer multiplication for Xeon Phi Knights Landing, reported about 2.5x faster than GMP; no code.

| | |
|---|---|
| **Beats** | GMP |
| **Claimed result** | About 2.5x faster execution time than GMP for large-integer multiplication on Knights Landing using AVX-512F (abstract as quoted in WebSearch summaries; paper not opened). |
| **Workload** | Large-integer multiplication with AVX-512F instructions in a reduced-radix representation on the Knights Landing Xeon Phi, comparing execution time and instruction counts with GMP. |
| **Metric** | throughput |
| **Hardware** | Intel Knights Landing (exact model not seen) |
| **Links** | [benchmark](https://ieeexplore.ieee.org/document/8622797/) |

## Verdict

Two search-engine summaries of the abstract (paper not opened) say the AVX-512F implementation is about 2.5x faster in execution time than GMP for large-integer multiplication on Knights Landing, also comparing instruction counts. GMP version, operand sizes, compiler, flags and the exact Xeon Phi model are not documented.

## Use it when

- Designing a multi-precision multiply for cores that have AVX-512F but not AVX-512IFMA, such as Knights Landing, where GMP's scalar path is slow.
- Throughput-oriented number crunching on many-core Xeon Phi nodes that still run, as a reference for vectorizing the column sums of a multi-limb product.
- As the baseline when evaluating the same authors' later AVX-512IFMA paper, which reports up to about 3.07x over this AVX-512F approach.

## Skip it when

- You need code you can run: nothing is published and attributed, so has_code is false.
- CPUs with AVX-512IFMA: the authors' own IFMA version (sibling entry) reports up to about 3.07x over their AVX-512F one.
- Mainstream x86 cores with fast scalar 64-bit multiply and carry chains: the 2.5x is specific to Knights Landing, and the gain elsewhere is not documented.
- Very large operands where GMP uses Toom-Cook or FFT multiplication: the operand-size range of the result is not documented.
- New deployments: Knights Landing (Xeon Phi) is discontinued.

## How it is fast

AVX-512F has no 64x64-bit vector multiply; VPMULUDQ (_mm512_mul_epu32) gives eight 32x32-to-64-bit products per instruction. With a reduced-radix representation (limbs narrower than 32 bits) each 64-bit accumulator keeps headroom, so the column sums of the product can be built from many vector multiply-adds before carries are propagated in a final normalization pass. On Knights Landing, whose scalar cores are weak, this vector path beats GMP's scalar mpn code; the exact limb width and multiplication algorithm used in the paper are not documented in anything readable this session.

## Compared with alternatives

Read it only as a design reference for AVX-512F-only hardware; on IFMA-capable CPUs prefer the same authors' AVX-512IFMA design, and for runnable code CGBN (GPU, 43.5x average on low multiplication vs 20-core GMP), lea-gl's batched AVX-512 Montgomery code or FLINT (large sizes) are the practical picks.

## Integration

| | |
|---|---|
| **Form** | not released (paper only) |
| **Dependencies** | not documented |
| **Minimum toolchain** | not documented (needs AVX-512F intrinsics or assembler support) |
| **Platforms** | x86-64 with AVX-512F; measured on Intel Knights Landing (exact Xeon Phi model not documented) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Evidence is snippet only: ieeexplore document 8622797 and semanticscholar are egress-blocked, so GMP version, operand sizes, compiler, flags and the exact CPU are unknown.
- Reduced-radix limbs need split and recombine passes to and from 32- or 64-bit limbs; whether the reported time includes that conversion is not documented.
- Hibari-K/bigint_mul_avx512f matches the topic and period (28-bit split/combine, _mm512_mul_epu32, 'naive algorithm', Makefile for Intel icc -xMIC-AVX512 on Knights Landing) but names no authors or paper, has no timing harness, no GMP comparison and no license; do not treat it as this paper's artifact.
- Knights Landing results lean on its weak scalar cores, so a 2.5x win over GMP there says little about Skylake-SP or later server parts.

## Known shortcomings

- No linked public code (github.com/Hibari-K/bigint_mul_avx512f looks related but is unattributed, unlicensed and has no GMP comparison); snippet-only evidence (IEEE HPCC 2018 unreachable here); best-case \~2.5x over GMP on discontinued Xeon Phi Knights Landing; GMP version, flags and sizes unknown.

## Caveats and trade-offs

Snippet only: the paper (2018 IEEE 20th International Conference on High Performance Computing and Communications, HPCC; ieeexplore document 8622797) could not be opened because ieeexplore and semanticscholar are egress-blocked. The 2.5x figure and its attribution to this paper are now confirmed by two separate search summaries of the abstract. Operand sizes, GMP version, compiler, flags and exact Xeon Phi model are unknown; GMP has no AVX-512 kernels, and Knights Landing's scalar cores are weak, so the win over GMP is specific to that platform. Knights Landing (Xeon Phi) is discontinued. Peer-reviewed venue, so a verifier with paper access may re-tier to B. The GitHub repo Hibari-K/bigint_mul_avx512f (C intrinsics, Makefile targets Knights Landing with -xMIC-AVX512, 28-bit limb splitting, commits 2017-2019, no license, 1 star) matches the topic and period, but nothing in it names the authors or the paper and it has no GMP comparison, so it is not attributed and has_code stays false.

Needs AVX-512F hardware; Knights Landing is discontinued.

## Maintenance

A 2018 peer-reviewed paper with no released code on discontinued hardware, so it is reference material only; it could be re-tiered to B once a verifier can read the paper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** WebSearch summaries of the abstract of 'Acceleration of Large Integer Multiplication with Intel AVX-512 Instructions' (Edamatsu and Takahashi, IEEE HPCC 2018, ieeexplore document 8622797) say it compares execution time and instruction counts with GMP and is 'approximately 2.5x faster than GMP' on Knights Landing. Peer-reviewed, but ieeexplore and semanticscholar are egress-blocked, so the evidence is snippet only and capped at C; no code is attributable to the paper.
- **Verifier notes:** Real peer-reviewed result; stays C because the paper could not be opened. Possible but unconfirmed author code: github.com/Hibari-K/bigint_mul_avx512f (also bigint_mul_avx512f_asm, karatsuba_scal and idiv_evaluator in the same account, no licenses); do not link it without attribution. Lead: a later 'Fast Multiple-Precision Integer Division Using Intel AVX-512' paper surfaced in results, with authors unconfirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier
- **Pages the verifier opened:**
  - <https://github.com/Hibari-K/bigint_mul_avx512f>
  - <https://github.com/Hibari-K>
  - <https://github.com/Hibari-K?tab=repositories>
  - <https://github.com/Hibari-K/bigint_mul_avx512f/commits>
- **Sources the enricher read:**
  - <https://github.com/Hibari-K?tab=repositories>
  - <https://github.com/Hibari-K/bigint_mul_avx512f>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/zmm_mul.h>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/mul_kernel.c>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/multiply.c>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/split_28bit.c>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/cmain.c>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f_asm/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:large-integer-multiplication-with-intel-avx-512-on-knights-landing`) · [data/wave8/enrich/raw/paper_large_integer_multiplication_with_intel_avx_512_on_knights_landing.json](../../../data/wave8/enrich/raw/paper_large_integer_multiplication_with_intel_avx_512_on_knights_landing.json) (enrichment confidence 0.4)

</details>
