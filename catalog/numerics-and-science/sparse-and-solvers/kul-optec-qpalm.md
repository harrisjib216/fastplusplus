# QPALM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `LGPL-3.0` · 🟢 active

> Sparse C solver for convex and nonconvex quadratic programs; lower runtime geometric mean than OSQP on Maros-Meszaros, but less reliable.

| | |
|---|---|
| **Beats** | OSQP |
| **Claimed result** | Independent qpbenchmark v2.3.0 (2024-09-07), Maros-Meszaros (138 problems), runtime shifted geometric mean (best solver = 1.0, which is PIQP): QPALM 3.6 vs OSQP 12.7 (default), 4.8 vs 16.1 (high accuracy), 3.4 vs 52.8 (low), 2.2 vs 51.9 (mid). Sparse subset (76 problems): QPALM 3.2 vs OSQP 9.5, 4.3 vs 17.4, 3.1 vs 30.0, 1.8 vs 56.0. Success rates on the full set: QPALM 55.8 / 25.4 / 31.2 / 31.2% vs OSQP 43.5 / 26.1 / 21.0 / 24.6%; on the sparse subset QPALM 53 / 8 / 11 / 13% vs OSQP 37 / 13 / 7 / 11%. QPALM's 'solved' return codes were correct on only 57 / 63 / 34 / 37% of problems (full set). |
| **Workload** | Convex QP solve time on the Maros-Meszaros test set (138 problems; 76-problem sparse subset), shifted geometric mean of runtime over four accuracy settings, run through the qpsolvers Python wrappers. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-6500U @ 2.50GHz (4 logical CPUs), run by a third party (qpsolvers maintainer) |
| **Adoption** | 32 stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/kul-optec/QPALM) · [benchmark](https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md) |

## Verdict

In the third-party qpbenchmark v2.3.0 run (2024-09-07, prebuilt Python wheels qpalm 1.2.3 and osqp 0.6.7.post0 via qpsolvers, Intel Core i7-6500U, no compiler flags applicable), QPALM's shifted geometric-mean runtime on the 138 Maros-Meszaros problems was 3.6/4.8/3.4/2.2 versus OSQP's 12.7/16.1/52.8/51.9 at default/high/low/mid accuracy, with PIQP = 1.0. Its success rates were 55.8/25.4/31.2/31.2%, and failures reported as 'solved' are timed at face value rather than at the 1000 s limit.

## Use it when

- Sparse convex QPs at default or moderate tolerances (around 1e-6 to 1e-3) where OSQP needs too many ADMM iterations; in qpbenchmark its runtime geometric mean is 3.6 vs OSQP 12.7 at default settings and 2.2 vs 51.9 at mid accuracy.
- Nonconvex QPs where a stationary point is acceptable (for example subproblems inside SQP or nonlinear MPC); the README states this scope and the code has a dedicated path (LOBPCG minimum-eigenvalue estimate, compiled in by default with QPALM_NONCONVEX).
- Sequences of related QPs (MPC, branch and bound) where warm starts, bound and vector updates and the optional dual-objective termination limit can be used.
- Projects that need the same solver from C, C++, Python, Julia, Matlab and Fortran, with prebuilt binaries for Linux, Windows and macOS on x86-64 and ARM64.

## Skip it when

- When a correct 'solved' status matters: in qpbenchmark v2.3.0 its solved return codes matched the tolerance check on only 57/63/34/37% of Maros-Meszaros problems (default/high/low/mid), against 96-100% for ProxQP and PIQP.
- High-accuracy solves (1e-9): success rate 25.4% vs OSQP 26.1% on the full set and 8% vs 13% on the sparse subset, and its duality-gap geometric mean (1237362.9) is the worst in the table.
- When the fastest robust convex QP solver is the goal: PIQP is 2-5x faster than QPALM in the same table and solves 73-97% of problems.
- Closed-source static linking without LGPL obligations: the core, LADEL and LOBPCG are LGPL-3.0.
- Dense small QPs: the solver is built around sparse LDL factorization; no dense path is documented in the files read.

## How it is fast

It is a proximal augmented Lagrangian method whose inner subproblems are solved with a semismooth Newton method and an exact line search (sorting breakpoints of a piecewise quadratic), so each outer iteration takes few, accurate steps instead of the many cheap ADMM steps OSQP takes. The Newton systems are solved with the bundled LADEL sparse LDL factorization (AMD ordering), choosing between the KKT system and a Schur complement, and updated by low-rank row updates and downdates when constraints enter or leave the active set instead of refactorizing. For nonconvex Q it estimates the minimum eigenvalue with LOBPCG and a Gershgorin bound to set the proximal term.

## Compared with alternatives

Pick QPALM over PIQP and ProxQP (ProxSuite) only when the QP may be nonconvex or you need its Fortran, Julia or Matlab bindings; for convex QPs PIQP is faster and far more reliable in the same independent benchmark, and ProxQP has much better solved-status correctness. Against the OSQP baseline QPALM wins on runtime at all four settings but is not more accurate at high tolerance.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake 3.23+), plus PyPI wheel, Julia package and Matlab zip |
| **Dependencies** | LADEL (bundled, LGPL-3.0, includes AMD ordering); bundled LOBPCG and LAPACK pieces; Eigen3 only for the C++ interface |
| **Minimum toolchain** | C11 compiler with stdatomic.h (MSVC needs /experimental:c11atomics); C++17 for the C++ interface; CMake 3.23 |
| **Platforms** | Portable C; binaries for Linux, Windows and macOS on x86-64 and ARM64, wheels also for ARMv6/ARMv7 |
| **Thread safety** | Not documented. Each solver keeps its state in its own QPALMWorkspace, and the cancel flag is an atomic_bool meant to be set from another thread or a signal handler; the custom calloc/malloc/realloc/free and printf hooks are process-global setters. |
| **Drop-in for the baseline** | partial — same problem form as OSQP (l &lt;= Ax &lt;= u, upper-triangular Q) and bindings through the qpsolvers Python package, but a different API, settings and status codes |

## Gotchas

- The default eps_abs and eps_rel are 1e-4 and verbose output is on by default; set tolerances explicitly before comparing against another solver.
- Check residuals yourself rather than trusting QPALM_SOLVED: the independent benchmark found many 'solved' answers that fail the stated tolerance, and qpbenchmark charges no time-limit penalty for them, which flatters the runtime figure.
- Version 1.3.0 (2026-08-26) fixed scaling of the initial dual guess, residual recomputation on time or iteration limits, the dual objective and the Fortran interface's unscaled solution; the qpbenchmark numbers are from 1.2.3, before these fixes. Issue #9 (solution variables returned scaled on HS21) is closed, while issue #7 (dual cost computation fails when the Hessian is rank deficient) is still open.
- The C++ Solver returns a solution view that is only valid while the Solver object is alive and unchanged; copy x and y into vec_t to keep them.

## Known shortcomings

- Its 'solved' return codes are correct on only 34-63% of problems, and success is 25-31% at non-default tolerances (8-13% on the sparse subset); qpbenchmark charges the 1000 s limit only when no solution returns, so wrong fast answers count at their real runtime; QP solver vs OSQP (off the baseline list); fork of Benny44/QPALM_vLADEL.
- qpbenchmark timed QPALM 1.2.3; 1.3.0 (2026-08-26) later fixed scaling of the initial dual guess, the dual objective, and the Fortran interface returning a scaled solution (#9). These fixes concern warm starts, dual-objective reporting and Fortran, not the cold-start path qpbenchmark times, so the tier stays B. Open #7: computing the dual cost fails when the Hessian is rank deficient, so the 'solved' status is unreliable there.

## Caveats and trade-offs

The runtime advantage is weakly supported outside default settings: qpbenchmark charges the 1000 s time limit only when a solver returns no solution (qpbenchmark/results.py not_found_value), so QPALM's frequent 'solved' answers that fail the tolerance check (return codes correct on only 34-37% of problems at low/mid accuracy) are timed at face value, and its success rate at high/low/mid accuracy is only 25-31% (8-13% on the sparse subset, below OSQP at high accuracy). Its duality-gap shifted geometric mean is very poor (1237362.9 at high accuracy). Category fit is loose: QP optimization solver, not a linear-system solver; OSQP is not in the SuiteSparse/Eigen/PETSc list. Prebuilt Python wheels (qpalm 1.2.3, osqp 0.6.7.post0), so no compiler or flags; the suite's known limitations include CPU thermal throttling. QPALM is itself about 2-5x slower than PIQP in the same table. The QPALM repo has no numbers of its own; it points to two arXiv papers that were not opened. LGPL-3.0 core; bundled LADEL and LOBPCG are LGPL-3.0 and LAPACK is BSD-3.

Proximal augmented-Lagrangian QP solver that also handles nonconvex QPs; C core with C++, Python, Julia, Matlab and Fortran interfaces; LGPL copyleft.

## Maintenance

Actively maintained by KU Leuven's optimization group (version 1.3.0 released 2026-08-26 with scaling and dual-objective fixes; the original Benny44/QPALM_vLADEL repo is unmaintained); LGPL-3.0 with prebuilt C/C++/Fortran libraries and PyPI wheels, so linking it is easy but vendoring into a closed binary carries LGPL obligations.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (qpsolvers/qpbenchmark v2.3.0 on a stated i7-6500U, public harness, solver versions listed) shows QPALM's runtime shifted geometric mean below OSQP's at all four settings; prebuilt Python wheels mean no compiler or flags, so B rather than A. The README also points to its arXiv papers (1911.02934, 2010.02653) for benchmarks; those were not opened (arxiv.org blocked).
- **Verifier notes:** Numbers in the record match both qpbenchmark pages, but the record omitted that QPALM's success rate and return-code correctness are poor at non-default tolerances; shortcoming worth recording: QPALM often reports 'solved' for solutions that fail the tolerance check. Repo page shows it is forked from Benny44/QPALM_vLADEL (the kul-optec repo is the maintained one); LGPL-3.0, 32 stars, 5 forks, latest commit 2026-08-26 ('Version 1.3.0').
- **Fields the verifier corrected:** `is_fork_of`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros_sparse.md>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/main/qpbenchmark/results.py>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/README.md>
  - <https://github.com/kul-optec/QPALM>
  - <https://github.com/kul-optec/QPALM/commits>
- **Sources the enricher read:**
  - <https://github.com/kul-optec/QPALM>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/README.md>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/CMakeLists.txt>
  - <https://github.com/kul-optec/QPALM/tree/main/QPALM>
  - <https://github.com/kul-optec/QPALM/tree/main/QPALM/include/qpalm>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/solver_interface.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/constants.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/types.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/global_opts.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/src/global_opts.c>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/linesearch.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/nonconvex.h>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/include/qpalm/newton.h>
  - <https://github.com/kul-optec/QPALM/tree/main/QPALM/interfaces>
  - <https://github.com/kul-optec/QPALM/tree/main/QPALM/interfaces/cxx/include/qpalm>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/interfaces/cxx/include/qpalm.hpp>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/interfaces/cxx/include/qpalm/sparse.hpp>
  - <https://raw.githubusercontent.com/kul-optec/QPALM/HEAD/QPALM/interfaces/cxx/CMakeLists.txt>
  - <https://github.com/kul-optec/QPALM/issues?q=is%3Aissue>
  - <https://github.com/kul-optec/QPALM/issues/7>
  - <https://github.com/kul-optec/QPALM/issues/9>
  - <https://github.com/kul-optec/QPALM/commits/main>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/main/results/maros_meszaros.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kul-optec/qpalm`) · [data/wave8/enrich/raw/github_com_kul_optec_qpalm.json](../../../data/wave8/enrich/raw/github_com_kul_optec_qpalm.json) (enrichment confidence 0.8)

</details>
