# cpp-httplib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++11 HTTP/1.1 client and server; easiest to embed, but not shown faster than C++ REST SDK.

| | |
|---|---|
| **Beats** | C++ REST SDK (cpprestsdk) v2.10.15 HTTP server |
| **Claimed result** | Read from images/rest_all.PNG (time from first request received to last reply, 10 producers x N requests). Local, N=1000, t=0 ms, C=28: cpp-httplib v0.5.8 3.015 s vs C++ REST SDK 3.401 s (1.13x faster, derived from page data). In the other five cells where C++ REST SDK completed (all C=28) cpp-httplib is slower or tied: VPN N=1000 t=0 3:31.510 vs 1:52.476 (1.88x slower, derived from page data); Local N=200 t=200 40.359 s vs 40.281 s; Local N=1000 t=200 3:21.790 vs 3:21.415; VPN N=200 t=200 1:22.168 vs 1:01.523 (1.34x slower, derived from page data); VPN N=1000 t=200 6:51.648 vs 5:11.715 (1.32x slower, derived from page data). In all six C=4 cells C++ REST SDK deadlocked while cpp-httplib finished (e.g. 1.915 s at Local N=1000 t=0). In the Local sprint cell cpp-httplib is slower than Crow (1.536 s), Pistache (1.059 s), Restbed (1.333 s) and Restinio (1.025 s), and it is marked worst (red) in 7 of the 12 cells. |
| **Workload** | Independent shootout (guteksan/REST-CPP-benchmark, 2020): 10 Python producer processes (postInLoop.py, http.client, a new TCP connection per request, printing under a shared lock) each POST N=200 or 1000 small JSON messages to a /test echo endpoint that sleeps t=0 or 200 ms; services use C=28 or C=4 worker threads and run Local (same machine) or over a VPN; metric is time from the service's first logged request reception to its last reply (log4cplus timestamps), one run per cell. |
| **Metric** | throughput |
| **Hardware** | 28x Intel Xeon CPU E5-2660 v4 @ 2.0 GHz, 64 GB RAM, Ubuntu 16.04.3 LTS |
| **Compiler and flags** | CMake -DCMAKE_BUILD_TYPE=Release, CMAKE_CXX_STANDARD 14, thread pool left at the library default (CPPHTTPLIB_THREAD_POOL_COUNT define commented out in basic-httplib/main.cpp); compiler and version not stated |
| **Adoption** | 16.9k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/yhirose/cpp-httplib) · [benchmark](https://github.com/guteksan/REST-CPP-benchmark) |

## Verdict

The only numbers come from a single-run 2020 shootout (guteksan/REST-CPP-benchmark; 28-thread Xeon E5-2660 v4, Ubuntu 16.04, CMake Release, compiler unstated). Ten Python processes POSTed small JSON to cpp-httplib v0.5.8 and cpprestsdk v2.10.15, opening a new connection per request. cpp-httplib won one of six comparable cells (local, 1000 requests each, no delay: 3.015 s vs 3.401 s, 1.13x), tied two and lost three by up to 1.88x over VPN; in the C=4 cells cpprestsdk deadlocked.

## Use it when

- Adding an embedded admin, health or REST endpoint to a C++ program where one header with no required dependencies matters more than requests per second.
- Tools and tests that need both an HTTP client and an HTTPS server from one small library, with a choice of OpenSSL, Mbed TLS or wolfSSL.
- Low to moderate concurrency (tens of clients) on 64-bit Linux, macOS or Windows 10+, where thread-per-connection costs little.
- Replacing cpprestsdk in a small service that has fewer worker threads than clients; in the 2020 shootout cpprestsdk deadlocked in all six C=4 cells while cpp-httplib finished.

## Skip it when

- High-throughput or many-idle-connection servers: blocking I/O ties up one thread per connection, and in the 2020 shootout it was slower than Crow, Pistache, Restbed and Restinio in the local sprint cell and worst in 7 of 12 cells.
- High-latency links: over the shootout's VPN its per-request overhead was about twice that of the other frameworks (210 s vs about 105 s per 1000 requests), and it trailed cpprestsdk in every VPN C=28 cell.
- Anything needing HTTP/2 or HTTP/3 (not implemented), WebSocket compression (permessage-deflate not supported) or many concurrent WebSocket clients (one thread per connection plus one per heartbeat).
- 32-bit targets, MinGW, Cygwin/MSYS2 or Windows 8 and older: the README says these are unsupported, and security reports that only affect 32-bit builds are closed without action.
- Internet-facing services that cannot be upgraded often: the repository lists 23 security advisories, 10 of them published between March and October 2026, including request smuggling, CRLF injection and leaking cookies or credentials on cross-origin redirects.

## How it is fast

It is not built for speed: each accepted connection is handed to a thread pool (8 or hardware_concurrency()-1 base threads, growing to 4x under load) and served with blocking reads and writes. There is no event loop, io_uring or HTTP/2 multiplexing. The one measured edge over C++ REST SDK comes from lower per-request overhead on a fast local link; current code also puts small bodies (under 16 KiB) in the same write as the headers.

## Compared with alternatives

Pick it over Crow, Drogon, aeronet or Sogou Workflow when integration effort dominates: it is one header that also gives you an HTTPS client, and it needs no Boost, event loop or build system. For throughput, any of those (or httpserver.h for a minimal C server) is the better choice. cofetch reports 35% more single-thread throughput than cpp-httplib's own sync client.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required; optional OpenSSL 3.0+ / Mbed TLS 2.x-4.x / wolfSSL 5.x for TLS, zlib, Brotli and zstd for compression; pthreads |
| **Minimum toolchain** | C++11 (BoringSSL needs C++14); g++ 4.9+ (4.8 has broken &lt;regex&gt;); latest Visual Studio only |
| **Platforms** | 64-bit Linux, macOS, Windows 10+; 32-bit, MinGW and Cygwin unsupported |
| **Thread safety** | The server runs handlers concurrently on its thread pool, so shared state in handlers needs its own locking; the README marks the static-file mount methods as not thread-safe. Client thread safety is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- TCP_NODELAY is off by default (CPPHTTPLIB_TCP_NODELAY false). Issue #2264 measured about 82 ms per keep-alive POST with an httplib client and server, fixed by set_tcp_nodelay(true) on both sides. Set it for any request/response latency test.
- Shootout harness flaw: the tested v0.5.8 header (vendored at basic-httplib/httplib/httplib.h) wrote response headers and body in two separate send() calls and had no TCP_NODELAY option. With Nagle's algorithm, the second send can wait one round trip for an ACK. This likely explains, but does not prove, its doubled VPN overhead. Current headers coalesce bodies under 16 KiB into one write.
- The shootout's 'C=28' cpp-httplib build actually ran hardware_concurrency()-1 = 27 pool threads (the v0.5.8 default), while its log line printed 28. The C=4 build needs CPPHTTPLIB_THREAD_POOL_COUNT uncommented and a recompile; the published main.cpp leaves it commented out. v0.5.8 also used a listen backlog of 5 (now 128).
- SO_REUSEPORT is set by default on Linux and macOS, so a second server binding the same port succeeds silently and the kernel splits connections between them. Regex routes are skipped for paths longer than 256 characters to avoid std::regex stack overflow.

## Known shortcomings

- Downgraded B to C: not faster than C++ REST SDK overall in guteksan/REST-CPP-benchmark (130 stars, 17 commits, May-June 2020, v0.5.8, compiler unstated, numbers only in a table image, the repo's own ab.sh warns of +/-20% noise). Wins 1 of 6 completed cells (Local N=1000 t=0 C=28: 3.015 vs 3.401 s, 1.13x, single run), loses or ties the other 5 (VPN 3:31.510 vs 1:52.476, 1.88x slower), worst framework in 7 of 12 cells; the C=4 'wins' exist only because the SDK deadlocks. The README's 'followed by Httplib' means second-worst. MIT, active.
- Enricher: the tested v0.5.8 sent headers and body in two separate send() calls with no TCP_NODELAY option (likely cause of the doubled VPN overhead; current v0.60.1 merges bodies under 16 KiB into one write); the 'C=28' build ran 27 threads (hardware_concurrency()-1) while the log printed 28; listen backlog was 5; TCP_NODELAY is still off by default (issue #2264 measured about 82 ms per keep-alive POST, fixed by set_tcp_nodelay(true)). 23 GitHub advisories, 10 in 2026 (request smuggling, CRLF injection, cookie leak on cross-origin redirect); blocking I/O; HTTP/1.1 only; no 32-bit.

## Caveats and trade-offs

Weak and mostly unfavourable evidence. cpp-httplib's authors make no speed claim; the repo's benchmark/ directory builds a Crow v1.3.1 server beside cpp-httplib (Makefile bench-all, bombardier -c 10 -d 5s, -O2, CPPHTTPLIB_THREAD_POOL_COUNT=16) but publishes no numbers, and benchmark/ab.sh compares two cpp-httplib git refs, not another library; ab.sh itself warns that the same binary varies by +/-20% run to run, which covers the single 1.13x cell below. The only numbers found are third-party, from a small 2020 shootout (130 stars, all 17 commits in May-June 2020) testing cpp-httplib v0.5.8 and C++ REST SDK v2.10.15, both far older than the current v0.60.0 (released 2026-10-07). The win over C++ REST SDK holds in one cell only (Local, N=1000, t=0 ms, C=28: 3.015 s vs 3.401 s); in the matching VPN cell cpp-httplib is 1.88x slower (3:31.510 vs 1:52.476), it ties or trails in the Local t=200 ms cells and trails in every VPN C=28 cell; in the C=4 cells it 'wins' only because C++ REST SDK deadlocks when threads are fewer than producers. It is slower than Crow, Pistache, Restbed and Restinio in the sprint cell and is marked worst in 7 of 12 cells; the shootout's analysis singles out its doubled VPN overhead (210 s per 1000 requests) and its large degradation at C=4. The shootout README's phrase that Restinio was over 3 times faster than 'the worst Cpp-REST-SDK followed by Httplib' ranks Httplib second-worst, which matches the table. Harness: Python client opening a new connection per request, server-side logging through log4cplus twice per request, about 10,000 requests per cell, a single run per cell with no repeats or variance; faster frameworks finish the same load in about 1 s, so the 3 s figures are server-bound rather than client-capped. The published basic-httplib/main.cpp leaves CPPHTTPLIB_THREAD_POOL_COUNT commented out, so the C=4 runs needed a recompile not in the repo. Numbers exist only as a table image; compiler and version not stated. The guessed baseline (OpenSSL) and category (tls) were wrong; the repo is an HTTP server and client library and was refiled under http-servers-frameworks.

Single-header, blocking socket I/O with a thread pool only; HTTP/1.1 only (no HTTP/2 or HTTP/3); 32-bit platforms not supported. Easiest integration of the six frameworks compared, but no event loop, so many idle connections cost threads.

## Maintenance

Very active (eight commits on 2026-10-09, header at v0.60.1, 16.9k stars, MIT) and trivially vendorable, but security fixes land often, so track releases rather than pinning an old copy; the 2020 performance data describe v0.5.8, which predates write coalescing and the dynamic thread pool.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The only numbers are an independent but obscure single-run 2020 shootout (guteksan/REST-CPP-benchmark, 130 stars, 17 commits, compiler unstated) whose results table image shows cpp-httplib beating C++ REST SDK in just one of the six cells where both completed (Local N=1000 t=0 C=28, 3.015 s vs 3.401 s, 1.13x) and losing or tying in the other five (up to 1.88x slower over VPN), so it does not show the win B requires; public code, CPU model and CMake Release flags are present but the compiler is not, so not A.
- **Verifier notes:** Real, very popular library (16.9k stars, MIT, active, v0.60.0 on 2026-10-07) but not shown faster than its baseline: of six completed comparisons against C++ REST SDK it wins one by 1.13x (single run, within its own repo's stated +/-20% noise), ties two and loses three (up to 1.88x slower), and it is the worst of six frameworks in 7 of 12 cells. Record shortcomings: not faster except one cell, obscure single-run 2020 shootout on v0.5.8, compiler unstated, baseline wins in C=4 cells only by deadlocking; the record's own caveats misread the VPN cell as the win and misread the README's 'followed by Httplib' wording, both fixed in the corrected caveats.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/images/rest_all.PNG>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-httplib/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-httplib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/postInLoop.py>
  - <https://github.com/guteksan/REST-CPP-benchmark>
  - <https://github.com/guteksan/REST-CPP-benchmark/commits>
  - <https://github.com/yhirose/cpp-httplib>
  - <https://github.com/yhirose/cpp-httplib/commits>
  - <https://github.com/yhirose/cpp-httplib/tree/master/benchmark>
  - <https://raw.githubusercontent.com/yhirose/cpp-httplib/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/yhirose/cpp-httplib/HEAD/benchmark/ab.sh>
- **Sources the enricher read:**
  - <https://github.com/yhirose/cpp-httplib>
  - <https://github.com/yhirose/cpp-httplib/commits/master>
  - <https://raw.githubusercontent.com/yhirose/cpp-httplib/HEAD/README.md>
  - <https://raw.githubusercontent.com/yhirose/cpp-httplib/HEAD/httplib.h>
  - <https://raw.githubusercontent.com/yhirose/cpp-httplib/HEAD/benchmark/Makefile>
  - <https://github.com/yhirose/cpp-httplib/security>
  - <https://github.com/yhirose/cpp-httplib/issues?q=is%3Aissue+performance>
  - <https://github.com/yhirose/cpp-httplib/issues/1180>
  - <https://github.com/yhirose/cpp-httplib/issues/2264>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/README.md>
  - <https://github.com/guteksan/REST-CPP-benchmark/tree/master/basic-httplib>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-httplib/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-httplib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-httplib/httplib/httplib.h>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/postInLoop.py>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/yhirose/cpp-httplib`) · [data/wave5/enrich/raw/github_com_yhirose_cpp_httplib.json](../../../data/wave5/enrich/raw/github_com_yhirose_cpp_httplib.json) (enrichment confidence 0.75)

</details>
