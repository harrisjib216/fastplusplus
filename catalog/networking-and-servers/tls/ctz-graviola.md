# Graviola

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR ISC OR MIT-0` · 🟢 active

> Rust crypto on formally verified s2n-bignum assembly, a rustls backend; one-handshake processes ran 1.6-3.8x faster than OpenSSL-backed.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | Page text: "OpenSSL is the slower library" and "Graviola is a promising new cryptography library". Numbers exist only as bar charts (hyperfine mean wall time per process, seconds, 0-0.010 s axis), not box plots. From the SVG bar heights (derived from page data): Graviola about 1.26-5.90 ms vs OpenSSL about 4.41-10.20 ms per full handshake process, about 1.6-3.8x; OpenSSL is slowest in all 45 combinations; Graviola is fastest in only 16 of 45 (ring or aws-lc-rs tie or win the rest). |
| **Workload** | One process per run: decode 3 PEM files, then a full TLS 1.3 handshake over loopback TCP (server in main thread, client in another thread), then exit with no application data. wtx TLS stack with a swappable crypto backend (aws-lc-rs, Graviola, ring, OpenSSL via openssl-sys). 5 certificate signature algorithms x 3 key agreements (secp256r1, secp384r1, x25519) x 3 cipher suites. Timed with hyperfine -N, 10 runs after 10 warmups; mean plotted. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5900X 12-Core, 32GB DDR4, Corsair Force MP510 SSD, Linux Fedora kernel 7.0.11-200.fc44.x86_64 |
| **Compiler and flags** | rustc version not stated (bench Cargo.toml: edition 2024, rust-version = 1.96, wtx 0.49 with 'nightly' feature); cargo profile 'deploy': opt-level=3, lto=true, codegen-units=1, panic=abort, debug-assertions and overflow-checks off (from wtx-bench.tar.xz). OpenSSL version and build flags not stated. |
| **Adoption** | 305 stars |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/ctz/graviola) · [benchmark](https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/) |

## Verdict

A third-party blog by the wtx author used hyperfine (10 runs after 10 warmups) on a Ryzen 9 5900X running Fedora (kernel 7.0.11) to time whole processes, each decoding PEM files, doing one TLS 1.3 handshake over loopback in wtx 0.49, and exiting; Graviola took about 1.26-5.90 ms and the OpenSSL backend 4.41-10.20 ms (the `openssl` 0.10 crate against unvendored system OpenSSL, version and rustc version not stated), so OpenSSL was 1.6-3.8x slower across 45 cipher, group and certificate combinations. OpenSSL was slowest in every combination, but Graviola was fastest in only 16 of 45, and the author cannot explain the near-constant 3.1-4.7 ms gap.

## Use it when

- Rust services on rustls 0.23 whose handshakes use ECDSA-P256, X25519 or X25519MLKEM768. Graviola's own benchmark ranks it first in ECDSA-P256 signing (92,694 vs aws-lc-rs 85,967 sigs/s on a Ryzen 9 7940HS), X25519 (42,363 vs 42,038 kx/s) and ML-KEM-768 (33,520 vs 31,044 per s).
- Builds that must avoid a C compiler, CMake or assembler, such as cross-compiling or hermetic cargo-only CI. The README says the crate builds in under one second with only rustc.
- Short-lived processes such as CLIs, test harnesses and serverless cold starts that do one TLS 1.3 handshake. In the c410-f3r test on a Ryzen 9 5900X, a whole run took about 1.3-5.9 ms with Graviola and 4.4-10.2 ms with the OpenSSL backend.
- Arm hosts with AES, SHA2 and PMULL (Apple M-series, Raspberry Pi 5). Graviola leads on aarch64 in ECDSA-P256 signing (84,286 vs aws-lc-rs 64,224 sigs/s on an M2) and in ML-KEM-768.
- Cases where formally verified bignum and ECC code, constant-time table selection, Arm DIT and SIMD-register zeroing after secret operations matter more than FIPS certification.

## Skip it when

- Servers that sign handshakes with RSA keys. On x86_64, RSA-2048 signing runs at 2,280.7 sigs/s against 5,276.3 for aws-lc-rs. Issue #209 traces this to bignum_emontredc_8n.
- P-384 certificates or key exchange. Graviola reaches roughly 56-68% of aws-lc-rs throughput here (ECDSA-P384 signing 9,175.8 vs 16,385 sigs/s; P384 kx 4,861.2 vs 7,197 kx/s). In the handshake blog, aws-lc-rs also beat it with P-384 certificates.
- Bulk AES-256-GCM throughput. Graviola ranks third on x86_64 (8.79 vs 9.88 GiB/s for aws-lc-rs) and fourth on the M2 (5.25 GiB/s).
- CPUs without ADX, AVX2 or BMI2, including Haswell, VMs that hide ADX (issue #222: an OVH VPS reported as 'Haswell, no TSX') and Raspberry Pi 4. Also RISC-V, 32-bit, wasm and no_std targets. None of these have a software fallback (issues #95, #57).
- Projects that need the OpenSSL API or C ABI, FIPS, an audited and mature library (the README says 'very new, so exercise due caution'), QUIC through quinn (still unmerged, issue #98), SHA-1, ML-DSA or RSA encryption (a stated non-goal).

## How it is fast

The field and group arithmetic for P-256, P-384, X25519/Ed25519, the RSA bignums, the ML-KEM NTT and Keccak-f is AWS s2n-bignum's hand-written, formally verified assembly, which a script converts into Rust inline `asm!` so only rustc is needed. It uses Booth-encoded fixed windows for point multiplication (7-bit with a 148 KB precomputed table for the P-256 base point, 5-bit elsewhere) and a 4-bit fixed window with CRT for RSA. Other parts are tuned for specific CPU features: stitched by-8 AES-CTR plus by-8 GHASH, an optional AVX-512/VAES by-16 path chosen at runtime, SHA-NI and Arm SHA intrinsics, and 4-way AVX2 Keccak for ML-KEM sampling. In the handshake benchmark the lead over OpenSSL is a nearly constant 3.1-4.7 ms, which points to a fixed per-process cost on the OpenSSL side, not to faster handshake math.

## Compared with alternatives

Pick Graviola when you already use rustls in Rust and want a cargo-only build with top ECDSA-P256, X25519 and ML-KEM speed. Pick AWS-LC when you need an OpenSSL-style C API, FIPS, or fast RSA and P-384. Pick ztls or picotls fusion when the bottleneck is record or AEAD throughput, not handshakes.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, getrandom 0.3 (graviola); rustls 0.23.18+ (rustls-graviola). No C toolchain. |
| **Minimum toolchain** | Rust 1.89, edition 2024 (graviola 0.4.1 rust-version); rustls-graviola 0.4.0 declares 1.85 but pulls in graviola 0.4.x |
| **Platforms** | x86_64 with AES, PCLMULQDQ, AVX, AVX2, BMI1/BMI2, ADX (Broadwell / AMD Zen and later; AVX-512 AES-GCM path used when present); aarch64 with NEON, AES, PMULL, SHA2. Needs std. |
| **Thread safety** | not documented (safe Rust API; the crate does not state Send/Sync guarantees) |
| **Drop-in for the baseline** | no |

## Gotchas

- An unsupported CPU does not return an error. Every public entry point runs `verify_cpu_features()`, and that function calls `assert!`, so the process panics on the first crypto call ('graviola requires adx CPU support'). Test on the real deployment hardware or VM type.
- Valgrind does not emulate ADX (KDE bug 494162). Set the `VALGRIND_BUG_494162` environment variable at compile time (read by `option_env!`) to run under Valgrind.
- RSA key generation is not side-channel safe. ECDSA uses hedged RFC 6979 nonces (extra random input), so repeated signatures of the same message differ.
- GitHub shows the license as NOASSERTION. The real license is 'Apache-2.0 OR ISC OR MIT-0' (per Cargo.toml and SPDX headers), which license scanners that expect MIT or Apache may flag.

## Known shortcomings

- Evidence is one personal blog (the wtx author): OpenSSL trails by a near-constant 3.1-4.7 ms in every combination, which fits a fixed per-process cost more than faster crypto (cause unknown to the author); Graviola is fastest in only 16 of 45 combinations. No rustc or OpenSSL version. Crypto primitives only, x86-64/aarch64.
- The gap to OpenSSL is a constant 3.1-4.7 ms in every combination, which looks like fixed process overhead rather than faster handshake math; the OpenSSL side is the openssl 0.10 crate linking Fedora's system OpenSSL (versions not stated), and current wtx dropped its OpenSSL backend, so the harness cannot be re-run. Not an OpenSSL replacement: no C API; it replaces ring/aws-lc-rs as a rustls provider. Every entry point asserts CPU features and panics without them (ADX/AVX2/BMI2 on x86_64, so no Haswell; VMs hiding ADX panic, #222); no Pi 4, RISC-V, 32-bit, wasm or no_std. Loses to aws-lc-rs on RSA-2048 signing (2,281 vs 5,276/s), ECDSA-P384, P-384 key exchange and bulk AES-256-GCM. Pre-1.0; no SHA-1, ML-DSA or RSA encryption; RSA key generation not side-channel safe. Valgrind needs a special build flag. MSRV differs between graviola (1.89) and rustls-graviola (1.85).

## Caveats and trade-offs

Independent third-party blog by the wtx author, not a well-known suite; code is public in wtx-bench.tar.xz but rustc and OpenSSL versions are not stated. It times whole processes (startup, PEM decode, loopback TCP), and the OpenSSL-minus-Graviola gap is a near-constant 3.1-4.7 ms across all 45 combinations, which is consistent with a fixed per-process cost rather than faster handshake crypto; the author says the cause is unknown ("a missing compile flag, an internal misconfiguration, the openssl-sys crate or OpenSSL itself"). Graviola is fastest in only 16 of 45 combinations; ring matches or beats it on several, and aws-lc-rs beats it with ECDSA-P384 certificates. Numbers exist only in SVG bar charts (means of 10 runs). Graviola's own jbp.io/graviola page (Ryzen 9 7940HS, Apple M2, no compiler/flags) compares only against ring, aws-lc-rs, rustcrypto, golang, dalek and libcrux, not OpenSSL. GitHub reports the license as NOASSERTION; LICENSE and Cargo.toml give 'Apache-2.0 OR ISC OR MIT-0' (the LICENSE prose says 'MIT license' but the included text is MIT-0).

Rust only; requires aarch64 with NEON+PMULL or x86_64 with AVX2/ADX/BMI2/PCLMULQDQ (excludes older CPUs like Raspberry Pi 4); very new/unaudited; RSA key generation is not side-channel-safe; built primarily as a rustls CryptoProvider rather than a standalone TLS stack

## Maintenance

The project is active: last commit 2026-08-24, graviola 0.4.1 on crates.io (about 282k downloads), no RustSec advisories. It is pre-1.0 and describes itself as very new, and it is permissively licensed, so it is easy to adopt as a rustls provider but not yet a conservative choice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The c410-f3r blog compares aws-lc-rs, Graviola, ring and OpenSSL as swappable crypto backends of the wtx TLS stack; its code is public (wtx-bench.tar.xz: assets/bench.sh, src/main.rs, Cargo.toml profile 'deploy' opt-level=3/LTO/CGU1) and the CPU is stated (Ryzen 9 5900X), but no rustc or OpenSSL version is given, so it is not A. It is a personal blog by the wtx author (wtx 401 stars), not a well-known independent suite, so it is not B (same rule as quicperf and gonwan/webframework-benchmark).
- **Verifier notes:** Real independent comparison against OpenSSL, but it comes from a small personal harness without compiler versions, and the OpenSSL gap looks like fixed process overhead, so the tier drops from B to C. The license is corrected from 'Apache-2.0 OR MIT OR ISC' to 'Apache-2.0 OR ISC OR MIT-0'. Stars (305), last commit (2026-08-24) and active status check out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes128gcmsha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes256gcmsha384.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/chacha20poly1305sha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/wtx-bench.tar.xz>
  - <https://github.com/ctz/graviola>
  - <https://github.com/ctz/graviola/blob/main/LICENSE>
  - <https://github.com/ctz/graviola/blob/main/graviola/Cargo.toml>
  - <https://github.com/ctz/graviola/blob/main/README.md>
  - <https://jbp.io/graviola/>
  - <https://github.com/c410-f3r/wtx>
- **Sources the enricher read:**
  - <https://github.com/ctz/graviola>
  - <https://github.com/ctz/graviola/blob/main/README.md>
  - <https://github.com/ctz/graviola/blob/main/COMPATIBILITY.md>
  - <https://github.com/ctz/graviola/blob/main/graviola/Cargo.toml>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/lib.rs>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/low/entry.rs>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/low/x86_64/cpu.rs>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/low/aarch64/cpu.rs>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/low/inline_assembly_safety.rs>
  - <https://github.com/ctz/graviola/blob/main/graviola/src/low/x86_64/curve25519_x25519.rs>
  - <https://github.com/ctz/graviola/blob/main/rustls-graviola/README.md>
  - <https://github.com/ctz/graviola/blob/main/rustls-graviola/Cargo.toml>
  - <https://github.com/ctz/graviola/blob/main/rustls-graviola/src/lib.rs>
  - <https://github.com/ctz/graviola/blob/main/rustls-graviola/src/kx.rs>
  - <https://github.com/ctz/graviola/blob/main/rustls-graviola/src/suites.rs>
  - <https://github.com/ctz/graviola/issues>
  - <https://github.com/ctz/graviola/issues/222>
  - <https://github.com/ctz/graviola/issues/209>
  - <https://github.com/ctz/graviola/issues/98>
  - <https://github.com/ctz/graviola/issues/95>
  - <https://github.com/ctz/graviola/issues/57>
  - <https://jbp.io/graviola/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/wtx-bench.tar.xz>
  - <https://github.com/c410-f3r/wtx/blob/wtx-v0.49.0/wtx/Cargo.toml>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/Cargo.toml>
  - <https://crates.io/api/v1/crates/graviola>
  - <https://crates.io/api/v1/crates/rustls-graviola>
  - <https://github.com/rustsec/advisory-db/tree/main/crates>
  - <https://hn.algolia.com/api/v1/search?query=graviola&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ctz/graviola`) · [data/wave5/enrich/raw/github_com_ctz_graviola.json](../../../data/wave5/enrich/raw/github_com_ctz_graviola.json) (enrichment confidence 0.55)

</details>
