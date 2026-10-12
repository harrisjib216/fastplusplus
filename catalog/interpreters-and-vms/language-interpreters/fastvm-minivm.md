# MiniVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Small C register VM running a Lua subset; 2022 build beat luajit -joff on fib(35) but lost to LuaJIT's JIT.

| | |
|---|---|
| **Beats** | LuaJIT (interpreter-only luajit -joff, and with the JIT on); the 2022 README also compares Node.js and C (clang -Ofast); the current test harness also runs PUC Lua |
| **Claimed result** | January 2022 README (commit cf7ec355, Paka frontend, hyperfine, fib.png): fib(35) minivm 159.3 ms versus luajit -joff 403.8 ms (about 2.5x faster, derived from page data), but LuaJIT with the JIT on took 51.6 ms (minivm about 3.1x slower, derived), Node 146.0 ms and C 36.7 ms. Binary trees (tree.png, log-scale bars without numeric labels): minivm bars sit below LuaJIT (JIT on) from depth 9 to 20 and near C. Current README (2024 code): fib(40) 'took: 1725.805ms' and hello world 'took: 0.307ms', no baseline. HN title (2022): 'on par with LuaJIT and C'. |
| **Workload** | 2022: recursive fib(35) and binary-trees allocation benchmark (depths 8-20) written in Paka, Lua, JS and C (FastVM/paka/bench), timed with hyperfine including process startup. Current repo: test/bench.sh times every test/\*.lua under minivm, luajit and lua with date-based wall clock and graphs them, but no results are published. |
| **Metric** | throughput |
| **Hardware** | 2020 MacBook Air M1, 8 GB RAM, macOS Big Sur 11.2.3 (2022 README) |
| **Compiler and flags** | 2022: C baseline built with clang -Ofast; MiniVM's build flags not stated. Current makefile defaults to OPT = -Os -flto; README 'For Speed' build is make -Bj OPT='-O3 -flto'. |
| **Adoption** | 1.7k stars |
| **Last commit** | 2025-06-08 |
| **Links** | [repository](https://github.com/FastVM/minivm) · [benchmark](https://raw.githubusercontent.com/FastVM/minivm/cf7ec35504622d6661c7f677fbed9dc8a8e1eb62/README.md) |

## Verdict

In January 2022 the Paka-frontend MiniVM ran recursive fib(35) in 159.3 ms against 403.8 ms for luajit -joff (about 2.5x faster, derived from page data) but 51.6 ms for LuaJIT with the JIT on, Node 146.0 ms and clang -Ofast C 36.7 ms, measured with hyperfine including startup on a 2020 MacBook Air M1 (first-party, MiniVM flags unstated). The rewritten Lua-frontend code has no published comparison.

## Use it when

- Studying how a compact (\~1,200-line backend) direct-threaded register interpreter with lazy basic-block translation is built
- Experiments with a small, MIT-licensed Lua-subset interpreter where startup time matters (README: 0.307 ms for hello world, first-party, no baseline)
- Teaching or prototyping a VM frontend on Linux x86-64 or WebAssembly (emcc targets in the makefile)
- Integer-typed numeric experiments: the --number= flag switches the number type among i8, i16, i32, i64, f32 and f64

## Skip it when

- As a LuaJIT replacement: on the only published comparison (fib(35), 2022, M1) LuaJIT with its JIT on was about 3.1x faster, and the JIT the README advertises does not exist in current code (issue #29 'Implement JIT', open since June 2024)
- Running real Lua programs: only a tested subset is supported; no metatables, coroutines or standard-library coverage appears in the test list
- Embedding in a host application: no documented library build or stable C API in the current tree
- Allocation-heavy work on macOS, Windows or WebAssembly builds: the makefile builds those with -DVM_NO_GC, which maps vm_malloc to plain malloc with no collector, so garbage is never reclaimed
- Production use: single maintainer, last functional change June 2024 (the June 2025 commit only fixes a --load argument check), and the only Windows bug report (#28, no output) was closed without a documented fix

## How it is fast

Direct-threaded dispatch: vm/backend/backend.c translates each IR basic block lazily, on first entry, into a byte stream of GCC labels-as-values handler addresses (computed goto) with operands inlined. Opcodes are specialised by operand kind (register/immediate variants such as ADD_RI, BLT_RR), literal-literal arithmetic is folded during translation, and values are tagged cells (8-byte union plus a 1-byte type tag) in a flat register file. The 2022 README attributed its binary-trees result to a custom allocator and GC; the current Linux build uses the Boehm conservative GC (vendor/bdwgc) instead.

## Compared with alternatives

Pick LuaJIT for any real Lua workload (faster with its JIT on, full Lua 5.1, embeddable API), and Wren when you want a small embeddable scripting VM with an independent benchmark re-run; MiniVM is mainly worth reading as a compact computed-goto register VM design, not something to deploy.

## Integration

| | |
|---|---|
| **Form** | built executable via GNU Make (source-drop for embedding; no documented library target) |
| **Dependencies** | git submodules vendor/bdwgc (Boehm GC, Linux/FreeBSD builds), vendor/tree-sitter (Lua parser runtime), vendor/isocline (REPL), vendor/raylib (drawing, mac/windows/freebsd/web targets); cargo only to regenerate the tree-sitter parser |
| **Minimum toolchain** | C11 with GNU extensions (computed goto, statement expressions), GCC or Clang; MSVC not supported |
| **Platforms** | Linux x86-64, FreeBSD amd64, Windows x64 and WebAssembly per README; the makefile also has a mac target |
| **Thread safety** | not documented; one shared register file per vm_t and the latest release commit is titled 'no threads' |
| **Drop-in for the baseline** | no |

## Gotchas

- The README speed commands do not run on current code: main/minivm.c has no --dump-time option (an unknown flag is treated as a file name and exits with 'error: no such file'), its clock() start time is never printed, and test/fib/fib40.lua does not exist (404); so the README's fib(40) 1725.805 ms and 0.307 ms timings come from an older build
- Only comparative numbers are the January 2022 Paka-frontend VM (README at commit cf7ec355): fib(35) minivm 159.3 ms vs luajit -joff 403.8 ms vs LuaJIT JIT 51.6 ms, hyperfine with process startup included, one M1 laptop, MiniVM build flags not stated; binary-trees results are only a log-scale chart without numbers, and its 'faster than C' claim is against FastVM/paka bench/tree.c, a naive malloc/free-per-node C version
- Current harness flaws (test/bench.sh with minivm.sh, lua.sh, luajit.sh): one run per test, wall clock from date +%s.%N that also includes process startup and a cat of the captured output, failing tests silently dropped from the table, and minivm.sh's rebuild step is commented out so it times whatever binary exists (the default makefile OPT is -Os -flto, size-optimised); no results are published
- Calls recurse on the C stack (vm_run_repl calls itself per Lua call) and each frame takes registers from a fixed 65,536-slot array allocated in main.c; no depth check is visible in vm/backend/backend.c, so deep recursion can run past that buffer

## Known shortcomings

- Numbers are from the January 2022 README (commit cf7ec355, hyperfine on an M1, fib(35)): 2.5x faster than luajit -joff but 3.1x slower than LuaJIT with the JIT on, measured on the old Paka-frontend VM before the rewrite. The current README's TB JIT claim is stale: no cuik submodule, backend.c is an interpreter.
- Enricher: the README speed commands are broken on current code (main/minivm.c has no --dump-time, so it is read as a file name and exits 'error: no such file'; the clock() start is never printed; test/fib/fib40.lua is 404), so the fib(40) 1725.805 ms and 0.307 ms timings come from an older build. No JIT (issue #29 'Implement JIT' open since 2024-06; backend.c is a computed-goto threaded interpreter). mac/windows/web builds use -DVM_NO_GC (plain malloc, nothing freed); fixed 65,536-slot register array with no recursion depth check. Current test/\*.sh harness: single run, date wall clock including startup and a cat of the output, failing tests dropped, rebuild commented out (default -Os). The 2022 binary-trees 'faster than C' was against paka bench/tree.c with naive malloc/free per node.

## Caveats and trade-offs

The only comparative numbers are from January 2022 and measure the old Paka-frontend VM, which was later rewritten around a Lua frontend; the current code has no published comparison. They come from one first-party run set on one M1 laptop with startup included. Against LuaJIT with its JIT on, minivm was about 3.1x slower on fib(35); the faster claims hold only against luajit -joff (about 2.5x) and on the binary-trees graph. The current README says MiniVM has a JIT based on Cuik's TB, but .gitmodules lists no cuik submodule and vm/backend/backend.c is a threaded interpreter, so that README text looks stale. The harness (test/bench.sh, lua.sh, luajit.sh, graph.py) exists but needs running. Last commit 2025-06-08.

Optimizing VM with a JIT built on Cuik's TB (git submodule); supports Linux x86-64, FreeBSD amd64, Windows x64 and WebAssembly only. Runs a Lua-like language, not full Lua compatibility. Written in C11 with minor GNU extensions, builds with GCC or Clang.

## Maintenance

Stale: real development stopped June 2024 (one small fix June 2025), the README's JIT and timing commands are out of date, and it is MIT-licensed and small enough to read, but is a research-grade toy, not a vendorable runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the January 2022 README (commit cf7ec355) has first-party hyperfine output on a 2020 MacBook Air M1 comparing minivm with LuaJIT (JIT on and -joff), Node and C on fib(35), with benchmark sources in FastVM/paka/bench; MiniVM's own build flags are not stated and the numbers describe the pre-rewrite Paka-frontend VM, so C. The current README has only two timings with no baseline.
- **Verifier notes:** Found 2022 benchmark numbers in repo history (README at cf7ec355 plus fib.png hyperfine screenshot and tree.png graph) and upgraded D to C. The record's claim that the repo was 'rebuilt around a TB-based JIT' does not match current main (no cuik submodule; backend is an interpreter). Shortcoming to record: numbers from pre-rewrite 2022 code, slower than LuaJIT with JIT on, faster only than luajit -joff; HN thread itself not opened (snippet only).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** measurement of the current VM against LuaJIT and Lua 5.4; current-build measurement with a working harness
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/README.md>
  - <https://github.com/FastVM/minivm>
  - <https://github.com/FastVM/minivm/commits>
  - <https://github.com/FastVM/minivm/commits/main?until=2022-01-12>
  - <https://github.com/FastVM/minivm/tags>
  - <https://github.com/FastVM/minivm/tree/main/test>
  - <https://github.com/FastVM/minivm/tree/main/vendor>
  - <https://github.com/FastVM/minivm/tree/main/vm>
  - <https://github.com/FastVM/minivm/tree/main/vm/backend>
  - <https://github.com/FastVM/minivm/blob/main/.gitmodules>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/bench.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/luajit.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/graph.py>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/makefile>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/backend/backend.c>
  - <https://raw.githubusercontent.com/FastVM/minivm/cf7ec35504622d6661c7f677fbed9dc8a8e1eb62/README.md>
  - <https://raw.githubusercontent.com/FastVM/minivm/cf7ec35504622d6661c7f677fbed9dc8a8e1eb62/fib.png>
  - <https://raw.githubusercontent.com/FastVM/minivm/cf7ec35504622d6661c7f677fbed9dc8a8e1eb62/tree.png>
  - <https://github.com/FastVM/paka/tree/main/bench>
- **Sources the enricher read:**
  - <https://github.com/FastVM/minivm>
  - <https://github.com/FastVM/minivm/commits/main>
  - <https://github.com/FastVM/minivm/issues?q=is%3Aissue>
  - <https://github.com/FastVM/minivm/issues/29>
  - <https://github.com/FastVM/minivm/issues/28>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/README.md>
  - <https://raw.githubusercontent.com/FastVM/minivm/cf7ec35504622d6661c7f677fbed9dc8a8e1eb62/README.md>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/makefile>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/tool/core.mak>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/bench.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/minivm.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/luajit.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/lua.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/graph.sh>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/graph.py>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/fib/fib.lua>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/fib/fib40.lua>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/test/tables/trees.lua>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/main/minivm.c>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/vm.h>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/ir.h>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/lib.h>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/lib.c>
  - <https://raw.githubusercontent.com/FastVM/minivm/HEAD/vm/backend/backend.c>
  - <https://github.com/FastVM/paka/tree/main/bench>
  - <https://raw.githubusercontent.com/FastVM/paka/main/bench/tree.paka>
  - <https://raw.githubusercontent.com/FastVM/paka/main/bench/tree.lua>
  - <https://raw.githubusercontent.com/FastVM/paka/main/bench/tree.c>
  - <https://raw.githubusercontent.com/FastVM/paka/main/bench/ptree.c>
  - <https://raw.githubusercontent.com/FastVM/paka/main/bench/tree.js>
  - https://news.ycombinator.com/item?id=29850562 (WebSearch snippet only; HN and mirrors blocked)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/fastvm/minivm`) · [data/wave12/enrich/raw/github_com_fastvm_minivm.json](../../../data/wave12/enrich/raw/github_com_fastvm_minivm.json) (enrichment confidence 0.7)

</details>
