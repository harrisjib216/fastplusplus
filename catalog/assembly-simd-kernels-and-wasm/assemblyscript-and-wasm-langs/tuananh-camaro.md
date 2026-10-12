# camaro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++ (pugixml) compiled to WebAssembly + JavaScript` · `MIT` · 🟢 active

> Node.js XML-to-JSON extractor (pugixml in Wasm) using XPath templates; about 5x txml, 24-37x other JS parsers on 60 KB.

| | |
|---|---|
| **Beats** | Pure-JavaScript XML parsers in Node.js/V8: txml, fast-xml-parser, xml-js, xml2js |
| **Claimed result** | README table (Node, mitata; CPU, Node and emcc versions unstated): camaro v6 98.94 us/iter vs txml 491.71 us, xml-js 2.49 ms, fast-xml-parser 2.63 ms, xml2js 3.58 ms; the summary prints 5.27x, 25.78x, 24.21x and 37.02x while the table as printed gives 4.97x, 25.17x, 26.58x and 36.18x (derived from page data). The camaro row and the summary ratios were replaced by commit bd296c7 (2026-08-13) while the four competitor rows date from the 2026-08-07 run (commit 2314fc6), so the ratios are cross-run; the summary ordering (25.78x before 24.21x despite mitata sorting by mean) shows it was not one run. camaro extracts about 64 template values from a 60 KB fixture of 681 elements and 405 attributes while the four JS parsers build the full tree, which the README itself calls 'an unfair game for camaro'. |
| **Workload** | Transform a 60 KB Expedia hotel-list XML response to JSON with an XPath-like template (only the template's fields are extracted), mitata-style iterations |
| **Metric** | latency |
| **Hardware** | Not stated for the current README (mitata) numbers. The 'AMD 4650G 6 cores - 12 threads/ 32GB memory' spec is in benchmark/README.md on the master branch and v6.2.3 tag, which belongs to an older ops/sec harness; that file is absent from the default develop branch. |
| **Compiler and flags** | emcc -O3 -flto -msimd128 -DNDEBUG -std=gnu++98 -fno-exceptions -fno-rtti (pugixml and core), Embind adapter at -std=gnu++17, linked with emmalloc and --closure 1 (build.sh); emcc version, Node.js version and mitata settings of the README run are not stated (package.json: engines node &gt;= 20.x, mitata ^1.0.34). |
| **Adoption** | 581 stars; npm package camaro |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/tuananh/camaro) · [benchmark](https://github.com/tuananh/camaro#-benchmark) |

## Verdict

In a first-party mitata run in Node.js (CPU, Node and emcc versions not stated), camaro's transform on a 60 KB Expedia hotel-list fixture averaged 98.94 us/iter. That covers UTF-8 encoding, the copy into the Wasm heap, a full pugixml parse, extraction of about 64 templated fields and JSON.parse of the result. Full-tree parses took 491.71 us (txml), 2.49 ms (xml-js), 2.63 ms (fast-xml-parser) and 3.58 ms (xml2js), but those rows come from an earlier run than camaro's row and the printed 5.27x/25.78x/24.21x/37.02x ratios; the table as printed gives about 5x, 25x, 27x and 36x (derived from page data).

## Use it when

- Node.js services that pull a few dozen fields out of large XML API responses (SOAP, travel/booking APIs, feeds) of tens of KB and up.
- When you want output shaped and typed by a declarative XPath template (renames, number() and boolean() casts, string functions) instead of walking a parsed tree by hand.
- Servers handling many XML documents concurrently: the first in-flight call runs on the main thread and further concurrent calls go to a worker_threads pool with SharedArrayBuffer IPC.
- Deployments that cannot build native addons: the package ships a prebuilt dist/camaro.wasm and runs on any OS with Node.js 20+.

## Skip it when

- Small XML strings: the README warns camaro will probably be slower than pure-JS parsers there, and the current harness only measures a 60 KB fixture.
- When you need the whole tree or round-tripping: transform only returns templated fields, and toJson emits camaro's own JSON shape with no published speed numbers.
- When malformed input must fail loudly: a parse failure makes the binding return an empty object (makeTransformValue in src/camaro_bindings.cpp), so transform resolves to {} instead of rejecting, and an invalid XPath yields '' (test/invalid-xpath.test.js).
- Browsers or streaming: it is a Node.js package (process.env, path, worker_threads), and each document is copied whole into the 32-bit Wasm heap, with no SAX or streaming mode.
- Templates generated per request: compiled templates are cached for the life of the process (see gotchas).

## How it is fast

The XML is encoded once with TextEncoder.encodeInto into a reused scratch buffer, copied into a reused Wasm heap buffer, and parsed in place by pugixml's single-pass DOM parser, so text is not copied into per-node strings (build: emcc -O3 -flto -msimd128, C++98 without exceptions or RTTI, emmalloc). Templates are compiled once and cached by id with their XPath queries, and simple paths are walked directly without the XPath engine. Only the selected values are written by a C++ JSON writer into one string, which JavaScript turns into objects with a single JSON.parse, so the hundreds of JS objects a full-tree parser allocates are never created.

## Compared with alternatives

The catalogued Wasm siblings that beat pure-JS parsers (json-as for JSON, calaminejs for spreadsheets, markdown_yo for Markdown) do not handle XML; pick camaro when the input is XML and you need a subset of fields. Like markdown_yo it has a small-input crossover, so check your document sizes first.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (a pugixml fork is compiled into dist/camaro.wasm); rebuilding needs Emscripten and napa to fetch tuananh/pugixml at a pinned commit |
| **Minimum toolchain** | Node.js 20+ (package.json engines; CI tests Node 20.x-26.x); the Wasm is built with -msimd128, so the runtime needs Wasm SIMD; the dev shell in flake.nix uses nixpkgs-unstable emscripten and nodejs_26 |
| **Platforms** | any OS and CPU that runs Node.js 20+ (WebAssembly, no native addon); Node.js only |
| **Thread safety** | All calls are async. One in-flight call runs on the main thread and concurrent calls go to a worker_threads pool sized by CAMARO_POOL_SIZE; CAMARO_FORCE_SINGLE_THREAD=true keeps everything on the main thread; destroy() shuts the pool down. |
| **Drop-in for the baseline** | no |

## Gotchas

- Reporting flaw in the README benchmark: commit bd296c7 (2026-08-13) replaced only the camaro row and the summary ratios, leaving the txml, fast-xml-parser, xml2js and xml-js rows from the 2026-08-07 run (commit 2314fc6). The summary cannot come from one mitata run: mitata sorts summary lines by mean time, yet 25.78x (xml-js) is printed before 24.21x (fast-xml-parser). The table as printed gives 4.97x, 25.17x, 26.58x and 36.18x (derived from page data). Magnitudes are similar, but the headline numbers mix two runs, and none of the runs states the CPU, Node or emcc version.
- Unequal work: the 60 KB fixture holds 681 elements and 405 attributes but only one HotelSummary with 12 rooms, so camaro's template returns about 64 values while the four JS parsers build the full tree as JS objects. The repo's like-for-like script (benchmark/to-json.js, npm run bench:to-json: camaro toJson against the same parsers) exists, but no results are published.
- Every distinct template string is cached for the life of the process: worker.js keeps a Map from template JSON to id with no eviction, and the native context keeps each registered template and its compiled XPath queries. Templates built dynamically per request therefore grow memory without bound.
- Releases 6.6.0 and 6.7.0 returned only the first parent's children for multi-parent paths such as players/group/player (issue #178, fixed in 6.7.1 on 2026-08-11); pin versions. pugixml runs with parse_cdata|parse_escapes only, so CRLF line ends and attribute whitespace are not normalised as the XML spec requires.

## Known shortcomings

- Downgraded A to C: README mitata numbers match but state no CPU, Node or emcc version; the AMD 4650G line comes from an older benchmark on master/v6.2.3 with a different harness; unequal work (template extraction vs full-tree parse); single fixture; the README calls its own benchmark unfair.
- The README benchmark mixes two runs: commit bd296c7 (2026-08-13) updated only the camaro row and the summary ratios, while the competitor rows date from commit 2314fc6 (2026-08-07); the summary cannot come from one mitata run (25.78x is printed before 24.21x despite sorting by average), and the table as printed gives 4.97x, 25.17x, 26.58x and 36.18x (derived from page data). Unequal work: the fixture has 681 elements and 405 attributes while the template extracts about 64 values; the like-for-like bench/to-json.js exists but its results are unpublished. Malformed XML resolves to {}; the template cache never evicts; #178 (XPath regression in 6.6.0-6.7.0) was fixed in 6.7.1.

## Caveats and trade-offs

README itself says this is 'an unfair game for camaro': camaro extracts only the template's fields while txml, fast-xml-parser, xml-js and xml2js build the full document tree, so the comparison is not like-for-like work. The README numbers (updated 2026-08-13, 'chore: update readme with latest benchmark') state no CPU, Node.js or emcc version; the AMD 4650G spec belongs to an older harness on the master branch. Single 60 KB fixture in the current harness; the README warns that small XML strings will probably be slower than pure-JS parsers (the older benchmark README showed camaro behind on the 7 KB fixture). The library's transform() is async and can dispatch to a worker_threads pool; a single in-flight request runs on the main thread, which is what the benchmark measures. [retier] The README itself says the comparison is unfair: camaro extracts only the template's fields while txml, fast-xml-parser, xml-js and xml2js build the full document tree, so the work is not like-for-like; the repo's like-for-like script (benchmark/to-json.js, npm run bench:to-json) exists but no results are published. Reporting flaw: the camaro row and summary ratios come from a different run (2026-08-13) than the competitor rows (2026-08-07), and the summary line order shows it was not a single mitata run. No CPU, Node.js or emcc version is stated (the AMD 4650G spec belongs to an older harness on master); a single 60 KB fixture; the README warns small XML strings will probably be slower than pure-JS parsers. Every distinct template string is cached for the life of the process with no eviction (worker.js Map plus native compiled XPath queries), so dynamic templates grow memory without bound; malformed XML resolves to {}; releases 6.6.0 and 6.7.0 returned only the first parent's children for multi-parent paths (issue #178, fixed in 6.7.1 on 2026-08-11); pugixml runs with parse_cdata|parse_escapes only, so CRLF and attribute whitespace are not normalised.

Template-driven extraction rather than a general parse: output only contains requested fields. Small XML strings are probably slower than pure JavaScript parsers (README warning). Worker-thread pool for multi-core.

## Maintenance

Actively maintained (last commit 2026-09-11, 769 commits, package 6.7.3, CI on Node 20-26), MIT-licensed with 581 stars and used by hexo's sitemap and feed generators; ship it as an npm dependency rather than vendoring, and pin the version given the 6.6-6.7 XPath regression.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now D.
- **Tier reason:** First-party mitata run with public code (benchmark/transform.js, build.sh flags), but the README numbers carry no CPU model, Node.js version or emcc version; the 'AMD 4650G' line comes from the older benchmark/README.md on the master branch / v6.2.3 tag, which describes a different harness (10,000 iterations, ops/sec, four fixture sizes), and that file no longer exists on the default develop branch.
- **Retiered** C to D: Enricher: the README table divides a camaro row re-measured on 2026-08-13 (commit bd296c7) by competitor rows kept from the 2026-08-07 run (commit 2314fc6), the summary ratios cannot come from one mitata run, and the work differs by design (about 64 extracted values against four full document trees); the like-for-like bench/to-json.js has no published results. Cross-run ratios on unequal work (PostgreSQL/MySQL cross-run precedent): C to D.
- **Verifier notes:** Numbers (98.94 us vs txml 491.71 us, 5.27x/25.78x/24.21x/37.02x) match the README exactly and the benchmark code is public, but the run has no stated CPU or runtime versions, so A drops to C. Shortcomings to record: unequal work (template extraction vs full-tree parse, admitted by the author), no hardware/Node version for the current numbers, single fixture, slower on small inputs.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-18 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tuananh/camaro#-benchmark>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/README.md>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/build.sh>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/package.json>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/transform.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/baseline.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/index.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/master/benchmark/README.md>
  - <https://raw.githubusercontent.com/tuananh/camaro/v6.2.3/benchmark/README.md>
  - <https://github.com/tuananh/camaro/tree/develop/benchmark>
  - <https://github.com/tuananh/camaro>
  - <https://github.com/tuananh/camaro/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/tuananh/camaro>
  - <https://github.com/tuananh/camaro/commits/develop/README.md>
  - <https://github.com/tuananh/camaro/commit/bd296c7>
  - <https://github.com/tuananh/camaro/commit/2314fc6>
  - <https://github.com/tuananh/camaro/commit/1f06a2c>
  - <https://github.com/tuananh/camaro/issues?q=is%3Aissue>
  - <https://github.com/tuananh/camaro/issues/178>
  - <https://github.com/tuananh/camaro/tree/develop/test>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/README.md>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/API.md>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/build.sh>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/package.json>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/.github/workflows/ci.yaml>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/index.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/index.d.ts>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/worker.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/json-parse.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/src/camaro.cpp>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/src/camaro_bindings.cpp>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/src/pugiconfig.hpp>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/transform.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/baseline.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/to-json.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/benchmark/fixtures/60kb.xml>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/test/input.test.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/test/invalid-xpath.test.js>
  - <https://raw.githubusercontent.com/tuananh/camaro/HEAD/test/template-cache.test.js>
  - <https://raw.githubusercontent.com/evanwashere/mitata/master/src/main.mjs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tuananh/camaro`) · [data/wave13/enrich/raw/github_com_tuananh_camaro.json](../../../data/wave13/enrich/raw/github_com_tuananh_camaro.json) (enrichment confidence 0.8)

</details>
