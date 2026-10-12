# Quarkus (Vert.x/Netty, JDK 21)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java framework (Jakarta REST on Vert.x/Netty) that beats nginx's HTTP/2-over-TLS path on HttpArena but loses every scored HTTP/1.1 profile.

| | |
|---|---|
| **Beats** | nginx (C, hand-written handler module compiled -O3 -march=native, per HttpArena frameworks.json) in the HttpArena suite; h2o, Drogon, Mongoose, libreactorng and other C/C++ rows come from the same results directory |
| **Claimed result** | Rows measured with the current entry (commit 029e5d6, 2026-08-21) against nginx rows from commit df1a679 (2026-08-20): baseline-h2-256 (h2 over TLS) 4,668,449 req/s vs nginx 3,414,750 (1.37x) but h2o 16,106,978 (0.29x); pipelined-4096 (16x pipelining, reference-only, excluded from the composite) 7,858,636 vs nginx 4,037,345 (1.95x), h2o 4,938,603 (1.59x), Drogon 7,801,404 (1.01x). Slower than nginx on the scored HTTP/1.1 and TLS profiles: baseline-4096 1,818,132 vs nginx 3,284,513 (0.55x), h2o 3,641,609 (0.50x), Drogon 2,022,710 (0.90x); limited-conn-4096 564,503 vs nginx 2,626,297 (0.21x); json-tls-4096 588,855 vs nginx 1,313,755 (0.45x) and h2o 1,229,462 (0.48x), though 2.33x Drogon's 253,055; static-h2-256 173,987 vs nginx 802,090 (0.22x); static-tls-1024 339,193 vs nginx 720,869 (0.47x); json-comp-4096 301,675 vs Drogon 127,466 (2.37x). The baseline-h2c-256 row (6,188,551 vs nginx 2,456,329, 2.52x) is stale and not valid evidence. All ratios derived from page data. |
| **Workload** | HttpArena request throughput on one 64-core machine (mixed GET/POST with query parsing at 4096 connections, plus pipelined, HTTP/2 and h2c baseline profiles as listed). Entry is Quarkus with RESTEasy Reactive on Vert.x/Netty, JDK 21, 'optimized JVM tuning' (HttpArena tuned mode). |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node, 8x DDR4-3200), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, site/content/docs/hardware/_index.md); server pinned to cpuset 0-31,64-95 for these profiles (scripts/lib/profiles.sh), load generator (gcannon, h2load for HTTP/2) on the same machine over loopback. |
| **Compiler and flags** | Quarkus 3.17.8 (RESTEasy Reactive, quarkus-rest) compiled for Java 21, run on the eclipse-temurin:25-jre image; quarkus.vertx.prefer-native-transport=true is set but pom.xml lacks netty-transport-native-epoll, which Quarkus 3.17.8 requires, so the runs almost certainly used Java NIO (inferred). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Netty event loops under Vert.x with JVM tuning (HttpArena description); no mechanism is given for the h2c gap to nginx. |
| **Adoption** | 15.9k stars |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/quarkusio/quarkus) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/quarkus-jvm.json) |

## Verdict

HttpArena on an AMD Threadripper PRO 3995WX (server pinned to 32 cores / 64 threads, load generator on the same machine over loopback, best of three 5 s runs): Quarkus 3.17.8 with RESTEasy Reactive on Temurin 25 with ParallelGC served 4.67M req/s on HTTP/2 over TLS vs 3.41M for nginx 1.31.4 running a custom C handler module built -O3 -march=native (1.37x), and 7.86M vs 4.04M on the reference-only 16x pipelined profile (1.95x). On the scored HTTP/1.1, TLS and static profiles it ran at 0.21x to 0.55x of nginx.

## Use it when

- JVM teams that want the Jakarta REST and CDI programming model with event-loop throughput, and accept a framework rather than a toolkit.
- HTTP/2-over-TLS APIs serving many small multiplexed requests: on baseline-h2-256 (GET /baseline2?a=1&b=1, 100 streams per connection) Quarkus served 4,668,449 req/s vs nginx 3,414,750 (1.37x), and 4,425,573 vs 3,320,285 at 1,024 connections (1.33x).
- Gzip JSON APIs on the JVM: json-comp-4096 served 301,675 req/s vs Drogon (C++) 127,466 (2.37x), though with gzip level 1 (see gotchas).
- Pipelined HTTP/1.1 clients (reference-only profile): 7,858,636 req/s vs nginx 4,037,345 (1.95x) and level with Drogon 7,801,404.

## Skip it when

- As a faster nginx or h2o for plain HTTP/1.1, TLS or static files: baseline-4096 0.55x of nginx and 0.50x of h2o, json-tls-4096 0.45x, static-tls-1024 0.47x, static-h2-256 0.22x of nginx (173,987 vs 802,090 req/s, also below h2o's 363,898).
- Short-lived connections: limited-conn-4096 (reconnect every 10 requests) reached 564,503 req/s vs nginx 2,626,297 and h2o 2,651,569 while using 3,256% CPU of the 64 threads available, against 6,200% for nginx and h2o, so connection setup rather than request handling looks like the limit (inferred).
- Memory-constrained hosts: 10.0 to 11.5 GiB on every HTTP/2, TLS and pipelined row (6.8 GiB on baseline-4096) vs nginx 3.5 to 3.8 GiB and h2o 69 to 308 MiB; even near idle (latency-10k) it held 789 MiB vs Drogon's 72 MiB. The Dockerfile sets ParallelGC with no -Xmx, so much of this is default heap sizing.
- CPU-efficiency or tail-latency budgets: latency-1m at a pinned 1M req/s cost 35.0 us CPU per request with p99 1,046 us vs Drogon 32.1 us and 196 us; the 10 KB TLS echo (8gbit-512) cost 164.3 us per request vs Drogon 58.3 us; at 500K req/s on 8 CPUs it held only 64% of the offered rate (Drogon 75%).
- Cleartext HTTP/2 (h2c) or gRPC claims: the benchmark entry disables h2c, and its h2c and grpc rows are stale.

## How it is fast

Quarkus moves framework wiring to build time (README: 'We do more at build time, we start fast'), and endpoints marked @NonBlocking run directly on the Vert.x event-loop threads, one per core, with no hand-off to a worker pool. HTTP/2 comes from Netty's codec with stream multiplexing (the h2 profile sends 100 concurrent streams per connection), and the HotSpot JIT compiles the hot path after warm-up. The benchmark entry also turns off Netty buffer bounds and accessibility checks and Vert.x URI and header validation, metrics and context timings. HttpArena gives no mechanism for the h2 lead; h2o (C) runs the same profile 3.45x faster than Quarkus, so the 1.37x over nginx reflects nginx's HTTP/2 path rather than a Java-over-C advantage (inference from page data).

## Compared with alternatives

Pick Quarkus over Eclipse Vert.x when you want Jakarta REST, CDI and build-time wiring on the same engine; raw Vert.x posted more on HttpArena's pipelined (11.78M vs 7.86M req/s) and baseline profiles, so the framework layer costs throughput. Against Helidon SE it posted more on baseline-h2-256 (4.67M vs 3.61M, separate runs), and Kestrel is the .NET counterpart with similar pipelined numbers (7.44M).

## Integration

| | |
|---|---|
| **Form** | module (Maven/Gradle extensions io.quarkus:quarkus-rest and quarkus-rest-jackson under the io.quarkus.platform:quarkus-bom, packaged by quarkus-maven-plugin as a fast-jar or native executable) |
| **Dependencies** | Vert.x core and Netty (via quarkus-vertx and quarkus-netty), SmallRye Mutiny, Jackson for JSON; Netty native transports (epoll, io_uring, kqueue) are optional and must be added explicitly |
| **Minimum toolchain** | JDK 17 to 25 for Quarkus 3.x (README 'Supported JVM Versions' badge); 4.0.0.Beta1 (2026-10-01) raises the minimum to Java 21; the HttpArena entry builds with maven:3.9-eclipse-temurin-25 targeting Java 21 |
| **Platforms** | any JVM platform; Linux containers are the stated focus ('Container First'); native executables via GraalVM/Mandrel; benchmarked on Linux x86-64 (Threadripper PRO 3995WX) in Docker |
| **Thread safety** | @NonBlocking endpoint methods run on Vert.x event-loop threads and must not block; resource instances are shared across requests (the entry keeps per-thread JDBC statements in ThreadLocals). Detailed threading rules not documented in the sources read. |
| **Drop-in for the baseline** | no |

## Gotchas

- Native transport is not actually on in the benchmark entry: application.properties sets quarkus.vertx.prefer-native-transport=true, but pom.xml has no io.netty:netty-transport-native-epoll dependency; the Quarkus 3.17.8 Vert.x guide says the platform dependency must be added explicitly, and quarkus-netty 3.17.8 marks netty-transport-native-epoll as optional, so the measured runs almost certainly used Java NIO (inferred; the startup log is not published). This handicaps Quarkus rather than inflating it, but the record's flags line overstates the configuration.
- The baseline-h2 win is one constant request (GET /baseline2?a=1&b=1, 100 streams per connection, h2load over loopback); on the wire Quarkus answered in about 27 bytes per response vs about 82 for nginx (bandwidth over req/s, derived from page data), so the two servers do not emit the same headers, and h2o (C) reached 16,106,978 req/s on the same profile.
- json-comp runs at quarkus.http.compression-level=1: about 1,580 bytes per response vs about 1,392 for Drogon (derived from page data). HttpArena scores this profile by rps times the squared ratio of the smallest response size to one's own, so the raw 2.37x over Drogon shrinks to about 1.84x once the size penalty is applied (derived).
- Stale and mislabelled data in the same results file: the baseline-h2c (2.52x nginx), json-h2c and unary-grpc rows predate the current entry, which passes -Dvertx.disableH2c=true and no longer subscribes to those profiles; meta.json and README say JDK 21 but the image runs Temurin 25; the Quarkus rows (2026-08-21) and nginx rows (2026-08-20) come from separate best-of-3, 5 s runs.

## Known shortcomings

- The headline h2c 2.52x row is stale (before 2026-07-24): the current entry cannot produce it (-Dvertx.disableH2c=true, no port 8082, h2c unsubscribed); real wins are h2-256 1.37x nginx and the reference-only pipelined 1.95x, with 0.21-0.55x nginx on the scored H1 and TLS profiles; runs JDK 25, not 21. HttpArena CPU: Threadripper PRO 3995WX.
- The entry sets quarkus.vertx.prefer-native-transport=true but its pom.xml lacks netty-transport-native-epoll, which Quarkus 3.17.8 requires (quarkus-netty marks it optional), so the runs almost certainly used Java NIO (inferred; this handicaps Quarkus rather than inflating it, but the record's flags line overstates the configuration). json-comp runs gzip level 1 at about 1,580 bytes per response against Drogon's 1,392, and HttpArena's size-squared scoring cuts the 2.37x to about 1.84x (derived); baseline-h2 is one constant GET /baseline2?a=1&b=1 with 100 streams per connection, Quarkus about 27 bytes per response against nginx's 82, and h2o is 3.45x Quarkus. The entry pins 3.17.8 (latest 3.40.1); the stale h2c and grpc rows are confirmed.

## Caveats and trade-offs

The baseline-h2c rows in quarkus-jvm.json (and its json-h2c and unary-grpc rows) were last written no later than the 2026-07-24 migration commit 5698fa8 and cannot come from the current entry: its Dockerfile has passed -Dvertx.disableH2c=true since at least 2026-03-28, application.properties opens no port 8082 (the h2c prior-knowledge port), and meta.json no longer subscribes to baseline-h2c, json-h2c or grpc; every h2c row also reports p99 equal to the mean, unlike nginx's h2c rows measured on 2026-08-20, so the 2.52x h2c ratio is a cross-run comparison against stale data. The remaining wins are on pipelining (reference-only in the HttpArena README) and h2 over TLS, where nginx's HTTP/2 path trails h2o by 4.7x on the same profile; on the scored HTTP/1.1 baseline, limited-conn, json-tls and static profiles Quarkus is 0.21x to 0.55x of nginx. Uses 6.8 to 10.7 GiB of memory against nginx's 3.5 GiB. The entry's meta.json and README say JDK 21 but the Dockerfile runs Temurin 25. nginx is a custom C handler module, not a stock config; every entry is a minimal hand-written handler, so this measures server-engine overhead, not static-file serving. Results are 5 s runs on one machine, rerun per framework by the maintainers. [retier] json-comp runs gzip level 1 at about 1,580 bytes per response against Drogon's 1,392, and HttpArena's size-squared scoring cuts the 2.37x to about 1.84x. baseline-h2 is one constant GET /baseline2?a=1&b=1 with 100 streams per connection, Quarkus about 27 bytes per response against nginx's 82; h2o is 3.45x Quarkus. The entry pins 3.17.8 (latest 3.40.1).

JVM start-up and warm-up cost and memory footprint are not part of the throughput figure; Netty/Vert.x event loop under a full framework.

## Maintenance

Very active (last commit 2026-10-12, 3.40.1 latest on 2026-09-30, 4.0.0.Beta1 on 2026-10-01, main merging Vert.x 5.1.10), Apache-2.0 with 15.9k stars and safe to adopt, but the HttpArena entry pins Quarkus 3.17.8, 23 minor releases behind, and its only valid wins over C are on nginx's HTTP/2 path and the unscored pipelined profile.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now A.
- **Tier reason:** Upgraded to A on the HttpArena precedent for the rows measured with the current entry: site/data/results/quarkus-jvm.json and the sibling nginx.json, h2o.json and drogon.json carry every number, the code is public (frameworks/quarkus-jvm/{Dockerfile,pom.xml,src/main/resources/application.properties}, frameworks/nginx/{Dockerfile,nginx.conf,ngx_http_httparena_module.c}, scripts/lib/profiles.sh), JVM and nginx flags are in the Dockerfiles, and the CPU (AMD Ryzen Threadripper PRO 3995WX) is in site/data/current.json. Downgraded because the headline baseline-h2c win is a stale row that the current entry cannot produce.
- **Verifier notes:** Numbers match quarkus-jvm.json and the nginx, h2o and drogon JSON files; tier raised to A on the HttpArena precedent (CPU in site/data/current.json), verdict downgrade because the headline h2c 2.52x is a stale cross-run row the current entry cannot produce (h2c disabled, no port 8082, profile unsubscribed). Shortcomings to record: stale h2c and grpc rows, wins only on h2-over-TLS and reference-only pipelining, 0.21x to 0.55x of nginx on scored H1 profiles, JDK 25 runtime despite 'JDK 21' docs, high memory use.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/quarkus-jvm.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/resources/application.properties>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/nginx>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/quarkus-jvm>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/quarkus-jvm.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/quarkus-jvm>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/quarkus-jvm/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/blame/main/site/data/results/quarkus-jvm.json>
  - <https://github.com/MDA2AV/HttpArena/blame/main/site/data/results/nginx.json>
  - <https://github.com/quarkusio/quarkus>
  - <https://github.com/quarkusio/quarkus/commits/main>
- **Sources the enricher read:**
  - <https://github.com/quarkusio/quarkus>
  - <https://github.com/quarkusio/quarkus/commits/main>
  - <https://github.com/quarkusio/quarkus/releases>
  - <https://github.com/quarkusio/quarkus/issues?q=is%3Aissue%20label%3Aarea%2Fperf%20state%3Aopen>
  - <https://github.com/quarkusio/quarkus/issues?q=is%3Aissue%20http2%20performance>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/HEAD/README.md>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/HEAD/docs/src/main/asciidoc/vertx-reference.adoc>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/HEAD/docs/src/main/asciidoc/native-transport-reference.adoc>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/3.17.8/docs/src/main/asciidoc/vertx-reference.adoc>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/3.17.8/extensions/netty/runtime/pom.xml>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/3.17.8/extensions/vertx/runtime/pom.xml>
  - <https://raw.githubusercontent.com/quarkusio/quarkus/3.17.8/extensions/vertx-http/runtime/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/quarkus-jvm.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/resources/application.properties>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/java/com/httparena/BenchmarkResource.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/java/com/httparena/ServerHeaderFilter.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/java/com/httparena/StaticFiles.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/quarkus-jvm/src/main/java/com/httparena/TlsListener.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/tools/h2load.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/validation.md>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/quarkus-jvm/src/main/java>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/quarkus-jvm/src/main/java/com/httparena>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/quarkus-jvm>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/quarkus-jvm.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/test-profiles>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/test-profiles/h1>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/quarkusio/quarkus`) · [data/wave14/enrich/raw/github_com_quarkusio_quarkus.json](../../../data/wave14/enrich/raw/github_com_quarkusio_quarkus.json) (enrichment confidence 0.75)

</details>
