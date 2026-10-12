# s7 Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `0BSD` · 🟡 stale

> Single-file embeddable Scheme interpreter (s7.c + s7.h); ran recursive fib(34) about 4.5x faster than Duktape 1.2.2 in Scriptorium 2015.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (the copy vendored in scriptorium's javascript/duktape; PUC Lua at 1.341 s in the same table is faster than s7) |
| **Claimed result** | 2.136 s versus Duktape 1.2.2 at 9.544 s, about 4.5x faster than Duktape (derived from page data); s7 was timed only once, in a later session than that Duktape row, and the later unlabelled Duktape runs of 9.06 to 9.71 s give about 4.2x to 4.5x (derived from page data). Slower than PUC Lua at 1.341 s (about 1.6x, derived from page data). |
| **Workload** | Recursive fibonacci test (tests/fib.\*) run as a separate process through the repo's bench.exe, wall time including process start-up averaged over 5 runs, July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | MSVC (VS2015 RC where possible, VS2013 elsewhere), static CRT; scheme/s7/make.bat builds s7 with /Ox /Oy /MT /DNDEBUG /DWITH_MAIN and javascript/duktape/make.bat builds Duktape with /Ox /Oy /MT /DNDEBUG |
| **Adoption** | 1 star (unofficial mirror); upstream is the Snd/CCRMA project, used by Snd, Common Music and Scheme for Max |
| **Last commit** | 2024-04-16 |
| **Links** | [repository](https://github.com/aboalang/s7) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

In r-lyeh's Scriptorium (July 2015, AMD A10 3.8 GHz, Windows 7 64-bit, MSVC VS2015 RC or VS2013, both engines built /Ox /Oy /MT /DNDEBUG), whole-process time for recursive fib(34), averaged over 5 launches, was 2.136 s for s7 3.31 versus 9.544 s for Duktape 1.2.2, about 4.5x (derived from page data; 4.2x to 4.5x against Duktape's other runs); PUC Lua at 1.341 s was about 1.6x faster than s7.

## Use it when

- A C or C++ application (especially audio or music software: Snd, Common Music, Scheme for Max/Pd, Radium all embed it) that wants Lisp/Scheme as its scripting layer and a two-file drop-in with no required dependencies.
- Several isolated interpreters in one process: each s7_init instance is independent, and the docs show 16 instances running in 16 pthreads.
- Numeric script code where you can register typed C fast paths (s7_set_d_dd_function and friends) so the optimizer calls them on unboxed doubles.
- Replacing a 2015-era Duktape 1.x on call-heavy script code where a Lisp syntax is acceptable to your users.

## Skip it when

- Raw interpreter speed is the priority: in the same Scriptorium table PUC Lua (1.341 s), Chibi-Scheme (1.009 s) and LuaJIT with the JIT off (0.521 s) beat s7 (2.136 s) on fib(34).
- Your users expect JavaScript or Lua, or you need syntax-rules / hygienic macros (s7 has only define-macro and says its macros are not hygienic).
- Scheme-level threads sharing one heap: removed in 2011; one interpreter per thread only.
- You need a reviewed, issue-tracked GitHub project: this repo is a 1-star, manually updated mirror; development, bug tracking and releases happen on CCRMA's cm-gitlab and in Snd tarballs.
- Builds where compile time or binary size matter: s7.c is one roughly 3.8 MB C file (the source notes a 49-second compile in 2022).

## How it is fast

There is no bytecode compiler: s7 walks the list structure, but an optimizer annotates each expression in place with a specialised opcode and direct C function pointers (the fx_\* and opt_info paths), so safe calls with constant, symbol or nested safe arguments skip the general eval loop and, in numeric code, can work on unboxed s7_int and s7_double values. Cells come from a pre-allocated heap of fixed-size cells popped off a free list and reclaimed by a mark-and-sweep GC. Current s7 also has pattern-specific recursion ops (for example OP_RECUR_IF_A_A_opLA_LAq) that run fib-shaped functions as native C recursion over unboxed integers; the 2015 copy that was benchmarked has none of these (no OP_RECUR code in the vendored s7.c).

## Compared with alternatives

Pick s7 over Chibi-Scheme when you want a single-file drop-in with first-class environments, define-macro and typed C fast paths for numeric/DSP code, or the CCRMA audio ecosystem; pick Chibi (1.009 s vs 2.136 s on the same table, R7RS with syntax-rules) when standards conformance or interpreter speed matter more, and Lua or Luau when users expect a conventional scripting syntax.

## Integration

| | |
|---|---|
| **Form** | source-drop (s7.c + s7.h compiled into your program); optional WITH_MAIN standalone REPL |
| **Dependencies** | none (libm; optional gmp, mpfr and mpc with WITH_GMP; dlopen for WITH_C_LOADER) |
| **Minimum toolchain** | C compiler with setjmp.h; the source says it no longer compiles with gcc 4.3 and that g++ 4.4 is too old; also compiles as C++ (HAVE_COMPLEX_TRIG 0) and with MSVC (both complex switches 0); exact minimum not documented |
| **Platforms** | Linux, macOS, FreeBSD/NetBSD/OpenBSD, Windows (MSVC, mingw, msys2), tcc, WebAssembly; 64-bit assumed by default (SIZEOF_VOID_P 4 for 32-bit) |
| **Thread safety** | Each s7_scheme instance is independent and may run in its own thread; a single instance must not be shared between threads (Scheme-level threads were removed in August 2011). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness limits behind the 4.5x: Scriptorium's bench.exe times five whole-process system() launches (start-up included) and never checks the printed result; s7 has a single bench.csv row (2.13558 s, s7 3.31 of 16-Jul-15 built with cl /Ox /Oy /MT /DNDEBUG /DWITH_MAIN) from a later session than Duktape's 9.544 s row, and the README keeps each engine's minimum across sessions. The test is one fib(34) micro-benchmark on Duktape 1.2.2, which is much older than Duktape 2.x.
- The measured binary is eleven years older than the code you would vendor today: current s7 adds pattern-matched recursion ops that turn exactly this kind of if-shaped fib into native C recursion (s7.html claims fib(40) in 0.8 s, 'approximately the same as sbcl'), so a fib benchmark of current s7 would test a special case rather than general interpreter speed; whether the two-clause cond form in Scriptorium's tests/fib.scm hits those ops was not determined (the cond variant with two recursive calls in the source needs a four-element cond).
- Errors longjmp out of s7 calls (s7_error unwinds the Scheme stack, then longjmps the C stack), so C++ frames between your entry point and a failing s7 call skip their destructors; values held in C across allocating calls must be protected with s7_gc_protect or the \*_via_stack variants.
- With MSVC (and tcc) HAVE_COMPLEX_NUMBERS is 0, and the docs warn that complex functions then become stubs that return their argument, so (sqrt -2) can return something bogus without an error; non-gmp builds use fixed 64-bit s7_int.

## Known shortcomings

- One 2015 scriptorium fib(34) run (2.136 s vs Duktape 1.2.2, about 4.5x), single s7 run, slower than Lua; the repo is an unofficial 1-star mirror stale since 2024-04-16 while upstream s7 (in Snd, snd-26.7, 2026-09-07, at cm-gitlab.stanford.edu/lib/s7, blocked here) is active. Engines built with /Ox /Oy /MT /DNDEBUG, CPU model and compiler version unstated.
- Enricher: the benchmarked 2015 s7 3.31 has no OP_RECUR code while current s7 adds fib-shaped recursion ops (OP_RECUR_IF_A_A_opLA_LAq, native C recursion over unboxed ints; s7.html claims fib(40) in 0.8 s), so a rerun on current s7 would time a special case; the s7 row is one bench.csv line (85) from a later session than Duktape's 9.544 s. MSVC build has complex-number stubs; errors longjmp past C++ destructors.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) of s7 3.31 (S7_DATE 16-Jul-15 in the vendored s7.h) on one recursive-fib(34) test; the author says 'Take it with a grain of salt'. bench.exe times whole processes with system() (start-up included), averages 5 launches, never checks the output, and the README table keeps the minimum over separate sessions; s7 has a single bench.csv row while Duktape ranges from 9.06 s to 14.3 s across sessions. Duktape 1.2.2 is much older than current Duktape 2.x releases, and PUC Lua (1.341 s in the same table) is faster than s7. The repo URL is an unofficial, occasionally hand-updated 1-star mirror of the official cm-gitlab.stanford.edu/lib/s7 repository (host blocked here, not opened); the mirror's last commit is 2024-04-16 (s7 10.8, 17-Apr-2024), while upstream s7 ships inside Snd, whose latest SourceForge release is snd-26.7 (2026-09-07). The 2015 s7.c said 'apparently tinyScheme is under the BSD license, so I guess s7 is too'; the current s7.c carries SPDX 0BSD and the mirror's LICENSE file reads '0-clause BSD'.

Scheme (R5RS/R7RS-leaning) interpreter with a single C file and header to embed; not Lua-like.

## Maintenance

The upstream s7 is actively developed by its author at CCRMA (Snd 26.7 released 2026-09-07) and is 0BSD, so copyable, but this GitHub mirror stopped at s7 10.8 (17-Apr-2024) and the only speed evidence is one 2015 fib micro-benchmark of a version that predates most of the current optimizer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, public-domain harness bench.cc + run.bat + tests/fib.scm + tests/fib.js + scheme/s7/make.bat) whose row 21 shows s7 2.136 s against Duktape 9.544 s (row 32) on fib(34); not A because the CPU is given only as 'AMD A10 3.8 GHz' (no model number) and the compiler is 'VS2015 RC if possible, VS2013 elsewhere'. Same tier as the other scriptorium verdicts.
- **Verifier notes:** Numbers match README row 21 and bench.csv line 85 exactly; s7 and Duktape used the same /Ox /Oy /MT /DNDEBUG flags (record's 'per-engine flags not stated' corrected). Metadata on github.com: mirror repo, 1 star, LICENSE 0BSD, last commit 2024-04-16 (stale for the mirror; upstream active per snd-26.7 on SourceForge). Consider a repo_url override to the official https://cm-gitlab.stanford.edu/lib/s7 (unverified here, host blocked); shortcomings: one 2015 fib test, beats only Duktape 1.2.2, about 1.6x slower than PUC Lua, single s7 run, unofficial mirror.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.scm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/scheme/s7>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/s7/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/s7/s7.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/s7/s7.c>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/javascript/duktape>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/aboalang/s7>
  - <https://github.com/aboalang/s7/commits>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/s7.c>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/s7.h>
  - <https://sourceforge.net/projects/snd/files/snd/>
- **Sources the enricher read:**
  - <https://github.com/aboalang/s7>
  - <https://github.com/aboalang/s7/commits>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/README.md>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/s7.h>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/s7.c>
  - <https://raw.githubusercontent.com/aboalang/s7/HEAD/s7.html>
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.scm>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/s7/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/scheme/s7/s7.c>
  - <https://sourceforge.net/projects/snd/files/snd/>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/aboalang/s7`) · [data/wave12/enrich/raw/github_com_aboalang_s7.json](../../../data/wave12/enrich/raw/github_com_aboalang_s7.json) (enrichment confidence 0.75)

</details>
