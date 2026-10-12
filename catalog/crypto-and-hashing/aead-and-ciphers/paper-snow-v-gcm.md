# SNOW-V-GCM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · ⚪ unknown

> SNOW-V stream cipher plus GHASH AEAD; \~13% faster than OpenSSL AES-256-GCM at 16 KB on an i7-8650U laptop.

| | |
|---|---|
| **Beats** | OpenSSL AES-256-GCM |
| **Claimed result** | Table 3, AEAD, 16384 B: 38.91 Gbps (SNOW-V-GCM C++) vs 34.42 Gbps (OpenSSL AES-256-GCM asm), \~13% faster (derived from page data). Roughly even at 2048 B (30.71 vs 30.49); AES-256-GCM wins at 1024 B and below (e.g. 64 B: 8.54 vs 5.16 Gbps). |
| **Workload** | Single-thread AEAD encryption throughput vs input size (64B-16384B) on a laptop CPU; SNOW-V-GCM implemented in C++ with AVX2/AES-NI/PCLMULQDQ intrinsics, benchmarked using code extracted from OpenSSL's own benchmarking harness against OpenSSL 3.0.0-dev (2019-04-01) AES-256-GCM assembly. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8650U @1.90GHz (Turbo up to 4.20GHz), single thread |
| **Compiler and flags** | Visual Studio 2017 + NASM, 'most possible optimizations switched on', native x64 build |
| **Adoption** | SNOW-V is a 3GPP/ETSI candidate stream cipher for 5G; no widely used, independently maintained open-source repo of SNOW-V-GCM was located in this search |
| **Links** | [benchmark](https://eprint.iacr.org/2018/1143.pdf) |

## Verdict

On one Intel i7-8650U laptop, single-threaded, with Visual Studio 2017 and 'most possible optimizations', the authors' C++ SNOW-V-GCM (AVX2/AES-NI/PCLMULQDQ intrinsics) reached 38.91 Gbps at 16 KB versus 34.42 Gbps for OpenSSL 3.0.0-dev (2019-04-01) AES-256-GCM asm. Both were measured with OpenSSL's own speed-loop code, reporting the best of several 1 to 3 second runs with key/IV setup per message. The curves cross near 2 KB, and AES-GCM leads below that.

## Use it when

- Research or interoperability work on the SNOW-V / 3GPP 256-bit algorithm candidates, where you need the published SNOW-V-GCM construction and its test vectors (Appendix C, Listing 3).
- Bulk AEAD of large messages (4 KB and up) on AES-NI + AVX2 CPUs from the Skylake/Kaby Lake era without VAES, where the paper's own data shows a small edge over OpenSSL AES-256-GCM.
- Platforms where AES-NI is missing: the paper argues SNOW-V stays usable with 16/32/64-bit registers while AES-256 becomes much slower, though it gives no SNOW-V-GCM numbers for that case.
- As a baseline when benchmarking newer AES-round-based AEADs (Rocca, AEGIS, HiAE), which all compare against SNOW-V.

## Skip it when

- Messages of 1 KB or less: in the paper's own Table 3 OpenSSL AES-256-GCM wins at 1024 B (27.22 vs 26.16 Gbps), 256 B (17.32 vs 13.93) and 64 B (8.54 vs 5.16).
- Modern CPUs with VAES/AVX-512 or Apple/AMD cores. In the authors' own SNOW-Vi paper, the SNOW-V keystream alone already loses to OpenSSL AES-256-CTR on an i7-1065G7 (58.52 vs 68.09 Gbps), a Ryzen 5 3600 (55.16 vs 68.84) and an Apple M1 (39.06 vs 58.61). HiAE's Table 10 has SNOW-V-GCM below OpenSSL 3.0 AES-256-GCM on all seven x86 CPUs it tested (e.g. 19.92 vs 51.90 Gbps on a Ryzen 9 7950X). HiAE's SNOW-V-GCM curve is nearly flat (13.04 Gbps at 16 KB vs 6.96 at 64 B on a Xeon W9-3495X), which points to a slow GHASH in that build, so that comparison probably understates the cipher.
- Production code: there is no maintained open-source SNOW-V-GCM library. The one C++ library found with SNOW-V-GCM (Protocol++, jpgreninger/protocolpp) is commercially licensed, and the paper's benchmarked AVX2/PCLMULQDQ build and harness were never published.
- Anything needing standards-track or FIPS-approved AEAD, nonce-misuse resistance or key commitment: it inherits every GCM restriction (unique IVs, SP 800-38D length limits) and adds SNOW-V's own limits of 2^64 keystream per key/IV and 2^64 IVs per key.
- Threat models with power side channels on microcontrollers: SNOW-SCA (HOST 2024) recovers the full 256-bit SNOW-V key from an unprotected Cortex-M4 implementation with fewer than 50 traces per key byte.

## How it is fast

SNOW-V is an LFSR plus FSM stream cipher. It uses two full AES encryption rounds (_mm_aesenc_si128 with zero round keys) as the FSM nonlinearity, keeps the two 16-bit-cell LFSRs in two 256-bit AVX2 registers so that one update does 8 LFSR steps, and outputs 128 bits of keystream per clock. On the i7-8650U that keystream alone ran at 58.25 Gbps versus 35.06 Gbps for OpenSSL AES-256-CTR asm at 16 KB. Wrapped in a PCLMULQDQ GHASH, it fell to 38.91 Gbps: the authors did not stitch GHASH into the keystream loop the way OpenSSL's AES-GCM asm does, and they say an assembly version could do better.

## Compared with alternatives

Pick it over libaegis (AEGIS-128L, maintained, about 3x AES-256-GCM) or HiAE only when you specifically need SNOW-V compatibility for 3GPP-related work. On speed alone, HiAE's Table 10 puts AEGIS-128L, Rocca and HiAE roughly 4x to 21x ahead of SNOW-V-GCM at 16 KB on every CPU tested, although its ARM SNOW-V builds were SSE2NEON conversions.

## Integration

| | |
|---|---|
| **Form** | source-drop (code listings in the paper's Appendices D and E; no repository or package) |
| **Dependencies** | An external GHASH implementation for the SIMD version (not provided). The 32-bit reference includes a slow bit-by-bit ghash_mult marked 'Informative'. |
| **Minimum toolchain** | Not documented. Benchmarks used Visual Studio 2017 (C++ with struct methods and templates); the SIMD listing needs a compiler with AVX2/AES-NI intrinsics such as _mm256_zextsi128_si256. |
| **Platforms** | x86-64 with AES-NI, SSSE3, AVX2 (plus PCLMULQDQ for a fast GHASH) for the SIMD code; the 32-bit reference is portable and endianness-free. The paper also reports an ARM NEON SNOW-V keystream (iPhone X A11) but no NEON SNOW-V-GCM. |
| **Thread safety** | Not documented. The reference keeps all cipher state in a per-call SnowV256/SnowV32 object on the stack, with only read-only globals (S-box, constants), so separate calls share no mutable state. |
| **Drop-in for the baseline** | no |

## Gotchas

- The printed SIMD snowv_gcm_decrypt calls SNOWV_ENCDEC(snowv, ciphertext + i, plaintext + i), but the macro's signature is (snowv, out, in). As printed, it writes into the ciphertext buffer instead of producing plaintext. Fix it and check against the SNOW-V-GCM test vectors before any use.
- The SIMD loops load and store whole 16-byte blocks, so a message whose length is not a multiple of 16 is over-read by up to 15 bytes. The output buffer must reserve length + 16 bytes, as the listing's comments say. Decrypt also subtracts 16 from ciphertext_sz without checking its size first.
- H is the first keystream block of each (key, IV) pair, not a per-key constant as in AES-GCM. Any precomputed GHASH table of H powers must therefore be rebuilt for every message, which hurts short messages (derived from the mode definition).
- The 32-bit reference decrypt compares the tag with an early-exit byte loop (not constant time) and calls exit(1) on failure. The SIMD version compares with _mm_test_all_zeros instead.

## Known shortcomings

- Compiler flags vague; the benchmark harness and PCLMULQDQ build are not public. The HiAE paper reports SNOW-V-GCM slower than AES-GCM on all modern x86 CPUs, and the original gain was only \~13% on large messages.
- Not faster on current CPUs: the authors' own SNOW-Vi paper (ePrint 2021/236) measures the SNOW-V keystream alone below OpenSSL AES-256-CTR on i7-1065G7, Ryzen 3600 and M1, and HiAE's Table 10 has SNOW-V-GCM slower than AES-GCM on all 7 x86 CPUs. No library: code exists only in paper appendices (GHASH extension not printed); the printed SIMD decrypt swaps arguments to SNOWV_ENCDEC, over-reads the tail, and the 32-bit reference tag compare is not constant-time.

## Caveats and trade-offs

Single 2018-era ultrabook CPU against a pre-release OpenSSL snapshot (3.0.0-dev, 2019-04-01); the win is small (\~13%) and only above \~2 KB. The paper prints the SNOW-V AVX2 keystream code and a portable SNOW-V-GCM reference, but not the PCLMULQDQ-optimized GCM build or the harness that produced Table 3. Counter-evidence: HiAE (ePrint 2025/377, Table 10) measured the official SNOW-V-GCM implementation well below OpenSSL 3.0 AES-256-GCM on every modern x86 CPU tested (e.g. 19.92 vs 51.90 Gbps on Ryzen 9 7950X, 13.04 vs 36.49 Gbps on Xeon W9-3495X at 16 KB). No maintained public repo, so usability is 'reference'.

Only faster than OpenSSL AES-256-GCM for larger messages (roughly &gt;=4KB); for short messages (&lt;2KB) OpenSSL's hand-tuned, instruction-stitched assembly wins outright. The paper's own C++ implementation does not get GHASH "for free" the way OpenSSL's asm does.

## Maintenance

A paper-only design (ePrint 2018/1143, last revised 2019-08-27, CC BY) with no maintained implementation; the authors' 2021 SNOW-Vi paper and HiAE's 2025 benchmarks both show it losing to AES on newer CPUs, so treat it as a reference, not a deployable library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed paper (ePrint 2018/1143, published by the IACR in FSE 2020). Table 3 shows SNOW-V-GCM beating OpenSSL 3.0.0-dev AES-256-GCM asm at 16 KB on a named i7-8650U. It falls short of A: compiler flags are only 'most possible optimizations switched on', the benchmark harness adapted from OpenSSL is not published, and the benchmarked AVX2/PCLMULQDQ SNOW-V-GCM build is not printed (Appendix D has a portable GHASH reference, and Appendix E has AVX2 code only for the SNOW-V keystream).
- **Verifier notes:** Numbers and setup (VS2017 + NASM, i7-8650U, single thread) match the paper exactly. The tier drops from A to B because neither the flags nor the benchmarked code/harness are public. Consider flagging this entry, because a later third-party measurement (the HiAE paper) contradicts the speed win on current CPUs.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2018/1143.pdf>
  - <https://eprint.iacr.org/2018/1143>
  - <https://eprint.iacr.org/2025/377.pdf>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2018/1143>
  - <https://eprint.iacr.org/2018/1143.pdf>
  - <https://eprint.iacr.org/2025/377.pdf>
  - <https://eprint.iacr.org/2021/236>
  - <https://eprint.iacr.org/2021/236.pdf>
  - <https://eprint.iacr.org/2021/1047>
  - <https://eprint.iacr.org/2024/428>
  - <https://eprint.iacr.org/2026/2197>
  - <https://eprint.iacr.org/search?q=SNOW-V>
  - <https://api.crossref.org/works?query.bibliographic=SNOW-V+stream+cipher>
  - <https://github.com/Concyclics/HiAE>
  - <https://github.com/jpgreninger/protocolpp>
  - <https://github.com/search?q=snowv&type=code>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:snow-v-gcm`) · [data/wave7/enrich/raw/paper_snow_v_gcm.json](../../../data/wave7/enrich/raw/paper_snow_v_gcm.json) (enrichment confidence 0.8)

</details>
