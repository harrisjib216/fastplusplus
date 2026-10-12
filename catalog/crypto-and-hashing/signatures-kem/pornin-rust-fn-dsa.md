# FN-DSA (Rust, Falcon-based post-quantum signatures)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Unlicense` · 🟢 active

> Pure-Rust, no_std FN-DSA (Falcon) post-quantum signatures whose author reports faster signing and keygen than OpenSSL RSA-2048.

| | |
|---|---|
| **Beats** | OpenSSL RSA-2048 signing |
| **Claimed result** | Prose only, no RSA numbers on page: on i5-8259U (x86_64) FN-DSA/512 is 'about as fast as RSA-2048 for verification, but about 2.5x faster for signature generation, and many times faster for key pair generation'; on the ARM Cortex-A76 'signature generation with this code is about 8 times faster than OpenSSL's RSA-2048'; FN-DSA/512 is said to be 'substantially faster than RSA-2048 on all these systems' except x86_64 verify parity. FN-DSA/512 cycles on i5-8259U: keygen 8.91M, sign 1.13M, verify 63.3K. |
| **Workload** | Single FN-DSA/512 (Falcon) key generation, signature generation and verification, measured in CPU clock cycles, compared in prose against OpenSSL's RSA-2048 signing/verification cost on the same CPU families |
| **Metric** | latency |
| **Hardware** | Intel i5-8259U (Coffee Lake); ARM Cortex-A76 (Broadcom BCM2712C1); SiFive U74 (RISC-V) |
| **Compiler and flags** | Rust 1.97.1 (rustc) for the i5-8259U table (toolchain for ARM/RISC-V tables not stated); cargo bench harness in fn-dsa/benches (keygen.rs, sign.rs, verify.rs) reading rdtsc / pmccntr_el0 / rdcycle; AVX2 path auto-selected at runtime on x86_64, NEON on aarch64; RUSTFLAGS/target-cpu not stated; OpenSSL build/version/flags for the RSA-2048 comparison not stated |
| **Adoption** | 66 stars |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/pornin/rust-fn-dsa) · [benchmark](https://github.com/pornin/rust-fn-dsa#performance) |

## Verdict

The README reports FN-DSA-512 at 8.91M keygen, 1.13M sign and 63.3K verify cycles on an Intel i5-8259U with Rust 1.97.1 (AVX2 path), plus tables for a Cortex-A76 and a SiFive U74, all from the repo's cargo benches. The RSA-2048 comparison is prose only: parity for verify, about 2.5x faster signing and much faster keygen on x86_64, and about 8x faster signing on the Cortex-A76. No RSA cycle counts, OpenSSL version or flags are given, and the benches never run OpenSSL.

## Use it when

- Rust services or firmware that need a post-quantum signature with small outputs: 666-byte signatures and 897-byte public keys at FN-DSA-512, per the README size table.
- Verify-heavy x86_64 workloads: about 63K cycles per verify (47K when reusing a decoded key) on an i5-8259U, which the README puts on par with OpenSSL RSA-2048 verify.
- Replacing RSA-2048 signing on ARM servers or SBCs: the README reports signing about 8x faster than OpenSSL RSA-2048 on a Cortex-A76 (1.15M cycles per FN-DSA-512 signature).
- Signing many messages with one key: keeping a decoded SigningKey instance saves roughly 13-26% per signature in the README tables ('+sign' column).
- no_std or embedded targets that only verify: depend on fn-dsa-vrfy alone, which uses integer arithmetic only.

## Skip it when

- Anything that needs long-term interoperability now: no FN-DSA draft existed when the README was written, the 2026-07-22 release implements the author's 'best guess' at FIPS 206, and keys and signatures may break again before 1.0.
- Code that expects an OpenSSL, EVP or X.509 drop-in: this is a different algorithm with its own key and signature formats and a Rust-only API.
- Workloads dominated by key generation where latency matters: FN-DSA-512 keygen costs about 8.9M cycles (34.5M for 1024) on x86_64 and 40M+ on a SiFive U74, far slower than its sign or verify.
- Threat models needing strict constant-time on non-x86_64/aarch64 targets: those use a software floating-point emulation that the author calls best-effort and warns recent compilers may make variable-time.
- Projects that have moved to rand_core 0.9 or 0.10: the crate still requires rand_core 0.6 traits, and the PR to update (#10) is open.

## How it is fast

Keygen is a Rust port of Pornin's ntrugen (ePrint 2023/290). It solves the NTRU equation with fixed-point and 31-bit-prime RNS integer arithmetic instead of the slower code in the original Falcon submission. Signing follows Falcon's sign_dyn: it builds the FFT-domain Gram matrix and runs fast Fourier sampling with a constant-time discrete Gaussian sampler, using hardware f64 through SSE2 on x86_64 or NEON on aarch64. Verification needs only integer NTT arithmetic mod q = 12289. On x86/x86_64 a second AVX2 code path is chosen at runtime through cpufeatures; the README says it almost halves keygen and verify cost compared with SSE2 and helps signing only slightly.

## Compared with alternatives

Pick it over VecFalcon when you need a maintained, complete keygen/sign/verify library in Rust: VecFalcon reports 1.13-1.59x faster Falcon-512 sign_core than the C twin of this code, but it only vectorizes signing and is a research artifact. Pick it over the libsecp256k1 and UltrafastSecp256k1 entries only if you need post-quantum security, because those classical ECDSA libraries have smaller keys and signatures but no quantum resistance.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rand_core 0.6, zeroize 1.8, cpufeatures 0.2 (x86/x86_64 only) |
| **Minimum toolchain** | Rust 1.82 (declared rust-version), edition 2021 |
| **Platforms** | Any Rust target (no_std); tuned paths for x86/x86_64 (SSE2 plus runtime-detected AVX2), aarch64/arm64ec (NEON), riscv64 (RV64GC with D; optional div_emu/sqrt_emu for cores with variable-time FP divide/sqrt); other targets use integer-emulated floating point |
| **Thread safety** | Not documented. keygen() and sign() take &mut self because each instance holds its own scratch buffers (about 26/52 kB for keygen and 42/84 kB for signing), while verify() takes &self. Use one generator or SigningKey per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Sign contexts are large: a SigningKey for degree 1024 takes about 114 kB (82 kB with the small_context feature, which costs about 25% more signing time). Box it rather than putting it on a small stack.
- keygen() panics through assert! if logn is outside the generator's range, and sign() returns None only for an invalid key. Output slices must be exactly sign_key_size, vrfy_key_size or signature_size bytes.
- 32-bit x86 builds of crate 0.3.0 contain a Gaussian-sampler bug in the SSE2 path (z2 used where z1 should be), fixed on 2026-03-11 and first released in 0.4.0. Avoid 0.3.x on i686.
- The benchmarks read rdtsc (TSC reference ticks, not core cycles) with lfence and report the median of 10 batches of 1,000 operations; the README does not say whether Turbo Boost was disabled. Also, the AVX2 kernels are unsafe fns that are sound only behind the runtime check.

## Known shortcomings

- The OpenSSL RSA-2048 comparison is prose only (8x signing on Cortex-A76, 2.5x on x86, verify at parity) with no RSA cycle counts or flags. Written before any FN-DSA draft standard was published ('best guess' implementation), so outputs may not match the final FIPS 206. Unlicense: no patent grant.
- Benchmarks never run OpenSSL; rdtsc timing with Turbo state unstated. Keys and signatures may change before 1.0 (pre-FIPS 206 draft of 2026-07-22). 32-bit x86 SSE2 sampler bug affected crate 0.3.0 (fixed in 0.4.0, 2026-03-11). Still pinned to rand_core 0.6 (PR #10 open).

## Caveats and trade-offs

The OpenSSL RSA-2048 comparison is a prose claim ('about 8 times faster', 'about 2.5x') with no RSA cycle table, OpenSSL version or flags, and the repo's benches do not run OpenSSL, so it is a first-party claim with partial methodology, not a reproducible A/B benchmark. Per the README, no FN-DSA draft has been published yet and the 2026-07-22 update implements a 'best guess' at the upcoming draft; keys/signatures are expected to break compatibility before v1.0. Unlicense (public-domain dedication): no patent grant.

Pure Rust with runtime AVX2/NEON dispatch; a feature-parity C port exists (pornin/c-fn-dsa) with similar performance; Falcon/FN-DSA keys and signatures are larger than RSA/ECDSA equivalents and keygen is comparatively expensive (though far faster than RSA-2048 keygen); floating-point signing requires care for constant-time behavior

## Maintenance

Active single-author project by Thomas Pornin (last commit 2026-07-30, crate fn-dsa 0.4.0 at about 107K downloads), Unlicense (public-domain dedication, no patent grant), and deliberately pre-1.0 until FIPS 206 is final; a C twin (pornin/c-fn-dsa) reproduces the same test vectors.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives first-party FN-DSA cycle tables (i5-8259U, Cortex-A76, SiFive U74; Rust 1.97.1) from public benches (fn-dsa/benches/\*.rs), but the OpenSSL RSA-2048 comparison is prose-only ratios with no RSA cycle counts, no OpenSSL version/flags and no benchmark harness for the baseline, so it cannot reach A; not peer-reviewed, so not B.
- **Verifier notes:** Metadata verified via gh: Unlicense, not archived/fork, 66 stars, last commit 2026-07-30 (active). Numbers and the 8x / 2.5x / parity phrasing match the README exactly; only the caveats/flags were sharpened.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pornin/rust-fn-dsa>
  - <https://github.com/pornin/rust-fn-dsa#performance>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/benches/util.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/pornin/rust-fn-dsa>
  - <https://github.com/pornin/rust-fn-dsa#performance>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-comm/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-kgen/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-sign/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-vrfy/Cargo.toml>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/src/lib.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-sign/src/lib.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-sign/src/sampler.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-sign/src/flr.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-kgen/src/lib.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-vrfy/src/lib.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-comm/src/lib.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa-comm/src/mq_avx2.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/benches/util.rs>
  - <https://github.com/pornin/rust-fn-dsa/blob/main/fn-dsa/benches/sign.rs>
  - <https://github.com/pornin/rust-fn-dsa/issues>
  - <https://github.com/pornin/rust-fn-dsa/issues/12>
  - <https://github.com/pornin/rust-fn-dsa/issues/6>
  - <https://github.com/pornin/rust-fn-dsa/pulls>
  - <https://github.com/pornin/rust-fn-dsa/commits/main>
  - <https://github.com/pornin/rust-fn-dsa/commit/0629bb118ebf077857e78c1bd067c704a37795ed>
  - <https://github.com/pornin/rust-fn-dsa/commit/b0c78e874d745be79a6068fdffd6bfafff3d653d>
  - <https://github.com/pornin/rust-fn-dsa/commit/e06720efc7b3f0e0583a18851011dc21d59ed7c2>
  - <https://crates.io/api/v1/crates/fn-dsa>
  - <https://crates.io/api/v1/crates/fn-dsa-sign/0.3.0/dependencies>
  - <https://crates.io/api/v1/crates/fn-dsa-sign/0.4.0/dependencies>
  - <https://crates.io/api/v1/crates/fn-dsa-kgen/0.3.0/dependencies>
  - <https://crates.io/api/v1/crates/fn-dsa-kgen/0.4.0/dependencies>
  - <https://github.com/pornin/c-fn-dsa>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/pornin/rust-fn-dsa`) · [data/wave7/enrich/raw/github_com_pornin_rust_fn_dsa.json](../../../data/wave7/enrich/raw/github_com_pornin_rust_fn_dsa.json) (enrichment confidence 0.72)

</details>
