# firenio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `Apache-2.0` · 🔴 abandoned

> Java NIO/epoll network framework whose stripped 'http-lite' TechEmpower entry ties lithium and cinatra (C++) on plaintext.

| | |
|---|---|
| **Beats** | lithium (C++) and cinatra (C++) in the TechEmpower Round 22 plaintext leaderboard |
| **Claimed result** | TechEmpower Round 22 plaintext, as shown in a third-party screenshot: firenio-http-lite rank 5 of 486 at 7,004,779 responses/s vs cinatra (C++) 6,998,076 (rank 7, +0.10%, derived from page data), lithium (C++) 6,993,976 (rank 9, +0.15%, derived), libsniper (C++) 6,883,107 (+1.8%, derived), cuehttp (C++) 6,224,825 (1.13x, derived) and userver[bare] (C++) 5,974,256 (1.17x, derived). Against the named baselines this is a tie at the network ceiling. The full-codec 'firenio' entry is rank 34 at 5,613,390, 0.80x lithium (derived). |
| **Workload** | TechEmpower Round 22 plaintext test (HTTP pipelining, 10 GbE) for firenio-http-lite, a Java NIO/epoll based entry. |
| **Metric** | throughput |
| **Hardware** | TechEmpower Round 22 physical environment: Dell R440 servers with an Intel Xeon Gold 5120 (28 HT cores), 32 GB RAM and a dedicated Cisco 10 GbE switch (leaderboard header 'Dell R440 Xeon Gold + 10 GbE' plus the hardware block in the gnet README that embeds the screenshot) |
| **Compiler and flags** | TechEmpower frameworks/Java/firenio/firenio-http-lite.dockerfile (the directory had no commits between January 2021 and a February 2026 display-name edit, so it matches the Round 22 build): OpenJDK 11 from maven:3.6.1-jdk-11-slim, firenio-all 1.3.6 from Maven, java -server -XX:+UseNUMA -XX:+UseParallelGC -XX:+AggressiveOpts -Dlite=true -Dcore=1 -Dframe=16 -DreadBuf=512 -Dpool=true -Dlevel=1 -Dread=false -Depoll=true -Dnodelay=true -Dcachedurl=true -DunsafeBuf=true. C++ side: lithium compile.sh builds with clang++ -O3 -march=native -flto plus PGO; cinatra's dockerfile runs cmake .. with no CMAKE_BUILD_TYPE. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 364 stars |
| **Last commit** | 2021-10-12 |
| **Links** | [repository](https://github.com/firenio/firenio) · [benchmark](https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg) |

## Verdict

TechEmpower Round 22 plaintext (Dell R440, Xeon Gold 5120, 10 GbE, pipelined), read from a third-party screenshot: firenio-http-lite on OpenJDK 11 did 7,004,779 responses/s, rank 5 of 486, against cinatra (C++) 6,998,076 and lithium (C++, clang -O3 -march=native -flto with PGO) 6,993,976, a +0.10% to +0.15% tie at the network ceiling; the full-decoder 'firenio' entry did 5,613,390, 0.80x lithium (derived from page data).

## Use it when

- Studying how a JVM server reaches the 10 GbE plaintext ceiling: the TFB handler plus decode_lite is a compact, readable example of pipelined write coalescing and allocation-free request-line parsing.
- Internal services on Linux where you control the client and only need GET/POST/HEAD with fixed-length bodies over HTTP/1.1.
- Custom binary protocols on the JVM where a length-value codec and a small event-loop API are enough and you want to avoid Netty's size.
- Benchmark baselines for a JVM entry in TechEmpower-style plaintext tests.

## Skip it when

- Anything that needs a maintained HTTP stack: last commit 2021-10-12, open crash and epoll-bind issues, no releases page, and the HTTP documentation lives on firenio.com rather than in the repository.
- Realistic HTTP traffic: only GET, POST and HEAD are accepted (other methods throw ILLEGAL_METHOD, issue #65), there is no chunked Transfer-Encoding in either decoder, no HTTP/2 (issue #3) and no ALPN (issue #62).
- Public-facing servers or anything behind a proxy that rewrites headers: lite mode ignores GET bodies and matches 'Content-Length:' case-sensitively, so a lowercase header leaves the body to be parsed as the next request.
- Workloads that parse headers: the full decoder is 0.80x lithium in the same TFB round, so the C++ comparison only holds for the stripped lite path.
- Modern JDKs without testing: the code targets Java 8 and reaches into sun.misc.Unsafe, the private DirectByteBuffer(long,int) constructor and sun.nio.ch.DirectBuffer; issue #58 reports illegal reflective access warnings and behaviour on JDK 17+ is not documented.

## How it is fast

The lite HttpCodec (decode_lite) matches the method as a little-endian int, resolves '/plaintext' through a pre-built ByteTree of cached URLs, and skips GET headers entirely instead of materialising them as Strings; only Content-Length is read for POST. The TFB handler coalesces all pipelined responses of one read into a single pooled buffer and flushes it once from an event-loop task, using sun.misc.Unsafe-backed direct buffers, an optional JNI epoll binding instead of the JDK selector, per-event-loop frame caches and TCP_NODELAY. The only difference between the rank-5 'firenio-http-lite' and rank-34 'firenio' docker images is -Dlite=true and -Dcachedurl=true, so building header Strings in the full decoder alone costs about 20% of plaintext throughput (5,613,390 vs 7,004,779, derived from page data).

## Compared with alternatives

Against faf (Rust, rank 2) and wizzardo-http (Java, rank 8), which sit within 0.1% of it at the same TechEmpower plaintext ceiling, firenio offers nothing measurable; pick it only if you want the readable Java lite-codec example. For production JVM serving, Netty or Vert.x (both catalogued, maintained, full HTTP stacks) are the better choice.

## Integration

| | |
|---|---|
| **Form** | Maven jar (com.firenio:firenio-all:1.3.6) with an optional bundled JNI epoll library |
| **Dependencies** | hppc 0.8.2; slf4j-api and wildfly-openssl-java as provided (optional) dependencies; the TFB entry adds jsoniter 0.9.23 for /json |
| **Minimum toolchain** | Java 8 (pom source/target 1.8); the TFB build used OpenJDK 11 via maven:3.6.1-jdk-11-slim |
| **Platforms** | any JVM through Java NIO; the JNI epoll path is Linux only (Makefile builds a -m64 shared object with g++ -std=c++11 and no -O flag, shipped as a resource 'native.o' and loaded from a temp file) and needs direct-buffer support |
| **Thread safety** | not documented; event-loop model with one NioEventLoop per (processors x core) thread, handlers run on the channel's event loop |
| **Drop-in for the baseline** | no |

## Gotchas

- Epoll silently falls back to NIO when the native library or epoll_create fails (errors are logged only with a debug flag), so a deployment can run the slow path without noticing; the native code opens AF_INET6 sockets and fails with 'Address family not supported by protocol' on IPv4-only hosts (issue #57, open).
- decode_lite assumes CRLF line endings and an ' HTTP/1.x' suffix (url_end = l_end - 10), parses Content-Length digits without validation, and never reads headers on GET; it is a benchmark parser, not a conforming one.
- The TFB handler coalesces pipelined responses into one buffer allocated from the channel with buffer auto-expansion disabled and a pool sized at 32 MiB per event loop; the -Dframe and -Dlevel options in the dockerfile are only logged, not used.
- Issue #66 (open) reports a JVM fatal error in Unsafe_SetNativeLong with firenio-all 1.3.6 on JDK 8 under Solaris SPARC; the maintainer asked whether epoll was enabled and the thread ends without a fix.

## Known shortcomings

- Ties lithium/cinatra (+0.10-0.15%) at the TechEmpower ceiling via its lite decoder while the full-codec entry is 0.80x lithium; screenshot only (JDK 11, Xeon Gold 5120). Abandoned since 2021-10-12.
- Screenshot numbers confirmed (lite 7,004,779; full 5,613,390 responses/s). The only difference between the two TFB dockerfiles is -Dlite and -Dcachedurl, so building header Strings costs about 20% throughput. decode_lite is a benchmark parser: it never reads GET headers, matches 'Content-Length:' case-sensitively, has no chunked encoding and accepts only GET, POST and HEAD. Epoll falls back to NIO silently, the native library is built without -O, the bind is IPv6-only (issue #57), a JVM crash is open (#66), and it needs sun.misc.Unsafe and JDK internals. Abandoned since October 2021.

## Caveats and trade-offs

The rank-5 result is the lite configuration: decode_lite in firenio-codec HttpCodec.java parses the request line, looks /plaintext up in a cached URL tree and scans but does not store GET headers (only Content-Length is read for other methods); the TFB handler batches writes per event loop with pooled unsafe buffers and native epoll. It is still classified Realistic/Platform in TFB. The full-codec 'firenio' entry ranks 34 at 5,613,390, 0.80x lithium (derived from page data), so the realistic codec is slower than the C++ baselines. Plaintext at the top of the table is saturated: the first nine rows are within 0.3% and the first 19 within 6%, network and pipelining bound, so the ordering among them is noise, not a language effect. Numbers are read from a screenshot hosted in the gnet author's illustrations repo (the header does not name the round; the gnet README links it to Round 22); techempower.com was unreachable from this environment. The firenio README links the TechEmpower results but gives no figures. -XX:+AggressiveOpts is deprecated in JDK 11. Last commit 2021-10-12 (abandoned). Drogon does not appear in the top 50 screenshot. [retier] The only difference between the two TFB dockerfiles is -Dlite and -Dcachedurl, so building header Strings costs about 20% throughput (lite 7,004,779 vs full 5,613,390). decode_lite never reads GET headers, matches 'Content-Length:' case-sensitively, has no chunked encoding and accepts only GET, POST and HEAD. Epoll falls back to NIO silently, the native library is built without -O, the bind is IPv6-only (issue #57), a JVM crash is open (#66), and it needs sun.misc.Unsafe and JDK internals.

Java NIO and epoll io framework; the winning entry is the 'lite' platform-level HTTP implementation, not the full framework.

## Maintenance

Abandoned since October 2021 (7 open issues including a JVM crash and an epoll bind bug, no releases page) but Apache-2.0 and the lite codec plus TFB handler are small enough to read or copy as a pattern; not advisable as a production dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** TechEmpower is a well-known independent suite and the screenshot of its Round 22 plaintext leaderboard shows firenio-http-lite (7,004,779), cinatra, lithium and the other C++ rows from one run; it falls short of A because the numbers come from a secondary screenshot (techempower.com unreachable), and cinatra's dockerfile sets no CMake build type.
- **Verifier notes:** Numbers and metadata (Apache-2.0, 364 stars, last commit 2021-10-12, abandoned, not archived) confirmed; tier B kept, compiler/flags and hardware filled in. Record as shortcomings: tie with lithium and cinatra (+0.10-0.15%) at the network-bound plaintext ceiling; only the lite decoder reaches it, the full-codec firenio entry is 0.80x lithium; numbers only from a third-party screenshot; abandoned since 2021.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-17 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
  - <https://raw.githubusercontent.com/panjf2000/gnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/firenio-http-lite.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/pom.xml>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/src/main/java/hello/TestHttpLoadServer.java>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/lithium/compile.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/cinatra/cinatra.dockerfile>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/commits/master/frameworks/Java/firenio>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/master/frameworks/Java/firenio/src/main/java>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/master/frameworks/Java/firenio/src/main/java/hello>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-codec/src/main/java/com/firenio/codec/http11/HttpCodec.java>
  - <https://github.com/firenio/firenio>
  - <https://github.com/firenio/firenio/commits>
- **Sources the enricher read:**
  - <https://github.com/firenio/firenio>
  - <https://github.com/firenio/firenio/issues?q=is%3Aissue>
  - <https://github.com/firenio/firenio/issues/66>
  - <https://github.com/firenio/firenio/issues/57>
  - <https://github.com/firenio/firenio/tree/master/firenio-epoll>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/README.md>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/README-en.md>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio/pom.xml>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-core/pom.xml>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-epoll/Makefile>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-codec/src/main/java/com/firenio/codec/http11/HttpCodec.java>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-core/src/main/java/com/firenio/component/Native.java>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-core/src/main/java/com/firenio/Options.java>
  - <https://raw.githubusercontent.com/firenio/firenio/HEAD/firenio-core/src/main/java/com/firenio/common/Unsafe.java>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/firenio-http-lite.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/firenio.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/pom.xml>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/README.md>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Java/firenio/src/main/java/hello/TestHttpLoadServer.java>
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/firenio/firenio`) · [data/wave14/enrich/raw/github_com_firenio_firenio.json](../../../data/wave14/enrich/raw/github_com_firenio_firenio.json) (enrichment confidence 0.75)

</details>
