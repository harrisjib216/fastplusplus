# NekoVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Deprecated dynamically typed bytecode VM behind Haxe's Neko target; about 1.2x PUC Lua on one 2015 fib run, within noise.

| | |
|---|---|
| **Beats** | PUC Lua 5.3.1 (the Scriptorium repo vendors lua/lua-5.3.1; the table links LuaDist/lua; build flags not stated) |
| **Claimed result** | Neko 1.104 s vs Lua 1.341 s on fib(34) (score line 'x01.2' relative to Lua; about 1.21x, derived from page data); rank 11 of 50 vs Lua rank 12 |
| **Workload** | Recursive Fibonacci fib(34) (result 433494437). bench.cc launches each engine's command-line executable 5 times through system() and records the mean wall time per launch (process startup included); the Neko script is compiled to bytecode with nekoc before timing. The README table keeps each engine's minimum over the sessions recorded in bench.csv and scores it relative to Lua. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | Visual Studio 2015 RC where possible, Visual Studio 2013 elsewhere; Neko 2.0.0 and Boehm GC 7.2 built by neko/make.bat with cl /Ox /Oy /DNDEBUG /MT; Lua build flags not stated |
| **Adoption** | 590 stars; the VM behind the Haxe compiler's Neko target |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/HaxeFoundation/neko) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

r-lyeh's Scriptorium (July 2015, MSVC 2013/2015 with /Ox /Oy /DNDEBUG /MT, AMD A10 3.8 GHz, Windows 7 64-bit) timed whole-process runs of recursive fib(34), 5 launches averaged per batch with the best batch kept: Neko 2.0.0's interpreter (JIT off, bytecode precompiled by nekoc outside the timing) took 1.104 s against 1.341 s for an unidentified PUC Lua on PATH, about 1.21x (derived from page data). In the earlier batch that timed both, Neko was about 4% slower (2.458 s vs 2.359 s), so the margin is within run-to-run noise.

## Use it when

- You already ship Haxe code to the Neko target, or maintain a host that loads existing .n modules and .ndll primitives.
- Embedding a small dynamically typed VM with GC in a C host where scripts can be compiled ahead of time and only bytecode is shipped.
- Integer- and call-heavy scripts whose values stay within 31-bit tagged ints, the case where Scriptorium's fib(34) run put the interpreter slightly ahead of PUC Lua.

## Skip it when

- New projects: the README says 'Deprecated as of 2021-09-09 ... not actively maintained anymore'; recent commits (to 2026-09-19) are build, dependency and CI fixes only.
- You need a reliable speed-up over Lua: the only measured margin (1.104 s vs 1.341 s) flips in the other recorded batch (2.458 s vs 2.359 s), and in the same table Chibi-Scheme (1.009 s), TinyVM, Pawn, LuaJIT and Terra are faster.
- You want the JIT on a modern platform: it is x86-32 only, 'disable jit for win64, which never worked' (2.2.0 changelog), issue #301 reports a segfault when forced on on x86-64, and issue #206 (no answer) asks whether it beats the interpreter at all.
- Numeric code with integers beyond plus or minus 2^30: results are boxed into heap-allocated Int32 values (alloc_best_int), and floats are always boxed.

## How it is fast

Scripts are compiled ahead of time to a compact accumulator-plus-stack bytecode, and globals are resolved at load time to direct slot pointers (AccGlobal reads \*pc), so a global function call costs no hash lookup; integers are 31-bit tagged immediates that need no allocation. With GCC the interpreter is direct-threaded (computed goto, opcodes rewritten to label addresses at module load); MSVC builds use a plain switch. An x86-32 JIT (jit_x86.c) exists but is off unless the host calls neko_vm_jit (the stock neko executable turns it on by default), and it is compiled out on x86-64, Win64 and macOS.

## Compared with alternatives

Pick Neko only when you are tied to Haxe's Neko target or existing .n/.ndll code; for a new embedded VM, Luau or Lua give a maintained dynamic language and Chibi-Scheme (1.009 s) or Pawn (0.719 s C core) were faster in the same Scriptorium fib(34) table.

## Integration

| | |
|---|---|
| **Form** | shared lib (libneko plus the neko executable, built with CMake) or source-drop of vm/\*.c as Scriptorium did; nekoc compiler as a separate tool |
| **Dependencies** | Boehm GC (required by the VM); the standard ndlls add OpenSSL/mbed TLS, pcre2, zlib, MariaDB Connector/C, SQLite, Apache/APR and GTK+3 on Linux, each switchable off with WITH_\* CMake options |
| **Minimum toolchain** | CMake 3.10.2; Visual Studio 2010-2017 on Windows, Xcode command line tools on macOS, gcc on Linux |
| **Platforms** | Windows, macOS, Linux and BSD; x86, x86-64 and (since 2.4.0) arm64 binaries for Linux and macOS; JIT only on 32-bit x86 outside macOS and Win64 |
| **Thread safety** | one neko_vm per OS thread, chosen with neko_vm_select; threads must be created or registered through neko_thread_create/neko_thread_register so the GC sees them; nothing more is documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: Scriptorium's neko.exe is a custom host (neko/neko.c, the embedding-tutorial code) that never calls neko_vm_jit, and neko_vm_alloc sets run_jit = 0, so the 1.104 s is the MSVC switch-dispatch interpreter, not the stock neko binary (JIT on by default on 32-bit x86) nor a GCC direct-threaded build. The Lua row runs a bare 'lua' from PATH (the repo has no lua.exe; lua/ holds only lua-5.3.1 and luajit-2.0 sources), so the baseline binary and build are unrecorded.
- Harness: bench.cc never checks program output, and the 'Should return 433494437' comment in fib.lua is fib(43); fib(34) is 5702887. The Neko and Lua scripts both call a global function, but Neko resolves globals to slots at load time while Lua's fibR does a hash lookup in _ENV per call, which favours Neko on this test.
- Integers are 31-bit tagged; arithmetic that leaves that range allocates a boxed Int32 through the GC, and wider results wrap as C int arithmetic.
- Licence is mixed: VM and runtime libraries are MIT, but nekoc and nekoml are GPL-2.0, mysql.ndll links the LGPL MariaDB Connector/C, and Boehm GC carries its own notice; the LICENSE file bundles all of these.

## Known shortcomings

- The scriptorium win sits inside run-to-run noise: in bench.csv's other session Neko took 2.458 s against Lua 2.359 s, so Neko was slower; baseline Lua 5.3.1, timing includes process startup, and Neko has been deprecated upstream since 2021-09-09.
- Enricher: scriptorium's neko.exe is a custom embedding host (neko/neko.c) that never calls neko_vm_jit and sets run_jit=0, so the 1.104 s is the MSVC switch interpreter rather than the stock neko binary (x86-32 JIT on by default); the Lua binary is a bare 'lua' from PATH with no lua.exe in the repo. The 1.21x margin flips in the other batch (2.458 vs 2.359 s); fib(34) is 5702887 (the record's 433494437 is fib(43)); bench.cc never checks output. JIT broken on Win64 and x86-64 (#301); nekoc and nekoml are GPL-2.0, mysql.ndll LGPL.

## Caveats and trade-offs

Single micro-benchmark (recursive fib(34)) from July 2015 on a Windows 7 AMD A10 3.8 GHz with MSVC 2013/2015 and Neko 2.0.0 vs Lua 5.3.1, so both engines are very old versions; the page says 'take it with a grain of salt'. Each figure is the mean of 5 process launches (startup included), and the table keeps the minimum over recorded sessions: bench.csv holds two sessions for Neko and Lua, and in the other one Neko took 2.458 s vs Lua 2.359 s (Neko about 4% slower), so the roughly 20% margin is not stable across runs. Lua build flags are not stated. The benchmark repo is hosted under the r-lyeh-archived account. The Neko README says 'Deprecated as of 2021-09-09 ... not actively maintained anymore' (compatibility fixes only), although commits continue (last 2026-09-19). Neko links Boehm GC (its LICENSE file also reproduces the GC licence).

Dynamically typed bytecode VM (target of Haxe and other compilers) with a C embedding API and Boehm GC; LICENSE file bundles third-party licences (Boehm GC and others) next to the MIT text.

## Maintenance

Deprecated upstream since 2021 (2.4.0 in 2024 and 2.4.1 in 2025 are maintenance releases, commits to 2026-09-19 update BoehmGC, mbed TLS and CI); the MIT VM is usable and embeddable, but expect no new features or answers on issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh Scriptorium, 525 stars) with public harness (bench.cc, run.bat, tests/fib.neko, tests/fib.lua, neko/make.bat building Neko 2.0.0 with /Ox /Oy /DNDEBUG /MT) whose row 11 shows nekovm 1.104 s against PUC Lua 1.341 s (row 12) on fib(34); not A because the CPU is given only as 'AMD A10 3.8 GHz' (no model number) and the Lua build flags are not stated.
- **Verifier notes:** Numbers match the Scriptorium README table exactly (1.104 s vs 1.341 s, 'x01.2', rank 11 vs 12). Main shortcoming: the win is within run-to-run noise; bench.csv's other recorded session has Neko slower than Lua (2.458 s vs 2.359 s), and the project itself is deprecated upstream. Kept at B for consistency with the chibi-scheme, Pawn and Terra Scriptorium verdicts.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.neko>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/neko/make.bat>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tests>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/neko>
  - <https://github.com/HaxeFoundation/neko>
  - <https://github.com/HaxeFoundation/neko/commits/master>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/HaxeFoundation/neko>
  - <https://github.com/HaxeFoundation/neko/commits/master>
  - <https://github.com/HaxeFoundation/neko/tree/master/vm>
  - <https://github.com/HaxeFoundation/neko/issues?q=is%3Aissue+jit+OR+performance+OR+crash>
  - <https://github.com/HaxeFoundation/neko/issues/206>
  - <https://github.com/HaxeFoundation/neko/issues/301>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/interp.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/main.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/module.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/neko.h.in>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/neko_vm.h>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/vm.h>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/opcodes.h>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/jit_x86.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/alloc.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/others.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/threads.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/neko/HEAD/vm/load.c>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/neko>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.neko>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/neko/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/neko/neko.c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/haxefoundation/neko`) · [data/wave12/enrich/raw/github_com_haxefoundation_neko.json](../../../data/wave12/enrich/raw/github_com_haxefoundation_neko.json) (enrichment confidence 0.6)

</details>
