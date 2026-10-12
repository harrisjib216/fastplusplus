# fast-pako (@r1ck404/fast-pako)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust compiled to WebAssembly (zlib port) with JavaScript wrapper` · `MIT AND Zlib` · 🟢 active

> pako 2.1.0's zlib ported to Rust/WebAssembly with byte-identical output; 4-6x faster inflate/ungzip, about 2x deflate.

| | |
|---|---|
| **Beats** | pako 2.1.0 (pure JavaScript zlib port) |
| **Claimed result** | ungzip typescript 5.9.3 npm tarball (4.4 MB) 99.8 ms vs 17.3 ms (5.8x); inflate 9 MB of JavaScript 28.1 ms vs 6.7 ms (4.2x); deflateRaw level 1 on 1 MB 9.9 ms vs 3.2 ms (3.0x); deflate level 6 on 1 MB 32.8 ms vs 15.7 ms (2.1x); level 9 140.2 ms vs 64.3 ms (2.2x); deflate level 6 on 75 B 80.6 us vs 4.0 us (20x); import plus first ungzip of a 1.4 MB tarball 49.7 ms vs 12.2 ms. |
| **Workload** | ungzip, inflate and deflate calls on npm tarballs and JavaScript files from 75 bytes to 9 MB, best of 3 rounds in fresh processes, Node 24.16 (some rows also in Chromium 149). |
| **Metric** | latency |
| **Hardware** | Ryzen 7 7800X3D, Node 24.16 and Chromium 149 |
| **Compiler and flags** | Rust (toolchain version not stated) via cargo build --release for wasm32-unknown-unknown: opt-level=3, lto="fat", codegen-units=1, panic="abort" (rust/Cargo.toml); rustflags -C target-feature=+simd128,+bulk-memory,+sign-ext,+mutable-globals,+nontrapping-fptoint, -C no-vectorize-loops, -C llvm-args=-unroll-max-count=1 (rust/.cargo/config.toml); then wasm-opt (binaryen) in build.mjs. Benchmarks run as node --expose-gc --max-old-space-size=8192 via bench/interleave.mjs on Node 24.16. |
| **Adoption** | 1 star (fast-packages repo) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/r1ck404/fast-packages/tree/main/packages/fast-pako) · [benchmark](https://github.com/R1ck404/fast-packages) |

## Verdict

Author-run results on a Ryzen 7 7800X3D with Node 24.16: ungzip of the typescript 5.9.3 tarball 99.8 ms with pako 2.1.0 vs 17.3 ms (5.8x), inflate of 9 MB JavaScript 28.1 vs 6.7 ms (4.2x), deflateRaw level 1 on 1 MB 9.9 vs 3.2 ms (3.0x), deflate level 6 on 1 MB 32.8 vs 15.7 ms (2.1x) and level 9 140.2 vs 64.3 ms (2.2x), with the committed raw results file matching the README; only pako is the baseline.

## Use it when

- Code or dependencies already calling pako 2.1.0 (for example npm tarball unpacking with ungzip, 1-100 MB) where you can swap the package via an npm/pnpm alias or bundler alias and want 4-6x faster decompression with identical results.
- Browsers or in-browser Node emulators (the package was built for Nodepod) where native node:zlib or CompressionStream is unavailable or lacks pako's exact streaming semantics.
- Many small one-shot calls (hundreds of bytes): 4-8x per call, and 20x for a 75-byte deflate, because sessions are pooled instead of re-allocated.
- deflateRaw level 1 packing where byte-for-byte equality with pako output matters (2.6-4.8x in the author's runs).

## Skip it when

- Server-side Node code that can call node:zlib (native zlib) or a native binding: no comparison against native zlib, zlib-ng or fflate is published, and the README's own notes put level-6 deflate at roughly native-zlib speed at best.
- Engines without WebAssembly SIMD or where wasm compilation is not allowed: the module is built with simd128 and other post-MVP features, has no JS fallback, and the first call throws.
- Bundle-size-sensitive pages: the gzip-compressed bundle is about 2x pako's (30.6 KB vs 15.1 KB for the default import, README size table).
- Projects needing a mature, widely used dependency: the repo is about two weeks old, has 1 star, a single author, no issue history, and npm's latest version (2.1.3) has no matching commit in the repository.
- Code that relies on pako's lib/\* or dist/\* subpaths, its CommonJS entry, or on looping/corrupting behaviour for invalid options (fast-pako throws instead).

## How it is fast

Inflate uses a new inner decode loop in Rust (64-bit bit buffer with branchless refill, single-level fast decode tables, 16-byte match copies, in the style of libdeflate) while keeping pako's case-for-case state machine for externally visible state; one-shot calls decode straight into a contiguous output buffer and skip window copies. Checksums use a table-free folding CRC-32 and SIMD128 Adler-32, and level-1 deflate emits precomputed codes. Deflate at levels 6-9 keeps zlib's match finder unchanged so output stays byte-identical, which caps that gain near 2x; small calls gain mostly because pooled wasm sessions avoid pako's per-call allocation and zeroing of windows and hash tables.

## Compared with alternatives

Pick it over zip.js's WASM zlib codec or @mtcute/wasm when existing code is written against pako's API and must keep pako's exact bytes, stream chunking and errors; pick those when you are building a zip pipeline (zip.js) or want a small general compression-plus-crypto wasm bundle (mtcute), since both publish comparisons that also include native zlib.

## Integration

| | |
|---|---|
| **Form** | module (ESM npm package with the wasm embedded as text in fastzlib.wasm.mjs) |
| **Dependencies** | none at runtime; building from source needs Rust for wasm32-unknown-unknown and binaryen (wasm-opt) |
| **Minimum toolchain** | Node &gt;= 18 (package engines) or a browser with WebAssembly SIMD128, bulk-memory, sign-ext and non-trapping float-to-int; Rust version for rebuilding not stated |
| **Platforms** | any JavaScript engine with WebAssembly SIMD; CI ran Linux Node 20/22/24 and Windows Node 24; benchmarks on x86-64 (Ryzen 7 7800X3D) only |
| **Thread safety** | not documented; module-level state (one-shot sessions, a pool of up to 4 streaming sessions) lives per JS realm, and each worker loads its own wasm instance |
| **Drop-in for the baseline** | partial — same API, bytes and error messages as pako 2.1.0 for valid use, but ESM-only exports (no require/CommonJS entry or lib/\*, dist/\* subpaths), needs WebAssembly, and throws where pako loops forever or corrupts data on invalid options |

## Gotchas

- The published tables (2026-09-28) were measured on an earlier build: commit 7df1749 (2026-09-30) changed rust/src/deflate.rs and the shipped wasm without re-measuring, and npm's latest @r1ck404/fast-pako 2.1.3 (published 2026-09-30, no gitHead) is newer than the 2.1.2 in the repository's package.json.
- Benchmark harness (bench/harness.mjs, interleave.mjs): 300 ms warm-up, batched samples, per-process median, then the minimum of 3 fresh-process medians; results are discarded but each call copies its output out of wasm memory, inputs are produced by real pako, and correctness is checked by separate test suites, not during timing. Warm repeated calls favour fast-pako's pooled sessions, so the tiny-input rows measure pako's per-call setup more than compression.
- Each one-shot call copies the whole input into wasm linear memory and builds the whole output there before slicing it out; the heap is trimmed to 8 MB per session, but a wasm Memory never shrinks, so the process keeps the peak of the largest call.
- fflate and pako 3.0.2 are wired into bench/pako.bench.mjs as implementations but no results for them are committed, so their relative standing is unknown.

## Known shortcomings

- Numbers match but the only baseline is pako (no native zlib or fflate); Rust toolchain version unstated (flags in rust/Cargo.toml and .cargo/config.toml); the tables predate the 7df1749 deflate.rs change; the 20x 75-byte row is pako setup cost; 1 star, days old.
- Harness is sound (300 ms warmup, per-process median, minimum of 3 fresh processes, output copied out of wasm memory), but the tiny-input rows mostly time pako's per-call setup against fast-pako's pooled sessions. npm latest 2.1.3 has no gitHead and the repo is at 2.1.2; the tables predate 7df1749; fflate and pako3 are wired into the bench with no committed results; no native zlib baseline; ESM-only exports; requires wasm SIMD with no JS fallback; wasm memory keeps the peak of the largest call; the gzip bundle is twice pako's.

## Caveats and trade-offs

First-party numbers on a repository that is only days old (oldest visible commits 2026-09-27, result files from 2026-09-26/28) with 1 star. Each row keeps the best (minimum) per-process median of 3 interleaved fresh-process rounds; raw data is in results/. The published tables were measured 2026-09-28, before commit 7df1749 (2026-09-30) changed rust/src/deflate.rs (level-0 stored path) and the shipped wasm; the README tables were not re-measured. The only baseline is pako 2.1.0; native Node zlib, zlib-ng and fflate are not compared (fflate and pako 3.0.2 sit in the devDependencies but are not in the published tables), so it is a win over the JS equivalent and not over native zlib. The deflate L6/L9 gains are about 2x and, per the README, bounded by zlib's match finder (output is byte-identical to pako). The 20x row (deflate level 6 on 75 B) and the other tiny-input rows mostly measure pako's per-call setup, not compression throughput. The repo covers several packages (fast-acorn, fast-esbuild-wasm, fast-es-module-lexer, fast-brotli-wasm, fast-noble-hashes); this entry is the zlib port only, and the repo URL points at its package directory. fast-pako throws where pako would loop forever or corrupt data on some invalid options (documented differences). [retier] First-party numbers on a repository only days old (1 star). The harness is sound (300 ms warmup, per-process median, minimum of 3 interleaved fresh-process rounds, output copied out of wasm memory), but the tiny-input rows (75 B, 20x) mostly time pako's per-call setup against fast-pako's pooled sessions. The tables (2026-09-28) predate commit 7df1749 (2026-09-30), which changed rust/src/deflate.rs and the shipped wasm without re-measuring; npm latest 2.1.3 has no gitHead while the repo is at 2.1.2. fflate and pako3 are wired into the bench with no committed results; no native zlib baseline; ESM-only exports; requires wasm SIMD with no JS fallback; wasm memory keeps the peak of the largest call; the gzip bundle is twice pako's.

Drop-in for pako 2.1.0 with byte-identical output and TypeScript types; throws if WebAssembly is unavailable; the WASM is embedded and loads synchronously on first use; deflate at levels 6 and 9 gains only about 2x because the zlib match finder must stay identical.

## Maintenance

Actively developed by one author since late September 2026 (last commit 2026-10-01), MIT AND Zlib licensed and installable from npm, but very young (1 star, no issues) and its README numbers predate the latest code and npm release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: the root README 'fast-pako vs pako 2.1.0' table matches the committed raw data (results/pako-pako_vs_prev_vs_fast-interleaved-2026-09-28T09-59-45-448Z.md), the harness is public (bench/interleave.mjs plus the pako suite), the CPU (Ryzen 7 7800X3D), Node 24.16 and the Rust release profile and RUSTFLAGS (rust/Cargo.toml, rust/.cargo/config.toml) are public. Not A: the Rust toolchain version is not stated anywhere (no rust-toolchain file), and the measured build is not pinned to a commit (HEAD 7df1749 changed rust/src/deflate.rs and the shipped wasm after the measurement without re-measuring).
- **Verifier notes:** Every claimed number matches the README and the committed results file (ungzip typescript 99.84 vs 17.25 ms, inflate 9 MB 28.13 vs 6.70 ms, deflateRaw L1 9.85 vs 3.24 ms, L6 32.80 vs 15.70 ms, L9 140.21 vs 64.33 ms, 75 B 80.6 vs 4.0 us; the import-plus-first-ungzip row is from the README startup table). Shortcomings to record: first-party only, 1 star, days old; pako is the only baseline (no native zlib or fflate); tables predate HEAD's deflate changes; Rust toolchain version unstated; tiny-input 20x reflects pako setup cost. License MIT AND Zlib confirmed from packages/fast-pako/package.json and LICENSE.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-22 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/R1ck404/fast-packages>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://github.com/R1ck404/fast-packages/commit/7df1749>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/build.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/.cargo/config.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/pako-pako_vs_prev_vs_fast-interleaved-2026-09-28T09-59-45-448Z.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/build.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/.cargo/config.toml>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/index.mts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/src/inflate.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/src/checksum.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-pako/rust/src/heap.rs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/harness.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/pako.bench.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/corpus.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/compare.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/pako-pako_vs_prev_vs_fast-interleaved-2026-09-28T09-59-45-448Z.md>
  - <https://github.com/R1ck404/fast-packages/tree/main/packages/fast-pako/rust/src>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/issues>
  - <https://registry.npmjs.org/@r1ck404%2ffast-pako>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:r1ck404-fast-packages-fast-pako`) · [data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_pako.json](../../../data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_pako.json) (enrichment confidence 0.6)

</details>
