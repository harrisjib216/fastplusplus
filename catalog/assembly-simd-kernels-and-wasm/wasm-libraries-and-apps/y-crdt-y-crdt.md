# ywasm (y-crdt, Rust port of Yjs compiled to WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (ywasm WebAssembly/JavaScript bindings)` · `MIT` · 🟢 active

> Yrs, the Rust port of the Yjs CRDT, as a WebAssembly npm module: loads Yjs documents faster but edits slower than Yjs.

| | |
|---|---|
| **Beats** | Yjs 13.6.11 (pure-JavaScript CRDT) |
| **Claimed result** | dmonad/crdt-benchmarks README, N=6000, i5-8400, Node 20.5.0, ywasm 0.9.3 vs yjs 13.6.11. Update time: ywasm faster on B1.1 append (154 vs 188 ms), B1.3 prepend (23 vs 119 ms, 5.2x, derived from page data), B1.4 random inserts (128 vs 131 ms), B1.7 (141 vs 158 ms), B1.8 append numbers (29 vs 148 ms, 5.1x, derived) and B1.10 prepend numbers (28 vs 122 ms, 4.4x, derived); slower on B1.5 (449 vs 154 ms), B1.11 (144 vs 134 ms), B2.2 (365 vs 65 ms), B2.3 (1,014 vs 85 ms), B2.4 (2,786 vs 178 ms), B3.1-B3.4 (278-299 vs 72-86 ms), B4 real-world trace (28,675 vs 5,714 ms, 5.0x slower) and B4x100 (2,829,633 vs 608,908 ms, 4.6x slower). Load time: ywasm parseTime is lower on 20 of 21 rows (B4 16 vs 39 ms, B4x100 1,328 vs 2,622 ms). Bundle 677,667 vs 69,124 bytes. Overall ywasm loses 11 of the 17 non-trivial update-time rows to Yjs, including the real-world trace; its only consistent win is parse/load time. The y-crdt README itself makes no speed claim. |
| **Workload** | dmonad/crdt-benchmarks suite at N=6000 in Node: B1 single-user text/array edits (B1.1-B1.11), B2 two-user concurrent edits, B3 20\*sqrt(N) clients writing a map/array, B4 replay of a real-world editing trace and B4x100; time, parseTime, encodeTime, docSize and bundle size per library. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-8400 CPU @ 2.80GHz x 6 |
| **Compiler and flags** | Node 20.5.0 (node --expose-gc run.js); prebuilt ywasm 0.9.3 npm package, wasm build flags not stated |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/y-crdt/y-crdt) · [benchmark](https://github.com/dmonad/crdt-benchmarks) |

## Verdict

In dmonad/crdt-benchmarks (written by Kevin Jahns, who also co-maintains y-crdt and wrote Yjs), N=6000 on an Intel i5-8400 with Node 20.5.0, ywasm 0.9.3 beat Yjs 13.6.11 on parse time in 20 of 21 rows and on prepend/append microbenchmarks (up to 5.2x), but lost the real-world editing trace 28,675 vs 5,714 ms. Its large B2.2-B2.4 and B3 losses came from a benchmark adapter that ran each ywasm edit or update as its own transaction while Yjs batched, so those rows do not measure the library like-for-like; no table for current ywasm (0.28.0) exists.

## Use it when

- Loading or syncing large stored Yjs documents in JS where parse time dominates: B4x100 (10.5M-character document) parses in 1,328 ms vs 2,622 ms for Yjs, B4 in 16 vs 39 ms.
- Keeping CRDT state off the JS GC heap: Yjs used 327.1 MB of JS heap after B4x100; ywasm's document lives in wasm memory (not measured by the suite, so check total RSS yourself).
- Mixed-language stacks where a Rust (yrs), Python (pycrdt) or other yrs-based backend and JS clients should share one CRDT implementation and identical behaviour.
- Append- or prepend-heavy bulk editing: B1.3 prepend 23 vs 119 ms, B1.8 append numbers 29 vs 148 ms, B1.10 28 vs 122 ms (ywasm 0.9.3).

## Skip it when

- Keystroke-by-keystroke editing with one transaction per edit: on the real-world LaTeX trace ywasm 0.9.3 took 28,675 ms vs 5,714 ms for Yjs (5.0x slower, about 110 vs 22 us per edit, derived from page data) and 4.6x slower on B4x100.
- Bundle-size-sensitive pages: 213,833 bytes gzipped vs 20,100 for Yjs in the table, and the npm package grew from 767,016 bytes unpacked (0.9.3) to 1,226,037 (0.28.0).
- Apps built on the Yjs ecosystem (y-websocket, y-webrtc, editor bindings): the repo's feature matrix lists no WebSocket or WebRTC provider for ywasm and marks its shared-type and document observers as incompatible with Yjs.
- Inserting words at random positions: B1.5 449 vs 154 ms; B1.4 and B1.11 are a wash (128 vs 131 ms, 144 vs 134 ms).

## How it is fast

Yrs implements the same YATA algorithm and block structure as Yjs (yrs README) in Rust, built with LTO, codegen-units=1, opt-level 3 and panic=abort (workspace release profile). Its measurable edge is decoding updates in compiled code and keeping blocks in wasm linear memory rather than as JS objects, which shows up as lower parseTime (20 of 21 rows) and near-zero JS heap use. The cost side is the boundary: in the benchmark harness each edit is three wasm-bindgen calls (writeTransaction, insert, free) plus an update callback that copies a Uint8Array out, against plain method calls in Yjs.

## Compared with alternatives

Pick ywasm over Loro or Automerge when you must stay wire-compatible with existing Yjs peers, servers or stored documents, or share one yrs core with non-JS backends. On raw editing speed in wasm, Loro beat Yjs on the same table's real-world trace (3,089 vs 5,714 ms) while ywasm lost it 5x, and plain Yjs remains the faster choice for per-keystroke editing in JS.

## Integration

| | |
|---|---|
| **Form** | module (npm package ywasm, 0.28.0; the Rust core is the yrs crate) |
| **Dependencies** | yrs, wasm-bindgen, js-sys, serde-wasm-bindgen, base64_light; console_error_panic_hook on by default |
| **Minimum toolchain** | Rust edition 2018 with wasm-bindgen to build; consumers need a JS runtime with WebAssembly (minimum Node or browser version not documented) |
| **Platforms** | any WebAssembly-capable JS runtime (the suite ran Node 20.5.0; it also has Bun and browser scripts) |
| **Thread safety** | One active transaction per document; ywasm's doc comment says further attempts throw an exception. Not designed for sharing across workers. |
| **Drop-in for the baseline** | partial — wire-compatible with Yjs (same update format; docSize identical to Yjs in the table), but a different JS API with explicit transactions, observers that differ from Yjs's, and no Yjs provider integration |

## Gotchas

- Harness flaw behind the published table: the ywasm 0.9.3 column was produced with benchmarks/ywasm/factory.js as of commits 362d241/8203fde (2024-01-24), whose transact() did `this.txn = this.txn || this.ydoc.beginTransaction()` and then free()d and nulled the transaction in finally. A nested insertText therefore committed the outer batch after the first edit, so in B2.2-B2.4 every ywasm edit ran as its own transaction and was applied to the peer one at a time while Yjs sent one batched update per side. The update sizes show it: B2.2 177,007 vs 33,444 bytes (about 6,000 updates of 29.5 bytes, matching B1.4's 29-byte per-edit update) with identical docSize, while the single-op B2.1 matches (6,094 both). In B3 the old applyUpdate called Y.applyUpdateV2(this.ydoc, update) outside the open transaction, so 1,540 updates were integrated one by one against Yjs's single transaction. The 3-16x B2.2-B2.4 and B3 losses are not like-for-like. Commit e03faa1 (2024-02-09, 'fixed ywasm@0.17 benchmark') fixed both paths, but the README table was never re-run.
- The B4 section of the suite's README says all actions replay in a single transaction, but js-lib/b4.js calls insertText/deleteText once per edit with no transact wrapper on both sides. B4 is like-for-like (per-edit transactions with an update listener for both), so the 5x B4 loss stands for 0.9.3. Every row is a single perf.now() sample with no warm-up or repetition (js-lib/utils.js benchmarkTime), and the current ywasm run.js skips B4x100.
- Transactions must be released: ywasm transactions auto-commit only when free()d, and a document allows one active transaction, so a leaked transaction blocks later edits. Text indices are UTF-16 code units (YDoc sets OffsetKind::Utf16), which matches JS strings but not the byte offsets of other yrs bindings.
- Open core issues: #233 'Unsound Unsafe Implementation for BlockPtr and BranchPtr' (open since 2022-12-28); #496 reports a slowdown from the RwLock added for multi-threading in single-threaded use (open; the maintainer said B4 showed no serious change); #516 is a panic on out-of-bounds range removal through yffi.

## Known shortcomings

- crdt-benchmarks author Kevin Jahns also maintains y-crdt, so the suite is not independent for ywasm (tier C); slower than Yjs on 11 of 17 update-time rows including the real-world trace B4 (28,675 vs 5,714 ms), winning only prepend/append microbenchmarks and parseTime; table stale (ywasm 0.9.3, harness now pins ^0.17.4).
- Harness flaw behind the published table: the ywasm 0.9.3 column came from crdt-benchmarks factory.js at 362d241/8203fde (2024-01-24), whose transact() freed the outer transaction after the first nested operation, so B2.2-B2.4 ran every ywasm edit as its own transaction plus a peer apply while Yjs batched (B2.2 updateSize 177,007 vs 33,444 bytes, identical docSize, single-op B2.1 equal), and B3's old applyUpdate bypassed the open transaction so 1,540 updates were integrated one by one; the 3-16x B2/B3 losses are therefore not like-for-like. Fixed in e03faa1 (2024-02-09) but the table was never re-run. The 5x B4 loss stands (per-edit on both sides). One perf.now() sample per row; issue #233 (unsound unsafe) open.

## Caveats and trade-offs

Mixed result, not an overall win: ywasm is about 5x slower than Yjs on the real-world trace (B4, B4x100), about 16x slower on concurrent insert/delete (B2.4), 3-12x slower on the other concurrent rows (B2.2, B2.3, B3.1-B3.4), and its bundle is about 10x larger; it wins prepend/append microbenchmarks and parse/load time. The suite is written by Kevin Jahns, author of Yjs and a listed maintainer and copyright holder of y-crdt, so it is not independent of either side. The table is stale: crdt-benchmarks' last commit is 2024-02-12, its results table measured ywasm 0.9.3 while the harness now pins ywasm ^0.17.4 and y-crdt has since released v0.28, so current ywasm may differ in either direction. memUsed shows 0 B for wasm because it excludes wasm memory. ywasm is the wasm/JS binding of the yrs Rust core in the same repo. [retier] Mixed result, not an overall win: ywasm is about 5x slower than Yjs on the real-world trace (B4, B4x100; per-edit on both sides, so this loss stands), and its bundle is about 10x larger; it wins prepend/append microbenchmarks and parse/load time. The 3-16x losses on B2.2-B2.4 and B3 are not like-for-like: the ywasm 0.9.3 column came from benchmarks/ywasm/factory.js at 362d241/8203fde (2024-01-24), whose transact() freed the outer transaction after the first nested operation, so every ywasm edit ran as its own transaction plus a peer apply while Yjs batched (B2.2 updateSize 177,007 vs 33,444 bytes), and the old applyUpdate bypassed the open transaction so B3 integrated 1,540 updates one by one; fixed in e03faa1 (2024-02-09), table never re-run. The suite is written by Kevin Jahns, author of Yjs and a listed y-crdt maintainer, so it is not independent of either side. One perf.now() sample per row. The table is stale (ywasm 0.9.3 vs current 0.28.0); issue #233 (unsound unsafe) open.

Bundle 677,667 bytes (213,833 gzipped) versus Yjs 69,124 (20,100); wasm memory not counted in memUsed; JS/wasm boundary costs dominate in event-heavy workloads.

## Maintenance

Actively maintained (last commit 2026-09-30, v0.28.0 released 2026-09-17 on npm; crates.io stops at ywasm 0.19.2), MIT, 2.2k stars; usable today, but the only published comparison is a 2024 run of ywasm 0.9.3 through a since-fixed adapter, so measure your own workload before switching from Yjs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** Every claimed number is in the ywasm column of the dmonad/crdt-benchmarks README N=6000 table (i5-8400, Node 20.5.0, harness benchmarks/ywasm/factory.js plus js-lib public), but the suite's author Kevin Jahns is also a listed maintainer and MIT copyright holder of y-crdt (and the author of the Yjs baseline), so for ywasm these are first-party numbers, not an independent suite. Not A because the prebuilt ywasm 0.9.3 npm package's wasm build flags are not stated.
- **Verifier notes:** Numbers verified row by row in the ywasm column; the record's numbers were right but it omitted most of the losing rows (B1.5, B2.2, B2.3, B3.x) and the parseTime wins, now corrected. Downgraded B to C because the benchmark author co-maintains y-crdt (this differs from the Loro entry, which was kept at B from the same table because Loro is unrelated to the suite author). Shortcomings to record: slower than Yjs on the real-world trace and on all concurrent workloads, stale 0.9.3 table, 10x larger bundle, no wasm build flags. Metadata holds: MIT, 2.2k stars, last commit 2026-09-30, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/y-crdt/y-crdt>
  - <https://github.com/y-crdt/y-crdt/commits>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/README.md>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/LICENSE>
  - <https://github.com/dmonad/crdt-benchmarks/commits>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/ywasm/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/ywasm/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/package.json>
- **Sources the enricher read:**
  - <https://github.com/y-crdt/y-crdt>
  - <https://github.com/y-crdt/y-crdt/commits/main>
  - <https://github.com/y-crdt/y-crdt/tree/main/yrs>
  - <https://github.com/y-crdt/y-crdt/tree/main/yrs/benches>
  - <https://github.com/y-crdt/y-crdt/tree/main/ywasm/src>
  - <https://github.com/y-crdt/y-crdt/issues?q=is%3Aissue+performance>
  - <https://github.com/y-crdt/y-crdt/issues/12>
  - <https://github.com/y-crdt/y-crdt/issues/496>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/README.md>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/README.md>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/src/doc.rs>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/src/transaction.rs>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/src/text.rs>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/ywasm/src/lib.rs>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/yrs/README.md>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/yrs/Cargo.toml>
  - <https://raw.githubusercontent.com/y-crdt/y-crdt/HEAD/yrs/benches/benches.rs>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/ywasm/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/ywasm/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/ywasm/run.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/index.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/utils.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b1.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b2.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b3.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b4.js>
  - <https://github.com/dmonad/crdt-benchmarks/commits/main>
  - <https://github.com/dmonad/crdt-benchmarks/commits/main/benchmarks/ywasm/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/362d2415be2dc51c820f006ab802b4c179ed84de/benchmarks/ywasm/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/362d2415be2dc51c820f006ab802b4c179ed84de/benchmarks/ywasm/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/362d2415be2dc51c820f006ab802b4c179ed84de/README.md>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/8203fde042bddb486f0387957cafb1dd94eb3dac/benchmarks/ywasm/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/8203fde042bddb486f0387957cafb1dd94eb3dac/benchmarks/ywasm/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/8203fde042bddb486f0387957cafb1dd94eb3dac/README.md>
  - <https://crates.io/api/v1/crates/ywasm>
  - <https://registry.npmjs.org/ywasm/latest>
  - <https://registry.npmjs.org/ywasm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/y-crdt/y-crdt`) · [data/wave13/enrich/raw/github_com_y_crdt_y_crdt.json](../../../data/wave13/enrich/raw/github_com_y_crdt_y_crdt.json) (enrichment confidence 0.6)

</details>
