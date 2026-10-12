# Spectra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only C++/Eigen implicitly restarted Arnoldi/Lanczos eigensolver; ARPACK redesign, modestly faster than ARPACK-NG in the author's dense tests.

| | |
|---|---|
| **Beats** | ARPACK (ARPACK-NG) |
| **Claimed result** | Performance page bar charts (median elapsed ms over 10 replicates, 10 random dense matrices per size, 10 eigenvalues; values read approximately from the plot images, ratios derived from page data): symmetric solver n=100 Spectra about 0.36-0.50 ms vs ARPACK about 0.53-0.68 ms (about 1.3x-1.5x), n=1000 about 20.5-25.7 ms vs 23.8-29.8 ms (about 1.15x-1.2x); general solver n=100 about 1.3-6.0 ms vs 1.8-9.7 ms (about 1.35x-1.6x), n=1000 about 184-317 ms vs 200-360 ms (about 1.0x-1.25x). Page text: the symmetric solver is uniformly faster than ARPACK in all tested cases and the general solver is almost identical to ARPACK. |
| **Workload** | benchmark/main.cpp: 10 random dense matrices (Eigen MatrixXd::Random; symmetric case A^T + A) of size n=100 (k=10, ncv=20) and n=1000 (k=10, ncv=30), 10 replicates each; Spectra SymEigsSolver/GenEigsSolver with DenseSymMatProd/DenseGenMatProd versus ARPACK's saupd/naupd reverse-communication routines called through the benchmark's F77.cpp and Fortran wrapper; median elapsed time. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-11800H 2.30GHz x 16, 32GB RAM, Solus 4.2 64-bit |
| **Compiler and flags** | Performance page: Clang 11.1.0, clang++ -Wall -O2 -march=native; OpenBLAS 0.3.15 single-threaded; ARPACK-NG 3.7.0 (its build flags not stated). Note the repo's benchmark/Makefile defaults to g++ -Wall -O2 and gfortran -O3 for the ARPACK wrapper. |
| **Adoption** | 866 stars; vcpkg port spectra and Conan recipe spectra exist |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/yixuan/spectra) · [benchmark](https://raw.githubusercontent.com/yixuan/spectra/gh-pages/performance.md) |

## Verdict

Using the repo's benchmark program (10 random dense matrices per size, 10 replicates, k=10, ncv 20/30, tol 1e-10, both sides using the same Eigen mat-vec), Spectra v1.0.0 vs ARPACK-NG 3.7.0 on an Intel Core i7-11800H (Clang 11.1.0 -O2 -march=native, single-threaded OpenBLAS 0.3.15) gave symmetric speedups of about 1.3-1.5x at n=100 and 1.15-1.2x at n=1000. The general solver was about 1.0-1.6x. These figures are read from bar charts.

## Use it when

- C++ code already using Eigen that needs a few extreme eigenpairs of a large sparse or matrix-free operator (spectral clustering, PCA, graph Laplacians, vibration modes) without linking Fortran ARPACK.
- Symmetric problems: the author's benchmark shows the symmetric solver faster than ARPACK-NG in every tested case (about 1.15-1.5x on n=100 and n=1000 random matrices, k=10).
- Matrix-free operators, where you implement perform_op() and never form A.
- Complex Hermitian or complex general matrices (HermEigsSolver, complex GenEigsSolver since 1.1.0/1.2.0) inside a header-only dependency.
- Code that wraps the same engine in R (RSpectra) or Python and wants one C++ core.

## Skip it when

- Shift-and-invert generalized problems with many requested eigenvalues: open issue #165 reports a SymGEigsShiftSolver run with k=128 that did not finish in 10 minutes, where SciPy eigsh (ARPACK) took about 9 s. Open issues #126 and #172 report shift-invert results differing from expected or MATLAB values.
- Large k or full spectra: nev must be at most n-1, and issue #182 asks to lift this limit; use a dense eigensolver (LAPACK/Eigen SelfAdjointEigenSolver) instead.
- Multi-threaded eigensolves: only your operator and Eigen's own kernels can be parallel (multithreading is requested in open issue #185).
- When you need a big speedup over ARPACK: the measured gains are 1.0-1.6x, the general solver is described as almost identical to ARPACK, and the numbers come only from small dense random matrices.
- Clustered or repeated eigenvalues with a tight ncv: open issue #133 reports SymEigsSolver missing one copy of a repeated eigenvalue at k=20, ncv=50, which reappears at k=25.

## How it is fast

It implements the same algorithm as ARPACK: implicitly restarted Arnoldi, or Lanczos for symmetric and Hermitian problems (Lehoucq-Sorensen, ARPACK Users' Guide). The speed comes from C++ templating over Eigen rather than Fortran reverse communication, so the user operator is called inline. It also has its own small-matrix kernels: TridiagQR with a deflation test, a dedicated UpperHessenbergSchur for the projected Hessenberg matrix (SIMD-accelerated in 1.0.1) and Givens-based UpperHessenbergQR. In the benchmark both sides use the same Eigen mat-vec, so the measured gap is the restart and projection machinery alone.

## Compared with alternatives

No other eigensolver is catalogued in this category. Spectra complements the sparse direct solvers listed here (for example CKTSO, BaSpaCho or a CHOLMOD-based operator): one of them can supply the factorization behind a SymEigsShiftSolver operator.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen 3 (header-only; the optional CMake install finds a system Eigen or downloads Eigen 3.4.0 through CPM). Your own sparse factorization (Eigen, CHOLMOD and so on) if you use shift-and-invert. |
| **Minimum toolchain** | C++11 (required since 1.0.0); CMake 3.10+ only for the optional install and tests |
| **Platforms** | any platform Eigen supports; open issue #177 reports ctest failures on Fedora s390x and #139 reports test eigenvalues differing between macOS and Linux |
| **Thread safety** | not documented (each solver object holds its own state; no internal threading beyond Eigen's own) |
| **Drop-in for the baseline** | false — same algorithm and selection rules as ARPACK, but a C++ object API (operator class plus solver object with init/compute/info) instead of ARPACK's Fortran reverse-communication saupd/naupd |

## Gotchas

- The constructor needs nev &lt; ncv &lt;= n, and the docs advise ncv &gt;= 2\*nev. Too small an ncv slows convergence and can miss eigenvalues.
- Always check info() == CompInfo::Successful. compute() returns the number of converged eigenvalues, which can be fewer than requested. Issue #158 reports a silent failure on a 2x2 matrix.
- Version 1.0.0 (2021) broke the API (enum classes, selection rule passed to compute() instead of as a template parameter, operators passed by reference); see MIGRATION.md when updating older code.
- In shift-and-invert mode the selection rule applies to 1/(lambda - sigma), and the quality of your shift-solve operator decides both accuracy and speed.

## Known shortcomings

- Gain only about 1.0-1.6x (read off plot images) on small dense random matrices; repo Makefile says g++ -O2, not the benchmark page's Clang 11.1.0 -O2 -march=native.
- Margins only 1.0-1.6x, measured on small dense random matrices. Open issues: #165 shift-invert generalized solve with k=128 unfinished after 10 min vs SciPy eigsh \~9 s; #133 repeated eigenvalue missed; #126/#172 shift-invert results disputed.

## Caveats and trade-offs

Numbers exist only as bar-chart images on the performance page (spectralib.org/performance.html, served from the gh-pages branch); values here are approximate plot readings. Margins are modest (about 1.0x-1.6x) and were measured with Spectra v1.0.0 (2021). The test matrices are small random dense matrices, so the result says little about large sparse problems where the matrix-vector product dominates. The repo Makefile (g++ -O2) differs from the page's stated clang++ -O2 -march=native, and ARPACK-NG's own build flags are not given. Results depend on the BLAS/LAPACK ARPACK links against. ARPACK is not in the SuiteSparse/Eigen/PETSc baseline list (PETSc users reach it through SLEPc).

Header-only on top of Eigen; matrix-free operators and Eigen sparse matrices; implicitly restarted Arnoldi/Lanczos. Not an ARPACK clone and does not use ARPACK code.

## Maintenance

Active (1.2.0 released 2025-06-29, last commit 2026-07-04, 38 open issues), MPL-2.0 like Eigen, header-only and packaged in vcpkg and Conan, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the performance page source (gh-pages performance.md) names the CPU (Intel Core i7-11800H), compiler and flags (Clang 11.1.0, clang++ -Wall -O2 -march=native), Spectra v1.0.0, ARPACK-NG 3.7.0 and single-threaded OpenBLAS 0.3.15, and its bar charts are produced by the public benchmark program (benchmark/main.cpp, Makefile, F77 wrapper) run against ARPACK.
- **Verifier notes:** spectralib.org is egress-blocked, but the page source is on the repo's gh-pages branch (performance.md plus img/benchmark-sym.png and img/benchmark-gen.png), which I opened and viewed; it confirms the excerpt's environment details. The charts show Spectra faster on every case including the general solver, which the page text calls almost identical (matrix 9 at n=1000 is about equal). Metadata confirmed: MPL-2.0, 866 stars, last commit 2026-07-04.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/performance.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/img/benchmark-sym.png>
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/img/benchmark-gen.png>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/Makefile>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/README.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/LICENSE>
  - <https://github.com/yixuan/spectra>
  - <https://github.com/yixuan/spectra/commits>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/F77.cpp>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/Cpp.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yixuan/spectra/master/README.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/performance.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/index.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/gh-pages/quick-start.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/MIGRATION.md>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/Makefile>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/benchmark/F77.cpp>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/include/Spectra/LinAlg/Lanczos.h>
  - <https://raw.githubusercontent.com/yixuan/spectra/master/include/Spectra/LinAlg/UpperHessenbergQR.h>
  - <https://github.com/yixuan/spectra/blob/master/include/Spectra/SymEigsSolver.h>
  - <https://github.com/yixuan/spectra/issues>
  - <https://github.com/yixuan/spectra/issues/165>
  - <https://github.com/yixuan/spectra/issues/133>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/yixuan/spectra`) · [data/wave8/enrich/raw/github_com_yixuan_spectra.json](../../../data/wave8/enrich/raw/github_com_yixuan_spectra.json) (enrichment confidence 0.8)

</details>
