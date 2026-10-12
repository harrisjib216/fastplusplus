# dhi (Zig SIMD WASM Zod 4 replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig (compiled to SIMD WebAssembly, plus an N-API addon and a Python C extension)` · `MIT` · 🟢 active

> Zod 4 API clone in plain TypeScript with code-generated validators; 1.6-7.8x faster than Zod 4 on reused schemas.

| | |
|---|---|
| **Beats** | Zod 4 (TypeScript/JavaScript schema validation) |
| **Claimed result** | README (release 1.3.1, bun run benchmarks/benchmark-vs-all.ts): 13.8x faster than Zod 4 on the full suite (arithmetic mean of per-row ratios); docs/benchmarks/benchmark-results.json (2026-03-18, Bun, 25 rows, arithmetic mean 27.3x, geometric mean 16.4x derived from page data): z.email() 15.9x, z.url() 13.8x, z.ipv4() 12.2x, z.int() 54.3x, z.float64() 61.8x, z.coerce.boolean() 74.5x, Object (valid) 4.4x, Nested Object 3.7x, Array&lt;number&gt; 7.8x, Union 1.6x, DiscriminatedUnion 2.1x, Optional 2.2x, Nullable 2.0x. The 12-75x rows construct a new Zod schema on every iteration; the 7 rows with schemas built once (objects, arrays, unions, modifiers) give about 2.9x (1.6-7.8x, derived from page data). The README's own 1.3.1 table has IPv4 at 1.1x. |
| **Workload** | Single-value safeParse micro-benchmarks in Bun, 1,000,000 iterations after a 10,000-iteration warm-up, dhi z.\* API vs Zod 4: string formats (email, uuid, url, ipv4, jwt, ulid, nanoid, base64), number formats, ISO date/time, coercion, stringbool, a 3-field object, a nested object, Array&lt;number&gt; of 10, unions and optional/nullable. In benchmark-zod4-features.ts the format, number and coercion rows build the schema inside the timed closure (e.g. zod.email().safeParse(...)), so they time schema construction plus one parse. |
| **Metric** | throughput |
| **Compiler and flags** | TypeScript benchmarks run with Bun (bun run benchmarks/benchmark-vs-all.ts or benchmark-vs-zod.ts; version not stated); Zod ^4.3.6 per js-bindings/package.json devDependencies (benchmark-vs-zod.ts header says Zod 4.3.6); the README's zig build bench -Doptimize=ReleaseFast is the Zig-only benchmark and is not part of the Zod comparison |
| **Adoption** | 387 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/justrach/dhi) · [benchmark](https://raw.githubusercontent.com/justrach/dhi/HEAD/docs/benchmarks/benchmark-results.json) |

## Verdict

First-party Bun micro-benchmarks (CPU and Bun version unstated) against Zod 4.3.6, 1,000,000 safeParse calls per row after a 10,000-call warm-up: with schemas built once, dhi is 1.6x (3-way union) to 7.8x (Array&lt;number&gt; of 10) faster and 3.7-4.4x on objects; the 12-75x rows time schema construction plus one parse per iteration. The published JSON is from 2026-03-18, before the v1.6.0 rewrite of the TypeScript core.

## Use it when

- Request-body or tool-input validation of small objects and short arrays with schemas built once at module load, where Zod parsing shows up in profiles: the hoisted-schema rows are 3.7-4.4x on objects and 7.8x on Array&lt;number&gt; of 10.
- Code that builds schemas inline per call (for example `z.email().safeParse(x)` inside a handler): Zod 4's construction cost dominates there and dhi's cheap constructors give the 12-75x rows.
- Existing Zod 4 codebases that can run their own test suite against a one-line import swap; dhi carries `_zod` internals and `~standard`, and ships compatibility tests for the MCP SDK and Vercel AI SDK.
- Node 18+, Bun or Deno servers where `new Function` is permitted, so the compiled fast path is actually taken.

## Skip it when

- Runtimes or pages that forbid eval (strict CSP): the `new Function` compile is wrapped in try/catch and silently falls back to the interpreted path, which no published benchmark measures.
- When exact Zod accept/reject parity matters (security filters, shared client/server rules): the format scanners re-implement Zod's regexes by hand and at least the email scanner diverges (see gotchas).
- Union-, optional- and nullable-heavy schemas: the published gain there is only 1.6-2.2x, small next to the risk of swapping a core dependency.
- Teams that need a stable, widely used dependency: single-maintainer project (387 stars, 7 forks) whose entry-point architecture changed within months (WASM default, then N-API, then pure TypeScript in v1.6.0).
- Python users relying on the pure-Python fallback: issue #56 reported it validates differently from the native extension (closed after 3.14 wheels shipped), and #57 reported int fields silently truncating 1.5 to 1 (fixed).

## How it is fast

Object, array and union schemas are compiled on first parse into a straight-line validator with `new Function` (runtime code generation, the same idea as Zod 4's eval-based fast path) that returns the output object or a null failure sentinel; error objects are only built by falling back to the interpreted path. String formats (email, UUID, IPv4, base64, ISO date) are hand-written `charCodeAt` scanners over `Uint8Array` lookup tables instead of regexes; URL goes through the WHATWG `URL` constructor. Schema construction is cheap plain-class instantiation, which is where most of the 12-75x rows come from, since Zod 4's format constructors are expensive. The Zig SIMD code is not on the TypeScript `z` path.

## Compared with alternatives

No schema validator is catalogued among the wasm-libraries-and-apps siblings; like fast-es-module-lexer (a pure-JS rewrite that beats a WASM library), dhi's measured win comes from JavaScript, not WASM, so pick it on Zod-compatibility grounds rather than over a WASM sibling. Against Zod itself, pick it when profiles show schema parsing or inline schema construction as a hotspot and your tests confirm parity.

## Integration

| | |
|---|---|
| **Form** | module (npm package `dhi`, ESM; also a PyPI wheel and Zig source) |
| **Dependencies** | none at runtime on npm or PyPI; Zod ^4.3.6 and Arktype are dev dependencies for benchmarks and parity tests |
| **Minimum toolchain** | Node.js 18+ (package engines), Bun or Deno; TypeScript 5 optional peer; Zig 0.17-dev to build the native and WASM parts; Python 3.9-3.14 wheels |
| **Platforms** | any JavaScript runtime for the `z` API (pure TypeScript); Python wheels for macOS arm64, Linux x86_64/aarch64 and, since v1.6.0, Windows |
| **Thread safety** | not documented (compiled validators are cached lazily on the schema object in `_jit`/`_jitTop`) |
| **Drop-in for the baseline** | partial — same `z` API and Zod 4 internals, and the README claims 100% parity, but format scanners are hand-written re-implementations (email diverges) and the README's `dhi/napi` backend is not exported by package.json |

## Gotchas

- Benchmark harness flaw: the 12-75x rows build the schema inside the timed closure (`zod.email().safeParse(...)`, `zod.int()`, `zod.coerce.boolean()`), so they mostly time Zod 4's schema construction: Zod does 0.42M ops/s on that z.email() row but 1.9M ops/s on a hoisted 3-field object that includes an email check. benchmark-vs-all.ts (source of the README's 13.8x) does the same for its 'Number type check' and coercion rows. The 13.8x and 27.3x headlines are arithmetic means of per-row ratios; the 25 rows of benchmark-results.json have a geometric mean of 16.4x and the 7 hoisted-schema rows about 2.9x (derived from page data). Each row runs dhi then Zod once, in one process, with results discarded; no script in the repo writes benchmark-results.json, and its 2026-03-18 timestamp predates the v1.6.0 core rewrite.
- Parity bug in the email fast path: `fastValidateEmail` accepts a local part ending in an apostrophe ("o'@example.com", "'@example.com"), which Zod 4's email regex rejects because the last local character must be [A-Za-z0-9_+-]. Reproduced this session by running the function from schema-core.ts against Zod's regex in Node 22; tests/test-zod-parity.ts only covers "o'neil@example.com".
- The README is partly stale: it still advertises a default '28KB SIMD WASM module' and an N-API backend via `import { z } from 'dhi/napi'` (1.7-2x faster), but package.json exports has no `./napi` entry, commit #73 publishes npm without the N-API build, and since v1.6.0 the `z` API has no WASM. The measured gain is a faster JavaScript implementation, not Zig or WASM.
- The js-bindings README's benchmark instructions point at `justrach/dhi-zig` and `bun run benchmark-vs-zod.ts` from the package root, while the scripts live in js-bindings/benchmarks/; the Arktype 2.1 rows that benchmark-vs-all.ts also times are never published.

## Known shortcomings

- The 12-75x rows build a new schema inside the timed loop (mostly Zod 4 construction cost), hoisted-schema rows are only 1.6-7.8x; the script that wrote benchmark-results.json is not in the repo; the TypeScript path is mostly plain JavaScript (WASM only for url/ipv4/datetime in v1.1.20 and none in the default entry since v1.6.0); benchmarked on Bun. Filed under wasm-libraries-and-apps.
- Harness flaw: the 12-75x rows build the schema inside the timed closure (zod.email().safeParse(...), zod.int(), zod.coerce.boolean()), so they mostly time Zod 4's schema construction; the 13.8x and 27.3x headlines are arithmetic means of per-row ratios, the geometric mean of the 25 benchmark-results.json rows is 16.4x and the 7 rows with hoisted schemas about 2.9x (1.6-7.8x). benchmark-results.json (2026-03-18) predates the v1.6.0 rewrite and no repo script writes it. Correctness bug: fastValidateEmail accepts a local part ending in an apostrophe (o'@example.com), which Zod's regex rejects (reproduced in Node 22; the parity corpus misses it). README stale: package.json does not export dhi/napi and the z API has had no WASM since v1.6.0, so the speedup comes from plain JavaScript.

## Caveats and trade-offs

First-party; CPU, Bun version and the script that produced benchmark-results.json are not published (none of the four js-bindings benchmark scripts writes that file). The 12-75x rows build a fresh schema per iteration in the timed loop, which mostly measures Zod 4's expensive schema construction (Zod runs about 0.3-0.5M ops/s on those rows but 1.9M ops/s on a hoisted 3-field object that includes an email check); rows with hoisted schemas show 1.6-7.8x, and the README's own 1.3.1 table has IPv4 at only 1.1x. Despite the 'SIMD WASM' description, the TypeScript path is mostly plain JavaScript: v1.1.20 called WASM only for url, ipv4 and ISO datetime, v1.5.2 only for ISO datetime, and since v1.6.0 (2026-08-30) the default entry is a single runtime-agnostic TypeScript core with no WASM dependency, so the measured gain is a faster JS reimplementation (JIT-compiled validators), not Zig/WASM. Runs on Bun (JavaScriptCore), not V8. Three different summary figures (13.8x README, 27.3x JSON, 29.7x chart) come from different runs. [retier] First-party; CPU, Bun version and the script that produced benchmark-results.json are not published (no repo script writes it, and its 2026-03-18 timestamp predates the v1.6.0 core rewrite). Harness flaw: the 12-75x rows build the schema inside the timed closure (zod.email().safeParse(...), zod.int(), zod.coerce.boolean()), so they mostly time Zod 4's schema construction (Zod does 0.42M ops/s on that z.email() row but 1.9M ops/s on a hoisted 3-field object with an email check); benchmark-vs-all.ts does the same for its number and coercion rows; each row runs dhi then Zod once in one process with results discarded; three summary figures (13.8x README, 27.3x JSON, 29.7x chart) come from different runs. Parity bug: fastValidateEmail accepts a local part ending in an apostrophe (o'@example.com), which Zod 4's email regex rejects (reproduced in Node 22; tests/test-zod-parity.ts only covers o'neil@example.com). Despite the 'SIMD WASM' description the TypeScript path is mostly plain JavaScript: v1.1.20 called WASM only for url, ipv4 and ISO datetime, v1.5.2 only for ISO datetime, and since v1.6.0 (2026-08-30) the default entry is a runtime-agnostic TypeScript core with no WASM; package.json exports no dhi/napi entry although the README advertises it. Runs on Bun (JavaScriptCore), not V8.

Browser and edge runtimes load a 28 KB SIMD WASM module; Node uses an N-API native addon (platform binaries); Zod 4 API parity is claimed but not complete for every refinement; Python side is a separate Pydantic replacement.

## Maintenance

Actively maintained by one author (v1.7.0 on 2026-08-30, last commit 2026-08-31, 1 open issue), MIT with zero runtime dependencies, so it is easy to trial as a Zod swap behind your own tests, but its speed figures are first-party, stale and inflated by the harness, and the 'Zig + SIMD WASM' framing does not describe the npm `z` path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Bun runs with public benchmark scripts (js-bindings/benchmarks/benchmark-vs-zod.ts, benchmark-vs-all.ts, benchmark-zod4-features.ts) but no CPU model, no Bun version, and the script that wrote docs/benchmarks/benchmark-results.json is not in the repo. The large format/number/coercion ratios are inflated by building the schema inside the timed loop, so the headline claim is overstated; tier stays C.
- **Verifier notes:** Numbers in the record match benchmark-results.json and the README, but the big ratios come from per-iteration schema construction in the timed loop; hoisted-schema rows are 1.6-7.8x. The TypeScript speedup is from a pure-JS core (WASM was used only for url/ipv4/datetime early on and not at all since v1.6.0), so the assemblyscript-and-wasm-langs category is a weak fit; consider a category override to a JS/TS validation category or keep with that shortcoming. Metadata confirmed: MIT, 387 stars, 6 forks, not a fork, last commit 2026-08-31 (v1.7.0).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/docs/benchmarks/benchmark-results.json>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/README.md>
  - <https://github.com/justrach/dhi>
  - <https://github.com/justrach/dhi/tree/main/js-bindings>
  - <https://github.com/justrach/dhi/tree/main/js-bindings/benchmarks>
  - <https://github.com/justrach/dhi/tree/main/docs/benchmarks>
  - <https://github.com/justrach/dhi/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-vs-all.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-vs-zod.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-zod4-features.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-results.json>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/generate-charts.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/package.json>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/schema.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/schema-core.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/v1.5.2/js-bindings/schema.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/v1.1.20/js-bindings/schema.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/docs/benchmarks/speedup-all.svg>
  - <https://github.com/justrach/dhi/commits/main/js-bindings/schema.ts>
  - <https://github.com/justrach/dhi/commits/main>
  - <https://github.com/justrach/dhi/tags>
- **Sources the enricher read:**
  - <https://github.com/justrach/dhi>
  - <https://github.com/justrach/dhi/issues?q=is%3Aissue>
  - <https://github.com/justrach/dhi/commits/main>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/README.md>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/docs/benchmarks/benchmark-results.json>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/package.json>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/README.md>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-vs-all.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-vs-zod.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/benchmarks/benchmark-zod4-features.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/schema.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/schema-core.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/js-bindings/tests/test-zod-parity.ts>
  - <https://raw.githubusercontent.com/justrach/dhi/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/colinhacks/zod/main/packages/zod/src/v4/core/regexes.ts>
  - <https://raw.githubusercontent.com/colinhacks/zod/main/packages/zod/src/v4/core/schemas.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/justrach/dhi`) · [data/wave13/enrich/raw/github_com_justrach_dhi.json](../../../data/wave13/enrich/raw/github_com_justrach_dhi.json) (enrichment confidence 0.75)

</details>
