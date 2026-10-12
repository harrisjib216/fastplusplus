# Ichor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> C++20/23 dependency-injection and event-queue framework with HTTP services on Boost.Beast; its 'faster than Beast' numbers come from a broken baseline.

| | |
|---|---|
| **Beats** | Boost.Beast (pure Beast http_server_fast-style server, beast_benchmark in the same repo) |
| **Claimed result** | No valid like-for-like win. Page rows, Ichor + Boost.Beast (keep-alive, 60 s runs) vs a pure Boost.Beast server that closes the connection after every response (10 s runs): 67,194.72 vs 41,397.00 req/s at 2 connections (about 1.6x, derived from page data), 87,048.80 vs 73,975.13 at 400 (about 1.18x, derived from page data), 72,971.55 vs 37,311.37 at 20,000 (about 1.96x, derived from page data). At 2 connections the Beast baseline's mean latency is lower (20.80 us vs 29.17 us), so its lower throughput comes from per-request reconnects. Drogon (132,285.77 / 132,936.53 / 117,676.17 req/s) and Go fasthttp (165,747.41 / 170,028.45 / 123,741.19 req/s) are faster than Ichor on the same page. |
| **Workload** | wrk POST of a small JSON body ({"sequence": 2}) to /ping on a localhost echo-style server, at 2, 400 and 20,000 connections, comparing Ichor's pong example (HTTP service layered on Boost.Beast) with a hand-written pure Boost.Beast server. |
| **Metric** | throughput |
| **Hardware** | AMD 7950X, 6000MHz CL38 RAM, Ubuntu 22.04 (stated at the top of the benchmarks README for the preliminary results; not restated in the HTTP section). |
| **Compiler and flags** | Ichor built with cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DICHOR_ARCH_OPTIMIZATION=X86_64_AVX2 -DICHOR_USE_BOOST_BEAST=ON -DICHOR_USE_SANITIZERS=OFF; the README setup line lists gcc 13.1.1 and clang 18 but does not say which compiled the HTTP runs. The Beast baseline is compiled in the same tree (guarded by ICHOR_USE_BOOST_BEAST); its num_workers and spin/block arguments for the runs are not stated. |
| **Adoption** | 237 stars |
| **Last commit** | 2026-02-06 |
| **Links** | [repository](https://github.com/volt-software/ichor) · [benchmark](https://raw.githubusercontent.com/volt-software/ichor/HEAD/benchmarks/README.md) |

## Verdict

On an AMD 7950X with Ubuntu 22.04 (gcc 13.1.1 or clang 18, not stated which), wrk POSTed {"sequence": 2} to /ping: Ichor's Beast-backed pong example reached 67,195 / 87,049 / 72,972 req/s at 2 / 400 / 20,000 connections against 41,397 / 73,975 / 37,311 req/s for a 'pure Beast' server that closes the connection after every response. The 1.18x-1.96x gap therefore measures per-request TCP reconnects (and, in the old architecture, an extra handler thread), not a faster HTTP stack; there is no valid evidence that Ichor beats Beast.

## Use it when

- You want an OSGi-style service lifecycle (dependencies appear and disappear at runtime, dependents are stopped and restarted) plus thread confinement in a C++20/23 codebase, and HTTP is one service among Redis, etcd, timers and TCP.
- You prefer coroutine route handlers over hand-written Beast session code and can live with Beast-level or lower throughput.
- Linux services that may later move to the io_uring queue without changing service code (the framework's stated goal of swapping submission/completion backends).
- Projects that want hardened builds by default (_FORTIFY_SOURCE=3, stack protector, -fno-rtti) and can vendor several submodules.

## Skip it when

- You need a faster HTTP server than Boost.Beast: no valid measurement shows one, and Drogon (about 132k req/s) and Go fasthttp (about 166k req/s) beat Ichor (about 67k-87k req/s) on Ichor's own benchmark page.
- Full HTTP/1.1 compliance, HTTP/2 or HTTPS without Boost.Beast: the README calls HTTP support partial.
- Large service graphs created at startup: the project's own conclusions say creating services with dependencies is likely O(N^2) and memory-heavy (the multi-threaded start benchmark peaks at about 300 MB).
- You want a small dependency footprint or a stable, widely used API: it is a single-maintainer 'personal project' (237 stars, version 0.5.0) that pulls in Boost (context, coroutine, fiber), a forked fmt, a forked static mimalloc, glaze, spdlog, Catch2 and liburing.
- macOS production use: support is described as partial (brew llvm, possible ASan false positives with Beast).

## How it is fast

There is no measured speed technique to credit: the HTTP path of the benchmarked build is Boost.Beast itself (Boost::v1::HttpHostService reads with http::async_read inside Asio stackful coroutines and writes through a per-connection outbox). What Ichor adds is structure: the read loop keeps reading the next request while the route handler runs as a queued event, and the framework runs on mimalloc, ankerl unordered_dense maps and glaze JSON. A non-Beast HTTP host on its own TCP services and an io_uring queue (liburing, Linux) also exist, but no HTTP numbers are published for them.

## Compared with alternatives

Pick Ichor only for its dependency-injection, lifecycle and thread-confinement model; for raw HTTP throughput over Boost.Beast, aeronet (2.75x on headers, 1.10-1.20x on static and routing at 10 connections) and libevhtp (about 1.15x) have valid comparisons, and Drogon is roughly 1.5-2x faster than Ichor on Ichor's own page.

## Integration

| | |
|---|---|
| **Form** | compiled library built with CMake (add_library without a type, so static unless BUILD_SHARED_LIBS is set; project ichor 0.5.0), with optional service sources selected by CMake flags |
| **Dependencies** | Boost 1.70+ (context, coroutine, fiber) for the Beast/Asio backend; git submodules fmt (fork), mimalloc (volt-software static fork), glaze, spdlog (optional), Catch2 (tests), liburing (Linux); OpenSSL for HTTPS; hiredis optional |
| **Minimum toolchain** | GCC 12+, Clang 15+ or MSVC 17.4+; CMake 3.22; CMake sets CMAKE_CXX_STANDARD 23 on non-Windows although the project describes itself as C++20 |
| **Platforms** | Linux (x86-64, aarch64, musl), Windows; partial macOS; io_uring backend Linux-only; arch tuning presets from X86_64 to AVX-512 and Raspberry Pi |
| **Thread safety** | Thread confinement: each DependencyManager and its services live on one event-queue thread; cross-thread communication goes through queued events, and code on threads Ichor does not manage is 'on your own' (README) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the Beast comparison: benchmarks/beast_benchmark/boost_beast_benchmark.cpp sets keep_alive(true) on the response but then calls shutdown(shutdown_send) and accept(), which closes the socket, after every response, so wrk reconnects for every request (read errors equal the request count in all three runs), while Ichor keeps connections open; each Beast worker also serves one connection at a time, and the worker count used is not stated. At 2 connections Beast's mean latency (20.80 us) beat Ichor's (29.17 us).
- The published Ichor runs are stale relative to the code: the top -H output shows separate 'HttpCon' and 'DepMan' threads (the README admits Ichor 'cheats' with an extra thread while Drogon, fasthttp and Beast ran on one), but the current BoostAsioQueue is a single-threaded io_context (BOOST_ASIO_CONCURRENCY_HINT_UNSAFE_IO) since the 'Refactor boost support to proper event loop, removing need for locks and threads' commit; the HTTP section dates from the Dec 2022 to Feb 2024 README revisions.
- Run lengths differ (Ichor 60 s, every other server 10 s), and the benchmarks README itself says the numbers identify bottlenecks rather than showcase performance.
- In the Beast-backed host, a request without keep-alive gets a keep_alive(false) response, but the server does not close the socket itself; the read loop only ends on end_of_stream, abort, timeout (30 s) or a bad descriptor.

## Known shortcomings

- Downgraded C to D: the pure Beast baseline (benchmarks/beast_benchmark/boost_beast_benchmark.cpp) calls shutdown_send and closes the socket after every response, so wrk reconnects on every request (read errors equal the request count: 418,099 / 740,671 / 374,703) while Ichor runs keep-alive; the 1.18x-1.96x is a harness artefact (crippled-baseline precedent). Beast's mean latency is lower at 2 connections (20.80 vs 29.17 us); Drogon and fasthttp are faster than Ichor on the same page; Ichor is built on Beast itself. MIT, active.
- Enricher: confirms the Beast baseline reconnects on every request (shutdown_send plus accept after each response; worker count unstated). Ichor's numbers are stale: the README's top -H shows separate HttpCon and DepMan threads ('cheats', README's word) but the current BoostAsioQueue is a single-threaded io_context since the 'Refactor boost support to proper event loop' commit; HTTP section dates December 2022 to February 2024; 60 s vs 10 s runs; Drogon and fasthttp faster on the same page. README says O(N^2) service creation; single maintainer, v0.5.0; C++23 on non-Windows.

## Caveats and trade-offs

First-party numbers, and the comparison is invalid as a speed claim: the pure Beast baseline in benchmarks/beast_benchmark/boost_beast_benchmark.cpp (adapted from Beast's http_server_fast example) sets keep_alive(true) in the response but then shuts down the send side and closes the socket after every response, so wrk must open a new TCP connection per request (every baseline run shows read errors equal to its request count: 418,099 / 740,671 / 374,703), while Ichor's pong example keeps connections alive and shows no socket errors. At 2 connections Beast's mean latency (20.80 us) is lower than Ichor's (29.17 us). Ichor is itself layered on Boost.Beast, and its README goal is only 'performance matching at least Boost Beast'. Ichor runs lasted 60 s and Beast runs 10 s; the Beast worker count is not stated. The benchmarks README says the benchmarks identify bottlenecks and do not showcase performance; proper throughput and latency benchmarks are TBD. The file was last updated 2024-02-02. Drogon and Go fasthttp are about 1.5x to 2.5x faster than Ichor on the same page. Hardware (AMD 7950X) is stated only at the top of the README for the preliminary core benchmarks.

C++20 framework (event queue, coroutines, dependency injection); the HTTP path is Boost.Beast underneath, HTTPS only through Beast, partial HTTP/1.1 implementation. The README says Ichor 'cheats' by running user logic on a separate thread from the networking thread while the other servers did everything on one thread. Service creation with dependencies is likely O(N^2) and uses a lot of memory per its own conclusions.

## Maintenance

Active single-maintainer MIT project (last commits 2026-02-06, no open issues), copyable and well hardened by default, but its HTTP numbers come from a crippled baseline on a 2022-2024 architecture that has since been rewritten, so treat it as a DI and lifecycle framework rather than a fast HTTP server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** The quoted numbers are on benchmarks/README.md, but the pure Boost.Beast baseline (benchmarks/beast_benchmark/boost_beast_benchmark.cpp) calls socket_.shutdown(shutdown_send) and accept() (which closes the socket) after every response, so wrk reconnects for every baseline request (read errors equal the request count in all three runs) while Ichor keeps connections alive; the measured win is a harness artifact, leaving no valid number showing Ichor faster than Beast (crippled-baseline precedent, as with AssemblyScript C to D).
- **Verifier notes:** Downgrade C to D: baseline Beast server closes every connection (shutdown_send + close after each response; wrk read errors = request count), Ichor uses keep-alive, so the 1.18x-1.96x figures are a harness artifact; with the lower Beast latency at 2 connections there is no valid evidence Ichor is faster than Beast. MIT, 237 stars, last commit 2026-02-06 (active) verified; keep-and-document candidate, not a fabrication.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://github.com/volt-software/ichor>
  - <https://github.com/volt-software/ichor/commits>
  - <https://github.com/volt-software/ichor/commits/main/benchmarks/README.md>
  - <https://github.com/volt-software/ichor/tree/main/benchmarks/beast_benchmark>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/README.md>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/benchmarks/beast_benchmark/boost_beast_benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/volt-software/ichor>
  - <https://github.com/volt-software/ichor/commits/main>
  - <https://github.com/volt-software/ichor/commits/main/benchmarks/README.md>
  - <https://github.com/volt-software/ichor/commits/main/src/ichor/event_queues/BoostAsioQueue.cpp>
  - <https://github.com/volt-software/ichor/issues>
  - <https://github.com/volt-software/ichor/tree/main/examples>
  - <https://github.com/volt-software/ichor/tree/main/examples/http_ping_pong>
  - <https://github.com/volt-software/ichor/tree/main/src/services/network>
  - <https://github.com/volt-software/ichor/tree/main/src/services/network/boost>
  - <https://github.com/volt-software/ichor/tree/main/src/services/network/http>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/README.md>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/benchmarks/beast_benchmark/boost_beast_benchmark.cpp>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/src/services/network/boost/HttpHostService.cpp>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/src/services/network/http/HttpHostService.cpp>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/src/ichor/event_queues/BoostAsioQueue.cpp>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/examples/http_ping_pong/pong.cpp>
  - <https://raw.githubusercontent.com/volt-software/ichor/HEAD/examples/http_ping_pong/PongService.h>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/volt-software/ichor`) · [data/wave5/enrich/raw/github_com_volt_software_ichor.json](../../../data/wave5/enrich/raw/github_com_volt_software_ichor.json) (enrichment confidence 0.7)

</details>
