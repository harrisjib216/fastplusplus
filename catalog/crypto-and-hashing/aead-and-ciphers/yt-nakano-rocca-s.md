# ROCCA-S

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟡 stale

> KDDI's reference C code for Rocca-S, a 256-bit-key AES-round AEAD; \~1.9-2.9x OpenSSL AES-128-GCM encryption throughput.

| | |
|---|---|
| **Beats** | OpenSSL AES-128-GCM |
| **Claimed result** | At 64 KB on Apple M5 Max, ROCCA-S AEAD runs at 208.1 Gbps encryption and 140.4 Gbps decryption, against OpenSSL AES-128-GCM's 70.8 and 70.2 Gbps (\~2.9x encryption, \~2.0x decryption, derived from page data). Its keystream path runs at 228.8 Gbps against OpenSSL AES-128-CTR's 159.6 (\~1.4x, derived from page data). On Zen 4 (Ryzen 7 7700 locked at 3.8 GHz), ROCCA-S does 174.6 Gbps encryption and 92.3 Gbps decryption, against AES-128-GCM's 92.7 and 92.9 Gbps. That is \~1.9x on encryption, but decryption is at parity, about 0.99x (derived from page data; the Zen 4 GCM figures appear only in the README's bar chart). |
| **Workload** | AEAD encryption and decryption throughput at 64 KB messages, with 48-byte associated data plus the tag, sweeping sizes from 16 B to 64 KB. A separate keystream-only mode is compared against OpenSSL AES-128-CTR. Buffers are 4096-byte aligned. Measured on Apple M5 Max and AMD Ryzen 7 7700 (Zen 4). |
| **Metric** | throughput |
| **Hardware** | Apple Silicon M5 Max (macOS 26); AMD Ryzen 7 7700 (Zen 4) at fixed 3.8GHz, performance governor, boost disabled |
| **Compiler and flags** | M5: Apple clang 21.0.0, -O3 -mcpu=native (the Makefile uses -mcpu=native on arm64), with OpenSSL 3.6.4. Zen 4: clang 21.1.8, -O3 -march=native, with OpenSSL 3.5.5. All builds also use -std=c99. |
| **Adoption** | 2 stars. KDDI's official reference implementation of Rocca-S (ESORICS 2023: 'An Ultra-High Throughput AES-based Authenticated Encryption Scheme for 6G'). The spec is IETF individual draft draft-nakano-rocca-s-06 (2026-01-28). It was presented at CFRG IETF-115, was never adopted, and expired on 2026-08-01. |
| **Last commit** | 2025-03-19 |
| **Links** | [repository](https://github.com/yt-nakano/rocca-s) · [benchmark](https://github.com/hiae-aead/benchmarks) |

## Verdict

jedisct1's hiae-aead/benchmarks harness ran a reformatted copy of this reference, with an added ARM-crypto backend, against OpenSSL EVP AES-128-GCM at 64 KB with 48 B of AD and the tag included. On an M5 Max (Apple clang 21.0.0, OpenSSL 3.6.4, -O3 -mcpu=native, median of three passes) it reached 208.1/140.4 Gbps encrypt/decrypt vs 70.8/70.2 (\~2.9x/2.0x), with keystream 228.8 vs AES-128-CTR 159.6. On a Ryzen 7 7700 locked at 3.8 GHz (clang 21.1.8, OpenSSL 3.5.5, -O3 -march=native) it reached 174.6/92.3 vs 92.7/92.9, so \~1.9x on encryption and parity on decryption. Note that this pits 256-bit-key Rocca-S against AES-128, not AES-256-GCM.

## Use it when

- You need Rocca-S itself, for example to interoperate with KDDI's beyond-5G/6G experiments or with their Rocca-S forks of libsodium and msquic (yt-nakano/Rocca-S-libsodium, yt-nakano/Rocca-S-msquic).
- Encrypt-heavy bulk AEAD on x86-64 with AES-NI, where you control both ends. At 64 KB on Zen 4 it encrypts at 174.6 Gbps vs 92.7 Gbps for OpenSSL AES-128-GCM.
- Messages of several KB and up. The Zig port's M4 table climbs from 4.67 Gbps at 64 B to 70 Gbps at 1 KB and 190 Gbps at 64 KB.
- Rust or Zig code that wants Rocca-S with a safe API: the `rocca` crate (no_std, in-place variants) or zig-rocca-s, which check the tag in constant time and overwrite the plaintext on failure.
- As a known-answer reference: the gtest suite checks the draft's test vectors, which is useful for validating other implementations.

## Skip it when

- Decrypt-heavy or symmetric traffic. At 64 KB, decryption runs at 140.4 Gbps on M5 Max (1.48x slower than encryption), and on Zen 4 its 92.3 Gbps merely ties OpenSSL AES-128-GCM's 92.9 Gbps. AEGIS-128x2 decrypts at 213.1 Gbps on the same M5.
- Anything that needs a standard, FIPS or interop. The spec is an individual draft that CFRG never adopted, it expired on 2026-08-01, and its IANA codepoint is still 'TBD'.
- Settings that need key commitment, such as multi-key or password-derived decryption, partitioning-oracle exposure or message franking. ePrint 2024/901 gives practical committing attacks with a test vector. Nonce reuse leaks the XOR of the plaintexts (draft section 3.3).
- ARM or other non-AES-NI targets with yt-nakano's code. There is no ARM crypto backend: the fallback is a T-table AES, which is slow and leaks through cache timing. The Rust crate likewise uses softaes's 'unprotected' tables on anything except x86 built with +aes, and that includes aarch64.
- If you need a maintained C library. The reference has 2 stars, no CI and no releases, and its CMake test build hard-codes GCC 12 x86_64-linux-gnu include paths.

## How it is fast

Rocca-S is an AEGIS-style stream AEAD built from bare AES rounds. The state is seven 128-bit words. Each 32-byte block is absorbed through six independent AESENC rounds, with state words or message halves as round keys, plus one XOR; the keystream costs two more rounds. That is 8 AES rounds per 32 bytes, against AES-128-GCM's 10 rounds per 16 bytes plus a GHASH multiply, and there is no key schedule. The rounds in each step are independent, so they pipeline on AES-NI or ARM AESE/AESMC units, and the macros keep the whole state in __m128i registers for an entire call. Decryption is slower because each plaintext block is only known after its keystream AES round, which adds a round of latency to the state-update chain.

## Compared with alternatives

In the same hiae-aead harness, libhiae's HiAE beats Rocca-S at both encryption and decryption (266.7/171.4 Gbps on M5, 268.4/139.1 on Zen 4), and libaegis's AEGIS-128x2 ties it on encryption and decrypts 1.5x faster (211.8/213.1 on M5), and AEGIS also has a separate constant-time bitsliced implementation (aegis-bitsliced). Pick Rocca-S only when the protocol requires Rocca-S; the original Rocca entry is its predecessor, which has published key-recovery and forgery attacks on v2-v4.

## Integration

| | |
|---|---|
| **Form** | source-drop (rocca-s_ref.c + rocca-s.h). The CMakeLists builds a shared lib with -O3 -march=native. The ports ship as a Rust crate (`rocca`) and a Zig package. |
| **Dependencies** | The library needs only libc, plus &lt;immintrin.h&gt; when __AES__ is defined. The bundled CMake unconditionally adds the test directory, which does find_package(GTest REQUIRED) and find_package(absl REQUIRED), so the stock build needs GoogleTest and Abseil. The Rust crate needs softaes on non-AES-NI targets. |
| **Minimum toolchain** | C99 (the benchmark copy builds with -std=c99), CMake 3.14+, C++ for the tests. The Zig port tracks Zig 0.16/master (its benchmark uses std.Io). The Rust crate is edition 2018. |
| **Platforms** | x86-64 with AES-NI, chosen at compile time via __AES__ (needs -maes or -march=native). Everything else, including aarch64, gets a portable T-table fallback. The ARM-crypto (vaeseq/vaesmcq) backend behind the M5 numbers exists only in the hiae-aead/benchmarks copy. The Zig port uses std.crypto.core.aes.Block. The Rust crate gets AES-NI only with RUSTFLAGS target-feature=+aes and falls back to soft AES elsewhere. |
| **Thread safety** | Not documented. There is no global state and rocca_context is caller-owned and per-message, so separate contexts on separate threads are independent. |
| **Drop-in for the baseline** | no |

## Gotchas

- rocca_decrypt writes plaintext without authenticating it. You must call rocca_tag, compare the 32-byte tag in constant time yourself, and erase the output on mismatch, as draft section 3.4 recommends. The context holds the raw key and is never wiped. The Zig and Rust ports do the comparison and fill the output with 0xaa on failure.
- It is not a real streaming API. Each rocca_add_ad/rocca_encrypt/rocca_decrypt call zero-pads its trailing partial block and advances the state, so every call except the last must be a multiple of 32 bytes, and all AD must come before the first encrypt/decrypt. Nothing enforces either rule.
- The backend is fixed at compile time. A generic x86-64 build without -maes silently falls back to the table-based AES. The Rust README likewise says to export RUSTFLAGS="-Ctarget-feature=+aes,+sse4.1" for decent x86 code.
- Only 256-bit keys and 16-byte nonces are implemented. Draft-06 also allows 12-16-byte nonces and 128/192-bit keys with a key-length-dependent S[6], added after ePrint 2024/901. Zero-padding a short key into this code reproduces the older expansion that has equivalent keys, so derive 256 bits with a KDF instead.

## Known shortcomings

- Gain is asymmetric: on M5 2.9x encrypt but 2.0x decrypt, and on Zen 4 1.9x encrypt with decrypt at parity (92.3 vs GCM 92.9 Gbps). Compares a 256-bit-key cipher with AES-128-GCM (not like-for-like). Benchmark runs KDDI's reference plus an ARM port, not this repo as-is. ePrint 2024/901 gives a practical FROB committing attack on Rocca-S (no nonce-respecting key recovery or forgery known). IETF draft-nakano-rocca-s-06 is an individual draft, not adopted, expired 2026-08-01. 2 stars, stale since 2025-03-19. Zig/Rust ports by jedisct1 are folded into this entry.
- M5 numbers measure jedisct1's benchmark copy (which adds an ARM crypto backend), not KDDI's code, which has only x86 AES-NI or a leaky T-table fallback. On M5, HiAE and AEGIS-128X2 match or beat it. KDDI C API: rocca_decrypt never checks the tag (no constant-time verify), the key in the context is never wiped, and every call except the last must be a multiple of 32 bytes. The folded-in Rust crate (`rocca` 0.3.2) uses unprotected software AES on aarch64. Not key-committing.
- Enricher (via the folded zig-rocca-s port): on the Zen 4 chart AEGIS-128x2-aesni (208.4/207.6 Gbps) beats Rocca-S (174.6/92.3) both ways; the Zig port's src/benchmark.zig is a single pass with no warm-up, repetitions or baseline row, its README M4 table (commit 04c6fb5, July 2025) was never re-run after the Zig 0.16 rewrite, and an Oct 2024 commit removed README numbers that were original-Rocca runs; the Zig port matched all 7 KDDI reference vectors.

## Caveats and trade-offs

The comparison numbers come from a separate repo, hiae-aead/benchmarks. It lives under the HiAE org, almost all commits are by jedisct1, and it has no top-level license. Its rocca-s/rocca-s.c is a reformatted copy of KDDI's MIT reference with an added ARM-crypto (vaeseq/vaesmcq) backend, so the M5 figures measure that port, not yt-nakano's code as-is; yt-nakano's code supports only x86 AES-NI plus a portable table fallback. The yt-nakano README itself gives only a standalone '&gt;200 Gbps on i9-12900K' figure with no baseline. The comparison is 256-bit-key Rocca-S against AES-128-GCM, not the like-for-like AES-256-GCM. Decryption is much slower than encryption (1.48x slower on M5, 1.89x on Zen 4), and on Zen 4 decryption only matches OpenSSL's VAES GCM. On security, Rocca-S is not key-committing. Practical FROB committing attacks with a test vector are in Takeuchi-Todo-Iwata, ePrint 2024/901, which extends their ToSC 2024(2) attack on revised Rocca and improves Derbez et al., ToSC 2024(1), which needed 2^64. The same note found an equivalent-key issue in the short-key expansion, fixed in draft-06; the reference code takes 256-bit keys only. The ToSC 2024(2) key-recovery and universal-forgery results target Rocca-v2/v3/v4, not Rocca-S; the paper notes that Rocca-S shares v4's unkeyed finalization and leaves Rocca-S open. I found no published key-recovery or nonce-respecting forgery against Rocca-S.

256-bit key / 256-bit tag only; decryption is 1.5-1.9x slower than encryption at large message sizes because the AES-round-then-fold state update recovers the message block only after the AES round completes; needs AES-NI or ARM crypto extensions to hit peak throughput

## Maintenance

The reference is stale: its last commit (2025-03-19) was a one-file update after the 2023 upload, and it has 2 stars and no issues. It is MIT-licensed and a single \~22 KB C file, so vendoring is easy. The maintained routes are jedisct1's MIT Zig port (21 stars, updated for Zig 0.16 in 2026) and the Rust crate `rocca` 0.3.2 (released 2026-09-25, \~7.7k downloads; Cargo.toml says MIT but the repo has no LICENSE file). yt-nakano's separate Rocca-SX repo (parallel SX2/SX4 variants, January 2026, no README) is a different, unspecified cipher.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** hiae-aead/benchmarks runs ROCCA-S (rocca-s/performance_test.c + rocca-s/rocca-s.c) against OpenSSL EVP AES-128-GCM/CTR (aes128-gcm-openssl/benchmark.c + encrypt.c) through a top-level Makefile, and the README states the compilers (Apple clang 21.0.0, clang 21.1.8), flags (-O3 -march=native, -mcpu=native on ARM), CPUs (Apple M5 Max, Ryzen 7 7700 at 3.8 GHz fixed) and OpenSSL versions. That is public code plus full methodology, so it is tier A.
- **Verifier notes:** Numbers match the README tables exactly (M5 table; Zen 4 ROCCA-S row plus the Zen 4 chart for GCM), and tier A holds. The main correction is that on Zen 4 ROCCA-S decryption (92.3 Gbps) only ties OpenSSL AES-128-GCM (92.9 Gbps), so the win there is encryption-only. The record's language 'C++' is wrong: the reference code is C, and only its gtest tests are C++. That field cannot be corrected in this schema, so the orchestrator should fix it. License MIT, 2 stars, last commit 2025-03-19 and 'stale' all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** hiae-aead/benchmarks: M5 encrypt 2.9x / decrypt 2.0x vs OpenSSL AES-128-GCM; Zen 4 encrypt 1.9x, decrypt 92.3 vs 92.9 Gbps.; enricher of the zig-rocca-s port
- **Pages the verifier opened:**
  - <https://github.com/yt-nakano/rocca-s>
  - <https://github.com/hiae-aead/benchmarks>
  - <https://raw.githubusercontent.com/hiae-aead/benchmarks/main/.media/zen4/throughput_comparison_zen4.png>
  - <https://raw.githubusercontent.com/hiae-aead/benchmarks/main/.media/m5/throughput_comparison_m5.png>
  - <https://datatracker.ietf.org/api/v1/doc/document/draft-nakano-rocca-s/?format=json>
  - <https://datatracker.ietf.org/doc/draft-nakano-rocca-s/history/>
  - <https://www.ietf.org/archive/id/draft-nakano-rocca-s-06.txt>
  - <https://api.crossref.org/works/10.46586/tosc.v2024.i2.85-117>
  - <https://tosc.iacr.org/index.php/ToSC/en/article/view/11622>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/11622/11113>
  - <https://api.crossref.org/works?query.bibliographic=Key%20committing%20attacks%20against%20AES-based%20AEAD%20schemes>
  - <https://eprint.iacr.org/search?q=Rocca-S>
  - <https://eprint.iacr.org/2024/901>
- **Sources the enricher read:**
  - <https://github.com/yt-nakano/rocca-s>
  - <https://github.com/yt-nakano/rocca-s/blob/main/README.md>
  - <https://github.com/yt-nakano/rocca-s/blob/main/rocca-s.h>
  - <https://github.com/yt-nakano/rocca-s/blob/main/rocca-s_ref.c>
  - <https://github.com/yt-nakano/rocca-s/blob/main/CMakeLists.txt>
  - <https://github.com/yt-nakano/rocca-s/blob/main/test/CMakeLists.txt>
  - <https://github.com/yt-nakano/rocca-s/blob/main/test/test_rocca-s_ref.cc>
  - <https://github.com/yt-nakano/rocca-s/issues?q=is%3Aissue>
  - <https://github.com/yt-nakano/rocca-s/commits/main>
  - <https://github.com/search?q=rocca-s&type=repositories>
  - <https://github.com/yt-nakano/Rocca-SX>
  - <https://github.com/jedisct1/zig-rocca-s>
  - <https://github.com/jedisct1/zig-rocca-s/blob/master/README.md>
  - <https://github.com/jedisct1/zig-rocca-s/blob/master/src/rocca.zig>
  - <https://github.com/jedisct1/zig-rocca-s/blob/master/src/benchmark.zig>
  - <https://github.com/jedisct1/zig-rocca-s/blob/master/build.zig>
  - <https://github.com/jedisct1/zig-rocca-s/issues?q=is%3Aissue>
  - <https://github.com/jedisct1/rust-rocca-s>
  - <https://github.com/jedisct1/rust-rocca-s/blob/master/README.md>
  - <https://github.com/jedisct1/rust-rocca-s/blob/master/Cargo.toml>
  - <https://github.com/jedisct1/rust-rocca-s/blob/master/src/lib.rs>
  - <https://github.com/jedisct1/rust-rocca-s/blob/master/src/aes_ni.rs>
  - <https://github.com/jedisct1/rust-rocca-s/blob/master/src/softaes.rs>
  - <https://github.com/jedisct1/rust-rocca-s/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/rocca>
  - <https://github.com/hiae-aead/benchmarks>
  - <https://github.com/hiae-aead/benchmarks/blob/main/README.md>
  - <https://github.com/hiae-aead/benchmarks/blob/main/rocca-s/rocca-s.c>
  - <https://github.com/hiae-aead/benchmarks/blob/main/rocca-s/rocca-s.h>
  - <https://github.com/hiae-aead/benchmarks/blob/main/rocca-s/performance_test.c>
  - <https://www.ietf.org/archive/id/draft-nakano-rocca-s-06.txt>
  - <https://eprint.iacr.org/2024/901>
  - <https://eprint.iacr.org/search?q=Rocca-S>
  - <https://hn.algolia.com/api/v1/search?query=rocca-s>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/yt-nakano/rocca-s`) · [data/wave7/enrich/raw/github_com_yt_nakano_rocca_s.json](../../../data/wave7/enrich/raw/github_com_yt_nakano_rocca_s.json) (enrichment confidence 0.8)

</details>
