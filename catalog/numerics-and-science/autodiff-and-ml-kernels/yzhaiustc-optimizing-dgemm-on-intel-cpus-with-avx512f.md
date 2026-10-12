# Optimizing DGEMM on Intel CPUs with AVX512F

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Step-by-step AVX-512 DGEMM tutorial whose final kernel roughly matches single-threaded Intel MKL on large square matrices.

| | |
|---|---|
| **Beats** | Intel oneMKL DGEMM |
| **Claimed result** | Kernel 18 (serial) and 19 (parallel) 'reach the performance comparable to / faster than Intel MKL' on latest Intel CPUs; peak single core 128 GFLOPS (exact ratios are in plots, not quoted) |
| **Workload** | Double-precision GEMM serial and parallel, 19 stepwise kernels vs MKL at multiple matrix sizes. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon W-2255 |
| **Compiler and flags** | GCC 7.3.0, Ubuntu 18.04.5; Makefile CFLAGS: -O0 -march=skylake-avx512 -w -lpthread -fopenmp; linked against oneMKL 2021.1 beta (mkl_sequential, ILP64) |
| **Adoption** | 164 stars |
| **Last commit** | 2022-02-03 |
| **Links** | [repository](https://github.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F) · [benchmark](https://github.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F) |

## Verdict

On one Intel Xeon W-2255 core (GCC 7.3.0, -march=skylake-avx512, oneMKL 2021.1 beta sequential), the repo's plot shows kernel 18 at about 33-115 GFLOPS across square n=100..3000, behind MKL from n=200 to 1500 and about 2-8% ahead from n=1600 to 3000 (about 115 vs 110 GFLOPS at n=3000, read from the plot). No measurement of the parallel kernel 19 against MKL was found.

## Use it when

- Learning or teaching how a BLIS/Goto-style DGEMM is built on AVX-512, one optimisation at a time
- Vendoring a small, readable FP64 GEMM micro-kernel into GPL-compatible code on Skylake-X/Cascade Lake-class CPUs
- Large square column-major FP64 GEMM (about n &gt;= 1600), where kernel 18 was a few percent ahead of single-threaded MKL on a Xeon W-2255
- As a starting point for your own AVX-512 kernel tuning experiments

## Skip it when

- Small and mid-size matrices: in the repo's own plot kernel 18 trails MKL by roughly 10-20% for n=200..1500
- Any production BLAS need: only NN column-major DGEMM, no transposes, no other precisions or routines; use MKL, OpenBLAS or BLIS
- CPUs without AVX-512F (all AMD before Zen 4, most Intel client chips), or non-x86
- Closed-source or permissive-licence projects: GPL-3.0
- Multi-threaded claims: the harness links mkl_sequential and run.sh sets MKL_NUM_THREADS=1, so the parallel kernel 19 was never compared to threaded MKL

## How it is fast

Goto/BLIS-style blocking (M=192, K=384, N=8640 blocks) with packing of A and B into 4096-byte-aligned buffers, and a 24x8 register-blocked micro-kernel in AVX-512 inline asm (vbroadcastsd + vfmadd231pd on zmm registers). It adds software prefetching (prefetcht0) on A, B and C, a tuned C-scaling routine, and 'discontinuous' packing of B meant to help the L2 hardware prefetcher. Kernel 19 parallelises over M with a shared packed-B buffer and OpenMP barriers.

## Compared with alternatives

Pick it over llamafile tinyBLAS or TCL when you want FP64 GEMM on AVX-512 and readable, staged code to learn from; tinyBLAS targets FP16/BF16/quantised LLM matmuls and TCL targets tensor contractions on top of a BLAS.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP (kernel 19); Intel MKL only for the test harness and correctness reference |
| **Minimum toolchain** | GCC with AT&T inline asm and -march=skylake-avx512 (tested with GCC 7.3.0); C11 aligned_alloc |
| **Platforms** | x86-64 with AVX-512F only |
| **Thread safety** | not documented; each call allocates its own packing buffers, kernel 19 spawns its own OpenMP team |
| **Drop-in for the baseline** | partial — same argument order as column-major cblas_dgemm NN, but 32-bit int dims, no layout/transpose flags, separate function per kernel |

## Gotchas

- If alpha==0 or K==0 the function returns without applying beta to C, unlike BLAS semantics (C = beta\*C)
- Correctness check in the harness uses an absolute tolerance of 1e-2, which is loose
- Timing is 3 repetitions via gettimeofday with no warm-up; MKL's 7 GFLOPS at n=100 in the plot looks like a first-call artifact
- The Makefile builds everything at -O0; the hot path is inline asm so this matters less, but the C driver/packing code is unoptimised

## Known shortcomings

- Win over MKL appears only in plots on cs.ucr.edu (unverified size); Makefile builds own kernels at -O0 against oneMKL 2021.1 beta; abandoned (last commit 2022-02-03).
- Single core: \~10-20% slower than MKL for n=200..1500, \~2-8% faster only for n&gt;=1600 (\~115 vs 110 GFLOPS at 3000); harness links mkl_sequential with MKL_NUM_THREADS=1, so parallel kernel never measured against threaded MKL; alpha==0 or K==0 returns without scaling C by beta (breaks BLAS semantics); loose 1e-2 correctness tolerance; 3 runs, no warm-up.

## Caveats and trade-offs

Tutorial-style. The win over MKL is stated as 'comparable to / faster than', shown only in plots (hosted on cs.ucr.edu, not readable here), on one CPU (Xeon W-2255) against a oneMKL 2021.1 beta. The project's own kernels are built at -O0 (they are intrinsics/inline asm, so -O0 matters less); MKL is the prebuilt sequential library. Kernel sources are linked from cs.ucr.edu. Baseline is MKL, not oneDNN. Last commit Feb 2022 (&gt;3 years).

AVX512F only, DGEMM only, inline assembly; GPL-3.0.

## Maintenance

Abandoned since February 2022 and tutorial code, but GPL-3.0 and small (one \~670-line header per kernel), so it can be vendored by GPL projects; last tested compiler GCC 7.3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README benchmarks kernels 1-19 against Intel MKL (kernel 0 in the same binary); code is public (repo .c files plus kernel headers), compiler GCC 7.3.0, flags in Makefile (-O0 -march=skylake-avx512 -fopenmp) and CPU Xeon W-2255 are all stated. Results are given only as plots; the text claims 'comparable to / faster than Intel MKL'.
- **Verifier notes:** Claim matches the README wording; I could not open the plot images (cs.ucr.edu blocked by proxy), so the size of the win is unverified. Makefile read: -O0 on own kernels is unusual but handicaps the project, not the baseline. Last commit 2022-02-03 is &gt;3 years old, so abandoned.
- **Fields the verifier corrected:** `compiler_and_flags`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** repo figures/Kernel18.png (single core vs MKL)
- **Pages the verifier opened:**
  - <https://github.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/README.md>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/LICENSE>
  - <https://github.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/commits>
- **Sources the enricher read:**
  - <https://github.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/README.md>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/kernels.h>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/test.c>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/utils.c>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/run.sh>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/include/kernel18.h>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/include/kernel19.h>
  - <https://raw.githubusercontent.com/yzhaiustc/Optimizing-DGEMM-on-Intel-CPUs-with-AVX512F/HEAD/figures/Kernel18.png>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/yzhaiustc/optimizing-dgemm-on-intel-cpus-with-avx512f`) · [data/wave8/enrich/raw/github_com_yzhaiustc_optimizing_dgemm_on_intel_cpus_with_avx512f.json](../../../data/wave8/enrich/raw/github_com_yzhaiustc_optimizing_dgemm_on_intel_cpus_with_avx512f.json) (enrichment confidence 0.8)

</details>
