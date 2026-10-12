# fiat-crypto (generated Curve25519 field arithmetic in BoringSSL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Coq (generates C, Rust, Go, Java, Zig, Bedrock2, x86-64 asm)` · `MIT OR Apache-2.0 OR BSD-1-Clause` · 🟢 active

> Coq-proved generator of finite-field arithmetic in C, Rust, Go and Zig; matches hand-written Curve25519 field code in BoringSSL, not faster.

| | |
|---|---|
| **Beats** | BoringSSL's previous curve25519 code: hand-written x86_64 x25519 assembly (884086e) and the earlier C field arithmetic on master (b2c312d) |
| **Claimed result** | No field-level speedup: parity or slightly slower. BoringSSL commit 884086e ('Remove x86_64 x25519 assembly', dated 2018-02-01): x86_64 assembly 15095.3 ops/sec base-point and 15094.0 ops/sec arbitrary-point multiplication versus fiat64 38817.1 and 13905.1 ops/sec; the message says 'The assembly is still about 9% faster than fiat64' and that fiat64 'gets to use the Ed25519 tables for the base point multiplication, so overall it is actually faster to disable the assembly' '(At the cost of touching a 30kB table.)'. The base-point win (about 2.6x, derived from page data) comes from that table-based algorithm, not from faster field arithmetic; one base-point plus one arbitrary-point multiplication works out to about 7547 ops/sec for the assembly versus about 10237 ops/sec for fiat64 (derived from page data; the commit gives no combined figure). Commit b2c312d ('curve25519: fiat-crypto field arithmetic.', dated 2017-11-03, 32-bit build): this branch 3546.5 / 3530.2 / 3014.5 ops/sec arbitrary-point and 11061.4 / 11226.2 / 8599.2 base-point versus master 3549.0 / 3551.9 / 3562.5 and 11177.1 / 11152.2 / 11306.7, i.e. parity; Ed25519 verify 2921.1 / 2919.0 / 2853.6 versus master 3055.7 / 3003.5 / 3058.6 ops/sec, about 4% slower (derived from page data); Ed25519 signing at parity (10759.3 / 10855.4 / 10807.0 versus 10840.8 / 10762.5 / 10863.2). |
| **Workload** | bssl speed -filter 25519 in BoringSSL: Curve25519 base-point multiplication, arbitrary-point multiplication, Ed25519 sign / verify ops/sec, with fiat-crypto generated 64-bit (fiat64) and 32-bit field code swapped in. |
| **Metric** | throughput |
| **Hardware** | Commit b2c312d: 'Google Cloud's unidentified Intel Xeon with AVX2' (two of the master runs are pasted from a shell prompt 'andreser@linux-andreser', so it is not certain every run shared one machine); commit 884086e states no CPU. |
| **Compiler and flags** | Commit b2c312d: CC=clang CXX=clang++ cmake -GNinja -DCMAKE_TOOLCHAIN_FILE=../util/32-bit-toolchain.cmake -DCMAKE_BUILD_TYPE=Release, then ninja and ./tool/bssl speed -filter 25519 (a 32-bit x86 build; compiler version not stated). Commit 884086e states no toolchain or flags. |
| **Adoption** | 844 stars; generated code adopted in BoringSSL (commits b2c312d, 884086e) and, per Linux commit 0ed42a6f431e, the kernel's 32-bit Curve25519 |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/mit-plv/fiat-crypto) · [benchmark](https://github.com/google/boringssl/commit/884086e0e28aad7efe418d9ed7459912e6683fbb) |

## Verdict

BoringSSL's bssl speed -filter 25519 runs show parity, not a speedup: in b2c312d (clang, 32-bit toolchain, Release, an unnamed Google Cloud Xeon with AVX2) the 32-bit fiat field code matched the previous C code on arbitrary-point and base-point multiplication and Ed25519 signing, with Ed25519 verify about 4% slower, and in 884086e (no CPU or compiler stated) fiat64 was about 9% slower than the old x86_64 assembly on arbitrary-point multiplication and won base-point multiplication only by using the Ed25519 table.

## Use it when

- You maintain a crypto library and want Curve25519, P-256, P-384, P-521, secp256k1 or Poly1305 field arithmetic with a machine-checked correctness proof at the speed of good hand-written C.
- You need constant-time field code for an unusual prime (the generator covers 80+ primes and arbitrary Solinas or Montgomery-friendly moduli) rather than writing and auditing your own.
- Portable 32-bit targets: the 10-limb 32-bit Curve25519 code is what the Linux kernel's generic 32-bit Curve25519 uses.
- Rust projects that already depend on it indirectly (curve25519-dalek tests the fiat backend; the crate has about 151 million crates.io downloads) and want the formally verified backend selected.

## Skip it when

- You want a faster X25519 or Ed25519 than BoringSSL or OpenSSL: the only third-party runs show parity with BoringSSL's C and the old x86_64 assembly about 9% faster on arbitrary-point multiplication.
- You need a complete protocol API (keygen, sign, verify, ECDH): Fiat stops at the field, so ladders, tables, encoding and side-channel hygiene of the rest are yours.
- MSVC or other compilers without unsigned __int128 for the 64-bit unsaturated files; use the 32-bit variants there.
- Regenerating code for new primes on a laptop: the toolchain needs Coq 9.0+ and OCaml 4.08+, a full build takes over an hour, and large primes can need a 1 GB stack and an hour per run.
- The Java backend: the README marks it unmaintained and known buggy (issue #707).

## How it is fast

It does not use a new algorithm; speed comes from emitting the same limb-scheduled, fully unrolled, branch-free multiply-and-reduce code an expert would write by hand (unsaturated Solinas reduction for 2^255-19, Montgomery word-by-word reduction for generic primes), with proven bounds that let it drop unnecessary carries. A value barrier (empty asm) keeps compilers from turning selectznz back into branches. Since 2023 BoringSSL also ships x86-64 ADX assembly that CryptOpt compiles from Fiat templates and checks with the translation validator in the Fiat repository.

## Compared with alternatives

Pick Fiat when correctness proofs and coverage of many primes matter more than peak speed; ENG25519 (AVX-512 IFMA) and the amd64-64-24k Ed25519 code are faster on their target CPUs but carry no machine-checked proofs, and libsecp256k1 remains the complete, faster choice for secp256k1 signing rather than Fiat's bare secp256k1 field code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the generated C (stdint.h only); generator needs Coq 9.0+ with Rocq stdlib 9.1+, OCaml 4.08+ and jq; Rust users take the fiat-crypto crate |
| **Minimum toolchain** | C99-style C with GCC or clang for the 64-bit files (unsigned __int128 and __extension__); 32-bit files are plain C; Rust crate fiat-crypto 0.3.0 states no rust-version |
| **Platforms** | any two's-complement target (the files #error otherwise); 64-bit unsaturated code needs a compiler with 128-bit integers; the CryptOpt ADX assembly in BoringSSL is x86-64 with BMI2/ADX only |
| **Thread safety** | Stateless pure functions on caller-provided limb arrays (no globals in fiat-c/src/curve25519_64.c), so safe to call concurrently on distinct outputs; not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Proof scope: only the Bedrock2 backend has a proof that the emitted AST matches the internal semantics; the C, Rust, Go and Zig printers are unproven, the README says integer-size casts are not verified against what gcc or clang select, and it gives no quality guarantee for generated code.
- Inputs must respect the typed bounds (loose versus tight field elements, e.g. call carry or carry_mul before feeding an add result to to_bytes); violating them voids the proofs and can overflow limbs silently.
- The BoringSSL base-point speedup in commit 884086e (38817.1 versus 15095.3 ops/sec) comes from switching to the Ed25519 precomputed 30 kB table, not from faster field arithmetic; on arbitrary-point multiplication fiat64 was slower (13905.1 versus 15094.0 ops/sec).
- Newer speed claims are for CryptOpt assembly, not the C: BoringSSL 43f8891 (2023, by fiat's lead author, reviewed by BoringSSL) reports +31.2% on Curve25519 arbitrary-point multiplication (28263.1 ops/sec) with no baseline row, CPU or compiler, and 20c9406 reports +63.5% P-256 ECDH on Cascade Lake but only under -DOPENSSL_SMALL=1 (against the small-footprint path, not nistz256), with no difference on Haswell.

## Known shortcomings

- Not faster than its baseline: BoringSSL commits 884086e and b2c312d show parity with BoringSSL's C, and the x86_64 assembly is still about 9% faster at arbitrary-point multiplication; the base-point win comes from switching to Ed25519 tables, not faster field code. No CPU model in either commit; the '7547 to 10237 ops/sec' figure is derived, not in commit 884086e; b2c312d was a 32-bit toolchain build, and two master runs appear to be the fiat author's own data. S&P 2019 paper unreachable. Lead: kbench9000 shows fiat64 about 1.12x faster than donna64 (snippet only).
- Enricher: parity with BoringSSL's C confirmed, not faster; the base-point win comes from the Ed25519 table. The README says only the Bedrock2 backend is proven and gives no quality guarantee for generated code; the Java backend is known buggy (#707); 64-bit C needs __int128 (no MSVC). Newer first-party evidence is CryptOpt assembly from Fiat templates in BoringSSL (43f8891 Curve25519 +31.2% with no baseline row or CPU; 20c9406 P-256 ECDH +63.5% on Cascade Lake only with -DOPENSSL_SMALL=1, no gain on Haswell); CryptOpt is catalogued separately in wave 13.

## Caveats and trade-offs

Evidence supports 'as fast as hand-written C, correct by construction', not 'faster': in 884086e the hand-written x86_64 assembly is still about 9% faster on arbitrary-point multiplication, and fiat64 wins base-point multiplication only by switching to the Ed25519 precomputed tables (a 30kB table), an algorithmic change rather than faster field code; in b2c312d the 32-bit fiat field code is at parity with master's C code (Ed25519 verify about 4% slower, derived from page data). Neither commit names a CPU model (tier B, not A); b2c312d was built with BoringSSL's 32-bit toolchain file, so it says nothing about 64-bit fiat code, and two of its master runs carry a shell prompt from the machine 'linux-andreser' (Andres Erbsen, fiat-crypto's lead author), so part of that data may be first-party and possibly from a different machine. Both measurements date from 2017-2018. The IEEE S&P 2019 paper (Erbsen et al.) and Jason Gross' thesis were not reachable (dspace.mit.edu, wireguard.com, ieee-security.org, adam.chlipala.net, moderncrypto.org, lists.zx2c4.com blocked here). Search snippets (snippet only) of Jason Donenfeld's 2018 kbench9000 runs report fiat64 at about 108,984 cycles per Curve25519 call against hacl64 about 109,782 and donna64 about 121,790 on a Skylake laptop, and in a later run on a Xeon E3-1505M v5 fiat64 about 144,106 against donna64 about 160,942 and hacl64 about 140,902, with the precomp_adx/precomp_bmi2 assembly fastest at roughly 117,000-121,000; fiat32 was roughly twice as slow as the 64-bit versions. Linux kernel commit 0ed42a6f431e ('crypto: curve25519 - generic C library implementations') takes the 32-bit Fiat and 64-bit HACL\* code as 'the fastest available C implementations' without numbers. The repo README, boringssl_notes.md and folkwisdom.md contain no benchmark tables. Not OpenSSL itself: the baseline is BoringSSL's earlier curve25519 code. The repo now also ships fiat-amd64 (generated assembly), which was not evaluated here.

Coq-verified synthesis of word-by-word field arithmetic (Curve25519 5x51-bit and 10x25.5-bit limbs, P-256, secp256k1, 80+ primes); the product is generated straight-line C (fiat-c), Rust, Go, Java, Zig, Bedrock2 and some amd64 asm, with proofs of the arithmetic but not of the C-to-machine step. Only field arithmetic: scalar-multiplication ladders, tables and protocols come from the host library. Generated code is large and unidiomatic.

## Maintenance

Actively maintained (Zig backend rewrite merged 2026-10-09) under a choice of MIT, Apache-2.0 or BSD-1-Clause; the generated C files are self-contained and easy to vendor, and BoringSSL, the Linux kernel's 32-bit Curve25519 and curve25519-dalek's fiat backend already do.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Both BoringSSL commits time fiat-crypto field code against BoringSSL's previous curve25519 code with the public 'bssl speed -filter 25519' tool; 884086e is an independent measurement by BoringSSL's maintainer and b2c312d states clang, CMake Release and a 32-bit toolchain, but neither names a CPU model (b2c312d says 'Google Cloud's unidentified Intel Xeon with AVX2', 884086e names no hardware or compiler), so B and not A.
- **Verifier notes:** Commit numbers match, but the record's 'commit's own combined figure 7547 to 10237 ops/sec' is not in the commit; it is a harmonic combination of the two rows and is now labelled derived. Keep with shortcoming 'not faster than the hand-written baseline (parity in C, about 9% slower than x86_64 asm on arbitrary-point; base-point win from a table algorithm)'; b2c312d was a 32-bit build and partly run on the fiat-crypto lead author's machine. Lead: Donenfeld's kbench9000 (git.zx2c4.com, not on GitHub) shows fiat64 about 1.12x faster than curve25519-donna64 (derived, snippet only); the S&P 2019 paper could lift this entry if a reachable copy turns up.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 7 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/google/boringssl/commit/884086e0e28aad7efe418d9ed7459912e6683fbb>
  - <https://github.com/google/boringssl/commit/884086e0e28aad7efe418d9ed7459912e6683fbb.patch>
  - <https://github.com/google/boringssl/commit/b2c312d.patch>
  - <https://github.com/mit-plv/fiat-crypto>
  - <https://github.com/mit-plv/fiat-crypto/commits>
  - <https://github.com/torvalds/linux/commit/0ed42a6f431e>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mit-plv/fiat-crypto/HEAD/README.md>
  - <https://raw.githubusercontent.com/mit-plv/fiat-crypto/HEAD/fiat-c/src/curve25519_64.c>
  - <https://github.com/mit-plv/fiat-crypto/commits>
  - <https://github.com/mit-plv/fiat-crypto/issues?q=is%3Aissue%20label%3Abug>
  - <https://crates.io/api/v1/crates/fiat-crypto>
  - <https://github.com/google/boringssl/commit/884086e0e28aad7efe418d9ed7459912e6683fbb>
  - <https://github.com/google/boringssl/commit/b2c312d>
  - <https://github.com/google/boringssl/commits/main/third_party/fiat/asm>
  - <https://github.com/google/boringssl/commit/43f8891>
  - <https://github.com/google/boringssl/commit/20c9406>
  - <https://raw.githubusercontent.com/google/boringssl/HEAD/third_party/fiat/asm/fiat_curve25519_adx_mul.S>
  - <https://raw.githubusercontent.com/google/boringssl/HEAD/third_party/fiat/README.md>
  - <https://github.com/torvalds/linux/commit/0ed42a6f431e>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mit-plv/fiat-crypto`) · [data/wave7/enrich/raw/github_com_mit_plv_fiat_crypto.json](../../../data/wave7/enrich/raw/github_com_mit_plv_fiat_crypto.json) (enrichment confidence 0.6)

</details>
