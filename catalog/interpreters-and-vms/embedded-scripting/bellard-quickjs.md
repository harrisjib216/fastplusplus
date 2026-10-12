# QuickJS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Fabrice Bellard's small embeddable C JavaScript interpreter; about 2.3x Duktape on the V8 v7 benchmark suite.

| | |
|---|---|
| **Beats** | Duktape 2.3.0 (also compared with XS 8.8.0, MuJS 1.0.6, JerryScript, Hermes 0.1.0 and V8 in the same table) |
| **Claimed result** | Total score 942 for QuickJS vs 408 for Duktape (about 2.3x, derived from page data). Per test QuickJS vs Duktape: Richards 777 vs 218, DeltaBlue 761 vs 266, Crypto 1061 vs 202, RayTrace 915 vs 484, EarleyBoyer 1417 vs 620, RegExp 251 vs 156, Splay 1641 vs 1389, NavierStokes 1856 vs 1003. |
| **Workload** | bench-v8 version 7 scores (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes); higher is better; all engines run as interpreters. |
| **Metric** | throughput |
| **Hardware** | 3.2 GHz Core i5 4570 |
| **Compiler and flags** | gcc 4.9.2 on Fedora 21; QuickJS 2019-07-09 qjs x86 64-bit -O2; Duktape 2.3.0 duk x86 64-bit -O2 |
| **Adoption** | 11k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/bellard/quickjs) · [benchmark](https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md) |

## Verdict

On the V8 benchmark suite version 7 run by QuickJS's author in 2019 (gcc 4.9.2 -O2 on Fedora 21, Core i5 4570 at 3.2 GHz, all engines as interpreters), QuickJS 2019-07-09 scored 942 vs 408 for Duktape 2.3.0 (about 2.3x, derived from page data), winning all eight sub-tests. Independent GitHub Actions runs (ahaoboy/js-engine-benchmark, QuickJS 2026.06.04) give 1217 vs 489 on ubuntu, 1761 vs 905 on macOS arm64 and 1067 vs 371 on Windows; per the catalog's njs and Quanta entries that CI's Duktape is an unreleased 2.99.99 master built at -Os on ubuntu and macOS, which flatters QuickJS somewhat.

## Use it when

- Embedding a modern-JavaScript scripting layer in a C or C++ application where binary size matters (about 1 MB qjs executable in independent 2026 CI builds; the docs cite 210 KiB of x86 code for hello world) and a JIT is not allowed or not worth it.
- Replacing Duktape, MuJS or JerryScript when you need newer ECMAScript (modules, async, Proxy, BigInt, ES2025 features) and roughly 2x their interpreter throughput.
- Many short-lived script instances: the docs say a runtime instance's full life cycle completes in under 300 microseconds, and qjsc can precompile scripts to bytecode so the compiler can be dropped.
- Hosts that need deterministic memory release (reference counting) and per-runtime limits via JS_SetMemoryLimit, JS_SetMaxStackSize and JS_SetInterruptHandler.
- Shipping self-contained executables from JS via qjsc, on Linux, macOS, FreeBSD, Windows (MinGW) or a Cosmopolitan build.

## Skip it when

- Throughput-bound JavaScript: JIT engines score 15-40x higher on the same suite (ahaoboy CI ubuntu: V8 48107, Node 40333, QuickJS 1217), and even V8 --jitless scored 1916 vs 942 in the author's own 2019 table.
- When Hermes's ahead-of-time bytecode pipeline fits better: Hermes 0.12.0 beat QuickJS on ubuntu in the 2026 CI (1530 vs 1217), though QuickJS led on macOS arm64 (1761 vs 1233) and Windows (1067 vs 941).
- Running untrusted bytecode: the docs say the bytecode format is version-specific and unchecked, and fuzzing issues (#547-#550) report heap-buffer overflows in JS_ReadFunctionTag, JS_ReadFunctionBytecode and JS_DupAtom.
- Hard CPU-time sandboxes for hostile code: issue #546 (open when read) reports that BigInt multiply/divide/power/toString run as single C calls between interrupt-handler polls (every 10,000 bytecode instructions), so one operation can pin a core for seconds.
- Multithreaded sharing of one heap: a JSRuntime supports no multi-threading; use one runtime per thread and message passing.

## How it is fast

The compiler emits compact stack-based bytecode in one pass with no parse tree, then runs a few optimisation passes; maximum stack depth is computed at compile time so the interpreter needs no runtime stack-overflow checks. Objects share shapes, property names are interned 32-bit atoms, integers have 32-bit fast paths, holeless arrays and typed arrays have fast paths, closure variables are almost as fast as locals, and the RegExp engine is its own bytecode compiler with an explicit backtracking stack. Memory is managed by reference counting plus an occasional cycle-removal pass, and the 2026-06-04 release added a small-block allocator (Changelog: 11% faster on bench-v8) and micro-optimisations (30% faster on bench-v8).

## Compared with alternatives

Pick QuickJS over XS (738 vs QuickJS 1138 without RegExp in the same 2019 table) or Duktape-class engines when you want the fastest small C interpreter with current ECMAScript; pick Hermes when you control an AOT bytecode build for React Native, and Escargot or PrimJS only after checking their numbers on your platform, since PrimJS scored below QuickJS in the independent 2026 CI (737 vs 1217 ubuntu, 1694 vs 1761 macOS) despite its own Octane claim.

## Integration

| | |
|---|---|
| **Form** | source-drop or static library (libquickjs.a); shared libraries on Linux/FreeBSD via the Makefile |
| **Dependencies** | none (libc, libm, pthreads; -latomic on some OSes or disable CONFIG_ATOMICS) |
| **Minimum toolchain** | gcc or clang (Makefile defaults to -O2 -fwrapv, optional LTO); minimum C standard not documented |
| **Platforms** | Linux, macOS, FreeBSD, Windows via MinGW cross-compilation (documented as preliminary), Cosmopolitan; 32-bit builds use NaN boxing, 64-bit builds use 128-bit JSValues |
| **Thread safety** | No multi-threading inside one JSRuntime; separate runtimes can run on separate threads but cannot exchange objects; class IDs are allocated globally |
| **Drop-in for the baseline** | no |

## Gotchas

- Every JSValue is reference counted: C code must pair JS_DupValue and JS_FreeValue exactly, and exceptions come back as JS_EXCEPTION return values that the caller must test; there is no implicit value stack as in Duktape.
- Benchmark reproducibility: the Makefile's bench-v8 target runs tests/bench-v8/combined.js, but tests/bench-v8 is not in the GitHub tree (only microbench.js is), and the headline 942 vs 408 table is the author's 2019 run (QuickJS 2019-07-09, gcc 4.9.2) read here from the quickjs-zh mirror because bellard.org is blocked.
- The record's 'bignum extension' and 'ES2020' notes are out of date: the 2025-04-26 release removed the bignum extensions and qjscalc and reimplemented BigInt, and the docs now claim almost complete ES2025 support.
- Forks are not interchangeable on speed: in the 2026 ahaoboy CI the quickjs-ng 0.17.0 fork (the engine under rquickjs and LLRT) scored 647 vs 1217 on ubuntu, 1660 vs 1761 on macOS arm64 and 766 vs 1067 on Windows.

## Known shortcomings

- The bench-v8 table (942 vs Duktape 408) is the author's own 2019 run and tests/bench-v8 is not in the GitHub tree; the original page on bellard.org was blocked and read through the quickjs-zh mirror. Independent ahaoboy CI corroboration: 1217 vs 489 on ubuntu. QuickJS is itself a spec baseline for embedded-scripting.
- Enricher: record outdated (bignum extension removed 2025-04-26, now ES2025); in the author's own 2019 table V8 --jitless (1916) and Hermes (968) are ahead of QuickJS (942), and the 2026 ahaoboy CI has Hermes 0.12.0 ahead on ubuntu (1530 vs 1217). Fuzzing found heap overflows in the bytecode loader (issues #547-#550) and BigInt operations dodge the interrupt handler (#546, open).

## Caveats and trade-offs

Numbers are from 2019 (QuickJS 2019-07-09, Duktape 2.3.0, gcc 4.9.2) and were run by QuickJS's own author. The page opened is a Chinese-language mirror of the author's bench page (quickjs-zh/QuickJS bench.md); the original bellard.org/quickjs/bench.html is blocked here and was not opened, though a search snippet confirms the same 942 vs 408 totals. The bench-v8 directory the Makefile target uses is absent from the GitHub tree at HEAD and from an unpacked-tarball mirror (twardoch/quickjs-1); it is distributed separately on bellard.org (not verified here), while the underlying V8 v7 suite is public (e.g. mozilla arewefastyet v8-v7). Independent corroboration on current versions: ahaoboy/js-engine-benchmark CI (10/5/2026) scores QuickJS 2026.06.04 at 1217 vs Duktape 489 on ubuntu, 1761 vs 905 on macos-arm64 and 1067 vs 371 on windows (about 2.5x, 1.9x and 2.9x, derived from page data). QuickJS is itself one of the category's named baselines, and it is an interpreter: JIT engines (V8, JavaScriptCore, ChakraCore) are 15-40x faster on the same suite.

Executable 620K vs 331K for Duktape on the same page; supports recent ECMAScript (ES2020 and later) and a bignum extension; reference counting with a cycle collector; interpreter only, no JIT.

## Maintenance

Actively maintained by Fabrice Bellard (release 2026-06-04, commits through 2026-09-29 mostly spec-conformance fixes, MIT licence), small enough to vendor, with a steady stream of fuzzer-found memory-safety reports that matter only if you load untrusted bytecode or run hostile code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** The bench page (opened as the quickjs-zh translated mirror bench.md; the bellard.org original is EGRESS_BLOCKED, a search snippet of an HN comment links it and repeats the same totals) runs the public V8 benchmark suite version 7 (bench-v8; harness invoked by the bellard/quickjs Makefile target `bench-v8`: `make -C tests/bench-v8; ./qjs -d tests/bench-v8/combined.js`) on QuickJS and Duktape 2.3.0, both built with gcc 4.9.2 -O2 on Fedora 21, on a Core i5 4570 at 3.2 GHz. Code, compiler, flags and CPU model are all stated, so A holds.
- **Verifier notes:** Numbers match the mirror page row for row (Total 942 vs 408, every sub-test as quoted). Metadata checked on github.com: MIT, 11k stars, last commit 2026-09-29, not archived. Shortcoming to record: harness directory not in the public GitHub tree, original page only via mirror, 2019 numbers by the author.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md>
  - <https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/README.md>
  - <https://github.com/bellard/quickjs>
  - <https://github.com/bellard/quickjs/commits/master>
  - <https://github.com/bellard/quickjs/tree/master/tests>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Makefile>
  - <https://github.com/twardoch/quickjs-1/tree/master/tests>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/bellard/quickjs>
  - <https://github.com/bellard/quickjs/commits/master>
  - <https://github.com/bellard/quickjs/tree/master/tests>
  - <https://github.com/bellard/quickjs/issues?q=is%3Aissue+CVE+OR+heap-buffer-overflow+OR+use-after-free+OR+security>
  - <https://github.com/bellard/quickjs/issues/546>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/VERSION>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Changelog>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/TODO>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/quickjs.h>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/doc/quickjs.texi>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/README>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/README.md>
  - <https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bellard/quickjs`) · [data/wave12/enrich/raw/github_com_bellard_quickjs.json](../../../data/wave12/enrich/raw/github_com_bellard_quickjs.json) (enrichment confidence 0.8)

</details>
