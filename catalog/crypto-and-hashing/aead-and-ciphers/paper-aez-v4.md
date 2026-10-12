# AEZ (v4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Unlicense` · 🔴 abandoned

> Krovetz's AES-NI code for AEZ v4, a nonce-misuse-resistant AEAD, uses \~2.7x fewer cycles than AES-256-GCM, but v4 is broken.

| | |
|---|---|
| **Beats** | AES-256-GCM |
| **Claimed result** | \~2.7x lower cycles/byte than aes256gcmv1 (0.26 vs 0.70 median, long+long encrypt); decrypt \~2.2x (0.26 vs 0.57); range across the page's 15 sections 1.9x (0+long) to 6.9x (64+64 forgery, noisy row) (derived from page data) |
| **Workload** | long+long encrypt, AES-NI implementation crypto_aead/aezv4/aesni, cycles/byte on a real CPU via the eBACS/SUPERCOP harness. 'long' is SUPERCOP's differential rate: 1/1920 of the cycle difference between a 2048-byte and a 128-byte message (here with the same length of associated data). |
| **Metric** | throughput |
| **Hardware** | amd64, Raptor Cove P-cores, 2024 Intel Core 5 210H, 4 x 2200MHz (eBACS machine "freshwrap,big") |
| **Compiler and flags** | aezv4/aesni fastest with clang -march=native -O -fwrapv -Qunused-arguments -fPIC -fPIE -gdwarf-4 -Wall (Debian Clang 19.1.7). The other clang/gcc -O2/-O3/-Os builds are within 1%. Baseline aes256gcmv1: fastest implementation dolbeau/aesenc-int, clang -march=native -O2 -fwrapv -Qunused-arguments -fPIC -fPIE -gdwarf-4 -Wall (Debian Clang 19.1.7); dolbeau/vaesenc-int is within 4%, and SUPERCOP's OpenSSL wrapper (opensslnew, gcc -O2) is 1.46x slower. |
| **Adoption** | 104 stars (floodyberry/supercop mirror); still included in current eBACS/SUPERCOP releases |
| **Last commit** | 2016-07-16 |
| **Links** | [repository](https://github.com/floodyberry/supercop) · [benchmark](https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html) |

## Verdict

The measurement is eBACS supercop-20260627 on 'freshwrap,big', an Intel Core 5 210H (Raptor Cove P-cores, 2.2 GHz). aezv4/aesni was built with clang 19.1.7 -march=native -O and aes256gcmv1 (fastest build: Dolbeau's AES-NI intrinsics) with clang -O2. Median long+long cost was 0.26 vs 0.70 cpb for encrypt (\~2.7x) and 0.26 vs 0.57 for decrypt (\~2.2x). Derived from the page data: message-only long+0 encrypt was 0.35 vs 1.07 cpb (\~3.1x), 1536+1536 encrypt 0.31 vs 0.82 (\~2.6x), and 64+64 encrypt 1.18 vs 4.70 (\~4x).

## Use it when

- Reproducing or analysing CAESAR-era eBACS/SUPERCOP AEAD results. It is a well-measured, readable (\~900-line) AES-NI implementation of a wide-block AEAD.
- As the starting point for studying or porting AEZ's AES4 + EME-style structure. For anything that encrypts real data, use the AEZ v5 code instead, which runs at essentially the same speed on the same page (0.28 vs 0.26 cpb long+long encrypt).
- The use cases AEZ targets (with v5): nonce reuse or nonce-less designs where you need misuse resistance at roughly AES-CTR cost, messages that fit in memory, and small packets, where AEZ is about 4x cheaper than AES-256-GCM at 64+64 bytes (1.18 vs 4.70 cpb).
- Decrypt paths that are flooded with forgeries: invalid ciphertexts are rejected at about half the cost of a valid decrypt (0.15 cpb long+long forgery).

## Skip it when

- Any real deployment. The v4 specification, which this code implements, has an offset-collision bug in its tweakable blockcipher: two different tweaks get the same offset. It was found by Bonnetain, Derbez, Duval, Jean, Leurent, Minaud and Suder (2017), who showed easy forgeries. The designers say this destroys authenticity (and probably privacy), and fixed it only in AEZ v5.
- Protocols that need a standard, interoperable AEAD (TLS, IETF, FIPS). AEZ never became a standard and was not in the CAESAR final portfolio.
- Streaming or online encryption, and messages of 4 GiB or more. As an MRAE scheme it needs two passes over the whole message, and this code converts lengths to 32-bit unsigned, so they silently truncate.
- Builds without AES-NI + SSE4.1 or ARMv8 Crypto Extensions, including MSVC, where __AES__ is not defined. The file hits #error, and the portable ref implementation took about 70x longer than aesni in eBACS's test-time column.
- High-volume keys or conservative security margins. Security holds only to the birthday bound, and key-recovery birthday attacks exist (Fuhr-Leurent-Suder 2015; Chaigneau-Gilbert 2016, which targets v4.1). The spec caps use at 2^48 bytes per key, and AEZ itself has no proof, because the AES4 substitution is heuristic.

## How it is fast

It follows the designers' 'prove-then-prune' approach. The provably secure AES-based tweakable blockcipher is swapped for AES4 (four aesenc rounds keyed directly by the 128-bit subkeys I, J and L, with no key expansion) in most calls, and full 10-round AES is kept only for a few blocks per message. AEZ-core is an EME/OTR-style encipher-mask-encipher over pairs of blocks: five AES4 calls per 32 bytes, i.e. about 10 AES rounds per 16-byte block and close to AES-CTR cost, against 14 rounds plus a GHASH multiply per block for AES-256-GCM. Per-block offsets come from XE-style doubling in GF(2^128), and pass one keeps 16 blocks (8 independent pairs) in flight per iteration to saturate the AES-NI pipeline. AD goes through an AES4-based universal hash (0.17 vs 0.32 cpb for GCM on 0+long). Forgeries are rejected after the first pass (0.15 vs 0.26 cpb on long+long).

## Compared with alternatives

Of the siblings measured on the same eBACS page, AEZ is the only one that is nonce-misuse-resistant, so it (as v5, not this v4 code) is the choice only when nonce reuse must be survivable. For pure speed, AEGIS-128L is faster (0.21 vs 0.26 cpb long+long encrypt; 0.97 vs 1.18 cpb at 64+64), and so is Tiaoxin-346 on encrypt (0.15 cpb).

## Integration

| | |
|---|---|
| **Form** | source-drop (a single crypto_aead/aezv4/aesni/encrypt.c plus api.h in SUPERCOP layout; outside SUPERCOP you must supply a crypto_aead.h shim) |
| **Dependencies** | none (a reference BLAKE2b is bundled and used only to derive subkeys from keys that are not 48 bytes) |
| **Minimum toolchain** | C99 on GCC or Clang with -maes -msse4.1 (or -march=native) so that __AES__ is defined. eBACS builds it with Clang 19.1.7 and GCC 14.2.0 at -O/-O2/-O3/-Os; MSVC is unsupported. |
| **Platforms** | x86-64 with AES-NI + SSSE3/SSE4.1; AArch64 with ARMv8 Crypto Extensions (__ARM_FEATURE_CRYPTO); anything else needs the slow portable ref implementation |
| **Thread safety** | Not documented. The SUPERCOP entry points build a fresh aez_ctx_t on the stack for every call and are reentrant, but the internal aez_hash writes ctx-&gt;delta3_cache, so a shared context must not be used from several threads at once. |
| **Drop-in for the baseline** | no |

## Gotchas

- Out-of-bounds reads. Encryption loads the 16 bytes after the end of the message and masks them off. The 12-byte nonce and the partial last AD block are fetched with full 16-byte loads. GCC 14 on eBACS warns about a read at offsets 33-48 of the 48-byte pad[] table. Pad your buffers, or expect ASan reports and possible faults at page boundaries.
- The SUPERCOP wrapper hard-codes a 48-byte raw key (I||J||L, with no key schedule), a 12-byte nonce and a 16-byte tag. aez_hash handles only nonces and abytes up to 16 and a single AD string, although the spec allows vector AD and arbitrary lengths.
- eBACS marks it 'T:' (constant time not declared as a goal; the build symbol is crypto_aead_aezv4_aesni_timingleaks_\*), while the aes256gcmv1 baseline has no such mark.
- Its ciphertexts do not match AEZ v5 or any other version: v5 changed the offset definition, so data encrypted with this code cannot be decrypted by v5 code.

## Known shortcomings

- CAESAR candidate that did not reach the final portfolio; code lives only in SUPERCOP/eBACS. Decrypt gain is \~2.2x. The eBACS baseline's fastest AES-GCM is Dolbeau's AES-NI code (OpenSSL's wrapper is 1.46x slower), so ratios against OpenSSL look larger. 'Long' is the 2048-vs-128-byte differential.
- AEZ v4 is broken: Bonnetain et al. (2017) found offset collisions giving easy forgeries; only v5 fixes it (same speed, \~0.28 cycles/byte). The SUPERCOP code reads out of bounds (message +16 bytes, 16-byte nonce load, AD tail) and truncates lengths to 32 bits; eBACS flags it for timing leaks. Needs AES-NI + SSE4.1 (#error on MSVC); two-pass; birthday-bound key recovery; not standardized. AEGIS-128L is faster. Useful only as a benchmark reference.

## Caveats and trade-offs

Public-domain dedication in the Unlicense wording (Ted Krovetz, 'free and unencumbered software'), so no patent grant. The baseline is SUPERCOP's fastest AES-256-GCM (Romain Dolbeau's AES-NI intrinsics), which beats SUPERCOP's OpenSSL wrapper, so the comparison is against a strong AES-GCM. The mirror is a stale 2016 snapshot, and the numbers come from the live bench.cr.yp.to page (supercop-20260627 dataset). eBACS results tables do not label which implementation or compiler produced each row. The aesni/compiler attribution comes from the web-impl pages. AEZ v4 was superseded by v5 (CAESAR round 3), which has about the same speed on this page (0.28).

Non-standard, misuse-resistant (nonce-reuse-resistant) AEAD with variable-length tags/nonces, wide-block-cipher design (AEZ) rather than a stream+MAC AEAD; not adopted in any mainstream TLS/library stack; the design underwent several security revisions (v1-v5) after cryptanalytic findings, and this repo only mirrors v3/v4 (not the latest v5).

## Maintenance

The mirror is an abandoned 2016 snapshot of Krovetz's public-domain (Unlicense, and the spec says 'no AEZ-related patents have been or will be requested') code that current SUPERCOP still builds, so it is easy to copy, but it implements a spec the designers withdrew in March 2017, so treat it as a benchmark artifact and use AEZ v5 instead.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B-&gt;A. The independent eBACS/SUPERCOP harness is public (supercop-20260627 crypto_aead/measure.c, running crypto_aead/aezv4/aesni, which is in the linked mirror) and measures aes256gcmv1 on the same machine. The web-impl pages give the compiler and flags for every implementation (aezv4/aesni: clang 19.1.7 -march=native -O ...), and the results page gives the CPU (Intel Core 5 210H, Raptor Cove).
- **Verifier notes:** The numbers match the aezv4 and aes256gcmv1 rows of the long+long encrypt table exactly (0.26/0.26/0.27 and 0.69/0.70/0.71). The record's claim that no compiler was stated was wrong: the linked web-impl pages list per-implementation compilers and flags. Metadata checks out: 104 stars, no repo license, not a fork, last commit 2016-07-16, and the aesni/encrypt.c header is Unlicense text.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** eBACS: AEZ v4 0.26 vs AES-256-GCM 0.70 cycles/byte (aesni, clang 19.1.7 -O).
- **Pages the verifier opened:**
  - <https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-aezv4.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-aes256gcmv1.html>
  - <https://github.com/floodyberry/supercop>
  - <https://raw.githubusercontent.com/floodyberry/supercop/master/crypto_aead/aezv4/aesni/encrypt.c>
  - <https://bench.cr.yp.to/supercop.html>
- **Sources the enricher read:**
  - <https://github.com/floodyberry/supercop>
  - <https://github.com/floodyberry/supercop/blob/master/crypto_aead/aezv4/aesni/encrypt.c>
  - <https://github.com/floodyberry/supercop/blob/master/crypto_aead/aezv4/aesni/api.h>
  - <https://github.com/floodyberry/supercop/blob/master/crypto_aead/aezv4/ref/api.h>
  - <https://github.com/floodyberry/supercop/blob/master/crypto_aead/aezv4/ref/encrypt.c>
  - <https://github.com/floodyberry/supercop/blob/master/crypto_aead/aezv4/designers>
  - <https://bench.cr.yp.to/results-aead/amd64-freshwrap,big.html>
  - <https://bench.cr.yp.to/web-impl/amd64-freshwrap,big-crypto_aead-aezv4.html>
  - <https://web.cs.ucdavis.edu/~rogaway/aez/>
  - <https://web.cs.ucdavis.edu/~rogaway/aez/bug.pdf>
  - <https://web.cs.ucdavis.edu/~rogaway/aez/AEZv4.1.pdf>
  - <https://web.cs.ucdavis.edu/~rogaway/aez/AEZv4.2.pdf>
  - <https://web.cs.ucdavis.edu/~rogaway/aez/aez.pdf>
  - <https://competitions.cr.yp.to/caesar-submissions.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:aez-v4`) · [data/wave7/enrich/raw/paper_aez_v4.json](../../../data/wave7/enrich/raw/paper_aez_v4.json) (enrichment confidence 0.72)

</details>
