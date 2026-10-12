# Hana Jit (LLVM-backed Python JIT, hanajit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0` · 🟢 active

> Alpha llvmlite-based Python JIT: ties Numba on scalar loops, beats it on call overhead and fused NumPy expressions.

| | |
|---|---|
| **Beats** | Numba 0.66 (and NumPy 2.x) |
| **Claimed result** | README summary: 5-operation fused NumPy expression 3.0x vs NumPy and 3.7x vs Numba; fib(30) 1.7x vs Numba; call/dispatch about 46 ns, 3.6x less than Numba. Four-way table: plain Hana Jit about equal to Numba (fp reduction 0.78 vs 0.74 ms, poly5 1.04 vs 0.96 ms, dot 0.80 vs 0.74 ms); evolve() 0.23, 0.22 and 0.31 ms against Numba 0.74, 0.96 and 0.74 ms, but fourway.py runs evolve(allow_fastmath=True) against plain njit without fastmath. The repo's fairer files show smaller wins: benchmarks/RESULTS-FOURWAY.md has the GA tying Numba fastmath on fp reduction (0.7 vs 0.7 ms) and the fused expression at 14.4 ms vs Numba fastmath 30.7 ms (about 2.1x, derived from page data); RESULTS-EVOLVE.md (fastmath on for both where allowed) gives a 1.19x geomean over Numba across 15 kernels; RESULTS-MICRO.md (hanajit 0.5.1) gives a 1.12x geomean over Numba across 52 workloads, driven by the dispatch rows (4.31x), with control 0.96x, recursion 0.92x and pointer 0.97x. |
| **Workload** | Numeric kernels compiled through llvmlite: a 5-operation fused NumPy expression, float reductions, polynomial evaluation, dot product, fib(30) recursion and call/dispatch overhead, compared with NumPy and Numba. |
| **Metric** | throughput |
| **Hardware** | README: single core in a shared CI container; RESULTS.md and RESULTS-MICRO.md: x86_64, 1 core, Python 3.12.3; CPU model never stated |
| **Compiler and flags** | LLVM -O3 through llvmlite (version not stated); Numba 0.66 compared with default njit (fastmath off) in fourway.py and bench_v016.py, njit(fastmath=True) on starred rows of evolve_bench.py; NumPy 2.x |
| **Adoption** | 2 stars, 0 forks; PyPI package hanajit 0.24.0 (2026-08-19) |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/ezducate/HanaJit) · [benchmark](https://github.com/ezducate/HanaJit) |

## Verdict

First-party runs on a single core of an unnamed x86_64 shared CI container (Python 3.12.3, Numba 0.66.0, NumPy 2.x, llvmlite and LLVM versions not stated): scalar loops tie Numba, call dispatch costs about 50 ns vs about 220 ns for Numba, a fused 5-op NumPy expression runs 14.4 ms vs 49.6 ms (Numba default) or 30.7 ms (Numba fastmath), and the GA-tuned geomean over 15 kernels is 1.19x over Numba with fastmath allowed for both, a figure biased upward by the harness timing selection described in gotchas.

## Use it when

- Python code that calls a small numeric kernel hundreds of thousands of times from an interpreted loop, where Numba's dispatcher overhead dominates (RESULTS-MICRO dispatch rows: 3.6x-5.0x less than Numba)
- Multi-operation NumPy expressions over large float64 arrays inside a jitted function, where temporaries cost memory bandwidth (14.4 ms vs Numba 49.6 ms, or 30.7 ms with Numba fastmath, on a 2M-element 5-op expression)
- Memory-bound reductions where float32 or reduce_reassoc reordering is acceptable, or exact int8/int16 sums via the opt-in narrow mode
- Experiments that need the same Python kernel exported to a no-Python x86-64 executable, a wasm module or a driver-only GPU launch without a CUDA toolkit

## Skip it when

- As a general Numba replacement: on the 48 non-dispatch micro-workloads it averages 1.00x of Numba (derived from page data), and it loses on cross-function calls (0.14x), loop break/continue (0.81x) and max element (0.86x)
- Production code: alpha status, 2 stars, 23 commits, one author, APIs may change before 1.0
- Code needing Python semantics for big integers or index errors: integers are int64 (silent wrap where CPython would grow) and array indexing has no bounds check (negative indices are wrapped NumPy-style)
- Object-heavy code, strings, dicts, classes or array allocation inside kernels: these fall back to the interpreter at CPython speed
- Callers from C++: it is a Python package only

## How it is fast

Ordinary LLVM -O3 code generation, which is why scalar loops land within a few percent of Numba (both use LLVM). The wins over Numba come from three specific mechanisms: a loop-fusion engine that compiles a whole NumPy expression (ufuncs, np.where, np.clip, np.sum) into one pass with no temporary arrays; a native CPython 3.12+ vectorcall object per jitted function, so dispatch is roughly 50 ns per call instead of Numba's roughly 220 ns; and evolve(), a genetic search over LLVM pass settings (vectorize, SLP, unroll count, vector width, codegen level and, if allowed, fast-math IR) that keeps the fastest variant on the caller's data.

## Compared with alternatives

Against Numba (catalogued, same LLVM backend and far more mature) pick Hana Jit only when per-call dispatch or temporary-array traffic from NumPy expressions dominates, or when you want the Python-to-executable/wasm/GPU export paths; PPy targets Python-integer-correct loops against PyPy, and the CPython JIT or Cinder speed up whole programs without restricting the subset.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | llvmlite&gt;=0.42 (bundles LLVM); NumPy for array kernels; optional cuda-python, nvidia-cuda-nvcc-cu12 (libdevice), a host C compiler for executable export and clang for wasm linking |
| **Minimum toolchain** | Python 3.10 (classifiers to 3.14, CI 3.10-3.13); native vectorcall dispatch needs CPython 3.12+ |
| **Platforms** | Linux, Windows and macOS (CI includes Apple Silicon); standalone-executable export is x86-64 only; GPU launch via CUDA, Level Zero, Vulkan, Metal drivers (HIP untested on hardware) |
| **Thread safety** | nogil=True releases the GIL around compiled kernels and the docs call this always safe; thread safety of compilation and the dispatcher cache is not documented |
| **Drop-in for the baseline** | partial — @jit mirrors Numba's @njit for simple numeric functions, but the supported subset differs and unsupported code silently runs in CPython (one warning) instead of raising like njit |

## Gotchas

- Harness flaw in benchmarks/evolve_bench.py (source of the 1.19x 'GA vs numba' geomean): the hanajit+GA column is evolve()'s internal best_ms, the minimum of re-measured top-3 finalists chosen from up to about 60 candidate timings, while Numba gets one best-of-5 measured by the harness; the harness's own re-measurement of the installed kernel (t_hj_check) is computed and discarded, so near-1.0x rows carry a selection bias in Hana Jit's favour.
- evolve()'s 'every candidate is checked' gate compares only the function's return value on the example and 3 random probes; arrays written in place are not compared, so a kernel that fills an output array and returns 0 is effectively unchecked. With allow_fastmath=True the candidate IR uses full LLVM 'fast' flags (nnan, ninf, nsz, reassoc) and passes at 1e-9 relative tolerance on uniform(-10, 10) probes that never contain NaN or Inf.
- README four-way table (fourway.py) runs evolve(allow_fastmath=True) against plain njit without fastmath, and its own check allows a 1e-6 relative difference, so 'guaranteeing an identical result' does not hold; with njit(fastmath=True) the fp-reduction win disappears (RESULTS-FOURWAY.md 0.7 vs 0.7 ms).
- RESULTS-MICRO's 1.12x overall geomean over Numba comes from the 4 dispatch rows (4.31x); without them the 48 compute workloads geomean is 1.00x (derived from page data), and the 'sum of range' row is 0.00 ms vs 0.00 ms (ratio is timer noise); results were recorded with hanajit 0.5.1, docs/performance.md still lists cross-function calls as uncompiled although the README now advertises helper inlining, and the core modules are about 4,400 lines rather than the README's 3,000.

## Known shortcomings

- The README evolve() wins over Numba compare evolve(allow_fastmath=True) with plain njit (benchmarks/fourway.py); the repo's own RESULTS-FOURWAY.md has the GA tying Numba fastmath on the fp reduction (0.7 vs 0.7 ms) and the fused expression about 2.1x over Numba fastmath (derived), with geomeans of 1.19x (RESULTS-EVOLVE.md) and 1.12x over 52 workloads coming mostly from dispatch. No CPU model, results files from old versions, 2 stars. Off-baseline (Numba); Python.

## Caveats and trade-offs

The README's evolve() wins over Numba compare fast-math code with strict Numba: benchmarks/fourway.py calls evolve(allow_fastmath=True) but times plain njit, and evolve.py then accepts candidates within a 1e-9 relative tolerance, so the README's 'guaranteeing an identical result' does not hold for that table; against njit(fastmath=True) the fp-reduction gain disappears (RESULTS-FOURWAY.md 0.7 vs 0.7 ms). Plain scalar loops tie Numba (both LLVM); the broad 52-workload geomean is 1.12x, mostly from dispatch overhead, and a cross-function call row is 0.14x of Numba. RESULTS.md and RESULTS-MICRO.md were recorded with old versions (hanajit 0.8.0 and 0.5.1; current 0.24.0). No CPU model; the README itself says absolute times are noisy. The 10-100x over CPython claim is not a named-incumbent comparison. Numba is not in the jits baseline list (PyPy, LuaJIT, V8, HotSpot). 2 stars, alpha status.

Alpha Python package (about 3,000 lines) for numeric and array code; unsupported code falls back to the interpreter; also exports standalone x86-64 executables, WebAssembly and GPU kernels; Python-only, not callable from C++.

## Maintenance

Actively developed alpha (PyPI 0.24.0 on 2026-08-19, last commit 2026-08-19, 476-case test suite), Apache-2.0 and pip-installable with only llvmlite, but a 2-star single-author project whose benchmark files lag the code by many versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README tables against Numba 0.66 and NumPy 2.x with public scripts (benchmarks/fourway.py, bench_v016.py, evolve_bench.py, microbench.py), but no CPU model ('single core in a shared CI container'; RESULTS\*.md say only x86_64, 1 core, Python 3.12.3) and no llvmlite/LLVM version, so not A; no independent run, so C.
- **Verifier notes:** README numbers are on the page, but the four-way table pits evolve(allow_fastmath=True) against non-fastmath Numba; the repo's own fastmath-for-both files show the GA tying Numba on fp reduction and a 1.19x (15 kernels) or 1.12x (52 workloads, dispatch-driven) geomean. Tier stays C; claim corrected, so recorded as downgrade of the claim, not the tier. Shortcomings: fastmath-vs-strict comparison, no CPU model, stale results files, baseline off-list, 2 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/README.md>
  - <https://github.com/ezducate/HanaJit>
  - <https://github.com/ezducate/HanaJit/commits>
  - <https://github.com/ezducate/HanaJit/tree/main/hanajit>
  - <https://github.com/ezducate/HanaJit/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/fourway.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/bench_experimental.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/bench_reductions.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-MICRO.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-FOURWAY.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-NUMPY.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-EVOLVE.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/microbench.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/evolve_bench.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/bench_v016.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/numpy_scipy.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/evolve.py>
  - <https://pypi.org/pypi/hanajit/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/README.md>
  - <https://github.com/ezducate/HanaJit>
  - <https://github.com/ezducate/HanaJit/tree/main/hanajit>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/fourway.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-FOURWAY.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-EVOLVE.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS-MICRO.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/RESULTS.md>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/evolve_bench.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/microbench.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/benchmarks/bench_v016.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/evolve.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/__init__.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/codegen.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/decorator.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/typeinfer.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/autopar.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/cache.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/doctor.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/errors.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/inline.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/narrow.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/parallel.py>
  - <https://raw.githubusercontent.com/ezducate/HanaJit/HEAD/hanajit/rewrite.py>
  - <https://pypi.org/pypi/hanajit/json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ezducate/hanajit`) · [data/wave12/enrich/raw/github_com_ezducate_hanajit.json](../../../data/wave12/enrich/raw/github_com_ezducate_hanajit.json) (enrichment confidence 0.75)

</details>
