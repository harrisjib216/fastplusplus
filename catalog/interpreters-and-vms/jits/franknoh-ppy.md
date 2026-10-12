# PPy (Pretty Python compiler with LLVM JIT and AOT backends)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🟢 active

> Ahead-of-time and JIT LLVM compiler for annotated Python; 1.27x faster than warm PyPy on one Collatz kernel.

| | |
|---|---|
| **Beats** | PyPy 3.11.15 (warm); also Numba 0.67, Codon 0.19.6, Cython 3.3, mypyc, Nuitka and CPython 3.14.5 |
| **Claimed result** | Collatz longest chain below 300000, kernel wall time, ten fresh processes: ppy run (Python integer semantics, overflow guards) 41.7 +/- 1.8 ms vs PyPy 3.11 52.8 +/- 0.5 ms (about 1.27x, derived from page data) and CPython 3.14 1068.8 +/- 5.5 ms; ppy build --unsafe 30.8 ms vs Numba 32.5 ms, clang -O3 32.8 ms, gcc -O3 41.9 ms, Codon 42.1 ms. ppy run excludes a one-time \~640 ms build. In the eight-kernel suite (examples/15_algorithms) Numba leads on six of the eight kernels by 10-30%. |
| **Workload** | Collatz longest-chain search below 300000, kernel wall time, ten fresh processes each. |
| **Metric** | throughput |
| **Hardware** | Not stated for the README Collatz table ('one machine'); examples/15_algorithms/measurements.json for the same 0.6.0 release records Intel Core Ultra 9 386H, 16 cores, WSL2 (probably the same machine, unconfirmed) |
| **Compiler and flags** | gcc 13.3 -O3, clang 22.1 -O3 for the C rows; PPy built with ppy build / ppy run (LLVM); PyPy 3.11.15 and Numba 0.67 warm |
| **Adoption** | 15 stars; PyPI package ppy-lang 0.6.0 |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/franknoh/PPy) · [benchmark](https://github.com/franknoh/PPy) |

## Verdict

The README Collatz kernel (longest chain below 300000), kernel wall time over ten fresh processes on an unnamed machine (the project's other measurements are on an Intel Core Ultra 9 386H under WSL2): `ppy run` 41.7 +/- 1.8 ms with Python integer semantics vs warm PyPy 3.11.15 at 52.8 +/- 0.5 ms (about 1.27x, derived from page data) and CPython 3.14.5 at 1068.8 ms; the reproducible eight-kernel suite has no PyPy column and shows Numba 0.67 faster than `ppy run` on Collatz (33.1 vs 41.6 ms).

## Use it when

- Integer- or array-heavy pure-Python kernels (loops over int, float and array.array/Buffer data) that you want native without leaving Python syntax: the project's eight kernels run 9x to 160x faster than plain CPython.
- You need exact Python integer results: `ppy run` keeps arbitrary-precision semantics via guards, whereas Numba, Cython `cdef long long` and Codon silently wrap at 64 bits.
- You want one source to yield a standalone native binary or C/C++17 source (for example to vendor generated C into a C++ build), with `python file.ppy` as the correctness oracle.
- Competitive-programming or batch tools on Linux where `ppy build --standalone --unsafe` matched or beat gcc/clang -O3 on 4 of 5 judge problems, largely through a faster integer reader than scanf.
- Programs run many times so the one-time build (about 0.3-0.9 s cold in run_overhead.json, about 640 ms for the Collatz example) amortises.

## Skip it when

- Arbitrary dynamic Python that you want accelerated as is: PyPy runs everything, while PPy compiles only what it can prove and leaves the rest on CPython speed (eval, star imports and failed imports stay in Python).
- Tight numeric kernels where the fastest option matters: in PPy's own suite Numba leads on six of eight kernels by 10-30%, and Numba beats `ppy run` on Collatz (33.1 vs 41.6 ms).
- One-shot short scripts: a cold `ppy run` costs 0.3-0.9 s of build per run_overhead.json, and even a warm cache adds a few milliseconds of start-up over plain CPython (basics example 40 ms vs 33 ms).
- Production code that needs a stable compiler: pre-1.0 alpha (Development Status 3), 15 PyPI releases between 2026-09-03 and 2026-10-03, minor releases may change the language, and recent releases fixed silent wrong-result bugs.
- Non-Linux or non-CPython hosts: CI runs on ubuntu-latest only, the package targets CPython 3.12-3.14, and Windows/macOS support is not documented.

## How it is fast

A whole-program static analysis (types, effects, value ranges) lowers proven functions to unboxed 64-bit machine code through LLVM, so loops like Collatz run as native integer arithmetic instead of interpreted bytecode. Python integer semantics are kept with overflow guards, and guard hoisting proves a loop's extreme cases once ahead of the loop so the body runs plain `mul nsw` that LLVM can strength-reduce and vectorise; `--unsafe` drops the overflow guards for C-like 64-bit wrap (bounds checks stay). Calls from Python go through a generated C wrapper (about 29 ns for two int arguments, against 30 ns for a CPython call, per the project's own table).

## Compared with alternatives

Pick PPy over Numba when you need exact Python-integer results, generated C/C++ or standalone binaries, or compilation of ordinary Python data structures (str, list, dict, classes) rather than NumPy-array kernels; pick Numba when raw kernel speed and maturity matter, since it leads six of eight kernels in PPy's own suite. Unlike Cinder or the CPython copy-and-patch JIT, PPy only speeds up annotated, provable code, but there it is native-speed rather than a 1.5x-class interpreter gain.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python package ppy-lang; llvmlite&gt;=0.44 through the [llvm] extra for native code (without it ppy run warns W2012 and runs on CPython); optional extras for NumPy, PyTorch, JAX, pydantic, SciPy, pandas, PyArrow; the recorded benchmark environment also lists a system cc used by PPy |
| **Minimum toolchain** | CPython 3.12+ (tested on 3.12, 3.13, 3.14) |
| **Platforms** | Linux x86-64 (CI on ubuntu-latest; measurements on WSL2); other platforms not documented |
| **Thread safety** | not documented for the compiler; the language exposes ppy.concurrent, ppy.atomic and ppy.parallel.range for native parallel code |
| **Drop-in for the baseline** | partial: the same .py-compatible source runs under CPython and under ppy run, but it replaces PyPy only for annotated, statically analysable functions; everything else runs on CPython, not on a JIT |

## Gotchas

- Harness gap behind the PyPy claim: no script in the repo produces the README Performance table; the README's collatz.ppy prints no timing line, and the in-repo harnesses (examples/compare.py, examples/bench_startup.py, examples/15_algorithms/compare) never run PyPy, Cython, mypyc or Nuitka, so the 52.8 ms PyPy row cannot be reproduced from the repo and its CPU is not named. Timing method: PPy's kernel is timed on its single first call per process (cached build excluded), while PyPy is labelled 'warm' and the Numba port makes one compile call first, so the asymmetry favours the baselines rather than PPy.
- The fastest rows (30.8 ms, 28.8 ms with --host-cpu) use `--unsafe`, which drops overflow guards for 64-bit wrap semantics, and `--host-cpu` artifacts are not portable; only the 41.7 ms `ppy run` row keeps the Python integer semantics PyPy has.
- A failed guard sends the call to the Python body ('A failed guard costs the wrapper plus a Python call', and printed output from a native call that falls back is dropped so nothing prints twice), which implies the whole call reruns on CPython: a value that overflows 64 bits late in a long kernel turns a 40 ms call into a CPython-speed one.
- Correctness churn: 0.6.0 (2026-10-03) fixed a global store dropped by the Python backend's optimizer with reads folded to the first value, and 0.5.0-era fixes include a stale `len(xs)` after pop/append taking the wrong native branch and `min`/`max` in emitted C reading unwritten memory; pin an exact version (the README itself says to) and keep `python file.ppy` as the oracle.

## Known shortcomings

- The 1.27x over PyPy is a single Collatz kernel with no PyPy script and no CPU named for that table; Numba leads 6 of 8 kernels by 10-30% in examples/15_algorithms (Intel Core Ultra 9 386H). Pre-1.0; Python.
- Enricher: no in-repo script produces the README's PyPy, Cython, mypyc or Nuitka rows (collatz.ppy prints no timing; compare.py, bench_startup.py and 15_algorithms never run PyPy); timing asymmetry favours PPy (timed on first call while PyPy is warm and Numba gets a compile call first), the fastest rows use --unsafe (64-bit wrap), failed guards rerun the call on CPython, and Numba beats ppy run on Collatz (33.1 vs 41.6 ms). Alpha: 15 PyPI releases between 2026-09-03 and 10-03; 0.6.0 fixed silent wrong results.

## Caveats and trade-offs

Single kernel against PyPy; the README table names no CPU and the repository has no script for the PyPy, Cython, mypyc or Nuitka rows, so those rows are not reproducible from the repo. The eight-kernel suite (examples/15_algorithms, code in compare/, Intel Core Ultra 9 386H, gcc 13.3 / clang 22.1 -O3) compares against C, Numba, Mojo and Codon, not PyPy, and there Numba leads six of eight kernels by 10-30%. PPy compiles an annotated, statically analyzable subset of Python while PyPy runs arbitrary Python. ppy run times exclude the \~640 ms first-run build. Pre-1.0 (0.6.0; minor releases may change the language), 15 stars.

Compiles only the statically analysable subset of Python (guards fall back to CPython); LLVM backend needs the llvm extra; first ppy run pays about 640 ms to build into the cache (not in the table); the --unsafe rows drop overflow guards and use 64-bit wrap semantics. Python tool, not callable from C++ except through its C or C++17 source emission.

## Maintenance

Very active but only a month old (0.1.0a1 on 2026-09-03, 0.6.0 on 2026-10-03, last commit 2026-10-03, 15 stars, single author) and MIT; treat it as an alpha compiler to pin and verify, not a vetted PyPy replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table compares one Collatz kernel against PyPy 3.11.15 (52.8 ms vs ppy run 41.7 ms) with tool versions and C flags, but names no CPU for that table and ships no PyPy, Cython, mypyc or Nuitka script; the reproducible suite (examples/15_algorithms, CPU named) covers C, Numba, Mojo and Codon, not PyPy. First-party, partial methodology: C.
- **Verifier notes:** Numbers match the README exactly; 1.27x over PyPy is one kernel with no PyPy script and no CPU named for that table, so C stands. Shortcomings: single-kernel PyPy comparison, PyPy row not reproducible from repo, Numba faster on 6 of 8 kernels in the project's own suite, pre-1.0.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/README.md>
  - <https://github.com/franknoh/PPy>
  - <https://github.com/franknoh/PPy/commits>
  - <https://github.com/franknoh/PPy/tree/main/scripts>
  - <https://github.com/franknoh/PPy/tree/main/examples>
  - <https://github.com/franknoh/PPy/tree/main/examples/15_algorithms/compare>
  - <https://github.com/franknoh/PPy/tree/main/docs>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/scripts/refresh.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/compare.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/README.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/measurements.json>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/CONTRIBUTING.md>
  - <https://pypi.org/pypi/ppy-lang/json>
- **Sources the enricher read:**
  - <https://github.com/franknoh/PPy>
  - <https://github.com/franknoh/PPy/tree/main/examples>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/README.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/docs/guide/native-lowering.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/scripts/refresh.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/compare.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/bench_startup.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/run_overhead.json>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/README.md>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/measurements.json>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/algorithms.ppy>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/algorithms.c>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/compare/algorithms_numba.py>
  - <https://raw.githubusercontent.com/franknoh/PPy/HEAD/examples/15_algorithms/bench.py>
  - <https://pypi.org/pypi/ppy-lang/json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/franknoh/ppy`) · [data/wave12/enrich/raw/github_com_franknoh_ppy.json](../../../data/wave12/enrich/raw/github_com_franknoh_ppy.json) (enrichment confidence 0.6)

</details>
