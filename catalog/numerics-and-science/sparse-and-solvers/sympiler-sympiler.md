# Sympiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Sparse-matrix code generator and kernel library; SC17 Cholesky 3.8x average over Eigen, 1.5x over CHOLMOD on fixed patterns.

| | |
|---|---|
| **Beats** | Eigen sparse (triangular solve, Cholesky); CHOLMOD |
| **Claimed result** | Triangular solve: average 1.49x over Eigen; Cholesky: average speedups over Eigen and CHOLMOD of 3.8x and 1.5x (abstract), up to 6.3x vs Eigen and 2.4x vs CHOLMOD |
| **Workload** | Sparse triangular solve and Cholesky factorization via symbolic-analysis-decoupled code generation |
| **Metric** | throughput |
| **Hardware** | 3.30GHz Intel Core i7-5820K, turbo-boost disabled |
| **Compiler and flags** | GCC 5.4.0 -O3, OpenBLAS 0.2.19, median of 5 runs |
| **Adoption** | 44 stars |
| **Last commit** | 2023-07-12 |
| **Links** | [repository](https://github.com/sympiler/sympiler) · [benchmark](https://www.cs.toronto.edu/~mmehride/papers/SC17.pdf) |

## Verdict

The SC17 paper measures generated code against Eigen and CHOLMOD on 11 SuiteSparse SPD matrices, single core, i7-5820K at 3.3GHz with turbo off, GCC 5.4 -O3 with OpenBLAS 0.2.19, median of 5 runs. Triangular solve averages 1.49x over Eigen. Cholesky averages 3.8x over Eigen (up to 6.3x) and 1.5x over CHOLMOD (up to 2.4x), with symbolic and compile cost excluded.

## Use it when

- Repeated triangular solves or Cholesky refactorizations with the same sparsity pattern and changing values (Newton steps, time stepping, preconditioner re-application)
- Single-core SPD factorization of SuiteSparse-sized matrices (13.7K-1M rows, 0.7-5M nonzeros in the paper) where CHOLMOD is the bottleneck
- Research or prototyping of inspector-executor sparse kernels; the code is MIT-licensed and readable
- When raw CSC/CSR pointer kernels without a matrix class are acceptable

## Skip it when

- Patterns that change every solve: per the paper, inspection plus code generation costs 6-197x a triangular solve and only pays off over many reuses
- LU, QR or unsymmetric direct solves: the paper covers only triangular solve and Cholesky (the library adds IC0, ILU0 and LDL kernels, with no published comparison)
- Production code that needs a maintained, documented API: last commit 2023-07, the code generator README says it is 'under major changes', and the docs site (sympiler.com) now serves a placeholder demo page
- Multicore or distributed Cholesky: the SC17 results are single-core
- Non-x86 Linux builds: CMake hard-codes -march=x86-64 -mavx2 on Linux

## How it is fast

Symbolic analysis (dependency-graph reach for triangular solve, elimination tree for Cholesky) runs once, before the numeric phase. Variable Iteration Space Pruning (VI-Prune) then shrinks the loops to the structurally nonzero work, and 2D Variable-Sized Blocking (VS-Block) groups columns into supernodes so dense BLAS kernels apply. Because loop bounds are known at generation time, it can also unroll, peel, vectorize and tile. The library kernels add level-set and load-balanced level coarsening (LBC) OpenMP schedules for parallel triangular solve.

## Compared with alternatives

Choose Sympiler over BaSpaCho when you are on a CPU, the pattern is fixed, and you want generated or simple single-core supernodal code with an MIT license. Choose it over Ginkgo or AMGCL when you need an exact direct triangular solve or Cholesky rather than an iterative method, and BaSpaCho is the more maintained choice for GPU or multithreaded Cholesky.

## Integration

| | |
|---|---|
| **Form** | static lib (sym_sparse_blas) plus a separate code generator |
| **Dependencies** | BLAS (OpenBLAS default, MKL or Apple Accelerate), METIS, aggregation git submodule; optional OpenMP, TBB, SCOTCH, PAPI; the legacy code_gen needs MKL and SuiteSparse |
| **Minimum toolchain** | C++11; CMake 3.16+ |
| **Platforms** | Linux x86-64 (AVX2 forced by CMake), macOS; CI on Ubuntu and macOS |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The README badge says Apache (copied from micromatch); LICENSE.txt is MIT
- Clone with --recursive, because the aggregation submodule is required
- CMake adds -w, which suppresses all compiler warnings
- Paper benchmarks used GCC 5.4 and OpenBLAS 0.2.19 on a 2014 Haswell-E CPU; there are no recent numbers

## Known shortcomings

- Search record overstated triangular solve (paper: 1.49x over Eigen; the 3.8x/1.5x averages are Cholesky); paper does not link the repo; README Apache badge contradicts MIT LICENSE.txt.
- Code generator README says 'under major changes', needs MKL and SuiteSparse via env vars; sympiler.com is a placeholder; Linux build forces -march=x86-64 -mavx2 and -w; SC17 results single-core and exclude inspection cost (6-197x one triangular solve); newer kernel library (IC0, ILU0, LDL) has no published comparison.

## Caveats and trade-offs

SC17 paper numbers on an i7-5820K with GCC 5.4 -O3; the paper does not link the repo; repo README shows a misleading Apache badge (copied from micromatch) but LICENSE.txt is MIT (Halide-derived); last commit 2023-07-12.

Code generator specialised on a fixed sparsity pattern; needs symbolic inspection phase

## Maintenance

Stale since July 2023 (44 stars, 135 commits) but MIT-licensed. The kernel library is small enough to vendor; the code generator is half-maintained research code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SC17 paper with GCC 5.4.0 -O3, i7-5820K, median of 5 runs, against Eigen and CHOLMOD; benchmark harness for the baselines not confirmed public, so B not A. Verdict is downgrade because the triangular-solve claim was overstated.
- **Verifier notes:** Record claimed 3.8x over Eigen for triangular solve; the paper says 1.49x (the 3.8x/1.5x averages are the abstract's factorization numbers). License found in LICENSE.txt (MIT text), so copyable.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://www.cs.toronto.edu/~mmehride/papers/SC17.pdf>
  - <https://github.com/sympiler/sympiler>
  - <https://github.com/sympiler/sympiler/commits>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/demo/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/demo/sptrsv_demo.cpp>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/code_gen/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/code_gen/README.md>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/sparse_blas/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sympiler/sympiler/HEAD/sparse_blas/sptrsv.cpp>
  - <https://www.cs.toronto.edu/~mmehride/papers/SC17.pdf>
  - <https://www.sympiler.com/docs/sympiler-lib/>
  - <https://github.com/sympiler/sympiler>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sympiler/sympiler`) · [data/wave8/enrich/raw/github_com_sympiler_sympiler.json](../../../data/wave8/enrich/raw/github_com_sympiler_sympiler.json) (enrichment confidence 0.7)

</details>
