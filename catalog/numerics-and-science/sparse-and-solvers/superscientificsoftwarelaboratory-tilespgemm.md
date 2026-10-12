# TileSpGEMM (tiled GPU SpGEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> Research CUDA SpGEMM on 16x16 sparse tiles; PPoPP '22 reports wins over cuSPARSE on 139 of 142 large matrices.

| | |
|---|---|
| **Beats** | cuSPARSE, bhSPARSE, NSPARSE and spECK SpGEMM |
| **Claimed result** | TileSpGEMM outperforms cuSPARSE, bhSPARSE, NSPARSE and spECK in 139, 138, 127 and 94 out of 142 square matrices, delivering up to 2.78x, 145.35x, 97.86x and 3.70x speedups respectively (snippet only). |
| **Workload** | Sparse general matrix-matrix multiplication (SpGEMM) on NVIDIA GPUs over 142 square matrices, using a tiled structure with non-empty tiles stored sparsely. |
| **Metric** | throughput |
| **Hardware** | README recommends an NVIDIA GPU with compute capability 8.6 and the CUDA Toolkit; GPU used in the paper not read |
| **Compiler and flags** | nvcc -O3 -w -arch=compute_61 -code=sm_86 -gencode=arch=compute_61,code=sm_86 -Xcompiler -fopenmp -Xcompiler -mfma, double precision, CUDA 11.4 path (src/Makefile) |
| **Adoption** | 48 stars, 12 forks, 52 commits |
| **Last commit** | 2022-11-09 |
| **Links** | [repository](https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM) · [benchmark](https://doi.org/10.1145/3503221.3508431) |

## Verdict

Per the PPoPP '22 abstract (search snippets; paper blocked here), on GeForce RTX 3090 and RTX 3060 over 142 square SuiteSparse matrices of at least one billion flops each (C = A^2 and C = A\*A^T), TileSpGEMM beat cuSPARSE, bhSPARSE, NSPARSE and spECK on 139, 138, 127 and 94 matrices, with maxima of 2.78x, 145.35x, 97.86x and 3.70x. The repo's cuSPARSE baseline is the generic cusparseSpGEMM API (workEstimation/compute/copy) built with nvcc -O3 against CUDA 11.4; averages, CPU model and cuSPARSE version were not seen.

## Use it when

- Benchmarking or researching GPU SpGEMM on large square matrices (the paper uses at least one billion flops each) for C = A^2 or C = A\*A^T, where it beat cuSPARSE's generic SpGEMM on 139 of 142 matrices.
- Matrices whose nonzeros cluster into dense-ish 16x16 blocks (FEM, structural, banded), where per-tile bitmask symbolic work and dense on-chip accumulators pay off.
- Pipelines that can keep matrices in a tiled format end to end, so the host-side CSR-to-tile conversion and tile-to-CSR conversion of C (both outside the reported SpGEMM time) are amortized.
- Ampere-class NVIDIA GPUs like the paper's RTX 3090 and RTX 3060 (the Makefile targets sm_86).

## Skip it when

- Any reuse in a product: the repo has no LICENSE and the README names none, so the code is not clearly reusable; spECK and OpSparse are MIT.
- Very large inputs or recent toolchains: open issue #6 (2025) reports a NULL-pointer error and a segfault on HV15R (283M nonzeros) and a 97.5M-nonzero matrix on an RTX 4090 with CUDA 11.8; open issue #5 (2024) reports a build error under CUDA 12.2; open issue #4 (2023) reports '__builtin_ia32_rndscaless_round is undefined' at build time. None shows a reply.
- Hypersparse or irregular matrices where spECK's per-row hashing wins: spECK was faster on 48 of the 142 paper matrices, and a later third-party study (snippet only) puts TileSpGEMM's average speedup over cuSPARSE at 3.47x, below spECK (5.67x) and OpSparse (4.91x).
- Code that needs a CSR-in, CSR-out API, single precision out of the box, 64-bit indices (m, n and nnz are int) or non-x86 hosts.
- Anything needing maintenance: last commit 2022-11-09, 5 open issues and an open undefined-behavior PR, all without maintainer response.

## How it is fast

Tiling turns SpGEMM into three bounded steps. Step 1 finds which C tiles are non-empty with a tile-level SpGEMM using a sparse accumulator. Step 2 computes each C tile's nonzero pattern with bitwise ORs of 16-bit row masks, so C is allocated exactly, with no intermediate-product buffers. Step 3 computes values: it intersects A's tile row with B's tile column by binary search (positions from step 2 are cached speculatively), bins C tiles by nonzero count (thresholds 32/224/256) and picks a sparse or dense accumulator in shared memory per bin. The paper's argument is that this fixes load imbalance, intermediate-buffer sizing and accumulator design at once.

## Compared with alternatives

Pick spECK (MIT, CSR in and out, float and double) or OpSparse (MIT, higher average speedup over cuSPARSE in the third-party snippet) for anything you ship. TileSpGEMM is worth studying when your matrices are block-structured and you can stay in its tiled format, or as the reference for the tile approach next to the same lab's TileSpMV and DASP.

## Integration

| | |
|---|---|
| **Form** | source-drop (single nvcc compile of src/main.cu with header-only .h files; no library target) |
| **Dependencies** | CUDA runtime and cuSPARSE (cuSPARSE only for the reference check), OpenMP on the host; src/ vendors its own copies of cuda_fp16.h and cuda_fp16.hpp |
| **Minimum toolchain** | CUDA 11.x (Makefile hard-codes /usr/local/cuda-11.4); tested on Ubuntu 18.04/20.04 per README; CUDA 12.2 build failure reported (issue #5) |
| **Platforms** | NVIDIA GPUs (Makefile builds compute_61 PTX to sm_86 only; compute capability 8.6 recommended); x86-64 Linux host (common.h includes x86intrin.h and immintrin.h, and the build passes -mfma) |
| **Thread safety** | not documented; the host function tilespgemm() does its own cudaMalloc calls for every operand and for C |
| **Drop-in for the baseline** | false — inputs must be converted from CSR into its SMatrix tile structure, C is returned in tiles, and the shipped driver only squares A or forms A\*A^T |

## Gotchas

- The reported SpGEMM time (gettimeofday, one run since REPEAT_NUM is 1, no warm-up) covers the three GPU steps plus allocations of C, but not CSR-to-tile conversion of A and B, which the paper reports separately, nor tile-to-CSR conversion of C.
- main.cu replaces the input matrix values with i % 10 before multiplying, so the driver's results are not your matrix's product; CHECK_RESULT defaults to 1 in common.h, which adds a host-side tile2csr and a cuSPARSE run.
- Open PR #2 (2022-10-14) reported an out-of-bounds read and wrong-size memsets in csr2tile.h (reproduced on RTX 3090, RTX 2080 and GTX 1650 Ti) and a use-after-free in main.cu under CHECK_RESULT. After the November 2022 re-upload of src/, the PR's remaining diff is 2 added lines and 1 removed line in main.cu, so the use-after-free fix is probably still unmerged; the csr2tile.h memsets now look size-correct, but the out-of-bounds fix was not confirmed.
- Issue #3: on a GTX 1650 Ti the cuSPARSE reference returned nnzC = 0 for cant and pdb1HYS, so the built-in check prints 'cuSPARSE failed!' even when TileSpGEMM's count is right; do not rely on the harness alone for validation.

## Known shortcomings

- No licence, so reference only; PPoPP'22 win counts confirmed from the abstract.
- No license. The driver only computes A^2 or A\*A^T and overwrites the input values with i % 10; C comes out tiled, not CSR; the timed region excludes the CSR-to-tile conversion and is a single run; 32-bit indices, x86-only host. Open and unanswered: #6 NULL pointer/segfault on HV15R (283M nnz) on an RTX 4090 with CUDA 11.8, #5 CUDA 12.2 build error, #4 build error, PR #2 undefined behaviour (out-of-bounds read, memsets, use-after-free). The repo's cuSPARSE baseline is the generic cusparseSpGEMM API; the paper's GPUs were an RTX 3090 and RTX 3060 (snippet).

## Caveats and trade-offs

Numbers come from the PPoPP '22 abstract as quoted in search results; the paper itself (dl.acm.org, ppopp22.sigplan.org) was not opened. This verifier's search confirmed the win counts (139, 138, 127 and 94 of 142 matrices executing at least one billion flops); the 'up to' maxima (2.78x, 145.35x, 97.86x, 3.70x) come from the search agent's snippet. Maxima are best cases; spECK is faster on 48 of 142 matrices, and the 145x/98x maxima are against bhSPARSE/NSPARSE, not cuSPARSE (2.78x maximum). A later third-party snippet puts TileSpGEMM's average at 3.47x over cuSPARSE, below spECK (5.67x) and OpSparse (4.91x). The repo's test program checks output against cuSPARSE and prints runtime and GFLOPS per matrix; README recommends a compute capability 8.6 GPU, but the GPU and host CPU used in the paper were not seen. No license file, so usability is 'reference'. Last commit 2022-11-09.

CUDA GPU only; repo has data/, src/ and README only; no LICENSE file visible and the README names none, so the code is not clearly reusable.

## Maintenance

Abandoned since 2022-11-09, with no license (reference only) and unanswered crash and build reports.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: TileSpGEMM is a peer-reviewed PPoPP '22 paper (doi 10.1145/3503221.3508431, README), and a search result quoting its abstract confirms it outperforms cuSPARSE, bhSPARSE, NSPARSE and spECK on 139, 138, 127 and 94 of 142 square matrices of at least one billion flops. B rests on venue plus abstract per earlier precedents; the paper is blocked, and while src/Makefile gives nvcc flags, the GPU and host CPU models are not stated in the repo, so not A.
- **Verifier notes:** Metadata checked: no LICENSE (404, GitHub detects none), 48 stars, 12 forks, 52 commits, last commit 2022-11-09 on main (abandoned). benchmark_url set to the paper DOI from the README (not opened; blocked).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/commits>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/Makefile>
- **Sources the enricher read:**
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/tree/main/src>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/commits/main>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/issues?q=is%3Aissue>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/issues/3>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/issues/5>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/issues/6>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/pulls?q=is%3Apr>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/pull/2>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpGEMM/pull/2/files>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/csr2tile.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/tilespgemm-cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/spgemm_cu.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpGEMM/HEAD/src/external/cusparse/spgemm_cusparse.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/superscientificsoftwarelaboratory/tilespgemm`) · [data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_tilespgemm.json](../../../data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_tilespgemm.json) (enrichment confidence 0.6)

</details>
