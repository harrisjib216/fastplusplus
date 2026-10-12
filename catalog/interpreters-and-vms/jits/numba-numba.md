# Numba

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python (LLVM-based JIT; C extension components)` · `BSD-2-Clause` · 🟢 active

> LLVM-based JIT for numeric Python: @njit-compiled NumPy loops run 1.4x to 450x faster than CPython 3.12 in pyccel-benchmarks.

| | |
|---|---|
| **Beats** | CPython 3.12 (interpreted Python; the dev-branch workflow sets python-version 3.12 via actions/setup-python, so the version is stated, not inferred; tables for 3.10, 3.11, 3.13 and 3.14 use the PyPI Pyccel 2.2.3 run) |
| **Claimed result** | pyccel-benchmarks dev-branch execution-time table (ms, CPython column vs numba column): Ackermann 456.00 vs 8.58; Bellman Ford 1950.00 vs 4.63; Dijkstra 5530.00 vs 19.80; Euler 3900.00 vs 36.70; RK4 19800.00 vs 127.00; FD L Convection 2280.00 vs 12.70; FD Poisson 6140.00 vs 13.60; FD Laplace 729.00 vs 510.00; M-D 8530.00 vs 56.80; Splines 1770.00 vs 18.00. Ratios across all 13 kernels range from 1.4x (FD Laplace) to 451.5x (FD Poisson), geometric mean about 115x (derived from page data). |
| **Workload** | 13 numeric kernels in benchmarks/tests (Ackermann, Bellman-Ford, Dijkstra, Euler, midpoint explicit/fixed, RK4, linear and non-linear convection, Poisson, Laplace, molecular dynamics, splines) written as scalar loops over NumPy arrays; execution time in ms from python3 -m timeit (best of 5), compilation excluded; compile time reported separately as CPU seconds (getrusage). |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest shared runner (CPU model not recorded) |
| **Compiler and flags** | Numba 0.66.0 with llvmlite 0.48.0 (version_specific_results/devel_performance_312_requirements.txt); kernels use @njit(fastmath=True), otherwise identical to the CPython source; CPython 3.12 from actions/setup-python; execution timed with 'python3 -m timeit' (best of 5), so Numba's JIT compilation falls outside the minimum |
| **Adoption** | 11.2k stars, 1.3k forks; on PyPI (0.68.0, released 2026-09-30); the benchmark measured 0.66.0 |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/numba/numba) · [benchmark](https://github.com/pyccel/pyccel-benchmarks) |

## Verdict

In the Pyccel developers' pyccel-benchmarks dev-branch run (2026-08-03, GitHub Actions ubuntu-latest, CPU not recorded), Numba 0.66.0 with llvmlite 0.48.0 and @njit(fastmath=True) beat interpreted CPython 3.12 on all 13 kernels, from 1.4x on the vectorised FD Laplace to 451x on FD Poisson (geometric mean about 115x, derived from page data), timed with python -m timeit best of 5 after timeit's autorange call absorbed the JIT compilation.

## Use it when

- Hot scalar loops over NumPy arrays that cannot be expressed as whole-array NumPy calls: graph algorithms, ODE time stepping, stencils written element by element (Poisson 451x, Bellman-Ford 421x, Dijkstra 279x over CPython in the benchmark, derived from page data).
- Functions that run long enough (docs: above about 10 us per call) to amortise dispatch, and processes that live long enough to amortise 0.3 to 6.8 CPU seconds of first-call compilation per kernel, or that can use cache=True.
- Pure-Python projects that want a pip-installable accelerator without a C/C++ build step: wheels exist for CPython 3.10 to 3.15 (including free-threaded 3.14t) on Linux x86-64 and aarch64, Windows x64/arm64 and macOS arm64.
- Multithreaded numeric code where nogil=True or parallel=True lets compiled kernels run on several cores without the GIL.

## Skip it when

- Code that is already vectorised NumPy: in the same benchmark the whole-array FD Laplace kernel is only 1.4x faster than CPython, and Numba's own docs show an @njit-decorated NumPy expression running at NumPy speed (0.659 s vs 0.581 s without Numba).
- Short-lived scripts or functions under about 10 us: JIT compilation (0.33 to 6.75 CPU s per kernel here) and call dispatch dominate; the FAQ says to leave such functions alone.
- When the last 2x to 8x matters: on the finite-difference kernels Numba trails pythran_gnu by 4.6x to 8.4x, and on Midpoint Fixed it is 297 ms vs 7.24 ms for pyccel_intel_c (derived from page data); ahead-of-time translators win there.
- Object-heavy Python (classes beyond @jitclass, async, dict/set comprehensions, \*\*kwargs, re-raised exceptions): unsupported in nopython mode.
- Calling from C++ without a Python runtime: the numba.pycc ahead-of-time path is deprecated.

## How it is fast

Type inference over Python bytecode turns dynamically typed loops into statically typed LLVM IR (via llvmlite), so element accesses on NumPy arrays become native loads and stores with no boxing or interpreter dispatch. LLVM then optimises and, with fastmath=True, may reassociate floating-point reductions so they vectorise (the docs' sqrt-sum example drops from 35.2 ms to 17.8 ms). Compiled functions can release the GIL (nogil=True) and parallel=True splits supported loops across a threading layer (TBB, OpenMP or workqueue).

## Compared with alternatives

Pick Numba over the CPython copy-and-patch JIT (7-8% geomean) or Cinder (1.5-4x) when the hot code is numeric loops over NumPy arrays, where Numba gains one to two orders of magnitude; pick it over Hana Jit, PPy or DIO-JIT when maturity matters, since those smaller JITs claim wins over Numba on a few microbenchmarks but lack its 11.2k-star user base, wheels for every current CPython and Anaconda-sponsored maintenance.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | llvmlite (0.50.x for Numba 0.68.0, bundles LLVM), NumPy &gt;=1.22,&lt;2.6; optional TBB or OpenMP for parallel=True |
| **Minimum toolchain** | CPython 3.10+ (0.68.0 wheels for 3.10 to 3.15 and 3.14t); no compiler needed at install time |
| **Platforms** | Linux x86-64 and aarch64, Windows 10+ x64 (arm64 wheels for 3.12+), macOS 11+ arm64; parallel=True only on 64-bit; NVIDIA GPUs of compute capability 5.0+ listed as a supported target |
| **Thread safety** | Compiled functions may run concurrently when nogil=True, with the usual race caveats left to the user; for parallel=True the 'default' threading layer gives no specific safety guarantee, 'threadsafe'/'forksafe'/'safe' (TBB) can be requested. |
| **Drop-in for the baseline** | partial — add @njit to existing functions; only the supported Python/NumPy subset compiles, and the first call per type signature pays compilation |

## Gotchas

- Harness note: the record's 'scalar loops' description is not true for every kernel. FD Laplace is whole-array NumPy slicing in both the CPython and Numba files (only the decorator differs), which is why it gains only 1.4x; the ODE kernels (Euler, midpoint, RK4) apply NumPy slice operations to 1-element rows a million times, a CPython worst case that inflates those ratios. The harness never compares outputs across accelerators, and every compiled column uses fast-math (Numba fastmath=True; pyccel and pythran -O3 -march=native -ffast-math).
- fastmath=True, used in all benchmark kernels, changes IEEE semantics: the docs show (x - y) + y with y = inf returning 0.0 instead of nan. Global variables are frozen as compile-time constants, and KeyboardInterrupt is ignored until compiled code returns.
- cache=True stores compiled code as pickles; loading a malicious cache file executes arbitrary code, so the cache directory must be trusted.
- The measured 0.66.0 and the current 0.68.0 carry an open 1D array-indexing regression (issue #10851, opened 2026-09-22: reads about 1.64x and writes about 1.67x slower than 0.65 on arrays above about 5000 elements, now slower than plain NumPy), milestoned for 0.68.1; 55 open performance-labelled issues include slow non-contiguous sum (#9819) and a jitclass slowdown since 0.62 (#10451).

## Known shortcomings

- pyccel-benchmarks run on a GitHub Actions runner with no CPU model, fastmath=True (numba 0.66.0, Python 3.12), and a CPython baseline that loops over NumPy elements one by one; FD Laplace gains only 1.4x. Python JIT, not C++; filed under jits.
- Enricher: the pyccel-benchmarks workload is not all scalar loops (FD Laplace is whole-array NumPy slicing in both the CPython and Numba files, so its 1.4x is the vectorised-code number) while the ODE kernels (Euler, midpoint, RK4) slice 1-element rows a million times, a CPython worst case that inflates the ratios; the harness never checks outputs and all compiled columns use fast-math. Open issue #10851: 1D indexing about 1.64x slower in 0.66-0.68.0.

## Caveats and trade-offs

Numbers come from the README of the Pyccel developers' benchmark repository (pyccel/pyccel-benchmarks, 5 stars), not from Numba's repo; the Numba README gives no numbers. The dev-branch run (dated Mon Aug 3 10:56:24 UTC 2026) is a GitHub Actions ubuntu-latest job on a shared VM with no CPU model recorded, timed with python3 -m timeit best-of-5 rather than pyperf. The CPython column runs scalar loops that index NumPy arrays element by element, the slowest way to use NumPy, so the ratios (1.4x to 451.5x, geometric mean about 115x, derived from page data) do not transfer to code that is already vectorised. Numba is compiled with fastmath=True. It is the weakest accelerator on FD Laplace (1.4x over CPython) and trails pythran_gnu by 4.6x to 8.4x on the four finite-difference kernels (derived from page data), while beating pythran_gnu on RK4 (127 ms vs 152 ms). Measured version 0.66.0; PyPI is at 0.68.0. Compile time (unit is CPU seconds) is 0.33 to 6.75 s per kernel for Numba.

Numerical subset of Python and NumPy only (nopython mode); JIT warm-up cost on first call (README compile-time column for Numba: 0.33 to 6.75 per kernel, unit not labelled); needs LLVM via llvmlite; not usable from plain C++ except through the Python runtime.

## Maintenance

Actively maintained (last commit 2026-10-05, 0.68.0 on PyPI 2026-09-30), BSD-2-Clause and pip/conda installable, so copyable as a dependency; the benchmark is independent (B) but from a single shared-VM run with no CPU model and no output validation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent automated shootout by the Pyccel developers (pyccel/pyccel-benchmarks: benchmarks/run_benchmarks.py, benchmarks/tests/numba_\*.py, .github/workflows/run_benchmarks.yml) with versions pinned in version_specific_results/devel_performance_312_requirements.txt (numba 0.66.0, llvmlite 0.48.0); every quoted CPython and numba value is in the README's dev-branch table. Not A because it runs on a GitHub Actions ubuntu-latest shared runner whose CPU model is never recorded; third party to Numba, so B.
- **Verifier notes:** All CPython and numba values in claimed_speedup match the dev-branch table and the derived ratios check out (geometric mean 114.9x). The requirements file the search agent could not open is version_specific_results/devel_performance_312_requirements.txt; it pins numba 0.66.0 and the workflow pins Python 3.12. Numba is a JIT, so the 'jits' category may fit better than language-interpreters.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/numba/numba>
  - <https://github.com/numba/numba/commits>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/LICENSE>
  - <https://pypi.org/pypi/numba/json>
  - <https://github.com/pyccel/pyccel-benchmarks>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://github.com/pyccel/pyccel-benchmarks/tree/main/version_specific_results>
  - <https://github.com/pyccel/pyccel-benchmarks/tree/main/.github/workflows>
  - <https://github.com/pyccel/pyccel-benchmarks/tree/main/benchmarks/tests>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312_requirements.txt>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/actions/linux_install/action.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/poisson_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_poisson_2d_mod.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/numba/numba/HEAD/README.rst>
  - <https://github.com/numba/numba>
  - <https://pypi.org/pypi/numba/json>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/5minguide.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/performance-tips.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/faq.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/threading-layer.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/jit.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/installing.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/user/withobjmode.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/reference/fpsemantics.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/reference/pysupported.rst>
  - <https://raw.githubusercontent.com/numba/numba/HEAD/docs/source/reference/deprecation.rst>
  - <https://github.com/numba/numba/issues?q=is%3Aissue%20state%3Aopen%20label%3Aperformance>
  - <https://github.com/numba/numba/issues/10851>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/laplace_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_laplace_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/linearconv_1d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_linearconv_1d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/poisson_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_poisson_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/euler_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_euler_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/rk4_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_rk4_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/splines.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_splines.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/ackermann_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_ackermann_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/bellman_ford_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_bellman_ford_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/dijkstra.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_dijkstra.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/midpoint_explicit_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_midpoint_explicit_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/midpoint_fixed_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_midpoint_fixed_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/nonlinearconv_1d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_nonlinearconv_1d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/md_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/numba_md_mod.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/numba/numba`) · [data/wave12/enrich/raw/github_com_numba_numba.json](../../../data/wave12/enrich/raw/github_com_numba_numba.json) (enrichment confidence 0.8)

</details>
