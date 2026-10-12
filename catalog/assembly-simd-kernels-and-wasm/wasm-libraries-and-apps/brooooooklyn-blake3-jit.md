# blake3-jit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟢 active

> BLAKE3 in TypeScript with a runtime-generated WASM SIMD module; beats the native napi-rs addon only on inputs under 4 KB.

| | |
|---|---|
| **Beats** | @napi-rs/blake-hash (native Rust BLAKE3 Node addon) |
| **Claimed result** | 96 B: 362 MB/s vs 149 MB/s (2.4x faster); 512 B: 748 vs 521 MB/s (1.4x); 1 KB: 811 vs 701 MB/s (1.2x); 32 KB: 1.36 vs 1.97 GB/s and 1 MB: 1.38 vs 2.06 GB/s (native wins). |
| **Workload** | BLAKE3 hashing of 96 B, 512 B, 1 KB, 32 KB and 1 MB inputs through blake3-jit (JavaScript with runtime-generated WASM SIMD) versus the native napi addon. |
| **Metric** | throughput |
| **Adoption** | 35 stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/Brooooooklyn/blake3-jit) · [benchmark](https://github.com/Brooooooklyn/blake3-jit#benchmarks) |

## Verdict

The author's README table compares one-shot hash() against @napi-rs/blake-hash 1.4.0, an N-API addon calling the official blake3 crate's single-threaded blake3::hash (runtime SIMD dispatch, NEON on aarch64), timed in Node with bench/compare-blake3-fast.ts on unstated hardware: 362 vs 149 MB/s at 96 B (2.4x), 748 vs 521 at 512 B, 811 vs 701 at 1 KB, then 1.36 vs 1.97 GB/s at 32 KB and 1.38 vs 2.06 GB/s at 1 MB where native wins.

## Use it when

- Node.js code hashing many small messages (96 B to 1 KB: cache keys, content IDs, small records) where the author's run shows 1.2x to 2.4x the throughput of the @napi-rs/blake-hash native addon because no FFI crossing happens.
- Browsers, Deno, Bun, edge workers or bundles that cannot load native addons or host a separate .wasm asset, and need BLAKE3 from one dependency-free ESM package.
- Large one-shot hashes in JS-only environments, where the author reports about 1.36-1.38 GB/s at 32 KB-1 MB (hardware not stated) from the WASM SIMD path.
- Code needing keyed MAC, derive_key or XOF in pure JS: the test suite checks all three modes against the official BLAKE3 test vectors (input lengths 0 to 102,400 bytes).

## Skip it when

- Node services hashing buffers of 4 KB and up where a native addon installs: @napi-rs/blake-hash measured 1.97 vs 1.36 GB/s at 32 KB and 2.06 vs 1.38 GB/s at 1 MB in the author's own table (native about 1.5x faster), and the Rust crate's multithreaded mode is not even in the comparison.
- Streaming, keyed or derive_key hashing of large data: only one-shot hash()/hashInto() route to WASM SIMD; the Hasher class (update/finalize, createKeyed, createDeriveKey) is pure JS at every size and has no published large-input numbers.
- One-shot output longer than 64 bytes: hash()/hashInto() allocate at most a 16-word buffer and throw a RangeError for outputLength above 64; use createHasher().update(x).finalize(n) or finalizeXof() instead.
- Pages whose Content Security Policy forbids WebAssembly compilation, or engines without WASM SIMD: initSimdSync() catches the failure, logs console.warn and silently falls back to the pure-JS path for all sizes.
- Non-V8 engines when speed matters: docs/optimizations.md lists 'V8 optimizations may not apply to other engines' as a known limitation and no SpiderMonkey or JavaScriptCore numbers are published.

## How it is fast

Below 4 KB (SIMD_THRESHOLD = 4 \* CHUNK_LEN in src/hash.ts) it runs a pure-JS compress that applies the Fleek Network blake3js-perf case-study tricks: message and state held in 32 local int32 (SMI) variables with precomputed permutations, module-level reusable typed arrays, and a single Uint32Array view over aligned little-endian input instead of per-block byte assembly; at 96 B to 1 KB this avoids the N-API call and Buffer allocation that dominate the native addon's cost. From 4 KB up, one-shot hash() transposes 4 chunks at a time into WASM linear memory and calls a JIT-emitted compressChunks4x (16 blocks x 4 chunks per call, i32x4 lanes, i8x16.shuffle for the 16- and 8-bit rotations) and a WASM parent-node compress, with the Merkle CV stack kept in a fixed 64 KB arena. That path is only 4 lanes wide and copies every input word through JS typed arrays, which is why native AVX2/AVX-512/NEON code stays ahead on large inputs.

## Compared with alternatives

Pick it over hash-wasm or awasm-noble when you only need BLAKE3, want no .wasm asset at all, and mostly hash inputs under a few KB in Node, where its pure-JS path avoids the boundary crossing; awasm-noble's third-party table (Apple M4) reports a higher 1 MB rate (1,943 MB/s single-threaded, plus a threaded mode), so prefer it for large buffers, and use hash-wasm when you need many algorithms behind one API.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (devDependencies only for tests and benchmarks) |
| **Minimum toolchain** | not documented; ESM-only package (type: module); WASM SIMD path needs an engine with fixed-width WebAssembly SIMD (feature-tested with WebAssembly.validate at init), otherwise pure JS |
| **Platforms** | any JavaScript engine; big-endian hosts and unaligned inputs take a byte-assembly slow path |
| **Thread safety** | single-threaded only per the docs: module-level scratch buffers and one shared WASM memory per module instance; each worker thread loads its own instance |
| **Drop-in for the baseline** | partial: different function names and return type (Uint8Array, not Buffer), Uint8Array input only (no string, hex/base64 digest or stream helpers), same digests for the default 32-byte output |

## Gotchas

- Harness flaw: every size where blake3-jit beats native (96 B, 512 B, 1 KB) runs the pure-JS path, so the win is N-API call and Buffer-allocation overhead, not WebAssembly; the runtime-generated WASM SIMD path (4 KB and up) loses to native at every published size (0.69x at 32 KB, 0.67x at 1 MB, derived from page data).
- bench/compare-blake3-fast.ts imports blake3-fast from an untracked ../tmp/blake3-fast build, so the published comparison cannot run from a clean checkout; each row is one 1-second loop after 100 warm-ups with no repeats, CPU or Node version, and the cross-library correctness check uses only a 5-byte input (the SIMD path is covered by the unit tests' official vectors, not by the harness).
- README and docs/optimizations.md report different runs (96 B: 362 MB/s in the README, 352 MB/s in the docs, where the comparison column is blake3-fast at 216 MB/s); the README omits the @huggingface/blake3-wasm column the harness also prints.
- hash()/hashInto() with outputLength &gt; 64 throw a RangeError (new Uint8Array over a 64-byte buffer); the unit tests exercise one-shot output lengths of only 16, 32 and 64 bytes and never call hashInto().

## Known shortcomings

- Wins at 96 B-1 KB run on the pure-JavaScript path (SIMD_THRESHOLD 4 KB) and the WASM SIMD path is 0.67-0.69x against @napi-rs/blake-hash; no hardware or Node version; the baseline is the same author's napi binding of the blake3 crate.
- Enricher: the wins at 96 B-1 KB come from the pure-JS path beating napi FFI overhead while the WASM SIMD path (4 KB and up) loses to native at 0.67-0.69x; compare-blake3-fast.ts imports blake3-fast from an untracked ../tmp; one 1 s loop per row; correctness checked only on a 5-byte input; README and docs come from different runs; hash()/hashInto() with outputLength above 64 throw RangeError (16-word buffer) and hashInto is untested; the Hasher (keyed, derive_key, streaming) has no SIMD path; the baseline blake3::hash is fair (NEON on by default on aarch64). @huggingface/blake3-jit is a fork. Lead: fleek-network/blake3js-perf (numbers only on the Fleek blog).

## Caveats and trade-offs

First-party; no hardware or Node version stated. Inputs below 4 KB (SIMD_THRESHOLD = 4 \* CHUNK_LEN in src/hash.ts) run the pure JavaScript path, so every size where blake3-jit wins (96 B, 512 B, 1 KB) is pure JS beating napi call overhead, not WebAssembly; the runtime-generated WASM SIMD path (4 KB and above) is slower than the native addon (32 KB 1.36 vs 1.97 GB/s, 0.69x; 1 MB 1.38 vs 2.06 GB/s, 0.67x, derived from page data). The baseline @napi-rs/blake-hash is the same author's napi binding of the official blake3 Rust crate (a different implementation, not the same code compiled natively). The harness also times @huggingface/blake3-wasm (a wasm-vs-wasm comparison) and blake3-fast, but the README publishes only the napi column; the blake3-fast build is loaded from ../tmp and is not in the repo. Correctness of the timed paths is checked only on a 5-byte input in the harness.

Faster than the native addon only for small inputs where FFI overhead dominates; native wins from tens of KB up. Generates wasm at runtime so there is no .wasm file to ship.

## Maintenance

Active: renovate commits through 2026-10-07 and release 1.1.0 on 2026-04-17 (npm registry, first release 2025-12-10), MIT, 35 stars, single maintainer (the napi-rs author); Hugging Face published its own fork as @huggingface/blake3-jit and had reset() upstreamed (issue #34).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table; the harness bench/compare-blake3-fast.ts is public (blake3-jit vs @napi-rs/blake-hash 1.4.0, @huggingface/blake3-wasm and a blake3-fast build loaded from an untracked ../tmp path), but no CPU model, Node version or run command output are stated.
- **Verifier notes:** Numbers, MIT licence, 35 stars, 122 commits and last commit 2026-10-07 (renovate bot; active) verified. Shortcoming for this category: the WASM part never beats native; wins are pure-JS small-input FFI-overhead wins. baseline_in_list left false; the napi baseline wraps the listed BLAKE3 crate (wave 7) if the orchestrator wants to treat it as an in-list baseline.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Brooooooklyn/blake3-jit>
  - <https://github.com/Brooooooklyn/blake3-jit/commits>
  - <https://github.com/Brooooooklyn/blake3-jit/tree/main/bench>
  - <https://github.com/Brooooooklyn/blake3-jit/tree/main/docs>
  - <https://github.com/Brooooooklyn/blake3-jit/tree/main/src>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/bench/benchmark.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/bench/compare-blake3-fast.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/hash.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake-hash/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/Brooooooklyn/blake3-jit>
  - <https://github.com/Brooooooklyn/blake3-jit/issues?q=is%3Aissue>
  - <https://github.com/Brooooooklyn/blake3-jit/issues/34>
  - <https://github.com/Brooooooklyn/blake3-jit/tree/main/test>
  - <https://github.com/Brooooooklyn/blake3-jit/tree/main/docs>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/bench/benchmark.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/bench/compare-blake3-fast.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/hash.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/wasm-simd.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/hasher.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/compress.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/utils.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/src/constants.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/test/official-vectors.test.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/test/vectors.test.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/test/test_vectors.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/test/reset.test.ts>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake3-jit/HEAD/docs/optimizations.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake-hash/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/blake-hash/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/BLAKE3-team/BLAKE3/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/BLAKE3-team/BLAKE3/HEAD/build.rs>
  - <https://registry.npmjs.org/blake3-jit>
  - <https://github.com/fleek-network/blake3js-perf>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/brooooooklyn/blake3-jit`) · [data/wave13/enrich/raw/github_com_brooooooklyn_blake3_jit.json](../../../data/wave13/enrich/raw/github_com_brooooooklyn_blake3_jit.json) (enrichment confidence 0.75)

</details>
