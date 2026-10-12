# angelsea (MIR-based AngelScript JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Alpha MIR-based AngelScript JIT; author reports about 5x over the stock interpreter on call loops, 0-40% over BMS JIT.

| | |
|---|---|
| **Beats** | AngelScript interpreter (stock bytecode VM, JIT instructions off); also BlindMindStudios AngelScript JIT |
| **Claimed result** | README: 'This allows angelsea to give a \~5x performance uplift for a 1 million generic calls benchmark' (vs the AngelScript interpreter); 'Compared to the BlindMindStudios JIT, we obtain +0\~40% runtime performance in a real world application, but YMMV.' |
| **Workload** | README: a 1 million iteration loop of AngelScript calls into a registered native function using the generic calling convention (tests/scripts/abi.as benchmark_1M_calls_noarg and benchmark_1M_calls_method_arg), JIT versus the interpreter in the same engine; separately an unpublished real-world game (King Arthur's Gold dev build) versus the BlindMindStudios JIT. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the benchmark; README build instructions say cmake -DCMAKE_BUILD_TYPE=Release; JIT backend is MIR via c2mir with mir_optimization_level 2 (default); test JitConfig uses eager compilation and experimental_stack_elision. |
| **Adoption** | 31 stars; used in a King Arthur's Gold dev build per README |
| **Last commit** | 2025-09-16 |
| **Links** | [repository](https://github.com/AsuMagic/angelsea) · [benchmark](https://github.com/AsuMagic/angelsea/blob/main/README.md) |

## Verdict

First-party only: the README's \~5x is the JIT versus the stock AngelScript interpreter in the same engine (interpreter module built without JIT instructions, both without line cues) on 1-million-iteration loops calling a near-empty registered generic function, timed with nanobench in relative mode, with no CPU, compiler, flags or results published. The +0 to 40% over the BlindMindStudios JIT comes from a private King Arthur's Gold dev build with no published workload or hardware.

## Use it when

- An existing AngelScript-based game or app on 64-bit x86 (Linux gcc/clang, Windows MinGW or MSVC) whose scripts spend much time calling registered application functions, especially through asCALL_GENERIC.
- You already use the BlindMindStudios JIT on 64-bit and want a maintained-ish replacement with better coverage; the author measured +0 to 40% over it on King Arthur's Gold.
- Long-running scripted hot loops where lazy compilation keeps cold #included code out of the JIT and async compilation hides compile latency.
- As a base for ahead-of-time translation of AngelScript to C (the bytecode2c output is plain C, though the README says AOT is not yet viable).

## Skip it when

- 32-bit x86, macOS x86-64 (fails CI, issue #3) or big-endian targets; aarch64 Linux and macOS are experimental and untested on a real app.
- Engines that run AngelScript contexts on multiple threads: the README says the JIT is not thread-safe with multithreaded contexts or engines (issue #7 open).
- Hosts that rely on suspending scripts (line callbacks, timeouts), on C++ exceptions thrown by registered functions, or on inspecting the calling context from native callbacks: the default hacks ignore all three during JIT execution.
- Production builds that need stability guarantees: alpha quality, a downstream MIR fork required, async compile failures crash the app (issue #24 open), and no commits since 2025-09-16.
- Huge script functions: MIR compile cost can reach gigabytes, so functions over 25,000 bytecode bytes are skipped by default.

## How it is fast

A bytecode-to-C translator (bytecode2c) emits one C function per AngelScript function with VM field offsets baked in, and MIR's c2mir compiles that C in memory to machine code (MIR optimisation level 2). Most of the advertised win is call overhead: generated code calls registered generic functions directly with per-function pooled asCGeneric objects, has a direct native-call path with optional stack elision, and fast script call/return paths, skipping VM bookkeeping such as suspend checks and program/stack-pointer updates (the hack_ignore_\* defaults).

## Compared with alternatives

Pick angelsea over the BlindMindStudios AngelScript JIT on 64-bit x86 or aarch64 with AngelScript 2.37+, since BMS is unmaintained, x86-only and falls back to the interpreter often per this README; keep BMS for 32-bit x86. Against switching the scripting language to Luau or Daslang it is the only option here that speeds up an existing AngelScript codebase in place.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | AngelScript 2.37.0+ (asIJITCompilerV2), fmt, MIR via the asumagic/mir downstream fork; all vendored as git submodules; Catch2 and nanobench only for tests |
| **Minimum toolchain** | C++20 (cxx_std_20), CMake |
| **Platforms** | x86-64 Linux (gcc, clang) and Windows (MinGW, MSVC); aarch64 Linux and macOS experimental; no 32-bit x86, no macOS x86-64, no big-endian |
| **Thread safety** | Not thread-safe with multithreaded AngelScript contexts or engines (README, issue #7); asynchronous compilation is supported with one codegen thread at a time |
| **Drop-in for the baseline** | partial — attaches to the stock engine through asIJITCompilerV2 with three engine properties and no script changes, but requires AngelScript 2.37+, the 64-bit platforms above, line cues disabled, and accepting the default semantic hacks |

## Gotchas

- Harness note on the \~5x figure: the generic ABI benchmark (tests/abi.cpp, tests/scripts/abi.as) binds noarg to generic_noarg_hack and add_obj to generic_add_obj_hack, which write asCGeneric::returnVal and read stackPointer/currentObject directly through AngelScript's private as_generic.h header instead of the virtual asIScriptGeneric calls; with near-empty callees the loop measures pure call dispatch, the case the JIT optimises most, so ordinary generic bindings (GetArgDWord, SetReturnDWord) would show a smaller ratio. No results, CPU or compiler are committed for this or the native-ABI and brainfuck benchmarks.
- The benchmark config is not the shipped default: tests use eager compilation and experimental_stack_elision = true, while the library defaults to lazy compilation after 15,000 hits and stack elision off.
- Part of the speed comes from relaxed semantics enabled by default: hack_ignore_suspend (asBC_SUSPEND ignored, so script suspension and line-callback timeouts do not fire in JIT code), hack_ignore_exceptions (C++ exceptions from application functions are not handled on direct system calls) and hack_ignore_context_inspect (program and stack pointers not updated, breaking callees that use the debug interface; issue #26 tracks m_callingSystemFunction).
- Upstream MIR miscompiles its code (GVN load/store optimisations, integer sign-extension issue #423, jump-optimisation use-after-free issue #424); the asumagic/mir fork works around them and the config warns that MIR level 3 is known broken.

## Known shortcomings

- First-party only: about 5x is the JIT against the stock interpreter on a 1M generic-call micro benchmark (tests/abi.cpp) with no results file, CPU or flags, and the 0-40% over the BlindMindStudios JIT is a private anecdote from the author's application; alpha; stale since 2025-09-16.
- Enricher: the about 5x benchmark binds noarg and add_obj to generic_noarg_hack and generic_add_obj_hack, which poke asCGeneric fields through the private as_generic.h, with near-empty callees, so it measures pure call dispatch; the test configuration is eager compilation plus stack elision rather than the shipped defaults (lazy, 15000 hits); the default hacks ignore suspend, C++ exceptions and context inspection, so part of the speed is relaxed semantics. Open #24 (async compile failure crashes) and #7 (multithreaded contexts unsupported).

## Caveats and trade-offs

Both headline numbers are first-party and thin. The \~5x figure is JIT versus the stock AngelScript interpreter in the same engine (interpreter module built with asEP_INCLUDE_JIT_INSTRUCTIONS false) on a calls-only micro benchmark: tests/abi.cpp 'generic abi benchmark' runs tests/scripts/abi.as benchmark_1M_calls_noarg (a registered generic function that only calls gen-&gt;SetReturnDWord(123)) and benchmark_1M_calls_method_arg (SomeClass::add_obj) through nanobench (relative mode, minEpochIterations 5, warmup 1). The speedup comes from angelsea's own generic-call shortcuts (per-function pooling of asCGeneric objects, skipping VM bookkeeping), so it measures call overhead, not general script code; it is not versus the BMS JIT. The repo prints nanobench output but commits no results and states no CPU, compiler or flags; a 'native abi benchmark' and a brainfuck-interpreter benchmark (tests/megatests.cpp) also exist with no published numbers. The +0-40% versus BMS JIT figure is from a private real-world application (King Arthur's Gold dev build) with no published script, data or hardware (README: 'YMMV. If you have results to share, we're interested!'). README says alpha quality and that angelsea may have higher JIT compile times and memory use than the BMS JIT; it depends on a downstream MIR fork (upstream MIR GVN load/store optimisations miscompiled its code). Last commit 2025-09-16, just over 12 months before 2026-10-06, so maintenance is stale.

Alpha quality per README. Needs AngelScript 2.37.0+ (asIJITCompilerV2), a downstream MIR fork and fmt; x86-64 and (experimental) aarch64 only, no 32-bit x86 (use the BMS JIT there); macOS x86-64 fails CI. Not thread-safe across multithreaded contexts. Higher JIT compile time and memory use than the BMS JIT (README), mitigated by lazy compilation, async compile callback and skipping huge functions. Bytecode is translated to C, then c2mir to machine code.

## Maintenance

Stale since 2025-09-16 (alpha, 12 open issues including crash-on-async-compile-failure #24 and multithreaded-context support #7) but BSD-2-Clause, CMake-vendorable with submodules, and exercised by its author on a commercial game's dev build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Both figures are first-party README statements ('\~5x performance uplift for a 1 million generic calls benchmark' vs the stock interpreter; '+0\~40% runtime performance in a real world application' vs the BlindMindStudios JIT). The benchmark code is public (tests/abi.cpp 'generic abi benchmark' with tests/scripts/abi.as, nanobench via tests/benchmark.hpp) but no results, CPU, compiler or flags are published, and the 0-40% figure has no published workload at all.
- **Verifier notes:** Record is accurate: README wording, BSD-2-Clause, 31 stars, last commit 2025-09-16 (stale) all confirmed. Shortcomings to record: first-party only, \~5x is versus the plain interpreter on a 1M-call micro benchmark with no published results or hardware, and the 0-40% versus the BMS JIT is an unpublished private-app anecdote; alpha quality.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** published comparison against the BMS JIT with hardware; default-configuration comparison against the BMS JIT with full semantics
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/README.md>
  - <https://github.com/AsuMagic/angelsea>
  - <https://github.com/AsuMagic/angelsea/commits>
  - <https://github.com/AsuMagic/angelsea/tree/main/tests>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/scripts/abi.as>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/abi.cpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/benchmark.hpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/megatests.cpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/doc/TESTS.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/README.md>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/include/angelsea/config.hpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/include/angelsea.hpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/abi.cpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/scripts/abi.as>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/benchmark.hpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/megatests.cpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/common.hpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/common.cpp>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/doc/TESTS.md>
  - <https://github.com/AsuMagic/angelsea/issues?q=is%3Aissue>
  - <https://github.com/AsuMagic/angelsea/issues/24>
  - <https://github.com/AsuMagic/angelsea/issues/7>
  - <https://github.com/AsuMagic/angelsea/commits/main>
  - <https://raw.githubusercontent.com/asumagic/asllvm/HEAD/README.md>
  - <https://raw.githubusercontent.com/quarnster/asaot/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/asumagic/angelsea`) · [data/wave12/enrich/raw/github_com_asumagic_angelsea.json](../../../data/wave12/enrich/raw/github_com_asumagic_angelsea.json) (enrichment confidence 0.75)

</details>
