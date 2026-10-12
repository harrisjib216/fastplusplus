# Squirrel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Small embeddable C++ bytecode VM for a Lua-like language with classes; ran fib(34) about 4.5x faster than Duktape 1.2.2 in 2015.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (the copy vendored in scriptorium's javascript/duktape; PUC Lua at 1.341 s in the same table is faster than Squirrel) |
| **Claimed result** | 2.126 s versus Duktape 1.2.2 at 9.544 s, about 4.5x faster than Duktape (derived from page data); in bench.csv's earlier session the ratio was about 3.5x (4.114 s vs 14.301 s, derived from page data). Slower than PUC Lua at 1.341 s (about 1.6x, derived from page data). |
| **Workload** | Recursive fibonacci test (tests/fib.\*) run as a separate process through the repo's bench.exe, wall time including process start-up averaged over 5 runs, July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | MSVC (VS2015 RC where possible, VS2013 elsewhere), static CRT; squirrel/make.bat builds Squirrel 3.0.7 with /Ox /Oy /MT /DNDEBUG and javascript/duktape/make.bat builds Duktape with /Ox /Oy /MT /DNDEBUG |
| **Adoption** | 1.1k stars; packaged as vcpkg port 'squirrel' and Conan Center recipe 'squirrel' |
| **Last commit** | 2026-02-28 |
| **Links** | [repository](https://github.com/albertodemichelis/squirrel) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

In r-lyeh's Scriptorium (July 2015, AMD A10 3.8 GHz, Windows 7 64-bit, MSVC VS2015 RC or VS2013, both engines built /Ox /Oy /MT /DNDEBUG), whole-process time for recursive fib(34), averaged over 5 launches, was 2.126 s for Squirrel 3.0.7 versus 9.544 s for Duktape 1.2.2 in the same pass, about 4.5x (derived from page data; 3.5x in an earlier, noisier pass); PUC Lua at 1.341 s was about 1.6x faster than Squirrel.

## Use it when

- Games or real-time C++ applications that want a compact scripting VM with no GC pauses (reference counting plus an explicit, host-triggered cycle collector).
- Script authors who prefer C/JavaScript-like syntax with built-in classes and inheritance over Lua's tables-and-metatables.
- Embedding on Windows, Linux, FreeBSD, Illumos or ARM boards from source or via the vcpkg/Conan packages, including compiler-less builds (NO_COMPILER) that only run precompiled bytecode.
- Several independent interpreters in one process (each sq_open creates its own shared state), or many cooperative coroutines inside one VM via sq_newthread.

## Skip it when

- Raw interpreter speed is the priority: on the same Scriptorium table PUC Lua (1.341 s), Wren (1.997 s) and AngelScript (2.039 s) beat Squirrel (2.126 s) on fib(34), and LuaJIT is far ahead.
- Running untrusted scripts or bytecode: the issue tracker has open, unanswered memory-safety reports from 2026 (#315 'Out Of Bounds Access Leads to Sandbox Breakout', #324 to #327 heap and stack buffer overflows in bytecode loading and format validation, #310 to #312 compiler overflows).
- You need responsive upstream maintenance: commits are sparse (Nov 2024, then one merged pull request on 2026-02-28) and about 91 issues are open.
- Floating-point-heavy code with default settings: SQFloat is a 32-bit float unless SQUSEDOUBLE is defined, and that switch is not in the build documentation.
- Host-to-script call overhead is the bottleneck: taksatou/embench (i7-2600S, Linux) measured 100000 echo calls at 22.3 ms for Squirrel versus 15.2 ms for Lua and 12.5 ms for LuaJIT, though Squirrel was slightly faster than Lua on its 'invert' test (480.0 vs 505.4 ms).

## How it is fast

Source is compiled to a register-based bytecode (each SQInstruction carries a target and up to three operand registers or a 32-bit immediate) executed by a single switch-dispatched loop in SQVM::Execute. Values are tagged unions (type plus value), so integers and floats are unboxed, and the arithmetic macros take a fast path when both operands are integers or floats. Memory is reference counted, so most objects are freed immediately with no GC pauses; an optional mark-and-sweep pass for cycles only runs when the host calls sq_collectgarbage. Nothing here is unusual for a bytecode VM; the gap to Duktape 1.2.2 says as much about Duktape's slow interpreter as about Squirrel.

## Compared with alternatives

Pick Squirrel over AngelScript when you want dynamic typing with classes and coroutines and no GC pauses; pick AngelScript for statically typed, C++-like scripts with similar speed (2.039 s vs 2.126 s), mruby (2.098 s) for Ruby syntax, and Luau or Lua when speed or a maintained, fuzzed sandbox matters more. Gaijin's Quirrel fork (already noted as a seed lead) is a more actively developed descendant.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libsquirrel + sqstdlib via CMake), or source-drop of the squirrel/ and sqstdlib/ .cpp files |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 per CMakeLists (CMake 3.12+); README lists MSVC 6.0 to 12.0 and gcc 3.2 to 5.3.1 as confirmed; builds with -fno-exceptions -fno-rtti on GCC |
| **Platforms** | Windows (x86, amd64), Linux (x86, amd64, ARM), Illumos, FreeBSD (x86, ARM); _SQ64 is auto-defined for _WIN64/_LP64 |
| **Thread safety** | Not documented as thread-safe. Each sq_open VM has its own SQSharedState, so separate VMs can live on separate threads; friend VMs from sq_newthread share that state (non-atomic reference counts) and are coroutines, not concurrent threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness limits behind the 4.5x: Scriptorium's bench.exe times five whole-process system() launches (start-up included) and never checks the printed result, and the test is a single recursive fib(34) in which fibR is a root-table global (a table lookup per call; the JavaScript and Lua versions are globals too). The 2.126 s Squirrel and 9.544 s Duktape rows come from the same alphabetical pass in bench.csv (lines 49 to 81), but the first pass gave 4.114 s versus 14.30 s (about 3.5x), so session noise moved the ratio by about a quarter. The timed build was Squirrel 3.0.7 (built with cl /Ox /Oy /MT /DNDEBUG), not today's 3.2.
- The baseline is Duktape 1.2.2, much older than Duktape 2.x; against a modern JavaScript interpreter such as QuickJS no comparison exists in the evidence.
- Reference counting means cycles (a table that refers to itself, closures captured in their own environment) leak unless the host calls sq_collectgarbage, or forever if built with NO_GARBAGE_COLLECTOR.
- Integer arithmetic is plain C++ on SQInteger with no overflow checks (32-bit unless _SQ64, which 64-bit builds define automatically). The integer fast path for '/' in SQVM::Execute (_ARITH_NOZERO) only tests for a zero divisor, so the INT_MIN / -1 guard in ARITH_OP is skipped, and that guard and the '%' one compare against the 32-bit INT_MIN even in 64-bit builds; a script dividing the minimum integer by -1 can therefore hit a hardware divide trap (read from source, not run).

## Known shortcomings

- One 2015 scriptorium fib(34) run (Squirrel 3.0.7 at 2.126 s vs Duktape 1.2.2, about 4.5x) with startup counted; slower than Lua there and in embench. Engines built with /Ox /Oy /MT /DNDEBUG, CPU model and compiler version unstated.
- Enricher: the 2.126 s vs Duktape 9.544 s come from the same bench.csv pass (lines 49-81) while an earlier pass gave 3.5x (4.114 vs 14.30 s). The _OP_DIV integer fast path checks only a zero divisor and skips the INT_MIN/-1 guard (which uses 32-bit INT_MIN even in 64-bit builds), a possible divide trap; open unanswered 2026 memory-safety issues (#315 sandbox breakout, #324-#327, #310-#312); maintenance sporadic (last merge 2026-02-28, prior commits November 2024); SQFloat is 32-bit unless SQUSEDOUBLE.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) of Squirrel 3.0.7 (SQUIRREL_VERSION in the vendored squirrel.h; the repo is now 3.2) on one recursive-fib(34) test; the author says 'Take it with a grain of salt'. bench.exe times whole processes with system() (start-up included), averages 5 launches, never checks the output, and the README table keeps the minimum over separate non-interleaved sessions (bench.csv has Squirrel at 4.114 s and 2.126 s, Duktape at 14.30, 10.29 and 9.544 s plus unlabelled runs of 9.06 to 9.71 s). Duktape 1.2.2 is much older than current Duktape 2.x releases, and PUC Lua (1.341 s in the same table) is faster than Squirrel. An older embedding-overhead benchmark (taksatou/embench, i7-2600S, Lua version not stated) shows Squirrel slower than Lua and LuaJIT on call overhead (echo 100000: 22.3 ms vs Lua 15.2 ms) but slightly faster than Lua on invert 100000 (480.0 ms vs 505.4 ms).

Lua-like dynamic language with classes and C++ binding libraries; Squirrel 3.2 reference implementation.

## Maintenance

MIT-licensed and copyable with 1.1k stars and vcpkg/Conan packages, but upstream maintenance is sporadic (last merge 2026-02-28, previous commits November 2024) and several 2026 memory-safety reports, including a sandbox-escape report, are open without a reply; the only speed evidence is one 2015 fib micro-benchmark against a 2015 Duktape.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, public-domain harness bench.cc + run.bat + tests/fib.nut + tests/fib.js + squirrel/make.bat) whose row 20 shows Squirrel 2.126 s against Duktape 9.544 s (row 32) on fib(34); not A because the CPU is given only as 'AMD A10 3.8 GHz' (no model number) and the compiler is 'VS2015 RC if possible, VS2013 elsewhere'. Same tier as the other scriptorium verdicts.
- **Verifier notes:** Numbers match README row 20 and bench.csv line 79 exactly; Squirrel and Duktape used the same /Ox /Oy /MT /DNDEBUG flags (record's 'per-engine flags not stated' corrected). Metadata confirmed on github.com: MIT (COPYRIGHT file), 1.1k stars, not archived, last commit 2026-02-28. Shortcomings to record: one 2015 fib micro-benchmark on Squirrel 3.0.7, beats only Duktape 1.2.2 and is about 1.6x slower than PUC Lua, start-up included; the record's 'Lua 5.1' label for embench was not on the page and was dropped.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.nut>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/squirrel>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/squirrel/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/squirrel/SQUIRREL3/include/squirrel.h>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/javascript/duktape>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/albertodemichelis/squirrel>
  - <https://github.com/albertodemichelis/squirrel/commits>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/taksatou/embench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/albertodemichelis/squirrel/commits>
  - <https://github.com/albertodemichelis/squirrel/issues?q=is%3Aissue+crash+OR+overflow+OR+performance+OR+vulnerability+OR+CVE>
  - <https://github.com/albertodemichelis/squirrel/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/albertodemichelis/squirrel/issues/315>
  - <https://github.com/albertodemichelis/squirrel/issues/323>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/README>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/HISTORY>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/include/squirrel.h>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/include/sqconfig.h>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqvm.cpp>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqvm.h>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqobject.h>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqopcodes.h>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqstate.cpp>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/squirrel/sqapi.cpp>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/doc/source/reference/introduction.rst>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/doc/source/reference/embedding/vm_initialization.rst>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/doc/source/reference/embedding/memory_management.rst>
  - <https://raw.githubusercontent.com/albertodemichelis/squirrel/HEAD/doc/source/reference/embedding/build_configuration.rst>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.nut>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/squirrel/make.bat>
  - <https://raw.githubusercontent.com/taksatou/embench/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/albertodemichelis/squirrel`) · [data/wave12/enrich/raw/github_com_albertodemichelis_squirrel.json](../../../data/wave12/enrich/raw/github_com_albertodemichelis_squirrel.json) (enrichment confidence 0.75)

</details>
