# moduletto (NEON i16 ML-KEM-512)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `PolyForm-Noncommercial-1.0.0` · 🟢 active

> Rust modular-arithmetic/NTT crate whose NEON ML-KEM-512 example edges out liboqs 0.16.0 on Apple M5 (\~1.18x).

| | |
|---|---|
| **Beats** | liboqs 0.16.0 (ML-KEM-512, built from source at tag 0.16.0, Release, -O3 -march=native, on aarch64/Apple M5) |
| **Claimed result** | \~1.18x faster full ML-KEM-512 session than LibOQS 0.16.0: 13.7-14.1 us vs 16.19 us per session. The page lists moduletto at 0.85x of LibOQS time; the README says \~1.18x. That is \~72,000 vs 61,800 sessions/sec, and moduletto is faster in all three phases: keygen 4.07 vs 4.72 us, encaps 3.84 vs 5.25 us, decaps 5.80 vs 6.22 us. Against the Kyber C reference (47.87 us, carried over from an unre-measured 2026-03-19 run) it is \~3.4-3.5x faster (derived from page data). The page's 2.96x is Kyber-ref vs LibOQS 0.16.0, not vs moduletto. |
| **Workload** | Full ML-KEM-512 KEM session (keygen+encaps+decaps), 10,000 iterations/100-iteration warmup, ACVP FIPS 203 conformant, on Apple M5 NEON |
| **Metric** | latency |
| **Hardware** | Apple M5 (Mac17,2), macOS Darwin 25.5.0 |
| **Compiler and flags** | moduletto: rustc (version unstated), Cargo release profile opt-level=3, lto=true, codegen-units=1, panic=abort; sha3 0.10 with the asm feature; timed by examples/kyber_benchmark (10,000 iterations, 100-iteration warmup). LibOQS: cmake -DCMAKE_BUILD_TYPE=Release -DOQS_MINIMAL_BUILD=KEM_ml_kem_512 -DCMAKE_C_FLAGS="-O3 -march=native" from tag 0.16.0, C compiler not named; a source comment says gcc. The LibOQS harness is not published and its results are hardcoded in the example. |
| **Adoption** | 10 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/crabnebula-dev/moduletto) · [benchmark](https://github.com/crabnebula-dev/moduletto/blob/main/BENCHMARKS.md) |

## Verdict

On an Apple M5 (macOS 25.5), the author's 10,000-iteration example times its NEON i16 ML-KEM-512 at 4.07/3.84/5.80 us (keygen/encaps/decaps, about 13.7-14.1 us per session), built with the Cargo release profile (LTO, codegen-units = 1) and an unstated rustc. That is compared with liboqs 0.16.0 built from source (-O3 -march=native) at 16.19 us, about 1.18x. The liboqs number comes from an unpublished C harness and is hardcoded in the example, so the comparison is first-party and not reproducible from the repo.

## Use it when

- Studying how a Rust ML-KEM-512 reaches liboqs-level speed on Apple Silicon: int16 NEON NTT, uzp/zip narrow layers, two-lane FEAT_SHA3 Keccak
- Non-commercial research or benchmarking on aarch64 with FEAT_SHA3 (Apple M-series), where the \~13.9 us session figure was measured
- Needing a small no_std-capable NTT/ModN arithmetic crate for q = 3329 experiments, with Coq proofs of the Barrett and constant-time primitives and fuzz targets
- Porting ideas (grouped codecs, streaming rejection sampler, paired Keccak lanes) into a permissively licensed ML-KEM implementation you write yourself

## Skip it when

- Any commercial product: PolyForm Noncommercial 1.0.0 forbids commercial use without a separate license
- Production key exchange: the KEM is benchmark example code with no public KEM API, no RNG integration, no zeroization, no independent review, and the decapsulation mask defect listed under gotchas
- x86-64 or other non-aarch64 targets: the NTT falls back to a portable i64 kernel and the i64 KEM backends measured 34.7-36.8 us on the M5, about 2x slower than liboqs
- ML-KEM-768/1024: only the 512 parameter set (k = 2) is implemented
- Needing a published package: the crate is not on crates.io (the README's moduletto = "0.1" snippet will not resolve), so it has to be a git dependency

## How it is fast

A pq-crystals-style int16 Montgomery NTT (R = 2^16, QINV = -3327) runs eight butterflies per NEON instruction (vmull_s16 / vmovn_s32 / vshrn_n_s32). The two narrow layers (len 4 and 2) are vectorised with uzp/zip deinterleaving, and lazy reduction plus a branchless rounding Barrett step removes per-layer reductions. Most of the session-level gain came from outside the NTT: grouped bit-packing codecs (43.6 to 27.7 us); a two-lane Keccak-f1600 that uses ARMv8.2 FEAT_SHA3 (EOR3/RAX1/XAR/BCAX) to pair independent SHAKE streams, with right-sized squeezing (to 16.1 us); and dropping round-3 Kyber's final KDF during the FIPS 203 fix (to 13.9 us).

## Compared with alternatives

Among the catalogued KEM/signature entries, this is the only ML-KEM one that times against liboqs on Apple Silicon NEON. sntrup is a usable, MIT/Apache crate for a different KEM (NTRU Prime) with a reproducible liboqs harness, and the Plantard-NTT paper targets formally verified NTTs compared against pq-crystals reference C. Pick moduletto only to learn aarch64 ML-KEM-512 optimisation techniques under a non-commercial license.

## Integration

| | |
|---|---|
| **Form** | crate (git only; also builds cdylib/rlib); the ML-KEM-512 code is a source-drop from examples/kyber_benchmark.rs |
| **Dependencies** | subtle 2.6 (core_hint_black_box); optional wasm-bindgen, web-sys, libm. The KEM example also needs sha3 0.10 (asm) and std; the hybrid example needs aes-gcm |
| **Minimum toolchain** | Not documented (no rust-version field; edition 2021). Fuzzing needs nightly, and the Coq proofs need Rocq 9.0+ and OCaml 5.0+ |
| **Platforms** | aarch64 (NEON i16 NTT; the two-lane Keccak needs FEAT_SHA3, runtime-detected); x86-64 and others use a portable i64 scalar path; wasm32 via the wasm feature; no_std supported |
| **Thread safety** | Not documented. Library functions are pure over stack arrays with no shared mutable state. The example caches the FEAT_SHA3 probe in an AtomicU8 |
| **Drop-in for the baseline** | no |

## Gotchas

- Decapsulation's constant-time equality mask is wrong in all three backends of the example (eq &= !(a ^ b).wrapping_neg() computes (a^b)-1 per byte, not 0x00/0xFF). A ciphertext whose only byte difference from the re-encryption is 0x02 yields mask 0x01, so the output mixes bits of the real key K' into the implicit-rejection key. The ACVP VAL vectors did not catch this. This is from reading the source; not reported upstream as of this review.
- The library's NEON NTT takes and returns [ModN&lt;3329&gt;; 256] (i64 per coefficient) and converts to and from i16 on every call (about 30 ns each way, per the source comment), so building a KEM on the public API will not reach the example's numbers
- Until 2026-08-11 the code implemented round-3 Kyber with a hardcoded zero implicit-rejection seed and eta1 = 2. The 2026-03-19 tables and the Platform Notes in BENCHMARKS.md describe that older, non-conformant code
- The LibOQS (16.19 / 20.43 us) and Kyber-ref (47.87 us) figures are hardcoded constants printed by the example. Running it re-times only moduletto

## Known shortcomings

- liboqs and Kyber-ref times are hard-coded constants in examples/kyber_benchmark.rs, measured by a C harness that is not in the repo; rustc version not stated (retiered A to C). The '2.96x' is Kyber-ref vs liboqs, not moduletto (moduletto vs Kyber-ref is \~3.4-3.5x, derived). The KEM lives in an example, not the library; FIPS 203 conformant only since 2026-08-11. PolyForm-Noncommercial license: reference use only. NEON (aarch64) only.
- Security bug (found in enrichment, by code reading): the decapsulation mask `!(a^b).wrapping_neg()` evaluates to (a^b)-1 rather than 0x00/0xFF in all three backends, so a ciphertext differing in one byte can leak real-key bits into the implicit-rejection output; ACVP vectors did not catch it and it is not reported upstream. Do not use for real keys. No API (KEM lives in an example), not on crates.io, no zeroize or RNG. Library NTT converts i64/i16 on every call; the x86 i64 path is \~2x slower than liboqs.

## Caveats and trade-offs

The margin over LibOQS is small (1.18x), and the author notes LibOQS 0.16.0 is itself 1.26x faster than 0.15.0, so comparisons against older releases overstate the lead. The LibOQS and Kyber-C-reference numbers are hardcoded constants in examples/kyber_benchmark.rs, measured by an unpublished C harness; the Kyber-ref column comes from a 2026-03-19 session and was not re-measured. The ML-KEM-512 KEM itself lives in the benchmark example, not the library API: the crate provides modular arithmetic and NTT. It only became FIPS 203 conformant on 2026-08-11, after ACVP vectors exposed six deviations, including a hardcoded zero implicit-rejection seed. The Platform Notes section at the bottom of BENCHMARKS.md is stale: it describes 2026-03-19, LibOQS 0.15.0 and Apple clang 17. The Cargo.toml repository field points to a nonexistent denjell/circlecimal. The PolyForm Noncommercial license is not OSI-approved, so the code is for study and evaluation only and cannot be used commercially without a separate license.

NEON-only fast path (i64 NTT + SHA3/inline-Keccak backends are 2.5-3x slower fallbacks for non-ARM); single-developer project, no independent security review; author's own doc flags that fixing FIPS 203 conformance bugs (found via ACVP vectors) was what got it under LibOQS, not the SIMD work alone

## Maintenance

One developer, 11 commits (the burst of 2026-08-11 changes delivered the FIPS 203 fixes and the speedups, and the last commit was 2026-09-03), no issues filed, not on crates.io, and noncommercial-licensed, so treat it as reference code to read, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** BENCHMARKS.md does show a same-machine full ML-KEM-512 session table against LibOQS 0.16.0 on an Apple M5, with LibOQS cmake flags. The public harness, examples/kyber_benchmark.rs, only times moduletto, though. The LibOQS 16.19/20.43 us and Kyber-ref 47.87 us figures are hardcoded constants in it (around lines 2518-2524), taken from a C harness that is not in the repo, and the rustc version is not stated. That makes these first-party numbers without a reproducible baseline run, so the tier is C, not A.
- **Verifier notes:** Downgraded A to C because the baseline numbers are hardcoded constants from a harness that is not in the repo. The Kyber-ref ratio was misattributed. Metadata is correct: license PolyForm-Noncommercial-1.0.0 (confirmed in the LICENSE file), 10 stars, last commit 2026-09-03, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/crabnebula-dev/moduletto>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/crabnebula-dev/moduletto/main/README.md>
  - <https://raw.githubusercontent.com/crabnebula-dev/moduletto/main/LICENSE>
  - <https://raw.githubusercontent.com/crabnebula-dev/moduletto/main/Cargo.toml>
  - <https://raw.githubusercontent.com/crabnebula-dev/moduletto/main/examples/kyber_benchmark.rs>
  - <https://github.com/denjell/circlecimal>
- **Sources the enricher read:**
  - <https://github.com/crabnebula-dev/moduletto>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/README.md>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/BENCHMARKS.md>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/Cargo.toml>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/LICENSE>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/src/lib.rs>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/src/ntt.rs>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/src/modn.rs>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/src/modn_ct.rs>
  - <https://github.com/crabnebula-dev/moduletto/blob/main/examples/kyber_benchmark.rs>
  - <https://api.github.com/repos/crabnebula-dev/moduletto/commits>
  - <https://api.github.com/repos/crabnebula-dev/moduletto/issues?state=all>
  - <https://crates.io/api/v1/crates/moduletto>
  - <https://github.com/denjell/circlecimal>
  - <https://hn.algolia.com/api/v1/search?query=moduletto>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/crabnebula-dev/moduletto`) · [data/wave7/enrich/raw/github_com_crabnebula_dev_moduletto.json](../../../data/wave7/enrich/raw/github_com_crabnebula_dev_moduletto.json) (enrichment confidence 0.8)

</details>
