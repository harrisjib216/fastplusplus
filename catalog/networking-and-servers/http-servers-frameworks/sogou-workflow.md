# Sogou C++ Workflow (HTTP Server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Sogou's C++11 async task engine; its embedded HTTP server hit \~2.2-2.6x nginx's QPS on small bodies (first-party test).

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | Read off the docs/benchmark.md charts (derived from page data). QPS vs concurrency (benchmark-01.png): at concurrency 256-2048, workflow \~490-530K QPS vs nginx \~203-213K for 64B/512B bodies (\~2.3-2.6x) and \~442-458K vs \~180-205K for 4096B (\~2.2-2.5x); the gap is small at concurrency 1-4, where brpc leads. QPS vs body length (benchmark-02.png): workflow \~425-545K vs nginx \~165-220K up to 4KB, but at 8-16KB the workflow-512 and nginx-512 curves nearly meet (\~202K vs \~195K; \~166K vs \~163K) and at 32KB/64KB all servers converge at \~88K/\~45K. Latency: at fixed body size workflow is lower than nginx as concurrency grows (\~4.0-4.5ms vs \~12.4-14.1ms at concurrency 2048), but at concurrency 512 with 16KB/32KB bodies workflow latency (\~8ms/\~18ms) is higher than nginx (\~4ms/\~9ms) (benchmark-04.png). The prose states only that workflow 'can maintain 500K QPS' for 64B and 512B bodies at sufficient concurrency and that it beats brpc and nginx throughout the QPS curves. |
| **Workload** | Minimal HTTP server returning a fixed random ASCII body (with Date/Content-Type headers); concurrency doubled over 1-2048 and body size doubled over 16B-64KB (orthogonal), load from wrk/wrk2 on a separate machine. workflow ran 16 poller + 20 handler threads; nginx 40 worker processes; brpc 40 threads. A second test measured latency CDFs vs brpc only (concurrency 1024, 1KB bodies, 20K/100K/200K QPS with 1% 5ms slow requests). |
| **Metric** | throughput |
| **Hardware** | Two identical machines (server and client, \~0.1ms RTT): Intel Xeon E5-2630 v4 @ 2.20GHz, '40 Cores' x86_64 (socket count not stated), 192GB RAM, 25000Mbps NIC, CentOS 7.8.2003, kernel 3.10.0-1127.el7.x86_64 |
| **Compiler and flags** | GCC 4.8.5 stated on the page; optimization flags are not stated. benchmark/CMakeLists.txt (initial 2020 commit) defaults to CMAKE_BUILD_TYPE RelWithDebInfo with -Wall -fPIC -pipe -std=c++11 -fno-exceptions. nginx and brpc build options are not stated. |
| **Adoption** | 14.4k stars |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/sogou/workflow) · [benchmark](https://github.com/sogou/workflow/blob/master/docs/benchmark.md) |

## Verdict

The authors' 2020 test ran wrk from a second identical machine: Xeon E5-2630 v4 (40 cores), 192 GB RAM, 25 GbE, CentOS 7.8 with kernel 3.10, GCC 4.8.5; optimization flags were not stated, and the library's CMake default is RelWithDebInfo. It served a fixed random body with Date/Content-Type headers, with workflow on 16 pollers + 20 handlers and nginx on 40 workers. Read off the charts, at concurrency 256-2048 workflow reached \~490-530K QPS vs nginx's \~203-213K for 64 B/512 B bodies and \~426-458K vs \~180-205K for 4 KB (\~2.2-2.6x), but the curves converge at 16-64 KB and nginx had lower latency at concurrency 512 with 16/32 KB bodies.

## Use it when

- C++ services that send many small (up to \~4 KB) dynamic HTTP responses over hundreds to \~2K keep-alive connections. This is where the first-party test showed \~2.2-2.6x nginx's QPS and lower latency.
- Handlers that fan out to other backends (HTTP, Redis, MySQL, Kafka, custom TCP/TLV protocols) and need async composition that holds no thread while waiting, using series/parallel/DAG tasks instead of callback nesting.
- Services that mix network IO with CPU work: compute queues and WFGoTask run in the same task graph as network tasks.
- Linux deployments (the primary target; CI builds Ubuntu, Fedora and FreeBSD) where an Apache-2.0 C++11 library with no Boost/asio dependency is wanted. It is packaged as libworkflow-dev (Debian/Ubuntu) and workflow-devel (Fedora).

## Skip it when

- Large responses. In the benchmark, QPS converges with nginx at 16-64 KB bodies (\~165K, \~88K, \~45K), and at concurrency 512 with 16/32 KB bodies workflow latency (\~8/\~18 ms) is about twice nginx's (\~4/\~9 ms).
- Tens of thousands of concurrent connections. No data above 2048 concurrency is published. In issue #906 the maintainer says the published concurrency range (hundreds to a few thousand) was chosen as typical and favorable, and that nginx degraded less above \~10K in their own tests. The default max_connections is 2000.
- You need HTTP/2, HTTP/3 or HTTP/1.1 pipelining. The source tree has no HTTP/2 code (issue #129 from 2020 only says it is planned). Server-side pipelining was rejected by design (issue #908): a pipelined connection got one response and was then closed.
- You want a configurable nginx replacement for TLS termination, static files or reverse proxying. Workflow is a library, and all of that is C++ you write and maintain.
- Handler code that blocks (synchronous DB drivers, sleeps, std::future). By default only 20 handler threads run process() and callbacks, and the FAQ warns that std::future can deadlock all of them. Use counter/timer/go tasks or WFFuture instead.

## How it is fast

It is a single-process multi-reactor. N poller threads (mpoller, each fd pinned to poller fd % N) run edge-triggered epoll, or kqueue on BSD/macOS. Each poller reads into its own 256 KB buffer and runs the incremental protocol parser on the poller thread. Complete messages go through a two-list message queue (separate put/get mutexes; the consumer takes the whole list) to a pool of handler threads that run process(). Replies are sent with writev straight from the handler thread and only fall back to EPOLLOUT on EAGAIN. Timeouts sit in a per-poller red-black tree that drives one timerfd, and append_output_body_nocopy() avoids copying the body. In issue #688 the maintainer says the project uses no memory pool and no lock-free structures, and that removing the IO-to-handler queue would add only about 10%.

## Compared with alternatives

Pick Workflow over H2O when the HTTP server is one piece of a C++ backend that also calls Redis/MySQL/Kafka/HTTP upstreams asynchronously. H2O's catalogued win over nginx is static-file serving, while Workflow's is small dynamic responses. Drogon, Crow and Oat++ are catalogued only against Go net/http on the-benchmarker, so Workflow is the only one in this group with a head-to-head against nginx, although that comparison is first-party.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (CMake or make; xmake and Bazel files included; distro packages libworkflow-dev / workflow-devel) |
| **Dependencies** | OpenSSL 1.1+ or BoringSSL (the nossl branch removes it), pthread; zlib, lz4, zstd and snappy only when the Kafka client is built |
| **Minimum toolchain** | C++11 (the library builds with -std=c++11 -fno-exceptions, C sources -std=gnu90), CMake 3.10+; the benchmark used GCC 4.8.5 |
| **Platforms** | Linux (epoll + timerfd), macOS and FreeBSD (kqueue), Android. Windows is a separate IOCP branch. The README claims any CPU (x86 32/64-bit, ARM of either endianness, Loongson). |
| **Thread safety** | process() and callbacks run concurrently on handler threads (20 by default). Poller threads (4 by default) do epoll and message parsing. Shared state inside process() needs your own synchronization (the FAQ example guards shutdown() with a flag because process runs concurrently). Handler threads must not block. |
| **Drop-in for the baseline** | false — a C++ library you link into your own server binary, not a configurable web server or reverse proxy like nginx |

## Gotchas

- WFServerParams.max_connections defaults to 2000. Past that, the server closes an idle keep-alive connection or refuses the new one with EMFILE. Raise it for high connection counts (issue #906). The published benchmark code used this default while testing 2048 concurrency.
- The response is sent only after all tasks in the server task's series finish, and there is no reply(). Data passed to append_output_body_nocopy() must stay alive until the task callback.
- The headline license is Apache-2.0, but src/kernel/rbtree.c is Linux-kernel code under a GPL v2-or-later header, and the repo ships LICENSE_GPLV2. Have the license reviewed before embedding it in proprietary binaries.
- The library is compiled with -fno-exceptions, so do not let exceptions escape process() or callbacks. Tasks you create but never start must be released with dismiss().

## Known shortcomings

- The \~2.2-2.6x over nginx holds at small bodies only: all servers converge at 16-64 KB bodies, and at concurrency 512 with 16-32 KB bodies workflow latency is about 2x worse than nginx. The nginx config and brpc code are not published, and no optimization flags are stated (CMake default RelWithDebInfo).
- The benchmark server keeps the default max_connections=2000, below the 2048 concurrency point, and socket errors are not reported, so the 2048 figures are suspect. Body-length chart legends are mislabelled. The maintainer says the range was chosen as typical but favourable and that nginx degraded less above \~10K concurrency (#906). src/kernel/rbtree.c is GPL-2.0-or-later Linux code inside an Apache-2.0 repo. No HTTP/2; server-side pipelining rejected by design (#908). Single-process queue may cap near 1M QPS (#891). Versions before 1.1.0 carry an HTTP parser bug and a TLS concurrency bug.

## Caveats and trade-offs

First-party benchmark from the 2020 docs (GCC 4.8.5, kernel 3.10). Results are PNG charts; only the \~500K QPS figure is in prose, and the page says only selected concurrency/length combinations are plotted. nginx config and brpc server code are not published, and their tuning (40 workers/threads) was chosen by the workflow authors. The advantage over nginx vanishes at large bodies: QPS converges at 16-64KB (likely bandwidth-bound on the 25Gbps NIC), and at concurrency 512 with 16KB/32KB bodies workflow latency is higher than nginx. brpc is slightly ahead at concurrency 1-4 and at 20K QPS in the latency CDF.

Task/series-based async programming model has a learning curve vs simple thread-per-request servers.

## Maintenance

Actively maintained: v1.1.0 was released 2026-08-10 after a run of fix releases (TLS concurrency, HTTP parser byte-by-byte bug, &gt;2 GB size handling), with 14.4k stars and Debian/Fedora packages. The README says it serves Sogou's back-end services at more than 10 billion requests per day. It is Apache-2.0, apart from the GPL-headed rbtree.c.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party docs/benchmark.md states the CPU (Xeon E5-2630 v4 @ 2.20GHz, 40 cores), GCC 4.8.5, NIC and OS, and the workflow server code is public (benchmark/benchmark-01-http_server.cc). Optimization flags are not stated on the page (only implied by the RelWithDebInfo default in benchmark/CMakeLists.txt), and the nginx config and brpc server code are not published, so the baseline side is not reproducible and it is not A; first-party, so not B.
- **Verifier notes:** Real entry with a genuine nginx comparison, but tier A was too high (flags unstated on page, baseline configs unpublished) and 'consistently better across all combinations' is overstated: the charts show convergence at 16-64KB bodies and worse latency than nginx at 16/32KB, concurrency 512. Metadata verified: Apache-2.0, not a fork, not archived, 14,424 stars, last commit 2026-08-10 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sogou/workflow>
  - <https://github.com/sogou/workflow/blob/master/docs/benchmark.md>
  - <https://github.com/sogou/workflow/blob/master/benchmark/README.md>
  - <https://github.com/sogou/workflow/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sogou/workflow/blob/0f6372c7/benchmark/CMakeLists.txt>
  - <https://github.com/sogou/workflow/blob/0f6372c7/benchmark/GNUmakefile>
  - <https://github.com/sogou/workflow/blob/master/benchmark/benchmark-01-http_server.cc>
  - <https://github.com/sogou/workflow/tree/master/benchmark/util>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-01.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-02.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-03.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-04.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-05.png>
- **Sources the enricher read:**
  - <https://github.com/sogou/workflow>
  - <https://github.com/sogou/workflow/blob/master/README.md>
  - <https://github.com/sogou/workflow/blob/master/docs/benchmark.md>
  - <https://github.com/sogou/workflow/blob/master/benchmark/README.md>
  - <https://github.com/sogou/workflow/blob/master/benchmark/benchmark-01-http_server.cc>
  - <https://github.com/sogou/workflow/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sogou/workflow/blob/0f6372c7/benchmark/benchmark-01-http_server.cc>
  - <https://github.com/sogou/workflow/blob/0f6372c7/src/server/WFHttpServer.h>
  - <https://github.com/sogou/workflow/blob/master/CMakeLists.txt>
  - <https://github.com/sogou/workflow/blob/master/src/CMakeLists.txt>
  - <https://github.com/sogou/workflow/blob/master/src/server/WFServer.h>
  - <https://github.com/sogou/workflow/blob/master/src/server/WFServer.cc>
  - <https://github.com/sogou/workflow/blob/master/src/server/WFHttpServer.h>
  - <https://github.com/sogou/workflow/blob/master/src/manager/WFGlobal.h>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/poller.c>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/mpoller.c>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/mpoller.h>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/msgqueue.c>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/Communicator.cc>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/rbtree.c>
  - <https://github.com/sogou/workflow/blob/master/src/kernel/list.h>
  - <https://github.com/sogou/workflow/blob/master/src/protocol/http_parser.c>
  - <https://github.com/sogou/workflow/blob/master/LICENSE_GPLV2>
  - <https://github.com/sogou/workflow/blob/master/.github/workflows/ci.yml>
  - <https://github.com/sogou/workflow/blob/master/README_cn.md>
  - <https://github.com/sogou/workflow/blob/master/docs/en/about-config.md>
  - <https://github.com/sogou/workflow/blob/master/docs/en/tutorial-04-http_echo_server.md>
  - <https://github.com/sogou/workflow/blob/master/docs/en/tutorial-05-http_proxy.md>
  - <https://github.com/sogou/workflow/issues/406>
  - <https://github.com/sogou/workflow/issues/906>
  - <https://github.com/sogou/workflow/issues/908>
  - <https://github.com/sogou/workflow/issues/891>
  - <https://github.com/sogou/workflow/issues/688>
  - <https://github.com/sogou/workflow/issues/878>
  - <https://github.com/sogou/workflow/issues/129>
  - <https://github.com/sogou/workflow/issues/1798>
  - <https://github.com/sogou/workflow/issues/1795>
  - <https://github.com/sogou/workflow/issues/37>
  - <https://github.com/sogou/workflow/pull/1817>
  - <https://github.com/sogou/workflow/pull/1820>
  - <https://github.com/sogou/workflow/releases/tag/v1.1.0>
  - <https://github.com/sogou/workflow/releases/tag/v1.0.1>
  - <https://github.com/sogou/workflow/releases/tag/v1.0.0>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-01.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-02.png>
  - <https://raw.githubusercontent.com/wiki/sogou/workflow/img/benchmark-04.png>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/sogou/workflow`) · [data/wave5/enrich/raw/github_com_sogou_workflow.json](../../../data/wave5/enrich/raw/github_com_sogou_workflow.json) (enrichment confidence 0.8)

</details>
