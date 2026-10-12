# evpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Qihoo 360's muduo-style C++11 TCP/UDP/HTTP library on top of libevent. In its own echo test it beats libevent 2.0's bufferevent sample by 1.1-2.4x.

| | |
|---|---|
| **Beats** | libevent 2.0.21 (libevent's own sample TCP ping-pong server and client) |
| **Claimed result** | Text: evpp throughput is about 17% higher than libevent2 when the message is smaller than 4096 bytes and about 40%\~130% higher when larger. Chart tables (MB/s at 1/10/100/1000/10000 connections, one thread per side): 1024 B evpp 49.0/148.7/154.7/113.1/87.2 vs libevent 44.5/126.8/135.2/99.8/67.0 (1.10x-1.30x); 4096 B 176.7/512.0/527.4/382.3/293.7 vs 164.3/437.9/448.1/299.5/213.5 (1.08x-1.38x); 8192 B 318.1/880.1/902.8/612.0/505.4 vs 259.8/658.9/661.3/430.6/388.7 (1.22x-1.42x); 16384 B 513.8/1353.5/1297.0/877.8/725.4 vs 527.5/669.4/632.2/370.4/314.4 (0.97x at 1 connection, 2.02x-2.37x at 10+ connections) (ratios derived from page data). Same docs set: evpp 20%\~50% faster than asio 1.10.8 on the IO-event benchmark, about 2% slower than raw libevent there; throughput vs asio similar (asio 5%\~10% ahead at 10,000+ connections) and vs muduo similar. |
| **Workload** | TCP ping-pong (echo) throughput on loopback, one I/O thread per side pinned with taskset, message sizes 1024 to 16384 bytes charted, 1 to 10000 concurrent connections, evpp v0.2.4 (built on libevent 2.0.21) against libevent's server.c and client.c. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2630 v2 @ 2.60GHz, Linux CentOS 6.2 (kernel 2.6.32-220.7.1.el6.x86_64) |
| **Compiler and flags** | gcc 4.8.2 20140120 (Red Hat 4.8.2-15); tools/benchmark-build.sh uses CMake release build, which CMakeLists.txt sets to -O3 -g -ggdb -DNDEBUG; libevent 2.0.21 |
| **Adoption** | 3.8k stars; README claims production use at Qihoo 360 |
| **Last commit** | 2022-11-06 |
| **Links** | [repository](https://github.com/Qihoo360/evpp) · [benchmark](https://github.com/Qihoo360/evpp/blob/master/docs/benchmark_throughput_vs_libevent.md) |

## Verdict

First-party ping-pong echo throughput test on loopback. Server and client each ran one I/O thread pinned to its own core with taskset, for 100 s per cell, with 1 to 10,000 connections. evpp v0.2.4 (on libevent 2.0.21) ran against libevent's own bufferevent echo server and client. Build was gcc 4.8.2 -O3 on CentOS 6.2 (kernel 2.6.32), Xeon E5-2630 v2. evpp was 1.08-1.42x faster at 1-8 KiB messages and 2.0-2.4x at 16 KiB with 10 or more connections, but 0.97x at 16 KiB with one connection (ratios derived from page data).

## Use it when

- Your C++ services already run on libevent and you want a muduo-style multi-threaded TCP server/client with C++11 callbacks without switching event libraries (EventLoop(struct event_base\*) wraps your existing base).
- Long-connection TCP gateways, proxies or echo-like relays that move messages of 4 KiB and up on Linux. There libevent bufferevent's 4096-byte read cap and deferred writes cost the most: the first-party chart shows 1.22-1.42x at 8 KiB and 2.0-2.4x at 16 KiB with 10 or more connections.
- You need async memcached (evmc) or NSQ (evnsq) clients built on the same loop. The README says both serve hundreds of billions of requests a day at Qihoo 360.
- GCC 4.8+ / C++11 toolchains on older Linux distributions (the benchmarks ran on CentOS 6.2), where newer C++17/20 networking libraries will not build.

## Skip it when

- You need a maintained dependency. The last release is v0.7.0 (2017-07-13), the last commit was 2022-11-06, and 136 issues are open. They include an unanswered ASan heap-use-after-free in the TCPServer tests (#303) and NULL-dereference reports (#310, #314).
- You need TLS on raw TCP connections. SSL exists only for the HTTP client and server, behind a compile-time HTTPS=1 option that links OpenSSL and event_openssl. TCPConn has no TLS layer.
- You want io_uring, kernel bypass or coroutine-style code. evpp is a readiness reactor over libevent (epoll on Linux), so look at uring_exec, Asio's io_uring backend or PhotonLibOS instead.
- You are comparing against Boost.Asio or raw libevent rather than bufferevent. evpp's own docs show it at parity with asio 1.10.8 on throughput (asio 5-10% ahead at 10,000 connections and about 10% ahead with multiple threads at 100 connections), and raw libevent about 2% faster on the IO-event benchmark.
- You need bounded memory under slow consumers. Each TCPConn output buffer grows until a 128 MB default high-water mark, and that mark only fires a callback; it does not pause reading.

## How it is fast

evpp uses libevent only for readiness, through raw struct event with EV_PERSIST, and bypasses bufferevent/evbuffer. TCPConn::HandleRead does one readv() into the free part of its Buffer plus a 64 KiB stack spill buffer (muduo's trick), so one syscall can drain the socket. libevent 2.0.21's evbuffer_read caps each read at EVBUFFER_MAX_READ = 4096 bytes. TCPConn::SendInLoop also calls ::send() directly when the output buffer is empty and arms EV_WRITE only for leftovers. A libevent bufferevent instead queues the data and writes on the next EV_WRITE readiness, which costs an extra event_add and loop pass per echo. The 4 KiB read cap explains the 2x gap at 16 KiB, and the write-through path plausibly explains the 10-30% gain at small sizes. The second point is inferred from the code, not measured by the authors.

## Compared with alternatives

libhv uses a similar multi-reactor model without libevent, is still maintained, and its README shows about 1.37x libevent's throughput at 4 threads, 1000 connections and 1 KiB. Prefer evpp only when the code base must keep libevent's event_base, evhttp or evdns, or needs the evmc/evnsq clients. For io_uring or coroutine-style I/O, pick uring_exec, Asio's io_uring backend or PhotonLibOS instead.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib built with CMake (evpp, evpp_static, evpp_lite_static, plus evpp_boost\* and evpp_concurrentqueue\* variants that change the cross-thread functor queue) |
| **Dependencies** | libevent 2.x (a 1.4 mode exists behind H_LIBEVENT_VERSION_14), glog, pthread; optional boost (lock-free pending queue), moodycamel concurrentqueue, gtest, gflags, thrift; OpenSSL and libevent_openssl only for the HTTPS build |
| **Minimum toolchain** | C++11 (-std=c++11), GCC 4.8+, CMake 2.8+; Visual Studio 2015 on Windows per the docs |
| **Platforms** | Linux is the tested target; the README badge lists Linux, BSD, OS X and Windows. The multiplexer is whatever libevent picks (epoll on Linux, kqueue on BSD/macOS). |
| **Thread safety** | Each TCPConn belongs to one EventLoop thread, and its callbacks run there. Send() may be called from any thread: off-loop calls copy the data into a std::string and post it through RunInLoop with a pipe wake-up. The README's event_add/event_del ownership checks are compiled only under H_DEBUG_MODE. |
| **Drop-in for the baseline** | false: it is a C++ class API over libevent's event_base, not a bufferevent replacement. Because it shares libevent's event_base, existing libevent code and evhttp can stay in the same process. |

## Gotchas

- The baseline is libevent 2.0.21's bufferevent echo sample, not raw libevent: on the IO-event benchmark raw libevent is about 2% faster than evpp. The 4096-byte per-read cap behind the 16 KiB gap is still hard-coded (EVBUFFER_MAX_READ) in libevent 2.1.12-stable, the latest stable release. Master adds evbuffer_set_max_read() but keeps a 4096 default and bufferevent_sock.c never raises it. So the large-message gap probably persists against current released libevent unless the application tunes it, which corrects the record's 'likely shrinks on newer libevent'.
- Harness ambiguity: for each buffer size and session count, evpp's single_thread.sh runs two clients in turn against one server instance, client.cc (streaming echo) and client_fixed_size.cc (echo only whole blocks). The doc does not say which output was charted. libevent's single_thread.sh runs only its streaming client.c, and it takes the buffer size from an environment variable (default 16384). The libevent client stops counting exactly at loopexit, while the evpp client counts until its asynchronous Disconnect completes. Over 100 s runs that difference is negligible.
- TCPConn::Send(Buffer\*) returns without consuming the buffer when the connection is not kConnected, so a message sent during disconnect is silently dropped and stays in the input buffer. Send(const void\*, size_t) on the loop thread skips that status check.
- FdChannel allocates a struct event and uses the deprecated event_set/event_base_set API with event2/event_struct.h, so evpp must be compiled against the exact libevent headers it links. A libevent upgrade means rebuilding evpp.

## Known shortcomings

- Numbers read from chart PNGs. The big-message win comes from libevent 2.0.21 hard-coding a 4096-byte read limit (EVBUFFER_MAX_READ), which newer libevent lets you change; evpp is 3% slower at 1 connection with 16 KiB messages and the 8192-byte gain is 22-42%, below the claimed 40-130%. Abandoned (last commit 2022-11-06).
- Enricher: the 4096-byte read cap is still hard-coded in libevent 2.1.12-stable (master adds evbuffer_set_max_read() but the default stays 4096), so the large-message gap likely persists on current libevent; single_thread.sh runs client.cc and then client_fixed_size.cc against one server per cell and the doc never says which run was charted, while the libevent script runs only the streaming client. The baseline is libevent's bufferevent sample and raw libevent is about 2% faster than evpp. Last release v0.7.0 (2017-07-13); #303 heap-use-after-free open.

## Caveats and trade-offs

First-party benchmark (full code, compiler, flags and CPU are public, so A by the tier rules) but old: CentOS 6.2, gcc 4.8.2 and libevent 2.0.21. The absolute numbers are in PNG charts with data tables hosted on raw.githubusercontent.com/zieckey/resources (the evpp author's own repo). The authors attribute the large-message gap to evpp's own buffer and to libevent reading at most 4096 bytes per read; that cap is EVBUFFER_MAX_READ hard-coded in libevent 2.0.21's evbuffer_read (a library limit, not just the sample), and current libevent master makes it configurable (evbuffer max_read, bufferevent_set_max_single_read with a 16384 bufferevent default), so the 2x gap at 16 KiB is specific to libevent 2.0.x and likely shrinks on newer libevent. With 16 KiB messages and a single connection evpp is about 3% slower (513.8 vs 527.5 MB/s); at 8192 bytes the gain is 22%-42%, below the stated 40%\~130% band, while at 16384 it peaks at 137%. In the same docs set raw libevent is about 2% faster than evpp on the IO-event benchmark, and asio and muduo throughput are described as similar, so the win is over libevent 2.0's bufferevent layer specifically. Repo has had no commits since 2022-11-06. The README file is readme.md (lowercase), which is why raw README.md returned 404. [retier] Numbers read from chart PNGs; the big-message win comes from libevent's hard-coded 4096-byte read limit (EVBUFFER_MAX_READ), still the default in 2.1.12-stable (master adds evbuffer_set_max_read()), so the gap is a libevent default rather than a faster core; evpp is 3% slower at 1 connection with 16 KiB messages and the 8192-byte gain is 22-42%, below the claimed 40-130%. single_thread.sh runs client.cc and then client_fixed_size.cc against one server per cell and the doc never says which run was charted, while the libevent script runs only the streaming client; the baseline is libevent's bufferevent sample and raw libevent is about 2% faster than evpp. Abandoned: last release v0.7.0 2017-07-13, last commit 2022-11-06, #303 heap-use-after-free open.

C++11 library layered on libevent (still depends on it), own IO buffer instead of evbuffer; nonblocking multi-threaded TCP/UDP/HTTP servers and clients, async DNS, timers, thread pool; no TLS or io_uring support was looked for in this pass.

## Maintenance

Abandoned: last release v0.7.0 on 2017-07-13, last commit 2022-11-06, 136 open issues with no maintainer replies on recent ones. It is BSD-3-Clause and production-proven at Qihoo 360, but it is a CMake library with libevent and glog dependencies, so adopt it only if you are ready to maintain a fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (benchmark/throughput/evpp and benchmark/throughput/libevent/server.c, client.c, single_thread.sh, built by tools/benchmark-build.sh as a CMake Release build with -O3 -g -ggdb -DNDEBUG), and the page states gcc 4.8.2, CentOS 6.2 and Xeon E5-2630 v2; first-party but fully reproducible, so A by the tier rules.
- **Verifier notes:** Doc page, scripts, CMake flags, BSD-3-Clause, 3.8k stars and last commit 2022-11-06 (abandoned) confirmed; opened the chart PNGs for absolute numbers. Shortcomings: old toolchain and libevent 2.0.21; large-message win comes from libevent 2.0's hard-coded 4096-byte read cap (configurable in newer libevent); evpp 3% slower at 1 connection with 16 KiB messages; 8192-byte gains (22%-42%) fall below the stated 40%\~130%.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party charts (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/Qihoo360/evpp/blob/master/docs/benchmark_throughput_vs_libevent.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_libevent.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_ioevent_performance_vs_asio.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_asio.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/tools/benchmark-build.sh>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/server.c>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/single_thread.sh>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/single_thread.sh>
  - <https://raw.githubusercontent.com/zieckey/resources/master/evpp/benchmark/throughput/evpp-vs-libevent-1thread-1024.png>
  - <https://raw.githubusercontent.com/zieckey/resources/master/evpp/benchmark/throughput/evpp-vs-libevent-1thread-4096.png>
  - <https://raw.githubusercontent.com/zieckey/resources/master/evpp/benchmark/throughput/evpp-vs-libevent-1thread-8192.png>
  - <https://raw.githubusercontent.com/zieckey/resources/master/evpp/benchmark/throughput/evpp-vs-libevent-1thread-16384.png>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/bufferevent_ratelim.c>
  - <https://github.com/Qihoo360/evpp>
  - <https://github.com/Qihoo360/evpp/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/Qihoo360/evpp>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_libevent.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_ioevent_performance_vs_asio.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_asio.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_ping_pong_spend_time_vs_asio.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/benchmark_throughput_vs_muduo_cn.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/docs/quick_start.md>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/tools/benchmark-build.sh>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/CMakeLists.txt>
  - <https://github.com/Qihoo360/evpp/tree/master/benchmark/throughput/evpp>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/README>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/server.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/client.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/client_fixed_size.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/evpp/single_thread.sh>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/server.c>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/client.c>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/benchmark/throughput/libevent/single_thread.sh>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/buffer.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/buffer.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/tcp_conn.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/tcp_conn.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/tcp_server.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/tcp_server.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/tcp_client.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/event_loop.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/event_loop.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/event_loop_thread_pool.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/fd_channel.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/inner_pre.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/inner_pre.cc>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/libevent.h>
  - <https://raw.githubusercontent.com/Qihoo360/evpp/HEAD/evpp/libevent.cc>
  - <https://github.com/Qihoo360/evpp/issues>
  - <https://github.com/Qihoo360/evpp/issues/303>
  - <https://github.com/Qihoo360/evpp/releases>
  - <https://github.com/Qihoo360/evpp/releases/tag/v0.7.0>
  - <https://github.com/Qihoo360/evpp/releases.atom>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/bufferevent_sock.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.1.12-stable/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/buffer.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/bufferevent_sock.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/bufferevent.c>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/qihoo360/evpp`) · [data/wave5/enrich/raw/github_com_qihoo360_evpp.json](../../../data/wave5/enrich/raw/github_com_qihoo360_evpp.json) (enrichment confidence 0.75)

</details>
