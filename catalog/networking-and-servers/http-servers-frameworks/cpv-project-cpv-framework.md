# CPV Framework

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> C++17 HTTP/1.1 web framework on Seastar's thread-per-core reactor; 5-14% more plaintext req/s than actix-web 2.0 at 100 connections.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | cpv-framework 0.2.0.0 vs actix-web 2.0.0 (wrk, best of 3): 84,691.95 vs 80,516.92 req/s (1 core, 100 conns, \~1.05x); 170,555.82 vs 149,625.67 (2 cores, 100 conns, \~1.14x); 76,556.09 vs 71,222.78 (1 core, 10000 conns, \~1.07x); 72,151.32 vs 58,860.81 (1 core, 20000 conns, \~1.23x); 123,234.96 vs 61,898.53 (2 cores, 20000 conns, \~1.99x, but actix-web returned 177,988 non-2xx responses in that run); at 2 cores/10000 conns cpv-framework was slower (136,694.89 vs 141,524.73, \~0.97x). All ratios derived from page data. |
| **Workload** | 'Hello World!' plaintext response on GET /, wrk (throughput) and wrk2 (fixed-rate latency), 60-180 s runs, best of 3; server pinned to 1 or 2 cores and client to cores 2,3 via taskset; 100, 10000 and 20000 connections; Intel Xeon E31225 @ 3.10GHz (4 cores). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E31225 @ 3.10GHz, 4 cores |
| **Compiler and flags** | cpv-framework: g++-9, CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG), C++17, -Wall -Wextra plus Seastar pkg-config CFLAGS; run with --smp=\$(nproc) --task-quota-ms=20 --reactor-backend=epoll. actix-web: cargo build --release (rustc version not stated). |
| **Adoption** | 122 stars |
| **Last commit** | 2020-01-21 |
| **Links** | [repository](https://github.com/cpv-project/cpv-framework) · [benchmark](https://github.com/cpv-project/cpv-framework/wiki/Benchmark-Results) |

## Verdict

The author's wiki run of 2020-01-21 was a single 4-core Xeon E31225 @ 3.10GHz host, with the server pinned to 1-2 cores and wrk/wrk2 pinned to cores 2-3 over loopback, best of 3. cpv-framework 0.2.0.0 (g++-9 Release, epoll backend) served a 'Hello World!' GET at 84.7k vs 80.5k req/s against actix-web 2.0.0 (cargo --release, rustc unstated) on 1 core/100 connections (\~1.05x) and 170.6k vs 149.6k on 2 cores (\~1.14x), lost at 2 cores/10k connections, and its 1.2-2x wins at 20k connections coincide with actix returning 158k-178k non-2xx responses; the fixed-rate wrk2 latencies were indistinguishable across all servers.

## Use it when

- You already run Seastar shard-per-core services on Linux and want routing, DI, static files and JSON on the same reactor, not a separate HTTP stack.
- Small plaintext or JSON responses over keep-alive or pipelined HTTP/1.1 on a few pinned cores, where per-core req/s matters (84.7k req/s on one 2011-era Xeon core in the author's test).
- You are willing to vendor it and port it yourself: 148 commented .cpp/.hpp files (\~690 KB including the vendored http-parser and sajson) on a pinned 2019 Seastar snapshot.
- As a reference design for zero-copy HTTP/1.1 parsing with ref-counted buffer slices and scatter-gather responses.

## Skip it when

- Anything that needs TLS, HTTP/2, an HTTP client or a reverse proxy: the 0.3 roadmap items (http client, ssl) never shipped, a reverse-proxy request (#15) was deferred to that release, and #17 (proxy, http2) is unanswered.
- Production services that need maintenance: no code commits since 2020-01-21, packages exist only for Ubuntu 18.04 with Seastar 20191017.1, and an open 2022 issue (#26) reporting a segfault inside libCPVFramework.so when running the hello-world example has no maintainer reply.
- Chasing maximum Seastar throughput: on the author's own page plain seastar-httpd beat cpv-framework in all six throughput configurations (e.g. 184.5k vs 170.6k req/s at 2 cores/100 connections).
- Comparing with a current actix-web: only actix-web 2.0.0 was measured, and cpv-framework already lost at 2 cores/10k connections (136.7k vs 141.5k req/s).
- macOS or Windows hosts, or code that can't be restructured into non-blocking future chains (C++20 coroutine support is only a backlog item).

## How it is fast

It inherits Seastar's shared-nothing, shard-per-core model: services are instantiated on every core with --smp and never shared, so the request path takes no locks and uses no atomics. Requests are parsed with a vendored Node.js http-parser 2.9.2, and the URL, headers, query values and body come out as cpv::SharedString, a reference-counted slice of the received seastar::temporary_buffer, so nothing is copied except in edge cases (headers split across packets, decoded query strings). Responses are built as cpv::Packet scatter lists of static and shared fragments and written with vectored I/O. Smaller tricks: a per-thread Date header cached per second, thread-local Reusable&lt;T&gt; free-list pools for per-request stream objects, and separate receive and reply loops per connection for pipelining, with a synchronous fast path when the flush future is already ready.

## Compared with alternatives

Pick it over Drogon, Crow or Oat++ only when your process is already a Seastar shard-per-core application and you'd rather maintain an abandoned framework than write routing on top of seastar-httpd. For a maintained C++ HTTP server with TLS, HTTP/2 or clients, Drogon, H2O or Sogou Workflow are the safer choices.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Seastar (via pkg-config 'seastar'; the author's PPA ships snapshot 20191017.1); vendored Node.js http-parser 2.9.2 and sajson; GoogleTest for tests only |
| **Minimum toolchain** | C++17, GCC 9 (g++-9), CMake 3.8+; library built with -O3 -flto and the gold linker |
| **Platforms** | Linux only (the README says to use a Docker Ubuntu 18.04 image on Windows/macOS); Debian package is amd64 for Ubuntu 18.04 (bionic) |
| **Thread safety** | Shared-nothing by design: each core runs its own copy of services, so handler code on a shard needs no locks, but nothing protects state you share across cores yourself; not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Keep-alive is dropped if a response has neither Content-Length nor chunked Transfer-Encoding, if Content-Length doesn't match the bytes written (logged as a warning), or if the handler didn't fully consume the request body.
- Default per-request limits: 512 KB and 512 packets for headers plus initial body (exceeding either returns 400 and closes), a 60 s timeout applied to every read and write, and a queue of 100 pipelined requests per connection; change them via HttpServerConfiguration.
- Reusable&lt;T&gt; keeps thread-local free lists (32768/sizeof(T) slots per type), and its header warns that keeping a Reusable&lt;&gt; alive after freeResources can segfault.
- The handler docs still show the pre-0.2 signature (const HttpServerRequestHandlerIterator&), but 0.2 changed it to pass by value. Every connection close is logged at Info, so raising the default Notice-level console logger to Info floods output under connection churn.

## Known shortcomings

- Plain seastar-httpd, which it is built on, beats it in every throughput configuration on the same page; at 20000 connections actix-web returned many non-2xx responses, so those gaps are not clean. Abandoned since 2020-01.
- Plain seastar-httpd (its own base) beat it in all 6 throughput configs on the author's page. The actix-web comparison is weak: actix-web 2.0.0 only, cpv loses at 2 cores/10k conns, the 1.2-2x wins coincide with actix returning 158k-178k non-2xx responses, wrk and server on the same 4-core host, debug logging enabled for actix. Fixed-rate latency tests are client-bound and show no edge. Last code commit 2020-01; PPA builds only for Ubuntu 18.04 amd64; hello-world segfault report (#26) unanswered; no TLS, HTTP/2 or client.

## Caveats and trade-offs

First-party wiki benchmark from January 2020 against actix-web 2.0.0 (several major versions old); the project has had no commits since 2020-01-21. cpv-framework loses to actix-web at 2 cores/10000 connections. It also loses to plain seastar-httpd (the framework it is built on) in every throughput configuration on the same page (e.g. 184,507 vs 170,556 req/s at 2 cores/100 conns). actix-web's 20000-connection results include many non-2xx responses, so the \~1.2-2x gaps there are not clean. rustc version and Seastar's exact CFLAGS are not stated.

Built on Seastar's shared-nothing/thread-per-core model, which requires restructuring app code around that model; wins over actix-web are marginal (\~5-14%) and inconsistent across configurations.

## Maintenance

Abandoned: the last code commit and 0.2 tag are from January 2020, and later pushes are only dependabot branches. It is MIT-licensed and small enough to vendor, but it is tied to GCC 9 and a 2019 Seastar snapshot, so expect to port it to current Seastar yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The wiki (dated 2020-01-21) has raw wrk output for actix-web 2.0.0 and cpv-framework 0.2.0.0 and states the CPU (Xeon E31225 @ 3.10GHz). The code is public: benchmarks/_runner.py, benchmarks/targets/cpv-framework/Main.cpp and benchmarks/targets/actix-web/src/main.rs (both 'Hello World!' on GET /). build.sh gives g++-9 with CMAKE_BUILD_TYPE=Release and cargo build --release, so code, compiler, flags and CPU are all stated.
- **Verifier notes:** Wiki numbers match the record apart from the 1-core/10000-connection ratio (1.07x, not 1.08x). Tier upgraded to A because the in-repo build scripts give the compiler and flags, and the wiki gives the CPU model. Metadata checked: MIT, 122 stars, not archived, not a fork, last commit 2020-01-21 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cpv-project/cpv-framework>
  - <https://github.com/cpv-project/cpv-framework/wiki/Benchmark-Results>
  - <https://raw.githubusercontent.com/wiki/cpv-project/cpv-framework/Benchmark-Results.md>
  - <https://github.com/cpv-project/cpv-framework/tree/master/benchmarks>
- **Sources the enricher read:**
  - <https://github.com/cpv-project/cpv-framework>
  - <https://github.com/cpv-project/cpv-framework/wiki/Benchmark-Results>
  - <https://raw.githubusercontent.com/wiki/cpv-project/cpv-framework/Benchmark-Results.md>
  - <https://github.com/cpv-project/cpv-framework/commits/master>
  - <https://github.com/cpv-project/cpv-framework/releases>
  - <https://github.com/cpv-project/cpv-framework/branches>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/README.md>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/_runner.py>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/cpv-framework/Main.cpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/cpv-framework/CMakeLists.txt>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/cpv-framework/build.sh>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/cpv-framework/run.sh>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/actix-web/src/main.rs>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/actix-web/Cargo.toml>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/actix-web/build.sh>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/actix-web/run.sh>
  - <https://github.com/cpv-project/cpv-framework/blob/master/benchmarks/targets/seastar-httpd/run.sh>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/CMakeLists.txt>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/HttpServer/Connections/Http11ServerConnection.cpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/HttpServer/Connections/Http11Parser.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/HttpServer/HttpServer.cpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/HttpServer/Handlers/HttpServerRequestRoutingHandler.cpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/src/Utility/DateUtils.cpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/HttpServer/HttpServerConfiguration.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/Utility/Reusable.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/Utility/Packet.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/Utility/SharedString.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/Application/Application.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/include/CPVFramework/Application/Modules/LoggingModule.hpp>
  - <https://github.com/cpv-project/cpv-framework/blob/master/docs/HttpServerRequestHandlers.md>
  - <https://github.com/cpv-project/cpv-framework/blob/master/docs/ReleaseNotes.md>
  - <https://github.com/cpv-project/cpv-framework/blob/master/docs/Roadmap.md>
  - <https://github.com/cpv-project/cpv-framework/blob/master/debian/control>
  - <https://github.com/cpv-project/cpv-framework/blob/master/.travis.yml>
  - <https://github.com/cpv-project/cpv-framework/blob/master/tests/travis_run_tests.sh>
  - <https://github.com/cpv-project/cpv-framework/issues>
  - <https://github.com/cpv-project/cpv-framework/issues/26>
  - <https://github.com/cpv-project/cpv-framework/issues/17>
  - <https://github.com/cpv-project/cpv-framework/issues/16>
  - <https://github.com/cpv-project/cpv-framework/issues/15>
  - <https://api.launchpad.net/1.0/~compiv/+archive/ubuntu/cpv-project?ws.op=getPublishedSources&status=Published>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cpv-project/cpv-framework`) · [data/wave5/enrich/raw/github_com_cpv_project_cpv_framework.json](../../../data/wave5/enrich/raw/github_com_cpv_project_cpv_framework.json) (enrichment confidence 0.6)

</details>
