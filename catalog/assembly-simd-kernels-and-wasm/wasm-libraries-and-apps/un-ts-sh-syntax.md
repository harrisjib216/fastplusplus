# sh-syntax

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> mvdan/sh (shfmt) shell parser and formatter compiled to WebAssembly with TinyGo; 4.3x faster than the GopherJS mvdan-sh package.

| | |
|---|---|
| **Beats** | mvdan-sh 0.10.1 (npm; archived GopherJS build of mvdan/sh, pure JavaScript) |
| **Claimed result** | 18.33 ms/iter vs 79.47 ms/iter for mvdan-sh, 4.34x faster (summary line on page); synckit worker variant 18.38 ms. |
| **Workload** | Formatting (print) of the shell script test/fixtures/install.sh with the same options through sh-syntax (TinyGo wasm) and mvdan-sh, measured with mitata under Node. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max (\~2.81 GHz), node 18.20.8 arm64-darwin |
| **Compiler and flags** | TinyGo (version not stated in package.json, CI workflows or README): tinygo build -o main.wasm -target ./target.json --no-debug, target.json inherits 'wasm' with ldflags --initial-memory=10485760 --max-memory=1073741824 -zstack-size=1048576; go.mod go 1.25.0, mvdan.cc/sh/v3 v3.13.1 (current; the benchmark predates this rebuild). Benchmark source: benchmark/index.js (mitata). |
| **Adoption** | 68 stars, 8 forks; recommended by upstream mvdan/sh as the replacement for its archived mvdan-sh npm package and used by prettier-plugin-sh |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/un-ts/sh-syntax) · [benchmark](https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/benchmark.txt) |

## Verdict

mitata under Node 18.20.8 on an Apple M1 Max formatted the repo's 140 KB, 4,352-line test/fixtures/install.sh (nvm.sh content) as bash with fixed printer options. sh-syntax took 18.33 ms/iter (synckit worker 18.38 ms) against 79.47 ms/iter for mvdan-sh 0.10.1 (GopherJS), 4.34x. The run dates from 2025-04-08, used the wasm built against mvdan/sh v3.11.0 with an unstated TinyGo version, and its sh-syntax times include per-call wasm instantiation.

## Use it when

- Formatting or parsing shell scripts from JavaScript (Prettier via prettier-plugin-sh, editors, CI linters, web playgrounds), where the only alternative is the archived mvdan-sh.
- Larger scripts: the 140 KB, 4,352-line benchmark fixture formats in about 18 ms on an M1 Max under Node 18, against 79 ms for mvdan-sh.
- Browser apps that can fetch or bundle the roughly 750 KB main.wasm (CDN fetch or Vite wasm?init loader).
- Node code that needs a synchronous call: the synckit worker variant measured the same per-call time (18.38 ms).

## Skip it when

- Hot loops over many tiny snippets: every call builds a new Go runtime and WebAssembly instance with a 10 MB initial memory, a fixed cost the benchmark (one large file) does not isolate.
- AST-transform pipelines: print(ast, { originalText }) never sends the AST to wasm; it re-parses and formats originalText, so edits made to the AST are lost.
- Bundle-size-sensitive pages: the wasm alone is about 750 KB before compression.
- When you can shell out to the native shfmt Go binary; native Go was not part of the comparison.
- Code that passes raw numeric LangVariant values written for 0.5.x: 0.6.0 switched to bit flags (LangBash 0 to 1, LangPOSIX 1 to 2, LangAuto 4 to 32).

## How it is fast

The speedup comes from the compilation target, not a new algorithm: the Go code runs as TinyGo-compiled WebAssembly (about 750 KB main.wasm) instead of GopherJS-transpiled JavaScript. Input is copied into wasm linear memory, the Go side parses and optionally prints, and the result is returned as one null-terminated JSON string (written with easyjson's jwriter) that JS decodes and JSON.parses. On the published run the wasm build executed about 289M instructions per format against 1.29G for mvdan-sh.

## Compared with alternatives

No catalogued sibling parses or formats shell; the nearest are wasm text parsers for other languages (markdown-wasm, md4w, es-module-lexer). Use sh-syntax whenever you need shfmt-compatible parsing or formatting from JavaScript, since its only alternative, mvdan-sh, is archived and was 4.3x slower on the published run.

## Integration

| | |
|---|---|
| **Form** | module (npm package, ESM and CJS, shipping a prebuilt TinyGo main.wasm) |
| **Dependencies** | none at runtime (vendored TinyGo wasm_exec glue); synckit only for a synchronous wrapper; rebuilding main.wasm needs Go, TinyGo and easyjson |
| **Minimum toolchain** | Node &gt;= 16 per package.json engines (CI tests Node 20, 22, 24 and 26); any browser with WebAssembly; rebuild needs go 1.25 (go.mod) and TinyGo (version not stated; glue copied from TinyGo v0.41.1) |
| **Platforms** | any JavaScript runtime with WebAssembly; CI runs on macOS, Windows and Linux |
| **Thread safety** | not documented; each call creates its own wasm instance, so concurrent async calls share no Go state |
| **Drop-in for the baseline** | partial: same mvdan/sh parser and printer options, but exposed as async parse/print functions with an options object instead of mvdan-sh's syntax.NewParser/NewPrinter object API |

## Gotchas

- Per-call instantiation: processor() runs new Go() and WebAssembly.instantiate on the cached bytes for every parse or print (as it already did in April 2025), so the measured 18.33 ms includes instance creation and Go runtime start-up; the mitata memory column (28.52 KB to 9.82 MB per iteration) matches a fresh 10 MB linear memory per call.
- Latent memory-safety bug, found by reading the code (not reproduced): main.go's wasmAlloc returns \*[]byte, the address of the heap-allocated slice header, not of its backing array, and processor.ts copies the whole input to that address and passes it to process() as the slice data pointer. Writes therefore run past the 12-byte header; this appears to work only because, in each fresh per-call heap, the header sits directly before the slice's own backing array.
- The benchmark numbers are stale and the build is not reproducible from CI: benchmark.txt dates from 2025-04-08 (wasm built against mvdan/sh v3.11.0), while main.wasm was rebuilt against v3.13.1 in July 2026 and again in September 2026. main.wasm is a checked-in binary built locally (issue #115, 'Build easyjson and wasm on CI', is still open). The TinyGo version appears only in the vendored glue's header: TinyGo v0.41.1 now, and TinyGo commit 3e60eeb in the April 2025 copy.
- benchmark/index.js still passes variant 0, which after 0.6.0 is not LangBash (now 1). It still runs as bash only because mvdan/sh v3.13 maps the legacy zero value (langBashLegacy) to LangBash. In the synckit row the hardware counters (434.86k cycles) see only the blocked main thread, not the worker doing the work.

## Known shortcomings

- TinyGo version unstated; benchmark.txt dates from 2025-04-08, older than the July 2026 wasm rebuild against mvdan/sh v3.13.1; the mvdan-sh 0.10.1 baseline is an archived GopherJS build of the same parser.
- Each processor() call builds a new Go runtime plus WebAssembly instance (10 MB initial memory), so the 18.33 ms includes instantiation; print(ast) ignores the AST and re-parses the original text. Possible memory-safety bug from code reading (not reproduced): main.go's wasmAlloc returns \*[]byte (the slice-header address) and JS writes the whole input there, past the 12-byte header, which seems to work only because of the fresh-heap layout. main.wasm is built locally and checked in (issue #115 open); the TinyGo version appears only in the vendored glue header (v0.41.1 now, 3e60eeb in the April 2025 copy); benchmark variant 0 still runs as bash via upstream's langBashLegacy.

## Caveats and trade-offs

Single workload (formatting test/fixtures/install.sh with fixed options), first-party, Node 18 on Apple Silicon, TinyGo version unstated. benchmark.txt was last regenerated 2025-04-08, before the wasm was rebuilt against mvdan/sh v3.13.1 in July 2026, so the numbers are stale relative to the shipped main.wasm. The baseline mvdan-sh 0.10.1 is an older, archived GopherJS transpilation of the same Go parser (upstream archived it for poor performance), so both sides run different versions of the same code and the ratio measures TinyGo-wasm vs GopherJS rather than wasm vs a hand-written JS parser.

Wasm must be loaded asynchronously (fetch or bundler wasm?init) and uses Go's wasm_exec glue; the synckit variant is needed for a synchronous API in Node. Wraps mvdan/sh, so shell dialect support follows that project.

## Maintenance

Active (107 commits, last 2026-09-24, CI on four Node versions and three OSes), MIT and endorsed upstream as the mvdan-sh replacement. But the shipped main.wasm is a locally built binary, the published benchmark predates it, and wasmAlloc hands JS a slice-header pointer (latent memory-safety bug, from code reading).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** benchmark/benchmark.txt (source benchmark/index.js, mitata, Apple M1 Max, node 18.20.8) shows sh-syntax 18.33 ms/iter vs mvdan-sh 79.47 ms/iter (4.34x), but the TinyGo version is stated nowhere (package.json, CI workflows, README), so not A; first-party with partial methodology is C. The file was last regenerated on 2025-04-08, before the wasm was rebuilt against mvdan/sh v3.13.1 (2026-07-06) and the 2026-09 simplify feature, so the numbers do not describe the current main.wasm.
- **Verifier notes:** Numbers match benchmark.txt and the README (18.33 vs 79.47 ms/iter, 4.34x; synckit 18.38 ms). Downgraded A to C: TinyGo version missing and the benchmark predates the July 2026 rebuild of main.wasm; record those as shortcomings. Upstream mvdan/sh README confirms mvdan-sh is archived 'given its poor performance' and points users to sh-syntax. MIT, last commit 2026-09-24, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/benchmark.txt>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/README.md>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/index.js>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/package.json>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/target.json>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/go.mod>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/main.go>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/yarn.lock>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/.github/workflows/release.yml>
  - <https://github.com/un-ts/sh-syntax>
  - <https://github.com/un-ts/sh-syntax/tree/main/.github/workflows>
  - <https://github.com/un-ts/sh-syntax/commits/main>
  - <https://github.com/un-ts/sh-syntax/commits/main/benchmark/benchmark.txt>
  - <https://raw.githubusercontent.com/mvdan/sh/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/un-ts/sh-syntax>
  - <https://github.com/un-ts/sh-syntax/tree/main/processor>
  - <https://github.com/un-ts/sh-syntax/commits/main/vendors/wasm_exec.cjs>
  - <https://github.com/un-ts/sh-syntax/commits/main/main.wasm>
  - <https://github.com/un-ts/sh-syntax/issues?q=is%3Aissue>
  - <https://github.com/un-ts/sh-syntax/issues/45>
  - <https://github.com/un-ts/sh-syntax/issues/115>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/README.md>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/benchmark.txt>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/index.js>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/benchmark/worker.mjs>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/package.json>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/target.json>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/go.mod>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/main.go>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/processor/main.go>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/processor/structs.go>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/src/browser.ts>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/src/processor.ts>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/src/types.ts>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/src/shim.ts>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/vendors/wasm_exec.cjs>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/test/fixtures/install.sh>
  - https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/main.wasm (HEAD request for size only)
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/c500f6d/vendors/wasm_exec.cjs>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/28d68ba/vendors/wasm_exec.cjs>
  - <https://raw.githubusercontent.com/un-ts/sh-syntax/c500f6d/src/processor.ts>
  - <https://raw.githubusercontent.com/mvdan/sh/v3.13.1/syntax/parser.go>
  - <https://raw.githubusercontent.com/mvdan/sh/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/un-ts/sh-syntax`) · [data/wave13/enrich/raw/github_com_un_ts_sh_syntax.json](../../../data/wave13/enrich/raw/github_com_un_ts_sh_syntax.json) (enrichment confidence 0.8)

</details>
