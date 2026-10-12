# Porffor (AOT JavaScript/TypeScript to Wasm and C)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟢 active

> Ahead-of-time JavaScript/TypeScript compiler emitting C and native binaries; first-party V8-suite score beats QuickJS and Node --jitless, not JIT engines.

| | |
|---|---|
| **Beats** | QuickJS and Node --jitless (V8 interpreter only); Node and Bun with JIT are NOT beaten |
| **Claimed result** | Snippet of the porffor.dev site (page blocked, not opened): Porffor 6,646 vs Node without JIT 5,828, Bun without JIT 4,464, QuickJS 3,564; Node and Bun with JIT score 13 to 17x higher. Ratios (derived from the snippet): 1.14x Node jitless, 1.86x QuickJS. |
| **Workload** | V8 benchmark suite (v8-v7) composite score, higher is better; the suite is committed as bench/v8-v7.js. |
| **Metric** | throughput |
| **Adoption** | 5.3k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/CanadaHonk/porffor) · [benchmark](https://porffor.dev/) |

## Verdict

Porffor's own site reports a V8 benchmark suite (v8-v7) composite score of 6,646 against 5,828 for Node with the JIT disabled, 4,464 for Bun without JIT and 3,564 for QuickJS (about 1.14x and 1.86x, derived from the snippet), with JIT-enabled Node and Bun 13 to 17x higher; engine versions, C compiler, flags, hardware and date are not available, and the repo commits the suite but no results.

## Use it when

- You want a single small native binary from a JS/TS program for CLI tools, serverless or embedded targets, with no Node, Bun or QuickJS runtime shipped beside it.
- Startup time and binary size matter more than peak throughput, for example short-lived commands that a JIT never warms up for.
- You would otherwise run under an interpreter-only engine (QuickJS, Node --jitless, Bun without JIT), where the first-party V8-suite numbers put Porffor ahead (about 1.86x QuickJS, 1.14x Node jitless, derived from a snippet).
- You want generated C you can inspect, patch or cross-compile (release CI builds the compiler with zig cc for Linux and macOS on x64 and arm64; the runtime has a WASI code path).

## Skip it when

- Throughput-bound long-running code: JIT-enabled Node and Bun score 13 to 17x higher on the same V8 suite (snippet), and issue #262 measured property access in a 1-billion-iteration loop about 12x slower than V8 in Chrome.
- Programs that need full ECMAScript or web APIs: open issues include no iterator objects (Map/Set iterators return arrays, for...of ignores Symbol.iterator, #375), no Proxy (#145), no dynamic import() (#345), no ReadableStream (#349) or crypto.getRandomValues (#347), and correctness bugs around classes and function reassignment (#356, #357, #389, #400).
- Production use: releases are labelled alpha (alpha 15 on 2026-10-02), the compiler was 'almost entirely rewritten' in July 2026 (issue #344), and CI gates releases only on 108 self-host test262 harness passes; the last full test262 figure in test262/history.json is 67.45 percent (34,211 of 50,718) from 2026-03-06, before the rewrite.
- Heaps above 4 GiB (the arena reserve is 1&lt;&lt;32 with 32-bit references; 64 MiB on WASI) or Windows hosts (no Windows release binary is built).

## How it is fast

Whole-program AOT compilation: a parser and semantic pass feed one flat IR tree (compiler/ir.js, constant folding at construction, no later lowering passes) that render.js prints as C, which the system C compiler then optimizes at -O3 with -flto by default. Options on by default (compiler/prefs.js) are indirectCalls, optUnused, optTypes, ctHash, closures, lazyObjects and ic, i.e. unused-code and type-driven optimizations plus what the names suggest are lazy object materialization and inline caches; values are a {f64 val; i32 type} struct, and memory comes from a 4 GiB reserved arena with 32-bit object references and a mark-based collector with minor and full cycles. With no interpreter or JIT warm-up the output starts quickly and stays small (README: hello world compiled in 105 ms to a 33.7 KB binary), but it has no runtime profiling or speculative optimization, which is why JIT engines stay far ahead on throughput.

## Compared with alternatives

Choose Porffor over scriptc or katsu when the input is general JavaScript rather than a typed TypeScript subset and you want inspectable C output; choose lumen (about 2.2x QuickJS on macOS arm64 in ahaoboy/js-engine-benchmark) or plain Node/V8 when you need a full engine with better measured throughput, and LLRT when the goal is fast Lambda cold starts with a fuller runtime.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Compiler is distributed as the porffor npm package or install script with prebuilt binaries; producing native output needs a system C compiler (cc, \$CC or --compiler; zig cc for --musl). Generated programs link only libm (uWebSockets is pulled in for the native fetch server mode). |
| **Minimum toolchain** | not documented; CI builds with Node 24, LLVM 21 and zig 0.16.0, and generated C uses C11 features such as _Generic and _Thread_local |
| **Platforms** | Release binaries for linux-x64, linux-arm64, linux-x64-musl, linux-arm64-musl, darwin-x64, darwin-arm64; generated C has a WASI path; no Windows release |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — runs ordinary JS/TS sources without changes when they stay inside the supported subset, but it is a whole-program compiler producing a binary, not a replacement engine you can embed like QuickJS, and unsupported features fail at compile or run time |

## Gotchas

- The V8-suite numbers (Porffor 6,646, Node no-JIT 5,828, Bun no-JIT 4,464, QuickJS 3,564) are first-party, seen only in a search snippet of porffor.dev (blocked here) with no date, hardware or versions; since the compiler was almost entirely rewritten in July 2026, they may describe the earlier Wasm-based compiler.
- Harness caveat: bench/v8-v7.js uses V8's base.js, whose final score is the geometric mean of only the suites that completed; a suite that throws (including a failed result check) is reported as ERROR and left out rather than scored zero. Whether Porffor completes all eight suites (RegExp, EarleyBoyer and others) in the published run cannot be checked, since no results or logs are committed, and a 'builtins/regexp: basic search' commit landed only on 2026-09-30.
- `porf foo.js` recompiles the program through the C compiler on every invocation (single-file builds pipe C to cc with no cache), so time scripts by building once with `porf native` and running the binary.
- Some speed options trade spec compliance: --fast-length is a 'non-compliant optimization', and a --safe mode exists to 'error on unsafe Porffor features', meaning the default build accepts them.

## Known shortcomings

- First-party snippet only (porffor.dev blocked): 6,646 vs Node --jitless 5,828 vs QuickJS 3,564, no hardware or versions; beats only interpreters and is 13-17x below JIT engines; js-compiled results are not committed.
- Enricher: the compiler was 'almost entirely rewritten' in July 2026 (issue #344; alpha 1 on 2026-07-15), so the snippet-only porffor.dev numbers may describe the old Wasm compiler. v8-v7.js base.js computes the geomean only over suites that finish, so an errored suite is dropped rather than zeroed, and no results are committed to confirm all 8 ran. Last full test262 pass rate 67.45% (2026-03-06, pre-rewrite); CI now gates only 108 selfhost harness passes. Issue #262: about 12x slower than V8 on property access. 4 GiB arena with u32 references; 'porf foo.js' recompiles C on every run; --fast-length is non-compliant.

## Caveats and trade-offs

Snippet only: the numbers come from a WebSearch snippet that quotes porffor.dev; the site is blocked by egress policy so hardware, versions, flags and date could not be read, hence tier C at most. The QuickJS, Node --jitless and Bun no-JIT figures are first-party runs of unknown versions on unknown hardware. The committed repo README has no numbers (only 'compiled hello.js in 105ms, 33.7KB') and now describes Porffor as compiling JS to C through an IR, with no Wasm mention; the README no longer says pre-alpha. Porffor is far slower than JIT-enabled V8 and JavaScriptCore on the same suite (Node and Bun with JIT score 13 to 17x higher), so the win is over Node's interpreter-only mode and QuickJS. Porffor is not in the ahaoboy/js-engine-benchmark shootout. Third-party harness jlucaso1/js-compiled (also proggeramlug/js-compiled) benchmarks Porffor vs Node, Bun and scriptc on 22 programs, but its results are published only on GitHub Pages (blocked) and are not committed (no results/ or REPORT.md in the tree, no gh-pages branch). The bench/ directory has 25 benchmark programs plus an ffi/ subdirectory (richards.js, v8-v7.js and more) but no results file.

100% AOT: compiles JS to C (with an IR) and also Wasm, with nothing interpreted or JIT-compiled; supports a subset of ECMA-262 (the README gives no conformance figure). Strong on startup, memory and binary size per the site, not on peak speed.

## Maintenance

Very active (alpha releases several times a week, last commit 2026-10-02, about 3,220 commits) and MIT-licensed, but alpha-quality after a mid-2026 rewrite, with a narrowing but real ECMAScript gap; usable today for small self-contained JS/TS tools, not for code that needs full spec conformance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers on the project's own site porffor.dev (EGRESS_BLOCKED here), seen only in a WebSearch snippet that repeats the record's figures exactly (Porffor 6,646, Node no-JIT 5,828, Bun no-JIT 4,464, QuickJS 3,564 on the V8 suite); the repo carries the suite (bench/v8-v7.js) but no results, hardware, versions or flags, so C (snippet-only precedent).
- **Verifier notes:** Snippet re-confirmed the record's numbers; porffor.dev and its results could not be opened, so benchmark_url is set to the blocked site per the snippet-only precedent. Metadata checked: MIT (Copyright 2023-2025 Oliver Medhurst), 5.3k stars, 137 forks, not a fork, last commit 2026-10-02. Shortcomings to record: snippet-only first-party numbers with no hardware or versions, beats only QuickJS and Node --jitless, 13 to 17x below JIT engines, no committed results.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** committed results with hardware and versions; committed results on the rewritten compiler
- **Pages the verifier opened:**
  - <https://github.com/CanadaHonk/porffor>
  - <https://github.com/CanadaHonk/porffor/commits>
  - <https://github.com/CanadaHonk/porffor/tree/main/bench>
  - <https://github.com/CanadaHonk/porffor/branches/all>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/README.md>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/CNAME>
  - <https://github.com/jlucaso1/js-compiled>
  - <https://raw.githubusercontent.com/jlucaso1/js-compiled/HEAD/README.md>
  - <https://raw.githubusercontent.com/proggeramlug/js-compiled/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/CanadaHonk/porffor>
  - <https://github.com/CanadaHonk/porffor/commits>
  - <https://github.com/CanadaHonk/porffor/tree/main/bench>
  - <https://github.com/CanadaHonk/porffor/tree/main/compiler>
  - <https://github.com/CanadaHonk/porffor/tree/main/runtime>
  - <https://github.com/CanadaHonk/porffor/tree/main/test262>
  - <https://github.com/CanadaHonk/porffor/tree/main/.github/workflows>
  - <https://github.com/CanadaHonk/porffor/issues>
  - <https://github.com/CanadaHonk/porffor/issues/262>
  - <https://github.com/CanadaHonk/porffor/issues/344>
  - <https://github.com/CanadaHonk/porffor/releases>
  - <https://github.com/CanadaHonk/porffor/wiki>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/README.md>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/.github/workflows/ci.yaml>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/test262/history.json>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/bench/v8-v7.js>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/runtime/index.js>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/compiler/prefs.js>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/compiler/index.js>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/compiler/ir.js>
  - <https://raw.githubusercontent.com/CanadaHonk/porffor/HEAD/compiler/render.js>
  - https://porffor.dev/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/canadahonk/porffor`) · [data/wave12/enrich/raw/github_com_canadahonk_porffor.json](../../../data/wave12/enrich/raw/github_com_canadahonk_porffor.json) (enrichment confidence 0.6)

</details>
