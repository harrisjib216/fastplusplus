# AngelScript JIT Compiler (BlindMindStudios)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> x86/x86-64 JIT plug-in for AngelScript 2.31.0 that turns bytecode into native code; about 1.10x over the interpreter on scriptorium fib(34).

| | |
|---|---|
| **Beats** | AngelScript bytecode interpreter (same SDK, no JIT) |
| **Claimed result** | 1.859 s with the JIT versus 2.039 s for the plain AngelScript interpreter, about 1.10x faster (derived from page data); Lua 5.x runs the same fib(34) in 1.341 s, so the JIT'd AngelScript is about 0.72x of Lua's speed (scriptorium column 'Relative Lua speed' 72%). Raw bench.csv rows: JIT 1.87916, 1.95594, 1.85891 s versus interpreter 2.04581, 2.08138, 2.03945 s. |
| **Workload** | scriptorium benchmark: recursive fib(34) script (tests/fib.as) run as a whole process, wall time averaged over 5 runs, run through an AngelScript host built with and without the JIT. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not given), 8 GiB, Windows 7 64-bit |
| **Compiler and flags** | Visual Studio 2015 RC where possible, VS2013 elsewhere; AngelScript host built with cl /Ox /Oy /MT /DNDEBUG (angelscript/make.bat); the JIT build adds /DUSE_JIT and the JIT sources. |
| **Adoption** | 254 stars, 51 forks |
| **Last commit** | 2016-06-28 |
| **Links** | [repository](https://github.com/BlindMindStudios/AngelScript-JIT-Compiler) · [benchmark](https://github.com/r-lyeh/scriptorium) |

## Verdict

Third-party scriptorium suite (r-lyeh, 2015, Windows 7 x64, AMD A10 3.8 GHz, MSVC 2015 RC or 2013 with /Ox /Oy /MT /DNDEBUG): recursive fib(34) script, whole process averaged over 5 runs, took 1.859 s with this JIT (AngelScript 2.29.2, flags 0) versus 2.039 s for the same host without it, about 1.10x (derived from page data), with a per-statement line callback active in both builds.

## Use it when

- You already ship an AngelScript 2.29-2.31 host on Windows (MSVC 2010+) or Linux (GCC 4.6.2+) and want extra speed without changing scripts or bindings.
- Hot script code is arithmetic, branches and script-to-script calls; those opcodes are compiled natively and do not fall back to the VM.
- You can live without line callbacks and context suspension in hot code and build with JIT_NO_SUSPEND; scriptorium built with flags 0 and a per-line callback and saw only about 10 percent.
- 32-bit x86 targets: angelsea, the newer AngelScript JIT, explicitly does not support 32-bit x86 and points users here.

## Skip it when

- AngelScript 2.32 or newer: the JIT reads VM internals (asCContext and asSVMRegisters offsets) and was last updated for 2.31.0 in February 2016; issue #29 (2023) asking for newer versions is unanswered.
- ARM, Apple Silicon or any non-x86 target: x86 and x86-64 only (issue #6 asking for ARM is open since 2014).
- When you need a large speed-up on a measured benchmark: the only third-party number is about 1.10x on fib(34), and the JIT's own README gives no performance figures.
- Hosts that rely on native calls with const-reference arguments returning objects on the stack on x86-64: open issue #27 (2022, AngelScript 2.35.1, MSVC) reports call_64conv clobbering an argument with the return value; open issues #17 (formatInt crash) and #23 (random crash) are also unresolved.
- Projects that need a maintained dependency: last commit 2016-06-28, no maintainer replies since.

## How it is fast

A template (one-pass) JIT: as_jit.cpp walks each function's bytecode and emits machine code per opcode through its own small assembler (virtual_asm_x86.cpp / virtual_asm_x64.cpp), removing the interpreter's dispatch loop and register-file loads and stores. Script-to-script calls are made natively (JitScriptCall) instead of returning to the VM, switch statements become native jump tables, and system calls are emitted inline per calling convention. Build flags (JIT_NO_SUSPEND, JIT_SYSCALL_NO_ERRORS, JIT_ALLOC_SIMPLE, JIT_FAST_REFCOUNT, JIT_SYSCALL_FPU_NORESET) drop suspend checks, exception checks and context bookkeeping for more speed.

## Compared with alternatives

Pick it only when you are locked into AngelScript 2.31 on x86; among siblings in the same scriptorium table, LuaJIT-class or compiled options (Terra 0.121 s, c4x86 0.136 s, Pawn 0.384 s) and even PUC Lua (1.341 s) beat its 1.859 s on fib(34), so a new project wanting a fast embedded language should look at Luau, LuaJIT Remake or Daslang instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | AngelScript SDK 2.31.0 sources (needs the internal headers, not only angelscript.h); no other libraries |
| **Minimum toolchain** | C++11 (lambdas, auto); MSVC 2010+ or GCC 4.6.2+ with -std=c++11 |
| **Platforms** | x86 and x86-64 on Windows (virtual_asm_windows.cpp) and Linux (virtual_asm_linux.cpp); no ARM |
| **Thread safety** | README: the JIT is thread-safe, one asCJITCompiler can serve several engines and several engines can compile at once (compilation is guarded by a CriticalSection). |
| **Drop-in for the baseline** | partial — scripts and bindings are unchanged and unsupported bytecodes fall back to the interpreter, but it only works with the AngelScript versions it was written for (2.31.0 in master, 2.29.x in older commits) and the speed flags change error and suspend semantics |

## Gotchas

- Harness flaw behind the 1.10x: scriptorium's angelscript/main.cpp (shared by as.exe and asjit.exe) installs ctx-&gt;SetLineCallback with a timeout check that calls timeGetTime() on every script statement, and builds the JIT with asCJITCompiler(0). With a line callback set, the vendored as_jit.cpp emits an out-of-line call to doSuspend, which calls CallLineCallback, at every asBC_SUSPEND, so both builds pay a host callback per statement; fib(34) runs fibR 18,454,929 times (derived), each executing at least two statements. This fixed cost is the same in both builds and compresses the measured ratio; the JIT's speed with JIT_NO_SUSPEND and no line callback was never measured.
- Other harness limits: whole-process wall time including engine setup, compile and JIT compile (bench.cc runs the exe 5 times via system() and divides), script output never checked; the README table shows the minimum per name across bench.csv sessions (JIT 1.879/1.956/1.859 s, interpreter 2.046/2.081/2.039 s), and the Lua reference row comes from a different session (2.359 s in session 1, 1.341 s later), so the 72 percent relative-Lua column mixes sessions.
- Measured code is the December 2014 snapshot vendored in scriptorium with AngelScript 2.29.2; 2016 fixes followed for sub-line jumps broken by multi-bytecode optimizations, suspends returning to the VM at the wrong instruction, asBC_POW using wrong registers on 64-bit, and asCALL_CDECL_OBJLAST clobbering the stack for 4+ parameters. None is on fib's path as far as the code shows.
- JIT_SYSCALL_NO_ERRORS and JIT_FAST_REFCOUNT are unsafe if any registered function sets a script exception or inspects the context (README: 'will likely result in crashes'); asBC_DIVd has a TODO about not raising AngelScript's divide-by-zero error.

## Known shortcomings

- Third-party r-lyeh/scriptorium (archived) fib(34): JIT 1.859 s vs AngelScript interpreter 2.039 s, only 1.10x; CPU given as 'AMD A10 3.8 GHz' with no model and the Visual Studio version unclear (2015 RC or 2013). The measured JIT is the December 2014 snapshot with SDK 2.29.2, before the 2016 correctness fixes (one in the multi-bytecode jump optimisations), none shown to touch fib. Scriptorium harness flaws apply (bare lua from PATH, overhead=0, output unchecked). Abandoned since 2016-06-28.
- Enricher: scriptorium's angelscript/main.cpp (shared by as.exe and asjit.exe) sets ctx-&gt;SetLineCallback, which calls timeGetTime() on every statement, and the JIT was built with asCJITCompiler(0) so the vendored as_jit.cpp runs doSuspend/CallLineCallback at every asBC_SUSPEND; fibR runs 18,454,929 times (derived), so the same fixed cost in both builds squeezes the 1.10x and the JIT_NO_SUSPEND speed was never measured. The README table is the per-name minimum over bench.csv sessions and the Lua row comes from a different session (2.359 s, then 1.341 s), so the relative-to-Lua column mixes sessions. Open issues #27 (call_64conv clobbers an argument on AS 2.35.1 with MSVC), #17, #23. Tied to AngelScript 2.31.0, x86 only.

## Caveats and trade-offs

Gain is only about 10 percent on a single recursive-call microbenchmark (fib(34)). Scriptorium harness caveats: it times the whole process including startup and script compilation (bench.cc runs the command N times through system()); overhead is hard-coded to 0 ('auto overhead = 0; // measure fib(0)'); script output is discarded, never checked; runs 1 to N-1 go to nul so only the last run prints; the README table is the third of three runs in bench.csv (JIT 1.87916, 1.95594, 1.85891 s; interpreter 2.04581, 2.08138, 2.03945 s), so run-to-run spread is about as large as half the gap; the Lua row runs a bare 'lua' from PATH, not a binary built in the repo; CPU model is a family name only ('AMD A10 3.8 GHz'), compiler is VS2015 RC or VS2013 without saying which; Scriptorium is archived (r-lyeh-archived) and dated July 2015. The measured JIT is the snapshot vendored in scriptorium's angelscript/jit folder with AngelScript SDK 2.29.2 (marker file .angelscript_2_29_2), i.e. the JIT as of its December 2014 commits; the JIT later moved to AngelScript 2.31.0 (February 2016) and received correctness fixes in 2016 ('Fix multi-bytecode optimizations breaking certain sub-line jumps', 'Fix suspends returning control to the VM at the wrong instruction', 'Fix asBC_POW instructions using wrong registers on 64-bit', 'Fix asCALL_CDECL_OBJLAST clobbering the stack for methods with 4+ parameters'); none is shown to touch fib's path, but the harness never checks output. The JIT's own README has no performance numbers. Numbers are the JIT author's code measured by a third-party suite, not by the JIT author. Last commit June 2016.

x86 and x86_64 only (Windows MSVC 2010+, Linux GCC 4.6.2+), needs C++11; written for AngelScript 2.31.0 and the JIT relies on VM internals ('native script calls ... may break on angelscript updates'), so it is tied to old SDK versions; build flags such as JIT_NO_SUSPEND, JIT_FAST_REFCOUNT and JIT_ALLOC_SIMPLE trade safety features for speed.

## Maintenance

Abandoned since June 2016 (5 open issues, 2 open pull requests, no maintainer activity) but MIT-licensed and eight source files, so it can be vendored for AngelScript 2.31.0 on x86/x86-64; for AngelScript 2.37+ on x86-64 the angelsea project (AsuMagic/angelsea, MIR-based) claims 0 to 40 percent more than this JIT in a real application.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Scriptorium (r-lyeh, 525 stars, public domain harness) is an independent third-party suite whose README results table lists angelscript-jit 1.859 s and the plain angelscript interpreter 2.039 s on fib(34); bench.cc, run.bat, tests/fib.as and angelscript/make.bat (cl /Ox /Oy /MT /DNDEBUG, JIT build adds /DUSE_JIT) are public. Not A because the CPU is only 'AMD A10 3.8 GHz' (no model) and the compiler is 'VS2015 RC if possible, VS2013 elsewhere' without saying which built AngelScript.
- **Verifier notes:** Confirmed at B: the 1.859 s vs 2.039 s figures (1.10x, derived from page data) and the 72% / 65.7% relative-Lua column are on the scriptorium README, and the bench.csv rows match the record. Caveat added that the measured JIT predates 2016 correctness fixes (one about multi-bytecode jump optimizations); if the orchestrator applies the later-fixed-bug rule strictly this would cap at C, but no fix is shown to affect fib(34). Metadata confirmed: MIT, 254 stars, 51 forks, not archived, not a fork, last commit 2016-06-28 (abandoned); benchmark_url github.com/r-lyeh/scriptorium now lives under r-lyeh-archived/scriptorium.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** re-run of the 2016 JIT against the matching AngelScript SDK; JIT_NO_SUSPEND run without a line callback
- **Pages the verifier opened:**
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/commits>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/commits/master>
  - <https://github.com/r-lyeh/scriptorium>
  - <https://github.com/r-lyeh/scriptorium/tree/master/angelscript>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/angelscript/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh/scriptorium/HEAD/tests/fib.as>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BlindMindStudios/AngelScript-JIT-Compiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/BlindMindStudios/AngelScript-JIT-Compiler/HEAD/as_jit.cpp>
  - <https://raw.githubusercontent.com/BlindMindStudios/AngelScript-JIT-Compiler/HEAD/as_jit.h>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/commits/master>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/issues?q=is%3Aissue>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/issues/27>
  - <https://github.com/BlindMindStudios/AngelScript-JIT-Compiler/issues/29>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/main.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/angelscript/jit/as_jit.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.as>
  - <https://github.com/AsuMagic/asllvm>
  - <https://github.com/AsuMagic/angelsea>
  - <https://raw.githubusercontent.com/AsuMagic/angelsea/HEAD/README.md>
  - https://angelcode.com/angelscript/resources.html (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/blindmindstudios/angelscript-jit-compiler`) · [data/wave12/enrich/raw/github_com_blindmindstudios_angelscript_jit_compiler.json](../../../data/wave12/enrich/raw/github_com_blindmindstudios_angelscript_jit_compiler.json) (enrichment confidence 0.75)

</details>
