# blake2b_simd / blake2s_simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust BLAKE2b/2s/2bp/2sp crates with AVX2/SSE4.1 kernels; its BLAKE2b hashes about 1.8x faster than OpenSSL SHA-512 in its own benchmark.

| | |
|---|---|
| **Beats** | OpenSSL SHA-512 / OpenSSL SHA-1 (also compared to libsodium BLAKE2b) |
| **Claimed result** | blake2b_simd BLAKE2b: 2.81 cpb vs OpenSSL SHA-512: 5.11 cpb (\~1.8x); vs OpenSSL SHA-1: 3.51 cpb (\~1.25x); vs libsodium BLAKE2b: 3.07 cpb (\~1.09x). blake2s_simd many::hash: 1.31 cpb, blake2b_simd many::hash: 1.43 cpb |
| **Workload** | 1,000,000-byte in-memory inputs hashed by BLAKE3, blake2b_simd/blake2s_simd (single, many::hash, BLAKE2bp/BLAKE2sp), libsodium BLAKE2b and OpenSSL SHA-1/SHA-512. Each algorithm runs in 100 worker processes across all 512 input offsets. Total time is averaged (a mean, not a median) and reported as cycles per byte (benches/bench_multiprocess). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-8250U (Kaby Lake Refresh) |
| **Compiler and flags** | rustc 1.40.0, `cargo run --release` (default release profile with no target-cpu flag; the crate picks SIMD paths by runtime CPU-feature detection). clang 9.0.1 was used only for Samuel Neves' blake2-avx2 C reference, built with `-mavx2` in benches/blake2-avx2-sneves/build.rs. OpenSSL 1.1.1d and libsodium 1.0.18 were linked through the openssl and libsodium-ffi crates, and the build flags of those libraries are not stated. |
| **Adoption** | 144 stars; crates.io: blake2b_simd \~57.8M downloads, blake2s_simd \~23.0M downloads |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/oconnor663/blake2_simd) · [benchmark](https://github.com/oconnor663/blake2_simd/blob/master/README.md) |

## Verdict

The README's bench_multiprocess table comes from one Intel Core i5-8250U laptop, which has no SHA-NI: rustc 1.40.0 with cargo --release, OpenSSL 1.1.1d, libsodium 1.0.18, hashing 1 MB in-memory inputs in 100 processes across all 512 offsets. It shows BLAKE2b at 2.81 cpb against OpenSSL SHA-512 at 5.11 (1.82x), many::hash/BLAKE2bp at 1.43/1.44 cpb (about 3.5x vs SHA-512, 2.45x vs SHA-1 at 3.51), and only 1.09x over libsodium's BLAKE2b at 3.07. The harness itself prints GB/s, and the README does not say how it converted that to cycles per byte.

## Use it when

- Rust code on x86-64 with AVX2 that needs BLAKE2 specifically, for example Argon2, Zcash/halo2, Substrate or multihash compatibility (crates.io lists 234 reverse dependencies, including sp-crypto-hashing, rust-argon2 and ff).
- Hashing many independent messages in batches of at least many::degree() (4 for BLAKE2b and 8 for BLAKE2s on AVX2), such as content-addressed chunks or Merkle leaves, where hash_many roughly doubles per-core throughput over one-at-a-time BLAKE2b.
- Replacing SHA-512 or SHA-1 in a design you control, on CPUs without SHA-NI, where the README's 1 MB benchmark shows BLAKE2b at 2.81 cpb against OpenSSL SHA-512 at 5.11 cpb.
- Keyed hashing or MAC use, via BLAKE2's built-in key/salt/personal parameters, which avoid HMAC's double hashing (the author's explanation in issue #32).
- Embedded or no_std Rust that wants a spec-complete, fuzzed, portable BLAKE2 (CI covers armv7, aarch64, i586 and big-endian powerpc64/s390x).

## Skip it when

- Anywhere SHA-256/SHA-512/SHA-1 output is required (interop, FIPS, certificates, git objects). The digests differ, and BLAKE2bp/BLAKE2sp also differ from plain BLAKE2b/BLAKE2s.
- New designs where you are free to pick a hash. BLAKE3, from the same author, ran at 0.95 cpb on the same laptop, about 3x faster than blake2b_simd's BLAKE2b at 2.81, and the author points users to it (issue #22).
- ARM, POWER and other non-x86 targets. There is no NEON kernel, so every call uses the portable Rust code (MAX_DEGREE = 1), which issue #7 found slightly slower than blake2-rfc on a Neoverse N1.
- x86 CPUs without AVX2 hashing a single message. Single-message BLAKE2b has only an AVX2 kernel (a code comment says the SSE compress1 was never ported), so SSE4.1-only machines fall back to portable code for plain BLAKE2b. SSE4.1 is only used for 2-way many/BLAKE2bp and for BLAKE2s.
- C/C++ projects. There is no C header or FFI layer, so Neves' blake2-avx2 C code (the ancestor, vendored in benches/) or libsodium is the natural pick there.

## How it is fast

The SIMD kernels are Rust intrinsic ports of Samuel Neves' blake2-avx2. Single-message BLAKE2b runs a one-lane AVX2 compression with row diagonalization and shift-or rotations; the code comments note these beat the byte-shuffle rotations on recent chips because of an LLVM bug, and LLVM turns them into AVX-512 rotates when that is enabled. The bigger win is multi-lane hashing: BLAKE2bp and many::hash_many transpose the state and message words of 4 independent BLAKE2b jobs (8 for BLAKE2s) across 256-bit AVX2 registers and compress them together, roughly doubling throughput over one-lane BLAKE2b. The best kernel is picked at runtime with is_x86_feature_detected!.

## Compared with alternatives

Pick this over BLAKE3 only when the BLAKE2 digest itself is required; BLAKE3 is about 3x faster on the same machine and has more SIMD backends. Over the SHA-256 siblings (sha2-with-c-intrinsic, ISA-L multi-buffer SHA, sha256-simd), pick it when you can drop SHA-2 compatibility and want a maintained, widely used Rust crate with built-in multi-message batching.

## Integration

| | |
|---|---|
| **Form** | crate (blake2b_simd, blake2s_simd; CLI in blake2_bin) |
| **Dependencies** | arrayvec 0.7, constant_time_eq 0.4.2 (arrayref was removed in 1.0.5) |
| **Minimum toolchain** | Rust edition 2024. CI's MSRV job builds with 1.85.1, but Cargo.toml declares no rust-version and the author does not treat MSRV bumps as breaking (issue #30). |
| **Platforms** | x86/x86-64 with runtime AVX2 and SSE4.1 dispatch; all other targets use portable Rust (tested in CI on aarch64 macOS, armv7, aarch64 Linux, i586/i686, powerpc64 and s390x); no_std is supported |
| **Thread safety** | Not documented. Params, State and Hash are plain owned structs with no shared mutable state (only CPU-feature detection through std), so use one State per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- With default-features = false (no_std), runtime detection is off and only portable code runs, unless the build enables the CPU features at compile time, for example RUSTFLAGS="-C target-feature=+avx2" (per a guts.rs comment).
- Params setters panic on out-of-range values (hash_length over 64, key over 64 bytes, and so on). Hash equality is constant-time, but as_bytes()/as_array() comparisons are not.
- Debug builds are dramatically slower. In issue #22 a user measured 17 s in a debug build versus 158 ms with --release on an \~80 MB file.
- BLAKE2bp throughput changes by several percent with the input buffer's offset modulo 512 bytes (issue #8), which is why the benchmark averages over all 512 offsets. Your allocator's alignment decides where you land.

## Known shortcomings

- Headline ratios are cross-algorithm (BLAKE2b/BLAKE2bp vs OpenSSL SHA-512/SHA-1); against libsodium's BLAKE2b the gain is only \~1.09x. Reported numbers are means, not medians. Rust-only.
- Same machine: BLAKE3 is \~3x faster. Single-message BLAKE2b has only an AVX2 kernel (no SSE); non-x86 targets use portable code with no NEON (#7: slower than blake2-rfc on Neoverse). Numbers are from 2020 on one machine. Rust only, no C ABI.

## Caveats and trade-offs

The numbers were last updated in the README on 2020-01-30 (rustc 1.40, OpenSSL 1.1.1d, libsodium 1.0.18) and come from one laptop. The bench crate has since been updated (edition 2024, blake3 1.8.3), so a rerun today uses different code and toolchains. The main comparison crosses algorithms. BLAKE2b, BLAKE2bp and many::hash are not drop-in replacements for SHA-512/SHA-1, since they produce different digests, and BLAKE2bp is a separate parallel mode. Against the same algorithm (libsodium BLAKE2b, 3.07 cpb), the win is only \~1.09x (derived from page data). The i5-8250U has no SHA-NI, so OpenSSL SHA-1 ran without hardware SHA extensions, and the margin would be smaller on SHA-NI CPUs. The bench code measures nanoseconds, and the README does not say how it converted them to cpb. Only first-party runs on a single machine exist.

Pure Rust with dynamic AVX2 CPU-feature detection at runtime; SIMD kernel is a Rust port of Samuel Neves' sneves/blake2-avx2 C code. Not C++-native (usable from C++ only via FFI/cbindgen), no_std support optional. Benchmark numbers are from 2019-2020 hardware (i5-8250U, OpenSSL 1.1.1d), so absolute cycles/byte on current CPUs/OpenSSL 3.x will differ, though the relative BLAKE2b-vs-SHA-512 gap is architectural and should persist.

## Maintenance

Actively maintained, if slowly: v1.0.5 (2026-08-20) removed arrayref after its newest crates.io release turned out to be malicious, and there were dependency and edition updates in 2025-26. It is MIT, copyable, and has \~58M (blake2b_simd) and \~23M (blake2s_simd) downloads. The 2020 benchmark was never rerun, and the bench crate was bumped to edition 2024 without code changes; it still calls env::set_var outside an unsafe block, which that edition rejects, so it may not build unmodified (not verified by building).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance section gives a table from benches/bench_multiprocess/src/main.rs. It has OpenSSL SHA-1 (3.51 cpb) and SHA-512 (5.11 cpb) rows next to blake2b_simd BLAKE2b (2.81), many::hash (1.43) and BLAKE2bp (1.44), and states rustc 1.40.0, clang 9.0.1, `cargo run --release` and an Intel Core i5-8250U. Public code, compiler, build mode and CPU model are all present, so tier A holds.
- **Verifier notes:** Every number in claimed_speedup matches the README table exactly, and the derived ratios are correct (5.11/2.81 = 1.82x, 5.11/1.43-1.44 = 3.55-3.57x, 3.51/1.43-1.44 = 2.44-2.45x). The repo is active (v1.0.5 on 2026-08-20 removed the compromised arrayref dependency), MIT, not a fork, and widely used on crates.io. I corrected the record's claim about what clang built and changed 'median' to 'mean'.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/oconnor663/blake2_simd/blob/master/README.md#performance>
  - <https://raw.githubusercontent.com/oconnor663/blake2_simd/master/README.md>
  - <https://github.com/oconnor663/blake2_simd>
  - <https://raw.githubusercontent.com/oconnor663/blake2_simd/master/benches/bench_multiprocess/Cargo.toml>
  - <https://raw.githubusercontent.com/oconnor663/blake2_simd/master/benches/bench_multiprocess/src/main.rs>
  - <https://raw.githubusercontent.com/oconnor663/blake2_simd/master/benches/blake2-avx2-sneves/build.rs>
  - <https://raw.githubusercontent.com/oconnor663/blake2_simd/master/Cargo.toml>
  - <https://crates.io/api/v1/crates/blake2b_simd>
  - <https://crates.io/api/v1/crates/blake2s_simd>
- **Sources the enricher read:**
  - <https://github.com/oconnor663/blake2_simd>
  - <https://github.com/oconnor663/blake2_simd/blob/master/README.md>
  - <https://github.com/oconnor663/blake2_simd/blob/master/README.md#performance>
  - <https://github.com/oconnor663/blake2_simd/tree/master>
  - <https://github.com/oconnor663/blake2_simd/blob/master/Cargo.toml>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/Cargo.toml>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2s/Cargo.toml>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/README.md>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/lib.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/guts.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/many.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/blake2bp.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/avx2.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2b/src/sse41.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2s/src/guts.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/blake2s/src/lib.rs>
  - <https://github.com/oconnor663/blake2_simd/blob/master/.github/workflows/ci.yml>
  - <https://github.com/oconnor663/blake2_simd/blob/master/benches/bench_multiprocess/Cargo.toml>
  - <https://github.com/oconnor663/blake2_simd/blob/master/benches/bench_multiprocess/src/main.rs>
  - <https://github.com/oconnor663/blake2_simd/commits/master>
  - <https://github.com/oconnor663/blake2_simd/commit/061b001f>
  - <https://github.com/oconnor663/blake2_simd/commit/5d4ae823>
  - <https://github.com/oconnor663/blake2_simd/issues?q=is%3Aissue>
  - <https://github.com/oconnor663/blake2_simd/pulls?q=is%3Apr>
  - <https://github.com/oconnor663/blake2_simd/issues/1>
  - <https://github.com/oconnor663/blake2_simd/issues/4>
  - <https://github.com/oconnor663/blake2_simd/issues/7>
  - <https://github.com/oconnor663/blake2_simd/issues/8>
  - <https://github.com/oconnor663/blake2_simd/issues/20>
  - <https://github.com/oconnor663/blake2_simd/issues/22>
  - <https://github.com/oconnor663/blake2_simd/issues/30>
  - <https://github.com/oconnor663/blake2_simd/issues/32>
  - <https://crates.io/api/v1/crates/blake2b_simd>
  - <https://crates.io/api/v1/crates/blake2s_simd>
  - <https://crates.io/api/v1/crates/blake2b_simd/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=blake2b_simd&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/oconnor663/blake2_simd`) · [data/wave7/enrich/raw/github_com_oconnor663_blake2_simd.json](../../../data/wave7/enrich/raw/github_com_oconnor663_blake2_simd.json) (enrichment confidence 0.82)

</details>
