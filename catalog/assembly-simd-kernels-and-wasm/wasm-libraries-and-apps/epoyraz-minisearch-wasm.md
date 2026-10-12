# minisearch-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/Wasm reimplementation of MiniSearch 7.2.0 behind the same API; about 2x faster search(), 3.3x addAll, 7.5x autoSuggest.

| | |
|---|---|
| **Beats** | MiniSearch 7.2.0 (JavaScript full-text search library) |
| **Claimed result** | Fresh-index first-batch rows (like-for-like): 2.09x/4.16x/8.85x over MiniSearch; 'warm' rows (same 38 queries on one index) are memo-dominated on real corpora (fuzzy walk about 86% of query cost per the source) and the older README 11x/23x figures come from them; autoSuggest 7.5x measured warm only |
| **Workload** | differential/bench_public.mjs: 20,000 synthetic documents from differential/gen_corpus.mjs, 38 queries with {prefix: true, fuzzy: 0.2, combineWith: 'AND'}, two warm-ups then 9 paired rounds in alternating order, medians; pinned MiniSearch 7.2.0 and the public package in the same Node process; search(), autoSuggest, addAll, loadJSON, save/load and vacuum rows, plus dirty-index (25% discarded) and callback rows. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3900X 12-Core Processor, 64 GiB RAM, Windows (win32 x64), Node v24.21.0 |
| **Compiler and flags** | Rust 1.96.0 pinned in rust-toolchain.toml; wasm-pack 0.15.0 build --target web --release; Cargo [profile.release] opt-level = 3, lto = true, codegen-units = 1; .cargo/config.toml rustflags -C target-feature=+simd128 for wasm32-unknown-unknown; benchmark run with node --expose-gc |
| **Adoption** | 4 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/epoyraz/minisearch-wasm) · [benchmark](https://github.com/epoyraz/minisearch-wasm#measured-speedups) |

## Verdict

The author's public harness differential/bench_public.mjs (AMD Ryzen 9 3900X, Windows, Node v24.21.0; Rust 1.96.0, wasm-pack 0.15.0, opt-level 3, LTO, codegen-units 1, simd128) timed the locally built package against pinned MiniSearch 7.2.0 in the same process on 20,000 synthetic documents and 38 prefix+fuzzy AND queries, after checking 934,016 result rows for identical scores; medians of 9 paired alternating rounds give search() 2.20x (479 vs 217 ms), autoSuggest 7.48x, addAll 3.25x and loadJSON 1.83x, while the 65x (toBytes vs JSON.stringify) and 10x (loadBytes vs loadJSON) rows compare a binary format against JSON.

## Use it when

- Existing MiniSearch users in Node or a browser whose search(), autoSuggest or addAll time shows up in profiles: swap the import (and await init() in browsers) and keep the same rankings and callbacks.
- Search-as-you-type over tens of thousands of documents, where the same committed terms are re-queried every keystroke (expansion memo; autoSuggest measured 7.5x).
- Apps that ship a prebuilt index: loadBytes measured 10x faster than MiniSearch loadJSON, and the binary snapshot is 7.5x smaller raw and about 2.5x smaller after brotli (736 vs 1,864 KiB, derived from page data).
- Hot paths that can consume compact results: searchRaw (typed arrays plus an interned term table) measured 9.9x and searchJoined 4.8x versus MiniSearch search(), decoding included.
- Bulk indexing and maintenance in Node: addAll 3.3x and vacuum after a 25% discard 17x on 20,000 documents.

## Skip it when

- Small indexes or cold-start-sensitive pages: module import measured 13.8 ms vs 3.7 ms for MiniSearch, the Wasm file is about 826 KB raw (313 KB gzipped) and the npm package 1.4 MB unpacked (469 KB tarball).
- Browsers that do not await init(): the constructor silently runs the bundled JavaScript MiniSearch at no gain; pages whose CSP lacks 'wasm-unsafe-eval', or runtimes without Wasm SIMD, cannot use the Wasm path.
- Code relying on MiniSearch edge behaviour: a query-tree node with its own boostDocument, non-string field text, Infinity in options or a repeated fields entry move the index permanently to JavaScript; boostDocument cannot search or change the index re-entrantly; loose coercions such as prefix: 1 or fuzzy: '0.2' throw; fractional fuzzy values of 1 or more mean an edit distance.
- Long-lived indexes under tight memory budgets: Wasm linear memory does not shrink after compact(), the expansion cache is bounded by entry count (4,096 per map), not bytes, and saving fails past 2,000,000 internal id slots until the index is compacted.
- Risk-averse production use: one maintainer, 4 stars, 29 commits since 2026-06-18, 12 npm releases in about three months with snapshot format changes (0.12.0 snapshots cannot be read by 0.11.0), and much of the work driven by coding agents (codex.md, TODO.md).

## How it is fast

Indexing, BM25 scoring and prefix/fuzzy expansion run in Rust: fuzzy matching walks the radix tree with Myers' bit-parallel Levenshtein algorithm (one 64-bit word for query terms up to 64 UTF-16 units, banded DP matrix beyond), per-query accumulation uses a dense scratch buffer with FxHash maps, and LLVM autovectorizes the scoring loops with wasm simd128 (about 5% per .cargo/config.toml). The JS-Wasm boundary is kept thin: results leave as a Float64Array of scores plus short ids and interned terms, and search() builds MiniSearch-shaped objects in one JavaScript loop. Prefix and fuzzy expansions are memoized per query term until the next mutation, which pays off for search-as-you-type. Snapshots are delta+varint binary with the radix tree stored node by node, so loadBytes is one validated pass with no tree rebuild.

## Compared with alternatives

No other client-side ranked full-text search engine is catalogued in this category; DuckDB-Wasm is the nearest data tool but answers SQL over tables with a much larger download, so pick this one when you need MiniSearch-compatible BM25 prefix/fuzzy search and auto-suggest.

## Integration

| | |
|---|---|
| **Form** | module (npm package: ESM, CommonJS and browser-global builds plus a .wasm file) |
| **Dependencies** | none at runtime (MiniSearch 7.2.0 is bundled for the fallback engine); building from source needs Rust 1.96.0, wasm-pack 0.15.0, Node and esbuild |
| **Minimum toolchain** | Node &gt;= 18 (package engines field); a WebAssembly runtime with SIMD (simd128); source build: Rust 1.96.0 and wasm-pack 0.15.0 |
| **Platforms** | Node (Wasm compiled on import) and browsers or module Workers after await init(); any CPU whose JavaScript engine supports Wasm SIMD |
| **Thread safety** | not documented; each index is a single-threaded Wasm instance (Rust Rc/RefCell state), so keep one index per JavaScript realm or worker; searching or mutating it from inside boostDocument throws |
| **Drop-in for the baseline** | partial — same import, documented API, callbacks, rankings and toJSON format as MiniSearch 7.2.0, but browsers must await init() for any speedup, a few inputs transfer the index to the bundled JavaScript engine, binary snapshots are a separate format, and some loose option coercions throw |

## Gotchas

- Harness note: the headline 'warm' rows repeat the same 38 queries on one index (a verification pass, 2 warm-ups, 9 rounds), so the Wasm engine serves prefix/fuzzy expansions from its memo (ExpansionCache in src/mini_search.rs) while MiniSearch re-walks its tree every time. The fresh-index 'first batch' rows (search() 2.09x, searchJoined 4.16x, searchRaw 8.85x) show the memo adds only 5-15% on this 707-word synthetic vocabulary, but the source comment says fuzzy traversal is about 86% of query cost on the real jobboard corpus, so the older README figures (searchJoined 11x, searchRaw 23x) are memo-dominated; the README itself puts cold first-run queries at 2-3x. autoSuggest (7.5x) is measured warm only.
- Without await init() in a browser, every index runs in JavaScript mode with no warning in normal use; check index.executionMode. A transfer to JavaScript is permanent and can block while a large index is converted.
- searchJoined/searchRaw encode ids as JSON and terms with space/newline separators: object ids, ids that do not survive JSON, or terms containing those delimiters need full search(); cache docIdTable() with idTableVersion and resolve raw results before the next mutation.
- The 0.12.0 benchmark ran on git HEAD 4a89964 plus uncommitted changes (committed later as 4aac30c), and the native loadJSONAsync was changed afterwards (0.60x in the run, re-measured 0.98x).

## Known shortcomings

- Run on an uncommitted tree (committed the same day as 4aac30c); the searchRaw/toBytes rows compare different calls; synthetic corpus; 4 stars. Toolchain pinned (Rust 1.96.0, wasm-pack 0.15.0, opt-level 3, LTO, +simd128, Ryzen 9 3900X) and results checked against MiniSearch before timing.
- Enricher: the 'warm' rows rerun the same 38 queries on one index, so the Wasm side reads prefix and fuzzy expansions from its memo (ExpansionCache in src/mini_search.rs) while MiniSearch re-walks its tree every time; the fresh-index 'first batch' rows (2.09x/4.16x/8.85x) show the memo adds only 5-15% on the 707-word synthetic vocabulary, but the source says the fuzzy walk is about 86% of query cost on the real jobboard corpus, so the older README 11x/23x figures are memo-dominated (README itself says cold 2-3x); autoSuggest 7.5x measured warm only; public history starts 2026-06-18 (npm 0.1.0 2026-06-19); 826 KB Wasm, 13.8 ms import.

## Caveats and trade-offs

First-party benchmark on one machine with a synthetic corpus. The report says the run used git HEAD 4a89964 plus uncommitted changes; the 0.12.0 code was committed later the same day (4aac30c), and the async loader was changed after the run (re-measured 0.98x vs MiniSearch, the run itself shows loadJSONAsync at 0.60x). Several headline rows are not like-for-like calls: searchJoined/searchRaw are compared with MiniSearch search(), loadBytes/toBytes with loadJSON/JSON.stringify (binary format vs JSON). Cold module import is slower (13.8 ms vs 3.7 ms), the package is 1.4 MB unpacked, and in browsers MiniSearch.init() must be awaited or indexes run on the bundled JavaScript engine at no gain. Older README sections (11x/23x search) come from an external jobboard script that is not in the repo and predate the compatibility facade. Very small project (4 stars, about 3 weeks of public history). [retier] Warm rows served from the Wasm-side ExpansionCache memo while MiniSearch re-walks its tree; 707-word synthetic vocabulary; 826 KB Wasm, 13.8 ms import; public history from 2026-06-18

MiniSearch-compatible API and BM25 rankings; callback-based options (filter, boostDocument, processTerm) run in JavaScript for some paths; compact binary snapshot format 7.5x smaller than JSON.

## Maintenance

Active and MIT-licensed (12 npm releases from 2026-06-19 to 2026-09-26, last commit 2026-09-26, v0.12.0 tagged) but a one-person, 4-star project whose public history starts 2026-06-18, not about three weeks before verification; usable as a drop-in today if you pin the version and keep MiniSearch's JSON as the persisted format so you can switch back.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: the README table and differential/results/2026-09-27-0.12.0-vs-original.md come from the public harness differential/bench_public.mjs (corpus from differential/gen_corpus.mjs, npm run bench:public) against pinned MiniSearch 7.2.0, with the CPU (AMD Ryzen 9 3900X), Node v24.21.0, the pinned toolchain (rust-toolchain.toml Rust 1.96.0, wasm-pack 0.15.0) and release flags (Cargo.toml opt-level 3, lto, codegen-units 1; .cargo/config.toml +simd128) all public. The harness checks result parity (934,016 rows, max relative score difference 0) before timing and uses paired alternating rounds with GC outside timed regions.
- **Verifier notes:** All claimed_speedup figures match the README table and the 2026-09-27 report (search 2.20x, stored fields 3.0x, autoSuggest 7.48x, addAll 3.25x, loadJSON 1.83x, loadBytes 10.46x, toBytes 65.38x, searchRaw 9.92x vs search()). License MIT (LICENSE.txt, keeps MiniSearch's copyright), last commit 2026-09-26, not a fork. Shortcomings for the record: uncommitted-tree run, compact-API rows compare different calls, synthetic corpus, tiny project.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-87 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/differential/results/2026-09-27-0.12.0-vs-original.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/differential/bench_public.mjs>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/CHANGELOG.md>
  - <https://github.com/epoyraz/minisearch-wasm>
  - <https://github.com/epoyraz/minisearch-wasm/commits>
- **Sources the enricher read:**
  - <https://github.com/epoyraz/minisearch-wasm>
  - <https://github.com/epoyraz/minisearch-wasm/tree/main/src>
  - <https://github.com/epoyraz/minisearch-wasm/commits/main>
  - <https://github.com/epoyraz/minisearch-wasm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/differential/bench_public.mjs>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/differential/gen_corpus.mjs>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/differential/results/2026-09-27-0.12.0-vs-original.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/COMPATIBILITY.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/src/mini_search.rs>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/src/searchable_map.rs>
  - <https://raw.githubusercontent.com/epoyraz/minisearch-wasm/HEAD/src/lib.rs>
  - <https://registry.npmjs.org/minisearch-wasm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/epoyraz/minisearch-wasm`) · [data/wave13/enrich/raw/github_com_epoyraz_minisearch_wasm.json](../../../data/wave13/enrich/raw/github_com_epoyraz_minisearch_wasm.json) (enrichment confidence 0.75)

</details>
