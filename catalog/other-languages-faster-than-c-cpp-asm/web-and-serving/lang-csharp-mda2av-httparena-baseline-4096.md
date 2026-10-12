# C# NativeAOT minima-sync (HttpArena entry)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> Benchmark-only NativeAOT C# io_uring HTTP/1.1 server; ties libreactorng (C) and beats nginx 1.34x on HttpArena baseline-4096.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG) and libreactorng (C, io_uring, gcc -O3 -march=native) implementing the same HttpArena endpoints |
| **Claimed result** | baseline-4096: 4,386,544 req/s vs nginx 3,284,513 (1.34x, derived from page data), h2o 3,641,609 (1.20x), mongoose 3,707,598 (1.18x), libioma 4,255,834 (1.03x), libreactorng 4,377,377 (1.00x, parity) and Drogon 2,022,710 (2.17x); the Zig io_uring entry zeemo is ahead at 4,422,489 and libxev (Zig) ties at 4,381,919, all at the roughly 4.4M req/s baseline ceiling the suite itself names in scripts/lib/profiles.sh. pipelined-4096 (reference-only): 57,140,640 vs libreactorng 43,424,448 (1.32x), h2o 4,938,603 (11.6x), nginx 4,037,345 (14.2x); libioma and mongoose have no pipelined result. limited-conn-4096: 2,687,059 vs libioma 2,707,029 (0.99x), mongoose 2,701,933 (0.99x), libreactorng 2,685,717 (1.00x), h2o 2,651,569 (1.01x), nginx 2,626,297 (1.02x). Ordinary .NET servers in the same suite: Kestrel 1,320,795 and ASP.NET Core minimal 1,305,946 req/s at baseline-4096. |
| **Workload** | HttpArena baseline (mixed GET/POST with query parsing, 4096 connections), 16x pipelined and limited-conn profiles for a synchronous single-issuer io_uring HTTP/1.1 server written in C# and compiled with NativeAOT: one pinned reactor thread per core, multishot accept, parse-in-place, responses serialized straight into the send buffer. Code lives in frameworks/minima-sync of the HttpArena repo. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine per site/data/current.json: AMD Ryzen Threadripper PRO 3995WX 64-Cores (64 cores, 128 threads), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), CPU governor performance; each entry runs in a container. current.json is undated and may differ from the machine state of the run behind a given results file. |
| **Compiler and flags** | C#: mcr.microsoft.com/dotnet/sdk:10.0 image, 'dotnet publish -c Release -r linux-x64 -p:PublishAot=true' with clang and zlib1g-dev for the native link; csproj sets PublishAot, Optimize, ServerGarbageCollection, InvariantGlobalization and AllowUnsafeBlocks, and no IlcInstructionSet, so the binary targets generic x86-64. The io_uring bindings are C# (raw io_uring_setup/enter/register through libc syscall(), mmap'd rings), not liburing. C side: libreactorng at pinned commit 7a65f8b plus a connection-close patch, library configured with CFLAGS='-O3 -march=native' and server.c built with gcc -O3 -march=native (ubuntu:24.04 build-essential, compiler version not stated); nginx 1.31.4 with a custom handler module, --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie build-essential, version not stated); libioma and mongoose -O3 -march=native with LTO, h2o CMake Release with clang -march=native, Drogon handler only against the prebuilt drogonframework/drogon:latest image. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Synchronous single-issuer io_uring reactor (SINGLE_ISSUER\|DEFER_TASKRUN), one pinned thread per core, parse-in-place and zero hot-path allocation under NativeAOT (frameworks/minima-sync README); same design as the C entries, no language-level mechanism claimed. |
| **Adoption** | HttpArena repo has 128 stars; the Minima io_uring bindings it reuses live in a separate HttpArena entry whose own repository was not found |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/MDA2AV/HttpArena) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/minima-sync.json) |

## Verdict

HttpArena on an AMD Ryzen Threadripper PRO 3995WX (Ubuntu 24.04, kernel 6.17, Docker, loopback, gcannon with 4,096 connections, best of 3 five-second runs): the NativeAOT C# entry served 4,386,544 req/s on baseline-4096 against 4,377,377 for libreactorng (C, io_uring, gcc -O3 -march=native; 1.00x) and 3,284,513 for nginx 1.31.4 (custom module, -O3 -march=native; 1.34x); pipelined-4096 57.1M against 43.4M (1.32x); limited-conn-4096 2,687,059 against 2,685,717 (1.00x). The rows come from separate runs weeks apart, and the algorithms differ (hand-rolled parser and minimal responses against libreactor's parser, and against nginx on epoll); all ratios are derived from page data.

## Use it when

- As a reference design for a thread-per-core io_uring HTTP/1.1 server in .NET without a runtime: NativeAOT reached 4,386,544 req/s on baseline-4096, level with libreactorng (C, 4,377,377) and 1.34x nginx 1.31.4 (3,284,513), on a 64-core Threadripper PRO 3995WX.
- Plain-text keep-alive or pipelined HTTP/1.1 microservices where every handler is CPU-only and short, so a synchronous reactor never blocks: pipelined-4096 57.1M req/s against libreactorng's 43.4M (1.32x) and nginx's 4.04M (14x).
- Studying how far C# can go with raw syscalls, NativeMemory buffers and AllowUnsafeBlocks: it matched the C io_uring server on CPU per request at a fixed 1M req/s (18.97 us against libreactorng's 21.04 us).

## Skip it when

- Anything with blocking or slow handlers (database calls, file I/O): the README says the synchronous reactor blocks the core, and the entry does not run the async-db, crud or TLS profiles.
- Tail-latency-sensitive services: at a fixed 1M req/s its p99.9 was 24,808 us against libreactorng's 687 us (about 36x worse), and at 10k req/s 1,012 us against 182 us; it also used 14% more CPU per request than libreactorng at 10k req/s (28.73 us against 25.21 us).
- As proof that C# beats C: against the C server built the same way it is a tie (1.00x on baseline-4096 and limited-conn-4096), it trails libioma and mongoose on limited-conn, and the margin over nginx compares an io_uring reactor with minimal responses against an epoll server that sends about twice the bytes per response.
- Production traffic: it is benchmark code with no Date header, no method check, a 200 answer with the a+b sum for any path outside /pipeline and /json/, an 8 KB request limit enforced by closing the connection without a 431, and no TLS or HTTP/2.

## How it is fast

Each allowed CPU gets one pinned reactor thread with its own SO_REUSEPORT listener and its own io_uring created with SINGLE_ISSUER | DEFER_TASKRUN through raw io_uring_setup/enter syscalls, with no liburing. It uses multishot accept and a single-shot recv into a per-connection native buffer; requests are parsed in place with span searches, and every response parsed from one read is written straight into a 16 KB native send buffer and flushed with one send, all inline on the reactor with no async machinery or hot-path allocation. Responses are minimal (status line, Content-Type and Content-Length, no Date or Server header): about 63 bytes each against libreactorng's 109 and nginx's 135 (derived from page data). That, together with the batched flush, is why the 16-deep pipelined profile reaches 57.1M req/s against libreactorng's 43.4M.

## Compared with alternatives

Pick minima-sync over ioxide (the same author's reusable .NET io_uring runtime, 4.11M req/s on baseline-4096) only to study the fastest synchronous design; ioxide has async handlers, TLS, h2 and h3 and is a NuGet package. Kestrel (1.32M) is the choice for real ASP.NET Core apps, and zeemo (Zig, 4.42M) or libreactorng (C) give the same architecture in a systems language.

## Integration

| | |
|---|---|
| **Form** | source-drop (frameworks/minima-sync in the HttpArena repo: Program.cs, io_uring/Native.cs, io_uring/Ring.cs; no package) |
| **Dependencies** | none beyond the .NET base library and libc (io_uring through syscall(), not liburing); clang and zlib1g-dev at build time for the NativeAOT link |
| **Minimum toolchain** | .NET SDK 10 with NativeAOT (csproj targets net10.0, PublishAot, AllowUnsafeBlocks; Docker build on mcr.microsoft.com/dotnet/sdk:10.0, runtime image debian:bookworm-slim) |
| **Platforms** | Linux x86-64 only (published for linux-x64 with no IlcInstructionSet, so generic x86-64 code). The kernel must accept IORING_SETUP_SINGLE_ISSUER \| DEFER_TASKRUN and io_uring must be allowed by seccomp (HttpArena runs it with seccomp=unconfined). The entry states no minimum kernel; it was measured on 6.17. |
| **Thread safety** | Shared-nothing: each reactor owns its ring, listener, connection slots, pool and native buffers, and handlers run synchronously on the reactor thread. Nothing is designed for cross-thread use; the only shared state is the read-only dataset. |
| **Drop-in for the baseline** | no |

## Gotchas

- Cross-run comparison: the code has not changed since PR #824 (2026-06-07), and the baseline-4096, pipelined-4096 and limited-conn-4096 rows were already present, unchanged, when results were split per framework on 2026-07-24 (commit 5698fa8). They were therefore measured between June 7 and July 24, about six weeks or more before the libreactorng row (2026-09-07) and before the August nginx rows it is compared with. That is earlier than the verifier's 'on or before 2026-08-29'. Kernel, harness and machine state in between are not documented (current.json is undated).
- Error paths drop requests silently. If a pipelined batch overflows the 16 KB write buffer, Handle() returns -1 and the connection is closed after the buffered responses, so the remaining requests get no answer. A request whose headers exceed the 8 KB receive buffer is closed without a response. A chunked body longer than 256 bytes is silently truncated, so the computed sum is wrong. None of these triggers on HttpArena's small requests.
- Smaller responses are part of the win: about 62.9 bytes per response on baseline-4096 against 108.7 for libreactorng and 135.4 for nginx (bandwidth divided by req/s, derived), consistent with omitting the Date and Server headers. HttpArena's validate.sh checks only status, body and Content-Type, so this is within the rules, but servers that send Date do more work per response.
- The C# binary targets generic x86-64 while the C competitors are built with -O3 -march=native, and runs are best of 3 five-second runs (RUNS=3 in scripts/lib/common.sh), with gcannon pinned to CPUs 32-63,96-127 and the server to 0-31,64-95.

## Known shortcomings

- Parity with libreactorng (C) at the suite's own \~4.4M req/s ceiling; behind libioma and mongoose on limited-conn; wins only against epoll servers with bigger responses or on the reference-only pipelined profile (unequal work); entry written by the suite owner MDA2AV; runs best of 3 from different dates.
- The code has been unchanged since PR #824 (2026-06-07) and the baseline, pipelined and limited-conn rows were already present at commit 5698fa8 (2026-07-24), so the measurement dates from June-July, not 'on or before 2026-08-29'; it is cross-run against libreactorng (2026-09-07) and nginx (August). latency-1m p99.9 is 24,808 us against libreactorng's 687 us (36x worse). Silent drops: a write-buffer overflow closes the connection and a chunked body over 256 bytes is truncated; no Date header, and validate.sh checks only Content-Type among headers.

## Caveats and trade-offs

Parity, not a win, against the C server with the same design: 1.00x libreactorng at baseline-4096 and limited-conn-4096, below libioma and mongoose at limited-conn, and the top baseline entries (zeemo, minima-sync, libxev, libreactorng) sit within 4% at the roughly 4.4M req/s ceiling that scripts/lib/profiles.sh names, with the gcannon load generator pinned to the other half of the machine (CPUs 32-63,96-127). The gains over nginx (1.34x), h2o and mongoose compare a minimal io_uring server against epoll servers and different response sizes (62.9 bytes per response vs nginx 135.4, Drogon 134.4, libreactorng 108.7, libioma 85.8, mongoose 72.5; derived from bandwidth divided by req/s), so same_algorithm is false. The pipelined profile (16x batched) is reference-only in HttpArena's composite score. The contender was written by the suite owner MDA2AV (PR #824, 2026-06-07) and exists only inside the HttpArena repo (meta.json repo is empty), modelled on the Zig zeemo architecture; the same-owner ioxide entry was tiered C in this wave while suite-owner entries such as kestrel kept A. Results are best of 3 runs of 5 s each (RUNS=3 in scripts/lib/common.sh), not one run, but the JSON files are undated and rows come from different runs on the same machine: minima-sync.json was last re-measured on or before 2026-08-29 (later commits only dropped profiles), libreactorng.json on 2026-09-07 and nginx.json in August. C/C++ entries are built -O3 -march=native (libioma and mongoose with LTO) or CMake Release with clang -march=native (h2o), while the C# binary targets generic x86-64, so the flags favour the C side; Drogon compiles only its handler against the prebuilt drogonframework/drogon:latest image, so the Drogon ratios are weaker evidence. The C competitor handlers are minimal hand-written servers by the suite maintainers or contributors, not tuned production configurations. The ordinary .NET servers are far slower than nginx at baseline-4096 (Kestrel 1,320,795 req/s). [retier] The code has been unchanged since PR #824 (2026-06-07) and the rows were already present at 5698fa8 (2026-07-24), so the measurement dates from June-July 2026 and is cross-run against libreactorng (2026-09-07) and nginx (August). latency-1m p99.9 is 24,808 us against libreactorng's 687 us. Silent drops: a write-buffer overflow closes the connection and a chunked body over 256 bytes is truncated; no Date header.

Benchmark-only synchronous reactor that blocks the core on slow handlers (the README says so); does not run the async-db, crud or TLS profiles; Linux io_uring only; NativeAOT drops reflection-based .NET features.

## Maintenance

The HttpArena repo is active (128 stars, MIT, last commit 2026-10-11), but this entry's code has not changed since 2026-06-07 and its H1 numbers predate 2026-07-24; it is copyable MIT benchmark code with no repository of its own, no API and no maintainers listed in meta.json, so treat it as a design reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/minima-sync.json and the sibling nginx, libreactorng, h2o, mongoose, libioma and drogon JSON files; the code is public (frameworks/minima-sync/{Dockerfile,minima-sync.csproj,Program.cs,io_uring/Native.cs,io_uring/Ring.cs}, frameworks/libreactorng/Dockerfile, frameworks/nginx/{Dockerfile,ngx_http_httparena_module.c}, scripts/benchmark.sh, scripts/lib/profiles.sh), flags are in the Dockerfiles and the CPU (Threadripper PRO 3995WX) in site/data/current.json, the HttpArena tier-A precedent (actix, dusty, libxev, kestrel, tokio-uring).
- **Verifier notes:** All numbers verified against the HttpArena JSON files; metadata confirmed (MIT, 128 stars, last commit 2026-10-11, not a fork). Tier A kept on the HttpArena precedent. Corrected: same_algorithm false, runs are best of 3 not one, compiler details. Shortcomings to record: parity with libreactorng (C) at the harness's 4.4M req/s ceiling and behind libioma and mongoose on limited-conn; wins only over epoll servers with larger responses or on the reference-only pipelined profile; contender written by the suite owner (ioxide precedent was C); cross-run rows.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-48 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/commits/main>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/zeemo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/libxev.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/kestrel.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/aspnet-minimal.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/edixoi.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data/results>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data/rounds>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/rounds/1.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/rounds/2.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/minima-sync>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/minima-sync/io_uring>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/minima-sync.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/Program.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/io_uring/Native.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/io_uring/Ring.cs>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/minima-sync>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/minima-sync.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/libreactorng.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/pull/1396>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/libreactorng>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/libreactorng/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/libreactorng/meta.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/nginx>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/libioma/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/mongoose/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/h2o/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/zeemo/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/common.sh>
- **Sources the enricher read:**
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/libreactorng>
  - <https://github.com/MDA2AV/HttpArena/tree/main/scripts>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/minima-sync>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/minima-sync.json>
  - <https://github.com/MDA2AV/HttpArena/commit/f3b6abb>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/minima-sync.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/Program.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/io_uring/Native.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/minima-sync/io_uring/Ring.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/libreactorng/src/server.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5698fa8/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/f78b367/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/8f6740e/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/validate.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/content/docs/add-framework/implementation-rules/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/content/docs/add-framework/implementation-rules/engine.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/zerg.json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:csharp/mda2av/httparena#baseline-4096`) · [data/wave14/enrich/raw/lang_csharp_mda2av_httparena_baseline_4096.json](../../../data/wave14/enrich/raw/lang_csharp_mda2av_httparena_baseline_4096.json) (enrichment confidence 0.6)

</details>
