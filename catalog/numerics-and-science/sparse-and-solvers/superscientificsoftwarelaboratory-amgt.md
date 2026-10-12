# AmgT (tensor-core AMG)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (CUDA; HYPRE-based)` · `Apache-2.0` · 🟡 stale

> Modified HYPRE 2.31 whose BoomerAMG SpGEMM and SpMV run on tensor cores; beats stock GPU HYPRE with cuSPARSE.

| | |
|---|---|
| **Beats** | HYPRE (GPU build calling cuSPARSE) |
| **Claimed result** | Paper (SC'24): AmgT outperforms the original GPU version of HYPRE by a factor of on geomean 1.46x, 1.32x and 2.24x (up to 2.10x, 2.06x and 3.67x) on NVIDIA A100, H100 and AMD MI210 GPUs, respectively. (Numbers taken from the WebSearch result text; which phase or total time they cover is not stated there.) |
| **Workload** | Algebraic multigrid solves on SuiteSparse matrices where AmgT replaces HYPRE's SpGEMM (setup phase) and SpMV (solve phase) with tensor-core kernels over a new mBSR storage format, in FP64 and mixed precision; the repo builds three executables (AmgT_FP64, AmgT_Mixed, and cuSPARSE = HYPRE baseline). |
| **Metric** | latency |
| **Hardware** | NVIDIA A100, H100 and AMD MI210 (per the paper text returned by search); repo recommends compute capability 8.0; host CPU not verified |
| **Compiler and flags** | compile.sh: CUDA_HOME=/usr/local/cuda-12.0; HYPRE configured with --with-cuda --enable-unified-memory and --with-gpu-arch='80 80' (A100) or '90 90' (H100); -gencode arch=compute_80,code=sm_80 (or compute_90); README advises CUDA 12.2+ and OpenMPI 4.0+. No explicit CXX optimization flags are visible in compile.sh. |
| **Adoption** | 9 stars |
| **Last commit** | 2024-11-11 |
| **Links** | [repository](https://github.com/SuperScientificSoftwareLaboratory/AmgT) · [benchmark](https://dl.acm.org/doi/10.1109/SC41406.2024.00058) |

## Verdict

Per a search-engine snippet of the SC '24 abstract (paper not opened: dl.acm.org and ieeexplore are blocked here), AmgT beats the original GPU HYPRE by geomean 1.46x on A100, 1.32x on H100 and 2.24x on MI210 (maximums 2.10x, 2.06x, 3.67x). The snippet does not say whether these are setup, solve or total times, or whether they are FP64 or mixed precision. The repo reproduces only the NVIDIA comparison: it builds stock HYPRE 2.31 with cuSPARSE SpGEMM/SpMV (HYPRE's default vendor path) against the AmgT builds and times setup and the 50-cycle solve separately with gettimeofday; it holds no result tables, and host CPU and matrix list are not stated.

## Use it when

- You already solve with HYPRE BoomerAMG on NVIDIA A100 (sm_80) or H100 (sm_90) and want faster setup and solve without retuning AMG parameters.
- Matrices whose nonzeros cluster into dense 4x4 blocks (FEM/PDE stencils, multi-DOF problems). The tensor-core paths only fire when blocks average 10 or more of 16 entries.
- Experiments with mixed-precision AMG where coarse levels can tolerate TF32/FP16 operators, inside an outer FP64 iteration that restores accuracy.
- Research baselines: reproducing or extending the SC '24 paper's tensor-core AMG kernels inside a known solver framework.

## Skip it when

- Production code that needs a maintained library: 7 commits, last on 2024-11-11, three open build/run issues (config file not found, missing HYPRE_krylov.h, cudaErrorInvalidDevice on H100 with CUDA 12.6), none answered.
- AMD or other GPUs: compile.sh builds only CUDA sm_80 or sm_90, and there is no HIP path, though the paper reports MI210 results.
- Very sparse or irregular matrices with little 4x4 block fill: these fall back to CUDA-core bitmap kernels and also pay a 4x4 padding memory cost.
- Accuracy-sensitive solves with the mixed build: level 1 runs in TF32 (10-bit mantissa) and levels 2 and coarser in FP16, which can change convergence.
- Multi-GPU runs: the driver calls cudaSetDevice(0) on every MPI rank, and multi-GPU behaviour is not documented.

## How it is fast

Matrices are converted lazily, on first use, from CSR to an 'mBSR' format: 4x4 dense blocks, each with a 16-bit occupancy bitmap, stored in the hypre_CSRMatrix struct next to the CSR arrays. SpGEMM uses binned, shared-memory hash-table symbolic passes over block columns. Its numeric pass issues FP64 mma.sync m8n8k4 tensor-core instructions for A-blocks with at least 10 of 16 entries filled, and CUDA-core bitmap arithmetic for sparser blocks. SpMV picks among four kernels by average nonzeros per block (tensor cores at 10 or more) and the standard deviation of blocks per block-row (warp-balanced row splitting at 12 or more). The mixed-precision build runs level-0 products in FP64, level-1 products through TF32 tensor cores (cvt.rna.tf32, mma m16n8k4) and all coarser levels in FP16. Because SpGEMM outputs mBSR directly, the format is reused across levels, which cuts CSR/BSR conversion cost.

## Compared with alternatives

Pick AmgT over Ginkgo or AMGCL only if you are committed to HYPRE BoomerAMG on A100/H100 and can carry a research fork; Ginkgo and AMGCL are maintained libraries with their own AMG. For a standalone tensor-core SpMV or SpGEMM kernel, use DASP or TileSpGEMM from the same lab. apxchol is the catalogued option that beats BoomerAMG with a different (approximate-Cholesky) method on Laplacian/SDDM systems.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Its own embedded HYPRE 2.31.0 (configured --with-cuda --enable-unified-memory), CUDA toolkit (cuSPARSE, cuBLAS, cuRAND, Thrust), MPI (README asks for OpenMPI 4.0+) |
| **Minimum toolchain** | CUDA 12.2+ recommended in the README (compile.sh defaults to /usr/local/cuda-12.0); mpicc; NVIDIA compute capability 8.0+ |
| **Platforms** | Linux, NVIDIA A100 (sm_80) or H100 (sm_90) only as built by compile.sh |
| **Thread safety** | Not documented. The modified HYPRE keeps non-atomic global timing counters (time_spmv_sum, spgemm_times, csr2bsr_step\*) and lazily attaches the mBSR copy to the matrix, so treat it as single-threaded per process. |
| **Drop-in for the baseline** | partial: same HYPRE/BoomerAMG API, but you must build and link this modified HYPRE in place of stock HYPRE, and the variant is fixed at compile time |

## Gotchas

- The test driver builds and configures a PCG solver (tol 1e-5, 300 iterations) but never uses it. The timed run is standalone BoomerAMGSetup plus BoomerAMGSolve with tol 1e-20 and max 50 iterations, i.e. a fixed 50 V-cycles, PMIS coarsening, Jacobi (relax 18) and extended+i interpolation. This corrects the verifier's 'PCG with BoomerAMG preconditioner' reading.
- compile.sh ships with execuative=cuSPARSE, so running it unchanged builds the baseline, not AmgT. It also contains a broken 'chmod -R \*' line and an unquoted CUDA_ARCH export.
- The AmgT SpMV entry (spmv_amgT_fp64/fp32/fp16) takes HYPRE's trans flag but never branches on it. It is correct inside BoomerAMG only because HYPRE's GPU default keeps explicit transposes (keepT = 1 in par_amg.c). Disabling KeepTranspose, or calling ParCSRMatrixMatvecT on a matrix without a stored transpose, would route a transposed product into a kernel that computes A\*x.
- The mBSR copy is built once (bsr_tag set on first SpMV or SpGEMM) and I found no code that invalidates it, so changing a matrix's values in place after first use is risky. Every kernel launch is followed by cudaDeviceSynchronize.

## Known shortcomings

- Tier B rests on the SC '24 proceedings record (DOI 10.1109/SC41406.2024.00058), which the verifier could not open; the numbers are from a search snippet and unverified. The repo harness (AmgT_test/test_new.c, compile.sh) builds the HYPRE+cuSPARSE baseline but names no host CPU or full flags. Last commit 2024-11-11, stale.
- The verifier's harness description was wrong: test_new.c creates a PCG but never uses it; the timed run is a standalone BoomerAMGSetup plus Solve with tol 1e-20 and max 50 iterations, so a fixed 50 V-cycles. compile.sh ships execuative=cuSPARSE, which builds the baseline. AmgT's SpMV ignores the transpose flag (safe only because HYPRE's GPU default is keepT=1). The mixed build runs level 1 in TF32 and coarser levels in FP16 against HYPRE's FP64. No HIP path, so the MI210 2.24x is not reproducible from the repo. Issues #1-#3 (build and run failures) unanswered.

## Caveats and trade-offs

Numbers are from a WebSearch snippet of the SC '24 abstract (ACM DL record of DOI 10.1109/SC41406.2024.00058, the DOI the repo README cites); the paper itself could not be opened here (dl.acm.org, doi.ieeecomputersociety.org, ieeexplore are egress-blocked), so which phase (setup, solve or total) the geomeans cover and the FP64 versus mixed-precision split are unverified. The repo has no result tables. Its harness (AmgT_test/test_new.c) runs HYPRE PCG with a BoomerAMG preconditioner (tolerance 1e-5, max 300 iterations) and times BoomerAMGSetup and the solve separately with gettimeofday; compile.sh builds three variants (AmgT_FP64, AmgT_Mixed, cuSPARSE = unmodified HYPRE calling cuSPARSE) for A100 (sm_80) or H100 (sm_90) only, on embedded HYPRE 2.31.0 (2024/02/14) configured with --with-cuda --enable-unified-memory. There is no MI210/HIP build path in compile.sh, so the 2.24x MI210 figure is not reproducible from the repo. Host CPU model and per-matrix problem set not verified. Not a GitHub fork, though it embeds modified HYPRE. [retier] 2026-10-03 retier attempt: the SC '24 paper body is still unreachable (dl.acm.org, ieeexplore.ieee.org and ssslab.cn are egress-blocked; no GitHub-hosted PDF found). The abstract snippet confirms that the third GPU is the AMD MI210 and that the three geomeans are for A100, H100 and MI210 in that order. Which phase they cover, the CUDA/ROCm and HYPRE versions, and the TF32/FP16 per-level precision mix are not verified from the paper.

Implemented inside a modified copy of HYPRE (AmgT_HYPRE/), not a standalone library: using it means taking that fork or porting the mBSR data structure (seq_mv.h), SpGEMM (csr_spgemm_device.c) and SpMV (csr_matvec_device.c). The variant is chosen at build time by copying config_files/&lt;variant&gt;.h over seq_mv.h. Needs tensor-core GPUs (compute capability 8.0 or newer) for the main gains; the mixed-precision mode changes numerics. The embedded HYPRE code carries its own license files, which I did not inspect.

## Maintenance

Stale research code (7 commits, last 2024-11-11, 9 stars, issues unanswered). It is Apache-2.0 at the top level, with HYPRE's own Apache-2.0/MIT files embedded, so the kernels are copyable, but expect build fixes before it runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SC '24 paper: the record's benchmark_url is the ACM DL record of DOI 10.1109/SC41406.2024.00058, which the repo README names as the AmgT SC '24 paper, so the search snippet's numbers come from that venue's abstract page; I could not open it (dl.acm.org and doi.ieeecomputersociety.org are egress-blocked). The repo's own harness (AmgT_test/test_new.c, compile.sh) builds the HYPRE+cuSPARSE baseline but states no host CPU or full flags, so not A.
- **Verifier notes:** Could not open the paper (EGRESS_BLOCKED on dl.acm.org and doi.ieeecomputersociety.org); B kept because the snippet's source is the SC '24 proceedings record whose DOI matches the repo README, but the numbers are unverified by me. Metadata confirmed: Apache-2.0 LICENSE, 9 stars, 7 commits, last commit 2024-11-11 (stale), not fork/archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/commits/main>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/tree/main/AmgT_test>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/compile.sh>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_test/test_new.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_test/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/CMakeLists.txt>
  - <https://github.com/SuperScientificSoftwareLaboratory>
- **Sources the enricher read:**
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/tree/main/config_files>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/issues>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/issues/1>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/issues/2>
  - <https://github.com/SuperScientificSoftwareLaboratory/AmgT/issues/3>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/compile.sh>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_test/test_new.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_test/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/config_files/AmgT_FP64.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/config_files/AmgT_Mixed.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/config_files/cuSPARSE.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/seq_mv/csr_matvec_device.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/seq_mv/csr_spgemm_device.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/parcsr_mv/par_csr_matvec.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/parcsr_mv/par_csr_matvec_device.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/parcsr_ls/par_amg.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/utilities/device_utils.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/utilities/handle.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/AmgT/HEAD/AmgT_HYPRE/src/utilities/general.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/superscientificsoftwarelaboratory/amgt`) · [data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_amgt.json](../../../data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_amgt.json) (enrichment confidence 0.62)

</details>
