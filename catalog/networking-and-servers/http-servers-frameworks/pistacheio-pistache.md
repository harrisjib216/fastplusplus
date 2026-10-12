# Pistache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++17 HTTP/1.1 REST server library; in a 2020 shootout it beat C++ REST SDK by 3.2x and Restbed by 1.26x on small POSTs.

| | |
|---|---|
| **Beats** | C++ REST SDK (cpprestsdk) v2.10.15, also Restbed v4.6 |
| **Claimed result** | From guteksan/REST-CPP-benchmark images/rest_all.PNG. Local, N=1000, t=0 ms: C=28 Pistache v0.0.002 1.059 s vs C++ REST SDK 3.401 s (3.21x faster, derived from page data) and Restbed 1.333 s (1.26x, derived from page data); C=4 Pistache 0.964 s vs Restbed 1.789 s (1.86x, derived from page data), C++ REST SDK deadlocked. Restinio (1.025 s, 0.85 s) is faster than Pistache in both cells. With 200 ms handling time Pistache ties at C=28 but is the slowest or second slowest at C=4 (Local N=1000 8:34.710 vs Restbed 8:21.744; VPN N=1000 10:19.625 vs Restbed 8:23.877). Secondary 2017 source (binaryspaceship/cpp-rest-frameworks-benchmark, ab -n 1000 -c 1 -k, 608,891-byte JSON response): Pistache 319.99 req/s vs Restbed 224.18, cpprestsdk with RapidJSON 47.06 and cpprestsdk default JSON 30.70 (1.43x, 6.8x and 10.4x, derived from page data). |
| **Workload** | Independent shootout (guteksan/REST-CPP-benchmark, 2020): six equivalent services (POST /test echoes the body, log4cplus logs each request and reply, optional sleep t) driven by 10 Python producer processes (postInLoop.py, http.client, a new TCP connection per request), each sending N=200 or 1000 requests; service thread pool C=28 or C=4; Local or VPN; metric is time from the service's first logged request to its last reply, one run per cell. |
| **Metric** | throughput |
| **Hardware** | 28x Intel Xeon CPU E5-2660 v4 @ 2.0 GHz, 64 GB RAM, Ubuntu 16.04.3 LTS (guteksan benchmark); the 2017 source states no host CPU (Vagrant VM, CPU count unset in the Vagrantfile). |
| **Compiler and flags** | Not stated; services built with cmake -DCMAKE_BUILD_TYPE=Release, Pistache linked as a separately built static library (flags not stated). In the 2017 source, bootstrap.sh builds RapidJSON, Pistache, Restbed and every sample with cmake -DCMAKE_BUILD_TYPE=Release in an Ubuntu 16.04 Vagrant box and installs cpprestsdk from the libcpprest-dev package; compiler version not stated. |
| **Adoption** | 3.5k stars |
| **Last commit** | 2026-07-11 |
| **Links** | [repository](https://github.com/pistacheio/pistache) · [benchmark](https://github.com/guteksan/REST-CPP-benchmark) |

## Verdict

guteksan/REST-CPP-benchmark (2020, linked from Pistache's README) ran equivalent POST-echo services on a 28-thread Xeon E5-2660 v4 with Ubuntu 16.04 (CMake Release, compiler not stated), driven by 10 Python clients with 1000 requests each and a new connection per request. Pistache v0.0.002 took 1.059 s vs C++ REST SDK 2.10.15's 3.401 s and Restbed 4.6's 1.333 s at 28 server threads, and 0.964 s vs Restbed's 1.789 s at 4 threads (cpprestsdk deadlocked); RESTinio was faster in both cells, and with 200 ms handlers Pistache tied or trailed. A 2017 ab test (one connection, 608 KB JSON) also favours Pistache, but it handicaps both baselines.

## Use it when

- A small or medium REST service on Linux where you want a simple handler and router API without Boost.Asio, and you can install a library (Debian 12 and Ubuntu 23.10 ship libpistache-dev, and Launchpad PPAs carry daily and stable builds).
- Short, CPU-light handlers with modest per-request work, which is where it beat cpprestsdk (3.2x) and Restbed (1.26x to 1.86x) in the guteksan shootout.
- Replacing cpprestsdk's http_listener, which deadlocked at 4 server threads with 10 clients in the same shootout and is itself in maintenance mode.
- You need an Apache-2.0 library (Restbed, the other baseline, is AGPL or commercial).
- Plain-HTTP services behind a TLS-terminating proxy, which sidesteps Pistache's single-threaded TLS handshake.

## Skip it when

- Maximum throughput: RESTinio was faster than Pistache in both no-delay cells of the same shootout, and in issue #994 Go net/http served 96,422 req/s vs Pistache's 16,578 with hey at 100 connections (55,138 vs 58,194 with ab -k), with Pistache's thread count making no difference.
- TLS-terminating servers under load: SSL_accept runs on the single listener thread, and issue #1312 (open, PR #1313 unmerged) measured about 24,792 ops/s plaintext vs about 1,004 with TLS at 20 worker threads.
- Handlers that block (database calls, sleeps): they run on the reactor thread, and connections are pinned to a worker by fd number with no work stealing, so other connections on that worker stall. In the shootout Pistache was the slowest or second slowest at C=4 with 200 ms handlers (Local N=1000 8:34.710 vs Restbed 8:21.744; VPN 10:19.625 vs about 8:23).
- Clients that pipeline HTTP/1.1 requests, large uploads, HTTP/2, or a stable ABI: pipelining is not supported, the default maxRequestSize is 4 KiB, there is no HTTP/2, and the project is pre-1.0 with the soname following feature releases.
- You need a reliable HTTP client: the README says the client 'has a few issues in it that make it buggy'.

## How it is fast

One listener thread accepts sockets and hands each one to one of N worker reactors, picked by fd modulo N on POSIX (an atomic counter on Windows). Each worker runs its own epoll loop on Linux (libevent on macOS, BSD and Windows) in edge-triggered mode, reads in 4 KiB chunks and calls the handler inline on that thread, so a request takes no cross-thread hand-off. Requests are parsed by an incremental step parser (request line, headers, body including chunked encoding) over a per-connection buffer, and routes are matched in a segment tree of string_view-keyed hash maps. Responses go through a per-worker write queue polled by the same reactor, files are sent with sendfile, and header, body and keep-alive timeouts use timerfd.

## Compared with alternatives

Pick Pistache over RESTinio (faster in the same shootout, header-only on Asio) or cpp-httplib (header-only, thread per connection, 3.0 s vs Pistache's 1.06 s in that shootout) when you want an Apache-2.0, distro-packaged library with a simple handler and router API and no Boost dependency. For raw throughput, TLS or pipelining clients, Drogon and Crow have stronger evidence (both beat Go net/http on the-benchmarker or TechEmpower code).

## Integration

| | |
|---|---|
| **Form** | shared lib (static archive also built; Meson subproject fallback supported) |
| **Dependencies** | pthreads; Howard Hinnant date (system or Meson fallback); RapidJSON (option PISTACHE_USE_RAPIDJSON, default on); optional OpenSSL (TLS), brotli, zstd, zlib (content encoding); libevent and libevent_pthreads on macOS, BSD and Windows (or with PISTACHE_FORCE_LIBEVENT); libatomic where 64-bit atomics need it; googletest for tests |
| **Minimum toolchain** | C++17; Meson &gt;= 0.57 (primary build) or CMake &gt;= 3.11; GCC before 9.1 and Clang link stdc++fs or c++fs (issue #1068 workaround) |
| **Platforms** | Linux with native epoll (Debian builds for amd64, arm64, armhf, i386, ppc64el, riscv64, s390x); macOS, FreeBSD, OpenBSD, NetBSD and Windows through libevent |
| **Thread safety** | Each worker reactor is single-threaded and owns its connections. Http::Handler subclasses are cloned per worker through HTTP_PROTOTYPE's clone(), so handler member state is per thread, not shared; state shared by Router callbacks must be synchronized by the user. Sending on a ResponseStream from another thread raced until issue #1290 was closed in March 2025. |
| **Drop-in for the baseline** | no |

## Gotchas

- Defaults are small: Endpoint::options() starts with threads(1), and maxRequestSize defaults to 4,096 bytes for the whole buffered request (headers plus body), so larger POSTs get 413 until you raise it. With limits in the MiB range, issue #1190 (open, labelled security) reports oversized uploads taking 4.7 s to 145 s to be rejected at 100% CPU.
- No HTTP pipelining: after the first request in a read buffer is handled, parser-&gt;reset() discards the rest of the buffer, so pipelined requests are silently lost (issue #1034, open since 2022). Responses to HTTP/1.1 requests that carry no Connection header are sent with 'Connection: close' (Handler::onInput in src/common/http.cc), so clients that rely on implicit keep-alive, such as Go's net/http client behind hey, reconnect for every request. Our inference, not stated in the thread: this, plus the single accept thread, probably explains issue #994's 16.6k req/s under hey vs 55.1k under ab -k, where ab sends Connection: Keep-Alive.
- The benchmark behind the record is client-bound. guteksan's driver is 10 Python processes using http.client with a new TCP connection per request, each printing every request and reply under one shared multiprocessing lock. The service logs every request through log4cplus, and each cell is a single run. The top no-delay results (Restinio 1.025 s, Pistache 1.059 s for 10,000 requests) are therefore near the client's limit, and the run used Pistache v0.0.002 from 2020, not the current 0.5.x code with its libevent abstraction.
- Security: GHSA-q474-pqcp-gqm5 (moderate, published 2026-06-25) is a stack-exhaustion DoS from regex_replace on long slash runs in the REST router's path normalization, fixed on master on 2026-06-24 (version.txt now 0.5.16). Older distro packages may still carry it.

## Known shortcomings

- Upgraded C to B on the guteksan shootout linked from Pistache's README (1.059 s vs cpprestsdk 3.401 s, vs Restbed 1.333/1.789 s); RESTinio is faster still and Pistache trails at C=4 with 200 ms handlers; the 2017 binaryspaceship numbers match but that harness hurts both baselines (Restbed sample forces Connection: close, cpprestsdk main busy-spins); baselines not spec-listed.
- Enricher: the guteksan harness client is 10 Python processes opening a new TCP connection per request, printing under one shared lock, single run, Pistache v0.0.002 (2020), with the top no-delay cells near the client's limit. Handlers run on the reactor thread with connections pinned fd%N, so blocking handlers stall (explains the C=4 t=200ms loss); TLS SSL_accept runs on the single listener thread (#1312: 24,792 vs about 1,004 ops/s); no pipelining and parser-&gt;reset drops buffered requests (#1034); default maxRequestSize 4096; HTTP/1.1 requests without a Connection header get 'Connection: close', which likely explains #994 (hey 16.6k vs Go net/http 96.4k req/s; ab -k 55.1k vs 58.2k). GHSA-q474-pqcp-gqm5 router stack-exhaustion DoS fixed 2026-06-24.

## Caveats and trade-offs

Evidence is dated and modest. guteksan/REST-CPP-benchmark (130 stars, 2020, single run per cell, results only as a screenshot) uses Pistache v0.0.002 against C++ REST SDK v2.10.15 and Restbed v4.6; the Python client opens a new connection per request and prints every reply, so the sprint cells mostly measure connection and request-handling overhead. Pistache wins only the no-delay Local cells (where Restinio is faster still) and trails at C=4 when handlers block for 200 ms; the shootout's README says Restbed (at C=28) and Pistache (with limited threads) 'slightly fall behind' when requests need processing. The 2017 binaryspaceship benchmark (23 stars, commits 2017-06-18 to 2017-06-20, Pistache then at oktal/pistache) handicaps both baselines: the Restbed sample sets a default 'Connection: close' header and closes the session, so ab reports Keep-Alive requests: 0 for it, and the cpprestsdk sample ends main() with a busy-spinning while (true); loop in a VM whose CPU count is not set; the cpprestsdk-rapidjson run also shows Keep-Alive requests: 0 and a bimodal latency (median 4 ms, 66th percentile 40 ms). That source is one sequential connection, one run, read from ab screenshots, with no host CPU stated. The Pistache README makes no quantitative speed claim (the GitHub About line says 'high-performance'). Neither baseline is in the category list (nginx, Go net/http, Boost.Beast, actix-web, uvloop). [retier] Client-bound harness (Python, new connection per request, single run, v0.0.002); handlers run on reactor threads with connections pinned fd%N so blocking handlers stall; TLS accept on one listener thread (#1312); no pipelining (#1034); default maxRequestSize 4096; Go net/http counter-evidence in #994.

Pre-1.0 and described as unstable on its repo page; the HTTP client component has known issues; Linux, macOS, BSD and Windows support; no inline code documentation per the third-party reviewer.

## Maintenance

Actively maintained (last commit 2026-07-11, version 0.5.16, 3.5k stars, 202 open issues) and Apache-2.0. It is still pre-1.0: the soname follows feature releases, the API is only partly documented, and the TLS-handshake, pipelining and oversized-body issues above remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B on stronger evidence: the independent guteksan/REST-CPP-benchmark shootout, which the Pistache README itself links, shows Pistache beating C++ REST SDK and Restbed in the Local no-delay cells with equivalent public service code (basic-\*/main.cpp, postInLoop.py) and the CPU stated, but no compiler, so not A. The record's 2017 source (binaryspaceship/cpp-rest-frameworks-benchmark) has the numbers as quoted but its harness handicaps both baselines.
- **Verifier notes:** Both sources' numbers match their images exactly. Switched benchmark_url to the guteksan shootout (linked from the Pistache README, equivalent service code) and raised the tier to B, consistent with the RESTinio entry from the same shootout; the 2017 benchmark stays as secondary evidence with its baseline handicaps (Restbed forced Connection: close, cpprestsdk busy-spin main loop) recorded. baseline_in_list corrected to false (cpprestsdk is not a listed baseline).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 5); enricher w5 pair-032
- **Pages the verifier opened:**
  - <https://github.com/binaryspaceship/cpp-rest-frameworks-benchmark>
  - <https://github.com/binaryspaceship/cpp-rest-frameworks-benchmark/tree/master/results>
  - <https://github.com/binaryspaceship/cpp-rest-frameworks-benchmark/commits/master>
  - <https://github.com/binaryspaceship/cpp-rest-frameworks-benchmark/tree/master/samples>
  - <https://github.com/binaryspaceship/cpp-rest-frameworks-benchmark/tree/master/samples/cpp>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/bootstrap.sh>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/Vagrantfile>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/results/benchmark-pistache.png>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/results/benchmark-restbed.png>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/results/benchmark-cpprestsdk-rapidjson.png>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/results/benchmark-cpprestsdk-default_json_impl.png>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/samples/cpp/pistache/main.cpp>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/samples/cpp/restbed/main.cpp>
  - <https://raw.githubusercontent.com/binaryspaceship/cpp-rest-frameworks-benchmark/HEAD/samples/cpp/cpprestsdk-rapidjson/main.cpp>
  - <https://github.com/guteksan/REST-CPP-benchmark>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/images/rest_all.PNG>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-pistache/main.cpp>
  - <https://github.com/pistacheio/pistache>
  - <https://github.com/pistacheio/pistache/commits/master>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/pistacheio/pistache>
  - <https://github.com/pistacheio/pistache/commits/master>
  - <https://github.com/pistacheio/pistache/tree/master/src/common>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/README.md>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/meson.build>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/version.txt>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/common/reactor.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/common/transport.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/common/http.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/common/stream.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/server/listener.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/server/endpoint.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/src/server/router.cc>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/include/pistache/endpoint.h>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/include/pistache/stream.h>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/include/pistache/config.h>
  - <https://raw.githubusercontent.com/pistacheio/pistache/HEAD/include/pistache/http_defs.h>
  - <https://github.com/pistacheio/pistache/issues?q=is%3Aissue+performance>
  - <https://github.com/pistacheio/pistache/issues?q=is%3Aissue+pipelining>
  - <https://github.com/pistacheio/pistache/issues/1034>
  - <https://github.com/pistacheio/pistache/issues/1190>
  - <https://github.com/pistacheio/pistache/issues/1312>
  - <https://github.com/pistacheio/pistache/issues/994>
  - <https://github.com/pistacheio/pistache/security/advisories>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-pistache/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restbed/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/basic-restinio/main.cpp>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/postInLoop.py>
  - <https://raw.githubusercontent.com/guteksan/REST-CPP-benchmark/HEAD/images/rest_all.PNG>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/pistacheio/pistache`) · [data/wave5/enrich/raw/github_com_pistacheio_pistache.json](../../../data/wave5/enrich/raw/github_com_pistacheio_pistache.json) (enrichment confidence 0.75)

</details>
