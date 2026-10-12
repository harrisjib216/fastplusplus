# crypto-js-wasm (@originjs/crypto-js-wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `WebAssembly (source language not confirmed; repo has a rust directory)` · `MulanPSL-2.0` · 🟡 stale

> crypto-js API with the hash and cipher block functions ported to Rust/WebAssembly; big wins only for SHA-512/384 and SHA-3.

| | |
|---|---|
| **Beats** | crypto-js (JavaScript) |
| **Claimed result** | README text: up to 16x faster than crypto-js. Per-algorithm results exist only as bar charts of average time for 10 loops (values read approximately from the PNGs, derived from page data): Chrome 102 SHA-3 \~103 vs \~1775 ms (\~17x), SHA-512 \~288 vs \~1410 ms (\~4.9x), SHA-384 \~297 vs \~1450 ms, MD5 \~245 vs \~490 ms (\~2x), SHA-256 \~318 vs \~340 ms (\~1.07x), AES \~275 vs \~248 ms (wasm slower); Firefox 101 SHA-512 \~452 vs \~1700 ms (\~3.8x), RIPEMD160 \~422 vs \~1345 ms (\~3.2x), SHA-3 \~138 vs \~555 ms (\~4x), AES \~240 vs \~215 ms (slower); Node 16.6.4 SHA-512 \~300 vs \~1492 ms (\~5x), SHA-3 \~118 vs \~678 ms (\~5.7x), AES \~320 vs \~292 ms (slower). RSA vs jsencrypt in Chrome: about 1.8-2x (4096-bit OAEP \~115 vs \~234 ms, 2048-bit \~17 vs \~34 ms). |
| **Workload** | MD5, SHA-x, AES, RC4 and other hash/cipher operations through crypto-js-wasm versus crypto-js in Chrome 102, Firefox 101 and Node.js 16.6.4, plus RSA versus jsencrypt in Chrome. |
| **Metric** | throughput |
| **Hardware** | Desktop PC with Intel i5-4590, 16 GB RAM, Windows 10 21H2 |
| **Compiler and flags** | Rust via wasm-pack build --release; Cargo release profile opt-level 3, lto = true (rust/\*/Cargo.toml); rustc and wasm-pack versions not stated; wasm binaries pako-deflated and base64-inlined (rust/build-rust.js). |
| **Adoption** | 249 stars |
| **Last commit** | 2024-06-25 |
| **Links** | [repository](https://github.com/originjs/crypto-js-wasm) · [benchmark](https://github.com/originjs/crypto-js-wasm#benchmark) |

## Verdict

First-party bar charts (README; i5-4590, Windows 10 21H2): average time per timed loop of identical crypto-js-style calls on 1 MiB random alphanumeric strings (the public Node harness uses one string, 1 warm-up and 10 timed loops; which harness version and package version produced the 2022 charts is not stated). crypto-js-wasm versus crypto-js: SHA3 \~103 vs \~1775 ms in Chrome 102 (\~17x, a Chrome-specific crypto-js slowdown; \~4x in Firefox 101 and \~5.7x in Node), SHA-512 \~4-5x, MD5 \~1.5-2x, SHA-1/SHA-256/Rabbit/RC4 \~1.05-1.15x, AES slower everywhere; RSA about 2x faster than jsencrypt in Chrome.

## Use it when

- An existing crypto-js code base that must keep byte-identical outputs (WordArray API, OpenSSL-format passphrase AES, crypto-js's Keccak 'SHA3') and spends its time in SHA-512, SHA-384 or SHA3 over inputs of a megabyte or more: about 4-5x (SHA-512/384) and 4-17x (SHA3) in the published charts.
- TripleDES, DES, MD5 or RIPEMD-160 over large strings in legacy crypto-js code, where the charts show roughly 1.3-2x.
- Browser or Node.js code that can await one asynchronous initialisation at startup and then needs synchronous crypto-js-style calls (WebCrypto's SubtleCrypto is async-only).
- Needing crypto-js-style RSA (key generation, OAEP, PSS) in the same API, local use only (see gotchas).

## Skip it when

- AES: slower than crypto-js in all three published charts (Chrome, Firefox, Node); SHA-1, SHA-224/256, Rabbit and RC4 gain only about 1.05-1.15x; the maintainer confirmed in issue #11 that DES decryption was slower than crypto-js in Chrome 116 and blamed the JS-to-wasm copy overhead.
- New code without a crypto-js compatibility constraint: WebCrypto (native AES-GCM, SHA-2, PBKDF2) or a dedicated wasm hash library is much faster; the sibling hash-wasm reports 426 MB/s for SHA-256 on 1 MB inputs, while this library's charts are within 10% of crypto-js there.
- Anything that needs FIPS 202 SHA-3, modern AEAD modes, or the CTRGladman mode with AES/DES/Blowfish (see gotchas); many covered algorithms (MD5, SHA-1, DES, RC4, Rabbit) are legacy and insecure.
- Server-side RSA decryption reachable by attackers: it uses the Rust rsa crate 0.6.1, affected by RUSTSEC-2023-0071 (Marvin timing attack, no patched version).
- Projects needing active maintenance: last commit 2024-06-25 (v1.1.1), seven open issues, and an open report that tree-shaking does not work (issue #17).

## How it is fast

Each algorithm's block loop is a line-by-line Rust port of the crypto-js code, built with wasm-pack (release profile opt-level 3, LTO) and shipped as pako-deflated base64 inside the JS bundle. The JS wrapper keeps crypto-js's buffering, padding and string/WordArray handling, copies the buffered words into wasm linear memory through wasm-bindgen glue and processes every ready block in one call. The large gains come where crypto-js emulates 64-bit arithmetic with X64Word objects: the Rust SHA-512/384 uses native u64, and SHA-3 keeps its 25 lanes as high/low u32 pairs in a stack array rather than heap objects. AES, DES and Blowfish are the same table-driven scalar algorithms as crypto-js; there is no SIMD.

## Compared with alternatives

Pick it over hash-wasm only when you must keep crypto-js's API and outputs (WordArray, OpenSSL-format passphrase AES, crypto-js's Keccak 'SHA3', HMAC/PBKDF2/EvpKDF wiring); for plain hashing hash-wasm is several times faster and has a streaming TypedArray API, and fast-noble-hashes or awasm-noble are the faster route for @noble/hashes users.

## Integration

| | |
|---|---|
| **Form** | module (npm package @originjs/crypto-js-wasm, ESM source built as UMD, wasm binaries inlined as base64) |
| **Dependencies** | pako at runtime (inflates the embedded wasm); package.json also lists 'add' and 'global' as dependencies; rebuilding the wasm needs a Rust toolchain plus wasm-pack |
| **Minimum toolchain** | Any JS runtime with WebAssembly.instantiate; minimum browser and Node versions not documented (charts used Chrome 102, Firefox 101, Node labelled v16.6.4); rustc and wasm-pack versions not stated |
| **Platforms** | Browsers and Node.js with WebAssembly (README); Cloudflare Workers support was requested in issue #22 (closed 2026-02-03) |
| **Thread safety** | not documented; each algorithm keeps one module-wide wasm instance in a static field, so use one instance per JS thread/worker |
| **Drop-in for the baseline** | partial — same API and outputs as crypto-js for the tested paths, but every algorithm needs an awaited loadWasm()/loadAllWasm() first (otherwise 'WASM is not loaded yet' is thrown), and v1.1.1 changed the PBKDF2 defaults to SHA-256 with 250,000 iterations (crypto-js 4.2.0 behaviour, not 4.1.1), while the README still says SHA-1 |

## Gotchas

- Silent no-encryption bug (code reading of rust/aes/src/lib.rs, not executed): the Rust doEncrypt/doDecrypt dispatch on mode._name.to_lowercase() and handle only cbc, ecb, cfb, ofb and ctr; any other mode, including the exported CTRGladman, falls into '_ =&gt; {}' and leaves the data words unchanged, so AES.encrypt(..., { mode: CTRGladman }) returns the padded plaintext as 'ciphertext'. The DES and Blowfish crates have the same fall-through. A round-trip test (like the benchmark's own equality check) would not catch it.
- Block counting in float32 (rust/md5, sha1, sha256, sha3 doCrypt: 'dataSigBytes as f32 / blockSizeBytes as f32'): above 16 MiB of buffered data the count can be off by one. Emulating the Rust f32 arithmetic: a streaming update() with 16,777,279 buffered bytes counts 262,145 SHA-256 blocks instead of 262,144 (a partial block is compressed as full, wrong digest), at 134,217,785 bytes it indexes past the slice (wasm trap), and a one-shot SHA3-512 of 134,217,864 bytes drops the final padded block. One-shot MD5/SHA-1/SHA-256 stay exact below about 1 GiB; the 1 MiB benchmark is unaffected.
- Compatibility quirks inherited from crypto-js: 'SHA3' pads with 0x01 (original Keccak), so it does not match FIPS 202 SHA3-512; CTR mode increments only the last 32-bit counter word; AES uses lookup tables (SubMix/SBOX), so it is not constant-time. RSA defaults to a 1024-bit key when generating (docs/rsa.md).
- Every _process call copies the whole buffered JS word array into wasm linear memory and copies state back; wasm memory grows to the largest message and never shrinks. String-to-WordArray conversion, padding and splicing stay in JS, which is why the cheap algorithms barely move (Node chart, derived from page data: wasm MD5 \~270 ms and SHA-256 \~330 ms per loop against \~118 ms for wasm SHA3-512, so glue, not the Rust kernel, dominates).

## Known shortcomings

- Numbers exist only in bar charts (harness in originjs/WASM-benchmark); the 16x headline rests on a Chrome 102 SHA-3 outlier, AES is slower than crypto-js everywhere and most hashes are about 1.1x; source is Rust. Stale since 2024-06-25.
- Correctness bugs found by reading the Rust code (not executed): AES with any mode outside cbc/ecb/cfb/ofb/ctr, including the exported CTRGladman, falls into a '_ =&gt; {}' arm and returns the padded plaintext as 'ciphertext' (the DES and Blowfish crates share the fall-through); MD5, SHA-1, SHA-256 and SHA-3 count blocks in f32 (dataSigBytes as f32), so a streaming update of 16,777,279 buffered bytes gives a wrong digest, 134,217,785 bytes traps on a slice index, and a one-shot SHA3-512 of 134,217,864 bytes drops its final block (the 1 MiB benchmark is unaffected). 'SHA3' is Keccak (0x01 padding); rsa 0.6.1 is hit by RUSTSEC-2023-0071; in the Node chart wasm MD5 and SHA-256 are slower than wasm SHA3, so JS glue dominates the time.

## Caveats and trade-offs

Numbers are bar charts only; the headline 16x rests on crypto-js SHA-3 in Chrome 102 (\~1775 ms there vs \~555 ms in Firefox), a Chrome-specific slowdown of the JS baseline; elsewhere SHA-3 gains are 4-6x. AES is slower than crypto-js in all three charts, and SHA-1/SHA-224/SHA-256/Rabbit/RC4 gain only about 1.05-1.15x in Chrome and Node, because the crypto-js-compatible API keeps string-to-WordArray conversion on the JS side. Harness (public in originjs/WASM-benchmark, packages/benchmark_base/src/benchmarkTests): 1 MiB random strings per item, warm-up and benchmark loop counts as parameters, same API calls for both libraries; which crypto-js-wasm version produced the 2022 charts is not stated (benchmark_base depends on ^1.1.0). Old browser and Node versions (2022). Wasm source language is Rust (wasm-pack crates in rust/). Many covered algorithms (MD5, SHA-1, DES, RC4, Rabbit) are legacy and insecure. Mulan PSL v2 is an OSI-approved permissive licence.

Same API as crypto-js but initialisation is async (loadWasm) and the wasm binaries are base64-embedded. Covers 15+ algorithms plus RSA.

## Maintenance

Stale since 2024-06-25 (v1.1.1) with seven open issues; Mulan PSL v2 (OSI-approved permissive), usable as a crypto-js speed-up for 64-bit hashes, but the AES mode fall-through and float32 block counting found in the source are unfixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party bar charts (i5-4590, Chrome 102, Firefox 101, Node 16.6.4) from a public harness (originjs/WASM-benchmark packages/benchmark_base/src/benchmarkTests/\*WasmTest.ts) against crypto-js; numbers are chart bars only, the Rust toolchain version is unstated and the benchmarked library version is not pinned, so C.
- **Verifier notes:** Charts and README text checked; benchmark code located in originjs/WASM-benchmark (0 stars). Shortcomings: chart-only numbers, 16x headline from one Chrome 102 SHA-3 outlier, AES slower than crypto-js everywhere, most hashes \~1.1x, toolchain versions unstated, last commit 2024-06-25 (stale). Record's language field should read Rust compiled to WebAssembly (not a correctable field).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/originjs/crypto-js-wasm>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/HEAD/README.md>
  - <https://github.com/originjs/crypto-js-wasm/commits>
  - <https://github.com/originjs/crypto-js-wasm/tree/main/rust>
  - <https://github.com/originjs/crypto-js-wasm/tree/main/benchmark>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_chrome.png>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_firefox.png>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_nodejs.png>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_chrome_rsa.png>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/README.md>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/build-rust.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha256/Cargo.toml>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/LICENSE>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/package.json>
  - <https://github.com/originjs/WASM-benchmark>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/README.md>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages/benchmark_base>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/package.json>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages/benchmark_base/src>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages/benchmark_base/src/benchmarkTests>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/sha3WasmTest.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/aesWasmTest.ts>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/README.md>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/package.json>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/README.md>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/build-rust.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha256/Cargo.toml>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/index.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/algo/hash/sha256.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/algo/hash/sha256_bg.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/algo/hash/sha3.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/algo/hash/md5.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/algo/pbkdf2/pbkdf2.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/encryption/aes.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/utils/wasm-utils.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/core/hasher.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/core/core.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/core/cipher-core.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/mode/mode-ctr-gladman.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/mode/mode-ctr.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/src/mode/mode-ecb.js>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha256/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha3/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha512/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/aes/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/md5/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/sha1/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/ripemd160/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/des/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/blowfish/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/rc4/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/rabbit/src/lib.rs>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/rust/rsa/Cargo.toml>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/docs/rsa.md>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_chrome.png>
  - <https://raw.githubusercontent.com/originjs/crypto-js-wasm/main/benchmark/benchmark_nodejs.png>
  - <https://github.com/originjs/crypto-js-wasm/tree/main/test>
  - <https://github.com/originjs/crypto-js-wasm/tree/main/rust>
  - <https://github.com/originjs/crypto-js-wasm/commits/main>
  - <https://github.com/originjs/crypto-js-wasm/issues?q=is%3Aissue>
  - <https://github.com/originjs/crypto-js-wasm/issues/7>
  - <https://github.com/originjs/crypto-js-wasm/issues/8>
  - <https://github.com/originjs/crypto-js-wasm/issues/11>
  - <https://github.com/originjs/crypto-js-wasm/issues/12>
  - <https://github.com/originjs/crypto-js-wasm/issues/14>
  - <https://github.com/originjs/crypto-js-wasm/issues/19>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/package.json>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/index.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/sha3WasmTest.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/aesWasmTest.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_base/src/benchmarkTests/sha256WasmTest.ts>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages>
  - <https://github.com/originjs/WASM-benchmark/tree/master/packages/benchmark_base/src>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_nodejs/package.json>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_nodejs/src/index.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_nodejs/src/benchmarkDatasets.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_nodejs/src/runBenchmark.ts>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_browser/package.json>
  - <https://raw.githubusercontent.com/originjs/WASM-benchmark/master/packages/benchmark_browser/src/main.ts>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/rsa/RUSTSEC-2023-0071.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/originjs/crypto-js-wasm`) · [data/wave13/enrich/raw/github_com_originjs_crypto_js_wasm.json](../../../data/wave13/enrich/raw/github_com_originjs_crypto_js_wasm.json) (enrichment confidence 0.75)

</details>
