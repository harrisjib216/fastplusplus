# fast-es-module-lexer (@r1ck404/fast-es-module-lexer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (port of lexer.c) compiled to WebAssembly with simd128, JavaScript wrapper` · `MIT` · 🟢 active

> SIMD Rust-to-WASM port of es-module-lexer's lexer.c; same API and results, 4-18x faster parses in Node.

| | |
|---|---|
| **Beats** | es-module-lexer 1.7.0 (C lexer compiled to a 9.3 KB WASM module, with JS fallback) |
| **Claimed result** | react-dom (536 KB) 2.11 ms vs 0.12 ms (18.1x in Node, 7.1x in Chromium); 1.6 KB module 4.6 us vs 0.7 us (6.6x Node, 3.9x Chromium); typescript.js (9 MB) 34.6 ms vs 4.7 ms (7.4x Node); 644 lodash-es modules 2.51 ms vs 0.32 ms (7.9x Node, 4.2x Chromium). Startup about equal (1.5 ms vs 1.6 ms). |
| **Workload** | parse of JavaScript modules from 70 B to 9 MB (single files parsed repeatedly in a loop) and batches of real package files (88 zod/v4, 34 @vue, 644 lodash-es, 753 three/src, 210 zod files), Node 24.16 and headless Chromium 149, implementations alternating in fresh processes, best of 3 rounds. |
| **Metric** | latency |
| **Hardware** | Ryzen 7 7800X3D, Node 24.16 and Chromium 149 |
| **Compiler and flags** | rustc via cargo build --release for wasm32-unknown-unknown (rust/Cargo.toml: opt-level 3, lto fat, codegen-units 1, panic abort; rust/.cargo/config.toml rustflags: target-feature=+simd128,+bulk-memory,+sign-ext,+mutable-globals,+nontrapping-fptoint), then binaryen wasm-opt -O3 (packages/fast-es-module-lexer/build.mjs); Rust toolchain version not pinned. Baseline is the npm es-module-lexer 1.7.0 prebuilt WASM build. |
| **Adoption** | 1 star (fast-packages repo) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/r1ck404/fast-packages/tree/main/packages/fast-es-module-lexer) · [benchmark](https://github.com/R1ck404/fast-packages) |

## Verdict

First-party run on a Ryzen 7 7800X3D, Node 24.16 and headless Chromium 149, alternating fresh processes and keeping the best of 3 per-process medians: es-module-lexer 1.7.0's C-to-WASM build vs this SIMD Rust WASM port took 2.11 ms vs 0.117 ms on react-dom-client.production (536 KB, 18.1x; 7.1x in Chromium), 4.6 vs 0.7 us on a 1.6 KB module (6.6x), 34.6 vs 4.7 ms on typescript.js (9 MB, 7.4x) and 2.51 vs 0.32 ms on 644 lodash-es modules (7.9x; 4.2x in Chromium). Speedups include the faster source copy into WASM memory, not only the lexer. The baseline is es-module-lexer 1.7.0 (April 2025), two majors and several upstream performance releases behind the 3.0.x current when the package was made.

## Use it when

- Dev servers, bundlers and module loaders that lex many ES modules per build or page load (batches of real package files ran 5-8x faster in Node, 3.5-4.4x in Chromium).
- Large single bundles of 0.5-1.2 MB, where the SIMD skip-ahead pays most (6-18x in Node, 4.9-7.1x in Chromium on the published run; the low end is a non-ASCII file that takes the UTF-16 path).
- In-browser Node runtimes or web IDEs on V8, where the js-string-builtins copy path avoids the slow TextEncoder in Blink.
- Any project already on es-module-lexer 1.7.x that can add an npm alias: no code change and identical results, including the original's quirks.

## Skip it when

- Engines without WebAssembly SIMD (older Safari, some embedded runtimes): there is no scalar or asm.js fallback.
- Size-critical browser bundles: { initSync, parse } bundles to 21.6 KB minified / 9.3 KB gzip vs 14.1 / 6.5 KB for es-module-lexer, mostly the 16.6 KB WASM.
- Projects on es-module-lexer 2.x or 3.x (3.0.3 is current): only 1.7.0 is mirrored, and upstream has since added its own speedups (2.3.1 fast native UTF-16 copy into WASM memory on Node, 2.3.2 bulk skipping of identifier and number runs, 3.0.0 SIMD scanning of long comments and templates, one-import parse 354 to 238 ns), so the gap to current upstream is smaller than the published ratios and unmeasured.
- Teams that need a maintained, widely used dependency: one author, 1 star, no issues filed, under three weeks old, and the npm latest (1.7.3) is not in the GitHub repository.
- Workloads that re-parse an identical string expecting cold-parse cost (benchmarks, profiling): since 1.7.2 the package returns a cached scan for repeated sources of 4,096-1,048,576 code units.

## How it is fast

lexer.c is ported function by function to no_std Rust, but the main loop stops only at the characters that can change state (( ) { } ' " / ` and the pairs ex, im, cl); a SIMD nibble-table classifier (two u8x16_swizzle lookups per 16 bytes, the simdjson-style character classification) finds them 64 characters at a time, and lastTokenPos is derived from a non-whitespace mask instead of being updated per character. Strings, templates and comments are skipped with SIMD scans, the source is narrowed to one byte per UTF-16 unit, and it is copied into WASM memory at memcpy speed (Buffer.latin1Write/ucs2Write in Node, a js-string-builtins WASM loop in Chromium, TextEncoder.encodeInto elsewhere) instead of the original's charCodeAt loop into a Uint16Array. Results return as one Int32Array rather than one WASM call per field, and specifiers without escapes are sliced instead of eval'd.

## Compared with alternatives

Pick it over es-module-lexer (the catalogued baseline) when parse time of many or large modules matters and the host has WASM SIMD; keep es-module-lexer when bundle size, the asm.js fallback or a long track record matter more. No other ES-module lexer is catalogued; the general WASM siblings (sax-wasm, markdown-wasm, source-map) solve different problems.

## Integration

| | |
|---|---|
| **Form** | module (npm package @r1ck404/fast-es-module-lexer; one ESM file with the WASM embedded as base64, plus browser.mjs selected by the browser export condition) |
| **Dependencies** | none at run time (Rust wasm32 toolchain and binaryen only to rebuild the WASM) |
| **Minimum toolchain** | Node 18+ (engines field); any engine with WebAssembly SIMD (simd128); rebuild needs rustc with the wasm32-unknown-unknown target (version not pinned) and binaryen ^132 |
| **Platforms** | any WebAssembly host with SIMD: Node, Chromium, Firefox, WebKit (browser test suite runs in all three); Deno and Bun take the TextEncoder or builtins copy path |
| **Thread safety** | not documented; one module-level WASM instance and a module-level cache per JS realm, so each worker gets its own (JS is single-threaded per realm) |
| **Drop-in for the baseline** | partial — same exports, results and errors as es-module-lexer 1.7.0 and installed under its name, but no /js asm.js subpath, it needs WASM SIMD, and malformed inputs on which the original reads outside its source are answered as a fresh original instance would (deterministic), and nesting deeper than 1024 brackets / 512 import( calls is handled where the original goes wrong |

## Gotchas

- Benchmark caveat: commit 7df1749 (2026-09-30, release 1.7.2) added a one-entry cache that reuses the last WASM scan when the identical string (4,096-1,048,576 UTF-16 units) is parsed again; the repo's bench/es-module-lexer.bench.mjs parses the same f.code string in a loop, so rerunning it on the current code times cache hits (result-object construction only) for the 51 KB, 513-536 KB, 948 KB and 1 MB single-file rows. The published numbers (results file of 2026-09-28) predate the cache; the batch rows (different files in turn) and the 70 B, 1.6 KB and 9 MB rows fall outside it, and three.module (1.2 MB) only if it exceeds 1,048,576 code units.
- The npm latest 1.7.3 (published 2026-09-30 19:09 UTC) has no matching commit: the repo stops at 1.7.2, yet 1.7.3 ships a different init (compile-only, instance created on first parse), a JS text decoder instead of the 356-byte decoder module, and the older 1.7.1 WASM binary rather than 1.7.2's.
- The Rust toolchain is not pinned: lib.rs and build.mjs are byte-identical between c59fa38 and HEAD, yet 1.7.1 and 1.7.2 embed different WASM binaries (22,068 vs 22,408 base64 characters), so a rebuild will not reproduce the measured module bit for bit.
- Deliberate behaviour differences on malformed code (documented): very deep nesting and record overflows are answered as a fresh original instance would, so results can differ from a long-lived es-module-lexer instance whose answer depends on earlier parses.

## Known shortcomings

- Raised C to A (public bench with raw results, Cargo and wasm-opt flags, Ryzen 7 7800X3D; Rust toolchain unpinned), but commit 7df1749 (2026-09-30) added a repeated-parse cache after the published 2026-09-28 numbers, so rerunning the bench on HEAD times cache hits for the 51 KB-1 MB rows; the baseline is es-module-lexer's C WASM build, not JS.
- Since 7df1749 (1.7.2) repeat parses of the same 4,096-1,048,576-unit string are served from a one-entry cache, so the repo's bench now times cache hits; the published 2026-09-28 numbers predate it. Stale baseline: es-module-lexer 1.7.0 (2025-04) versus current 3.0.3, whose 2.3.1-3.0.0 releases added a Node fast copy and SIMD comment/template scans (354 to 238 ns per parse), so 18x overstates the gain over current upstream. npm latest 1.7.3 has no repo commit and ships the older 1.7.1 wasm; the same lib.rs and build.mjs produced different wasm bytes (unpinned toolchain).

## Caveats and trade-offs

The bench imports 'es-module-lexer' and calls initSync, so the baseline ran its default C-to-WASM build: this is a SIMD Rust WASM port against scalar C WASM, not WASM against JS. The published numbers come from the 2026-09-28 results file, measured before commit 7df1749 (2026-09-30, the 1.7.2 patch release) added a cache that reuses the last WASM scan when the same 4,096-1,048,576-code-unit source is parsed again (index.mts cachedSource; absent at a3e28b4 on 2026-09-29). Because bench/es-module-lexer.bench.mjs parses the same string in a loop, rerunning it on the current code would time cache hits for the 51 KB to 1 MB single-file rows (react-dom 18.1x among them); batch rows and the 1.6 KB and 9 MB rows are unaffected. First-party numbers on a days-old, 1-star repo; Rust toolchain unpinned. The repo URL points at the package directory of R1ck404/fast-packages. [retier] The bench imports 'es-module-lexer' and calls initSync, so the baseline ran its default C-to-WASM build: this is a SIMD Rust WASM port against scalar C WASM, not WASM against JS. The published numbers (2026-09-28 results file) predate commit 7df1749 (2026-09-30, 1.7.2), which added a one-entry cache that reuses the last WASM scan when the same 4,096-1,048,576-code-unit string is parsed again; the repo's bench parses the same string in a loop, so rerunning it on current code times cache hits. Stale baseline: es-module-lexer 1.7.0 (2025-04) versus current 3.0.3, whose 2.3.1-3.0.0 releases added a Node fast copy and SIMD comment/template scans (354 to 238 ns per parse), so 18x overstates the gain over current upstream. npm latest 1.7.3 has no repo commit and ships the older 1.7.1 wasm; the same lib.rs and build.mjs gave different wasm bytes, so the measured build is not reproducible from the public sources.

Same exports and results as es-module-lexer; WASM is about 16.6 KB (6.9 KB gzipped) vs 9.3 KB for the original and the browser bundle is larger (21.6 KB vs 14.1 KB minified); requires WebAssembly SIMD; SIMD nibble-table classifier over 64-character blocks.

## Maintenance

Active but brand new (37 commits, 2026-09-26 to 2026-10-01, single author, 1 star, no issues), MIT-licensed and installable by npm alias; it mirrors a stale es-module-lexer 1.7.0, the shipped npm 1.7.3 is not reproducible from the repository, and the current code caches repeated parses, so re-benchmark on your own varied inputs against current es-module-lexer before relying on the published ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C: the README table is backed by public benchmark code (bench/es-module-lexer.bench.mjs, bench/harness.mjs, bench/interleave.mjs, plus the browser bench) and raw data (results/es-module-lexer-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-14-20-431Z.md, whose times match the README); the build flags are public (rust/Cargo.toml: opt-level 3, fat LTO, codegen-units 1; rust/.cargo/config.toml: wasm32-unknown-unknown with +simd128 and others; build.mjs: binaryen wasm-opt -O3) and the CPU is named (Ryzen 7 7800X3D, Node 24.16, Chromium 149). Only the Rust toolchain version is unpinned.
- **Retiered** A to C: Enricher: the bench on current code times a one-entry cache added in 7df1749 (1.7.2), the shipped npm 1.7.3 carries the older 1.7.1 wasm and the same lib.rs and build.mjs produce different wasm bytes (unpinned toolchain), so the published numbers cannot be reproduced from the public sources; the baseline es-module-lexer 1.7.0 is two major versions behind an upstream that has since added its own SIMD scans. First-party, unreproducible build: A to C.
- **Verifier notes:** All claimed numbers match the README table and the 2026-09-28 raw results file. Metadata confirmed: MIT (package LICENSE carries es-module-lexer's MIT; rest of repo MIT), 1 star, 37 commits, last commit 2026-10-01. Main shortcoming to record: the current release caches repeated parses of the same source, so the public bench no longer measures cold parses for mid-size single files; published numbers predate the cache, hence no reject.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/R1ck404/fast-packages>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/commits/main/packages/fast-es-module-lexer>
  - <https://github.com/R1ck404/fast-packages/commit/7df1749>
  - <https://github.com/R1ck404/fast-packages/tree/main/bench>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/index.mts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/a3e28b4/packages/fast-es-module-lexer/index.mts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/a3e28b4/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/test/repeated.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/build.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/rust/.cargo/config.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/es-module-lexer.bench.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/harness.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/es-module-lexer-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-14-20-431Z.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/index.mts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/build.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/rust/.cargo/config.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-es-module-lexer/test/repeated.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/c59fa38/packages/fast-es-module-lexer/index.mts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/c59fa38/packages/fast-es-module-lexer/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/c59fa38/packages/fast-es-module-lexer/build.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/c59fa38/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/a3e28b4/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/73a1829/packages/fast-es-module-lexer/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/es-module-lexer.bench.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/harness.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/corpus.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package-lock.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/es-module-lexer-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-14-20-431Z.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/es-module-lexer-browser-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-42-40-358Z.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/es-module-lexer-orig_vs_prev_vs_fast-interleaved-2026-09-26T23-58-20-241Z.md>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/issues?q=is%3Aissue>
  - <https://registry.npmjs.org/@r1ck404%2ffast-es-module-lexer>
  - <https://registry.npmjs.org/@r1ck404/fast-es-module-lexer/-/fast-es-module-lexer-1.7.1.tgz>
  - <https://registry.npmjs.org/@r1ck404/fast-es-module-lexer/-/fast-es-module-lexer-1.7.2.tgz>
  - <https://registry.npmjs.org/@r1ck404/fast-es-module-lexer/-/fast-es-module-lexer-1.7.3.tgz>
  - <https://registry.npmjs.org/es-module-lexer>
  - <https://github.com/guybedford/es-module-lexer/releases>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:r1ck404-fast-packages-fast-es-module-lexer`) · [data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_es_module_lexer.json](../../../data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_es_module_lexer.json) (enrichment confidence 0.7)

</details>
