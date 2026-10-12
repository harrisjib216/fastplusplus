# dusty

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig HTTP/1.1 server and client framework on the zio coroutine runtime; ties nginx and beats Drogon in HttpArena.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C) and Drogon (C++) in the HttpArena suite; Hical (C++) and h2o (C) rows alongside |
| **Claimed result** | HttpArena, same harness but separate runs: baseline-4096 dusty 3,309,488 req/s vs nginx (C) 3,284,513 (+0.8%, derived from page data, a tie), Hical (C++) 3,228,043 (1.03x, derived), Drogon (C++) 2,022,710 (1.64x, derived); behind h2o (C) 3,641,609, mongoose (C) 3,707,598 and libreactorng (C) 4,377,377. json-tls-4096: 989,946 vs Drogon 253,055 (3.91x, derived) and Hical 549,765 (1.80x, derived), but behind nginx 1,313,755, h2o 1,229,462 and mongoose 1,102,964. json-comp-4096: 397,047 vs Drogon 127,466 (3.11x, derived) and Hical 261,955 (1.52x, derived). limited-conn-4096: 1,930,687, ahead of Drogon 1,694,883 but behind nginx 2,626,297, Hical 2,407,681 and h2o 2,651,569. pipelined-4096 (reference-only profile, excluded from the composite score): 4,379,900 vs nginx 4,037,345, but behind Drogon 7,801,404, Hical 4,851,267 and h2o 4,938,603. |
| **Workload** | HttpArena baseline profile (mixed GET/POST with query parsing, 4096 connections, 64-core machine) for the Dusty HTTP framework on the zio async runtime, 'standard configuration, no tuning'. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (64 cores, 128 threads), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json). The server container is pinned to cpuset 0-31,64-95 (32 cores plus SMT siblings) and the load generator runs on the remaining cores (scripts/lib/profiles.sh). |
| **Compiler and flags** | dusty: Zig 0.16.0, target x86_64-linux-musl, zig build --release=fast -Dcpu=x86_64_v3+aes+pclmul+adx (frameworks/dusty/Dockerfile). nginx 1.31.4 with the custom C handler module ngx_http_httparena_module.c, configured with --with-cc-opt='-O3 -march=native -DNDEBUG' on Debian trixie build-essential (frameworks/nginx/Dockerfile). Drogon: CMake Release build of main.cc on the unpinned drogonframework/drogon:latest image, run with LD_PRELOAD=libjemalloc.so.2 (frameworks/drogon/Dockerfile). Server containers run with --security-opt seccomp=unconfined and unlimited memlock (scripts/lib/framework.sh), so io_uring is available. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | zio async runtime using io_uring where available (engine description in HttpArena meta.json); no mechanism analysis from the authors. |
| **Adoption** | 145 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/lalinsky/dusty) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/dusty.json) |

## Verdict

In HttpArena's baseline profile (GET/POST summing query parameters and body, 4096 connections, gcannon load generator, AMD Ryzen Threadripper PRO 3995WX with the server pinned to 32 cores plus SMT siblings), dusty 0.4 built with Zig 0.16 --release=fast for x86_64_v3 musl served 3,309,488 req/s against nginx 1.31.4 with a custom C module at -O3 -march=native (3,284,513, a tie) and Drogon (2,022,710, 1.64x). It also beats Drogon 3.91x on json-tls-4096 and 3.11x on json-comp-4096 but trails nginx on limited-conn and json-tls and trails h2o, mongoose and libreactorng on baseline; rows come from separate runs on the same machine.

## Use it when

- A Zig service that wants one dependency covering router, gzip, SSE, static files, WebSocket, HTTPS with mTLS and an HTTP client.
- Many concurrent keep-alive connections whose handlers call other services (PostgreSQL, Redis, NATS): zio coroutines keep blocking-looking calls cheap.
- JSON APIs behind gzip or TLS where the alternative is Drogon with jsoncpp: 3.11x on HttpArena json-comp-4096 and 3.91x on json-tls-4096 (derived from page data).
- Small-response HTTP/1.1 throughput at nginx level from a framework rather than a hand-written C module: 3,309,488 vs 3,284,513 req/s on baseline-4096.

## Skip it when

- Peak HTTP/1.1 throughput: h2o (3,641,609), mongoose (3,707,598), libreactorng (4,377,377) and several catalogued siblings above 4.3M req/s beat it on the same baseline-4096 profile.
- Connection churn or TLS-heavy traffic: behind nginx on limited-conn-4096 (1,930,687 vs 2,626,297) and json-tls-4096 (989,946 vs 1,313,755); TLS is a pure-Zig tls.zig fork, not OpenSSL, and certificates cannot be reloaded without a restart (issue #132).
- Pipelined traffic: Drogon does 7,801,404 req/s vs dusty 4,379,900 on pipelined-4096; in-order pipelining only arrived in 0.4.0 (earlier versions closed the connection).
- HTTP/2 or HTTP/3: not implemented (issue #38 is a wishlist item; vendored nghttp2 sits behind use_http2, which defaults to off).
- Production on std.Io.Threaded: the README says that backend needs an OS thread per connection plus a watchdog thread per connection while timeouts are enabled; use zio. Also expect API churn: 0.3.0 and 0.4.0 both moved server configuration.

## How it is fast

Handlers run as stackful coroutines that zio schedules across work-stealing executor threads, with socket I/O through io_uring on Linux (epoll fallback), so blocking-style handler code does not cost an OS thread per connection. Release 0.4.0 added the main throughput work: response bodies are written into arena-backed segments and sent with vectored writes, request read buffers and arenas are pooled in a sharded pool and kept across keep-alive requests, and each listener runs several accept loops (log2 of the cgroup-visible CPUs, at least two). Request parsing is done by the vendored llhttp C parser from Node.js, gzip by vendored C zlib 1.3.2, and the response head is minimal (status line, handler headers, Content-Length; no Date or Server header).

## Compared with alternatives

Pick dusty over the raw HttpArena servers in this category (zix 4,442,329, zeemo 4,422,489, libxev 4,381,919, tokio-uring 3,565,878 req/s on baseline-4096) when you need a complete Zig web framework with an HTTP client, TLS, gzip and WebSocket rather than the fastest HTTP/1.1 loop; among general frameworks on the same profile it is ahead of actix-web (2,775,120) and ntex (2,168,712).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | libc (vendored llhttp C sources are compiled in); tls.zig fork (lazy, on by default, -Duse_tls=false removes it); zlib.zig with vendored zlib 1.3.2 (lazy, on by default, -Duse_zlib=false removes it); zio recommended for production and injected by the application; nghttp2 vendored but off by default |
| **Minimum toolchain** | Zig 0.16.0 (also builds with Zig 0.17) |
| **Platforms** | Linux (io_uring with epoll fallback through zio), macOS and BSDs (kqueue), Windows (iocp); CHANGELOG 0.4.0 says CI covers Linux, macOS and Windows on both Zig releases |
| **Thread safety** | Handlers run as coroutines on zio's multi-threaded work-stealing executors; each request has its own arena; WebSocket sends are serialized so concurrent tasks cannot interleave frames, and the client connection pool is safe to share across tasks (CHANGELOG 0.3.0). Other guarantees not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- No Date or Server header: Response.sendHeader writes only the status line, handler headers, Connection: close when needed and Content-Length or Transfer-Encoding. HttpArena's bandwidth/rps gives about 81 bytes per baseline response for dusty vs about 142 for nginx and 141 for Drogon (derived from page data), so the small-response profiles compare unequal response heads; RFC 9110 requires an origin server with a clock to send Date, so add it yourself if caches or clients need it.
- The JSON-profile wins over Drogon are mostly a serializer gap, not a language one: HttpArena's Drogon /json handler deep-copies a jsoncpp Json::Value per item on every request (its Dockerfile notes jsoncpp allocates a node per value and preloads jemalloc to soften it), while dusty encodes plain structs with the compile-time-specialized json.zig. The hot path is also partly C: HTTP parsing is the vendored llhttp parser and gzip is vendored zlib 1.3.2 at the default level with a window sized to the body.
- HttpArena rows are best-of-N 5-second runs taken on different dates: dusty at commit ae164fa ('Fix tls.zig compat', just after v0.4.0) saved 2026-10-07 in PR #1529 by the dusty author, nginx last saved 2026-08-30, so the +0.8% over nginx is a tie.
- Servers are bounded by default (30 s request timeout, 60 s keep-alive, max_connections); the HttpArena build raises max_connections to 65,536, so long-lived or high-fan-in deployments need the same tuning.

## Known shortcomings

- Ties nginx at baseline-4096 (+0.8%) and loses to h2o, mongoose, libreactorng and to nginx on limited-connection and json-tls; beats only Drogon (1.64x baseline, 3.91x json-tls) and Hical while Drogon is 1.78x faster pipelined; rows from separate HttpArena runs (dusty 2026-10-07, nginx 2026-08-30); the gain is io_uring against epoll, not Zig.
- dusty sends no Date or Server header (Response.sendHeader), about 81 bytes per baseline response against nginx's 142 and Drogon's 141 (derived from bandwidth over rps). The Drogon JSON wins (3.91x json-tls, 3.11x json-comp) are mostly a serializer gap: HttpArena's Drogon /json deep-copies a jsoncpp Json::Value per item while dusty uses compile-time json.zig. The hot path is partly C (vendored llhttp parser, zlib 1.3.2 gzip); the nginx tie is cross-run.

## Caveats and trade-offs

Not faster than the strongest C servers: a tie with nginx on baseline-4096 (+0.8%), behind nginx on limited-conn-4096 (1,930,687 vs 2,626,297) and json-tls-4096 (989,946 vs 1,313,755), and behind h2o (3,641,609), mongoose (3,707,598) and libreactorng (4,377,377) on baseline-4096. The clear wins are over the C++ frameworks Drogon (1.64x baseline, 3.91x json-tls, 3.11x json-comp) and Hical (1.03x baseline, 1.80x json-tls); on the pipelined profile Drogon (7,801,404) is 1.78x faster than dusty (derived from page data). Rows come from separate runs on the same machine: dusty.json was saved on 2026-10-07 (PR #1529, dusty 0.4), nginx.json last changed on 2026-08-30 and drogon.json on 2026-09-06, so the nginx tie is within run-to-run noise. The dusty entry is maintained by the dusty author (meta.json maintainers: lalinsky); handlers on all sides are minimal benchmark handlers (nginx is a custom C module; Drogon is built on an unpinned image). The baseline profile mixes GET and POST with query parsing, not static files. The dusty README itself makes no comparison with C or C++ servers. [retier] dusty sends no Date or Server header, about 81 bytes per baseline response against nginx's 142 and Drogon's 141. The Drogon JSON wins (3.91x json-tls, 3.11x json-comp) are mostly a serializer gap (HttpArena's Drogon /json deep-copies a jsoncpp Json::Value per item; dusty uses compile-time json.zig). The hot path is partly C (vendored llhttp, zlib 1.3.2 gzip); the nginx tie is cross-run.

Full HTTP framework (router with params and wildcards, JSON, gzip, WebSocket) on Zig 0.16; young project; the Dusty README gives no performance numbers.

## Maintenance

Active (last commit 2026-10-11, v0.4.0 released 2026-10-06, 148 stars, 10 open issues, none labelled bug) and MIT-licensed, so copyable, but a young pre-1.0 library tied to Zig 0.16/0.17 whose server API changed in 0.3.0 and again in 0.4.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: every dusty number matches site/data/results/dusty.json and the nginx, drogon, hical, h2o, mongoose and libreactorng rows match their sibling JSON files; the benchmark code is public in MDA2AV/HttpArena (frameworks/dusty/Dockerfile, frameworks/nginx/Dockerfile, frameworks/drogon/Dockerfile, scripts/benchmark.sh, scripts/lib/profiles.sh, scripts/lib/framework.sh), compilers and flags for both sides are in the Dockerfiles, and the CPU model (AMD Ryzen Threadripper PRO 3995WX) is in site/data/current.json, the same basis on which wtx and cutelyst on this harness were tiered A in wave 5.
- **Verifier notes:** Numbers and metadata (MIT, 145 stars, last commit 2026-10-11, not a fork, not archived) confirmed; tier raised to A on the HttpArena precedent. Record as shortcomings: ties nginx and loses to h2o, mongoose, libreactorng on baseline and to nginx on limited-conn and json-tls; wins only over Drogon and Hical; Drogon beats it 1.78x on pipelined; cross-run rows (dusty 2026-10-07 vs nginx 2026-08-30); win comes from io_uring vs epoll, not the language.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-17 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/dusty.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/dusty.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/drogon.json>
  - <https://github.com/lalinsky/dusty>
  - <https://github.com/lalinsky/dusty/commits>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/lalinsky/dusty>
  - <https://github.com/lalinsky/dusty/tree/main/src>
  - <https://github.com/lalinsky/dusty/issues>
  - <https://github.com/lalinsky/dusty/commits>
  - <https://github.com/lalinsky/dusty/commit/ae164fac083fa09b9d38a1c0e0390334fca73268>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/README.md>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/build.zig>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/src/response.zig>
  - <https://raw.githubusercontent.com/lalinsky/dusty/HEAD/src/server.zig>
  - <https://raw.githubusercontent.com/lalinsky/zlib.zig/HEAD/README.md>
  - <https://raw.githubusercontent.com/lalinsky/zlib.zig/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/lalinsky/zio/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/build.zig.zon>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/dusty/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/dusty.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/main.cc>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/dusty>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/lalinsky/dusty`) · [data/wave14/enrich/raw/github_com_lalinsky_dusty.json](../../../data/wave14/enrich/raw/github_com_lalinsky_dusty.json) (enrichment confidence 0.8)

</details>
