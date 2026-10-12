# Umka

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Statically typed, Go-like embeddable scripting language in C99; one old chart shows it beating Wren and CPython on matrix multiplication.

| | |
|---|---|
| **Beats** | Wren and Python (no Lua row) |
| **Claimed result** | README bar chart (image resources/perf.png): Umka about 26 s, Wren about 35 s, Python about 51 s for 400 x 400 matrix multiplication (values read off the image, approximate; about 1.35x faster than Wren and 1.96x faster than Python, derived from page data). A later contributor run recorded in the header of benchmarks/matrices.ml (Kakadu, PR #122, Dec 2021, Intel Core i5-4570) shows the opposite ordering against Wren: OCaml 2.39 s, Wren 6.26 s, Umka 7.19 s, Python 11.77 s (Umka about 1.15x slower than Wren and 1.64x faster than Python, derived from page data). |
| **Workload** | 400 x 400 matrix multiplication, computation time in seconds, Umka vs Wren vs Python. |
| **Metric** | throughput |
| **Hardware** | AMD A4-3300M @ 1.9 GHz, Windows 7 (README caption) |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/vtereshkov/umka-lang) · [benchmark](https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/README.md) |

## Verdict

The README shows one undated bar chart for 400x400 double matrix multiplication on an AMD A4-3300M under Windows 7 (interpreter versions, compiler and flags not stated): Umka about 26 s, Wren about 35 s, CPython about 51 s (bars read off the image). The repo's own Dec 2021 run on an i5-4570 puts Wren (6.26 s) ahead of Umka (7.19 s), with CPython at 11.77 s, and no comparison with Lua, Duktape or QuickJS is published.

## Use it when

- Adding a scripting layer to a C or C++ game, simulator or tool where you want script type errors caught at compile time rather than at run time (tophat, SaveScum and several simulators in the README use it this way).
- Passing arrays and structs between host and script without marshalling, since Umka's arrays and structures are C-compatible.
- Script-side cooperative multitasking (entity logic, coroutines) through fibers, with a small BSD-2-Clause C99 code base you can vendor.
- Numeric loops over fixed-size typed arrays, where static typing avoids the boxing that hurts CPython and Wren on the same code.

## Skip it when

- When interpreter speed against the Lua family is the deciding factor: open issue #163 (2022, labelled 'Umka 2') measures Umka about 2-3x slower than PUC Lua (fib(40) 20 s vs 10 s, an arithmetic loop about 3x), and there is no JIT; Luau, LuaJIT or Daslang are faster choices.
- When you need a published, reproducible speed claim: the only chart is one 400x400 matrix-multiply run on an AMD A4-3300M under Windows 7 with no versions or flags, and the repo's own later run has Wren ahead of Umka.
- Scripts written by users who expect dynamic typing and quick throwaway code: every variable has a static type, closures must list captured variables, and method receivers must be pointers.
- Data structures with reference cycles unless you design with weak pointers: the README says garbage collection is reference counting, so cycles need `weak` pointers.
- Multithreaded script execution: the API docs describe a per-instance handle and say nothing about thread safety; fibers are cooperative, not parallel.

## How it is fast

Static typing lets the compiler emit typed bytecode for a stack VM: OP_BINARY carries the operand type and operator, so the VM never boxes values or checks dynamic types, and fixed-size arrays of `real` are contiguous doubles rather than lists of boxed objects. The code generator runs a small peephole pass (merging PUSH_ZERO and POP runs, dropping PUSH_REG/POP_REG pairs, fusing PUSH_LOCAL_PTR with ZERO). The interpreter itself is plain: a switch-dispatched loop with a stack-overflow check on every instruction and a run-time switch on type kind and operator inside OP_BINARY, no JIT and no computed goto; memory is managed by reference counting.

## Compared with alternatives

Pick Umka over the Lua-family siblings (Luau, LuaJIT Remake) when compile-time type checking, Go-like syntax and C-compatible data layout matter more than speed, since its own issue tracker shows it slower than PUC Lua; if you want static typing and interpreter speed together, Daslang beats Lua and QuickJS in its published tables.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (also source-drop: 13 C99 files plus a CLI front end) |
| **Dependencies** | none beyond libc; libm and libdl on Linux |
| **Minimum toolchain** | C99 compiler; build_linux.sh uses gcc -O3 -malign-double -fno-strict-aliasing; Makefile for Linux, macOS (Darwin) and MinGW64 |
| **Platforms** | Windows, Linux and macOS builds in the repo (release binaries for Windows and Linux, Homebrew formula); Android support added in 1.5.7; a browser playground exists |
| **Thread safety** | not documented; all state lives in the Umka instance handle, so the safe assumption is one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark compares unlike programs: matrices.um uses fixed-size typed arrays (`var a, b, c: [size][size] real`), while matrices.py and matrices.wren use lists of lists of boxed values (the Python a and b even hold ints), so the chart measures static typing plus C-layout arrays rather than VM quality.
- Timed regions differ and are undocumented for Umka: the Python and Wren files time only the multiply loop, the current matrices.um has no timer (allbench.um times the whole test, including fill and check), and the Dec 2021 run in the matrices.ml header printed an 'elapsed' line from an earlier version of the file.
- The repo's own later run (matrices.ml header, Intel Core i5-4570) contradicts the chart's ordering against Wren: OCaml 2.39 s, Wren 6.26 s, Umka 7.19 s, Python 11.77 s, so only the win over CPython (about 1.6x, derived from page data) is reproduced in-repo.
- The language still changes between minor releases (1.5.5 deprecated typeptr, 1.5.6 turned `str` into a predeclared identifier and reworked the bytecode compiler and VM), so pin a release when embedding.

## Known shortcomings

- README chart (resources/perf.png, 400x400 matmul on an AMD A4-3300M) has no compiler, flags or interpreter versions, and the repo's own later run in the benchmarks/matrices.ml header (PR #122, December 2021, i5-4570) has Wren at 6.26 s beating Umka at 7.19 s, contradicting the claim. Timing is asymmetric (Python and Wren time the multiply loop only; the Umka file has no timer). Off-baseline: no Lua, Duktape or QuickJS comparison.
- Enricher: the matmul benchmark uses typed fixed [400][400] real arrays in Umka against boxed lists in Python (holding ints) and Wren, and the timed regions differ; open issue #163 reports Umka 2-3x slower than PUC Lua.

## Caveats and trade-offs

First-party single benchmark shown only as an image; the numbers are approximate readings of the bars. Benchmark code is public in benchmarks/ (matrices.um, matrices.py, matrices.wren, matrices.ml), but no compiler, flags, Umka/Wren/Python versions or run count are stated, and the chart is old (Windows 7, AMD A4-3300M; image last moved in April 2022). Timing is not symmetric: matrices.py and matrices.wren time only the multiply loop, while matrices.um has no internal timer (allbench.um times the whole test including fill and check). The repo's own later run in the benchmarks/matrices.ml header (i5-4570) has Wren 6.26 s beating Umka 7.19 s, so the README's win over Wren is not reproduced in the repo's own data. Baselines are Wren and Python, not Lua, Duktape or QuickJS; the only Lua file (benchmarks/trees_nostruct.lua) has no published result, so it does not show a win over the category incumbents; kept as a flagged entry.

Statically typed, Go-like embeddable scripting language with fibers and reference-counted GC; distributed as a static or dynamic library with a simple C API; C99 source.

## Maintenance

Actively developed by its author (commits through 2026-10-06, release 1.5.7 adding Android support and faster composite literals, 2.1k stars) and BSD-2-Clause, so it is safe to vendor; usable in production for its niche, but the performance case for it is weak and 'faster than Lua' is not claimed or shown.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (resources/perf.png) shows Umka about 26 s, Wren about 35 s, Python about 51 s for 400 x 400 matrix multiplication on an AMD A4-3300M; the benchmark sources are public (benchmarks/matrices.um, matrices.py, matrices.wren) but no compiler, flags or interpreter versions are stated, so it falls short of A and stays C.
- **Verifier notes:** Chart numbers match the record, but the repo's own later contributor run (benchmarks/matrices.ml header, i5-4570) shows Umka 7.19 s slower than Wren 6.26 s and only faster than Python 11.77 s, so the 'faster than Wren' claim is contradicted in-repo; no comparison against Lua, Duktape or QuickJS exists. Metadata checked on github.com: BSD-2-Clause, 2.1k stars, not archived, last commit 2026-10-06 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/README.md>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/resources/perf.png>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/LICENSE>
  - <https://github.com/vtereshkov/umka-lang>
  - <https://github.com/vtereshkov/umka-lang/tree/master/benchmarks>
  - <https://github.com/vtereshkov/umka-lang/commits>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.um>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.py>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.wren>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.ml>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/allbench.um>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/expected.log>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/trees_nostruct.lua>
  - <https://github.com/vtereshkov/umka-lang/commits/master/benchmarks/matrices.ml>
  - <https://github.com/vtereshkov/umka-lang/commits/master/resources/perf.png>
- **Sources the enricher read:**
  - <https://github.com/vtereshkov/umka-lang>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/README.md>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/resources/perf.png>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/build_linux.sh>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.um>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.py>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.wren>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/matrices.ml>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/allbench.um>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/benchmarks/expected.log>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/src/umka_vm.c>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/src/umka_vm.h>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/src/umka_gen.c>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/src/umka_api.h>
  - <https://raw.githubusercontent.com/vtereshkov/umka-lang/HEAD/doc/api.md>
  - <https://github.com/vtereshkov/umka-lang/releases>
  - <https://github.com/vtereshkov/umka-lang/issues?q=is%3Aissue+performance>
  - <https://github.com/vtereshkov/umka-lang/issues/163>
  - <https://github.com/vtereshkov/umka-lang/issues/3>
  - <https://github.com/vtereshkov/umka-lang/commits/master/benchmarks/matrices.um>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vtereshkov/umka-lang`) · [data/wave12/enrich/raw/github_com_vtereshkov_umka_lang.json](../../../data/wave12/enrich/raw/github_com_vtereshkov_umka_lang.json) (enrichment confidence 0.7)

</details>
