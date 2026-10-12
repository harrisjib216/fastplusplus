# Loro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust compiled to WebAssembly with JavaScript bindings` · `MIT` · 🟢 active

> Rust CRDT library compiled to WebAssembly; replays a real 260k-op editing trace about 1.85x faster than Yjs 13.6.

| | |
|---|---|
| **Beats** | Yjs 13.6.11 (pure-JS CRDT library); the same table also lists ywasm 0.9.3 and Automerge 2.1.10 (both wasm) |
| **Claimed result** | dmonad/crdt-benchmarks README, N=6000, i5-8400, Node 20.5.0, loro 0.10.1 vs yjs 13.6.11: B4 apply real-world editing dataset 3,089 ms vs 5,714 ms (1.85x, derived from page data); B4x100 309,689 ms vs 608,908 ms (2.0x, derived from page data); B4 parseTime 13 ms vs 39 ms; B1.1 append N characters 120 ms vs 188 ms; B1.4 79 ms vs 131 ms; B1.5 82 ms vs 154 ms; B3.1 56 ms vs 75 ms. Mixed: Yjs is faster on B2.2 (65 vs 83 ms), B2.3 (85 vs 112 ms), B2.4 (178 vs 208 ms), B3.3 (86 vs 116 ms), B3.4 (72 vs 227 ms) and trivially on B1.6, B1.9 and B2.1; Loro's encodeTime is far higher (B4 77 ms vs 11 ms, B4x100 14,429 ms vs 365 ms, B2.4 233 ms vs 12 ms), its documents are larger (B4 258,228 vs 159,929 bytes) and its bundle is 15x larger (1,052,250 vs 69,124 bytes; 399,276 vs 20,100 gzipped). |
| **Workload** | dmonad/crdt-benchmarks suite on Node 20.5.0: B1 no conflicts, B2 two users with conflicts, B3 many conflicts, B4 replay of a real-world editing trace (259,778 operations) at N=6000. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-8400 @ 2.80GHz x 6, Node 20.5.0 |
| **Adoption** | 6.2k stars (loro); crdt-benchmarks 542 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/loro-dev/loro) · [benchmark](https://github.com/dmonad/crdt-benchmarks) |

## Verdict

In dmonad/crdt-benchmarks, the suite maintained by the Yjs author, on an Intel i5-8400 with Node 20.5.0, the prebuilt loro-crdt 0.10.1 wasm package replayed the 259,778-op real-world editing trace in 3,089 ms vs 5,714 ms for Yjs 13.6.11 (1.85x), the 100x replay in 309,689 vs 608,908 ms (2.0x), and parsed its snapshot in 13 vs 39 ms. Yjs won encode time, document size, bundle size and most concurrent-conflict workloads, and all numbers come from single runs of a 2024 table.

## Use it when

- Long single-writer editing histories applied op by op: the B4 trace (259,778 single-character inserts and deletes) ran in 3,089 ms vs Yjs 5,714 ms on an i5-8400 with Node 20.5.0.
- Apps that reload documents from a stored snapshot often and care about load time (B4 parseTime 13 ms vs 39 ms; B4x100 parseTime 1,304 ms vs 2,622 ms).
- Data models beyond text, list and map: movable trees and lists, rich text, time travel and version control are built in.
- Stacks that share one CRDT core across Rust, JavaScript/WebAssembly and Swift.

## Skip it when

- Tight bundle budgets: 1,052,250 bytes (399,276 gzipped) for loro 0.10.1 vs 69,124 (20,100) for Yjs, and 2,919,363 bytes for 1.0.0-beta.2 in Loro's own fork of the benchmark.
- Workloads dominated by concurrent conflicting edits or frequent full encodes: Yjs is faster on B2.2-B2.4, B3.3 and B3.4, and B4x100 encodeTime is 14,429 ms vs 365 ms.
- Bandwidth-sensitive per-keystroke sync: average update size is 109 bytes vs 27 for Yjs on B1.1.
- Existing Yjs deployments: different API and wire format, so moving over means migrating documents and code.
- Very large documents in the browser: wasm32 caps memory at 4 GiB, and issue #1092 (loro-crdt 1.15.1) showed container-by-container reads retaining about 4 KB per container until a trap, fixed by PR #1093 on 2026-09-04.

## How it is fast

The core is Rust compiled to wasm32: the text CRDT is Fugue, merging adapts the Event Graph Walker (Eg-walker) from diamond-types so concurrent ranges are replayed instead of keeping per-character CRDT metadata live, and operations are run-length encoded and held in an in-tree generic B-tree. Encoding is columnar (serde_columnar, after Automerge), and the snapshot format stores the operation log plus the encoded in-memory state, so loading skips replay; that is why B4 parseTime is 13 ms against Yjs's 39 ms while encodeTime and document size go the other way.

## Compared with alternatives

Pick Loro over ywasm (y-crdt) when long editing traces or snapshot loading dominate (B4 3,089 ms vs 28,675 ms) or you need movable trees, rich text or history, and over Automerge 2.x when load time matters (B4 parseTime 13 ms vs 1,805 ms) and you accept larger documents (258,228 vs 129,116 bytes). For text-only editing, compare diamond-types, the Eg-walker reference implementation whose algorithm Loro adapts.

## Integration

| | |
|---|---|
| **Form** | module (npm loro-crdt, wasm plus JS bindings); crate (loro) for Rust |
| **Dependencies** | none at runtime for the npm package (self-contained wasm); the Rust crate pulls serde_columnar, rustc-hash, smallvec, xxhash-rust and other crates.io dependencies |
| **Minimum toolchain** | Rust stable (rust-toolchain file; no rust-version declared); any JS runtime with WebAssembly (Node, browsers, Deno and Bun are in the package test script) |
| **Platforms** | any WebAssembly host plus native Rust targets and Swift; other languages via loro-ffi |
| **Thread safety** | Rust LoroDoc is Send but not built for shared concurrent use: internal try_lock().unwrap() panics on contention and the maintainer says to add an outer lock (issue #685, lock-hierarchy check added in PR #688); JS use is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the source benchmark: in B1-B3 of dmonad/crdt-benchmarks the parseTime timer wraps getMemUsed() and logMemoryUsed(), each of which calls global.gc() (the suite runs node --expose-gc), so those rows include two forced full GCs whose cost grows with the JS heap; wasm libraries keep document state in linear memory that V8 does not trace, which likely biases B1-B3 parseTime against pure-JS Yjs (B1.2's 6 KB document takes 27-34 ms to parse in Yjs, ywasm and Loro alike, consistent with a GC-dominated floor). B4 parseTime is timed outside the GC calls, but every figure is a single perf.now() run rounded to milliseconds, and memUsed ignores wasm memory, so Loro's 0 B rows mean nothing.
- The table is stale: it measured loro-crdt 0.10.1 (the harness pins ^0.10.1 and calls the pre-1.0 Loro, exportSnapshot and exportFrom APIs). Loro's own fork (zxch3n/crdt-benchmarks, MacBook Pro M1, loro 1.0.0-beta.2 vs Yjs 13.6.15 with gc disabled) shows B4 at 2,271 vs 2,616 ms, only about 1.15x (derived from page data), and says the 1.0 encoding is slower than the pre-1.0 one; the current release is 1.16.4.
- Loro keeps the full operation history: in dmonad's table B3.3 (overwriting map string values) gives a 7,798,572-byte document vs 38,357 for Yjs, which garbage-collects overwritten values; shallow snapshots are the documented way to trim history.
- Open data-loss bugs remain around LoroTree and undo/redo (#1055 undo after import deletes a pre-existing node ID; #938 redo loses text when a tree node is recreated), and #1117 reports a stack overflow in fork_at/checkout after concurrent tree moves.

## Known shortcomings

- crdt-benchmarks loro column verified but the table is stale (last commit 2024-02-12, loro 0.10.1); Yjs wins B2.2-B2.4, B3.3, B3.4, encode time, doc size and bundle size (15x); snapshot mode favours parseTime.
- Harness flaw in dmonad/crdt-benchmarks: the B1-B3 parseTime timer wraps getMemUsed and logMemoryUsed, i.e. two forced global.gc() calls, which likely biases those rows against pure-JS Yjs; B4 parseTime is clean. All rows are single runs. Stale: the table measured 0.10.1 while the current release is 1.16.4; Loro's own fork (M1, 1.0.0-beta.2, Yjs gc:false) shows B4 at only 2,271 vs 2,616 ms (about 1.15x); bundle 2.9 MB. Open LoroTree undo data-loss issues #1055 and #938; #1092 (4 GiB wasm trap) fixed by PR #1093.

## Caveats and trade-offs

Third-party shootout maintained by the Yjs author, so the competitor ran it; wasm compiler flags are not stated. The results table is old: crdt-benchmarks' last commit is 2024-02-12 and the table measures loro 0.10.1 (now 1.x) and ywasm 0.9.3. The harness uses Loro's snapshot export by default (exportSnapshot stores the in-memory state, which lowers parseTime but enlarges docSize and encodeTime) and batches cached remote updates with importUpdateBatch inside a transaction. memUsed excludes wasm runtime memory, so Loro's 0 B rows are not comparable with Yjs's JS heap figures. Gains are workload-specific: Yjs wins most concurrent-conflict text/array workloads (B2.2-B2.4, B3.3, B3.4), all encode times and bundle size. [retier] Third-party shootout maintained by the Yjs author, so the competitor ran it; wasm compiler flags are not stated; every row is a single run. Harness flaw: in B1-B3 the parseTime timer wraps getMemUsed() and logMemoryUsed(), each of which calls global.gc() (node --expose-gc), so those rows include two forced full GCs whose cost grows with the JS heap, which likely biases them against pure-JS Yjs (B1.2's 6 KB document takes 27-34 ms to parse in Yjs, ywasm and Loro alike); the B4 parseTime and apply rows are timed cleanly. The table is stale: it measured loro-crdt 0.10.1 (pre-1.0 APIs: exportSnapshot, exportFrom) and ywasm 0.9.3, while the current release is 1.16.4 and the harness's last commit is 2024-02-12; Loro's own fork (zxch3n/crdt-benchmarks, MacBook Pro M1, loro 1.0.0-beta.2 vs Yjs 13.6.15 with gc disabled) shows B4 at 2,271 vs 2,616 ms, only about 1.15x (derived from page data), and says the 1.0 encoding is slower than the pre-1.0 one. The harness uses Loro's snapshot export by default (lower parseTime, larger docSize and encodeTime) and batches cached remote updates inside a transaction; memUsed excludes wasm runtime memory, so Loro's 0 B rows are not comparable. Gains are workload-specific: Yjs wins most concurrent-conflict text/array workloads (B2.2-B2.4, B3.3, B3.4) and all encode rows; Loro keeps the full operation history (B3.3 document 7,798,572 bytes vs 38,357 for Yjs). Bundle 2.9 MB. Open data-loss bugs around LoroTree undo/redo (#1055, #938) and #1117 (stack overflow in fork_at/checkout); #1092 (4 GiB wasm trap) fixed by PR #1093.

Bundle size 1,052,250 bytes vs Yjs 69,124 bytes; larger update messages (B1.1 average update size 109 vs 27 bytes). Compared with ywasm and Automerge (both wasm) Loro is also faster on B4 (28,675 ms and 14,326 ms).

## Maintenance

Actively maintained (loro-crdt 1.16.4, 2,226 commits, 6.2k stars, MIT), but the independent numbers cover only the 0.10.1 release, so re-run the suite on 1.x before relying on the B4 margin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** dmonad/crdt-benchmarks is the widely used independent CRDT shootout, maintained by the Yjs author (the competitor ran it), with public harness code (benchmarks/loro/factory.js, js-lib) and CPU (i5-8400) and Node 20.5.0 stated; every claimed number is in loro's column of its N=6000 table. Not A because the wasm build flags of the prebuilt loro-crdt 0.10.1 npm package are not stated.
- **Verifier notes:** Numbers verified in loro's column of the crdt-benchmarks README and the harness (benchmarks/loro/package.json pins loro-crdt ^0.10.1, factory.js uses exportSnapshot). Metadata holds (MIT, 6.2k stars, last commit 2026-10-09). Shortcomings to record: table measured 0.10.1 and is stale since 2024-02-12, Yjs wins most conflict workloads, encode time, doc size and bundle size; snapshot mode favors parseTime; memUsed ignores wasm memory.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-13 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/loro-dev/loro>
  - <https://github.com/loro-dev/loro/commits>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/README.md>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/LICENSE>
  - <https://github.com/dmonad/crdt-benchmarks>
  - <https://github.com/dmonad/crdt-benchmarks/commits>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/loro/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/loro/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/package.json>
- **Sources the enricher read:**
  - <https://github.com/loro-dev/loro>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/README.md>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/crates/loro/Cargo.toml>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/crates/loro-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/crates/loro-wasm/package.json>
  - <https://raw.githubusercontent.com/loro-dev/loro/HEAD/crates/loro-wasm/scripts/build.ts>
  - <https://github.com/loro-dev/loro/issues?q=is%3Aissue+slow+OR+performance+OR+memory>
  - <https://github.com/loro-dev/loro/issues/1092>
  - <https://github.com/loro-dev/loro/issues/685>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/loro/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/loro/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/loro/run.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/factory.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/benchmarks/yjs/package.json>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/index.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/utils.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b1.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b2.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b3.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/js-lib/b4.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/bin/measure-bundle.js>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/bin/render-table.js>
  - <https://raw.githubusercontent.com/zxch3n/crdt-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/zxch3n/crdt-benchmarks/HEAD/benchmarks/yjs/factory.js>
  - <https://raw.githubusercontent.com/zxch3n/crdt-benchmarks/HEAD/benchmarks/loro/factory.js>
  - https://loro.dev/docs/performance (DNS failure, not read; WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/loro-dev/loro`) · [data/wave13/enrich/raw/github_com_loro_dev_loro.json](../../../data/wave13/enrich/raw/github_com_loro_dev_loro.json) (enrichment confidence 0.75)

</details>
