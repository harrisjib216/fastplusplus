# Crow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++17 Flask-style HTTP/WebSocket framework on Asio; a 2014 first-party /json run beat Go net/http by \~1.5x.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | Crow: 136,297-296,733 req/s vs Go net/http (TechEmpower reference code): 92,893-180,517 req/s at concurrency 16-16384, i.e. \~1.46x-1.64x higher throughput at every level (e.g. 296,733 vs 180,517 at 4096, \~1.64x; lowest gap 233,349 vs 159,935 at 64, \~1.46x). Ratios derived from page data. |
| **Workload** | TechEmpower '/json' test (simple JSON response {"message":"Hello, World!"}), with the Go, Netty and Play code copied from TechEmpower/FrameworkBenchmarks; wrk load generator using 8 cores; concurrency 16, 64, 256, 1024, 4096 and 16384. |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c3.8xlarge; wrk used 8 cores for load generation (the README does not say whether the client ran on the same instance); CPU model not stated. |
| **Adoption** | 5.0k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/CrowCpp/Crow) · [benchmark](https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/edit?usp=sharing) |

## Verdict

Crow's original author ran a first-party test in October 2014 of the ipkn/crow code (submodule 3e5e91c, not today's CrowCpp/Crow) on TechEmpower's /json test, using an AWS c3.8xlarge with wrk on 8 cores. Crow did 136k-297k req/s against 93k-181k for TechEmpower's Go net/http code (GOMAXPROCS=NumCPU) at 16 to 16,384 connections, about 1.46x-1.64x, and was roughly level with Netty; the Go version, C++ compiler, flags and CPU model are not stated. A 2024 third-party run (Lemire, Crow 1.1.0, bombardier, 2x Xeon Gold 6338) measured 260k-380k req/s but included no Go baseline.

## Use it when

- Adding a REST/JSON or WebSocket endpoint to an existing C++ application when you want Flask-style routes and URL parameters that are type-checked at compile time.
- Short CPU-bound handlers on keep-alive HTTP/1.1, where per-request framework overhead dominates. That is the shape of the /json test where it beat TechEmpower's Go net/http code at every concurrency from 16 to 16,384.
- Builds that want a header-only dependency (a single amalgamated header is available) needing only Asio headers, with OpenSSL and zlib opt-in.
- Cross-platform services: CI builds GCC and Clang on Linux, Clang on macOS and MSVC on Windows; the docs list x86-64 and ARM64.
- Serving behind a reverse proxy on a Unix domain socket (app.local_socket_path()).

## Skip it when

- Handlers that block on I/O (database calls, upstream HTTP). There are no native async handlers yet (README 'still in development', issue #258 open since 2021), and a blocking handler holds one of the hardware_concurrency()-1 worker threads.
- You need HTTP/2 (issue #8, open since 2020), chunked responses (#1013 open) or streaming uploads. Request bodies are buffered whole into a std::string (#1064), and the parser path has no request-body size cap.
- Very high connection counts. Open issue #791 reports 'Worker Crash: ... Transport endpoint is not connected' at 10,000 simultaneous connections, and file-descriptor exhaustion under floods only got accept back-off in v1.3.4 (#1188).
- Internet-facing deployments that can't be kept current. v1.3.4 (2026-09-07) fixed five advisories, four rated high: a WebSocket global-middleware auth bypass, a WebSocket fragmented-payload limit bypass, JSON-depth stack overflow on Windows, and FileStore session path traversal.
- You need a current, independent throughput figure. Crow is not in the TechEmpower rounds or in the-benchmarker's C++ set, and the Go comparison is from 2014.

## How it is fast

It runs on (Boost.)Asio. One acceptor thread gives each new socket to whichever of the N-1 per-thread io_contexts has the fewest live connections, so each connection's parse, route, handle and write cycle stays on one thread. Requests are parsed from a fixed 4 KB per-connection buffer by an embedded copy of the Node.js http_parser, a callback state machine derived from nginx's parser. Routing uses a per-method trie that is path-compressed at startup, and URL parameter types are fixed at compile time (black_magic::get_parameter_tag), so arguments go straight through strtoll/strtoull/strtod. Responses go out as a single scatter/gather write of asio buffers that point at the cached status line, each header name and value, and the body, with no header string building.

## Compared with alternatives

Pick Crow over Drogon or Oat++ when you want a header-only framework whose only required dependency is Asio, with Flask-style routes that are type-checked at compile time. Prefer Drogon or Oat++ when you need a current third-party comparison against Go net/http: both have 2026 the-benchmarker results, while Crow's comparison is a 2014 first-party run.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Standalone Asio headers (docs: 1.28 to 1.30) or Boost.Asio (Boost &gt;= 1.64 with CROW_USE_BOOST); optional OpenSSL (CROW_ENABLE_SSL) and zlib (CROW_ENABLE_COMPRESSION); pthreads |
| **Minimum toolchain** | C++17 (CMake sets CMAKE_CXX_STANDARD 17 and the setup docs require it, although the README still says 'modern C++ (11/14)'). The docs name g++ 9.4 and clang 10 as the CI compilers; CMake 3.15+ is needed only for install, tests or examples. |
| **Platforms** | Linux x86-64 and ARM64 (docs), macOS (Clang, libc++/libstdc++) and Windows (MSVC) in CI; TCP or Unix domain sockets |
| **Thread safety** | Handlers run concurrently on concurrency()-1 worker threads (multithreaded() = std::thread::hardware_concurrency()), and each connection is pinned to one thread, so any state shared between handlers needs your own locking. Finishing a crow::response from another thread is not supported: users report double-free crashes (#843) and async support is still open (#258). mustache::set_loader has a reported data race (#1246). |
| **Drop-in for the baseline** | no |

## Gotchas

- The default log level is INFO, and at that level Crow logs a line for every request and every response. Call app.loglevel(crow::LogLevel::Warning) before measuring throughput.
- Responses are written with a synchronous asio::write on the connection's worker thread (http_connection.h). A slow-reading client can therefore stall the other connections on that thread, and bodies above stream_threshold (1 MiB by default) are sent with the timeout timer cancelled.
- In a 2024 report (#875, closed without a stated cause), a handler that added a header or returned crow::json fell to \~9.6k req/s at \~41 ms latency, versus \~335k req/s for a bare string. TCP_NODELAY is off unless you call app.tcp_nodelay(true) (available in v1.3.4), so benchmark your real handler both with and without it.
- Current master sends no Date header: the code that wrote the per-thread cached Date is commented out in http_response.h. Add the header yourself if your clients or caches need it, and keep in mind that responses are a little lighter than those from servers that send Date, such as Go net/http.

## Known shortcomings

- Evidence is the author's 2014 spreadsheet (TechEmpower /json, 1.46-1.64x over Go net/http) with no compiler, flags or CPU and no independent re-run; Crow is not in TechEmpower rounds. The logo and graphics are under a separate all-rights-reserved copyright.
- The only Go comparison is the original author's 2014 test of ipkn/crow, not current CrowCpp; Go version, compiler, flags and CPU not stated; no independent re-run against Go. Current master sends no Date header (commented out), so responses do less work than Go's. No async handlers (#258); finishing a response from another thread double-frees (#843); responses written synchronously on the worker thread. No HTTP/2, chunked or streaming; no request-body size limit found. Unexplained drop to \~9.6k req/s when adding a header or returning JSON (#875; TCP_NODELAY off by default). Worker crashes at 10,000 connections (#791). Five advisories (four high: WebSocket auth bypass, FileStore path traversal) fixed only in v1.3.4 (2026-09-07). README still says C++11/14; C++17 required.

## Caveats and trade-offs

First-party benchmark by Crow's original author (ipkn), dated 2014-10-02 in the sheet title; the benchmark repo's commits are all from 2014-09-27 to 2014-10-01. It tested the 2014 ipkn/crow code (submodule commit 3e5e91c), not current CrowCpp/Crow, and an old Go release. Results exist only in the Google Sheet and its charts. No compiler, flags or CPU model are stated. Crow is slightly behind Netty at concurrency 16384 (257,296 vs 262,335). Crow is not in the TechEmpower rounds, so there is no independent re-run. The LICENSE file is BSD-3-Clause for the code (the GitHub API reports NOASSERTION), but the Crow logo and graphics are under a separate all-rights-reserved copyright.

Header-only, largely synchronous-style API (native async listed as still in development in the current README); comparison used an older Go/TFB implementation that may not reflect modern Go net/http tuning.

## Maintenance

Actively maintained by the CrowCpp community fork: v1.3.4 shipped 2026-09-07, the last commit was 2026-09-23, and there are \~5.0k stars. The code is BSD-3-Clause (the logo and graphics are separately all-rights-reserved) and header-only, so it is easy to vendor, but pin v1.3.4 or later for the September 2026 security fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Google Sheet ('Crow benchmark result (2014. 10. 2)') has req/s for crow, netty, go, play2 and express at concurrency 16-16384. It was made by Crow's original author. The linked ipkn/crow-benchmark repo gives the code (go/src/hello/hello.go is the TechEmpower net/http code; crow is a submodule at 3e5e91c) and the instance type, but no compiler, flags or CPU model, so it stays first-party C.
- **Verifier notes:** Sheet numbers match the record's endpoints exactly. The '1.3x-1.7x' range was imprecise; the page data gives 1.46x-1.64x. Corrected workload ('/json', not plaintext) and date (2014, not \~2015-2018). Metadata checked: 4,983 stars, not archived, not a fork, last commit 2026-09-23 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/CrowCpp/Crow>
  - <https://github.com/CrowCpp/Crow/blob/master/LICENSE>
  - <https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/edit?usp=sharing>
  - <https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/export?format=csv>
  - <https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/export?format=csv&gid=604151204>
  - <https://github.com/ipkn/crow-benchmark>
  - <https://github.com/guteksan/REST-CPP-benchmark>
  - <https://www.techempower.com/benchmarks/results/round23/ph.json>
  - <https://www.techempower.com/benchmarks/results/round22/ph.json>
- **Sources the enricher read:**
  - <https://github.com/CrowCpp/Crow>
  - <https://github.com/CrowCpp/Crow/blob/master/README.md>
  - <https://github.com/CrowCpp/Crow/blob/master/LICENSE>
  - <https://github.com/CrowCpp/Crow/blob/master/CMakeLists.txt>
  - <https://github.com/CrowCpp/Crow/blob/master/cmake/compiler_options.cmake>
  - <https://github.com/CrowCpp/Crow/blob/master/vcpkg.json>
  - <https://github.com/CrowCpp/Crow/blob/master/.github/workflows/build_and_test.yml>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/http_server.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/http_connection.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/http_response.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/app.h>
  - <https://github.com/CrowCpp/Crow/blob/v1.3.4/include/crow/app.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/routing.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/parser.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/http_parser_merged.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/json.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/websocket.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/tcp_socket_options.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/ci_map.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/settings.h>
  - <https://github.com/CrowCpp/Crow/blob/master/include/crow/version.h>
  - <https://github.com/CrowCpp/Crow/blob/master/docs/getting_started/setup/linux.md>
  - <https://github.com/CrowCpp/Crow/blob/master/docs/guides/app.md>
  - <https://github.com/CrowCpp/Crow/releases>
  - <https://github.com/CrowCpp/Crow/releases/tag/v1.3.4>
  - <https://github.com/CrowCpp/Crow/security/advisories>
  - <https://github.com/CrowCpp/Crow/issues/258>
  - <https://github.com/CrowCpp/Crow/issues/843>
  - <https://github.com/CrowCpp/Crow/issues/875>
  - <https://github.com/CrowCpp/Crow/issues/1077>
  - <https://github.com/CrowCpp/Crow/issues/791>
  - <https://github.com/CrowCpp/Crow/issues/1188>
  - <https://github.com/CrowCpp/Crow/issues/1239>
  - <https://github.com/CrowCpp/Crow/issues/1013>
  - <https://github.com/CrowCpp/Crow/issues/1064>
  - <https://github.com/CrowCpp/Crow/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/ipkn/crow-benchmark>
  - <https://github.com/ipkn/crow-benchmark/blob/master/go/install.sh>
  - <https://github.com/ipkn/crow-benchmark/blob/master/go/src/hello/hello.go>
  - <https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/edit?usp=sharing>
  - <https://docs.google.com/spreadsheets/d/1KidO9XpuwCRZ2p_JRDJj2aep61H8Sh_KDOhApizv4LE/export?format=csv>
  - <https://github.com/guteksan/REST-CPP-benchmark>
  - <https://github.com/the-benchmarker/web-frameworks/tree/f673364>
  - <https://lemire.me/blog/2024/04/06/c-web-app-with-crow-early-scalability-results/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/crowcpp/crow`) · [data/wave5/enrich/raw/github_com_crowcpp_crow.json](../../../data/wave5/enrich/raw/github_com_crowcpp_crow.json) (enrichment confidence 0.55)

</details>
