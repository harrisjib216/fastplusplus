# cofetch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only async HTTP client on libcurl's multi interface and ASIO; out-runs one-request-at-a-time cpr and cpp-httplib clients by multiplexing.

| | |
|---|---|
| **Beats** | cpp-httplib (sync client) and cpr (libcurl wrapper) |
| **Claimed result** | README: '+35% single-thread throughput over the fastest sync client, +31% with one event loop per core against equal-sized thread pools, +16% on sequential chains driven from a busy-poll loop'. bench/README.md (results dated 2026-07-10), one thread, 20,000 GETs: cofetch 18,240 req/s (busy poll) and 17,412 req/s (run()) vs cpp-httplib 12,889 and cpr 10,127 (1.35x run() and 1.42x busy poll over cpp-httplib, derived from page data); 20 threads: cofetch 166,646 req/s vs cpp-httplib 127,333 and cpr 122,122 (1.31x, derived from page data); 2,000-request chain: cofetch busy poll 14,804 req/s vs cpp-httplib 12,761 and cpr 10,209 (1.16x, derived from page data), but cofetch run() 11,116 and coroutine 10,547 are slower than cpp-httplib. With 10 ms injected RTT one cofetch thread (9,353 req/s) ties 100-thread pools (cpp-httplib 9,571, cpr 9,345) and is about 98x a single-threaded sync client (95 and 94 req/s); at 50 ms RTT cofetch 1,819 req/s vs 100-thread pools about 1,918 (cofetch about 5% slower, derived from page data) and sync clients 20 req/s. |
| **Workload** | 20,000 HTTP GETs against a local nginx (keep-alive) with 100 requests in flight: one cofetch thread against one-request-at-a-time synchronous cpr and cpp-httplib clients; also 20 threads per client, 10 ms and 50 ms injected RTT, and a 2,000-request dependent chain. |
| **Metric** | throughput |
| **Hardware** | WSL2 host with 20 logical cores (CPU model not stated); run-to-run variance about +/-10% per the page |
| **Compiler and flags** | gcc 14 -O3 (CMake Release build driven by bench/run_bench.sh), libcurl 8.14 (system libcurl, also used by cpr via CPR_USE_SYSTEM_CURL=ON), asio 1.38; cpr 1.11.2 and cpp-httplib v0.20.0 pinned via FetchContent in bench/CMakeLists.txt; Debian 13 on WSL2; nginx from bench/nginx.conf (4 workers, keep-alive, access log off) on the same host |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/SSARCandy/cofetch) · [benchmark](https://github.com/SSARCandy/cofetch/blob/main/bench/README.md) |

## Verdict

First-party runs (2026-07-10, gcc 14 -O3, libcurl 8.14, asio 1.38, Debian 13 on WSL2 with 20 logical cores, CPU model not named) of 20,000 keep-alive GETs against a local 4-worker nginx returning a 28-byte JSON: one cofetch thread with 100 requests in flight did 17,412 req/s (run()) and 18,240 (busy poll) against cpp-httplib 12,889 and cpr 10,127 with one request in flight, and with 20 threads 166,646 vs 127,333 and 122,122 while cofetch kept 5x the in-flight requests. Every driver checks the status of every response and all rows report 0 failures, so the gains are concurrency, not a faster per-request path (an internal raw-epoll client is about 14% faster still), and they predate the 2026-09-29 fix commit c1bd40f.

## Use it when

- A C++ service already running an asio (or Boost.Asio) event loop that must fan out many outbound HTTP calls without a thread per request.
- Workloads with real network latency: one thread with 100 requests in flight matched a 100-thread cpr or cpp-httplib pool at 10 ms RTT and was about 98x a single blocking client.
- Latency-sensitive loops (trading-style) that already busy-poll: busy-poll mode was the fastest client in the 2,000-request dependent chain (14,804 req/s vs cpp-httplib 12,761).
- Code that wants co_await for dependent requests while keeping libcurl's HTTP/2, TLS and compression support.

## Skip it when

- Simple scripts or tools making a few sequential requests in the default run() mode: in the chain test cofetch run() (11,116 req/s) and its coroutine form (10,547) were slower than cpp-httplib (12,761).
- Very high RTT links where you already have a thread pool: at 50 ms RTT one cofetch thread (1,819 req/s) was about 5% behind 100-thread pools (about 1,918).
- Multi-threaded callers sharing one client: a Client is not thread-safe and must live on its io_context's thread.
- You need a server, a zero-dependency build, or a streaming download API: cofetch is client-only, needs libcurl plus ASIO, and buffers each whole response body into a std::string.
- Production use that needs a track record: first commit 2026-07-10, 8 stars, no issues filed yet, and no Windows CI.

## How it is fast

It uses libcurl's multi socket API (CURLMOPT_SOCKETFUNCTION and CURLMOPT_TIMERFUNCTION) and hands every socket curl opens to an asio socket, so one thread waits on all transfers through asio's reactor (epoll on Linux) instead of parking one OS thread per request. Hot-path tweaks from the 2026-07-10 tuning: easy handles and transfer nodes are pooled and reused without curl_easy_reset (static options set once per handle), curl's 0 ms timer kicks become one deduplicated asio::post, timer rescheduling is skipped when the pending expiry is early enough, handlers use asio::recycling_allocator, and completions are invoked directly instead of dispatched. An optional busy-poll mode (io_context::poll() in a spin loop) removes the kernel sleep and wake per request that hurts the sequential-chain case.

## Compared with alternatives

Every catalogued sibling in this category is a server or a framework (Drogon, Crow, cinatra, aeronet, Sogou Workflow's HTTP server) or a Go library (fasthttp, whose client is claimed up to 4x net/http); pick cofetch when the job is outbound HTTP from C++ inside an asio event loop. If you also need to serve HTTP, pair it with one of those servers rather than replacing them.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | libcurl &gt;= 7.55 (linked) and standalone ASIO or Boost.Asio (-DCOFETCH_USE_BOOST_ASIO); vendored asio submodule optional; also available as a vcpkg port |
| **Minimum toolchain** | C++17 (C++20 for the co_await interface); CMake 3.14 for the package config; CI builds with gcc and clang on ubuntu-24.04 and clang on macOS |
| **Platforms** | Linux and macOS tested in CI; Windows has code paths (_WIN32) but no CI job, and there the resolver descriptor is not watched |
| **Thread safety** | Not thread-safe: one Client per io_context, used from that loop's thread; Clients on different threads are fine (curl_global_init is serialized behind a mutex, covered by a 4-thread test). |
| **Drop-in for the baseline** | no |

## Gotchas

- Completion handlers are invoked inline from the client's curl-message loop (check_completions) without dispatching to the handler's associated executor, so a handler bound to a strand or another io_context runs on the client thread; by code reading, destroying the Client from inside a completion (for example a coroutine that owns the Client returning right after co_await) would leave check_completions iterating a freed multi handle, and no test covers that case.
- Destroying a Client drops in-flight requests and never calls their handlers (documented and tested), so pending futures or awaiting coroutines do not complete normally; drain the io_context first.
- Every request has a 5 s whole-transfer timeout by default, redirects are not followed by default (a 3xx arrives with is_ok() false), and HTTP error statuses are not reported through the error_code; check is_ok() or http_code_.
- Each easy handle asks for a 512 KiB receive buffer (CURLOPT_BUFFERSIZE) and up to 64 idle handles are pooled by default; bench note: the RTT script says each run holds about 10 s of steady state, but its 100-in-flight runs are sized to about 2 s (results.csv: 2.09-2.20 s), and the 20-thread tier lasts 0.12-0.16 s including thread and Client start-up; only cofetch gets warm-up runs.

## Known shortcomings

- bench/README.md (gcc 14 -O3, WSL2, 20 cores, no CPU model): the gain comes from async multiplexing (100 requests in flight) against synchronous cpr 1.11.2 and cpp-httplib v0.20.0 with 1 in flight (the 20-thread tier still gives cofetch 5x the in-flight count); the README's 'wins every scenario' is false per its own RTT rows (ties 100-thread pools at 10 ms, pools about 5% faster at 50 ms); chain wins only in busy-poll mode. HTTP client filed under http-servers-frameworks (Boost.Beast precedent).
- Bench drivers are honest (all rows 0 failed) but only cofetch gets warm-up runs; run_netem.sh claims about 10 s of steady state while the 100-in-flight runs last about 2 s (results.csv 2.09-2.20 s) and the 20-thread tier runs 0.12-0.16 s including thread and Client start-up. Code-reading risks: handlers are invoked inline and skip the associated executor; destroying the Client inside a completion leaves check_completions on a freed multi handle (untested). No Windows CI.

## Caveats and trade-offs

First-party benchmark with public code (bench/) but the CPU model is not stated, so tier C. The headline is asynchronous (100 requests in flight on one thread) against synchronous clients with one request in flight, so the single-thread win measures concurrency, not a faster HTTP client. In the 20-thread tier cofetch splits 100 in-flight requests over 20 loops (5 each) while the cpr and cpp-httplib pools keep only 20 in flight, so 'equal-sized thread pools' still gives cofetch 5x the concurrency; those runs last only 0.12-0.16 s. The README's 'wins every scenario' is contradicted by its own RTT rows: at 10 ms RTT one cofetch thread only ties 100-thread pools (cpp-httplib's pool is 2% faster) and at 50 ms RTT the pools are about 5% faster (derived from page data). In the sequential chain the README uses the busy-poll mode: in the default run() mode cofetch (11,116 req/s) and its coroutine form (10,547 req/s) are slower than cpp-httplib (12,761 req/s), and the page says so. Loopback to a local nginx sharing the WSL2 host, not a real network; run-to-run variance about +/-10% per the page. Compared to cpr both sit on libcurl. The page also reports an internal epoll baseline about 14% faster than cofetch on loopback. The numbers (2026-07-10) predate commit c1bd40f (2026-09-29), which fixed leaked in-flight easy handles at Client destruction, resolver descriptors ignored by socket_cb and multi-block header parsing, and added transfer-node recycling; none of these affect the IP-literal, redirect-free benchmark's correctness, but the published numbers are from older code. HTTP client, filed under http-servers-frameworks for lack of a client category.

Header-only (needs libcurl and ASIO), C++17, C++20 coroutines optional; callbacks, futures and coroutines from one implementation; libcurl gives HTTP/2, TLS and connection pooling. Needs an asio::io_context to drive it. Very new repo (first commit 2026-07-10).

## Maintenance

Active (v0.1.2; 84 commits, the last on 2026-09-29 fixing leaked in-flight handles, resolver-descriptor watching and multi-block header parsing), MIT, header-only and in vcpkg, but brand new with 8 stars and no external bug reports yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark with public code (bench/run_bench.sh, bench/bench_cofetch.cpp, bench_cpr.cpp, bench_httplib.cpp, bench/results.csv) and stated compiler and flags (gcc 14 -O3 Release), but the host is described only as WSL2 with 20 logical cores and no CPU model, so it cannot reach A; no independent measurement exists.
- **Verifier notes:** Numbers and the bench harness check out; the drivers are honest (keep-alive sessions for cpr and cpp-httplib, status checked on every response) and the README's +35/+31/+16% match the bench/README tables, but the gain is from async multiplexing versus one-request-per-thread sync clients, the 20-thread tier gives cofetch 5x the in-flight requests, and the RTT rows show 100-thread pools tie or beat it (about 5% faster at 50 ms). Category: cofetch is client-only; http-servers-frameworks (Boost.Beast is a client and server library) is acceptable, and event-loops-io is the plausible alternative since the measured win comes from the asio reactor; neither cpr nor cpp-httplib is a listed baseline. Small project (8 stars, 2 forks) but published as a vcpkg port; MIT, last commit 2026-09-29.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party bench README (verifier); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://github.com/SSARCandy/cofetch>
  - <https://github.com/SSARCandy/cofetch/commits>
  - <https://github.com/SSARCandy/cofetch/commits/main>
  - <https://github.com/SSARCandy/cofetch/tree/main/bench>
  - <https://github.com/SSARCandy/cofetch/blob/main/bench/README.md>
  - <https://github.com/SSARCandy/cofetch/commit/c1bd40f3694ad6febdfc2f77b54479df6912163f>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/README.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/run_bench.sh>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_cofetch.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_cpr.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_httplib.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_util.h>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/results.csv>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/nginx.conf>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/SSARCandy/cofetch>
  - <https://github.com/SSARCandy/cofetch/commits/main>
  - <https://github.com/SSARCandy/cofetch/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/README.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/run_bench.sh>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/run_netem.sh>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_cofetch.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_cpr.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_httplib.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_epoll.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/bench_util.h>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/results.csv>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/bench/nginx.conf>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/include/cofetch.h>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/docs/api-reference.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/test/cofetch_tests.cpp>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SSARCandy/cofetch/HEAD/LICENSE>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/ssarcandy/cofetch`) · [data/wave3/enrich/raw/github_com_ssarcandy_cofetch.json](../../../data/wave3/enrich/raw/github_com_ssarcandy_cofetch.json) (enrichment confidence 0.75)

</details>
