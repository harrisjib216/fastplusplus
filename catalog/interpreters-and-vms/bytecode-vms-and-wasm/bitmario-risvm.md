# RISVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Tiny untyped 32-bit register bytecode VM in about 1000 lines of C++; one hand-written assembly benchmark ran 1.45x faster than Lua 5.3.

| | |
|---|---|
| **Beats** | Lua 5.3 and CPython 3.6.6 |
| **Claimed result** | x86-64: RISVM 4.97s vs Lua 5.3 7.23s (about 1.45x faster, derived from page data) and Python 3.6.6 35.95s (about 7.2x faster, derived); C++ g++ 7.3 -O3 1.80s, node 8.10 2.18s. |
| **Workload** | examples/asm/primes.asm (prime sieve written in RISVM assembly) run on the VM versus equivalent programs in C++, Node, Lua and Python. |
| **Metric** | throughput |
| **Hardware** | x86-64 (CPU model not stated) |
| **Compiler and flags** | C++ row: G++ 7.3.0 -O3; RISVM VM build per current repo Makefile: g++ -std=c++11 -Wall -O2 -march=native -fno-strict-aliasing -g (not stated whether this Makefile was used for the timing) |
| **Adoption** | 31 stars |
| **Last commit** | 2018-12-25 |
| **Links** | [repository](https://github.com/bitmario/RISVM) · [benchmark](https://raw.githubusercontent.com/bitmario/RISVM/HEAD/README.md) |

## Verdict

A single first-party run (2018) of a trial-division prime finder below 100,000, hand-written in RISVM assembly, took 4.97 s against 7.23 s for an equivalent Lua 5.3 script (about 1.45x faster) and 35.95 s for module-level Python 3.6.6 (about 7.2x), but 2.8x slower than C++ (G++ 7.3 -O3, 1.80 s) and 2.3x slower than node 8.10 (derived from page data). The machine is an unnamed x86-64 system, and the VM build flags behind the timing are not stated.

## Use it when

- Microcontroller or embedded targets (the README mentions Xtensa and AVR) where you want a tiny, dependency-free VM to run small downloadable programs written in assembly.
- As a teaching or starting codebase for a register VM: about 1000 lines, MIT-licensed, with Catch2 unit tests for the system, register, stack, memory, arithmetic, conversion and branching instructions.
- Integer-heavy control logic you are willing to hand-write in assembly, where a dynamically typed scripting language's per-operation type checks would dominate.
- Hosts that need an instruction budget: run(maxInstr) returns VM_PAUSED after N instructions so the host can time-slice scripts.

## Skip it when

- Running untrusted bytecode: division or modulo by zero is not checked (a host-process SIGFPE on x86), and OP_READS passes a pointer into VM memory to getline(), which may realloc it if the input line is longer than the buffer.
- Programs larger than 64 KB or needing a heap: addresses, program length and stack size are 16-bit, and there is no allocator or garbage collection.
- Anything that needs a compiler toolchain or portability guarantees: use a WebAssembly interpreter, which runs code compiled from C, C++ or Rust; RISVM has only its assembler and an undocumented 2018 'reduced C' prototype.
- Big-endian targets or compilers other than GCC and Clang (the decoder uses GNU statement expressions and assumes little-endian).
- Maintained production use: the last commit was 2018-12-25 and the one open issue (#10, arrays, 2019) has no answer.

## How it is fast

There is no special dispatch technique: run() is a while loop over a switch on one-byte opcodes, with operands read byte by byte from unaligned memory and the instruction pointer kept in the register array. Its edge over Lua and CPython comes from doing far less work per instruction: registers are raw uint32 values with no type tags, boxing or overflow checks, arithmetic is native 32-bit unsigned, and the benchmark program is hand-written register assembly (five instructions per inner-loop iteration) rather than compiled from a high-level language.

## Compared with alternatives

Pick RISVM over wasm3, WAMR or Wasmi only when you want a minimal, hackable custom ISA (about 1000 lines) and will write the bytecode yourself; wasm3 and WAMR run code compiled by standard toolchains, sandbox memory accesses, are maintained, and have independent benchmarks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the VM (C standard library stdio); Python 3 for the assembler |
| **Minimum toolchain** | C++11 (Makefile -std=c++11) with GNU statement expressions, so GCC or Clang |
| **Platforms** | any little-endian platform with GCC or Clang per the README; numbers given only for an unnamed x86-64 machine, with Xtensa and AVR mentioned qualitatively |
| **Thread safety** | not documented; all state lives in the VM object (registers, memory, interrupt callback), so separate instances share nothing in the code read, and I/O goes straight to the process's stdio. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 4.97 s figure dates from the 2018-10-15 commit 'add performance docs and new lua benchmark', before bounds and stack-overflow checks were added on 2018-10-19. The checks are now on by default (compile with VM_DISABLE_CHECKS to remove them) and add branches to every instruction, and the current build has not been re-timed.
- Harness asymmetry: the RISVM and C++ versions use 32-bit unsigned modulo, while Lua 5.3 uses 64-bit signed integers (lua_Integer is long long by default, and luaV_mod adds zero/-1 and sign-correction checks). The loop does about 455 million modulo operations (derived), and on Intel Skylake-class cores 64-bit DIV takes 35-88 cycles against 26 for 32-bit (search snippets), so part of the 1.45x over Lua may come from operand width rather than the VM. The CPU is not named, so this is untested.
- The baselines' 'globals' handicap is uneven. In Lua, num and i are for-loop locals and only isPrime is global (written about 100,000 times against 455 million inner iterations), so it is negligible. The Python version runs at module level, so num and i are looked up by name on every iteration, which inflates the 7.2x.
- Printing about 9,600 primes is negligible next to the 455 million trial divisions (derived), so the benchmark measures one modulo-compare-branch loop: about 10.9 ns per iteration for RISVM vs 15.9 ns for Lua and 4.0 ns for C++ (derived from page data).

## Known shortcomings

- Toy primes benchmark with Lua and Python baselines that use globals, no CPU named, abandoned 2018-12-25. Off-baseline: a bytecode VM compared against Lua and Python rather than a wasm runtime.
- Enricher: the 4.97 s comes from the 2018-10-15 commit, before the 2018-10-19 bounds checks (now on by default, never re-timed); RISVM and the C++ reference use 32-bit unsigned modulo while Lua 5.3 uses 64-bit signed luaV_mod over about 455M divisions, so some of the 1.45x may be division width. No division-by-zero check (SIGFPE), OP_READS calls getline() on a pointer into VM memory (realloc undefined behaviour), 16-bit progLen and memSize truncation.

## Caveats and trade-offs

Toy-scale: one microbenchmark (trial-division primes below 100000, printing each prime) hand-written in RISVM register assembly versus idiomatic scripts, so it compares a low-level untyped 32-bit register bytecode with dynamically typed language VMs. The Lua 5.3 and Python 3.6.6 versions (in examples/asm/primes.asm comments) use global variables (Lua isPrime is global; Python runs at module level), which handicaps both baselines; Python loops to 100000 inclusive. Every run prints about 9,600 lines, so output cost is part of the timing. Versions (node 8.10, Python 3.6.6, Lua 5.3) are old and the machine is not named; the README itself says RISVM is about 3x slower than native and loses to node. Not compared with wasm3, WAMR, LuaJIT or any wasm runtime. The README warns there were no stack or bounds checks at the time (later commits added them).

About 1000 lines of C++ plus a Python 3 assembler; 16 registers, 70 instructions, no overflow or bounds checking, little-endian only. README says it is about 3x slower than native on x86-64 and up to 10x slower on Xtensa and AVR.

## Maintenance

Abandoned since 2018-12-25 (31 stars, the README itself says work in progress with no compatibility promises), but MIT-licensed and small enough to vendor and harden yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Performance table; the benchmark programs for every language are in examples/asm/primes.asm comments, and the C++ row states G++ 7.3.0 -O3, but the CPU model is not named and the VM build used for the timing is not stated, so C.
- **Verifier notes:** Numbers match the README and primes.asm exactly (RISVM 4.97s, Lua 5.3 7.23s, Python 3.6.6 35.95s; 1.45x and 7.2x derived correctly). Shortcomings: single toy benchmark, Lua and Python baselines written with globals, no CPU named, VM build flags not tied to the timing, abandoned since 2018-12-25. Metadata verified: MIT, 31 stars, 4 forks, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/examples/asm/primes.asm>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/LICENSE>
  - <https://github.com/bitmario/RISVM>
  - <https://github.com/bitmario/RISVM/commits/master>
  - <https://github.com/bitmario/RISVM/tree/master/examples>
- **Sources the enricher read:**
  - <https://github.com/bitmario/RISVM>
  - <https://github.com/bitmario/RISVM/commits/master>
  - <https://github.com/bitmario/RISVM/issues?q=is%3Aissue>
  - <https://github.com/bitmario/RISVM/tree/master/rc>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/examples/asm/primes.asm>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/src/vm.cpp>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/src/vm.h>
  - <https://raw.githubusercontent.com/bitmario/RISVM/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/lua/lua/v5.3.6/lvm.c>
  - <https://raw.githubusercontent.com/lua/lua/v5.3.6/luaconf.h>
  - WebSearch: 'Skylake DIV r64 latency vs DIV r32 latency' (snippets citing https://arxiv.org/pdf/1902.01961 and an LKML thread; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bitmario/risvm`) · [data/wave12/enrich/raw/github_com_bitmario_risvm.json](../../../data/wave12/enrich/raw/github_com_bitmario_risvm.json) (enrichment confidence 0.7)

</details>
