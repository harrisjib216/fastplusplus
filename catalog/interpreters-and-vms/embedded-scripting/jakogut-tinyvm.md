# TinyVM (tvm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> About 1,200-line C virtual machine for an x86-style assembly language; a hand-written fib(34) ran about 1.7x faster than PUC Lua in 2015.

| | |
|---|---|
| **Beats** | Lua (LuaDist lua build, July 2015, version not stated) |
| **Claimed result** | TinyVM 0.786 s vs Lua 1.341 s on fib(34) (score line 'x01.7' relative to Lua; about 1.7x derived from page data); rank 9 of 50 |
| **Workload** | Recursive Fibonacci fib(34) (result 433494437). The scriptorium harness (bench.cc, driven by run.bat) runs each engine's standalone executable through system() ('tinyvm\tvm tests\fib.tvm', 'lua tests\fib.lua'), so each time is whole-process wall clock including startup and parsing, averaged over 5 runs; the README table keeps the lowest of the recorded averages per engine. The TinyVM row runs a hand-written assembly-like fib.tvm program (register accumulator, recursive call/ret). |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | Visual Studio 2015 RC where possible, Visual Studio 2013 elsewhere; optimisation flags not stated |
| **Adoption** | 3.3k stars |
| **Last commit** | 2018-03-22 |
| **Links** | [repository](https://github.com/jakogut/tinyvm) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

r-lyeh's Scriptorium (2015, MSVC 2013/2015 with /Ox /Oy /MT /DNDEBUG per tinyvm/make.bat, AMD A10 3.8 GHz, Windows 7 64-bit) timed whole-process runs of the 2015 TinyVM on a hand-written fib(34) assembly program: best 5-run average 0.786 s against 1.341 s for an unidentified PUC Lua on PATH timed in an earlier batch, about 1.7x (derived from page data); against Lua's other recorded batch (2.359 s) the ratio would be 3.0x.

## Use it when

- Studying or teaching interpreter construction: the whole VM (lexer, preprocessor, parser, dispatch loop) is about 1,200 lines of dependency-free C under MIT.
- A back end for a toy compiler or code generator that can emit x86-like assembly text and wants to run it portably without native code generation.
- Integer-only kernels on hosts with only a C compiler, including freestanding builds linked against the mlibc submodule.
- A minimal baseline when measuring dispatch overhead of other VM designs.

## Skip it when

- You need an embedded scripting language: there are no strings, floats, tables, closures or GC, and scripts are assembly listings.
- Running untrusted programs: memory operands, stack pushes and jump targets are not bounds-checked, and div/mod by zero or signed overflow are C undefined behaviour, so a bad program can crash or corrupt the host.
- The host must expose functions to scripts or feed programs from memory: the TODO file lists 'C interface' and 'JIT compilation' as not done, and tvm_vm_interpret only accepts a file name.
- You need a maintained project: last commit 2018-03-22, the TODO says the debugger 'doesn't work', and issue #41 (parser error handling) is open without a reply.
- Memory-tight hosts: every tvm_vm_create callocs a fixed 64 MB address space (MIN_MEMORY_SIZE) with a 2 MB stack inside it, not configurable through the API.

## How it is fast

All decoding happens once at load time: each line becomes an int opcode plus an array of int\* operand pointers (registers point into the register file, immediates and label targets point to heap-allocated ints, [n] memory operands point straight into a 64 MB arena), and labels are resolved to instruction indices through a hash table. The run loop is a plain switch in tvm_step on 32-bit ints with no type tags, boxing, bounds checks or garbage collector. The benchmark program itself is hand-written assembly that sums leaf values into a register (ebx) instead of returning values, so each fib call is only a handful of trivial instructions.

## Compared with alternatives

Pick TinyVM only as an assembly-level teaching or codegen-target VM; for embedded scripting, Pawn (a compiled C-like language with host natives; 0.719 s C core, 0.384 s asm core in the same table) or Lua/Luau give a real language and host interface, and c4-jit (0.136 s) is far faster on the same fib(34) test.

## Integration

| | |
|---|---|
| **Form** | static lib (libtvm.a) plus the tvmi command-line runner, or source-drop of libtvm/\*.c and include/tvm |
| **Dependencies** | none beyond the C standard library; optional mlibc git submodule for freestanding builds |
| **Minimum toolchain** | C99-level compiler; the GNUmakefile builds with clang -std=gnu11 -O3 -pedantic -Werror, and Scriptorium built its 2015 snapshot with MSVC 2013/2015 |
| **Platforms** | any platform with a C compiler (no architecture-specific code); the README documents only UNIX-like builds with make |
| **Thread safety** | not documented; all VM state lives in struct tvm_ctx and libtvm has no mutable globals (only const opcode and register name tables), but prn writes through printf |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: TinyVM was never timed in the same batch as Lua. Its five averages (0.786-0.815 s) are in a later block of bench.csv (lines 93-96 and 105) that has no Lua row, while the 1.341 s Lua figure comes from an earlier batch (line 65); Lua's other batch was 2.359 s. Duktape, timed in both blocks (9.544 s vs 9.06-9.71 s), suggests the machine ran at similar speed, so 1.7x is plausible but cross-batch. The Lua row runs a bare 'lua' from PATH (the repo has no lua.exe; lua/ holds only lua-5.3.1 and luajit-2.0 sources), so its version and build are unrecorded.
- Not like-for-like: fib.tvm is hand-written assembly that accumulates leaf values in ebx with no return values or frames, while fib.lua returns values and looks up the global fibR in _ENV on every call. bench.cc never checks output; fib(34) is 5702887 (the 433494437 in the fib.lua comment and in the record's workload is fib(43)), and fib.tvm's logic does yield 5702887.
- Record correction: Scriptorium's tinyvm/make.bat does state the flags, cl /Ox /Oy /MT /DNDEBUG. The timed code is a 2015 snapshot with the older API (tvm_create, tvm_interpret, tvm_run); HEAD renamed these to tvm_vm_\* and the runner to tvmi, with the same switch dispatch in tvm_step.
- [n] operands are turned into raw pointers into the 64 MB arena at parse time (value from strtoul, cast to int) with no range check, and jmp/call through a register set the instruction index to any value, so out-of-range addresses or jumps read or write outside VM memory.

## Known shortcomings

- One 2015 scriptorium fib micro-benchmark (0.786 s vs Lua 1.341 s) with whole-process timing including startup, hand-written assembly against Lua source, and Lua's other recorded average of 2.36 s; last commit 2018-03-22 (abandoned).
- Enricher: TinyVM was never timed in the same bench.csv batch as Lua (TinyVM lines 93-96 and 105, Lua 1.341 s at line 65), so the 1.7x is cross-batch (Duktape is similar in both batches, 9.544 vs 9.06-9.71 s); a hand-written assembly accumulator against Lua with returns and global lookups; make.bat gives cl /Ox /Oy /MT /DNDEBUG. No bounds checks on memory operands, stack or jumps; fixed 64 MB arena per VM; bench.cc never checks output.

## Caveats and trade-offs

Single micro-benchmark (recursive fib(34)) from July 2015 on a Windows 7 AMD A10 3.8 GHz with MSVC 2013/2015 and unstated flags; the page says 'take it with a grain of salt'. Engines are timed as separate executables (process start-up included), not embedded from C++ despite the suite's stated requirement. The Lua row is the LuaDist build (version and flags not stated); bench.csv holds two Lua averages, 2.359 s and 1.341 s, and the table keeps the faster one, while TinyVM's five averages span 0.786-0.815 s, so the 1.7x rests on Lua's better record. The comparison is hand-written VM assembly against interpreted Lua source, not a realistic scripting workload: TinyVM is an assembly-level VM with no high-level language. The TinyVM repo is not archived but its last commit is 2018-03-22 (abandoned); the benchmark repo r-lyeh-archived/scriptorium is archived. The TinyVM README makes no performance claims.

Small ANSI C VM that executes an x86-flavoured assembly language (registers, push/call/ret), not a high-level scripting language; no GC, no dynamic types.

## Maintenance

Abandoned since 2018-03-22 (last commits were scan-build and memory-leak fixes) but MIT-licensed, dependency-free and small enough to vendor; treat it as a teaching VM rather than a production scripting engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh scriptorium, public-domain harness bench.cc + run.bat + tests/fib.tvm and tests/fib.lua) lists TinyVM 0.786 s vs Lua 1.341 s on fib(34); compiler is named (VS2015 RC / VS2013) but flags are not and the CPU is given only as 'AMD A10 3.8 GHz', so it is short of A; same tier as the other scriptorium entries (Terra, Pawn, chibi-scheme).
- **Verifier notes:** Numbers match the scriptorium README and bench.csv (TinyVM 0.786 s, Lua 1.341 s, 'x01.7', rank 9 of 50); fib.tvm computes the right result, so the evidence is valid. Shortcomings: one 2015 micro-benchmark, process-level timing incl. startup, Lua's other recorded run was 2.36 s, assembly program against Lua source, abandoned since 2018. Record's 'repo is archived' and 'README could not be fetched' were wrong and are corrected in caveats.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tests>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tinyvm>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tinyvm/programs>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.tvm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://github.com/jakogut/tinyvm>
  - <https://github.com/jakogut/tinyvm/commits>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/README>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/jakogut/tinyvm>
  - <https://github.com/jakogut/tinyvm/commits/master>
  - <https://github.com/jakogut/tinyvm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/README>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/SYNTAX>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/TODO>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/GNUmakefile>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_program.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_memory.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_stack.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_htab.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_parser.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_preprocessor.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_lexer.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_tokens.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/include/tvm/tvm_file.h>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_htab.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_lexer.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_memory.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_parser.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_preprocessor.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_program.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/libtvm/tvm_file.c>
  - <https://raw.githubusercontent.com/jakogut/tinyvm/HEAD/src/tvmi.c>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tinyvm>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.tvm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/include/tvm/tvm.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/libtvm/tvm.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/GNUmakefile>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/include/tvm/tvm_memory.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tinyvm/include/tvm/tvm_stack.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/jakogut/tinyvm`) · [data/wave12/enrich/raw/github_com_jakogut_tinyvm.json](../../../data/wave12/enrich/raw/github_com_jakogut_tinyvm.json) (enrichment confidence 0.55)

</details>
