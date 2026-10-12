# Clarabel.rs (Rust interior-point conic and QP solver) vs ECOS in qpbenchmark Maros-Meszaros

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust interior-point solver for LP, QP, SOCP, SDP and exponential/power-cone problems; roughly ties ECOS on speed, solves far more QPs.

| | |
|---|---|
| **Beats** | ECOS 2.0.14 (C interior-point conic solver, also homogeneous self-dual embedding based) |
| **Claimed result** | Dense-subset (62 problems) runtime scores are shifted geometric means normalised to the best solver (PIQP = 1.0), not seconds: default Clarabel 20793.9 vs ECOS 126497.0 (6.1x lower, derived from page data); high accuracy 20.1 vs 112.3 (5.6x); mid accuracy 116.6 vs 652.7 (5.6x); low accuracy 26095.2 vs 171259.8 (6.6x). Success rate at default 51.6% vs 12.9% (high accuracy 43.5% vs 0.0%). These gaps measure failures charged at the 1000 s limit, not solve speed: in results/qpbenchmark_results.csv every ECOS dense run ends within 0.03 s and every Clarabel dense run within 0.07 s, and on the 9 dense problems both solvers solve at default settings ECOS is faster on geometric mean (ECOS/Clarabel time 0.84, about 1.19x in ECOS's favour; derived from page data). Clarabel wins DUAL1-DUAL4, DUALC1 and DUALC5 by 1.05-1.55x and loses HS118, HS21 and HS53 by 1.6-4.8x; the same commonly-solved comparison gives ECOS/Clarabel ratios of 0.84 (high), 0.88 (mid) and 0.94 (low accuracy). On the full 138-problem set at default Clarabel (163.8) trails PIQP (1.0), QPALM (3.6), OSQP (12.7), SCS (15.1), HiGHS (30.7), ProxQP (53.3) and CVXOPT (94.1); ECOS is not run there. |
| **Workload** | Solve time (shifted geometric mean, shift 10, failed solves scored at the 1000 s limit) over the 62-problem dense subset of the Maros-Meszaros QP test set, four tolerance settings, solvers called from Python through qpsolvers 4.3.3. |
| **Metric** | latency |
| **Hardware** | Intel(R) Core(TM) i7-6500U CPU @ 2.50GHz (4 logical CPUs), benchmark version 2.3.0 run 2024-09-07 by the qpbenchmark author (@stephane-caron); thermal throttling listed as known limitation #88 |
| **Compiler and flags** | Not stated by the benchmark. Solvers are PyPI builds (clarabel 0.9.0, ecos 2.0.14) called from Python 3.12.4 through qpsolvers 4.3.3; ecos-python's setup.py passes no extra_compile_args (setuptools defaults of the Python build), and Clarabel.rs's Cargo.toml does not override the release profile. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README (Clarabel.rs and Clarabel.jl): unlike solvers based on the standard homogeneous self-dual embedding, it handles quadratic objectives without epigraphical reformulation, so it can be significantly faster than other HSDE-based solvers on problems with quadratic objectives. |
| **Adoption** | 617 stars; default QP/conic solver in CVXPY per the paper snippet |
| **Last commit** | 2026-04-13 |
| **Links** | [repository](https://github.com/oxfordcontrol/Clarabel.rs) · [benchmark](https://github.com/qpsolvers/maros_meszaros_qpbenchmark/blob/main/results/maros_meszaros_dense.md) |

## Verdict

qpbenchmark (Maros-Meszaros dense subset, 62 problems, i7-6500U, PyPI builds called from Python through qpsolvers 4.3.3, run 2024-09-07) reports Clarabel 0.9.0 with a 6.1x lower shifted-geometric-mean runtime than ECOS 2.0.14. That gap comes entirely from failures charged at the 1000 s limit: ECOS fails because qpsolvers converts QPs to SOCPs, and Clarabel 0.9.0 fails on most infinite-bound problems because of presolve bug #127. On the 9 problems both solve, ECOS is about 1.19x faster in 2024 and Clarabel 0.5.1 about 1.05x faster in the 2023 run (derived from page data), so the measured speed is roughly a tie.

## Use it when

- Convex QPs where you need an interior-point answer at 1e-8 accuracy without reformulating the objective as an SOCP (the case where ECOS forces a Cholesky-based epigraph).
- Mixed conic models (SOCP plus exponential or power cones) from CVXPY or similar modelling layers, where you want one open-source solver under Apache-2.0 instead of GPL ECOS.
- Rust services or WebAssembly targets that need an embedded optimiser with no C toolchain; the default build pulls only pure-Rust crates.
- Small and medium sparse problems (up to thousands of variables) solved once each; for repeated solves of a fixed-structure problem, use the update API with presolve disabled.

## Skip it when

- Pure QPs where speed is the goal: even in the 2023 qpbenchmark run, before the presolve bug, ProxQP had a 6.6x lower shifted-geometric-mean runtime on the dense subset and PIQP a 4.2x lower one on the full set, and against ECOS on the problems both solve Clarabel is roughly a tie (ECOS/Clarabel time 1.05 in 2023, 0.84 in 2024; derived from page data).
- Low-accuracy, warm-started model-predictive-control loops: an ADMM solver (OSQP) or an active-set QP solver is usually cheaper per solve, and Clarabel takes no warm-start point (qpsolvers drops initvals; warm-start settings are open feature request #198).
- Problems with explicit np.inf bounds on Clarabel 0.8.x or 0.9.x: their presolve panics when equality constraints and infinite-bound rows are mixed (issue #127, fixed in 0.10.0). Updating b with np.inf through solver.update still yields NumericalError in 0.11.1 (issue #218, open).
- Badly scaled data: open issue #217 (0.11.1) reports false PrimalInfeasible and InsufficientProgress results on 8-variable QPs that solve once equilibration is turned off.
- SDPs without a BLAS/LAPACK: the sdp feature needs one of the blas-src backends (OpenBLAS, MKL, Accelerate, netlib).

## How it is fast

It is a primal-dual interior-point method on a homogeneous embedding that keeps the quadratic term P in the KKT system instead of lifting it into a second-order-cone epigraph, as ECOS and other HSDE solvers must. QPs therefore stay QPs, with no extra cone and no Cholesky factor of P. Each iteration is a sparse quasidefinite LDL factorisation (a Rust QDLDL with AMD ordering by default; faer supernodal or Pardiso optional) after Ruiz-style equilibration and a presolve that drops rows whose bound is at or above 1e20.

## Compared with alternatives

No catalogued sibling solves optimisation problems. The nearest are OrdinaryDiffEq.jl (replacing C/Fortran ODE codes) and hpla-rs (Rust sparse linear algebra on faer, which Clarabel can also use as its LDL backend). Pick Clarabel when the job is a convex conic or QP solve and you want a Rust or Python dependency rather than a C one.

## Integration

| | |
|---|---|
| **Form** | crate (also a Python extension module built with maturin and a C API; cdylib) |
| **Dependencies** | amd, cfg-if, itertools, derive_builder, enum_dispatch, lazy_static, num-traits, thiserror (plus serde and serde_json in the default feature set); optional BLAS/LAPACK for SDP, faer for supernodal LDL, Pardiso (MKL or Panua) |
| **Minimum toolchain** | Rust 1.70 (rust-version in Cargo.toml for 0.11.x); Python wheels need Python 3.9+ |
| **Platforms** | any Rust target including wasm; PyPI wheels for Linux x86-64 and aarch64, macOS x86-64 and arm64, Windows x86-64 |
| **Thread safety** | Not documented for solver objects; a max_threads setting controls multithreaded KKT backends (faer, Pardiso), and the Python binding releases the GIL during solve (changelog 0.10.0, PR #122). |
| **Drop-in for the baseline** | partial: CVXPY can switch solver=ECOS to solver=CLARABEL with the same model, but direct ECOS callers must rewrite G/h/A/b plus cone dimensions into Clarabel's single A, b and cone list. |

## Gotchas

- The 2024-09-07 qpbenchmark run used Clarabel 0.9.0, which contains the presolve panic its runner had reported two months earlier (Clarabel.rs #127, filed 2024-07-31, fixed in PR #137, released in 0.10.0 on 2025-02-02). qpsolvers 4.3.3 turns lb/ub = +-inf into inequality rows with h = inf, and qpbenchmark catches the exception as a failed solve. Across all 138 problems in results/qpbenchmark_results.csv, Clarabel solves 32 of 32 problems with all-finite variable bounds and 4 of 70 with both infinite bounds and equality constraints, so most of its 48% dense failure rate is this bug (derived from the repo's .mat files and CSV). In the 2023-08-30 run (qpbenchmark 1.1.0, Clarabel 0.5.1, same i7-6500U) it solved 96.8% of the dense subset and 89.9% of the full set.
- Default verbose is true in the Rust DefaultSettings, so the solver prints its iteration log unless you turn it off.
- Presolve (on by default) disables parametric data updates; an infinite b entry passed through solver.update is not clamped to get_infinity() = 1e20 and produces NaNs (issue #218).
- If P is not upper-triangular the solver silently copies it to its upper triangle (problemdata.rs), so a non-symmetric P is not rejected.

## Known shortcomings

- Not faster than ECOS: the 6x shifted-geometric-mean gap is failures charged at 1000 s (the qpsolvers QP-to-SOCP conversion fails, qpbenchmark #60); no Clarabel or ECOS run exceeds 0.07 s, and on the 9 problems both solve ECOS is faster (geomean 0.84, derived from results/qpbenchmark_results.csv); the record's high/low accuracy figures were swapped.
- The qpbenchmark 2024-09-07 run used Clarabel 0.9.0, which has the presolve panic #127 (filed by the qpbenchmark author 2024-07-31, fixed in 0.10.0 on 2025-02-02); qpsolvers 4.3.3 passes infinite bounds as h=inf rows and qpbenchmark scores the caught exception as a failure, so Clarabel solves 32 of 32 problems with finite bounds but only 4 of 70 with infinite bounds plus equality constraints (derived from the .mat files and CSV). In the 2023 run (Clarabel 0.5.1) it solved 96.8% of the dense set against 51.6% in 2024. Speed against ECOS on problems both solve is about a tie (ECOS/Clarabel 1.05 in 2023, 0.84 in 2024); the failure gap is an artefact on both sides.

## Caveats and trade-offs

Not faster than ECOS on solve time in this suite: the 6x shifted-geometric-mean gap is produced by failures charged at the 1000 s limit, and ECOS fails 53 of 62 dense problems within milliseconds because qpsolvers converts each QP to an SOCP through a NumPy Cholesky factorisation that needs a positive definite P (qpbenchmark issue #60, open, labelled fairness: 'failing to solve the problem is no fault of the solver itself'). On the problems both solve, ECOS is faster on geometric mean (derived from results/qpbenchmark_results.csv). Clarabel's own failures also end in milliseconds (no timeouts), so its 51.6% success rate is low for an interior-point solver; the cause was not investigated. The report also lists CPU thermal throttling (#88) as a known limitation. Python wrapper and qpsolvers conversion overhead are included for every solver. Clarabel trails OSQP (C), SCS (C), HiGHS (C++), PIQP (C++) and others on the full and sparse sets. The broader 'faster than commercial and open-source solvers on QPs' claim is from the Goulart and Chen paper (arXiv 2405.12762, Mathematical Programming Computation per a search snippet; neither arxiv.org nor the Oxford repository copy could be opened), so its numbers are unverified. ClarabelBenchmarks (oxfordcontrol) holds the authors' benchmark code but commits no result tables. [retier] The 2024-09-07 run used Clarabel 0.9.0 with the presolve panic #127 (fixed in 0.10.0, 2025-02-02): qpsolvers 4.3.3 passes infinite bounds as h=inf rows and qpbenchmark scores the caught exception as a failure, so Clarabel solved 32 of 32 finite-bound problems but only 4 of 70 with infinite bounds plus equality constraints; in the 2023 run (0.5.1) it solved 96.8% of the dense set. Speed against ECOS on problems both solve is about a tie (ECOS/Clarabel 1.05 in 2023, 0.84 in 2024).

Rust crate with Python (pip install clarabel) and a separate Julia port (oxfordcontrol/Clarabel.jl); handles quadratic objectives natively; interior-point solves are dense in iterations but high accuracy, whereas ADMM solvers (OSQP, SCS) are cheaper per problem at low accuracy.

## Maintenance

Apache-2.0 and widely used (about 2.17M crates.io downloads), but development has slowed: 0.11.1 (June 2025) is the latest release, only two commits have landed since (September 2025 and April 2026), and 26 issues are open, including RUSTSEC advisories against its pyo3 dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The independent qpbenchmark dense report (public code, i7-6500U, PyPI solver versions, no compiler flags) lists Clarabel and ECOS, but its 6x runtime gap is a success-rate artifact: every failure is charged the 1000 s limit, no Clarabel or ECOS run in results/qpbenchmark_results.csv takes more than 0.07 s, ECOS's failures come from qpsolvers' QP-to-SOCP conversion (open fairness issue #60 listed under the report's Known limitations), and on the 9 dense problems both solve ECOS is faster (derived from page data). With the independent data not supporting a speed win, the remaining speed claim is first-party (README without numbers, paper seen only as a search snippet), so C.
- **Verifier notes:** Keep with shortcoming 'not faster than ECOS on commonly solved problems; 6x figure is a failure-penalty artifact of qpsolvers' QP-to-SOCP conversion (qpbenchmark #60)'. The record had the high- and low-accuracy figures swapped (20.1 vs 112.3 is high accuracy, 26095.2 vs 171259.8 is low accuracy); fixed in claimed_speedup. Per-problem ratios were derived from results/qpbenchmark_results.csv in the same repo. Metadata checked: 617 stars, Apache-2.0, last commit 2026-04-13, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`, `hardware`
- **Shortcomings recorded by:** verifier batch-100 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros_dense.md>
  - <https://github.com/qpsolvers/maros_meszaros_qpbenchmark/tree/main/results>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros_sparse.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/qpbenchmark_results.csv>
  - <https://github.com/qpsolvers/qpbenchmark/issues/60>
  - <https://github.com/qpsolvers/qpbenchmark/issues?q=clarabel>
  - <https://github.com/oxfordcontrol/ClarabelBenchmarks>
  - <https://github.com/oxfordcontrol/ClarabelBenchmarks/tree/main/latex>
  - <https://raw.githubusercontent.com/oxfordcontrol/ClarabelBenchmarks/HEAD/latex/main.tex>
  - <https://github.com/oxfordcontrol/Clarabel.rs>
  - <https://github.com/oxfordcontrol/Clarabel.rs/commits>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/embotech/ecos-python/HEAD/setup.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/src/solver/implementations/default/settings.rs>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/src/solver/implementations/default/solver.rs>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/src/solver/implementations/default/problemdata.rs>
  - <https://raw.githubusercontent.com/oxfordcontrol/Clarabel.rs/HEAD/src/lib.rs>
  - <https://github.com/oxfordcontrol/Clarabel.rs/issues>
  - <https://github.com/oxfordcontrol/Clarabel.rs/issues/127>
  - <https://github.com/oxfordcontrol/Clarabel.rs/issues/217>
  - <https://github.com/oxfordcontrol/Clarabel.rs/issues/218>
  - <https://github.com/oxfordcontrol/Clarabel.rs/commits>
  - <https://crates.io/api/v1/crates/clarabel>
  - <https://pypi.org/pypi/clarabel/json>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros_dense.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/maros_meszaros_dense_posdef.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/results/qpbenchmark_results.csv>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/maros_meszaros.py>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/maros_meszaros_dense.py>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/pixi.toml>
  - https://raw.githubusercontent.com/qpsolvers/maros_meszaros_qpbenchmark/HEAD/data/ (all 138 .mat files, bounds parsed locally)
  - <https://github.com/qpsolvers/maros_meszaros_qpbenchmark>
  - <https://github.com/qpsolvers/maros_meszaros_qpbenchmark/tree/main/results>
  - <https://raw.githubusercontent.com/qpsolvers/qpsolvers/v4.3.3/qpsolvers/solvers/clarabel_.py>
  - <https://raw.githubusercontent.com/qpsolvers/qpsolvers/v4.3.3/qpsolvers/conversions/linear_from_box_inequalities.py>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/v2.3.0/qpbenchmark/run.py>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/v2.3.0/qpbenchmark/utils.py>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/v1.1.0/maros_meszaros/results/maros_meszaros_dense.md>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/v1.1.0/maros_meszaros/results/maros_meszaros.md>
  - <https://raw.githubusercontent.com/qpsolvers/qpbenchmark/v1.1.0/maros_meszaros/results/maros_meszaros_dense.csv>
  - <https://github.com/qpsolvers/qpbenchmark/issues?q=clarabel>
  - <https://pypi.org/pypi/qpbenchmark/2.3.0/json>
  - <https://pypi.org/pypi/qpsolvers_benchmark/1.1.0/json>
  - WebSearch: Clarabel Goulart Chen benchmark ECOS MOSEK Maros-Meszaros (snippet of arXiv 2405.12762; arxiv.org not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/oxfordcontrol/clarabel.rs`) · [data/wave14/enrich/raw/github_com_oxfordcontrol_clarabel_rs.json](../../../data/wave14/enrich/raw/github_com_oxfordcontrol_clarabel_rs.json) (enrichment confidence 0.8)

</details>
