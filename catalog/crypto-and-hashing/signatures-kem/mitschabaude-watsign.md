# watsign

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `WebAssembly (WAT) + JavaScript` · `MIT` · 🟡 stale

> WebAssembly port of TweetNaCl Ed25519 sign/verify for browsers, Node and Deno; \~4-6x faster than tweetnacl-js warmed up.

| | |
|---|---|
| **Beats** | tweetnacl-js (Ed25519 sign/verify) |
| **Claimed result** | 4-6x faster than tweetnacl-js warmed up, up to 33x faster on cold start after page load; 1.2-3x faster than noble-ed25519 warmed up, up to 17x on cold start |
| **Workload** | Ed25519 sign and verify of short and long messages, warm (50x average after 50x warmup) and cold-start timings, in-browser via puppeteer |
| **Metric** | latency |
| **Hardware** | Intel i7-10700, Chromium 93 (via puppeteer) |
| **Adoption** | 14 stars; \~154 npm downloads/month (npm, 2026-08-27 to 2026-09-25) |
| **Last commit** | 2024-04-15 |
| **Links** | [repository](https://github.com/mitschabaude/watsign) · [benchmark](https://github.com/mitschabaude/watsign/blob/main/README.md) |

## Verdict

Setup: Intel i7-10700, Chromium 93 driven by puppeteer 10.4.0 via chrode 0.3.3, mean of 50 runs after 50 warm-ups, in October 2021. watsign signed and verified a 10-byte message in 0.67/1.11 ms and an \~80 KB message in 0.96/1.28 ms. tweetnacl-js 1.0.3 took 2.86/5.65 and 5.70/7.21 ms (4.3-5.9x slower) and noble-ed25519 1.2.6 took 1.00/3.09 and 1.27/3.24 ms (1.3-2.8x slower). The '33x' and '17x' cold-start figures are single first-call samples (tweetnacl sign of the long message at 43.88 ms vs 1.32 ms; noble short sign at 53.17 ms vs 2.99 ms).

## Use it when

- You use tweetnacl-js only for Ed25519 signatures and must support runtimes without native Web Crypto Ed25519 (Chrome before 137, Firefox before 129, Safari before 17)
- Cold-start-sensitive pages that sign or verify once right after load (e.g. an auth token): the README shows first-call sign/verify of 1.3-3 ms vs 8-44 ms for tweetnacl-js
- Verifying signatures over large payloads (tens of KB) in the browser, where native SHA-512 helps: \~5.6-5.9x vs tweetnacl-js on an \~80 KB message
- Bundle-size-sensitive front ends that need only signing: 7.4 kB min+gz vs 10.6 kB for tweetnacl-js (which also includes box/secretbox)
- You want TweetNaCl's constant-time design (no secret-dependent branches or memory access), not the BigInt field arithmetic of noble-ed25519 v1

## Skip it when

- Modern targets with native Web Crypto Ed25519 sign/verify (Chrome 137+, Firefox 129+, Safari 17+, Node 16.17+, Deno 1.26+); watsign was never benchmarked against these native paths
- Strict-CSP pages or Chrome MV3 extensions: the watever-js-wrapper glue calls indirect eval on the JS import strings, and issue #4 (open) reports it failing in MV3
- Synchronous code paths, X25519/box/secretbox, batch verification or other curves: none are provided
- Choosing between it and today's @noble/ed25519 (3.2.0): the noble comparison used noble-ed25519 1.2.6 from 2021, so the '1.2-3x faster than noble' claim is outdated
- Consensus-critical or compliance-driven use: there is one maintainer, the project has been stale since 2024-04, it has no audit, it gets \~154 npm downloads/month, and verification inherits TweetNaCl's non-strict rules

## How it is fast

It runs the same TweetNaCl algorithms: 16-limb radix-2^16 field elements mod 2^255-19, and a constant-time cswap double-and-add over extended twisted Edwards coordinates for both fixed-base and variable-base scalar multiplication, with no precomputed tables. The gain comes from moving limb arithmetic from tweetnacl-js's Float64Array math to Wasm i64 integer ops. The 16x16 schoolbook field multiply is fully unrolled, which the source calls 'the hottest path of the entire library'. SHA-512 is delegated to the native Web Crypto or Node implementation instead of JS, which widens the gap on long messages. Shipping precompiled Wasm avoids JIT warm-up, hence the large first-call ratios.

## Compared with alternatives

The catalogued siblings (ENG25519 AVX-512IFMA, SUPERCOP amd64-64-24k Ed25519, libsecp256k1, UltrafastSecp256k1) are native C or assembly and cannot run inside a browser or Deno sandbox. Pick watsign only when Ed25519 must run in JS or Wasm; on servers, use those native libraries or the runtime's built-in crypto.

## Integration

| | |
|---|---|
| **Form** | module (ESM-only npm package; Wasm embedded as base64 in the JS; Deno can import mod.js from raw.githubusercontent.com or use npm:watsign) |
| **Dependencies** | watever-js-wrapper ^0.3.2 at runtime, plus the platform's Web Crypto (crypto.subtle SHA-512, getRandomValues) or node:crypto |
| **Minimum toolchain** | Node &gt;= 16 (package engines); ESM ('type': 'module'); browsers need WebAssembly and Web Crypto SHA-512; rebuilding needs the author's watever WAT bundler (0.5.2) |
| **Platforms** | Any JS runtime with WebAssembly: modern browsers, Node &gt;= 16, Deno |
| **Thread safety** | Not documented. There is one Wasm instance per imported module copy, and concurrent async calls interleave on its linear memory through watever's keep/free allocator; each worker loads its own copy. |
| **Drop-in for the baseline** | partial — keys and signatures are byte-compatible with tweetnacl-js nacl.sign.detached (the tests check identical signatures), but every call is async, the names differ (sign = nacl.sign.detached), and only the high-level detached-signing API exists |

## Gotchas

- sign() does not check the secret-key length: the 64-byte check exists only as a comment in sign.wat. Passing the wrong value (e.g. the whole key pair) gives 'RuntimeError: memory access out of bounds' (issue #3) instead of tweetnacl's 'bad secret key size'. verify and the keyPair functions do validate sizes.
- verify ports TweetNaCl's check (unpack A, reduce H, compute [H](-A) + [S]B, compare with R) without rejecting non-canonical S &gt;= L, so it is not a strict RFC 8032 verifier and accepts malleated signatures just as tweetnacl-js does.
- Tests only cover two fixed identities cross-checked against tweetnacl-js; there are no RFC 8032 or Wycheproof vectors. Version 0.1.6 fixed a byte-widening bug in i8_to_i64 that had corrupted the hash reduction, so avoid anything older than 0.1.6 (latest is 0.1.9).
- Timing uses performance.now() around awaited calls, so the async hop through the Web Crypto promise is included; cold-start numbers are single samples that the README itself says vary between runs.

## Known shortcomings

- WebAssembly/JS only. The 33x cold-start figure is a single sample; warm gain is 4-6x over tweetnacl-js (a slow pure-JS baseline). No engine flags; \~154 npm downloads/month; stale.
- Benchmark is from Oct 2021 (Chromium 93) against noble-ed25519 1.2.6 (current @noble/ed25519 is 3.2.0) and never against native Web Crypto Ed25519 (now in Chrome 137+, Firefox 129+, Safari 17+, Node 16.17+). sign() lacks a secret-key length check (WASM out-of-bounds error, #3); verify lacks the S&lt;L check, so malleated signatures are accepted; the wrapper uses eval (breaks strict CSP / Chrome MV3, #4). Only 2 fixed test identities, no RFC 8032 vectors.

## Caveats and trade-offs

First-party benchmark from the project's own repo. The harness is test/performance.js, which runs test/test-watsign.js, test/test-tweetnacl-js.js and test/test-noble-ed25519.js via chrode (headless Chromium), with timing in test/perf.js. The Performance section dates from October 2021 (commit 'cleaner perf test, add comparison with noble-ed25519', 2021-10-06) on Chromium 93 and has not been revalidated on modern V8 or hardware. The 'up to 33x' figure comes from a single cold-start sample (sign long msg: 43.88 ms vs 1.32 ms), and the README says cold-start runs vary between runs. The steady-state figure is 4-6x (derived from page data: 4.3x sign short, 5.1x verify short, 5.9x sign long, 5.6x verify long). Against noble-ed25519, page data gives 1.3-2.8x warm, which the README rounds to 1.2-3x. Last commit 2024-04-15 (v0.1.9), about 2.4 years before today.

JS/WebAssembly only, not usable directly from C++; ports the TweetNaCl algorithm rather than a novel design; API is async-only because of WebAssembly plus native SHA-512; signing/verification only, no encryption support.

## Maintenance

Stale: the WAT core last changed in October 2021 (v0.1.6), and the latest release, v0.1.9 (2024-04-15), only fixed TypeScript exports. Two issues are open, including the CSP/MV3 breakage. It is MIT-licensed and small, but edits require the author's watever toolchain, and native Web Crypto Ed25519 now covers most of its use case.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section gives first-party timings against tweetnacl-js and noble-ed25519 on an Intel i7-10700 in Chromium 93. The harness is public (test/performance.js runs test-watsign.js, test-tweetnacl-js.js and test-noble-ed25519.js through chrode, with timing in test/perf.js), but there are no engine flags or build settings, so this is C, not A.
- **Verifier notes:** The claims match the README exactly and the ratios check out against the listed timings. The only real fix is the benchmark script path: the record's caveats pointed to src-experiments/test/, but the scripts live in test/. Metadata confirmed: MIT, not a fork, not archived, 14 stars, last commit 2024-04-15, so stale is correct.
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/mitschabaude/watsign>
  - <https://github.com/mitschabaude/watsign/blob/main/README.md>
  - <https://github.com/mitschabaude/watsign/blob/main/test/performance.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/perf.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/test-tweetnacl-js.js>
  - <https://github.com/mitschabaude/watsign/blob/main/package.json>
  - <https://github.com/mitschabaude/watsign/commits/main/README.md>
  - <https://api.npmjs.org/downloads/point/last-month/watsign>
  - <https://registry.npmjs.org/watsign>
- **Sources the enricher read:**
  - <https://github.com/mitschabaude/watsign>
  - <https://github.com/mitschabaude/watsign/blob/main/README.md>
  - <https://github.com/mitschabaude/watsign/blob/main/package.json>
  - <https://github.com/mitschabaude/watsign/blob/main/package-lock.json>
  - <https://github.com/mitschabaude/watsign/blob/main/index.d.ts>
  - <https://github.com/mitschabaude/watsign/blob/main/src/crypto.js>
  - <https://github.com/mitschabaude/watsign/blob/main/src/crypto.node.js>
  - <https://github.com/mitschabaude/watsign/blob/main/src/sign.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/math25519.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/math25519/multiply.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/math25519/select.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/sign/scalarmult.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/sign/modL.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/src/bytes_utils.wat>
  - <https://github.com/mitschabaude/watsign/blob/main/build/build.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/perf.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/performance.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/test-watsign.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/test-tweetnacl-js.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/test-noble-ed25519.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/simple-test.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/helper.js>
  - <https://github.com/mitschabaude/watsign/blob/main/test/identity.js>
  - <https://github.com/mitschabaude/watsign/issues?q=is%3Aissue>
  - <https://github.com/mitschabaude/watsign/issues/3>
  - <https://github.com/mitschabaude/watsign/issues/4>
  - <https://github.com/mitschabaude/watsign/pulls?q=is%3Apr>
  - <https://github.com/mitschabaude/watsign/commits/main>
  - <https://github.com/mitschabaude/watsign/commit/c9a12af0a7e5c3447438884f9cc17f84d240f3d8>
  - <https://github.com/mitschabaude/watever/blob/main/watever-js-wrapper/wrap.js>
  - <https://registry.npmjs.org/watsign>
  - <https://api.npmjs.org/downloads/point/last-month/watsign>
  - <https://registry.npmjs.org/@noble/ed25519/latest>
  - <https://registry.npmjs.org/tweetnacl/latest>
  - <https://api.npmjs.org/downloads/point/last-month/tweetnacl>
  - <https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/SubtleCrypto.json>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mitschabaude/watsign`) · [data/wave7/enrich/raw/github_com_mitschabaude_watsign.json](../../../data/wave7/enrich/raw/github_com_mitschabaude_watsign.json) (enrichment confidence 0.75)

</details>
