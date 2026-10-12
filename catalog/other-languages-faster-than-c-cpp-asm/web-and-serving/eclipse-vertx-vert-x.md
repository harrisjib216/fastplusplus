# Eclipse Vert.x (HttpArena vertx entry)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `EPL-2.0 OR Apache-2.0` · 🟢 active

> JVM event-loop HTTP toolkit on Netty; beats some C++ servers on HttpArena but trails nginx, h2o and mongoose on scored profiles.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, ./configure --with-cc-opt='-O3 -march=native -DNDEBUG', quictls TLS); h2o, mongoose, libreactorng, libioma (C) and Drogon, userver, proxygen, agensio, cutelyst (C++) rows in the same suite |
| **Claimed result** | pipelined-4096 (reference-only profile): 11,782,768 req/s vs nginx 4,037,345 (2.92x), h2o 4,938,603 (2.39x), agensio (C++) 4,958,241 (2.38x), hical (C++) 4,851,267 (2.43x), Drogon 7,801,404 (1.51x), cutelyst 10,167,331 (1.16x), proxygen 1,857,311 (6.34x), userver 1,395,512 (8.44x); libreactorng 43,424,448 (0.27x) is far ahead. async-32000: 1,859,046 vs Drogon 143,001 (13.0x), userver 408,981 (4.55x), cutelyst 761,563 (2.44x), hical 1,682,305 (1.11x), but mongoose 2,668,972 (0.70x). baseline-4096: 1,994,369 vs userver 949,125 (2.10x), Drogon 2,022,710 (0.99x), proxygen 2,128,172 (0.94x), cutelyst 2,153,860 (0.93x), but nginx 3,284,513 (0.61x), h2o 3,641,609 (0.55x), mongoose 3,707,598 (0.54x), libreactorng 4,377,377 (0.46x). limited-conn-4096: 602,586 vs nginx 2,626,297 (0.23x), behind every C and C++ entry. json-tls-4096: 601,618 vs nginx 1,313,755 (0.46x), h2o 1,229,462 (0.49x), mongoose 1,102,964 (0.55x), ahead of Drogon 253,055 (2.38x), cutelyst 326,846 (1.84x), hical 549,765 (1.09x), userver 562,062 (1.07x). json-comp-4096: 256,544 vs Drogon 127,466 (2.01x), proxygen 243,887 (1.05x), hical 261,955 (0.98x), userver 297,311 (0.86x). static-tls-1024: 195,103 vs nginx 720,869 (0.27x). All ratios derived from page data. |
| **Workload** | HttpArena profiles for the Vert.x 5.1.6 entry (vertx-core and vertx-web on Netty, one ServerVerticle instance per available processor sharing port 8080, Router API, JsonObject serialization, server-side gzip via setCompressionSupported; JDK 21, G1GC; pom.xml declares no Netty native-epoll dependency, so the JDK NIO transport is used (inferred)): 16x pipelined HTTP/1.1 at 4096 connections (reference-only, not in the composite score), baseline-4096, limited-conn-4096 (reconnect every 10 requests), json-tls-4096, json-comp at 4096 and 16384, static-tls-1024 and async-32000 (GET /delay/10 over 32,000 held connections). |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (64 cores / 128 threads), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, undated, describes the machine now). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and the load generator (gcannon for HTTP/1.1 and WebSocket, wrk for json-tls and static-tls) runs on CPUs 32-63,96-127 of the same machine over loopback (scripts/lib/profiles.sh, scripts/lib/common.sh); each row is the best of 3 runs of 5 s against one container (scripts/benchmark.sh, RUNS=3). |
| **Compiler and flags** | Vert.x 5.1.6 (vertx-core, vertx-web), maven.compiler.release 21, built with maven:3.9-eclipse-temurin-21 and run on eclipse-temurin:21-jre with java -server -XX:+UseG1GC -XX:+AlwaysPreTouch -Dvertx.disableDnsResolver=true (frameworks/vertx/Dockerfile, pom.xml); JIT, so no -O level to match. C side: nginx 1.31.4 with a custom C handler module, --with-cc-opt='-O3 -march=native -DNDEBUG'; mongoose 7.23 gcc-14 -O3 -march=native -flto; libreactorng gcc -O3 -march=native; h2o clang Release -march=native; C++ entries CMake Release. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 14.7k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/eclipse-vertx/vert.x) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vertx.json) |

## Verdict

HttpArena (Vert.x 5.1.6 with vertx-web on JDK 21 G1 vs nginx 1.31.4 -O3 -march=native with a custom C handler, plus h2o, mongoose, libreactorng and C++ entries; Threadripper PRO 3995WX, server on 32 cores / 64 threads, best of 3 x 5 s runs) shows Vert.x ahead of C only on the reference-only pipelined-4096 row (11.78M vs nginx 4.04M req/s, but 0.27x libreactorng) and ahead of most C++ entries on async-32000 (1.86M vs Drogon 0.14M), while it runs at 0.23x to 0.61x of nginx on the scored baseline, limited-conn, json-tls and static-tls rows.

## Use it when

- JVM services that must hold tens of thousands of mostly idle or slow connections (long polls, delayed responses): HttpArena async-32000 shows 1.86M req/s against Drogon 143K and userver 409K.
- Pipelined or high-request-rate HTTP/1.1 APIs on a many-core box where a Java stack is required and C/C++ is not an option.
- Teams that want Netty-level throughput with routing, JSON and TLS already wired, instead of hand-writing Netty channel pipelines.
- Gzip JSON APIs, where the json-comp-4096 row (256,544 req/s) is level with hical (0.98x) and proxygen (1.05x), behind userver (0.86x) and twice Drogon's.

## Skip it when

- As a replacement for nginx, h2o or mongoose on plain HTTP/1.1, TLS or static files: 0.46x to 0.61x of them on baseline-4096 and json-tls-4096 and 0.27x of nginx on static-tls-1024.
- Short-lived connections: limited-conn-4096 (reconnect every 10 requests) reaches 602,586 req/s vs 2.4M to 2.7M for nginx, h2o, mongoose, hical and libreactorng, while using only 3,255% CPU of the 64 threads (the others use 5,448% to 6,644%), which points to connection setup rather than request handling as the limit (inferred).
- Memory- or CPU-constrained hosts: 2.4 GiB resident when nearly idle (latency-10k) vs 50 to 73 MiB for hical, mongoose, libreactorng and Drogon; 30.3 us CPU per request at a paced 1M req/s vs 21.0 to 22.5 us for libreactorng, mongoose and hical (Drogon 32.1 us); on 8 logical CPUs it held only 75% of a 500K req/s target (2.48 s average latency) where libreactorng held 99.8%.
- Workloads that cannot tolerate JIT warm-up or GC pauses: HttpArena reports the best of three 5 s runs, so cold-start cost is not in the numbers.
- HTTP/2-heavy services expecting the 5.0 fast path: open bug #6143 reports a 5-8% h2c regression in 5.1.0, and the maintainer plans to move HTTP/1.1 onto the same generic path, accepting possibly worse raw performance.

## How it is fast

Each verticle instance is pinned to one Netty event loop and all instances share the listening port, so request handling is lock-free per connection and needs no thread per request; long waits (the /delay test) are event-loop timers, so 32,000 pending requests cost memory rather than threads. HTTP/1.1 parsing and encoding come from Netty's codec (netty-codec-http). The HotSpot JIT compiles the hot path after warm-up; the HttpArena entry also returns minimal 66-byte responses (status line, content-type, content-length, body, no Date or Server header; derived from 741.43 MiB/s divided by 11,782,768 req/s), which helps most on the pipelined test.

## Compared with alternatives

Pick Vert.x over raw Netty when you want routing, JSON and TLS without writing channel handlers, and over Quarkus (which runs on Vert.x) when you want the toolkit without a full framework on top; on the same HttpArena suite actix-web (2.78M), the tokio entry (4.19M) and every C entry post higher baseline-4096 numbers than its 1.99M, so choose Vert.x for the JVM ecosystem, not for raw speed.

## Integration

| | |
|---|---|
| **Form** | Maven/Gradle jars (io.vertx:vertx-core, vertx-web) |
| **Dependencies** | Netty (common, buffer, transport, handler, codec-http/http2/http3, resolver) and jackson-core; jackson-databind and the native transports (epoll, io_uring, kqueue) are optional and must be added explicitly |
| **Minimum toolchain** | Java 11 for Vert.x 5 (build toolchains JDK 11 and 21); the HttpArena entry uses JDK 21 (eclipse-temurin:21) |
| **Platforms** | any JVM platform; native epoll and io_uring on Linux, kqueue on BSD/macOS, JDK NIO elsewhere (the HttpArena entry ships no native transport jar, so it ran on NIO; inferred from its pom.xml) |
| **Thread safety** | Each verticle's handlers run on its own event loop thread and must not block; a blocking call stalls every connection on that loop |
| **Drop-in for the baseline** | no |

## Gotchas

- HttpArena's pipelined win partly reflects response size: its /pipeline check only requires the body 'ok' and Content-Type text/plain, and the Vert.x entry sends 66-byte responses with no Date or Server header against about 142 bytes for nginx (derived from bandwidth divided by req/s); the profile is reference-only and libreactorng (C) is 3.7x faster there anyway.
- Memory numbers are partly configuration: the Dockerfile runs G1 with -XX:+AlwaysPreTouch and no -Xms or -Xmx, so the resident size reflects pre-touched default-sized heap as much as working set (inferred); the reported 4.8 to 16.9 GiB rows should not be read as a minimum.
- The measured release is 5.1.6; 5.1.10 and 5.2.1 were tagged on 2026-10-07, so current releases may differ, and the latency-500k-8cpu row (rate_ratio 0.75) is one the harness itself flags as not comparable on CPU because the offered rate was not held.
- Cross-run comparison: the Vert.x, nginx and mongoose result files were written on different dates (2026-09-06, 2026-08-30, 2026-09-21 per the verifier), so small gaps (for example json-comp vs hical, 0.98x) are within run-to-run noise.

## Known shortcomings

- HttpArena: wins over C only on the reference-only pipelined row and async-32000 (mongoose ahead there); responses are 62.9 B vs nginx's 135.4 B, so the pipelined ratio is inflated; memory 4.8-16.9 GiB; 0.22-0.61x of nginx on the scored rows; built on Netty (listed, wave 14); JIT, so no matched optimisation level; best of 3 runs.
- HttpArena pipelined responses are exactly 66 bytes with no Date or Server header (derived from bandwidth over req/s; validate.sh checks only body and Content-Type). limited-conn uses only 3,255% CPU against 5,448-6,644% for the C entries, which points to connection setup as the limit (inferred). latency-1m costs 30.3 us per request against 21.0-22.5 for libreactorng, mongoose and hical; latency-500k-8cpu held only rate_ratio 0.75, a row the harness itself flags as not comparable. Memory figures are inflated by -XX:+AlwaysPreTouch with no -Xmx. Open bug #6143: 5-8% HTTP/2 slowdown in 5.1.0; measured 5.1.6, current 5.2.1. HttpArena prices are integers, so getLong is correct.

## Caveats and trade-offs

Not faster than C on HttpArena's scored HTTP/1.1 and TLS profiles: 0.46x to 0.61x of nginx, h2o and mongoose on baseline-4096 and json-tls-4096, 0.22x to 0.23x on limited-conn-4096, 0.27x of nginx on static-tls. The wins over C are pipelined-4096, which HttpArena marks reference-only (excluded from the composite score), where nginx trails libreactorng 10x, and async-32000 (C++ only except mongoose, which is ahead); the harness notes that the async result depends on the load generator's thread count, so it is not the server's alone (scripts/lib/common.sh). Vert.x writes 62.9 bytes per response vs nginx 135.4, hical 141.1, Drogon 130.7 and libreactorng 106.2 (derived from page data, bandwidth divided by req/s): the entry sends only content-type and content-length (ServerVerticle.java), so part of the pipelined margin is smaller responses. Memory is 4.8 to 8.0 GiB on the HTTP/1.1 and TLS rows and 16.9 GiB on async-32000, against nginx 3.5 GiB, h2o 69 to 308 MiB, libreactorng 105 to 175 MiB and mongoose 178 to 495 MiB (page data). Each row is the best of 3 runs of 5 s against one running container, so JIT warm-up is mostly absorbed by the first run rather than included in the reported number. Rows come from separate runs (vertx.json last written 2026-09-06, nginx.json 2026-08-30, mongoose.json 2026-09-21, per git history). The C and C++ competitor entries are minimal hand-written handlers, not tuned production configurations. The Vert.x README makes no performance claim; BENCHMARKING.md only describes JMH microbenchmarks without numbers. Vert.x runs on Netty (Netty is a separate wave-14 record), and Quarkus (already verified A in wave 14) runs on Vert.x. [retier] HttpArena pipelined responses are exactly 66 bytes with no Date or Server header (validate.sh checks only body and Content-Type) against about 142 bytes for nginx. limited-conn uses only 3,255% CPU against 5,448-6,644% for the C entries (connection setup as the limit, inferred); latency-1m costs 30.3 us per request against 21.0-22.5 for libreactorng, mongoose and hical; latency-500k-8cpu held only rate_ratio 0.75, which the harness flags as not comparable. Memory figures are inflated by -XX:+AlwaysPreTouch with no -Xmx. Open bug #6143: 5-8% HTTP/2 slowdown in 5.1.0; measured 5.1.6, current 5.2.1.

JVM startup and warm-up, heavy memory (HttpArena shows 4.8 GiB on baseline-4096 and 16.9 GiB on async-32000 against 69 MiB to 3.5 GiB for the C entries on pipelined-4096), GC pauses; an event-loop model that must not block.

## Maintenance

Very active (tags 5.2.1, 5.1.10 and 4.5.35 on 2026-10-07, 14.7k stars), dual EPL-2.0/Apache-2.0, and a mature production toolkit; its catalogue value is as a fast JVM option, not as a C/C++ replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/vertx.json and the sibling nginx, h2o, mongoose, libreactorng, drogon, cutelyst, agensio, proxygen and userver JSON files in MDA2AV/HttpArena; the code is public (frameworks/vertx/{Dockerfile,pom.xml,src/main/java/httparena/ServerVerticle.java}, frameworks/nginx/Dockerfile, scripts/benchmark.sh, scripts/lib/profiles.sh), JVM options and C flags are in the Dockerfiles, and the CPU (Threadripper PRO 3995WX) is in site/data/current.json, the HttpArena tier-A precedent (cardigan, helidon, quarkus).
- **Verifier notes:** All numbers verified; tier A on the HttpArena precedent. Corrections: Vert.x 5.1.6; rows are best of 3 runs and JIT warm-up is largely discarded; memory is 1.4x-2.3x nginx and 30x-100x h2o/libreactorng/mongoose rather than uniformly an order of magnitude above C; responses are about half nginx's size. Shortcomings to record: only wins over C on the reference-only pipelined row; 0.22x-0.61x of nginx on scored H/1.1, TLS and static rows; smaller responses inflate pipelined ratio; high memory; cross-run rows.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-101 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vertx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/src/main/java/httparena/Main.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/src/main/java/httparena/ServerVerticle.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/vertx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/vertx>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/eclipse-vertx/vert.x>
  - <https://github.com/eclipse-vertx/vert.x/commits>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/BENCHMARKING.md>
- **Sources the enricher read:**
  - <https://github.com/eclipse-vertx/vert.x>
  - <https://github.com/eclipse-vertx/vert.x/releases>
  - <https://github.com/eclipse-vertx/vert.x/tags>
  - <https://github.com/eclipse-vertx/vert.x/issues?q=is%3Aissue%20state%3Aopen%20performance>
  - <https://github.com/eclipse-vertx/vert.x/issues/6143>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/README.md>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/eclipse-vertx/vert.x/HEAD/vertx-core/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/src/main/java/httparena/Main.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vertx/src/main/java/httparena/ServerVerticle.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vertx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/validate.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/generate_dataset.py>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/data/dataset.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/scripts>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/eclipse-vertx/vert.x`) · [data/wave14/enrich/raw/github_com_eclipse_vertx_vert_x.json](../../../data/wave14/enrich/raw/github_com_eclipse_vertx_vert_x.json) (enrichment confidence 0.8)

</details>
