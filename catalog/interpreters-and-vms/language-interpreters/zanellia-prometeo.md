# prometeo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (transpiler that emits C calling BLASFEO)` · `BSD-2-Clause` · 🔴 abandoned

> Typed-Python-subset DSL transpiled to self-contained C on BLASFEO; beats CPython, Nuitka and PyPy on a Fibonacci loop.

| | |
|---|---|
| **Beats** | CPython 3.7 (also compared with Nuitka and PyPy) |
| **Claimed result** | Fibonacci CPU time (README and examples/fibonacci/CPU_time.txt): CPython 3.7 11.787 s, Nuitka 10.039 s, PyPy3.7 1.78 s, prometeo 0.657 s, about 17.9x faster than CPython, 15.3x faster than Nuitka and 2.7x faster than PyPy (derived from page data). An earlier run set in CPU_time.txt reads Python 27.128 s, Nuitka 12.525 s, prometeo 0.6999 s. Riccati factorization (benchmarks/riccati_benchmark_\*.json, derived from page data): prometeo 2.1x-35.7x faster than NumPy and 2.0x-18.3x faster than Julia across sizes, and 0.84x-1.04x of hand-written C with BLASFEO (parity). |
| **Workload** | Fibonacci: examples/fibonacci/fibonacci.py computes an iterative fib(n) (integer loop, not recursion) 1,000,000 times for each n from 0 to 29 (3e7 calls), run under CPython, Nuitka, PyPy and as prometeo-generated C. Riccati: examples riccati_mass_spring benchmark over state sizes 4-292 versus hand-written BLASFEO C, NumPy and Julia (benchmarks/run_benchmark\*.py). |
| **Metric** | throughput |
| **Hardware** | Dell XPS-9360 with i7-7560U CPU at 2.30 GHz (README says 'all the benchmarks' ran on it) |
| **Compiler and flags** | Generated C is built by pmt's Makefile template with gcc -fPIC -std=c99 and no optimization flag (current template; not stated as the build behind the README table). Python-side harness and flags not in the repo. |
| **Adoption** | 654 stars |
| **Last commit** | 2022-05-19 |
| **Links** | [repository](https://github.com/zanellia/prometeo) · [benchmark](https://raw.githubusercontent.com/zanellia/prometeo/HEAD/README.md) |

## Verdict

First-party only, on a Dell XPS-9360 (i7-7560U at 2.30 GHz): a typed iterative fib loop (3e7 calls, labelled '10E7 runs') took 11.787 s under CPython 3.7, 10.039 s under Nuitka, 1.78 s under PyPy3.7 and 0.657 s as prometeo-generated C (about 17.9x CPython and 2.7x PyPy, derived from page data); a Riccati factorization matched hand-written BLASFEO C (0.84x-1.05x of its speed) and beat NumPy by 2.1x-35.7x and Julia with MKL by 2.0x-18.3x, with prometeo doing one fewer stage than NumPy and Julia.

## Use it when

- Embedded MPC or optimal-control kernels with small-to-medium dense matrices (state sizes about 4-300) that must ship as self-contained C with a bounded, statically known heap.
- Prototyping such kernels in Python syntax and running them under CPython for debugging, then emitting C for an embedded Linux or bare-metal toolchain.
- Small dense linear algebra where NumPy/SciPy call overhead dominates: the Riccati benchmark ran 2.1x-35.7x faster than NumPy, largest at the smallest sizes (derived from page data).
- Typed integer or float loops that need to leave Python without dragging in libpython, where Nuitka or Cython would not be embeddable.

## Skip it when

- General Python code: only a typed subset with a few linear algebra operations is supported (README disclaimer), with no standard library, dynamic typing or Python objects in generated code.
- Production or long-lived projects: last commit and last PyPI release 0.0.11 on 2022-05-19, open issues on overloads (#20) and Apple M1 loading (#23).
- Python 3.10 or newer, or Windows: setup.py pins python_requires '&gt;=3.8, &lt;3.10' and casadi==3.5.5, and pmt raises 'Running on unsupported operating system' outside Linux and macOS.
- Large matrices where BLAS work dominates: the lead over NumPy falls to 2.3x and over Julia with MKL to 2.0x at state size 292, before correcting for the stage-count mismatch noted in gotchas.
- Code that relies on Python's arbitrary-precision integers (see gotchas).

## How it is fast

AST-level transpilation of a statically typed subset to plain C, so integer and float loops become native C loops (Python `int` maps to C `int`, `float` to `double`). Static analysis computes a worst-case heap size and the generated code uses two preallocated bump heaps (8- and 64-byte aligned) instead of malloc and garbage collection. Matrix operations call BLASFEO, a small-matrix BLAS/LAPACK with panel-major storage and hand-tuned kernels, which is where the large wins over NumPy and Julia at small sizes come from.

## Compared with alternatives

Pick prometeo over Codon, Nuitka, Cython or Pythran only when the output must be standalone C with no Python runtime and a bounded heap for small dense linear algebra on embedded targets; for speeding up ordinary Python programs, Codon, Shed Skin or Pythran cover far more of the language.

## Integration

| | |
|---|---|
| **Form** | module (pip package prometeo-dsl with the `pmt` CLI) that emits a source-drop C file, header and Makefile linked against libcpmt and libblasfeo shared libraries |
| **Dependencies** | BLASFEO (git submodule) and libcpmt for generated code; Python side: astpretty, strip_hints, astunparse, numpy, scipy, multipledispatch, pyparsing, casadi==3.5.5, jinja2, numexpr |
| **Minimum toolchain** | Python 3.8-3.9 per setup.py (README says 3.6+); gcc with -std=c99 for generated code |
| **Platforms** | Linux and macOS (pmt refuses other OSes); BLASFEO targets x86-64 and ARM; Apple M1 load failure open as issue #23 |
| **Thread safety** | Not documented; generated code keeps its heap pointers in file-scope globals (___c_pmt_8_heap, ___c_pmt_64_heap), so it is not reentrant across threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Fibonacci harness is uneven and unoptimised: pmt's Makefile template builds generated C with `gcc -fPIC -std=c99` and no -O flag (so it times -O0 code, where gcc cannot hoist the loop-invariant fib call); prometeo's 0.657075 s matches the generated main's printf("%f") timer that starts after heap malloc, CPython's 3-decimal 11.787 s matches pmt's wall-clock around exec(), and the Nuitka and PyPy timing commands are not in the repo.
- Riccati work mismatch (derived from benchmark sources): riccati_mass_spring.py.in runs 4 stages (`for i in range(1, N)`, N=5) while the NumPy template (`range(N)`) and Julia riccati.jl (`1:N`) run 5, so the NumPy and Julia ratios are overstated by up to 1.25x (about 1.7x-28.6x and 1.6x-14.6x after scaling by 4/5, derived from page data); the hand-written BLASFEO C used for the parity line is not in benchmarks/.
- The committed Riccati JSONs cannot be regenerated as is: run_benchmark.py does float(outs) on the program output but the current generator prints 'execution time:...s' and 'total time:...s'; run_benchmark_numpy.py now writes riccati_benchmark_numpy_blasfeo.json, which is not committed and which run_benchmark.py tries to load.
- Python `int` becomes a 32-bit C `int` in generated code, so results can wrap (undefined behaviour in C) past 2^31 while the same program under CPython uses bignums; also the repo LICENSE is BSD-2-Clause but the PyPI metadata says LGPL.

## Known shortcomings

- Fibonacci figure is a toy iterative integer loop (examples/fibonacci/fibonacci.py plus CPU_time.txt, 0.657 s vs CPython 3.7 11.787 s); the Python harness is missing, the gcc template has no -O flag, and prometeo is a Python-to-C transpiler rather than an interpreter. Riccati JSON data gives 2.1-35.7x over NumPy and parity with BLASFEO C (derived from page data). Abandoned since 2022-05.
- Enricher: the Riccati template runs 4 stages (range(1, N)) while the NumPy and Julia versions run 5, so those ratios are overstated up to 1.25x (adjusted about 1.7x-28.6x NumPy and 1.6x-14.6x Julia, derived from page data). Committed JSONs are not reproducible (run_benchmark.py does float(outs) while the current generator prints 'execution time:...s'; the NumPy script writes an uncommitted riccati_benchmark_numpy_blasfeo.json; the hand-written BLASFEO C source is absent). Fib C built with no -O flag; prometeo time from an in-program timer, CPython from a wall clock around exec(); Nuitka and PyPy commands absent. Python int becomes a 32-bit C int; LICENSE BSD-2-Clause but PyPI metadata says LGPL; Python 3.8-3.9 only.

## Caveats and trade-offs

The Fibonacci source is in the repo (examples/fibonacci/fibonacci.py with raw times in CPU_time.txt), but how CPython, Nuitka and PyPy were timed is not, and their versions are only partly given (Python 3.7, PyPy3.7). CPU_time.txt labels the run '10E7 runs' while the code makes 3e7 calls. The benchmark is a statically typed integer loop compiled to C, so an 18x win over CPython says little about general Python code; prometeo accepts only a typed Python subset. The current Makefile template compiles generated C without -O, so the C path may be unoptimized. Not an interpreter: a Python-subset-to-C transpiler compared with CPython, filed here as the closest category. Last commit 2022-05-19. [retier] Python-to-C transpiler, not an interpreter; abandoned since 2022-05, Python 3.8-3.9 only. Fibonacci is a toy iterative integer loop built with no -O flag and timed differently per side. Riccati: prometeo runs 4 stages while NumPy and Julia run 5, so the adjusted ratios are about 1.7x-28.6x over NumPy and 1.6x-14.6x over Julia (derived from page data), parity with BLASFEO C; the committed JSONs are not reproducible from the current scripts. Python int becomes a 32-bit C int.

Not Python semantics: a statically typed DSL subset written in Python syntax with type hints, aimed at embedded high-performance linear algebra (BLASFEO). Output is plain C, so the generated code can be called from C++. Python-to-C transpile step needed; no dynamic features or standard Python libraries in the translated code.

## Maintenance

Abandoned since 2022-05-19 (PyPI 0.0.11, self-described very preliminary) but BSD-2-Clause in the repo and its generated C is plain C99 callable from C++; treat it as a reference design for Python-to-embedded-C with BLASFEO rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (CPython 3.7 11.787 s, Nuitka 10.039 s, PyPy 1.78 s, prometeo 0.657 s) with the CPU model stated and the benchmark source in examples/fibonacci/fibonacci.py, but the Python-side timing harness, interpreter versions and the C compiler and flags behind the table are not stated, so C, not A.
- **Verifier notes:** Numbers match the README; the record wrongly said the Fibonacci source was missing (it is at examples/fibonacci/) and called it recursion (it is an iterative loop). Riccati data files exist and give derived ratios versus NumPy and Julia. Shortcoming to record: toy integer benchmark, Python-side harness missing, transpiler of a typed subset rather than an interpreter, abandoned since 2022.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** stated optimisation flags and a published harness; stage-matched Riccati comparison with committed scripts
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/README.md>
  - <https://github.com/zanellia/prometeo>
  - <https://github.com/zanellia/prometeo/commits>
  - <https://github.com/zanellia/prometeo/tree/master/benchmarks>
  - <https://github.com/zanellia/prometeo/tree/master/examples>
  - <https://github.com/zanellia/prometeo/tree/master/examples/fibonacci>
  - <https://github.com/zanellia/prometeo/tree/master/prometeo>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/examples/fibonacci/CPU_time.txt>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/examples/fibonacci/fibonacci.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/run_benchmark.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_prometeo.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_blasfeo_api.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_numpy.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_julia.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/cmdline/pmt.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/cpmt/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/setup.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/examples/fibonacci/fibonacci.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/examples/fibonacci/CPU_time.txt>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/cpmt/Makefile>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/cmdline/pmt.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/cgen/code_gen_c.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/__init__.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/mem/__init__.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/auxl/__init__.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/prometeo/linalg/__init__.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/run_benchmark.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/run_benchmark_numpy.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/run_benchmark_julia.py>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_mass_spring.py.in>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/test_riccati_numpy.py.in>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/test_riccati.jl>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati.jl>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/Project.toml>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_prometeo.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_blasfeo_api.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_numpy.json>
  - <https://raw.githubusercontent.com/zanellia/prometeo/HEAD/benchmarks/riccati_benchmark_julia.json>
  - <https://github.com/zanellia/prometeo/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/prometeo-dsl/json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/zanellia/prometeo`) · [data/wave12/enrich/raw/github_com_zanellia_prometeo.json](../../../data/wave12/enrich/raw/github_com_zanellia_prometeo.json) (enrichment confidence 0.6)

</details>
