# uv-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++11 callback wrapper over libuv with TCP/UDP/HTTP; ties Boost.Asio 1.67 on loopback echo, trails nginx on HTTP.

| | |
|---|---|
| **Beats** | Boost.Asio 1.67 (TCP ping-pong echo); nginx 1.14.2 (HTTP, Apache bench, chart images only) |
| **Claimed result** | README tables, kbyte/s received by the echo server (uv-cpp vs boost.asio 1.67), one client: 1K 16138 vs 16119 (+0.1%, derived from page data), 2K 32071 vs 31566 (+1.6%, derived), 4K 59264 vs 58322 (+1.6%, derived), 8K 123813 vs 126210 (-1.9%, derived: Asio faster). 4K packets with N clients: 10 654282 vs 633818 (+3.2%, derived), 100 591869 vs 585716 (+1.1%, derived), 1000 401500 vs 371386 (+8.1%, derived), 5000 412855 vs 382402 (+8.0%, derived). Apache bench HTTP screenshots (1000 concurrency, 100000 requests; images in wlgq2/uv_cpp_res/vs_nginx): uv-cpp 15408.06 req/s (6.490 s, 0 failed, 56-byte /hello.html) vs nginx 1.14.2 16945.71 req/s (5.901 s, 512 failed requests, 13-byte /hello.html), so uv-cpp is about 9% slower than nginx (derived from page data). |
| **Workload** | Loopback TCP ping-pong echo between a client and a server process on one machine, throughput as kbyte/s received by the server (one-second timer printout), at 1K/2K/4K/8K bytes per packet with one client and with 10/100/1000/5000 clients at 4K bytes; uv-cpp (libuv 1.30.0 wrapper) echo_server/echo_client against a Boost.Asio 1.67 echo server/client written in the same style. A second comparison runs Apache bench (1000 concurrency, 100000 requests, /hello.html) against uv-cpp's HTTP server and nginx 1.14.2. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5 8265U (second table also lists 4G memory); loopback on one machine |
| **Compiler and flags** | gcc 8.3.0, '-O2', libuv 1.30.0, Boost.Asio 1.67 (README environment line: Intel Core i5 8265U + debian8 + gcc8.3.0 + libuv1.30.0 + '-O2') |
| **Adoption** | 839 stars, 213 forks |
| **Last commit** | 2025-11-13 |
| **Links** | [repository](https://github.com/wlgq2/uv-cpp) · [benchmark](https://github.com/wlgq2/uv-cpp) |

## Verdict

The repo's echo_server/echo_client pair was run against an equivalent Boost.Asio 1.67 pair on one Intel Core i5-8265U laptop over loopback (Debian 8, gcc 8.3.0 -O2, libuv 1.30.0), with one one-second kbyte/s printout per cell. With one client, uv-cpp was within -1.9% to +1.6% of Asio across 1-8 KB messages; with 10-5000 clients at 4 KB it was 1.1% to 8.1% ahead. A separate ab run (1000 concurrency, 100,000 requests) has its HTTP server at 15,408 req/s against nginx 1.14.2's 16,946, about 9% slower (derived from page data).

## Use it when

- You already depend on libuv (or want its Linux epoll and Windows IOCP backends) but want C++11 lambdas and classes instead of raw uv_\* handles and C callbacks.
- Single-threaded TCP services with small-to-medium messages where a small, readable, MIT-licensed code base you can vendor matters more than peak throughput; heartbeat timeouts come built in via TimerWheel.
- Internal tools that need a minimal HTTP/1.x endpoint with radix-tree routing (prefix wildcards, path values, query parameters) and no dependency beyond libuv, such as health checks or control endpoints.
- Framed binary protocols that fit the bundled Packet/PacketBuffer format (head byte, end byte, payload up to 65,535 bytes).

## Skip it when

- You expect it to beat Asio: the published echo numbers are a tie (-1.9% to +8.1% versus Boost.Asio 1.67, single runs), and its HTTP server is about 9% slower than nginx 1.14.2 in the README's own ab screenshots.
- Multi-core servers: an EventLoop is single-threaded and TcpServer has no multi-reactor or SO_REUSEPORT mode, so scaling means wiring your own loops per thread; libhv's 4-thread pingpong reports about 1.38x over plain libuv.
- Production HTTP: the server closes the connection after every response (no keep-alive), has no TLS, sends nothing for unmatched routes or parse errors, caps requests at the 32 KB CycleBuffer by default, and has no static-file serving (issue #48 open).
- Writers whose buffers do not outlive the call, or peers that read slowly: write() never copies and the connection keeps reading while writes queue, so there is no backpressure.
- You need macOS/BSD support, coroutines or io_uring: the README lists Linux and Windows only and the API is callbacks only; for io_uring see uring_exec, Condy or Asio's io_uring backend.

## How it is fast

There is no new I/O technique; it is libuv's epoll (Linux) or IOCP (Windows) reactor with a thin layer on top. Each connection reuses one std::string read buffer sized to libuv's 64 KB read suggestion, and write() hands the caller's pointer straight to uv_write without copying; libuv 1.30 attempts the write() syscall immediately when the write queue is empty, so an echo is one read callback plus one synchronous write. TCP_NODELAY is on by default for accepted and client sockets. Per message it still pays a shared_from_this refcount, two std::function hops and a heap-allocated WriteReq per write.

## Compared with alternatives

Pick uv-cpp over libhv or evpp only if you specifically want libuv underneath a thin C++11 callback layer that is small enough to vendor and read in an afternoon. libhv reports about 1.37-1.38x over libevent and libuv in a 4-thread pingpong, and on Linux uring_exec (1.27-3.46x over Asio's io_uring backend) or PhotonLibOS are better-measured choices for throughput.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | libuv (libuv 1.30.0 headers plus prebuilt static libraries for gcc 8.3.0 and Windows SDK 10.0.10240 are checked into libuv1.30.0/, and CMakeLists.txt links that prebuilt libuv.a), pthread |
| **Minimum toolchain** | C++11 (CMakeLists.txt sets -std=c++11 -O2), CMake 2.8+; README build targets are VS2017, Code::Blocks and CMake on Linux; VS2015 build errors were reported (#23) |
| **Platforms** | Linux and Windows (README); Signal is Linux-only (#ifdef __linux__); macOS not documented |
| **Thread safety** | One EventLoop per thread. TcpServer, CycleBuffer and ListBuffer are marked not thread-safe in the source, and write() must run on the loop thread (cross-thread write() crashed in #41); only writeInLoop and EventLoop::runInThisLoop are safe from other threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- write() never copies, while libuv requires the buffer to stay valid until the write callback. The library's own code ignores that: HttpServer writes each response from a local std::string, HttpClient writes the request from a local string (still so after the 2023 'fix http send' commit), the echo client writes from a stack array, and the README echo server writes straight from the connection's reused read buffer while reading continues. It works on Linux only because libuv writes immediately when the queue is empty; once a send buffer fills or a payload is large, the queued write reads freed or overwritten memory.
- HTTP server: it needs HttpServer::SetBufferMode(CycleBuffer or ListBuffer) or it logs an error and serves nothing. The CycleBuffer is a fixed 32 KB ring whose append() failure is ignored, so a larger request is silently dropped and never answered. ListBuffer is a std::list&lt;uint8_t&gt;, one heap node per byte. Every response closes the connection.
- writeInLoop() on a connection that has already gone calls the AfterWriteCallback without a null check, so passing nullptr there throws std::bad_function_call inside the loop. Heap corruption on client reconnect (#43, CentOS 7, uv-cpp 1.5.4) was never answered. Packet lengths are uint16_t (#30). With setTimeout() enabled, every received message inserts a shared_ptr into a std::set in the TimerWheel.
- Harness flaws behind the README numbers (the numbers are not invalidated; with one message in flight per connection the zero-copy echo is safe): uv-cpp's sockets get TCP_NODELAY by default but the Boost.Asio harness never sets no_delay; the Asio side std::copies each read into a second 32 KB buffer and uses async_write_some, ignoring short writes; and each cell is one one-second printout. The one-client cells work out to about 14.6k-16.1k round trips per second for both libraries at every packet size (derived from page data), so they measure loopback wake-up latency, not library overhead.

## Known shortcomings

- Public harness (examples echo_server/echo_client vs boost_asio_echo_server/client; gcc 8.3.0 -O2, libuv 1.30.0, Boost.Asio 1.67, i5-8265U) but no clear win: +0.1% to +8% over Asio and -1.9% at 8K, one 1-second sample per number with no repeats, packet size and client count hard-coded; uv-cpp echoes from its read buffer without a copy while the Asio sample copies into a write buffer and uses async_write_some. The nginx screenshots show uv-cpp about 9% slower (15,408 vs 16,946 req/s, different documents, 512 failed nginx requests). Numbers from about April 2020; last code change 2023-12-23.
- Enricher: write() never copies while libuv needs the buffer alive until the callback, and the library's own HttpServer response, HttpClient request, echo_client stack array and README echo all write from short-lived or reused buffers (safe only through libuv's immediate write; use-after-free once the send buffer fills; echo numbers not invalidated since one message is in flight). TCP_NODELAY is on by default only on the uv-cpp side, the Asio side copies into a second buffer and ignores short writes, and one-client cells run about 14.6k-16.1k round trips/s for both libraries at every size, so the test is latency-bound. HTTP closes after every response, a 32 KB CycleBuffer silently drops larger requests, writeInLoop with a nullptr callback throws bad_function_call, #43 heap-corruption crash unanswered.

## Caveats and trade-offs

Benchmark harness is public but not parameterized: examples/echo_client/main.cpp hard-codes a 4096-byte message and 1 client, examples/boost_asio_echo_client/main.cpp hard-codes 8192 bytes and 1 client, so each README cell needs a constant edited; each number is one one-second printout with no repeat count or variance, on a 4-core laptop CPU (i5-8265U) with client and server sharing the machine, so the 0.1% to 8% gaps are within plausible run-to-run noise. uv-cpp is slower at 8K packets (-1.9%) and slower than nginx 1.14.2 on the HTTP test (15408 vs 16946 req/s, about 9% slower; the two servers also returned different documents, 56 vs 13 bytes, and nginx had 512 failed requests). Harness asymmetry: the uv-cpp echo writes straight from its libuv read buffer with no copy (TcpConnection::write passes the pointer to uv_write), while the Asio harness std::copies each read into a separate 32 KB write buffer and uses async_write_some (a short write would silently drop bytes). The README numbers date from about April 2020 (echo_client was added 2020-04-18); TcpConnection.cpp received further 'fix bug', 'cycle buffer' and 'time wheel' commits in July-December 2020, so the measured code is not pinned to a commit. Boost.Asio 1.67 and nginx 1.14.2 are old (2018). The examples/pingpang program (packet-framed, message count per second) is not the source of the tables. The comparison is libuv wrapper versus Asio and nginx, not a C++ standard-library facility. Last commit 2025-11-13 is a README edit; the last code change is 2023-12-23 ('fix http send').

Thin C++11 callback wrapper over libuv (bundled libuv 1.30.0), so it inherits libuv's single-loop model and adds TCP, UDP, DNS, HTTP server with radix-tree routing, timers, timer wheel, packet framing. Not header-only; Linux and Windows only.

## Maintenance

MIT with 839 stars, but the last code change was 2023-12-23 (HttpClient only) and the last commit is a 2025-11-13 README edit, so 'active' holds only by the 12-month rule. The 2021 reconnect crash (#43) and the September 2026 benchmarking question (#58) have no maintainer reply. The README numbers date from about April 2020, are not pinned to a commit, and come from a harness with TCP_NODELAY only on uv-cpp's side and latency-bound one-client cells. Usable as a small vendorable wrapper, provided you keep every write buffer alive until its callback, which the library's own HTTP code does not.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the README tables match a public harness pair in the repo, examples/echo_server/main.cpp + examples/echo_client/main.cpp (uv-cpp) versus examples/boost_asio_echo_server/main.cpp + examples/boost_asio_echo_client/main.cpp (Boost.Asio), both servers printing received kbyte/s exactly as the README and the chart axes ('K byte/sec', 'one client ping-pong', 'concurrency client ping-pong') report, and the README states gcc 8.3.0, '-O2', libuv 1.30.0 (vendored in the repo), Boost.Asio 1.67 and an Intel Core i5-8265U. Packet size and client count are hard-coded constants that must be edited per table cell, and each figure is a single one-second printout with no repeats.
- **Verifier notes:** Numbers in claimed_speedup match the README exactly; the nginx screenshots are readable and show uv-cpp about 9% slower than nginx, which the record omitted, so the entry is essentially a tie with Boost.Asio rather than a clear win (record as a 'not clearly faster' shortcoming, not a reject). The record's caveat pointed at examples/pingpang as the harness; the real harness is the echo_server/echo_client pair, which makes the benchmark reproducible with constant edits, hence the upgrade to A. Metadata checked on github.com: MIT, 839 stars, 213 forks, not a fork, not archived, last commit 2025-11-13 (README only; maintenance 'active' by the 12-month rule, code untouched since 2023-12-23).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party public harness (verifier C to A, not clearly faster); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/wlgq2/uv-cpp>
  - <https://github.com/wlgq2/uv-cpp/commits>
  - <https://github.com/wlgq2/uv-cpp/tree/master/examples>
  - <https://github.com/wlgq2/uv-cpp/tree/master/examples/pingpang>
  - <https://github.com/wlgq2/uv-cpp/tree/master/examples/boost_asio_echo_server>
  - <https://github.com/wlgq2/uv-cpp/tree/master/examples/boost_asio_echo_client>
  - <https://github.com/wlgq2/uv-cpp/commits/master/uv/TcpConnection.cpp>
  - <https://github.com/wlgq2/uv-cpp/commits/master/examples/echo_client/main.cpp>
  - <https://github.com/wlgq2/uv-cpp/commits/master/README.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/README_cn.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/pingpang/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/pingpang/Clinet.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/pingpang/EchoServer.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/echo_server/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/echo_client/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/boost_asio_echo_server/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/boost_asio_echo_client/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/TcpConnection.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv_cpp_res/master/vs_asio/one_no_data.png>
  - <https://raw.githubusercontent.com/wlgq2/uv_cpp_res/master/vs_asio/concurrency_no_data.png>
  - <https://raw.githubusercontent.com/wlgq2/uv_cpp_res/master/vs_nginx/uv_http_1000.png>
  - <https://raw.githubusercontent.com/wlgq2/uv_cpp_res/master/vs_nginx/nginx_http_1000.png>
- **Sources the enricher read:**
  - <https://github.com/wlgq2/uv-cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/README_cn.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/echo_server/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/echo_client/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/boost_asio_echo_server/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/examples/boost_asio_echo_client/main.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/uv11.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/TcpConnection.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/TcpConnection.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/EventLoop.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/EventLoop.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/Async.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/Async.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/TcpServer.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/TcpServer.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/TcpClient.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/TcpClient.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/TcpAcceptor.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/TcpAcceptor.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/GlobalConfig.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/GlobalConfig.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/ListBuffer.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/ListBuffer.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/CycleBuffer.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/CycleBuffer.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/Packet.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/TimerWheel.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/Signal.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/http/HttpServer.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/http/HttpServer.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/http/Request.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/http/Response.cpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/uv/include/http/RadixTree.hpp>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/doc/en/TcpConnection.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/doc/en/TcpServer.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/doc/en/TcpClient.md>
  - <https://raw.githubusercontent.com/wlgq2/uv-cpp/HEAD/doc/en/EventLoop.md>
  - <https://github.com/wlgq2/uv-cpp/issues?q=is%3Aissue>
  - <https://github.com/wlgq2/uv-cpp/issues/25>
  - <https://github.com/wlgq2/uv-cpp/issues/26>
  - <https://github.com/wlgq2/uv-cpp/issues/41>
  - <https://github.com/wlgq2/uv-cpp/issues/43>
  - <https://github.com/wlgq2/uv-cpp/issues/58>
  - <https://github.com/wlgq2/uv-cpp/tree/master/doc>
  - <https://github.com/wlgq2/uv-cpp/tree/master/doc/en>
  - <https://github.com/wlgq2/uv-cpp/tree/master/examples>
  - <https://github.com/wlgq2/uv-cpp/tree/master/libuv1.30.0>
  - <https://github.com/wlgq2/uv-cpp/tree/master/libuv1.30.0/lib>
  - <https://github.com/wlgq2/uv-cpp/commits/master>
  - <https://github.com/wlgq2/uv-cpp/commits/master/uv>
  - <https://github.com/wlgq2/uv-cpp/commits/master/uv/http/HttpServer.cpp>
  - <https://github.com/wlgq2/uv-cpp/commit/f80c2487e03c2409d88f4add53197a575182da1f>
  - <https://github.com/wlgq2/uv-cpp/commit/f80c2487e03c2409d88f4add53197a575182da1f.diff>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.x/docs/src/stream.rst>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.30.0/src/unix/stream.c>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/wlgq2/uv-cpp`) · [data/wave5/enrich/raw/github_com_wlgq2_uv_cpp.json](../../../data/wave5/enrich/raw/github_com_wlgq2_uv_cpp.json) (enrichment confidence 0.8)

</details>
