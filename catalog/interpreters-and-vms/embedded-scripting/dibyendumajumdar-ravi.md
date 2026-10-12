# Ravi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Lua 5.3 dialect with optional static types and a MIR-based JIT; typed numeric loops ran 10-26x faster than Lua 5.3.2 (old LLVM backend).

| | |
|---|---|
| **Beats** | Lua 5.3 (the dialect it extends; LuaJIT is named as a different-goal alternative) |
| **Claimed result** | readthedocs/ravi-benchmarks.rst (llvm branch, Lua 5.3.2 baseline, archived LLVM 3.9 backend): the 29x fornum row is a dead-store loop (0.3 ns per iteration, loop overhead only) and the 26x matmul1.ravi row is a different program (flat 1-D arrays with omitArrayGetRangeCheck); the closer typed port matmul1_ravi.lua runs at 1.137 s. Typed mandel and fannkuchen 10-26x with range checks skipped; untyped code only 1.6-2.5x. LuaJIT is equal or faster throughout. |
| **Workload** | Numeric micro-benchmarks in tests/performance (fornum loop tests, mandel1 at 4000, fannkuchen at 11, matmul1 at 1000), each as plain Lua and as Ravi-typed variants, timed under Lua 5.3.2, the Ravi interpreter, Ravi with the LLVM JIT, and LuaJIT 2.1 interpreter and JIT. |
| **Metric** | throughput |
| **Hardware** | Windows 10 64-bit; CPU not stated. |
| **Compiler and flags** | Ravi and Lua 5.3.2 compiled with Visual C++ 2015 (flags not stated); LLVM 3.9 JIT backend. |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/dibyendumajumdar/ravi) · [benchmark](https://github.com/dibyendumajumdar/ravi/blob/llvm/readthedocs/ravi-benchmarks.rst) |

## Verdict

The author's 2016-era table (readthedocs/ravi-benchmarks.rst, llvm branch) times numeric scripts on Windows 10 64-bit, unknown CPU, Visual C++ 2015 builds of Lua 5.3.2 and Ravi, LLVM 3.9 JIT, compile time excluded: typed mandel1 1.571 s, fannkuchen 4.634 s and matmul 1.039 s versus untyped Lua 5.3.2 runs of 20.324, 46.203 and 26.672 s (about 13x, 10x, 26x, derived from page data), roughly matching LuaJIT 2.1 (1.594, 4.672, 1.078 s). Untyped code under the Ravi JIT gains only 1.6-2.5x, and the Ravi interpreter alone is within about 5% of Lua 5.3.2.

## Use it when

- Numeric loops in embedded Lua 5.3 code where you can annotate locals and arrays as integer, number, integer[] or number[] and pre-compile the hot functions at startup.
- You need Lua 5.3 semantics (64-bit integers, integer division, utf8, 5.3 C API) that LuaJIT's Lua 5.1 dialect does not provide, with JIT speed on typed hot paths.
- Hosts on Linux or macOS that can ship a shared library with a vendored JIT (MIR is bundled; no LLVM dependency any more).
- Projects that want to AOT-compile some Ravi modules to native shared libraries or inline small C snippets (alpha compiler framework).

## Skip it when

- Untyped Lua code: in the author's table the JIT gains only 1.6-2.5x over Lua 5.3.2 on untyped mandel, fannkuchen and matmul, and LuaJIT 2.1 is about 5-16x faster than the Ravi JIT on those same untyped programs (derived from page data).
- Windows with JIT: the MIR build instructions say the JIT does not work correctly on Windows (stack unwinding), although the published benchmarks were run on Windows with the old LLVM backend.
- Coroutine-heavy, tail-recursive or debug-hook code: JIT code runs only on the main thread (coroutines are interpreted), JIT tail calls are plain calls limited to about 110 deep, and the debug API and hooks are unavailable in JIT mode.
- Code that needs a fast C FFI or cross-function inlining; the benchmark page notes Ravi has neither, unlike LuaJIT.
- Programs near Lua's parser limits: Ravi halves MAXUPVAL, MAXREGS, MAXVARS and LUAI_MAXCCALLS to about 125, and its bytecode is incompatible with Lua 5.x.

## How it is fast

Type annotations let the front end emit specialised bytecodes (integer/float arithmetic, typed array get/set, integer for-loops) that skip Lua's dynamic tag checks, with runtime type assertions where values cross from untyped code. The bytecode JIT translates each compiled function's bytecode to C source and compiles it in-process with MIR's c2mir and MIR generator (optimisation level 0-3, default 2); the published numbers came from the earlier LLVM 3.9 backend. An omitArrayGetRangeCheck compile option drops bounds checks on typed array reads.

## Compared with alternatives

Pick Ravi over LuaJIT Remake (Deegen) when you need Lua 5.3 semantics, an embeddable C library with optional typing and a JIT/AOT path rather than a faster Lua 5.1 interpreter; pick Terra instead when you want explicitly staged low-level code generated from Lua rather than a typed Lua dialect.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none external for the default build (MIR/c2mir vendored); readline for the REPL on some Linux builds (issue #254) |
| **Minimum toolchain** | C99, CMake 3.12+; Visual Studio 2019 documented for Windows (interpreter only in practice) |
| **Platforms** | Interpreter: portable C99 (Linux, macOS, Windows). MIR JIT: Linux and macOS; not reliable on Windows per ravi-mir-instructions.rst. CPU architectures for the JIT follow MIR's backends (not documented in the Ravi pages read). |
| **Thread safety** | Same model as Lua 5.3: one lua_State per thread, no shared-state locking; JIT state is per global_State (not documented beyond this) |
| **Drop-in for the baseline** | partial — runs Lua 5.3 source in interpreted mode and keeps the Lua 5.3 C API, but bytecode is incompatible, several limits are halved, the GC interface follows Lua 5.4, and the speedups need type annotations plus explicit ravi.compile calls |

## Gotchas

- Harness flaws behind the headline ratios: fornum_test1 (29x) is a dead-store loop (j = i for 1e9 iterations, returning only the last value), so it times empty-loop overhead (0.309 s, about 0.3 ns per iteration); fornum_test3 likewise overwrites j in an inner 3-iteration loop. They show JIT loop overhead, not useful work.
- The 26x typed matmul figure (matmul1.ravi, 1.039 s) is a different program from matmul1.lua: it stores matrices as flat 1-D number arrays (matrix.mul2/gen2) instead of tables of rows and compiles with omitArrayGetRangeCheck=1; matmul1_ravi.lua (1.137 s) is the closer typed port. The current fannkuchen.ravi and mandel1.ravi also pass omitArrayGetRangeCheck=1, which the page mentions only for matmul.
- All published numbers are from about 2016 on the archived LLVM 3.9 backend with JIT compile time excluded (ravi.compile runs before the os.clock window, and LuaJIT gets one untimed warm-up run); no numbers exist for the current MIR backend, whose code path (bytecode to C to c2mir) is different.
- A 2026-09-12 interpreter review in the repo (readthedocs/INTERPRETER_REVIEW.md) found typed integer-array stores silently truncating floats, 64-bit array indices narrowed to 32 bits before the bounds check (a[4294967297] aliased a[1]), fixed-size arrays growing, and a coroutine/defer use-after-realloc crash; commits the same day say they fixed all four (#267-#270), so older builds carry them.

## Known shortcomings

- Raised D to C on readthedocs/ravi-benchmarks.rst (llvm branch) and ravi-luaconf-2015.pdf: about 29x on fornum and 10-26x on typed mandel, fannkuchen and matmul over Lua 5.3.2 but only 1.6-2.5x untyped; the LLVM backend is archived, JIT compile time is excluded, matmul bounds checks were off, no CPU or flags, no MIR-backend numbers, and LuaJIT is equal or faster.
- Enricher: fornum_test1 (the 29x row) is a dead-store loop timing only loop overhead (0.3 ns per iteration); the 26x matmul1.ravi is a different program (flat 1-D arrays, mul2/gen2 plus omitArrayGetRangeCheck) while the closer typed port matmul1_ravi.lua runs at 1.137 s, and fannkuchen.ravi also skips range checks. All numbers come from the archived LLVM 3.9 backend; the MIR JIT has no numbers and its docs say it does not work correctly on Windows. Interpreter bugs #267-#270 (readthedocs/INTERPRETER_REVIEW.md) fixed 2026-09-12; 95 open issues.

## Caveats and trade-offs

All numbers are the author's own, from about 2016 (Lua 5.3.2, LLVM 3.9, Visual C++ 2015, Windows 10) with no CPU or flags given. They measure the LLVM JIT backend, which the README says is archived; the current MIR backend has no published numbers that were found, so today's performance is unverified. JIT compilation time is excluded, the large wins need Ravi type annotations (untyped Lua code gains only 1.6-2.5x), and matmul ran with array read bounds checks disabled. The README says Ravi favours maintainability, safety and Lua 5.3 compatibility over maximum performance, and LuaJIT 2.1 is as fast or faster on every benchmark. The benchmark page is no longer in master's readthedocs folder (only on the llvm branch; the readthedocs.io copy is blocked here, its numbers were confirmed from a search snippet and the branch file).

Dialect of Lua with optional type annotations (not a drop-in for LuaJIT-style Lua 5.1 code); JIT backend is MIR, with AOT compilation to shared libraries; Lua 5.4 generational GC backported. Compatible with Lua 5.3 programs.

## Maintenance

Sporadically maintained (bursts in June 2024, February 2025 and September 2026, 95 open issues) and MIT-licensed; usable as a Lua 5.3 replacement library, but its performance claims describe a backend that was archived in 2020 and nobody has published MIR-era numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded D to C: the author's benchmark page (readthedocs/ravi-benchmarks.rst, still on the archived llvm branch) and the 2015 Lua Workshop slides in the repo give timings against Lua 5.3 and LuaJIT 2.1, with benchmark programs public in tests/performance; first-party, and no CPU model or compiler flags (only Windows 10 64-bit, LLVM 3.9, Visual C++ 2015), so not A or B.
- **Verifier notes:** Upgrade D to C: numbers exist in readthedocs/ravi-benchmarks.rst on the llvm branch and in readthedocs/ravi-luaconf-2015.pdf on master, against Lua 5.3.2 (in-list baseline) with benchmark code in tests/performance. Main shortcomings: measured on the archived LLVM backend with JIT time excluded and typed code only, no CPU/flags, no numbers for the current MIR JIT. Metadata (MIT, 1.3k stars, last commit 2026-09-12, not a fork) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dibyendumajumdar/ravi>
  - <https://github.com/dibyendumajumdar/ravi/commits>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/README.rst>
  - <https://github.com/dibyendumajumdar/ravi/tree/master>
  - <https://github.com/dibyendumajumdar/ravi/tree/master/readthedocs>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/ravi-overview.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/ravi-luaconf-2015.pdf>
  - <https://github.com/dibyendumajumdar/ravi/tree/master/tests>
  - <https://github.com/dibyendumajumdar/ravi/tree/master/tests/performance>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/llvm/readthedocs/ravi-benchmarks.rst>
  - <https://github.com/dibyendumajumdar/ravi/blob/llvm/readthedocs/ravi-benchmarks.rst>
- **Sources the enricher read:**
  - <https://github.com/dibyendumajumdar/ravi>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/README.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/ravi-overview.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/llvm/readthedocs/ravi-benchmarks.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/ravi-reference.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/ravi-mir-instructions.rst>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/readthedocs/INTERPRETER_REVIEW.md>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/src/ravi_mirjit.c>
  - <https://github.com/dibyendumajumdar/ravi/tree/master/tests/performance>
  - <https://github.com/dibyendumajumdar/ravi/tree/master/readthedocs>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fornum_test1.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fornum_test2.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fornum_test2.ravi>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fornum_test3.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/mandel1.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/mandel1.ravi>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fannkuchen.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/fannkuchen.ravi>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/matmul1.lua>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/matmul1.ravi>
  - <https://raw.githubusercontent.com/dibyendumajumdar/ravi/HEAD/tests/performance/matmul1_ravi.lua>
  - <https://github.com/dibyendumajumdar/ravi/issues>
  - <https://github.com/dibyendumajumdar/ravi/commits>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dibyendumajumdar/ravi`) · [data/wave12/enrich/raw/github_com_dibyendumajumdar_ravi.json](../../../data/wave12/enrich/raw/github_com_dibyendumajumdar_ravi.json) (enrichment confidence 0.75)

</details>
