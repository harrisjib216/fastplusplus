# ActiveJ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java NIO event-loop platform whose HTTP server beat actix-web by \~9% on the-benchmarker's empty GET test.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | 178398.2 req/s vs actix-web 163414.7 req/s at concurrency 512 (\~9% faster; derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24 (data.json updated_at 2026-09-24 06:59 UTC): GET / (empty body), load from zrk --plain --closed (a closed loop over keep-alive connections) after a 5s warmup at c=50, 15s measured run, concurrency 512, values are the mean of 3 runs, server in a Docker container on a single host |
| **Metric** | throughput |
| **Hardware** | data.json metadata reports 16 vCPUs, cpu_name 'M1 Eight-Core Processor', machine 'x86_64', kernel 7.2.6-200.fc44 (self-contradictory CPU name); both activej and actix used about 3.95 server cores at 0.99 CPU saturation |
| **Compiler and flags** | Java 21, Maven build, launched as `java -jar target/benchmark.jar benchmark.App` with no extra JVM flags (the-benchmarker java/config.yaml, java/activej/config.yaml) |
| **Adoption** | 998 stars |
| **Last commit** | 2026-01-09 |
| **Links** | [repository](https://github.com/activej/activej) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

On the-benchmarker/web-frameworks run of 2026-09-24 (develop commit f673364), ActiveJ 5.5 (MultithreadedHttpServerLauncher, workers = availableProcessors) served an empty GET / at 193,023 / 182,021 / 178,398 req/s at concurrency 64 / 256 / 512 vs actix-web 4.8 at 179,203 / 168,270 / 163,415 (+7.7% / +8.2% / +9.2%). Load came from zrk closed-loop keep-alive runs of 15 s (mean of 3) after a 5 s warmup, with both servers saturating about 4 pinned cores in Docker. The JVM was plain `java -jar` with no flags; the Java Dockerfile template defaults to an Eclipse Temurin 25 JRE and the benchmark pom targets release 25, although java/config.yaml says 21. Host metadata says 16 vCPU x86_64 but names an 'M1 Eight-Core Processor', so the exact CPU is unknown.

## Use it when

- You must stay on the JVM and want the most small-response HTTP throughput per core: ActiveJ was the top Java entry in the 2026-09-24 run (178.4k req/s at c=512 vs jooby 167.4k, Vert.x 145.5k, Undertow 129.8k, Spring 44.1k).
- Many keep-alive connections with tiny, CPU-light responses (internal APIs, health or metrics endpoints, gateways) on a few pinned cores, where one event loop per core fits well.
- You want a small embedded server without Spring or Netty: the README gives 1.4 MB JAR and 0.65 s cold start for its DI-based hello-world launcher.
- You already use other ActiveJ parts (Inject, RPC, Serializer, CSP streams) and want one async model across them.

## Skip it when

- Handlers mostly do blocking work (JDBC, blocking SDKs): a blocked call stalls the whole worker loop and every connection on it, so you must offload to executors (BlockingServlet, Promise.ofBlocking).
- You need a maintained release line: the last stable release is 5.5 (June 2023), 6.0 has been at rc2 since December 2024, and issue #326 asking for the next release has no maintainer reply.
- You depend on the mainstream Java ecosystem: no Servlet/Jakarta API, and the OpenTelemetry Java agent does not propagate context automatically (open issue #338).
- Server-push WebSocket traffic written from other threads: a WebSocket can only be used on its reactor thread and writes must be chained serially (issue #280, where the reporter moved to another library).
- You are already on Rust: the lead over actix-web is 8-9% on one route that does no work, and only \~4% in the 2026-09-20 run.

## How it is fast

Reactor pattern: each worker runs a single-threaded Eventloop over a java.nio Selector, and a PrimaryServer on its own loop accepts sockets and hands them round-robin to per-core worker HTTP servers, so the request path takes no locks and makes no thread hand-offs. Requests are parsed straight from pooled byte[] ByteBufs: the method is found by summing its bytes into a 128-slot table, header names are hashed case-insensitively (b | 0x20) to interned HttpHeader tokens, and connection state lives in a bit-flag byte. Each response is rendered into one pooled buffer sized by estimateSize() and sent in one socket write, and pipelined requests already in the read buffer are answered in one batched write. Buffers come from ByteBufPool (33 power-of-two slab classes) and are recycled, which keeps GC load low.

## Compared with alternatives

Pick it when you must stay on the JVM: it is the only Java framework among the siblings that beat actix-web in this run. On the same run may_minihttp (194.4k), caprese (212.6k), ohkami-nio (181.8k) and httpbeast (175.5k) post equal or higher req/s at c=512. ActiveJ's data.json p99 at c=512 (2.95 ms) is far below caprese's (10.57 ms) and httpbeast's (11.26 ms).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | slf4j-api (logging facade, imported by Eventloop); the HTTP launcher also pulls activej-specializer, which needs ASM (asm, asm-commons: 9.4 in 5.5, 9.7.1 on master). HTTP core itself uses no other third-party libraries. |
| **Minimum toolchain** | Java 8 for 5.5 (the benchmarked release); Java 17 for the 6.0 line (6.0-rc2, master 6.0-SNAPSHOT); Maven Central artifacts under io.activej |
| **Platforms** | any JVM (pure java.nio Selector; no native epoll/io_uring transport documented) |
| **Thread safety** | Each Eventloop, and the servers, connections and WebSockets bound to it, is single-threaded and must only be touched from its own reactor thread; other threads submit work with Eventloop#execute/submit. ByteBufPool is shared across threads through concurrent slab queues. |
| **Drop-in for the baseline** | no |

## Gotchas

- 5.5 and 6.0 APIs differ: 5.5 uses AsyncHttpServer.create(...) and servlets that return HttpResponse directly, while 6.0 uses builders (HttpServer.builder, Eventloop.builder) and .toPromise(). The benchmark ran 5.5, not current master.
- 5.5 pins ASM 9.4, and Serializer fails with 'Unsupported class file major version 65' on Java 21 class files until you override ASM to 9.5 or newer (issue #325).
- In 6.0 the launcher's default listen address changed from \*:8080 to localhost:8080, so IPv6 clients are refused until http.listenAddresses is set (issue #290). TLS behind PrimaryServer throws an NPE unless the worker servers also get the SSLContext (issue #312).
- HttpClient's DnsClient defaults to Google Public DNS. It ignores /etc/hosts and Kubernetes resolv.conf search domains, so cluster short names fail (issue #315, open).

## Known shortcomings

- The benchmark pom targets Java 25 and the Dockerfile uses Temurin 25, so the run likely used JDK 25, not the recorded Java 21. It benchmarks ActiveJ 5.5 (2023) with the 5.x API; 6.0 changed the API and has sat at rc2 since 2024-12, the last commit is 2026-01 and a release request (#326) got no reply. Margin over actix is small and run-dependent (+7.7-9.2% here, \~4% in the 2026-09-20 run), and actix has lower p99 at c=64 and c=256. 5 s warmup may be short for the JIT; the JVM ran with no flags. 'No third-party dependencies' is loose (slf4j-api; specializer and ASM for HTTP). Known issues: serializer fails on Java 21 class files with ASM 9.4 (#325); 6.0 listens on localhost by default (#290); TLS behind PrimaryServer NPE (#312); DNS client ignores hosts files and Kubernetes search domains (#315); WebSockets are single-thread with chained writes (#280); no OpenTelemetry context propagation (#338).

## Caveats and trade-offs

Single synthetic route with a modest margin (\~9%). The harness warms up for only 5s at c=50, which may be short for JIT steady state. In the earlier 2026-09-20 run (master data.json) the margin was only \~4% (104123 vs 99835 req/s). Harness methods changed several times in 2026, so numbers from different revisions do not compare.

Full-stack Java platform (own DI, serialization, RPC, HTTP) built on a single-threaded-event-loop-per-core model similar to Netty; departs from the typical JVM thread-per-request model, so integration with existing Java stacks is nontrivial

## Maintenance

Slow-moving rather than active: occasional commits (last on 2026-01-09), no release since 6.0-rc2 (December 2024), last stable release 5.5 (June 2023). It is Apache-2.0 and published on Maven Central, so usable as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (the-benchmarker/web-frameworks, \~7.1k stars) with public harness code; its data.json has activej at 178398.16 req/s and actix (actix-web 4.8) at 163414.69 req/s at c=512. It is not A because the CPU model in the metadata is self-contradictory ('M1 Eight-Core Processor' on x86_64) and no JVM flags are stated beyond a plain `java -jar`.
- **Verifier notes:** The claimed numbers are exact, but they come from develop (the default branch, commit f673364f), not master. Master's data.json is the older 2026-09-20 run with different numbers. The record's workload ('oha, keep-alive disabled') describes the pre-2026-09 harness; config.rake at f673364f shows zrk --closed with keep-alive, and the saturation fields in data.json confirm the new harness produced these numbers.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/activej/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://github.com/activej/activej>
- **Sources the enricher read:**
  - <https://github.com/activej/activej>
  - <https://github.com/activej/activej/blob/master/README.md>
  - <https://github.com/activej/activej/blob/master/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/pom.xml>
  - <https://github.com/activej/activej/blob/v6.0-rc2/pom.xml>
  - <https://github.com/activej/activej/blob/master/core-http/pom.xml>
  - <https://github.com/activej/activej/blob/master/core-eventloop/pom.xml>
  - <https://github.com/activej/activej/blob/master/core-bytebuf/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/core-http/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/util-common/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/core-specializer/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/launchers/http/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/launchers/common/pom.xml>
  - <https://github.com/activej/activej/blob/v5.5/core-eventloop/src/main/java/io/activej/eventloop/Eventloop.java>
  - <https://github.com/activej/activej/blob/v5.5/core-bytebuf/src/main/java/io/activej/bytebuf/ByteBufPool.java>
  - <https://github.com/activej/activej/blob/v5.5/core-net/src/main/java/io/activej/net/PrimaryServer.java>
  - <https://github.com/activej/activej/blob/v5.5/launchers/http/src/main/java/io/activej/launchers/http/MultithreadedHttpServerLauncher.java>
  - <https://github.com/activej/activej/blob/v5.5/core-http/src/main/java/io/activej/http/HttpServerConnection.java>
  - <https://github.com/activej/activej/blob/v5.5/core-http/src/main/java/io/activej/http/AbstractHttpConnection.java>
  - <https://github.com/activej/activej/tags>
  - <https://github.com/activej/activej/issues>
  - <https://github.com/activej/activej/issues/325>
  - <https://github.com/activej/activej/issues/326>
  - <https://github.com/activej/activej/issues/290>
  - <https://github.com/activej/activej/issues/312>
  - <https://github.com/activej/activej/issues/315>
  - <https://github.com/activej/activej/issues/280>
  - <https://search.maven.org/solrsearch/select?q=g:io.activej+AND+a:activej-http&core=gav&rows=12&wt=json>
  - <https://activej.io/http>
  - <https://activej.io/http/benchmarks>
  - <https://activej.io/async-io/eventloop>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/activej/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/activej/pom.xml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/java/activej/src/main/java/benchmark/io/activej/http/Main.java>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/master/frameworks/Java/activej/benchmark_config.json>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/master/frameworks/Java/activej/pom.xml>
  - <https://hn.algolia.com/api/v1/search?query=activej&tags=story&hitsPerPage=20>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/activej/activej`) · [data/wave5/enrich/raw/github_com_activej_activej.json](../../../data/wave5/enrich/raw/github_com_activej_activej.json) (enrichment confidence 0.55)

</details>
