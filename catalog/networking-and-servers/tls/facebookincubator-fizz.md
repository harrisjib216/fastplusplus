# Fizz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Meta's C++ TLS 1.3 library built on folly; Meta reports \~10% more load-balancer throughput than its OpenSSL AsyncSSLSocket stack.

| | |
|---|---|
| **Beats** | OpenSSL (via folly's AsyncSSLSocket) |
| **Claimed result** | "we found in our load balancer benchmarks that Fizz has 10% higher throughput than our prior SSL library which uses folly's AsyncSSLSocket"; also states Fizz uses less memory per connection |
| **Workload** | Facebook load-balancer production traffic comparing Fizz's AsyncFizzServer/Client TLS 1.3 implementation against folly's prior AsyncSSLSocket-based TLS stack |
| **Metric** | throughput |
| **Adoption** | 1.2k stars; used in production at Facebook/Meta load balancers |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/facebookincubator/fizz) · [benchmark](https://github.com/facebookincubator/fizz#performance) |

## Verdict

The README says, in text unchanged since commit 5a46d88 (2018-08-03), that Meta's internal load-balancer benchmarks showed about 10% higher throughput for Fizz than for its prior TLS stack on folly's AsyncSSLSocket (OpenSSL libssl), with less memory per connection. No OpenSSL version, cipher suite, record size, hardware, compiler or data is given, and the 2018 engineering blog repeats only 'approximately 10 percent higher throughput'. Fizz still uses OpenSSL for the ciphers, so the gain is in the record layer and buffer handling.

## Use it when

- You already terminate TLS on folly AsyncSocket (Proxygen, mvfst, or custom folly servers) and want the TLS 1.3 stack Meta runs at scale; Meta's 2018 blog says it handles millions of TLS 1.3 handshakes per second.
- Load balancers or proxies with many concurrent connections, where per-connection memory and copy overhead matter more than raw cipher speed.
- You need handshake features that are awkward through libssl: future-based async certificate signing and ticket decryption (offload to a key server), 0-RTT with a sliding-Bloom replay cache, delegated credentials, ECH, or exported authenticators.
- QUIC or custom protocols that need a TLS 1.3 handshake state machine with direct access to traffic secrets, not a byte-stream socket.
- Linux servers on AES-GCM that want to hand the record layer to the kernel after the handshake (experimental kTLS support, TLS 1.3 AES-128/256-GCM only).

## Skip it when

- You must serve TLS 1.2 or older clients from one library: Fizz is TLS 1.3 only, and fallback means running OpenSSL libssl (for example AsyncSSLSocket) alongside it.
- You are not already on folly: the build needs folly, fmt, glog, gflags, libevent, OpenSSL, libsodium, zlib and zstd, and the public API uses IOBuf, EventBase and AsyncTransport throughout.
- You need a reproducible speedup before adopting: the only number is a first-party 2018 README sentence with no methodology, hardware, OpenSSL version or data, and no independent benchmark was found (HN, arXiv).
- Your bottleneck is crypto primitives: bulk AEAD, hashing and P-curve ECDHE still run in OpenSSL libcrypto, so a faster libcrypto (e.g. AWS-LC) is a separate fix Fizz does not provide.
- You need a C API or a stable ABI: a C ABI request (issue #71) is open, releases are weekly date tags built with getdeps, and core internals recently moved from exceptions to Status return codes.

## How it is fast

The record layer works on chains of folly IOBufs (scatter/gather I/O). The AEAD encrypts in place when a buffer is unshared, appends the content-type byte and tag into existing tailroom, and writes the 5-byte record header into headroom reserved via setEncryptedBufferHeadroom, so a typical write avoids extra allocations and memcpys. Reads can use readv (ReadVec mode) or Linux TCP zero-copy receive (zeroCopyMemStore), and setDecryptInplace decrypts records inside the receive buffers. The crypto is unchanged: AES-GCM, ChaCha20-Poly1305, SHA-2, P-256/384/521 ECDHE and X.509 go through OpenSSL, while X25519 and the RNG come from libsodium. Any gain therefore comes from fewer copies and less per-connection state, not from faster ciphers.

## Compared with alternatives

Pick Fizz over picotls or ztls when your server already runs on folly/Proxygen/mvfst and you want Meta's production TLS 1.3 stack with async key offload and 0-RTT; picotls is the lighter C TLS 1.3 library (with the faster fusion AES-GCM), and ztls publishes per-operation numbers against OpenSSL where Fizz publishes none. Pick AWS-LC or wolfSSL instead when you need an OpenSSL-API-compatible libssl with TLS 1.2 and published HAProxy handshake results. Fizz can also run on top of a faster libcrypto rather than replace it.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, exported as fizz::fizz); getdeps.py builds it together with its dependencies |
| **Dependencies** | folly, fmt, OpenSSL (libcrypto), libsodium, glog (default logging backend; XLOG or DISABLED selectable), gflags, libevent, zlib, zstd, Threads; optional liboqs &gt;= 0.11.0 for ML-KEM hybrid groups and libaegis for the AEGIS cipher suites; GTest/GMock 1.8+ for tests |
| **Minimum toolchain** | C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20 when unset), CMake 3.14+; the GitHub description and the 2018 blog still say C++14 |
| **Platforms** | Linux, macOS and Windows (getdeps CI workflows for each); kTLS offload is Linux-only and experimental; open build issues on RISC-V (#161), PPC 8-byte atomics (#139), macOS Monterey (#151), and an open Android build question (#106) |
| **Thread safety** | not documented. The transports are folly DelayedDestruction objects tied to one EventBase (attach/detachEventBase), and contexts are shared as shared_ptr&lt;const FizzServerContext&gt;/FizzClientContext. |
| **Drop-in for the baseline** | partial — AsyncFizzServer/Client implement the same folly AsyncTransportWrapper interface as AsyncSSLSocket, but contexts, cert managers and handshake callbacks differ, and TLS 1.2 clients still need AsyncSSLSocket/OpenSSL via the fallback hook |

## Gotchas

- In-place encryption is opportunistic: by default it applies only to a unique buffer that is not split into records. Writes over the 16 KB record size, or cloned/shared IOBufs, take the allocate-and-copy path. setEncryptInplace(true) forces it, but then silently overwrites the plaintext of any other IOBuf that shares the buffer.
- The default ReadBuffer mode reads into 4000-byte allocations (minimum read 1460 bytes); the header warns this can raise memory use and blocks in-place decryption of shared buffers. ReadVec mode needs an IOVecQueueOps you supply.
- Past remote DoS CVEs: CVE-2019-3560 (infinite loop in PlaintextRecordLayer, fixed v2019.03.04.00), CVE-2019-11924 (memory exhaustion from padding-only handshake fragments, fixed v2019.08.05.00) and CVE-2023-23759 (remotely triggerable CHECK crash when the second ClientHello changes the cipher list, fixed v2023.01.30.00). Track the weekly tags.
- Issue #36 (open): if you list ChaCha20-Poly1305 as supported on a build whose OpenSSL lacks it, Fizz can still pick it and fail the handshake; a maintainer says the default config does not list it in that case.

## Known shortcomings

- The '10% higher throughput' claim is first-party (2018) with no methodology, against Facebook's 2018 OpenSSL-based AsyncSSLSocket; Fizz still uses OpenSSL libcrypto and libsodium, so the gain is in the TLS layer. TLS 1.3 only; depends on folly.
- The \~10% throughput claim has no data (OpenSSL version, cipher, record size, hardware, compiler) and no independent benchmark; the shipped benchmark tools have no published results. The crypto still comes from OpenSSL and libsodium; the gain is in the record layer and IOBuf handling. In-place encryption applies only to unshared buffers not split into records; forcing it with setEncryptInplace(true) overwrites plaintext of shared IOBufs. TLS 1.3 only, so TLS 1.2 clients need a fallback stack. Needs folly, fmt, glog, gflags, libevent, OpenSSL, libsodium, zlib, zstd; no C API (#71); weekly date tags, internals moving from exceptions to Status codes. CMake now requires C++20 (not C++14). Past remote DoS CVEs (2019-3560, 2019-11924, 2023-23759, fixed). Build failures on RISC-V (#161), PPC (#139), macOS Monterey (#151); kTLS experimental, Linux and AES-GCM only.

## Caveats and trade-offs

First-party (Meta) README claim with no published methodology, hardware or reproducible artifact; the '10%' number is not backed by linked data. The sentence was added in commit 5a46d88 (2018-08-03) and has not changed since, so the baseline is Meta's 2018-era AsyncSSLSocket/OpenSSL stack; the exact OpenSSL version is not stated. Fizz itself still uses OpenSSL libcrypto and libsodium for crypto primitives (README Dependencies, fizz/CMakeLists.txt find_package(OpenSSL REQUIRED)), so the win is in the TLS 1.3 state machine and record layer (IOBuf scatter/gather, in-place encryption), not in faster crypto. GitHub reports the license as NOASSERTION; the LICENSE file is BSD 3-Clause text.

Depends on folly (IOBuf, AsyncTransportWrapper), a large dependency graph; C++14 only; scatter/gather in-place encryption trades API simplicity for the throughput/memory win

## Maintenance

Actively maintained by Meta: commits through 2026-09-26 and weekly date-tagged releases (latest v2026.09.21.00). It is BSD-3-Clause (the LICENSE file; GitHub shows NOASSERTION), but in practice usable only inside a folly/getdeps build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section says, word for word, that Fizz has 10% higher throughput than Meta's prior SSL library built on folly's AsyncSSLSocket (an OpenSSL libssl wrapper) and uses less memory per connection. This is a first-party number with no linked benchmark code, hardware, compiler, flags or data, so it is C.
- **Verifier notes:** The quote and the baseline match the README exactly, and the tier stays C. Metadata checks out: 1,202 stars, not a fork, not archived, last commit 2026-09-26 (active), BSD-3-Clause per the LICENSE file. The only change is added caveat context: the 2018 date and the fact that Fizz still links OpenSSL libcrypto.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebookincubator/fizz#performance>
  - <https://github.com/facebookincubator/fizz>
  - <https://github.com/facebookincubator/fizz/blob/main/LICENSE>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/CMakeLists.txt>
  - <https://github.com/facebookincubator/fizz/commit/5a46d888181ac2d3764af89005f83dd138365c03>
- **Sources the enricher read:**
  - <https://github.com/facebookincubator/fizz>
  - <https://github.com/facebookincubator/fizz#performance>
  - <https://github.com/facebookincubator/fizz/blob/main/README.md>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/CMakeLists.txt>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/cmake/FizzOptions.cmake>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/crypto/aead/Aead.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/crypto/aead/CryptoUtil.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/backend/openssl/crypto/aead/OpenSSLEVPCipher.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/backend/openssl/crypto/aead/OpenSSLEVPCipher-inl.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/record/EncryptedRecordLayer.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/record/EncryptedRecordLayer.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/record/BufAndPaddingPolicy.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/protocol/AsyncFizzBase.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/protocol/AsyncFizzBase.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/server/AsyncFizzServer.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/server/Actions.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/server/FizzServerContext.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/client/FizzClientContext.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/protocol/MultiBackendFactory.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/experimental/ktls/KTLS.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/experimental/ktls/KTLS.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/util/Status.h>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/tool/FizzServerBenchmarkCommand.cpp>
  - <https://github.com/facebookincubator/fizz/blob/main/fizz/record/test/EncryptedRecordBench.cpp>
  - <https://github.com/facebookincubator/fizz/commit/5a46d888181ac2d3764af89005f83dd138365c03>
  - <https://github.com/facebookincubator/fizz/tags>
  - <https://github.com/facebookincubator/fizz/commits>
  - <https://github.com/facebookincubator/fizz/issues>
  - <https://github.com/facebookincubator/fizz/issues/36>
  - <https://github.com/facebookincubator/fizz/issues/110>
  - <https://github.com/facebookincubator/fizz/issues/139>
  - <https://github.com/facebookincubator/fizz/issues/169>
  - <https://github.com/facebookincubator/fizz/security/advisories>
  - <https://github.com/facebook/mvfst/blob/main/CMakeLists.txt>
  - <https://github.com/facebook/proxygen/blob/main/CMakeLists.txt>
  - <https://engineering.fb.com/2018/08/06/security/fizz/>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Fizz>
  - <https://hn.algolia.com/api/v1/search?query=fizz%20tls&tags=story>
  - <https://hn.algolia.com/api/v1/items/17698883>
  - <https://export.arxiv.org/api/query?search_query=abs:fizz%20AND%20abs:TLS>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/facebookincubator/fizz`) · [data/wave5/enrich/raw/github_com_facebookincubator_fizz.json](../../../data/wave5/enrich/raw/github_com_facebookincubator_fizz.json) (enrichment confidence 0.6)

</details>
