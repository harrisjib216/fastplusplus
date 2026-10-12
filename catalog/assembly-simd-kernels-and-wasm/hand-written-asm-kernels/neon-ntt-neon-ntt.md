# neon-ntt (hand-written Armv8-A Neon assembly NTTs for Dilithium, Kyber and Saber)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR CC0-1.0` · 🟡 stale

> Hand-written Armv8-A Neon assembly NTTs for Kyber, Dilithium and Saber; about 4-6x faster than reference-C Dilithium NTTs.

| | |
|---|---|
| **Beats** | Dilithium reference C implementation (pq-crystals ref code compiled with gcc 10.3.0 -O3 on Cortex-A72 and Apple clang 12.0.5 -O3 on Apple M1); for Kyber and Saber the baseline is the previous Neon implementation by Nguyen and Gaj (re-benchmarked in SUPERCOP) |
| **Claimed result** | Paper Table 4 (dilithium3, Cortex-A72): NTT 2 241 cycles vs 9 302 for the reference code (4.15x, derived from page data), inverse NTT 2 821 vs 11 633 (4.12x, derived); Apple M1 NTT 479 vs 2 865 (5.98x, derived). Table 5: dilithium2 MatrixVectorMul 26 268 vs 135 182 cycles on Cortex-A72 (5.15x, derived) and 5 316 vs 45 742 on M1 (8.6x, derived). Table 6 (dilithium3, Cortex-A72): key generation 515 776 vs 743 166 cycles (1.44x, derived), signing 1 089 387 vs 2 308 598 (2.12x, derived), verification 447 460 vs 728 866 (1.63x, derived). Against prior Neon work the paper states kyber768 MatrixVectorMul is 1.7x faster on Cortex-A72 and 2.1x on M1, full Kyber 9-14% faster on Cortex-A72 and 26-41% on M1, Saber MatrixVectorMul 2.0x on Cortex-A72. |
| **Workload** | Median or mean cycle counts for NTT, inverse NTT, base multiplication, matrix-vector multiplication, inner product and full key generation, encapsulation/signing and decapsulation/verification of Dilithium2/3/5, Kyber512/768/1024 and Saber on a Raspberry Pi 4 (Cortex-A72) and an Apple M1. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi 4 Model B (Broadcom BCM2711, Arm Cortex-A72 at 1.5 GHz); Apple M1 Mac mini |
| **Compiler and flags** | gcc 10.3.0 -O3 on Cortex-A72 (full schemes through SUPERCOP 20210604); Apple clang 12.0.5 -O3 on Apple M1 |
| **Adoption** | 34 stars; artifact of a TCHES 2022 paper |
| **Last commit** | 2024-11-10 |
| **Links** | [repository](https://github.com/neon-ntt/neon-ntt) · [benchmark](https://raw.githubusercontent.com/vincentvbh/vincentvbh.github.io/master/papers/2021-986.pdf) |

## Verdict

On a Raspberry Pi 4 (Cortex-A72 at 1.5 GHz, gcc 10.3.0 -O3, PMU medians) and an Apple M1 (Apple clang 12.0.5 -O3, averages), the dilithium3 Neon NTT takes 2 241 cycles against 9 302 for pq-crystals reference C (4.15x; 5.98x on M1), dilithium2 MatrixVectorMul 26 268 against 135 182 (5.15x), and full dilithium3 signing in SUPERCOP 20210604 1 089 387 against 2 308 598 cycles (2.12x). Against Nguyen-Gaj's Neon Kyber, full Kyber is 9-14% faster in a same-harness SUPERCOP re-run on Cortex-A72 (ratios derived from paper data).

## Use it when

- Round-3 Kyber or Dilithium on 64-bit Armv8-A application cores (Cortex-A72 class, Apple M1) where polynomial arithmetic dominates: dilithium3 signing 2.12x the reference on Cortex-A72 and 3.3x on M1 (derived from paper Table 6).
- Matrix-vector-heavy lattice code: kyber768 MatrixVectorMul 11 077 cycles on Cortex-A72 and 2 291 on M1; dilithium2 26 268 vs 135 182 cycles for reference C.
- As a reference design when porting Neon NTTs to another lattice scheme or modulus; the Barrett-multiplication and asymmetric-multiplication tricks are documented in the paper and visible in the .S files.
- Reproducible academic baseline: pinned commit a96c17d plus SUPERCOP 20210604 reproduce the paper's full-scheme tables on a Raspberry Pi 4.

## Skip it when

- Production ML-KEM/ML-DSA (FIPS 203/204): the paper code is round-3 Kyber/Dilithium; HEAD's Oct 2024 commits ('update dilithium to standard', 'sync to standard') move toward the standards, but the README documents no conformance testing. The maintained route is mlkem-native (SLOTHY-scheduled AArch64 assembly with HOL-Light proofs, default in liboqs 0.13.0 and in AWS-LC).
- Anything other than 64-bit Arm: no x86 path, and a 32-bit OS fails with assembler errors such as "bad instruction 'stp x19,x20,...'" (issue #1); for Cortex-M4 use pqm4, for RISC-V use PQRV.
- Saber at HEAD: commit fb2e067 (2024-10-12) says 'Saber not working now, but will soon' and no later commit message reports a fix; Saber was also not standardised by NIST.
- When you already have a good Neon Kyber: against Nguyen-Gaj's Neon code full Kyber is only 9-14% faster on Cortex-A72.
- When you need documented side-channel review or formal verification: neither is claimed in the README or the paper's results section.

## How it is fast

The paper's core idea is 'Barrett multiplication', a Montgomery/Barrett hybrid for multiplying by a known constant with Neon sqrdmulh/mul/mls, combined with two-unknown-factor Montgomery multiplication, Barrett reduction sequences and interleaved multi-stage butterflies that merge NTT layers to cut loads and stores. 'Asymmetric multiplication' caches precomputed products of the incomplete NTT so matrix-vector products do less work, and Saber switches from Toom-Cook or 16-bit NTTs plus CRT to a single 32-bit NTT. Full-scheme numbers also use a two-way Neon Keccak on Cortex-A72 and Keccak with the M1's SHA-3 instructions (feat.S from armed-keccak).

## Compared with alternatives

Pick neon-ntt over pqm4 (Cortex-M4) and PQRV (RISC-V) when the target is a 64-bit Armv8-A core with Neon; for maintained FIPS 203 code on AArch64, mlkem-native (not catalogued) builds on the same line of work.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the kernels; full schemes need a randombytes source (SUPERCOP's, or the bundled one in m1_benchmarks) and use the bundled fips202/fips202x2 Keccak; M1 benchmarks need m1cycles.c and root |
| **Minimum toolchain** | gcc 10.3.0 on 64-bit Ubuntu 21.04 (tested) or Apple clang 12.0.5 on macOS 11.4 (tested); any aarch64 assembler with Neon |
| **Platforms** | aarch64 (Armv8-A Neon) only; tested on Cortex-A72 (Raspberry Pi 4) and Apple M1; the M1 Keccak path needs the SHA-3 extension; benchmark harness tested only on Cortex-A72 |
| **Thread safety** | not documented (the kernels read caller buffers and constant tables; no global state seen in the files read) |
| **Drop-in for the baseline** | partial: a scheme directory replaces the round-3 reference implementation behind the same crypto_kem_\*/crypto_sign_\* API, but only on aarch64 and only for the round-3 parameter sets |

## Gotchas

- Cross-run comparisons behind the Kyber/Saber headlines: Table 5's Cortex-A72 Nguyen-Gaj rows are round hundreds (kyber768 MatrixVectorMul 19 300, saber 71 300) and Table 6's Apple M1 Nguyen-Gaj rows (23 000, 36 300, 51 300) carry no 're-benchmarked in SUPERCOP' footnote, unlike the Cortex-A72 full-scheme rows; so the abstract's 1.7x/2.1x kyber768 MatrixVectorMul and the 26-41% M1 full-Kyber gains appear to compare fresh runs against figures from the earlier paper. Only the Cortex-A72 full-scheme rows are same-harness.
- Prior work has moved: Nguyen-Gaj's PQC_NEON README now lists Kyber NTT 1,162 and inverse NTT 1,320 cycles and Kyber512 keypair 68,919 on Cortex-A72, against 1 200 / 1 338 / 62 459 here (the paper notes Nguyen-Gaj counts omit a final reduction), so the remaining lead is in matrix-vector multiplication, not the bare NTT.
- Harness details: the M1 harness averages one counter pair around 1 000 000-iteration loops, signs 32-byte messages (MLEN 32) where the paper says 59-byte, and adds polyveck_reduce to its MatrixVectorMul timing, which the Cortex-A72 speed.c does not; both harnesses time kernels on uninitialised stack arrays (harmless for constant-time kernels). Full-scheme Dilithium gains also mix in faster Keccak (Neon two-way on A72, SHA-3 instructions on M1) against reference fips202.c, and the paper does not separate the two.
- HEAD is not the measured code: 2024 commits switched Kyber to 16-bit subtractive Montgomery and Barrett variants, rewrote constants and macros and added PQClean namespacing; reproduce from a96c17d (which already contains the x29 frame-pointer fix from PQClean issue #431). Cortex-A72 cycle counting needs the bundled enable_ccr kernel module ('Illegal instruction' otherwise), and the M1 counters need sudo.

## Known shortcomings

- The Dilithium baseline is unoptimised reference C, Kyber/Saber gains are only 1.1-2.1x over the Nguyen-Gaj Neon code, full-scheme gains include a faster Keccak, and the repo has no harness for the reference microbenchmark rows (reproduce at commit a96c17d). Licence MIT OR CC0-1.0.
- Cross-run comparisons behind the Kyber and Saber headlines: the paper's Table 5 Cortex-A72 Nguyen-Gaj rows are round hundreds (19 300, 71 300) and the Table 6 Apple M1 Nguyen-Gaj rows (23 000, 36 300) lack the 're-benchmarked in SUPERCOP' footnote, so the abstract's 1.7x/2.1x kyber768 MatrixVectorMul and the 26-41% M1 full-Kyber gains appear to compare fresh runs against the earlier paper's figures; only the Cortex-A72 full-scheme rows are same-harness, and the Dilithium-vs-reference A72 rows are sound. Nguyen-Gaj's PQC_NEON README now lists Kyber NTT 1,162 and inverse NTT 1,320 cycles on the A72 against 1 200 and 1 338 here. The M1 harness signs 32-byte messages where the paper says 59; the harnesses run on uninitialised arrays (harmless). HEAD commit fb2e067 says 'Saber not working now' with no later fix; reproduce from a96c17d (already has the x29 fix from PQClean #431).

## Caveats and trade-offs

The Dilithium baseline is the unoptimised portable reference code, so the 4-8x kernel gains largely measure hand vectorisation against scalar C; the Kyber and Saber comparisons are against another Neon implementation (Nguyen-Gaj, intrinsics), where gains are roughly 1.1-2.1x. The paper notes the Nguyen-Gaj NTT cycle counts omit the final reduction. Cortex-A72 numbers are medians (10 000 runs; 100 000 for full Dilithium), Apple M1 numbers are averages (10 000 runs; 1 000 000 for full Dilithium). Full-scheme ratios mix NTT and hashing gains: the optimised builds use a two-way Neon SHA-3/SHAKE (Nguyen et al.) on Cortex-A72 and Westerbaan's Keccak with the M1's SHA-3 instructions, and the paper does not separate the two effects. The repository's microbenchmarks and m1_benchmarks harnesses time only the optimised code; the reference rows of Tables 4-5 have no harness in the repo, while Table 6 reference rows can be reproduced through SUPERCOP 20210604 (README steps, first okcompilers line only). The microbenchmark Makefile builds with gcc -O3 -fomit-frame-pointer -march=native -mcpu=native. The repository was updated after publication (last commit 2024-11-10, PQClean namespacing and new compressions); the README says to use commit a96c17dbe74ac7675c785a728396e216555c432b to reproduce the paper. The LICENSE file offers MIT or CC0 1.0, and files without a header are CC0; vendored third-party files keep their own licences (Kyber and Dilithium reference code CC0 or Apache-2.0, Nguyen-Gaj Neon Kyber Apache-2.0 or public domain, feat.S MIT). CC0 has no patent grant. Cycle counts were read from the paper PDF (copy on the author's github.io repository), not re-run. The hand-written files are the __asm_NTT.S, __asm_iNTT.S, __asm_base_mul.S and __asm_poly.S sources in each scheme's ntt directory. [retier] The Dilithium baseline is the unoptimised portable reference code, so the 4-8x kernel gains largely measure hand vectorisation against scalar C, and the full-scheme ratios mix NTT gains with faster Keccak (two-way Neon SHA-3 on Cortex-A72, SHA-3 instructions on M1) against reference fips202.c. Cross-run comparisons behind the Kyber and Saber headlines: Table 5's Cortex-A72 Nguyen-Gaj rows are round hundreds (kyber768 MatrixVectorMul 19 300, saber 71 300) and Table 6's Apple M1 Nguyen-Gaj rows (23 000, 36 300, 51 300) carry no 're-benchmarked in SUPERCOP' footnote, unlike the Cortex-A72 full-scheme rows, so the abstract's 1.7x/2.1x kyber768 MatrixVectorMul and the 26-41% M1 full-Kyber gains appear to compare fresh runs against the earlier paper's figures; only the Cortex-A72 full-scheme rows are same-harness. Nguyen-Gaj's PQC_NEON README now lists Kyber NTT 1,162 and inverse NTT 1,320 cycles and Kyber512 keypair 68,919 on Cortex-A72 against 1 200 / 1 338 / 62 459 here (their counts omit a final reduction), so the remaining lead is in matrix-vector multiplication, not the bare NTT. Cortex-A72 numbers are medians (10 000 runs; 100 000 for full Dilithium), Apple M1 numbers are averages; the M1 harness signs 32-byte messages (the paper says 59) and adds polyveck_reduce to its MatrixVectorMul timing, which the Cortex-A72 speed.c does not; both harnesses time kernels on uninitialised stack arrays (harmless for constant-time kernels). HEAD is not the measured code: 2024 commits switched Kyber to 16-bit subtractive Montgomery and Barrett variants and added PQClean namespacing, and commit fb2e067 says 'Saber not working now' with no later fix; reproduce from a96c17d (which already carries the x29 frame-pointer fix from PQClean issue #431). Cortex-A72 cycle counting needs the bundled enable_ccr kernel module; M1 counters need sudo.

Armv8-A (aarch64) only, tuned for Cortex-A72 and Apple M1. The benchmark harness is only tested on Cortex-A72; user-mode cycle-counter access needs a kernel module there and root on the M1. The speedups combine new algorithms (Barrett multiplication, asymmetric multiplication, interleaved butterflies) with hand-written assembly, so they are not a pure assembly-versus-compiler comparison. Bundled third-party code is CC0, Apache-2.0, MIT or public domain.

## Maintenance

Stale research artifact (last commit 2024-11-10, 34 stars, all 5 issues closed), MIT or CC0 and easy to vendor per scheme; reproduce from commit a96c17d, treat the Kyber/Saber-versus-Nguyen-Gaj MatrixVectorMul and M1 full-scheme gains as cross-paper comparisons, and prefer a maintained FIPS 203/204 implementation in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** TCHES 2022 paper (author's PDF copy) with a public artifact repo: microbenchmark harness dilithium3/microbenchmarks/speed.c (PMU cycle counter, gcc 10.3.0 -O3), m1_benchmarks/dilithium_speed.c (Apple clang 12.0.5 -O3) and full-scheme runs through public SUPERCOP 20210604, on a Raspberry Pi 4 (Cortex-A72 at 1.5 GHz) and an Apple M1 Mac mini; every claimed number matches Tables 4, 5 and 6 and the paper's prose. Reference rows of Tables 4-5 have no harness in the repo, but Table 6 reference rows are reproducible through SUPERCOP.
- **Verifier notes:** All Dilithium ratios (4.15x, 4.12x, 5.98x, 5.15x, 8.6x, 1.44x, 2.12x, 1.63x) and the Kyber/Saber statements (1.7x, 2.1x, 9-14%, 26-41%, 2.0x) check out against the paper. Shortcomings to record: baseline is unoptimised reference C for Dilithium, Kyber/Saber gains only 1.1-2.1x over prior Neon code, full-scheme gains include faster Keccak, reference microbenchmark rows have no harness in the repo, repo changed after the paper (pinned commit a96c17d). Licence corrected to MIT OR CC0-1.0 per the current LICENSE file. Not a duplicate (pqm4 and PQRV in wave 13 target Cortex-M4 and RISC-V).
- **Fields the verifier corrected:** `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-115 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vincentvbh/vincentvbh.github.io/master/papers/2021-986.pdf>
  - <https://github.com/neon-ntt/neon-ntt>
  - <https://github.com/neon-ntt/neon-ntt/commits>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/HEAD/README.md>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/microbenchmarks/Makefile>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/microbenchmarks/speed.c>
  - <https://github.com/neon-ntt/neon-ntt/tree/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3>
  - <https://github.com/neon-ntt/neon-ntt/tree/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/m1_benchmarks>
- **Sources the enricher read:**
  - <https://github.com/neon-ntt/neon-ntt>
  - <https://github.com/neon-ntt/neon-ntt/commits>
  - <https://github.com/neon-ntt/neon-ntt/commits/master?since=2024-10-12&until=2024-10-13>
  - <https://github.com/neon-ntt/neon-ntt/commit/fb2e067>
  - <https://github.com/neon-ntt/neon-ntt/commit/a96c17dbe74ac7675c785a728396e216555c432b>
  - <https://github.com/neon-ntt/neon-ntt/issues?q=is%3Aissue>
  - <https://github.com/neon-ntt/neon-ntt/issues/1>
  - <https://github.com/neon-ntt/neon-ntt/issues/2>
  - <https://github.com/neon-ntt/neon-ntt/issues/5>
  - <https://github.com/PQClean/PQClean/issues/431>
  - <https://github.com/neon-ntt/neon-ntt/tree/a96c17dbe74ac7675c785a728396e216555c432b/lightsaber/ntt>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/HEAD/README.md>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/microbenchmarks/Makefile>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/microbenchmarks/speed.c>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium3/microbenchmarks/hal.c>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium2/m1_benchmarks/Makefile>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/dilithium2/m1_benchmarks/dilithium_speed.c>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/saber/ntt/__asm_mul.S>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/a96c17dbe74ac7675c785a728396e216555c432b/saber/ntt/macros_common.i>
  - <https://raw.githubusercontent.com/neon-ntt/neon-ntt/HEAD/saber/ntt/__asm_mul.S>
  - <https://raw.githubusercontent.com/vincentvbh/vincentvbh.github.io/master/papers/2021-986.pdf>
  - <https://github.com/GMUCERG/PQC_NEON>
  - <https://github.com/pq-code-package/mlkem-native>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/neon-ntt/neon-ntt`) · [data/wave13/enrich/raw/github_com_neon_ntt_neon_ntt.json](../../../data/wave13/enrich/raw/github_com_neon_ntt_neon_ntt.json) (enrichment confidence 0.85)

</details>
