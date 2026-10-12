# c4x86 (JIT variant of c4 by EarlGray)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-2.0` · 🔴 abandoned

> 86-line x86-32 template JIT for the c4 C subset; about 9.9x faster than stock Lua on a 2015 fib(34) run.

| | |
|---|---|
| **Beats** | Lua (LuaDist lua build, July 2015, version not stated) |
| **Claimed result** | c4-jit 0.136 s vs Lua 1.341 s on fib(34) (score line 'x09.8' relative to Lua; about 9.9x derived from page data); rank 4 of 50. The plain c4 interpreter in the same table takes 2.538 s (slower than Lua). |
| **Workload** | Recursive Fibonacci fib(34) (tests/fib.c for c4-jit, tests/fib.lua for Lua; the sources' comment says 'Should return 433494437', which is fib(43), while fib(34) is 5702887), each engine launched as a standalone executable through system() by bench.cc ('bench 5'): the wall time of five whole-process runs is averaged, so process start, parsing and JIT compilation are included; the board keeps the minimum of repeated recordings in bench.csv and gives a score relative to Lua. The c4-jit row compiles the C fib to x86 machine code with c4x86. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz, 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | Visual Studio 2015 RC where possible, Visual Studio 2013 elsewhere (README); c4jit built with 'cl /Fec4jit.exe c4x86.c /Ox /Oy /MT /DNDEBUG' (c/c4jit/make.bat); the Lua baseline is invoked as 'lua' from PATH with its version and build flags not stated (the repo vendors lua/lua-5.3.1 sources). |
| **Adoption** | 973 stars |
| **Last commit** | 2015-07-26 |
| **Links** | [repository](https://github.com/EarlGray/c4) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

In r-lyeh's archived scriptorium suite (July 2015, AMD A10 3.8 GHz, 8 GiB, Windows 7 64-bit), c4x86 built with MSVC 'cl /Ox /Oy /MT /DNDEBUG' ran recursive fib(34) in 0.136 s per whole-process launch (mean of five launches, best recording kept), against 1.341 s for a LuaDist 'lua' taken from PATH whose version and flags are not stated, about 9.9x (derived from page data). The same table lists MSVC native C at 0.074 s, LuaJIT 2.0 at 0.111 s, libtcc -run at 0.151 s and the c4 interpreter at 2.538 s; scriptorium's c/c4jit/c4x86.c is byte-identical to EarlGray/c4 HEAD.

## Use it when

- Studying how a minimal bytecode-to-native JIT works: the code generator is about 86 lines, and JIT.md maps every opcode to its x86 sequence.
- Teaching or experimenting with JIT techniques (two-pass relocation, cdecl argument reversal, 16-byte stack alignment for native calls) on 32-bit x86 Linux with gcc -m32, or Windows with 32-bit MSVC.
- Running small self-contained integer and pointer programs in the c4 subset, such as recursive fib, where it beat Lua, libtcc -run (0.151 s) and the c4 interpreter in the 2015 scriptorium table.
- As a starting point for a toy-compiler project, if GPL-2.0 is acceptable.

## Skip it when

- Embedding a scripting language in an application: there is no API, sandbox, garbage collector, error recovery or host-function registration beyond the hard-coded builtins.
- Any 64-bit-only target (x86-64 without 32-bit multilib, ARM, current macOS): it is x86-32 only and casts pointers to int throughout.
- Programs that divide integers, take the modulo of negative numbers or right-shift negative ints: the generated code for DIV, MOD and SHR is wrong in those cases (see gotchas).
- Code that needs structs, floating point, for loops, switch, the preprocessor or multiple translation units; the c4 subset has none of them.
- When raw speed is the goal: LuaJIT 2.0 (0.111 s), Terra (0.121 s) and MSVC native C (0.074 s) were faster on the same fib(34) run.

## How it is fast

It is a template (macro-expansion) JIT: each c4 opcode becomes a fixed short x86 sequence with %eax as the accumulator and operands on the machine stack via push/pop, emitted in one pass and then patched in a second pass that fills rel32 jump and call offsets from a bytecode-to-native jitmap table. That removes the interpreter's fetch/decode/dispatch loop entirely, which is why it ran about 18.7x faster than the c4 interpreter (0.136 s vs 2.538 s, derived from page data); there is no register allocation or optimization, so it stayed about 1.8x slower than MSVC /Ox native C (0.074 s) in the same table.

## Compared with alternatives

Pick it over Terra (0.121 s, LLVM-backed with Lua metaprogramming), Pawn (0.384 s, an embeddable scripting VM) or TinyVM (0.786 s) only when the goal is to read and learn from the smallest working JIT; for real embedded scripting use Pawn, Daslang or LuaJIT, and for fast native code generation use Terra.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libc plus mmap and dlfcn (libdl) on Linux and macOS; on Windows the bundled mman32.h and dlfcn32.h shims (added by r-lyeh's MSVC patch) |
| **Minimum toolchain** | Plain C; gcc -m32 (needs 32-bit multilib) on Linux; 32-bit MSVC (VS2013/VS2015, built by scriptorium with cl /Ox /Oy /MT /DNDEBUG) on Windows |
| **Platforms** | x86-32 only: Linux, OS X ('known to work on Linux (and OS X?)' per JIT.md), Windows via shims; no x86-64 or ARM backend |
| **Thread safety** | not documented; all compiler state is global and the program runs once per process |
| **Drop-in for the baseline** | no |

## Gotchas

- Integer division bug: DIV emits 'pop %ecx; xchg %eax,%ecx; idiv %ecx' with no cltd/cdq, so idiv divides %edx:%eax with whatever a previous native call or MOD left in %edx, giving wrong quotients or a divide-error crash (SIGFPE); confirmed by disassembling the emitted bytes. MOD uses 'xor %edx,%edx' (zero- instead of sign-extension), so negative dividends give wrong remainders (e.g. -7 % 3 yields 0, not -1) or a divide error (-7 % 1). tests/ has no division test; fib uses neither, so the benchmark numbers are unaffected.
- SHR emits a logical 'shr', while the c4 interpreter's '&gt;&gt;' on int is arithmetic with common compilers, so negative values shift differently under c4 and c4x86.
- Unchecked limits: fixed 256 KiB pools; native code shares one 256 KiB RWX mapping with the jitmap table in its upper half with no overflow check; LEA and ENT reject frames beyond about 31 locals or params (8-bit displacement), ADJ silently truncates to an 8-bit immediate, and mmap failure is tested against 0 instead of MAP_FAILED. JIT.md is partly stale (it describes 1-byte branch offsets and native pointers stored in text cells; the code uses rel32 and the jitmap table).
- Harness: scriptorium's bench.cc times whole-process system() launches (cmd.exe start, parse and JIT included), never checks the printed fib value or the exit code, and keeps the minimum of repeated recordings; fib.c's comment 'Should return 433494437' is fib(43), not fib(34) = 5702887. Fixed startup cost dilutes rather than inflates c4x86's ratio.

## Known shortcomings

- One 2015 fib(34) micro-benchmark from scriptorium (0.136 s vs Lua 1.341 s) as a whole-process mean of 5 launches, Lua version and flags unstated, 32-bit x86 only (c4jit flags /Ox /Oy /MT /DNDEBUG), abandoned. Toy C-subset JIT, not an embeddable scripting engine.
- Enricher: codegen bugs found by disassembly (DIV emits idiv without cdq so a stale edx gives a wrong quotient or SIGFPE; MOD zero-extends so negative dividends go wrong, -7 % 3 gives 0; SHR is logical); the fib bench uses none of these, so the numbers stand. bench.cc never checks output or exit code, times whole processes with system() and keeps the minimum; LuaJIT 2.0 (0.111 s) and Terra are faster in the same table.

## Caveats and trade-offs

Single micro-benchmark (recursive fib(34)); numbers are from July 2015 on a Windows 7 'AMD A10 3.8 GHz' (exact model not stated) with MSVC 2013/2015, so engine versions are very old; the page says 'take it with a grain of salt'; the Lua row is labelled LuaDist lua and run from PATH with version and build flags not stated; each time is the mean of five whole-process launches (startup and compile included), with no variance reported. The benchmark repo (scriptorium) is archived; EarlGray/c4 itself is not archived but has had no commits since 2015-07-26, and its last commit merges an 'MSVC support' patch from r-lyeh, the scriptorium author. c4x86 is 32-bit x86 only and not self-hosted per its README; the fork gives no benchmarks itself and the 9.9x figure comes only from the scriptorium fib test; toy-grade, included mainly for study.

86-line x86 JIT for the C-subset language of c4; 32-bit x86 only (gcc -m32), not self-hosting, a C subset with no libraries beyond a few builtins; an exercise in minimalism rather than an embedding library; GPL-2.0.

## Maintenance

Abandoned since 2015-07-26 (the last commit merges r-lyeh's MSVC support; two open issues from 2019 and 2020 have no reply); GPL-2.0, small enough to vendor for study, but it has the integer-division codegen bug above and targets only 32-bit x86.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite r-lyeh-archived/scriptorium (public-domain run.bat, bench.cc, tests/fib.c, c/c4jit/make.bat) ranks c4-jit 4th at 0.136 s vs Lua 1.341 s ('x09.8'). Compiler (VS2015 RC/VS2013) and c4jit flags (/Ox /Oy /MT /DNDEBUG) are public, but the CPU is given only as 'AMD A10 3.8 GHz' and the Lua binary's version and flags are not stated, so not A.
- **Verifier notes:** c4-jit 0.136 s vs Lua 1.341 s, rank 4 of 50, plain c4 2.538 s all match the scriptorium README; about 9.9x is derived from page data. Shortcoming: one fib micro-benchmark from 2015, Lua build unstated, whole-process timing, 32-bit x86 only, abandoned since 2015; GPL-2.0, 973 stars, fork of rswier/c4 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/c/c4jit/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/c>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/c/c4jit>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lua/lua-5.3.1>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master>
  - <https://github.com/EarlGray/c4>
  - <https://github.com/EarlGray/c4/commits>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/EarlGray/c4>
  - <https://github.com/EarlGray/c4/commits/master>
  - <https://github.com/EarlGray/c4/issues?q=is%3Aissue>
  - <https://github.com/EarlGray/c4/tree/master/tests>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/README.md>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/JIT.md>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/c4x86.c>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/c4.c>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/hello.c>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/mman32.h>
  - <https://raw.githubusercontent.com/EarlGray/c4/HEAD/dlfcn32.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/c/c4jit/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/c/c4jit/c4x86.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/c/c4jit>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/earlgray/c4`) · [data/wave12/enrich/raw/github_com_earlgray_c4.json](../../../data/wave12/enrich/raw/github_com_earlgray_c4.json) (enrichment confidence 0.8)

</details>
