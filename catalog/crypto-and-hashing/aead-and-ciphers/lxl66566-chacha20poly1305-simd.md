# chacha20poly1305-simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust (X)ChaCha20-Poly1305 with hand-written AVX-512/AVX2/SSE2/NEON kernels; beats RustCrypto everywhere, OpenSSL mainly on small messages.

| | |
|---|---|
| **Beats** | OpenSSL EVP_chacha20_poly1305 (ChaCha20-Poly1305) |
| **Claimed result** | 2.0-3.1x faster than OpenSSL 4.1.0-dev at tiny sizes (16-256B), 1.3-1.9x at mid sizes (512B-1KiB), 1.0-1.1x at large sizes (&gt;=4KiB); also 1.7-6.2x vs RustCrypto chacha20poly1305 0.11 (same ISA tier) and 0.8-1.4x vs aws-lc-rs depending on size |
| **Workload** | AEAD seal (encrypt_in_place_detached), 16-byte AAD, in-place, across message sizes from 16 B to ≥16 KiB |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X (Zen 4), Linux |
| **Compiler and flags** | rustc 1.100-nightly; cargo bench --bench aead (Criterion; bench profile codegen-units=1; runtime SIMD dispatch, no target-cpu flag). OpenSSL 4.1.0-dev static build with runtime auto-dispatch (AVX-512 ChaCha and AVX-512 IFMA Poly1305 on this CPU). The OpenSSL driver perf/openssl_bench.c is built with cc -O2. aws-lc-rs 1.18 is benchmarked in the same Criterion harness. |
| **Adoption** | 0 stars (GitHub repo created 2026-08-26; crate first published 2026-08-27); 108 crates.io downloads (v0.3.1) |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/lxl66566/chacha20poly1305-simd) · [benchmark](https://github.com/lxl66566/chacha20poly1305-simd#performance) |

## Verdict

On an AMD Ryzen 9 7950X (Zen 4, Linux), the author measured in-place seal with 16 B AAD using Criterion (rustc 1.100-nightly, codegen-units=1, runtime dispatch; this crate picked its AVX-512 IFMA path). This crate took 126 ns at 16 B vs 396 ns for OpenSSL 4.1.0-dev EVP_chacha20_poly1305 (3.1x) and 408 vs 532 ns at 1 KiB (1.3x), and tied OpenSSL from 16 KiB to 1 MiB (about 188 us per MiB each, about 5.6 GB/s). The small-size gap is inflated: the C driver (cc -O2) re-runs EVP_EncryptInit_ex with cipher, key and nonce every iteration, and aws-lc-rs in the same Rust harness beats this crate below 1 KiB (119 vs 126 ns at 16 B).

## Use it when

- Pure-Rust ChaCha20-Poly1305 or XChaCha20-Poly1305 on x86-64 where you currently use RustCrypto chacha20poly1305: the author's Zen 4 numbers are about 2.8x faster at 16 B and about 6.2x at 1 MiB against RustCrypto's AVX-512 build.
- Bulk sealing or opening of 4 KiB and larger buffers on x86-64 when you would otherwise use aws-lc-rs: about 1.2x faster at 4 KiB and about 1.4x at 64 KiB to 1 MiB, and 1.47x on 1 MiB open.
- no_std or embedded-adjacent Rust builds that need an AEAD with no C toolchain (unlike aws-lc-rs or OpenSSL bindings), with a scalar fallback and compile-time backend pinning.
- XChaCha20-Poly1305 (24-byte random nonces) at SIMD speed; the aws-lc-rs benchmark notes that aws-lc-rs has no XChaCha.

## Skip it when

- Anywhere an audited implementation is required. The README says it was developed with AI assistance and has had no security audit, and the repo is about one month old, with four crate releases (0.1 to 0.3.1) in three days.
- Small-message workloads (16 B to 1 KiB) where aws-lc-rs is an option: aws-lc-rs is faster at 16 to 256 B (about 0.8-0.94x for this crate) and roughly even at 512 B to 1 KiB.
- Large-buffer workloads where you already link OpenSSL 3.x/4.x on an AVX-512 IFMA CPU: from 16 KiB up it only ties OpenSSL (1.03x down to 1.00x).
- aarch64 production deployments: no NEON performance numbers are published, NEON correctness was checked only under QEMU user mode (500k differential cases), and CI runs only on ubuntu-latest x86-64 with nightly, and only on pull requests.
- Callers who need AES-GCM or other AEADs; the crate supports only the ChaCha20-Poly1305 family.

## How it is fast

The seal/open loop fuses ChaCha20 keystream generation, the message XOR and Poly1305 absorption, so the latency-bound MAC multiplies overlap with the throughput-bound cipher in the out-of-order window. ChaCha20 runs as 8-block batches: AVX2, or on AVX-512VL in YMM registers with single-instruction vprold rotations (chosen because Zen 4 double-pumps 512-bit ops). Poly1305 uses the Goll-Gueron 4-block batched algorithm on AVX2, a port of OpenSSL's radix-2^44 vpmadd52 8-lane path on AVX-512 IFMA CPUs, and 26-bit-limb lane-parallel code on NEON. Messages of 3 blocks or fewer take a small-message fast path, and backend dispatch is one cached relaxed AtomicU8 load per call.

## Compared with alternatives

Pick it over libaegis, HiAE or Rocca when the wire format must stay standard RFC 8439 ChaCha20-Poly1305 or XChaCha, in pure Rust; those siblings are faster but use different, newer AEAD constructions. Pick hardware-rust-crypto instead when you need AES-256-GCM, or want formal-verification evidence instead of an unaudited AI-assisted codebase.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional aead 0.6, bytes 1, getrandom 0.4, zeroize 1.8, hotpath 0.24 |
| **Minimum toolchain** | Rust 1.89 (edition 2024, rust-version in Cargo.toml); the author's benchmarks and CI use nightly |
| **Platforms** | x86-64 (SSE2 baseline; AVX2, AVX-512F+VL and AVX-512 IFMA picked at runtime), aarch64 (NEON), portable scalar fallback elsewhere |
| **Thread safety** | Not documented explicitly. Per the source, the cipher only holds the 32-byte key (it is Copy unless zeroize is on), all methods take &self, and the backend cache is a global AtomicU8, so one instance can be shared across threads. |
| **Drop-in for the baseline** | partial: it is not a drop-in for OpenSSL EVP (different language and API). Against RustCrypto chacha20poly1305 it is drop-in only through the optional `aead` feature's wrapper types (aead 0.6 traits), and the native API differs (new takes the key by value; detached methods return Result&lt;Tag&gt;). |

## Gotchas

- Decryption is fused with authentication, as in BoringSSL: on a tag mismatch the in-place buffer holds unspecified (partly decrypted) bytes, so discard it on Err.
- The IFMA Poly1305 file (src/poly1305/ifma.rs) is a port of OpenSSL's poly1305-x86_64.pl under Apache-2.0, so the crate-level 'MIT OR Apache-2.0' choice is effectively Apache-2.0 for that file.
- The AVX-512 backend is on by default. Build with default-features = false (then re-enable std/alloc) to keep AVX-512 instructions out of the binary. Forcing a backend via RUSTFLAGS --cfg chacha20poly1305_backend removes the other kernels and assumes the CPU supports the chosen one.
- The README usage snippet is out of date for 0.3.1 (it calls new(&key) and treats the result as a bare Tag); the lib.rs doctests show the current API. Tag comparison is a plain XOR-OR loop, not the `subtle` crate.

## Known shortcomings

- The OpenSSL driver re-keys on every iteration, inflating the small-message 2-3x wins; at 64 KiB and above it ties OpenSSL, and at tiny sizes it is 0.8-0.9x of aws-lc-rs. AI-assisted code with no audit. Rust-only.
- aws-lc-rs is faster below 1 KiB (119 vs 126 ns at 16 B). About a month old, 0 stars, AI-built and unaudited; tag comparison is a plain loop (no `subtle` constant-time crate); failed open leaves the buffer unspecified. No aarch64 numbers (NEON tested only under QEMU). The IFMA file is ported from OpenSSL, so that part is Apache-2.0 only.

## Caveats and trade-offs

A very new project (Aug 2026) with no independent verification. The README says it was developed with AI assistance and has not had a security audit. The OpenSSL comparison uses an OpenSSL 4.1.0-dev pre-release, and the setups are asymmetric: the C driver calls EVP_EncryptInit_ex with the cipher and key on every iteration, while the Rust cipher is keyed once outside the loop. That likely inflates the 2-3x gap at 16-256 B. At &gt;=64 KiB it merely ties OpenSSL. Against aws-lc-rs it is slower at tiny sizes (0.8-0.9x) and about even at 512 B-1 KiB. It wins only at &gt;=4 KiB (1.2-1.4x).

Disclaimer in README: developed with AI assistance and has not undergone a security audit; pure Rust with hand-written AVX-512/AVX2/SSE2/NEON backends and runtime CPU dispatch

## Maintenance

Active but brand new: the repo was created on 2026-08-26, last commit 2026-08-29, 0 stars, 0 issues and 108 crates.io downloads. It is dual MIT/Apache-2.0 (the IFMA file is Apache-2.0 only), and usable as a crate today, but unaudited and pre-1.0 with a fast-moving API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance table matches perf/bench_results.json and perf/openssl.csv; for example, at 16 B it is 126.3 vs 396.4 ns (3.1x), and at 1 MiB it ties at 1.0x. The benchmark code is public (benches/aead.rs, and perf/openssl_bench.c built with cc -O2). The page states rustc 1.100-nightly, cargo bench with codegen-units=1, and an AMD Ryzen 9 7950X.
- **Verifier notes:** The claimed ratios match the README table and the raw bench data. The license really is MIT OR Apache-2.0 (Cargo.toml, README and both LICENSE files), even though GitHub's detector reports only Apache-2.0.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lxl66566/chacha20poly1305-simd>
  - <https://github.com/lxl66566/chacha20poly1305-simd#performance>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/README.md>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/Cargo.toml>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/perf/openssl_bench.c>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/perf/openssl.csv>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/perf/bench_results.json>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/benches/aead.rs>
  - <https://raw.githubusercontent.com/lxl66566/chacha20poly1305-simd/main/LICENSE-MIT>
  - <https://crates.io/api/v1/crates/chacha20poly1305-simd>
- **Sources the enricher read:**
  - <https://github.com/lxl66566/chacha20poly1305-simd>
  - <https://github.com/lxl66566/chacha20poly1305-simd#performance>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/README.md>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/Cargo.toml>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/build.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/perf/openssl_bench.c>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/perf/openssl.csv>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/perf/bench_results.json>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/benches/aead.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/lib.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/aead.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/aead_compat.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/backend.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/backend/avx512.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/chacha/mod.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/chacha/avx512.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/poly1305/mod.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/poly1305/ifma.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/src/poly1305/avx2.rs>
  - <https://github.com/lxl66566/chacha20poly1305-simd/blob/main/.github/workflows/test.yml>
  - <https://api.github.com/repos/lxl66566/chacha20poly1305-simd>
  - <https://api.github.com/repos/lxl66566/chacha20poly1305-simd/issues?state=all>
  - <https://api.github.com/repos/lxl66566/chacha20poly1305-simd/commits>
  - <https://crates.io/api/v1/crates/chacha20poly1305-simd>
  - <https://hn.algolia.com/api/v1/search?query=chacha20poly1305-simd&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/lxl66566/chacha20poly1305-simd`) · [data/wave7/enrich/raw/github_com_lxl66566_chacha20poly1305_simd.json](../../../data/wave7/enrich/raw/github_com_lxl66566_chacha20poly1305_simd.json) (enrichment confidence 0.7)

</details>
