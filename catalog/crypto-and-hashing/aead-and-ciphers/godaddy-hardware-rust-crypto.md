# hardware-rust-crypto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Hardware-only AES-256-GCM/GCM-SIV crate for Rust with compact, zeroized key state; faster than ring and RustCrypto on Apple M4.

| | |
|---|---|
| **Beats** | ring (BoringSSL-derived) and RustCrypto aes-gcm crate |
| **Claimed result** | Allocation-free encrypt beats ring at every size from 16 B to 16 KiB: 26.8 vs 57.8 ns at 16 B, 130.5 vs 216.6 ns at 1 KiB, and 1.77 vs 2.38 us at 16 KiB (8.64 vs 6.41 GiB/s). Decrypt also wins: 1.79 vs 2.19 us at 16 KiB. Against a default-build RustCrypto aes-gcm 0.10 it is 14x-43x faster. Against RustCrypto with its ARMv8 cfgs it is 3.4x-5.0x faster at &gt;=256 B, but only \~1.3x-1.7x at 16-64 B. ring's key setup is faster (86 vs 94 ns). |
| **Workload** | AES-256-GCM allocation-free encrypt/decrypt (encrypt_to/decrypt_to), Criterion benchmarks over sizes 16B-16KiB |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max, macOS (Darwin 25.4) |
| **Compiler and flags** | rustc 1.96.0, cargo bench (Criterion, default release build); RustCrypto 'armv8 cfgs' variant built with RUSTFLAGS="--cfg aes_armv8 --cfg polyval_armv8" |
| **Adoption** | 1 star; 3,375 crates.io downloads (v1.0.1) |
| **Last commit** | 2026-06-21 |
| **Links** | [repository](https://github.com/godaddy/hardware-rust-crypto) · [benchmark](https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/benchmarks.md) |

## Verdict

On one Apple M4 Max laptop (macOS, rustc 1.96.0, Criterion default release build, empty AAD), allocation-free AES-256-GCM encrypt_to took 26.8 ns at 16 B, 130.5 ns at 1 KiB and 1.77 us at 16 KiB (8.64 GiB/s), against ring 0.17's 57.8 ns, 216.6 ns and 2.38 us (6.41 GiB/s); decrypt_to was 1.79 vs 2.19 us at 16 KiB. It was 14x-43x faster than a default RustCrypto aes-gcm 0.10 build (software AES on aarch64), and 3.4x-5.0x faster than RustCrypto built with the armv8 cfgs from 256 B up but only about 1.3-1.7x at 16-64 B; ring was faster at key setup (86 vs 94 ns). These are single-run results with a stated +/-10% variance at sub-microsecond sizes, and no x86-64 numbers are published.

## Use it when

- Rust services on aarch64 (Graviton, Ampere, Apple Silicon) that use RustCrypto aes-gcm without the armv8 cfg flags: 14x-43x faster on M4 and no silent software-AES fallback.
- Workloads that hold many AES-256-GCM keys in memory, such as key caches and guarded-page key stores, where the 368 B zeroize-on-drop key state (11 keys per 4 KiB page vs 4 for RustCrypto) and caller-controlled placement matter.
- Encrypting records from 16 B to 16 KiB with AES-256-GCM, where the allocation-free encrypt_to beat ring on M4 at every size measured: about 1.2-1.5x in the fairest pre-sized-buffer comparison.
- Applications that want the library to own GCM nonce generation (per-instance counter over an OS-random 96-bit salt, re-salted on fork), or that need nonce-misuse-resistant AES-256-GCM-SIV, which ring does not offer.
- Teams that value published verification evidence: Kani, SAW, crux-mir, F\*, Z3 proofs of the glue code, Wycheproof and NIST CAVP vectors, dudect timing tests, and Miri and sanitizers in CI.

## Skip it when

- On x86-64 servers without re-benchmarking. No x86-64 numbers are published, there is no VAES/VPCLMULQDQ wide path yet (listed as a follow-up), and on x86-64 stock RustCrypto already detects AES-NI at runtime, so the 14x-43x figure does not apply there.
- When you need AES-128-GCM, other nonce or tag sizes, ChaCha20-Poly1305, or a fallback for CPUs without AES instructions (for example some embedded, older, or emulated targets). Construction fails on such CPUs.
- When you need a drop-in for ring or the RustCrypto aead traits, such as TLS/QUIC record layers with explicit nonces. The explicit-nonce and detached seal/open APIs sit behind the non-default, doc(hidden) hazmat-explicit-nonce feature, and no aead trait impls are provided.
- When compliance requires validated or independently audited crypto: the docs say it has had no independent third-party audit and has no CAVP/CMVP validation. The 'security audit' document is a multi-model agentic (AI) review.
- Tiny-message decrypt, where the gain over ring is within noise: 33.6 vs 36.6 ns at 16 B, inside the author's stated +/-10% variance. The allocating decrypt is slower than ring's in-place open at 16-64 B.

## How it is fast

The encrypt and decrypt loops are stitched: eight interleaved hardware AES-CTR chains (AESE/AESMC or AESENC) run in the same loop body as an eight-block aggregated GHASH. Eight precomputed Montgomery-form powers H^1..H^8 let eight carryless products be XOR-summed before one field reduction, so the AES and PMULL/PCLMULQDQ pipelines stay busy together. The round keys live in vector registers, the fused bulk path touches each byte once, and the \*_to APIs do no heap allocation. Against default RustCrypto on aarch64, most of the gain comes simply from using hardware AES/PMULL where stock aes-gcm silently runs fixsliced software AES unless built with --cfg aes_armv8 --cfg polyval_armv8.

## Compared with alternatives

Pick it over libaegis, HiAE, or Rocca when you must keep standard AES-256-GCM (or GCM-SIV) wire compatibility with ring, OpenSSL, or RustCrypto peers; those siblings are faster but use different, newer AEAD constructions. Pick it over chacha20poly1305-simd when you need AES-GCM, compact placeable key state, or formal-verification evidence, and you run on hardware with AES and carryless-multiply instructions.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | getrandom 0.3, subtle 2.6, zeroize 1.8, libc 0.2 (Unix only, for pthread_atfork fork detection) |
| **Minimum toolchain** | Rust 1.88 (edition 2021); requires std (uses Vec/Box, no no_std mode documented) |
| **Platforms** | x86-64 with AES-NI + PCLMULQDQ; aarch64 with ARMv8 AES + PMULL; CI covers Linux x64/arm64, macOS arm64, Windows x64/arm64. Other CPUs fail at construction with UnsupportedCpu. |
| **Thread safety** | Not documented explicitly. Nonce-generating encrypt/encrypt_to take &mut self (per-instance nonce counter), so sharing one key handle across threads for encryption needs external locking or per-thread instances (each gets its own OS-random salt). decrypt takes &self. |
| **Drop-in for the baseline** | partial: it produces standard AES-256-GCM ciphertexts that interoperate byte-for-byte with ring, RustCrypto and OpenSSL, but the API differs from both. The default wire format is ciphertext\|\|tag\|\|nonce with a library-generated nonce, and ring-style explicit-nonce seal/open needs the hazmat-explicit-nonce feature. |

## Gotchas

- The envelope puts the nonce at the end (ciphertext||tag||nonce), not the common nonce||ciphertext||tag. Peers using other libraries must split it the same way.
- Decrypt writes plaintext before the final tag check and zeroizes the plaintext-length prefix of the caller buffer on failure; do not read the output buffer on Err.
- The headline ring encrypt benchmark times ring's seal_in_place_append_tag on an exact-capacity Vec clone, so the tag append reallocates inside the timed loop. The pre-sized nonce-appended table is fairer: 28.1 vs 41.6 ns at 16 B and 1.77 vs 2.08 us at 16 KiB.
- It vendors code from rand_aes 0.7.0 and RustCrypto ghash 0.5.1 / polyval 0.6.2 (recorded in NOTICE), so upstream fixes do not flow in automatically. On aarch64, ARMv8.4 PSTATE.DIT is not set (a documented constant-time residual).

## Known shortcomings

- Measured on Apple M4 Max only (no x86 numbers). Against RustCrypto's armv8 backend the gain is 3.4-5.0x only from 256 bytes (1.3-1.7x at 16-64 B). Vendors rand_aes and RustCrypto ghash/polyval. Rust-only.
- Headline ring comparison times ring's Vec reallocation; a fair comparison is only 1.2-1.5x (28.1 vs 41.6 ns at 16 B; 1.77 vs 2.08 µs at 16 KiB). The 14-43x over RustCrypto is an aarch64 default-build artifact. Single M4 laptop run (±10%), no x86 or VAES path. AES-256-GCM only with no software fallback; nonce is appended to the ciphertext (explicit nonce needs the hazmat feature); no AEAD traits. The 'audit' document is an AI review. 1 star, quiet since 2026-06-21.

## Caveats and trade-offs

This is a single-run laptop benchmark. The author states +/-10% run-to-run variance at sub-microsecond sizes and says to read results as 'tie/win/lose, not exact ratios' and to re-run on target Linux x86_64 hardware before integration decisions; no x86_64 numbers are published. The 14x-43x figure is against a RustCrypto build whose hardware AES is off by default on aarch64. It is not a GitHub fork, but per its NOTICE it vendors and adapts hasenbanck/rand_aes 0.7.0 (AES) and RustCrypto ghash/polyval backends. OpenSSL is used only for interop tests, not benchmarks. Only AES-256 is supported. The project has only 1 GitHub star.

AES-256-only (no AES-128), hardware-instruction-only design (no software fallback, so it hard-fails on CPUs lacking AES-NI/ARMv8 crypto extensions); extensively formally verified (Kani, SAW, crux-mir, F\*, Z3) as its other main selling point besides speed

## Maintenance

Released as 1.0.1 on 2026-06-20; last commit 2026-06-21, 1 star, no open issues, 3,375 crates.io downloads and one reverse dependency (pq-modern-rust-tls). It is Apache-2.0 and backed by an unusually heavy CI proof and test battery, but has not been independently audited and has been quiet for three months.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md has tables against ring and RustCrypto aes-gcm, with the exact reproduction commands. The Criterion benchmark code is public (benches/aes_gcm.rs). The page states rustc 1.96.0, a default release build plus the stated RUSTFLAGS cfg variant, and an Apple M4 Max.
- **Verifier notes:** The numbers match docs/benchmarks.md. The record overstated the win over RustCrypto's ARMv8 build: 3.4-5.0x holds only from 256 B up. The main claim against ring (BoringSSL-derived) is accurate.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** Fair table (M4): 28.1 vs ring 41.6 ns at 16 B; 1.77 vs 2.08 µs at 16 KiB.
- **Pages the verifier opened:**
  - <https://github.com/godaddy/hardware-rust-crypto>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/godaddy/hardware-rust-crypto/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/godaddy/hardware-rust-crypto/main/README.md>
  - <https://raw.githubusercontent.com/godaddy/hardware-rust-crypto/main/Cargo.toml>
  - <https://raw.githubusercontent.com/godaddy/hardware-rust-crypto/main/NOTICE>
  - <https://raw.githubusercontent.com/godaddy/hardware-rust-crypto/main/LICENSE>
  - <https://crates.io/api/v1/crates/hardware-rust-crypto>
- **Sources the enricher read:**
  - <https://github.com/godaddy/hardware-rust-crypto>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/README.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/benchmarks.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/design.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/assurance.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/security-audit.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/docs/constant-time.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/Cargo.toml>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/NOTICE>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/CHANGELOG.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/SECURITY.md>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/src/lib.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/src/aes_gcm/mod.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/src/aes_gcm/aes.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/src/aes_gcm/ghash.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/src/aes_gcm/nonce.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/blob/main/benches/aes_gcm.rs>
  - <https://github.com/godaddy/hardware-rust-crypto/tree/main/.github/workflows>
  - <https://api.github.com/repos/godaddy/hardware-rust-crypto>
  - <https://api.github.com/repos/godaddy/hardware-rust-crypto/issues?state=all>
  - <https://api.github.com/repos/godaddy/hardware-rust-crypto/commits>
  - <https://crates.io/api/v1/crates/hardware-rust-crypto>
  - <https://crates.io/api/v1/crates/hardware-rust-crypto/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=hardware-rust-crypto&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/godaddy/hardware-rust-crypto`) · [data/wave7/enrich/raw/github_com_godaddy_hardware_rust_crypto.json](../../../data/wave7/enrich/raw/github_com_godaddy_hardware_rust_crypto.json) (enrichment confidence 0.7)

</details>
