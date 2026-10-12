# CB-SpMV / CB-Sparse (xing-cong)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++` · `Apache-2.0` · 🟢 active

> FP64 GPU SpMV on a 16x16 compressed-block format; about 3x faster than cuSPARSE BSR SpMV on SuiteSparse matrices.

| | |
|---|---|
| **Beats** | cuSPARSE BSR SpMV (cusparse_bsrmv, cuSPARSE v12.4); also TileSpMV and DASP |
| **Claimed result** | Paper (ICS '25): over cuSPARSE-BSR average 2.95x (max 37.54x on TSOPF_FS_b39_c30) on RTX 4090 and 2.99x (max 54.27x on boyd1) on A100; over TileSpMV average 3.06x (max 8.56x on piston) on RTX 4090 and 3.95x (max 10.34x on rgg_n_2_21_s0) on A100; over DASP average 2.76x on RTX 4090 and 1.21x on A100. The abstract's 'up to 3.95x' is the A100 TileSpMV average. |
| **Workload** | FP64 SpMV Gflop/s averaged over 2,843 SuiteSparse matrices on A100 and RTX 4090, each kernel run 1000 times; cuSPARSE-BSR uses the best block size from 2x2, 4x4, 8x8 and 16x16. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 (40 GB, 1.56 TB/s) and NVIDIA RTX 4090 (24 GB, 1.01 TB/s); host CPU not stated |
| **Compiler and flags** | Paper: CUDA 12.4, driver 550.135. Repo Makefiles: cb-spmv/src/Makefile uses nvcc -O3 -w -arch=sm_89 -Xcompiler -fopenmp; the cuSPARSE baseline (cb-spmv/benchmark/cuSparse/Makefile) uses nvcc -std=c++14 -O3 -arch=sm_89 with -lcusparse (sm_80 for A100). The README's tested environment is RTX 4090, CUDA 12.4, driver 550.144.03. |
| **Adoption** | 29 stars |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/xing-cong/CB-Sparse) · [benchmark](https://raw.githubusercontent.com/hpcrl/ICS2025-webpage/HEAD/program/Proceedings_ICS25/ics25-7.pdf) |

## Verdict

The ICS '25 paper measures FP64 SpMV Gflop/s over 2,843 SuiteSparse matrices on an A100 and an RTX 4090 with CUDA 12.4: averages of per-matrix speedups are 2.99x and 2.95x over cuSPARSE v12.4 BSR SpMV (best of block sizes 2, 4, 8, 16), 3.95x and 3.06x over TileSpMV, and 1.21x and 2.76x over DASP. The repo ships only the cuSPARSE-BSR harness, not cuSPARSE CSR, TileSpMV or DASP runners, and the host CPU is not stated.

## Use it when

- Repeated FP64 SpMV with the same matrix (iterative solvers, power iterations) on an NVIDIA GPU, where the CPU-side conversion is paid once.
- Irregular matrices with many very sparse 16x16 blocks, where cuSPARSE BSR wastes bandwidth on padded zeros (the paper's largest wins, 37.54x and 54.27x, are such cases).
- Consumer or FP64-weak GPUs such as the RTX 4090, where it beat tensor-core DASP by 2.76x on average in the paper.
- As a reference implementation for a block-based SpMV kernel you will adapt into your own code.

## Skip it when

- You need a library API: there is none, the code is a benchmark driver that reallocates and copies the matrix on every cb_spmv() call.
- A100/H100-class GPUs with strong FP64 tensor cores, where the paper's average edge over DASP is only 1.21x.
- FP32 or mixed precision, or AMD/Intel GPUs or CPUs: ValType is hard-coded to double and the code is CUDA only.
- Matrices that change every call, since the COO-to-block conversion runs on the CPU and the paper reports it as comparable to TileSpMV and BSR conversion for matrices above 1 million nonzeros.
- Matrices beyond 32-bit indexing: nnz, rows and columns are int.

## How it is fast

Intra-block data aggregation: each sub-block's 4-bit row and column indices are packed into one uint8 and stored next to its FP64 values in one contiguous region, which raises L1/L2 hit rates (the paper measures this with Nsight Compute). Adaptive sub-block formats (COO under 32 nonzeros, dense above 128, CSR between, thresholds taken from TileSpMV) avoid BSR's padded zeros. Block-aware column aggregation packs the non-empty columns of super-sparse sub-blocks together so warps stay busy, and an inter-thread-block load-balancing pass redistributes blocks across SMs; partial sums are combined with warp shuffles and atomicAdd into y.

## Compared with alternatives

Pick CB-SpMV over DASP when the GPU has weak FP64 tensor cores (RTX-class) and over TileSpMV for the same 16x16 tiling with better cache locality; prefer merge-spmv, CSR5 or ISpMV when you need to stay in CSR without a conversion step, and DASP on A100-class hardware where the gap is small and DASP has more history.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA Toolkit (nvcc, CUDA runtime; cuSPARSE only for the baseline harness), host C++ compiler with OpenMP |
| **Minimum toolchain** | Tested with CUDA 12.4 and driver 550.144.03; minimum version not documented |
| **Platforms** | NVIDIA GPUs only; Makefiles default to -arch=sm_89 (RTX 4090), change to sm_80 for A100 |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Results are accumulated into y with FP64 atomicAdd, so y must be zeroed before each call and the summation order (and last bits of the result) is nondeterministic run to run.
- The built-in correctness check uses loose tolerances for FP64 (absolute 1e-3, relative 1e-4).
- The repo harness averages over ITER = 10 timed launches after one untimed launch, while the paper says each kernel ran 1000 times, so repo numbers will be noisier than the paper's.
- The program accepts only an absolute path to the .mtx file and uses GPU 0.

## Known shortcomings

- Tier B: the ICS '25 paper (read via raw.githubusercontent.com/hpcrl/ICS2025-webpage) carries every claimed number and the repo has a cuSPARSE-BSR harness with nvcc -O3 flags, but the host CPU is unstated and the TileSpMV and DASP harnesses are not in the repo, so not A.
- No library API: cb_spmv() is a benchmark driver that reallocates, copies and frees the matrix on every call. FP64 hard-coded, int32 indices, atomicAdd into y so results are nondeterministic; the repo times ITER=10 launches where the paper says 1000; the self-check tolerance is loose (abs 1e-3, rel 1e-4). The edge over DASP on A100 is only 1.21x.

## Caveats and trade-offs

Peer-reviewed (ICS 2025). The repo now has the CB-SpMV code and a cuSPARSE-BSR benchmark harness with nvcc flags, but the host CPU is not stated and the TileSpMV and DASP comparison harnesses are not in the repo, so the tier is B rather than A. The cuSPARSE baseline is cusparse_bsrmv (the BSR path, best of 2x2/4x4/8x8/16x16 block sizes), not cuSPARSE CSR SpMV. Averages are of per-matrix speedups, and the large maxima (37.54x, 54.27x) are single matrices where BSR pads sparse blocks badly. The advantage over DASP on A100 is only 1.21x, and DASP's own entry in this catalog was retiered to C on harness and correctness evidence. A later commit (2026-09-02, 'bug fix and opt preprocess') postdates the paper, so numbers may differ from the current code. Not a CPU comparison: SuiteSparse, Eigen and PETSc are not compared.

GPU-only (NVIDIA), needs conversion of CSR into the CB 2D block format (preprocessing cost, extra metadata); CPU-side aggregation of mixed-type data. Only CB-SpMV is released; CB-SpMM and CB-SpGEMM are 'coming soon (under review)'.

## Maintenance

Active (last commit 2026-09-02, a bug fix and preprocessing change that postdates the paper) and Apache-2.0, but small (six commits, no issues filed) and research-grade; CB-SpMM and CB-SpGEMM are announced but not released.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICS '25 paper (ics25-7.pdf, section 4.2.1) compares CB-SpMV against cusparse_bsrmv from cuSPARSE v12.4, TileSpMV and DASP on 2,843 SuiteSparse matrices, and every number in claimed_speedup appears there. The repo now carries the CB-SpMV code and a cuSPARSE-BSR harness (cb-spmv/run/run_cbspmv.sh, run/run_cusparse.sh, benchmark/cuSparse/) with nvcc flags in the Makefiles, but the host CPU is never stated and the TileSpMV/DASP harnesses are not in the repo, so it stays B rather than A.
- **Verifier notes:** I opened the paper PDF via raw.githubusercontent.com/hpcrl/ICS2025-webpage and checked all the speedups in the text. The metadata matches: Apache-2.0, 29 stars, not a fork, last commit 2026-09-02, active. The repo now ships a benchmark harness (added in the 2026-07-04 commit).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier read the ICS '25 PDF; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hpcrl/ICS2025-webpage/HEAD/program/Proceedings_ICS25/ics25-7.pdf>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/README.md>
  - <https://github.com/xing-cong/CB-Sparse>
  - <https://github.com/xing-cong/CB-Sparse/commits>
  - <https://github.com/xing-cong/CB-Sparse/tree/master/cb-spmv>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/Makefile>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/benchmark/cuSparse/Makefile>
- **Sources the enricher read:**
  - <https://github.com/xing-cong/CB-Sparse>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/README.md>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/Code-Guide.md>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/README.md>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/Makefile>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/run/run_cbspmv.sh>
  - <https://github.com/xing-cong/CB-Sparse/tree/master/cb-spmv/src>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/main.cu>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/cb-spmv.cuh>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/coo2block.h>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/format.h>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/macros.h>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/src/utils.h>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/benchmark/cuSparse/main.cu>
  - <https://raw.githubusercontent.com/xing-cong/CB-Sparse/HEAD/cb-spmv/benchmark/cuSparse/Makefile>
  - <https://github.com/xing-cong/CB-Sparse/issues?q=is%3Aissue>
  - <https://github.com/xing-cong/CB-Sparse/commits>
  - <https://raw.githubusercontent.com/hpcrl/ICS2025-webpage/HEAD/program/Proceedings_ICS25/ics25-7.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/xing-cong/cb-sparse`) · [data/wave8/enrich/raw/github_com_xing_cong_cb_sparse.json](../../../data/wave8/enrich/raw/github_com_xing_cong_cb_sparse.json) (enrichment confidence 0.8)

</details>
