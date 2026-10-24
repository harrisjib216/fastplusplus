# Event loops and async I/O

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** libuv, libevent, epoll, io_uring baseline the benchmark names  
**47 entries:** 8 tier A · 8 tier B · 30 tier C · 1 tier D · 42 copyable, 5 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**gnet**](panjf2000-gnet.md) | Pure-Go epoll/kqueue multi-reactor TCP/UDP framework; 1.4-1.95x Go net's packet rate on streaming 1KB echo. | **A** | Go | Apache-2.0 | 🟢 active |
| 2 | [**monoio**](bytedance-monoio.md) | Thread-per-core Rust async runtime on io_uring (epoll/kqueue fallback); \~1.9x Tokio's peak echo QPS on 4 cores. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**uv-cpp**](wlgq2-uv-cpp.md) | C++11 callback wrapper over libuv with TCP/UDP/HTTP; ties Boost.Asio 1.67 on loopback echo, trails nginx on HTTP. | **A** | C++ | MIT | 🟢 active |
| 4 | [**aquatic (aquatic_udp)**](greatest-ape-aquatic.md) | Rust open UDP BitTorrent tracker (BEP 15) whose io_uring backend out-serves its own epoll path and opentracker. | **A** | Rust | Apache-2.0 | 🟢 active |
| 5 | [**rsloop**](rustedbytes-rsloop.md) | Rust/PyO3 asyncio event loop on io_uring, IOCP or kqueue; beats uvloop on TLS, bulk and TCP round-trips, not plaintext WebSockets. | **A** | Rust | Apache-2.0 | 🟢 active |
| 6 | [**Condy**](condy-cpp-condy.md) | Header-only C++20 coroutine runtime over io_uring: \~1.22x epoll TCP recv throughput, matches raw liburing, cheaper coroutines than Asio. | **A** | C++ | MIT | 🟢 active |
| 7 | [**uring_exec**](caturra000-uring-exec.md) | Header-only liburing adapter for stdexec (std::execution) senders; beats Asio's io_uring backend on loopback TCP ping-pong. | **A** | C++ | MPL-2.0 | 🟢 active |
| 8 | [**evpp**](qihoo360-evpp.md) | Qihoo 360's muduo-style C++11 TCP/UDP/HTTP library on top of libevent. In its own echo test it beats libevent 2.0's bufferevent sample by 1.1-2.4x. | **A** | C++ | BSD-3-Clause | 🔴 abandoned |
| 9 | [**Demikernel**](microsoft-demikernel.md) | Rust kernel-bypass library OS with a zero-copy, queue-based socket API over DPDK; 4-5x lower echo RTT than Linux sockets. | **B** | Rust | MIT | 🟢 active |
| 10 | [**Caladan**](shenango-caladan.md) | Interference-aware core scheduler and kernel-bypass runtime; memcached 99.9% latency 52 us vs 580 ms under Parties\* during GC. | **B** | C | Apache-2.0 | 🟢 active |
| 11 | [**mTCP**](mtcp-stack-mtcp.md) | User-level, per-core TCP stack over DPDK/PSIO/netmap with an epoll-like API; beats Linux kernel sockets+epoll on short connections. | **B** | C | BSD-3-Clause | 🔴 abandoned |
| 12 | [**wepoll**](piscisaureus-wepoll.md) | Linux epoll API for Windows sockets on the AFD driver; flat 1.4 us select cost where select() grows linearly. | **B** | C | BSD-2-Clause | 🔴 abandoned |
| 13 | [**Arrakis**](paper-arrakis.md) | Research OS (Barrelfish fork) giving apps direct SR-IOV NIC and storage queues; beat tuned Linux 3.8 I/O by 1.7-9x. | **B** | C | MIT | 🔴 abandoned |
| 14 | [**Shenango**](shenango-shenango.md) | Kernel-bypass runtime reallocating cores every 5 us; ZygOS-level tail latency, 6.3x Linux DNS throughput, idle cores freed for batch jobs. | **B** | C | Apache-2.0 | 🔴 abandoned |
| 15 | [**FlexTOE**](tcp-acceleration-service-flextoe.md) | Netronome Agilio SmartNIC TCP offload engine running the established-connection data path on-NIC; beats Linux, TAS and Chelsio TOE. | **B** | C | BSD-3-Clause | 🔴 abandoned |
| 16 | [**IX (protected dataplane OS)**](paper-ix-protected-dataplane-os.md) | Protected dataplane OS that runs TCP/IP and one app on dedicated polling cores; 2.8-3.6x memcached throughput over Linux+epoll. | **B** | C | MIT (study only) | 🔴 abandoned |
| 17 | [**uvloop**](magicstack-uvloop.md) | Cython/libuv replacement for CPython's default asyncio event loop; 2-4x echo throughput in its own 2016 benchmark. | **C** | Python | Apache-2.0 OR MIT | 🟢 active |
| 18 | [**Seastar**](scylladb-seastar.md) | Shard-per-core C++ futures framework with optional DPDK userspace TCP; its memcached beat libevent-based stock memcached 2-4x (2015). | **C** | C++ | Apache-2.0 | 🟢 active |
| 19 | [**libhv**](ithewei-libhv.md) | Cross-platform C event-loop library with built-in HTTP/WebSocket/MQTT; \~1.4-1.6x libevent/libuv echo throughput, ties libev/asio. | **C** | C | BSD-3-Clause | 🟢 active |
| 20 | [**Asio io_uring backend (ASIO_HAS_IO_URING)**](chriskohlhoff-asio.md) | Opt-in io_uring backend inside Asio/Boost.Asio that replaces the epoll reactor on Linux 5.10+ without API changes. | **C** | C++ | BSL-1.0 | 🟢 active |
| 21 | [**Apache Iggy (thread-per-core io_uring backend, v0.7.0)**](apache-iggy.md) | Rust message-streaming server whose v0.7.0 rewrite on thread-per-core io_uring (compio) cuts tail latency versus its Tokio/epoll build. | **C** | Rust | Apache-2.0 | 🟢 active |
| 22 | [**PcapPlusPlus**](seladb-pcapplusplus.md) | C++ packet capture, parsing and crafting library; parses pcap TCP/DNS traffic 1.06-1.26x faster than libtins in its maintainers' run. | **C** | C++ | Unlicense | 🟢 active |
| 23 | [**may**](xudong-huang-may.md) | Rust stackful-coroutine runtime with Go-style go! and blocking-style I/O; its may_minihttp demo beat pre-1.0 tokio_minihttp by \~15% req/s. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 24 | [**PhotonLibOS**](alibaba-photonlibos.md) | Alibaba's stackful-coroutine C++ I/O runtime (epoll/io_uring/kqueue); its echo server beats boost::asio on single-core QPS. | **C** | C++ | Apache-2.0 | 🟢 active |
| 25 | [**OpenOnload (with ef_vi and TCPDirect kernel-bypass APIs)**](xilinx-cns-onload.md) | AMD's user-level TCP/UDP stack that accelerates unmodified BSD-sockets apps by bypassing the Linux kernel network stack. | **C** | C | GPL-2.0 AND BSD-2-Clause | 🟢 active |
| 26 | [**JUring**](davidtos-juring.md) | Java FFM bindings to Linux io_uring (via liburing) for batched file reads/writes; beats FileChannel on small random reads. | **C** | Java | Unlicense | 🟢 active |
| 27 | [**COROIO**](resetius-coroio.md) | C++23 coroutine networking library with compile-time epoll/kqueue/IOCP/io_uring backends; lower dispatch latency than libevent at small descriptor counts. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 28 | [**Boost.Corosio**](cppalliance-corosio.md) | Coroutine-only C++20 Boost-track networking library; 9-49% faster coroutine dispatch than Asio coroutines on Windows IOCP, socket I/O at parity. | **C** | C++ | BSL-1.0 | 🟢 active |
| 29 | [**redcon.c**](tidwall-redcon-c.md) | Small C framework for Redis-protocol (RESP) servers on epoll/kqueue; its toy clone outruns Redis 6.0.6 under deep pipelining. | **C** | C | MIT | 🟢 active |
| 30 | [**Rain**](wzxzhuxi-rain.md) | Small header-only C++23 coroutine runtime for Linux: per-thread epoll loops with SO_REUSEPORT, \~1.13x Tokio req/s on one loopback test. | **C** | C++ | MIT | 🟢 active |
| 31 | [**see (see::sync)**](compio-rs-see.md) | Runtime-agnostic watch (latest-value broadcast) channel with sync and single-threaded variants; beats tokio::sync::watch at 1, 4 and 64 subscribers. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 32 | [**ringline**](ringline-rs-ringline.md) | Thread-per-core io_uring runtime for Rust servers: 4-71% faster than default tokio on TCP echo, -10% to +9% versus tuned tokio. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 33 | [**uringcore**](ankitkpandey1-uringcore.md) | Rust/PyO3 io_uring asyncio event loop; claims \~3x lower single-op latency than uvloop, but loses on gather(100). | **C** | Rust | Apache-2.0 | 🟢 active |
| 34 | [**BusterMQ**](bpd1069-bustermq.md) | Zig thread-per-core io_uring server for the core NATS pub/sub protocol; \~1.4x Go nats-server publish rate in its own benchmark. | **C** | Zig | Apache-2.0 | 🟢 active |
| 35 | [**UCall (formerly ujrpc)**](unum-cloud-ucall.md) | JSON-RPC 2.0 server library in C++ with C and Python APIs; io_uring backend beats FastAPI/uvicorn on small-call latency and throughput. | **C** | C++ | Apache-2.0 | 🟡 stale |
| 36 | [**io_uring-echo-server (frevib)**](frevib-io-uring-echo-server.md) | Single-threaded \~200-line C TCP echo server on liburing, benchmarked in 2020 against the same author's minimal epoll echo server. | **C** | C | MIT | 🟡 stale |
| 37 | [**liburing4cpp**](carterli-liburing4cpp.md) | Header-only C++20 coroutine wrapper over liburing; its echo server roughly matches the author's raw C io_uring server. | **C** | C++ | MIT | 🟡 stale |
| 38 | [**mrloop**](markreedz-mrloop.md) | Tiny single-threaded C event loop on io_uring; README echo test shows 1.51x an unnamed epoll server. | **C** | C | MIT | 🟡 stale |
| 39 | [**Hinsightd MT (hin10)**](gitlab-com-tiotags-hin10.md) | Tiny multi-threaded io_uring HTTP/1.1 static-file server in C; edges nginx 1-16% on a 102-byte file, loses on larger files. | **C** | C | BSD-3-Clause | 🟡 stale |
| 40 | [**libev**](enki-libev.md) | Small, embeddable C event loop with io, timer, signal, child and stat watchers; halves libevent 1.4's per-iteration cost when timers churn. | **C** | C | BSD-2-Clause OR… | 🔴 abandoned |
| 41 | [**libPhenom**](facebook-libphenom.md) | Archived Facebook C eventing framework (epoll/kqueue/ports job scheduler); first-party gut check shows 1.07-1.39x libevent events/s. | **C** | C | Apache-2.0 | 🔴 abandoned |
| 42 | [**picoev**](kazuho-picoev.md) | Tiny C event loop (\~1k lines; epoll/kqueue/select) that beat 2009-era libevent \~2x on libev's bench.c. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 43 | [**uWebSockets (µWebSockets / uSockets)**](unetworking-uwebsockets.md) | C++ HTTP/WebSocket server on the uSockets event layer; author measured 12x the req/s of clustered Node.js/Fastify. | **C** | C++ | Apache-2.0 (study only) | 🟢 active |
| 44 | [**F-Stack**](f-stack-f-stack.md) | DPDK kernel-bypass framework with a ported FreeBSD TCP/IP stack and epoll/kqueue-style API; beats kernel-stack epoll Nginx on RPS/CPS. | **C** | C | BSD-2-Clause for F-Stack's… (study only) | 🟢 active |
| 45 | [**exec-rs**](npuichigo-exec-rs.md) | Rust port of C++ P2300 senders/receivers with a mio event loop; its single-threaded echo server beats Tokio 10-26% (self-reported). | **C** | Rust | no license (study only) | 🟢 active |
| 46 | [**io_uring hybrid storage I/O architecture (Oracle Database)**](paper-io-uring-hybrid-storage-i-o-architecture-oracle-database.md) | Design paper: Oracle Database swaps libaio for io_uring on batched async paths; 29% less CPU per write, sync reads unchanged. | **C** | C | no license (study only) | 🟢 active |
| 47 | [**LibTorrent (rakshasa)**](rakshasa-libtorrent.md) | C++ BitTorrent engine behind rTorrent that writes mmap'ed file pages straight to sockets; old first-party claim of 3x the mainline client's seeding speed. | **D** | C++ | GPL-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
