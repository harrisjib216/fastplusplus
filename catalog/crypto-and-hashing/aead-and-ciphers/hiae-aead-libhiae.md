# HiAE (libhiae)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Portable C library for the HiAE AES-round AEAD; about 3.8x OpenSSL AES-128-GCM encryption throughput on Apple M5 Max.

| | |
|---|---|
| **Beats** | OpenSSL AES-128-GCM / AES-256-GCM |
| **Claimed result** | On Apple M5 Max with 64 KB messages, HiAE (a vendored libhiae copy) reaches 266.7 Gbps AEAD encryption against 70.8 Gbps for OpenSSL 3.6.4 AES-128-GCM (\~3.77x, derived from page data). Separately, the designers' ePrint 2025/377 paper benchmarks their own Concyclics/HiAE implementation, not libhiae, against OpenSSL 3.0. Its abstract claims over 340 Gbps (x86) and 180 Gbps (ARM) for AEAD. Table 10, AMD Ryzen 9 7950X, 16384-byte messages: AEAD 340.02 Gbps vs AES-256-GCM 51.90 Gbps (\~6.6x, derived from paper data); encryption-only 352.73 Gbps vs AES-256-CTR 95.71 Gbps (\~3.7x, derived). The record's 269.01 vs 84.09 Gbps pair is encryption-only at 1024 bytes against AES-256-CTR, not AEAD against AES-256-GCM. |
| **Workload** | AEAD encryption with associated data and tag, 64 KB messages, 4096-byte-aligned buffers |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max (macOS 26) for the AES-GCM comparison. The page also has a Zen 4 (Ryzen 7 7700, 3.8 GHz fixed) run, but its text table gives no AES-GCM figure. The paper covers 14 CPUs (Table 9), including the AMD Ryzen 9 7950X and Intel Xeon W9-3495X. |
| **Compiler and flags** | M5 Max run: Apple clang 21.0.0 on macOS 26, -O3 -mcpu=native, OpenSSL 3.6.4. Paper: GCC 11.4 -O3 on the x86 servers (Ubuntu 22.04) and on the desktop (Windows 11 WSL2, Ubuntu 22.04, which includes the 7950X), and GCC 14 on the Apple laptops. |
| **Adoption** | 59 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/hiae-aead/libhiae) · [benchmark](https://github.com/hiae-aead/benchmarks#performance-results) |

## Verdict

The author's hiae-aead/benchmarks harness ran a vendored libhiae copy against OpenSSL 3.6.4 AES-128-GCM on an Apple M5 Max (macOS 26, Apple clang 21.0.0, -O3 -mcpu=native, median of three passes, 4096-byte-aligned buffers, with AD and tag). At 64 KB, HiAE encrypted at 266.7 Gbps vs 70.8 for GCM (\~3.8x) and decrypted at 171.4 vs 70.2 (\~2.4x). The ePrint 2025/377 figures (for example 340.02 vs 51.90 Gbps against OpenSSL 3.0 AES-256-GCM on a Ryzen 9 7950X with GCC 11.4 at 16 KB) measure the designers' separate Concyclics/HiAE code, not libhiae.

## Use it when

- Bulk AEAD on Apple Silicon or other ARMv8 cores with AES and SHA3 extensions, when AES-GCM is the bottleneck. On an M5 Max at 64 KB, HiAE encrypts at 266.7 Gbps vs 70.8 for OpenSSL AES-128-GCM.
- x86-64 servers and desktops with AVX-512 and VAES (the README's Zen 4 run: 251.7 Gbps encryption at 64 KB) in systems where you control both ends: storage, backups, internal links, high-rate tunnels.
- Messages of several KB and up. Throughput climbs from about 131 Gbps at 1 KB to about 252 Gbps at 64 KB on Apple M4, and from 71 to 252 Gbps on Zen 4.
- Encrypt-heavy workloads such as write-mostly storage or broadcast senders, since encryption runs 1.5-1.9x faster than decryption.
- When you want 128-bit random nonces and a 256-bit key without GCM's 96-bit nonce limits (the draft caps a key at 2^64 messages).

## Skip it when

- Anywhere that needs interoperability, FIPS or a published standard. HiAE is only an individual IETF draft (rev 06, expires 2026-11-11), not an RFC, and there are no NIST or TLS registrations.
- Systems where nonce reuse, release of unverified plaintext, or unlimited forged-decryption attempts are possible. ePrint 2025/1180 (Bille and Tischhauser, TOSC 2026) gives full key recovery from a small constant number of repeated nonces or unverified decryptions, plus nonce-respecting key recovery at 2^128 data and 2^129 time using decryption queries. The designers (ePrint 2025/1235) and the draft answer that repeated forgery attempts are outside the security model.
- Decrypt-heavy or receive-side workloads. On the M5 Max, HiAE decrypts at 171.4 Gbps against 211.8 for AEGIS-128x2 (which decrypts as fast as it encrypts), and on Zen 4 HiAE decryption is 48% slower than its encryption.
- CPUs without AES instructions. The fallback is a T-table soft AES (hardened by touching every cache line, not bitsliced), and the WASM scalar build uses plain table lookups. There is no constant-time bitsliced path like aegis-bitsliced.
- Tiny messages or MSVC/gcc toolchains. Throughput is 4-16 Gbps at 16-64 B on M4, and the benchmark page's text tables give AES-GCM figures only at 64 KB. MSVC proper cannot build the VAES backend, and the README says gcc produces noticeably slower code than clang or zig cc.

## How it is fast

HiAE is a stream-cipher-style AEAD with a 2048-bit state of sixteen 128-bit words. Each 16-byte block costs two bare AES rounds plus a few XORs (the draft's 'XAXX' structure, arranged to suit both ARM AESE/AESMC and x86 AESENC), with no AES key schedule and no GHASH multiply. The code avoids physically rotating the state by using a cycling index (offset) and unrolls 16 blocks (256 bytes) per loop, so all 16 state words stay in registers. A load-time constructor picks a backend by CPU detection: ARMv8 AES, ARMv8 AES plus FEAT_SHA3 (EOR3 three-way XOR), x86 AES-NI+AVX, 'VAES+AVX512' (still 128-bit _mm_aesenc_si128 code, compiled for AVX-512 targets), WASM SIMD128, or a table-based software fallback.

## Compared with alternatives

Pick libhiae over Concyclics/HiAE when you want the same cipher as an MIT-licensed, runtime-dispatched library with streaming and MAC APIs and IETF test vectors; the designers' repo has no license. Pick it over libaegis only if you control both ends and mostly encrypt on ARM or AVX-512 x86 (266.7 vs 211.8 Gbps for AEGIS-128x2 on M5 Max). Otherwise AEGIS has an RFC, a bitsliced constant-time fallback, and decrypts as fast as it encrypts.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Make, CMake with find_package(hiae), or zig build); also a source-drop of src/hiae/\*.c or a single-file amalgamation (make amalgamate) |
| **Dependencies** | none (standard C library only) |
| **Minimum toolchain** | C99, CMake 3.10+. clang or zig cc recommended, GCC 14+ if gcc must be used. CI builds with gcc, clang and MSVC (cl), and with Zig for wasm32-wasi. |
| **Platforms** | x86-64 (AES-NI+AVX, or VAES+AVX-512F, chosen at runtime), aarch64 (ARMv8 AES, FEAT_SHA3 when present, detected via getauxval/sysctl), wasm32 (SIMD128/relaxed SIMD), portable software fallback elsewhere |
| **Thread safety** | The backend is chosen once by a load-time constructor into a global pointer, and HiAE_init_library() is documented as thread-safe and idempotent. States are caller-owned 256-byte structs, independent per operation. HiAE_force_implementation() resets that global and must be called before other use. |
| **Drop-in for the baseline** | no |

## Gotchas

- One-shot HiAE_decrypt writes plaintext into the output buffer before comparing tags and does not wipe it on failure; the header only says the output is 'undefined'. HiAE_stream_decrypt/HiAE_dec also return plaintext before the tag is checked. Given the RUP key-recovery attack, zero or discard that output yourself.
- The low-level API needs every absorb/enc/dec call except the last to be a multiple of 16 bytes, needs the exact total lengths at finalize, and states must not be reused. HiAE_enc_partial_noupdate does not advance the state.
- CMake defaults to a Debug build. Pass -DCMAKE_BUILD_TYPE=Release (-O3), or benchmarks will be far off.
- HiAEx2/HiAEx4 are separate, non-spec ciphers that do not interoperate with HiAE. HiAEx4's C1 constant was fixed on 2026-09-18, which changed its outputs. The README says they need unique nonces even in MAC mode.

## Known shortcomings

- jedisct1's own implementation (not a port of the designers' concyclics/hiae, listed separately); benchmark page numbers are his runs. The paper pair 269.01/84.09 compares encryption-only 1 KB against CTR, not AEAD against AEAD. HiAE is a 2025 design: reference decrypt-before-verify concerns and a ToSC 2026 key-recovery result in the release-unverified-plaintext setting (see the HiAE entry); individual Internet-Draft only.
- ePrint 2025/1180 (ToSC 2026) gives full key recovery from a few repeated nonces or from released unverified plaintext (nonce-respecting attack at 2^128 data). HiAE_decrypt leaves unverified plaintext in the output buffer on tag failure, and streaming decrypt releases plaintext before the tag check. Decrypt is 1.5-1.9x slower than encrypt. Software fallback is table-based AES (not bitsliced); MSVC cannot build the VAES path; CMake defaults to Debug.

## Caveats and trade-offs

The benchmark repo (hiae-aead/benchmarks, no LICENSE file) is maintained by libhiae's main author (jedisct1), so these are first-party measurements of a vendored libhiae copy. The ePrint 2025/377 figures measure a different implementation, the designers' Concyclics/HiAE (no license). The paper is still an ePrint preprint (4 revisions, last 2025-06-04) and no Crossref record for it was found. It accompanies draft-pham-cfrg-hiae (rev 06), which is an individual draft and not yet an RFC.

Newer, non-standardized AES-based AEAD tied to an individual IETF CFRG draft (draft-pham-cfrg-hiae) and ePrint 2025/377; best performance needs clang/zig cc rather than gcc; HiAEx2/HiAEx4 variants are explicitly experimental benchmarking-only, not part of the spec

## Maintenance

Actively maintained (v0.2.4 tagged 2026-07-17, commits through 2026-09-20, no open issues) and MIT-licensed, with a single-file amalgamation that makes vendoring trivial. It is essentially a one-maintainer, pre-1.0 project for a cipher that is still an individual draft.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** hiae-aead/benchmarks publishes the harness (hiae/benchmark.c, a vendored copy of the libhiae sources, and aes128-gcm-openssl/benchmark.c) and states the setup: Apple clang 21.0.0, -O3 -mcpu=native, OpenSSL 3.6.4, Apple M5 Max. Its 64 KB table shows HiAE AEAD encryption at 266.7 Gbps against 70.8 Gbps for AES-128-GCM.
- **Verifier notes:** libhiae and the catalogued concyclics/hiae are separate code bases. libhiae is jedisct1/Frank Denis's full implementation (117 of about 120 commits are his; the HiAE designer Concyclics made 2); it is not a fork, port or binding. Denis (Fastly) co-authors the IETF HiAE draft with the Huawei designers. The benchmark-page numbers are Denis's own runs of libhiae code; the paper numbers are the designers' runs of their own repo, so the two entries cover the same algorithm and one may be redundant.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** hiae-aead/benchmarks: M5 266.7 vs AES-128-GCM 70.8 Gbps; 7950X AEAD 16 KB 340.02 vs GCM 51.90 Gbps (\~6.6x).
- **Pages the verifier opened:**
  - <https://github.com/hiae-aead/benchmarks>
  - <https://github.com/hiae-aead/libhiae>
  - <https://eprint.iacr.org/2025/377>
  - <https://eprint.iacr.org/2025/377.pdf>
  - <https://github.com/Concyclics/HiAE>
  - <https://datatracker.ietf.org/api/v1/doc/document/?name__contains=hiae&format=json>
  - <https://datatracker.ietf.org/api/v1/doc/documentauthor/?document__name=draft-pham-cfrg-hiae&format=json>
  - <https://api.crossref.org/works?query.bibliographic=HiAE+High-Throughput+Authenticated+Encryption+Algorithm+Cross-Platform+Efficiency&rows=5>
- **Sources the enricher read:**
  - <https://github.com/hiae-aead/libhiae>
  - <https://github.com/hiae-aead/libhiae/blob/main/README.md>
  - <https://github.com/hiae-aead/libhiae/blob/main/include/HiAE.h>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_internal.h>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_arm.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_arm_sha3.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_aesni.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_vaes_avx512.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/HiAE_stream.c>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/hiae/softaes.h>
  - <https://github.com/hiae-aead/libhiae/blob/main/src/common/cpu.h>
  - <https://github.com/hiae-aead/libhiae/blob/main/CMakeLists.txt>
  - <https://github.com/hiae-aead/libhiae/blob/main/Makefile>
  - <https://github.com/hiae-aead/libhiae/blob/main/.github/workflows/cmake-multi-platform.yml>
  - <https://github.com/hiae-aead/libhiae/issues?q=is%3Aissue>
  - <https://github.com/hiae-aead/libhiae/pulls?q=is%3Apr>
  - <https://github.com/hiae-aead/libhiae/commits/main>
  - <https://github.com/hiae-aead/libhiae/releases>
  - <https://github.com/hiae-aead/libhiae/tags>
  - <https://github.com/hiae-aead/benchmarks>
  - <https://github.com/hiae-aead/benchmarks/blob/main/aes128-gcm-openssl/benchmark.c>
  - <https://github.com/hiae-aead/benchmarks/blob/main/aes128-gcm-openssl/Makefile>
  - <https://eprint.iacr.org/search?q=HiAE>
  - <https://eprint.iacr.org/2025/377>
  - <https://eprint.iacr.org/2025/1180>
  - <https://eprint.iacr.org/2025/1203>
  - <https://eprint.iacr.org/2025/1235>
  - <https://datatracker.ietf.org/api/v1/doc/document/?name__contains=hiae&format=json>
  - <https://www.ietf.org/archive/id/draft-pham-cfrg-hiae-06.txt>
  - <https://hn.algolia.com/api/v1/search?query=HiAE&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/hiae-aead/libhiae`) · [data/wave7/enrich/raw/github_com_hiae_aead_libhiae.json](../../../data/wave7/enrich/raw/github_com_hiae_aead_libhiae.json) (enrichment confidence 0.8)

</details>
