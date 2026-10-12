# Armeria gRPC server (Java): grpc_bench unary echo vs C++ gRPC (cpp_grpc_mt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> JVM microservice framework (Netty-based) whose gRPC server out-served the stock gRPC C++ async server at 2-4 CPUs in one grpc_bench run.

| | |
|---|---|
| **Beats** | gRPC C++ async server (cpp_grpc_mt in LesnyRumcajs/grpc_bench): the stock async greeter pattern with one completion queue per server thread, GRPC_SERVER_CPUS threads and a single pre-posted CallData per queue; main.cpp and the generated code are built with g++ 15.2.0 --std=c++20 -O3 -flto and linked with jemalloc against Debian-packaged libgrpc++, libgrpc and libprotobuf (versions and build flags not recorded). It was the fastest of the run's three C++ rows (cpp_grpc_mt, cpp_asio_grpc, cpp_grpc_st) at 1, 3 and 4 CPUs and within 0.4% of cpp_asio_grpc at 2 CPUs. |
| **Claimed result** | Discussion #559 (2026-04-23 run), java_armeria vs cpp_grpc_mt in req/s: 1 CPU 56315 vs 57403 (0.98x, C++ ahead); 2 CPUs 95471 vs 74574 (1.28x); 3 CPUs 134838 vs 81581 (1.65x); 4 CPUs 140386 vs 85485 (1.64x) (ratios derived from page data). Average latency at 4 CPUs 5.25 ms vs 11.28 ms; average CPU 330.65% vs 405.58% at 4 CPUs. |
| **Workload** | grpc_bench complex_proto unary RPC echo (the handler puts the request's Hello message into the reply; the C++ server std::moves it), ghz 0.114.0 client with 50 connections and 1000 concurrent requests, 120 s measured after a 30 s warm-up, server capped at 1 to 4 CPUs and 4096m RAM, run at grpc_bench commit c4c93b3 (2026-04-22) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548N (16) @ 2.800GHz, 64 GB RAM, Digital Ocean dedicated server, Ubuntu 24.04.3 LTS, kernel 6.8.0-71-generic; server limited by Docker to 1, 2, 3 or 4 CPUs, ghz 0.114.0 client given 11 CPUs |
| **Compiler and flags** | Server under test (Dockerfile at c4c93b3): eclipse-temurin:23-jdk-noble, JAVA_OPTS -XX:+UseG1GC -XX:MinRAMPercentage=70 -XX:MaxRAMPercentage=70 -Dcom.linecorp.armeria.validateHeaders=false; armeria and armeria-grpc 1.20.3 with protoc-gen-grpc-java 1.58.0 and protoc 3.21.5, built by gradlew installDist; HelloWorldServer.java calls disableDateHeader() and disableServerHeader() and restricts serialization to PROTO. Baseline cpp_grpc_mt at commit c4c93b3: FROM gcc:15.2.0, apt-get install (unpinned, at image build time) protobuf-compiler protobuf-compiler-grpc libgrpc++-dev libjemalloc-dev, then g++ --std=c++20 -O3 -flto main.cpp gen/helloworld.grpc.pb.cc gen/helloworld.pb.cc -lgrpc++ -lprotobuf -lgrpc -lgpr -lpthread -ljemalloc; only the 179-line main.cpp and the generated stubs get -O3 -flto, while the gRPC and protobuf runtime that does the measured work is the Debian package build (versions and flags not recorded by the run). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | No source gives a mechanism (the grpc_bench README and discussion only report numbers). Inference from the same tables: at 4 CPUs the C++ server used 405.58% CPU for 85485 req/s while Armeria used 330.65% for 140386 req/s, so the gap is cost per request, not idle CPU; the cause (gRPC C++ completion-queue overhead against Netty event loops and JIT-compiled code) is not established. |
| **Adoption** | 5.1k stars |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/line/armeria) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

In grpc_bench run #559 (maintainer, commit c4c93b3, 2026-04-23, Xeon Gold 6548N, server Docker-capped at 1-4 CPUs and 4 GiB, ghz 0.114.0 client on 11 CPUs, 50 connections and 1000 concurrent complex_proto unary echoes, 120 s after a 30 s warm-up, one run per setting), Armeria 1.20.3 on Temurin 23 with G1GC served 0.98x, 1.28x, 1.65x and 1.64x the req/s of cpp_grpc_mt (g++ 15.2.0 -O3 -flto glue over Debian-packaged libgrpc++) at 1, 2, 3 and 4 CPUs. Three other published runs (#441, #475, #547) have Armeria at 0.03-1.02x of the same C++ server, so the win is specific to this run's C++ build and host.

## Use it when

- JVM shops that already run grpc-java and want one server for gRPC, gRPC-Web, Protobuf-JSON, Thrift and REST on a single port, with throughput at or slightly above plain grpc-java (run #559: 0.98-1.06x the grpc-java G1GC row).
- Small unary RPCs with non-blocking handlers on 2-4 cores, where the event-loop-inline execution avoids a thread hop.
- Teams that need an off-the-shelf gRPC server with gRPC-Web for browsers, unframed JSON access and server reflection, without an Envoy sidecar for gRPC-Web translation.
- Services where heap memory of hundreds of MiB is acceptable and JIT warm-up can be absorbed before traffic.

## Skip it when

- Memory-constrained deployments: run #559 shows 570-679 MiB average for Armeria against 21-32 MiB for the C++ server (about 20-28x).
- Tail-latency-sensitive single-core services: at 1 CPU Armeria matched the C++ throughput but its p90 was 58.18 ms against 19.93 ms and p99 65.14 ms against 21.81 ms; at 2 CPUs its p99 was still worse (46.85 vs 39.43 ms) despite 1.28x the throughput.
- Handlers that block (JDBC, file I/O, synchronous HTTP): service code runs on the event loop by default, so blocking stalls every connection on that loop unless @Blocking or useBlockingTaskExecutor(true) is used.
- Large or complex request messages: issue #5152 (open since 2023-08) reports p95 rising from about 100 ms on raw grpc-java to about 300 ms on Armeria for \~500 KB requests at 10-12K QPS, traced to deserialization on the I/O thread.
- When the fastest JVM gRPC server is the goal: in the same run Vert.x gRPC served 1.78x Armeria's req/s at 1 CPU and Pekko gRPC 1.29x.

## How it is fast

Armeria's GrpcService runs its own gRPC framing on Armeria's Netty HTTP/2 stack (the grpc module depends on grpc-core, grpc-stub and grpc-protobuf but not grpc-netty), and, unlike upstream grpc-java, it runs service logic directly on the event-loop thread rather than handing each call to a separate executor (documented under 'Blocking service implementation'). No source attributes the grpc_bench margin over C++ to a mechanism. In run #559 Armeria's CPU per request stayed at 17.9-23.6 us from 1 to 4 CPUs while the C++ server's rose from 18.0 to 47.4 us (derived from page data), so the gap comes from the C++ server not scaling on that build, not from Armeria being cheaper per request.

## Compared with alternatives

Pick Armeria over Vert.x gRPC or Pekko gRPC when you want grpc-java's own service API plus gRPC-Web, JSON transcoding and Thrift on one server; pick Vert.x gRPC or Pekko gRPC when raw unary throughput per core matters, since both beat Armeria at every CPU count in run #559, and tonic or grpc-go when memory footprint matters.

## Integration

| | |
|---|---|
| **Form** | Maven/Gradle JAR modules (com.linecorp.armeria:armeria plus armeria-grpc) |
| **Dependencies** | Netty, grpc-java core/stub/protobuf/services, protobuf-java (HEAD pins Netty 4.2.18.Final, grpc-java 1.84.0, protobuf 3.25.9); grpc-kotlin optional |
| **Minimum toolchain** | Java 8 or later for users (README); the benchmark image used Temurin JDK 23 |
| **Platforms** | any platform with a supported JVM |
| **Thread safety** | Service methods run on Netty event-loop threads by default; blocking work must be moved to ServiceRequestContext.blockingTaskExecutor(), the @Blocking annotation or GrpcServiceBuilder.useBlockingTaskExecutor(true) (docs). |
| **Drop-in for the baseline** | partial — not a replacement for the C++ gRPC library; for grpc-java service implementations it reuses the generated ImplBase stubs, so only the server bootstrap changes |

## Gotchas

- The C++ baseline collapses with core count rather than Armeria pulling ahead: cpp_grpc_mt went from 57,403 req/s at 1 CPU to only 85,485 at 4 CPUs (1.49x) while its CPU per request rose from 18.0 to 47.4 us (derived from page data); at 1 CPU, where both burn one core, the two servers tie. The C++ server pre-posts a single CallData per completion queue on the legacy async API and links the unpinned Debian libgrpc++ of the gcc:15.2.0 image, so the 1.28-1.65x margin measures that build and pattern on this host, not C++ codegen.
- Armeria is not special among the JVM rows of the same run: the plain grpc-java 1.58 Netty server (java_hotspot_grpc_g1gc, same JVM flags minus the Armeria header switches) was 1.7% ahead at 1 CPU and 1.0% ahead at 2 CPUs, and Armeria led it by about 6% at 3-4 CPUs; any JVM gRPC server here beats cpp_grpc_mt at 2+ CPUs.
- At 3-4 CPUs the top rows (Vert.x 149-153k, Pekko 141-142k, Quarkus 140-142k req/s) cluster with idle server CPU (Vert.x 225-230%, Pekko 261-271%), and Armeria used 330.65% of 400% at 4 CPUs, which points to the 11-CPU ghz client capping the run near 150k req/s; the 4-CPU ratio is client-bound and not a server ceiling.
- The benchmark server is tuned (Date and Server headers off, -Dcom.linecorp.armeria.validateHeaders=false, PROTO-only serialization, 70% heap) and pins armeria 1.20.3 (2022) with grpc-java 1.58.0, still the pins at grpc_bench HEAD, while Armeria is at 1.42.0 (2026-10-06).

## Known shortcomings

- Downgraded from A to B: slower at 1 CPU (0.98x) and in most other runs (0.48-1.02x); the server is tuned for the benchmark with armeria pinned at 1.20.3. Shared reason for B: the C++ side links unpinned Debian libgrpc++, libgrpc and libprotobuf with version and flags unrecorded (only the 179-line main.cpp gets -O3 -flto), one run per CPU count, and cpp_asio_grpc sits within about 2% of cpp_grpc_mt while rust_tonic_mt also beats it, so the limit is the C++ gRPC library build, not C++ code generation.
- Enricher: the apparent win is the C++ baseline failing to scale: cpp_grpc_mt's CPU per request rises from 18.0 to 47.4 us between 1 and 4 CPUs while Armeria stays at 17.9-23.6 us (derived from #559); at 1 CPU they tie. Armeria matches plain grpc-java 1.58 on Netty (0.98-1.06x) and Vert.x gRPC beats it 1.78x at 1 CPU; the 4-CPU row is probably capped by the ghz client (top rows cluster near 150k req/s with idle server CPU); 1-CPU p90 is 58 ms vs 20 ms for C++; open issue #5152 (large messages slow, deserialisation on the event loop).

## Caveats and trade-offs

The win is not stable across the suite's own published runs. Other published grpc_bench result threads (ratios derived from page data): #441 (i9-13900KF, 2024-04, commit e64db6d) armeria/cpp_grpc_mt = 0.71, 0.72, 0.80, 0.82, 0.84, 0.92 at 1 to 6 server CPUs; #475 (i5-6600K, 2024-09, commit 38875a7) 0.03 (1138 req/s, an apparent 1-CPU JVM anomaly), 0.48, 0.84, 0.87 at 1 to 4 CPUs; #547 (Ryzen 9 5900X, 2025-12) 0.92, 0.97, 1.02 at 1, 4 and 24 CPUs. Armeria is clearly ahead only in the April 2026 Xeon run (2 to 4 CPUs) and behind at 1 CPU there. One run per CPU count, no variance, results posted by the suite maintainer rather than the Armeria authors. The server is tuned for the benchmark (Date and Server headers off, header validation off, 70% heap), while the C++ server is the plain gRPC async pattern on distro libgrpc. The build pins armeria 1.20.3 and grpc-java 1.58.0 (the project is at release 1.42.0 on 2026-10-06), so the rows do not describe current Armeria. Armeria used 570 to 679 MiB against 21 to 32 MiB for C++. cpu and memory columns come from docker stats. The Dockerfile at HEAD for the C++ side says gcc:16.1.0; the run used gcc:15.2.0. [verifier] All #559 numbers and the ratios for #441, #475 and #547 were checked against the pages. In #559 the C++ ceiling is the gRPC C++ core library rather than the app's completion-queue pattern: cpp_asio_grpc (a different C++ server design on the same libgrpc) lands within about 2% of cpp_grpc_mt at every CPU count, cpp_grpc_mt ranks 13th to 25th of 40 rows, and rust_tonic_mt (82515 to 139886 req/s) also beats it at every CPU count, so the result says more about the Debian libgrpc build on this box than about the JVM; the C++ server also ran at 405.58% CPU against a 4-CPU cap. The C++ standing dropped sharply in this run (cpp_grpc_mt was ahead of or near the JVM rows in #441 and #547), which hints at a change in the C++ image (gcc base image and distro libgrpc version) or the host, not established. The 120 s duration is below the README's recommended \~300 s for implementations that need warm-up. #475 was posted by a user (Opa-), not the maintainer; #547 gives no commit. [retier] Enricher: cpp_grpc_mt pre-posts one call per completion queue and its CPU per request rises 18.0 to 47.4 us from 1 to 4 CPUs while Armeria stays at 17.9-23.6 us; at 1 CPU they tie; Armeria matches grpc-java 1.58 Netty and Vert.x gRPC beats it 1.78x at 1 CPU; the 4-CPU row is probably client-capped near 150k req/s; 1-CPU p90 58 ms vs 20 ms for C++.

Memory: 570.43 to 678.56 MiB average for Armeria against 20.59 to 31.71 MiB for the C++ server in the same run (about 21 to 28x more). JVM warm-up (the suite uses a 30 s warm-up) and G1GC; gRPC-Java stack with Netty underneath; the C++ server needs no runtime.

## Maintenance

Actively developed by LINE (release 1.42.0 on 2026-10-06, 5,257 commits, 5.1k stars, 621 open issues), Apache-2.0 and copyable as Maven artifacts; the benchmarked 1.20.3 build is about four years and 22 minor releases old.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** grpc_bench (939 stars, MIT) is a widely used independent suite and #559 is the maintainer's run with public code at c4c93b3 (cpp_grpc_mt_bench/main.cpp and Dockerfile, java_armeria_bench/Dockerfile, build.gradle and HelloWorldServer.java), the CPU model and the app's g++ flags; it falls short of A because the C++ side's measured work runs in Debian-packaged libgrpc++/libgrpc/libprotobuf installed by an unpinned apt-get whose versions and build flags the run does not record (only the 179-line glue gets -O3 -flto), and the margin comes from one run per CPU count that three other published runs do not reproduce.
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own async server pre-posts 5000) and links an unpinned Debian libgrpc++; the enricher shows the C++ server's CPU per request rising from 18.0 to 47.4 us between 1 and 4 CPUs, so the win is the baseline failing to scale.
- **Verifier notes:** Numbers and cross-run ratios check out; downgraded A to B because the C++ gRPC runtime is an unpinned Debian package with unrecorded version and flags, and the 1.28-1.65x margin at 2-4 CPUs is from one run (other runs show 0.48-1.02x, so Armeria is usually slower). Shortcomings: slower at 1 CPU in the cited run and in most other runs, benchmark-tuned server options, pinned old armeria 1.20.3, \~20x more memory, the result reflects the gRPC C++ library build rather than C++ codegen.
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
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/src/main/java/com/linecorp/armeria/examples/helloworld/HelloWorldServer.java>
  - <https://github.com/LesnyRumcajs/grpc_bench/tree/c4c93b3/java_armeria_bench/src/main/java>
  - <https://github.com/line/armeria>
  - <https://github.com/line/armeria/commits/main.atom>
- **Sources the enricher read:**
  - <https://github.com/line/armeria>
  - <https://raw.githubusercontent.com/line/armeria/HEAD/README.md>
  - <https://raw.githubusercontent.com/line/armeria/HEAD/site/src/content/docs/server/grpc.mdx>
  - <https://raw.githubusercontent.com/line/armeria/HEAD/grpc/build.gradle>
  - <https://raw.githubusercontent.com/line/armeria/HEAD/dependencies.toml>
  - <https://github.com/line/armeria/tree/main/site>
  - <https://github.com/line/armeria/releases>
  - <https://github.com/line/armeria/issues?q=is%3Aissue+grpc+performance>
  - <https://github.com/line/armeria/issues/5152>
  - <https://github.com/line/armeria/issues/799>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/src/main/java/com/linecorp/armeria/examples/helloworld/HelloWorldServer.java>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_armeria_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/java_armeria_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/java_armeria_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_asio_grpc_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_hotspot_grpc_g1gc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_hotspot_grpc_sgc_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_hotspot_grpc_sgc_bench/src/main/java/io/grpc/examples/helloworld/HelloWorldServer.java>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/line/armeria`) · [data/wave14/enrich/raw/github_com_line_armeria.json](../../../data/wave14/enrich/raw/github_com_line_armeria.json) (enrichment confidence 0.72)

</details>
