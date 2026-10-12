# AEAD and ciphers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md)</sub>

**What these beat:** OpenSSL AES-GCM, ChaCha20-Poly1305, libsodium  
**23 entries:** 8 tier A · 4 tier B · 8 tier C · 3 tier D · 19 copyable, 4 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**HiAE (libhiae)**](hiae-aead-libhiae.md) | Portable C library for the HiAE AES-round AEAD; about 3.8x OpenSSL AES-128-GCM encryption throughput on Apple M5 Max. | **A** | C | MIT | 🟢 active |
| 2 | [**camellia-simd-aesni**](jkivilin-camellia-simd-aesni.md) | Byte-sliced Camellia kernels computing S-boxes with AES-NI/VAES/GFNI; 3-19x faster than NTT's table-based reference C. | **A** | C | MIT | 🟢 active |
| 3 | [**chacha20poly1305-simd**](lxl66566-chacha20poly1305-simd.md) | Pure-Rust (X)ChaCha20-Poly1305 with hand-written AVX-512/AVX2/SSE2/NEON kernels; beats RustCrypto everywhere, OpenSSL mainly on small messages. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 4 | [**hardware-rust-crypto**](godaddy-hardware-rust-crypto.md) | Hardware-only AES-256-GCM/GCM-SIV crate for Rust with compact, zeroized key state; faster than ring and RustCrypto on Apple M4. | **A** | Rust | Apache-2.0 | 🟢 active |
| 5 | [**LeMac**](augustinbariant-implementations-lemac-petitmac.md) | Designers' AES-NI C code for LeMac, a nonce-based AES-round MAC about 4-7x faster than AES-128-GCM's GHASH on long messages. | **A** | C | CC0-1.0 (reference… | 🟡 stale |
| 6 | [**ROCCA-S**](yt-nakano-rocca-s.md) | KDDI's reference C code for Rocca-S, a 256-bit-key AES-round AEAD; \~1.9-2.9x OpenSSL AES-128-GCM encryption throughput. | **A** | C | MIT | 🟡 stale |
| 7 | [**AEZ (v4)**](paper-aez-v4.md) | Krovetz's AES-NI code for AEZ v4, a nonce-misuse-resistant AEAD, uses \~2.7x fewer cycles than AES-256-GCM, but v4 is broken. | **A** | C | Unlicense | 🔴 abandoned |
| 8 | [**Tiaoxin-346**](paper-tiaoxin-346.md) | Tiaoxin-346, an AES-round AEAD with 3 AES rounds per 16 bytes in AES-NI C; 1.8-5.6x faster than SUPERCOP's AES-256-GCM, unmaintained. | **A** | C | GPL-2.0-or-later | 🔴 abandoned |
| 9 | [**libaegis (AEGIS-128L, AEGIS-128X/256X)**](aegis-aead-libaegis.md) | Portable C library for the AEGIS AEAD family (RFC 10032), roughly 3x AES-GCM throughput on AES-NI/VAES CPUs. | **B** | C | MIT | 🟢 active |
| 10 | [**SNOW-V-GCM**](paper-snow-v-gcm.md) | SNOW-V stream cipher plus GHASH AEAD; \~13% faster than OpenSSL AES-256-GCM at 16 KB on an i7-8650U laptop. | **B** | C++ | no license (study only) | ⚪ unknown |
| 11 | [**MORUS-1280**](paper-morus-1280.md) | CAESAR-finalist AND/XOR/rotate AEAD in AVX2 C; edges out SUPERCOP AES-256-GCM on message-only and 64-byte inputs, loses elsewhere, and is broken. | **B** | C | no license (study only) | 🔴 abandoned |
| 12 | [**Rocca (AES-based AEAD for 6G)**](paper-rocca-aes-based-aead-for-6g-original-pre-attack-version.md) | AES-round-based 256-bit-key AEAD for 6G; \~5x OpenSSL AES-256-GCM at 16 KB on one laptop, much less elsewhere. | **B** | C | CC BY (license of the… (study only) | 🔴 abandoned |
| 13 | [**Mbed TLS**](mbed-tls-mbedtls.md) | Small-footprint C TLS library and PSA Crypto reference implementation; edges OpenSSL EVP only on 64-byte one-shot AEAD calls. | **C** | C | Apache-2.0 OR… | 🟢 active |
| 14 | [**GnuPG (gpg)**](gpg-gnupg.md) | The reference OpenPGP command-line tool; in 2021 runs it streamed public-key encryption 1.3-2.7x faster than Sequoia's sq. | **C** | C | GPL-3.0-or-later | 🟢 active |
| 15 | [**Intel(R) Multi-Buffer Crypto for IPsec (intel-ipsec-mb)**](intel-intel-ipsec-mb.md) | Intel's x86-64 assembly packet-crypto library; batches many packets per SIMD pass; beat OpenSSL AES-CBC+HMAC-SHA-256 once. | **C** | C | BSD-3-Clause | 🟢 active |
| 16 | [**ChaCha20-BLAKE3**](skerkour-chacha20-blake3.md) | Rust committing AEAD (ChaCha20 + keyed-BLAKE3 MAC); about 2x RustCrypto XChaCha20-Poly1305 and AES-256-GCM on 1-10 MB messages. | **C** | Rust | MIT | 🟢 active |
| 17 | [**Bitsliced AEGIS-128L / AEGIS-128X2 (constant-time…**](aegis-aead-aegis-bitsliced.md) | Constant-time bitsliced C AEGIS for CPUs without AES instructions; beats bitsliced AES-GCM by 1.4-6x. | **C** | C | MIT | 🟢 active |
| 18 | [**stdx-go ChaCha20 (Go simd/archsimd)**](skerkour-stdx-go.md) | Go ChaCha20 stream cipher written with experimental simd/archsimd (AVX2/AVX-512/NEON); claims 7.5x over x/crypto's scalar amd64 path. | **C** | Go | MIT (per LICENSE.txt and… | 🟢 active |
| 19 | [**LeMac (pauldreik C++20 port)**](pauldreik-lemac.md) | C++20 library and lemacsum CLI for LeMac, an AES-round MAC measured at \~27x OpenSSL SHA-1 bulk throughput on Zen 4. | **C** | C++ | BSL-1.0 | 🟡 stale |
| 20 | [**HiAE (High-throughput Authenticated Encryption)**](concyclics-hiae.md) | Reference C code for HiAE, Huawei's AES-round AEAD; 2-6.6x OpenSSL AES-256-GCM on 16 KB messages on recent x86/ARM. | **C** | C | no license (study only) | 🟢 active |
| 21 | [**Crypto++**](weidai11-cryptopp.md) | Broad C++ crypto class library; a 2013 hobby benchmark had its CAST-128-CBC about 1.3-1.4x faster than libgcrypt. | **D** | C++ | BSL-1.0 | 🟢 active |
| 22 | [**Botan**](randombit-botan.md) | Broad BSD-licensed C++20 crypto toolkit; maintainer reports faster small-message AES-128-GCM than OpenSSL 3.6.0 on one Skylake. | **D** | C++ | BSD-2-Clause | 🟢 active |
| 23 | [**TgCrypto (pyrogram/tgcrypto)**](pyrogram-tgcrypto.md) | Archived C extension for Python giving Pyrogram AES-256-IGE/CTR/CBC; replaces pure-Python pyaes, does not beat OpenSSL. | **D** | C | LGPL-3.0-or-later | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
