# authia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust compiled to WebAssembly` · `MIT` · 🟢 active

> Rust/Wasm Ed25519-only JWT verifier; first-party 1.5x lower latency than jose on Cloudflare Workers, 6-20x slower on Node.

| | |
|---|---|
| **Beats** | jose (JavaScript JOSE library: WebCrypto on Cloudflare Workers, native Node.js crypto bindings on Node) |
| **Claimed result** | Cloudflare Workers: authia (WASM) 0.20 ms avg, 0.17 ms p50, 0.36 ms p95 vs jose (WebCrypto) 0.30 / 0.28 / 0.50 ms (avg 1.5x lower, derived from page data). Node.js: jose (native crypto) 0.01-0.03 ms vs authia 0.17-0.20 ms, so the wasm build is 6-20x slower there (derived). |
| **Workload** | Ed25519 JWT verification per call on Cloudflare Workers / edge runtimes and on Node.js. |
| **Metric** | latency |
| **Adoption** | 0 stars; npm authia |
| **Last commit** | 2026-01-23 |
| **Links** | [repository](https://github.com/HaradaTakuma/authia) · [benchmark](https://github.com/HaradaTakuma/authia) |

## Verdict

First-party README tables only: on Cloudflare Workers, authia (Wasm) averaged 0.20 ms per verification (p50 0.17, p95 0.36) against jose on WebCrypto at 0.30 ms (0.28, 0.50), about 1.5x lower average latency (derived from page data); on Node.js jose with native crypto took 0.01-0.03 ms against 0.17-0.20 ms for authia, 6-20x slower. No hardware, Workers/Node/jose versions, iteration counts or harness are published, and how sub-millisecond per-call times were taken inside Workers (whose timers do not advance during synchronous execution) is not explained.

## Use it when

- Cloudflare Workers or another edge runtime verifying Ed25519 JWTs that are all signed by one fixed key, where a synchronous verify call is convenient.
- Tokens that match the author's schema (string sub, exp, single-string iss and aud, type access or refresh) and need no custom claims returned.
- Experiments with Rust-to-Wasm JWT verification (the README lists learning Rust and WebAssembly as a good fit).

## Skip it when

- Node.js or Bun backends: by the README's own table jose with native crypto takes 0.01-0.03 ms against 0.17-0.20 ms for authia, and the author recommends jose there and for production systems requiring maximum stability.
- More than one verification key in a process or isolate (multi-tenant issuers, key rotation without restart): the OnceLock cache keeps the first key and silently verifies later calls against it (see gotchas).
- Strict or custom claim handling: iss, aud, iat and type are optional, nbf is ignored, array-valued aud fails to parse, and unknown claims (roles, scope) are dropped from the returned payload because it is re-serialized from the fixed struct.
- Any algorithm other than EdDSA/Ed25519 (RS256, ES256, HS256) or token issuance.
- Size-sensitive bundles: the npm 0.3.4 package unpacks to 509,719 bytes (two wasm-pack targets, wasm-opt disabled).

## How it is fast

Each call is one synchronous trip into Rust compiled to Wasm: base64url decoding, a single serde_json pass straight into the typed claims struct (v0.3.0 cut three JSON passes to one), and ed25519-dalek 2.x signature verification, with the decoded VerifyingKey kept in a process-wide OnceLock so the JWK is parsed once. The release profile uses opt-level 3, LTO and codegen-units 1 (wasm-opt disabled). The claimed Workers win is over jose's WebCrypto Ed25519 path; on Node.js the README and ROADMAP put the JS-to-Wasm boundary cost (serde-wasm-bindgen conversion of options and payload) at about 0.1-0.15 ms per call, which is why jose's native crypto wins there.

## Compared with alternatives

No catalogued sibling verifies JWTs (tiny-secp256k1 and bls-eth-wasm cover other signature schemes, hash-wasm covers hashes); pick authia only for single-key Ed25519 JWT checks on Workers, and given its key-cache and claim-validation flaws jose remains the safer default.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime for the npm package (Wasm embedded); the Rust crate uses wasm-bindgen, serde, serde_json, serde-wasm-bindgen, base64 0.22, ed25519-dalek 2.1, js-sys and subtle |
| **Minimum toolchain** | Node.js 18+ (package.json engines); building needs Rust (edition 2021) and wasm-pack |
| **Platforms** | any JavaScript runtime with WebAssembly: Node.js, bundlers/browsers, Cloudflare Workers |
| **Thread safety** | not documented; each JS isolate or worker gets its own Wasm instance, and the public-key cache is a single process-wide OnceLock shared by every call in that instance |
| **Drop-in for the baseline** | partial — replaces jose's jwtVerify only for EdDSA tokens with the author's fixed claim schema; different call signature (synchronous, JWK string inside options) and custom claims are stripped from the result |

## Gotchas

- Security bug in the key cache (src/jwt.rs get_or_decode_public_key): CACHED_PUBLIC_KEY is a OnceLock; when a call passes a different publicKeyJwkRaw or publicKeyJwk than the cached one, the new key is decoded, CACHED_PUBLIC_KEY.set() fails silently, and the function returns the first cached key, so the signature is checked against the wrong key. In a multi-key isolate, tokens signed with the first key are accepted for the second key's issuer/audience and genuine second-key tokens are rejected. Only a Japanese code comment ('restart the process if the public key changes') mentions the single-key assumption; the README says the library 'automatically caches the decoded public key internally'.
- Claim validation is weaker than SECURITY.md states ('All required claims (iss, aud, exp, iat, type) are validated'): in 0.3.4 only sub and exp are required, iss and aud are compared only when present, iat is optional, the type claim is never compared (a token without type passes both verifyAccessToken and verifyRefreshToken, so INVALID_TOKEN_TYPE is never raised) and nbf is not checked. Claims are validated before the signature, and invalid_issuer/invalid_audience errors include the expected values, which reach unauthenticated callers if errors are surfaced. The alg check is a substring search for 'EdDSA' anywhere in the header (harmless, since Ed25519 is always used).
- Benchmark harness flaw: the repository has no code for the jose comparison, and its Rust benches are placeholders that time no-ops: in benches/jwt_verify_real.rs the verify_token_legacy_base64 and verify_token_raw_jwk closures only black_box string literals (the verification call is commented out) and the public_key_cache group times black_box("cached_key"), while jwt_verify.rs times only token.split('.'). The README and CHANGELOG '2-5x faster with publicKeyJwkRaw' and the docs/api.md '\~2-4x faster than JavaScript implementations' claims therefore have no measurement behind them, and docs/benchmarks.md, which api.md links to, is a 404.
- Docs drift: the README Known Issues says 0.3.1-0.3.3 reject tokens missing optional fields such as email, but the 0.3.3/0.3.4 code makes every field except sub and exp optional; docs/api.md still documents publicKeyJwk-only options and required fields; SECURITY.md lists only 0.1.x as supported; package.json and Cargo.toml still point to Taniyama2024/authia.

## Known shortcomings

- Faster only on Cloudflare Workers (1.5x); on Node it is 6-20x slower than jose; no jose harness in the repo (benches/ is Rust criterion only); 0 stars, 3 commits.
- Enricher: security bug: the public-key cache is a OnceLock, so a call with a second key silently verifies against the first cached key (src/jwt.rs get_or_decode_public_key); claim checks are weaker than SECURITY.md says (iss/aud checked only when present, typ never compared, nbf ignored, custom claims dropped); no jose harness in the repo and the Rust benches time no-ops (black_box of string literals with the verify call commented out), so the '2-5x faster with publicKeyJwkRaw' has no measurement behind it; all 7 npm versions were published 2026-01-22/23 with no commits since.

## Caveats and trade-offs

Mixed, first-party result: the README says jose is significantly faster on Node.js (native crypto, 0.01-0.03 ms vs authia 0.17-0.20 ms, 6-20x slower, derived from page data) and recommends jose for Node backends and for production systems requiring maximum stability. The only win is about 1.5x on Cloudflare Workers, where both use similar APIs. The jose comparison harness is not in the repository: benches/ (jwt_verify.rs, jwt_verify_real.rs) contains Rust criterion benches of authia alone, and examples/ holds usage samples only. No CPU, Workers/wrangler or Node versions, jose version or iteration counts are stated; Cloudflare Workers freezes Date.now()/performance.now() during synchronous execution, so how the sub-millisecond per-call Workers times were taken is unclear. README Known Issues: v0.3.1-v0.3.3 strict claim schema can reject tokens missing optional fields such as email. Repository has 3 commits; package.json and Cargo.toml still point to Taniyama2024/authia (moved to HaradaTakuma/authia).

Ed25519 JWT verification only; WASM must be initialised; slower than native crypto on Node.js (README says so).

## Maintenance

Effectively a one-day project: all seven npm versions (0.1.0-0.3.4) were published on 2026-01-22/23, the repository has 3 commits, 0 stars and 102 crates.io downloads, with no commits since 2026-01-23; MIT and small enough to vendor, but the first-key cache bug, lax claim checks and no-op benchmarks make it unsuitable beyond single-key experiments without fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (English and Japanese) carries first-party tables only: Cloudflare Workers authia 0.20/0.17/0.36 ms avg/p50/p95 vs jose (WebCrypto) 0.30/0.28/0.50 ms, and Node.js jose 0.01-0.03 ms vs authia 0.17-0.20 ms. No harness, CPU, runtime versions, jose version or iteration counts are published; benches/ holds only Rust criterion benches of authia itself (jwt_split, verify_token_legacy_base64, verify_token_raw_jwk), never jose.
- **Verifier notes:** Numbers match the README exactly; tier C stands (first-party, no methodology, no published jose harness). Shortcomings to record: slower than jose on Node.js by 6-20x, Workers-only 1.5x win, no benchmark code against jose, 0 stars and 3 commits.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-120 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/HaradaTakuma/authia>
  - <https://github.com/HaradaTakuma/authia/commits/main>
  - <https://github.com/HaradaTakuma/authia/tree/main/benches>
  - <https://github.com/HaradaTakuma/authia/tree/main/examples>
  - <https://github.com/HaradaTakuma/authia/tree/main/scripts>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/README.ja.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/package.json>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/benches/jwt_verify.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/benches/jwt_verify_real.rs>
- **Sources the enricher read:**
  - <https://github.com/HaradaTakuma/authia>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/README.ja.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/docs/api.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/package.json>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/src/jwt.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/src/types.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/src/error.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/scripts/build.js>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/benches/jwt_verify.rs>
  - <https://raw.githubusercontent.com/HaradaTakuma/authia/HEAD/benches/jwt_verify_real.rs>
  - <https://registry.npmjs.org/authia>
  - <https://crates.io/api/v1/crates/authia>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/haradatakuma/authia`) · [data/wave13/enrich/raw/github_com_haradatakuma_authia.json](../../../data/wave13/enrich/raw/github_com_haradatakuma_authia.json) (enrichment confidence 0.85)

</details>
