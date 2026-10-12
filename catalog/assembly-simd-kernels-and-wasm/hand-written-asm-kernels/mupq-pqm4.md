# pqm4

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C / ARM Cortex-M4 assembly` · `Apache-2.0 OR CC0-1.0` · 🟢 active

> Cortex-M4F assembly-optimized ML-KEM and ML-DSA (plus other PQC schemes) that run 1.25-2.1x faster than PQClean clean C.

| | |
|---|---|
| **Beats** | pqm4 'clean' implementations (PQClean portable C) built with the same arm-none-eabi-gcc flags, but with the same hand-written assembly Keccak-f1600 (common/keccakf1600.S) linked in by mk/crypto.mk, so the baseline is portable C plus assembly hashing |
| **Claimed result** | Cycle counts from benchmarks.md (ratios derived from page data). ml-kem-768 KeyGen/Encaps/Decaps: clean 988,722 / 1,138,225 / 1,387,984 vs m4fspeed 642,096 / 658,754 / 707,827 (1.54x / 1.73x / 1.96x). ml-kem-512 KeyGen 595,793 vs 392,423; Decaps 888,653 vs 428,167 (2.08x). ml-dsa-44 KeyGen/Sign/Verify: clean 1,874,405 / 7,925,955 / 2,063,096 vs m4f 1,426,025 / 3,943,121 / 1,421,623 (1.31x / 2.01x / 1.45x). |
| **Workload** | ML-KEM-512/768/1024 KeyGen, Encaps, Decaps and ML-DSA-44/65/87 KeyGen, Sign, Verify on a Cortex-M4 board at 24 MHz: Cortex-M4(F)-specific implementations (m4f, m4fspeed, typically assembly) versus clean C. |
| **Metric** | latency (CPU cycles per operation) |
| **Hardware** | NUCLEO-L4R5ZI (STM32L4R5, Cortex-M4F) at 24 MHz to avoid flash wait states; the README says min/max/avg over 100 executions for most schemes, but the ML-KEM rows cited are over 10 executions and the ML-DSA rows over 1000 executions |
| **Compiler and flags** | arm-none-eabi-gcc (Arm GNU Toolchain 11.3.Rel1) 11.3.1 20220712; default --opt speed, which mupq/mk/config.mk maps to -O3 -g3 (same flags for clean and M4 implementations) |
| **Adoption** | 456 stars, 124 forks; de-facto PQC benchmark framework for Cortex-M4 |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/mupq/pqm4) · [benchmark](https://github.com/mupq/pqm4/blob/master/benchmarks.md) |

## Verdict

benchmarks.md (ML-KEM rows added 2024-11-28 over 10 runs, ML-DSA rows updated 2025-02-10 over 1000 runs) reports SysTick-derived cycle counts on a NUCLEO-L4R5ZI at 24 MHz, built with arm-none-eabi-gcc 11.3.Rel1 at -O3 -g3 with identical -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 flags for clean and optimized variants. ml-kem-768 m4fspeed beats PQClean clean by 1.54x/1.73x/1.96x on KeyGen/Encaps/Decaps and ml-dsa-44 m4f by 1.31x/2.01x/1.45x on KeyGen/Sign/Verify (derived from page data), with both columns sharing the same assembly Keccak.

## Use it when

- Shipping ML-KEM-512/768/1024 on a Cortex-M4F microcontroller (STM32F4/L4 class) where KeyGen/Encaps/Decaps latency matters: ml-kem-768 m4fspeed decapsulates in about 708k cycles vs 1.39M for clean C.
- Stack-constrained ML-KEM: ml-kem-768 m4fstack needs about 2.8-2.9 KB of stack (clean 10-14.5 KB) and is within 1% of m4fspeed's speed.
- Firmware or certificate signature checks on an M4F: ml-dsa-44 m4f verifies in about 1.42M cycles with 8.9 KB of stack vs 2.06M cycles and 36 KB for clean.
- Benchmarking a new Cortex-M4 PQC implementation against established numbers with the same speed/stack/hashing/size harness and board.

## Skip it when

- You need a maintained, audited product library: the README carries a deprecation notice (archive in or after January 2027) and points to mlkem-native and mldsa-native; the PQClean code behind the clean baseline was itself archived in August 2026.
- Targets other than Cortex-M4F: the code uses ARMv7E-M DSP instructions and FPU registers, ml-dsa's ntt.S warns it must never be built for Cortex-M3 (UMULL is not constant time there); use PQRV for RISC-V or neon-ntt for Armv8-A.
- ML-DSA signing on RAM-tight parts: ml-dsa-44 m4f needs about 38 KB of stack for KeyGen and 45 KB for Sign; the m4fstack variant fits in about 5 KB but signs slower than clean C (12.1M vs 7.9M cycles average).
- Flash-bound designs: ml-kem-768 m4fspeed .text is 16,016 bytes vs 5,120 for clean, and ml-dsa-44 m4f is 19,592 vs 8,212.
- You need power/EM side-channel or fault countermeasures: masking is not documented; the goal is speed, stack and constant-time code.

## How it is fast

The NTT and pointwise multiplication are hand-written ARMv7E-M assembly using the DSP halfword SIMD instructions (smulwb, smlabt, pkhtb, uadd16, usub16) and the improved Plantard modular multiplication of IACR ePrint 2022/956 (ML-KEM m4fspeed), with FPU s-registers used as extra storage for twiddle factors (vmov), which is why the variants are named m4f. ML-KEM fuses on-the-fly sampling of the public matrix with the matrix-vector product (matacc_asm.S, matacc_cache32/matacc_opt32 reuse cached products of the secret vector); ML-DSA m4f uses a 32-bit assembly NTT plus a small NTT modulo 769 (smallntt_769.S) for products with the short secret and challenge polynomials. Keccak is a shared XKCP-derived assembly permutation used by every variant, clean included.

## Compared with alternatives

Pick pqm4 when the target is a Cortex-M4F microcontroller: neon-ntt covers Armv8-A Neon (Cortex-A72, Apple M1) and PQRV covers RV32/RV64 cores for the same Kyber/Dilithium arithmetic. aadomn/aes is complementary rather than competing: it is the bitsliced constant-time AES that pqm4's common/aes.h already uses.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | pqm4/mupq shared symmetric code (mupq/common/fips202.c plus common/keccakf1600.S, optionally sha2 and AES) and a randombytes() provider; libopencm3, OpenOCD/stlink and pyserial only for the board harness |
| **Minimum toolchain** | arm-none-eabi-gcc with GNU assembler syntax (numbers taken with Arm GNU Toolchain 11.3.Rel1, 11.3.1 20220712), C gnu99, Python 3.8+ for the harness |
| **Platforms** | ARM Cortex-M4F (ARMv7E-M with FPv4-SP FPU); harness boards NUCLEO-L4R5ZI (default), STM32F4 Discovery, NUCLEO-L476RG, CW308T-STM32F3, MPS2-AN386 (QEMU, cycle counts meaningless there) |
| **Thread safety** | not documented; the functions work on caller buffers and the stack, and the only global (hash_cycles) exists for hash-profiling builds |
| **Drop-in for the baseline** | partial — same crypto_kem_\*/crypto_sign_\* API and test vectors as the PQClean clean code (whose symbols carry a PQCLEAN_..._CLEAN_ prefix), but it only builds for Cortex-M4F |

## Gotchas

- The 'clean C' baseline is not pure portable C: mk/crypto.mk links the same assembly Keccak (common/keccakf1600.S) into every implementation, clean included. The hashing table shows Keccak costs the same cycles in both columns (ml-kem-768 KeyGen about 479k of 989k clean vs 478k of 642k m4fspeed), so outside hashing the M4 code is about 3.1x (KeyGen) to 4.1x (Decaps) faster for ml-kem-768 and 2.5-3.5x for ml-dsa-44 (derived from page data); the end-to-end 1.25-2.1x across ML-KEM and ML-DSA is capped by shared Keccak.
- ML-DSA signing time is dominated by rejection sampling: ml-dsa-44 m4f Sign ranges from 1.81M to 17.0M cycles (average 3.94M over 1000 runs), so budget for the tail, not the average.
- Licensing is per file, there is no top-level LICENSE file: the README dual-licenses non-implementation code under Apache-2.0 or CC0, but ml-dsa-44/m4f/smallntt_769.S carries an Apache-2.0-only header (Junhao Huang, 2023) while ntt.S is CC0 by permission; check headers before treating a directory as CC0.
- Implementations are research code of uneven review: open issue #404 reports BIKE m4f with its Fujisaki-Okamoto constant-time protections commented out. Issue #411 (swapped polyveck_make_hint arguments, 'all signatures fail') names crypto_sign/dilithium2/m4fspeed, a path absent from master; master ml-dsa-44/m4f/sign.c passes (w0, w1) in the reference order, and ml-kem m4fspeed compress/tomsg already use the KyberSlash-safe multiply-shift instead of division.

## Known shortcomings

- benchmarks.md numbers exact (-O3 -g3 via mupq/mk/config.mk) but mixed C+asm vs clean C; deprecation notice (archive in or after January 2027); ML-KEM rows use 10 executions, not 100.
- The 'clean C' baseline is not pure C: mk/crypto.mk links the same assembly Keccak (common/keccakf1600.S) into every implementation, and the hashing table shows near-identical Keccak cycles in both columns (ml-kem-768 KeyGen about 479k vs 478k), so outside Keccak the M4 code is 3.1-4.1x faster (ml-kem-768) and 2.5-3.5x (ml-dsa-44) while the end-to-end 1.25-2.1x is capped by the shared Keccak (derived from page data); not a harness bug. Deprecated (issue #409, archive in or after January 2027; PQClean archived August 2026). Licence per file (ml-dsa-44/m4f/smallntt_769.S Apache-2.0 only; no top-level LICENSE); ml-dsa m4f stack 38-45 KB; the issue #411 swapped make_hint path is absent from master; KyberSlash-safe compress confirmed.

## Caveats and trade-offs

The m4/m4f implementations are 'typically' assembly; many are mixed C and assembly (e.g. ml-kem-768/m4fspeed has fastntt.S, fastbasemul.S, matacc_asm.S, reduce.S alongside C files, using the improved Plantard arithmetic of IACR ePrint 2022/956), so the comparison is optimized-M4 vs portable C rather than strictly hand-asm vs C. ML-DSA signing has high variance from rejection sampling (clean min 3,322,507 to max 33,055,004 cycles; averages over 1000 runs). m4fstack variants trade speed for stack. SPHINCS+ rows have only a clean C implementation. The README now carries a deprecation notice: the project is no longer under active maintenance, will likely be archived in or after January 2027, and points to mlkem-native and mldsa-native as maintained successors. Per-implementation directories checked (ml-kem-768/m4fspeed, ml-dsa-44/m4f) carry no own LICENSE file, so they fall under the repository's Apache-2.0 OR CC0-1.0 terms. [retier] The m4/m4f implementations are 'typically' assembly; many are mixed C and assembly (e.g. ml-kem-768/m4fspeed has fastntt.S, fastbasemul.S, matacc_asm.S, reduce.S alongside C files, using the improved Plantard arithmetic of IACR ePrint 2022/956), so the comparison is optimized-M4 vs portable C rather than strictly hand-asm vs C. The 'clean C' baseline is not pure portable C: mk/crypto.mk links the same assembly Keccak (common/keccakf1600.S) into every implementation, and the hashing table shows Keccak costs the same cycles in both columns (ml-kem-768 KeyGen about 479k of 989k clean vs 478k of 642k m4fspeed), so outside hashing the M4 code is about 3.1x (KeyGen) to 4.1x (Decaps) faster for ml-kem-768 and 2.5-3.5x for ml-dsa-44 while the end-to-end 1.25-2.1x is capped by the shared Keccak (derived from page data). ML-DSA signing has high variance from rejection sampling (ml-dsa-44 m4f Sign 1.81M to 17.0M cycles, average 3.94M over 1000 runs; clean 3.32M to 33.1M); m4fstack variants trade speed for stack (ml-dsa m4f stack 38-45 KB); SPHINCS+ rows have only a clean C implementation. The README carries a deprecation notice (issue #409: no longer under active maintenance, to be archived in or after January 2027; PQClean archived August 2026). Licensing is per file with no top-level LICENSE: ml-dsa-44/m4f/smallntt_769.S is Apache-2.0 only while ntt.S is CC0 by permission. Research code of uneven review: open issue #404 reports BIKE m4f with its Fujisaki-Okamoto protections commented out; the issue #411 swapped make_hint path is absent from master; ml-kem m4fspeed compress/tomsg use the KyberSlash-safe multiply-shift.

Cortex-M4/M4F specific (ARMv7E-M assembly, FPU registers in m4f); not portable to other cores. m4fspeed ML-KEM-768 code size is 16,016 bytes vs 5,120 for clean in the size table; the m4fstack variants trade speed for stack. Each implementation directory carries its own LICENSE.

## Maintenance

Commits continue (last 2026-09-04), but issue #409 (2026-08-22) deprecates pqm4: final pull requests by 30 November 2026 and archive in or after January 2027, with a volunteer co-maintainer invited on 2026-08-31; the per-scheme source is copyable under Apache-2.0 or CC0 apart from files with their own headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks.md lists clean (PQClean C) and m4f/m4fspeed rows side by side; benchmark code is public (benchmarks.py plus the mupq speed harness), the README names arm-none-eabi-gcc 11.3.Rel1 11.3.1 20220712 and the 24 MHz NUCLEO-L4R5ZI board, and the default --opt speed maps to -O3 -g3 in mupq/mk/config.mk.
- **Verifier notes:** All cited cycle counts match benchmarks.md exactly and the derived ratios are correct (ml-kem-768 1.54x/1.73x/1.96x; ml-kem-512 Decaps 2.08x; ml-dsa-44 1.31x/2.01x/1.45x). Metadata confirmed: 456 stars, 124 forks, not archived, last commit 2026-09-04; maintenance_status stays active by the commit-date rule but the deprecation notice should be recorded as a shortcoming.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-30 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/benchmarks.md>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/README.md>
  - <https://github.com/mupq/pqm4>
  - <https://github.com/mupq/pqm4/commits/master>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/config.mk>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/mk/config.mk>
  - <https://github.com/mupq/pqm4/tree/master/crypto_kem/ml-kem-768/m4fspeed>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/fastntt.S>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/README.md>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/benchmarks.md>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/config.mk>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/crypto.mk>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/tests.mk>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/nucleo-l4r5zi.mk>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/mk/opencm3.mk>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/ldscripts/devices.data>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/benchmarks.py>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/common/hal-opencm3.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/common/keccakf1600.S>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/crypto_kem/speed.c>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/crypto_sign/speed.c>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/mk/config.mk>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/mk/schemes.mk>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/mk/rules.mk>
  - <https://raw.githubusercontent.com/mupq/mupq/HEAD/common/fips202.c>
  - <https://github.com/mupq/pqm4/tree/master/crypto_kem/ml-kem-768/m4fspeed>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/poly.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/polyvec.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/indcpa.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/matacc.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/fastntt.S>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_kem/ml-kem-768/m4fspeed/reduce.S>
  - <https://github.com/mupq/pqm4/tree/master/crypto_sign/ml-dsa-44/m4f>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/ml-dsa-44/m4f/sign.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/ml-dsa-44/m4f/ntt.S>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/ml-dsa-44/m4f/smallntt_769.S>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/ml-dsa-44/m4f/smallpoly.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/dilithium2/m4fspeed/sign.c>
  - <https://raw.githubusercontent.com/mupq/pqm4/HEAD/crypto_sign/ml-dsa-44/m4fspeed/sign.c>
  - <https://github.com/mupq/pqm4/issues/409>
  - <https://github.com/mupq/pqm4/issues/411>
  - <https://github.com/mupq/pqm4/issues?q=is%3Aissue+kyberslash+OR+timing+OR+bug>
  - <https://github.com/mupq/pqm4/commits/master/benchmarks.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mupq/pqm4`) · [data/wave13/enrich/raw/github_com_mupq_pqm4.json](../../../data/wave13/enrich/raw/github_com_mupq_pqm4.json) (enrichment confidence 0.85)

</details>
