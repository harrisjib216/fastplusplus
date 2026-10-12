# commp-wasm (@hugomrdias/commp-wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust-to-WASM Filecoin CommP (piece commitment) hasher; 11-34x the throughput of @web3-storage/data-segment in Node and browsers.

| | |
|---|---|
| **Beats** | @web3-storage/data-segment (original JavaScript CommP implementation) |
| **Claimed result** | Node 26: 181.2 MiB/s vs 11.8 MiB/s original JS (15.38x), versus 41.4 MiB/s for a faster JS SHA-256 variant (3.52x). Browsers: Chromium 153 185.6 vs 7.5 MiB/s (24.8x), Firefox 155 170.7 vs 5.0 (34.2x), WebKit 187.3 vs 16.5 (11.3x). |
| **Workload** | Streaming Filecoin Piece Commitment (CommP) hashing of 1 MiB inputs in Node and in Chromium, Firefox and WebKit via playwright-test. |
| **Metric** | throughput |
| **Hardware** | Apple Silicon (chip not stated for the README tables), Node 26, Chromium 153, Firefox 155, WebKit (Safari 26.6). The repo's compare/results/apple-m1-pro-darwin-arm64.md run of 2026-09-30 is on an Apple M1 Pro with node v26.10.0 and shows the same wasm rate (182.8 MiB/s at 1 GiB), so the README bench probably ran on that machine (inference, not stated). |
| **Compiler and flags** | Rust release profile opt-level 3, fat LTO, codegen-units 1, strip; wasm-opt -O4 --enable-bulk-memory --enable-simd --strip-producers (rs/commp/Cargo.toml); rustc 1.92.0 pinned per compare/README.md; wasm32 simd128 with a 4-message multi-buffer SHA-256 backend. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/hugomrdias/commp) · [benchmark](https://github.com/hugomrdias/commp#benchmarks) |

## Verdict

First-party tinybench run (100 ms / 250 iterations, one 1 MiB buffer, create-write-digest per iteration) on Apple Silicon, probably the M1 Pro of compare/results: WASM 181.2 MiB/s vs data-segment 5.3.x 11.8 MiB/s in Node 26 (15.4x); in browsers 185.6 vs 7.5 (Chromium 153), 170.7 vs 5.0 (Firefox 155), 187.3 vs 16.5 (WebKit). The separate compare/ run (M1 Pro, Node v26.10.0, 1 GiB) reproduces the WASM rate at 182.8 MiB/s and shows native Rust and Go faster.

## Use it when

- Computing CommP / piece CIDs for Filecoin or Storacha uploads in a browser, Deno, Bun or Node where native addons are unwanted.
- Large uploads streamed in chunks: memory stays O(log n) (about 3 MiB RSS growth for a 1 GiB payload in the repo's M1 Pro run).
- Replacing @web3-storage/data-segment's multihash hasher when hashing is the bottleneck; same digest layout, checked against data-segment and Lotus vectors.
- Bundler-free setups: inline base64 WASM needs no .wasm asset handling or async init.

## Skip it when

- Server-side bulk CommP where native code is allowed: the project's own native Rust build is 681 MiB/s single-threaded and 3,738 MiB/s with the parallel feature on an M1 Pro, versus 183 MiB/s for WASM; go-fil-commp-hashhash reaches 728 MiB/s (derived ratios 3.7x and 4x from page data). The native crate is not published on crates.io.
- You need piece aggregation, inclusion proofs or segment indexes: this only hashes; data-segment's aggregate/proof APIs have no counterpart here.
- Payloads above 127 \* 2^47 bytes (MAX_PAYLOAD_SIZE): write() throws RangeError.
- Maturity-sensitive deployments: npm package created 2026-09-30, 0 stars, single author; issues #2-#7 fixed off-by-one height, wrong empty-input padding, a usize overflow above about 31.75 MiB and a destructive build() in the week before the benchmarks.

## How it is fast

All three steps (FR32 pad, leaf hashing, tree reduction) run inside one WASM call per 1 MiB chunk instead of one JS-level SHA-256 call plus fresh Uint8Array allocations per 64-byte node, which is how data-segment works. Leaves are batched 128 quads (256 leaves) at a time and hashed with a hand-written 4-lane SIMD128 SHA-256 (one message per u32 lane of a v128, transposed in and out), and the second compression block uses a precomputed K+W table because every message is exactly 64 bytes. Completed subtrees go onto an O(log n) binary-counter stack and zero-padding commitments are computed once and cached.

## Compared with alternatives

hash-wasm, fast-noble-hashes and awasm-noble give faster generic SHA-256/BLAKE3 to JS, but a CommP built on them still pays one JS-to-WASM call per 64-byte node (the README's @webbuf row reaches only 41 MiB/s that way); pick commp-wasm when the output you need is the Filecoin piece commitment itself.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (inline WASM; Rust build uses wasm-bindgen, sha2 0.11 and talc) |
| **Minimum toolchain** | Node &gt;= 24 per repo engines; WASM SIMD128 support in the engine; rebuilding needs Rust 1.92.0 (pinned in compare/), wasm-pack and binaryen wasm-opt |
| **Platforms** | any JS engine with WebAssembly SIMD (Node, Chromium, Firefox, WebKit, Deno, Bun per README) |
| **Thread safety** | Single-threaded WASM instance; one hasher per stream, not documented for workers sharing an instance |
| **Drop-in for the baseline** | partial — same PieceDigest fields and multihash bytes as data-segment's multihash hasher, but a separate package with its own create(); hashers should be freed with free() (a FinalizationRegistry frees them eventually) |

## Gotchas

- Harness note: in Node the baseline's SHA-256 is node:crypto createHash per 64-byte node (sync-multihash-sha2 node export, native and hardware SHA-capable), wrapped in new Uint8Array, Digest objects and spread pushes; in browsers it is @noble/hashes (pure JS). So the 11.8 MiB/s Node baseline (about 85 ms per MiB, roughly 33,000 hash calls, about 2.6 us per call, derived) measures per-call and allocation overhead, not SHA arithmetic; the speedup comes from fusing and batching, not from a faster compression function.
- The README's 'Fast JS (@webbuf/sha256)' row is not pure JavaScript: commp-js's own header says it uses WASM-backed SHA-256.
- The bench hashes one constant 1 MiB buffer (fill(4)) per iteration with create/write/digest/free; no implementation has a data-dependent shortcut, so this does not inflate the numbers, but it is a single size and the WASM row includes the copy into WASM memory.
- WASM memory never shrinks; the JS wrapper feeds writes in 1 MiB chunks to bound it. Forgetting free() leaves cleanup to the FinalizationRegistry.

## Known shortcomings

- CPU model unstated (compare results say Apple M1 Pro); the wasm build is 3.7x slower than its own native Rust; 0 stars, no LICENSE file (MIT declared).
- Harness note: in Node the data-segment baseline calls node:crypto createHash once per 64-byte node with fresh Uint8Array and Digest objects, so the 11.8 MiB/s baseline measures per-call and allocation overhead (about 2.6 us per hash, derived), not SHA arithmetic; the 'Fast JS (@webbuf/sha256)' row is WASM SHA-256. Issues #2-#7 (height off by one, padding overflow, destructive build) were fixed one day before the SIMD release. Native Rust is about 3.7x faster than the wasm build. Two weeks old, 0 stars, not on crates.io.

## Caveats and trade-offs

Very new (npm package created 2026-09-30), 0 stars, first-party, chip model not stated for the README tables. Harness: tinybench (100 ms, 250 iterations) hashing one constant 1 MiB buffer per iteration with create/write/digest (plus free for wasm) for every implementation; correctness is checked separately by differential tests against data-segment and Lotus vectors (compare results: 1072 checks, 0 failures). The baseline data-segment hashes through sync-multihash-sha2 (npm metadata: a node-specific sha256 export in Node, @noble/hashes in browsers); its per-call cost was not inspected and likely dominates the 11.8 MiB/s figure. The 'Fast JS (@webbuf/sha256)' row may itself run WASM SHA-256 (the README describes webbuf as an inline-base64 WASM pattern). Against the category's native baseline the wasm build is slower: on the M1 Pro, native single-thread Rust reaches 681.2 MiB/s and go-fil-commp-hashhash with GOMAXPROCS=1 343.0 MiB/s vs 182.8 MiB/s for wasm (compare/results/apple-m1-pro-darwin-arm64.md), i.e. wasm about 3.7x slower than native Rust (derived from page data). License: README and npm package say MIT, the Rust crate's Cargo.toml says MIT OR Apache-2.0, and the repo has no LICENSE file.

Inline base64 wasm, streaming with O(log n) memory. Checked against go-fil-commp-hashhash known-answer vectors (rs/commp/tests). Uses wasm SIMD for the 4-message SHA-256 backend.

## Maintenance

Active (last commit 2026-10-01, all 11 issues closed) but two weeks old with 0 stars; MIT per README and npm (crate says MIT OR Apache-2.0, no LICENSE file), small and dependency-free enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (Node 26 and three browsers) produced by the public tinybench harness packages/bench/bench.js against @web3-storage/data-segment; all numbers match the record. Build flags are public but the README tables name only 'Apple Silicon', not a CPU model, so not A.
- **Verifier notes:** Numbers verified on the README; harness and build profile read. Shortcomings: first-party, CPU model unstated, no LICENSE file (MIT declared in package.json/README), baseline JS internals not inspected, and wasm is about 3.7x slower than the project's own native Rust build on M1 Pro.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/hugomrdias/commp>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/README.md>
  - <https://github.com/hugomrdias/commp/commits>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/Cargo.toml>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/bench/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/bench/bench.js>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-wasm/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/compare/README.md>
  - <https://github.com/hugomrdias/commp/tree/master/compare>
  - <https://github.com/hugomrdias/commp/tree/master/compare/results>
  - <https://raw.githubusercontent.com/hugomrdias/commp/master/compare/results/apple-m1-pro-darwin-arm64.md>
  - <https://raw.githubusercontent.com/hugomrdias/commp/master/packages/commp-js/package.json>
  - <https://raw.githubusercontent.com/storacha/data-segment/HEAD/package.json>
  - <https://registry.npmjs.org/sync-multihash-sha2/latest>
  - <https://registry.npmjs.org/@hugomrdias%2fcommp-wasm>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/README.md>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/bench/bench.js>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/bench/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/pnpm-workspace.yaml>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/Cargo.toml>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/lib.rs>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/hasher.rs>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/tree.rs>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/fr32.rs>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/sha256/mod.rs>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/rs/commp/src/sha256/wasm.rs>
  - <https://github.com/hugomrdias/commp/tree/master/rs/commp/src/sha256>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-wasm/src/index.js>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-wasm/src/inline/commp_bg.js>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-wasm/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-js/src/index.js>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/packages/commp-js/package.json>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/compare/README.md>
  - <https://raw.githubusercontent.com/hugomrdias/commp/HEAD/compare/results/apple-m1-pro-darwin-arm64.md>
  - <https://github.com/hugomrdias/commp/issues?q=is%3Aissue>
  - <https://github.com/hugomrdias/commp/commits>
  - <https://github.com/storacha/data-segment/tree/main/src>
  - <https://raw.githubusercontent.com/storacha/data-segment/HEAD/src/multihash.js>
  - <https://raw.githubusercontent.com/storacha/data-segment/HEAD/src/proof.js>
  - <https://raw.githubusercontent.com/storacha/data-segment/HEAD/src/ipld/sha256.js>
  - <https://raw.githubusercontent.com/storacha/data-segment/HEAD/package.json>
  - <https://registry.npmjs.org/sync-multihash-sha2/latest>
  - <https://registry.npmjs.org/sync-multihash-sha2/-/sync-multihash-sha2-1.0.0.tgz>
  - <https://registry.npmjs.org/@hugomrdias%2fcommp-wasm>
  - <https://crates.io/api/v1/crates/commp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/hugomrdias/commp`) · [data/wave13/enrich/raw/github_com_hugomrdias_commp.json](../../../data/wave13/enrich/raw/github_com_hugomrdias_commp.json) (enrichment confidence 0.8)

</details>
