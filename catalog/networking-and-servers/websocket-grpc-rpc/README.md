# WebSocket, gRPC and RPC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** gRPC, uWebSockets, Thrift  
**25 entries:** 5 tier A · 2 tier B · 18 tier C · 0 tier D · 23 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**rpcx**](smallnest-rpcx.md) | Go RPC framework with its own binary TCP protocol and built-in service governance; 2.3-2.6x grpc-go throughput in author's benchmark. | **A** | Go | Apache-2.0 | 🟢 active |
| 2 | [**Kitex**](cloudwego-kitex.md) | ByteDance's Go RPC framework whose gRPC-compatible transport, built on the Netpoll event loop, out-serves grpc-go on small unary RPCs. | **A** | Go | Apache-2.0 | 🟢 active |
| 3 | [**wtx (gRPC server)**](c410-f3r-wtx.md) | Rust crate with its own HTTP/2 and gRPC stack. Its unary gRPC server served 3.7-5.5x grpc-go's req/s on HttpArena. | **A** | Rust | MPL-2.0 | 🟢 active |
| 4 | [**ActualLab.Rpc (part of ActualLab.Fusion)**](actuallab-fusion.md) | .NET RPC library (Fusion's transport) that multiplexes calls over one WebSocket; vendor loopback benchmark shows 5-8x grpc-dotnet call throughput. | **A** | C# | MIT | 🟢 active |
| 5 | [**cmd-stream (with MUS codec)**](cmd-stream-cmd-stream-go.md) | Go client/server framework sending typed Command objects over raw TCP/TLS; author benchmark shows 3.1-4.6x grpc-go echo QPS. | **A** | Go | MIT | 🟢 active |
| 6 | [**Homa (HomaModule) — Linux kernel implementation of the Homa…**](platformlab-homamodule.md) | Linux kernel module for Homa, a message-based datacenter RPC transport with far lower short-message tail latency than TCP. | **B** | C | BSD-2-Clause OR GPL-2.0+… | 🟢 active |
| 7 | [**eRPC**](erpc-io-erpc.md) | Kernel-bypass C++ datacenter RPC library over DPDK UDP or InfiniBand, near FaSST/RDMA speed on lossy Ethernet. | **B** | C++ | Apache-2.0 | 🟡 stale |
| 8 | [**brpc**](apache-brpc.md) | Baidu's C++ RPC framework built on bthread M:N scheduling; its 2016 benchmark shows 6-24x gRPC 0.11's QPS. | **C** | C++ | Apache-2.0 | 🟢 active |
| 9 | [**libwebsockets**](warmcat-libwebsockets.md) | Pure C client/server library for WebSockets, HTTP/1-2-3 and MQTT; in a 2016 competitor table it used \~5.7x less memory per connection than WebSocket++. | **C** | C | MIT | 🟢 active |
| 10 | [**Volo (CloudWeGo Rust RPC framework)**](cloudwego-volo.md) | CloudWeGo's Rust Thrift/gRPC framework. Self-reports 350k QPS on a 4-core 1KB Thrift echo, about 1.5x Kitex's published pingpong number. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 11 | [**iceoryx (iceperf)**](eclipse-iceoryx-iceoryx.md) | Zero-copy shared-memory publish/subscribe IPC for C++ and C; sub-microsecond same-host latency versus POSIX message queues and Unix sockets. | **C** | C++ | Apache-2.0 | 🟢 active |
| 12 | [**SRPC (Sogou C++ Workflow RPC)**](sogou-srpc.md) | C++ RPC framework on Sogou Workflow speaking SRPC, Thrift-framed and bRPC wire protocols; \~1.6-2.8x Apache Thrift server QPS. | **C** | C++ | Apache-2.0 | 🟢 active |
| 13 | [**rest_rpc**](qicosmos-rest-rpc.md) | Header-only C++20 coroutine RPC over raw TCP; its 2019 C++11 version beat brpc 1.2-1.9x on same-machine echo. | **C** | C++ | MIT | 🟢 active |
| 14 | [**DRPC**](storj-drpc.md) | Storj's small Go replacement for grpc-go, using its own framed protocol instead of HTTP/2; not wire-compatible with gRPC. | **C** | Go | MIT | 🟢 active |
| 15 | [**sockudo-ws**](sockudo-sockudo-ws.md) | Rust WebSocket library (Tokio/Compio; HTTP/1.1, /2, /3) that self-reports 2-3% higher echo throughput than uWebSockets. | **C** | Rust | MIT | 🟢 active |
| 16 | [**Machnet**](microsoft-machnet.md) | DPDK kernel-bypass messaging sidecar for cloud VMs; 2.6x lower median and 7.4x lower p99.9 RTT than Linux TCP. | **C** | C++ | MIT | 🟢 active |
| 17 | [**nexus-async-rt / nexus-async-web**](abso1ut3zer0-nexus.md) | Sans-IO, zero-copy async WebSocket/REST library for Tokio; receives small TLS frames 2-3x faster than tokio-tungstenite. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 18 | [**grpcxx**](uatuko-grpcxx.md) | Small C++20 unary-only gRPC server on nghttp2 and libuv; author's hello-world h2load runs show \~2.3-3x gRPC C++ throughput. | **C** | C++ | MIT | 🟢 active |
| 19 | [**rustrtc**](restsend-rustrtc.md) | Pure-Rust WebRTC/RTP/SRTP stack with its own ICE, DTLS and SCTP; first-party data-channel loopback runs 3.3x webrtc-rs and 3.2x pion. | **C** | Rust | MIT | 🟢 active |
| 20 | [**Lightstream**](spacecell-lightstream.md) | Rust/Python Arrow-table transport over raw TCP, QUIC, HTTP/2 and WebSocket; 1.06-1.71x Arrow Flight throughput between AWS hosts. | **C** | Rust | MPL-2.0 | 🟢 active |
| 21 | [**fRPC (frpc-go)**](loopholelabs-frpc-go.md) | Go proto3 RPC generator that swaps gRPC's HTTP/2 and Protobuf for 8-byte-header TCP framing and Polyglot encoding. | **C** | Go | Apache-2.0 | 🟡 stale |
| 22 | [**rpclib**](rpclib-rpclib.md) | Small C++11/14 msgpack-rpc client and server with no IDL; its author's 2017 benchmark has small calls 2.5x faster than gRPC 1.1.0. | **C** | C++ | MIT | 🔴 abandoned |
| 23 | [**Exposed (reflectionless RPC for Go)**](thesyncim-exposed.md) | Go RPC library over one batched TCP connection, derived from valyala/fastrpc; README shows \~1.1-3x gRPC echo throughput. | **C** | Go | MIT | 🔴 abandoned |
| 24 | [**Courierust**](blueokanna-courierust.md) | Zero-dependency Rust HTTP/WebSocket stack; its WebSocket codec encodes small masked frames \~2.5x faster than tungstenite. | **C** | Rust | PolyForm-Perimeter-1.0.1 (study only) | 🟢 active |
| 25 | [**grpc_homa (Homa transport plugin for gRPC)**](platformlab-grpc-homa.md) | gRPC C++ transport plugin that replaces HTTP/2-over-TCP with the Homa kernel RPC protocol; reports \~40% lower short-RPC round-trip time. | **C** | C++ | no license (study only) | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
