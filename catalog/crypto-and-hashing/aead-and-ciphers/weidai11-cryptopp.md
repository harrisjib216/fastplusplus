# Crypto++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Broad C++ crypto class library; a 2013 hobby benchmark had its CAST-128-CBC about 1.3-1.4x faster than libgcrypt.

| | |
|---|---|
| **Beats** | libgcrypt (CAST5 in CBC mode), also Botan 1.10 (CAST_128) |
| **Claimed result** | README sample output: Crypto++ CAST128 101.73 MB/s encrypt and 109.73 MB/s decrypt versus libgcrypt 75.70 and 76.00 MB/s (about 1.34x and 1.44x, derived from page data) and Botan 96.69 and 97.17 MB/s (about 1.05x and 1.13x, derived from page data); the Linux kernel AF_ALG path was faster than all three (135.10 and 315.98 MB/s). |
| **Workload** | CAST-128 (CAST5) encryption and decryption of a 4096-byte buffer, 50000 rounds per implementation, timed with clock(), each round re-creating the cipher object and key schedule. |
| **Metric** | throughput |
| **Compiler and flags** | g++ -O2 -Wall -march=corei7-avx (from the Makefile); compiler and library versions not stated; Botan 1.10 headers |
| **Adoption** | 5.5k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/weidai11/cryptopp) · [benchmark](https://github.com/ketotek/crypto-bench) |

## Verdict

ketotek/crypto-bench, a May 2013 third-party hobby harness, CBC-encrypts and decrypts a 4096-byte buffer 50000 times per library, re-creating the cipher and key schedule every round. It was built with g++ -O2 -march=corei7-avx against system libraries of unstated versions (Botan 1.10) on an unstated CPU. Its sample output, which is CPU time from clock() in MiB/s, has Crypto++ CAST-128 at 101.73/109.73 against libgcrypt CAST5 at 75.70/76.00 (about 1.34x/1.44x, derived from page data) and Botan CAST_128, run as a bare ECB block loop, at 96.69/97.17. The Linux AF_ALG row (135.10/315.98) is not comparable: it keys once outside the loop and passes an 8-byte key to setsockopt, so it runs the 12-round reduced CAST5 that RFC 2144 specifies for keys of 80 bits or less, against 16 rounds for the three libraries.

## Use it when

- An existing C++ codebase that needs one permissively licensed library (BSL-1.0 compilation, public-domain files) with an unusually wide algorithm set, including legacy ciphers (CAST-128, Blowfish, IDEA, Camellia, ARIA, SEED, SM4) for reading old formats or talking to old peers.
- Old or unusual toolchains and targets. The 8.9 Readme lists support from Visual Studio 2003, GCC 3.3, Sun Studio and IBM XL through 2023 compilers, and Install.txt only asks for C++03 with RTTI and exceptions. In-core code exists for x86, x64, x32, ARM-32, Aarch64 and POWER8.
- Streaming transformations where the Source/Filter/Sink pipeline is convenient, e.g. encrypt-and-encode or hash-while-copying with little glue code.
- x86-64 servers with AES-NI and CLMUL, where AES and GCM dispatch to hardware code. Run the built-in `cryptest.exe b` benchmark (bench2.cpp covers AES/GCM with 2K and 64K tables, AES/CTR and CAST-128/CTR) against your current library before switching for speed.

## Skip it when

- As a throughput upgrade over OpenSSL for AES-GCM, ChaCha20-Poly1305 or SHA-2. No current evidence shows Crypto++ ahead, and the only cross-library claim catalogued here is a 2013 CAST-128 result against libgcrypt.
- Apple Silicon with the 8.9.0 release. Issue #1373 found that HasAES/HasSHA2/PMULL/NEON returned false on every Apple chip except a plain 'Apple M1', so the hardware paths were never selected. On an M1 Max the fix took AES-CBC from 252 to 866 MB/s and SHA-256 from 318 to 2071 MB/s.
- Projects that need timely security releases. 8.9.0 (2023-10-01) is still the latest release, and fixes since then exist only on master: ChaCha SIMD carry, Ed25519 S &gt;= L, OAEP underflow, DEFLATE HLIT. Release request #1345 has no maintainer reply, and issues #1247 (Marvin attack), #1249 (ModularSquareRoot DoS) and #1364/#1369 (zero-length AEAD tags accepted) are open.
- FIPS 140 requirements. The Readme says the validated DLL moved to the CMVP historical list and should no longer be used.
- New designs that would use CAST-128. Crypto++ itself files CAST-128 under 'insecure or obsolescent algorithms retained for backwards compatibility'.

## How it is fast

The CAST-128 code behind the measured numbers is a plain table-driven implementation: four 256-entry S-box lookups per round, one 8-byte block at a time, and 12 rounds for keys of 80 bits or less (cast.cpp). The 2013 margin over libgcrypt therefore reflects both libraries' code and call overhead at that time, not a special technique. CAST-128 also gets no multi-block SIMD path, because adv_simd.h says the library stopped using the 64-bit-block AdvancedProcessBlocks templates in July 2020. Elsewhere, Crypto++'s speed comes from ISA-specific translation units (AES-NI with SSE4.1, CLMUL with SSSE3 for GCM, AVX2 for ChaCha, SHA-NI, ARMv8 crypto/PMULL, POWER8) that are selected by runtime CPU detection. AdvancedProcessBlocks templates process 4 or 6 128-bit blocks at once for parallelisable modes such as CTR and CBC decryption, and GCM falls back to 2K or 64K GHASH tables without CLMUL.

## Compared with alternatives

Pick Crypto++ over Botan or Mbed TLS only when you need its unusually wide or legacy algorithm catalogue, a C++03-era toolchain, or the pipeline API. For AEAD speed, the catalogued siblings (Botan's GCM vs OpenSSL at small sizes, libaegis or HiAE if you can change the cipher) have stronger and newer evidence than this 2013 CAST-128 result.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (GNUmakefile builds libcryptopp.a / libcryptopp.so; MSVC solution for Windows). CMake and Autotools builds are unofficial side projects. vcpkg port available. |
| **Dependencies** | none |
| **Minimum toolchain** | C++03 with 64-bit words, RTTI and exceptions; GNU Make 3.81+. The 8.9 Readme lists GCC 3.3-13.1, Clang 2.9-14, Apple Clang 4.3-12, VS2003-2022, Intel 9-16, Sun Studio 12u1-12.7 and IBM XL 10-14. |
| **Platforms** | x86, x86-64, x32, ARM-32/Aarch32, Aarch64, POWER8, with runtime CPU feature detection; portable C++ fallback elsewhere |
| **Thread safety** | Thread-safe at the class level (Readme): separate objects can be used concurrently, but you must synchronize when several threads use one Crypto++ object. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the catalogued numbers (ketotek/crypto-bench). No library's output is checked. Crypto++ uses its own 0x01 key and 0x73 plaintext, while Botan and libgcrypt read the base-class key and in arrays, which are never initialized (CryptoppTest declares a shadowing key member). Crypto++'s encrypt_round builds std::string from the uninitialized out buffer with a strlen-style constructor, which is undefined behaviour and only works because fresh heap memory is zero. The AF_ALG row passes an 8-byte key (12-round reduced CAST5) and keys once. The libgcrypt baseline is stale: libgcrypt 1.6.0 (2013-12-16) 'improved performance of most cipher algorithms' and 1.9.0 (2021-01-19) made CAST5 '40% to 70% faster', enough to cover the 1.34x gap if that speedup applies to this CBC path (derived from page data). The counter-evidence is also flawed: scc-tw/cryptobench-cpp puts Crypto++ 8.9.0 at a flat 42-78 MB/s at 16 KiB for every algorithm on a MacBook Air, including portable BLAKE2b (78.2 vs Botan 1337.3) and SHA3-256 (74.4 vs Botan 601.4), which points to a build or dispatch problem (see issue #1373) rather than a fair comparison.
- Zero-length authentication tags are accepted (issue #1364, open, PR #1365 unmerged): AuthenticatedDecryptionFilter with truncatedDigestSize 0 for GCM and ChaCha20Poly1305 DecryptAndVerify with macSize 0 report modified ciphertext as valid. Enforce a minimum tag length yourself.
- The 8.9.0 release has two SIMD bugs that are fixed only on master. ChaCha on SSE2, NEON and Altivec (AVX2 was correct) gave a silent 1-bit keystream error when the 64-bit feed-forward add carried from word 12 into word 13 (issue #1362, fixed 2026-07-13). Apple chips other than a plain 'Apple M1' never selected hardware AES/SHA/PMULL (issue #1373, fixed 2026-10-01).
- Pipeline ownership: an object passed by pointer (new StreamTransformationFilter(..., new StringSink(s))) is owned and deleted by the receiver, while objects passed by reference stay caller-owned. Builds that do not use the GNUmakefile must define NDEBUG and keep cryptlib.cpp, cpu.cpp and integer.cpp first in the build and link order (Readme).

## Known shortcomings

- ketotek README numbers match but the harness is a 2013 hobby benchmark with no CPU, MiB/s labelled MB/s, Botan run in ECB while the others run CBC, Crypto++ decrypt that does not round-trip and leaked libgcrypt handles; the win is off-baseline (libgcrypt CAST5). Modern data has Crypto++ slower than OpenSSL.
- Enricher: the ketotek/crypto-bench harness has no output check; Botan and libgcrypt run with never-initialized base-class key and input buffers (CryptoppTest shadows key) and Crypto++ builds its std::string from an uninitialized output with strlen (undefined behaviour); the AF_ALG row uses an 8-byte key (12-round reduced CAST5) keyed once; the libgcrypt baseline (pre-1.6.0) is stale and 1.9.0's CAST5 speedup (40-70%) covers the 1.34x gap. Counter-evidence is flawed too: scc-tw/cryptobench-cpp has Crypto++ 8.9.0 flat at 42-78 MB/s for every algorithm because 8.9.0 never picks hardware AES/SHA2/PMULL/NEON on Apple chips other than plain M1 (#1373). No release since 8.9.0 (2023-10-01); open #1364/#1369 (zero-length AEAD tag accepted), #1247 Marvin, #1249 DoS; ChaCha SIMD carry bug #1362 fixed on master only; CAST-128 listed by Crypto++ itself as obsolescent.

## Caveats and trade-offs

Weak, old and third-party: a May 2013 hobby repository (2 stars, 8 commits, no licence shown) with a sample output only, no CPU model and no library versions except Botan 1.10 (from the Makefile). The 'MB/s' column is MiB/s (the driver divides by 1024 twice) and is timed with clock(), i.e. CPU time, over 50000 rounds of a 4096-byte buffer. The three library implementations are not like for like: Botan is called as a bare encrypt_n/decrypt_n block loop (ECB, no chaining mode) while Crypto++ and libgcrypt run CBC; every round of every library repeats object creation and key setup; libgcrypt handles are opened every round and never closed; Crypto++ goes through StringSource, StreamTransformationFilter and StringSink with heap allocation (the sample shows 412 MB of malloc traffic for encrypt). Crypto++'s encrypt_round builds its output string from the 4096-byte 'out' buffer with a strlen-style constructor and never copies the ciphertext back, so its decrypt pass decrypts an untouched buffer rather than a real round trip (the timed work is still 4096 bytes of CBC decryption). The Linux kernel AF_ALG path beat all three (135.10 and 315.98 MB/s). CAST-128 is a legacy cipher, and libgcrypt is not the category's usual baseline (OpenSSL), so the result says little about AES or SHA performance. Current independent data points the other way: https://github.com/scc-tw/cryptobench-cpp (Crypto++ 8.9.0 vs OpenSSL 3.6.0, result.json dated 2025-11-05 from a MacBook Air, CPU model not stated, median of 5 repetitions) has Crypto++ far behind OpenSSL, e.g. AES-128-GCM 54 vs 7880 MB/s and SHA-256 71 vs 2787 MB/s at 16 KiB, probably because ARM crypto instructions were not used (the same harness's Botan AES rows all failed, so treat it as a rough data point); and the 2014 gist https://gist.github.com/aalness/577c7a6da1e669a07db9 (no CPU or compiler stated) has Crypto++ SHA-256 slower than OpenSSL (286.192 ms vs 162.157 ms for 300000 32-byte hashes; 19195 ms vs 17554.8 ms at 8192 bytes), though about 2x faster than libsecp256k1's own SHA-256. The Crypto++ repository itself publishes no cross-library comparison (its README only lists benchmarks as a feature). License: the compilation is BSL-1.0 and individual files are placed in the public domain (some 32-bit ARM files are CRYPTOGAMS, BSD-style). [retier] Harness UB and unchecked output; libgcrypt baseline pre-1.6.0; counter-evidence from scc-tw/cryptobench-cpp is also flawed (8.9.0 never selects hardware crypto on Apple chips other than plain M1, #1373). No release since 8.9.0 (2023-10-01); open #1364/#1369, #1247, #1249; CAST-128 obsolescent per Crypto++.

Large C++ class library of cryptographic schemes under the Boost Software License 1.0 for the compilation (License.txt), individual files placed in the public domain, some CRYPTOGAMS code under a BSD-style licence; the API is filter and pipeline based.

## Maintenance

Master is active (last commit 2026-10-02) and the code is copyable (BSL-1.0 compilation, public-domain files), but the last release is still 8.9.0 (2023-10-01), cryptopp.com's certificates expired in April 2026 (#1347), and the cryptopp-modern fork (BSL-1.0, release 2026.9.1) is the packaged route to post-8.9.0 fixes and CVE patches (CVE-2023-50980, CVE-2023-50981, CVE-2024-28285). The catalogued speedup rests on a flawed 2013 CAST-128 harness against a since-accelerated libgcrypt (see gotchas), so treat it as historical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** ketotek/crypto-bench is a 2013 third-party hobby harness with public code (crypto_bench.cpp, cryptopp.cpp, gcrypt.cpp, botan.cpp) and Makefile flags (-O2 -march=corei7-avx) but no compiler version, library versions beyond Botan 1.10, or CPU model, and only a README sample output; not A, not a well-known suite, so C.
- **Retiered** C to D: The only harness behind the numbers (ketotek/crypto-bench) performs no output check, feeds never-initialized key and input buffers to Botan and libgcrypt and reads Crypto++'s output through strlen on an uninitialized buffer (undefined behaviour), keys the AF_ALG row with a reduced 8-byte CAST5 key, and its pre-1.6.0 libgcrypt baseline is stale by enough (1.9.0 CAST5 40-70% faster) to erase the 1.34x gap; no valid measurement remains, so directional only.
- **Verifier notes:** README numbers match the record exactly (Crypto++ 101.73/109.73 vs libgcrypt 75.70/76.00 and Botan 96.69/97.17 MB/s); ratios recomputed. Shortcomings: off-baseline (libgcrypt CAST5, not OpenSSL), 2013 hobby harness with no CPU or versions, Botan run in ECB vs CBC, every round re-keys, and modern data shows Crypto++ slower than OpenSSL on AES-GCM and SHA-256. Metadata on github.com: 5.5k stars, last commit 2026-10-02 (active), latest version 8.9.0 (Oct 2023), BSL-1.0 compilation licence from License.txt.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 7); enricher w7 pair-012
- **Pages the verifier opened:**
  - <https://github.com/ketotek/crypto-bench>
  - <https://github.com/ketotek/crypto-bench/commits>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/crypto_bench.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/cryptopp.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/gcrypt.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/botan.cpp>
  - <https://github.com/weidai11/cryptopp>
  - <https://github.com/weidai11/cryptopp/commits>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/License.txt>
  - <https://gist.github.com/aalness/577c7a6da1e669a07db9>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/result.json>
- **Sources the enricher read:**
  - <https://github.com/weidai11/cryptopp>
  - <https://github.com/weidai11/cryptopp/commits>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/Readme.txt>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/README.md>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/License.txt>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/Install.txt>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/Security.md>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/cast.cpp>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/cast.h>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/modes.cpp>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/adv_simd.h>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/cpu.cpp>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/GNUmakefile>
  - <https://raw.githubusercontent.com/weidai11/cryptopp/HEAD/bench2.cpp>
  - <https://github.com/weidai11/cryptopp/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/weidai11/cryptopp/issues/1362>
  - <https://github.com/weidai11/cryptopp/issues/1364>
  - <https://github.com/weidai11/cryptopp/issues/1345>
  - <https://github.com/weidai11/cryptopp/issues/1373>
  - <https://github.com/cryptopp-modern/cryptopp-modern>
  - <https://github.com/ketotek/crypto-bench>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/crypto_bench.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/crypto_bench.h>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/cryptopp.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/cryptopp.h>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/gcrypt.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/gcrypt.h>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/botan.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/botan.h>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/af_alg.cpp>
  - <https://raw.githubusercontent.com/ketotek/crypto-bench/HEAD/af_alg.h>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/master/NEWS>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/cmake/FetchCryptopp.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/src/adapters/cryptopp_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/src/benchmarks/hash_benchmarks.cpp>
  - https://www.cryptopp.com/benchmarks.html (attempted; host did not resolve)
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/weidai11/cryptopp`) · [data/wave7/enrich/raw/github_com_weidai11_cryptopp.json](../../../data/wave7/enrich/raw/github_com_weidai11_cryptopp.json) (enrichment confidence 0.65)

</details>
