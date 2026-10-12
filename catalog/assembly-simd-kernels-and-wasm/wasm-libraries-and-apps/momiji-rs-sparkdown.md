# sparkdown (@momiji-rs/sparkdown, WebAssembly build)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (wasm32 with simd128 and bulk-memory) with JavaScript wrapper` · `MIT` · 🟢 active

> Zero-dependency Rust CommonMark parser shipped as SIMD WebAssembly; replaces remark-parse and beats JS markdown renderers in Node.

| | |
|---|---|
| **Beats** | remark-parse (mdast-util-from-markdown, JavaScript) and the native pulldown-cmark crate |
| **Claimed result** | README mdast table (CommonMark spec, 198 KB, Node, Apple Mac Studio): like-for-like with positions kept, sparkdown toMdast() \~1.9 ms vs remark (mdast-util-from-markdown) \~73 ms, about 38x (derived from page data); the printed \~80x pairs sparkdown's no-position tree (\~0.9 ms, timed through a reader written in the harness rather than the shipped toMdast entry point) against remark, which always emits positions. Native table: sparkdown wasm 0.93 ms vs native pulldown-cmark 0.68 ms (wasm 1.37x slower than native) and cmark \~1.9 ms (CLI-to-CLI on a 16 MB document). The README's HTML rows (sparkdown wasm 0.90 ms vs markdown-it 4.52 ms and marked 5.20 ms) have no benchmark in the repo and are not reproducible. |
| **Workload** | Parsing the 200 KB CommonMark spec document to an mdast tree (fully materialised plain objects) and rendering it to HTML, measured in Node on one machine. |
| **Metric** | latency |
| **Hardware** | Apple Mac Studio (chip not stated), Node |
| **Compiler and flags** | RUSTFLAGS='-C target-feature=+simd128,+bulk-memory' cargo build --release --target wasm32-unknown-unknown (features wasm, or ast,wasm for the mdast benchmarks), then wasm-opt -O4 --enable-simd --enable-bulk-memory into harness/sparkdown.wasm (harness/README.md); Rust stable via rustup, version not stated (MSRV 1.95); Node version not stated |
| **Adoption** | 3 stars; about 46k npm downloads per month |
| **Last commit** | 2026-06-27 |
| **Links** | [repository](https://github.com/momiji-rs/sparkdown) · [benchmark](https://github.com/momiji-rs/sparkdown) |

## Verdict

First-party, one Apple Mac Studio (chip not stated), 198 KB CommonMark spec: native sparkdown renders HTML in 0.59 ms against pulldown-cmark's 0.68 ms (criterion, in-repo), the wasm build in 0.90-0.93 ms in Node against markdown-it 4.52 ms and marked 5.20 ms (no in-repo harness), and the wasm mdast path builds a fully materialised tree in \~1.9 ms with positions against \~73 ms for mdast-util-from-markdown (\~38x; \~0.9 ms without positions).

## Use it when

- unified/remark/rehype pipelines in Node, Bun, Deno or edge runtimes where remark-parse dominates build time and plugins only walk the tree
- Rendering CommonMark or GFM to HTML in JavaScript hosts that would otherwise use markdown-it or marked, with cmark-identical output
- Non-JS hosts (wasmtime, wazero, Workers) that want a self-contained, WASI-free markdown .wasm module with a raw C-ABI
- Native Rust code that wants a dependency-free CommonMark renderer about as fast as pulldown-cmark (0.59 vs 0.68 ms on the 198 KB spec, first-party)

## Skip it when

- Native Rust users already on pulldown-cmark who need its event/iterator API or ecosystem: sparkdown's lead there is about 1.15x and its wasm build is slower than native pulldown-cmark
- remark pipelines that rely on syntax-extension plugins hooking micromark (math, MDX and similar): parsing happens in wasm, so only the extensions compiled into sparkdown (GFM, footnotes, frontmatter, directives, definition lists, emoji) are available
- Hosts without WebAssembly SIMD support: the documented wasm build enables +simd128 and +bulk-memory
- Synchronous use on the browser main thread: initSync throws there because synchronous wasm compilation is capped at about 4 KB; use the async init
- Teams that need a maintained, widely reviewed parser: v0.1.0, 3 stars, 145 crates.io downloads (npm about 46k per month per the verifier's registry search), no commits since 2026-06-27

## How it is fast

A port of cmark's incremental block algorithm over zero-copy borrowed slices, SIMD byte-set matchers (simdjson-style nibble lookup on NEON/SSE, wasm v128 kernels) that skip plain text to the next significant byte, a fused SIMD HTML escaper, an intrusive first-child/next-sibling node tree and a bump arena. For mdast it builds the tree in wasm and ships it to JS as a compact binary wire format (string-pooled when positions are off) that is read into plain objects without JSON.parse.

## Compared with alternatives

Against markdown-wasm and md4w (md4c compiled to wasm, also beating markdown-it), pick sparkdown when you need an mdast tree for the unified/remark ecosystem or GFM/extension bundles behind one API; for plain HTML rendering the three have not been measured on the same run, so md4c-based packages remain the more established choice.

## Integration

| | |
|---|---|
| **Form** | crate (rlib + cdylib) + npm module (ESM, wasm base64-inlined, four subpath bundles) + raw .wasm with a C-ABI |
| **Dependencies** | none |
| **Minimum toolchain** | Rust 1.95, edition 2024; npm package declares Node &gt;=18 |
| **Platforms** | any Rust target (SIMD paths on NEON/SSE, SWAR fallback); wasm32-unknown-unknown with simd128 + bulk-memory for Node, browsers, Deno, Bun and edge runtimes |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — /mdast is a drop-in unified parser plugin for remark-parse (deep-equal on the 652 CommonMark examples including position, per README) but not for micromark syntax extensions; the HTML API is not API-compatible with markdown-it or marked |

## Gotchas

- Harness flaw: the README's JS table (sparkdown wasm 0.90 ms vs markdown-it 4.52 ms and marked 5.20 ms) has no benchmark in the repo; harness/package.json depends on neither markdown-it nor marked, and their versions and options (markdown-it preset, html flag) are not stated, so the 5.0x/5.7x rows cannot be reproduced.
- Harness flaw: harness/nopos_bench.mjs times sparkdown_to_mdast_wire_nopos_opts through an inline-string reader written in the harness (best of 20 batches of 25), while the published npm toMdast({position:false}) calls sparkdown_to_mdast_wire_fast_opts with a string-pooled reader, and the harness wasm is built with ast,wasm while the npm /mdast bundle is ast,full; the README's \~0.9 ms 'best-of-15' row therefore does not come from a script that runs the shipped entry point. The \~80x headline also pairs the no-position tree with remark, which always builds positions; like-for-like it is \~1.9 vs \~73 ms (\~38x, derived from page data).
- Only sparkdown vs pulldown-cmark is benchmarked in-repo (benches/vs_pulldown.rs, criterion); the rushdown, comrak, markdown-rs and cmark rows have no harness, cmark was compared CLI-to-CLI on a 16 MB document, and the wasm rows (measured in Node) sit in the same table as native in-process times.
- Output is not cmark-identical in every case: the README lists fuzz-found differences (native to_html keeps a trailing tab at the end of a block where cmark strips it; mdast value of indented code with trailing blank lines keeps one fewer newline than remark; a nested blockquote closed by '&gt;\t' over-extends by a line).

## Known shortcomings

- The 80x pairs remark with positions against sparkdown without (like-for-like about 38x, derived); the wasm HTML path is slower than native pulldown-cmark (0.93 vs 0.68 ms) and beats only markdown-it (4.52 ms) and marked (5.20 ms); the harness README is stale (13-23x, 537/652); chip unstated.
- Harness flaw 1: the markdown-it 4.52 ms and marked 5.20 ms rows have no harness in the repo (neither is a harness dependency; versions and options unstated). Harness flaw 2: harness/nopos_bench.mjs times sparkdown_to_mdast_wire_nopos_opts through a reader written in the harness, while the shipped toMdast uses _fast_opts (pooled strings) and the harness wasm build differs (ast,wasm vs ast,full); like-for-like with positions kept the gap is about 38x, not 80x. No commits since 2026-06-27.

## Caveats and trade-offs

First-party, one machine (Apple Mac Studio, chip not stated), absolute times machine-specific. The \~80x headline pairs sparkdown's no-position tree against remark, which always emits positions; the like-for-like position-on comparison is \~38x (derived from page data). harness/nopos_bench.mjs times a hand-written wire reader inside the harness (best of 20 batches of 25) rather than the published npm toMdast entry point, and the README table says best-of-15. The harness README is a stale SPIKE document that still reports the wasm mdast path as \~13-23x faster than JS parsing and 537/652 shape matches, while the top README claims deep equality on all 652 examples. The wasm HTML path (0.93 ms) is slower than native pulldown-cmark (0.68 ms); its win is only over JS libraries (markdown-it, marked). The in-repo cargo bench covers only sparkdown vs pulldown-cmark. Very young project (v0.1.0, 27 June 2026, 3 stars, about 46k npm downloads per month per the npm registry search API). [retier] First-party, one machine (Apple Mac Studio, chip not stated). Harness flaw 1: the markdown-it and marked rows have no harness in the repo (harness/package.json depends on neither; versions and options unstated). Harness flaw 2: harness/nopos_bench.mjs times sparkdown_to_mdast_wire_nopos_opts through an inline-string reader written in the harness (best of 20 batches of 25) while the shipped toMdast({position:false}) calls sparkdown_to_mdast_wire_fast_opts with a string-pooled reader, and the harness wasm is built with ast,wasm while the npm bundle is ast,full; the \~80x headline also pairs a no-position tree against remark's positioned tree (like-for-like about 38x). Only sparkdown vs pulldown-cmark is benchmarked in-repo (benches/vs_pulldown.rs); the rushdown, comrak, markdown-rs and cmark rows have no harness and the wasm rows (Node) sit in the same table as native in-process times. The harness README is a stale SPIKE document. Output is not cmark-identical in every case (fuzz-found trailing-tab, indented-code newline and nested-blockquote differences). No commits since 2026-06-27.

Wasm build is about 1.4x slower than sparkdown's own native build (0.93 vs 0.59 ms) and slower than native pulldown-cmark on HTML rendering; the mdast path crosses the wasm boundary as a binary wire format.

## Maintenance

MIT, zero dependencies and small, but a two-week burst of work (0.0.1 to 0.1.0 between 2026-06-24 and 2026-06-27) with no commits since and no open issues; treat it as an unproven young release rather than an actively maintained project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers in the README (mdast table: toMdast({position:false}) \~0.9 ms, toMdast() with position \~1.9 ms, remark mdast-util-from-markdown \~73 ms; wasm HTML 0.90 ms vs markdown-it 4.52 ms and marked 5.20 ms) with public bench code (harness/nopos_bench.mjs, harness/via_mdast_bench.mjs, harness/e2e_bench.mjs) and published wasm build flags, but the CPU is only 'Apple Mac Studio' (chip not stated) and the rustc and Node versions are not stated, so not A.
- **Verifier notes:** Numbers match the README; the comparison against remark is real and backed by public harness code, but the 80x headline is position-off vs position-on (like-for-like \~38x). Last commit 2026-06-27 confirmed (release 0.1.0), MIT confirmed, npm monthly downloads 46,331 confirmed via registry.npmjs.org search.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/momiji-rs/sparkdown>
  - <https://github.com/momiji-rs/sparkdown/commits>
  - <https://github.com/momiji-rs/sparkdown/tree/main/harness>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/nopos_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/via_mdast_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/e2e_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/package.json>
  - <https://registry.npmjs.org/-/v1/search?text=@momiji-rs/sparkdown&size=3>
- **Sources the enricher read:**
  - <https://github.com/momiji-rs/sparkdown>
  - <https://github.com/momiji-rs/sparkdown/commits/main>
  - <https://github.com/momiji-rs/sparkdown/issues>
  - <https://github.com/momiji-rs/sparkdown/tree/main/harness>
  - <https://github.com/momiji-rs/sparkdown/tree/main/npm>
  - <https://github.com/momiji-rs/sparkdown/tree/main/benches>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/benches/vs_pulldown.rs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/package.json>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/nopos_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/via_mdast_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/e2e_bench.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/harness/wasm_boundary.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/npm/package.json>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/npm/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/npm/sparkdown.mjs>
  - <https://raw.githubusercontent.com/momiji-rs/sparkdown/HEAD/npm/mdast.mjs>
  - <https://crates.io/api/v1/crates/sparkdown>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/momiji-rs/sparkdown`) · [data/wave13/enrich/raw/github_com_momiji_rs_sparkdown.json](../../../data/wave13/enrich/raw/github_com_momiji_rs_sparkdown.json) (enrichment confidence 0.6)

</details>
