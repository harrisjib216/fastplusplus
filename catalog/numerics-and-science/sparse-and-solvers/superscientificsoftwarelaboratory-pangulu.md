# PanguLU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `AGPL-3.0` · 🟢 active

> Distributed MPI+CUDA sparse LU direct solver using regular 2D sparse blocks; reports up to 11.7-18x over SuperLU_DIST on 128 GPUs.

| | |
|---|---|
| **Beats** | SuperLU_DIST |
| **Claimed result** | Peer-reviewed SC '23 paper, per its abstract as quoted in search results: on two distributed heterogeneous platforms with 128 NVIDIA A100 and 128 AMD MI50 GPUs, PanguLU achieves up to 11.70x and 17.97x speedups over SuperLU_DIST, and scales up to 47.51x and 74.84x over a single GPU. Paper body not opened. |
| **Workload** | Distributed sparse LU factorization and solve of sparse test matrices on CPU+GPU clusters (up to 128 NVIDIA A100 and 128 AMD MI50 GPUs, per a search-result excerpt of the SC'23 paper abstract). |
| **Metric** | latency |
| **Adoption** | 51 stars |
| **Last commit** | 2026-06-25 |
| **Links** | [repository](https://github.com/SuperScientificSoftwareLaboratory/PanguLU) · [benchmark](https://dl.acm.org/doi/10.1145/3581784.3607050) |

## Verdict

Per the SC'23 paper's abstract (paper body not opened, so matrices, SuperLU_DIST version and flags are unknown), PanguLU reached up to 11.70x over SuperLU_DIST on 128 NVIDIA A100s and up to 17.97x on 128 AMD MI50s, and scaled 47.51x and 74.84x over one GPU. These are best-case maxima from the 2023 code, not typical ratios. An independent 2025 paper (Hu et al.) implies about 2.2x over SuperLU_DIST on one A100 (derived from the 1.50x and 3.32x geometric means in its abstract).

## Use it when

- Large unsymmetric sparse systems whose factors outgrow one node, on an MPI cluster with one NVIDIA GPU per rank, where you would otherwise run SuperLU_DIST
- Matrices whose factors are still fairly sparse inside blocks, so sparse block kernels beat SuperLU_DIST's dense supernodal kernels (an independent 2025 study on one A100 found PanguLU about 2.2x faster than SuperLU_DIST in numeric factorization, geometric mean, derived from its abstract)
- Many right-hand sides with a fixed matrix: factor once with pangulu_gstrf, then call pangulu_gstrs repeatedly
- Complex-valued or single-precision systems on GPUs (all four value types are supported, chosen at build time)

## Skip it when

- Ill-conditioned or hard-to-pivot matrices: numeric factorization does no partial pivoting and silently replaces pivots smaller than 1e-16 with 1e-16, MC64 static pivoting is optional and unavailable for complex values, and there is no iterative refinement; open issue #5 (2025, unanswered) reports relative residuals around 10 for some matrices and kernels
- Single-GPU use where newer solvers exist: Caracal (SC25) reports up to 94x over PanguLU on one A100, and the structure-aware irregular blocking paper reports 1.50x over PanguLU
- Reproducing the paper's numbers out of the box: closed issue #2 measured 2-10x slower factorization than the paper on one A100 40GB (cage12: 578.7 s numeric, 7.3 GFLOP/s) with no maintainer explanation
- Proprietary or SaaS products that cannot accept AGPL-3.0, which also covers network use
- AMD GPUs with the current code: the SC'23 paper ran on MI50, but the repo ships only CPU and CUDA platform backends

## How it is fast

Instead of supernodal or multifrontal layouts, the matrix is cut into equal nb x nb blocks that stay sparse, which avoids the extra fill a dense supernode stores, and the blocks are mapped 2D block-cyclically over a p x q process grid. Each block task (GETRF, TSTRF, GESSM, SSSSM) adaptively picks a sparse or dense BLAS kernel on CPU or GPU, and a synchronisation-free communication scheme lets ranks start tasks as soon as their inputs arrive instead of waiting at level barriers. Version 5.0 adds a task aggregator for numeric factorization and a smaller GPU memory layout.

## Compared with alternatives

Pick PanguLU over CKTSO, GSS or RSLAB when you need a distributed, multi-node GPU LU and SuperLU_DIST is your reference. For single-node circuit matrices CKTSO targets KLU-class workloads, and for SPD systems a Cholesky solver such as BaSpaCho or the task-based CHOLMOD is the better fit.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | MPI (tested MPICH 4.3.0), OpenMP, BLAS for CPU kernels (tested OpenBLAS 0.3.26), CUDA for GPU (tested 12.9), optional METIS (32-bit index build); MC64 is built in |
| **Minimum toolchain** | C compiler with OpenMP (gcc), mpicc, nvcc and GNU make; you edit make.inc and examples/Makefile by hand (it builds both libpangulu.a and libpangulu.so) |
| **Platforms** | Linux clusters, x86-64 CPU-only or NVIDIA GPU; make.inc defaults to -gencode arch=compute_61 (Pascal), so edit it for newer GPUs such as the A100 (sm_80) |
| **Thread safety** | not documented; the library keeps some settings in global variables and the example initialises MPI with MPI_THREAD_MULTIPLE, so treat one solver per process at a time as the safe pattern |
| **Drop-in for the baseline** | no |

## Gotchas

- On errors such as a null options pointer, nb = 0 or a value-type mismatch, the library calls exit(1) inside the solver rather than returning a status
- The process grid is p x q, where p is the largest divisor of the rank count at or below its square root, so a prime number of ranks gives a 1 x P grid
- Missing structural diagonal entries are filled with 1e-8 before factoring, which perturbs the matrix you passed in
- Block size nb strongly affects speed and must be tuned per matrix (the example uses -nb 10 on a toy matrix; init falls back to 256 only when nb is negative)

## Known shortcomings

- SC'23 abstract (via search): 11.70x and 17.97x over SuperLU_DIST, which is not a listed baseline; paper unreadable here.
- Numerical robustness: no partial pivoting; pivots below 1e-16 are replaced by +1e-16; no iterative refinement; MC64 optional and unavailable for complex. Open #5: residual \~10 on some matrices. Closed #2: one A100 2-10x slower than the paper (cage12 578.7 s), unexplained. Errors call exit(1). make.inc defaults to sm_61. Repo has no AMD backend although the paper used MI50.

## Caveats and trade-offs

Paper not opened (dl.acm.org, sc23.supercomputing.org, arxiv.org and researchgate.net are blocked here) and the README has no performance numbers, so the SuperLU_DIST version, matrices, typical (not maximum) speedups, compiler and flags are unverified. The figures are 'up to' maxima from a 2023 version (v3.x era); the code is now v5.0.0. Distributed multi-GPU result (MPI + OpenMP + CUDA), so single-node CPU users may see very different ratios. SuperLU_DIST is not in the SuiteSparse/Eigen/PETSc baseline list (PETSc can call it). AGPL-3.0 is OSI-approved but strong copyleft, including network use.

Written in C with MPI, OpenMP and CUDA; regular 2D block-cyclic layout with sparse blocks and synchronisation-free communication; optional METIS and MC64 reordering; real and complex, single and double precision. AGPL-3.0 copyleft. Tested with MPICH 4.3.0, CUDA 12.9, OpenBLAS 0.3.26 per README.

## Maintenance

Active research code (v5.0.0, latest commit 2026-06-25, 38 commits, 51 stars), but AGPL-3.0, with an unanswered accuracy report (issue #5) and an unanswered performance-gap report (issue #2), so validate residuals on your own matrices before adopting it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README cites the peer-reviewed SC '23 paper (Fu et al., 'PanguLU: A Scalable Regular Two-Dimensional Block-Cyclic Sparse Direct Solver on Distributed Heterogeneous Systems'), and a search result quoting its abstract gives up to 11.70x (128 A100) and 17.97x (128 MI50) over SuperLU_DIST. The paper itself could not be opened (dl.acm.org and sc23.supercomputing.org are egress-blocked), so B rests on the venue plus the abstract, per earlier precedents.
- **Verifier notes:** Repo page: AGPL-3.0, 51 stars, 15 forks, not archived, 38 commits. The commits page heads its latest commit 'v5.0.0' with 'Commits on Jun 25, 2026', while the README dates v5.0.0 to Jul. 31, 2025; I used the commit date, which makes the project active rather than stale.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/README.md>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/commits>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/commits/main>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/releases>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/include/pangulu.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/include/pangulu_interface_common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/make.inc>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/build_list.csv>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/examples/example.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/src/pangulu.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/src/pangulu_common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/src/pangulu_numeric.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/src/pangulu_reordering.c>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/PanguLU/HEAD/src/platforms/01_SHAREDMEM/00_CPU/000_CPU/pangulu_platform_0100000.c>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/tree/main/src>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/tree/main/src/platforms>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/tree/main/src/platforms/01_SHAREDMEM/00_CPU/000_CPU>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/issues?q=is%3Aissue>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/issues/2>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/issues/4>
  - <https://github.com/SuperScientificSoftwareLaboratory/PanguLU/issues/5>
  - https://arxiv.org/abs/2512.04389 (EGRESS_BLOCKED; abstract read from WebSearch snippets)
  - https://dl.acm.org/doi/10.1145/3581784.3607050 (not opened; abstract via WebSearch snippet)
  - https://dl.acm.org/doi/full/10.1145/3712285.3759792 (Caracal, not opened; abstract via WebSearch snippet)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/superscientificsoftwarelaboratory/pangulu`) · [data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_pangulu.json](../../../data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_pangulu.json) (enrichment confidence 0.7)

</details>
