# LuaAOT (lua-aot-5.4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟡 stale

> Patched Lua 5.4.3 plus a bytecode-to-C compiler (luaot); compiled modules ran 1.2x to 2.6x faster than the stock interpreter.

| | |
|---|---|
| **Beats** | Lua 5.4.3 interpreter (the stock interpreter the fork is based on) |
| **Claimed result** | statistics/times-slow.txt (20 runs, Lua 5.4.3 baseline), 'cor' column (the paper's LuaAOT): 1.21x-2.64x over PUC Lua; the 'aot' column (earlier variant) gives 1.22x-2.25x (mandelbrot 2.25x). SBLP 2021 paper reports 20-60% (snippet only). LuaJIT -joff is faster on 4 of 7 benchmarks (derived from page data). |
| **Workload** | Seven Computer Language Benchmarks Game programs in experiments/ (binarytrees, fannkuch, fasta, knucleotide, mandelbrot, nbody, spectralnorm) compiled ahead of time to C with luaot and run through experiments/main.lua, versus the same scripts on the stock Lua 5.4.3 interpreter and LuaJIT; 20 runs each, wall-clock time. |
| **Metric** | throughput |
| **Compiler and flags** | Interpreter built with the Lua 5.4.3 Makefile (gcc -std=gnu99 -O2, make guess); benchmark modules compiled with gcc -shared -fPIC -O2 -g (scripts/compile). gcc version not stated. |
| **Adoption** | 165 stars |
| **Last commit** | 2023-12-06 |
| **Links** | [repository](https://github.com/hugomg/lua-aot-5.4) · [benchmark](https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/statistics/times-slow.txt) |

## Verdict

The repo's statistics/times-slow.txt has 20 wall-clock runs per cell (/usr/bin/time -p on the whole process, output to /dev/null) on an unnamed x86-64 CPU at about 3.06 GHz (perf counters), with gcc -O2 and a gcc version not stated. Against the stock Lua 5.4.3 interpreter, the paper's LuaAOT variant took 1.21x (knucleotide) to 2.64x (mandelbrot) less time; I recomputed all seven means from the raw file and they match the record. The SBLP 2021 paper reports 20% to 60% shorter run times (abstract seen as a search snippet only).

## Use it when

- You embed Lua 5.4 in a C or C++ host and need its semantics (integers, bitwise operators, goto, to-be-closed variables), which rules out LuaJIT's 5.1 dialect.
- Platforms that forbid runtime code generation (W^X or app-store rules) but allow shipping native code built ahead of time.
- Numeric, loop-heavy scripts: fannkuch, mandelbrot and spectralnorm ran 2.0x to 2.6x faster than Lua 5.4.3.
- Shipping a fixed set of Lua modules or a single-file executable (luaot -e) where a build step per script is acceptable.

## Skip it when

- When LuaJIT is allowed: it was 2.4x to 31x faster than Lua on the same runs. Even LuaJIT with the JIT off (-joff) beat LuaAOT on 4 of 7 programs (binarytrees 1.91 s vs 2.68 s, fasta 3.02 vs 3.84, knucleotide 2.28 vs 3.44, nbody 8.92 vs 12.14; derived from page data).
- Allocation-, string- or table-heavy code, where the gain was only 1.21x to 1.32x (binarytrees, fasta, knucleotide).
- Large code bases: issue #13 reports Teal (11,012 Lua lines) becoming about 600,000 lines of C that took 28.7 s and 6.7 GB peak memory to compile, and issue #11 reports about 200 KB extra memory per compiled module versus 5-15 KB for the plain one.
- Projects that need current Lua: the base is 5.4.3, without the 5.4.4+ bug fixes or 5.5. There has been no commit since 2023-12-06, and there is no test suite (issue #3 open).
- Builds that would use the switch-based trampoline compiler (luaot-trampoline): it gave only 0.99x to 1.48x over Lua 5.4.3 (derived from page data).

## How it is fast

The compiler partially evaluates the reference interpreter: each Lua function becomes one C function, each bytecode becomes a labelled block holding that opcode's interpreter code with the instruction word baked in as a constant, and Lua jumps become C gotos. This removes fetch-and-dispatch, and gcc can constant-fold the immediate operands and drop dead branches. A patched luaV_execute runs a trampoline loop: compiled functions return the next CallInfo instead of recursing, which keeps coroutines, tail calls and debug hooks working.

## Compared with alternatives

Pick LuaAOT over LuaJIT only when you must stay on Lua 5.4 semantics or cannot JIT and your hot code is numeric loops; otherwise LuaJIT, even with its JIT off, is as fast or faster. It is the Lua counterpart of Lightstorm (mruby AOT, about 30% less time): the same no-dispatch compile-the-interpreter idea, with larger gains here on numeric code.

## Integration

| | |
|---|---|
| **Form** | Modified Lua 5.4.3 (static liblua.a and lua binary) plus the luaot compiler; generated C is built as a shared module or an executable |
| **Dependencies** | none beyond a C compiler and libc/libm (dlopen for .so modules) |
| **Minimum toolchain** | C99 (src/Makefile uses gcc -std=gnu99 -O2); compile generated modules with at least -O2 per the README |
| **Platforms** | Whatever Lua 5.4.3's 'make guess' supports (Linux, macOS, other POSIX); the experiments ran on Linux x86-64 |
| **Thread safety** | Same as Lua (one lua_State per thread). A module's luaopen_ function mutates a file-static counter, so it is not safe to call concurrently or more than once per process. |
| **Drop-in for the baseline** | partial — same language and public C API as Lua 5.4.3, but the host must link the LuaAOT-patched interpreter (Proto gains an aot_implementation field and internal APIs are exported), and compiled modules load only into that build |

## Gotchas

- Bug in the generated loader (src/luaot_footer.c): bind_magic takes function pointers from LUAOT_FUNCTIONS[next_id++], where next_id is a file-static counter that is never reset. Calling luaopen_&lt;module&gt; a second time in the same process (a second lua_State, or require after clearing package.loaded) starts past the end of the array. The main chunk silently falls back to the interpreter on the trailing NULL, and nested functions get out-of-bounds pointers, which is undefined behaviour and a likely crash. Multi-state C++ hosts are affected; the single-process benchmarks are not.
- The module embeds the original Lua source and re-parses it with luaL_loadbuffer at load time, then binds compiled functions by traversal order. Load errors call exit(1) instead of raising a Lua error, the source ships readable inside the .so, and issue #19 reports that files starting with a shebang fail to run.
- Undated benchmark data: statistics/times-slow.txt has seven columns (lua, lsw, aot, cor, trm, jof, jit), but the current scripts/bench-run.lua only produces five. Per statistics/plot.r, the paper's 'LuaAOT' is the 'cor' column, while 'aot' (an earlier variant) gives 1.22x to 2.25x, not 2.64x, on mandelbrot.
- LuaJIT rows ran slightly different source on 3 of 7 programs (binarytrees_jit, fasta_jit and mandelbrot_jit use 2^, the bit library and math.floor in place of 5.4 operators). Use only knucleotide and nbody when comparing LuaJIT's interpreter with LuaAOT on identical code.

## Known shortcomings

- Upgraded C to B: the repo's statistics/times-slow.txt gives 1.21x-2.64x over Lua 5.4.3 (20 runs) and the peer-reviewed SBLP 2021 paper reports 20-60% (snippet only, PUC-Rio blocked). No CPU or gcc version, far behind LuaJIT, stale since 2023-12-06.
- Enricher: the record's numbers are the 'cor' column of statistics/times-slow.txt (the paper's LuaAOT); the 'aot' column is an earlier variant (mandelbrot 2.25x not 2.64x). LuaJIT -joff beats LuaAOT on 4 of 7 benchmarks and ran ported _jit.lua sources on 3 of 7. Bug in src/luaot_footer.c: static next_id is never reset, so a second luaopen_ in one process reads past LUAOT_FUNCTIONS (out-of-bounds function pointers) in multi-state hosts; a module load error calls exit(1).

## Caveats and trade-offs

CPU model and gcc version not stated (perf counters in statistics/perf-slow.txt only show about 3.06 GHz); the timing file is undated and comes from the paper's experiments. The paper itself (ACM DL, inf.puc-rio.br preprint) is blocked here, so its numbers are snippet only. Gains are uneven: 1.21x to 1.5x on four of seven benchmarks, about 2x to 2.6x only on fannkuch, mandelbrot and spectralnorm; LuaJIT is far faster on every benchmark. Based on Lua 5.4.3 (older than 5.4.7/5.5), every module must be compiled to C with a C compiler at build time, and the repo has had no commits since 2023-12-06.

Modified Lua 5.4.3 with an extra luaot compiler that translates Lua bytecode to C (jumps become gotos, no bytecode dispatch); keeps full Lua 5.4 semantics and is embeddable from C/C++, but compiled modules must be built per script.

## Maintenance

Stale research artefact from PUC-Rio (last commit 2023-12-06, 91 commits, 165 stars), MIT-licensed and small (luaot.c plus its goto-mode opcode template is about 1,600 lines of C), so it can be vendored. You would own rebasing onto a newer Lua 5.4.x and fixing the luaopen re-entry bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the repo's statistics/times-slow.txt holds 20 timed runs per benchmark of LuaAOT, the stock Lua 5.4.3 interpreter and LuaJIT (experiments/\*.lua, scripts/compile with gcc -O2 -g), and the peer-reviewed SBLP 2021 paper 'A Surprisingly Simple Lua Compiler' (Gualandi and Ierusalimschy; extended version in Journal of Computer Languages 2022) reports a 20% to 60% running-time reduction (abstract seen as search snippet only). Not A: no CPU model or gcc version in the repo, and the paper could not be opened.
- **Verifier notes:** README quote verified and backed by raw timing data in statistics/times-slow.txt (LuaAOT 1.21x to 2.64x faster than Lua 5.4.3), plus a peer-reviewed SBLP 2021 paper whose abstract (snippet only) reports 20% to 60% lower running times; upgraded to B on that basis. If snippet-only paper evidence is not accepted, the repo data alone supports C. Licence MIT confirmed from LICENSE.txt (PUC-Rio plus Hugo Musso Gualandi); last commit 2023-12-06, stale. Shortcomings: no CPU/compiler version, uneven gains, far behind LuaJIT, old Lua 5.4.3 base, unmaintained since 2023.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/README.md>
  - <https://github.com/hugomg/lua-aot-5.4>
  - <https://github.com/hugomg/lua-aot-5.4/commits>
  - <https://github.com/hugomg/lua-aot-5.4/tree/master/statistics>
  - <https://github.com/hugomg/lua-aot-5.4/tree/master/experiments>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/statistics/times-slow.txt>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/statistics/perf-slow.txt>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/statistics/plot.r>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/scripts/run>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/scripts/compile>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/experiments/main.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/experiments/mandelbrot.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/src/Makefile>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/src/lua.h>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/master/LICENSE.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/README.md>
  - <https://github.com/hugomg/lua-aot-5.4>
  - <https://github.com/hugomg/lua-aot-5.4/commits/master>
  - <https://github.com/hugomg/lua-aot-5.4/tree/master/experiments>
  - <https://github.com/hugomg/lua-aot-5.4/tree/master/scripts>
  - <https://github.com/hugomg/lua-aot-5.4/tree/master/statistics>
  - <https://github.com/hugomg/lua-aot-5.4/issues?q=is%3Aissue>
  - <https://github.com/hugomg/lua-aot-5.4/issues/5>
  - <https://github.com/hugomg/lua-aot-5.4/issues/9>
  - <https://github.com/hugomg/lua-aot-5.4/issues/11>
  - <https://github.com/hugomg/lua-aot-5.4/issues/13>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/statistics/times-slow.txt>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/statistics/perf-slow.txt>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/statistics/plot.r>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/run>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/compile>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/bench-all>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/bench-run.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/bench-sizes>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/bench-tocsv.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/bench-parse-perf.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/scripts/0002-Changes-to-the-core-Lua-interpreter.patch>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/main.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/mandelbrot.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/mandelbrot_jit.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/binarytrees.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/binarytrees_jit.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/fasta.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/fasta_jit.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/experiments/fannkuch.lua>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/luaot.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/luaot_gotos.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/luaot_switches.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/luaot_header.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/luaot_footer.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/trampoline_footer.c>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/lobject.h>
  - <https://raw.githubusercontent.com/hugomg/lua-aot-5.4/HEAD/src/lvm.c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/hugomg/lua-aot-5.4`) · [data/wave12/enrich/raw/github_com_hugomg_lua_aot_5_4.json](../../../data/wave12/enrich/raw/github_com_hugomg_lua_aot_5_4.json) (enrichment confidence 0.75)

</details>
