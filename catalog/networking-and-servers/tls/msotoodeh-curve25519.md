# curve25519 (mehdi sotoodeh / "Mehdi")

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> C/x86-64-asm X25519 and Ed25519 library; precomputed fixed-base tables give 2.8x faster Ed25519 keygen than OpenSSL 1.1.1.

| | |
|---|---|
| **Beats** | OpenSSL 1.1.1 EVP_PKEY API: EVP_PKEY_ED25519 (CreateKeyPair, SignMessage via EVP_DigestSign) and EVP_PKEY_X25519 (CalculatePublicKey, CreateSharedKey via EVP_PKEY_derive) |
| **Claimed result** | README OpenSSL comparison (HP EliteBook 755 G5, Ubuntu 18.04.2, OpenSSL 1.1.1; TSC cycles, the '@3.4GHz' usec figures are a fixed constant in the test code): CreateKeyPair 74,822 vs 210,738 cycles (ratio 2.817, delta 64.50%); CalculatePublicKey 316,096 vs 208,714 (ratio 0.660, Mehdi 51.45% slower); CreateSharedKey 270,930 vs 442,750 (ratio 1.634, delta 38.81%); SignMessage 78,628 vs 425,656 (ratio 5.414, delta 81.53%). The OpenSSL timed region also includes EVP_PKEY creation from the raw secret (plus peer-key and context setup for CreateSharedKey), while the Mehdi SignMessage call receives a precomputed 64-byte private+public key, so the CreateSharedKey and SignMessage margins are not like-for-like. Separately, X25519 base-point multiplication is 5.33x to 19.59x faster than curve25519-donna across the README platform/compiler table (README text says 6.2 to 19.5); fastest 43,229 cycles (W7-64/MASM V1.1, Intel Core i7-2670QM). |
| **Workload** | test/openssl_test.c: Ed25519 key-pair creation, X25519 public-key derivation, X25519 shared-secret computation and Ed25519 signing of a 32-byte message; min of 100 runs per operation timed with rdtsc (TSC ticks, minus rdtsc overhead), comparing the x86-64 assembly library build ('make asm && make openssl') against OpenSSL's EVP_PKEY API; outputs are memcmp-checked for equality |
| **Metric** | latency |
| **Hardware** | OpenSSL comparison: HP EliteBook 755 G5 laptop, x86_64 (CPU model not stated), Ubuntu 18.04.2; donna comparison and internal cycle tables: Intel Core i7-2670QM |
| **Compiler and flags** | gcc via Rules.mk (version not stated for the OpenSSL run); source/asm64/Makefile compiles the C glue with -O2 -m64 -Wall -Wno-format -DUSE_ASM_LIB and assembles amd64.gnu/\*.s with 'as --64'; test objects, including openssl_test.c, use -O2; RELEASE=1 adds -DNDEBUG, otherwise -g -D_DEBUG. The portable-C library (source/Makefile) also uses -O2. Donna table: VS2010/MASM, GNU assembler 2.25 (mingw) and gcc 4.5.3 (Cygwin-32). |
| **Adoption** | 165 stars |
| **Last commit** | 2020-04-20 |
| **Links** | [repository](https://github.com/msotoodeh/curve25519) · [benchmark](https://github.com/msotoodeh/curve25519/blob/master/README.md) |

## Verdict

In a June 2019 run of test/openssl_test.c (asm build, gcc -O2, OpenSSL 1.1.1, HP EliteBook 755 G5, Ubuntu 18.04.2, CPU model not given; minimum of 100 TSC reads), Ed25519 key-pair creation took 74,822 vs 210,738 TSC ticks (2.8x), the only like-for-like row. The 5.4x sign and 1.6x shared-key rows count OpenSSL's EVP_PKEY construction, which recomputes the public key, inside the timed loop, and the 0.66x public-key row timed the Montgomery-ladder function instead of the faster _fast comb path; the separate 5.3x-19.6x figures are against portable-C curve25519-donna on an i7-2670QM.

## Use it when

- Ed25519 keygen- or signing-heavy services on x86-64: 74,822 TSC ticks per key pair vs 210,738 for OpenSSL 1.1.1, and 78,628 per 32-byte-message signature (roughly 2.7x after removing OpenSSL's in-loop key rebuild; estimate).
- Verifying many signatures from the same few public keys: call ed25519_Verify_Init once per key and reuse the context (about 103-111K cycles per check on an i7-2670QM in the README tables).
- Generating ephemeral X25519 key pairs, provided you call curve25519_dh_CalculatePublicKey_fast (Edwards comb, about 43-48K cycles on i7-2670QM), not the plain ladder function.
- Embedding a dependency-free MIT C implementation where you control the build: about 16 C sources/headers plus 7 x86-64 asm files.

## Skip it when

- X25519 shared-secret (variable-base) throughput: its ladder took 270,930 TSC ticks; subtracting OpenSSL's in-loop key construction (\~208,714) from OpenSSL's 442,750 suggests OpenSSL 1.1.1's derive alone was faster (rough estimate).
- When you need cache-timing-safe code without extra setup: fixed-base multiplies index the \~24 KB table directly by secret scalar bits; protection depends on blinding, which the X25519 _fast path cannot take per call.
- Consensus or interop code needing RFC 8032 strict verification: Verify_Check does not check S &lt; L or validate the public-key point, and CreateSharedKey does not reject all-zero output from small-order peer keys.
- aarch64, macOS or other non-x86-64 targets: only portable C (32-bit limbs; README says asm is about 3x faster than C on 64-bit) and the Makefiles reject anything but Linux, Cygwin and MinGW.
- Anything needing a maintained or audited library: no commits since 2020-04-20, open issues unanswered, no audit documented, and its OpenSSL comparison predates OpenSSL 3.x.

## How it is fast

Fixed-base scalar multiplication uses what the author calls FOLDING, which is essentially a fixed-base comb (Lim-Lee style): the 256-bit scalar is cut into 8 limbs of 32 bits, and each bit-slice indexes a 256-entry hard-coded table (source/base_folding8.h) of precomputed sums of 2^(32i)\*B, so a base-point multiply is 31 doublings plus 31 mixed additions in extended twisted-Edwards coordinates. Verification computes s\*B - h\*A jointly with the 8-fold base table plus a 16-entry 4-fold table built once per public key (ed25519_Verify_Init). Field multiply/square/add are hand-written x86-64 assembly on 4x64-bit limbs using plain MUL/ADC (no MULX/ADX/AVX). Variable-base X25519 (shared secret) is an ordinary Montgomery ladder and gets no comb speedup.

## Compared with alternatives

Pick it over EverCrypt/HACL\* or AWS-LC only when Ed25519 keygen/sign speed on x86-64 matters more than assurance and you want a tiny MIT C drop-in outside any TLS stack; for X25519 shared secrets, EverCrypt's formally verified Vale code (about 114K cycles per scalar multiply on its own test machine) is the better pick, and AWS-LC or wolfSSL are the choice when you need a maintained full TLS library.

## Integration

| | |
|---|---|
| **Form** | static lib (libcurve25519.a portable C, libcurve25519x64.a asm) or source-drop |
| **Dependencies** | none at runtime (bundled SHA-512); build runs a bundled custom tool that generates custom_blind.h; OpenSSL 1.1.0+ only for the comparison test |
| **Minimum toolchain** | Plain C with stdint types; GNU as (x86-64) or MASM for the asm build; documented builds: gcc 4.5.3 (Cygwin-32), VS2010, mingw GNU as 2.25; Makefiles use gcc and uname -o |
| **Platforms** | x86-64 asm on Linux and Windows (no ADX/BMI2/AVX needed); portable C for 32-bit and other CPUs, big-endian via -DECP_CONFIG_BIG_ENDIAN; macOS not supported by the Makefiles (a user in issue #9 reports it works after header changes) |
| **Thread safety** | not documented; the code read keeps no mutable global state (read-only tables and a build-time blinder), and per-key verify/blinding contexts are caller-owned |
| **Drop-in for the baseline** | partial — outputs match OpenSSL byte-for-byte in the test, but it is a separate C API over raw 32/64-byte buffers, not an EVP/ENGINE/provider replacement and not usable inside libssl |

## Gotchas

- curve25519_dh_CalculatePublicKey and curve25519_dh_CreateSharedKey take a non-const secret key and clamp it in place (issue #2); the plain CalculatePublicKey is the slow ladder that lost to OpenSSL, while the _fast variant is the comb path.
- Side-channel protection relies on blinding, not constant-time table access: pass a context from ed25519_Blinding_Init to CreateKeyPair/SignMessage to blind the scalar; with NULL, only a static build-time blinder randomizes the projective Z coordinate.
- The repo ships a fixed source/custom_blind.h; the Makefile regenerates it with custom_tool on each build. Vendoring the .c files without that step ships a public blinder, and omitting custom_blind.c gives 'unresolved external symbol edp_custom_blinding' (issue #13). The tool's RNG reads /dev/urandom in text mode without checking the fread length (author agreed in issue #10).
- ed25519_Verify_Init mallocs a context when passed NULL and returns NULL on failure; Verify_Check does not check for NULL, and you must call ed25519_Verify_Finish.

## Known shortcomings

- The OpenSSL test puts OpenSSL's key-object setup inside the timed loop while the library uses a precomputed key, inflating the SignMessage and CreateSharedKey wins; only CreateKeyPair (2.8x) is clean, and X25519 public-key derivation is 51% slower. Compared against OpenSSL 1.1.1 on an unspecified laptop CPU. Abandoned since 2020-04.
- The OpenSSL comparison is not like-for-like: CalculatePublicKey times the plain ladder rather than the table-based _fast path, while OpenSSL uses a fixed-base table; OpenSSL 1.1.1's EVP_PKEY_new_raw_private_key recomputes the public key inside the timed loops and leaks EVP_PKEY objects. Adjusted, signing stays \~2.7x faster and key generation 2.8x, but the X25519 shared-secret ladder is \~15% slower than OpenSSL's derive. The headline 43k cycles is base-point multiplication, not a shared secret (\~271k). Fixed-base multiplies index a 24 KB table with secret bits; protection relies on optional blinding, and the repo ships a public default blinder (custom tool's RNG read unchecked, #10). Not RFC-strict: verify skips S &lt; L and point validation (malleable), X25519 accepts all-zero outputs, DH clamps the caller's key in place (#2). Donna baseline is the portable 32-bit version. Linux/Cygwin/MinGW Makefiles only; x86-64 asm without MULX/ADX. Unmaintained since 2020; no audit; predates OpenSSL 3.

## Caveats and trade-offs

OpenSSL comparison dates from June 2019 (commit 'Performance comparison with OpenSSL') against OpenSSL 1.1.1 on one laptop whose CPU model is not given. OpenSSL-side timings include EVP_PKEY object creation from the raw secret inside the timed loop, and the Mehdi SignMessage side gets a precomputed public key, so the SignMessage and CreateSharedKey margins are inflated; the like-for-like CalculatePublicKey (X25519) row shows this library 51.45% slower than OpenSSL. Minimum of 100 TSC-timed runs, not core cycles. Current OpenSSL 3.x results are unknown. The curve25519-donna comparison (5.33x-19.59x) uses a different, non-list baseline across different compilers/platforms. Repo has had no commits since 2020-04-20.

One of four benchmarked operations (CalculatePublicKey) is markedly slower than OpenSSL, so the library is not a strict win across the board; portable-C build has no stated optimization level (only the asm build is used for the OpenSSL comparison); constant-time/blinding variants are slower than the non-hardened V1.1 numbers; abandoned since 2020, predates OpenSSL 3.x and modern OpenSSL X25519/Ed25519 assembly optimizations, so the OpenSSL side of the comparison is likely stale

## Maintenance

Abandoned (last commit 2020-04-20; a 2024 issue and a 2022 PR sit unanswered) but MIT-licensed and small enough to vendor; the OpenSSL comparison predates OpenSSL 3.x and no security audit is documented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** README's 'OpenSSL comparison (make openssl)' block shows the claimed cycle counts, and the benchmark code is public (test/openssl_test.c, built by 'make openssl' with -O2), but the OpenSSL run names only the laptop (HP EliteBook 755 G5, Ubuntu 18.04.2, OpenSSL 1.1.1), not the CPU model or gcc version, so it falls short of A. The donna table has a CPU model (i7-2670QM) and compilers, but its baseline, curve25519-donna, is not OpenSSL.
- **Verifier notes:** Downgraded A to C: the OpenSSL benchmark omits the CPU model and gcc version, and the record's claim that the portable-C build lacks -O2 is wrong (source/Makefile and source/asm64/Makefile both use -O2). Reading test/openssl_test.c shows OpenSSL timings include EVP_PKEY setup while the Mehdi sign path gets a precomputed key, so only CreateKeyPair (2.8x) is a clean win; X25519 public-key derivation is slower than OpenSSL. MIT license, 165 stars, last commit 2020-04-20 (abandoned), not fork, not archived: metadata confirmed.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/msotoodeh/curve25519>
  - <https://github.com/msotoodeh/curve25519/blob/master/README.md>
  - <https://github.com/msotoodeh/curve25519/blob/master/test/openssl_test.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/Rules.mk>
  - <https://github.com/msotoodeh/curve25519/blob/master/test/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/asm64/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/license.txt>
- **Sources the enricher read:**
  - <https://github.com/msotoodeh/curve25519>
  - <https://github.com/msotoodeh/curve25519/blob/master/README.md>
  - <https://github.com/msotoodeh/curve25519/blob/master/include/curve25519_dh.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/include/ed25519_signature.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/include/external_calls.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/test/openssl_test.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/test/curve25519_test.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/test/curve25519_donna.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/curve25519_dh.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/curve25519_mehdi.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/curve25519_utils.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/ed25519_sign.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/ed25519_verify.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/custom_blind.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/custom_blind.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/BaseTypes.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/asm64/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/asm64/amd64.gnu/Mult.s>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/asm64/amd64.gnu/Fold.s>
  - <https://github.com/msotoodeh/curve25519/blob/master/source/asm64/amd64.gnu/defines.inc>
  - <https://github.com/msotoodeh/curve25519/blob/master/Makefile>
  - <https://github.com/msotoodeh/curve25519/blob/master/Rules.mk>
  - <https://github.com/msotoodeh/curve25519/blob/master/custom/random.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/custom/main.c>
  - <https://github.com/msotoodeh/curve25519/blob/master/C++/ed25519.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/C++/x25519.h>
  - <https://github.com/msotoodeh/curve25519/blob/master/C++/ed25519.cpp>
  - <https://github.com/msotoodeh/curve25519/issues?q=is%3Aissue>
  - <https://github.com/msotoodeh/curve25519/pulls?q=is%3Apr>
  - <https://github.com/msotoodeh/curve25519/commits/master>
  - <https://github.com/msotoodeh/curve25519/issues/2>
  - <https://github.com/msotoodeh/curve25519/issues/4>
  - <https://github.com/msotoodeh/curve25519/issues/6>
  - <https://github.com/msotoodeh/curve25519/issues/9>
  - <https://github.com/msotoodeh/curve25519/issues/10>
  - <https://github.com/msotoodeh/curve25519/issues/12>
  - <https://github.com/msotoodeh/curve25519/issues/13>
  - <https://github.com/openssl/openssl/blob/OpenSSL_1_1_1-stable/crypto/ec/ecx_meth.c>
  - <https://github.com/openssl/openssl/blob/OpenSSL_1_1_1-stable/crypto/ec/curve25519.c>
  - https://hn.algolia.com/api/v1/search?query=msotoodeh&tags=(story,comment)
  - https://hn.algolia.com/api/v1/search?query=%22curve25519%22%20folding&tags=(story,comment)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/msotoodeh/curve25519`) · [data/wave5/enrich/raw/github_com_msotoodeh_curve25519.json](../../../data/wave5/enrich/raw/github_com_msotoodeh_curve25519.json) (enrichment confidence 0.7)

</details>
