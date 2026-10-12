# QUICHE (Google)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's C++ QUIC/HTTP/3 stack behind Chrome; production A/B trials cut Search latency 8% (desktop) vs TLS/TCP.

| | |
|---|---|
| **Beats** | TCP+TLS (HTTPS over TCP, pre-QUIC production stack) |
| **Claimed result** | Mean Google Search latency reduced 8.0% for desktop users and 3.6% for mobile users; mean YouTube Video Rebuffer Rate reduced 18.0% for desktop and 15.3% for mobile, QUICg vs the TLS/TCP control group (Introduction, and Section 6 'QUIC Performance', Tables 1 and 2). The same Table 1 also gives a mean Video Latency reduction of 8.0% for desktop and 5.3% for mobile. |
| **Workload** | Live production A/B experiment across billions of Chrome, YouTube app, and Google Search app users comparing Google's QUIC implementation (predecessor of this repo, now called QUICHE) against HTTPS-over-TCP for search page latency and video rebuffer rate |
| **Metric** | latency |
| **Adoption** | 898 stars (2026-09-26). README: powers Google's servers, Chromium, Envoy and other projects. The paper says QUIC carried over 30% of Google's egress traffic (about 7% of Internet traffic) in 2017. |
| **Last commit** | 2026-09-25T16:10:07Z |
| **Links** | [repository](https://github.com/google/quiche) · [benchmark](https://storage.googleapis.com/gweb-research2023-media/pubtools/4102.pdf) |

## Verdict

Google's SIGCOMM 2017 paper reports randomized, equal-size production A/B groups of Chrome (desktop) and Google Search/YouTube app (mobile) users, gQUIC version 35 vs a TLS/TCP control (TCP Fast Open enabled on servers), with over a billion samples collected December 2016 to January 2017: mean Search Latency fell 8.0% desktop and 3.6% mobile, mean Video Latency 8.0% and 5.3%, and mean Video Rebuffer Rate 18.0% and 15.3%. There is no lab setup, compiler, flags or hardware; all authors are Google employees, and the same paper reports about 2x server CPU vs TLS/TCP and possible losses above 100 Mbps.

## Use it when

- You serve latency-sensitive HTTPS to clients on the public Internet, especially high-RTT or lossy (mobile, long-haul) users, where saving handshake round trips and avoiding head-of-line blocking is worth more than CPU per byte.
- You want the QUIC stack Chrome actually runs, for interop with Chrome or for features other libraries lack or lag on: MASQUE proxying, WebTransport, Media over QUIC, BBRv2/v3.
- You already build with Bazel and Abseil, or you embed through Envoy or Chromium, which provide the platform implementations and build files.
- Video or streaming delivery where rebuffering matters: the paper's randomized trials showed 15-18% lower mean rebuffer rate for QUIC users.
- You can dedicate engineering time to wiring your own event loop, batch packet writers and certificate handling around a large, fast-moving C++ codebase.

## Skip it when

- High-bandwidth, low-RTT paths (data centre, LAN, gigabit links). The paper saw little gain, and sometimes worse results than TCP, above about 100 Mbps or at a few ms RTT. An independent WWW'24 study found Chromium's QUIC stack (Chrome and the Chromium quic_client) falling behind TCP+TLS+HTTP/2 from about 500-600 Mbps, with Chrome 45.2% slower at 1 Gbps because receiver-side packet processing saturated the client CPU.
- CPU-bound servers: even after optimization Google measured QUIC serving at about 2x the CPU of TLS/TCP, and UDP packet send/receive was one of the three main costs (with crypto and connection state).
- Networks that block or throttle UDP: in Google's November 2016 data 4.4% of video clients could not use QUIC (mostly corporate firewalls), so you still need a TCP+TLS fallback path.
- You want a small, stable C library with a CMake build, releases and a stable ABI. QUICHE has no tags or releases, marks its public Bazel targets \*_unstable_api, and has no documented CMake/Make integration (issue #85 unanswered).
- Big-endian targets, WebAssembly, or Windows with MSVC: the README says little-endian only, a WASM build attempt stalled on the protobuf dependency (issue #86), and the Windows build needs clang-cl (issue #100, open).

## How it is fast

The measured gain comes from the QUIC protocol, not from faster code: a 0-RTT handshake (about 88% of desktop QUIC connections in the paper) that removes the 2-3 RTT TCP+TLS setup, streams that don't head-of-line block each other, and loss recovery built on monotonically increasing packet numbers, which removes TCP's retransmission ambiguity and gives precise RTT samples; gains grow with RTT and in the latency tail. On the I/O side the code has Linux batch writers (UDP GSO via UDP_SEGMENT with optional SO_TXTIME release times, and sendmmsg), batched reads of 16 packets per call, UDP GRO and ECN receive support, and pacing with Cubic, BBRv1/v2/v3 and Prague congestion controllers. Google's own server CPU work described in the paper (hand-optimized ChaCha20, PACKET_RX_RING receive, cache-friendlier data structures) cut QUIC's server CPU from about 3.5x to about 2x that of TLS/TCP.

## Compared with alternatives

Pick QUICHE over ngtcp2, LSQUIC, picoquic, TQUIC or quic-zig when you need Chrome's own stack (interop, MASQUE, WebTransport, MoQT) or already embed through Envoy or Chromium; those siblings are easier-to-embed C/C++/Zig libraries with measured bulk-throughput or request-rate wins over Cloudflare's Rust quiche, while QUICHE's catalogued win is protocol-level latency vs TCP+TLS with no lab throughput comparison against them.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib: Bazel cc_library quiche_core, exported as //quiche:quiche_unstable_api; no releases or tags; Chromium (GN) and Envoy (Bazel) vendor the source |
| **Dependencies** | BoringSSL, Abseil, Protocol Buffers, googleurl (gurl; the README installs libicu-dev on Linux), zlib; MODULE.bazel also pulls quic-trace and anonymous-tokens; libevent optional (QUICHE_ENABLE_LIBEVENT); googletest, fuzztest and re2 for tests |
| **Minimum toolchain** | C++20 (-std=c++20, -fno-rtti in .bazelrc), Bazel 8.2.1 (.bazelversion); README builds with clang + lld; maintainers say clang-14 is not supported (issue #141) and a GCC 13.3 build break is open (issue #155) |
| **Platforms** | Little-endian only (README). Standalone binaries are documented for Linux; .bazelrc has a macOS config; Windows socket code exists but the build needs clang-cl (issue #100). The GSO and sendmmsg batch writers are in a linux_only source list. |
| **Thread safety** | Not thread-safe: quic_connection.h says QuicConnection is not thread-safe and asynchronous callbacks must come back on the connection's thread. Each connection is driven by a single-threaded event loop (poll(2) by default, libevent optional); no multi-threaded server model is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Open-source flag defaults differ from Google's internal build: 17 of 62 feature flags in quiche_feature_flags_list.h have different internal and external values. For example quic_default_to_bbr is true internally but false in the open-source build, and gQUIC Q046 is disabled externally. The production numbers reflect Google's configuration, not the one you get.
- The bundled quic_server and quic_client are test tools, and the standalone Bazel build does not compile the fast I/O paths: quiche/BUILD.bazel never uses the linux_only (GSO and sendmmsg batch writers) or libevent source lists. QuicServer writes one packet per call with QuicDefaultPacketWriter on the poll(2) event loop, and the paper itself says the test server and client are not tuned for production performance. Benchmarking those binaries understates the library; build the batch writers with your own build files and wire QuicGsoBatchWriter into your dispatcher.
- The paper's numbers are from gQUIC version 35 with Google's QUIC-crypto handshake (December 2016 to January 2017). The repo now supports IETF QUIC v1 (RFC 9000), v2 (RFC 9369) and draft-29 with the TLS 1.3 handshake, plus gQUIC Q046, so the code version that was measured is no longer in the repo.
- Robustness reports are open on GitHub: a QPACK blocked-decoding memory DoS that Google's bug bounty team rated below its security-bug threshold (issue #105), a QUIC_BUG in HTTP/3/WebTransport server streams that a remote client can trigger (#147), a fuzzer-found null dereference in client header parsing (#103), and 33 RFC 9000 conformance reports filed in May 2026 (#108-#140), 31 of them still open. GitHub PRs are not merged directly; changes go through Google's internal review.

## Known shortcomings

- Evidence is Google's own 2016-17 measurement of gQUIC v35 (QUIC-crypto), a version no longer in the repo; no lab setup, compiler or hardware; the gain is protocol design (0-RTT, loss recovery), not faster code. The paper's own costs: server CPU \~2x TLS/TCP after optimization, little or negative gain above 100 Mbps or at a few ms RTT, 4.4% of video clients needed TCP fallback. 17 of 62 feature flags default differently outside Google (e.g. quic_default_to_bbr). The standalone Bazel build omits the GSO/sendmmsg batch writers and libevent; the bundled quic_server writes one packet per call and is 'not tuned for production'. No tags or releases, '\*_unstable_api' targets, C++20 + Bazel 8.2.1, no CMake (#85), clang-14 unsupported (#141), GCC 13.3 build break (#155), little-endian only, Windows needs clang-cl (#100). Open robustness reports: QPACK blocked-decoding DoS (#105), remotely triggerable QUIC_BUG (#147), fuzzer null deref (#103), 31 open RFC 9000 conformance reports. No head-to-head with other QUIC stacks.

## Caveats and trade-offs

The numbers are from the SIGCOMM 2017 paper 'The QUIC Transport Protocol: Design and Internet-Scale Deployment'. They were measured on Google's original gQUIC code, then in Chromium (paper Section 3.9) and the ancestor of today's IETF-QUIC QUICHE, in live randomized production trials rather than a lab benchmark. The paper is first-party: all authors are at Google. The gains come mainly from protocol design (0-RTT handshakes, loss recovery), not from implementation speed. The paper also reports costs: QUIC server CPU was about 3.5x TLS/TCP at first and about 2x after optimization (Section 6.7), and QUIC can do worse than TCP on high-bandwidth (&gt;100 Mbps) or very-low-RTT links (Section 6.8). No comparison is made against Cloudflare's Rust quiche, msquic, nghttp3 or c-ares. Google's C++ QUICHE is unrelated to Cloudflare's Rust 'quiche', despite the similar name. Standalone embedding needs platform API implementations; the README points to Chromium and Envoy for these.

UDP-based transport needs OS/kernel support (GSO/GRO) for high throughput and historically costs more CPU per byte than TCP; large dependency footprint (BoringSSL, Abseil); embedding API is designed for Google-scale integrators (Chromium/Envoy), not a drop-in small library.

## Maintenance

Actively developed by Google (last commit 2026-09-25, about 900 stars) and BSD-3-Clause, but there are no releases and the APIs are explicitly unstable, so you pin a commit and track breaking changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SIGCOMM'17 paper (Langley et al., Google) reports randomized production A/B trials of QUIC users (QUICg) against a TLS/TCP control group (TCPg); the 8.0%/3.6% mean Search Latency and 18.0%/15.3% mean Rebuffer Rate reductions appear in the Introduction and in Tables 1-2 of Section 6. No public benchmark code, compiler, flags or CPU model, so it cannot be A.
- **Verifier notes:** The PDF is live, and every claimed number matches the paper exactly. The only fix to claimed_speedup is the section reference: the paper has no 'Application Performance' section, and the figures sit in Section 6 'QUIC Performance'. The GitHub REST API was rate-limited (403), so the metadata came from other sources: license BSD-3-Clause from the raw LICENSE file and the repo page; not archived, not a fork, and 898 stars from the repo page HTML; last commit 2026-09-25 from the commits atom feed, so the repo is active.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** WWW'24 paper (arXiv 2310.09423): Chromium's QUIC stack (built on this code) trails TCP+TLS+HTTP/2 from about 500-600 Mbps; Chrome is 45.2% slower at 1 Gbps, with client CPU saturated on receive.
- **Pages the verifier opened:**
  - <https://storage.googleapis.com/gweb-research2023-media/pubtools/4102.pdf>
  - <https://github.com/google/quiche>
  - <https://github.com/google/quiche/commits/main.atom>
  - <https://raw.githubusercontent.com/google/quiche/main/LICENSE>
  - <https://raw.githubusercontent.com/google/quiche/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/google/quiche>
  - <https://github.com/google/quiche/blob/main/README.md>
  - <https://github.com/google/quiche/blob/main/CONTRIBUTING.md>
  - <https://github.com/google/quiche/blob/main/MODULE.bazel>
  - <https://github.com/google/quiche/blob/main/.bazelrc>
  - <https://github.com/google/quiche/blob/main/.bazelversion>
  - <https://github.com/google/quiche/blob/main/BUILD.bazel>
  - <https://github.com/google/quiche/blob/main/quiche/BUILD.bazel>
  - <https://github.com/google/quiche/blob/main/build/source_list.bzl>
  - <https://github.com/google/quiche/blob/main/build/BUILD.bazel>
  - <https://github.com/google/quiche/blob/main/build/source_list.json>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_versions.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_connection.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_dispatcher.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/batch_writer/quic_gso_batch_writer.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_udp_socket.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_linux_socket_utils.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_packet_reader.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_default_packet_writer.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/io/quic_default_event_loop.cc>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/quic_packet_reader.cc>
  - <https://github.com/google/quiche/blob/main/quiche/quic/core/io/quic_poll_event_loop.h>
  - <https://github.com/google/quiche/blob/main/quiche/quic/tools/quic_server.cc>
  - <https://github.com/google/quiche/blob/main/quiche/common/quiche_feature_flags_list.h>
  - <https://github.com/google/quiche/blob/main/quiche/common/platform/default/quiche_platform_impl/quiche_flags_impl.h>
  - <https://github.com/google/quiche/blob/main/quiche/common/platform/default/quiche_platform_impl/quiche_flags_impl.cc>
  - <https://github.com/google/quiche/issues/29>
  - <https://github.com/google/quiche/issues/42>
  - <https://github.com/google/quiche/issues/85>
  - <https://github.com/google/quiche/issues/86>
  - <https://github.com/google/quiche/issues/100>
  - <https://github.com/google/quiche/issues/103>
  - <https://github.com/google/quiche/issues/105>
  - <https://github.com/google/quiche/issues/124>
  - <https://github.com/google/quiche/issues/141>
  - <https://github.com/google/quiche/issues/147>
  - <https://github.com/google/quiche/issues/155>
  - <https://github.com/google/quiche/issues>
  - <https://storage.googleapis.com/gweb-research2023-media/pubtools/4102.pdf>
  - <https://export.arxiv.org/api/query?id_list=2310.09423>
  - <https://arxiv.org/pdf/2310.09423>
  - <https://hn.algolia.com/api/v1/search?query=%22google%2Fquiche%22&tags=comment&hitsPerPage=15>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/google/quiche`) · [data/wave5/enrich/raw/github_com_google_quiche.json](../../../data/wave5/enrich/raw/github_com_google_quiche.json) (enrichment confidence 0.7)

</details>
