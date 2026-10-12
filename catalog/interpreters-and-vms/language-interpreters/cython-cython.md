# Cython

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Python/C (Python-to-C/C++ compiler)` · `Apache-2.0` · 🟢 active

> Python-to-C/C++ compiler; hand-typed Cython kernels ran 30-190x faster than CPython 3.10, untyped code about 1x.

| | |
|---|---|
| **Beats** | CPython 3.10.7 (kostya/jit-benchmarks 'Python3' rows; Ubuntu 22.10 package, version listed in the README Versions table) |
| **Claimed result** | Cython vs Python3 (CPython 3.10.7) best times, round 1 (2023-02-28): binarytrees 0.81 s vs 73.15 s; fannkuchredux 0.13 s vs 4.04 s; mandelbrot 0.43 s vs 37.52 s; nbody 0.56 s vs 53.72 s; matmul 0.39 s vs 22.73 s; spectralnorm 0.11 s vs 20.69 s; pidigits 1.73 s vs 6.17 s (about 31x to 188x on the numeric kernels, derived from page data). Small or no win on text tests: fasta 6.81 s vs 8.65 s, knucleotide 8.33 s vs 8.41 s; slower on regexdna 6.1 s vs 5.2 s; brainfuck 165.97 s vs CPython timing out above 190 s. No Cython row for brainfuck2 or revcomp. |
| **Workload** | kostya/jit-benchmarks: benchmarks-game programs (binarytrees, fannkuchredux, mandelbrot, nbody, matmul and others) run as CPython scripts and as Cython-compiled .pyx files. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80 GB DDR4-3200, Docker on Ubuntu 22.10 (README, round 1 dated 2023-02-28) |
| **Compiler and flags** | Cython 0.29.30 (Ubuntu cython3 package) `cython3 --embed test.pyx`, then gcc (Ubuntu 22.10 build-essential; the suite reports gcc 12.2.0) `-O3 -march=native -fomit-frame-pointer -funroll-loops -Wno-unused-result -g`, linked with -lpython3.10 (tools/languages.rb, GCC_FLAGS and the cython build_cmd). |
| **Adoption** | 10.9k stars; README cites more than 70 million PyPI downloads per month |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/cython/cython) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

In kostya/jit-benchmarks round 1 (2023-02-28, AMD Ryzen 7 3800X, Docker on Ubuntu 22.10), Cython 0.29.30 --embed output built with gcc 12.2.0 -O3 -march=native ran hand-typed .pyx ports against idiomatic CPython 3.10.7 scripts: binarytrees 0.81 vs 73.15 s, mandelbrot 0.43 vs 37.52 s, nbody 0.56 vs 53.72 s, spectralnorm 0.11 vs 20.69 s, matmul 0.39 vs 22.73 s, fannkuchredux 0.13 vs 4.04 s and pidigits (GMP) 1.73 vs 6.17 s (best in-process times). Lightly typed ports were level or slower: fasta 6.81 vs 8.65 s, knucleotide 8.33 vs 8.41 s, regexdna 6.1 vs 5.2 s.

## Use it when

- Numeric inner loops on doubles and ints that you are willing to annotate with C types (n-body, mandelbrot, spectral norm, matrix multiply style kernels), where the suite shows 30-190x over CPython.
- Wrapping existing C or C++ libraries for Python, or calling them from hot paths (generated code can be C++ with --cplus).
- Speeding up a module while staying on CPython with full access to its C-extension ecosystem, which PyPy and Codon do not fully offer.
- Incremental optimization: compile unchanged Python first, then add types only where profiling shows the time goes.
- Shipping a single executable that embeds the interpreter (cython --embed, as this benchmark did).

## Skip it when

- You expect large gains on unmodified Python: the suite's barely typed ports gain little or lose (regexdna 6.1 s vs CPython 5.2 s, knucleotide 8.33 vs 8.41, fasta 6.81 vs 8.65).
- The time is already spent in C-implemented builtins or stdlib modules (re, dict, str operations), where removing interpreter dispatch saves almost nothing.
- You cannot add a C compiler and per-platform binary wheels to the build, or need a pure-Python package.
- You build against the Limited API (abi3) for speed-critical code: open issue #6741 reports Limited-API builds 2x to 12x slower than regular Cython builds on its benchmarks.
- A JIT on unmodified code is acceptable: PyPy reached 0.54 s on mandelbrot and 0.36 s on matmul in the same suite without type annotations.

## How it is fast

Typed code is lowered to plain C: cdef int/double variables, C structs, malloc'd arrays and cdef functions compile to unboxed arithmetic and direct C calls with no bytecode dispatch, reference counting or dynamic lookup, which gcc then optimizes (-O3 -march=native in the benchmark). Untyped code still goes through the CPython C-API on PyObjects, so it saves only interpreter dispatch overhead. 'cdef extern from' lets a kernel call a C library directly; the pidigits kernel calls GMP's mpz functions.

## Compared with alternatives

Pick Cython over PyPy, GraalPy or Codon when you must stay on CPython with its C extensions, and over mypyc or Nuitka (which compile type-hinted or plain Python for 1.5-5x at best) when you are willing to write C-level types to get C speed or need to wrap C/C++ code; pick PyPy or Codon instead when the code should stay unmodified Python.

## Integration

| | |
|---|---|
| **Form** | module (build-time compiler, pip install Cython, that emits C/C++ for extension modules or embedded executables) |
| **Dependencies** | a C or C++ compiler and the target Python's headers/libpython; Cython itself is needed only at build time; GMP in the benchmark's pidigits kernel only |
| **Minimum toolchain** | Python 3.9+ for current Cython (setup.py python_requires); C99 compiler for generated code since 3.1; the benchmark used Cython 0.29.30 with gcc 12.2.0 |
| **Platforms** | any platform with a CPython C toolchain (setup.py lists OS Independent); classifiers also list PyPy and GraalPy |
| **Thread safety** | Generated code follows CPython's GIL model; nogil sections release the GIL for pure C code, and the 3.2-3.3 changelogs carry fixes for free-threading builds |
| **Drop-in for the baseline** | partial — most Python modules compile unchanged into extension modules with the same behaviour, but the measured speedups need Cython-specific C typing, i.e. different source |

## Gotchas

- The benchmark's .pyx files are C written in Cython syntax, not compiled Python: binarytrees, nbody, fannkuchredux, matmul and spectralnorm use C structs or malloc'd arrays (fannkuchredux, matmul and spectralnorm never free them, so memory grows over the five in-process repetitions; matmul MaxMem 84.5 MB vs 16.6 MB for C), and Cython ties or beats the suite's own C entries on five kernels (fannkuchredux 0.13 s vs C 0.21 s uses a cheaper permutation loop than test.c).
- pidigits' 3.6x (1.73 s vs 6.17 s) comes from calling GMP directly (cdef extern from "gmp.h", linked with -lgmp) against CPython's built-in integers; it measures a C bignum library, not compiled Python.
- The .pyx files rely on Cython 0.29's language_level=2 default (Python 2 print statements in pidigits, binarytrees and spectralnorm); Cython 3.0 (2023-07-17) changed the default to 3str and 3.1 to 3 and dropped Python 2.7-3.7, so they do not build unchanged on current Cython without a language_level=2 directive.
- Timing is the best of up to 5 repetitions inside one process, read from each program's own time.time() report, so start-up and the 0.8-2.6 s Cython+gcc compile are excluded; output correctness is checked only on small debug inputs. Upstream also has open slowdown reports: #6597 (compiled try/except plus list.append 48% slower than CPython, Cython 3.0.11) and #6710 (performance regressions in 3.1).

## Known shortcomings

- kostya/jit-benchmarks numbers (Cython 0.29.30, CPython 3.10.7, gcc -O3 -march=native -funroll-loops, Ryzen 7 3800X) come from hand-typed C-like .pyx sources with malloc'd structs rather than idiomatic Python; slower than CPython on regexdna (6.1 vs 5.2 s), level on knucleotide, 2023 versions, single CPython runs. Ahead-of-time compiler, not an interpreter.
- Enricher: the pidigits .pyx calls GMP directly (cdef extern gmp.h, -lgmp), so its 3.6x is GMP against CPython int rather than compiled Python; the typed .pyx files are C in Cython syntax and tie or beat the suite's own C rows on 5 kernels, fannkuch uses a cheaper loop than test.c, and fannkuch, matmul and spectralnorm never free their mallocs. The .pyx files need language_level=2 (Python 2 print statements) and do not build on Cython 3.x. Open upstream issues #6597, #6741, #6710.

## Caveats and trade-offs

The .pyx files are hand-typed Cython that is close to C: binarytrees allocates C structs with malloc/free while the CPython test.py builds Python class instances, and nbody uses cdef structs and extern math.h (Cythonized by Robert Bradshaw), so the numbers measure statically typed Cython, not unmodified Python compiled by Cython. Several CPython rows are a single run (binarytrees, nbody). Time is measured inside the program with time.time(), so process start-up and the 0.8-2.6 s Cython+gcc compile time are excluded. Versions are old (Cython 0.29.30, Python 3.10.7, round 1 dated 2023-02-28, not rerun). Cython's own README makes no numeric speed claim. Cython is a Python-to-C compiler rather than an interpreter.

Needs a build step and a C/C++ compiler; the large speedups require cdef type annotations and C-level constructs, i.e. effectively a different (typed) program. Output can be C++ and linked from C++ code.

## Maintenance

Actively maintained (3.3.0 released 2026-08-22 per CHANGES.rst, Apache-2.0, 10.9k stars) and a build-time-only dependency, but the measured versions (Cython 0.29, Python 3.10) are two major releases old and the benchmark's .pyx files need language_level=2 to build on Cython 3.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: the independent kostya/jit-benchmarks suite publishes the benchmark code (&lt;bench&gt;/test.pyx and test.py), the exact build command and flags (tools/languages.rb: cython3 --embed, then gcc -O3 -march=native -fomit-frame-pointer -funroll-loops -g against libpython3.10), versions (Cython 0.29.30, Python 3.10.7, gcc 12.2.0 on the Ubuntu 22.10 base image) and the CPU (AMD Ryzen 7 3800X).
- **Verifier notes:** All numbers checked against the kostya/jit-benchmarks README rows; the record wrongly said the interpreter version and compiler flags were unstated (README Versions table and tools/languages.rb give them), which lifts the tier to A. Shortcomings to record: typed C-like .pyx vs idiomatic Python (different source per side), slower than CPython on regexdna and level on knucleotide, old 2023 versions, single CPython runs on the slowest rows.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://github.com/kostya/jit-benchmarks>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/cython3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/python3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.pyx>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/README.rst>
  - <https://github.com/cython/cython>
  - <https://github.com/cython/cython/commits>
- **Sources the enricher read:**
  - <https://github.com/cython/cython>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/README.rst>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/CHANGES.rst>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/setup.py>
  - <https://raw.githubusercontent.com/cython/cython/HEAD/pyproject.toml>
  - <https://github.com/cython/cython/issues?q=is%3Aissue%20state%3Aopen%20label%3Aperformance>
  - <https://github.com/cython/cython/issues/6597>
  - <https://github.com/cython/cython/issues/6741>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://github.com/kostya/jit-benchmarks/tree/master/tools>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/python3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/cython3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.c>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/pidigits/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/pidigits/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fasta/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fasta/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/regexdna/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/regexdna/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.pyx>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/cython/cython`) · [data/wave12/enrich/raw/github_com_cython_cython.json](../../../data/wave12/enrich/raw/github_com_cython_cython.json) (enrichment confidence 0.75)

</details>
