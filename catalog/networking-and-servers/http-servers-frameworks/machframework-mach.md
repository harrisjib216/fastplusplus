# Mach

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 web framework with ASP.NET Core-style minimal APIs on Boost.Beast; mixed against an unnamed C# server, slower than Drogon.

| | |
|---|---|
| **Beats** | unspecified C# HTTP server (probably ASP.NET Core; the repo file is only labelled 'csharp', server code not included) |
| **Claimed result** | No faster-than claim is made; README says only 'designed to provide high HTTP throughput' and links machframework.dev/benchmarks (EGRESS_BLOCKED, not opened). The repo CSVs cover 7 wrk configs x 6 routes (42 rows per server). Against the file labelled 'csharp', Mach is faster on 20 of 42 rows and slower on 22 (derived from page data): at 16 threads / 100 connections plain 280385.96 vs 100290.9 req/s (2.80x), headers 280097 vs 221091.36 (1.27x), cookies 280342.45 vs 234736.06 (1.19x), body 156975.64 vs 101549.67 (1.55x), small JSON binding 280337.85 vs 253793.28 (1.10x), large JSON binding 149575.36 vs 307173.48 (0.49x); but at 1 thread / 1 connection and 2 threads / 10 connections the C# server is faster on every route (Mach 0.22x to 0.71x, e.g. plain 1/1 29137.3 vs 51441.04 req/s, 0.57x), and it wins every large-binding row. Against the file labelled 'drogon', Mach is slower on all 42 rows (Mach 0.13x to 0.65x; plain 16/100 280385.96 vs 1072586.17 req/s, Drogon 3.83x faster; derived from page data). |
| **Workload** | wrk against a trivial endpoint (204 no-content for 'plain'), 16 threads, 100 connections, 30 s, plus headers, cookies, body and JSON model-binding variants, run on loopback via benchmarks/runner/request_runner.py. |
| **Metric** | throughput |
| **Compiler and flags** | Runner uses the CMake 'release' build directory (build/release/benchmarks/RequestBenchmarks); exact compiler and flags not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/machframework/mach) · [benchmark](https://github.com/machframework/mach/tree/main/benchmarks/results) |

## Verdict

Mach claims no speedup; its repo holds wrk CSVs (7 thread/connection configs x 6 routes, loopback, 30 s, no hardware or compiler stated) where Mach's release build beats a C# server of unknown version on 20 of 42 rows (all at 4 or more wrk threads, up to 2.80x on the 204 route at 16/100) and loses all 1-thread, 2-thread and large-JSON rows, while Drogon is 1.53x to 7.60x faster on all 42 rows. Mach-only framework runs from 2026-09-24 (commit 5705b5a, 5 runs, 5 s warm-up, zero socket errors and non-2xx) give a median 273,576 to 277,064 req/s plaintext and about 243k to 252k req/s for model-binding and controller routes at 16 threads / 100 connections.

## Use it when

- Teams coming from ASP.NET Core who want the same minimal-API, controller, DI and validation model in C++20 on Windows (MSVC) or Ubuntu (GCC).
- Internal JSON APIs where about 250k req/s per box on loopback (Mach's own framework runs, 16 threads / 100 connections) is far above the real load.
- Projects that want an installer and project CLI (mach new, mach run) rather than wiring Boost.Beast by hand.

## Skip it when

- When throughput is the reason to switch: in Mach's own result files Drogon is faster on all 42 wrk rows (1.53x to 7.60x; plain 16/100 1,072,586 vs 280,386 req/s), and the C# server wins every 1-thread, 2-thread and large-JSON row.
- Handlers that block (database, file or RPC calls): handlers are synchronous and run on the shared I/O threads; asynchronous handlers are an open roadmap item (#88).
- Uploads or large bodies: request bodies are capped at 1 MiB, headers at 16 KiB and targets at 8 KiB in BeastSession.cpp; configurable limits are open issue #92.
- TLS, HTTP/2 or macOS: none appear in the library's source list; v1.0 supports only Windows/MSVC and Ubuntu/GCC.
- Production use that needs a track record: 4 stars, 0 forks, version bumped to 1.0.0 on 2026-09-23 with no tagged GitHub release.

## How it is fast

Nothing specific to Mach: it is a Boost.Beast coroutine session loop (C++20 awaitables) on one shared Boost.Asio io_context run by threadCount threads (default 4; the benchmark server uses std::thread::hardware_concurrency). Each request is adapted into two std::unordered_map&lt;std::string,std::string&gt; (lowercased headers and cookies), passes a DI scope and a middleware pipeline, and the response body is copied into a Beast response. Its own numbers plateau at about 277k to 292k req/s from 4 wrk threads up, which fits a single shared reactor (inference, not measured).

## Compared with alternatives

Pick Mach over Drogon, Crow or Oat++ only for its ASP.NET Core-style API (minimal APIs, controllers, DI, validation) and Windows/MSVC packaging; on speed, Drogon beats it on every row of Mach's own comparison files, and Crow and Oat++ carry independent the-benchmarker or TechEmpower-style results that Mach lacks.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target Mach::Mach) plus a CLI; Windows .msi and Ubuntu .deb packages |
| **Dependencies** | Boost.Asio and Boost.Beast (FetchContent downloads the Boost 1.90.0 source tarball if Boost is not found), nlohmann_json 3.12, fmt 12.1, spdlog 1.17; Catch2 for tests |
| **Minimum toolchain** | C++20 with &lt;format&gt; and coroutines, CMake 3.26; MSVC on Windows, GCC on Ubuntu (minimum versions not documented) |
| **Platforms** | Windows x64 (MSVC) and Ubuntu amd64 (GCC); others 'may be supported in future releases' |
| **Thread safety** | AppOptions is documented as not thread-safe during configuration and read-only safe afterwards; handlers run concurrently on up to threadCount I/O threads sharing one io_context, so handler and service state must be thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws in benchmarks/runner/request_runner.py, the script behind the C# and Drogon comparison files: one 30 s run per row with no warm-up, wrk and the server (hardware_concurrency threads) on the same loopback host with up to 16 wrk threads, and only Requests/sec and latency are parsed, so wrk's 'Non-2xx or 3xx responses' and 'Socket errors' lines are never recorded. The C# file is internally inconsistent: at 16 threads / 100 connections its large-JSON-binding route (307,173 req/s) runs 3.06x faster than its empty 204 route (100,291 req/s) with identical 81-byte responses, so the 20-of-42 C# 'wins' for Mach track run-to-run noise as much as the framework (derived from page data). The newer framework_runner.py does record errors, warm-up and 5-run medians, but covers Mach alone.
- Comparison servers do not return the same response: bytes per response derived from Transfer/sec divided by Requests/sec are 86 for Mach, 81 for the C# server and 127 for Drogon on every route, so Drogon's handler sends a bigger reply than Mach's 204 and still wins; the C# and Drogon server sources, versions and build flags are not in the repo.
- BeastSession::handle_request sets 'Content-Type: text/plain' on every response after copying the handler's headers (src/server/BeastSession.hpp), and content-type is not on the reserved list, so a handler's own Content-Type such as application/json is overwritten (read from code at HEAD, not run).
- BeastListener::do_accept creates each socket on its own strand but co_spawns the session on the raw io_context; the strand executor it computes is unused, so with more than one thread the session coroutine is not serialised with beast::tcp_stream's timeout handler, which BeastSession::run's comment says requires a strand (latent race on request timeouts; inference from code, not observed).

## Known shortcomings

- Tier C, claim overstated: repo CSVs only; the C# file wins every 1-thread and 2-thread row plus all large-binding rows (Mach wins 20 of 42) and Drogon is 1.53x-7.60x faster on all 42 rows; no C# server source, hardware or flags; machframework.dev blocked; 4 stars.
- Enricher: request_runner.py does 1 run with no warm-up, wrk and server on the same host, non-2xx and socket errors never recorded; the C# results file is inconsistent (binding_large 307,173 vs plain 100,291 req/s at 16/100 with the same 81-byte responses), so the 20-of-42 C# wins are noise-prone; bytes per response differ (Mach 86, C# 81, Drogon 127) and Drogon is faster on all 42 rows. Code bugs read, not run: handle_request forces Content-Type text/plain on every response (overwriting application/json), session co_spawned on the io_context rather than a strand (latent timeout race); handlers synchronous (#88), 1 MiB body cap (#92).

## Caveats and trade-offs

Weak and mixed evidence. (1) Mach publishes no claim of beating any named baseline; the only comparison data are two CSVs (request_wrk_results_csharp.csv and request_wrk_results_drogon.csv) with no server source, no versions, no hardware, no compiler flags. (2) The Mach rows (request_wrk_results.csv, commit de36047, 2026-08-11T00:26) and the comparison rows (commit 34c12a4, 2026-08-11T11:57 and 13:26) are from different runs and may not share a machine or build. (3) Handler work in the comparison servers is unknown; Mach's 'plain' route returns 204 no content. (4) The C# 'win' is selective: Mach beats the C# file only at 4 or more wrk threads (20 of 42 rows) and loses every 1-thread and 2-thread row and every large-JSON-binding row; Mach's own throughput plateaus at about 280k to 292k req/s from 4 threads up while the C# server falls off at 16 threads, which on a loopback run suggests client/server CPU contention rather than a framework difference (inference, not measured). (5) Drogon, the C++ incumbent, is 1.53x to 7.60x faster than Mach on every one of the 42 rows (derived from page data). (6) Website results page machframework.dev/benchmarks could not be opened (EGRESS_BLOCKED). Not evidence that Mach is faster than the C++ incumbent; 4 stars.

Built on Boost.Asio and Boost.Beast. v1.0 supports only Windows (MSVC) and Ubuntu (GCC). Very new, tiny user base (3 stars), 526 commits on main.

## Maintenance

Active (last commit 2026-09-27, version bumped to 1.0.0 on 2026-09-23, four open v1.1.0 roadmap issues) and MIT-licensed, but a very young project with 4 stars and 0 forks whose own benchmark files do not show it beating the C++ incumbent.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party wrk CSVs in benchmarks/results (request_wrk_results.csv for Mach at commit de36047, request_wrk_results_csharp.csv and request_wrk_results_drogon.csv at commit 34c12a4) with the runner benchmarks/runner/request_runner.py public, but no source for the C# or Drogon servers, no hardware, no compiler or flags; partial methodology from the project itself is tier C.
- **Verifier notes:** CSV numbers in the record are exact, but the record quotes only the 16-thread/100-connection rows: the C# server beats Mach on all 1-thread and 2-thread rows and on every large-binding row (Mach wins 20 of 42), and Drogon beats Mach on all 42 rows. Shortcomings: not faster than the C++ incumbent (Drogon), mixed against an unidentified C# server with no source, first-party, no hardware or flags, 4 stars. Metadata checked: MIT, not a fork, last commit 2026-09-27, active.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 5); enricher w5 pair-028
- **Pages the verifier opened:**
  - <https://github.com/machframework/mach>
  - <https://github.com/machframework/mach/commits>
  - <https://github.com/machframework/mach/tree/main/benchmarks>
  - <https://github.com/machframework/mach/tree/main/benchmarks/results>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results_csharp.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results_drogon.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/framework_wrk_summary.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/framework_wrk_results.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/runner/request_runner.py>
- **Sources the enricher read:**
  - <https://github.com/machframework/mach>
  - <https://github.com/machframework>
  - <https://github.com/machframework/mach/commits/main>
  - <https://github.com/machframework/mach/issues>
  - <https://github.com/machframework/mach/tree/main/include/mach>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/README.md>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/cmake/Dependencies.cmake>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/include/mach/AppOptions.hpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/include/mach/Reply.hpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/include/mach/Response.hpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/include/mach/Json.hpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/server/Server.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/server/BeastListener.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/server/BeastSession.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/server/BeastSession.hpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/application/Runtime.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/dispatching/Dispatcher.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/adapter/inbound/BeastRequestAdapter.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/adapter/outbound/BeastResponseAdapter.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/http/Response.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/http/ContentType.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/results/Results.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/src/routing/RouteTrie.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/request/RequestBenchmarks.cpp>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/scripts/request/wrk-body.lua>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/scripts/request/wrk-small.lua>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/scripts/request/wrk-large.lua>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/runner/request_runner.py>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/runner/framework_runner.py>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results_csharp.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/request_wrk_results_drogon.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/framework_wrk_summary.csv>
  - <https://raw.githubusercontent.com/machframework/mach/HEAD/benchmarks/results/framework_wrk_results.csv>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/machframework/mach`) · [data/wave5/enrich/raw/github_com_machframework_mach.json](../../../data/wave5/enrich/raw/github_com_machframework_mach.json) (enrichment confidence 0.6)

</details>
