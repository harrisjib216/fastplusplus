# IAAT (small GEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `?` · `no license` · ⚪ unknown

> Research small-GEMM framework for ARMv8 (paper only, no code) reporting 1.1-1.8x over OpenBLAS for M=N=K&lt;=80.

| | |
|---|---|
| **Beats** | OpenBLAS 0.3.13, ARMPL 21.0, BLIS 0.8.1 |
| **Claimed result** | SGEMM_NN (M=N=K&lt;=80): on average 1.81x, 2.3x and 20.17x faster than OpenBLAS, ARMPL and BLIS respectively; DGEMM up to 1.48x vs OpenBLAS, 1.66x vs ARMPL, 15.0x vs BLIS; CGEMM/ZGEMM 9.6-13.68x vs BLIS |
| **Workload** | SGEMM/DGEMM/CGEMM/ZGEMM with M=N=K&lt;=80 on Kunpeng920 |
| **Metric** | throughput |
| **Hardware** | Kunpeng920 2.6 GHz |
| **Compiler and flags** | GCC 7.5; flags unstated |
| **Links** | [benchmark](https://arxiv.org/pdf/2208.09822) |

## Verdict

Measured single-threaded on a Kunpeng920 at 2.6 GHz with GCC 7.5 (flags not given). Average speedups for M=N=K&lt;=80 were SGEMM_NN 1.81x over OpenBLAS 0.3.13, 2.30x over ArmPL 21.0 and 20.17x over BLIS 0.8.1; DGEMM_NN 1.48x over OpenBLAS; ZGEMM about 1.1x over OpenBLAS.

## Use it when

- As a design reference for packing-free, size-specialised small-GEMM kernels on ARMv8/NEON
- Workloads that repeat GEMMs of the same small shape (the paper says this is the case it fits), e.g. M=N=K up to about 64 in fp32/fp64/complex
- Comparing against your own Kunpeng-class aarch64 small-GEMM results when OpenBLAS or ArmPL small-size performance falls short

## Skip it when

- Any production use: no code, binary or license has been released
- Matrices above about 80 (or 32 for TN), where the paper's gains flatten and normal packed BLAS wins
- x86, SVE or SME targets: the kernels are written for 128-bit ARMv8 NEON only
- Multi-threaded GEMM: only single-threaded results are reported
- TN transpose: it cannot be vectorised well, so its kernels are smaller and gains are lower

## How it is fast

It does no packing: every block size has its own generated kernel (for example SGEMM 16x{1-4}, 12x{1-6}, 8x{1-8} and 4/3/2/1 x {1-13}), so A and B are read in place. An input-aware adaptive tiling step splits C into blocks that minimise L2-to-register traffic and stay a multiple of the SIMD width, which also removes most of the per-call edge handling. The generator uses computational templates, a register allocator for the 32 128-bit NEON registers, and instruction scheduling with ping-pong buffering.

## Compared with alternatives

You cannot use IAAT itself because no code was released. For usable small GEMM on aarch64, LibShalom (ARMv8, with code) or BLASFEO (small dense linear algebra) are the shipped alternatives; read IAAT for its size-specialised kernel generation and tiling heuristic.

## Integration

| | |
|---|---|
| **Form** | not released (paper only) |
| **Dependencies** | not documented |
| **Minimum toolchain** | GCC 7.5 used in the paper; flags not stated |
| **Platforms** | aarch64 ARMv8 NEON (evaluated only on Huawei Kunpeng920) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Throughput rises and falls with size: dimensions that are multiples of 4 (fp32) or 2 (fp64) hit peak, other sizes run noticeably slower
- The 11-20x ratios over BLIS 0.8.1 reflect that BLIS lacked a small-matrix path at the time; they say little about current BLIS
- The gain over OpenBLAS shrinks with precision: about 1.8x for SGEMM, 1.3-1.5x for DGEMM/CGEMM and about 1.1x for ZGEMM

## Known shortcomings

- Paper only: no code, flags or venue; large ratios over BLIS (20.17x) come from BLIS lacking a small-matrix path at the time.
- Gains over OpenBLAS shrink with precision (SGEMM \~1.8x, DGEMM \~1.3-1.5x, CGEMM \~1.2-1.4x, ZGEMM \~1.1x); peak only at dims that are multiples of 4 (fp32)/2 (fp64); weak TN transpose; 128-bit NEON only; single-threaded.

## Caveats and trade-offs

Paper only, no code repo; flags unstated; the large ratios over BLIS reflect BLIS lacking a small-GEMM path at the time; Kunpeng920 only

ARMv8 only

## Maintenance

Research artifact only (arXiv 2208.09822, venue not stated); no repository, no license, and maintenance is not applicable, so it is listed as a reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv paper with no venue stated and no code; it gives GCC 7.5 on Kunpeng920 but no flags. That is first-party numbers with partial methodology, so C.
- **Verifier notes:** The record misread the ratios as three transpose variants versus OpenBLAS; the paper attributes 1.81x, 2.3x and 20.17x to OpenBLAS, ARMPL and BLIS respectively.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2208.09822>
  - <https://arxiv.org/pdf/2208.09822>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2208.09822>
  - <https://arxiv.org/pdf/2208.09822>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:iaat-small-gemm`) · [data/wave8/enrich/raw/paper_iaat_small_gemm.json](../../../data/wave8/enrich/raw/paper_iaat_small_gemm.json) (enrichment confidence 0.6)

</details>
