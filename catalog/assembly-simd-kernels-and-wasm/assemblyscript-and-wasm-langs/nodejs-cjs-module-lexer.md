# cjs-module-lexer (C lexer compiled to WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C compiled to WebAssembly (wasi-sdk and Binaryen), with a JavaScript build` · `MIT` · 🟢 active

> C CommonJS export lexer compiled to Wasm; beat its own pure-JS build in 2020 Node, near parity on Node 24.

| | |
|---|---|
| **Beats** | the same lexer's pure JavaScript build (lexer.js) running in V8/Node.js |
| **Claimed result** | README (November 2020 harness, no CPU or Node version): cold run, all samples, JS build 299 ms vs Wasm build 43 ms (6.95x, derived from page data, JIT warm-up of the JS build); warm run, all samples, 40.28 ms vs 27.76 ms (1.45x, README says about 1.5x; per-parse timings rounded to whole milliseconds). Maintainers' own later numbers: PR #124 (Node 24.20.0) JS build 11,094.91 us vs Wasm build 11,671.96 us per warm sweep (JS ahead); PR #131 small-module cold parse Wasm 0.370 vs JS 0.43 us. Module load time 4 ms (JS) vs 10 ms (Wasm). |
| **Workload** | Lexing 3,635 KiB of real-world JavaScript samples (angular, d3, magic-string, rollup and their minified forms) to detect CommonJS named exports: cold run over all samples and warm runs averaged over 25 |
| **Metric** | throughput |
| **Compiler and flags** | wasi-sdk 21.0 clang -target wasm32-unknown-wasi -Oz (build/Makefile), then binaryen 116 wasm-opt -Oz; versions are pinned in build/wasm.js and built via docker or npm run build-wasm-local. The build optimises for size, not speed. The JS build is lexer.js. The Node version is not stated; the README numbers date from November 2020, the Node 14 era. |
| **Adoption** | 262 stars; used by Node.js ESM-CommonJS interop |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/nodejs/cjs-module-lexer) · [benchmark](https://github.com/nodejs/cjs-module-lexer) |

## Verdict

The README (first-party, November 2020, Node and CPU not stated, npm run bench) times the same lexer as lexer.js and as -Oz Wasm over eight angular/d3/magic-string/rollup samples (3,635 kB): cold first pass 299 ms vs 43 ms (6.95x, derived from page data), warm average of 25 runs 40.28 ms vs 27.76 ms (1.45x), module load 4 ms vs 10 ms. The maintainers' September 2026 PR #124 on Node 24.20.0 (V8 13.6, CPU not stated) measures 11,094.91 us (JS) vs 11,671.96 us (Wasm) per sweep of a 3,629,072-code-unit corpus, so the warm gap has closed or reversed (the Wasm-only copy speedup in PR #122, 13,921.11 to 10,368.47 us, was measured on a different base and is not combined there).

## Use it when

- You need Node-compatible CommonJS named-export detection (bundlers, ESM/CJS interop shims, dev servers, browsers) with the frozen semantics Node.js core used until its January 2026 switch to merve.
- Cold or one-shot lexing, such as a CLI or a dev server parsing each dependency once: the README run shows 43 ms vs 299 ms for the JS build over 3,635 kB on the first pass.
- Many small modules per process: PR #131 (Node 22.23.3) measured 0.370 us per parse for the Wasm wrapper vs 0.43 us for the JS build on a two-export module.
- Environments that forbid eval or string code generation: since 2.2.0 string literals are decoded without eval, and tests run under --disallow-code-generation-from-strings.

## Skip it when

- Long-running warm workloads on current Node: the maintainers' own September 2026 numbers (PR #124, Node 24.20.0) put the JS build at 11,094.91 us vs Wasm 11,671.96 us per sweep of the same eight-file corpus, so the README's 1.5x warm advantage no longer holds.
- Inside Node.js core or when you want Node's current behaviour: Node replaced this package with the C++ lexer merve (nodejs/node PR #61456, Jan 2026, shipped in 24.14.0), which reports 26.83% faster cold import-cjs; merve has had its own interop regressions (merve#49).
- You need accurate exports for renamed exports objects, Object.defineProperties, computed or arrow getters, or webpack bundles: it is a heuristic lexer that both over- and under-classifies, and those cases are wontfix because patterns are frozen.
- Browser main threads that cannot compile Wasm synchronously, unless you await init() first; parse() now calls initSync() automatically on first use.
- Code with more than 255 star-export require bindings or nesting deeper than 2,048: see gotchas.

## How it is fast

A single forward pass over UTF-16 code units with a tiny state machine (open-token and template stacks) instead of an AST; regex/division ambiguity is resolved by backtracking over the preceding punctuator or keyword, and export patterns are matched by fixed keyword comparisons (str_eq5 style) at token starts. The C version (src/lexer.c) works on raw uint16_t pointers in linear memory with fixed global stacks, built with wasi-sdk clang -Oz and wasm-opt -Oz; the JS wrapper copies the string into Wasm memory (Buffer utf16le write for sources of 64+ units) and reads results back through exported cursor functions. Its main measured edge is avoiding JIT warm-up: the Wasm code is compiled at init, so the first parse is fast.

## Compared with alternatives

No catalogued sibling does CommonJS export detection; unlike camaro or VectorJSON, whose Wasm cores beat third-party JS parsers, this entry's speedup is against its own JS build and now shows mainly at cold start, so pick it for Node-compatible export detection rather than raw throughput, and look at the C++ merve if you can link native code.

## Integration

| | |
|---|---|
| **Form** | module (npm package cjs-module-lexer; ESM entry embeds the Wasm as base64, CommonJS entry is plain JavaScript) |
| **Dependencies** | none at runtime; building the Wasm needs docker (ghcr.io/nodejs/wasm-builder v0.0.9) or the pinned wasi-sdk 21.0 and binaryen 116, plus babel and terser for dist |
| **Minimum toolchain** | Node.js 18+ (engines field); browsers with WebAssembly support |
| **Platforms** | any JavaScript engine with WebAssembly (wasm32, no SIMD or threads required); pure-JS fallback runs anywhere |
| **Thread safety** | not documented; both builds keep parser state in module-level globals (one Wasm instance per module load), so it is single-threaded per realm and each worker needs its own import |
| **Drop-in for the baseline** | partial — same parse() API and results as the JS build, but only the ESM import resolves to the Wasm build (the exports map sends require() to lexer.js), and browsers must await init() before parse() |

## Gotchas

- Benchmark harness (bench/index.mjs) rounds every timed parse to whole milliseconds (Math.round per call) before averaging, so per-file warm figures such as magic-string 0.64 ms vs 0.16 ms and both builds' 0 ms rows are rounding artifacts; the README results date from November 2020 with no Node version or CPU, and the 6.95x cold ratio is JIT warm-up of the JS build, not faster steady-state code.
- Builds diverge on large Babel/TypeScript star-reexport files: the C lexer keeps star-export bindings in a fixed 256-entry array and silently stops recording after 255 ('gracefully overflow'), while lexer.js uses an unbounded map; reexports past that point vanish from the Wasm result (open PR #136, October 2026).
- Before 2.3.0 the Wasm build wrote past its fixed 2,048-entry parser stacks on deeply nested input (issue #81, opened February 2023: 3,069 nested braces gave 'Bus error: 10' and could crash Node on import); fixed only on 2026-09-08 in PR #125, so pin 2.3.0 or later for untrusted input.
- Wasm linear memory grows to about 4 bytes per source character plus heap base on the largest input parsed and is never shrunk.

## Known shortcomings

- Numbers date from 2020-11-02 (about 6 years stale, 2026 perf commits came later); the harness rounds each timing to whole ms; the baseline is the project's own JavaScript build; warm gain only 1.45x; built at -Oz.
- The README's 1.5x warm claim is contradicted by the maintainers' own numbers: PR #124 (Node 24.20.0) measured the JS build at 11,094.91 us vs the Wasm build at 11,671.96 us per sweep, so JS is ahead warm; the Wasm edge left is cold start and small modules (PR #131: 0.370 vs 0.43 us). The harness rounds each parse to whole milliseconds. Node core dropped this lexer for merve in January 2026 (node PR #61456), so the usage claim is stale. Wasm bugs: an out-of-bounds write past 2,048 nesting levels (issue #81, fixed only in #125 on 2026-09-08) and star-export bindings past 255 silently dropped (PR #136 open).

## Caveats and trade-offs

First-party README numbers with no CPU or Node version, run with npm run bench (bench/index.mjs). git blame dates the benchmark block to the 2020-11-02 commit d38263b and the '1.5x faster' line to 2020-09-27. They predate the wasi-sdk/binaryen builder change (2024) and the September-October 2026 perf commits (#122, #123, #124, #131), so they are about six years stale. The harness rounds every timed parse to whole milliseconds (Math.round per call) before averaging, so per-file warm figures under a few ms (magic-string 0.64/0.16/0 ms) are rounding artifacts and the all-samples sums carry up to about 4 ms of rounding per run. The baseline is the project's own JavaScript build, not a third-party package. The warm-run advantage is only 1.45x; the 6.95x cold-run gap reflects JIT warm-up of the JS build that the Wasm build skips. Wasm module load is slower (10 ms vs 4 ms). [retier] First-party README numbers from the 2020-11-02 commit d38263b with no CPU or Node version, about six years stale against the wasi-sdk/binaryen builder change (2024) and the September-October 2026 perf commits (#122-#124, #131). The harness (bench/index.mjs) rounds every timed parse to whole milliseconds before averaging, so per-file warm figures under a few ms are rounding artifacts and the all-samples sums carry up to about 4 ms of rounding per run; the cold 6.95x is JIT warm-up of the JS build, not faster steady-state code. The maintainers' own PR #124 run on Node 24.20.0 shows the JS build ahead of the Wasm build in the warm sweep, so the README's 1.5x warm claim no longer holds; the remaining Wasm edge is cold start and small modules. Node core dropped this lexer for merve in January 2026 (node PR #61456), so the usage claim is stale. Wasm-build bugs: the C lexer wrote past its fixed 2,048-entry parser stacks on deeply nested input (issue #81, 'Bus error: 10', fixed only in PR #125 on 2026-09-08, so pin 2.3.0 or later), and it keeps star-export bindings in a fixed 256-entry array and silently drops reexports past 255 while lexer.js uses an unbounded map (open PR #136). Wasm linear memory grows to about 4 bytes per source character on the largest input and is never shrunk.

Wasm build needs initSync() or await init() (ESM only; browsers should await init()); wasm instantiation adds about 6 ms of module load; detection patterns are frozen by design; both builds are lexers, not parsers, so the work per byte is small.

## Maintenance

Actively maintained (2.3.0 on 2026-10-05, perf and safety fixes through 2026-10-10) and MIT-licensed, but no longer used by Node.js core since the January 2026 switch to merve, its 2020 benchmark figures are stale, and the README's 1.5x warm claim is contradicted by the maintainers' own 2026 numbers, which leave the Wasm build's measured advantage mostly at cold start.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The README numbers come from the public bench/index.mjs, and the build flags are public (wasi-sdk 21.0 clang -Oz, binaryen 116 wasm-opt -Oz). But no CPU or Node version is stated and the numbers are first-party, so the tier is C.
- **Retiered** C to D: Enricher: the maintainers' own PR #124 numbers (Node 24.20.0) put the JS build ahead of the Wasm build in the warm sweep (11,094.91 vs 11,671.96 us), the 2020 README harness rounds each parse to whole milliseconds so its warm per-file figures are rounding artifacts, the cold 6.95x is JIT warm-up, and Node core replaced the lexer with merve in January 2026. The catalogued warm speedup no longer holds and the remaining edge is cold start only: C to D.
- **Verifier notes:** Numbers match the README exactly (cold 299 vs 43 ms, warm 40.28 vs 27.76 ms, load 4 vs 10 ms). Shortcomings to record: the numbers are from November 2020 and stale relative to the 2026 perf commits; there is no hardware or Node version; the harness has whole-millisecond rounding; the baseline is the project's own JS build. Metadata: MIT, 262 stars, 31 forks, last commit 2026-10-10, not archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-117 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/nodejs/cjs-module-lexer>
  - <https://github.com/nodejs/cjs-module-lexer/commits>
  - <https://github.com/nodejs/cjs-module-lexer/commits/main/README.md>
  - <https://github.com/nodejs/cjs-module-lexer/blame/main/README.md>
  - <https://github.com/nodejs/cjs-module-lexer/commit/70d33c7>
  - <https://github.com/nodejs/cjs-module-lexer/commit/9c13a80>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/README.md>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/package.json>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/Makefile>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/bench/index.mjs>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/build/wasm.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/build/Makefile>
- **Sources the enricher read:**
  - <https://github.com/nodejs/cjs-module-lexer>
  - <https://github.com/nodejs/cjs-module-lexer/commits>
  - <https://github.com/nodejs/cjs-module-lexer/issues>
  - <https://github.com/nodejs/cjs-module-lexer/pull/122>
  - <https://github.com/nodejs/cjs-module-lexer/pull/124>
  - <https://github.com/nodejs/cjs-module-lexer/pull/125>
  - <https://github.com/nodejs/cjs-module-lexer/pull/131>
  - <https://github.com/nodejs/cjs-module-lexer/pull/136>
  - <https://github.com/nodejs/cjs-module-lexer/issues/81>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/README.md>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/package.json>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/Makefile>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/bench/index.mjs>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/build/wasm.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/build/Makefile>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/build.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/lexer.d.ts>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/lexer.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/src/lexer.c>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/src/lexer.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/include-wasm/cjs-module-lexer.h>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nodejs/node/HEAD/lib/internal/modules/esm/translators.js>
  - <https://raw.githubusercontent.com/nodejs/node/HEAD/src/node_cjs_lexer.cc>
  - <https://raw.githubusercontent.com/nodejs/node/HEAD/deps/merve/merve.h>
  - <https://github.com/nodejs/node/commits/main/src/node_cjs_lexer.cc>
  - <https://github.com/nodejs/node/commit/37e4004>
  - <https://github.com/nodejs/node/pull/61456>
  - <https://github.com/nodejs/merve>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nodejs/cjs-module-lexer`) · [data/wave13/enrich/raw/github_com_nodejs_cjs_module_lexer.json](../../../data/wave13/enrich/raw/github_com_nodejs_cjs_module_lexer.json) (enrichment confidence 0.8)

</details>
