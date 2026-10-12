# AVX-512IFMA large integer multiplication (Edamatsu and Takahashi)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Study only · `unknown` · `no license` · ⚪ unknown

> Peer-reviewed AVX-512IFMA large-integer multiplication method, reported up to about 2.97x faster than GMP; no code released.

| | |
|---|---|
| **Beats** | GMP |
| **Claimed result** | Up to about 3.07x faster than the authors' own AVX-512F implementation and about 2.97x faster than GMP for large-integer multiplication on a Cannon Lake CPU (abstract as quoted in WebSearch summaries; paper not opened). |
| **Workload** | Large-integer multiplication using Intel AVX-512IFMA (52-bit multiply-add, reduced-radix representation with the spare 12 bits used to accumulate carries) on a Cannon Lake processor, compared with the authors' AVX-512F implementation and with GMP. |
| **Metric** | throughput |
| **Hardware** | Cannon Lake processor with AVX-512IFMA (exact model not seen) |
| **Links** | [benchmark](https://www.semanticscholar.org/paper/Accelerating-Large-Integer-Multiplication-Using-Edamatsu-Takahashi/ee766c654ad4acc8d42340ff3b5fd37f1229dff3) |

## Verdict

Two search-engine summaries of the abstract (paper not opened) report large-integer multiplication with AVX-512IFMA up to about 3.07x faster than the authors' AVX-512F implementation and about 2.97x faster than GMP on a Cannon Lake processor. GMP version, operand sizes, compiler and flags are not documented.

## Use it when

- You are writing your own mpn-level multiply kernel for x86 cores with AVX-512IFMA (Cannon Lake, Ice Lake and later Intel parts that kept it, AMD Zen 4/5 per the record) and want a peer-reviewed design reference for radix-2^52 vector multiplication.
- Sizing the payoff before adding an IFMA path to a bignum library: the paper's reported best case is about 2.97x over GMP and 3.07x over an AVX-512F implementation on one CPU.
- Comparing against the authors' earlier AVX-512F (Knights Landing) design to see how much IFMA adds over a 32-bit-multiply vector kernel.

## Skip it when

- You need code you can run: nothing is published, so has_code is false and every number is the authors' own.
- CPUs without AVX-512IFMA (anything before Cannon Lake/Ice Lake and later parts that dropped the extension): the technique cannot run there.
- Very large operands where GMP switches to Toom-Cook or FFT multiplication: the operand-size range of the reported speedup is not documented, so it may not hold there.
- Constant-time or cryptographic use: no side-channel properties are documented; for RSA-size modular work OpenSSL's IFMA almost-Montgomery routines (benchmarked in the VROOM sibling entry) are shipping code.
- Decisions that need typical rather than best-case gains: both ratios are 'up to' figures.

## How it is fast

AVX-512IFMA (VPMADD52LUQ / VPMADD52HUQ) multiplies 52-bit fields in each of eight 64-bit lanes and adds the low or high 52 bits of the product into a 64-bit accumulator. Storing operands in radix 2^52 leaves 12 spare bits per lane, so many partial products can be summed before any carry has to be propagated, and carry normalization is deferred. That gives eight 52x52-bit products per instruction instead of GMP's scalar 64x64-bit multiply-with-carry chain, and products wider than the 32x32-bit VPMULUDQ products an AVX-512F-only kernel is limited to. Whether it uses schoolbook, Karatsuba or Toom-style splitting is not documented in anything readable this session.

## Compared with alternatives

Read it when designing a general (non-modular) IFMA multiply for single large operand pairs; for runnable code, DigitsOnTurbo patches GMP's multiplication (1.41x geomean at 512-32768 bits), lea-gl's truncated batch AVX-512 Montgomery code beats GMP 3.95-5.34x on batched modular products, and FLINT is the practical pick for very large sizes.

## Integration

| | |
|---|---|
| **Form** | not released (paper only) |
| **Dependencies** | not documented |
| **Minimum toolchain** | not documented (needs a compiler with AVX-512IFMA intrinsics or assembler support) |
| **Platforms** | x86-64 with AVX-512IFMA required; measured on a Cannon Lake processor (exact model not documented) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Evidence is snippet only: the chapter (DOI 10.1007/978-3-030-38991-8_5) could not be opened because link.springer.com and semanticscholar are egress-blocked, so GMP version, operand sizes, compiler, flags and exact CPU are unknown.
- A radix-2^52 kernel needs conversion from and to GMP's 64-bit limbs (split and recombine passes); whether that cost is inside the reported times is not documented.
- Cannon Lake, the test CPU, was a short-lived discontinued microarchitecture, so the ratios may differ on Ice Lake, Sapphire Rapids or Zen 4/5.
- No public repository is attributable: github.com/topics/avx512ifma lists no repositories, and Hibari-K's AVX-512F multiply repos (no IFMA variant, no license) are not linked to the authors.

## Known shortcomings

- No public code; snippet-only evidence (ICA3PP 2019 paper unreachable here); 'up to' best-case ratios (2.97x over GMP, 3.07x over own AVX-512F); discontinued CPU (Cannon Lake); GMP version, flags and operand sizes unknown.

## Caveats and trade-offs

Snippet only: the paper (ICA3PP 2019, Springer LNCS, DOI 10.1007/978-3-030-38991-8_5; also indexed on semanticscholar and ResearchGate) could not be opened because semanticscholar, link.springer.com, dl.acm.org and researchgate are egress-blocked. The 3.07x/2.97x figures and the attribution to this paper are now confirmed by two separate search summaries of its abstract, and both are 'up to' (best-case) ratios. Peer-reviewed venue, so a verifier who can open the paper may re-tier to B. GMP version, operand sizes, compiler, flags and exact CPU model are unknown; GMP has no AVX-512 kernels, so the baseline is presumably its scalar x86-64 mpn code. Cannon Lake was a short-lived, discontinued microarchitecture (IFMA now ships on Ice Lake and later Intel cores and on AMD Zen 4/5). No public code found (WebSearch for code and PDF copies on GitHub turned up nothing attributable), so has_code=false.

Needs AVX-512IFMA hardware (Cannon Lake, Ice Lake and later server/desktop parts that kept the extension).

## Maintenance

A 2019 peer-reviewed paper with no released code or license, so it is reference material only; it could be re-tiered to B once a verifier can read the paper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Two independent WebSearch summaries of the abstract (Edamatsu and Takahashi, ICA3PP 2019, Springer LNCS chapter 10.1007/978-3-030-38991-8_5) give 'up to approximately 3.07 times faster than AVX-512F and approximately 2.97 times faster than GMP' on Cannon Lake. The paper is peer-reviewed, which would justify B, but semanticscholar, Springer and ACM are egress-blocked, so it was never opened and the numbers are snippet only; the harness caps snippet-only evidence at C, and no code was found.
- **Verifier notes:** Real peer-reviewed result; numbers and attribution confirmed via search summaries only, so it stays C; candidate for a B retier once springer/semanticscholar is reachable. A search summary also mentioned an Intel Core i3-8121U, but my query contained that model name, so hardware was left uncorrected. Shortcomings to record: no public code, snippet-only evidence, best-case 'up to' ratios, discontinued test CPU.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier
- **Sources the enricher read:**
  - <https://github.com/topics/avx512ifma>
  - <https://github.com/topics/avx512>
  - <https://github.com/Hibari-K?tab=repositories>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hibari-K/bigint_mul_avx512f_asm/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:avx-512ifma-large-integer-multiplication-edamatsu-and-takahashi`) · [data/wave8/enrich/raw/paper_avx_512ifma_large_integer_multiplication_edamatsu_and_takahashi.json](../../../data/wave8/enrich/raw/paper_avx_512ifma_large_integer_multiplication_edamatsu_and_takahashi.json) (enrichment confidence 0.4)

</details>
