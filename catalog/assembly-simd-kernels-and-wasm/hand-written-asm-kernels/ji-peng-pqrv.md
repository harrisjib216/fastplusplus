# PQRV (Keccak, Kyber, Dilithium on RV{32,64}IM{B}{V})

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `RISC-V assembly / C` · `MIT` · 🟡 stale

> RISC-V assembly Keccak, Kyber and Dilithium for RV32/RV64 with B and V; 2-5x fewer cycles than pq-crystals reference C.

| | |
|---|---|
| **Beats** | pq-crystals reference C for Kyber (ref, commit 441c051) and Dilithium (ref, commit f1f8085) and PQClean fips202.c for Keccak (commit 05df469), compiled with the XuanTie GCC 10.4.0 at -O3 on the same core |
| **Claimed result** | Table 4 (k cycles): Kyber768 KeyGen ref RV64IM 742k vs ours RV64IM 278k (2.7x, derived from page data) and ours RV64IMBV 165k (4.5x vs ref RV64IM, or 3.7x vs ref RV64IMB 603k; derived from page data); ref RV32IM 1222k vs ours RV32IM 496k and RV32IMBV 284k. Dilithium3 Sign ref RV64IM 8232k vs ours RV64IM 3333k and RV64IMBV 2139k; ref RV32IM 13671k vs ours RV32IM 5069k and RV32IMBV 3054k. Table 2 Keccak-f1600 cycles: C ref RV64I 4926 vs ours 2591, RV64IB 2412 vs 1770, RV32I 15779 vs 7808, RV32IB 12341 vs 6222. Text: RV64I 90% faster, RV64IB 36% faster, RV32I twice as fast and RV32IB 98% faster than the C reference; Kyber/Dilithium 'often achieve speedups of nearly 2x or more' over the reference C on the same architecture. |
| **Workload** | Keccak-f1600/SHAKE, Kyber768 KeyGen/Encaps/Decaps and Dilithium3 KeyGen/Sign/Verify on a XuanTie C908 core, RV32/RV64 with and without B (bit-manip) and V (vector) extensions. |
| **Metric** | latency (CPU cycles) |
| **Hardware** | CanMV-K230 board, XuanTie C908 core (RV{32,64}GCBV, VLEN=128, 1.6 GHz, dual-issue in-order); repo also supports SpacemiT X60 (VLEN=256) |
| **Compiler and flags** | Xuantie-900 linux-5.10.4 glibc GCC toolchain V2.8.0 (GCC 10.4.0); ches2025 Makefiles use -O3 -fomit-frame-pointer -static with -march=rv32imac/rv64imac plus _zbb/_zba_zbb and v variants (-mabi=ilp32/lp64) for both the reference C and the optimized builds; the paper itself states only -O3, -static comes from the README and Makefiles |
| **Adoption** | 15 stars; artifact of a TCHES 2025 paper |
| **Last commit** | 2025-07-15 |
| **Links** | [repository](https://github.com/Ji-Peng/PQRV) · [benchmark](https://raw.githubusercontent.com/Ji-Peng/Ji-Peng.github.io/HEAD/uploads/tches2025/paper.pdf) |

## Verdict

On a 1.6 GHz XuanTie C908 (CanMV-K230), with everything built by the Xuantie GCC 10.4.0 toolchain at -O3 -fomit-frame-pointer -static and timed with rdcycle (median of 10,000 runs; Dilithium Sign averaged), the assembly takes Keccak-f1600 from 4926 to 2591 cycles on RV64I and from 2412 to 1770 on RV64IB versus PQClean fips202.c, and Kyber768 KeyGen from 742k (pq-crystals ref, RV64IM) to 278k (RV64IM) and 165k (RV64IMBV); I re-read the result .txt files on the ches2025 branch and they match the paper's Tables 2 and 4.

## Use it when

- Kyber/ML-KEM or Dilithium on an in-order dual-issue RISC-V core such as XuanTie C908 (CanMV-K230) or SpacemiT X60, where the paper shows Kyber768 KeyGen 742k to 278k cycles on RV64IM and 165k with B+V.
- SHA-3/SHAKE on RV32I or RV64I without the B extension: the scalar Keccak-f1600 is 1.9x (RV64I, 4926 to 2591 cycles) and 2.0x (RV32I, 15779 to 7808) faster than PQClean's fips202.c.
- As a source of RISC-V kernels to port into a maintained library; leancrypto already pulled its RV64 ML-KEM/Keccak code (issues #1 and #2).
- Studying how to schedule crypto kernels for dual-issue in-order RISC-V cores; the cpi/ directory holds measured instruction latencies for the C908.

## Skip it when

- ML-DSA: the Dilithium code (checked in main's Dilithium/RV64: CRHBYTES 64, no context string) is round-3 Dilithium, not FIPS 204 ML-DSA, so its signatures do not interoperate with ML-DSA; only the main branch's Kyber was updated toward FIPS 203.
- RVV on cores whose VLEN is not 128 (or 256 on main for the Kyber NTT): index tables and coefficient layouts are hard-coded for VLEN=128, and the ches2025 branch has no runtime VLEN detection.
- Fast Keccak via vectors on RV64: on C908 the pure RVV Keccak costs 4827 cycles per state against 1770 for the scalar RV64IB assembly, and the RV64 hybrid variants never beat scalar (best about 1980 per state), so the Kyber/Dilithium RV64 V builds keep scalar Keccak.
- Production use without a side-channel review: the scalar C wrappers keep the pre-KyberSlash division by KYBER_Q in poly_tomsg and poly_compress (see gotchas), and there is no ct-verification tooling in the repo.
- Out-of-order or wider RISC-V cores: the scheduling targets dual-issue in-order pipelines and gains elsewhere are not measured.

## How it is fast

Keccak uses lane complementing, a one-round in-place state layout and instruction scheduling for the C908's dual-issue in-order pipeline (CPI about 0.51-0.52 vs 0.57-0.64 for compiled C); RV32IB adds bit interleaving and RV32 with V adds hybrid scalar/vector multi-way Keccak (3-5 states). NTTs use Plantard (scalar) or Montgomery (RVV) reductions with merged layers and no extra modular reduction, plus cached base multiplication; rej_uniform, cbd2/cbd3 and rej_eta are vectorized with vrgather index tables built for VLEN=128.

## Compared with alternatives

Pick PQRV when the target is RISC-V; neon-ntt (Armv8 Neon) and pqm4 (Cortex-M4) cover the same Kyber/Dilithium kernels on ARM, and pqm4 is maintained and already tracks ML-KEM/ML-DSA, so prefer it, or leancrypto's RISC-V port, wherever a FIPS-aligned maintained library matters more than raw cycles.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond a RISC-V cross toolchain; measured with the Xuantie-900 GCC 10.4.0 toolchain V2.8.0; main also has Makefile_x60 files for the SpacemiT board |
| **Minimum toolchain** | GCC with RVV 1.0 and Zba/Zbb assembler support (paper used Xuantie GCC 10.4.0; leancrypto's port built it with a distro toolchain using -march=rv64imadcv per issue #2) |
| **Platforms** | RISC-V only: RV32IM{B}{V} and RV64IM{B}{V}; V variants need RVV 1.0 with VLEN=128 (main adds VLEN=256 Kyber NTT for SpacemiT X60) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the KEM and signature entry points keep the pq-crystals NIST API and test vectors match the reference (make run_diff_vectors), but you must pick per-ISA source sets from the Makefiles and Dilithium is round 3, not ML-DSA |

## Gotchas

- KyberSlash pattern still present: Kyber/RV64, RV32 and ref poly.c on both ches2025 and main compute t = (((t &lt;&lt; 1) + KYBER_Q/2)/KYBER_Q) & 1 in poly_tomsg (decapsulation, secret-dependent) and divide by KYBER_Q in poly_compress, while upstream pq-crystals/kyber ref/poly.c now uses multiply-and-shift (t \*= 80635; t &gt;&gt;= 28). GCC at -O3 usually lowers a constant division to a multiply, so the measured numbers are likely unaffected, but -Os or other compilers can emit a variable-time div; the paper's statement that it avoids secret-dependent timing does not cover these C paths.
- Headline ratios mix ISAs: the 4.5x KeyGen figure compares the RV64IMBV build against reference C built for plain RV64IM. The harness also builds the reference with -march=rv64imacv_zba_zbb (Kyber/ref/results_rv64imbv.txt): same-ISA Kyber768 ratios are 3.7x KeyGen (615,950 to 164,706), 4.2x Encaps and 4.9x Decaps; compiler-only V actually slows the reference about 5% (RV64IMV ref KeyGen 779,568 vs RV64IM 742,535).
- Two branches: numbers reproduce only from ches2025, whose Makefiles hard-code the board at 192.168.123.99 (root, /sharefs), build with -static and scp/ssh the binaries; main has refactored RVV NTTs, X60 support and FIPS 203 changes and no matching result files for the paper.
- Issue #1 (stack smash in polyvec_basemul_acc_montgomery) was a missing ret in leancrypto's copy, not in PQRV; both PQRV branches end every function in ntt_dualissue_plant_rv64im.S with ret. Issue #2 showed the RVV Keccak gives no gain on SpacemiT X60 either (author's 4-way figures: RVV 2415, RV64IM 2580, RV64IMB 1819 cycles).

## Known shortcomings

- TCHES 2025 Tables 2/4 match (ches2025 Makefiles: -O3 -fomit-frame-pointer -static -march) but the 4.5x headline mixes RV64IMBV against an RV64IM reference; same-ISA gains are 2.7x/3.7x; single C908 core. Stale (last commit 2025-07-15).
- Harness clean (rdcycle, median of 10000, same GCC 10.4 -O3 -static both sides; ches2025 result files match paper Tables 2 and 4). Headline 4.5x KeyGen mixes ISAs; same-ISA Kyber768 ratios against ref built with V and B flags (Kyber/ref/results_rv64imbv.txt) are 3.7x KeyGen, 4.2x Encaps, 4.9x Decaps, and the plain V flag slows ref 5%. KyberSlash-style division by KYBER_Q remains in poly_tomsg and poly_compress on both branches (upstream pq-crystals now uses multiply-shift); at -O3 GCC lowers it to a multiply, so numbers stand. Dilithium is round 3, not ML-DSA. RVV Keccak is slower than scalar RV64IB (4827 vs 1770 cycles per state), as the paper admits. Issue #1 stack smash was in leancrypto's copy, not PQRV.

## Caveats and trade-offs

Reference C numbers depend on the compiler exploiting B-extension rotates (the paper's RV64IB Keccak assembly is only 36% faster than the C reference, versus 90% on RV64I, because the compiler uses rotate and andn). The headline 4.5x KeyGen ratio compares the optimized RV64IMBV build with the reference built for plain RV64IM; same-ISA gains are smaller (2.7x RV64IM, 3.7x RV64IMB versus RV64IMBV). The RV32IB Keccak comparison is called 'slightly unfair' by the authors (bit interleaving). Paper comparisons with Cortex-A55/A72 NEON and Cortex-M4 are labelled 'unfair, for reference only'. The repo's main branch has been updated beyond the paper (refactored NTT RVV, SpacemiT X60 support, FIPS 203 alignment); reproduce from the ches2025 branch, whose Makefiles hard-code a board IP and require -static builds. Medians over 10000 iterations except Dilithium Sign (average). Results are for a single in-order dual-issue core (C908, VLEN=128); the vector code targets VLEN=128. MIT overall, reusing public-domain pq-crystals code and Apache-2.0 code from UIC-ESLAS/Kyber_RV_M3. The paper PDF was read through a raw.githubusercontent.com mirror of the author's site.

Hand-written assembly per ISA variant (the sha3 directory alone has 49 .S files); tuned for dual-issue in-order RISC-V cores (C908, X60) and specific extensions B and V; RVV code assumes VLEN of 128 or 256; not portable and not a drop-in library API (derived from pq-crystals code). Constant-time claims are the authors'.

## Maintenance

Research artifact with 15 stars and 2 closed issues; last commit 2025-07-15 (C908 CPI table updates), so stale, but MIT-licensed (reusing public-domain pq-crystals code) and already adopted by leancrypto, which is the better route to a maintained build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** TCHES 2025 paper (Tables 2 and 4) compares against the pq-crystals Kyber/Dilithium ref C (commits 441c051, f1f8085) and PQClean fips202.c (05df469) built with the same Xuantie GCC 10.4.0 toolchain at -O3 on a stated CPU (XuanTie C908 on CanMV-K230, 1.6 GHz); the harness is public on the ches2025 branch (Kyber/ref/Makefile and Kyber/RV64/Makefile 'make speed', sha3/Makefile, common/cpucycles.c) with full flags (-O3 -fomit-frame-pointer -static -march=rv64imac[_zba_zbb][v]) and result .txt files that match the paper.
- **Verifier notes:** All Table 2 and Table 4 numbers in the record match the paper; sha3/results_ko_rv32im.txt on ches2025 reproduces the 8734-cycle [Sto19] row. Only fix: last commit 2025-07-15 is about 15 months old, so maintenance is stale, not active. Shortcomings: cross-ISA headline ratio (4.5x mixes RV64IMBV against RV64IM ref), single C908 core, main branch diverged from the paper.
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Ji-Peng/Ji-Peng.github.io/HEAD/uploads/tches2025/paper.pdf>
  - <https://github.com/Ji-Peng/PQRV>
  - <https://github.com/Ji-Peng/PQRV/commits>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/LICENSE>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV64/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/ntt/speed_ntt.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_ko_rv32im.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/cpucycles.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/README.md>
  - <https://github.com/Ji-Peng/PQRV/tree/ches2025>
  - <https://github.com/Ji-Peng/PQRV/tree/ches2025/Kyber/RV64>
  - <https://github.com/Ji-Peng/PQRV/tree/ches2025/sha3>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV64/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/cpucycles.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/cpucycles.h>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/test_speed_kyber.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/speed_print.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/speed_print.h>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/common/randombytes.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/results_rv64im.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/results_rv64imb.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/results_rv64imv.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/results_rv64imbv.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV64/results_rv64im.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV64/results_rv64imbv.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/Makefile>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/test_sha3.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/fips202.h>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64im.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64im_ref.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64imb.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64imb_ref.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64imbv.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv64imv.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv32im.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/sha3/results_rv32im_ref.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV64/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/RV32/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/Kyber/ref/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Kyber/RV64/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Kyber/RV32/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Kyber/ref/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Kyber/RV64/kem.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Dilithium/RV64/sign.c>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/Dilithium/RV64/params.h>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/ches2025/ntt/kyber/ntt_dualissue_plant_rv64im.S>
  - <https://raw.githubusercontent.com/Ji-Peng/PQRV/main/ntt/kyber/ntt_dualissue_plant_rv64im.S>
  - <https://raw.githubusercontent.com/pq-crystals/kyber/main/ref/poly.c>
  - <https://raw.githubusercontent.com/Ji-Peng/Ji-Peng.github.io/HEAD/uploads/tches2025/paper.pdf>
  - <https://github.com/Ji-Peng/PQRV/issues?q=is%3Aissue>
  - <https://github.com/Ji-Peng/PQRV/issues/1>
  - <https://github.com/Ji-Peng/PQRV/issues/2>
  - <https://github.com/Ji-Peng/PQRV/commits/main>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ji-peng/pqrv`) · [data/wave13/enrich/raw/github_com_ji_peng_pqrv.json](../../../data/wave13/enrich/raw/github_com_ji_peng_pqrv.json) (enrichment confidence 0.85)

</details>
