# diamond-types

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (npm packages diamond-types-node and diamond-types-web via WebAssembly)` · `ISC` · 🟢 active

> Rust Eg-walker text CRDT (wasm npm builds) merging editing histories 22-404x faster than Automerge and mostly faster than Yjs.

| | |
|---|---|
| **Beats** | Automerge v0.5.9 (Rust) and Yjs v13.6.10 (JavaScript on Node.js v22.2.0), per the EuroSys 2025 Eg-walker paper; also the authors' own reference CRDT (Yrs, the Rust port of Yjs, was run but omitted from the paper) |
| **Claimed result** | Native Rust, CPU time to merge a whole editing trace received from a remote replica, means from egwalker-paper results/timings.json (derived from page data): diamond-types 1.77-82.6 ms vs Automerge 485-24,636 ms, i.e. 22x (A2) to 404x (S3); vs Yjs (55-88 ms) 32.5x on S1, 31.8x on S2, 22.3x on S3, 1.5x on C1, 10.0x on A1, 3.2x on A2, but 0.67x on C2 (diamond-types slower, 82.6 vs 55.2 ms). Cached document reload takes 0.012-0.12 ms against CRDT load times equal to their merge times. Paper text: 160,000x faster than OT on trace A2 and 7-10x faster than the authors' reference CRDT on the sequential traces. The README's link to a '5000x faster' blog post and its 'another 10-80x' claim, and the About text 'The world's fastest CRDT', could not be checked (blog unreachable). |
| **Workload** | Merging each of seven real editing traces (S1-S3 sequential, C1-C2 concurrent, A1-A2 asynchronous) into an empty document as if received from a remote replica, plus reloading the saved document; Yjs is timed on Y.applyUpdateV2 of the pre-encoded document, Automerge and Yrs on loading their encoded documents. |
| **Metric** | throughput |
| **Hardware** | Ryzen 7950x, 64 GB RAM, Linux 6.5.0-28 (paper footnote) |
| **Compiler and flags** | rustc 1.78.0 in release mode with -C target-cpu=native, Rust benchmarks pinned to one core (taskset 0x1 nice -10), Criterion.rs; Yjs on Node.js v22.2.0 via smolbench (paper footnote). The artifact README says the current results used Rust 1.80 and Node.js v21, so the two sources disagree on versions. |
| **Adoption** | 1.8k stars |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/josephg/diamond-types) · [benchmark](https://github.com/josephg/egwalker-paper) |

## Verdict

The EuroSys 2025 Eg-walker artifact (Ryzen 7950x, native Rust release build with Criterion pinned to one core, Yjs 13.6 on Node) replayed each full editing trace into an empty document. Diamond-types took 1.77-82.6 ms vs Automerge's Rust load at 485-24,636 ms, which is 22-404x, derived from results/timings.json. Yjs took 55-88 ms, so diamond-types ranged from 32.5x faster on S1 to 0.67x (slower) on C2. Diamond-types' time excludes decoding its own file while the competitors' times include decoding theirs, and the wasm npm builds were never measured.

## Use it when

- Collaborative plain-text editors whose history is mostly sequential or turn-taking. The paper's S1-S3 traces merged in 1.77-3.58 ms vs Automerge 620-1,444 ms and Yjs 57-85 ms.
- Apps that must open big documents instantly and keep steady-state memory to the text itself. Reloading the cached text took 0.012-0.12 ms, versus CRDTs whose load equals a full merge.
- Offline or branch-heavy asynchronous workflows (A1, A2), where it was about 10x and 3.2x faster than Yjs and OT took up to an hour on A2.
- Rust-native code or JS via wasm when you also need index-based (OT-style) positional updates to interoperate with simple peers.

## Skip it when

- Highly concurrent real-time editing. On C1/C2 it took 56.1 and 82.6 ms, slower than Yjs on C2 (55.2 ms), 4.8x and 9.5x slower than Yrs 0.20 in the same artifact, and over a 16 ms frame budget.
- Rich text, JSON/maps, or built-in undo/redo. Master is plain text only, and issues #3 (undo) and #11 (rich text) are open.
- Projects that need a released, stable API. crates.io 1.0.0 (2022-08-25) and npm 1.0.2 (2023-05-15) predate the benchmarked code, v2.0.0 is unreleased (issues #44, #45), and master needs Rust 1.96.
- Ingesting untrusted peer bytes without isolation. OpLog::load_from panicked on malformed input in 1.0.0 (issue #50, open), and master only gained a decode fuzzer and some panic fixes on 2026-07-31.
- Teams wanting an ecosystem of network providers, persistence adapters and editor bindings comparable to Yjs or Automerge.

## How it is fast

It implements the Eg-walker algorithm (Gentle and Kleppmann, EuroSys 2025). Instead of keeping CRDT metadata in memory, it replays the event graph and builds temporary CRDT state only for concurrent sections, then discards it. Critical versions (points where all prior events precede all later ones) let it skip transformation entirely for sequential runs; that fast-forward path is why S1 takes 1.77 ms with it on versus 9.81 ms with it off. Records are run-length encoded and stored in an order-statistic B-tree (range tree) plus an ID-to-leaf B-tree, so position/ID mapping is O(log n). Loading for editing reads a cached copy of the final text rather than the history.

## Compared with alternatives

Pick it over Automerge (Rust core to wasm) when load time, steady-state memory and merge speed on mostly sequential text dominate (22-404x faster merges in the native artifact). Prefer Yjs/ywasm or Loro when you need rich text, JSON types, a mature ecosystem, or mostly concurrent editing, where Yrs was faster than diamond-types in the same artifact.

## Integration

| | |
|---|---|
| **Form** | crate (git master; crates.io 1.0.0 is outdated) or npm packages diamond-types-node / diamond-types-web built with wasm-pack |
| **Dependencies** | smartstring, str_indices, smallvec 2.0.0-alpha, rle (in-repo crate), bumpalo, jumprope, humansize, num_enum, crc, libc; lz4_flex optional (default feature) |
| **Minimum toolchain** | Rust 1.96 for master (Cargo.toml rust-version); the paper used rustc 1.78; wasm-pack for the npm builds |
| **Platforms** | any Rust target including wasm32 (Node and browser packages); the artifact was tested on Linux only |
| **Thread safety** | not documented; a merge or checkout is single-threaded work on one ListOpLog/ListBranch |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the merge ratios. In egwalker-paper tools/diamond-types/crates/bench/src/main.rs, ListOpLog::load_from(&bytes) runs once outside Criterion's b.iter, and only oplog.checkout_tip() is timed. Automerge (AutoCommit::load in tools/paper-benchmarks/src/convert1.rs), Yrs (Update::decode_v2 plus apply_update) and Yjs (Y.applyUpdateV2 in tools/bench-yjs/bench-remote.js) are timed including parsing their serialized documents. DT's own decode time is not reported, so the ratios against CRDTs are overstated by an unknown amount, most on S1-S3 where DT's timed work is only 1.8-3.6 ms.
- The flat Yjs/Yrs times are explained, not a bug. Their inputs are GC-enabled encode_state_as_update_v2 snapshots (yrs Options::default, deleted content dropped, runs merged), and the traces were duplicated to similar sizes (608k-947k keystrokes), so the Yjs 'merge' is a compacted-state load of comparable size per trace. Yrs 0.20.0 (8-13 ms) beats DT on C1, C2 and A2 even with DT's decode excluded.
- Build and version drift. The paper footnote claims -C target-cpu=native, but no RUSTFLAGS or .cargo/config is in the artifact scripts, so a reproduction gets a generic build unless set by hand. The lockfile pins automerge 0.5.11 and yrs 0.20.0 against the paper's Automerge v0.5.9, and the README says results were regenerated with Rust 1.80 and Node v21 against the footnote's 1.78 and v22.2.0.
- The 0.012-0.12 ms 'load' is reading the cached final text into a JumpRope from a temp file (opt_load bench), not loading the event graph. Any merge of concurrent remote edits still has to load and replay from the last critical version. No wasm build was benchmarked anywhere.

## Known shortcomings

- Tier A rests on the EuroSys 2025 Eg-walker artifact (josephg/egwalker-paper, Ryzen 7950X, rustc 1.78.0 -C target-cpu=native) for native Rust only; the wasm npm builds (1.0.2, 2023-05-15) are unmeasured; against Yjs it is 1.5-32x but slower on C2 (82.6 vs 55.2 ms); Yrs is left out of the paper although the artifact's timings.json shows Yrs faster on C1, C2 and A2; the 5000x README claim is unverified (josephg.com blocked).
- Harness asymmetry: the diamond-types bench calls ListOpLog::load_from outside Criterion's b.iter and times only checkout_tip, while Automerge (AutoCommit::load), Yrs (decode_v2 plus apply) and Yjs (applyUpdateV2) timings include decoding their serialized documents, so the ratios are overstated by an unknown amount, most on S1-S3 where DT's timed work is 1.8-3.6 ms. The flat Yjs/Yrs times are GC'd snapshots of traces duplicated to 608k-947k keystrokes, not a bug. -C target-cpu=native is set nowhere in the artifact; the lockfile pins automerge 0.5.11 and yrs 0.20.0 (paper says 0.5.9). load_from panic issue #50 is open; no wasm build was ever benchmarked.

## Caveats and trade-offs

All measured numbers are for the native Rust library; no benchmark of the wasm builds exists, and the npm packages diamond-types-node and diamond-types-web were last published as 1.0.2 on 2023-05-15 (crates.io 1.0.0 on 2022-08-25; the README says the published crate is quite out of date), so the wasm packages predate the benchmarked May-2024 code. Mixed against Yjs: diamond-types is slower on C2 (82.6 vs 55.2 ms) and only 1.5x faster on C1, although the paper text says it is significantly faster than Yjs on C1, C2 and A2. Yrs was omitted from the paper on the grounds that it was slower than Yjs, yet the artifact's committed results/timings.json shows Yrs at 8-13 ms, faster than diamond-types on C1 (4.8x), C2 (9.5x) and A2 (1.8x); Yjs and Yrs times are nearly flat across traces of very different size, which an enricher should check. Diamond-types is also slightly slower than the authors' reference CRDT on C1 and C2. The cached-load advantage comes from storing the final document text, a design difference rather than a like-for-like load. Automerge was measured as its Rust v0.5.9 core, not the JavaScript build. The paper is first-party (diamond-types' author, co-authored with Automerge's creator) but peer-reviewed. The 5000x and 10-80x README figures remain unverified because josephg.com did not resolve. Not part of dmonad/crdt-benchmarks (its README lists Yjs, ywasm, Loro and Automerge only). [retier] All measured numbers are for the native Rust library; no wasm build was ever benchmarked, and the npm packages diamond-types-node and diamond-types-web (1.0.2, 2023-05-15) predate the benchmarked May-2024 code. Harness asymmetry: in egwalker-paper tools/diamond-types/crates/bench/src/main.rs, ListOpLog::load_from runs once outside Criterion's b.iter and only oplog.checkout_tip() is timed, while Automerge (AutoCommit::load), Yrs (Update::decode_v2 plus apply_update) and Yjs (Y.applyUpdateV2) are timed including parsing their serialized documents; DT's own decode time is not reported, so the ratios against the CRDTs are overstated by an unknown amount, most on S1-S3 where DT's timed work is only 1.8-3.6 ms. The flat Yjs/Yrs times are GC-enabled snapshots of traces duplicated to 608k-947k keystrokes, not a bug; Yrs 0.20.0 (8-13 ms) beats DT on C1, C2 and A2 even with DT's decode excluded, and DT is slower than Yjs on C2 (82.6 vs 55.2 ms). Build drift: the paper footnote claims -C target-cpu=native but no RUSTFLAGS or .cargo/config exists in the artifact; the lockfile pins automerge 0.5.11 and yrs 0.20.0 against the paper's 0.5.9; the README says results were regenerated with Rust 1.80 and Node v21. The 0.012-0.12 ms 'load' reads the cached final text from a temp file, not the event graph. load_from panic issue #50 is open.

README marks it WIP; the crates.io package is described as out of date; wasm packages exist for Node and browsers; designed to interoperate with positional updates (operational transform).

## Maintenance

Active (fuzz-driven fixes through 2026-09-02) and ISC-licensed, but still marked WIP: the published crate (1.0.0, 2022) and npm wasm packages (1.0.2, 2023) predate the benchmarked code, v2.0.0 is unreleased, and master requires Rust 1.96.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C: the EuroSys 2025 Eg-walker paper (Gentle and Kleppmann) benchmarks diamond-types against Automerge and Yjs with public artifact code in josephg/egwalker-paper (step2b-benchmarks.sh; DT bench crate merge_norm, tools/paper-benchmarks/src/main.rs for Automerge and Yrs, tools/bench-yjs/bench-remote.js for Yjs; means in results/timings.json), and the paper footnote states Ryzen 7950x, rustc 1.78.0 release with -C target-cpu=native, Node.js v22.2.0. The A tier covers the native Rust library only; nothing measures the wasm npm builds.
- **Retiered** A to C: Enricher: the egwalker-paper bench loads the diamond-types oplog outside Criterion's timed closure and times only checkout_tip, while Automerge, Yrs and Yjs are timed including decoding their documents, so the published ratios are overstated by an unknown amount (asymmetric-harness precedent: TensorFlow DLPerf, LC); the paper's -C target-cpu=native flag appears in no artifact script (flags absent from public sources). A to C.
- **Verifier notes:** Upgraded C to A on the EuroSys 2025 Eg-walker paper artifact (josephg/egwalker-paper), which is reproducible with code, compiler, flags and CPU model, but it measures native Rust only; consider a category override out of wasm-libraries-and-apps or a caveat that the wasm packages (npm 1.0.2, 2023) are unmeasured. Shortcomings to record: slower than Yjs on C2 and than Yrs on C1, C2 and A2 in the artifact's own results; Yrs omitted from the paper; README 5000x claim unverifiable (blog josephg.com unreachable, getaddrinfo ENOTFOUND). Metadata checked: ISC, 1.8k stars, last commit 2026-09-02, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/README.md>
  - <https://github.com/josephg/diamond-types>
  - <https://github.com/josephg/diamond-types/commits>
  - <https://github.com/josephg/diamond-types/tree/master/js>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/bench.sh>
  - <https://github.com/josephg/egwalker-paper>
  - <https://github.com/josephg/egwalker-paper/commits/master>
  - <https://github.com/josephg/egwalker-paper/commits/master/results/timings.json>
  - <https://github.com/josephg/egwalker-paper/tree/master/tools/paper-benchmarks/src>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/results/timings.json>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/Makefile>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/step2b-benchmarks.sh>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/eg-walker.tex>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/svg-plot/render.js>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/collect.js>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/bench-yjs/bench-remote.js>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/src/benchmarks.rs>
  - <https://raw.githubusercontent.com/dmonad/crdt-benchmarks/HEAD/README.md>
  - <https://registry.npmjs.org/diamond-types-node>
  - <https://registry.npmjs.org/diamond-types-web>
  - <https://crates.io/api/v1/crates/diamond-types>
- **Sources the enricher read:**
  - <https://github.com/josephg/diamond-types>
  - <https://github.com/josephg/diamond-types/issues>
  - <https://github.com/josephg/diamond-types/issues/50>
  - <https://github.com/josephg/diamond-types/pull/54>
  - <https://github.com/josephg/diamond-types/commits/master>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/build_wasm.sh>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/INTERNALS.md>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/crates/dt-wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/josephg/diamond-types/HEAD/crates/dt-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/step2b-benchmarks.sh>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/Makefile>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/collect.js>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/results/timings.json>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/results/dataset_stats.json>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/eg-walker.tex>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/bench-yjs/bench-remote.js>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/bench-yjs/package.json>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/Cargo.lock>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/src/benchmarks.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/paper-benchmarks/src/convert1.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/diamond-types/crates/bench/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/diamond-types/crates/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/diamond-types/src/list/oplog.rs>
  - <https://raw.githubusercontent.com/josephg/egwalker-paper/HEAD/tools/diamond-types/src/list/merge.rs>
  - <https://crates.io/api/v1/crates/diamond-types>
  - <https://registry.npmjs.org/diamond-types-node>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/josephg/diamond-types`) · [data/wave13/enrich/raw/github_com_josephg_diamond_types.json](../../../data/wave13/enrich/raw/github_com_josephg_diamond_types.json) (enrichment confidence 0.82)

</details>
