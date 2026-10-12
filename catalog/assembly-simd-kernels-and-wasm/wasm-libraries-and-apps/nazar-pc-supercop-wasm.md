# supercop.wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (orlp/ed25519 compiled to WebAssembly with Emscripten, JavaScript wrapper)` · `0BSD` · 🔴 abandoned

> orlp/ed25519 compiled to a size-optimized WebAssembly module; about 10x faster than pure-JS @noble/curves 0.7.0 for Ed25519.

| | |
|---|---|
| **Beats** | @noble/curves 0.7.0 (pure JavaScript ed25519) and node:crypto ed25519 (native OpenSSL) in the third-party berith benchmark; tweetnacl-js and a native SUPERCOP build are not measured |
| **Claimed result** | berith README Node table (Apple M1 Max): supercop.wasm 5.0.1 187.96 us/iter; @noble/curves 0.7.0 1.99 ms/iter (about 10.6x slower than supercop.wasm, derived from page data); node:crypto native 152.67 us/iter with unserialized keys (supercop.wasm about 1.23x slower, derived) and 555.61 us/iter serialized (supercop.wasm about 3.0x faster, derived); berith (Wasm) 281.68 us/iter, which the README itself reports as '0.67x faster than supercop.wasm'. The supercop.wasm README makes no speed claim (only 'multiple times smaller' than supercop.js). |
| **Workload** | berith repo src/node/bench/index.bench.ts on Node v18.12.1: per iteration generate an ed25519 keypair, sign a 1,024-byte message and verify the signature, 1,000 samples, average time per iteration. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max (aarch64-apple-darwin), Node v18.12.1 |
| **Compiler and flags** | Measured artifact is the prebuilt npm supercop.wasm 5.0.1; its build in gulpfile.ls runs emcc on orlp/ed25519 with -Oz --llvm-lto 1 --closure 1 -s WASM=1 -s NO_EXIT_RUNTIME=1 -s NO_FILESYSTEM=1 (size-optimized; Emscripten version not stated). The benchmark is JavaScript run with Node v18.12.1. |
| **Adoption** | 13 stars; npm supercop.wasm 5.0.1 (2018-02-24) is the latest version |
| **Last commit** | 2018-02-24 |
| **Links** | [repository](https://github.com/nazar-pc/supercop.wasm) · [benchmark](https://raw.githubusercontent.com/hazae41/berith/HEAD/README.md) |

## Verdict

In a third-party benchmark in the competing hazae41/berith repo (Node v18.12.1, Apple M1 Max, 1,000 samples of keygen + sign + verify on a 1,024-byte message), supercop.wasm 5.0.1 took 187.96 us per iteration against 1.99 ms for pure-JS @noble/curves 0.7.0 (about 10.6x, derived from page data); native node:crypto was faster at 152.67 us with KeyObject keys and slower at 555.61 us when keys were serialized.

## Use it when

- Browser or Node code that needs Ed25519 sign/verify on raw key bytes and is currently on an old pure-JS library such as @noble/curves 0.7.x or supercop.js
- Bundles where module size matters: the wasm build is size-optimized and the README says it is multiple times smaller than supercop.js
- Workloads that already store keys as raw bytes, where node:crypto would need a KeyObject import per call (the serialized node:crypto row was about 3x slower in the berith table)
- Projects already using the supercop.js API that want a faster, smaller replacement with the same key format

## Skip it when

- Node with KeyObject-held keys: native node:crypto measured 152.67 vs 187.96 us per keygen+sign+verify in the same table
- Interoperating with libsodium, tweetnacl or RFC 8032 seed-based keys: the 64-byte secretKey is the clamped SHA-512 expansion of the seed, not seed||publicKey, so secret keys are not interchangeable (orlp/ed25519 issue #35)
- Consensus or strict-verification settings: verify only rejects signatures whose top three bits of S are set, it does not check S &lt; L or reject small-order or non-canonical public keys, so it accepts malleable signatures that strict verifiers reject
- Code that needs maintenance, audits or side-channel guarantees: last commit and npm release 5.0.1 date from 2018-02-24, with no constant-time claim in the README
- Signing very large messages in one call: the build does not set ALLOW_MEMORY_GROWTH, so the message must fit in Emscripten's fixed default heap (limit not documented)

## How it is fast

The speed comes from running the ref10-derived C field and group arithmetic of orlp/ed25519 (radix-2^25.5 field elements, precomputed base-point tables for ge_scalarmult_base) as WebAssembly instead of JavaScript BigInt or number arithmetic. The JS wrapper only copies inputs into the wasm heap with malloc, calls the exported C function and copies the result out. The build is tuned for size (-Oz, LTO, Closure), not speed.

## Compared with alternatives

No other Ed25519 or signature library is catalogued in this category; hash-wasm is the closest wasm crypto sibling but covers hashes only, so pick supercop.wasm when you need signatures in JS and can accept an old, unaudited code base.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (prebuilt src/supercop.js and wasm in the npm package); rebuilding needs Emscripten, gulp and LiveScript plus a vendored orlp/ed25519 checkout |
| **Minimum toolchain** | Any engine with WebAssembly support (Node 8+ era, modern browsers); Emscripten version used for the published build is not documented |
| **Platforms** | any WebAssembly host (Node, browsers); no SIMD or threads |
| **Thread safety** | not documented; each module instance keeps a shared list of allocated pointers in JS, so use one instance per thread or worker |
| **Drop-in for the baseline** | partial — same operations as @noble/curves ed25519 but a different API (ready callback, seed-to-keypair, sign takes the public key) and an incompatible 64-byte secret-key format |

## Gotchas

- sign(msg, publicKey, secretKey) trusts the caller's publicKey: the nonce depends only on the secret key and message, so signing the same message under two different public keys yields two signatures with the same R and lets an attacker recover the private scalar; always pass the matching key.
- Secret keys and messages are copied into the wasm heap and released with free() without being zeroed, so key material can remain in linear memory after a call.
- Benchmark harness: the berith bench at HEAD (src/node/bench/index.bench.ts) has no serialized node:crypto row, so the 555.61 us figure came from an older harness version; every iteration mixes RNG, keygen, sign and verify of a 1,024-byte message, and the verify result is never checked.
- The published wasm is built with -Oz (size first); a speed-optimized build of the same C would likely be faster, but no such number is published.

## Known shortcomings

- Numbers come from a competitor's (berith) README table, a single M1 Max run with keygen, sign and verify mixed per iteration (187.96 us vs @noble/curves 1.99 ms); slower than native node:crypto with unserialised keys (152.67 us); the HEAD bench file lacks the serialised rows, so the table is from an older harness; built at -Oz (emcc -Oz --llvm-lto 1 --closure 1) with the Emscripten version unstated; abandoned since 2018-02-24.
- Enricher: no harness bug inflates the 10.6x over @noble/curves 0.7.0, but the bench never checks the verify result and the serialised node:crypto row is missing at HEAD. Security flaws in the bundled orlp/ed25519 at the pinned commit: sign trusts the caller-supplied public key (double-public-key key leak); verify checks only the top 3 bits of S with no S &lt; L check, so malleable signatures pass; the 64-byte secret key is the SHA-512-expanded form, incompatible with libsodium and tweetnacl; key bytes are freed from the wasm heap without zeroing.

## Caveats and trade-offs

Third-party benchmark in a competing library's repository (hazae41/berith, 7 stars, now marked DEPRECATED by its author): public code, CPU and Node version stated, but one machine, 1,000 samples, and a mixed keygen+sign+verify iteration rather than separate operations, so tier B rather than A. The current bench file at HEAD (last changed 2023-10-12) has no serialized node:crypto or serialized berith rows, so the README table came from an earlier version of the harness. The wasm is built with -Oz (size, not speed), and the Emscripten version is unstated. Neither tweetnacl-js nor a native SUPERCOP ed25519 build appears in the table; the JS baseline is @noble/curves 0.7.0, and the native node:crypto row with KeyObject (unserialized) keys beats supercop.wasm (152.67 vs 187.96 us/iter). The serialized node:crypto row (555.61 us/iter) is the closer like-for-like comparison, since supercop.wasm works on raw key bytes. Last commit and last npm release are both 2018-02-24, so the code is old and unmaintained. The licence is listed on GitHub as Free Public License 1.0.0 / Zero Clause BSD (0BSD, OSI-approved, no patent grant). [retier] Enricher: the bundled orlp/ed25519 trusts a caller-supplied public key when signing (double-public-key key leak), checks only the top 3 bits of S when verifying (malleable signatures pass), uses SHA-512-expanded 64-byte secret keys incompatible with libsodium and tweetnacl, and frees key bytes from the wasm heap without zeroing; the bench never checks the verify result.

The README states no constant-time or side-channel guarantees; it wraps orlp/ed25519, a small portable C implementation, and the measured wasm is slower than native node:crypto when keys are not serialized. Wasm module is small, works in browsers and Node with the supercop.js API (Uint8Array instead of Buffer).

## Maintenance

Abandoned since 2018-02-24 (34 commits, 13 stars, one enhancement issue) but 0BSD-licensed and tiny, so it can be vendored; treat it as legacy code because of the orlp key format, lax verification and absent maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement in a competing library's repo (hazae41/berith README Node table, code at src/node/bench/index.bench.ts, Apple M1 Max, Node v18.12.1) that shows supercop.wasm 5.0.1 at 187.96 us/iter against @noble/curves 0.7.0 at 1.99 ms/iter; the measured wasm's emcc flags are public in supercop.wasm's gulpfile.ls, but the Emscripten version is unstated and the README table includes serialized rows the current bench file no longer has, so it falls short of A.
- **Verifier notes:** Numbers match the berith README Node table exactly; ratios in claimed_speedup are correctly marked as derived. Main shortcomings: about 10.6x faster than pure-JS @noble/curves 0.7.0, but slower than native node:crypto with unserialized keys; the benchmark is a single run on an M1 Max by a competitor; the wasm build is size-optimized and the project has been abandoned since 2018. The repo README is readme.md (lowercase) and makes no speed claim.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-128 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/README.md>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/node/bench/index.bench.ts>
  - <https://github.com/hazae41/berith>
  - <https://github.com/hazae41/berith/commits/master/src/node/bench/index.bench.ts>
  - <https://github.com/nazar-pc/supercop.wasm>
  - <https://github.com/nazar-pc/supercop.wasm/commits>
  - <https://github.com/nazar-pc/supercop.wasm/tree/master>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/gulpfile.ls>
- **Sources the enricher read:**
  - <https://github.com/nazar-pc/supercop.wasm>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/readme.md>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/gulpfile.ls>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/src/index.ls>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/src/supercop.c>
  - <https://raw.githubusercontent.com/nazar-pc/supercop.wasm/HEAD/src/bytes_allocation.js>
  - <https://github.com/nazar-pc/supercop.wasm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/README.md>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/node/bench/index.bench.ts>
  - <https://raw.githubusercontent.com/orlp/ed25519/7fa6712ef5d581a6981ec2b08ee623314cd1d1c4/src/verify.c>
  - <https://raw.githubusercontent.com/orlp/ed25519/7fa6712ef5d581a6981ec2b08ee623314cd1d1c4/src/keypair.c>
  - <https://raw.githubusercontent.com/orlp/ed25519/7fa6712ef5d581a6981ec2b08ee623314cd1d1c4/src/sign.c>
  - <https://github.com/orlp/ed25519/issues?q=is%3Aissue+public+key>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nazar-pc/supercop.wasm`) · [data/wave13/enrich/raw/github_com_nazar_pc_supercop_wasm.json](../../../data/wave13/enrich/raw/github_com_nazar_pc_supercop_wasm.json) (enrichment confidence 0.75)

</details>
