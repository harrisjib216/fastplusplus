# tape-sha256 (spool-labs/sha256) WebAssembly SIMD build

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust (WebAssembly simd128 backend, also native AVX-512, AVX2, SHA-NI, NEON)` · `Apache-2.0` · 🟢 active

> Multi-buffer SHA-256 in Rust whose wasm simd128 build hashes small-message batches about 3.4-3.7x faster than @noble/hashes in V8.

| | |
|---|---|
| **Beats** | @noble/hashes SHA-256 (pure JavaScript, what @solana/web3.js 1.x uses) in V8 |
| **Claimed result** | Node v24, 64-leaf batch: tape wasm 100.61 us/batch (673 MB/s) vs noble one-shot 337.97 us/batch (200 MB/s), about 3.4x (derived from page data), vs hash-wasm 156.24 us (1.55x derived). Chrome 150 grinding: 4.55 M candidates/s, 3.72x the noble/web3.js stack (1.22 M/s) and 1.61x hash-wasm (2.82 M/s) |
| **Workload** | Merkle-style batch of 64 separate \~1 KB messages hashed per call in Node (JS-to-wasm copies included), and a Chrome vanity-address grinding loop over 2048 candidates of 87 bytes |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max |
| **Compiler and flags** | RUSTFLAGS='-C target-feature=+simd128' cargo build --release --example wasm_lib --target wasm32-unknown-unknown. The rustc version is not stated (Cargo.toml rust-version 1.89; Cargo.lock committed). Runtimes: Node v24 (V8, 'unpinned, read as ratios') and Chrome 150. JS baselines: @noble/hashes ^1.5.0 and hash-wasm ^4.11.0 (benches/wasm/package.json). Harnesses: bench.mjs, pda.mjs, matrix.cjs and browser/browser-bench.mjs in benches/wasm. Estimator: best of 15 rounds x 50 iterations after 200 warmups. |
| **Adoption** | 1 star, 0 forks, 13 commits (July-August 2026); crate tape-sha256 0.2.1 on crates.io, 468 downloads |
| **Last commit** | 2026-08-11 |
| **Links** | [repository](https://github.com/spool-labs/sha256) · [benchmark](https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/README.md) |

## Verdict

On an Apple M4 Max, a 64-leaf Merkle batch (67,680 bytes) in Node v24 took 100.61 us with the simd128 wasm build including copies in and out, against 337.97 us for @noble/hashes 1.x one-shot (about 3.4x) and 156.24 us for hash-wasm (1.55x), while node:crypto took 42.89 us; in Chrome 150 an 87-byte createWithSeed grind reached 4.55 M candidates/s against 1.22 M for noble (3.72x) and 2.82 M for hash-wasm (1.61x). Builds used rustc release with +simd128; best of 15 rounds x 50 iterations (Chrome: 12 x 20, grind 12 x 4) after warmup, with every tape lane checked against node:crypto or noble.

## Use it when

- Hashing many small independent messages (about 60-100 bytes, two SHA-256 blocks) in a synchronous browser loop, such as Solana createWithSeed vanity-address grinding: 4.55 M candidates/s in Chrome 150, 3.7x noble and 1.6x hash-wasm.
- Replacing @noble/hashes (the @solana/web3.js 1.x path) or hash-wasm for batched Merkle-leaf hashing in a JS runtime without native crypto, where you can collect leaves into one call.
- Rust code (native, not wasm) that hashes Merkle leaves or verifies many hash chains: the same crate dispatches to AVX-512, SHA-NI, ARM SHA-2 and NEON multi-buffer kernels, 2.0-6.8x the sha2 crate in its BENCHMARKS.md.
- Engines where the multi-buffer wasm kernel is known to help: V8 (Node, Chrome) and JavaScriptCore (Bun) per the repo's matrix.cjs runs.

## Skip it when

- Node.js: native node:crypto crypto.hash does the 64-leaf batch in 42.89 us against 100.61 us for the wasm build (2.3x faster, derived from page data); the author recommends a napi binding of the native backend instead.
- Browser batches of \~1 KB messages: Chrome's WebCrypto subtle.digest with Promise.all measured 75 us against 80-90 us for the wasm build, and the README says to use WebCrypto there.
- One message at a time or one large message: the speedup comes from filling four lanes per call; a single-stream hasher such as hash-wasm or WebCrypto fits better.
- Solana PDA derivation: the ed25519 off-curve check is 94-99% of each candidate's cost, so batching the hashes gained only 4% (37.5 vs 39.1 us per PDA in Chrome).
- Targets that must run on engines without wasm SIMD (Safari and iOS before 16.4, per Emscripten's SIMD docs found by search): a simd128 build is rejected at instantiation and there is no runtime fallback inside one module.

## How it is fast

SHA-256 cannot be vectorised within one message because each round depends on the last, so the crate runs four independent messages in lockstep, one per u32x4 lane of a wasm v128 register (multi-buffer hashing, as in Intel's isa-l_crypto). Input words are loaded with a byte-swapping i8x16 shuffle and transposed into lane order with canonical i32x4 shuffles that engines lower to single instructions; rotates are shift-pair plus or, since wasm has no vector rotate. The rounds are fully unrolled (flat-round body), and one wasm call amortises the JS-to-wasm boundary over the whole batch, which is what beats per-call libraries on 60-90 byte messages.

## Compared with alternatives

Pick it over sha2-wasm (single-stream SHA-2, about 5-7% faster than hash-wasm) when you hash many independent short messages per call, since multi-buffer lanes and one boundary crossing per batch give 1.55-1.6x over hash-wasm here; pick sha2-wasm or WebCrypto for one long stream. For Solana PDA work pair it with a faster curve check such as berith's wasm Ed25519, because the hash is only 1-6% of the cost.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); for JS, a self-built wasm32-unknown-unknown cdylib from examples/wasm_lib.rs, no npm package |
| **Dependencies** | none at runtime (sha2, rand and ed25519-dalek are dev-dependencies only); JS glue must be written by the user |
| **Minimum toolchain** | Rust 1.89 (rust-version in Cargo.toml); wasm build needs RUSTFLAGS='-C target-feature=+simd128' and the wasm32-unknown-unknown target |
| **Platforms** | wasm32 with simd128 (simd128-4 kernel); native x86-64 (AVX-512, AVX2, SHA-NI), aarch64 (ARM SHA-2, NEON), portable Rust fallback elsewhere |
| **Thread safety** | Entry points are stateless; the crate docs say two threads may call them concurrently on disjoint halves of a batch. The crate never spawns or pins threads. |
| **Drop-in for the baseline** | partial — produces bit-identical SHA-256 digests, but replaces noble's per-message sha256(bytes) with a batch call over wasm linear memory and JS glue you write yourself |

## Gotchas

- Stale fallback claim: benches/wasm/README.md says a build without +simd128 falls back to portable-8 and 'roughly ties hash-wasm', but current dispatch in src/lib.rs (changed in commit d967d91 'fix portable fallback width', 2026-07-27; BENCHMARKS.md agrees) picks portable-8 only on aarch64 and portable-1 on every other target including wasm32, so the non-SIMD wasm speed is not documented for the current code.
- SIMD is a build-time fact in wasm (no runtime probing): ship two modules and feature-detect in JS if you need older engines. SpiderMonkey runs the 2x4 and 4x4 multi-wave kernels at 0.57-0.64x, so dispatch stays on the single 4-lane wave and Firefox gains are not measured beyond that.
- The example module's walloc never frees memory and the bench module is about 210 KB because it exports three extra wave kernels; the author measured a dispatch-only build at 47.1 KB (38.7 KB after wasm-opt, 14.2 KB gzipped).
- Benchmark reproducibility gaps: benches/wasm has no package-lock, so the exact @noble/hashes 1.x (^1.5.0; noble's current line is 2.4.0) and hash-wasm versions measured are not recorded; Node numbers are unpinned; Chrome's performance.now is clamped to 100 us, so batch rows move in 5 us steps and the grind rows (4 iterations of about 0.45 ms for tape) in roughly 5% steps, enough to blur tape vs WebCrypto at \~1 KB.

## Known shortcomings

- 3.36x and 1.55x (derived; Chrome grind 3.72x) but node:crypto (42.89 us) beats the wasm build (100.61 us) in Node; rustc unversioned (MSRV 1.89, Cargo.lock committed).
- Numbers stand. benches/wasm/README.md is stale: it says a build without +simd128 falls back to portable-8 and 'roughly ties hash-wasm', but the current src/lib.rs dispatch (commit d967d91, 2026-07-27; BENCHMARKS.md agrees) picks portable-1 on every non-aarch64 target including wasm32, so the non-SIMD wasm speed is undocumented. No JS lockfile, so the measured @noble/hashes 1.x and hash-wasm versions are unknown (noble's latest is 2.4.0); no npm package; the example walloc never frees; the simd128 module is rejected on Safari below 16.4; Chrome's 100 us timer clamp moves the grind rows in about 5% steps.

## Caveats and trade-offs

Inside Node, native node:crypto is much faster than this wasm build: crypto.hash one-shot takes 42.89 us per batch against 100.61 us for tape wasm (2.3x, derived from page data). The author recommends a napi binding over wasm in Node. In a browser, WebCrypto beats the wasm build on batched \~1 KB messages (75 us vs 80-90 us), and the page recommends WebCrypto there. So the win is against pure-JS noble and against hash-wasm, mainly for small messages in synchronous loops. For PDA derivation the gain is only 4%, because the ed25519 curve check dominates. Chrome clamps performance.now to 100 us, so the batch rows are quantised to 5 us steps. Node is unpinned, and the noble baseline is the 1.x line used by @solana/web3.js 1.x, not the latest noble. The repository is very young, has a single author and one star.

Without the simd128 flag the wasm falls back to a portable-8 backend that roughly ties hash-wasm; wasm SIMD cannot reach the SHA hardware units, so Node's native crypto (42.89 us/batch) and Chrome's WebCrypto are faster for \~1 KB batches; Node results are 'unpinned, read as ratios'.

## Maintenance

Active but very young (13 commits, 2026-07-26 to 2026-08-11, two committers, 1 star, 0 issues, crate 0.2.1 with 469 downloads); Apache-2.0 and small enough to vendor, but the JS integration is an example, not a maintained package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The harnesses are public: benches/wasm/bench.mjs (Node 64-leaf batch), pda.mjs and browser/browser-bench.mjs (Chrome grind). They run @noble/hashes, the stated baseline, with a correctness gate against node:crypto. The build command and flags (RUSTFLAGS +simd128, cargo build --release --example wasm_lib) and the CPU (Apple M4 Max) are stated. The rustc version is not stated, but the crate sets rust-version 1.89 and commits Cargo.lock.
- **Verifier notes:** The numbers match benches/wasm/README.md. Node 64-leaf batch: 100.61 vs 337.97 us against noble (3.36x, derived) and against 156.24 us for hash-wasm (1.55x, derived). Chrome grind: 4.55 M/s, 3.72x noble and 1.61x hash-wasm. The record omitted that node:crypto (42.89 us) beats the wasm in Node; that is now in the caveats. The crate's native SIMD claims against sha2, Firedancer and isa-l in BENCHMARKS.md could be a lead for a hashing category.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/spool-labs/sha256>
  - <https://github.com/spool-labs/sha256/commits>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/bench.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/pda.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/package.json>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/check.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/browser/browser-bench.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/browser/index.html>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/examples/wasm_lib.rs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/LICENSE>
  - <https://crates.io/api/v1/crates/tape-sha256>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/README.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/bench.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/pda.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/package.json>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/check.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/matrix.cjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/browser/browser-bench.mjs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/examples/wasm_lib.rs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/spool-labs/sha256/HEAD/src/simd128.rs>
  - https://raw.githubusercontent.com/spool-labs/sha256/HEAD/benches/wasm/package-lock.json (404)
  - <https://github.com/spool-labs/sha256/commits>
  - <https://github.com/spool-labs/sha256/commit/d967d91>
  - <https://github.com/spool-labs/sha256/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/tape-sha256>
  - https://registry.npmjs.org/tape-sha256 (404)
  - <https://registry.npmjs.org/@noble%2Fhashes>
  - WebSearch: Safari 16.4 WebAssembly SIMD support (snippets from emscripten.org/docs/porting/simd.html, nutrient.io, gigazine.net)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/spool-labs/sha256`) · [data/wave13/enrich/raw/github_com_spool_labs_sha256.json](../../../data/wave13/enrich/raw/github_com_spool_labs_sha256.json) (enrichment confidence 0.8)

</details>
