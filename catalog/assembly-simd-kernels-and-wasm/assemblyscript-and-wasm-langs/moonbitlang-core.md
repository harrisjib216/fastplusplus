# MoonBit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Study only · `MoonBit` · `Apache-2.0` · 🟢 active

> Standard library of MoonBit, a Wasm/JS/native-targeting language; vendor benchmark shows its JS output 7.7-7.9x faster than idiomatic JS.

| | |
|---|---|
| **Beats** | Plain JavaScript in Node v22.0.0 (V8): an idiomatic Array flatMap/filter/map/reduce chain and the same chain on JS Iterator Helpers, plus the json5 npm library's parse; vendor snippets also compare wasm output against Rust and Go compiled to WebAssembly |
| **Claimed result** | benchmark-202404 README (Node v22.0.0, MBP 2023 Apple M2 Max): iter 2,953,032 ops/s MoonBit vs 383,701 Plain JS (7.7x, derived from page data), 117,733 JS Iterator Helpers (25.1x, derived from page data; the source of the vendor's 'up to 25x faster than native JS' headline) and 155,935 Kotlin/JS; json5 22,908 ops/s MoonbitJson5.parse vs 2,887 json5.parse (7.9x, derived from page data). Snippet only, not checked: fib(46) run ten million times as wasm, MoonBit 177.9 ms vs Rust 160.8 ms vs Go 6357.8 ms (slower than Rust); 626 packages compiled in 1.06 s. |
| **Workload** | MoonBit JS-backend output vs plain JS in Node v22.0.0 (tinybench, warmup then run): bench_iter runs a flat_map/filter/map/map/filter/fold pipeline over a JSON class/member dataset; bench_json5 parses data/data.json5 with MoonBit core's json5 package (compiled to JS) versus json5.parse from npm. Precompiled MoonBit JS is committed in the repo (April 2024). |
| **Metric** | other |
| **Hardware** | MacBook Pro 2023, Apple M2 Max |
| **Compiler and flags** | moon build --target js (release output under target/js/release, per bench_iter/package.json and bench_json5/package.json); MoonBit compiler version not stated; JS baselines run as-is on Node v22.0.0 |
| **Adoption** | 1.2k stars (moonbitlang/core standard library) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/moonbitlang/core) · [benchmark](https://github.com/moonbit-community/benchmark-202404) |

## Verdict

Vendor benchmark (moonbit-community/benchmark-202404, tinybench, Node v22.0.0 on an Apple M2 Max, MoonBit JS backend built with 'moon build --target js', compiler version not stated, April 2024). Results: an iterator pipeline over 189 records ran at 2,953,032 ops/s against 383,701 for a JS Array chain (7.7x) and 117,733 for JS Iterator Helpers (25.1x); MoonBit core's JSON5 parser ran at 22,908 ops/s against 2,887 for json5 npm (7.9x). All ratios are derived from page data, and no Wasm-backend numbers are in the repo.

## Use it when

- New code that must ship as both a JavaScript module and a Wasm/Wasm-GC module (or native binary) from one source, such as parsers, format converters and data transforms.
- Iterator-heavy data processing destined for the JS backend, where compiler fusion turns a combinator chain into one loop (338 ns versus 2,606 ns per run over 189 records in the vendor test).
- Porting a slow pure-JS parser to a compiled language while still exposing a JS API (JSON5: 22,908 versus 2,887 ops/s on a 6.3 KB config in the vendor test).
- Projects that can track a pre-1.0 language and accept toolchain-driven API changes.

## Skip it when

- To speed up existing JavaScript: the MoonBit output that won is itself plain JS loops, so rewriting a hot Array chain as a for loop gets the same effect without a new language.
- When you need the benchmarked code as it was measured: the json5 package is no longer in core, and Iter was migrated to external-iterator semantics in 0.7.1, so the April 2024 numbers describe a library that has since changed.
- Compute-bound Wasm where Rust is the alternative: the vendor's own fib(46) figures (snippet only) put MoonBit at 177.9 ms against Rust's 160.8 ms.
- Organisations that need an OSI-licensed compiler or plan commercial compiler modifications: the compiler is under the MoonBit Public License (relaxed SSPL, modifications for non-commercial purposes only).
- Code that needs a stable API: the core README says the library is experimental and the API is subject to change; the CHANGELOG lists breaking changes up to 0.10.x.

## How it is fast

On the iterator benchmark the compiler inlined the whole as_iter/flat_map/filter/map/fold chain and its closures into two nested while loops with an int counter (the committed target/js/release/build/bench_iter.js), so no intermediate arrays or per-element callbacks remain, while the JS baseline's Array flatMap/filter/map chain allocates a new array per stage. The JSON5 row compares MoonBit core's hand-written char-dispatch lexer and recursive-descent parser (compiled to JS) with the json5 npm package's parser.

## Compared with alternatives

Choose MoonBit for new code that should target JS and Wasm-GC from one small, fast-compiling language, as svgo.mbt did; for existing Kotlin, Scala or OCaml code use Kotlin/Wasm, the Scala.js WebAssembly backend or wasm_of_ocaml, and use AssemblyScript-based libraries such as json-as when the team already writes TypeScript.

## Integration

| | |
|---|---|
| **Form** | module (MoonBit standard library, shipped with the compiler and used through the moon build tool) |
| **Dependencies** | MoonBit toolchain (moon build system and compiler); the JS benchmark adds Node.js, tinybench and pnpm |
| **Minimum toolchain** | the matching MoonBit compiler release (core 0.10.13, 2026-09-15, pairs with compiler v0.10.13+cbb11c36f); the April 2024 benchmark's compiler version is not stated |
| **Platforms** | Wasm, Wasm-GC, JavaScript, native (C) and LLVM backends; the benchmark ran the JS backend on Node v22.0.0, Apple M2 Max |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the iter workload is 5 classes and 189 members (the expected answer is 8), the return value is discarded, and the only JS baselines are an eager Array chain and the Iterator Helpers chain; there is no hand-written JS loop, which is what the MoonBit compiler emitted, so 7.7x measures loop fusion rather than language speed.
- The '25x faster than JS' headline is the ratio to the slowest JS row (Iterator Helpers, 117,733 ops/s); against the ordinary Array chain the figure is 7.7x (derived from page data), and Kotlin/JS ran at 155,935 ops/s.
- The json5 row compares two different parsers with different outputs (MoonBit builds a JsonValue, inserting each key with @map.insert; json5 npm builds JS objects) and never checks that MoonBit's parse returned Ok. From reading the lexer (not executed), it handles every feature in the 6,294-byte input: one line comment, unquoted keys, trailing commas, plain decimals, no escapes.
- Licensing is split: core is Apache-2.0, but the compiler is under the MoonBit Public License (artifacts can be licensed freely; compiler modifications only for non-commercial purposes). The compiler README says the Wasm backend has been open-sourced, which contradicts the record's 'wasm backend not open-sourced'.

## Known shortcomings

- Vendor benchmark repo moonbit-community/benchmark-202404 (Node v22.0.0, Apple M2 Max): iter 7.7x vs plain JS and 25.1x vs JS Iterator Helpers, json5 7.9x; but the JS baseline is an eager array chain, the json5 parse result is never checked, the JS backend (not wasm) was measured and the MoonBit compiler version is unstated. Compiler licence is the non-OSI MoonBit Public License (usability mixed).
- Harness flaw: the compiled MoonBit output is plain JavaScript with fused while-loops, so the 7.7x iter figure measures loop fusion against an eager Array chain with no hand-written JS loop baseline; the dataset is 189 records with result 8, discarded; the '25x' is the ratio to the Iterator Helpers row only. The benchmarked json5 package is gone from core and Iter switched to external iterators in 0.7.1, so the April 2024 numbers are stale; the json5 parse result is never checked (a static read says the lexer covers the input's features). Record correction: the compiler README says the Wasm backend has been open-sourced (MoonBit Public License).

## Caveats and trade-offs

Benchmark is first-party (moonbit-community, April 2024, MoonBit pre-1.0) and runs MoonBit's JS backend, not its wasm backend. The iter baseline is an eager Array chain that allocates an intermediate array per stage while MoonBit's Iter is a fused push-style pipeline; no hand-written JS loop baseline is included, so the 7.7x/25x figures measure iteration strategy more than language. The json5 row compares two different parser implementations (MoonBit's port returns MoonBit JsonValue with a persistent map, json5 builds JS objects), and the harness discards the return value without checking that parse returned Ok; a zenn.dev reviewer (snippet only) attributes the json5 gain to char-code handling that hand-written JS could copy. MoonBit compiler version not stated. The fib(46) and compile-time numbers are snippet-only relays of vendor posts (moonbitlang.com and thenewstack.io unreachable) and show MoonBit slower than Rust. Licensing: moonbitlang/core is Apache-2.0, but the compiler (moonbitlang/moonbit-compiler) is under the MoonBit Public License, a non-OSI 'relaxed SSPL' that allows modification only for non-commercial use, and its wasm backend is not open-sourced; compiled artifacts may be licensed freely.

Wasm-first language with its own toolchain (moon build system); the core library is Apache-2.0 and the repo page does not state whether the compiler source is open. Young ecosystem.

## Maintenance

Actively developed (last commit 2026-10-11, 5,141 commits, 95 open issues, still pre-1.0 at 0.10.13); usability is mixed because core is Apache-2.0 but the compiler is source-available under a non-OSI licence, and the measured json5 package and push-style Iter no longer exist in core.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party benchmark repo exists (moonbit-community/benchmark-202404: bench_iter/bench.mjs and bench_json5/bench.mjs with tinybench, precompiled MoonBit JS committed) and states Node v22.0.0 and an Apple M2 Max, with build command 'moon build --target js' in package.json; the MoonBit compiler version is not stated, so it falls just short of A and stays C (first-party). The record's own fib/compile-time numbers are snippet-only relays of vendor posts and were replaced.
- **Verifier notes:** Upgraded evidence within tier C: found the vendor's public benchmark repo moonbit-community/benchmark-202404 comparing MoonBit's JS backend against plain JS in V8 (in-list baseline), 7.7x-25x on an iterator pipeline and 7.9x on JSON5 parsing; near-A except for the missing MoonBit compiler version. Shortcomings for the record: eager-array JS baseline vs fused iterators, different json5 parser implementations with unchecked results, JS backend rather than wasm, first-party, numbers from April 2024; compiler licence is non-OSI so usability set to mixed. Stars 1.2k, Apache-2.0 and last commit 2026-10-11 confirmed for moonbitlang/core.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/moonbitlang/core>
  - <https://github.com/moonbitlang/core/commits/main>
  - <https://github.com/moonbitlang/core/tree/main/bench>
  - <https://github.com/orgs/moonbitlang/repositories?q=bench>
  - <https://github.com/moonbitlang/benchmark>
  - <https://github.com/moonbitlang/moonbit-compiler>
  - <https://github.com/moonbit-community/benchmark-202404>
  - <https://github.com/moonbit-community/benchmark-202404/commits/master>
  - <https://github.com/moonbit-community/benchmark-202404/tree/master/bench_iter>
  - <https://github.com/moonbit-community/benchmark-202404/tree/master/bench_iter/moonbit-project>
  - <https://github.com/moonbit-community/benchmark-202404/tree/master/bench_json5/moonbit-core/json5>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/README.md>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_js.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_js2.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_moonbit.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/package.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/moonbit-project/bench_iter.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/package.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/bench.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/moon.pkg.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/parse.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/json5.mbti>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/target/js/release/build/json5/json5.js>
- **Sources the enricher read:**
  - <https://github.com/moonbitlang/core>
  - <https://raw.githubusercontent.com/moonbitlang/core/main/README.md>
  - <https://raw.githubusercontent.com/moonbitlang/core/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/moonbitlang/moonbit-compiler/main/README.md>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/README.md>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_js.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_js2.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/bench_iter_moonbit.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/package.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/moonbit-project/bench_iter.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/moonbit-project/target/js/release/build/bench_iter.js>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_iter/data/data.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/package.json>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/bench.mjs>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/data/data.json5>
  - <https://github.com/moonbit-community/benchmark-202404/tree/master/bench_json5/moonbit-core/json5>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/json5.mbti>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/parse.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/types.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/internal_types.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/lex_main.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/lex_misc.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/lex_prop.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/lex_number.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/lex_string.mbt>
  - <https://raw.githubusercontent.com/moonbit-community/benchmark-202404/master/bench_json5/moonbit-core/json5/util.mbt>
  - WebSearch: MoonBit JS backend benchmark vs JavaScript iterator 25x (snippets: moonbitlang.com/blog/js-support, moonbitlang.com/blog/beta-preview, thenewstack.io; no independent reproduction found)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/moonbitlang/core`) · [data/wave13/enrich/raw/github_com_moonbitlang_core.json](../../../data/wave13/enrich/raw/github_com_moonbitlang_core.json) (enrichment confidence 0.7)

</details>
