# es-module-lexer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C compiled to WebAssembly (emcc) with a TypeScript/JavaScript wrapper` · `MIT` · 🟢 active

> C lexer compiled to Wasm that returns ES module import/export records; 2-3x faster than its own asm.js build.

| | |
|---|---|
| **Beats** | Acorn (fastest pure-JS parser, per the README) and the library's own CSP asm.js build of the same C lexer |
| **Claimed result** | README Package Exports table (3.1 MB test/samples set, Node.js 26, chomp bench): full Wasm build 4.7 ms/MB cold and 3.2 ms/MB warm versus the CSP asm.js build of the same C lexer at 14.9 / 6.3 ms/MB (3.2x cold, 2.0x warm, derived from page data); minimal Wasm build 4.5 / 3.1 versus minimal asm.js 10.8 / 5.7 ms/MB (2.4x cold, 1.8x warm, derived from page data). README prose: 'Angular 1 (720KiB) is fully parsed in 1ms, in comparison to the fastest JS parser, Acorn which takes over 100ms' (no Acorn row or benchmark code). |
| **Workload** | Lexing ECMAScript module import/export syntax over the 3.1 MB test/samples set (run via `chomp bench`, warm numbers averaged over 25 parses); README example: Angular 1 (720KiB) lexed in 1 ms. |
| **Metric** | throughput |
| **Hardware** | Unnamed 'standard desktop machine' |
| **Compiler and flags** | Full wasm build: emcc 6.0.0 (emsdk) src/lexer.c -Oz -flto -DLEXER_SIMD -D LEX_TS --no-entry -s STANDALONE_WASM=1; minimal build -DLEXER_MIN -Oz -flto -mcpu=mvp then wasm-opt; asm.js baseline built with fastcomp emscripten 1.40.1 -Oz --closure 1 (all from chompfile.toml); Node.js 26 for the benchmark |
| **Adoption** | 1.0k stars; used by es-module-shims and bundler/tooling pipelines |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/guybedford/es-module-lexer) · [benchmark](https://github.com/guybedford/es-module-lexer) |

## Verdict

The author's bench/index.js (Node.js 26, unnamed desktop machine, one run per build) lexes the 3.1 MB test/samples set: the full Wasm build takes 4.7 ms/MB cold and 3.2 ms/MB warm versus 14.9 and 6.3 ms/MB for the same C lexer compiled to asm.js by fastcomp emscripten 1.40.1 (3.2x cold, 2.0x warm, derived from page data), and the minimal Wasm build 4.5/3.1 versus 10.8/5.7 ms/MB for minimal asm.js. No Acorn or other JavaScript lexer is in the benchmark; the 'Angular 1 in 1 ms versus over 100 ms for Acorn' line is README prose comparing a lexer with a full parser.

## Use it when

- Build tools, dev servers and bundler plugins that need every import specifier and its offsets across thousands of modules (dependency graphs, specifier rewriting) at roughly 3-5 ms per MB.
- In-browser module analysis where download size matters: the minimal build is about 7.3 KiB Brotli including the inlined Wasm and runs on MVP Wasm engines.
- TypeScript sources limited to erasable syntax: the full build reports type-only imports/exports (typeOnly) the way Node type stripping erases them, so one pass handles .js and .ts graphs.
- Pages under a CSP that forbids Wasm compilation, via the es-module-lexer/js and es-module-lexer/minimal/js asm.js builds with the same API.
- Facade or ESM detection (the third and fourth return values) without a full parse.

## Skip it when

- You need an AST, scopes, validation or code transforms: it is a lexer and accepts some invalid source (README: `export const = 1` yields an empty exports list), so pair it with a real parser such as Acorn or SWC when correctness checking matters.
- Non-erasable TypeScript (enum, runtime namespace, parameter properties, legacy decorators) is out of scope, and dynamic import() types in annotation positions are classified heuristically (probablyTypeOnly). JSX support is not documented.
- Engines without Wasm SIMD (before Chrome 91, Firefox 89, Safari 16.4) cannot run the full build; use the minimal build, which lacks TypeScript, attributes, facade and export-origin data.
- Deeply nested input: more than 1024 open brackets/template substitutions or 512 nested dynamic imports throws a parse error.
- Raw scan speed is the only criterion: the catalogued fast-es-module-lexer reports 6.6-18x faster scans than es-module-lexer 1.7.0.

## How it is fast

A hand-written single-pass C state machine walks the UTF-16 source in Wasm linear memory and tracks only what import/export detection needs (open brace/paren/template stacks, keyword positions), resolving the regex-versus-division ambiguity by backtracking checks against the preceding punctuator instead of building tokens or an AST. The full build adds Wasm SIMD128 scans (i16x8 compares, i8x16 bitmask, count-trailing-zeros) for template literals after 16 scalar templates and for line comments after a 4-character unrolled prefix. On Node the wrapper blits the source into Wasm memory with Buffer.write('utf16le') for sources of 64+ characters, and full-build export records are read straight from memory with a DataView rather than through per-field calls.

## Compared with alternatives

Pick it over fast-es-module-lexer when you need the richer v3 record set (TypeScript typeOnly, import attributes, source/defer phases, export origin analysis, glob specifiers), a CSP-safe asm.js fallback or the dependency already used by es-module-shims and bundler pipelines; fast-es-module-lexer's 6.6-18x lead was measured against 1.7.0, not the 3.x SIMD build. Other wasm-libraries-and-apps siblings (sh-syntax, sax-wasm, markdown-wasm) solve different parsing tasks.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (single JS file with base64-inlined Wasm; ESM and CJS entry points) |
| **Minimum toolchain** | Node.js 18+; full build needs Wasm SIMD (Chrome 91+, Firefox 89+, Safari 16.4+); minimal build needs ES module support (Chrome 63+, Firefox 67+, Safari 11.1+); rebuilding from source needs Chomp plus emsdk 6.0.0 and fastcomp emsdk 1.40.1 |
| **Platforms** | any JavaScript engine with WebAssembly (SIMD for the full build); asm.js builds for engines or CSP policies without Wasm |
| **Thread safety** | not documented; the module holds one Wasm instance and its memory in module-level state and parse() is synchronous, so it is safe within one JS thread, and each worker loads its own instance |
| **Drop-in for the baseline** | partial — it replaces Acorn only for import/export discovery; it returns offset records, not an AST, and does not validate syntax |

## Gotchas

- v3.0.2 (PR #249) made init a function: old `await init` code silently skips compilation and parse() then compiles the Wasm synchronously on first call, which browser main threads restrict. The repo's own bench/index.js still does `if (init) await init;` (last edited in #240, before #249), so with current code the Wasm cold column includes base64 decode plus synchronous WebAssembly compile/instantiate inside the first sample, and the printed module load time understates Wasm load; this biases the cold ratio against Wasm, not for it.
- The Wasm-versus-asm.js ratios in the README mix three effects measured only on Node: Wasm versus fastcomp 1.40.1 asm.js codegen, SIMD scans present only in the full Wasm build, and the Node-only Buffer.write source copy in the Wasm wrapper versus a charCodeAt copy loop in the asm.js wrapper; in browsers (no Buffer) the gap is likely smaller (not measured).
- Releases before the v3 line pushed onto the fixed 1024-entry open-token stack and 512-entry dynamic-import stack without a depth check, so deeply nested input wrote past the arrays in Wasm memory; PR #243 (merged via #244 into v3) turned that into a parse error. Release 2.2.0 also failed with 'WebAssembly.Memory.grow(): Maximum memory size exceeded' on inputs above about 4 MB (issue #214, broke Vite 8.1.1 builds), fixed in 2.3.0.
- Template-literal globs: the README says a literal `*` in the static part of a template specifier is emitted as-is, but decodeTemplate in src/lexer.ts emits it as `\*` to keep the glob invertible; test against the version you ship before treating `specifier` as a pattern.

## Known shortcomings

- Baseline is its own asm.js build (3.2x cold, 2.0x warm, derived); the &gt;100x over Acorn claim is prose only; no CPU model; built -Oz; the listed fast-es-module-lexer (tier A) beats it 6.6-18x.
- Enricher: bench/index.js still runs 'if (init) await init;' although v3.0.2 (PR #249) made init a function, so with current code the Wasm cold column includes the base64 decode plus a synchronous WebAssembly compile on the first parse (skews the cold ratio against Wasm); the Wasm-vs-asm.js ratios mix three Node-only effects (SIMD only in the full Wasm build, the Wasm wrapper copies the source with Buffer.write while the asm.js wrapper uses a charCodeAt loop); pre-v3 releases pushed unchecked onto the token stacks so deep nesting wrote out of bounds in Wasm memory (fixed by PR #243) and 2.2.0 failed on inputs over about 4 MB (#214); the README says a literal '\*' in template globs is emitted as-is but the code emits '\\*'.

## Caveats and trade-offs

First-party numbers on an unnamed machine, one run per build. bench/index.js times only the four package builds (no Acorn or any independently written JS lexer); cold time excludes module load and init. The &gt;100x comparison against Acorn compares a module-syntax lexer with a full AST parser and is not backed by any table or code. The asm.js baseline is the same C source compiled by the 2020-era fastcomp emscripten 1.40.1 (-Oz --closure 1), so the ratio measures Wasm versus asm.js output of one lexer, not Wasm versus a JS implementation. The Wasm builds use -Oz (size) rather than -O3; the full build needs Wasm SIMD (-DLEXER_SIMD) while the minimal build targets MVP. A listed entry, fast-es-module-lexer (paper:r1ck404-fast-packages-fast-es-module-lexer, tier A), reports 6.6-18x faster scans than es-module-lexer 1.7.0, so es-module-lexer is no longer the fastest option for this task (the current 3.0.3 full build is compiled with -DLEXER_SIMD; whether 1.7.0 used SIMD was not checked).

Lexer only (imports/exports, no AST); full build needs WebAssembly SIMD (Chrome 91+, Firefox 89+, Safari 16.4+), the minimal build avoids SIMD; async init() before use; a CSP-safe asm.js build exists for environments that forbid wasm.

## Maintenance

Actively maintained (v3.0.3 on 2026-10-05, perf commit on 2026-10-06, 2 open issues), MIT, zero runtime dependencies and easy to adopt; the benchmark harness is stale against the v3 init API (wasm cold numbers include synchronous compile) and the only baseline is the project's own asm.js build after the pure-JS port was removed in #204.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by public benchmark code (bench/index.js run by `chomp bench`) with compilers and flags in chompfile.toml, but the machine is only 'a standard desktop machine' with no CPU model; the Acorn comparison is a prose claim with no benchmark code.
- **Verifier notes:** Record accurate; table numbers and derived ratios match the README, flags match chompfile.toml (emcc 6.0.0, fastcomp 1.40.1). Shortcomings to record: baseline is its own asm.js build, Acorn &gt;100x claim is prose only, no CPU model, and the listed fast-es-module-lexer beats it 6.6-18x. Metadata checked: MIT, 1.0k stars, last commit 2026-10-06 (v3.0.3 released 2026-10-05).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/guybedford/es-module-lexer>
  - <https://github.com/guybedford/es-module-lexer/commits>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/README.md>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/chompfile.toml>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/package.json>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/bench/index.js>
- **Sources the enricher read:**
  - <https://github.com/guybedford/es-module-lexer>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/README.md>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/chompfile.toml>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/package.json>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/bench/index.js>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/src/lexer.c>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/src/lexer.h>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/src/lexer.ts>
  - <https://raw.githubusercontent.com/guybedford/es-module-lexer/HEAD/src/lexer.asm.js>
  - <https://github.com/guybedford/es-module-lexer/issues>
  - <https://github.com/guybedford/es-module-lexer/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/guybedford/es-module-lexer/issues/214>
  - <https://github.com/guybedford/es-module-lexer/pull/243>
  - <https://github.com/guybedford/es-module-lexer/pull/249>
  - <https://github.com/guybedford/es-module-lexer/commits>
  - <https://github.com/guybedford/es-module-lexer/commits/main/bench/index.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/guybedford/es-module-lexer`) · [data/wave13/enrich/raw/github_com_guybedford_es_module_lexer.json](../../../data/wave13/enrich/raw/github_com_guybedford_es_module_lexer.json) (enrichment confidence 0.85)

</details>
