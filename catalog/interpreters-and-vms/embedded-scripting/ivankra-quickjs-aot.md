# QuickJS-AOT (ivankra/quickjs-aot)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> QuickJS fork whose qjsc -A compiles a script's bytecode to C ahead of time; about 1.36-1.43x the stock QuickJS interpreter on V8 suites.

| | |
|---|---|
| **Beats** | QuickJS interpreter ('base' column: commit b226856 of ivankra/quickjs, a bellard/quickjs fork) |
| **Claimed result** | qjsc -A (each bytecode function compiled to C by unrolling the interpreter loop) scores 3518 vs 2582 for the base QuickJS interpreter on the v8-v7 geomean (about 1.36x, derived from page data) and 7784 vs 5425 on v8-v9 (about 1.43x, derived). The best individual cases are about 2.1x (derived): NavierStokes 7946 vs 3710, Crypto 4305 vs 2018, MandreelLatency 33458 vs 16673 and Mandreel 3973 vs 1957; RegExp gains only about 4% and CodeLoad none. Each printed % column is the next column relative to the previous one: the tail-call dispatch branch alone is +8.45% (v8-v7, 2800) and +13.29% (v8-v9, 6146) over base, and qjsc -A is +25.64% and +26.65% over tail-call dispatch. |
| **Workload** | V8 benchmark suites v7 and v9 (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes, PdfJS, Mandreel, Gameboy, CodeLoad, Box2D, zlib, Typescript), score inversely proportional to runtime, median of 20 runs. |
| **Metric** | throughput |
| **Hardware** | Apple Mac M4 running a Debian 13 VM |
| **Compiler and flags** | Generated C compiled with clang -O2 (bytecode exposed as a static const array for constant folding); clang version and the build flags of the base interpreter are not stated |
| **Adoption** | 9 stars |
| **Last commit** | 2025-12-09 |
| **Links** | [repository](https://github.com/ivankra/quickjs-aot) · [benchmark](https://github.com/ivankra/quickjs-aot) |

## Verdict

The README table (Mac M4, Debian 13 VM, median of 20 runs, higher score is faster) gives qjsc -A 3518 vs 2582 for upstream QuickJS commit b226856 on the v8-v7 geomean (1.36x, derived from page data) and 7784 vs 5425 on v8-v9 (1.43x), with tail-call dispatch alone at 2800 and 6146; scores come from the benchmarks' own in-script timers, so compile time is excluded. The harness is probably javascript-zoo's harness/bench.py, which parses the printed scores, but the compiler and flags for the base and tail columns are not stated, and the AOT build omits -fwrapv.

## Use it when

- A fixed, known-at-build-time JavaScript program (CLI tool, embedded script, game logic) that already runs on QuickJS and needs more throughput without a JIT.
- Numeric or loop-heavy code: the README shows the largest gains on NavierStokes (2.14x), Crypto (2.13x), Mandreel and Gameboy (derived from page data).
- Platforms where a JIT is forbidden or unwanted but a C compiler is available at build time.
- As a template for building an AOT compiler for another tail-call-dispatched interpreter: the generator is about 160 lines of C plus a 90-line Python extractor.

## Skip it when

- Code created at run time (eval, new Function, code loaded after the build): it stays interpreted; CodeLoad gained nothing (0.995x) and RegExp-heavy code only about 4%.
- ES modules: aot_compile returns immediately for a module ('TODO: handle modules'), before visiting child functions, so a module input gets no native code at all.
- Production use: it is a 9-star proof of concept from one commit (2025-12-09) on top of the tail-call refactor, with no AOT tests in the Makefile or CI.
- Toolchains without clang's preserve_none and musttail attributes (GCC lacks preserve_none): the opcode extractor needs the tail-call dispatch table, so the build fails.
- When you only need the cheaper part of the gain: the tail-call dispatch branch alone gives +8.45% (v8-v7) and +13.29% (v8-v9), and on zlib it gives nearly all of the 1.56x.

## How it is fast

It is a first Futamura projection: the interpreter is partially specialized for a fixed bytecode input. After the interpreter is refactored into one preserve_none/musttail function per opcode (tail-call dispatch), aot-parse.py extracts each opcode body from the preprocessed quickjs.c, and qjsc pastes the bodies in bytecode order, turning jumps into direct gotos and exposing the bytecode as a static const array so clang can constant-fold operands. That removes dispatch and lets the C compiler optimize across opcodes; the -B mode, which keeps a label at every opcode, gets about half the gain.

## Compared with alternatives

Pick it over plain QuickJS when the script is fixed at build time and a 1.36-1.43x gain on V8-style workloads matters; PrimJS reports a similar 1.29x on Octane but speeds up any code, including eval, as a maintained engine, and gkurt/quickjs (+18% Octane over QuickJS-NG) is an interpreter-only fork, so prefer those when code arrives at run time or production maturity matters.

## Integration

| | |
|---|---|
| **Form** | source-drop (fork of QuickJS; qjsc -A emits C that is compiled into a standalone executable) |
| **Dependencies** | clang at build time (Makefile forces CONFIG_CLANG=y), python3 for aot-parse.py; the generated executable links libquickjsaot.a, -lm, -ldl, -lpthread |
| **Minimum toolchain** | clang with __attribute__((preserve_none)) and musttail support; exact minimum version not documented |
| **Platforms** | Measured only on aarch64 Linux (Mac M4, Debian 13 VM); the tail-call dispatch is disabled on Emscripten; other targets not documented |
| **Thread safety** | not documented (generated code uses the unchanged QuickJS runtime) |
| **Drop-in for the baseline** | partial — same engine and JS semantics, but you ship one native binary per script built from the repo's build tree instead of running scripts with qjs; runtime-loaded code and modules stay interpreted |

## Gotchas

- Build-flag mismatch behind the table: the Makefile adds -fwrapv ('ensure that signed overflows behave as expected') to every interpreter object, but qjsc's compile command for -A is only 'clang -O2 -D _GNU_SOURCE' and the generated file #includes the whole preprocessed engine (quickjs.i), so the AOT column's engine core is built without -fwrapv while the base and tail columns had it; signed-overflow UB in the engine is no longer defined in AOT binaries.
- The README does not say how the base and tail columns were built: the base commit b226856 (Bellard's upstream 'updated to unicode 17.0.0' commit) builds with gcc on Linux by default, the tail-20251204 branch needs -DTAIL_CALL_DISPATCH=1 and clang, and the author's own javascript-zoo QuickJS recipe says clang builds are 'significantly more performant' than gcc and uses -O3, so compiler choice could account for part of the base-to-tail step.
- qjsc -A works only from the build tree: make install copies neither libquickjsaot.a nor quickjs.i. Functions with bytecode shorter than 5 or longer than 10000 bytes are not compiled, a bytecode mismatch silently falls back to the interpreter with a stderr warning, and AOT binaries print 'aot enabled' to stderr.
- The qjs-aot helper caches its binary at /tmp/qjs-aot-&lt;script basename&gt;, keyed only by the file name and content, so concurrent or multi-user runs can collide.

## Known shortcomings

- The search record misread the percentage columns, which compare each column with the previous one: tail dispatch alone is +8.45%/+13.29% over base QuickJS and AOT is +26% over tail dispatch; the best case is NavierStokes 2.14x (derived from page data). The harness is not linked (likely the author's ivankra/javascript-zoo bench/); no clang version stated.
- Enricher: qjsc -A builds with only 'clang -O2 -D _GNU_SOURCE' and the generated C includes the whole engine (quickjs.i), while the Makefile's -fwrapv is present for the base and tail-dispatch columns but missing from the AOT column, so the columns use different flags and signed-overflow undefined behaviour in the engine is live again in AOT binaries. Base b226856 defaults to gcc on Linux while tail needs clang with preserve_none, and the author's javascript-zoo notes say clang is 'significantly more performant' than gcc, so compiler choice may account for part of the gain. ES modules get no AOT, eval code stays interpreted (CodeLoad 0.995x), functions under 5 or over 10000 bytecode bytes are skipped, make install omits libquickjsaot.a and quickjs.i, no AOT tests in CI. b226856 is Bellard's upstream 'updated to unicode 17.0.0' commit (2025-11-29).

## Caveats and trade-offs

First-party numbers with incomplete methodology: the clang version, the build flags of the base interpreter and the benchmark harness are not documented in the README, and the repo has no V8 benchmark files (tests/ holds only microbench.js and the test suites). The author's separate ivankra/javascript-zoo repo has a bench/ directory with V8-suite scripts (v8-v7.js, richards.js and others) and bench.py, which is probably the harness, but the README does not link it. The baseline is the author's own QuickJS fork commit b226856, not an upstream bellard/quickjs release. Gains depend on the workload (RegExp +4%, CodeLoad none) and the author calls the result modest; the project is a proof of concept. GitHub shows no fork link to bellard/quickjs, although the code and LICENSE (MIT, Bellard and Gordon) are QuickJS's.

Proof-of-concept ahead-of-time compiler: needs a C compiler (clang) at build time and produces a native binary per script, so it only speeds up scripts known at build time; the tail-call dispatch change is separate and easier to adopt (ivankra/quickjs tail branch). Generated C is larger than bytecode.

## Maintenance

Proof of concept, last commit 2025-12-09 (one AOT commit on top of the tail-call refactor of the 2025-11-29 upstream), 9 stars, no issues and no AOT tests; MIT, so the generator is easy to study or port, but it is not something to ship without your own test262 run on AOT binaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table compares qjsc -A with a base QuickJS interpreter commit on the V8 v7/v9 suites on a Mac M4 (Debian 13 VM), median of 20 runs, but the harness and benchmark sources are not in the repo or linked from it, and the clang version is not stated. That makes it first-party with partial methodology: C.
- **Verifier notes:** The headline numbers match the README. The search record misread the % columns: they are column-to-column ratios, so tail-call dispatch is +8.45% and +13.29% over base and AOT is about +26% over tail. The best case is NavierStokes at 2.14x (derived), not Crypto. MIT confirmed from the LICENSE file; last commit 2025-12-09; 9 stars; default branch aot.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** linked harness with compiler version; same-flag, same-compiler comparison
- **Pages the verifier opened:**
  - <https://github.com/ivankra/quickjs-aot>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/HEAD/README.md>
  - <https://github.com/ivankra/quickjs-aot/commits/aot>
  - <https://github.com/ivankra/quickjs-aot/tree/aot>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/LICENSE>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/Makefile>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/qjs-aot>
  - <https://github.com/ivankra/quickjs-aot/tree/aot/tests>
  - <https://github.com/ivankra/javascript-zoo>
  - <https://github.com/ivankra/javascript-zoo/tree/master/bench>
- **Sources the enricher read:**
  - <https://github.com/ivankra/quickjs-aot/tree/aot>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/README.md>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/Makefile>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/qjs-aot>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/LICENSE>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/qjsc.c>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/aot-parse.py>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/quickjs.c>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/TODO>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/Changelog>
  - <https://raw.githubusercontent.com/ivankra/quickjs-aot/aot/.github/workflows/ci.yml>
  - <https://github.com/ivankra/quickjs-aot/tree/aot/.github/workflows>
  - <https://github.com/ivankra/quickjs-aot/commits/aot>
  - <https://raw.githubusercontent.com/ivankra/quickjs/b22685617750e51d95f643d8eb1382dd09dd3bf1/Makefile>
  - <https://github.com/ivankra/quickjs/commit/b22685617750e51d95f643d8eb1382dd09dd3bf1>
  - <https://raw.githubusercontent.com/ivankra/quickjs/tail-20251204/Makefile>
  - <https://raw.githubusercontent.com/ivankra/quickjs/tail-20251204/quickjs.c>
  - <https://github.com/ivankra/javascript-zoo/tree/master/bench>
  - <https://raw.githubusercontent.com/ivankra/javascript-zoo/master/bench/Makefile>
  - <https://raw.githubusercontent.com/ivankra/javascript-zoo/master/harness/bench.py>
  - <https://github.com/ivankra/javascript-zoo/tree/master/engines/quickjs>
  - <https://raw.githubusercontent.com/ivankra/javascript-zoo/master/engines/quickjs/Dockerfile>
  - <https://raw.githubusercontent.com/ivankra/javascript-zoo/master/engines/quickjs/Makefile>
  - <https://raw.githubusercontent.com/ivankra/javascript-zoo/master/engines/quickjs/README.md>
  - <https://github.com/bnoordhuis/quickjit>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ivankra/quickjs-aot`) · [data/wave12/enrich/raw/github_com_ivankra_quickjs_aot.json](../../../data/wave12/enrich/raw/github_com_ivankra_quickjs_aot.json) (enrichment confidence 0.7)

</details>
