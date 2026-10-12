# Rocca (AES-based AEAD for 6G)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `CC BY (license of the ePrint 2022/116 paper; the reference implementation exists only in the paper's Appendix C)` · 🔴 abandoned

> AES-round-based 256-bit-key AEAD for 6G; \~5x OpenSSL AES-256-GCM at 16 KB on one laptop, much less elsewhere.

| | |
|---|---|
| **Beats** | OpenSSL AES-256-GCM / OpenSSL ChaCha20-Poly1305 |
| **Claimed result** | 16384B AEAD on i7-1068NG7 (Table 7): Rocca 150.95 Gbps vs OpenSSL AES-256-GCM 29.08 Gbps (\~5.2x, derived from page data) and vs ChaCha20-Poly1305 7.60 Gbps (\~19.9x, derived from page data). The paper text says 4.16x faster than SNOW-V and 3.10x faster than AES-256-CTR at 16384B; both figures come from the encryption-only rows. The lead shrinks on other CPUs and for small messages. On the i9-11900 (Appendix A, Table 9), 16384B AEAD is 175.12 vs AES-256-GCM 117.60 Gbps (\~1.5x, derived from page data), and Rocca is slower than AES-256-GCM at 256B (13.81 vs 15.57 Gbps) and at 64B (3.68 vs 4.51 Gbps). These numbers are for the revised Rocca (key feedforward in initialization). The original peer-reviewed ToSC 2021 paper reports 138.22 Gbps vs AES-256-GCM 30.59 and ChaCha20-Poly1305 7.57 Gbps at 16384B AEAD. |
| **Workload** | Single-thread throughput in encryption-only and AEAD modes, messages 64B to 16384B, 13-byte associated data. AEAD mode repeats init, AD, encryption, tag and finalization for every message. Rocca, SNOW-V, Tiaoxin-346 and AEGIS (from SUPERCOP) were built into OpenSSL (latest PDF says 3.1.0-dev; the Jan 2022 revision says 3.0.0-alpha3-Dev) and compared with OpenSSL's AES-256-GCM/CTR/CBC, ChaCha20 and ChaCha20-Poly1305, and SNOW-V-GCM. |
| **Metric** | throughput |
| **Hardware** | Main table (Table 7): Intel Core i7-1068NG7 @2.30GHz, 32GB RAM. Appendix A adds Intel i9-12900K, i9-11900 and i9-10910 (Windows 10 Pro / macOS Big Sur 11.4), plus ARM NEON builds on Apple M1, Apple A15 Bionic and Qualcomm Snapdragon 888. |
| **Adoption** | Peer-reviewed in IACR ToSC 2021(2) (presented at FSE 2022). ePrint 2022/116 is the full version: 4 revisions, last on 2023-03-16. The only standalone code found is a third-party C implementation of the original Rocca, ericlagergren/rocca (BSD-3-Clause, 5 stars, last commit 2022-01-28, no benchmarks). The successor Rocca-S has separate implementations such as jedisct1/zig-rocca-s (MIT, 21 stars). |
| **Links** | [benchmark](https://eprint.iacr.org/2022/116.pdf) |

## Verdict

The authors built Rocca into OpenSSL 3.1.0-dev and ran it single-threaded on an Intel i7-1068NG7 with 13-byte AD; compiler and flags are not stated. Rocca reached 150.95 Gbps AEAD at 16 KB, versus 29.08 Gbps for OpenSSL AES-256-GCM and 7.60 for ChaCha20-Poly1305. These are numbers for the revised, key-feedforward Rocca; the peer-reviewed ToSC 2021 original reported 138.22 vs 30.59 / 7.57 Gbps, and on the paper's i9-11900 the margin shrinks to 175.12 vs 117.60 Gbps.

## Use it when

- Benchmarking or research on AES-round-function AEADs (AEGIS, Tiaoxin, Rocca-S, HiAE), where Rocca is a standard point of comparison.
- Bulk AEAD of 8 KB and larger messages on AES-NI x86 or ARMv8 cores in a closed system you control at both ends. At 16 KB it led OpenSSL AES-256-GCM on every CPU in the paper, by 1.5x (i9-11900) to 5.9x (i9-10910), and on every x86 CPU in HiAE's independent tests (e.g. 250.16 vs 51.90 Gbps on a Ryzen 9 7950X).
- Pre-VAES Intel servers (Cascade Lake, Haswell class), where HiAE's own Table 10 puts Rocca ahead of HiAE on large messages (Xeon Gold 6242R: 156.60 vs 133.19 Gbps AEAD at 16 KB).
- Raw encryption-only use (keystream mode with no tag): 180.55 Gbps at 16 KB on the i7-1068NG7, versus 58.19 Gbps for AES-256-CTR.

## Skip it when

- Short messages (1 KB and under). Initialization and finalization each run 20 rounds, which the paper equates to about 1280 bytes of input per message. Rocca loses to AES-256-GCM at 256 B and 64 B on the paper's own i9-11900 (13.81 vs 15.57 and 3.68 vs 4.51 Gbps), Apple M1 and A15, and at 64 B on all seven x86 CPUs HiAE tested (e.g. 4.00 vs 12.57 Gbps on a Xeon W9-3495X).
- Anywhere key commitment matters (multi-recipient, password-based or message-franking designs). Takeuchi, Todo and Iwata (ToSC 2024(2)) give concrete FROB colliding inputs against the designers' latest version and show that no Rocca version is committing-secure.
- Settings where a nonce could repeat. The same paper shows universal forgery with practical data complexity under nonce misuse, even with an ideal keyed finalization. The original design also fell to a 2^128 full key recovery (Hosoyamada et al., ToSC 2022(3)).
- Production or compliance use: no standard, no FIPS status, no maintained library. The design has been superseded by Rocca-S, whose IETF individual draft (draft-nakano-rocca-s-06) is marked expired and which also has practical committing attacks (ePrint 2024/901).
- Interop with ericlagergren/rocca, the only standalone C implementation. It implements the pre-revision initialization, without the key feedforward (open issue #1 since 2024-10-28), so its ciphertexts do not match the revised cipher that produced the cited numbers.

## How it is fast

The 1024-bit (128-byte) state holds eight 128-bit words, and each round spends 4 independent aesenc and 4 128-bit XORs, absorbing 32 bytes of message. Every aesenc sits on its own short critical path, so the round pipelines well on AES-NI or ARMv8 AES units. The designers found this layout by searching a wider space of round functions than Jean and Nikolic's (FSE 2016), including a cost-free word permutation. Each 32-byte ciphertext block adds only 2 more AES rounds for keystream, instead of the \~14 per 16 bytes that AES-256-CTR needs plus GHASH.

## Compared with alternatives

libaegis is the deployable choice: it is maintained, and in HiAE's independent Table 10 AEGIS-128L beats Rocca at 1 KB and below on all seven x86 CPUs. HiAE is faster than Rocca on VAES-era CPUs, and Rocca is about 5x SNOW-V-GCM. Pick Rocca only for research baselines or large-message bulk encryption on pre-VAES Intel servers, and only if its committing and nonce-misuse weaknesses are acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop (C listing in Appendix C of ePrint 2022/116). A third-party alternative is ericlagergren/rocca: include/rocca.h plus src/rocca.c, with one-shot rocca_seal/rocca_open, BSD-3-Clause, original Rocca only. |
| **Dependencies** | none beyond libc and compiler intrinsics (immintrin.h). ericlagergren/rocca also uses memset_s from the optional C11 Annex K. |
| **Minimum toolchain** | Not documented. The paper never states a compiler or flags. ericlagergren/rocca builds its tests with -O2 -maes and passes the Apple-clang-only '-arch x86_64' flag, which suggests it was developed on macOS. |
| **Platforms** | x86-64 with AES-NI and SSE2 (the paper's Appendix C). The paper also benchmarks ARM NEON + AES builds on Apple M1, A15 and Snapdragon 888 but does not print them. ericlagergren/rocca supports x86-64 (SSE2 + AES) and ARMv8 (NEON + Crypto) and fails with #error elsewhere. |
| **Thread safety** | Not documented. The reference keeps all state in a caller-owned rocca_context, and ericlagergren/rocca keeps it on the stack per call with only const globals, so separate contexts share nothing. |
| **Drop-in for the baseline** | no |

## Gotchas

- Several incompatible 'Rocca' variants exist. The ToSC 2021 original has no key feedforward. The ePrint revision (last updated 2023-03-16) XORs the key into S[0] and S[4] after initialization; this is the version benchmarked at 150.95 Gbps. An intermediate version added a finalization key feedforward that was later removed. Rocca-S is a separate cipher with a 256-bit tag. Check test vectors against the exact version.
- ericlagergren/rocca mishandles partial blocks: rocca_seal copies the tail from the start of the plaintext and AD (memcpy(tmp, plaintext, remain)) and writes the partial ciphertext to dst[0]. Any input longer than 32 bytes that is not a multiple of 32 is therefore processed wrongly, and its tests (64-byte plaintexts, AD of 18 or 32 bytes) never exercise that path.
- The paper's streaming reference decrypts before the tag is checked and has no verify function. The caller must compute the tag with rocca_tag and compare it in constant time. Each encrypt or AD call zero-pads its own tail, so only the final chunk may be a non-multiple of 32 bytes.
- The headline 5.2x rests on a weak baseline. OpenSSL AES-256-GCM measures 29.08 Gbps on the i7-1068NG7 but 117.60 on the paper's i9-11900 and 57.87 on its i9-12900K, and the baseline numbers are identical to two decimals across ePrint revisions whose OpenSSL version label changes.

## Known shortcomings

- Cited page's numbers are for the revised Rocca (2023 ePrint, key feed-forward), not the original ToSC 2021 design, which was attacked. Original: 138.22 vs AES-GCM 30.59 / ChaCha20-Poly1305 7.57 Gbps (ratios derived). OpenSSL baselines were not re-measured across revisions; on an i9-11900 the gain is only \~1.5x and Rocca loses to AES-GCM at 64 and 256 bytes. Code is C.
- The revised Rocca (source of the numbers) is also broken: ToSC 2024(2) (Takeuchi-Todo-Iwata) gives FROB collisions and nonce-misuse universal forgery; the Rocca-S IETF draft -06 expired. Loses at &lt;= 256 B on the paper's i9-11900/M1/A15 and at 64 B on all 7 HiAE x86 CPUs; the OpenSSL GCM baseline varies 4x across the paper's CPUs (29.08 vs 117.60), inflating the 5.2x headline. No compiler or flags stated; reference code releases plaintext before the tag check. ericlagergren/rocca implements the original init without key feed-forward and has an untested tail-block bug.
- Enricher on the folded ericlagergren/rocca C port: partial blocks copy from the buffer start instead of offset nblocks\*32, so plaintexts longer than 32 bytes and not a multiple of 32 never round-trip (lengths 33/40/63/100 fail in rocca_open), tail ciphertext bytes are never written (in-place encryption leaves plaintext), AD tail bytes are unauthenticated (the README's own 42-byte AD example is affected), the ARM64 constant_time_compare_u128 accepts a forged tag with probability about 2^-24 (code analysis), there is no dst_len check and no portable fallback (#error). Do not use that port as an implementation; its test/test.c has only a baseline-free MB/s loop.

## Caveats and trade-offs

The numbers at benchmark_url (the latest ePrint PDF, 2023-03-16) are for the REVISED Rocca, which adds key feedforward in initialization after the Hosoyamada et al. ToSC 2022(3) attack: a full 256-bit key recovery with about 2^128 data and time, which breaks the original 256-bit claim. They are not for the original design. The original design's peer-reviewed numbers are in ToSC 2021(2): 138.22 vs 30.59 / 7.57 Gbps. Across ePrint revisions the OpenSSL baseline numbers stay identical to two decimals (AES-256-GCM 29.08 and ChaCha20-Poly1305 7.60 Gbps on the i7; 57.87 and 21.99 on the i9-12900K) while the OpenSSL version label and the Rocca numbers change. So the baselines were probably not re-measured. Compiler and flags are never stated. The advantage depends heavily on the CPU: only about 1.5x over AES-256-GCM on the i9-11900, and Rocca loses at 64B and 256B there. The code is C with AES-NI/NEON intrinsics, not C++. The design has since been superseded by Rocca-S.

The original Rocca was later shown to have practical forgery/committing weaknesses (see IACR ePrint 2024/901 and the ToSC 2024/2025 Derbez et al. and Takeuchi et al. papers) and was superseded by the redesigned Rocca-S. Treat these numbers as a data point on the AES-NI+SIMD 'wide round function' technique, not as a currently-recommended cipher.

## Maintenance

Abandoned as a design, usable only as a reference. The authors' last revision is dated 2023-03-16, the successor Rocca-S's IETF draft is expired, and the only standalone C code (ericlagergren/rocca, BSD-3-Clause, 5 stars) was last committed 2022-01-28, implements the pre-revision cipher, and has an unanswered issue saying so.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Table 7 of ePrint 2022/116 compares Rocca, built into OpenSSL, with OpenSSL AES-256-GCM and ChaCha20-Poly1305 on a named CPU (i7-1068NG7). ePrint 2022/116 is the full version and a major revision of the peer-reviewed ToSC 2021(2) paper, and that paper shows the same win (138.22 vs 30.59 Gbps). Tier A is impossible: the benchmark harness is not public and neither version states a compiler or flags. The only code is the reference C in Appendix C.
- **Verifier notes:** The record's name says 'original/pre-attack', but the numbers it cites (150.95 Gbps, OpenSSL 3.1.0-dev) belong to the revised Rocca in the 2023 ePrint revision. Either rename the entry to 'Rocca (revised, key feedforward)' or repoint benchmark_url to the ToSC 2021 paper (https://tosc.iacr.org/index.php/ToSC/article/download/8904/8480) and use its original-design numbers. The record's language field says C++, but the code is C. repo_url could point to ericlagergren/rocca (original Rocca, BSD-3-Clause), but that repo has no benchmarks.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compared_against_cpp_std_directly`, `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** ToSC 2021: 138.22 Gbps vs AES-256-GCM 30.59, ChaCha20-Poly1305 7.57 (Intel, AES-NI).; enricher code reading of the folded port
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2022/116.pdf>
  - <https://eprint.iacr.org/2022/116>
  - <https://eprint.iacr.org/archive/versions/2022/116>
  - <https://eprint.iacr.org/archive/2022/116/1643615825.pdf>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/8904/8480>
  - <https://api.crossref.org/works/10.46586/tosc.v2021.i2.1-30>
  - <https://api.crossref.org/works/10.46586/tosc.v2022.i3.123-151>
  - <https://github.com/jedisct1/zig-rocca-s>
  - <https://github.com/ericlagergren/rocca>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2022/116>
  - <https://eprint.iacr.org/2022/116.pdf>
  - <https://eprint.iacr.org/archive/versions/2022/116>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/8904/8480>
  - <https://api.crossref.org/works/10.46586/tosc.v2021.i2.1-30>
  - <https://api.crossref.org/works/10.46586/tosc.v2022.i3.123-151>
  - <https://api.crossref.org/works/10.46586/tosc.v2024.i2.85-117>
  - <https://api.crossref.org/works/10.46586/tosc.v2024.i1.135-157>
  - <https://eprint.iacr.org/2024/901>
  - <https://eprint.iacr.org/search?q=Rocca>
  - <https://eprint.iacr.org/2025/377.pdf>
  - <https://github.com/ericlagergren/rocca>
  - <https://github.com/ericlagergren/rocca/blob/main/include/rocca.h>
  - <https://github.com/ericlagergren/rocca/blob/main/src/rocca.c>
  - <https://github.com/ericlagergren/rocca/blob/main/src/rocca_amd64.h>
  - <https://github.com/ericlagergren/rocca/blob/main/test/test.c>
  - <https://github.com/ericlagergren/rocca/blob/main/test/Makefile>
  - <https://github.com/ericlagergren/rocca/issues/1>
  - <https://github.com/jedisct1/zig-rocca-s>
  - <https://datatracker.ietf.org/api/v1/doc/document/draft-nakano-rocca-s/>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:rocca-aes-based-aead-for-6g-original-pre-attack-version`) · [data/wave7/enrich/raw/paper_rocca_aes_based_aead_for_6g_original_pre_attack_version.json](../../../data/wave7/enrich/raw/paper_rocca_aes_based_aead_for_6g_original_pre_attack_version.json) (enrichment confidence 0.8)

</details>
