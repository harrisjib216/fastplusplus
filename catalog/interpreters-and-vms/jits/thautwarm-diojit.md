# DIO-JIT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `BSD-2-Clause` · 🔴 abandoned

> Experimental CPython 3.8/3.9 JIT that compiles type-specialised functions through Julia's LLVM backend; about 7x on fib(15).

| | |
|---|---|
| **Beats** | CPython 3.8 and 3.9 (PyPy is not compared) |
| **Claimed result** | fib(15): 11.63 vs 1.54 on Python 3.8 and 10.41 vs 1.51 on 3.9 (about 7x); trans 24.22 vs 7.79; append3 23.94 vs 10.70; BF 265.74 vs 134.23; selection sort 46.95 vs 33.88; DNA READ shows little gain (16.96 vs 14.82). The README also claims 500x on a partial-evaluation fib example. |
| **Workload** | Seven small Python programs (brainfuck interpreter, append3, DNA read, fib(15), hypot on strings, selection sort, trans), pure CPython versus the same code under the DIO-JIT decorator; each script in benchmarks/ times a fixed number of calls with timeit (fib.py 100,000 calls of f(15), trans.py 111,111,111 calls), so the README figures are presumably total seconds, though the table states no units. |
| **Metric** | throughput |
| **Adoption** | 116 stars |
| **Last commit** | 2021-02-18 |
| **Links** | [repository](https://github.com/thautwarm/diojit) · [benchmark](https://github.com/thautwarm/diojit) |

## Verdict

The author's README table compares the same seven microbenchmarks in pure CPython 3.8 and 3.9 against DIO-JIT-compiled versions, timed with timeit in the benchmarks/ scripts: fib(15) 11.63 s vs 1.54 s on 3.8 (7.6x, derived from page data) and trans 24.22 s vs 7.79 s (3.1x), with smaller gains elsewhere and almost none on bytes-heavy DNA READ. Hardware, CPython build and run count are not stated, and PyPy is not compared.

## Use it when

- Research or teaching on extensible JITs: specialisation rules are plain Python functions registered per type and attribute, which makes it a compact example of abstract-interpretation-driven specialisation.
- Hot recursive or straight-line integer and list code on CPython 3.8 or 3.9 that avoids for loops, try/except and closures (fib(15) about 7x, a 7-addition function about 3x, three list.append calls about 2x per the README).
- Domain-specific cases where you can write your own rules, including constant folding on known literal arguments.

## Skip it when

- Python 3.10 or newer: the translator handles 3.8-era opcodes (BINARY_ADD, CALL_FUNCTION, CALL_METHOD, LOAD_METHOD), which CPython 3.11 replaced, and the README and PyPI badge claim only 3.8 and 3.9, both end-of-life.
- Production code: the README says it is not production-ready and that many specialisation rules are missing; even `a - 1` has no rule (the examples write `a + -1`).
- Code with loops, exceptions, closures or variadic arguments, which the JIT cannot compile; bytes and bytearray-heavy code gains almost nothing (DNA READ 16.96 vs 14.82).
- Environments where installing Julia (1.6 recommended), DIO.jl and pyjulia next to Python is not acceptable, or where Julia's own startup and compile latency matter.
- Numeric array code: Numba or PyPy are the maintained options and are not compared here.

## How it is fast

It translates CPython stack bytecode into a register IR (diojit/stack2reg), runs abstract interpretation over it to infer types and pick specialisation rules (diojit/absint), and emits Julia source (diojit/codegen/julia.py) with explicit Py_INCREF/Py_DECREF that Julia compiles to native code through LLVM in the same process via pyjulia. The speedup comes from removing bytecode dispatch, binding declared-fixed globals (such as the recursive `fib`) at compile time instead of looking them up in a dict, and calling type-specific CPython slots directly (int add is the int type's nb_add, comparisons use int's tp_richcompare), so Python semantics such as arbitrary-precision ints are kept. Optional user rules can constant-fold calls on literal arguments (partial evaluation).

## Compared with alternatives

Pick DIO-JIT only to study or extend a rule-based specialising JIT on CPython 3.8/3.9; for real workloads Numba (maintained, numeric code) or the built-in CPython copy-and-patch JIT (3.13+) are better choices, and Cinder or S6 are the comparable research JITs with larger published evaluations.

## Integration

| | |
|---|---|
| **Form** | module (pip package diojit; last PyPI release 0.2a0, 2021-02-09) plus the Julia package DIO.jl |
| **Dependencies** | Julia (README suggests 1.6) with DIO.jl installed from GitHub, the pyjulia `julia` Python package, pyrsistent |
| **Minimum toolchain** | CPython 3.8 (relies on LOAD_METHOD); 3.8 and 3.9 only in practice |
| **Platforms** | any platform with CPython 3.8/3.9 and Julia (README gives install routes for Windows, macOS and Linux); not documented further |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: decorate the function and call the object returned by spec_call; only a restricted subset of Python compiles, and the rest falls back to CPython C-API calls |

## Gotchas

- The README's 500x example (benchmarks/const_fib.py) specialises try_const_fib on the literal value 20 (jit.ofval(20)) with user rules that constant-fold additions and comparisons, so the timed call returns a precomputed constant; it is not a JIT speedup on real input.
- Benchmarks are not quite like-for-like in source: the pure-Python fib uses `a - 1` and an ordinary global lookup, while the JIT version uses `a + -1` with `fixed_references=['fib_fix']`; the +/-1 rewrite costs CPython nothing, but the fixed global is one of the advantages being measured.
- The README table is total seconds for the iteration counts in the current scripts (fib: 100,000 calls of f(15), each making 1,219 calls, gives about 95 ns per Python call; trans: 111,111,111 calls gives about 218 ns), while the docstrings inside the scripts (fib 1.33 s vs 0.18 s, trans 2.68 s vs 0.85 s) must come from runs with 10x fewer iterations; the ratios agree (about 7.5x and 3.1x, derived from page data). No hardware or CPython build is given.
- Fixed global references and spliced constants are embedded by object address (id()) in the generated Julia code, so rebinding a fixed global after compilation is not seen by the compiled function; @eagerjit assumes every global is fixed.

## Known shortcomings

- No PyPy comparison, no hardware or units; the 500x example times a constant-folded literal (jit.ofval(20)); needs Julia at runtime; abandoned since 2021-02-18. LICENSE is BSD-2-Clause while setup.py says MIT.
- Enricher: the translator handles 3.8-era opcodes only (BINARY_ADD, CALL_FUNCTION, CALL_METHOD), so it supports Python 3.8 and 3.9 only, both end of life; the README table is total seconds for the current script counts while the docstrings come from runs with 10x fewer iterations (ratios agree at 7.5x and 3.1x, derived); fixed globals are embedded by id().

## Caveats and trade-offs

No hardware, no units, no CPython build details, and no comparison with PyPy, which is the strong baseline for Python JIT speed. Only microbenchmarks. The docstring timings inside the scripts (fib 1.33 s vs 0.18 s, trans 2.68 s vs 0.85 s) differ from the README table, so the table came from a separate unrecorded run. In fib.py the pure-Python baseline uses a - 1 while the JIT version uses a + -1 because no rule for subtraction exists. The README's 500x partial-evaluation example (benchmarks/const_fib.py) specialises the function on the literal value 20 (jit.ofval(20)), so the JIT side returns a constant-folded result; it is not a general speedup. Requires Julia plus the DIO.jl package at runtime; no for loops, exception handling or closures inside JIT functions; README says not production-ready. LICENSE is BSD-2-Clause but setup.py declares 'mit'. Last commit 2021-02-18.

A JIT that runs inside CPython (3.8 and later, relies on LOAD_METHOD) and optimizes by type specialisation rules; users add @jit.jit decorators. The README says it is not production ready and many specialisation rules are still missing. Programs using bytearray and bytes see no gain.

## Maintenance

Abandoned since February 2021 (last PyPI release 0.2a0) and tied to end-of-life CPython 3.8/3.9 plus a Julia runtime; the code is BSD-2-Clause per LICENSE (setup.py and PyPI say 'mit') and readable as a research prototype, but not something to deploy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table of pure CPython 3.8/3.9 vs DIO-JIT with public timeit scripts in benchmarks/, but no hardware, units, CPython build or run count; C.
- **Verifier notes:** README numbers match the record. Tier C stands. Shortcomings: no PyPy comparison, no hardware or units, 500x claim is constant folding on a literal argument, Julia runtime dependency, abandoned since 2021-02-18, license metadata mismatch (LICENSE BSD-2-Clause vs setup.py 'mit').
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thautwarm/diojit>
  - <https://github.com/thautwarm/diojit/commits/master>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/README.md>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/fib.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/trans.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/const_fib.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/LICENSE>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/setup.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/README.md>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/setup.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/LICENSE>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/fib.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/trans.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/benchmarks/const_fib.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/diojit/absint/prescr.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/diojit/stack2reg/translate.py>
  - <https://raw.githubusercontent.com/thautwarm/diojit/master/diojit/codegen/julia.py>
  - <https://github.com/thautwarm/diojit/tree/master/diojit>
  - <https://github.com/thautwarm/diojit/tree/master/diojit/codegen>
  - <https://github.com/thautwarm/diojit/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/diojit/json>
  - <https://github.com/thautwarm/DIO.jl/tree/master/src>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/dynamic.jl>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/symbols.jl>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/DIO.jl>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/static.jl>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/support.jl>
  - <https://raw.githubusercontent.com/thautwarm/DIO.jl/master/src/python.jl>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/thautwarm/diojit`) · [data/wave12/enrich/raw/github_com_thautwarm_diojit.json](../../../data/wave12/enrich/raw/github_com_thautwarm_diojit.json) (enrichment confidence 0.75)

</details>
