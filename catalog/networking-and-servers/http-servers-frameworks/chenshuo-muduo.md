# Muduo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Linux one-loop-per-thread C++ TCP reactor library; author's ping-pong test puts it about 18% above libevent2's bufferevents.

| | |
|---|---|
| **Beats** | libevent 2.x (libevent2) ping-pong echo server and client |
| **Claimed result** | Author's blog post 'muduo vs libevent2 throughput' concludes muduo throughput is on average more than 18% higher than libevent2 (as quoted by the evpp benchmark page: 'muduo throughput averages more than 18% higher than libevent2'). |
| **Workload** | Ping-pong echo throughput benchmark (client and server both echo, as in the Boost.Asio LinuxPerformanceImprovements method) between muduo and libevent2 over loopback, varying message size and number of connections. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the 18% claim (author's blog, not opened). The test code is public: chenshuo/recipes pingpong/libevent (Makefile CFLAGS -g -Wall -O2, single_thread.sh pins server and client with taskset) and chenshuo/muduo examples/pingpong (muduo built release via BUILD_TYPE=release ./build.sh). |
| **Adoption** | 16.3k stars |
| **Last commit** | 2025-02-28 |
| **Links** | [repository](https://github.com/chenshuo/muduo) · [benchmark](https://github.com/Qihoo360/evpp/blob/master/docs/benchmark_throughput_vs_muduo_cn.md) |

## Verdict

The muduo author's 2010 CSDN post (not reachable here; quoted by Qihoo360's evpp docs) reports muduo ping-pong echo throughput on loopback averaging more than 18% above libevent 2.0.x across message sizes and connection counts; hardware, compiler and per-row numbers are not verifiable. The public harness builds the libevent test programs with -g -Wall -O2 against an installed libevent, while muduo's current CMake release build uses -O2 -march=native. Evpp's separate run (Xeon E5-2630 v2, gcc 4.8.2) shows muduo-v1.0.9 roughly equal to evpp-v0.2.4, which is itself 17% to 130% faster than libevent-2.0.21's samples, so the 18% is indirectly plausible but never measured by a third party.

## Use it when

- Custom binary or line-based TCP protocol servers on Linux (RPC, gateways, game or chat servers) where you want a small, readable reactor rather than a full web framework.
- Throughput-bound echo/relay/proxy workloads with message sizes of a few KiB and up, where the larger reads beat libevent bufferevents' 4 KiB-per-read path.
- Multi-core servers that fit the one-loop-per-thread model: set TcpServer::setThreadNum(N) and keep per-connection state in the owning loop.
- Teaching or vendoring: BSD-3-Clause, small C++11 codebase, documented in the author's book on Linux multithreaded server programming.

## Skip it when

- HTTP services: the bundled HttpServer parses request line and headers only; the kExpectBody branch in HttpContext.cc is an empty FIXME, so request bodies (POST) and chunked encoding are not handled. Use Drogon or Sogou Workflow for HTTP.
- Windows, macOS or BSD targets: Linux-only (epoll, timerfd, eventfd; kernel &gt;= 2.6.28).
- Projects that need TLS, HTTP/2, coroutines or async DNS out of the box: none are in the core library (c-ares, curl, hiredis and protobuf appear only in examples/contrib).
- Long-term-supported dependencies: last code change 2022-11-01, 41 open issues and 45 open PRs, no tagged GitHub releases; open bugs include timer callbacks still running after cancel (#668) and a stack overflow in TimeZone::loadZoneFile on a crafted zone file (#728).

## How it is fast

Reads go through Buffer::readFd, a single readv into the buffer's free space plus a 64 KiB stack buffer, so one syscall drains up to about 128 KiB without an ioctl(FIONREAD); libevent 2.0.21 and 2.1.12 evbuffer_read issue FIONREAD and cap every read at EVBUFFER_MAX_READ = 4096 bytes. Sends try a direct write() when the output buffer is empty and only queue the remainder; each connection is pinned to one I/O thread, so the hot path takes no locks. Built with -O2 -march=native by default.

## Compared with alternatives

Pick muduo over Drogon, Sogou Workflow or cinatra when you are writing a raw TCP protocol server, not an HTTP API, and want a small Linux reactor you can read end to end; for HTTP serving those siblings are complete frameworks with published HTTP benchmarks, while muduo's HttpServer has no request-body support.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake or Bazel; libmuduo_base and libmuduo_net, optional muduo_http) |
| **Dependencies** | Boost headers (boost::any only); pthreads; examples optionally use protobuf, zlib, c-ares, curl, hiredis, thrift, gd, tcmalloc |
| **Minimum toolchain** | C++11, GCC &gt;= 4.7 or Clang &gt;= 3.5, CMake &gt;= 2.6 |
| **Platforms** | Linux only (kernel &gt;= 2.6.28), any architecture GCC targets; default flags include -march=native |
| **Thread safety** | One EventLoop per thread; EventLoop::runInLoop/queueInLoop/quit and TcpConnection::send are safe from other threads (cross-thread send copies the data); TcpConnection::shutdown, TcpServer setters and HttpServer::setHttpCallback are documented as not thread safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note on the 18% claim: each side is measured with its own client and server (chenshuo/recipes pingpong/libevent vs muduo examples/pingpong, the scripts default to 16 KiB blocks, server and client pinned to separate cores with taskset). The libevent side runs on bufferevents, whose evbuffer_read caps each read at 4096 bytes after an ioctl(FIONREAD) (libevent 2.0.21 buffer.c, unchanged in 2.1.12), so a 16 KiB message costs libevent at least four read callbacks per hop versus one readv for muduo. The gap measures that default buffer path, not the epoll loop; evpp's docs say evpp beats libevent2 for the same reason (it uses libevent's event loop but its own muduo-style Buffer instead of evbuffer).
- CMakeLists.txt compiles with -Werror plus -Wconversion, -Wold-style-cast and -Wshadow, and with -march=native; new compilers can stop the build on fresh warnings, and binaries are not portable across CPUs unless you remove -march=native. build.sh defaults to an out-of-tree ../build directory.
- TcpConnection::send(Buffer\*) is commented 'this one will swap data' but copies: in-loop it writes or appends from the buffer and then retrieveAll(); from another thread it copies into a std::string first.
- Buffer::readFd uses a 64 KiB stack array on every read callback, so I/O threads need a normal-size stack; Buffer is backed by std::vector&lt;char&gt; and never shrinks unless you call shrink().

## Known shortcomings

- Tier C: the 18% over libevent2 claim is the author's 2010 CSDN post 5864889 (blocked), quoted verbatim on the evpp page; evpp's own numbers give only indirect support (muduo about equal to evpp, evpp 17-130% over libevent-2.0.21); echo throughput, not HTTP; test code public in chenshuo/recipes/pingpong; stale (last code commit 2022-11-01).
- Enricher: each side ran its own client and server with default 16 KiB blocks, and libevent bufferevents cap every read at EVBUFFER_MAX_READ=4096 after an ioctl(FIONREAD) (2.0.21 and 2.1.12), so a libevent message costs at least 4 read callbacks against 1 readv into muduo's 64 KiB extrabuf; the 18% measures that default buffer path, not the event loop (evpp's docs give the same reason). libevent test programs built -O2 against muduo's -O2 -march=native; bundled HttpServer has no request-body support; open bugs #668 (timer runs after cancel) and #728 (TimeZone stack overflow); last code change 2022-11-01.

## Caveats and trade-offs

The 18% figure comes from the author's 2010 CSDN blog post 'muduo与libevent2吞吐量对比' (blog.csdn.net/solstice/article/details/5864889, not opened) and is seen only as quoted by the evpp project's benchmark page ('muduo吞吐量平均比libevent2高 18% 以上'), so hardware, compiler and per-row numbers for muduo vs libevent2 are not verified; tier C, first-party. Benchmark code for both sides is public (chenshuo/recipes pingpong/libevent with Makefile CFLAGS -g -Wall -O2; muduo examples/pingpong built with BUILD_TYPE=release ./build.sh), but the build flags of the published run are unknown, and the libevent2 in the 2010 post is a 2.0.x release. Indirect third-party support only: Qihoo360's evpp docs, on one machine (Xeon E5-2630 v2, CentOS 6.2, gcc 4.8.2, public ping-pong code), show muduo-v1.0.9 roughly equal to evpp-v0.2.4 (each wins some rows) and, in a separate report, evpp 17% to 130% faster than libevent-2.0.21's own server.c/client.c; muduo vs libevent2 was never measured directly there. muduo is a general reactor-style TCP network library (with only an example HTTP server), so the comparison is an event-loop/echo throughput test, not an HTTP framework benchmark. Last commit 2025-02-28 is an issue-template update; the last code change is 2022-11-01. [retier] Default-buffer-path comparison (libevent 4 KiB read cap vs muduo 64 KiB readv); libevent tests built -O2, muduo -O2 -march=native; last code change 2022-11-01; open #668, #728.

Linux-only (epoll, kernel &gt;= 2.6.28), reactor-per-thread design, requires Boost only for boost::any. One-loop-per-thread model with its own Buffer class based on std::vector&lt;char&gt;.

## Maintenance

Stale: the last code commit is 2022-11-01 (the 2025-02-28 commit is an issue-template update) and there are no tagged GitHub releases, but it is BSD-3-Clause, widely forked (16.3k stars, 5.3k forks) and small enough to vendor; the issue #720 reporter built it with gcc 13.3 once the distro Boost replaced a self-built one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The 18% figure is the muduo author's own 2010 blog conclusion (blog.csdn.net/solstice/article/details/5864889, not opened), quoted verbatim by the evpp page; the evpp page itself measures muduo against evpp, not libevent2, so muduo vs libevent2 rests on first-party numbers without verifiable methodology.
- **Verifier notes:** 18% claim matches the evpp page's quotation of the author's blog (blog URL 5864889 is correct; 5848547 is the muduo intro post). Shortcomings: first-party only, original post unreachable, 2010-era libevent 2.0.x baseline, echo throughput rather than HTTP, evpp's third-party data only transitively supports muduo over libevent2. Metadata checked: BSD-3-Clause (License file), 16.3k stars, not a fork, stale (last commit 2025-02-28; last code commit 2022-11-01).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 5); enricher w5 pair-028
- **Pages the verifier opened:**
  - <https://github.com/Qihoo360/evpp/blob/master/docs/benchmark_throughput_vs_muduo_cn.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_muduo_cn.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_libevent.md>
  - <https://github.com/chenshuo/muduo>
  - <https://github.com/chenshuo/muduo/commits>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/License>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/libevent/Makefile>
- **Sources the enricher read:**
  - <https://github.com/chenshuo/muduo>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/README>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/build.sh>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/Buffer.h>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/Buffer.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/EventLoop.h>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/TcpServer.h>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/TcpConnection.h>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/TcpConnection.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/EventLoopThreadPool.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/poller/EPollPoller.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/http/HttpServer.h>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/muduo/net/http/HttpContext.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/examples/pingpong/server.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/examples/pingpong/client.cc>
  - <https://raw.githubusercontent.com/chenshuo/muduo/HEAD/examples/pingpong/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/libevent/Makefile>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/libevent/server.c>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/libevent/client.c>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/libevent/single_thread.sh>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/muduo/single_thread.sh>
  - <https://raw.githubusercontent.com/chenshuo/recipes/HEAD/pingpong/asio/single_thread.sh>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/bufferevent_sock.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.1.12-stable/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.1.12-stable/bufferevent_sock.c>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_muduo_cn.md>
  - <https://github.com/chenshuo/muduo/issues?q=is%3Aissue+bug>
  - <https://github.com/chenshuo/muduo/issues/720>
  - <https://github.com/chenshuo/muduo/issues/668>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/chenshuo/muduo`) · [data/wave5/enrich/raw/github_com_chenshuo_muduo.json](../../../data/wave5/enrich/raw/github_com_chenshuo_muduo.json) (enrichment confidence 0.6)

</details>
