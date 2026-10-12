# Helidon SE (Nima WebServer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java 27 microservice framework on the virtual-thread Níma WebServer; edges nginx on HttpArena's HTTP/2 hello-world profiles only.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native) for HTTP/2; Drogon, userver, hical (C++) for the other profiles, all in the HttpArena suite |
| **Claimed result** | HttpArena (ratios derived from page data): baseline-h2-256 3,612,898 req/s (tuned) vs nginx 3,414,750 (1.06x), production variant 3,502,618 (1.03x); baseline-h2-1024 3,819,721 vs nginx 3,320,285 (1.15x), production 3,761,200 (1.13x); baseline-h2c (cleartext HTTP/2) 4,156,960 / 4,457,541 / 4,497,059 at 256 / 1024 / 4096 connections vs nginx 2,456,329 / 2,490,271 / 2,519,351 (1.69x to 1.79x); json-comp-4096 325,703 vs userver 297,311 (1.10x), proxygen-coro 262,212 (1.24x), hical 261,955 (1.24x), proxygen 243,887 (1.34x), Drogon 127,466 (2.56x), the top C/C++ rows on that profile (nginx, h2o, agensio and mongoose do not run it); pipelined-4096 (reference-only profile) 10,654,871 vs nginx 4,037,345 (2.64x), Drogon 7,801,404 (1.37x). |
| **Workload** | HttpArena profiles on one 64-core machine: baseline-h2 (HTTP/2 over TLS with 256 and 1024 connections), pipelined-4096 and json-comp-4096; Helidon SE 27 on Nima WebServer, Java 27 virtual threads, 'tuned' and 'production' variants. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (HttpArena site/data/current.json and site/content/docs/hardware/_index.md). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and the load generator (gcannon for H/1.1, h2load for HTTP/2) to 32-63,96-127 over loopback; 5 s runs, best of 3 (scripts/lib/common.sh, scripts/lib/profiles.sh, scripts/benchmark.sh). |
| **Compiler and flags** | Helidon: Oracle JDK 27 image (container-registry.oracle.com/java/jdk-no-fee-term:27), Maven 3.9.16 package of Helidon SE 27.0.0, run as java -jar app.jar with default JVM options (frameworks/helidon-tuned/Dockerfile); the tuned variant turns off HTTP/1.1 and HTTP/2 request/response-header and path validation in application.yaml, the production variant keeps it. C/C++ rows: nginx 1.31.4 with a custom handler module, Debian trixie toolchain, --with-cc-opt='-O3 -march=native -DNDEBUG', linked against the system OpenSSL (the Dockerfile's quictls comment has no matching build step); h2o clang CMake Release -march=native -mtune=native (no LTO); userver CMake Release -march=native; hical gcc-14 CMake Release -march=native -mtune=native; proxygen CMake Release from a digest-pinned proxygen base image with mimalloc preloaded; Drogon CMake Release in the unpinned drogonframework/drogon:latest image with jemalloc preloaded (HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/helidon-io/helidon) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/helidon-tuned.json) |

## Verdict

HttpArena on a Threadripper PRO 3995WX (server pinned to 32 cores / 64 threads, h2load with 64 threads and 100 streams per connection over loopback, 5 s runs, best of 3): Helidon SE 27.0.0 on Oracle JDK 27 with default JVM flags served 3.61M (tuned) and 3.50M (production) req/s on baseline-h2-256 against 3.41M for nginx 1.31.4 with a custom C handler module built -O3 -march=native, and 4.16-4.50M req/s on h2c against nginx's 2.46-2.52M. It also beat the C++ frameworks on gzip JSON (json-comp-4096, 1.10x over userver) but lost to nginx on six other shared profiles by 0.23x to 0.64x.

## Use it when

- JVM teams that want blocking, thread-per-request handler code with HTTP/1.1, HTTP/2 (TLS and h2c), gRPC and WebSocket on one server and one config file.
- HTTP/2-heavy services with many multiplexed small requests per connection: on HttpArena baseline-h2 it served 3.50-3.82M req/s, slightly above the nginx entry (3.32-3.41M) with the same 32-core server cpuset.
- Pipelined or many-streams HTTP/1.1 traffic, where it posted 10.65M req/s on pipelined-4096 (reference-only profile) against nginx's 4.04M.
- Gzip-compressed JSON APIs, where it led the C++ frameworks that run json-comp-4096 (325,703 req/s vs userver 297,311) with comparable compressed sizes (about 1,337 vs 1,358-1,393 bytes per response, derived from bandwidth over req/s).

## Skip it when

- Plain HTTP/1.1 keep-alive at high connection counts: baseline-4096 1.69M req/s vs nginx 3.28M (0.52x), and limited-conn-4096 0.61M vs 2.63M (0.23x).
- TLS HTTP/1.1, static files and h2c JSON: json-tls 0.70M vs nginx 1.31M, static-tls 0.33M vs 0.72M, static-h2 0.28M vs 0.80M, json-h2c 1.09M vs 1.73M; the fastest C/C++ HTTP/2 stacks (h2o 16.1M, agensio 14.7M, proxygen 5.85M on baseline-h2-256) are 1.6x to 4.5x ahead.
- Memory-constrained hosts: peak memory was 10.5-28.2 GiB on the h2/h2c rows (default JVM heap sizing, no -Xmx in the Dockerfile) vs 3.5-3.7 GiB for nginx and 104-288 MiB for proxygen.
- Tail-latency-sensitive endpoints: p99 at baseline-h2-1024 was 297.28 ms (tuned) vs nginx 151.79 ms, and at json-comp-4096 276.30 ms vs userver 28.70 ms.
- Short-lived processes, serverless or anything that cannot use JDK 27: Helidon 27 requires Java 27, and JVM start-up and JIT warm-up are outside the measured windows.

## How it is fast

Níma is written for Java virtual threads: blocking socket I/O per connection and request, with the JDK parking virtual threads on I/O instead of an event-loop and callback stack (README: 'high throughput of a reactive server with the simplicity of thread-per-request'). The HTTP/2 layer advertises 8192 concurrent streams and a 1 MiB initial window by default. The benchmark entry adds an 8192 accept backlog, zero read/connect timeouts and, in the tuned variant, turns off configurable header, prologue and path validation. JSON uses helidon-json binding and gzip uses java.util.zip.GZIPOutputStream, which calls the JDK's native zlib.

## Compared with alternatives

Pick Helidon over the event-loop JVM siblings (Eclipse Vert.x, Quarkus on Vert.x/Netty, Netty, Undertow) when you want blocking thread-per-request code on virtual threads with HTTP/2 and gRPC built in; for raw numbers on the same suite, Vert.x posted more on pipelined-4096 (11.78M vs 10.65M) and Quarkus more on baseline-h2-256 (4.67M vs 3.61M, separate runs), and Kestrel is the .NET counterpart.

## Integration

| | |
|---|---|
| **Form** | module (Maven artifacts io.helidon.webserver:helidon-webserver, helidon-webserver-http2, -grpc, -websocket; parent io.helidon.applications:helidon-se 27.0.0) |
| **Dependencies** | Helidon common, config and webserver modules; JDK 27 standard library (TLS from configured PEM key and certificate); no native libraries |
| **Minimum toolchain** | JDK 27 (README: 'Java 27 is required to use Helidon 27'); Maven 3.8.0+ to build Helidon itself |
| **Platforms** | any platform with a JDK 27 build; benchmarked on Linux x86-64 (Threadripper PRO 3995WX) in Docker |
| **Thread safety** | Each request runs on its own virtual thread (thread-per-request model per the README); handler instances are shared across requests, so handler state must be thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The tuned entry disables validate-request-headers, validate-response-headers and validate-path for HTTP/1.1 and HTTP/2 plus validate-prologue for HTTP/1.1; all default to true in Helidon (HttpConfigBlueprint warns that turning off response validation 'can allow invalid response header values to be written'). The effect is within run noise: the default-validation production variant was faster than tuned on all three baseline-h2c rows (4.21M/4.69M/4.54M vs 4.16M/4.46M/4.50M) and only 1.6-3.1 percent behind on baseline-h2, so the production numbers (3.50M and 3.76M vs nginx 3.41M and 3.32M, 1.03x and 1.13x) are the ones to quote.
- Harness anomaly behind the largest ratio: the nginx entry's cleartext h2c rows (2.46-2.52M req/s) are 25-28 percent below its own HTTP/2-over-TLS rows (3.32-3.41M), while proxygen, agensio and Helidon all run h2c at or above their TLS rate. nginx's port-8082 h2c server block lacks the explicit http2_max_concurrent_streams and server-level keepalive_requests tuning of its 8443 TLS block; the cause was not established, but the 1.69-1.79x h2c lead is measured against an nginx h2c path that underperforms the same build's TLS path.
- Margins on baseline-h2-256 (1.03-1.06x) are smaller than the spread between Helidon's own tuned and production runs, rows come from 5 s runs with best-of-3 selection (which also discards JIT warm-up), and the Helidon (October 2026) and nginx (August 2026) rows were recorded in separate runs. On the wire Helidon's h2 responses averaged about 61 bytes vs nginx's 82 (bandwidth over req/s, derived from page data), so the per-response header work is not identical.
- Both HttpArena Helidon entries are maintained by Helidon developer tomas-langer (vendor-tuned submissions), static files in the tuned entry go through a custom handler serving precompressed .br/.gz variants instead of Helidon's static-content feature (which the production entry uses), and async-db uses blocking JDBC with HikariCP rather than an async driver (documented divergence).

## Known shortcomings

- HttpArena (Threadripper PRO 3995WX): beats nginx only on h2 and h2c (1.69-1.79x) and the reference-only pipelined row; loses to nginx 0.23-0.64x on six other profiles; h2o, agensio, proxygen and proxygen-coro beat it on h2. The tuned entry is vendor-maintained (tomas-langer) with header validation off; rows come from separate runs (Oct vs Aug 2026).
- HttpArena flaw: nginx's h2c rows (2.46-2.52M) sit 25-28% below nginx's own TLS h2 rows (3.32-3.41M) while every other server runs h2c at or above TLS, so the 1.69-1.79x h2c lead is inflated. The production variant (validation on) beats the tuned one on all three h2c rows, so the tuning is noise; quote production 1.03x/1.13x on h2. Memory 10.5-28.2 GiB against nginx's 3.5-3.7; json-comp p99 276 ms against userver's 28.7 ms.

## Caveats and trade-offs

Narrow win. Against nginx, Helidon is ahead only on baseline-h2 (1.06x to 1.15x), baseline-h2c (1.69x to 1.79x) and the reference-only pipelined profile; it is behind nginx on baseline-4096 (0.52x), limited-conn-4096 (605,487 vs 2,626,297, 0.23x), json-tls-4096 (0.53x), json-h2c (1,087,863 vs 1,730,838, 0.63x), static-h2 (0.32x) and static-tls (0.45x). nginx's HTTP/2 path is the slowest C/C++ HTTP/2 stack on the board: at baseline-h2-256 h2o (16,106,978), agensio (14,744,015), proxygen (5,845,844) and proxygen-coro (5,185,268) are all ahead of Helidon (0.22x to 0.70x), and agensio and proxygen also lead on h2c. The json-comp win is over C++ frameworks only; Helidon gzips through java.util.zip GZIPOutputStream, which calls the JDK's native zlib, so compression is C code on both sides. The tuned entry disables header and path validation for the benchmark (the production variant keeps it and still edges nginx on h2). Both Helidon entries are maintained in HttpArena by Helidon developer tomas-langer, so they are vendor-tuned submissions run by the suite. Results files carry no dates; git history shows helidon-tuned.json last changed 2026-10-08/10 (Helidon 27.0.0 upgrade) and nginx.json 2026-08-30, so rows come from separate runs on the same machine. 5 s runs, best of 3, server limited to 32 of 64 cores. The Helidon README states no benchmark numbers. [retier] nginx's h2c rows (2.46-2.52M) sit 25-28% below nginx's own TLS h2 rows (3.32-3.41M) while every other server runs h2c at or above TLS, so the 1.69-1.79x h2c lead is inflated. The production variant (validation on) beats the tuned one on all three h2c rows, so the tuning is noise; quote production 1.03x/1.13x on h2. Memory 10.5-28.2 GiB against nginx's 3.5-3.7; json-comp p99 276 ms against userver's 28.7 ms.

JVM startup, warm-up and heap are not part of the throughput figure; Helidon 27 needs Java 27 for the virtual-thread server.

## Maintenance

Actively maintained Oracle-led project (Apache-2.0, 3.8k stars, 5,057 commits, last commit 2026-10-11, 585 open issues) and safe to adopt, but the speed claim is narrow: it beats nginx only on HTTP/2 hello-world and pipelined profiles in one vendor-tuned suite entry, and loses to the fastest C/C++ HTTP/2 servers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A on the HttpArena precedent (actix, cardigan, dusty, libxev, ntex): every quoted number matches site/data/results/helidon-tuned.json, helidon-production.json and the sibling nginx/userver/hical/drogon JSON files; the code is public (frameworks/helidon-tuned/{Dockerfile,pom.xml,src/main/java/com/httparena/\*.java,src/main/resources/application.yaml}, frameworks/nginx/{Dockerfile,nginx.conf}, scripts/benchmark.sh, scripts/lib/profiles.sh), JDK and nginx build flags are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json.
- **Verifier notes:** All quoted numbers verified and tier raised to A on the HttpArena precedent (CPU model published in current.json). Shortcomings to record: beats nginx only on h2/h2c and the reference-only pipelined profile while losing 0.23x-0.64x on six other shared profiles; h2o, agensio, proxygen and proxygen-coro (C/C++) beat it on h2, the record's caveats omitted proxygen; json-comp win is over C++ frameworks with zlib on both sides; vendor-maintained tuned entry with validation off; cross-run rows (Oct vs Aug 2026). Metadata confirmed: Apache-2.0, 3.8k stars, last commit 2026-10-11, not a fork, not archived.
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-43 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/helidon-tuned.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/helidon-production.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen-coro.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/java/com/httparena/Main.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/java/com/httparena/JsonHandler.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/resources/application.yaml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-production/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/userver/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/hical/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/proxygen/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data/results>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/helidon-tuned.json>
  - <https://github.com/helidon-io/helidon>
  - <https://github.com/helidon-io/helidon/commits>
- **Sources the enricher read:**
  - <https://github.com/helidon-io/helidon>
  - <https://raw.githubusercontent.com/helidon-io/helidon/HEAD/README.md>
  - <https://raw.githubusercontent.com/helidon-io/helidon/HEAD/webserver/http2/src/main/java/io/helidon/webserver/http2/Http2ConfigBlueprint.java>
  - <https://raw.githubusercontent.com/helidon-io/helidon/HEAD/http/http/src/main/java/io/helidon/http/HttpConfigBlueprint.java>
  - <https://github.com/helidon-io/helidon/issues?q=is%3Aissue+http2+performance>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/pom.xml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/java/com/httparena/Main.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/java/com/httparena/JsonHandler.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/java/com/httparena/BaselineHandler.java>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-tuned/src/main/resources/application.yaml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-production/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-production/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/helidon-production/src/main/resources/application.yaml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/helidon-tuned.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/helidon-production.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen-coro.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/tools/h2load.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/helidon-io/helidon`) · [data/wave14/enrich/raw/github_com_helidon_io_helidon.json](../../../data/wave14/enrich/raw/github_com_helidon_io_helidon.json) (enrichment confidence 0.75)

</details>
