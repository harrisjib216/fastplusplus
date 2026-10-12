# PIQP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only C++14/Eigen proximal interior-point convex QP solver; fastest and most robust on Maros-Meszaros, well ahead of OSQP.

| | |
|---|---|
| **Beats** | OSQP |
| **Claimed result** | Independent qpbenchmark v2.3.0 (2024-09-07), Maros-Meszaros (138 problems), runtime shifted geometric mean with PIQP = 1.0: OSQP 12.7 (default), 16.1 (high accuracy), 52.8 (low), 51.9 (mid); sparse subset (76 problems): OSQP 9.5 / 17.4 / 30.0 / 56.0. Success rates on the full set: PIQP 95.7 / 73.2 / 97.1 / 94.2% vs OSQP 43.5 / 26.1 / 21.0 / 24.6%. First-party piqp_benchmarks on Maros-Meszaros (shifted geometric means, PIQP = 1.0): OSQP 7.55 at low accuracy (eps_abs 1e-3, eps_rel 1e-4) and 42.66 at high accuracy (eps_abs 1e-8, eps_rel 1e-9). |
| **Workload** | Convex QP solve time on the Maros-Meszaros test set (138 problems; 76-problem sparse subset), shifted geometric mean of runtime over four accuracy settings, run through the qpsolvers Python wrappers. |
| **Metric** | latency |
| **Hardware** | qpbenchmark run: Intel Core i7-6500U @ 2.50GHz (4 logical CPUs). First-party piqp_benchmarks: AMD Ryzen Threadripper 3990X 64-core @ 4.3GHz. |
| **Adoption** | 149 stars; PyPI package piqp |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/PREDICT-EPFL/piqp) · [benchmark](https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md) |

## Verdict

The independent qpbenchmark v2.3.0 (2024-09-07, i7-6500U laptop, prebuilt wheels through qpsolvers 4.3.3: piqp 0.4.1, osqp 0.6.7.post0) ran 138 Maros-Meszaros problems and ranked PIQP first at every setting. OSQP's shifted geometric mean runtime was 12.7x (default), 16.1x (high accuracy), 52.8x (low) and 51.9x (mid) PIQP's, with failures counted at the 1000 s limit, so the ratios mix speed with OSQP's 21-44% success rate. PIQP's own piqp_benchmarks on a Threadripper 3990X give OSQP 7.55x (low accuracy) and 42.66x (high accuracy).

## Use it when

- Small-to-medium convex QPs that must be solved to 1e-6 to 1e-9 accuracy, where OSQP often stalls (qpbenchmark high accuracy: PIQP solved 73% of Maros-Meszaros vs OSQP 26%)
- Hard or ill-conditioned problems with degenerate or dependent constraints: PIQP solved 94-97% of the 138 problems at low, mid and default accuracy
- Model predictive control and other repeated solves with fixed sparsity: update() re-solves without allocating, and the sparse_multistage backend exploits stage structure
- Embedding in C++ code that already uses Eigen (header-only, BSD-2 core), or in Python, Matlab, Octave or R through prebuilt packages

## Skip it when

- Very large sparse QPs where one KKT factorization is too costly in memory or time; first-order methods such as OSQP or SCS only need matrix-vector products and a cheaper factorization
- Fast warm-started low-accuracy MPC loops are OSQP's home ground; this catalog has no matched warm-start comparison
- Nonconvex QPs, mixed-integer or conic (SOCP/SDP) problems are out of scope; use Clarabel, MOSEK or Gurobi
- Code paths that enable preconditioner_scale_cost with bounds near zero: open issue #37 (v0.6.1-0.6.2) reports false PRIMAL_INFEASIBLE results on feasible problems
- Strict BSD-only licensing needs: the sparse backend is derived from SuiteSparse LDL, whose LGPL-2.1+ notice ships next to it

## How it is fast

It combines an infeasible primal-dual interior-point method with the proximal method of multipliers (an adaptation of Pougkakiotis and Gondzio), so it converges in a few dozen Newton steps to tight tolerances and tolerates rank-deficient constraints and ill-conditioning, where the ADMM in OSQP needs many cheap iterations and stalls at high accuracy. Each step solves a regularized KKT system with a modified SuiteSparse LDL (sparse, AMD ordering), a dense Cholesky, or a Blasfeo-based multistage backend for MPC-structured problems, with Ruiz equilibration and iterative refinement. Most of the speed ratio comes from far fewer failed or stalled solves rather than from cheaper iterations.

## Compared with alternatives

Against ProxQP (ProxSuite) and QPALM, the other OSQP-beaters here, PIQP leads both runtime and success rate on Maros-Meszaros in the independent qpbenchmark (ProxQP 5.9-53x and QPALM 2.2-4.8x slower by shifted geometric mean). Choose ProxQP for dense, robotics-style QPs, where its own benchmark is strongest.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen &gt;= 3.3 (Eigen 5 supported since 0.6.3); optional Blasfeo for the sparse_multistage backend; optional OpenMP; pybind11 and cpu_features for the Python bindings |
| **Minimum toolchain** | C++14 (C++17 if built with std::optional or std::filesystem), CMake 3.21+ for the CMake build |
| **Platforms** | any platform Eigen supports; PyPI wheels for Linux x86-64/aarch64/i686 (glibc and musl), macOS x86-64/arm64 and Windows x64 |
| **Thread safety** | not documented; each solver is a self-contained object, and OpenMP parallelism is opt-in (BUILD_WITH_OPENMP=OFF by default) |
| **Drop-in for the baseline** | no |

## Gotchas

- Default tolerances are tight (eps_abs 1e-8, eps_rel 1e-9, duality-gap check on) against OSQP's 1e-3, so comparisons at default settings compare different accuracy targets
- Versions before 0.6.4 (released 2026-08-28) have an out-of-bounds read in inequality dual recovery (#42) that caused intermittent PIQP_MAX_ITER_REACHED on identical inputs; 0.6.0 also brought a segfault report (#31) and new PRIMAL_INFEASIBLE results (#33), both closed, so pin 0.6.4 or later
- The default KKT solver is dense_cholesky; sparse problems need SparseSolver or one of the sparse_ldlt\* backends
- BUILD_WITH_EIGEN_MAX_ALIGN_BYTES and template-instantiation options affect Eigen ABI compatibility when you link the prebuilt library into code built with different Eigen alignment

## Known shortcomings

- QP solver measured against OSQP, which is off the sparse-and-solvers baseline list (no optimization category in wave 8).
- Bug #42: out-of-bounds read in dual recovery, fixed only in 0.6.4 (2026-08-28). Open #37: false PRIMAL_INFEASIBLE with preconditioner_scale_cost. Sparse LDL is derived from SuiteSparse LDL; an LGPL-2.1+ notice ships beside the BSD-2 header. qpbenchmark ratios count failures at 1000 s, so they mix speed with robustness (OSQP 21-44% success).

## Caveats and trade-offs

Category fit is loose: PIQP is a convex QP optimization solver (header-only C++14 on Eigen), not a sparse linear-system solver, and OSQP is not in the SuiteSparse/Eigen/PETSc baseline list; there is no optimization-solver category in this wave. The qpbenchmark run used prebuilt Python wheels (piqp 0.4.1, osqp 0.6.7.post0, qpsolvers 4.3.3, Python 3.12), so no compiler or flags apply, runtimes include a sliver of wrapper time, and the versions are two years old (PIQP is now 0.6.x). The suite's known limitations include CPU thermal throttling (issue 88) on a 2-core laptop CPU. Only solves that return no solution are counted at the 1000 s time limit (qpbenchmark/results.py not_found_value); solutions returned as solved but failing the tolerance check keep their measured runtime. Rankings depend on the suite: ProxQP's own benchmark (different problem classes) shows ProxQP ahead of OSQP instead.

Convex QPs only. Header-only C++14 built on Eigen, with dense, sparse and multistage backends; C/C++, Python, Matlab/Octave and R interfaces. Proximal interior-point method, so it needs sparse/dense LDL factorizations per iteration.

## Maintenance

Actively maintained (0.6.4 released 2026-08-28, 580 commits, 149 stars, on PyPI and conda-forge) and BSD-2-licensed, so it is safe to adopt; pin 0.6.4 or later for the memory-safety fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (qpsolvers/qpbenchmark v2.3.0, run by its maintainer on a stated i7-6500U, public harness, solver versions listed) shows PIQP ahead of OSQP on runtime shifted geometric mean at all four settings with a 73-97% success rate; it runs prebuilt Python wheels, so no compiler or flags exist and it falls short of A. Also backed by the peer-reviewed CDC 2023 paper (doi 10.1109/CDC49753.2023.10383915) cited in the README.
- **Verifier notes:** All qpbenchmark numbers match results/maros_meszaros.md and maros_meszaros_sparse.md; piqp_benchmarks numbers and Threadripper 3990X match its README. Repo: BSD-2-Clause, 149 stars, 23 forks, not a fork, latest commit 2026-08-28 ('prepare 0.6.4 release'). Category: QP solver compared with OSQP, off the sparse-and-solvers baseline list.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros_sparse.md>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/main/README.md>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/main/qpbenchmark/results.py>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/README.md>
  - <https://github.com/PREDICT-EPFL/piqp>
  - <https://github.com/PREDICT-EPFL/piqp/commits>
  - <https://github.com/PREDICT-EPFL/piqp_benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/README.md>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/include/piqp/settings.hpp>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/include/piqp/solver.hpp>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/include/piqp/sparse/ldlt.hpp>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/include/piqp/sparse/LDL_License.txt>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp/HEAD/include/piqp/sparse/ordering.hpp>
  - <https://github.com/PREDICT-EPFL/piqp>
  - <https://github.com/PREDICT-EPFL/piqp/tree/main/include/piqp>
  - <https://github.com/PREDICT-EPFL/piqp/tree/main/include/piqp/sparse>
  - <https://github.com/PREDICT-EPFL/piqp/issues?q=is%3Aissue>
  - <https://github.com/PREDICT-EPFL/piqp/issues/42>
  - <https://github.com/PREDICT-EPFL/piqp/issues/37>
  - <https://raw.githubusercontent.com/PREDICT-EPFL/piqp_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md>
  - <https://pypi.org/pypi/piqp/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/predict-epfl/piqp`) · [data/wave8/enrich/raw/github_com_predict_epfl_piqp.json](../../../data/wave8/enrich/raw/github_com_predict_epfl_piqp.json) (enrichment confidence 0.85)

</details>
