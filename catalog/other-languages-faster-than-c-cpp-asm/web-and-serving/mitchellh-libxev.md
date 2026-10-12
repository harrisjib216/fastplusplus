# libxev (HttpArena baseline server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig proactor event loop (io_uring, epoll, kqueue, WASI) with a C API; its HttpArena server ties libreactorng and beats h2o, nginx, Drogon.

| | |
|---|---|
| **Beats** | libreactorng (C, io_uring) and h2o (C) in the HttpArena suite; also nginx 1.31.4 (C) and Drogon (C++) |
| **Claimed result** | baseline-4096: 4,381,919 req/s vs libreactorng 4,377,377 (+0.1%, derived from page data, a tie), h2o 3,641,609 (1.20x, derived), nginx 3,284,513 (1.33x, derived) and Drogon 2,022,710 (2.17x, derived). On limited-conn-4096 (connections close after 10 requests) libxev's 2,672,662 is behind libreactorng's 2,685,717 (-0.5%, derived) and level with h2o (2,651,569) and nginx (2,626,297). latency-1m/10k/500k-8cpu are fixed-rate profiles scored on CPU per request, not throughput. |
| **Workload** | HttpArena baseline profile: mixed GET/POST /baseline11 requests with query parsing (sum of query integers plus the body), 4096 keep-alive connections, pipeline depth 1, 5 s runs. Server on 32 cores / 64 threads of a Threadripper PRO 3995WX, gcannon load over loopback. The HTTP/1.1 server is written in Zig on libxev's io_uring backend, with one forked worker per CPU, SO_REUSEPORT and TCP_NODELAY, and parses requests with picohttpparser (C). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, 8x DDR4-3200, one NUMA node), per HttpArena site/content/docs/hardware/_index.md. The server is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and the gcannon load generator to the other half. Traffic goes over loopback with MTU set to 1500, the governor is set to performance, and the sysctls are raised by scripts/lib/system.sh. |
| **Compiler and flags** | libxev entry: Zig 0.16.0, zig build -Doptimize=ReleaseFast -Dcpu=native; picohttpparser.c is compiled by zig's C frontend at -O3 (frameworks/libxev/build.zig). libreactorng: Ubuntu 24.04 gcc, library configured with CFLAGS=-O3 -march=native and the server built with gcc -O3 -march=native. nginx 1.31.4: --with-cc-opt=-O3 -march=native -DNDEBUG (Debian trixie gcc). h2o: clang with CMake Release and -march=native -mtune=native, no LTO. Drogon: CMake Release (CMake's default -O3 -DNDEBUG) in the drogonframework/drogon:latest image, without -march=native, with jemalloc LD_PRELOADed. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | io_uring backend with one forked worker per CPU and SO_REUSEPORT (engine description in HttpArena meta.json); the same io_uring design as the C competitor libreactorng. |
| **Adoption** | 3.6k stars |
| **Last commit** | 2026-05-06 |
| **Links** | [repository](https://github.com/mitchellh/libxev) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libxev.json) |

## Verdict

HttpArena (Threadripper PRO 3995WX, server on 32 cores/64 threads, gcannon over loopback, 4096 keep-alive connections, 5 s, best of N runs; libxev entry built with Zig 0.16.0 ReleaseFast -Dcpu=native, libreactorng with gcc -O3 -march=native): baseline-4096 4,381,919 req/s vs libreactorng 4,377,377 (a tie), h2o 3,641,609 (1.20x), nginx 3,284,513 (1.33x) and Drogon 2,022,710 (2.17x); limited-conn-4096 2,672,662 vs libreactorng 2,685,717 (-0.5%). At fixed offered rates libxev used 20.31 vs 21.04 us CPU per request at 1 M req/s, 21.49 vs 25.21 us at 10 k req/s and 15.45 vs 15.63 us at 500 k req/s on 8 CPUs against libreactorng (p99 1.12 ms vs 7.49 ms on the last), and Drogon used 32.13, 31.96 and 21.30 us (all ratios derived from page data; h2o and nginx are not enrolled in those profiles).

## Use it when

- Zig programs (or C programs willing to link a Zig-built library) that want one completion-based event loop across Linux io_uring, epoll fallback, macOS kqueue and WASI.
- Linux network servers with many keep-alive connections where an io_uring loop per core with SO_REUSEPORT is the intended architecture; in HttpArena that design matched the best C io_uring entry (libreactorng) and used slightly less CPU per request at fixed rates.
- Embedded or latency-sensitive code that needs predictable memory: completions are caller-owned and the loop does not allocate at runtime.
- Terminal or desktop apps already in the Zig ecosystem (Ghostty and zml use it) that need timers, process watching and file IO on one loop.

## Skip it when

- You want a measured speedup over a good C io_uring loop: against libreactorng the HttpArena numbers are a tie (+0.1% baseline, -0.5% limited-conn), and the libxev README itself declines to publish benchmarks.
- Windows production use: an IOCP backend exists (src/backend/iocp.zig) but the README still lists the Windows backend as planned, and issues #227 (completion reuse corrupts the IOCP loop) and #81 (thread panic) are open.
- You need an HTTP server, TLS, HTTP/2 or routing: libxev provides none of them; the HttpArena entry is a minimal handler using picohttpparser and answers every path with the /baseline11 sum.
- Toolchain stability matters: it requires Zig 0.16 exactly (stable releases only, no nightlies), does not integrate with Zig 0.16 std.Io, and the README warns integrating it will break the API.
- Heavy use of cancel or completion reuse across queues: open issues #233 (io_uring cancel matches reused user_data), #231 (epoll leaks the duplicated fd of cancelled TCP ops), #234 and #169.

## How it is fast

On Linux the default backend is io_uring: accept, read and write are submitted as ring operations and completed in batches, so a request costs no readiness syscall round-trip; completions are caller-allocated and the README promises zero runtime allocations inside the loop. Zig's lazy compilation tree-shakes unused watchers out of the binary. The HttpArena server adds the usual throughput recipe on top: one forked worker per CPU in the affinity mask, each with its own 4096-entry ring and SO_REUSEPORT listener, TCP_NODELAY, picohttpparser (C, -O3) for parsing, and a hand-written response with only Content-Type, Content-Length and Connection headers. The io_uring ring is created with flags 0: no SQPOLL, multishot accept/recv or provided/registered buffers (issue #58 open since 2023).

## Compared with alternatives

Pick libxev when you want a reusable, cross-platform event-loop library for Zig or C; the HttpArena siblings (Rust raw tokio 4,187,085 req/s, tokio-uring 3,565,878, zix 4,442,329, zeemo 4,422,489 on baseline-4096) are application servers or runtimes in other ecosystems, and tokio/tokio-uring are the Rust equivalents if you are not on Zig.

## Integration

| | |
|---|---|
| **Form** | module (Zig package via build.zig.zon) or static/shared C library built with zig build install |
| **Dependencies** | none at runtime beyond OS APIs; the C library links libc; building needs Zig 0.16 |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon; libxev tracks stable Zig releases only) |
| **Platforms** | Linux (io_uring, epoll), macOS (kqueue), WASI (poll_oneoff); Windows IOCP backend present but README lists Windows as planned |
| **Thread safety** | One Loop per thread; loop.stop() and submission must happen on the loop's own thread; cross-thread wakeups go through xev.Async and an optional shared thread pool |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note (HttpArena libxev entry): the response carries only Content-Type, Content-Length and Connection headers, about 86 bytes per response against libreactorng's about 109 (bandwidth divided by rps, derived from page data), the handler does no routing (every path gets the sum) while libreactorng dispatches /pipeline, /baseline11, /baseline2 and 404s, and libxev is enrolled only in baseline, limited-conn and the three latency profiles, not pipelined; all three tilt slightly toward libxev, so the +0.1% baseline edge is not a win.
- Harness note: HttpArena reports the best of N runs, and the top baseline-4096 entries cluster at 4.38-4.44 M req/s (libxev 4,381,919, libreactorng 4,377,377, zeemo 4,422,489, zix 4,442,329) at what scripts/lib/profiles.sh calls 'the \~4.4M baseline peak', with the server at about 6,145% of its 6,400% CPU; differences under 1-2% there do not rank implementations.
- The HttpArena server uses the single-shot TCP.write and discards the byte count, so a short write would silently truncate a response (libxev's queueWrite handles partial writes); its integer parser ignores '-' and clamps negative sums to 0, unlike libreactorng's signed parse. HttpArena's request templates (get.raw, post_cl.raw, post_chunked.raw) only carry positive values, so the measured numbers are unaffected.
- Loop.init caps ring entries at a u13 (8191; error.TooManyEntries above) and completions are caller-owned memory that must stay valid and unaliased until their callback runs; reusing a queued completion is the root of several open issues (#169, #227, #234).

## Known shortcomings

- Ties the C libreactorng (+0.1% baseline, -0.5% limited-connection) on HttpArena (Threadripper PRO 3995WX); parsing is done by picohttpparser (C); the wins over h2o, nginx and Drogon come from io_uring and a minimal handler, not Zig.
- No bug behind the numbers, but the harness tilts toward libxev: responses are about 86 bytes against libreactorng's about 109 (no Date or Server headers), there is no routing, and it is not enrolled in pipelined. Best-of-N runs, and the top entries cluster at the '\~4.4M baseline peak' per profiles.sh, so the +0.1% is noise. The server ignores the write byte count (a short write would truncate) and clamps negative sums to 0 (positive-only templates, so unaffected). Fixed-rate CPU per request slightly below libreactorng (20.31 vs 21.04 us at 1M; 21.49 vs 25.21 at 10k). Open io_uring/IOCP/epoll issues #233, #227, #231.

## Caveats and trade-offs

The libxev README says it will not post benchmark results and claims only that you 'shouldn't notice a slowdown' against other event loops, so the figure here is an HttpArena application, not a library claim. Request parsing is done by picohttpparser (C, compiled at -O3), so the Zig code is the event loop, the glue and the arithmetic. Against the best C entry (libreactorng, also io_uring and SO_REUSEPORT per CPU) the result is a tie on baseline (+0.1%), and libreactorng is 0.5% ahead on limited-conn. The margins over h2o, nginx and Drogon reflect io_uring against epoll engines and minimal handlers against full servers (nginx runs a custom C handler module), not Zig codegen. The libxev server does no routing (every path gets the sum response) while libreactorng dispatches on the path, a small saving for the Zig side. The results JSON files are undated and are rerun by the suite's maintainers; competitor rows come from sibling JSON files in the same directory. HttpArena is a smaller suite (about 128 GitHub stars) than TechEmpower. [retier] Responses are about 86 bytes against libreactorng's about 109 (no Date or Server headers), there is no routing, and the entry is not enrolled in pipelined; best-of-N runs with the top entries clustered at the '\~4.4M baseline peak' per profiles.sh, so the +0.1% is noise. The server ignores the write byte count (a short write would truncate) and clamps negative sums to 0 (templates are positive-only). Fixed-rate CPU per request slightly below libreactorng (20.31 vs 21.04 us at 1M). Open io_uring/IOCP/epoll issues #233, #227, #231.

libxev is an event loop (timers, sockets, files) rather than a web server; the measured server is a minimal handler in the HttpArena repo, not part of libxev.

## Maintenance

Actively maintained (3.6k stars, 591 commits, last commit 2026-05-06, used by Ghostty and zml) and MIT-licensed; stable on Linux and macOS per its README, with Windows and some cancel/reuse paths still carrying open bugs, and no benchmark claims from the project itself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. Every quoted number matches site/data/results/libxev.json and the sibling libreactorng/h2o/nginx/drogon.json files in MDA2AV/HttpArena. The benchmark code is public (frameworks/libxev/{Dockerfile,build.zig,src/main.zig}, frameworks/libreactorng/{Dockerfile,src/server.c}, frameworks/nginx/Dockerfile, scripts/benchmark.sh, scripts/lib/profiles.sh), compilers and flags are in the Dockerfiles, and site/content/docs/hardware/_index.md names the CPU (AMD Ryzen Threadripper PRO 3995WX). That matches the HttpArena tier-A precedent set for wtx and cutelyst.
- **Verifier notes:** Numbers verified. Tier raised B to A because HttpArena's hardware page names the CPU (Threadripper PRO 3995WX), the same basis as the wtx/cutelyst precedent. Shortcomings to record: tie with C libreactorng (+0.1% baseline, -0.5% limited-conn); parsing is picohttpparser C; the win over h2o/nginx/Drogon is io_uring and a minimal handler, not Zig; the libxev README itself makes no benchmark claim.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libxev.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/src/server.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs>
  - <https://github.com/mitchellh/libxev>
  - <https://github.com/mitchellh/libxev/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mitchellh/libxev/HEAD/README.md>
  - <https://github.com/mitchellh/libxev>
  - <https://github.com/mitchellh/libxev/tree/main/src/backend>
  - <https://raw.githubusercontent.com/mitchellh/libxev/HEAD/src/backend/io_uring.zig>
  - <https://raw.githubusercontent.com/mitchellh/libxev/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/mitchellh/libxev/HEAD/src/watcher/stream.zig>
  - <https://raw.githubusercontent.com/mitchellh/libxev/HEAD/build.zig.zon>
  - <https://github.com/mitchellh/libxev/issues?q=is%3Aissue%20bug%20OR%20performance%20OR%20crash%20OR%20leak>
  - <https://github.com/mitchellh/libxev/issues/110>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/build.zig.zon>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libxev/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/src/server.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libxev.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://github.com/MDA2AV/HttpArena/tree/main/requests>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/get.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/post_cl.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/post_chunked.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/valid-get1.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/valid-post1.raw>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/requests/noise-badcl.raw>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/mitchellh/libxev`) · [data/wave14/enrich/raw/github_com_mitchellh_libxev.json](../../../data/wave14/enrich/raw/github_com_mitchellh_libxev.json) (enrichment confidence 0.75)

</details>
