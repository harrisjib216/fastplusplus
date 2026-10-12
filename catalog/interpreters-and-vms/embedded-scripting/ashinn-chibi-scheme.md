# Chibi-Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Small embeddable R7RS Scheme bytecode VM in C; ran recursive fib(34) about 1.3x faster than PUC Lua in Scriptorium 2015.

| | |
|---|---|
| **Beats** | Lua (PUC) |
| **Claimed result** | chibi 1.009 s vs Lua 1.341 s (page shows 'x01.3' relative Lua speed). |
| **Workload** | Scriptorium: recursive Fibonacci fib(34) as a top-level/global function in each language, whole-process wall time (startup included) averaged over 5 runs via system() in bench.cc; seconds, lower is better. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB, Windows 7 64bit |
| **Compiler and flags** | Compiled on VS2015 RC if possible, VS2013 elsewhere (per page) |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/ashinn/chibi-scheme) · [benchmark](https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md) |

## Verdict

In r-lyeh's Scriptorium (July 2015, AMD A10 3.8 GHz, Windows 7 64-bit, VS2015 RC or VS2013, flags not stated), whole-process time for recursive fib(34) averaged over 5 runs was 1.009 s for chibi 0.7.3 versus 1.341 s for the PATH 'lua' binary (version unconfirmed), about 1.33x; startup is included and each figure is the best of several logged sessions.

## Use it when

- You want Scheme (hygienic syntax-rules and low-level macros, call/cc, proper tail calls, R7RS libraries) as the scripting layer of a C or C++ application.
- You need several fully isolated interpreters in one process: independent contexts have separate heaps and can run in different OS threads without locking.
- Integer- and call-heavy script code where PUC Lua 5.3-era interpreter speed is acceptable and a small, dependency-free interpreter is wanted.
- Unix-like targets, iOS, Android or Emscripten/WebAssembly builds where the standard Makefile works.

## Skip it when

- Raw script speed is the priority: on the same Scriptorium page LuaJIT (0.111 s) and even LuaJIT with the JIT off (0.521 s) and Pawn (0.719 s) beat chibi (1.009 s).
- Float-heavy numeric code: flonums are heap-allocated doubles by default (immediate flonums are an experimental, single-precision option), so each float result allocates.
- Your users expect Lua or JavaScript syntax, or your engine already has Lua bindings (sol2, LuaBridge3).
- Native Windows desktop: README-win32.md calls support limited (R7RS-small libraries only; (chibi net), (chibi process), (chibi time) not ported; make install unsupported; degraded flonum precision on MSVC).
- Text processing that indexes strings: strings are UTF-8, so string-ref and string-set! are O(n) unless built with SEXP_USE_STRING_INDEX_TABLE.

## How it is fast

Source is macro-expanded and compiled to a compact bytecode run by a switch-dispatched stack VM (vm.c), after a simplify pass that does dead-code elimination, constant folding and propagation of non-mutated let bindings. Top-level references compile to a direct read of the binding cell (SEXP_OP_GLOBAL_KNOWN_REF), fixnums are tagged immediates with inline add/compare opcodes, and memory is managed by a custom precise, non-moving mark-and-sweep GC. Nothing here is unusual for a bytecode VM; the speed edge in the benchmark is small.

## Compared with alternatives

Pick chibi over NekoVM, TinyVM or Pawn (all near it on the same Scriptorium fib table) when you want a standards-conforming Scheme with macros, continuations and isolated multi-heap embedding; pick Luau or Daslang instead when interpreter throughput matters more than the language.

## Integration

| | |
|---|---|
| **Form** | shared lib (libchibi-scheme) or static lib, plus the lib/ tree of Scheme module files needed at runtime for (scheme base); CMake example for Visual Studio |
| **Dependencies** | none (Boehm GC optional) |
| **Minimum toolchain** | C compiler with GNU make (Makefile builds with -O3 by default); Visual Studio 2017, MinGW32/64 or MSYS on Windows; minimum C standard not documented |
| **Platforms** | 32- and 64-bit Linux, FreeBSD, NetBSD, OpenBSD, DragonFlyBSD, macOS, Plan 9, iOS, Android, ARM, Emscripten; limited native Windows |
| **Thread safety** | Independent contexts with separate heaps may run concurrently in different OS threads; contexts sharing a heap (children of one parent) must stay on one thread; SRFI 18 green threads run inside a single VM; SRFI-27 is not thread-safe on Windows. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the 1.3x: tests/fib.lua defines fibR as a global, so every recursive call does a hash lookup in the globals table, while chibi compiles its top-level fibr reference to a direct cell read; the idiomatic Lua form (local function) was not measured and would narrow the gap. The table also reports the minimum over separate sessions: bench.csv holds two Lua runs (2.359 s and 1.341 s) and chibi was timed later in its own session (1.010, 1.009, 1.029 s), not interleaved with Lua.
- The Lua binary is not pinned: run.bat calls a bare 'lua' from the repo root, which has no lua.exe, so the interpreter on PATH ran (the table links LuaDist/lua); the vendored lua/lua-5.3.1 tree is not proven to be the one timed. Chibi was 0.7.3 then; the current release is 0.12.0.
- Precise GC: C code that holds Scheme objects across allocating calls must declare and protect them with sexp_gc_varN / sexp_gc_preserveN / sexp_gc_releaseN, or they can be collected underneath you. Contexts live inside the GC heap and cannot be free()d or held in a C++ smart pointer; use sexp_destroy_context.
- Continuations do not capture C frames, so call/cc across a Scheme-to-C-to-Scheme chain (load, eval, your own callbacks) may misbehave; issue #808 (2022, closed) reported segfaults when the sources were compiled as C++, so build them as C and link from C++.

## Known shortcomings

- One fib(34) test from the 2015 scriptorium table (chibi 0.7.3 at 1.009 s against Lua 5.3.1 at 1.341 s) with startup counted in the timing and no flags; slower than LuaJIT.
- Enricher: the scriptorium harness favours chibi: tests/fib.lua uses a global fibR so every Lua call does a hash lookup while chibi reads the binding cell directly (SEXP_OP_GLOBAL_KNOWN_REF); the table is a minimum over separate, non-interleaved sessions (bench.csv has Lua at 2.359 s and 1.341 s, chibi at 1.010/1.009/1.029 s), and run.bat calls a bare 'lua' from PATH so the 'PUC Lua 5.3.1' version is unproven. The margin is about parity; flonums are heap-boxed by default.

## Caveats and trade-offs

Marginal win (about 1.3x) on one recursive-Fibonacci micro-benchmark from July 2015 on Windows 7; the page says to take it with a grain of salt. Versions per the scriptorium tree: chibi-scheme 0.7.3 (scheme/chibi-scheme/VERSION) against PUC Lua 5.3.1 (lua/lua-5.3.1); current Lua 5.4 and current chibi were not measured. Timing is whole-process wall time including interpreter startup, build flags are not stated and the CPU model is not given. LuaJIT (0.111 s) and LuaJIT with the JIT off (0.521 s) are both faster than chibi on the same page.

Small R7RS Scheme designed as an extension language; VM-based threads, Unicode, hygienic macros and a module system; Scheme syntax rather than Lua-like.

## Maintenance

Actively maintained (last commit 2026-09-27, release 0.12.0) and BSD-3-Clause, so copyable; the only speed evidence is one 2015 micro-benchmark with a harness asymmetry that penalises Lua (global function lookup per call) and min-over-sessions reporting, so treat the margin over Lua as roughly parity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh scriptorium, 525 stars, archived) with public harness (bench.cc, run.bat, tests/fib.scm and tests/fib.lua) shows chibi 1.009 s vs Lua 1.341 s; compiler is only 'VS2015 RC if possible, VS2013 elsewhere', flags are unstated and the CPU is given as 'AMD A10 3.8 GHz' without a model number, so not A.
- **Verifier notes:** Row 10 (chibi 1.009 s, x01.3) and row 12 (lua 1.341 s) match the claim; both fib scripts compute fib(34) with a global recursive function, so the comparison is like for like. Metadata checked on github.com: COPYING is BSD-3-Clause text, 1.4k stars, last commit 2026-09-27. Shortcoming to record: single 2015 micro-benchmark, marginal win over an old Lua 5.3.1, slower than LuaJIT.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.scm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/chibi-scheme/VERSION>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://github.com/ashinn/chibi-scheme>
  - <https://github.com/ashinn/chibi-scheme/commits/master>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/VERSION>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/Makefile.detect>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/include/chibi/sexp.h>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/include/chibi/features.h>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/include/chibi/eval.h>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/doc/chibi.scrbl>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/vm.c>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/gc.c>
  - <https://raw.githubusercontent.com/ashinn/chibi-scheme/HEAD/README-win32.md>
  - <https://github.com/ashinn/chibi-scheme/issues?q=is%3Aissue+performance+OR+slow+OR+startup>
  - <https://github.com/ashinn/chibi-scheme/issues?q=is%3Aissue+is%3Aopen+segfault+OR+crash+OR+fuzz+OR+overflow>
  - <https://github.com/ashinn/chibi-scheme/issues/808>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.scm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/chibi-scheme/VERSION>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ashinn/chibi-scheme`) · [data/wave12/enrich/raw/github_com_ashinn_chibi_scheme.json](../../../data/wave12/enrich/raw/github_com_ashinn_chibi_scheme.json) (enrichment confidence 0.75)

</details>
