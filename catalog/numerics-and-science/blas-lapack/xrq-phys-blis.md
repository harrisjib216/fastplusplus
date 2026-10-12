# GEMMFIP (BLIS fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> Research BLIS fork whose DGEMM fuses packing into the first compute pass; paper plots show it ahead of OpenBLAS/ArmPL on medium sizes.

| | |
|---|---|
| **Beats** | OpenBLAS, AMD BLIS/AOCL, ArmPL, Intel MKL |
| **Claimed result** | Qualitative only (plots): outperforms OpenBLAS and conventional BLIS on Epyc 7R32 and matches AOCL there; highest throughput and consistency of all tested libraries on Graviton 3 (vs ArmPL, OpenBLAS); only MKL on Xeon E5-2690 beats it. No numeric ratios on page. |
| **Workload** | Single-core DGEMM, medium sizes (m=n=k \~100-400) on x86_64 and Arm |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2690, AMD Epyc 7R32, AWS Graviton 2/3, Apple M2 |
| **Compiler and flags** | GCC 10.2 (Xeon), GCC 11.3 (Epyc), Clang 14.0 (Graviton), Apple Clang 14.0 (M2); other flags unstated |
| **Adoption** | 1 star |
| **Last commit** | 2023-04-26 |
| **Links** | [repository](https://github.com/xrq-phys/blis) · [benchmark](https://arxiv.org/pdf/2302.08417) |

## Verdict

The authors' paper (arXiv 2302.08417, later published as 'Towards a Unified Implementation of GEMM in BLIS', ICS '23, pp. 111-121) compares single-core DGEMM against OpenBLAS, AMD BLIS/AOCL, ArmPL and MKL on Xeon E5-2690, Epyc 7R32, Graviton 2/3 and Apple M2 (GCC 10.2/11.3, Clang 14, Apple Clang 14; other flags unstated), and its plots show it beating OpenBLAS and conventional BLIS on Epyc, matching AOCL, leading on Graviton 3, and trailing MKL on Xeon. No numeric ratios are given; I could not open the paper itself in this session (arXiv and ACM blocked) and relied on the verified record plus search-result metadata.

## Use it when

- Single-threaded DGEMM at medium sizes (roughly m=n=k 100-400) where neither the small-matrix nor the large-matrix path of a stock BLAS is at its best
- AWS Graviton 2/3 or other ARMv8-A NEON servers where the paper reports it ahead of ArmPL and OpenBLAS in single-core DGEMM
- AMD Epyc (Zen 2 class) single-core DGEMM, where the paper reports it beating OpenBLAS and conventional BLIS and matching AMD's BLIS/AOCL
- Research or prototyping of fused packing / unified small-large GEMM strategies inside the BLIS framework

## Skip it when

- Single precision, complex, or mixed-datatype GEMM: the sandbox handles only dgemm and falls back to stock BLIS for everything else
- Multithreaded GEMM: only the JR loop is parallelised; threads assigned to the JC/PC/IC/packing loops return immediately and the master thread does their work (source comment: 'Limited threading capability')
- Intel Xeon with MKL available: the paper reports MKL ahead of it on the Xeon E5-2690
- Production use: research fork with 1 star, no releases, last commit 2023-04-26, based on pre-1.0 BLIS; the gemmfip sandbox does not appear in upstream flame/blis's sandbox directory
- General-stride operands (neither A column-stored nor B row-stored): the fused path is skipped and stock BLIS runs

## How it is fast

Fused-in packing (FIP): the GEMMSUP-style millikernel reads A and B directly from the caller's unpacked memory and, while computing the first micro-tile pass, writes the panels it touched into BLIS's packing buffers, so later passes over the same block reuse packed data without a separate memcpy-like packing stage. Whether A and B are packed at all is decided by size thresholds (BLIS_MT/NT/KT block sizes), so small problems never pay for packing and large ones still get contiguous, prefetch-friendly panels. Kernels are hand-written inline assembly: a 6x8 AVX2/FMA millikernel (reusing BLIS's Haswell 6x8 microkernel for fully packed large-k cases) and 8x6 NEON millikernels for ARMv8-A with explicit prefetch; small-m problems are transposed into small-n ones.

## Compared with alternatives

Pick it over BLASFEO or LibShalom when you want a standard BLAS dgemm interface that stays fast across small, medium and large sizes on Arm or AMD rather than a small-matrix specialist; for very small matrices BLASFEO/LibShalom/IAAT report larger gains, and for anything beyond single-thread double precision a maintained BLAS (or Eigen) is the safer choice.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (a BLIS build with the gemmfip sandbox compiled in) |
| **Dependencies** | none beyond a C99 compiler and BLIS's configure/make build; optional OpenMP/pthreads for threading |
| **Minimum toolchain** | C99 with GNU extensions (sandbox uses typeof and GNU inline asm), i.e. GCC or Clang; paper used GCC 10.2/11.3, Clang 14 and Apple Clang 14 |
| **Platforms** | x86-64 with AVX2+FMA (Haswell kernel set) and AArch64 NEON (ARMv8-A kernels, incl. Apple M-series and Graviton); other ISAs get a plain-C reference millikernel |
| **Thread safety** | Not documented for the sandbox; inherits BLIS's reentrant design, but intra-GEMM threading is JR-loop only |
| **Drop-in for the baseline** | partial — exposes the full BLIS/BLAS API so dgemm_ users can relink, but only dgemm takes the new path and it is a source build of a research fork, not a packaged library |

## Gotchas

- GEMMFIP is off unless you configure with -s gemmfip; the README is the stock BLIS README and never mentions the sandbox (only sandbox/gemmfip/README.md does)
- Setting BLIS_JC_NT/BLIS_IC_NT (or letting BLIS auto-factor threads into those loops) wastes threads: non-master workers in those loops exit and the master computes their share
- Source reading: the x86 edge kernels for n=7 and n=3 load a full 8- or 4-wide row of unpacked B, reading one double past the row end (results are masked off, but it can touch memory past the last row of B), and an in-code TODO notes packed-B padding columns are left undefined
- In non-DEBUG builds the millikernel dispatch silently does nothing for an unexpected (pack_a, n) combination instead of failing; correctness depends on caller invariants in bls_dgemm

## Known shortcomings

- Only source is an arXiv preprint by the fork's author (not peer reviewed); flags unstated; results plots only, no numbers; MKL still beats it on Xeon; fork of BLIS.
- Double precision only; threading is JR-loop only (non-master JC/IC threads exit and the master does their share); x86 edge kernels for n=7 and n=3 read one double past the unpacked B row (out-of-bounds read, result masked off); release-build dispatch default silently skips the tile; fork stale and not merged upstream.

## Caveats and trade-offs

Evidence is an arXiv preprint (not peer-reviewed as far as found) by the fork's author; compiler flags unstated; no numeric ratios; MKL not beaten on Intel; fork with 1 star; GEMMFIP lives on the 'gemmfip' branch and is enabled with ./configure -s gemmfip; README does not document it. [retier] Peer-reviewed at ICS '23 (DOI 10.1145/3577193.3593707); comparison is in plots only, flags unstated.

Fork of BLIS with unified packing/skinny-GEMM (gemmfip branch); single-core evaluation only

## Maintenance

Stale research fork (last commit 2023-04-26, 1 star) under BSD-3-Clause; the sandbox is a few C/asm files that could be ported to current BLIS, but expect to own the maintenance yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** arXiv:2302.08417 is a preprint by the fork's own author (with BLIS maintainers); no peer-reviewed venue found, and compiler flags are unstated, so it is first-party evidence with partial methodology. It compares against OpenBLAS, MKL, AOCL and ArmPL with plots only, no numeric ratios.
- **Retiered** C to B: Enrichment found arXiv 2302.08417 published at ICS '23 ('Towards a Unified Implementation of GEMM in BLIS', DOI 10.1145/3577193.3593707, pp. 111-121), a peer-reviewed venue; the verifier's B-to-C downgrade assumed no venue. Plots only and flags unstated, so B, not A.
- **Verifier notes:** Record called the paper peer-reviewed (ACM); I found only the arXiv preprint (v2) and a BLIS Retreat 2023 talk. Last commit date 2023-04-26 not verified (GitHub commits page blocked by robots.txt). License BSD-3-Clause and fork-of flame/blis confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2302.08417>
  - <https://github.com/xrq-phys/blis>
- **Sources the enricher read:**
  - <https://github.com/xrq-phys/blis>
  - <https://github.com/xrq-phys/blis/commits/gemmfip>
  - <https://github.com/xrq-phys/blis/tree/gemmfip/sandbox>
  - <https://github.com/xrq-phys/blis/tree/gemmfip/sandbox/gemmfip>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/README.md>
  - <https://raw.githubusercontent.com/xrq-phys/blis/master/README.md>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/README.md>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_sandbox.h>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemm_ex.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bls_dgemm.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemmsup2_dref.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemmsup2_rv_haswell_asm_d6x8m.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemmsup2_rv_haswell_asm_d6x8n.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemmsup2_rv_armv8a_asm_d8x6m.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/sandbox/gemmfip/bli_gemmsup2_cv_armv8a_asm_d8x6m.c>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/configure>
  - <https://raw.githubusercontent.com/xrq-phys/blis/gemmfip/CHANGELOG>
  - <https://github.com/flame/blis/tree/master/sandbox>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/xrq-phys/blis`) · [data/wave8/enrich/raw/github_com_xrq_phys_blis.json](../../../data/wave8/enrich/raw/github_com_xrq_phys_blis.json) (enrichment confidence 0.7)

</details>
