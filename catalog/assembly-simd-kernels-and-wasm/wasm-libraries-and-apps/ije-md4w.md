# md4w

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig and C (md4c) compiled to WebAssembly, JavaScript API` · `MIT` · 🟡 stale

> md4c Markdown parser plus a Zig HTML writer compiled to WebAssembly; renders 2.7-11.6x faster than markdown-it in JavaScript runtimes.

| | |
|---|---|
| **Beats** | markdown-it (pure JavaScript); markdown-wasm (another WASM md4c wrapper) also in the benchmark |
| **Claimed result** | README: about 2.5x faster than markdown-it. Screenshot test/benchmark-screenshot.png: md4w 1.89 ms/iter (529.1 iter/s), markdown-wasm 2.16 ms/iter (462.0 iter/s), markdown-it 5.19 ms/iter (192.6 iter/s); 5.19/1.89 is 2.7x over markdown-it and 2.16/1.89 is 1.14x over markdown-wasm (derived from page data). |
| **Workload** | deno bench of test/benchmark.js: render Markdown to HTML, time per iteration, Apple M1, Deno 1.40.5. |
| **Metric** | throughput |
| **Hardware** | Apple M1 (aarch64-apple-darwin), Deno 1.40.5, from test/benchmark-screenshot.png |
| **Compiler and flags** | Zig 0.11.0 (README Development section, also at the screenshot commit a2ff722), build.zig optimize mode ReleaseFast for md4w-fast.wasm (loaded from the file system, which test/benchmark.js does) with md4c.c compiled with no extra C flags; ReleaseSmall for md4w-small.wasm; run with Deno 1.40.5 |
| **Adoption** | 155 stars |
| **Last commit** | 2025-05-28 |
| **Links** | [repository](https://github.com/ije/md4w) · [benchmark](https://github.com/ije/md4w) |

## Verdict

The author's deno bench (test/benchmark.js, Apple M1, Deno 1.40.5, Zig 0.11.0 ReleaseFast) rendered the CommonMark spec file in 1.89 ms/iter against 5.19 ms for markdown-it 14.0.0 (2.7x) and 2.16 ms for markdown-wasm (1.14x), with the wasm libraries fed a Uint8Array and markdown-it a decoded string and no output-equality check. Third-party runs with string input on both sides agree or show more: md4x's mitata bench (i7-10700K, Bun 1.4.2) 17.40 vs 72.68 us/iter (4.2x, derived from page data) and ox-content's CI (AMD EPYC, Node v26.8.1, median of 7) 2,361 vs 293 ops/s at 48.7 KB (8.1x) and 116 vs 10 ops/s at about 1 MB.

## Use it when

- Server, build-time or edge rendering of trusted Markdown (docs sites, static site generators, CMS previews) in Node.js, Deno or Bun when markdown-it plugins are not needed.
- Medium to large documents: third-party runs show the gap widening with size (ox-content CI: 8.1x over markdown-it at 48.7 KB, 11.6x at about 1 MB for parse plus render).
- Runtimes that cannot load native addons (Cloudflare Workers, browsers) where an N-API Markdown engine is not an option.
- HTTP handlers that want to stream HTML out in fixed-size chunks (mdToReadableHtml, 4 KB default buffer), as long as the whole Markdown input fits in memory.
- Pipelines that need a lightweight element tree (mdToJSON) rather than markdown-it's flat token list.

## Skip it when

- Untrusted input without a separate HTML sanitizer: raw HTML passes through under the default flags, link and image URLs are only percent-escaped (no javascript:/data: scheme filtering like markdown-it's validateLink), and the NO_HTML shorthand is broken (see gotchas).
- When you need CommonMark reference output or byte-stable HTML: the custom Zig renderer appends heading anchors, writes &lt;hr&gt;/&lt;br&gt;, leaves entities undecoded, and the ox-content conformance column scores md4w at 91.7% of CommonMark examples against 99.5% for md4x and 100% for markdown-it; md4w's own test only checks three substrings of the spec render.
- When you rely on markdown-it plugins, typographer, linkify options or custom link rendering (issue #16 asking for link-render customization is open).
- When raw speed on Node.js is the goal: the md4x benchmark has md4x's N-API build 2.36x faster than md4w and its wasm build 1.15x faster, and ox-content and satteri also beat md4w on HTML render there.
- Browser or CDN use expecting the benchmarked speed: from a CDN (and for workerd/unwasm since v0.2.6) init() loads the 28 KB md4w-small.wasm (ReleaseSmall), whose speed is not documented; the published numbers are for the 270 KB md4w-fast.wasm.

## How it is fast

Parsing is done by md4c, a single-pass SAX-style C parser that fires enter/leave block, enter/leave span and text callbacks without building an AST. md4w replaces md4c-html.c with its own HTML (and JSON) writer in Zig that appends into a buffer in wasm linear memory and flushes it to JavaScript in chunks through one imported function, so each call costs one copy in, one copy out and one TextDecoder pass. md4w-fast.wasm is built with Zig ReleaseFast for wasm32-freestanding with std.heap.wasm_allocator; markdown-it, by contrast, builds a token array with regex-driven rules and concatenates JavaScript strings.

## Compared with alternatives

Pick md4w over markdown-wasm (same md4c core, about 1.14x slower in md4w's bench) when you also want streaming HTML or a JSON tree; pick sparkdown instead when you need an mdast tree for the remark/unified ecosystem, and md4x (catalogued under md4c) when you want more speed and better conformance from the same parser lineage.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (npm package md4w ships prebuilt md4w-fast.wasm and md4w-small.wasm; md4c is vendored as a git submodule pinned at 481fbfb, March 2024) |
| **Minimum toolchain** | A JavaScript runtime with ES modules and WebAssembly whose i64 values map to BigInt (the glue decodes pointer/length pairs from BigInt); rebuilding needs Zig 0.11.0 (build.zig uses the 0.11 build API) |
| **Platforms** | wasm32: Node.js, Deno, Bun, browsers, Cloudflare Workers (workerd and unwasm entry points in package.json) |
| **Thread safety** | Not documented. One wasm instance per module realm with a module-level emit callback, so calls are not re-entrant (a code highlighter that itself calls mdToHtml would clobber the output sink); each Web Worker must call init() itself. |
| **Drop-in for the baseline** | no |

## Gotchas

- NO_HTML is defined wrongly in js/md4w.js as 0x00200 | 0x0040 (STRIKETHROUGH | NO_HTML_SPANS) instead of md4c's MD_FLAG_NOHTML = 0x0020 | 0x0040, so the README's parseFlags ["DEFAULT", "NO_HTML"] still passes raw HTML blocks (a line-start &lt;script&gt; or &lt;iframe&gt;) through verbatim; pass "NO_HTML_BLOCKS" and "NO_HTML_SPANS" explicitly and still sanitize output.
- parseFlags given as an array replaces the defaults unless it includes "DEFAULT", and unknown names are silently dropped: the README calls the task-list flag TASK_LISTS but the accepted key is TASKLISTS.
- Release-build edge cases in src/md4w.zig: invalid UTF-8 lead bytes in a heading (possible only with Uint8Array input; strings go through TextEncoder) hit an 'unreachable' in the slug code, which is undefined behaviour in ReleaseFast/ReleaseSmall; &lt;ol start&gt; is formatted into a 4-byte buffer, so list start numbers of 10000 or more hit 'catch unreachable' in bufPrintIntToSlice; render() returns a slice of the output buffer after its deferred free, which works only because Zig's WasmAllocator stores its free-list link at the end of the slot and the JS glue copies the bytes before the next allocation.
- Code-highlighter output is inserted without escaping, heading anchor ids are not de-duplicated (two identical headings share one id), and open issue #13 reports init() silently leaving the module unset when the wasm import matches neither expected shape, so the first render throws.

## Known shortcomings

- Raised C to A: Zig 0.11.0 named at screenshot commit a2ff722, build.zig ReleaseFast, Apple M1, Deno 1.40.5, public test/benchmark.js; but a one-file screenshot run with input-type asymmetry and only 1.14x over markdown-wasm. Stale.
- Library bug: js/md4w.js sets NO_HTML = 0x00200|0x0040 (STRIKETHROUGH|NO_HTML_SPANS) where md4c.h says 0x0020|0x0040, so the README usage ['DEFAULT','NO_HTML'] still passes raw HTML blocks through (XSS risk); no javascript: URL filtering. The renderer passes 91.7% of CommonMark examples (ox-content table); &lt;ol start&gt; goes through a 4-byte buffer so starts of 10000+ hit 'catch unreachable'; invalid UTF-8 in a heading hits unreachable (UB in release builds); the CDN default loads the small wasm build, which was never benchmarked. No harness flaw behind the numbers: third-party runs agree or exceed (md4x bench 17.40 vs 72.68 us, 4.2x; ox-content 8.1-11.6x).

## Caveats and trade-offs

Results are a terminal screenshot (no text table) from a single input file (test/commonmark-spec.md), single machine, one run, last updated 2024-02-21; vendored md4c was updated afterwards (2024-03-15) without a new run. The Zig version comes from the README's Development note rather than the run itself. The wasm libraries get the input as a Uint8Array while markdown-it gets a pre-decoded string (small advantage to the wasm side); markdown-it runs its default preset (html off, linkify off) while md4c runs its own default flags, so outputs are not checked for equality. markdown-wasm is measured through markdown-wasm-es@1.2.1, an ES-module repackaging published by md4w's author. Win over markdown-wasm (same md4c core) is only 1.14x. Author's own benchmark.

Two WASM binaries: a small one and md4w-fast.wasm that is faster but larger (270 KB gzipped); built with Zig; HTML-only renderer with parse flag options.

## Maintenance

Stale: last commit and v0.2.7 on npm are from 2025-05-28 (packaging only; vendored md4c unchanged since March 2024), MIT and small enough to use as-is for trusted Markdown, but the NO_HTML flag bug and open init issue #13 are unfixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: benchmark code is public (test/benchmark.js, deno bench, markdown-it@14.0.0 and markdown-wasm-es@1.2.1 pinned), the compiler is stated (README Development section names Zig 0.11.0, present at the screenshot commit a2ff722 of 2024-02-21), flags are in build.zig (ReleaseFast for md4w-fast.wasm, which index.js loads from the file system as the bench does; build.zig unchanged since that commit), and the screenshot names the CPU (Apple M1) and runtime (Deno 1.40.5).
- **Verifier notes:** Numbers match the screenshot exactly; upgraded to A because Zig 0.11.0, ReleaseFast (build.zig), Apple M1 and Deno 1.40.5 are all stated and the harness is public. Shortcomings: single-file screenshot run from Feb 2024, input-type asymmetry, no output-equality check, only 1.14x over markdown-wasm; stale (last commit 2025-05-28).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-05 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ije/md4w>
  - <https://github.com/ije/md4w/commits>
  - <https://github.com/ije/md4w/commits/main/test/benchmark-screenshot.png>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/README.md>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark-screenshot.png>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/build.zig>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/js/index.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/js/md4w.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/package.json>
  - <https://raw.githubusercontent.com/ije/md4w/a2ff722/README.md>
  - <https://raw.githubusercontent.com/ije/md4w/a2ff722/build.zig>
  - <https://raw.githubusercontent.com/ije/md4w/a2ff722/test/benchmark.js>
  - <https://registry.npmjs.org/markdown-wasm-es/1.2.1>
- **Sources the enricher read:**
  - <https://github.com/ije/md4w>
  - <https://github.com/ije/md4w/commits/main>
  - <https://github.com/ije/md4w/issues?q=is%3Aissue>
  - <https://github.com/ije/md4w/issues/13>
  - <https://github.com/ije/md4w/tree/main/vendor>
  - <https://github.com/ije/md4w/tree/main/test>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/README.md>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/test.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/build.zig>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/package.json>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/js/index.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/js/md4w.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/js/md4w.d.ts>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/src/md4w.zig>
  - <https://raw.githubusercontent.com/mity/md4c/481fbfbdf72daab2912380d62bb5f2187d438408/src/md4c.h>
  - <https://raw.githubusercontent.com/ziglang/zig/0.11.0/lib/std/heap/WasmAllocator.zig>
  - <https://registry.npmjs.org/md4w>
  - <https://github.com/unjs/md4x>
  - <https://raw.githubusercontent.com/unjs/md4x/HEAD/packages/md4x/bench/index.mjs>
  - <https://github.com/ubugeeei-prod/ox-content>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ije/md4w`) · [data/wave13/enrich/raw/github_com_ije_md4w.json](../../../data/wave13/enrich/raw/github_com_ije_md4w.json) (enrichment confidence 0.8)

</details>
