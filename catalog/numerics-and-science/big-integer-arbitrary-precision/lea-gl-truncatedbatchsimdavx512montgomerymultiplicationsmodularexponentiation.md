# Truncated batch SIMD AVX512 Montgomery multiplication

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-3.0` · 🟡 stale

> Research C code doing 8 Montgomery multiplications or modexps at once with AVX512-IFMA; \~4-5x GMP/OpenSSL throughput.

| | |
|---|---|
| **Beats** | GMP 6.2.0 (also OpenSSL 3.2.1) |
| **Claimed result** | 8 batched Montgomery multiplications vs 8 GMP calls: 5.34x (1024-bit), 4.86x (2048), 3.95x (4096); vs OpenSSL 4.31x/4.10x/3.69x. Batched fixed-window modexp vs GMP mpn_sec_powm: 5.42x/5.17x/4.66x; vs OpenSSL BN_mod_exp_mont_consttime 3.98x/3.71x/3.30x; vs OpenSSL BN_mod_exp_mont_consttimex2 (AVX512-IFMA 256-bit) only 1.75x (1024) / 1.38x (2048) |
| **Workload** | Batch Montgomery multiplication and fixed-window modular exponentiation, 260-4154 bit operands using AVX512 VPMADD52 |
| **Metric** | throughput |
| **Hardware** | Dell Inspiron laptop, 11th Gen Intel Core i7-1165G7 @ 2.80GHz, Turbo Boost disabled |
| **Compiler and flags** | GCC 9.4.0 -O3 -funroll-all-loops -g -march=native |
| **Adoption** | 3 stars |
| **Last commit** | 2024-09-19 |
| **Links** | [repository](https://github.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation) · [benchmark](https://arxiv.org/html/2410.18129) |

## Verdict

On an i7-1165G7 (Tiger Lake, Turbo off), GCC 9.4.0 -O3 -march=native, a batch of 8 truncated Montgomery multiplications ran 5.34x/4.86x/3.95x faster than 8 GMP 6.2.0 calls at 1024/2048/4096 bits, and batched fixed-window modexp ran 3.98x/3.71x/3.30x faster than OpenSSL 3.2.1 BN_mod_exp_mont_consttime. Against OpenSSL's IFMA consttimex2 path the gain is 1.75x (1024) and 1.38x (2048).

## Use it when

- You have many independent modular multiplications or exponentiations with the same bit size, e.g. batched RSA/DH private-key operations or batch signature work, and can group them in eights.
- Your CPU has AVX512-IFMA (Ice Lake, Tiger Lake, Sapphire Rapids, Zen 4 or later) and you want throughput, not single-operation latency.
- Operand sizes from 1024 to 4096 bits, where the paper measures 3.3-5.4x over GMP mpn_sec_powm and OpenSSL BN_mod_exp_mont_consttime.
- You are studying or prototyping IFMA Montgomery kernels and want a reference for the truncated-reduction trick.

## Skip it when

- You need a single modexp at a time: the speedup comes from 8-way batching, and a batch of one still costs a full batch.
- You already use OpenSSL 3's IFMA path (BN_mod_exp_mont_consttimex2): the margin falls to 1.75x at 1024 bits and 1.38x at 2048, and the 256-bit-vector batch-of-4 variant is only 1.05x faster at 2048 bits.
- You need general big-integer arithmetic (add, divide, GCD, arbitrary sizes): only Montgomery mul/sqr/modexp at compile-time-fixed sizes are provided.
- The CPU lacks AVX512-IFMA (older Intel, Zen 3 and earlier, ARM): the paper notes NEON has no 52-bit multiply-add equivalent and no fallback exists.
- You need GPL-incompatible licensing or a maintained API: GPL-3.0, 7 commits, no releases, benchmark mains rather than a library interface.

## How it is fast

Operands are held in radix 2^52 and word-sliced, so lane i of each 512-bit register holds one word of operand i; VPMADD52LUQ/HUQ then do eight 52x52-bit multiply-adds per instruction. The 'truncated' Montgomery reduction skips computing low-order product words that are known to cancel to zero, which the paper reports saves about 21% over the non-truncated variant. Schoolbook multiplication is used up to 4108 bits and Karatsuba (double Karatsuba at 4154 bits) above that. Each operand size gets its own code: a script includes a size-specific source file (e.g. sb512_1040.c) at build time.

## Compared with alternatives

Pick it over ctbignum or mp++ only for batched fixed-size modular exponentiation on AVX512-IFMA hardware, a case they do not vectorize; for general mpz-style arithmetic use mp++ or FLINT, and for small fixed-limb compile-time arithmetic use ctbignum.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | GMP and OpenSSL libcrypto (linked by the benchmark Makefiles for baselines and tests); libm |
| **Minimum toolchain** | GCC with AVX512-IFMA intrinsics (paper used GCC 9.4.0, -O3 -funroll-all-loops -march=native) |
| **Platforms** | x86-64 with AVX512F + AVX512-IFMA required; Linux assumed (rdtsc/rdpmc benchmarking) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Operand size is a compile-time macro (SIZE) and script.sh rewrites a source include per size, so each size needs a separate build.
- Converting between 64-bit limbs and the 52-bit sliced format costs extra; the paper reports conversion overhead separately, and it is not included in the headline cycle counts.
- Measured on a laptop with Turbo Boost off; AVX512 frequency effects on other CPUs are acknowledged but not characterized.
- The GMP baseline is eight sequential mpn calls; GMP has no batched API, so the comparison is throughput-vs-latency by design.

## Known shortcomings

- Batch of 8 SIMD ops vs 8 sequential GMP/OpenSSL calls; needs AVX512-IFMA; vs OpenSSL's IFMA path only 1.38-1.75x; modular arithmetic only, research code; stale (2024-09-19).
- No library API, only benchmark programs; operand size fixed at compile time (script swaps size-specific source); conversion into batch format excluded from headline cycle counts; one laptop with Turbo Boost off.

## Caveats and trade-offs

Batch-of-8 SIMD throughput compared with 8 sequential GMP/OpenSSL calls; needs AVX512-IFMA (VPMADD52); only modular multiplication and exponentiation, not general bigint; against OpenSSL's own IFMA path (consttimex2) the gain shrinks to 1.38-1.75x; research code (7 commits, 3 stars), GPL-3.0.

Needs AVX512-IFMA; batch (SIMD across independent operands) not single-operation latency.

## Maintenance

Stale research code (last commit 2024-09-19, 3 stars) under GPL-3.0; copyable if GPL fits, but expect to extract kernels from benchmark mains yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** arXiv 2410.18129 compares against GMP 6.2.0 (mpn_sec_powm) and OpenSSL 3.2.1 with GCC 9.4.0 -O3 -funroll-all-loops -march=native on an i7-1165G7 (Turbo off); the paper links the public code repo (Montgomery/, WindowExponentiation/, Openssl_RSA_Z_512/ dirs).
- **Verifier notes:** The record's claimed speedup put the multiplication-vs-OpenSSL range next to the exponentiation figures. I corrected it and added the much smaller margin over OpenSSL's IFMA path.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2410.18129>
  - <https://github.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation>
  - <https://github.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/commits>
- **Sources the enricher read:**
  - <https://github.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation>
  - <https://raw.githubusercontent.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/HEAD/readme.md>
  - <https://raw.githubusercontent.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/HEAD/SBClassicMultiplicationSquaring/Makefile>
  - <https://raw.githubusercontent.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/HEAD/SBClassicMultiplicationSquaring/main.c>
  - <https://raw.githubusercontent.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/HEAD/SBClassicMultiplicationSquaring/script.sh>
  - <https://raw.githubusercontent.com/lea-gl/TruncatedBatchSIMDAVX512MontgomeryMultiplicationsModularExponentiation/HEAD/SBClassicMultiplicationSquaring/fonctions.h>
  - <https://arxiv.org/html/2410.18129>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lea-gl/truncatedbatchsimdavx512montgomerymultiplicationsmodularexponentiation`) · [data/wave8/enrich/raw/github_com_lea_gl_truncatedbatchsimdavx512montgomerymultiplicationsmodularexponentiation.json](../../../data/wave8/enrich/raw/github_com_lea_gl_truncatedbatchsimdavx512montgomerymultiplicationsmodularexponentiation.json) (enrichment confidence 0.8)

</details>
