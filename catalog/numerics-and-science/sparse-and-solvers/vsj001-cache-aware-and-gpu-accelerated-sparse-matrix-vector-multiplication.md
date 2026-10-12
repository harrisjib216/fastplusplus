# Cache-Aware and GPU-Accelerated SpMV (VSJ001)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🟢 active

> Coursework-scale CUDA CSR-vector SpMV kernel (one warp per row) that edges out cuSPARSE CSR_ALG2 on three regular SuiteSparse matrices.

| | |
|---|---|
| **Beats** | cuSPARSE SpMV (CSR_ALG2) |
| **Claimed result** | 'beats NVIDIA's cuSPARSE library by 24-56 percent on regular real-world matrices': cant 1531 vs 1172 GB/s (+30.6%), consph 1557 vs 1252 GB/s (+24.4%), pdb1HYS 1718 vs 1102 GB/s (+55.8%); cuSPARSE wins on webbase-1M (847 vs 203 GB/s). |
| **Workload** | CSR SpMV effective memory bandwidth (GB/s) of a hand-written one-warp-per-row CUDA kernel versus cuSPARSE on four SuiteSparse matrices (cant, consph, pdb1HYS, webbase-1M) on an A100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 80GB (README also quotes a 1555 GB/s HBM2 peak) on the Northeastern University Explorer cluster; Intel Xeon Gold host CPUs |
| **Compiler and flags** | src/Makefile: nvcc (CUDA 12.3 per README) -O3 -arch=sm_80 -lineinfo -std=c++14 --ptxas-options=-v -Xcompiler -O3, linked with -lcusparse -lcublas; CPU build gcc -O3 -march=native -ftree-vectorize. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-05-08 |
| **Links** | [repository](https://github.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication) · [benchmark](https://github.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication) |

## Verdict

On one A100 (CUDA 12.3, nvcc -O3 -arch=sm_80), the hand-written CSR-vector kernel ran double-precision SpMV in 0.053, 0.078 and 0.051 ms on cant, consph and pdb1HYS versus 0.069, 0.097 and 0.079 ms for cuSPARSE CSR_ALG2 called through a freshly created handle each time (24-56 percent higher effective bandwidth), while cuSPARSE was about 4.2x faster on webbase-1M; all numbers come from the author's committed results/gpu/timings.csv.

## Use it when

- Learning or teaching GPU SpMV: a compact, readable side-by-side of CSR scalar, CSR vector, ELL and cuSPARSE with a roofline script and committed A100 results.
- FEM or structural matrices with fairly uniform, moderately long rows (tens of nonzeros per row) where a plain warp-per-row kernel is enough and you want no library dependency.
- As a starting point for your own fused SpMV (for example inside an iterative solver loop) where launching a cuSPARSE call per iteration is not wanted.
- Double precision, 32-bit indices, matrices that fit on one GPU (tested on A100 sm_80; Makefile also targets sm_70 and sm_90).

## Skip it when

- Power-law or web-graph matrices: on webbase-1M cuSPARSE is about 4.2x faster (0.087 vs 0.365 ms), because the kernel has no load balancing for heavy-tailed rows.
- Very short rows (about 1-5 nnz per row): on the committed 50K and 100K-row synthetic matrices the vector kernel takes 0.016-0.032 ms while the scalar and ELL kernels take 0.007-0.017 ms, since one warp per row idles most lanes.
- Production code: no LICENSE file (all rights reserved by default), 4 commits, 0 stars, no tests beyond a --validate max-abs-error print, so it can only be read as a reference.
- Anything needing float, complex, transposed SpMV, alpha/beta scaling, 64-bit indices or multiple right-hand sides; none are implemented.
- When you need a decision-grade comparison: only one cuSPARSE algorithm (CSR_ALG2) was tried, on one GPU, with four real matrices.

## How it is fast

The CSR-vector kernel assigns one 32-thread warp per row, so the lanes stride through a row's nonzeros with coalesced loads of values and col_idx, then combine partial sums with a __shfl_down_sync warp-shuffle tree reduction (block of 128 threads, 4 rows per block). This is the classic Bell and Garland CSR-vector scheme; it pays off when rows hold tens of nonzeros (cant, consph and pdb1HYS average about 64-119 nnz per row, derived from page data). There is no load balancing, no row binning and no adaptive selection between scalar and vector inside the kernel; the harness only decides whether to skip ELL.

## Compared with alternatives

Pick it only to read a minimal warp-per-row CUDA CSR kernel; for real GPU SpMV, ISpMV (2.17x geomean over cuSPARSE ALG2 on an H100, preprocessing excluded) or merge-spmv/CSR5 (load-balanced, peer-reviewed, robust on irregular matrices) are the better choices, and on CPUs CVR, SPC5 or ALBUS target MKL instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit 12.x (tested with nvcc 12.3), cuSPARSE and cuBLAS linked by the Makefile; gcc for the CPU kernels |
| **Minimum toolchain** | nvcc 12.x with -std=c++14; GPU sm_70 or newer per the Makefile options (sm_80 default) |
| **Platforms** | NVIDIA GPUs (A100 tested; V100 and H100 build targets); CPU kernels need x86-64 with AVX2 |
| **Thread safety** | not documented; each launcher uses the default stream and synchronizes on its own events |
| **Drop-in for the baseline** | partial — the vector kernel takes the same zero-based int32 CSR device arrays that cusparseCreateCsr wraps, but it only computes y = A\*x (no alpha/beta, no transpose, double only) and has no cuSPARSE-style handle or descriptor API |

## Gotchas

- Reported GB/s counts every x[col] read as DRAM traffic, so figures above 100 percent of peak (pdb1HYS 1718 GB/s) reflect L2 reuse of x, as the README itself notes; the CSR arrays alone are about 48-72 MB per matrix (derived from page data).
- The README pairs 'A100 80GB' with a 1555 GB/s peak, which is the A100 40GB figure; per vendor specs quoted in search results the 80GB SXM part is rated about 2039 GB/s, so the '98-110 percent of peak' framing is likely overstated if the card really was the 80GB model.
- The cuSPARSE wrapper creates a new handle, CSR and vector descriptors and a workspace buffer on every call and times only the cusparseSpMV call; nothing is reused across iterations, and cuSPARSE takes about 0.021-0.036 ms even on the tiny synthetic matrices, so part of the 24-56 percent margin may be per-call cuSPARSE overhead rather than kernel efficiency.
- The cuSPARSE launcher casts nnz to int and all index arrays are int32, so matrices above 2^31 nonzeros are out of scope; the committed run scripts use --iters 20 (the README's CLI default is 10), with one untimed warm-up.

## Known shortcomings

- Each timed cuSPARSE CSR_ALG2 call recreates the handle and descriptors; cuSPARSE's floor is \~0.021-0.025 ms on tiny matrices while the gaps on real matrices are 0.016-0.028 ms (derived), so much of the 24-56% win may be per-call overhead; no license (reference only).
- README pairs 'A100 80GB' with a 1555 GB/s peak, the 40GB card's figure (the 80GB SXM is \~2039 GB/s), so '98-110% of peak' is overstated. cuSPARSE wrapper creates a new handle on every call (penalizes the baseline). Committed run scripts use --iters 20, not 10. Vector kernel loses to the scalar and ELL kernels on short rows. No licence.

## Caveats and trade-offs

Coursework-style project with four real matrices, one A100 run, 1 warm-up plus 10 timed single-call iterations. Bandwidth figures use a formula that counts every x[col] read as DRAM traffic, which is why they exceed the 1555 GB/s peak (98-110 percent); the CSR arrays themselves are about 48-72 MB (derived from page data), so this is x-vector reuse in L2, not the whole matrix fitting in cache. Only cuSPARSE CSR_ALG2 was compared, and each timed cuSPARSE call uses a freshly created handle and descriptors with no reuse or preprocessing. In results/gpu/timings.csv cuSPARSE takes about 0.021-0.025 ms on the 10K-row synthetic matrices where the custom kernels take about 0.007-0.010 ms, and the absolute gaps on cant, consph and pdb1HYS are 0.016, 0.019 and 0.028 ms (derived from page data), so much of the 24-56 percent win may be cuSPARSE per-call overhead rather than kernel efficiency. cuSPARSE is 4.2x faster on webbase-1M. No LICENSE file, so reference only.

Simple CSR-vector kernel (one warp per row, warp-shuffle reduction) with an ELL variant and a selector that skips ELL on irregular rows; CPU side adds cache tiling and AVX2 with software prefetching. Loses to cuSPARSE on irregular web-graph matrices.

## Maintenance

Single-author coursework-style repository (4 commits, all 2026-05-08, 0 stars) with no license, so it is reference-only and cannot be vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness (src/gpu/bench_gpu.cu, src/gpu/spmv_cusparse.cu, scripts/run_gpu.sh) with committed results (results/gpu/timings.csv), compiler and flags in src/Makefile (nvcc 12.3, -O3 -arch=sm_80 -std=c++14 -Xcompiler -O3) and the GPU named (A100 80GB), so it meets A as a reproducible first-party run against cuSPARSE; the README table numbers match the CSV.
- **Verifier notes:** README table matches results/gpu/timings.csv exactly (e.g. cant 0.052838 ms vector vs 0.069018 ms cuSPARSE). Tier A holds on the reproducibility rule, but the cuSPARSE timing setup is a fairness shortcoming worth recording. Metadata: no license file (LICENSE 404, none shown on github.com), 0 stars, 4 commits all on 2026-05-08 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication>
  - <https://github.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/commits>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/README.md>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/Makefile>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/results/gpu/timings.csv>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/results/gpu/roofline.txt>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/spmv_cusparse.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/spmv_csr_vector.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/bench_gpu.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/gpu_utils.h>
- **Sources the enricher read:**
  - <https://github.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/README.md>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/Makefile>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/spmv_csr_vector.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/spmv_cusparse.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/bench_gpu.cu>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/gpu_utils.h>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/spmv_kernels.h>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/gpu/mtx_loader.cpp>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/src/csr.h>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/scripts/run_gpu.sh>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/scripts/run_all.sh>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/data/suitesparse/README.md>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/results/gpu/timings.csv>
  - <https://raw.githubusercontent.com/VSJ001/Cache-Aware-and-GPU-Accelerated-Sparse-Matrix-Vector-Multiplication/HEAD/results/gpu/roofline.txt>
  - WebSearch: NVIDIA A100 80GB memory bandwidth 2039 GB/s vs A100 40GB 1555 GB/s (snippets from nvidia.com/en-us/data-center/a100 and third-party spec pages)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/vsj001/cache-aware-and-gpu-accelerated-sparse-matrix-vector-multiplication`) · [data/wave8/enrich/raw/github_com_vsj001_cache_aware_and_gpu_accelerated_sparse_matrix_vector_multiplication.json](../../../data/wave8/enrich/raw/github_com_vsj001_cache_aware_and_gpu_accelerated_sparse_matrix_vector_multiplication.json) (enrichment confidence 0.8)

</details>
