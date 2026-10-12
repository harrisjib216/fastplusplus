# mruby

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Embeddable lightweight Ruby VM in C; ran a 2015 recursive-fib test 4.5x faster than Duktape 1.2.2, 1.6x slower than PUC Lua.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (the copy vendored in scriptorium's javascript/duktape; PUC Lua at 1.341 s in the same table is faster than mruby) |
| **Claimed result** | 2.098 s versus Duktape 1.2.2 at 9.544 s, about 4.5x faster than Duktape (derived from page data); in bench.csv's earlier session the ratio was about 3.1x (4.641 s vs 14.301 s, derived from page data). Slower than PUC Lua at 1.341 s (about 1.6x, derived from page data). |
| **Workload** | Recursive fibonacci test (tests/fib.\*) run as a separate process through the repo's bench.exe, wall time including process start-up averaged over 5 runs, July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | MSVC (VS2015 RC where possible, VS2013 elsewhere), static CRT; ruby/make.bat builds mruby with /Ox /Oy /DNDEBUG /MT and javascript/duktape/make.bat builds Duktape with /Ox /Oy /MT /DNDEBUG |
| **Adoption** | 5.6k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/mruby/mruby) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

In r-lyeh's scriptorium shootout (July 2015, AMD A10 at 3.8 GHz, Windows 7 64-bit, both engines built with MSVC /Ox /Oy /MT /DNDEBUG), mruby 1.1.x ran recursive fib(34) as a separate process in 2.098 s averaged over 5 launches against 9.544 s for Duktape 1.2.2, about 4.5x faster (derived from page data; 3.1x in an earlier session). PUC Lua took 1.341 s on the same test, so mruby is about 1.6x slower than Lua.

## Use it when

- You want Ruby syntax as the scripting or configuration language of a C/C++ application (game logic, DSLs, device firmware) and can accept interpreter speed in the Lua/Squirrel range rather than LuaJIT's.
- You are on Duktape 1.x and your scripts are call-heavy and integer-heavy; in scriptorium's fib(34) test mruby took 2.098 s against Duktape 1.2.2's 9.544 s.
- Memory-constrained or embedded targets: allocations go through one overridable mrb_basic_alloc_func(), heap regions can be added for fixed memory banks, and bytecode can ship without the compiler (mrbc output plus the compiler-free mruby-bin-mrb runtime).
- Hosts that need to stop runaway scripts: mrb_vm_interrupt() can be called from a signal handler or another thread and raises inside the running script at the next send or jump.

## Skip it when

- Raw interpreter speed is the goal: PUC Lua beat it in the same scriptorium table (1.341 s vs 2.098 s) and LuaJIT, Luau and Terra are far ahead.
- Host-call-heavy embedding: in taksatou/embench (i7-2600S) mruby needed 36.1 ms vs Lua's 15.2 ms for 100000 echo calls and 1260.6 ms vs 505.4 ms for the invert test.
- Code that needs full CRuby compatibility or CRuby gems: many core features come only from optional mrbgems, Array cannot hold instance variables, and a Fiber cannot switch across a C function boundary.
- Running untrusted bytecode or untrusted scripts without a host sandbox: SECURITY.md says .mrb bytecode is not a security boundary and that resource limits (CPU, memory) are the host's job.
- You need JavaScript or its ecosystem: QuickJS or XS are the comparable embeddable choices.

## How it is fast

A register-based bytecode VM (mrb_vm_exec) dispatches with computed goto (direct threading) under GCC, Clang and ICC and falls back to a switch elsewhere, including MSVC. Word boxing keeps Integer, Symbol, true/false/nil and, on 64-bit, Float inside one machine word, so fib-style integer code allocates nothing; specialised opcodes (OP_ADDI, OP_SUBI, OP_ADDILV, OP_LT, OP_SEND0 and others) carry integer fast paths, and method lookups go through a per-state method cache plus a constant cache. The garbage collector is tri-color incremental mark-and-sweep with an optional generational mode; the project states its priority as memory first, then performance.

## Compared with alternatives

Pick mruby when the scripting language should be Ruby: in the same scriptorium run Squirrel (2.126 s), AngelScript (2.039 s) and Lily (2.005 s) landed within a few percent of mruby's 2.098 s, so the choice among them is language, ecosystem and maintenance (mruby is the most actively maintained), not speed. For the fastest small interpreter choose PUC Lua or Luau; for JavaScript choose QuickJS, which beats Duktape 2.3.0 by about 2.3x on bench-v8.

## Integration

| | |
|---|---|
| **Form** | static lib (libmruby built by rake) or single-file amalgamation (rake amalgam: mruby.c + mruby.h) |
| **Dependencies** | Build time: Ruby 2.7+ with rake, and the Prism parser git submodule (clone with --recursive, or rake fetches it); optional C++ compiler only for C++ mrbgems. Runtime: libc and libm. |
| **Minimum toolchain** | A C compiler (GCC, Clang, Visual Studio and Zig toolchains are provided) plus Ruby 2.7+ to drive the build; minimum C standard not documented |
| **Platforms** | any: Linux, macOS, Windows (MSVC), cross-compiled embedded targets; CI covers 32-bit x86 and 32-bit Arm. NaN boxing on 32-bit was only fixed after 4.0 (#6815); word boxing is the default. |
| **Thread safety** | One mrb_state per thread; concurrent use of a single mrb_state is not documented as safe. mrb_vm_interrupt() is the only call documented as safe from another thread or a signal handler. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: scriptorium's bench.exe times whole processes through system() (start-up included, output discarded and never checked, the 'overhead' term is hard-coded to 0) and the README keeps each engine's minimum across non-interleaved sessions; the mruby/Duktape ratio was 3.1x in the first session (4.641 s vs 14.301 s) and 4.5x in the third, and the four unlabelled Duktape runs (9.06-9.71 s) are dropped by the CSV parser because they have two fields instead of three. The ranking comparator (idx::operator&lt;) is not a strict weak ordering, which is undefined behaviour for std::set; the times themselves match bench.csv.
- The 2015 numbers come from an MSVC build, and mruby's vm.c enables computed-goto dispatch only for GCC, Clang and ICC, so the measured mruby used switch dispatch; a GCC/Clang build of today's mruby (4.0.0, April 2026) dispatches differently and has had eleven years of VM changes, so the ratio to Duktape should be re-measured rather than assumed.
- GitHub's auto-generated 'Source code' archives and the master ZIP omit the Prism submodule and do not build; use the release tarballs or git clone --recursive. Post-4.0 master removed the lrama parser and its gemboxes, so build configs that name them break.
- Ruby-level recursion is capped by MRB_STACK_MAX (about 60000 calls in the simplest case) and C-level re-entry by MRB_CALL_LEVEL_MAX (512, or 128 under ASan); performance has regressed between versions before (issue #6369: a 400000-hash allocation script went from 10 s user time on 3.1 to 1013 s on 2024 master, since closed).

## Known shortcomings

- One 2015 scriptorium fib(34) run (2.098 s vs Duktape 1.2.2 at 9.544 s, about 4.5x) with startup counted; about 1.6x slower than PUC Lua there and also slower than Lua in embench. Engines and Duktape built with /Ox /Oy /MT /DNDEBUG, but the CPU model (an AMD A10 at 3.8 GHz) and which of VS2015 RC or VS2013 built which engine are unstated.
- Enricher: scriptorium's bench.exe times whole processes via system(), never checks output, hard-codes the overhead term to 0 and keeps each engine's minimum across sessions (the Duktape ratio is 3.1x in session 1 and 4.5x in session 3); the MSVC build ran mruby with switch dispatch (vm.c enables computed goto only for GCC, Clang and ICC); the current 4.0.0 release (2026-04-20) is unmeasured. Not faster than PUC Lua.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) of mruby (include/mruby/version.h reports 1.1.1) on one recursive-fib(34) test; the author says 'Take it with a grain of salt'. bench.exe times whole processes with system() (start-up included), averages 5 launches, never checks the output, and the README table keeps the minimum over separate non-interleaved sessions (bench.csv has mruby at 4.641 s and 2.098 s, Duktape at 14.30, 10.29 and 9.544 s plus unlabelled Duktape runs of 9.06 to 9.71 s). Duktape 1.2.2 is much older than current Duktape 2.x releases, and PUC Lua (1.341 s in the same table) is faster than mruby. In taksatou/embench (embedding-call overhead, i7-2600S) mruby is slower than Lua on both tests (echo 100000: 36.1 ms vs 15.2 ms; invert 100000: 1260.6 ms vs 505.4 ms).

Ruby subset for embedding with a C API and mrbgems; the language is far from Lua or JavaScript semantics, so the comparison is across languages.

## Maintenance

Actively maintained (commits through 2026-10-06, release 4.0.0 dated 2026-04-20, MIT licensed); the only speed evidence is an eleven-year-old single fib micro-benchmark against an obsolete Duktape 1.2.2 with a harness that times process launches and never checks output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, 525 stars, public-domain harness bench.cc + run.bat + tests/fib.rb + tests/fib.js + ruby/make.bat) whose row 19 shows mruby 2.098 s against Duktape 9.544 s (row 32) on fib(34); not A because the CPU is given only as 'AMD A10 3.8 GHz' (no model number) and the compiler is 'VS2015 RC if possible, VS2013 elsewhere' without saying which built which. Same tier as the chibi-scheme, Pawn, Terra, Neko, TinyVM and c4-jit scriptorium verdicts.
- **Verifier notes:** Numbers match README row 19 and bench.csv line 75 exactly; Duktape and mruby were built with the same /Ox /Oy /MT /DNDEBUG flags, so the record's 'per-engine flags not stated' was wrong and is corrected. Metadata confirmed on github.com: MIT, 5.6k stars, not archived, last commit 2026-10-06. Shortcomings to record: one 2015 fib micro-benchmark, beats only Duktape 1.2.2 and is about 1.6x slower than PUC Lua, start-up included, mruby also slower than Lua in embench.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.rb>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/ruby>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/repl.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/mruby/include/mruby/version.h>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/javascript/duktape>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/mruby/mruby>
  - <https://github.com/mruby/mruby/commits>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/taksatou/embench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/mruby/mruby>
  - <https://github.com/mruby/mruby/commits>
  - <https://github.com/mruby/mruby/issues?q=is%3Aissue+performance>
  - <https://github.com/mruby/mruby/issues/6369>
  - <https://github.com/mruby/mruby/releases>
  - <https://github.com/mruby/mruby/tree/master/benchmark>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/README.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/limitations.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/guides/compile.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/guides/mrbconf.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/guides/memory.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/guides/link.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/internal/architecture.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/doc/internal/boxing.md>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/build_config/default.rb>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/include/mruby.h>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/include/mruby/version.h>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/src/vm.c>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/src/class.c>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/benchmark/vm_dispatch_bench.c>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/benchmark/vm_optimization_bench.rb>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/benchmark/bm_fib.rb>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.rb>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/repl.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/mruby/src/vm.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/ruby/mruby/include/mruby/version.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://raw.githubusercontent.com/taksatou/embench/HEAD/README.md>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/mruby/mruby`) · [data/wave12/enrich/raw/github_com_mruby_mruby.json](../../../data/wave12/enrich/raw/github_com_mruby_mruby.json) (enrichment confidence 0.5)

</details>
