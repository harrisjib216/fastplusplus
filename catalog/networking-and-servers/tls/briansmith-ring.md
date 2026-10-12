# ring

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 AND ISC (ring's own code ISC; BoringSSL-derived code Apache-2.0 per LICENSE-BoringSSL; once_cell polyfill Apache-2.0/MIT)` · 🟢 active

> Rust crypto-primitives crate (BoringSSL-derived C/asm) behind rustls; beat OpenSSL 1.5-3.7x on whole-process TLS handshake runs.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | Whole-process handshake run time (hyperfine mean, lower is better), read from the page's SVG bar charts (derived from page data, about +/-0.01 ms): ring 1.29-6.50 ms vs OpenSSL 4.41-10.20 ms. ring is faster than OpenSSL in all 45 combinations, by 1.47x-3.67x (median about 2.15x), e.g. Ed25519 + X25519 + AES-128-GCM 1.29 vs 4.74 ms (3.67x), ECDSA-P384 + secp384r1 + AES-128-GCM 4.77 vs 7.03 ms (1.47x). ring is the fastest of the 4 libraries in 16 of 45 combinations (none with secp384r1, where it trails aws-lc-rs by up to about 2.2x). Page text: 'OpenSSL is the slower library'; room for optimization in secp384r1 'for both OpenSSL and ring'. |
| **Workload** | Whole-process wall time of one wtx-bench binary run (hyperfine -N, 10 warmup + 10 measured runs, mean): decode 3 PEM files, start a TCP server thread and a client thread, complete one TLS handshake, exit without application data. 36 builds (4 crypto backends aws-lc-rs/Graviola/ring/OpenSSL x 3 key agreements secp256r1/secp384r1/X25519 x 3 cipher suites) each run with 5 certificate types (ECDSA P-256, ECDSA P-384, Ed25519, RSA-PSS-SHA256, RSA-PSS-SHA384), inside the WTX project's pluggable crypto layer. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5900X 12-Core, Linux Fedora 7.0.11-200.fc44.x86_64, 32GB DDR4 |
| **Compiler and flags** | wtx-bench Cargo.toml (in the page's wtx-bench.tar.xz): cargo build --profile deploy, which inherits release with opt-level=3, lto=true, codegen-units=1, panic='abort', debug-assertions and overflow-checks off. Exact rustc version not stated (Cargo.toml only sets rust-version = 1.96; wtx is built with its 'nightly' feature). OpenSSL version and build flags not stated; the author says OpenSSL's result may come from 'a missing compile flag'. |
| **Adoption** | 4.1k stars; used transitively via rustls/quinn/tokio ecosystem |
| **Last commit** | 2026-07-22 |
| **Links** | [repository](https://github.com/briansmith/ring) · [benchmark](https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/) |

## Verdict

One blog benchmark by the WTX author timed whole processes with hyperfine (10 runs, mean): decode 3 PEM files, do one loopback TLS handshake in WTX, exit. It used a Rust 'deploy' profile (opt-level 3, fat LTO, codegen-units 1) with rustc and OpenSSL versions unstated, on a Ryzen 9 5900X under Fedora (kernel 7.0.11). Re-reading the SVG bars gives ring 1.29-6.49 ms vs OpenSSL 4.40-10.17 ms, 1.47-3.67x faster (median about 2.15x) in all 45 certificate/key-agreement/cipher combinations, but the gap is a near-constant 2.2-4.4 ms that the author could not explain, and ring was fastest of the four backends in only 16 of 45.

## Use it when

- Rust TLS clients/servers on rustls (or wtx) whose handshakes use X25519 or P-256 key agreement with Ed25519, ECDSA-P256 or RSA-PSS certificates: in the benchmark ring was fastest or within about 0.1 ms of the fastest backend on these rows (e.g. Ed25519 + X25519: 1.29-1.32 ms vs OpenSSL 4.40-4.73 ms).
- RSA-PSS certificate handshakes: ring beat aws-lc-rs in every RSA-PSS row with X25519 or secp256r1 (about 0.71-0.79x of aws-lc-rs time, e.g. 1.76 vs 2.47 ms).
- Rust binaries that must build with only cargo and a C compiler (no CMake, Go, Perl or NASM when using the crates.io package) on x86, x86-64, 32-bit ARM or aarch64, including cross-compiles and no_std (+alloc) targets.
- Short-lived processes that open one TLS connection (CLIs, test harnesses), where the benchmark's whole-process time fell from about 4.4-10.2 ms with OpenSSL to 1.3-6.5 ms with ring.
- Code that needs only primitives (AEAD for QUIC/Noise, HKDF, signature verification for webpki-style X.509) and benefits from a small, misuse-resistant API.

## Skip it when

- Anything P-384-heavy: with ECDSA-P384 certificates, or secp384r1 key agreement plus an ECDSA-P256/Ed25519 certificate, ring was 1.4-2.2x slower than aws-lc-rs (e.g. ECDSA-P384 + X25519 3.40 vs 1.79 ms); P-384 runs on portable C with generic bn_mul_mont_small Montgomery code, and the packaged sources have no P-384-specific assembly.
- You need post-quantum key exchange (ML-KEM hybrids), P-521, finite-field DH, static-key ECDH, AES-CTR/CBC or streaming (pre-hashed) signing: none is offered; the rustls README says the ring provider 'does not support post-quantum algorithms', and P-521 and static-ECDH issues have been open since 2016-2023. No FIPS 140 validation is documented.
- You need a steady release train: the last crates.io release is 0.17.14 (2025-03-11); main holds about 18 months of unreleased work and a 'Request for new release' issue has been open since 2026-05-12. The README now calls the project 'an experiment' and quotes BoringSSL's advice that third parties not depend on it.
- x86-64 macOS or other lightly tested targets: issue #2751 (closed completed) deprecates x86-64 macOS because CI can no longer test ADX/AVX2/AVX-512 paths there; the README warns against toolchains or targets that BoringSSL does not support, and SIDE-CHANNELS.md says constant-time mitigations likely fail on WebAssembly/JIT targets and that ring uses no blinding.
- Non-Rust callers wanting an OpenSSL replacement: there is no C API, no X.509/PEM handling and no TLS protocol code.

## How it is fast

Most hot paths are BoringSSL/OpenSSL-lineage perlasm assembly chosen at runtime by CPU feature detection: AES-NI+PCLMULQDQ+MOVBE stitched AES-GCM, an AVX2 VAES/VPCLMULQDQ AES-GCM path (added in 0.17.13, fixed in 0.17.14), vector-permutation (vpaes) and bitsliced AES fallbacks, SIMD ChaCha20-Poly1305, Montgomery-multiplication asm for RSA, and the Gueron-Krasnov (Intel) P-256 assembly. X25519 uses fiat-crypto field arithmetic (third_party/fiat), with an ADX assembly path on x86-64 (not Windows) and NEON on 32-bit ARM Linux/Android. In the cited benchmark, most of ring's lead over OpenSSL is a near-constant 2.2-4.4 ms extra per OpenSSL process that the benchmark author could not explain, so the result reflects integration and startup cost as much as primitive speed.

## Compared with alternatives

Pick ring over aws-lc-rs when your handshakes use X25519/P-256 with Ed25519, ECDSA-P256 or RSA-PSS certificates and you want the simpler cargo-plus-C-compiler build; pick aws-lc-rs for P-384 or post-quantum key exchange (the rustls team recommends aws-lc-rs for features and performance). Graviola was fastest in as many combinations (16 of 45) as ring; ring is not an alternative to rustls but one of its crypto backends.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, getrandom, untrusted; libc on ARM Linux/Android and Apple aarch64; windows-link on aarch64 Windows; build-time: cc crate plus a C (not C++) compiler that can assemble .S files. Building from Git additionally needs Perl, and NASM for Windows x86/x86-64. |
| **Minimum toolchain** | Released 0.17.14: Rust 1.66 (crates.io rust_version). Current main: Rust 1.85, edition 2024. Windows needs Visual Studio 2022 Build Tools (plus the clang component for aarch64-pc-windows-msvc). |
| **Platforms** | Assembly fast paths on x86, x86-64, 32-bit ARM and little-endian aarch64 (Linux, Android, Apple, Windows) with runtime CPU feature detection; portable fallbacks elsewhere, including wasm32 (wasm32_unknown_unknown_js feature) and no_std targets. x86-64 macOS deprecated (issue #2751). |
| **Thread safety** | signature::KeyPair requires Send + Sync; verification algorithms are Sync statics; SystemRandom and LessSafeKey are Clone handles. No broader thread-safety statement is documented. |
| **Drop-in for the baseline** | partial — not an OpenSSL API; it replaces OpenSSL only as the crypto backend of a Rust TLS library (rustls-ring provider, wtx), which is how the benchmark swapped it in. |

## Gotchas

- Pin &gt;= 0.17.12: RUSTSEC-2025-0009 / CVE-2025-4432 lets a crafted QUIC packet panic HeaderProtectionKey::new_mask() when overflow checks are enabled (default in debug builds, opt-in for release); AES-GCM could also panic near 64 GB in one call. 0.16.x is marked unmaintained (RUSTSEC-2025-0010), and fixes are hard to backport before 0.17.10 because of the license change.
- Open issue #2868 (2026-07): ChaCha20-Poly1305 produced wrong output for messages of 512 bytes and up in x86-64 builds under Rosetta on an Apple M5. It was not reproduced on M4 Pro or on an M5 Pro with newer macOS and is unresolved; the maintainer asked for M5 help with it to speed up the next release.
- API shape differs from EVP: one-shot signing only (no separate digest step), in-place AEAD with the tag appended or separate, nonces from a NonceSequence unless you use LessSafeKey, and agree_ephemeral consumes the EphemeralPrivateKey.
- Maintenance history: RUSTSEC-2025-0007 flagged ring unmaintained on 2025-02-20 and was withdrawn on 2025-02-22 after the rustls team got access; the advisory now says things are 'more-or-less back to how they were before'.

## Known shortcomings

- The only evidence (c410-f3r WTX blog, numbers derived from SVG bar heights) times whole program runs; OpenSSL's constant 2-5 ms gap looks like startup/integration overhead rather than slower crypto. rustc and OpenSSL versions/flags not stated. ring is fastest of the four libraries in only 16 of 45 combinations and never with secp384r1 key exchange.
- P-384 runs on generic C math (no P-384 assembly), so with ECDSA-P384 certificates or secp384r1 key exchange ring took 1.4-2.2x as long as aws-lc-rs; it beats aws-lc-rs on RSA-PSS rows with X25519/secp256r1 (\~0.71-0.79x the time). Only 10 runs per point. No release for 18 months (0.17.14, 2025-03-11) while main moved to Rust 1.85/edition 2024; release request #2840 open. The README calls it 'an experiment' and quotes BoringSSL's advice not to depend on it. No post-quantum key exchange (rustls recommends aws-lc-rs), P-521, finite-field DH, static-key ECDH, AES-CTR/CBC or FIPS validation. Advisories: RUSTSEC-2025-0009 (CVE-2025-4432, QUIC packet panic with overflow checks, fixed 0.17.12); versions before 0.17 unmaintained (RUSTSEC-2025-0010). Open bug #2868: ChaCha20-Poly1305 wrong output for 512+ byte messages under Rosetta on an Apple M5 (unconfirmed elsewhere; blocks the next release). x86-64 macOS deprecated (#2751); constant-time protections probably fail on WebAssembly/JIT targets; no blinding.

## Caveats and trade-offs

Single blog benchmark by the WTX author. Numbers exist only as SVG bar charts; values here were read from bar geometry (plotters output, about 0.01 ms per pixel). It times whole processes (process start, PEM decoding, loopback TCP, one handshake), not crypto alone. OpenSSL's near-constant 2-4.4 ms penalty against ring in every combination suggests fixed init or integration overhead, and the author says the cause is unknown (compile flag, misconfiguration, openssl-sys, or OpenSSL itself). Only 10 runs per point; rustc and OpenSSL versions unstated. ring is slow with secp384r1 key agreement.

Deliberately minimal, low-level unsafe-adjacent API by design (no general-purpose TLS API of its own); non-standard composite license complicates SPDX classification/compliance tooling.

## Maintenance

Main is active (last commit 2026-07-22) but the newest crates.io release, 0.17.14, dates from 2025-03-11; licensed Apache-2.0 AND ISC and very widely depended on (about 759M crates.io downloads), so it is safe to depend on from crates.io despite the README's 'experiment' wording.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Independent blog benchmark with public code (wtx-bench.tar.xz: assets/bench.sh, Cargo.toml deploy profile) and a stated CPU (Ryzen 9 5900X), but no rustc version and no OpenSSL version or build flags, so not A. It is not a peer-reviewed paper or well-known suite, so not B; it measures whole-process time rather than isolated handshake cost.
- **Verifier notes:** SVG values extracted successfully: ring beats OpenSSL in all 45 combos (1.47x-3.67x) in this whole-process benchmark, but the fixed OpenSSL offset makes this weak evidence of crypto speed. License is now Apache-2.0 AND ISC with no non-OSI parts in LICENSE, LICENSE-BoringSSL or LICENSE-other-bits, so usability changed from mixed to copyable. The record's 'faster than the others in most cases' was loose: ring wins 16/45.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes128gcmsha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes256gcmsha384.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/chacha20poly1305sha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/wtx-bench.tar.xz>
  - <https://github.com/c410-f3r/wtx>
  - <https://github.com/briansmith/ring>
  - <https://raw.githubusercontent.com/briansmith/ring/main/LICENSE>
  - <https://raw.githubusercontent.com/briansmith/ring/main/LICENSE-BoringSSL>
  - <https://raw.githubusercontent.com/briansmith/ring/main/LICENSE-other-bits>
  - <https://raw.githubusercontent.com/briansmith/ring/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/briansmith/ring>
  - <https://raw.githubusercontent.com/briansmith/ring/main/README.md>
  - <https://raw.githubusercontent.com/briansmith/ring/main/Cargo.toml>
  - <https://raw.githubusercontent.com/briansmith/ring/main/BUILDING.md>
  - <https://raw.githubusercontent.com/briansmith/ring/main/SECURITY.md>
  - <https://raw.githubusercontent.com/briansmith/ring/main/SIDE-CHANNELS.md>
  - <https://raw.githubusercontent.com/briansmith/ring/main/RELEASES.md>
  - <https://raw.githubusercontent.com/briansmith/ring/main/LICENSE>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/lib.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/signature.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/agreement.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/rand.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/aead/mod.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/aead/less_safe_key.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/ec/suite_b/ops/p256.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/ec/suite_b/ops/p384.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/src/ec/curve25519/x25519.rs>
  - <https://raw.githubusercontent.com/briansmith/ring/main/crypto/fipsmodule/ec/gfp_p384.c>
  - <https://raw.githubusercontent.com/briansmith/ring/main/crypto/curve25519/curve25519_64_adx.c>
  - <https://github.com/briansmith/ring/tree/main/src/aead>
  - <https://github.com/briansmith/ring/issues/2868>
  - <https://github.com/briansmith/ring/issues/2840>
  - <https://github.com/briansmith/ring/issues/2751>
  - <https://github.com/briansmith/ring/issues?q=P-384+performance>
  - <https://crates.io/api/v1/crates/ring>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/ring>
  - <https://raw.githubusercontent.com/rustls/rustls/main/README.md>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes128gcmsha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes256gcmsha384.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/chacha20poly1305sha256.svg>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/briansmith/ring`) · [data/wave5/enrich/raw/github_com_briansmith_ring.json](../../../data/wave5/enrich/raw/github_com_briansmith_ring.json) (enrichment confidence 0.4)

</details>
