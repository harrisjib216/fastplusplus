# @gmod/inflate (wasm libdeflate batch inflate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (libdeflater compiled to WebAssembly) with TypeScript` · `MIT` · 🟢 active

> libdeflate compiled to WebAssembly for JS, inflating many raw-deflate blocks per call; about 2-3x faster than pako on BigWig blocks.

| | |
|---|---|
| **Beats** | pako 3.x inflateRaw (pure JavaScript inflate in V8), called once per block with a chunkSize hint. Both arms skip the 2-byte zlib header and leave adler32 unchecked. |
| **Claimed result** | bbi-js docs/wasm.md (benchmarks/inflate.bench.ts, best of three runs, mean ms): wasm 1.9 ms vs pako 6.0 ms on volvox.bw (49 blocks), 5.4 vs 16.6 ms on cow.bw (125), 31 vs 86 ms on ENCFF826FLP.bw (436), 29 vs 62 ms on variable_step_large.bw (489), i.e. 2.1-3.2x (derived from page data). The doc's own speedup table gives per-fixture ranges of 2.3-3.8x across three runs and summarizes them as '\~2.5-3x faster'. The platform DecompressionStream, called once per block, is 4-11x slower than wasm. The inflate-js README's 'roughly 4x faster than pako' is not backed by any table and exceeds the doc's own summary. |
| **Workload** | Inflate of the real zlib blocks of four BigWig fixtures (49 to 489 blocks per file), whole block run per call, timed in Node against pako and the platform DecompressionStream; the wasm module was extracted from the bbi-js genome-file parser |
| **Metric** | throughput |
| **Compiler and flags** | Rust crate (libdeflater 1.x with the freestanding feature, so libdeflate's C is built through cc-rs by a wasm-capable clang) built with cargo build --release --target wasm32-unknown-unknown. The release profile in crate/Cargo.toml sets opt-level=3, lto=true, codegen-units=1 and panic=abort. wasm-bindgen runs at the Cargo.lock version, webpack base64-inlines the result, and there is no wasm-opt pass. The Node version is not stated. Baseline pako is ^3.0.1 per bbi-js package.json. |
| **Adoption** | 0 stars (extracted August 2026 from bbi-js, 9 stars, 567 commits, used in GMOD genome-browser parsers) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/GMOD/inflate-js) · [benchmark](https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/docs/wasm.md) |

## Verdict

bbi-js's benchmarks/inflate.bench.ts ran under vitest bench in Node, with version and CPU not stated, and reports the best of three runs. Inflating every block of four BigWig fixtures (49-489 blocks, 139 KB to 3.3 MB compressed) took 1.9, 5.4, 31 and 29 ms through the wasm libdeflate batch call, against 6.0, 16.6, 86 and 62 ms for pako 3 inflateRaw called once per block with a chunkSize hint, about 2.1-3.2x (derived from page data). Outputs were asserted byte-identical before timing, and neither arm checked adler32.

## Use it when

- Genomics or other container formats in the browser or Node that store hundreds of separately zlib-compressed blocks with known uncompressed sizes (BigWig/BigBed, .hic, bgzf-style records), decoded in one batch per query.
- Replacing pako's per-block inflateRaw loop when inflate shows up in profiles: on BigWig fixtures of 49-489 blocks it took 1.9-31 ms against 6.0-86 ms for pako.
- Replacing a per-block DecompressionStream loop: the bbi-js doc measured 220-410 microseconds of fixed overhead per call in Node, which made it 4-11x slower than the batch call.
- Libraries that must not ask consumers to host a separate .wasm asset or configure a bundler: the module is base64-inlined and instantiated lazily on first call.

## Skip it when

- One large stream or concatenated gzip members: DecompressionStream needs one call and lands within about 2x of wasm there (bgzf case in the README table), and you avoid about 60 KB of base64.
- Whole-query speedups: the gain is the inflate step only, and bbi-js reports that an older whole-genome parseBigWig comparison was only about 5% apart end to end.
- Data that needs integrity checking: raw deflate skips zlib's adler32, and the package's own test pins that a flipped byte decodes silently to wrong output.
- Compression, streaming or incremental output, synchronous call sites (every function returns a Promise), or outputs over 256 MB per call (a hard cap in the crate).
- Pages with a strict Content-Security-Policy that blocks fetch() of data: URLs or wasm compilation: the loader fetches the inlined wasm as a data: URL and calls WebAssembly.instantiate.

## How it is fast

libdeflate is a whole-buffer, non-streaming DEFLATE decoder that writes straight into an output buffer sized from the index, with no growth loop and no streaming state machine. The batch entry point crosses the JS-wasm boundary once for the whole group of blocks and reuses one Decompressor and one scratch buffer across them, so the per-call overhead is paid once. It is built with opt-level 3, LTO and codegen-units=1, but it runs libdeflate's portable C path: the x86 and ARM-specific code does not apply on wasm32, and the build has no wasm SIMD target feature and no wasm-opt pass.

## Compared with alternatives

No other inflate implementation is catalogued in this category. It follows the same pattern as tape-sha256 and berith (native code compiled to wasm to replace a pure-JS library in V8), and is the one to pick when the hot path is many small deflate blocks rather than hashing or curve arithmetic.

## Integration

| | |
|---|---|
| **Form** | npm module (ESM and CommonJS builds) with the wasm inlined as base64; Rust crate source included for rebuilding |
| **Dependencies** | none at runtime (npm metadata lists no dependencies); rebuilding needs Rust with the wasm32-unknown-unknown target, wasm-bindgen-cli at the Cargo.lock version, webpack, and a clang that can target wasm (Apple clang cannot) |
| **Minimum toolchain** | not documented for consumers; the runtime needs WebAssembly plus a global fetch() that accepts data: URLs |
| **Platforms** | any JavaScript runtime with WebAssembly (Node, browsers, bundlers) |
| **Thread safety** | One wasm instance per module realm, created on first call and shared; concurrent first calls share one in-flight init promise. Workers each instantiate their own copy, and a bundle that reaches both the ESM and CJS entry points instantiates twice. |
| **Drop-in for the baseline** | no |

## Gotchas

- The header handling differs between functions: inflateRaw wants bare raw deflate (strip the 0x78 zlib header yourself), while inflateRawBatch expects every block to keep its 2-byte zlib header and skips two bytes without checking them, so gzip members or headerless blocks decode wrongly or fail.
- inflateRawBatch reserves num_blocks x maxBlockSize up front in grow-only wasm linear memory and refuses the call when that product exceeds 256 MB, even when the real output is far smaller; the memory is never returned to the host.
- Harness and evidence: the README's 'roughly 4x faster than pako' has no table behind it, and the bbi-js doc's two tables disagree. The best-of-three means give cow.bw 3.07x and variable_step_large.bw 2.14x, outside the same doc's per-fixture ranges of 2.3-2.7x and 2.7-3.0x, so they come from different runs. The numbers were measured on bbi-js's copy of the crate (without inflate-js's bounds checks), with Node version and CPU not stated.
- In the same benchmark, the DecompressionStream arm is fed whole zlib blocks with format 'deflate', so it also parses the header and verifies adler32. Its output is only length-checked. Both contradict the harness comment and the doc ('every arm does the same work', 'the same byte-identical assertion'), but this affects only the DecompressionStream column, not the pako comparison, which is byte-checked.

## Known shortcomings

- README "4x" exceeds the bbi-js doc's 2.5-3x (2.1-3.2x from page data); the benchmark lives in bbi-js, not inflate-js; no CPU or Node version; end-to-end gain only about 5%.
- Enricher: the bbi-js docs/wasm.md tables disagree (the mean table gives cow 3.07x and variable_step_large 2.14x, outside the doc's own 2.3-2.7x and 2.7-3.0x ranges); in the DecompressionStream column the 'deflate' arm parses the zlib header and checks adler32 while the output is only length-checked, contrary to the 'same work' and 'byte-identical' claims (the pako arm is byte-checked and fair); batch mode reserves num_blocks x maxBlockSize in grow-only wasm memory with a 256 MB cap; inflateRaw and inflateRawBatch disagree on zlib-header handling; the README '4x' is unbacked.

## Caveats and trade-offs

The benchmark lives in the sibling repo bbi-js (benchmarks/inflate.bench.ts, MIT, same author) and runs bbi-js's copy of the crate. Its inflate_raw_batch matches inflate-js's except for the bounds and length checks inflate-js added. inflate-js has no benchmark of its own; it is a 5-commit extraction (v1.0.0, August 2026). The harness asserts byte-identical output before timing, and both arms skip the zlib header and the adler32 check, so the comparison does equal work. CPU, Node version and run count beyond 'three runs on one machine' are not stated, and the doc asks readers to 'treat them as an order of magnitude'. The README's '4x' overstates the doc's 2.5-3x summary. The win is inflate in isolation: an older end-to-end whole-genome parseBigWig comparison was only about 5% apart. Raw deflate has no checksum, so corrupt but legal streams decode silently.

Decompression only (inflateRaw and inflateRawBatch), no compression; wasm inlined as base64 in one bundle (about 65 KB) and instantiated lazily; the speedup depends on batching many blocks in one JS-wasm crossing.

## Maintenance

A 5-commit extraction from bbi-js published as 1.0.0 on 2026-08-17; later commits only edit the README (last on 2026-10-11). It has 0 stars and no dependents among the GMOD parsers checked (@gmod/bbi, bgzf-filehandle, bam, tabix, cram and twobit keep their own copies or use pako-esm2). It is MIT-licensed and about 150 lines of Rust, so it is easy to vendor but has little external use behind it yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** bbi-js docs/wasm.md prints wasm-vs-pako timings from the public harness benchmarks/inflate.bench.ts, and the Rust release profile is public in crate/Cargo.toml, but neither the CPU model nor the Node version is stated, and the numbers are first-party (same author), so the tier stays C.
- **Verifier notes:** Real entry with a fair, byte-checked harness. Shortcomings to record: the README's 4x claim exceeds the bbi-js doc's 2.5-3x (derived 2.1-3.2x); CPU and Node version are unstated; the benchmark is in bbi-js, not in inflate-js; and the end-to-end gain is about 5%. Metadata checked: MIT, 0 stars, 5 commits, last commit 2026-10-11.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-117 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/docs/wasm.md>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/benchmarks/inflate.bench.ts>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/crate/src/lib.rs>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/crate/build-wasm.sh>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/src/unzip.ts>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/package.json>
  - <https://github.com/GMOD/bbi-js>
  - <https://github.com/GMOD/inflate-js>
  - <https://github.com/GMOD/inflate-js/commits>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/README.md>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/package.json>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/src/lib.rs>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/build-wasm.sh>
- **Sources the enricher read:**
  - <https://github.com/GMOD/inflate-js>
  - <https://github.com/GMOD/inflate-js/commits/main>
  - <https://github.com/GMOD/inflate-js/tree/main/test>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/README.md>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/package.json>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/src/lib.rs>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/build-wasm.sh>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/src/wrapper.ts>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/package.json>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/crate/webpack.config.js>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/GMOD/inflate-js/HEAD/test/inflate.test.ts>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/docs/wasm.md>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/benchmarks/inflate.bench.ts>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/crate/src/lib.rs>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/src/unzip.ts>
  - <https://raw.githubusercontent.com/GMOD/bbi-js/HEAD/package.json>
  - <https://raw.githubusercontent.com/ebiggers/libdeflate/HEAD/README.md>
  - <https://registry.npmjs.org/@gmod/inflate>
  - <https://registry.npmjs.org/@gmod/bbi>
  - <https://registry.npmjs.org/@gmod/bgzf-filehandle>
  - <https://registry.npmjs.org/hic-straw>
  - <https://registry.npmjs.org/@gmod/cram>
  - <https://registry.npmjs.org/@gmod/bam>
  - <https://registry.npmjs.org/@gmod/tabix>
  - <https://registry.npmjs.org/@gmod/twobit>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gmod/inflate-js`) · [data/wave13/enrich/raw/github_com_gmod_inflate_js.json](../../../data/wave13/enrich/raw/github_com_gmod_inflate_js.json) (enrichment confidence 0.8)

</details>
