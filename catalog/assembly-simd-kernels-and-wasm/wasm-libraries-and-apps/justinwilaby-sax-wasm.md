# sax-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Rust` · `MIT` · 🟢 active

> Rust/WebAssembly streaming SAX parser for XML, HTML, JSX and Angular templates with positions; claims to beat saxes and sax-js, but only measured with no events subscribed.

| | |
|---|---|
| **Beats** | sax-js and saxes (JavaScript streaming XML parsers) |
| **Claimed result** | README table (benchmarks last updated 2026-02-12, v3.1.4, Node v25.6.1, macOS arm64): sax-wasm 6.80 ms vs saxes 11.00 ms (\~1.6x), ltx 11.56 ms, sax-js 26.99 ms (\~4.0x), node-xml 31.73 ms, node-expat 41.51 ms (ratios derived from page data). sax-wasm ran with no events subscribed, so its figure times tokenization only, with no event objects built or delivered. |
| **Workload** | src/js/__test__/benchmark.mjs: one full parse of the bundled src/js/__test__/xml.xml (about 3 MB) written from memory in 64 KiB chunks, repeated 10 times per parser with no warm-up, mean reported. sax-wasm is constructed with new SAXParser() (events = 0, nothing subscribed); no parser has handlers attached. |
| **Metric** | latency |
| **Hardware** | macOS Apple Silicon (arm64), Node v25.6.1; exact chip not stated |
| **Compiler and flags** | Rust stable (version not pinned); cargo build --target wasm32-unknown-unknown --release with [profile.release] opt-level = 3, lto = "fat", codegen-units = 1, panic = "abort"; then wasm-opt -O4 --enable-bulk-memory --enable-simd --enable-sign-ext (package.json build:wasm) |
| **Adoption** | 199 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/justinwilaby/sax-wasm) · [benchmark](https://github.com/justinwilaby/sax-wasm#benchmarks) |

## Verdict

The README times one parse of the bundled 2.99 MB xml.xml written in 64 KiB chunks (mean of 10 runs, no warm-up, Node v25.6.1, macOS arm64, chip not stated, sax-wasm 3.1.4): sax-wasm 6.80 ms vs saxes 11.00 ms and sax-js 26.99 ms. But sax-wasm ran with no events subscribed, so the figure is tokenization only, and no like-for-like number is published. This session reproduced the direction under the README setup (15.9 vs 34.6 ms) and a reversal with four event types and handlers on both parsers (117.9 vs 46.8 ms, Node 22.22.0 on an Intel Xeon VM).

## Use it when

- You need source positions (line/character and UTF-8 byte offsets) for every tag, attribute and text node, for example in LSP servers, linters or codemods over XML, HTML, JSX or Angular templates.
- You need one tolerant tokenizer for JSX fragments, Angular bindings and unquoted HTML attributes, which strict XML parsers such as saxes reject.
- You stream UTF-8 bytes from fetch() or fs streams in a browser or Node in chunks of about 64 KiB, subscribe to one or two event types and read few fields per event, which is where lazy decoding helps most (this case was not measured).
- You want a parser whose memory stays bounded by chunk size rather than document size, with no DOM built.

## Skip it when

- Throughput-critical XML ingestion that consumes tags, attributes and text. In this enrichment session's check (npm 3.1.4, Node 22.22.0, a 4-vCPU Intel Xeon 2.1 GHz cloud VM, the repo's 2.99 MB xml.xml in 64 KiB chunks, median of 20 runs after 3 warm-ups), sax-wasm with OpenTag|CloseTag|Text|Attribute subscribed and names/values read took 117.9 ms, against 46.8 ms for saxes 6.0.0 with equivalent handlers (about 2.5x slower). Even with a no-op handler it took 72.0 ms. The README's own setup (no events) reproduced its 'faster' result: 15.9 vs 34.6 ms.
- Feeding whole documents or large ReadableStream chunks: any chunk near or above 1 MiB silently corrupts results or crashes (see gotchas), and the README gives no size limit.
- You need validation, namespace events, DTD/entity expansion or strict well-formedness errors: it is non-validating ('emits what it sees') and reports namespaces only as attributes.
- You need whitespace-only text nodes between elements: they are deliberately not emitted.
- You need a stable event ABI: the next major release (on HEAD, unreleased as of 2026-10-11) changes the event format and rejects older wasm binaries. The 2025 history also includes lost tags, text and attributes in large or chunked input (#113, #117, #119) and truncated leading zeros in text (#142), all since closed.

## How it is fast

A byte-oriented state machine in Rust walks the UTF-8 input (a grapheme iterator tracks line and column) and only materialises ('hydrates') strings for the event types set in the bitmask. Event payloads are written as descriptors into wasm linear memory, and the JS Reader objects decode fields lazily with TextDecoder on first access, so fields you never read cost nothing. The unreleased next major on HEAD (PRs #160 and #164, October 2026) adds wasm SIMD128 scans (i8x16_eq/bitmask) that skip ASCII runs up to the next delimiter and pools event descriptors; PR #160 reports only about 5% faster full decoding than the previous build. The release build uses opt-level 3, fat LTO, codegen-units 1 and wasm-opt -O4.

## Compared with alternatives

Against libxml2-wasm (the catalogued wasm XML sibling): pick sax-wasm when you need a small streaming tokenizer with byte and line positions that tolerates HTML, JSX and Angular syntax. Pick libxml2-wasm when you need a conformant parser with DOM, XPath or schema validation. For plain XML throughput where you consume events, the pure-JS baseline saxes was faster in this session's like-for-like check.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime, but you must ship or serve lib/sax-wasm.wasm yourself and pass it to prepareWasm() |
| **Minimum toolchain** | npm 3.1.4: Node &gt;=18.20.5 (ESM and CJS); repo HEAD (unreleased next major): Node &gt;=24.3.0 and TypeScript 7 tooling; building needs Rust stable (version not pinned) with the wasm32-unknown-unknown target and binaryen wasm-opt |
| **Platforms** | Node and modern browsers with WebAssembly. HEAD's parser uses wasm SIMD128 intrinsics and the build enables SIMD, bulk memory and sign-ext, so engines without wasm SIMD cannot run HEAD builds (inference from source; minimum browser versions not documented). |
| **Thread safety** | Single-threaded: each SAXParser owns one wasm instance holding a global static parser. Detail objects are only valid inside the handler or generator iteration, and calling write() from inside the handler risks overwriting live memory (README). |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory-safety bug in chunk handling, confirmed in this session on npm 3.1.4. write() copies each chunk to wasm linear-memory address 4 (`writeBuffer.set(chunk, 4)`), but the Rust module's own 17-page memory is laid out stack-first: __stack_pointer starts at 1,048,576, static data runs to 1,050,616 and the heap follows. On the repo's xml.xml, chunks of 64 KiB to 1,040,000 bytes gave identical results (27,637 open tags). 1,048,000-byte chunks silently produced 27,625 tags and a different content hash, with no error. 1,060,000 and 1,100,000-byte chunks raised 'RuntimeError: memory access out of bounds', and a 2.99 MB single write raised 'RangeError: offset is out of bounds'. Issue #141 hit the RangeError and was closed with a 'feed 64 KiB slices' workaround; the silent-corruption window is undocumented, and HEAD's src/js/saxWasm.ts still writes at address 4 (HEAD itself not re-tested). Slice inputs to 64 KiB yourself.
- Harness flaws behind the README table: sax-wasm runs with `new SAXParser()` (events = 0), so it hydrates nothing and never calls into JS, while saxes and sax-js build names, attributes and text and node-expat emits every event. The 'ltx (using Saxes as the parser)' row passes the raw SaxesParser instead of ltx's lib/parsers/saxes.js adapter, so ltx's startElement/endElement listeners land on an `undefined` property (saxes maps unknown event names that way), no tree is built, and the row is just saxes plus a no-op text callback. The README links node-xml to dylang/node-xml, an XML builder, while the script runs robrighter's 2012 node-xml 1.0.2 SAX parser. And despite the README's '100 internal runs per parser', the script does 10 single cold-inclusive runs.
- Event details are lazy views over wasm memory: they are overwritten by the next write(), so call toJSON() to keep anything. Memory also grows with chunk size: about 2.5 MB of wasm memory with 64 KiB chunks against 21.8 MB with 1,000,000-byte chunks in this session's run.
- prepareWasm(Uint8Array) passes `saxWasm.buffer` (the whole underlying ArrayBuffer) to WebAssembly.instantiate, ignoring byteOffset and byteLength. A Uint8Array view into a larger buffer (a bundle slice or a pooled Buffer) therefore fails; pass a standalone copy, a Response or a compiled WebAssembly.Module. The shared env.memory the wrapper constructs is never used, because the module defines and exports its own memory.

## Known shortcomings

- benchmark.mjs builds SAXParser() with the default events=0, so the wasm parser only tokenizes (no events built or sent to JavaScript) while saxes builds text, attributes and tags and checks well-formedness: no like-for-like run exists (tier D); the README's "100 internal runs" are not in the script and the numbers predate the October 2026 rewrites.
- Not faster in a like-for-like run (this session, npm 3.1.4, Node 22.22.0, 2.99 MB xml.xml, 64 KiB chunks, median of 20): with 4 events subscribed and names and values read, sax-wasm took 117.9 ms vs saxes 6.0.0 46.8 ms, about 2.5x slower; the README's no-events setup reproduced 15.9 vs 34.6 ms. Memory bug confirmed: write() copies each chunk to wasm address 4 inside the 1 MiB stack-first region, so chunks of 1,048,000 bytes silently produce wrong results (27,625 vs 27,637 open tags), 1,060,000 bytes raise 'RuntimeError: memory access out of bounds' and the whole file raises 'RangeError: offset is out of bounds' (issue #141 closed with a workaround only; HEAD still writes at 4). More README harness flaws: the ltx row passes a raw SaxesParser so no tree is built, the node-xml link points at the wrong package, and prepareWasm(Uint8Array) ignores byteOffset and byteLength.

## Caveats and trade-offs

Harness flaw: benchmark.mjs runs sax-wasm with zero subscribed events (constructor default), so the Rust parser skips hydration, event emission and every JS boundary crossing, while saxes and sax-js still build text, attribute and tag values and enforce well-formedness, and node-expat (a native libexpat binding) delivers each event to JavaScript; the comparison does not reflect any real use of sax-wasm. scripts/benchmark-performance.mjs measures callbacks and field reads but only between sax-wasm builds, with no recorded results. The README says 10 batches of 100 internal runs, but the script does 10 single parses with no warm-up (mean includes the cold first run). Numbers predate the October 2026 parser rewrites (#160, #164). CPU model not stated (macOS Apple Silicon only); Rust version not pinned. First-party. [retier] Harness flaw: benchmark.mjs runs sax-wasm with zero subscribed events (constructor default), so the Rust parser skips hydration, event emission and every JS boundary crossing, while saxes and sax-js build text, attribute and tag values and node-expat delivers each event to JavaScript. Like-for-like run in this session (npm 3.1.4, Node 22.22.0, 2.99 MB xml.xml, 64 KiB chunks, median of 20) with 4 events subscribed and names and values read: sax-wasm 117.9 ms vs saxes 6.0.0 46.8 ms, about 2.5x slower; the README's no-events setup reproduced at 15.9 vs 34.6 ms. The 'ltx (using Saxes as the parser)' row passes a raw SaxesParser instead of ltx's adapter, so no tree is built; the node-xml link points at dylang's XML builder while the script runs robrighter node-xml 1.0.2; the README says 10 batches of 100 runs but the script does 10 single parses with no warm-up. Memory-safety bug confirmed on npm 3.1.4: write() copies each chunk to wasm linear-memory address 4 inside the 1 MiB stack-first region, so chunks of 1,048,000 bytes silently produce wrong results (27,625 vs 27,637 open tags), 1,060,000-byte chunks raise 'RuntimeError: memory access out of bounds' and the whole file raises 'RangeError: offset is out of bounds' (issue #141 closed with a workaround only; HEAD glue still writes at 4). prepareWasm(Uint8Array) ignores byteOffset and byteLength; event details are lazy views overwritten by the next write(). Numbers predate the October 2026 parser rewrites (#160, #164); CPU model not stated; first-party.

Event-based SAX API with fixed-memory streaming; supports JSX and Angular templates. Requires loading the wasm file; node &gt;=24.3.0 per README.

## Maintenance

Actively maintained (commits through 2026-10-10, next major in progress) and MIT-licensed. The evidence stays at D: the only published comparison is degenerate, a like-for-like run in this session found it about 2.5x slower than saxes, and npm 3.1.4 silently corrupts or traps on chunks near or above 1 MiB, so slice input to 64 KiB if you adopt it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README numbers match, but src/js/__test__/benchmark.mjs builds sax-wasm with new SAXParser() and the constructor default is events = 0, so src/sax/parser.rs hydrates nothing, emits no event and never crosses into JavaScript (a tokenizer-only pass), while saxes still accumulates text, builds attribute lists and tags and checks well-formedness, and node-expat emits every event to JS. No like-for-like comparison is recorded anywhere (scripts/benchmark-performance.mjs, which subscribes events, only compares sax-wasm builds with each other), so there is no valid comparative measurement (degenerate-workload precedent).
- **Verifier notes:** Numbers on page are accurate but measure sax-wasm with events = 0 (confirmed in src/js/saxWasm.ts constructor and src/sax/parser.rs, where every hydrate/emit is gated on self.events), so the comparison is degenerate; downgraded C to D rather than rejected because the parser does tokenize the full input. MIT, 199 stars, last commit 2026-10-10, not a fork. A like-for-like run (events OpenTag|CloseTag|Text|Attribute with handlers on all parsers) would be needed to restore C.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier batch-87 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/js/__test__/benchmark.mjs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/scripts/benchmark-performance.mjs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/js/saxWasm.ts>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/sax/parser.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lddubeau/saxes/HEAD/src/saxes.ts>
  - <https://github.com/justinwilaby/sax-wasm>
  - <https://github.com/justinwilaby/sax-wasm/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/js/__test__/benchmark.mjs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/js/__test__/xml.xml>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/scripts/benchmark-performance.mjs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/js/saxWasm.ts>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/sax/parser.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/sax/grapheme_iterator.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/sax_wasm.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/src/sax/mod.rs>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/justinwilaby/sax-wasm/HEAD/package-lock.json>
  - <https://github.com/justinwilaby/sax-wasm/commits>
  - <https://github.com/justinwilaby/sax-wasm/pull/160>
  - <https://github.com/justinwilaby/sax-wasm/issues?q=is%3Aissue>
  - <https://github.com/justinwilaby/sax-wasm/issues/141>
  - <https://github.com/justinwilaby/sax-wasm/issues/113>
  - <https://registry.npmjs.org/sax-wasm>
  - <https://registry.npmjs.org/sax-wasm/-/sax-wasm-3.1.4.tgz>
  - <https://raw.githubusercontent.com/lddubeau/saxes/HEAD/src/saxes.ts>
  - <https://registry.npmjs.org/saxes/-/saxes-6.0.0.tgz>
  - <https://registry.npmjs.org/xmlchars/-/xmlchars-2.2.0.tgz>
  - <https://registry.npmjs.org/ltx>
  - <https://registry.npmjs.org/ltx/-/ltx-3.1.2.tgz>
  - <https://raw.githubusercontent.com/xmppjs/ltx/main/src/Parser.js>
  - <https://raw.githubusercontent.com/xmppjs/ltx/HEAD/package.json>
  - <https://registry.npmjs.org/node-xml>
  - <https://registry.npmjs.org/node-xml/-/node-xml-1.0.2.tgz>
  - <https://raw.githubusercontent.com/dylang/node-xml/HEAD/package.json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/justinwilaby/sax-wasm`) · [data/wave13/enrich/raw/github_com_justinwilaby_sax_wasm.json](../../../data/wave13/enrich/raw/github_com_justinwilaby_sax_wasm.json) (enrichment confidence 0.8)

</details>
