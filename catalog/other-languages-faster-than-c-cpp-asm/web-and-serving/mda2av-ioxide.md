# ioxide

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Shared-nothing io_uring runtime for .NET; a hand-written HTTP/1.1 handler on it outruns nginx 1.25x on HttpArena baseline-4096.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C) and h2o (C) in the HttpArena suite; also libreactorng and libioma (C, io_uring), mongoose (C) and agensio (C++) |
| **Claimed result** | baseline-4096: 4,111,381 req/s vs nginx 3,284,513 (1.25x, derived from page data), h2o 3,641,609 (1.13x), mongoose 3,707,598 (1.11x), agensio 3,558,559 (1.16x). pipelined-4096: 53,376,982 vs nginx 4,037,345 and libreactorng 43,424,448. baseline-h2-1024: 12,235,767 vs nginx 3,320,285 (3.7x). |
| **Workload** | HttpArena baseline (mixed GET/POST with query parsing, 4096 connections), pipelined and HTTP/2 profiles for a hand-written HTTP/1.1 handler on ioxide, a shared-nothing io_uring runtime for .NET (one ring per reactor thread, raw syscalls without liburing). |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated 64-core machine, containers per entry (README says '64-core dedicated hardware'; CPU model, RAM, NIC and kernel not stated) |
| **Compiler and flags** | .NET SDK 11.0.100-preview.7 / runtime 11.0.0-preview.7, dotnet publish -c Release with ServerGarbageCollection and runtime-async=on (HttpArena frameworks/ioxide/Dockerfile and ioxide-arena.csproj, ioxide NuGet 0.7.211); nginx 1.31.4 configured with --with-cc-opt='-O3 -march=native -DNDEBUG' on debian:trixie (frameworks/nginx/Dockerfile); h2o built with clang, CMAKE_BUILD_TYPE=Release and -march=native. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | One io_uring ring per reactor thread, multishot accept and recv into provided buffer rings, inline continuations, no liburing (engine description in HttpArena meta.json); nginx in the same suite uses epoll. |
| **Adoption** | 56 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/MDA2AV/ioxide) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ioxide.json) |

## Verdict

HttpArena on an AMD Ryzen Threadripper PRO 3995WX (Ubuntu 24.04, kernel 6.17, loopback, 64 load-generator threads, best of repeated 5 s runs): ioxide 0.7.211 on .NET 11 preview.7 with a hand-written HTTP/1.1 handler served 4,111,381 req/s on baseline-4096 vs nginx 1.31.4 (C, custom module, -O3 -march=native) 3,284,513 (1.25x), h2o 3,641,609 (1.13x), mongoose 3,707,598 (1.11x) and agensio (C++) 3,558,559 (1.16x), but trailed libreactorng 4,377,377 and libioma 4,255,834; pipelined-4096 53.4M vs libreactorng 43.4M (1.23x); h2 is 3.7x nginx but 0.78x h2o (ratios derived from page data).

## Use it when

- Linux 6.1+ services in .NET where you would otherwise hand-write an epoll or io_uring server in C: the entry served 4.11M req/s on HttpArena baseline-4096, 1.25x nginx, 1.13x h2o and 1.16x agensio (C++), derived from page data.
- Keep-alive or pipelined HTTP/1.1 traffic where batching pays off: pipelined-4096 53.4M req/s against libreactorng (C, io_uring) 43.4M (1.23x) and nginx 4.04M.
- TLS-terminating JSON or static services that can use kTLS: json-tls-4096 1.80M req/s vs nginx 1.31M (1.37x) and agensio 1.72M (1.05x); static-tls-1024 1.12M vs nginx 0.72M (1.55x), though agensio is ahead at 1.19M.
- Thread-per-core designs that also need outbound I/O on the same core (Postgres via ioxide.pg, HTTP upstreams, timers), since every client rides the ring of the reactor that accepted the request.
- Existing ASP.NET Core apps that want an io_uring transport without rewriting endpoints, via ioxide.Kestrel's UseIoxide() (not measured in the HttpArena rows read here).

## Skip it when

- As a faster nginx for C-level throughput: C io_uring servers libreactorng (4.38M) and libioma (4.26M) beat it on baseline-4096, so the win over nginx is io_uring against epoll, not C#.
- HTTP/2 or HTTP/3 at the top end: baseline-h2-1024 12.2M req/s is 3.7x nginx but 0.78x h2o (15.6M) and 0.86x agensio (14.2M); baseline-h3-64 3.71M is 0.77x nginx and 0.43x agensio; agensio also leads static-h2-1024 (1.42M vs 0.95M).
- Connection-churn loads: limited-conn-4096 (reconnect every 10 requests) 2.54M req/s is below every C server in the table (nginx 2.63M, libioma 2.71M).
- Anything that must run on Windows, macOS, older kernels, under default seccomp profiles, or with a small RLIMIT_MEMLOCK: each reactor pins about 836 KB, so the default 12 reactors do not start under an 8 MB ulimit -l (README).
- Production use without your own HTTP layer: ioxide moves bytes; the benchmark's HTTP/1.1 parser is entry code with no request-size limits, and the README marks the runtime experimental.

## How it is fast

Each ring is created with IORING_SETUP_SINGLE_ISSUER | DEFER_TASKRUN (plus NO_SQARRAY on 6.6+), driven by raw io_uring_setup/io_uring_enter syscalls without liburing. Connections are accepted with multishot accept and read with multishot recv into a provided buffer ring, and completions resume IValueTaskSource continuations inline on the reactor thread, so a request never crosses threads or takes a lock. The benchmark entry batches every response parsed from one read into a single flush, which is why its 16-deep pipelined number (53.4M req/s) is 13x nginx's, and its plain-text responses carry no Date or Server header (about 63 bytes per response on baseline-4096 against nginx's 135 and libreactorng's 109, derived from page data). Static files are read off the ring straight into the write slab behind the header, and h1 TLS uses kernel kTLS transmit so handlers write plaintext.

## Compared with alternatives

Pick ioxide over the C# NativeAOT minima-sync HttpArena entry (4.39M req/s on baseline-4096, ahead of ioxide's 4.11M) when you want a reusable, MIT-licensed .NET runtime with async handlers, TLS/kTLS, h2/h3 and ring-native Postgres rather than a single benchmark server; pick it over Kestrel (1.32M on the same profile) when you can accept an experimental, Linux-only stack for about 3x the plain HTTP/1.1 throughput.

## Integration

| | |
|---|---|
| **Form** | module (NuGet packages: ioxide plus optional ioxide.http2, ioxide.http3, ioxide.nghttp2, ioxide.ngtcp2, ioxide.nghttp3, ioxide.pg, ioxide.file, ioxide.timer, ioxide.httpclient, ioxide.Kestrel) |
| **Dependencies** | .NET runtime only for the core; OpenSSL 3 and the Linux tls kernel module for TLS; the native HTTP/2, QUIC and HTTP/3 packages bundle nghttp2, ngtcp2 + picotls and nghttp3 (pure-C# ioxide.http2 and ioxide.http3 avoid native code) |
| **Minimum toolchain** | .NET 10 or .NET 11 (the library targets net10.0 and net11.0); the HttpArena build used SDK 11.0.100-preview.7 with runtime-async=on and Server GC |
| **Platforms** | Linux 6.1+ per README (issue #220 notes the pre-6.6 NO_SQARRAY fallback was unreachable until the fix in 0.15.251); x86-64 benchmarked; io_uring must be allowed by seccomp; kTLS needs modprobe tls |
| **Thread safety** | Shared-nothing by design: each reactor's ring, connections and pools are single-threaded, and a per-reactor SynchronizationContext brings timers, HttpClient and Task.Run continuations back to the owning reactor; touching a connection from another thread is unsupported (issue #249, TLS flush from another thread broke the session, closed 2026-10-07). |
| **Drop-in for the baseline** | no |

## Gotchas

- Verifier caveat corrected: the stored baseline-4096 row (4,111,381 req/s, 6443% CPU) is the final saved run of HttpArena PR #1372 (results commit 048221e, merged 2026-08-29), made after the Dockerfile pinned .NET 11 preview.7 and turned on runtime-async; the merge commit 5c2aa0b already pins preview.7 and holds that number. The 3,896,541 figure was preview.7 before runtime-async was enabled (saved in PR #1341), so the 1.25x lead over nginx stands for the pinned build rather than shrinking to 1.19x. The nginx rows date from 2026-08-15/20, so ioxide and its baselines are separate runs about two weeks apart on the same machine.
- Security bug in the benchmarked line: HttpArena pins ioxide 0.7.211, which predates the fix for issue #221 (severity high): a torn-down connection's write slab could be reused while its SEND was in flight, so one client received another client's response bytes (5,239 bytes in the repro). Fixed in 0.15.251 (2026-09-27), together with #220 (EINTR from a signal silently killed a reactor). The trigger needs a client that stops reading and half-closes, so the keep-alive throughput rows are probably unaffected, but use 0.15.251 or later (current 0.16.281).
- The HTTP/1.1 handler behind the numbers is benchmark-shaped: no Date or Server header (about half nginx's bytes per response), any unmatched path answers 200 with the a+b sum, no method check, and the carry buffer and Content-Length are unbounded, so a client can make it buffer without limit. It also turns on kTLS receive offload (IOXIDE_KTLS_RX=1), which the entry's README calls experimental (roughly one first connection in twelve fails the handoff). HttpArena ranks it as an engine entry, separately from nginx and h2o (infrastructure).
- Harness rule breach on static-h2 and static-h3: Multiplexed.cs reads every static file (and its .br/.gz siblings) into an in-memory dictionary at startup and never reloads it (StaticRefresh only refreshes the h1 caches), while HttpArena's engine rules allow in-memory static serving only through the engine's own file handling and only if it follows the disk. The static-h2-1024 lead over nginx (950,009 vs 796,607 req/s, 1.19x) and static-h3-64 (545,922 vs 361,025, 1.51x) therefore compare a frozen RAM cache against servers reading files; agensio (C++) still leads both.

## Known shortcomings

- Suite and repo share the owner MDA2AV and HttpArena states no CPU model; the C io_uring servers libreactorng and libioma beat it, so the win over nginx is io_uring against epoll rather than the language; h2o and agensio beat it on h2; the 4.11M figure is preview.6, pinned preview.7 gives 3.90M.
- Verifier caveat corrected: the stored 4,111,381 baseline-4096 comes from the final saved run of HttpArena PR #1372 (results commit 048221e, merge 5c2aa0b), already on the pinned .NET preview.7 with runtime-async=on; 3,896,541 was preview.7 before runtime-async, so the 1.25x over nginx stands. The benchmarked ioxide 0.7.211 carries issue #221 (severity high: a recycled write slab lets one client receive another client's response bytes), fixed only in 0.15.251 (2026-09-27); keep-alive rows are probably unaffected. The entry's h2/h3 static cache (Multiplexed.cs) is built in the entry and never refreshed, which breaks HttpArena's engine rule, so the static-h2 and static-h3 wins over nginx are suspect. The HTTP/1.1 handler sends no Date or Server header (about 63 vs 135 bytes per response against nginx) and uses unbounded buffers. Cross-run: nginx rows 2026-08-15/20, ioxide 2026-08-29.

## Caveats and trade-offs

The ioxide repo is owned by the same GitHub account as the HttpArena suite (MDA2AV), so tier is C rather than B even though every entry runs through one public harness. The ioxide Dockerfile notes that moving from .NET 11 preview.6 to preview.7 took baseline-4096 from 4.11M to 3.90M with no change to the entry; the saved 4,111,381 is the preview.6 figure, and at the 3.90M the currently pinned preview.7 gives, the lead shrinks to about 1.19x nginx, 1.07x h2o, 1.05x mongoose and 1.10x agensio (derived from page data). It is behind libreactorng (4,377,377) and libioma (4,255,834), both C io_uring servers, at baseline-4096, so the win over nginx comes from io_uring against nginx's epoll rather than from C#; behind nginx at limited-conn-4096 (2,543,314 vs 2,626,297); and on baseline-h2-1024 the 3.7x over nginx is against nginx's slow h2 path, while h2o (15,633,023) and agensio (C++, 14,210,433) both beat ioxide's 12,235,767, and agensio also leads static-h2-1024 (1,420,432 vs 950,009). The h2 path uses pure-C# ioxide.http2 with OpenSSL encrypting in userspace; h1 TLS uses OpenSSL handshake plus kernel kTLS; h3 rides the bundled C libraries ngtcp2 and nghttp3. The repo README gives no throughput numbers against C servers. Results JSON files are undated and the suite is rerun by its maintainers; entries are minimal hand-written handlers (nginx is a custom C handler module, ngx_http_httparena_module.c), and the baseline-4096 profile mixes GET and POST with query parsing, not static files. CPU model not stated, so not tier A. The .NET build uses Server GC and the runtime-async preview feature; README marks ioxide experimental. [retier] Correction: the stored 4,111,381 baseline-4096 is the final saved run of HttpArena PR #1372 (results commit 048221e), already on the pinned .NET preview.7 with runtime-async=on (3,896,541 was preview.7 before runtime-async), so the 1.25x over nginx stands. The benchmarked ioxide 0.7.211 carries issue #221 (severity high: a recycled write slab lets one client receive another client's response bytes), fixed only in 0.15.251 (2026-09-27); keep-alive rows are probably unaffected. The entry's h2/h3 static cache (Multiplexed.cs) is built in the entry and never refreshed, breaking HttpArena's engine rule, so the static-h2 and static-h3 wins are suspect. The HTTP/1.1 handler sends no Date or Server header (about 63 vs 135 bytes per response) and uses unbounded buffers; nginx rows 2026-08-15/20, ioxide 2026-08-29 (cross-run).

Linux-only (io_uring, seccomp must be unconfined), needs a preview .NET 11 runtime; HTTP/3 uses ngtcp2/nghttp3 and TLS uses OpenSSL (C libraries).

## Maintenance

Very active (469 commits, 56 stars, version 0.16.281, last commit 2026-10-10, 32 open issues including several severity-high slab and fd lifetime bugs fixed in September and October 2026) and MIT-licensed, but the README calls it experimental, the suite owner is also its author, and the published numbers are from 0.7.211, which carries the cross-connection response leak fixed in 0.15.251.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** HttpArena results JSON (site/data/results/ioxide.json and sibling nginx/h2o/mongoose/agensio/libreactorng/libioma files) carries every number in the record, with public entry code (frameworks/ioxide, frameworks/nginx with -O3 -march=native) and stated build settings, but the suite and ioxide share an owner (MDA2AV) and the README gives only '64-core dedicated hardware' with no CPU model, so first-party C, not A.
- **Verifier notes:** All record numbers match the HttpArena JSON files (baseline-4096 4,111,381 vs nginx 3,284,513, h2o 3,641,609, mongoose 3,707,598, agensio 3,558,559; pipelined 53,376,982 vs nginx 4,037,345 and libreactorng 43,424,448; h2 12,235,767 vs nginx 3,320,285). Tier C stays: same owner as the suite, no CPU model; C io_uring servers (libreactorng, libioma) beat it, and h2o and agensio beat it on h2, so the win is io_uring against epoll rather than the language. MIT, 56 stars, last commit 2026-10-10.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-19 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ioxide.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/ioxide>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/ioxide-arena.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/README.md>
  - <https://github.com/MDA2AV/ioxide>
  - <https://github.com/MDA2AV/ioxide/commits>
- **Sources the enricher read:**
  - <https://github.com/MDA2AV/ioxide>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/global.json>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/src/ioxide/ioxide.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/src/ioxide/io_uring/Ring.cs>
  - <https://raw.githubusercontent.com/MDA2AV/ioxide/HEAD/src/ioxide/ServerConfig.cs>
  - <https://github.com/MDA2AV/ioxide/tree/main/src/ioxide>
  - <https://github.com/MDA2AV/ioxide/tree/main/bench>
  - <https://github.com/MDA2AV/ioxide/issues?q=is%3Aissue>
  - <https://github.com/MDA2AV/ioxide/issues/221>
  - <https://github.com/MDA2AV/ioxide/issues/220>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/ioxide>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/ioxide-arena.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Handler.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/HttpSession.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Program.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Config.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/Multiplexed.cs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ioxide.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/ioxide.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/ioxide/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/ioxide/ioxide-arena.csproj>
  - <https://github.com/MDA2AV/HttpArena/commit/5c2aa0bb89b84f4e3e045b225b59401d173440c4>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5c2aa0bb89b84f4e3e045b225b59401d173440c4/frameworks/ioxide/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5c2aa0bb89b84f4e3e045b225b59401d173440c4/frameworks/ioxide/ioxide-arena.csproj>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5c2aa0bb89b84f4e3e045b225b59401d173440c4/site/data/results/ioxide.json>
  - <https://github.com/MDA2AV/HttpArena/pull/1372>
  - <https://github.com/MDA2AV/HttpArena/pull/1341>
  - <https://github.com/MDA2AV/HttpArena/pull/1396>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/add-framework/implementation-rules/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/add-framework/implementation-rules/engine.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ioxide/StaticRefresh.cs>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/add-framework>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/mda2av/ioxide`) · [data/wave14/enrich/raw/github_com_mda2av_ioxide.json](../../../data/wave14/enrich/raw/github_com_mda2av_ioxide.json) (enrichment confidence 0.6)

</details>
