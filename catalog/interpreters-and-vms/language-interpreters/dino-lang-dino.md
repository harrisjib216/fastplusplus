# Dino

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-or-later (DINO interpreter sources; COPYING is GPLv2) and LGPL-2.0-or-later (AMMUNITION library sources; COPYING.LIB is the Library GPL v2)` · 🔴 abandoned

> Research scripting language and VM in C (RTL bytecode, type-inferred specialization, GCC-based JIT); beats Python 3.4 and Ruby 2.1 interpreters.

| | |
|---|---|
| **Beats** | Python 3.4.x and Ruby 2.1.x (also PyPy 2.2.x, SpiderMonkey 1.8.x, Scala 2.10.x, OCaml 4.0.x) |
| **Claimed result** | 2016 README tables (Dino 0.98, Python 3.4, Ruby 2.1), relative times with plain Dino (no hints) as the fair reference: Loop Python 257 vs Dino 19 (13.5x), Fact 90.4 vs 13.2 (6.8x), Fib 492 vs 112 (4.4x), Method 5.8 vs 1.0, Object 4.4 vs 1.0, Sieve 37.9 vs 1.0, Thread 125 vs 1.0, Hash 2.4 vs 1.0; Ruby 157/25.2/142/1.5/1.4/4.5/43.6/2.2. The 'Dino best' rows for Fact and Fib use !pure result caching and are not comparable. PyPy beats plain Dino on 8 of 14 x86-64 benchmarks (derived from page data). |
| **Workload** | Old computer-language-shootout style programs (loop, hash, fact, fib, exceptions, method calls, object creation, sieve, sort, statistics, random, threads, startup, compile) on x86-64, AARCH64, ARM and PPC64; times are relative to Dino's best result = 1.0. |
| **Metric** | throughput |
| **Hardware** | x86-64 i5-4670 3.4 GHz Haswell; also AARCH64 (X-Gene), ARM (Exynos 5410 1.6 GHz Cortex-A15), PPC64 (3.5 GHz Power7) |
| **Compiler and flags** | Not stated. |
| **Adoption** | 129 stars |
| **Last commit** | 2019-11-19 |
| **Links** | [repository](https://github.com/dino-lang/dino) · [benchmark](https://github.com/dino-lang/dino/blob/master/README.md) |

## Verdict

First-party April 2016 README tables (Dino 0.98 dev; x86-64 i5-4670 Haswell, plus X-Gene, Exynos 5410 and Power7) give user CPU times relative to Dino's best variant, on old shootout-style programs run by DINO/compare.tst. Plain Dino without hints beat Python 3.4.x by 13.5x on loop, 6.8x on fact, 4.4x on fib and 37.9x on sieve, and Ruby 2.1.x by 8.3x, 1.9x, 1.3x and 4.5x (derived from page data). PyPy 2.2 was faster than plain Dino on 8 of 14 x86-64 benchmarks.

## Use it when

- Studying or porting interpreter techniques into your own VM (RTL bytecode, superinstructions, type-inference-driven specialization, a JIT that emits C for GCC); the preprint's ablation table shows what each step bought.
- Integer loop and array-heavy scripts: on x86-64, plain Dino without hints was 13.5x faster than Python 3.4 on an empty loop and 37.9x faster on sieve (derived from page data).
- Producer-consumer concurrency on one core: green-thread fibers took 1/125 of Python's time and 1/43.6 of Ruby's on the thread benchmark.
- Tools that start the interpreter often or load huge generated scripts: startup was 10.9x faster than Python and 29.4x faster than Ruby, and compiling a very long assignment list was 3.3x faster than Python.

## Skip it when

- Production use: development stopped in 2019, there is no release after the 0.98 development snapshot (issue #21, 'When release a new version?', is open), and build issues remain open (#13 ONIGURUMA/missing, #12 -liconv on Darwin).
- Object-heavy or call-heavy code against a tracing JIT: PyPy 2.2 beat plain Dino on 8 of 14 x86-64 benchmarks (method 0.2, object 0.1, fact 0.4 relative to Dino's best run).
- Code that needs the Python or Ruby ecosystem; Dino is its own language with a small standard library.
- Proprietary embedding: the interpreter is GPL-2.0-or-later (only the AMMUNITION support library is LGPL), and an embedding API is not documented.
- Multi-core parallelism: fibers are green threads; OS threads without a GIL are listed only as a plan.

## How it is fast

Bytecode is register-based with multi-operand instructions (RTL) rather than a stack machine. Instruction combining fuses common sequences: add, compare and branch becomes a single `btltinc`. With `-O`, a whole-program type inference pass builds a CFG, def-use chains and forward data-flow, then specializes generic instructions into typed ones (add into iadd or fadd) that skip operand type checks. Optional per-function hints add inlining (`!inline`), result caching for pure functions (`!pure`), and a function-level JIT (`!jit`) that turns bytecode into C and compiles it with GCC on first call. In the preprint's ablation on a six-deep nested loop (i7-4790K), CPU time drops from 6.51 s for a stack VM to 2.12 s with RTL, 1.38 s with combining, 0.61 s with JIT and 0.14 s with type inference and specialization. Memory management combines mark-and-sweep with a mark-and-copy collector and uses simple escape analysis to move heap allocations onto the stack.

## Compared with alternatives

For an embeddable, permissively licensed fast interpreter, choose Wren (MIT; it beats Lua 5.2, Python 3.3 and Ruby 2.0 on its own suite) or LuaJIT. For raw speed on dynamic code, choose PyPy, which beats plain Dino on most object and call benchmarks. Pick Dino only as a reference implementation of RTL bytecode plus type-inferred specialization and a GCC-emitting JIT, or if you specifically want its language features.

## Integration

| | |
|---|---|
| **Form** | built interpreter (autotools configure and make, plus `make install`); C functions plug in as shared objects (-L option) or as inline `%{ %}` C blocks compiled at run time |
| **Dependencies** | GMP; bundled Oniguruma 6.0.0 regexp library and the COCOM tools (SPRUT, MSTA, SHILKA, AMMUNITION) in the same repo; a C compiler (GCC) at run time for `!jit` functions and inline C |
| **Minimum toolchain** | not documented; configure targets GCC (adds -Ofast, or -O3 as a fallback, plus -flto when supported); the preprint used GCC 4.9.2 for JIT compilation on Fedora Core 21 |
| **Platforms** | Linux, Windows via Cygwin, macOS (Xcode and GMP needed); benchmarked on x86-64, AArch64, 32-bit ARM and PPC64 |
| **Thread safety** | Fibers are green threads scheduled by the interpreter; simple statements are atomic and there is a `wait (cond)` statement; no OS-thread parallelism. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the README tables: the 'Dino best = 1.0' row for fact and fib uses the `!pure` hint, which caches arguments and results of pure-function calls (preprint section 3.3.2; the manual defines the hint). fact(12) repeated N times and naive fib then become cache lookups, while Python, Ruby and PyPy run the full recursion. Only the plain Dino row is like-for-like, and its ratios have to be divided out: Python vs plain Dino on fib is 492/112 = 4.4x, not 492x (derived from page data).
- DINO/compare.tst times each variant once with `time -p` and records user CPU time only. System time is ignored, helper threads in other runtimes add to their user time, and Dino's base is the minimum over plain, `-O` and hinted variants. Which of plain or `-O` produced the README's plain Dino row is not stated.
- Default GCC builds use -Ofast (which implies -ffast-math) plus -flto (DINO/configure.ac), so the interpreter's own float arithmetic is not guaranteed IEEE-strict; the compiler version behind the 2016 tables is not stated.
- `!jit` invokes a C compiler on a function's first call (the README says 50-70 ms for a small function) and writes temporary C and object files (to /tmp per the manual), so short scripts pay that cost and target machines need GCC installed.

## Known shortcomings

- First-party README tables from 2016 (Python 3.4, Ruby 2.1) with the build compiler and flags unstated; PyPy beats plain Dino on 8 of 14 x86-64 benchmarks (the record's PyPy claim understated this), Python wins fact and hash on ARM and Ruby wins loop on PPC64. The companion dino.pdf is an arXiv preprint, not peer-reviewed. Abandoned since 2019-11-19; GPL-2.0-or-later plus LGPL-2.0-or-later.
- Enricher: the 'Dino best = 1.0' rows for fact and fib use !pure, which caches pure-function results (preprint section 3.3.2), so the best run does a cache lookup while the other implementations run the full recursion; the plain-Dino row is the fair one (Python vs plain Dino on fib 492/112, about 4.4x, not 492x). compare.tst does one run per variant, user CPU time only, with the base taken as the minimum over plain, -O and hint variants; the default build uses -Ofast (implies -ffast-math) plus -flto.

## Caveats and trade-offs

Results are from a 2016 README slide deck (version 0.98 development) on Python 3.4 and Ruby 2.1; numbers are relative to Dino's best run, not seconds. Dino's best row uses JIT, pure-function and inline hints; the plain row is quoted here. PyPy is faster than plain Dino on 8 of 14 benchmarks on x86-64. On AARCH64 Python 2.7.5 was used (Python 3 absent) and Python wins hash (0.5 vs 1.7); on ARM Python beats plain Dino on fact (4.4 vs 18.1) and hash (0.6 vs 1.0); on PPC64 Ruby beats plain Dino on loop (17.6 vs 23.2). The thread benchmark compares Dino green threads with GIL-bound OS threads. The benchmark driver is DINO/compare.tst (shell script, old shootout programs); compiler version and flags for the interpreter build are not stated. The companion arXiv preprint (dino.pdf in dino-lang/implemenation-article, dated 2016/4/5) has a variant table on Python 3.3.x and Ruby 2.0.x with different numbers (e.g. x86-64 loop Python 416, Ruby 237), Fedora Core 21, and GCC 4.9.2 used only for JIT compilation. Author is a GCC maintainer; repo dormant since 2019-11-19. [retier] First-party 2016 tables from DINO/compare.tst: one run per variant, user CPU time only, base taken as the minimum over the plain, -O and hint variants; the Fact and Fib best rows use !pure, which caches pure-function results (preprint section 3.3.2), so the best run does a cache lookup while Python and Ruby run the full recursion. Default build is -Ofast (implies -ffast-math) plus -flto. Python wins fact and hash on ARM, Ruby wins loop on PPC64. Abandoned since 2019-11-19; GPL-2.0-or-later plus LGPL-2.0-or-later.

Dynamically typed scripting language with an optimizing bytecode interpreter, mark-and-sweep plus mark-and-copy GC, optional function-level JIT through C code generation, type inference, fibers and a C FFI; its own language, not source compatible with Python or Ruby.

## Maintenance

Abandoned since 2019-11-19 (129 stars, 10 open issues including build failures) and GPL-2.0-or-later. Useful as readable reference code for interpreter design rather than as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README slide deck (Apr 2016) gives relative-time tables against Python 3.4.x and Ruby 2.1.x with CPU models named, and the benchmark driver DINO/compare.tst is public, but the compiler version and flags used to build the interpreter are not stated, so not A. The companion paper (dino-lang/implemenation-article, dino.pdf) is the author's own arXiv preprint, not peer-reviewed, so not B.
- **Verifier notes:** All quoted x86-64 numbers match the README table; the PyPy statement understated where PyPy wins and is corrected. License tightened from file headers (GPL-2.0-or-later interpreter, LGPL-2.0-or-later AMMUNITION library). Metadata confirmed: 129 stars, not archived, not a fork, last commit 2019-11-19 (abandoned).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dino-lang/dino>
  - <https://github.com/dino-lang/dino/commits>
  - <https://raw.githubusercontent.com/dino-lang/dino/HEAD/README.md>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/compare.tst>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_dino.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/AMMUNITION/allocate.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/COPYING>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/COPYING.LIB>
  - <https://github.com/dino-lang/implemenation-article>
  - <https://raw.githubusercontent.com/dino-lang/implemenation-article/master/dino.pdf>
- **Sources the enricher read:**
  - <https://github.com/dino-lang/dino>
  - <https://github.com/dino-lang/dino/issues>
  - <https://github.com/dino-lang/dino/tree/master/DINO>
  - <https://raw.githubusercontent.com/dino-lang/dino/HEAD/README.md>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/compare.tst>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/dino.txt>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/configure.ac>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_gen.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_eval.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_func.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_heap.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_dino.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_main.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_runtab.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_conv.c>
  - <https://raw.githubusercontent.com/dino-lang/dino/master/DINO/d_context.c>
  - <https://raw.githubusercontent.com/dino-lang/implemenation-article/master/dino.pdf>
  - <https://github.com/vnmakarov/ruby/tree/rtl_mjit_branch>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dino-lang/dino`) · [data/wave12/enrich/raw/github_com_dino_lang_dino.json](../../../data/wave12/enrich/raw/github_com_dino_lang_dino.json) (enrichment confidence 0.7)

</details>
