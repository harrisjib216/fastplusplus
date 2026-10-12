# pocketlang

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Tiny embeddable C99 bytecode VM with Ruby-flavoured Python syntax; roughly CPython speed, well behind Lua 5.3.

| | |
|---|---|
| **Beats** | CPython (version unstated in issue #140) and Lua 5.3.4; the README chart (image only) compares against CPython 3.7.4, Ruby MRI 2.7.2 and Wren 0.3.0 |
| **Claimed result** | Issue #140 (third-party run, 2021-06-25), pocketlang vs Python seconds: factors 4.00 vs 5.27 (1.32x faster), fib 3.04 vs 3.03 (parity), list 2.88 vs 2.59 (0.90x, slower), loop 1.23 vs 2.20 (1.79x faster), primes 3.74 vs 2.91 (0.78x, slower) (ratios derived from page data). Lua 5.3.4 was 3.2x to 6.8x faster than pocketlang on every benchmark. The README's own bar chart (pocketlang pre-alpha vs Wren 0.3.0, Python 3.7.4, Ruby 2.7.2) could not be read here. |
| **Workload** | Five benchmark programs in tests/benchmarks/ (factors, fib, list, loop, primes; a tco directory exists but is not in the runner list) run by scripts/run_benchmarks.py, which times each interpreter via the 'elapsed: &lt;time&gt;s' line each script prints; Node.js is deliberately excluded from the runner. |
| **Metric** | throughput |
| **Hardware** | Unstated for the issue #140 numbers; the README chart was run on Windows 10 64-bit, ASUS N552VX, Intel Core i7-6700HQ 2.6GHz, 12GB RAM |
| **Adoption** | 1.5k stars, 361 commits |
| **Last commit** | 2026-01-03 |
| **Links** | [repository](https://github.com/ThakeeNathees/pocketlang) · [benchmark](https://github.com/ThakeeNathees/pocketlang/issues/140) |

## Verdict

A third-party run in issue #140 (2021-06-25, the day after the benchmark scripts were last changed; no hardware, Python version or pocketlang build mode given) timed the repo's five scripts: pocketlang beat CPython on factors (4.00 s vs 5.27 s) and loop (1.23 s vs 2.20 s), tied on fib (3.04 vs 3.03) and lost on list (2.88 vs 2.59) and primes (3.74 vs 2.91), while Lua 5.3.4 took 0.39 to 0.95 s on every test. The README's own chart (pre-alpha pocketlang vs Wren 0.3.0, Python 3.7.4, Ruby 2.7.2 on an i7-6700HQ under Windows 10) is an image that could not be read here (user-images.githubusercontent.com blocked).

## Use it when

- Embedding a small scripting layer in a C or C++ host where a single dependency-free C99 source tree (cli/, src/core/, src/libs/) is the main requirement and CPython-class speed is acceptable.
- Configuration, glue or game-logic scripts where users expect Python/Ruby-like syntax rather than Lua's.
- Tail-recursive code: TAIL_CALL reuses the caller's frame, so deep tail recursion does not grow the stack.
- Browser demos or sandboxes via the existing Emscripten/WebAssembly build.
- Teaching or studying a compact Crafting-Interpreters-style VM (about 12k lines in src/core) that you are willing to own and patch.

## Skip it when

- When you need more speed than CPython: in the only readable numbers (issue #140) it was slower than Python on list and primes, tied on fib, and Lua 5.3.4 was 3.2x to 6.8x faster on all five benchmarks.
- Integer-heavy code: all numbers are doubles, % is fmod, and integers are exact only up to 2^53.
- Running untrusted scripts: open issue #302 (2026-02-11) reports a heap-buffer-overflow in pkByteBufferAddString on an unterminated string, a NULL function-pointer call in parsePrecedence and a crash in varContains, with no maintainer reply.
- Projects that need a maintained runtime: feature work stopped in June 2022, the 'Abandoned?' issue #298 (2024) has no reply, 30 issues and 28 PRs are open, and the language is still version 0.1.0.
- Large scripts: the compiler caps a scope at 256 variables, 256 upvalues and 256 break statements, and global indices are single bytes.

## How it is fast

Values are NaN-boxed 64-bit words (VAR_NAN_TAGGING on by default in internal.h), so numbers, booleans and null need no heap allocation. The compiler emits a stack-based bytecode with single-byte operands, and locals and module globals are read and written by array index (PUSH_GLOBAL/STORE_GLOBAL index into module-&gt;globals), not by name lookup. Return-position calls compile to TAIL_CALL so tail recursion reuses the frame. Dispatch is a plain switch inside a goto loop (no computed goto), arithmetic goes through out-of-line varAdd/varModulo helpers, and every number is a double (the integer tag is defined but unused), so there is no special integer fast path.

## Compared with alternatives

Pick it over Wren or pocketpy only when you specifically want its Ruby-flavoured Python syntax in a few thousand lines of C99 and accept unmaintained code; Wren has an independent re-run showing it ahead of Lua 5.4.4 and CPython 3.11.3, and pocketpy offers real Python syntax with a measured edge over CPython 3.8.10. For speed alone, LuaJIT or stock Lua beat it by a wide margin.

## Integration

| | |
|---|---|
| **Form** | source-drop (Makefile also builds a static lib, libpocketlang.a, and a CLI) |
| **Dependencies** | none (libm and libdl on \*nix; cJSON and cwalk are vendored in src/libs/thirdparty) |
| **Minimum toolchain** | C99 compiler (GCC, Clang, MinGW, MSVC; Emscripten for WebAssembly) |
| **Platforms** | Windows, Linux, macOS (the benchmark runner accepts only these three), WebAssembly; any 64-bit target where NaN-boxed pointers fit in 48 bits |
| **Thread safety** | not documented; state lives in a per-instance PKVM with its own configuration, so separate VMs per thread look feasible but this is untested here |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: factors.py and loop.py run their hot loops at module scope (CPython dict-based global name lookups), while the .pk scripts get index-addressed globals and the .lua scripts use locals; the two benchmarks pocketlang wins against Python in issue #140 (factors 1.32x, loop 1.79x) are exactly these two, and on the three function-bodied benchmarks (fib, list, primes) it ties or loses. The wins likely measure Python's module-scope penalty more than the VM.
- scripts/run_benchmarks.py runs each interpreter once with no repetition or warm-up and trusts each script's self-printed 'elapsed:' line; pocketlang times with C clock() (CPU time on POSIX, wall time under MSVC on Windows, where the README chart was made) while Python uses process_time and Ruby uses Time.now, so the clocks differ by platform. The Lua scripts are not line-for-line ports (loop.lua fills by index instead of appending).
- Build mode matters and is easy to get wrong: plain 'make' builds the Debug target (-Og with DEBUG assertions) and the README's one-line gcc command passes no -O flag; the benchmark runner expects build/Release/bin/pocket from 'make release' (-g -O3). Issue #140 does not say which build it used.
- Range loops ('for i in 2..n') allocate a Range object per loop entry and iterate with doubles; the WebAssembly build disables input, file handling and relative import.

## Known shortcomings

- Evidence is a 2021 third-party run in issue #140 with no hardware, build mode or Python version: mixed vs CPython (loop 1.79x and factors 1.32x faster, fib tie, list 0.90x and primes 0.78x slower); Lua 5.3.4 is 3-7x faster on all five. README chart is an image (blocked here). No code work since 2022-06.
- Enricher: factors.py and loop.py run their hot loops at module scope, where CPython looks globals up by dict, while the .pk scripts index globals by array and the .lua scripts use locals; pocketlang's only two wins in issue #140 are exactly those scripts, so they likely measure Python's module-scope penalty. One run per interpreter, no warm-up, each script's own printed time with different clocks (C clock(), Python process_time, Ruby Time.now). Plain make builds Debug (-Og, asserts) and the README gcc one-liner has no -O flag; issue #140 build mode unknown. Every number is a double, plain switch dispatch. Open unanswered crash reports #302 (heap-buffer-overflow in pkByteBufferAddString) and #298 'Abandoned?'.

## Caveats and trade-offs

Only readable numbers are a 2021 third-party GitHub issue with no hardware, Python version or pocketlang build mode: pocketlang beat CPython on 2 of 5 benchmarks (loop, factors), tied on fib and was slower on list and primes, and Lua 5.3.4 was 3-7x faster than pocketlang on all five. The README chart (pre-alpha pocketlang vs Wren 0.3.0, Python 3.7.4, Ruby 2.7.2, i7-6700HQ) is an image that could not be read here; compiler and flags not stated. Timing comes from each script's self-reported elapsed time, not an external harness. Development effectively stopped in June 2022; the only later commit (2026-01-03) adds native API documentation and build-system changes. [retier] Mixed and probably not faster: in issue #140 pocketlang beats CPython only on factors (1.32x) and loop (1.79x), whose Python ports run hot loops at module scope (dict global lookups) while the .pk scripts index globals by array; fib ties and list (0.90x) and primes (0.78x) lose, and Lua 5.3.4 is 3-7x faster on all five. One run per interpreter, mixed clocks, build mode unknown (plain make builds Debug with -Og). No code work since 2022-06; unanswered crash reports.

Small C99 embeddable bytecode VM (about 3000 semicolons), zero dependencies, NaN-boxing, tail-call optimization, Python and Ruby-like syntax, WebAssembly build for the browser.

## Maintenance

Effectively unmaintained since June 2022 (one 2026-01-03 commit adds native API docs and build changes, and a 2026 memory-safety report is unanswered), but MIT-licensed, dependency-free and small enough to vendor if you are prepared to fix crashes yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the README chart is unreadable here (user-images.githubusercontent.com EGRESS_BLOCKED), but issue #140 (third-party user esrrhs, 2021-06-25) posts per-benchmark seconds from the repo's own benchmark set for pocketlang, Python and Lua 5.3.4; no hardware, Python version or pocketlang build mode, so numbers without methodology, tier C. Benchmark code is public (tests/benchmarks/\*, scripts/run_benchmarks.py).
- **Verifier notes:** Shortcomings: not faster than CPython on 3 of 5 benchmarks in the only readable run (issue #140), Lua 3-7x faster, README chart unreadable and on old versions, no compiler flags. Tier raised D to C on the issue #140 numbers; if the orchestrator prefers the README as the anchor, keep D and carry the issue numbers as a caveat. Metadata checked on github.com: MIT, 1.5k stars, 85 forks, 361 commits, last commit 2026-01-03 (previous 2022-06-14), not archived.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** independent measurement with stated build and versions; function-scoped ports with one clock and a release build
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/README.md>
  - <https://github.com/ThakeeNathees/pocketlang>
  - <https://github.com/ThakeeNathees/pocketlang/commits>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/tests>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/tests/benchmarks>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/tests/benchmarks/fib>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/scripts>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/scripts/run_benchmarks.py>
  - <https://github.com/ThakeeNathees/pocketlang/issues/140>
  - <https://github.com/ThakeeNathees/pocketlang/issues?q=benchmark>
  - <https://github.com/ThakeeNathees/pocketlang/pull/35>
  - <https://github.com/ThakeeNathees/pocketlang/issues/132>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/scripts/run_benchmarks.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/fib/fib.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/fib/fib.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/fib/fib.lua>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/fib/fib.rb>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/fib/fib.wren>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/loop/loop.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/loop/loop.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/loop/loop.lua>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/primes/primes.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/primes/primes.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/primes/primes.lua>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/list/list.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/list/list.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/list/list.lua>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/factors/factors.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/factors/factors.py>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/factors/factors.lua>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/tests/benchmarks/tco/tco.pk>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/vm.c>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/vm.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/value.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/value.c>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/core.c>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/common.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/internal.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/core/compiler.c>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/include/pocketlang.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/libs/std_time.c>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/src/libs/libs.h>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ThakeeNathees/pocketlang/HEAD/docs/README.md>
  - <https://github.com/ThakeeNathees/pocketlang>
  - <https://github.com/ThakeeNathees/pocketlang/commits/master>
  - <https://github.com/ThakeeNathees/pocketlang/commits/master/tests/benchmarks/loop/loop.py>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/src/core>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/tests/benchmarks>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/docs>
  - <https://github.com/ThakeeNathees/pocketlang/tree/master/docs/static>
  - <https://github.com/ThakeeNathees/pocketlang/issues/140>
  - <https://github.com/ThakeeNathees/pocketlang/issues>
  - <https://github.com/ThakeeNathees/pocketlang/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/ThakeeNathees/pocketlang/issues?q=label%3A%22Performance+related%22>
  - <https://github.com/ThakeeNathees/pocketlang/issues/302>
  - <https://github.com/ThakeeNathees/pocketlang/issues/298>
  - https://user-images.githubusercontent.com/41085900/120123257-6f043280-c1cb-11eb-8c20-a42153268a0f.png (EGRESS blocked, 403)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/thakeenathees/pocketlang`) · [data/wave12/enrich/raw/github_com_thakeenathees_pocketlang.json](../../../data/wave12/enrich/raw/github_com_thakeenathees_pocketlang.json) (enrichment confidence 0.6)

</details>
