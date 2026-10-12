# Pyccel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (transpiler that emits Fortran or C)` · `MIT` · 🟢 active

> Ahead-of-time transpiler from type-annotated Python to C or Fortran extension modules; 5x-2000x faster than CPython on scalar-loop numeric kernels.

| | |
|---|---|
| **Beats** | CPython 3.12 for the dev-branch table (the workflow installs it with actions/setup-python python-version '3.12'); separate tables for pyccel 2.2.3 from PyPI under CPython 3.10, 3.11, 3.12, 3.13 and 3.14 |
| **Claimed result** | pyccel-benchmarks: the devel-branch table (commit 0ccf9ec, timeit best-of, GitHub Actions ubuntu-latest, Python 3.12) gives the headline; the PyPI 2.2.3 tables (pyperf mean) show the GNU C backend much slower (Euler 21.0 vs 6.94 ms, Midpoint Fixed 180 vs 47.4 ms), a release C geomean of about 210x over CPython 3.12 rather than 336x (derived from page data). The GNU C backend is slower than Pythran on 6 of 12 kernels. The Midpoint Fixed row is loop-invariant (humps_deriv depends only on x) and likely collapsed by the Intel compiler (7.24 ms equals its Euler time). |
| **Workload** | 13 numeric kernels (Ackermann, Bellman-Ford, Dijkstra, Euler, midpoint explicit/fixed, RK4, four finite-difference solvers, molecular dynamics, splines); execution time in ms, compilation excluded. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest hosted runner (.github/workflows/run_benchmarks.yml); CPU model not stated and may differ between runs, while builds use -march=native |
| **Compiler and flags** | -O3 -march=native -mtune=native -mavx -ffast-math added to the pyccel_gnu and pyccel_intel configs (the same flags are added to Pythran); GNU compilers are Ubuntu apt gcc/gfortran and Intel compilers come from the apt intel-oneapi-toolkit, versions not pinned or stated. Dev run used pyccel commit 0ccf9ec3e964e071b933947b75767a052c9692f4, numba 0.66.0, pythran 0.18.1, numpy 2.4.6 (version_specific_results/devel_performance_312_requirements.txt) |
| **Adoption** | 398 stars; on PyPI (2.2.3 per the PyPI JSON API); JOSS 2023 paper (Pyccel: a Python-to-X transpiler for scientific high-performance computing) cited in the README |
| **Last commit** | 2026-08-03 |
| **Links** | [repository](https://github.com/pyccel/pyccel) · [benchmark](https://github.com/pyccel/pyccel-benchmarks) |

## Verdict

Pyccel's own pyccel-benchmarks workflow ran 13 scalar-loop kernels under CPython 3.12 on a GitHub Actions ubuntu-latest runner (CPU unstated) with -O3 -march=native -ffast-math. Times are python3 -m timeit best-of in ms, compilation excluded. The devel GNU C backend was 4.8x (FD Laplace) to 1624x (FD Poisson) faster than CPython, geomean about 336x; the Fortran backend's geomean was about 388x. Pythran (geomean about 264x) and Numba were measured in the same table.

## Use it when

- Pure-Python numeric loops (ODE integrators, stencils, graph shortest paths, recursion) that run 100x-1000x slower in CPython than in compiled code.
- You want the generated C or Fortran to be readable and kept, for example to hand a kernel to an HPC code base or to read what the compiler sees.
- Fortran-heavy scientific groups: in the published tables the Fortran backend is the steadier of the two (geomean about 383x over CPython in both the dev and 2.2.3 tables).
- Shared-memory or MPI parallel kernels written in Python syntax, using `#$ omp` pragmas.

## Skip it when

- Code that already spends its time inside NumPy calls: FD Laplace, written with NumPy slices, gains only 4.8x with the C backend (729 ms vs 151 ms) because CPython was not the bottleneck.
- Dynamic Python (types that change at run time, heterogeneous containers, arbitrary third-party libraries). Lists and tuples are only partly supported, and module-level tuples are not handled.
- You need the fastest accelerator in this class: Pythran beats Pyccel's GNU C backend on 6 of 12 shared kernels (Dijkstra, M-D, the four FD solvers) in Pyccel's own table.
- Windows deployments that use external libraries (support is documented as experimental and limited), or environments without a C or Fortran toolchain at build time.
- Code that relies on Python's arbitrary-precision int: `int` becomes int64_t or integer(i64).

## How it is fast

Pyccel does static type inference over the annotated code and emits plain loops over int64_t and double values and over NumPy-layout arrays (STC cspan in C, allocatable arrays in Fortran). The result has no interpreter dispatch, no boxing and no reference counting, and gcc, gfortran, icx or ifx then optimise it. Non-literal negative indexing gets no runtime check unless you request one, so array accesses compile to direct loads. OpenMP pragmas written as `#$ omp` comments and MPI give parallelism beyond what one core can do.

## Compared with alternatives

Pick Pyccel over Pythran when you want a Fortran backend or readable C/Fortran output with OpenMP/MPI pragmas; Pythran is as fast or faster on NumPy-style stencils and graph kernels in the same harness. Pick it over Cython, Shed Skin or Codon when the code is already numeric Python with type hints and you want no new syntax and no new runtime; pick those for general-purpose Python.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python &gt;=3.10, numpy&gt;=2.1, sympy, textx, meson, ninja and a few small packages (PyPI 2.2.3); a C and/or Fortran compiler (GNU, Intel icx/ifx, LLVM clang/flang, NVIDIA nvc/nvfort); BLAS/LAPACK for linear algebra; optional OpenMP and MPI |
| **Minimum toolchain** | Python 3.10; any supported C99/Fortran compiler family (versions not documented) |
| **Platforms** | Linux and macOS (CI for both, plus Intel and Anaconda jobs); Windows experimental |
| **Thread safety** | not documented; generated modules can use OpenMP threads internally |
| **Drop-in for the baseline** | partial: the compiled .so replaces the .py module with no change for callers, but the source must be annotated and stay within Pyccel's typed subset |

## Gotchas

- The headline table comes from an unreleased devel commit (0ccf9ec), timed as timeit best-of. The released PyPI 2.2.3 tables (pyperf mean) show a much slower GNU C backend: Euler 21.0 ms vs 6.94, Midpoint Explicit 42.2 vs 12.9, Midpoint Fixed 180 vs 47.4, FD L Convection 4.44 vs 2.04, M-D 106 vs 74.5. Its C-backend geomean over CPython 3.12 is about 210x, not 336x (derived from page data).
- Harness flaw: the Midpoint Fixed kernel's derivative (humps_deriv) depends only on x, so its 10 'implicit' iterations per step all compute the same value. In the dev table Intel C runs it in 7.24 ms, exactly its Euler time and 6.5x faster than GNU C, which suggests the compiler collapsed the loop. The harness also never checks outputs across tools, even with -ffast-math and a tolerance-terminated Laplace loop whose iteration count can differ.
- Indexing an array with a negative variable or expression is unchecked unless the function carries @allow_negative_index; the docs warn this 'can cause a crash'.
- Open bug reports include memory leaks (#2435 in classes for C, #2342 with LLVM compilers), wrong numpy.sum translation of np.full arguments (#1815), and `and`/`or` translation problems (#2088).

## Known shortcomings

- pyccel-benchmarks dev-branch table is the team's own run on GitHub Actions ubuntu-latest (Python 3.12) with CPU and compiler versions unstated; the GNU C backend is slower than Pythran on 6 of 12 kernels (the record said 3). Ahead-of-time transpiler, filed with Cython, Codon and Nuitka.
- Enricher: the headline comes from an unreleased devel commit 0ccf9ec (timeit best-of) while the PyPI 2.2.3 tables (pyperf mean) show the GNU C backend much slower (Euler 21.0 vs 6.94 ms, Midpoint Fixed 180 vs 47.4 ms; release C geomean about 210x over CPython 3.12 rather than 336x, derived). In Midpoint Fixed, humps_deriv depends only on x so the 10 implicit iterations are loop-invariant (the Intel C 7.24 ms equals its Euler time, so the loop likely collapsed), and the harness never compares outputs across tools despite -ffast-math and a tolerance-terminated Laplace.

## Caveats and trade-offs

Numbers come from the Pyccel developers' own benchmark repository (pyccel/pyccel-benchmarks, 5 stars), regenerated by a GitHub Actions workflow on an ubuntu-latest shared runner; CPU model and compiler versions are not stated. Execution times are python3 -m timeit best-of results and exclude compilation; the compile-time table is CPU seconds (rusage user plus system) and lists 0.33 to 8.31 s per kernel across all tools. The CPython column is plain interpreted Python on scalar-loop numeric kernels adapted from Burkardt and Barba examples, so the large ratios do not transfer to code that already runs in NumPy. Pyccel is not the fastest accelerator in its own table: the GNU C backend is slower than Pythran (GNU) on 6 of 12 shared kernels (Dijkstra, FD L Convection, FD NL Convection, FD Poisson, FD Laplace, M-D), and the GNU Fortran backend is slower than Pythran on Dijkstra and M-D. Built with -ffast-math. Pyccel is an ahead-of-time Python-to-C/Fortran transpiler (filed next to Cython, Codon and Nuitka), not an interpreter. The JOSS paper was not opened (host blocked), so no peer-reviewed numbers are used. [retier] Team's own repo run on GitHub Actions ubuntu-latest with CPU and compiler versions unstated; the harness never compares outputs across tools despite -ffast-math and a tolerance-terminated Laplace, and the CPython baseline loops over NumPy elements one by one. Ahead-of-time transpiler for a typed Python subset, filed with Cython, Codon and Nuitka.

Restricted, statically typed Python subset; emits readable C or Fortran that is compiled and wrapped as a Python extension; supports NumPy and SciPy calls through generated code.

## Maintenance

Actively developed (devel commits through 2026-08-03, PyPI 2.2.3 from 2026-03-20, 398 stars, JOSS 2023 paper) and MIT-licensed. The headline speedups come from the unreleased devel branch and are first-party, so expect the 2.2.3 release figures (about 210x C, 383x Fortran geomean on these kernels) unless you install from git.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** pyccel/pyccel-benchmarks (benchmarks/run_benchmarks.py, run by .github/workflows/run_benchmarks.yml) publishes the code, the added flags and pinned package versions, but the runs happen on a GitHub Actions ubuntu-latest runner whose CPU model is not stated (and varies), and the gcc/gfortran and Intel oneAPI versions are unpinned, so not A; it is the Pyccel team's own repository, so C.
- **Verifier notes:** Every number in the record matches the dev-branch table; added the four missing kernels, the Fortran-backend ratios and the run details from the workflow (Python 3.12 confirmed, not just inferred; ubuntu-latest runner). Corrected the caveat that Pyccel trails Pythran on only three kernels: the C backend trails it on six. MIT, 398 stars, 63 forks, last devel commit 2026-08-03, PyPI 2.2.3 (uploaded 2026-03-20) confirmed.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pyccel/pyccel>
  - <https://github.com/pyccel/pyccel/commits>
  - <https://github.com/pyccel/pyccel-benchmarks>
  - <https://github.com/pyccel/pyccel-benchmarks/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/actions/linux_install/action.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312_requirements.txt>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel/HEAD/README.md>
  - <https://pypi.org/pypi/pyccel/json>
- **Sources the enricher read:**
  - <https://github.com/pyccel/pyccel>
  - <https://raw.githubusercontent.com/pyccel/pyccel/HEAD/README.md>
  - <https://github.com/pyccel/pyccel/tree/devel/docs>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/quickstart.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/installation.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/type_annotations.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/compiler.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/openmp.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/ndarrays.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/builtin-functions.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/supported-libraries.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel/devel/docs/decorators.md>
  - <https://github.com/pyccel/pyccel/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://pypi.org/pypi/pyccel/json>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312_requirements.txt>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/laplace_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/midpoint_fixed_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/ackermann_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/poisson_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/dijkstra.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/md_mod.py>
  - <https://github.com/pyccel/pyccel-benchmarks/commits/main>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pyccel/pyccel`) · [data/wave12/enrich/raw/github_com_pyccel_pyccel.json](../../../data/wave12/enrich/raw/github_com_pyccel_pyccel.json) (enrichment confidence 0.7)

</details>
