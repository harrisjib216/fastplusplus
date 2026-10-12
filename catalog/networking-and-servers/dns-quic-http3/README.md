# DNS, QUIC and HTTP/3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** c-ares, quiche, msquic, nghttp3  
**18 entries:** 0 tier A · 8 tier B · 10 tier C · 0 tier D · 17 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**KCP**](skywind3000-kcp.md) | Two-file C reliable-UDP ARQ library. It spends extra bandwidth to get much lower tail latency than ENet or TCP under packet loss. | **B** | C | MIT | 🟢 active |
| 2 | [**LSQUIC (LiteSpeed QUIC)**](litespeedtech-lsquic.md) | LiteSpeed's C QUIC + HTTP/3 client/server library; LSQUIC-to-LSQUIC bulk downloads beat quiche-to-quiche 1.2-1.5x at 10 Gbit/s. | **B** | C | MIT | 🟢 active |
| 3 | [**QUICHE (Google)**](google-quiche.md) | Google's C++ QUIC/HTTP/3 stack behind Chrome; production A/B trials cut Search latency 8% (desktop) vs TLS/TCP. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 4 | [**simdzone**](nlnetlabs-simdzone.md) | SIMD DNS zone-file (presentation format) parser in C; about 4x Knot DNS's zscanner on the .se zone. | **B** | C | BSD-3-Clause | 🟢 active |
| 5 | [**LSQUIC-DPDK (tumi8 kernel-bypass fork)**](tumi8-lsquic-dpdk.md) | LSQUIC 4.2 fork with a zero-copy DPDK datapath; 1.3x kernel MsQuic (GSO+GRO) goodput on single-connection bulk downloads. | **B** | C | MIT | 🟢 active |
| 6 | [**Nail (NailDNS demo server)**](jbangert-nail.md) | 295-line C authoritative DNS demo built on the Nail parser generator; \~2.9x BIND 9.9.5 qps in a 2014 loopback test. | **B** | C | MIT | 🔴 abandoned |
| 7 | [**picoquic-DPDK (Tyunyayev kernel-bypass fork)**](ipnetworkinglab-picoquic-dpdk.md) | Research fork of picoquic that swaps kernel UDP sockets for DPDK; about 3x picoquic single-connection goodput on 100 GbE. | **B** | C | MIT | 🔴 abandoned |
| 8 | [**quiche-DPDK (tumi8 kernel-bypass fork)**](tumi8-quiche-dpdk.md) | DPDK kernel-bypass client/server built on unmodified quiche; 1.83x the single-connection goodput of kernel-socket quiche on 100G NICs. | **B** | C | no license (study only) | 🟢 active |
| 9 | [**Hickory DNS (formerly Trust-DNS)**](hickory-dns-hickory-dns.md) | Memory-safe Rust DNS server, resolver and protocol crates; matches BIND 9.11 on single-query UDP latency, within noise. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 10 | [**Unbound**](nlnetlabs-unbound.md) | NLnet Labs' validating, recursive, caching DNS resolver in C; the developer's 2008 changelog puts cache-hit throughput at \~3.4x BIND's. | **C** | C | BSD-3-Clause | 🟢 active |
| 11 | [**dnspython**](rthalley-dnspython.md) | Pure-Python DNS toolkit; gevent's wrapper for it beat gevent's c-ares resolver on the maintainer's macOS, but lost on Linux. | **C** | Python | ISC | 🟢 active |
| 12 | [**mvfst**](facebookincubator-mvfst.md) | Meta's C++ IETF QUIC transport (client+server) under Proxygen HTTP/3; cut Facebook-app tail latency 20% vs HTTP/2-over-TCP. | **C** | C++ | MIT | 🟢 active |
| 13 | [**ngtcp2**](ngtcp2-ngtcp2.md) | Pure-C IETF QUIC transport library (RFC 9000); in one loopback harness, 1.5-2.1x quiche's bulk-transfer throughput. | **C** | C | MIT | 🟢 active |
| 14 | [**TQUIC**](tencent-tquic.md) | Tencent's Rust QUIC/HTTP3 library with C API: \~2.4x quiche on request and stream-churn rate, slower on bulk. | **C** | Rust | Apache-2.0 | 🟢 active |
| 15 | [**picoquic**](private-octopus-picoquic.md) | Minimal C QUIC/HTTP3 research stack; beats quiche by \~6-7% on bulk upload and connection setup in one loopback harness. | **C** | C | MIT | 🟢 active |
| 16 | [**Bundy-DNS (l1cache experimental branch)**](bundy-dns-bundy.md) | Bundy's unpublished l1cache experiment: pre-rendered wire-format DNS answer cache, claimed 180K vs 41K qps over BIND 9.9.2. | **C** | C++ | ISC | 🟢 active |
| 17 | [**ls-qpack**](litespeedtech-ls-qpack.md) | LiteSpeed's C QPACK (RFC 9204) codec. On one 2019 trace, its history-gated indexing out-compressed nghttp3 1.3-2.2x. | **C** | C | MIT | 🟢 active |
| 18 | [**quic-zig**](endel-quic-zig.md) | Pure-Zig QUIC/HTTP/3/WebTransport stack; \~3% faster than quiche on handshake rate in one harness, slower almost everywhere else. | **C** | Zig | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
