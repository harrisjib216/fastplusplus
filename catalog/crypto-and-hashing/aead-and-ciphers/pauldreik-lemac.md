# LeMac (pauldreik C++20 port)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> C++20 library and lemacsum CLI for LeMac, an AES-round MAC measured at \~27x OpenSSL SHA-1 bulk throughput on Zen 4.

| | |
|---|---|
| **Beats** | SHA-1 (OpenSSL EVP) |
| **Claimed result** | LeMac oneshot 76.7 GiB/s (256 kB) and 74.3 GiB/s (1 MB), median of 5 runs, vs about 2.8 GiB/s for OpenSSL SHA1 (`openssl speed -evp SHA1`) on the same AMD Ryzen 9 7950X3D, i.e. \~26-27x (derived from page data). The same README also reports: xxh3/xxh128 reach about 89 GiB/s with `xxhsum -b`, 'about 16% faster than lemac' (LeMac does not beat xxh3); clhash reaches 0.11 cycles/byte vs LeMac's 0.067 cycles/byte, which the README states as clhash being 'about 39% slower than lemac' (equivalently LeMac \~1.6x clhash throughput, derived from page data); raw AES-128-ECB (`openssl speed -evp AES-128-ECB`) reaches about 16.4 GiB/s. On a Raspberry Pi 5, LeMac does about 11.4 GiB/s against 13.2 GiB/s for xxh and 3.4 GiB/s for AES-128-ECB. |
| **Workload** | Single-core bulk MAC/digest throughput: LeMac oneshot() hashing 256 KB/1 MB buffers vs `openssl speed -evp SHA1`, same AMD Ryzen 9 7950X3D machine (Debian 13 Trixie) |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X3D, Debian 13 Trixie (primary bulk numbers, 77 GiB/s / 0.067 cycles/byte); also Apple M4 MacBook Air (48 GiB/s), Apple M3 MacBook Air, and Raspberry Pi 5 / Ubuntu 24.04 (11 GiB/s, thermally throttled per README) |
| **Compiler and flags** | cmake -DCMAKE_BUILD_TYPE=Release, with per-file flags from CMakeLists.txt on gcc/clang: -maes -msse2 for the AES-NI-128 path, and -maes -mvaes -mavx512f -mavx512vl for the VAES/AVX-512 path. The compiler is not named for the Zen4/Linux run (the README says Linux support is clang&gt;=16 and gcc&gt;=12); 'compiler: clang' is printed only for the Apple M3/M4 runs. |
| **Adoption** | 4 stars, 2 forks |
| **Last commit** | 2025-06-17 |
| **Links** | [repository](https://github.com/pauldreik/lemac) · [benchmark](https://github.com/pauldreik/lemac) |

## Verdict

The numbers are first-party and come from the README. On a Ryzen 9 7950X3D (Debian 13, compiler unnamed, Release build with per-file -maes / -mvaes -mavx512f -mavx512vl), the repo's benchmark gave LeMac oneshot 76.7 (256 kB) and 74.3 (1 MB) 'GiB/s' (median of 5), against about 2.8 GiB/s from `openssl speed -evp SHA1` on the same machine, roughly 27x, but that compares a keyed MAC with an unkeyed digest. benchmark.cpp actually prints bytes/s x 1e-9 under a 'GiB/s' label, so the LeMac figures are decimal GB/s (about 71 GiB/s), while the baselines (openssl speed, xxhsum -b, clhash's benchmark) come from outside tools with their own units.

## Use it when

- Authenticating large buffers (16 KB and up) under a secret 128-bit key where GMAC or HMAC throughput is the bottleneck. The README measured about 74-77 GB/s single-core on a Ryzen 9 7950X3D and 43-48 GB/s on Apple M3/M4 at 256 KB-1 MB.
- Integrity tags for storage or replication pipelines where both ends are your code and a unique nonce per message is available, since the paper claims 128-bit security only when nonces are respected.
- Many messages under one key: build the keyed hasher once, then copy it or reset() it per message. Keying costs about 5 KB of hashing and finalisation about 2 KB.
- C++20/CMake projects on x86-64 with AES-NI, or arm64 with crypto extensions (Linux, macOS Apple silicon, Windows), that want FetchContent/find_package integration, runtime CPU dispatch and a sanitizer-tested codebase instead of the upstream research C code.

## Skip it when

- As an unkeyed digest or 'cryptographic checksum' against adversaries, which is how lemacsum and the README example use it (all-zero key and nonce). The paper's UHF security 'only requires collision resistance on average over a random key', so with a public key there is no claimed collision resistance.
- Non-adversarial fast checksums: xxh3/xxh128 is about 16% faster on the same Zen 4 (89 vs 77 GiB/s per README) and faster on the Pi 5 (13.2 vs 11.4 GiB/s).
- Short messages without reuse. A fresh object costs about 5 KB of hashing to key, and on M4 a 1-byte oneshot runs at 0.021 GiB/s (0.049 us/hash), while 1 KB reaches only 17-23 GiB/s against about 48 GiB/s at 256 KB.
- CPUs without AES-NI or ARMv8 crypto, and any other architecture. There is no software fallback: CMake stops with FATAL_ERROR on unknown architectures, and the constructor calls std::abort() on unsupported CPUs.
- Interoperable or standardised MACs (protocols, FIPS). LeMac is a 2024 research design whose spec already changed once (LeMac-0 to LeMac, so values differ), and this port is a 4-star v0.1 that has had no commits since June 2025.

## How it is fast

LeMac is an AES-round universal hash from the paper's MILP-optimised framework. A 9 x 128-bit state plus a 4-register message schedule (RR, R0-R2) absorbs each 64-byte block with 8 independent AESENC instructions (2 AES rounds per 128-bit word) and a few XORs. That lets CPUs that issue two AESENC per cycle approach 4 cycles per 64 bytes, and the README measured 0.067 c/B. Tags use the EWCDM construction: four zero-block rounds, nine modified AES-128 calls over the state, and AES of the nonce, which gives the fixed \~2 KB-equivalent finalisation cost. On x86 the runtime dispatch chooses between a -maes build and a build of the same 128-bit intrinsics compiled with -mvaes -mavx512f -mavx512vl; there is no 256/512-bit multi-block AES. On arm64, AESENC is emulated as AESE(zero)+AESMC+EOR.

## Compared with alternatives

Pick it over the upstream LeMac sibling (AugustinBariant/Implementations_LeMac_PetitMac: C/Python research code, AES-NI only, Makefile) when you need arm64/Windows support, a streaming C++ API, CMake packaging or a CLI; both implement the corrected LeMac and share test vectors. Pick it over libaegis (AEGIS-128L) only when you need a MAC and never encryption on AES-capable hardware: the LeMac paper measured 0.068 vs 0.195 c/B for AEGIS128L in AD-only mode on Ice Lake at 256 kB. For AEAD, portability without AES hardware or a mature, widely deployed codebase, libaegis wins.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_library; can also be installed with find_package config or packaged as Debian liblemac0/liblemac-dev) plus the lemacsum CLI |
| **Dependencies** | none for the library; CMake &gt;= 3.23 to build; Catch2 v3 only for tests (vcpkg.json) |
| **Minimum toolchain** | C++20; GCC 12+ / Clang 16+ on Linux (CI matrix covers g++ 12-14 and clang++ 16-18), Apple clang on macOS, MSVC for Windows amd64/arm64, and a MinGW cross-build |
| **Platforms** | x86-64 with AES-NI (VAES+AVX512F+AVX512VL CPUs get the separately compiled fast path) and arm64 with ARMv8 AES (Linux via HWCAP_AES; Apple silicon and Windows arm64 are assumed and not checked). Nothing else. |
| **Thread safety** | Not documented. oneshot() is const and leaves the object untouched (arm64 works on an internal copy), so one keyed object can serve concurrent oneshot calls. update/finalize/reset mutate state, so each thread needs its own copy. CPU detection is cached in function-local statics. |
| **Drop-in for the baseline** | no |

## Gotchas

- Defaults are all-zero. LeMac() uses a zero key, and finalize()/oneshot(data) use a zero nonce. A fixed nonce puts you in the paper's nonce-misuse bound (attacks at about 2^64 data), and a known key voids the MAC's guarantees entirely.
- finalize()/finalize_to() absorb the padding block and four zero blocks into the object's own state and do not reset it. Calling finalize() twice, or update() after it, silently gives a different tag, so reset() or use a fresh copy after each tag.
- Nonce length is checked only by assert(nonce.size() == 16). In release builds a shorter span makes _mm_loadu_si128/vld1q_u8 read past its end, while a wrong key size does throw std::runtime_error.
- Unsupported hardware aborts the process instead of throwing. x86 dispatch checks CPUID bits only (no XGETBV check that the OS enabled AVX-512 state). A CPU reporting VAES+AVX512F without AVX512VL maps to an unhandled 'vaes512' case and hits std::abort(), and Windows arm64 has no check at all.

## Known shortcomings

- Implements the corrected LeMac (passes upstream v1 test vectors), but its README compares only against SHA-1 (\~27x, derived), AES-128-ECB, clhash and xxh3 (LeMac \~16% slower than xxh3), not against a MAC incumbent such as GMAC/GHASH or AEGIS. Compiler for the main Zen 4 run unnamed. MAC only, not an AEAD.
- The default all-zero key and nonce (lemacsum, README example) gives no collision resistance per the paper, so it is not a SHA-1 substitute. finalize() mutates state with no reset; in release builds the nonce size is checked only by assert, so a short nonce reads out of bounds. Without AES hardware it calls std::abort (no fallback, no XGETBV check). The benchmark prints bytes/s x 1e-9 labelled 'GiB/s' (real \~71 GiB/s). v0.1, stale since 2025-06.

## Caveats and trade-offs

The README compares only against SHA1 (OpenSSL EVP), raw AES-128-ECB (OpenSSL), xxh3/xxh128 (xxhsum -b) and clhash. It has no comparison against a MAC incumbent such as GMAC/GHASH, Poly1305, HMAC or AEGIS. LeMac is a nonce-based MAC, so beating SHA1 (a bare digest) is not a like-for-like comparison and is best read as directional evidence of AES-NI-class speed. LeMac loses to xxh3 on Zen4 and to xxh on the Pi 5. The compiler is not named for the primary Zen4 run, and the baseline numbers come from outside tools rather than the repo's benchmark. This port implements the corrected LeMac from the ToSC 2025(1) corrigendum (DOI 10.46586/tosc.v2025.i1.623-628), not LeMac-0. src/lemac_aesni_impl.h and src/lemac_arm64_v8A.cpp use the extra RR message-schedule register and 'Four final rounds', as in upstream commit d035564f 'Fix LeMac specification, and rename erroneous version as LeMac-0' (Oct 2024). test/tests.cpp asserts the corrected 'LeMac' test vectors (for example 52282e853c9cfeb5537d33fb916a341f for the empty message) rather than the LeMac-0 ones. Arm64 on Windows has no runtime check for hardware support.

Requires AES-NI (amd64) or ARMv8 crypto extensions (arm64); no portable/software fallback yet (planned); ships a lemacsum CLI (sha256sum/xxhsum-style) plus a library API with reusable hasher objects to amortize \~5 KB init / \~2 KB finalize overhead; requires C++20.

## Maintenance

Stale. v0.1, last commit 2025-06-17, 16 merged PRs, 15 of them by the author (macOS arm64 support came from one outside contributor), and no issues ever filed. It is BSL-1.0, about 2.2k lines of source, tested under ASan/UBSan in CI, and implements the corrected LeMac (tests assert the upstream 'LeMac' vectors, not LeMac-0), so it is easy to vendor if you accept pinning your own fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Results on AMD zen4' section gives first-party numbers on a Ryzen 9 7950X3D: LeMac oneshot at 76.7 GiB/s (256 kB) and 74.3 GiB/s (1 MB), against SHA1 at about 2.8 GiB/s from `openssl speed -evp SHA1` on the same machine. The benchmark code is public (benchmark/benchmark.cpp) and flags can be read from CMakeLists.txt, but the compiler is not named for the Zen4 run and the baselines were measured with outside tools (openssl speed, xxhsum -b, clhash's own benchmark), so this stays at C.
- **Verifier notes:** LeMac is the corrected version from the corrigendum, not LeMac-0. The code matches upstream's fix (RR register, four final zero rounds) and the tests check the upstream 'LeMac' (v1) vectors. The corrigendum fixed a mismatch between the published message schedule and the MILP-analysed design (25 vs 26 active S-boxes), not a padding bug. The README compares against SHA1, AES-128-ECB, xxh3/xxh128 and clhash, never against a MAC incumbent. It wins against SHA1 (\~27x), AES-ECB and clhash, and loses to xxh3 by about 16%. The only wording fix is the clhash comparison.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pauldreik/lemac>
  - <https://github.com/pauldreik/lemac/blob/main/README.md>
  - <https://github.com/pauldreik/lemac/blob/main/include/lemac.h>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_aesni_impl.h>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_arm64_v8A.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/test/tests.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/benchmark/benchmark.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/CMakeLists.txt>
  - <https://github.com/pauldreik/lemac/commits/main>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/commit/d035564f>
  - <https://api.crossref.org/works/10.46586/tosc.v2025.i1.623-628>
- **Sources the enricher read:**
  - <https://github.com/pauldreik/lemac>
  - <https://github.com/pauldreik/lemac/blob/main/README.md>
  - <https://github.com/pauldreik/lemac/blob/main/include/lemac.h>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_aesni_impl.h>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_aesni.h>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_aesni_128.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_aesni_full.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/x86_capabilities.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/arm64_capabilities.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/lemac_arm64_v8A.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/src/main.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/CMakeLists.txt>
  - <https://github.com/pauldreik/lemac/blob/main/benchmark/benchmark.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/test/tests.cpp>
  - <https://github.com/pauldreik/lemac/blob/main/test/CMakeLists.txt>
  - <https://github.com/pauldreik/lemac/blob/main/vcpkg.json>
  - <https://github.com/pauldreik/lemac/blob/main/debian/changelog>
  - <https://github.com/pauldreik/lemac/blob/main/lemacsum.1>
  - <https://github.com/pauldreik/lemac/blob/main/.github/workflows/sanitizers.yml>
  - <https://github.com/pauldreik/lemac/blob/main/.github/workflows/ubuntu.yml>
  - <https://github.com/pauldreik/lemac/commits/main>
  - <https://github.com/pauldreik/lemac/pulls?q=is%3Apr>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/README.md>
  - <https://api.crossref.org/works/10.46586/tosc.v2024.i2.35-67>
  - <https://api.crossref.org/works/10.46586/tosc.v2025.i1.623-628>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/11619/11111>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/pauldreik/lemac`) · [data/wave7/enrich/raw/github_com_pauldreik_lemac.json](../../../data/wave7/enrich/raw/github_com_pauldreik_lemac.json) (enrichment confidence 0.8)

</details>
