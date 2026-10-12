# Networking and servers

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

HTTP parsers and servers, event loops, TLS, QUIC and RPC stacks measured against nginx, libuv, OpenSSL, gRPC and friends.

**181 entries in 6 categories:** 27 tier A · 45 tier B · 104 tier C · 5 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [DNS, QUIC and HTTP/3](dns-quic-http3/README.md) | 18 | 0 | 8 | 10 | 0 | c-ares, quiche, msquic, nghttp3 |
| [Event loops and async I/O](event-loops-io/README.md) | 44 | 8 | 8 | 27 | 1 | libuv, libevent, epoll, io_uring baseline the benchmark names |
| [HTTP parsers](http-parsers/README.md) | 25 | 5 | 1 | 18 | 1 | llhttp, http-parser, picohttpparser |
| [HTTP servers and frameworks](http-servers-frameworks/README.md) | 53 | 6 | 22 | 22 | 3 | nginx, Go net/http, Boost.Beast, actix-web, uvloop |
| [TLS](tls/README.md) | 16 | 3 | 4 | 9 | 0 | OpenSSL, BoringSSL, rustls |
| [WebSocket, gRPC and RPC](websocket-grpc-rpc/README.md) | 25 | 5 | 2 | 18 | 0 | gRPC, uWebSockets, Thrift |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**gnet**](event-loops-io/panjf2000-gnet.md) | Pure-Go epoll/kqueue multi-reactor TCP/UDP framework; 1.4-1.95x Go net's packet rate on streaming 1KB echo. | [Event loops and async I/O](event-loops-io/README.md) | **A** | Go | Apache-2.0 | 🟢 active |
| 2 | [**rpcx**](websocket-grpc-rpc/smallnest-rpcx.md) | Go RPC framework with its own binary TCP protocol and built-in service governance; 2.3-2.6x grpc-go throughput in author's benchmark. | [WebSocket, gRPC and RPC](websocket-grpc-rpc/README.md) | **A** | Go | Apache-2.0 | 🟢 active |
| 3 | [**Kitex**](websocket-grpc-rpc/cloudwego-kitex.md) | ByteDance's Go RPC framework whose gRPC-compatible transport, built on the Netpoll event loop, out-serves grpc-go on small unary RPCs. | [WebSocket, gRPC and RPC](websocket-grpc-rpc/README.md) | **A** | Go | Apache-2.0 | 🟢 active |
| 4 | [**rustls**](tls/rustls-rustls.md) | Memory-safe Rust TLS 1.2/1.3 library on AWS-LC crypto; beats OpenSSL 3.6.1 per core on handshakes, resumption and AES-GCM bulk. | [TLS](tls/README.md) | **A** | Rust | Apache-2.0 OR MIT OR ISC | 🟢 active |
| 5 | [**Granian**](http-servers-frameworks/emmett-framework-granian.md) | Rust (hyper + tokio) HTTP server for Python ASGI/WSGI/RSGI apps, with higher single-worker throughput than Uvicorn and Gunicorn. | [HTTP servers and frameworks](http-servers-frameworks/README.md) | **A** | Rust | BSD-3-Clause | 🟢 active |
| 6 | [**monoio**](event-loops-io/bytedance-monoio.md) | Thread-per-core Rust async runtime on io_uring (epoll/kqueue fallback); \~1.9x Tokio's peak echo QPS on 4 cores. | [Event loops and async I/O](event-loops-io/README.md) | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 7 | [**Lithium (HTTP server / web framework)**](http-servers-frameworks/matt-42-lithium.md) | Header-only C++ HTTP server and async SQL toolkit on fibers; beat actix-web on TechEmpower DB tests only in Round 20. | [HTTP servers and frameworks](http-servers-frameworks/README.md) | **A** | C++ | MIT | 🟢 active |
| 8 | [**Ultimate Express**](http-servers-frameworks/dimdengd-ultimate-express.md) | Express 4 API re-implemented on uWebSockets.js; README shows 3-12x Express req/s, but Node 24 narrows most gaps. | [HTTP servers and frameworks](http-servers-frameworks/README.md) | **A** | JavaScript | Apache-2.0 | 🟢 active |
| 9 | [**Cutelyst**](http-servers-frameworks/cutelyst-cutelyst.md) | Qt 6 web framework with its own epoll HTTP/1.1, HTTP/2 and FastCGI server; edges Drogon on HttpArena, trails nginx and actix-web. | [HTTP servers and frameworks](http-servers-frameworks/README.md) | **A** | C++ | BSD-3-Clause | 🟢 active |
| 10 | [**uv-cpp**](event-loops-io/wlgq2-uv-cpp.md) | C++11 callback wrapper over libuv with TCP/UDP/HTTP; ties Boost.Asio 1.67 on loopback echo, trails nginx on HTTP. | [Event loops and async I/O](event-loops-io/README.md) | **A** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
