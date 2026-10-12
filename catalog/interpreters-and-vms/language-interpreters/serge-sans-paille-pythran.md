# Pythran

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python (compiler that emits C++)` · `BSD-3-Clause` · 🟢 active

> Ahead-of-time compiler from a NumPy-flavoured Python subset to C++17 extension modules; 11x-2096x faster than CPython on loop kernels.

| | |
|---|---|
| **Beats** | CPython 3.12 (interpreted Python; the dev-branch workflow sets python-version 3.12 via actions/setup-python, so the version is stated, not inferred; tables for 3.10, 3.11, 3.13 and 3.14 use the PyPI Pyccel 2.2.3 run) |
| **Claimed result** | pyccel-benchmarks dev-branch execution-time table (ms, CPython column vs pythran_gnu column): Ackermann 456.00 vs 2.70; Bellman Ford 1950.00 vs 4.58; Dijkstra 5530.00 vs 18.00; Euler 3900.00 vs 26.10; RK4 19800.00 vs 152.00; FD L Convection 2280.00 vs 1.52; FD Poisson 6140.00 vs 2.93; FD Laplace 729.00 vs 67.10; M-D 8530.00 vs 36.30. Ratios across the 12 supported kernels range from 10.9x (FD Laplace) to 2095.6x (FD Poisson), geometric mean about 264x (derived from page data). Splines is unsupported ('-'). |
| **Workload** | 13 numeric kernels in benchmarks/tests (Ackermann, Bellman-Ford, Dijkstra, Euler, midpoint explicit/fixed, RK4, linear and non-linear convection, Poisson, Laplace, molecular dynamics, splines) written as scalar loops over NumPy arrays; execution time in ms from python3 -m timeit (best of 5), compilation excluded; Splines is unsupported by Pythran. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest shared runner (CPU model not recorded) |
| **Compiler and flags** | Pythran 0.18.1 (version_specific_results/devel_performance_312_requirements.txt); pythran_gnu column uses benchmarks/pythran_gnu.config: cflags -std=c++14 -fno-math-errno -fvisibility=hidden -fno-wrapv -Wno-unused-function -Wno-int-in-bool-context -Wno-unknown-warning-option -O3 -march=native -mtune=native -mavx -ffast-math, ldflags -fvisibility=hidden -Wl,-strip-all; system GNU g++ on ubuntu-latest (version not recorded); a pythran_intel column uses Intel oneAPI; execution timed with 'python3 -m timeit' (best of 5) |
| **Adoption** | 2.1k stars, 203 forks; on PyPI (0.19.0, released 2026-08-17) and conda-forge; Arch (pacman python-pythran) and Fedora (dnf install pythran) packages per the README, whose Debian/Ubuntu section installs with pip; the benchmark measured 0.18.1 |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/serge-sans-paille/pythran) · [benchmark](https://github.com/pyccel/pyccel-benchmarks) |

## Verdict

In the Pyccel developers' pyccel-benchmarks GitHub Actions run (ubuntu-latest shared VM, CPU model and g++ version unrecorded, 2026-08-03), Pythran 0.18.1 built with g++ -O3 -march=native -mavx -ffast-math ran 12 numeric kernels 10.9x (FD Laplace) to 2096x (FD Poisson) faster than CPython 3.12, geometric mean about 264x (derived from page data), timed with python3 -m timeit best of 5, compile time excluded; Splines did not compile.

## Use it when

- Hot numeric kernels written as explicit Python loops that index NumPy arrays element by element (stencils, finite differences, graph shortest paths): 130x-2096x over CPython 3.12 in the pyccel-benchmarks run.
- You want to keep one pure-Python source file that still runs uncompiled, with types given only in '# pythran export' comments rather than Cython-style declarations.
- Code that mixes NumPy array expressions with loops and can use the optional xsimd vectorisation and '#omp parallel for' OpenMP loops (neither was enabled in the cited benchmark).
- Building wheels with setuptools or Meson for Linux, macOS or Windows (clang-cl) where a C++17 compiler is available at build time.
- Recursive integer code such as Ackermann (169x over CPython) as long as values fit in a C long.

## Skip it when

- Code that already spends its time inside vectorised NumPy calls: the one baseline that used NumPy slicing (FD Laplace) gained only 10.9x, and open issues report Pythran slower than NumPy on array assignment (#2095), some broadcasting patterns above \~20 columns (#2019) and slower than SciPy on long-double convolution (#2275).
- Object-oriented code: classes are not supported (the Splines benchmark, a class, does not compile), nor are heterogeneous lists or arbitrary-precision integers.
- Small-array ODE-style kernels that pass function arguments and operate on 1-element arrays: Pythran trailed Pyccel 3.8x on Euler, 4.1x on Midpoint Explicit and 5.6x-37x on Midpoint Fixed in the same table.
- Environments without a C++17 compiler at install/build time, or where 2-7.5 CPU s of compile time per module (higher than Pyccel's 1.6-3.1 s in the same run) matters.
- Calls on small inputs where argument conversion dominates: non-ndarray arguments are deep-copied at the Python boundary (open issue #2012).

## How it is fast

Type inference from the export signatures lets it instantiate monomorphic, heavily templated C++ (the MANUAL's description), so element-wise loops over NumPy arrays become plain C++ loops with no interpreter dispatch or boxing, which the C++ compiler can auto-vectorise. NumPy expressions are handled in that template layer with laziness analysis and expression combiners (named in recent commits and the 0.19.0 Changelog) to avoid intermediate arrays, with optional explicit SIMD through xsimd (-DUSE_XSIMD) and OpenMP from '#omp parallel for' comment annotations (-fopenmp). Range and alias analysis (helped by asserts) speeds indexing, and the GIL is released while the compiled function runs.

## Compared with alternatives

Pick Pythran over Pyccel when the kernel uses richer Python (comprehensions, dicts, sets, exceptions, polymorphic helpers) or NumPy expressions, and over Cython when you want the source to stay plain Python with types only in export comments. In the same run Pythran had the fastest M-D (36.3 ms) and Dijkstra (pythran_intel 16.8 ms) rows while Pyccel won Ackermann, Euler, Midpoint and RK4. Shed Skin or Codon fit whole programs with classes better, since Pythran does not support classes.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python &gt;=3.7, ply, gast \~0.7.0, beniget \~0.5.0, numpy, setuptools; Boost and xsimd headers (vendored in the PyPI package, may be unvendored by conda-forge and distros); a BLAS (configurable: none, scipy-openblas, openblas, mkl and others); a C++17 compiler at build time |
| **Minimum toolchain** | C++17 compiler from 0.19.0 (Changelog 'Bump C++ dependency to C++17'); the MANUAL FAQ still lists g++ 4.9+ and clang++ 3.5+, which is stale; Python 3.7+ |
| **Platforms** | Linux and macOS (PyPI classifiers); Windows described as ongoing, with Visual Studio 2017 or clang-cl; 32-bit compatibility improved in 0.19.0; xsimd SIMD optional |
| **Thread safety** | Releases the GIL during the compiled call; internal reference counting is non-atomic for non-OpenMP code unless built with -DTHREAD_SAFE_REF_COUNT (small penalty); free-threading support added in 0.18.0 via a config option |
| **Drop-in for the baseline** | partial — the compiled module is a drop-in import replacement for the .py module, but only for code inside Pythran's subset (no classes, homogeneous containers, C long integers) with export signatures added |

## Gotchas

- Harness flaw in the cited benchmark: pyccel-benchmarks' run_benchmarks.py never compares outputs between CPython and the compiled versions, so with -ffast-math a numerically different result would go unnoticed; FD Laplace also stops on a relative-tolerance test, so its iteration count (and time) can differ between implementations.
- The cited table is not a scalar-loop-only baseline as the record says: FD Laplace's CPython code uses NumPy slice expressions (hence only 10.9x), and the ODE kernels (Euler, Midpoint, RK4) run on 1-element arrays with a function argument.
- The benchmark's pythran_gnu.config defines no USE_XSIMD and no -fopenmp, so the measured numbers use g++ auto-vectorisation only; it also passes -std=c++14, which matched 0.18.1 but conflicts with 0.19.0's C++17 requirement, so copy it with care.
- Integers are C long (system-dependent width, no overflow promotion), and non-ndarray arguments are deep copies, so in-place mutation of a list argument is not visible to the caller.

## Known shortcomings

- pyccel-benchmarks run (Pythran 0.18.1, cflags from benchmarks/pythran_gnu.config) with no CPU model or g++ version and -ffast-math; Splines unsupported; geomean 264.0x over 12 kernels against a CPython baseline that loops over NumPy elements one by one. Ahead-of-time Python-to-C++ compiler.
- Enricher: pyccel-benchmarks' run_benchmarks.py never compares outputs across implementations, so -ffast-math result drift goes unseen and FD Laplace (stopped by an rtol test) can run different iteration counts; the Laplace CPython baseline uses NumPy slices (hence only 10.9x) while the ODE kernels run on 1-element arrays. pythran_gnu.config has no USE_XSIMD and no -fopenmp (auto-vectorisation only) and passes -std=c++14, conflicting with 0.19.0's C++17 bump; Pyccel is 3.8x-37x faster on Euler and Midpoint.

## Caveats and trade-offs

Numbers come from the README of the Pyccel developers' benchmark repository (pyccel/pyccel-benchmarks, 5 stars; Pyccel competes with Pythran), not from Pythran's repo; the Pythran README gives no numbers. The dev-branch run (dated Mon Aug 3 10:56:24 UTC 2026) is a GitHub Actions ubuntu-latest job on a shared VM with no CPU model or g++ version recorded, built with -march=native -ffast-math and timed with python3 -m timeit best-of-5 rather than pyperf. The CPython column runs scalar loops that index NumPy arrays element by element, so the ratios (10.9x to 2095.6x over 12 kernels, geometric mean about 264x, derived from page data) do not transfer to vectorised NumPy code. Splines does not compile under Pythran ('-'). pythran_gnu trails Numba on RK4 (152 ms vs 127 ms) and trails pythran_intel there (36.1 ms) and on Midpoint Fixed (266 ms vs 92.4 ms). Compile time (unit is CPU seconds) is 2.14 to 7.50 s per kernel for pythran_gnu. Measured version 0.18.1; PyPI is at 0.19.0. [retier] Numbers come from the Pyccel developers' benchmark repository (pyccel/pyccel-benchmarks, Pyccel competes with Pythran), not Pythran's own; GitHub Actions ubuntu-latest run with no CPU model or g++ version. pythran_gnu.config: -ffast-math, no USE_XSIMD and no -fopenmp (auto-vectorisation only), -std=c++14 (conflicts with Pythran 0.19.0's C++17 bump). The harness never compares outputs across implementations, FD Laplace stops on an rtol test so iteration counts can differ, the Laplace CPython baseline uses NumPy slices (hence only 10.9x) and the ODE kernels run on 1-element arrays, a CPython worst case. Splines unsupported; Pyccel is 3.8x-37x faster on Euler and Midpoint. Ahead-of-time Python-to-C++ compiler.

Only a numeric subset of Python (with NumPy support) compiles; needs '# pythran export' signatures and a C++ compiler at build time; produces a native extension module with the same interface.

## Maintenance

Actively maintained (0.19.0 on PyPI 2026-08-17, commits through 2026-09-14), BSD-3-Clause and packaged on PyPI, conda-forge, Arch and Fedora, but 140 open issues include a long tail of performance gaps versus NumPy, SciPy and Julia.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent automated shootout by the Pyccel developers (pyccel/pyccel-benchmarks: benchmarks/run_benchmarks.py, benchmarks/tests/\*.py with '# pythran export' lines, benchmarks/pythran_gnu.config) with Pythran 0.18.1 pinned in the requirements file and full cflags public; every quoted CPython and pythran_gnu value is in the README's dev-branch table. Not A because the GNU compiler version and the CPU model of the GitHub Actions ubuntu-latest runner are never recorded; third party to Pythran, so B.
- **Verifier notes:** All CPython and pythran_gnu values in claimed_speedup match the dev-branch table and the derived ratios check out (geometric mean 264.0x over 12 kernels). Flags confirmed from benchmarks/pythran_gnu.config (the README's benchmarks/config.pythranrc link is a 404). Metadata checked on the GitHub page and PyPI: BSD-3-Clause, last commit 2026-09-14.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/serge-sans-paille/pythran>
  - <https://github.com/serge-sans-paille/pythran/commits>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/README.rst>
  - <https://pypi.org/pypi/pythran/json>
  - <https://github.com/pyccel/pyccel-benchmarks>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://github.com/pyccel/pyccel-benchmarks/tree/main/version_specific_results>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312_requirements.txt>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/actions/generate_pyccel_config/action.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/pythran_gnu.config>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/poisson_2d_mod.py>
- **Sources the enricher read:**
  - <https://github.com/serge-sans-paille/pythran>
  - <https://github.com/serge-sans-paille/pythran/commits>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/README.rst>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/setup.py>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/Changelog>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/docs/MANUAL.rst>
  - <https://raw.githubusercontent.com/serge-sans-paille/pythran/HEAD/docs/TUTORIAL.rst>
  - <https://pypi.org/pypi/pythran/json>
  - <https://github.com/serge-sans-paille/pythran/issues?q=is%3Aissue+is%3Aopen+slower>
  - <https://github.com/serge-sans-paille/pythran/issues/2389>
  - <https://github.com/serge-sans-paille/pythran/issues/2019>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/pythran_gnu.config>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/version_specific_results/devel_performance_312_requirements.txt>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/.github/workflows/run_benchmarks.yml>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/poisson_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/linearconv_1d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/laplace_2d_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/ackermann_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/splines.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/midpoint_fixed_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/rk4_mod.py>
  - <https://raw.githubusercontent.com/pyccel/pyccel-benchmarks/HEAD/benchmarks/tests/md_mod.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/serge-sans-paille/pythran`) · [data/wave12/enrich/raw/github_com_serge_sans_paille_pythran.json](../../../data/wave12/enrich/raw/github_com_serge_sans_paille_pythran.json) (enrichment confidence 0.8)

</details>
