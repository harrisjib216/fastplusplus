# Cutelyst

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Qt 6 web framework with its own epoll HTTP/1.1, HTTP/2 and FastCGI server; edges Drogon on HttpArena, trails nginx and actix-web.

| | |
|---|---|
| **Beats** | Drogon (C++ web framework, HttpArena's maintainer-written Drogon entry); the same results directory also holds Express, Flask and Django rows, and the listed incumbents nginx and actix-web, which beat Cutelyst on baseline-4096 and json-tls-4096 |
| **Claimed result** | Against Drogon on HttpArena (all ratios derived from page data): baseline-4096 2,153,860 vs 2,022,710 req/s (1.06x); limited-conn-4096 1,736,401 vs 1,694,883 (1.02x); json-tls-4096 326,846 vs 253,055 (1.29x); pipelined-4096 (reference-only profile) 10,167,331 vs 7,801,404 (1.30x); async-32000 761,563 vs 143,001 (5.3x, but the Drogon entry runs every delay timer on its single main loop, so this row measures the entry, not Drogon). Against slower stacks on baseline-4096: Express 525,879 (4.1x), Flask 77,319 (27.9x), Django 29,206 (73.7x). The category's listed incumbents on the same board are faster: baseline-4096 nginx 3,284,513 and actix 2,775,120 req/s (Cutelyst 0.66x and 0.78x), json-tls-4096 nginx 1,313,755 and actix 1,157,219 (Cutelyst 0.25x and 0.28x), async-32000 actix 2,112,168 (0.36x); Cutelyst beats actix only on limited-conn-4096 (1,736,401 vs 1,135,157, 1.53x) and beats nginx only on pipelined-4096 (10,167,331 vs 4,037,345, 2.5x). |
| **Workload** | HttpArena HTTP/1.1 profiles, each the best of three 5 s runs (scripts/benchmark.sh) with the gcannon load generator: baseline (mixed GET/POST /baseline11 summing query parameters and body, 4096 connections), limited-conn (same, connections closed after 10 requests), pipelined (16x pipelining, reference-only and excluded from the composite score), json-tls (JSON serialization over HTTP/1.1 TLS, 4096 connections) and async (GET /delay/10, a flat 10 ms timer over 32,000 held connections, ceiling 3.2M req/s). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX 64-Cores (128 threads), 251 GiB RAM, Ubuntu 24.04.4 host, kernel 6.17.0-22, Docker 29.3.0 (runc), performance governor (site/data/current.json); per scripts/lib/profiles.sh the server container is pinned to cpuset 0-31,64-95 (32 physical cores plus SMT siblings) and the load generator runs on the remaining CPUs of the same machine. |
| **Compiler and flags** | Cutelyst: g++ from the ubuntu:26.04 image (version not stated), C++23, CMAKE_BUILD_TYPE=Release with no extra flags, Ninja; Cutelyst built from upstream commit 5ec5ce95d80a87b38ea45a326945bb22e515a23a (its libraries overlaid on the v5.1.0 .deb in the runtime image), Qt 6 from Ubuntu, Cutelee v6.2.0, ASql commit eebafdde (frameworks/cutelyst/Dockerfile and CMakeLists.txt in MDA2AV/HttpArena). Drogon: built on the unpinned drogonframework/drogon:latest image (per drogon's docker/ubuntu/Dockerfile: Ubuntu 22.04, g++-11, Drogon master at image build time built by build.sh with CMAKE_BUILD_TYPE=release), app built with CMake Release, C++20, and libjemalloc preloaded (frameworks/drogon/Dockerfile). |
| **Adoption** | 977 stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/cutelyst/cutelyst) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/cutelyst.json) |

## Verdict

On HttpArena (AMD Threadripper PRO 3995WX, server container pinned to 32 cores plus SMT siblings, gcannon load generator on the remaining CPUs, best of three 5 s runs), Cutelyst built from upstream commit 5ec5ce9 with Ubuntu 26.04's g++ in Release mode served 2,153,860 req/s on baseline-4096 vs Drogon's 2,022,710 (1.06x), 1.02x on limited-conn, 1.29x on json-tls and 1.30x on the reference-only pipelined profile; Drogon's rows are a month older and built with g++-11 on an unpinned image, and the 5.3x async row reflects the Drogon entry running all timers on one loop. nginx and actix-web on the same board are faster on the main profiles.

## Use it when

- You already build on Qt 6 (QString, QJsonDocument, Qt SQL or ASql) and want a web backend in the same stack with throughput in the same class as Drogon (2.15M vs 2.02M req/s on HttpArena baseline-4096).
- Many idle or slow keep-alive connections served by async handlers on Linux: per-worker timers held 761,563 req/s over 32,000 connections with a 10 ms delay.
- Pipelined HTTP/1.1 clients: 10.17M req/s on HttpArena's 16-deep pipelined profile, above Drogon (7.80M) and nginx (4.04M).
- Apps that want Catalyst-style chained dispatch, sessions, auth and templates in one BSD-3-Clause package, deployed directly or behind a front proxy via FastCGI.

## Skip it when

- Maximum raw throughput: on the same HttpArena board nginx (3.28M) and actix-web (2.78M req/s) beat Cutelyst's 2.15M on baseline-4096, and on json-tls-4096 nginx, h2o and actix serve 3.5-4x more (1.31M, 1.23M, 1.16M vs 326,846); even Express is ahead there (394,866).
- TLS JSON APIs that care about tail latency: Cutelyst's json-tls-4096 p99 was 478 ms against Drogon's 117 ms, despite higher mean throughput.
- Fixed-rate, latency-sensitive serving at moderate load: Drogon had lower mean latency and CPU at 1M req/s (108.1 us, 3551.7% vs 137.6 us, 3825.6%) and served more on latency-500k-8cpu (374,962 vs 329,347 req/s).
- Projects that cannot take a Qt 6 runtime dependency or a C++23 compiler (README asks for g++-14 or newer; Clang builds are forced onto libc++).
- Database-backed pages if you rely on HttpArena for evidence: its async-db and fortunes rows (384 req/s) measure a misconfigured entry, so Cutelyst's DB performance is unmeasured rather than shown to be good or bad.

## How it is fast

On Linux it replaces Qt's default event dispatcher with its own epoll-based one (EventLoopEPoll, using eventfd and timerfd) and runs one event loop per core, each with its own Application instance and, with reuse_port, its own SO_REUSEPORT listener so the kernel spreads connections without a shared accept lock. The HTTP/1.1 parser works in a fixed per-connection buffer, finds line ends with memchr and compacts pipelined requests with memmove, so the hot path avoids per-request allocations for the request head. Async handlers (ASync, QTimer, coroutines) hand responses back on the worker's own loop, which is why its 32,000-connection delay test scales across all cores.

## Compared with alternatives

Against Drogon, its closest C++ sibling, throughput is within 2-6% on HttpArena's scored HTTP/1.1 profiles, so pick Cutelyst when your code is already Qt and you want Catalyst-style dispatch, HTTP/2 and FastCGI in one engine, and Drogon when you want no Qt dependency. For maximum req/s look at h2o, Sogou Workflow or Lithium instead, and for a small embeddable server Crow or cpp-httplib.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Qt 6.5+ (Core, Network; Sql and LinguistTools at build time), CMake 3.28+; optional Cutelee (templates), ASql (async PostgreSQL/MySQL/SQLite), libmemcached, libpwquality |
| **Minimum toolchain** | C++23 (README: g++-14 or newer); CMake 3.28; Clang builds add -stdlib=libc++ for coroutines |
| **Platforms** | Linux (custom epoll event loop, SO_REUSEPORT, process forking), plus other Qt platforms including Windows (recent Windows server fixes); 'cross-platform' per README |
| **Thread safety** | Server creates one Application (and controller set) per worker thread when the app constructor is Q_INVOKABLE and threads &gt; 1; each thread runs its own event loop, so state shared across threads is the user's responsibility. README warns that local QEventLoops in async code will eventually crash. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind HttpArena's database rows: the entry (frameworks/cutelyst/app.cpp) gives each worker thread an ASql pool of min(240, DATABASE_MAX_CONN)/idealThreadCount connections (3 per thread with 64 threads) and calls enterPipelineMode(500 ms), which in ASql's Postgres driver arms a single-shot timer that sends PQpipelineSync only every 500 ms. Each pooled connection therefore completes one query per sync tick: 64 x 3 x 2/s = 384 req/s, exactly the async-db-1024 and fortunes-1024 results (fortunes: 1,920 responses in 5 s = 192 connections x 10 ticks), with 2.0-2.3 s mean latency from 1,024 clients queueing for 192 connections (derived from page data and source). Those rows measure the entry's sync timer, not Cutelyst or ASql.
- The benchmarked server is not a release: HttpArena builds upstream commit 5ec5ce9 (2026-09-11, 'Add http chunked for HttpArena benchmarks', +171 lines in protocolhttp.cpp), which added Transfer-Encoding: chunked request-body parsing for the first time. The latest tag v5.1.0 and its Ubuntu .deb (the entry's runtime base before the overlay) cannot parse chunked request bodies.
- The whole request head must fit in buffer_size (default 4096 bytes). When the buffer fills, protocolhttp.cpp reaches an empty block commented '414 Request-URI Too Long' and sends nothing, so requests with large cookies or bearer tokens appear to hang (read from source, not tested); raise buffer_size (the HttpArena entry uses 128 KiB).
- Robustness history: issue #379 (closed December 2022) reported a malformed HTTP/1.0 POST whose body was longer than its Content-Length making the whole server unresponsive until kill -9; issue #146 (Ctrl+C abort crash) and #214 (SIGTERM handling) are still open.

## Known shortcomings

- Tier A kept, claim downgraded: the async 5.3x over Drogon is not valid evidence because the HttpArena Drogon entry runs every delay timer on the app().getLoop() main loop (812% CPU), so that row measures the entry, not Drogon. Category incumbents on the same board beat Cutelyst: baseline-4096 nginx 3,284,513 and actix 2,775,120 vs 2,153,860 req/s; json-tls nginx 1,313,755 and actix 1,157,219 vs 326,846; async actix 2,112,168. Wins only limited-conn vs actix (1.53x) and pipelined vs nginx (reference-only profile); 1.02-1.06x over Drogon on scored profiles. Drogon rows saved 2026-09-06 on an unpinned drogon:latest image with g++-11, Cutelyst rows 2026-10-06; async-db and fortunes stall at 384 req/s; the entry was written by the Cutelyst author on a commit made for the benchmark; harness takes best of three.
- Enricher (orphaned file): the HttpArena entry (frameworks/cutelyst/app.cpp) gives each worker thread min(240, DATABASE_MAX_CONN)/idealThreadCount ASql connections (3 per thread with 64 threads) and calls enterPipelineMode(500 ms), whose Postgres driver sends PQpipelineSync only every 500 ms, so each pooled connection completes one query per tick: 64 x 3 x 2/s = 384 req/s, exactly the async-db-1024 and fortunes-1024 results (database rows invalid). The benchmarked server is unreleased master commit 5ec5ce9 (2026-09-11, 'Add http chunked for HttpArena benchmarks'), which added chunked request-body parsing; the latest tag v5.1.0 cannot parse chunked bodies. The whole request head must fit buffer_size (default 4096 bytes) or the server sends nothing (the entry uses 128 KiB). Issue #379 (closed 2022) had an over-long POST body hang the whole server; #146 and #214 (signal handling) still open.

## Caveats and trade-offs

Margins over Drogon on the scored throughput profiles are small (1.06x baseline, 1.02x limited-conn) from best-of-three 5 s runs with no variance reported. The async 5.3x row is not evidence about Drogon: HttpArena's Drogon entry (frameworks/drogon/main.cc) schedules each delay with app().getLoop()-&gt;runAfter, the main event loop, so all 32,000 timers fire on one thread (Drogon CPU 812% vs Cutelyst 6172%), while Cutelyst's entry uses a per-worker QTimer. Pipelined is a reference-only profile. The runs are weeks apart: all Cutelyst rows were saved on 2026-10-06 (PR #1520), Drogon's rows were last saved on 2026-09-06 (PRs #1455 and #1460) on an unpinned drogon:latest image built with g++-11, so compiler generation and harness state differ between the two rows. The category's listed incumbents on the same board are faster: nginx 3,284,513 and actix 2,775,120 req/s vs Cutelyst 2,153,860 on baseline-4096; nginx 1,313,755, h2o 1,229,462 and actix 1,157,219 vs 326,846 on json-tls-4096; actix 2,112,168 vs 761,563 on async-32000; nginx 2,626,297 vs 1,736,401 on limited-conn-4096. Drogon beats Cutelyst on latency-500k-8cpu (374,962 vs 329,347 req/s), on mean latency and CPU in latency-1m (108.1 us vs 137.6 us, 3551.7% vs 3825.6%) and in 8gbit-512 (102.5 us vs 120.5 us, 304.0% vs 342.7%). Express beats Cutelyst on json-tls-4096 (394,866 vs 326,846 req/s). Cutelyst's database profiles are very weak: async-db-1024 and fortunes-1024 both reached 384 req/s with 2.0-2.3 s mean latency and 22-43% CPU (Express 173,099 and 58,855), which looks like a stall in its per-thread ASql pool (about 3 connections per worker thread), so Cutelyst does not win on database or template workloads. The entry was written by Cutelyst's own author (meta.json maintainers: dantti, PRs #1479 and #1520), and its Dockerfile pins an upstream commit (2026-09-11, 'Add http chunked for HttpArena benchmarks') that adds chunked request bodies for this benchmark. The live leaderboard (www.http-arena.com) is blocked here and rankings may have changed. The Cutelyst README links HttpArena and historical TechEmpower Round 23 results but quotes no numbers.

Full-stack Qt-based framework: needs Qt 6 and the Qt event loop, uses QJsonDocument and QString throughout, so footprint and API are tied to Qt. Catalyst-style controllers and routing, HTTP/1.1, HTTP/2, FastCGI and WebSockets in one engine (Cutelyst::Server).

## Maintenance

Actively maintained (last commit 2026-09-11, latest tag v5.1.0) and BSD-3-Clause, so copyable, but the HttpArena numbers come from an unreleased master commit written for the benchmark by Cutelyst's own author, and its database rows are invalid because the entry's 500 ms pipeline auto-sync caps them at 384 req/s.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/cutelyst.json and the sibling drogon/express/flask/django.json files in MDA2AV/HttpArena; the benchmark code is public (frameworks/cutelyst/{Dockerfile,CMakeLists.txt,main.cpp,root.cpp,app.cpp}, frameworks/drogon/{Dockerfile,main.cc}, scripts/benchmark.sh, scripts/lib/profiles.sh), both entries build with CMake Release, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json, so tier A holds as for wtx on the same harness. The verdict is a downgrade of the claim, not of the tier: the async 5.3x row is an artifact of the Drogon entry's code, and the category's listed incumbents on the same board (nginx, actix-web) beat Cutelyst on the main profiles.
- **Verifier notes:** Numbers and ratios versus Drogon, Express, Flask and Django are exact, and license (BSD-3-Clause), 977 stars, last commit 2026-09-11 (not a fork, not archived) are confirmed, so tier A stays; the claim is downgraded because the async 5.3x win comes from the Drogon entry scheduling every timer on its main loop, Drogon's rows are a month older and built on an unpinned g++-11 image, and the category's listed incumbents nginx and actix-web on the same board beat Cutelyst on baseline-4096, json-tls-4096 and async. Record shortcomings: not faster than nginx or actix-web; only 1.02-1.06x over Drogon on scored throughput profiles; database and template profiles stall at 384 req/s; entry written by Cutelyst's author with a benchmark-specific upstream commit. The record's 'single 5 s runs' was corrected to best of three 5 s runs.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/express.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/flask.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/django.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/actix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/main.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/root.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/app.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/drogonframework/drogon/master/docker/ubuntu/Dockerfile>
  - <https://raw.githubusercontent.com/drogonframework/drogon/master/build.sh>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/cutelyst.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/drogon.json>
  - <https://github.com/MDA2AV/HttpArena/pull/1520>
  - <https://github.com/cutelyst/cutelyst>
  - <https://github.com/cutelyst/cutelyst/commits>
- **Sources the enricher read:**
  - <https://github.com/cutelyst/cutelyst>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/README.md>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/CMakeLists.txt>
  - <https://github.com/cutelyst/cutelyst/tree/master/Cutelyst/Server>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/protocolhttp.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/server.h>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/server.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/serverengine.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/tcpserverbalancer.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/Cutelyst/Server/tcpsslserver.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/EventLoopEPoll/eventdispatcher_epoll.cpp>
  - <https://raw.githubusercontent.com/cutelyst/cutelyst/HEAD/EventLoopEPoll/eventdispatcher_epoll_p.cpp>
  - <https://github.com/cutelyst/cutelyst/commits>
  - <https://github.com/cutelyst/cutelyst/commit/5ec5ce95d80a87b38ea45a326945bb22e515a23a>
  - <https://github.com/cutelyst/cutelyst/releases>
  - <https://github.com/cutelyst/cutelyst/releases/tag/v5.1.0>
  - <https://github.com/cutelyst/cutelyst/issues?q=is%3Aissue+crash+OR+leak+OR+performance+OR+security>
  - <https://github.com/cutelyst/cutelyst/issues/379>
  - <https://raw.githubusercontent.com/cutelyst/asql/eebafdde3069008626a558b15ae641ab356c799b/README.md>
  - <https://raw.githubusercontent.com/cutelyst/asql/eebafdde3069008626a558b15ae641ab356c799b/src/adatabase.h>
  - <https://raw.githubusercontent.com/cutelyst/asql/eebafdde3069008626a558b15ae641ab356c799b/src/adatabase.cpp>
  - <https://raw.githubusercontent.com/cutelyst/asql/eebafdde3069008626a558b15ae641ab356c799b/src/adriverpg.cpp>
  - <https://raw.githubusercontent.com/cutelyst/asql/eebafdde3069008626a558b15ae641ab356c799b/src/apool.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/main.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/app.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/app.h>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/root.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/cutelyst/root.h>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/scripts/lib/profiles.sh>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cutelyst/cutelyst`) · [data/wave5/enrich/raw/github_com_cutelyst_cutelyst.json](../../../data/wave5/enrich/raw/github_com_cutelyst_cutelyst.json) (enrichment confidence 0.8)

</details>
