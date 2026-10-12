# tiny-secp256k1 (WASM build)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (wrapping the C libsecp256k1) compiled to WebAssembly, TypeScript wrapper` · `MIT` · 🟡 stale

> bitcoin-core libsecp256k1 compiled to WebAssembly with a TypeScript API; about 2-4x faster than elliptic, but slower than native addons.

| | |
|---|---|
| **Beats** | elliptic (pure JavaScript, the fallback of tiny-secp256k1 1.1.6); the Rust native addon is faster than the WASM build |
| **Claimed result** | PR #53 maintainer comment, Intel i5-8250U Linux: sign WASM 469.03 us/op (2132.07 op/s) vs tiny-secp256k1@1.1.6 elliptic 913.58 us/op (1094.60 op/s); verify WASM 605.01 us/op vs elliptic 2576.87 us/op; pointFromScalar WASM 280.10 us/op vs elliptic 542.96 us/op. Apple M1: sign WASM 133.19 us/op vs elliptic 522.64 us/op; verify WASM 212.05 us/op vs elliptic 1515.26 us/op; pointFromScalar WASM 96.43 us/op vs elliptic 316.96 us/op. Author summary: 'Wasm vs js: 2x for sign and pk creation, 4x for verify'. The Rust N-API addon in the same PR did sign in 51.71 us/op on the i5-8250U, about 9x faster than WASM (derived from page data). README (no numbers): the wasm2js asm.js build is 10x-20x slower than WASM and noble-based @bitcoinerlab/secp256k1 is 1.5x-5x slower than WASM. |
| **Workload** | ECDSA sign and verify micro-benchmarks from the repo's benches directory, posted by the maintainer in PR #53 (March 2021). |
| **Metric** | throughput |
| **Hardware** | Intel i5-8250U (Linux); Apple M1; a Debian i686 VirtualBox run without an elliptic row; Node.js version not stated |
| **Compiler and flags** | Rust &gt;= 1.50.0, wasm32-unknown-unknown target, wasm-opt from binaryen (README build section); the PR mentions -Z build-std=panic_abort,std and opt-level variants for the addon, but no wasm-opt flags or Node.js version are given for the benchmark run |
| **Adoption** | 108 stars |
| **Last commit** | 2025-06-21 |
| **Links** | [repository](https://github.com/bitcoinjs/tiny-secp256k1) · [benchmark](https://github.com/bitcoinjs/tiny-secp256k1/pull/53#issuecomment-801844450) |

## Verdict

Source: the maintainer's run of the repo's benches harness on pre-release PR #53 code (2021-03-18), against tiny-secp256k1 1.1.6's elliptic fallback. Node.js version unstated. On an i5-8250U under Linux, WASM was 1.9x faster for sign (469 vs 914 us/op), 4.3x for verify (605 vs 2577) and 1.9x for pointFromScalar (280 vs 543). On an Apple M1 the gaps were 3.9x, 7.1x and 3.3x (ratios derived from page data). In the same run the C++ and Rust native addons signed about 9x faster than WASM.

## Use it when

- Browser or other non-Node JS code that needs secp256k1 ECDSA or BIP340 Schnorr, where the alternative is elliptic or another pure-JS library.
- bitcoinjs-lib, ecpair and bip32 projects that need the exact tiny-secp256k1 interface and its test vectors (validation errors such as 'Expected Private' and 'Expected Point').
- Verify-heavy code in JS: in the maintainer's 2021 runs, verify gained the most over elliptic (4.3x on i5-8250U, 7.1x on Apple M1).
- Deployments that want one portable artifact, with no node-gyp toolchain at install time and no native addon per platform.

## Skip it when

- Node.js servers where a native binding is allowed. In the same PR #53 run, the old tiny-secp256k1 1.1.6 C++ NAN addon signed in 49.33 us/op against 469.03 us/op for WASM (about 9.5x faster), and the unshipped Rust N-API addon took 51.71 us/op.
- React Native/Hermes or other runtimes without WebAssembly (issue #91). Use the asm.js build (@bitcoin-js/tiny-secp256k1-asmjs; the README says it is 10-20x slower than WASM) or @bitcoinerlab/secp256k1 on noble (README: 1.5-5x slower than WASM).
- Bundle-size-sensitive front ends: the 2.2.4 secp256k1.wasm is 1,242,788 bytes, against 163,363 bytes in 2.2.3, because of the full precomputed tables.
- Bundlers or frameworks without WASM-module support. Open loading bugs: #122 (NestJS ENOENT on lib/secp256k1.wasm) and #92 (wrong path under Electron); closed reports: #116 (missing wasm file), #86 (fs.readFileSync in Vue) and #98 (browserify).
- Projects that need fast releases: the repo calls itself 'under development' and 'a research effort'. Commits are sparse; the last one, on 2025-06-21, shipped a performance fix that had waited about two years.

## How it is fast

The C library bitcoin-core/secp256k1 is compiled to wasm32-unknown-unknown through the Rust crate secp256k1-sys 0.8.1, then optimized with wasm-opt -O4. Build settings: Rust release profile with LTO, panic=abort and codegen-units=1; vendored libsecp256k1 revision 21ffe4b. The WASM therefore runs libsecp256k1's own field and scalar arithmetic and constant-time multiplication by the generator, instead of elliptic's bn.js big-number arithmetic. Since 2.2.4 the build no longer uses the lowmemory feature, so it embeds precomputed tables (ECMULT_WINDOW_SIZE 15, ECMULT_GEN_PREC_BITS 4). The context is a 192-byte static buffer, created and randomized once. The JS wrapper copies arguments into fixed static buffers in WASM memory, so there are no allocations on the hot path.

## Compared with alternatives

Pick this one when you need secp256k1 (Bitcoin, BIP340 Schnorr, bitcoinjs plug-ins). bls-eth-wasm covers BLS12-381 and starknet-rs's WASM build covers the StarkNet Pedersen hash; neither does secp256k1. Like those two, this entry is a native crypto library compiled to WASM that beats pure-JS code but not native bindings.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | uint8array-tools 0.0.7 at runtime. Building from source needs Rust (pinned to 1.70.0 in rust-toolchain) with the wasm32-unknown-unknown target, a clang that compiles libsecp256k1 to wasm (the Dockerfile uses LLVM 12) and binaryen wasm-opt (version_114 in the Dockerfile). |
| **Minimum toolchain** | Node.js &gt;= 14 (package.json engines). For browsers, a bundler that can import a .wasm ES module, because lib/wasm_loader.browser.js runs `import * as wasm from './secp256k1.wasm'`. The README still says 'Rust &gt;= 1.50.0', but Cargo.toml uses edition 2021 and the repo pins 1.70.0. |
| **Platforms** | Any JS runtime with WebAssembly: Node (loads the binary synchronously with fs.readFileSync and new WebAssembly.Module at import time) and browsers through a bundler. No WebAssembly in React Native/Hermes. |
| **Thread safety** | Not documented. Each module instance has one WASM instance, its static input buffers and a lazily created global context, and every call is synchronous. Single-threaded JS calls are therefore safe, and each worker_thread loads its own instance. |
| **Drop-in for the baseline** | partial: it keeps the tiny-secp256k1 function set that the bitcoinjs ecc plug-ins expect, so it is a drop-in for the 1.x package, elliptic fallback included. It is not a drop-in for elliptic's own EC/KeyPair API, and it needs WASM support in the runtime or bundler. |

## Gotchas

- Avoid 2.2.3. It switched secp256k1-sys to its lowmemory feature, and pointFromScalar slowed from 99.09 to 176.99 us/op in the maintainer's measurement (issue #123). 2.2.4 removed the feature, but npm only got that release on 2025-06-21; 2.2.3 had been the latest release since 2023-06-29.
- The catalogued numbers are from pre-release PR #53 code (March 2021; closed unmerged, and the work landed in #55 without node bindings). No one has re-measured the shipped 2.2.4, which uses a newer libsecp256k1, different tables and a different toolchain. The Node.js version, wasm-opt flags and repetition count of the 2021 runs are not given.
- Harness quirk in benches/index.js. The 'recover' row passes f.recoveryId, but the fecdsa fixtures never set that field, so every recover runs with recoveryId undefined, treated as 0, whatever the signature's real id. That row is not in the catalogued claim. The sign, verify and pointFromScalar rows look sound: each module runs the same valid test vectors, warms up for 2 s, then is timed for at least 5 s with process.hrtime.
- Secret keys pass through fixed static buffers in WASM memory, which the wrapper zeroes after every call. libsecp256k1's constant-time C code is compiled to WASM, but the project does not document any side-channel guarantee once a JIT engine runs that code.

## Known shortcomings

- Numbers match the PR #53 maintainer comment (2021-03-18) exactly but are first-party; PR #53 was closed unmerged; no Node version or wasm-opt flags; the Rust N-API addon was about 9x faster than WASM and never shipped, and the old C++ addon was also faster. WASM packaging of the catalogued bitcoin-core/secp256k1. Stale.
- Enricher: the catalogued numbers come from PR #53 pre-release code; 2.2.3 (npm 2023-06-29 to 2025-06-21) was built with secp256k1-sys lowmemory and pointFromScalar slowed from 99.09 to 176.99 us/op (issue #123), 2.2.4 removed lowmemory but secp256k1.wasm grew from 163,363 to 1,242,788 bytes (window-15 tables) and was never re-measured; the same PR run had the old C++ NAN addon signing at 49.33 vs WASM 469.03 us/op (about 9.5x faster); benches/index.js 'recover' passes an undefined recoveryId (treated as 0); no independent measurement.

## Caveats and trade-offs

Numbers are a 2021 maintainer comment in PR #53, which was closed unmerged ('Moved to #55'), so they were measured on pre-release code; the Rust N-API addon that beat WASM by about 9x was not shipped (it is commented out of the current benches/index.js and the README describes the current version as WASM only), and the old 1.1.6 C++ NAN addon is also faster than WASM per the README ('faster than elliptic but slower than node bindings'). Against the category's other baseline, the same library compiled natively, WASM loses. Node.js version, wasm-opt flags and repetition counts are not stated; no independent measurement. libsecp256k1 (bitcoin-core/secp256k1) is already catalogued; this entry is its WASM packaging.

One portable WASM binary replaces the old C++ addon plus elliptic fallback; slower than node native bindings, so on Node the native addon would be the faster choice; JS BigInt alternatives are 1.5x-5x slower than this WASM per the README.

## Maintenance

Stale but usable: MIT-licensed, npm latest is 2.2.4 (2025-06-21, the lowmemory fix), the last commit is from 2025-06-21, and open issues are mostly about loading the .wasm file in bundlers and frameworks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party maintainer (fanatid) comment of 2021-03-18 in PR #53 gives WASM vs tiny-secp256k1@1.1.6 elliptic numbers on i5-8250U and Apple M1; bench code is public (benches/index.js) but Node version, Rust/wasm-opt flags and benchmark repetitions are not stated, so not A, and nothing independent, so not B.
- **Verifier notes:** Numbers in the record match the PR comment exactly; added the pointFromScalar rows and the comment anchor the README links to. Main shortcomings: first-party 2021 numbers from an unmerged PR, no Node or flag details, and the WASM build is about 9x slower than a native addon of the same library.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-23 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bitcoinjs/tiny-secp256k1/pull/53>
  - <https://github.com/bitcoinjs/tiny-secp256k1/pull/53#issuecomment-801844450>
  - <https://github.com/bitcoinjs/tiny-secp256k1>
  - <https://github.com/bitcoinjs/tiny-secp256k1/commits>
  - <https://github.com/bitcoinjs/tiny-secp256k1/tree/master/benches>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/index.js>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/package.json>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/cryptocoinjs_secp256k1.js>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/package.json>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/index.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/wasm_loader.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/wasm_loader.browser.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/wasm_path.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/rand.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/validate.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/src_ts/validate_error.ts>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/index.js>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/package.json>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/fixtures.js>
  - <https://raw.githubusercontent.com/bitcoinjs/tiny-secp256k1/HEAD/benches/cryptocoinjs_secp256k1.js>
  - <https://github.com/bitcoinjs/tiny-secp256k1/pull/53>
  - <https://github.com/bitcoinjs/tiny-secp256k1/pull/55>
  - <https://github.com/bitcoinjs/tiny-secp256k1/issues?q=is%3Aissue>
  - <https://github.com/bitcoinjs/tiny-secp256k1/issues/123>
  - <https://github.com/bitcoinjs/tiny-secp256k1/issues/106>
  - <https://github.com/bitcoinjs/tiny-secp256k1/commits/master>
  - <https://raw.githubusercontent.com/rust-bitcoin/rust-secp256k1/secp256k1-sys-0.8.1/secp256k1-sys/build.rs>
  - <https://raw.githubusercontent.com/rust-bitcoin/rust-secp256k1/secp256k1-sys-0.8.1/secp256k1-sys/depend/secp256k1-HEAD-revision.txt>
  - <https://registry.npmjs.org/tiny-secp256k1>
  - <https://registry.npmjs.org/tiny-secp256k1/-/tiny-secp256k1-2.2.4.tgz>
  - <https://registry.npmjs.org/tiny-secp256k1/-/tiny-secp256k1-2.2.3.tgz>
  - <https://raw.githubusercontent.com/bitcoinerlab/secp256k1/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/bitcoinjs/tiny-secp256k1`) · [data/wave13/enrich/raw/github_com_bitcoinjs_tiny_secp256k1.json](../../../data/wave13/enrich/raw/github_com_bitcoinjs_tiny_secp256k1.json) (enrichment confidence 0.62)

</details>
