# Kore

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `ISC` · 🟢 active

> Sandboxed C (or Python/Lua) web application server; outran an OpenResty nginx echo setup 1.5x in a 2015 unequal hello-world test.

| | |
|---|---|
| **Beats** | nginx (with the echo module) |
| **Claimed result** | Best of four 20 s wrk runs per framework: Kore 572,782 req/s (99% latency 3.99 ms) vs Nginx echo module 381,368 req/s (99% latency 24.24 ms), about 1.50x throughput (derived from page data); raw files show Kore 568,319-572,782 and nginx_echo 371,800-381,368 req/s across runs 02-04 and 01-04. Nginx ran 4 worker processes and Kore 12 workers, so the ratio is not like-for-like. Same table: libmicrohttpd 533,626, Undertow 616,547 (ahead of Kore), Go net/http 270,253, C++ Crow 256,552, Node HTTP 112,086 req/s. |
| **Workload** | Hello World text/plain response over HTTP/1.1 keep-alive on localhost, measuring framework overhead only: wrk with 12 threads (one per hardware thread), 100 connections, four 20 s runs per framework (time.sh), best run reported; Kore built with make NOTLS=1 and 12 workers, nginx (OpenResty build) with the echo module and 4 worker processes. |
| **Metric** | throughput |
| **Hardware** | Xeon E5-1650 v2 @ 3.50GHz (6 cores, 12 threads; results directory E5-1650v2-Ubuntu-14.04LTS), 32 GB RAM, Ubuntu 14.04 LTS, Linux 3.16; wrk ran on the same host over localhost |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/jorisvink/kore) · [benchmark](https://github.com/nanoant/WebFrameworkBenchmark) |

## Verdict

Third-party nanoant/WebFrameworkBenchmark (2015, Ubuntu 14.04, Xeon E5-1650 v2, wrk 12 threads and 100 keep-alive connections on the same host, best of four 20 s runs): Kore 2.0-devel built with make NOTLS=1 and 12 workers served 572,782 hello-world req/s vs 381,368 for OpenResty's nginx with the echo module and 4 workers, about 1.5x; Undertow (616,547) beat both. The worker counts, response headers and bodies differ, so the ratio is not like-for-like.

## Use it when

- A small, self-contained HTTP/1.1 or WebSocket API service written in C where you want TLS termination, privilege separation and seccomp/pledge sandboxing without a separate reverse proxy.
- Embedded or appliance-style deployments on Linux, OpenBSD, FreeBSD or macOS (x64, arm, aarch64) that want a single binary with handlers compiled in.
- Dynamic responses where per-request handler cost is low and you want one event loop per core; the 2015 test showed about 570k hello-world req/s on a 6-core Xeon E5-1650 v2.
- Projects that want to mix C handlers with Python or Lua handlers and async PostgreSQL in one process model.

## Skip it when

- Serving static files or reverse proxying at scale: nginx (or H2O) is the incumbent there, and the only Kore-vs-nginx number compared a 4-worker nginx echo module against 12 Kore workers.
- You need HTTP/2 or HTTP/3: the README lists HTTP/1.1 and WebSocket only.
- Windows or exotic architectures: only Linux, OpenBSD, FreeBSD and macOS on x64, arm and aarch64 are supported.
- Teams that need a large ecosystem or a GitHub-based contribution flow: development is essentially one maintainer, patches go to a mailing list, and Kore is absent from the current the-benchmarker/web-frameworks suite (2026-10-06 data), so there is no recent third-party performance data.

## How it is fast

One single-threaded, edge-triggered event loop (epoll on Linux, kqueue on BSD and macOS) per worker process, workers pinned to CPUs by default, and a shared-memory compare-and-swap accept lock that each worker takes for a batch of new connections (worker_accept_threshold) so accepts are spread without a thundering herd. Requests and buffers come from fixed-size freelist pools (kore_pool), responses are queued as netbufs, files go out with sendfile, and TCP_NODELAY is set on accepted sockets.

## Compared with alternatives

Pick Kore over H2O, Lwan, libevhtp or Drogon when you want a C application server with built-in TLS, ACME, privilege separation and seccomp/pledge sandboxing rather than raw peak throughput; Lwan and H2O have stronger and newer performance evidence (TechEmpower, HTTP/2), and H2O or nginx are the better choice for static files and proxying.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | OpenSSL 1.1.1/3 or LibreSSL 3.x (omit with TLS_BACKEND=none); optional libcurl 7.64+, pthreads (tasks), libpq (pgsql), Python 3.6+, Lua 5.4+ |
| **Minimum toolchain** | C99 compiler (Makefile uses -std=c99 -O2 -Werror); GNU make |
| **Platforms** | Linux, OpenBSD, FreeBSD, macOS; x64, arm and aarch64 only |
| **Thread safety** | Each worker is a single-threaded event-loop process; optional background tasks (TASKS=1) run on pthreads. No broader thread-safety guarantee is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw beyond the known worker-count gap (nginx worker_processes 4 vs Kore workers 12 on a 12-thread CPU shared with 12 wrk threads): the responses were not equivalent. The benchmark handler calls http_response(req, 200, "Hello World", 12), so Kore sends a 12-byte body including the C string's NUL terminator, no Content-Type, and its 2.0-devel default server, keep-alive and strict-transport-security headers; nginx sent 'Hello World!' as text/html with Date and Server stripped. wrk's byte counts work out to about 191 bytes per Kore response vs about 119 for nginx (derived from the raw result files). Kore did more bytes, so this does not inflate its lead, but neither matches the suite's text/plain spec.
- Compiler flags at the benchmarked Kore commit 4356c3e (2.0.0-devel) were -g with no -O flag in both the Makefile and the module build in cli.c, so unless the tester exported CFLAGS, Kore ran at GCC's default -O0; current Kore builds with -O2. Nginx's p50 latency (63-68 us) was actually lower than Kore's (122-127 us); only its p75 and higher (6.9-7.7 ms at p75, 22.5-28.7 ms at p99) were worse, consistent with 4 nginx workers being preempted by wrk threads.
- HSTS is on by default (HTTP_HSTS_ENABLE 31536000) even in plain-HTTP builds; set http_hsts_enable 0 behind a TLS-terminating proxy. Worker CPU affinity is also on by default (worker_set_affinity 1), which can collide with container CPU limits.
- Fixes land on master well after the last release (4.2.3): for example 'http: Make sure nb-&gt;s_off - len doesn't underflow' (2026-09-02) and a request-queue ordering fix (2026-10-03); several build flavors cannot be combined (README).

## Known shortcomings

- nanoant suite ran nginx with worker_processes 4 against Kore's 12 workers on a 12-thread E5-1650 v2, with wrk on the same host and flags unstated; weak-baseline downgrade (AssemblyScript precedent).
- Enricher: the bench handler http_response(req,200,"Hello World",12) sends a NUL byte with no Content-Type plus server, keep-alive and HSTS headers (about 191 vs 119 bytes per response, derived from raw files), and the Kore module build at commit 4356c3e used -g with no -O; nginx's p50 (63-68 us) beat Kore's (122-127 us), only nginx's tail was worse. Kore is absent from current the-benchmarker data. nb-&gt;s_off underflow fixed on master 2026-09-02.

## Caveats and trade-offs

Independent third-party suite (nanoant/WebFrameworkBenchmark, MIT, public wrk script and raw results) but a single 2015 setup with an unequal baseline: benchmarks/nginx/conf/echo.conf sets worker_processes 4 while benchmarks/kore/conf/kore.conf sets workers 12 on a 12-thread CPU, and wrk's 12 threads share the same machine, so nginx was given a third of Kore's worker count (its 24 ms p99 is consistent with saturation). Nginx is OpenResty's binary (run_echo.sh) serving through the third-party echo module with more_clear_headers instead of a static response. Kore built without TLS (make NOTLS=1) from a very early 2015 Kore submodule; compiler and flags unstated. Undertow (Java) beat Kore in the same table. Later independent data is less flattering: the-benchmarker/web-frameworks (README at commit 37f10ec, updated 2020-05-06, wrk with 8 threads; not re-checked by this verifier) lists Kore 3.3 at 85,687 req/s with 64 connections, behind Go fasthttp 159,448 and gin 95,867, and has no nginx row. Kore's own README and GitHub page contain no performance numbers; the listing's claim word is only 'scalable'.

C (or Python handlers) application platform: apps are built as shared modules or one binary; per-CPU worker processes, privilege separation, seccomp and pledge sandboxing, TLS on by default, HTTP/1.1 and WebSocket only (no HTTP/2 listed in the README).

## Maintenance

Actively maintained by its author (commits through 2026-10-03, ISC licence, 3.8k stars, release 4.2.3), with a security-first design, but performance evidence is a single 2015 third-party run against a deliberately small nginx configuration.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** Independent third-party suite with public scripts and raw wrk outputs, but the only baseline comparison is unequal: benchmarks/nginx/conf/echo.conf runs nginx with worker_processes 4 while benchmarks/kore/conf/kore.conf runs Kore with 12 workers on a 6-core/12-thread E5-1650 v2, with wrk on the same host; compiler and flags are unstated, so the 1.50x over nginx is not a like-for-like measurement and the record drops to C.
- **Verifier notes:** Table numbers and raw wrk files match; ISC, 3.8k stars, last commit 2026-10-03 confirmed. Downgraded B to C because the nginx baseline ran 4 worker processes against Kore's 12 workers on a 12-thread box (crippled-baseline config, AssemblyScript precedent), wrk shared the host, and flags are unstated; no other Kore-vs-nginx data found.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** nanoant suite (verifier downgrade B to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/nanoant/WebFrameworkBenchmark>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/nginx>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/kore>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/run_echo.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/conf/kore.conf>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/results/E5-1650v2-Ubuntu-14.04LTS>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_04.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_04.txt>
  - <https://github.com/jorisvink/kore>
  - <https://github.com/jorisvink/kore/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/jorisvink/kore>
  - <https://github.com/jorisvink/kore/commits/master>
  - <https://github.com/jorisvink/kore/issues>
  - <https://github.com/jorisvink/kore/issues?q=is%3Aissue+is%3Aclosed+crash+OR+leak+OR+overflow+OR+performance>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/README.md>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/Makefile>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/LICENSE>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/worker.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/linux.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/http.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/pool.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/net.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/connection.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/src/config.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/include/kore/kore.h>
  - <https://raw.githubusercontent.com/jorisvink/kore/master/include/kore/http.h>
  - <https://raw.githubusercontent.com/jorisvink/kore/4356c3e628a8de9438443ef2e7fd8b379a41ea92/Makefile>
  - <https://raw.githubusercontent.com/jorisvink/kore/4356c3e628a8de9438443ef2e7fd8b379a41ea92/src/http.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/4356c3e628a8de9438443ef2e7fd8b379a41ea92/src/cli.c>
  - <https://raw.githubusercontent.com/jorisvink/kore/4356c3e628a8de9438443ef2e7fd8b379a41ea92/includes/http.h>
  - <https://raw.githubusercontent.com/jorisvink/kore/4356c3e628a8de9438443ef2e7fd8b379a41ea92/includes/kore.h>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/time.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/common/threads.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/run_echo.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/nginx/conf/echo.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/run.sh>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/conf/kore.conf>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/benchmarks/kore/src/kore.c>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/kore>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/kore/src>
  - <https://github.com/nanoant/WebFrameworkBenchmark/tree/master/benchmarks/kore/lib>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/kore_04.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_01.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_02.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_03.txt>
  - <https://raw.githubusercontent.com/nanoant/WebFrameworkBenchmark/HEAD/results/E5-1650v2-Ubuntu-14.04LTS/nginx_echo_04.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/jorisvink/kore`) · [data/wave5/enrich/raw/github_com_jorisvink_kore.json](../../../data/wave5/enrich/raw/github_com_jorisvink_kore.json) (enrichment confidence 0.75)

</details>
