# cardigan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MPL-2.0` · 🟢 active

> Experimental Java 26 HTTP/1.1 and HTTP/2 server on raw io_uring; out-runs nginx's custom C module on HttpArena's plaintext profiles.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native) in the HttpArena suite; h2o, mongoose (C) and Drogon (C++) rows in the same table |
| **Claimed result** | baseline-4096: 3,947,346 req/s vs nginx 3,284,513 (1.20x, derived from page data), Drogon 2,022,710 (1.95x), h2o 3,641,609 (1.08x), mongoose 3,707,598 (1.06x). pipelined-4096: 45,708,428 vs nginx 4,037,345. baseline-h2-256: 14,467,569 vs nginx 3,414,750 (4.2x). baseline-h2c-256: 15,144,652 vs nginx 2,456,329 (6.2x). |
| **Workload** | HttpArena baseline profile (mixed GET/POST with query parsing, 4096 connections), plus pipelined, HTTP/2 and h2c baseline profiles, on one 64-core machine; cardigan is a Java io_uring HTTP engine using Panama FFI, virtual threads and the Vector API. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, single NUMA node), 251 GiB RAM, Ubuntu 24.04.4, kernel 6.17.0-22, Docker 29.3.0 (runc), performance governor (site/data/current.json; site/content/docs/hardware/_index.md). Server container and the gcannon/h2load load generator are pinned to separate halves of the same machine (load generator on CPUs 32-63,96-127) and talk over loopback with MTU 1500; 5 s runs, best of 3 (scripts/lib/common.sh, scripts/benchmark.sh). |
| **Compiler and flags** | cardigan 0.1.0-alpha.5: maven eclipse-temurin JDK 26 build, eclipse-temurin:26-jre runtime with --enable-preview --enable-native-access=ALL-UNNAMED --add-modules jdk.incubator.vector -Xms512m -Xmx2g -XX:MaxInlineSize=150 -XX:FreqInlineSize=600 (frameworks/cardigan/Dockerfile); TLS through the system libssl.so.3/libcrypto.so.3 via Panama with opportunistic kTLS. nginx 1.31.4: -O3 -march=native -DNDEBUG with a custom C handler module, worker_processes auto, reuseport. Drogon: CMake Release with jemalloc preloaded. h2o: clang Release -march=native -mtune=native, no LTO. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Thread-per-core event loops on io_uring with Panama FFI, virtual threads and the Vector API (engine description in HttpArena meta.json); nginx in the same suite uses epoll. |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/phjeltman/cardigan) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cardigan.json) |

## Verdict

On HttpArena's 64-core AMD Threadripper PRO 3995WX (loopback, server and load generator on separate CPU halves, 5 s runs, best of 3), cardigan 0.1.0-alpha.5 on Temurin JDK 26 served 3,947,346 req/s at baseline-4096 vs 3,284,513 for nginx 1.31.4 with a custom C module built -O3 -march=native (1.20x, derived from page data), and 14.5M/15.1M req/s on baseline-h2-256/h2c-256 vs nginx 3.4M/2.5M. C io_uring engines libreactorng (4,377,377) and libioma (4,255,834) beat it on the same board, and cardigan's rows were saved days after nginx's in separate runs.

## Use it when

- Experimenting with a JVM service where small, CPU-cheap HTTP/1.1 or HTTP/2 handlers dominate and you want io_uring-class throughput without async/reactive code.
- Plaintext HTTP/1.1 with many keep-alive connections or heavy pipelining on a dedicated Linux 6.1+ x86-64 box (HttpArena baseline-4096 3.95M req/s, pipelined-4096 45.7M req/s on a 64-core Threadripper).
- HTTP/2 cleartext or TLS fan-in where nginx's HTTP/2 stack is the bottleneck (14.5M req/s at baseline-h2-256 vs nginx 3.4M), and a JDK 26 preview runtime is acceptable.
- Research or benchmarking of Loom-plus-io_uring designs; the code is MPL-2.0 and the repo documents its scheduler in detail.

## Skip it when

- Production: 0.1.0-alpha.5, 28 commits, one maintainer, 1 star, public API and configuration declared experimental, and it depends on --add-opens java.base/java.lang (APOLOGY.md) with no compatibility promise across JDK releases.
- Anything outside 64-bit Linux 6.1+ with full io_uring support: it refuses to start rather than fall back when a required ring feature is rejected, and containers need seccomp relaxed for io_uring.
- As an nginx replacement for reverse proxying, static files with caching rules or config-driven sites: it is an application framework, not a web server product.
- Short-lived-connection or tail-latency-sensitive loads: at limited-conn-4096 it is level with or behind nginx, h2o, mongoose and the C io_uring engines, and its p99 on json-tls-4096 is 205.72 ms vs nginx 52.31 ms.
- Memory-tight deployments: the HttpArena container ran a 512 MiB-2 GiB heap and showed 1.2 GiB RSS at baseline-4096 (up to 5.9 GiB at baseline-h2c-4096), vs 75-105 MiB for h2o and libreactorng.

## How it is fast

Thread-per-core, shared-nothing event loops, each pinned to a CPU and driving its own io_uring ring through Panama FFI with SINGLE_ISSUER, DEFER_TASKRUN, registered files, provided-buffer rings and multishot accept/receive (no epoll fallback). Handlers run as virtual threads whose scheduler is the ring-owning carrier itself (via the internal Loom builder), so a blocking read parks on the same core that owns the socket; responses are encoded straight into native egress buffers and pipelined HTTP/1 replies are batched. The HTTP/1 parser is a Java port of picohttpparser and JSON uses a Vector API port of simdjson.

## Compared with alternatives

Pick it over Vert.x, Quarkus, Helidon SE or Netty when you want blocking-style Java handlers with io_uring thread-per-core throughput and can live with an alpha on JDK 26 preview; the C# minima-sync, zeemo, zix, vanilla and libxev rows beat it at baseline-4096 (4.31-4.44M vs 3.95M req/s), so on raw HTTP/1 throughput it is not the leader even among non-C entries.

## Integration

| | |
|---|---|
| **Form** | Maven artifact dev.cardigan:cardigan (0.1.0-alpha.5), a JAR library you embed |
| **Dependencies** | No runtime Maven dependencies (JUnit is test scope); system libssl.so.3/libcrypto.so.3 via Panama when TLS is enabled; JVM flags --enable-native-access=ALL-UNNAMED, --add-opens java.base/java.lang=ALL-UNNAMED, --add-modules jdk.incubator.vector (HttpArena also passes --enable-preview) |
| **Minimum toolchain** | JDK 26 with the incubating Vector API, Maven 3.9+ |
| **Platforms** | 64-bit Linux 6.1+ only (x86-64 is the regularly exercised target); kTLS optional, TLS 1.3 kTLS needs OpenSSL 3.5+ and kernel rekey support |
| **Thread safety** | Each event loop owns its connections and native resources on one pinned carrier; ordinary handlers run as virtual threads on that carrier and may block; @Isolated moves CPU-heavy or untrusted blocking work to a separate carrier pool; @DecodedBody decoders must be bounded, non-blocking and thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness parity (derived from page data): HttpArena's bandwidth/rps gives about 66 bytes per baseline response for cardigan (status line, Content-Type, Content-Length, body) against about 142 for nginx, 114 for libreactorng and 103 for h2o; cardigan sends no Date header (RFC 9110 requires one from an origin server with a clock) and no Server or Connection header, while nginx's module response carries all three, so cardigan writes roughly half the bytes per request. HttpArena's validate.sh checks only Content-Type, so this is legal for the suite but not equal work.
- On the h2/h2c rows the top servers converge at 14.5-16.1M req/s while using only 13-30 of the 64 server hardware threads (cardigan 1474% CPU at baseline-h2-256, agensio 1953%, h2o 3033%), which suggests h2load rather than the server sets the ceiling; the 4.2x and 6.2x over nginx measure nginx (6485% CPU, server-bound), not a lead over other fast HTTP/2 stacks.
- Virtual-thread scheduling uses an internal JDK builder through --add-opens java.base/java.lang; a JDK update can break it, and the same opening is used to read compact String bytes on hot paths.
- HttpArena runs pull the 0.1.0-alpha.5 Maven artifact, not the repo HEAD, and the benchmark entry was written and submitted by the cardigan author; the cardigan repo itself publishes no benchmark numbers and points to HttpArena.

## Known shortcomings

- The win is the io_uring architecture, not Java: the C io_uring servers libreactorng and libioma beat it at baseline-4096; the h2/h2c 4.2x/6.2x reflect nginx's slow HTTP/2 (h2o and agensio are level or ahead); TLS crypto is OpenSSL/kTLS via FFI; an experimental alpha with 1 star.
- Parity flaw: HttpArena bandwidth over rps gives about 66 bytes per baseline response for cardigan against 142 for nginx, 114 for libreactorng and 103 for h2o (derived from page data); cardigan sends no Date, Server or Connection header (none in the Response or Http2ResponseWriter source) and validate.sh checks only Content-Type, so it does less work per request. On the h2 and h2c rows the top servers cluster at 14.5-16.1M req/s on 13-30 of 64 hardware threads, so h2load sets the ceiling and the 4.2x/6.2x measure nginx's slowness. The run used the Maven alpha.5 artifact; the author submitted the entry.

## Caveats and trade-offs

The win over nginx is architectural (io_uring thread-per-core vs nginx's epoll workers), not Java: the io_uring C engines on the same board beat cardigan at baseline-4096 (libreactorng 4,377,377, libioma 4,255,834 vs 3,947,346), and at limited-conn-4096 cardigan (2,613,832) is behind nginx 2,626,297, h2o 2,651,569, libreactorng 2,685,717, mongoose 2,701,933 and libioma 2,707,029. On h2/h2c nginx is the outlier: h2o leads baseline-h2-256 (16,106,978 vs 14,467,569) and agensio (C++) leads baseline-h2-256 (14,744,015) and h2c-256 (15,185,367 vs 15,144,652), so the 4.2x and 6.2x ratios measure nginx's HTTP/2 stack. TLS rows (baseline-h2, json-tls 1,703,461 vs nginx 1,313,755 and agensio 1,716,076) run OpenSSL 3 through Panama FFI with kTLS, so crypto is C or kernel code. pipelined-4096 (45,708,428 vs nginx 4,037,345; libreactorng 43,424,448) is a reference-only profile excluded from the composite score. Fixed-rate CPU per request is mixed (latency-1m 20.4 us, second only to libioma 19.3; latency-10k 31.7 us, behind most C/C++ entries; 8gbit 60.7 vs mongoose 57.4 and Drogon 58.3). Experimental alpha (0.1.0-alpha.5, 28 commits, 1 star), relies on unsupported JDK internals (APOLOGY.md), needs JDK 26 preview and incubator Vector API and Linux 6.1+. The entry was contributed by the cardigan author; rows come from separate runs on the same machine (cardigan last saved 2026-09-03, nginx 2026-08-30); the repo README states no benchmark numbers; handlers are minimal (nginx is a custom C module). [retier] Cardigan sends no Date, Server or Connection header, about 66 bytes per baseline response against 142 for nginx, 114 for libreactorng and 103 for h2o; validate.sh checks only Content-Type, so it does less work per request. On the h2 and h2c rows the top servers cluster at 14.5-16.1M req/s on 13-30 of 64 hardware threads, so h2load sets the ceiling and the 4.2x/6.2x measure nginx's slowness. The run used the Maven alpha.5 artifact; the author submitted the entry.

Experimental alpha Java server needing JDK 26 preview features, Panama FFI and the incubating Vector API; io_uring needs seccomp unconfined in containers; JVM heap 512m-2g and warm-up are not part of the throughput figure.

## Maintenance

Active alpha (last commit 2026-09-02, releases alpha1 to alpha5 between 2026-08-08 and 2026-09-02, no issues filed), MPL-2.0 with MIT/Apache-2.0 ported files; usable for experiments, not for production until it stops depending on JDK internals and preview features.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: every quoted number matches site/data/results/cardigan.json and the sibling nginx/drogon/h2o/mongoose JSON files in MDA2AV/HttpArena; code is public (frameworks/cardigan/{Dockerfile,pom.xml,src/.../HttpArenaController.java}, frameworks/nginx/{Dockerfile,nginx.conf}, scripts/benchmark.sh), JDK and nginx flags are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json and the hardware docs, as accepted for wtx and Cutelyst on this harness in wave 5.
- **Verifier notes:** Tier upgraded to A (HttpArena publishes the CPU model); all quoted numbers verified. Shortcomings to record: not a language win (C io_uring engines libreactorng and libioma beat it at baseline-4096; behind every C engine at limited-conn-4096), h2/h2c ratios reflect a slow nginx HTTP/2 stack (h2o and agensio level or ahead), TLS crypto is OpenSSL/kTLS via FFI, pipelined is reference-only, experimental alpha with 1 star and unsupported JDK internals.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-16 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cardigan.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/pom.xml>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/cardigan/src/main/java/dev/cardigan/httparena>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/src/main/java/dev/cardigan/httparena/HttpArenaController.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/cardigan.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/phjeltman/cardigan>
  - <https://github.com/phjeltman/cardigan/commits>
  - <https://github.com/phjeltman/cardigan/tree/main>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/DOCUMENTATION.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/APOLOGY.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/THIRD_PARTY_NOTICES.md>
- **Sources the enricher read:**
  - <https://github.com/phjeltman/cardigan>
  - <https://github.com/phjeltman/cardigan/commits/main>
  - <https://github.com/phjeltman/cardigan/issues?q=is%3Aissue>
  - <https://github.com/phjeltman/cardigan/tree/main/src/main/java/dev/cardigan>
  - <https://github.com/phjeltman/cardigan/tree/main/src/main/java/dev/cardigan/http>
  - <https://github.com/phjeltman/cardigan/tree/main/src/main/java/dev/cardigan/core>
  - <https://github.com/phjeltman/cardigan/tree/main/src/main/java/dev/cardigan/serdes>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/README.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/DOCUMENTATION.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/APOLOGY.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/THIRD_PARTY_NOTICES.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/http/Response.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/http/ResponseHeaders.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/http/FastRouteHandler.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/http/Router.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/core/ConnectionWriter.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/core/Http1ExchangeSequencer.java>
  - <https://raw.githubusercontent.com/phjeltman/cardigan/HEAD/src/main/java/dev/cardigan/core/Http2ResponseWriter.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cardigan.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/src/main/java/dev/cardigan/httparena/HttpArenaController.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cardigan/src/main/java/dev/cardigan/httparena/HttpArenaMain.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/ngx_http_httparena_module.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/validate.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/phjeltman/cardigan`) · [data/wave14/enrich/raw/github_com_phjeltman_cardigan.json](../../../data/wave14/enrich/raw/github_com_phjeltman_cardigan.json) (enrichment confidence 0.6)

</details>
