# Mobius

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Embeddable C-syntax scripting language with a register bytecode VM; about 16% less total time than Lua 5.4 on its own micro-suite.

| | |
|---|---|
| **Beats** | Lua 5.4 and CPython 3 |
| **Claimed result** | README totals 373.9 ms vs Lua 443.3 ms vs CPython 1424.8 ms are whole-script times including untimed setup; per-row geomean is 0.93x of Lua's time and 0.47x of CPython's (about 2.1x faster than CPython, not 3.8x; derived from page data). The committed benchmark_summary_latest.json (2026-07-12) has Mobius 1.3x slower than Lua. |
| **Workload** | Eight checksum-verified micro-benchmarks (integer arithmetic, fib(30), dense array ops, string-key table ops, string ops, nested loops, object create and destroy, mixed workload), median of five runs, in milliseconds. |
| **Metric** | throughput |
| **Compiler and flags** | buildy.yaml release configuration: -O3 -march=native -funroll-loops -flto with -flto -Wl,-O1 at link on Linux (macOS: -O3 -funroll-loops -flto); run_benchmarks.py picks bin/mobius or build/linux-x86_64-release/bin/mobius. Which build produced the README table is not stated. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/bholcomb/mobius) · [benchmark](https://github.com/bholcomb/mobius) |

## Verdict

On the project's own eight checksum-verified micro-benchmarks (median of five runs, run_benchmarks.py), the README reports a total of 373.9 ms for Mobius vs 443.3 ms for Lua 5.4 and 1424.8 ms for CPython 3; Mobius wins five of eight rows against Lua and five of eight against CPython. The Mobius build is the release configuration (-O3 -march=native -funroll-loops -flto, C++17), but the CPU, the Lua build and the CPython version are not stated and the raw results behind the table are not committed.

## Use it when

- Adding a scripting layer to a C or C++ application (game engine, editor, tool) where you want C-like syntax and Lua-class interpreter speed on integer loops and string building.
- Scripts that need concurrency inside the language: fan-out with spawn/await across worker threads without writing a native threading layer.
- Standalone tools and small web services that benefit from JSON, HTTP, SQLite and WebSockets shipped with the runtime instead of third-party packages.
- Replacing CPython for CPU-bound integer loops in an embedded context: its arithmetic and nested-loop rows are 6.5-8x faster than CPython in the project's own table.

## Skip it when

- When raw speed is the goal: it is only on par with PUC Lua 5.4 (slower on fib(30), dense arrays and string-key tables) and far behind LuaJIT, which the project does not compare against.
- Workloads dominated by string handling, short-lived containers or record building: CPython beat it on string ops (1.69x), object create/destroy (1.14x) and the mixed workload (1.15x).
- Tight memory budgets: a minimal embedded state peaks around 6.3 MB RSS (5.4 MB tuned) and starts worker threads by default, far heavier than a Lua state.
- Production use that needs stability or TLS: version 0.1.0, 3 stars, one main author, the C API changed repeatedly in October 2026 (userdata parameters, removed time limits and abort), Windows and macOS ports marked untested, and network modules are plain-transport only.
- Code that relies on Lua or Python integer semantics: Mobius '/' truncates and '%' is a C-style remainder, so negative operands give different results.

## How it is fast

A Lua-style register VM with 32-bit ABC/ABx instructions and RK constant operands, dispatched with computed goto (labels-as-values) on GCC and Clang. Type locking lets the compiler emit type-specialized opcodes (ADD_II, LT_II, integer-only IFORPREP/IFORLOOP, immediate-operand ADDI/LTI) and the peephole stage emits superinstructions such as MOVE_ADDI, GETGLOBAL_CALL, CALL_DIRECT and AGET_ADD_CHECK (a fused 'sum = sum + arr[i]' that never materializes the element). Type tags live in a separate array beside the registers, strings are interned, and memory is reclaimed by reference counting with a backup cycle collector.

## Compared with alternatives

Pick Mobius over Wren or pocketpy when you want built-in multi-threaded fibers and a large bundled standard library in an embeddable C-syntax language; pick LuaJIT when interpreter or JIT speed matters most, and Wren or plain Lua when you need a small, mature, low-memory runtime.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | pthread and dl on Linux for the core; bundled modules pull in miniz, SQLite and others; built with the repo's own bundled 'buildy' build tool (committed binaries), not CMake |
| **Minimum toolchain** | C++17 (buildy.yaml cpp_standard c++17); computed-goto dispatch needs GCC or Clang, other compilers fall back to a switch loop |
| **Platforms** | Linux x86-64 is the tested platform; Windows and macOS ports were added 2026-10-04 and are marked untested; release builds use -march=native (a 'portable' configuration targets x86-64-v2) |
| **Thread safety** | Each MobiusState is independent and can run concurrently with others; within a state, fibers run on a worker-thread pool (default hardware_concurrency/2 - 1 extra threads), reference counts are atomic and shared containers use locks; registered native functions may be called from any worker thread and must be thread-safe themselves. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetries in the README benchmark: the Mobius fib(30) function is annotated 'n: int64): int64' even though the comment above it says 'Deliberately left un-annotated: this is the un-specialized call path' (the Lua and Python versions cannot express types); the mixed workload preallocates its Mobius array with array_create(n) inside the timer while Lua and Python grow from empty; Lua times itself with os.clock (process CPU time) while Mobius and Python use monotonic wall clocks; Mobius is built -O3 -march=native -flto while Lua and CPython are whatever binaries are on PATH.
- The Total row is the median of each script's whole-run timer, which includes untimed setup; the eight row medians sum to 359.0 ms (Mobius) vs 420.3 ms (Lua) vs 1402.6 ms (CPython). The total is dominated by the arithmetic row (850.9 of CPython's 1424.8 ms), so the geometric mean of the eight row ratios is about 0.93x of Lua's time and 0.47x of CPython's (about 2.1x faster, not 3.8x) (derived from page data).
- The raw output behind the README table is not committed; the committed benchmark_summary_latest.json (2026-07-12) predates later VM and benchmark-script changes and shows Mobius about 1.3x slower than Lua.
- Several superinstructions (AGET_ADD_CHECK for 'sum = sum + arr[i]', ADD_CHECK for locked accumulators, MOVE_MULI) match the benchmark loops' exact shapes, so the suite may flatter Mobius relative to code that does not hit those patterns.

## Known shortcomings

- The README Lua win (373.9 vs Lua 443.3 vs CPython 1424.8 ms) has no committed raw results; the committed benchmark_summary_latest.json (2026-07-12, Mobius 1.3x slower than Lua) predates the 2026-07-13/14 optimization commits and benchmark-script changes (typed fib parameters for Mobius only, mixed-workload data[i] fix). Hardware, Lua and CPython versions unstated, 3 stars.
- Enricher: the fib benchmark is annotated 'n: int64): int64' under a comment saying it is deliberately unannotated, the mixed workload preallocates with array_create(n) inside the timer while Lua and Python start empty, Lua times os.clock (CPU time) against wall clock for the others, and Mobius is built -march=native -flto against Lua and CPython from PATH; the total row is whole-script time including untimed setup (row sums 359.0/420.3/1402.6 ms). The arithmetic row dominates: geomean 0.93x of Lua and 0.47x of CPython (about 2.1x, not 3.8x, derived). Superinstructions such as AGET_ADD_CHECK match the benchmark loop shapes.

## Caveats and trade-offs

The committed raw results (benchmarks/benchmark_summary_latest.json and benchmark_comprehensive_\*_latest.txt, last changed 2026-07-12 in commit 7f9a92c) show Mobius totalling 0.547 s vs Lua 0.420 s (about 1.3x slower than Lua) and CPython 1.419 s (about 2.6x faster) (derived from page data). They predate the README table: the 2026-07-13 and 2026-07-14 commits added intrinsic opcodes and small-string pools (commit 4fdf039 reports 431 ms vs Lua 455 ms), slimmer call frames, table and array op fusions, added type annotations to the Mobius fib benchmark only (f32cde8), and changed the Mobius mixed workload from data:get(i) to data[i] (29a409c). So the README's Lua win is newer than the committed JSON rather than contradicted by it, but the raw output behind the README table is not committed. The Mobius fib script uses typed parameters that the Lua and Python scripts cannot express. Hardware, Lua build (run_benchmarks.py uses whatever 'lua' or 'lua5.4' is on PATH) and CPython version are not stated. Micro-benchmarks only; Mobius is slower than Lua on fib, dense arrays and string-key tables and slower than CPython on string ops, object create/destroy and the mixed workload; version 0.1.0, 3 stars. [retier] Benchmark scripts favour Mobius: fib is annotated 'n: int64): int64' despite a comment saying it is unannotated, the mixed workload preallocates with array_create(n) inside the timer while Lua and Python start empty, Lua is timed with os.clock (CPU time) against wall clock for the others, and Mobius is built -march=native -flto against Lua and CPython from PATH; superinstructions such as AGET_ADD_CHECK match the loop shapes. Hardware, Lua and CPython versions unstated; the README Lua win has no committed raw results; 3 stars.

Embeddable C/C++ scripting language with fibers, channels and worker threads, optional type locking, and a large built-in library (JSON, HTTP, SQLite, WebSockets). Version 0.1.0; no TLS yet. Integer division and modulo follow C semantics (truncating), unlike Lua and Python, per benchmarks/run_benchmarks.py.

## Maintenance

Actively developed (last commit 2026-10-04, 391 commits) but version 0.1.0 with a fast-moving C API and 3 stars; MIT-licensed and copyable, best treated as an experimental embeddable language rather than a drop-in faster Lua.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by the repo's own harness (benchmarks/run_benchmarks.py with benchmark_comprehensive.mob/.lua/.py, checksum-verified medians of five runs); release flags are in buildy.yaml but CPU model, Lua build and CPython version are not stated, so not A.
- **Verifier notes:** README table numbers match the record exactly (373.9 vs Lua 443.3 vs CPython 1424.8 ms). The search agent's contradiction is real but explained by timing: the committed benchmark_summary_latest.json (1.30x slower than Lua) is from 2026-07-12, before the 2026-07-13/14 optimization and benchmark-script commits that the README table reflects; record as shortcoming 'README Lua win not backed by committed raw results; committed results are stale and show Mobius 1.3x slower than Lua'. Metadata checked: MIT, 3 stars, last commit 2026-10-04.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/bholcomb/mobius>
  - <https://github.com/bholcomb/mobius/commits/main>
  - <https://github.com/bholcomb/mobius/tree/main/benchmarks>
  - <https://github.com/bholcomb/mobius/commits/main/benchmarks/benchmark_summary_latest.json>
  - <https://github.com/bholcomb/mobius/commits/main/benchmarks/benchmark_comprehensive_mobius_latest.txt>
  - <https://github.com/bholcomb/mobius/commits/main/benchmarks/benchmark_comprehensive.mob>
  - <https://github.com/bholcomb/mobius/commits/main/README.md>
  - <https://github.com/bholcomb/mobius/commit/29a409c>
  - <https://github.com/bholcomb/mobius/commit/4fdf039>
  - <https://github.com/bholcomb/mobius/commit/52b46d4>
  - <https://github.com/bholcomb/mobius/commit/612c62f>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/README.md>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_summary_latest.json>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive_lua_latest.txt>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive_mobius_latest.txt>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive_python_latest.txt>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/buildy.yaml>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/bholcomb/mobius>
  - <https://github.com/bholcomb/mobius/commits/main>
  - <https://github.com/bholcomb/mobius/tree/main/src>
  - <https://github.com/bholcomb/mobius/tree/main/src/mobius>
  - <https://github.com/bholcomb/mobius/tree/main/src/mobius/vm>
  - <https://github.com/bholcomb/mobius/tree/main/docs>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/README.md>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/run_benchmarks.py>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive.mob>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive.lua>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_comprehensive.py>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/benchmarks/benchmark_summary_latest.json>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/buildy.yaml>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/src/buildy.yaml>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/src/mobius/vm/opcodes.h>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/src/mobius/vm/vm.h>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/src/mobius/vm/vm.cpp>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/include/mobius/mobius.h>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/docs/embedding/embedding-guide.md>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/docs/reference/standard-library.md>
  - <https://raw.githubusercontent.com/bholcomb/mobius/HEAD/docs/guide/getting-started.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bholcomb/mobius`) · [data/wave12/enrich/raw/github_com_bholcomb_mobius.json](../../../data/wave12/enrich/raw/github_com_bholcomb_mobius.json) (enrichment confidence 0.75)

</details>
