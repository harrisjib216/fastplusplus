# Optimizing Dilithium Implementation with AVX2/AVX-512 (PSPM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `no license` · 🟡 stale

> Research AVX2/AVX-512 Round 3 Dilithium code using PSPM-TEE sparse c·s multiplication; paper reports 1.6-2.9x fewer cycles than pq-crystals AVX2.

| | |
|---|---|
| **Beats** | pq-crystals/dilithium AVX2 implementation: the 'standard' branch (FIPS 204 ML-DSA) AVX2 code for the headline Table XI numbers, and the NIST Round 3 submission AVX2 code for Table IX. This is the upstream code that liboqs/PQClean also derive from; liboqs and PQClean were not benchmarked directly. |
| **Claimed result** | Cycle-count reductions of AVX-512 vs the pq-crystals FIPS 204 AVX2 code (Table XI) for ML-DSA-44/65/87: KeyGen 43.2%/39.3%/45.6%, Sign 36.6%/41.6%/43.7%, Verify 45.3%/46.5%/47.4%. For example, ML-DSA-44 KeyGen drops from 84270 to 47760 cycles. That is about 1.58x-1.90x faster (derived from page data). Against the NIST Round 3 AVX2 code (Table IX), Dilithium2/3/5 cycle reductions are 50.0%-65.1%, about 2.0x-2.9x (derived from page data). Within both the AVX2 and the AVX-512 implementations, PSPM cuts c·s / c·e multiplication cycles by 47%-66% versus NTT (Table VI, Dilithium3). |
| **Workload** | Round 3 Dilithium2/3/5 and FIPS 204 ML-DSA-44/65/87 KeyGen, Sign and Verify cycle counts on one core (median of 100000 runs). PSPM(-TEE) replaces NTT for the small-polynomial products (c·s, c·e) in both the AVX2 and AVX-512 implementations, not only on the AVX-512 path. Metric is per-operation cycles (latency). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-11700F (Rocket Lake) at 2.5 GHz, TurboBoost and Hyper-Threading disabled, Ubuntu 20.04 |
| **Compiler and flags** | gcc-9.4.0 with -Wshadow -Wpointer-arith -mavx2 -mavx512f -mavx512vbmi -mavx512bw -mavx512cd -mavx512vl -mpopcnt -maes -march=native -mtune=native -O3. The paper prints the AVX-512 flags as '-mAVX-512F' etc.; the repo Makefiles use -mavx512\*. |
| **Adoption** | 3 stars |
| **Last commit** | 2025-07-16 |
| **Links** | [repository](https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512) · [benchmark](https://arxiv.org/abs/2306.01989) |

## Verdict

On one core of an Intel i7-11700F at 2.5 GHz (Turbo and HT off, Ubuntu 20.04, gcc 9.4.0 -O3 -march=native plus AVX-512 flags, median of 100000 runs), the paper's AVX-512 code needs 36.6-47.4% fewer cycles than the pq-crystals FIPS 204 AVX2 code (e.g. ML-DSA-44 KeyGen 47760 vs 84270 cycles, about 1.6-1.9x). It needs 50.0-65.1% fewer cycles than the Round 3 AVX2 code (about 2.0-2.9x). PSPM alone cuts the Dilithium3 c·s / c·e product by 47-66% versus NTT but only speeds up whole AVX2 signing by about 3-8%. The repo cannot reproduce the ML-DSA table or either full-scheme baseline.

## Use it when

- Studying or porting PSPM-TEE: the repo's PSPMTEE.c shows a 64-coefficient-per-zmm int8-table version of the sparse c·s product with early norm checks
- Reading reference AVX-512 kernels for Dilithium (16-way NTT in ntt512.c/inv_ntt512.c, 8-way SHAKE sampling in fips202x8.c and keccak8x.c) when writing your own ML-DSA backend
- Checking the paper's component benchmarks: dilithium2_avx512/test/test_speed.c times PQClean ('clean') against the authors' ('xurq') Keccak permutation, matrix expansion, uniform_eta and uniform_gamma1 side by side
- Research on Rocket Lake / Ice Lake-class CPUs with full AVX-512 (F/VL/CD/BW/DQ/VBMI/VBMI2), where the paper's i7-11700F numbers apply

## Skip it when

- Any production or FIPS 204 use: the repo is Round 3 Dilithium only (Dilithium2 sk = 2528 bytes) and does not include the ML-DSA code behind the headline Table XI numbers
- Anywhere you need a license: there is no LICENSE file, so legally the code is reference-only even though parts derive from permissively licensed PQClean/NIST code
- Code you would trust without re-testing. By reading (not running) it: only dilithium5_avx512 signing actually calls pspm_tee_r0/pspm_tee_z, and those functions store |value| (after _mm512_abs_epi32) into z and r0 before z is packed into the signature. The last 64-coefficient block is also loaded at offset N+182-j, versus 192 in pspm()
- CPUs without AVX-512 (many client Intel parts, older AMD): the _avx512 trees are compiled with -mavx512f/vl/cd/bw/dq/vbmi/vbmi2, and the AVX2 trees gain only about 3-8% in signing from PSPM-TEE (paper Tables VII/X)
- Side-channel-sensitive deployments: the paper says constant-time was 'not the focus', and PSPM-TEE branches on challenge coefficients and returns early from rejection checks

## How it is fast

PSPM (parallel small polynomial multiplication, from Zheng et al., ACSAC 2022) exploits the fact that the challenge c has only tau coefficients equal to ±1. It packs the small secret polynomials into a precomputed table, so c·s1 and c·s2 become tau shifted adds or subtracts instead of an NTT. PSPM-TEE adds 'tailored early evaluation': it checks the r0 norm before the z norm (r0 rejects more often) one polynomial at a time and aborts at the first failure. The paper credits most of the AVX-512 gain to other work: a 16-way AVX-512 NTT/NTT^-1 with merged layers, 8-way AVX-512 Keccak for matrix and vector sampling, vectorized rejection sampling and packing, and a 'tailored reduction' for q = 2^23 - 2^13 + 1 using AVX-512IFMA.

## Compared with alternatives

Dilithium-AVX512 (github.com/Dilithium-AVX512/Dilithium-AVX512) is catalogued from the same paper with the same numbers. It is a single pq-crystals-style tree with KAT files and a DILITHIUM_MODE switch, but it has no PSPM code. Pick this repo only when you want the PSPM-TEE source and the AVX2 variants; for a usable ML-DSA, neither sibling qualifies, and the Plantard-NTT codegen entry is the more rigorous (formally verified) option if you need portable speedups.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc; Keccak (XKCP-style KeccakP-1600 times4/times8 files) and Daan Sprenkels' MIT randombytes.c are bundled |
| **Minimum toolchain** | GCC with AVX-512 intrinsics; the paper used gcc 9.4.0, and the dilithium5_avx512 Makefile adds -std=c99 |
| **Platforms** | x86-64 only. The _avx2 trees need AVX2+POPCNT; the _avx512 trees need AVX-512F/VL/CD/BW/DQ/VBMI/VBMI2. Benchmarked only on an Intel i7-11700F (Rocket Lake) |
| **Thread safety** | Not documented. dilithium2_avx512/sign.c increments a file-scope 'int count' inside the signing function, so concurrent signing races on it. |
| **Drop-in for the baseline** | partial — it produces Round 3 Dilithium byte formats with NIST crypto_sign-style signatures, but the function prefixes are renamed and inconsistent, the LIB Makefile targets omit the AVX-512/PSPM objects, and it is not FIPS 204 ML-DSA |

## Gotchas

- PSPM is not used in most trees: dilithium2_avx512 compiles PSPMTEE.c but signs with NTT, and dilithium3_avx512 plus all three _avx2 trees contain no PSPM code, although the paper describes PSPM-TEE for AVX2 and AVX-512
- The test_speed harnesses never check verify's return value (the D5 AVX-512 harness even signs in place over its message buffer). They run NTESTS = 10000, not the paper's 100000 repetitions, so a passing speed run proves nothing about correctness
- Build artifacts are committed (common/keccak/\*.o and a roughly 20 MB 'our_3_avx512_test_speed' binary in dilithium3_avx512); rebuild from source rather than trusting them
- The paper's text and tables disagree on where PSPM-TEE helps most: the text says 7.7% for Dilithium3, while Table VII shows 7.7% for Dilithium2 and 3.1% for Dilithium3

## Known shortcomings

- Repo holds Round 3 Dilithium only: no ML-DSA code behind the headline numbers and no pq-crystals baseline in the repo (retiered A to B on the peer-reviewed TDSC 2025 paper). Percentages are cycle-count reductions (\~1.58-1.90x). No license: reference use only.
- PSPM is only called in dilithium5 AVX-512 signing (dilithium2 AVX-512 compiles it but never calls it; dilithium3 AVX-512 and all AVX2 trees lack it); PSPM-TEE alone gives only 3-8% AVX2 signing gain. By code reading, pspm_tee_z/r0 store abs() values into z/r0 that are then packed into the signature, so signatures may be wrong; speed tests never check the verify result and run 10,000 iterations vs the paper's 100,000. Object files and a \~20 MB binary are committed. A second anonymous repo (Dilithium-AVX512/Dilithium-AVX512) for the same paper is a plain AVX-512 port without these techniques and exports pq-crystals symbol names.

## Caveats and trade-offs

The repo has no LICENSE file (GitHub license null), so it is reference-only. The code derives from the NIST reference Dilithium and PQClean, but the repo itself grants no license. The repo describes itself as 'the source code of the paper Optimizing Dilithium Implementation with AVX2/-512', but the arXiv v3 PDF still says 'We will later open source our code' and does not link it. The owner xurq5953 does not match a listed author name, so the attribution rests on the repo's own statement. The repo holds Round 3 Dilithium only (Dilithium2 sk 2528 bytes), so the headline ML-DSA numbers in the abstract/Table XI cannot be reproduced from it. The percentages are cycle reductions, not throughput increases. The paper says the implementation is not fully constant-time-audited. It also notes that some hash functions are not yet vectorized.

Requires AVX-512 hardware support (not present on all deployed x86-64 CPUs, and historically disabled on some consumer Intel chips); the PSPM technique changes the internal multiplication algorithm, so it is not a drop-in replacement without re-verifying constant-time behavior.

## Maintenance

Stale research dump (10 commits, last 2025-07-16, 3 stars, no issues) with no license, so it is reference-only; treat it as a companion to the TDSC paper, not a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The paper is peer-reviewed (IEEE TDSC 2025, DOI 10.1109/TDSC.2025.3575915; arXiv 2306.01989v3). It states gcc-9.4.0, the flags and an i7-11700F, and compares against the pq-crystals AVX2 code (Tables IX and XI). It falls short of A because the repo's per-variant test/test_speed.c harness only covers the authors' own Round 3 AVX2/AVX-512 code (Dilithium2 sk = 2528 bytes). The repo ships neither a clearly identified unmodified pq-crystals/NIST AVX2 baseline nor the FIPS 204 ML-DSA code behind the headline Table XI numbers.
- **Verifier notes:** Downgraded A-&gt;B: the paper is peer-reviewed and its methodology is complete, but the artifact repo lacks the baseline and the ML-DSA variant the claimed numbers come from. All claimed percentages appear verbatim in the abstract and Table XI. Metadata checked: 3 stars, not a fork, not archived, last commit 2025-07-16 (stale), no license, so usability is corrected from 'mixed' to 'reference'.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2306.01989>
  - <https://arxiv.org/abs/2306.01989v1>
  - <https://arxiv.org/pdf/2306.01989>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512>
  - <https://api.crossref.org/works?query.bibliographic=Optimized+Vectorization+Implementation+of+CRYSTALS-Dilithium>
- **Sources the enricher read:**
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/README.md>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/commits/main>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/issues>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/PSPMTEE.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium5_avx512/PSPMTEE.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium5_avx512/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium3_avx512/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx2/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium3_avx2/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium5_avx2/sign.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/Makefile>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium5_avx512/Makefile>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/api.h>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/params.h>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/test/test_speed.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium5_avx512/test/test_speed.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium3_avx2/test/test_mul.c>
  - <https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512/blob/main/dilithium2_avx512/randombytes.c>
  - <https://api.github.com/users/xurq5953/repos>
  - <https://arxiv.org/abs/2306.01989>
  - <https://arxiv.org/pdf/2306.01989>
  - <https://api.crossref.org/works/10.1109/TDSC.2025.3575915>
  - <https://api.crossref.org/works?query.bibliographic=Optimizing+Dilithium+Implementation+with+AVX2+AVX-512>
  - <https://eprint.iacr.org/search?q=Dilithium+AVX-512>
  - <https://github.com/Dilithium-AVX512/Dilithium-AVX512>
  - <https://github.com/Dilithium-AVX512/Dilithium-AVX512/blob/main/config.h>
  - <https://github.com/Dilithium-AVX512/Dilithium-AVX512/blob/main/sign.c>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/xurq5953/optimizing-dilithium-implementation-with-avx2-512`) · [data/wave7/enrich/raw/github_com_xurq5953_optimizing_dilithium_implementation_with_avx2_512.json](../../../data/wave7/enrich/raw/github_com_xurq5953_optimizing_dilithium_implementation_with_avx2_512.json) (enrichment confidence 0.75)

</details>
