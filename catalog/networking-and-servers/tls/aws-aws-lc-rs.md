# aws-lc-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `ISC AND (Apache-2.0 OR ISC)` · 🟢 active

> Rust crypto crate with a ring-style API over AWS-LC and optional FIPS module; beat OpenSSL in wtx handshake runs.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | Whole-process handshake run time (hyperfine mean, lower is better), read from the page's SVG bar charts (derived from page data, about +/-0.01 ms): aws-lc-rs 1.38-6.71 ms vs OpenSSL 4.41-10.20 ms. aws-lc-rs is faster than OpenSSL in all 45 combinations, by 1.30x-3.44x (median about 2.95x), e.g. Ed25519 + X25519 + AES-128-GCM 1.38 vs 4.74 ms (3.44x), RSA-PSS-SHA384 + X25519 + AES-256-GCM 6.66 vs 8.68 ms (1.30x). With RSA-PSS-SHA384 certificates aws-lc-rs (6.4-6.7 ms) trails ring (4.9-6.5 ms) and Graviola (5.2-5.9 ms), matching the page text; with secp384r1 key agreement it is fastest or near-fastest. |
| **Workload** | Whole-process wall time of one wtx-bench binary run (hyperfine -N, 10 warmup + 10 measured runs, mean): decode 3 PEM files, start a TCP server thread and a client thread, complete one TLS handshake, exit without application data. 36 builds (4 crypto backends aws-lc-rs/Graviola/ring/OpenSSL x 3 key agreements secp256r1/secp384r1/X25519 x 3 cipher suites) each run with 5 certificate types (ECDSA P-256, ECDSA P-384, Ed25519, RSA-PSS-SHA256, RSA-PSS-SHA384), inside the WTX project's pluggable crypto layer. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5900X 12-Core, Linux Fedora 7.0.11-200.fc44.x86_64, 32GB DDR4 |
| **Compiler and flags** | wtx-bench Cargo.toml (in the page's wtx-bench.tar.xz): cargo build --profile deploy, which inherits release with opt-level=3, lto=true, codegen-units=1, panic='abort', debug-assertions and overflow-checks off. Exact rustc version not stated (Cargo.toml only sets rust-version = 1.96; wtx is built with its 'nightly' feature). OpenSSL version and build flags not stated; the author says OpenSSL's result may come from 'a missing compile flag'. bench.sh sets AWS_LC_SYS_USE_SYSTEM=0 (vendored AWS-LC build). |
| **Adoption** | 655 stars (Rust-bindings crate); underlying aws-lc C library used in production AWS TLS stacks |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/aws/aws-lc-rs) · [benchmark](https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/) |

## Verdict

c410-f3r's wtx-bench timed whole processes: decode 3 PEM files, run one loopback TLS handshake in WTX, and exit (hyperfine mean of 10 runs). Builds used the Rust deploy profile (opt-level 3, fat LTO, 1 codegen unit; rustc and OpenSSL versions unstated) on a Ryzen 9 5900X under Fedora. aws-lc-rs (vendored AWS-LC) took 1.38-6.71 ms against 4.41-10.20 ms for OpenSSL, 1.30-3.44x faster (median about 2.95x) in all 45 combinations. OpenSSL's near-constant penalty is unexplained by the author, so this is weak evidence about crypto speed.

## Use it when

- A Rust service that must use a FIPS-validated module: the `fips` feature links AWS-LC-FIPS 4.x (lab-tested and submitted to NIST) with the same API, and try_fips_mode() checks it at runtime.
- rustls deployments that want post-quantum key exchange or the most complete provider: rustls recommends rustls-aws-lc-rs, and its ring provider has no post-quantum algorithms.
- Porting ring 0.16/0.17 code that also needs AES-CBC/CTR, CMAC, AES key wrap or ML-KEM, which ring does not offer.
- Handshake-heavy servers that use P-384 key agreement: in wtx it was fastest or near-fastest with secp384r1.
- Mainstream targets (x86_64/aarch64 Linux, macOS, Windows) where a C compiler is available at build time.

## Skip it when

- no_std or embedded targets: the crate requires std.
- Latency-critical handshakes with RSA-PSS certificates: in wtx aws-lc-rs took 6.4-6.7 ms, against 4.9-6.5 ms for ring and 5.2-5.9 ms for Graviola.
- Size- or build-time-constrained builds: issue #745 (open) reports +4 MB (AWS SDK) up to +17 MB (MSVC static) and about 1.8 MiB more than ring on x86_64 Linux; a user reports builds several times slower than ring (#851). opt-level s/z (v1.18.0+) cuts the AWS-LC footprint 60-70% on x86_64, but P-256 becomes about 2-3x slower and P-384 about 3-6x slower.
- Short-lived processes and cold starts: the guide gives a one-time jitter-entropy cost of about 50 ms per process, and #899 reports a \~1 s Lambda cold-start regression. AWS_LC_SYS_NO_JITTER_ENTROPY=1 removes it (non-FIPS only).
- Old or unusual cross toolchains: #1022 (open) fails on aarch64 manylinux GCC 4.8.5 (no __ARM_ARCH), FIPS builds with GCC 14+ are still reported broken (#569), and Windows x86 needs NASM (x86-64 can opt into prebuilt NASM objects).

## How it is fast

The wrapper adds no crypto of its own. The speed is AWS-LC's: BoringSSL-derived assembly (AVX-512 AES-GCM routines on x86_64), vendored s2n-bignum assembly for X25519, Ed25519 and P-384 scalar multiplication, and large precomputed elliptic-curve tables. Rust calls go over thin FFI into a statically linked, symbol-prefixed library, initialized once through std::sync::Once. In the wtx benchmark OpenSSL carries an almost constant 2-5 ms extra per run, which points to OpenSSL setup or integration overhead rather than faster primitives. Against ring the times are close (1.38 vs 1.29 ms at the fastest point), except with RSA-PSS certificates, where ring and Graviola win.

## Compared with alternatives

Choose it over ring or Graviola when you need FIPS, post-quantum KEM, extra primitives such as AES-CBC/CTR, CMAC or key wrap, or P-384-heavy handshakes. ring builds smaller and compiles faster, and ring and Graviola were faster with RSA-PSS certificates in wtx. Relative to the AWS-LC (C) and rustls entries, it is the Rust binding to AWS-LC and the crypto provider under rustls, not a competitor to them.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | aws-lc-sys (bundled AWS-LC source built by a cc-crate build script; needs a C/C++ compiler, and NASM on Windows x86 unless prebuilt objects are allowed), zeroize, untrusted 0.7 (default ring-io/ring-sig-verify features). The `fips` feature swaps in aws-lc-fips-sys and always needs CMake and Go, plus bindgen/libclang except on 6 targets with pre-generated FIPS bindings. |
| **Minimum toolchain** | Rust 1.71 (rust-version) and a C11 compiler by default; a few tier-3 targets (mips, aarch64-apple-tvos-sim) need nightly. |
| **Platforms** | Built and tested on Linux (x86_64, aarch64, arm/armv7, i686, ppc/ppc64/ppc64le, riscv64gc, s390x, mips), macOS and iOS, Windows MSVC and GNU (x86, x86_64, aarch64), Android, FreeBSD, NetBSD, illumos and wasm32-emscripten. FIPS is a subset: Linux x86_64/aarch64/arm-musl/ppc, macOS x86_64/aarch64, Windows MSVC x86_64/aarch64, FreeBSD x86_64. |
| **Thread safety** | Key types are Send + Sync (for example aead::LessSafeKey on docs.rs), and library init is guarded by std::sync::Once. There is no wider documented contract; the FIPS service indicator is thread-local. |
| **Drop-in for the baseline** | partial — it does not replace OpenSSL's API or libssl. It replaces ring 0.16 with documented differences (std required, extra check on Ed25519 PKCS#8 v2 keys), and as a rustls CryptoProvider it replaces OpenSSL only if you move the TLS layer to rustls. |

## Gotchas

- The build silently links a system AWS-LC if OPENSSL_DIR, OPENSSL_INCLUDE_DIR/OPENSSL_LIB_DIR or pkg-config points at a new-enough AWS-LC install. Dynamic linking embeds no rpath. Set AWS_LC_SYS_USE_SYSTEM=0 to force the vendored build, as the wtx benchmark did. With `fips`, detection may execute the candidate library.
- FIPS is a compile-time Cargo feature. It unifies across the whole dependency graph, `fips` plus `non-fips` is a compile error, and the FIPS module version follows the crate version (module 3.0.x needs aws-lc-rs &lt;1.18, 2.0.x needs &lt;1.12), so pin the version to stay on a certified module. The FIPS static library is Linux/BSD x86_64/aarch64 only; other platforms get a shared library.
- ML-KEM decapsulation (mlkem-native since aws-lc-sys 0.39) overflowed macOS's 544 KiB default non-main thread stack (#1101). Maintainers call this a configuration issue and advise 8 MiB thread stacks.
- Jitter-entropy init can call abort(): #1072 (open) reports crashes in tree_jitter_initialize_once in Windows VMs, also seen in uv. The documented \~50 ms per-process cost does not appear in the wtx 1.4 ms whole-process runs, and the reason is not documented.

## Known shortcomings

- aws-lc-rs is the Rust wrapper around AWS-LC (catalogued separately), so its speed is AWS-LC's. The only evidence times whole program runs (startup, PEM decoding, local TCP connect, one handshake); OpenSSL is a constant 2-5 ms slower in every combination, which looks like fixed startup/integration overhead rather than slower crypto (the author says the cause is unknown). rustc and OpenSSL versions/flags not stated. Trails ring and Graviola with RSA-PSS-SHA384 certificates.
- Adds no crypto of its own (every primitive is AWS-LC's); kept as AWS-LC's Rust binding. Loses to ring and Graviola with RSA-PSS certificates (6.4-6.7 ms vs 4.9-6.5 and 5.2-5.9). Binaries grow \~4 MB (up to 17 MB static MSVC, #745) and builds are several times slower than ring (#851); the size mode cuts footprint 60-70% but slows P-256 2-3x and P-384 3-6x. Jitter-entropy setup costs \~50 ms per process (Lambda cold-start regression #899; abort() in Windows VMs, #1072), avoidable only in non-FIPS builds. FIPS builds need CMake, Go and often bindgen/libclang; open build failures with old GCC cross-builds (#1022) and GCC 14+ FIPS (#569); no no_std. FIPS is a compile-time feature for the whole dependency graph (#1160), the certified module version is tied to the crate version, and the FIPS static library exists only for Linux/BSD x86_64/aarch64. The build silently links a system AWS-LC found via OPENSSL_DIR/pkg-config without rpath. ML-KEM decapsulation overflows macOS's 544 KiB default thread stack (#1101). Five 2026 aws-lc-sys advisories (AES-CCM timing; PKCS7, X.509, CRL bypasses) need aws-lc-sys 0.38/0.39+. ring-style API, no TLS/X.509 layer.

## Caveats and trade-offs

Single blog benchmark by the WTX author. Numbers exist only as SVG bar charts; values here were read from bar geometry (plotters output, about 0.01 ms per pixel). It times whole processes (process start, PEM decoding, loopback TCP, one handshake), not crypto alone. OpenSSL's near-constant 2-5 ms penalty in every combination suggests fixed init or integration overhead, and the author says the cause is unknown (compile flag, misconfiguration, openssl-sys, or OpenSSL itself). Only 10 runs per point; rustc and OpenSSL versions unstated. aws-lc-rs is Rust bindings over AWS-LC (github.com/aws/aws-lc, already catalogued), so the crypto speed shown is AWS-LC's.

Wraps the C aws-lc library via FFI; RSA-PSS handshake path is comparatively slower than ring/Graviola per this benchmark; larger binary footprint than pure-Rust alternatives.

## Maintenance

Active and widely used: v1.18.1 (2026-09-01), last commit 2026-09-17, about 237M crates.io downloads (88.6M in the last 90 days) and 366 reverse dependencies, under Apache-2.0 or ISC. Security fixes ship through aws-lc-sys (five 2026 RustSec advisories, patched in &gt;=0.38/0.39), so keep the sys crate current.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Independent blog benchmark with public code (wtx-bench.tar.xz: assets/bench.sh, Cargo.toml deploy profile) and a stated CPU (Ryzen 9 5900X), but no rustc version and no OpenSSL version or build flags, so not A. It is not a peer-reviewed paper or well-known suite, so not B; it measures whole-process time rather than isolated handshake cost.
- **Verifier notes:** SVG values extracted successfully: aws-lc-rs beats OpenSSL in all 45 combos (1.30x-3.44x) in this whole-process benchmark, but the fixed OpenSSL offset makes this weak evidence of crypto speed. Overlaps the catalogued AWS-LC entry (same C core); the orchestrator may prefer to fold it into AWS-LC as the Rust binding. License corrected from the repo LICENSE SPDX line.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes128gcmsha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/aes256gcmsha384.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/chacha20poly1305sha256.svg>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/wtx-bench.tar.xz>
  - <https://github.com/c410-f3r/wtx>
  - <https://github.com/aws/aws-lc-rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/LICENSE>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-sys/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/aws/aws-lc-rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/README.md>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs/README.md>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-fips-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/LICENSE>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/BUILDING.md>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-sys/README.md>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs/src/lib.rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs/src/fips.rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/builder/main.rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/builder/cc_builder.rs>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs-testing/Cargo.toml>
  - <https://raw.githubusercontent.com/aws/aws-lc-rs/main/aws-lc-rs-testing/benches/aead_benchmark.rs>
  - <https://aws.github.io/aws-lc-rs/index.html>
  - <https://aws.github.io/aws-lc-rs/platform_support.html>
  - <https://aws.github.io/aws-lc-rs/requirements/index.html>
  - <https://aws.github.io/aws-lc-rs/requirements/linux.html>
  - <https://aws.github.io/aws-lc-rs/resources.html>
  - <https://aws.github.io/aws-lc-rs/faq.html>
  - <https://c410-f3r.github.io/thoughts/tls-handshakes-measuring-the-performance-of-4-cryptography-libraries/>
  - <https://github.com/aws/aws-lc-rs/issues/745>
  - <https://github.com/aws/aws-lc-rs/issues/899>
  - <https://github.com/aws/aws-lc-rs/issues/851>
  - <https://github.com/aws/aws-lc-rs/issues/1101>
  - <https://github.com/aws/aws-lc-rs/issues/1107>
  - <https://github.com/aws/aws-lc-rs/issues/569>
  - <https://github.com/aws/aws-lc-rs/issues/1022>
  - <https://github.com/aws/aws-lc-rs/issues/1072>
  - <https://github.com/aws/aws-lc-rs/issues/1160>
  - <https://docs.rs/aws-lc-rs/latest/aws_lc_rs/aead/struct.LessSafeKey.html>
  - <https://crates.io/api/v1/crates/aws-lc-rs>
  - <https://crates.io/api/v1/crates/aws-lc-rs/reverse_dependencies>
  - <https://raw.githubusercontent.com/rustls/rustls/main/README.md>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/aws-lc-sys>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-sys/RUSTSEC-2026-0044.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-sys/RUSTSEC-2026-0045.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-sys/RUSTSEC-2026-0046.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-sys/RUSTSEC-2026-0047.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-sys/RUSTSEC-2026-0048.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-fips-sys/RUSTSEC-2026-0042.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/aws-lc-fips-sys/RUSTSEC-2026-0043.md>
  - <https://hn.algolia.com/api/v1/search?query=%22aws-lc-rs%22&tags=comment>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/aws/aws-lc-rs`) · [data/wave5/enrich/raw/github_com_aws_aws_lc_rs.json](../../../data/wave5/enrich/raw/github_com_aws_aws_lc_rs.json) (enrichment confidence 0.4)

</details>
