# Wren

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Tiny embeddable class-based scripting VM in C; fastest on method-dispatch benchmarks, slower than Lua 5.4 elsewhere.

| | |
|---|---|
| **Beats** | Lua 5.4.4 (PUC), Python 3.11.3, Ruby 3.0.5 in the re-run; Lua 5.2.3, Python 3.3, Ruby 2.0 on the original page |
| **Claimed result** | Independent re-run (asb, PR #1164, Ryzen 9 5950X, median of 10): method_call 0.079 s vs Lua 5.4.4 0.121 s (about 1.5x), DeltaBlue 0.086 s vs Python 3.11.3 0.107 s; behind Lua 5.4 on fib (0.148 vs 0.087 s) and slowest on binary trees (0.141 vs Lua 0.139, Ruby 3.0.5 0.116). The doc/site/performance.markdown table (about 2014: Lua 5.2.3, Python 3.3, Ruby 2.0) shows broader wins that do not hold against current baselines. |
| **Workload** | Four small benchmarks (method call, DeltaBlue, binary trees, recursive Fibonacci); best of 10 runs, interpreter startup excluded. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X (asb re-run, PR #1164); i7-12700H in discussion #1183; original 2014 page unstated |
| **Compiler and flags** | Not stated. |
| **Adoption** | 8.1k stars |
| **Last commit** | 2025-11-19 |
| **Links** | [repository](https://github.com/wren-lang/wren) · [benchmark](https://github.com/wren-lang/wren/pull/1164) |

## Verdict

On the author's 2.3 GHz Core i7 MacBook Pro (no compiler or flags stated, best of 10, startup excluded) Wren beat Lua 5.2.3, Python 2.7.5/3.3.4 and Ruby 2.0.0 on method call (0.12 s vs Lua 0.35 s), DeltaBlue (Python only), binary trees and Fibonacci, while LuaJIT 2.0.2 -joff won binary trees and Fibonacci. An independent 2023 re-run on a Ryzen 9 5950X against Lua 5.4.4, Python 3.11.3 and Ruby 3.0.5 keeps only the method-call (0.079 s vs Lua 0.121 s) and DeltaBlue (0.086 s vs Python 0.107 s) wins.

## Use it when

- Embedded scripting dominated by object method calls and dynamic dispatch: on an independent 2023 re-run (Ryzen 9 5950X) method_call took 0.079 s vs Lua 5.4.4 0.121 s, Ruby 3.0.5 0.104 s, Python 3.11.3 0.171 s.
- Games or apps that want a class-based language with fibers in a VM small enough to read and patch, on platforms where JIT compilation is not allowed.
- Hosts that run several isolated interpreters at once: the C implementation has no global state, so separate VMs can run concurrently on different threads.
- Projects that need to compile the interpreter as C99 or C++98 with no dependencies beyond the C standard library (and libm).

## Skip it when

- Recursion- or arithmetic-heavy scripts: in the same 2023 re-run Lua 5.4.4 ran recursive Fibonacci in 0.087 s vs Wren 0.148 s, and an i7-12700H run (discussion #1183) had Lua 5.4.6 at 0.085 s vs Wren 0.131 s and 0.33 s vs 0.56 s on the for-loop benchmark.
- Allocation-heavy code: on binary trees Wren 0.4 (0.141 s) was slower than Lua 5.4 (0.139 s), Python 3.11 (0.137 s), Ruby 3.0 (0.116 s) and LuaJIT -joff (0.074 s) in the 2023 re-run.
- Hash maps with numeric keys: discussion #1183 measured map_numeric at 0.728 s for Wren vs 0.431 s for CPython 3.9.18.
- Running untrusted script source: five fuzzer-reported memory-safety bugs in the compiler (heap/stack/global buffer overflows, NULL dereference; issues #1217-#1221, January 2026) are open, and deep recursion is not checked (issue #939: memory grows until the OOM killer sends SIGKILL).
- When you need a large ecosystem or standard library, or a JIT: Wren has a small standard library (README), and LuaJIT even in -joff mode beat it on binary trees and Fibonacci in both the original and the 2023 runs.

## How it is fast

Values are NaN-tagged 8-byte doubles, so numbers, bools and null are unboxed. Classes are declared statically with private fields, so field access is a fixed slot offset known at compile time, and copy-down inheritance plus arity-overloaded signatures make a method call a single lookup in the receiver class's method table with no argument-count check. The interpreter loop uses computed-goto dispatch on GCC/Clang (author: 5-10% gain; switch fallback on MSVC), and a Lua-style single-pass compiler emits bytecode while parsing.

## Compared with alternatives

Pick Wren over LuaJIT or pocketpy when you want a class-based language with fibers in a tiny VM and your scripts are dominated by method calls, where it beat LuaJIT -joff, Lua 5.4 and CPython 3.11; for numeric, recursive or allocation-heavy scripts LuaJIT (even with the JIT off) or plain Lua 5.4 is faster.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C standard library; libm must be linked explicitly on Linux and BSD |
| **Minimum toolchain** | C99 or C++98; computed-goto dispatch needs GCC or Clang (disabled for MSVC without clang) |
| **Platforms** | any platform with IEEE-754 doubles (NaN tagging; WREN_NAN_TAGGING=0 switches to a larger struct representation) |
| **Thread safety** | No global state; multiple VMs can run concurrently on different threads. Sharing one VM across threads is not documented as safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the published numbers: the page (doc/site/performance.markdown) uses about-2014 baselines (Lua 5.2.3, Python 2.7.5/3.3.4, Ruby 2.0.0) and best-of-10 times; each script times itself with a different clock (Wren clock()/CLOCKS_PER_SEC, Lua os.clock and Python time.process_time are CPU time, Ruby Time.now is wall time); the current .py scripts call time.process_time (changed by PR #844 in 2021), which Python 2.7 does not have, so the page's Python 2.7.5 rows cannot be reproduced with today's scripts; DeltaBlue exists only for Wren, Python and Dart (delta_blue.lua.inprogress), so its win is over Python only.
- The map_numeric benchmark is not like-for-like against Lua: the Lua script fills keys 1..2,000,000 in order, which Lua stores in a table's array part, while Wren uses its hash Map.
- A refreshed performance page with modern baselines (PR #1164 by asb, Ryzen 9 5950X, median of 10, Lua 5.4.4, LuaJIT 2.1.0-beta3, Python 3.11.3, Ruby 3.0.5) has been open and unreviewed since 2023-04-10; it keeps Wren's method-call and DeltaBlue wins but shows Wren slowest on binary trees and behind Lua 5.4 and Ruby 3.0 on Fibonacci.
- The embedding API is unchecked in release builds (wrong slot or argument counts are undefined behaviour), calling a Wren method handle from inside a foreign method is an open issue (#1169), and hard limits apply: 16 parameters per method, 255 fields per class, 65,536 module variables (wren_common.h).

## Known shortcomings

- doc/site/performance.markdown numbers date from about 2014 (Lua 5.2.3, Python 3.3, Ruby 2.0) with no CPU model or flags, and LuaJIT -joff beats Wren on binary trees and fib (rows the record left out).
- Enricher: an independent modern re-run (asb, PR #1164, open since 2023-04-10; Ryzen 9 5950X, median of 10; Lua 5.4.4, Python 3.11.3, Ruby 3.0.5) keeps Wren's method-call win (0.079 vs Lua 0.121 s) and DeltaBlue over Python (0.086 vs 0.107 s) but has Wren slowest on binary trees (0.141 vs Lua 0.139, Ruby 0.116) and behind Lua 5.4 on fib (0.148 vs 0.087 s); discussion #1183 (i7-12700H, Lua 5.4.6) agrees that Wren wins only method_call, so the broad claim holds only against 2014 baselines. The page mixes clocks (Ruby wall, others CPU), the Python 2.7.5 rows are not reproducible with today's scripts, and map_numeric's Lua uses the array part rather than a hash. Five fuzzer memory-safety bugs open (#1217-#1221); no stack-overflow check (#939).

## Caveats and trade-offs

Old first-party numbers (undated page; baselines are Lua 5.2.3, LuaJIT 2.0.2, Python 2.7.5/3.3.4 and Ruby 2.0.0, i.e. about 2014) on the author's laptop with no compiler, flags or CPU model stated; modern Lua 5.4, CPython 3.11+ and Ruby 3.x are faster, so the margins are likely smaller today. LuaJIT in interpreter mode (-joff) beats Wren on binary trees (0.11 s vs 0.22 s) and Fibonacci (0.10 s vs 0.20 s); DeltaBlue is compared only with Python. Development is slow: the 2025-11-19 commits are a merged PR (#1194, method-limit checks) plus CI edits, and the previous commits are from 2025-03. [retier] Wins only method dispatch against current baselines (discussion #1183 on an i7-12700H with Lua 5.4.6 agrees); the original page's broad wins are against about 2014 interpreters with no CPU model or flags, mixed clocks (Ruby wall, others CPU), Python 2.7.5 rows not reproducible with today's scripts, map_numeric's Lua using the array part rather than a hash, and LuaJIT -joff beating Wren on binary trees and fib. Five fuzzer memory-safety bugs open (#1217-#1221); no stack-overflow check (#939).

Small class-based language (VM under 4,000 lines); NaN-tagged values, fixed object layout, copy-down inheritance; classes cannot be modified at runtime; compiles as C99 or C++98 and later, embeddable through a C API.

## Maintenance

Slow-moving but not abandoned: latest release still 0.4.0, commits only in February-March 2025 and November 2025 after a gap since September 2022, MIT and easy to vendor; the headline speed claim holds only against the old baselines and should be narrowed to method dispatch against current Lua, Python and Ruby.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** doc/site/performance.markdown shows the author's timings against Lua 5.2.3, LuaJIT 2.0.2 -joff, Python 2.7.5/3.3.4 and Ruby 2.0.0, and the harness and per-language benchmark programs are public in test/benchmark, but the page gives no compiler or flags and only '2.3 GHz Intel Core i7' (no CPU model), so first-party with partial methodology.
- **Retiered** C to B: C to B on an independent modern re-run (asb, PR #1164, Ryzen 9 5950X, median of 10 against Lua 5.4.4, Python 3.11.3 and Ruby 3.0.5), which narrows the claim to method dispatch: Wren wins method_call and DeltaBlue over Python but is behind Lua 5.4 on fib and slowest on binary trees.
- **Verifier notes:** All Wren, Lua, Ruby and Python numbers in the record match the page; the record omitted the LuaJIT -joff rows for method call and Fibonacci, now added. Metadata checked: MIT, 8.1k stars, default branch main, last commit 2025-11-19 (within 12 months, so active), test/benchmark holds matching .wren/.lua/.py/.rb programs.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`, `benchmark_url`, `baseline`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/doc/site/performance.markdown>
  - <https://github.com/wren-lang/wren>
  - <https://github.com/wren-lang/wren/commits.atom>
  - <https://github.com/wren-lang/wren/tree/main/test/benchmark>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/README.md>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/doc/site/performance.markdown>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/doc/site/embedding/index.markdown>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/util/benchmark.py>
  - <https://github.com/wren-lang/wren/tree/main/test/benchmark>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/README.md>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/method_call.wren>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/method_call.lua>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/method_call.py>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/method_call.rb>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/fib.wren>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/fib.lua>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/fib.py>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/fib.rb>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/binary_trees.wren>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/binary_trees.lua>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/binary_trees.py>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/binary_trees.rb>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/map_numeric.wren>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/map_numeric.lua>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/test/benchmark/map_numeric.py>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/src/vm/wren_core.c>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/src/vm/wren_common.h>
  - <https://raw.githubusercontent.com/wren-lang/wren/HEAD/src/include/wren.h>
  - <https://github.com/wren-lang/wren/issues?q=is%3Aissue+is%3Aopen+crash>
  - <https://github.com/wren-lang/wren/issues/939>
  - <https://github.com/wren-lang/wren/commits/main>
  - <https://github.com/wren-lang/wren/releases>
  - <https://github.com/wren-lang/wren/discussions/1183>
  - <https://github.com/wren-lang/wren/pulls?q=is%3Apr+benchmark>
  - <https://github.com/wren-lang/wren/pull/1164>
  - <https://github.com/wren-lang/wren/pull/1164/files>
  - <https://raw.githubusercontent.com/asb/wren/update-benchmarks/doc/site/performance.markdown>
  - https://muxup.com/2023q2/updating-wrens-benchmarks (EGRESS_BLOCKED; search snippets only, superseded by the branch file above)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wren-lang/wren`) · [data/wave12/enrich/raw/github_com_wren_lang_wren.json](../../../data/wave12/enrich/raw/github_com_wren_lang_wren.json) (enrichment confidence 0.8)

</details>
