# GLPK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later` · ⚪ unknown

> GNU's plain-C LP/MIP solver with MathProg modelling; ranks ahead of lp_solve but far behind HiGHS and Clp.

| | |
|---|---|
| **Beats** | lp_solve |
| **Claimed result** | HiGHS-team slides (Hall, INFORMS 2019; snippet only, tables said to be drawn from Mittelmann's LP benchmarks), relative time, lower is better. 17 March 2019 table (Clp = 1): HiGHS 5.3, GLPK 26, lp_solve 112, so GLPK about 4.3x faster than lp_solve (derived from page data). 4 June 2019 table (COPT = 1): Clp 1.3, GLPK 24.0, lp_solve 92.2, about 3.8x (derived from page data). 9 October 2019 table (COPT = 1, not Clp): Clp 1.4, QSopt 26, GLPK 28, lp_solve 108, about 3.9x (derived from page data), with GLPK solving 31 instances against lp_solve's 23. ALGLIB benchmark over 90 NETLIB LPs (snippet only): ALGLIB, HiGHS and Clp roughly equal, GLPK roughly 2x behind them, lp_solve roughly 3x behind, so GLPK about 1.5x faster than lp_solve (derived from page data). Sandia report SAND2013-8847 (2013, snippet only): lp_solve considerably slower than GLPK and failed on several test problems; no ratio seen. |
| **Workload** | LP solve time: relative total solution time of GLPK, lp_solve, Clp and HiGHS on the HiGHS group's LP test set (INFORMS 2019 slides), and ALGLIB's benchmark over 90 NETLIB LP problems. |
| **Metric** | other |
| **Adoption** | GNU package, shipped in Debian/Ubuntu, openSUSE, Oracle Linux EPEL and OpenBSD ports (search snippets); the only GitHub copy found, github.com/firedrakeproject/glpk, is a one-commit 4.60 snapshot with 57 stars and 31 forks, archived 2025-06-16, not the official source |
| **Links** | [repository](https://www.gnu.org/software/glpk/) · [benchmark](https://webhomes.maths.ed.ac.uk/hall/INFORMS-HiGHS19/INFORMS-HiGHS19.pdf) |

## Verdict

HiGHS-team slides (Hall, INFORMS 2019), drawn from Mittelmann's simplex benchmark, give GLPK a relative time of 24-28 against lp_solve's 92-112 (about 3.8-4.3x), and ALGLIB's 90-problem NETLIB run puts GLPK about 2x and lp_solve about 3x behind the leaders (about 1.5x). All of this comes from search snippets: no solver versions, settings, compiler or hardware were seen, and the slides note that HiGHS presolve and crash were off while Clp used its Idiot crash.

## Use it when

- You use lp_solve or need a free embeddable LP/MIP solver, and GPL-3.0 linking is acceptable: GLPK beat lp_solve in every third-party table seen (about 3.8-4.3x on Mittelmann-derived 2019 tables, about 1.5x on ALGLIB's NETLIB set).
- Small to medium LPs and easy MIPs where solve time is not the bottleneck and a dependency-free C library is worth more than top speed.
- Models written in GNU MathProg or AMPL-like syntax that you want to solve from the glpsol CLI without a commercial modelling system.
- You need an exact rational-arithmetic simplex (glp_exact, with GMP) to certify an optimal basis.
- Browser or Node use through the Emscripten build (glpk.js) or a vendored source tree (igraph ships GLPK 5.0 in vendor/glpk).

## Skip it when

- LP speed matters: GLPK sits about 5x behind HiGHS and about 20-26x behind Clp on the same 2019 tables, and Mittelmann's current LPopt benchmark (29 Apr 2026: COPT 1.00, HiGHS 13.07, CLP 27.38) no longer includes GLPK at all.
- Hard MIPs or large instances that need multithreading: the solver runs single-threaded and was reported (Sandia 2013, snippet only) unable to match Clp or CPLEX.
- Proprietary or permissively licensed products: GPL-3.0-or-later, so linking makes the combined work GPL.
- Large LPs through the interior-point path: glp_interior is a basic primal-dual method, and in 5.0 the QMD ordering is a stub that aborts.
- You need an actively developed project: 5.0 (Dec 2020) is still the release every packager ships, there is no public repository, and GCC 15 needs a downstream patch.

## How it is fast

Revised primal and dual simplex with projected steepest-edge pricing, Harris' two-pass ratio test and an optional long-step (bound-flipping) dual ratio test (GLP_RT_FLIP), on an LU basis factorization with Forrest-Tomlin or Schur-complement updates (bflib). An LP presolver, a primal-dual interior-point method with AMD ordering, and a branch-and-cut MIP solver with Gomory, MIR, cover and clique cuts plus feasibility-pump and proximity heuristics complete it. The edge over lp_solve comes from these standard techniques; there is no parallelism or SIMD.

## Compared with alternatives

Among catalogued siblings, SCS (first-order conic, no basic solution) and the QP solvers PIQP, QPALM and ProxQP solve continuous problems only; pick GLPK when you need simplex basic solutions, integer variables or MathProg models in a small C library. For pure LP speed, look at HiGHS or Clp, which are not catalogued yet.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools build of the GNU tarball); also a source-drop (igraph vendors src/ with its own CMake) |
| **Dependencies** | none required; optional GMP (exact simplex; Homebrew and conda-forge build --with-gmp), zlib, libltdl/dlfcn, ODBC and MySQL drivers for MathProg tables; bundles copies of SuiteSparse AMD/COLAMD and MiniSat (Debian and msys2 patch these out) |
| **Minimum toolchain** | ANSI C compiler; GCC 15's default C23 mode breaks on minisat.h's 'typedef int bool' unless patched (msys2 0005-fix-build-with-gcc-15.patch, igraph's own fix) |
| **Platforms** | any: POSIX autotools, Windows (w32/w64 MSVC build files, mingw-w64 via msys2), every Julia Yggdrasil target, WebAssembly via Emscripten (glpk.js) |
| **Thread safety** | The global environment pointer (env/tls.c) is thread-local only if the TLS macro is defined at build time; then independent problems can be solved in separate threads, one glp_prob per thread. The 4.60 autotools config.h.in defines no TLS; whether 5.0's configure enables it by default was not checked (configure.ac for 5.0 was unreachable). |
| **Drop-in for the baseline** | partial — not API-compatible with lp_solve (glp_prob/glp_simplex vs lprec); models move between them through files such as MPS, or the model-building code is rewritten |

## Gotchas

- Any detected error, including an invalid control parameter, prints a message and calls abort() (env/error.c); only a glp_error_hook that longjmps out keeps the host process alive.
- Defaults are conservative: glp_init_smcp selects the primal simplex with presolve off and msg_lev GLP_MSG_ALL (terminal output). Switch to GLP_DUALP and enable presolve before comparing speed, and note that the benchmark tables do not say which settings they used.
- GLPK 5.0 replaced the QMD ordering routines (misc/qmd.c) and glp_gridgen with stubs that call xerror ('temporarily disabled due to licensing problems'), so ord_alg = GLP_ORD_QMD aborts; glp_netgen_prob was removed but left in the Windows .def file (conda-forge patch).
- Numbers behind the lp_solve ratio are shifted geometric means in which unsolved instances count at the time limit, and lp_solve solved fewer instances (23 vs GLPK's 31 in October 2019, snippet only), so part of the gap is robustness rather than per-instance speed.

## Known shortcomings

- Every numbers source unreachable (HiGHS slides, alglib.net, plato.asu.edu, coin-or.org, osti.gov, sandia.gov, gnu.org); snippet-only ratios derived from page data: about 4.3x, 3.8x, 3.9x over lp_solve on 2019 HiGHS slide tables from Mittelmann's benchmarks, about 1.5x on ALGLIB's NETLIB set. Reference solver changes between tables; the gap over lp_solve is partly its failures (23 solved vs GLPK's 31). GLPK is about 20x slower than Clp and 5x slower than HiGHS. No public version control; last release 5.0 (2020-12-16). Possible B if plato.asu.edu or SAND2013-8847 becomes reachable.
- Enricher: Mittelmann dropped GLPK from his LP benchmarks (absent since at least the Dec 2022 snapshot in mattmilten/mittelmann-plots; LPopt 29 Apr 2026: COPT 1.00, HiGHS 13.07, CLP 27.38); the lp_solve gap is partly lp_solve's unsolved instances counted at the time limit. Any error calls abort() unless glp_error_hook longjmps; glp_init_smcp defaults to primal simplex with presolve off; 5.0 turned QMD ordering and glp_gridgen into xerror stubs; GCC 15/C23 build breaks on minisat.h 'typedef int bool'; thread-local env only when the TLS macro is defined at build; 5.0 (Dec 2020) is still the only release; GPL-3.0.

## Caveats and trade-offs

SNIPPET ONLY: every numbers page (webhomes.maths.ed.ac.uk slides, alglib.net, plato.asu.edu, coin-or.org GAMSlinks LP benchmarks, osti.gov and sandia.gov for SAND2013-8847) and gnu.org itself fail with ENOTFOUND in this sandbox; table values, test set, hardware and solver versions were taken from WebSearch summaries and were not seen on the pages. The HiGHS slide tables change their reference solver (Clp = 1 in March 2019, COPT = 1 in June and October 2019), and the 'time' column is probably Mittelmann's scaled shifted geometric mean in which unsolved instances count at the time limit, so part of lp_solve's gap reflects its failures (23 solved against GLPK's 31 in October 2019). The same sources rank GLPK far behind the current open-source leaders (about 20x slower than Clp and about 5x slower than HiGHS on the slides; about 2x behind ALGLIB, HiGHS and Clp on ALGLIB's NETLIB set; a 2020 HiGHS table puts GLPK at 54 against Clp's 1), and the Sandia 2013 report found GLPK could not match Clp or CPLEX; neither HiGHS nor Clp is in the catalog yet. The only win is over lp_solve, the slowest solver in those sets. The slides are by HiGHS's authors and ALGLIB's page by a competing commercial vendor, though both are third parties to GLPK and lp_solve. An unverified Medium post claims GLPK beats Clp and HiGHS on a few large LPs (woodw, pilot, pds-20). The GLPK FAQ's claim of beating lp_solve 4.0 'in many cases' has no numbers. GLPK has no public version-control repository; the last release found is 5.0, announced on info-gnu on 2020-12-16 (snippet only), with no later release seen. Category sparse-and-solvers chosen over the lead's guessed blas-lapack because GLPK is an LP/MIP solver.

Simplex (primal and dual), interior point and branch-and-cut MIP in plain C with the GNU MathProg modelling language and glpsol CLI; single-threaded; GPL (not LGPL), so linking forces GPL on the combined work.

## Maintenance

GPL-3.0-or-later; GLPK 5.0 (16 Dec 2020) is still what Homebrew, conda-forge, msys2 and Julia Yggdrasil package in 2026, with no public repository and a GCC 15 build patch needed downstream. The evidence is snippet-only and stale: Mittelmann's LP benchmarks have not included GLPK since at least the December 2022 snapshot in the mittelmann-plots archive.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark_url (webhomes.maths.ed.ac.uk) and every other source (alglib.net, plato.asu.edu, coin-or.org GAMSlinks, osti.gov, sandia.gov, gnu.org) fail with ENOTFOUND here, so the GLPK-vs-lp_solve numbers are known only from WebSearch snippets; per the snippet-only rule the tier stays at C. The underlying data look like Mittelmann's independent LP benchmarks (the slides say so, snippet only), so a retier to B is possible once plato.asu.edu or the slides can be opened.
- **Verifier notes:** Kept at C: GLPK beats lp_solve by about 3.8-4.3x on the Mittelmann-derived HiGHS slide tables and by about 1.5x on ALGLIB's NETLIB set, all from snippets because every source host is blocked. Main shortcomings: snippet-only evidence, slow against Clp (about 20x) and HiGHS (about 5x), no public VCS, last release 5.0 in December 2020 (not corrected to 'abandoned' because the release list could not be opened), and the lp_solve ratio is inflated by lp_solve's failed instances. Leads: HiGHS (ERGO-Code/HiGHS) and COIN-OR Clp are the faster open-source LP solvers and are not catalogued; Mittelmann's plato.asu.edu LP benchmarks and SAND2013-8847 are retier sources if they become reachable.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-176 (wave 8); enricher w8 pair-044
- **Pages the verifier opened:**
  - <https://github.com/firedrakeproject/glpk>
- **Sources the enricher read:**
  - <https://github.com/firedrakeproject/glpk>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/README>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/NEWS>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/config.h.in>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/w64/config_VC>
  - <https://raw.githubusercontent.com/firedrakeproject/glpk/HEAD/src/env/error.c>
  - <https://github.com/igraph/igraph/tree/master/vendor/glpk>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/README>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/glpk.h>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/glpk_tls_config.h>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/env/tls.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/env/env.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/env/env.h>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/simplex/spxprim.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/simplex/spydual.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/CMakeLists.txt>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/draft/glpapi06.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/draft/glpapi08.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/misc/qmd.c>
  - <https://raw.githubusercontent.com/igraph/igraph/master/vendor/glpk/minisat/minisat.h>
  - <https://raw.githubusercontent.com/conda-forge/glpk-feedstock/HEAD/recipe/meta.yaml>
  - <https://raw.githubusercontent.com/Homebrew/homebrew-core/HEAD/Formula/g/glpk.rb>
  - <https://raw.githubusercontent.com/JuliaPackaging/Yggdrasil/HEAD/G/GLPK/build_tarballs.jl>
  - <https://raw.githubusercontent.com/msys2/MINGW-packages/HEAD/mingw-w64-glpk/PKGBUILD>
  - <https://raw.githubusercontent.com/msys2/MINGW-packages/HEAD/mingw-w64-glpk/0005-fix-build-with-gcc-15.patch>
  - <https://raw.githubusercontent.com/msys2/MINGW-packages/HEAD/mingw-w64-glpk/0004-no-embedded-suitesparse.patch>
  - <https://raw.githubusercontent.com/jvail/glpk.js/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jvail/glpk.js/HEAD/.gitmodules>
  - <https://github.com/mattmilten/mittelmann-plots>
  - <https://raw.githubusercontent.com/mattmilten/mittelmann-plots/master/mittelmann_plots.py>
  - <https://raw.githubusercontent.com/mattmilten/mittelmann-plots/master/docs/index.md>
  - <https://raw.githubusercontent.com/mattmilten/mittelmann-plots/master/docs/lpopt-14-Dec-2022.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://gnu.org/software/glpk`) · [data/wave8/enrich/raw/gnu_org_software_glpk.json](../../../data/wave8/enrich/raw/gnu_org_software_glpk.json) (enrichment confidence 0.4)

</details>
