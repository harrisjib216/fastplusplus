# source-map (mozilla/source-map, Rust/WebAssembly mappings parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `JavaScript with Rust compiled to WebAssembly (wasm-mappings)` · `BSD-3-Clause` · 🟢 active

> Mozilla's source-map library with its mappings parser in Rust compiled to WebAssembly; beats the library's own 0.6 JavaScript parser.

| | |
|---|---|
| **Beats** | source-map 0.6 pure-JavaScript source map parser (the same library before the Rust/wasm rewrite of the mappings parser) |
| **Claimed result** | Independent (@jridgewell/trace-mapping README, Node v20.10.0): source-map 0.8.0-beta.0 (wasm SourceMapConsumer) is 1.8-4.8x faster than source-map 0.6.1 (pure JS) on originalPositionFor across the README's fixtures (derived from page data); on ascending-order lookups the pure-JS trace-mapping beats it (196,695 vs 51,427 ops/s). Vendor post (Mozilla Hacks, January 2018, snippet only): up to 5.89x faster than the JavaScript implementation on realistic benchmarks over real-world source maps; editor's note: later algorithmic improvements give up to 10.9x total over the original. |
| **Workload** | Parsing and querying real-world source maps in the library's own benchmark page (bench/bench.html), Rust-to-WebAssembly mappings parser versus the previous JavaScript parser. |
| **Metric** | throughput |
| **Adoption** | 3.7k stars; the wasm parser ships in source-map 0.7+, widely used by JS tooling |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/mozilla/source-map) · [benchmark](https://hacks.mozilla.org/2018/01/oxidizing-source-maps-with-rust-and-webassembly/) |

## Verdict

First-party: the January 2018 Mozilla Hacks post (seen only through search snippets; hacks.mozilla.org and fitzgen.com fail to resolve here) says the Rust/wasm parser was up to 5.89x faster than the 0.6 JS parser on bench/bench.html with real-world maps, and an editor's note gives up to 10.9x after later algorithmic work; no hardware or browser versions are recorded in the repo, and the per-browser 5.3x/10.8x/9.4x split could not be confirmed this session. Independent: trace-mapping's README (node v20.10.0, hardware not stated) has source-map 0.8.0-beta.0 at 1.8-4.8x the originalPositionFor throughput of 0.6.1 on amp.js.map, babel.min.js.map and preact.js.map (for example 28,198 vs 8,057 ops/s random on amp.js.map; derived from page data); its init-speed table omits the async 0.8 consumer, so parse cost is not compared.

## Use it when

- Node.js tooling that symbolicates many stack frames or profiler samples against large maps through the mozilla API (originalPositionFor, allGeneratedPositionsFor, eachMapping) and can await consumer construction.
- Existing source-map 0.6 users who want faster lookups and can afford the async constructor and the explicit destroy() calls.
- Short-lived consumers wrapped in SourceMapConsumer.with(), so the wasm memory is freed automatically.
- Random-access lookups on very large maps: in trace-mapping's own benchmark (babel.min.js.map, 347,793 segments) source-map 0.8.0-beta.0 reached 84,002 ops/s against 60,761 for encoded trace-mapping (derived from page data).
- Cases where you need the consumer, SourceMapGenerator and SourceNode from one zero-dependency package.

## Skip it when

- Long-running services that cache many consumers. All consumers in a realm share one wasm instance and one linear memory, and issue #476 (open since Feb 2023) reports RuntimeError: unreachable after about 100 cached consumers, with no catchable out-of-memory error.
- Code paths that must stay synchronous. The 0.7.0 constructor returns a Promise, which is why much tooling stayed on 0.6.1 or moved to other parsers.
- Pure-JS deployments, browser ESM or single-bundle builds. 0.8.0 ships no browser bundle (dist/ was removed in #362; #408 and #527 are open), ESM in the browser is reported broken (#496), and mappings.wasm must be served or passed as an ArrayBuffer.
- Workloads where @jridgewell/trace-mapping (pure JS, no wasm, no destroy) is enough. Its README (node v20.10.0) has it beating source-map 0.8.0-beta.0 on ascending lookups (196,695 vs 51,427 ops/s on amp.js.map, 3.8x) and on random lookups in amp.js.map (37,995 vs 28,198); all figures derived from page data.
- Builds that must compile the wasm from source with current Rust. Building wasm-mappings fails on Rust 1.96+ with 'rust-lld: error: undefined symbol: mapping_callback' (#530, open since Jul 2026).

## How it is fast

JavaScript copies the mappings string byte by byte into wasm linear memory. Rust then decodes the base64 VLQ segments into flat Mapping structs, which avoids allocating one JS object per mapping. The generated-order array only sorts the tail of each generated line, because the encoding is already ordered by line. Original-order lookups use per-source buckets that are sorted lazily on first use, and queries are binary searches over these arrays. The parse is lazy: it runs on the first query, not in the constructor. Nick Fitzgerald's follow-up posts say part of the gain is algorithmic: mraleph tuned the plain JS version to roughly match, and the Rust code then adopted the same ideas (seen in search snippets only).

## Compared with alternatives

No sibling parses source maps. The closest pattern is Automerge 2.x (Rust core compiled to wasm replacing the same project's earlier JS), and like there, the gain is over the project's own older JS with a manual-free/async API cost. Pick this for the mozilla consumer API; for lookups alone, check pure-JS @jridgewell/trace-mapping first.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (npm package with a prebuilt lib/mappings.wasm); rebuilding the wasm needs Rust targeting wasm32-unknown-unknown (1.95 or older per #530) plus wasm-nm, wasm-gc, wasm-snip and wasm-opt (build.py) |
| **Minimum toolchain** | Node.js &gt;= 12 (package.json engines); browsers need WebAssembly and fetch, or an ArrayBuffer passed to initialize() |
| **Platforms** | any JavaScript engine with WebAssembly (wasm32; 4 GiB linear-memory ceiling shared by all consumers in a realm) |
| **Thread safety** | not documented; one cached wasm instance per JS realm, shared by every consumer through a callback stack; each worker instantiates its own |
| **Drop-in for the baseline** | partial: same query and generator API as 0.6, but construction is async (Promise), browsers must call SourceMapConsumer.initialize(), and consumers must be destroy()ed |

## Gotchas

- Wasm memory is never garbage collected and never shrinks. parse_mappings preallocates the generated-order vector at input.len()/2 Mapping structs and never shrinks it. By my reading of the struct layout that is about 36 bytes per Mapping, so roughly 18 bytes of wasm memory reserved per byte of mappings text. Per-source copies are added on the first original-order query. This fits the out-of-memory 'unreachable' traps in #476: release builds call process::abort() instead of returning an error.
- destroy() only frees the parsed data and resets the pointer to 0. Querying the consumer again silently re-parses the retained mappings string (_getMappingsPtr), allocating fresh wasm memory that must be destroyed again; use after destroy is not an error.
- Parsing is lazy, so the constructor does not validate the mappings. Bad VLQ data throws 'Error parsing mappings (code N)' at the first query, and the first query pays the whole parse cost.
- The README's 'Use on the Web' snippet still loads unpkg source-map@0.7.3/dist/source-map.js, because 0.7.5 and 0.8.0 ship no dist bundle. The in-repo benchmark (bench/bench.html) likewise needs a bundle built with bench/webpack.config.js on webpack ^4.9.1 and webpack-cli ^3.1, and the repo records no results, hardware or browser versions.

## Known shortcomings

- The 5.89x and 10.9x figures are known from search snippets only (hacks.mozilla.org blocked); mraleph tuned the JavaScript version first and Fitzgerald then moved those ideas into Rust (10.9x).
- The Rust parser preallocates input.len()/2 Mapping structs (about 18 bytes of wasm memory per byte of mappings text, estimate) and never shrinks them, which fits open issue #476 ('RuntimeError: unreachable' after about 100 consumers); querying after destroy() silently re-parses and re-leaks; bench/bench.html needs a webpack 4 build and records no results; the wasm rebuild fails on Rust 1.96+ (#530). The 5.89x and 10.9x remain snippet-only (hacks.mozilla.org and fitzgen.com unreachable). Independent numbers: the @jridgewell/trace-mapping README (Node v20.10.0) shows source-map 0.8.0-beta.0 1.8-4.8x faster than 0.6.1 on originalPositionFor, while pure-JS trace-mapping beats it on ascending lookups (196,695 vs 51,427 ops/s).

## Caveats and trade-offs

Snippet only: hacks.mozilla.org failed to resolve (ENOTFOUND) in this environment, so the 5.89x figure and the editor's-note 10.9x total come from web-search snippets; the repo itself carries no numbers (CHANGELOG 0.7.0 says SourceMapConsumer 'now uses WebAssembly, and is much faster' and links the post). bench/ is a browser page (bench/bench.html against dist/source-map.js) with no recorded hardware or browser versions. Vyacheslav Egorov (mraleph) showed a tuned pure-JavaScript parser could come close to the Rust/wasm version; Nick Fitzgerald's follow-up 'Speed Without Wizardry' ported those algorithmic ideas to the Rust code, which is where the 10.9x total comes from (snippet: 5.3x Chrome, 10.8x Firefox, 9.4x Safari over the original JavaScript). The win is against the 0.6.x JS parser in 2018 browsers. 0.7.0 made SourceMapConsumer construction asynchronous (returns a Promise) and browsers must call SourceMapConsumer.initialize() with the lib/mappings.wasm URL. The wasm-mappings Rust crate (source-map-mappings 0.5.0) is in the repo with [profile.release] debug = true. [retier] The Mozilla Hacks figures (5.89x, 10.9x) remain snippet-only (hacks.mozilla.org and fitzgen.com unreachable); the repo carries no numbers and bench/bench.html needs a webpack 4 build and records no results, hardware or browser versions. The independent trace-mapping README numbers compare 0.8.0-beta.0 against 0.6.1 on one unnamed machine under Node v20.10.0 and show pure-JS trace-mapping ahead on ascending lookups, so the wasm consumer is not the fastest JS-side option. Vyacheslav Egorov showed a tuned pure-JavaScript parser could come close to the Rust/wasm version, and Nick Fitzgerald's follow-up ported those algorithmic ideas into the Rust code, which is where the 10.9x total comes from. Wasm memory is never garbage collected and never shrinks: parse_mappings preallocates input.len()/2 Mapping structs (about 18 bytes of wasm memory per byte of mappings text, estimate) and never shrinks them, which fits the out-of-memory 'unreachable' traps in open issue #476; querying after destroy() silently re-parses and re-leaks; parsing is lazy, so bad VLQ data throws at the first query. The wasm rebuild fails on Rust 1.96+ (#530); 0.7.5 and 0.8.0 ship no dist bundle.

Consumers must load lib/mappings.wasm (URL or ArrayBuffer passed to SourceMapConsumer.initialize), initialization is async, and each consumer must be freed manually with destroy() because wasm memory is not garbage collected; adds a .wasm file to deployments.

## Maintenance

Active Mozilla project (0.8.0 published to npm 2026-07-20 after a three-year gap, last commit 2026-07-21), BSD-3-Clause and copyable. The 2018 speedup is over the library's own untuned JS, which mraleph showed could be tuned to roughly match, and the open issues on wasm memory exhaustion (#476), browser bundling (#408, #527, #496) and Rust 1.96+ builds (#530) are the main risks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** First-party numbers from the library authors' Mozilla Hacks post (5.89x, later 10.9x), seen only through web-search snippets because hacks.mozilla.org did not resolve here; the repo's bench/bench.html harness is public but runs in a browser with no recorded hardware, browser versions or flags, and the CHANGELOG 0.7.0 entry only says 'much faster' with a link to the post.
- **Retiered** C to B: Enricher found an independent measurement: the @jridgewell/trace-mapping README (Node v20.10.0) benchmarks source-map 0.8.0-beta.0 (the wasm consumer) at 1.8-4.8x faster than the pure-JS source-map 0.6.1 on originalPositionFor, while pure-JS trace-mapping beats it on ascending lookups. Independent third-party numbers: C to B, with the vendor-post figures kept as snippet-only.
- **Verifier notes:** Figures match the snippet the search agent used and a second snippet search; page itself unopenable (ENOTFOUND). Metadata verified: BSD-3-Clause LICENSE, 3.7k stars, last commit 2026-07-21 (0.8.0 release), not archived or forked, wasm-mappings and bench folders present. Shortcomings: snippet-only 2018 numbers, no hardware or browser versions, baseline is the library's own untuned older JS parser.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-87 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/package.json>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/Cargo.toml>
  - <https://github.com/mozilla/source-map>
  - <https://github.com/mozilla/source-map/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/package.json>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/lib/source-map-consumer.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/lib/wasm.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/lib/read-wasm.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/lib/read-wasm-browser.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/bench.html>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/bench.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/bench-dom-bindings.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/package.json>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/bench/webpack.config.js>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/Cargo.toml>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/README.md>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/src/lib.rs>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/source-map-mappings-wasm-api/Cargo.toml>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/source-map-mappings-wasm-api/src/lib.rs>
  - <https://raw.githubusercontent.com/mozilla/source-map/HEAD/wasm-mappings/source-map-mappings-wasm-api/build.py>
  - <https://github.com/mozilla/source-map/tree/master/bench>
  - <https://github.com/mozilla/source-map/issues?q=is%3Aissue+wasm>
  - <https://github.com/mozilla/source-map/issues/476>
  - <https://github.com/mozilla/source-map/issues/530>
  - <https://registry.npmjs.org/source-map>
  - <https://raw.githubusercontent.com/jridgewell/sourcemaps/HEAD/packages/trace-mapping/README.md>
  - https://hacks.mozilla.org/2018/01/oxidizing-source-maps-with-rust-and-webassembly/ (ENOTFOUND; search snippets only)
  - https://fitzgen.com/2018/02/26/speed-without-wizardry.html (ENOTFOUND; search snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mozilla/source-map`) · [data/wave13/enrich/raw/github_com_mozilla_source_map.json](../../../data/wave13/enrich/raw/github_com_mozilla_source_map.json) (enrichment confidence 0.72)

</details>
