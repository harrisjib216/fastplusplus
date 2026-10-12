# merge-spmv (merge-based CsrMV)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Merge-path load-balanced CSR SpMV (SC'16) for CPU and GPU; about 1.2x over MKL on average, wins big on skewed rows.

| | |
|---|---|
| **Beats** | Intel MKL CSR SpMV; NVIDIA cuSPARSE csrmv |
| **Claimed result** | SC'16 paper Fig. 10, 4,201 U.Fl. matrices: CPU merge CsrMV vs MKL CsrMV harmonic-mean 1.21x (max 15.8x, min 0.51x); NUMA variant 1.26x (1.58x on large matrices &gt;6M nnz). GPU vs cuSPARSE CsrMV harmonic-mean 0.84x overall (0.79x small, 1.13x large &gt;300K nnz; max 198x, min 0.34x); vs cuSPARSE HybMV 1.29x. README single-matrix example (circuit5M): MKL 53.62 ms vs merge 12.64 ms, about 4.2x (derived from page data). |
| **Workload** | fp64 CSR SpMV over 4,201 U.Fl. (SuiteSparse) matrices, CPU vs MKL and GPU vs cuSPARSE; README example on circuit5M (5.56M rows, 59.5M nonzeros), 48 threads. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon E5-2690 v2 per paper evaluation section (README/artifact appendix say E5-2695 v2); NVIDIA Tesla K40 |
| **Compiler and flags** | CPU: Intel icpc 16.0.1 with -openmp -O3 -fno-alias -xHost -mkl (Makefile; paper artifact appendix), MKL from Parallel Studio XE 2016; GPU: nvcc 7.5 -O3 with gcc 4.4.7 host, sm_35 |
| **Adoption** | 98 stars |
| **Last commit** | 2017-02-10 |
| **Links** | [repository](https://github.com/dumerrill/merge-spmv) · [benchmark](https://github.com/dumerrill/merge-spmv/raw/master/merge-based-spmv-sc16-preprint.pdf) |

## Verdict

SC'16 paper over 4,201 SuiteSparse matrices, fp64. CPU, built with icpc 16 -O3 -xHost on dual Xeon E5-2690/2695 v2: harmonic-mean 1.21x vs MKL CsrMV (range 0.51-15.8x), 1.26x for the NUMA variant. GPU on a Tesla K40 with CUDA 7.5: 0.84x vs cuSPARSE CsrMV overall (1.13x on matrices above 300K nnz) and 1.29x vs cuSPARSE HybMV.

## Use it when

- fp64/fp32 CSR SpMV on multicore CPUs where row lengths are highly skewed (circuit, web and graph matrices); the README circuit5M run is 53.6 ms with MKL vs 12.6 ms merge on 48 threads
- You need a short, permissively licensed (BSD-3) SpMV kernel to vendor into your own code, with no inspector or format-conversion step
- Matrices change every call, so per-matrix preprocessing (HYB, CSR5 tiles, plan-based libraries) would not amortize
- As a teaching or reference implementation of merge-path decomposition for other segmented reductions

## Skip it when

- Regular, well-balanced matrices (FEM stencils): the paper's minimum is 0.51x vs MKL, and open issue #5 (Dec 2025) reports it 4x slower than plain row-parallel SpMV inside a CG solver on 6 threads
- Small matrices on GPU: harmonic mean 0.79x vs cuSPARSE CsrMV for matrices with 300K nnz or fewer on the K40
- Modern CUDA: the GPU path relies on cub::DeviceSpmv, which CCCL 2.8 deprecates ('Use the cuSPARSE library instead') and which is gone from CCCL 3.0
- If you need a maintained library: no commits since 2017, and the build expects icpc 16 + MKL and CUDA 7.5-era nvcc (open build issues #2 and #3)

## How it is fast

It treats the parallel split as a logical merge of the CSR row-end offsets with the nonzero indices 0..nnz-1. That merge path is cut into equal-length diagonals, one per thread, and each thread binary-searches its start coordinate (MergePathSearch). Every thread gets the same rows+nonzeros work no matter how skewed the row lengths are. Rows that span threads are patched in a carry-out fix-up pass. The gain comes from load balance, not from better memory access per nonzero, so it shows most on power-law or very irregular matrices.

## Compared with alternatives

Pick it over CSR5 when you want to keep plain CSR with zero preprocessing and need a tiny vendorable kernel; CSR5 needs a format transform but reported higher averages on its irregular set. Pick it over ISpMV when you need open source or commercial use, or when the matrix changes too often to amortize a plan.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CPU kernel: OpenMP only (the harness also links MKL and libnuma for comparison); GPU: bundled CUB snapshot, CUDA runtime, cuSPARSE for the comparison |
| **Minimum toolchain** | Tested with icpc 16.0.1 and nvcc 7.5 + gcc 4.4.7; the CPU kernel is plain C++ plus OpenMP |
| **Platforms** | CPU: x86-64 as tested (Intel AVX Xeon); GPU: NVIDIA compute capability 3.5+ |
| **Thread safety** | Not documented; the kernel is a pure function of its inputs with stack-local carry arrays |
| **Drop-in for the baseline** | partial: same CSR input and output as mkl csrmv or cusparse csrmv, but you call the template function directly; there is no MKL- or cuSPARSE-compatible API |

## Gotchas

- The CPU kernel uses fixed row_carry_out[256] and value_carry_out[256] stack arrays, so more than 256 OpenMP threads overflows them
- Merge coordinates and diagonals are int/int2, so rows+nnz must stay below 2^31
- The kernel computes y = A\*x only (no alpha/beta), and the cross-thread fix-up is a serial loop after the parallel region
- The paper names the CPU as Xeon E5-2690 v2 while the README and artifact appendix say E5-2695 v2

## Known shortcomings

- On GPU it averages 0.84x of cuSPARSE CsrMV (a loss); CPU average 1.21x over MKL; last commit 2017 (abandoned); paper and README name different Xeon models.
- Open issue #5 (Dec 2025): 4x slower than row-parallel SpMV inside a CG solver on 6 threads; GPU path uses cub::DeviceSpmv, deprecated in CCCL 2.8 and removed in 3.0; fixed 256-entry carry arrays overflow above 256 threads; int coordinates (rows+nnz &lt; 2^31).

## Caveats and trade-offs

On the GPU it is slower than cuSPARSE CsrMV on harmonic mean (0.84x overall, 0.79x on small matrices); wins only on large or highly irregular matrices. CPU gain over MKL is modest on average (1.21x) with min 0.51x; the 4.2x README figure is one irregular matrix. Very old toolchain and hardware (icc 16, CUDA 7.5, K40). Paper and README disagree on the CPU model (E5-2690v2 vs E5-2695v2). Baselines MKL/cuSPARSE are not on the list. Last commit 2017.

No preprocessing; requires Intel compiler/MKL for CPU path, CUDA cc3.5+ for GPU

## Maintenance

Abandoned since February 2017 but BSD-3 licensed. The CPU kernel is small enough to copy; the GPU path is better taken from its CUB lineage (deprecated in CCCL 2.8, removed in 3.0) or replaced by current cuSPARSE.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded: the peer-reviewed SC'16 paper (preprint in the repo) evaluates the full U.Fl. collection against MKL and cuSPARSE; the benchmark code is public (cpu_spmv.cpp, gpu_spmv.cu, eval_csrmv.sh), the artifact appendix names icc 16.0.1 / nvcc 7.5, the Makefile gives the flags (icpc -openmp -O3 -fno-alias -xHost -mkl; nvcc -O3), and the CPU is named.
- **Verifier notes:** Tier upgraded C to A on the strength of the SC'16 paper plus its artifact appendix and Makefile flags. The original claim (4.2x) is a cherry-picked single-matrix README example; the corrected claim gives the corpus-wide harmonic means, including the GPU loss vs cuSPARSE CsrMV.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** SC'16 paper appendix: icc 16.0.1, -O3 -xHost -fno-alias -mkl
- **Pages the verifier opened:**
  - <https://github.com/dumerrill/merge-spmv>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/README.md>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/LICENSE.TXT>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/merge-based-spmv-sc16-preprint.pdf>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/Makefile>
  - <https://github.com/dumerrill/merge-spmv/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/README.md>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/Makefile>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/cpu_spmv.cpp>
  - <https://raw.githubusercontent.com/dumerrill/merge-spmv/HEAD/gpu_spmv.cu>
  - <https://github.com/dumerrill/merge-spmv/issues>
  - <https://github.com/dumerrill/merge-spmv/issues/5>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/v2.8.0/cub/cub/device/device_spmv.cuh>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/v3.0.0/cub/cub/device/device_spmv.cuh>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dumerrill/merge-spmv`) · [data/wave8/enrich/raw/github_com_dumerrill_merge_spmv.json](../../../data/wave8/enrich/raw/github_com_dumerrill_merge_spmv.json) (enrichment confidence 0.8)

</details>
