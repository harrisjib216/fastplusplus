# cinatra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 coroutine HTTP/1.1 server and client library. On the project's own plaintext test it beats nginx by about 3%.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | cinatra 247841 req/s vs nginx 239629 req/s (\~3% faster); also beat drogon (216982 req/s) and brpc (147954 req/s) in the same run (verbatim numbers from repo doc) |
| **Workload** | wrk -t4 -c240 -d35s against GET /plaintext, identical response body/headers, comparing cinatra, drogon, brpc and a bare nginx config on the same host |
| **Metric** | throughput |
| **Hardware** | 4-core, 2.3GHz Ubuntu cloud VM (exact CPU model not stated) |
| **Compiler and flags** | gcc 11, -O3 |
| **Adoption** | 2.18k stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/qicosmos/cinatra) · [benchmark](https://github.com/qicosmos/cinatra/blob/master/lang/coroutine_based_http_lib.md) |

## Verdict

The project's doc reports wrk -t4 -c240 -d35s against GET /plaintext (13-byte body, same headers) on one 4-core 2.3 GHz Ubuntu cloud VM. CPU model not given; wrk ran on the same host over loopback. Builds used GCC 11 with -O3. Results: cinatra 247,841 req/s vs a tuned static-response nginx (return 200, reuseport, access_log off) at 239,629 req/s, about 3.4% more; Drogon 216,982; brpc 147,954 (on a different path). Separately, TechEmpower's Round 23 continuous run (Citrine, 2025-01-30, pipelined plaintext) had cinatra's best level at about 14.8M req/s (15.8M if a 15 s window is assumed), about 40th of 533 plaintext entries by my calculation from ph.json; TFB's nginx entry reached about 4.5M. At 16,384 connections cinatra logged 2,391 timeouts and 287 ms average latency.

## Use it when

- You write a C++20 service that needs an HTTP/1.1 endpoint and client inside the process, and you want coroutine handlers without adding a separately built framework (header-only, dependencies vendored).
- Small responses at high request rates over keep-alive connections, especially pipelined GETs. That is the shape of both the project's wrk run and TechEmpower plaintext.
- You want WebSocket, SSE, chunked, range and multipart handling, plus a basic RR/WRR/random proxy, from one library.
- Cross-platform C++ code: CI covers Linux (GCC 11.2, Clang 14), macOS (AppleClang 14) and Windows (MSVC 19.33).

## Skip it when

- You need HTTP/2 or HTTP/3. Only HTTP/1.x ships, and the HTTP/2 pull request (#748) was still open on 2026-09-26.
- You want to replace nginx as a TLS terminator, reverse proxy or static-file server. Only a fixed-string response was benchmarked. The proxy supports only RR, WRR and random balancing, and the static directory is read at startup (new files need a restart).
- You would switch from nginx for throughput alone. The measured gain is 3.4% from one self-run on a 4-core VM that also ran wrk, which is within typical run-to-run noise.
- Your toolchain lacks C++20 coroutines (older than GCC 10.2, Clang 13 or VS 2022), or your project already uses yalantinglibs or iguana. The bundled iguana submodule causes duplicate-definition errors with yalantinglibs (issue #706).
- Your handlers block, such as synchronous DB calls. A blocking handler holds up every connection on its IO thread unless you wrap the work in `coro_io::post`.

## How it is fast

The server runs one standalone-asio `io_context` per worker thread, with optional CPU pinning. One acceptor coroutine hands new sockets to those contexts in round-robin order. Each connection is a C++20 stackless coroutine, and a synchronous handler runs inline on that connection's IO thread, so the server never passes a request to another thread. Request heads are parsed by a vendored picohttpparser into `string_view`s held in a fixed array of 100 headers. The header scan has optional SIMD paths (SSE4.2 `PCMPESTRI`, AVX2, NEON) that you turn on at build time. Responses go out as one scatter-gather write or one string. The Date header comes from a per-thread string that is refreshed once per second. The responses to pipelined GET/HEAD requests are joined into a single `async_write`, and that helps a lot on pipelined plaintext tests.

## Compared with alternatives

Pick cinatra over Drogon when you want a header-only library with coroutine handlers and an HTTP client in the same package. On throughput the two are close: cinatra led by about 14% in the project's own doc run (247,841 vs 216,982 req/s), and in TechEmpower's Round 23 continuous plaintext run (2025-01-30) cinatra reached about 14.8M req/s against Drogon's 14.7M. If beating nginx is the main goal, Sogou Workflow and H2O are in the catalog with larger claimed margins over nginx than cinatra's 3%.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Standalone asio and async_simple, both vendored under include/. Optional: OpenSSL (CINATRA_ENABLE_SSL; the bundled CMake requires it on macOS), zlib (gzip), Brotli. The iguana git submodule is optional. |
| **Minimum toolchain** | C++20 with coroutines: GCC 10.2+, Clang 13+ or Visual Studio 2022 (per the README). GCC also needs -fcoroutines, and Release builds need -fno-tree-slp-vectorize. |
| **Platforms** | Linux, macOS, Windows. Scalar parser by default. Optional SSE4.2 or AVX2 on x86-64, or NEON on aarch64, chosen with ENABLE_SIMD (only one at a time). |
| **Thread safety** | Each connection and its handlers run on a single IO thread from the pool, so per-connection state needs no locks but shared application state does. sync_start, async_start and stop are commented 'only call once, not thread safe'. The server's connection table is protected by a mutex. |
| **Drop-in for the baseline** | false — cinatra is a library linked into your own binary. It does not read nginx configuration, speaks only HTTP/1.x, and its proxy supports only RR, WRR and random balancing. |

## Gotchas

- Pipelining works only for GET and HEAD. If a non-GET/HEAD request has more pipelined bytes behind it, the server replies 405 and discards the buffered remainder. Follow-on pipelined requests are matched only against exact routes, so `:param` and regex routes return 404 for them (coro_http_connection.hpp).
- A handler registered on an exact path that throws produces a 503 whose body is `e.what()`, unless you install `set_error_handler`, so internal error text reaches clients by default. Handlers on `:param` and regex routes are called outside that try/catch.
- GCC builds need -fcoroutines, plus -fno-tree-slp-vectorize in Release: build.cmake says SLP vectorization combined with coroutines causes a link error. The SSE4.2 parser path trips -Werror=array-bounds on GCC 13 (open issue #707).
- Hash-flooding hardening is recent: #751, merged 2026-09-20, keys request-field maps with SipHash-2-4. Issue #752 is still open: when the application calls get_session(), a client-chosen CSESSIONID cookie becomes a key in the shared, mutex-guarded session map. The fix is PR #753, which was unmerged on 2026-09-26.

## Known shortcomings

- The +3.4% over nginx is one first-party run on a 4-core VM with no CPU model, wrk on the same host, nginx returning a fixed string: within run-to-run noise. The README's 8.15M req/s plaintext chart and 'rust vs cinatra pipeline' chart have no source, date or method. The benchmark doc's code doesn't match itself (port 9001 vs 8090) or the in-repo example (Date header off, CPU pinning). Pipelining: non-GET/HEAD requests followed by pipelined bytes get 405 and the rest is dropped; follow-on pipelined requests only match exact routes (:param/regex return 404). Exact-path handlers that throw return 503 with e.what() as the body (leaks internals); :param/regex handlers run outside the try/catch. HTTP/1.x only (HTTP/2 PR #748 open). Client-chosen CSESSIONID keys the shared session map, a hash-flooding risk (#752, fix #753 unmerged). GCC needs -fcoroutines and -fno-tree-slp-vectorize in Release; SSE4.2 path fails -Werror=array-bounds on GCC 13 (#707); bundled iguana clashes with yalantinglibs (#706).

## Caveats and trade-offs

Margin over nginx is small (\~3%). No CPU model is given, only core count and clock. The numbers come from the project's own benchmark and are not reproduced independently. wrk ran on the same 4-core host over 127.0.0.1, so the load generator shared cores with the server. The brpc run used a different path (/HttpService/Echo). The sample response carries a Date of 21 Feb 2024, which suggests the numbers date from about Feb 2024 and an older cinatra version. The benchmark code and nginx config are in section 8 of the same doc, so the run can be reproduced in principle.

Header-only, requires C++20 coroutines (needs a recent GCC/Clang, via async_simple); nginx side of the comparison was a bare static-response config, not a full reverse-proxy workload

## Maintenance

Actively maintained: 1.0.0 released 2026-04-29, last commit 2026-09-20 (hash-flooding hardening), about 2.18k stars, 38 open issues. MIT-licensed and header-only with vendored dependencies, so it is easy to vendor, but it requires a C++20 coroutine toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party doc (lang/coroutine_based_http_lib.md, section 1 results and section 8 code) gives cinatra 247841, nginx 239629, drogon 216982 and brpc 147954 qps from wrk -t4 -c240 -d35s, with gcc11 -O3. The hardware is only '4-core 2.3GHz Ubuntu cloud VM' with no CPU model, so this is not A. First-party benchmark code with partial methodology is C, not B.
- **Verifier notes:** The numbers match the doc exactly, and nginx is a recognizable incumbent. The tier drops from B to C because this is a first-party benchmark with no CPU model. The last commit on the default branch is 2026-09-20; pushed_at is 2026-09-22.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Shortcomings recorded by:** TechEmpower Round 23 continuous run (Citrine, 2025-01-30, ph.json; rank derived): cinatra's best plaintext was \~14.8M req/s (15.8M on a 15 s window), roughly 40th of 533 entries and level with Drogon (14.7M); TechEmpower's nginx entry reached \~4.5M. At 16,384 connections cinatra had 2,391 timeouts and 287 ms average latency. The TechEmpower image is pinned to a Feb 2024 commit (c9bec308).
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/lang/coroutine_based_http_lib.md>
  - <https://github.com/qicosmos/cinatra>
- **Sources the enricher read:**
  - <https://github.com/qicosmos/cinatra>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/README.md>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/lang/coroutine_based_http_lib.md>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/lang/qps.png>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/lang/qps-comp.png>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/lang/qps-pipeline.png>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/cmake/build.cmake>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/cmake/develop.cmake>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/coro_http_server.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/coro_http_connection.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/coro_http_router.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/coro_http_response.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/http_parser.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/picohttpparser.h>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/io_service_pool.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/time_util.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/version.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/include/cinatra/secure_string_hash.hpp>
  - <https://raw.githubusercontent.com/qicosmos/cinatra/master/example/benchmark.cpp>
  - <https://github.com/qicosmos/cinatra/issues>
  - <https://github.com/qicosmos/cinatra/issues/752>
  - <https://github.com/qicosmos/cinatra/pull/753>
  - <https://github.com/qicosmos/cinatra/issues/750>
  - <https://github.com/qicosmos/cinatra/pull/751>
  - <https://github.com/qicosmos/cinatra/pull/748>
  - <https://github.com/qicosmos/cinatra/issues/735>
  - <https://github.com/qicosmos/cinatra/issues/707>
  - <https://github.com/qicosmos/cinatra/issues/706>
  - <https://github.com/qicosmos/cinatra/issues/702>
  - <https://github.com/qicosmos/cinatra/issues/618>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/master/frameworks/C%2B%2B/cinatra>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C++/cinatra/benchmark_config.json>
  - <https://www.techempower.com/benchmarks/results/round23/ph.json>
  - <https://hn.algolia.com/api/v1/search?query=cinatra&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/qicosmos/cinatra`) · [data/wave5/enrich/raw/github_com_qicosmos_cinatra.json](../../../data/wave5/enrich/raw/github_com_qicosmos_cinatra.json) (enrichment confidence 0.72)

</details>
