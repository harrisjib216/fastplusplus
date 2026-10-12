# ChaCha20-BLAKE3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust committing AEAD (ChaCha20 + keyed-BLAKE3 MAC); about 2x RustCrypto XChaCha20-Poly1305 and AES-256-GCM on 1-10 MB messages.

| | |
|---|---|
| **Beats** | XChaCha20-Poly1305 and AES-256-GCM via RustCrypto's pure-Rust crates (chacha20poly1305 0.11.0-rc.2 and aes-gcm 0.11.0-rc.2 per benchmarks/Cargo.toml), not OpenSSL or libsodium |
| **Claimed result** | Against XChaCha20-Poly1305: about 1.3x at 64 KB (2,153 vs 1,636 MB/s) and about 2x at 1 to 10 MB (3,297 to 3,353 vs 1,654 to 1,664 MB/s). Against AES-256-GCM: about 1.5x at 64 KB (2,153 vs 1,475 MB/s) and about 2.2x at 1 to 10 MB (3,297 to 3,353 vs 1,476 to 1,477 MB/s). All ratios derived from page data. It is slower at small sizes: about 1.1 to 1.5x slower than XChaCha20-Poly1305 (64 B: 103 vs 116 MB/s; 1 KB: 523 vs 767 MB/s) and about 2.5 to 5.2x slower than AES-256-GCM (64 B: 103 vs 540 MB/s; 1 KB: 523 vs 1,287 MB/s). |
| **Workload** | Single-core AEAD encrypt throughput at message sizes 64 B, 1 KB, 64 KB, 1 MB, and 10 MB |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9R45 (virtualized, AWS ma8.xlarge) |
| **Compiler and flags** | No rustc version is stated. The table does not state flags. The repo Makefile `bench` target runs RUSTFLAGS="-C target-cpu=native --cfg chacha20_force_avx2" cargo bench (criterion 0.5), and .cargo/config.toml also sets target-cpu=native. The aes_avx256/aes_avx512 cfgs are commented out. |
| **Adoption** | 103 stars |
| **Last commit** | 2026-01-15 |
| **Links** | [repository](https://github.com/skerkour/chacha20-blake3) · [benchmark](https://github.com/skerkour/chacha20-blake3#performance) |

## Verdict

The README table is first-party, single-core encryption on a virtualized AMD EPYC 9R45 (AWS ma8.xlarge), with no flags or rustc version stated; the repo's make bench target and .cargo/config.toml both use target-cpu=native. At 1-10 MB it measured 3,297-3,353 MB/s, against 1,654-1,664 MB/s for RustCrypto XChaCha20-Poly1305 and 1,476-1,477 MB/s for RustCrypto AES-256-GCM (0.11.0-rc.2 crates). It wins at 64 KB (2,153 vs 1,636 and 1,475 MB/s) and loses at 64 B and 1 KB. The shipped criterion bench covers only 64 B-64 KB with a 128-byte AAD, so the 1 MB and 10 MB rows cannot be reproduced from it. The AES-GCM arm runs without the aes crate's VAES cfgs, which open issue #4 argues understates AES-GCM on Zen CPUs.

## Use it when

- Rust code encrypting large one-shot buffers (64 KB and up, best at 1 MB and up), such as files, backups or object-storage blobs, where the author measured about 2x RustCrypto XChaCha20-Poly1305 and 2.2x RustCrypto AES-256-GCM.
- Designs that use one long-lived key with random 24-byte nonces and want a committing AEAD; the README claims full context commitment.
- Targets without AES hardware (microcontrollers, WASM with simd128, older ARM) when you control both ends of the channel and AES-GCM would be slow.
- no_std builds: with default-features = false you still get the in-place detached API and compile-time SIMD selection.

## Skip it when

- Small messages. At 64 B-1 KB it is 1.1-1.5x slower than XChaCha20-Poly1305 and 2.5-5.2x slower than AES-256-GCM in the author's own table.
- Interoperability or compliance needs (TLS, FIPS, JOSE/COSE). It is a non-standard construction specified only on the author's site, IANA/JOSE/COSE registration is still an open issue (#2), and the spec's KDF choice is questioned in open issue #11.
- Portable x86-64 binaries built without -C target-cpu=native. The SIMD functions have no #[target_feature] attribute, and unmerged PR #12 reports about 55 MB/s instead of about 1.2 GB/s on an AVX2 i7-9750H as a result.
- Streaming or larger-than-memory data. There is only a one-shot API (a streaming API is requested in open issue #1), and each call makes two passes over the buffer (encrypt, then MAC).
- Machines with AES instructions where you just want the fastest AEAD. The AES-based siblings (AEGIS, HiAE, ROCCA-S) report tens to hundreds of Gbps, against about 3.3 GB/s here.

## How it is fast

The bundled `chacha` crate computes ChaCha blocks in a word-sliced (one block per SIMD lane) layout: 16 blocks per iteration with AVX-512 (_mm512_rol_epi32 rotates), 8 with AVX2, and 4 with NEON or WASM simd128. A scalar fallback covers inputs under 128 bytes and machines without SIMD. Authentication uses the blake3 crate, whose x86_64 build defaults to hand-written SSE4.1/AVX2/AVX-512 assembly (NEON C intrinsics on aarch64), so the MAC also scales with vector width. In the author's table the RustCrypto baselines plateau near 1.5-1.7 GB/s from 64 KB up while this construction reaches 3.3 GB/s. A per-message BLAKE3 KDF call plus a MAC finalization makes it slower than both baselines at 64 B-1 KB.

## Compared with alternatives

Pick it over chacha20poly1305-simd when messages are large (64 KB and up), you want key commitment and random 24-byte nonces, and you do not need RFC 8439 wire compatibility; chacha20poly1305-simd is the better choice for small messages and standard ChaCha20-Poly1305. Over the AES-based siblings (libaegis, HiAE, ROCCA-S), pick it only when the target lacks AES instructions or you want one algorithm across microcontrollers, WASM and servers.

## Integration

| | |
|---|---|
| **Form** | crate (upstream recommends a git dependency on the main branch; the crates.io release is a third-party fork) |
| **Dependencies** | blake3 1.x (default features off, with neon and wasm32_simd; on x86_64 it builds hand-written assembly and on aarch64 the NEON code needs a C compiler), constant_time_eq 0.4, the in-repo `chacha` crate (path dependency), and optional zeroize 1. |
| **Minimum toolchain** | Rust 1.85 (edition 2024, rust-version = "1.85") |
| **Platforms** | x86_64: AVX2/AVX-512 chosen by runtime detection with the std feature, or by compile-time target features in no_std builds. aarch64: NEON assumed. wasm32: simd128 at compile time only. Everything else uses the portable scalar fallback. |
| **Thread safety** | Not documented. ChaCha20Blake3 holds only the 32-byte key and every method takes &self, so one instance can be shared across threads; the inner ChaCha state is created per call. |
| **Drop-in for the baseline** | no |

## Gotchas

- The crates.io crate chacha20-blake3 (0.9.11-0.10.0) is published by a third party from the paddor/chacha20-blake3 fork. That fork includes changes upstream has not merged: the target_feature fix, zeroization fixes, a Session API, and SSE2/AVX2 small-message paths. The upstream Cargo.toml is still at 0.9.11, so `cargo add` does not give you upstream.
- Upstream's zeroize feature does not wipe everything. decrypt_in_place_detached never wipes kdf_out, Zeroizing::new(encryption_key).zeroize() wipes a copy of a Copy array, and the derived authentication-key copies are never wiped. The fork commit 'Zeroize all derived key material in AEAD' addresses this.
- The tag is 32 bytes, 16 more than GCM or Poly1305. The Go port in skerkour/stdx-go (crypto/chacha20blake3) declares NonceSize = 32, while the Rust crate and that port's own error text say 24, so verify cross-language interop before you rely on it.
- The maturity signals conflict. The author's January 2026 announcement title calls ChaCha20-BLAKE3 'stable and production-ready', but the bundled chacha crate's README says 'preliminary release, DO NOT USE IN PRODUCTION'. No third-party audit or cryptanalysis is documented.

## Known shortcomings

- Slower than XChaCha20-Poly1305 at small sizes (1.1-1.5x) and only \~2.2x faster than AES-GCM at 1-10 MB; the benchmark code stops at 64 KB, so the 1 MB/10 MB rows cannot be rerun from the repo; no rustc version. Non-standard AEAD construction (ChaCha20 + BLAKE3) with no external review.
- SIMD functions lack #[target_feature]: open PR #12 reports \~55 MB/s instead of \~1.2 GB/s in a non-native build. The crates.io crate is a third-party fork (paddor); upstream recommends a git dependency. Zeroization incomplete on the decrypt path; no streaming API; 32-byte tag; the Go port's nonce size (32) differs from the Rust version (24). AES-GCM comparison on ARM lacks VAES (#4).

## Caveats and trade-offs

The benchmark is first-party. The README calls all three implementations, including ChaCha20-BLAKE3 itself, 'pure-Rust, non-optimized'. The shipped criterion bench (benchmarks/benches/encrypt.rs) covers 64 B to 64 KB and passes a 128-byte AAD on every call, so the README's 1 MB and 10 MB rows are not produced by the current bench code. The AES-256-GCM arm is RustCrypto aes-gcm without the VAES cfgs enabled, which may explain its low throughput of about 1.5 GB/s. No rustc version is stated, and nothing is compared against OpenSSL or libsodium. The author remarks cited earlier (an optimized build being about 30% faster, and surprise at AES-GCM being slow) are not in the README and were not verified, because kerkour.com was not fetched.

New, non-standardized AEAD construction (not NIST/IETF standardized like GCM/Poly1305); requires a 24-byte nonce; committing-AEAD design adds security (full context commitment) but is slower than both baselines for small messages

## Maintenance

The upstream repo is MIT-licensed with 103 stars; its last commit was 2026-01-15, and PR #12, the 2026-04 portable-build performance fix, has had no maintainer reply. The more recently updated crates.io release comes from a third-party fork, so 'active' is generous; pin a git revision or vendor the two small crates.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table gives first-party throughput against RustCrypto XChaCha20-Poly1305 and AES-256-GCM on an EPYC 9R45. The criterion bench code is public (benchmarks/benches/encrypt.rs). No rustc version is stated, and the shipped bench stops at 64 KB, so the 1 MB and 10 MB rows cannot be reproduced from it. That makes it C, not A.
- **Verifier notes:** The README numbers match the record's figures. The only error was in the slowdown clause, where 'about 2 to 5x slower than both' is wrong: against XChaCha20-Poly1305 it is only 1.1 to 1.5x slower. Metadata checked: MIT, 103 stars, not a fork, not archived, last commit 2026-01-15, active.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/skerkour/chacha20-blake3>
  - <https://github.com/skerkour/chacha20-blake3#performance>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/Makefile>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/.cargo/config.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/benchmarks/benches/encrypt.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/Cargo.toml>
  - <https://hn.algolia.com/api/v1/items/46644084>
  - <https://hn.algolia.com/api/v1/items/39204412>
- **Sources the enricher read:**
  - <https://github.com/skerkour/chacha20-blake3>
  - <https://github.com/skerkour/chacha20-blake3#performance>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/Cargo.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha20-blake3/Cargo.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha20-blake3/README.md>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha20-blake3/chacha20_blake3.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha20-blake3/tests/mod.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/Cargo.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/README.md>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/src/lib.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/src/chacha_avx512.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/src/chacha_avx2.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/chacha/src/chacha_neon.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/benchmarks/benches/encrypt.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/benchmarks/benches/chacha.rs>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/Makefile>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/.cargo/config.toml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/.github/workflows/test.yml>
  - <https://github.com/skerkour/chacha20-blake3/blob/main/.github/workflows/benchmarks.yml>
  - <https://github.com/skerkour/chacha20-blake3/issues?q=is%3Aissue>
  - <https://github.com/skerkour/chacha20-blake3/pull/12>
  - <https://github.com/skerkour/chacha20-blake3/branches>
  - <https://github.com/paddor/chacha20-blake3>
  - <https://github.com/paddor/chacha20-blake3/commit/9a4fc2b5ec925bc7d80f11cbd99e1934a08f1327>
  - <https://crates.io/api/v1/crates/chacha20-blake3>
  - <https://crates.io/api/v1/crates/chacha20-blake3/versions>
  - <https://crates.io/api/v1/crates/chacha12-blake3>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/Cargo.toml>
  - <https://github.com/skerkour/stdx-go/blob/main/crypto/chacha20blake3/chacha20_blake3.go>
  - <https://hn.algolia.com/api/v1/items/46644084>
  - <https://hn.algolia.com/api/v1/items/39204412>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/skerkour/chacha20-blake3`) · [data/wave7/enrich/raw/github_com_skerkour_chacha20_blake3.json](../../../data/wave7/enrich/raw/github_com_skerkour_chacha20_blake3.json) (enrichment confidence 0.7)

</details>
