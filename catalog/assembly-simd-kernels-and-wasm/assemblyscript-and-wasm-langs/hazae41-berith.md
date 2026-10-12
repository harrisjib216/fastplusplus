# berith (Ed25519 and X25519 in Rust WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (ed25519-dalek and x25519-dalek compiled to WebAssembly with wasm-pack) with TypeScript` · `Unlicense` · 🟡 stale

> Deprecated wasm-pack build of Rust ed25519-dalek/x25519-dalek for JS; 5.9-7.1x faster than @noble/curves 0.7 on keygen+sign+verify.

| | |
|---|---|
| **Beats** | @noble/curves 0.7.0 (pure TypeScript/JavaScript Ed25519 in V8) |
| **Claimed result** | Deno 1.30.3: berith unserialized 325.78 us/iter vs @noble/curves 0.7.0 1.9 ms/iter (5.85x faster); Node 18.12.1: 281.68 us vs 1.99 ms (7.06x faster). Counter-rows on the same page: supercop.wasm 5.0.1 187.96 us/iter and node:crypto unserialized 152.67 us/iter are faster than berith |
| **Workload** | Per iteration: generate a random Ed25519 keypair, derive the public key, sign a 1 KiB random message and verify the signature. Measured with deno bench and a Node benchSync harness (1,000 samples). 'Unserialized' keeps keys as wasm objects; 'serialized' round-trips them through bytes. Rows: berith, @noble/curves 0.7.x, supercop.wasm 5.0.1 and node:crypto. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max (aarch64-apple-darwin) |
| **Compiler and flags** | The numbers date from February 2023; the README benchmark output is identical at commit e383614 (2023-02-16). That build used the rust:1.64.0 Docker image and wasm-pack build --target web --release (wasm-pack itself unpinned). The Cargo release profile was opt-level "z" with lto true, and the crates were ed25519-dalek 1.0.1 and x25519-dalek 1.2.0 with u64_backend. Runtimes were Deno 1.30.3 and Node v18.12.1. The baseline was @noble/curves 0.7.0 in Deno and 0.7.1 in Node (per package-lock, though the row is labelled 0.7.0). The current HEAD build (rust 1.71.0 Dockerfile, opt-level 3, ed25519-dalek 2.0.0, Sept 2023 rewrite) has never been re-benchmarked. |
| **Adoption** | 7 stars |
| **Last commit** | 2025-05-25 |
| **Links** | [repository](https://github.com/hazae41/berith) · [benchmark](https://github.com/hazae41/berith) |

## Verdict

On an Apple M1 Max, a loop of random Ed25519 keypair generation, public-key derivation, signing a 1 KiB message and verifying it took 325.78 us per iteration in Deno 1.30.3 versus 1.9 ms for @noble/curves 0.7.0 (5.85x), and 281.68 us versus 1.99 ms for noble 0.7.1 in Node 18.12.1 (7.06x), with berith built from Rust 1.64.0 via wasm-pack at opt-level z with LTO. The same Node table shows supercop.wasm 5.0.1 at 187.96 us and node:crypto at 152.67 us, both faster than berith; noble-curves' current README (Apple M4, a newer CPU and much newer noble) lists 137 + 283 + 665 us for getPublicKey, sign and verify, so the gap to today's noble is likely smaller than the 2023 ratio, though no run compares them directly.

## Use it when

- Browser or Deno code that needs Ed25519 signatures or X25519 and has no WebCrypto Ed25519/X25519 it can rely on, where pure-JS noble is the alternative and per-operation latency matters (hundreds of signatures or verifications per second).
- Projects pinned to the 1.1.x/1.2.x API that want a reproducible, CI-checked wasm binary rather than a JS implementation.
- Workloads that keep long-lived key objects in wasm and sign or verify many messages, which is the 'unserialized' case that produced the 5.85x (Deno) and 7.06x (Node) figures.
- Public-domain (Unlicense) licensing is required and a small vendored wasm blob is acceptable.

## Skip it when

- New code: the author deprecated it in favour of @hazae41/ed25519 (pure TypeScript) and @hazae41/ed25519-wasm / @hazae41/x25519-wasm; it gets README edits only since October 2023.
- On Node.js: node:crypto (OpenSSL) ran the same keygen+sign+verify loop in 152.67 us versus berith's 281.68 us, and supercop.wasm 5.0.1 ran it in 187.96 us, so berith is the third-fastest option on its own page.
- When keys must be serialised on every call (e.g. stored as bytes and reloaded): the serialized variant is about 13% slower and the wasm objects must still be created and freed.
- Consensus-critical verification that must match another library bit-for-bit: current noble-curves defaults to permissive ZIP-215 rules (zip215: true), while berith calls ed25519-dalek's default verify (dalek 1.0.1 in the benchmarked build, dalek 2.0.0 now); the two are different rule sets and berith does not document which edge cases it accepts.
- X25519-heavy workloads: only Ed25519 was benchmarked; X25519 speed is not documented.

## How it is fast

The curve arithmetic runs as compiled Rust in WebAssembly instead of JavaScript BigInt: the benchmarked 1.1.x build used ed25519-dalek 1.0.1 on curve25519-dalek 3.2.1 with the u64_backend (radix-2^51 field elements using native wasm i64 multiplies), whereas @noble/curves 0.7 does field arithmetic on BigInts in V8. Keys stay inside wasm memory between calls in the 'unserialized' mode, so only the 1 KiB message and 64-byte signature cross the JS-wasm boundary. There is no SIMD or hand-written assembly; the gain is compiled fixed-width limb arithmetic versus arbitrary-precision BigInt.

## Compared with alternatives

It is the only Ed25519/X25519 signature entry in this category; tape-sha256, sha2-wasm and md5-wasm cover hashing, not signatures. Against its own comparison rows, prefer node:crypto on Node and consider supercop.wasm (faster in the same table) or the author's successor @hazae41/ed25519-wasm for new browser code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | @hazae41/box at runtime (HEAD 1.2.6); bundled wasm built from ed25519-dalek 2.0.0, x25519-dalek 2.0.0, wasm-bindgen 0.2.87, getrandom 0.2 (js feature). The benchmarked 1.1.x line bundled ed25519-dalek 1.0.1, x25519-dalek 1.2.0 and rand 0.7.3. |
| **Minimum toolchain** | Using: a JS runtime with WebAssembly and crypto.getRandomValues (browsers, Node, Deno); the README's `using` examples need TypeScript 5.2+ explicit resource management, otherwise call .free(). Building: Rust 1.71.0 (Dockerfile) plus wasm-pack (unpinned) and Node 20. |
| **Platforms** | Any JS engine with WebAssembly (wasm32); reproducible build documented only on linux/amd64 hosts. Numbers measured on Apple M1 Max with Deno 1.30.3 and Node 18.12.1. |
| **Thread safety** | not documented (one wasm instance per JS realm; JS is single-threaded per realm) |
| **Drop-in for the baseline** | partial — same algorithm and wire formats (32-byte keys, 64-byte signatures), but a different object API: inputs must be wrapped in Berith.Memory, results are wasm objects that must be freed, and init is async; noble's functional ed25519.sign/verify calls cannot be swapped in place. |

## Gotchas

- The published numbers are for npm 1.1.x (Feb 2023, curve25519-dalek 3.2.1 with u64_backend, opt-level z). The current 1.2.x build uses ed25519-dalek 2.0.0 on curve25519-dalek 4.0.0, whose build.rs picks the 32-bit field backend for wasm32 (the wasm32-to-64-bit override is commented out with 'TODO(Wasm32): Needs tests + benchmarks') and berith sets no curve25519_dalek_bits cfg, so the shipped arithmetic backend differs from the one measured and has never been benchmarked.
- The benchmarked 1.1.x line is built on ed25519-dalek 1.0.1, which is affected by RUSTSEC-2022-0093 / CVE-2022-50237 (double public key signing oracle): its Ed25519Keypair.from_bytes accepts a 64-byte secret||public pair and signs with whatever public half is supplied, which leaks the private key if an attacker can choose that half. The 'serialized' benchmark row exercises exactly this from_bytes path. 1.2.0+ (dalek 2.x, 32-byte SigningKey.from_bytes) is not affected; do not use 1.1.x.
- Wasm objects are not garbage collected: every key, signature and Memory must be freed or wasm heap memory leaks. The February 2023 bench loop never called .free(), so the measured berith rows excluded deallocation and leaked about three boxed objects per iteration (minor at 300 us per iteration, but not what a correct caller pays).
- The deimos benchSync harness has no warm-up and averages all 1,000 performance.now() samples, and its summary prints ratio = other/this, so slower results appear as '0.67x faster' and '0.54x faster'; read those as berith being 1.5x and 1.85x slower than supercop.wasm and node:crypto.

## Known shortcomings

- Numbers measured on February 2023 code (commit e383614: rust 1.64.0, opt-level z, dalek 1.x), not HEAD; deprecated by the author; slower than supercop.wasm and node:crypto.
- Numbers were measured on npm 1.1.x (curve25519-dalek 3.2.1 u64 backend, opt-level z), which sits on ed25519-dalek 1.0.1 affected by RUSTSEC-2022-0093 / CVE-2022-50237; the 'serialized' row exercises exactly the vulnerable Ed25519Keypair.from_bytes(64-byte) path. The shipped 1.2.x build runs curve25519-dalek 4.0.0, whose build.rs picks the 32-bit field backend on wasm32 with no cfg override, so the shipped arithmetic backend differs from the measured one and was never benchmarked. The February 2023 bench loop never freed wasm objects; the deimos benchSync harness has no warm-up. Deprecated by its author.

## Caveats and trade-offs

The repository is marked DEPRECATED in favour of @hazae41/ed25519 and @hazae41/x25519. Code last changed in October 2023, and every commit since then (to 2025-05-25) is a README edit. The README numbers were measured on the February 2023 code (dalek 1.x, size-optimised opt-level z, rust 1.64.0) and were not regenerated after the September 2023 rewrite. The current bench files have no serialized rows, and the Node bench imports @noble/curves unpinned (^1.2.0), so re-running HEAD measures different code against a different baseline. The baseline, @noble/curves 0.7.x from early 2023, is old, so the 5.85-7.06x ratio is dated. The same table shows berith slower than supercop.wasm 5.0.1 (187.96 vs 281.68 us) and slower than node:crypto unserialized (152.67 us): the win is only against pure JS. The README's summary prints slowdowns as '0.67x faster' and '0.54x faster'. Each iteration bundles key generation, signing and verification, so per-operation costs are not separated. The Unlicense is a public-domain dedication with no patent grant. [retier] DEPRECATED by its author in favour of @hazae41/ed25519 and @hazae41/x25519; code unchanged since October 2023. The README numbers were measured on the February 2023 npm 1.1.x code (curve25519-dalek 3.2.1 u64 backend, opt-level z, rust 1.64.0) and never regenerated: the shipped 1.2.x build uses ed25519-dalek 2.0.0 on curve25519-dalek 4.0.0, whose build.rs selects the 32-bit field backend for wasm32 (berith sets no curve25519_dalek_bits cfg), so the shipped arithmetic has never been benchmarked. The benchmarked 1.1.x line sits on ed25519-dalek 1.0.1, affected by RUSTSEC-2022-0093 / CVE-2022-50237 (double public key signing oracle); the 'serialized' row exercises exactly that Ed25519Keypair.from_bytes(64-byte) path, so do not use 1.1.x. The February 2023 bench loop never called .free() (about three leaked boxed objects per iteration); the deimos benchSync harness has no warm-up and averages all 1,000 performance.now() samples; its summary prints slowdowns as '0.67x faster' and '0.54x faster'. Baseline @noble/curves 0.7.x (early 2023) is old; the same table shows berith slower than supercop.wasm 5.0.1 (187.96 vs 281.68 us) and node:crypto (152.67 us), so the win is only against pure JS. Each iteration bundles keygen, sign and verify. Unlicense (no patent grant).

README marks the package DEPRECATED in favour of @hazae41/ed25519 and @hazae41/x25519; wasm must be initialised asynchronously (Berith.initBundledOnce); Unlicense is a public-domain dedication with no patent grant; inputs and outputs cross the JS-wasm boundary and the 'serialized' variant is about 13% slower.

## Maintenance

Deprecated by its author and stale (code unchanged since npm 1.2.6 in October 2023, README edits through 2025-05-25, 7 stars, no issues); Unlicense makes it free to vendor, but use 1.2.x only, since the benchmarked 1.1.x line sits on the RUSTSEC-2022-0093-affected ed25519-dalek 1.0.1, and the shipped 1.2.x build has never been benchmarked.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README numbers are reproducible from the public snapshot at commit e383614 (2023-02-16): the harnesses are src/deno/bench/mod.bench.ts and src/node/bench/index.bench.ts, the Dockerfile pins rust:1.64.0, wasm/Cargo.toml sets opt-level "z" and lto, and the README names the CPU (Apple M1 Max) and the Deno and Node versions. Every row runs the named baseline, @noble/curves 0.7.x, on the same keygen+sign+verify loop.
- **Retiered** A to C: Enricher: the published numbers are for the 1.1.x line (curve25519-dalek 3.2.1 u64 backend on ed25519-dalek 1.0.1), whose benchmarked 'serialized' row runs the RUSTSEC-2022-0093 / CVE-2022-50237 from_bytes path, and the shipped 1.2.x build picks curve25519-dalek 4.0.0's 32-bit field backend on wasm32 and was never benchmarked; numbers measured on a since-replaced build with a security bug in the measured path (later-fixed-code rule, Topaz precedent) go to C.
- **Verifier notes:** The numbers match the README exactly (5.85x Deno, 7.06x Node against noble 0.7.x), with supercop.wasm and node:crypto faster than berith on the same page. The record's compiler_and_flags described the 2023-09 HEAD build, not the February 2023 build that produced the numbers; that field is corrected. The project is deprecated by its author, and the successor packages @hazae41/ed25519 and @hazae41/ed25519.wasm are not in this record. Category fit is loose: it is a Rust library compiled to wasm, not a wasm language.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/hazae41/berith>
  - <https://github.com/hazae41/berith/commits>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/README.md>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/package.json>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/deno/bench/mod.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/node/bench/index.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/LICENSE.md>
  - <https://github.com/hazae41/berith/tree/master/src/node/bench>
  - <https://github.com/hazae41/berith/commits/master/src/deno/bench/mod.bench.ts>
  - <https://github.com/hazae41/berith/commits/master/Dockerfile>
  - <https://github.com/hazae41/berith/commits/master/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/hazae41/berith/bc4d33d/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/README.md>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/src/deno/bench/mod.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/src/node/bench/index.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/Dockerfile>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/package.json>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/package-lock.json>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/hazae41/berith>
  - <https://github.com/hazae41/berith/issues>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/README.md>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/package.json>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/Cargo.lock>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/src/ed25519.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/wasm/src/ed25519/private_key.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/deno/bench/mod.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/src/node/bench/index.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/src/deno/bench/mod.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/src/node/bench/index.bench.ts>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/Dockerfile>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/Cargo.lock>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/src/ed25519.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/src/ed25519/keypair.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/src/ed25519/public_key.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/wasm/src/ed25519/signature.rs>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/package.json>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/package-lock.json>
  - <https://raw.githubusercontent.com/hazae41/berith/e383614dbdd2d1cc32ff7118813656d2ed2f56af/src/deno/mod.ts>
  - <https://registry.npmjs.org/@hazae41/berith>
  - <https://registry.npmjs.org/@hazae41/deimos/-/deimos-1.0.5.tgz>
  - <https://github.com/hazae41/deimos>
  - <https://github.com/hazae41/deimos/tree/master/src>
  - <https://raw.githubusercontent.com/hazae41/ed25519/HEAD/README.md>
  - <https://raw.githubusercontent.com/hazae41/ed25519.wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/paulmillr/noble-curves/HEAD/README.md>
  - <https://raw.githubusercontent.com/dalek-cryptography/curve25519-dalek/main/curve25519-dalek/build.rs>
  - <https://raw.githubusercontent.com/dalek-cryptography/curve25519-dalek/curve25519-4.0.0/curve25519-dalek/build.rs>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ed25519-dalek/RUSTSEC-2022-0093.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/hazae41/berith`) · [data/wave13/enrich/raw/github_com_hazae41_berith.json](../../../data/wave13/enrich/raw/github_com_hazae41_berith.json) (enrichment confidence 0.82)

</details>
