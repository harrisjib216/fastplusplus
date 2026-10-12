# grpc-dotnet (gRPC for .NET)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `Apache-2.0` · 🟢 active

> Managed gRPC for ASP.NET Core; outran stock gRPC C++ async servers 1.48-1.67x on grpc_bench's 2026 unary test.

| | |
|---|---|
| **Beats** | gRPC C++ (grpc/grpc) servers cpp_grpc_st, cpp_grpc_mt and cpp_asio_grpc in the grpc_bench suite |
| **Claimed result** | Newest maintainer run (discussion #559, 2026-04-22, commit c4c93b3, .NET 9 with Grpc.AspNetCore 2.66.0): dotnet_grpc is ahead of every C++ server at every CPU count. 1 CPU: 84,809 req/s vs cpp_grpc_mt 57,403, cpp_grpc_st 57,140 and cpp_asio_grpc 56,669 (1.48x, 1.48x, 1.50x). 2 CPUs: 123,609 vs cpp_asio_grpc 74,869 and cpp_grpc_mt 74,574 (1.65x, 1.66x). 3 CPUs: 136,452 vs cpp_grpc_mt 81,581 (1.67x). 4 CPUs: 135,948 vs 85,485 (1.59x). 2022-04-23 wiki run (commit 14a8435, .NET 6): 1 CPU 33,899 vs cpp_grpc_st 26,700, cpp_grpc_mt 26,376 and cpp_asio_grpc 24,926 (1.27x, 1.29x, 1.36x). 2 CPUs: 68,266 vs cpp_grpc_mt 69,882 (0.98x). 3 CPUs: 68,821 vs 71,806 (0.96x). Third-party run (discussion #547, 2025-12-09, Ryzen 9 5900X, client CPUs equal to server CPUs, 10 s): near tie with cpp_grpc_mt, 0.92x at 1 CPU, 1.01x at 4 and 1.14x at 24. All ratios derived from page data. |
| **Workload** | grpc_bench complex_proto unary SayHello over loopback: 50 client connections, 1000 concurrent requests, unlimited QPS, 120 s with 30 s warmup, ghz client. One run per server-CPU setting: 1 to 4 server CPUs in the 2026-04-22 run (commit c4c93b3, discussion #559) and 1 to 3 in the 2022-04-23 run (commit 14a8435, wiki). |
| **Metric** | throughput |
| **Hardware** | Newest run (discussion #559, posted by maintainer LesnyRumcajs 2026-04-22, commit c4c93b3): Intel Xeon Gold 6548N (16) @ 2.80 GHz, 64 GB RAM, Ubuntu 24.04.3, kernel 6.8.0-71, DigitalOcean dedicated server. Server limited to 1, 2, 3 or 4 CPUs and 4096m RAM; client 11 CPUs. 2022-04-23 wiki run (commit 14a8435): Intel Xeon E5-1650 v3 @ 3.50GHz, 32 GB RAM. Server limited to 1, 2 or 3 CPUs and 512m RAM; client 9 CPUs. |
| **Compiler and flags** | dotnet_grpc in the 2026-04 run (c4c93b3): mcr.microsoft.com/dotnet/sdk:9.0, net9.0, Grpc.AspNetCore 2.66.0, dotnet build -c Release, Kestrel listener HTTP/2 only (dotnet_grpc_bench/Dockerfile, GreeterServer/GreeterServer.csproj, Program.cs). In the 2022 run (14a8435): sdk:6.0, net6.0, Grpc.AspNetCore 2.41.0 with DOTNET_ReadyToRun=0, DOTNET_TieredPGO=1 and DOTNET_TC_QuickJitForLoops=1. The HEAD Dockerfile now uses sdk:10.0. C++ baselines: cpp_grpc_mt and cpp_grpc_st are built with g++ --std=c++20 -O3 -flto over main.cpp and the generated stubs, linking jemalloc and Debian's prebuilt libgrpc++-dev from the base image (gcc:15.2.0 at c4c93b3, gcc:11 at 14a8435, gcc:16.1.0 at HEAD). The gRPC core's version and build flags are the distro package's and are not stated or pinned. cpp_asio_grpc uses asio-grpc v1.0.0, CMake Release with jemalloc, against the same distro libgrpc++. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 4.5k stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/grpc/grpc-dotnet) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

In grpc_bench run #559 (posted by the maintainer on 2026-04-22, Xeon Gold 6548N, server Docker-limited to 1-4 CPUs and 4 GiB, ghz client on 11 CPUs, 50 connections x 1000 concurrent unary complex_proto calls, 120 s after 30 s warm-up, one run per setting), the .NET 9 / Grpc.AspNetCore 2.66.0 server served 1.48-1.67x the req/s of the cpp_grpc_mt, cpp_grpc_st and cpp_asio_grpc servers, built with g++ -O3 -flto against Debian's prebuilt libgrpc++. The 2022 wiki run (.NET 6, Xeon E5-1650 v3) led only at 1 CPU and trailed by 2-4 percent at 2-3 CPUs, and a client-bound third-party run (#547, Ryzen 9 5900X) was a tie.

## Use it when

- A .NET service exposing unary gRPC APIs where a C++ gRPC server was considered for throughput: at 1-4 server CPUs it served 84,809-136,452 req/s versus 56,669-85,485 for the three C++ servers in grpc_bench #559.
- Small CPU-limited containers (1-2 CPUs) where requests per core matter more than resident memory: about 12.0 us of server CPU per request at 1 CPU versus 18.0 us for cpp_grpc_mt, and 20.5 us versus 47.4 us at 4 CPUs (derived from page data).
- Teams already on ASP.NET Core that want gRPC to share its middleware, DI, authentication, logging and Kestrel configuration.
- Replacing the deprecated Grpc.Core package; Grpc.Net.Client also targets net462, netstandard2.0 and netstandard2.1, so older clients can talk to the same services.

## Skip it when

- Memory-tight deployments: 122-135 MiB per server in #559 versus 9-32 MiB for the C++ servers and 13-15 MiB for tonic and Thruster (part of that is probably the dotnet run host process, see gotchas).
- Strict tail-latency budgets on one core: p99 at 1 CPU was 54.20 ms versus 21.81 ms for cpp_grpc_mt.
- You want the fastest gRPC server regardless of language: in the same run rust_tonic_st (102,754), java_vertx_grpc (100,308) and rust_thruster_st (98,464) beat it at 1 CPU, and Vert.x, thruster_mt and tonic_mt at 2 CPUs.
- Handlers that fail often: issue #2033 (open since Feb 2023) measured grpc-dotnet falling from 494 to 116 kops/s when unary handlers fault, below the old Grpc.Core server's 223 kops/s failure case (.NET 7).
- Hosting a server outside ASP.NET Core or on .NET Framework: Grpc.AspNetCore.Server targets only net8.0, net9.0 and net10.0, and a standalone non-ASP.NET server is still an open request (#2543).

## How it is fast

The whole stack is managed code with no native gRPC core: Kestrel's HTTP/2 implementation over System.IO.Pipelines with pooled buffers; the unary handler deserializes the request straight from the request body's PipeReader and, when the message length is known and compression is off, Google.Protobuf serializes the reply straight into the response PipeWriter after writing the 5-byte gRPC frame header (HttpContextSerializationContext's direct-serialization path) instead of an intermediate array. The .NET tiered JIT recompiles the hot path after the 30 s warm-up (grpc_bench set DOTNET_TieredPGO=1 for .NET 6 in Dec 2021; the 2026 .NET 9 image sets no runtime flags and builds without ReadyToRun or Native AOT). The benchmark server adds two tuning steps of its own, a singleton service and a middleware that skips per-request DI scope creation, while the C++ baseline is the untuned helloworld async completion-queue server on Debian's prebuilt libgrpc++.

## Compared with alternatives

Pick it over tonic or Thruster (Rust), which are faster at 1 CPU and use about a tenth of the memory, when the codebase is already .NET; it beats grpc-go at every CPU count in #559 (84,809 vs 55,667 req/s at 1 CPU, 135,948 vs 117,082 at 4). The Kestrel sibling entry is the HTTP/2 server it runs on, so much of the measured advantage belongs to Kestrel.

## Integration

| | |
|---|---|
| **Form** | module (NuGet packages: Grpc.AspNetCore for servers, Grpc.Net.Client and Grpc.Net.ClientFactory for clients) |
| **Dependencies** | ASP.NET Core (Kestrel) for the server, Google.Protobuf, Grpc.Tools for build-time code generation from .proto files |
| **Minimum toolchain** | Server: .NET 8 (Grpc.AspNetCore.Server targets net8.0, net9.0, net10.0); client: .NET Framework 4.6.2 or netstandard2.0; the repo itself builds with .NET SDK 10.0.100 |
| **Platforms** | wherever ASP.NET Core runs; the README lists no platform restrictions |
| **Thread safety** | Not documented in the README; calls are handled concurrently, so a service registered as a singleton (as the benchmark does) must be thread-safe. |
| **Drop-in for the baseline** | partial — speaks the same gRPC wire protocol and .proto contracts as gRPC C++, so it can replace a C++ server process, but the service must be rewritten in C# and run on the .NET runtime |

## Gotchas

- Harness asymmetry: the .NET server in grpc_bench has been maintained by grpc-dotnet's own author (JamesNK, commits 2020-2026) and uses ServiceProvidersMiddleware to bypass per-request DI scopes. Copied into an app with scoped services (an EF Core DbContext, for example), that resolves them from the root provider and shares them across concurrent calls. The C++ servers are the stock helloworld async example with one pre-posted request per completion queue on the older async API, not the callback API.
- Baseline age: the C++ servers link the libgrpc++-dev of the gcc:15.2.0 image, which is Debian trixie; packages.debian.org lists 1.51.1 in bookworm and sid (search snippets only, trixie page not reachable), so the 2026 run probably compared .NET 9 with Grpc.AspNetCore 2.66.0 (2024) against a late-2022 gRPC C++ core built with distro flags.
- The memory column comes from docker stats, and the image's ENTRYPOINT is 'dotnet run -c Release -p GreeterServer --no-build', which likely keeps the SDK CLI process resident next to the server, so the 122-135 MiB probably overstates the server itself.
- At 3-4 CPUs the .NET server used only 256-279 percent CPU while the top seven servers cluster at 136-153k req/s, which suggests the 11-CPU ghz client caps those rows, whereas the C++ servers saturate 306-406 percent. In the client-bound third-party run (#547, 1 CPU) cpp_grpc_mt needed 14.4 us of CPU per request versus 32.4 us for dotnet_grpc (derived from page data), so the CPU-efficiency lead flips between runs.

## Known shortcomings

- grpc_bench discussion 559 (2026-04): 1.48-1.67x over all C++ servers at 1-4 CPUs in the newest run, but the 2022 run led at 1 CPU only and #547 was a client-bound tie; memory 4-6x higher and worse 1-CPU p99; the HTTP/2 work is Kestrel's (dotnet/aspnetcore, separate record). Shared C++ baseline flaw: unpinned distro libgrpc++, helloworld async pattern, poor scaling (85,485 req/s at 4 CPUs).
- Harness asymmetry: the .NET bench server has been maintained by grpc-dotnet's author (JamesNK, 2020-2026) and uses ServiceProvidersMiddleware to skip per-request DI scopes plus a singleton service, which is unsafe to copy into apps with scoped services; the C++ servers are the stock helloworld async completion-queue pattern with one pre-posted request per queue, linking libgrpc++ from Debian trixie (probably 1.51.1, late 2022; version from search snippets only). The memory column likely includes the resident dotnet run SDK process; the 3-4 CPU rows are likely capped by the client (.NET at 256-279% CPU). In #547 cpp_grpc_mt used 14.4 us CPU per request against .NET's 32.4 at 1 CPU. Open issue #2033: throughput falls from 494 to 116 kops/s when handlers fault.

## Caveats and trade-offs

The result depends on the run.
- In the newest maintainer run (.NET 9) dotnet_grpc leads every C++ server by 1.48-1.67x at 1-4 CPUs. Its p99 at 1 CPU is worse (54.20 vs 21.81 ms for cpp_grpc_mt), and it uses about 4-6x the memory (127.87 vs 20.59 MiB at 1 CPU, 134.64 vs 31.71 MiB at 4).
- In the 2022 run (.NET 6) it led only at 1 CPU and trailed cpp_grpc_mt by 2-4% at 2 and 3 CPUs.
- In a client-bound third-party run (#547, by the wtx author) the two tie.
- The C++ servers link Debian's prebuilt libgrpc++, which is unpinned and of unstated version and flags, so the -O3 -flto applies only to the server code and stubs. They follow the helloworld async-example pattern: one completion queue and thread per server CPU, with one pre-posted request per queue (cpp_grpc_mt_bench/main.cpp). They scale poorly: cpp_grpc_mt does 57,403 req/s at 1 CPU and 85,485 at 4 CPUs while using 405% CPU. So the baseline is a stock but untuned gRPC C++ server.
- grpc-dotnet runs on ASP.NET Core Kestrel (dotnet/aspnetcore, a separate wave 14 record), so much of the HTTP/2 work is Kestrel's.
- The workload is a unary complex_proto SayHello only, over loopback on one host, with a single run per setting.
- The grpc-dotnet README makes no performance claim. [retier] Enricher (Pekko gRPC pass): grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own server_async.cc pre-posts 5000) and allocates per RPC; it links unpinned Debian libgrpc++ (likely 1.51.1). Every grpc_bench row compared against cpp_grpc_mt inherits this crippled baseline.

.NET runtime and JIT required; it sits on Kestrel (ASP.NET Core).

## Maintenance

Actively maintained by the gRPC project and Microsoft (Grpc.AspNetCore 2.84.0 on NuGet 2026-09-21, last commit 2026-09-17), Apache-2.0, and the recommended C# gRPC implementation; copyable as NuGet packages, with the grpc_bench image already moved to .NET 10 (PR #560) after the measured run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** LesnyRumcajs/grpc_bench is a well-known independent third-party gRPC shootout. Its 2022-04-23 wiki page and its newest maintainer-posted run (discussion #559, 2026-04-22) both state the CPU, commit and settings, and the harness is public (dotnet_grpc_bench, cpp_grpc_mt_bench/{Dockerfile,main.cpp}, cpp_asio_grpc_bench). It falls short of A for the same reason as wave 5's grpc/grpc verdict: the C++ baseline links Debian's prebuilt libgrpc++-dev, whose version and build flags are neither stated nor pinned.
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's C++ entry cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own async QPS server pre-posts 5000 per queue, and it links unpinned Debian libgrpc++ (likely gRPC 1.51.1) with version and flags unrecorded, so wins over it measure a weak C++ server setup rather than the C++ gRPC stack at its best.
- **Verifier notes:** The 2022 numbers match the wiki page exactly. The newest run of the same harness (discussion #559, 2026-04) strengthens the claim to 1.48-1.67x at 1-4 CPUs, so benchmark_url moved there and the claim now lists both runs plus the client-bound tie in #547. Shortcomings to record: the result is run-dependent (2022 showed a lead at 1 CPU only); the C++ baseline is an untuned helloworld-pattern server on an unpinned distro libgrpc++; it uses 4-6x the memory of the C++ server and has a worse 1-CPU p99; and the HTTP/2 work is Kestrel's. Metadata confirmed: Apache-2.0, 4.5k stars, last commit 2026-09-17, not a fork or archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-42 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/categories/benchmark-results>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/GreeterServer.csproj>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/Program.cs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/dotnet_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/dotnet_grpc_bench/GreeterServer/GreeterServer.csproj>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/dotnet_grpc_bench/Dockerfile>
  - <https://github.com/grpc/grpc-dotnet>
  - <https://github.com/grpc/grpc-dotnet/commits>
- **Sources the enricher read:**
  - <https://github.com/grpc/grpc-dotnet>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/src/Grpc.AspNetCore.Server/Internal/HttpContextSerializationContext.cs>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/src/Grpc.AspNetCore.Server/Internal/PipeExtensions.cs>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/src/Grpc.AspNetCore.Server/Internal/CallHandlers/UnaryServerCallHandler.cs>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/src/Grpc.AspNetCore.Server/Grpc.AspNetCore.Server.csproj>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/src/Grpc.Net.Client/Grpc.Net.Client.csproj>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/Directory.Build.props>
  - <https://raw.githubusercontent.com/grpc/grpc-dotnet/HEAD/global.json>
  - <https://github.com/grpc/grpc-dotnet/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://github.com/grpc/grpc-dotnet/issues/2033>
  - <https://api.nuget.org/v3/registration5-semver1/grpc.aspnetcore/index.json>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://github.com/LesnyRumcajs/grpc_bench/commits/master/dotnet_grpc_bench>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/README.md>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/build.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/GreeterServer.csproj>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/Program.cs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/Services/GreeterService.cs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/dotnet_grpc_bench/GreeterServer/ServiceProvidersMiddleware.cs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/docker-library/gcc/master/15/Dockerfile>
  - WebSearch: Debian trixie libgrpc++-dev package version grpc 1.51.1 (snippets of packages.debian.org bookworm and sid pages)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/grpc/grpc-dotnet`) · [data/wave14/enrich/raw/github_com_grpc_grpc_dotnet.json](../../../data/wave14/enrich/raw/github_com_grpc_grpc_dotnet.json) (enrichment confidence 0.7)

</details>
