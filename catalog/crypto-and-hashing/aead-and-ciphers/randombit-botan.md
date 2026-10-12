# Botan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Broad BSD-licensed C++20 crypto toolkit; maintainer reports faster small-message AES-128-GCM than OpenSSL 3.6.0 on one Skylake.

| | |
|---|---|
| **Beats** | OpenSSL 3.6.0 (openssl speed -evp aes-128-gcm) |
| **Claimed result** | Issue #969 small-message AES-128-GCM lead over OpenSSL is an artifact of per-message re-keying on the OpenSSL side only; the Zen 4 run with full flags has Botan about 2.7x slower at 16 B and OpenSSL about 1.65x faster at 16 KiB (derived). |
| **Workload** | AES-128/GCM encryption of small buffers (16, 64, 256 bytes), botan speed output compared with openssl speed -evp output on one Skylake desktop; same thread shows OpenSSL ahead for buffers above 4 KiB. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700K (Skylake) at 4 GHz, as named in the 2018 comments of the thread; the Mar 31 2026 comment says 'same machine as above comments' |
| **Compiler and flags** | Not stated for the 2026 runs. An Aug 28 2018 comment in the same thread on the same host used GCC 8.2 on Arch Linux with -march=skylake and 16 KiB buffers. |
| **Adoption** | 3.3k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/randombit/botan) · [benchmark](https://github.com/randombit/botan/issues/969) |

## Verdict

The maintainer's Mar 31 2026 comment on issue #969 compares Botan 3.11.1 `botan speed` with OpenSSL 3.6.0 `openssl speed -seconds 1 -evp aes-128-gcm` on an i7-6700K at 4 GHz (compiler and flags not stated): Botan is about 1.5x faster at 16 B and 64 B and 1.2x at 256 B, OpenSSL about 1.65x faster at 16 KiB (derived from page data), with the two tools timing different per-message work. The only fully specified run in the thread (Jul 22 2026, Botan 3.12.0 with gcc 15.3 against OpenSSL 4.0.1 with gcc 16, -march=znver4, Ryzen 9 7950X3D at 4.2 GHz) has Botan slower at every size, 54.84 vs 20.31 cycles/byte at 16 B and 0.38 vs 0.25 at 16 KiB.

## Use it when

- C++20 code bases that want one permissively licensed library for AEAD, TLS 1.3, X.509 and post-quantum schemes (ML-KEM, ML-DSA, SLH-DSA, FrodoKEM) behind a single modern C++ API, with C and Python bindings.
- Bulk AES-GCM on AVX-512 CPUs with Botan 3.11 or later: on a Ryzen 9 7950X3D the original poster measured 0.38 cycles/byte at 16 KiB, within about 1.5x of OpenSSL 4.0.1, down from 12x in 2017.
- Many messages under one long-lived key where AEAD is not the bottleneck (TLS records, file encryption), since key setup and associated data can be done once and only start()/finish() run per message.
- Targets without AES instructions that still need constant-time AES: the bitsliced and vperm fallbacks avoid table lookups.
- Builds that need a trimmed footprint: configure.py --minimized-build --enable-modules=... or the single-file amalgamation.

## Skip it when

- Maximum bulk AES-GCM throughput: OpenSSL is about 1.65x faster at 16 KiB on the maintainer's Skylake and about 1.5x on Zen 4 in the same thread, because Botan's GCM is not stitched.
- Tiny messages with a new nonce each: every start() precomputes a full keystream batch (256 bytes with AES-NI, 512 bytes with VAES), so a 16-byte message costs 16 or 32 AES blocks; the Zen 4 run measured 54.84 cycles/byte at 16 B against OpenSSL's 20.31.
- Projects that need OpenSSL's EVP/C ABI, provider model or engines; Botan's C FFI is its own API.
- Toolchains older than C++20: Botan 3 needs GCC 11.2+, Clang 14+, Visual C++ 2022, Xcode 15+ or NDK 26; Botan 2 reached end of life on 2025-01-01.

## How it is fast

AES and GHASH are separate kernels picked at run time by CPUID: AES uses VAES with AVX2 (8 blocks in flight), AES-NI or ARMv8 AES (4 blocks), POWER8, vperm SIMD, or a bitsliced constant-time fallback; GHASH uses CLMUL/PMULL with 4 or 8 precomputed powers of H, or AVX-512 VPCLMULQDQ with 16 precomputed powers (aggregated reduction; new GCM/GMAC AVX-512 paths landed in 3.11.0). GCM runs two passes over the buffer, CTR keystream then GHASH, rather than OpenSSL's stitched AES+GHASH loop, which the maintainer names as the remaining large-message gap. The small-message advantage claimed in issue #969 comes from per-message setup cost, not from the kernels (see gotchas).

## Compared with alternatives

Pick Botan over Mbed TLS when you run on desktop or server CPUs and want pipelined AES-NI/VAES and aggregated GHASH (Mbed TLS GCM does one block at a time), or over Crypto++ when you want a C++20 API with quarterly releases and post-quantum and TLS 1.3 support in the same library. For raw AEAD speed, a dedicated library such as chacha20poly1305-simd, hardware-rust-crypto or libaegis (if you can change cipher) is faster.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib built with configure.py, or a single-file amalgamation; also packaged by most distributions |
| **Dependencies** | none required; optional zlib, bzip2, lzma (compression API), SQLite (certificate store), PKCS#11, TPM 2.0 and ESDM modules |
| **Minimum toolchain** | C++20; tier-1 GCC 11.2+, Clang 14+, Visual C++ 2022; Xcode 15+ and NDK 26 on Apple and Android |
| **Platforms** | tier-1 Linux x86-64, aarch64 and ppc64le, Windows x86-64; tier-2 macOS, iOS, Android, Linux arm32 and x86-32, FreeBSD, MinGW; WebAssembly SIMD paths since 3.11.0; runtime CPUID dispatch for AES-NI, VAES, AVX-512 CLMUL, ARMv8 and POWER8 |
| **Thread safety** | Not documented in the files read; cipher mode objects hold per-message state (nonce, AD, GHASH accumulator), so use one object per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the claim: `botan speed` (src/cli/perf_sym.cpp) calls set_key() once outside the timer and times only start(iv) plus finish() per message, while OpenSSL 3.6.0 `openssl speed -evp aes-128-gcm` runs EVP_Update_loop_aead_enc for every GCM cipher, calling EVP_CipherInit_ex(ctx, NULL, NULL, key, aead_iv, -1) per message, which re-runs AES key expansion and CRYPTO_gcm128_init. The 16-256 B rows therefore charge OpenSSL a re-key per message that Botan never pays. OpenSSL 1.1.0e's speed tool instead streamed EVP_EncryptUpdate with no per-message init or tag, so the 'OpenSSL regressed since 1.1.0' small-message comparison in the thread partly reflects a change in what the tool measures.
- Per-message fixed cost: GCM start() calls CTR_BE::set_iv, whose seek(0) encrypts parallel_bytes() of keystream (parallelism x 16 B x ParallelismMult 4: 256 B on AES-NI, 512 B on VAES) even for a 16-byte message.
- Associated data must be set after set_key() and before start() and persists across messages; calling it after start() throws (GHASH::set_associated_data checks BOTAN_STATE_CHECK(!m_nonce)). The scc-tw/cryptobench-cpp adapter makes exactly this mistake, which is why every Botan 3.9.0 AES-GCM and ChaCha20-Poly1305 row in its result.json reads 'Encryption failed'; its CBC rows fail because the --minimized-build module list omits cbc. That suite therefore has no valid Botan AEAD data.
- The 3.11.0 release introduced a certificate verification bypass (CVE-2026-34580) fixed in 3.11.1, the version the maintainer benchmarked; 3.12.0 added maximum input length limits for ChaCha20Poly1305 and GHASH/GCM. Stay on the latest 3.x release.

## Known shortcomings

- Numbers match issue #969 but the win is maintainer-measured, small messages only, one Skylake, no compiler or flags for the 2026 run; the same comment has OpenSSL about 1.65x faster at 16 KiB (derived from page data), and a Jul 22 Zen 4 run with full flags has Botan about 2.7x slower at 16 B ('Factor 20.7' there is a typo). cryptobench-cpp Botan AES rows all errored 'Encryption failed'.
- Enricher: in issue #969 botan speed (perf_sym.cpp) sets the key once outside the timer and times only start+finish, while OpenSSL 3.6.0 speed -evp aes-128-gcm runs EVP_Update_loop_aead_enc, which calls EVP_CipherInit_ex with the key on every message, so OpenSSL is re-keyed per message and Botan is not; the small-message win is likely that artifact, and the fully specified Jul 22 Zen 4 run has Botan slower at every size. Each start() precomputes 256 B (AES-NI) or 512 B (VAES) of keystream even for 16 B messages. The cryptobench Botan adapter calls set_associated_data after start(), which throws, so all Botan AEAD rows read 'Encryption failed', and its CBC rows fail because the module list omits cbc.

## Caveats and trade-offs

The winning claim is the maintainer's own, covers only small messages and is disputed in the same thread (issue closed Mar 31 2026). The Mar 31 2026 comment text says Botan's AES/GCM is faster than 'OpenSSL 3.5' for small messages while its speed table is headed 'OpenSSL 3.6.0 (openssl speed -seconds 1 -evp aes-128-gcm)'; it gives no compiler, flags or build metadata, only 'same machine as above comments' (the i7-6700K at 4 GHz from the 2017 opening post and the 2018 comments). The same 2026 comment's 16 KiB figures still favour OpenSSL on Skylake: Botan 1.16 cycles/byte for AES-128/GCM against OpenSSL's 5724897.28k bytes/s, about 0.70 cycles/byte at 4 GHz (derived from page data), so OpenSSL is about 1.65x faster at 16 KiB. On Jul 22 2026 the original poster ran Botan 3.12.0 (gcc 15.3, -march=znver4, avx512_clmul, 'botan speed --msec=3000 --buf-size=N AES-128/GCM') against OpenSSL 4.0.1 (gcc-16, -march=znver4, 'openssl speed -evp aes-128-gcm') on a Ryzen 9 7950X3D at 4.2 GHz and got 54.84 cycles/byte (Botan) versus 20.31 (OpenSSL) at 16 B and 0.38 versus 0.25 at 16 KiB, concluding 'I cannot confirm that Botan is faster than OpenSSL, even for small messages'; the comment's 'Factor 20.7' is a typo for about 2.7 (54.84/20.31, derived from page data), and it says the large-message factor 'is now only 1.5'. The two tools use different timing windows. Historical numbers in the thread show OpenSSL 1.1.0e 12.2x faster than Botan 2.0.1 on AES-128/GCM (0.65 vs 7.94 cycles/byte) and 1.7 vs 7.34 on ChaCha20Poly1305, narrowed by Botan 2.8.0 to 2.2x and 2.4x (GCC 8.2, -march=skylake, 16 KiB). An independent harness, https://github.com/scc-tw/cryptobench-cpp (Botan 3.9.0 vs OpenSSL 3.6.0, result.json dated 2025-11-05 from a MacBook Air, CPU model not stated, median of 5 repetitions), shows Botan slower than OpenSSL on SHA-256 (471 vs 2787 MB/s at 16 KiB), SHA-512 at 16 KiB (741 vs 1636 MB/s), SHA3-256 and HMAC-SHA256, and marginally ahead only at 64 bytes on Poly1305 (393 vs 352 MB/s), BLAKE2b (228 vs 214 MB/s) and SHA-512 (297 vs 273 MB/s); every Botan AES-GCM and AES-CBC row in that file failed with 'Encryption failed', so it has no Botan AEAD data. [retier] botan speed keys once outside the timer; each start() precomputes 256-512 B of keystream; cryptobench Botan AEAD rows all 'Encryption failed' (set_associated_data after start) and CBC rows fail (module list omits cbc).

C++ library; hardware paths (AES-NI, CLMUL, AVX2, AVX-512) are chosen at run time, as the CPUID lines in the issue show. Per the same thread, large-message AES-GCM is slower than OpenSSL's assembly.

## Maintenance

Actively developed (3.13.0 released 2026-08-13, quarterly minor releases, last commit 2026-10-10, 3.3k stars), BSD-2-Clause and copyable; the small-message speed claim rests on one maintainer machine and an unequal tool comparison.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** Issue #969 holds the maintainer's own Mar 31 2026 botan speed vs 'openssl speed -seconds 1 -evp aes-128-gcm' output on the i7-6700K named earlier in the thread, with no compiler or flags for the 2026 run and no benchmark code beyond the two CLI tools; first-party numbers short of A. The fully specified run in the same thread (Jul 22 2026, Ryzen 9 7950X3D, gcc 16/15.3, -march=znver4, exact commands) is independent but shows Botan slower, so it cannot lift the winning claim.
- **Retiered** C to D: Lowered C to D: the only measurement favouring Botan (issue #969, small messages) times Botan with the key set once outside the timer against openssl speed, which re-keys on every message (EVP_Update_loop_aead_enc calls EVP_CipherInit_ex per message), so the win is a harness artifact; the one fully specified run (Jul 22, Zen 4) has Botan slower at every size, and the independent cryptobench rows all errored. No valid measurement supports a win; directional only.
- **Verifier notes:** Numbers on issue #969 match the record (three WebFetch reads of the thread). Shortcomings: maintainer-only small-message win on one Skylake with no compiler or flags for the 2026 run; OpenSSL still about 1.65x faster at 16 KiB on that machine; the only fully specified 2026 run (Zen 4, Jul 22) has Botan about 2.7x slower at 16 B and 1.5x slower at 16 KiB. Metadata checked on github.com: BSD-2-Clause, 3.3k stars, last commit 2026-10-10, latest release 3.13.0 (2026-08-13).
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-54 (wave 7); enricher w7 pair-010
- **Pages the verifier opened:**
  - <https://github.com/randombit/botan/issues/969>
  - <https://github.com/randombit/botan>
  - <https://github.com/randombit/botan/commits>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/HEAD/result.json>
- **Sources the enricher read:**
  - <https://github.com/randombit/botan>
  - <https://github.com/randombit/botan/issues/969>
  - <https://github.com/randombit/botan/issues?q=is%3Aissue%20GCM%20performance>
  - <https://github.com/randombit/botan/tree/master/src/cli>
  - <https://raw.githubusercontent.com/randombit/botan/master/readme.rst>
  - <https://raw.githubusercontent.com/randombit/botan/master/license.txt>
  - <https://raw.githubusercontent.com/randombit/botan/master/news.rst>
  - <https://raw.githubusercontent.com/randombit/botan/master/doc/support.rst>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/cli/perf.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/cli/perf.h>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/cli/speed.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/cli/perf_sym.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/modes/aead/aead.h>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/modes/aead/gcm/gcm.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/modes/aead/gcm/gcm.h>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/utils/ghash/ghash.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/utils/ghash/ghash.h>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/utils/ghash/ghash_cpu/ghash_cpu.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/utils/ghash/ghash_avx512_clmul/ghash_avx512_clmul.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/block_cipher.h>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes_ni/aes_ni.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes_vaes/aes_vaes.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes_armv8/aes_armv8.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes_power8/aes_power8.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/block/aes/aes_vperm/aes_vperm.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/utils/ghash/ghash_vperm/ghash_vperm.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/modes/aead/gcm_siv/gcm_siv.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/lib/stream/ctr/ctr.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/master/src/build-data/buildh.in>
  - <https://raw.githubusercontent.com/openssl/openssl/openssl-3.6.0/apps/speed.c>
  - <https://raw.githubusercontent.com/openssl/openssl/OpenSSL_1_1_0e/apps/speed.c>
  - <https://raw.githubusercontent.com/openssl/openssl/openssl-3.6.0/providers/implementations/ciphers/cipher_aes_gcm_hw_aesni.inc>
  - <https://raw.githubusercontent.com/openssl/openssl/openssl-3.6.0/providers/implementations/ciphers/cipher_aes_gcm.c>
  - <https://raw.githubusercontent.com/openssl/openssl/openssl-3.6.0/providers/implementations/include/prov/ciphercommon_gcm.h>
  - <https://github.com/openssl/openssl/tree/openssl-3.6.0/providers/implementations/ciphers>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/README.md>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/botan_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/benchmarks/symmetric_benchmarks.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchBotan.cmake>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/randombit/botan`) · [data/wave7/enrich/raw/github_com_randombit_botan.json](../../../data/wave7/enrich/raw/github_com_randombit_botan.json) (enrichment confidence 0.75)

</details>
