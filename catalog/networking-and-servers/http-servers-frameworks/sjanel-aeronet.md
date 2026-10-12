# aeronet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++23 HTTP/1.1, HTTP/2 and WebSocket server library; out-serves Go net/http and mostly Boost.Beast in first-party single-thread tests.

| | |
|---|---|
| **Beats** | Boost.Beast and Go net/http |
| **Claimed result** | vs beast (10 conns): headers 12,035.73 vs 4,376.77 req/s (2.75x), static 54,259.34 vs 49,281.00 (1.10x), routing 57,644.49 vs 47,995.38 (1.20x). vs go net/http (10 conns): headers 12,035.73 vs 3,996.83 (3.0x), static 54,259.34 vs 25,399.27 (2.14x), routing 57,644.49 vs 28,141.20 (2.05x), mixed 25,261.40 vs 9,003.95 (2.81x), body 3,827.02 vs 407.32 (9.4x); at 100 conns aeronet leads go net/http in every scenario (e.g. static 93,479.14 vs 37,787.70, routing 91,957.05 vs 44,446.00) (all derived from page data) |
| **Workload** | wrk-driven HTTP/1.1 benchmark (1 thread, 30s duration, 5s warmup) across headers/body/body-codec/static/cpu/mixed/files/routing scenarios at 10 and 100 connections, run in CI against scripted competitor servers built from the same harness. |
| **Metric** | throughput |
| **Compiler and flags** | CMake Release (-DCMAKE_BUILD_TYPE=Release, Ninja) on GitHub Actions ubuntu-latest with apt build-essential GCC (workflow comment: 'Both use GCC'); GCC version not pinned; no explicit -O flags beyond the CMake Release default; Go server built with stdlib net/http; Beast server built in the same Release CMake config |
| **Adoption** | 44 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/sjanel/aeronet) · [benchmark](https://sjanel.github.io/aeronet/benchmarks/) |

## Verdict

The author's GitHub Actions dashboard (run of 2026-09-26) is a per-core test: every server is built with GCC in CMake Release on an ubuntu-latest runner (no CPU model or GCC version stated) and gets one thread (Go GOMAXPROCS=1, Beast one io_context thread), with wrk driving 30 s after a 5 s warmup at 10 and 100 connections. aeronet beat Go net/http in all 16 scenario/connection cells (for example 2.14x on static and 2.05x on routing at 10 connections) and Boost.Beast in 13 of 16, but lost to Beast on cpu at 10 connections and on static and routing at 100.

## Use it when

- Linux C++ microservices that need HTTP/1.1, HTTP/2 (h2 and h2c), WebSocket and TLS from one library, with Kubernetes probes and (experimental) OpenTelemetry built in.
- Header-heavy or body-heavy request handling: at 10 connections it served 2.75x Beast's req/s on the many-headers test and 6.9x on the 'body' POST test, and 3.0x and 9.4x Go net/http.
- Replacing a hand-rolled Boost.Beast server when you want routing, middleware, compression and static-file serving without writing the asio plumbing yourself.
- APIs with large route tables: in the 1,000-route test it did 57.6k req/s vs Beast's 48.0k and Go's 28.1k at 10 connections.
- Projects already on C++23 (GCC 13+, Clang 21, MSVC 17.x) that can build with CMake 3.28+.

## Skip it when

- Static-file or tiny-response loads at high connection counts: at 100 connections Beast (96.4k) and Drogon (99.7k) beat it on the static test, and Beast won 1,000-route routing (100.8k vs 92.0k).
- Toolchains below C++23, GCC 13 or CMake 3.28; the install guide says GCC 12 may lack needed C++23 features.
- When you need a proven production track record: the project started in September 2025, has 44 stars, and one maintainer made 1,329 of about 1,358 commits.
- When you need HTTP/3/QUIC (not in the feature matrix) or an async HTTP/2 client: the bundled HttpClient is synchronous and carries one HTTP/2 stream at a time.
- Peak performance on macOS or Windows: kTLS, sendfile and MSG_ZEROCOPY are Linux-only, and Windows uses WSAPoll.

## How it is fast

One edge-triggered epoll reactor per thread (kqueue on macOS, WSAPoll on Windows), scaled across cores with SO_REUSEPORT so each thread has its own listening socket and no shared accept lock. Requests are parsed in place: HttpRequestView fields are std::string_views into a pooled per-connection buffer, and CRLF scanning uses memchr. Responses are built in one contiguous buffer (status line, headers, body) and sent with writev plus TCP_CORK, with a Date header cached once per second; literal routes sit in a CityHash flat_hash_map and pattern routes in a radix tree. Linux-only extras include sendfile, kTLS and MSG_ZEROCOPY (128 KiB threshold).

## Compared with alternatives

Pick aeronet over Drogon or Crow when you need HTTP/2 and WebSocket in the same C++ library (the harness excludes Drogon and Crow from HTTP/2 runs for lack of support) and the header-, body- and route-heavy wins shown here matter. Pick Drogon for a longer production record and ecosystem (it also won static and files at 100 connections here), or libevhtp or Lwan if you want plain C.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (AERONET_BUILD_SHARED=ON); experimental C++20 module interface |
| **Dependencies** | none for a plain HTTP build; optional OpenSSL 1.1.1/3.x (TLS, JWT), zlib or zlib-ng, zstd, brotli, spdlog, glaze, opentelemetry-cpp plus protobuf. Vendors amc, skarupke flat_hash_map and CityHash. |
| **Minimum toolchain** | C++23, CMake 3.28+; tested GCC 13 and Clang 21, MSVC 17.x (VS 2022), Apple Clang from Xcode 15; modules need GCC 15 or Clang 18 |
| **Platforms** | Linux x86-64 and aarch64 (primary, epoll); macOS arm64/x86-64 (kqueue); Windows x64 (WSAPoll) |
| **Thread safety** | Each SingleHttpServer is single-threaded and runs handlers on its event-loop thread; change routes or config on a running server only through router()/postRouterUpdate()/postConfigUpdate(). HttpServer runs N such reactors with the same handlers, so state shared by handlers needs your own synchronization. |
| **Drop-in for the baseline** | no |

## Gotchas

- Before 1.5.0, built-in CONNECT tunneling was on and fail-open by default, which made any default-config server an unauthenticated open proxy (GHSA-m9r8-5wrg-mvh5, CVSS 8.6). Use 1.5.0 or later, where an empty connectAllowlist disables CONNECT.
- Handlers run on the reactor thread, so a blocking or CPU-heavy handler stalls every connection on that thread. Use coroutine handlers or push the work to other threads.
- Request path, headers and body are string_views into the connection buffer. Copy anything you keep after the handler returns; in async handlers, co_await req.bodyAwaitable() before you read the body.
- Date, Connection, Content-Length, Transfer-Encoding, Trailer, TE and Upgrade are reserved, and header names are forced to lower-case. header() scans and memmoves, so fill a response in order: status, headers, then body. Server move operations are not noexcept and throw if the server is running.

## Known shortcomings

- Boost.Beast beats it in 3 of 16 cells (cpu at 10 connections, static and routing at 100). Project's own dashboard; GCC version not pinned.
- Security: before 1.5.0 (2026-08-20) CONNECT tunnelling was on and fail-open by default, making default servers unauthenticated open proxies (GHSA-m9r8-5wrg-mvh5, CVSS 8.6). The benchmark is single-core only (1 thread each; Go with GOMAXPROCS=1). The harness's Beast server sends files without sendfile (87 req/s at 10 connections), so several ratios against Beast reflect that server, not Beast; Beast wins 3 of 16 cells and Drogon wins static and files at 100 connections. wrk gets extra threads in some scenarios while the dashboard says 'Threads: 1'. LICENSE is MIT with the '[year] [fullname]' placeholder unfilled; vendored skarupke flat_hash_map has no licence. Created 2025-09, one main maintainer. Needs C++23 and CMake 3.28+; blocking handlers stall their event-loop thread; no HTTP/3.

## Caveats and trade-offs

First-party CI benchmark (project builds and runs all competitors itself); GitHub Actions ubuntu-latest runner is a generic shared/virtualized host with no CPU model stated, and the GCC version is not pinned, so this falls short of Tier A despite public benchmark code and full wrk parameters. Dashboard is regenerated on every push to main (30s x1 sample) and weekly (45s x3-sample median), so numbers move run-to-run. aeronet does not beat Boost.Beast everywhere: in the 2026-09-26 run Beast was faster on cpu at 10 conns (7,354.19 vs 7,120.30), static at 100 conns (96,444.03 vs 93,479.14) and routing at 100 conns (100,848.37 vs 91,957.05); drogon also beat aeronet on static at 100 conns (99,662.33) and files at 100 conns (2,496.81 vs 2,490.52). aeronet beat Go net/http in all 16 scenario/connection cells. LICENSE is MIT text with an unfilled '[year] [fullname]' placeholder (GitHub reports NOASSERTION).

Linux-focused for peak performance (also supports macOS/Windows); benchmark harness builds and runs competitor servers (drogon, pistache, crow, beast, Rust Axum, Java Undertow, Go net/http, Python) itself in CI rather than using each project's own tuned deployment configuration, so absolute numbers may not reflect each competitor's best-case tuning.

## Maintenance

Active: commits on 2026-09-26 and releases v1.0.0 (January 2026) to v1.5.0 (August 2026). It is effectively a one-person project, and its MIT LICENSE file still has the '[year] [fullname]' placeholder (GitHub reports NOASSERTION); the README also lists vendored flat_hash_map code as having no license, so check with legal before you ship it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Live dashboard (run 2026-09-26 16:19 UTC) shows aeronet vs beast and go rows with every quoted req/s figure; benchmark code is public (benchmarks/scripted-servers/run_benchmarks.py, \*_server.cpp, go_server.go, lua/\*.lua, .github/workflows/benchmarks-gh-pages.yml) but no CPU model and no pinned compiler version, so not A; first-party, so C.
- **Verifier notes:** All claimed_speedup figures match the live page exactly; the 100-conn go comparison claim ('leads in every scenario') checks out. Added caveat that Beast wins 3 of 16 cells (cpu@10, static@100, routing@100), so the Beast claim is scenario-dependent. License NOASSERTION on GitHub, but the LICENSE file is MIT text, so MIT/copyable stays.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://sjanel.github.io/aeronet/benchmarks/>
  - <https://github.com/sjanel/aeronet>
  - <https://github.com/sjanel/aeronet/blob/main/LICENSE>
  - <https://github.com/sjanel/aeronet/blob/main/.github/workflows/benchmarks-gh-pages.yml>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/README.md>
  - <https://github.com/sjanel/aeronet/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/sjanel/aeronet>
  - <https://github.com/sjanel/aeronet/blob/main/README.md>
  - <https://github.com/sjanel/aeronet/blob/main/docs/INSTALL.md>
  - <https://github.com/sjanel/aeronet/blob/main/docs/FEATURES.md>
  - <https://github.com/sjanel/aeronet/blob/main/LICENSE>
  - <https://github.com/sjanel/aeronet/blob/main/VERSION>
  - <https://github.com/sjanel/aeronet/releases>
  - <https://github.com/sjanel/aeronet/issues>
  - <https://github.com/sjanel/aeronet/security/advisories/GHSA-m9r8-5wrg-mvh5>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/README.md>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/run_benchmarks.py>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/go_server.go>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/beast_server.cpp>
  - <https://github.com/sjanel/aeronet/blob/main/benchmarks/scripted-servers/aeronet_server.cpp>
  - <https://github.com/sjanel/aeronet/blob/main/.github/workflows/benchmarks-gh-pages.yml>
  - <https://github.com/sjanel/aeronet/blob/main/aeronet/http/include/aeronet/router.hpp>
  - <https://github.com/sjanel/aeronet/blob/main/aeronet/http/include/aeronet/http-response.hpp>
  - <https://github.com/sjanel/aeronet/blob/main/aeronet/server/src/http-parser.cpp>
  - <https://github.com/sjanel/aeronet/blob/main/aeronet/tech/include/aeronet/search-crlf.hpp>
  - <https://github.com/sjanel/aeronet/blob/main/aeronet/tech/include/aeronet/avx2.hpp>
  - <https://sjanel.github.io/aeronet/benchmarks/>
  - <https://hn.algolia.com/api/v1/search?query=aeronet%20http&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=sjanel%2Faeronet>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/sjanel/aeronet`) · [data/wave5/enrich/raw/github_com_sjanel_aeronet.json](../../../data/wave5/enrich/raw/github_com_sjanel_aeronet.json) (enrichment confidence 0.8)

</details>
