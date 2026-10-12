# FakeLua

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Embeddable Lua 5.4-subset runtime that compiles scripts to C (GCC/TCC) and runs numeric kernels 30-40x faster than PUC Lua 5.4.

| | |
|---|---|
| **Beats** | PUC Lua 5.4.7 (LuaJIT not compared) |
| **Claimed result** | JIT_GCC vs PUC Lua 5.4 (CPU-time ratios, 2026-08-14 run): Fibonacci n=32 36.6x (277.9 ms vs 7.59 ms CPU), Sum n=5M 30.4x, Popcount n=100K 37.3x, FloatPoly n=1M 34.9x, Recursion n=25 42.9x, TailRecursion n=5K 107.5x (that bench has since been removed from the harness); TCC backend Fibonacci n=32 11.2x (derived from page data: 277.9 ms vs 24.86 ms CPU). Most table and string rows are only 1.0-6.1x (TableChurn 9.3x); GCD 0.45x, ToNumber 0.53x, Variadic 0.91x and StringFind 0.85x are slower, and the Boost.Regex rows are much slower (0.06-0.21x). |
| **Workload** | 51 Lua micro-scenarios in 6 categories (algorithms, strings, tables, function calls, ...), Google Benchmark harness bench_mark, FakeLua JIT_GCC and JIT_TCC backends versus Lua 5.4 and hand-written C++. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7K62 48-Core Processor, 2-vCPU VM at 2595 MHz, load average 5.87 during the run (GCC/TCC JIT run, 2026-08-14); AMD EPYC 7551, 16-vCPU KVM (interpreter run, 2026-09-16) |
| **Compiler and flags** | Release build, -O3 -DNDEBUG (plus -g3 -fPIC from the top-level CMakeLists); GCC 15.1.0 for the JIT_GCC run, whose generated C is compiled at -O3 at script load; GCC 16.2.0 for the interpreter run. Lua baseline is the system liblua5.4 found via pkg-config (distro build flags not stated); Lua 5.4.7 is named only for the 2026-09-16 interpreter run. Google Benchmark v1.9.4. |
| **Adoption** | 214 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/esrrhs/fakelua) · [benchmark](https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/README.md) |

## Verdict

In one Google Benchmark binary that verifies every result, FakeLua's GCC backend (generated C built with system GCC 15.1.0 at -O3, run on a loaded 2-vCPU AMD EPYC 7K62 VM on 2026-08-14) beat the distro PUC Lua 5.4 library by 36.6x on Fibonacci n=32 (277.9 ms vs 7.59 ms CPU), 30.4x on a 5M-iteration sum, 37.3x on popcount and 34.9x on a float polynomial, while table and string rows were mostly 1.0-6x and several call-bound rows were slower. A later 2026-09-16 run (EPYC 7551, GCC 16.2.0, Lua 5.4.7) covers only the bytecode interpreter, which is slower than Lua 5.4 on algorithm rows.

## Use it when

- C++ game or real-time servers that embed short Lua-syntax logic scripts and want no GC pauses, with long-lived state kept on the C++ side
- Integer and float loops and recursive numeric functions (Fibonacci, sums, bit tricks, polynomial evaluation) where the GCC backend measured 30-43x over PUC Lua 5.4
- Table-heavy scripts with literal keys (struct specialization) or many short-lived tables per frame (TableChurn 9.3x via the arena)
- Hosts where a system GCC is available at run time and a one-off compile at script load is acceptable; JIT_TCC for fast iteration in development

## Skip it when

- Existing Lua code that uses coroutines, metatables/metamethods, require, the debug library or implicit string-to-number coercion; it will not run
- When LuaJIT is the incumbent: it was never compared, so no win over LuaJIT is shown
- Call-dominated or tiny functions: GCD 0.45x, ToNumber 0.53x, Variadic 0.91x and StringFind 0.85x were slower than PUC Lua under JIT_GCC, and the bytecode interpreter is 1.3-7.6x slower than Lua 5.4 on algorithm rows (34x on deep tail recursion, which it does not eliminate)
- Scripts that keep large data alive across frames: there is no GC, memory is reclaimed only by the per-frame arena reset
- Deployments that cannot ship a C compiler or tolerate fork/exec of gcc from the host process; the repository is young and changes fast (multiple correctness fixes per week in September-October 2026)

## How it is fast

Lua source is translated to C: a type inferencer finds parameters used in arithmetic and emits 2^k int64_t/double specializations behind a type-dispatching entry, so hot numeric code runs unboxed; table constructors with static keys become C structs accessed by fixed offsets. JIT_GCC writes the C to a temp file, runs the system `gcc -x c -shared -fPIC -O3` and dlopens the result, so GCC's own optimizations (vectorization, popcount idiom recognition, tail-call-to-loop) do the heavy lifting; JIT_TCC uses embedded TinyCC for fast compiles. Memory is a bump-pointer arena reset per frame with State::Reset() instead of a garbage collector.

## Compared with alternatives

Pick FakeLua when you want Lua-syntax scripting embedded in a C++ server with C-compiler-grade numeric code and no GC, and can live with a Lua subset; pick libriscv (also libtcc-based, measured against LuaJIT) when you need sandboxed execution of arbitrary compiled guest code, or a general-purpose JIT language such as Julia or Chez Scheme when you need full language semantics rather than an embedded script layer.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target fakelua::fakelua, find_package and pkg-config supported) plus the flua CLI |
| **Dependencies** | TinyCC (fetched from the unpinned 'mob' branch), Boost 1.90 (regex, json, container, algorithm and others), OpenSSL (find_package REQUIRED), libevent, hiredis, MariaDB Connector/C, SQLite amalgamation, lz4, zlib, zstd, yaml-cpp, pugixml, toml++, inih, all fetched by CPM; system gcc on PATH at run time for JIT_GCC; liblua5.4-dev only for tests and benchmarks |
| **Minimum toolchain** | C++23 (README: GCC 11+, Clang 16+, MSVC 2022+), CMake 3.5+ |
| **Platforms** | Linux, macOS and Windows (MSYS2/MinGW) per CI badges; GCC JIT is not given -march flags, so it targets the host's default ISA |
| **Thread safety** | One State per thread; the README says each State is currently thread-local and must not be shared |
| **Drop-in for the baseline** | partial — scripts in the supported subset run unchanged, but the embedding API (Call/CompileFile instead of the Lua C API) and the missing features (coroutines, metatables, require) make it a different runtime, not a liblua replacement |

## Gotchas

- Harness flaw in the 2026-08-14 GCC run: the hand-written C++ reference rows are 8-18x slower than FakeLua's GCC-compiled version of the identical C loops (C++ Fibonacci n=32 60.6 ms vs 7.59 ms CPU, Sum n=5M 27.4 ms vs 1.55 ms, Popcount 5.0 ms vs 0.59 ms). Their per-step cost of about 5.5-8.6 ns fits a host binary built with per-basic-block atomic coverage counters (the project's USE_COV option adds -fprofile-update=atomic) or without optimization, not the stated Release -O3 (inference, not stated on the page). The 'GCC vs C++' column and any 'faster than C++' claim are therefore invalid. The JIT code is compiled by a separate `gcc -O3` call and Lua is the distro library, so the headline Lua ratios are not inflated by this; if anything, FakeLua's own runtime (Call dispatch, tables, strings) was slowed too.
- The 'MultiReturn' benchmark (23.3x) calls inner_multi, which returns a single value, so it measures plain single-return calls rather than multiple returns.
- The README's headline table (Fibonacci 297.9 ms vs 6.8 ms, Sum 33.9 ms vs 1.1 ms) does not match the raw output on benchmark/README.md (277.9 ms vs 7.59 ms CPU); use the raw rows. The regex rows used Boost.Regex, which commit a55a4bf (2026-10-03) replaced with a Lua 5.4 pattern engine, so the string-pattern ratios are obsolete in both directions.
- JIT_GCC forks and execs `gcc` from PATH and writes temporary .c/.so files at script load; compile time is excluded from all benchmark numbers. TinyCC is fetched from the moving 'mob' branch, so builds are not pinned.

## Known shortcomings

- Baseline is PUC Lua 5.4 (distro liblua5.4), not LuaJIT; the GCC 15.1.0 -O3 run (EPYC 7K62, 2026-08-14) was on a loaded 2-vCPU VM and predates the math-spec fixes 236a757 and 598632f (edge cases outside the bench scripts). The record's '297.9 ms vs 6.8 ms' was not on the page; the real CPU times are 277.9 ms vs 7.59 ms (36.6x). The TailRecursion bench (107.5x) was removed in 12fbcd7, the regex rows may be obsolete after a55a4bf, and the C++ reference column is anomalous.
- Enricher: in the 2026-08-14 GCC run the C++ reference rows are 8-18x slower than FakeLua's GCC JIT on identical C loops (Fib n=32 60.6 ms vs 7.59 ms CPU, Sum 27.4 vs 1.55 ms, Popcount 5.0 vs 0.59 ms), a per-step cost of about 5.5-8.6 ns that fits a coverage-instrumented (USE_COV, -fprofile-update=atomic) or unoptimized host build rather than the stated -O3, so the 'GCC vs C++' column and any 'faster than C++' claim are invalid; the Lua ratios stand (JIT code built by a separate gcc -O3, Lua is the distro library). The MultiReturn bench returns a single value, the README headline table disagrees with the raw rows, TinyCC is pulled unpinned from 'mob', and OpenSSL is REQUIRED despite the FAQ calling native dependencies optional.

## Caveats and trade-offs

Baseline is PUC Lua 5.4 (distro liblua5.4), not LuaJIT, so the result does not show a win over LuaJIT. Lua source is compiled to C and built by GCC/TCC at script load; that compile time is outside the timed region. The GCC JIT numbers come from a 2026-08-14 run on a loaded 2-vCPU cloud VM (wall times about 1.6x CPU times; the ratios use CPU time) and predate many later correctness fixes, including math-specialization eligibility fixes (commits 236a757 and 598632f, 2026-10-02); those fixes target shadowed, nested, multi-return and vararg functions that the bench scripts do not use, and the harness verifies every result, but the GCC run has not been repeated on current code. The TailRecursion bench (107.5x) was removed from the harness on 2026-09-18 (commit 12fbcd7), so that row is not reproducible from HEAD. The regex rows used Boost.Regex; commit a55a4bf (2026-10-03) implements Lua 5.4 patterns, so those rows may be obsolete. Some StringFindPattern/StringGmatch raw lines predate a workload correction (the page says so). The hand-written C++ reference column is not credible: the page says some references are folded, and C++ Sum n=5M took 27.4 ms CPU against 1.55 ms for FakeLua's GCC-compiled version of the same loop, so 'faster than C++' claims should be ignored. The bytecode interpreter tier is 1.3x to 7.6x slower than Lua 5.4 in its algorithm rows (34x on TailRecursion). Very young, fast-moving repository. [retier] Baseline is PUC Lua 5.4 (distro liblua5.4), not LuaJIT. The 2026-08-14 GCC run (EPYC 7K62, loaded 2-vCPU VM) predates the math-spec fixes 236a757 and 598632f. CPU times 277.9 ms vs 7.59 ms on Fib (36.6x); TCC 11.2x derived. The C++ reference column is invalid: 8-18x slower than the GCC JIT on identical loops (Fib n=32 60.6 vs 7.59 ms, Sum 27.4 vs 1.55 ms, Popcount 5.0 vs 0.59 ms), a 5.5-8.6 ns per-step cost that fits a coverage-instrumented (USE_COV) or unoptimized host build, so ignore any 'faster than C++' reading. TailRecursion bench removed in 12fbcd7; regex rows obsolete after a55a4bf; MultiReturn bench returns a single value; README headline table disagrees with the raw rows; TinyCC pulled unpinned from 'mob'; OpenSSL REQUIRED.

Runs a Lua 5.4 subset: no coroutines, metatables or require, and no implicit string-number coercion; arena allocation with per-frame reset instead of GC. JIT_GCC shells out to the system GCC at run time (compile latency and a compiler dependency); JIT_TCC uses embedded TinyCC; JIT_INTERP bytecode VM needs no compiler.

## Maintenance

Actively developed (last commit 2026-10-03, 566 commits, 0 open issues) and MIT-licensed, but very young, heavy on dependencies and still landing correctness fixes in its specializer, so pin a commit and run its tests on your scripts before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Public Google Benchmark harness (benchmark/benchmark_algo.cpp, benchmark_function.cpp, benchmark_string.cpp, benchmark_table.cpp, benchmark_gc.cpp, benchmark_math.cpp; benchmark_common.cpp checks every iteration's result with VerifyEqual, which throws on a wrong answer) runs FakeLua JIT_GCC/JIT_TCC/JIT_INTERP against PUC Lua 5.4 in the same binary, and benchmark/README.md states GCC 15.1.0, -O3 -DNDEBUG (Release) and the CPU model (AMD EPYC 7K62) for the GCC JIT run, with full raw output. All A criteria are met; the headline ratios match the page's CPU-time rows.
- **Verifier notes:** Ratios check out against the raw CPU-time rows (Fib 277,915,868 ns vs 7,590,283 ns; Sum 46.98 ms vs 1.55 ms; Popcount 22.1 ms vs 0.593 ms; TailRecursion 209.8 us vs 1.95 us), but the record's '297.9 ms vs 6.8 ms' Fibonacci figures are not on the page and were corrected; the TCC 11.2x is a derived ratio. Shortcomings to record: baseline is PUC Lua not LuaJIT; GCC numbers come from an older (2026-08-14) run on a loaded 2-vCPU VM that predates later math-specialization correctness fixes (edge cases outside the bench scripts; results were verified); the TailRecursion bench was later removed; the C++ reference column is anomalous. Metadata confirmed: MIT, 214 stars, not a fork, last commit 2026-10-03.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/README.md>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_algo.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_function.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_common.h>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_common.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/CMakeLists.txt>
  - <https://github.com/esrrhs/fakelua>
  - <https://github.com/esrrhs/fakelua/commits>
  - <https://github.com/esrrhs/fakelua/commits/master>
  - <https://github.com/esrrhs/fakelua/commit/236a757>
  - <https://github.com/esrrhs/fakelua/commit/12fbcd7>
  - <https://github.com/esrrhs/fakelua/commit/598632f>
  - <https://github.com/esrrhs/fakelua/commit/a781e47>
- **Sources the enricher read:**
  - <https://github.com/esrrhs/fakelua>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/README.md>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_common.h>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_common.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_algo.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_function.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_table.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/benchmark/benchmark_gc.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/jit/gcc_jit.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/jit/gcc_handle.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/compile/c_gen.cpp>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/compile/c_gen.h>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/compile/c_runtime_header.h>
  - <https://raw.githubusercontent.com/esrrhs/fakelua/HEAD/src/CMakeLists.txt>
  - <https://github.com/esrrhs/fakelua/tree/master/src/jit>
  - <https://github.com/esrrhs/fakelua/issues>
  - <https://github.com/esrrhs/fakelua/commits/master>
  - <https://github.com/esrrhs/fakelua/commit/a55a4bf>
  - <https://github.com/esrrhs/fakelua/search?q=FL_INT_ADD>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/esrrhs/fakelua`) · [data/wave12/enrich/raw/github_com_esrrhs_fakelua.json](../../../data/wave12/enrich/raw/github_com_esrrhs_fakelua.json) (enrichment confidence 0.75)

</details>
