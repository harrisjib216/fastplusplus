# CSR5 (Benchmark_SpMV_using_CSR5)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Reference code for CSR5, a tiled CSR variant for SpMV that beat MKL, cuSPARSE, CUSP and pOSKI on irregular matrices in 2015.

| | |
|---|---|
| **Beats** | Intel MKL 11.2, cuSPARSE v6.5, CUSP, ViennaCL, BiCSB, pOSKI |
| **Claimed result** | On 10 irregular matrices, average improvement over the best existing method per platform: 17.6% (dual Xeon CPU, best was pOSKI), 28.5% (GTX 980), 173.0% (R9 290X), 293.3% (Xeon Phi); up to 213.3%, 153.6%, 405.1%, 943.3% |
| **Workload** | SpMV on irregular matrices across CPU, NVIDIA GPU, AMD GPU and Xeon Phi |
| **Metric** | throughput |
| **Hardware** | Dual Xeon E5-2667 v3; GTX 980; Radeon R9 290X; Xeon Phi 5110p |
| **Compiler and flags** | Intel C/C++ 15.0.1 (x86), g++ 4.8.2 (GPU hosts), CUDA 6.5, OpenCL 1.2, OpenMP+AVX2; exact flags not seen |
| **Adoption** | 111 stars |
| **Last commit** | 2020-12-26 |
| **Links** | [repository](https://github.com/bhSPARSE/Benchmark_SpMV_using_CSR5) · [benchmark](https://arxiv.org/pdf/1503.05032) |

## Verdict

Peer-reviewed ICS 2015 paper: in double-precision SpMV on 10 irregular matrices, CSR5 averaged 17.6% over the best prior method on dual Xeon E5-2667 v3 (pOSKI there, not MKL), 28.5% on GTX 980, 173.0% on R9 290X and 293.3% on Xeon Phi 5110p, with peaks of 213.3/153.6/405.1/943.3%. On 14 regular matrices it was 'comparable or better', but MKL had the best CPU average. Compilers were Intel C/C++ 15.0.1, g++ 4.8.2 and CUDA 6.5; the paper gives no flags.

## Use it when

- Repeated double-precision SpMV on irregular matrices (power-law graphs, web, circuit) where row-length skew hurts CSR kernels
- Iterative solvers with tens or more iterations: the paper says conversion costs about as much as a few SpMVs and that CSR5 was the only format beating CSR at 50 iterations
- GPU SpMV (CUDA or OpenCL) where you want one format that copes with both regular and irregular sparsity
- As a reference design to port into your own sparse kernel library under MIT terms

## Skip it when

- Regular, well-balanced matrices on Intel CPUs: the paper says MKL had the best CPU average on the regular set, and on Xeon Phi CSR5 lost to ESB and MKL there
- Single-shot SpMV, where the CSR-&gt;CSR5 conversion is not amortized
- When you need a maintained, packaged library: no commits since Dec 2020, the code is per-platform folders built from Makefiles, and the 2015-era baselines (MKL 11.2, cuSPARSE 6.5) have been improved since
- Single precision on CPU or Phi: the AVX2, KNC and KNL versions support only double; float exists only in the CUDA and OpenCL versions
- Other kernels (SpMM, SpGEMM, transpose-multiply): this repo does SpMV only

## How it is fast

Nonzeros are cut into fixed-size 2D tiles of omega columns (the SIMD or warp width) by sigma rows (chosen from the matrix's average nonzeros per row and the cache). Each tile gets a bit-flag descriptor of row starts, so every SIMD lane does the same amount of work no matter how uneven the row lengths are. Partial row sums are combined with a redesigned segmented sum that is mostly a prefix-sum scan, and a calibrator array fixes rows that span tiles. Load balance comes from the nonzero count, not the row count, so power-law and other irregular matrices do not leave lanes idle.

## Compared with alternatives

Ginkgo is a maintained solver library with its own SpMV formats, so prefer it for production; pick CSR5 when you need to study or port a load-balanced SpMV kernel for irregular matrices. Sympiler and the A64FX CHOLMOD work target direct factorization, not SpMV.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP and AVX2 intrinsics (CPU); CUDA toolkit (CUDA version); OpenCL 1.2 runtime (OpenCL versions); Intel compiler suggested for Phi/KNL |
| **Minimum toolchain** | C++ compiler with OpenMP and AVX2 (Makefile: -O3 -mavx -mavx2 -march=native -fopenmp); README tested Intel C/C++ 2015; CUDA 6.5-era |
| **Platforms** | x86-64 with AVX2; Xeon Phi KNC; KNL AVX-512; NVIDIA GPUs (CUDA/OpenCL); AMD GPUs (OpenCL) |
| **Thread safety** | not documented; the handle stores raw pointers to caller arrays and mutates them, so one handle per matrix and no concurrent use |
| **Drop-in for the baseline** | partial — it takes standard CSR arrays as input, but you must keep a handle, convert, and call its own spmv(alpha, y) instead of mkl_sparse_d_mv or cusparseSpMV |

## Gotchas

- asCSR5() transposes the caller's col_idx and values arrays in place; they are not valid CSR again until you call asCSR() or destroy().
- spmv() returns ANONYMOUSLIB_UNSUPPORTED_CSR_SPMV if the handle has not been converted to CSR5 first.
- The bundled main.cpp times only CSR5 against a single-thread naive loop and checks results with a 1% relative tolerance; it does not rerun the MKL/cuSPARSE comparisons from the paper.
- The README's change log records later fixes to the AVX2 and Phi versions (a small-matrix bug and y-update performance, Jul 2016) and a CUDA timing bug (Apr 2016), all after the ICS 2015 numbers.

## Known shortcomings

- Paper compares against the best other method per platform (pOSKI on CPU), not MKL; no compiler flags; repo benchmark runs only CSR5 with no baseline; abandoned (last commit 2020-12-26).
- CSR5 conversion rearranges the caller's CSR arrays in place; AVX2/Phi/KNL versions double precision only; on regular matrices MKL had the best CPU average and CSR5 lost to ESB and MKL on Xeon Phi; bug fixes in 2016 postdate the ICS 2015 measurements.

## Caveats and trade-offs

ICS 2015 paper with 2015-era baselines; the 'best existing work' differs per platform (pOSKI on CPU, not MKL); paper gives no compiler flags (repo Makefile uses -O3 -mavx2 -march=native -fopenmp); repo benchmark runs CSR5 only; last commit 2020-12-26.

New storage format (conversion cost from CSR); per-platform code folders

## Maintenance

Abandoned since Dec 2020, but MIT-licensed, header-only per platform, and small enough to vendor or port; expect to modernize the CUDA and OpenCL build files and to re-benchmark against current MKL and cuSPARSE before adopting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICS 2015 paper (arXiv 1503.05032) benchmarks CSR5 against MKL, cuSPARSE, CUSP, pOSKI, BiCSB, ViennaCL etc. and states the 17.6/28.5/173.0/293.3% average gains over the best existing method on 10 irregular matrices; compilers and CPU stated but flags not in the paper, and the repo's main.cpp runs only CSR5 (no baseline), so not A.
- **Verifier notes:** Numbers match the abstract exactly. Repo MIT, 111 stars, not archived; last commit Dec 2020 so abandoned.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1503.05032>
  - <https://arxiv.org/pdf/1503.05032>
  - <https://github.com/bhSPARSE/Benchmark_SpMV_using_CSR5>
  - <https://github.com/bhSPARSE/Benchmark_SpMV_using_CSR5/commits>
  - <https://raw.githubusercontent.com/bhSPARSE/Benchmark_SpMV_using_CSR5/HEAD/CSR5_avx2/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bhSPARSE/Benchmark_SpMV_using_CSR5/HEAD/README.md>
  - <https://raw.githubusercontent.com/bhSPARSE/Benchmark_SpMV_using_CSR5/HEAD/CSR5_avx2/Makefile>
  - <https://raw.githubusercontent.com/bhSPARSE/Benchmark_SpMV_using_CSR5/HEAD/CSR5_avx2/main.cpp>
  - <https://raw.githubusercontent.com/bhSPARSE/Benchmark_SpMV_using_CSR5/HEAD/CSR5_avx2/anonymouslib_avx2.h>
  - <https://arxiv.org/abs/1503.05032>
  - <https://arxiv.org/pdf/1503.05032>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bhsparse/benchmark_spmv_using_csr5`) · [data/wave8/enrich/raw/github_com_bhsparse_benchmark_spmv_using_csr5.json](../../../data/wave8/enrich/raw/github_com_bhsparse_benchmark_spmv_using_csr5.json) (enrichment confidence 0.75)

</details>
