# Undertow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Embeddable non-blocking Java HTTP server (Red Hat); a 2014 build topped Kore, libmicrohttpd and a 4-worker nginx in a 2015 hello-world test.

| | |
|---|---|
| **Beats** | nginx (echo module) plus Kore, libmicrohttpd, Onion (C) and Crow (C++) in the same table |
| **Claimed result** | 616,547 req/s (3.29 ms p99) vs Kore 572,782 (1.08x, derived from page data), libmicrohttpd 533,626 (1.16x), Onion 483,824 (1.27x), nginx with echo module 381,368 (1.62x), Crow 256,552 (2.40x). Each README row is the best of four 20 s wrk runs (Undertow's four runs: 607,522 to 616,547). Undertow's p99 (3.29 ms) is worse than libmicrohttpd's (1.28 ms) and Onion's (2.82 ms). |
| **Workload** | Trivial dynamic 'Hello World' text/plain response over HTTP/1.1 keep-alive with wrk, 100 connections, framework overhead only (no database, no JSON). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-1650 v2 @ 3.50GHz (results directory name), 32 GB RAM, Ubuntu 14.04 LTS, Linux 3.16; wrk on the same host with 12 threads (common/threads.sh counts 'core id' lines) and 100 connections; time.sh does a separate 10 s warm-up call and four 20 s runs, and the README reports the best of the four. |
| **Compiler and flags** | Undertow: build.gradle requests io.undertow:undertow-core and undertow-servlet '1.0.0+' (dynamic, resolved at build time in late 2015), started with 'gradle run'; JVM and JVM flags not stated; default Undertow IO/worker thread counts. libmicrohttpd: helloworld.c built 'cc -O3' against the system libmicrohttpd (Ubuntu package, version not stated), MHD_USE_EPOLL_TURBO with a 12-thread pool. Crow: 'c++ -O3 -std=c++11' with boost_system, multithreaded(). Onion: cmake -GNinja with no CMAKE_BUILD_TYPE plus a static libev (current Onion CMakeLists then uses -O2; the 2015 submodule was not checked). Kore: 'kore run', built with 'make NOTLS=1', 12 workers. nginx: the OpenResty-bundled nginx binary (/usr/local/openresty/nginx/sbin/nginx) with the echo module, conf/echo.conf worker_processes 4. Compiler versions not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | The suite's conclusion only says Undertow 'is most optimized'; no mechanism is given. |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/undertow-io/undertow) · [benchmark](https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md) |

## Verdict

nanoant/WebFrameworkBenchmark (December 2015, Xeon E5-1650 v2, Ubuntu 14.04, Linux 3.16; wrk with 12 threads and 100 keep-alive connections on the same host; 20 s runs after a 10 s warm-up; best of four) measured a hello-world handler on Undertow 1.0.0.Final with an unstated JVM at 616,547 req/s. That is 1.08x Kore (make NOTLS=1, 12 workers), 1.16x libmicrohttpd (cc -O3, 12-thread epoll pool, identical 137-byte responses), 1.27x Onion, 1.62x OpenResty nginx with the echo module at 4 workers, and 2.40x Crow (c++ -O3). All ratios are derived from page data, and Undertow's p99 is worse than libmicrohttpd's and Onion's.

## Use it when

- JVM services that want an embedded HTTP/1.1 or HTTP/2 server with a small, explicit handler-chain API rather than a full framework
- Request handlers that can answer without blocking, so they run on the I/O thread with no hand-off; this is the case the benchmark measured
- Applications that need an embeddable Servlet 6.0 or Jakarta WebSocket container in the same process as non-blocking handlers
- Long-running services where JVM start-up, JIT warm-up and a resident heap are acceptable and steady-state keep-alive throughput matters

## Skip it when

- As a replacement for nginx's proxying, TLS termination or static-file serving by configuration; with Undertow you write and run Java code
- Spring Boot 4.x applications: the Spring Boot 4.0 migration guide drops Undertow support ('Spring Boot 4 requires a Servlet 6.1 baseline, with which Undertow is not yet compatible'); use Tomcat or Jetty there
- Tail-latency-sensitive services chosen on this evidence: in the same table libmicrohttpd's p99 was 1.28 ms against Undertow's 3.29 ms (Undertow's four runs ranged 2.16 to 4.08 ms)
- Short-lived processes or tight memory budgets, where JVM start-up, warm-up and heap size dominate; none of that is in the throughput figure
- If you need current numbers against C/C++ servers: Undertow has no entry in the HttpArena suite (frameworks/undertow returns 404) and its own repo has only JMH microbenchmarks

## How it is fast

Handlers run directly on XNIO I/O threads (one per logical CPU by default: Math.max(availableProcessors, 2)), so a non-blocking response like the benchmark's needs no thread hand-off. Blocking work goes to a worker pool of 8 threads per I/O thread through exchange.dispatch(). Buffers come from a pooled allocator that picks direct 16 KB-minus-20-byte buffers when the heap limit is at least 128 MB. The Date header string is cached and invalidated by a timer once a second (DateUtils). The measured 1.0.0.Final release parsed requests with a build-time generated state machine (HttpRequestParser\$\$generated) that has a fast path for 'GET ' and returns interned strings for common methods, protocols and headers; current main replaces it with a hand-written RequestParser.

## Compared with alternatives

Pick Undertow over Netty (same 2015 table, 422,580 req/s) when you want a ready HTTP and Servlet server with a handler API instead of building the pipeline yourself. For current evidence against nginx 1.31.4, the siblings Vert.x, Quarkus and Helidon SE have recent HttpArena rows, and Undertow does not.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | XNIO (xnio-api, xnio-nio 3.8.16.Final), jboss-logging, jboss-threads; the servlet and WebSocket modules add the Jakarta Servlet and WebSocket APIs |
| **Minimum toolchain** | Java 17 for 2.4.x (2.4.4.Final, 2026-10-02) and main (2.5.0.Alpha1-SNAPSHOT); Java 11 for 2.3.x (2.3.26.Final); Maven to build from source |
| **Platforms** | any platform with a supported JVM (pure Java on JDK NIO through XNIO; no native transport) |
| **Thread safety** | Each exchange starts on an XNIO I/O thread; blocking calls there stall every connection on that thread, so handlers check isInIoThread() and dispatch blocking work to the worker pool (exchange.dispatch, startBlocking for stream I/O). The no-argument dispatch() is deprecated as 'hard to use safely'. |
| **Drop-in for the baseline** | no |

## Gotchas

- Old artifact measured: benchmarks/undertow/build.gradle asks for 'io.undertow:undertow-core:1.0.0+'. Gradle treats a trailing '+' as a prefix match (SubVersionSelector: candidate.startsWith("1.0.0"), in Gradle 2.9 of late 2015 and in current master), so the candidates are the 61 versions starting with '1.0.0' on Maven Central (Alpha1-22, Beta1-33, CR1-5, Final), and, because Gradle's version comparator ranks 'final' above any other qualifier, the build resolves 1.0.0.Final (tagged 2014-02-10), which excludes even 1.0.1.Final to 1.0.19.Final and every later 1.x release, so the 2015 run measured a jar from February 2014. Current releases are 2.4.4.Final and 2.3.26.Final. The JVM version and flags are not stated, and build.gradle sets no JVM arguments.
- Response sizes derived from page data (MB/s over req/s): Undertow sends exactly 137 bytes, the same as libmicrohttpd (status line, Connection, Content-Type, Content-Length 11, a Date header and 'Hello World'). That makes the 1.16x over libmicrohttpd (12-thread epoll pool) the like-for-like row. Kore sends 191 bytes and Onion 197, so they do more work per request. The nginx echo row sends 119 bytes with Date and Server stripped, but runs only worker_processes 4 against Undertow's 12 default I/O threads on the 6-core/12-thread Xeon, so the 1.62x over nginx comes from configuration.
- README rows are the best of four 20 s runs for every server, and the ratios hold on four-run means: Undertow 612,590 req/s against libmicrohttpd 531,964 (1.15x), Kore 570,784 (1.07x) and nginx echo 376,520 (1.63x), all derived from page data. The p99 column is unstable for some servers: Kore's run 01 p99 was 87.03 ms and Onion's 105.21 ms, while the README shows 3.99 ms and 2.82 ms from their best runs.
- SECURITY.md lists only 2.2.x and 2.3.x as supported, although 2.4.x has been released since May 2026. WebSearch snippets list recent CVEs: CVE-2025-9784 (HTTP/2 'MadeYouReset' stream-reset DoS), CVE-2026-3260 (multipart/form-data on GET written to disk; fix reported in 2.4.0.Beta1) and CVE-2026-5680 (WebSocket permessage-deflate memory exhaustion; fixed in 2.4.3.Final per Mend). The GitHub Security tab has no advisories because disclosure goes through Red Hat SecAlert, so track Red Hat errata.

## Known shortcomings

- nanoant 2015 suite: the nginx row is crippled (echo.conf worker_processes 4 vs 12 threads/workers elsewhere), so the 1.62x is not like-for-like; small margins over Kore (1.08x) and libmicrohttpd (1.16x) with worse p99 than libmicrohttpd; JVM and compiler versions unstated; wrk ran on the same host.
- Harness flaw: the benchmark measured an old jar. build.gradle asks for undertow-core:1.0.0+, which Gradle treats as a prefix match ranking 'final' highest, so the build got 1.0.0.Final (tagged 2014-02-10), not a 2015 release. Undertow and libmicrohttpd both send 137 bytes per response, so the 1.16x over libmicrohttpd is the only like-for-like row; the 1.62x over nginx comes from worker_processes 4 against 12 I/O threads. The ratios hold on four-run means (1.15x, 1.07x Kore, 1.63x nginx). Spring Boot 4 dropped Undertow (needs Servlet 6.1); SECURITY.md is stale (no 2.4.x); CVEs from search snippets only.

## Caveats and trade-offs

Benchmark is from November-December 2015 (last suite commit 22 Dec 2015) on Undertow 1.x resolved from a '1.0.0+' dynamic dependency, so it is far older than current Undertow, Kore, libmicrohttpd, Onion, Crow and nginx. Single-author suite (53 stars) re-running a TechEmpower-style plaintext hello-world on one 6-core/12-thread machine with the 12-thread wrk load generator on the same host. The nginx row is configuration-skewed: conf/echo.conf sets worker_processes 4 while Kore runs 12 workers, libmicrohttpd a 12-thread pool and Undertow defaults to one IO thread per logical CPU, so the 1.62x over nginx is not a like-for-like comparison; nginx was OpenResty's build answering 'Hello World!' as text/html with Date and Server headers stripped. Kore's MB/s (104.33) exceeds Undertow's (80.55) because it sends larger headers, so bytes per response differ across rows. JVM version and C/C++ compiler versions are not stated; Onion and Kore build flags are not given in the suite. Margins over the strongest C servers are small (1.08x Kore, 1.16x libmicrohttpd) and come from server architecture and thread configuration, not from Java codegen. The Undertow README itself carries no benchmark numbers. [retier] build.gradle asks for undertow-core:1.0.0+, which Gradle treats as a prefix match ranking 'final' highest, so the build got 1.0.0.Final (tagged 2014-02-10). Undertow and libmicrohttpd both send 137 bytes per response, so the 1.16x over libmicrohttpd is the only like-for-like row; the 1.62x over nginx comes from worker_processes 4 against 12 I/O threads. Ratios hold on four-run means (1.15x, 1.07x Kore, 1.63x nginx). Spring Boot 4 dropped Undertow.

JVM start-up, warm-up and memory are not part of the throughput figure; larger footprint than the C servers in the table.

## Maintenance

Actively maintained by Red Hat (Apache-2.0, 3.8k stars, last commit 2026-10-08, 2.4.4.Final on 2026-10-02) and copyable as a Maven dependency. The only evidence is a 2015 single-author benchmark of the 2014 1.0.0.Final jar, so treat the ratios as historical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent third-party suite (nanoant/WebFrameworkBenchmark, not by Undertow authors) with public run scripts (time.sh, benchmarks/\*/run.sh, configs) and raw wrk outputs in results/E5-1650v2-Ubuntu-14.04LTS/; the README table rows match those files (Undertow 616,547 is run 02 of 4, nginx 381,368 is run 01). Not A because compiler versions, the JVM and the resolved Undertow version are not stated and only some C builds carry flags; a small single-author suite (53 stars), so B is the ceiling.
- **Retiered** B to C: Enricher: the suite's '1.0.0+' dependency resolved to Undertow 1.0.0.Final (2014), so the measured build is not the 2015 release the record assumed, and the nginx margin comes from 4 workers against 12 I/O threads; the one like-for-like row (libmicrohttpd) is 1.16x. Stale, mislabelled build with a crippled main baseline: B to C.
- **Verifier notes:** Numbers verified against the README and the raw wrk files. Shortcomings to record: 2015-era versions, load generator on the same host, nginx row crippled by worker_processes 4 (versus 12 threads/workers elsewhere), JVM and compiler versions unstated, small single-author suite, worse p99 than libmicrohttpd. Not a language-level win.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://github.com/nanoant/WebFrameworkBenchmark>
  - <https://github.com/nanoant/WebFrameworkBenchmark/commits/master>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/nginx>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/undertow>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results/E5-1650v2-Ubuntu-14.04LTS>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/build.gradle>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/src/main/java/HelloWorldServer.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/microhttpd/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/microhttpd/helloworld.c>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/crow/helloworld.cpp>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/onion/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/conf/kore.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/run_echo.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/undertow_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/microhttpd_01.txt>
  - <https://raw.githubusercontent.com/davidmoreno/onion/HEAD/CMakeLists.txt>
  - <https://github.com/undertow-io/undertow>
  - <https://github.com/undertow-io/undertow/commits/main>
- **Sources the enricher read:**
  - <https://github.com/undertow-io/undertow>
  - <https://github.com/undertow-io/undertow/commits/main>
  - <https://github.com/undertow-io/undertow/tags>
  - <https://github.com/undertow-io/undertow/commits/1.0.0.Final>
  - <https://github.com/undertow-io/undertow/security>
  - <https://github.com/undertow-io/undertow/tree/main/benchmarks>
  - <https://github.com/undertow-io/undertow/tree/main/core/src/main/java/io/undertow/server/protocol/http>
  - <https://github.com/undertow-io/undertow/blob/2.4.4.Final/pom.xml>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/README.md>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/SECURITY.md>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/pom.xml>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/pom.xml>
  - <https://raw.githubusercontent.com/undertow-io/undertow/2.3.26.Final/pom.xml>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/Undertow.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/UndertowOptions.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/util/DateUtils.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/server/HttpServerExchange.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/server/protocol/http/RequestParser.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/main/core/src/main/java/io/undertow/server/protocol/http/HttpResponseConduit.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/1.0.0.Final/pom.xml>
  - <https://raw.githubusercontent.com/undertow-io/undertow/1.0.0.Final/core/src/main/java/io/undertow/Undertow.java>
  - <https://raw.githubusercontent.com/undertow-io/undertow/1.0.0.Final/core/src/main/java/io/undertow/server/protocol/http/HttpRequestParser.java>
  - <https://repo1.maven.org/maven2/io/undertow/undertow-core/maven-metadata.xml>
  - <https://raw.githubusercontent.com/gradle/gradle/v2.9.0/subprojects/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/strategy/SubVersionSelector.java>
  - <https://raw.githubusercontent.com/gradle/gradle/v2.9.0/subprojects/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/strategy/StaticVersionComparator.java>
  - <https://raw.githubusercontent.com/gradle/gradle/master/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/strategy/SubVersionSelector.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/build.gradle>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/undertow/src/main/java/HelloWorldServer.java>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/microhttpd/helloworld.c>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/conf/kore.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results/E5-1650v2-Ubuntu-14.04LTS>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/undertow_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/undertow_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/undertow_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/undertow_04.txt>
  - https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt (also _02 to _04)
  - https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_01.txt (also _02 to _04)
  - https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/microhttpd_01.txt (also _02 to _04)
  - https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/onion_01.txt (also _02 and _03; _04 came back empty)
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks>
  - https://github.com/MDA2AV/HttpArena/tree/main/frameworks/undertow (404)
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/jooby>
  - <https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide>
  - WebSearch: Undertow CVE 2025 2026 (snippets from advisories.gitlab.com, vulert.com, mend.io; advisories.gitlab.com itself unreachable)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/undertow-io/undertow`) · [data/wave14/enrich/raw/github_com_undertow_io_undertow.json](../../../data/wave14/enrich/raw/github_com_undertow_io_undertow.json) (enrichment confidence 0.8)

</details>
