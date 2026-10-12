# ttf2woff2-wasm (@0x6b/ttf2woff2-wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust TTF-to-WOFF2 converter compiled to WebAssembly for Node; 2.0-2.7x faster than the ttf2woff2 npm package at Brotli quality 11.

| | |
|---|---|
| **Beats** | nfroidure/ttf2woff2 v8 (vendored 2013-2015 C++ Brotli encoder and woff2 snapshot; may have run its Emscripten fallback rather than the node-gyp native build) |
| **Claimed result** | WarpnineSans-Regular.ttf (269.1 KB): native avg 1331 ms vs wasm avg 500 ms (2.7x faster); NotoSansJP-Medium.ttf (5.5 MB): 19039 ms vs 9756 ms (2.0x faster). The README's '2.2x / 2.6x less memory' figures are JS heap deltas (44.8 KB vs 20.6 KB, 30.0 KB vs 11.4 KB) and do not measure conversion memory. Installed size 968 KB vs 11 MB. |
| **Workload** | TTF to WOFF2 conversion at Brotli quality 11 on both sides of two fonts (269.1 KB WarpnineSans-Regular and 5.5 MB NotoSansJP-Medium), average of 10 timed calls after 3 warmups per implementation (bench/benchmark.cjs). |
| **Metric** | latency |
| **Hardware** | Apple M1 Max |
| **Compiler and flags** | wasm side: Cargo release profile opt-level="s", lto=true (Cargo.toml), built via cargo xtask; rustc, wasm-bindgen and Node versions not stated; baseline built by node-gyp defaults |
| **Adoption** | 1 star |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/0x6b/ttf2woff2-wasm) · [benchmark](https://github.com/0x6b/ttf2woff2-wasm#benchmark) |

## Verdict

First-party bench/benchmark.cjs on an Apple M1 Max (Node, rustc and wasm-bindgen versions not stated): average of 10 synchronous calls after 3 warmups at Brotli quality 11, ttf2woff2-wasm took 500 ms versus 1331 ms for nfroidure ttf2woff2 v8.0.0 on a 269 KB font (2.7x) and 9756 ms versus 19039 ms on the 5.5 MB NotoSansJP-Medium (2.0x). The baseline's 'native' path is a node-gyp addon of a 2013-2015 woff2 and C++ Brotli snapshot that may have fallen back to Emscripten unreported, and output sizes were not compared.

## Use it when

- Node.js build pipelines (font subsetting, icon-font generators, static-site builds) that call ttf2woff2 on TrueType fonts and suffer from node-gyp compile failures or the 11 MB install.
- CI images or serverless bundles without a C++ toolchain, where the native ttf2woff2 path would silently fall back to its Emscripten -O2 build anyway.
- Large CJK TrueType fonts at quality 11, where the author's run shows 9.8 s against 19.0 s for a 5.5 MB NotoSansJP.
- Projects that want MIT OR Apache-2.0 licensing and a dependency-free npm package.

## Skip it when

- CFF-flavoured OpenType (.otf, 'OTTO'), TrueType collections (.ttc) or Apple 'true' fonts: the Rust parser accepts only sfnt version 0x00010000 and returns UnsupportedFormat, while Google's woff2 in the baseline handles collections and non-glyf fonts.
- Browsers, Deno or ESM-only bundles: the package is built with wasm-pack --target nodejs, which emits CommonJS that loads the .wasm file from disk.
- When byte-identical output to Google's woff2 is required: the README warns output size differs and asks users to verify fonts before production; the core crate points to woofwoof or bodoni/woff for byte compatibility or decompression.
- Large-font batch jobs where native code is allowed: the core crate's native CLI with -t 0 (multithreaded Brotli) encodes NotoSansJP at q11 in 0.96 s on an Apple M4 Pro, far faster than any single-threaded wasm call; multithreading is silently disabled on wasm.
- Latency-sensitive servers calling it on the main thread: the call is synchronous and blocks the event loop for 0.5 s (269 KB font) to about 10 s (5.5 MB font) at quality 11.

## How it is fast

The work is the WOFF2 glyf/loca transform followed by Brotli quality-11 compression (BROTLI_MODE_FONT, default 22-bit window) done by the Rust brotli crate v9, a port of Google's modern C Brotli encoder, compiled to wasm32 with opt-level "s" and LTO through wasm-pack. The baseline it beats vendors a much older encoder: nfroidure/ttf2woff2's csrc/ holds a 2013-2015 snapshot of Google's woff2 plus the pre-C-rewrite C++ Brotli encoder (namespace brotli, BrotliCompressBuffer, encode_parallel.cc, streams.cc). Most of the measured gap is therefore a newer compressor implementation, not WebAssembly beating native code; the wasm build has no SIMD and no threads.

## Compared with alternatives

Among catalogued wasm libraries it is the only font converter; like libxml2-wasm it replaces a node-gyp native binding with a toolchain-free wasm package, and like zip.js's wasm zlib codec its speed comes from the compressor implementation, so pick it when the job is TrueType-to-WOFF2 in Node and native builds are a nuisance.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (npm package ships the .wasm, wasm-bindgen glue and a CommonJS wrapper); building from source needs Rust, wasm-pack and the ttf2woff2 0.13 and brotli 9 crates |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+) and wasm-pack to build; Node.js runtime with CommonJS require (minimum Node version not documented) |
| **Platforms** | Node.js on any OS/CPU (wasm32, no SIMD, single-threaded); not built for browsers |
| **Thread safety** | not documented; synchronous single-threaded call, each worker_thread loads its own module instance |
| **Drop-in for the baseline** | partial: same call signature and exports for TrueType input, but OTF/CFF, TTC and 'true'-flavoured fonts are rejected, output bytes and size differ, and it is CommonJS for Node only |

## Gotchas

- Harness flaw in bench/benchmark.cjs: the 'native' row is whatever nfroidure/ttf2woff2 loaded. Its install script swallows node-gyp failures into builderror.log and src/index.ts silently falls back to the Emscripten build (debug-only log), and the benchmark sets no TTF2WOFF2_VERSION, so the row may not be native at all.
- The baseline is not current Google woff2 plus Brotli 1.x: it vendors a 2013-2015 C++ Brotli encoder and woff2 snapshot, so the 2.0-2.7x says little about wasm versus a modern native build; the benchmark also never compares output sizes or validates output, so a faster but weaker or stronger compressor is not ruled out.
- The README's '2.2x / 2.6x less memory' figures are process.memoryUsage().heapUsed deltas across the timed loop (tens of KB); they exclude wasm linear memory and native malloc and do not measure conversion memory.
- Only TrueType-outline fonts are accepted (sfnt version 0x00010000); the README's migration snippet still names ttf2woff2 ^3.0.0 and @0x6b/ttf2woff2-wasm ^0.10.3, and js/package.json says 0.13.1 while Cargo.toml and npm are at 0.13.2.

## Known shortcomings

- The memory claim is invalid (heapUsed delta only); the "native" baseline is unverified (node-gyp with a silent Emscripten fallback); no output-size check; the win comes from the Rust Brotli encoder, not from wasm.
- Enricher: the baseline nfroidure/ttf2woff2 v8 vendors a 2013-2015 C++ Brotli encoder plus an old woff2 snapshot, so the 2.0-2.7x is mostly the newer compressor rather than wasm; the install script swallows node-gyp failures and index.ts silently falls back to the Emscripten build while the bench sets no TTF2WOFF2_VERSION, so the 'native' row is unproven; no output-size or validity check; memory figures are JS heap deltas; the Rust parser accepts only sfnt 0x00010000 (no OTF/CFF, TTC or 'true') and the package is Node CommonJS only. Retiered to D.

## Caveats and trade-offs

First-party, 1-star wrapper; the conversion core is the author's pure-Rust crate 0x6b/ttf2woff2 (Rust brotli crate v9), exposed through wasm-bindgen. Both sides compress at Brotli quality 11 (the wasm wrapper defaults to 11), but the benchmark neither compares output sizes nor validates the output, and the README warns the output differs in size from nfroidure/ttf2woff2. The 'native' label is unverified: ttf2woff2's npm install script runs node-gyp and silently falls back to an Emscripten build on failure, and the script does not report which path loaded. The 'less memory' figures are process.memoryUsage().heapUsed deltas, which exclude native-addon malloc and wasm linear memory, so they say nothing about real memory use. The speedup comes mostly from the Rust Brotli encoder, not from wasm: the core crate's README shows Rust q11 at 3.25 s versus fonttools (C brotli) at 9.86 s on the same NotoSansJP font with near-identical output size (Apple M4 Pro). Single machine, Node version not stated.

Zero native dependencies and a drop-in API for ttf2woff2; WOFF2 output size can differ because a different Brotli implementation is used (the README warns to verify output fonts).

## Maintenance

Active (20 commits, npm 0.13.2 published 2026-07-12, 1 star; the core crate has no issues filed), dual MIT/Apache-2.0 and small enough to vendor, but a one-author wrapper whose core crate was written with AI coding assistants and validated only against fonttools, so check output fonts before shipping.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README numbers against nfroidure ttf2woff2 v8.0.0 on an Apple M1 Max, with the harness public in bench/benchmark.cjs (10 timed calls after 3 warmups). rustc, wasm-bindgen, Node versions and the baseline's build are not stated, so not A.
- **Retiered** C to D: Enricher (2026-10-12): no valid wasm-vs-native measurement. The baseline nfroidure/ttf2woff2 v8 vendors a 2013-2015 C++ Brotli encoder and an old woff2 snapshot, so the 2.0-2.7x mostly measures compressor versions; the 'native' row is unproven because the baseline's install script swallows node-gyp failures and index.ts silently falls back to its Emscripten build while bench/benchmark.cjs sets no TTF2WOFF2_VERSION; output sizes and validity are never compared.
- **Verifier notes:** The README numbers match the bench/benchmark.cjs output format exactly, and the baseline is the named incumbent npm package. Shortcomings: memory claim invalid (JS heap delta only), 'native' baseline path unverified (node-gyp with silent Emscripten fallback), no output-size or correctness check, and the win comes from the Rust Brotli encoder rather than wasm. The core crate 0x6b/ttf2woff2 (11 stars) may be the better catalog target for native use.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/0x6b/ttf2woff2-wasm>
  - <https://github.com/0x6b/ttf2woff2-wasm/commits>
  - <https://github.com/0x6b/ttf2woff2-wasm/tree/main/js>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/bench/benchmark.cjs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/js/index.js>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/js/package.json>
  - <https://github.com/0x6b/ttf2woff2>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/Cargo.toml>
  - <https://github.com/nfroidure/ttf2woff2>
  - <https://registry.npmjs.org/ttf2woff2>
- **Sources the enricher read:**
  - <https://github.com/0x6b/ttf2woff2-wasm>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/bench/benchmark.cjs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/js/index.js>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/js/index.d.ts>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/js/package.json>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2-wasm/HEAD/xtask/src/main.rs>
  - <https://registry.npmjs.org/@0x6b%2Fttf2woff2-wasm>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/README.md>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/woff2/mod.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/woff2/encoder.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/woff2/brotli_quality.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/woff2/sfnt.rs>
  - <https://raw.githubusercontent.com/0x6b/ttf2woff2/HEAD/src/error.rs>
  - <https://github.com/0x6b/ttf2woff2/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/README.md>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/package.json>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/binding.gyp>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/csrc/addon.cc>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/csrc/woff2/woff2_enc.cc>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/csrc/enc/encode.h>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/csrc/enc/backward_references.cc>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/install/try-build.js>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/jssrc/index.js>
  - <https://raw.githubusercontent.com/nfroidure/ttf2woff2/HEAD/CHANGELOG.md>
  - <https://registry.npmjs.org/ttf2woff2>
  - <https://github.com/nfroidure/ttf2woff2/issues?q=is%3Aissue+woff2+update>
  - <https://github.com/nfroidure/ttf2woff2/commits/master/csrc/enc>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/0x6b/ttf2woff2-wasm`) · [data/wave13/enrich/raw/github_com_0x6b_ttf2woff2_wasm.json](../../../data/wave13/enrich/raw/github_com_0x6b_ttf2woff2_wasm.json) (enrichment confidence 0.72)

</details>
