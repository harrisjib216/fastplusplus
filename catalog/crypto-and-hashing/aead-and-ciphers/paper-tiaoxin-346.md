# Tiaoxin-346

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-2.0-or-later` · 🔴 abandoned

> Tiaoxin-346, an AES-round AEAD with 3 AES rounds per 16 bytes in AES-NI C; 1.8-5.6x faster than SUPERCOP's AES-256-GCM, unmaintained.

| | |
|---|---|
| **Beats** | AES-256-GCM |
| **Claimed result** | \~4.7x lower cycles/byte than aes256gcmv1 (0.15 vs 0.70 median, long+long encrypt), but only \~2.0x on long+long decrypt/forgery (0.28 vs 0.57); range across the page's 15 sections 1.8x (long+0 decrypt) to 5.6x (long+0 encrypt, noisy row) (derived from page data) |
| **Workload** | long+long encrypt, AES-NI-optimized C implementation crypto_aead/tiaoxinv2/nim, cycles/byte on a real CPU via the eBACS/SUPERCOP harness. 'long' is SUPERCOP's differential rate: 1/1920 of the cycle difference between a 2048-byte and a 128-byte message (here with the same length of associated data). |
| **Metric** | throughput |
| **Hardware** | amd64, Raptor Cove P-cores, 2024 Intel Core 5 210H, 4 x 2200MHz (eBACS machine "freshwrap,big") |
| **Compiler and flags** | tiaoxinv2/nim fastest with gcc -march=native -mtune=native -O2 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall (gcc 14.2.0). Clang builds are 4-10% slower, and one clang configuration fails to compile (missing ssse3/aes target features). Baseline aes256gcmv1: fastest implementation dolbeau/aesenc-int, clang -march=native -O2 -fwrapv -Qunused-arguments -fPIC -fPIE -gdwarf-4 -Wall (Debian Clang 19.1.7); dolbeau/vaesenc-int is within 4%, and SUPERCOP's OpenSSL wrapper (opensslnew, gcc -O2) is 1.46x slower. |
| **Adoption** | 104 stars (floodyberry/supercop mirror); algorithm still included in current eBACS/SUPERCOP releases (page shows dataset supercop-20260627) |
| **Last commit** | 2016-07-16 |
| **Links** | [repository](https://github.com/floodyberry/supercop) · [benchmark](https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html) |

## Verdict

eBACS (supercop-20260627, page dated 2026-09-25) measured tiaoxinv2/nim, built with gcc 14.2.0 -march=native -O2, against SUPERCOP's fastest AES-256-GCM (Dolbeau's AES-NI intrinsics, Debian clang 19.1.7 -O2) on one Raptor Cove P-core of an Intel Core 5 210H. Median cycles/byte were 0.15 vs 0.70 on long+long encrypt (4.7x) and 0.28 vs 0.57 on decrypt/forgery (2.0x). Across all 15 sections the gain ranges from 1.8x (long+0 decrypt, 0.44 vs 0.81) to 5.6x (long+0 encrypt, 0.19 vs 1.07, a row flagged noisy).

## Use it when

- Encrypt-heavy bulk AEAD on AES-NI x86 in a closed system where you control both ends: long+long encrypt 0.15 vs 0.70 cycles/byte (4.7x) and 1536+1536 encrypt 0.20 vs 0.82 (4.1x) against SUPERCOP's fastest AES-256-GCM.
- Authenticating large AD with little or no message: 0+long is 0.11-0.12 against 0.32-0.33 cycles/byte (about 2.7-2.9x), though eBACS flags these rows as noisy.
- Short messages despite the setup cost: initialization plus finalization is worth about 1120 bytes of message (per the spec), yet 64+64 still measures 1.25-1.33 against 4.70-5.13 cycles/byte (about 3.8x).
- As a research baseline for AES-round AEADs (AEGIS, Rocca, HiAE) or for cryptanalysis: weak-key distinguishers on 8-round Tiaoxin (ToSC 2021(2), ePrint 2021/187) and quantum hidden-shift state recovery (ToSC 2024, ePrint 2023/1306) both target it.

## Skip it when

- Anything that needs a standardized or vetted AEAD. Tiaoxin was CAESAR round 3 only, has no library adoption, and a GitHub repository search finds only two 0-star repositories named tiaoxin. The only optimized code is GPL-2.0-or-later.
- Anywhere a nonce could repeat. The update and initialization are invertible, so recovering the state recovers the master key. Vaudenay and Vizar (ePrint 2017/1147) recover the key with 30 nonce-reusing queries, and Kales, Eichlseder and Mendel (ePrint 2017/1137) give an implemented nonce-misuse key recovery. For AES-GCM, reuse enables forgery and CPA decryption rather than key recovery.
- Decrypt-dominated traffic sized from the headline: decrypt and forgery are only 1.8-2.2x AES-256-GCM (long+long 0.28 vs 0.57, long+0 0.44 vs 0.81).
- When AEGIS is available. On the same page AEGIS-128X2 (0.11 cycles/byte long+long) beats Tiaoxin in every section, and AEGIS-128L decrypts faster (0.21 vs 0.28 long+long, 0.23 vs 0.44 long+0).
- CPUs without AES-NI. The only fallback is the table-lookup ref variant (sboxes.h), about 13.6x slower in SUPERCOP's timing column (21560 vs 1589 cycles) and exposed to classic T-table cache-timing leaks.

## How it is fast

The state is three shift registers of 3, 4 and 6 128-bit words (T3, T4, T6). Each 32-byte block feeds M0 into T3, M1 into T4 and M0^M1 into T6, costing 6 aesenc calls with no data dependencies between them. They pipeline through the AES-NI unit and hide its 7-8 cycle latency, which the spec cites as the reason for the wider state. Ciphertext comes from a cheap output function (6 XOR, 2 AND per 32 bytes), the code unrolls 128 bytes per loop iteration, and AD is absorbed with the same update but no output function. Decryption is slower because M1's recovery depends on the freshly recovered M0 before the state can absorb them (DECRYPTION_ROUND), which lengthens the critical path.

## Compared with alternatives

Choose it over libaegis only for the peak single-stream encrypt rate on a pre-VAES AES-NI core, where it beats AEGIS-128L (0.15 vs 0.21 cycles/byte long+long). AEGIS-128L wins on decrypt, AEGIS-128X2 wins everywhere on this Raptor Cove host, and libaegis is maintained and MIT-licensed. Against the MORUS-1280 and AEZ entries from the same mirror, Tiaoxin is 4.4x and 1.7x faster on long+long encrypt, and unlike MORUS it has no published break of the full cipher in the nonce-respecting setting.

## Integration

| | |
|---|---|
| **Form** | source-drop (tiaoxin-optimized.c/.h, encrypt.c and api.h; you supply crypto_aead.h or call tiaoxin_optimized_encrypt/decrypt directly) |
| **Dependencies** | none beyond libc (string.h, stdlib.h) and the SSE2/SSSE3/AES-NI intrinsic headers |
| **Minimum toolchain** | GCC or clang with -maes -mssse3, or -march=native on an AES-NI CPU. eBACS's fastest build is gcc 14.2.0 -march=native -mtune=native -O2; Debian clang 19.1.7 builds are 4-10% slower, and clang -mcpu=native fails to compile (always_inline _mm_shuffle_epi8/_mm_aesenc_si128 without ssse3/aes). The designer used gcc 4.8.1 -O3 -msse2 -maes -mavx -march=native. |
| **Platforms** | x86-64 with AES-NI and SSSE3 (nim variant; only amd64 results were checked). The ref variant is portable C with table-based AES. |
| **Thread safety** | Not documented. In the nim code all state and constants are locals, with no mutable globals, so separate calls are reentrant. |
| **Drop-in for the baseline** | no |

## Gotchas

- Decrypt does 'clen -= 16; if (clen &lt; 0) return -1;' on an unsigned long long, so the check never fires. A ciphertext shorter than 16 bytes wraps clen to about 2^64 and the loop reads c and writes m out of bounds. Check clen &gt;= 16 before calling; the table-based ref variant has the same code.
- The load macro is _mm_load_si128, an aligned load, applied directly to the caller's key, nonce, AD, message and ciphertext pointers. Unaligned buffers are undefined behavior and can fault, so switch it to _mm_loadu_si128 when vendoring.
- The tag is checked with memcmp, which is not constant-time. Plaintext is written to m before verification and not wiped on failure, although the spec's security goals assume only 'false' is returned.
- The key is 128 bits (CRYPTO_KEYBYTES 16), so the AES-256-GCM baseline is not like-for-like. Against aes128gcmv1 on the same page the gain is 4.2x encrypt (0.15 vs 0.63) and 1.8x decrypt (0.28 vs 0.50). The exported tiaoxin_optimized_encrypt/decrypt symbols are unprefixed (flagged by eBACS as namespace violations) and collide with tiaoxinv1's identical names.

## Known shortcomings

- CAESAR third-round candidate not in the final portfolio; code only in SUPERCOP. Decrypt gain is only \~2.0x (encrypt 0.15 vs 0.70 cycles/byte). GPL-2.0+.
- CAESAR round 3 (v2.1), not a finalist; 128-bit key, so against AES-128-GCM it is 4.2x encrypt / 1.8x decrypt. Decrypt bug (also in the reference): `clen -= 16; if (clen < 0)` on an unsigned length never fires, so inputs under 16 bytes read/write out of bounds; aligned loads on caller buffers; memcmp tag check; plaintext released before verification. Nonce reuse gives master-key recovery in 30 queries (ePrint 2017/1147). AEGIS-128X2 is faster in every section.

## Caveats and trade-offs

GPL-2.0-or-later (Ivica Nikolic, header in tiaoxin-optimized.c; the thin encrypt.c/.h wrappers carry no header), which is copyleft. The headline 4.7x is the best-case encrypt direction, and decrypt/forgery is about 2x because SUPERCOP's AES-256-GCM decrypts faster than it encrypts on this machine. The baseline is SUPERCOP's fastest AES-256-GCM (Dolbeau AES-NI intrinsics), which beats its OpenSSL wrapper. The mirror is a stale 2016 snapshot, and the numbers come from the live bench.cr.yp.to page (supercop-20260627). Results tables do not label which implementation or compiler produced each row. The nim/gcc -O2 attribution comes from the web-impl pages. Tiaoxin-346 was a CAESAR round-2 candidate and did not reach round 3.

Not NIST/IETF standardized, no TLS/library adoption; requires AES-NI; smaller 128-bit security margin scrutiny than AES-GCM; CAESAR-competition cipher (finalist, high-performance use case) rather than a production-hardened library.

## Maintenance

Abandoned. The mirror is frozen at supercop-20160716 (its open issue #4 says to fetch SUPERCOP from bench.cr.yp.to instead), but the GPL-2.0-or-later nim file is about 16 KB and easy to vendor if copyleft and the bugs above are acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B-&gt;A. The independent eBACS/SUPERCOP harness is public (supercop-20260627 crypto_aead/measure.c, running crypto_aead/tiaoxinv2/nim, which is in the linked mirror) and measures aes256gcmv1 on the same machine. The web-impl pages give the compiler and flags (tiaoxinv2/nim: gcc 14.2.0 -march=native -mtune=native -O2), and the results page gives the CPU (Intel Core 5 210H, Raptor Cove).
- **Verifier notes:** The numbers match the tiaoxinv2 (0.15/0.15/0.16) and aes256gcmv1 (0.69/0.70/0.71) rows of the long+long encrypt table exactly. I added the decrypt figure because it halves the headline. Metadata is correct: GPL-2.0+ header, 104 stars, last commit 2016-07-16. The record's claim that the compiler was unstated was wrong.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** eBACS: Tiaoxin-346 0.15 vs AES-256-GCM 0.70 cycles/byte (nim, GCC 14.2 -O2).
- **Pages the verifier opened:**
  - <https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-tiaoxinv2.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-aes256gcmv1.html>
  - <https://github.com/floodyberry/supercop>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/tiaoxin-optimized.c>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/encrypt.c>
  - <https://bench.cr.yp.to/supercop.html>
- **Sources the enricher read:**
  - <https://github.com/floodyberry/supercop>
  - <https://github.com/floodyberry/supercop/issues/4>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/tiaoxin-optimized.c>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/tiaoxin-optimized.h>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/encrypt.c>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/nim/api.h>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/designers>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/tiaoxinv2/ref/tiaoxin-tablebased.c>
  - <https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-tiaoxinv2.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-aes256gcmv1.html>
  - <https://competitions.cr.yp.to/caesar-submissions.html>
  - <https://competitions.cr.yp.to/round2/tiaoxinv2.pdf>
  - <https://competitions.cr.yp.to/round3/tiaoxinv21.pdf>
  - <https://eprint.iacr.org/2017/1147>
  - <https://eprint.iacr.org/2017/1147.pdf>
  - <https://eprint.iacr.org/2017/1137>
  - <https://eprint.iacr.org/2017/1137.pdf>
  - <https://eprint.iacr.org/2021/187>
  - <https://eprint.iacr.org/2023/1306>
  - <https://eprint.iacr.org/search?q=tiaoxin>
  - <https://github.com/search?q=tiaoxin&type=repositories>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:tiaoxin-346`) · [data/wave7/enrich/raw/paper_tiaoxin_346.json](../../../data/wave7/enrich/raw/paper_tiaoxin_346.json) (enrichment confidence 0.85)

</details>
