# ocaml-curve448

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `OCaml (C backend via FFI)` · `ISC` · 🟢 active

> OCaml X448/Ed448 library whose optional fiat-crypto C backend roughly matches OpenSSL 3.6.4 on X448 and Ed448 signing; verification is slower.

| | |
|---|---|
| **Beats** | OpenSSL 3.6.4 (`openssl speed`, EVP Ed448/X448) |
| **Claimed result** | On AMD Ryzen AI 9 HX PRO 370: C backend Ed448 sign \~2.3x faster than OpenSSL (48us vs 111us), X448 key exchange \~19% faster (93us vs 115us); on Apple M1 Pro sign/key-exchange are roughly on par with OpenSSL; Ed448 verify is consistently slower than OpenSSL (152-203us vs 121-141us) because it is constant-time versus OpenSSL's variable-time double-scalar multiplication |
| **Workload** | Single-operation X448 key exchange, Ed448 key pair from seed, and Ed448 sign/verify of a 64-byte message (Ed448ph is not benchmarked). Best of three 1-second runs of the project's OCaml bench (bench/bench_curve448.ml, via the OCaml bindings), compared against `openssl speed` numbers for OpenSSL 3.6.4 on the same machine. Keypair-from-seed has no OpenSSL figure. |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (macOS) and AMD Ryzen AI 9 HX PRO 370 (Linux) |
| **Compiler and flags** | C backend stubs built with dune --profile release using OCaml's :standard C flags (lib/c/dune), with GCC or Clang (compiler and version not stated); OCaml 5.4.1 (M1 Pro) / 5.5.1 (Ryzen); baseline OpenSSL 3.6.4 via `openssl speed` (its build flags not stated) |
| **Adoption** | 0 stars (repo created 2026-09-13; not yet published to opam) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/thevilledev/ocaml-curve448) · [benchmark](https://github.com/thevilledev/ocaml-curve448/blob/main/docs/performance.md) |

## Verdict

These are the author's best-of-three one-second single-operation timings of the C backend through the OCaml bindings (dune release profile, OCaml's :standard C flags, compiler not named), next to `openssl speed` for OpenSSL 3.6.4 on the same machines. On an Apple M1 Pro (OCaml 5.4.1), X448 took 130 vs 133 us, Ed448 sign 64 vs 60 us and verify 203 vs 141 us. On a Ryzen AI 9 HX PRO 370 under Linux (OCaml 5.5.1), X448 took 93 vs 115 us, sign 48 vs 111 us and verify 152 vs 121 us. So X448 ranges from a tie to a 1.24x win, signing is mixed, and verification always loses.

## Use it when

- OCaml services that must speak X448 or Ed448, such as TLS 1.3 x448 key shares, HPKE DHKEM(X448) or Ed448 X.509 certificates, and want an API that matches mirage-crypto-ec instead of binding OpenSSL.
- X448 key exchange on x86-64. On a Ryzen AI 9 HX PRO 370 the C backend took 93 us against 115 us for `openssl speed` (about 1.24x). On an Apple M1 Pro the two are even (130 vs 133 us).
- Signing-heavy Ed448 workloads on x86-64. The project measured 48 us against OpenSSL's 111 us on the Ryzen, but that OpenSSL figure is unexplained (see gotchas), and on the M1 Pro OpenSSL signs faster (60 vs 64 us).
- Code that wants constant-time scalar multiplication everywhere, including verification, and C field arithmetic with machine-checked proofs (fiat-crypto) plus Valgrind-checked constant-time paths under GCC and Clang.
- Any 64-bit OCaml target where the C backend cannot build (MSVC) or no C is wanted. The pure-OCaml backend runs the same algorithms and API about 2-3x slower.

## Skip it when

- Verification-heavy workloads such as checking many Ed448 certificates or signatures. Verify is 1.44x slower than OpenSSL on the M1 Pro (203 vs 141 us) and 1.26x slower on the Ryzen (152 vs 121 us), and batch verification is not provided.
- When you are free to choose the curve. On the same machines, mirage-crypto-ec's X25519 takes 30/21 us and Ed25519 signs in 39/27 us, roughly 3-4x faster than X448/Ed448 here.
- C or C++ projects looking for a faster OpenSSL replacement. There is no C API, header install or ABI; the C code exists only to back the OCaml bindings.
- Production use that needs audited or battle-tested code. The project is about two weeks old: 11 commits, one author, 0 stars and no issues, and SECURITY.md says it is not independently audited.
- 32-bit targets, js_of_ocaml or MSVC. The C backend needs a 64-bit GCC or Clang with unsigned __int128, and the OCaml backend needs 63-bit ints.

## How it is fast

Field arithmetic mod 2^448 - 2^224 - 1 is fiat-crypto v0.1.6's formally verified unsaturated-Solinas code: eight 56-bit limbs, with products in unsigned __int128. Above that, hand-written C provides a BoringSSL-style X448 Montgomery ladder (448 constant-time swap-and-step iterations), complete HWCD extended-coordinate edwards448 formulas, and a signed radix-16 fixed-base comb over a 14x8 precomputed table of about 21 KB (112 mixed additions and 28 doublings). All of it is one translation unit, so the compiler inlines across layers, and it is called through [@@noalloc] externals to keep OCaml FFI overhead small. Verification deliberately reuses the constant-time scalar multiplications instead of a variable-time double-scalar multiplication, which is why it loses to OpenSSL there.

## Compared with alternatives

None of the catalogued signature siblings cover Curve448: ENG25519 is X25519/Ed25519 with AVX-512 IFMA, libsecp256k1 and UltrafastSecp256k1 are secp256k1 ECDSA, and the rest are post-quantum. Pick this only when a protocol requires X448 or Ed448 and you are in OCaml; if the curve is your choice, the Curve25519 options are several times faster.

## Integration

| | |
|---|---|
| **Form** | module (opam package curve448 with dune sublibraries curve448.ocaml and curve448.c; the C part is a header source-drop compiled into one stub file) |
| **Dependencies** | mirage-crypto-rng &gt;= 2.0.1, used for key generation and itself built with C stubs. fiat-crypto p448, plus code adapted from BoringSSL and tiny_sha3, is vendored in lib/c/native. |
| **Minimum toolchain** | OCaml 4.14.0+, Dune 3.6+, opam 2.0. For curve448.c, a 64-bit GCC or Clang with unsigned __int128; the constant-time checks name GCC 13.3/16.2 and Clang 18.1/22.1. MSVC builds fall back to the OCaml backend. |
| **Platforms** | The C backend builds on amd64, arm64, power, s390x and riscv (64-bit, non-MSVC). CI covers Linux only; macOS and Windows are not in CI, although the M1 Pro benchmark ran on macOS. The C code has no SIMD or runtime dispatch. |
| **Thread safety** | Documented as having no global mutable state, so the deterministic operations are safe across OCaml 5 domains (test/test_domains.ml). Key generation is only as safe as the Mirage_crypto_rng generator in use: getrandom via use_default is fine, Fortuna must not be shared. |
| **Drop-in for the baseline** | partial — keys, signatures and shared secrets are interoperable with OpenSSL 3.6.4, and a differential test agrees on all honest inputs. But it is an OCaml API mirroring mirage-crypto-ec, not OpenSSL's EVP interface, and OpenSSL rejects two small-order Ed448 key encodings that this library accepts. |

## Gotchas

- The project's figures and OpenSSL's come from different harnesses. The project uses an OCaml gettimeofday loop through the FFI; OpenSSL uses `openssl speed`, with no build flags or compiler named for either side. OpenSSL's Ryzen Ed448 sign time (111 us, nearly its 121 us verify time and almost twice its M1 sign time) is not explained, and the 2.3x signing lead depends on it.
- Small-order Ed448 public keys (four encodings) are accepted as RFC 8032 allows, and under such a key a forged signature verifies for every message. Protocols that need a signature to bind an honest key must reject those encodings themselves.
- The C stubs never release the runtime lock, so hashing a very long message for Ed448 blocks other threads in that domain. Secrets sit in ordinary OCaml strings the GC may copy, and C temporaries in the lower-level helpers are not wiped.
- The v0.1.0 tarball on opam predates the 2026-09-23 fixes. The one in PR #3 (Int_val truncation of phflag in the C stubs) could not be reached through the public API, which only passes 0 or 1.

## Known shortcomings

- New (created 2026-09-13), not on opam. Compiler/version unstated (dune default flags); the OCaml FFI harness is compared against `openssl speed`, so harnesses differ; Ed448ph not benchmarked; results against OpenSSL 3.6 are mixed.
- OCaml-only library (no C API); 2 weeks old, one author, unaudited. Mixed against OpenSSL: X448 ties on M1 (130 vs 133 µs) and is 1.24x on Ryzen; signing 7% slower on M1; verification always slower (1.26-1.44x, constant-time). The Ryzen 2.3x signing win is doubtful (OpenSSL's sign time there equals its verify time, unexplained). Now on opam (curve448 0.1.0, 2026-09-19).

## Caveats and trade-offs

Results are mixed, not a clean win: X448 is only about 2% faster on the M1 Pro (130 vs 133 us); Ed448 sign is about 7% slower than OpenSSL on the M1 Pro; Ed448 verify is always slower (1.26-1.44x, derived from page data) because the C backend is constant-time and OpenSSL uses variable-time double-scalar multiplication. The project timings go through the OCaml FFI with its own gettimeofday loop while OpenSSL uses `openssl speed`, so the harnesses differ. The project is brand new (0 stars, not on opam) with no independent review, and the C compiler/version are not stated. LICENSE.md is ISC for project code; the vendored C pieces are MIT/ISC (fiat-crypto, BoringSSL, tiny_sha3).

Verification is slower than OpenSSL by design (constant-time vs. OpenSSL's variable-time path); pure-OCaml backend is 2-4x slower than both the C backend and OpenSSL; targets Ed448/X448 rather than the far more common Ed25519/X25519

## Maintenance

Active and brand new (created 2026-09-13; v0.1.0 tagged 2026-09-18; last commit 2026-09-26), with one maintainer, 0 stars and several recent PRs marked as generated with Claude Code. Contrary to the README and the record, curve448.0.1.0 has been in opam-repository since 2026-09-19 (PR #30768), and the same author's hpke 0.3.0 depends on it. The license is ISC AND MIT, so it is copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** docs/performance.md gives first-party best-of-three timings for the C backend next to `openssl speed` (OpenSSL 3.6.4) on named CPUs (Apple M1 Pro, Ryzen AI 9 HX PRO 370). The bench code (bench/bench_curve448.ml) is public, but the C compiler and version are not stated, flags are only dune's :standard, and OpenSSL is timed by a different harness, so this is C, not A.
- **Verifier notes:** gh shows license NOASSERTION only because LICENSE.md adds a third-party table; the project code is ISC and the vendored C is MIT/ISC, so copyable is correct. Last commit is 2026-09-26 (active), 0 stars, not a fork. All page numbers match the record.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thevilledev/ocaml-curve448>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/performance.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/testing.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/LICENSE.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/dune>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/bench/dune>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/bench/bench_curve448.ml>
- **Sources the enricher read:**
  - <https://github.com/thevilledev/ocaml-curve448>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/README.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/performance.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/backends.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/design.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/usage.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/compatibility.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/interoperability.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/docs/testing.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/SECURITY.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/CHANGES.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/LICENSE.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/curve448.opam>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/dune-project>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/dune>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/native/README.md>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/native/curve448.h>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/native/curve448_stubs.c>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/native/edwards448.h>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/lib/c/native/field448.h>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/bench/bench_curve448.ml>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/bench/timing.ml>
  - <https://github.com/thevilledev/ocaml-curve448/blob/main/bench/dune>
  - <https://github.com/thevilledev/ocaml-curve448/commits/main>
  - <https://github.com/thevilledev/ocaml-curve448/pulls?q=is%3Apr>
  - <https://github.com/thevilledev/ocaml-curve448/pull/2>
  - <https://github.com/thevilledev/ocaml-curve448/pull/3>
  - <https://github.com/thevilledev/ocaml-curve448/issues>
  - <https://github.com/thevilledev/ocaml-curve448/releases>
  - <https://github.com/ocaml/opam-repository/tree/master/packages/curve448>
  - <https://github.com/ocaml/opam-repository/pull/30768>
  - <https://github.com/ocaml/opam-repository/pull/30813>
  - <https://hn.algolia.com/api/v1/search?query=ocaml-curve448>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/thevilledev/ocaml-curve448`) · [data/wave7/enrich/raw/github_com_thevilledev_ocaml_curve448.json](../../../data/wave7/enrich/raw/github_com_thevilledev_ocaml_curve448.json) (enrichment confidence 0.8)

</details>
