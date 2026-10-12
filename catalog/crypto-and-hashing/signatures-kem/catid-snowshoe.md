# Snowshoe (catid/snowshoe)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Constant-time EC scalar multiplication on a custom 2^127-1 GLS curve, claimed 4-8x faster than OpenSSL 1.0.1e P-256.

| | |
|---|---|
| **Beats** | OpenSSL 1.0.1e (NIST P-256 elliptic-curve math, ecp_nistp256.c) |
| **Claimed result** | README: 'Kasper demonstrates that the improvements in the paper are roughly 3x faster than normal OpenSSL, pegging Snowshoe roughly 6x faster than OpenSSL 1.0.1e for the same security level' (an indirect estimate). It also says the author's own OpenSSL 1.0.1e `make tests` run (64-bit, ectest.c timing macros enabled) showed 'roughly 100 usec to generate a key (4x slower)' and 'roughly 400 usec for EC-DH (8x slower)'. Both ratios are stated verbatim on the page, not derived. The same page says Crypto++ 5.6.2 and LibTomCrypt 1.17 ECC-256 are 'roughly 20x slower than Snowshoe'. |
| **Workload** | Elliptic-curve scalar multiplication / EC-DH and signature-style operations (ec_mul, ec_simul) on a custom \~252-bit curve at \~128-bit security, cycle-counted with RDTSC (Turbo Boost disabled), compared against OpenSSL 1.0.1e's P-256 timing tests and a third-party paper's OpenSSL-optimization results |
| **Metric** | latency |
| **Hardware** | Snowshoe's own RDTSC runs, Turbo Boost off: Core i5-2557M (MacBook Air), Core i5-2500S (iMac) and Core i7 620M (Windows 7 laptop). The page does not say which machine ran OpenSSL 1.0.1e. The i7-2600 and i7-3770 figures on the page are Longa's implementation numbers, not Snowshoe-vs-OpenSSL. |
| **Compiler and flags** | Snowshoe side: Makefile default clang++ -m64 with OPTFLAGS -O4 (make ecmultest / make release); a GCC alternative, -O3 -fomit-frame-pointer -funroll-loops, is commented out. OpenSSL 1.0.1e side: default 64-bit build, flags unstated. |
| **Adoption** | 64 stars |
| **Last commit** | 2018-02-03 |
| **Links** | [repository](https://github.com/catid/snowshoe) · [benchmark](https://github.com/catid/snowshoe/blob/master/README.md) |

## Verdict

Snowshoe side: median of 10,000 RDTSC samples with Turbo Boost off, clang++ -m64 -O4, on Sandy Bridge i5-2557M and i5-2500S. ec_mul_gen took about 60k cycles, ec_mul about 131k and ec_simul about 192k, or 22.4 us for keygen and 49.3 us for EC-DH on the 2.7 GHz iMac. OpenSSL side: the author reports 'roughly 100 usec' for keygen (4x slower) and 'roughly 400 usec' for EC-DH (8x slower) from OpenSSL 1.0.1e's make tests with the ectest.c timing macros, on an unnamed machine with no harness in the repo. Two further caveats on that run. First, the ecp_nistp256.c path the README names is gated by ec_nistp_64_gcc_128, which OpenSSL 1.0.1e's Configure disables by default, and the README does not say it was enabled. Second, the '\~6x' headline chains Kasper's P-224-only paper (which claims 'up to 4 times faster' atomic operations, not 3x) with a cycle-count projection. A 2020 third-party MSVC reproduction measured 2-2.5x more cycles than the README.

## Use it when

- Studying or teaching constant-time GLS/GLV-SAC scalar multiplication: the README derives the curve, endomorphism, decomposition and base point in detail, with MAGMA scripts, and the code is about 5.3k heavily commented lines.
- Closed systems where you control both endpoints and already depend on Snowshoe or Tabby, and interoperability with standard curves does not matter.
- As a historical reference point when benchmarking 2013-era 128-bit-security EC implementations on x86-64 (Sandy Bridge figures published with methodology).
- Experiments that need a fast, allocation-free, constant-time variable-base mul or double-base simul on x86-64 built with GCC or Clang.

## Skip it when

- Any new production system: in 2020 the author told a user who could not reproduce the benchmarks, 'These days I'd recommend not to use this library and instead use one of the more active projects' (issue #4).
- Anything that must interoperate with P-256, X25519/Ed25519 or secp256k1. The curve is non-standard, public keys are 64-byte uncompressed (X,Y), and there is no ASN.1, EVP or ECDSA layer.
- MSVC or Intel C++ builds of the source. The README says these compilers are unsupported, and a 2020 MSVC 2019 x64 build measured 2-2.5x more cycles than the README on the same Sandy Bridge class of CPU (issue #4, never resolved).
- Non-x86-64 targets where speed matters. The fast paths are x86-64 inline asm plus native 128-bit integers; 32-bit and ARM builds exist (a 2014 commit and a Makefile target hardwired to a local toolchain path) but have no published numbers.
- When you need the fastest or best-reviewed option. The README's own comparison table shows Longa's GLV-GLS code and 'Kummer strikes back' beating it on several operations, and the author's handshake constructions had no security proof (issue #1). The README also says there is no blinding against power analysis.

## How it is fast

Field arithmetic is in Fp^2 over the Mersenne prime 2^127-1: reduction is a shift and add, multiplies use x86-64 64x64-&gt;128 instructions (GCC/Clang __uint128_t plus AT&T inline asm), and Fp^2 multiplication uses 3 Fp multiplies (Karatsuba). Points use extended twisted Edwards coordinates (Hisil et al.) with complete formulas. A 2-dimensional GLS endomorphism (Galbraith-Lin-Scott), with Smith's short lattice basis, splits the 252-bit scalar into two \~126-bit halves, which are then recoded with GLV-SAC (Faz-Hernandez/Longa/Sanchez, 'Keep Calm and Stay with One'). The halves are evaluated with 2-bit windows and masked constant-time table lookups. Fixed-base multiplication uses an LSB-set comb (w=6, v=7) over static precomputed tables. The whole library compiles as one translation unit so the compiler can inline everything.

## Compared with alternatives

FourQlib uses the same design ideas (Fp^2 over 2^127-1, twisted Edwards, endomorphism decomposition), adds a 4-dimensional decomposition, and is maintained. Its catalog entry reports about 72k cycles for variable-base multiplication on Sandy Bridge, against Snowshoe's about 131k (a comparison across different pages), so pick FourQlib when you want speed with that design. Pick the Ed25519, libsecp256k1 or curve25519-voi entries for standard, interoperable curves; Snowshoe only makes sense as a readable reference implementation or for existing Snowshoe/Tabby deployments.

## Integration

| | |
|---|---|
| **Form** | static lib (build src/snowshoe.cpp, one translation unit, or link the prebuilt bin/libsnowshoe.a / libsnowshoe.lib) or source-drop |
| **Dependencies** | libcat (catid/libcat git submodule, pinned; per-file BSD-style headers but no repo-level LICENSE file) for platform macros, 128-bit math, endian and secure-erase helpers. The caller must supply the RNG and any hash function. |
| **Minimum toolchain** | GCC or Clang with __uint128_t for full speed (Makefile default: clang++ -m64 -O4; the README says Clang generates better code). No C++ standard is stated. MSVC and Intel C++ are unsupported for compiling, but MSVC can link a MinGW/LLVM-built .lib. |
| **Platforms** | x86-64 is the primary target; its fast paths use inline asm. A little-endian fast path is included and big-endian loads/saves are handled. A 32-bit mode was added in March 2014 via emulated 128-bit math, and there is an ARM cross-compile target. Only the x86-64 builds have benchmarks (macOS and Windows). |
| **Thread safety** | Not documented. From reading the source there is no mutable global state (precomputed tables are static const and nothing is heap-allocated), so concurrent calls on separate buffers appear safe, but this is unverified. |
| **Drop-in for the baseline** | no |

## Gotchas

- Call snowshoe_init() at startup and check its return value. It checks struct sizes and the library version, and runs a power-on self-test meant to catch compilers that build the 128-bit math but produce wrong results (the source names Intel C++).
- Scalars must satisfy 0 &lt; k &lt; q, and input points are validated. Every multiply returns non-zero on bad input, and you must check it because this is the defence against invalid-point attacks. mul, simul and simul_gen compute 4\*k\*P (cofactor clearing); mul_gen multiplies by 4 only when its mul4 flag is set.
- simul_gen is explicitly not constant-time. Use it only with public inputs, such as signature verification.
- The README's 'EdDSA sign/verify' timings come from tests/snowshoe_test.cpp, which uses fake hashes ('to avoid implementing Skein'). They leave out hashing cost and are not directly comparable to full Ed25519 or ECDSA timings.

## Known shortcomings

- Abandoned since 2018; non-standard curve (not usable where P-256/Ed25519 interoperability is required). OpenSSL was 4x/8x slower per the README, but the OpenSSL machine and flags are unstated and there is no harness; other research code (Longa's FourQ, Kummer, Hamburg's work) is faster on some operations.
- The author said in 2020 (issue #4) not to use it and to pick more active projects; an MSVC 2019 build took 2-2.5x the README's cycle counts (unresolved). OpenSSL 1.0.1e's ecp_nistp256 path was off by default and the README does not say it was enabled. The '6x' relies on Käsper's paper, which covers P-224 only and claims up to 4x. README EdDSA timings use fake hashes (no hashing cost); not in eBACS; FourQlib is faster (\~72k vs \~131k cycles, cross-paper).

## Caveats and trade-offs

The OpenSSL 1.0.1e baseline (2013) is over a decade old. The '6x' figure is an indirect estimate that chains Kasper's paper (about 3x over stock OpenSSL on Core 2) with the author's projected Snowshoe cycle counts. The 4x/8x figures come from the author's own rough OpenSSL run ('roughly' 100/400 usec) on an unstated machine, with no harness in the repo. On the same page some competing 128-bit curve implementations beat Snowshoe on some operations: Longa ecmul_gen/ecmul/ecsimul_gen, Kummer ecmul 72kcy, kumfp127g ecmul and Hamburg ecmul_gen per the page's labels. The BSD-3-Clause LICENSE was added only in 2018 (PR #3). Custom non-standard curve.

Targets a custom non-standard curve rather than NIST P-256 or secp256k1, limiting interoperability; project is explicitly pre-1.0/experimental

## Maintenance

Abandoned: the last code change was in March 2014 (a BSD-3-Clause LICENSE was added in February 2018), and in 2020 the author recommended more active projects instead. It is small and permissively licensed enough to vendor for study, but it is not advisable for new production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Comparisons section compares Snowshoe with OpenSSL 1.0.1e (ecp_nistp256.c). It gives an indirect '\~6x faster' estimate built on Kasper's paper, plus the author's own approximate OpenSSL `make tests` timings ('roughly 100 usec' keygen, 4x slower; 'roughly 400 usec' EC-DH, 8x slower). The Snowshoe side has public bench code (tests/ecmul_test.cpp, tests/snowshoe_test.cpp, Makefile clang++ -m64 -O4, median of 10,000 RDTSC runs, CPUs named). The OpenSSL run gives no machine or flags and ships no harness, so this is first-party partial methodology: C.
- **Verifier notes:** Real entry, accurate apart from a mislabel: the 4x/8x ratios were marked '(derived from page data)' but the README states them outright. The hardware field wrongly mixed in Longa's CPUs. Metadata checked: BSD-3-Clause, not archived, not a fork, 64 stars, last commit 2018-02-03, so abandoned is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/catid/snowshoe>
  - <https://github.com/catid/snowshoe/blob/master/README.md>
  - <https://raw.githubusercontent.com/catid/snowshoe/master/README.md>
  - <https://raw.githubusercontent.com/catid/snowshoe/master/Makefile>
  - <https://raw.githubusercontent.com/catid/snowshoe/master/tests/ecmul_test.cpp>
- **Sources the enricher read:**
  - <https://github.com/catid/snowshoe>
  - <https://github.com/catid/snowshoe/blob/master/README.md>
  - <https://github.com/catid/snowshoe/blob/master/include/snowshoe.h>
  - <https://github.com/catid/snowshoe/blob/master/Makefile>
  - <https://github.com/catid/snowshoe/blob/master/LICENSE>
  - <https://github.com/catid/snowshoe/blob/master/.gitmodules>
  - <https://github.com/catid/snowshoe/blob/master/src/README.md>
  - <https://github.com/catid/snowshoe/blob/master/src/snowshoe.cpp>
  - <https://github.com/catid/snowshoe/blob/master/src/fp.inc>
  - <https://github.com/catid/snowshoe/blob/master/src/fe.inc>
  - <https://github.com/catid/snowshoe/blob/master/src/ecmul.inc>
  - <https://github.com/catid/snowshoe/blob/master/src/recode.inc>
  - <https://github.com/catid/snowshoe/blob/master/src/precomp.inc>
  - <https://github.com/catid/snowshoe/blob/master/tests/README.md>
  - <https://github.com/catid/snowshoe/blob/master/tests/ecmul_test.cpp>
  - <https://github.com/catid/snowshoe/blob/master/tests/snowshoe_test.cpp>
  - <https://github.com/catid/snowshoe/blob/master/bin/LINKING.md>
  - <https://github.com/catid/snowshoe/blob/master/supercop/crypto_sign/snowshoe/ref/README.md>
  - <https://github.com/catid/snowshoe/commits/master>
  - <https://github.com/catid/snowshoe/issues/1>
  - <https://github.com/catid/snowshoe/issues/2>
  - <https://github.com/catid/snowshoe/issues/4>
  - <https://github.com/catid/snowshoe/issues/6>
  - <https://github.com/catid/libcat>
  - <https://github.com/catid/libcat/blob/9ca03e48e7f6f38ee001d8c89eda0f7c1e2a7734/BigMath.hpp>
  - <https://github.com/catid/libcat/blob/9ca03e48e7f6f38ee001d8c89eda0f7c1e2a7734/Platform.hpp>
  - <https://github.com/catid/tabby>
  - <https://bench.cr.yp.to/primitives-dh.html>
  - <https://bench.cr.yp.to/primitives-sign.html>
  - <https://hn.algolia.com/api/v1/search?query=snowshoe%20curve>
  - <https://raw.githubusercontent.com/openssl/openssl/OpenSSL_1_0_1e/Configure>
  - <https://raw.githubusercontent.com/openssl/openssl/OpenSSL_1_0_1e/CHANGES>
  - <http://static.googleusercontent.com/media/research.google.com/en/us/pubs/archive/37376.pdf>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/catid/snowshoe`) · [data/wave7/enrich/raw/github_com_catid_snowshoe.json](../../../data/wave7/enrich/raw/github_com_catid_snowshoe.json) (enrichment confidence 0.8)

</details>
