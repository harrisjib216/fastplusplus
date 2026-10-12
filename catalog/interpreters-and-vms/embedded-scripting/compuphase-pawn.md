# Pawn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0 (with a static-linking exception clause)` · 🔴 abandoned

> Tiny typeless C-like scripting language and abstract machine; 1.9x (C core) to 3.5x (x86 asm core) PUC Lua on recursive fib.

| | |
|---|---|
| **Beats** | Lua (PUC) |
| **Claimed result** | pawn-asm 0.384 s (page shows 'x03.4') and pawn 0.719 s ('x01.8') vs Lua 1.341 s (about 3.5x and 1.9x, derived from page data). |
| **Workload** | Scriptorium: recursive Fibonacci fib(34), whole-process wall time per run (bench.cc times system() calls, averaged over 5 runs, table keeps the best run), seconds, lower is better; 50 scripting-language implementations. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB, Windows 7 64bit |
| **Compiler and flags** | MSVC, VS2015 RC if possible, VS2013 elsewhere (per page); Pawn AMX built with cl /Ox /Oy /MT /DNDEBUG (pawn/make.bat), pawn-asm adds the AMX_ASM assembler core amxexec.asm assembled with 32-bit ml /coff; script compiled with pawncc -d0 -O3 (run.bat); Lua build flags not stated. |
| **Adoption** | 575 stars |
| **Last commit** | 2025-09-26 |
| **Links** | [repository](https://github.com/compuphase/pawn) · [benchmark](https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md) |

## Verdict

r-lyeh's Scriptorium (2015, MSVC /Ox, AMD A10 3.8 GHz, Windows 7) timed whole-process runs of recursive fib(34), averaging 5 runs per batch and keeping the best batch: Pawn 4.0 (build 4733, script compiled with pawncc -O3) ran in 0.384 s on the x86-32 assembler core and 0.719 s on the C core, against 1.341 s for an unidentified PUC Lua binary found on PATH (about 3.5x and 1.9x, derived from page data). Both Pawn and Lua times come from the same batch (bench.csv lines 65-70); nothing checks that the programs printed the right result.

## Use it when

- Embedding a small, sandboxed script VM in a C/C++ host where scripts are integer- and call-heavy and a C-like syntax suits the script authors.
- Microcontrollers and small devices: assembler cores exist for ARM7, Thumb-2 and ARMv6-M (Cortex-M0/M0+), and the 4.1 release documents running scripts from ROM.
- Hosts that can compile scripts ahead of time and ship only bytecode plus the abstract machine, with scripts calling into host natives.
- 32-bit x86 hosts that can link the MASM/WASM/TASM (or NASM via amxexecn.asm) assembler core, where Scriptorium's 3.5x-over-Lua figure applies.

## Skip it when

- You need a dynamic language with tables, strings as first-class values, closures or GC: Pawn is typeless 32-bit cells with fixed-size arrays (the garbage collector is an optional module).
- 64-bit hosts that need 64-bit cells or 64-bit builds: open issues #77 (64-bit Windows -C64 builds run scripts into memory errors), #85 and #86 (master does not build on Linux x86_64, unresolved amx_jit_\* symbols) were never fixed before the archive.
- You want peak speed: in the same Scriptorium table LuaJIT (0.111 s), LuaJIT -joff (0.521 s), Terra, c4-jit and libtcc all beat both Pawn rows.
- You need an actively maintained GitHub upstream: the repo was archived on 2025-09-26 and development moved to Codeberg (not checked here, blocked).

## How it is fast

Work is moved to compile time: pawncc resolves calls and variables statically and its peephole optimizer emits macro instructions (-O2) and packed opcodes with the operand folded into the opcode cell (-O3), so the VM executes fewer, typeless register-style instructions (PRI/ALT registers) with no type tags, hashing or garbage collection. Native calls are relocated to direct function pointers (SYSREQ.D). The fastest row uses the hand-written x86-32 assembler core (amxexec.asm, token threading); the portable C core in amx.c is a plain switch loop, and amxexec_gcc.c offers an indirect-threaded core via GCC labels-as-values.

## Compared with alternatives

Pick Pawn over Lua-family siblings (Luau, LuaJIT, Ravi) when the script language can be a typeless C-like dialect compiled ahead of time and the host is a 32-bit or microcontroller target that wants a tiny sandboxed VM; on desktop x86-64, Luau or LuaJIT give a full dynamic language and Daslang a typed one at higher speed, and in the same fib(34) table c4-jit (0.136 s) and Terra (0.121 s) are faster but are not small sandboxed VMs.

## Integration

| | |
|---|---|
| **Form** | source-drop (amx.c plus amxaux.c and optional extension modules compiled into the host; pawncc compiler as a separate executable; Windows DLL builds also provided) |
| **Dependencies** | none for the C core; an x86 assembler (MASM/WASM/TASM, or NASM for amxexecn.asm) for the x86 assembler core and JIT; GNU as for the ARM cores |
| **Minimum toolchain** | ANSI C compiler (CMake setup lists Microsoft, Borland, OpenWatcom and GNU); amxexec_gcc.c needs GCC or Intel C/C++ |
| **Platforms** | Win32 and Linux with 32-bit cells; x86-32 assembler core and JIT; ARM7, Thumb-2 and Cortex-M0 assembler cores; CMake forces i386 on macOS because of 64-bit issues |
| **Thread safety** | not documented; all VM state is held in the per-script AMX structure passed to amx_Exec |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws in the Scriptorium numbers: run.bat runs a bare `lua` resolved through PATH (the repo root has no lua.exe and lua/ holds only lua-5.3.1 and luajit-2.0 sources), so the PUC Lua binary, version and build behind the 1.341 s baseline are unrecorded; fib.lua declares fibR as a global, so every recursive Lua call pays a global-table lookup that Pawn's statically resolved CALL does not; bench.cc never checks program output (the scripts' comment 'Should return 433494437' is fib(43), not fib(34)).
- The 3.5x figure needs the 32-bit x86 assembler core; Scriptorium built the portable C core with MSVC, where amx.c dispatches through a switch, and that row is 1.9x. An earlier batch in bench.csv shows only 1.44x (C core) and 3.3x (asm core) against Lua 2.36 s; the table keeps the per-row minimum.
- JIT is incompatible with macro instructions, packed opcodes and overlays (amx.c turns them off under AMX_JIT), so -O3 scripts cannot use it; Scriptorium's JIT build failed (amxjitr.err) and has no row.
- Licence: Apache-2.0 with a static-linking exception that applies only to unmodified Work distributed in Object form; amxexec_gcc.c carries its own zlib-style notice, and the documentation is CC BY-SA.

## Known shortcomings

- One fib(34) test from the 2015 scriptorium table: the 3.4x over Lua needs the 32-bit x86 assembler core (the portable C core gives 1.8x), LuaJIT is faster, and the GitHub repo was archived 2025-09-26 with development moved to Codeberg (not checked, host blocked). Apache-2.0 with a static-link exception.
- Enricher: scriptorium's run.bat calls a bare 'lua' through PATH with no lua.exe in the repo, so the PUC Lua build behind the 1.341 s baseline is unknown; fib.lua uses a global fibR so every Lua call pays a table lookup, bench.cc never checks output, and an earlier bench.csv batch shows only 1.44x (C core) and 3.3x (asm core). 64-bit bugs #77, #85 and #86 still open.

## Caveats and trade-offs

Single micro-benchmark (recursive fib(34)) from 2015-2016 on Windows 7, 'take it with a grain of salt'; times are whole-process wall time including startup. The 3.4x row is pawn-asm, the hand-written x86-32 assembler core (built with 32-bit ml); the portable C core is only 1.8x faster than PUC Lua, and LuaJIT (0.111 s) and even LuaJIT -joff (0.521 s) beat both Pawn rows. Pawn is a typeless 32-bit-cell language compiled ahead of time to bytecode, against dynamically typed Lua. A pawn-jit.exe was built but has no row (amxjitr.err in the folder). Pawn version used is not stated. The GitHub repo is archived (2025-09-26) and its README says the project moved to Codeberg (codeberg.org was blocked here, so activity there is unchecked). Licence is Apache-2.0 plus a static-linking exception; documentation is CC BY-SA 3.0.

Typeless 32-bit-cell extension language with a C-like syntax compiled to P-code; the faster 'pawn-asm' row uses the assembler-optimized abstract machine; small footprint, not Lua-compatible.

## Maintenance

Archived on GitHub on 2025-09-26 after the 4.1.7152 release (2025-03-25), with development moved to Codeberg (activity there unchecked); Apache-2.0 with a static-linking exception and small enough to vendor, but 64-bit builds have open, unanswered bug reports.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh Scriptorium) with public harness (bench.cc, run.bat, tests/fib.p, pawn/make.bat) whose table rows 6 and 8 show pawn-asm 0.384 s and pawn 0.719 s against PUC Lua 1.341 s; not A because the CPU is given only as 'AMD A10 3.8 GHz' (no model) and Lua's build flags are not stated.
- **Verifier notes:** Numbers match Scriptorium rows exactly; tier B kept as independent shootout. Shortcomings: one recursive-fib test, main 3.4x figure needs the 32-bit x86 asm core (C core 1.8x), LuaJIT faster, GitHub repo archived (moved to Codeberg, unchecked).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.p>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/make.bat>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/commits>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/pawn>
  - <https://github.com/compuphase/pawn>
  - <https://github.com/compuphase/pawn/commits>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/compuphase/pawn>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/readme.md>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/history.txt>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/amx/CMakeLists.txt>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/amx/amx.c>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/amx/amx.h>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/amx/amxexec.asm>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/amx/amxexec_gcc.c>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/compiler/sc1.c>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/compiler/sc.h>
  - <https://raw.githubusercontent.com/compuphase/pawn/HEAD/compiler/CMakeLists.txt>
  - <https://github.com/compuphase/pawn/tree/master/amx>
  - <https://github.com/compuphase/pawn/issues?q=is%3Aissue>
  - <https://github.com/compuphase/pawn/issues/86>
  - <https://github.com/compuphase/pawn/issues/77>
  - <https://github.com/compuphase/pawn/releases>
  - https://codeberg.org/compuphase/pawn (EGRESS_BLOCKED)
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/pawn>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/pawn/pawn>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.p>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/main.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/cscript.cpp>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/cscript.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/amxjitr.err>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/pawn/pawn/history.txt>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/compuphase/pawn`) · [data/wave12/enrich/raw/github_com_compuphase_pawn.json](../../../data/wave12/enrich/raw/github_com_compuphase_pawn.json) (enrichment confidence 0.6)

</details>
