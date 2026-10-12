# keccak-batch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0` · 🟢 active

> Rust crate that hashes 2/4/8 equal-length inputs at once with SIMD Keccak-256; \~5.5x per hash over keccak-asm (README).

| | |
|---|---|
| **Beats** | keccak-asm (assembly Keccak-256 backend behind Alloy's asm-keccak feature) and tiny-keccak scalar implementation |
| **Claimed result** | 8-wide AVX-512 batch: \~5.4x (64-byte) / \~4-5x (4 KiB) over own scalar path; scalar path is at parity with tiny-keccak; keccak-asm is \~1.3x faster than scalar; 8-wide batch is still \~5.5x faster per hash than keccak-asm |
| **Workload** | Batched Keccak-256 hashing of 64-byte inputs (Merkle/BMT-node hot path) and 4 KiB inputs, comparing SIMD-batched (SSE2/NEON/wasm, AVX2, AVX-512) lane widths against the crate's own scalar path and against keccak-asm/tiny-keccak, via `cargo run --release --example perf` |
| **Metric** | throughput |
| **Hardware** | "Zen-class AVX-512 part" (exact CPU model not stated) |
| **Compiler and flags** | cargo run --release --example perf; KECCAK_BATCH_NO_AVX512 / KECCAK_BATCH_NO_AVX2 env flags to cap backend |
| **Adoption** | 1 star; crates.io keccak-batch 0.1.0 (\~3.2k downloads); used as the batched hash in nxm-rs/nectar (Swarm BMT) |
| **Last commit** | 2026-07-24 |
| **Links** | [repository](https://github.com/nxm-rs/keccak-batch) · [benchmark](https://github.com/nxm-rs/keccak-batch/blob/main/README.md) |

## Verdict

The crate's own perf example, run with cargo --release on an unnamed 'Zen-class AVX-512 part', measured 8-wide batched Keccak-256 at \~5.4x (64 B) and \~4-5x (4 KiB) per hash over its scalar path; open PR #15 names the maintainer's Zen 4 host as a Ryzen 9 7940HS and puts width-8 at \~3.5 us per 64 hashes. The tiny-keccak parity and keccak-asm comparisons (\~1.3x over scalar; batch \~5.5x over keccak-asm) come from an unpublished same-binary harness; the public examples/perf.rs and benches/keccak.rs time only the crate's own scalar vs batch.

## Use it when

- Merkle/BMT levels, proof systems or sampling loops that hash many independent 64-byte (one-permutation) inputs in Ethereum/Swarm Keccak-256
- x86-64 servers with AVX-512F (8-wide, \~5.4x over the crate's scalar path at 64 B) or AVX2 (4-wide, \~3.1x at 64 B)
- Bulk hashing of equal-length blocks up to multi-KiB (README reports \~4-5x at 4 KiB, 8-wide)
- wasm with simd128 enabled at build time, where the 2-wide path took the 64-byte hash from \~379 ns to \~222 ns under wasmtime
- Rust code already generic over digest::Digest or alloy's Keccak256 shape that also needs a batch entry point

## Skip it when

- Single-message or latency-bound hashing: keccak256/Keccak256 run the scalar path, which the README puts at parity with tiny-keccak and \~1.3x slower than keccak-asm
- Inputs of mixed lengths: a batch absorbs in lockstep and panics on unequal lengths, so you must bucket inputs by length yourself
- FIPS-202 SHA3-256, SHAKE or other Keccak widths: only legacy-padded Keccak-256 with a 32-byte output is implemented
- Proprietary or closed-source products: AGPL-3.0-or-later copyleft, and there is no C/C++ API
- aarch64 servers looking for more than 2-wide: aarch64 is fixed at NEON width 2, and there is no SVE path or use of the ARMv8.2 SHA3 instructions

## How it is fast

It does not speed up a single Keccak-f[1600] permutation. It runs one independent state per SIMD lane: 8 states in AVX-512 zmm registers, 4 with AVX2, 2 with SSE2/NEON/wasm simd128. The permutation is written once, generic over a small Lane trait (xor, andnot, rotate, splat, load, store). The 25-lane state is passed by value and rho/pi is unrolled so LLVM can keep the lanes in vector registers. The maintainers' disassembly (PRs #7 and #15) shows the AVX-512 build already fuses chi/theta into vpternlogq and turns the rotates into immediate vprolq. Spilling from register pressure on the 25-lane state is the remaining bottleneck, and the gather/scatter transpose costs about 9%.

## Compared with alternatives

Pick it over KangarooTwelve/XKCP when you must keep Ethereum/Swarm Keccak-256 output and want a native Rust crate. XKCP also ships parallel Keccak-p[1600] times2/times4 kernels, but in C. BLAKE3 or blake2_simd are faster choices only when you are free to change the hash function.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | digest 0.11 (optional, default-on feature 'digest'); otherwise none (std required: dispatch uses is_x86_feature_detected!, std::env and a std atomic) |
| **Minimum toolchain** | Rust 1.92 (edition 2024) |
| **Platforms** | x86-64 (SSE2 baseline 2-wide; AVX2 4-wide; AVX-512F+AVX2 8-wide, runtime-detected), aarch64 (NEON 2-wide), wasm32 (2-wide only with +simd128 at compile time, else scalar), other targets scalar |
| **Thread safety** | Not documented; the batch functions are pure and the only shared state is an atomic cache of the detected width, and Keccak256 is a plain owned value |
| **Drop-in for the baseline** | partial — keccak256()/Keccak256 match alloy's Keccak256 shape and digest traits, but they are scalar; the speedup needs the new equal-length batch API |

## Gotchas

- The detected width and the KECCAK_BATCH_NO_AVX512 / KECCAK_BATCH_NO_AVX2 caps are read once and cached per process, so set the env vars before the first hash
- keccak256_many::&lt;1&gt; is a compile error, but keccak256_many_into accepts a count of 0 or 1 and runs the scalar path
- The README numbers don't compose: \~5.4x over scalar divided by keccak-asm's \~1.3x over scalar gives \~4.2x, yet the README claims \~5.5x over keccak-asm
- AVX-512 kernels require only avx512f (plus avx2 for batch tails); on parts where AVX-512 downclocks, the README suggests capping to AVX2

## Known shortcomings

- Created 2026-07-02, \~3.2k downloads. CPU given only as 'Zen-class'; the keccak-asm/tiny-keccak comparison exists only in README prose, not in perf.rs or the benchmark code.
- README ratios do not compose (5.4x / 1.3x is \~4.2x, but it claims 5.5x over keccak-asm) and the external baselines come from an unpublished harness; hardware unnamed (PR #15 hints Ryzen 9 7940HS). Equal-length batches only (panics otherwise); single hashes run scalar; legacy Keccak-256 (0x01 padding), not SHA-3; aarch64 capped at 2-wide. AGPL; 1 star, 1 reverse dependency; MSRV 1.92.

## Caveats and trade-offs

Young, single-organization (nxm-rs), 1-star project: repo created 2026-07-02 (not 2026-09-24), crate 0.1.0 published on crates.io 2026-07-02 (\~3.2k downloads) though the README still calls it pre-release. Benchmark hardware is only 'a Zen-class AVX-512 part' (no exact CPU model). The external-baseline comparisons (tiny-keccak, keccak-asm) are README prose only: the public examples/perf.rs and benches/keccak.rs measure only the crate's own scalar vs batched paths, and keccak-asm is not even a dev-dependency. Batch speedup applies only to many equal-length independent inputs; single-message hashing is scalar. Legacy Keccak-256 (0x01 padding), not FIPS-202 SHA3. AGPL-3.0-or-later copyleft.

Pre-release (marked pre-release in repo badge), only implements legacy 0x01-padding Keccak-256 (not full SHA3-256 with 0x06 padding), AGPL-3.0 copyleft license restricts embedding in proprietary C++ code without a compatible C API wrapper, no C/C++ bindings provided (Rust crate only, though a cdylib could be built).

## Maintenance

Active but very young: created 2026-07-02, one crates.io release (0.1.0, \~3.2k downloads, single reverse dependency nectar-primitives), last main commit 2026-07-24, README still says pre-release. AGPL-3.0-or-later limits use to copyleft-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives first-party speedups (\~5.4x/\~4-5x AVX-512 over own scalar; scalar at parity with tiny-keccak; keccak-asm \~1.3x over scalar; 8-wide \~5.5x over keccak-asm) measured on an unnamed 'Zen-class AVX-512 part'; no exact CPU model, and the public harness (examples/perf.rs, benches/keccak.rs) does not include the tiny-keccak/keccak-asm comparisons, so it cannot be A.
- **Verifier notes:** Numbers match README exactly. last_commit 2026-07-24 on main is correct (repo pushed_at 2026-09-24 reflects activity on side branches such as perf/absorb-fast-path). License AGPL-3.0 (Cargo.toml says AGPL-3.0-or-later) is OSI, so copyable holds.
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/nxm-rs/keccak-batch>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/README.md>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/examples/perf.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/benches/keccak.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/Cargo.toml>
  - <https://crates.io/api/v1/crates/keccak-batch>
- **Sources the enricher read:**
  - <https://github.com/nxm-rs/keccak-batch>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/README.md>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/Cargo.toml>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/rust-toolchain.toml>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/CHANGELOG.md>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/lib.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/dispatch.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/lane.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/lane/avx512.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/lane/simd128.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/sponge.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/f1600.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/src/single.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/examples/perf.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/benches/keccak.rs>
  - <https://github.com/nxm-rs/keccak-batch/blob/main/.github/workflows/ci.yml>
  - <https://github.com/nxm-rs/keccak-batch/issues?q=is%3Aissue>
  - <https://github.com/nxm-rs/keccak-batch/pulls?q=is%3Apr>
  - <https://github.com/nxm-rs/keccak-batch/pull/15>
  - <https://github.com/nxm-rs/keccak-batch/pull/7>
  - <https://github.com/nxm-rs/keccak-batch/pull/6>
  - <https://crates.io/api/v1/crates/keccak-batch>
  - <https://crates.io/api/v1/crates/keccak-batch/reverse_dependencies>
  - <https://crates.io/api/v1/crates/keccak-asm>
  - <https://github.com/nxm-rs/nectar>
  - <https://github.com/XKCP/XKCP>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/nxm-rs/keccak-batch`) · [data/wave7/enrich/raw/github_com_nxm_rs_keccak_batch.json](../../../data/wave7/enrich/raw/github_com_nxm_rs_keccak_batch.json) (enrichment confidence 0.4)

</details>
