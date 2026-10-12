# rustrtc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust WebRTC/RTP/SRTP stack with its own ICE, DTLS and SCTP; first-party data-channel loopback runs 3.3x webrtc-rs and 3.2x pion.

| | |
|---|---|
| **Beats** | webrtc-rs 0.17.1 (Rust) and pion/webrtc v3.3.6 (Go); no C or C++ stack (libwebrtc, libdatachannel, usrsctp) was compared |
| **Claimed result** | README, release 0.3.141: throughput 549.04 MB/s vs 165.98 (webrtc-rs) and 169.58 (pion), about 3.3x and 3.2x; message rate 562,214 vs 169,967 and 173,648 msg/s; data-channel open latency 0.45 ms vs 25.64 and 3.00 ms; peak RSS 21 MB vs 44 and 48 MB; CPU 739.62% vs 677.95% and 555.20% (higher for rustrtc); throughput per CPU-percent 0.74 vs 0.24 and 0.31 MB/s. |
| **Workload** | WebRTC data-channel loopback benchmark (cargo run -r --example benchmark): 10 concurrent peer-connection pairs in one process (ICE/DTLS/SCTP, each with an idle Opus audio track), each sending 1 KiB messages on one data channel for 10 s. Throughput = bytes received / whole run time including setup (MiB/s, labelled MB/s). 'Setup latency' = time from connected to data-channel open, not ICE/DTLS setup; pion's is truncated to whole ms. CPU and RSS are sampled with ps every 500 ms. rustrtc's channel is reliable unordered (DataChannelConfig default ordered=false); webrtc-rs and pion channels are reliable ordered. The pion sender throttles on a 100 KB bufferedAmount threshold, while the Rust senders yield every 32 sends. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-9700T @ 2.00GHz (8 cores), Debian 13, kernel 6.12.101+deb13-amd64 |
| **Compiler and flags** | rustc 1.97.1 (8bab26f4f 2026-07-14) with Cargo.toml [profile.release] lto="fat", codegen-units=1, strip=symbols. This applies to both rustrtc and webrtc-rs, which are built into the same example binary by cargo run -r --example benchmark. go 1.24.4 linux/amd64, default go build for the pion program. |
| **Adoption** | 110 stars, 20 forks, 352 commits; crates.io rustrtc 0.3.145 (2026-10-03), 15,220 downloads |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/restsend/rustrtc) · [benchmark](https://github.com/restsend/rustrtc) |

## Verdict

Author's single run at release 0.3.141 on an Intel i7-9700T (8 cores, Debian 13), rustc 1.97.1 with fat LTO for rustrtc and webrtc-rs 0.17.1 in one example binary, go 1.24.4 for pion v3.3.6: ten in-process loopback pairs each push 1 KiB messages for 10 s, giving 549.04 MiB/s for rustrtc against 165.98 (webrtc-rs) and 169.58 (pion). The comparison is not like-for-like: rustrtc's channel is unordered while both baselines are ordered, the stacks pace their senders differently, and the setup-latency timers start at different points, so the 3.3x figure is an upper bound for unordered bulk transfer, not a general WebRTC speedup.

## Use it when

- Rust SIP/WebRTC gateways, SFUs or voice-agent backends (the author's rustpbx and active-call) that need ICE, DTLS-SRTP, RTP and data channels in one dependency without OpenSSL or libwebrtc.
- Many concurrent peer connections in one process where memory matters: 21 MB peak RSS for ten loopback pairs against 44 MB for webrtc-rs and 48 MB for pion in the author's run.
- Bulk data-channel transfer where message order does not matter, which is exactly the default rustrtc channel and the case the benchmark measures.
- Mixed telephony deployments that also need plain RTP latching, RTP rewrite bridging, UPnP port mapping or T.38 fax alongside WebRTC.

## Skip it when

- C or C++ applications: there is no C ABI; libwebrtc or libdatachannel are the native options, and neither was compared.
- Expecting the 3.3x on ordered channels: every quoted throughput number compares rustrtc's unordered channel with ordered channels in webrtc-rs 0.17.1 and pion v3.3.6, so no like-for-like ordered result exists; ordered receive also caps pending out-of-order messages per stream at 128 (MAX_INBOUND_STREAM_PENDING).
- Deployments that need an audited TLS stack: DTLS handshake and record layer are written in-house (src/transports/dtls), and the ClientHello also offers TLS_RSA_WITH_AES_128_GCM_SHA256, a suite without forward secrecy, after the two ECDHE suites.
- CPU-bound hosts: in the same run rustrtc used 739.62% CPU against 555.20% for pion, so the gain is in throughput per CPU-percent (0.74 against 0.31 MB/s), not lower absolute CPU.
- Code that needs a frozen API: 0.3.x has had 145 patch releases since 2025-11-27 and still ships protocol-behaviour fixes (two ICE restart/nomination issues, #54 and #55, open on 2026-10-04).

## How it is fast

It replaces webrtc-rs's layered crates with in-tree implementations: an SCTP association (src/transports/sctp.rs) that drains up to 1000 queued chunks per transmit pass under one lock, delivers the next in-order TSN straight to the channel without touching the reassembly queue, sends SACKs with SACK_DELAY = 0 and computes the CRC-32C checksum with SSE4.2 or the aarch64 CRC instructions; a homegrown DTLS 1.2 record layer using RustCrypto AES-128-GCM; Bytes buffers and parking_lot locks; and fat LTO with one codegen unit in the release profile. Part of the published gap comes from the benchmark configuration rather than the stack: rustrtc's default data channel is reliable unordered (DataChannelConfig derives Default, so ordered = false and DATA chunks carry the U flag), while both baselines run ordered reliable channels.

## Compared with alternatives

The only transport sibling is uvgRTP, a C++ RTP library for high-rate media without ICE, DTLS or data channels; pick rustrtc when a Rust service needs a full WebRTC peer (ICE, DTLS-SRTP, SCTP data channels) and pick uvgRTP for raw RTP streaming from C++. The codec siblings (opus-rs from the same author, dav1d, the Opus ports) solve a different problem and pair with it rather than compete.

## Integration

| | |
|---|---|
| **Form** | crate (rustrtc on crates.io, 0.3.145) |
| **Dependencies** | tokio (multi-thread runtime), RustCrypto aes/aes-gcm/ctr/hmac/sha1/sha2/md-5/p256, rcgen (ring) and x509-parser for certificates, bytes, parking_lot, socket2, crc32fast/crc32c, igd (UPnP), serde/serde_json, tracing, rand, base64, local-ip-address |
| **Minimum toolchain** | Rust edition 2024 with let-chains in src (Rust 1.88 or later); no rust-version is declared; the README run used rustc 1.97.1 |
| **Platforms** | Any tokio target; hardware CRC-32C on x86-64 (SSE4.2) and aarch64 (CRC extension), software fallback elsewhere. The benchmark ran only on Linux x86-64. |
| **Thread safety** | PeerConnection and DataChannel are shared through Arc and used from multiple tokio tasks (the benchmark spawns sender and receiver tasks per pair); sends on one channel serialise on a per-channel async lock. A tokio runtime is required. |
| **Drop-in for the baseline** | no |

## Gotchas

- create_data_channel(label, None) gives a reliable unordered channel, unlike the W3C, webrtc-rs and pion default of ordered; pass a DataChannelConfig with ordered = true if the application relies on order.
- Data-channel events go into an unbounded tokio mpsc queue, so a slow consumer grows memory instead of exerting SCTP backpressure. On the send side, send_data waits once flight plus queued bytes exceed sctp_max_buffered_amount (256 KB by default).
- The benchmark's 'Setup Latency' is not comparable across stacks: the rustrtc arm starts its timer only after both peers report Connected and then reads a DataChannelEvent::Open that may already sit in that queue, while the webrtc-rs and pion arms start after pc1 alone is Connected and wait for an on_open callback; pion's figure is also truncated to whole milliseconds.
- The harness's send-side pacing differs per stack: rustrtc's send_data has the built-in 256 KB limit, the pion sender blocks above a 100 KB bufferedAmount threshold, and the webrtc-rs sender has no explicit gate. CPU is the process-lifetime ps %cpu value, sampled every 500 ms in Rust and every 2000 ms in Go, from one run per stack.

## Known shortcomings

- Rust (language-filter mismatch) and off-category: WebRTC data channels are networking, not audio or video coding. Downgraded A to C: no C baseline at all (webrtc-rs 0.17.1 in Rust and pion v3.3.6 in Go; no libwebrtc, libdatachannel or usrsctp), and not like-for-like: rustrtc's channel ran unordered (DataChannelConfig Default, ordered=false) while both baselines ran ordered, and pion alone was throttled at 100 KB bufferedAmount. Metrics were throughput, message rate, data-channel open latency, CPU and RSS over 10 loopback pairs.
- Moved to networking-and-servers (websocket-grpc-rpc): a WebRTC data-channel stack, not a codec. The comparison is not like-for-like: unordered against ordered delivery is confirmed (create_data_channel None maps to unwrap_or_default, U flag 0x04); the setup-latency timer is asymmetric (rustrtc starts after both peers are Connected and may read an already-queued Open event from an unbounded mpsc, while the baselines start after pc1 only); send pacing differs (rustrtc built-in 256 KB limit, pion 100 KB threshold, webrtc-rs none); CPU comes from ps lifetime %cpu with 500 ms versus 2000 ms sampling, one run each. Homegrown DTLS whose ClientHello also offers TLS_RSA_WITH_AES_128_GCM_SHA256 (no forward secrecy); unbounded inbound event queue.

## Caveats and trade-offs

This is networking, not audio or video coding. The benchmark measures WebRTC data channels (SCTP over DTLS over UDP loopback), with no RTP media, codec or SRTP work in the timed path. The baselines are a Rust stack (webrtc-rs) and a Go stack (pion v3.3.6, an old major version), not C or C++; libwebrtc, libdatachannel and usrsctp were not compared. The configurations differ. rustrtc's channel is reliable unordered (DataChannelConfig derives Default, so ordered=false), while webrtc-rs and pion default to ordered reliable channels. Only pion's sender waits on a 100 KB bufferedAmount threshold. Pion's latency is integer milliseconds. The 'setup latency' figure is data-channel open time after connection, not full connection setup. These are the author's own numbers from one run on one 2019 low-power desktop CPU (i7-9700T), taken at release 0.3.141 while HEAD is 0.3.145. Throughput is MiB/s labelled MB/s, and rustrtc uses more CPU in absolute terms.

Pure Rust WebRTC, RTP/SRTP, T.38 fax and UPnP stack, no C API; claims interoperability with Chrome and pion. Uses more CPU than pion in the same run.

## Maintenance

Very active (352 commits, 0.3.145 published 2026-10-03, issues closed within days) and MIT-licensed, so it is easy to adopt in Rust, but its speed evidence is first-party, it is networking rather than audio or video coding, and its security-critical DTLS is homegrown.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README benchmark (release 0.3.141) carries every quoted number, and it formally has the A fields: public harness (examples/benchmark.rs, examples/go_bench/benchmark.go), rustc 1.97.1 and go 1.24.4, Cargo.toml release profile (fat LTO, codegen-units=1), and an i7-9700T. But the harness does not run the same work on each stack. rustrtc's channel comes from DataChannelConfig's derived Default (ordered=false, so DCEP type 0x80 reliable-unordered). webrtc-rs 0.17.1 and pion v3.3.6 default to ordered reliable channels, and only the pion sender is gated by a 100 KB bufferedAmount threshold. A first-party, mismatched comparison is C.
- **Verifier notes:** No C baseline at all: the comparison is against webrtc-rs and pion only. WebRTC data channels are networking, not audio/video coding, so the category should move to a networking/transport category (orchestrator's call). The headline 3.3x compares rustrtc's unordered channel with ordered channels in both baselines (verified in src/transports/datachannel.rs at HEAD, webrtc-rs v0.17.1 peer_connection/mod.rs and pion v3.3.6 peerconnection.go), so the comparison is not like-for-like.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/restsend/rustrtc>
  - <https://github.com/restsend/rustrtc/commits>
  - <https://github.com/restsend/rustrtc/tree/main/src>
  - <https://github.com/restsend/rustrtc/tree/main/examples/go_bench>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/README.md>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/benchmark.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/go_bench/benchmark.go>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/go_bench/go.mod>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/peer_connection.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/transports/sctp.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/transports/datachannel.rs>
  - <https://raw.githubusercontent.com/webrtc-rs/webrtc/v0.17.1/webrtc/src/peer_connection/mod.rs>
  - <https://raw.githubusercontent.com/pion/webrtc/v3.3.6/peerconnection.go>
  - <https://crates.io/api/v1/crates/rustrtc>
- **Sources the enricher read:**
  - <https://github.com/restsend/rustrtc>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/README.md>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/peer_connection.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/transports/datachannel.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/transports/sctp.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/src/transports/dtls/mod.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/benchmark.rs>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/go_bench/benchmark.go>
  - <https://raw.githubusercontent.com/restsend/rustrtc/HEAD/examples/go_bench/go.mod>
  - <https://github.com/restsend/rustrtc/tree/main/src/transports>
  - <https://github.com/restsend/rustrtc/tree/main/src/transports/dtls>
  - <https://github.com/restsend/rustrtc/issues?q=is%3Aissue>
  - <https://github.com/restsend/rustrtc/issues/1>
  - <https://crates.io/api/v1/crates/rustrtc>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/restsend/rustrtc`) · [data/wave10/enrich/raw/github_com_restsend_rustrtc.json](../../../data/wave10/enrich/raw/github_com_restsend_rustrtc.json) (enrichment confidence 0.75)

</details>
