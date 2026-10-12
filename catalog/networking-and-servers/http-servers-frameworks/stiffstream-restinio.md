# RESTinio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++17 embedded async HTTP/WebSocket server on ASIO; served a 10-client POST echo test 1.3-2.1x faster than Restbed.

| | |
|---|---|
| **Beats** | Restbed v4.6 (also compared against C++ REST SDK v2.10.15, Crow v0.1, cpp-httplib v0.5.8, Pistache v0.0.002 in the same table) |
| **Claimed result** | Read from images/rest_all.PNG. Local, N=1000, t=0 ms: C=28 Restinio v0.6.2 1.025 s vs Restbed v4.6 1.333 s (1.30x faster, derived from page data) and C++ REST SDK 3.401 s (3.32x, derived from page data); C=4 Restinio 0.85 s vs Restbed 1.789 s (2.10x, derived from page data), C++ REST SDK deadlocked. The README: Restinio 'was over 3 times faster than the worst Cpp-REST-SDK'. Restinio is best in both Local sprint cells, but its margin over Pistache is small (1.059 s and 0.964 s, 1.03x and 1.13x, derived from page data); over Crow it is 1.50x and 1.68x (1.536 s, 1.43 s). Over VPN at t=0 Restinio 1:51.788 vs Restbed 1:55.122 (C=28) and 1:48.743 vs 1:48.880 (C=4). With 200 ms handling time all frameworks that complete are within about 3 percent of each other, except Httplib over VPN and Pistache over VPN at C=4 (C++ REST SDK deadlocks at C=4). |
| **Workload** | Independent shootout (guteksan/REST-CPP-benchmark, 2020): six equivalent services (POST /test echoes the body prefixed with 'Sending response: ', log4cplus logs each request and reply, optional sleep t) driven by 10 Python producer processes (postInLoop.py, http.client, a new TCP connection per request, printing under a shared lock), each sending N=200 or 1000 requests; service thread pool C=28 or C=4; Local (same machine) or VPN; metric is time from the service's first logged request to its last reply, one run per cell. |
| **Metric** | throughput |
| **Hardware** | 28x Intel Xeon CPU E5-2660 v4 @ 2.0 GHz, 64 GB RAM, Ubuntu 16.04.3 LTS |
| **Compiler and flags** | Not stated; services built with cmake -DCMAKE_BUILD_TYPE=Release |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/Stiffstream/restinio) · [benchmark](https://github.com/guteksan/REST-CPP-benchmark) |

## Verdict

In guteksan/REST-CPP-benchmark (independent, 2020, one run per cell, results only as a screenshot), ten Python processes each sent 1,000 POSTs to /test over a new TCP connection per request on the same 28-thread Xeon E5-2660 v4 (Ubuntu 16.04, Release builds, compiler not stated). RESTinio 0.6.2 finished in 1.025 s at C=28 and 0.85 s at C=4 against Restbed 4.6's 1.333 s and 1.789 s (1.30x and 2.10x, derived from page data), with Pistache close behind (1.03x and 1.13x). That is about 1 ms per closed-loop request per client (derived from page data), so the Python client sets most of the floor. The timer runs from the service's first logged request to its last 'Processing finished' line, which RESTinio writes before resp.done() and Restbed after the asynchronous yield(), so neither includes the socket write; with a 200 ms handler or over a VPN the frameworks tie.

## Use it when

- Embedding a REST endpoint into an existing ASIO-based C++ service, sharing its io_context, where handlers often complete asynchronously (database or message-bus calls).
- Moderate-concurrency internal APIs with small requests and responses, where the measured margin over Restbed (1.3x at 28 threads, 2.1x at 4 threads in the 10-client local sprint) and over Crow v0.1 (1.5-1.7x) matters.
- Projects that want a BSD-3-Clause server rather than Restbed's AGPL/commercial licence, and need TLS, compression, sendfile and WebSocket upgrade in one library.
- Code bases on C++17 or later with GCC 13, Clang 18, MSVC or macOS toolchains (the CI matrix).

## Skip it when

- Maximum raw throughput: the only measurement is a 2020 shootout of six C++ frameworks driven by a Python client; Drogon, cinatra or Boost.Beast-based servers have stronger published numbers on standard harnesses.
- HTTP/2 or HTTP/3 (open issue #211), streaming uploads of large request bodies (the whole body is buffered before the handler runs; issue #177 says partial reception is unsupported), or other new features: development beyond maintenance has been on hold since March 2021 (issue #148).
- Handlers that take real time: with 200 ms of handling time every framework that completed was within about 3 percent, so the advantage is in request overhead only.
- Teams wanting a dependency-free single header: RESTinio needs ASIO, llhttp (compiled), fmt and expected-lite, plus zlib, OpenSSL or a regex engine for the optional features; the benchmark author rated it hardest to integrate (restinio issue #86 on Ubuntu Xenial).

## How it is fast

The server is a thin layer over ASIO's proactor: connections are accepted and read asynchronously on a single thread or a pool, each connection's operations are serialised by an asio strand (a no-op strand in single-thread mode), and the request is parsed by nodejs/llhttp (nodejs/http-parser 2.9.2 in the benchmarked 0.6.2). The handler gets the fully parsed request, and the response is queued and written asynchronously, with HTTP pipelining supported. The benchmark gives no profile, so which of these explains the margin over Restbed is not documented.

## Compared with alternatives

Against cpp-httplib (same shootout, where RESTinio's 1.025 s beat httplib's roughly 3 s at C=28) and Crow (1.5-1.7x slower here, v0.1), pick RESTinio when you need asynchronous handlers, an externally owned io_context, pipelining and WebSocket in a BSD library. Pick Drogon or cinatra instead when peak req/s on wrk-style harnesses is the goal; both have stronger published numbers than RESTinio's single obscure shootout.

## Integration

| | |
|---|---|
| **Form** | header-only library plus the compiled nodejs/llhttp parser; CMake package, also vcpkg (Conan was used for the benchmarked 0.6.2) |
| **Dependencies** | standalone ASIO 1.36 or Boost.ASIO, nodejs/llhttp 9.3.0, fmt 12.0.0, expected-lite 0.8.0; optional zlib (compression), OpenSSL (TLS), PCRE/PCRE2/Boost.Regex router engines, SObjectizer timer integration |
| **Minimum toolchain** | C++17, CMake 3.14 (CI: GCC 13, Clang 18, MSVC latest, macOS 15; C++17/20/23). The benchmarked 0.6.2 was C++14. |
| **Platforms** | Linux, Windows and macOS per CI; anything ASIO supports in principle (32-bit narrowing errors in open issue #124, QNX untested) |
| **Thread safety** | On a thread pool the same request handler object is called concurrently from pool threads, so it must be thread-safe; per-connection I/O is serialised by an asio strand (default_strand_t, or noop_strand_t for single-thread traits). A request_handle_t may be completed from another thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- incoming_http_msg_limits_t defaults to unlimited URL, header and body sizes, and bodies are fully buffered in memory; set max_body_size and the other limits on any public-facing server.
- express_router_t&lt;&gt; uses std::regex by default; for many routes switch to the PCRE, PCRE2 or Boost.Regex engine or to the easy_parser_router (since 0.6.6).
- The independent numbers are for RESTinio 0.6.2, which used nodejs/http-parser 2.9.2, ASIO 1.14.0 and C++14; current 0.7.x uses llhttp and C++17 and has not been re-measured.
- Issue #246, a heap-use-after-free at shutdown with separate_accept_and_create_connect(true) and the connection-count limiter, was fixed only in 0.7.10 (September 2026); use 0.7.10 or later if you enable those options.

## Known shortcomings

- Tier B on guteksan/REST-CPP-benchmark (rest_all.PNG: 1.025 s vs Restbed 1.333 s, 0.85 vs 1.789 s, cpprestsdk 3.401 s; margin over Crow 1.50x/1.68x): no compiler stated, the Python client opens a new connection per request, single 2020 run, ties the field at t=200 ms.
- Enricher: the benchmarked 0.6.2 used nodejs/http-parser 2.9.2, ASIO 1.14 and C++14; current 0.7.x uses llhttp and C++17 and was not re-measured. The clock stops at a log line before the socket write on both sides (symmetric, minor); Python client with a new connection per request gives about a 1 ms per-request floor. Default incoming_http_msg_limits unlimited and whole body buffered (#177); Express router defaults to std::regex; feature work on hold since 2021 (#148); shutdown heap-use-after-free #246 fixed in 0.7.10. Jami ab numbers (snippet only): thread-pool RESTinio 12,719 vs Restbed 12,677 req/s, a tie; 18,834 only single-threaded.

## Caveats and trade-offs

Independent but obscure (130 stars, 17 commits, 2020) single-run shootout; results exist only as a screenshot (images/rest_all.PNG), times in min:sec.ms with no error bars. The compiler is not stated; services use cmake -DCMAKE_BUILD_TYPE=Release, Restinio v0.6.2 comes from Conan, Restbed v4.6 is a system install with unstated build flags. The client is a Python script that opens a new TCP connection for every request and prints each request and response under a lock, so the client sets a floor and the sprint cells (about 1 s for 10,000 requests) mostly measure connection accept and request handling overhead. Versions are 2020-era (Restinio is now 0.7.10) on a 2016 Xeon E5-2660 v4 under Ubuntu 16.04. The win shows only in the no-delay Local cells; with 200 ms handling time Restinio ties the field (for example 3:21.367 vs Restbed 3:27.542 at C=28, 1:40.859 vs Restbed 1:40.530 over VPN at C=4), and over a VPN the t=0 cells are dominated by network overhead. Restbed is AGPL/commercial; the margin over Pistache is only 3 percent at C=28 and 13 percent at C=4. Restinio's own README makes no measured speed claim and does not cite this benchmark. Neither Restbed nor C++ REST SDK is in the category baseline list (nginx, Go net/http, Boost.Beast, actix-web, uvloop). A Jami issue (git.jami.net, blocked) reportedly measured Restinio at 18,834 req/s vs Restbed 12,677 req/s with ab (10,000 requests, concurrency 20); search snippet only, not opened.

Header-only C++17 on standalone ASIO or Boost.ASIO, but depends on the non-header-only nodejs/llhttp. Asynchronous request handling with HTTP pipelining, ExpressJS-style router, TLS, compression, sendfile and basic WebSocket. The independent benchmark author scored it lowest for ease of including (dependency problems on Ubuntu Xenial via apt, restinio issue #86) and middling for ease of use.

## Maintenance

Maintenance-mode but alive: releases continue (0.7.10 on 2026-09-03, last commit 2026-09-03, 1.3k stars, BSD-3-Clause), while feature development has been on hold since 2021 for lack of funding; safe to adopt for HTTP/1.1 if you pin a recent release and set message limits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (guteksan/REST-CPP-benchmark; author not on the Restinio team, linked from the Pistache README) whose results image images/rest_all.PNG shows every quoted figure; code for all six equivalent services and the client (basic-\*/main.cpp, postInLoop.py) is public and the CPU is stated, but the compiler is not, so not A.
- **Verifier notes:** All quoted times match the results image (Restinio 1.025/0.85, Restbed 1.333/1.789, C++ REST SDK 3.401, Pistache 1.059/0.964, Crow 1.536/1.43). Corrected the record's caveat that the margin over Crow is 3 to 12 percent (it is 1.50x and 1.68x; only Pistache is close). Kept B as an independent measurement with public, equivalent service code; same benchmark the cpp-httplib entry uses (there tier C because cpp-httplib did not win).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 5); enricher w5 pair-034
- **Pages the verifier opened:**
  - <https://github.com/guteksan/REST-CPP-benchmark>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/images/rest_all.PNG>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/postInLoop.py>
  - <https://github.com/guteksan/REST-CPP-benchmark/tree/master/basic-restinio>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restinio/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restinio/CMakeLists.txt>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restbed/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restbed/CMakeLists.txt>
  - <https://github.com/Stiffstream/restinio>
  - <https://github.com/Stiffstream/restinio/commits>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/Stiffstream/restinio>
  - <https://github.com/Stiffstream/restinio/releases>
  - <https://github.com/Stiffstream/restinio/tree/master/dev>
  - <https://github.com/Stiffstream/restinio/tree/master/dev/benches>
  - <https://github.com/Stiffstream/restinio/tree/master/.github/workflows>
  - <https://github.com/Stiffstream/restinio/issues?q=is%3Aissue+performance+OR+slow+OR+crash+OR+leak>
  - <https://github.com/Stiffstream/restinio/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/Stiffstream/restinio/issues/148>
  - <https://github.com/Stiffstream/restinio/issues/177>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/externals.rb>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/dev/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/dev/restinio/incoming_http_msg_limits.hpp>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/dev/restinio/traits.hpp>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/dev/restinio/router/express.hpp>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/dev/restinio/router/easy_parser_router.hpp>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/v.0.6.2/README.md>
  - <https://raw.githubusercontent.com/Stiffstream/restinio/v.0.6.2/externals.rb>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/postInLoop.py>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restinio/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restinio/CMakeLists.txt>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restbed/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-pistache/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-crow/main.cpp>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/stiffstream/restinio`) · [data/wave5/enrich/raw/github_com_stiffstream_restinio.json](../../../data/wave5/enrich/raw/github_com_stiffstream_restinio.json) (enrichment confidence 0.75)

</details>
