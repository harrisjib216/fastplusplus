# starknet-rs (WebAssembly build, Pedersen hash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (compiled to wasm32-wasi in the benchmark)` · `Apache-2.0 OR MIT` · 🟢 active

> Rust Starknet library whose starknet-crypto Pedersen hash, compiled to WebAssembly, ran 6.88x faster than pure-JS micro-starknet in Node.js (2022).

| | |
|---|---|
| **Beats** | micro-starknet (paulmillr, pure-JavaScript StarkNet library) on Node.js |
| **Claimed result** | starknet-rs 228.67 us vs micro-starknet 1.573 ms per pedersen_hash (6.88x relative, as printed in the README). |
| **Workload** | One pedersen_hash call: starknet-rs built for wasm32-wasi and run on wasmer-js 0.4.1 under Node.js v18.12.1, versus micro-starknet in Node.js (criterion.rs for the wasm side). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5950X 16-Core Processor, Ubuntu 20.04.5 LTS |
| **Compiler and flags** | cargo wasi build --bench=pedersen_hash --release (scripts/build_bench_wasm.sh; default release profile, no profile overrides in Cargo.toml); rustc version not stated; criterion 0.4.0 run under wasmer-js 0.4.1; starknet-crypto pinned at rev 76e32ef; micro-starknet pinned at commit a1e7fa0 and timed with benchmark.js 2.1.4 (js-bench.ts, webpack build); Node.js v18.12.1 |
| **Adoption** | 312 stars |
| **Last commit** | 2025-11-09 |
| **Links** | [repository](https://github.com/xJonathanLEI/starknet-rs) · [benchmark](https://github.com/xJonathanLEI/pedersen-bench) |

## Verdict

In xJonathanLEI/pedersen-bench (November 2022), one pedersen_hash on fixed inputs took 228.67 us for starknet-crypto rev 76e32ef built with cargo wasi --release and run by criterion 0.4 under wasmer-js 0.4.1 on Node.js v18.12.1, against a 1.573 ms benchmark.js mean for micro-starknet a1e7fa0 in the same Node.js, on an AMD Ryzen 9 5950X with Ubuntu 20.04.5 (6.88x); the same repo's native table shows starknet-rs 1.15x slower than pathfinder.

## Use it when

- Rust services, indexers or wallets that compute many Starknet Pedersen hashes (contract addresses, Merkle-Patricia nodes, hash chains) natively: 13 us per hash on an Apple M3 Max per the crate README.
- Browser or Node.js code that hashes in bulk and can ship a wasm module: about 65 us per hash under wasmtime on the M3 Max, against 883 us per hash for scure-starknet in JS on an Apple M4 (different machines and runtimes, so only a rough gap).
- Projects already in Rust that want one dependency covering Pedersen, Poseidon, ECDSA and RFC 6979 for the Stark curve, with no_std support.
- When the hash path's 100 KB-plus lookup table in the binary is acceptable; otherwise the pedersen_no_lookup feature trades about 10x speed for size.

## Skip it when

- Signing with secret keys in hostile environments: the README states starknet-crypto has no constant-time guarantees and is not audited, while scure-starknet (the renamed micro-starknet) reports an audit funded by StarkWare.
- Small JS apps that hash a handful of values: wasm instantiation, binary size of the lookup table and the glue code outweigh a \~1 ms per-hash saving.
- When you need a ready-made npm package: starknet-rs ships no wasm npm build of starknet-crypto; you write and maintain the wasm-bindgen wrapper.
- When you rely on the 6.88x figure for capacity planning: it was measured on 2022 code that has since been replaced by the lambdaworks implementation, against a JS version that has also changed.
- Projects that need a stable API: the README calls the library experimental with breaking changes before 1.0 (starknet-crypto went 0.7 to 0.8 in August 2025).

## How it is fast

Pedersen hash here is a fixed-base subset sum over four Stark-curve points; the crate precomputes 4-bit lookup tables (15 affine multiples per 4-bit chunk, 62 chunks for the low 248 bits plus one for the top 4 bits of each input) and adds one table point per non-zero nibble with mixed projective-affine addition, so a hash costs about 120 point additions and one inversion. The 2022 code that was benchmarked (rev 76e32ef, from PR #245) ported this table from eqlabs/pathfinder on top of ark-ff 0.3 Montgomery arithmetic; current releases (checked at 0.7.4 and 0.8.1) delegate pedersen_hash to starknet-types-core, which calls lambdaworks' PedersenStarkCurve, a port of the same 4-bit table. The JavaScript baseline at the pinned commit walks all 252 bits of each input and does one BigInt Jacobian addition per set bit (its windowed variant is commented out), so the ratio mixes algorithm and runtime.

## Compared with alternatives

Among the catalogued wasm libraries the closest analogues are bls-eth-wasm and tiny-secp256k1, which replace pure-JS elliptic-curve code for BLS12-381 and secp256k1; pick starknet-crypto only when the curve is the Stark curve and the hash is Starknet Pedersen, since none of the siblings implement it. For general-purpose hashes in the browser, hash-wasm is the packaged choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | starknet-crypto 0.8.1: starknet-types-core 0.2 (lambdaworks-math and lambdaworks-crypto), starknet-curve, crypto-bigint, hmac, sha2, rfc6979, num-bigint/num-integer/num-traits, zeroize; for JS use add wasm-bindgen (and wasm-pack) yourself |
| **Minimum toolchain** | Rust 2021 edition; no rust-version (MSRV) declared in Cargo.toml |
| **Platforms** | any Rust target; no_std with optional alloc; wasm32 (wasm32-wasi in the benchmark, wasm32-unknown-unknown via wasm-bindgen in the example) |
| **Thread safety** | pedersen_hash is a pure function over immutable static tables; PedersenHasher is a plain owned struct; not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: the JS baseline at micro-starknet a1e7fa0 is a bit-serial subset sum (252 iterations per input, one BigInt Jacobian add per set bit, plus a per-step point-equality check), its windowed path commented out, while starknet-rs uses a 4-bit lookup table with mixed additions; part of the 6.88x is the table algorithm, which a JS port could also use, not WebAssembly versus JS.
- The benchmarked code no longer ships: rev 76e32ef used starknet-ff (ark-ff 0.3) with a codegen lookup_table!(4); starknet-crypto 0.7.4 and 0.8.1 call starknet_types_core::hash::Pedersen, i.e. lambdaworks, so the 2022 numbers describe a predecessor implementation.
- WebAssembly runs about 7x slower than native here (228.67 us wasm vs 31.99 us native on the same Ryzen 9 5950X in 2022; 64.96 vs 13.02 us on the M3 Max now); issue #241 reporting the gap was closed 'not planned' in July 2023, so do not expect native speed in the browser.
- The benchmark linked only starknet-crypto and starknet-ff, not the whole starknet crate; pulling starknet (providers, reqwest, serde) into a wasm module is a separate and much larger build.

## Known shortcomings

- pedersen-bench is the author's own harness frozen 2022-11-22 with both sides pinned to 2022 commits; each side runs its own harness (criterion under wasmer-js vs benchmark.js parsing hex inputs); rustc version unstated.
- The micro-starknet baseline at the pinned a1e7fa0 does a bit-serial BigInt subset sum (252 steps per input, windowed path commented out) while starknet-rs uses a 4-bit lookup table, so part of the 6.88x is the algorithm rather than WebAssembly versus JS. The benchmarked starknet-crypto rev 76e32ef no longer ships: 0.7.4 and 0.8.1 delegate pedersen_hash to starknet-types-core/lambdaworks. The same README shows the wasm build about 7x slower than native; issue #241 (wasm performance) was closed as not planned.

## Caveats and trade-offs

First-party benchmark repo by the starknet-rs author, frozen since 22 November 2022 with both implementations pinned to 2022 commits (starknet-crypto rev 76e32ef, micro-starknet a1e7fa0); both have changed a lot since, so the 6.88x is stale. Different harnesses on each side: criterion compiled to wasm32-wasi and run through the wasmer-js WASI shim on Node's V8, versus benchmark.js mean on pure JS whose inputs are hex strings parsed on every call. Single function (pedersen_hash). The same README's native table shows starknet-rs 1.15x slower than pathfinder, whose Pedersen code starknet-crypto credits as its source. Current first-party figures from separate machines are not comparable: the starknet-crypto README gives wasm pedersen_hash 64.96 us on wasmtime 21.0.1 (Apple M3 Max) and the renamed scure-starknet README gives pedersen 883 us/op on an Apple M4 in JS. starknet-crypto has no constant-time guarantees and is not audited (README warning). Last commit 2025-11-09, near the 12-month line, so this entry will turn stale soon. [retier] First-party benchmark repo by the starknet-rs author, frozen since 22 November 2022 with both implementations pinned to 2022 commits (starknet-crypto rev 76e32ef, micro-starknet a1e7fa0). Harness asymmetry: the JS baseline at a1e7fa0 does a bit-serial BigInt subset sum (252 steps per input, windowed path commented out) while starknet-rs uses a 4-bit lookup table, so part of the 6.88x is the algorithm, not WebAssembly versus JS. Different harnesses on each side (criterion through wasmer-js WASI on Node vs benchmark.js with hex-string inputs parsed per call). The benchmarked code no longer ships: 0.7.4 and 0.8.1 delegate pedersen_hash to starknet-types-core/lambdaworks. The same README shows the wasm build about 7x slower than native; issue #241 closed as not planned.

Whole Starknet crate pulled into the wasm module; the module is usable from JS as a wasm package; benchmark runs through a WASI shim rather than a browser.

## Maintenance

Maintained but slowing (last commit 2025-11-09, starknet-crypto 0.8.1 released August 2025, 4.8 million crates.io downloads), dual MIT/Apache-2.0 and easy to depend on, but the 2022 benchmark measured code that has since been replaced by the lambdaworks implementation, so the ratio is stale and first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own pedersen-bench README shows starknet-rs wasm 228.67 us vs micro-starknet 1.573 ms (6.88x) with public bench code (benches/pedersen_hash, js-bench.ts, scripts/build_bench_wasm.sh) and a stated CPU (Ryzen 9 5950X), but the rustc version is not stated and the two sides run under different harnesses (criterion under wasmer-js vs benchmark.js), so first-party C.
- **Verifier notes:** Numbers and hardware match the pedersen-bench README; the comparison is real but stale (2022 pins) and cross-harness. Metadata confirmed: 312 stars, Apache-2.0 OR MIT, last commit 2025-11-09 (active, borderline). The record's caveat that the wasm did not run in V8 was misleading (wasmer-js runs on Node's WebAssembly engine) and has been reworded.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/xJonathanLEI/starknet-rs>
  - <https://github.com/xJonathanLEI/starknet-rs/commits>
  - <https://github.com/xJonathanLEI/pedersen-bench>
  - <https://github.com/xJonathanLEI/pedersen-bench/commits>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/package.json>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/js-bench.ts>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/scripts/build_bench_wasm.sh>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/scripts/run_bench_wasm.sh>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/paulmillr/scure-starknet/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/xJonathanLEI/starknet-rs>
  - <https://github.com/xJonathanLEI/starknet-rs/commits/master>
  - <https://github.com/xJonathanLEI/starknet-rs/commits/master/starknet-crypto/src/pedersen_hash/default.rs>
  - <https://github.com/xJonathanLEI/starknet-rs/issues?q=is%3Aissue+wasm>
  - <https://github.com/xJonathanLEI/starknet-rs/issues/241>
  - <https://github.com/xJonathanLEI/starknet-rs/issues/236>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/src/lib.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/src/pedersen_hash/mod.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/src/pedersen_hash/default.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/src/pedersen_hash/no_lookup.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-crypto/benches/pedersen_hash.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/starknet-curve/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/examples/starknet-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/examples/starknet-wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/HEAD/examples/starknet-wasm/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-crypto/src/pedersen_hash.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-crypto/src/pedersen_points.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-crypto/src/lib.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-crypto/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-crypto/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/76e32efe609919d1fdc6724cbefa2d3e119dea88/starknet-ff/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/starknet-crypto/v0.7.4/starknet-crypto/src/pedersen_hash/default.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/starknet-rs/starknet-crypto/v0.7.4/starknet-crypto/Cargo.toml>
  - <https://github.com/xJonathanLEI/pedersen-bench>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/package.json>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/js-bench.ts>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/benches/pedersen_hash.rs>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/scripts/build_bench_wasm.sh>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/scripts/run_bench_wasm.sh>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/xJonathanLEI/pedersen-bench/HEAD/webpack.config.ts>
  - <https://raw.githubusercontent.com/paulmillr/micro-starknet/a1e7fa08e714677b9b1123ae410681c413b22f27/index.ts>
  - <https://raw.githubusercontent.com/paulmillr/micro-starknet/a1e7fa08e714677b9b1123ae410681c413b22f27/package.json>
  - <https://raw.githubusercontent.com/paulmillr/micro-starknet/a1e7fa08e714677b9b1123ae410681c413b22f27/README.md>
  - <https://raw.githubusercontent.com/paulmillr/scure-starknet/HEAD/README.md>
  - <https://raw.githubusercontent.com/paulmillr/scure-starknet/HEAD/index.ts>
  - <https://raw.githubusercontent.com/starknet-io/types-rs/HEAD/crates/starknet-types-core/src/hash/pedersen.rs>
  - <https://raw.githubusercontent.com/starknet-io/types-rs/HEAD/crates/starknet-types-core/Cargo.toml>
  - <https://raw.githubusercontent.com/starknet-io/types-rs/HEAD/crates/starknet-types-core/src/hash/mod.rs>
  - <https://raw.githubusercontent.com/lambdaclass/lambdaworks/HEAD/crates/crypto/src/hash/pedersen/mod.rs>
  - <https://crates.io/api/v1/crates/starknet-crypto>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/xjonathanlei/starknet-rs`) · [data/wave13/enrich/raw/github_com_xjonathanlei_starknet_rs.json](../../../data/wave13/enrich/raw/github_com_xjonathanlei_starknet_rs.json) (enrichment confidence 0.7)

</details>
