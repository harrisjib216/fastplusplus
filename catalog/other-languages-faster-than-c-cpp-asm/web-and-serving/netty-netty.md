# Netty

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java asynchronous network framework; a 2015 Netty 3 hello-world server out-ran a 4-worker nginx echo setup and Crow.

| | |
|---|---|
| **Beats** | nginx (echo module) and Crow (C++) in the same table |
| **Claimed result** | 422,580 req/s (99th percentile 4.08 ms) vs nginx with the echo module 381,368 (1.11x, derived from page data) and Crow 256,552 (1.65x, derived from page data); slower than the C servers Kore 572,782 (0.74x), libmicrohttpd 533,626 (0.79x) and Onion 483,824 (0.87x) in the same table (derived from page data). |
| **Workload** | Trivial dynamic 'Hello World' text/plain response over HTTP/1.1 keep-alive with wrk, 12 threads and 100 connections on the same host, framework overhead only; the nginx echo row answers 'Hello World!' as text/html with the Date and Server headers cleared, so bytes per response differ. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-1650 v2 @ 3.50 GHz (6 cores, 12 threads; results/E5-1650v2-Ubuntu-14.04LTS and commit 'All recent results were on E5-1650v2'), 32 GB RAM, Ubuntu 14.04 LTS, Linux 3.16; wrk on the same machine with 12 threads (thread count from common/threads.sh, shown in the raw wrk output) and 100 connections, a 10 s warm-up then four 20 s runs (time.sh). |
| **Compiler and flags** | Netty side: benchmarks/netty/build.gradle pulls org.jboss.netty:netty:latest.integration (the legacy Netty 3 artifact under the old JBoss groupId, before Netty moved to io.netty) plus Guice and Guava 'latest.integration', run with 'gradle run'; JVM version and flags not stated. Crow: c++ -O3 -std=c++11 with boost_system and pthread, multithreaded() (benchmarks/crow/run.sh, helloworld.cpp); compiler version not stated (Ubuntu 14.04 toolchain implied). nginx: the OpenResty nginx binary at /usr/local/openresty/nginx/sbin/nginx with the echo module, worker_processes 4 (benchmarks/nginx/run_echo.sh, conf/echo.conf); version and build flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 35.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/netty/netty) · [benchmark](https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md) |

## Verdict

Setup: nanoant/WebFrameworkBenchmark, December 2015, Xeon E5-1650 v2, Ubuntu 14.04, Linux 3.16, wrk with 12 threads and 100 keep-alive connections on the same machine, 20 s runs, JVM version unstated. A Netty 3.2-era hello-world server reached 422,580 req/s (best of four, p99 4.08 ms) against OpenResty nginx with the echo module limited to 4 workers at 381,368 (1.11x), and Crow (-O3, multithreaded) at 256,552 (1.65x). Both ratios are derived from page data, and Netty also sent the smallest response (no Date header).

## Use it when

- Custom TCP/UDP or binary protocol servers, proxies and gateways on the JVM, where you need control over the pipeline, buffers and threading
- High-connection-count HTTP/1.1, HTTP/2 or WebSocket front ends on Linux, with the epoll or io_uring native transport
- As the I/O layer under a higher-level framework (Vert.x, Quarkus and many RPC stacks build on it) when you need to drop below the framework
- Long-running services where JIT warm-up and a resident JVM are acceptable and steady-state throughput matters

## Skip it when

- Static files, TLS termination or reverse proxying that nginx handles with configuration alone; with Netty you write and maintain the server code
- Short-lived processes or tight memory budgets: JVM start-up and warm-up, plus pooled direct memory (issue #15691 reports direct memory growing from about 70 MB to 700 MB between 4.2.2 and 4.2.4; #15850 'Adaptive allocator direct memory allocation regression' is open)
- When you expect to beat a properly configured native server: in the same 2015 table Kore (572,782 req/s), libmicrohttpd (533,626) and Onion (483,824) beat Netty, and so did Undertow (616,547), another JVM server
- When you want routing, middleware and a ready HTTP API rather than raw handlers; use a framework built on Netty instead

## How it is fast

Each channel's handlers run on a single event-loop thread, so request handling needs no locks. On Linux, the native transports (epoll, edge-triggered by default per EpollMode; io_uring, a first-class module in 4.2) replace the JDK NIO selector; kqueue serves macOS/BSD. Buffers come from pooled direct-memory allocators: the 4.1 pooled allocator (page/run/subpage chunks) or the 4.2 default adaptive allocator (magazines chosen by thread id, sized from allocation histograms), which cut GC pressure and copying. FastThreadLocal indexes an array instead of hashing. In the cited benchmark, though, most of the margin over nginx comes from configuration (see gotchas), not these techniques.

## Compared with alternatives

Vert.x and Quarkus (siblings with current HttpArena wins over nginx 1.31.4) run on Netty and add routing and an application model, so pick raw Netty only when you need custom protocols or direct control of pipeline, buffers and transports. For plain HTTP on the JVM, the sibling Undertow beat Netty in this same table (616,547 vs 422,580 req/s).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond the JDK for the NIO transport; optional native transport jars (epoll, io_uring, kqueue; 4.2 needs glibc 2.17+), optional netty-tcnative/BoringSSL or BouncyCastle for TLS |
| **Minimum toolchain** | Java 8 for Netty 4.2 (the io_uring transport needs Java 9+); building from source needs a JDK and Maven |
| **Platforms** | any JVM platform via NIO; native epoll and io_uring on Linux, kqueue on macOS/BSD |
| **Thread safety** | Each Channel is bound to one event-loop thread of a MultiThreadIoEventLoopGroup and its handlers run there; blocking inside a handler stalls every channel on that loop, and handlers shared across channels must be written to be thread-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- Wrong artifact measured: benchmarks/netty/build.gradle resolves org.jboss.netty:netty:latest.integration. Per Maven Central metadata that is 3.2.10.Final, the last release under the old JBoss groupId (org.jboss.netty.\* API), which is incompatible with io.netty 4.x. The 2015 numbers say nothing about the current 4.2.19.Final / 4.1.139.Final (both tagged 2026-10-06).
- Harness asymmetries, all favouring Netty. (1) HelloWorldServerHandler sets only Content-Type, Content-Length and Connection, never the Date header the benchmark's own spec requires. Response sizes derived from page data (MB/s over req/s): Netty exactly 100 bytes; the nginx echo row 119 bytes, matching a chunked 'Hello World!\n' body with Date and Server cleared; Crow 128 bytes. So Netty skips date formatting and sends the fewest bytes. (2) nginx is capped at worker_processes 4 on a 6-core/12-thread Xeon, and its latency is bimodal: p50 68 us, p75 6.90 ms, p99 24.24 ms. (3) wrk runs 12 threads on the same host.
- The README's Netty figure is the best of four runs (420,723 / 422,543 / 421,462 / 422,580 req/s; the spread is only 0.4%). nginx has a single run file (nginx_echo_01, 381,368). Crow's README figure, 256,552, is not crow_01 (251,341), so the README appears to pick favourable runs.
- Upgrading to 4.2: the default allocator switched from pooled to adaptive (set -Dio.netty.allocator.type=pooled to restore 4.1 behaviour), client TLS hostname verification is now on by default, and 4.1 and 4.2 jars cannot coexist on one classpath. Security fixes arrive often (12 pages of GitHub advisories; ten published 2026-09-10, including High GHSA-pvjx-v7vp-62vq, unbounded per-connection queue growth via HTTP/1.1 pipelining in HttpServerCodec), so stay on the latest patch release.

## Known shortcomings

- The 2015 nanoant suite ran the legacy Netty 3 jar (org.jboss.netty latest.integration), not current Netty; the nginx row was OpenResty echo with worker_processes 4 on a 12-thread E5-1650 v2; wrk on the same host; Netty was slower than Kore, libmicrohttpd and Onion, and only the Crow row (1.65x, -O3) is a fair comparison.
- The measured jar is org.jboss.netty 3.2.10.Final per the Maven metadata. The handler omits the Date header the benchmark spec requires; bytes per response derived from page data: Netty 100, nginx echo 119 (chunked), Crow 128. nginx is capped at 4 workers with bimodal latency; the README picks the best of 4 runs. Current Netty 4.2 has open adaptive-allocator memory issues (#15691, #15850) and the HttpServerCodec pipelining advisory GHSA-pvjx-v7vp-62vq (High).

## Caveats and trade-offs

Measured in December 2015 (last results commit 2015-12-22) with the legacy Netty 3 artifact org.jboss.netty:netty resolved through 'latest.integration', so the numbers describe neither Netty 4.x nor the current netty/netty code. The nginx baseline is handicapped: conf/echo.conf sets worker_processes 4 on a 6-core/12-thread Xeon while Netty 3's NioServerSocketChannelFactory uses a cached thread pool with its default worker count, and nginx is the OpenResty build with the echo module, not a tuned stock nginx; its 24.24 ms p99 against Netty's 4.08 ms points to worker saturation. Load generator (wrk, 12 threads) shares the host. JVM, Netty, Crow, OpenResty and compiler versions are not stated; the README table matches single runs (netty_04, nginx_echo_01). Crow is the 2015 ipkn/crow submodule, built -O3 and multithreaded, which is the fairer comparison. Netty loses to all three C servers (Kore, libmicrohttpd, Onion), so it is not faster than C servers in general. Single-author suite with 53 stars, not a well-known third-party benchmark. [retier] The measured jar is org.jboss.netty 3.2.10.Final per the Maven metadata. The handler omits the Date header the benchmark spec requires (bytes per response: Netty 100, nginx echo 119 chunked, Crow 128); nginx is capped at 4 workers with bimodal latency; the README picks the best of 4 runs. Current Netty 4.2 has open adaptive-allocator memory issues (#15691, #15850) and the HttpServerCodec pipelining advisory GHSA-pvjx-v7vp-62vq (High).

JVM start-up, warm-up and memory are not part of the throughput figure; Netty is a networking toolkit, so the benchmarked server is hand-written on top of it.

## Maintenance

Netty is very actively maintained (Apache-2.0, 35.1k stars; 4.2.19.Final and 4.1.139.Final tagged 2026-10-06; 5.0.0.Alpha2 on Maven Central). This entry's evidence, however, is a 2015 single-author benchmark of the long-superseded org.jboss.netty 3.2 jar, so treat the nginx ratio as historical and config-driven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README table and raw wrk files (results/E5-1650v2-Ubuntu-14.04LTS/netty_04.txt 422,580 req/s, nginx_echo_01.txt 381,368, crow_\*.txt) carry the numbers and the code is public, but compiler versions and the JVM are unstated, the suite is a 53-star single-author repo rather than a well-known one, the nginx baseline is handicapped by its config (4 workers) and the measured artifact is the legacy Netty 3 jar, not the current netty/netty code, so C rather than B.
- **Verifier notes:** Numbers match the README and raw wrk files. Shortcomings to record: legacy Netty 3 jar (org.jboss.netty, latest.integration) measured, not current Netty; 2015 data; nginx limited to worker_processes 4 on a 12-thread CPU (crippled baseline config) and run as OpenResty with the echo module; load generator on the same host; versions and compiler flags unstated; Netty slower than Kore, libmicrohttpd and Onion. Only the Crow row (1.65x, -O3, multithreaded) is a fair C++ comparison.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://github.com/nanoant/WebFrameworkBenchmark>
  - <https://github.com/nanoant/WebFrameworkBenchmark/commits/master>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/crow>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/netty>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/nginx>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/netty/src/main/java>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/nginx/conf>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results/E5-1650v2-Ubuntu-14.04LTS>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/helloworld.cpp>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/build.gradle>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/src/main/java/HelloWorldServer.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/src/main/java/HelloWorldServerHandler.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/run_echo.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_04.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/crow_01.txt>
  - <https://github.com/netty/netty>
  - <https://github.com/netty/netty/commits/4.2>
- **Sources the enricher read:**
  - <https://github.com/netty/netty>
  - <https://github.com/netty/netty/tags>
  - <https://github.com/netty/netty/security/advisories>
  - <https://github.com/netty/netty/wiki/Netty-4.2-Migration-Guide>
  - <https://github.com/netty/netty/issues?q=is%3Aissue+adaptive+allocator+memory>
  - <https://raw.githubusercontent.com/netty/netty/4.2/buffer/src/main/java/io/netty/buffer/PoolChunk.java>
  - <https://raw.githubusercontent.com/netty/netty/4.2/buffer/src/main/java/io/netty/buffer/AdaptivePoolingAllocator.java>
  - <https://raw.githubusercontent.com/netty/netty/4.2/buffer/src/main/java/io/netty/buffer/ByteBufUtil.java>
  - <https://raw.githubusercontent.com/netty/netty/4.2/transport-classes-epoll/src/main/java/io/netty/channel/epoll/EpollMode.java>
  - <https://raw.githubusercontent.com/netty/netty/4.2/common/src/main/java/io/netty/util/concurrent/FastThreadLocal.java>
  - <https://repo1.maven.org/maven2/org/jboss/netty/netty/maven-metadata.xml>
  - <https://repo1.maven.org/maven2/io/netty/netty-all/maven-metadata.xml>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/build.gradle>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/src/main/java/HelloWorldServer.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/src/main/java/HelloWorldServerHandler.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/netty/src/main/java/HelloWorldServerPipelineFactory.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/run_echo.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/helloworld.cpp>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/netty_04.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/crow_01.txt>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks>
  - https://github.com/MDA2AV/HttpArena/tree/main/frameworks/netty (404)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/netty/netty`) · [data/wave14/enrich/raw/github_com_netty_netty.json](../../../data/wave14/enrich/raw/github_com_netty_netty.json) (enrichment confidence 0.8)

</details>
