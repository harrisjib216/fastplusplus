# merve (nodejs CommonJS export lexer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 OR MIT` · 🟢 active

> C++20 lexer that finds CommonJS named exports for Node's ESM import(); replaced cjs-module-lexer, making cold CJS imports about 21% faster.

| | |
|---|---|
| **Beats** | cjs-module-lexer (the JS/WebAssembly lexer previously bundled in Node.js core) |
| **Claimed result** | Node PR 61456 body: 'the new cjs module lexer is 25% faster for cold importing cjs files'. Benchmark CI compare run quoted in the PR: esm/import-cjs.js type='cold' +26.83 % (accuracy +/-0.58 %, \*\*\*), type='warm' +11.95 % (+/-0.14 %, \*\*\*). Node's compare tool reports improvement in operations per second, so +26.83 % corresponds to about 21 % less time per cold import (derived from page data). |
| **Workload** | Node.js benchmark esm/import-cjs.js: ESM import() of a CommonJS fixture (typescript.js, 2000+ exports), cold (one first import) and warm (ten imports), comparing a Node build using merve against one using cjs-module-lexer. |
| **Metric** | latency |
| **Adoption** | 63 stars; replaced cjs-module-lexer in Node.js core (PR 61456 merged 2026-01-28, shipped in v24.14.0 LTS and v25.6.1) |
| **Last commit** | 2026-04-17 |
| **Links** | [repository](https://github.com/nodejs/merve) · [benchmark](https://github.com/nodejs/node/pull/61456) |

## Verdict

In Node PR 61456, merve's own author ran Node's benchmark CI to compare a Node build using merve with one using cjs-module-lexer on benchmark/esm/import-cjs.js, which runs ESM import() of the 2000+-export typescript.js fixture. The cold single import was +26.83 % ops/s (+/-0.58 %) and ten warm imports were +11.95 % (+/-0.14 %), which is about 21 % and 11 % less time per import (derived from page data). No CPU, compiler or flags are given, and the timing is end to end, including file read, compile, evaluation and the baseline's wasm start-up, so lexer-only speed is not isolated.

## Use it when

- Tools outside Node that must reproduce Node's CJS-to-ESM named-export detection, such as bundlers, resolvers, alternative runtimes or linters, written in C, C++ or Rust.
- Bulk scans of npm packages to list CJS exports and re-exports with line numbers, where a native library is easier to embed than a JS or wasm module.
- Runtimes where the cold-start cost of instantiating cjs-module-lexer's wasm matters, for example the first import() of a CJS dependency.
- Flagging .js files that contain ESM syntax: it returns UNEXPECTED_ESM_IMPORT, UNEXPECTED_ESM_EXPORT or UNEXPECTED_ESM_IMPORT_META.

## Skip it when

- Untrusted or adversarial source until a nesting-depth bound is added: parentheses and braces nested more than 2048 deep overrun fixed-size stacks (see gotchas).
- You need exports that the cjs-module-lexer rules miss: module.exports = { test: 5 } yields no exports (open issue #27, the same won't-fix behaviour as upstream), and import \* namespaces lose exports whose names start with 'get' (open issue #49).
- You need a general JavaScript tokenizer or parser: merve only recognises export patterns.
- Pure-JS environments: the cjs-module-lexer npm package stays the portable option, and merve needs a native C++20 build.
- You need lexer-only throughput numbers: none are published, and the repository has no benchmarks directory although CMake has a MERVE_BENCHMARKS option.

## How it is fast

It is a hand-written single-pass scanner that does not backtrack. It keeps the structure of cjs-module-lexer's lexer.c: the same open-token and template stacks with STACK_DEPTH 2048, and the same star-export backtracking. Characters are classified with 256-entry lookup tables built by consteval lambdas. Export names are std::string_view slices of the source, and a std::string is allocated only when an escape must be decoded. With MERVE_USE_SIMDUTF, which Node enables, simdutf::find locates backslashes and simdutf converts UTF-32 to UTF-8. Inside Node, part of the measured gain comes from calling native C++ directly, where the old path ran JS that called a WebAssembly lexer that had to be initialised first.

## Compared with alternatives

The catalogued siblings (flex, logos, simd-lexing, the Zig SIMD tokenizer, LRSTAR) are general lexer generators or language tokenizers. Pick merve only for the narrow job of detecting CommonJS exports with Node-compatible semantics, which none of them provide.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake target lexer::lexer) or source-drop (singleheader/merve.h and merve.cpp); Rust crate in rust/ |
| **Dependencies** | none; simdutf optional (MERVE_USE_SIMDUTF, fetched with CPM when not found) |
| **Minimum toolchain** | C++20 (consteval lookup tables), CMake 3.16 |
| **Platforms** | Linux, macOS and Windows per the README; scalar portable code, with SIMD only through optional simdutf |
| **Thread safety** | parse_commonjs keeps its state in a local CJSLexer, and the last-error state has been thread_local since 1.1.0, so separate threads can parse concurrently (read from parser.cpp; not otherwise documented). Results hold string_views into the caller's buffer. |
| **Drop-in for the baseline** | partial: it follows cjs-module-lexer's detection rules and replaced it inside Node core, but the language and API differ (C++/C/Rust instead of a JS/wasm parse() function) |

## Gotchas

- No nesting-depth check on brackets: upstream cjs-module-lexer guards every push with pushOpenToken(), which raises a syntax error at STACK_DEPTH 2048 in lexer.c and throws 'Maximum nesting depth exceeded.' in lexer.js. merve's src/parser.cpp checks only template nesting (TEMPLATE_NEST_OVERFLOW). Its five openTokenDepth++ pushes (plain '(' and '{', import(, __interopRequireWildcard( and __export( or __exportStar( contexts), and the ++openTokenDepth in templateString(), write to std::array&lt;..., 2048&gt; members with no bound. More than 2048 nested parentheses or braces therefore writes out of bounds in the CJSLexer object, which is a local on the stack in parse_commonjs. Because openTokenDepth is uint16_t, the index can reach 65535, about 512 KB past openTokenPosStack_. Node runs this lexer on any CJS file that ESM code imports. This was found by reading the code at HEAD; it was not reproduced (no build), and the repository has no fuzz directory.
- Benchmark harness: the warm row of nodejs/node benchmark/esm/import-cjs.js asserts deepStrictEqual(Object.keys(require(fixture)), Object.keys(result.default)). result.default is module.exports, which does not depend on the lexer, so the check does not validate the names merve detects; those appear on the namespace object itself. The cold row times a single import() that includes reading, compiling and evaluating typescript.js, plus the baseline's wasm initialisation.
- Zero-copy names: for exports held as string_view (most plain identifiers), the source buffer must outlive the analysis, including through the C API, where the merve_analysis handle must also be freed with merve_free().
- Released versions had memory-safety and correctness regressions: a heap-buffer-overflow read when require() is the first token (Node issue 62212, fixed in 1.2.1 by merve PR 41), a ToLocalChecked abort in Node's binding (fixed by node PR 63885), 'get' export names breaking later exports (fixed in 1.2.0), and Rust-binding unsoundness (issues #16 and #28, fixed in 1.1.x).

## Known shortcomings

- Only evidence is the author's own Node CI run (cold +26.83%, warm +11.95%) with no CPU or flags; it times the whole import(), so the binding change and wasm start-up removal are mixed in with the lexer. The CMake benchmark option points to a benchmarks directory that does not exist. Post-merge regressions node #62212 and #63323 were fixed; merve issue #49 is still open.
- Enricher (code reading, not reproduced): no bracket-nesting bound; upstream cjs-module-lexer checks pushes against STACK_DEPTH 2048, but merve's src/parser.cpp checks only template nesting, so more than 2048 nested ( or { writes out of bounds into the stack-allocated CJSLexer arrays (up to about 512 KB past). No fuzz directory. Harness: the import-cjs.js warm assert compares Object.keys(result.default), which is module.exports and independent of the lexer output, so the warm row does not check lexer correctness.

## Caveats and trade-offs

The numbers come from the PR author's own Node Benchmark CI run (the author, anonrig, also wrote merve); the PR page gives no CPU, compiler or flags and links only to the CI console. The benchmark (nodejs/node benchmark/esm/import-cjs.js) is end-to-end import() of the 2000+-export typescript.js fixture, which includes reading, wrapping and compiling the file, so the lexer-only speedup is not isolated; it compares whole Node builds that also changed the binding (native C++ instead of JS calling wasm), and the cold row includes wasm initialization for the baseline (the warm path's own comment says 'Initialize the wasm first'). The warm row asserts that the imported export names match require(), so it checks correctness. Other rows of the same run are noise-level (esm/detect-esm-syntax +1.47 % and +0.64 %) or noisy (esm-loader-defaultResolve node:os -8.43 % +/-9.28 %). The merve README gives no numbers; its CMakeLists.txt has a MERVE_BENCHMARKS option (default OFF) that calls add_subdirectory(benchmarks), but no benchmarks directory exists in the repository (raw path 404), so the option cannot build. Post-merge correctness regressions: nodejs/node issue 62212 (SIGSEGV when import() analyses a large CJS webpack bundle, bisected to PR 61456, fixed by nodejs/merve PR 41), issue 63323 (FATAL ERROR v8::ToLocalChecked Empty MaybeLocal in cjs_lexer::Parse since v24.14.0, fixed by nodejs/node PR 63885, closed 2026-06-15) and nodejs/merve issue 49 (still open: import \* namespace objects lose exports whose names begin with 'get', reported with @tonaljs/chord). The measured build therefore predates several correctness fixes. [retier] Enricher (code reading, not reproduced): no bracket-nesting bound, unlike upstream cjs-module-lexer's STACK_DEPTH 2048 check, so more than 2048 nested ( or { writes past the stack-allocated CJSLexer arrays. The import-cjs.js warm assert compares Object.keys(result.default), which is independent of the lexer output, so the warm row does not verify correctness.

Zero-copy export names via std::string_view, single pass without backtracking, consteval lookup tables, optional simdutf for escape detection (off by default, Node enables it). Ships a C API and Rust bindings, no dependencies. Detection behavior must match the frozen cjs-module-lexer patterns; error handling returns std::optional. The old lexer was JS plus WebAssembly, so the swap also removes wasm instantiation from the cold path.

## Maintenance

The project is active (v1.2.2 released 2026-03-11, last commit 2026-04-17), Apache-2.0 OR MIT, and shipped in Node v24.14.0 LTS and v25.6.1. It is young, though: there have been several post-merge crash and wrong-export fixes, issue #49 is open, HEAD has no bracket-nesting bound (a possible stack out-of-bounds write on deeply nested input), and the only numbers come from a first-party end-to-end Node CI run whose warm-row assertion does not check the lexer's output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Node PR 61456 states '25% faster for cold importing cjs files' and quotes a Benchmark CI compare run with esm/import-cjs.js cold +26.83 % (+/-0.58 %, \*\*\*) and warm +11.95 % (+/-0.14 %, \*\*\*); the benchmark code (nodejs/node benchmark/esm/import-cjs.js) is public but the run was launched by merve's own author and no CPU, compiler or flags are given, so first-party with partial methodology (C).
- **Verifier notes:** Record is accurate; tier C stands (first-party CI run, no hardware or flags, end-to-end import timing that bundles a binding change and wasm start-up). Shortcomings: lexer speed not isolated, benchmark directory referenced by CMake is missing, three post-merge crash or wrong-export regressions (two fixed, merve issue 49 open). Metadata checked: Apache-2.0 OR MIT, 63 stars, not archived or a fork, last commit 2026-04-17 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 3 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/nodejs/node/pull/61456>
  - <https://github.com/nodejs/merve>
  - <https://github.com/nodejs/merve/commits>
  - <https://github.com/nodejs/merve/commits/main.atom>
  - <https://github.com/nodejs/merve/tree/main>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nodejs/node/HEAD/benchmark/esm/import-cjs.js>
  - <https://github.com/nodejs/node/issues/62212>
  - <https://github.com/nodejs/node/issues/63323>
  - <https://github.com/nodejs/merve/issues/49>
- **Sources the enricher read:**
  - <https://github.com/nodejs/merve>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/README.md>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/src/parser.cpp>
  - <https://raw.githubusercontent.com/nodejs/merve/HEAD/CHANGELOG.md>
  - <https://github.com/nodejs/merve/pull/41>
  - <https://github.com/nodejs/merve/issues?q=is%3Aissue>
  - <https://github.com/nodejs/merve/issues/27>
  - <https://github.com/nodejs/node/pull/61456>
  - <https://raw.githubusercontent.com/nodejs/node/HEAD/benchmark/esm/import-cjs.js>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/src/lexer.c>
  - <https://raw.githubusercontent.com/nodejs/cjs-module-lexer/HEAD/lexer.js>
  - <https://crates.io/api/v1/crates/merve>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/nodejs/merve`) · [data/wave3/enrich/raw/github_com_nodejs_merve.json](../../../data/wave3/enrich/raw/github_com_nodejs_merve.json) (enrichment confidence 0.75)

</details>
