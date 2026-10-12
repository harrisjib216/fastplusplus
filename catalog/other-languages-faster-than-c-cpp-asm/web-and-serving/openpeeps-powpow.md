# PowPow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim event-loop library with a built-in HTTP/1.1 server that out-served Drogon by 1.34-1.39x in one the-benchmarker snapshot.

| | |
|---|---|
| **Beats** | Drogon 1.9.13 (C++, trantor event loop; the-benchmarker cpp/drogon, cmake release build); also agoo-c 0.7 (C) in the same table |
| **Claimed result** | powpow 0.2 in data.json updated 2026-10-06: 237,033 / 248,309 / 238,538 req/s at 64 / 256 / 512 connections vs Drogon 177,005 / 178,341 / 171,358 (1.34x / 1.39x / 1.39x, derived from page data); vs agoo-c (C) 1.65x at 64, 1.16x at 256, 1.19x at 512, and vs cwist 3.9 (C, best C row at 64, 186,252) 1.27x (derived from page data). Per busy server core: powpow 106.6k / 116.5k / 112.4k vs Drogon 69.9k / 71.8k / 69.3k req/s (derived from total_requests_per_s / server_cpu_cores). The win appears in this one snapshot only: the 2026-10-02 snapshot (commit 8657397), after the suite's 2026-09-30 commit 4cce691 'ensure powpow is running multithreaded', has powpow at 100,905 / 93,959 / 91,689 req/s with 13% CPU saturation (0.56x / 0.53x / 0.53x Drogon), and the 2026-09-24 snapshot (commit f673364) has it on one core at 0.63x / 0.55x / 0.55x (derived from page data). README 'Dummy Benchmarks' (first-party, no baseline, wrk 4 threads / 100 connections / 5 s run via GitHub Actions, hardware not stated): 202,743 req/s multi-threaded (4 workers, SO_REUSEPORT) keep-alive and 97,965 req/s single-threaded keep-alive. |
| **Workload** | the-benchmarker/web-frameworks minimal HTTP contract (GET /, GET /user/:id, POST /user on port 3000), total_requests_per_s at 64, 256 and 512 connections, each framework in its own container. |
| **Metric** | throughput |
| **Hardware** | data.json hardware field (published 2026-10-06): cpu_name 'M1 Eight-Core Processor', cpus 16, memory 7,733,008 kB, Linux 7.2.7-200.fc44.x86_64 (Fedora). Per-run server_cpu_cores / server_cpu_saturation imply about 4 CPUs allotted to each server container (derived from page data). |
| **Compiler and flags** | Suite nim/Dockerfile: every Nim entry built with --passC:-flto --passL:-flto --assertions:off (nimlang/nim:2.2 on bookworm); -d:powpowPewPew is read only in powpow's own config.nims, which the suite's server.nim build does not use, so it is most likely a no-op. Drogon: plain cmake release without LTO on debian:trixie-slim. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Event loop built directly on epoll with one worker per core and SO_REUSEPORT (README, suite entry). |
| **Adoption** | 20 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/openpeeps/powpow) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json) |

## Verdict

In the independent the-benchmarker/web-frameworks suite (data.json, 2026-10-06; 3 trivial routes; 15 s runs at 64/256/512 keep-alive connections; each server in its own container with about 4 CPUs on a host reporting 'M1 Eight-Core Processor', 16 CPUs, Fedora x86_64 kernel), powpow 0.2 served 237,033 / 248,309 / 238,538 req/s. Drogon 1.9.13 (cmake release, no LTO) served 177,005 / 178,341 / 171,358, so powpow was 1.34-1.39x faster. The two earlier snapshots, run before or just after the server was made multi-threaded, had powpow at 0.53-0.63x Drogon. powpow was built by Nim 2.2 with -O3-level speed options plus LTO.

## Use it when

- You write services in Nim and want one event-loop package that covers HTTP/1.1, WebSocket, TLS, UDP and raw TCP, not std/asynchttpserver.
- Keep-alive HTTP/1.1 APIs with tiny responses on Linux, where you want most of the box's req/s from a few cores (in this table it served about 107-117k req/s per busy core, against about 70k for Drogon).
- Prototyping or internal services where you control the clients and can accept a pre-1.0 library.
- Zero-copy static file or media serving (sendfile, Range and conditional requests built in; optional kTLS and io_uring SPLICE paths).

## Skip it when

- Anything public-facing that needs a vetted server: the README says it is not production-ready and may contain bugs and security vulnerabilities, and a use-after-free in the event loop was fixed as recently as 2026-09-30.
- If tail latency matters: in the same snapshot powpow's p99 was 7.6 / 15.9 / 21.3 ms at 64 / 256 / 512 connections, while cwist (C) was at 0.50 / 1.84 / 3.68 ms and agoo-c (C) at 1.18 / 7.7 / 11.5 ms (from data.json). The win is in throughput only.
- If you need routing, middleware or a C/C++ API: it is a Nim library with a single callback, so it does not replace Drogon in a C++ codebase.
- Multi-threaded serving on Windows: proto/multithread.nim compiles only when not defined(windows), and the README says it has been tested on Linux and macOS only.
- If you need stable performance across releases: issue #2 (2026-08-04) records an 8x regression, from 138k/s to 16-30k/s, after security timer fixes. It was resolved, but it shows how sensitive the hot path is.

## How it is fast

One edge-triggered epoll (kqueue on BSD/macOS) loop per worker thread, with SO_REUSEPORT spreading connections in the kernel, so workers never talk to each other. The HTTP/1.1 parser works on byte offsets and builds strings only on demand. CRLF and end-of-headers are found with SSE2 (scalar fallback elsewhere). Simple responses are built in one stack buffer and sent with a single send(), with the Date header cached. Connections, buffers, parsers, requests and responses come from pools, and writes are corked (TCP_CORK/TCP_NOPUSH) or batched with writev.

## Compared with alternatives

Pick it if you work in Nim and want a full event-loop toolkit (HTTP/1.1, HTTP/2, WS, TLS, UDP), not just a raw HTTP responder. In the same 2026-10-06 the-benchmarker table, jet_server (Dart) is 1.5-4% faster, while khttp and Tako (Rust) are 8-24% slower (derived from page data). The HttpArena entries (vanilla, zix, zeemo) carry stronger evidence because they beat a tuned nginx under one harness.

## Integration

| | |
|---|---|
| **Form** | module (Nimble package, built from source) |
| **Dependencies** | voodoo, nimsimd, mimedb, openparser, multipart, checksums (Nimble packages); OpenSSL 3.x for TLS |
| **Minimum toolchain** | Nim 2.2.0+ (powpow.nimble); io_uring backend needs Linux 5.6+ |
| **Platforms** | Linux (epoll by default, io_uring opt-in with -d:powpowIoUring), macOS/BSD (kqueue), Windows (IOCP, single-threaded server only); SSE2 scanning on x86, scalar elsewhere |
| **Thread safety** | One loop per worker thread with no shared state. Handlers must be {.gcsafe.}. Loop.stop() is safe to call across threads (eventfd or self-pipe). Thread-pool results come back as callbacks on one dispatch thread. The rate limiter was made thread-safe for multi-threaded mode (README security roadmap). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the suite build: nim/Dockerfile compiles every Nim entry with --passC:-flto --passL:-flto --assertions:off -d:release --opt:speed in the nimlang/nim:2.2 image (Debian bookworm). Drogon is built with plain cmake -DCMAKE_BUILD_TYPE=release and no LTO on debian:trixie-slim. So the Nim side had LTO and the C++ side did not, and the two used different distro GCCs (inferred from the base images; versions not pinned). The record's 'no LTO' for powpow is wrong.
- The suite flag -d:powpowPewPew is read only in powpow's own config.nims, where it turns on -d:danger, turns off bound and overflow checks and adds -march=native. The suite builds /usr/src/app/server.nim with powpow installed as a Nimble dependency. Nim reads config.nims only from the project directory and its parents, and the suite's nim/powpow folder has no config.nims (only config.yaml, server.nim and server.nimble). So the flag most likely did nothing in the published run, and no source file under src/ references it.
- The suite entry was written by the powpow author. Until commit 4cce691 (2026-09-30) it ran one event loop (newHttpServer()), which explains the earlier single-core snapshots. The 2026-10-06 data.json is the only published run with the threaded server ahead of Drogon. That run was below the suite README's 75% server-bound threshold (powpow 53-56% CPU saturation, Drogon 62-63%), so the load generator may have been the ceiling.
- Responses always carry Date and Connection headers but no Content-Type unless you set one. That is 99.3 bytes per response against Drogon's 78.3 in this suite, so powpow was not winning by sending less. README doc links point to docs/contents/..., but the repository ships md_docs/.

## Known shortcomings

- Win appears in one snapshot only (2026-10-06); the prior two snapshots were 0.53-0.63x Drogon with CPUs under-used; suite entry by the author with no router; the -d:powpowPewPew flag is not in the source; README says not production-ready; the-benchmarker 2026-10-06 rows sit at 53-62% CPU saturation (the suite counts only above 75% as server-bound); CPU string 'M1 Eight-Core Processor' names no model and the C++ compiler version is not pinned; cwist (C) is the best C row at 64 connections.
- Build asymmetry: the suite's nim/Dockerfile builds every Nim entry with --passC:-flto --passL:-flto --assertions:off while Drogon is a plain cmake release without LTO, so the record's 'no LTO' for PowPow was wrong; different distro GCCs (nimlang/nim:2.2 bookworm vs debian:trixie-slim); -d:powpowPewPew is read only in powpow's own config.nims, which the suite's server.nim build does not use, so the flag is most likely a no-op. p99 is 7.6/15.9/21.3 ms against cwist's 0.50/1.84/3.68 ms (a throughput-only win); single-threaded until suite commit 4cce691 (2026-09-30); issue #2 reports an 8x regression (138k to 16-30k req/s); the multithreaded server does not run on Windows.

## Caveats and trade-offs

The README says 'not production-ready and may contain bugs and security vulnerabilities' and claims 'Pow Pow is the #1 fastest HTTP server' from the same benchmark site, a first-party reading of this table. The suite entry nim/powpow was written by the powpow author (georgelemon commits, including 4cce691 on 2026-09-30); it has no router and dispatches on method and path by hand, while the Drogon entry runs Drogon's routing and HttpResponse path; powpow averages 99.3 bytes received per request vs 78.3 for Drogon (derived from total_bytes_received / total_requests). The win over Drogon is in one published snapshot only: on 2026-10-02 (after the multithreading fix) powpow ran at 13% CPU saturation and 0.53-0.56x Drogon, on 2026-09-24 at one core and 0.55-0.63x. The build flag -d:powpowPewPew does not appear in src/powpow.nim, src/powpow/{loop,net,types,proto}.nim or src/powpow/proto/{http,httpserver,multithread}.nim at HEAD, so its effect was not found (possibly a no-op). The README footer says 'All rights reserved' beside an MIT LICENSE file (2026 OpenPeeps); the LICENSE file governs. The README 'Dummy Benchmarks' (wrk -t4 -c100, 5 s) ran on a GitHub Actions runner with client and server on the same machine and no baseline. 20 stars. Suite-level weaknesses: published snapshots move a lot between runs (Drogon 101,282-179,279 req/s across the 2026-09-15 to 2026-10-06 snapshots) and a snapshot gives no repeat spread; the suite README says a run is server-bound only above 75% CPU saturation and invalid below 50%, and in the 2026-10-06 snapshot the 60 fastest rows sit at 49-63% (Drogon 62-63%), so the ceiling for the fastest servers may be the load generator or the box rather than the server; the presence of the server_cpu_saturation / server_cpu_cores probe places this snapshot in the README's current zrk --closed keep-alive revision, although the README's contract paragraph still describes oha with keep-alive disabled; the workload is three trivial routes (GET /, GET /user/:id, POST /user) with near-empty bodies. The C/C++ rows are only Drogon 1.9.13 (cmake -DCMAKE_BUILD_TYPE=release, threads_num 0 = auto, Server and Date headers disabled, no LTO), oatpp 1.3, agoo-c 0.7 and cwist 3.9 (C); cwist is the best C row at 64 connections (186,252) and agoo-c at 256 and 512; nginx, h2o and lithium are not rows in this suite. Same table, losers to Drogon at 256 connections: Crystal toro 166,910, Go fasthttp 166,243, C# aspnet-minimal-api 147,805 vs Drogon 178,341. The CPU string 'M1 Eight-Core Processor' on an x86_64 Fedora kernel is not a recognisable CPU model, and no C++ compiler version is pinned in the suite files read (cpp/drogon/config.yaml language version '14/17'), which is why this is B and not A. [retier] Build asymmetry: the Nim entry gets LTO and assertions off while Drogon is a plain release without LTO, on different distro GCCs. p99 is 7.6/15.9/21.3 ms against cwist's 0.50/1.84/3.68 ms (a throughput-only win); single-threaded until suite commit 4cce691 (2026-09-30); issue #2 reports an 8x regression (138k to 16-30k req/s); the multithreaded server does not run on Windows; the README says not production-ready.

Event-notification library (alternative to libuv and libevent) with a built-in HTTP/1.1 and HTTP/2 server, epoll/kqueue/IOCP and an io_uring option; no router, so the suite entry hand-matches paths.

## Maintenance

Very active single-author MIT project (293 commits, latest 2026-10-06, version 0.2.2, 20 stars) that calls itself not production-ready; usable for Nim experiments and internal services, not as a hardened public server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** data.json (updated 2026-10-06) of the independent the-benchmarker/web-frameworks suite has powpow (framework_id 1927) and Drogon (55) with exactly the quoted req/s, with public code and build options (nim/powpow/server.nim, nim/config.yaml, nim/powpow/config.yaml, cpp/drogon/\*). Not A: the CPU string 'M1 Eight-Core Processor' is not a recognisable model and no C++ compiler version is pinned; the README's own wrk numbers have no baseline and no hardware.
- **Retiered** B to C: Enricher: the suite builds the Nim entry with LTO and assertions off while Drogon is a plain release without LTO (the record's 'no LTO' was backwards), the entry was written by the author, and the win is throughput-only with p99 15-40x worse than the C row; asymmetric build precedent: B to C.
- **Verifier notes:** Numbers verified in data.json (2026-10-06); kept at B like the other the-benchmarker entries, but the win is unreproduced: the previous two snapshots show powpow slower than Drogon (0.53-0.63x) while it was under-utilising its CPUs. Shortcomings to record: single-snapshot win, first-party suite entry without a router, self-described not production-ready, untraced -d:powpowPewPew flag, rows below the suite's 75% server-bound threshold.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-51 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8657397/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/5d9db56/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/.spec/route_spec.rb>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/main.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/controllers/UserCtrl.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/plugins/SyncPlugin.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/c/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/c/agoo-c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/powpow/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/powpow/server.nim>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/nim/powpow>
  - <https://github.com/openpeeps/powpow>
  - <https://github.com/openpeeps/powpow/commits/main>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/README.md>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/powpow.nimble>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/http.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/httpserver.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/multithread.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/loop.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/net.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/types.nim>
- **Sources the enricher read:**
  - <https://github.com/openpeeps/powpow>
  - <https://github.com/openpeeps/powpow/tree/main/src/powpow>
  - <https://github.com/openpeeps/powpow/commits/main>
  - <https://github.com/openpeeps/powpow/issues?q=is%3Aissue>
  - <https://github.com/openpeeps/powpow/issues/1>
  - <https://github.com/openpeeps/powpow/issues/2>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/README.md>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/powpow.nimble>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/config.nims>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/md_docs/contents/performance.md>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/http.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/httpserver.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/multithread.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/proto/simdscan.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/loop.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/net.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/net/tcp.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/net/common.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/types.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/platform.nim>
  - <https://raw.githubusercontent.com/openpeeps/powpow/HEAD/src/powpow/http.nim>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/powpow/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/powpow/server.nim>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/nim/powpow/server.nimble>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/nim/powpow>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/nim/powpow>
  - <https://github.com/the-benchmarker/web-frameworks/commit/4cce691>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/main.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/controllers/UserCtrl.cc>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/openpeeps/powpow`) · [data/wave14/enrich/raw/github_com_openpeeps_powpow.json](../../../data/wave14/enrich/raw/github_com_openpeeps_powpow.json) (enrichment confidence 0.55)

</details>
