# sntrup (Streamlined NTRU Prime, pure Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust Streamlined NTRU Prime KEM: ties liboqs AVX2 on Zen 5 and beats liboqs portable C on Apple M2 1.2-2.7x.

| | |
|---|---|
| **Beats** | liboqs 0.13.0 via oqs-sys 0.11.0 (sntrup761: AVX2 SUPERCOP-derived backend on x86_64, portable C on aarch64) and PQClean sntrup761 clean C via pqcrypto-ntruprime 0.1.6 (avx2 feature off) |
| **Claimed result** | Current page (Where things stand and the README). On x86_64 (Ryzen AI 9 HX 370, Zen 5) against liboqs's AVX2 build: keypair 106.6 vs 107.9 us (0.99x), encapsulate 10.5 vs 11.5 us (0.91x), decapsulate 8.4 vs 8.4 us (1.00x). That is parity to \~9% faster; round 24 gives 107.81/10.46/8.46 us (0.99x/0.91x/1.01x). Against PQClean clean C on x86 it is 42.7x/22.9x/72.6x faster. On aarch64 (Apple M2 Max, ARM round 3) against liboqs portable C: keypair 683.7 us vs 1.876 ms (2.7x), encapsulate 37.0 vs 52.7 us (1.42x), decapsulate 77.1 vs 91.8 us (1.19x). The record's figures (1.341 ms/50.00/84.52 us on ARM; liboqs 3.3x/2.8x/6.3x ahead on x86) are from the first runs in this append-only log and are outdated. |
| **Workload** | sntrup761 keypair generation, encapsulation and decapsulation, Criterion benchmarks run in the same process against liboqs (oqs-sys) and PQClean (pqcrypto-ntruprime) in benches/comparison |
| **Metric** | latency |
| **Hardware** | Apple M2 Max, macOS (aarch64); AMD Ryzen AI 9 HX 370 'Strix Point' Zen 5, Fedora Linux, pinned to one 5.16GHz core via taskset (x86_64) |
| **Compiler and flags** | rustc 1.97.1 (aarch64 runs) / rustc 1.98.0-nightly (x86_64 runs), Cargo release profile. Criterion 0.8.1 with a 1 s warm-up, a 3 s measurement window and 10 samples for keygen. oqs 0.11.0 (oqs-sys 0.11.0+liboqs-0.13.0) is built from vendored source; its C build is driven by oqs-sys, with clang 22 on Fedora mentioned for bindgen. pqcrypto-ntruprime 0.1.6 is built without its avx2 feature. |
| **Adoption** | 0 stars; crates.io sntrup v0.4.0 has \~2.8k total downloads |
| **Last commit** | 2026-08-05 |
| **Links** | [repository](https://github.com/mikelodder7/sntrup) · [benchmark](https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/RESULTS.md) |

## Verdict

A public same-process Criterion 0.8.1 harness runs sntrup761 against liboqs 0.13.0 (oqs-sys 0.11.0) and PQClean clean C (pqcrypto-ntruprime 0.1.6, avx2 off), with one key reused per benchmark. On a Ryzen AI 9 HX 370 (Zen 5, one pinned core, rustc 1.98 nightly) against liboqs's AVX2 build, it measured 106.6/10.5/8.4 us vs 107.9/11.5/8.4 us for keypair/encaps/decaps, parity to about 9% faster, and 23-73x faster than PQClean. On an Apple M2 Max (rustc 1.97.1) against liboqs portable C, it measured 683.7 us vs 1.876 ms, 37.0 vs 52.7 us and 77.1 vs 91.8 us.

## Use it when

- Rust services that need sntrup761 (for example an OpenSSH-style sntrup761x25519 hybrid) without a C toolchain or FFI to liboqs
- aarch64 servers or Apple Silicon, where liboqs and PQClean have no NEON sntrup path: measured 2.7x keypair, 1.42x encapsulation and 1.19x decapsulation on an M2 Max
- Long-lived decapsulation keys that decapsulate many ciphertexts: the per-key decoded-polynomial cache is amortised, which is the pattern the benchmark measures
- Needing sntrup653/857/953/1013/1277, which liboqs and pqcrypto-ntruprime do not provide
- Code that must wipe secret-derived scratch (the C references do not), or wasm32 via the js feature

## Skip it when

- x86_64 stacks that already link liboqs: it is at parity at best (0.91-1.00x), and on AVX2-only CPUs without AVX-512 keypair measured about 1.11x slower than liboqs
- Ephemeral single-use keys: the first encapsulate/decapsulate on a fresh key pays the public-key decode that the benchmark amortises (about 2 us of x86 decapsulation; the encapsulation-key cache was worth 12% on ARM)
- Anything requiring an audited or certified KEM: the code is unaudited by its own warning, has one maintainer and 0 stars, and its reviews are LLM audits noted in the log and commits
- no_std or embedded targets, despite the README claim (see gotchas)
- Non-761 parameter sets or aarch64 where you expect the x86 sntrup761 numbers: the NTT, codec761, codec3, djbsort and bitsliced R/3 modules compile on x86_64 only, and the NTT multiply is used only for sntrup761, so the other sets and all of aarch64 run schoolbook multiplies

## How it is fast

On x86_64, sntrup761 uses ports of the SUPERCOP/liboqs AVX2 techniques. The polynomial multiply uses Good's trick (3x512) with two 512-point NTTs over the NTT-friendly primes 7681 and 10753, recombined by CRT, in place of an O(p^2) schoolbook. Both ring inversions use constant-time Bernstein-Yang divstep (R/3 bitsliced), and the R/q divstep also has an AVX-512BW 32-lane kernel that liboqs lacks. Constant-weight sampling uses a djbsort crypto_sort_int32 port, and the variable-radix codecs are vectorised. aarch64 gets a NEON divstep, a schoolbook multiply spread over eight independent widening multiply-accumulate chains, and a NEON Batcher sort. Both architectures cache each key's decoded public polynomial and Hash4(pk), draw randomness in one bulk fill, and keep scratch on the stack with wide volatile wipes.

## Compared with alternatives

Pick it over moduletto (ML-KEM-512 NEON code that is benchmark-example-only and PolyForm-Noncommercial) when you need a permissively licensed, published KEM crate with a reproducible same-process liboqs comparison, and specifically NTRU Prime. fasthqc/hqc is a research speedup of the HQC round-2 reference, a different KEM family and not a Rust library.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | hex, rand 0.10, rand_chacha 0.10, sha2 0.11, subtle 2, thiserror 2, zeroize 1; optional getrandom 0.4 (js), kem 0.3 + hybrid-array + rand_core (kem), serde + serdect (serde) |
| **Minimum toolchain** | Rust 1.95 (edition 2024; MSRV declared and CI-enforced) |
| **Platforms** | x86_64 (AVX2, AVX-512F/BW/VL and AVX-VNNI detected at run time, scalar fallback); aarch64 (NEON); other targets scalar; wasm32-unknown-unknown with the js feature |
| **Thread safety** | Not documented. Key types hold std::sync::OnceLock caches and the CPU probes are cached in atomics, so keys can be shared across threads and a first-use race is resolved by OnceLock |
| **Drop-in for the baseline** | partial: the sntrup761 key and ciphertext sizes match liboqs (the harness asserts this) and the IETF-draft decapsulation KATs pass, but the interface is a typed Rust API, not liboqs's OQS_KEM C ABI |

## Gotchas

- The README says no_std-compatible, but 0.4.0 has no #![no_std] attribute and unconditionally uses std::sync::OnceLock (key caches, the decode-plan cache) and std::is_x86_feature_detected!. The std/alloc features are empty markers.
- `--all-features` turns on force-scalar and silently compiles out every SIMD kernel. Do not build release or CI binaries with it if you want the benchmarked speed.
- Pin 0.4.0 or later: earlier releases had a non-canonical Barrett freeze that could produce rare invalid keys or ciphertexts on all six sets (fixed in 0.4.0), and sntrup953 misreduced about 0.7% of reductions before 0.3.0.
- The only external known-answer vectors are two IETF-draft sntrup761 decapsulation cases. The other five sets rely on round-trip, implicit-rejection and SIMD-vs-scalar differential tests. The ChaCha20 state used by generate_key_deterministic is not wiped.

## Known shortcomings

- On x86 (Zen 5) it is now at parity with liboqs AVX2 (0.99x/0.91x/1.00x keygen/encaps/decaps; keygen wins need AVX-512); the clear win is on aarch64 against liboqs's portable C (2.7x/1.42x/1.19x). Baseline is liboqs 0.13.0 via oqs-sys 0.11.0.
- Benchmark reuses one key, so per-key decode caches stay warm (the author notes it is not like-for-like); ephemeral keys cost \~2 µs more. AVX2-only keypair is 1.11x slower than liboqs. README's 'no_std' is false (uses std OnceLock and is_x86_feature_detected!); `--all-features` silently selects the scalar path. Unaudited (LLM audits only), one maintainer, 0 stars; only 2 external KATs (sntrup761 decaps).

## Caveats and trade-offs

On x86_64 the lead over liboqs's AVX2 build is only parity to \~9%. The keypair win depends on an AVX-512 divstep path (Zen 5) that liboqs lacks. With AVX2 only (round 23), keypair was still 1.11x slower than liboqs. The aarch64 wins (2.7x/1.42x/1.19x) are against liboqs and PQClean portable C, because neither has a NEON sntrup761 path. The very large PQClean ratios on x86 are against clean C, since the avx2 feature was deliberately left off. The baseline is liboqs 0.13.0 via oqs-sys 0.11.0, not a current liboqs release. The headline summary table mixes figures from different rounds (keypair 106.6 in the summary vs 107.81 in the round 24 table), and the early x86 run had a concurrent video call. The project has a single maintainer and 0 GitHub stars, but RESULTS.md is an unusually rigorous same-run engineering log.

Pure Rust with automatic AVX-512/AVX2/AVX-VNNI/NEON runtime dispatch; on x86_64 it does not beat liboqs's hand-tuned AVX2 SUPERCOP kernel, only PQClean's plain C; every secret-derived buffer is zeroized (a security win over the C references, which don't wipe), at a measured \~11% throughput cost that is included in the reported numbers

## Maintenance

Active single-maintainer crate: v0.4.0 went to crates.io on 2026-08-05 with the whole optimisation campaign, about 2.8k total downloads, MIT OR Apache-2.0, no issues filed, and explicitly unaudited, so it is fine to adopt for sntrup761 in Rust if you accept that risk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The public Criterion harness, benches/comparison/benches/implementations.rs, runs sntrup, liboqs (oqs 0.11.0 / oqs-sys 0.11.0+liboqs-0.13.0) and PQClean (pqcrypto-ntruprime 0.1.6, avx2 off) in the same process, with pinned versions. RESULTS.md states rustc 1.97.1 on an Apple M2 Max, rustc 1.98.0-nightly on a Ryzen AI 9 HX 370 (Zen 5) pinned to one core, the release profile and the feature choices. Tier A holds.
- **Verifier notes:** Confirmed at tier A. The claim was understated: the record's x86 'liboqs wins by 2.8-6.3x' caveat reflects the first x86 run; the latest rounds show parity to slightly faster than liboqs on x86 and 1.19-2.7x faster on aarch64. Metadata is correct: Apache-2.0 OR MIT (dual license files, and the README says 'either of'), last commit 2026-08-05, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** sntrup bench: Zen 5 vs liboqs AVX2 0.99x/0.91x/1.00x; aarch64 vs liboqs portable C 2.7x/1.42x/1.19x.
- **Pages the verifier opened:**
  - <https://github.com/mikelodder7/sntrup>
  - <https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/RESULTS.md>
  - <https://raw.githubusercontent.com/mikelodder7/sntrup/main/README.md>
  - <https://raw.githubusercontent.com/mikelodder7/sntrup/main/benches/comparison/README.md>
  - <https://raw.githubusercontent.com/mikelodder7/sntrup/main/benches/comparison/Cargo.toml>
  - <https://raw.githubusercontent.com/mikelodder7/sntrup/main/benches/comparison/Cargo.lock>
  - <https://raw.githubusercontent.com/mikelodder7/sntrup/main/benches/comparison/benches/implementations.rs>
  - <https://crates.io/api/v1/crates/sntrup>
  - <https://crates.io/api/v1/crates/oqs-sys/versions>
- **Sources the enricher read:**
  - <https://github.com/mikelodder7/sntrup>
  - <https://github.com/mikelodder7/sntrup/blob/main/README.md>
  - <https://github.com/mikelodder7/sntrup/blob/main/Cargo.toml>
  - <https://github.com/mikelodder7/sntrup/blob/main/CHANGELOG.md>
  - <https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/RESULTS.md>
  - <https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/README.md>
  - <https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/Cargo.toml>
  - <https://github.com/mikelodder7/sntrup/blob/main/benches/comparison/benches/implementations.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/src/lib.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/src/cpu.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/src/types.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/src/wipe.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/src/rq/encoding.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/tests/kat.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/tests/kem.rs>
  - <https://github.com/mikelodder7/sntrup/blob/main/.github/workflows/sntrup.yml>
  - <https://api.github.com/repos/mikelodder7/sntrup/commits>
  - <https://api.github.com/repos/mikelodder7/sntrup/issues?state=all>
  - <https://crates.io/api/v1/crates/sntrup>
  - <https://crates.io/api/v1/crates/sntrup/versions>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mikelodder7/sntrup`) · [data/wave7/enrich/raw/github_com_mikelodder7_sntrup.json](../../../data/wave7/enrich/raw/github_com_mikelodder7_sntrup.json) (enrichment confidence 0.8)

</details>
