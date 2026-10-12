# ActualLab.Rpc (part of ActualLab.Fusion)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> .NET RPC library (Fusion's transport) that multiplexes calls over one WebSocket; vendor loopback benchmark shows 5-8x grpc-dotnet call throughput.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | Localhost calls: Sum 9.91M calls/s vs gRPC 1.28M (\~7.7x) and SignalR 4.85M; GetUser 8.75M vs gRPC 1.24M (\~7.1x); SayHello 6.04M vs gRPC 1.16M (\~5.2x). Streams: Stream1 99.96M items/s vs gRPC 43.78M (\~2.3x); Stream100 44.89M vs 25.87M (\~1.7x); Stream10K 807.84K vs 572.76K (\~1.4x). Docker 4-CPU server: SayHello 2.52M vs gRPC 399.32K calls/s (\~6.3x, stated on page). Speedup ranges are printed on docs/Performance.md. README says "2-7x faster than gRPC and SignalR even in its 'raw' mode". |
| **Workload** | Client/server RPC over Windows localhost loopback (not in-process): unary calls Sum/GetUser/SayHello (calls/s) and server streaming of 1-byte/100-byte/10KB items (items/s); plus a Docker run with a 4-CPU server matching grpc_bench's SayHello setup. ActualLab.Rpc uses its msgpack6c serializer; gRPC is grpc-dotnet (Grpc.AspNetCore). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D (16C/32T), 96 GB DDR5, Windows 11; localhost loopback with Windows loopback large MTU enabled. Docker variant: server container limited to 4 CPUs, clients 24 CPUs. |
| **Compiler and flags** | .NET 10.0.8 (Docker runs: .NET 10 SDK image 10.0.10); dotnet run -c Release; RpcBenchmark.csproj sets TieredPGO=true, TieredCompilation + QuickJit/QuickJitForLoops=true, ServerGarbageCollection=true, RetainVMGarbageCollection=true, GarbageCollectionAdaptationMode=0; args: test -b calls\|streams -l rpc,grpc,signalr -f msgpack6c -s -n 6 |
| **Adoption** | 178 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/ActualLab/Fusion) · [benchmark](<https://github.com/ActualLab/Fusion.Samples/blob/master/Benchmarks.md (Run-RpcBenchmark.cmd section; rendered copy in https://github.com/ActualLab/Fusion/blob/master/docs/Performance.md)>) |

## Verdict

The vendor's harness (Fusion.Samples src/RpcBenchmark) runs the ASP.NET Core server and the clients in one process over TLS on 127.0.0.1, on a Ryzen 9 9950X3D with Windows 11 and .NET 10.0.8. Worker count and concurrency are auto-tuned for each framework, and the best of 6 x 5 s runs is reported. ActualLab.Rpc (msgpack6c over WebSocket) did 9.91M/8.75M/6.04M calls/s on Sum/GetUser/SayHello vs grpc-dotnet's 1.28M/1.24M/1.16M (5.2-7.7x), and 1.4-2.3x more stream items/s. With the server limited to 4 CPUs in Docker, SayHello ran at 2.52M vs 399.32K calls/s (\~6.3x) and Sum at 4.77M vs 437.85K (\~10.9x, derived).

## Use it when

- Both ends are .NET (ASP.NET Core server; .NET, Blazor WebAssembly or MAUI clients), and you have many small unary calls where per-call overhead dominates. Sum/GetUser-sized payloads were 7-8x grpc-dotnet in the vendor localhost test.
- Many concurrent callers share each connection. The writer batches whatever is queued into about 12 KB frames, so the gain grows with in-flight calls (the benchmark uses 200 concurrent tasks per client for calls).
- Server streaming of small items (1-100 bytes each), for example telemetry or UI feeds. The vendor results were 1.7-2.3x gRPC on localhost and 2.1-3.0x in the 4-CPU Docker run.
- A browser or TypeScript front end talks to a .NET back end and you would otherwise use gRPC-Web or SignalR. @actuallab/rpc uses the same wire format (json5np or msgpack6/msgpack6c).
- You already use Fusion, or you plan to. Compute Service Clients add client-side caching with server-pushed invalidation on top of the same transport.

## Skip it when

- Polyglot systems. Only .NET and TypeScript implementations exist, contracts are C# interfaces, not .proto files, and gRPC clients, proxies and tooling cannot talk to it.
- Large-payload streaming. The lead shrinks to 1.4x at 10 KB items on localhost (8.27 vs 5.86 GB/s) and to about 2x in Docker.
- Workloads that care about single-call latency at low concurrency. The published latencies are measured at saturation, and in the 4-CPU Docker run gRPC had the lower p50 (SayHello 4.2 ms vs 6.4 ms; Sum 3.3 ms vs 3.5 ms), although ActualLab.Rpc had the lower p99 on Sum (12.8 ms vs 45.4 ms).
- You need independent or Linux bare-metal numbers before you commit. All published results are the vendor's own, on Windows loopback and Docker Desktop/WSL2.
- Payloads above 15.5 MiB per call, or older mixed-runtime clients that exchange interface-typed values. See gotchas.

## How it is fast

All calls from one client peer share one WebSocket. The frame-based writer (RpcFrameBasedTransport) drains a channel of queued messages, serializes them back-to-back into a pooled buffer, and flushes a frame when it reaches FrameSize (12,000 bytes by default) or when the queue is empty. Under load, many calls therefore go out in one write (opportunistic write coalescing, with no timer by default), and the next frame is serialized while the previous one flushes. Each call is a compact binary envelope (varint call IDs) with MessagePack or MemoryPack arguments, and proxies are source-generated (ActualLab.Interception: 1 allocation per call, no boxing); RpcStream&lt;T&gt; sends items in batches of up to 1024 under an ack-window flow control, where gRPC sends one protobuf message per item.

## Compared with alternatives

All other catalogued entries that beat gRPC are for Go (rpcx, Kitex, DRPC, cmd-stream, fRPC, Exposed), Rust (wtx) or C++ (brpc, grpcxx), so pick ActualLab.Rpc when both ends are .NET, or when a TypeScript client talks to a .NET server. Pick wtx or grpcxx instead if you must stay on the gRPC wire protocol.

## Integration

| | |
|---|---|
| **Form** | module: NuGet packages (ActualLab.Rpc for clients, ActualLab.Rpc.Server for ASP.NET Core hosting), with a Roslyn source generator (ActualLab.Generators) |
| **Dependencies** | ActualLab.Core, ActualLab.Interception, ActualLab.Generators (compile-time), MemoryPack (default serializer) or MessagePack-CSharp; System.IO.Pipelines package on pre-net9 targets; the server side needs ASP.NET Core |
| **Minimum toolchain** | ActualLab.Rpc.csproj multi-targets netstandard2.0, netstandard2.1, netcoreapp3.1 and net5.0-net10.0; the HTTP/2 client transport needs net5+. The benchmark ran on .NET 10.0.8. |
| **Platforms** | Any .NET runtime (server, Blazor WebAssembly, MAUI per README); Native AOT and trimming are supported (runtime codegen switches to interpreted expressions); TypeScript client via @actuallab/rpc |
| **Thread safety** | Not documented as a statement. The benchmark shares one client proxy (one peer and WebSocket) across 200 concurrent tasks, which is the intended usage. |
| **Drop-in for the baseline** | no |

## Gotchas

- Size limits (tightened in v14.2): a message whose argument data exceeds 15.5 MiB, or whose header or method reference exceeds 1 KiB, is dropped on receive with no error reply. The caller sees the call as never answered.
- Abstract and interface-typed arguments and results are sent with a runtime type name (TypeRef). Open issue #60: a net472 client calling a net10 server that returns IList&lt;string&gt; fails with 'Type System.Collections.Generic.List`1[...], System.Private.CoreLib is not found'.
- The format is chosen per connection (?f=key), and both peers must support it. The README says MemoryPack is the default and MessagePack (msgpack6c, used in the benchmark) needs runtime IL emit. The TypeScript client supports only JSON and MessagePack, with no MemoryPack and no polymorphism.
- RpcStream defaults are BatchSize 64, AckPeriod 30 and AckAdvance 61. The benchmark server overrides them to BatchSize 200 for items under 50 bytes, AckPeriod 900 and AckAdvance 1801. Expect lower stream throughput without similar tuning.

## Known shortcomings

- Vendor-only evidence with no independent reproduction. Server and client run in one process over TLS to 127.0.0.1 on Windows loopback or Docker Desktop/WSL2, sharing 32 hardware threads. Each figure is the best of 6 x 5 s runs; localhost gRPC stream figures come from an earlier run and the Docker table keeps the better of two runs. The stream benchmark retunes RpcStream (BatchSize 200 for small items, AckPeriod 900, AckAdvance 1801) while gRPC sends one message per item, so part of the stream speedup is application-level batching; it uses the non-default msgpack6c serializer and WebSocket/HTTP-1.1 vs gRPC's HTTP/2. Benchmarks.md overstates grpc-dotnet as the fastest in grpc_bench #441 (it ranked 4th). Latency is measured at saturation, where gRPC had the lower p50 in Docker (SayHello 4.2 vs 6.4 ms). Oversized messages are dropped without an error reply; net472-to-net10 IList&lt;string&gt; deserialization fails (#60); .NET/TypeScript only, not gRPC wire-compatible.

## Caveats and trade-offs

First-party benchmark (harness lives in the separate ActualLab/Fusion.Samples repo, MIT, 17 stars). Windows loopback only for the headline table; Benchmarks.md notes gRPC/SignalR results are more variable on Windows loopback and that the gRPC stream figures were kept from a previous run because the latest run was lower, so the stream rows mix runs. Serializers differ (MessagePack vs protobuf). The page cross-checks its 4-CPU gRPC SayHello figure (399.32K) against grpc_bench's published .NET result (\~402K) on a different CPU. No independent reproduction found.

.NET/C# only; part of a larger real-time framework (Fusion) with its own caching/pub-sub model, so adopting ActualLab.Rpc in isolation is less common; API differs substantially from gRPC's contract-first model

## Maintenance

Actively maintained: last commit 2026-09-15, about 5,500 commits, ActualLab.Rpc 14.4.16 on NuGet with \~663K total downloads. MIT-licensed and usable standalone from Fusion, but the published benchmarks were run on v14.0.17.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C-&gt;A: the README table (9.91M vs gRPC 1.28M calls/s; 99.96M vs 43.78M items/s) traces to ActualLab/Fusion.Samples Benchmarks.md, which gives the public harness src/RpcBenchmark (RpcBenchmark.csproj, MIT), the exact commands (dotnet run -c Release ... test -b calls|streams -l rpc,grpc,signalr -f msgpack6c -s -n 6), .NET 10.0.8 and CPU AMD Ryzen 9 9950X3D. Code, runtime/compiler, flags and CPU are all stated.
- **Verifier notes:** Numbers match the README and Performance docs. Upgraded to tier A because the benchmark code, commands, .NET version and CPU are all public. Metadata checked via gh GraphQL: MIT, 178 stars, last commit 2026-09-15, not a fork or archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ActualLab/Fusion>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/README.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/Performance.md>
  - <https://github.com/ActualLab/Fusion.Samples>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/Benchmarks.md>
  - <https://github.com/ActualLab/Fusion.Samples/tree/master/src/RpcBenchmark>
  - <https://github.com/ActualLab/Fusion.Samples/blob/master/src/RpcBenchmark/RpcBenchmark.csproj>
- **Sources the enricher read:**
  - <https://github.com/ActualLab/Fusion>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/README.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/Performance.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR-Serialization.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR-RpcStream.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR-CO.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR-D.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartR-HttpTransport.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartAOT.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartTS.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/PartTS-Rpc.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/docs/QA.md>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/src/ActualLab.Rpc/README.md>
  - <https://github.com/ActualLab/Fusion/blob/master/src/ActualLab.Rpc/ActualLab.Rpc.csproj>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/src/ActualLab.Rpc/Infrastructure/RpcFrameBasedTransport.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion/master/src/ActualLab.Rpc/WebSockets/RpcWebSocketTransport.cs>
  - <https://github.com/ActualLab/Fusion/issues/60>
  - <https://github.com/ActualLab/Fusion/issues/26>
  - <https://github.com/ActualLab/Fusion/issues/53>
  - <https://github.com/ActualLab/Fusion/issues/167>
  - <https://github.com/ActualLab/Fusion/pull/58>
  - <https://github.com/ActualLab/Fusion/pull/114>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/Benchmarks.md>
  - <https://github.com/ActualLab/Fusion.Samples/tree/master/src/RpcBenchmark>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/RpcBenchmark.csproj>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Program.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/GlobalUsings.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/CommandLine/TestCommand.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/CommandLine/BenchmarkCommandBase.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/CommandLine/ClientCommand.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/BenchmarkRunner.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/BenchmarkWorker.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/GrpcBenchmarkWorker.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/ParameterSearcher.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/Clients/ClientFactories.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Client/Clients/GrpcTestClient.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Server/TestService.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Server/GrpcTestService.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Contracts/ITestService.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Contracts/HelloWorld.proto>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/RpcBenchmark/Contracts/Examples.cs>
  - <https://raw.githubusercontent.com/ActualLab/Fusion.Samples/master/src/ActualLab.Benchmarking/BenchmarkRunnerBase.cs>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/441>
  - <https://azuresearch-usnc.nuget.org/query?q=packageid:ActualLab.Rpc&prerelease=false>
  - <https://hn.algolia.com/api/v1/search?query=ActualLab&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22ActualLab.Rpc%22>
  - <https://hn.algolia.com/api/v1/search?query=%22Stl.Fusion%22>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/actuallab/fusion`) · [data/wave5/enrich/raw/github_com_actuallab_fusion.json](../../../data/wave5/enrich/raw/github_com_actuallab_fusion.json) (enrichment confidence 0.55)

</details>
