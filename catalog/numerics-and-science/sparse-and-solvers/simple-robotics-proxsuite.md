# ProxQP (ProxSuite)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only C++ QP solver (ProxQP) on Eigen; 3.5-18x lower shifted-geomean solve time than OSQP on random QPs.

| | |
|---|---|
| **Beats** | OSQP (also compared against Gurobi, MOSEK, qpOASES, quadprog) |
| **Claimed result** | First-party proxqp_benchmark, shifted geometric means with PROXQP = 1.0, high accuracy: dense random QPs OSQP 18.2, qpOASES 282.6, quadprog 20.4; sparse (\~15%) random QPs OSQP 3.5, qpOASES 260.6, quadprog 19.3; Maros-Meszaros OSQP 14.2, qpOASES 4.5, Gurobi 114.2 (low accuracy 1e-3: OSQP 108.5, qpOASES 17.1). |
| **Workload** | Randomly generated dense and sparse (about 15% density) convex QPs and the hard Maros-Meszaros problems, shifted geometric mean of solve time at high accuracy (eps 1e-9) and low accuracy (1e-3). |
| **Metric** | latency |
| **Hardware** | 11th Gen Intel Core i7-11850H @ 2.50GHz |
| **Adoption** | 594 stars; vcpkg port proxsuite; PyPI proxsuite |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/Simple-Robotics/proxsuite) · [benchmark](https://github.com/Simple-Robotics/proxqp_benchmark) |

## Verdict

The project's own proxqp_benchmark (dense backend, i7-11850H, compiler, flags and solver versions unstated) reports shifted geometric means at 1e-9 accuracy with ProxQP = 1.0: OSQP 18.2 on dense random QPs, 3.5 on random QPs of about 15% density, and 14.2 on Maros-Meszaros (108.5 at 1e-3). The independent qpbenchmark run (i7-6500U, proxqp 0.6.6 vs osqp 0.6.7.post0 called through qpsolvers) has ProxQP ahead of OSQP at high, mid and low accuracy (5.9 vs 16.1, 19.2 vs 51.9, 36.0 vs 52.8) but behind at default settings (53.3 vs 12.7).

## Use it when

- Small to medium dense QPs, solved repeatedly. The docs recommend the dense backend below a few thousand variables or above 0.1 matrix density; robotics MPC and inverse dynamics (TSID) are typical.
- High-accuracy solutions (1e-6 to 1e-9). In the independent qpbenchmark Maros-Meszaros run, ProxQP scored 5.9 vs OSQP's 16.1 runtime shifted geomean at 1e-9, with a 52.9% vs 26.1% success rate.
- Sequences of closely related QPs (MPC, control loops): the default WARM_START_WITH_PREVIOUS_RESULT mode reuses the previous iterates and factorization.
- Problems that may be infeasible, where the closest feasible solution is useful, and QP layers in PyTorch that need derivatives (QPLayer).
- C++ code already built on Eigen, or Python users who want `pip`/`conda` installs and CVXPY/CasADi integration.

## Skip it when

- Hard sparse QPs when PIQP or QPALM is available. On qpbenchmark Maros-Meszaros, PIQP is fastest at every accuracy (1.0 vs ProxQP's 5.9-53.3) with a higher success rate, and QPALM's runtime shifted geomean (2.2-4.8) also beats ProxQP's.
- Loose default-tolerance runs: on qpbenchmark default settings ProxQP's runtime shifted geomean is 53.3 vs OSQP's 12.7.
- Larger sparse MPC. One user (issue #227, 9 states per stage) found OSQP about 1.7x faster at horizon 70+, although ProxQP was faster at horizon 25 (1.1 vs 1.6 ms).
- Sparse problems whose sparsity pattern changes between solves: a sparse `update` only works for an identical pattern, otherwise you must build a new QP object.
- Hard real-time loops that need a guaranteed allocation-free solve: issues #103 and #200 about memory allocations are still open, and which calls allocate is not documented.

## How it is fast

ProxQP is a proximal method of multipliers. Each outer step minimizes a primal-dual augmented Lagrangian merit function with a semismooth Newton method, and penalty parameters follow a BCL (bound-constrained Lagrangian) update rule. When penalties or the active set change, the dense backend updates its LDL^T factorization with rank-r updates instead of refactorizing. It factors either the regularized KKT matrix (PrimalDualLDLT) or H + rho I + A'A/mu_eq (PrimalLDLT, quicker when constraints far outnumber variables), after Ruiz equilibration. Warm starts keep the factorization between solves, and the linear algebra is vectorized through SIMDe (AVX2/AVX-512) when built with -march=native; the paper benchmarks used AVX2.

## Compared with alternatives

PIQP and QPALM also beat OSQP in qpbenchmark, and PIQP is faster and more robust on hard sparse Maros-Meszaros problems at every accuracy, so prefer PIQP there. Pick ProxQP for small dense QPs re-solved with warm starts (robotics MPC, whole-body control), or when you need its box-constraint handling, closest-feasible solving, nonconvex regularization or QPLayer differentiation.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen &gt;= 3.0.5; optional SIMDe (vectorization, on by default in the CMake build), OpenMP (parallel batch solves), nanobind and cereal (Python bindings), Matio (tests) |
| **Minimum toolchain** | C++14 minimum (CMake enforces 14, README says C++14/17/20); defaults to C++17, which the install doc lists as required; CMake build |
| **Platforms** | Linux, macOS and Windows (CI plus pip, conda-forge and Homebrew packages); x86 AVX2/AVX-512 through SIMDe when compiled with -march=native; vectorization can be switched off for other CPUs |
| **Thread safety** | not documented for one QP object; separate QPs can be solved in parallel through the OpenMP batch solver (solve_in_parallel) or from Python threads with solve_no_gil (dense backend) |
| **Drop-in for the baseline** | partial — it handles the same convex QP class as OSQP and can stand in for it as a CVXPY, CasADi or qpsolvers backend, but the native API, the problem layout (separate equality and inequality matrices) and the settings all differ |

## Gotchas

- SIMD speed needs the vectorized build (CMake target proxsuite::proxsuite-vectorized or -DPROXSUITE_VECTORIZE) plus -march=native in your own compile flags. The docs name the CMake switch inconsistently: BUILD_WITH_VECTORIZATION_SUPPORT in the install guide, BUILD_WITH_SIMD_SUPPORT in the API doc.
- The default initial guess is WARM_START_WITH_PREVIOUS_RESULT, so a re-solve on the same object starts from the previous iterates, proximal parameters and factorization unless you change `settings.initial_guess`.
- The dense backend picks PrimalDualLDLT or PrimalLDLT by a complexity heuristic, and PrimalLDLT is documented as less accurate. For very ill-conditioned problems at tight tolerances, undoing the Ruiz scaling can lose precision.
- Issue #63, a termination problem on the Maros-Meszaros problem QGFRDXPN, is still open.

## Known shortcomings

- QP solver whose baseline (OSQP) is not a category incumbent; independent qpbenchmark Maros-Meszaros shows it faster than OSQP at high/mid/low accuracy but slower at default settings (53.3 vs 12.7); RSS 2022 paper unreadable here.
- Independent qpbenchmark has PIQP faster than ProxQP at every accuracy (1.0 vs 5.9-53.3) and QPALM faster too. User issue #227: OSQP 1.7x faster on a larger sparse MPC. Open termination bug #63. QP solver, a loose fit for the sparse-and-solvers category.

## Caveats and trade-offs

The headline numbers are first-party (proxqp_benchmark, i7-11850H, no compiler, flags or solver versions) and cover the dense ProxQP backend only; the RSS 2022 paper is peer reviewed but could not be opened from this container. The independent qpbenchmark Maros-Meszaros report (i7-6500U, 2024-09-07, proxqp 0.6.6, osqp 0.6.7.post0) is mixed: at default settings ProxQP is slower (runtime shifted geometric mean 53.3 vs OSQP 12.7) but it is faster at high accuracy (5.9 vs 16.1), mid (19.2 vs 51.9) and low accuracy (36.0 vs 52.8), and its success rate is higher (73.2% vs 43.5% at default). Category fit is loose (QP optimization, not linear-system solving) and OSQP is not in the SuiteSparse/Eigen/PETSc list.

Dense and sparse backends, Eigen-based, vectorized and allocation-free updates, Python bindings; targets robotics (MPC) use. Convex QPs.

## Maintenance

Actively maintained by Inria and LAAS-CNRS (594 stars, release 0.7.3 on 2026-05-11, commits through 2026-09-14). BSD-2-Clause and packaged for pip, conda-forge, Homebrew and vcpkg.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the first-party proxqp_benchmark README numbers match, and the win over OSQP is backed by the peer-reviewed RSS 2022 paper (PROX-QP, Bambade et al.; page itself blocked here, known from search snippet) and by the independent qpbenchmark Maros-Meszaros report (i7-6500U, proxqp 0.6.6 vs osqp 0.6.7.post0), where ProxQP's runtime shifted geometric mean beats OSQP at high (5.9 vs 16.1), mid (19.2 vs 51.9) and low (36.0 vs 52.8) accuracy; no compiler/flags anywhere, so not A.
- **Verifier notes:** All quoted shifted-geometric-mean numbers (18.2, 282.6, 20.4, 3.5, 260.6, 19.3, 14.2, 4.5, 114.2, 108.5, 17.1) appear in the proxqp_benchmark README. Metadata confirmed: BSD-2-Clause, 594 stars, not archived, last commit 2026-09-14. roboticsproceedings.org is egress-blocked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Simple-Robotics/proxqp_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/README.md>
  - <https://github.com/Simple-Robotics/proxsuite>
  - <https://github.com/Simple-Robotics/proxsuite/commits>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros.md>
- **Sources the enricher read:**
  - <https://github.com/Simple-Robotics/proxsuite>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/README.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/doc/1-Overview.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/doc/2-ProxQP_api.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/doc/3-ProxQP_solve.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/doc/5-installation.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/package.xml>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxsuite/HEAD/include/proxsuite/proxqp/dense/solver.hpp>
  - <https://github.com/Simple-Robotics/proxsuite/tree/devel/doc>
  - <https://github.com/Simple-Robotics/proxsuite/issues>
  - <https://github.com/Simple-Robotics/proxsuite/issues/227>
  - <https://github.com/Simple-Robotics/proxsuite/issues/200>
  - <https://raw.githubusercontent.com/Simple-Robotics/proxqp_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/simple-robotics/proxsuite`) · [data/wave8/enrich/raw/github_com_simple_robotics_proxsuite.json](../../../data/wave8/enrich/raw/github_com_simple_robotics_proxsuite.json) (enrichment confidence 0.8)

</details>
