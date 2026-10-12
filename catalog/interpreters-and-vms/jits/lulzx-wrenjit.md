# WrenJIT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Tracing JIT for the Wren scripting language on SLJIT; beats LuaJIT on a few microkernels but loses on 9 of 10 Benchmarks Game ports.

| | |
|---|---|
| **Beats** | LuaJIT 2.1 with JIT on (docs/index.html report names LuaJIT 2.1.1785763465; build flags not stated); the report also shows a LuaJIT -joff column |
| **Claimed result** | README microbenchmark table, WrenJIT vs LuaJIT time (lower is better): sum 0.641 ms vs 1.092 ms (0.59x), range for 0.074 ms vs 0.584 ms (0.13x), fib(35) 39.4 ms vs 51.9 ms (0.76x), tak 2.224 ms vs 6.361 ms (0.35x), ack(3,7) 0.024 ms vs 1.066 ms (0.02x), mutual recursion 0.098 ms vs 0.321 ms (0.31x), deep recursion 0.625 ms vs 6.724 ms (0.09x), binary trees 8.807 ms vs 19.8 ms (0.45x), method call 0.087 ms vs 0.448 ms (0.19x). Five of these rows do not time equivalent work: range for and method call are computed in closed form by optimizer passes 15-16 (irOptFastForwardRangeSum, irOptFastForwardToggleCounter), ack is replaced by the closed form 2^(n+3)-3 for m=3, mutual recursion by a parity test, and deep recursion is collapsed into a loop, while LuaJIT runs the real loops and calls; binary trees run a hand-written C tree builder and walker. Rows with comparable work: sum 0.59x, fib 0.76x, tak 0.35x. The author's own published report (docs/index.html, ten Benchmarks Game ports) says WrenJIT is faster than LuaJIT on 1 of 10: pidigits 66.4 ms vs 119.8 ms (0.55x); slower on the rest, e.g. nbody 848.4 ms vs 31.8 ms (26.69x slower), regex-redux 19.06x, k-nucleotide 5.68x, fasta 5.25x, binary-trees 4.25x, fannkuch-redux 3.63x, mandelbrot 3.15x, spectral-norm 1.68x, reverse-complement 1.58x. |
| **Workload** | Nine small paired kernels, each written once in Wren and once in Lua (sum, range for, fib, tak, ack, mutual recursion, deep recursion, binary trees, method call); the Wren timer includes JIT warmup and compilation, process startup excluded; best of five self-timed runs. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro |
| **Compiler and flags** | CMake -DCMAKE_BUILD_TYPE=Release with a C99 compiler (compiler not named); SLJIT backend; pinned Wren 99d2f0b and sljit d9902b1; LuaJIT build and flags not stated |
| **Adoption** | 4 stars |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/Lulzx/WrenJIT) · [benchmark](https://github.com/Lulzx/WrenJIT) |

## Verdict

On an Apple M4 Pro (2026-08-07, best of five, both sides self-timed with clock()-based CPU time, process startup excluded, Wren timer includes JIT compilation, C compiler not named, LuaJIT build flags not stated) WrenJIT beat LuaJIT 2.1 on nine paired microkernels from 0.76x (fib 35: 39.4 vs 51.9 ms) to 0.02x (ack 3,7), but most rows time closed-form or hand-written replacements; on the author's ten Benchmarks Game ports (2026-08-08, LuaJIT 2.1.1785763465) it won only pidigits (66.4 vs 119.8 ms) and lost the rest by 1.58x to 26.69x.

## Use it when

- You already embed Wren and have hot numeric loops over ranges, lists or object fields that you want to run several times faster than the Wren interpreter (author's report: spectral-norm 652.8 to 17.0 ms, mandelbrot 701.9 to 68.3 ms, pidigits 1190.2 to 66.4 ms on Apple M4 Pro).
- Research or teaching: a compact (about 10,000 lines across the seven JIT source files read) tracing JIT with SSA IR, guard snapshots and per-pass debug dumps (WREN_JIT_DUMP_IR, WREN_JIT_DEBUG).
- ARM64 or x86-64 hosts, which are the only tested targets.

## Skip it when

- You want to beat LuaJIT on real programs: on the author's own ten Benchmarks Game ports WrenJIT is slower on 9 of 10 (nbody 848.4 vs 31.8 ms, regex-redux 455.9 vs 23.9 ms, k-nucleotide 175.4 vs 30.9 ms); only pidigits wins (66.4 vs 119.8 ms).
- Production use: one author, 29 commits, 4 stars, no releases; no side traces or trace chaining (one trace per loop PC), so branchy loops keep exiting to the interpreter (fannkuch-redux logged 30,219,029 side exits in bench/benchmarksgame_results.json).
- General recursive code: there is no method JIT, only six recognised bytecode shapes; anything else runs in the stock interpreter.
- Code that must stay correct for any input program: the shape matchers for the recursive kernels do not check operator or call-target symbols (see gotchas).
- Platforms other than ARM64 and x86-64, or builds without CMake and Git submodules.

## How it is fast

Loops: after 50 backward LOOP hits at one PC (JIT_HOT_THRESHOLD) one iteration is recorded as typed SSA, run through about 20 passes (box/unbox elimination, GVN, LICM, guard hoisting, integer induction-variable inference, bounds-check hoisting, escape analysis, comparison/guard fusion), linear-scan allocated and emitted via SLJIT, with snapshot-based side exits back to the interpreter. Several passes are closed-form or pattern rewrites: pass 15 replaces a boolean-toggle counter loop with arithmetic, pass 16 replaces an integer range sum with (limit-iter)\*(iter+limit+1)/2, and pass 18 (irOptDenomRecurrence) turns the spectral-norm A(i,j) denominator into a running recurrence. Recursion: called functions are matched against exact bytecode shapes (byte count and opcode positions) and replaced by native kernels for binary Fibonacci, Takeuchi (real int64 native recursion), linear recursion (collapsed to a loop), mutual parity (one AND), Ackermann (closed forms for small m) and binary-tree make/check (hand-written C in wren_jit_recursion.c).

## Compared with alternatives

Pick it only when you are committed to Wren and want its hot loops faster; for Lua code LuaJIT itself wins on 9 of the 10 paired ports, and Apogee (Lua 5.5 with a JIT in pure Go) is the sibling that measures honestly against a reference interpreter across 17 benchmarks rather than against LuaJIT on shaped kernels. Among new-language JITs, stryke and Objeck also claim LuaJIT wins on a minority of rows, so none of these is a general LuaJIT replacement.

## Integration

| | |
|---|---|
| **Form** | static lib (wrenjit_vm, the patched Wren VM plus JIT) built with CMake; CLI runner wrenjit_cli |
| **Dependencies** | Wren (git submodule pinned at 99d2f0b, patched by scripts/setup.sh) and SLJIT (submodule pinned at d9902b1); pthread and libm |
| **Minimum toolchain** | C99 compiler (GCC, Clang or AppleClang flags in CMakeLists.txt), CMake 3.16+; Release builds use -O3 and IPO/LTO when supported |
| **Platforms** | ARM64 and x86-64 tested (README Limits); report measured on Apple M4 Pro |
| **Thread safety** | not documented (JIT state lives in the per-VM vm-&gt;jit; Wren VMs are single-threaded) |
| **Drop-in for the baseline** | partial — replaces the stock Wren VM behind the same wren.h embedding API, but it runs only Wren, so it is not a drop-in for LuaJIT or Lua code |

## Gotchas

- Correctness bug by code reading (not run here): the recursive matchers for binary Fibonacci, linear recursion, Ackermann and Takeuchi in src/jit/wren_jit_recursion.c check opcode positions, integer constants and that both call sites use the same module variable and symbol, but never check which operator symbols are called (&lt;, -, +, ==, !) or that the call target is the function itself; only the tree and mutual-parity kernels resolve names. A hot static method with the same bytecode shape but different operators or callee (for example `return Other.g(n - 1) * Other.g(n - 2)`, or `if (n > 2)`) would be replaced by the Fibonacci kernel after 50 calls with integer arguments, despite the README's 'validates constants, symbols, arity'.
- Five of the nine README microbenchmark rows (range for, method call, ack, mutual recursion, deep recursion) run closed-form or loop-collapsed replacements and binary trees runs hand-written C (treeMakeFill bypasses the constructor), while LuaJIT runs the real loops and calls; fib and tak are real recursion but in specialised int64 native kernels with no type checks inside, so even those rows compare a hand-shaped kernel with LuaJIT's general JIT.
- bench/run_benchmarks.py only parses each program's self-reported 'elapsed:' line; it never compares Wren and Lua outputs, or JIT and no-JIT outputs, so a miscompile would not show up in the benchmark run (the upstream Wren test suite and test/test_jit.c run under ctest instead).
- By code reading, pass 16 (irOptFastForwardRangeSum) keeps the body nodes before the sum add for one execution and deletes every node after it up to the back edge, with no check that the body holds nothing else; whether other passes stop such traces is not documented. Also the JIT can be slower than the interpreter: the earlier Benchmarks Game run shows fannkuch-redux 11,430 vs 7,124 ms, fasta 182 vs 75 ms and regex-redux 765 vs 518 ms with JIT on.

## Known shortcomings

- Claim overstated: ack, range-for, method-call and mutual-recursion benchmarks are closed-form or O(1) replacements (wren_jit_recursion.c, optimization passes 15-16), deep recursion is collapsed to a loop and binary trees run hand-written C; only sum (0.59x), fib (0.76x) and tak (0.35x) compare like work. The author's own docs/index.html shows WrenJIT slower than LuaJIT on 9 of 10 Benchmarks Game ports (nbody 26.7x slower, pidigits the only win at 0.55x); compiler and LuaJIT build flags unstated. Results are disclosed, so kept.
- Enricher (code reading): in src/jit/wren_jit_recursion.c the fib, linear, Ackermann and Takeuchi shape matchers never check operator symbols (&lt;, -, +, ==) or that the call target is the function itself, so any hot static method with the same bytecode shape gets the wrong native kernel after 50 calls although the README says symbols are validated (only the tree and parity kernels check names); pass 16 deletes body nodes after the range-sum add without checking the body holds nothing else, pass 18 is a spectral-norm-specific rewrite, and bench/run_benchmarks.py never compares Wren and Lua outputs. An earlier Benchmarks Game run had the JIT slower than the Wren interpreter on fannkuch (11.43 vs 7.12 s), fasta and regex-redux.

## Caveats and trade-offs

The README calls these 'narrow kernels, not a language-wide victory lap'. Several microbenchmark rows measure benchmark-shaped special cases rather than JIT code doing the same work as LuaJIT: src/jit/wren_jit_recursion.c recognizes exact bytecode shapes and emits Ackermann as the closed form 2^(n+3)-3 (no recursion), mutual even/odd recursion as a single parity test, linear recursion as a loop, and binary-tree make/check through hand-written C (treeMakeFill and a C tree walker); optimizer passes 15-16 in src/jit/wren_jit_opt.c fast-forward range sums and boolean toggle counters in closed form (the report admits these are 'reduced as recurrences instead of paid one iteration at a time'). Outputs are correct and the specializations are guarded, but the 0.02x-0.19x rows say nothing about general Wren code. On the author's ten paired Benchmarks Game ports (docs/index.html; also bench/benchmarksgame_results.json from an earlier run) WrenJIT is slower than LuaJIT on 9 of 10 programs (up to 26.7x slower on nbody) and slower than the plain Wren interpreter on k-nucleotide; only pidigits wins. Programs are separate Wren and Lua ports, self-timed with System.clock/os.clock, best of five, sub-millisecond timings on several rows; Wren timer includes JIT warmup. C compiler not named; LuaJIT build flags not stated. Single author, 4 stars, repo started 2026-02-22. [retier] Claim overstated: ack, range-for, method-call and mutual-recursion benchmarks are closed-form or O(1) replacements (wren_jit_recursion.c, optimization passes 15-16), deep recursion is collapsed to a loop and binary trees run hand-written C; only sum (0.59x), fib (0.76x) and tak (0.35x) compare like work. The fib, linear, Ackermann and Takeuchi shape matchers never check operator symbols or that the call target is the function itself (the README says symbols are validated), so a hot static method with the same bytecode shape gets the wrong native kernel after 50 calls; pass 16 deletes body nodes after the range-sum add without checking the body is otherwise empty; pass 18 is spectral-norm-specific; bench/run_benchmarks.py never compares Wren and Lua outputs. The author's own docs/index.html shows WrenJIT slower than LuaJIT on 9 of 10 Benchmarks Game ports (nbody 26.7x slower) and an earlier run had the JIT slower than the Wren interpreter on fannkuch (11.43 vs 7.12 s), fasta and regex-redux. Compiler and LuaJIT build flags unstated.

Only runs Wren programs (a patched Wren VM, patches/0001-wren-jit-hooks.patch). One trace per loop PC, no side traces or trace chaining. Recursion is compiled by recognising complete bytecode shapes and emitting native kernels, not by a general method JIT. Tested on ARM64 and x86-64 only.

## Maintenance

Active single-author research project (last commit 2026-08-14, 29 commits, MIT); usable as a Wren VM replacement for experiments, but the shape-matched recursive kernels need symbol and callee checks before it is trusted on arbitrary programs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers with public paired harness (bench/run_benchmarks.py, bench/\*.wren, bench/lua_equivalents/\*.lua, results in bench/results.json) and CPU stated (Apple M4 Pro), but the C compiler is not named and the LuaJIT build flags are not stated, so not A; no independent measurement, so not B.
- **Verifier notes:** Numbers in the record match the README table exactly, but the claim is overstated: ack, range for, method call and mutual recursion are closed-form or O(1) replacements, deep recursion is collapsed to a loop and binary trees run hand-written C, so only sum/fib/tak (0.59x/0.76x/0.35x) compare like work. The author's own published report shows WrenJIT slower than LuaJIT on 9 of 10 Benchmarks Game ports (faster only on pidigits 0.55x). Kept at tier C with these shortcomings (results are correct and disclosed, so not a reject under the invalid-evidence rule); metadata checked: MIT, 4 stars, last commit 2026-08-14, not a fork.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Lulzx/WrenJIT>
  - <https://github.com/Lulzx/WrenJIT/commits/main>
  - <https://github.com/Lulzx/WrenJIT/tree/main/bench>
  - <https://github.com/Lulzx/WrenJIT/tree/main/src/jit>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/run_benchmarks.py>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/results.json>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/benchmarksgame_results.json>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_ack.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_ack.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_for.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_for.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_method_call.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_method_call.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_mutual.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_trees.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_recursion.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_opt.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/docs/index.html>
- **Sources the enricher read:**
  - <https://github.com/Lulzx/WrenJIT>
  - <https://github.com/Lulzx/WrenJIT/commits/main>
  - <https://github.com/Lulzx/WrenJIT/issues?q=is%3Aissue>
  - <https://github.com/Lulzx/WrenJIT/issues/1>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/run_benchmarks.py>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/runner.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/results.json>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/benchmarksgame_results.json>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/patches/0001-wren-jit-hooks.patch>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_sum.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_sum.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_for.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_for.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_fib.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_fib.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_tak.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_tak.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_ack.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_ack.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_mutual.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_mutual.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_deep.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_deep.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_trees.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_trees.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/bench_method_call.wren>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/bench/lua_equivalents/bench_method_call.lua>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_opt.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_opt_iv.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_recursion.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_codegen.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit.h>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/src/jit/wren_jit_memory.c>
  - <https://raw.githubusercontent.com/Lulzx/WrenJIT/HEAD/test/test_jit.c>
  - <https://raw.githubusercontent.com/wren-lang/wren/99d2f0b/src/vm/wren_core.c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/lulzx/wrenjit`) · [data/wave12/enrich/raw/github_com_lulzx_wrenjit.json](../../../data/wave12/enrich/raw/github_com_lulzx_wrenjit.json) (enrichment confidence 0.75)

</details>
