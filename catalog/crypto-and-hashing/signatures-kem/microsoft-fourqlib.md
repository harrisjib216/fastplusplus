# FourQlib (SchnorrQ / FourQ curve arithmetic)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Microsoft Research C library for FourQ ECDH and SchnorrQ signatures; up to 5.6x faster scalar multiplication than fast P-256 code.

| | |
|---|---|
| **Beats** | NIST P-256 (Gueron-Krasnov fast implementation, the code later merged into OpenSSL as nistz256) |
| **Claimed result** | Table 5 (ePrint 2015/565): variable-base scalar multiplication up to 5.6x faster than the Gueron-Krasnov P-256 implementation [27] (Sandy Bridge 72k vs 400k cycles; Haswell 56k vs 312k). One ephemeral DH round is up to 4.4x faster than P-256 (Sandy Bridge 112k vs 490k). Variable-base is 2.2-2.9x faster than the Curve25519 implementations [3,14], and ephemeral DH 1.9-3.7x faster. |
| **Workload** | Variable-base and fixed-base elliptic-curve scalar multiplication (the core operation underlying ECDH and SchnorrQ signing/verification), modeled as one ephemeral Diffie-Hellman round, on several x64 CPUs |
| **Metric** | throughput |
| **Hardware** | Intel Atom N570 (1.66GHz), Core i7-2600 Sandy Bridge (3.4GHz), Core i7-3770 Ivy Bridge (3.4GHz), Core i7-4770 Haswell (3.4GHz), Core i5-5300U Broadwell (2.30GHz), AMD A8 PRO-7600B Kaveri (3.1GHz); TurboBoost/TurboCore disabled |
| **Adoption** | 95 stars (Microsoft Research) |
| **Last commit** | 2022-08-31 |
| **Links** | [repository](https://github.com/microsoft/FourQlib) · [benchmark](https://eprint.iacr.org/2015/565.pdf) |

## Verdict

In Table 5 of the ASIACRYPT 2015 paper (ePrint 2015/565), FourQlib 2.0 did a variable-base scalar multiplication in 72k cycles on a Sandy Bridge i7-2600 and 56k on a Haswell i7-4770 (TurboBoost off), against 400k and 312k for the Gueron-Krasnov P-256 code (about 5.6x), and one ephemeral DH round in 112k vs 490k cycles (4.4x). The P-256 figures were copied from the Gueron-Krasnov paper rather than re-run, no compiler or flags are given, the FourQ code then used no vector instructions, and the current v3.1 code has not been re-benchmarked against a baseline.

## Use it when

- You control both ends of the protocol (internal RPC, a device fleet, a research prototype) and want the fastest constant-time ECDH or signatures at the 128-bit security level, with no standards requirement.
- Ephemeral Diffie-Hellman on x64 Linux, where scalar multiplication dominates the cost. The paper reports 30-40k cycles for fixed-base key generation and 50-72k cycles for variable-base multiplication on Broadwell through Sandy Bridge.
- 32-bit ARM, NEON (Cortex-A7/A8/A9/A15) or Cortex-M4 targets, which have their own tuned code trees that share the same API.
- Benchmarking or teaching endomorphism-accelerated ECC: the code is compact, comes with Magma scripts that check the paper's operation counts, and can be built with or without the endomorphisms (USE_ENDO).

## Skip it when

- Anything that needs interop or compliance, such as TLS, X.509, SSH, JOSE/COSE or FIPS 140. FourQ is not a NIST or IETF curve, and the Curve4Q Internet-Draft (draft-ladd-cfrg-4q-01) expired in 2017.
- macOS or any OS other than Linux or Windows. FourQ.h stops with #error "Unsupported OS" unless __LINUX__ or __WINDOWS__ is defined, and the Mac issues #2 and #6 are unanswered.
- Production use without your own validation. Open issue #10 (2024) reports that the GF(p^2) inversion test FAILS with GCC 11.4.1 at -O2/-O3 while clang 15 passes, and nobody from the project has replied.
- SchnorrQ over large or streamed messages. Sign and Verify calloc a full copy of the message (SizeMessage+64 bytes, length typed as unsigned int), and there is no prehash or streaming API.
- Hardened embedded deployments using the bundled side-channel tree as-is: FourQ_ARM_side_channel is labeled experimental and 'DO NOT USE AS IS IN PRODUCTION', and its SHA-512 is not DPA-protected.

## How it is fast

FourQ has two cheap endomorphisms, psi (from the Q-curve construction) and phi (from complex multiplication with discriminant -40), which allow a four-dimensional GLV decomposition of a 256-bit scalar into four 64-bit sub-scalars. After a constant-time recoding (the Faz-Hernandez/Longa/Sanchez GLV-GLS recoding), variable-base multiplication is 64 double-and-add steps over an 8-point table, using complete extended twisted Edwards formulas over the Mersenne prime 2^127-1, where reduction is very cheap. Fixed-base multiplication uses an LSB-set comb with an 80-point (7.5 KB) table, and verification uses interleaved wNAF with a 24 KB table. On x64 Linux the GF(p^2) arithmetic is hand-written assembly, whose AVX2 variant also uses MULX and ymm registers.

## Compared with alternatives

Choose FourQlib over the SUPERCOP Ed25519 code or ENG25519 only when you do not need Ed25519/X25519 compatibility and your CPUs lack AVX-512 IFMA. Its 2015 paper measured 2.2-2.9x faster variable-base multiplication than the Curve25519 code of that era, whereas ENG25519 speeds up the standard curves on IFMA hardware. Use libsecp256k1 for Bitcoin's secp256k1 and ocaml-curve448 if you need X448/Ed448.

## Integration

| | |
|---|---|
| **Form** | source-drop (the makefile builds the test binaries, and libFourQ.so with SHARED_LIB=TRUE; a Visual Studio 2015 solution builds FourQ.lib; no install target, CMake or pkg-config) |
| **Dependencies** | None external. Bundled public-domain SHA-512 and a /dev/urandom or BCryptGenRandom/RtlGenRandom RNG, both replaceable via macros in FourQ.h. The Cortex-M4 trees bundle libopencm3 (LGPL-3.0) and CC0 STM32 wrappers. |
| **Minimum toolchain** | C with 128-bit integers (GCC/clang mode(TI)) or MSVC _umul128. Tested with Visual Studio 2015, GCC 4.9 and clang 3.8; GCC 11.4.1 at -O2/-O3 is reported to fail the fp tests. The makefile uses GNU sed -i. |
| **Platforms** | Linux and Windows only. x64 has the optimized path (the default AVX2 assembly needs Haswell+ with BMI2 MULX, and assembly is Linux-only, so Windows gets the C path). ARMv8 64-bit has optimized C; x86 and 32-bit ARM use the portable C. ARMv6/ARMv7, NEON and Cortex-M4 have separate trees. |
| **Thread safety** | Not documented. Operations keep their state on the stack and read constant tables, but the Linux RNG lazily opens a static /dev/urandom descriptor with no locking, so concurrent first calls race. |
| **Drop-in for the baseline** | no |

## Gotchas

- ecc_mul takes a clear_cofactor flag. The high-level SecretAgreement calls clear the cofactor (x392) and reject a neutral-point result, but raw ecc_mul callers must pass true for any untrusted point. The ECDH output is only the 32-byte y-coordinate.
- The default Linux build adds -march=native (EXTENDED_SET) and, on x64, AVX2+MULX assembly, so the binaries are not portable. Set EXTENDED_SET=FALSE and AVX2=FALSE (or GENERIC=TRUE) for distributable builds.
- TEMP_ZEROING is commented out by default, so secret intermediates in scalar multiplication are not wiped. ecc_mul_double (used for verification) and point validation are explicitly non-constant-time and meant only for public inputs.
- SchnorrQ signatures always end in a 0x00 byte because s &lt; 2^246, and the verifier rejects anything else (issue #3). Secret keys are unclamped 256-bit hash outputs, and nonces are deterministic, as in EdDSA.

## Known shortcomings

- FourQ is a non-standard curve (not NIST or IETF approved for TLS), so it cannot replace P-256 where interoperability matters. P-256 comparison figures are copied from the Gueron-Krasnov paper, not re-measured. ARM directories vendor LGPL-3.0 libopencm3.
- Linux and Windows only (macOS hits #error; x64 asm is Linux-only). Open #10: GCC 11.4.1 at -O2/-O3 fails the fp2 inversion test, unanswered. Code inactive since 2021, no releases or tags. Default build uses -march=native with AVX2/MULX (binaries not portable); TEMP_ZEROING off by default. Curve4Q Internet-Draft expired 2017.

## Caveats and trade-offs

The P-256 comparison figures (Sandy Bridge and Haswell only) were copied directly from the Gueron-Krasnov paper [27], not re-measured on the FourQ authors' machines. That code is the basis of OpenSSL's ecp_nistz256, whose header credits Gueron and Krasnov. The paper states no compiler or flags, only CPU models. The benchmark CPUs are 2011-2015-era. No SchnorrQ signing/verification cycle comparison against a baseline appears in the paper, which covers scalar multiplication and DH only. The core is MIT-licensed, but the ARM folders include CC0 wrappers and LGPL-3.0 libopencm3.

FourQ is a non-NIST, non-standardized curve, so adopting it trades interoperability/standard compliance for speed; correct use requires careful handling of the curve's cofactor and endomorphisms for security.

## Maintenance

Abandoned: the last code change was the hash-to-curve addition on 2021-03-19, the last commit (2022-08-31) only added Microsoft's SECURITY.md, and there has never been a tagged release (issue #1). The MIT core is small enough to vendor, but plan on validating your own compiler and maintaining fixes yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed ASIACRYPT 2015 paper (extended ePrint 2015/565) Table 5 compares FourQlib 2.0 against the Gueron-Krasnov P-256 code [27] and Curve25519, with CPU models and TurboBoost-off stated. It falls short of A because no compiler or flags are given. Also, the P-256 figures were copied from [27] rather than measured by the FourQ authors on their own machines.
- **Verifier notes:** All claimed ratios match the paper text and Table 5. The DH-vs-Curve25519 range (1.9-3.7x) was added, and the claim that the numbers 'predate OpenSSL's nistz256 merge' was dropped as unverified. Metadata checked: MIT, 95 stars, not a fork, not archived, last commit 2022-08-31 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2015/565.pdf>
  - <https://github.com/microsoft/FourQlib>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/ec/ecp_nistz256.c>
- **Sources the enricher read:**
  - <https://github.com/microsoft/FourQlib>
  - <https://github.com/microsoft/FourQlib/blob/master/README.md>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/README.md>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/FourQ_api.h>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/FourQ.h>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/FourQ_internal.h>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/makefile>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/eccp2.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/eccp2_core.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/kex.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/schnorrq.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/table_lookup.h>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/crypto_util.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/AMD64/fp_x64.h>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/AMD64/fp2_1271_AVX2.S>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/AMD64/fp2_1271.S>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/tests/crypto_tests.c>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_64bit_and_portable/tests/test_extras.c>
  - <https://github.com/microsoft/FourQlib/blob/master/random/random.c>
  - <https://github.com/microsoft/FourQlib/blob/master/SECURITY.md>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_ARM_NEON/README.md>
  - <https://github.com/microsoft/FourQlib/blob/master/FourQ_ARM_side_channel/README.md>
  - <https://github.com/microsoft/FourQlib/commits/master>
  - <https://github.com/microsoft/FourQlib/issues/2>
  - <https://github.com/microsoft/FourQlib/issues/3>
  - <https://github.com/microsoft/FourQlib/issues/5>
  - <https://github.com/microsoft/FourQlib/issues/6>
  - <https://github.com/microsoft/FourQlib/issues/8>
  - <https://github.com/microsoft/FourQlib/issues/9>
  - <https://github.com/microsoft/FourQlib/issues/10>
  - <https://github.com/microsoft/FourQlib/issues/11>
  - <https://eprint.iacr.org/2015/565.pdf>
  - <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/SchnorrQ.pdf>
  - <https://datatracker.ietf.org/api/v1/doc/document/draft-ladd-cfrg-4q/>
  - <https://hn.algolia.com/api/v1/search?query=FourQ%20curve&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/microsoft/fourqlib`) · [data/wave7/enrich/raw/github_com_microsoft_fourqlib.json](../../../data/wave7/enrich/raw/github_com_microsoft_fourqlib.json) (enrichment confidence 0.8)

</details>
