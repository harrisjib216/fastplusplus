# CapelliniSpTRSV (thread-level synchronization-free GPU sparse triangular solve)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> GPU sparse lower-triangular solve (CSR) using one thread per row; ICPP '20 reports 4.00x over cuSPARSE csrsv2.

| | |
|---|---|
| **Beats** | cuSPARSE SpTRSV (CUSPARSE_SOLVE_POLICY_NO_LEVEL / USE_LEVEL) and the SyncFree SpTRSV of bhSPARSE |
| **Claimed result** | 3.41 GFLOPS/s, which is 5.26x speedup over the state-of-the-art synchronization-free SpTRSV algorithm and 4.00x speedup over the SpTRSV in cuSPARSE. |
| **Workload** | Sparse triangular solve (CSR input, no level-set preprocessing) on 245 matrices from the Florida (SuiteSparse) Sparse Matrix Collection, three GPU platforms. |
| **Metric** | throughput |
| **Hardware** | NVIDIA GTX 1080 (Pascal, CUDA 8.0, Ubuntu 16.04.4), Tesla V100 (Volta, CUDA 9.0, Ubuntu 16.04.1), GeForce RTX 2080 Ti (Turing, CUDA 10.2, Ubuntu 18.04.4); OpenCL variant tested on Radeon Vega 11 APU with ROCm; host CPU model not stated |
| **Compiler and flags** | nvcc -O3 -w -m64 -Xptxas -dlcm=cg -gencode arch=compute_61,code=sm_61 (CUDA/ourWrtFst/Makefile); CUDA 8.0 / 9.0 / 10.2 |
| **Adoption** | 56 stars, 12 forks |
| **Last commit** | 2021-03-19 |
| **Links** | [repository](https://github.com/JiyaSu/CapelliniSpTRSV) · [benchmark](https://github.com/JiyaSu/CapelliniSpTRSV) |

## Verdict

The ICPP '20 paper abstract (reproduced in the README) reports a 3.41 GFLOPS/s average for SpTRSV over 245 SuiteSparse matrices on three NVIDIA GPUs (GTX 1080, V100, RTX 2080 Ti; CUDA 8.0-10.2; nvcc -O3, sm_61 in the shipped Makefile). That is 5.26x over warp-level SyncFree SpTRSV and 4.00x over cuSPARSE csrsv2. The README does not say which GPU or aggregation the headline ratios come from, and the paper itself was not opened.

## Use it when

- Repeated triangular solves on NVIDIA GPUs where the matrix changes often enough that cuSPARSE's analysis phase or a level-set preprocessing step is a real cost
- Lower-triangular factors with short rows (few nonzeros per row) and many rows per dependency level, the case the paper targets
- As a reference implementation or starting point for your own thread-level sync-free SpTRSV kernel (MIT, about 100 lines of kernel code)
- OpenCL/AMD GPUs, using the openCL/WrtFst and openCL/mix variants (tested on a Radeon Vega 11 APU with ROCm)

## Skip it when

- Matrices with long rows or few rows per level: the README says the thread-level kernels target short-row, wide-level matrices, so use 'mix' or a warp-level solver there
- You need a maintained library API: there is no header, CMake target, error handling or upper-triangular/transposed solve, and the last commit was in 2021
- Comparisons against current cuSPARSE: the cuSP baseline calls the legacy cusparseDcsrsv2 routines on CUDA 8-10.2, not the generic cusparseSpSV API of later CUDA versions
- Modern toolchains without edits: Makefiles hard-code sm_61 and /usr/local/cuda, and open issue #2 reports a build failure in SyncFree_csc with CUDA 11.5 + GCC 11.4 (workaround: GCC 10.5 as host compiler)

## How it is fast

Synchronization-free SpTRSV (Liu et al.) gives each row a whole warp and waits on per-row ready flags. Capellini gives each row a single thread. Rows are handed out in order through an atomicAdd counter. Each thread walks its row in column order, adds up the entries whose x[col] flag is already set and spins on the next one; when it reaches the diagonal it writes x[i], calls __threadfence and sets its own flag. This removes the warp-per-row waste on matrices with many independent rows per level and few nonzeros per row. The 'mix' variant has a host pass that gives a 32-row group to a warp-per-row kernel when its average nnz/row is 10 or more, and to the thread-per-row path otherwise.

## Compared with alternatives

Pick it over Sympiler when the triangular solve has to run on a GPU and you have no time for symbolic preprocessing. Pick it over CSR5/merge-spmv/ISpMV only for triangular solves; those siblings are SpMV kernels and solve a different problem.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (cudart, cuSPARSE for the baseline folders, Thrust headers included); OpenCL/ROCm for the OpenCL variant |
| **Minimum toolchain** | Tested with CUDA 8.0, 9.0 and 10.2; Makefile targets compute_61/sm_61 (edit for other GPUs) |
| **Platforms** | NVIDIA GPUs (GTX 1080, V100, RTX 2080 Ti tested); AMD Radeon Vega 11 via OpenCL |
| **Thread safety** | not documented; each call allocates and frees its own device buffers |
| **Drop-in for the baseline** | partial — same CSR input as cusparse csrsv2, but a different, benchmark-shaped C function (it allocates device memory, builds b from x = 1 and times itself); you must extract the kernel and its flag/counter setup |

## Gotchas

- The kernel assumes column indices sorted ascending within each row and the diagonal stored as the last entry of every row (it divides by csrVal[rowPtr[i+1]-1]); a row without a stored diagonal never sets its ready flag, so dependent rows spin forever
- Ready flags are a plain int array (not volatile or atomic); visibility relies on __threadfence plus the -Xptxas -dlcm=cg flag in the Makefile that keeps global loads out of L1. Keep that flag if you vendor the kernel
- The benchmark harness does not solve with your matrix's values: change2tran keeps A's strictly-lower sparsity pattern, sets every value to 1 (unit lower-triangular), and checks the result against x = 1 with a loose 1% relative tolerance
- Precision, repeat count (BENCH_REPEAT 100) and warps per block are compile-time macros in common.h (default double precision); timings use gettimeofday around launch + cudaDeviceSynchronize

## Known shortcomings

- Evidence is the ICPP'20 paper abstract quoted in the README; host CPU not stated, so not A.

## Caveats and trade-offs

Numbers are the paper abstract as reproduced in the README (ICPP '20 per the README citation); the paper itself was not opened. The README does not say which GPU or aggregation the 5.26x/4.00x refer to. cuSPARSE baseline is the CUDA 8-10.2 era SpTRSV; newer cuSPARSE versions were not tested. Authors note the win is for matrices with many components per level and few nonzeros per row. Last commit 2021. Host CPU model not stated, so not tier A.

GPU-only research code (CUDA and OpenCL); takes CSR, so no format conversion; one folder per algorithm (SyncFree_csc, cuSP, cuSP-layer, our2Part, ourWrtFst, mix); precision and GPU parameters are edited in common.h and the CUDA path in each Makefile, which hard-codes sm_61.

## Maintenance

Abandoned: last commit 2021-03-19, with one unanswered build issue from 2024. It is MIT-licensed and the kernel is small enough to vendor, but expect to update Makefiles for current CUDA/GCC versions and GPU architectures.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README reproduces the abstract of the peer-reviewed ICPP '20 paper (bibtex in README): 245 SuiteSparse matrices on three GPUs, 3.41 GFLOPS/s, 5.26x over SyncFree SpTRSV and 4.00x over cuSPARSE SpTRSV. Benchmark code (CUDA/ourWrtFst, CUDA/cuSP baselines) and nvcc flags (CUDA/ourWrtFst/Makefile) are public and GPUs are named, but the host CPU model is not stated and the paper (dl.acm.org) and slides (\*.github.io) are blocked here, so not A.
- **Verifier notes:** Record matches the README and repo: MIT license, 56 stars, 12 forks, last commit 2021-03-19 ('upload example matrices'), so abandoned. The README does not say which GPU or aggregation the 5.26x/4.00x headline uses; common.h defaults to double precision and 100 repeats.
- **Shortcomings recorded by:** verifier
- **Pages the verifier opened:**
  - <https://github.com/JiyaSu/CapelliniSpTRSV>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/commits>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/README.md>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/Makefile>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/common.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/JiyaSu/CapelliniSpTRSV>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/tree/master/CUDA>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/tree/master/CUDA/ourWrtFst>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/tree/master/CUDA/cuSP>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/tree/master/openCL>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/issues?q=is%3Aissue>
  - <https://github.com/JiyaSu/CapelliniSpTRSV/issues/2>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/README.md>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/Makefile>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/common.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/main.cu>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/spts_syncfree_cuda_csr_wrt.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/read_mtx.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/ourWrtFst/tranpose.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/mix/main.cu>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/mix/Makefile>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/mix/spts_syncfree_cuda_csr_wrt.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/mix/tranpose.h>
  - <https://raw.githubusercontent.com/JiyaSu/CapelliniSpTRSV/HEAD/CUDA/cuSP/spts_cuSPARSE.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jiyasu/capellinisptrsv`) · [data/wave8/enrich/raw/github_com_jiyasu_capellinisptrsv.json](../../../data/wave8/enrich/raw/github_com_jiyasu_capellinisptrsv.json) (enrichment confidence 0.75)

</details>
