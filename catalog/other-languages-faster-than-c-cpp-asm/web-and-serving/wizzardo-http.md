# wizzardo-http

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `MIT` · 🟡 stale

> Small Java HTTP server and web framework on a JNI epoll core; ties C++ cinatra and lithium in TechEmpower plaintext.

| | |
|---|---|
| **Beats** | lithium and cinatra (C++) in the TechEmpower Round 22 plaintext leaderboard |
| **Claimed result** | plaintext rank 8 of 486: wizzardo-http 6,995,129 responses/s vs lithium (C++, rank 9) 6,993,976 (+0.02%, derived from page data) and cinatra (C++, rank 7) 6,998,076 (-0.04%), libsniper (C++) 6,883,107, cuehttp (C++) 6,224,825 and userver[bare] (C++) 5,974,256; a tie within noise with the top C++ entries. |
| **Workload** | TechEmpower Framework Benchmarks round 22 plaintext test (best responses per second, Dell R440 Xeon Gold with 10 GbE, 486 tests), as shown in a screenshot kept in the gnet repository's illustrations repo. |
| **Metric** | throughput |
| **Hardware** | Dell R440 Xeon Gold + 10 GbE (screenshot header). The gnet README's TechEmpower section lists 28 HT cores of Intel Xeon Gold 5120, 32 GB RAM, a dedicated Cisco 10-gigabit switch and Debian 12. |
| **Compiler and flags** | Not stated on the screenshot. TFB master (not pinned to Round 22): wizzardo-http runs on openjdk:11.0.3-jdk-slim with -Xmx2G -Xms2G -server -XX:+UseNUMA -XX:+UseParallelGC -XX:+AggressiveOpts. Its event loop is the author's native library wizzardo/epoll, whose EpollCore.c is compiled with gcc -g -Ofast -shared -fpic and called through JNI (Dockerfile-x64). lithium builds with clang++ -O3 -march=native -flto plus a PGO pass (compile.sh), and cinatra with a default CMake build at commit c9bec30. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 221 stars |
| **Last commit** | 2025-05-11 |
| **Links** | [repository](https://github.com/wizzardo/http) · [benchmark](https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg) |

## Verdict

TechEmpower Round 22 plaintext (Dell R440 Xeon Gold 5120, 10 GbE, pipelined 'Hello, World!' at up to 16,384 connections), read from a third-party screenshot. wizzardo-http, as com.wizzardo:http 0.4 on openjdk 11.0.3, ranked 8th of 486 at 6,995,129 responses/s, between C++ cinatra (6,998,076) and C++ lithium (6,993,976), and 0.3% above C libreactor (6,971,119, derived). That is a tie inside a saturated top cluster, measured with a benchmark-specific configuration that skips request-header storage and shortens the Server header.

## Use it when

- Small self-contained JSON or plaintext microservices on Linux x86-64 or aarch64, where you want a single fat jar with routing, DI and templates and few dependencies.
- High request rates of tiny keep-alive or pipelined HTTP/1.1 responses served from I/O threads, the shape the TechEmpower plaintext and JSON tests measure.
- Experimenting with JNI-based socket I/O in Java as an alternative to Netty's native epoll transport.

## Skip it when

- Anything that needs a maintained ecosystem. It has one maintainer and 221 stars, the last Maven Central release (com.wizzardo:http 0.4) dates from 2020-08-28, master is 0.5-SNAPSHOT, and TechEmpower marked the test 'broken' on 2026-02-10 (PR #10708: 'Fail in the last runs').
- macOS or Windows: off Linux it falls back to Java NIO, which the maintainer says 'might be not optimised at all'. In issue #10 it served 58,623 req/s against 616,765 for robaho's httpserver on the same Mac.
- As evidence that Java beats C++: the TechEmpower result is a tie at the top-of-table cluster (cinatra 0.04% ahead, lithium 0.02% behind), and the socket hot path is C reached over JNI.
- Copying the TechEmpower configuration (onlyCachedHeaders = true with a trimmed string cache) into production: request headers are then dropped, see gotchas.
- Blocking handlers with workersCount 0 (the TechEmpower setting): handlers run on the I/O threads, so a slow handler stalls every connection on that thread.

## How it is fast

On Linux, I/O runs through the author's wizzardo/epoll library. Its C core (EpollCore.c, gcc -Ofast, called over JNI) does accept4 with SOCK_NONBLOCK and TCP_NODELAY, edge-triggered epoll_wait, and read/write straight from direct ByteBuffers by raw address. Responses are assembled from preallocated direct buffers: cached status lines, 'Content-Length: N' for N &lt; 1024, header constants, and a Date header re-rendered once per second. They are copied with native memcpy helpers (copyInto2 to copyInto5). Request parsing interns method, version and known header strings through a byte trie (ByteTree), so a hit allocates no String, and finds line ends with a stride-2 CR/LF scan. Pipelined requests from one read are handled in a loop and flushed once. In the TechEmpower setup, handlers run directly on one I/O thread per core, with no worker pool.

## Compared with alternatives

Among the Java siblings, Netty, Undertow and Vert.x are far more mature, and firenio placed above wizzardo-http in the same Round 22 plaintext table (rank 5, 7,004,779 vs 6,995,129). Pick wizzardo-http only if you want a tiny all-in-one Linux framework (routing, DI, templates) in one jar and can live with a single maintainer; for production Java HTTP, prefer Vert.x or Netty.

## Integration

| | |
|---|---|
| **Form** | Maven/Gradle jar (com.wizzardo:http 0.4 on Maven Central) plus a per-platform JNI native library from com.wizzardo:epoll |
| **Dependencies** | com.wizzardo:epoll (native libepoll-core .so for x32, x64 and aarch64 Linux; libepoll-ssl needs OpenSSL), com.wizzardo.tools:tools, com.wizzardo:simple-websocket-client. Master pins epoll 0.3.5-SNAPSHOT and tools 0.24-SNAPSHOT from the OSSRH snapshots repository; 0.4 pins epoll 0.3.4 and tools 0.23 |
| **Minimum toolchain** | Java 8 (source/target 1.8; CI on JDK 8). Built with Gradle 6.8, whose 'compile' configuration no longer exists in Gradle 7+. The TechEmpower image used openjdk 11.0.3. |
| **Platforms** | Linux (x86, x86-64, aarch64) through native epoll; other OSes and EPOLL_DISABLED=true use the slow Java NIO fallback |
| **Thread safety** | Handlers can run concurrently on several I/O threads or a worker pool (ioWorkersCount, workersCount). Controllers are prototype-scoped and services singletons in the DI container. Thread safety of shared application state is otherwise not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark-only parsing shortcut (harness flaw). The TechEmpower app overrides initHttpPartsCache() to seed the string cache with only the HTTP method names and 'HTTP/1.1', and Config.groovy sets onlyCachedHeaders = true. In HttpHeadersReader.getValue every string missing from that cache comes back null, so no request header is ever stored: Host, Connection: close and Content-Length are all ignored. Reading the current source, an HTTP/1.0 request leaves protocol null and hits a NullPointerException in prepareKeepAlive, which becomes a 400 and a closed connection. The library default is onlyCachedHeaders = false, yet the entry is classified 'Realistic'.
- The TechEmpower config sets the server name to 'W', so responses carry 'Server: W' instead of the default 'Server: wizzardo', 7 bytes less on every response. TechEmpower's rules expect the Server header to be 'whatever is normal for the platform or framework'. Fewer bytes per response may matter in a plaintext table whose top 18 entries sit within 1.9% of each other (derived from the screenshot).
- The measured build is the 2020 0.4 release on JDK 11.0.3 with -XX:+UseParallelGC and the deprecated -XX:+AggressiveOpts, not the current master. The test no longer builds or runs in TechEmpower, so the result cannot be reproduced from TFB master.
- The I/O core is native C code (gcc -Ofast) that handles raw buffer addresses passed from Java as jlong. A bad offset or length is a native memory fault, not a Java exception.

## Known shortcomings

- TechEmpower tie at the 10 GbE cap (6,995,129 vs lithium 6,993,976; cinatra above); the event loop is the author's own C JNI library (EpollCore.c, gcc -Ofast); screenshot-only source; TFB master tags the test 'broken'.
- Harness flaw: the TFB app seeds its string cache with the methods plus 'HTTP/1.1' only and sets onlyCachedHeaders = true, so no request headers are stored (Connection and Content-Length ignored); in the current source an HTTP/1.0 request hits an NPE and returns 400; it is classified Realistic although the library default is false. The Server name is trimmed to 'W' (7 bytes less per response; the TFB rule wants the framework's normal header). The measured build is the 2020 release 0.4 on JDK 11.0.3; TFB marked it broken on 2026-02-10 (PR #10708); the macOS NIO fallback gives 58,623 vs 616,765 req/s (issue #10); the repo was renamed wizzardo/webery.

## Caveats and trade-offs

A tie, not a win. Ranks 1 to 17 of the plaintext test are within 1.5% because the 10 GbE link is the limit. C++ cinatra (rank 7) is above wizzardo-http, and lithium (rank 9) is 0.02% below. The repo README makes no benchmark claim. The numbers are read from a screenshot in panjf2000/illustrations that the gnet README attributes to TechEmpower Round 22, not from the live TechEmpower page, which was not reachable. wizzardo-http's network hot path runs through the author's C epoll library via JNI (wizzardo/epoll EpollCore.c, gcc -Ofast), so the Java entry is partly C. TFB master now tags the wizzardo-http test 'broken', and the screenshot does not show the round's commit or flags. Classes differ: wizzardo-http and lithium are 'Micro', cinatra is 'Full'. [retier] The TFB app seeds its string cache with the methods plus 'HTTP/1.1' only and sets onlyCachedHeaders = true, so no request headers are stored (Connection and Content-Length ignored); an HTTP/1.0 request hits an NPE in the current source; it is classified Realistic although the library default is false. The Server name is trimmed to 'W' (7 bytes less per response). The measured build is the 2020 release 0.4 on JDK 11.0.3; TFB marked it broken on 2026-02-10 (PR #10708); the repo was renamed wizzardo/webery.

Small Java HTTP server built on the author's own epoll library (wizzardo/epoll, JNI), so it needs a native library per platform.

## Maintenance

Stale (last commit 2025-05-11; the TechEmpower entry has been marked broken since 2026-02-10) but MIT-licensed. The last release is 0.4 from 2020, master depends on SNAPSHOT artifacts from the retired OSSRH snapshot repository, and the Linux speed depends on the author's JNI epoll native library, so treat it as a reference design rather than something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The screenshot shows independent TechEmpower plaintext numbers, but no win: wizzardo-http is at 6,995,129 responses/s, between C++ cinatra (6,998,076, above) and C++ lithium (6,993,976, below), in a test that saturates the 10 GbE link. The data comes from a third-party screenshot (the round is named only by the gnet README) because the TFB results page was not reachable. Tier B needs a win against the baseline, so C.
- **Verifier notes:** Screenshot numbers match the record (rank 8, 6,995,129 vs lithium 6,993,976 and cinatra 6,998,076; libsniper 6,883,107; cuehttp 6,224,825; userver[bare] 5,974,256). Downgraded B to C because the independent data shows parity at the network cap, not a win, and the Java framework's I/O core is native C via JNI. Shortcomings: not faster (tie at 10 GbE cap), JNI C epoll core, screenshot-only source, TFB test now tagged broken, stale repo (last commit 2025-05-11, 221 stars, MIT confirmed).
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-44 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
  - <https://raw.githubusercontent.com/panjf2000/gnet/HEAD/README.md>
  - <https://github.com/wizzardo/http>
  - <https://github.com/wizzardo/http/commits>
  - <https://raw.githubusercontent.com/wizzardo/http/HEAD/README.md>
  - <https://github.com/wizzardo/epoll>
  - <https://github.com/wizzardo/epoll/tree/master/natives>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/README.md>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/build_natives.sh>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/Dockerfile-x64>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/wizzardo-http.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C++/lithium/lithium.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C++/lithium/compile.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C++/cinatra/cinatra.dockerfile>
- **Sources the enricher read:**
  - <https://github.com/wizzardo/http>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/README.md>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/build.gradle>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/settings.gradle>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/gradle/wrapper/gradle-wrapper.properties>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/.github/workflows/gradle.yml>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/.circleci/config.yml>
  - <https://github.com/wizzardo/webery/tree/master/src/main/java/com/wizzardo/http>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/AbstractHttpServer.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpConnection.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpHeadersReader.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpStringsCache.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpServer.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpWorker.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/HttpIOThread.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/ServerDate.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/response/Response.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/request/Request.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/request/RequestReader.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/request/Header.java>
  - <https://raw.githubusercontent.com/wizzardo/webery/HEAD/src/main/java/com/wizzardo/http/framework/WebApplication.java>
  - <https://github.com/wizzardo/webery/commits/master>
  - <https://github.com/wizzardo/webery/issues?q=is%3Aissue>
  - <https://github.com/wizzardo/webery/issues/10>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/README.md>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/build.gradle>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/build_natives.sh>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/Dockerfile-x64>
  - <https://raw.githubusercontent.com/wizzardo/epoll/HEAD/src/main/c/com/wizzardo/epoll/EpollCore.c>
  - <https://repo1.maven.org/maven2/com/wizzardo/http/0.4/http-0.4.pom>
  - <https://repo1.maven.org/maven2/com/wizzardo/http/maven-metadata.xml>
  - <https://repo1.maven.org/maven2/com/wizzardo/http/0.4/>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/master/frameworks/Java/wizzardo-http>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/src/main/java/com/wizzardo/techempower/App.java>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/src/main/resources/Config.groovy>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/build.gradle>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/wizzardo-http.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/Java/wizzardo-http/config.toml>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/commits/master/frameworks/Java/wizzardo-http>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/pull/10708>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Framework-Tests-Overview>
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/wizzardo/http`) · [data/wave14/enrich/raw/github_com_wizzardo_http.json](../../../data/wave14/enrich/raw/github_com_wizzardo_http.json) (enrichment confidence 0.7)

</details>
