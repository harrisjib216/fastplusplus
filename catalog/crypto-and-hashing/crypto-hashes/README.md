# Cryptographic hashes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md)</sub>

**What these beat:** OpenSSL SHA-2/SHA-3, BLAKE2  
**19 entries:** 4 tier A · 5 tier B · 8 tier C · 2 tier D · 16 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**blake2b_simd / blake2s_simd**](oconnor663-blake2-simd.md) | Rust BLAKE2b/2s/2bp/2sp crates with AVX2/SSE4.1 kernels; its BLAKE2b hashes about 1.8x faster than OpenSSL SHA-512 in its own benchmark. | **A** | Rust | MIT | 🟢 active |
| 2 | [**rscrypto**](loadingalias-rscrypto.md) | Zero-dependency Rust crypto crate whose SIMD/asm SHA-2, SHA-3, BLAKE2 and AEADs beat RustCrypto, ring and aws-lc-rs in its benchmarks. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**sha256mb**](asylian21-sha256mb.md) | Go multi-buffer SHA-256 for batches of 33-byte pubkeys; its 4-lane ARMv8 kernel runs \~2.6x faster than crypto/sha256.Sum256 on M3. | **A** | Go | MIT | 🟢 active |
| 4 | [**sha2-with-c-intrinsic (AWS Crypto Algorithms Group)**](aws-samples-sha2-with-c-intrinsic.md) | C-intrinsics SHA-256/SHA-512 kernels from AWS; only the SHA-NI SHA-256 path beats OpenSSL's assembly, by 5-8%. | **A** | C | Apache-2.0 | 🔴 abandoned |
| 5 | [**BLAKE3**](blake3-team-blake3.md) | Official Rust/C implementation of BLAKE3, a Merkle-tree hash/XOF/MAC about 4x faster than SHA-256 on long single-core inputs. | **B** | Rust | CC0-1.0 OR Apache-2.0 OR… | 🟢 active |
| 6 | [**LSH-256 / LSH-512 (Korean hash standard, TTAK.KO-12.0276)**](paper-lsh-hash.md) | Korean-standard LSH-256/LSH-512 hash; SUPERCOP's SIMD C code beats BLAKE2 and SHA-3 on long x86 messages. | **B** | C | BSL-1.0 (the Crypto++… | 🟢 active |
| 7 | [**KangarooTwelve (XKCP)**](xkcp-xkcp.md) | Keccak team's C package; its KangarooTwelve XOF hashes long messages 5-8x faster than SHAKE128 via SIMD tree hashing. | **B** | C | CC0-1.0 for most files… (study only) | 🟢 active |
| 8 | [**j-lanes tree hashing mode and j-lanes SHA-256 (Gueron)**](paper-j-lanes-tree-hashing-mode-and-j-lanes-sha-256-gueron.md) | Tree-hash mode that runs one message as 4 interleaved SHA-256 lanes on AVX; 2-2.5x OpenSSL 1.0.1c, different digests. | **B** | any | no license (study only) | 🔵 finished |
| 9 | [**Simultaneous hashing of multiple messages / S-HASH (Gueron…**](paper-simultaneous-hashing-of-multiple-messages-s-hash-gueron-krasnov.md) | Multi-buffer SHA-256 that hashes 4 independent messages per AVX register with standard digests; 3.42x OpenSSL 1.0.1 on 4KB messages. | **B** | any | no license (study only) | 🔵 finished |
| 10 | [**libsodium (BLAKE2b)**](jedisct1-libsodium.md) | libsodium's crypto_generichash BLAKE2b: \~1.2-2.7x OpenSSL EVP BLAKE2b-512 on 64 B-1 KB inputs, roughly even from 4 KB. | **C** | C | ISC | 🟢 active |
| 11 | [**Firedancer fd_sha256 batch (AVX-512 / AVX2 / SHA-NI)**](firedancer-io-firedancer.md) | Firedancer's 8- and 16-lane multi-buffer SHA-256 kernels in C; about 2x the Rust sha2 crate on AVX-512 x86. | **C** | C | Apache-2.0 | 🟢 active |
| 12 | [**Intel ISA-L Crypto (multi-buffer SHA)**](intel-isa-l-crypto.md) | Intel's SIMD multi-buffer SHA/MD5/SM3 hashing library; beats single-buffer SHA-256 throughput when many independent buffers are in flight. | **C** | C | BSD-3-Clause | 🟢 active |
| 13 | [**hashtree**](offchainlabs-hashtree.md) | Batched SHA-256 of many fixed 64-byte inputs for Merkle trees; \~4.7x OpenSSL's per-message SHA256() on AVX2. | **C** | C | MIT | 🟢 active |
| 14 | [**keccak-batch**](nxm-rs-keccak-batch.md) | Rust crate that hashes 2/4/8 equal-length inputs at once with SIMD Keccak-256; \~5.5x per hash over keccak-asm (README). | **C** | Rust | AGPL-3.0 | 🟢 active |
| 15 | [**tape-sha256**](spool-labs-tape-sha256.md) | Pure-Rust multi-buffer SHA-256 for batches and hash chains; 2-3.5x the serial sha2 crate on x86 batch hashing. | **C** | Rust | Apache-2.0 | 🟢 active |
| 16 | [**sha256-simd (minio)**](minio-sha256-simd.md) | Go SHA-256 using SHA-NI, ARMv8 SHA2 and 16-lane AVX-512; once beat crypto/sha256, now only its multi-buffer mode might. | **C** | Go | Apache-2.0 | 🔴 abandoned |
| 17 | [**blake2b-simd (Minio)**](minio-blake2b-simd.md) | Archived Go BLAKE2b with AVX2/AVX/SSSE3 assembly, about 4x its pure-Go fallback and faster than 2016-era Go SHA-256/SHA-512. | **C** | Go | Apache-2.0 | 🔴 abandoned |
| 18 | [**Intel Cryptography Primitives Library**](intel-cryptography-primitives.md) | Intel's C crypto-primitives library (ex-IPP Crypto) with SHA-NI/AVX2/AVX-512 SHA-1/2/3 kernels; claimed but unbenchmarked alternative to OpenSSL. | **D** | C | Apache-2.0 | 🟢 active |
| 19 | [**SHA-Intrinsics (noloader)**](noloader-sha-intrinsics.md) | Public-domain SHA-1/SHA-256 block functions on Intel SHA-NI and ARMv8 crypto intrinsics, plus POWER8 SHA-256/512; no measured baseline. | **D** | C | LicenseRef-Public-Domain | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
