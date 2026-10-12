# Jooby (Java)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java/Kotlin web framework on Netty (or Jetty/Undertow/Vert.x); ties actix-web on the-benchmarker's empty GET / test.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop commit f673364): jooby 4.5 (Java) 178,206 / 170,003 / 167,390 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.99x / 1.01x / 1.02x (derived from page data). Earlier snapshots (older harness method): commit 0fccb1d (2026-09-20, on master) 118,041 / 101,984 / 103,009 vs 115,638 / 102,329 / 99,835 = 1.02x / 1.00x / 1.03x; commit 8ae370a (2026-09-18) 117,595 / 101,701 / 98,735 vs 117,177 / 100,171 / 98,722 = 1.00x / 1.02x / 1.00x (derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24 (data.json updated_at 2026-09-24 06:59 UTC, develop commit f673364): GET / (empty body) on the suite's minimal per-framework app, load from `zrk --plain --closed` (a closed loop over keep-alive connections, not wrk) after a 5 s warmup at c=50, 15 s runs at concurrency 64/256/512, server container on \~4 cores (server_cpu_cores \~3.95, saturation \~0.99) with the load generator on separate cores; values are averages of the stored samples; jooby Java variant on jooby-netty |
| **Metric** | throughput |
| **Hardware** | Single host per data.json: 16 CPUs, 7,733,008 kB RAM, Linux 7.2.6-200.fc44.x86_64 (x86_64); the cpu_name 'M1 Eight-Core Processor' is a string hard-coded in .tasks/db.rake, not a measured CPU model; server container used \~3.95 cores; run dated 2026-09-24 |
| **Compiler and flags** | Maven build (`mvn clean package`, maven:3-eclipse-temurin build image, eclipse-temurin JRE runtime; java/config.yaml lists language version 21), jooby-netty [4.5,4.6), launched as `/usr/bin/java -jar target/benchmark.jar benchmark.App` with no JVM flags. Baseline: actix-web 4.8 built with Rust 1.98 (rust:1.98-slim) `cargo build --release`, opt-level=3, lto=true, codegen-units=1, panic=abort |
| **Adoption** | 1.8k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/jooby-project/jooby) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks run of 2026-09-24 (develop commit f673364), Jooby 4.5 (Java, jooby-netty, EVENT_LOOP, default headers off) served an empty GET / at 178,206 / 170,003 / 167,390 req/s at concurrency 64 / 256 / 512. actix-web 4.8 (Rust 1.98, release build, LTO) served 179,203 / 168,270 / 163,415, giving 0.99x / 1.01x / 1.02x, and two earlier runs gave 1.00-1.03x. Load came from zrk closed-loop keep-alive runs of 15 s after a 5 s warmup, with both servers saturating about 4 cores in Docker. The JVM ran as plain `java -jar` with no flags on JDK 25: the pom targets release 25, and the Dockerfile template falls back to JDK 25 images because the `version: 21` in java/config.yaml is only a metadata key. Host metadata says 16 vCPU x86_64, but the 'M1 Eight-Core Processor' name is hard-coded, so the CPU model is unknown.

## Use it when

- You are on the JVM and want plaintext or light-API throughput in the actix/hyper range. In the 2026-09-24 run Jooby (Java, Netty, EVENT_LOOP) was the second-fastest JVM entry at 167k req/s at c=512. ActiveJ led with 178k; Vert.x (145k), Undertow (130k), Quarkus (109k) and Spring Boot (44k) were all slower.
- Your handlers are non-blocking (CompletableFuture, Reactor or RxJava types, Kotlin coroutines) and can stay on the event loop, and only a few routes need `dispatch { }` for JDBC or other blocking I/O.
- You want a conventional framework (Guice/Avaje DI, Jackson, Hibernate/JDBI, OpenAPI generation, hot reload) rather than a bare async I/O toolkit, and want to keep the option to swap Netty for Jetty or Undertow later.
- You run microservices where an empty or tiny response at high keep-alive concurrency dominates, and you can pin the ExecutionMode per route.

## Skip it when

- You want a speedup over actix-web. This is a tie (0.99-1.03x across three runs), so porting a Rust service to Jooby gains no throughput.
- Tail latency matters at low concurrency. At c=64 in the same run, Jooby's p99 was 0.68 ms vs actix's 0.39 ms, and p99.999 was 4.2 ms vs 1.4 ms. At c=512 both were within 10%. The cause (JIT, GC or other) was not measured.
- You plan to use the Kotlin DSL and expect the same numbers. The Kotlin variant (Gradle build, same Netty and EVENT_LOOP setup) ran at 0.92-0.94x actix even with -Xms2g -Xmx2g -XX:+UseParallelGC. The cause is not documented.
- Your handlers block for a long time under the default settings. On Netty the worker pool is only CPU count x 8 threads: in issue #3540 a 1 s sleep endpoint served 8 req/s vs Spring's 170 until a cached or virtual-thread executor was supplied.
- You need evidence beyond an empty GET. No JSON, DB, TLS or HTTP/2 comparison with actix is cited here. TechEmpower plaintext for 4.x regressed against 3.x in 2025 (issue #3770, since fixed), and fortunes lost some speed when a thread-local cache was removed.

## How it is fast

jooby-netty is a thin layer over Netty 4.2. It uses one event loop per CPU (ioThreads = availableProcessors), the pooled ByteBufAllocator, TCP_NODELAY and an 8192 backlog, and picks its transport in the order io_uring &gt; epoll &gt; kqueue &gt; JDK NIO, depending on which optional native jars are present. In EVENT_LOOP mode, which the benchmark uses, handlers run on the I/O thread with no hand-off to a worker pool. Hot-path tricks: a case-insensitive header multimap taken from Vert.x (HeadersMultiMap) that encodes straight into the output ByteBuf, a Date header string refreshed once a second by a background thread, exact-class checks before `instanceof` to avoid HotSpot's secondary-supertype cache contention (JDK-8180450, see SlowPathChecks), and Netty leak detection switched off by default. Routing is a port of go-chi's radix tree; static paths are checked first against unrolled 1-6-entry exact-match tables (a HashMap past that), which hold a precomputed match object per HTTP method.

## Compared with alternatives

ActiveJ, the other JVM sibling, was 7-8% faster in the same run (193k/182k/178k vs 178k/170k/167k req/s at c=64/256/512). Jooby is a mainstream framework (Netty, Jetty or Undertow, MVC annotations, OpenAPI, 50+ integration modules, Kotlin DSL), so pick it when ecosystem matters more than those few percent. Against hyper or actix-web it is a throughput tie, so pick it only if you are staying on the JVM.

## Integration

| | |
|---|---|
| **Form** | module (Maven Central: io.jooby:jooby plus exactly one server artifact, e.g. io.jooby:jooby-netty; Gradle and Maven plugins available) |
| **Dependencies** | jooby-netty: jooby core and Netty 4.2.18.Final (netty-handler, netty-codec-http, netty-codec-http2). netty-transport-native-epoll, -kqueue and -io_uring are optional, so you must add them yourself. Other server artifacts: jooby-jetty (Jetty 12.1.13), jooby-undertow (Undertow 2.4.3.Final) and jooby-vertx. jooby-kotlin provides the Kotlin DSL (built against Kotlin 2.4.20). |
| **Minimum toolchain** | Java 21 for the 4.x line (maven.compiler.release 21). The benchmark app was compiled with release 25. |
| **Platforms** | Any JVM 21+ platform. With jooby-netty, io_uring or epoll (Linux) and kqueue (macOS) are used only when their optional jars are present; otherwise JDK NIO is used. |
| **Thread safety** | Handlers run concurrently. On Netty that means availableProcessors event-loop threads plus a fixed worker pool of max(CPUs, 2) x 8 threads (Jetty: 200). In EVENT_LOOP mode, blocking on the I/O thread is 'STRICTLY FORBIDDEN'; use dispatch() or WORKER mode. Whether the per-request Context is thread-safe is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default ExecutionMode is DEFAULT, not EVENT_LOOP. Routes that return plain values (String, POJO) are sent to the worker pool, and only CompletableFuture, reactive or coroutine returns stay on the event loop. The benchmark numbers come from an explicit `runApp(args, new NettyServer(options), EVENT_LOOP, App::new)`, where any blocking call stalls an I/O thread.
- The benchmark app also set `setDefaultHeaders(false)` (no Date, Content-Type or Server header) and depended only on jooby-netty. Netty therefore ran on JDK NIO, not native epoll or io_uring. A default Jooby app sends more headers per response.
- NettyServer sets io.netty.leakDetection.level=DISABLED unless you pass that property, so ByteBuf leaks in your own Netty code go unreported. Header validation stays on unless -Dio.netty.disableHttpHeadersValidation=true is set; keep it on, because the project had a CRLF response-splitting advisory (GHSA-gv3v-92v6-m48j, 2020).
- Only one server artifact may be on the classpath. The 4.x (Java 21) and 3.x lines are maintained in parallel, with separate docs at jooby.io and jooby.io/v3. jooby-pac4j had a high-severity deserialization advisory (GHSA-7c5v-895v-w4q5, 2025).

## Known shortcomings

- Parity with actix, within noise: 0.99x/1.01x/1.02x on 2026-09-24 and 1.00-1.03x in the earlier runs; the Kotlin variant is slower (0.94x at c=512).
- ActiveJ, the other JVM entry, was 7-8% faster in the same run. At c=64 p99 is 0.68 vs actix's 0.39 ms (p99.999 4.2 vs 1.4 ms). The benchmark config isn't Jooby's default: EVENT_LOOP set explicitly (default sends value-returning handlers to the worker pool), default headers off (no Date/Content-Type/Server), JDK NIO rather than the optional native epoll/io_uring transports. Effective JDK is 25 (pom release 25; 'version: 21' is only metadata), and a graalvm engine is also defined without saying which produced the row. Default worker pool is CPU x 8 on Netty (a 1 s sleep endpoint served 8 req/s vs Spring's 170, #3540). 4.x had a TechEmpower plaintext regression (#3770, fixed). Netty leak detection is turned off by default. Advisories: jooby-pac4j deserialization (GHSA-7c5v-895v-w4q5, 2025, high), assets path traversal and CRLF response splitting (2020). Evidence covers a single empty GET / only.

## Caveats and trade-offs

This is parity, not a speedup: 0.99x / 1.01x / 1.02x at c=64/256/512 in the cited run and 1.00x-1.03x in the two earlier snapshots, all within run-to-run noise. The Kotlin variant of jooby is slower than actix (153,750 req/s at c=512, 0.94x). Plain `java -jar` with no JVM tuning. Single-route synthetic GET / benchmark; the CPU name is a hard-coded label.

JVM startup/warmup and GC pauses matter under sustained load; the Kotlin variant of jooby in the same shootout (153,750 req/s) does NOT beat actix, only the Java variant does.

## Maintenance

Actively maintained: last commit 2026-09-26, 7,400 commits, 5 open issues, 4.5.4 released 2026-07-29, and the 3.x line still patched (3.12.0 on 2026-08-07). Apache-2.0 on Maven Central, so it is an ordinary dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs jooby (Java) and actix in one run with public code (java/jooby/pom.xml, java/jooby/config.yaml, java/config.yaml, java/Dockerfile, rust/actix, rust/Dockerfile, .tasks/config.rake). Not A: the cpu_name is hard-coded in .tasks/db.rake, and no JVM flags are given.
- **Verifier notes:** Numbers match data.json exactly (row id 1009 'jooby' java 4.5; actix id 3052). The claim was already caveated as noise, so this is a confirm with the claim expanded to all levels and snapshots. benchmark_url is pinned to develop commit f673364, and wrk is corrected to zrk --closed. Metadata verified via GraphQL: Apache-2.0, 1,779 stars, last commit 2026-09-26, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8ae370ae89075281c056a138e57de25682d36e02/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/jooby/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/jooby/pom.xml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/Dockerfile>
  - <https://github.com/jooby-project/jooby>
- **Sources the enricher read:**
  - <https://github.com/jooby-project/jooby>
  - <https://github.com/jooby-project/jooby/blob/main/README.md>
  - <https://github.com/jooby-project/jooby/tree/main>
  - <https://github.com/jooby-project/jooby/blob/main/docs/asciidoc/execution-model.adoc>
  - <https://github.com/jooby-project/jooby/blob/main/docs/asciidoc/servers.adoc>
  - <https://github.com/jooby-project/jooby/blob/main/docs/asciidoc/getting-started.adoc>
  - <https://github.com/jooby-project/jooby/blob/main/pom.xml>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/pom.xml>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/netty/NettyServer.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/NettyTransport.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/NettyServerCodec.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/NettyPipeline.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/HeadersMultiMap.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/NettyUnsafeHeapByteBuf.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/SlowPathChecks.java>
  - <https://github.com/jooby-project/jooby/blob/main/modules/jooby-netty/src/main/java/io/jooby/internal/netty/NettyDateService.java>
  - <https://github.com/jooby-project/jooby/blob/main/jooby/src/main/java/io/jooby/internal/Chi.java>
  - <https://github.com/jooby-project/jooby/blob/main/jooby/src/main/java/io/jooby/ServerOptions.java>
  - <https://github.com/jooby-project/jooby/issues/3770>
  - <https://github.com/jooby-project/jooby/issues/3754>
  - <https://github.com/jooby-project/jooby/issues/3540>
  - <https://github.com/jooby-project/jooby/issues?q=performance>
  - <https://github.com/jooby-project/jooby/security/advisories>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/jooby/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/jooby/pom.xml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/jooby/src/main/java/benchmark/App.java>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/java/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/kotlin/jooby/src/main/kotlin/benchmark/App.kt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/kotlin/jooby/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/kotlin/jooby/build.gradle.kts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://api.github.com/repos/the-benchmarker/web-frameworks/git/trees/f673364fb30748e5bb8e57319ec2772bc872f78a?recursive=1>
  - <https://hn.algolia.com/api/v1/search?query=jooby&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/jooby-project/jooby`) · [data/wave5/enrich/raw/github_com_jooby_project_jooby.json](../../../data/wave5/enrich/raw/github_com_jooby_project_jooby.json) (enrichment confidence 0.45)

</details>
