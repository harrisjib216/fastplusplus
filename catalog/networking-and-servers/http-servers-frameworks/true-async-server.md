# TrueAsync Server (PHP extension with a C core, HttpArena true-async-server entry)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (PHP extension; HttpArena labels the entry PHP)` · `Apache-2.0` · 🟢 active

> C HTTP/1.1, HTTP/2 and HTTP/3 server inside PHP (TrueAsync fork) that out-runs HttpArena's nginx on small-response HTTP/2.

| | |
|---|---|
| **Beats** | nginx (C, custom handler module compiled -O3 -march=native, per HttpArena frameworks.json); Drogon (C++, CMake Release build), h2o (C), agensio and proxygen (C++) rows from the same suite |
| **Claimed result** | No claim by the project; ratios derived from HttpArena result JSON (derived from page data). baseline-h2c: 6,038,026 vs nginx 2,456,329 req/s at 256 connections (2.46x), 3,991,541 vs 2,490,271 at 1024 (1.60x), 3,753,829 vs 2,519,351 at 4096 (1.49x). baseline-h2 (TLS): 4,969,431 vs 3,414,750 at 256 (1.46x), 3,288,741 vs 3,320,285 at 1024 (0.99x). static-h2 at 256: 1,035,118 vs 802,090 (1.29x). baseline-4096 (HTTP/1.1): 2,260,254 vs Drogon 2,022,710 (1.12x) but below nginx 3,284,513 (0.69x). |
| **Workload** | HttpArena baseline-h2c, baseline-h2 (TLS) and static-h2 profiles (HTTP/2 over cleartext and TLS, 256 to 4096 connections) and the HTTP/1.1 baseline-4096 profile on one 64-core machine; the server is a PHP extension that runs HTTP/1.1, HTTP/2 and HTTP/3 on a libuv coroutine loop with a trivial PHP handler. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX 64-Cores (128 threads), 251 GiB RAM, Ubuntu 24.04.4, kernel 6.17.0-22 (HttpArena site/data/current.json) |
| **Compiler and flags** | Pre-built image trueasync/php-true-async:0.7.0-rc.6-php8.6 (PHP 8.6 TrueAsync fork) with opcache.jit=1255; the extension's own build flags are not visible in the benchmark Dockerfile; nginx -O3 -march=native; Drogon CMake Release with jemalloc preloaded |
| **Adoption** | 72 stars; listed in HttpArena as an emerging, tuned-mode entry |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/true-async/server) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/true-async-server.json) |

## Verdict

HttpArena (third-party suite, load generator on the same AMD Threadripper PRO 3995WX 64-core host, Ubuntu 24.04, 5 s runs) shows TrueAsync Server with a trivial PHP handler at 6.04M req/s vs the HttpArena nginx 1.31.4 custom C module (-O3 -march=native) at 2.46M on baseline-h2c with 256 connections (2.46x), 1.60x at 1024 and 1.49x at 4096, 1.46x on TLS h2 at 256 and parity at 1024, and 1.29x on static-h2; it is slower than nginx on every HTTP/1.1 and JSON profile. The TrueAsync rows predate nginx's run by at least four weeks, come from an older harness version and, judging by HTTP/1.1 response sizes, a server build older than 0.7.0, and carry smaller responses (no Date or Server headers).

## Use it when

- PHP services that want HTTP/2, HTTP/3, WebSocket, SSE and gRPC on one port from a single process, without php-fpm plus nginx in front.
- Many small HTTP/2 responses with multiplexed streams (HttpArena baseline-h2c at 256 connections: 6.04M req/s vs 2.46M for the HttpArena nginx module, on a 64-core Threadripper PRO 3995WX).
- Static-file serving over HTTP/2 with precompressed assets (static-h2 at 256 connections: 1.04M vs 0.80M req/s for nginx, same \~15 KB responses).
- Memory-constrained hosts: about 0.2-0.5 GiB RSS on the HttpArena baseline and h2 profiles versus about 3.5 GiB for that nginx build.
- Async PHP handlers that wait on databases or timers, since a waiting coroutine yields to the loop instead of holding a worker.

## Skip it when

- Plain HTTP/1.1 front-door or proxy duty: in the same suite it trails nginx on baseline-4096 (0.69x), pipelined (0.57x), limited-conn (0.68x), json-tls (0.60x) and json-h2c (about 0.71x).
- When you need the fastest C or C++ HTTP/2 server: h2o (16.1M req/s) and agensio (14.7M) are about 3x faster on baseline-h2 at 256 connections in the same HttpArena data.
- Stock PHP deployments: it requires the TrueAsync php-src fork (issue #6, run on stock PHP, is still open) plus OpenSSL 3.x, nghttp2 1.57+, and OpenSSL 3.5 / ngtcp2 / nghttp3 built from source for HTTP/3.
- Windows multi-core serving: SO_REUSEPORT is Linux/BSD only, so on Windows workers &gt; 1 give no parallelism (docs/USAGE.md caveats; closed issue #375).
- Production users who need a stable API: 1,392 commits, 0.x releases roughly weekly, and the CHANGELOG keeps removing or rewiring config methods (twelve no-op HttpServerConfig setters now throw, #393).

## How it is fast

One libuv event loop per worker thread (setWorkers(N) spawns an Async\ThreadPool), each binding the same port with SO_REUSEPORT, so a connection is accepted, parsed, dispatched and answered on one thread with no hand-off or locks. Each HTTP/1.1 request or HTTP/2/3 stream runs as a stack-switched PHP coroutine with a per-connection arena reset between requests; parsing and framing stay in C (llhttp, nghttp2), and static files go out via sendfile with precompressed .br/.gz sidecars and an open-file cache without entering PHP. The benchmark handler is a trivial PHP closure run under OPcache JIT (opcache.jit=1255).

## Compared with alternatives

Pick it over Qbix Server or a php-fpm stack when the application code is PHP and you want HTTP/2/3, gRPC and WebSocket in-process; for a C or C++ server where raw HTTP/2 throughput matters, H2O is about 3x faster in the same HttpArena data, and for HTTP/1.1 nginx-class serving Kore, Lwan or Sogou Workflow are the better-documented choices.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | TrueAsync PHP 8.6 fork with ext-async (libuv bundled), OpenSSL 3.0+ (3.5 for HTTP/3), libnghttp2 1.57+, optional libngtcp2 1.22+ and libnghttp3 1.15+, optional zlib-ng/zlib, brotli, zstd; llhttp 9.3.0 vendored |
| **Minimum toolchain** | PHP 8.6 TrueAsync fork; phpize/configure build with a C compiler on Linux/macOS, PHP-SDK with MSVC on Windows |
| **Platforms** | Linux (full; HTTP/3 GSO and SO_REUSEPORT load balancing), macOS and BSD, Windows (single accept thread, no WebSocket build, lower HTTP/3 throughput) |
| **Thread safety** | Each worker thread owns its own event loop and a deep-copied server object; handlers run as coroutines on that thread and share no mutable state unless you use the provided shared structures (rooms, cross-worker pub/sub, ThreadChannel). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (cross-run, stale build): the TrueAsync rps lines in HttpArena's true-async-server.json have not changed since commit #1034 of 2026-07-24 (git blame), while nginx's rows come from the 2026-08-20 run (#1212); TrueAsync's h2 rows also lack the p99_latency field every other framework's h2 rows carry, so they were produced by an older harness version. The current Dockerfile image tag (0.7.0-rc.6) therefore does not identify the build that was measured.
- Harness asymmetry (lighter responses): bytes per response derived from HttpArena's MiB/s bandwidth column are about 66 for TrueAsync vs 142 for nginx on HTTP/1.1, 21 vs 62 on h2c and 21 vs 86 on TLS h2 (nginx adds Server, Date, Connection and, on 8443, Alt-Svc). 66 bytes fits a response with no Date header, yet the server's own CHANGELOG added the RFC 9110 Date header to HTTP/1 in 0.7.0 (2026-06-01) and src/http1/http1_format.c now emits it on every response, so the HTTP/1.1 numbers were measured on code later changed for conformance.
- The HTTP/2 path still emits no Date header: only src/http1/http1_format.c calls the Date formatter; nothing in src/http2 generates one, although RFC 9110 section 6.6.1 requires an origin server with a clock to send it on every protocol.
- On kernels without load-balancing SO_REUSEPORT the shared-fd listener lets one worker take nearly every connection (open issue #329); HttpArena's frameworks/true-async-server/README.md is stale (names image 0.7.0-beta.5 and says baseline-h2c is not subscribed, while meta.json subscribes it and results exist).

## Known shortcomings

- Core is C (PHP extension), so this is not an other-language win and the entry is filed under wave 5 http-servers-frameworks by override; HttpArena: beats nginx only on the HTTP/2 baseline at low connection counts and on static-h2, slower on HTTP/1.1, pipelined and JSON profiles, about 3x behind h2o and agensio; extension build flags unpublished (prebuilt 0.7.0-rc.6 image).
- Cross-run: by git blame the HttpArena TrueAsync rps lines are unchanged since #1034 (2026-07-24) while the nginx rows come from the #1212 run (2026-08-20), and the TrueAsync h2 rows lack the p99_latency field every other framework's rows carry, so they come from an older harness version. Stale build: about 66 vs 142 bytes per HTTP/1.1 response means no Date or Server header, although the server added the RFC 9110 Date header to HTTP/1 in 0.7.0 (2026-06-01); the HTTP/2 path still sends no Date.

## Caveats and trade-offs

Beats nginx only on the HTTP/2 baseline profiles at low connection counts and on static-h2; it loses to nginx on baseline-4096 (0.69x), pipelined (0.57x), limited-conn (0.68x), json-h2c (about 0.71x) and json-tls (0.60x), and it trails the C++ agensio (14,744,015 req/s at baseline-h2-256) and C h2o (16,106,978) by roughly 3x on HTTP/2; against C++ proxygen it is 1.03x at baseline-h2c-256 but 0.70x at 1024 and 4096 (derived from page data). Response sizes differ on the baseline profiles: bytes per response derived from the bandwidth column are about 21 for TrueAsync versus about 62 (h2c) and 87 (h2) for nginx, so part of the gap is header bytes; static-h2 is like-for-like (about 15 KB per response for both, 15.88 vs 12.30 GB/s). The HttpArena nginx entry is a custom C handler module (nginx 1.31.4, quictls, worker_processes auto), not stock nginx. The TrueAsync image is a pre-built trueasync/php-true-async:0.7.0-rc.6-php8.6 (the entry's README still names 0.7.0-beta.5), so the extension's build flags are not visible and the tier stays at B. The core is C code (llhttp, nghttp2, libuv), so this is a C library with a PHP front end rather than a PHP-versus-C result; the repo itself publishes no benchmark numbers (only h2load log files). [retier] Cross-run: by git blame the TrueAsync rps lines are unchanged since #1034 (2026-07-24) while the nginx rows come from the #1212 run (2026-08-20), and the TrueAsync h2 rows lack the p99_latency field every other framework's rows carry. Stale build: about 66 vs 142 bytes per HTTP/1.1 response means no Date or Server header, although the server added the RFC 9110 Date header to HTTP/1 in 0.7.0 (2026-06-01); the HTTP/2 path still sends no Date.

Needs the TrueAsync fork of PHP 8.6, libnghttp2 1.57 or newer and OpenSSL 3.0 (3.5 for HTTP/3); handlers are PHP callbacks, static files are served from C.

## Maintenance

Very active single-maintainer project (last commit 2026-10-06, 0.16.0 released 2026-09-26, 72 stars), Apache-2.0 and usable today if you can run the TrueAsync PHP fork; expect API churn and evidence closer to C than B, since the HttpArena rows are cross-run and were measured on a build without the HTTP/1 Date header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent third-party suite (HttpArena, MDA2AV/HttpArena) with public harness and per-framework Dockerfiles, CPU model in site/data/current.json and nginx built with -O3 -march=native; every TrueAsync and competitor rps figure in the record matches the result JSONs. Not A because the TrueAsync extension comes from a pre-built Docker image whose compiler flags are not published.
- **Retiered** B to C: Enricher: the TrueAsync rows date from a 2026-07-24 run of a build that sends no Date header (added in 0.7.0) while the nginx rows come from 2026-08-20, so the comparison is cross-run and the measured build is stale; stale-build precedent: B to C.
- **Verifier notes:** All claimed figures re-derived from HttpArena result JSONs for true-async-server, nginx, drogon, h2o, agensio and proxygen; license Apache-2.0, 72 stars, last commit 2026-10-06 confirmed. Shortcomings: win limited to HTTP/2 baseline at low connection counts and static-h2, slower than nginx on HTTP/1.1, pipelined and JSON profiles, about 3x behind h2o and agensio on HTTP/2; extension build flags unpublished; not an other-language win since the server core is C.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/true-async-server.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://github.com/true-async/server>
  - <https://github.com/true-async/server/commits>
- **Sources the enricher read:**
  - <https://github.com/true-async/server>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/README.md>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/docs/USAGE.md>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/config.m4>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/h2load1.log>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/h2load2.log>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/h2load4.log>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http1/http1_format.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http2/http2_strategy.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http2/http2_session.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http2/http2_stream.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http2/http2_static_response.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http_response_framing.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http_response_server_api.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http_response.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/src/http_date.c>
  - <https://raw.githubusercontent.com/true-async/server/HEAD/include/http2/http2_session.h>
  - <https://github.com/true-async/server/tree/main/src>
  - <https://github.com/true-async/server/tree/main/src/http2>
  - <https://github.com/true-async/server/issues>
  - <https://github.com/true-async/server/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/true-async-server/entry.php>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/true-async-server.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/true-async-server.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/blame/main/site/data/results/true-async-server.json>
  - <https://github.com/MDA2AV/HttpArena/blame/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/true-async-server>
  - <https://github.com/MDA2AV/HttpArena/commits/main/scripts/benchmark.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/true-async/server`) · [data/wave14/enrich/raw/github_com_true_async_server.json](../../../data/wave14/enrich/raw/github_com_true_async_server.json) (enrichment confidence 0.6)

</details>
