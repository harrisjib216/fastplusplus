# libhv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Cross-platform C event-loop library with built-in HTTP/WebSocket/MQTT; \~1.4-1.6x libevent/libuv echo throughput, ties libev/asio.

| | |
|---|---|
| **Beats** | libevent, libuv |
| **Claimed result** | README pingpong run (4 threads, 1000 connections, 10s, 1024-byte messages): libhv 215 MB/s vs libevent 157 MB/s (\~1.37x) and libuv 156 MB/s (\~1.38x); it also beats poco (165) and asio (132) and trails libev (210). Ratios derived from page data. Three GitHub Actions runs on 2026-09-25 (benchmark.yml, 2 threads, 100 connections) are consistent: libhv 115/207/120 MB/s vs libevent 79/149/81 (\~1.39-1.48x) and libuv 77/125/73 (\~1.49-1.66x). In those runs libhv is at parity with libev (118/212/119) and asio (118/211/115), so the README's win over asio is not reproduced. |
| **Workload** | pingpong echo-servers benchmark (echo-servers/benchmark.sh + pingpong_client): a single-event-loop TCP echo server per library, loaded over loopback by the libhv-based pingpong_client with 4 threads, 1000 connections, 1024-byte messages for 10s, measuring aggregate read throughput (MB/s). The CI version uses 2 threads and 100 connections. |
| **Metric** | throughput |
| **Hardware** | Not stated for the README run. The current CI runs use GitHub-hosted ubuntu-latest (ubuntu-24.04) runners; the CPU model is not logged. |
| **Compiler and flags** | Makefile target echo-servers compiles each echo server and pingpong_client with -g -Wall -O3 (-std=c99 or c++11). libhv itself is built with the default BUILD_TYPE=RELEASE (-O2, -DNDEBUG). libevent, libev, libuv, asio and poco are distro packages (apt/yum/brew via echo-servers/build.sh). No compiler or library versions are given for the README run. The current CI run uses gcc 13.3.0 on ubuntu-24.04 with libevent 2.1.12, libev 4.33 and libuv 1.48.0. |
| **Adoption** | 7,555 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/ithewei/libhv) · [benchmark](https://github.com/ithewei/libhv/blob/master/README.md) |

## Verdict

Setup: single-loop TCP echo servers on loopback, all written by the libhv author, driven by a libhv-based pingpong client sending 1 KB messages for 10 s. The README run (2021, 4 threads, 1000 connections, compiler and CPU not stated) measured libhv 215 MB/s vs libevent 157 and libuv 156 (\~1.37x), with libev at 210. The 2026-09-25 GitHub Actions run I opened (ubuntu-24.04, gcc 13.3.0, distro libevent 2.1.12, libuv 1.48.0, libev 4.33, asio 1.28.1; 2 threads, 100 connections; CPU not logged) measured libhv 115 vs libevent 79 and libuv 77 (\~1.46-1.49x), with libev and asio both at 118.

## Use it when

- C or C++11 services that need one BSD-3 library for the event loop plus TCP/UDP, timers and HTTP/WebSocket/MQTT/Redis clients or servers, instead of stitching libuv or libevent to separate protocol libraries.
- Many-connection request/response or proxy traffic with small messages (about 1 KB) where your current libuv/libevent code allocates per read or per write.
- Code that must build on Linux, Windows, macOS, Android and iOS from one source tree (all five are built in CI) and cross-compile for ARM or MinGW.
- C++ servers that want muduo-style one-loop-per-thread scaling through TcpServer::setThreadNum or EventLoopThreadPool with little code.

## Skip it when

- Existing libev or asio TCP code: in current CI libhv (115 MB/s) is level with libev and asio (both 118 MB/s), so porting buys no throughput.
- You need to keep libevent or libuv call sites: there is no compatibility layer (issue #354 asked for one; only a partial sketch exists in comments), so every call site must be ported.
- You want completion-based io_uring I/O: the io_uring backend (added 2026-03, off by default, needs liburing) only submits IORING_OP_POLL_ADD readiness polls and is not in any tagged release yet.
- Untrusted input through the HTTP or DNS modules without your own review: three medium 2023 CVEs (CVE-2023-26146/26147/26148: XSS, response splitting, CRLF injection) are recorded for the HTTP layer, and an open report (#851, 2026-07) shows an ASan-confirmed heap overflow in protocol/dns.c (the WITH_PROTOCOL module, off by default).
- Code that often starts, stops and destroys C++ TcpClient/UdpClient objects on a shared EventLoop from other threads: open issue #704 reports crashes on destruction and after repeated Stop/Start. Detailed docs are mostly Chinese (docs/cn).

## How it is fast

All connections on one loop share a single 8 KB per-loop read buffer, and hio_write calls send() directly, copying only the unsent remainder into a per-connection queue on EAGAIN; a steady-state echo therefore does no heap allocation per message. The benchmark's libuv server instead mallocs a read buffer and a write request per echo, and its libevent server allocates an evbuffer per read. The libev server uses a static buffer plus direct send(), which is why libev ties libhv. Supporting pieces: an fd-indexed io array, min-heap timers, and priority-ordered pending callbacks over epoll, kqueue, event ports, wepoll or select.

## Compared with alternatives

Pick libhv over uWebSockets when you need a general C event loop with TCP/UDP, timers and HTTP/WebSocket/MQTT/Redis clients on five platforms, not just a fast HTTP/WebSocket server. Pick it over PhotonLibOS (a C++ coroutine library whose catalogued win over asio is \~1.05x) when you want a plain C callback API; for io_uring-first designs, monoio (Rust) and the frevib echo server go further than libhv's poll-only io_uring backend.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (both built by default via Makefile/configure, CMake or Bazel; also in vcpkg and xrepo) |
| **Dependencies** | none for the core; optional OpenSSL, GnuTLS or mbedTLS (TLS), nghttp2 (HTTP/2), liburing (io_uring backend), curl (deprecated), Lua, QuickJS, protobuf (hrpc) |
| **Minimum toolchain** | C99 and C++11 (C++ layer optional via --without-evpp); GCC 4.8+ or MSVC 2015+; CMake 3.6+ |
| **Platforms** | Linux (epoll, optional io_uring), Windows (wepoll over IOCP by default, else WSAPoll), macOS/BSD (kqueue), Solaris (event ports), Android, iOS; select fallback elsewhere |
| **Thread safety** | One loop per thread. hio_write and hio_close are thread-safe (per-connection recursive mutex), and hloop_post_event is the thread-safe way to hand work to a loop. Other hio/timer calls are meant for the loop thread; the C++ layer offers runInLoop and isInLoopThread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The buffer passed to the read callback is the loop's shared read buffer. It is overwritten by the next read on any connection of that loop, so copy the data before storing or deferring it, or give the connection its own buffer with hio_set_readbuf.
- Unsent data is copied into a per-connection write queue. Past 16 MB (max_write_bufsize default) hio_write closes the connection with ERR_OVER_LIMIT, so large senders need flow control through the write callback or hio_write_is_complete.
- The hloop_post_event queue has no size limit (issue #818); the maintainer says to add your own cap if producers can outrun the loop.
- hloop_new defaults to HLOOP_FLAG_AUTO_FREE, and the header forbids calling hloop_free on such a loop. For C++ TcpClient/UdpClient on an external loop, the maintainer advises heap allocation and deletion inside loop-&gt;runInLoop.

## Known shortcomings

- README numbers are a manual 2021 run; current CI shows libhv about 1.4-1.7x faster than libevent and libuv but tied with libev and asio. The baseline echo servers and the load client (built on libhv) were written by the libhv author.
- The lead comes from the harness: libhv shares one read buffer and sends directly, while the author's libuv and libevent echo servers allocate per message; the libev server, written the same way, ties libhv. The io_uring backend (2026-03, off by default) only uses poll readiness and is not in a release. Three 2023 HTTP-layer CVEs (XSS, response splitting, CRLF injection) list no patched version; open ASan heap overflow in the optional DNS module (#851). Docs mostly in Chinese.

## Caveats and trade-offs

All echo servers and the pingpong client were written by the libhv author, and the client is itself built on libhv. The baselines are simple implementations: the libuv server mallocs a buffer per read plus a write request per echo, and the libevent server allocates an evbuffer per read. The README numbers come from a 2021-03-09 run whose 4-thread/1000-connection setting was pingpong_client's default at the time; they cannot be traced to a CI run, and today's CI uses 2 threads and 100 connections. Compiler and library versions and the CPU are not stated for the README run. CI numbers swing \~1.8x between runners, though the ordering holds. The margin over libevent and libuv is modest (\~1.4-1.6x), and libhv ties libev and (in current CI) asio.

Simpler, richer-protocol API than libevent/libuv/asio (built-in HTTP/WebSocket/MQTT/Redis); C core with C++ wrapper (evpp namespace, unrelated to Qihoo360/evpp)

## Maintenance

Actively maintained (last commit 2026-09-25) under BSD-3-Clause, but the last tagged release is v1.3.4 (2025-10-25), so the io_uring backend and Redis client exist only on master; the library itself is easy to build and vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark section has pingpong echo-server output (4 threads, 1000 connections, 10s) with libevent 157, libev 210, libuv 156, libhv 215, asio 132 and poco 165 MB/s, matching the claim. The harness is public (echo-servers/build.sh, benchmark.sh, pingpong_client.cpp and the per-library \*_echo.c/cpp; Makefile target echo-servers builds them with -O3). The README run (added 2021-03-09) states no compiler, library versions or CPU, so it is first-party C. Current GitHub Actions runs (ubuntu-24.04, gcc 13.3.0, runner CPU not logged) use a different config (2 threads, 100 connections) but show the same ordering against libevent and libuv.
- **Verifier notes:** The numbers match the README exactly and the tier stays C. The record's claim that the README numbers came from GitHub Actions is not supported: the README run used 4 threads and 1000 connections, while benchmark.sh (and so CI) has defaulted to 2 threads and 100 connections since 2021-11. The three latest CI logs still show libhv \~1.4-1.7x over libevent and libuv but tied with libev and asio. The metadata checks out (BSD-3-Clause, 7,555 stars, not a fork or archived, last commit 2026-09-25, active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ithewei/libhv/blob/master/README.md>
  - <https://github.com/ithewei/libhv>
  - <https://github.com/ithewei/libhv/blob/69aa5617f680122decdc592b22400a486f2827c7/README.md>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/build.sh>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/benchmark.sh>
  - <https://github.com/ithewei/libhv/blob/bfc1bfb/echo-servers/benchmark.sh>
  - <https://github.com/ithewei/libhv/blob/bbe9c5b/echo-servers/benchmark.sh>
  - <https://github.com/ithewei/libhv/blob/072526a/echo-servers/benchmark.sh>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/pingpong_client.cpp>
  - <https://github.com/ithewei/libhv/blob/bfc1bfb/echo-servers/pingpong_client.cpp>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libhv_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libuv_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libevent_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/Makefile>
  - <https://github.com/ithewei/libhv/blob/master/Makefile.in>
  - <https://github.com/ithewei/libhv/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/ithewei/libhv/actions/runs/36168301435>
  - <https://github.com/ithewei/libhv/actions/runs/36163525348>
  - <https://github.com/ithewei/libhv/actions/runs/36162606409>
- **Sources the enricher read:**
  - <https://github.com/ithewei/libhv>
  - <https://github.com/ithewei/libhv/blob/master/README.md>
  - <https://github.com/ithewei/libhv/blob/master/BUILD.md>
  - <https://github.com/ithewei/libhv/blob/master/config.ini>
  - <https://github.com/ithewei/libhv/blob/master/hconfig.h.in>
  - <https://github.com/ithewei/libhv/blob/master/CMakeLists.txt>
  - <https://github.com/ithewei/libhv/blob/master/Makefile.vars>
  - <https://github.com/ithewei/libhv/blob/master/base/hplatform.h>
  - <https://github.com/ithewei/libhv/blob/master/docs/PLAN.md>
  - <https://github.com/ithewei/libhv/blob/master/docs/cn/hloop.md>
  - <https://github.com/ithewei/libhv/blob/master/docs/cn/EventLoop.md>
  - <https://github.com/ithewei/libhv/blob/master/docs/cn/TcpServer.md>
  - <https://github.com/ithewei/libhv/blob/master/docs/cn/Channel.md>
  - <https://github.com/ithewei/libhv/blob/master/event/README.md>
  - <https://github.com/ithewei/libhv/blob/master/event/iowatcher.h>
  - <https://github.com/ithewei/libhv/blob/master/event/hloop.h>
  - <https://github.com/ithewei/libhv/blob/master/event/hloop.c>
  - <https://github.com/ithewei/libhv/blob/master/event/hevent.h>
  - <https://github.com/ithewei/libhv/blob/master/event/hevent.c>
  - <https://github.com/ithewei/libhv/blob/master/event/nio.c>
  - <https://github.com/ithewei/libhv/blob/master/event/epoll.c>
  - <https://github.com/ithewei/libhv/blob/master/event/io_uring.c>
  - <https://github.com/ithewei/libhv/blob/master/event/hdns.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libhv_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libuv_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libevent_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/libev_echo.c>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/asio_echo.cpp>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/pingpong_client.cpp>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/build.sh>
  - <https://github.com/ithewei/libhv/blob/master/echo-servers/benchmark.sh>
  - <https://github.com/ithewei/libhv/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/ithewei/libhv/blob/master/.github/workflows/CI.yml>
  - <https://github.com/ithewei/libhv/actions/runs/36168301435>
  - <https://github.com/ithewei/libhv/actions/runs/36168301435/job/108181352532>
  - <https://github.com/ithewei/libhv/commits/master>
  - <https://github.com/ithewei/libhv/commits/master/event/io_uring.c>
  - <https://github.com/ithewei/libhv/releases>
  - <https://github.com/ithewei/libhv/security/advisories>
  - <https://github.com/ithewei/libhv/issues?q=label%3Abug>
  - <https://github.com/ithewei/libhv/issues?q=is%3Aopen>
  - <https://github.com/ithewei/libhv/issues/851>
  - <https://github.com/ithewei/libhv/issues/637>
  - <https://github.com/ithewei/libhv/issues/473>
  - <https://github.com/ithewei/libhv/issues/442>
  - <https://github.com/ithewei/libhv/issues/704>
  - <https://github.com/ithewei/libhv/issues/818>
  - <https://github.com/ithewei/libhv/issues/764>
  - <https://github.com/ithewei/libhv/issues/354>
  - <https://api.github.com/advisories?cve_id=CVE-2023-26146>
  - <https://api.github.com/advisories?cve_id=CVE-2023-26147>
  - <https://api.github.com/advisories?cve_id=CVE-2023-26148>
  - <https://github.com/alibaba/PhotonLibOS>
  - <https://github.com/uNetworking/uWebSockets>
  - <https://github.com/monoio-rs/monoio>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ithewei/libhv`) · [data/wave5/enrich/raw/github_com_ithewei_libhv.json](../../../data/wave5/enrich/raw/github_com_ithewei_libhv.json) (enrichment confidence 0.85)

</details>
