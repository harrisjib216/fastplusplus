# TileSpMV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (CUDA)` · `Apache-2.0` · 🔴 abandoned

> CUDA SpMV on 16x16 sparse tiles with per-tile format choice; paper beats Merge-SpMV, CSR5 and BSR on most SuiteSparse matrices.

| | |
|---|---|
| **Beats** | Merge-SpMV (Merrill and Garland), CSR5 and BSR SpMV on NVIDIA GPUs, as named in the IPDPS 2021 abstract. The BSR implementation is presumably cuSPARSE bsrmv, but the snippets do not say so, and whether cuSPARSE CSR was also compared is unconfirmed. |
| **Claimed result** | Peer-reviewed paper (Niu, Lu, Dong, Jin, Liu, Tan, 'TileSpMV: A Tiled Algorithm for Sparse Matrix-Vector Multiplication on GPUs', IPDPS 2021, pp. 68-78). According to its abstract as quoted in search results, TileSpMV is faster than Merge-SpMV, CSR5 and BSR on most matrices of the full SuiteSparse Matrix Collection, with up to 2.61x, 3.96x and 426.59x speedups respectively. These are maxima only; average or geomean speedups were not visible. The paper body was not opened, and the repo README has no numbers. |
| **Workload** | SpMV (y = Ax) on NVIDIA GPUs over all 2757 matrices of the SuiteSparse Matrix Collection (per abstract snippets). The matrix is split into 16x16 sparse tiles, and seven warp-level kernels (CSR, COO, ELL, HYB, dense, dense row, dense column) are chosen per tile; nonzeros of very sparse tiles go to a separate matrix, which the repo computes with an embedded CSR5 (src/external/CSR5_cuda). FP64 by default (MAT_VAL_TYPE=double). |
| **Metric** | throughput |
| **Hardware** | Paper, per search-result snippets: NVIDIA A100 (Ampere) and NVIDIA Titan RTX (Turing), all 2757 SuiteSparse matrices; host CPU unknown. README: GPU with compute capability &gt;= 3.5 ('NVIDIA Tesla K40 as tested'), CUDA 11.1, Ubuntu 18.04/20.04. |
| **Compiler and flags** | From src/Makefile: nvcc, CUDA 11.1 path, -O3 -w -arch=compute_61 -code=sm_86 -gencode=arch=compute_61,code=sm_86, -Xcompiler -fopenmp -O3, MAT_VAL_TYPE=double |
| **Adoption** | 13 stars |
| **Last commit** | 2022-08-12 |
| **Links** | [repository](https://github.com/SuperScientificSoftwareLaboratory/TileSpMV) · [benchmark](https://doi.org/10.1109/IPDPS49936.2021.00016) |

## Verdict

IPDPS 2021 paper (abstract seen only through search results; the paper was not opened): on all 2757 SuiteSparse matrices, on an NVIDIA A100 and a Titan RTX, TileSpMV beat Merge-SpMV on 1813 matrices, CSR5 on 2040 and BSR on 1638, with maximum speedups of 2.61x, 3.96x and 426.59x. Average speedups, precision per figure and the BSR implementation (presumably cuSPARSE) were not visible. The repo's harness times only TileSpMV: it averages 1000 runs, each timed with gettimeofday around the launch and a synchronize, after 200 warm-up runs and 4000 untimed runs, then checks against a CPU CSR reference. It runs no baselines.

## Use it when

- Repeated FP64 SpMV with a fixed sparsity pattern on NVIDIA GPUs (iterative solvers), where the one-time host-side tile conversion is amortized.
- Matrices with local dense structure inside 16x16 windows (small dense blocks, dense rows or columns) that do not fit BSR well; the paper's largest wins (up to 426.59x) are against BSR.
- As a research baseline or starting point for tile-based GPU sparse kernels: DASP, TileSpMSpV and CB-SpMV all benchmark against it, and the same lab's TileSpGEMM uses a similar tile structure.
- When you need Apache-2.0 CUDA kernels to vendor and adapt, rather than a closed vendor library.

## Skip it when

- Production code that needs an API, error handling or cuSPARSE-style alpha/beta semantics: this is a benchmark harness, and call_tilespmv_cuda allocates, times and frees everything in one function.
- When you need the fastest current GPU SpMV: the same lab's tensor-core DASP (SC'23) reports 2.09x average over TileSpMV in FP64 on A100, and CB-SpMV (ICS'25) reports average 3.95x (A100) and 3.06x (RTX 4090) over it (both from search-result text).
- Matrices that change between calls, or a single SpMV: the conversion runs on the CPU plus a setup kernel, and its cost is not measured by the harness.
- Highly irregular matrices with many near-empty tiles. Per the paper's abstract it is not faster than Merge-SpMV on 944 of 2757 matrices, than CSR5 on 717 or than BSR on 1119 (derived from page data: 2757 minus the counts of wins).
- AMD or Intel GPUs, or CPUs: CUDA only.

## How it is fast

The matrix is cut into 16x16 tiles whose intra-tile row and column indices are packed into 4-bit nibbles, so index traffic is a fraction of 32-bit CSR. Each tile gets its own storage format: dense if at least 75% full, COO if it has 12 or fewer nonzeros, dense-row or dense-column when whole rows or columns are full, ELL when the row-length coefficient of variation is at most 0.2, and CSR otherwise (the HYB path is commented out at HEAD). One warp processes a chunk of up to 4 tiles of a tile row, stages the x segment in shared memory and reduces with warp shuffles; long tile rows are split into chunks that merge into y with atomicAdd. The very sparse COO tiles are not handled in the tile loop. At HEAD a one-time setup kernel records their offsets, and the timed kernel processes them in a separate pass at its start. The paper and README instead describe extracting them into a separate matrix, and the repo still builds a CSR5 handle for that matrix.

## Compared with alternatives

Choose TileSpMV over DASP when you have no FP64 tensor cores, or when you want the simpler tile-format-selection design as a research baseline; on A100-class GPUs DASP is reported to be faster. Choose merge-spmv or CSR5 instead when you cannot afford a format conversion, or when you need a kernel with a longer track record across matrix types.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA Toolkit (11.1 tested); CUDA Samples common/inc headers (helper_cuda.h, helper_functions.h, needed by the bundled CSR5 code); OpenMP on the host. CSR5 CUDA (src/external/CSR5_cuda) and a Matrix Market reader are bundled. The README lists cuSPARSE, but the Makefile links only cudart. |
| **Minimum toolchain** | nvcc from CUDA 11.1 (tested), GCC with OpenMP. The FP64 build needs a GPU with compute capability 6.0 or newer because it uses native double atomicAdd (the CAS fallback in the bundled CSR5 utils_cuda.h is commented out). The README's 'compute capability 3.5, Tesla K40' note is out of date. |
| **Platforms** | Linux (Ubuntu 18.04/20.04 tested) with NVIDIA GPUs. The Makefile's -arch=compute_61 -code=sm_86 embeds only sm_86 SASS and no PTX, so you must edit it for A100 (sm_80), Turing, Hopper and other GPUs. |
| **Thread safety** | not documented; the kernels accumulate into y with atomics and the host entry point is a monolithic per-matrix benchmark routine |
| **Drop-in for the baseline** | no |

## Gotchas

- y must be zeroed before every launch. The kernel writes a row only when its sum is nonzero and uses atomicAdd for split tile rows and COO tiles, so FP64 results are not bitwise reproducible from run to run. alpha is passed only to the CSR5 path.
- main.cu rounds the row count down to a multiple of 16 (rowA = (rowA / BLOCK_SIZE) \* BLOCK_SIZE), so up to 15 trailing rows are neither computed nor checked, while GFlops still counts every nonzero. It also overwrites the matrix values and x with i % 10, and the matrix path must be the third argument after '-d N'.
- At HEAD the timed loop has the CSR5 call commented out, but the timed kernel (v6) still computes the very-sparse COO tiles in its separate first pass, so the reported time appears to cover all nonzeros. The CSR5 handle built from the duplicate extracted matrix runs only in the warm-up loops, where it adds those nonzeros a second time. This is my reading of the source; the code was not run.
- Open, unanswered issues: #2 (May 2023) reports an abort in the bundled CSR5 setup at cudaFree(d_scan) on an A100 with rma10; #1 (Jun 2022) reported a missing step.h, which current main.cu no longer includes.

## Known shortcomings

- Raised D to B on the IPDPS 2021 paper's abstract (search snippets only: faster than Merge-SpMV, CSR5 and BSR on most of 2757 SuiteSparse matrices, up to 2.61x / 3.96x / 426.59x on A100 and Titan RTX); the paper itself (ssslab.cn PDF, IEEE, doi.org) was blocked, so average speedups, precision and the cuSPARSE version are unverified. The repo runs no baselines (the embedded CSR5 is part of TileSpMV), and at HEAD the timed loop's CSR5 call for deferred very-sparse nonzeros is commented out, so reported GFlops leave that work out when coototal != 0. Last commit 2022-08-12, abandoned.
- The enricher's source reading contradicts the verifier's CSR5 caveat: the v6 kernel computes the very-sparse COO tiles in a separate first pass (offsets from a one-time v5 kernel), so the timed run seems to cover all nonzeros while CSR5 runs only in warm-up (not run, source only). main.cu rounds rowA down to a multiple of 16, dropping up to 15 trailing rows while GFlops still counts the full nnzA; values and x are overwritten with i%10. The Makefile embeds sm_86 SASS only with no PTX, so no run on A100, Turing or K40 without edits; FP64 needs CC 6.0+; it needs CUDA Samples helper_cuda.h and links only cudart. Issues #1 (missing step.h) and #2 (A100 rma10 abort at a CSR5 cudaFree) open, unanswered. Abstract snippets: beats Merge-SpMV on 1813, CSR5 on 2040 and BSR on 1638 of 2757 matrices.
- Retier check 13 opened the independent CB-SpMV ICS '25 PDF (hpcrl/ICS2025-webpage via raw.githubusercontent.com): its averages put TileSpMV no faster than cuSPARSE 12.4's best-block BSR, about 0.96x on RTX 4090 and 0.76x on A100 (derived from page data). The IPDPS 2021 paper itself stays unopened.

## Caveats and trade-offs

Paper not opened: IEEE, doi.org, ResearchGate, Semantic Scholar and the lab's PDF at ssslab.cn are blocked from this container. Speedups are 'up to' maxima from the abstract, and the 426.59x maximum against BSR is an outlier typical of matrices that do not suit BSR. Precision per figure, average speedups and the cuSPARSE version are unverified. The repo does not reproduce any comparison: src/main.cu checks one TileSpMV run against a CPU CSR reference, and the CSR5 code is part of TileSpMV, not a baseline. In the current HEAD harness (src/tilespmv_cuda.h), the timed loop has the CSR5 call for the extracted very-sparse nonzeros commented out. Reported runtime and GFlops (computed from all nnzA) therefore leave that work out whenever coototal != 0, and the y checked afterwards would lack those contributions. Whether the paper's numbers came from this harness is unknown. The Makefile builds only sm_86 SASS plus compute_61 PTX, a target that matches neither the README's K40 nor the paper's GPUs. Same-lab follow-up DASP (SC'23) reports beating TileSpMV by 2.09x on average in FP64 on A100 (search-result text only), so this is no longer the lab's fastest SpMV. Last commit 2022-08-12. [retier] Independent measurement (Cong, Sun, Chen, Xie, Liu, Qian, 'CB-SpMV', ICS '25, Salt Lake City; opened): on 2843 SuiteSparse matrices in FP64, with CUDA 12.4 and driver 550.135, each kernel was run 1000 times. cuSPARSE v12.4 bsrmv used the best block size of 2x2, 4x4, 8x8 or 16x16 per matrix, and TileSpMV used 16x16 tiles. CB-SpMV averaged 2.95x over cuSPARSE-BSR and 3.06x over TileSpMV on the RTX 4090, and 2.99x over cuSPARSE-BSR and 3.95x over TileSpMV on the A100. That suggests TileSpMV was on average no faster, and on the A100 slower, than best-block-size cuSPARSE BSR on current GPUs. The ratio of those averages, about 0.96x on the RTX 4090 and 0.76x on the A100, is derived from page data and is only indicative, since averages of per-matrix speedups do not divide exactly. The original IPDPS 2021 paper body (average speedups, cuSPARSE version, precision) remains unopened.

NVIDIA GPUs only (compute capability 3.5 or newer). Matrices are first converted to a tiled format (csr2tile), and very sparse tiles are split into a separate matrix; conversion cost and the extra format memory are tradeoffs. Research code driven by a Matrix Market file (./test -d 0 matrix.mtx). Bundles the CSR5 CUDA code under src/external/CSR5_cuda.

## Maintenance

Abandoned: the last commit was 2022-08-12, it has 48 commits, and two issues are open and unanswered. It is Apache-2.0 and small enough to vendor, but expect to rewrite the Makefile targets and the harness before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now B.
- **Tier reason:** Upgraded from D: the README cites the peer-reviewed IPDPS 2021 paper (pp. 68-78, doi 10.1109/IPDPS49936.2021.00016), and two search results quoting its abstract say TileSpMV beats Merge-SpMV, CSR5 and BSR on most of the full SuiteSparse collection with up to 2.61x, 3.96x and 426.59x speedups respectively. The paper itself could not be opened (IEEE, doi.org, ResearchGate and the lab's ssslab.cn PDF are egress-blocked), and the repo harness times only TileSpMV with no baseline runs, so this is B per the precedent for peer-reviewed papers confirmed through abstract snippets, not A.
- **Verifier notes:** I checked the README, src/Makefile, src/main.cu, src/common.h, src/csr2tile.h and src/tilespmv_cuda.h via raw.githubusercontent.com, plus the repo page (Apache-2.0, 13 stars, 4 forks, not a fork, not archived, 48 commits) and the commits page (latest 2022-08-12, so abandoned). License, stars, last commit, usability and compiler flags in the record are correct. An agent with IEEE or ssslab.cn access should confirm average speedups, precision and whether cuSPARSE CSR was a baseline; that could also check for an A-tier artifact.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; independent (snippets): CB-SpMV (ICS '25, xing-cong/CB-Sparse, Apache-2.0) averages 3.95x on A100 and 3.06x on RTX 4090 over TileSpMV; TileSpMSpV (ICPP '22) 1.83x average over TileSpMV; independent: CB-SpMV ICS '25 PDF, TileSpMV vs cuSPARSE 12.4 BSR about 0.96x (RTX 4090) and 0.76x (A100), derived from page data
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/README.md>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV/commits>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/tilespmv_cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/csr2tile.h>
- **Sources the enricher read:**
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV/tree/main/src>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV/issues?q=is%3Aissue>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV/issues/1>
  - <https://github.com/SuperScientificSoftwareLaboratory/TileSpMV/issues/2>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/csr2tile.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/tilespmv_cpu.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/tilespmv_cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/mmio_highlevel.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/mmio.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/step.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/external/CSR5_cuda/anonymouslib_cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/external/CSR5_cuda/detail/utils.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/external/CSR5_cuda/detail/cuda/common_cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/external/CSR5_cuda/detail/cuda/format_cuda.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/TileSpMV/HEAD/src/external/CSR5_cuda/detail/cuda/utils_cuda.h>
  - <https://github.com/xing-cong/CB-Sparse>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/superscientificsoftwarelaboratory/tilespmv`) · [data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_tilespmv.json](../../../data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_tilespmv.json) (enrichment confidence 0.6)

</details>
