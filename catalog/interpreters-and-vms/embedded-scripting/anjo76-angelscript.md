# AngelScript

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Zlib` · 🟢 active

> Statically typed, C++-syntax embeddable script engine; about 4.7x Duktape 1.2.2 on 2015 fib(34), but slower than PUC Lua.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (javascript/duktape/duktape.h in the scriptorium tree); the same table lists PUC Lua 5.3.1 at 1.341 s, where this engine is slower |
| **Claimed result** | 2.039 s versus Duktape 9.544 s, about 4.7x faster than Duktape (derived from page data); slower than PUC Lua at 1.341 s (about 1.5x, derived from page data). The scriptorium table also lists an AngelScript JIT variant at 1.859 s. |
| **Workload** | Recursive fibonacci test (tests/fib.as, tests/fib.js, tests/fib.lua) run as a separate process through the repo's bench.exe ('bench 5 ...' in run.bat), wall time including process start-up averaged over 5 runs; AngelScript 2.29.2 versus Duktape 1.2.2 and Lua 5.3.1, July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | MSVC, VS2015 RC where possible and VS2013 otherwise (which one per engine is not stated); per-engine make.bat: AngelScript 2.29.2 built with cl /Ox /Oy /MT /DNDEBUG /EHsc /DAS_USE_STLNAMES=1, Duktape built with cl /Ox /Oy /MT /DNDEBUG |
| **Adoption** | 286 stars, 58 forks; packaged as vcpkg port 'angelscript' (2.38.0) and Conan Center recipe 'angelscript' (2.38.0) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/anjo76/angelscript) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

r-lyeh's Scriptorium (July 2015, MSVC VS2013/VS2015 RC with /Ox /Oy /MT /DNDEBUG, AMD A10 3.8 GHz, Windows 7 64-bit) timed whole-process runs of recursive fib(34), 5 launches averaged with the best batch kept: AngelScript 2.29.2 took 2.039 s against 9.544 s for Duktape 1.2.2 (about 4.7x, derived from page data) and 1.341 s for an unidentified PUC Lua on PATH, which is about 1.5x faster than AngelScript. AngelScript's run also paid a per-call and per-line host timeout callback that the other engines did not.

## Use it when

- A C++ application (games, tools, plug-in hosts) that wants scripts with C++-like syntax and compile-time type checking, and wants to expose existing C++ classes and functions directly without a binding generator.
- Hosts that need to suspend and resume scripts, enforce timeouts through a line callback, or run co-routines and concurrent scripts on multiple contexts.
- Replacing an old Duktape 1.x or similar slow interpreter for call- and integer-heavy script logic; Scriptorium's 2015 fib(34) run put it at 2.039 s against Duktape 1.2.2's 9.544 s.
- Shipping precompiled bytecode with the compiler stripped (AS_NO_COMPILER) to cut binary size; the docs put the engine and VM at about 300 KB and the compiler at another 350 KB (MSVC 2012, 2.30.2).

## Skip it when

- You need the fastest interpreter: PUC Lua 5.3.1 beat it in the same Scriptorium table (1.341 s vs 2.039 s), and in sashi0034/script-language-benchmark (MSVC 2022, 2026) Lua 5.x was faster on like-for-like recursive fib (599.702 vs 795.218) and Daslang beat both (266.421).
- You want a JIT: none is built in; the third-party BlindMindStudios AngelScript-JIT-Compiler targets x86/x86-64 and AngelScript 2.31.0 and looks inactive, and in Scriptorium it gained only about 9% (1.859 s vs 2.039 s).
- You need an existing script ecosystem or a widely known language for end users (Lua, JavaScript, Python); AngelScript has its own language and a small community (286 stars on the new GitHub home).
- Platforms without native calling-convention support fall back to AS_MAX_PORTABILITY, where every registered function must use the generic asIScriptGeneric wrapper, which adds work at each call and binding effort.
- Hosts that must run untrusted scripts safely: recent issues include a SEGV with enum + uint64 in bytecode (#91, fixed 2026-09-02) and a crash passing null to ?&in (#76); there is no documented sandboxing or fuzzing.

## How it is fast

Because the language is statically typed, the compiler emits typed opcodes (CMPi, ADDi, INCi and their float/double/int64 variants) on unboxed variables in the stack frame, so the VM does no run-time type dispatch or boxing for primitives, and asCByteCode::Optimize/OptimizeLocally run a peephole pass over the bytecode. Registered C++ functions and methods are called through per-ABI native calling-convention thunks (as_callfunc_x86/x64/arm/arm64/riscv64 with assembly files) instead of wrapper stubs. The interpreter uses computed-goto dispatch only with GCC 6+ or Clang (including clang-cl); native MSVC builds, like the benchmarked one, use a switch. There is no built-in JIT, only a public JIT interface (asEP_INCLUDE_JIT_INSTRUCTIONS, JIT interface v1/v2).

## Compared with alternatives

Pick AngelScript over Lua, Squirrel or mruby when you want static typing, C++-like syntax and direct registration of C++ classes with native calling conventions; on raw interpreter speed it was in the same band as Lily (2.005 s), mruby (2.098 s) and Squirrel (2.126 s) in Scriptorium and behind PUC Lua, Luau and Daslang, so pick those when throughput matters most.

## Integration

| | |
|---|---|
| **Form** | static lib (recommended by the docs) or shared lib via CMake (sdk/angelscript/projects/cmake), or source-drop of sdk/angelscript/source; add-ons (string, array, dictionary, builder) are separate source files |
| **Dependencies** | none beyond the C++ standard library and the platform thread library (CMake find_package(Threads)); assembly files for native calling conventions on x64 MSVC, ARM, ARM64, RISC-V64 and e2k |
| **Minimum toolchain** | CMake 3.10; C++ compiler with as_config.h support (MSVC, GCC, Clang, clang-cl); GCC-based builds must use -fno-strict-aliasing per the docs |
| **Platforms** | Windows, Linux, macOS, iOS, Android and consoles (as_config.h has Xbox 360, PS Vita, Switch branches); native calling conventions on x86, x86-64, ARM, ARM64, RISC-V64, MIPS, PPC and e2k; Emscripten/WebAssembly and other unsupported targets are forced into AS_MAX_PORTABILITY (generic calling convention only) |
| **Thread safety** | Multiple threads may run scripts in separate contexts on one engine; only one thread may build scripts at a time; call asPrepareMultithread before creating engines in several threads and asThreadCleanup before a thread exits; module globals, shared registered objects and many add-ons are not protected (doc_adv_multithread). AS_NO_THREADS on some platforms. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: Scriptorium's AngelScript host (angelscript/main.cpp) installs a line callback that calls timeGetTime() to enforce a 100 s timeout, and AngelScript 2.29.2 invokes it on every script function entry and every statement line cue, so the 2.039 s includes tens of millions of host callbacks the Duktape and Lua runs did not pay; the figure is pessimistic for AngelScript (size of the penalty not measured). The build was native MSVC, so the switch dispatcher, not computed gotos, was timed.
- Harness: bench.cc times whole processes (5 launches, script compilation included), keeps the best batch per engine across sessions, and never checks output; the tests' 'Should return 433494437' comment is fib(43), not fib(34). AngelScript's fib uses 32-bit int while Duktape computes with doubles.
- Harness in the secondary sashi0034 benchmark: its 'sort' row times a hand-written insertion sort in AngelScript (O(n^2), ignoring the seed) against Lua's C table.sort, and its 'dictionary' row uses string keys in the dictionary add-on against integer keys in a Lua table, so the 328.950 vs 6.175 and 20.888 vs 4.025 losses are not like-for-like; the README also says the code was generated with Codex and not reviewed.
- Memory management is reference counting plus an incremental cycle GC; registered types must implement AddRef/Release (and GC behaviours for types that can form cycles), and those must be thread safe if scripts run in several threads.

## Known shortcomings

- Slower than PUC Lua 5.3.1 on the one 2015 scriptorium fib(34) test (2.039 s vs 1.341 s); beats only Duktape 1.2.2. Engines built with /Ox /Oy /MT /DNDEBUG, CPU model and compiler version unstated; the GitHub repo is a mirror of the SVN upstream.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) of AngelScript 2.29.2 against Duktape 1.2.2 on one recursive-fib test; the author says 'Take it with a grain of salt'. Timings include process start-up and vary between logged runs (bench.csv shows Duktape from 9.06 s to 14.3 s and AngelScript 2.04 to 2.08 s). Both engines are many releases old. AngelScript loses to the main embedded-scripting incumbent: PUC Lua 5.3.1 is faster in the same table (1.341 s versus 2.039 s, about 1.5x, derived from page data), so the only baseline it beats is Duktape. Scriptorium is an archived repository; per-engine flags are in each make.bat (/Ox /Oy /MT /DNDEBUG) but the CPU model is not exact and the VS2013/VS2015 choice per engine is not stated. The 1.859 s 'angelscript-jit' row is the separate BlindMindStudios AngelScript-JIT-Compiler, not this repository. A separate April 2026 benchmark (sashi0034/script-language-benchmark, Windows, Visual Studio 17 2022 Release; the author notes the code was generated with Codex and not fully reviewed) has AngelScript faster than Lua on 7 of 16 workloads (float2string, mandelbrot, native_loop by 0.3%, particles_kinematics, queen, sha256, spectral_norm) and slower on 9 (for example dictionary 20.888 versus 4.025, sort 328.950 versus 6.175, fibonacci_recursive 795.218 versus 599.702); units are not stated.

Statically typed C++-like script language with a C++ registration API; the official GitHub repository replaced the older SVN mirror (codecat/angelscript-mirror, archived 2025-08-14).

## Maintenance

Actively maintained by its original author (2.38.0 packaged in vcpkg and Conan, 2.39.0 WIP on master, bug-fix commits to 2026-10-05, GitHub replacing the old SVN mirror); Zlib-licensed and easy to vendor, with a policy rejecting AI-generated contributions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, 525 stars) with public harness (bench.cc, run.bat, tests/fib.as, per-engine make.bat) lists AngelScript 2.039 s against Duktape 9.544 s and PUC Lua 1.341 s. Compiler is ambiguous (VS2015 RC or VS2013) and the CPU is only 'AMD A10 3.8 GHz', so it falls short of A.
- **Verifier notes:** Numbers verified on the scriptorium README and bench.csv; licence (Zlib, LICENSE.md), last commit 2026-10-05 and vcpkg/Conan packaging confirmed. Main shortcoming: slower than PUC Lua (1.341 s vs 2.039 s) and only faster than an old Duktape 1.2.2 on a 2015 single fib test; caveat corrected because per-engine flags do exist in make.bat.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/angelscript>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/javascript>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/anjo76/angelscript>
  - <https://github.com/anjo76/angelscript/commits>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/HEAD/ports/angelscript/vcpkg.json>
  - <https://raw.githubusercontent.com/conan-io/conan-center-index/HEAD/recipes/angelscript/config.yml>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/anjo76/angelscript>
  - <https://github.com/anjo76/angelscript/tree/master/sdk>
  - <https://github.com/anjo76/angelscript/commits/master>
  - <https://github.com/anjo76/angelscript/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/README.md>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/angelscript/include/angelscript.h>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/angelscript/source/as_config.h>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/angelscript/source/as_context.cpp>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/angelscript/source/as_bytecode.cpp>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/angelscript/projects/cmake/CMakeLists.txt>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/docs/doxygen/source/doc_adv_multithread.h>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/docs/doxygen/source/doc_adv_jit.h>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/docs/doxygen/source/doc_compile_lib.h>
  - <https://raw.githubusercontent.com/anjo76/angelscript/HEAD/sdk/docs/doxygen/source/doc_overview.h>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/HEAD/ports/angelscript/vcpkg.json>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.as>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/main.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/sdk/angelscript/source/as_context.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/sdk/angelscript/include/angelscript.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/AngelScript/scripts/bench.as>
  - <https://raw.githubusercontent.com/sashi0034/script-language-benchmark/HEAD/Lua/scripts/bench.lua>
  - https://www.angelcode.com/angelscript/changes.php (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/anjo76/angelscript`) · [data/wave12/enrich/raw/github_com_anjo76_angelscript.json](../../../data/wave12/enrich/raw/github_com_anjo76_angelscript.json) (enrichment confidence 0.65)

</details>
