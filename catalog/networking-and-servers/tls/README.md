# TLS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** OpenSSL, BoringSSL, rustls  
**16 entries:** 3 tier A · 4 tier B · 9 tier C · 0 tier D · 15 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**rustls**](rustls-rustls.md) | Memory-safe Rust TLS 1.2/1.3 library on AWS-LC crypto; beats OpenSSL 3.6.1 per core on handshakes, resumption and AES-GCM bulk. | **A** | Rust | Apache-2.0 OR MIT OR ISC | 🟢 active |
| 2 | [**ztls**](mattrobenolt-ztls.md) | Sans-I/O TLS 1.3 state machine in Zig; lower per-record latency than OpenSSL libssl (1.04-3.6x) and rustls on AES-GCM. | **A** | Zig | Apache-2.0 | 🟢 active |
| 3 | [**ChaChaCha**](soda4fries-chachacha.md) | Experimental AVX-512 ChaCha20-Poly1305 assembly for x86-64 Linux; 19-48% fewer cycles/byte than OpenSSL's assembly on AMD Zen 5. | **A** | C | Apache-2.0 | 🟢 active |
| 4 | [**wolfSSL**](wolfssl-wolfssl.md) | Embedded-first C TLS 1.3 library, not an OpenSSL fork, that beat every OpenSSL version in HAProxy's 64-core Graviton4 tests. | **B** | C | GPL-3.0 (the LICENSING file… | 🟢 active |
| 5 | [**EverCrypt (HACL\*) Curve25519 (Vale-optimized)**](hacl-star-hacl-star.md) | Formally verified C/asm crypto library; its ADX X25519 took about 4% fewer cycles than OpenSSL's ADX assembly. | **B** | C | Apache-2.0 | 🟢 active |
| 6 | [**AWS-LC**](aws-aws-lc.md) | BoringSSL-derived, OpenSSL-1.1.1-API-compatible TLS/crypto library from AWS; out-scales OpenSSL 3.x in HAProxy handshakes and resumption. | **B** | C | Apache-2.0 OR ISC for new… | 🟢 active |
| 7 | [**OpenSSLNTRU (libsntrup761 + engntru OpenSSL ENGINE)**](opensslntru-cr-yp-to.md) | Batched sntrup761/857 post-quantum key exchange for OpenSSL 1.1.1 TLS 1.3; more LAN handshakes/sec than OpenSSL's asm X25519/P-256. | **B** | C | no license (study only) | 🔴 abandoned |
| 8 | [**FreeBSD in-kernel TLS (kTLS) with NIC TLS offload**](freebsd-freebsd-src.md) | FreeBSD in-kernel TLS record encryption, optionally NIC-offloaded, keeping zero-copy sendfile for HTTPS; beats userspace OpenSSL SSL_write data paths. | **C** | C | BSD-2-Clause | 🟢 active |
| 9 | [**ring**](briansmith-ring.md) | Rust crypto-primitives crate (BoringSSL-derived C/asm) behind rustls; beat OpenSSL 1.5-3.7x on whole-process TLS handshake runs. | **C** | Rust | Apache-2.0 AND ISC (ring's… | 🟢 active |
| 10 | [**Fizz**](facebookincubator-fizz.md) | Meta's C++ TLS 1.3 library built on folly; Meta reports \~10% more load-balancer throughput than its OpenSSL AsyncSSLSocket stack. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 11 | [**Tempesta FW (Tempesta TLS)**](tempesta-tech-tempesta.md) | Linux-kernel TLS 1.2 server stack in the Tempesta FW proxy; 6-83% more handshakes/s than Nginx+OpenSSL in vendor tests. | **C** | C | GPL-2.0 | 🟢 active |
| 12 | [**aws-lc-rs**](aws-aws-lc-rs.md) | Rust crypto crate with a ring-style API over AWS-LC and optional FIPS module; beat OpenSSL in wtx handshake runs. | **C** | Rust | ISC AND (Apache-2.0 OR ISC) | 🟢 active |
| 13 | [**picotls "fusion" AES-GCM engine**](h2o-picotls.md) | x86-64 AES-GCM engine inside picotls, tuned for short QUIC packets; \~1.3x OpenSSL 1.1.1g throughput at 1440-byte records. | **C** | C | MIT | 🟢 active |
| 14 | [**Graviola**](ctz-graviola.md) | Rust crypto on formally verified s2n-bignum assembly, a rustls backend; one-handshake processes ran 1.6-3.8x faster than OpenSSL-backed. | **C** | Rust | Apache-2.0 OR ISC OR MIT-0 | 🟢 active |
| 15 | [**Cloudflare ChaCha20-Poly1305 (sslconfig OpenSSL patch)**](cloudflare-sslconfig.md) | Cloudflare's 2016 OpenSSL 1.0.2 patch adding x86-64 ChaCha20-Poly1305 TLS suites; about 7% faster seal than OpenSSL 1.1.0-pre on Haswell. | **C** | C | BSD-3-Clause | 🟡 stale |
| 16 | [**curve25519 (mehdi sotoodeh / "Mehdi")**](msotoodeh-curve25519.md) | C/x86-64-asm X25519 and Ed25519 library; precomputed fixed-base tables give 2.8x faster Ed25519 keygen than OpenSSL 1.1.1. | **C** | C | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
