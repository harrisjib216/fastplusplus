# mypyc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🟢 active

> mypyc: compiles type-annotated Python modules to CPython C extensions; about 1.5x geomean on unannotated code, 2.4-22x on tuned code.

| | |
|---|---|
| **Beats** | CPython 3.10.7 |
| **Claimed result** | kostya/jit-benchmarks valid rows: about 1.49x geomean over CPython 3.10.7, from 0.91x (matmul) to 3.15x (binarytrees) (derived from page data); the nbody, knucleotide and revcomp mypyc rows are failed runs shown as 0.0 s and must be ignored. First-party mypyc-benchmark-results (i5-1145G7, CPython 3.13.1): 2.41x-22.36x on 8 mypyc-tuned benchmarks (richards 22.36x, hexiom 10.42x, deltablue 7.86x) where the compiled bm_\*_mypyc.py sources differ from the interpreted bm_\*.py. mypyc/doc/introduction.rst prose: 1.5-5x typical, 5-10x tuned, mypy itself 4x. |
| **Workload** | kostya/jit-benchmarks: the same unannotated Python benchmark source run on CPython and after `mypyc test.py` (compiled to a C extension). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80 GB DDR4-3200 |
| **Compiler and flags** | mypyc 1.0.1, `mypyc test.py` (tools/languages.rb), CPython 3.10.7 in Docker on Ubuntu 22.10. |
| **Adoption** | 20.7k stars (python/mypy; mypyc lives in the mypyc/ directory) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/python/mypy) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

First-party tracking (mypyc-benchmarks runbench.py, interpreted vs compiled in separate subprocesses, slowest third of runs dropped) on CPython 3.13.1, Ubuntu 24.04.1 and an Intel Core i5-1145G7 (C compiler and flags not stated) reports 2.41x (nqueens) to 22.36x (richards, tuned vec variant) at mypy commit 1ca7337. The independent kostya/jit-benchmarks round (mypyc 1.0.1 against CPython 3.10.7 on a Ryzen 7 3800X in Docker, unannotated code) gives about 1.5x geomean with a 0.91x-3.15x range (derived from page data).

## Use it when

- Pure-Python, CPU-bound application code that already has (or can be given) precise type annotations: object-heavy logic with method calls and attribute access, integer and float loops, list indexing
- Whole-program compilation of a typed codebase shipped as wheels, the way mypy ships itself (the docs credit this for a 4x speedup), when you want a speedup without leaving CPython or its C-extension ecosystem
- Replacing a hand-written C extension, or code you would otherwise move to Cython, with plain annotated Python that still runs interpreted for development
- Short-lived CLI tools, where a JIT's warm-up would eat the gain; mypyc is AOT, so startup is not penalised

## Skip it when

- Unannotated code expecting a big win: in kostya/jit-benchmarks (mypyc 1.0.1, CPython 3.10.7) the gain was about 1.5x geomean over 10 programs (binarytrees 3.15x, brainfuck2 1.84x, mandelbrot 1.61x, but matmul 0.91x, pidigits and regexdna 1.00x), and knucleotide, revcomp and nbody produced no valid result (derived from page data)
- Code dominated by exceptions, dataclass/attrs creation or hashing, or interpreted callers touching compiled objects: first-party microbenchmarks show catch_exceptions 0.48x, access_attr_from_interpreted 0.41x, dataclass_as_dict_key 0.74x, create_dataclass 0.90x
- Code that relies on monkey patching or mocks of compiled functions, nested or conditional class/function definitions, arbitrary descriptors, __getattribute__/__delattr__/__index__ on native classes, generator expressions with lazy semantics, or `if __name__ == '__main__'`
- Workflows that need pdb breakpoints, cProfile/trace hooks or inspect on hot code, since compiled functions trigger none of them
- Deep recursion: compiled code does not check for stack overflow and can crash the process; the docs still call mypyc alpha software

## How it is fast

It compiles ahead of time to C through mypy's type information. Calls, names and attributes inside one compilation unit are bound early, with no namespace dict lookups. Classes become C extension 'native classes' with vtable method dispatch and slot-like attribute storage. Small ints, bools, floats and fixed-length tuples are unboxed, and many list, dict, str and int operations use type-specialised primitives. The optional librt package adds a growable typed array (librt.vecs.vec) and other primitives that only help compiled code. Generated C is built with -O3 by default (mypyc/build.py opt_level).

## Compared with alternatives

Pick mypyc when your code is already type-annotated and must stay standard Python on CPython. Cython reaches C speed more easily on numeric loops (it won most kostya programs on unannotated code) but needs cdef/cpdef or its own build model for top speed. Codon and Shed Skin are faster but compile a restricted Python to native binaries outside CPython, and PyPy is a separate runtime. Over Nuitka, mypyc gives larger gains on annotated object code (binarytrees 23.25 s vs 72.55 s in kostya).

## Integration

| | |
|---|---|
| **Form** | module (Python-to-C compiler; output is a C extension .so/.pyd per compilation unit) |
| **Dependencies** | mypy[mypyc] (setuptools) and a C compiler with CPython headers at build time (GCC/Clang on Linux, Xcode CLT on macOS, MSVC Build Tools on Windows); at run time mypy_extensions types are erased, and librt is needed only if the code imports librt |
| **Minimum toolchain** | CPython 3.10+ (mypy 2.4.0 requires-python &gt;=3.10); code must pass mypy type checking |
| **Platforms** | anywhere CPython builds C extensions: Linux x86-64/aarch64, macOS, Windows (mypy's own compiled wheels exist for these plus musllinux x86-64 and win_arm64); not PyPy |
| **Thread safety** | Supports free-threaded CPython; since mypyc 2.3 most operations are memory-safe under races, but primitives may have different atomicity from CPython and librt vec is not race-safe |
| **Drop-in for the baseline** | partial — same CPython interpreter and libraries, but you must annotate code for a large win, rebuild per Python minor version (not abi3), and accept semantic differences (early binding, runtime type checks, unboxed ints lose bool identity) |

## Gotchas

- Harness flaw in the catalogued kostya/jit-benchmarks numbers: the nbody table lists 'Python3 MYPYC 0.0 s, 1 run, MaxMem -' as the fastest entry, above C and Cython. That is a failed run recorded as a time, not a result. knucleotide and revcomp also show '-' (no successful run). Only 10 of 13 programs have usable mypyc numbers.
- Methodology note on the headline 22.36x richards, 10.42x hexiom and 7.86x deltablue: runbench.py times a different source for the compiled side. bm_\*_mypyc.py (compiled_variant=True) swaps lists for librt vec[i64] and globals for Final instance attributes, while the interpreted baseline runs bm_\*.py. Even the baselines carry mypyc-specific i64 annotations. These numbers show what tuned code reaches, not what an existing annotated program gets.
- Calls between separately compiled units, or from interpreted code, fall back to the boxed Python calling convention and late binding, so compile hot paths as one unit. Caching bound methods in locals, a classic CPython trick, slows compiled code.
- Open segfault reports in the mypyc tracker: #1186 (subclassing collections.defaultdict), #1198 (module-level __getattr__), #1209 (dataclass field annotation using a TYPE_CHECKING-only compiled class) and #1203 (native attribute access on free-threaded builds). `# type: ignore` in compiled code can produce bad code.

## Known shortcomings

- mypyc intro gives prose ranges only (1.5-5x, 5-10x tuned); the first-party mypyc-benchmark-results page (i5-1145G7, CPython 3.13.1) shows 2.41x-22.36x on 8 mypyc-tuned benchmarks with compiler and flags unstated. Alpha quality; ahead-of-time compiler for typed Python, not an interpreter.
- Enricher: the kostya/jit-benchmarks nbody table lists 'MYPYC 0.0 s, 1 run' ranked fastest above C, a failed run shown as a time, and knucleotide and revcomp also have no valid run; the valid rows give about 1.49x geomean (0.91x matmul to 3.15x binarytrees, derived). The first-party 22.36x richards, 10.42x hexiom and 7.86x deltablue time different compiled sources (bm_\*_mypyc.py with librt vec) against interpreted bm_\*.py, and microbenchmarks show slowdowns (catch_exceptions 0.48x, access_attr_from_interpreted 0.41x).

## Caveats and trade-offs

The intro page gives prose ranges only, and the 4x for mypy is the project's own figure with no harness on that page. The tracking suite (mypyc/mypyc-benchmarks, runbench.py) is first-party, covers only 8 benchmarks written for mypyc (e.g. bm_richards_mypyc.py), so its 2.4x-22x reflects tuned code rather than typical annotated code, and it does not state the C compiler or flags. mypyc is a subdirectory of the mypy repository, not a standalone repo, and the docs call it alpha software ('only recommended for production use cases with careful testing'); generated code must be rebuilt per Python release (not abi3). Licence is MIT, with mypyc/lib-rt/pythonsupport.h, getargs.c and getargsfast.c under PSF-2.0 and lib-rt/base64 under a BSD-2-Clause-style licence (all OSI).

Ahead-of-time compiles type-annotated Python modules to C extensions that run on top of CPython (all third-party libraries keep working); some Python dynamism is not supported (see mypyc differences_from_python docs); needs a C compiler at build time.

## Maintenance

Very active (mypy 2.4.0 released 2026-10-01, commits daily) and MIT-licensed with PSF/BSD portions in lib-rt, but the docs still label mypyc alpha and recommend careful testing before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now C.
- **Tier reason:** The intro doc gives only prose ranges against interpreted CPython; the project's own tracking suite (mypyc/mypyc-benchmarks code, results in mypyc/mypyc-benchmark-results reports/summary-main.md) states CPython 3.13.1, Ubuntu 24.04.1 and an Intel Core i5-1145G7 but not the C compiler or flags, so it is first-party with partial methodology: C, not A.
- **Verifier notes:** Numbers on the intro page match the record; tier C stays. Added the stronger first-party results page (CPU stated, compiler/flags not) to claimed_speedup and caveats; consider it as an alternative benchmark_url. Metadata checked: MIT (PSF-2.0 and BSD portions in lib-rt), 20.7k stars, last commit 2026-10-06, active.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/python/mypy>
  - <https://github.com/python/mypy/commits>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/introduction.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/LICENSE>
  - <https://github.com/mypyc/mypyc-benchmarks>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/runbench.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/summary-main.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/benchmarks/richards.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/README.md>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/introduction.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/differences_from_python.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/performance_tips_and_tricks.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/getting_started.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/using_type_annotations.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/native_classes.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/compilation_units.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/librt.rst>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/doc/dev-intro.md>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/mypyc/build.py>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/setup.py>
  - <https://raw.githubusercontent.com/python/mypy/HEAD/pyproject.toml>
  - <https://pypi.org/pypi/mypy/json>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/knucleotide/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/revcomp/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/runbench.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarking.py>
  - <https://github.com/mypyc/mypyc-benchmarks/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_richards.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_richards_mypyc.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_hexiom.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_hexiom_mypyc.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_deltablue.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_deltablue_mypyc.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmarks/HEAD/benchmarks/bm_spectral_norm.py>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/summary-main.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/summary-microbenchmarks.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/benchmarks/richards.md>
  - <https://raw.githubusercontent.com/mypyc/mypyc-benchmark-results/HEAD/reports/benchmarks/hexiom.md>
  - <https://github.com/mypyc/mypyc/issues?q=is%3Aissue%20state%3Aopen%20segfault>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/python/mypy`) · [data/wave12/enrich/raw/github_com_python_mypy.json](../../../data/wave12/enrich/raw/github_com_python_mypy.json) (enrichment confidence 0.8)

</details>
