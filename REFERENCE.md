# Reference

No license, unclear/non-OSI license, mixed licensing, or paper-only. Study the idea and reimplement clean-room; do not copy the code.

## Verified

### crypto-and-hashing

#### aead-and-ciphers

##### MORUS-1280  `C`  `no license`  `abandoned`  `Tier B`

CAESAR-finalist AND/XOR/rotate AEAD in AVX2 C; edges out SUPERCOP AES-256-GCM on message-only and 64-byte inputs, loses elsewhere, and is broken.

**Beats:** AES-256-GCM — eBACS (supercop-20260627) measured MORUS-1280-256 v1 (avx2 code, Debian clang 19.1.7 -march=native -O3) against SUPERCOP's fastest AES-256-GCM (Dolbeau's AES-NI intrinsics, clang -O2) on one Raptor Cove P-core of an Intel Core 5 210H. By median cycles/byte, MORUS wins 7 of 15 sections (long+0 encrypt 0.69 vs 1.07, 1.55x; long+long encrypt 0.66 vs 0.70, 1.06x; 64+64 1.11-1.18x), ties 1536+1536 encrypt (0.81 vs 0.82) and loses the other 7: long+long and 1536+1536 decrypt/forgery at about 0.85x, and AD-only (0+long) at about 0.5x.

**Known shortcoming:** The 1.06x is cherry-picked: MORUS loses long-message decryption (0.67 vs 0.57 cycles/byte) and AD-only processing (~0.5x); it wins only long encryption with no AD (1.55x). Did not reach the CAESAR final portfolio; license unclear.

**Known shortcoming:** Cryptographically broken: ePrint 2019/172 reduces attack cost to ~2^76, and Linux removed MORUS in 2019 as broken. Wins only 7 of 15 eBACS sections (loses 7, ties 1); AES-128-GCM (0.63) beats MORUS-1280-128 (0.67 cycles/byte). The mirrored code is v1, not the round-3 v2; plaintext is released before the tag check; unprefixed exported symbols; no license header.

**How:** The state is five 256-bit words, one __m256i each, and every 32-byte block costs one state update: five chained rounds of XOR, AND, 64-bit-lane rotations (slli/srli/or) and _mm256_permute4x64_epi64 word rotations. The keystream is only S0 ^ rot192(S1) ^ (S2 & S3). There are no AES rounds, table lookups or GF(2^128) multiplications, and authentication comes from the same state update that encrypts, so no separate GHASH pass is needed. The rounds are serially dependent (round i reads round i-1's output), which caps it near 0.66-0.69 cycles/byte on long inputs. That is the designers' Haswell figure (0.69 cpb, gcc 4.8.1 -O3 -mavx2), and unlike AES-round designs it does not get faster with AES-NI or VAES.

**Use it when:**
- Reproducing or extending eBACS/SUPERCOP AEAD comparisons. supercop-20260627 still measures it, as both morus1280256v1 and morus1280256v2.
- Cryptanalysis or teaching on non-AES AND/XOR/rotate stream-cipher AEADs, such as reproducing the linear-correlation attacks of Ashur et al. (ePrint 2018/464) or Shi et al. (ePrint 2019/172).
- Studying SIMD mapping of a wide state: the avx2 (five __m256i), sse2 and portable ref64 versions of the same cipher sit side by side, and on this host they measure 4990, 6820 and 8569 cycles respectively in SUPERCOP's per-implementation timing column.
- Checking legacy MORUS v1 (round 1/2) test vectors. This code produces v1 tags, which differ from v2.

**Skip it when:**
- Any production use. Shi et al. (CRYPTO 2019, ePrint 2019/172) found correlation-2^-38 trails in all full MORUS versions, which cuts the MORUS-1280-256 attack from 2^152 to about 2^76, far below its 256-bit confidentiality claim. Linux removed MORUS in July 2019 (commit 5cb97700beaa), calling it 'cryptographically broken'.
- AD-heavy traffic. With AD only (0+long) it runs at 0.65 cycles/byte against 0.32-0.33 for AES-256-GCM, about 2x slower, and 1536+1536 decrypt/forgery is 0.82 against 0.70.
- Decrypt-dominated bulk with AD: long+long decrypt and forgery are 0.67 against 0.57 cycles/byte (0.85x).
- Seeking a faster AEAD on AES-NI CPUs. On the same page AES-128-GCM (0.63) already beats MORUS-1280-128 (0.67) on long+long encrypt, and AEGIS-128L runs at 0.21, about 3x faster.
- Any setting where a nonce could repeat. The spec voids its claims under reuse, and Vaudenay and Vizar (ePrint 2017/1147) show universal forgery and decryption from about 20 nonce-reusing queries (worked out for MORUS-640, which has the same structure).

**Vs siblings:** Practically never for new systems. On the same eBACS page, libaegis's AEGIS-128L (0.21) and AEGIS-128X2 (0.11 cycles/byte long+long) are 3-6x faster and maintained, Tiaoxin-346 (0.15) and AEZ (0.26) are also faster, and the bitsliced AEGIS sibling covers CPUs without AES-NI. Pick MORUS only to reproduce CAESAR-era or eBACS comparisons, or to study non-AES AND/rotate designs.

**Gotchas:**
- This is MORUS v1. Round-3 MORUS v2 changed tag generation and raised finalization from 8 to 10 steps, so v1 tags do not match v2 implementations. SUPERCOP's current morus1280256v2 is about 6% slower on 64+64 encrypt (4.49 vs 4.22 cycles/byte), which shrinks the short-message win over AES-256-GCM (4.70) to 1.05x.
- morus_enc_aut_step and morus_dec_aut_step are declared plain (non-static) inline. Under C99 inline rules, an uninlined call has no external definition. eBACS's gcc -Os build fails to link for this reason, with undefined references to both functions. The file also exports unprefixed symbols (morus_stateupdate, morus_initialization and others), which eBACS flags as namespace violations and which collide if two MORUS variants are linked together. Make them static when vendoring.
- Decrypt writes the plaintext into m before the tag check and does not wipe it on failure, although the spec says unverified plaintext must not be released. Key and state are never zeroized. The tag comparison itself is a branch-free sum loop.
- Associated data goes through morus_enc_aut_step, which computes and discards a keystream block, so AD costs as much as message bytes. That explains the 2x loss on AD-only workloads.

**Status:** Abandoned. The mirror is frozen at supercop-20160716 (its own open issue #4 calls it stale), no MORUS source file has a license header, and the algorithm was dropped from Linux in 2019 as broken, so this is for reference and study only.

[repo](https://github.com/floodyberry/supercop) · [benchmark](https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html)

##### Rocca (AES-based AEAD for 6G)  `C`  `CC BY (license of the ePrint 2022/116 paper; the reference implementation exists only in the paper's Appendix C)`  `abandoned`  `Tier B`

AES-round-based 256-bit-key AEAD for 6G; ~5x OpenSSL AES-256-GCM at 16 KB on one laptop, much less elsewhere.

**Beats:** OpenSSL AES-256-GCM / OpenSSL ChaCha20-Poly1305 — The authors built Rocca into OpenSSL 3.1.0-dev and ran it single-threaded on an Intel i7-1068NG7 with 13-byte AD; compiler and flags are not stated. Rocca reached 150.95 Gbps AEAD at 16 KB, versus 29.08 Gbps for OpenSSL AES-256-GCM and 7.60 for ChaCha20-Poly1305. These are numbers for the revised, key-feedforward Rocca; the peer-reviewed ToSC 2021 original reported 138.22 vs 30.59 / 7.57 Gbps, and on the paper's i9-11900 the margin shrinks to 175.12 vs 117.60 Gbps.

**Known shortcoming:** Cited page's numbers are for the revised Rocca (2023 ePrint, key feed-forward), not the original ToSC 2021 design, which was attacked. Original: 138.22 vs AES-GCM 30.59 / ChaCha20-Poly1305 7.57 Gbps (ratios derived). OpenSSL baselines were not re-measured across revisions; on an i9-11900 the gain is only ~1.5x and Rocca loses to AES-GCM at 64 and 256 bytes. Code is C.

**Known shortcoming:** The revised Rocca (source of the numbers) is also broken: ToSC 2024(2) (Takeuchi-Todo-Iwata) gives FROB collisions and nonce-misuse universal forgery; the Rocca-S IETF draft -06 expired. Loses at <= 256 B on the paper's i9-11900/M1/A15 and at 64 B on all 7 HiAE x86 CPUs; the OpenSSL GCM baseline varies 4x across the paper's CPUs (29.08 vs 117.60), inflating the 5.2x headline. No compiler or flags stated; reference code releases plaintext before the tag check. ericlagergren/rocca implements the original init without key feed-forward and has an untested tail-block bug.

**Independent measurement:** ToSC 2021: 138.22 Gbps vs AES-256-GCM 30.59, ChaCha20-Poly1305 7.57 (Intel, AES-NI).

**How:** The 1024-bit (128-byte) state holds eight 128-bit words, and each round spends 4 independent aesenc and 4 128-bit XORs, absorbing 32 bytes of message. Every aesenc sits on its own short critical path, so the round pipelines well on AES-NI or ARMv8 AES units. The designers found this layout by searching a wider space of round functions than Jean and Nikolic's (FSE 2016), including a cost-free word permutation. Each 32-byte ciphertext block adds only 2 more AES rounds for keystream, instead of the ~14 per 16 bytes that AES-256-CTR needs plus GHASH.

**Use it when:**
- Benchmarking or research on AES-round-function AEADs (AEGIS, Tiaoxin, Rocca-S, HiAE), where Rocca is a standard point of comparison.
- Bulk AEAD of 8 KB and larger messages on AES-NI x86 or ARMv8 cores in a closed system you control at both ends. At 16 KB it led OpenSSL AES-256-GCM on every CPU in the paper, by 1.5x (i9-11900) to 5.9x (i9-10910), and on every x86 CPU in HiAE's independent tests (e.g. 250.16 vs 51.90 Gbps on a Ryzen 9 7950X).
- Pre-VAES Intel servers (Cascade Lake, Haswell class), where HiAE's own Table 10 puts Rocca ahead of HiAE on large messages (Xeon Gold 6242R: 156.60 vs 133.19 Gbps AEAD at 16 KB).
- Raw encryption-only use (keystream mode with no tag): 180.55 Gbps at 16 KB on the i7-1068NG7, versus 58.19 Gbps for AES-256-CTR.

**Skip it when:**
- Short messages (1 KB and under). Initialization and finalization each run 20 rounds, which the paper equates to about 1280 bytes of input per message. Rocca loses to AES-256-GCM at 256 B and 64 B on the paper's own i9-11900 (13.81 vs 15.57 and 3.68 vs 4.51 Gbps), Apple M1 and A15, and at 64 B on all seven x86 CPUs HiAE tested (e.g. 4.00 vs 12.57 Gbps on a Xeon W9-3495X).
- Anywhere key commitment matters (multi-recipient, password-based or message-franking designs). Takeuchi, Todo and Iwata (ToSC 2024(2)) give concrete FROB colliding inputs against the designers' latest version and show that no Rocca version is committing-secure.
- Settings where a nonce could repeat. The same paper shows universal forgery with practical data complexity under nonce misuse, even with an ideal keyed finalization. The original design also fell to a 2^128 full key recovery (Hosoyamada et al., ToSC 2022(3)).
- Production or compliance use: no standard, no FIPS status, no maintained library. The design has been superseded by Rocca-S, whose IETF individual draft (draft-nakano-rocca-s-06) is marked expired and which also has practical committing attacks (ePrint 2024/901).
- Interop with ericlagergren/rocca, the only standalone C implementation. It implements the pre-revision initialization, without the key feedforward (open issue #1 since 2024-10-28), so its ciphertexts do not match the revised cipher that produced the cited numbers.

**Vs siblings:** libaegis is the deployable choice: it is maintained, and in HiAE's independent Table 10 AEGIS-128L beats Rocca at 1 KB and below on all seven x86 CPUs. HiAE is faster than Rocca on VAES-era CPUs, and Rocca is about 5x SNOW-V-GCM. Pick Rocca only for research baselines or large-message bulk encryption on pre-VAES Intel servers, and only if its committing and nonce-misuse weaknesses are acceptable.

**Gotchas:**
- Several incompatible 'Rocca' variants exist. The ToSC 2021 original has no key feedforward. The ePrint revision (last updated 2023-03-16) XORs the key into S[0] and S[4] after initialization; this is the version benchmarked at 150.95 Gbps. An intermediate version added a finalization key feedforward that was later removed. Rocca-S is a separate cipher with a 256-bit tag. Check test vectors against the exact version.
- ericlagergren/rocca mishandles partial blocks: rocca_seal copies the tail from the start of the plaintext and AD (memcpy(tmp, plaintext, remain)) and writes the partial ciphertext to dst[0]. Any input longer than 32 bytes that is not a multiple of 32 is therefore processed wrongly, and its tests (64-byte plaintexts, AD of 18 or 32 bytes) never exercise that path.
- The paper's streaming reference decrypts before the tag is checked and has no verify function. The caller must compute the tag with rocca_tag and compare it in constant time. Each encrypt or AD call zero-pads its own tail, so only the final chunk may be a non-multiple of 32 bytes.
- The headline 5.2x rests on a weak baseline. OpenSSL AES-256-GCM measures 29.08 Gbps on the i7-1068NG7 but 117.60 on the paper's i9-11900 and 57.87 on its i9-12900K, and the baseline numbers are identical to two decimals across ePrint revisions whose OpenSSL version label changes.

**Status:** Abandoned as a design, usable only as a reference. The authors' last revision is dated 2023-03-16, the successor Rocca-S's IETF draft is expired, and the only standalone C code (ericlagergren/rocca, BSD-3-Clause, 5 stars) was last committed 2022-01-28, implements the pre-revision cipher, and has an unanswered issue saying so.

[benchmark](https://eprint.iacr.org/2022/116.pdf)

##### SNOW-V-GCM  `C++`  `no license`  `unknown`  `Tier B`

SNOW-V stream cipher plus GHASH AEAD; ~13% faster than OpenSSL AES-256-GCM at 16 KB on an i7-8650U laptop.

**Beats:** OpenSSL AES-256-GCM — On one Intel i7-8650U laptop, single-threaded, with Visual Studio 2017 and 'most possible optimizations', the authors' C++ SNOW-V-GCM (AVX2/AES-NI/PCLMULQDQ intrinsics) reached 38.91 Gbps at 16 KB versus 34.42 Gbps for OpenSSL 3.0.0-dev (2019-04-01) AES-256-GCM asm. Both were measured with OpenSSL's own speed-loop code, reporting the best of several 1 to 3 second runs with key/IV setup per message. The curves cross near 2 KB, and AES-GCM leads below that.

**Known shortcoming:** Compiler flags vague; the benchmark harness and PCLMULQDQ build are not public. The HiAE paper reports SNOW-V-GCM slower than AES-GCM on all modern x86 CPUs, and the original gain was only ~13% on large messages.

**Known shortcoming:** Not faster on current CPUs: the authors' own SNOW-Vi paper (ePrint 2021/236) measures the SNOW-V keystream alone below OpenSSL AES-256-CTR on i7-1065G7, Ryzen 3600 and M1, and HiAE's Table 10 has SNOW-V-GCM slower than AES-GCM on all 7 x86 CPUs. No library: code exists only in paper appendices (GHASH extension not printed); the printed SIMD decrypt swaps arguments to SNOWV_ENCDEC, over-reads the tail, and the 32-bit reference tag compare is not constant-time.

**How:** SNOW-V is an LFSR plus FSM stream cipher. It uses two full AES encryption rounds (_mm_aesenc_si128 with zero round keys) as the FSM nonlinearity, keeps the two 16-bit-cell LFSRs in two 256-bit AVX2 registers so that one update does 8 LFSR steps, and outputs 128 bits of keystream per clock. On the i7-8650U that keystream alone ran at 58.25 Gbps versus 35.06 Gbps for OpenSSL AES-256-CTR asm at 16 KB. Wrapped in a PCLMULQDQ GHASH, it fell to 38.91 Gbps: the authors did not stitch GHASH into the keystream loop the way OpenSSL's AES-GCM asm does, and they say an assembly version could do better.

**Use it when:**
- Research or interoperability work on the SNOW-V / 3GPP 256-bit algorithm candidates, where you need the published SNOW-V-GCM construction and its test vectors (Appendix C, Listing 3).
- Bulk AEAD of large messages (4 KB and up) on AES-NI + AVX2 CPUs from the Skylake/Kaby Lake era without VAES, where the paper's own data shows a small edge over OpenSSL AES-256-GCM.
- Platforms where AES-NI is missing: the paper argues SNOW-V stays usable with 16/32/64-bit registers while AES-256 becomes much slower, though it gives no SNOW-V-GCM numbers for that case.
- As a baseline when benchmarking newer AES-round-based AEADs (Rocca, AEGIS, HiAE), which all compare against SNOW-V.

**Skip it when:**
- Messages of 1 KB or less: in the paper's own Table 3 OpenSSL AES-256-GCM wins at 1024 B (27.22 vs 26.16 Gbps), 256 B (17.32 vs 13.93) and 64 B (8.54 vs 5.16).
- Modern CPUs with VAES/AVX-512 or Apple/AMD cores. In the authors' own SNOW-Vi paper, the SNOW-V keystream alone already loses to OpenSSL AES-256-CTR on an i7-1065G7 (58.52 vs 68.09 Gbps), a Ryzen 5 3600 (55.16 vs 68.84) and an Apple M1 (39.06 vs 58.61). HiAE's Table 10 has SNOW-V-GCM below OpenSSL 3.0 AES-256-GCM on all seven x86 CPUs it tested (e.g. 19.92 vs 51.90 Gbps on a Ryzen 9 7950X). HiAE's SNOW-V-GCM curve is nearly flat (13.04 Gbps at 16 KB vs 6.96 at 64 B on a Xeon W9-3495X), which points to a slow GHASH in that build, so that comparison probably understates the cipher.
- Production code: there is no maintained open-source SNOW-V-GCM library. The one C++ library found with SNOW-V-GCM (Protocol++, jpgreninger/protocolpp) is commercially licensed, and the paper's benchmarked AVX2/PCLMULQDQ build and harness were never published.
- Anything needing standards-track or FIPS-approved AEAD, nonce-misuse resistance or key commitment: it inherits every GCM restriction (unique IVs, SP 800-38D length limits) and adds SNOW-V's own limits of 2^64 keystream per key/IV and 2^64 IVs per key.
- Threat models with power side channels on microcontrollers: SNOW-SCA (HOST 2024) recovers the full 256-bit SNOW-V key from an unprotected Cortex-M4 implementation with fewer than 50 traces per key byte.

**Vs siblings:** Pick it over libaegis (AEGIS-128L, maintained, about 3x AES-256-GCM) or HiAE only when you specifically need SNOW-V compatibility for 3GPP-related work. On speed alone, HiAE's Table 10 puts AEGIS-128L, Rocca and HiAE roughly 4x to 21x ahead of SNOW-V-GCM at 16 KB on every CPU tested, although its ARM SNOW-V builds were SSE2NEON conversions.

**Gotchas:**
- The printed SIMD snowv_gcm_decrypt calls SNOWV_ENCDEC(snowv, ciphertext + i, plaintext + i), but the macro's signature is (snowv, out, in). As printed, it writes into the ciphertext buffer instead of producing plaintext. Fix it and check against the SNOW-V-GCM test vectors before any use.
- The SIMD loops load and store whole 16-byte blocks, so a message whose length is not a multiple of 16 is over-read by up to 15 bytes. The output buffer must reserve length + 16 bytes, as the listing's comments say. Decrypt also subtracts 16 from ciphertext_sz without checking its size first.
- H is the first keystream block of each (key, IV) pair, not a per-key constant as in AES-GCM. Any precomputed GHASH table of H powers must therefore be rebuilt for every message, which hurts short messages (derived from the mode definition).
- The 32-bit reference decrypt compares the tag with an early-exit byte loop (not constant time) and calls exit(1) on failure. The SIMD version compares with _mm_test_all_zeros instead.

**Status:** A paper-only design (ePrint 2018/1143, last revised 2019-08-27, CC BY) with no maintained implementation; the authors' 2021 SNOW-Vi paper and HiAE's 2025 benchmarks both show it losing to AES on newer CPUs, so treat it as a reference, not a deployable library.

[benchmark](https://eprint.iacr.org/2018/1143.pdf)

#### crypto-hashes

##### j-lanes tree hashing mode and j-lanes SHA-256 (Gueron)  `any`  `no license`  `finished`  `Tier B`

Tree-hash mode that runs one message as 4 interleaved SHA-256 lanes on AVX; 2-2.5x OpenSSL 1.0.1c, different digests.

**Beats:** OpenSSL SHA-256 (v1.0.1c) — On a Core i7-3770 (Ivy Bridge; Hyper-Threading, Turbo and SpeedStep off; RDTSC, minimum of 5 runs of 100,000 iterations), AVX 4-lanes SHA-256 took 6.75 c/B at 2KB and 5.05 c/B at 128KB, against 13.27 and 12.78 c/B for OpenSSL 1.0.1c's serial SHA-256 (1.97-2.53x) and 10.45-10.09 c/B for the authors' improved n-SMS serial code (1.55-2x). No compiler or flags are given, and the outputs are j-lanes digests, not SHA-256 digests.

**Known shortcoming:** New tree-hashing mode: digests differ from standard SHA-256, so it is not a drop-in replacement. Published in a weak venue (JIS 2013); measured on an i7-3770 (Ivy Bridge).

**Known shortcoming:** No code, no compiler or flags. Compared against OpenSSL 1.0.1c on a 2012 CPU with no SHA-NI comparison (minio's Ryzen SHA-extension figure ~1.9 cycles/byte vs the paper's best 5.05, different CPUs). The 2012 paper and the 2014 spec (ePrint 2014/170) produce incompatible digests (per-lane IVs). Nearest shipping code, ISA-L mh_sha256, is not digest-compatible. Lead over BLAKE-512 only ~5-7%.

**How:** Serial SHA-256 is one dependent chain of compression calls. Slicing turns one message into j independent messages, which the authors' S-HASH multi-buffer kernel runs with one slice per 32-bit lane of a 128-bit AVX register, so each SIMD Update compresses 4 blocks at once. For a 256x-byte message this costs 4x+7 Updates instead of 4x+1: one padding block per lane plus 3 serial Updates to wrap the 128 bytes of digests. The 4x bulk Updates run 4-wide. Word interleaving means plain sequential loads put each word in the right lane with no transpose. Without SIMD the mode loses: calling OpenSSL once per slice took 13.57 c/B against 12.87 c/B for plain OpenSSL at 8KB.

**Use it when:**
- You own both ends of the format and can define a new digest, for example signed boot or firmware images or an internal integrity manifest, and messages are at least a few KB. The paper measured 1.97x at 2KB rising to 2.53x at 128KB against OpenSSL 1.0.1c.
- One long message at a time, where multi-buffer hashing (S-HASH) has nothing to run in parallel.
- x86 cores with 128-bit or 256-bit SIMD but no SHA extensions (the paper used Ivy Bridge AVX; the 2014 follow-up also measured Haswell AVX2 with j=8).
- As a design reference when specifying a SIMD-friendly tree mode: the 2014 spec gives slicing rules, IV derivation and test vectors.

**Skip it when:**
- Anywhere a standard SHA-256 value is expected: TLS, HMAC interop, signature schemes, Git or any content address shared with third parties. The digest is different by construction.
- Short messages. The fixed wrap and per-lane padding cost is only amortized on longer inputs; the paper says gains are fully realized only for 'sufficiently long' messages, and Intel's similar Multi-Hash paper says benefits diminish below about 1KB.
- When you need code today. Nothing was released. The nearest shipping code, Intel ISA-L crypto's mh_sha256 (16 word-interleaved segments), pads and wraps differently, so its digests are not j-lanes digests.
- CPUs with SHA extensions. The paper predates them and never compares against them. minio/sha256-simd's README reports 1979 MB/s for SHA-extension SHA-256 on a 3.7 GHz Ryzen 7 2700X, about 1.9 c/B, well under the paper's best 4-lanes figure of 5.05 c/B. The CPUs differ, so treat that comparison as rough.
- Settings that need a standardized or formally analysed mode. Security is argued only by pointing to general tree-hashing theory, and the author's own recommended j moved from 8 (2012) to 16 (2014).

**Vs siblings:** Pick j-lanes over S-HASH only when there is a single long message in flight and you control the digest format. S-HASH needs many independent messages but keeps standard SHA-256 outputs. Against minio/sha256-simd, which is shipping Go code that produces standard digests (with SHA-extension, ARM64 and AVX-512 multi-buffer paths), j-lanes is only a design option for a new format on hardware without SHA instructions.

**Gotchas:**
- There are two incompatible versions. The 2012 mode uses the standard SHA-256 IV everywhere, while the 2014 spec prepends per-lane prefix blocks (lane index, j, a mode byte and 'SHA256'), which gives different IVs and different digests. Pin the spec version and j, because the digest depends on both.
- The 2014 spec text slices by 32-bit words, but its j=4 test-vector lanes are interleaved in 64-byte blocks (lane 0 is message bytes 0-63, 256-319, 512-575 and 768-831). Resolve this against the vectors before implementing.
- With j=4, a length not divisible by 256 bytes leaves at least one slice a different length and needs special last-Update handling (the paper calls the cost negligible). Very short messages give empty slices, which are hashed as the empty message. Choosing j above the SIMD width adds wrap Updates: at 8KB, 16-lanes needs 153 Updates against 135 for 4-lanes.
- The SHA-3 comparison in Fig. 4 is close. At 8KB, 4-lanes SHA-256 took 5.46 c/B against 5.74 for 4-lanes BLAKE-512 and 5.82 for plain BLAKE-512, a margin of about 5-7%.

**Status:** This is finished research: ePrint 2012/476, republished in Journal of Information Security 4(1):7-11 (2013, a SCIRP journal, 2 Crossref citations), plus a 2014 follow-up spec with test vectors (ePrint 2014/170, CC BY). No code or standard adoption turned up in the sources read, and the closest shipping relative, ISA-L's mh_sha256, is not digest-compatible.

[benchmark](https://eprint.iacr.org/2012/476.pdf)

##### KangarooTwelve (XKCP)  `C`  `CC0-1.0 for most files, with per-file exceptions: CRYPTOGAMS BSD-style/GPL (AVX2 and AVX-512 KeccakP-1600 asm), Apache-2.0 OR ISC OR MIT (ARMv8-A cores), and Brian Gladman's permissive license (brg_endian.h)`  `active`  `Tier B`

Keccak team's C package; its KangarooTwelve XOF hashes long messages 5-8x faster than SHAKE128 via SIMD tree hashing.

**Beats:** SHAKE128 (FIPS 202), SHA-256 and SHA-512, using the fastest implementations available to the authors, cross-checked with eBASH; 'often' OpenSSL for the traditional hashes — In the designers' peer-reviewed paper (ACNS 2018, Table 2; compiler not stated), single-core long-message KangarooTwelve ran at 0.55/1.22/1.44 cycles/byte on a Core i7-7800X (AVX-512), i5-6500 and i5-4570 (AVX2), against 4.28/5.56/7.09 for SHAKE128 and 6.65/6.91/9.27 for SHA-256 (the fastest implementations found, often OpenSSL, cross-checked against eBASH) on CPUs without SHA-NI. Independent eBASH 2026 runs at about 16 KiB show K12 about 1.8x faster than SHAKE128 but slightly slower than SHA-NI SHA-256 (2.47 vs 2.21 cycles/byte on Tiger Lake).

**Known shortcoming:** KangarooTwelve's '2x SHAKE128' holds for low-end CPUs and short messages; on modern x86 eBASH shows it slower than SHA-NI SHA-256. The fast x86 assembly comes from CRYPTOGAMS under its own license, not CC0.

**Known shortcoming:** K12 evidence is the designers' 2018 paper on pre-SHA-NI CPUs with no compiler stated; eBASH 2026 at ~16 KiB has K12 slower than SHA-NI SHA-256 (2.47 vs 2.21 cycles/byte Tiger Lake, 2.93 vs 2.02 Zen 4) and ~1.8x faster than SHAKE128. SIMD path engages only when one Update call carries >= 16/32/64 KiB; no multithreading API. Not FIPS-approved. Build needs xsltproc + GNU make; MSVC gets noAsm only. CVE-2022-37454 buffer overflow (fixed); open #171 UBSan misaligned loads in AVX2 times4.

**Independent measurement:** ePrint 2016/770 (ACNS 2018) Table 2: K12 0.55/1.22/1.44 vs SHAKE128 4.28/5.56/7.09 cycles/byte.

**Independent measurement:** eBASH ~16 KiB: K12 2.47 vs SHA-256 (SHA-NI) 2.21 cycles/byte (Tiger Lake); 2.93 vs 2.02 (Zen 4).

**How:** It makes two changes to SHAKE128. First, the permutation is Keccak-p[1600] reduced to 12 rounds (TurboSHAKE), roughly halving the per-block cost. Second, a Sakura-coded tree mode cuts the input into 8 KiB leaves whose chaining values feed a final node, and 'kangaroo hopping' merges the first chunk into that final node so inputs of 8 KiB or less pay no tree overhead. Independent leaves go through 2-, 4- or 8-way parallel Keccak-p code (SSSE3/AVX2/AVX-512, chosen at runtime by the x86-64 target), where AVX-512 rotate and ternary-logic instructions and its 32 registers cut the instruction count further.

**Use it when:**
- You want to stay in the Keccak/SHA-3 family (same permutation and cryptanalysis track record, 128-bit claim like SHAKE128) but SHAKE128 is too slow: even serially (8 KiB or less), KT128 is about 1.8x faster than SHAKE128 (paper Table 2; eBASH gives 2.77 vs 4.98 cycles/byte at 1536 B on Tiger Lake).
- Hashing large single buffers (tens of KiB and up) on x86-64 with AVX2 or AVX-512: the paper reports 1.22-1.44 cycles/byte on Skylake/Haswell and 0.55 on SkylakeX, against 4.28-7.09 for SHAKE128.
- ARMv8.4-A cores with SHA-3 instructions (Apple A14/M1): the Keccak team reports 0.75 cycles/byte for KT128, 1.7x hardware SHA-256 (a first-party figure).
- Protocols that want a standardized fast XOF with domain separation: KT128/KT256 are specified in RFC 9861.
- Projects that also need other Keccak-team constructions (SHA-3, SHAKE, cSHAKE/KMAC, TurboSHAKE, Xoodyak) from one mostly CC0 code base.

**Skip it when:**
- Short to medium messages on x86 CPUs with SHA-NI: in eBASH 2026 at about 16 KiB, K12 takes 2.47 cycles/byte on Tiger Lake and 2.93 on Zen 4, against 2.21/2.02 for SHA-256, so it is slower than hardware SHA-256 there.
- When FIPS 202 / FIPS 140 compliance is required: KT128 is not one of the six approved FIPS 202 instances, and its 12-round permutation has a smaller margin (the paper claims 7 of 12 rounds).
- Streaming input in small pieces: the SIMD multi-leaf path runs only when a single Update call still holds 16/32/64 KiB of full 8 KiB leaves (2/4/8-way); 4-16 KiB reads fall back to serial speed.
- When you need multi-core hashing out of the box: XKCP's K12 is single-threaded (SIMD only) and has no parallel API like BLAKE3's update_rayon.
- MSVC/Windows builds: the fast x86 assembly uses GCC syntax, so MSVC needs the *noAsm targets, and libXKCP.dll does not link yet.

**Vs siblings:** Pick K12 over BLAKE3 when you want to stay in the Keccak/SHA-3 family (RFC 9861, KT256 for 256-bit security) or target ARMv8.4-A SHA-3 hardware; pick BLAKE3 for peak speed at shorter lengths (1 KiB vs 8 KiB leaves), multithreading and a maintained Rust crate. Versus sha256-simd, ISA-L multi-buffer SHA, j-lanes and S-HASH, K12 fits when you can change the digest and hash single long messages, not many parallel SHA-256 streams.

**Gotchas:**
- Licensing is mixed: the AVX2/AVX-512 single-permutation Keccak-p assembly is CRYPTOGAMS (BSD-style or GPL), the ARMv8-A cores are Apache-2.0/ISC/MIT, and only the rest is CC0 (which gives no patent grant). Keep the LICENSE file when redistributing.
- Past memory-safety bug: CVE-2022-37454 (GHSA-6w4m-2xhg-2658, critical) was a buffer overflow in the sponge queue when a partial input reached 2^32-200 bytes or more, fixed in commit fdc6fef. Open issue #171 (Aug 2026) reports UBSan misaligned loads in the AVX2 times4 code.
- Makefile.build is XML that xsltproc expands into a makefile; there is no CMake or pkg-config support. Pick a SIMD-capable target (e.g. x86-64/libXKCP.a), because generic32/generic64 are plain C and will not reach the headline numbers.
- Headline numbers are single-core and need very long messages: parallelism starts only after the first 8 KiB, and 4-way needs 5 chunks (40 KiB) on the paper's Skylake plot. eBASH's 16 KiB 'long message' metric therefore shows K12 near its serial speed.

**Status:** Actively maintained by the Keccak team (commits through 2026-09-25, including recent alignment and aliasing fixes; 664 stars) and mostly CC0, but the fast x86 cores carry CRYPTOGAMS terms, so vendor it through the .pack targets or the trimmed XKCP/K12 repo and keep the LICENSE file.

[repo](https://github.com/XKCP/XKCP) · [benchmark](https://eprint.iacr.org/2016/770.pdf)

##### Simultaneous hashing of multiple messages / S-HASH (Gueron & Krasnov)  `any`  `no license`  `finished`  `Tier B`

Multi-buffer SHA-256 that hashes 4 independent messages per AVX register with standard digests; 3.42x OpenSSL 1.0.1 on 4KB messages.

**Beats:** OpenSSL SHA-256 (v1.0.1) — On a Core i5-2500 (Sandy Bridge, 3.3GHz; Turbo, HT and SpeedStep off; Fedora 16), 4-buffer AVX SHA-256 hashed 4KB chunks at 5.18-5.21 c/B from L1 through main memory. Serial OpenSSL 1.0.1 took 17.72-17.80 c/B (3.42x) and the authors' n-SMS took 11.68-11.81 c/B (2.25x). Hashing files from a two-SSD RAID0 at native clock gave 8.65 vs 19.55 c/B (2.26x) for eight equal 17.76MB files and 17.53 vs 30.32 c/B (1.73x) for 350 mixed-size files. No compiler or flags are stated.

**Known shortcoming:** 3.42x holds for cached data only; the '~3x from disk' figure was measured with the CPU at 1.6 GHz (native 2.26x / 1.73x). OpenSSL later shipped its own multi-buffer SHA-256 (sha256-mb), so the baseline is superseded. JIS 2012.

**Known shortcoming:** Paper has no code; shipping forms are ISA-L sha256_mb (submit/flush API), OpenSSL's internal sha256_multi_block (used only by TLS AES-CBC-HMAC multi-block) and minio's AVX-512 server. Needs a batch of independent messages: single-stream gains nothing and uneven sizes cut the gain to 1.73x. Linux dropped its AVX2 multibuffer SHA in 2018 (broken, real-world gains debated).

**How:** This is SIMD across messages ('multi-buffer', first tried by Aciicmez in 2004 on Pentium 4 SSE2 for a 1.71x gain). Each lane holds one message's state, so one S-UPDATE compresses four 64-byte blocks from four messages with the same instruction stream. The scheduler runs min(remaining length)/64 blocks at a time, then finalizes or refills the lanes that ran out, and finishes any leftover buffers serially. The paper gives two reasons it falls short of 4x on Sandy Bridge: the scalar ALU path is faster than the SIMD unit, and each SHA-256 rotate costs two SIMD shifts plus an xor instead of one ROR.

**Use it when:**
- Many independent messages are ready at once and each needs a standard SHA-256 digest: boot-time integrity checks of OS components, dedup chunk fingerprints, file-tree manifests, or TLS/HMAC servers that batch work across connections (the paper's own scenarios).
- Messages of similar length. Eight equal 17.76MB files reached 2.26x over OpenSSL from disk at native clock, against 1.73x for 350 mixed Windows driver files, because equal lanes finish together.
- Data already in cache or RAM. On 4KB chunks, speed was flat at 5.18-5.21 c/B whether the data sat in L1, L2, LLC or main memory.
- Wide-SIMD x86 without SHA extensions. AVX2 doubles the lane count to 8 and AVX-512 to 16. minio's README reports 3498 MB/s per core with 16-lane AVX-512 on a Xeon Platinum 8124M, 7.8x its AVX2 path.

**Skip it when:**
- One message at a time, or latency-bound single-stream hashing. Only one lane does useful work. For that, use a fast serial or SHA-extension SHA-256, or a tree mode such as j-lanes if you control the format.
- Very uneven message sizes. Lanes stall until they are refilled and stragglers finish serially, which is why the mixed-size directory got only 1.73x.
- Pipelines limited by I/O. At 3.3GHz, the 400MB/s SSD RAID0 equals about 7.15 c/B, so S-HASH reached 8.65 c/B from disk rather than 5.2. The abstract's '~6.73 c/B, almost 3x' needed the CPU down-clocked to 1.6GHz.
- Small messages or thin batches. OpenSSL's multi-buffer notes say real-world gains on 2KB fragments are 75-130% on Haswell, against a 170% asymptotic figure. minio's README advises plain SHA-256 below about 1MB for its channel-scheduled server.
- Code you would have to maintain yourself. Linux added AVX2 multibuffer SHA-256/512 in 4.8 (2016), then removed it in August 2018 because it was broken, too complex to maintain, and its 'performance benefits for real-world use cases are debatable'.

**Vs siblings:** Choose S-HASH (in practice ISA-L's sha256_mb) over j-lanes when you have many independent messages and need interoperable standard SHA-256 digests. j-lanes speeds up a single message but changes the digest. In Go, minio/sha256-simd already ships the same multi-buffer idea as its AVX-512 server alongside a drop-in crypto/sha256 replacement, so use it rather than porting the paper.

**Gotchas:**
- Completion is decoupled from submission. ISA-L processes jobs out of order and returns a context only when its lane finishes, so callers must keep submitting or call flush to drain. The paper itself says the software needs restructuring to benefit.
- The 2.25x figure is against the authors' own n-SMS serial code, which is also their OpenSSL RT #2784 patch, not against a third-party implementation. The 3.42x figure is against stock OpenSSL 1.0.1.
- The disk results are in cycles/byte, so down-clocking flatters them. At 1.6GHz, S-HASH on the UNIFORM files is 6.73 c/B but only 226.73 MB/s, against 363.83 MB/s at 3.3GHz.
- OpenSSL's sha256_multi_block is internal. It is used only by the AES-CBC-HMAC-SHA256 multi-block TLS cipher code and cannot be reached as a general multi-message digest API.

**Status:** This is finished 2012 research (ePrint 2012/371, republished in Journal of Information Security 3(4):319-325, a SCIRP journal, 9 Crossref citations) with no code of its own. The technique is maintained in Intel ISA-L crypto (last push 2026-07) and survives inside OpenSSL's TLS multi-block path, while Linux dropped its copy in 2018.

[benchmark](https://eprint.iacr.org/2012/371.pdf)

#### encoding

##### fastbase64 (lemire)  `C`  `no license`  `abandoned`  `Tier A`

Archived research AVX2 base64 codec from the Muła–Lemire paper; roughly 7-11x faster than Chrome's scalar codec on Skylake.

**Beats:** base64 (glibc/Linux base64 utility and Google Chrome's base64 implementation) — The paper measured on an i7-6700 Skylake at 3.4 GHz with Turbo off, GCC 5.3 -O3 -march=native, taking the minimum rdtsc count over 500 runs. There the AVX2 codec needs about 0.25 cycles/byte on large random inputs, against 2.7 (encode) and 1.8 (decode) for Chrome 56's modp_b64, and it decodes six real files at 0.21-0.27 cycles/byte against Chrome's 1.8-2.1 and Klomp AVX2's 0.43-0.53. In Turbo-Base64's independent 1 MB table (i7-9700K, gcc 11.2) fb64avx2 reaches 23,686/21,231 MB/s encode/decode against Chrome's 2,541/4,289, but by then it trails aklomp's b64avx2 (26,153/22,515).

**Known shortcoming:** Research artifact of the Muła & Lemire paper (arXiv 1704.00605): numbers are from GCC 5.3 -O3 -march=native on an i7-6700 (Skylake, 2017). The Turbo-Base64 comparison figures come from a closed third-party harness (C-level on their own).

**Known shortcoming:** Archived; README says research-only and points to simdutf. Strict input only (no whitespace, no URL-safe, length must be a multiple of 4); no runtime dispatch (SIGILL without AVX2); no gain under ~100 bytes. AVX-512BW encoder emits garbage on 64-byte input (#17, closed unfixed); NEON is decode-only and not built. In the independent Turbo-Base64 1 MB table it trails aklomp/base64 and Turbo-Base64 (23.7/21.2 vs 26.2/22.5 and 29.1/29.7 GB/s).

**Independent measurement:** Turbo-Base64 1 MB table: fastbase64 23.7/21.2 GB/s enc/dec vs aklomp 26.2/22.5, TB64 29.1/29.7.

**How:** Encoding: a vpshufb puts each 3-byte group into a 32-bit lane. A vpmulhuw/vpmullw multiply-shift then extracts all four 6-bit fields at once, and ASCII translation uses a saturating-subtract/compare range index into a 16-entry vpshufb offset table instead of a 64-byte lookup table. Decoding uses aqrit's nibble-LUT scheme: two vpshufb lookups on the high and low nibbles produce bitmasks whose vptest catches any invalid byte, and a third vpshufb supplies the per-range offset. Then vpmaddubsw + vpmaddwd pack four 6-bit values into 24 bits, and vpshufb + vpermd compact 32 characters into 24 bytes. The paper counts about 11 vector instructions per 24 input bytes for encoding and 14 per 32 for decoding, which is about 0.25 cycles/byte on Skylake. Tails shorter than 28 bytes (encode) or 45 characters (decode) go to the Chromium scalar code.

**Use it when:**
- Reproducing or extending Muła & Lemire (ACM TWEB 2018): this repo is the paper's artifact, with basic_benchmark.c, the test images and the rival codecs in one harness.
- Reading a minimal reference of the AVX2 base64 kernels (about 200 lines in src/fastavxbase64.c) before porting the technique into your own code.
- Only if you must vendor a tiny C kernel and cannot take simdutf: strict, padded, whitespace-free standard-alphabet data of about 200 bytes or more (data URIs, embedded images) on AVX2 x86-64 that you build for yourself.

**Skip it when:**
- Anything in production: the README says it is unmaintained research code and not for production, the repo is archived, and the author sends users to simdutf.
- MIME/PEM or other input with line breaks or spaces, URL-safe alphabet, or missing padding: the Chromium fallback returns MODP_B64_ERROR and there are no options.
- Short strings: the paper says that under about 100 bytes the AVX2 codec is no faster than scalar code.
- The AVX-512BW encoder: issue #17 (2024) reports garbage output for a 64-byte input on Sapphire Rapids while still returning the expected length. It was closed without a fix.
- Non-x86 targets: the POWER9 AltiVec port is only about 2-2.4x Chrome at 2 KB (decode 0.32 vs 0.65 ns/byte, encode 0.27 vs 0.66), the NEON file is decode-only and not built by the Makefile, and there is no aarch64 encoder.

**Vs siblings:** For real use, pick simdutf (maintained descendant of this algorithm, runtime dispatch, whitespace and URL-safe support), aklomp/base64 (maintained C99 library that adopted these kernels) or Turbo-Base64 (29,086/29,748 MB/s vs fastbase64's 23,686/21,231 MB/s encode/decode in the same i7-9700K table). Pick fastbase64 only to reproduce the paper or to read the smallest reference version of the AVX2 kernels.

**Gotchas:**
- No CPU detection: fast_avx2_* crashes with SIGILL on CPUs without AVX2, and the Makefile builds everything with -march=native, so the binaries are not portable.
- Each decode step stores 32 bytes but advances only 24, so the region past the current output position gets scratch bytes. By our reading this stays inside a buffer sized for the decoded output. On invalid input the function returns MODP_B64_ERROR after writing partial output.
- The encoder's first load is a masked vpmaskmovd from str-4 (that lane is masked, so no fault per Intel docs). Turbo-Base64's source calls fastbase64 'unsafe, can reads/writes beyound i/o buffers'; we did not confirm that for the AVX2 path, and the unit tests cover only three fixed strings plus an invalid-character sweep.
- Decoding requires a length that is a multiple of 4. The header says encode returns strlen+1, but the code returns strlen and writes a NUL terminator.

**Status:** Archived, with the last commit on 2024-04-04; the README and issue #17 call it obsolete and point to simdutf. The LICENSE file is standard BSD-2-Clause text (GitHub shows NOASSERTION), so vendoring is allowed, but every fix is yours.

[repo](https://github.com/lemire/fastbase64) · [benchmark](https://arxiv.org/abs/1704.00605)

#### signatures-kem

##### fasthqc/hqc (vectorized sparse-dense multiplication + syndrome generation)  `C`  `no license`  `abandoned`  `Tier A`

AVX2 patch to the HQC Round-2 KEM's sparse-dense multiply and BCH syndrome step; 34-46% fewer cycles than the optimized reference.

**Beats:** HQC NIST Round 2 optimized reference implementation (Aguilar-Melchior et al.); HQC is a KEM historically supported by liboqs — Against the HQC Round-2 optimized implementation on a 4th-gen Core i5-4690S (Turbo off, compiler not stated), both patches together cut keygen cycles 34.9-42.8%, encapsulation 33.7-45.2% and decapsulation 45.0-46.3% across all six parameter sets. On an i5-8400H with gcc 7.4.0 (-O3 -mavx2) the reductions were 30.9-43.2%, about 1.45-1.86x in speed. Each figure is the mean of per-dataset minimum cycle counts over 1,000 runs for 50 random data sets.

**Known shortcoming:** Gain is 33.7-46.3% on i5-4690S and 30.9-43.2% on i5-8400H (not the claimed 35.1-46.3%); GCC 7.4.0 is stated only for the 8400H run. liboqs re-enabled HQC in 0.16.0, so the baseline has moved.

**Known shortcoming:** Not constant-time: fastConvolutionMult indexes memory by secret positions and syndrome_gen2 branches on decoded bits (timing side channels); the Rand_FC variant shuffles with libc rand(). Not thread-safe (global scratch buffers); ~200 KB table never freed. No license, abandoned 2020, Round-2 HQC only (hqc-256-3); liboqs now ships the 2025-08-22 spec. Constant-time follow-up: Robert & Véron, JCE 2022.

**How:** The 'fast convolution' keeps the sparse operand as a list of its w nonzero positions (67-153), so the product is the XOR of w copies of the dense polynomial, each shifted by one of those positions. Each shift is done with AVX2 256-bit shifts (_mm256_slli/srli_epi64 plus a carry from the neighboring word) and XORed into a double-length accumulator, followed by one vectorized reduction mod X^N-1; the baseline instead used an NTL-inspired vectorized multiply. syndrome_gen2 spreads the received BCH codeword bits into bytes with a shuffle and mask, then XOR-accumulates rows of a precomputed alpha^(ij) table, 16 syndromes per ymm register, instead of evaluating each syndrome separately in GF(2^10).

**Use it when:**
- Studying or reproducing HQC Round-2 performance on x86-64 with AVX2 (Haswell and later): keygen, encapsulation and decapsulation for N = 24,677-70,853.
- As a reference technique for multiplying a sparse position list by a dense polynomial in F2[X]/(X^N-1), in quasi-cyclic code-based schemes where the sparse operand has weight around 100 and N is tens of thousands of bits. The report puts the multiplication alone at about 64-75% faster.
- As a template for vectorized BCH syndrome computation with a precomputed power table (400,209 to 18,101 cycles, about 22x, for n1 = 766 in the report).

**Skip it when:**
- Anything deployed. The code is not constant-time: fastConvolutionMult indexes memory by the secret sparse positions (C256[vbi], tab[i64]), and syndrome_gen2 branches on bits of the decoded word.
- Current HQC. This targets the Round-2 code base and its six parameter sets (hqc-128-1 ... hqc-256-3). liboqs now ships HQC-1/3/5 from the official 20250822-spec implementation (re-enabled by default in 0.16.0, July 2026), so the percentages and code will not carry over as-is.
- Multi-threaded use. Scratch buffers (C2, TT, tmp8), syndrome_gen2's static tmp_array and the precomputed tables are process-global mutable state.
- Any use that needs a license. The repo has no LICENSE file and has been abandoned since April 2020 (6 stars, no issues, no releases).
- Non-x86 or pre-AVX2 CPUs; the Arith2020 experiments additionally need PCLMUL and, for several tables, the gf2x 1.2 library.

**Vs siblings:** It is the only key-encapsulation and code-based post-quantum entry in this category. ENG25519 and UltrafastSecp256k1 are classical elliptic-curve code and VecFalcon is a post-quantum signature. Pick it only to study HQC or quasi-cyclic binary-polynomial arithmetic on AVX2; it is not a deployable alternative to any of them.

**Gotchas:**
- The PATCH2 syndrome path reads global tables that syndrome_gen_init() must fill first. Forgetting that call leaves them NULL. The init also prints to stdout and never frees its roughly 200 KB alpha^(ij) table (796 x 128 int16 for hqc-256-3).
- Patches are switched on by rewriting src/patch.h, which script.sh overwrites with '#define PATCH' between builds. Building by hand gives whatever the header currently says.
- The randomized FastConvolution variant (Arith2020 Rand_FC) shuffles the order of the sparse positions using libc rand(), which is not a cryptographic RNG, and it keeps the same position-indexed accumulator writes (C256[vbi]).
- The report's 'speed-up %' is a reduction in cycles. 34-46% fewer cycles is about 1.45-1.86x in speed ratio, and the 70-75% figure applies to the multiplication kernel only, not the whole KEM.

**Status:** Abandoned since April 2020 and unlicensed, and it patches a superseded Round-2 HQC code base with non-constant-time kernels. Read it for the technique; do not vendor it. The authors' later constant-time Karatsuba/Toom-Cook multiplication work (Robert & Véron, J. Cryptographic Engineering 2022) is the more relevant follow-up.

[repo](https://github.com/fasthqc/hqc) · [benchmark](https://github.com/fasthqc/hqc/blob/master/report-23072019.pdf)

##### ML-KEM AVX-512 optimization for TLS 1.3 (Zheng et al., Fudan University)  `C`  `no license`  `unknown`  `Tier B`

Unreleased AVX-512 ML-KEM (ESORICS 2024) reporting 1.30-1.64x fewer cycles than pq-crystals AVX2 Kyber, but only 0.4-5.6% more TLS handshakes.

**Beats:** pq-crystals Kyber 'standard' branch AVX2 implementation (FIPS 203 draft code, the paper's ref [5]) for ML-KEM cycle counts; liboqs 0.10.1 ML-KEM AVX2 via OQS-provider on OpenSSL 3.3.0-dev for TLS 1.3 handshakes/sec — On a 4-vCPU Alibaba c8i VM (Xeon Platinum 8475B, GCC 9.4.0, flags unstated, Turbo and HT on), the median over 100,000 runs shows the AVX-512 code using 1.30-1.64x fewer cycles than the pq-crystals 'standard'-branch AVX2 Kyber built with AVX-512 disabled (for example, ML-KEM-1024 encaps at 25,062 vs 41,162 cycles). Through liboqs 0.10.1, the OQS provider and OpenSSL 3.3.0-dev, openssl s_time handshakes/sec rose only about 0.4-5.6% in PQ-only and hybrid modes.

**Known shortcoming:** No public code. Real baseline is the pq-crystals Kyber AVX2 implementation (liboqs is used only for the TLS integration); gain 1.30-1.64x on the KEM, but only ~0.4-5.6% end-to-end in TLS 1.3 (derived), and one Table 3 cell is slower. Needs AVX-512.

**Known shortcoming:** Code still unreleased (cccccosine/Kyber_AVX512_32w is a different paper). Table 3's ML-KEM-1024/Dilithium5 cell looks like a copy error; the 3.5-4.9x batch keygen is not explained by Algorithm 4 as printed (it batches only SHA3-256(ek)). Measured on a 4-vCPU VM with Turbo and HT on, flags unstated, against FIPS 203 draft code. liboqs has no AVX-512 ML-KEM (it now uses mlkem-native).

**Independent measurement:** ESORICS 2024: ML-KEM AVX-512 1.30-1.64x vs pq-crystals AVX2; TLS 1.3 handshake gain ~0.4-5.6%.

**How:** Each 512-bit zmm register holds 32 signed 16-bit coefficients, so one polynomial fits in 8 registers. All 7 NTT layers are merged: coefficients load once, and shuffle16/8/4/2/1 permutes pair them up at each butterfly distance. The butterflies use signed Montgomery reduction (vpmullw/vpmulhw with twiddles premultiplied by q^-1), Barrett reduction (vpmulhw plus a shift), and lazy reduction in the inverse NTT. Keccak-p[1600] runs 8 states in parallel instead of AVX2's 4. Rejection sampling and CBD sampling use AVX-512 mask registers and compress-store, and pk/sk decode and decompress use the byte permute vpermb.

**Use it when:**
- As a design blueprint if you maintain an ML-KEM backend for AVX-512 x86 servers such as Sapphire Rapids and want roughly 1.3-1.6x over the pq-crystals AVX2 kernels.
- TLS terminators or KEM key pools that can pre-generate ephemeral keys 8 at a time: batched keygen is reported at 2,804 / 4,866 / 7,394 cycles per key for ML-KEM-512/768/1024.
- Capacity planning: the paper's handshake data shows faster KEM code barely moves openssl s_time throughput, which is useful evidence before spending effort on KEM kernels.
- Research on IND-1-CCA KEMs for ephemeral TLS key exchange: TRH decaps is 5,666 vs 19,838 cycles for ML-KEM-512 (measured on the AVX2 code), with the same ciphertext size.

**Skip it when:**
- When you need something you can build or audit: the paper says 'we will later open source our code', and no repository was found as of 2026-09. The only public AVX-512 Kyber repo found (cccccosine/Kyber_AVX512_32w) is a different ISC 2024 multi-way paper.
- CPUs without AVX-512: the design depends on 32 zmm registers, mask registers, compress-store and vpermb, and has no fallback path.
- Hybrid-mode TLS (X25519/P-256 + ML-KEM) where you expect big handshake gains: Table 4 shows about 0.4-5.6% more connections/sec, because ECDH and signatures dominate.
- Deployments that need final-FIPS 203 or CMVP conformance: the code was built on FIPS 203 draft base code, final-standard conformance is not documented, and the faster TRH/TCH variants are not ML-KEM at all.
- One-off keygen latency: batching only pays off when the caller consumes 8 key pairs at once, which needs application or protocol changes.

**Vs siblings:** It is the only catalogued AVX-512 ML-KEM result, so use it as a reference design; for runnable ML-KEM code, moduletto (NEON ML-KEM-512 on aarch64, benchmarked against liboqs 0.16.0) actually ships. The same group's Dilithium-AVX512 (the paper's ref [56]) has public code for the signature side, and ENG25519 (ref [55]) speeds up the X25519 half that this paper's own data shows dominates hybrid handshakes.

**Gotchas:**
- Table 3 anomaly: the AVX2 ML-KEM-1024/Dilithium5 cell (3191.46 conn/s) duplicates the Falcon512 cell, so AVX-512 appears slower there (2451.08). It also contradicts the paper's own statement that handshakes/sec drop as the security level rises, so it is likely a copy error and that column is unreliable.
- The batch-keygen ratios printed in Table 2 (4.9x/4.2x/3.5x) are a bit higher than the same table's non-batched AVX-512 keygen implies (about 4.7x/4.0x/3.4x). Also, Algorithm 4 as printed batches only the final SHA3-256 over the 8 encapsulation keys while K-PKE.KeyGen runs in a loop, so the paper does not explain how per-key cost falls to 2,804 cycles.
- The printed assembly has errors: Algorithm 2 (Gentleman-Sande butterfly) repeats 'vpmulhw %zmm\zh' on two lines where a low-half product with the zeta*q^-1 constant is needed, so do not transcribe the listings verbatim.
- Noisy measurement setup: Turbo Boost and hyper-threading were left on, the host was a 4-vCPU cloud VM, and TLS client and server ran on the same machine. Handshake deltas of about 1-5% are within what such setups can drift.

**Status:** Peer-reviewed (ESORICS 2024, LNCS pp. 123-143), but the promised code never appeared, liboqs has no AVX-512 ML-KEM from this work (it switched to mlkem-native in 2025), and there is no license or maintenance, so treat it as a paper-only reference design.

[benchmark](https://arxiv.org/abs/2404.13544)

##### Optimizing Dilithium Implementation with AVX2/AVX-512 (PSPM)  `C`  `no license`  `stale`  `Tier B`

Research AVX2/AVX-512 Round 3 Dilithium code using PSPM-TEE sparse c·s multiplication; paper reports 1.6-2.9x fewer cycles than pq-crystals AVX2.

**Beats:** pq-crystals/dilithium AVX2 implementation: the 'standard' branch (FIPS 204 ML-DSA) AVX2 code for the headline Table XI numbers, and the NIST Round 3 submission AVX2 code for Table IX. This is the upstream code that liboqs/PQClean also derive from; liboqs and PQClean were not benchmarked directly. — On one core of an Intel i7-11700F at 2.5 GHz (Turbo and HT off, Ubuntu 20.04, gcc 9.4.0 -O3 -march=native plus AVX-512 flags, median of 100000 runs), the paper's AVX-512 code needs 36.6-47.4% fewer cycles than the pq-crystals FIPS 204 AVX2 code (e.g. ML-DSA-44 KeyGen 47760 vs 84270 cycles, about 1.6-1.9x). It needs 50.0-65.1% fewer cycles than the Round 3 AVX2 code (about 2.0-2.9x). PSPM alone cuts the Dilithium3 c·s / c·e product by 47-66% versus NTT but only speeds up whole AVX2 signing by about 3-8%. The repo cannot reproduce the ML-DSA table or either full-scheme baseline.

**Known shortcoming:** Repo holds Round 3 Dilithium only: no ML-DSA code behind the headline numbers and no pq-crystals baseline in the repo (retiered A to B on the peer-reviewed TDSC 2025 paper). Percentages are cycle-count reductions (~1.58-1.90x). No license: reference use only.

**Known shortcoming:** PSPM is only called in dilithium5 AVX-512 signing (dilithium2 AVX-512 compiles it but never calls it; dilithium3 AVX-512 and all AVX2 trees lack it); PSPM-TEE alone gives only 3-8% AVX2 signing gain. By code reading, pspm_tee_z/r0 store abs() values into z/r0 that are then packed into the signature, so signatures may be wrong; speed tests never check the verify result and run 10,000 iterations vs the paper's 100,000. Object files and a ~20 MB binary are committed. A second anonymous repo (Dilithium-AVX512/Dilithium-AVX512) for the same paper is a plain AVX-512 port without these techniques and exports pq-crystals symbol names.

**How:** PSPM (parallel small polynomial multiplication, from Zheng et al., ACSAC 2022) exploits the fact that the challenge c has only tau coefficients equal to ±1. It packs the small secret polynomials into a precomputed table, so c·s1 and c·s2 become tau shifted adds or subtracts instead of an NTT. PSPM-TEE adds 'tailored early evaluation': it checks the r0 norm before the z norm (r0 rejects more often) one polynomial at a time and aborts at the first failure. The paper credits most of the AVX-512 gain to other work: a 16-way AVX-512 NTT/NTT^-1 with merged layers, 8-way AVX-512 Keccak for matrix and vector sampling, vectorized rejection sampling and packing, and a 'tailored reduction' for q = 2^23 - 2^13 + 1 using AVX-512IFMA.

**Use it when:**
- Studying or porting PSPM-TEE: the repo's PSPMTEE.c shows a 64-coefficient-per-zmm int8-table version of the sparse c·s product with early norm checks
- Reading reference AVX-512 kernels for Dilithium (16-way NTT in ntt512.c/inv_ntt512.c, 8-way SHAKE sampling in fips202x8.c and keccak8x.c) when writing your own ML-DSA backend
- Checking the paper's component benchmarks: dilithium2_avx512/test/test_speed.c times PQClean ('clean') against the authors' ('xurq') Keccak permutation, matrix expansion, uniform_eta and uniform_gamma1 side by side
- Research on Rocket Lake / Ice Lake-class CPUs with full AVX-512 (F/VL/CD/BW/DQ/VBMI/VBMI2), where the paper's i7-11700F numbers apply

**Skip it when:**
- Any production or FIPS 204 use: the repo is Round 3 Dilithium only (Dilithium2 sk = 2528 bytes) and does not include the ML-DSA code behind the headline Table XI numbers
- Anywhere you need a license: there is no LICENSE file, so legally the code is reference-only even though parts derive from permissively licensed PQClean/NIST code
- Code you would trust without re-testing. By reading (not running) it: only dilithium5_avx512 signing actually calls pspm_tee_r0/pspm_tee_z, and those functions store |value| (after _mm512_abs_epi32) into z and r0 before z is packed into the signature. The last 64-coefficient block is also loaded at offset N+182-j, versus 192 in pspm()
- CPUs without AVX-512 (many client Intel parts, older AMD): the _avx512 trees are compiled with -mavx512f/vl/cd/bw/dq/vbmi/vbmi2, and the AVX2 trees gain only about 3-8% in signing from PSPM-TEE (paper Tables VII/X)
- Side-channel-sensitive deployments: the paper says constant-time was 'not the focus', and PSPM-TEE branches on challenge coefficients and returns early from rejection checks

**Vs siblings:** Dilithium-AVX512 (github.com/Dilithium-AVX512/Dilithium-AVX512) is catalogued from the same paper with the same numbers. It is a single pq-crystals-style tree with KAT files and a DILITHIUM_MODE switch, but it has no PSPM code. Pick this repo only when you want the PSPM-TEE source and the AVX2 variants; for a usable ML-DSA, neither sibling qualifies, and the Plantard-NTT codegen entry is the more rigorous (formally verified) option if you need portable speedups.

**Gotchas:**
- PSPM is not used in most trees: dilithium2_avx512 compiles PSPMTEE.c but signs with NTT, and dilithium3_avx512 plus all three _avx2 trees contain no PSPM code, although the paper describes PSPM-TEE for AVX2 and AVX-512
- The test_speed harnesses never check verify's return value (the D5 AVX-512 harness even signs in place over its message buffer). They run NTESTS = 10000, not the paper's 100000 repetitions, so a passing speed run proves nothing about correctness
- Build artifacts are committed (common/keccak/*.o and a roughly 20 MB 'our_3_avx512_test_speed' binary in dilithium3_avx512); rebuild from source rather than trusting them
- The paper's text and tables disagree on where PSPM-TEE helps most: the text says 7.7% for Dilithium3, while Table VII shows 7.7% for Dilithium2 and 3.1% for Dilithium3

**Status:** Stale research dump (10 commits, last 2025-07-16, 3 stars, no issues) with no license, so it is reference-only; treat it as a companion to the TDSC paper, not a library.

[repo](https://github.com/xurq5953/Optimizing-Dilithium-Implementation-with-AVX2-512) · [benchmark](https://arxiv.org/abs/2306.01989)

### networking-and-servers

#### dns-quic-http3

##### quiche-DPDK (tumi8 kernel-bypass fork)  `C (DPDK kernel-bypass I/O layer added on top of upstream Rust quiche core)`  `no license`  `active`  `Tier B`

DPDK kernel-bypass client/server built on unmodified quiche; 1.83x the single-connection goodput of kernel-socket quiche on 100G NICs.

**Beats:** quiche — The test was a single-connection download of an 8 GiB file, 50 repetitions, between two Xeon Gold 6421N hosts with 100G Intel E810 NICs (Debian 12, Linux 6.1, DPDK 24.11). The quiche-DPDK client+server pair averaged 5937 Mbit/s (range 5826-6018). The kernel-socket quiche pair averaged 3241 Mbit/s (range 2554-3605) with GSO on and 32x socket buffers, for 1.83x; on an SR-IOV VF quiche-DPDK reached 6168 Mbit/s. The DPDK side builds quiche 0.23.2 on unpinned Rust stable and C at RelWithDebInfo. The kernel quiche binary comes from a private CI branch ('25.02') whose version and flags are unpublished.

**Known shortcoming:** Research kernel-bypass client/server around an unmodified quiche; no licence (reference only). Needs DPDK and dedicated NICs; baseline builds are private and compiler versions not pinned.

**Known shortcoming:** Not HTTP/3: it negotiates only hq-interop/http/0.9 and sends a bare GET. Frozen paper artifact (3 commits, no LICENSE file). Source defects: path traversal in the server (admitted in a comment), whole file loaded into one malloc, client disables certificate verification, TX mbuf allocations not NULL-checked, ARP frames for other IPs freed twice; IPv4 only, one port/queue/lcore. With a quiche-DPDK server, 13 of 100 picoquic(-DPDK) client runs produced no goodput. An unpublished XDP variant averaged 3168 Mbit/s, no gain over kernel quiche. Slowest of the four DPDK stacks; kernel MsQuic with GSO/GRO (8250 Mbit/s) beats it without bypass.

**How:** It uses a run-to-completion busy-poll loop on one NUMA-local lcore. The loop pulls up to 32 packets with rte_eth_rx_burst, hands each to quiche_conn_recv straight from the mbuf, then drains quiche_conn_send into freshly allocated mbufs and sends them in 32-packet rte_eth_tx_burst batches. This removes the syscalls and kernel/user context switches that the paper identifies as quiche's bottleneck; kernel quiche supports only GSO, which barely helps it (3055 -> 3197 Mbit/s in the paper's data). Other throughput settings are 4096 RX/TX descriptors, hardware IPv4 checksum offload with the UDP checksum zeroed, MBUF_FAST_FREE, CUBIC, and quiche pacing turned off on the server.

**Use it when:**
- Bulk single-connection transfers between dedicated bare-metal hosts on 25-100G links, when a quiche-based app is limited by packet I/O and not by crypto (measured: 3.2 -> 5.9 Gbit/s per connection).
- Controlled environments (datacenter point-to-point links, CDN-internal transfers, testbeds) where you can give DPDK a NIC port or an SR-IOV VF plus hugepages and root. The SR-IOV VF run was slightly faster (6168 Mbit/s) and lets the kernel keep the physical port.
- When the downloading side is the bottleneck: a DPDK client against a kernel quiche server alone gave 5464 Mbit/s (1.69x), while a DPDK server with a kernel client gave only 4036 Mbit/s (1.25x).
- As a template for adding DPDK to your own quiche application without patching quiche. The whole integration is about 1,600 lines of C (headers included) around the public quiche C API.
- To reproduce or extend the NOMS 2026 kernel-bypass measurements (configs, CSVs and Zenodo raw data are public).

**Skip it when:**
- Anything production-facing. It is a single-purpose hq-interop file-transfer demo: no HTTP/3, the client skips certificate verification, the server has a path-traversal hole its own source comment admits, and there is no LICENSE file.
- When you want the most goodput. It is the slowest of the four DPDK stacks in the paper: LSQUIC-DPDK reaches 10756 Mbit/s, picoquic-DPDK 8347 and MsQuic-DPDK 7983, and kernel-socket MsQuic with GSO+GRO reaches 8250 with no bypass at all.
- Shared or general-purpose hosts. One core busy-polls at 100% even when idle, and the programs need hugepages, elevated privileges and a DPDK-bound port or VF. They support IPv4 only, use port 0 with a single RX/TX queue, and do not route: the peer must be ARP-reachable on the same L2 segment.
- Many concurrent connections or multi-core scaling. All work runs on one lcore with one queue and no RSS, and only single-connection transfers were measured.
- Multi-hop or WAN paths. The server disables quiche pacing and sends 32-packet back-to-back bursts; the paper's Appendix D shows DPDK quiche traffic is burstier than kernel quiche.

**Vs siblings:** Pick it over LSQUIC-DPDK or picoquic-DPDK only when your stack already uses quiche's API and you want kernel bypass without forking the protocol library. Those siblings patch their libraries and reach about 1.8x and 1.4x higher goodput in the same paper. If you can't dedicate a NIC, a kernel-socket sibling such as ngtcp2 beats quiche without any bypass.

**Gotchas:**
- The protocol is hq-interop/HTTP/0.9, not HTTP/3: ALPN is `hq-interop`/`http/0.9` and the request is a bare `GET /path\r\n`. The server reads the whole requested file into one malloc'd buffer before sending, so an 8 GiB file costs 8 GiB of RAM.
- Possible memory bugs from reading the code: TX-path rte_pktmbuf_alloc results are never NULL-checked. An ARP frame for another IP, or a malformed one, is freed in handle_arp_request and then again by rte_pktmbuf_free_bulk, which is a double free. This is harmless on the paper's point-to-point fiber but risky on a shared L2 or SR-IOV segment that carries broadcast ARP.
- Interop is flaky in the published data. With the quiche-DPDK server, 7 of 50 runs against the picoquic client and 6 of 50 against the picoquic-DPDK client recorded no goodput (implementation-matrix processed.csv).
- The AF_XDP-style 'quiche-dpdkxdp' variant in the SR-IOV dataset averaged only 3168 Mbit/s and was bimodal (median 1596). That is no better than kernel quiche. Its xdp branch is not on GitHub; only main and an instrumented perf branch are.

**Status:** A frozen research artifact: 3 commits, last push 2026-02-12 to accompany the NOMS 2026 paper, 0 stars, no issues. There is no LICENSE file (upstream quiche is BSD-2-Clause), so read it as a reference design and don't vendor it.

[repo](https://github.com/tumi8/quiche-dpdk) · [benchmark](https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf)

#### event-loops-io

##### IX (protected dataplane OS)  `C`  `MIT`  `abandoned`  `Tier B`

Protected dataplane OS that runs TCP/IP and one app on dedicated polling cores; 2.8-3.6x memcached throughput over Linux+epoll.

**Beats:** Linux 3.16.1 kernel TCP stack via libevent + epoll: stock memcached-1.4.18 on tuned Linux (pinned threads, IRQ affinity, tuned interrupt moderation); mTCP is a second baseline in the microbenchmarks — OSDI'14 paper: memcached-1.4.18 ported to libix on 6 cores vs. stock memcached (libevent+epoll) on 8 pinned, interrupt-tuned cores of Linux 3.16.1, on a Xeon E5-2665 @ 2.4 GHz server with Intel x520 (82599) 10GbE and 23 Linux mutilate clients over 1,476 connections. Max RPS within a 500us p99 SLA rose from 550K to 1,550K (ETC, 2.8x) and from 500K to 1,800K (USR, 3.6x), and unloaded p99 latency fell from 94 to 45us and from 85 to 32us; no compiler or version is given (the 2016 release builds the dataplane with gcc -O3).

**Known shortcoming:** Research dataplane OS: needs Dune/VT-x, GPL kernel modules and dedicated NICs; not a library. Code was released in 2016, two years after the OSDI '14 paper, and is abandoned since 2017-11. libdune has no licence file. No compiler versions stated.

**Known shortcoming:** No receive flow control: one connection holding 128 unread segments makes the server exit (#12). The released benchmark differs from the paper (2,720 vs 1,476 connections; memcached maintenance threads disabled as a hack). DPDK pinned at 16.04, Python 2 scripts, Dune unlikely to build on recent kernels; IPv4 only, one instance per host, i40e transmit broken (#31).

**How:** Each elastic thread runs to completion: it polls its own NIC RX ring, pushes a bounded batch (default 64 packets) through an lwIP-derived TCP/IP stack, switches to the application to consume events, then executes the application's batched system calls, TCP timers and TX in the same loop, with no interrupts and no intermediate socket buffers. Batching is adaptive, so batches only grow under congestion and light load keeps latency low. RSS flow-consistent hashing gives each hyperthread its own RX/TX queue pair, flows and memory pools, so the common path takes no locks and causes no cache-coherence traffic. The dataplane also uses only 2MB pages, a hierarchical timing wheel, and refills RX descriptors 32 at a time to cut PCIe writes.

**Use it when:**
- Reproducing or extending the OSDI'14/SoCC'15 results: ix-project/ix-bench holds the memcached, ping-pong, short-message and connection-scaling scripts, and the ported memcached (ix branch of ix-project/memcached) and the mutilate load generator are public under ix-project.
- Small-message TCP request/response servers (e.g. key-value GETs with <20B keys and 2B values) where p99 latency under a few hundred microseconds sets capacity, on a dedicated server with Intel 82599/X520/X540 10GbE.
- High connection churn or many connections: the paper reports 3.8M TCP connections/s on 4x10GbE and runs up to 250K concurrent connections (at 250K, throughput falls to 47% of IX's peak from L3 cache misses).
- Research on kernel-bypass designs that keep the network stack isolated from application code (VT-x ring separation) while Linux remains the control plane.

**Skip it when:**
- Anything production or long-lived: no commits since 2017-11-06, DPDK pinned at 16.04, and the maintainer said in 2021 (issue #36) that Dune has not been updated and likely does not support recent kernels.
- Hardware or network setups outside its narrow support: non-Intel NICs (mlx4 was requested, never added, issue #24), machines without VT-x, non-x86, IPv6, SR-IOV, or more than one IX instance per host (issue #2).
- Untrusted or bursty peers: libix has no receive flow control, and one flooding connection can terminate the server process (issue #12).
- Applications that block in handlers or depend on POSIX sockets, TLS libraries or other socket-based code: every network path must be rewritten to ixev callbacks or the batched API.
- Lock-heavy or CPU-bound servers: IX only removes kernel network overhead; memcached gained less on ETC (2.8x) and stopped scaling past 6 cores on IX because of its own lock contention.

**Vs siblings:** Pick IX over mTCP or F-Stack only when you need the TCP stack protected from application code (separate rings under VT-x) or are reproducing the OSDI'14 comparison, where IX delivered 1.9x mTCP's short-message rate and lower 64B latency. Arrakis is the closer research analogue and adds IOMMU/SR-IOV support that IX lacks; for anything you must run today, F-Stack or Seastar are the maintained DPDK stacks.

**Gotchas:**
- No receive flow control: if one connection holds 128 unconsumed receive segments (IXEV_RECV_DEPTH), ixev prints 'ixev: ran out of receive memory' and calls exit(-1); a single `nc < /dev/zero` flood took down the echoserver (issue #12). A full syscall batch array likewise exits with 'ran out of command space'.
- Zero-copy rules: received buffers are read-only and should be released quickly; send buffers must stay unmodified until the peer ACKs, or the wire payload is silently wrong. sendv returns bytes accepted by the TCP window, not bytes buffered, so partial sends are resumed on the 'sent' event.
- The TCP stack runs on the application's threads: a slow handler stalls every flow hashed to that core, and IX flags the app non-responsive after about 10ms in user mode. Outbound connections pick ephemeral ports so RSS returns replies to the same thread, so two threads cannot share a flow.
- Released artifacts differ from the paper: ix-bench's bench_memcached.py drives 2,720 connections from 16 threads (paper: 1,476), and the ported memcached disables its assoc-maintenance and slab-rebalance threads while the scripts pre-size the hash with hashpower=20. No IOMMU is used, so the dataplane is trusted with host-physical addresses; profiling needs `perf kvm --guest` because IX runs as a VT-x guest (issue #35).

**Status:** Abandoned since 2017-11-06 (the maintainer still answered issues until 2021); IX's own code is MIT-style, but it needs the unlicensed Dune repo, kernel modules and DPDK 16.04 on old kernels, so treat it as a research artifact to study or reproduce, not a dependency.

[repo](https://github.com/ix-project/ix) · [benchmark](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-belay.pdf)

#### http-servers-frameworks

##### Bun (Bun.serve)  `Rust/C++/C`  `MIT for Bun's own code, per LICENSE.md (GitHub reports NOASSERTION). Bun statically links JavaScriptCore/WebKit (LGPL-2) and tinycc (LGPL-2.1), plus permissive libraries such as BoringSSL, a uWebSockets fork and uSockets (Apache-2.0), mimalloc (MIT) and zstd (BSD OR GPL-2.0).`  `active`  `Tier B`

Bun's built-in JavaScript HTTP server (Bun.serve); 2.0-2.2x Go net/http throughput on a 3-route hello-world API, 4 cores.

**Beats:** Go net/http — In the-benchmarker/web-frameworks run of 2026-09-24 (commit f673364; zrk closed-loop keep-alive, 15 s per level, mean of GET /, GET /user/:id and POST /user; server pinned to cpuset 0-3 and load generator to CPUs 4-15 of a 16-CPU x86-64 Linux 7.2 host, CPU model not recorded), Bun 1.4.x (oven/bun:1.4-slim, mislabelled 1.2.5 in data.json) running Bun.serve routes as one reusePort node:cluster worker per core did 144,254 / 145,871 / 145,897 req/s at c=64/256/512 vs 71,499 / 67,382 / 67,239 for Go 1.27 net/http with http.ServeMux (go build -trimpath, GOAMD64=v3), i.e. 2.02-2.17x. p99 latency was 0.90 vs 3.05 ms at c=64 and 4.38 vs 15.51 ms at c=512; an earlier 2026-09-20 snapshot of the suite, measured differently, gave only ~1.12x.

**Known shortcoming:** The older 2026-09-20 run (different method) shows only ~1.12x over Go net/http (93,972 vs 83,964 req/s); in the current run Bun beats Go fasthttp (the fastest Go option) by only ~1.16x. The image was oven/bun:1.4-slim though data.json labels Bun 1.2.5. The CPU name is hard-coded (uname reports x86_64, 16 CPUs). Bun's code is MIT but it statically links LGPL-2 JavaScriptCore/WebKit.

**Known shortcoming:** Bun 1.4 (2026-08-20, the benchmarked image) is a Rust rewrite; the HTTP core is still uSockets (C) plus Bun's uWebSockets fork (C++), on epoll/kqueue, not io_uring. The exact version is unknown (image tag floats at 1.4). Go was built with GOAMD64=v3 while Bun ships a Nehalem-baseline binary with runtime AVX2/AVX-512 dispatch. Routes don't match exactly (Bun 204 vs Go 200 with empty body). Raw Bun.serve with JS callbacks sat below uWebSockets.js on Node in the same run. Multi-core scaling works only on Linux (reusePort ignored on macOS/Windows; node:http ignores reusePort, #43690); Bun needed one process per core while Go used 3.9 cores in one. No published GitHub security advisories; request smuggling #29732 fixed without a CVE (#30921 open). 1.4 is the first release of a Zig-to-Rust port done largely by AI agents in 11 days (~4% unsafe); HTTP/2 and HTTP/3 in Bun.serve are experimental (no gRPC trailers, no WebSockets over h2/h3; HTTP/3 not for production). idleTimeout defaults to 10 s and counts a slow handler as idle (max 255 s, #15589); malformed framing gets 400 and close with no handler call or log; docs disagree on minimum kernel (5.1 vs 3.10).

**How:** Sockets, parsing and routing stay in native code: uSockets (C) runs an epoll (epoll_pwait2) or kqueue loop, not io_uring, and Bun's uWebSockets fork (C++) parses requests with SWAR word-at-a-time scanning (the `hasLess` bit trick on 8-byte words, with 32 bytes of required buffer post-padding) and a Bloom filter over header names, then dispatches through uWS's tree router. The glue layer (Rust since 1.4, Zig before) takes request contexts from a pre-allocated pool of 2,048 and writes response metadata inside uWS 'corked' sections, while ServerRouteList keeps route callbacks in a fixed array and caches one JavaScriptCore Structure per route's params object so the JIT sees a single shape; params are percent-decoded with SIMD. Constant `Response` routes are served with no allocation and no JS. Multi-core throughput comes from one process per core sharing the port through `reusePort` (Linux SO_REUSEPORT), with the kernel spreading connections across them.

**Use it when:**
- JS/TS HTTP APIs on Linux where per-request stack overhead dominates. In the 2026-09-24 the-benchmarker run on 4 cores, Bun.serve with JS route callbacks did 145,897 req/s at c=512 vs 67,239 for Go net/http, with p99 latency of 4.4 ms vs 15.5 ms.
- Node.js services that want more throughput without leaving JavaScript: in the same run raw Bun.serve beat Fastify on Node (68,128 req/s) by ~2.1x and Express (42,586) by ~3.4x.
- Health checks, redirects, fixed JSON and static files: constant `Response` routes are dispatched with no allocation (the docs claim at least 15% faster than returning a new Response), and `{ dir }` routes (1.4+) stream files with sendfile and handle ETag, 304 and Range.
- WebSocket fan-out servers that want built-in topic pub/sub, per-socket backpressure limits and permessage-deflate without extra packages.
- Linux deployments where one worker process per core behind `reusePort` (or node:cluster) is acceptable.

**Skip it when:**
- As a speed-only reason to leave Go: in the same run Go fasthttp (125,657 req/s) and Fiber (123,666) came within ~1.16-1.18x of Bun, and an earlier 2026-09-20 snapshot of this suite, measured differently, showed Bun only ~1.12x ahead of net/http.
- macOS or Windows production, or any host without SO_REUSEPORT: `reusePort` is ignored there, and Bun's docs say node:cluster can only load-balance HTTP on Linux. You get one JS thread per server, while the Go binary in this run used 3.9 cores from a single process with no cluster code.
- CPU-heavy handlers or state shared in memory across requests: each worker is a separate process with its own heap and one event-loop thread, so a slow synchronous handler stalls every connection on that worker.
- gRPC, or anything that needs production HTTP/2 or HTTP/3: both are experimental in Bun.serve. There is no WebSocket over HTTP/2, no server push and no response trailers. The 1.4 notes say not to ship `http3: true` to production yet, since 0-RTT is disabled and server.upgrade() returns false over H3.
- Risk-averse deployments: Bun 1.4 (2026-08-20) is the first release of a Zig-to-Rust port done mostly by Claude agent workflows in 11 days. About 4% of the Rust sits in `unsafe` blocks. Advisories for the 1.4 security fixes are held back until people upgrade, and a request-smuggling bug (issue #29732, fixed 2026-04-27) has an open request for a CVE (#30921).

**Vs siblings:** Pick Bun.serve over fasthttp only when the service is, or should become, JS/TS: staying in Go, fasthttp reached 0.86x Bun's throughput in the same run with no runtime switch. Bun.serve is the zero-dependency base under Elysia, which scored 173,877 req/s largely because its benchmark routes are constants Bun serves natively; uWebSockets.js scored 174,621 on Node with a lower-level API, so pick it instead if you must stay on Node.

**Gotchas:**
- `idleTimeout` defaults to 10 s and counts a handler that is still working but has not written a byte as idle, so slow handlers see connection resets. The maximum is 255 s (open issue #15589 asks to raise it). For SSE or long streams, call `server.timeout(req, 0)` for that request.
- Multi-core scaling fails silently: `reusePort` is ignored on macOS and Windows, and open issue #43690 (2026-09-21) reports that node:http `listen({ reusePort: true })` is ignored even on Bun, while node:net honours it.
- Since 1.3.4, requests with malformed Content-Length, Transfer-Encoding or chunked framing get 400 and the connection is closed without calling your handler or logging anything. Check a hand-written client's framing headers first.
- Constant `Response` routes are cached for the server's lifetime; call `server.reload()` to change them. WebSockets (`server.upgrade()`) work only over HTTP/1.1, so `http1: false` disables them.

**Status:** Very active (last push 2026-09-26, v1.4.2 on 2026-09-05, 96k stars, owned by Anthropic since December 2025) and MIT for Bun's own code, but the binary statically links LGPL-2 JavaScriptCore/WebKit and LGPL-2.1 tinycc, and 1.4 is the first release of the Rust rewrite, so expect a few releases of settling.

[repo](https://github.com/oven-sh/bun) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json)

#### tls

##### OpenSSLNTRU (libsntrup761 + engntru OpenSSL ENGINE)  `C`  `no license`  `abandoned`  `Tier B`

Batched sntrup761/857 post-quantum key exchange for OpenSSL 1.1.1 TLS 1.3; more LAN handshakes/sec than OpenSSL's asm X25519/P-256.

**Beats:** OpenSSL TLS 1.3 key exchange (ASM-optimized X25519 and P-256) — In the USENIX Security '22 paper (Section 4.4, Figure 5), tls_timer ran 100 samples of 8,192 sequential full TLS 1.3 handshakes (RSA-2048 certificate) from an i7-6700 client to a stunnel server on a Ryzen 7 2700X over a Gigabit LAN with Turbo off. The sntrup761 and sntrup857 CDFs sit above OpenSSL 1.1.1k's asm X25519 and P-256 on a 440-620 conn/s axis with no tabulated numbers (the demo page's example run gives about 522 vs 462 vs 449 conn/s), and the paper states no compiler, while the build scripts use gcc/clang -O3 -march=haswell or native; keygen is 156,317 amortized cycles per key at batch size 32 on a Haswell Xeon E3-1275 v3, vs 819,332 unbatched in the same library and 269,191 for CECPQ2's ntruhrss701.

**Known shortcoming:** The headline handshake comparison is CDF plots only; the only numbers are the demo page's example run (sntrup761 ~522 conn/s vs X25519 ~462, P-256 ~449), and the authors say the unloaded LAN hides the 2,197 extra bytes per handshake, so sntrup should not be read as cheaper than ECC overall. No compiler stated in the paper (build scripts use -O3 -march=haswell/native). Dead platform: patches cover OpenSSL 1.1.1f-1.1.1m (EOL 2023-09); ENGINE deprecated in 3.0 and removed in 4.0; OpenSSL 3.5+ ships X25519MLKEM768 instead. Private codepoints, post-quantum only (no ECC hybrid), dynamically linked apps only. A process that forks after filling the key pool can reuse keys (no atfork handling). The handshake that empties the pool pays the whole 32-key refill (~2.5 ms on 2 GHz Haswell) unless async_batch_lib is used. Batch keygen doesn't check malloc and frees secret polynomials without zeroing. Mixed licences; libsntrup761 has none. The maintained successor libntruprime (public domain, in Debian/Ubuntu) lacks the batch speedup (949,559 vs 156,317 amortized cycles). x86-64 Linux with AVX2 only.

**How:** Key generation is batched: for 32 keys, Montgomery's batch-inversion trick replaces 32 inversions in R/3 and in R/q with one inversion plus 3n-3 multiplications each, which brings amortized sntrup761 keygen from about 819k to 156k Haswell cycles. Batching needs big×big multiplication in (Z/4591)[x], so the authors use Schönhage's and Nussbaumer's tricks to get radix-2 NTTs over an NTT-unfriendly modulus, run on AVX2 16-bit lanes after 16x16 transposes; the R/3 side uses Karatsuba, a 5-way split with vpshufb reductions, and a Barrett-based invertibility check. engntru keeps batching invisible to TLS: each parameter set has a lock-protected per-process pool of 32 precomputed keypairs that is refilled when it runs empty.

**Use it when:**
- Reproducing or extending post-quantum TLS 1.3 handshake measurements on an OpenSSL 1.1.1 stack. The USENIX Security '22 artifact earned the Available, Functional and Reproduced badges, and tls_timer is included.
- Lab or internal testbeds where you control both endpoints and want sntrup761/857 key exchange in unmodified, dynamically linked OpenSSL apps (stunnel, nginx, Apache httpd, GNOME Web).
- Workloads dominated by many fresh full handshakes from long-lived processes on x86-64 Linux with AVX2, where ephemeral keygen CPU is the cost you care about.
- As reference code for batch sntrup761 key generation to port into another library. libntruprime lists this batch-inversion work as faster than its own code and not yet included.

**Skip it when:**
- Production TLS. OpenSSL 1.1.1 reached end of life on 2023-09-11, the ENGINE API was deprecated in OpenSSL 3.0 and removed in 4.0, and OpenSSL 3.5+ already offers the standardized X25519MLKEM768 hybrid by default.
- Talking to anything that isn't another OpenSSLNTRU peer. The codepoints are private-use (0xFE00/0xFE01), key exchange is PQ-only with no ECC hybrid, and authentication stays classical (RSA/ECDSA certificates).
- Bandwidth-bound or high-latency links. Each handshake carries 2,197 bytes of key plus ciphertext, and the authors warn that their unloaded Gigabit LAN hides this, so sntrup should not be read as cheaper than ECC overall.
- Pre-fork servers or other processes that fork after the key pool has been filled (README caveat: key reuse), statically linked applications, and non-AVX2, non-Linux or OpenSSL 3.x setups (not supported or not documented).
- When you need clear licensing: the speed-critical libsntrup761 tarball has no license file or statement.

**Vs siblings:** The siblings (EverCrypt and Mehdi Sotoodeh's curve25519, AWS-LC, wolfSSL, Tempesta TLS) speed up classical ECC or whole TLS stacks. OpenSSLNTRU is the only catalogued entry that adds post-quantum key exchange, so pick it only to study what batched sntrup KEM handshakes cost on OpenSSL 1.1.1, not to make classical handshakes faster.

**Gotchas:**
- The README warns that if a process loads engntru, fills a batch and then forks without erasing the heap, keys can be reused. There is no pthread_atfork handling.
- The request that finds the pool empty pays for the whole 32-key batch synchronously. That is about 5.0M Haswell cycles, which the paper puts at about 2.5 ms on a 2 GHz Haswell, with roughly a 143 KB footprint per batch. The async_batch_lib build option moves the refill onto a filler thread.
- The patch appends sntrup761/sntrup857 to OpenSSL's default supported_groups list. To actually send a PQ key share you still set Groups (for example SNTRUP761:SNTRUP857:X25519:P-256), and debug builds of engntru log per operation (ENGNTRU_DEBUG), which skews timing.
- In libsntrup761's batch keygen, the malloc of the scratch buffer holding secret polynomials is unchecked, and the buffer is freed without being zeroed. engntru does OPENSSL_cleanse each keypair it takes out of its pool.

**Status:** This is an abandoned research artifact (tarballs dated 2021-06-08, last patch for OpenSSL 1.1.1m in Dec 2021) that depends on an OpenSSL line that reached end of life in 2023 and an ENGINE API that OpenSSL 4.0 removed; with mixed licensing (engntru LGPL-3.0+, tls_timer Apache-2.0, libsntrup761 without a license statement) it is only usable as reference code, and maintained sntrup761 now lives in the public-domain libntruprime, which does not include the batch keygen.

[repo](https://opensslntru.cr.yp.to) · [benchmark](https://opensslntru.cr.yp.to/opensslntru-20211006.pdf)

### parsing-and-text

#### lexers-tokenizers

##### StreamTok (Static Analysis for Efficient Streaming Tokenization)  `Rust`  `no license`  `unknown`  `Tier B`

Rust streaming tokenizer using static max-lookahead analysis for O(1)-per-symbol maximal-munch tokenization vs flex's backtracking

**Beats:** flex — Peer-reviewed benchmark (RQ3, Fig. 10) reports StreamTok 2x-3x faster than flex-generated C lexers across JSON/CSV/TSV/XML/YAML/FASTA/DNS-zone/log grammars on a 10MB input; application-level tests (RQ5, Table 2) show 2.5x-3.1x for log-to-TSV and up to 5.39x for JSON minify. RQ1-RQ2 ran on an Intel Xeon E5-2640 v4 @ 2.40GHz/128GB RAM; the flex throughput comparisons (RQ3-RQ6) ran on an AMD EPYC 7252 8-core @ 3.10GHz/256GB RAM. Rust compiler version and build flags are not stated in the paper.

**Known shortcoming:** Compared against flex, which is not in this category's baseline list (re2c and hand-written lexers).

**Known shortcoming:** Paper only: no public code was found.

**How:** The paper introduces 'maximum token neighbor distance' (max-TND): the worst-case number of extra symbols needed to confirm no longer token is possible past a given match. When max-TND is bounded (statically computed via a co-accessibility fixpoint over the tokenizer DFA, O(state^2)), StreamTok builds a second automaton via powerset construction that runs K symbols ahead of the main DFA, so a fixed-size lookahead buffer of size K replaces flex's unbounded backtracking. This turns per-symbol tokenization from flex's O(k) backtracking (worse for pathological grammars) into O(1) amortized work per symbol.

**Use it when:**
- You're building/generating a tokenizer for a grammar you can statically analyze up front (JSON, CSV/TSV, XML, YAML, log formats, DNS zone files) and want to prove/bound the lookahead cost
- Streaming or memory-constrained pipelines where you cannot buffer the whole input the way a flex backtracking lexer might need to
- Grammars with pathological repeated-prefix ambiguity (the paper's synthetic (a{0,k}b)|a family) where flex's backtracking degrades with grammar parameter k but StreamTok stays O(1) per symbol
- Research/prototyping contexts where you can implement the pre-analysis + Rust runtime yourself, since there is no published crate

**Skip it when:**
- You need a drop-in flex replacement today: no public source, crate, or build artifact exists for StreamTok as of this writing
- Your grammar has unbounded max-TND — the paper found this true for ~32% of a 2,669-grammar GitHub sample, including C, R, and SQL, which fall back to non-constant (unbounded lookahead) behavior
- You need production maturity guarantees: this is a single ASPLOS '26 paper's evaluation artifact with no maintenance history, license, or usage outside the paper
- Computing max-TND for an arbitrary grammar is PSPACE-hard in the worst case (practical instances reportedly analyze in <100ms for 99.4% of the sampled grammars, but there's no guarantee for yours)
- You need C interop or the flex/re2c ecosystem (skeleton files, %option flags, yacc/bison integration) — StreamTok has none of that tooling

**Vs siblings:** Pick StreamTok over the other flex-beating entries (LRSTAR, simd-lexing, Ragel, CrossDB's hand-written parser) only if you specifically need a formal, provable bound on streaming lookahead for maximal-munch tokenization and are willing to reimplement from the paper — those other tools are usable today with real repos, while StreamTok has no code to run.

**Gotchas:**
- Falls back to unbounded lookahead behavior on grammars with unbounded max-TND (no error is thrown per se, but the O(1) guarantee disappears)
- Requires an upfront static-analysis and DFA/powerset-construction build step before any streaming can start, unlike flex's simpler generate-then-run model
- No public source, artifact, or package exists to inspect for actual API ergonomics or unsafe code use

**Status:** Maintenance status is unknown because no public repository exists at all; usability is 'reference' — this is an ASPLOS '26 paper's evaluation prototype, not a distributed library.

[benchmark](https://github.com/bojieli/ai-infra-book/blob/main/references/proceedings/ASPLOS/2026/paper-152.txt)

#### regex-engines

##### BLARE (Blazingly Fast Regular Expression)  `C++`  `no license`  `stale`  `Tier B`

Research framework that decomposes regexes into reordered sub-matches via a bandit-picked plan, layered on RE2/PCRE2/Boost/ICU.

**Beats:** RE2 — The peer-reviewed paper (Proc. ACM Manag. Data 1(2), Art. 152, SIGMOD 2023), run single-threaded on an Azure Xeon Platinum 8370C VM with C++17 code at -O3, reports BLARE 1.6x-3.7x faster than RE2 (09-2022 build), 3.4x-7.9x faster than Boost 1.65.1, and 3.1x to over 100x faster than PCRE2 10.40/JIT, across 2 Microsoft-internal production log workloads and the public US-Accidents Kaggle dataset; only the RE2/US-Accidents comparison (~1.6x) can be independently rerun from the public repo, and the ACM DOI page returns HTTP 403 to automated fetches (paper is mirrored as BLARE.pdf in the repo).

**How:** The regex is split (3-way split_regex or N-way split_regex_multi) into sub-patterns, and a multi-armed-bandit policy picks which sub-pattern to evaluate first based on observed cost/selectivity, so cheap or highly discriminating fragments reject non-matching lines before the full pattern is ever run through the underlying engine. Because the same regex is reused across many lines (log/dataset scanning), the bandit amortizes its exploration cost and converges on a near-optimal evaluation order for that workload; the final per-fragment match still calls the wrapped engine (RE2/PCRE2/Boost/ICU), so BLARE is an execution-order optimizer on top of those engines, not a replacement matcher.

**Use it when:**
- Batch, single-threaded scanning of many lines against one recurring regex (e.g. log parsing, dataset filtering) where the bandit can amortize warm-up
- You already depend on RE2, PCRE2, Boost.Regex, or ICU Regex and want extra throughput without switching engines
- Regexes with decomposable structure (alternations, literal anchors) that benefit from evaluating a cheap/selective piece first
- Reproducing or extending the SIGMOD 2023 paper's results, using original_codebase/BLARE_CODE for exact numbers
- First-match-per-line extraction workloads similar to the paper's US-Accidents / production log benchmarks

**Skip it when:**
- Any production dependency requiring maintenance or support: last commit 2023-11-20, 9 stars, 0 forks, no CI visible
- Anywhere licensing matters: no LICENSE file, so GitHub marks it all-rights-reserved by default
- Environments that can't add Abseil, Boost >=1.65.1, ICU4C, and PCRE2/jPCRE2 as build dependencies
- Multi-threaded or latency-sensitive services: paper benchmarks are single-threaded only; thread safety is not documented
- Anything needing the exact paper numbers from current main: README states main-branch code 'may not produce results identical to that in the BLARE paper'
- Non-Linux targets: build instructions are Ubuntu/apt-based and the original experiment flags use -march=native, tying binaries to the build host's CPU

**Vs siblings:** Pick BLARE over re2jit or rejit only when the goal is specifically reproducing or studying the SIGMOD 2023 decomposition/bandit technique on RE2, PCRE2, Boost, or ICU; for a production RE2 speedup, re2jit is the safer sibling (20-30% faster on capture-group workloads, no extra Abseil/Boost/ICU/PCRE2 dependency chain) since BLARE is stale and unlicensed.

**Gotchas:**
- Main-branch code is under active change and the README itself warns it may not reproduce the paper's numbers; use original_codebase/BLARE_CODE for that
- No LICENSE file is present (GitHub reports 'license: none'), so usage/redistribution rights are unclear by default
- The bundled US-Accidents CSV requires 'git lfs pull'; a newer Kaggle CSV format breaks the hard-coded read_traffic parser and needs manual edits
- Two of the three paper workloads (DB-X, System-Y) are Microsoft-internal logs and cannot be rerun outside Microsoft; only the 1.6x-vs-RE2 US-Accidents result is publicly reproducible

**Status:** Stale research prototype (last commit 2023-11-20, 9 stars, no LICENSE) — useful as a reference implementation of the decompose-and-reorder technique, not something to take a runtime dependency on.

[repo](https://github.com/mush-zhang/Blare) · [benchmark](https://dl.acm.org/doi/10.1145/3589297)

### serialization-and-formats

#### binary-schemas

##### Cornflakes  `Rust`  `no license`  `abandoned`  `Tier B`

Rust research serialization library and kernel-bypass UDP stack that sends large fields zero-copy via NIC scatter-gather, beating Protobuf/FlatBuffers/Cap'n Proto.

**Beats:** Protobuf, FlatBuffers and Cap'n Proto via the pure-Rust crates protobuf 3.0.3 (rust-protobuf), flatbuffers 2.1.2 and capnp 0.13.6 (cf-kv/Cargo.toml); Redis handwritten serialization for Table 3 — The SOSP 2023 paper runs a single-core Rust KV server on CloudLab c6525-100g machines (2x EPYC 7402P, ConnectX-5Ex 100 Gb, MTU 9000), with every system on the Cornflakes UDP stack and the pure-Rust protobuf 3.0.3, flatbuffers 2.1.2 and capnp 0.13.6 crates as baselines; the rustc version is not stated. Cornflakes served 366.5k vs 161.0-186.1k objects/s on the CDN image trace, delivered 15.4-45.9% more throughput on the Twitter trace (p99 about 52-61 us) and roughly tied on Google's small-field trace; in Redis, get/mget/lrange gained 15-40.1% over Redis's own handwritten serialization.

**Known shortcoming:** Research prototype, abandoned since 2023-07. No win on small objects (paper Table 1). Baselines are the pure-Rust protobuf/flatbuffers/capnp crates, not the C++ libraries, and the Redis gains are against Redis's own handwritten serialization.

**Known shortcoming:** Needs a kernel-bypass NIC datapath (mlx5); the Linux-socket datapath always copies. Single-core, single-jumbo-frame prototype with no segmentation or write protection for buffers in flight. Code defaults use a 256 B zero-copy threshold, while the paper's numbers use 512 B. C bindings exist but use from C++ is undocumented, and generated code fails for int32-only messages (issue #1, open since 2021).

**How:** Protobuf, FlatBuffers and Cap'n Proto copy each bytes/string field into a contiguous buffer and then again into DMA memory; Cornflakes instead posts each pinned-memory field of 512 B or more as its own NIC scatter-gather entry (zero-copy transmit), and a per-buffer reference count keeps that memory alive until the DMA completes. A per-field size threshold, checked when the field's smart pointer (CFBytes/CFPtr) is constructed, chooses copy or zero-copy: smaller fields go into an arena-backed copy buffer, because below about 512 B the reference-count cache miss costs more than the memcpy. Serialize-and-send writes the packet header, the object header and the copied data into one entry and posts the zero-copy entries directly onto the NIC ring, with no intermediate scatter-gather array (a 7.7-17.4% throughput gain in the paper). All framing (a field bitmap plus u32 size/offset forward pointers) is at the front of the object, so each zero-copy field needs only one extra scatter-gather entry.

**Use it when:**
- Microsecond-scale datacenter services such as caches and KV stores that already run on kernel bypass with Mellanox ConnectX-5/6 or Intel E810 NICs, where serialization copies are a large share of CPU time per request.
- Responses built from values of 512 B or more that already sit in pinned memory, e.g. a store that returns stored blobs. On the paper's CDN image trace (objects of 1 KB and up) it served 97-128% more objects/s than the three baselines.
- Workloads that mix small and large values, like the Twitter cache trace (about 32% of requests are 512 B or more), where the hybrid copy/zero-copy path beat pure scatter-gather by 2.3-3.9% and beat the copy-based libraries by 15.4-45.9%.
- Applications that never modify data in place while it is being sent, such as Redis-style stores, versioned stores, or code that updates by allocating and swapping pointers.
- As a reference design and threshold-calibration method (paper Section 5) when adding zero-copy serialization to your own kernel-bypass stack.

**Skip it when:**
- Small-field workloads. On Google's field-size distribution (94.9% of fields are 512 B or less) it ties or slightly trails Protobuf (844.7 vs 852.5 k req/s at 1 value) and wins only at 1-8 and 1-16 values per list.
- Standard Linux sockets. The linux-datapath returns usize::MAX as its copy threshold (always copies), and many of its functions are unimplemented!().
- Messages larger than one jumbo frame. The prototype has no segmentation: the CDN benchmark split objects into sub-objects that fit a jumbo frame, and the copy path carries a 'doesn't work if buffer is > than an MTU' TODO.
- Production or multicore use, or any need for Protobuf wire compatibility, proto2 required fields, or recursive pointer-based types (the author confirms in issue #7 that trees with pointers are not supported). The paper evaluates a single-core server and leaves multicore to future work.
- Any project that needs a license: the repo has no LICENSE file.

**Vs siblings:** Pick it over rkyv, or over FlatBuffers-family formats such as Karmem and Lite³, only when your bottleneck is the transmit-path memcpy on a kernel-bypass NIC and your fields are 512 B or larger. Those siblings speed up CPU encode/decode over any transport, but Cornflakes's gain comes from NIC scatter-gather and disappears for small fields or on normal sockets.

**Gotchas:**
- The kv app's --copy_threshold CLI default and the mlx5 datapath default are both 256 B, not the paper's 512 B. The experiment configs pass 512 explicitly (cornflakes-dynamic-512). The paper recommends re-measuring the threshold on your own NIC and CPU.
- Zero-copy applies only to data inside the stack's registered pinned memory. For any other pointer, recover_metadata returns None and the field is copied without any warning.
- Copied entries come before zero-copy entries on the wire. As a result, peers configured with different thresholds can serialize repeated elements in different orders.
- Issue #1, open since 2021: the code generator emits code with lifetime errors for messages that contain only int32 fields.

**Status:** Abandoned research prototype: the main branch was last committed on 2023-07-27 (the timetrace branch on 2024-01-19), and there is no LICENSE file, so use it as a reference design to study, not as a dependency.

[repo](https://github.com/deeptir18/cornflakes) · [benchmark](https://people.eecs.berkeley.edu/~matei/papers/2023/sosp_cornflakes.pdf)

#### json

##### Mison (speculative structural-index JSON parser)  `C++`  `no license`  `unknown`  `Tier B`

VLDB 2017 JSON parser (no public code) that jumps straight to queried fields; reports 5.5-9.1x over best of RapidJSON/Jackson/Gson.

**Beats:** RapidJSON — The authors' own single-threaded benchmark ran field-projection queries on a 3.5 GHz Xeon E5-1620 v3 under Windows 10, with data preloaded into memory and no compiler or flags stated. On Twitter records, Mison was 5.5-9.1x faster than the best of Jackson, Gson and RapidJSON (all using their streaming APIs; Jackson, not RapidJSON, was the strongest), and about 2x faster than Jackson when all 31 GitHub fields were read. No one has reproduced the full parser; Sparser's authors reimplemented only the index step, found Mison over 2 GB/s per core and over 5x RapidJSON, and noted that the implementation 'is not open source'.

**How:** First it builds a per-record structural index. AVX2 compares 32 bytes at a time against quote, backslash, colon and braces (and brackets or commas when arrays are queried), and the results become bitmaps. 64-bit bit tricks (x&(x-1), x&-x, x^(x-1), popcnt) then drop escaped quotes, build a string mask, and use a brace stack to split colons into 'leveled colon bitmaps', one per nesting depth, built only down to the deepest queried field. The k-th set bit therefore locates the k-th field's key/value boundary without tokenizing. Second, it parses speculatively. 'Pattern trees', trained on a sample (the first 1,000 records in the paper, keeping patterns seen more than 1% of the time), predict each queried field's ordinal position. The parser jumps there, checks that the key name matches, tries less frequent patterns if it doesn't, and falls back to scanning every colon at that level if none match. In the paper's Fig. 11, index-only (basic) Mison was 3.6x faster than Jackson and speculation raised that to 10.2x.

**Use it when:**
- In-memory scans of newline-delimited record streams where a query needs 1-2 fields out of dozens (the Twitter records had 25-30 top-level fields plus a 37-38-field user object). That is where the paper shows its 8-9x best case.
- Record collections that share a few layouts in a stable field order, such as the paper's GitHub user records (31 fields, always in the same order) or Twitter's user field, which sat at position 11 in 80.7% of tweets and 12 in the rest. Speculation pays off there.
- Selective filters that can be evaluated before projection. In the Spark TPC-H runs, queries with 0.5-3.7% selectivity on lineitem ran 16.3-32.5x faster with Mison than with Spark's Jackson path.
- As a design reference for a query-on-raw-JSON engine. The leveled colon/comma bitmap index is implemented in C++ in AutomataLab/Pison (MIT). The full algorithm, including pattern-tree speculation, exists in the Rust crate pikkr (MIT).

**Skip it when:**
- You need a maintained library. No official code exists, and the reimplementations are research or hobby code: pikkr's last push was 2017, and its open issue #76 reports it doesn't build on Rust 1.80. The misosoup README says 'DO NOT use for production use'. gomison contains only a README and a LICENSE.
- Full-document parsing, DOM building or serialization. With all 31 GitHub fields read, the lead over Jackson falls to about 2x. Mison has no writer and builds no tree.
- Untrusted or possibly malformed input. The simdjson paper notes that Mison does not validate documents and assumes pure ASCII rather than UTF-8. pikkr, which follows the same design, accepts {"x":0,} and returns the value '0,'.
- Highly irregular or schema-drifting data, optional fields, and arrays. In the paper, Q5 (a field with 7 root-level patterns) was slower, and Q6-Q8 needed Bloom filters or leveled comma bitmaps, which cut Mison's advantage.
- Data you will query many times. The paper itself finds converting to Parquet faster (Spark+Parquet was 1.6x faster than Spark+Mison, geometric mean over TPC-H SF1, not counting about 100 s of conversion). A single huge JSON document is also a poor fit: Mison indexes each record serially, and Pison was built to parallelize that case.

**Vs siblings:** For shipping code, use simdjson's On-Demand API: the simdjson paper says it follows Mison's structural-index outline but with branchless stage-1 code, and On-Demand skips fields you never access while validating the ones you use. Reach for Mison, in practice pikkr or Pison, only to study or reproduce pattern-tree speculation and leveled-bitmap projection. For full parsing or writing, yyjson or glaze fit better.

**Gotchas:**
- Keys are assumed unique within an object (the paper states this assumption), and input is assumed to be ASCII. Neither is checked.
- A missing queried field makes Mison either skip the whole record or return null, depending on configuration. Choosing skip silently drops rows; the Anghagaed/MISON reimplementation lists exactly this as a known bug compared with Spark.
- Speculation depends on a one-time training sample, and patterns below the weight threshold are pruned. The paper describes no retraining, so if the data layout drifts, every record falls back to the slower basic parse.
- The training cost is included in the paper's timings, but the paper does not report how much of the total it is.

**Status:** Nothing was ever released: the MSR page carries only the PDF, and Microsoft's FishStore used Mison in its SIGMOD 2019 paper but ships simdjson in the open-source repo, so treat Mison as a reference design whose nearest usable code is pikkr (Rust, MIT, dormant since 2017) or Pison (C++, MIT, index only, no speculation).

[benchmark](http://www.vldb.org/pvldb/vol10/p1118-li.pdf)

### stdlib-replacements

#### allocators

##### NUMAlloc  `C++`  `no license`  `abandoned`  `Tier B`

NUMA-aware LD_PRELOAD malloc replacement, ~21% faster than glibc malloc and ~16% faster than mimalloc on 128-thread NUMA workloads.

**Beats:** default Linux allocator (glibc 2.28 malloc) — Per the ISMM'23 manuscript (source/ISMM2023/evaluation.tex, read directly): on an Intel Xeon Platinum 8153 (8 nodes x 16 cores, 512GB RAM, Debian 10, GCC-8.3.0, THP+AutoNUMA on, hyperthreading off), averaged over 30 runs at 128 threads across PARSEC, five CORAL-2 OpenMP/MPI apps, and 7 real applications, NUMAlloc was 20.9% faster than glibc-2.28's default malloc and 15.7% faster than the next-best allocator tested (mimalloc-1.6.7), also beating TCMalloc, TCMalloc-NUMA, and TBB by 18-21%; the OpenMP/MPI subset alone showed 26.1% over glibc and 16.5% over mimalloc; best case fluidanimate was 5.3x glibc and 4.6x mimalloc. A superseded SC'22 draft in the same repo reports different numbers (19.0% vs glibc) for an overlapping but not identical benchmark set.

**How:** Layers a fast per-thread heap over a per-node heap tier, so the common malloc/free path never touches cross-node state; freed objects are returned to the heap tier matching the node they came from ('origin-aware' return) instead of a shared free list, keeping frees node-local under NUMA. During a program's single-threaded startup/teardown, an optional interleaved 'inter-heap' spreads allocations across all nodes to avoid one node absorbing all pre-fork memory. It's also built with transparent huge pages (-DUSE_HUGE_PAGE) to cut TLB misses on the large per-node heaps, which the ISMM'23 paper's own remote-access/TLB-miss profiling (perf) ties directly to the wins on dedup, fluidanimate, pbzip2, streamcluster and swaptions.

**Use it when:**
- Multi-socket/multi-node NUMA Linux servers (paper: 8-node, 128-core Xeon Platinum 8153) running allocation-heavy, multi-threaded HPC or server workloads similar to PARSEC, CORAL-2 OpenMP/MPI, httpd, MySQL, or Memcached
- You can rebuild the allocator with -DNUMA_NODES=<actual node count> -- it's hardcoded at compile time and the shipped Makefile defaults to 2
- A plain C/C++ executable you can LD_PRELOAD, not something needing a vendored/linked allocator API
- You can pin to an old toolchain matching the paper (GCC 8.3.0, C++14, Debian 10) and, critically, a pre-2.34 glibc
- Research/reference use where you can independently validate results, not a production dependency

**Skip it when:**
- Any current Linux distro: an open, unmerged PR (#1, filed 2026-07-08) shows NUMAlloc infinite-recurses and crashes via an assertion the moment a second thread is created on glibc >= 2.34 (Ubuntu 22.04+, Debian 12+, effectively any 2022+ distro), because its pthread_create interposition looks for a libpthread.so.0 that glibc merged into libc.so.6
- Single-socket/single-NUMA-node machines -- the whole design is cross-node locality, so on one node you likely get the ~10-12% THP memory overhead for no throughput gain
- Production or license-sensitive use -- no top-level LICENSE file; core NUMA-specific headers (pernodeheap.hh, perthreadheap.hh, interheap.hh) carry no license header at all, and files inherited from the FreeGuard project are GPL-2.0-or-later
- Need active maintenance -- last push 2023-03-01, 2 GitHub stars, and the repo is a research dump of ~10 UTSASRG projects plus a dozen near-duplicate source-* variant folders with no indication which one produced the paper's numbers
- Serial-phase-heavy programs -- the interleaved inter-heap exists specifically to offset interleaving costs during single-threaded phases, so a program that spends most of its time before spawning threads pays extra bookkeeping for little benefit

**Vs siblings:** Pick NUMAlloc over SuperMalloc/Hoard/scalloc/rpmalloc/ltalloc/smmalloc only if you specifically need NUMA-node-local allocation on an 8-node-class multi-socket server, can rebuild for your topology, and are willing to fix the glibc>=2.34 pthread_create crash yourself; those siblings target single-node thread-count scaling and work off the shelf today, whereas NUMAlloc is an abandoned research prototype that currently fails to launch multi-threaded programs on modern Linux.

**Gotchas:**
- Open, unmerged PR #1 (2026-07-08): pthread_create resolves to the library's own wrapper instead of the real symbol on glibc >= 2.34, causing infinite self-recursion and an assertion crash on the second thread spawned under LD_PRELOAD; the author confirms the same bug exists in all ~12 source-* copies in the repo
- NUMA_NODES is a compile-time constant (Makefile default 2, paper implies 8) -- building for the wrong node count is a silent topology mismatch, not a runtime-detected error
- Heap is placed at a fixed virtual address (0x100000000000) rather than obtained from mmap(NULL, ...), which can collide with sanitizers or other tools that reserve that address range
- About 10-12% higher RSS than glibc from transparent-huge-page use; drops to roughly glibc-comparable memory use with THP disabled (dropping -DUSE_HUGE_PAGE), per the input record's tradeoffs

**Status:** Abandoned since its last push on 2023-03-01 (2 GitHub stars) and usability is 'reference' only -- no top-level LICENSE, several core headers unlicensed, GPL-2.0-or-later on FreeGuard-derived files, and an unresolved crash-on-second-thread bug on any glibc >= 2.34 system as of this writing.

[repo](https://github.com/UTSASRG/numalloc) · [benchmark](https://raw.githubusercontent.com/UTSASRG/numalloc/master/ISMM2023/evaluation.tex)

#### bitsets-and-succinct

##### plf::bitset (plf_bitsets)  `C++`  `Computing For Good License v1.01 (non-OSI; zlib-style terms plus ethical field-of-use restrictions 4a-4e)`  `active`  `Tier A`

Header-only bitset beating std::bitset at ranged set/reset, shifts, and bit search, minus from-string constructors.

**Beats:** std::bitset — First-party benchmark (plflib.org/bitsets.htm, author's own numbers, methodology and code published) on an Intel i7-9750H under Windows 10, GCC 13.2 (libstdc++) and MSVC 2022 (MSVC STL), O2/AVX2/C++23 release build: plf::bitset beat std::bitset by 24%/20% overall on a full-operation test-suite loop, ~101%/98% (GCC) and 35%/22% (MSVC) on left/right shift, and 34,652%/67,612% on set_range/reset_range across 10,000 random ranges of a 128,000-bit bitset - the last figure mostly reflects that std::bitset has no bulk range-set primitive at all rather than a raw constant-factor win.

**How:** Same word-array layout as std::bitset (array of storage_type words), but set_range/reset_range write whole words with masks instead of looping bit-by-bit like std::bitset callers have to (std::bitset has no bulk range primitive at all, which is why that number is ~340x-676x rather than a small constant factor). Bit search (first/next/prev one or zero) uses compiler builtins directly (__builtin_ctz/_BitScanForward64, or std::countr_zero/std::popcount under C++20's <bit>) instead of a generic scan loop. No SIMD/AVX intrinsics are used in the header itself despite the AVX2 benchmark flag - the ~20-24% overall test-suite gain comes from tighter, more branch-light word-level code (e.g. compile-time-eliminated overflow-bit handling, template-gated bounds checks) rather than a different algorithm.

**Use it when:**
- Fixed-size bit flags where you already use std::bitset and don't rely on its from-string constructor
- Workloads that set/clear/query contiguous ranges of bits (set_range/reset_range) instead of single bits in a loop
- Need a runtime-sized or user-buffer-backed bitset (plf::bitsetb) - e.g. per-instance variable size, or placement over pre-allocated/arena memory
- GCC or MSVC targets on x86-64, where the author's release numbers were actually measured (i7-9750H, O2/AVX2, C++23)
- Want first/last-one/zero search or an allocation-free swap that std::bitset doesn't offer

**Skip it when:**
- Code that constructs std::bitset from a string or unsigned long/long long - those constructors aren't implemented here
- Organizations that require an OSI-approved license - Computing For Good v1.01 is zlib-like but adds ethical-use restrictions (4a-4e) and is not OSI-approved
- Clang/libc++ targets - the author states libc++ was not tested or benchmarked
- Projects that need independently-reproduced numbers - all benchmark results are first-party (author's own page and repo), with 14 stars and no third-party reproduction found
- Code paths hitting the four currently-open correctness issues (overflow-bit restoration, not-found sentinels - see gotchas) until they're resolved

**Vs siblings:** Pick plf::bitset over CRoaring, pasta::bit_vector, better_bitset, BitLib, and sul::dynamic_bitset when you specifically want std::bitset's fixed-size, non-succinct, no-rank/select shape (not a compressed/sparse structure like CRoaring, not a rank/select index like pasta::bit_vector) but need faster ranged set/reset or shifts than std::bitset provides; use plf::bitsetb instead of BitLib or sul::dynamic_bitset when you want that same std::bitset-shaped API with a runtime-determined size or a user-supplied buffer rather than a vector<bool>-style resizable container.

**Gotchas:**
- Four issues are open on the repo (#3, #4, #5 filed against overflow-bit restoration in set_overflow_to_one, all_range's empty-range path, and next/prev_zero's not-found path; #6 requests a proper not-found sentinel for the search functions) - check these before relying on exact behavior at bitset-size edges
- from-string / from-ulong / from-ullong constructors aren't implemented - existing std::bitset(str) call sites need to be rewritten, not just retyped
- The third template parameter (hardened, default false) controls bounds checking; with it left at default, operator[] is unchecked like std::bitset's, while test() still throws - read the header if you rely on a specific check point
- License is Computing For Good v1.01, not a standard permissive license - clauses 4a-4e restrict use by field/purpose, which needs a legal read some organizations won't accept

**Status:** Actively maintained (last commit 2026-09-19, four open bug-tracking issues under active triage); usability is marked 'reference' rather than drop-in because the non-OSI Computing For Good v1.01 license's ethical-use clauses (4a-4e) call for a legal review before production adoption at most companies.

[repo](https://github.com/mattreecebentley/plf_bitsets) · [benchmark](https://plflib.org/bitsets.htm)

#### ordered-maps-trees

##### S+ tree (Algorithmica static B-tree array layout)  `C++`  `no license`  `abandoned`  `Tier A`

SIMD (AVX2) static B+-tree array layout beating std::lower_bound/std::set on batched int32 lookups.

**Beats:** std::lower_bound (primary), std::set (bench code binsearch/set.cc actually uses std::multiset), absl::btree — Reciprocal-throughput microbenchmarks on an AMD Zen 2 CPU with Clang 10 (-O3 -march=native) show the S+ tree up to ~15x faster than std::lower_bound on cache-resident sorted int32 arrays (~8x for arrays >1e6, up to 2^25 elements), up to ~30x faster than std::multiset::lower_bound, and (pointer variant) ~15x faster than Abseil's absl::btree on large arrays; the author explicitly notes real single-query latency gains are much smaller than these throughput figures.

**How:** The sorted array is rearranged into a B-ary tree (16 keys per node/cache line, branching factor 17) stored as one flat array with compile-time layer offsets instead of pointers (the 'S+ tree' = separate internal/leaf layers, vs. the pointer/Eytzinger-numbered 'S-tree'). Each node comparison loads 16 keys into two AVX2 256-bit registers, does _mm256_cmpgt_epi32 SIMD compares, permutes/packs the masks, and extracts the branch index with tzcnt, replacing several scalar branchy comparisons per level with one branchless SIMD step; large trees also use aligned_alloc + madvise(MADV_HUGEPAGE) to cut TLB misses. The headline numbers are reciprocal-throughput over batches of independent queries, which lets the CPU overlap several independent tree descents (~3x ILP per the article) rather than shrinking single-query latency much.

**Use it when:**
- Read-mostly/static sorted 32-bit-integer key sets that are bulk-built once (or rarely rebuilt), not mutated incrementally
- Workloads that issue many independent lookups that can be batched/pipelined (joins, index probes, columnar scans) so the reciprocal-throughput gains actually materialize
- x86-64 targets with AVX2 where you can build with -march=native and enable transparent huge pages for large (>1e6-element) arrays
- Arrays that fit or mostly fit in cache, where the article's ~15x-over-std::lower_bound number applies (~8x still holds up to 2^25 elements)
- You're willing to vendor and adapt a single .cc file into your own build rather than link a maintained library

**Skip it when:**
- You need insert/delete or any online mutation of the key set -- no dynamic update path is implemented, only a full prepare() rebuild
- Latency-sensitive single-query paths with data-dependent lookups (pointer chasing between queries) -- the author states real per-query latency gains are much smaller than the throughput numbers
- Non-x86 or AVX2-unavailable targets -- the article says porting to AVX-512 or Arm NEON needs 'non-trivial changes', and none is provided in this repo
- You need arbitrary key/value types, comparators, or a runtime-chosen array size -- N is a compile-time constant baked into the offset/height calculations
- Anything beyond experimentation/benchmarking in production -- no LICENSE file, abandoned since 2022, and the author frames this as teaching/reference code

**Vs siblings:** Pick this over tlx::btree or boost::container::flat_set/fast-containers when your key set is effectively static (bulk-loaded, then read-heavy) and lookups can be batched for throughput; those siblings are actual libraries supporting online insert/erase/find, whereas amh-code is an unpackaged technique reference you'd have to adapt, re-tune, and maintain yourself.

**Gotchas:**
- Array size N is a preprocessor/constexpr constant (binsearch.hh defaults to 1<<20), so each key-set size effectively needs its own compiled variant rather than being a runtime parameter
- Requires AVX2 codegen (-march=native or explicit target attributes); there is no scalar fallback path in these files
- Large-array speedups depend on aligned_alloc + madvise(MADV_HUGEPAGE) actually getting huge pages from the OS; without that configured, expect smaller gains than reported
- Headline speedups are reciprocal-throughput over batches of independent queries -- single dependent-query ('real') latency shows a much smaller win, per the author's own caveat in the article

**Status:** Abandoned reference code (last commit 2022-10-06, no LICENSE file) published as teaching/benchmark material for the Algorithmica HPC book, not a maintained library -- treat it as a technique to study and port, not a dependency to pull in.

[repo](https://github.com/sslotin/amh-code) · [benchmark](https://en.algorithmica.org/hpc/data-structures/s-tree/)

#### perfect-hash-static-tables

##### zmph (Zig Minimal Perfect Hash Map)  `Zig`  `no license`  `active`  `Tier A`

Pure-Zig minimal perfect hash map for fixed string key sets; about 1.7x faster average lookups than std.StringHashMap.

**Beats:** Zig std.StringHashMap and std.StaticStringMap — The author's own zBench run (Zig 0.15.1, ReleaseFast, Core i7-8750H, Debian) built each map at runtime from /usr/share/dict/words and timed 100,000 single lookups, all hits, one timer per call: zmph averaged 26 ns (min 18, p99 38), std.StringHashMap 45 ns (min 22, p99 106), and std.StaticStringMap 10.4 us, because its lookup is a linear scan over keys of equal length. Build times were 28.9 ms, 6.1 ms and 2.0 ms. Timer overhead is included in every figure and the comptimeInit path was never measured, so the ~1.7x is an average of wall-clock samples, not an exact ratio of lookup costs.

**How:** It uses hash-and-displace minimal perfect hashing, as in Steve Hanov's 'Throw away the keys' post (which cites CHD by Belazzougui, Botelho and Dietzfelbinger), and this is what the README links to. Keys are grouped into n buckets by Murmur3_32 with seed 0. Buckets are placed largest first by trying seeds d = 1, 2, ... until every key in the bucket lands in a free slot, and single-key buckets go straight into the leftover slots, stored as -slot-1. A lookup reads one displacement entry, computes a second Murmur3_32 only for keys from multi-key buckets, and does one key comparison, with no probing and no empty slots; std.StringHashMap is open addressing with linear probing (Wyhash, 80% max load), so its lookups can probe several slots.

**Use it when:**
- Zig code with a fixed string key set (a word list, command names, identifiers) that is built rarely and read very often. From the README averages, the extra ~23 ms of build time versus StringHashMap on a dictionary is paid back after roughly 1.2M lookups per build (derived: 22.8 ms / 19 ns).
- Read paths where tail latency matters on a large set: the README reports p99 38 ns vs 106 ns and max 96 ns vs 29.8 us against StringHashMap (all hits, dictionary-sized key set).
- Dictionary-sized string sets where you would otherwise use std.StaticStringMap. That map scans every key of the same length, which is why it is ~400x slower in this benchmark.
- Small key sets known at compile time, such as a tokenizer's keyword table (see examples/parser.zig). `comptimeInit` puts the table in the binary with no runtime build and no allocator. Note that this path is not benchmarked.

**Skip it when:**
- Maps that change after they are built. There is no put, remove or iteration, so any change means a full rebuild. `init` is documented as O(N^2), and the build took 28.9 ms vs 6.1 ms for StringHashMap on the same word list.
- Lookups where many keys are absent, on a map built with `init()` at runtime. See gotchas: from my reading of the source, a miss that lands on an empty bucket is illegal behavior. The benchmark and the tests only look up keys that are present.
- Non-string keys. K is generic, but getIndex compares with `std.mem.eql(u8, ...)`, so in practice only `[]const u8` keys compile.
- Small keyword sets where StaticStringMap is the incumbent. Nothing in the repo measures that size, which is the size StaticStringMap is designed for ('optimized for small sets of disparate string keys').
- Anything you need to ship or modify. There is no LICENSE file, it has 8 stars, and no CI run has ever been recorded (the test workflow only runs when triggered by hand).

**Vs siblings:** It is the only Zig entry in this category, so choose it when you write Zig and want faster reads than StringHashMap on a large fixed string set. In C++ (frozen, qlibs mph, constexpr-phf), Rust (rust-phf, QuickPHF) or Go (constmap), use those siblings instead, and since zmph has no license, treat it as a reference for writing your own hash-and-displace table.

**Gotchas:**
- On a map built with `init()`, empty buckets keep displacement maxInt(isize). getIndex then @intCasts that value to a u32 hash seed. The Zig 0.15.1 langref calls this safety-checked illegal behavior: a panic in Debug/ReleaseSafe, anything can happen in ReleaseFast. So misses can crash a map built this way. `comptimeInit` fills empty slots with 0 and avoids the problem.
- Duplicate keys are not detected. Two equal keys always hash to the same slot, so the seed search never succeeds. Keys are stored as borrowed slices, so the key bytes must outlive the map. Do not call `deinit` on a `comptimeInit` map, because its allocator field is left undefined.
- `comptimeInit` builds n buckets that each hold an n-slot fixed array and sets an n^2 eval branch quota, so compile-time memory and work grow quadratically. It suits keyword-sized tables, not dictionaries. It also failed to compile from the Aug 2025 port to Zig 0.15.1 until the v0.2.1 fix on 2026-01-31.
- build.zig.zon pins zBench by hash to a branch archive (refs/heads/zig-0.15.1). That branch changed zbench.zig in Dec 2025, after the pin, so a fresh fetch will likely fail the hash check, and because the dependency is not lazy, projects that depend on zmph may hit this too. examples/build.zig still passes the pre-0.15 addExecutable fields (root_source_file/target/optimize), which Zig 0.15.1 removed.

**Status:** Active but small: v0.2.1 was released 2026-01-31, it has one author and 8 stars, and no issues or CI runs have ever been recorded. With no LICENSE file it is reference-only, so read it to learn the technique rather than vendoring it.

[repo](https://github.com/PaNDa2code/zmph) · [benchmark](https://github.com/PaNDa2code/zmph/blob/master/README.md)

#### searching

##### SIMD Quad search (Lemire blog benchmark)  `C++`  `no license`  `active`  `Tier A`

SIMD quaternary-interpolation search over sorted 16-bit arrays in 16-element blocks; beats std::binary_search on Roaring-Bitmap-style containers.

**Beats:** std::binary_search — On an Intel Emerald Rapids server (GCC) and an Apple M4 (Apple LLVM), Release-mode C++23 builds (CMake default -O3 -DNDEBUG, no -march flags) benchmarking membership queries on sorted uint16_t arrays (sizes 2-4096, 100,000 arrays per size, 10M cold-cache + 10M warm-cache queries per size): simd_quad beat std::binary_search in every tested configuration, with the >2x speedup holding specifically for Intel-warm-cache and Apple-M4-cold-cache; the opposite cache mode on each platform showed smaller, numerically unstated gains (charts only, no numeric tables in the post text).

**How:** It narrows to a candidate 16-element block using quaternary interpolation search over block-boundary keys (comparing 3 split points per round instead of binary search's 1, so fewer rounds), then checks all 16 candidates in that block with one SIMD compare pass (NEON vceqq_u16 or SSE2 _mm_cmpeq_epi16 over two 8-lane loads, ORed and reduced) instead of continuing scalar element-by-element comparisons.

**Use it when:**
- Sorted arrays of uint16_t, roughly 16-4096 elements (the tested range and Roaring array-container size cap)
- Membership-only lookups (found/not-found), not insertion-point queries
- Workload is warm-cache-dominated on x86 (author measured >2x vs std::binary_search there) or cold-cache-dominated on Apple Silicon (>2x there)
- You can adapt call sites to the array_container_t{const uint16_t*, size_t} shape and compile with NEON or SSE2 guaranteed
- You're comfortable vendoring a ~40-line function rather than linking a library

**Skip it when:**
- Any key type other than uint16_t — the compares are hardcoded to 16-bit values
- General-purpose sorted containers with arbitrary element types/sizes where std::binary_search/lower_bound already fits
- Platforms without SSE2 or NEON — no scalar/AVX2/SVE fallback beyond a small-array linear scan below 16 elements
- Need for an insertion point (lower_bound semantics) — simd_quad only returns a boolean
- Anything requiring production hardening: this is unpackaged blog-benchmark code with no test suite beyond a self-check against std::binary_search inside the benchmark harness itself, and no issue tracker for this specific function

**Vs siblings:** Pick simd_quad over the generic siblings (sb_lower_bound, scandum/binary_search, FastBinarySearch) only when you're already working with sorted uint16_t arrays capped near 4096 elements in the Roaring-Bitmap array-container shape and can adapt to its struct-based calling convention; for generic sorted-array membership or lower_bound over other primitive types or larger/unbounded sizes, the siblings are closer to drop-in replacements for std::lower_bound/bsearch and are the better fit.

**Gotchas:**
- Assumes the array is already sorted ascending; the code does not check this and will silently return wrong answers on unsorted input
- Arrays smaller than 16 elements (the fixed block size) skip the SIMD/interpolation path entirely and fall back to a plain linear scan, so there's no benefit below that size
- The quaternary-interpolation step over plain SIMD-binary-search only helped in the author's own ablation on the Intel machine (large arrays, cold cache); on Apple M4 it had little effect, so porting it as-is to ARM buys less than the Intel numbers suggest

**Status:** Not a maintained library — it's single-author blog-benchmark code; the repo README explicitly disclaims industrial-strength quality ('don't expect or ask for industrial-strength software... it can be wrong, slow, poorly coded') and states the code is public domain ('don't bother forking, just steal it') even though no formal LICENSE file exists. Usability is reference-only: read the technique, don't depend on the repo as a dependency.

[repo](https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog) · [benchmark](https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/)

### storage-and-data

#### caches

##### Cacheus  `Python`  `reference (no LICENSE file found in repo)`  `stale`  `Tier B`

Research Python simulator of Cacheus (FAST'21), a learned two-expert page-cache eviction policy that competes with ARC/LIRS/DLIRS on hit rate.

**Beats:** LRU — Only simulated hit rate was measured, in Python, with no compiler, hardware or throughput numbers. The study ran 17,766 simulations on 329 one-day block-I/O traces from 5 datasets at 6 cache sizes (0.05%-10% of footprint). In paired t-tests over the paper's 30 workload/cache-size combinations, Cacheus C3 is distinctly best in 47%, indistinguishable from the best of ARC/LIRS/DLIRS/LeCaR in about 40%, and worse in 13%. The extremes are +38.32 absolute hit-rate points vs ARC (CloudPhysics, 10%) and -15.12 vs DLIRS (MSR, 5%). The paper gives no isolated Cacheus-vs-LRU number; LRU appears only in the compared set and the ranking study.

**Known shortcoming:** 'Best on the majority of workloads' is overstated: the paper has it distinctly best on 47%, tied on ~40% and worse on 13%; the 38.32% is an absolute hit-rate difference vs ARC; Python simulator (verifier downgrade).

**Known shortcoming:** Hit rate only, from a pure-Python simulator; no throughput or hardware, no isolated vs-LRU number. Does not run as shipped (example.config is invalid JSON; run_alg.py raises TypeError for Cacheus). Code differs from the paper (fixed learning-rate init, global np.random.seed(123)); per-request list append grows memory with trace length.

**Known shortcoming:** Metadata is 3.3x LRU's (SIEVE paper); the S3-FIFO paper finds Cacheus often trails ARC-class algorithms. No LICENSE; reuse via the libCacheSim C port (Apache-2.0 since 2026-09). Issue #16 unanswered.

**How:** The gain is hit rate, not speed. Following LeCaR, it uses online regret minimization: on each eviction it samples one of two experts by weight, and when a missed key is found in an expert's eviction history (each N/2 entries), that expert's weight is multiplied by exp(-learning_rate). Expert one is SR-LRU (scan-resistant LRU): the cache is split into a reuse partition R and a small scan-resistant partition SR that new keys enter, evictions come only from SR, and the partition sizes adapt when demoted or new items are re-referenced. Expert two is CR-LFU (churn-resistant LFU), an LFU heap that breaks frequency ties by evicting the most recently used key, which pins a stable subset during churn. The learning rate itself is tuned every N requests by stochastic hill climbing and resets after 10 degrading windows, so no hyperparameters are hand-set.

**Use it when:**
- Reproducing the FAST'21 results, or using Cacheus as a baseline in cache-policy research on block-storage traces (FIU and MSR readers are built in)
- Estimating, before any native implementation, whether a fixed-size page or block cache (buffer cache, SSD or flash cache tier) would gain hit rate from an adaptive recency/frequency policy
- Workloads that shift between scan, churn, LRU-friendly and LFU-friendly phases, with caches small relative to footprint (the paper tests 0.05%-10%)
- When you want LeCaR-style learned eviction without hand-tuning the learning or discount rate
- As a readable reference to port; for reusable code, use libCacheSim's Apache-2.0 C port (Cacheus.c, SR_LRU.c, CR_LFU.c)

**Skip it when:**
- Any throughput- or latency-sensitive path: it is pure Python with an O(log N) LFU heap update on every hit and no concurrency, and no throughput numbers are published
- Variable-size objects (web, CDN, key-value caches): the simulator counts unit-size 4 KiB pages and the cache size is in pages
- Memory-constrained caches: the paper states about 2N metadata entries (N resident plus N history), and the SIEVE paper (NSDI'24) puts Cacheus per-object metadata at 3.3x LRU's
- Workloads where most objects are requested exactly twice with a gap: the S3-FIFO paper (SOSP'23) names Cacheus among partitioned policies that handle this badly at small cache sizes, and found Cacheus often less competitive than traditional algorithms such as ARC in its broad simulations
- Code reuse in products: the repo has no LICENSE file

**Vs siblings:** Pick Cacheus over SIEVE, S3-FIFO and GL-Cache (all in libCacheSim, which also carries a Cacheus port) only when the target is a unit-size block or page storage cache with mixed scan and churn phases, and hit rate matters more than CPU and metadata cost. For throughput, simplicity or web/KV traces, use SIEVE or S3-FIFO. For a production in-process cache, use Caffeine or W-TinyLFU. For variable-size objects, use LHD, AdaptSize or LRB.

**Gotchas:**
- Won't run out of the box: example.config is invalid JSON (trailing comma in the alecar6 block) and doesn't list cacheus, and run_alg.py still calls the constructor and request() with one argument, which raises TypeError for Cacheus
- The code differs from the paper. It starts the learning rate deterministically at sqrt(2 ln 2 / N) rather than a random value in [0.001, 1], and the constructor calls np.random.seed(123), which resets numpy's global RNG for anything else in the process. libCacheSim's port says it follows the paper instead, so results from the two can differ.
- Memory grows with trace length: the learning-rate updater appends to a list on every request, even with visualization turned off
- SR-LRU and CR-LFU are not separate modules. They are inlined in cacheus.py (s = R, q = SR, and the heap's tie-break in Cacheus_Entry.__lt__). Open issue #16 (June 2025, no reply) asks where they are, so readers can mistake the code for plain LRU+LFU.

**Status:** Stale research code: cacheus.py last changed in April 2021 (bug fixes) and the repo last changed in October 2023. With no LICENSE it is reference-only; the maintained, Apache-2.0 route is libCacheSim's C port (relicensed September 2026), though that port has open TODOs such as 'this function may not work' in Cacheus_to_evict.

[repo](https://github.com/sylab/cacheus) · [benchmark](https://www.usenix.org/system/files/fast21-rodriguez.pdf)

##### Masstree  `C++`  `MIT plus two clauses taken from the W3C license (no use of the copyright holders' names in publicity without prior written permission; title to copyright stays with the holders). It is a custom text, not a verbatim OSI/SPDX license; GitHub reports NOASSERTION.`  `stale`  `Tier B`

Concurrent in-memory trie of B+-trees with ordered range scans; authors measured 1.5-3.7x Redis 2.4 throughput on 16 cores.

**Beats:** Redis — In the authors' EuroSys 2012 paper, on 16 cores of a 2.4 GHz AMD Opteron 8431 server with networking and logging on, the full Masstree server did 9.10M uniform gets/s against 5.97M for 16 Redis 2.4.5 processes, 5.84M puts/s against 2.97M, and 6.05-9.86M against 2.13-2.70M on Zipfian MYCSB-A/B/C (about 1.5-3.7x), while memcached 1.4.8 was 7.4% faster on uniform gets. No compiler or flags are given, the baselines date from 2011, and the paper itself calls the comparisons 'not entirely fair'.

**Known shortcoming:** Numbers are from the EuroSys'12 paper vs Redis 2.4.5 and memcached 1.4.8 (2012 versions); the license is MIT plus W3C-style publicity clauses (custom).

**Known shortcoming:** Against memcached it is only +7.4% on uniform gets (the 2.5x figure is the authors' own hash table inside Masstree's framework). x86-only inline asm (arm64 PR #31 open since 2018); a source drop with no install/lib, and embedders must define epoch globals and run rcu_quiesce or memory is never freed. Open bugs: scan race (#33), empty leftmost leaves not freed (#43), reads outside the key buffer / possible segfault (#42). Stale since 2023-10; own protocol, no TTL or eviction (not Redis-compatible).

**How:** Keys are cut into 8-byte slices stored as byte-swapped 64-bit integers, so each trie layer is a fanout-15 B+-tree that compares keys with plain integer compares (the paper credits this with 13-19%) and compares a long shared prefix only once per layer. Nodes are four cache lines and are prefetched whole before use, so each level costs about one DRAM latency. Readers use optimistic concurrency control (they check per-node version counters, take no locks and never write shared memory), while writers lock only the nodes they touch, publish a leaf insert in one step through a 64-bit permutation field, and free nodes through epoch-based (RCU-like) reclamation. The paper's factor analysis also credits a fast allocator and 2 MB superpages with a 27-37% gain.

**Use it when:**
- You need an ordered in-memory index with range scans that many threads share, for example the index layer of an in-memory database or transactional store where a hash table cannot serve scans.
- Access is skewed (Zipfian) on a multicore box. At the paper's highest skew (delta=9), one shared Masstree delivered 3.5x the throughput of 16 hard-partitioned instances, which stall on the hot partition.
- Keys share long prefixes (URLs, hierarchical or composite keys). The trie layers compare each 8-byte slice once instead of re-comparing the whole key at every tree level.
- Workloads are small-key, small-value and read-heavy on x86-64 Linux. The paper measured 9-10M gets/s on 16 cores with networking and logging included.
- You want a reference design or research baseline. HN commenters note Masstree became a standard comparator in key-value store papers.

**Skip it when:**
- You want a Redis replacement. It has no RESP protocol, rich data types, TTLs or eviction (none found in the source), replication or clustering, and mtd is a research-grade server.
- You only do point lookups on uniform keys. The paper's own concurrent hash table reached 2.5x Masstree's throughput, 16 hard-partitioned Masstrees beat the shared tree by 1.5x on uniform gets, and memcached 1.4.8 was 7.4% faster on uniform gets.
- You target anything other than x86. The master branch hard-codes x86 inline asm (pause, mfence, prefetcht0, bswapq, rdtsc), and its acquire/release fences are compiler-only barriers that rely on x86 ordering. The arm64 port (PR #31) has been open and unmerged since 2018.
- You need an actively maintained dependency. The last commit was 2023-10-12, it has one old tag (v0.9.0) and no GitHub releases, and 9 issues remain open, including a scan race (#33) and empty leftmost leaves that are not freed after deleting all keys (#43).
- Your legal review cannot approve a custom license. It is MIT plus W3C-style publicity and title clauses, and GitHub shows NOASSERTION.

**Vs siblings:** Pick Masstree over MICA or MemC3 when you need ordered keys and range scans: both are hash-based, and MICA's paper reports 75.5-76.9 Mops against Masstree's 16.5 on tiny point operations. Prefer it over Garnet, Dragonfly or Valkey only if you are building your own storage engine and want an embeddable concurrent ordered index rather than a maintained server that speaks the Redis protocol.

**Gotchas:**
- Embedding it means defining the globals the library expects (globalepoch, active_epoch and recovering, as unit-mt.cc does), creating a threadinfo per thread, and advancing epochs or calling rcu_quiesce regularly. Without that, freed nodes accumulate in per-thread limbo lists.
- Key handling does intentional 'sloppy' reads that can touch up to 8 bytes outside the key buffer (the preconditions are documented in string_slice.hh). Open issue #42 reports a possible segfault for key lengths that are not a multiple of 8, so pad key buffers and expect sanitizer reports.
- The write API is low-level. tcursor.find_insert() or find_locked() locks the leaf, you write lp.value(), and lp.finish(+1/0/-1, ti) must always be called because it applies the insert or remove and releases the lock.
- Assertions are compiled in by default. The README says to build with ./configure --disable-assertions before measuring performance, and the tree's node allocations go through the threadinfo pool allocator, so the malloc you link affects results.

**Status:** Stale (last commit 2023-10-12, no GitHub releases, arm64 PR never merged) and under a custom MIT-plus-W3C-clause license, so treat it as a reference design to study, or to vendor after legal review, rather than a maintained dependency.

[repo](https://github.com/kohler/masstree-beta) · [benchmark](https://pdos.csail.mit.edu/papers/masstree:eurosys12.pdf)

#### columnar-analytics

##### Databend  `Rust`  `Apache-2.0 (core) + Elastic-2.0 (enterprise code: src/query/ee, src/meta/ee, src/bendsave, ee_main.rs binaries), per the repo LICENSE file`  `active`  `Tier B`

Rust SQL data warehouse over object storage; ~1.6x faster than DuckDB on ClickBench hot runs on 192-vCPU hardware.

**Beats:** DuckDB — ClickBench runs 43 queries on the 100M-row hits table, both engines on the same AWS c7a.metal-48xl (AMD EPYC 9R14, 192 vCPU). Databend v0.9.53-nightly (a prebuilt musl binary from Feb 2023, run 2026-09-26) sums best-of-3 per query to 9.91s, against 15.70s for the official prebuilt DuckDB CLI on its native .db file (run 2026-05-11, version not recorded): ~1.6x, faster on 35/43 queries, ~1.75x geomean using ClickBench's +10ms shift. c6a.metal looks similar (10.65s vs 17.32s), but c6a.4xlarge reverses (41.93s vs 26.25s), cold sums favour DuckDB everywhere, and neither side states compiler or flags.

**Known shortcoming:** ClickBench still pins a v0.9.53-nightly build from 2023-02; loses on c6a.4xlarge and on cold runs. Enterprise directories are Elastic-2.0 (mixed license).

**Known shortcoming:** ClickBench pins v0.9.53-nightly (2023-02); current v1.2.x was never tested vs DuckDB. Setups are unequal (the Databend daemon keeps caches across tries and the table is CLUSTER BY sorted, while DuckDB runs a fresh CLI per try on an unsorted table); the 1.75x geomean includes ClickBench's +10 ms shift. Open wrong-result/spill bugs (#20512, #20511, #20568); VACUUM, streams, MVs, masking and encryption are Elastic-2.0 licensed features; nightly-only releases, Linux binaries only.

**How:** Fuse storage prunes before reading. A snapshot points to segments, segments point to Parquet blocks, and multi-level min/max statistics prune segments and then blocks; per-block bloom indexes (xor8 by default, binary fuse32 as an option, from the xorf crate) skip blocks on equality predicates, and CLUSTER BY keys keep data sorted so range filters touch few blocks. Execution is a multi-threaded processor-graph pipeline (processors signal NeedData, NeedConsume, Sync or Async events to an executor), with GROUP BY and joins on a linear-probing hash table ported from ClickHouse's C++ implementation. On ClickBench the biggest gaps over DuckDB (5-9x on Q20-Q22 and Q28, 3-5x on the ORDER BY ... LIMIT queries Q24-Q27) are on point-lookup, LIKE and top-N queries, which fits pruning; that link is my inference. The heavy GROUP BY queries are close to even.

**Use it when:**
- You want a shared, multi-user SQL warehouse over S3/GCS/Azure, with storage separate from compute, rather than an in-process library.
- Repeated (hot) analytic queries on very large machines: ClickBench hot totals beat DuckDB ~1.6x on c7a.metal-48xl (192 vCPU) and c6a.metal.
- Selective queries on large fact tables: point lookups on high-cardinality columns (bloom index), tenant/date range filters that match a CLUSTER BY key, and top-N ORDER BY ... LIMIT.
- You need concurrent query serving from one process: ClickBench's concurrent test recorded 11.99 QPS over 10 connections with 0 errors (DuckDB's CLI entry skips this test).
- You want Snowflake-style features self-hosted: snapshot-based time travel, stages/COPY loading, and external Parquet/ORC/Iceberg/Paimon tables (the repo has storage crates for each).

**Skip it when:**
- Mid-size machines: on c6a.4xlarge (16 vCPU) Databend's hot total is 41.93s vs DuckDB's 26.25s, and 9 queries are more than 1.5x slower (for example the REGEXP_REPLACE query Q29: 11.9s vs 6.5s).
- Cold or first-touch queries: DuckDB wins the cold-run sums on every machine checked (162.8s vs 184.9s on c7a.metal-48xl, 115.2s vs 182.7s on c6a.4xlarge).
- Embedded analytics inside a C/C++/Rust app or notebook where DuckDB's library and extension ecosystem is the point. Databend only embeds via Python, and the full product needs two daemons.
- Joins or NOT IN subqueries that spill under memory pressure. Open bugs as of Sept 2026: #20512 (a spilling hash join fails once max_hash_join_spill_level >= 2), #20511 (NOT IN returns rows when a NULL is present and the mark join spills) and #20568 (duplicate rows from predicate pushdown into a RIGHT JOIN anti-join). There are 45 open C-bug issues.
- You need everything under an OSI license: VACUUM, streams, materialized views, data masking, row access policies, storage encryption, attach table and workload groups are enterprise features that need a license key and fall under the Elastic-2.0 code paths.

**Vs siblings:** Apache DataFusion shows the same ~1.6x over DuckDB on ClickBench c7a.metal-48xl, but it is an embeddable Apache-2.0 Rust library for building an engine. Pick Databend when you want a finished multi-user warehouse on object storage with time travel. For in-app embedding, DataFusion or chDB fit better, and Doris or StarRocks are the MPP-warehouse alternatives whose catalogued evidence is against ClickHouse, not DuckDB.

**Gotchas:**
- The ClickBench result comes from v0.9.53-nightly (Feb 2023), which ClickBench's install script pins. Current v1.2.9xx builds are not in that comparison, so today's numbers could be higher or lower.
- The benchmark setups differ. Databend is a long-lived server that keeps its in-process caches between the 3 tries, and its hits table is CLUSTER BY (CounterID, EventDate, UserID, EventTime, WatchID). DuckDB's entry starts a fresh `duckdb hits.db` process for every try (BENCH_RESTARTABLE=no), so its hot runs only get a warm OS page cache, and its table has no sort key. Against that, Databend's times include a curl HTTP round-trip.
- Releases are almost all -nightly tags (about daily). The last non-nightly release is v1.2.881 (2026-04-17), so pin exact versions.
- Changing bloom_index_type with ALTER TABLE affects only new writes, so old and new filter types coexist until the data is rewritten. binary_fuse32 is about 4x larger than xor8.

**Status:** Actively developed (default-branch commits daily, last push 2026-09-26, 9.45k stars) but shipped almost entirely as nightlies, and an Apache-2.0 core with Elastic-2.0 enterprise directories makes usability 'mixed'.

[repo](https://github.com/databendlabs/databend) · [benchmark](https://github.com/ClickHouse/ClickBench (data.generated.js: databend/results/20260926/c7a.metal-48xl.json vs duckdb/results/20260511/c7a.metal-48xl.json))

##### Firebolt Core  `C++`  `Elastic License 2.0`  `active`  `Tier B`

Firebolt's free self-hosted distributed SQL engine (ClickHouse-derived runtime); beats DuckDB on ClickBench hot runs, roughly ties ClickHouse.

**Beats:** DuckDB and ClickHouse via the ClickBench leaderboard (Firebolt wins vs DuckDB on hot runs; roughly ties ClickHouse hot and trails it cold and on Combined) — ClickBench's 43 queries, run on single AWS instances (c6a, c7a and Graviton4 c8g families) with the hits dataset ingested into a managed table (PRIMARY INDEX CounterID, EventDate, UserID, EventTime, WatchID) and result, subresult and scan caches disabled (2026-08-29 image engine:dev, compiler and flags undisclosed). Hot runs beat native DuckDB by about 1.6x (geomean) on c6a.4xlarge (hot sums 15.6 s vs 26.3 s; ClickHouse 18.0 s) and about 3-3.8x on metal-class machines. They roughly tie ClickHouse, while cold runs trail both, so the June 2025 '#1 on ClickBench' claim no longer holds.

**Known shortcoming:** '#1 on ClickBench' is a vendor June-2025 claim that no longer holds: hot runs are ~1.6-3.8x faster than DuckDB but cold runs 1.6-2.3x slower; about parity hot vs ClickHouse and behind it cold and combined. Closed ELv2 binary (ClickBench tags it a ClickHouse derivative).

**Known shortcoming:** SECURITY: the engine HTTP endpoint has no auth or TLS. Closed binary only (Docker image, ELv2, non-OSI; the repo holds deploy scripts and notices). A ~0.47 s/query cold floor (vs ClickHouse ~1 ms); on machines with 32 GB or less, ClickBench's concurrency test errors 30-57% (vs ClickHouse 0.1%) and 7-18 of 43 queries return no result on small instances. One write transaction per engine; a DoS fix (#59) left metadata broken. Needs Linux 6.1+ io_uring, seccomp=unconfined and 8 GiB memlock; releases are 'preview RC'; stats.elapsed understates by up to 3.6x; errors come back as HTTP 200.

**How:** Per Firebolt's CDMS 2022 paper ('Assembling a Query Engine From Spare Parts'), the runtime is a hard fork of ClickHouse's vectorized execution engine. The planner, forked from HPI's Hyrise, does cost-based join reordering, and a custom shuffle-based distributed executor replaced ClickHouse's distributed layer so that large-large joins and high-cardinality GROUP BYs scale out. Managed tables are immutable tablets sorted on a PRIMARY INDEX, with a sparse index of one mark per 8,192-row granule (found by binary search), per-tablet min/max statistics, min/max data-skipping indexes, Roaring-bitmap inverted indexes and aggregating indexes, and the scan refines a selection vector one predicate at a time so wide columns are decoded only for rows that survive. I/O goes through io_uring, and tablets are cached on local SSD with prefetching; none of this can be checked in source, because only the binary is published.

**Use it when:**
- Repeated, dashboard-style aggregations over one large fact table on a big-RAM machine where hot-cache latency matters: its ClickBench hot-run sum on c8g.metal-48xl is 2.66 s, vs 3.14 s for ClickHouse and 11.29 s for DuckDB.
- Queries that filter or join on a sort key, where the sparse primary index, data-skipping, inverted and aggregating indexes can prune most granules before any column data is read.
- You want one engine that runs as a single Docker container on a laptop and scales to a multi-node cluster with shuffle joins and distributed aggregations, all in a Postgres-style SQL dialect.
- Ad-hoc SQL over Parquet or Iceberg in S3/GCS (or S3-compatible stores such as MinIO or R2) without a separate load pipeline.
- Self-hosting inside your own product is acceptable under Elastic License 2.0, which bars only offering it as a competing hosted service.

**Skip it when:**
- Cold or first-touch latency matters: after a restart, each ClickBench query except Q1 took at least ~0.47 s (vs ~0.001 s minimum for ClickHouse and 0.04-0.09 s for DuckDB), which makes the cold geomean 1.6-2.3x slower than DuckDB's.
- Machines with 32 GB of RAM or less under concurrent load. In ClickBench's 10-connection concurrency test, 30% (c6a.4xlarge) and 57% (c8g.4xlarge) of queries errored, vs 0.1% for ClickHouse. 18 of 43 queries returned no result on c6a.large (4 GB) and 7 on c6a.xlarge (8 GB). The README recommends at least 16 GB.
- You need an embeddable in-process library (DuckDB, DataFusion), or you must build, audit, patch or vendor the engine: it is a closed binary under a non-OSI license.
- Write-concurrent workloads: only one write transaction can be active per engine at a time, and a second concurrent write returns an error.
- Networks you don't trust, or restricted hosts. The engine's HTTP endpoint has no built-in authentication or TLS, and a large-DDL bug (issue #59) left metadata unusable after the fix. It needs Linux 6.1+ io_uring, seccomp=unconfined and an 8 GiB memlock ulimit, and Docker Desktop for Mac 4.42.1-4.43.1 cannot run it.

**Vs siblings:** Pick it over Apache DataFusion or Databend when you want a ready-made scale-out server with a Postgres dialect and index-driven pruning, and closed source is acceptable. Its c7a.metal-48xl hot-run sum (3.11 s, 2026-08-29) is about a third of the catalogued DataFusion (9.78 s) and Databend (9.91 s) figures for that machine, though from different run dates. Choose DataFusion if you need Apache-licensed code you can embed or modify, and note that Umbra and ClickHouse still lead it on the ClickBench Combined score.

**Gotchas:**
- Errors come back as a JSON body with an 'errors' key, even with HTTP 200. During startup the port answers 'Cluster not yet healthy' at HTTP 200, so readiness checks must inspect the result body rather than the status code.
- The response's statistics.elapsed understates query time by up to 3.6x on high-core machines, because the trailing statistics chunk is sent tens of milliseconds after the rows. ClickBench measures client wall-clock time for this reason.
- ClickBench runs with enable_result_cache, enable_subresult_cache and enable_scan_cache set to false 'so timings are real'. Set these explicitly in your own benchmarks, or repeated queries may measure cache hits.
- The HTTP protocol is stateless: the current database and explicit transactions are carried by echoing the Firebolt-Update-Parameters / Firebolt-Remove-Parameters response headers back as query-string parameters, so naive clients silently lose that state.

**Status:** Actively maintained by Firebolt (repo commits through 2026-08-13; engine releases labelled 'preview release candidate', default tag :dev). Free to self-host under Elastic License 2.0, but the GitHub repo holds only deployment scripts, examples and license notices; the engine is a closed binary you cannot build, patch or vendor.

[repo](https://github.com/firebolt-db/firebolt-core) · [benchmark](https://benchmark.clickhouse.com/)

##### Umbra  `C++`  `proprietary`  `active`  `Tier B`

Closed-source TU Munich research SQL database (HyPer successor) that runs ClickBench about 2.4x faster than ClickHouse on one node.

**Beats:** ClickHouse — ClickBench's GitHub Actions automation ran the vendor's umbradb/umbra:26.09 image (submitted in PR #2066 by Umbra team member Tobias Schmidt) on one AWS c6a.4xlarge over the 100M-row hits table, untuned. Summing each query's best hot run over 43 queries gives 7.41s for Umbra, 18.03s for ClickHouse (2026-09-26, about 2.4x) and 26.25s for DuckDB (2026-05-11); cold sums are 47.3s vs 114.2s. ClickHouse wins only Q2 hot (1 ms vs 4 ms), and compiler and flags are unknown because only the binary is tested.

**Known shortcoming:** Closed-source binary (Docker 26.09), proprietary licence, no flags; ClickBench sums check out (7.41 vs ClickHouse 18.03 vs DuckDB 26.25 s; faster on 40/43 queries) but a concurrent-test error ratio of 0.547 is reported (verifier downgrade from A).

**Known shortcoming:** Evaluation-only licence ('not for production purposes'), closed-source binary. Fails on small machines (c6a.large 14/43 and t3a.small 17/43 queries fail with allocation errors, where ClickHouse runs all 43). ClickBench concurrency test (10 connections, 600 s): 54.7% of queries error on c6a.4xlarge and 58.8% on c8g.4xlarge, with no logged cause. The ClickBench maintainer found silent NULL rows for unimplemented functions, hard-coded memory settings, and a failed bulk load that left a partial table with fake-fast timings. Not a ClickHouse drop-in (Postgres wire protocol and dialect); arm64 images only since 26.01.

**How:** Umbra compiles each query into code organised around the data flow. It uses its own lightweight intermediate representation (IR), generates machine code directly so execution starts almost immediately (the 'Flying Start' backend, with 'FireARM' for AArch64), and hands only long-running pipeline steps to the LLVM optimizing compiler (adaptive compilation). Work is spread across cores with morsel-driven parallelism. Storage sits on a buffer manager derived from LeanStore with variable-size pages (64 KiB minimum, power-of-two size classes), pointer swizzling and optimistic versioned latches, and the CIDR 2020 paper measures its overhead at under 6% on average versus flat memory-mapped tables. Strings use 16-byte headers that store strings of 12 bytes or fewer inline and keep a 4-byte prefix for longer ones.

**Use it when:**
- Single-node ad-hoc analytical SQL over a wide table of about 100M rows (filtered counts, GROUP BY, COUNT(DISTINCT), LIKE '%x%' scans, top-N) when hot-query latency matters: on ClickBench it beats ClickHouse on 40 of 43 queries, often by 2-18x.
- Machines with plenty of RAM: on c6a.metal it completes all 43 queries with a 3.8s hot sum and no concurrent-test errors.
- Loading Parquet into a compressed table: ClickBench ingests the 14 GB hits.parquet through the umbra.parquetview table function in 163s and stores it in 8.3 GB with zstd (ClickHouse: 182s, 9.4 GB).
- Join-heavy analytical SQL: the CIDR 2020 paper reports geometric-mean speedups of 3.0x over HyPer and 4.6x over MonetDB on the Join Order Benchmark (2.3x over MonetDB on TPC-H SF10).
- Research or benchmarking where you want a state-of-the-art compiled engine as a reference point behind a PostgreSQL endpoint and running a Docker container is fine.

**Skip it when:**
- Production use: the license in the Docker image says the software is 'intended strictly for internal evaluation and review purposes and not for production purposes'. The commercial product from the same group is CedarDB.
- Small-memory machines: in the 2026-09-18 ClickBench run, 14 of 43 queries failed on c6a.large with 'ERROR: unable to allocate memory' (mostly COUNT(DISTINCT) and big GROUP BYs), and 17 failed on t3a.small. ClickHouse finished all 43 on c6a.large. Earlier 16 GB runs also failed during data load.
- Many concurrent clients on mid-size boxes: in ClickBench's 10-connection, 600-second test, 54.7% of attempted queries errored on c6a.4xlarge (58.8% on c8g.4xlarge; ClickHouse 0.1%). The log does not say why.
- Anything that needs source code, patches, audits, embedding in-process or a distributed or replicated cluster: it is a proprietary, binary-only, single-node server.
- ClickHouse-specific workloads: it speaks PostgreSQL SQL and wire protocol, not ClickHouse SQL, HTTP or native protocol, and has no MergeTree-style engines.

**Vs siblings:** Pick Umbra for the fastest single-node SQL engine behind a PostgreSQL endpoint when an evaluation-only, closed-source license is acceptable. Pick chDB (in-process ClickHouse for Python) or Bodo (compiled Python DataFrames) when you need open source, production use, or execution inside a Python process.

**Gotchas:**
- In May 2026 the ClickBench maintainer found that Umbra silently returns a NULL row for unimplemented functions (e.g. regexp_substr), with no error, so a query can look like a microsecond-fast success. The note was removed in the 26.09 update, and whether it was fixed is not documented.
- When memory ran out during bulk load, the load transaction errored partway through but the harness carried on, leaving a partial table that gave implausibly fast timings. Check row counts after loading.
- The ClickBench maintainer found memory settings hardcoded in the binary (shared_buffers 128MB, work_mem 4MB): 'SET work_mem' is rejected and ALTER SYSTEM is 'not implemented yet'. The only runtime knob in ClickBench's scripts is the ASYNCIO=0 environment variable.
- It needs raised container limits: Docker Hub's quick-start sets nofile=1048576 and memlock=8 GiB, and ClickBench runs it --privileged with unlimited memlock.

**Status:** Actively released, with roughly monthly Docker tags from 25.01 to 26.09 (pushed 2026-09-16). It is a research project whose license allows only internal evaluation, so use it as a reference point and look at CedarDB for a supported product.

[benchmark](https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.4xlarge.json (baselines in the same repo: clickhouse/results/20260926/c6a.4xlarge.json and duckdb/results/20260511/c6a.4xlarge.json))

#### embedded-kv

##### mpedb  `Rust`  `LicenseRef-mpedb-1.0 (custom source-available license: free except a one-time USD 0.07/device fee for organizations over $5B revenue/valuation)`  `active`  `Tier A`

Rust embedded SQL database (mmap'd copy-on-write B+tree, MVCC, sqlite3 C-API shim) that beats SQLite on in-process point operations.

**Beats:** SQLite — The author's mpedb-bench harness ran once on 2026-07-23 on an Apple M3 Pro (11 cores, macOS 26.6), built with rustc 1.96.0 --release, thin LTO and codegen-units=1. It measured mpedb 0.1.0 against bundled SQLite 3.45.0 through rusqlite 0.31 (STRICT table, prepare_cached) on a 50,000-row table. Warm PK point-select ran at 1.98M vs 320k ops/s non-durable (tmpfs; SQLite journal=MEMORY, sync=OFF) and 1.94M vs 762k durable (mpedb wal vs SQLite WAL, sync=FULL plus fullfsync), and point-insert at 231k vs 115k, with SQLite ahead on durable update, single-client durable insert and the deferred-fsync class. A same-day 2-core AMD EPYC-Milan Linux run shows point-select at 490k vs 80k.

**Known shortcoming:** The 'volume-backed' 490,310 vs 79,619 figure is a separate Linux EPYC run; SQLite wins some durable-mode cells; custom non-OSI license.

**Known shortcoming:** LICENSE: custom non-OSI terms charging $0.07 per device (counting server-connected devices, claimed retroactively), so not freely usable. The 6.2x headline is inflated (SQLite's 'none' class ran journal MEMORY + sync OFF, 2.4x slower than its own WAL; uneven arms); durable single-writer ties or loses on M3 and SQLite is 4.4x ahead in the deferred-fsync class; the bench is v0.1.0 while releases are at v0.3.1. File size is fixed at create (DbFull); a stalled reader can wedge writers; the SQLite shim covers ~50 of 300 functions with no-op hooks and unenforced READONLY; v0.3.x releases ship no assets; a single-author 'research project'.

**How:** SQL is compiled once into a content-hashed plan, so the hot path is execute(hash, params) with no parsing or statement lookup. Rows live in an LMDB-style copy-on-write B+tree inside a MAP_SHARED mmap'd file, with double-buffered meta pages. A read is an in-process walk over mapped pages under an MVCC snapshot, pinned in a lock-free reader table of packed {pid, seq} slots, so readers never take the writer lock. Writers enqueue into a shared-memory intent ring; whoever holds the single writer lock drains it in key-locality order and commits the batch with one meta flip and one flush (group commit). durability=wal appends lean records (only touched COW pages, with node free space elided) using one pwrite plus one fdatasync. The repo's own bisect credits the 1.26M to 1.98M ops/s point-select jump on the M3 to one plan-cache and parameter-resolution commit (7fb0d53).

**Use it when:**
- Several processes on one host (workers, CLI tools, notebooks) writing one local database file, where SQLite gives you SQLITE_BUSY and retry loops. The README's fork test (none-class, median of 3) shows 250-302k writes/s for mpedb vs 79-90k for SQLite WAL with a 60 s busy_timeout.
- Read-heavy primary-key lookups through prepared plans on a table that fits in the mapped file. M3: 1.98M vs 320k ops/s in the non-durable config and 1.94M vs 762k in the durable WAL config.
- Readers that must keep going while a writer is active. M3 commit-class: 2.41M vs 1.32M reads/s against SQLite WAL, with durable write rates about equal (345 vs 338/s).
- Batched durable writes with durability=wal: 29.7k vs 27.4k rows/s at 100 rows/commit on the M3, and the README reports a larger lead on Linux.
- Development and test: running an existing Django or CPython sqlite3 suite through the shim as a stricter 'second opinion' before deploying to PostgreSQL. This is the use the author recommends, rather than replacing SQLite.

**Skip it when:**
- Single-writer durable workloads. On the M3 it ties or loses: durable insert 328 vs 353 ops/s, update 300 vs 392, and deferred-fsync inserts (mpedb async vs SQLite synchronous=NORMAL) 19,720 vs 86,062, so SQLite is 4.4x faster there. The default-style durability=commit manages only 143 ops/s.
- Production or long-lived deployments. The author calls it a 'personal research project' and 'not production-hardened'. It has one author, 11 stars and no externally filed issues, and the author names the multi-process write path, where harnesses found a leak (#37), an atomicity hole (#119) and a shared-page corruption (#160), as the part to be sceptical about.
- Organizations that need OSI licensing or have more than $5B revenue or valuation. The custom license charges USD 0.07 per device, counted per device connecting to servers backed by it, with a five-year tail. It claims to apply retroactively to every prior version and says ambiguities resolve in the licensor's favour.
- Full libsqlite3 fidelity. Only about 50 of roughly 300 C functions are exported. Commit, update and authorizer hooks and tracing are silent no-ops, custom VFS (such as encryption) and loadable extensions are refused, SQLITE_OPEN_READONLY is not enforced, and writes to ATTACHed databases are refused. The pip module passed only 2/89 of sqlitedict's tests and 67/87 of diskcache's at 0.1.3, and PY-COMPAT.md lists an overlay INSERT OR REPLACE duplicate (#133) as a wrong answer.
- Windows, NFS or containers. On Windows the contended-insert cell is about 4x worse relative to SQLite than on Linux, with the cause unknown. Network filesystems are unsupported. Attaching from a different PID namespace is refused, and the platform table says nothing has run on Linux aarch64.

**Vs siblings:** Among the SQLite-baseline siblings (CalicoDB, ForestDB, ZoneTree, BTreePlus, DBX, CacheAdvance), pick mpedb when you want to keep SQL and existing libsqlite3/Python sqlite3 code while gaining multi-process writers and faster point reads. The others expose key-value or custom APIs, so adopting them means rewriting the data layer. Prefer them when a plain KV API is enough and you need a conventional license or a longer track record.

**Gotchas:**
- The file size is fixed at creation: it is fallocate'd from size_mb, the shim defaults are 64 MiB file-backed and 16 MiB in-memory, and it never grows. Exceeding it gives DbFull or SQLITE_FULL. A reader that is alive but stalled (SIGSTOP, debugger, a long scan) pins its snapshot and can eventually stall every writer with DbFull, because snapshot eviction is only half built.
- Pick durability deliberately. `commit` (msync data, then meta) costs two device flushes, and on macOS each is a full F_FULLFSYNC, so it runs at about half the speed of `wal`. The benchmark page calls `wal` the like-for-like comparand. The data file and its -wal sidecar must be copied together for snapshots.
- The benchmark arms are not symmetric. mpedb shares one handle across threads and uses execute(hash); the batched-insert cell uses the typed insert_row, bypassing SQL, while SQLite gets one connection per thread and prepared SQL. WAL auto-checkpoint is deferred out of the timed cells for both engines. SQLite's none-class mode is journal_mode=MEMORY with synchronous=OFF, a rollback-journal setup in which SQLite's own point-select is 2.4x slower than in its WAL setup. That inflates the 6.2x headline and produces the pathological 180 reads/s read-while-write cell, which the author labels as such.
- The README's prebuilt-shim install line points at releases/latest, but v0.3.0 and v0.3.1 have no assets attached and the filename says 0.2.1. v0.2.9 has no macOS build either, so on current releases you build the shim with cargo.

**Status:** Actively developed by a single author: the repo was created 2026-07-13, the last commit was 2026-08-28, and the latest release is v0.3.1 (2026-08-22, also on PyPI), not the 0.2.1 in the record. The benchmark measured 0.1.0 and has not been re-run on 0.3.x. The author describes it as a research project rather than production software, and it ships under a custom non-OSI source-available license.

[repo](https://github.com/punnerud/mpedb) · [benchmark](https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-macos-apple-m3-pro-11c.md)

##### BVLSM  `C++`  `no license`  `unknown`  `Tier B`

Research RocksDB variant that splits big values out at WAL-write time. Paper reports 7.6x RocksDB random-write throughput at 64KB.

**Beats:** RocksDB — The authors ran db_bench on a Xeon Gold 5218 with 128GB DDR4 and a Samsung 990 EVO NVMe (Ubuntu 20.04): 100GB of data, 16B keys, 4-64KB values, against RocksDB v9.7.3 and BlobDB 'configured identically' (configs not published). With 64KB random writes they report 7.6x RocksDB and 1.9x BlobDB with async WAL, about 7x and 3x with sync WAL, and up to 8x and 2x with WAL off. YCSB-A with 8KB values gives insert, update and read latencies of 27.2%, 28.4% and 19.7% of RocksDB's, and a 100GB sustained 4KB-value write test averages 1.5x RocksDB and 2x BlobDB. Compiler, flags and thread counts are not stated, and nobody else has reproduced the results.

**Known shortcoming:** The '7x/3x over RocksDB' was wrong: the 3x is against BlobDB with a synchronous WAL. IEEE HPCC 2025; no code.

**Known shortcoming:** Paper only: no code, license or repo (a GitHub 'bvlsmz' result is spam); 0 citations. No GC or space reclamation for BValue files; no scan, crash-recovery or space-amplification tests. The 7.6x headline comes from an async-WAL mode the design section never defines; sync mode does two syncs per Put.

**Known shortcoming:** Write-time key-value separation is not novel (legacy StackableDB BlobDB did it) and the paper does not discuss it. Internal contradictions (BVCache eviction policy, BlobDB read-latency percentages, MemTable counts). Datasets (~4 GB YCSB) are small against 128 GB RAM, so reads are likely page-cached. No compiler, flags or thread counts.

**How:** It moves WiscKey-style key-value separation from flush time, where BlobDB and WiscKey do it, to the write path before the WAL. MemTables then hold only pointers, so flushes are rarer, fewer WAL bytes are written, and compaction rewrites only keys plus pointers. That cuts write amplification and the L0-stall throughput dips seen in RocksDB. Separated values are spread by hash or round-robin across several BValue files, each meant to feed its own NVMe submission queue. The paper credits this for up to 40% more write throughput; its FIO microbenchmark (4 threads, 4KB) shows multi-queue 60.6% faster than single-queue. A BVCache (a fixed-size deque plus hash table, sized like one MemTable) keeps recently written entries to cut read latency on separated values.

**Use it when:**
- As a design reference if you maintain a RocksDB fork and want to separate values before the WAL rather than at flush.
- Ingest of values of 16-64KB and up (images, embeddings, large log chunks) on NVMe, where RocksDB throughput flattens above 32KB and L0 stalls make it oscillate. The paper's gains are largest at 32-64KB.
- Big-value writes that must use a synchronous WAL. Only pointer-sized records reach the WAL, and this is where the paper shows its largest relative gains: about 7x RocksDB on random writes and 4.1x on sequential writes.
- As an argument when you evaluate BlobDB or Titan: flush-time separation still buffers full values in MemTables and the WAL.

**Skip it when:**
- Any time you need running code. There is no public repository, license, build instructions or API, so you would have to reimplement it from an 8-page paper.
- Small values. Values under the threshold (example 4KB) stay inline and take RocksDB's normal path, and nothing below 4KB was benchmarked.
- Update- or delete-heavy or space-constrained workloads. The paper describes no garbage collection or space reclamation for BValue files and reports no space-amplification numbers. Integrated BlobDB and Titan both have GC.
- Range-scan or iterator-heavy reads. No scan benchmark is reported, and any separated value missing from the BVCache costs an extra random read from a BValue file.
- Anything with strict durability needs. No crash-recovery testing is reported. In WAL-disabled mode values sit in an in-memory buffer until a background thread writes them, and the paper does not say how those writes are ordered against MemTable flushes.

**Vs siblings:** For large values you can actually deploy, use Titan (Apache-2.0 RocksDB plugin, commits as recent as September 2026) or RocksDB's integrated BlobDB. KVell, PebblesDB, MatrixKV and SplinterDB also ship code. BVLSM is the only catalogued entry that separates values before the WAL, so read it only as a design reference when your values are 32KB or more and ingest is bound by the synchronous WAL.

**Gotchas:**
- The 7.6x headline comes from the async-WAL mode (R-WA), but the design section defines only two modes: WAL-enabled (value fsync'd to its BValue file, then the pointer record written synchronously to the WAL, so two syncs per Put with no group commit described) and WAL-disabled (values buffered and written by a background thread). How async-WAL mode behaves is not described.
- Write-time separation is not new inside RocksDB. The legacy StackableDB BlobDB wrote blob files synchronously in the write API. The RocksDB wiki says the integrated BlobDB moved to flush and compaction for consistency and large I/Os. The paper benchmarks only the integrated BlobDB and does not discuss the legacy one.
- The paper contradicts itself in places. BVCache eviction is described as Most-Recent-Write-First, as LRU tail eviction, and as time- or frequency-based 'depending on system load'. The text says BlobDB cuts read latency by 35.5%, but Fig. 8 shows BlobDB at 29.1us vs RocksDB's 82.1us, i.e. 35.4% of RocksDB. The setup lists '1 immutable and 5 mutable MemTables'. A '2.49x BlobDB' figure appears in the FIO-only section.
- The benchmark datasets are small relative to the host's 128GB RAM: 100GB for db_bench, and about 4GB for YCSB-A (500k x 8KB). So the YCSB read latencies were probably served largely from the page cache (my inference; the paper does not discuss caching).

**Status:** Paper only: arXiv v2 from June 2025, peer-reviewed at IEEE HPCC 2025 (pp. 34-41, doi:10.1109/HPCC67675.2025.00037). There is no code, repository or license (the only GitHub hit for 'bvlsm' is an unrelated spam repo), and OpenAlex shows zero citations as of 2026-09-26, so it is usable only as a design reference.

[benchmark](https://arxiv.org/abs/2506.04678)

#### indexes

##### LB+-Trees (persistent B+-Tree optimized for 3D XPoint memory)  `C++`  `no license`  `abandoned`  `Tier B`

Persistent B+-Tree for Intel Optane PM; 1.12-2.92x faster inserts than WB+-Tree and FP-Tree, similar lookups.

**Beats:** WB+-Tree and FP-Tree (state-of-the-art NVM-optimized persistent B+-trees) — On a dual-socket Cascade Lake-SP with 512GB Optane DC PM (fsdax, Linux 4.9.135), each tree was bulkloaded with 2 billion 8B/8B entries and then given 50K-300K random or monotonic inserts. LB+-Tree beat WB+-Tree and FP-Tree, implemented in the same framework, by 1.12-2.92x (up to 2.69x with 1-16 threads), with lookups and deletes on par; the paper gives no compiler or flags and the baseline code is not public. The independent VLDB'22 'Part Two' evaluation (Xeon Gold 6242R, GCC 11.1, PMDK) also found it the best performer in most cases, but only after its authors fixed persistence and added scans.

**Known shortcoming:** The Get/Put numbers are vs a divided skip list, not WB+-tree/FP-tree; search is on par; baseline source missing; abandoned since 2020-09. Requires 3D XPoint persistent memory.

**Known shortcoming:** Not a library: a benchmark executable with main(); API is bulkload/lookup/insert/del only (no scan, update or recovery). The RTM retry loop has no fallback and hangs if TSX is off (#1, #7); needs Optane with clwb. Read-uncommitted bug (#2) and signed-overflow search bug (PR #5) with fixes unmerged since 2021; no license ('TBD'); 8 B integer keys only. The independent VLDB'22 study confirms the best multi-threaded inserts (2.09x FPTree) but ~30% slower scans.

**How:** Entry moving: Optane write cost depends on how many 64B lines are written, not how many words change. So when an insert lands in a slot outside the header line, the code also moves entries out of line 0 into free slots in the target line. Later inserts then find a free slot next to the header and need only one clwb'd line (the paper derives at least 1.35x fewer line writes per insert in a stable tree). Logless leaf split: each leaf has two alternative sibling pointers and an alt bit, and one 8-byte NVM atomic write of the header word flips alt and the bitmap after the new node is persisted, so there is no write-ahead log as in WB+-Tree and FP-Tree. It also uses 256B nodes matching Optane's internal 256B access size, FP-Tree-style DRAM inner nodes, 14 one-byte fingerprints probed with a single SSE _mm_cmpeq_epi8, and Intel RTM transactions plus a per-leaf lock bit so that clwb/sfence run outside the transaction.

**Use it when:**
- Benchmarking or studying persistent B+-Trees on Intel Optane DC PM in App Direct/fsdax mode with 8-byte integer keys and 8-byte values or pointers
- Insert-heavy workloads with full leaves (frequent splits) or monotonic, hot-spot inserts such as time-ordered keys: this is where the paper shows 2.2-2.9x over WB+-Tree and FP-Tree
- Multi-threaded insert or update throughput on one socket: the independent VLDB'22 'Part Two' evaluation found its inserts scale best, 2.09x faster than FPTree and 1.55-3.07x faster than ROART, DPTree and PACTree
- As a strong baseline to beat in new PM-index work (APEX and the 'Part Two' evaluation both use it)

**Skip it when:**
- Anything in production: there is no license, no crash-recovery code, no range scan, a known read-uncommitted bug and no HTM fallback path
- Machines without Optane (discontinued) or without working Intel TSX/RTM plus clwb: TSX is off by default in Linux according to the author, and the code does not run correctly without it
- Scan-heavy workloads: the 14-entry 256B leaves made scans about 30% slower than FPTree single-threaded, and much worse multi-threaded, in the independent evaluation, and the repo has no scan anyway
- Variable-length or string keys: the repo only handles 8-byte keys, the paper's X-Engine/Memcached key-pointer variant is not published, and an independent test found pointer chasing dominates, with trie-based ROART winning
- Lookup-dominant or instant-restart needs: search only matches WB+-Tree and FP-Tree, APEX searches up to 3.9x faster, and restart must rebuild the DRAM inner nodes, whereas FAST+FAIR and APEX recover in under a second

**Vs siblings:** Pick LB+-Tree over FAST+FAIR or DPTree when multi-threaded insert or update throughput on Optane with DRAM inner nodes matters most and you can live with a rebuild at restart and a TSX dependency. Pick it over APEX when keys are hard for learned models to fit or splits are frequent: APEX was 5.8% slower on the FB dataset for inserts and 1.3x slower with intensive splits at 24 threads. For everything else APEX is faster (up to 2.7x inserts and 3.9x lookups) and FAST+FAIR recovers instantly.

**Gotchas:**
- If _xbegin() fails, the code just jumps back and retries with no bound and no lock fallback, so with TSX disabled every operation spins forever (issues #1 and #7). The author's fix is the boot options tsx=on tsx_async_abort=off mds=off, which also switch off the MDS mitigation.
- Two community fixes have been open and unmerged since 2021. PR #6 fixes read-uncommitted isolation by releasing the lock with a non-temporal store. PR #5 fixes a signed overflow in the inner-node binary search (r = key - p->k(m)) that UBSAN caught and that can misroute keys.
- LEAF_SIZE is hard-wired to 256B (#error otherwise), so the paper's multi-256B 'distributed headers' variant is not in the repo. The fptree-src and wbtree-src baselines are also missing (issue #4).
- A user reported that bulkload must run before inserts to initialise the tree. Issue #8 (unanswered) reports that the first store to each DAX page aborts RTM after a restart, and that recycled NVM nodes are neither zeroed nor persistently allocated.

**Status:** Abandoned: six commits on 2020-09-06, fix PRs open since 2021, no license file (the headers say 'LICENSE TBD'), and it is tied to discontinued Optane and TSX hardware, so treat it as a reference design to study rather than code to vendor.

[repo](https://github.com/schencoding/lbtree) · [benchmark](http://www.vldb.org/pvldb/vol13/p1078-liu.pdf)

#### probabilistic-filters

##### Adaptive Learned Bloom Filter (Ada-BF)  `Python`  `no license`  `abandoned`  `Tier B`

Research Python for learned Bloom filters that tune hashing per classifier-score band, cutting FPR versus standard and learned Bloom filters.

**Beats:** Bloom filter — This is a numerical FPR-versus-bitmap-size comparison, not a timing benchmark. On a 485,730-URL Kaggle set, with a random forest whose 146Kb pickle is added to the standard BF's budget, Ada-BF cut FPR by 81% versus LBF/sandwiched LBF at 500Kb (disjoint Ada-BF: 84%) and reached about 0.35% FPR in 300Kb where LBF needed over 500Kb. On VirusShare MD5 data it needed about 150Kb versus about 300Kb for LBF at 0.2% FPR, and all learned filters were over 98% below the standard BF. No hardware, compiler or runtime is reported; the only cost figure is hash operations per query in the NeurIPS version.

**Known shortcoming:** Gains are mostly over other learned Bloom filters and are in FPR/memory, not speed; abandoned since 2022-05.

**Known shortcoming:** Not a library: five argparse Python scripts with no API, persistence or license; bits stored as 64-bit numpy ints; hashing in Python loops. Queries cost more (classifier inference plus 9.40/12.07 hashes vs 3.39 for a Bloom filter at 400 Kb) and there is no timing benchmark.

**Known shortcoming:** README commands are partly broken (disjoint mode needs --model_path; PLBF 'query' KeyError, issue #1; model pickles absent); only the URL dataset runs (the malware CSV has the wrong label/column format) and it has 411,184 rows vs the paper's 485,730. Needs matplotlib <3.8. Unseeded hashes; the final FPR includes tuning negatives and the disjoint FPR denominator is wrong. Superseded: the PLBF paper reports 9x lower FPR than Ada-BF on URLs at 500 Kb.

**How:** The win is FPR per bit, not speed. The learned Bloom filter (Kraska et al. 2018) uses a single score threshold; Ada-BF generalizes this to g score regions with K_j hash functions, fixing K_j - K_{j+1} = 1 and a non-key ratio m_j/m_{j+1} = c so that only (K_max, c) need tuning, with the aim of equalizing expected false positives m_j * alpha^K_j across groups. Disjoint Ada-BF sizes each group's filter from R_j/n_j - R_1/n_1 = (j-1)log(c)/log(0.618). Queries cost more than a plain Bloom filter: the NeurIPS version reports 3.39 (BF), 6.98 (LBF), 9.40 (Ada-BF) and 12.07 (disjoint Ada-BF) hash operations per query at 400Kb, on top of one classifier inference.

**Use it when:**
- Reproducing or teaching learned-filter results: the repo has BF, LBF, Ada-BF, disjoint Ada-BF and PLBF implementations that run on the same URL CSV.
- A static key set, such as a URL blocklist or malware-hash list, where a small classifier's score separates members (high scores) from non-members (low scores) and bits stored or sent matter more than per-query CPU. The paper reports 40-50% less memory than an LBF at the same FPR.
- Prototyping the score-banding idea before porting it to a real filter implementation; each script is 80-250 lines of plain numpy/pandas.
- Distributing a filter to many servers where update size is the constraint (the NeurIPS fake-news experiment reports half the space of an LBF at equal FPR).

**Skip it when:**
- Any production or library use: there is no license, no API, and no persistence, every hash is a Python-level loop over sklearn's murmurhash3_32, and each bit is stored as a 64-bit numpy int.
- Latency-sensitive lookups: every query needs a classifier inference (a 10-tree random forest in the URL experiment) plus about 2.8x the hash operations of a plain Bloom filter at 400Kb, and no timing benchmark exists.
- Adversarial or drifting query streams: the FPR depends on non-key scores following the tuning distribution, and items above the top threshold are accepted without any hash check. The paper itself names adversarial examples and drift as weaknesses of learned filters.
- Weak classifiers, or when you want the best learned filter: the later PLBF paper (arXiv 2006.03176) reports 9x lower FPR than AdaBF on URLs at 500Kb, and AdaBF needs 2.5x PLBF's space at FPR 0.001; on EMBER, where the model helps less, the gap was only 1.1x.
- Dynamic sets: there are no deletes, and thresholds and filter sizes are tuned offline over the full key set, so changing the keys means retraining or re-scoring and rebuilding.

**Vs siblings:** Every sibling (Xor, BuRR, Prefix, Vacuum, Morton, and so on) is a key-agnostic filter with a fixed space overhead that needs no model; BuRR's table puts Xor/Xor+ at 14-23% over the information-theoretic minimum, versus the roughly 44% the Ada-BF paper cites for a standard Bloom filter. Pick Ada-BF only to study or prototype a learned filter when a classifier cleanly separates members from non-members and you count the model's bytes in the budget; for anything you ship over a static set, use Xor or BuRR.

**Gotchas:**
- The scripts run everything at top level (argparse, CSV load, a histogram with plt.show() that writes Score_Dist.png to the working directory), so they cannot be imported as modules, and plt.show() blocks on GUI backends.
- The README commands are partly broken. disjoint_Ada-BF.py requires --model_path, which the README omits, and it subtracts the model file size x8 from the budget while Ada-BF.py does not, so --size_of_Ada_BF means different things in the two scripts. PLBF.py reads a 'query' column that the shipped CSVs lack (open issue #1) and needs model pickles that are not in the repo.
- Datasets/Malware_data.csv has the columns label,score,md5 with labels 0/1, but every script selects label == -1 and a 'url' column, so only URL_data.csv runs as-is. Even that file has 411,184 rows (66,385 malicious), not the paper's 485,730, so reruns will not match the paper's figures exactly.
- Results are not reproducible run to run: hash seeds come from an unseeded randint and the 30% tuning sample is unseeded. The final FPR is measured on all negatives, including the tuning sample. Disjoint Ada-BF divides by only the below-threshold negatives, which overstates its printed FPR.

**Status:** Abandoned: the last code change was PLBF.py on 2022-05-24, the two 2021 issues were never answered, and with no LICENSE file the code is study-only (17 stars, 7 forks).

[repo](https://github.com/DAIZHENWEI/Ada-BF) · [benchmark](https://arxiv.org/abs/1910.09131)

##### ChainedFilter  `C++`  `no license`  `abandoned`  `Tier B`

SIGMOD'24 research code chaining approximate and exact filters for zero false positives on known negatives; beats RocksDB's Bloom P99.

**Beats:** Bloom filter — The 36% figure comes from the SIGMOD 2024 paper, not from runnable repo code. RocksDB was set up with all SSTables in L0 and a 64MB write buffer, with 36-byte keys, 64-byte values and 16M items (1.6GB, 30 SSTables). P99 latency for existing-key point lookups was about 31us with RocksDB's own Bloom filter at the same filter space and under 20us with ChainedFilter (RocksDB's Bloom filter plus an Othello whitelist), on an Intel i9-10980XE with 128GB DRAM and g++ 7.5.0 -O3. The repo's runnable experiments cover only the static dictionary, Huffman and Cuckoo-hash results, and none of them runs a Bloom baseline.

**Known shortcoming:** The RocksDB benchmark code isn't in the repo; no licence (reference only); abandoned since 2023-04.

**Known shortcoming:** No LICENSE; three commits in April 2023; reference code only. The RocksDB P99 code (Bloom + Othello) is not in the repo, so the 36% is paper-only. Zero false positives hold only for negatives known at build time; unknown keys still see the Bloom FPR, and Algorithm 1 is static (rebuild on change).

**Known shortcoming:** int32 keys only (the paper used 64-bit); reported bits ignore int[]/bool[] storage, so real RAM is far larger. UB (uninitialised 'upper' in Algorithm 2, a cuckoo function missing a return), leaks, non-inline header functions, duplicate ChainedFilter class; 'register' contradicts the README's C++17 claim and the Makefiles use c++11.

**How:** The paper's 'chain rule' shows that the space for exact membership factorizes as f(0,λ) = f(ε,λ) + f(0,ελ), so splitting the job into stages costs no extra space. Stage 1 is an approximate Bloomier (xor) filter with ⌊log2 λ⌋-bit fingerprints, built by hypergraph peeling with its 3 hash positions inside a window about 1/120 of the table (as in binary fuse filters), and stage 2 is a 1-bit exact Bloomier (retrieval) table that holds only the positives and stage 1's false positives and is probed only when stage 1 says yes. At λ=16 this gives 64% less space and 103% higher query throughput than a single exact Bloomier filter. The RocksDB gain is not a faster probe: each SSTable's filter (RocksDB's Bloom filter plus an Othello whitelist) is made exact with respect to keys in the later SSTables of the same level, so a lookup of an existing key reads at most one extra SSTable per level instead of up to N.

**Use it when:**
- Static exact membership or 1-bit retrieval over a closed universe, where every key that will ever be queried is known at build time and false positives are not acceptable (the paper's implicit static dictionary uses about 26% more space than the lower bound).
- LSM-trees with many overlapping sorted runs in one level (tiered compaction, or a large L0) where the P99 latency of existing-key point lookups matters. Treat the paper's design (Bloom stage 1, Othello stage 2 whitelisting keys from later SSTables) as a blueprint to implement yourself; this repo has no code for it.
- Cuckoo hash tables in slow or external memory: Algorithm 2, trained online, predicts which of the two tables holds each key. The paper reports 31% fewer external memory accesses at load 0.4 and zero mispredictions after 7 training rounds.
- Random-access decoding of Huffman-coded data, where the paper reports 0.22 extra bits per item over the lower bound.
- Studying the chain-rule construction before writing your own version on top of a maintained xor, binary-fuse or ribbon filter library.

**Skip it when:**
- As a general Bloom filter replacement when negatives are unknown. False positives on never-seen keys are only as good as stage 1, and in the paper's RocksDB test, latency for non-existing keys at 16M items still rises depending on which SSTable reports the false positive.
- Workloads with frequent inserts or deletes. Algorithm 1 is static and must be rebuilt, the paper says the chain rule does not hold for general dynamic membership, and the dynamic whitelist it suggests (Othello or Coloring Embedder) costs about 2.2-2.33 bits per item.
- Anything that ships. There is no LICENSE file (all rights reserved), the repo has 3 commits from April 2023, and there are no tests and no build system beyond per-folder Makefiles. The code also has leaks and undefined behavior (see gotchas).
- Keys that are not 32-bit ints, or large sets built on a tight memory budget. The code hashes only int keys, and a build keeps the full positive and negative arrays plus peeling scratch arrays in RAM; the paper notes peeling needs Ω(n log n) extra construction space.
- Range queries: ChainedFilter handles point lookups only.

**Vs siblings:** Choose ChainedFilter's design over Xor Filter or BuRR only when you know the negative keys at build time and need zero false positives on them, as in an exact static dictionary or the paper's trick of excluding keys that live in later SSTables. For ordinary approximate membership, Xor Filter and BuRR are licensed, usable libraries built on the same peeling/retrieval ideas, and SuRF is the RocksDB choice when you need range queries.

**Gotchas:**
- build() signals failure with negative return codes (-1 to -6), not exceptions, and retries peeling with only a fixed list of 10 seeds. The 'memory' it returns is a computed bit count (slots × fingerprint length), while the tables are stored as int[] (32 bits per slot), and Algorithm 2 stores bool[] (1 byte per bit), so real RAM use is far above the reported filter space.
- Undefined behavior: Algorithm 2's Layer never initializes its 'upper' pointer (or sum1) before 'upper==NULL' checks. In the Cuckoo experiment, CuckooHash::query_with_pre can fall off the end without returning, and query() reads an uninitialized variable.
- Leaks: ~ChainedFilter calls ~Bloomier() directly instead of delete, each seed retry allocates a new Encoder without freeing the old one, error paths leak their scratch arrays, and the experiment mains call ~ChainedFilter() by hand. The experiment mains also declare multi-GB static arrays (for example, three int[2^27] arrays in the Static Dictionary experiment).
- The headers define non-inline functions (MurmurHash32 is actually MurmurHash2, plus getp) and put 'using namespace std' at global scope, and both Algorithm1.h and Algorithm2.h declare 'class ChainedFilter'. You cannot include both in one translation unit, and including either from two .cpp files breaks the link. The faster interleaved variant, ChainedFilter_fast.h, ships but no main.cpp uses it, and the paper's experiments used 64-bit keys while the repo code hashes 32-bit ints.

**Status:** Abandoned after three commits in April 2023, with no license file. Treat it as a reference for reading the paper, not code you can vendor, and note that the RocksDB integration was never published.

[repo](https://github.com/ChainedFilter/ChainedFilter) · [benchmark](https://arxiv.org/abs/2308.13632)

##### Partitioned Learned Bloom Filter (PLBF)  `Python`  `no license`  `abandoned`  `Tier B`

Python solver for Partitioned Learned Bloom Filter parameters; the resulting design uses less space than Bloom, sandwiched LBF, Ada-BF.

**Beats:** Bloom filter — ICLR 2021 paper (arXiv 2006.03176v2, Section 4.1), Python simulations with an sklearn random-forest model counted at its pickle size, k=5, N=1000, and an idealized 'optimal' backup filter (standard Bloom size / log2 e) for every learned variant. At 400/500/3000 Kb on synthetic/URLs/EMBER, PLBF had 22x/26x/3x lower FPR than sandwiched LBF and 8.5x/9x/1.9x lower than Ada-BF; to reach FPR 0.001, sandwiched LBF needed 8.8x/3.3x/1.2x and Ada-BF 6x/2.5x/1.1x PLBF's space. There are no compiler, hardware or query-latency numbers, and the comparison against a standard Bloom filter appears only as a plot (Appendix E.1, Fig. 4).

**Known shortcoming:** The repo is only the algorithm file with no license (all rights reserved); abandoned since 2022-06. Venue is ICLR 2021.

**Known shortcoming:** The repo is only a parameter solver (thresholds and per-region FPR) with no filter or query code; importing it runs a demo. Well-separated scores (the strong-model case PLBF targets) crash with a math domain error (log 0). It implements Algorithm 2 with <=100 chunks while the paper benchmarked Algorithm 3 with N=1000. Gains are space vs learned variants, no latency numbers; CLBF reports PLBF reject is 14.6x on average (up to 65x) slower. atsukisato/FastPLBF (MIT) is a runnable alternative.

**How:** The gain is in space, not speed. With boundaries fixed, the KKT conditions give each region's optimal FPR as f_i = F * g_i / h_i (the region's share of keys divided by its share of non-key queries), and the space saved against a plain Bloom filter works out to c * |S| * KL(g||h) minus the model size. So the thresholds come from a dynamic program over a discretized score axis that maximizes the KL divergence between region-level key and non-key distributions (O(N^2 k)). Algorithm 1 then caps any f_i >= 1 at 1 (no filter in that region) and re-solves the rest; the paper finds that 4-6 regions are enough.

**Use it when:**
- Static key sets that come with predictive features and a classifier that separates keys from non-keys well, such as malicious-URL or malware blocklists. The large paper wins (3.3x-8.8x less space than sandwiched LBF at FPR 0.001) came from models with F1 of 0.97-0.99.
- You have a representative sample of non-key queries (for example, historical query logs). The solver estimates the non-key score distribution from it, and the target FPR holds only in expectation over that distribution.
- Filter size is the binding constraint (for example, a blocklist shipped to clients or edge nodes) and each query can afford a model inference.
- You already run a sandwiched or Ada-BF-style learned filter and want principled thresholds and per-region FPRs instead of heuristics. The solver is about 200 lines of plain Python and easy to port.
- Studying the algorithm: this is the authors' own reference code for Algorithm 1 and the KL-divergence DP.

**Skip it when:**
- Keys with no learnable signal (random IDs, bare hashes). The model adds bytes without adding divergence. Even EMBER, with a model at F1 0.85, needed only 1.1x-1.2x less space than the learned baselines at FPR 0.001.
- Latency-sensitive query paths. Every query pays for model inference (a random forest in the paper) plus a filter probe, and the paper reports no query-time numbers. The CLBF paper (arXiv 2502.03696v2) measures PLBF reject time at about 14.6x slower on average, and up to 65x slower, than its cascaded design.
- Dynamic sets or query distributions that drift. Any change means retraining the model and re-solving, there is no insert or delete path, and queries aimed at high-score regions can push the FPR above target.
- Production use of this repo as-is. It has no license and no filter implementation, and it crashes (ValueError: math domain error) when any score chunk contains no keys, which happens with exactly the well-separated models PLBF is meant for. For runnable code, use atsukisato/FastPLBF (MIT).
- Workloads that want a plain, fast, model-free AMQ in C/C++. Xor filters sit only 14-23% above the space lower bound (figures from the catalog's BuRR entry), and ribbon filters sit lower still, all without a model.

**Vs siblings:** Over Ada-BF: same learned-filter setup, but PLBF picks thresholds and FPRs by optimization and needed 1.1x-6x less space at FPR 0.001 in the paper. Over CLBF: only when you want the simpler PLBF formulation and query latency does not matter, since CLBF reports up to 17% less memory and much faster rejects than PLBF. For key sets with no learnable signal, Xor Filter or BuRR is the better pick, and for working PLBF code start from FastPLBF rather than this solver.

**Gotchas:**
- Importing plbf_algo runs the module-level demo: it generates about 200k normal samples, solves for K=5 at FPR 0.1 and prints the result. Strip the bottom block before importing it as a library.
- Crashes on well-separated scores: the DP calls math.log(delta_G/delta_H), so a score chunk with zero keys raises ValueError and a chunk with zero non-keys divides by zero. Reproduced here with keys in [0.8,1] and non-keys in [0,0.3], and again with Gaussians at 0.9/0.1 and 0.1/0.1. FastPLBF's DP guards both cases.
- Not the benchmarked algorithm. The repo runs Algorithm 2 (relaxed-DP thresholds, then the Algorithm 1 fix-up) over at most 100 quantile chunks. Paper Section 4.1 used Algorithm 3 (search over the last region's boundary, O(N^3 k)) with N=1000, which the Fast PLBF paper says takes over 3 minutes at k=5. Expect results somewhat off the paper's curves.
- Inputs must be Python lists of scores in [0,1]; with numpy arrays, key_scores+non_key_scores would add elementwise instead of concatenating. Several regions can come back with FPR 1 (the demo returns [..., 1, 1]); those regions accept everything and should be merged. The README's 'ICLR 2020' is wrong: the paper appeared at ICLR 2021.

**Status:** Abandoned: six commits, all on 2022-06-29, 7 stars, zero issues, no license, and the experiment code was never released. Treat it as an algorithm reference and use the MIT-licensed atsukisato/FastPLBF (NeurIPS 2023; its PLBF class builds real backup Bloom filters) as the runnable base.

[repo](https://github.com/kapilvaidya24/PLBF) · [benchmark](https://arxiv.org/abs/2006.03176)

## Unverified claims (tier C/D)

### crypto-and-hashing

#### aead-and-ciphers

##### HiAE (High-throughput Authenticated Encryption)  `C`  `no license`  `active`  `Tier C`

Reference C code for HiAE, Huawei's AES-round AEAD; 2-6.6x OpenSSL AES-256-GCM on 16 KB messages on recent x86/ARM.

**Beats:** OpenSSL AES-256-GCM — The comparison comes from the designers' non-peer-reviewed ePrint 2025/377, Table 10. It measures single-core AEAD encryption at 16 KB with 48-byte AD, built with -O3 and GCC 11.4 on the x86 machines. HiAE reached 340.02 Gbps against 51.90 for OpenSSL 3.0 AES-256-GCM on a Ryzen 9 7950X (about 6.6x), 253.19 vs 38.80 on an EPYC 9334, and 171.46 vs 36.49 on a Xeon W9-3495X. The GCM baseline swings widely (114.07 Gbps on an i7-11700, where HiAE's lead falls to about 2.2x), decryption was not measured, phones used a hand-written AES instead of OpenSSL, and the repo's harness times only HiAE.

**Known shortcoming:** ePrint preprint only; the harness times HiAE alone (no OpenSSL code in the repo), so ratios against AES-GCM are derived from separately reported numbers. The repo has no license; hiae-aead/libhiae is an MIT-licensed alternative implementation. New 2025 design with little cryptanalysis yet.

**Known shortcoming:** Designer's preprint measures encryption only; libhiae shows decryption ~35-45% slower. At 64 bytes OpenSSL AES-GCM beats HiAE on every CPU in the paper's Table 10, and AEGIS-128L beats it on all 7 x86 CPUs. Reference HiAE_AEAD_decrypt releases plaintext without checking the tag (RUP setting), where ePrint 2025/1180 (ToSC 2026) gives key recovery. Init changed Oct/Nov 2025, so current ciphertexts differ from the paper version; no runtime ISA dispatch; individual Internet-Draft only, not CFRG-adopted.

**How:** HiAE is an NFSR-style stream cipher with a 2048-bit state (16 x 128-bit blocks). Each 16-byte block costs two AES rounds plus a few XORs, arranged in an 'XAXX' shape (AESL(a xor b) xor c xor d). That shape matches x86 aesenc and fuses well with ARM aese+aesmc, so neither ISA pays the extra XOR that aesenc-shaped designs such as AEGIS and Rocca pay on ARM. The keystream tap position was picked to leave four dependency-free rounds of parallelism during decryption. The code unrolls 16 state updates, so the shifting state costs no index arithmetic. On x86 with VAES and AVX-512 it switches to inline assembly that keeps all 16 state blocks in xmm0-xmm15 and uses xmm16-31 for message and ciphertext blocks. The paper says this is why older CPUs, where aesenc can only use xmm0-15, fall behind.

**Use it when:**
- Point-to-point links where you control both endpoints and messages are 1 KB or larger, on CPUs with VAES and AVX-512 (Ice Lake, Sapphire Rapids, Zen 4). In the designers' Table 10 at 16 KB AEAD, HiAE runs at 340.02 Gbps against 51.90 for OpenSSL 3.0 AES-256-GCM on a Ryzen 9 7950X, and 195.02 against 43.85 on a Xeon Gold 6326.
- ARMv8/v9 servers and laptops with crypto extensions, where the gain over other AES-based AEADs is largest. On Kunpeng 920 at 16 KB, HiAE does 53.72 Gbps, against 23.11 for AEGIS-128L and 14.66 for OpenSSL AES-256-GCM. On Apple M3 Pro it does 189.19, against 70.95 for GCM.
- Reproducing or extending the ePrint 2025/377 measurements on your own hardware. make benchmark times encryption-only, AEAD and MAC-only runs at 16 B to 16 KB.
- Designs that want a 256-bit key-recovery target with a 128-bit tag and can guarantee unique nonces and verify-before-release decryption.

**Skip it when:**
- Interoperating with TLS, IPsec, QUIC or any existing protocol. HiAE has no RFC. Its specification is an individual Internet-Draft (draft-pham-cfrg-hiae-06, May 2026) that CFRG has not adopted.
- Small messages. At 64 B, OpenSSL AES-256-GCM beats HiAE on every CPU in Table 10 where OpenSSL was used (7950X 18.35 vs 12.12 Gbps, M3 Pro 28.05 vs 9.72), and AEGIS-128L beats it on all seven x86 chips. On Kunpeng 920 and 920X, GCM still wins at 256 B. The fixed 32-round initialization and 32-round finalization dominate short messages.
- x86 without VAES (Cascade Lake, Haswell). Rocca is faster there: 156.60 vs 133.19 Gbps on a Xeon Gold 6242R and 75.97 vs 63.90 on a Xeon E5-2620 v3, both at 16 KB AEAD.
- Any setting where a nonce might repeat, unverified plaintext might be released, or an attacker can submit many forged decryptions. ePrint 2025/1180 (a minor revision of a ToSC 2026 paper) recovers the full 256-bit key with 2^128 data and at most 2^129 time using nonce-respecting decryption queries, and with only a small constant number of repeated nonces or unverified decryptions. The designers' rebuttal (2025/1235) says these settings are outside HiAE's model.
- Decrypt-heavy workloads or shipping this repo. The paper benchmarks encryption only, while libhiae's own numbers show decryption about 35-45% slower (Zen 4 at 16 KB: 129.71 vs 222.32 Gbps). This repo also has no LICENSE file.

**Vs siblings:** Use HiAE over Rocca, Rocca-S and AEGIS-128L for bulk (1 KB and up) traffic on ARM or VAES-capable x86, where Table 10 shows it ahead. Stay with Rocca on pre-VAES Xeons, with AEGIS-128L or AES-GCM for messages of 256 B or less, and with libaegis (RFC-published AEGIS, including the wider AEGIS-128X variants the HiAE paper never measured) when you need a standardized, licensed library. To deploy HiAE itself, take the MIT-licensed hiae-aead/libhiae rather than this repo. intel-ipsec-mb and SNOW-V-GCM target different needs: standard IPsec algorithms and a 5G-style stream cipher.

**Gotchas:**
- HiAE_AEAD_decrypt never checks the tag. It writes the plaintext, then overwrites the caller's tag buffer with the computed tag and always returns 0. The caller has to save the received tag first, compare the two in constant time, and wipe the plaintext on mismatch. As written, the API is the release-of-unverified-plaintext setting in which 2025/1180 recovers the key. libhiae's HiAE_decrypt does verify and returns non-zero on failure.
- The algorithm changed after the paper. The October and November 2025 commits changed how key and nonce are loaded during initialization, and a July 2025 fix made finalization encode lengths in bits. Ciphertexts and tags from older checkouts will not match the current draft test vectors. The round count is the same, so throughput should be unaffected.
- Building with -march=native on a VAES/AVX-512 machine emits EVEX instructions that fault on older x86 CPUs, and there is no CPUID check. Build per target, or use libhiae, which dispatches at run time.
- Every HiAE_stream_encrypt, HiAE_stream_decrypt and HiAE_stream_proc_ad call pads its own trailing partial block. When streaming, every chunk except the last must therefore be a multiple of 16 bytes. The header does not document this; it follows from the code.

**Status:** This is a 21-star designer reference repo, last changed 2025-11-11 to match the updated initialization and IETF test vectors. It has no LICENSE file, so it is study-only. For real use, take the MIT-licensed hiae-aead/libhiae (59 stars, pushed 2026-09-20), which adds runtime dispatch, tag verification and a portable fallback.

[repo](https://github.com/Concyclics/HiAE) · [benchmark](https://eprint.iacr.org/2025/377.pdf)

#### encoding

##### Faster CRC32 on Apple M1 (dougallj, PMULL multi-chain)  `C++`  `no license`  `abandoned`  `Tier C`

Single-file C++17 AArch64 CRC-32/CRC-32C kernel with 12 PMULL folding chains; about 2.5x zlib's crc32 on Apple M1.

**Beats:** zlib crc32() function — On a 3.2 GHz Apple M1 the author measured zlib's crc32 (a separate, unpublished test of Apple's system zlib, version unknown) at about 30 GB/s; the companion 12-chain gist reached about 70-75 GB/s on a 2 MiB buffer (clang++ -std=c++17 -O3), and this cleaner template/asm version about 76 GB/s. corsix/fast-crc32 independently measured this gist at 77.55 GB/s on M1 (512 KiB default buffer) against 25.03 GB/s for Chromium zlib's scalar code and 26.57 GB/s for its vector code, but only 17.41 GB/s on Ampere Altra, where the Chromium scalar code wins at 22.68 GB/s.

**Known shortcoming:** A gist, not a library: Apple M1 only (PMULL multi-chain), untouched since 2022-06-06. ~76 GB/s is this gist's own figure (70/75 GB/s from an earlier test gist); zlib is not in the harness, so the ~2.3x over zlib is derived. clang++ -O3.

**Known shortcoming:** No license. Builds only with Apple clang as published (corsix had to add <cstring> and -flax-vector-conversions). Loses on Ampere Altra (17.41 vs 22.68 GB/s); inputs under 192 bytes take a serial path. Superseded by corsix/fast-crc32 (~85 GB/s on M1).

**Independent measurement:** corsix/fast-crc32 independent run: 77.55 GB/s on M1 vs Chromium zlib 25-27 GB/s; Ampere Altra 17.41 vs 22.68 GB/s.

**How:** It uses Intel's 2009 carry-less-multiply folding ("Fast CRC Computation for Generic Polynomials Using PCLMULQDQ") ported to ARM PMULL/PMULL2, but with 12 independent 16-byte accumulators (192 bytes per iteration) instead of the usual 4. The chain count is sized to M1 Firestorm's latency: the Apple core fuses PMULL/PMULL2 with a following EOR into one 3-cycle uop, so each chain costs 6 cycles and 2 fused uops, and 12 chains fill the 4-per-cycle SIMD pipes. The fold step is inline asm to keep valid fusion pairs. The final 128-to-32-bit reduction uses two CRC32X/CRC32CX instructions, or a Barrett reduction for other polynomials.

**Use it when:**
- Bulk CRC-32 or CRC-32C over large buffers (the author profiled 128 KB and up; the test harness uses 2 MiB) on Apple M-series cores, where the checksum is the throughput bottleneck, e.g. zip/PNG/gzip writers or storage checksums on macOS/iOS.
- Studying or porting the N-chain PMULL+EOR folding technique: about 270 readable lines, with the constants derived by constexpr code rather than magic numbers.
- Arbitrary reflected 32-bit CRC polynomials on AArch64: pass the polynomial as a template parameter (NO_CRC_INSNS builds without the ARMv8 CRC instructions, using a table plus Barrett reduction).

**Skip it when:**
- Non-Apple ARM cores. The PMULL+EOR fusion it depends on is, per the author, probably unique to Apple CPUs. corsix/fast-crc32 measured it at 17.41 GB/s on Ampere Altra, slower than Chromium zlib's scalar CRC32X loop at 22.68 GB/s.
- x86 or any non-AArch64 target: there is no fallback path, since it includes arm_neon.h and uses PMULL inline asm unconditionally.
- Small or latency-sensitive buffers. Below 192 bytes (after 16-byte alignment) it drops to a single serial CRC32X chain, and the author warns its 5 ops per 16 bytes (vs 3 for CRC32X) can hurt when the checksum shares the core with other work.
- Shipping code that needs a clear license. The gist carries only an 'AS IS' warranty disclaimer and no license grant.
- When you want the fastest M1 result: the author's 2024 update points to corsix/fast-crc32 at 85.05 GB/s vs 77.55 GB/s for this gist.

**Vs siblings:** corsix/fast-crc32 is the direct successor: it ships explicit license files, is about 10% faster on M1 (85.05 vs 77.55 GB/s by blending EOR3 and CRC32X) and covers x86 and non-Apple ARM, while crc-fast and crc32fast are packaged libraries. Pick this gist only as a compact, readable C++17 reference for 12-chain PMULL+EOR folding; for shipping code use corsix/fast-crc32.

**Gotchas:**
- It does not build as-is outside Apple clang. corsix/fast-crc32's vendored copy had to rewrite the asm to standard syntax (`pmull v0.1q, %[val].1d, %[consts].1d`), add the missing `#include <cstring>` for memcpy, add an extern "C" wrapper, and compile with `-march=armv8-a+crypto+crc -flax-vector-conversions` under g++ on Linux.
- Speed depends on fusion pairs, i.e. each PMULL immediately followed by its dependent EOR. The author reports about 70 GB/s without them and about 75 GB/s with them; the inline asm pins this order, so do not 'clean it up' into intrinsics without re-measuring.
- The final fold from 12 accumulators to one is serial (about 72 cycles, per the author's TODO), a fixed cost per call on top of the small-buffer fallback.
- This gist has no test or harness of its own. The companion gist's harness checks only one 2 MiB buffer against a slice-by-4 table, but corsix's bench.c (which checks every length from 1 to 4,160 bytes and every split point against a table CRC) runs this code before benchmarking it.

**Status:** Abandoned: last edited 2022-06-06, and the author's 2024 blog update names corsix/fast-crc32 as the new state of the art. With no license grant it is a reference implementation, not code to vendor.

[repo](https://gist.github.com/dougallj/263f132023f590aec31a11bbc746b897) · [benchmark](https://dougallj.wordpress.com/2022/05/22/faster-crc32-on-the-apple-m1/)

#### signatures-kem

##### GOLF: GPU-accelerated Optimization for Lattice-based FALCON  `CUDA`  `no license`  `unknown`  `Tier C`

CUDA batch port of Falcon-512 signing and verification, one signature per GPU thread; 70x/369x the reference's published CPU throughput.

**Beats:** Falcon reference implementation throughput as published on falcon-sign.info (Intel Core i5-8259U @ 2.3 GHz, TurboBoost off), cited as Fouque et al. (Ref) in Table II and not re-run by the authors; also prior CPU/GPU Falcon papers — On an RTX 4090 (CUDA 12.1, sm_89, -maxrregcount=127, 128x512 threads), GOLF measures 420,250 sign/s and 10,311,039 verify/s for Falcon, with parameters implied to be 512 by the baseline. That baseline (5,948.1 sign/s, 27,933.0 verify/s) was copied from falcon-sign.info for the reference implementation on an i5-8259U at 2.3 GHz with TurboBoost off and compiler flags not given, so 70.65x/369.13x compares a GPU batch against one CPU. On an A100 GOLF reaches 157,995 sign/s and 4,180,879 verify/s, which is 2.69x/1.53x over Lee et al.'s published A100 figures (not re-run).

**Known shortcoming:** No public code. GPU vs CPU comparison: the 58.05x/73.14x ratios are against Nguyen et al. on an Apple M1, and the 70.65x/369.13x ratios against the reference use numbers copied from falcon-sign.info (i5-8259U, flags unknown). The ePrint page shows signing as 42.02 kops/s; the PDF says 420.25.

**Known shortcoming:** Paper never names the parameter set (baseline is falcon-sign.info's Falcon-512 row) and its ratios are inconsistent (abstract 58x/73x vs Apple M1; 70.65x/369.13x vs reference; intro 387.84x). Batch latency ~156 ms. Side channels argued away, not measured. The possibly related russdrh/FP-GOLF repo (no license) reuses one salt across threads and its benchmark clones one key/message 65,536 times and checks only thread 0.

**Independent measurement:** IEEE TIFS 2025: signing 420.25 kops/s; vs Nguyen et al. (M1) 58.05x/73.14x; vs reference 70.65x/369.13x.

**How:** The main gain is coarse-grained parallelism: one thread per signature, 128 blocks x 512 threads (65,536 signatures per launch), with -maxrregcount=127 so that 512 threads fit in a block. A 2-threads-per-signature fine-grained variant that swaps data with __shfl_sync reached only 177,027 sig/s, against 361,726 for coarse-grained. Kernel fusion avoids repeated launches and global-memory round trips, and the recursive ffSampling is rewritten as an explicit stack-frame loop (Lee et al.'s method) so that NVCC will compile it. Finally, the FFT/iFFT butterfly units run in depth-first rather than layer-by-layer (breadth-first) order to shorten data reuse distance. This added 14.51% signing throughput (361,726 to 414,216 sig/s at 128x512) and, per Nsight, cut L2-to-DRAM traffic by 18%.

**Use it when:**
- Cloud or server backends that queue tens of thousands of Falcon-512 signatures at a time, where aggregate ops/s matters and roughly 156 ms of batch latency is acceptable (RTX 4090 figure).
- Bulk Falcon-512 verification, e.g. checking large signature sets. Verification shows the largest gain (10.3M verify/s on an RTX 4090, about 6.4 ms batch latency) and needs no secret material on the GPU.
- You are building your own GPU Falcon and want proven, simple tricks: one thread per signature, a stack-frame iterative ffSampling, and depth-first butterfly ordering for FFT/iFFT cache locality.
- You need published RTX 4090 and A100 throughput numbers to size GPU capacity for Falcon against Lee et al.'s earlier GPU work.

**Skip it when:**
- Single-signature or latency-bound signing. Each 65,536-signature batch takes about 156 ms on an RTX 4090 (415 ms on an A100), while the CPU reference produces one Falcon-512 signature in about 0.17 ms (5,948 sign/s on an i5-8259U).
- You need usable, licensed code. The paper links none. The candidate repo russdrh/FP-GOLF has no license, 0 stars and a single benchmark/KAT driver, and has per-thread indexing bugs (see gotchas).
- Falcon-1024 or FIPS 206 FN-DSA interoperability. The paper never names a parameter set (its baseline row is Falcon-512), cites the 2018 NIST submission, and FP-GOLF hard-codes logn=9 (Falcon-512).
- Shared or multi-tenant GPUs with side-channel concerns. The paper argues GPU global-memory side channels are 'not practical' rather than measuring leakage, and does not analyze the floating-point Gaussian sampler's timing on GPU.
- Tight GPU memory. The FP-GOLF tree mode allocates 7,169 doubles (about 56 KB) of expanded key per thread, about 3.8 GB for its 65,536-thread batch, plus a 36 KB per-thread scratch union.

**Vs siblings:** Pick GOLF over VecFalcon only when you have a CUDA GPU and large batches and need Falcon throughput far beyond a CPU core. VecFalcon (CPU SIMD, 1.13-1.59x faster signing, released code) is the practical choice for per-signature latency or deployable code. GRASP is the matching GPU batch design for SPHINCS+ and also ships no code; if you need working GPU Falcon code today, Lee et al.'s benlwk/Falcon-Mitaka (GPL-3.0, Falcon-512), the prior work GOLF benchmarks against, is released.

**Gotchas:**
- Headline ratios are easy to misread. The abstract's 58.05x/73.14x is against Nguyen et al.'s Apple M1 NEON code, not the reference. Against the reference (falcon-sign.info) the gain is 70.65x/369.13x, though the introduction says 387.84x. The ePrint web abstract prints 42.02 kops/s where the PDF says 420.25 kops/s.
- Throughput depends heavily on batch size. Across nine grid/block configurations from 16,384 to 65,536 threads, the best signing throughput is 2.93x the worst (1.47x for verification). Keys are generated ahead of time and shipped to the GPU in bulk, and the paper does not say whether host-device copies are inside the timed region.
- In FP-GOLF, the sign kernels read the 40-byte nonce (salt) with no per-thread offset, so every thread in a batch hashes and emits the same host-supplied salt. They also memmove thread 0's message into every signed-message output. Falcon (the paper's Algorithm 1) needs a fresh uniform salt per signature.
- The FP-GOLF benchmark copies one key, one message, one seed and one nonce into all 65,536 slots, checks only thread 0's signature against the CPU result, and times kernel launch plus cudaDeviceSynchronize only. Its grid is 256x256, not the paper's 128x512.

**Status:** This is a peer-reviewed reference design (IEEE TIFS vol. 20, pp. 9441-9453, 2025; ePrint revised 2025-08-15) with no linked code, license or maintenance. The first author's russdrh/FP-GOLF (3 commits on 2026-05-25, 0 stars, no license) contains the paper's depth-first FFT/iFFT loops (logm/loghm counters) and stack-based ffSampling, so it is probably related. It is unconfirmed as the paper's artifact and not usable as-is.

[benchmark](https://eprint.iacr.org/2025/749)

##### GRASP: GPU-based paRallel Accelerated SPHINCS+  `CUDA`  `no license`  `unknown`  `Tier C`

Single-kernel CUDA SPHINCS+-SHA256-f-simple batch signer/verifier; 1.37-3.45x over Kim et al.'s GPU code, 1,820-3,659x the single-core reference.

**Beats:** NIST PQC SPHINCS+ reference C code (version 3.0), SHA-256 simple fast parameter sets, run by the authors on a single core of an AMD Ryzen 5 5600G; also the open-source GPU SPHINCS+ of Kim et al. (re-run on the same GPU) plus prior GPU/FPGA works — On an RTX 4090, timing kernels only (host-device copies excluded, averaged over 1,000 runs, NVCC version and flags unstated), GRASP signs 146,363 / 82,621 / 40,489 and verifies 1,499,590 / 933,696 / 886,362 SPHINCS+-SHA256-128f/192f/256f-simple signatures per second. That is 3,114-3,659x (signing) and 1,820-2,029x (verification) the NIST reference C code v3.0 on one Ryzen 5 5600G core. The like-for-like result is 1.37-1.79x signing and 1.53-3.45x verification over Kim et al.'s open-source GPU code re-run on the same RTX 4090.

**Known shortcoming:** No public code. The >1000x ratios compare an RTX 4090 against one Ryzen 5 5600G core running the NIST SPHINCS+ reference; the headline numbers exclude memcpy, and NVCC/CPU flags are not given. Against other GPU code (Kim et al., re-run on the same RTX 4090) the gain is 1.37-3.45x.

**Known shortcoming:** Only SHA256-f-simple is measured; including memcpy, level-1 signing drops from 146k to 118k/s. Needs a 128x512 launch grid (128x64 reaches 45% of peak). Level-3 verify figure differs between text (1,408,846) and table (933,696). Baseline is the portable reference v3.0 on one core, with no optimized CPU build compared. SLH-DSA (FIPS 205) compatibility not documented.

**Independent measurement:** IEEE TC 2026: signing 3659x/3178x/3115x, verifying 2029x/1898x/1820x vs SPHINCS+ ref v3.0 (1 core); 1.37-3.45x vs Kim et al. GPU.

**How:** Kernel fusion runs FORS, WOTS+ and the MSS hypertree in a single CUDA kernel. This avoids the global-memory hand-offs of Kim et al.'s multi-kernel design. The thread-team size is chosen so that both the hypertree layer count d and the FORS tree count k divide evenly (gcd(22,33)=11), with one thread per layer or subtree, so no threads sit idle during node merging. When the root of the layer below is already known, WOTS+ signing is folded into that leaf's public-key chain computation, which removes about 33% of the hash calls for those leaves and cuts separate WOTS+ signings from d to t per thread. The n-byte hash blocks move with 16-byte int4 loads and stores at levels 1 and 5, and with int2 at level 3, where 24-byte blocks would misalign.

**Use it when:**
- High-volume SPHINCS+ signing on a data-center GPU (e.g. a code- or firmware-signing farm) that accepts SHA-256 fast-simple parameters: 146,363 / 82,621 / 40,489 signatures/s at levels 1/3/5 on an RTX 4090.
- Mass verification of SPHINCS+-SHA256-f signatures: 1.5M/s at level 1 on an RTX 4090, one thread per signature.
- A GPU signer that needs per-signature latency: the low-latency mode signs in 0.512 ms at level 1 (25 ms for the CPU reference, 4.8 ms for Kim et al.), at the cost of dropping to 19,521 ops/s.
- Reference techniques for your own GPU or CPU hash-based signer. Kernel fusion, gcd-sized thread teams and merging WOTS+ signing into leaf keygen are all described in enough detail to reimplement, and the paper says the WOTS+ merge also helps CPU code.

**Skip it when:**
- You need code. None was released and there is no license. The only open GPU SPHINCS+ code found is Kim et al.'s kindongsy/TCAS-SPHINCSp_GPU, which is unlicensed and consists of per-security-level Visual Studio projects.
- You need SHAKE, Haraka, 'robust' or small (s) parameter sets. Only SHA-256 fast-simple was measured; the claim that it is 'equally effective in all modes' is asserted, not benchmarked.
- You need FIPS 205 SLH-DSA compliance. The work targets SPHINCS+ round 3 (reference code v3.0), and compatibility with the final SLH-DSA standard is not documented.
- Small batches in the throughput mode. The peak needs a 128x512 grid; at 128x64, level-1 signing drops to 66.4 kops/s, 45% of the peak.
- Sizing end-to-end PCIe throughput from the headline. It excludes host-device copies: with memcpy, RTX 4090 level-1 signing falls from 146,363 to 117,723 ops/s, and with-memcpy verification numbers are not reported.

**Vs siblings:** Pick GRASP when you are committed to hash-based SPHINCS+ signatures and need GPU batch throughput. GOLF is the same group's GPU design for Falcon; it reaches 420k sign/s on the same RTX 4090 with 666-byte Falcon-512 signatures versus 17,088 bytes for SPHINCS+-128f, and it also ships no code. The CPU siblings (VecFalcon, ENG25519, UltrafastSecp256k1) release code and suit per-signature latency on CPUs.

**Gotchas:**
- Level-3 verification is reported inconsistently: the text says 1,408,846 ops/s, while Table VI and Fig. 13 say 933,696 (933.7 kops/s). The table value drives the 1897.76x and 1.80x ratios.
- The 1,820-3,659x ratios are against the portable reference C code on one Ryzen 5 5600G core with unstated flags (40/26/13 sign/s, 739/492/487 verify/s). No optimized CPU SPHINCS+ implementation was compared.
- The gap over Kim et al. shrinks with apples-to-apples conditions: 1.37/1.79/1.58x kernel-only on an RTX 4090 (Kim's open-source code re-run), 1.36/1.65/1.49x with memcpy, and 1.22/1.25/1.30x on an RTX 3090 against Kim's published with-memcpy figures.
- The low-latency and high-throughput modes are separate thread configurations. Low-latency gives 5.5x lower throughput than Kim et al. on the RTX 4090, so pick one per deployment.

**Status:** This is unreleased research code from a peer-reviewed paper (IEEE TC vol. 75 no. 4, pp. 1579-1592, 2026; ePrint revised 2025-01-16) with no repo, license or maintenance, so treat it as a technique reference only. Both the ePrint and the journal version are titled 'GRASP: Accelerating Hash-based PQC Performance on GPU Parallel Architecture'; the catalog name is the expanded acronym.

[benchmark](https://eprint.iacr.org/2024/1030)

##### moduletto (NEON i16 ML-KEM-512)  `Rust`  `PolyForm-Noncommercial-1.0.0`  `active`  `Tier C`

Rust modular-arithmetic/NTT crate whose NEON ML-KEM-512 example edges out liboqs 0.16.0 on Apple M5 (~1.18x).

**Beats:** liboqs 0.16.0 (ML-KEM-512, built from source at tag 0.16.0, Release, -O3 -march=native, on aarch64/Apple M5) — On an Apple M5 (macOS 25.5), the author's 10,000-iteration example times its NEON i16 ML-KEM-512 at 4.07/3.84/5.80 us (keygen/encaps/decaps, about 13.7-14.1 us per session), built with the Cargo release profile (LTO, codegen-units = 1) and an unstated rustc. That is compared with liboqs 0.16.0 built from source (-O3 -march=native) at 16.19 us, about 1.18x. The liboqs number comes from an unpublished C harness and is hardcoded in the example, so the comparison is first-party and not reproducible from the repo.

**Known shortcoming:** liboqs and Kyber-ref times are hard-coded constants in examples/kyber_benchmark.rs, measured by a C harness that is not in the repo; rustc version not stated (retiered A to C). The '2.96x' is Kyber-ref vs liboqs, not moduletto (moduletto vs Kyber-ref is ~3.4-3.5x, derived). The KEM lives in an example, not the library; FIPS 203 conformant only since 2026-08-11. PolyForm-Noncommercial license: reference use only. NEON (aarch64) only.

**Known shortcoming:** Security bug (found in enrichment, by code reading): the decapsulation mask `!(a^b).wrapping_neg()` evaluates to (a^b)-1 rather than 0x00/0xFF in all three backends, so a ciphertext differing in one byte can leak real-key bits into the implicit-rejection output; ACVP vectors did not catch it and it is not reported upstream. Do not use for real keys. No API (KEM lives in an example), not on crates.io, no zeroize or RNG. Library NTT converts i64/i16 on every call; the x86 i64 path is ~2x slower than liboqs.

**How:** A pq-crystals-style int16 Montgomery NTT (R = 2^16, QINV = -3327) runs eight butterflies per NEON instruction (vmull_s16 / vmovn_s32 / vshrn_n_s32). The two narrow layers (len 4 and 2) are vectorised with uzp/zip deinterleaving, and lazy reduction plus a branchless rounding Barrett step removes per-layer reductions. Most of the session-level gain came from outside the NTT: grouped bit-packing codecs (43.6 to 27.7 us); a two-lane Keccak-f1600 that uses ARMv8.2 FEAT_SHA3 (EOR3/RAX1/XAR/BCAX) to pair independent SHAKE streams, with right-sized squeezing (to 16.1 us); and dropping round-3 Kyber's final KDF during the FIPS 203 fix (to 13.9 us).

**Use it when:**
- Studying how a Rust ML-KEM-512 reaches liboqs-level speed on Apple Silicon: int16 NEON NTT, uzp/zip narrow layers, two-lane FEAT_SHA3 Keccak
- Non-commercial research or benchmarking on aarch64 with FEAT_SHA3 (Apple M-series), where the ~13.9 us session figure was measured
- Needing a small no_std-capable NTT/ModN arithmetic crate for q = 3329 experiments, with Coq proofs of the Barrett and constant-time primitives and fuzz targets
- Porting ideas (grouped codecs, streaming rejection sampler, paired Keccak lanes) into a permissively licensed ML-KEM implementation you write yourself

**Skip it when:**
- Any commercial product: PolyForm Noncommercial 1.0.0 forbids commercial use without a separate license
- Production key exchange: the KEM is benchmark example code with no public KEM API, no RNG integration, no zeroization, no independent review, and the decapsulation mask defect listed under gotchas
- x86-64 or other non-aarch64 targets: the NTT falls back to a portable i64 kernel and the i64 KEM backends measured 34.7-36.8 us on the M5, about 2x slower than liboqs
- ML-KEM-768/1024: only the 512 parameter set (k = 2) is implemented
- Needing a published package: the crate is not on crates.io (the README's moduletto = "0.1" snippet will not resolve), so it has to be a git dependency

**Vs siblings:** Among the catalogued KEM/signature entries, this is the only ML-KEM one that times against liboqs on Apple Silicon NEON. sntrup is a usable, MIT/Apache crate for a different KEM (NTRU Prime) with a reproducible liboqs harness, and the Plantard-NTT paper targets formally verified NTTs compared against pq-crystals reference C. Pick moduletto only to learn aarch64 ML-KEM-512 optimisation techniques under a non-commercial license.

**Gotchas:**
- Decapsulation's constant-time equality mask is wrong in all three backends of the example (eq &= !(a ^ b).wrapping_neg() computes (a^b)-1 per byte, not 0x00/0xFF). A ciphertext whose only byte difference from the re-encryption is 0x02 yields mask 0x01, so the output mixes bits of the real key K' into the implicit-rejection key. The ACVP VAL vectors did not catch this. This is from reading the source; not reported upstream as of this review.
- The library's NEON NTT takes and returns [ModN<3329>; 256] (i64 per coefficient) and converts to and from i16 on every call (about 30 ns each way, per the source comment), so building a KEM on the public API will not reach the example's numbers
- Until 2026-08-11 the code implemented round-3 Kyber with a hardcoded zero implicit-rejection seed and eta1 = 2. The 2026-03-19 tables and the Platform Notes in BENCHMARKS.md describe that older, non-conformant code
- The LibOQS (16.19 / 20.43 us) and Kyber-ref (47.87 us) figures are hardcoded constants printed by the example. Running it re-times only moduletto

**Status:** One developer, 11 commits (the burst of 2026-08-11 changes delivered the FIPS 203 fixes and the speedups, and the last commit was 2026-09-03), no issues filed, not on crates.io, and noncommercial-licensed, so treat it as reference code to read, not a dependency.

[repo](https://github.com/crabnebula-dev/moduletto) · [benchmark](https://github.com/crabnebula-dev/moduletto/blob/main/BENCHMARKS.md)

### networking-and-servers

#### event-loops-io

##### exec-rs  `Rust`  `no license`  `active`  `Tier C`

Rust port of C++ P2300 senders/receivers with a mio event loop; its single-threaded echo server beats Tokio 10-26% (self-reported).

**Beats:** Tokio — The top-level README table compares a single-threaded exec_echo (mio loop) with Tokio's multi-thread runtime at worker_threads(1). Results were 114,723 vs 104,601 req/s (50 connections), 130,694 vs 114,478 (200), 135,157 vs 107,333 (500) and 100,321 vs 85,745 (4 KB), which is +10% to +26%. benchmark.sh shows the load came from haraldh/rust_echo_bench on 127.0.0.1: one blocking client thread per connection, 128 B messages, 10 s, with 'Large' being 100 connections of 4096 B. No CPU, OS, rustc version or run count is given. The script launches a nonexistent 'exec_echo_async' example, and the example directory's own README (Linux 5.15) reports only +4-7% single-threaded and parity at 4 threads.

**Known shortcoming:** Contradicted inside the repo: the top README claims 10-26% over Tokio, but examples/echo_server/README.md (Linux 5.15) reports +4-7% single-threaded and near-identical at 4 threads (3,714k vs 3,703k req/s). Not like-for-like: Tokio runs the multi-thread scheduler with worker_threads(1) and write_all, while exec-rs does one write and drops partial writes. benchmark.sh (rust_echo_bench, loopback, 128 B) gives no CPU, OS, rustc or run count and launches a nonexistent example. The README's exec-rs = "0.1" pulls an unrelated crates.io crate; this project is unpublished and Cargo.toml's repository points elsewhere. No LICENSE or CI; 'vibe coding' rewrite in 2026-01, idle since. Code bugs: spurious wakeups return WouldBlock and end accept loops or connections; one pending operation per socket (concurrent read and write overwrite each other); closed sockets never removed; spawn leaks the operation; heavy unsafe Send/Sync over RefCell. Unix TCP only; the 'work-stealing' pool is a single shared channel.

**How:** The echo result comes from a small single-threaded reactor. IoContext::run_one polls mio (epoll/kqueue) and runs readiness callbacks inline on the same thread, so the hot path has no work-stealing scheduler, task wakers or cross-thread handoff. Each read or write is tried directly on the non-blocking socket first. Only on WouldBlock does it store a boxed completion in a per-token HashMap. repeat_effect_until keeps each iteration's operation state inline and uses a thread-local trampoline to bound recursion. The Tokio baseline is not a current_thread runtime: it is Tokio's multi-thread scheduler with worker_threads(1), with the accept loop running inside block_on.

**Use it when:**
- Studying or prototyping P2300/stdexec-style sender pipelines in Rust: then/let_value/when_all/bulk, stop tokens, and async scopes.
- Research on how the sender/receiver design compares with Future-based runtimes on allocations and scheduling overhead, since operation states are exposed and kept inline.
- A single-threaded, Unix-only TCP request/response loop with trivial per-connection work, where you will re-run the echo benchmark on your own hardware before trusting the gap.
- Reading material for porting C++ std::execution code (stdexec, uring_exec) to Rust or comparing the two.

**Skip it when:**
- Production services. There is no LICENSE file, CI or issue history, the repo has 30 commits and 0 forks, and the author's commit messages describe the January 2026 rewrite as 'Brand new version with vibe coding'.
- Multi-core servers. IoContext is single-threaded, and the repo's own examples/echo_server/README.md reports Tokio and exec-rs as 'nearly identical' at 4 threads (3,714k vs 3,703k at 500 connections).
- Anything beyond plain TCP: there is no TLS, UDP, DNS, file I/O or I/O-integrated timers, and no ecosystem (hyper, tonic, reqwest). Nested when_all and the merge/transform_each sequence senders are listed as incomplete.
- Windows. Sockets are registered with the poller only under cfg(unix).
- async/await codebases. Handlers become nested closures that clone Arcs: the exec echo example is 105 lines against 51 for the Tokio one.

**Vs siblings:** Pick exec-rs only if you want P2300 sender/receiver semantics in Rust specifically; uring_exec is the more serious C++ equivalent (P2300-style over io_uring). If you just need to beat Tokio, monoio (thread-per-core io_uring, about 1.86x Tokio at 4 cores in its own benchmark) and ringline are far more complete.

**Gotchas:**
- The README's `exec-rs = "0.1"` resolves on crates.io to an unrelated crate (robinfriedli/exec-rs, task-execution utilities, versions 0.1.0-0.2.0). Use a git dependency instead. Cargo.toml's repository field also points to the wrong place (github.com/yuchao/exec-rs).
- I/O senders make one non-blocking syscall per readiness event. A spurious wakeup completes with a WouldBlock error instead of retrying, and repeat_effect/repeat_effect_until stop on error, so one spurious wakeup can end the accept loop or a connection.
- async_send_from does a single write and the echo example ignores the byte count, so partial writes are silently dropped (Tokio's echo uses write_all). IoContext keeps one pending op per socket token, so a concurrent read and write on one socket overwrite each other.
- Resource handling is loose. TcpStream has no Drop impl and deregister_socket is never called in the net module, so socket-map entries build up per connection. IoContext::spawn deliberately leaks the operation ('For now, we leak it'). The README calls StaticThreadPool work-stealing, but it is one shared crossbeam bounded channel.

**Status:** The last commit was 2026-01-31, about 8 months ago, so 'active' is generous. The current code is a January 2026 rewrite. README and Cargo.toml say Apache-2.0 but the repo has no LICENSE file, so read it for reference and do not take it as a dependency.

[repo](https://github.com/npuichigo/exec-rs) · [benchmark](https://github.com/npuichigo/exec-rs#benchmark-results)

##### F-Stack  `C`  `BSD-2-Clause for F-Stack's main code, per the LICENSE file (GitHub reports 'Other'/NOASSERTION). Bundled components: DPDK BSD-3-Clause (kernel modules GPL-2.0), FreeBSD stack BSD-4-Clause, Nginx BSD-2-Clause, Redis BSD-3-Clause, libplebnet/libuinet BSD-2-Clause, inih BSD-3-Clause, Microthread framework GPL-2.0.`  `active`  `Tier C`

DPDK kernel-bypass framework with a ported FreeBSD TCP/IP stack and epoll/kqueue-style API; beats kernel-stack epoll Nginx on RPS/CPS.

**Beats:** epoll — Tencent's README charts compare Nginx on the Linux 3.10 kernel stack (epoll) with Nginx+F-Stack on a Xeon E5-2670 v3 and an Intel XL710 40GbE NIC (CentOS 7.2; compiler and load generator not stated). F-Stack shows ~12x CPS/RPS over untuned kernel Nginx, but only ~1.46x RPS over IRQ-tuned Nginx (keep-alive, 24 cores) and ~2.3x CPS over reuseport Nginx (16 cores, different environment), and 3.7 KB-body bandwidth ties at 40GbE line rate. Values are read from chart images. A separate Photon wiki test (single thread, 25G NIC, 512 B messages) shows +20% ping-pong and +40% streaming over Linux 6.x kernel sockets.

**Known shortcoming:** The ~12x headline is against untuned kernel Nginx; against the best-tuned kernel setup it is about 1.46x RPS and 2.3x CPS, and both hit the 40GbE limit at 3.7 KB. Numbers are read off the project's own charts; no compiler, flags, load generator or scripts published. The '10M concurrent connections' claim has no data, and the architecture doc's '25x vs kernel 200K RPS' contradicts the README. Needs DPDK and dedicated NICs; bundles BSD-4-Clause and GPL-2.0 parts.

**Known shortcoming:** Worst case is single-connection and low-concurrency workloads: users measured it slower than Linux sockets (#774: 672 MB/s vs 1.88 GB/s; #758 in VMs). Exhausting the mbuf pool hangs the whole stack (#1076; safeguard off by default). ff_epoll_wait ignores its timeout and EPOLLET is emulated. Docs lag the code (FreeBSD 15.0 stack, DPDK 24.11); no ABI stability for ff_config.

**How:** Kernel bypass: DPDK poll-mode drivers pull packets straight from NIC rings into hugepage mbufs on a busy-polling core, removing interrupts, syscalls, kernel copies and scheduler wakeups. Each lcore runs its own process (or thread with thread_mode=1) holding its own stack instance and RSS queue, so nothing is shared, and the port strips the FreeBSD stack's locks, kernel threads and scheduler. TX is batched (pkt_tx_delay holds up to 100 us while fewer than 32 packets are queued), and optional zero-copy send/receive (ff_zc_send/ff_zc_recv) skips socket-buffer copies.

**Use it when:**
- Dedicated front-end servers that open and close many short TCP connections (HTTP with Connection: close, L4/L7 proxies, TCP DNS), where kernel accept/teardown and softirq cost is the limit. The README shows ~2.3x CPS over reuseport-tuned kernel Nginx at 16 cores.
- Keep-alive serving of small requests over many connections spread across many cores: ~1.46x RPS over IRQ-affinity-tuned kernel Nginx at 24 cores on a 40GbE XL710.
- You already run Nginx or Redis and can switch to the bundled patched versions (Nginx 1.28.0, Redis 6.2.6) instead of rewriting code.
- You own the hardware: a NIC with a DPDK driver (Intel XL710/82599 and Mellanox ConnectX-5 appear in project reports, virtio in VMs) that you can give up entirely, plus hugepages and spare cores to pin at 100% busy-poll.
- Porting a C epoll/kqueue event loop where each core owning its own connections is a natural fit.

**Skip it when:**
- Single-connection or low-concurrency workloads. The maintainer calls a single TCP echo/stream F-Stack's worst case, and users measured it slower than Linux sockets (#774: 672 MB/s vs 1.88 GB/s for one-way 4 KB writes on the same host; #758: 350-400 vs 450-500 Mb/s in VMs).
- Bulk transfer that already saturates the NIC: with a 3.7 KB body both stacks reach ~37 Gbit/s on 40GbE at 16 cores, so there is no gain at line rate.
- Shared or general-purpose hosts, or containers without NIC passthrough. The data NIC disappears from Linux, so kernel tools and firewalls no longer see it, and without a separate management port even SSH needs the KNI/virtio exception path.
- Low-rate, latency-sensitive RPC on default settings: pkt_tx_delay=100 us and delayed ACK add latency to each round trip, and idle_sleep=0 burns a full core per lcore even when idle.
- macOS or Windows, or teams that cannot run as root, disable ASLR (required for multi-process mode) and operate DPDK in production.

**Vs siblings:** Pick F-Stack over mTCP, IX or Arrakis when you want an actively maintained kernel-bypass TCP stack that is in production at Tencent Cloud, with the full FreeBSD TCP feature set and ready-made Nginx/Redis ports, rather than a paper-era research system. Pick Seastar instead if you are writing a new C++ service and accept its framework. If you must keep the Linux stack and a shared NIC, io_uring options (Asio's io_uring backend, monoio, Condy) give ~1.2-1.9x with far less operational burden.

**Gotchas:**
- ff_epoll_wait ignores its timeout argument and always returns at once, because ff_run is the real loop. EPOLLET is emulated with kqueue EV_CLEAR, which the source says is not exactly the same. Sockets must be set non-blocking with ff_ioctl(FIONBIO), or ff_write can misbehave.
- Overload fails hard: when connections exhaust the mbuf pool, the whole stack becomes unresponsive, ff_* tools included (#1076). An opt-in mbuf_low_watermark SYN-drop exists but is off by default, so cap kern.ipc.maxsockets to what the mbuf pool can hold.
- Defaults are tuned for high concurrency (pkt_tx_delay=100 us, net.inet.tcp.delayed_ack=1); maintainers tell single-connection users to lower both. The patched Nginx requires user root, sendfile off, use kqueue and worker_processes equal to the lcore count, and reload drops service for about 1 s unless graceful_reload=1.
- No ABI stability: a change to struct ff_config's layout made a helloworld built against the old lib segfault, so rebuild apps on every lib update. The docs lag the code: the README says FreeBSD 11.01/13.0, but dev ships a FreeBSD 15.0 stack (__FreeBSD_version 1500068) that measured 2-6% slower than 13.0 on Nginx short connections.

**Status:** Actively developed by Tencent Cloud: dev commits run through 2026-09-18, the last tagged release is v1.25 (2025-11), and dev is VERSION 2.0 on FreeBSD 15.0 and DPDK 24.11.6. The core is BSD-2-Clause, but the bundled BSD-4-Clause FreeBSD code and the GPL-2.0 kernel modules and micro-thread framework need license review.

[repo](https://github.com/F-Stack/f-stack) · [benchmark](https://github.com/F-Stack/f-stack#nginx-testing-result)

##### io_uring hybrid storage I/O architecture (Oracle Database)  `C`  `no license`  `active`  `Tier C`

Design paper: Oracle Database swaps libaio for io_uring on batched async paths; 29% less CPU per write, sync reads unchanged.

**Beats:** libaio (Linux AIO) — The end-to-end runs used an OCI bare-metal AMD EPYC 7J13 (96 vCPUs given to the database, 8 NVMe SSDs in RAID-0, Oracle Linux UEK R8), an internal Oracle Database 26ai build and a libaio baseline, each reported as the vendor's unaudited mean of 3 runs. Switching to io_uring raised DBWR-isolated write IOPS from 1.07M to 1.43M with 29% less CPU per write, cut CPU per direct-path read by 19% at equal throughput and TPC-H CPU per query by 8.5% (geomean), and left TPC-C tpmC unchanged. The database's compiler and flags are not stated; the separate single-NVMe microbenchmarks (gcc -O2, CPU not stated) show -39% CPU per I/O for batched io_uring against batched libaio, as a geomean over 24 block-size x device-count cells.

**Known shortcoming:** Closed-source Oracle Database 26ai with a custom io_uring layer (bypasses liburing); only a microbenchmark artifact is public. First-party preprint, not peer-reviewed; TPC runs unaudited. Gains are CPU efficiency only (TPC-H elapsed time unchanged) and the TPC-C saving needs background writers cut from 32 to 23. Best read as evidence for io_uring over libaio.

**Known shortcoming:** Cross-process buffer cloning as described likely fails on current kernels: since Linux 6.14 io_clone_buffers requires the same mm (-EINVAL), and since 2025-09 a SINGLE_ISSUER source owned by another task gives -EEXIST; the paper does not explain how its separate processes pass these checks. The '270x' shared-registration result is not measured: the artifact calls register opcode 27 (IORING_REGISTER_NAPI in mainline), ignores the return value, and times ring creation only. Figure 2 compares depth-1 libaio against batched io_uring; Figure 3 (-39%) is the fair comparison. No public code for the write path, Table 3 or Table 8; artifact sources may not compile against recent headers; no LICENSE file. Nothing reusable ships: best treated as evidence for io_uring/liburing.

**How:** Syscall amortization: one io_uring_enter submits a batch of 32-4096 I/Os, and completions are reaped by peeking the shared completion queue in user space, where libaio needs io_submit plus io_getevents. Registered (pre-pinned) buffers remove the per-I/O get_user_pages cost, and Table 7 credits them with almost all of the CPU saving (3.66 to 2.58 us per I/O, -29.5%); ring-fd and file-fd registration add only about 1.4%. Each process owns a private ring with IORING_SETUP_SINGLE_ISSUER and io-wq capped at one worker, because a mutex-shared ring collapsed to 23K IOPS at 128 threads. IOPOLL and SQPOLL were rejected: IOPOLL cost 385 us of CPU per I/O at 128 threads, and SQPOLL threads sit outside the database's cgroup CPU accounting.

**Use it when:**
- You maintain a multi-process or multi-threaded storage engine on Linux NVMe whose background writers or scan workers already submit deep libaio batches (32+ I/Os) and poll for completions. That is the path where the paper measured -29% CPU per write and -19% CPU per scan read.
- Your write-flush path is CPU-bound per process. In the DBWR-isolated test, write IOPS rose from 1.07M to 1.43M, and 23 io_uring DBWR processes delivered 1.24M write IOPS against 1.07M from 32 libaio ones.
- You want to free CPU at the same throughput, not cut latency. TPC-H CPU per query fell 8.5% (geomean), and scan-heavy queries gained most (Q6 -14.6%, Q1 -12.7%).
- You are deciding which I/O paths to port first. Section 3 and Table 7 work as a checklist: batched async paths first, buffer registration before ring-fd or file-fd registration, and no polling modes.

**Skip it when:**
- Synchronous single-block reads, the most common OLTP I/O. pread and io_uring submit-and-wait matched from 4 KB to 256 KB, and at 512 KB and 1 MB io_uring used about twice the CPU per I/O (16.18 vs 7.33 us, and 27.00 vs 13.44 us) because of io-wq offload.
- Small-batch, immediate-reap paths such as redo/WAL writes. With batches of 1-8, libaio and io_uring were indistinguishable (13.32 vs 13.47 us CPU per I/O, same 110 us p99).
- When the goal is lower latency or more OLTP throughput. TPC-C tpmC was unchanged, TPC-H elapsed times were within noise, and direct-path read latency was 9.8 vs 9.9 ms.
- When you need reusable or reproducible code. The Oracle layer is proprietary, and the Update IOPS, Scan, TPC-C and TPC-H results cannot be rerun outside Oracle.
- When you need to share buffers across separate processes on current kernels. Mainline IORING_REGISTER_CLONE_BUFFERS returns -EINVAL when the two rings were created under different mm (Linux 6.14, commit 19d340a, tagged for stable). Since September 2025 it also returns -EEXIST when the source ring is SINGLE_ISSUER and owned by another task. The paper does not explain how its separate Oracle processes get past these checks; threads within one process are not affected.

**Vs siblings:** All the siblings (Condy, uring_exec, Asio's io_uring backend, monoio, PhotonLibOS, Seastar) are reusable event loops benchmarked on network servers or echo/ping-pong, and none reports database write-flush or scan numbers. Read this paper when deciding which storage paths in a multi-process engine should move from libaio to io_uring; for code, use liburing or a sibling library, and for a reproducible database study use Jasny et al. (github.com/mjasny/vldb26-iouring), which the paper cites.

**Gotchas:**
- The artifact's 'shared' registration mode never calls IORING_REGISTER_CLONE_BUFFERS. It issues register opcode 27 (IORING_REGISTER_NAPI in mainline; the code calls it IORING_REGISTER_BUFFERS_SHARE, after the unmerged SHARE_BUF/ATTACH_BUF patches) and ignores the result. So Table 6's shared column (7.5 ms for 200 processes, behind the '270x' claim) measures only ring creation.
- Figure 2's libaio baseline runs at depth 1, while the io_uring configurations batch 32-128 I/Os. Its CPU per I/O (CLOCK_PROCESS_CPUTIME_ID) also includes busy-spin think time, which batching spreads over more I/Os. The like-for-like batched libaio vs batched io_uring comparison is Figure 3 (sensitivity_bench, geomean -39%).
- Every artifact benchmark is a random read on a raw NVMe device. The write path behind the headline +34% write IOPS, the sync pread comparison (Table 3) and the redo test (Table 8) have no public code.
- io_uring_bench.c and sensitivity_bench.c include <linux/io_uring.h> and then redeclare IORING_REGISTER_IOWQ_MAX_WORKERS, IORING_REGISTER_RING_FDS and struct io_uring_rsrc_update. Newer uapi headers already define these, so expect a compile error and a small patch before running (not built here).

**Status:** The work is active (arXiv v1 in September 2026, artifact v1.1 on Zenodo in May 2026, 'submitted to PVLDB') but is reference-only: the Oracle implementation is closed, and the 1-star artifact repo has no LICENSE file, while Zenodo lists CC-BY-4.0 and the README says it is 'provided for academic evaluation'.

[benchmark](https://arxiv.org/abs/2609.22781v1)

##### uWebSockets (µWebSockets / uSockets)  `C++`  `Apache-2.0`  `active`  `Tier C`

C++ HTTP/WebSocket server on the uSockets event layer; author measured 12x the req/s of clustered Node.js/Fastify.

**Beats:** Node.js (Fastify, run as a cluster) — In a Feb 2021 blog post, the author ran the uWS HelloWorldThreaded example on a fanless 4-core Raspberry Pi 4 (Ubuntu 20.10 ARM64, overclocked to 1.75 GHz), loaded over Ethernet from a laptop by uSockets' http_load_test with 200 non-pipelined connections. It served 106k req/s (93k at stock clock, 77k with TLS 1.3) against 8.8k for Node.js/Fastify run as a cluster (12x); uWebSockets.js reached 75k. This is a single first-party run: Node/Fastify versions and code are not published, and compiler flags are not stated (today's build.c uses -O3 -march=native -flto).

**Known shortcoming:** The 12x figure is the author's 2021 blog (uWS 106k vs Fastify cluster 8.8k req/s on an overclocked Raspberry Pi 4) with no compiler, flags or Fastify versions; the repo's own older chart shows about 6x. Apache-2.0 notices are missing from some source files and one file is third-party MIT.

**Known shortcoming:** No HTTP/1.0 (declined, #1547) or HTTP/2; HTTP/3 is WIP. The io_uring backend is dev-only and drops WebSocket messages over ~2 KB (#1931, open); an ASan double-free on shutdown is open (#1863). The benchmarked threaded example uses the 'highly experimental' LocalCluster.h. Returning from a handler without end() or onAborted() calls std::terminate. 4 KB header limit by default.

**How:** Shared-nothing, thread-per-core event loops run on raw epoll or kqueue (uSockets, up to 1024 ready events per wait). Each loop has one 512 KB receive buffer shared by all its sockets instead of per-socket buffers. The HTTP parser is zero-copy (string_views into that buffer) and scans 8 bytes per step with the SWAR 'hasLess(x, n)' bit trick. It writes a '\r' sentinel past the end of the data so the hot loops need no bounds checks, and a 256-bit Bloom filter answers most getHeader misses. Responses are 'corked' into a 16 KB per-loop buffer, so status, headers and body leave in one send() and one TLS record. Idle timeouts use a coarse 4-second sweep instead of per-socket timers.

**Use it when:**
- C++ services that hold many HTTP/1.1 or WebSocket connections with small messages (trading feeds, games, chat, notifications), where server I/O plumbing, not a database, is the bottleneck.
- Replacing a Node.js HTTP/WebSocket tier. In the author's Raspberry Pi test, uWebSockets.js inside Node reached 75k req/s against 8.8k for clustered Fastify, so you can keep JavaScript if you cannot move to C++.
- WebSocket fan-out with built-in topic pub/sub, where per-socket maxBackpressure drops sends to slow subscribers automatically. On the author's 1-core echo chart, v20.42.0 beats Deno's fastwebsockets v0.4.2 by roughly 1.2x from 512 B to 16 kB messages (derived from bar heights).
- In-process TLS 1.3 termination on small hardware. The blog measured 77k req/s with TLS against 106k cleartext. The author's own docs quote TLS retention anywhere from about 60% to about 80%.
- Cross-platform deployment: epoll on Linux, kqueue on macOS/FreeBSD and libuv on Windows, all behind one API.

**Skip it when:**
- Clients or proxies that speak HTTP/1.0 upstream. The parser accepts only 'HTTP/1.1' request lines, and the maintainer declined 1.0 support (issue #1547, whose reporter hit it behind nginx). There is no HTTP/2, and HTTP/3/QUIC is work in progress.
- General-purpose event-loop work (custom protocols, heavy outbound clients). uWS is server-first, and its C++ WebSocket client (src/ClientApp.h) is a 35-line minimal header. For that work, use uSockets directly or a general event library.
- Designs where many threads share sockets. Sockets must never be touched off their loop's thread, and only Loop::defer is thread-safe.
- Production use of the io_uring backend. The maintainer calls it 'extremely experimental and only for dev', and open issue #1931 reports WebSocket messages above about 2 KB silently dropped on io_uring while epoll works.
- Projects that need clean licensing without legal review. The README reserves all rights except for files with an explicit Apache-2.0 notice, and several headers (ClientApp.h, Http3*.h, LocalCluster.h) have none.

**Vs siblings:** Pick uWS when you need a finished HTTP/1.1 + WebSocket server in C++ (routing, pub/sub, TLS, backpressure). The libhv and PhotonLibOS entries are general event-loop/runtime layers measured on ping-pong against libevent/libuv and boost::asio, so pick them for custom protocols. Their 1.05-1.4x gains are not comparable to uWS's 12x, which is measured against a JavaScript HTTP stack, not another native event loop.

**Gotchas:**
- If a handler returns without calling res->end() and without registering res->onAborted(), uWS calls std::terminate. HttpRequest is stack-allocated and valid only during the handler, so copy what you need before going async.
- Automatic corking applies only inside uWS callbacks. Sends from third-party library callbacks or later async code are uncorked, so wrap them in res->cork(...) or pay for several syscalls and TLS records. Only one socket per thread can be corked at a time.
- Hard request limits: 4096 bytes of headers (the UWS_HTTP_MAX_HEADERS_SIZE environment variable) and 100 headers (the UWS_HTTP_MAX_HEADERS_COUNT macro); larger requests get 400. Timeouts are only accurate to about 4 seconds.
- The benchmarked multi-core example uses LocalCluster.h, which calls itself 'highly experimental' and defines non-inline globals in a header. Open issue #1863 reports an ASAN double-free of WebSocket UserData when ending sockets from the server side during shutdown.

**Status:** Actively maintained (v20.80.0 released 2026-09-03, last commit 2026-09-18) and fuzzed in OSS-Fuzz (18 OSV records from 2020-08 to 2021-12, all marked fixed), but usability is 'mixed' because the README reserves all rights except for files that carry an explicit Apache-2.0 notice.

[repo](https://github.com/uNetworking/uWebSockets) · [benchmark](https://levelup.gitconnected.com/serving-100k-requests-second-from-a-fanless-raspberry-pi-4-over-ethernet-fdd2c2e05a1e)

#### http-parsers

##### jianrong7/http-parser (Go zero-alloc parser)  `Go`  `no license`  `active`  `Tier C`

Tiny zero-allocation Go HTTP/1.x request parser that records byte offsets; ~5-10x faster than net/http.ReadRequest, with far less validation.

**Beats:** net/http (Go standard library, http.ReadRequest) — The author's go test -bench on an Apple M1 Pro (Go version and flags not stated) compares Parser.Parse against http.ReadRequest over a fresh 4 KB bufio.Reader per iteration: 133 vs 1,377 ns (2-header GET), 161 vs 1,602 ns (POST) and 374 vs 2,021 ns (8-header GET), with 0 vs 5,177-5,345 B/op. The POST case declares Content-Length: 27 but carries a 24-byte body, so on that row Parse returns (0, nil) 'incomplete' on every iteration and times only header parsing; net/http's Body.Close error is not checked either.

**Known shortcoming:** The POST benchmark row is invalid: its Content-Length (27) exceeds the 24-byte body, so Parse returns 'incomplete' every iteration and the 161 ns times header parsing only (net/http's failure is hidden by an ignored Body.Close error). The net/http side allocates a new 4 KB bufio.Reader per iteration; the gap shrinks from ~10x to ~5x as headers grow, and the speed is mostly skipped work (byte-at-a-time, no SIMD, 495-641 MB/s). Empty header values (legal) swallow the next line or never complete (traced, not run). Almost no validation: control bytes accepted, invalid Content-Length treated as no body, last duplicate CL wins, CL+TE accepted, 'chunked' matched by substring; the README's bare-LF claim is wrong. Body() returns the rest of the buffer (pipelined requests leak in); HeaderAt has no bounds check. Module path 'http-parser' breaks go get, no licence, one init commit (2026-02-08), 0 stars: reference only.

**How:** A hand-written, byte-at-a-time finite-state machine (one switch per byte, with no SIMD, SWAR or lookup tables) stores [start,end) offset spans in a fixed [64]Header array embedded in the Parser struct. Nothing reaches the heap, and Reset only zeroes counters. Content-Length and Transfer-Encoding are found by name length (14 or 17 bytes) followed by an ASCII case-insensitive compare; no other header is interpreted. Most of the gap versus net/http is work that this parser skips: http.ReadRequest reads the request line as a string through a textproto reader, checks validMethod, runs url.ParseRequestURI, builds the header map with readMIMEHeader, reconciles Host and sets up the body reader in readTransfer.

**Use it when:**
- Studying or prototyping a zero-copy Go request parser. It is ~380 readable lines with a unit-test and benchmark file, and the README lists its gaps honestly.
- Trusted, well-formed HTTP/1.1 requests (internal tooling, load-generator harnesses, fixed clients) that arrive complete in one buffer, with at most 64 headers and bodies framed by Content-Length.
- Hot paths that only need the method, raw URI and a few header spans, where net/http's per-request *http.Request, header map and URL parsing cost more than the work you actually do.
- Small requests, where the reported gap is largest: ~10x for the 2-header cases, narrowing to ~5x at 8 headers.

**Skip it when:**
- Any internet-facing server. The method (after its first byte), the URI, header values and the version are not validated, so CR, LF, NUL and other control bytes are accepted. CL/TE conflicts and duplicate Content-Length are not rejected (the last value wins), and an invalid Content-Length such as 'abc' or '+5' is silently treated as 'no body'.
- Requests with an empty header value such as 'X-Foo:' or 'X-Foo: '. Traced from parser.go, the value state consumes the CR unchecked, so the next header line is swallowed into that value. If the empty header is the last one, Parse returns (0, nil) forever.
- Chunked uploads, bare-LF clients or streaming bodies. A chunked request is 'complete' at the end of its headers with raw chunk framing left for you. Bare-LF lines are absorbed into the version or header value, or the request never completes; they are not rejected with an error, despite what the README says.
- Large header blocks or long URIs where scan speed matters. It scans one byte at a time at 495-641 MB/s, while SIMD parsers in this category report GB/s (for example thhp at 4.4 GB/s with SSE4.2, on other hardware).
- Anything that needs a dependency you can legally ship. There is no license, it is a single 'init' commit with 0 stars, and the module path is 'http-parser', not github.com/jianrong7/http-parser, so it cannot be fetched with go get.

**Vs siblings:** The only Go sibling is blazehttp, a tier-A, zero-alloc header parser inside a full HTTP/1.1 and HTTP/2 server benchmarked against fasthttp. Pick blazehttp for anything real, and pick this one only as a ~380-line teaching or prototyping parser to copy (license permitting) when you want offsets without a framework. The C and Rust siblings (picohttpparser forks, httparse, thhp) are far more mature choices outside Go.

**Gotchas:**
- Body() returns everything from the end of the headers to the end of the buffer, not ContentLength() bytes, so pipelined next requests or trailing garbage show up in the body. Slice with the returned n, or with bodyStart+ContentLength, yourself.
- All accessors alias your buffer and are valid only while it is unchanged. Copy them before recycling a pooled read buffer. HeaderAt(i) does not check i against HeaderCount(), so an out-of-range index returns stale spans from an earlier request or panics.
- Chunked detection is a case-insensitive substring match on the Transfer-Encoding value ('xchunkedx' counts). Header values keep trailing whitespace, and duplicate headers are stored separately.
- Parse returns (0, nil) for incomplete input but keeps its state. Re-calling it with the grown, contiguous buffer resumes, but the whole request must end up in one slice, and a Content-Length that overflows int can make it wait forever or swallow the rest of the buffer.

**Status:** The record says active, but the repo is a single 'init' commit from 2026-02-08, untouched for ~7.5 months, with 0 stars, 0 issues, no releases and no license. That makes it usable only as a reference to read, not as a dependency to vendor.

[repo](https://github.com/jianrong7/http-parser) · [benchmark](https://github.com/jianrong7/http-parser/blob/main/README.md)

##### Picozig (zig-pico)  `Zig`  `no license`  `active`  `Tier C`

Pure-Zig port of picohttpparser's request parser. A self-run bench claims ~1.6x over scalar picohttpparser, but the baseline was not re-measured.

**Beats:** picohttpparser — src/request/bench.zig parses picohttpparser's bench.c 'kittyhell' request (10 headers, 32-slot array) 10 million times in one run, timed with a millisecond wall clock. Built with zig run -O ReleaseFast (Zig version not stated; the code targets 0.15.1) for the native CPU, it printed 5,086,000 requests/s on an AMD Ryzen 8845H mobile CPU. The '~3.2M headers/sec without SSE4' picohttpparser figure has no stated source and was not re-measured: upstream bench.c has no timer and was not run on that machine. The units also differ, so the ~1.6x is only indicative.

**Known shortcoming:** Memory-safety bug: parseRequest ignores the caller's num_headers and slices headers[0..100] on a many-item pointer (picozig.zig:265), so a request with more headers than the caller's array writes past its end in every build mode; callers must supply at least 100 slots (the repo's own bench passes 32). Looser than picohttpparser: accepts an empty method or target, doesn't check method token characters, rejects multiple spaces upstream accepts, keeps trailing whitespace in values. The '~3.2M headers/sec' pico baseline has no source and wasn't run on the same machine; units differ (requests/s vs headers/s); one 10M-iteration run; host-CPU build may auto-vectorize despite 'without SSE4'. Partial port: no response parser, chunked decoder or last_len path; body never filled. No licence file and no picohttpparser copyright notice; 9 commits, 0 stars; build.zig.zon says Zig 0.14 but code needs 0.15, untested on 0.16.

**How:** It uses the same scalar design as picohttpparser without SSE4.2: a stateless single pass over the buffer, a 256-entry comptime lookup table for header-name token characters, and a byte-by-byte printable-ASCII scan (c -% 0x20 < 0x5F) for header values. The only 'fast' helper, findCharFast, loads 16 bytes into a @Vector(16, u8) on x86-64/aarch64 but then tests each lane in a scalar loop. It has no vector compare and no PCMPESTRI, and it is only used for the method and path tokens. The README's 'without SSE4' means no hand-written SIMD. It does not mean a no-SSE4 build: zig run targets the host CPU by default, so LLVM was free to auto-vectorize with the benchmark machine's extensions.

**Use it when:**
- Reading or forking a compact example: about 275 lines of Zig in src/request/picozig.zig that map almost one-to-one onto picohttpparser's parse_request/parse_headers
- Zig prototypes and internal services that want zero-allocation request parsing with no C in the build, where you control the clients and can hand the parser at least 100 header slots
- Code that already calls picohttpparser's request API and wants the same i32 return convention in native Zig types instead of @cImport
- Targets where you would build picohttpparser without SSE4.2 anyway (aarch64, other non-x86). The code is portable Zig, but no speed number exists for those targets

**Skip it when:**
- Internet-facing servers. The header array can overflow (see gotchas), request-line validation is looser than upstream, and there is no fuzzing or audit. The project has one contributor and 0 stars
- You need responses, headers-only parsing, chunked transfer-encoding, or incremental re-parse with last_len. Only the request path is ported
- You already build picohttpparser with SSE4.2 or use an AVX2 fork. The claim is only against the scalar build, and it was not measured on the same machine
- Clients that send bare-LF line endings or several spaces between request-line tokens. Picozig returns -2 or -1 where picohttpparser accepts them
- Anything that needs clear reuse terms. There is no license file, and the code is a translation of Perl/MIT-licensed picohttpparser without its copyright notice

**Vs siblings:** Among the Zig siblings, hparse also beats picohttpparser and reports wall time, cycles and instructions against it, which makes it the better-evidenced choice. Picozig is mainly worth picking as a minimal, readable scalar translation of pico's request path to study or fork. For production use, the vkrasnov AVX2 fork, httparse or httpp (about 2.26x at -O3) have stronger benchmark evidence and more complete APIs.

**Gotchas:**
- Header-array overflow: parseRequest ignores params.num_headers and slices the many-item pointer as headers[0..100]. A request with more headers than your array writes past its end, and Zig cannot bounds-check a [*]T slice in any build mode. The repo's own bench and a zig-httpuring test pass 32 slots, and test.zig passes 4-14. Always supply at least 100
- Looser than picohttpparser on the request line. test.zig asserts success for an empty method (' / HTTP/1.0') and an empty target ('GET  HTTP/1.0'), where upstream test.c expects -1. The method is not checked against token characters, so ':GET' is accepted. Multiple spaces between tokens, which upstream accepts, are rejected
- Header values keep trailing spaces and tabs (upstream trims them). A request whose final empty line is a lone LF at the end of the buffer returns -2 (incomplete) until more bytes arrive. test.zig asserts this for 'GET / HTTP/1.0\nHost: example.com\n\n'
- HttpRequest.body is never filled in. Errors come back only as i32 codes, because the internal ParseError is not surfaced. The bundled response formatter heap-allocates a StringHashMap and an ArrayList for every response

**Status:** Counts as active under the 12-month rule (last commit 2025-10-11, a port to Zig 0.15.1). In practice it is a 9-commit, single-author, unlicensed side project that only the author's own repos use (zig-httpuring and buddy-blocks, via a relative ../zig-pico path), so treat it as reference code rather than a dependency.

[repo](https://github.com/solenopsys/zig-pico) · [benchmark](https://github.com/solenopsys/zig-pico/blob/master/readme.md)

##### SynapServe  `Rust`  `no license`  `unknown`  `Tier C`

Closed-source zero-allocation Rust HTTP/1.1 parser inside the SynapServe io_uring server; claims 1.11-1.25x faster tokenization than httparse.

**Beats:** httparse — First-party Criterion runs (100 samples, single core) against httparse 1.10 on three synthetic requests, where SynapServe also extracts content_length, chunked and keep_alive: 42 vs 52 ns at 35 B, 200 vs 230 ns at 368 B and 420 vs 466 ns at 733 B (1.25x/1.15x/1.11x). With a matching extraction loop added to httparse it is 220 vs 304 ns and 413 vs 604 ns (1.38x/1.46x), and known-header lookup is about 0.6 ns vs 20.5-23.1 ns. No CPU, OS, rustc version, flags or benchmark code is given for these parser runs; the site's separate static-file server benchmark ran on an Intel i7-8550U laptop under Linux 6.17.

**Known shortcoming:** No code and no licence: the SynapServe GitHub org (created 2026-02-20) has 0 public repos, no crates.io crate, 'All rights reserved' footer, and the benchmark crate the founder mentioned on HN was never published. The page misdescribes the baseline: httparse 1.10 selects AVX2/SSE4.2 at runtime and enables NEON on aarch64, not 'SSE4.2 compile-time only'. Internal inconsistencies (medium request 200 vs 220 ns; large request faster with extraction than without; response-writer claims with no baseline numbers). The 1.38-1.46x relies on an unpublished extraction loop added to httparse; raw parsing alone is 1.11-1.25x. No CPU, OS, rustc or flags for the parser runs. O(1) lookup covers only 21 unpublished headers; 64 KB header cap and 64-header table; 'not production-battle-tested', no fuzzing documented; server Linux-only (io_uring, 6.1+). Only activity: one blog post (2026-02-21) and a Show HN; solo founder's pitch site, partly AI-generated per the founder. Design reference only.

**How:** The output is compact. Fields are Span{off: u16, len: u16} (4 bytes, Copy), so a header entry is 10 bytes in a [Header; 64] stack table (640 bytes) instead of httparse's 32-byte &str/&[u8] pairs, and a reset clears 29 bytes instead of re-initializing a 2 KB header array. Scanning uses hand-written SIMD with runtime dispatch (AVX2 or SSE4.2 on x86-64, NEON on aarch64, SWAR elsewhere), memchr for delimiters, and fused passes: the CRLF search also rejects NUL and bare CR, and tchar validation of header names runs in the same loop as the colon search. Known headers are recognized by length, then first byte, then word-sized compares (u64/u32 with |0x20 case folding), and recorded in a u32 presence bitmap plus a known_index[21] array, so a lookup is one bit test and one array load instead of a case-insensitive linear scan.

**Use it when:**
- As a design reference for your own Rust HTTP/1.1 front end: u16 span output, a parse-time known-header bitmap index, and fused CRLF plus validation scans are the ideas worth copying.
- If you get the code from the vendor and every request handler checks the same few headers (Content-Length, Transfer-Encoding, Connection, Host). The page reports 0.59-0.67 ns vs 20.5-23.1 ns per lookup and 60-112 ns saved per handler, which is more than the parse gain.
- Small-to-medium request heads (35-733 B tested, 1-20 headers) where you would otherwise parse with httparse and then loop over the headers to find framing fields.
- Evaluating SynapServe itself as a Linux (kernel 6.1+) io_uring HTTP/1.1 server or reverse proxy, since the parser ships only inside it.

**Skip it when:**
- You need a dependency now: there is no public repo (the GitHub org, created 2026-02-20, has 0 public repositories), no crate on crates.io under any synapserve name, and no named license. The site promises an open-source core but its footer says 'All rights reserved'.
- Request heads over 64 KB or more than 64 headers: the founder calls the 64 KB header area, which follows from the u16 spans, a hard limit, and the header table is [Header; 64]. Neither case's behavior is documented.
- You need httparse's API inside hyper, axum or actix-web: the output type is different (buffer-relative spans, not slices), and nothing can be linked anyway.
- You need reproducible numbers: the page gives no benchmark code, CPU, OS, rustc version or flags for the parser runs. The honest parse-only gain is 1.11-1.25x, and the 1.38-1.46x figure depends on an unpublished extraction loop the author bolted onto httparse.
- Security-sensitive or production parsing: the founder says it is 'not production-battle-tested', and no fuzzing, conformance testing or request-smuggling handling (e.g. Content-Length plus Transfer-Encoding conflicts) is documented.

**Vs siblings:** In practice, never as a dependency. httparse (catalogued, the baseline here) is what you would actually ship, and thhp and picohttpparser-rs are public Rust parsers with code you can benchmark yourself. SynapServe is only worth reading for its parse-time header index and fused semantic extraction, which none of those siblings do.

**Gotchas:**
- The comparison table misstates the baseline. It lists httparse SIMD as 'SSE4.2 (compile-time only)', but in httparse 1.10's default std build src/simd/runtime.rs picks AVX2 or SSE4.2 at runtime via is_x86_feature_detected!, and build.rs turns on NEON for aarch64 with rustc 1.59+.
- The numbers do not agree with each other. The medium request parses in 200 ns in the tokenize chart but 220 ns in the equal-work chart. The large request takes 420 ns alone but 413 ns with extraction. The 'Response writer: 46% faster' heading and the '1.38-1.40x on responses' claim come with no baseline numbers, only absolute times (3.9 / 33.5 / 41.3 ns).
- O(1) lookup covers only the 21 headers recognized during parsing, and the list is not published (the benchmark shows it includes Content-Type, Content-Length and X-Request-Id). Lookup cost for any other header is not documented.
- Zero allocations is not a difference from the baseline: httparse also never allocates (the caller provides the header array), as the page's own table says. The real differences are entry size (10 vs 32 bytes) and reset cost.

**Status:** Usable only as a reference. The GitHub org has been empty since 2026-02-20, nothing is on crates.io, and the license is unknown despite the promised open-source core. The only activity is a Feb 2026 blog post and a Show HN (2 points), and the roadmap on the site still lists its Q1 2026 milestone as in progress, so maintenance status is unknown for a solo-founder startup seeking seed funding.

[benchmark](https://synapserve.io/posts/http-parser-performance/)

#### http-servers-frameworks

##### uhttp (io_uring-http-benchmark)  `C++`  `no license`  `active`  `Tier C`

Single-route io_uring static HTTP server in C++20; 40-54% more req/s than tuned nginx serving one 10 KB file on loopback.

**Beats:** nginx — On loopback, with 2 server workers pinned to 2 physical cores of an unnamed 8-core SMT 'mobile CPU' and wrk on the other 6, uhttp served a 10,240-byte file at 276-358k req/s against 184-256k for tuned nginx (reuseport, sendfile on or off, open_file_cache, logging off, same cores), +40% to +54% at 64-4,096 connections, as medians of 3 interleaved 45 s runs after a 15 s warmup. The build was CMake Release (-O3 -march=native, LTO) on a kernel with CONFIG_INIT_ON_ALLOC_DEFAULT_ON=y; compiler, kernel, nginx and wrk versions are not stated, and the raw CSVs are gitignored, so only the README's medians are published.

**Known shortcoming:** A benchmark server, not a library: serves one route from memory; nginx has the better p99 at 64 connections. No licence (reference only).

**Known shortcoming:** No LICENSE file (reference only); two commits on 2026-08-17, no tests or CI. CMake accepts liburing 2.5 but the code calls io_uring_register_napi(), which needs 2.6; DEFER_TASKRUN needs Linux 6.1+ (undocumented). More than 32 pipelined requests in one write may stall (code reading). ETag/Last-Modified/Accept-Ranges are sent but conditional and Range requests are ignored; the file is read once at startup. Serves GET on one exact path, IPv4 only, no timeouts, TLS, HTTP/2, bodies or logging. Loopback-only numbers without CPU, compiler, kernel, nginx or wrk versions; raw CSVs gitignored; -march=native; results bimodal run to run (~350k vs ~389k). bench/tune_system.sh lowers perf_event_paranoid and kptr_restrict system-wide until restored. nginx has the better p99 at 64 connections and higher IPC.

**How:** Shared-nothing worker threads each own one io_uring ring (SINGLE_ISSUER + DEFER_TASKRUN, registered ring fd, CQ 4x the SQ) and use multishot accept into direct (fixed-file) descriptors plus multishot recv over a provided buffer ring, so a connection is accepted and read repeatedly without new submissions and completions are drained and acknowledged in batches. Each response is pre-serialised into one buffer, kept as two copies so only the Date field is patched once a second; SO_REUSEPORT with a classic-BPF steering program keeps each connection on the core that handled its SYN; and per-connection state is a packed 20-byte struct. perf puts syscall entry/exit at 0.07% of uhttp's cycles against 8.71% for nginx, and instructions per request at 17,583 vs 35,831. nginx still has the higher IPC (0.86 vs 0.64), so the author's own summary is that the gain comes from doing less work, not from doing it faster.

**Use it when:**
- Learning or prototyping io_uring networking: a small C++20 codebase (about 1,400 lines in src/) that shows multishot accept/recv, provided buffer rings, direct descriptors, DEFER_TASKRUN and generation-tagged user_data for recycled descriptor slots.
- Measuring io_uring against nginx on your own kernel and hardware: the harness interleaves targets, gives the client 3x the server's cores, flags client-bound runs and reports server CPU microseconds per request.
- A synthetic load-test target that must return one small fixed response at very high request rates on Linux 6.1+ where you control both ends.
- Ablation studies: structural io_uring options are compile-time switches in src/config.hpp and bench/ablation.sh rebuilds and measures each one.

**Skip it when:**
- Serving a real site or directory: one route, one file read at startup, GET only, exact path match (a query string gets 404), no MIME mapping, index files, Range or conditional requests.
- Anything that needs TLS, HTTP/2 or HTTP/3, request bodies, access logging, config reload, IPv6 (the listener is AF_INET only) or idle/read timeouts; none are implemented, so idle or slow clients hold connection slots (default 4,096 per worker) indefinitely.
- Shipping or vendoring code: there is no LICENSE file, and the repo has two commits (both 2026-08-17), no tests, no CI and 0 stars.
- Low-concurrency tail-latency work: nginx had the better p99 at 64 connections (333 us vs 360 us).
- As evidence that io_uring beats sendfile on a real network: every number is loopback, where nginx's sendfile zero-copy path gives no benefit, and the author says the NIC case was not tested.

**Vs siblings:** Pick it over epoll-httpd when the question is specifically io_uring versus nginx's epoll model at 64-4,096 connections with perf-level attribution; epoll-httpd is the better base for real code because it is MIT-licensed and serves arbitrary files. For serving actual traffic, use H2O (static files, TLS, HTTP/2/3) or Sogou Workflow (C++ backend) instead.

**Gotchas:**
- Build floor is wrong: CMakeLists.txt accepts liburing >= 2.5, but server.cpp calls io_uring_register_napi(), which first appears in liburing 2.6's header (the 2.6 CHANGELOG adds NAPI busy-poll support), so a build against 2.5 should fail to compile.
- Pipelining is capped at 32 queued responses per connection. From reading server.cpp, bytes beyond that are carried over and only parsed when the next recv completes, so a client that pipelines more than 32 requests in one write and then waits for all of them can stall.
- It sends ETag, Last-Modified and 'Accept-Ranges: bytes' to match nginx's headers, but ignores If-None-Match, If-Modified-Since and Range and always returns a full 200. The file is never re-read, so edits need a restart.
- The harness's `sudo bench/tune_system.sh apply` sets kernel.perf_event_paranoid=-1 and kernel.kptr_restrict=0 system-wide (plus the performance governor and larger backlogs) until you run `restore`.

**Status:** A one-shot research dump (two commits on 2026-08-17, none since, no issues, releases or stars) with no LICENSE file, so it is reference-only: read it to learn the io_uring techniques, but do not copy or vendor it.

[repo](https://github.com/SquiggleKernel/io_uring-http-benchmark) · [benchmark](https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/README.md)

#### websocket-grpc-rpc

##### Courierust  `Rust`  `PolyForm-Perimeter-1.0.1`  `active`  `Tier C`

Zero-dependency Rust HTTP/WebSocket stack; its WebSocket codec encodes small masked frames ~2.5x faster than tungstenite.

**Beats:** tokio-tungstenite / tungstenite — WS_BENCHMARK.md reports one `cargo bench` release run (thin LTO, codegen-units=1) on a shared Windows machine with no CPU model or rustc version, against tungstenite 0.30 and tokio-tungstenite 0.30 in the same process: masked encode 15.2 vs 40.0 ns at 64 B, 9.5 vs 90-99 us at 256 KiB and parity at 16 KiB; loopback echo at 64 B is 26.5 us against 37.2 us for tokio-tungstenite (2 worker threads) and 26.5 us for sync tungstenite. The repo's own Linux CI report (commit d7d52b3, complexity bench) shows smaller or reversed codec gaps: 64 B masked encode 32.8 vs 40.8 ns (1.24x) and 256 KiB masked encode 100.0 vs 20.5 us (4.9x slower), in a noisy run.

**Known shortcoming:** The repo's own Linux CI run does not reproduce the codec claims: 64 B masked encode only 1.24x (claimed 2.6x) and 256 KiB masked encode 4.9x slower (claimed ~10x faster); headline speedups come from one Windows run. Echo and push benchmarks use the deprecated one-job-per-connection server path (event_driven: false), not the default. The echo win over tokio-tungstenite is sync vs async; sync tungstenite ties it. The UTF-8 loss row is stale (now at parity). The CI has no performance thresholds despite the README. Loses 256 KiB echo (297.6 vs 165.0 us) and 16 KiB echo (9%) to tungstenite. PolyForm Perimeter 1.0.1 licence (noncompete, not OSI) with an extra term. Blocking API only (select/poll), no RFC 8441. First published 2026-08, 5 stars. Filed under WebSocket: it is an HTTP/TLS/gRPC/WebSocket stack, not an event loop.

**How:** Masking XORs 16-byte lanes against one precomputed u128 per key phase: 16 is a multiple of the 4-byte key, so every lane starts at the same phase and the loop autovectorizes in safe Rust (25-37 GB/s on the page). The per-byte `i & 3` key lookup does not vectorize. The masked writer masks in place into a reused staging buffer, while tungstenite 0.30's masked `format` allocates and masks a new copy of the payload for every frame. Other techniques: frames up to 64 KiB go out in one write syscall, payloads over 8 KiB are read straight into the message buffer, and the DEFLATE match-finder tables are reused for each message. The echo win over tokio-tungstenite comes from blocking threads against a 2-worker Tokio runtime, not from the codec, because sync tungstenite ties it (26.5 vs 26.5 us at 64 B).

**Use it when:**
- WebSocket clients that send many small masked frames (64 B-1 KiB) and where the CPU cost per frame matters: the page shows 15.2 vs 40.0 ns at 64 B and 1.3-1.5x at 1 KiB
- Client uploads of large masked messages where allocation churn matters: courierust allocates 0 bytes per masked frame, while tungstenite allocates a full copy of the payload (1 MiB per 1 MiB message)
- Threaded or blocking Rust programs outside Tokio that need lower small-message latency than tokio-tungstenite: 64 B echo 26.5 vs 37.2 us and 1 KiB echo 26.6 vs 39.0 us, the same as sync tungstenite
- Builds that need a dependency-free or no_std + alloc WebSocket framing core, with strict RFC 6455 validation and incremental UTF-8 checks across fragments
- Programs already on Courierust's HTTP server that need WebSocket on the same port; in the event-driven driver an idle socket costs a poller slot, not a thread

**Skip it when:**
- Async or Tokio code (axum, hyper, tokio-tungstenite users): there is no Future/Stream API, and the benchmark win against tokio-tungstenite is sync against async, not codec against codec
- Bulk transfers of 256 KiB or more with Courierust at both ends: echo is 297.6 vs 165.0 us for tungstenite, and 16 KiB echo is 9% behind (39.3 vs 35.8 us)
- Any product that could compete with Courierust: PolyForm Perimeter 1.0.1 has a noncompete clause and is not OSI-approved, so many OSS distributions and commercial networking products cannot ship it
- WebSocket over HTTP/2 (RFC 8441) is not implemented. The encoder never uses context takeover, so compression ratio is lower on streams of small repetitive messages
- Risk-averse production: the crate was first published 2026-08-21, has 5 stars, 990 crates.io downloads and no issues filed, and its TLS stack is from scratch with no documented third-party audit. Readiness uses select/poll only, and no epoll/kqueue/io_uring backend is documented

**Vs siblings:** Among the siblings, uWebSockets (C++) is the WebSocket server to pick for raw server throughput. monoio or ringline are the picks when the Tokio runtime itself is the bottleneck, which is most of the gap measured here against tokio-tungstenite. Pick Courierust only for a dependency-free, blocking Rust WebSocket client or server where masked-encode cost and allocation per frame matter and the PolyForm license is acceptable.

**Gotchas:**
- The echo and push benchmarks start the server with `event_driven: false`. The README calls this one-job-per-connection model deprecated for production, so the default event-driven server path was not measured
- On Windows, the client keeps `ClientConfig::read_timeout` (30 s by default) armed as SO_RCVTIMEO. The authors measured this at about 2x slower on 256 KiB bulk transfers; for bulk use, set `read_timeout: None` and rely on ping keepalive
- In the event-driven driver, a bulk push loop inside `on_message` blocks the reactor worker, and the bounded send queue then closes the connection. Push fan-out from another thread with `WsConn::sender()`
- The UTF-8 loss row in WS_BENCHMARK.md (1.9x slower than std) is stale. utf8.rs now hands the bulk scan to core::str::from_utf8, and COMPLEXITY.md reports 891.5 vs 890.3 ns (Windows); the Linux CI report gives a ratio of 1.04

**Status:** Actively developed: last commit 2026-09-15, 1.0.7 on crates.io (main is at 1.0.8) and a CI bench/interop/fuzz suite. Its PolyForm Perimeter 1.0.1 license bars competing products, so treat it as reference code to study unless your use clearly does not compete.

[repo](https://github.com/blueokanna/Courierust) · [benchmark](https://github.com/blueokanna/Courierust/blob/main/benches/WS_BENCHMARK.md)

##### grpc_homa (Homa transport plugin for gRPC)  `C++`  `no license`  `stale`  `Tier C`

gRPC C++ transport plugin that replaces HTTP/2-over-TCP with the Homa kernel RPC protocol; reports ~40% lower short-RPC round-trip time.

**Beats:** gRPC (default TCP transport) — The README's 'initial performance measurements' put a short gRPC RPC at about 55 us round trip over Homa versus about 90 us over the stock TCP transport (~40% faster), with no hardware, NIC, kernel, compiler, load level or method given; the repo's rtt test (a mean over 50,000 sequential unary Sum calls on one client thread) is not tied to those numbers. On the Homa wiki the author separately puts ~60 us of an unloaded small gRPC round trip in gRPC software and ~30 us in TCP plus the network, which suggests the remaining 55 us is mostly gRPC itself and that Homa's tail-latency-under-load advantage was not measured here.

**Known shortcoming:** The ~40% (55 vs 90 us) claim gives no hardware or method; development was suspended in late 2023; insecure channels only; the C++ code has no licence (reference only).

**Known shortcoming:** The author suspended work and does not recommend using it (#17, 2025). Open bugs: release-only segfault in BuildAndStart (#15), Homa RPC timeouts where TCP works (#16). A burst of outstanding RPCs exhausted kernel memory and hung a host (#14). Compiles against internal gRPC src/core headers with branches only for gRPC 1.41/1.43/1.57, and HomaModule has changed incompatibly since. Makefile hard-codes the author's paths; x86-64 only (rdtsc); insecure channels only. Homa messages capped at 1 MB, oversized metadata fails the RPC. The 55 vs 90 us figure has no hardware, kernel, NIC or load stated and is a mean over sequential unary calls; tail latency under load, Homa's main claim, is not measured. No licence for the C++ code.

**How:** Homa is a connectionless, message-based datacenter transport. A sender transmits the first rtt_bytes of a message at once as 'unscheduled' bytes. After that, the receiver sends GRANT packets that pace the rest of the message and set its network priority, so a short RPC needs no handshake and has no byte-stream head-of-line blocking. The plugin drops HTTP/2 framing for a packed 21-byte header (stream id, sequence number, metadata and body lengths, flags), sends gRPC slices through one gathered sendmsg iovec, and hands gRPC received slices that point into a kernel-shared mmapped buffer (SO_HOMA_RCVBUF), so contiguous payloads are not copied.

**Use it when:**
- Research or prototyping on Linux clusters where you control the kernel and can load HomaModule on every client and server host.
- Unary gRPC C++ services with small messages inside one datacenter, where tens of microseconds per round trip matter.
- Measuring how much of gRPC's round-trip time comes from TCP. The bundled test_client 'rtt' test runs over Homa, or over TCP with --tcp.
- As a starting point for reviving Homa support in gRPC, if you can build gRPC 1.57.0 from source and are ready to own the code.

**Skip it when:**
- When you need TLS or per-call auth: only insecure channel and server credentials exist.
- In production. The author suspended work in late 2023, and in 2025 (issue #17) he wrote that he does not recommend anyone try to use it. Open issues include a release-build segfault in BuildAndStart (#15) and Homa RPC timeouts on a setup where TCP works (#16).
- Across data centers, on mixed or public networks, on non-Linux hosts, or on managed platforms where you cannot load a custom kernel module on both ends.
- For bursty servers with many outstanding RPCs. Issue #14 reports kernel memory exhaustion that hung the host, and the author said poor application behavior can exhaust Homa kernel resources.
- For Java or other gRPC languages: Java support is only partly done, and the C++ code compiles against gRPC 1.57.0 internals, so newer gRPC releases are untested.

**Vs siblings:** Pick this only if you must keep the gRPC C++ API and want the transport itself to cut small-RPC latency. brpc, grpcxx and Kitex beat gRPC in user space over plain TCP, need no kernel module and are maintained, while this plugin is only the gRPC front end for the catalogued HomaModule, so every gain depends on that driver.

**Gotchas:**
- The Makefile hard-codes the author's paths (HOMA_DIR, GRPC_INSTALL_DIR), so you must edit it by hand; there is no CMake or Bazel build.
- It tracks two moving targets: gRPC internals (branches exist only for gRPC 1.41.0, 1.43.0 and 1.57.0) and the HomaModule API. The last commit (Aug 2025) says 'Homa API has gone through several incompatible changes', and HomaModule has changed since, including a protocol change in Sept 2026.
- Homa messages are capped at 1,000,000 bytes (HOMA_MAX_MESSAGE_LENGTH). Larger gRPC messages are split across several Homa messages, and initial or trailing metadata that does not fit in one Homa message fails the RPC.
- Each socket mmaps a 1000 x 64 KB (~64 MB) receive-buffer region. A server that leaves many RPCs outstanding can exhaust Homa kernel memory (issue #14).

**Status:** Stale: work stopped in late 2023 and the last commit (Aug 2025) only ported the code to the Homa API of that time; the C++ code has no LICENSE file or license headers, so treat it as reference only, not something to vendor.

[repo](https://github.com/PlatformLab/grpc_homa) · [benchmark](https://github.com/PlatformLab/grpc_homa)

### parsing-and-text

#### text-search-and-indexing

##### trigrep  `Rust`  `no license`  `active`  `Tier C`

Rust CLI that pre-builds a disk-backed trigram index of a repo, then searches only candidate files, beating ripgrep in a first-party benchmark.

**Beats:** ripgrep — First-party README benchmark on a clone of git/git (4 patterns, 5 timed runs + 1 warmup each, index pre-built) reports mean query time 0.0405s for trigrep vs 0.0640s for ripgrep and 0.5990s for grep, i.e. ~1.58x and ~14.79x; medians for trigrep and ripgrep are tied at 0.0500s. Timed with `/usr/bin/time -p` (10ms resolution) over 20 samples; no CPU model or rustc version given, and index build time is excluded.

**How:** Indexing extracts every overlapping 3-byte trigram per file and writes a sorted, mmap'd lookup table (`lookup.bin`) plus posting lists (`postings.bin`), enabling binary search instead of a byte scan. At query time the regex is parsed into a `regex-syntax` HIR and decomposed into an AND/OR tree of literal trigrams; posting lists are intersected/unioned (smallest-first) to shrink the file set before the real regex engine ever runs. An 8-bit `loc_mask` (byte-offset adjacency) and an 8-bit `next_mask` Bloom filter on the following byte further prune false-positive candidates pre-verification. Indexing itself is parallelized with rayon.

**Use it when:**
- Large, mostly-static trees (git.git-scale or bigger) searched repeatedly, so index-build cost amortizes
- AI coding agents or scripted workflows issuing many regex searches per checkout, as the README targets
- Patterns with real literal content (e.g. TODO|FIXME, ^#include) that decompose into selective trigrams
- Need for grep-compatible text output or structured JSON output in the same tool
- Prebuilt-binary install wanted on Linux/macOS (x86_64/aarch64) or Windows (x86_64) without a Rust toolchain

**Skip it when:**
- One-off or rarely-repeated searches on a tree: index-build time is excluded from the published benchmark and isn't amortized
- Anything requiring code reuse or redistribution rights: no LICENSE file and no license field in either Cargo.toml, so it is reference-only
- Patterns with no extractable literal (bare character classes, anchors, `.`) fall back to a MatchAll node, losing index selectivity
- Decisions resting on the headline 1.58x: trigrep and ripgrep have the same 0.0500s median, so the gap is mean-only and close to the 10ms timer resolution used
- Concurrent or long-lived multi-process use where index staleness/locking matters: thread/process safety around the on-disk index is not documented

**Vs siblings:** Pick trigrep over ngi or ugrep-indexer mainly for its Cursor-derived on-disk format (mmap'd trigram lookup + loc/next-mask filtering) rather than for the strength of the evidence: ngi reports 1.7x-5.9x and ugrep-indexer 10x-21x with clearer separation, while trigrep's own numbers show tied medians and only a mean-based 1.58x over ripgrep.

**Gotchas:**
- Search auto-builds the index if missing, so a cold first query pays full index-build cost that the published benchmark excludes
- No LICENSE file and no license field in Cargo.toml: code can be read but not legally reused or redistributed
- The next_mask adjacency filter is a Bloom filter (false positives possible, no false negatives); correctness depends on the final real-regex verification pass, not the index alone
- `trigrep status` checks staleness against git HEAD but the index is not auto-refreshed on file edits without rerunning `trigrep index`

**Status:** Actively maintained (last commit 2026-04-30, 46 stars) but ships with no license, so usability is reference-only rather than reusable/redistributable.

[repo](https://github.com/PythonicNinja/trigrep) · [benchmark](https://github.com/PythonicNinja/trigrep#benchmark)

#### unicode-utf8

##### Parabix (bitstream UTF-16 validation kernel)  `C++`  `OSL-3.0`  `abandoned`  `Tier C`

Bitstream-parallel text-processing framework whose LLVM-JIT'd SIMD kernel beat a simdutf CLI wrapper on UTF-16 validation.

**Beats:** simdutf — On valid UTF-16LE corpora (128/256 MiB, single thread, Apple M1, median of 7 runs), a third-party benchmark measured Parabix's SIMD kernel at 2900-3760 MiB/s raw (5075-5205 MiB/s overhead-adjusted) against a simdutf v9.0.0 CLI wrapper (clang -O3 -std=c++17) at 1824-2532 MiB/s raw (1883-2600 MiB/s adjusted) -- about 1.18-2.0x raw and 2.0-2.7x adjusted -- but the simdutf wrapper reads the whole file into memory before validating while Parabix streams it, so part of the gap reflects I/O handling rather than the validation kernels.

**Known shortcoming:** The benchmarked UTF-16 validator is not in this mirror: it is a patch in an unlicensed 0-star student repo (dakshkashyap/cmpt479-project-group8), and its timings are whole-process runs dominated by file I/O rather than validation.

**How:** Core technique is Cameron et al.'s parallel bit-stream method: input is transposed (s2p) into 8/16 bitstreams, each holding one bit-position across the whole buffer, turning per-character branching into bitwise AND/OR/shift ops across a full register width, plus optional multicore pipeline parallelism (--thread-num). On this specific benchmark part of the apparent win is a process/I-O gap rather than kernel speed: Parabix streams the file through ReadSourceKernel while the simdutf wrapper CLI reads the whole file into a std::vector via ifstream before validating; the benchmark authors' own methodology doc says I/O is not equalized between the two.

**Use it when:**
- Building a new streaming text pipeline (regex search, XML parsing, transcoding) where adopting the whole Parabix framework is acceptable, not just linking a validator
- Multi-stage text transforms where replacing many per-character branches with bitwise ops across a full register/vector width is the goal (icgrep-style regex matching)
- Research or teaching on bit-parallel SIMD algorithms and LLVM JIT code generation
- Environments that can carry an LLVM 5+/Boost 1.61+/Z3/CMake toolchain at both build and run time
- Workloads that also want multicore pipeline parallelism (thread-num > 1) inside the same kernel model

**Skip it when:**
- You need a small, embeddable UTF-8/UTF-16 validator with a stable C/C++ API — no such component exists in this mirror; use simdutf directly
- Startup latency matters: Parabix's LLVM JIT pipeline load adds ~0.019s fixed overhead per process vs ~0.002s for simdutf, dominating small-input timings
- You need permissive licensing — Parabix/icgrep is OSL-3.0 (strong copyleft), unlike simdutf's permissive license
- You need an actively maintained project — no commits on this mirror since 2021-08-10
- You need UTF-8 rather than UTF-16 — this benchmark and the validator it measures are UTF-16LE only

**Vs siblings:** None of the catalogued UTF-8 siblings (ada-url/idna, simdutf8, xutf, SimdUnicode, utf8_range) target UTF-16, so there's no direct sibling for this workload; pick Parabix over building your own UTF-16 path only if you're already adopting its whole bit-parallel framework for other text processing, not for a standalone validator.

**Gotchas:**
- The benchmarked tools/utf16validate isn't in this GitHub mirror; it's added by a third-party patch to Parabix commit f0369dd pulled from the SFU GitLab, and that commit postdates this mirror's last sync (2021-08-10)
- Fixed per-process overhead (~0.019s, mostly LLVM JIT pipeline load) is roughly 9x simdutf's (~0.002s) — raw wall-clock throughput on small inputs is dominated by this, use the benchmark's overhead-adjusted numbers instead
- GitHub reports this repo's license as NOASSERTION even though the README and OSL3.0.txt/LLVM-LICENSE.txt in the tree declare OSL-3.0 for Parabix code and the LLVM Release License for vendored LLVM files
- This is a read-only mirror: it does not accept GitHub pull requests; patches go to an SFU GitLab research repo instead

**Status:** Abandoned on this mirror since 2021-08-10 (no evidence in this session of active development elsewhere) and usability is mixed: it's a research framework with no stable API, requiring a full LLVM/Boost/Z3 build toolchain rather than a library you can drop in.

[repo](https://github.com/parabix/parabix-devel-mirror) · [benchmark](https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/utf16_benchmark_apple_arm64_summary.md)

### serialization-and-formats

#### binary-schemas

##### MTS-1 (Lightweight Delta-Encoded Telemetry Format)  `Rust`  `CC-BY-4.0`  `unknown`  `Tier C`

Rust per-packet binary telemetry format (MTS-1/MWire) reporting ~5% smaller payloads than MessagePack on synthetic host metrics.

**Beats:** MessagePack — The only claim is size: on a synthetic 10k-record set, per-packet MTS-1 totals 1,390,000 B vs 1,469,521 B for MessagePack (rmp-serde, structs as arrays) and 5,475,079 B for JSON (5.4% and 74.6% smaller), and the 20k and 50k sets scale linearly. Protobuf was not measured, and no compiler, hardware or timings are given. My arithmetic on the repo's generator reproduces the MessagePack and MTS-1 byte counts exactly for all three sizes.

**Known shortcoming:** Size-only claim, no speed numbers. The benchmark generator runs with delta encoding off on synthetic sin/cos data at 1 s intervals, so the 139 B/record is the fixed packet size. The MessagePack baseline stores the UUID as a 36-char string; with a binary UUID MessagePack would be about 127 B and win (derived from the generator, not measured). No root LICENSE file although the README says MIT.

**How:** The win is in size, not speed. Each present field is a 1-byte tag (3-bit type, 5-bit field number) followed by a fixed-width little-endian value, absent fields are skipped, and the UUID is stored as 16 raw bytes. In the paper's generator this gives a constant 139 B per record: a 2 B length prefix, 15 B header, 18 B device ID, 16 B UUID, 84 B payload and 4 B CRC. The 'delta' mode is change suppression: a delta packet or frame carries the new values of fields that changed (optionally only past a per-field epsilon), not arithmetic differences. Per-packet LZ4 (lz4_flex block mode) is optional.

**Use it when:**
- Reproducing or auditing the paper: the repo's generate_dataset binary and committed tele20k/tele50k files let you re-derive Table I byte counts.
- Rust host agents sending fixed host metrics (CPU %, temperature, frequency, memory, disk, network counters, uptime) where you own both ends and want a checksummed packet with timestamp, sequence number and a LAN-proxy flag.
- Slowly changing metric streams stored as JSON arrays, where the MTS1 stream mode stores field names once and writes only changed fields between snapshots (every 10th record by default).
- As a small reference design for a telemetry packet layout: the core crate is about 100 KB of Rust in 7 files, with no unsafe code.

**Skip it when:**
- You need speed numbers. No encode or decode timings are published. The README's ~65,000 encode / ~112,000 decode records/s gives no hardware, method or baseline, and no results from the criterion comparison bench are published.
- You want a fair size win over MessagePack. The 5.4% margin exists because the baseline stores the UUID as a 36-char hex string (38 B) while MTS-1 stores 16 raw bytes. By my arithmetic on the generator code (not a measurement), rmp-serde MessagePack with a binary UUID would be ~127 B per record vs MTS-1's 139 B.
- C++ codebases, or platforms without prebuilt artifacts. It is Rust only, with no C/C++ API. The only prebuilt artifacts are a Windows x86-64 mwire.exe and a single PyPI wheel (magenta-telemetry 0.1.0, CPython 3.11 win_amd64). Nothing is published on crates.io.
- Untrusted input. The decoders call `Vec::with_capacity` / `HashMap::with_capacity` with u32 counts read from the packet, and CRC32 is not authentication, so a crafted packet can request very large allocations.
- Production dependencies. It is single-author code (5 stars, 6 commits from 2026-02-15 to 2026-03-01, no issues filed) with no root LICENSE file. The packet format has a fixed field table (numbers 0-31). A lost snapshot breaks delta reconstruction, and an epsilon above 0 makes delta mode lossy.

**Vs siblings:** Pick it only if you want a ready-made, CRC-checked host-metrics packet in Rust. For compactness alone, JSON BinPack (smallest or tied-smallest across 27 documents) and qdf (IoT/OTLP batch fixtures) have broader size evidence, and fernBuffer's MessagePack comparison covers more data shapes.

**Gotchas:**
- The paper's 'delta-encoded' results do not use delta mode. generate_dataset.rs calls `encode()` on full records with `is_delta` false, so Table I measures plain fixed-width packets. The constant 139 B per record is therefore the natural packet size, not evidence of computed numbers.
- The paper and the code describe different methods. The paper cites real Magenta samples at ~30 s intervals and deltas of c_i - c_(i-1). The generator uses sin/cos synthetic values at 1 s intervals with one device ID and UUID, and delta frames carry replacement values. The paper's 100-host example (1.95 GB vs 0.24 GB, '87.7%') also disagrees with its own 548 B vs 139 B per payload.
- The two spec documents disagree. docs/FORMAT.md's type-ID table (e.g. 0x01 = Null) and its legacy flag bits do not match core/src/types.rs and encoder.rs, which follow FORMAT_SPEC.md (0x06 = Null, delta = flag bit 4). Treat the code as the spec.
- Per-packet LZ4 makes these packets larger (2,794,270 vs 2,780,000 B on S2) because `compress_prepend_size` adds a 4-byte length and the ~84-byte payload barely compresses. Only the stream mode's whole-body LZ4 pays off: DISTRIBUTION_README reports 1,340,041 vs 4,440,224 B on a 25,957-record dataset.

**Status:** Single-author research code behind a non-peer-reviewed January 2026 arXiv preprint: last commit 2026-03-01, one v1.0.0 Windows release, MIT according to the README and Cargo.toml but with no root LICENSE file; use it as a reference, not a maintained dependency.

[repo](https://github.com/ndourc/mwire) · [benchmark](https://arxiv.org/abs/2601.01602)

##### psio / pSSZ (successor to fracpack)  `C++`  `no license`  `active`  `Tier C`

C++23 reflection-driven, SSZ-derived binary format with zero-copy views; author benchmarks show faster encode/decode than libprotobuf, capnp, FlatBuffers, msgpack.

**Beats:** Protobuf, Cap'n Proto, FlatBuffers, MessagePack — On the author's own psio_bench_vs_externals harness (unspecified Apple M-series, llvm-clang 22.1, -O3 -DNDEBUG, library versions not stated), per-shape geomeans show libprotobuf 6.4x slower than pSSZ to decode and 43x slower to encode, FlatBuffers 1.23x slower to decode and 2.3x slower on a single-field view, and Cap'n Proto 5.4x slower to decode and 48x slower on a view. The comparison is weaker than it looks: the external encode cells include copying a native C++ struct into the library's builder or message, FlatBuffers and capnp 'decode' means materializing a native struct, the validate ratios are against psio's own re-implementations of those formats, and the anchor CSV is not committed.

**Known shortcoming:** The validate ratios are against psio's own reimplementations of protobuf, flatbuffers and capnp, not the canonical libraries. The C++ core has no LICENSE file (only the Rust and npm manifests declare MIT). Published ratios are latency, measured on an unspecified Apple M-series chip.

**Known shortcoming:** The competitor encode timings include copying a native struct into each library's builder, FlatBuffers/capnp 'decode' builds a full native struct, and the capnp view timing constructs a new reader per call, likely inflating the 43-82x and 47.57x ratios. Decode and view are unchecked (only validate reports errors). Verified only on macOS ARM64; host byte order only; requires C++23, Boost and Homebrew LLVM on macOS.

**How:** Each record is a fixed region (scalars inline, one offset slot per variable field) followed by a dynamic region, so a field's position is a compile-time constant that a view reads with one load, and a variable field's size comes from the next offset instead of a length prefix. The offset width (1, 2 or 4 bytes) is chosen per type at compile time from length_bound and maxDynamicData annotations. Records marked definitionWillNotChange() (DWNC) drop the extensibility header, and a trivially copyable, unpadded DWNC record (or a vector of them) encodes and decodes as one memcpy. Validation is one bounds check per offset slot, with nesting depth capped at 64.

**Use it when:**
- C++23 services that exchange existing structs between processes you control, and want to serialize them with no separate IDL or codegen step.
- Read-heavy paths that pull one field out of a validated buffer. The spec's view_one table shows 0.33-0.56 ns for pSSZ, against 0.58-3.46 ns for FlatBuffers and 17-28 ns for Cap'n Proto on the same shapes.
- Content-addressed or signed payloads that need exactly one canonical byte sequence per value (spec §15).
- Bulk arrays of fixed-layout records such as validator or tick lists. Marking the record DWNC and trivially copyable turns encode and decode into a memcpy.
- Small bounded messages, where length_bound annotations shrink offset slots and headers to 1 or 2 bytes.

**Skip it when:**
- Integer-heavy or sparse payloads where wire size matters most. In the author's table Avro, MessagePack and Protobuf are 0.56-0.65x pSSZ's raw size. The gap narrows to 0.87-0.91x after zstd-1.
- Streaming or incremental parsing. Offsets are container-relative, so the whole container must be in memory before any field can be read.
- Polyglot systems. pSSZ exists only in C++ and Rust: JS/TS has no pSSZ, and no Python, Go or Java port exists. psio's own Protobuf, MessagePack, capnp and FlatBuffers codecs are covered by only two shared fixture records each.
- Production code or code that parses untrusted input today. The library is at 0.1.0 with no tags or releases and no LICENSE file, and it has been verified only on macOS ARM64. Its own release checklist asks for sanitizer and fuzz jobs 'before accepting untrusted inputs'.
- Builds with -fno-exceptions or for WASI guests. The docs say the exception-free profile is incomplete: headers still contain unguarded throws.

**Vs siblings:** Pick pSSZ when both ends run C++ (or Rust) and you want one reflected struct declaration to give zero-copy single-field reads, canonical bytes and append-only schema evolution together, and you can accept a pre-release, unlicensed codebase. Pick hpp-proto if you must stay on the Protobuf wire, and rkyv for a Rust-only zero-copy codebase.

**Gotchas:**
- Only validate reports errors. error.hpp says decode and view accessors assume the input has already been validated, so call psio::validate<T>(psio::pssz{}, bytes) on every untrusted buffer first. The 64-level depth cap applies to validate, not to decode.
- The offset width W is derived from the type and never stored on the wire. Changing a length_bound in a way that flips W, or adding definitionWillNotChange() to an existing record, silently breaks bytes that are already stored. Encoding more than maxDynamicData throws codec_exception.
- Unknown trailing fields are silently dropped, strings are not checked for UTF-8 unless you use validate_strict (which also fully decodes), and appending a variant-typed field is not a safe evolution.
- The spec promises single-pass encode, but the C++ encode entry point first runs size_of over the value and then writes into the pre-sized buffer with unchecked memcpy (fast_buf_stream).

**Status:** Actively worked on (last push 2026-09-16) but pre-release, so treat it as a reference design rather than a dependency: version 0.1.0, 0 stars, no tags or releases, verified only on macOS ARM64, and no LICENSE file (the Rust and npm manifests declare MIT, while the C++ core declares no license).

[repo](https://github.com/gofractally/psio) · [benchmark](https://github.com/gofractally/psio/blob/main/docs/format-comparison.md)

#### yaml-toml-xml

##### SupXML (sup-xml)  `Rust`  `Proprietary source-available (Supported Source; LICENSE requires a paid or free-tier license certificate to use the code; not OSI)`  `active`  `Tier C`

Source-available Rust XML stack with a libxml2-compatible C ABI; the vendor reports ~2.1x median DOM-parse throughput over libxml2.

**Beats:** libxml2 — This is a first-party bench (cargo bench -p sup-xml-bench --bench head_to_head). It compares sup-xml's bumpalo-arena DOM (parse_bytes_unchecked, default options, input copied into an owned buffer) with libxml2 xmlParseMemory plus xmlFreeDoc through FFI, taking best-of-N MiB/s per fixture. The 11 fixtures shown range from 1.61x to 3.75x, the claimed median over 21 is ~2.1x, and the XSTS 1.0 wall-clock is 2.86 s vs 6.81 s with libxml2's 3 timeouts excluded. No CPU, OS, rustc version, flags or libxml2 version is disclosed; build.rs links whatever libxml2 pkg-config or the macOS system provides, and the numbers have not been independently reproduced.

**Known shortcoming:** Proprietary source-available licence (needs a licence certificate). The timed SupXML run skips UTF-8 validation (parse_bytes_unchecked) while libxml2 validates inside its timing, contradicting the page's 'matched contract' claim. No CPU, rustc or libxml2 version; the repo's own COMPARISON.md says only ~1.0-1.3x vs libxml2; the XSD validation text and table disagree. 1 star.

**Known shortcoming:** The timed run also skips encoding sniffing and namespace processing (namespace_aware false) while libxml2 is namespace-aware; best-of-2, no warmup. The project's documents contradict each other (COMPARISON.md ~1.0-1.3x vs the docs page's ~2.1x; W3C suite 255/257 vs 244/257). By its own numbers quick-xml streams faster on 4 of 5 fixtures and its fastest DOM mode reaches about half of pugixml. The libxml2 C shim frees arenas only at thread exit and is off by default because linking it with real libxml2 is undefined behaviour. Parsing hard-fails without a licence certificate. Enrichment confidence 0.4.

**How:** The tokenizer is a strict byte-level SAX reader built on memchr SIMD searches. Text runs scan for '<', '&' and ']' in one memchr3 pass. A start tag jumps to the first '>' and accepts it if a memchr2 count of both quote characters before it is even; otherwise it falls back to a quote-aware scan. XML Name characters are checked against 256-entry ASCII lookup tables. XML 1.0 §2.2 character validation is one upfront SWAR pass over the whole document (the has-zero-byte trick, 8 bytes per iteration) instead of per-token checks, and UTF-8 is validated with simdutf8 (AVX2/SSE4.2/NEON dispatch). The DOM uses libxml2-shaped nodes allocated in one bumpalo arena per document, so each node costs a pointer bump and the whole arena is freed at once. Strings are borrowed from the owned source buffer where possible. An opt-in parse_bytes_in_place mode decodes entities inside the input buffer to avoid copies.

**Use it when:**
- Rust services that need libxml2-class features (XSD 1.0 validation, XPath 1.0, XSLT, C14N for XML-DSig/SAML, recovery mode) without linking C, and that can get a Supso certificate: paid commercial, free 30-day evaluation, or free hobbyist for non-monetized projects
- DOM-parsing UTF-8 documents from about 15 KB to 95 MB into an owned tree. The vendor's table shows 1.61x (pubmed) to 3.75x (Arabic gazali_maqasid_ar, 599 KB) over libxml2's xmlParseMemory; the largest gains are on text-heavy and non-ASCII documents
- XSD pipelines with complex Microsoft-style particle and derivation schemas. On W3C XSTS 1.0, libxml2 goes quadratic and times out at 30 s on 3 schemas that SupXML compiles in under 1 ms, and total schema-compile time is 1.74 s vs 3.96 s
- Browser or edge runtimes that need XML, XPath, XSLT, XSD or HTML parsing: it builds for wasm32-unknown-unknown with every feature except network-resolver
- As a reference design for a strict, validating XML tokenizer built from memchr, SWAR and lookup tables

**Skip it when:**
- Any open-source, redistributable or unlicensed deployment. The LICENSE is proprietary Supported Source (not OSI), and every document-parse entry point returns a fatal error unless a valid certificate is found
- Pure streaming or event workloads. The vendor's own page shows quick-xml faster on 4 of the 5 fixtures it lists (nasa 0.74x, swiss_prot 0.59x, wikipedia_ww2 0.11x), with only ~1.04x median across 21 fixtures at the matched contract
- Maximum DOM speed on trusted input. Its own docs say parse_bytes_in_place with all four skip_* flags reaches 'roughly half of pugixml's throughput', and pugixml-beating siblings go further
- HTML parsing for speed. It wraps html5ever and is at parity with libxml2 (~1.02x geomean on the docs page); COMPARISON.md even shows hn.html at 35 vs 45 MiB/s
- Long-running processes that use the C-ABI shim on persistent threads, because per-document arenas are freed only at thread exit. Also note the maturity: 1 contributor, 1 GitHub star and 121 crates.io downloads

**Vs siblings:** Choose it over yxml, quick-xml, xmloxide or rusty_xml only when you need libxml2's broader surface (XSD, XSLT, XPath, C14N, recovery) in memory-safe Rust or behind a libxml2 C ABI, and you are willing to license it. For plain streaming, quick-xml beats it on most fixtures in SupXML's own table. yxml offers a similar ~2.2-2.4x over libxml2 in a tiny C SAX parser. xmloxide is the other pure-Rust libxml2 reimplementation, catalogued at roughly libxml2 parity.

**Gotchas:**
- Runtime license gate: the first parse in a process looks for a certificate (SUPSO_LICENSE_PATH, ~/.supso/license_certificates/, ./.supso/license_certificates/). Without one, every parse returns a fatal error. An expired certificate only gets a logged grace period before parsing fails.
- The headline benchmark is not symmetric. The timed sup-xml call is parse_bytes_unchecked, which skips encoding sniffing and SIMD UTF-8 validation (the harness checks UTF-8 outside the timer). It also runs with the default namespace_aware: false, so there is no xmlns scanning or QName resolution. libxml2's xmlParseMemory does detection and validation inside the timer and uses its namespace-aware SAX2 interface. Timing is best-of-N with no warmup (default N=2), and 'MB/s' is actually MiB/s.
- The project's own documents disagree. COMPARISON.md gives ~1.0-1.3x median vs libxml2 against the docs page's ~2.1x. The README claims 255/257 on the W3C XML Conformance Suite, but the COMPARISON.md table shows 244/257. An XSD instance-validate time of 1.12 s vs 2.85 s is described as 'parity'. A bench comment still says gazali parses at ~14 MB/s vs libxml2's ~140 MB/s.
- The defaults differ from libxml2: namespace_aware is false (set it true for prefixed XPath), there is a 1 MB entity-expansion cap and a depth limit of 256, and external DTDs are not loaded. The 'memory-safe' claim is scoped: unsafe code is allowed in the scanner, readers, parser, encoding and dom.rs, and the C shim is #![allow(unsafe_code)] even though CONTRIBUTING lists the shim among the forbid-unsafe modules.

**Status:** The project is actively developed by a single maintainer (111 commits from one contributor; v1.3.0 released 2026-06-17; last commit 2026-06-20). It is reference-only here because the proprietary Supported Source license requires a paid or free-tier certificate, and parsing fails without one.

[repo](https://github.com/SupsoOrg/sup-xml) · [benchmark](https://supso.org/projects/sup-xml/docs/reference/performance/)

### stdlib-replacements

#### allocators

##### arena-allocator (ShortAlloc)  `C++`  `no license`  `stale`  `Tier C`

Single-file bump-pointer arena allocator with an STL-compatible wrapper; beats glibc malloc via std::vector, especially above the mmap threshold.

**Beats:** operator new/delete (GNU/glibc malloc via std::vector's default std::allocator) — On QuickBench (clang 17.0, -O3, -std=c++20, libstdc++, single CPU core from a shared AWS pool), std::vector<TestClass, ShortAlloc> doing 100 emplace_back calls was 2.2x-4.4x faster than std::vector's default allocator (glibc malloc) for 8B-512B objects, and 93x-230x faster for 1KB-8KB objects — the latter driven by the default allocator crossing glibc's mmap threshold during vector reallocation, not a general per-allocation speed advantage at that size.

**How:** Allocation is a pointer bump plus an alignment round-up (no free-list search, no locking, no syscalls) as long as the arena has room, so it stays in cache and skips heap-manager bookkeeping entirely. The largest gains (93x-230x) show up once std::vector's reallocations grow past glibc's mmap threshold (~128KB total), where the default allocator pays for an mmap syscall and first-touch page faults that the arena avoids by staying on the stack-backed buffer.

**Use it when:**
- Short-lived, single-threaded scopes with a known upper bound on total allocation, e.g. a function-local std::vector that shouldn't touch the heap
- Many same-sized emplace_back/reallocation cycles where the arena can be sized to the container's peak footprint
- LIFO-order allocate/deallocate patterns, since deallocate() only reclaims the block at the top of the arena
- Containers whose elements grow into the 1KB-8KB+ range, where you want to sidestep glibc's mmap-threshold latency cliff
- Reference/teaching use: a ~180-line file showing a bump allocator plus STL-allocator plumbing

**Skip it when:**
- Multi-threaded code — no locking or atomics in Arena or ShortAlloc; concurrent use is undefined behavior
- Workloads needing out-of-order or random-order frees, since only the most recent allocation can be reclaimed
- Long-running or size-unbounded containers — the arena is a fixed std::array<N> and silently falls back to global operator new once exhausted, with no bookkeeping to route the matching free back correctly
- Anywhere licensing matters — the repo ships no LICENSE file, so reuse terms are undefined
- Copy-pasting the repo as-is into production — the committed source has active std::cout debug prints in allocate()/deallocate() that the benchmarked version did not have

**Vs siblings:** Pick this over general-purpose allocator replacements in the catalog (Hoard, SuperMalloc, NUMAlloc, scalloc) when you want a tiny, dependency-free, single-file bump allocator for a bounded, single-threaded, LIFO-style scope rather than a global malloc replacement for multi-threaded programs. Against the other same-domain arena-allocator (yaroslavaristov), prefer that one for broader, harder benchmark evidence (AMD EPYC and Apple M1, direct malloc/free comparison); prefer this one specifically for the ready-made STL-compatible ShortAlloc wrapper usable as std::vector<T, Alloc>.

**Gotchas:**
- The GitHub source (arena-benchmark.cpp) has its std::cout diagnostic lines active inside allocate()/deallocate(); the QuickBench snippet that produced the published numbers has those lines commented out, so running the repo file as-is will not reproduce the benchmark
- deallocate() silently no-ops (leaks the block) if you free anything that isn't both in-buffer and the most-recently-allocated block — no error or assertion is raised
- Once the arena is exhausted, allocate() falls back to ::operator new, but deallocate() has no bookkeeping to route those heap-backed blocks to ::operator delete except via the top-of-stack pointer check — mixed arena/heap blocks can be freed incorrectly
- The free operator== / operator!= for ShortAlloc reference a nonexistent `rhs.arena` member (the field is actually private `d_arena`) and access it without a friend declaration — this code would fail to compile if a container ever invoked allocator comparison

**Status:** Stale (last commit 2025-03-13, 9 GitHub stars, no open issues, no LICENSE file) and marked 'reference' usability — best read as a worked example of a bump allocator plus STL-allocator wiring rather than adopted as-is; the repo currently ships the un-optimized, debug-print-enabled source, so strip those lines before reusing it.

[repo](https://github.com/shantanu/arena-allocator) · [benchmark](https://github.com/shantanu/arena-allocator#%EF%B8%8F-performance-benchmarks)

##### SpeedMalloc  `C++`  `no license`  `unknown`  `Tier C`

Hardware support-core design offloading malloc/free; gem5-simulated 1.75x throughput over jemalloc, no real silicon exists.

**Beats:** jemalloc (also compared against TCMalloc, mimalloc, Mallacc, Memento) — In gem5 full-system simulation (1-16 AArch64 out-of-order big cores + 1 in-order support core, GCC 9.4 -O3 -march=armv8.1-a), the paper reports SpeedMalloc achieves 1.75x/1.18x/1.15x/1.23x/1.18x geomean throughput over jemalloc/TCMalloc/mimalloc/Mallacc/Memento+ across 10 multithreaded workloads (7 from mimalloc-bench, GAPBS BFS and BC, NAS DC), with smaller single-threaded gains of ~1.09x/1.08x/1.04x/1.03x over jemalloc/TCMalloc/mimalloc/Mallacc. It never compares against glibc malloc or std::allocator directly.

**How:** Metadata never touches main-core caches: the support-core holds a segregated free-list layout in its own L1, eliminating the cache pollution and cross-core atomic-instruction traffic (up to ~22.8% of cycles in the paper's jemalloc/TCMalloc profiling) that shared/thread-local allocator metadata causes today. Hardware message queues (dispatcher, malloc/free queues, scheduler, response queue) in the support-core pipeline and round-robin allocation requests from up to 16 cores instead of serializing on coherence traffic. free() is fire-and-forget and returns to the main core immediately (processed asynchronously off the critical path); malloc() only stalls the main core if it has no independent work to overlap while waiting for the support-core's 'end' signal.

**Use it when:**
- You're researching or designing CPU memory-subsystem hardware and want a concrete design point for offloading allocator metadata to a dedicated core
- Comparing hardware-accelerated allocator proposals (Mallacc, Memento) for multithreaded, many-core AArch64 systems
- Need a gem5 full-system reference for quantifying cache-pollution and metadata-synchronization overhead across allocators
- Interested in the paper's 'butterfly effect' data: allocation is ~4.4% of instructions but choice of allocator swings whole-program performance up to 2.7x

**Skip it when:**
- You need something to link into a real program today: has_code is false, no repo, no artifact was published with the paper
- Your target is x86 or any platform without a custom support-core wired above the LLC and a modified ISA/compiler toolchain
- Single-threaded or lightly threaded workloads: SpeedMalloc's edge there is only ~1.09x/1.08x/1.04x over jemalloc/TCMalloc/mimalloc
- You need peer-reviewed or independently reproduced results: this is a v1 arXiv preprint ('manuscript submitted to ACM'), not yet reviewed
- Any production or deployment use case: the authors state they could not prototype even on FPGA because the required ISA and coherent-bus hardware do not exist in current systems

**Vs siblings:** Not applicable for real use: every catalogued sibling (metapool, NUMAlloc, SuperMalloc, Hoard, scalloc, both arena-allocators, ltalloc, rpmalloc, smmalloc) is a software allocator you can build and link today, while SpeedMalloc requires hardware that does not exist. Treat it only as a research reference for hardware/software co-design ideas, never as a substitute for any of the software allocators.

**Gotchas:**
- Interrupts and exceptions are masked on the main core while it waits for the support-core's 'end' signal during a malloc() call
- free() completes asynchronously off the critical path, so its completion is not visible/synchronous to the caller
- Gains are concentrated in multithreaded workloads (1.75x geomean over jemalloc); single-threaded gains are much smaller (~1.09x)
- No FPGA or real-silicon prototype exists — footnote 8 states current ISA and hardware cannot support one; every number is gem5-simulated

**Status:** Research preprint only (arXiv v1, Aug 2025, 'manuscript submitted to ACM'), not peer-reviewed and with no linked code or artifact; usability is 'reference' and maintenance status is not applicable since nothing is released to maintain.

[benchmark](https://arxiv.org/abs/2508.20253)

#### async-tasks-threadpools

##### meet1214/thread-pool  `C++`  `no license`  `active`  `Tier C`

Header-only C++17 fixed-size thread pool with typed futures and exception propagation, beats std::async by reusing worker threads.

**Beats:** std::async — README's own benchmark/benchmark.cpp, run once on an unspecified 4-core Linux box with no compiler or flags stated, timed 100 std::sqrt-loop tasks: single-threaded 68ms, std::async 18ms (3.8x), ThreadPool at 4 threads 10ms (6.8x) and at 8 threads 7ms (9.7x) — all relative to the single-threaded run; against std::async directly that's about 1.8x (4 threads) to 2.6x (8 threads) faster.

**How:** Amortizes thread-creation cost: std::async(std::launch::async, ...) typically spawns a fresh OS thread per call, while ThreadPool spawns n threads once and reuses them across all submitted tasks via a locked queue. Workers block on a condition_variable when idle (no busy-waiting). No lock-free structures, work stealing, or SIMD — the entire speedup story is 'don't call clone()/pthread_create() 100 times.'

**Use it when:**
- Many short-lived CPU-bound tasks where std::async's per-call thread spawn is the dominant cost
- You want a drop-in-shaped replacement for ad-hoc std::async fan-out with typed futures and exception propagation
- A single-header dependency is acceptable and you can vendor code without a LICENSE file being a blocker (internal/prototype use)
- A fixed, known worker count is fine and you don't need cancellation or priorities
- Teaching/reference use: the README's architecture section is a clear worked example of the packaged_task + shared_ptr pattern for storing move-only tasks in std::function

**Skip it when:**
- Any production dependency where a license is required — there is no LICENSE file despite an MIT badge in the README (404 on GitHub)
- Workloads needing task cancellation, priorities, or dynamic pool resizing — none are implemented
- High task-submission-rate workloads — single global queue/mutex/condvar means no work stealing and one contention point across all workers
- Any decision that needs trustworthy performance numbers — the published benchmark shows superlinear speedup (3.2x on 2 threads, 9.7x on 8 threads, all on a 4-core machine), a single untimed-repetition run, and an unoptimized default build
- Projects wanting an actively maintained, community-vetted pool — 0 stars, single author, no issues or PRs, so no external validation exists

**Vs siblings:** Pick this only as a tiny, license-free-to-check, easy-to-read reference implementation of the packaged_task/shared_ptr pattern; for real use, BS::thread_pool (also header-only, mature, widely used) or utl::parallel (also targets std::async, with a somewhat more detailed benchmark) are safer choices since both have far more scrutiny and, in BS::thread_pool's case, an actual license.

**Gotchas:**
- No LICENSE file exists despite the README's MIT badge — legal status of reuse is actually undefined
- CMakeLists.txt sets no CMAKE_BUILD_TYPE and only passes -Wall -Wextra, so the documented `cmake -B build && cmake --build build` produces an unoptimized (likely -O0) benchmark and test build
- Single shared queue/mutex/condvar design (no work stealing) means throughput will not scale past the point where lock contention dominates, unlike pools built for high task-submission rates
- The benchmark's std::async row spawns 100 OS threads for 100 tasks, so the reported 'ThreadPool beats std::async' number is largely measuring thread-creation overhead, not scheduling efficiency

**Status:** Repo shows recent activity (last push 2026-04-01, marked active) but has zero stars, one author, no issues/PRs, and no LICENSE file, so despite MIT branding it is usable only as a reference, not a dependency to actually take on.

[repo](https://github.com/meet1214/thread-pool) · [benchmark](https://github.com/meet1214/thread-pool#benchmark-results)

#### bitsets-and-succinct

##### better_bitset  `C++`  `no license`  `abandoned`  `Tier C`

Header-only C++20 bitset adding fast first_one/first_zero bit-scan that std::bitset lacks above 64 bits.

**Beats:** std::bitset — First-party Google Benchmark (compiler/flags unstated) on a 20-logical-core ~3.6GHz host: better_bitset::first_one() beats a naive std::bitset .test(i) bit-by-bit loop from N=8 through N=8192 (e.g. 18,134ns vs 953,294ns at N=8192, ~52.6x; 1,789ns vs 128,450ns at N=1024, ~71.8x), but is ~1.6x slower than std::bitset at N=4 (405ns vs 250ns). The mean of the 13 per-size ratios is ~34x, well below the README's claimed '60x average'.

**How:** first_one()/first_zero() call std::countr_zero()/std::countr_one() on each 64-bit (or smaller) storage chunk instead of the .test(i) bit-by-bit loop std::bitset forces on scans above 64 bits. On x86 these compile to a single hardware bit-scan instruction (the BSF/TZCNT family) per chunk, turning an O(N) per-bit test into O(N/64) chunk-level instructions. No SIMD or manual vectorization beyond whatever the compiler emits for those built-ins.

**Use it when:**
- Fixed-size bitsets above 64 bits where you need the position of the first set/unset bit (e.g. slot allocation) without hand-writing a scan loop
- Bitsets of 16 bits or fewer, where the smaller backing integer type (uint8_t/uint16_t) saves a few bytes versus std::bitset
- You're willing to vendor a single ~200-line header and require only C++20, with no upstream support expected
- Reference/inspiration for implementing your own countr_zero/countr_one-based bit-scan rather than using the library directly
- N is not tiny: the measured gains hold from N=8 up through N=8192 in the authors' own benchmark

**Skip it when:**
- You need bitwise operators (&, |, ^, ~) between bitsets — not implemented
- You need std::bitset's assignable reference proxy (bs[i] = true) — operator[] here is const-only
- You need a maintained dependency — inactive since last commit 2022-04-08, 8 stars, two open issues with no response
- You need to ship/vendor code under a known license — no LICENSE file exists and an open issue (#4) asking for one is unanswered
- Your bitsets are consistently very small (N=4) — the authors' own benchmark shows better_bitset ~1.6x slower than std::bitset there

**Vs siblings:** Pick better_bitset over plf::bitset only if you want a single tiny header with zero build configuration and care solely about first_one/first_zero on fixed-size bitsets above 64 bits; plf::bitset covers more operations (set_range/reset_range, shifts) with gains measured on both GCC and MSVC and is the more complete std::bitset alternative in this catalog. For runtime-sized bitsets use sul::dynamic_bitset or BitLib instead (they target std::vector<bool>), and for sparse/succinct workloads use CRoaring or pasta::bit_vector.

**Gotchas:**
- No LICENSE file in the repo; an open, unanswered GitHub issue (#4, filed 2024-11-03) asks the maintainer to add one — treat the code as look-but-don't-ship
- Open issue #3 (2024-10-01, unaddressed) disputes the correctness of first_one/first_zero for some bit patterns; unresolved since the repo has had no commits since 2022
- Benchmark numbers are self-reported with no stated compiler or optimization flags (the CMakeLists sets neither CMAKE_BUILD_TYPE nor compile options), so real gains under -O2/-O3 may differ
- Only smaller than std::bitset for N<=16; at N=4 in the authors' own benchmark it was slower than std::bitset's naive loop (405ns vs 250ns)

**Status:** Abandoned since its last commit on 2022-04-08 (8 stars); no LICENSE file exists and a 2024 issue asking for one is unanswered, so it's readable reference code, not something to vendor as-is.

[repo](https://github.com/MrElectrify/better_bitset) · [benchmark](https://github.com/MrElectrify/better_bitset/blob/master/benchmark/results.txt)

#### hash-maps-sets

##### CYBHash  `C++`  `no license`  `stale`  `Tier C`

Header-only bit-packing + BMI2 pext lookup for fixed-format Chinese futures/stock/option ticker symbols, vs std::unordered_map.

**Beats:** std::unordered_map — The README states CYBHash is 'approximately 10 times faster than std::unordered_map' for symbol-to-value lookup, while the repo's separate GitHub description says 'approximately 5-30 times faster' -- the two first-party figures disagree. testCYBHash.cc + test.sh do contain a real benchmark harness (bench_file_unordered_map alongside the symbol-table benches, run via g++ -std=c++17 -mbmi2 -O3 -DNDEBUG over bundled combine.txt/shfe.txt/stock.txt/dce.txt/option.txt files), but no output numbers, hardware, or compiler version tied to the README's claim are published anywhere in the repo.

**How:** Each fixed-length ticker string (5-16 bytes) is packed into a uint64 id via per-table bit-selection logic (get_id), then find_min_mask_by_cost greedily/bruteforce-searches for a small bit mask whose _pext_u64 (BMI2 pext instruction) extraction gives few collisions across the known key set. Lookups become one pext plus linear-probe over a flat vector<pair<id,value>>, skipping std::unordered_map's string hashing and bucket-chain traversal entirely. The idea is borrowed from qlibs/mph (pext-based hashing) and MengRao/str (fast fixed-size string keys, bundled as Str.h/StrHash.h though unused in the active benchmark path).

**Use it when:**
- Keys are exactly Chinese futures/stock/option ticker symbols (5-16 ASCII chars, e.g. '600000.SSE', 'eb2505-C-10000') that fit this project's packing rules
- The key set is known/stable before the hot lookup loop (build via sync_with_unordered_map() once, then read-only queries)
- Running on x86-64 hardware with BMI2 (pext) available
- Throughput on symbol->value lookup matters more than general-purpose map semantics
- You are prototyping/studying the technique rather than shipping it verbatim (no license to redistribute)

**Skip it when:**
- Any key format other than these narrow ticker patterns -- get_id()'s bit layout is hard-coded per table type, not a general string hash
- Keys are inserted/removed continuously; the design assumes a build-then-freeze workflow, not interleaved mutation
- Target platform lacks BMI2 (older x86, most ARM/aarch64) -- pext isn't available, and the code isn't portable around it
- You need a license to copy/redistribute the code -- no LICENSE file exists at the repo root
- You need verified performance numbers before adopting -- no benchmark output, hardware, or run data is published, and the project shows no CI, tests-as-assertions beyond ad hoc checks, or recent activity

**Vs siblings:** Only if your keys are literally these Chinese exchange ticker formats and you're willing to vendor unlicensed, unbenchmarked code for a niche win; for general string/integer key hashing, catalogued siblings like emhash, tsl::robin_map, or Verstable are general-purpose, actively tested, and (unlike CYBHash) carry reproducible benchmark data and clear licenses.

**Gotchas:**
- Symbol length is constrained to 5-16 characters; if length is 16 the last byte must be '0', otherwise sync_with_unordered_map() prints an error and calls std::exit(0)
- Table size is capped at 1<<MAX_BIT_SIZE (2^25) entries; sync returns false / prints 'table size too large' beyond that
- get_id() bit-packing differs per subclass (option/stock/stock6/future) and is specific to real Chinese exchange symbol formats (e.g. '.SSE'/'.SZE'/'.BSE' suffixes, 'eb2505-C-10000' style option codes) -- using it outside those formats gives undefined/garbage ids
- future_symbol_table's calculate_mask disallows id conflicts and can abort (exit(0)) if no collision-free mask is found within the search space

**Status:** Last commit 2025-03-14 with 10 stars; maintenance looks stale (no issues, PRs, releases, or CI found). Usability stays reference-only: GitHub reports license: null (no repo-root LICENSE file), even though CYB_Hash.h itself carries an inline MIT header (Copyright 2023 Chen Yibo) and the bundled StrHash.h/Str.h carry a separate inline MIT header (Copyright 2019 Meng Rao) -- the absence of a formal LICENSE file leaves redistribution rights ambiguous despite these in-file notices.

[repo](https://github.com/chenyibo1029/CYBHash) · [benchmark](https://github.com/chenyibo1029/CYBHash/blob/main/README.md)

#### number-parsing-formatting

##### fast_io  `C++`  `Anti-Tivo License (ATL) v1.0 (custom, non-OSI-approved)`  `active`  `Tier C`

Header-only C++20 I/O library replacing iostream/cstdio and std::to_chars with buffered, syscall-near I/O.

**Beats:** iostreams (std::fstream); std::to_chars (MSVC, for double formatting) — Author-run benchmarks (no CPU model or optimization flags stated) show fast_io's buffered file I/O beating std::fstream by roughly 6-15x for writing/reading 10 million integers on GCC 11 (Linux and MinGW-W64) and MSVC 19.26, and beating MSVC's std::to_chars(charconv) by about 23% (~1.29x throughput) for round-trip formatting of 10 million doubles, also on MSVC 19.26.

**How:** Devices are abstracted through C++20 concepts (static polymorphism), avoiding the vtable dispatch, locale machinery, and sentry-object overhead that <iostream>/streambuf carry on every call. I/O goes through the library's own buffered file objects close to the raw syscall/native-handle level rather than through libc FILE* layering. Integer formatting uses the jeaiii digit-pair method (include/fast_io_core_impl/integers/jeaiii_method.h, the same technique as the jeaiii/itoa sibling entry). Double round-trip formatting is implemented in include/fast_io_unit/floating/roundtrip.h, whose header comment attributes the algorithm to 'Dragonbox' (Jk Jeon) even though the readme's benchmark section calls it the 'Ryu algorithm' — these are different, related fast float-to-string algorithms.

**Use it when:**
- Bulk sequential file I/O (writing/reading millions of integers or lines) where std::fstream or stdio throughput is the bottleneck.
- Already on C++20 with a concepts-capable compiler (GCC>=14, Clang>=17, or MSVC per current support.md) and able to adopt a non-drop-in API.
- Low-level, embedded, kernel-driver, or freestanding/WASM targets that need direct handle/syscall-level I/O and small binaries (readme's static-link comparison: 155KB fast_io vs 925KB fstream).
- Need Unicode-aware (UTF-8/16/32) transcoding I/O in the same layer as raw throughput.
- Can accept the Anti-Tivo License's non-standard terms in exchange for the speed.

**Skip it when:**
- Need a true drop-in replacement for std::iostream or std::to_chars without touching call sites — fast_io's API shape and exceptions-only error model differ substantially.
- Legal review requires an OSI-approved permissive or conventional copyleft license — Anti-Tivo License v1.0 is custom and not OSI-approved.
- Toolchain can't reach the current minimum (GCC>=14/Clang>=17 per support.md), which is notably newer than the GCC 11/MSVC 19.26 used in the readme's own benchmark numbers.
- Need independently reproduced numbers before adopting — all published results are the author's own, with no CPU model or optimization flags stated, and the readme's cited benchmark paths no longer exist in the reorganized benchmark/ directory.
- Multithreaded writers by default — the fast unbuffered types are not thread-safe; the thread-safe *_mutex variants give up much of the speed edge (readme: 0.049s to 0.146s output time on MinGW for the mutex variant).

**Vs siblings:** Pick fast_io over Boost.Charconv, c4core, fast_double_parser, rigtorp/CharConv, or jeaiii/itoa when the goal is whole-file/stream I/O throughput via buffered file objects and syscall-near handles, not just isolated number<->string conversion — those siblings only replace to_chars/from_chars/stoi/strtod, while fast_io replaces the entire iostream/cstdio layer (and internally reuses jeaiii's itoa method for its own integer formatting).

**Gotchas:**
- readme's cited benchmark source paths (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) do not exist in the current repo; benchmark/ has been reorganized into numbered dirs (e.g. 0002.file_io_tsc, 0004.file_io_floating).
- readme calls the double round-trip formatting the 'Ryu algorithm', but the implementation header (include/fast_io_unit/floating/roundtrip.h) is commented 'Algorithm: Dragonbox, Author: Jk Jeon' — a different, related algorithm.
- MinGW benchmark numbers required the author to patch libstdc++'s BUFSIZ from 512 bytes to 1MB before comparing against fstream; the out-of-the-box gap on stock MinGW would be smaller.
- License is the custom Anti-Tivo License v1.0 (non-OSI-approved, GitHub reports it as NOASSERTION) — review it before shipping, it is not a standard permissive or copyleft license.

**Status:** Actively maintained (last commit 2026-07-02 on the 'next' branch, 2026-03-13 on master); usability is capped at 'reference' because of the non-OSI Anti-Tivo License, not because of code immaturity — 851 stars and an extensive examples/benchmark/fuzzing tree.

[repo](https://github.com/cppfastio/fast_io) · [benchmark](https://github.com/cppfastio/fast_io/blob/master/readme.md)

#### perfect-hash-static-tables

##### strager/perfect-hash-tables  `C++`  `CC-BY-NC-ND-4.0`  `abandoned`  `Tier C`

Research generator of CRC32-hashed perfect hash tables for 80 JS/TS keywords; beats gperf ~1.2-1.4x except on keyword-only input.

**Beats:** gperf — The author's dev log (notes.txt: rounded '~' figures, no raw output) gives time per benchmark iteration, where one iteration looks up every identifier in a ~287 KB corpus built from jquery-3.5.1.js. pht icrc32 + check1memcmp took ~69 us vs ~95 us for stock gperf 3.1 on non-keywords (~1.38x) and ~152 us vs ~188 us on mixed (~1.24x; ~1.21x vs gperf with inline strings), and only tied gperf on keywords-only. Builds are -O3 -std=c++20 with g++-12 or a local clang on Linux x86-64; notes.txt names no CPU or compiler for these figures, and the Ryzen 9 5950X appears only in its perf-stat section.

**How:** Stock gperf hashes with len + asso_values[s[0]] + asso_values[s[1]] + asso_values[s[len-1]]. The winning pht variant instead packs four selected bytes (first two and last two) into one 32-bit word and hashes it with a single SSE4.2 CRC32 instruction (_mm_crc32_u32). The generator brute-forces the seed and table size until all 80 keys land in distinct slots (a perfect hash: one probe, no collision chain); the --table-size=small search settled on 262 slots. A lookup rejects lengths outside 2..11, compares the first character, memcmps the rest, and checks the length by reading the NUL at entry_keyword[size], with keywords stored inline in 13-byte entries instead of gperf's default const char* pointers. Other variants try SIMD compares (SSE2 movemask, PTEST, PCMPESTRM, NEON), cmov-based branchless result selection, and AES, Lehmer-128, xxHash3, FNV-1a and Pearson hashers.

**Use it when:**
- You write a lexer and want to know how to beat gperf on a small fixed keyword set (here 80 keys of 2-11 bytes); read generate-pht.cpp and the committed generated/ outputs as a worked design study.
- Your lookups are mostly misses (identifiers that are not keywords). The length bounds check plus the first-character check rejected them fastest: ~69 us vs ~95 us for stock gperf on the non-keyword corpus.
- You target x86-64 with SSE4.2. The winning hasher is the CRC32 instruction, and the Makefile builds the icrc32 variants only on Linux x86-64.
- You want a ready harness that compares gperf options, frozen::unordered_map, std::unordered_map, binary/linear search and Rust phf on one key set, using Google Benchmark and perf stat.

**Skip it when:**
- Anything you ship or modify. LICENSE is CC-BY-NC-ND-4.0 and README says 'EDUCATIONAL USE ONLY', so commercial use and derivatives are not allowed.
- Keyword-heavy input. On the keywords-only corpus gperf was only 'competitive' with the best pht variant, so expect no win there.
- A plain memcmp compare. Every pht hasher with --string-compare=memcmp lost to gperf on all three corpora; the gain comes from the check1memcmp compare.
- Key sets that change at runtime or come from a file. Keys are compiled in from token.h, there is no insertion, and the generator exits with 'character selection is not unique' if the chosen characters do not tell the keys apart.
- Non-x86-64 or big-endian targets for the winning config. icrc32 needs the SSE4.2 CRC32 intrinsic, and pht.h has a FIXME noting that its 2-byte memcpy character load is endian-dependent.

**Vs siblings:** Pick this repo to learn why a gperf-class keyword table is fast or slow: it ablates hasher, character selection, table size and compare strategy against gperf 3.1 options and frozen::unordered_map on one workload. For code you can ship, use triehash (also benchmarked against gperf) or frozen (a constexpr C++ container API), after you check their licenses, because this repo forbids derivatives.

**Gotchas:**
- The SIMD compare variants (sse2, ptest, cmpestri, neon-mask-test) load 16 bytes, and chunk84 loads 12 bytes, from the input pointer whatever the key length. The harness pads every buffer by 32 bytes (padding_bytes in token.h). The check1memcmp winner reads only `size` input bytes.
- --no-early-bounds-check read past the end of the table through entry_keyword[size] (issue #1). It is safe only together with --keyword-size-in-entry, which is how the Makefile pairs them.
- The 'gperf --inline-strings' baseline is not a stock gperf 3.1 option. The Makefile strips the flag and defines GPERF_INLINE, which changes token.gperf's struct to inline char arrays. mygperf is a Python post-processor of gperf's tables with the author's compare code.
- Source files carry GPL-3.0-or-later 'part of quick-lint-js' headers, while README and LICENSE say CC-BY-NC-ND-4.0, and issue #3 about licensing is still open. Treat the code as read-only reference.

**Status:** Abandoned since 2023-03-12 (not archived, 2 open issues) and licensed CC-BY-NC-ND-4.0 'EDUCATIONAL USE ONLY', so read it rather than vendor it; the author's maintained GPL-3.0 descendant of the technique is quick-lint-js's tools/generate-lex-keyword.cpp, which hashes the first two and last two characters with a multiply-shift into a power-of-two table.

[repo](https://github.com/strager/perfect-hash-tables) · [benchmark](https://github.com/strager/perfect-hash-tables/blob/master/notes.txt)

#### searching

##### simdsearch (Needle-Hammer)  `C++`  `no license`  `active`  `Tier C`

Header-only SIMD substring search with a linear-time worst-case fallback; ~30x libc memmem on Apple M-series.

**Beats:** memmem (platform libc; the headline figure is on an Apple M-series core) — The README claims about 45 GB/s substring-search throughput on an unnamed Apple M-series core, roughly 30x the platform's libc memmem, measured on ordinary text at memory speed. The repo's own benchmark/README.md notes Apple's memmem 'uses a much simpler scan and lands well behind strstr,' so the 30x figure is against a weak platform baseline, and the top-level README tells readers to reproduce numbers on their own machine rather than publishing a results table for this specific claim.

**How:** Needle-Hammer picks 2-4 selective bytes from the needle as anchors and SIMD-filters 256 haystack positions per AVX-512 iteration (64 on NEON) against them, narrowing survivors byte by byte. A per-call work counter caps how much filtering it does; once the budget is spent on adversarial input it hands off to a Crochemore-Perrin two-way search, so every call stays O(n+m) instead of degrading like an unguarded anchor filter.

**Use it when:**
- Substring/byte search over ordinary text or binary data on x86-64 with AVX-512F+BW, or any AArch64 core (NEON is architectural there)
- Throughput-bound scanning (log grepping, large-buffer search) rather than a single short lookup, since the design targets memory-speed scanning
- You can tolerate adversarial-input inputs falling back only to two-way's O(n+m), not needing sublinear worst-case behavior
- You can vendor a header-only, dependency-free library and compile per target machine (a checked-in single header and single-header releases exist)
- You need byte-exact, NUL-safe, non-UTF-8-aware search rather than a character-aware routine

**Skip it when:**
- Shipping one binary to x86-64 machines with unknown/mixed CPUs — there is no runtime dispatch; a CPU without AVX-512F+BW hits an illegal instruction
- Targeting mainstream x86-64 client parts (most Intel client chips have AVX-512 fused off, pre-Zen4 AMD lacks it) or 32-bit/RISC-V/POWER, all unsupported
- Building with MSVC — unsupported, since the headers use GCC/Clang builtins and attributes
- Needing a licensed dependency for production use — the repo ships no LICENSE file
- Wanting a published, apples-to-apples comparison against std::search or std::string::find — the benchmark driver includes both but no numbers for them are in the README

**Vs siblings:** The catalogued siblings (sb_lower_bound, scandum/binary_search, SIMD Quad search, FastBinarySearch) all accelerate binary search over sorted arrays; simdsearch instead accelerates unsorted substring/byte search, i.e. memmem/strstr territory. Pick it when the task is finding a byte pattern inside a buffer, not locating a key in an already-sorted sequence.

**Gotchas:**
- No runtime CPU dispatch: an AVX-512-compiled binary executes illegal instructions on hardware without AVX-512F+BW; the caller must detect the CPU and keep a fallback path itself
- find_unguarded skips the work-counter guard entirely (a few percent faster on ordinary text) but reverts to O(n·m) worst case; documented as safe only on input the caller controls
- Tuning constants (NH2_START_ANCHORS, NH2_BUDGET_DEN, etc.) were fitted on Emerald Rapids, Zen 5 and Apple M4 Max; the README says you shouldn't need to touch them but does not claim they are optimal on other hardware
- No LICENSE file anywhere in the repo, so there is no stated legal basis for use, modification, or redistribution

**Status:** Active: created 2026-07-28, last commit 2026-09-21, with one merged PR already fixing kernel correctness issues, but it is a brand-new, single-contributor project (9 stars, no LICENSE file), so treat it as reference material rather than something to depend on directly.

[repo](https://github.com/lemire/simdsearch) · [benchmark](https://github.com/lemire/simdsearch#readme)

#### serialization-json

##### Tachyon.JSON v6  `C++`  `Proprietary (TACHYON PROPRIETARY SOURCE LICENSE v1.0; LICENSE file allows free personal/commercial use but forbids redistribution of source, sub-licensing, and modifying the ASM/SIMD kernels)`  `active`  `Tier C`

Single-header AVX2 JSON parser under a proprietary license; benchmarks nlohmann/simdjson but times only its structural-bitmask build, not full parsing.

**Beats:** nlohmann::json (also compared against simdjson and Glaze) — README claims Tachyon's parse_view() (builds only a structural bitmask index, no value materialization) reaches 4,577 MB/s on a 25MB in-memory generated array and 5,585 MB/s on canada.json, vs simdjson's ondemand parser.iterate() at 1,886/3,541 MB/s (~2.4x/~1.6x) and nlohmann::json's full json::parse() DOM build at 25/31 MB/s (~183x/~180x), built with g++ -std=c++23 -O3 -march=native -flto (compiler version unstated) on an unspecified Intel Xeon (Haswell). The harness runs 1000 iterations for Tachyon and simdjson, 100 for Glaze, and only 10 for nlohmann, despite the README stating a uniform 'median of 1000 iterations'.

**How:** The structural scan (SIMD::compute_structural_mask) loads 128 bytes at a time into four 256-bit AVX2 registers, uses a PSHUFB (_mm256_shuffle_epi8) nibble lookup table to classify bytes as quote/backslash/structural in one pass, and derives a per-32-byte token-boundary bitmask with _mm256_movemask_epi8. String/escape state is tracked with a branchless XOR-prefix-sum over the quote bitmask rather than a byte-by-byte state machine, falling back to a scalar loop only when a chunk contains a backslash. Because parse_view() stops at building this index and never allocates or decodes individual values, the benchmarked 'parse' step skips the DOM construction that nlohmann, simdjson OnDemand, and Glaze all pay for in the same loop -- which accounts for most of the measured gap.

**Use it when:**
- Read-heavy code that only probes a few keys/values from a large document via Cursor-based lazy lookup and never needs a materialized DOM
- x86-64 deployments where AVX2 is guaranteed and build flags can be tuned per machine (e.g. -march=native)
- Studying/benchmarking a PSHUFB structural-classification + branchless quote-escape-bitmask technique, given the license blocks reusing the code itself
- Data that is only integers, strings, and booleans -- no fractional numbers anywhere in the document
- Throwaway internal tooling where a 0-star, single-maintainer, unlicensed-for-redistribution header is acceptable

**Skip it when:**
- Any JSON containing floating-point values: materialize() and the lazy number accessor both parse bare numbers as int64_t via std::from_chars, so "3.14" silently becomes 3, and dump() has no serialization case for the double variant (a json built from a double prints the literal string "null")
- Anything needing portability: the scan hard-requires AVX2 (_mm256_* intrinsics) with no scalar fallback and no runtime CPU dispatch like simdjson's -- it won't build/run on non-AVX2 x86 or ARM
- Commercial or open-source products you need to redistribute, fork, or modify -- the TACHYON PROPRIETARY SOURCE LICENSE v1.0 forbids redistribution and forbids modifying the ASM/SIMD kernels
- CBOR or MessagePack support -- from_cbor()/from_msgpack() are stubs that throw std::runtime_error
- Trusting the throughput numbers as apples-to-apples: the README times Tachyon's index-only parse_view() against nlohmann's/simdjson's/glaze's full value decode, runs nlohmann for only 10 iterations vs 1000 for Tachyon/simdjson (README claims uniform 'median of 1000') and has no CPU model, compiler version, or public CI run behind the numbers

**Vs siblings:** Rarely: the catalogued siblings (cjson.cpp, json.cpp, DAW JSON Link, utl::json) all measure the same operation on both sides of their comparison and ship under permissive licenses. Tachyon's index-only benchmark isn't measuring the same thing as a full nlohmann/simdjson parse, and its DOM path silently mangles floating-point data, so pick it only to study the AVX2 structural-bitmask/PSHUFB technique in isolation -- not for production parsing, redistribution, or any dataset with fractional numbers.

**Gotchas:**
- Materializing to DOM (or calling as_int64() on any lazy node) parses every bare number as int64_t via std::from_chars, silently truncating fractional values (3.14 -> 3); there is no reachable path that produces a double from parsed text
- json::dump() has no case for the double variant -- a json constructed from a C++ double (e.g. json(3.14)) serializes to the literal string "null"
- No scalar/fallback path for non-AVX2 hardware: compute_structural_mask and skip_whitespace assume 256-bit AVX2 registers are available at compile time
- from_cbor()/from_msgpack() exist as API stubs and always throw std::runtime_error("... not fully implemented")

**Status:** Repo history spans only 2026-01-02 to 2026-01-04 (created and last pushed within days of each other), 0 stars, and the proprietary license permits free use but forbids redistribution, forking, or modifying the SIMD kernels -- reference/study-only despite counting as 'active' under a 12-month recency rule.

[repo](https://github.com/mrcodechef/Tachyon.JSON) · [benchmark](https://github.com/mrcodechef/Tachyon.JSON)

#### small-buffer-and-strings

##### zuu_string_view  `C++`  `no license`  `active`  `Tier C`

Header-only C++11 SWAR-accelerated string_view alternative; faster find/rfind/find_first_of than std::string_view, slower on not_of scans.

**Beats:** std::string_view — README's first-party Google Benchmark table (one ~95-char haystack, compiler/flags/stdlib unstated, hardware reported only as '12x 2096 MHz CPU') shows zuu::string_view beating std::string_view on find_first_of (6.11 vs 15.7 ns, ~2.5x), find/substring (11.1 vs 14.1 ns), rfind/substring (11.4 vs 16.7 ns), find_last_of (11.0 vs 14.7 ns), and find/char (1.56 vs 2.24 ns), while std::string_view wins on find_first_not_of (5.01 vs 6.22 ns) and find_last_not_of (5.00 vs 6.82 ns).

**How:** The positive-search functions (find, rfind, find_first_of, find_last_of) use SWAR (SIMD-within-a-register): they memcpy 8 bytes at a time into a uint64_t 'tape', broadcast the needle byte(s) across all 8 lanes, XOR against the tape, and apply the classic branchless haszero/hasless byte-detection trick (0x7F7F...7F and 0x8080...80 masks) plus count_trailing_zeros/count_leading_zeros to locate the matching byte in one shot instead of a per-byte loop. Multi-char searches (find_first_of family) extend this with a 256-bit bitmap built from 4 uint64_t lookup words. This path only triggers for sizeof(CharT)==1 outside constexpr evaluation; everything else falls back to a scalar loop.

**Use it when:**
- Hot-path find/rfind/find_first_of/find_last_of/find(char) calls over ASCII/byte strings (README's own test string is ~95 chars) where a few nanoseconds per call matters
- C++11-only codebases that want string_view-style ergonomics without raising the language standard
- Header-only vendoring is acceptable: just include/zuu/string_view.hpp + include/zuu/char_class.hpp, no build step
- Single-threaded or read-only-shared usage (it's a raw pointer+length pair with no internal synchronization)
- Data provably under ~4 billion characters, since length is stored as a 32-bit unsigned int

**Skip it when:**
- find_first_not_of / find_last_not_of-heavy code: the README's own numbers show zuu 20-26% slower than std::string_view there
- Buffers that could exceed ~4B characters, or code that assumes std::string_view's std::size_t-typed npos/return values
- wchar_t/char16_t/char32_t workloads or constexpr contexts: the SWAR path is disabled there (sizeof(CharT)==1 and non-constexpr only), so performance likely reduces to the scalar fallback, which is unbenchmarked
- Projects that need a licensed dependency to ship: no LICENSE file and no license field in vcpkg.json
- Teams wanting proven maturity: repo created 2026-09-11, all 30 commits land within about a day, 0 stars, 0 issues, no third-party validation

**Vs siblings:** It's the only catalogued entry benchmarked against std::string_view itself (the other siblings target std::string/std::to_string), so pick it specifically when your bottleneck is string_view::find-family calls on a C++11 toolchain; for std::string construction/formatting/conversion speedups, use FastString, to_static_string, or Str instead.

**Gotchas:**
- size_type and npos are `unsigned int` (32-bit), not std::size_t like std::string_view — a real interop gap, not just a naming difference
- The SWAR fast path only activates when sizeof(CharT)==1 and outside constexpr evaluation; wide-char types and constexpr calls silently use the scalar loop instead
- find_first_not_of and find_last_not_of are slower than std::string_view (20-26% per the README), the opposite of the library's headline claim
- No LICENSE file and no license field in vcpkg.json, so legal usability is unresolved even though the source is public

**Status:** Actively developed as of the last commit (2026-09-12) but very early: v0.4.0, all 30 commits landed within about a day of creation (2026-09-11), 0 stars, and no LICENSE file, so treat it as unlicensed and unproven rather than production-ready.

[repo](https://github.com/zuudevs/zuu_string_view) · [benchmark](https://github.com/zuudevs/zuu_string_view)

#### smart-pointers-and-refcount

##### Delegate (bdiamand/Delegate)  `C++`  `Custom permissive notice in the delegate.h header (not an OSI-approved license; no LICENSE file)`  `abandoned`  `Tier C`

Fixed-size, heapless C++17 delegate beating std::function's invocation speed by 1.1-1.4x in a third-party benchmark.

**Beats:** std::function — On MSVC 15.9.4 (Visual Studio, 64-bit Release, Boost 1.69.0, CPU unspecified) in jamboree/CxxFunctionBenchmark's various.cpp, Delegate beat MSVC STL's std::function in all 7 invocation categories (e.g. function_pointer 0.210s vs 0.264s, ~1.26x; compile_time_function_pointer 0.132s vs 0.188s, ~1.42x), and was the fastest of 13 implementations in 5 of 7 categories (stdex::function and func::function tied or edged it out in heavy_functor and lambda_capture).

**How:** Never allocates: captured state is stored inline in a fixed-size aligned byte buffer (default 12 bytes, resizable via DELEGATE_ARGS_SIZE macro), so there is no heap round-trip on construction, copy, move, or destruction. Dispatch uses a raw function pointer plus a small static per-type vtable (copy/move/destroy) built once via templates, avoiding the extra indirection and RTTI/exception bookkeeping std::function implementations carry. No dynamic memory management and no exception-safety machinery to execute on the hot call path.

**Use it when:**
- Callback/handler slots where the callable's capture state is small and known ahead of time (fits in ~12-20 bytes, adjustable via DELEGATE_ARGS_SIZE)
- Hot paths that construct/copy/destroy callables frequently and need to avoid heap allocation and its jitter
- Embedded or latency-sensitive code that wants predictable, allocation-free memory behavior
- Code that already avoids RTTI/exceptions and does not need std::function's arbitrary-size type erasure
- Move-only captures (e.g. unique_ptr) via the MoveDelegate variant, where std::function historically disallows or complicates this

**Skip it when:**
- Captures larger than the fixed buffer size — code fails to compile (static_assert), unlike std::function's silent heap fallback
- Codebases that rely on std::function's RTTI/exception interplay or allocator-aware construction
- Projects needing an OSI-approved license: this ships a custom permissive header notice, not MIT/Apache/BSD
- Long-term maintenance risk: repo has been inactive since 2022-07-27 and only 43 stars
- Multi-threaded use without external synchronization — no thread-safety guarantees are documented or implemented

**Vs siblings:** Pick Delegate over stdext::inplace_function or SmallFunction when you want the smallest reported invocation times in this same benchmark suite for pointer/lambda-heavy call patterns; pick stdext::inplace_function instead if you need an OSI-approved (SG14/Boost-style) license, since Delegate's license is a non-standard permissive notice.

**Gotchas:**
- Default capture buffer is only sizeof(int)+sizeof(int*) (12 bytes on typical 64-bit builds), plus 8 bytes of vtable/call-pointer overhead; override via #define DELEGATE_ARGS_SIZE / DELEGATE_ARGS_ALIGN before including the header if captures don't fit
- Copying a Delegate built from a non-copyable functor calls std::terminate() at runtime rather than failing to compile (only FuncCopyable's copy path is affected; use MoveDelegate to avoid this class of captures entirely)
- No exception awareness at all — the header does not catch or propagate exceptions from the wrapped callable differently than a normal call would
- No LICENSE file; licensing is a custom notice embedded in the delegate.h comment block requiring the comment block to remain in derived works

**Status:** Abandoned since the last commit on 2022-07-27; usability is 'reference' because the custom header license is not OSI-approved, though the code is small (~350 lines) and easy to vendor or re-license by copying and adapting.

[repo](https://github.com/bdiamand/Delegate) · [benchmark](https://github.com/jamboree/CxxFunctionBenchmark#sample-result)

### storage-and-data

#### caches

##### Dragonfly  `C++`  `BUSL-1.1`  `active`  `Tier C`

Multi-threaded, shared-nothing in-memory store that speaks the Redis and Memcached protocols; beats single-process Redis once there are many cores.

**Beats:** Redis, Memcached — Vendor memtier_benchmark runs on AWS (instance types only; no CPU model, compiler, flags or baseline versions, and no published harness) show parity with single-threaded Redis on m5.large, about 1.4-1.5x on m5.xlarge, and 3.8M QPS on c6gn.16xlarge, which is the '25x a single Redis process' headline. The same runs show Memcached at 806K SET and 2.1M GET QPS against Dragonfly's 3.84M and 3.72M. Redis's 2022 rebuttal on the same instance, using a 40-shard Redis 7.0 Cluster, measured 18-40% more throughput than Dragonfly (GET pipeline 1: 4.43M vs 3.8M reproduced). tidwall's suite on ARM64 c8g.8xlarge with Dragonfly 1.30.3 gives mixed results: At pipeline 1, Dragonfly beats Redis 8.2.1 on GET at 2 and 10-16 threads, loses at 1 and 3-8 threads, and loses to Memcached on GET in every configuration.

**Known shortcoming:** The 25x is against a single-threaded Redis process; Redis's 2022 rebuttal ran a 40-shard Redis cluster on the same c6gn.16xlarge and got 18-40% more throughput than Dragonfly. In the tidwall cache-benchmarks suite Redis wins at 8 threads, Dragonfly leads ~2.2x only at 16 threads, and memcached wins GET in every config. BUSL-1.1 licence (not OSI) (verifier downgrade).

**Known shortcoming:** On few cores it ties or loses: about equal to Redis on m5.large; in the tidwall suite Redis 8.2.1 wins at 1 and 3-8 threads and Dragonfly only leads at 16 threads (2.94M vs 1.32M). memcached beats it on GET in every tidwall config, Pogocache in every config and Garnet in all but two. Deep pipelines are weak (1-thread GET p99 ~289 ms vs Redis ~15 ms). BUSL-1.1 forbids hosted/managed services and embedding in in-memory store products (becomes Apache-2.0 on 2030-11-01 or 4 years after release). Compatibility gaps: no SCRIPT KILL (#8269), no Redis 8.10 RDB v15 (#8361), EXEC not atomic under maxmemory (#8275), Lua undeclared keys blocked by default, cluster needs an external manager. Needs >=256 MB per thread or exits; PEXPIRE above 2^28 ms rounds to 1 s; HTTP console on port 6379; a 2026 advisory fixed an unauthenticated heap overflow in the memcached reply builder.

**How:** It uses a shared-nothing, thread-per-core design built on the helio fiber library, with io_uring by default and epoll on kernels older than 5.10. Each thread owns one shard of the keyspace, and cross-shard work goes by message passing instead of locks. Multi-key atomicity uses the VLL lock-manager scheme from the VLDBJ paper. The main index is Dashtable, an implementation of Dash (extendible hashing): a directory of fixed-size open-addressed segments of 56 buckets plus 4 stash buckets, 14 slots per bucket. Lookups compare 8-bit fingerprints with one SSE2 compare per bucket (sse2neon on aarch64). Growth splits one segment at a time instead of rehashing the whole table. Per-bucket version counters in the table metadata are what make fork-less point-in-time snapshots possible. The same bucket layout drives cache-mode eviction: items are bumped toward the front of their bucket, and the last slot of a stash bucket is evicted.

**Use it when:**
- A single large multi-core box (16+ vCPUs) where you would otherwise run many Redis shards or a Redis Cluster, and you want one endpoint where MULTI/EXEC, Lua and multi-key commands keep single-node semantics.
- Unpipelined GET/SET at high server thread counts. In tidwall/cache-benchmarks (c8g.8xlarge, 16 server cores, pipeline 1) Dragonfly did about 2.9M GET/s against 1.3M for Redis 8.2.1 with io-threads.
- Write-heavy Memcached-protocol traffic on a big instance. On c6gn.16xlarge the vendor measured 3.84M SET/s against 806K for Memcached.
- Large datasets that snapshot often, where the copy-on-write memory spike from Redis fork is the problem. In the vendor's 5 GB BGSAVE test Redis peaked at about 3x Dragonfly's memory.
- Many small keys where per-key overhead dominates. The Dashtable doc estimates 6-16 bytes of table overhead per item against 16-32 for the Redis dict. It measured 20M keys at 1 GB versus 1.73 GB on Redis 6.

**Skip it when:**
- Small instances or few threads. On a 2-vCPU m5.large the vendor itself shows parity with Redis (GET 191K vs 194K). In tidwall's pipeline-1 runs Redis 8.2.1 with io-threads beat Dragonfly on GET at 1 and 3-8 threads (for example 1.51M vs 1.41M at 8).
- As a read-heavy Memcached replacement. Memcached 1.6.38 posted higher GET throughput than Dragonfly in every tidwall configuration, and in the vendor's own table Memcached had the lower GET p99 (0.34 ms vs 1 ms).
- Deep pipelining. At pipeline 10-50 on 16 threads, Garnet and Pogocache did roughly 3-4x Dragonfly's GET throughput in tidwall's runs. At pipeline 50 on 1 thread, Dragonfly's GET p99 was about 289 ms against about 15 ms for Redis.
- Offering it as a hosted or managed service, or embedding it in an in-memory data store product. The BUSL-1.1 Additional Use Grant forbids both. Each version converts to Apache-2.0 on 2030-11-01 or four years after its release, whichever comes first.
- Setups that need recent Redis features or files, or that let untrusted clients run EVAL. It cannot load the RDB v15 format from Redis 8.10 (#8361; the maintainer says it supports formats up to Redis 7). There is no SCRIPT KILL or lua-time-limit, so one infinite Lua script pins a thread until kill -9 (#8269). Cluster mode has no gossip protocol and needs an external cluster manager.

**Vs siblings:** Pick Dragonfly over Pogocache, Pelikan/Segcache or Garnet when you need broad Redis data types and commands, replication, snapshots and single-node multi-key atomicity on one big box, not just raw GET/SET cache throughput. In tidwall's suite Pogocache beat it on GET in every configuration, and Garnet beat it in all but two configurations, by about 3x under pipelining. Against KeyDB, both are multithreaded Redis alternatives; Dragonfly is the actively released one (v2.0.0 on 2026-09-16), but its license is BUSL-1.1.

**Gotchas:**
- maxmemory defaults to 80% of detected memory, and the server exits at startup if maxmemory is below 256 MB per proactor thread.
- Lua scripts that touch undeclared keys fail by default. Allowing them (default_lua_flags=allow-undeclared-keys) runs the script as a GLOBAL transaction that locks every shard.
- PEXPIRE/PSETEX deadlines above 2^28 ms (about 3.1 days) are silently rounded to the nearest second. Expiries are capped at about 8 years, strings at 256 MB, and hash-field TTLs have 1-second precision.
- An HTTP console and /metrics are served on the main 6379 port by default; disable with --primary_port_http_enabled=false if the port is exposed. Several 2026 advisories include an unauthenticated heap overflow in the memcached reply builder (GHSA-9q98-cx72-pg45), so stay on current releases.

**Status:** Very active (v2.0.0 released 2026-09-16, last push 2026-09-26, about 31.7k stars) and production-positioned. It is a BUSL-1.1 source-available server, not a library, so evaluate the license and a few days of your own workload (as the FAQ advises) before replacing Redis.

[repo](https://github.com/dragonflydb/dragonfly) · [benchmark](https://github.com/dragonflydb/dragonfly#benchmarks)

##### EloqKV  `C++`  `GPL-2.0-only OR AGPL-3.0-only`  `active`  `Tier C`

Multi-threaded Redis-API distributed KV database with ACID transactions; vendor benchmark shows about 4.5-8.5x single-threaded Redis throughput.

**Beats:** Redis — EloqData's own August 2024 post (now only on the Wayback Machine) tested EloqKV 0.7.4 with WAL and data store off against Redis 7.2.5 (persistence off, no io-threads) and DragonflyDB 1.21.2. Server: one AWS c7g.8xlarge Graviton. Client: memtier_benchmark on a c6gn.8xlarge. Workload: 128-byte values, 5M keys, 128-1024 connections, 300 s runs. Read by eye from the charts, Redis stays near 200K ops/s while EloqKV rises from about 950K to 1.7M ops/s (roughly 4.5-8.5x), and at 1024 connections P999 is about 3 ms for EloqKV versus 11-12 ms for Redis. No compiler or build flags are given, and the page itself says Redis would normally run as a multi-instance cluster on such a machine.

**Known shortcoming:** First-party benchmark in which Redis ran without io-threads; chart values are approximate. The tx_service core is BSL-licensed (usability mixed).

**Known shortcoming:** LICENSE CHANGE: the required data_substrate core moved from GPL/AGPL to BSL 2.0 on 2026-01-27 (non-production, non-commercial use only until 2031), so a source build is not production-usable without a commercial agreement. Benchmark is a vendor 2024 v0.7.4 run (Wayback copy) read off charts; Redis single-threaded without io-threads; Dragonfly slightly faster.

**Known shortcoming:** 178 commands at HEAD (no Streams/HLL/Geo/RENAME/COPY/RESP3/Functions/SCRIPT KILL). Default eloqkv.ini has enable_wal=off (not durable out of the box) and one replica (no auto-failover). Open bugs: MULTI aborts on first error (#502), no Lua timeout (#507), replay TTL/key-length bugs (#503/#504/#498), Jepsen stall (#188). Linux only; io_uring default needs --privileged in Docker.

**How:** It uses a thread-per-core, shared-nothing design. Keys are partitioned (Redis CRC16 hash slots) into one CcShard per core, and each shard is driven by one TxProcessor. Work for another shard is passed to that shard as a message, not done under a lock, so each shard's state has a single writer. With external processing on (the CMake default), brpc worker N runs the processing round for shard N, so a command can be parsed and executed on the same worker without a thread hand-off. Each shard also allocates from its own mimalloc heap. Networking uses io_uring by default; the 2024 benchmark post said io_uring networking was missing then and that EloqKV was bound by the network stack. The margin over Redis comes mostly from using all 32 vCPUs where Redis runs commands on one thread.

**Use it when:**
- You want one large multi-core Redis-API node instead of running a Redis Cluster, and the traffic is mostly simple string, hash, list, set or sorted-set commands. The benchmark used 128-byte values, 5M keys and 128-1024 connections.
- You need real multi-key atomicity: BEGIN/COMMIT/ROLLBACK sessions, MULTI/EXEC that rolls back on error, or Lua scripts that read and create keys across nodes without hash-tag co-location.
- You want Redis-API data that survives power loss (WAL on) and can be larger than RAM, with cold data on local disk or object storage. A metadata store is a better fit than a throwaway cache.
- You run on Linux x86-64 or ARM64 (the benchmark host was Graviton) and can use the Ubuntu 24.04 release tarballs or a privileged Docker container.

**Skip it when:**
- Production or commercial use of a build from this repo without a deal with EloqData. On 2026-01-27 the required data_substrate/tx_service submodule moved from GPLv2/AGPLv3 to a 'Business Source License 2.0' text. That license allows only non-production, non-commercial use until the 2031-01-08 change date.
- Apps that need commands with no handler registered in src/redis_service.cpp at HEAD: Streams (XADD), HyperLogLog (PFADD), Geo, RENAME, COPY, OBJECT, WAIT, TOUCH, RANDOMKEY, FUNCTION/FCALL, BZPOPMIN/BZPOPMAX and HELLO (so no RESP3). The vendor compatibility page also marks ACL users, CLIENT TRACKING, MONITOR and SCRIPT KILL as unsupported.
- Pure in-memory cache throughput is the only goal. In EloqData's own test DragonflyDB was slightly ahead on every workload, with lower P999 latency on the read-only and mixed runs.
- Code that depends on exact Redis semantics. On the first runtime error, MULTI/EXEC aborts the whole transaction (#502). OCC conflicts make MULTI and Lua re-run from the start, so a PUBLISH inside a script can be delivered twice (#500). Pub/Sub is best-effort, process-local plus forwarding, and not scoped by namespace (#499).
- You need proven HA and correctness under faults. The shipped eloqkv.ini says node_group_replica_num currently supports only 1, which means no automatic failover. An internal Jepsen run that ended with no responsive nodes is still open (#188).

**Vs siblings:** Pick EloqKV over Dragonfly, Valkey or KeyDB when you need ACID BEGIN/COMMIT/ROLLBACK, cross-node transactions without hash tags, or durable larger-than-RAM data behind the Redis API. For a pure in-memory cache, Dragonfly was slightly faster than EloqKV even in EloqData's own benchmark.

**Gotchas:**
- The shipped eloqkv.ini sets enable_wal = off, so a default install is not durable even though durability is the headline feature. The README's docker-compose example turns it on with -enable_wal=true.
- Lua has no time limit and there is no SCRIPT KILL, so one infinite EVAL pins a worker and holds its locks indefinitely (#507). Scripts are also re-run in full on OCC conflicts.
- The EVALSHA script cache is per process and not replicated, so EVALSHA must reach a node that has already seen the script body.
- Open replay and serialization bugs filed in June 2026: SET ... KEEPTTL loses the TTL on WAL replay (#504); SET over a non-string key stores an empty value on replay paths (#503); keys are serialized with a uint16 length although MAX_KEY_SIZE allows 32 MB (#498).

**Status:** Actively developed (release 1.3.8 on 2026-09-09, nightly builds, last push 2026-09-17, 1.5k stars), but usability is mixed. The Redis layer is GPLv2 or AGPLv3, while the mandatory Data Substrate core is BSL 2.0 limited to non-production use until 2031. The benchmarked 0.7.4 is two years older than current builds.

[repo](https://github.com/eloqdata/eloqkv) · [benchmark](http://web.archive.org/web/20260616115015/https://eloqdata.com/blog/2024/08/17/benchmark-single-node)

##### W-TinyLFU (C++ header-only, based on the TinyLFU paper)  `C++`  `reference (no LICENSE file in vimpunk/w-tinylfu)`  `abandoned`  `Tier C`

Small C++ header-only W-TinyLFU cache: frequency-sketch admission in front of segmented LRU, for higher hit ratios than plain LRU.

**Beats:** LRU — This C++ port has no benchmark of its own. The only evidence is hit-ratio plots in the TinyLFU paper (arXiv 1512.00727v2), which the authors produced with a Java prototype and with Caffeine 2.0 on Zipf 0.7/0.94, SPC1-like and real traces. There, W-TinyLFU with a 1% window tied or beat LRU, ARC and LIRS on most traces, but OLTP, F1 and F2 needed a 20-40% window, which this port cannot configure. Hit ratio does not depend on hardware, and no compiler, hardware or throughput figures exist for this code.

**Known shortcoming:** 'Best on every trace' is overstated: the default 1% window loses on OLTP/F1/F2 traces (needs 20-40%); the ~89% figure is memory saved vs a strawman sketch, not a gain over LRU. No licence (reference only), last commit 2018-10, not thread-safe (verifier downgrade).

**Known shortcoming:** No benchmark of its own; hit-ratio figures come from the paper (Java prototype and Caffeine). The window is fixed at 1% with no adaptation, while the paper's OLTP/F1/F2 traces needed 20-40%. Not thread-safe, no HashDoS guard (issue #1 open since 2017), abandoned 2018.

**Known shortcoming:** The frequency sketch hashes raw key bytes, so std::string or padded keys hash wrongly and admission quietly degrades. From code reading (not run): capacity 1 and change_capacity shrinking hit UB on an empty probationary list; 1L/0xfL shifts are UB where long is 32-bit (Windows). README says C++11 but a constexpr loop needs C++14; missing <cstdint> etc. may break GCC 13+. No LICENSE file, but every header carries an MIT-style notice.

**How:** The gain is in hit ratio, not per-operation speed. A count-min sketch of 4-bit counters (four counters per key, packed sixteen to a 64-bit word, following Caffeine) estimates each key's recent frequency. Once about 10x capacity increments have been recorded, every counter is halved (the paper's 'reset' aging). New keys go into an LRU window sized at 1% of capacity. The window's LRU victim is admitted into a 99% segmented LRU (80% protected, 20% probationary) only if its estimated frequency is strictly higher than that of the probationary segment's LRU victim; otherwise the newcomer is dropped. Each get() pays a std::map lookup, a std::list splice, four sketch increments and a shared_ptr copy, so it costs more per call than a hand-rolled LRU. A Bloom-filter 'doorkeeper' header ships in the repo but is not wired in.

**Use it when:**
- Single-threaded, or externally locked, in-process C++ object caches where plain LRU loses hit ratio to scans or to skewed (Zipf-like) traffic full of one-time keys.
- Keys that are integers or padding-free POD ids. The sketch hashes the key's raw bytes, so only these keys hash consistently.
- Expensive or large values (the repo's test caches 4 KB objects), where each extra hit is worth more than the policy's per-operation overhead (map lookup, list splice, sketch updates), and where returning shared_ptr keeps an evicted value alive while a caller still uses it.
- As a readable reference (under 900 lines across four headers, including license text) to vendor and harden when you need W-TinyLFU in C++ and cannot use the JVM.
- Frequency-skewed workloads like the paper's search-engine, DS1 and SPC1-like traces, where the fixed 1% window tied or beat LRU, ARC and LIRS.

**Skip it when:**
- Multithreaded access without your own lock. Even get() mutates the LRU order and the sketch, and a single global mutex serializes every operation.
- Recency-heavy or 'sparse burst' workloads such as the paper's OLTP, F1 and F2 traces, which needed a 20-40% window. This port hard-codes a 1% window and an 80/20 split, with no hill-climbing adaptation of the kind Caffeine now does.
- Untrusted or adversarial keys. There is no HashDoS protection: Caffeine's random admission of 'warm' candidates is missing, and issue #1 has been open since 2017.
- std::string keys, or structs with pointers or padding. Equal keys hash differently, so admission decisions silently degrade.
- Windows/MSVC builds, caches bounded by bytes or needing expiry, or latency-critical hot paths. Every insert does three heap allocations (std::map node, std::list node, make_shared block) and stores two copies of the key, and no throughput benchmark exists.

**Vs siblings:** On the JVM, use Caffeine: it is the canonical W-TinyLFU, with an adaptive window, HashDoS jitter and concurrency. For offline trace studies, libCacheSim (SIEVE's repo) already ships WTinyLFU.c next to SIEVE, LRU and ARC. Pick this one only when you want a tiny dependency-free C++ W-TinyLFU object to embed in a single-threaded component with integer keys and are prepared to fix its edge cases. If you mainly need a simpler, better-than-LRU C++ policy, SIEVE or LHD have stronger evidence.

**Gotchas:**
- The sketch hashes the key's raw object bytes (Jenkins one-at-a-time over reinterpret_cast<const char*>(&key)), not std::hash. For std::string, or any key holding pointers or padding, the caller's key and the cache's stored copy can hash differently, so frequency comparisons turn into noise and nothing reports it.
- Capacity edge cases (found by reading the code, not by running it): with capacity 1 the main SLRU gets 0 slots, and the second insert reads the victim of an empty probationary list, which is undefined behavior. Shrinking with change_capacity() can hit the same path when the protected segment holds more entries than the new capacity. change_capacity() also clears the sketch and, because is_full uses >=, evicts one entry more than needed.
- insert() on an existing key only swaps the value. It does not refresh recency or bump the sketch; only get() records accesses. If the window is full it runs an eviction first anyway, so an update can shrink a full cache by one entry.
- Portability: uint32_t, std::enable_if, std::max, std::min and std::hash are used without including <cstdint>, <type_traits>, <algorithm> or <functional>. The code relies on transitive includes of the kind GCC 13 removed from libstdc++. The hit and miss counters are plain int and overflow after 2^31.

**Status:** Abandoned: the last commit was 2018-10-24, there are no releases, and six issues opened in 2017-2018 are still open, including HashDoS protection and 'Thorough testing required'. GitHub detects no license and there is no LICENSE file, but every header carries an MIT-style permission notice (Copyright 2017 mandreyel), so it is best treated as a small reference to vendor and fix rather than a dependency.

[repo](https://github.com/vimpunk/w-tinylfu) · [benchmark](https://arxiv.org/pdf/1512.00727)

#### columnar-analytics

##### FireDucks  `Python (compiler-generated C++ backend)`  `BSD-3-Clause`  `active`  `Tier C`

NEC's closed-source drop-in for pandas: lazy IR optimization plus multithreaded Arrow kernels; first-party TPC-H SF10 claims 141x.

**Beats:** pandas — FireDucks' own TPC-H SF10 run (22 queries written in pandas by the FireDucks team and executed through the import hook) on an AWS m7i.8xlarge (Xeon Gold 6526Y, 32 cores, 512 GB, Ubuntu 24.04, performance governor) reports an average 141x speedup over pandas excluding I/O and 55x including Parquet I/O, against DuckDB 109x/61x and Polars 58x/50x, so DuckDB wins once I/O counts. No library versions, compiler flags or independent reproduction exist, and result checking is off by default in the harness; in Nov 2024 the Polars author ran an earlier FireDucks through the same harness (including I/O, Polars-generated data, his own unstated hardware) and got slower times than Polars on q1-q9 (e.g. q9 58.6 s vs 1.68 s) and a std::length_error crash on q10.

**Known shortcoming:** First-party benchmark from NEC with binary-only wheels (the GitHub repo is an issue tracker, no public source); no compiler/flags and unpinned versions.

**Known shortcoming:** Closed engine (32 MB .so with MLIR+TFRT+Arrow, no SBOM; GPU backend enterprise-only). Pins pandas<2.4 and pyarrow 21.0.x exactly (pyarrow CVE issue #81 unanswered); no release since 1.4.4 (2025-12). Loops/apply/fallbacks are slower than pandas (its own PyData 2025 slides, #73); memory blowups and failed end-to-end runs (#73, #80). The harness's result check is off by default; in Polars' author's Nov 2024 run of the same harness an older FireDucks was slower than Polars on q1-q9 and crashed on q10. Lazy semantics: late errors, different merge row order, isinstance(pandas.DataFrame) is False.

**How:** Each pandas call adds an op to a dataframe-specific intermediate representation. The wheel bundles LLVM/MLIR and TFRT and its extension exports MLIR symbols. A compiler pass optimizes that IR before it runs: projection pushdown (drop unused columns before sort, merge or groupby), predicate pushdown (filter before merge), pattern rewrites such as where().groupby() into filter-then-groupby, and caching of intermediate results. The default 'dfkl' backend then runs the ops as multithreaded C++ kernels over Apache Arrow columns, adding its own parallelism on top of Arrow compute, where pandas runs single-threaded; data is treated as immutable and column buffers are shared rather than copied.

**Use it when:**
- Existing vectorized pandas pipelines (read_parquet/read_csv, filter, merge, groupby-agg, sort) that you cannot afford to rewrite in Polars or SQL; try it by running the script under `python -m fireducks.pandas`.
- Multi-GB in-memory tables on many-core Linux x86-64 boxes (the headline run used 32 cores and TPC-H SF10), where pandas' single-threaded execution is the bottleneck.
- Code with a poorly ordered data flow, such as filtering after a merge, sorting whole frames, or selecting columns late. FireDucks' own talk says query-optimizing engines gain most here, because pushdown fixes the order automatically.
- CPU-only machines where cudf.pandas is not an option; Apple Silicon (macOS 14+ arm64) is also supported, as experimental since 1.2.7.

**Skip it when:**
- Loop-heavy code (iterrows, apply, row-wise loc/iloc, NumPy calls on frames). FireDucks' own PyData 2025 talk rates this code 'Slower' than pandas, UDFs in apply are not compiled, and users report 2-3x slowdowns there (issue #73).
- Workloads that hit unimplemented APIs. Fallbacks convert data to pandas and back and cache copies: users report memory growth that crashed a server (#73), and higher memory, longer runtime and failed end-to-end runs versus pandas on 1.4.3 (#80, Dec 2025).
- Modern or locked-down stacks. 1.4.4 requires pandas <2.4 (pandas 3.0.x is current) and pyarrow 21.0.x exactly; an issue asking for pyarrow >=23.0.1 to fix CVE-2026-25087 (#81, June 2026) has no reply. It does not support Python 3.14, native Windows, Linux aarch64 or glibc <2.28.
- Environments that must audit or vendor code. The engine is a 32 MB closed-source .so from NEC, with no SBOM or build provenance, and the FAQ says no organization offers paid support. The GPU backend is enterprise-only.
- Remote or fsspec inputs (s3://, http URLs), non-default read_parquet arguments, and pandas subclassing or extension dtypes: all of these fall back to pandas or are out of scope.

**Vs siblings:** Pick FireDucks over cuDF (cudf.pandas) when there is no NVIDIA GPU or the pandas code has an unoptimized data flow, because cuDF executes eagerly and FireDucks reorders lazily. Pick it over chDB when the code must stay pandas rather than become SQL. Prefer cuDF or chDB when you need an open-source, auditable engine or current pandas/pyarrow versions.

**Gotchas:**
- Lazy execution makes per-step timings meaningless. A user's '30,713x faster sort' (#72) and a 'slow head()' (#48) were both deferred work. Use FIREDUCKS_FLAGS="--benchmark-mode" or call ._evaluate() before timing.
- try/except KeyError around df[col] may not fire, because the lookup runs later. Use `if col in df` (non-lazy) or ._evaluate().
- Fallbacks are silent by default. Set FIREDUCKS_FLAGS="-Wfallback" to log them, and "--trace=3 --trace-file=-" for a per-kernel/fallback time profile.
- Memory is held longer than in pandas: column buffers are shared via shared_ptr until every referencing frame dies, the Arrow memory pool does not return freed memory to the OS promptly, and fallback caching can grow memory until gc.collect() runs. A delayed-deallocation bug was fixed in 1.4.0 (#69, #49).

**Status:** Rated active from its roughly monthly PyPI releases through 1.4.4 (2025-12-02), though none has shipped in the ~10 months since, the GitHub repo is only an issue tracker, and a pyarrow CVE issue is unanswered. Usability is 'reference': the engine is BSD-3-licensed on paper but ships as a binary-only wheel you can neither audit, patch nor vendor.

[repo](https://github.com/fireducks-dev/fireducks) · [benchmark](https://fireducks-dev.github.io/docs/benchmarks/)

##### JetStream  `C++`  `no license`  `unknown`  `Tier C`

MIT research prototype: LLM agents generate query-specific accelerators that plug into DuckDB or PostgreSQL; claims 833x geomean over single-threaded DuckDB.

**Beats:** DuckDB — On TPC-H SF=20 (all 22 queries, warm reads, state already built), stateful accelerators were 833x faster by geomean than single-threaded DuckDB and 3544x faster than PostgreSQL 18.4, on a 2x Xeon Gold 6230 server with 376 GiB RAM. Stateless accelerators were 1.99x faster, and with RF1/RF2 refreshes every 60, 120 or 300 s the geomean including maintenance was 375x, 629x or 733x. On SEC-EDGAR SF=3 it was 102x over DuckDB and 486x over PostgreSQL. No compiler, flags, DuckDB version or code are given.

**Known shortcoming:** Paper only: no code, compiler or flags. The baseline is single-threaded DuckDB; the figure legend says 843x while the text says 833x (also 3544x vs PostgreSQL).

**Known shortcoming:** The 833x needs persistent per-query state (range trees, q-gram index, bitmaps); stateless it is only 1.99x, and memory rises to 28.1 GB vs 10.3 GB. Writes erode the gain (733x to 375x as the refresh interval drops from 300 s to 60 s; point writes 8.8x). Needs patched DuckDB transaction hooks and queries go through an accel_qN_aux() table function, so it is not a drop-in; the SEC figure plots only 6 selected queries.

**How:** Almost all of the speedup comes from persistent, query-specific auxiliary state. This is generated sufficient statistics keyed on the query's parameters: per-month revenue for TPC-H Q14; per brand/container 2-D range trees over part size x quantity for Q19, so each predicate branch becomes one range-sum probe; a q-gram inverted index plus a baseline histogram with sparse corrections for Q13; dense-ID bitmaps for distinct counts in SEC-EDGAR Q1. A read then touches a few state partitions instead of scanning, joining and aggregating the base tables. Without that state, the generated kernels over native scans reach only 1.99x. Writes go through generated maintenance code, similar to incremental view maintenance. At pre-commit a per-accelerator cost model picks one of four actions (apply delta, rebuild the affected partitions, full rebuild, or invalidate and repair lazily), and the result is published optimistically under per-partition versions.

**Use it when:**
- A fixed set of parameterized analytical templates (reports, dashboards) runs repeatedly on DuckDB or PostgreSQL, and each query reduces to a small aggregate over parameters you can key state on.
- The workload is read-heavy and writes arrive in batches. With TPC-H RF1/RF2 refreshes (about 0.1% of the database each) every 60 s, the workload geomean including maintenance was still 375x over DuckDB.
- You want the existing DBMS to remain the single copy of the data, with ad-hoc SQL and transactions intact. GenDB and Bespoke OLAP instead rewrite storage or keep a second copy.
- You are researching LLM-synthesized database specialization. The workflow is reusable: an external orchestrator owns the differential tests and A/B benchmarks so the coding agent cannot game them.
- You have memory to spare. Stateful accelerators used 28.1 GB at TPC-H SF=20, against 10.3 GB for stateless.

**Skip it when:**
- Anything production-bound. No code, license or release is public, so the only option is to reimplement the design from a v1 arXiv preprint with no venue.
- Ad-hoc or exploratory SQL. Only the pre-declared templates are accelerated; every other query runs at plain DuckDB or PostgreSQL speed.
- Memory-constrained hosts. At SF=20, stateful JetStream needs 28.1 GB, against 18.1 GB for GenDB, 16.12 GB for Bespoke OLAP and 10.3 GB for stateless JetStream.
- Write-heavy workloads. The TPC-H geomean falls from 733x to 375x as refreshes go from every 300 s to every 60 s. On SEC-EDGAR with point writes every 0.5 s it is only 8.8x over DuckDB and 4.0x over PostgreSQL.
- You only need faster execution without precomputation. Stateless accelerators give 1.99x, and that is against single-threaded DuckDB; multi-threaded DuckDB was not used as a baseline.

**Vs siblings:** Sirius also speeds up DuckDB workloads, but as a GPU engine with public code that is about 5.5x faster at SF100 on general queries. Umbra and Velox are general-purpose engines. Pick JetStream's approach only for a fixed set of parameterized templates on DuckDB or PostgreSQL, where you will trade memory and a from-paper reimplementation for precomputed state; otherwise use one of the siblings.

**Gotchas:**
- The Figure 6 numbers are warm reads with valid state and exclude the one-time state build. After an invalidation or a publish conflict, the affected queries run on the base-table fallback path until the state is repaired.
- Correctness is checked empirically, not proven. It rests on differential tests against the host DBMS and an audit agent with extra hidden tests. Each query gets unique LLM-written code (plus maintenance logic) that someone has to review and own.
- The geomean hides a wide spread. Section 3.4 reports about 8.6x best-valid for Q13 and about 2638x for Q19. The SEC-EDGAR figure plots only six selected queries (Q1-Q4, Q6, Q24) out of a 1000-query SQLSmith set.
- The text and the Figure 6 legend disagree (833x vs 843x, and 3544x vs 3554x for PostgreSQL). The DuckDB baseline is single-threaded with no version given, while GenDB is plotted multi-threaded. Changing a template means re-running synthesis, which cost $41.63 for all 22 stateful TPC-H accelerators.

**Status:** Reference only: an MIT CSAIL arXiv preprint (v1, 23 Aug 2026) with no code, license or release; a co-author's publication page links only the paper and BibTeX, so maintenance status is unknown.

[benchmark](https://arxiv.org/abs/2608.22476)

##### tickdb (DerekNest)  `Rust`  `no license`  `active`  `Tier C`

Rust tick-trade store: delta-of-delta/varint+zstd segments ~20% smaller than Parquet+zstd, but slower than DuckDB on ingest and all queries.

**Beats:** Parquet (zstd-compressed) — The author's BENCHMARKS.md (2 runs on 2M synthetic Binance-style trades, hardware not stated, release profile with opt-level 3 and thin LTO) reports 6.50 bytes/trade vs 8.13 for Parquet written by DuckDB COPY with ZSTD, about 20% smaller. DuckDB reading that Parquet wins every query (OHLCV ~1.5x, VWAP ~190-240x, top-10 ~55-115x), and DuckDB's CSV load is ~2.7x faster at ingest. Neither side is tuned: each query is timed once, the Parquet file sets only COMPRESSION ZSTD and leaves column types to read_csv_auto, and the synthetic data (i.i.d. sides, uniform qty, 950-1050 ms between trades despite a '~1ms' comment) was never replaced with the real Binance run the docs describe.

**Known shortcoming:** NOT FASTER: the only win is storage (6.50 vs 8.13 B/trade, ~20% smaller than Parquet+zstd); ingest is ~2.7x slower and every query is slower than DuckDB (the author's own doc says 1.5-240x). No license.

**Known shortcoming:** The 'includes durability' excuse is false (both tickdb bench paths use FsyncPolicy::Never); mmap is not zero-copy (segments are copied to the heap); FORMAT.md says CRC-32C but the code computes IEEE CRC-32; DESIGN.md still claims a ~3x OHLCV win withdrawn by BENCHMARKS.md. Synthetic data only; Parquet side untuned; each query timed once; single-threaded; two commits, 0 stars, ~0.8 GB repo of committed build files.

**How:** It is not faster; its only win is size, from how each 65,536-row block is encoded: it stores timestamps as delta-of-delta + zigzag + LEB128 varints (a byte-aligned simplification of Gorilla), rescales prices to a common decimal exponent and delta + zigzag varint-codes the mantissas, stores sizes and trade_ids as plain varints and side as run-length pairs, then zstd-compresses the block at level 3. Reads are slow by construction: every query decompresses and decodes all five columns of each block (no projection pushdown), the 'mmap' reader copies each whole segment into a heap Vec, and the kernels are single-threaded scalar loops (OHLCV does one BTreeMap insert per row). The author credits DuckDB's vectorized engine for the gap.

**Use it when:**
- As readable reference code for a trade-specific block codec (DoD timestamps, decimal-mantissa delta prices, RLE side, zstd) that reached 6.50 bytes/trade on the author's 2M-row synthetic set, vs 8.13 for Parquet+zstd written by DuckDB.
- To study a small end-to-end storage engine in Rust: CRC-framed WAL with EveryWrite/EveryNMs/Never fsync policies, a manifest updated by atomic rename, immutable segments with zone maps, size-tiered compaction and crash-recovery tests.
- To learn Raft testing: an I/O-free RaftNode::step state machine driven by a seeded fault-injection simulator (drop, delay, duplicate, partition, crash). The README reports 1,000 seeds with zero invariant violations.
- As design input only, when bytes per trade in cold storage matter more than query or ingest speed and you will write your own implementation. The code has no license.

**Skip it when:**
- Any query-speed goal. DuckDB over the same Parquet file was about 1.5x faster on 1-minute OHLCV, 190-240x faster on VWAP and 55-115x faster on top-10. Polars also beat it on VWAP.
- Ingest-bound pipelines: 7.32M rows/s (one run) vs 20.05-20.67M rows/s for DuckDB's CSV load. BENCHMARKS.md excuses this by saying tickdb pays for durability, but both tickdb bench paths open the engine with FsyncPolicy::Never.
- Production use or code reuse: no license, 2 commits (both 2026-07-04), 0 stars, no releases, not on crates.io, and the author calls it a portfolio project. The Dockerfile says it has never been built.
- Data outside the fixed trade schema. There are no dynamic or optional columns, the CLI's CSV parser expects Binance aggTrades columns, qty is stored as 8-decimal fixed point (extra digits are truncated), and there is no Parquet or Arrow file import.
- Concurrent readers or writers. Engine is documented as single-threaded, so callers must serialize access (the server wraps it in a Mutex), and queries run on one thread.

**Vs siblings:** Practically never for real workloads. Among catalogued Parquet alternatives, Vortex, BtrBlocks and FastLanes report faster writing or decoding than Parquet, and QuestDB is a real time-series engine for tick data. Pick tickdb only as a compact, readable Rust example of a trade-specific codec together with a WAL, compaction and Raft simulation.

**Gotchas:**
- Segments are not really zero-copy mmap. MmapSegment::open copies the whole mapped file into a Vec (mmap.to_vec()), and Engine::scan collects each segment's decoded batches into a Vec before yielding them, so RAM use grows with segment size.
- FORMAT.md says checksums are CRC-32C (Castagnoli), but the code uses crc32fast, which computes standard CRC-32 (IEEE). An independent reader built from FORMAT.md would reject every block.
- The docs contradict each other. DESIGN.md Phase 4 still says tickdb is ~3x faster than DuckDB on OHLCV and only 3-4x slower on VWAP and top-N, and agg.rs says the kernels hit a >=100M rows/s/core target. The later BENCHMARKS.md withdraws the OHLCV win and measures 15-34M rows/s.
- The repo has about 24.5k build-artifact files committed under target/ and no .gitignore, and GitHub reports about 0.8 GB of disk usage, so a clone is heavy.

**Status:** Dormant single-drop portfolio repo (2 commits on 2026-07-04, none since) with no license, so the code is reference-only and cannot legally be reused.

[repo](https://github.com/DerekNest/tickdb) · [benchmark](https://github.com/DerekNest/tickdb/blob/main/docs/BENCHMARKS.md)

#### embedded-kv

##### BTreePlus  `C#`  `MIT for the Community Edition NuGet package (binary only) and the demo/docs repo; the engine source is not published; the Pro/Enterprise Edition is proprietary (private NuGet feed plus license token)`  `active`  `Tier C`

Binary-only fixed-width B+Tree index for .NET; vendor claims 4.4-7x faster bulk inserts than SQLite (paid Pro build).

**Beats:** SQLite — According to the vendor's NuGet README (the only evidence), the paid BTreePlus Pro, using 32 KB pages on NVMe under .NET 9.0/Linux, bulk-inserted 4M rows in 1.03 s vs 4.53 s for SQLite (4.4x) and 1B rows in 346 s vs 2410 s (7x), with no CPU, SQLite pragmas, batching method or harness published. A separate i9-13900 + Samsung 990 PRO run loaded 1B 14-byte records in 5m10s vs PostgreSQL's 6m08s (~1.19x throughput), labelled 'WAL enabled for both engines' even though the same README says BTreePlus has no WAL.

**Known shortcoming:** Binary-only NuGet (engine source not published); the fast numbers come from the closed paid Pro build, and the README's Community 3.26x conflicts with the vendor PDF.

**Known shortcoming:** The engine is a binary-only NuGet DLL (MIT covers the free binary and docs only) and the 4.4x/7x claims are for the paid Pro build. In 1.3.1 the constructor forces enableCache=false, so the demo/PDF's enableCache:true is silently ignored. No WAL/journal, yet the PostgreSQL bench is labelled 'WAL enabled for both'; no CPU/pragmas/harness for the SQLite table. One Monitor lock per tree serializes readers and writers; fixed-capacity errors; the release DLL ships a test/fuzz class and a hard-coded /home/mmh log path; 9 stars.

**How:** It has no SQL or VM layer: fixed-width key/value slots sit directly in fixed-size pages (pageSize x 512 bytes, up to 64 KB) and are compared as raw bytes. The vendor attributes the headline numbers mainly to a write-back page cache with deferred flush: dirty pages are written at Commit(), at a byte watermark or by a ~1 s auto-commit, and the PDF gives ~3.16M inserts/s with the cache on vs ~418K/s with it off. Other speed paths are an append fast path for monotonically increasing keys (TryAppendFastPath in the DLL), a bottom-up BulkLoad into an empty tree (0.90 leaf fill) and FNV-1a hash sharding across several trees (ShardManager) for parallel batch inserts. It also has no journal (no WAL or rollback journal), so it avoids the double write SQLite pays for crash safety.

**Use it when:**
- A .NET process that needs a local sorted index over fixed-width keys (big-endian Int64 IDs, Unix timestamps, padded product codes) with small fixed-size values, e.g. a POS/kiosk secondary index or a log keyed by sequence number.
- Loading tens of millions to billions of fixed-width records in key order when losing uncommitted work on a crash is acceptable. This is the shape of the published SQLite and PostgreSQL runs.
- Hot-path point lookups that must not allocate: Find writes into a caller-supplied Span<byte>, so a SQL engine's parsing and row materialisation are avoided.
- You are prepared to evaluate and license the commercial Pro Edition. Every published speedup is for that build (page cache plus Bulk Insert), not for the free package.

**Skip it when:**
- You need source you can audit, patch or vendor. The engine is closed, and the MIT license covers only the free binary and the docs.
- You need crash-safe atomic commits. The NuGet README says it is 'not journaling-based' and has no WAL: power loss during a write can lose the latest uncommitted operation, and consistency is promised only after a successful Commit().
- Variable-length keys or values, secondary queries, multi-statement transactions, or concurrent readers. Each tree has one Monitor lock that serialises Find, Insert, Erase and Commit.
- You expect the free Community build to be fast. The vendor calls it 'not optimized for speed' (page cache disabled, ~418K inserts/s in the PDF), so the 4.4x/7x figures do not apply to it.
- Production-critical use generally. It has 9 GitHub stars, zero issues, one Show HN post with no comments and no independent benchmarks. The release DLL even ships its delete/rebalance test suite as a public class (DeleteEdgeCases) with a hard-coded /home/mmh/... log path and 'ROUTING BUG DETECTED' repro strings.

**Vs siblings:** For .NET, ZoneTree (MIT, source on GitHub, a transactional ACID LSM engine that also reports beating SQLite) is the default pick. Choose BTreePlus only if you want a minimal fixed-width B+Tree file with a published on-disk format that third-party readers can parse, and you are willing to license the closed Pro build to get the advertised speed.

**Gotchas:**
- In the public 1.3.1 DLL the BTree constructor overwrites the enableCache argument with false (visible in the IL), so CreateOrOpen(..., enableCache: true), as used in the GitHub demo and the PDF, is silently ignored. A public SetUseCache(bool) method with no license check exists, but its behaviour in the free build is not documented.
- The docs contradict each other and the binary. The GitHub README shows a new BTree(path, keyLength, ...) constructor in namespace BTreePlus that the DLL does not use (it is mmh.BTree with static factories), and it credits the Community Edition with the cache-on 3M-inserts-in-0.95 s result. The NuGet README lists Erase as free, while NOTICE.md and the PDF call it Enterprise-only. The DLL publicly exposes Erase, BulkLoad, FindRangeValues, PageCache and ShardManager anyway.
- Plan capacity up front. max_recs sizes the page allocation table (PAT), and the DLL has 'PAT is full (fixed size)' and 'PAT exhausted after second grow' errors. In-memory trees are capped by the MemoryStream size limit. Count is an int that is recomputed across all leaf pages on each call.
- Ordering is raw byte order. Integers must be written big-endian and right-aligned, and strings zero-padded, or range order is wrong. The format spec says over-long keys are truncated to keylen, so distinct long keys can collide.

**Status:** Maintained: NuGet 1.3.1 shipped in December 2025 and the GitHub docs were updated 2026-01-23 by a single vendor (MMH Systems), but usability is mixed: the free MIT package is binary-only with its page cache forced off, and the advertised speed needs a closed commercial license.

[repo](https://github.com/koyllis/BTreePlus) · [benchmark](https://www.nuget.org/packages/BTreePlus)

##### CompassDB  `C++`  `no license`  `unknown`  `Tier C`

Paper-only RocksDB-derived KV engine that replaces SST indexes with in-memory two-tier perfect hashing; reports 2.5-4x RocksDB YCSB point-op throughput.

**Beats:** RocksDB — The DiPeak authors ran YCSB with 16 threads on a Dell T440 (Xeon Silver 2.40 GHz, exact model not given; 128GB RAM; Samsung PM9A3 NVMe; Ubuntu 20.04 ext4). They loaded 200M 20B/1KB records and ran 100M operations with O_DIRECT, compression off, and 4x128MB memtables, against RocksDB 7.9.2 and PebblesDB commit 703bd0 (2019). Bar labels give CompassDB vs RocksDB of 122.7 vs 33.8 KOPS on A (3.6x), 186.3 vs 42.1 on B (4.4x), 137.0 vs 54.2 on C (2.5x), 262.7 vs 74.4 on D (3.5x), 98.4 vs 24.1 on F (4.1x) and 2.08 vs 11.04 on E (5x slower). Compiler and flags are not stated, and nobody else has reproduced the results.

**Known shortcoming:** The 5-17x is against PebblesDB, not SplinterDB. The claimed SIGMOD/PACMMOD venue could not be found in Crossref, so this is an arXiv-only vendor preprint; no code.

**Known shortcoming:** Loses YCSB-E about 5x (2.08 vs 11.04 KOPS; scans become random reads in hash order). Lopsided baseline: RocksDB 7.9.2 with a 32 MB cache under O_DIRECT and no stated Bloom filter, while CompassDB keeps its whole index in RAM (measured ~29-34 B/key including memtables, vs a 6.5 B/key estimate). Internal mismatches (text 5.5x vs bars ~3.5x on D; duplicated figure bars); deletes leave tombstones until GC; AVX2/x86 only.

**How:** Each TPH (the SSTable replacement) carries a global perfect-hash table that maps a key's 64-bit hash to a 1-byte signature (a Bloom-filter substitute with about 1/255 false positives) plus the ID of the piece file holding the key. Each piece has a local perfect-hash table that maps the key to a block offset, and because both tables stay in RAM (estimated at about 6.5 bytes per key), a Get costs two in-memory lookups and one disk read. Compaction writes only new or changed keys into a new delta piece file and leaves unchanged keys where they are, and 'hash range' mode partitions each level by a 32-bit key hash so every compaction touches a fixed number of TPHs (similar to PebblesDB's guards). The perfect hash is CPHash, a mix of CHD and PTHash (dense and sparse buckets, parameter reuse, load factor 0.9), and its construction uses AVX2 with Lemire's fastmod and is split into 64 parallel segments.

**Use it when:**
- As a design reference if you maintain a RocksDB fork whose traffic is mostly point Get/Put/update (YCSB A, B, C, D, F shapes) on NVMe, with a dataset much larger than RAM.
- Read-heavy point lookups where RocksDB index and filter blocks miss cache and cost extra I/Os. The design aims for one device read per Get. The paper reports about 3x lower read amplification (about 10 vs about 32 for RocksDB with 20B keys and 128B values) and 8.5x db_bench readrandom throughput at 200M keys.
- Point-read workloads with 1KB-50KB values. The perfect-hash index size depends on key count, not data size, and read-only YCSB-C reports 3.6x RocksDB at 1KB and 7.2x at 50KB (my reading of the Fig. 10b bar labels).
- SSD write-endurance-sensitive loads with random inserts. Delta piece files avoid rewriting unchanged keys, and the paper reports write amplification of 4.34 vs about 10.6-11 for RocksDB and PebblesDB at 500M keys. For read-mostly data, 'one level' mode reports 15x lower write amplification than RocksDB (100M keys, 1KB values).
- If you are evaluating CHD or PTHash as a replacement for an SST index, CPHash's dense/sparse bucketing, parameter reuse, AVX2 fastmod and per-segment parallel build are documented well enough to copy.

**Skip it when:**
- Whenever you need something to run. There is no public repository, binary, license, API reference or build instructions, and GitHub has only unrelated 'compassdb' projects.
- Range scans and iterators. On YCSB-E, CompassDB gets 2.08 KOPS vs RocksDB's 11.04 (about 5x slower), with average read latency of 8.0ms vs 1.5ms. Data is stored in hash order, so scans go through a sorted key-location array (8 bytes per key, sampled every 64 keys) and one random read per key.
- Memory-constrained hosts or very large key counts with small values. The one-I/O guarantee requires every global and local index to stay in RAM, and memory grows with key count. The paper measured 1.7GB at 50M keys and 2.9GB at 100M keys (about 29-34 bytes per key in total, including memtables), well above its 6.5 bytes-per-key estimate.
- Workloads heavy in deletes or overwrites under a tight space budget. A deleted key keeps a placeholder in the global index until its old piece file is garbage-collected. Each TPH holds up to 16 piece files by default (configurable up to 1024), so stale versions accumulate, and every compaction reads all piece files of the TPH. The paper's local-index sizing assumes 1.7x space amplification.
- Non-x86 targets, or any production decision based on these numbers. Perfect-hash construction uses AVX2 and no other ISA is mentioned. The results are first-party vendor numbers that nobody has reproduced.

**Vs siblings:** You can't pick it for deployment, because there is no code. For deployable point-lookup speedups over RocksDB, use SplinterDB (2-2.6x point queries, about 2x lower write amplification, open source), KVell, or F2/FASTER. DobLIX is the closest code-available idea: it also swaps RocksDB's SST index, for a learned one. Read CompassDB only as the catalogued reference for putting perfect hashing plus delta piece files in place of SSTs, when scans do not matter.

**Gotchas:**
- The baseline setup is lopsided. RocksDB 7.9.2 and PebblesDB got a 32MB LRU block cache under O_DIRECT, while CompassDB runs with no block cache but keeps its whole perfect-hash index in RAM (about 1.3GB even at the estimated 6.5 bytes per key for 200M keys). The paper says other RocksDB options stayed at defaults and argues against a '10-bit Bloom filter default'. But RocksDB 7.9.2's BlockBasedTableOptions::filter_policy defaults to nullptr, so whether the YCSB baseline had Bloom filters at all is not stated.
- The numbers disagree with each other. The text claims 5.5x over RocksDB on YCSB-D, but the bar labels read 262.67 vs 74.37 KOPS, which is about 3.5x. The 1KB point in the Workload-C value-size sweep (122.7/33.79/11.86) exactly repeats the Workload-A bars rather than the Workload-C bars (137.01/54.24/24.84). The advantage over RocksDB also does not grow steadily with value size, as the text says: it is 4.2x at 300B, 2.5x at 10KB and 7.2x at 50KB.
- The manuscript reads like a draft. It still carries the ACM template's placeholder running header 'Trovato et al.', it cites a 'Table 5.5-1' that does not exist, and two background paragraphs appear twice. It is arXiv v1 only, and the claimed SIGMOD/PACMMOD publication does not appear in Crossref.
- The benchmark used 'hash range' mode, where TPHs are partitioned by a hash of the key rather than by key order. I infer, though the paper does not say so, that a range scan must visit every TPH on every level. That fits the YCSB-E loss, which the paper leaves as future work.

**Status:** Paper only: arXiv v1 (26 Jun 2024), with no later version and no journal reference. It is absent from Crossref's PACMMOD records (551 since June 2025), so the claimed SIGMOD publication is unverified. OpenAlex lists only the arXiv version, with zero citations. There is no repository or license, DiPeak's homepage (an enterprise LLM data-intelligence vendor) shows no CompassDB material in its static HTML, and maintenance is unknown, so it is usable only as a design reference.

[benchmark](https://arxiv.org/abs/2406.18099 (arXiv v1 preprint, 26 Jun 2024; no journal reference listed))

##### DiaLSM  `C++`  `no license`  `active`  `Tier C`

Hash-sharded LSM built on RocksDB 8.3.2 that reroutes writes around stalled shards, cutting write stalls ~94%. Code not released.

**Beats:** RocksDB — Setup: arXiv preprint (v1, 2026-09-13). Hardware: 2x AMD EPYC 7352, 256GB DRAM, one 3.84TB Samsung PCIe Gen3x4 NVMe, CentOS 7/ext4. Baselines: RocksDB v8.3.2 with Sub-Compaction and ADOC, all with throttling, WAL and block cache off. Results: on 8KB FillRandom, DiaLSM had up to 2.4x ADOC's throughput, 94.3% fewer stalls than both baselines, and about 50% lower mean/median latency than both. YCSB-E was about 1.7x over both at scan length 128 and 3.3x/5.7x/8.9x at 1K/4K/16K. Compiler and flags are not stated, and there is no artifact to reproduce the numbers.

**Known shortcoming:** The 2.4x/1.8x/2.2x gains are against ADOC, not RocksDB; against RocksDB it is ~50% lower latency, 94.3% fewer stalls and 8.9x on YCSB-E. 'ICDE 2027' is an author claim only (conference in May 2027, no accepted list yet). The repo is README-only (verifier downgrade).

**Known shortcoming:** The repo is README-only: no code, no license. The big wins (2.4x/1.8x/2.2x/2.3x) are vs ADOC, not stock RocksDB, and all runs disable throttling, WAL and block cache. Rollback is off in the main runs; above 1M compaction entries rollback is forced and stalls return. Space amplification 1.14-1.5x; more CPU.

**Known shortcoming:** Read-heavy: parity on YCSB-C, loses throughput beyond a few shards at 90% reads; short scans peak at 4 shards. The paper's API is only Open/Close/Put/Get/Seek, the scan algorithm shows no merge step, no resharding. ICDE 2027 acceptance is author-claimed only (program page 404).

**How:** The authors model the write-flush-compaction pipeline as an M/G/1 queue with vacations, where each vacation is a stall. The model says tuning one stage only moves stalls to another layer (a 'balloon effect'): this applies to ADOC's memtable/thread tuning and to RocksDB Sub-Compaction. With L independent shards, the chance that all of them stall at once falls roughly as alpha^L. A write to a stalled primary goes to the fallback shard with the smallest L0, then lowest memtable use, then smallest pending backlog, then smallest total size. It leaves a 20-byte Clue Entry (CE) in a 2MB reserved memtable area that stall thresholds ignore. CEs are pinned in L0 ('CE L0 capping') and mirrored in an in-memory CE cache so the extra hop stays cheap. Range scans run Seek/Next on all shards in parallel, which is where the large YCSB-E gains on long scans come from.

**Use it when:**
- Sustained write-heavy ingest with large values (the paper's best case is 8KB FillRandom), where RocksDB write stalls cap throughput and cause p99.99+ latency spikes.
- Write-dominated mixes such as ReadRandomWriteRandom at 10% reads / 90% writes, or insert/update-heavy OLTP on MyRocks (Sysbench oltp_insert, oltp_write_only), on a many-core box with spare CPU. The paper gave DiaLSM 32 compaction threads split across shards.
- Long range scans (1K-16K keys per scan), where parallel per-shard iteration gave 3.3x-8.9x over both ADOC and RocksDB.
- Servers with several NVMe SSDs: shards can be spread across devices, and with 8KB values throughput kept scaling past 8 shards only when a second SSD was added.
- As a reference design for LSM write-stall work (queueing model plus fallback redirection). Until code ships it is not a library you can adopt.

**Skip it when:**
- Anything that needs working code now. The repo is one README commit saying source 'will be available soon', with no license.
- Read-dominant or read-only workloads. YCSB-C is at parity with RocksDB and ADOC. At 90% reads / 10% writes, DiaLSM loses some throughput as shards grow while ADOC stays flat. On the fallback path a Get needs two shard reads.
- Short scans with many shards: YCSB-E at the default scan length of 128 peaks at 4 shards (about 1.7x) and then declines as the cost of parallel iteration outweighs the gain.
- Space- or CPU-constrained setups. Space amplification is 1.14x-1.5x with 2-16 shards (Table IV, millions of CEs), and DiaLSM uses more CPU than both baselines (Fig. 15).
- Deployments that need the full RocksDB feature set (transactions, column families, snapshots, WAL durability, block cache) or elastic shard counts. Only Open/Close/Put/Get/Seek is described, every benchmark ran with WAL and block cache off, and hash-mod-N placement has no resharding or auto-tuning.

**Vs siblings:** MatrixKV also targets write stalls but needs NVM for its matrix container, while PebblesDB (fragmented LSM) and Titan (key-value separation for large values) change the on-disk layout. DiaLSM is the one to watch if you want to stay on plain NVMe with stock RocksDB format per shard and remove stalls by structure rather than tuning. Today, pick MatrixKV, PebblesDB or Titan when you need code you can run, since DiaLSM has none.

**Gotchas:**
- Every headline experiment ran with rollback disabled. Rollback is the step that moves redirected keys back to their primary shards. Turned on after an 850K-CE write burst, it added about 60s of delay before reads. Once CEs pass the default limit of 1M, rollback is forced and no new CEs are accepted, so write stalls come back.
- The benchmark config is non-default for every system: write-stall throttling, WAL/commit logging and block cache all off. The RocksDB baseline was also reconfigured: 2m memtables of 512/m MB each and 32 compaction threads. The 2.4x/1.8x/2.2x/2.3x headlines are against ADOC, not stock RocksDB.
- Crash recovery scans shards for redirected keys whose CE is missing and blocks user I/O while it runs. Because the WAL was off in all experiments, the cost with durability on was never measured.
- Algorithm 1 bounds a range scan at Kstart + L and appends each shard's results with no merge step, even though global ordering is a stated design goal. YCSB-E ran with a single I/O thread 'to avoid the parallel processing overhead'.

**Status:** The repo was created 2026-09-13 with a single README commit (1 star, no license, no code); ICDE 2027 acceptance is author-claimed and not yet listed publicly. The lab's earlier DownForce paper did publish a GPL-2.0 RocksDB fork, so a release is plausible, but for now this is a paper to read, not a dependency.

[repo](https://github.com/DISCOS-LAB/DiaLSM) · [benchmark](https://arxiv.org/abs/2609.14370)

##### LUDA  `C++`  `no license`  `unknown`  `Tier C`

Paper-only LevelDB 1.22 fork that moves most compaction work to an NVIDIA GPU; about 2x LevelDB/RocksDB YCSB-A throughput, but only under heavy CPU contention.

**Beats:** LevelDB — The HUST authors ran YCSB-A (50/50 update/read) with 16 B keys and 128 B-1 KB values: 10M pairs loaded (about 5 GB), then 10M operations, with 4 MB memtables/SSTs, 4 KB blocks and 10-bit Bloom filters. They compared against LevelDB 1.22 and RocksDB 6.4.6 (4 threads), on a 4-core/8-thread Xeon E5-1620 v4 with 64 GB RAM, a GTX 1080Ti, an Optane 900p and Ubuntu 16.04 with CUDA 10.1, and used stress-ng to load the CPU to 0/40/80%. At 80% stress and 1 KB values, LUDA got about 2x the throughput of both baselines: RocksDB kept about 30% of its unstressed throughput and LUDA/LevelDB about 70%, and running time grew by 100 s for LUDA vs 203 s for LevelDB. With a free CPU, RocksDB was fastest. Host compiler and flags are not stated, and nobody else has reproduced the results.

**Known shortcoming:** The 2x appears only with 80% of CPU consumed by stress-ng; with free CPU RocksDB is fastest. No public code (the linked repo is github.com/anonymous) and no peer-reviewed version.

**Known shortcoming:** Sorting still runs on the CPU and every SST crosses SSD to host to GPU; uses more CPU than LevelDB. Baselines ran defaults (LevelDB 1.22 uses Snappy while LUDA has none, so compression may be unequal); at 128 B it compacts ~2x LevelDB's data due to a prototype shortcut, inflating the data-speed metric. Draft errors in the arXiv v1; later GPU-compaction papers (gLSM TOS'24, RGKV TC'25, GPComp) are better references.

**How:** Compaction is split into three GPU phases that can run in parallel. An 'unpack' kernel runs per input SST, verifying each data block's CRC32 and rebuilding the prefix-compressed keys. It stores values in a KV pair buffer and emits small <key, value_offset> tuples. Packing uses three kernels: 'shared_key' rebuilds prefix-shared keys per 4 KB block, 'encode' copies values in and computes CRC32 per block, and 'filter' builds the Bloom filter block. Finished data blocks are sent back to the host with cudaMemcpyAsync while the filter is still being built. The merge-sort itself is not done on the GPU: the tuples are copied to the host, deduplicated and sorted on the CPU, then copied back (the 'cooperative sort'). Values move only twice ('lazy value movement'), and every SST goes SSD -> host RAM -> GPU and back, with no GPUDirect Storage.

**Use it when:**
- As a design reference for moving LSM compaction CPU work (block CRC, prefix-key decode/encode, Bloom filter build) onto a GPU, on hosts where other tenants leave the KV store about 20% of the CPU. That is the only setting where it beat both baselines by about 2x.
- Write-heavy or mixed (YCSB-A-shaped) workloads on very fast storage (the paper used an Intel Optane 900p), with a small host CPU (4 cores / 8 threads) and a spare NVIDIA GPU. In that setup LevelDB-style compaction is CPU-bound.
- When steady 99th-percentile write latency under a LevelDB-style engine matters more than peak throughput. With no CPU stress, the paper's Fig. 12 shows LUDA with the lowest and flattest p99 of the three stores after a short warm-up spike. Under 80% CPU stress, its average write latency rose by only 7 us.
- As a starting point for reading the later GPU-compaction papers that cite it (gLSM in ACM TOS 2024, RGKV in IEEE TC 2025, GPComp in TPDS 2025, gParaKV, GCLComp). gLSM's abstract adds a GPU-oriented radix sort and key-value separation, the two costs LUDA leaves on the CPU and the PCIe bus.

**Skip it when:**
- Whenever you need something to run. There is no source, binary, license or build instructions. GitHub searches for LUDA and for GPU LevelDB/LSM compaction find nothing, and the footnote's github.com/anonymous link is a dead placeholder.
- Hosts with free CPU. With no CPU stress, stock RocksDB 6.4.6 (4 threads) finished the 5 GB YCSB-A run fastest at every value size and LUDA came second. In the one-hour 50 GB run, RocksDB with 4 background jobs also had the shortest running time.
- Read-dominated workloads. LUDA does not touch the read path, and the paper blames part of its throughput loss under CPU stress on reads that get less CPU time.
- Machines without an NVIDIA CUDA GPU, or where the extra PCIe traffic and host CPU cost matter. LUDA used more CPU than LevelDB because data moves back and forth between CPU and GPU, and every compaction stages SSTs in host RAM.
- Workloads that need compressed SSTs or low SSD write amplification. Snappy is not implemented. Because the prototype triggers compaction only when L0 is full and does not flush the immutable memtable first, it compacts about 2x as much data as LevelDB at 128 B values.

**Vs siblings:** You can't pick it for deployment, because there is no code. For a code-available LevelDB-lineage speedup, use HyperLevelDB (about 3.4x LevelDB on 100M writes). To cut compaction work itself, use PebblesDB (guards) or MatrixKV/SpanDB on fast storage. Read LUDA only as the catalogued reference for offloading compaction to a GPU when the host CPU is contended.

**Gotchas:**
- The headline depends on the scenario. 'Up to 2x higher throughput' comes from the 80% stress-ng setting (20% of a 4-core CPU left) at 1 KB values. The text gives no numbers for the other cells, and Fig. 7/8 bars carry no value labels.
- The '2x data processing speed' / 'compaction speed 1x faster than LevelDB' claim divides compaction bytes by running time. Part of those bytes is extra work the prototype creates for itself: it compacts about 2x LevelDB's data at 128 B values. The '46% less running time' at 1 KB does not say which CPU-stress level it refers to.
- The compression settings may favor LUDA. All stores ran with 'default parameters', and LevelDB 1.22's default is kSnappyCompression whenever it is built with libsnappy, but LUDA does no compression at all. The paper does not say whether the baselines were built with Snappy, so their CPU budget may include compression work that LUDA skips.
- The manuscript has draft errors. The 50 GB run is called '0.1 billion' pairs in Section IV-A but '0.1 million' in IV-D. The text cites Fig. 9 (latency) for running times that are in Fig. 8. It is an arXiv v1 (7 Apr 2020) only, with no peer-reviewed version in Crossref.

**Status:** Paper only: arXiv v1 (April 2020) with no later version, no journal reference and no public repository or license, so maintenance is unknown and it is usable only as a design reference. Semantic Scholar lists about 21 citing papers, including newer GPU-compaction systems (gLSM, RGKV, GPComp) that are better starting points today.

[benchmark](https://arxiv.org/abs/2004.03054)

##### Mycelium (TE-LSM)  `C++`  `no license`  `unknown`  `Tier C`

RocksDB fork that splits columns, re-encodes values or builds secondary indexes during compaction, for faster analytic reads than RocksDB.

**Beats:** RocksDB — The test machine had two 16-core 3.0 GHz CPUs, 128 GB RAM and SATA SSDs on Ubuntu 20.04; the paper does not name the CPU model, compiler, flags or RocksDB version. After a 100 GB preload of 200M records, Mycelium's JSON-to-FlatBuffers transform cut latency 4.25x on Q2 (MAX over a key range, Zipfian keys) against RocksDB storing JSON, and split cut it 2.8x; single transforms cost 10-15% of write throughput and split+convert cost 21%. The index-query wins are measured against RocksDB full scans, and the paper's setup text is internally inconsistent (32 vs 50 columns per row, stated as about 500 B).

**Known shortcoming:** The 4.25x is Q2 query latency after converting JSON to FlatBuffers during compaction, not throughput; writes cost 10-21% more. Only a probable anonymous code repo (anon-rev-repo/mycelium-anon, no licence) and no link from the paper.

**Known shortcoming:** The paper links no repo; attribution to anon-rev-repo/mycelium-anon is inferred (one squashed commit, 0 stars, no top-level license). Its Scan ignores begin_key and the column list, and split-row reassembly is commented out, so the paper's Q2-Q7 are not reproducible as shipped.

**Known shortcoming:** Column-family tree updates are not atomic (separate LogAndApply per family); delete scans the whole index family; the index misses memtable/L0. Build needs Arrow (not in README), experiment scripts are missing, an x86-64 re2 path is hard-coded, errors exit(1). Paper is inconsistent (32 vs 50 columns per row); 4.25x is only vs a JSON baseline and row queries are slower under split.

**How:** Compaction already reads every record from its SST files and writes it back out. Mycelium does the transformation during that same pass, adding in-memory CPU work but no extra read I/O (the paper calls this 'transformation-embedded compaction'). A cross-column-family compaction writes the source family's merged L0 runs into a destination family's L0, and 'Tierveling' uses tiering for compactions that transform data and leveling for identity compactions. Reads speed up because they touch less data: a column-group split cuts the bytes read and deserialized by single-column queries, JSON-to-FlatBuffers made SSTs 34.76% smaller, and a secondary index replaces a full table scan.

**Use it when:**
- Research or prototyping, when you want to measure whether ETL done during compaction (column-group splitting, format conversion, index building) beats a separate pipeline on your own write-heavy data.
- Write-heavy ingest of wide rows (the paper uses rows of about 500 B with 32-50 columns) where later reads project one or a few columns or aggregate over key ranges. On a range MAX query, split gave 2.8x and JSON-to-FlatBuffers gave 4.25x.
- Values arrive as text JSON and you can accept about 15% lower write throughput to have them stored in a compact binary format.
- You need lookups on a non-key attribute and can accept an index that covers only data already compacted out of L0. The paper measured about 10% write-throughput cost for this.

**Skip it when:**
- Production, or anywhere you need clear licensing. The paper does not link any code. The probable repo is an anonymous single-commit snapshot with no top-level license.
- Row-retrieving workloads (SELECT * point or range queries). Under the split transform, the point query (Q7) was slower than plain RocksDB at most percentiles, and the range query (Q6) had worse tail latency.
- Systems bound by write throughput. Each transformation cost 10-21% of RocksDB's write throughput in the paper, and each extra cross-column-family compaction adds write amplification (the cost model's WA + n).
- Delete-heavy tables with a secondary index. In the repo, every Delete scans the whole secondary-index column family to find matching entries.
- Workloads that need read-your-writes through the index. Index entries are created only when data leaves L0, and IndexRead never checks the memtable or L0.

**Vs siblings:** Every catalogued sibling (KVell, MatrixKV, PebblesDB, SplinterDB, Nova-LSM, NuDB, Titan) speeds up the write or key-lookup path. Mycelium is the only one that reshapes data for column-projection and non-key reads, so consider it only when those reads are the bottleneck. For anything you will ship, Titan (large values) and SplinterDB or PebblesDB (write-heavy loads) have public, licensed code.

**Gotchas:**
- In the probable repo, MymBroker::Scan ignores begin_key (it calls SeekToFirst) and ignores the column list, and the code that reassembles split rows in Read/Scan is commented out. The paper's Q2-Q7 query paths therefore cannot be reproduced from this harness as shipped.
- Updates across the tree family are not atomic. The manifest edit for the source column family and the edit for each destination family are separate LogAndApply calls. Delete propagation issues a separate Delete per derived column family, and failures are logged and skipped. Crash consistency is not documented.
- Secondary-index keys are field values converted to strings and joined with '%%' and '$$$KEY$$$'. Numeric fields go through std::to_string, so the index sorts lexicographically rather than numerically, and values that contain the separators are ambiguous.
- Error paths print FATAL and call exit(1) instead of returning a status. More than 4 transformers, or transformer and SchemaDescriptor counts that don't match, throw std::runtime_error. The top-level CMakeLists also copies experiment/*.sh scripts that are not in the repo.

**Status:** Research prototype only: an arXiv v1 preprint (June 2025, UC Santa Cruz) whose code is 'hidden due to anonymity'. The probable code is an anonymous review repo (one squashed commit on 2026-07-27, 0 stars, no top-level license) that has already moved to newer names (WHLSM, LSM-Grove, mRoutines), so treat it as a reference, not a dependency.

[benchmark](https://arxiv.org/abs/2506.08923)

##### ToplingDB  `C++`  `GPL-2.0 OR Apache-2.0`  `active`  `Tier C`

RocksDB 8.10 fork with a trie memtable and searchable compressed SSTs; about 5x RocksDB's in-cache random-read throughput.

**Beats:** RocksDB — The project's own GitHub Actions dashboard (run 34935695406, 2026-09-15) ran db_bench with 50M 8-byte keys and 50-byte values, one client thread, and the DB on /dev/shm fitting inside a 7.8 GiB block cache. Hardware was an AMD EPYC 7763 with 4 vCPU and 15.6 GiB RAM on Ubuntu 24.04, with release builds at -march=haswell and the compiler unstated. ToplingDB zipkeyvalue did 1.74M readrandom ops/s against 349K for RocksDB 8.10.2 (4.98x) and 379K for RocksDB master (4.58x), with 2.50x fillrandom, 1.57x readseq and 0.62x compaction speed. The sides are tuned differently: ToplingDB uses a tuned YAML (512 MB write buffer, CSPP memtable as WAL index, zero-copy reads), while RocksDB uses db_bench defaults plus an OPTIONS file that mainly sets the L0-none/Snappy/L6-Zstd compression ladder.

**Known shortcoming:** The fair figure is zipkeyvalue 4.98x; the 13.5x zipkeyonly result stores values uncompressed. The ZipTable builder and CSPP memtable that produce the speedups are private and shipped as 90-day trial binaries; compiler not stated.

**Known shortcoming:** The default make silently downloads the private ZipTable/CSPP trial object files; behaviour after the 90-day expiry is undocumented. Linux only (#66, #67); only bytewise/reverse comparators; dynamic column families, user timestamps and wide columns are compiled out by default; its WAL format differs from RocksDB's.

**Known shortcoming:** Compaction is slower (0.30-0.62x; with distributed compaction fillseq 0.64x, fillrandom ~1.0x). Unequal tuning: ToplingDB uses a tuned YAML (512 MB write buffer, memtable as WAL index) while RocksDB runs db_bench defaults, and the data fits in cache. License is RocksDB's GPLv2/Apache-2.0 dual license.

**How:** ToplingZipTable SSTs pair a CO-Index (NestLoudsTrie, a nested LOUDS succinct trie mapping key to id) with PA-Zip (DictZipBlobStore, global-dictionary compression that can read one value directly). Both are searched while still compressed in mmap'd memory, so there is no block decompression or block cache, and uncompressed values go back to the caller zero-copy. The CSPP MemTable, a Crash-Safe Parallel Patricia trie, replaces the skiplist and uses integer offsets instead of pointers. So with memtable_as_log_index it can point into the WAL and be turned straight into an SST without a flush. Comparator calls are devirtualized and key-prefix caches were added in hot paths such as MergingIterator and FindFileInRange, which only works because these components are limited to bytewise key order.

**Use it when:**
- An existing RocksDB app on Linux x86-64 with bytewise-ordered keys where point lookups are CPU-bound and the data fits in RAM or page cache. The project's dashboard shows 3.7-5.0x single-thread readrandom (zipkeyvalue vs RocksDB v8.10/master across three suites) with 8-byte keys and 50-byte values.
- Scan-heavy work on small values: readseq is 1.6-1.9x RocksDB v8.10, and scans that skip loading values (ToplingDB's lazy value load) reach 3.6-4.8x.
- RAM- or disk-constrained nodes: in the fillrandom suite, zipkeyvalue used 0.56x RocksDB's disk and 18% of its RSS during readrandom. Page cache is counted separately.
- Teams that want YAML/JSON-defined DB configuration, online option changes and Prometheus metrics built in, and can either license the Enterprise components or run the open-source distributed-compaction workers (topling-dcompact) to absorb compression CPU.

**Skip it when:**
- You need a fully open-source build. The components that deliver the speedup, the ToplingZipTable builder (private topling-rocks) and the CSPP MemTable (private), ship only as precompiled 90-day trial objects. No published benchmark covers a build with both turned off.
- Windows or macOS: the maintainer says ToplingDB currently supports only Linux (issues #66, #67). The released JNI jar contains only librocksdbjni-linux64.so.
- Custom comparators: the CSPP MemTable supports only BytewiseComparator and ReverseBytewiseComparator, and the performance components are built around bytewise order.
- Compaction- or write-bound workloads on few cores: compaction runs at 0.62x (fillrandom) and 0.30x (fillseq) of RocksDB v8.10, and ZipTable compression costs about 2x zstd CPU. In the project's dcompact run with the write side capped at 50% CPU, fillseq was 0.64x RocksDB v8.10 and fillrandom only about 1.0x.
- Larger-than-memory datasets or apps that need recent upstream RocksDB features: every published run fits in cache, the code base tracks RocksDB 8.10.2, and dynamic column-family creation, user timestamps and wide columns are compiled out by default.

**Vs siblings:** Pick ToplingDB over Titan when values are tiny and reads dominate: Titan's catalogued gains grow with value size, while ToplingDB's come from 50-byte-value lookups and scans. Pick it over research engines such as PebblesDB, KVell or SplinterDB when you want to keep RocksDB's API and feature set. Prefer those siblings or F2 for write-heavy or larger-than-memory work, where ToplingDB's compaction is slower and its gains are unmeasured.

**Gotchas:**
- A default release make (DEBUG_LEVEL=0) tries an SSH clone of the private topling-rocks repo. If that fails, it silently wgets precompiled top_zip_table_builder.o and cspp_memtable.o from an Aliyun OSS bucket as 90-day trials. For a clean open build pass WITH_TOPLING_ROCKS=0 WITH_CSPP_MEMTABLE=0 together; CSPP cannot be on without topling-rocks. What the trial builder does after 90 days is not documented, though the ZipTable reader is open source.
- Dynamic ColumnFamily creation (ROCKSDB_DYNAMIC_CREATE_CF), user-level key timestamps and wide columns are disabled at compile time by default. RocksDB code that calls CreateColumnFamily at runtime needs a rebuild with -DROCKSDB_DYNAMIC_CREATE_CF.
- memtable_as_log_index is an immutable DB option with its own WAL format. All WALs must be flushed before you toggle it. A large WriteBatch can overflow the WAL mmap and fail with 'IO fenced off ... exceeds mmap size' unless max_total_wal_size is large enough.
- CSPP reserves mem_cap of virtual address space per memtable (default 2G, max 16G). The wiki warns that on Linux, touching that memory when the system has no free RAM segfaults instead of returning an error, unless explicit commit (MADV_POPULATE_WRITE, kernel 5.14+) is used.

**Status:** Actively maintained by Topling Inc (pushes through 2026-09-20, CI benchmark runs through 2026-09-15, 1016 stars). Usability is mixed: it is Linux-only, and the components behind the headline numbers are proprietary trial binaries. The open parts keep RocksDB's GPLv2/Apache-2.0 dual license, so the license is no stricter than upstream's.

[repo](https://github.com/topling/toplingdb) · [benchmark](https://topling.github.io/toplingdb/)

##### UStore (UDisk engine)  `C++`  `Apache-2.0`  `abandoned`  `Tier C`

Closed-source NVMe KV engine (UDisk) behind UStore's open C API; vendor numbers show 2-7x RocksDB throughput.

**Beats:** RocksDB — These are vendor-run UCSB numbers: apart from Batch Upsert, the README rows match Unum's September 2022 10 TB run of RocksDB 6.29.3 against UDisk (then 'UnumDB'), with 8-byte integer keys, 1 KB values, compression off, no flushing, 64 client threads and 256-key batches on an AMD Threadripper PRO 3995WX with 1 TB RAM, 8x Samsung PM1733 NVMe and Ubuntu 22.04 (kernel 5.15, ext4); no compiler is stated, and the README table gives no setup at all. Under those conditions batch reads ran ~6.9x and point reads ~2.4x faster, scans tied, and RocksDB won range selects ~2.5x.

**Known shortcoming:** The UDisk engine behind the numbers is closed source and binary-only; the table does not state the dataset size.

**Known shortcoming:** The README table comes from a 2022-09 10 TB post (Threadripper 3995WX, 8x PM1733, RocksDB 6.29.3 without WAL, 64 threads); the 260K batch-upsert figure matches no run (the post says 117K CPU, 182K GPU). The table omits Range Select, where RocksDB wins 5M vs 2M; RocksDB was capped at 4 db_paths; a 1 TB single-thread run shows reads only ~1.1x.

**Known shortcoming:** Cannot be reproduced: the UCSB benchmark's cmake clones a deleted main-dev branch and passes the wrong UDisk path variable, and UCSB has no license. UDisk has no public download; Linux only. Durability is off by default and the RocksDB adapter disables WAL. Abandoned since 2023-08; bug #434 (README RocksDB open fails).

**How:** Unum describes UDisk as a modified LSM tree built for NVMe block devices, with io_uring for partial kernel bypass, SPDK for full bypass, a custom internal filesystem and optional CUDA offload of background compactions. Its config offers posix, 'pulling' and 'polling' IO mechanisms with queue depths up to 4096, native fixed-size integer keys and optional fixed-size values. Batch reads go in as a group so the engine can reorder them and issue them asynchronously, which is where the widest gap over RocksDB's MultiGet shows up; none of this can be checked, because the source is closed.

**Use it when:**
- You have, or can negotiate, a UDisk binary from Unum and run Linux servers with several NVMe drives, where batched random reads and upserts of values around 1 KB dominate.
- Keys are naturally 64-bit integers (row IDs, graph vertex IDs) and you can send batches of hundreds of keys per call instead of single Gets; batch read is the vendor's largest win (650K vs 4.5M ops/s).
- You want one transactional C API over blobs, documents and graphs, with NetworkX- and Pandas-style Python front ends. You can start on the open UCSet or RocksDB engines and swap in UDisk later without changing application code.

**Skip it when:**
- You need an engine you can build, audit or patch: UDisk is binary-only, and UStore's own engine table marks it as not open source.
- Range-select-heavy workloads: in the vendor's own 10 TB run RocksDB did 5M ops/s against 2M for UDisk (then called UnumDB), and the README table leaves that row out.
- Non-Linux targets, or code that relies on RocksDB features such as string keys with custom comparators, prefix seeks and column-family options. UDisk is Linux-only and links liburing, libnuma and libexplain.
- You need durable writes by default. UStore turns durability off unless you pass ustore_option_write_flush_k, and its RocksDB adapter sets disableWAL whenever that flag is missing.
- Production systems that need a live upstream: main was last committed 2023-08-18, and open bugs include the README's rocksdb.DataBase('/path') example failing to open (#434).

**Vs siblings:** Pick UDisk only if you have a commercial path to the binary and a batch-heavy, integer-keyed workload on Linux machines with several NVMe drives; for an engine you can build and audit, SplinterDB (6-10x faster inserts and 2-2.6x faster point queries than RocksDB), KVell or F2 (FASTER) have open code and better evidence. UStore's open parts only beat them if you want its multi-modal API over RocksDB or UCSet, not for speed.

**Gotchas:**
- The December 2022 table matches Unum's September 2022 10 TB post row for row except Batch Upsert. The post gives UDisk 117K ops/s on CPU and 182K with a GPU, not 260K, so no published run backs the ~4.6x upsert figure. The table also leaves out Initialization (603K vs 60M) and Range Select, where RocksDB won.
- The setup favored UDisk. In the post each engine got 8 SSD partitions, but RocksDB can take at most 4 db_paths and ingested SSTs land on the first disk. The UCSB RocksDB adapter runs with the WAL disabled. In the earlier single-threaded 1 TB run the gaps were much smaller: random reads 175.7K vs 160.7K (~1.1x), batch insert 813K vs 690K (~1.2x).
- Reproduction is blocked even with a binary. UCSB's cmake/ustore.cmake clones a 'main-dev' branch that no longer exists and passes -DUSTORE_ENGINE_NAME_UDISK_PATH, while UStore's CMake reads USTORE_ENGINE_UDISK_PATH. UCSB also has no license, and its committed RocksDB 10TB.cfg says 7.2.9 while the post says 6.29.3.
- The PyPI package is 'ukv' (imported as ustore.*), not 'ustore'; issue #383 shows users confused by the ukv/ustore/ucset naming. Per #434, opening RocksDB works only when you pass a JSON config with create_if_missing, not a bare path.

**Status:** Abandoned: main (the only branch) was last committed 2023-08-18 at v0.13.12, and neither UStore nor the placeholder UDisk repo links a public UDisk download, so the Apache-2.0 bindings still work with RocksDB, LevelDB and UCSet but the engine this entry measures is out of reach.

[repo](https://github.com/unum-cloud/UStore) · [benchmark](https://github.com/unum-cloud/UStore/blob/main/benchmarks/README.md)

#### indexes

##### MountDB (learned indexing integrated into RocksDB)  `C++ (no code released)`  `no license`  `unknown`  `Tier C`

Paper-only RocksDB v8.10 extension replacing SkipList memtable and fence-pointer index with learned indexes; up to 1.77x reads.

**Beats:** RocksDB v8.10.0 (plus the learned-index LSMs DobLIX and TridentKV, ported to RocksDB 8.10.0) — The authors ran db_bench on a 2x Xeon E5-2690 v4 machine with an NVMe SSD (16 client threads, 64 MB Memtables, compression off, 8-byte keys and 100-byte values, about 55 GB and 500M operations per dataset). They report up to 1.3x write-only, 1.44x balanced and 1.77x read-only throughput over stock RocksDB v8.10.0, rising to 2.8x for reads at 16 B values. No compiler or flags are given, and no independent reproduction exists.

**Known shortcoming:** arXiv preprint with no code. The abstract's 1.5x/2.1x is vs DobLIX/TridentKV; vs RocksDB it is up to 1.77x reads (2.8x at small values) and ~1.3x writes.

**Known shortcoming:** Numeric keys only, compression off, pinned to RocksDB 8.10; deletes and recovery are not discussed. With direct I/O all systems are about equal and with 10% cached the gain is 1.2-1.3x; block size was cut to a third for the 3-block read and it is unclear whether baselines matched. Baselines were ported by the authors (DobLIX without its RL tuner); the lead author's GitHub has only a plain RocksDB fork and a DobLIX port.

**How:** In memory it uses ALEX+ (the concurrent variant of ALEX, with gapped arrays and model-based placement) plus 'skeletonization': every 10 flushes (phi=10) a background task bulk-loads ALEX+ from the immutable Memtable's sorted keys and strips payloads, counters and locks. New Memtables then start from that model hierarchy and gap bitmap instead of cold. Without this, a 64 MB ALEX+ Memtable is flushed about every 0.4 s, before it converges, and ends up no better than SkipList. On disk, PGM (Fence) trains a PGM-index with epsilon=1 on only the first key of each block. A lookup therefore predicts a block and reads it together with both neighbours in one FilePrefetchBuffer I/O, and the resulting index is about 172 KB per 64 MB SST, versus 296 KB for RocksDB's fence table.

**Use it when:**
- You are designing or evaluating learned indexing inside an LSM store and want a worked recipe (an ALEX+ Memtable with skeleton reuse, and PGM over fence keys) that leaves RocksDB's SST and block format unchanged.
- Read-heavy RocksDB workloads with numeric 8-byte keys and a mostly cached working set: up to 1.77x over RocksDB on read-only, and 1.34-1.52x over all baselines when the data is fully cached.
- Small values (16-64 B): up to 2.8x read and about 1.5x write throughput over RocksDB at the smallest sizes, and 1.3-1.6x reads on the mixed-size UDB, ZippyDB and UP2X traces.
- Write-heavy ingest with smooth or slowly shifting key distributions, where the reused skeleton stays accurate: up to 1.3x write-only, and 0.95-1.05 vs 0.6-0.7 Mops/s (98 s vs 161 s) in the microbenchmark that cycles through six distributions.

**Skip it when:**
- You need working code. Nothing is released: the lead author's GitHub has only an unmodified RocksDB fork and a DobLIX port, so you would reimplement MountDB against RocksDB internals yourself.
- String or variable-length keys: the design and evaluation cover numeric keys only, and learned string indexing is left to future work.
- I/O-bound reads: with use_direct_reads, throughput was 'virtually the same' across all systems, and with only 10% of the data cached the gain shrinks to 1.2-1.3x.
- Irregular key distributions or abrupt distribution shifts: write gains narrow to about 1.2x on OSM, and a never-refreshed skeleton lost throughput when the distribution changed.
- Production use: it is an unreviewed preprint pinned to RocksDB v8.10.0, evaluated with compression disabled, and it never discusses deletes, recovery or the rest of RocksDB's feature surface.

**Vs siblings:** Compared with Bourbon, MountDB's design also speeds up writes (Bourbon indexes only the disk component and depends on WiscKey's key-value separation) and keeps RocksDB's SST format, but Bourbon ships an artifact and MountDB ships none. If you need something runnable against RocksDB today, the practical routes are TerarkDB (a RocksDB fork with code) or building directly on the ALEX and PGM-index libraries.

**Gotchas:**
- The abstract's 'up to 1.5x write, 2.1x read' is measured against DobLIX and TridentKV (the 2.1x only at the smallest value size), not against RocksDB. Against stock RocksDB at the default 100 B values the figures are 1.3x write-only, 1.44x balanced and 1.77x read-only.
- PGM (Fence) always reads three blocks (the predicted one plus or minus one), so MountDB cuts the maximum block size to a third of the default. The paper says the baselines had identical Memtable, cache and compaction settings, but it does not say whether their block size was matched.
- Skeletons are a partial deep copy of the previous Memtable's ALEX+ nodes (keys and gap bitmap, with null payloads). Their memory cost is not quantified, and the refresh interval phi=10 was chosen empirically.
- The authors ported the DobLIX and TridentKV baselines from RocksDB 5.x to 8.10.0 themselves, and the DobLIX code lacks its paper's RL tuner, so the learned-LSM comparisons are against reduced versions.

**Status:** This is an arXiv preprint from McGill (v1, 22 May 2026; not peer-reviewed as of 2026-09-26) with no released code or license, so it is a reference design only, and its maintenance status is unknown.

[benchmark](https://arxiv.org/abs/2605.23815)

##### PGM++ (adaptive search-strategy PGM-index)  `C++`  `no license`  `stale`  `Tier C`

Research patch to PGM-index static lookups: hybrid branchless/linear segment search plus cost-model epsilon tuning, up to 2.31x faster.

**Beats:** PGM-index — The PVLDB 2025 paper reports up to 2.31x faster lookups than the original PGM-Index and up to 1.56x faster than CDFShop-tuned RMI at comparable index size. It tested 4 SOSD datasets (fb and wiki at 200M uint64 keys, books and osm at 800M) plus 3 synthetic sets, on an i7-13700K and 2x EPYC 7413 with g++ 11.4 and on an Apple M3 with clang++ 15; the body gives 1.2x-2.2x over PGM at equal eps_l. There is no stdlib or B+-tree baseline in the static comparison, and optimization flags are unstated. The public harness times 5,000 lookups per round, each wrapped in its own high_resolution_clock pair, and its documented build has no -O flag, while the paper's text says 100M lookups.

**Known shortcoming:** Code exists at qyliu-hkust/bench_search but has no LICENSE (usability mixed) and is stale since 2025-02; the documented builds pass no -O flag, so published numbers may be -O0; paper in PVLDB 18(9) 2025.

**Known shortcoming:** The in-repo 'PGM' baseline sets linear_search_threshold=0 (always std::upper_bound) whereas upstream PGM linear-scans at eps <= 32, so the baseline is not upstream's code path. The code implements only part of the paper (layer bypassing commented out; no cost-model tuner, DPGM++ or last-mile linear scan). Branchless lower/upper_bound never return end (keys above the max get the last element; untested because queries use existing keys). The harness times 5k lookups per round individually while the paper says 100M; RMI still wins on normal/lognormal; code stale since 2024-10.

**How:** The paper finds PGM lookups are memory-bound and dominated by the internal error-bounded searches, which take 69-81% of lookup time in its Table 7. Upstream does these with std::upper_bound once eps_i is above a small threshold. PGM++ replaces them with a CMOV-style branchless binary search (base = base[half-1] < k ? base + half : base), falls back to a linear scan for tiny ranges, and uses the branchless search for the last-mile step too; per the Table 9 ablation, removing this makes lookups 39-60% slower. The paper adds two more pieces: 'layer bypassing', which starts the descent at the first level whose child level is dense (12-22% in the same ablation), and a calibrated cost model that estimates leaf-segment count from gap mean/variance via kernel change-point detection on a 0.05% sample and then picks the eps_i with the lowest modeled lookup cost.

**Use it when:**
- You already use the static pgm::PGMIndex on sorted 64-bit integer keys and profiling shows the internal segment search dominates. Porting the ~20-line branchless bound from exp_pgm/search_algo.h is the cheap change behind the paper's 1.2x-2.2x at equal eps_l.
- Read-only lookups over large in-memory sorted arrays (200M-800M uint64 keys in the paper) where you want a learned index with a guaranteed maximum error instead of RMI's data-dependent error (the paper measured RMI max error up to 1.77M positions on osm).
- Tight index-memory budgets: the paper reports a 0.1 MB PGM++ beating a 100+ MB CDFShop-tuned RMI on the wiki dataset.
- Reproducing or extending the study. exp_pgm/main.cpp sweeps the full eps_l x eps_i grid over {4..1024}, and exp_rmi/ holds the pre-generated CDFShop RMI models for all 7 datasets.
- Hosts with relatively low memory latency. On osm the average gain over PGM was 1.78x on the i7-13700K and Apple M3 but only 1.32x on the EPYC 7413 server.

**Skip it when:**
- As a production dependency. This is a benchmark harness with no LICENSE for the PGM++-specific files, no tests, no build system beyond a one-line g++ command, and no code changes since 2024-10-02.
- Updatable workloads. The repo contains only the static PGMIndex; the paper's DPGM++ is not published there, and even in the paper ALEX has the highest throughput on every mix except write-heavy (80%) and write-only.
- Keys that follow smooth normal or lognormal distributions: in the paper, CDFShop-tuned RMI (with cubic-spline models) beats both PGM and PGM++ there.
- Code that probes keys larger than the maximum indexed key, or that relies on getting end(): the branchless helpers never return the end iterator (see gotchas).
- If you need upstream's other structures (DynamicPGMIndex, compressed/bucketing/Elias-Fano variants, multidimensional). Only pgm_index.h and piecewise_linear_model.h are vendored.

**Vs siblings:** Pick it over the PGM-index sibling only when you want PGM's guaranteed error bound with faster static lookups and are willing to vendor unlicensed research code, or just port its branchless search. CHT (which reports 1.7-2.5x over PGM), RadixSpline and RMI are different static designs, RMI still wins on normal/lognormal keys, and ALEX or LIPP are the choice when you need inserts.

**Gotchas:**
- search::lower_bound_branchless and upper_bound_branchless never return end. When every element in the range is below (or not above) the key, they return the last element instead. I checked a Python port of the exact loops against bisect on 20k random cases, and every mismatch was this end case. The benchmark only queries existing keys, so this path is never exercised.
- Build flags: the README command and exp_rmi/Makefile_all pass no -O flag, so the documented builds compile both PGM and PGM++ at -O0, and the paper does not state flags. Re-measure at -O2/-O3 before trusting the ratios.
- The artifact's 'original PGM' baseline is PGMIndex<..., false, 0, float>. linear_search_threshold=0 forces std::upper_bound on every internal level, whereas upstream master linear-scans when EpsilonRecursive <= 8*64/sizeof(Segment) = 32. For eps_i of 4-32 the in-repo baseline is therefore not upstream's code path.
- The code covers only part of what the paper's ablation credits. Layer bypassing is commented out in segment_for_key (start_level is computed but unused), the last-mile search has no linear-scan branch, and the KCPD/cost-model tuner is absent.

**Status:** Stale, low-adoption research artifact: 6 stars, code last touched 2024-10-02 (README 2025-02-01), no LICENSE for the PGM++ files (the vendored PGM headers keep Apache-2.0), and upstream PGM-index issue #58, which proposed upstreaming it, has had no reply since 2024-10-20.

[repo](https://github.com/qyliu-hkust/bench_search) · [benchmark](https://www.vldb.org/pvldb/vol18/p2886-liu.pdf)

#### message-queues-logs

##### Harper (formerly HarperDB)  `JavaScript (unverified - Harper's source is not public; only the benchmark harness is)`  `The Harper Pro image under test is Elastic-2.0 (source-available, non-OSI; source at github.com/HarperFast/harper-pro). The open-source Harper core (github.com/HarperFast/harper) is Apache-2.0, and the benchmark harness is Apache-2.0.`  `active`  `Tier C`

Node.js runtime fusing RocksDB-backed tables, app code and MQTT/WebSocket pub/sub; vendor benchmark: lower latency than Kafka stacks at ≤1k events/s.

**Beats:** Apache Kafka (plus Postgres/Redis/Debezium/Kafka Streams ecosystem, workload-dependent) — This is a Harper-affiliated whole-stack benchmark run in one OrbStack VM on an Apple Silicon Mac (24 GB, 8 vCPU; chip not stated). It pits a 3-node Harper Pro cluster (digest-pinned image, RocksDB default) against 3 Kafka brokers at RF=3 plus Postgres/Debezium/Redis/Kafka Streams as each workload needs. Harper's p50 was 9.4 ms vs 876 ms with Go glue, or 523 ms with language-matched Node glue, which the authors' own decision log adopts as the headline (~56x, not ~100x); 12.5 ms vs 165 ms on W2; 1.05 s vs 3.65 s on W3 freshness; and 1.4 ms vs 57 ms on W4 at 1,000 events/s, while Kafka Streams won point lookups (2.75 ms vs 17 ms). The runs were short (15-30 s at 10-1,000 events/s, 3 paired runs, one run per stack for W3), W1 delivered only 83-84% on both stacks although the README says 100%, and a containerized Harper W4 variant cut the W4 gap to about 10-20x.

**Known shortcoming:** Vendor benchmark on an Apple Silicon M-series OrbStack VM; the open-source core is Apache-2.0 but harper-pro features are Elastic-licensed.

**Known shortcoming:** The W1 ~100x is stale (its own decision log says ~56x); runs are tiny (15-30 s, 3 runs, W3 one run) and W1 delivered only 83-84% on both stacks (the README says 100%). Harper's notify is an awaited HTTP call in the handler, not durable, and per-thread load produced 7-21x duplicate notifies; the containerized MQTT variant is ~10-20x, not 40x. Replication is only in Harper Pro (ELv2); subscriptions can drop up to 88.5% of intermediate changes under burst (#2483), bad for CDC/log use; not a Kafka-protocol drop-in.

**How:** The speedup comes from removing hops. The durable write, the enrichment lookups and the downstream notify all run in one process against embedded RocksDB (the `@harperfast/rocksdb-js` native binding; LMDB is the legacy engine), with a WeakRef-based LRU record cache, so there is no network or serialization step between database, cache and broker. Subscribers are fed from the audit (transaction) log: each 'committed' event schedules one `setImmediate` pass that walks the log and dispatches to per-key subscriber maps on every worker thread. Bursts collapse into one pass, and a QoS 0 MQTT frame is encoded once and shared by all matching subscribers. In the benchmark, the conventional stack pays for Debezium's WAL polling (the authors estimate 100-300 ms, not measured) and for a 50 ms Kafka consumer batch window, and Harper's MQTT path has neither.

**Use it when:**
- Write-then-notify or filtered fan-out at tens to about 1,000 events/s, where you would otherwise wire up Postgres + Debezium + Kafka + Redis. The benchmark measured 9.4 ms vs 523 ms p50 at 50 events/s and 12.5 ms vs 165 ms at 10 events/s.
- Pushing live state to browsers or devices over MQTT or WebSockets when the consumer needs the latest value per key, not every intermediate change.
- Live dashboards with windowed aggregates at low per-key event rates, where Kafka Streams' suppress-until-window-close holds back results (W3 freshness: 1.05 s vs 3.65 s p50, 1.56 s vs 13.6 s p95).
- Node.js teams that want the database, API and pub/sub in one deployable unit, and that accept Harper Pro (Elastic-2.0) or Harper Fabric for multi-node.

**Skip it when:**
- Throughput-bound log ingestion at 10^5-10^6 events/s. The benchmark never ran a steady state above about 1,000 events/s, and its authors expect Kafka to win or tie on real multi-node hardware.
- CDC, event sourcing or audit consumers that need every change. Record subscriptions over in-process subscribe(), SSE and MQTT coalesce intermediate updates under burst writes, dropping up to 88.5% at threads: 4, with no gap marker (harper#2483, open).
- Point reads against live aggregates. Kafka Streams Interactive Queries answered in 2.75 ms p50 vs Harper's 17 ms through a REST endpoint.
- Stacks that depend on Kafka clients, Connect, Streams or Schema Registry, because Harper does not speak the Kafka protocol.
- When you need OSI-licensed multi-node replication. Replication ships in Harper Pro under Elastic-2.0, which forbids offering it as a hosted or managed service.

**Vs siblings:** Choose Harper over standalone brokers such as NATS JetStream, RabbitMQ or Mosquitto when the broker would otherwise sit beside a separate database and cache, and your app logic can run as Node.js inside the same process. Choose Redpanda or AutoMQ instead when you need Kafka API compatibility and Kafka-scale throughput.

**Gotchas:**
- In the benchmark's Harper handlers, async work fired after the handler returned was cancelled (most fire-and-forget notifies were dropped). The harness therefore awaits an outbound HTTP notify inside the request. That notify is logged on failure and never retried, unlike the durable Debezium-to-Kafka path it is compared against.
- Resource modules load once per worker thread. A table.subscribe-based notifier fired about 7 times per node (21 times across 3 nodes), and W3 window-close notifies fired 2-21 times. At benchmark time there was no leader-election or compare-and-swap primitive to deduplicate them.
- Durability comparable to Kafka's acks=all must be opted into per request with `this.getContext().replicatedConfirmation = N`, where N counts peers. The default is async replication, and the MQTT broker has no per-write confirmation.
- Several subscription bugs are open: ending a subscription during fan-out makes the next subscriber miss that event (#2771), deletes are reported as empty puts or bare nulls (#2738, #2438), and startTime replay drops events committed after the audit cursor ends (#2311).

**Status:** The core is under active development: v5.2.14 and v5.3.0-beta.3 were released 2026-09-25, and the repo has 941 open issues and 90 stars. The core is Apache-2.0, but the replication behind the benchmarked 3-node setup is Elastic-2.0 Harper Pro, and the benchmark repo is a 0-star snapshot created and last pushed on 2026-05-28.

[repo](https://github.com/HarperFast/harper) · [benchmark](https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/README.md)

##### Redpanda  `C++`  `BUSL-1.1 (core; converts to Apache-2.0 four years after each release) + Redpanda Community License (enterprise features); GitHub reports no SPDX id`  `active`  `Tier C`

Kafka-API-compatible streaming broker in C++ on Seastar; vendor OMB runs show 12-70x lower p99.99 latency than Kafka.

**Beats:** Apache Kafka — Redpanda's own 2022 OpenMessaging Benchmark (v22.2.2 vs Kafka 3.2.0, TLS+SASL-SCRAM, 1:1 read/write, 4 partitions per core, i3en brokers, 4x m5n.8xlarge clients, no CPU model or build/JVM flags given) measured p99.99 latency of 13.9 / 16.7 / 79.6 ms vs Kafka's 164.6 / 388.7 / 5509.7 ms at 50 MB/s, 500 MB/s and 1 GB/s. Kafka had 3/4/6 brokers against Redpanda's 3, ran on Java 11, and was set to fsync every batch (log.flush.interval.messages=1). A 2023 vendor rerun against Kafka 3.4 KRaft showed a similar pattern (p99.9 24.4 ms vs 98.0 ms on i3en.6xlarge, 3 vs 6+3 nodes). Confluent's Jack Vanlightly repeated the test on 3x i3en.6xlarge with Kafka at default durability and Java 17 and could not reproduce the gap, so treat 12-70x as a vendor best case.

**Known shortcoming:** Vendor benchmark; Confluent's 2023 re-run (Vanlightly) disputes it. Kafka ran on 4-6 nodes vs Redpanda's 3 in the vendor setup. BUSL-1.1 plus Redpanda Community License (not OSI).

**Known shortcoming:** The 70x is the vendor's best case (Kafka forced to fsync per batch, Java 11, more nodes); Vanlightly's re-run did not reproduce it. Degrades under load in that re-run: 50 producers ~24 s end-to-end, keyed ~330 MB/s vs Kafka 500, 12 h p99.99 of 26 s, backlogs that never drain. BSL-1.1 forbids offering it as a hosted streaming service. Linux only, takes over cores, needs ~2 GB RAM per core; dev mode skips fsync. Kafka wire-compatible but missing request_percentage quotas, server-side KIP-890 and multiple SCRAM credentials per user.

**How:** It uses a thread-per-core, shared-nothing design built on Redpanda's fork of the Seastar framework. There is one pinned reactor thread per core, memory is allocated up front and split per core, cores talk by message passing instead of locks, and all I/O runs as futures/coroutines rather than OS-scheduled threads. The storage layer skips the Linux page cache: segment_appender batches data into page-aligned chunks and issues Seastar dma_write calls with adaptive fallocate, and reads come from a per-shard LRU batch_cache that Seastar's memory reclaimer can shrink. There is no JVM, so no GC pauses (the vendor's stated cause of Kafka's tail latency). The build has Clang ThinLTO and PGO configurations.

**Use it when:**
- You already use Kafka clients and need low p99.9/p99.99 produce-to-consume latency with acks=all and fsync before ack (Redpanda's production default), on dedicated Linux hosts with local NVMe.
- Moderate partition counts with well-batched producers, where you want fewer brokers and no JVM/GC tuning. The vendor ran 50 MB/s to 1 GB/s on 3 i3en brokers against 3-6 Kafka brokers.
- You want one binary with built-in consensus (Raft; no ZooKeeper or KRaft controller quorum), plus schema registry, HTTP proxy and tiered storage, on x86-64 or Arm64 (the vendor claims about 2x the 50 MB/s workload on Arm is4gen.medium).
- Local development and CI against the Kafka API: `rpk container start` brings up a local cluster via Docker (dev mode, not durable).

**Skip it when:**
- You would offer it to third parties as a hosted streaming or queuing service. BSL 1.1 forbids that until each release's change date (4 years), and enterprise features need an RCL license.
- Many producers, many partitions, small batches or keyed records. Vanlightly's independent re-run saw about 24 s end-to-end latency with 50 producers, a cap near 330 MB/s with record keys (288 partitions, 100 producers) while Kafka reached the 500 MB/s target, and consumer backlogs that never drained under 800 MB/s-1 GB/s produce load. He attributes this to small 16 KB fsync'd writes across many partitions (about 200K fsyncs/s).
- Long sustained runs or disks sitting at their retention limit: the same re-run measured p99 3.5 s and p99.99 up to 26 s after about 12 h, with step increases once retention kicked in. With acks=1 at NVMe saturation, Kafka reached 1900 MB/s against Redpanda's 1400 MB/s.
- Shared or containerised hosts, macOS/Windows production, NFS or IPv6-only networks. It needs Linux (RHEL 8+/Ubuntu 20.04+, kernel 4.19+ recommended), x86-64 Westmere+ or aarch64, XFS/ext4 on local SSD, IPv4, and at least 2 GB RAM per core plus 2 MB per partition replica. Thread-per-core assumes it owns its cores.
- You depend on Kafka request-rate quotas (request_percentage), KIP-890 server-side transaction defense, or several SCRAM mechanisms per user.

**Vs siblings:** Pick Redpanda over FluxMQ (a Rust Kafka-compatible broker claiming 20 implemented Kafka APIs, 8 stars) when you need a production-grade Kafka-protocol broker with Raft replication, tiered storage and years of regular releases. Pick it over Woodpecker (an embedded Go WAL on object storage with its own API, no topics or consumer groups) or Zenoh (a different pub/sub protocol) when your applications must keep speaking the Kafka API.

**Gotchas:**
- Development mode (the default for rpk container/dev setups) skips fsync, runs --overprovisioned and turns off the tuners. rpk's own help says this gives 'unrealistically fast clusters and may result in data loss', so only benchmark in production mode after `rpk redpanda tune`.
- write.caching / write_caching_default turns acks=all into 'acked by a majority in memory, fsync later' (flush.ms/flush.bytes), which is roughly Kafka's default durability. It is on by default in dev mode, off in production, and never applies to transactions or consumer offsets. Check which mode any comparison used.
- Seastar's per-core heap fragments. The project's own guide says contiguous allocations over 128 KiB after startup can fail even when plenty of memory is free, and 'oversized allocation' bugs keep appearing (e.g. #22737, #18325). Memory is budgeted per core and per partition, so size RAM to cores × partitions.
- Licensing is split: the core is BSL-1.1 (becomes Apache-2.0 four years after each release) and enterprise features are under the Redpanda Community License. GitHub reports no SPDX id, so automated license scanners may flag it.

**Status:** Very active (v26.2.2 and v26.1.17 released August 2026, 12.6k stars, 525 open issues) and shipped as prebuilt packages, so you deploy it as a server rather than vendor the code; read the BSL terms before offering it as a service.

[repo](https://github.com/redpanda-data/redpanda) · [benchmark](https://redpanda.com/blog/redpanda-vs-kafka-performance-benchmark)

##### SocketPro  `C++`  `no license`  `abandoned`  `Tier C`

C++ async RPC framework with a built-in persistent server queue; the vendor claims 3.6-54x RabbitMQ's enqueue/dequeue speed.

**Beats:** RabbitMQ — The vendor's 2016 study (PDF in the repo, HTML archived in 2020) enqueued and dequeued 100,000 persistent 200/1024/10240-char messages with the RabbitMQ .NET tutorial clients (RabbitMQ version, compiler and flags not stated). On one i7-4770 running Windows 8.1, SocketPro was 3.6-26x faster (200-char dequeue 14,129 -> 544 ms). Across 1 Gbps to a 4 GB Xeon E5-2630 v2 Windows Server 2012R2 VMware broker it was 4.3-10.9x faster on enqueue and 9.8-54x on dequeue (200-char dequeue 44,400 -> 820 ms), with RabbitMQ's consumer limited to prefetch 1 and per-message acks. A separate 2017 in-repo study against Kafka 0.10.1.1 (acks=1, Ubuntu 16.04, i7-4770, 7200-rpm HDD) reported SocketPro about 20-25% faster at writing medium and large messages, but Kafka about 20% faster on unbatched 4-32 B messages.

**Known shortcoming:** The live evidence page is gone (DNS dead); only a 2020 Wayback copy remains. No LICENSE file and the core ships as prebuilt binaries. Baseline is RabbitMQ, outside the category's list.

**Known shortcoming:** The 54x is mostly a configuration artifact: the in-repo RabbitMQ consumer uses prefetch=1 with a manual ack per message (one round trip each, ~444 us/msg flat across sizes) and no publisher confirms. SocketPro's queue defaults to memory-cached and the bench server never flushes, so its 'durable' numbers aren't disk-committed. An in-repo 2017 Kafka comparison (0.10.1.1, percentages only) has Kafka ~20% faster on unbatched 4-32 B messages and SocketPro ~20-25% faster on medium/large. Closed binary core (.dll/.so), 'enterprise license', x86-64 Linux/Windows only; proprietary non-AMQP protocol; abandoned since 2023-02; vendor site dead.

**How:** Requests are pipelined: a client keeps sending without waiting for replies, and both the client and server cores merge pending requests and results into full TCP packets. The vendor calls this 'inline batching', and Nagle's algorithm is disabled. Each Dequeue returns a batch of messages (16 KB by default, 32 KB in the benchmark server), and the benchmark keeps three Dequeue requests in flight so that disk reads, network transfer and client parsing overlap. On the server, enqueues under 4 KB run on the main thread to avoid a thread handoff, and EnqueueBatch commits many messages as one job. Two more factors matter. Queue writes default to oMemoryCached, which buffers them in process memory (revision 6.0.2.5), with FlushQueue pushing them to the OS cache or disk. The storage engine lives in the closed-source server core binary, so its file format and indexing cannot be inspected.

**Use it when:**
- You already build on SocketPro RPC (C++, .NET, Java, Python or Node.js) and want a work queue served from the same server process and port, without running a separate broker.
- Windows or x86-64 Linux hosts where producers stream many 200 B-1 KB messages and consumers drain in bulk, especially over higher-latency links where pipelining hides round trips. The vendor's largest gains are in this range.
- Producers must not lose messages during broker or network outages. An optional client-side queue file backs up every request and replays it after reconnect, and the tutorial shows this surviving repeated server kills.
- You are maintaining or re-measuring a legacy UDAParts deployment. The in-repo qperf drivers (C++, C#, Java, RabbitMQ C#) and the Kafka command lines let you rerun the comparisons.

**Skip it when:**
- You need AMQP, MQTT or the Kafka protocol, exchange or topic fan-out semantics, clustering or quorum queues, or ecosystem tooling such as a management UI. None of these exist, and the only way to interoperate is through SocketPro adapters.
- You need license-clear or auditable code. There is no LICENSE file, the client and server cores ship only as prebuilt .dll/.so files, and the changelog mentions an 'enterprise license'. Only the adapters and plugins such as the queue come as source.
- Tiny (4-32 B) messages without manual batching: the vendor's own 2017 Kafka study found Kafka about 20% faster at both writing and reading them. In that study, cross-machine dequeue of medium and large messages was roughly equal to Kafka.
- You need maintained software or other platforms. The last commit was in February 2023, issues #3 and #4 (2017, 2019) have no replies, there are no GitHub releases, and binaries exist only for x86-64 Linux, Windows x86/x64 and a Windows CE client. There are none for macOS or aarch64.
- You need per-message disk durability by default. Queues default to oMemoryCached, and a signal handler writes cached messages to the file on shutdown. Behavior on kill -9 or power loss is not documented.

**Vs siblings:** The siblings replace Kafka, NATS or ZeroMQ (Redpanda, Woodpecker, FluxMQ, Zenoh, Wisp, TCPSHM), and none targets RabbitMQ-style work queues. Pick SocketPro only if you are committed to its RPC framework and want the queue inside that server. For a maintained, durable, open log use Redpanda, and for crash-recoverable broker-less C++ point-to-point messaging use MIT-licensed TCPSHM.

**Gotchas:**
- The benchmark is not like-for-like. The RabbitMQ consumer in samples/qperf/rabbitmq/Program.cs sets BasicQos prefetch=1 and acks every message manually, so it pays one round trip per message. Cross-machine RabbitMQ dequeue took 44.4 s for 200-char and 45.4 s for 1024-char messages (about 444 us per message, flat with size), which fits that bottleneck. RabbitMQ enqueue timing stops when the BasicPublish loop returns (no publisher confirms), while SocketPro's waits for every server reply.
- The benchmark servers (cperf sq_server.cpp and the C# sq_server) never call FlushQueue or SetOptimistic, so the 'durable' SocketPro numbers ran at the oMemoryCached default. Call FlushQueue(key, cb, tagOptimistic::oDiskCommitted) when you need data committed to disk.
- Dequeue is batch-and-repeat: your DDequeue callback must re-issue Dequeue while messageCount > 0, and throughput depends on keeping 2-3 requests in flight. The consumer must deserialize payloads with the same types and order the producer used (CUQueue), because there is no schema.
- The plugin opens every queue with a hard-coded ttl of 120 hours (StartQueue(key, 120*3600)), and what expires is not documented. CloseQueue fails with QUEUE_DEQUEUING while messages are mid-dequeue, and the plugin drops all queue handles when its last client disconnects.

**Status:** Abandoned: the last commit is 2023-02-16 (v6.4), udaparts.com no longer resolves and old issues have no replies. With no license and a closed binary core, it is a reference design, not something you can legally vendor or patch.

[repo](https://github.com/udaparts/socketpro) · [benchmark](https://web.archive.org/web/20200210003353/http://www.udaparts.com/document/articles/fastsocketpro.htm)

##### Wisp  `Rust`  `no license`  `active`  `Tier C`

Experimental Rust server speaking the NATS Core client protocol; about 3.7-4.4x nats-server throughput on 1,000-subscriber loopback fan-out.

**Beats:** NATS — Setup: a single shared Ryzen 7 9700X Linux host over loopback, with server and nats.go client pinned to disjoint 4-core sets, 1 publisher and 1,000 subscriber connections receiving 100,000 x 128 B messages (100M deliveries). Median of 3 runs: Wisp 9.02M deliveries/s vs 2.07M for nats-server 2.14.6 (4.37x), using 87 vs 371 server CPU-seconds; the rustc version is not stated. That build predates the slow-consumer limits, headers, auth/TLS and metrics. Later sessions on the same host measured 4.39x, 3.89x and 3.70x (9.21 vs 2.49M/s at commit 26d0376). The latest committed build (8.45M/s fan-out) has not been rerun against NATS.

**Known shortcoming:** Numbers match (vs NATS 2.14.6, Ryzen 9700X, public harness) but rustc version unstated, 2 stars, no licence (reference only); Rust, not C++ (verifier downgrade from A).

**Known shortcoming:** The 4.37x was measured before limits/TLS/auth/metrics were added; later same-host runs gave 4.39x/3.89x/3.70x and the latest build's fan-out wasn't re-run vs NATS. 8 publishers to 1 subscriber: older builds dropped the subscriber at the cap in 6/10 runs; the batched build passes but uses ~1.35x NATS's CPU and 73 vs 21 MiB RSS. Roughly parity on 1:1 small messages; ~7.5% behind NATS past 100k subjects; any SUB/UNSUB clears the account plan cache. No clustering, JetStream, NKeys or JWT; Unix only; needs rustc 1.88+ (unstated); TLS/auth throughput unmeasured. One author, v0.1.0, 27 of 48 commits in one day.

**How:** For each subject it builds a dispatch plan (the matching subscriptions plus a pre-encoded `MSG subject sid` header prefix per subscriber) and caches it in a bounded, sharded FIFO cache with generation-number invalidation. A per-connection last-subject cache sits in front of that, so hot publishes skip the submap subject trie entirely. Payloads are refcounted `bytes::Bytes` slices of the 64 KiB socket read buffer, shared by every recipient (zero-copy fan-out), and are parsed with a memchr line scan and a fast-path PUB parser. Each connection has its own Tokio writer task, which swaps the pending queue out from under the mutex in O(1), encodes up to 64 KiB or 1,024 messages into one contiguous buffer and writes it, flushing as soon as the queue drains with no idle timer. Single-subscriber subjects also get producer-side batching: up to 1,024 deliveries are pre-encoded into one wire frame and admitted with one lock acquisition. The global allocator is jemalloc and the hash maps use ahash.

**Use it when:**
- Your clients already speak NATS Core and the load is high fan-out transient pub/sub: one publisher to hundreds or thousands of subscriber connections on a subject, with small (64-128 B) payloads, where nats-server CPU is the limit. At 1,000 subscribers it measured 3.7-4.4x the deliveries/s with roughly a quarter of the server CPU-seconds (87 vs 371) and lower peak RSS (61 vs 93 MiB).
- Many-subject publishing where the hot subject set fits the dispatch cache (100,000 plans per account by default). The 5,000-subject wildcard case measured about 5.1M deliveries/s vs 1.9-2.0M for NATS, using about a third of the CPU.
- A single-node, at-most-once Core broker on Linux/Unix where you can live without clustering, for example in-host or in-rack telemetry fan-out, or a local stand-in for nats-server in tests.
- Idle request/reply over loopback: p50 about 17 us vs 19-20 us for NATS. The gain is small but it has held in every session.
- As a reference design for a NATS-protocol server in Rust. The harness is reproducible, and the reports keep failed runs and regressions.

**Skip it when:**
- You need clustering, leafnodes or gateways, JetStream or any persistence/replay, KV or object store, NKeys/JWT operator mode, auth callouts, account imports/exports, or queue-name-specific and dynamic response permissions. None of these are implemented.
- Any production or redistribution use. There is no LICENSE file, so default copyright applies. It is also a single-author 0.1.0 project with 2 stars, no releases or tags, no issue history, and 27 of its 48 commits landed on one day (2026-09-08).
- Many publishers into one subscriber under sustained load. Earlier builds disconnected the subscriber at the pending-message cap in 6 of 10 runs of 100M messages. The current batched build completed 5 of 5, but still uses about 1.35x NATS server CPU (50 vs 37 CPU-s per 100M) and 73 vs 21 MiB peak RSS.
- One publisher to one subscriber with small messages: this is roughly parity (0.97x-1.07x across sessions). Larger-payload results have swung between sessions, from -34% and -49% at 1 KiB and 8 KiB in the first run to +2% to +12% later.
- Workloads with subscription churn or cold subjects. Any SUB or UNSUB invalidates every cached plan in that account. Past the 100,000-subject cache it ran about 7.5% behind NATS (1.76 vs 1.90M msg/s). TLS- or auth-enabled throughput has never been measured.

**Vs siblings:** Pick Wisp only if your clients already speak NATS Core and you need single-node, non-durable fan-out with far less broker CPU than nats-server. Zenoh is the closest sibling for transient pub/sub but has its own protocol and API. TCPSHM targets point-to-point RTT. Redpanda, FluxMQ and Woodpecker fit when you need a persistent, replayable log, which Wisp does not have.

**Gotchas:**
- Slow consumers: a recipient that exceeds 64 MiB or 524,288 pending messages, or misses the 10 s write deadline, loses its whole connection and its queued output. If the 1 GiB aggregate output budget runs out, the recipient that cannot reserve space is closed, which can be a healthy peer rather than the largest backlog. In the stall test a subscriber survived a 400 ms read pause but was dropped at 550 ms; NATS lasted until 400-700 ms.
- Any SUB or UNSUB bumps a per-account generation counter, and that invalidates every cached dispatch plan in the account. Subscription churn therefore turns unrelated hot subjects cold.
- Batched single-subscriber deliveries wait in the publisher connection until a flush point and count against no pending limit until admitted. Prometheus publication and delivery counters can lag by up to 1,023 publications per publisher. Fan-out and queue-group paths skip batching and still admit each message separately.
- The WISP_WRITEV_FLUSH_THRESHOLD_BYTES setting does not use writev: the writer copies each batch into one contiguous buffer. On SIGHUP, any change to the security or client-CA file, even formatting only, disconnects every client. The monitoring HTTP listener has no authentication or TLS.

**Status:** Actively developed as of 2026-09-08 but single-author and unlicensed. Treat it as reference-only: you can read and benchmark it, but there is no grant to reuse or redistribute the code.

[repo](https://github.com/iamd3vil/wisp) · [benchmark](https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/REPORT.md)

#### probabilistic-filters

##### Binary Fuse Filter demo (FastFilter/FilterPassword)  `C++`  `no license`  `stale`  `Tier C`

Demo CLI pair that builds an mmap-queried binary fuse filter over HaveIBeenPwned SHA1 prefixes, with a Bloom filter for comparison.

**Beats:** Bloom filter — The data comes from single CLI runs on an undisclosed machine and compiler (the Makefile builds with c++ -O3 -std=c++11) over the first 10M 64-bit prefixes of the HIBP v4 ordered-by-count SHA1 list. binaryfuse8 took 0.420 s of CPU time to construct vs 0.613 s for a classic unblocked k=8, 12-bit/key Bloom filter, and wrote 11.27 MB vs 15.00 MB, at a slightly higher false-positive rate (2^-8 ≈ 0.39% vs about 0.32% for the Bloom filter, measured by a user in issue #4). Only the build-time and size figures stand. The one-shot query timings include open and mmap, and the binary fuse query hit a since-fixed header-parsing bug and gave a wrong answer.

**Known shortcoming:** A demo program rather than a library; ratios are derived from README numbers; the CI badge machine differs from the benchmark machine.

**Known shortcoming:** The README query numbers are void: they predate a header-parse fix (2021-11, #6), and binaryfuse8 then gave a false negative for SHA1('123456'); README keys are 17 hex chars while the current query tool accepts exactly 16. Timing is clock() CPU time over open+mmap+one lookup. build_filter's realloc passes an element count as bytes, so input beyond 629,145,600 lines overflows the heap (current HIBP ~1B lines). No LICENSE; demo only (use xor_singleheader).

**How:** The default filter is an 8-bit binary fuse filter (Graf & Lemire, arXiv 2201.01174), taken from the pinned xor_singleheader submodule. Each key is mixed with a murmur64 finalizer and mapped to 3 byte slots in 3 adjacent segments. A lookup XORs those 3 bytes against the key's fingerprint, so it always costs exactly 3 memory reads. The table has about 1.125 slots per key (about 9 bits/key at 10M keys; the README's file is 11.27 MB). Construction peels a 3-uniform hypergraph, like xor filters, but first bucket-sorts the hashes by segment block so memory accesses stay local. The bloom12 baseline is fastfilter_cpp's classic unblocked Bloom filter: 12 bits/key, k=8 double-hashed probes into random 64-bit words, so a positive lookup can take up to 8 cache misses and the file is 15 MB.

**Use it when:**
- You want a small, readable end-to-end example of building a static membership filter offline and querying it through mmap without loading it into RAM.
- Offline or batch screening of password hashes against an HIBP-style list, where a ~0.4% false-positive rate (2^-8 for binaryfuse8) is acceptable and an exact lookup follows on a hit.
- Comparing the file size and build time of binaryfuse8, binaryfuse16, xor8 and bloom12 on your own 64-bit-keyed data with one tool (-f picks the filter type, -V checks for false negatives and estimates the false-positive rate).
- Sets of tens to a few hundred million keys on a Linux or macOS box with plenty of RAM for the one-time build.

**Skip it when:**
- Anything you ship or depend on: the maintainer calls it a demonstration and not a library (README, issue #9), and the repo has no LICENSE file. Build on xor_singleheader instead; the maintainer says it is Apache-licensed.
- Sets that change: the filter is build-once and immutable, with no insert or delete.
- Build machines with little RAM: construction needs up to ~64 bytes/key (README), the full list is said to need 64 GB, and build_filter reserves a fixed ~5 GB key buffer (600*1024*1024 uint64 slots) whatever -m is set to.
- Current full HIBP dumps (issue #9 puts them near 1 billion records): past 629,145,600 input lines, read_data grows the buffer with realloc(array, array_capacity), which passes an element count as a byte count, so the buffer shrinks and later writes overflow the heap. HIBP also no longer ships the ordered-by-count 7z file the README tells you to download (issue #9).
- Measuring or serving high query throughput: query_filter answers one key per process, and there is no batch or server mode (issue #1 has been open since 2019).
- Windows: the README expects Linux or macOS, and the code uses POSIX getline, getopt and mmap.

**Vs siblings:** Pick it only as a runnable, HIBP-shaped reference for the build-once, mmap-and-query pattern. For code you ship, use Xor Filter (xor_singleheader), which this repo wraps and which has built-in serialize/deserialize, or xorfilter (Go) or xorf (Rust) in those languages. Use Boost.Bloom if you need incremental inserts or a cache-blocked Bloom filter, which is a stronger baseline than the unblocked bloom12 used here.

**Gotchas:**
- The README benchmark block was written on 2021-06-03 (commit 202f2180), before commit c5eac973 (2021-11-01, issue #6) fixed query_filter so it reads SegmentLengthMask from the binary fuse file header. In that block, binaryfuse8 answers 'Surely not in the set' for 7C4A8D09CA3762AF, the SHA1 prefix of '123456', which the README's own full-list example reports as present. It also 'expects' 11,206,692 bytes for a file it wrote as 11,272,228 bytes. That query result is a false negative from the old bug, so the 241 us vs 344 us comparison is void.
- The example query keys in the README have 17 hex characters (7C4A8D09CA3762AF6). The current query_filter rejects any key that is not exactly 16 characters, so the README output cannot be reproduced as written.
- The timings use clock(), which is CPU time, not wall time. 'Processing time' and 'Expected number of queries per second' cover fopen, the header read, mmap and page-faulting a single lookup. They do not measure lookup cost; a bulk benchmark with the same filter family cited in issue #1 reports about 50 ns per query.
- Latent limits in the pinned xor_singleheader: key counts go through uint32_t parameters, so more than 4,294,967,295 keys would be silently truncated. Its duplicate-removal qsort comparator also casts a uint64_t difference to int, which is not a valid ordering if 64-bit prefixes ever collide. The same comparator is still on upstream master.

**Status:** Stale: the last commit is 2024-12-09 (a dependency tidy and a CMake file), the repo has 50 stars and no LICENSE, and the maintainer describes it as a demonstration, so read it for the pattern and build on xor_singleheader.

[repo](https://github.com/FastFilter/FilterPassword) · [benchmark](https://github.com/FastFilter/FilterPassword#performance-comparisons)

### toolchain-and-build

#### compile-caching-and-distribution

##### NativeLink  `Rust`  `FSL-1.1-Apache-2.0`  `active`  `Tier C`

REAPI remote build-cache and execution server for Bazel/Buck2/CMake; beats local-only, non-distributed builds.

**Beats:** local, non-distributed single-machine build (no remote cache / no distributed compilation) — Independent blog (Reid Kleckner, 2026-03-30): a full LLVM+Clang build via CMake/Ninja/recc took 1026s locally (laptop, PCH disabled, Ninja default -j) versus 257s distributed at -j96 through NativeLink on a home Kubernetes/Talos cluster (~4.0x); with PCH enabled the local build dropped to 683s, making the real distributed gain 2.65x, which the author calls the 4x headline an overstatement. No CPU models are given for the laptop or cluster nodes, and each configuration was run once (evidence tier C).

**How:** Content-addressed storage caches and reuses previously-built objects across machines and CI runs so unchanged actions are skipped entirely. A scheduler fans independent build actions from the action graph out to remote worker pods for parallel execution over the REAPI protocol (the same protocol Bazel, Buck2, and reclient use). In the verified benchmark this let a CMake/Ninja LLVM build run at -j96 across a home Kubernetes cluster instead of the client machine's default -j.

**Use it when:**
- Already building with Bazel, Buck2, Goma/Siso, or another REAPI client, where integration is closer to transparent
- CMake/Ninja C/C++ projects willing to add the recc compiler-launcher shim
- Large action graphs with many independent, cacheable steps (e.g. LLVM/Chromium-scale monorepos)
- Teams/CI where a cache and worker pool shared across many machines pays off more than single-machine speed
- You can operate a Docker/Kubernetes cluster to host the CAS, scheduler and workers

**Skip it when:**
- Solo local dev with no cluster to distribute to — the verified benchmark shows no win without remote workers
- Builds that depend on precompiled headers through recc: its input scanner doesn't recognize PCH files, so PCH had to be disabled, and re-enabling it locally cut the measured gain from ~4.0x to ~2.65x
- Teams that want a single dependency-free binary rather than standing up and operating a CAS/RE server
- Production use of the metrics/persistent-worker modules without a commercial license — those are Business Source Licensed separately from the FSL-1.1 core
- Windows Bazel builds: README claims Windows support but an open issue reports Bazel tests failing on Windows x64 (#485, unresolved since 2024)

**Vs siblings:** Pick NativeLink over FASTBuild/HOMCC/octobuild when you're already on, or willing to adopt, a Bazel Remote Execution API client (Bazel, Buck2, or CMake via recc) and want a shared cache plus a horizontally scalable Kubernetes-style execution cluster, rather than the single-protocol local caching (FASTBuild) or distcc-style compiler forwarding (HOMCC, octobuild) the siblings use.

**Gotchas:**
- recc's input scanner doesn't recognize precompiled headers as build inputs; disabling PCH was required, and doing so alone accounts for most of the gap between the claimed 4.0x and the author's corrected 2.65x
- Core is FSL-1.1 (source-available, permits only non-competing use, converts to Apache-2.0 two years after each release, not OSI-approved); the metrics and persistent-worker modules are separately Business Source Licensed, needing a commercial license for shared production use
- Open issue reports Bazel tests failing on a Windows x64 machine (#485, open since 2024)
- The only third-party speedup evidence is a single-author, single-run personal blog post; the vendor's own '4-15x' homepage claim has no published methodology

**Status:** Actively maintained (last commit 2026-09-24; 1.6k stars, 244 forks; vendor claims 10B+ build requests/month in production including Samsung); usability is 'reference' because it's infrastructure to deploy and operate, not a library to link.

[repo](https://github.com/TraceMachina/nativelink) · [benchmark](https://reidkleckner.dev/posts/llvm-recc-nativelink/)
