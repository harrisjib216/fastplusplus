# Kestrel (ASP.NET Core HTTP server, HttpArena kestrel entry)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> ASP.NET Core's managed HTTP server; in HttpArena it beats nginx on pipelined and cleartext HTTP/2 but loses on plain HTTP/1.1, TLS and HTTP/3.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG); h2o (C), agensio, proxygen, userver and Drogon (C++) rows in the same suite |
| **Claimed result** | pipelined-4096: 7,438,251 req/s vs nginx 4,037,345 (1.84x, derived from page data), h2o 4,938,603 (1.51x), agensio (C++) 4,958,241 (1.50x), proxygen 1,857,311 (4.0x), but Drogon 7,801,404 (0.95x) and libreactorng 43,424,448 (0.17x). baseline-h2c-256: 2,884,638 vs nginx 2,456,329 (1.17x), but proxygen 5,881,888 (0.49x) and agensio 15,185,367 (0.19x). json-comp-4096: 478,176 vs userver (C++) 297,311 (1.61x), proxygen 243,887 (1.96x), Drogon 127,466 (3.75x). Slower than nginx on most other profiles: baseline-4096 1,320,795 vs 3,284,513 (0.40x), baseline-h2-256 2,360,754 vs 3,414,750 (0.69x), json-tls-4096 617,570 vs 1,313,755 (0.47x), limited-conn-4096 455,508 vs 2,626,297 (0.17x). |
| **Workload** | HttpArena profiles for Kestrel with a single RequestDelegate (no routing, MVC or model binding): 16x pipelined HTTP/1.1, cleartext h2c baseline, gzip JSON, plus HTTP/1.1 baseline, TLS and h2 profiles where it is slower. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node, 8x DDR4-3200), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json; site/content/docs/hardware/_index.md). The server container runs with seccomp=unconfined on the cpuset 0-31,64-95 for the H/1.1 profiles and the load generator on CPUs 32-63,96-127 of the same machine over loopback (scripts/lib/framework.sh, scripts/lib/profiles.sh, scripts/lib/common.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. TechEmpower Round 22 plaintext: 'Dell R440 Xeon Gold + 10 GbE' as printed on the leaderboard image; the gnet README describing that environment gives 28 HT cores of Intel Xeon Gold 5120. |
| **Compiler and flags** | kestrel: mcr.microsoft.com/dotnet/sdk:10.0, dotnet publish -c Release, net10.0 with ServerGarbageCollection=true and InvariantGlobalization=true (frameworks/kestrel/{Dockerfile,kestrel.csproj}); runs on the JIT (no NativeAOT). C/C++ rows: nginx 1.31.4 with a custom C handler module built --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); h2o pinned commit ccea64b, clang CMake Release -march=native -mtune=native, no LTO; mongoose 7.23 gcc-14 -O3 -march=native -flto; libreactorng pinned 7a65f8b and its server gcc -O3 -march=native; agensio v0.1.0-alpha.23 CMake Release -DAGENSIO_NATIVE=ON; proxygen CMake Release on the pinned facebook/proxygen base image with mimalloc; Drogon CMake Release (handler only) on the unpinned drogonframework/drogon:latest image; userver v3.2 image, CMake Release -march=native; hical gcc-14 CMake Release -march=native -mtune=native (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Kestrel's pipelined parsing and h2c framing paths on .NET sockets with its own HTTP/2 implementation; HttpArena gives no explicit mechanism and the baseline HTTP/1.1 row shows the managed stack losing to nginx. |
| **Adoption** | 38.5k stars (dotnet/aspnetcore); the default ASP.NET Core server |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/dotnet/aspnetcore) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/kestrel.json) |

## Verdict

In HttpArena on a Threadripper PRO 3995WX (server on 64 logical CPUs, load generator on the other 64, loopback, best of 3 runs of 5 s), Kestrel on .NET 10 with a single RequestDelegate served 7.44M req/s pipelined (16 deep) vs nginx 1.31.4's 4.04M (1.84x), 2.88M vs 2.46M req/s on cleartext HTTP/2 with 256 connections (1.17x) and 478k req/s on gzip/brotli JSON vs userver 297k (1.61x), but only 0.40x nginx on plain HTTP/1.1 keep-alive, 0.47x on JSON over TLS and 0.14x on HTTP/3 (all ratios derived from page data).

## Use it when

- You are already on .NET and need an in-process HTTP server: Kestrel with a raw RequestDelegate measured 1.32M req/s on HttpArena baseline-4096 and 2.88M req/s on cleartext HTTP/2 with 256 connections, without a reverse proxy.
- Internal cleartext HTTP/2 (h2c) service traffic with many streams per connection, where it edged nginx 1.17x on baseline-h2c-256 once the entry raised MaxStreamsPerConnection to 256 and the flow-control windows to 1-2 MiB.
- Clients that pipeline HTTP/1.1 requests in bulk (7.44M req/s at 16-deep pipelining, 1.84x nginx), though browsers and proxies no longer pipeline.
- Gzip or brotli JSON APIs where you compare against C++ frameworks rather than nginx: 478k req/s on json-comp-4096 vs userver 297k and Drogon 127k, with brotli quality 1 from .NET's native encoder.

## Skip it when

- As a faster nginx for plain HTTP/1.1 keep-alive traffic: baseline-4096 1.32M req/s is 0.40x nginx (3.28M) and 0.36x h2o (3.64M), and 0.65x Drogon.
- Connection-churn heavy loads: limited-conn-4096 (reconnect every 10 requests) 456k req/s is 0.17x nginx; the entry leaves the socket Backlog at its 512 default.
- TLS termination and HTTP/3: json-tls-4096 0.47x nginx, baseline-h2-256 0.69x nginx and 0.15x h2o (16.1M), baseline-h3-64 0.14x nginx.
- Memory-tight hosts on HTTP/2: the entry's h2c footprint grows from 941 MiB at 256 connections to 8.1 GiB at 4,096 (server GC on), against 117-279 MiB for h2o on its HTTP/2 profiles.
- Startup-sensitive or tiny deployments: the entry runs on the JIT with tiered compilation (no NativeAOT), so peak numbers assume a warmed process.

## How it is fast

Kestrel parses HTTP/1.1 straight out of System.IO.Pipelines buffers with SequenceReader and vectorized IndexOfAny searches for CR, LF, space and '?', stack-allocating small header lines, and writes responses into pooled pipe memory. The socket transport spreads completions over IOQueue workers sized from the processor count. Its HTTP/2 encoder indexes response headers in an HPACK dynamic table (DynamicHPackEncoder): on baseline-h2c-256 Kestrel sent about 25 bytes per response against nginx's 60 (derived from page data), which helps it pass nginx there. HttpArena states no mechanism, and the pipelined gain over nginx comes from the 16-deep pipelined batches rather than per-request speed.

## Compared with alternatives

Pick Kestrel over the HttpArena C# NativeAOT minima-sync entry, nilo or Helidon SE when you need a supported, full-protocol server (TLS, HTTP/2, HTTP/3) inside an ASP.NET Core app rather than the fastest number: minima-sync beats nginx 1.34x on baseline-4096 where Kestrel reaches 0.40x, and nilo reaches 3.67x nginx on baseline-h2c-256 against Kestrel's 1.17x.

## Integration

| | |
|---|---|
| **Form** | module (part of the Microsoft.AspNetCore.App shared framework; Microsoft.NET.Sdk.Web project) |
| **Dependencies** | .NET runtime and ASP.NET Core shared framework; libmsquic for HTTP/3 on Linux (installed in the entry's Dockerfile) |
| **Minimum toolchain** | .NET 10 SDK as benchmarked (net10.0, mcr.microsoft.com/dotnet/sdk:10.0); Kestrel ships with every ASP.NET Core release |
| **Platforms** | Windows, Linux and macOS per the repository description; benchmarked on Linux x86-64 (Zen 2) in Docker |
| **Thread safety** | not documented in the sources read (the server handles concurrency; handlers run on the .NET thread pool) |
| **Drop-in for the baseline** | partial — it replaces a hand-written nginx or C++ handler only if you rewrite the handler in C#; it has no nginx-style config, proxying or static-file module beyond what you code or add as middleware |

## Gotchas

- Harness flaw on json-comp: HttpArena's requests send 'Accept-Encoding: gzip, br', so Kestrel answers with brotli quality 1 while the C++ rows use their own encoders; Kestrel's responses average 1,582 bytes against Drogon's 1,392 (derived from page data), so it ships about 14% more bytes per response and the 1.6-3.8x wins compare different compressors and outputs. Engines are not scored on compression profiles, and pipelined is reference-only, so the profiles Kestrel wins mostly do not count on its own board.
- The record's memory tradeoff is only half right: on the HTTP/1.1 throughput profiles Kestrel used 118-590 MiB (1.5 GiB on async-32000) while nginx used 3.5-3.8 GiB in every profile, but h2o used 69-308 MiB and Kestrel's HTTP/2 memory climbs to 3.9-8.1 GiB at 1,024-4,096 connections.
- Kestrel does not saturate the box on plain HTTP/1.1: on baseline-4096 it used 5,589% CPU of a 64-thread cpuset vs nginx's 6,444% (derived from page data), matching open issue dotnet/aspnetcore#68915 (2026-08-31: about 20% of a 24-core host idle under high-concurrency HTTP/1.1, reproduced on .NET 8, 10 and 11; IOQueueCount and socket thread-count tweaks did not fix it).
- The HttpArena entry is maintained by the suite owner, not the ASP.NET team; its README still says JSON is serialized once at startup while Dataset.cs serializes per request, and rows for Kestrel and the C/C++ servers come from separate runs days apart.

## Known shortcomings

- HttpArena: 0.40x nginx on baseline, 0.17x limited-conn, 0.14x h3; the pipelined win is reference-only and loses to Drogon and Cutelyst; json-comp has no C rows and Kestrel serves brotli q1 via native C libraries. Entry README's 'serialized once at startup' is stale (Dataset.cs serializes per request); the TechEmpower screenshot is a 0.17% tie; rows from different runs on the same machine.
- Harness flaw on json-comp: HttpArena requests send 'Accept-Encoding: gzip, br', so Kestrel serves brotli q1 while the other rows use their own encoders; its responses average 1,582 bytes against Drogon's 1,392 (about 14% more), and engines are not scored on compression profiles. The h2c win is partly HPACK dynamic-table use (25 vs nginx 60 bytes per response, derived). The record's memory trade-off against nginx was wrong: nginx sits at 3.5-3.8 GiB everywhere while Kestrel uses 118-590 MiB on HTTP/1.1 and 3.9-8.1 GiB on HTTP/2. Baseline CPU 5,589% vs nginx 6,444% matches open issue dotnet/aspnetcore#68915 (idle cores under HTTP/1.1 load).

## Caveats and trade-offs

Weak claim. Kestrel is far behind the C and C++ servers on the main HTTP/1.1 profile: baseline-4096 1,320,795 is 0.40x nginx and 0.65x Drogon, limited-conn-4096 455,508 is 0.17x nginx, baseline-h2-256 2,360,754 is 0.69x nginx (h2o 16.1M), and baseline-h3-64 668,997 is 0.14x nginx (4.85M). The pipelined win over nginx is mostly nginx's pipelining cost, Kestrel loses pipelined to Drogon and Cutelyst, and pipelined is reference-only in HttpArena's framework and engine scoring. json-comp: nginx and h2o do not run it, so it compares only against the C++ frameworks; the entry answers brotli at quality 1 when the client offers br (gzip CompressionLevel.Fastest otherwise) and its responses average 1,582 bytes against 1,320 to 1,393 for the other rows (derived from page data), so the encoders and output differ; .NET's BrotliEncoder and GZipStream run native C brotli and zlib code. The frameworks/kestrel/README.md claim that JSON is serialized once at startup is stale: Dataset.cs serializes per request and says it keeps no precomputed responses. Kestrel is entered as type 'engine', so it is ranked on the engine board, not against the C++ frameworks. The entry is maintained by the suite owner (MDA2AV), not the ASP.NET team. Each number is the best of 3 runs of 5 s; rows come from different runs on the same machine (kestrel.json 2026-09-05, nginx.json and h2o.json 2026-08-30, drogon.json 2026-09-06, userver.json 2026-09-11 per git history). The TechEmpower plaintext tie is a 10 GbE-limited top group (ranks 1 to 13 within 0.8%, libreactor (C) rank 11 at 6,971,119), so it shows parity, not a win; that ranking is read from a screenshot in panjf2000/illustrations (benchmark/techempower-plaintext-top50-light.jpg), not the live results page. Every HttpArena entry is a minimal hand-written handler for the same endpoint contract (nginx runs a custom C handler module); Drogon is built against the unpinned drogonframework/drogon:latest image. [retier] json-comp: HttpArena requests send 'Accept-Encoding: gzip, br', so Kestrel serves brotli q1 while the C++ rows use their own encoders; Kestrel's responses average 1,582 bytes against Drogon's 1,392 (about 14% more), so the 1.6-3.8x wins compare different compressors and outputs, and engines are not scored on compression profiles. The h2c win is partly HPACK dynamic-table use (25 vs nginx 60 bytes per response). Memory correction: nginx sits at 3.5-3.8 GiB on every profile while Kestrel uses 118-590 MiB on HTTP/1.1 and 3.9-8.1 GiB on HTTP/2. Baseline CPU 5,589% vs nginx 6,444% matches open issue dotnet/aspnetcore#68915 (idle cores under HTTP/1.1 load).

Managed runtime with JIT warm-up, tiered compilation and a GC; memory use is much higher than the C entries (941 MiB to 8.1 GiB on the h2c profiles); full ASP.NET Core feature set sits above Kestrel.

## Maintenance

Actively developed by Microsoft (38.5k stars, 3.8k open issues, last commit 2026-10-09) and MIT-licensed; the speed claim is narrow, since Kestrel is a strong managed server that beats nginx only on the pipelined and h2c profiles, and its json-comp lead rests on a different compressor and larger responses.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded B to A: every quoted HttpArena number matches site/data/results/kestrel.json and the sibling nginx/h2o/hical/drogon/cutelyst/userver JSON files; the code is public (frameworks/kestrel/{Dockerfile,Program.cs,Dataset.cs,kestrel.csproj}, frameworks/nginx/Dockerfile, scripts/benchmark.sh), the .NET SDK and C/C++ flags are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json and the hardware docs, the HttpArena tier-A precedent; the entry is maintained by the suite owner, not by Microsoft. The TechEmpower R22 row was read on the gnet-hosted screenshot and is supporting evidence only.
- **Verifier notes:** Numbers verified (HttpArena JSON files and the TechEmpower screenshot); tier raised B to A on the HttpArena CPU-model precedent. Shortcomings to record: 0.40x nginx on baseline, 0.17x on limited-conn, 0.14x on h3; pipelined win is reference-only and loses to Drogon and Cutelyst; json-comp has no C rows and Kestrel serves brotli q1 via native C libraries; entry README's 'serialized once at startup' note is stale (code serializes per request); TechEmpower is a 0.17% tie; cross-run rows. same_opt_level left null (JIT vs -O3 -march=native; neither side crippled).
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-41 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/kestrel.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Program.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Dataset.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/kestrel.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/hical/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cutelyst/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/kestrel>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/kestrel.json>
  - <https://raw.githubusercontent.com/panjf2000/illustrations/HEAD/benchmark/techempower-plaintext-top50-light.jpg>
  - <https://raw.githubusercontent.com/panjf2000/gnet/HEAD/README.md>
  - <https://github.com/dotnet/aspnetcore>
  - <https://github.com/dotnet/aspnetcore/commits>
- **Sources the enricher read:**
  - <https://github.com/dotnet/aspnetcore>
  - <https://github.com/dotnet/aspnetcore/issues?q=is%3Aissue%20state%3Aopen%20label%3Aarea-networking%20perf%20HTTP%2F2>
  - <https://github.com/dotnet/aspnetcore/issues/68915>
  - <https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/Servers/Kestrel/Core/src/Internal/Http/HttpParser.cs>
  - <https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/Servers/Kestrel/Transport.Sockets/src/SocketTransportOptions.cs>
  - <https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/Servers/Kestrel/Core/src/KestrelServerLimits.cs>
  - <https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/Shared/Hpack/DynamicHPackEncoder.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Program.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/Dataset.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/kestrel.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/kestrel/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/kestrel.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://github.com/MDA2AV/HttpArena/tree/main/requests>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/json-gzip-1.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/json-gzip-50.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/pipeline.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/get.raw>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dotnet/aspnetcore`) · [data/wave14/enrich/raw/github_com_dotnet_aspnetcore.json](../../../data/wave14/enrich/raw/github_com_dotnet_aspnetcore.json) (enrichment confidence 0.5)

</details>
