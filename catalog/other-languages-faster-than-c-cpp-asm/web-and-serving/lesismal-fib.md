# fib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Go` · `no license` · 🟢 active

> Go event-loop networking library serving net/http handlers; beats Sogou workflow (C++) on HTTP/1 echo, ties uSockets on TLS.

| | |
|---|---|
| **Beats** | Sogou workflow (C++ HTTP server) and uSockets (C, BoringSSL) in the lesismal go-\*-benchmark repositories; nginx (C) in HttpArena |
| **Claimed result** | HttpArena (Threadripper PRO 3995WX; fib under prefork, 32 child processes; ratios derived from page data): over nginx baseline-h2c 5.25x, baseline-h2 1.65x, baseline-h3 1.25x, static-tls 1.71x, pipelined 5.05x (reference-only profile); behind nginx on json-tls (0.59x) and json-h2c (0.64x); agensio (C++) ahead. First-party go-http1-benchmark (single GitHub Actions run, 10,000 connections, 1 KiB): fib 194,671 TPS vs Sogou workflow (C++) 150,407 (1.29x), memory 32 MB vs 14 MB. |
| **Workload** | HTTP/1.1 echo, pipelined, TLS 1.3 echo and WebSocket echo benchmarks, 10,000 connections, 1 KiB payload, GitHub-hosted ubuntu-24.04 runners with 4 vCPUs (2 for server, 2 for client), single run each. |
| **Metric** | throughput |
| **Hardware** | HttpArena: AMD Ryzen Threadripper PRO 3995WX (site/data/current.json). First-party rows: GitHub Actions ubuntu-24.04 runner (the container got 4 vCPUs instead of the wanted 8). |
| **Compiler and flags** | Go 1.27; HttpArena entry built with CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' (frameworks/fib/Dockerfile). Baselines: workflow v1.1.0 built from source with CMAKE_BUILD_TYPE=Release and its server main.cc with c++ -std=c++11 -O3 -DNDEBUG (go-http1-benchmark frameworks/workflow/build.sh); uSockets server.c with cc -std=c11 -O3 -DNDEBUG on pinned uSockets and BoringSSL (go-tls-benchmark frameworks/usockets/build.sh); nginx 1.31.4 with a custom handler module at -O3 -march=native -DNDEBUG (HttpArena frameworks/nginx/Dockerfile). Compiler versions not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | A few event loops wait for I/O readiness and a shared worker pool does the work, so an idle connection costs no goroutine; pipelined requests are batched (README). |
| **Adoption** | 27 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/lesismal/fib) · [benchmark](https://raw.githubusercontent.com/lesismal/fib/HEAD/README.md) |

## Verdict

In the author's go-http1-benchmark (one GitHub Actions run, ubuntu-24.04 runner with 4 vCPUs split 2/2 between server and Rust tokio client, 10,000 connections, 1 KiB POST echo), fib at commit 4ffe768 built with Go 1.27 completed 194,671 round trips/s against Sogou workflow v1.1.0 (C++, Release build, server at -O3) at 150,407 (1.29x), using 32 MB vs 14 MB; in go-tls-benchmark against uSockets with BoringSSL (C) it tied on TLS 1.3 echo (103,427 vs 103,972) and reached 0.94x on TLS 1.3 pipelining. In HttpArena (Threadripper PRO 3995WX per site/data/current.json, separate runs) it trails nginx 1.31.4 on baseline-4096 (3,164,504 vs 3,284,513) and leads it on HTTP/2, HTTP/3 and static TLS profiles, where agensio (C++) is ahead of fib on the HTTP/2 rows.

## Use it when

- Go servers holding many mostly idle connections (WebSocket, long polling, device gateways): no goroutine per idle connection; 32 MB at 10,000 WebSocket connections vs 229 MB for gorilla in the author's run.
- Existing net/http handlers that need more HTTP/1.1 throughput, especially pipelined: 2.3x net/http on echo and 6.9x on pipelining in the author's go-http1-benchmark run.
- One Go engine serving HTTP/1.1, h2, h2c, HTTP/3 and gRPC: in HttpArena fib is ahead of nginx on baseline-h2-256 (1.65x), baseline-h2c-256 (5.25x), baseline-h3-64 (1.25x) and static-tls-1024 (1.71x), ratios derived from page data.
- TLS-terminating Go services on AES-GCM where crypto/tls over net costs throughput or memory: 2.3-2.9x crypto/tls pipelining on about a third of the memory, and a tie with uSockets plus BoringSSL on TLS 1.3 echo.

## Skip it when

- Anything you need to copy or vendor: the repository has no LICENSE file (raw LICENSE returns 404, the repo page shows no license), so by default no reuse rights are granted.
- Production-critical services today: on 2026-10-11 (issue #1) the author wrote that it has not yet been heavily used in production, that client-side work is still in progress, and advised starting with small features; 27 stars, no tagged releases on the repo page.
- Handlers that block (synchronous database calls, long waits) or keep request objects after returning: handlers run on scarce engine workers, and recycled Request/Header/URL/Context objects are handed to the next request once the handler returns.
- Peak throughput against the best C and C++ servers: in HttpArena it trails nginx on baseline-4096 (0.96x), json-tls-4096 (774,182 vs 1,313,755) and json-h2c-1024 (1,102,054 vs 1,730,838), agensio (C++) by 2.6x on baseline-h2-256 and 2.2x on json-tls, libreactorng (C) by 2.1x on pipelined-4096 and mongoose on most WebSocket profiles.
- Tight memory budgets: workflow serves the same HTTP/1 echo in 14 MB vs fib's 32 MB, and uSockets the TLS runs in 51 MB vs 180 MB.

## How it is fast

A few event loops only wait for readiness (edge-triggered epoll, kqueue, IOCP) and hand ready connections in one batch to a P-sharded, lock-free (Vyukov MPMC ring) worker pool, so an idle connection holds no goroutine and no I/O buffer. A worker reads until a short read, runs the parser and handler, and corks every response of the round into one writev or sendfile, which is where the pipelining numbers come from; on Linux sockets are read and written with raw recvfrom/sendto/sendmsg system calls. After the crypto/tls handshake fib runs the AES-GCM and AES-CBC record layers itself and decrypts in place, and request, header, URL and Context objects are recycled fasthttp-style to keep the Go heap and GC out of the hot path.

## Compared with alternatives

Pick fib over nilo (baseline-h2c-256 9,010,310 vs fib 12,891,491) or Helidon SE (baseline-h2-256 3,612,898 vs 5,634,126) when you want a Go codebase with net/http-style handlers and HTTP/1.1, h2, h2c, HTTP/3, WebSocket and gRPC on one engine; for raw HTTP/1.1 throughput the HttpArena siblings zix, zeemo, vanilla and minima-sync (4.3-4.4M req/s on baseline-4096 vs fib's 3.16M) are faster, and tokio-websockets ties it on echo-ws-limited-4096 (2,641,801 vs 2,613,729).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none outside the Go standard library (README); gRPC with google.golang.org/protobuf messages needs a codec registered with grpc.RegisterCodec |
| **Minimum toolchain** | Go 1.27 (go.mod) |
| **Platforms** | Linux (epoll, raw socket syscalls, prefork), macOS (kqueue), Windows (IOCP) on amd64, arm64, 386, arm, riscv64 and loong64; FreeBSD and other systems fall back to the standard net package |
| **Thread safety** | Each connection's events run one at a time, in FIFO order, on whichever worker is idle; handlers share the engine's worker pool (HTTP/2, HTTP/3, async arpc and gRPC handlers run on a separate streams pool). Recycled request objects belong to a handler only until it returns and releases every Retain; keep copies (Request.Clone, Header.Clone) for anything used later. |
| **Drop-in for the baseline** | partial — net/http handlers run on it unchanged within the documented limits, but it does not replace workflow, uSockets or nginx deployments, and it is a Go library rather than a C or C++ server |

## Gotchas

- Object reuse is on by default under fasthttp's RequestCtx rule: a net/http handler that keeps the \*http.Request, its Header or URL past its return (for example in a goroutine started without Retain) reads or writes another request's data. http.Hijacker is not implemented, so gorilla/websocket does not work, and Request.Context() is not cancelled when the client goes away.
- Writes never block and request bodies are buffered whole by default: a handler that writes faster than the peer reads queues the difference in memory (reads pause at a 64 KiB watermark, MaxPendingBytes is off by default), and over TLS SendFile reads and encrypts the whole range up front.
- The HttpArena numbers run under prefork: a child process per two CPUs (GOMAXPROCS=2 each, so 32 processes on 64 cores) sharing ports with SO_REUSEPORT; the docs say one process with 64 Ps stalls on Go's shared heap lock and GC (baseline 1.23M to 1.63M req/s only after object reuse). Children share nothing but the port, so in-memory state exists once per child and HTTP/3 datagrams after a NAT rebinding can reach a child without the connection.
- Harness limits of the headline numbers: go-\*-benchmark rows are single runs on a shared 4-vCPU GitHub runner whose run annotation says the container got 4 CPUs instead of the 8 it wants, with client and server on the same VM; workflow ran its stock benchmark server (2 pollers plus 20 handler threads on 2 vCPUs, Date formatted with strftime on every response vs fib's once-a-second cached Date) and has no pipeline row because it closes connections on pipelined input; the TLS pipeline rows (690,000, 735,000, 750,000) come from a rate-driven phase that measures how much of the offered rate each server held. HttpArena rows are cross-run (fib.json saved 2026-10-08 by the fib author, nginx.json 2026-08-30).

## Known shortcomings

- The only clear C/C++ win is HTTP/1 echo against workflow (-O3 Release), 1.29x in a single first-party run on a GitHub runner; TLS ties uSockets; uws_events is Go, not uWebSockets; on HttpArena nginx is ahead at baseline and agensio (C++) ahead on h2/h2c; no licence (reference).
- Identity kept by override: a w14-web-hn copy took the bare id at merge; the verified claim is the w14-web-papers one (batch-19).
- No correctness bug (the TLS CBC record check copies crypto/tls's constant-time logic; max_connections already raised to 2,000,000). Harness limits: single runs; the Actions annotation says the container got 4 CPUs, not the wanted 8; workflow ran its stock 2 pollers plus 20 handler threads on 2 vCPUs with strftime Date per response; the TLS pipeline is rate-driven. The record missed losses to nginx on HttpArena (json-tls 0.59x, json-h2c 0.64x); the HttpArena entry runs prefork (32 child processes). No LICENSE; the author says not production-proven (issue #1); object reuse is on by default (fasthttp rule); no http.Hijacker.

## Caveats and trade-offs

First-party single runs on noisy shared GitHub runners (the README says read differences of a few percent as ties); 2 vCPUs for the server, where workflow keeps its default 20 handler threads plus pollers. It loses to axum on HTTP/1 echo (236,244 vs 194,671), to uSockets on TLS pipelining (690,000 vs 735,000) and to the Go servers uws_std, fnet and uws_events on WebSocket pipelining; the workflow pipeline row is missing because workflow does not support pipelining. 'uws_events'/'uws_std' are Go servers on UIO, not uWebSockets; the C++ uWebSockets entry of go-websocket-benchmark is not shown in fib's table. In HttpArena (fib entry maintained by lesismal, CPU model not stated) it is slightly behind nginx at baseline-4096 (3,164,504 vs 3,284,513) and far ahead of nginx on h2c (12,891,491 at 256 connections vs 2,456,329), but agensio (C++) beats it on h2c (15,185,367) and h2 (14,744,015 vs 5,634,126 at 256), libreactorng (C) beats it on pipelined-4096 (43,424,448 vs 20,397,414) and mongoose (C) on most WebSocket profiles; fib leads static-tls-1024 (1,229,892 vs agensio 1,191,970 and nginx 720,869). No LICENSE file in the repo. [retier] HttpArena rows are cross-run against nginx's (different dates) and agensio is ahead; the entry runs prefork with 32 child processes (GOMAXPROCS=2 each) because one process with 64 Ps stalls on Go's shared heap lock and GC. First-party rows are single runs on a shared 4-vCPU runner with client and server on one VM, workflow at its stock 2 pollers plus 20 handler threads with strftime Date per response, and the TLS pipeline rate-driven. No LICENSE; the author says not production-proven (issue #1); object reuse is on by default (fasthttp rule); no http.Hijacker.

Event-loop networking library for Go that keeps the net/http handler model; no LICENSE file found in the repo, so reference only; uses far more memory than workflow (32 MB vs 14 MB) and TLS 1.3 pipelining uses 180 MB vs 51 MB for uSockets.

## Maintenance

Actively developed (last commit 2026-10-11, 297 commits, 27 stars, no tagged releases on the repo page) and, by the author's own account, not yet proven in heavy production use; with no LICENSE file it stays reference-only. No correctness bug was found behind the measured numbers (the hand-written TLS CBC record check copies crypto/tls's constant-time padding logic), but the first-party rows are single runs with the harness limits listed under gotchas. HttpArena's machine model is in site/data/current.json (Threadripper PRO 3995WX) and fib's Go build flags are in frameworks/fib/Dockerfile, so its HttpArena wins over nginx (h2c 5.25x, h2 1.65x, h3 1.25x, static-tls 1.71x, pipelined 5.05x, derived from page data) meet the same basis on which dusty, wtx and cutelyst were tiered A, subject to the cross-run and agensio caveats.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** The README Benchmarks section shows fib 194,671 vs workflow (C++) 150,407 echo TPS, TLS 1.3 echo 103,427 vs uSockets 103,972, all from the author's own lesismal/go-\*-benchmark repos (public code; workflow built -O3 Release in frameworks/workflow/build.sh) as single runs on GitHub-hosted 4-vCPU runners with no CPU model stated, so first-party C. The HttpArena rows are from a third-party harness (128 stars) whose fib entry is maintained by lesismal, with no CPU model stated; they show fib behind nginx at baseline-4096, so they do not lift the tier.
- **Retiered** C to A: Enricher: HttpArena publishes fib's Dockerfile build flags and the machine (Threadripper PRO 3995WX), so its HttpArena rows against nginx (h2c 5.25x, h2 1.65x, h3 1.25x, static-tls 1.71x, pipelined 5.05x; json-tls 0.59x, json-h2c 0.64x) meet the basis on which dusty, wtx and cutelyst are A; the first-party GitHub Actions rows stay as single-run caveats. C to A (reference usability: no LICENSE).
- **Verifier notes:** Numbers match the README; tier C stays (author-run benchmark repos, single runs, no CPU model). Main shortcoming: the only clear win over a C/C++ server is HTTP/1 echo vs workflow (1.29x); TLS is a tie, the WebSocket runner-up the record cited (uws_events) is a Go server, and in HttpArena nginx is ahead at baseline while agensio (C++) is ahead on h2/h2c. No license (reference); 27 stars, last commit 2026-10-11.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-19 (wave 14); orchestrator (wave 14 merge); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/README.md>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/LICENSE>
  - <https://github.com/lesismal/fib>
  - <https://github.com/lesismal/fib/commits>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/frameworks/workflow/build.sh>
  - <https://github.com/lesismal/go-http1-benchmark/actions/runs/36839290265>
  - <https://raw.githubusercontent.com/lesismal/go-websocket-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/lesismal/go-tls-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/lesismal/go-tls-benchmark/HEAD/frameworks/usockets/build.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/fib.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/fib/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/fib/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
- **Sources the enricher read:**
  - <https://github.com/lesismal/fib>
  - <https://github.com/lesismal/fib/issues?q=is%3Aissue>
  - <https://github.com/lesismal/fib/issues/1>
  - <https://github.com/lesismal/fib/tree/main/http>
  - <https://github.com/lesismal/fib/tree/main/tls>
  - <https://github.com/lesismal/fib/tree/main/c>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/README.md>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/go.mod>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/config.go>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/http/response_writer.go>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/tls/record.go>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/tls/fast.go>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/docs/http1.md>
  - <https://raw.githubusercontent.com/lesismal/fib/HEAD/docs/hacks.md>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/README.md>
  - <https://github.com/lesismal/go-http1-benchmark/tree/main/frameworks/workflow>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/frameworks/workflow/main.cc>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/frameworks/workflow/build.sh>
  - <https://github.com/lesismal/go-http1-benchmark/tree/main/frameworks/fib>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/frameworks/fib/server.go>
  - <https://raw.githubusercontent.com/lesismal/go-http1-benchmark/HEAD/script/config.sh>
  - <https://github.com/lesismal/go-http1-benchmark/actions/runs/36839290265>
  - <https://raw.githubusercontent.com/lesismal/go-tls-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/fib.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/fib/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/fib/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/fib.json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/lesismal/fib`) · [data/wave14/enrich/raw/github_com_lesismal_fib.json](../../../data/wave14/enrich/raw/github_com_lesismal_fib.json) (enrichment confidence 0.75)

</details>
