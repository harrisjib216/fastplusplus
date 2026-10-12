# Apache Pekko gRPC (Scala): grpc_bench unary echo vs C++ gRPC (cpp_grpc_mt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Scala` · `Apache-2.0` · 🟢 active

> Scala/Java gRPC on Pekko HTTP and Pekko Streams; out-served the stock C++ async gRPC greeter 1.27-1.73x in one grpc_bench run.

| | |
|---|---|
| **Beats** | gRPC C++ async server (cpp_grpc_mt in LesnyRumcajs/grpc_bench): the stock async greeter pattern with one completion queue per server thread, GRPC_SERVER_CPUS threads and a single pre-posted CallData per queue; main.cpp and the generated code are built with g++ 15.2.0 --std=c++20 -O3 -flto and linked with jemalloc against Debian-packaged libgrpc++, libgrpc and libprotobuf (versions and build flags not recorded). It was the fastest of the run's three C++ rows (cpp_grpc_mt, cpp_asio_grpc, cpp_grpc_st) at 1, 3 and 4 CPUs and within 0.4% of cpp_asio_grpc at 2 CPUs. |
| **Claimed result** | Discussion #559 (2026-04-23 run), scala_pekko vs cpp_grpc_mt in req/s: 1 CPU 72808 vs 57403 (1.27x); 2 CPUs 120072 vs 74574 (1.61x); 3 CPUs 141296 vs 81581 (1.73x); 4 CPUs 142375 vs 85485 (1.67x) (ratios derived from page data). Average latency at 4 CPUs 5.23 ms vs 11.28 ms. |
| **Workload** | grpc_bench complex_proto unary RPC echo (the handler puts the request's Hello message into the reply; the C++ server std::moves it), ghz 0.114.0 client with 50 connections and 1000 concurrent requests, 120 s measured after a 30 s warm-up, server capped at 1 to 4 CPUs and 4096m RAM, run at grpc_bench commit c4c93b3 (2026-04-22) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548N (16) @ 2.800GHz, 64 GB RAM, Digital Ocean dedicated server, Ubuntu 24.04.3 LTS, kernel 6.8.0-71-generic; server limited by Docker to 1, 2, 3 or 4 CPUs, ghz 0.114.0 client given 11 CPUs |
| **Compiler and flags** | Server under test at commit c4c93b3: sbtscala/scala-sbt:eclipse-temurin-23.0.1_11_1.10.7_3.6.3 build (sbt assembly), run on eclipse-temurin:23-jdk-noble with _JAVA_OPTIONS -XX:+UseParallelGC -XX:MinRAMPercentage=70 -XX:MaxRAMPercentage=70; Scala 2.13.17, Pekko 1.2.1, pekko-http 1.3.0, pekko-grpc-sbt-plugin 1.2.0. At HEAD the benchmark uses Pekko 2.0.0-M3, pekko-http 2.0.0-M1, pekko-grpc 2.0.0-M2, Scala 2.13.18 and -XX:+UseSerialGC, so the April rows do not use that configuration. Baseline cpp_grpc_mt at commit c4c93b3: FROM gcc:15.2.0, apt-get install (unpinned, at image build time) protobuf-compiler protobuf-compiler-grpc libgrpc++-dev libjemalloc-dev, then g++ --std=c++20 -O3 -flto main.cpp gen/helloworld.grpc.pb.cc gen/helloworld.pb.cc -lgrpc++ -lprotobuf -lgrpc -lgpr -lpthread -ljemalloc; only the 179-line main.cpp and the generated stubs get -O3 -flto, while the gRPC and protobuf runtime that does the measured work is the Debian package build (versions and flags not recorded by the run). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | No source gives a mechanism. Inference from the same tables: the C++ server spent more CPU per request (405.58% CPU for 85485 req/s at 4 CPUs against 270.92% for 142375 req/s for Pekko); the underlying cause is not established by the benchmark. |
| **Adoption** | 55 stars (Apache Pekko project) |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/apache/pekko-grpc) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

In grpc_bench discussion #559 (maintainer run, commit c4c93b3, Xeon Gold 6548N, server capped at 1-4 CPUs via docker --cpus, ghz 50 connections and 1000 concurrent unary echo calls, 120 s after 30 s warm-up), scala_pekko on Pekko 1.2.1 and Temurin 23 served 72808-142375 req/s against 57403-85485 req/s for the C++ async greeter built with g++ 15.2.0 -O3 -flto on Debian-packaged libgrpc++ (1.27x at 1 CPU up to 1.73x at 3 CPUs). Earlier published runs put the two within 0.89-1.15x of each other, so the size of the gap depends on the run and on a C++ baseline that is neither pinned nor tuned.

## Use it when

- You already run Pekko (or are migrating from Akka gRPC) and want gRPC endpoints that share the actor system, dispatcher and Pekko Streams backpressure for streaming RPCs.
- Unary or streaming gRPC services on 2-4 cores where throughput per container matters more than memory: in grpc_bench #559 it reached 120-142k req/s at 2-4 CPUs on a Xeon Gold 6548N, ahead of the stock C++ greeter and rust_tonic_mt.
- JVM shops that want one generated API for Scala and Java with sbt, Maven or Gradle builds.
- Services where p50/average latency under heavy concurrency matters (5.23 ms average against 11.28 ms for the C++ greeter at 4 CPUs in #559).

## Skip it when

- Memory-constrained deployments: the Pekko server averaged 450-998 MiB in #559 against 21-32 MiB for the C++ server (largely JVM heap sizing, but a JVM floor of hundreds of MiB remains).
- Tail-latency-critical paths: p99 at 4 CPUs was 22.14 ms against 19.69 ms for C++, and JIT warm-up plus GC pauses affect short-lived or bursty processes.
- Single-core containers: in other grpc_bench runs (#441 on an i9-13900KF) it trailed cpp_grpc_mt at 1 and 2 CPUs (0.89x and 0.97x), and one 1-CPU result in #475 collapsed to 5661 req/s.
- If raw JVM gRPC throughput is the goal and you are not tied to Pekko: Vert.x gRPC posted more req/s than Pekko at 1 and 2 CPUs in the same #559 run.
- Teams that need a stable 2.x API now: the repo tracks Pekko 2.0 and pekko-http 2.0 milestones, and the README warns APIs and build plugins may still change.

## How it is fast

The benchmark gives no mechanism. What the server does: requests are served by Pekko HTTP's own HTTP/2 implementation on Pekko Streams (not by gRPC C++ core or grpc-java's Netty server), entities are collected strictly and dispatched to a Future-returning handler on a fork-join dispatcher capped at the container's CPU count, all JIT-compiled on the HotSpot JVM. In the April 2026 run the C++ server burned more CPU per request (405.58% CPU for 85485 req/s at 4 CPUs against 270.92% for 142375 req/s), which points at the C++ side's library build and server pattern rather than any trick in Pekko.

## Compared with alternatives

Pick it over Armeria, Vert.x gRPC or grpc-dotnet when the service already lives in a Pekko actor system or uses Pekko Streams for streaming RPCs; for raw unary throughput on few cores Vert.x gRPC posted higher numbers in the same #559 run, and tonic gives similar req/s at a fraction of the memory.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Pekko actor and streams, Pekko HTTP (server side, HTTP/2 enabled), grpc-java grpc-netty-shaded (client side), generated protobuf classes via the sbt/Maven/Gradle plugin |
| **Minimum toolchain** | JDK 17+ (README); Scala 2.13 default, other cross-built Scala versions not listed in the README; the benchmark used Scala 2.13.17 on Temurin 23 |
| **Platforms** | any JVM platform |
| **Thread safety** | not documented in the pages read; service methods return Futures and run on the Pekko default dispatcher, so implementations must be safe for concurrent calls. |
| **Drop-in for the baseline** | partial — wire-compatible gRPC over HTTP/2, so existing clients keep working, but the C++ server must be rewritten in Scala or Java against the generated Pekko traits. |

## Gotchas

- Harness flaw on the C++ side: grpc_bench's cpp_grpc_mt keeps exactly one pre-posted RequestSayHello per completion queue and does a new/delete of CallData per RPC, whereas gRPC's own async QPS benchmark server (test/cpp/qps/server_async.cc) pre-posts 5000 request contexts per queue, so the baseline is the tutorial pattern, not gRPC C++ at its fastest.
- The C++ server links Debian-packaged libgrpc++ installed by unpinned apt-get on the gcc:15.2.0 image; that image line is built on Debian trixie (docker-library gcc 15 Dockerfile FROM buildpack-deps:trixie), whose grpc package is 1.51.1 per Debian package listings seen in search snippets, many releases behind upstream gRPC (pekko-grpc itself moved to grpc-java 1.84.2 on 2026-10-10). The exact version was not recorded by the run, so this is an inference.
- Memory figures in grpc_bench come from docker stats with -XX:MinRAMPercentage=70 -XX:MaxRAMPercentage=70 on a 4096m container, so the JVM row reflects a pre-sized heap more than its working set; tune heap flags before judging memory.
- The published win was measured with Pekko 1.2.1, pekko-http 1.3.0 and ParallelGC at grpc_bench c4c93b3; the benchmark now builds Pekko 2.0 milestones with SerialGC, and no run of that configuration is published; the 1.27-1.73x margin comes from one 120 s run per CPU count, while other runs show 0.89-1.15x.

## Known shortcomings

- Downgraded from A to B: the win (1.27-1.73x) appears only in grpc_bench #559; other runs show 0.89-1.15x; the old Pekko 1.2.1 stack was measured and uses about 50x more memory than C++. Shared reason for B: the C++ side links unpinned Debian libgrpc++, libgrpc and libprotobuf with version and flags unrecorded (only the 179-line main.cpp gets -O3 -flto), one run per CPU count, and cpp_asio_grpc sits within about 2% of cpp_grpc_mt while rust_tonic_mt also beats it, so the limit is the C++ gRPC library build, not C++ code generation.
- Enricher: crippled C++ baseline in grpc_bench: cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own test/cpp/qps/server_async.cc pre-posts 5000 per queue; it links unpinned Debian libgrpc++ (likely gRPC 1.51.1 on the gcc:15 trixie base, inferred from snippets). JVM memory rows mostly reflect heap pre-sizing (MinRAMPercentage=70 of 4096m). Vert.x gRPC beat Pekko at 1-2 CPUs in #559. The same C++ flaw applies to every grpc_bench row compared against cpp_grpc_mt.

## Caveats and trade-offs

Single run of the suite maintainer, one run per CPU count. Other published grpc_bench result threads (ratios derived from page data): #441 (i9-13900KF, 2024-04) scala_pekko/cpp_grpc_mt = 0.89, 0.97, 1.14, 1.15, 1.04, 1.04 at 1 to 6 CPUs (behind at 1 and 2 CPUs); #475 (i5-6600K, 2024-09) 0.14 (5661 req/s, apparent 1-CPU anomaly), 1.15, 1.13, 1.14 at 1 to 4 CPUs; scala_pekko is absent from #547 (the akka build failed under podman). The win is therefore real at 3 or more CPUs in three runs but small (4 to 15%) outside the April 2026 run. In #559 the Pekko row was built from the older Pekko 1.2.1 stack, not the Pekko 2.0 milestone now in the repo. The bench uses the Pekko HTTP/2 server through pekko-grpc, with the quickstart-style Greeter service. At 1 CPU Pekko used 998.48 MiB against 20.59 MiB for C++. cpu and memory come from docker stats. The Dockerfile at HEAD for the C++ side says gcc:16.1.0; the run used gcc:15.2.0. [verifier] All #559 numbers and the ratios for #441, #475 and #547 were checked against the pages. In #559 the C++ ceiling is the gRPC C++ core library rather than the app's completion-queue pattern: cpp_asio_grpc (a different C++ server design on the same libgrpc) lands within about 2% of cpp_grpc_mt at every CPU count, cpp_grpc_mt ranks 13th to 25th of 40 rows, and rust_tonic_mt (82515 to 139886 req/s) also beats it at every CPU count, so the result says more about the Debian libgrpc build on this box than about the JVM; the C++ server also ran at 405.58% CPU against a 4-CPU cap. The C++ standing dropped sharply in this run (cpp_grpc_mt was ahead of or near the JVM rows in #441 and #547), which hints at a change in the C++ image (gcc base image and distro libgrpc version) or the host, not established. The 120 s duration is below the README's recommended \~300 s for implementations that need warm-up. #475 was posted by a user (Opa-), not the maintainer; #547 gives no commit. [retier] Enricher (Pekko gRPC pass): grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own server_async.cc pre-posts 5000) and allocates per RPC; it links unpinned Debian libgrpc++ (likely 1.51.1). Every grpc_bench row compared against cpp_grpc_mt inherits this crippled baseline.

Memory: 450.71 to 998.48 MiB average for Pekko against 20.59 to 31.71 MiB for C++ in the same run. JVM warm-up and GC pauses (99% latency 22.14 ms at 4 CPUs against 19.69 ms for C++). Scala/Pekko Streams programming model.

## Maintenance

Actively maintained Apache project (commits through 2026-10-10, currently tracking Pekko and pekko-http 2.0 milestones) under Apache-2.0 and usable as a library today, but the catalogue's speed claim rests on one benchmark run against an untuned tutorial-pattern C++ server built on an unpinned distro gRPC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** grpc_bench (939 stars, MIT) is a widely used independent suite and #559 is the maintainer's run with public code at c4c93b3 (cpp_grpc_mt_bench/main.cpp and Dockerfile, scala_pekko_bench/Dockerfile and build.sbt), the CPU model and the app's g++ flags; it falls short of A because the C++ side's measured work runs in Debian-packaged libgrpc++/libgrpc/libprotobuf installed by an unpinned apt-get whose versions and build flags the run does not record (only the 179-line glue gets -O3 -flto), and the margin comes from one run per CPU count that three other published runs do not reproduce.
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's C++ entry cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own async QPS server pre-posts 5000 per queue, and it links unpinned Debian libgrpc++ (likely gRPC 1.51.1) with version and flags unrecorded, so wins over it measure a weak C++ server setup rather than the C++ gRPC stack at its best.
- **Verifier notes:** Numbers and cross-run ratios check out; downgraded A to B because the C++ gRPC runtime that does the work is an unpinned Debian package with unrecorded version and flags, and the 1.27-1.73x margin is from one run (other runs show 0.89-1.15x). Shortcomings: single run, win small or absent in other runs, old Pekko 1.2.1 stack, \~50x more memory than C++, the result reflects the gRPC C++ library build rather than C++ codegen.
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-119 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/441>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/475>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://github.com/LesnyRumcajs/grpc_bench>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/build.sbt>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/project/plugins.sbt>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/scala_pekko_bench/build.sbt>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/scala_pekko_bench/Dockerfile>
  - <https://github.com/apache/pekko-grpc>
  - <https://github.com/apache/pekko-grpc/commits>
- **Sources the enricher read:**
  - <https://github.com/apache/pekko-grpc>
  - <https://github.com/apache/pekko-grpc/commits>
  - <https://github.com/apache/pekko-grpc/issues?q=is%3Aissue%20performance>
  - <https://github.com/LesnyRumcajs/grpc_bench/tree/c4c93b3/scala_pekko_bench>
  - <https://github.com/LesnyRumcajs/grpc_bench/tree/c4c93b3/scala_pekko_bench/src/main>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/src/main/resources/application.conf>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/src/main/scala/com/example/helloworld/GreeterServer.scala>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/src/main/scala/com/example/helloworld/GreeterServiceImpl.scala>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scala_pekko_bench/build.sbt>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/grpc/grpc/master/test/cpp/qps/server_async.cc>
  - <https://github.com/docker-library/gcc/blob/master/15/Dockerfile>
  - WebSearch: Debian trixie libgrpc++-dev package version 1.51 (snippets from packages.debian.org and piuparts.debian.org)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/apache/pekko-grpc`) · [data/wave14/enrich/raw/github_com_apache_pekko_grpc.json](../../../data/wave14/enrich/raw/github_com_apache_pekko_grpc.json) (enrichment confidence 0.6)

</details>
