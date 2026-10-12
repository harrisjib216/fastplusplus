# Automerge (Rust core compiled to WebAssembly, 2.x)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust (WebAssembly build) with JavaScript bindings; also a C API` · `MIT` · 🟢 active

> JSON-document CRDT, Rust core compiled to WebAssembly; much faster and smaller than pure-JS Automerge 0.14, slower than Yjs and Loro.

| | |
|---|---|
| **Beats** | Automerge 0.14.1, the earlier pure-JavaScript implementation (Yjs 13.6.11 shown as the JS reference) |
| **Claimed result** | Cross-run only (two separate tables of the crdt-benchmarks README, different runs, Yjs 13.3.0 vs 13.6.11): B1.1 append 6000 chars 365 ms (Automerge 2.1.10, wasm) vs 2460 ms (Automerge 0.14.1, JS) = 6.7x (derived from page data); B1.3 prepend 307 ms vs 83,488 ms = 272x (derived from page data); B4 editing trace 14,326 ms vs 489,104 ms = 34x (derived from page data). Normalised to Yjs in each run, Automerge went from 8.1x slower to 1.9x slower on B1.1 and from 298x slower to 2.6x slower on B1.3 (derived from page data). Same run: Automerge 2.1.10 is slower than Yjs on B1.1 (365 vs 188 ms), B1.3 (307 vs 119 ms) and B4 (14,326 vs 5,714 ms), and slower than Loro (120, 81, 3,089 ms). |
| **Workload** | crdt-benchmarks: B1.x text editing sequences of N=6000 operations in Node, e.g. append N characters (B1.1) and prepend N characters (B1.3), plus the real-world editing trace B4. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-8400 CPU @ 2.80GHz x 6 (current table); older table's machine not stated |
| **Compiler and flags** | Node 20.5.0; wasm build flags not stated |
| **Adoption** | 6.7k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/automerge/automerge) · [benchmark](https://github.com/dmonad/crdt-benchmarks) |

## Verdict

dmonad/crdt-benchmarks (N=6000, Node) shows Automerge 2.1.10, the Rust core compiled to wasm, at 365 ms (B1.1 append), 307 ms (B1.3 prepend) and 14,326 ms (B4 real editing trace) on an i5-8400 with Node 20.5.0, against 2,460, 83,488 and 489,104 ms for pure-JS Automerge 0.14.1 in an older table with no machine or Node version stated, so the 6.7x to 272x speedups are cross-run (tier D). In the same run Automerge 2.1.10 is slower than Yjs 13.6.11 and Loro 0.10.1 on all three rows; the robust cross-version gain is document size (B4 84 MB to 129 KB).

## Use it when

- Local-first JavaScript or TypeScript apps that need a general JSON document model (maps, lists, text, counters) with merge, history and a ready-made sync protocol, rather than only a text CRDT.
- Projects still on Automerge 0.14 or 1.0-era JS: the old implementation is the baseline that collapses on long histories (crdt-benchmarks B4: 489,104 ms and an 83,966,886-byte document; automerge-perf: old Automerge.Text ran out of memory after about 235,000 operations at Node's \~1.4 GB default heap).
- Storage- or bandwidth-sensitive persistence of whole documents: in the 2024 suite run its saved documents were the smallest of the four libraries (B4 129,116 bytes vs Yjs 159,929 and Loro 258,228; B1.1 3,992 vs 6,031).
- Polyglot stacks that want one binary format across Rust servers, C/FFI clients and browser or Node front ends (Node, browsers via a bundler or the base64 entry point, Deno, Cloudflare workerd).

## Skip it when

- Keystroke-rate text editing where per-op latency matters most: in the same run Automerge 2.1.10 trailed Yjs (pure JS) and Loro (wasm) on every quoted text row (B1.1 365 vs 188 and 120 ms; B1.3 307 vs 119 and 81 ms; B4 14,326 vs 5,714 and 3,089 ms).
- Many clients writing concurrently to one map or array: B3.1-B3.4 took 1,632-2,780 ms against 56-299 ms for Yjs, ywasm and Loro, with larger update messages (B3.1 283,296 bytes vs 49,169 for Yjs).
- Fast cold load of large documents on the main thread: B4 parseTime 1,805 ms vs 13-39 ms for the others; open issue #1244 reports a large doc blocking the main thread for 10+ seconds, and a community run in #1201 (Automerge 3.2.1 wasm) loads a 200,000-update snapshot in 535 ms vs 24 ms for Yjs.
- Bundle-size-sensitive pages: the measured wasm is 1,737,571 bytes (604,118 gzipped) vs Yjs's 69,124 (20,100), and the 3.5.0 npm package unpacks to about 47.5 MB across its many entry points.
- Native Rust write-heavy services on recent crates without benchmarking first: open issue #1387 shows map-insert throughput falling from 158,621 to 9,742 files/s between crate 0.6.1 and 0.11.0 (maintainer re-run), and #1591 shows applying one remote keystroke growing linearly with text length since 0.7 (13.38 ms vs 0.006 ms at 124,018 characters).

## How it is fast

The pure-JS 0.14 line kept every operation as JS objects and saved history as JSON, which is why its B4 document was 84 MB and its heap 1.1 GB. The Rust core stores operations in the columnar, run-length and delta encoded format of the Automerge binary spec (hexane crate: Column, PrefixColumn and DeltaColumn types that support splice directly on compressed bytes in O(log n + affected bytes)), and since Automerge 3 the in-memory op set (op_set2) uses that columnar form too, which the project credits with a 10x-plus memory cut (blog, snippet only). List and text positions are resolved through hexane's PrefixColumn, which keeps per-slab running sums in a B-tree for O(log n) offset queries; compression uses flate2 with the pure-Rust zlib-rs backend, and the release profile builds with LTO and one codegen unit.

## Compared with alternatives

Loro is faster on every text and map row of the same 2024 run and also ships as wasm, diamond-types merges text traces faster in the Eg-walker paper, and Yjs or ywasm have far smaller bundles; pick Automerge when you need its full JSON document model with history, sync protocol and C/Rust/JS bindings on one documented binary format, and when the smallest saved documents matter more than per-keystroke speed.

## Integration

| | |
|---|---|
| **Form** | npm module (@automerge/automerge over @automerge/automerge-wasm), crate (automerge), C library (automerge-c) |
| **Dependencies** | JS: none beyond the bundled wasm; browsers need a bundler with async WebAssembly (webpack asyncWebAssembly) or the base64 entry point. Rust: hexane, flate2 (zlib-rs), sha2, leb128, rustc-hash, smol_str, tinyvec, unicode-segmentation, rand, tracing and others |
| **Minimum toolchain** | Rust 1.90 (rust-version in Cargo.toml); the wasm build also needs nightly with rust-src (std rebuilt with panic=unwind so panics surface as JS exceptions), wasm-bindgen-cli and wasm-opt; automerge-c needs cmake, cmocka, doxygen and ninja |
| **Platforms** | any Rust target; wasm32 for Node, browsers, Deno and workerd (32-bit wasm memory cap; Memory64 support is open issue #1107) |
| **Thread safety** | not documented for the wasm build; JS documents are immutable snapshots updated by change(), and wasm-side allocations are freed by FinalizationRegistry or must be freed explicitly on platforms without it |
| **Drop-in for the baseline** | partial: same project, data model and change/merge style as Automerge 0.14, but the binary format, text API and package layout changed, so code and stored documents need migration |

## Gotchas

- Harness note: the only speed evidence is cross-run. The 2.1.10 column (i5-8400, Node 20.5.0, Jan 2024) and the 0.14.1 column (older table, machine and Node not stated) come from different runs; Yjs itself moved from 303 to 188 ms on B1.1 between them, so ratios such as 272x on B1.3 mix version and machine effects. Only machine-independent columns compare cleanly: B4 docSize 83,966,886 vs 129,116 bytes (about 650x smaller, derived from page data) and B1.1 docSize 2,161,851 vs 3,992 bytes.
- Harness note: the suite's memUsed is process.memoryUsage().heapUsed after a forced GC, clamped at zero, so wasm linear memory is invisible and Automerge's '0 B' rows say nothing. The README's B4 section says all actions are replayed in a single transaction because Automerge ran out of memory, but js-lib/b4.js calls insertText/deleteText per edit, each wrapped in automerge.change plus saveIncremental, and the results note says the opposite; and the table (ywasm 0.9.3) predates the suite's last harness commits of Feb 12, 2024 ('ensure that the benchmarks also extract content', ywasm bumped to 0.17), so it was not regenerated against the HEAD code.
- The measured 2.1.10 is not what you install today: the Automerge team wrote the suite's adapter (alexjg PR #22, the 'next' API; B3.3 stores RawString instead of text CRDTs to avoid memory blow-up), Automerge 3 rewrote the in-memory representation, and the Rust core has open write-path regressions (#1387, #1591), so 2024 timings do not predict 3.5.0 in either direction.
- saveIncremental() chunks are less compressed than a full save() (automerge-wasm README), so append-only logs should be compacted with periodic save(); historical queries at old heads are not indexed and are slower unless you forkAt().

## Known shortcomings

- The speedup over the 0.14.1 JavaScript version exists only across two crdt-benchmarks tables (cross-run comparison, tier D); in the same run Automerge is slower than Yjs and Loro on B1.1, B1.3 and B4; the measured 2.1.10 predates Automerge 3.
- Enricher: cross-run only; the only machine-independent comparison is B4 docSize (83,966,886 vs 129,116 bytes, derived); memUsed reads JS heapUsed clamped at 0 so wasm memory is invisible; the suite README says B4 runs as one transaction while b4.js runs one change per edit; the table (ywasm 0.9.3) predates the last harness commits (2024-02-12); the measured 2.1.10 is stale with open Rust-core regressions (#1387 write throughput 158,621 to 9,742 files/s, #1591 remote apply linear in text length since 0.7).

## Caveats and trade-offs

Cross-run comparison: the older table (Automerge 0.14.1, Yjs 13.3.0, delta-crdts 0.10.3) states no machine or Node version, while the current table was run on an Intel Core i5-8400 with Node 20.5.0; the baseline is the project's own predecessor. Within one run Automerge 2.1.10 (Rust compiled to wasm) is slower than pure-JS Yjs and than Loro on the quoted B1.1, B1.3 and B4 rows, so it is not faster than the leading JS equivalent. The suite is maintained by the Yjs author; memUsed excludes wasm memory; the README notes Automerge does B4 in about 1 s when all edits go in a single change() transaction. The benchmarked 2.1.10 is outdated: the repository README now describes Automerge 3 (about 10x lower memory use), which the suite does not measure. The repo's own edit-trace harness (rust/edit-trace) commits no numbers.

Bundle 1,737,571 bytes (604,118 gzipped) versus Yjs 69,124 (20,100); smaller documents than Yjs (3,992 vs 6,031 bytes on B1.1); suite's memUsed does not include wasm runtime memory.

## Maintenance

Actively maintained by Ink & Switch staff (MIT, 6.7k stars, last commit 2026-10-09, @automerge/automerge 3.5.0 and crate 0.12.0 released 2026-09-16, about 694k crate downloads), production-usable from JS; the README calls the Rust API low level and not well documented, and the only public cross-library numbers date from January 2024 (issue #1201 asks for new ones).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now D.
- **Tier reason:** dmonad/crdt-benchmarks is a well-known third-party suite, but it never measures Automerge 2.x against the old JS Automerge in one run: the 6.7x and 272x ratios come from the current table (i5-8400, Node 20.5.0, Automerge 2.1.10) and an 'older results' table with no machine or Node version, so this is a cross-run comparison, which goes to D under the PostgreSQL/MySQL/ODB precedent. In the same-run table the wasm Automerge is slower than the pure-JS Yjs (and Loro) on every quoted row, so no valid same-run win over a JS equivalent exists.
- **Verifier notes:** Numbers quoted in the record all appear in dmonad/crdt-benchmarks README (365 vs 2460 ms, 307 vs 83,488 ms, 14,326 vs 5,714 ms), but only across two tables from different runs; one WebSearch found the Automerge 2.0 announcement claims large gains without quantifying them in the snippet, and the repo commits no comparison numbers. Metadata confirmed: MIT, 6.7k stars, 273 forks, 1,731 commits, last commit 2026-10-09, not a fork. Shortcomings: cross-run only, slower than Yjs and Loro in the same run, measured version 2.1.10 predates Automerge 3, suite run by a competitor's author.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/dmonad/crdt-benchmarks>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://github.com/automerge/automerge>
  - <https://github.com/automerge/automerge/commits>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/edit-trace/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge-perf/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge/Cargo.toml>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge/src/lib.rs>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge/src/op_set2.rs>
  - <https://github.com/automerge/automerge/tree/main/rust/automerge/src>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge-wasm/package.json>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/automerge-wasm/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/hexane/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/hexane/Cargo.toml>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/edit-trace/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/edit-trace/Cargo.toml>
  - <https://github.com/automerge/automerge/tree/main/rust/benchmark-battery>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/benchmark-battery/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/rust/benchmark-battery/Cargo.toml>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/javascript/README.md>
  - <https://raw.githubusercontent.com/automerge/automerge/HEAD/javascript/package.json>
  - <https://github.com/automerge/automerge/issues?q=is%3Aissue%20is%3Aopen%20performance%20OR%20slow%20OR%20memory>
  - <https://github.com/automerge/automerge/issues/1387>
  - <https://github.com/automerge/automerge/issues/1591>
  - <https://github.com/automerge/automerge/issues/1201>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://github.com/dmonad/crdt-benchmarks/tree/main/benchmarks>
  - <https://github.com/dmonad/crdt-benchmarks/commits/main>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/automerge/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/automerge/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/automerge-wasm/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b4.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/utils.js>
  - <https://raw.githubusercontent.com/automerge/automerge-perf/HEAD/README.md>
  - <https://crates.io/api/v1/crates/automerge>
  - <https://registry.npmjs.org/@automerge/automerge>
  - https://automerge.org/blog/automerge-3/ (fetch failed: ENOTFOUND)
  - WebSearch: Automerge 3 memory usage reduction (snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/automerge/automerge`) · [data/wave13/enrich/raw/github_com_automerge_automerge.json](../../../data/wave13/enrich/raw/github_com_automerge_automerge.json) (enrichment confidence 0.8)

</details>
