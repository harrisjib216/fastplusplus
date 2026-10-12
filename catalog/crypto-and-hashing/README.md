# Crypto and hashing

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Ciphers, cryptographic and non-cryptographic hashes, signatures and encoders that beat OpenSSL, libsodium and the common hash functions.

**122 entries in 5 categories:** 33 tier A · 34 tier B · 50 tier C · 5 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [AEAD and ciphers](aead-and-ciphers/README.md) | 23 | 8 | 4 | 8 | 3 | OpenSSL AES-GCM, ChaCha20-Poly1305, libsodium |
| [Cryptographic hashes](crypto-hashes/README.md) | 19 | 4 | 5 | 8 | 2 | OpenSSL SHA-2/SHA-3, BLAKE2 |
| [Encoding (base64, hex, CRC)](encoding/README.md) | 26 | 8 | 1 | 17 | 0 | base64, hex, CRC32 baselines the benchmark names |
| [Non-cryptographic hashes](non-crypto-hashes/README.md) | 31 | 6 | 18 | 7 | 0 | xxHash, wyhash, CityHash, std::hash |
| [Signatures and key exchange](signatures-kem/README.md) | 23 | 7 | 6 | 10 | 0 | OpenSSL, libsodium, BoringSSL, liboqs |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**xxHash**](non-crypto-hashes/cyan4973-xxhash.md) | SIMD-vectorized non-cryptographic hash family; XXH3 beats CityHash \~2.7x on in-RAM buffer bandwidth. | [Non-cryptographic hashes](non-crypto-hashes/README.md) | **A** | C | BSD-2-Clause (library… | 🟢 active |
| 2 | [**libsecp256k1 (bitcoin-core/secp256k1)**](signatures-kem/bitcoin-core-secp256k1.md) | Bitcoin Core's secp256k1-only C signature library; ECDSA verification 2.5-5.5x faster than the 2015-era OpenSSL it replaced. | [Signatures and key exchange](signatures-kem/README.md) | **A** | C | MIT | 🟢 active |
| 3 | [**aklomp/base64 (SIMD Base64 C99 library)**](encoding/aklomp-base64.md) | Portable C99 SIMD base64 codec with runtime CPU dispatch; the Muła–Lemire paper measured its decoder about 4x faster than Chrome's. | [Encoding (base64, hex, CRC)](encoding/README.md) | **A** | C | BSD-2-Clause | 🟢 active |
| 4 | [**foldhash**](non-crypto-hashes/orlp-foldhash.md) | Seeded folded-multiply Rust hasher for in-memory HashMaps; about 4.6x lower geometric-mean time per op than SipHash-1-3. | [Non-cryptographic hashes](non-crypto-hashes/README.md) | **A** | Rust | Zlib | 🟢 active |
| 5 | [**CLHash**](non-crypto-hashes/simdhash-clhash.md) | Keyed 64-bit universal string hash built on carry-less multiply; about 40% faster than CityHash64 on inputs over 64 bytes. | [Non-cryptographic hashes](non-crypto-hashes/README.md) | **A** | C | Apache-2.0 | 🟢 active |
| 6 | [**pybase64**](encoding/mayeut-pybase64.md) | Python base64 module replacement backed by the SIMD libbase64 codec; roughly 6.6x faster encode than the stdlib. | [Encoding (base64, hex, CRC)](encoding/README.md) | **A** | Python | BSD-2-Clause | 🟢 active |
| 7 | [**blake2b_simd / blake2s_simd**](crypto-hashes/oconnor663-blake2-simd.md) | Rust BLAKE2b/2s/2bp/2sp crates with AVX2/SSE4.1 kernels; its BLAKE2b hashes about 1.8x faster than OpenSSL SHA-512 in its own benchmark. | [Cryptographic hashes](crypto-hashes/README.md) | **A** | Rust | MIT | 🟢 active |
| 8 | [**fast-crc32 (corsix) — novel CRC32/CRC32C SIMD kernels**](encoding/corsix-fast-crc32.md) | Code generator emitting tuned CRC32/CRC32C C kernels (PCLMUL/VPCLMULQDQ/PMULL plus crc32 instruction) that beat Chromium zlib's SIMD CRC32. | [Encoding (base64, hex, CRC)](encoding/README.md) | **A** | C | MIT OR Zlib | 🟢 active |
| 9 | [**curve25519-voi**](signatures-kem/oasisprotocol-curve25519-voi.md) | Go Ed25519/X25519/sr25519 library ported from curve25519-dalek; \~1.9x faster signing, \~1.7x faster verification than Go 1.17 crypto/ed25519. | [Signatures and key exchange](signatures-kem/README.md) | **A** | Go | BSD-3-Clause | 🟢 active |
| 10 | [**const-hex**](encoding/danipopes-const-hex.md) | Rust hex codec with runtime-dispatched SIMD and const-fn API; near drop-in for `hex`, 6–100x faster on README benches. | [Encoding (base64, hex, CRC)](encoding/README.md) | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
