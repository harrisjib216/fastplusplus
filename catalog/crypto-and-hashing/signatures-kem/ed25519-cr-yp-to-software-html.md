# Ed25519 (original amd64-64-24k SUPERCOP/eBATS submission)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Public Domain` · 🔴 abandoned

> The original 2011 public-domain Ed25519 amd64 assembly in SUPERCOP. On Westmere it signs about 20x and verifies about 7.6x faster than OpenSSL-based P-256 ECDSA.

| | |
|---|---|
| **Beats** | OpenSSL ECDSA (NIST P-256), benchmarked as SUPERCOP/eBATS entry 'ecdonaldp256' (an OpenSSL-based ECDSA wrapper) |
| **Claimed result** | Signing: 87548 cycles vs ecdonaldp256 (OpenSSL-based ECDSA P-256) at 1790936 cycles, \~20.5x faster (derived from page data). Single-signature verification: 273364 vs 2087500 cycles, \~7.6x faster (derived from page data). Batch verification of 64 signatures takes 8.55 million cycles (under 134000 cycles/signature), \~15.6x faster than ecdonaldp256 verification (derived from page data). All figures are on hydra2 (Xeon E5620, Westmere). |
| **Workload** | Single-signature signing and verification (and batch verification of 64 signatures) on an Intel Xeon E5620 Westmere core (machine 'hydra2'), measured in CPU cycles via the eBATS benchmarking framework |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5620 (Westmere, 2.4 GHz), eBATS machine 'hydra2', Turbo Boost disabled |
| **Adoption** | Foundational EdDSA implementation; later adopted (with modifications) by libsodium, OpenSSH, OpenSSL 1.1+, GnuPG, Signal, and most modern TLS stacks |
| **Links** | [repository](https://ed25519.cr.yp.to/software.html) · [benchmark](https://ed25519.cr.yp.to/ed25519-20110926.pdf) |

## Verdict

The paper (CHES 2011 / JCEN 2012) cites official eBATS reports on hydra2, a 2.4 GHz Intel Xeon E5620 (Westmere): 87548 cycles to sign and 273364 cycles to verify a short message. Against eBATS ecdonaldp256 (P-256 ECDSA; current eBATS shows it is an OpenSSL EC_KEY wrapper) at 1790936 and 2087500 cycles on the same machine, that is about 20.5x and 7.6x; the compiler is not stated. Current eBATS on 'alder' (Core i3-12100, SUPERCOP 20260831) shows the gap has narrowed. The fastest listed ed25519 is at a median of 27171 cycles to sign and 102613 to open, against 90965 and 248160 for ecdonaldp256 (about 3.3x and 2.4x).

## Use it when

- You want the canonical, public-domain Ed25519 code to study, benchmark against, or vendor into C on x86-64, and you control the SUPERCOP/NaCl-style glue (sha512, verify_32, randombytes)
- Server-side verification of many signatures from many keys: the amd64 open_batch path handles up to 64 at a time. The paper measured under 134000 cycles per signature versus 273364 for single verification on Westmere
- Designing a new protocol that is free to pick its signature scheme and wants small keys and signatures (32/64 bytes) and deterministic signing that needs no RNG
- Side-channel-conscious signing on general-purpose CPUs: the authors state there are no secret-dependent branches or array indices, and SUPERCOP's goal files record a TIMECOP pass for amd64-51-30k (titan0, 2020)

## Skip it when

- Environments that must interoperate with ECDSA P-256 (X.509 PKI, FIPS-only policies, existing P-256 keys): Ed25519 is a different curve, key format and signature semantics, so there is no drop-in path
- Non-x86-64 targets: both assembly variants are amd64-only (the 'architectures' file says amd64), and the software page calls the portable 'ref' 'slow'
- Systems that need strict, consensus-grade validity rules. open.c rejects S only when its top 3 bits are set, so S values in [ℓ, 2^253) pass the check. Single verification is cofactorless (encoding of SB−hA must equal R), while the batch equation only guarantees 8SB = 8R + 8hA, so the two paths can disagree on crafted signatures
- Production deployments that want a maintained library: this 2011 code is frozen, and SUPERCOP itself now carries lib25519-amd64, lib25519-ref10 and s2n implementations of the same primitive
- Very long or streamed messages: the API takes the whole message in memory, copies it into the signed-message buffer, and for long messages the time is dominated by SHA-512

## How it is fast

Field elements mod 2^255-19 use five radix-2^51 limbs. This avoids the slow add-with-carry chains that radix 2^64 hits on Nehalem/Westmere, and reduction is folded into the 25-mul schoolbook product through multiplies by 19. amd64-64-24k keeps radix 2^64 for CPUs such as K10/Core 2. Signing computes rB as a signed radix-16 fixed-base sum (Pippenger-style) over a 30KB precomputed table. Constant-time lookups load every candidate entry and combine them arithmetically, at a bit under 1000 cycles per step plus about 21000 for the final inversion. Verification merges the inversion into the square root when decompressing points, runs a double-scalar multiplication with a=-1 Edwards formulas, and compares encodings so R is never decompressed. Batch verification checks a random linear combination (128-bit z_i) with the Bos–Coster multi-scalar method over a heap using Floyd's bottom-up root replacement.

## Compared with alternatives

Pick this over ENG25519 when you need plain x86-64 Ed25519 without AVX-512IFMA hardware, or when public-domain provenance matters more than peak throughput. libsecp256k1 and UltrafastSecp256k1 fit only when you need secp256k1 interop, and FourQlib only when a non-standard curve is acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | SUPERCOP/NaCl-provided crypto_hash_sha512, crypto_verify_32, randombytes and the crypto_sign.h namespace macros |
| **Minimum toolchain** | C compiler plus an assembler for the qhasm-generated AT&T-syntax .S files (gcc or clang). The paper states no compiler; SUPERCOP's goal files show gcc -march=native -O3 builds |
| **Platforms** | x86-64 only for amd64-51-30k and amd64-64-24k; the portable C ref/ref10 run anywhere but slowly |
| **Thread safety** | Not documented. The C entry points read (keypair, sign, open, open_batch) keep their state on the stack, and keypair and open_batch call randombytes, so thread safety depends on that function |
| **Drop-in for the baseline** | no |

## Gotchas

- The 64-byte secret key is the 32-byte seed followed by the 32-byte public key. crypto_sign copies A from sk+32 instead of recomputing it, so never assemble sk from a separately stored or untrusted public key
- crypto_sign_open needs an output buffer m of at least smlen bytes because it uses it as scratch. On failure it sets \*mlen to (unsigned long long)-1 and zeroes m
- open_batch calls randombytes and caps batches at 64. It verifies fewer than 3 signatures one by one and, on any failure, falls back to individual verification. The paper's batch figures were the authors' own and were 'not yet benchmarked by' eBATS
- The Westmere numbers come from the radix-2^51 amd64-51-30k code; the paper says radix 2^64 (amd64-64-24k) bottlenecks on Nehalem/Westmere. SUPERCOP selects the fastest implementation per machine, so which one you get varies by CPU

## Known shortcomings

- Ratios against 'OpenSSL' are derived: the paper compares eBATS implementations, and the Westmere figures likely come from amd64-51-30k rather than amd64-64-24k. The original 2011 code is superseded by later Ed25519 implementations (e.g. in libsodium, BoringSSL) and is no longer developed.
- Frozen 2011 source drop inside SUPERCOP; needs SUPERCOP glue (sha512, verify_32, randombytes); amd64 only. open.c checks only the top 3 bits of S, so S in [l, 2^253) is accepted; single verification is cofactorless while batch verification is cofactored, so they can disagree. Batch numbers are the authors' own. The gap to P-256 has narrowed: on eBATS alder the fastest Ed25519 is \~3.3x sign / \~2.4x verify over ecdonaldp256 (vs 20.5x / 7.6x on Westmere).

## Caveats and trade-offs

The paper does not say ecdonaldp256 uses OpenSSL; it only says 'ECDSA signatures using the NIST P-256 elliptic curve'. The OpenSSL basis is confirmed by current eBATS, which lists ecdonaldp256 implementations 'openssl' and 'opensslnew' (code calls EC_KEY_new). The paper does not state compiler or flags. The hydra2 figures come from the radix-2^51 / 30KB-table code that the paper targets at Westmere (i.e. amd64-51-30k, inferred from Sections 3-4), not the radix-2^64 amd64-64-24k variant, which the paper says bottlenecks on Nehalem/Westmere. The numbers are 2011-era; the implementations still ship in SUPERCOP and are still benchmarked on eBATS alongside the newer lib25519 code. The software is a public-domain dedication with no patent grant; the authors say they have not been notified of any patent claims.

Ed25519 uses a fixed, non-NIST curve and deterministic nonces, which differ from ECDSA's API/semantics and key format; this original submission is unpadded raw assembly (amd64-64-24k), not a general-purpose library API.

## Maintenance

Frozen 2011 research code (software page last revised 2017-01-22) that is still shipped and benchmarked in SUPERCOP 20260831. The promised NaCl integration never shipped: NaCl's latest release, 20110221, still ships a prototype crypto_sign and points to SUPERCOP. It is public domain and easy to copy for study, but a maintained descendant is the better production choice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed paper (CHES 2011, and J. Cryptographic Engineering 2012, DOI 10.1007/s13389-012-0027-1) reports eBATS cycle counts on hydra2 (Xeon E5620, Turbo Boost off). It compares them with eBATS ecdonaldp256 (ECDSA P-256) on the same machine. The paper states no compiler or flags, and the 2011 hydra2 eBATS pages were not opened, so the tier is B, not A.
- **Verifier notes:** All numbers check out in the paper intro; the only fixes are marking the ratios as derived and correcting the claim that the paper calls ecdonaldp256 OpenSSL. The record name's 'amd64-64-24k' label is likely wrong for the Westmere figures, which point to amd64-51-30k. maintenance_status changed from 'finished' to 'abandoned' because the authors give no completion statement and the software page was last revised 2017-01-22; the code is still distributed in SUPERCOP 20260831.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** eBATS (alder): fastest Ed25519 \~3.3x sign, \~2.4x verify vs ecdonaldp256.
- **Pages the verifier opened:**
  - <https://ed25519.cr.yp.to/software.html>
  - <https://ed25519.cr.yp.to/ed25519-20110926.pdf>
  - <https://bench.cr.yp.to/impl-sign/ecdonaldp256.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_sign-ecdonaldp256.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_sign-ed25519.html>
  - <https://api.crossref.org/works?query.bibliographic=High-speed+high-security+signatures+Bernstein+Duif+Lange+Schwabe+Yang>
- **Sources the enricher read:**
  - <https://ed25519.cr.yp.to/software.html>
  - <https://ed25519.cr.yp.to/>
  - <https://ed25519.cr.yp.to/ed25519-20110926.pdf>
  - <https://bench.cr.yp.to/impl-sign/ed25519.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_sign-ed25519.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_sign-ecdonaldp256.html>
  - <https://bench.cr.yp.to/results-sign/amd64-alder.html>
  - <https://github.com/jedisct1/supercop/tree/master/crypto_sign/ed25519>
  - <https://github.com/jedisct1/supercop/tree/master/crypto_sign/ed25519/amd64-51-30k>
  - <https://github.com/jedisct1/supercop/tree/master/crypto_sign/ed25519/amd64-64-24k>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/api.h>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/keypair.c>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/sign.c>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/open.c>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/batch.c>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/goal-constbranch>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/goal-constindex>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/architectures>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_sign/ed25519/amd64-51-30k/implementors>
  - <https://nacl.cr.yp.to/install.html>
  - <https://nacl.cr.yp.to/sign.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://ed25519.cr.yp.to/software.html`) · [data/wave7/enrich/raw/ed25519_cr_yp_to_software_html.json](../../../data/wave7/enrich/raw/ed25519_cr_yp_to_software_html.json) (enrichment confidence 0.8)

</details>
