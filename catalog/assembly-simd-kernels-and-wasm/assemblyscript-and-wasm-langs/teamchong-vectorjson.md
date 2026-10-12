# VectorJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig (simdjson port compiled to WebAssembly SIMD) with TypeScript` · `Apache-2.0` · 🟢 active

> Incremental streaming partial-JSON parser for LLM tool calls (Zig to WASM plus TypeScript); beats AI SDKs' re-parse-every-chunk loops.

| | |
|---|---|
| **Beats** | Stock streaming/partial JSON parsers in the Vercel AI SDK, Anthropic SDK, TanStack AI and OpenClaw (JavaScript, run under Bun); JSON.parse for one-shot parsing |
| **Claimed result** | 1 KB: Vercel AI SDK 3.9 ms vs 283 µs (14x); Anthropic SDK 3.3 ms vs 283 µs (12x). 5 KB: Vercel AI SDK 23.1 ms vs 739 µs (31x); Anthropic SDK 34.7 ms vs 739 µs (47x). 50 KB: Anthropic SDK 3.39 s vs 2.7 ms (1255x). 100 KB: Vercel AI SDK 6.1 s vs 6.6 ms (920x); Anthropic SDK 13.4 s vs 6.6 ms (2028x). One-shot: JSON.parse is faster (1 KB 2.16M ops/s vs 1.37K ops/s). |
| **Workload** | Streaming an LLM tool_use JSON block in \~12-character chunks, materialising a partial object on every chunk, payloads of 1 KB to 100 KB. |
| **Metric** | latency |
| **Hardware** | GitHub Actions ubuntu x86_64 runner (CPU model not stated) |
| **Compiler and flags** | zig build -Doptimize=ReleaseSmall for wasm32 with simd128 (Zig 0.15.2 in CI), then wasm-opt -Oz --enable-simd --enable-bulk-memory and others, JS bundled with bun build --minify; benchmarks run as 'cd bench/ai-parsers && bun --expose-gc bench.mjs' and 'bun --expose-gc bench/parse-stream.mjs' in the CI benchmark job with Bun 'latest' (unpinned); baselines pinned in bench/ai-parsers/package.json: @anthropic-ai/sdk 0.74.0, ai ^6.0.86, @tanstack/ai ^0.5.0, partial-json ^0.1.7 |
| **Adoption** | 18 stars |
| **Last commit** | 2026-03-10 |
| **Links** | [repository](https://github.com/teamchong/vectorjson) · [benchmark](https://github.com/teamchong/vectorjson) |

## Verdict

The project's CI benchmark (GitHub Actions ubuntu x86-64 runner, Bun latest, CPU unnamed) streams a synthetic JSON payload in 12-character chunks and reads a partial object after every chunk: stock parsers from Vercel AI SDK, Anthropic SDK 0.74.0, TanStack AI and partial-json re-parse the concatenated buffer each time, taking 3.2-3.9 ms at 1 KB and 6.1-13.4 s at 100 KB, against 283 us and 6.6 ms for VectorJSON's feed() plus getValue() (11x-2028x). Its one-shot parse() is slower than JSON.parse at every size measured.

## Use it when

- Agent UIs that render partial tool_use or structured-output JSON on every token, payloads from about 1 KB up, where the SDK's partial parser re-parses the whole buffer (README on Bun: 11-14x at 1 KB, 31-47x at 5 KB, 660-2000x at 50-100 KB).
- Field-level reactions while streaming: act as soon as the tool name completes, append a code string's new characters to an editor, abort the LLM stream early on a wrong tool.
- Mixed LLM output with &lt;think&gt; blocks, code fences or prose around the JSON, which createEventParser skips to find the JSON value.
- Reading a few fields from a multi-megabyte JSON document through the lazy Proxy (README: 2.3 vs 4.6 ms for one field of a 2.2 MB payload against JSON.parse).

## Skip it when

- One-shot parsing of complete JSON: JSON.parse is far faster on small inputs (1 KB: 2.16M vs 1.37K ops/s) and still slightly faster at 500 KB and 2 MB.
- When streamed JSON must be validated: createParser only reports closing-bracket underflow as an error, and malformed scalar tokens become null.
- When each chunk's partial must be an immutable snapshot (React state updates, diffing previous against current partial): getValue() hands back the same object, mutated by later feed() calls.
- CommonJS-only projects or runtimes without WebAssembly SIMD128 (package is ESM-only, Node &gt;= 20).
- If an O(n) incremental JavaScript parser already fits (for example @streamparser/json, which the benchmark installs but never measures): the headline gap is algorithmic, not WASM or SIMD.

## How it is fast

It turns the O(n^2) pattern buffer += chunk; parsePartialJson(buffer) into O(n): each feed() appends bytes to a WASM buffer where a Zig structure tracker (bracket depth, string and escape state, 16-byte SIMD128 skip inside strings) updates completion status, and a JavaScript byte scanner (spScan) extends one mutable live object in place, so getValue() just returns the reference. The simdjson-derived zimdjson DOM parser compiled to WASM SIMD128 backs one-shot parse() and tape/Proxy access, not the streaming numbers.

## Compared with alternatives

Pick it over json-as (AssemblyScript JSON that beats JSON.parse on whole-document deserialization in V8) when input arrives as a token stream and you need partial objects or per-field events; for complete documents json-as or plain JSON.parse is faster.

## Integration

| | |
|---|---|
| **Form** | npm module (ESM only; WASM embedded as base64, about 148 KB JS, 47 KB gzipped) |
| **Dependencies** | none at runtime; building from source needs Zig 0.15.2, Bun and wasm-opt |
| **Minimum toolchain** | Node.js 20+, Bun, Deno, browsers or Cloudflare Workers with WebAssembly SIMD128 |
| **Platforms** | any JavaScript runtime with WebAssembly SIMD128 |
| **Thread safety** | not documented; parser objects are single-threaded, and getTapeBuffer()/importTape() move parsed tapes between workers |
| **Drop-in for the baseline** | partial: replaces the partial-JSON call in an SDK accumulation loop (the benchmark ships patches for Vercel AI SDK, Anthropic SDK MessageStream and TanStack AI), but its API differs from JSON.parse and from each SDK's parser, and getValue() returns a live mutable object rather than a fresh snapshot |

## Gotchas

- Live object: while incomplete, getValue() returns the same object that later feed() calls mutate; clone it before storing a snapshot. That is also why the benchmark's 'both sides materialize a partial object per chunk' framing is uneven: stock parsers build a fresh object graph per chunk, VectorJSON returns a reference in O(1).
- Weak validation in streaming mode: src/zig/stream.zig only flags '}'/']' underflow (it counts '{' and '[' together, so mismatched bracket kinds pass), and spScan in src/js/index.ts turns any scalar JSON.parse cannot read into null inside a try/catch, so malformed model output can finish as 'complete' with nulls instead of 'error'.
- Docs contradict the code: the README 'How It Works' section and the benchmark's comment say each feed()/getValue() re-runs the SIMD parse over the accumulated buffer, but the code scans each new byte once (Zig structure tracker plus a JavaScript scanner) and zimdjson is only used for one-shot parse() and tapes, so WASM SIMD contributes little to the 14x-2028x figures.
- Harness asymmetries: when a stock run is slow (warmup x 4 &gt; 30 s, the 100 KB rows) the stock time is one cold warmup run while VectorJSON is the median of 3 after 2 warmups; Bun is 'latest' (unpinned) on an unnamed GitHub Actions CPU; the README one-shot rows give VectorJSON exactly 1.37K ops/s at both 1 KB and 10 KB, which points to a fixed per-call cost of about 0.7 ms in parse().

## Known shortcomings

- The win is algorithmic (an O(n) live object built by a JavaScript byte scanner against O(n^2) re-parsing), so the Wasm/SIMD gain is not isolated; some 100 KB stock rows are single cold runs; CPU not named, Bun unpinned; weak fit for the AssemblyScript category.
- The streaming path is a Zig bracket tracker plus a JavaScript byte scanner (spScan) mutating one live object, and getValue() returns an O(1) reference; zimdjson and SIMD are unused there, so the README 'How It Works' section and the benchmark comment contradict the code and the 14x-2028x figures are an O(n) versus O(n^2) algorithm difference, not a wasm or SIMD win; the stock 100 KB rows are single cold runs; @streamparser/json is installed but never benchmarked. Validation gap: streaming only flags '}' or ']' underflow, malformed scalars silently become null, and mismatched bracket kinds pass.

## Caveats and trade-offs

The 14x-2028x streaming figures come from an algorithmic difference, not raw parse speed: the stock loop does buffer += chunk and re-parses the whole buffer into a fresh object graph on every 12-character chunk (O(n^2)), while VectorJSON's createParser().getValue() returns the same live object that a JavaScript byte-by-byte scanner (spScan in src/js/index.ts) extends in place, so per-chunk work and allocation differ by design; the bench comment saying getValue() re-parses the accumulated buffer with SIMD does not match the code, and no WebAssembly or SIMD contribution is isolated. Where a stock run is slow (warmup x 4 &gt; 30 s, e.g. Anthropic SDK and OpenClaw at 100 KB) the stock time is a single cold warmup run, while VectorJSON is the median of 3 runs after 2 warmups. One-shot JSON.parse is much faster on small inputs (1 KB: 2.16M vs 1.37K ops/s) and still slightly faster at 500 KB-2 MB. Runtime is Bun (JavaScriptCore), not V8; first-party CI numbers, CPU not named, Bun version unpinned. The streaming engine is zimdjson (a Zig port of simdjson) vendored in deps/zimdjson. Fits a JSON-parsing category better than assemblyscript-and-wasm-langs. [retier] The 14x-2028x streaming figures come from an algorithmic difference, not raw parse speed: the stock loop does buffer += chunk and re-parses the whole buffer into a fresh object graph on every 12-character chunk (O(n^2)), while VectorJSON's createParser().getValue() returns the same live object that a JavaScript byte-by-byte scanner (spScan in src/js/index.ts) extends in place with a Zig bracket tracker (src/zig/stream.zig) only counting structure; zimdjson and SIMD are used only for one-shot parse() and tapes, so no WebAssembly or SIMD contribution is isolated in the streaming rows, and the README 'How It Works' section and the benchmark comment (which say each feed()/getValue() re-runs the SIMD parse over the accumulated buffer) contradict the code. One-shot JSON.parse is faster (1 KB 2.16M ops/s vs 1.37K ops/s, a fixed per-call cost of about 0.7 ms in parse()). Harness asymmetries: when a stock run is slow (the 100 KB rows) the stock time is one cold warm-up run while VectorJSON is the median of 3 after 2 warm-ups; Bun is 'latest' (unpinned) on an unnamed GitHub Actions CPU; @streamparser/json is installed but never benchmarked. Live object: getValue() returns the same object later feed() calls mutate. Weak validation in streaming mode: only '}' or ']' underflow is flagged (mismatched bracket kinds pass) and malformed scalars become null inside a try/catch, so malformed input can finish as 'complete'.

Not a JSON.parse replacement: README says JSON.parse wins on one-shot parses of small payloads and is roughly equal at 500 KB+. Wins come from incremental O(n) streaming with a live object versus re-parsing the whole buffer per chunk. WASM SIMD required.

## Maintenance

Apache-2.0 npm package (0.5.1; 15 releases from 2026-02-16 to 2026-03-10), 18 stars, no issues filed and no commits since 2026-03-10, so 'active' is generous; easy to adopt for streaming UI work, but young, single-maintainer, and its streaming parser does not validate JSON grammar.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party numbers from the project's own bench/ai-parsers/bench.mjs run in its GitHub Actions benchmark job (ubuntu-latest, Bun 'latest', CPU model not named), so code is public but CPU and runtime version are missing: C.
- **Retiered** C to D: Enricher: the streaming path that produces the 14x-2028x rows is a Zig bracket tracker plus a JavaScript byte scanner mutating one live object with an O(1) getValue(), while the stock loop re-parses the whole buffer per 12-character chunk, so the figures measure an O(n) versus O(n^2) algorithm with a JS scanner, not wasm or SIMD (zimdjson is unused in streaming); the README and bench comment contradict the code, the 100 KB stock rows are single cold runs, and one-shot JSON.parse is faster. No valid measurement of a wasm speedup: C to D.
- **Verifier notes:** All claimed numbers match the README Benchmarks section (1 KB 14x/12x, 5 KB 31x/47x, 50 KB Anthropic 1255x, 100 KB 920x/2028x, one-shot 2.16M vs 1.37K ops/s). Metadata checked: Apache-2.0, 18 stars, 188 commits, last commit 2026-03-10, not a fork. Main shortcoming: the win is incremental O(n) live-object building versus O(n^2) re-parse, largely in JavaScript; the WebAssembly/SIMD part is not what the headline numbers measure, and category fit is weak.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/teamchong/vectorjson>
  - <https://github.com/teamchong/vectorjson/commits>
  - <https://github.com/teamchong/vectorjson/tree/main/src>
  - <https://github.com/teamchong/vectorjson/tree/main/src/js>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/bench/ai-parsers/bench.mjs>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/bench/ai-parsers/package.json>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/build.zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/package.json>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/src/js/index.ts>
- **Sources the enricher read:**
  - <https://github.com/teamchong/vectorjson>
  - <https://github.com/teamchong/vectorjson/issues?q=is%3Aissue>
  - <https://github.com/teamchong/vectorjson/tree/main/src>
  - <https://github.com/teamchong/vectorjson/tree/main/src/zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/bench/ai-parsers/bench.mjs>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/bench/ai-parsers/package.json>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/bench/parse-stream.mjs>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/build.zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/package.json>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/src/js/index.ts>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/src/zig/stream.zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/src/zig/main.zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/src/zig/simd.zig>
  - <https://raw.githubusercontent.com/teamchong/vectorjson/HEAD/deps/zimdjson/README.md>
  - <https://registry.npmjs.org/vectorjson>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/teamchong/vectorjson`) · [data/wave13/enrich/raw/github_com_teamchong_vectorjson.json](../../../data/wave13/enrich/raw/github_com_teamchong_vectorjson.json) (enrichment confidence 0.8)

</details>
