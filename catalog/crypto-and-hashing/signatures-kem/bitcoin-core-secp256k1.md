# libsecp256k1 (bitcoin-core/secp256k1)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Bitcoin Core's secp256k1-only C signature library; ECDSA verification 2.5-5.5x faster than the 2015-era OpenSSL it replaced.

| | |
|---|---|
| **Beats** | OpenSSL (ECDSA_verify / o2i_ECPublicKey on secp256k1) |
| **Claimed result** | ECDSA verify on secp256k1 (compressed-pubkey parse + DER sig parse + verify), libsecp256k1 at Bitcoin Core v30.0 (v0.7.0, commit b9313c6) vs OpenSSL 3.5.0. Ryzen 9 5950X (Wuille): 8.5x (stated). Author's arm64 with gcc 14.2.0: '&gt;8x' stated, about 8.3x read from the chart. Ryzen 9 3950X with gcc 12.2.0 (independent issue #2): about 9.0x read from the chart. Historical baseline, libsecp at Core v0.12 (2015) vs OpenSSL 1.1.1: about 4.3x (arm64), 5.4x (5950X) and 4.8x (3950X), read from the charts. The original PR #6954 claim was 2.5-5.5x. Chart readings are pixel measurements, accurate to about ±2-3%. |
| **Workload** | ECDSA signature verification (parse compressed pubkey, parse DER signature, verify) on the secp256k1 curve, benchmarked via dlopen loading of historical OpenSSL and libsecp256k1 release versions on the same binary |
| **Metric** | latency |
| **Hardware** | Author: unnamed arm64 machine (he says 3 machines gave very similar results). Wuille: AMD Ryzen 9 5950X. Independent: AMD Ryzen 9 3950X, 32GB RAM, Debian x86_64. |
| **Compiler and flags** | Compiler: gcc 14.2.0 for the author's arm64 run and gcc 12.2.0 for the independent 3950X run. Wuille's 5950X run does not state a compiler. All builds use defaults with no custom flags. libsecp256k1 was built with ./autogen.sh && ./configure --enable-static=no --enable-benchmark=no --enable-tests=no --enable-exhaustive-tests=no && make, which gives autoconf '-g -O2' plus libsecp's own -O2 (checked in the v0.7.0 configure.ac). OpenSSL was built with ./config shared && make, whose Linux release default is -O3 (checked in 3.5.0 Configurations/10-main.conf). The harness itself is built with plain cc. These are not Bitcoin Core's own build flags. |
| **Adoption** | 2.5k stars; consensus-critical ECDSA/Schnorr library in Bitcoin Core since 2015, also used by Ethereum, libp2p, and most cryptocurrency software |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/bitcoin-core/secp256k1) · [benchmark](https://delvingbitcoin.org/t/comparing-the-performance-of-ecdsa-signature-validation-in-openssl-vs-libsecp256k1-over-the-last-decade/2087) |

## Verdict

Bitcoin Core's own PR #6954 (Nov 2015) reports ECDSA signature validation 2.5-5.5x faster than the OpenSSL it replaced, and the v0.12.0 release notes say over 5x on x86_64; OpenSSL version, compiler and CPU are not stated. Whole-node runs on one Xeon E31245 took IBD from about 7h37m to 3h48m (dbcache=3000), and a separate reindex fell from 8.0 h to 3.2 h. For a recent cross-check I derived ratios from UltrafastSecp256k1's 2026-09-07 benchmark JSON: on an i5-14400F with turbo off, GCC 14.2 -O3 -march=native, libsecp256k1 (Dec 2025 master) did verify in 41.5 us vs 400.3 us for system OpenSSL (version unrecorded; about 9.6x), sign in 29.4 vs 419.1 us (about 14x) and public-key generation in 21.1 vs 394.4 us (about 19x).

## Use it when

- Verifying secp256k1 ECDSA or Schnorr signatures in bulk (block or transaction validation, indexers, exchanges, wallets). Bitcoin Core's switch made raw verification 2.5-5.5x faster and cut a full reindex from 8.0 h to 3.2 h.
- Signing or deriving keys on shared or hostile hardware. Signing and key generation are constant-time with constant memory access, use RFC6979 deterministic nonces and support optional context blinding. That was Bitcoin Core's reason for moving signing off OpenSSL in v0.10.
- Embedded or allocation-free builds. It needs only C89 with uint64_t, does no runtime heap allocation (preallocated and static contexts exist) and uses no floating point. Table sizes can be configured (signing table 2/22/86 KiB, verify window 2-24).
- Bitcoin-protocol features that must match other implementations exactly: strict DER, lower-S only, x-only keys, MuSig2, BIP-324 ElligatorSwift and BIP-352 Silent Payments, all maintained by the same reviewers.

## Skip it when

- Any curve other than secp256k1 (P-256, Ed25519, ...), or anything beyond signatures, ECDH and key tweaks, such as TLS, X.509 or generic EC math. OpenSSL is still needed for those.
- Large-batch verification where you want a batch API. There is no public batch-verify call (issue #1087 is still open); the multi-scalar Strauss/Pippenger code is internal only.
- Signatures from systems that emit high-S or loosely encoded DER. Verify rejects high-S, so you must normalize first (which accepts malleable signatures) or copy the unsupported contrib/lax_der_parsing.c into your code.
- Tight flash or RAM budgets with default settings. The verify tables are about 1 MiB of static data plus the 86 KiB signing table. Shrinking ECMULT_WINDOW_SIZE or ECMULT_GEN_KB costs speed.
- Cases where the published speedup must reflect current OpenSSL on your CPU. The only first-party OpenSSL comparison dates from 2015 and covers verification only; the repo's in-tree OpenSSL benchmark was removed in 2021 (PR #983).

## How it is fast

Verification computes a\*P + b\*G in one pass using Strauss/Shamir interleaving over wNAF digits. It uses the curve's GLV endomorphism to split P's scalar into two \~128-bit halves, and reads multiples of G from a large static precomputed table (window 15 by default: two 512 KiB tables). Field elements use 5x52-bit limbs with lazy carries and __int128 multiplies, and inversions use a variant of Bernstein-Yang safegcd. The ECDSA r check runs in Jacobian coordinates with no inversion, and the subgroup check is skipped because the cofactor is 1. Signing and key generation use a constant-time signed-digit multi-comb (Hamburg, ePrint 2012/309) over an 86 KiB table with scalar blinding. There is no heap allocation and no per-curve dispatch.

## Compared with alternatives

Pick it over UltrafastSecp256k1, the only same-curve sibling, when you want the reviewed implementation that Bitcoin Core deploys. Ultra's own benchmark shows only a 1.1-1.5x micro-benchmark gain over libsecp256k1 (Ultra built with LTO, libsecp256k1 without) and about 1% in ConnectBlock; it also had correctness fixes in Sep 2026 and was Concept-NACKed by Bitcoin Core. ENG25519 (Curve25519, AVX-512 IFMA) and the post-quantum siblings only matter if you can change the signature scheme.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Autotools, or CMake 3.22+, which builds shared by default); can also be vendored as a git subtree like Bitcoin Core does, or embedded via the secp256k1_objs CMake object library |
| **Dependencies** | none at runtime; the build needs Autotools or CMake 3.22+ |
| **Minimum toolchain** | C89/C90 compiler with uint64_t. The fast 64-bit path needs __int128, or MSVC 128-bit multiply on x86_64/arm64. Clang-cl is recommended on Windows. |
| **Platforms** | Portable C. 64-bit targets use the 5x52 field and 4x64 scalar code; 32-bit targets use 10x26 and 8x32. Optional x86_64 scalar assembly (on by default where detected) and experimental ARM32 field assembly. Big-endian s390x has run in CI. |
| **Thread safety** | Documented in secp256k1.h: a created context can be used from many threads at once. Calls that take a non-const context (destroy, randomize, setting callbacks) need exclusive access, so randomize once at creation or guard it with a read-write lock. |
| **Drop-in for the baseline** | partial — it performs the same secp256k1 ECDSA sign/verify/keygen math, but through its own C API (context object, opaque 64-byte key and signature structs, caller-hashed 32-byte messages), with strict DER parsing and lower-S-only verification. Code that calls OpenSSL ECDSA_do_verify or EVP must be rewritten. |

## Gotchas

- secp256k1_ecdsa_verify rejects valid high-S signatures by design. secp256k1_ecdsa_signature_parse_der is strict, and lax BER-style parsing exists only as a copy-in contrib snippet with no stability promise.
- When a caller passes an illegal argument, the default callback prints to stderr and calls abort(). Long-running services should install their own illegal/error callbacks, either per context or by link-time replacement.
- Call secp256k1_context_randomize before signing or key generation to get side-channel blinding. secp256k1_context_static cannot sign, the ECDH module gets no blinding, and creating a context per operation is expensive.
- Constant-time behaviour depends on the compiler. Releases 0.3.1 and 0.3.2 were security fixes for timing leaks introduced by Clang &gt;=14 and GCC 13.1. s390x has a known non-constant-time scalar comparison (issue #784). With Clang, the x86_64 assembly makes scalar_mul about 25% slower than the plain C build (issue #1682).

## Known shortcomings

- Only numbers are first-party and old (2015): Bitcoin Core PR #6954 reports signature validation 2.5-5.5x faster than OpenSSL, and v0.12.0 notes &gt;5x on x86-64; verification only, no compiler or flags. secp256k1 curve only (Bitcoin-specific), not a general ECDSA library.
- The in-repo OpenSSL benchmark was removed in 2021 (PR #983), so nothing current is in-tree; a modern ratio exists only in a competitor's (UltrafastSecp256k1) benchmark JSON (verify \~9.6x, sign \~14x, keygen \~19x vs an unrecorded OpenSSL version). Not a drop-in: own API, 32-byte caller-hashed messages, strict DER, low-S only; no public batch verification (#1087). Constant-time behaviour depends on the compiler (0.3.1/0.3.2 fixed Clang &gt;= 14 / GCC 13 leaks; s390x non-CT #784). Pre-1.0 with repeated ABI breaks; default tables \~1 MiB static.
- OpenSSL's secp256k1 path is unoptimized and uses an old API, so the \~8-9x verify ratio reflects a weak baseline for this curve.

## Caveats and trade-offs

Speedup figures are first-party, from Bitcoin Core developers (who also wrote libsecp256k1), in a 2015 PR and in release notes. They have no published benchmark harness, compiler or flags, and they compare against 2015-era OpenSSL, not a current OpenSSL. Figures cover verification only. Signing moved to libsecp256k1 in v0.10.0 mainly for constant-time and side-channel reasons, not measured speed. The repo's bench binaries (README Benchmark section) time libsecp256k1 alone and do not compare against OpenSSL. The IBD/reindex timings are whole-node measurements that include non-crypto work. [retier] The two headline runs (&gt;8x and 8.5x) are first-party: both are listed in libsecp256k1 SECURITY.md. The only independent run is a GitHub issue with a chart and no stated ratio. OpenSSL's secp256k1 path is not specially optimized (the post notes P-256 is heavily optimized, and OpenSSL PR #26097 aims to speed up secp256k1), so this comparison does not show OpenSSL is slow in general. The harness uses the deprecated EC_KEY/o2i_ECPublicKey/ECDSA_verify API. Each run times the 5000 signatures once by default; Wuille used 500000 iterations because of run-to-run variance. OpenSSL 0.9.8h and 1.0.0 crash on arm64 and were skipped. Old libsecp versions were built with modern compilers, which biases the history (Wuille). Arch-dependent: bc-22.0 safegcd gave about 30% on arm64, -3.6% on the 5950X and about 16% on the 3950X, and bc-27.0 (x86_64 asm removal) gave +8% on the 5950X. The harness repo has no license. The archive file is on branch 'master', not 'main'.

Narrow scope (secp256k1 only) vs. OpenSSL's general-purpose EC support; requires a separate dependency instead of reusing an existing OpenSSL install

## Maintenance

Actively maintained: v0.8.0 shipped 2026-08-03, commits continue through 2026-09-25, and release tags are GPG-signed. MIT-licensed and easy to vendor. Still pre-1.0, and releases 0.3.0, 0.6.0, 0.7.0 and 0.8.0 each broke or trimmed the ABI, so pin a version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded from D. Bitcoin Core PR #6954, which switched validation from OpenSSL to libsecp256k1, gives first-party numbers: signature validation is 2.5-5.5x faster. The v0.12.0 release notes say validation is over 5x faster on x86_64, and reindex/new-block validation takes less than half the time. No compiler, flags or benchmark harness is stated for the micro figures, so this cannot be A or B.
- **Retiered** C to A: Upgraded from C. Source is Delving Bitcoin topic 2087 (Nov 2025) by Sebastian Falbesoner (theStack). It uses a public harness, github.com/theStack/secp256k1-plugbench. build_libs.sh pins the exact libsecp256k1 commits used in Bitcoin Core v0.12 through v30.0 and the OpenSSL tags 0.9.8h, 1.0.0, 1.1.1, 3.0.0, 3.1.0, 3.3.0 and 3.5.0, all as default shared builds. secp-plugbench.c dlopens each .so and times, with CLOCK_PROCESS_CPUTIME_ID, pubkey parse + DER signature parse + ECDSA verify over 5000 signatures made with libsecp256k1. The OpenSSL path uses EC_GROUP_precompute_mult. Three runs have results. (1) The author on an arm64 machine with gcc 14.2.0 reports &gt;8x (first-party). (2) Pieter Wuille on a Ryzen 5950X with 500000 iterations reports 8.5x (first-party; compiler not stated). (3) Bayernatoor, an independent third party with 0 commits in bitcoin-core/secp256k1, reproduced it in plugbench issue #2 on an AMD Ryzen 9 3950X with gcc 12.2.0 on Debian x86_64 (chart only, about 9.0x). Falbesoner and Wuille are both listed in secp256k1 SECURITY.md (maintainer keys), so they are first-party. The A criteria are met: public code, a stated compiler, default flags fixed by the public build script, and a stated CPU. Run 3 meets all of them and is independent. Run 1 lacks only the CPU model.
- **Verifier notes:** The record said no numbers existed, but PR #6954 and the v0.12.0 release notes give quantified wins over OpenSSL, so the tier goes D to C and the verdict is confirm. Metadata checked via gh: MIT license, not a fork, not archived, 2,484 stars, last commit 2026-09-25, active; all match the record.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** bitcoin/bitcoin PR #6954 (2015): ECDSA validation 2.5-5.5x faster than OpenSSL.; secp256k1-plugbench (public harness, default builds): independent run on Ryzen 9 3950X, GCC 12.2 \~9.0x ECDSA verify vs OpenSSL 3.5.0 (secp256k1 v0.7.0); maintainers' runs 8.3x (arm64, GCC 14.2) and 8.5x (5950X).
- **Pages the verifier opened:**
  - <https://github.com/bitcoin-core/secp256k1>
  - <https://github.com/bitcoin-core/secp256k1/commits>
  - <https://raw.githubusercontent.com/bitcoin-core/secp256k1/master/README.md>
  - <https://raw.githubusercontent.com/bitcoin-core/secp256k1/master/src/bench.c>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.12.0/doc/release-notes.md>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.10.0/doc/release-notes.md>
  - <https://github.com/bitcoin/bitcoin/pull/6954>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.12.0/src/secp256k1/src/bench_verify.c>
- **Sources the enricher read:**
  - <https://github.com/bitcoin-core/secp256k1>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/README.md>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1.h>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/CHANGELOG.md>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/SECURITY.md>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/CMakeLists.txt>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/src/ecmult_gen_impl.h>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/src/ecmult_impl.h>
  - <https://github.com/bitcoin-core/secp256k1/blob/master/contrib/lax_der_parsing.h>
  - <https://github.com/bitcoin-core/secp256k1/issues/736>
  - <https://github.com/bitcoin-core/secp256k1/pull/983>
  - <https://github.com/bitcoin-core/secp256k1/issues/1682>
  - <https://github.com/bitcoin-core/secp256k1/issues/1700>
  - <https://github.com/bitcoin-core/secp256k1/issues/784>
  - <https://github.com/bitcoin-core/secp256k1/issues/1769>
  - <https://github.com/bitcoin-core/secp256k1/issues?q=batch+verification>
  - <https://github.com/bitcoin-core/secp256k1/issues?q=label%3Abug+is%3Aopen>
  - <https://github.com/bitcoin-core/secp256k1/issues?q=label%3Aside-channel+is%3Aopen>
  - <https://github.com/bitcoin-core/secp256k1/issues?q=label%3Aperformance+is%3Aopen>
  - <https://github.com/bitcoin/bitcoin/pull/6954>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.12.0/doc/release-notes.md>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.10.0/doc/release-notes.md>
  - <https://raw.githubusercontent.com/bitcoin/bitcoin/v0.12.0/src/secp256k1/src/bench_verify.c>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/docs/bench_unified_2026-09-07_gcc14_x86-64.json>
  - <https://hn.algolia.com/api/v1/search?query=libsecp256k1%20openssl>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/bitcoin-core/secp256k1`) · [data/wave7/enrich/raw/github_com_bitcoin_core_secp256k1.json](../../../data/wave7/enrich/raw/github_com_bitcoin_core_secp256k1.json) (enrichment confidence 0.8)

</details>
