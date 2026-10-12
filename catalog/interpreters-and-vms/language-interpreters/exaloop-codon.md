# Codon

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> LLVM-based ahead-of-time compiler for a statically typed Python subset; 10-90x faster than CPython, mostly ahead of PyPy.

| | |
|---|---|
| **Beats** | CPython 3.10.7 |
| **Claimed result** | kostya/jit-benchmarks best times in s, Codon vs PyPy3: brainfuck 2.05 vs 8.77; brainfuck2 1.91 vs 11.03; binarytrees 1.0 vs 3.84; fasta 1.66 vs 3.19; knucleotide 2.69 vs 3.7 (1 run each); matmul 0.25 vs 0.36; nbody 2.23 vs 4.44; spectralnorm 0.53 vs 0.71. Slower on fannkuchredux 1.82 vs 0.71 and mandelbrot 0.65 vs 0.54; failed on pidigits, regexdna and revcomp. Same page, Codon vs CPython 3.10.7: binarytrees 1.0 vs 73.15, brainfuck2 1.91 vs 142.26, mandelbrot 0.65 vs 37.52, matmul 0.25 vs 22.73, nbody 2.23 vs 53.72, spectralnorm 0.53 vs 20.69, fannkuchredux 1.82 vs 4.04 (about 2x to 90x, derived from page data). README: typical speedups over vanilla Python on the order of 10-100x or more, on a single thread. |
| **Workload** | kostya/jit-benchmarks: single-threaded Benchmarks Game style programs run as the same Python source (CPython interpreter vs `codon build --release` native executable); time measured inside the program, so Codon compile time is excluded. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80 GB DDR4-3200 |
| **Compiler and flags** | Codon 0.15.5 installed by exaloop's install.sh in docker/codon, built with 'codon build --release' (kostya/jit-benchmarks tools/languages.rb); PyPy 7.3.11 official linux64 binary (python 3.9.16, gcc 10.2.1); CPython 3.10.7 from Ubuntu 22.10; C rows gcc 12.2.0. Times are measured inside each program (time() marks written to stderr), so Codon's 4-6 s compile time is reported separately. |
| **Adoption** | 16.9k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/exaloop/codon) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

On kostya/jit-benchmarks round 1 (AMD Ryzen 7 3800X, Docker on Ubuntu 22.10, best in-program time with compile time excluded), Codon 0.15.5 binaries built with `codon build --release` beat CPython 3.10.7 by about 2x to 90x (fannkuchredux 1.82 s vs 4.04 s, binarytrees 1.0 s vs 73.15 s). They beat PyPy 7.3.11 on 8 of 10 kernels (brainfuck 2.05 s vs 8.77 s, matmul 0.25 s vs 0.36 s), lost on fannkuchredux and mandelbrot, and failed pidigits, regexdna and revcomp. The suite's check step compares small-input output with expected text, and Codon is on no expected-failure list.

## Use it when

- CPU-bound pure-Python kernels (loops over ints and floats, small-object trees, string scanning, interpreters) that you can compile as a standalone program or extension: 2-90x over CPython 3.10.7 in the independent suite
- Code where PyPy is the current speedup: Codon beat PyPy 7.3.11 on 8 of 10 kernels that ran (brainfuck2 1.91 s vs 11.03 s, nbody 2.23 s vs 4.44 s, binarytrees 1.0 s vs 3.84 s)
- Batch or HPC jobs that can use @par multithreading or GPU kernels, which CPython's GIL rules out
- Hot functions inside a larger CPython codebase via @codon.jit or the extension build mode, when the function uses statically typeable Python

## Skip it when

- Programs that need arbitrary-precision ints, heterogeneous containers, runtime monkey patching or other dynamic features: int is 64-bit by default and these are rejected at compile time (pidigits, regexdna and revcomp failed to run in the independent suite)
- Workloads dominated by C-implemented libraries, I/O or the network; the FAQ says these see no substantial speedup
- Allocation-heavy code that creates many short-lived objects: issue #553 (open) reports a ray tracer twice as slow as PyPy with more than half the time in the Boehm GC's alloc_atomic
- fannkuchredux- and mandelbrot-style kernels, where PyPy was faster (0.71 s vs 1.82 s, 0.54 s vs 0.65 s)
- Short scripts where the 4-6 s compile time per program outweighs the run time, and Windows without WSL

## How it is fast

Whole-program static type inference turns Python code into monomorphic, unboxed code. Tuples compile to structs and library code is inlined with no object files, and the result is optimized by an LLVM 20-based fork. Codon adds its own IR passes for Python-level patterns (for example fusion in its native NumPy) and has no interpreter or VM at run time; memory is managed by the Boehm conservative garbage collector. Native threads without a GIL (@par over OpenMP) and GPU kernels give further speedups beyond the single-thread numbers.

## Compared with alternatives

Pick Codon over PyPy when the program fits the static subset and runs long enough to amortize the compile, since it led PyPy on 8 of 10 kernels and adds GIL-free threads; pick PyPy for unmodified dynamic Python, bigints or fannkuch-like code. Over Cython and mypyc, Codon needs no .pyx or C-API knowledge and was far faster on interpreter-style code (brainfuck 2.05 s vs Cython 165.97 s and mypyc 93.55 s), though Cython won binarytrees (0.81 s vs 1.0 s) and fannkuchredux (0.13 s vs 1.82 s) in the same suite.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (CLI producing native executables, shared libraries or Python extension modules) plus the codon-jit pip package |
| **Dependencies** | prebuilt install via exaloop's install.sh; building from source needs Codon's LLVM fork (based on LLVM 20, with openmp and compiler-rt) and libgfortran; Boehm GC is bundled; Python interop needs a CPython shared library set via CODON_PYTHON |
| **Minimum toolchain** | Codon CLI 0.20.x current (benchmarked 0.15.5); source build needs CMake, Clang and Python 3.8+ for the build step |
| **Platforms** | Linux and macOS natively (docs timings on an M1, independent suite on x86-64); Windows only through WSL |
| **Thread safety** | No GIL; @par loops run on OpenMP threads, and simple reductions such as `total += 1` become atomic automatically. Thread safety of built-in containers under concurrent mutation is not documented. |
| **Drop-in for the baseline** | partial — much Python source compiles unchanged, but it is not a CPython replacement: 64-bit ints, static typing, compile-time-sized tuples, C numeric semantics unless -numerics=py, and CPython modules only through the bridge |

## Gotchas

- The independent numbers come from Codon 0.15.5, which used ASCII strings and unordered dicts. Since v0.20, Unicode strings and insertion-ordered dicts are the defaults, and the docs say the old unordered dict (`-unordered-dict`) 'generally performs better', so the string- and dict-heavy rows (knucleotide, fasta, brainfuck) may not reproduce on current Codon defaults.
- Codon ran adapted test.codon.py sources; most changes are cosmetic (f-strings, typed class fields, a typed Dict), but CPython and PyPy ran matmul over array.array('d') rows, which box a new float on every read, while Codon used plain lists. That skews the CPython matmul ratio (22.73 s vs 0.25 s) somewhat in Codon's favour. Codon's nbody uses copy.copy instead of copy.deepcopy, so in-process repetitions 2-5 start from the mutated state of run 1. The operation count is unchanged and the correctness check runs only once, so timing is not materially affected.
- Integer overflow follows 64-bit machine semantics, and division by zero and math-domain checks follow C semantics unless -numerics=py is passed; results can differ silently from CPython on large integers.
- The best-time column excludes Codon's 4.3-6.4 s compile time, and several PyPy and knucleotide rows are single runs; `codon run` without -release is unoptimized (fib(40): 0.43 s vs 0.31 s with -release in the docs).

## Known shortcomings

- kostya/jit-benchmarks ran adapted, statically typed test.codon.py sources rather than the same test.py as the other implementations; Codon is an ahead-of-time compiler for a Python subset, slower than PyPy on fannkuchredux and mandelbrot, and failed pidigits, regexdna and revcomp. The version measured (0.15.5) was BSL-1.1; the repository is now Apache-2.0.
- Enricher: the benchmarked 0.15.5 used ASCII str and an unordered dict while v0.20 defaults to Unicode str and an ordered dict (docs say unordered 'generally performs better'), so knucleotide, fasta and brainfuck may not reproduce on current defaults; the CPython and PyPy matmul used array.array rows (float boxed on every read) against Codon lists, skewing the CPython ratio. Open issue #553: Boehm GC allocation makes object-heavy code 2x slower than PyPy.

## Caveats and trade-offs

Codon compiles a statically typed Python subset ahead of time with LLVM; it is not a drop-in Python runtime. The suite ran Codon on separate test.codon.py sources adapted for Codon (typed class fields such as Optional[TreeNode], a restructured binarytrees create function, copy.copy in place of copy.deepcopy in nbody), while PyPy and CPython ran test.py. Independent shootout is a 2023 snapshot with Codon 0.15.5; the Codon rows were added in the 2023-03-30 'Add codon' commit, after the round-1 date (2023-02-28) in the header. Codon failed to run pidigits, regexdna and revcomp and lost to PyPy on fannkuchredux and mandelbrot. Best-time column excludes the 4-6 s compile time; knucleotide and some PyPy rows are a single run. Benchmarks are simple single-thread kernels. exaloop.io benchmarks page and the Codon paper (CC 2023) were not opened (blocked). The repository is Apache-2.0 today (LICENSE checked); Codon 0.15.5, the version benchmarked, was released under BSL-1.1, so check the license of the version you use.

Ahead-of-time compiler for a Python subset, not a drop-in CPython replacement: static typing, fixed-width ints, different semantics for some features; imports CPython modules through a bridge; native multithreading (no GIL), OpenMP and GPU support; compiler is written in C++ on LLVM.

## Maintenance

Actively maintained by Exaloop (v0.20.3 on 2026-09-28, 16.9k stars, 95 open issues) and Apache-2.0 since v0.18; the benchmarked 0.15.5 was under BSL-1.1, so use a v0.18+ release for unrestricted use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded B to A: every Codon and PyPy3 number in the record matches the Codon and 'Python3 PYPY' rows of kostya/jit-benchmarks README.md, and the suite is fully reproducible. The benchmark code is public (&lt;bench&gt;/test.codon.py vs &lt;bench&gt;/test.py, build and run commands in tools/languages.rb: 'codon build --release'; docker/codon, docker/pypy3), versions are stated (Codon 0.15.5, PyPy 7.3.11 official binaries, CPython 3.10.7), and the CPU is stated (AMD Ryzen 7 3800X).
- **Verifier notes:** All record numbers verified row by row on the kostya/jit-benchmarks README; upgraded to A because code, versions, build flags (codon build --release) and CPU are public. Main shortcomings: Codon ran adapted typed sources rather than the same test.py, it is an AOT compiler for a Python subset, and it lost to PyPy on 2 of 10 kernels and failed 3 others.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/codon>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/pypy3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.codon.py>
  - <https://github.com/kostya/jit-benchmarks>
  - <https://github.com/kostya/jit-benchmarks/tree/master/binarytrees>
  - <https://github.com/kostya/jit-benchmarks/commits>
  - <https://github.com/exaloop/codon>
  - <https://github.com/exaloop/codon/commits>
  - <https://raw.githubusercontent.com/exaloop/codon/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/exaloop/codon>
  - <https://raw.githubusercontent.com/exaloop/codon/HEAD/README.md>
  - <https://raw.githubusercontent.com/exaloop/codon/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/exaloop/codon/HEAD/docs/start/install.md>
  - <https://raw.githubusercontent.com/exaloop/codon/develop/docs/language/overview.md>
  - <https://raw.githubusercontent.com/exaloop/codon/develop/docs/start/faq.md>
  - <https://raw.githubusercontent.com/exaloop/codon/develop/docs/start/changelog.md>
  - <https://raw.githubusercontent.com/exaloop/codon/develop/docs/developers/build.md>
  - <https://github.com/exaloop/codon/tree/develop/docs>
  - <https://github.com/exaloop/codon/tree/develop/docs/language>
  - <https://github.com/exaloop/codon/releases>
  - <https://github.com/exaloop/codon/releases/tag/v0.20.0>
  - <https://github.com/exaloop/codon/commits/develop>
  - <https://github.com/exaloop/codon/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/exaloop/codon/issues/553>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/dc>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/codon>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fannkuchredux/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/mandelbrot/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/spectralnorm/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.codon.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.codon.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/exaloop/codon`) · [data/wave12/enrich/raw/github_com_exaloop_codon.json](../../../data/wave12/enrich/raw/github_com_exaloop_codon.json) (enrichment confidence 0.8)

</details>
