# ztls

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `Apache-2.0` · 🟢 active

> Sans-I/O TLS 1.3 state machine in Zig; lower per-record latency than OpenSSL libssl (1.04-3.6x) and rustls on AES-GCM.

| | |
|---|---|
| **Beats** | OpenSSL libssl 3.6.3; rustls 0.23.4x |
| **Claimed result** | Headline row (AppPingPong AES-128-GCM 1350B, x86_64 c7i.2xlarge, n=10): ztls 790.7 ns/op vs rustls 1447.5 ns/op (1.83x) vs OpenSSL libssl 1820.5 ns/op (2.30x). ztls executes 42.7% of libssl's cycles/op and 54.8% of rustls's on that row (row-perf capture). Faster than libssl on all 45 comparable app-data rows on x86_64, aarch64 and macOS (from +4% on ChaCha20 16384B ping-pong on aarch64 to +261% on AES-128-GCM 16B client-to-server on x86_64). Faster than rustls on all 30 AES-GCM rows per platform (x86_64 +65% to +131%). On x86_64 it loses to rustls on ChaCha20-Poly1305 at 16B/128B (-50% to -56%) and, per the benchstat file, by about 6% at 1350B (the page calls this an approximate tie). |
| **Workload** | Sans-I/O TLS 1.3 in-memory application-data round trips (client-to-server, server-to-client, ping-pong) at record sizes 16B, 128B, 1350B, 8192B, 16384B, across TLS_AES_128_GCM_SHA256, TLS_AES_256_GCM_SHA384, and TLS_CHACHA20_POLY1305_SHA256, over caller-owned in-memory transport (no sockets), n=10 captures with formal confidence intervals |
| **Metric** | latency |
| **Hardware** | AWS c7i.2xlarge (Intel Xeon Platinum 8488C, x86_64, KVM guest); AWS c7g.2xlarge, which the page and README call Graviton4 but whose committed lscpu metadata shows Neoverse-V1 / 'AWS Graviton3 CPU @ 2.6GHz'; Apple M1 Max (macOS Darwin 24.6) |
| **Compiler and flags** | Zig 0.15.2, -Doptimize=ReleaseFast, native CPU target, crypto_backend=openssl (OpenSSL 3.6.3 libcrypto via nix); comparison backends OpenSSL 3.6.3 libssl and rustls 0.23.40 (x86_64) / 0.23.41 (aarch64, macOS) release profile, rustc 1.97.0 on the x86_64 capture; benchstat over --count 10 --benchtime 500ms. Captured at git revisions 2c102a5 (x86_64), e39f5a6 (aarch64) and 80083f5 (macOS), before ztls required Zig 0.16 |
| **Adoption** | 7 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/mattrobenolt/ztls) · [benchmark](https://github.com/mattrobenolt/ztls/blob/main/docs/research/PERFORMANCE.md) |

## Verdict

The comparison covers in-memory TLS 1.3 application-data rows with no sockets: ztls over caller buffers, libssl over memory-BIO pairs and rustls over Vec transfer buffers. ztls was built with Zig 0.15.2 ReleaseFast for the native CPU and linked the same OpenSSL 3.6.3 libcrypto as the libssl baseline; rustls 0.23.40/41 used its ring provider, not its default aws-lc-rs. In n=10 benchstat captures ztls beat libssl on all 45 rows on each host (c7i.2xlarge Xeon 8488C, c7g.2xlarge that lscpu identifies as Graviton3 although the docs say Graviton4, and an M1 Max), by +4% to +261%; the headline AES-128-GCM 1350B ping-pong measured 790.7 ns vs libssl 1820.5 ns and rustls 1447.5 ns.

## Use it when

- Zig servers, proxies or clients that already own their event loop (epoll, io_uring, kqueue via libxev, or blocking std.Io) and want TLS 1.3 without adopting a library's I/O model.
- Small to MTU-sized AES-GCM records (16B-1350B) where per-record overhead dominates: on x86_64 AES-128-GCM, 202 ns vs libssl's 731 ns at 16B client-to-server, and 1.83x faster than rustls on 1350B ping-pong.
- Many long-lived connections where per-connection memory matters: the post-handshake EstablishedSession measured 736 B (OpenSSL lane) to about 1.9 KB (AWS-LC/BoringSSL), with no ztls-owned heap state (a Zig 0.15.2 measurement the docs call historical).
- Linux services that want a userspace TLS 1.3 handshake followed by a kernel kTLS data plane, using the ztls_ktls module rather than hand-coding the key handoff.
- Designs that must keep the allocator out of TLS parsing, framing and transcript code, provided the libcrypto backend's own setup-time allocations are acceptable.

## Skip it when

- Anything carrying real traffic or secrets today: pre-alpha with no release tag, an API that changes without notice, and no external audit. SECURITY.md says not to use it in front of real traffic, and an internal review found and fixed a PSK server-auth bypass and an integer-overflow DoS.
- You need TLS 1.2 fallback, DTLS, Windows, or a C/C++/Rust/Go caller. These are out of scope, and the C surface covers only the client lifecycle.
- Handshake-bound workloads: there is no handshake speed claim. On the full-handshake row, which the project itself marks non-equivalent, ztls took 391.7 µs against libssl's 354.9 µs (libssl also verified CertificateVerify) and rustls's 147.5 µs (rustls skipped signature verification).
- Tiny ChaCha20-Poly1305 records on x86_64: 50-56% slower than rustls at 16B and 128B, and about 6% slower at 1350B, because OpenSSL's EVP ChaCha20-Poly1305 path costs more than ring's for small inputs.
- Server keys that need Ed25519 or P-521 CertificateVerify signing, rsa_pss_pss schemes, or encrypted PEM private keys. These fail at load or are not implemented.

## How it is fast

Each direction's RecordLayer keeps an AEAD context that is keyed once when traffic keys are installed; per record it writes the 5-byte header, derives the nonce with one 12-byte vector XOR of IV and sequence number, encrypts or decrypts in place inside the caller's buffer, and returns a subslice (the inner content type is found by a last-byte fast path plus a SIMD scan over padding). That removes the BIO copies, per-record allocation and libssl's WPACKET / tls13_cipher / EVP_CIPHER_CTX_ctrl dispatch; with the OpenSSL backend a record costs one IV-only EVP_\*Init_ex, two Update calls, Final and a tag ctrl on the same libcrypto primitive libssl uses (encryptPrepared also skips the one plaintext memcpy). On the x86_64 AES-128-GCM 1350B ping-pong row, perf counters show ztls at 42.7% of libssl's cycles/op and 54.8% of rustls's, with rustls's extra time in ChunkVecBuffer::write_to, memmove and malloc. The gain is record-layer overhead removal, not faster crypto.

## Compared with alternatives

Pick ztls when you write Zig, own your I/O loop, and your cost is per-record overhead on small AES-GCM records. The AWS-LC and wolfSSL entries measure full-handshake throughput under HAProxy, where ztls has no winning evidence, and ztls can itself link AWS-LC as its crypto backend. For C/C++ callers or production use, Fizz or picotls are the mature choices; picotls's fusion engine speeds up the AES-GCM primitive itself rather than the layers around it.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | A libcrypto located via pkg-config: OpenSSL 3.x (all benchmarks used 3.6.3), AWS-LC (5.5.0 used in consumer gates) or BoringSSL; libxev only if ztls_xev is enabled. No minimum libcrypto version is documented. |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon). The published benchmarks were built with Zig 0.15.2, which is no longer supported. |
| **Platforms** | Linux and macOS; x86_64 and aarch64 were benchmarked (Xeon 8488C, Graviton3, Apple M1 Max). ztls_ktls is Linux-only and Windows is out of scope. Build for the native CPU (the default) for published performance. |
| **Thread safety** | Core engines are plain mutable per-connection values with no documented internal locking. The ztls_std wrapper supports exactly one reader task and one writer task per connection (TX serialized by a mutex); multiple readers or writers are unsupported, and ztls_ktls assumes a single-threaded blocking caller. |
| **Drop-in for the baseline** | false — a different API shape (records in, records out over caller-owned buffers, with an explicit completeWrite latch), Zig-only, and no libssl API or ABI compatibility |

## Gotchas

- Every record-producing call sets a pending-write latch. Call completeWrite() only after the bytes are actually on the transport, or the next engine call returns error.PendingWrite. For partial or non-blocking writes, use the Outbox helper, which keeps the OutBuffer borrowed until the record drains.
- Decryption happens in place. Application data is a slice into RecordBuffer storage and stays valid only until the next next()/writable() call, so copy it first. After error.AuthenticationFailed the buffer may hold unauthenticated plaintext on the OpenSSL backend; treat it as poisoned.
- 'Zero allocation' covers only ztls's own code. The OpenSSL lane heap-allocates two EVP_CIPHER_CTX per record layer at key installation, key exchange and signing allocate inside libcrypto, and AWS-LC keeps per-thread RNG and error-queue state. Budget caller memory too: RecordBuffer's recommended storage is about 33 KiB and a ServerHandshake is about 19-21 KB.
- Performance depends on the build target. The benchmark doc warns that generic or baseline CPU targets can select slower std.crypto paths; issue #138 measured +43.6% handshake cycles on a baseline build before SHA-2 moved to the backend. Ed25519 chain verification still runs on std.crypto.

## Known shortcomings

- Uses OpenSSL 3.6.3 libcrypto for its crypto, so the win over libssl is TLS record-layer and wrapper overhead, not faster crypto. Loses to rustls by about 6% on x86 ChaCha20 at 1350 B; the handshake row is not like-for-like. Zig, pre-alpha, 7 stars.
- The rustls baseline is built with ring, not rustls 0.23's default aws-lc-rs. ztls and the libssl baseline share the same OpenSSL 3.6.3 libcrypto, so the win is record-layer overhead (no BIO copies or dispatch, in-place AEAD), not faster crypto. The handshake is slower than libssl (391.7 vs 354.9 us; rustls 147.5 us). Captures used Zig 0.15.2 and older revisions; current ztls needs Zig 0.16 and later handshake fixes were not re-benchmarked. libssl gets a warm-up round the others don't; transport APIs differ; hosts ran with ASLR disabled. 'Zero allocation' covers ztls's own code only (the OpenSSL backend allocates EVP_CIPHER_CTX and libcrypto allocates). Pre-alpha, single author, no release or audit; SECURITY.md says not to face real traffic; an internal review fixed a PSK server-auth bypass and an overflow DoS. Zig-only (C ABI is #30); TLS 1.3 only; Linux/macOS; no encrypted PEM, Ed25519 or P-521 server signing.

## Caveats and trade-offs

Pre-alpha single-author project (7 stars) with no independent reproduction. ztls delegates AEAD, key exchange and SHA-2 to a libcrypto backend (OpenSSL 3.6.3 in all headline captures), the same library as the libssl baseline, so the win over libssl is TLS record-layer and wrapper overhead (WPACKET, tls13_cipher, BIO copies), not faster crypto. Only application-data rows over in-memory transport are compared; the handshake row is explicitly non-equivalent and not claimed. libssl gets one warm-up round while ztls and rustls do not. The captures used Zig 0.15.2 at older revisions, and current ztls requires Zig 0.16. The page labels the c7g.2xlarge host Graviton4, but its lscpu metadata says Graviton3 (Neoverse-V1).

Pre-alpha, API not stable; TLS 1.3 only (no 1.2 fallback, no DTLS, no Windows); crypto primitives (AEAD, ECDHE, signatures, SHA-2) are still delegated to a libcrypto backend (OpenSSL, AWS-LC, or BoringSSL) which allocates during setup, so the zero-allocation claim covers only ztls's own framing/parsing/transcript code, not the crypto backend; loses to rustls on small ChaCha20-Poly1305 records on x86_64; full-handshake row is explicitly documented as non-equivalent across implementations (different certificate-verification scope) and the project itself says not to quote it as a comparison

## Maintenance

Actively developed by a single author (last commit 2026-09-26, 7 stars, no release tag; depend on main or a commit hash). Apache-2.0, Zig 0.16-only, and pre-alpha by its own statement; known downstream use is limited to the author's z53 DNS forwarder and a private PlanetScale consumer called handoff.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** PERFORMANCE.md compares ztls against OpenSSL 3.6.3 libssl (memory-BIO harness bench/bio.zig) and rustls (bench/rustls/src/main.rs), with the ztls harness in src/bench/record_protection.zig. Committed n=10 captures under docs/research/perf/ carry metadata: Zig 0.15.2 ReleaseFast with a native CPU target, and lscpu showing Intel Xeon Platinum 8488C (c7i.2xlarge) and Neoverse-V1/Graviton3 (c7g.2xlarge), plus an Apple M1 Max run. Code, compiler, flags and CPU model are all stated.
- **Verifier notes:** Numbers verified against docs/research/perf/20260712-102422-ec2-c7i-2xlarge/benchstat.txt plus the c7g and M1 Max benchstat files: libssl loses on all 45 comparable rows on each platform. The hardware field is corrected because the c7g host's own lscpu says Graviton3, not Graviton4. License Apache-2.0 with a vendored Zig MIT file (LICENSE-ZIG), both OSI; 7 stars, last commit 2026-09-26, not fork, not archived.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mattrobenolt/ztls>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/PERFORMANCE.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/README.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-102422-ec2-c7i-2xlarge/metadata.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-102422-ec2-c7i-2xlarge/benchstat.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-201912-ec2-c7g-2xlarge/metadata.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-201912-ec2-c7g-2xlarge/benchstat.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260713-003534-macos-m1max/metadata.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260713-003534-macos-m1max/benchstat.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/LICENSE>
  - <https://github.com/mattrobenolt/ztls/blob/main/LICENSE-ZIG>
- **Sources the enricher read:**
  - <https://github.com/mattrobenolt/ztls>
  - <https://github.com/mattrobenolt/ztls/blob/main/README.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/PERFORMANCE.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/USAGE.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/PRODUCTION_READINESS.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/SECURITY.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/CHANGELOG.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/build.zig.zon>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/RecordLayer.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/aead.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/capi.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/memx.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/crypto/backend_openssl.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/src/crypto/c_openssl.zig>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/PROVIDER_INTERFACE.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/bench/rustls/Cargo.toml>
  - <https://github.com/mattrobenolt/ztls/blob/main/bench/rustls/src/main.rs>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260705-215953-ec2-c7i-2xlarge-row-perf/explanations/AppPingPong-TLS_AES_128_GCM_SHA256-1350.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260705-215953-ec2-c7i-2xlarge-row-perf/explanations/AppClientToServer-TLS_CHACHA20_POLY1305_SHA256-16.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260706-000535-ec2-c7i-2xlarge-handshake-row-perf/explanations/Handshake-TLS_AES_128_GCM_SHA256-1.md>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-102422-ec2-c7i-2xlarge/benchstat.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/perf/20260712-201912-ec2-c7g-2xlarge/metadata.txt>
  - <https://github.com/mattrobenolt/ztls/blob/main/docs/research/CONSUMER_GATE/20260920-launchpad-8814f1e/README.md>
  - <https://github.com/mattrobenolt/ztls/issues>
  - <https://github.com/mattrobenolt/ztls/issues/138>
  - <https://github.com/mattrobenolt/ztls/issues/106>
  - <https://github.com/mattrobenolt/z53>
  - <https://github.com/rustls/rustls/blob/v/0.23.40/rustls/Cargo.toml>
  - <https://hn.algolia.com/api/v1/search?query=ztls&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=mattrobenolt%2Fztls>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/mattrobenolt/ztls`) · [data/wave5/enrich/raw/github_com_mattrobenolt_ztls.json](../../../data/wave5/enrich/raw/github_com_mattrobenolt_ztls.json) (enrichment confidence 0.75)

</details>
