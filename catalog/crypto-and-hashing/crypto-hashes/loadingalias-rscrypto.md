# rscrypto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Zero-dependency Rust crypto crate whose SIMD/asm SHA-2, SHA-3, BLAKE2 and AEADs beat RustCrypto, ring and aws-lc-rs in its benchmarks.

| | |
|---|---|
| **Beats** | Fastest external Rust implementation per case. SHA-256/384/512: RustCrypto sha2, aws-lc-rs (AWS-LC) and ring. SHA3-224/256/384/512: RustCrypto sha3. BLAKE2: RustCrypto blake2, plus dryoc for BLAKE2b. |
| **Claimed result** | Fastest-external geomean on the 2026-08-18 eight-host Linux scorecard (ratio = external_time / rscrypto_time; &gt;1x means rscrypto is faster): sha256 1.27x (104 rows, W/T/L 44/46/14; all-pairs geomean 1.60x), sha384 1.30x, sha512 1.29x, sha3-224 2.27x, sha3-256 2.28x, sha3-384 2.35x, sha3-512 2.38x, blake2b256 1.07x (all-pairs 1.31x), blake2b512 1.08x (all-pairs 1.33x), blake2s256 1.11x, blake2s128 1.13x. The page gives no per-primitive medians. The 1.60x, 1.31x and 1.33x figures that the original record labelled medians are all-pairs geomeans. |
| **Workload** | Criterion benchmarks (benches/sha2.rs, benches/sha3.rs, benches/blake2.rs) of one-shot and streaming SHA-224/256/384/512, SHA3-224/256/384/512 and BLAKE2b/BLAKE2s hashing across input sizes. They ran on the 2026-08-18 eight-host Linux matrix: x86_64 AMD/Intel, aarch64 Graviton3/4, ppc64le Power10 and s390x z16. |
| **Metric** | throughput |
| **Hardware** | 2026-08-18 eight-host Linux scorecard: AMD Zen4, AMD Zen5, AWS Graviton3, AWS Graviton4, IBM Power10, IBM z16 (s390x), Intel Ice Lake and Intel Sapphire Rapids. The page names microarchitecture families only, with no exact SKUs or instance types for this snapshot. The RISC-V host did not contribute, and there are no Windows hosts in this scorecard. |
| **Compiler and flags** | Not stated on the page for the 2026-08-18 snapshot. At the snapshot commit 7eb44e9 the repo pins rust-toolchain nightly-2026-07-17 and sets RUSTFLAGS -C target-cpu=native in .cargo/config.toml (with +lse on aarch64) for Linux x86_64/aarch64. The bench profile inherits release: opt-level=3, lto=fat, codegen-units=1, panic=abort. The harness is Criterion. Rust 1.98.1 and 1.99.0-nightly were the toolchains of the separate 2026-09-14 run, whose ratios are not in the scorecard. |
| **Adoption** | 38 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/loadingalias/rscrypto) · [benchmark](https://github.com/loadingalias/rscrypto/blob/main/benchmark_results/OVERVIEW.md) |

## Verdict

On the 2026-08-18 eight-host Linux snapshot, rscrypto's fastest-external geomean was 1.27-1.30x on SHA-256/384/512 (against RustCrypto sha2, ring and aws-lc-rs), 2.27-2.38x on SHA3 (against RustCrypto sha3) and 1.07-1.13x on BLAKE2 (against RustCrypto blake2 and dryoc). The hosts were Zen4/Zen5, Graviton3/4, Power10, z16, Ice Lake and Sapphire Rapids, running commit 7eb44e9 built with nightly-2026-07-17, target-cpu=native and fat LTO, with Criterion over 0 B-1 MiB inputs. The AEAD geomeans, against RustCrypto, ring, aws-lc-rs and the aegis/ascon-aead crates, were 1.80x/1.83x (AES-128/256-GCM), 2.20x/2.34x (AES-GCM-SIV), 1.12x (ChaCha20-Poly1305), 1.43x (XChaCha20-Poly1305), 1.23x (AEGIS-256) and 1.39x (Ascon-AEAD128). OpenSSL itself was never measured.

## Use it when

- You want one dependency-free, no_std-capable Rust crate for SHA-2, SHA-3, BLAKE2 and AEADs instead of mixing RustCrypto, ring and aws-lc-rs, and you can live with a pre-1.0 API.
- SHA-3/SHAKE-heavy workloads: the fastest-external geomean is 2.27-2.38x over RustCrypto sha3, with zero losses in 88-104 rows per variant.
- AES-GCM-SIV or AES-GCM on AVX-512/VAES x86-64 Linux: geomeans of 2.20x/2.34x (GCM-SIV) and 1.80x/1.83x (GCM) against the fastest of RustCrypto, ring and aws-lc-rs.
- Mixed-ISA fleets that include IBM z16 (s390x) or POWER10, where it ships native kernels and posts its widest margins (2.77x per-host geomean on s390x).
- Pure-Rust XChaCha20-Poly1305: 173 wins, 3 ties and 0 losses, a 1.43x geomean against RustCrypto (the only competitor benchmarked for it).

## Skip it when

- You need a third-party audit, FIPS 140-3 validation or a whole-crate constant-time guarantee. The README says it has none of these; constant-time claims are per operation and per target in ct.toml.
- Your code is generic over RustCrypto's `digest`/`aead` traits or uses ring/aws-lc-rs types. rscrypto has its own traits and no dependencies, so every call site changes.
- BLAKE2 or ChaCha20-Poly1305 alone would justify the switch. Their margins are thin (1.07-1.13x geomean, with roughly half the rows ties, e.g. blake2b256 101 wins, 99 ties).
- You need a stable, slow-moving dependency. Versions 0.1 to 0.9 shipped in four months (May-Aug 2026), and main already requires Rust 1.100.0 and pins a nightly toolchain.
- You would adopt the whole stack for ECDSA. P-256/P-384 loses overall (0.87x fastest-external geomean), and the 2026-08-18 run recorded a severe s390x signing regression.

## How it is fast

Three-tier dispatch (compile-time target features, then cached runtime CPU detection, then portable Rust) routes each primitive to a per-ISA kernel. SHA-256 uses the Intel SHA extensions (SHA-NI) or the ARMv8 SHA2 instructions; SHA-512 uses AVX2/AVX-512VL kernels based on the Gueron-Krasnov two-block schedule; on s390x the IBM Z CPACF KIMD instruction runs SHA-2 and absorbs SHA-3 blocks in hardware. Single-message SHA-3 on x86-64 and AArch64 is portable Keccak-f[1600] using XKCP's 'Bebigokimisa' lane-complementing trick; the AVX-512 and ARM SHA3 kernels only serve two-state paired paths. On AEADs, Linux x86-64 gets in-house VAES-512 AES-GCM and GCM-SIV assembly (16-, 64- and 128-block variants) plus ChaCha20-Poly1305 assembly adapted from AWS-LC/BoringSSL, and BLAKE2 gets AVX2/AVX-512VL row-vectorized compression.

## Compared with alternatives

Pick it over blake2b_simd, the official BLAKE3 crate or keccak-batch when you want one dependency-free crate covering SHA-2, SHA-3, BLAKE2/3 and AEADs, with runtime dispatch on x86, ARM, POWER and s390x. Stay with blake2b_simd or official BLAKE3 for a mature single-algorithm crate (rscrypto's BLAKE3 median against official blake3 is only 1.04x), and with hashtree or keccak-batch for batched many-message hashing.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional getrandom (OS entropy), rayon (`parallel` BLAKE3/Argon2) and serde |
| **Minimum toolchain** | Published 0.9.0 declares Rust 1.91 on crates.io. The main branch (README says 0.10, not yet published) declares rust-version 1.100.0 and edition 2024, and pins nightly-2026-09-25. |
| **Platforms** | Portable Rust anywhere. Accelerated and tested on Linux x86-64, AArch64, POWER (ppc64le), IBM Z (s390x) and RISC-V, Windows x86-64, Apple Silicon macOS and wasm32 (simd128). Windows AArch64 is compile-only; x86_64-apple-darwin is unsupported. |
| **Thread safety** | Not documented explicitly. Hashers and ciphers are owned values updated through &mut self. CPU detection is cached process-wide on first use, and capability overrides must happen before the first platform::caps() call. |
| **Drop-in for the baseline** | partial — same algorithms and byte-identical outputs, but its own Digest/Aead traits and typed key/nonce API replace RustCrypto's digest/aead traits and the ring/aws-lc-rs interfaces, so call sites must be rewritten. |

## Gotchas

- no_std builds select kernels only from compile-time target features. Without -C target-cpu or target-feature flags they run portable Rust (no SHA-NI, VAES and so on). The published scorecard was built with -C target-cpu=native.
- The `portable-only` feature only disables runtime detection. It does not remove the compiled SIMD/asm code or override compile-time target features.
- Some paths stay portable by design: single-message SHA-3 on x86-64/AArch64 (the vector Keccak kernels are two-state only) and SHA-256 on POWER, where the vector kernel lost to portable Rust.
- The 2026-08-18 AEAD rows time buffer restoration (copy-and-encrypt), and the BLAKE2 rows include duplicated cases. The maintainer flags both but has not recomputed those historical ratios. The newer 2026-09-14 run (19,614 cases) has no curated ratios yet.

## Known shortcomings

- Rust-only; baselines are Rust crates (ring, aws-lc-rs, RustCrypto), not OpenSSL directly. The 'median 1.60/1.31/1.33x' figures are all-pairs geometric means; raw results for the cited 2026-08-18 run are no longer in the repo. Built with nightly and target-cpu=native.
- Own Digest/Aead traits (not a RustCrypto drop-in); unaudited, no FIPS; pre-1.0 API churn; main needs Rust 1.100 plus a nightly pin (published 0.9.0 needs 1.91). AEAD rows include a buffer copy; BLAKE2 rows are duplicated; OpenSSL is never measured. Single-message SHA-3 on x86/ARM and SHA-256 on POWER use portable Rust; no_std without target flags is portable only.

## Caveats and trade-offs

The baseline is the fastest competing Rust crate or binding per case. For SHA-2 it includes aws-lc-rs (AWS-LC, OpenSSL/BoringSSL lineage) and ring, but OpenSSL itself was not tested, so baseline_in_list stays false. OVERVIEW.md withdraws its ML-KEM and Argon2 comparisons. It also flags historical BLAKE2 host-overhead and parameter rows as duplicates of the main one-shot cases without recomputing ratios, so the BLAKE2 row counts and geomeans may include duplicated cases. The scorecard is a historical snapshot of commit 7eb44e9. The raw results.txt files it cites under benchmark_results/2026-08-18/ are no longer in the repo. Compiler flags for the cross-built POWER and s390x hosts are not stated.

Rust-only, no_std feature-gated, zero default OpenSSL/system-lib dependency; baseline is other Rust crates, not the OpenSSL C library itself.

## Maintenance

Active single-author project: first release May 2026, 0.9.0 on crates.io in August 2026 (about 1.5k downloads), commits through 2026-09-26. It is MIT OR Apache-2.0 and usable as a crate today, but it is pre-1.0, unaudited and changing fast.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** OVERVIEW.md's Primitive Summary gives the fastest-external geomeans for every listed primitive (sha256 1.27x, sha3-256 2.28x, blake2b256 1.07x, and so on) from the 2026-08-18 eight-host Linux snapshot at commit 7eb44e9. The benchmark code is public (benches/sha2.rs, benches/sha3.rs, benches/blake2.rs, Criterion). The repo at that commit pins rust-toolchain nightly-2026-07-17 and sets -C target-cpu=native in .cargo/config.toml, and the bench profile uses opt-level=3, fat LTO and codegen-units=1. CPU families are named per host.
- **Verifier notes:** The original record mixed in hardware and toolchains from the separate 2026-09-14 run (c8a/c8i/c9g plus Windows), which the page says is not folded into the scorecard; I replaced them with the 2026-08-18 hosts. GitHub's API reports the license as Apache-2.0, but Cargo.toml declares MIT OR Apache-2.0 and both LICENSE files are present. I kept tier A because code, toolchain pin, flags and CPU families are all recoverable at the snapshot commit.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `workload`, `license`, `caveats`
- **Shortcomings recorded by:** rscrypto CI geomeans vs fastest external Rust crate: SHA-2 1.27-1.30x, SHA-3 2.27-2.38x, BLAKE2 1.07-1.13x; AES-GCM 1.80-1.83x, GCM-SIV 2.20-2.34x, ChaCha20-Poly1305 1.12x, XChaCha20-Poly1305 1.43x, AEGIS-256 1.23x, Ascon-AEAD128 1.39x.
- **Pages the verifier opened:**
  - <https://github.com/loadingalias/rscrypto>
  - <https://github.com/loadingalias/rscrypto/blob/main/benchmark_results/OVERVIEW.md>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/Cargo.toml>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/.cargo/config.toml>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/benches/sha2.rs>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/benches/sha3.rs>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/benches/blake2.rs>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/main/docs/benchmarking.md>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/7eb44e9a38ef7a031d9181dc8c4c0fad38f46504/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/loadingalias/rscrypto/7eb44e9a38ef7a031d9181dc8c4c0fad38f46504/.cargo/config.toml>
- **Sources the enricher read:**
  - <https://github.com/loadingalias/rscrypto>
  - <https://github.com/loadingalias/rscrypto/blob/main/README.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/benchmark_results/OVERVIEW.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/Cargo.toml>
  - <https://github.com/loadingalias/rscrypto/blob/main/rust-toolchain.toml>
  - <https://github.com/loadingalias/rscrypto/blob/main/.cargo/config.toml>
  - <https://github.com/loadingalias/rscrypto/blob/main/docs/platforms.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/docs/features.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/docs/benchmarking.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/CHANGELOG.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/THREAT_MODEL.md>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/lib.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/traits/digest.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/platform/detect.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha256/x86_64.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha256/aarch64.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha256/s390x.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha256/dispatch_policy.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha512/x86_64_avx512vl.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/kernels.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/dispatch.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/dispatch_tables.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/x86_64.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/aarch64.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/keccak/s390x.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/sha3.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/hashes/crypto/blake2b/x86_64.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/aead/mod.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/aead/aes/x86_64/asm.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/aead/aes/x86_64_ni.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/aead/aes256gcmsiv.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/src/aead/chacha20poly1305/x86_64_asm.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/benches/aead.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/benches/sha2.rs>
  - <https://github.com/loadingalias/rscrypto/blob/main/benches/common/mod.rs>
  - <https://github.com/loadingalias/rscrypto/issues>
  - <https://crates.io/api/v1/crates/rscrypto>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/loadingalias/rscrypto`) · [data/wave7/enrich/raw/github_com_loadingalias_rscrypto.json](../../../data/wave7/enrich/raw/github_com_loadingalias_rscrypto.json) (enrichment confidence 0.7)

</details>
