# icey (HTTP server module)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1-or-later` · 🟢 active

> Single-threaded libuv + llhttp HTTP/1.1 server inside a C++20 media toolkit; 34% more keep-alive req/s than Go net/http on one vCPU.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | Keep-alive: icey 72,209 req/s at 1.43 ms average latency versus Go 1.25 net/http 53,878 req/s at 2.31 ms (README: 'outperforms Go's net/http by 34%'), Node.js v20 45,514 req/s at 3.56 ms, raw libuv+llhttp 96,088 req/s at 1.04 ms. Connection: close is parity: icey 14,330 req/s versus Go 14,723 req/s (Go marginally ahead), Node.js 9,309 req/s, raw libuv 18,468 req/s. |
| **Workload** | wrk -t4 -c100 -d10s against an empty-body 200 OK handler on one vCPU: icey single-threaded HTTP/1.1 keep-alive server versus a Go net/http keep-alive server (Node.js v20 and a hand-rolled libuv+llhttp C server also measured). |
| **Metric** | throughput |
| **Hardware** | 11th Gen Intel Core i7-11800H @ 2.30GHz, 1 vCPU, Linux 6.8.0-106-generic x86_64 |
| **Compiler and flags** | C++ compiler not stated for the published run (README lists GCC 12+ / Clang 15+ as supported; the CHANGELOG's clang-18 CI benchmark job covers only the httpbench microbenchmarks, not the wrk numbers). Built with cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PERF=ON -DENABLE_LOGGING=OFF; no project-specific optimisation flags in CMakeLists.txt or src/http/perf/CMakeLists.txt (CMake Release defaults, docs say -O2/-O3), C++20. Baselines: go1.25.0 default net/http, Node v20.19.5, wrk 4.1.0 [epoll] with -t4 -c100 -d10s --timeout 5s. Harness: src/http/perf/benchmark.sh, httpperf.cpp, go-server.go, node-server.js. |
| **Adoption** | 1.4k stars, 353 forks (repository is the renamed sourcey/libsourcey; github.com/sourcey/libsourcey now shows nilstate/icey) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/nilstate/icey) · [benchmark](https://github.com/nilstate/icey/blob/main/src/http/perf/README.md) |

## Verdict

First-party wrk 4.1.0 run (-t4 -c100 -d10s, one run) on a single vCPU of an i7-11800H, Linux 6.8, with wrk on the same vCPU: an empty 200 OK keep-alive handler served 72,209 req/s (1.43 ms) on icey vs 53,878 req/s (2.31 ms) on default go1.25.0 net/http, Node v20.19.5 at 45,514 and a hand-written libuv+llhttp server at 96,088. With Connection: close icey and Go tie (14,330 vs 14,723 req/s). icey was a CMake Release, C++20 build with logging off; the compiler is unstated, and icey's responses omit the Date header that Go and Node send.

## Use it when

- You already use icey for WebRTC, TURN, Symple signalling or FFmpeg pipelines and want HTTP/WebSocket endpoints on the same libuv loop without adding a second framework
- Small-response HTTP/1.1 keep-alive APIs or control endpoints where per-request overhead dominates and one core per server instance (SO_REUSEPORT for more cores) fits
- Streaming HTTP to browsers (MJPEG via multipart/x-mixed-replace, chunked responses, WebSocket) from a C++ media process
- Embedding an HTTP server in a C++20 application on Linux, macOS or Windows where a CMake FetchContent build with libuv/llhttp is acceptable

## Skip it when

- Connection-per-request traffic: with Connection: close the published run shows no gain (icey 14,330 vs Go 14,723 req/s)
- You need HTTP/2, HTTP/3, a router, middleware or strict RFC compliance: the module is HTTP/1.1 only, routing is your own responder code, and the Server class comment says it is 'not strictly standards compliant' (for example, responses carry no Date header unless you add one)
- Multi-core throughput claims matter: only single-vCPU numbers are published; the SO_REUSEPORT 'multi' and Node cluster variants that benchmark.sh runs are not in the results table
- LGPL-2.1+ is a problem for static linking into proprietary binaries
- You want a dedicated, independently benchmarked C++ web framework rather than one module of a 16-module media toolkit

## How it is fast

Everything runs on one libuv loop with no locking: signals are LocalSignal (NullSharedMutex), and ServerConnection objects are recycled through a LIFO ConnectionPool (default 128) via reset() instead of being reallocated. Hot-path trims from the 2.1.0 release include pre-formatted status lines for common codes, single-pass header assembly with a pre-computed reserve, a uv_write_t freelist in Stream, cached peer addresses and an intrusive non-atomic refcount; parsing is llhttp. Against Go the gain is the absence of goroutine scheduling and GC on a tight empty-response loop; the benchmark's raw libuv+llhttp ceiling (96,088 req/s) shows icey's abstractions cost about 25% of that.

## Compared with alternatives

Pick icey when the HTTP server lives inside a C++ media or WebRTC process that already runs icey's libuv loop. For a standalone C++ HTTP service, Drogon, Crow or aeronet beat Go net/http in multi-core, third-party or broader runs (the-benchmarker, TechEmpower-style code, Beast comparisons) and include routing that icey's http module lacks.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake modules; link icey::base, icey::net, icey::http) |
| **Dependencies** | libuv 1.50, llhttp 9.2.1, zlib 1.3.1 and nlohmann/json 3.11.3 (fetched by CMake); OpenSSL 3.x optional for HTTPS/WSS |
| **Minimum toolchain** | C++20, CMake 3.21; GCC 12+, Clang 15+, AppleClang 15+ (Xcode 15) or MSVC 2022 |
| **Platforms** | Linux, macOS, Windows (SO_REUSEPORT multicore mode Linux 3.9+) |
| **Thread safety** | One server per event loop; signals use NullSharedMutex, so a server and its connections must only be touched from their loop thread. Multi-core means one Server per thread, each with its own uv::ScopedLoop and setReusePort(). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: icey's benchmark responses carry no Date header (and neither do the raw libuv responses), while Go net/http adds Date and Node adds Date, Connection and Keep-Alive. Server::DateCache is refreshed every second but nothing in src/http/src (HEAD or tag 2.3.0) writes it into a response, so docs/modules/http.md wrongly credits a 'date cache' for the 72,209 req/s row. Go spends extra formatting and bytes per response that icey skips; the effect is probably small next to the 4.7 us per-request gap (derived from page data), but the comparison is not like-for-like.
- Connection: close rows are not symmetric either: icey's 'single' handler sends a Connection: close header but never calls close(), and because wrk's request is keep-alive, ServerConnection::onComplete readies the socket for another request, so wrk tears the connection down; Go, Node and the raw libuv server close it server-side.
- Server::Connection is documented as 'Signals when a new connection has been created' but is emitted from ServerConnection::onHeaders on every request. Lambdas attached inside it (the README's conn-&gt;Payload += ... pattern) are never deduplicated (FunctionDelegate equality is always false) and ConnectionPool reuse via reset() does not detach Payload slots, so slots pile up across keep-alive requests and pooled sockets. Use a ServerResponder factory for per-request state. (From reading server.cpp, signal.h and delegate.h; not run.)
- Results table is hand-edited and single-run: its labels differ from what benchmark.sh prints (e.g. 'Raw libuv+llhttp (baseline)' for the keep-alive raw row, 'Go 1.25 (single)'), the icey rows are misaligned by 6 characters, the multi-core and Node cluster rows are dropped, and the numbers date from 2.1.0 (2026-03-19); the C++ compiler is not named.

## Known shortcomings

- Compiler never named; wrk shares a single vCPU with the server; one run; numbers are from 2.1.0 (2026-03-19), not re-run on 2.5.0, and the same release fixed a sendHeader() use-after-free with run order vs fix unknown; docs/modules/http.md gives wrk -c400 -d30s while the perf README gives -c100 -d10s; the README's claim that Go shares libuv plus llhttp is wrong; the media-stack claims against libWebRTC are qualitative only. The repo is the renamed sourcey/libsourcey (seeds.json lists it under that name; fold as duplicate if seeded again). Filed under networking-and-servers/http-servers-frameworks by override although mined into wave 10.
- Enricher: icey and raw libuv responses send no Date header while Go and Node do (the 'date cache' credit in docs/modules/http.md is wrong, nothing writes it into responses); the Connection: close handler never calls close(), so wrk tears connections down; the table is hand-edited from a single 2.1.0 run with misaligned rows and dropped multi/cluster rows. Server::Connection fires per request, lambda slots never dedup, Pool reset() leaks Payload slots.

## Caveats and trade-offs

First-party benchmark with public harness and CPU stated, but the C++ compiler is not named, so it falls short of tier A. Server and wrk (4 threads) share the single vCPU, so the load generator competes with the server for CPU; one run, no variance reported. The numbers were recorded in the 2.1.0 release (CHANGELOG, 2026-03-19) and have not been re-measured on the current 2.5.0; the same 2.1.0 release also fixed a use-after-free in sendHeader() (the call the benchmark handler makes), and the page does not say whether the run came before or after that fix. docs/modules/http.md quotes the same numbers but gives a different load (wrk -t4 -c400 -d30s) than the perf README and CHANGELOG (-t4 -c100 -d10s). The handler returns an empty 200 with no routing, TLS or body, so this measures per-request framework overhead only. With Connection: close the claim disappears (Go 14,723 versus icey 14,330 req/s); the README headline table shows only the keep-alive rows. The Go server is default net/http (goroutine-per-connection, no tuning), and the README's statement that icey, Go and Node 'all share the same foundation (libuv ... llhttp)' is wrong for Go, which uses its own netpoller and parser. The project's headline claim (lightweight libwebrtc alternative, media stack) has no numeric comparison: the README table against libWebRTC, libdatachannel and GStreamer is qualitative (build time 'Hours' versus 'Minutes', binary size '50MB+' versus 'Small'), so this record documents the HTTP module only.

Single-threaded libuv loop per server; multi-core scaling is one server per core with SO_REUSEPORT (the 'multi' variant, not part of the quoted comparison). LGPL-2.1+ licence. C++20. The HTTP module is one of about 16 modules (WebRTC via libdatachannel, TURN, Symple signalling, FFmpeg pipeline).

## Maintenance

Actively maintained (2.5.0 released 2026-06-19, commits through 2026-09-30, 1.4k stars under the renamed sourcey/libsourcey repo) and usable as a CMake FetchContent dependency under LGPL-2.1+; the HTTP numbers have not been re-measured since 2.1.0, and 2.5.0's changelog lists a broad memory-safety hardening pass across sockets and HTTP.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wrk results on src/http/perf/README.md with public harness (src/http/perf/benchmark.sh, httpperf.cpp, go-server.go, node-server.js), CPU (i7-11800H, 1 vCPU), kernel, Go/Node/wrk versions and CMake Release build stated, but the C++ compiler is never named, so it misses A; no independent measurement, so not B.
- **Verifier notes:** Numbers on the perf README match the record exactly (keep-alive 72,209 vs Go 53,878 req/s, 34%; Connection: close 14,330 vs 14,723). Harness code is fair-looking (identical empty-200 handlers with Content-Length: 0 across icey, Go, Node). Shortcomings to record: compiler unstated, wrk on the same single vCPU, single run, numbers from 2.1.0 not re-run, inconsistent wrk parameters between docs and perf README, parity with Go under Connection: close, false 'same foundation' claim for Go, media-stack claims purely qualitative. Category http-servers-frameworks (wave 5 category, Go net/http baseline as for Drogon, Lwan, Crow) is outside wave 10's categories. Duplicate risk: seeds.json also lists https://github.com/sourcey/libsourcey (awesome-cpp frameworks), which is this same repo under its old name; fold it as duplicate if a seed pass picks it up.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** multi-core run on a current release with compiler stated; enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/nilstate/icey>
  - <https://github.com/nilstate/icey/commits>
  - <https://github.com/nilstate/icey/tree/main/src/http/bench>
  - <https://github.com/sourcey/libsourcey>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/README.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/README.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/benchmark.sh>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/go-server.go>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/httpperf.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/node-server.js>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/docs/modules/http.md>
- **Sources the enricher read:**
  - <https://github.com/nilstate/icey>
  - <https://github.com/nilstate/icey/tags>
  - <https://github.com/nilstate/icey/tree/main/src/http/src>
  - <https://github.com/nilstate/icey/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/README.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/README.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/benchmark.sh>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/httpperf.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/go-server.go>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/node-server.js>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/docs/modules/http.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/VERSION>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/include/icy/http/server.h>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/server.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/connection.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/response.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/message.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/client.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/websocket.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/http/src/parser.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/base/include/icy/signal.h>
  - <https://raw.githubusercontent.com/nilstate/icey/HEAD/src/base/include/icy/delegate.h>
  - <https://raw.githubusercontent.com/nilstate/icey/2.3.0/src/http/src/server.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/2.3.0/src/http/src/connection.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/2.3.0/src/http/perf/README.md>
  - <https://raw.githubusercontent.com/nilstate/icey/2.3.0/src/http/perf/httpperf.cpp>
  - <https://raw.githubusercontent.com/nilstate/icey/2.3.0/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/nilstate/icey`) · [data/wave10/enrich/raw/github_com_nilstate_icey.json](../../../data/wave10/enrich/raw/github_com_nilstate_icey.json) (enrichment confidence 0.75)

</details>
