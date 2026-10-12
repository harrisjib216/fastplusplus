# spECK (lightweight-analysis GPU SpGEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> CUDA SpGEMM (C = A\*B in CSR) with adaptive hash/dense accumulators; PPoPP '20 reports wins over cuSPARSE and other GPU SpGEMM libraries.

| | |
|---|---|
| **Beats** | cuSPARSE SpGEMM |
| **Claimed result** | PPoPP '20 abstract (search-result quote): outperforms all currently available GPU SpGEMM solutions in 79 percent of cases over all matrices with more than 15k products and is second best in 15 percent, on average 83 percent faster than the second-best approach and up to 25x faster. A later third-party study ('Optimizing General Sparse Matrix-Matrix Multiplication on the GPU', ACM, doi 10.1145/3774654) reportedly gives spECK 5.67x average over cuSPARSE (OpSparse 4.91x, TileSpGEMM 3.47x) (snippet only, not verified here). |
| **Workload** | Sparse general matrix-matrix multiplication (SpGEMM) in CSR on NVIDIA GPUs over a large SuiteSparse-derived matrix set (PPoPP '20 evaluation; matrix count and GPU not seen), compared with other GPU SpGEMM libraries. |
| **Metric** | throughput |
| **Adoption** | 61 stars, 15 commits |
| **Last commit** | 2022-07-29 |
| **Links** | [repository](https://github.com/GPUPeople/spECK) · [benchmark](https://dl.acm.org/doi/10.1145/3332466.3374521) |

## Verdict

Per the PPoPP '20 abstract as seen in search snippets (paper blocked here): over thousands of matrices spECK beat all compared GPU SpGEMM codes (snippets name CUSP, nsparse, RMerge, AC-SpGEMM and bhSPARSE) in 85% of cases and was second in 12%, about 2x the second-best on average and up to 25x; restricted to matrices with more than 15k products, the figures are 79%, 15% and 83% faster. GPU model, CUDA version and how cuSPARSE ranked were not seen, and third-party runs in the OpSparse paper (V100 per its README) put spECK 1.52x behind OpSparse on average.

## Use it when

- Repeated CSR SpGEMM on an NVIDIA GPU where cuSPARSE SpGEMM/csrgemm is the bottleneck, e.g. Galerkin products in algebraic multigrid setup or matrix powers in graph analytics.
- Input sets whose row-length distribution varies widely (power-law and regular matrices mixed), the case the per-call analysis and accumulator choice are designed for.
- float or double data with 32-bit indices and nnz(C) below 2^32.
- As a strong, MIT-licensed baseline when benchmarking a new GPU SpGEMM; OpSparse and TileSpGEMM both measure against it.

## Skip it when

- If you can use OpSparse: its IEEE Access 2022 paper reports OpSparse 1.52x faster than spECK on average, up to 2.04x (per its catalog entry; the OpSparse README gives a V100 with CUDA 11.2), and the OpSparse repo vendors spECK for that comparison.
- AMD, Intel or CPU targets: CUDA only.
- Production code that needs a supported library: master was last touched 2022-07-29 and the cuda11 branch 2023-07-18, CUDA 12 is not mentioned anywhere, and 64-bit index support was added and then removed on the cuda11 branch in January 2022. CornellHPC/Ocean-SpGEMM, partly adapted from spECK per its README, targets CUDA 12.4+ on compute capability 8.0+ (tested on A100 and H100); its speedups were not seen here.
- Workloads that need bitwise reproducible values or proven correctness on unusual inputs: closed issues report wrong values on a small 4x7 by 7x4 product (#4, labelled bug), row-index mismatches against cuSPARSE on webbase-1M on a 1080 Ti (#6), and an illegal memory access on a 2048x2048 matrix with 80% nonzeros (#10, RTX 3060, CUDA 11.6); the issue pages show no maintainer reply, though later commits fix related kernel bugs.

## How it is fast

A lightweight, multi-level analysis: a cheap first kernel counts products per row of C (max and total), and finer per-row analysis and block load balancing run only when those statistics say the cost pays off (hard-coded thresholds in Multiply.cu). Rows are binned into six kernel variants that scale shared memory and threads per block, with up to 32 short rows packed into one block. Each row group gets the cheapest accumulator that fits: direct array indexing when the column range fits the map, a shared-memory hash map with linear probing and atomicCAS, dense accumulation for long rows, or a global-memory hash map fallback. It runs a symbolic (count) pass, then a numeric pass, then CUB segmented sort or in-place sorting of column indices.

## Compared with alternatives

Over cuSPARSE, use it when you can vendor and tune research code for a fixed NVIDIA GPU. Over OpSparse (faster on V100 per its paper) and TileSpGEMM (faster on 94 of 142 large matrices, but no license), pick spECK when you need an MIT-licensed standalone library with float and double, or a reference baseline. Kokkos Kernels SpGEMM is the maintained, portable choice when support matters more than peak speed.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target spECKLib) plus the runspECK benchmark executable; source-drop in practice |
| **Dependencies** | CUDA toolkit (Thrust, CUB); cuSPARSE is linked only by the runspECK driver for transposes and result comparison |
| **Minimum toolchain** | master: CUDA 10.1 or 10.2, g++ &gt; 7 (C++17) or Visual Studio, CMake 3.15.5 per README; CUDA 11+ needs the cuda11 branch (master's harness calls cusparseDcsrgemm, which CUDA 11 removed; cuda11 uses cusparseSpGEMM) |
| **Platforms** | NVIDIA GPUs; CMake options for compute capability 5.0 through 8.6, a 2022 commit restores launch bounds so all kernels run on Pascal; Linux and Windows; a 2020 commit fixes PowerPC builds |
| **Thread safety** | not documented; each call does its own cudaMalloc/cudaFree and uses the streams held in the spECKConfig you pass |
| **Drop-in for the baseline** | partial — same CSR semantics as cuSPARSE SpGEMM, but you wrap your device pointers in spECK's dCSR&lt;T&gt; (unsigned int offsets and column ids) and call its template; no cuSPARSE-compatible API |

## Gotchas

- Per-GPU shared-memory limits are compile-time constants in include/Multiply.h (49152 static; dynamic 49152 pre-Volta, 65536 Turing, 98304 Volta, 101376 RTX 30xx, 166912 A100 per the cuda11 README); wrong values give runtime errors or warnings telling you to recompile.
- Results are not bit-stable: config.ini says values differ from cuSPARSE, so CompareResult checks only row lengths and column indices; a 2023 cuda11 commit restores the value-correctness check.
- CMake builds with -use_fast_math, and master also with -DVERBOSE and -keep/-lineinfo (CUDA_BUILD_INFO on by default).
- Multi-row hash keys pack a 5-bit local row and a 27-bit column into one uint32 (HashMap.cuh masks columns with 0x7FFFFFF), so B with more than 2^27 columns looks unsafe in that path (inferred from code, not documented).

## Known shortcomings

- Evidence is the PPoPP'20 abstract (83% average over second best, up to 25x); a third-party 5.67x figure was not re-verified.
- Closed issues report wrong values (#4, a 4x7 by 7x4 product), a row-index mismatch on webbase-1M (#6) and an illegal memory access on an 80%-dense 2048x2048 (#10), with no visible maintainer reply; not bit-stable against cuSPARSE. master's harness uses cusparseDcsrgemm, which CUDA 11 removed; no CUDA 12 support stated; the cuda11 branch's last commit is 2023-07-18 (master 2022-07-29). The paper's averages and CUDA versions were not seen (tugraz.at blocked); OpSparse's README says its spECK runs used a V100 with CUDA 11.2.

## Caveats and trade-offs

Numbers come from abstract quotes in search results; the PPoPP '20 paper (dl.acm.org, tugraz.at PDF) is blocked here, so GPU, CUDA version and the exact baseline list were not seen, and the quoted abstract does not single out cuSPARSE (the repo's harness checks results against cuSPARSE via externals/cusparse and config.ini CompareResult). Newer peer-reviewed work beats spECK: OpSparse (IEEE Access 2022) reports 1.52x average over spECK, and TileSpGEMM (PPoPP '22) is faster on 94 of 142 large matrices (spECK wins on 48). The 5.67x average over cuSPARSE comes from a third-party snippet the search agent saw and was not re-verified. Builds need per-GPU shared-memory constants set by hand in include/Multiply.h; CUDA 11+ needs the cuda11 branch. Last commit 2022-07-29, which fixed a readOperations kernel bug on matrices whose last row is empty.

CUDA GPU only (CUDA 10.1+; cuda11 branch for CUDA 11+), CMake build; per-device static/dynamic shared-memory sizes must be set by hand in include/Multiply.h; also builds as a library (spECKLib) with an .mtx reader and a config.ini for benchmarking.

## Maintenance

Abandoned (master 2022-07-29, cuda11 branch 2023-07-18, all issues closed) but MIT-licensed and compact enough to vendor; expect to port it yourself for CUDA 12 and newer GPUs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: spECK is a peer-reviewed PPoPP '20 paper (doi 10.1145/3332466.3374521, README bibtex), and a search result quoting its abstract says it outperforms all available GPU SpGEMM solutions in 79 percent of cases over matrices with more than 15k products, on average 83 percent faster than the second-best approach and up to 25x faster. B rests on venue plus abstract per earlier precedents; the paper (dl.acm.org, tugraz.at PDF) is blocked and the repo has a runner (runspECK with config.ini timing) but no results, CPU model or stated flags, so not A.
- **Verifier notes:** Metadata checked: MIT (LICENSE, 2019 Mathias Parger), 61 stars, 15 forks, 15 commits on master, last commit 2022-07-29 (abandoned). spECK is also vendored inside lorentzbf/OpSparse for comparison, which is not a duplicate issue for this entry.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/GPUPeople/spECK>
  - <https://github.com/GPUPeople/spECK/commits>
  - <https://github.com/GPUPeople/spECK/tree/master/externals/cusparse>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/readme.md>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/LICENSE>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/config.ini>
- **Sources the enricher read:**
  - <https://github.com/GPUPeople/spECK>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/readme.md>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/LICENSE>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/config.ini>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/linuxsetup.sh>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/include/Multiply.h>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/include/spECKConfig.h>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/include/dCSR.h>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/include/HashMap.cuh>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/include/GPU/spECK_HashSpGEMM.cuh>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/source/GPU/Multiply.cu>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/source/Executor.cpp>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/master/externals/cusparse/source/cuSparseMultiply.cu>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/cuda11/readme.md>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/cuda11/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GPUPeople/spECK/cuda11/externals/cusparse/source/cuSparseMultiply.cu>
  - <https://github.com/GPUPeople/spECK/issues?q=is%3Aissue>
  - <https://github.com/GPUPeople/spECK/issues/4>
  - <https://github.com/GPUPeople/spECK/issues/5>
  - <https://github.com/GPUPeople/spECK/issues/6>
  - <https://github.com/GPUPeople/spECK/issues/10>
  - <https://github.com/GPUPeople/spECK/issues/11>
  - <https://github.com/GPUPeople/spECK/commits/master>
  - <https://github.com/GPUPeople/spECK/commits/cuda11>
  - <https://github.com/lorentzbf/OpSparse>
  - <https://github.com/CornellHPC/Ocean-SpGEMM>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gpupeople/speck`) · [data/wave8/enrich/raw/github_com_gpupeople_speck.json](../../../data/wave8/enrich/raw/github_com_gpupeople_speck.json) (enrichment confidence 0.6)

</details>
