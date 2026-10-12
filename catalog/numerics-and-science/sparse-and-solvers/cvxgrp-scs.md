# SCS (Splitting Conic Solver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> First-order (ADMM) conic solver in C; on large LPs at 1e-4 accuracy it beats Clarabel, HiGHS and PDLP in its author's campaign.

| | |
|---|---|
| **Beats** | Clarabel 0.11.1 (interior point); the same page also times HiGHS 1.15.1, PIQP 0.6.4, OR-Tools PDLP 9.15, OSQP 1.1.3, ProxQP 0.7.3 and NVIDIA cuOpt 26.8.0 (PIQP and ProxSuite are already listed in wave 8). SuiteSparse (the guessed baseline) is not a baseline here: SCS vendors AMD from SuiteSparse (BSD-3-Clause) and QDLDL from the OSQP project (Apache-2.0) in linsys/external. |
| **Claimed result** | Mittelmann LP set, shifted geometric mean time (verified solves of 37): SCS GPU cuDSS 208 s (28), SCS CPU MKL Pardiso 431 s (24), PDLP 733 s (19), Clarabel 817 s (20), PIQP 1352 s (12), cuOpt 2086 s (7), HiGHS 2889 s (9); about 3.9x faster than Clarabel on GPU and 1.9x on CPU (derived from page data), but SCS CPU used MKL Pardiso with 4 threads while Clarabel, PIQP, OSQP, HiGHS and PDLP ran single-threaded at their defaults, and the GPU row is an A100 against 4-core CPU runs. Largest QP quartile at 1e-4: SCS GPU 9.4 s (38 solved), SCS CPU 12.8 s (38), Clarabel 12.6 s (37), PIQP 18.3 s (34), OSQP 29.4 s (32), so SCS CPU is level with Clarabel there, not faster. Page text: 'SCS with cuDSS solves more instances than any other solver, in less than half the geometric mean time of the runner-up.' |
| **Workload** | Wall-clock solve time to a verified 1e-4 accuracy on the 37 large LPs of Mittelmann's LP test set (100,000 to 126 million nonzeros, 1800 s limit, 4-core Modal container, or A100 80GB for the cuDSS backend), plus the largest quartile (40) of 157 Maros-Meszaros/QPLIB QPs; every returned solution re-checked against the problem data. |
| **Metric** | latency |
| **Hardware** | CPU runs: Modal containers reserving 4 physical cores (the container sees 20; OMP_NUM_THREADS=4 pinned) on AMD EPYC Zen 3 'Milan' hosts (CPU family 25 model 1, exact model string masked by gVisor; AVX2/FMA, no AVX-512, observed 1.8-3.1 GHz), 16 GB memory (64 GB for the Mittelmann, SDP and large shards); GPU runs: NVIDIA A100-80GB with 8 reserved host cores and 64 GB. Source: bodono/solver_benchmarks_results scs33_2026-09/MANIFEST.md (the SCS page itself says only '4-core Linux x86-64 containers (Modal)'). |
| **Compiler and flags** | Not stated; every solver was the prebuilt PyPI wheel of its latest September 2026 release (SCS 3.3.1 wheel with MKL Pardiso; cuDSS backend on GPU). |
| **Adoption** | 638 stars; default CVXPY solver for SDP, exponential-cone and power-cone problems; PyPI and conda-forge packages |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/cvxgrp/scs) · [benchmark](https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/benchmarks/index.rst) |

## Verdict

In the author's own campaign on the 37 Mittelmann LPs at 1e-4 (1800 s limit, failures charged 5400 s), the shifted geometric mean was 208 s with 28 verified solves for SCS with cuDSS on an A100, and 431 s with 24 solves for SCS CPU (PyPI wheel, MKL Pardiso backend, 4-core AMD EPYC Milan Modal container). Clarabel 0.11.1 took 817 s (20 solves), OR-Tools PDLP 733 s and HiGHS 2889 s, all run from prebuilt wheels with no compiler flags stated and every solution re-checked against the data. On the largest QP quartile SCS CPU is level with Clarabel (12.8 s against 12.6 s), and the author's own QTQP, which the page omits, beat SCS GPU (192 s against 208 s).

## Use it when

- Very large sparse LPs or QPs (millions of nonzeros) where 1e-4 relative accuracy is enough and interior-point or simplex codes run out of time or memory: on the Mittelmann set it verified 28 of 37 on an A100 and 24 on CPU, against 20 for Clarabel.
- Problems with exponential, power, spectral or large semidefinite cones that interior-point solvers cannot fit in memory (Clarabel was killed at 64 GB on equalG11, maxG55, maxG60 and others, which SCS attempted).
- Sequences of related solves: scs_update changes b and c and warm-starts while keeping the factorization.
- GPU acceleration of a direct-factorization first-order method through the cuDSS backend (needs a source build).
- When you need infeasibility or unboundedness certificates checked against the data: SCS returns Farkas rays and certified 24 of 29 infeasible Netlib LPs at 1e-4.

## Skip it when

- Small and medium QPs or LPs, or anything that needs 1e-6 or tighter: over all 157 QPs Clarabel (3.1 s) and PIQP (3.7 s) beat SCS CPU (7.5 s) in shifted geometric mean, and HiGHS beats it on all 349 LPs (5.0 s against 11.9 s).
- Small or medium SDPs: SCS was last in geometric mean on the 94 SDPs (107.5 s against 38.2 s for SDPA), and on badly conditioned control, truss and gpp instances it ran hundreds of thousands of iterations; the GPU does not help there because the eigendecompositions dominate.
- Badly scaled problems where a reported 'solved' must be trusted: QGROW7, QGROW22 and neos-4413714-turia returned false certificates when the diagonal rescaling hit its floor.
- Platforms without the MKL wheel (aarch64, macOS, Windows, musllinux) fall back to single-threaded QDLDL, so the published CPU numbers do not carry over directly.
- Exact or vertex solutions (basis, sensitivity data): use a simplex code such as HiGHS.

## How it is fast

Douglas-Rachford splitting (ADMM) on a homogeneous self-dual embedding (O'Donoghue et al., JOTA 2016; SIAM J. Optim. 2021), so each iteration is one linear solve with a fixed quasi-definite KKT matrix plus a cone projection. The matrix is factored once (AMD + QDLDL by default, or MKL Pardiso, cuDSS on GPU, Apple Accelerate, or matrix-free CG with eigCG deflation) and reused until the adaptive scaling changes it. Type-I Anderson acceleration (Zhang, O'Donoghue, Boyd, SIAM J. Optim. 2020) and adaptive per-row diagonal rescaling cut the iteration count. Iterations are cheap at moderate accuracy, so very large LPs reach 1e-4 sooner than with interior-point codes, which pay for a fresh factorization at every iteration.

## Compared with alternatives

Pick SCS over PIQP, ProxQP or QPALM when the problem is a very large LP/QP at moderate (1e-4) accuracy, needs non-QP cones (SDP, exponential, power), or should run on a GPU through cuDSS. Prefer PIQP (or Clarabel) for small and medium QPs and for 1e-6 or tighter, where the interior-point codes were faster in this same campaign.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Make or CMake), plus PyPI and conda-forge Python packages and other language bindings |
| **Dependencies** | none for LP/QP/SOCP and exponential/power cones (AMD from SuiteSparse and QDLDL are vendored in linsys/external); BLAS/LAPACK for SDP and spectral cones (USE_LAPACK=1 by default); optional Intel MKL, NVIDIA CUDA + cuDSS, Apple Accelerate; Python wheel needs numpy and scipy |
| **Minimum toolchain** | C99 (CMAKE_C_STANDARD 99), CMake 3.22+ or GNU make; Python 3.9+ for the wheel |
| **Platforms** | Linux, macOS, Windows on x86-64 and aarch64; the MKL Pardiso backend ships only in x86-64 manylinux wheels; cuDSS and GPU-indirect need an NVIDIA GPU and a source build |
| **Thread safety** | Not documented as such; each solve owns its ScsWork workspace, and the process-wide Ctrl-C handler is reference-counted under a mutex. USE_OPENMP=1 parallelizes matrix multiplies (off by default). |
| **Drop-in for the baseline** | partial — in CVXPY or JuMP switching from Clarabel is a one-argument solver change, but the native C API, tolerance semantics (eps_abs/eps_rel, default 1e-4) and accuracy differ |

## Gotchas

- Harness finding: the record's caveat says SCS CPU ran 4-thread MKL Pardiso against single-threaded rivals. But the scs-python 3.3.1 README and meson.build say the x86-64 manylinux wheel statically links sequential MKL (libmkl_sequential.a, 'single-threaded'), so OMP_NUM_THREADS=4 does not parallelize Pardiso. The CPU linear solves were therefore most likely single-threaded too, which makes that comparison fairer than the record states. Only BLAS calls such as the SDP eigendecompositions could use more threads.
- Harness finding: the GPU row is not the PyPI 3.3.1 release the page names. tools/bench_modal.py builds it with 'git clone --recursive --depth 1' of scs-python HEAD (unpinned, -Dlink_cudss=true -Dint32=true) against an unpinned apt cuDSS on a CUDA 12.6 image, so the exact SCS code version behind 208 s is not recorded in the harness.
- The defaults are eps_abs = eps_rel = 1e-4 and max_iters = 100000. Tighten both for accurate answers and raise max_iters for long runs; a 'solved' status on a badly scaled problem can still fail an independent residual check.
- linear_solver=AUTO picks MKL Pardiso only in the x86-64 Linux wheel (QDLDL elsewhere, and QDLDL even on macOS where Accelerate is available). cuDSS needs 32-bit indices (-Dint32=true), and spectral cones need USE_SPECTRAL_CONES=1.

## Known shortcomings

- First-party benchmark campaign run by the SCS author (docs benchmarks page, raw tables in bodono/solver_benchmarks_results): CPU SKU masked (EPYC Milan only), prebuilt wheels, no compiler flags; SCS CPU ran 4-thread MKL Pardiso against single-threaded Clarabel, PIQP, OSQP, HiGHS and PDLP, and the GPU rows pit an A100 against 4-core CPU runs; the author's own QTQP (Mittelmann 192 s vs SCS GPU 208 s) is left off the page. SCS CPU is level with Clarabel on the largest QPs, behind HiGHS, Clarabel and PIQP on the full LP and QP sets, and last on SDPs. QDLDL comes from the OSQP project, not SuiteSparse.
- Enricher: the GPU row comes from an unpinned git clone --depth 1 scs-python HEAD build (tools/bench_modal.py), not PyPI 3.3.1 as the page claims; and scs-python 3.3.1's README and meson.build link libmkl_sequential.a, so the record's '4-thread MKL Pardiso' is wrong and OMP_NUM_THREADS=4 likely did nothing for Pardiso.

## Caveats and trade-offs

First-party benchmark of SCS 3.3.1 by the SCS author on his own harness (bodono/solver_benchmarks branch scs33-campaign commit 24ac4ca, with harness fixes made during the campaign), run 2026-09-13 to 2026-09-18, results in bodono/solver_benchmarks_results campaign scs33_2026-09 (0 stars, no license file), published via cvxgrp/scs PRs #476 and #482; the full raw archive is said to be a release asset but the results repo's Releases section shows none. CPU model only at family level (EPYC Milan, SKU masked) and no compiler flags (prebuilt PyPI wheels), so tier C and not A. Thread counts differ: SCS CPU used MKL Pardiso with OMP_NUM_THREADS=4 while Clarabel, PIQP, OSQP, HiGHS and PDLP ran single-threaded at defaults (stated only in the results MANIFEST, not on the SCS page), and the GPU rows compare an A100 against 4-core CPU runs. The same campaign ran the author's other solver QTQP (and qpo3), which the SCS page omits: on the Mittelmann set QTQP GPU cuDSS has 192 s geometric mean with 27 verified solves against SCS GPU 208 s with 28, and QTQP also beats SCS on all QPs and the largest LP quartile (tables/records_geomean_summary_1e-4.csv), so 'less than half the geometric mean time of the runner-up' holds only among the solvers shown. SCS is not fastest overall: on all 349 LPs HiGHS has shifted geometric mean 5.0 s against 11.9 s for SCS CPU; on all 157 QPs Clarabel is 3.1 s and PIQP 3.7 s against 7.5 s for SCS CPU; on SDPs SCS is last in geometric mean (107.5 s against SDPA 38.2 s) though it solves the most (77 of 94). Each solver is shown from the run whose achieved accuracy is nearest the 1e-4 target (SCS at 1e-4, interior-point codes at 1e-6, or 1e-8 for Clarabel on SDP); the Mittelmann set ran with 1800 s limits on 4 cores, so simplex and interior-point codes time out far more than in Mittelmann's own multi-hour runs ('not a re-run of his benchmark'); failures are charged 3x the time limit (5400 s on the Mittelmann set) in the geometric mean. SCS returned false certificates on QGROW7, QGROW22 and neos-4413714-turia (counted as failures). cuOpt's PDLP mostly fails the independent residual check (7 of 37 pass). Vendored AMD (BSD-3-Clause, SuiteSparse) and QDLDL (Apache-2.0, OSQP project) are OSI-licensed, so the whole tree is copyable. [retier] First-party campaign by the SCS author; CPU SKU masked (EPYC Milan); prebuilt wheels, no flags; GPU rows pit an A100 against 4-core CPU runs; GPU build unpinned (git clone --depth 1); SCS CPU single-threaded (libmkl_sequential); QTQP omitted (192 s vs SCS GPU 208 s); SCS level with Clarabel on the largest QPs, behind HiGHS, Clarabel and PIQP on full LP/QP sets, last on SDPs.

First-order operator-splitting (ADMM with Anderson acceleration): moderate accuracy (1e-4 default) is cheap, tight tolerances are not. Interior-point codes are faster on small problems and at 1e-6, and are the better default for SDPs. The GPU result needs the NVIDIA cuDSS backend; spectral cones need a build flag.

## Maintenance

Actively maintained (3.3.1 on PyPI 2026-09-05, commits into October 2026) and MIT-licensed with OSI-licensed vendored AMD and QDLDL, so it can be vendored. The evidence stays first-party (tier C), and the GPU row ran an unpinned source build rather than the named release; the record's 4-thread caveat looks wrong because the wheel's MKL is sequential.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party campaign by the SCS author (harness bodono/solver_benchmarks, raw per-problem results and tables in bodono/solver_benchmarks_results/scs33_2026-09) whose numbers match docs/src/benchmarks/index.rst exactly; hardware is given only as AMD EPYC Zen 3 'Milan' hosts with the exact CPU model string masked, and all solvers are prebuilt PyPI wheels with no compiler or flags stated, so not A, and no independent or peer-reviewed run, so not B.
- **Verifier notes:** Every number in the record matches the SCS benchmarks page and the raw tables in bodono/solver_benchmarks_results; metadata (MIT, 638 stars, last commit 2026-10-06 on master, SCS 3.3.1 on PyPI 2026-09-05) checks out. Shortcomings to record: first-party campaign by the SCS author, 4-thread MKL Pardiso SCS against single-threaded Clarabel/PIQP/OSQP/HiGHS/PDLP and A100 GPU against 4-core CPU, the author's own QTQP (faster than SCS GPU on the Mittelmann set, 192 s vs 208 s) omitted from the page, SCS CPU level with Clarabel on the largest QPs and behind HiGHS/Clarabel/PIQP on the full LP and QP sets and last on SDPs, no compiler flags and CPU SKU masked.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-179 (wave 8); enricher w8 pair-028
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/benchmarks/index.rst>
  - <https://github.com/cvxgrp/scs>
  - <https://github.com/cvxgrp/scs/commits>
  - <https://github.com/cvxgrp/scs/tree/master/linsys/external>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/linsys/external/qdldl/qdldl.c>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/linsys/external/qdldl/LICENSE>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/linsys/external/amd/LICENSE.txt>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/linsys/external/amd/amd.h>
  - <https://pypi.org/pypi/scs/json>
  - <https://github.com/bodono/solver_benchmarks>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/HEAD/README.md>
  - <https://github.com/bodono/solver_benchmarks_results>
  - <https://github.com/bodono/solver_benchmarks_results/tree/main/scs33_2026-09>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/MANIFEST.md>
  - <https://github.com/bodono/solver_benchmarks_results/tree/main/scs33_2026-09/per_problem>
  - <https://github.com/bodono/solver_benchmarks_results/tree/main/scs33_2026-09/tables>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/tables/records_geomean_summary_1e-4.csv>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/tables/geomean_summary_lpbig.csv>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/tables/all_geomean_summary_1e-4.csv>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/per_problem/mittelmann.csv>
  - <https://pypi.org/pypi/qtqp/json>
- **Sources the enricher read:**
  - <https://github.com/cvxgrp/scs>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/README.md>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/benchmarks/index.rst>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/algorithm/index.rst>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/linear_solver/index.rst>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/citing/index.rst>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/docs/src/algorithm/relaxation.rst>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/include/scs.h>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/include/glbopts.h>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/src/ctrlc.c>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/Makefile>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/scs.mk>
  - <https://raw.githubusercontent.com/cvxgrp/scs/HEAD/LICENSE.txt>
  - <https://github.com/cvxgrp/scs/issues>
  - <https://github.com/cvxgrp/scs/issues/312>
  - <https://github.com/cvxgrp/scs/pull/482>
  - <https://pypi.org/pypi/scs/json>
  - <https://raw.githubusercontent.com/bodono/scs-python/HEAD/README.md>
  - <https://raw.githubusercontent.com/bodono/scs-python/3.3.1/README.md>
  - <https://raw.githubusercontent.com/bodono/scs-python/3.3.1/meson.build>
  - <https://github.com/bodono/solver_benchmarks>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/HEAD/README.md>
  - <https://github.com/bodono/solver_benchmarks/tree/master/solver_benchmarks/solvers>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/scs_adapter.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/clarabel_adapter.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/piqp_adapter.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/highs_adapter.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/pdlp_adapter.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/solver_benchmarks/solvers/base.py>
  - <https://github.com/bodono/solver_benchmarks/tree/master/tools>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks/master/tools/bench_modal.py>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/MANIFEST.md>
  - <https://github.com/bodono/solver_benchmarks_results/tree/main/scs33_2026-09/configs>
  - <https://github.com/bodono/solver_benchmarks_results/tree/main/scs33_2026-09/configs/scs33big>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/campaign.json>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_scs_cpu_1e-4.yaml>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_scs_cudss_1e-4.yaml>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_clarabel_1e-4.yaml>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_highs_1e-4.yaml>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_piqp_1e-4.yaml>
  - <https://raw.githubusercontent.com/bodono/solver_benchmarks_results/HEAD/scs33_2026-09/configs/scs33big/lpbig_mittelmann0_pdlp_1e-4.yaml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cvxgrp/scs`) · [data/wave8/enrich/raw/github_com_cvxgrp_scs.json](../../../data/wave8/enrich/raw/github_com_cvxgrp_scs.json) (enrichment confidence 0.8)

</details>
