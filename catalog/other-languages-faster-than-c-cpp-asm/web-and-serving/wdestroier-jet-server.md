# jet_server

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Dart` · `MIT` · 🟢 active

> Experimental pure-Dart HTTP/1.1 server driving epoll through dart:ffi; 1.36-1.46x Drogon's req/s in the-benchmarker.

| | |
|---|---|
| **Beats** | Drogon 1.9.13 (C++, trantor event loop; the-benchmarker cpp/drogon, cmake release build); also agoo-c 0.7 (C) in the same table |
| **Claimed result** | jet_server 0.2 in data.json updated 2026-10-06: AOT build 240,586 / 255,549 / 249,136 req/s and Dart VM build 248,591 / 256,385 / 249,676 req/s at 64 / 256 / 512 connections vs Drogon 177,005 / 178,341 / 171,358 (AOT 1.36x / 1.43x / 1.45x, VM 1.40x / 1.44x / 1.46x, derived from page data); vs agoo-c (C) 1.67x-1.73x at 64, 1.19x at 256, 1.24x at 512, and vs cwist 3.9 (C, best C row at 64 connections, 186,252) 1.29x AOT / 1.33x VM (derived from page data). The 2026-10-02 snapshot (commit 8657397) repeats the result: AOT 240,062 / 255,010 / 249,609 vs Drogon 179,279 / 178,932 / 173,062 (1.34x / 1.43x / 1.44x, derived from page data). jet_server 0.1 in the 2026-09-24 snapshot (commit f673364) was 1.22x Drogon at 64 connections, 0.64x at 256 and 0 req/s at 512 (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks minimal HTTP contract (GET /, GET /user/:id, POST /user on port 3000), total_requests_per_s at 64, 256 and 512 connections, each framework in its own container. |
| **Metric** | throughput |
| **Hardware** | data.json hardware field (published 2026-10-06): cpu_name 'M1 Eight-Core Processor', cpus 16, memory 7,733,008 kB, Linux 7.2.7-200.fc44.x86_64 (Fedora). Per-run server_cpu_cores / server_cpu_saturation imply about 4 CPUs allotted to each server container (derived from page data). |
| **Compiler and flags** | Dart 3.13 (dart/config.yaml engines aot: /app/server, vm: dart run /app/server.dart); jet_server ^0.2.0 from pub (dart/jet_server/pubspec.yaml). Drogon 1.9.13: cmake -DCMAKE_BUILD_TYPE=release (CMake release flags), C++17, no LTO; no C++ compiler version pinned in the suite files read (cpp/drogon/config.yaml language version '14/17'); config.json threads_num 0 (auto), log level WARN, Server and Date headers disabled. No server_cpu_cores or server_cpu_saturation metric is recorded for any Dart row. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Dart FFI binding to epoll with an event loop (README); the margin is not explained. |
| **Adoption** | 1 star, 1 fork, 8 commits |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/Wdestroier/jet_server) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json) |

## Verdict

In the-benchmarker/web-frameworks data.json updated 2026-10-06 (16-CPU x86_64 Fedora host labelled 'M1 Eight-Core Processor', about 4 CPUs per server container judging by Drogon's 2.5 cores at 62% saturation), jet_server 0.2 AOT served 240,586 / 255,549 / 249,136 req/s at 64 / 256 / 512 connections. Drogon 1.9.13 (CMake release, threads auto) served 177,005 / 178,341 / 171,358, so jet_server was 1.36-1.45x faster (ratios derived from page data). All rows recorded zero socket and HTTP errors, and the Dart VM build matched AOT within 3.5%.

## Use it when

- Dart services on x86-64 Linux that answer tiny, fixed or computed responses synchronously (health checks, echo, small lookups from memory) and need far more req/s than shelf (about 33k vs 256k req/s in the same table).
- Benchmarks or experiments on how far Dart AOT or JIT can go with raw epoll through FFI.
- Very small, auditable code (about 1,300 lines across lib/src) that you plan to vendor and harden yourself.

## Skip it when

- Handlers that need async work (database calls, HTTP clients, timers): the handler is synchronous and serve() blocks the isolate in epoll_wait, so Futures and timers scheduled in that isolate cannot run while it serves (by code reading).
- aarch64 or other non-x86-64 Linux: the code hard-codes the packed 12-byte x86-64 struct epoll_event (stride 12, fd at offset 4), but Linux packs the struct only on x86_64. Elsewhere it is 16 bytes, so events are misread and epoll_wait can write past the 12\*maxEvents-byte buffer.
- Internet-facing or proxied traffic: no Transfer-Encoding: chunked support (chunked bodies are parsed as the next request), no idle or slowloris timeouts, no TLS, no HTTP/2, and no Date header unless the handler writes one.
- Anyone needing a supported framework: 8 commits, 1 star, self-described experimental, Linux/WSL only.

## How it is fast

Each isolate runs a level-triggered epoll loop written in Dart that calls accept4, recv, send and epoll_ctl in libc through dart:ffi, bypassing dart:io's socket and stream layers. It reuses a 64 KiB native receive buffer and a 64 KiB send buffer per loop, keeps per-connection stashes for pipelined or fragmented requests, and parses only the request line plus the Connection and Content-Length headers. The hot loops carry vm:unsafe:no-bounds-checks and vm:unsafe:no-interrupts pragmas. In the suite entry the handler matches routes byte by byte and returns pre-built response arrays without Date, Server or Content-Type headers, so most of the per-request work in a framework like Drogon never runs.

## Compared with alternatives

Pick it only when the server must be Dart. In the same the-benchmarker table, PowPow (Nim, 248,309 req/s at 256 connections), khttp (Rust, 199,813) and Tako (Rust, 200,361) beat Drogon without the x86-64-only FFI layout or the synchronous-handler limit, and PowPow and the HttpArena siblings (vanilla, by enghitalo, who is co-credited in jet_server's LICENSE) are more mature.

## Integration

| | |
|---|---|
| **Form** | module (pub.dev package jet_server 0.2.0) |
| **Dependencies** | package:ffi ^2.1.0; glibc or musl libc at runtime (libc.so.6 or process symbols) |
| **Minimum toolchain** | Dart SDK 3.13 |
| **Platforms** | Linux and WSL only (throws UnsupportedError elsewhere); x86-64 only in practice because of the hard-coded 12-byte epoll_event layout; IPv4 INADDR_ANY bind only |
| **Thread safety** | one JetServer loop per isolate with no shared state; scale out by spawning isolates that each bind the port with SO_REUSEPORT (the benchmark spawns Platform.numberOfProcessors isolates) |
| **Drop-in for the baseline** | no |

## Gotchas

- Remote crash, by code reading (not run): Content-Length is parsed with unchecked n\*10+d on wrapping 64-bit Dart ints, so a 20-digit value wraps negative. total = headerEnd + contentLength then passes the end &lt; total test, conn.start is set below the request start, and the next pass calls findHeadersEnd (vm:unsafe:no-bounds-checks) at a negative index, or conn.compact() throws an uncaught RangeError out of serve(). Either way one request can take down a serving isolate.
- Stale connection state: _flushPending's close-after path (and a blocked _sendClose) closes the fd without removing conns[fd], so a later accept that reuses the fd number inherits the previous client's leftover buffered bytes.
- Benchmark entry is author-written and suite-specialised: dart/jet_server/server.dart compares raw method and path bytes and returns pre-built 62-byte replies with no Content-Type, Date or Server header, while Drogon runs its router and builds HttpResponse objects. jet_server averages 62.3 bytes per response vs Drogon's 78.3, and no Dart row records the suite's server_cpu_saturation check.
- Under write backpressure, a connection with pending output returns from _handleRead without reading, so level-triggered EPOLLIN keeps firing and the loop spins until the socket becomes writable. BufferPool is allocated but unused in the hot path.

## Known shortcomings

- Suite entry written by the author and tuned to the benchmark (pre-built responses, no router, no Content-Type); no Dart row has a saturation probe; the event loop is pure Dart via dart:ffi, not a native loop; the-benchmarker 2026-10-06 rows sit at 53-62% CPU saturation (the suite counts only above 75% as server-bound); CPU string 'M1 Eight-Core Processor' names no model and the C++ compiler version is not pinned; cwist (C) is the best C row at 64 connections.
- Security bugs by code reading (not behind the numbers): the Content-Length parse overflows (20 digits wrap negative), conn.start goes negative, then findHeadersEnd reads with no bounds checks or compact() throws an uncaught RangeError, so one request kills the serving isolate; the epoll_event stride is hard-coded at 12 bytes (x86-64 packing only), so it is broken on aarch64 with a possible buffer overrun; stale conns[fd] after the close-after path; no chunked encoding; a sync handler blocks async I/O. The suite entry is suite-specialised (pre-built 62-byte replies); zero errors in data.json.

## Caveats and trade-offs

The suite entry dart/jet_server/server.dart was written by the jet_server author (suite commits b869a75, ac9f6f2 and b3f17f2 by Wdestroier) and is specialised to the benchmark: it returns pre-built response byte arrays, routes by comparing raw bytes, sends no Content-Type header and uses no router, while the Drogon entry runs Drogon's routing (a sync advice for GET /, UserCtrl for the /user routes) and builds HttpResponse objects with Content-Type: text/plain; jet_server averages 62.3 bytes received per request vs 78.3 for Drogon (derived from total_bytes_received / total_requests), so handler work is not equal. The library is pure Dart: lib/src holds buffer_pool, constants, http_parser, jet_server_impl and syscall .dart files and the package depends only on ffi, so the event loop and parser are Dart code calling libc epoll/read/write through dart:ffi; the near-equal AOT and VM rows mean the JIT reaches AOT speed after warmup or both rows hit a common ceiling, not that a native C loop does the work. No Dart row in data.json (jet_server, shelf, relic, spry) carries the suite's server_cpu_saturation / server_cpu_cores validity probe, so whether jet_server was server-bound, or ran under the same 4-CPU allotment as Drogon, cannot be checked. The top rows at 256 connections cluster within 1.5% (morojs-engine 259,617, morojs 259,418, jet_server-vm 256,385, caprese 256,004, jet_server 255,549), consistent with a shared ceiling. The README prints no numbers and points to the-benchmarker; its own benchmarks/jet_vs_shelf compares only against Dart's shelf. The project calls itself experimental and targets Linux/WSL only; 8 commits, 1 star. Suite-level weaknesses: published snapshots move a lot between runs (Drogon 101,282-179,279 req/s across the 2026-09-15 to 2026-10-06 snapshots) and a snapshot gives no repeat spread; the suite README says a run is server-bound only above 75% CPU saturation and invalid below 50%, and in the 2026-10-06 snapshot the 60 fastest rows sit at 49-63% (Drogon 62-63%), so the ceiling for the fastest servers may be the load generator or the box rather than the server; the presence of the server_cpu_saturation / server_cpu_cores probe places this snapshot in the README's current zrk --closed keep-alive revision, although the README's contract paragraph still describes oha with keep-alive disabled; the workload is three trivial routes (GET /, GET /user/:id, POST /user) with near-empty bodies. The C/C++ rows are only Drogon 1.9.13 (cmake -DCMAKE_BUILD_TYPE=release, threads_num 0 = auto, Server and Date headers disabled, no LTO), oatpp 1.3, agoo-c 0.7 and cwist 3.9 (C); cwist is the best C row at 64 connections (186,252) and agoo-c at 256 and 512; nginx, h2o and lithium are not rows in this suite. Same table, losers to Drogon at 256 connections: Crystal toro 166,910, Go fasthttp 166,243, C# aspnet-minimal-api 147,805 vs Drogon 178,341. The CPU string 'M1 Eight-Core Processor' on an x86_64 Fedora kernel is not a recognisable CPU model, and no C++ compiler version is pinned in the suite files read (cpp/drogon/config.yaml language version '14/17'), which is why this is B and not A. [retier] Security bugs by code reading: the Content-Length parse overflows (20 digits wrap negative) and findHeadersEnd then reads with no bounds checks or compact() throws an uncaught RangeError, so one request kills the serving isolate; the epoll_event stride is hard-coded at 12 bytes (x86-64 packing only), broken on aarch64; stale conns[fd] after close-after; no chunked encoding; a sync handler blocks async I/O. The suite entry is suite-specialised (pre-built 62-byte replies).

Experimental HTTP/1.1 server for Linux built with Dart FFI and epoll; Linux/WSL only, minimal feature set.

## Maintenance

Active but experimental (8 commits, last on 2026-09-26; pub.dev versions 0.1.0 to 0.2.0 between 2026-08-30 and 2026-09-26), MIT-licensed and small enough to vendor, but by code reading it has an unchecked Content-Length overflow that can crash a serving isolate and an x86-64-only epoll layout; fix both before exposing it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** data.json (updated 2026-10-06) of the independent the-benchmarker/web-frameworks suite has jet_server (framework_id 316) and jet_server-vm (325) rows next to Drogon (55) with exactly the quoted req/s, and the 2026-10-02 snapshot repeats them; code and build files are public (dart/jet_server/server.dart, dart/config.yaml, cpp/drogon/\*). Not A: the CPU string 'M1 Eight-Core Processor' is not a recognisable model, no C++ compiler version is pinned, and no Dart row carries the suite's saturation validity probe.
- **Verifier notes:** Numbers verified in data.json (2026-10-06) and repeated in the 2026-10-02 snapshot; kept at B like the earlier the-benchmarker entries (caprese, morojs, hyper). Shortcomings to record: first-party benchmark-specialised suite entry (pre-built responses, no router, no Content-Type), no saturation probe for any Dart row, top rows clustered at a possible shared ceiling, 1-star experimental project; the record's 'native epoll loop' inference was wrong (the loop is Dart over dart:ffi).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
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
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/server.dart>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/pubspec.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/dart/jet_server>
  - <https://github.com/Wdestroier/jet_server>
  - <https://github.com/Wdestroier/jet_server/commits/main>
  - <https://github.com/Wdestroier/jet_server/tree/main/lib>
  - <https://github.com/Wdestroier/jet_server/tree/main/lib/src>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/pubspec.yaml>
- **Sources the enricher read:**
  - <https://github.com/Wdestroier/jet_server>
  - <https://github.com/Wdestroier/jet_server/commits/main>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/pubspec.yaml>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/jet_server.dart>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/src/jet_server_impl.dart>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/src/http_parser.dart>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/src/syscall.dart>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/src/buffer_pool.dart>
  - <https://raw.githubusercontent.com/Wdestroier/jet_server/HEAD/lib/src/constants.dart>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/server.dart>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/jet_server/pubspec.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/dart/config.yaml>
  - <https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/eventpoll.h>
  - <https://pub.dev/api/packages/jet_server>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/wdestroier/jet_server`) · [data/wave14/enrich/raw/github_com_wdestroier_jet_server.json](../../../data/wave14/enrich/raw/github_com_wdestroier_jet_server.json) (enrichment confidence 0.6)

</details>
