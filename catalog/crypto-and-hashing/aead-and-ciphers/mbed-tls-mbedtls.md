# Mbed TLS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 OR GPL-2.0-or-later` · 🟢 active

> Small-footprint C TLS library and PSA Crypto reference implementation; edges OpenSSL EVP only on 64-byte one-shot AEAD calls.

| | |
|---|---|
| **Beats** | OpenSSL 3.6.0 EVP one-shot AES-128-GCM, AES-256-GCM and ChaCha20-Poly1305 |
| **Claimed result** | Only at the 64-byte message size, means of 5 repetitions: AES-128-GCM 211.7 vs 163.9 MB/s (1.29x), AES-256-GCM 197.0 vs 160.9 MB/s (1.22x), ChaCha20-Poly1305 168.5 vs 135.3 MB/s (1.25x) (all derived from page data: bytes_per_second / 1e6). The ranking flips from 256 bytes up: OpenSSL is faster by 1.05x for AES-128-GCM at 256 B and by 4.7x at 16384 B (7840.4 vs 1683.0 MB/s), and OpenSSL wins every hash, HMAC and AES-256-CBC row where both libraries have data. |
| **Workload** | Google Benchmark of one-shot AEAD encryption of a 16-byte-AAD message, 64 to 16384 bytes, per call including key setup (Mbed TLS PSA psa_import_key plus psa_aead_encrypt; OpenSSL EVP_CIPHER_CTX_new, init, update, final, free), Mbed TLS 4.0.0 vs OpenSSL 3.6.0 built from source and statically linked in the scc-tw/cryptobench-cpp suite. |
| **Metric** | throughput |
| **Hardware** | MacBook Air host 'sccdeMacBook-Air.local' (Apple Silicon implied by the cache sizes; chip model not named), 8 logical CPUs, 64 KB L1D, 128 KB L1I, 4 MB L2 in the result.json context block; single run dated 2025-11-05. |
| **Compiler and flags** | README states -O3 -march=native -mtune=native -flto -funroll-loops -fomit-frame-pointer (PGO optional) applied to all libraries; result.json records no compiler name, version or PGO state. Mbed TLS 4.0.0 (tag v4.0.0) is built with its default configuration, static, via cmake/FetchMbedTLS.cmake. |
| **Adoption** | 7.0k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/Mbed-TLS/mbedtls) · [benchmark](https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json) |

## Verdict

A third-party Google Benchmark suite (scc-tw/cryptobench-cpp, one run on 2025-11-05 on an Apple Silicon MacBook Air, compiler version not recorded, -O3 -march=native -flto) timed one-shot AEAD with per-call key setup and 16-byte AAD: Mbed TLS 4.0.0 beat statically linked OpenSSL 3.6.0 only at 64-byte messages (AES-128-GCM 211.7 vs 163.9 MB/s, AES-256-GCM 197.0 vs 160.9, ChaCha20-Poly1305 168.5 vs 135.3; means of 5 repetitions). OpenSSL was ahead from 256 bytes up and 4.7x faster at 16 KiB.

## Use it when

- Microcontroller and other embedded targets where code size, RAM use, C99 portability and a PSA Crypto API (TF-M, secure elements, PSA drivers) matter more than AEAD throughput.
- Per-message AEAD with a fresh key on every call (import, encrypt one 64-byte record, destroy): the only measured case where it beat OpenSSL 3.6.0, by 1.22x to 1.29x.
- Applications already built on the PSA Cryptography API that want a reference implementation with hardware drivers able to slot in under the same calls.
- Products that need an LTS branch with API/ABI stability (mbedtls-3.6 until March 2027, mbedtls-4.1 until March 2029) and Apache-2.0 licensing.

## Skip it when

- Bulk AEAD on desktop or server CPUs: in the same run OpenSSL was 1.7x to 4.7x faster for AES-GCM from 1 KiB up (7840 vs 1683 MB/s at 16 KiB) and 2.5x to 3.8x faster for ChaCha20-Poly1305; the maintainers traced the GCM gap to unpipelined AES-NI and per-block GHASH reduction in issue #1189.
- Hashing and HMAC throughput in the default build: OpenSSL won every SHA-256, SHA-512, SHA3 and HMAC row in the cited run, by 5.9x to 7.5x for SHA-256 at 1 KiB and up, partly because the default config leaves MBEDTLS_SHA256_USE_ARMV8_A_CRYPTO_IF_PRESENT and MBEDTLS_SHA512_USE_A64_CRYPTO_IF_PRESENT off, so the Apple Silicon run hashed in portable C.
- Multithreaded use of the default build: MBEDTLS_THREADING_C is off by default and the config says the PSA subsystem is then not thread-safe.
- Hot paths that encrypt many small records under one key through PSA: psa_aead_encrypt re-runs AEAD setup (key schedule and GCM H) on every call, a known overhead (issue #10775 shows about 50% throughput loss on an embedded target at 1000-byte frames).
- Targets without unaligned access (Xtensa, Cortex-M0/M0+/M23, PowerPC) if GCM speed matters: open issue #9476 reports the table GCM regressing to 258.7 cycles/byte from 75.88 on Xtensa.

## How it is fast

It is not built for peak throughput. GCM processes one 16-byte block at a time: one AES block encryption (AES-NI on x86, Armv8 Crypto Extensions via MBEDTLS_AESCE_C, otherwise table AES) followed by one GHASH multiply (PCLMULQDQ or PMULL with immediate reduction, or a 4-bit table), with no multi-block pipelining, stitched AES+GHASH or aggregated reduction. Its small-message edge in the benchmark comes from cheap key setup: on the accelerated paths gcm_gen_table() stores only H and builds no table of powers of H, so per-call setup costs less than OpenSSL's EVP context creation, cipher fetch and GHASH precomputation. ChaCha20 was scalar C in 4.0.0; a NEON 2-6-block implementation (default 3 blocks on AArch64, 2x to 2.7x faster per the ChangeLog) shipped in 4.1.0.

## Compared with alternatives

Pick Mbed TLS over Botan, Crypto++ or chacha20poly1305-simd only when footprint, C99 portability, PSA API compatibility or an LTS branch matter more than throughput; for bulk AES-GCM or ChaCha20-Poly1305 speed, hardware-rust-crypto, chacha20poly1305-simd or OpenSSL itself are faster, and libaegis is faster still if you can change cipher.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; libtfpsacrypto, libmbedx509, libmbedtls) |
| **Dependencies** | none at run time (libc only); building from a git checkout needs the framework and tf-psa-crypto submodules, Python 3.8+ and Perl to generate source files (release tarballs include them) |
| **Minimum toolchain** | C99, CMake 3.20.2+; tested with GCC 5.4, Clang 3.8, Arm Compiler 6 and Visual Studio 2017. AESCE needs Clang 4.0, GCC 6.0, armclang 6.6 or MSVC 2019 16.11.2 on aarch64. |
| **Platforms** | any C99 target; AES-NI and PCLMUL on x86 and x86-64, Armv8 Crypto Extensions on aarch64 and 32-bit Arm, NEON ChaCha20 from 4.1.0; portable C fallback elsewhere |
| **Thread safety** | Not thread-safe by default: enable MBEDTLS_THREADING_C with MBEDTLS_THREADING_PTHREAD or MBEDTLS_THREADING_ALT before calling PSA functions from more than one thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured small-message win is a property of the harness, not of the cipher: both adapters in scc-tw/cryptobench-cpp redo all key setup per message (Mbed TLS psa_import_key plus a heap std::vector and two memcpy per call; OpenSSL EVP_CIPHER_CTX_new, an implicit EVP_aes_128_gcm() fetch, two init calls and free), and the loop never checks the output against a known answer.
- The ChaCha20-Poly1305 rows measured Mbed TLS 4.0.0, which used scalar ChaCha20; 4.1.0 (2026-03-31) added NEON ChaCha20 (2x to 2.7x on AArch64), so those rows understate current Mbed TLS on the Apple Silicon host.
- AESCE runtime detection works only on Linux; on macOS and other non-Linux systems a build with MBEDTLS_AESCE_C assumes the CPU has Armv8 Crypto Extensions. TF-PSA-Crypto 1.0 (shipped in Mbed TLS 4.0.0) produced wrong GCM tags with GCC 10 to 14.2 at -O3 when neither AES-NI nor AESCE was used (fixed in 1.1.0, issue #665).
- SECURITY.md recommends -O2 or -Os; the benchmark built with -O3 -funroll-loops -flto -march=native, which the project calls less scrutinized for timing side channels. Release 4.2.0 fixed 11 CVEs in the TLS layer and its TF-PSA-Crypto 1.2.0 fixed 5 more (including CVE-2026-50584, a ChaCha20 32-bit counter wrap that reused keystream), so track the latest maintained branch.

## Known shortcomings

- Wins only at 64-byte messages (1.22-1.29x); OpenSSL is faster from 256 B up (4.66x at 16384 B) and on every hash, HMAC and CBC row. Harness pays EVP ctx new/init/free per call; single laptop run under load average 3.6-4.3, no CPU model or compiler version, 0-star benchmark repo.
- Enricher: cryptobench redoes key setup on every call for both libraries and never checks output; Mbed TLS GCM handles one block per step (single AES block then single GHASH multiply, issue #1189), so OpenSSL is 4.7x faster at 16 KiB; the ChaCha20-Poly1305 rows are stale (4.0.0 scalar, 4.1.0 added NEON, 2x to 2.7x on AArch64); SHA-256/512 Armv8 acceleration is off in the default config, explaining the hash losses; the default build is not thread-safe (MBEDTLS_THREADING_C off).

## Caveats and trade-offs

Harvested shootout row, not a claim Mbed TLS makes: the README and ChangeLog contain no comparison with OpenSSL, and Mbed TLS is the slower library for every hash, HMAC and CBC row and for AEAD at 256 B and above (OpenSSL 1.05x faster for AES-128-GCM at 256 B, 4.66x at 16384 B, 7840.4 vs 1683.0 MB/s; ChaCha20-Poly1305 3.79x at 16384 B, derived from page data). The benchmark owner's repo (scc-tw/cryptobench-cpp, MIT) has 0 stars and 39 commits and one local laptop run (2025-11-05) with no CPU model or compiler version; the context block shows a load average of 3.6 to 4.3 on the 8-CPU host during the run, so the machine was not idle. The 64-byte advantage reflects per-call overhead rather than cipher speed: src/adapters/openssl_adapter.cpp calls EVP_CIPHER_CTX_new, two EVP_EncryptInit_ex calls with an implicit EVP_aes_128_gcm() fetch, and EVP_CIPHER_CTX_free on every message, while src/adapters/mbedtls_adapter.cpp runs psa_import_key, allocates a std::vector, copies the output with two memcpy calls and destroys the key per message. In the same file every OpenSSL public-key row and Botan's AES-GCM, ChaCha20-Poly1305 and AES-256-CBC rows are error rows ('Key generation failed', 'Encryption failed' and similar), so OpenSSL is the only peer for this comparison. A wolfSSL vendor benchmark (WebSearch snippet only, page not opened) reports wolfCrypt well ahead of Mbed TLS 3.6.6; no source reached shows Mbed TLS ahead of OpenSSL on bulk throughput. [retier] cryptobench re-keys per call, no output check; GCM one block per step (#1189) so OpenSSL 4.7x faster at 16 KiB; ChaCha20-Poly1305 rows measured 4.0.0 scalar code (4.1.0 NEON 2-2.7x faster on AArch64); SHA-256/512 Armv8 acceleration off by default; default build not thread-safe (MBEDTLS_THREADING_C off); single laptop run under load, no CPU model or compiler version.

Mbed TLS targets small code size and portability, not peak throughput. The 64-byte win comes with a PSA API that imports a key per call; for messages of 1 KB and up OpenSSL is 1.7x to 4.7x faster for GCM, 2.5x to 3.8x faster for ChaCha20-Poly1305 and 5.7x to 7.5x faster for SHA-256 in the same run (all derived from page data).

## Maintenance

Actively maintained under Trusted Firmware (4.2.0 released 2026-07-07, 4.1 LTS supported until March 2029, 3.6 LTS until March 2027), Apache-2.0 OR GPL-2.0-or-later, 7.0k stars; copyable, but treat it as a portability and footprint choice, not a speed upgrade over OpenSSL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** result.json in scc-tw/cryptobench-cpp contains the BM_MbedTLS_\* and BM_OpenSSL_\* rows with the quoted 64-byte means (211.66 vs 163.95, 197.00 vs 160.93, 168.53 vs 135.30 MB/s) and the reversal from 256 B up; benchmark code and README flags are public, but no compiler name or version and no CPU model are recorded, and the 0-star suite is not a well-known independent shootout, so C.
- **Verifier notes:** All quoted numbers and the flip at 256 B confirmed in result.json; adapter code confirms the per-call EVP context setup that explains OpenSSL's 64-byte loss. Shortcomings: win only at 64-byte messages in a per-call setup-dominated harness, OpenSSL faster at every larger size and for every hash, HMAC and CBC row, single noisy laptop run with no CPU model or compiler version, 0-star benchmark repo. Mbed TLS metadata checked: 7.0k stars, Apache-2.0 OR GPL-2.0-or-later, last commit 2026-10-07 on development, not archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 7); enricher w7 pair-010
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/README.md>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/openssl_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/mbedtls_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/benchmarks/symmetric_benchmarks.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchMbedTLS.cmake>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://github.com/Mbed-TLS/mbedtls>
  - <https://github.com/Mbed-TLS/mbedtls/commits>
- **Sources the enricher read:**
  - <https://github.com/Mbed-TLS/mbedtls>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/README.md>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/BRANCHES.md>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/SECURITY.md>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/ChangeLog>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/.gitmodules>
  - <https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/include/mbedtls/mbedtls_config.h>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/README.md>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/ChangeLog>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/include/psa/crypto_config.h>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/gcm.c>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/aesce.c>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/aesni.c>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/aes.c>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/chacha20.c>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/chacha20_neon.h>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/v1.0.0/drivers/builtin/src/chacha20_neon.h>
  - <https://raw.githubusercontent.com/Mbed-TLS/TF-PSA-Crypto/development/drivers/builtin/src/poly1305.c>
  - <https://github.com/Mbed-TLS/mbedtls/issues?q=is%3Aissue%20gcm%20performance>
  - <https://github.com/Mbed-TLS/mbedtls/issues/1189>
  - <https://github.com/Mbed-TLS/mbedtls/issues/9476>
  - <https://github.com/Mbed-TLS/mbedtls/issues/10775>
  - <https://github.com/h2o/picotls/pull/485>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/README.md>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/benchmarks/symmetric_benchmarks.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/mbedtls_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/openssl_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchMbedTLS.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchOpenSSL.cmake>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mbed-tls/mbedtls`) · [data/wave7/enrich/raw/github_com_mbed_tls_mbedtls.json](../../../data/wave7/enrich/raw/github_com_mbed_tls_mbedtls.json) (enrichment confidence 0.75)

</details>
