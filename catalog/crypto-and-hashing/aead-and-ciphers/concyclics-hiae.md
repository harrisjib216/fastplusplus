# HiAE (High-throughput Authenticated Encryption)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟢 active

> Reference C code for HiAE, Huawei's AES-round AEAD; 2-6.6x OpenSSL AES-256-GCM on 16 KB messages on recent x86/ARM.

| | |
|---|---|
| **Beats** | OpenSSL AES-256-GCM |
| **Claimed result** | AEAD at 16384 B (Table 10): 340.02 Gbps (HiAE) vs 51.90 Gbps (OpenSSL 3.0 AES-256-GCM) on AMD Ryzen 9 7950X (\~6.6x, derived from page data); 171.46 vs 36.49 Gbps on Intel Xeon W9-3495X (\~4.7x, derived from page data); 253.19 vs 38.80 Gbps on AMD EPYC 9334 (\~6.5x, derived from page data). The abstract states over 340 Gbps on x86 and 180 Gbps on ARM in AEAD mode, 'making it the fastest AEAD solution on ARM chips and setting a new performance record on the latest x86 processors'. |
| **Workload** | Single-core AEAD encrypt+authenticate throughput across 14 named ARM and x86 CPUs (server/desktop/laptop/mobile/router), message sizes 64B-16384B, -O3 builds, vs OpenSSL 3.0 AES-256-GCM, AES-256-CTR, SNOW-V-GCM, Rocca, Rocca-S and AEGIS-128L. |
| **Metric** | throughput |
| **Hardware** | 14 CPUs in Table 9/10: Intel Xeon W9-3495X, AMD EPYC 9334, AMD Ryzen 9 7950X, Intel Xeon Gold 6326, Intel Core i7-11700, Intel Xeon Gold 6242R, Intel Xeon E5-2620 v3, HiSilicon Kunpeng 920, Kunpeng 920X, Kirin 9000S, Qualcomm Snapdragon 8+ Gen1, Apple M2 Max, Apple M3 Pro, Rockchip RK3568 (an M1 MacBook Air is named in the setup text but has no result row) |
| **Compiler and flags** | GCC 11.4 (x86 servers/desktop, Ubuntu 22.04 or WSL2), GCC 10.3 (Kunpeng/openEuler), GCC 14 (Apple M-series), ArkCompiler 3.0.0.5 (Huawei mobile), openWRT GCC 11.2.0 (router); -O3 maximum optimization used for every implementation compared |
| **Adoption** | 21 stars |
| **Last commit** | 2025-11-11 |
| **Links** | [repository](https://github.com/Concyclics/HiAE) · [benchmark](https://eprint.iacr.org/2025/377.pdf) |

## Verdict

The comparison comes from the designers' non-peer-reviewed ePrint 2025/377, Table 10. It measures single-core AEAD encryption at 16 KB with 48-byte AD, built with -O3 and GCC 11.4 on the x86 machines. HiAE reached 340.02 Gbps against 51.90 for OpenSSL 3.0 AES-256-GCM on a Ryzen 9 7950X (about 6.6x), 253.19 vs 38.80 on an EPYC 9334, and 171.46 vs 36.49 on a Xeon W9-3495X. The GCM baseline swings widely (114.07 Gbps on an i7-11700, where HiAE's lead falls to about 2.2x), decryption was not measured, phones used a hand-written AES instead of OpenSSL, and the repo's harness times only HiAE.

## Use it when

- Point-to-point links where you control both endpoints and messages are 1 KB or larger, on CPUs with VAES and AVX-512 (Ice Lake, Sapphire Rapids, Zen 4). In the designers' Table 10 at 16 KB AEAD, HiAE runs at 340.02 Gbps against 51.90 for OpenSSL 3.0 AES-256-GCM on a Ryzen 9 7950X, and 195.02 against 43.85 on a Xeon Gold 6326.
- ARMv8/v9 servers and laptops with crypto extensions, where the gain over other AES-based AEADs is largest. On Kunpeng 920 at 16 KB, HiAE does 53.72 Gbps, against 23.11 for AEGIS-128L and 14.66 for OpenSSL AES-256-GCM. On Apple M3 Pro it does 189.19, against 70.95 for GCM.
- Reproducing or extending the ePrint 2025/377 measurements on your own hardware. make benchmark times encryption-only, AEAD and MAC-only runs at 16 B to 16 KB.
- Designs that want a 256-bit key-recovery target with a 128-bit tag and can guarantee unique nonces and verify-before-release decryption.

## Skip it when

- Interoperating with TLS, IPsec, QUIC or any existing protocol. HiAE has no RFC. Its specification is an individual Internet-Draft (draft-pham-cfrg-hiae-06, May 2026) that CFRG has not adopted.
- Small messages. At 64 B, OpenSSL AES-256-GCM beats HiAE on every CPU in Table 10 where OpenSSL was used (7950X 18.35 vs 12.12 Gbps, M3 Pro 28.05 vs 9.72), and AEGIS-128L beats it on all seven x86 chips. On Kunpeng 920 and 920X, GCM still wins at 256 B. The fixed 32-round initialization and 32-round finalization dominate short messages.
- x86 without VAES (Cascade Lake, Haswell). Rocca is faster there: 156.60 vs 133.19 Gbps on a Xeon Gold 6242R and 75.97 vs 63.90 on a Xeon E5-2620 v3, both at 16 KB AEAD.
- Any setting where a nonce might repeat, unverified plaintext might be released, or an attacker can submit many forged decryptions. ePrint 2025/1180 (a minor revision of a ToSC 2026 paper) recovers the full 256-bit key with 2^128 data and at most 2^129 time using nonce-respecting decryption queries, and with only a small constant number of repeated nonces or unverified decryptions. The designers' rebuttal (2025/1235) says these settings are outside HiAE's model.
- Decrypt-heavy workloads or shipping this repo. The paper benchmarks encryption only, while libhiae's own numbers show decryption about 35-45% slower (Zen 4 at 16 KB: 129.71 vs 222.32 Gbps). This repo also has no LICENSE file.

## How it is fast

HiAE is an NFSR-style stream cipher with a 2048-bit state (16 x 128-bit blocks). Each 16-byte block costs two AES rounds plus a few XORs, arranged in an 'XAXX' shape (AESL(a xor b) xor c xor d). That shape matches x86 aesenc and fuses well with ARM aese+aesmc, so neither ISA pays the extra XOR that aesenc-shaped designs such as AEGIS and Rocca pay on ARM. The keystream tap position was picked to leave four dependency-free rounds of parallelism during decryption. The code unrolls 16 state updates, so the shifting state costs no index arithmetic. On x86 with VAES and AVX-512 it switches to inline assembly that keeps all 16 state blocks in xmm0-xmm15 and uses xmm16-31 for message and ciphertext blocks. The paper says this is why older CPUs, where aesenc can only use xmm0-15, fall behind.

## Compared with alternatives

Use HiAE over Rocca, Rocca-S and AEGIS-128L for bulk (1 KB and up) traffic on ARM or VAES-capable x86, where Table 10 shows it ahead. Stay with Rocca on pre-VAES Xeons, with AEGIS-128L or AES-GCM for messages of 256 B or less, and with libaegis (RFC-published AEGIS, including the wider AEGIS-128X variants the HiAE paper never measured) when you need a standardized, licensed library. To deploy HiAE itself, take the MIT-licensed hiae-aead/libhiae rather than this repo. intel-ipsec-mb and SNOW-V-GCM target different needs: standard IPsec algorithms and a 5G-style stream cipher.

## Integration

| | |
|---|---|
| **Form** | source-drop (code/HiAE.c plus code/HiAE.h). The Makefile only builds tests, the benchmark and two demo apps; there is no library target. |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | GCC or Clang with GNU extensions. The code uses GNU inline asm and vector operators on __m128i/uint8x16_t; the paper used GCC 10.3-14 at -O3, and MSVC support is not documented. Build with -maes on x86-64 or -march=...+crypto on AArch64. The VAES/AVX-512 assembly path is compiled only when __VAES__ and __AVX512F__ are defined, for example with -march=native on Ice Lake or Zen 4. |
| **Platforms** | x86-64 with AES-NI (fastest with VAES + AVX-512) and AArch64 with the crypto extensions. Other targets stop at #error. The ISA path is fixed at compile time with no runtime dispatch. |
| **Thread safety** | Not documented. The code has no mutable globals (only two const constant tables), and the one-shot calls keep their state on the stack, so concurrent calls on separate buffers look safe. A HiAE_stream_\* state must not be shared between threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- HiAE_AEAD_decrypt never checks the tag. It writes the plaintext, then overwrites the caller's tag buffer with the computed tag and always returns 0. The caller has to save the received tag first, compare the two in constant time, and wipe the plaintext on mismatch. As written, the API is the release-of-unverified-plaintext setting in which 2025/1180 recovers the key. libhiae's HiAE_decrypt does verify and returns non-zero on failure.
- The algorithm changed after the paper. The October and November 2025 commits changed how key and nonce are loaded during initialization, and a July 2025 fix made finalization encode lengths in bits. Ciphertexts and tags from older checkouts will not match the current draft test vectors. The round count is the same, so throughput should be unaffected.
- Building with -march=native on a VAES/AVX-512 machine emits EVEX instructions that fault on older x86 CPUs, and there is no CPUID check. Build per target, or use libhiae, which dispatches at run time.
- Every HiAE_stream_encrypt, HiAE_stream_decrypt and HiAE_stream_proc_ad call pads its own trailing partial block. When streaming, every chunk except the last must therefore be a multiple of 16 bytes. The header does not document this; it follows from the code.

## Known shortcomings

- ePrint preprint only; the harness times HiAE alone (no OpenSSL code in the repo), so ratios against AES-GCM are derived from separately reported numbers. The repo has no license; hiae-aead/libhiae is an MIT-licensed alternative implementation. New 2025 design with little cryptanalysis yet.
- Designer's preprint measures encryption only; libhiae shows decryption \~35-45% slower. At 64 bytes OpenSSL AES-GCM beats HiAE on every CPU in the paper's Table 10, and AEGIS-128L beats it on all 7 x86 CPUs. Reference HiAE_AEAD_decrypt releases plaintext without checking the tag (RUP setting), where ePrint 2025/1180 (ToSC 2026) gives key recovery. Init changed Oct/Nov 2025, so current ciphertexts differ from the paper version; no runtime ISA dispatch; individual Internet-Draft only, not CFRG-adopted.

## Caveats and trade-offs

Very new design (2025) by the paper's authors; numbers are first-party, from a non-peer-reviewed preprint. The public repo harness (test/performance_test.c) benchmarks HiAE only; the OpenSSL comparison code is not published. On mobile phones the AES-256 baseline was hand-implemented rather than OpenSSL. HiAE trails Rocca on pre-VAES Xeons (Gold 6242R, E5-2620 v3). Under active cryptanalysis: ePrint 2025/1180 'Cryptanalysis of the Authenticated Stream Cipher HiAE' (now a minor revision of a ToSC 2026 paper), 2025/1203 'Analyze the Security of the AEAD Scheme HiAE by Algebraic Techniques', and the designers' rebuttal 2025/1235. The reference repo has no license file; an MIT-licensed implementation exists at hiae-aead/libhiae (59 stars), but its README does not benchmark against AES-GCM.

Reference repo carries no LICENSE file, so the code can be studied but not safely reused/redistributed as-is. HiAE is a brand-new (2025) design with far less cryptanalysis history than AES-GCM or even AEGIS; the paper's own results show HiAE falls slightly behind Rocca on older Xeon Gold 6242R/E5-2620 v3 CPUs that lack VAES.

## Maintenance

This is a 21-star designer reference repo, last changed 2025-11-11 to match the updated initialization and IETF test vectors. It has no LICENSE file, so it is study-only. For real use, take the MIT-licensed hiae-aead/libhiae (59 stars, pushed 2026-09-20), which adds runtime dispatch, tag verification and a portable fallback.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** ePrint 2025/377 Table 10 does compare HiAE against OpenSSL 3.0 AES-256-GCM on 14 named CPUs with GCC version and -O3 stated, but the paper is a non-peer-reviewed preprint by the designers (ePrint lists 'Publication info: Preprint'; no venue found on Crossref), and the public harness (test/performance_test.c) times only HiAE with no OpenSSL/baseline code, so it is neither A (baseline benchmark code not public) nor B (not peer-reviewed/independent).
- **Verifier notes:** All three quoted numbers match Table 10 exactly; the only fix is marking the ratios as derived (7950X is 6.55x, not 6.5x). Metadata checked: no LICENSE file, not archived or a fork, 21 stars, last commit 2025-11-11 (active). Orchestrator may prefer hiae-aead/libhiae (MIT) as the copyable repo, but that is a different project URL, so I did not change repo_url.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2025/377.pdf>
  - <https://eprint.iacr.org/2025/377>
  - <https://eprint.iacr.org/2025/1180>
  - <https://eprint.iacr.org/2025/1203>
  - <https://eprint.iacr.org/2025/1235>
  - <https://github.com/Concyclics/HiAE>
  - <https://github.com/Concyclics/HiAE/blob/main/README.md>
  - <https://github.com/Concyclics/HiAE/blob/main/test/performance_test.c>
  - <https://github.com/Concyclics/HiAE/blob/main/Speed/speed.py>
  - <https://github.com/Concyclics/HiAE/blob/main/Speed/speed.csv>
  - <https://github.com/hiae-aead/libhiae>
  - <https://api.crossref.org/works?query.bibliographic=HiAE+High-Throughput+Authenticated+Encryption+Algorithm+Cross-Platform+Efficiency&rows=5>
- **Sources the enricher read:**
  - <https://github.com/Concyclics/HiAE>
  - <https://github.com/Concyclics/HiAE/blob/main/README.md>
  - <https://github.com/Concyclics/HiAE/blob/main/code/HiAE.h>
  - <https://github.com/Concyclics/HiAE/blob/main/code/HiAE.c>
  - <https://github.com/Concyclics/HiAE/blob/main/Makefile>
  - <https://github.com/Concyclics/HiAE/blob/main/test/performance_test.c>
  - <https://github.com/Concyclics/HiAE/blob/main/test/test_vectors_ietf.c>
  - <https://github.com/Concyclics/HiAE/blob/main/Speed/speed.csv>
  - <https://github.com/Concyclics/HiAE/commits/main>
  - <https://github.com/Concyclics/HiAE/commit/01e30348d608d05429449d8e3357c94c382b4bd0>
  - <https://github.com/Concyclics/HiAE/commit/56dccf9073a5970a9289cb55eaf7dc3097a07ebf>
  - <https://eprint.iacr.org/2025/377>
  - <https://eprint.iacr.org/2025/377.pdf>
  - <https://eprint.iacr.org/2025/1180>
  - <https://eprint.iacr.org/2025/1203>
  - <https://eprint.iacr.org/2025/1235>
  - <https://github.com/hiae-aead/libhiae>
  - <https://datatracker.ietf.org/api/v1/doc/document/draft-pham-cfrg-hiae/?format=json>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/concyclics/hiae`) · [data/wave7/enrich/raw/github_com_concyclics_hiae.json](../../../data/wave7/enrich/raw/github_com_concyclics_hiae.json) (enrichment confidence 0.82)

</details>
