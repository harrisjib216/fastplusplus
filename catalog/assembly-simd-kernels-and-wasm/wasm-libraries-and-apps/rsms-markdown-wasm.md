# markdown-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (md4c) compiled to WebAssembly with a JavaScript API` · `MIT` · 🔴 abandoned

> md4c CommonMark parser and HTML renderer compiled to 31 kB-gzipped WebAssembly; about 2.3-2.4x markdown-it throughput.

| | |
|---|---|
| **Beats** | markdown-it ^10.0.0 (commonmark preset, IDNA link encoding disabled), marked ^0.7.0, commonmark.js ^0.29.2 and showdown ^1.9.1 (JavaScript) in Node.js 14.11 / V8 |
| **Claimed result** | Average ops/second from the README chart test/benchmark/results/avg-ops-per-sec.svg: markdown-wasm 195,065; markdown-it 84,774; marked 76,942; commonmark 66,185; showdown 8,502 (2.3x over markdown-it, derived from page data). Average throughput chart: 49 MB/s vs 17 MB/s for markdown-it (2.9x, derived from page data). A later third-party run in ije/md4w (Apple M1, Deno 1.40.5, commonmark-spec.md) shows markdown-wasm 2.16 ms/iter vs markdown-it 14.0.0 5.19 ms/iter (2.4x, derived from page data). |
| **Workload** | Parse and render to HTML a set of sample markdown files (benchmark suite adapted from commonmark.js bench), single thread, Node.js. |
| **Metric** | throughput |
| **Hardware** | 2.9 GHz MacBook, macOS 10.15, Node.js v14.11.0 (CPU model not given) |
| **Compiler and flags** | Measured build (charts last touched 2020-10-16, 'new benchmarks after upgrading md4c'): wasmc (emcc wrapper) at its 2020 version with release cflags only -DMD4C_USE_UTF8, optimisation level wasmc's default, emcc version unstated, Node 14.11; the wasmc ^2.2.1 in package.json dates from the 2021-07-01 upgrade and is not the measured build. |
| **Adoption** | 1.7k stars |
| **Last commit** | 2021-07-06 |
| **Links** | [repository](https://github.com/rsms/markdown-wasm) · [benchmark](https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/results/avg-ops-per-sec.svg) |

## Verdict

Author's own run, charts dated 2020-10-16, on a 2.9 GHz MacBook with macOS 10.15 and Node 14.11, markdown-wasm in bytes-in/bytes-out mode. Over the 27 commonmark.js bench samples it averaged 195,065 parse+render ops/s vs 84,774 for markdown-it 10 (commonmark preset, IDNA link encoding disabled), 76,942 for marked 0.7, 66,185 for commonmark.js 0.29 and 8,502 for showdown 1.9 (2.3x over markdown-it, derived from page data). Mean throughput was 49 vs 17 MB/s (graph.js divides by 1,024,000). The md4w repo's run (Apple M1, Deno 1.40.5, 200 KB commonmark-spec.md, string output, markdown-wasm-es 1.2.1, a repackaging of 1.2) shows 2.16 vs 5.19 ms/iter against markdown-it 14.0.0 (2.4x, derived from page data), so the direction holds without the bytes-mode advantage.

## Use it when

- Server-side or build-time rendering of trusted CommonMark/GFM-style Markdown to HTML in Node, where no markdown-it or marked plugins are needed and throughput matters (about 2.4x markdown-it 14 on the 200 KB CommonMark spec in md4w's run)
- High volumes of small documents (comments, chat messages, README snippets), especially if the HTML can stay as bytes (bytes: true) and go straight to a socket or file
- Browser bundles that want a small zero-dependency renderer (31 kB gzipped per the README)
- Simple custom code-block rendering through the synchronous onCodeBlock hook

## Skip it when

- You depend on markdown-it or marked plugins, custom renderer rules, or a token stream or AST: only HTML/XHTML output is offered
- Untrusted input without a separate sanitizer: raw HTML passes through unless ParseFlags.NO_HTML is set, and the URI filter only drops hrefs that start with 'javascript:' (case-insensitive)
- You need a maintained package: the last commit is 2021-07-06, md4c is pinned to an October 2020 commit plus patches, and 8 issues are open, including ESM loading failing in the browser (#26), Cloudflare Workers support (#25) and async onCodeBlock (#28). md4w covers these.
- Output must match the CommonMark reference renderer: every heading gets an injected &lt;a id=... class="anchor"&gt; slug link (issue #22 asks to disable it), and ParseFlags.DEFAULT turns on tables, strikethrough, task lists, permissive autolinks/ATX headers and whitespace collapsing (pass parseFlags: 0 for plain CommonMark)

## How it is fast

md4c is a single-pass, SAX-style C parser: it emits enter/leave/text callbacks straight into an HTML formatter that appends to one growable byte buffer reserved at 2x the input size. It never builds a JS object tree, so there is no per-node allocation or GC pressure. The JS boundary costs one copy of the input into the wasm heap, plus a TextDecoder pass on the output unless bytes: true is set, which is why the gap is widest on small inputs used in bytes mode.

## Compared with alternatives

md4w wraps the same md4c core with Zig glue, is maintained, supports streaming and JSON output and runs on Cloudflare Workers, and measured about 1.14x faster than markdown-wasm in its own Deno run, so prefer it for new code. Pick markdown-wasm only for its single-file Node build with embedded wasm, its stable 2021 API or onCodeBlock. sparkdown (pulldown-cmark in wasm) is the alternative if you want a Rust parser compared against remark.

## Integration

| | |
|---|---|
| **Form** | module (npm markdown-wasm 1.2.0: Node CommonJS file with embedded compressed wasm, UMD browser script with sidecar markdown.wasm, ES module with separate wasm) |
| **Dependencies** | none at runtime; building needs wasmc (an Emscripten emcc wrapper) |
| **Minimum toolchain** | Any JS runtime with WebAssembly and TextEncoder/TextDecoder (published numbers on Node 14.11; no engines field). Rebuilding needs wasmc ^2.2.1 and Emscripten (emcc version not documented); release cflags are only -DMD4C_USE_UTF8. |
| **Platforms** | Node and browsers via wasm. Known gaps: the ES build fetches 'markdown.wasm' relative to the page rather than the module (#26), Cloudflare Workers is unsupported (#25), and 'TypeError: Cannot set property exports of undefined' is reported (#18). |
| **Thread safety** | Single-threaded per instance: parse() reuses one static output buffer in wasm memory, so a bytes: true result is overwritten by the next parse() call (README says to slice() it); use one module instance per worker |
| **Drop-in for the baseline** | partial — parse(string) returns an HTML string like marked(str) or markdownit.render(str), but there are no plugins or renderer overrides, the extension set differs, and headings always gain anchor links, so the HTML is not byte-identical |

## Gotchas

- Benchmark harness flaws (test/benchmark/bench.js and graph.js). Only markdown-wasm gets bytes in and bytes out: parse(Buffer, {asMemoryView: true}) skips the TextEncoder on input and the TextDecoder on output, while the four JS libraries take and return strings. A commented-out 'markdown-wasm/string' row exists, and a 2020-10-16 commit titled 'benchmark: remove unused markdown-wasm/string' dropped it before the charts were published. The headline 'average ops/s' is an unweighted mean of per-file ops/s over 27 sample files, 24 of them 64-730 bytes, so it mostly measures per-call overhead, where skipping the string conversion helps most. Output is never compared across libraries.
- The README charts are stale: avg-ops-per-sec.svg was last touched on 2020-10-16 ('new benchmarks after upgrading md4c'), before the v1.1.0 release and before the 2021-07-01 commits that upgraded wasmc to 2.2.1, added the javascript: URI filter and added onCodeBlock. The record's compiler note (wasmc ^2.2.1) describes the current package.json, not the measured build. The baselines are markdown-it 10 and marked 0.7.
- Latent use-after-free in heading anchors (src/fmt_html.c, text_callback). slugptr is captured from r-&gt;outbuf-&gt;ptr before WBufAppendSlug, render_literal and WBufReserve run, and each of those can realloc the output buffer (WBufGrow). The slug is then memcpy'd from the possibly freed old buffer, so when growth moves the buffer, the href='#...' of a heading can receive stale heap bytes. That is wrong output and possibly fragments of earlier documents, not a sandbox escape. The bug does not affect the timing.
- bytes: true and the deprecated asMemoryView return a view that is only valid until the next parse(). onCodeBlock bridges JS and wasm for every code block, which the README says hurts performance, and its return value is inserted unescaped.

## Known shortcomings

- README SVG numbers match but bench.js gives markdown-wasm a Buffer in and asMemoryView out while the JS libraries get strings; no CPU model or emcc version; stale baselines (markdown-it 10, marked 0.7); md4w's third-party run backs about 2.4x. Abandoned since 2021-07-06.
- Harness biased toward markdown-wasm: only it runs bytes in and bytes out (asMemoryView), and the 2020-10-16 commit 'benchmark: remove unused markdown-wasm/string' dropped the like-for-like string row; the 'avg ops/s' is an unweighted mean over 27 files, 24 of them 64-730 bytes, so it is mostly per-call overhead. The SVG charts were last touched on 2020-10-16, before the v1.1.0 release and the 2021-07-01 wasmc 2.2.1 upgrade, so the record's wasmc ^2.2.1 flags do not describe the measured build. md4w's third-party string-output run still shows 2.4x, so the direction holds. Bug: use-after-free in src/fmt_html.c text_callback (slugptr captured before WBufAppendSlug, render_literal and WBufReserve, any of which can realloc the output buffer), so a heading href can receive stale heap bytes; wrong output only, timing unaffected.

## Caveats and trade-offs

Author's own 2020-era run (Node 14.11) on a '2.9 GHz MacBook' with no CPU model; emcc version and optimisation level not stated, hence tier C. The README values appear only in SVG charts; results/bench.csv is not committed (404). Harness asymmetry: bench.js feeds markdown-wasm a UTF-8 Buffer and calls parse(..., {asMemoryView:true}), so it skips string encoding of input and string decoding of output, while every JS library takes and returns JS strings; the README itself says the bytes/memory-view mode only helps when output is never converted to a string. The averaged ops/s is an unweighted mean across sample files, and the JS baselines are old versions (markdown-it 10, marked 0.7). A later third-party run (ije/md4w test/benchmark.js, string output, markdown-it 14.0.0) still shows about 2.4x, so the direction holds. md4w reports itself about 1.14x faster than markdown-wasm. Repository unmaintained since July 2021. [retier] Author's own 2020-era run (Node 14.11) on a '2.9 GHz MacBook' with no CPU model; emcc/wasmc version and optimisation level not stated; values exist only in SVG charts (results/bench.csv not committed) that predate the v1.1.0 release and the 2021-07-01 wasmc 2.2.1 upgrade, javascript: URI filter and onCodeBlock. Harness bias: bench.js feeds markdown-wasm a UTF-8 Buffer and calls parse(..., {asMemoryView: true}), skipping string encoding of input and decoding of output, while the four JS libraries take and return strings; a 'markdown-wasm/string' row existed and was removed by the 2020-10-16 commit 'benchmark: remove unused markdown-wasm/string' before the charts were published. The 'average ops/s' is an unweighted mean over 27 files, 24 of them 64-730 bytes, so it mostly measures per-call overhead; the baselines are markdown-it 10 and marked 0.7. A third-party run in ije/md4w (Apple M1, Deno 1.40.5, commonmark-spec.md, string output) still shows markdown-wasm 2.16 ms/iter vs markdown-it 14.0.0 5.19 ms/iter (2.4x, derived from page data), so the direction holds. Latent use-after-free in heading anchors (src/fmt_html.c text_callback captures slugptr before calls that can realloc the output buffer), giving stale heap bytes in an href; wrong output only. bytes: true views are valid only until the next parse(); onCodeBlock's return value is inserted unescaped.

31 kB gzipped, CommonMark via md4c; no plugin ecosystem comparable to markdown-it; output follows md4c, not identical to the JS parsers.

## Maintenance

Abandoned since 2021-07-06 (npm 1.2.0 published 2021-07-01; 1.7k stars, 69 forks, 2 open PRs, 8 open issues). MIT and small, so it is usable as a frozen dependency for trusted input. md4w is the maintained successor on the same md4c core. Reading the code turned up a heading-anchor use-after-free, and the benchmark harness favours markdown-wasm (bytes-only mode, string row removed, mean dominated by sub-KB files).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks section embeds test/benchmark/results/avg-ops-per-sec.svg whose text carries exactly markdown-wasm 195,065, markdown-it 84,774, marked 76,942, commonmark 66,185, showdown 8,502 ops/s (and avg-throughput.svg 49 vs 17 MB/s); the harness test/benchmark/bench.js is public, but the machine is only a '2.9 GHz MacBook' (no CPU model) and the emcc version and optimisation level are not stated, so first-party tier C.
- **Verifier notes:** Numbers verified in the SVG chart text; tier stays C (no CPU model, no emcc version). Shortcomings: benchmark gives markdown-wasm a bytes-in/memory-view-out fast path the JS baselines do not get, stale baseline versions, abandoned since 2021-07-06; md4w's independent Deno run corroborates about 2.4x over markdown-it 14.0.0.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-05 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/rsms/markdown-wasm>
  - <https://github.com/rsms/markdown-wasm/commits>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/results/avg-ops-per-sec.svg>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/results/avg-throughput.svg>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/README.md>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/package.json>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/bench.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/wasmc.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark-screenshot.png>
- **Sources the enricher read:**
  - <https://github.com/rsms/markdown-wasm>
  - <https://github.com/rsms/markdown-wasm/commits>
  - <https://github.com/rsms/markdown-wasm/commits/master/test/benchmark/results/avg-ops-per-sec.svg>
  - <https://github.com/rsms/markdown-wasm/issues>
  - <https://github.com/rsms/markdown-wasm/issues/21>
  - <https://github.com/rsms/markdown-wasm/issues/26>
  - <https://github.com/rsms/markdown-wasm/tree/master/test/benchmark/samples>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/markdown.d.ts>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/wasmc.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/md.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/md.c>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/wlib.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/wlib.c>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/wbuf.c>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/fmt_html.c>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/src/md4c.h>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/README.md>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/package.json>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/bench.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/graph.js>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/results/avg-ops-per-sec.svg>
  - <https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/results/avg-throughput.svg>
  - https://raw.githubusercontent.com/rsms/markdown-wasm/HEAD/test/benchmark/samples/ (all 27 sample files)
  - <https://registry.npmjs.org/markdown-wasm>
  - <https://registry.npmjs.org/markdown-wasm-es>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/README.md>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark.js>
  - <https://raw.githubusercontent.com/ije/md4w/HEAD/test/benchmark-screenshot.png>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rsms/markdown-wasm`) · [data/wave13/enrich/raw/github_com_rsms_markdown_wasm.json](../../../data/wave13/enrich/raw/github_com_rsms_markdown_wasm.json) (enrichment confidence 0.8)

</details>
