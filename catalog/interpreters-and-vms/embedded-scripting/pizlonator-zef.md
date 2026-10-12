# Zef

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Toy AST-walking interpreter tuned with inline caches; its leaky Yolo-C++ build beats CPython 3.10 and QuickJS-ng on four benchmarks.

| | |
|---|---|
| **Beats** | QuickJS-ng 0.14.0 (release binary qjs-linux-x86_64), Lua 5.4.7 (built with GCC 11.4.0), CPython 3.10 (Ubuntu 22.04 package) |
| **Claimed result** | Write-up 'Raw Data' table, which matches run-benchmarks-results-1776652178.csv, gives geomean seconds: CPython 3.10 0.1296, Lua 5.4.7 0.0577, QuickJS-ng 0.14.0 0.2036, Zef Fil-C++ build #21 (no asserts) 0.2759, Zef in Yolo-C++ 0.0686. The author's table states Yolo-C++ Zef is 1.889x faster than CPython, 1.189x slower than Lua and 2.968x faster than QuickJS-ng; the memory-safe Fil-C++ build is 2.13x slower than CPython, 4.781x slower than Lua and 1.355x slower than QuickJS-ng. Per row, Yolo-C++ Zef beats QuickJS-ng on splay (0.3992 vs 0.7090), richards (0.0309 vs 0.7193) and deltablue (0.0784 vs 0.1585) but not nbody (0.0233 vs 0.0214); it beats CPython on all four rows and Lua only on splay and deltablue. The QuickJS-ng richards figure covers 20 runs of the benchmark (ScriptBench/richards.js loops runRichards() 20 times) while the Zef, Lua and Python ports run it once; dividing that row by 20 gives about 0.036 s per run, so Yolo-C++ Zef is about 1.16x faster on richards and about 1.40x faster than QuickJS-ng on the geomean, not 2.97x (derived from page data). The write-up's own headline is a 16x speed-up (67x with the Yolo-C++ port) that brings the interpreter 'into the ballpark' of QuickJS, CPython and Lua. |
| **Workload** | ScriptBench1 run by run-benchmarks: nbody (5000 advance steps), splay (32 runs on an 8000-node tree), richards (one run with COUNT 10000 in the Zef, Lua and Python ports, but 20 runs in richards.js) and deltablue (20 rounds of chainTest(100) plus projectionTest(100); the JS port adds one extra projectionTest). Wall-clock seconds of the whole process including interpreter startup, averaged over randomly interleaved runs (write-up says 30; the script defaults to --repeat 3), with a geomean row. |
| **Metric** | throughput |
| **Hardware** | Intel Core Ultra 5 135U, 32GB RAM, Ubuntu 22.04.5 |
| **Compiler and flags** | Fast column: Yolo-C++ build with GCC 11.4.0 (write-up); meson.build sets buildtype=debugoptimized (-O2 -g), cpp_std=c++20, -fno-exceptions, -fno-rtti, -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE. The exact configure command and source revision of the pizlscript/yoloBuild directory are not stated. Memory-safe columns: Fil-C++ 0.677 (write-up; README asks for 0.678 or later) with the same meson.build. |
| **Adoption** | 39 stars, 82 commits |
| **Last commit** | 2026-04-22 |
| **Links** | [repository](https://github.com/pizlonator/zef) · [benchmark](https://github.com/pizlonator/zef/blob/master/website/source/implementation.md) |

## Verdict

On the author's ScriptBench1 (nbody, splay, richards, deltablue; mean wall-clock seconds over 30 interleaved runs on an Intel Core Ultra 5 135U, Ubuntu 22.04.5), the GCC 11.4.0 Yolo-C++ build's geomean was 0.0686 s against CPython 3.10 0.1296 s (1.89x faster), Lua 5.4.7 0.0577 s (1.19x slower) and QuickJS-ng 0.14.0 0.2036 s; the QuickJS-ng margin is about 1.40x once richards.js's 20 iterations are divided out (derived from page data). The memory-safe Fil-C++ 0.677 build (geomean 0.2759 s) is slower than all three baselines.

## Use it when

- You are writing your own dynamic-language interpreter and want a worked, diff-by-diff example of inline caches and watchpoints in an AST interpreter, with measured gains per step.
- You want evidence of what each classic trick buys in an interpreter without a JIT: object model plus inline caches gave 4.55x, symbols 18%, argument specialization about 4%, per the write-up.
- Teaching or research on memory-safe C++ (Fil-C++) overheads: the write-up documents Fil-C pathologies (std::optional unions and stack Values becoming heap allocations) and their workarounds.
- Short-lived scripts in a hobby setting where a self-contained interpreter in about 100 source files is acceptable.

## Skip it when

- Embedding a scripting language in an application: there is no host API, no sandboxing and no documented C++ interface; Lua, Luau or QuickJS are the realistic choices.
- Any long-running workload on the fast build: the Yolo-C++ path allocates with calloc and never frees (src/utils.h marks it 'FIXME: This is unsound'), so memory grows until the process dies.
- Wanting speed with memory safety: the documented Fil-C++ build (with GC) is 2.13x slower than CPython 3.10, 4.78x slower than Lua 5.4.7 and 1.36x slower than QuickJS-ng 0.14.0 on the author's geomean.
- Anything needing a licence: the repo has no LICENSE file and the README names none, so the code cannot be reused.
- Production maturity: single-author side project, 82 commits, last commit 2026-04-22, no releases, one open issue (broken localhost links in the docs).

## How it is fast

It stays a recursive AST walker but adds the machinery a JIT would use: NaN-style tagged 64-bit values (doubles offset by 0x1000000000000, inline int32s), hash-consed Symbols instead of std::string lookups, a Storage/Offsets object model computed in a resolve pass, and inline caches implemented by placement-constructing specialized AST nodes over generic ones (constructCache&lt;&gt;), guarded by watchpoints for scope-chain and subclass invariants. The rest is grinding: per-operator Binary&lt;&gt;/Unary&lt;&gt; nodes, getter/setter inference, a global (class, symbol) to callee table, Zero/One/TwoArguments specializations, and constant array-literal specialization. The final 4x comes from compiling with an ordinary C++ compiler instead of Fil-C++, where GC allocations become calloc and are never freed.

## Compared with alternatives

Pick Zef only as reading material on interpreter optimization; for an actual embedded engine Lua or Luau (faster than Zef's fast build on nbody and richards, with an embedding API) or QuickJS (a real JS engine) win, and Daslang or LuaJIT Remake (Deegen) are the catalogued choices when interpreter speed itself is the goal.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone executable built with Meson; no library target) |
| **Dependencies** | Fil-C++ 0.678 or later for the documented GC build; Meson and Ninja. The non-Fil-C path in src/utils.h builds with an ordinary C++20 compiler but has no GC. |
| **Minimum toolchain** | C++20 (meson.build cpp_std=c++20, -fno-exceptions, -fno-rtti); Fil-C++ 0.678+ per README; GCC 11.4.0 used for the Yolo-C++ measurements |
| **Platforms** | Only Linux x86-64 (Ubuntu 22.04.5) is tested in the write-up; the value encoding assumes no object pointer falls below 0x100000000 |
| **Thread safety** | not documented; the language has no threads and runtime structures such as watchpoints (src/watchpoint.h: plain version counter and std::vector of handlers) are unsynchronized |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: ScriptBench/richards.js calls runRichards() 20 times while the Zef, Lua and Python ports run it once, so QuickJS-ng's richards time (0.7193 s) covers 20x the work. Per run QuickJS-ng takes about 0.036 s vs 0.0309 s for Yolo-C++ Zef, and the headline 2.97x geomean win over QuickJS-ng shrinks to about 1.40x (derived from page data). deltablue.js also runs one extra projectionTest(100) after its 20 rounds, and splay.js keys come from Math.random() while the other ports use a seeded xorshift.
- The Yolo-C++ build never reclaims memory, and it beats Lua 5.4.7 only on splay (0.3992 vs 0.4393 s) and deltablue (0.0784 vs 0.0832 s), the two allocation-heavy rows, so those wins carry no collection cost while CPython, Lua and QuickJS-ng do collect (inference from the write-up and src/utils.h). The benchmarked binary came from a separate checkout (pizlscript/yoloBuild) whose revision is not stated.
- Result checks are uneven: ScriptBench/richards.lua tests 'qpktcount == QPKTCOUNT or holdcount == HOLDCOUNT' and only prints FAILURE without a non-zero exit, and run-benchmarks only checks exit status, so a wrong Lua result would still be timed. The Python and Zef ports do fail the run on a wrong count.
- Timing is wall-clock of the whole process via Ruby Time.now, including interpreter startup; several rows run only 14-40 ms (nbody: Lua 0.0142 s, QuickJS-ng 0.0214 s, Yolo Zef 0.0233 s), so startup compresses the ratios. The script defaults to --repeat 3; the write-up says 30 runs.

## Known shortcomings

- ScriptBench/richards.js runs runRichards() 20 times while the other language ports run it once, so the QuickJS-ng richards row is inflated about 20x; the win over QuickJS-ng is about 1.40x after correction, not 2.97x (derived from page data). The fast yoloBuild is an incomplete port that never frees memory (the author calls it unsound) built from a separate checkout of unstated revision; the memory-safe Fil-C++ build is slower than QuickJS, CPython and Lua. No licence file, so reference only. CPU Intel Core Ultra 5 135U, GCC 11.4.0.
- Enricher: deltablue.js runs one extra projectionTest and splay.js uses Math.random() keys while the other ports use seeded xorshift; richards.lua prints FAILURE without a non-zero exit and run-benchmarks checks only exit status, so a wrong Lua result still gets timed. The Yolo-C++ build allocates through calloc and never frees (src/utils.h FIXME 'unsound'), and it beats Lua only on splay and deltablue, the allocation-heavy rows that therefore pay no GC cost. Dormant since 2026-04-22, no embedding API.

## Caveats and trade-offs

First-party, four benchmarks only. The QuickJS-ng richards column runs 20x the work of the other ports, inflating the QuickJS-ng comparison (about 1.40x rather than 2.97x after correction, derived from page data). The fast Yolo-C++ build is, in the author's words, an incomplete and unsound port: GC allocations become calloc and memory is never freed, which only survives because the benchmarks are short; it was built from a separate checkout (pizlscript/yoloBuild) whose revision is not stated. The memory-safe Fil-C++ build documented in the README is slower than all three baselines. Wall-clock timing includes process startup, and several rows run only 14-40 ms. Splay's Python and Lua ports were written with Claude; the Lua richards check uses 'or' instead of 'and'. No LICENSE file (LICENSE, LICENSE.md, LICENSE.txt and COPYING return 404) and the README names no licence, hence reference only. The write-up is checked into the repo at website/source/implementation.md, so its text was read directly.

AST-walking interpreter (NaN boxing, stack-frame slots, watchpoints, inline caches, no bytecode or JIT); the fast numbers need the memory-unsafe Yolo-C++ build, while the Fil-C++ build the README documents is memory-safe but 4.8x slower than Lua (derived from page data). Standalone interpreter with no documented embedding API; no GC-pause or memory data given.

## Maintenance

Single-author demonstration project, dormant since 2026-04-22 after a month of commits; no licence, so reference only, and its fast configuration leaks all memory by design.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** Benchmark code (run-benchmarks, ScriptBench/\*.zef/.js/.py/.lua) and interpreter source are public, and the in-repo write-up (website/source/implementation.md) states the CPU (Intel Core Ultra 5 135U), GCC 11.4.0 for the Yolo-C++ build, with meson.build giving debugoptimized plus -fno-exceptions -fno-rtti, which is close to A. It stays at C because the fast column is a separate, undocumented checkout (pizlscript/yoloBuild) of what the author calls an incomplete, unsound port, and the QuickJS richards script runs 20x the work of the other ports, so the first-party comparison is not a clean run against the baseline.
- **Verifier notes:** Numbers match the CSV and the in-repo write-up, but the 2.97x win over QuickJS-ng is inflated because ScriptBench/richards.js runs runRichards() 20 times while the other ports run it once; corrected it is about 1.40x (derived). The fast build is an incomplete Yolo-C++ port that never frees memory (author calls it unsound), and the memory-safe Fil-C++ build is slower than CPython, Lua and QuickJS-ng. Kept at C with no licence (reference); not a reject because the CPython and Lua comparisons are like-for-like and the author documents the flaws.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** corrected richards iteration count, licence; like-for-like ports with result checks and a freeing build
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/run-benchmarks-results-1776652178.csv>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/README.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/COPYING>
  - <https://github.com/pizlonator/zef>
  - <https://github.com/pizlonator/zef/commits>
  - <https://github.com/pizlonator/zef/commits/master>
  - <https://github.com/pizlonator/zef/commit/7f33f429e17a64c5f6b29d5f3f99c93e35a39745>
  - <https://github.com/pizlonator/zef/tree/master/ScriptBench>
  - <https://github.com/pizlonator/zef/tree/master/website>
  - <https://github.com/pizlonator/zef/tree/master/website/source>
  - <https://github.com/pizlonator/zef/blob/master/website/source/implementation.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/run-benchmarks>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/meson.build>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/website/generate.sh>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/website/source/index.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/website/source/implementation.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/README.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.zef>
- **Sources the enricher read:**
  - <https://github.com/pizlonator/zef>
  - <https://github.com/pizlonator/zef/tree/master/src>
  - <https://github.com/pizlonator/zef/commits/master>
  - <https://github.com/pizlonator/zef/issues>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/README.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/run-benchmarks>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/meson.build>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/run-benchmarks-results-1776652178.csv>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/website/source/implementation.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/website/source/index.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/README.md>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/richards.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/splay.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.lua>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/nbody.py>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.js>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/ScriptBench/deltablue.zef>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/src/storage.h>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/src/value.h>
  - <https://raw.githubusercontent.com/pizlonator/zef/HEAD/src/watchpoint.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pizlonator/zef`) · [data/wave12/enrich/raw/github_com_pizlonator_zef.json](../../../data/wave12/enrich/raw/github_com_pizlonator_zef.json) (enrichment confidence 0.45)

</details>
