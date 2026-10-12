# Vert.x gRPC server (Java): grpc_bench unary echo vs C++ gRPC (cpp_grpc_mt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `EPL-2.0 OR Apache-2.0` · 🟢 active

> Eclipse Vert.x's own gRPC server for the JVM; served unary grpc_bench echo 1.75x faster than the gRPC C++ async server in one 2026 run.

| | |
|---|---|
| **Beats** | gRPC C++ async server (cpp_grpc_mt in LesnyRumcajs/grpc_bench): the stock async greeter pattern with one completion queue per server thread, GRPC_SERVER_CPUS threads and a single pre-posted CallData per queue; main.cpp and the generated code are built with g++ 15.2.0 --std=c++20 -O3 -flto and linked with jemalloc against Debian-packaged libgrpc++, libgrpc and libprotobuf (versions and build flags not recorded). It was the fastest of the run's three C++ rows (cpp_grpc_mt, cpp_asio_grpc, cpp_grpc_st) at 1, 3 and 4 CPUs and within 0.4% of cpp_asio_grpc at 2 CPUs. |
| **Claimed result** | Discussion #559 (2026-04-23 run), java_vertx_grpc vs cpp_grpc_mt in req/s: 1 CPU 100308 vs 57403 (1.75x); 2 CPUs 148200 vs 74574 (1.99x); 3 CPUs 153126 vs 81581 (1.88x); 4 CPUs 149776 vs 85485 (1.75x) (ratios derived from page data). Vert.x has the highest req/s of the four rows at 2, 3 and 4 CPUs; average latency at 4 CPUs 4.95 ms vs 11.28 ms. |
| **Workload** | grpc_bench complex_proto unary RPC echo (the handler puts the request's Hello message into the reply; the C++ server std::moves it), ghz 0.114.0 client with 50 connections and 1000 concurrent requests, 120 s measured after a 30 s warm-up, server capped at 1 to 4 CPUs and 4096m RAM, run at grpc_bench commit c4c93b3 (2026-04-22) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548N (16) @ 2.800GHz, 64 GB RAM, Digital Ocean dedicated server, Ubuntu 24.04.3 LTS, kernel 6.8.0-71-generic; server limited by Docker to 1, 2, 3 or 4 CPUs, ghz 0.114.0 client given 11 CPUs |
| **Compiler and flags** | vertx-grpc-server 4.4.4 on default JVM ergonomics: the Dockerfile's JAVA_OPTS (SerialGC, RAMPercentage=70) are not read by its exec-form java -jar ENTRYPOINT (enricher correction); C++ baseline links unpinned Debian libgrpc++ with only main.cpp built at -O3 -flto |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | No source gives a mechanism. Inference from the same tables: the C++ server used 405.58% CPU for 85485 req/s at 4 CPUs while Vert.x used 230.43% for 149776 req/s, so the difference is cost per request; the cause is not established by the benchmark. |
| **Adoption** | 53 stars (Eclipse Vert.x component) |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/eclipse-vertx/vertx-grpc) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

In grpc_bench discussion #559 (maintainer run, commit c4c93b3, Intel Xeon Gold 6548N, ghz 0.114.0 with 50 connections and 1000 concurrent unary complex_proto echo calls, 120 s after a 30 s warm-up), Vert.x gRPC server 4.4.4 on Temurin 23 served 100308 req/s on 1 CPU against 57403 for cpp_grpc_mt (g++ 15.2.0 -O3 -flto glue linked to Debian-packaged libgrpc++ and jemalloc), 1.75x, and 1.75x to 1.99x at 2 to 4 CPUs where the faster rows appear to hit a shared ceiling; earlier published runs (#441, #475, #547) put it only 0.98x to 1.22x ahead.

## Use it when

- JVM services that are mostly small unary gRPC calls and need the highest requests per CPU core of the Java options (it topped all 13 JVM rows of grpc_bench #559 at 1 and 4 CPUs).
- Applications already on Vert.x or Quarkus, where the gRPC endpoint can share the event loops and the HTTP server with REST routes.
- gRPC proxies and gateways: the message-level API forwards protobuf-encoded (even compressed) messages without decoding and re-encoding them.
- Services that must expose gRPC-Web or HTTP/JSON transcoding from the same port without an Envoy sidecar.

## Skip it when

- Memory-tight deployments or sidecars: grpc_bench #559 measured 108 to 333 MiB for Vert.x against 21 to 32 MiB for the C++ server and 13 to 15 MiB for Rust tonic.
- Tail-latency-bound services: despite lower averages, Vert.x's p99 was worse than C++ in #559 (29.95 ms vs 21.81 ms at 1 CPU, 21.70 ms vs 19.69 ms at 4 CPUs).
- Handlers that block (JDBC, file I/O, heavy CPU) unless they are moved off the event loop; a blocking handler stalls every call on that loop.
- Short-lived processes or cold-start-sensitive deployments: the measured numbers come after a 30 s JIT warm-up.
- Teams that need the C++ result reproduced: three other published grpc_bench runs show only 0.98x to 1.22x over cpp_grpc_mt.

## How it is fast

The benchmark gives no mechanism. In the source, GrpcServerImpl handles each gRPC call on the Vert.x context (event loop) that owns the HTTP/2 request, with message framing done on Vert.x Buffers, so there is no hand-off to a separate executor; the grpc_bench app deploys one ServerVerticle per CPU, each with its own HttpServer on its own event loop sharing port 50051. The measurable effect in #559 is CPU per request (derived from page data): about 10.1 us for Vert.x against 18.0 us for cpp_grpc_mt at 1 CPU, and 15.4 us against 47.4 us at 4 CPUs, where the C++ server's per-request CPU rose 2.6x while Vert.x's rose 1.5x.

## Compared with alternatives

Pick it over grpc-dotnet (84809 req/s at 1 CPU), Rust tonic (82515) and Armeria (56315) when the service must stay on the JVM and per-core unary throughput matters most, since it posted 100308 req/s at 1 CPU in the same run; pick tonic instead when memory matters (13 to 15 MiB against 108 to 333 MiB) or p99 latency is the target.

## Integration

| | |
|---|---|
| **Form** | module (Maven artifact io.vertx:vertx-grpc-server; vertx-grpcio-server for grpc-java stubs) |
| **Dependencies** | vertx-core (Vert.x HTTP/2 server on Netty), protobuf-java; protobuf-java-util for the JSON wire format; grpc-java stubs only through vertx-grpcio-server |
| **Minimum toolchain** | Minimum JDK not documented in the pages read; the benchmark built vertx-grpc-server 4.4.4 on eclipse-temurin 23 with Gradle and protoc 3.21.6 |
| **Platforms** | any JVM platform (the benchmark ran on x86-64 Linux in Docker) |
| **Thread safety** | Not documented in the gRPC docs; each call is handled on the Vert.x context of its HTTP request (event-loop model), so a handler must not block |
| **Drop-in for the baseline** | partial — it speaks the standard gRPC over HTTP/2 wire protocol, so existing C++ clients need no change, but the service itself must be rewritten in Java against the Vert.x API |

## Gotchas

- Harness flaw in the measured row: java_vertx_grpc_bench/Dockerfile sets ENV JAVA_OPTS (-XX:+UseSerialGC, Min/MaxRAMPercentage=70) but starts the server with an exec-form ENTRYPOINT ["java", "-jar", ...]; the java launcher does not read JAVA_OPTS, so those flags never reached the JVM and Vert.x ran on default JVM ergonomics. The java_hotspot_grpc_\* images use the Gradle installDist start script, which does read JAVA_OPTS, so the Vert.x row is not configured like its JVM siblings and the record's compiler_and_flags is wrong on this point.
- The 2 to 4 CPU rows look capped outside the server: Vert.x stayed near 150k req/s (148200, 153126, 149776) and used only 230% CPU of a 4-CPU limit, and Quarkus, Armeria, tonic and .NET cluster at 131k to 142k; with a ghz client limited to 11 CPUs and the server reached through a Docker-published port on 127.0.0.1, the 1.88x to 1.99x figures probably measure the C++ server against a shared ceiling. The CPU-bound like-for-like point is 1 CPU (100308 vs 57403 req/s, 1.75x).
- The C++ baseline pre-posts a single CallData per completion queue, whereas gRPC's own async QPS benchmark server (test/cpp/qps/server_async.cc) pre-posts 5000 request contexts per queue; it also links an unpinned Debian libgrpc++ build. cpp_asio_grpc lands within about 2% of it, so the ceiling is most likely the packaged gRPC C++ core rather than the app pattern, but the baseline is not gRPC C++ at its tuned best.
- Security: the benchmarked vertx-grpc-server 4.4.4 is in the range of CVE-2024-8391 (GHSA-g76f-gjfx-4rpr: no limit on inbound message length, 4.3.0 to 4.5.9, fixed in 4.5.10), and a per-message allocation bound for compressed messages was only added on 2026-10-07 (5.1.9); set a maximum message size and use a current release.

## Known shortcomings

- Downgraded from A to B: tops the 2-4 CPU tables in #559 (1.75-1.99x) but other runs show 0.98-1.22x; vertx-grpc-server pinned at 4.4.4. Shared reason for B: the C++ side links unpinned Debian libgrpc++, libgrpc and libprotobuf with version and flags unrecorded (only the 179-line main.cpp gets -O3 -flto), one run per CPU count, and cpp_asio_grpc sits within about 2% of cpp_grpc_mt while rust_tonic_mt also beats it, so the limit is the C++ gRPC library build, not C++ code generation.
- Enricher: java_vertx_grpc_bench's Dockerfile sets JAVA_OPTS (SerialGC, RAMPercentage=70) but uses an exec-form ENTRYPOINT that the java launcher runs without reading JAVA_OPTS, so Vert.x ran on default JVM ergonomics unlike the HotSpot rows that use the Gradle start script. The 2-4 CPU rows hit a shared ceiling near 150k req/s (only 230% CPU at the 4-CPU cap), so the like-for-like point is 1 CPU only (1.75x); p99 is worse than C++ (29.95 vs 21.81 ms at 1 CPU); the measured 4.4.4 carries CVE-2024-8391; the C++ baseline pre-posts one CallData per queue.

## Caveats and trade-offs

The benchmark pins vertx-grpc-server 4.4.4 (Vert.x 4.x); the repository is now at 5.1.9 releases with a 5.3.0-SNAPSHOT, so the rows describe an old release. One run per CPU count, posted by the suite maintainer. Other published grpc_bench result threads (ratios derived from page data): #441 (i9-13900KF, 2024-04) java_vertx_grpc/cpp_grpc_mt = 1.12, 1.02, 1.11, 1.15, 1.09, 1.09 at 1 to 6 CPUs; #475 (i5-6600K, 2024-09) 0.13 (5282 req/s, apparent 1-CPU anomaly), 1.22, 1.18, 1.18 at 1 to 4 CPUs; #547 (Ryzen 9 5900X, 2025-12) 1.01, 0.98, 1.15 at 1, 4 and 24 CPUs. Vert.x is the most consistent winner of the three JVM rows, but the margin is 2 to 22% in the older runs against 75 to 99% in the April 2026 run. Vert.x used 108 to 333 MiB against 21 to 32 MiB for C++. cpu and memory come from docker stats. The Dockerfile at HEAD for the C++ side says gcc:16.1.0; the run used gcc:15.2.0. [verifier] All #559 numbers and the ratios for #441, #475 and #547 were checked against the pages. In #559 the C++ ceiling is the gRPC C++ core library rather than the app's completion-queue pattern: cpp_asio_grpc (a different C++ server design on the same libgrpc) lands within about 2% of cpp_grpc_mt at every CPU count, cpp_grpc_mt ranks 13th to 25th of 40 rows, and rust_tonic_mt (82515 to 139886 req/s) also beats it at every CPU count, so the result says more about the Debian libgrpc build on this box than about the JVM; the C++ server also ran at 405.58% CPU against a 4-CPU cap. The C++ standing dropped sharply in this run (cpp_grpc_mt was ahead of or near the JVM rows in #441 and #547), which hints at a change in the C++ image (gcc base image and distro libgrpc version) or the host, not established. The 120 s duration is below the README's recommended \~300 s for implementations that need warm-up. #475 was posted by a user (Opa-), not the maintainer; #547 gives no commit. [retier] Enricher: grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own server_async.cc pre-posts 5000) and allocates per RPC, linking an unpinned Debian libgrpc++. Vert.x's Dockerfile sets JAVA_OPTS but its exec-form ENTRYPOINT ignores them, so it ran on default JVM ergonomics; the 2-4 CPU rows hit a shared ceiling near 150k req/s, leaving 1 CPU (1.75x) as the like-for-like point; p99 is worse than C++ (29.95 vs 21.81 ms at 1 CPU); 4.4.4 carries CVE-2024-8391.

Memory: 108.17 to 333.09 MiB average for Vert.x against 20.59 to 31.71 MiB for C++ in the same run. JVM warm-up and GC; the Vert.x event-loop model (callbacks) with one verticle per CPU.

## Maintenance

Actively maintained Eclipse Vert.x component (5.1.9 released 2026-10-07, 5.3.0-SNAPSHOT on main, dual EPL-2.0/Apache-2.0); the measured 4.4.4 release is old, carries CVE-2024-8391, and its grpc-java MethodDescriptor style of binding moved to vertx-grpcio-server in 5.x, so the benchmark code needs porting before it can be rerun on a current release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** grpc_bench (939 stars, MIT) is a widely used independent suite and #559 is the maintainer's run with public code at c4c93b3 (cpp_grpc_mt_bench/main.cpp and Dockerfile, java_vertx_grpc_bench/Dockerfile, build.gradle and src/main/java/vertx/Main.java), the CPU model and the app's g++ flags; it falls short of A because the C++ side's measured work runs in Debian-packaged libgrpc++/libgrpc/libprotobuf installed by an unpinned apt-get whose versions and build flags the run does not record (only the 179-line glue gets -O3 -flto), and the margin comes from one run per CPU count that three other published runs do not reproduce.
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's C++ entry cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own async QPS server pre-posts 5000 per queue, and it links unpinned Debian libgrpc++ with version and flags unrecorded. For Vert.x the JVM flags in the Dockerfile were also never applied (exec-form ENTRYPOINT ignores JAVA_OPTS).
- **Verifier notes:** Numbers and cross-run ratios check out; Vert.x tops all 40 rows at 2, 3 and 4 CPUs in #559 and is the steadiest JVM winner across runs, but downgraded A to B because the C++ gRPC runtime is an unpinned Debian package with unrecorded version and flags and the 1.75-1.99x margin comes from one run (other runs show 0.98-1.22x). Shortcomings: single run, margin much smaller elsewhere, pinned Vert.x 4.4.4, more memory, the result reflects the gRPC C++ library build rather than C++ codegen.
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
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/src/main/java/vertx/Main.java>
  - <https://github.com/LesnyRumcajs/grpc_bench/tree/c4c93b3/java_vertx_grpc_bench>
  - <https://github.com/eclipse-vertx/vertx-grpc>
  - <https://github.com/eclipse-vertx/vertx-grpc/commits>
- **Sources the enricher read:**
  - <https://github.com/eclipse-vertx/vertx-grpc>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/HEAD/README.md>
  - <https://github.com/eclipse-vertx/vertx-grpc/tree/main/vertx-grpc-docs/src/main/asciidoc>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/main/vertx-grpc-docs/src/main/asciidoc/index.adoc>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/main/vertx-grpc-docs/src/main/asciidoc/server.adoc>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/main/vertx-grpc-docs/src/main/asciidoc/ioserver.adoc>
  - <https://github.com/eclipse-vertx/vertx-grpc/tree/main/vertx-grpc-server/src/main/java/io/vertx/grpc/server/impl>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/main/vertx-grpc-server/src/main/java/io/vertx/grpc/server/impl/GrpcServerImpl.java>
  - <https://raw.githubusercontent.com/eclipse-vertx/vertx-grpc/main/vertx-grpc-server/src/main/java/io/vertx/grpc/server/impl/Http2GrpcOutboundStream.java>
  - <https://github.com/eclipse-vertx/vertx-grpc/issues?q=is%3Aissue+performance+OR+leak+OR+memory+OR+slow>
  - <https://github.com/eclipse-vertx/vertx-grpc/commits/main>
  - <https://github.com/advisories/GHSA-g76f-gjfx-4rpr>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/src/main/java/vertx/Main.java>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/build.gradle>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_vertx_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/java_hotspot_grpc_sgc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/grpc/grpc/master/test/cpp/qps/server_async.cc>
  - WebSearch snippets: 'vertx-grpc CVE max message size decompression vulnerability' (CVE-2024-8391 records on vulert.com, sentinelone.com, advisories.gitlab.com)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/eclipse-vertx/vertx-grpc`) · [data/wave14/enrich/raw/github_com_eclipse_vertx_vertx_grpc.json](../../../data/wave14/enrich/raw/github_com_eclipse_vertx_vertx_grpc.json) (enrichment confidence 0.62)

</details>
