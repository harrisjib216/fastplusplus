# Pipy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++ programmable proxy scripted in PipyJS; the vendor's single-core hello-world test shows 1.4-2.6x nginx keep-alive throughput.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | wrk on ubuntu21-arm64: Pipy 218539 req/s vs nginx 82759 req/s (\~2.6x, derived from page data) |
| **Workload** | HTTP GET 'hello world' via wrk -c100 -t1 -d20 --latency (100 connections, 1 wrk thread, 20s), client and server on the same 2 vCPU/4GB ARM64 VM over 127.0.0.1; Ubuntu 21 Server and FreeBSD 13; Pipy script tutorial/02-echo/hello.js; also ab (short-lived connections) and fortio (fixed 10k QPS latency) |
| **Metric** | throughput |
| **Hardware** | 2 vCPU / 4GB ARM64 VM (Ubuntu 21 Server and FreeBSD 13, ARM64); no CPU model stated |
| **Adoption** | 832 stars |
| **Last commit** | 2026-06-12 |
| **Links** | [repository](https://github.com/flomesh-io/pipy) · [benchmark](https://github.com/flomesh-io/pipy/wiki/BENCHMARK-:-Pipy-as-Echo-server) |

## Verdict

In the project's own 2022 wiki test (Pipy version not stated, no compiler flags or CPU model), nginx 1.18.0 (Ubuntu 21) and 1.20.2 (FreeBSD 13) were distro packages with 1 worker, running on the same 2 vCPU ARM64 VM as the client. wrk -c100 -t1 measured Pipy at 218,539 vs 82,759 req/s (2.6x) on Ubuntu and 281,176 vs 204,544 (1.37x) on FreeBSD, with ab short-lived connections a tie. The comparison is not like-for-like: Pipy's replies were \~74 bytes against nginx's \~249 (63-byte vs \~243-byte headers). fortio opened 10,000 sockets for nginx against 100 for Pipy, which fits nginx 1.18's default keepalive_requests of 100 and likely inflates the Ubuntu gap. The FreeBSD Pipy runs used the 8081 echo port (empty body), not the 8080 hello port.

## Use it when

- You want an L4/L7 proxy, sidecar or gateway whose routing, auth and rewriting logic is written as code (JS-like expressions) rather than nginx directives or Lua, shipped as one \~10 MB binary with vendored dependencies.
- Small edge, IoT or cheap ARM64 hosts where requests/s per core counts: the vendor's 1-worker test on a 2 vCPU ARM64 VM gave 218,539 vs 82,759 req/s on Ubuntu and 281,176 vs 204,544 on FreeBSD over keep-alive, at about 9.3 MB RSS (nginx 6.5-7.5 MB).
- Keep-alive HTTP/1.1 traffic with small messages, where the vendor data also shows a lower saturated p50 (0.45 ms vs 1.20 ms on Ubuntu, 350 us vs 485 us on FreeBSD).
- Proxying or converting between several protocols (HTTP/2, TLS, MQTT, Dubbo, Thrift, RESP, SOCKS) from one binary.
- Scaling across many cores with --threads=N --reuse-port: the vendor's Pipy 0.90 test went from \~139k req/s on 1 thread to \~1.21M req/s on 12 threads (Xeon Gold 6144, no nginx comparison).

## Skip it when

- As a drop-in nginx web server: nginx.conf is not supported, static files go through script code (http.File), and I found no sendfile() use in Pipy's own src/.
- Workloads with one request per connection: in the vendor's ab runs Pipy only ties nginx (59,698 vs 60,824 req/s on Ubuntu, 95,074 vs 93,680 on FreeBSD).
- Latency at a fixed request rate: at 10k QPS (fortio) Pipy's p50 on Ubuntu was worse (1.851 ms vs 1.449 ms), and on FreeBSD it tied (506 vs 507 us).
- You need Windows binaries or a standard JS runtime: maintainers said in issue #200 that there are no Windows builds, and PipyJS has no classes or prototypes, no BigInt or Symbol, and no npm ecosystem.
- You need a large ecosystem or fast-moving project: 832 stars, last release 1.5.14 (2025-09-18), and the 2026 commits are mostly CI, TLS-cipher and admin fixes.

## How it is fast

It is C++ built on standalone Asio (an epoll/kqueue reactor). Each worker thread owns its own io_context and its own loaded copy of the script, so threads share nothing, and --reuse-port (SO_REUSEPORT, or SO_REUSEPORT_LB on FreeBSD) lets the kernel spread connections across threads. Payload bytes sit in reference-counted 16 KB chunks that are sliced by views, and the HTTP/1 decoder is a hand-written byte-scanning state machine that passes body bytes on as chunk references instead of copying them. Chunks, views and other hot objects come from thread-local per-type free-list pools (pjs::Pool, with an atomic return list for frees from other threads), which keeps malloc off the hot path. PipyJS is an in-house tree-walking interpreter with reference counting and no JIT. In the benchmark the response was a Message built once at load time, so almost no script ran per request.

## Compared with alternatives

Pick Pipy over Pingora when you want proxy logic you can script and hot-reload at runtime from a prebuilt binary, instead of compiling a Rust program against a framework. Pick H2O as an nginx-style origin/static server, and Sogou Workflow or cinatra to embed an HTTP server inside a C++ service; Pipy's niche is programmable proxying and protocol conversion.

## Integration

| | |
|---|---|
| **Form** | standalone executable (proxy server); the CMake options PIPY_STATICLIB and PIPY_SHARED can also build it as a static or shared library |
| **Dependencies** | Vendored in deps/ and built in: standalone Asio 1.28.0, OpenSSL 3.2.0, zlib 1.3.1, Brotli 1.0.9, LevelDB 1.23, SQLite 3.43.2, yajl 2.1.0, libyaml 0.2.5, libexpat 2.2.6. There are options to use system zlib/OpenSSL or TongSuo. Node.js v12+ is needed only to build the admin GUI. |
| **Minimum toolchain** | C++11 (CMake calls cxx_11()); Clang 5.0+ (build.sh defaults CC/CXX to clang); CMake 3.10+ per the README (the docs say 3.0+) |
| **Platforms** | Linux (RHEL/CentOS, Fedora, Ubuntu, Debian, openEuler, OpenWrt, Deepin, Kylin), macOS, FreeBSD, OpenBSD, Android; x86-64, ARM64, LoongArch, Hygon. Release binaries: Linux x86-64/aarch64, macOS x86-64/aarch64, Android arm64, EL7 RPM. No Windows binaries. |
| **Thread safety** | One worker thread by default. --threads=N (up to hardware_concurrency) starts N worker threads, each with its own Asio io_context and its own instance of the script module (shared-nothing). Context variables belong to each pipeline, not to the process. Cross-thread sharing beyond that is not documented in what I read. |
| **Drop-in for the baseline** | no |

## Gotchas

- CMakeLists.txt makes Debug the default build type. build.sh passes Release, but if you call CMake yourself, set -DCMAKE_BUILD_TYPE=Release or you will benchmark a debug binary.
- The defaults are one worker thread and no SO_REUSEPORT. Multi-core throughput needs --threads=N, which the vendor pairs with --reuse-port. Run with no arguments, Pipy starts in repo mode with an admin service/UI on port 6060 (turn it off with --admin-port-off).
- The PipyJS reference docs still describe an expression-only language with no if/for/try/class/import, but src/pjs/stmt.hpp implements If/For/Switch/Try/Import/Export statements, so the docs lag the engine. Strings are UTF-8 internally with code-point length ("😀".length is 1).
- The third-party list in the LICENSE file (Boost Asio, OpenSSL 1.1.1o/1.1.1g) is out of date: deps/ vendors standalone Asio 1.28.0 and OpenSSL 3.2.0. Check notices yourself when redistributing.

## Known shortcomings

- The 2.6x headline is the most favourable row on the project's own wiki page: FreeBSD wrk shows \~1.37x (281,176 vs 204,544), ab (one request per connection) is about even, and on Ubuntu fortio median latency is worse for Pipy. nginx ran the distro package with 1 worker and sent more header bytes per response. Old test (nginx 1.18/1.20, Ubuntu 21) on a 2 vCPU ARM64 VM with no CPU model, compiler or flags.
- Response sizes differ: Pipy's hello replies were \~74 bytes vs nginx's \~249 (63-byte vs \~243-byte headers), so nginx did 3.4x more header work. nginx 1.18 (the Ubuntu run) closes keep-alive connections after 100 requests by default (1000 from 1.19.10); fortio shows 10,000 sockets for nginx vs 100 for Pipy, which likely explains much of the 2.6x Ubuntu gap vs 1.37x on FreeBSD (inference). The FreeBSD Pipy runs hit the empty-body echo port 8081, not the 8080 hello service. Benchmark from 2022, Pipy version unstated, named script no longer exists, never re-run. LICENSE third-party list is stale (names Boost Asio and OpenSSL 1.1.1 while deps/ vendors Asio 1.28.0 and OpenSSL 3.2.0); PipyJS docs describe an expression-only language that the engine has outgrown; CMake defaults to Debug (only build.sh sets Release). Last release 1.5.14 (2025-09-18), 2026 commits mostly CI; no Windows binaries (#200).

## Caveats and trade-offs

First-party benchmark (project's own wiki), partial methodology: no compiler/build flags and no CPU model (only '2 vcpus', '2C4G', ARM64), so capped at tier C although command lines and raw tool outputs are published. The 2.6x headline is the most favorable row: on FreeBSD13 wrk the gap is 281176 vs 204544 req/s (\~1.37x, derived from page data); with ab short-lived connections Pipy roughly ties nginx (Ubuntu 59698 vs 60824, FreeBSD 95074 vs 93680); fortio P50 latency on Ubuntu is worse for Pipy (1.851ms vs 1.449ms). Raw wrk output shows nginx returned larger responses (393.12MB for 1.66M requests vs Pipy 308.60MB for 4.37M), i.e. more header bytes per reply. nginx was a distro package with 1 worker; Pipy built from source. Old test (nginx 1.18.0/1.20.2, Ubuntu 21), not re-run on current Pipy. LICENSE file: Pipy itself MIT; bundled deps (Boost Asio, OpenSSL 1.1.1o, zlib, SQLite, etc.) carry their own licenses (GitHub reports NOASSERTION).

Pipy is a programmable proxy (scriptable via PipyJS), not a drop-in nginx replacement; nginx was run with only 1 worker in this test which is not how nginx is typically deployed in production

## Maintenance

Active but slow-moving: last release 1.5.14 (2025-09-18) with CI and small fixes into mid-2026. Pipy's own code is MIT; the vendored dependencies keep their own licenses (GitHub reports NOASSERTION). Prebuilt Linux and macOS binaries make it easy to try.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Project's own wiki page benchmarks Pipy vs nginx (1 worker, distro package nginx/1.18.0) and hashicorp http-echo with full wrk/ab/fortio command lines and raw outputs; wrk Ubuntu21-arm64 rows show 82759.60 (nginx) vs 218539.23 (pipy) req/s. No CPU model, compiler or build flags stated (only a 2 vCPU/4GB ARM64 VM), so first-party with partial methodology = C.
- **Verifier notes:** Numbers verified verbatim in summary table (cases 4 and 6) and raw wrk appendices. Metadata checked via gh: 832 stars, not fork/archived, last commit 2026-06-12 (active), LICENSE text is MIT for Pipy. Only caveats/workload refined to reflect the less favorable rows.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/flomesh-io/pipy/wiki/BENCHMARK-:-Pipy-as-Echo-server>
  - <https://raw.githubusercontent.com/wiki/flomesh-io/pipy/BENCHMARK-:-Pipy-as-Echo-server.md>
  - <https://github.com/flomesh-io/pipy>
  - <https://github.com/flomesh-io/pipy/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/flomesh-io/pipy>
  - <https://github.com/flomesh-io/pipy/blob/main/README.md>
  - <https://github.com/flomesh-io/pipy/wiki>
  - <https://github.com/flomesh-io/pipy/wiki/BENCHMARK-:-Pipy-as-Echo-server>
  - <https://raw.githubusercontent.com/wiki/flomesh-io/pipy/BENCHMARK-:-Pipy-as-Echo-server.md>
  - <https://github.com/flomesh-io/pipy/wiki/BENCHMARK-:-Pipy-as-Echo-server/_history>
  - <https://raw.githubusercontent.com/wiki/flomesh-io/pipy/BENCHMARK-:-Pipy-0.90-Multi-Threads-HTTP1.1.md>
  - <https://raw.githubusercontent.com/wiki/flomesh-io/pipy/BENCHMARK-:-Pipy-sidecar-proxy-SpringBoot.md>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/cmake/compiler-options.cmake>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/build.sh>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/LICENSE>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/tutorial/01-hello/main.js>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/tutorial/02-echo/main.js>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/allocator.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/constants.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/data.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/scarce.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/net.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/main-options.cpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/main-options.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/worker-thread.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/worker-thread.cpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/listener.cpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/filters/http.cpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/pjs/pjs.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/pjs/types.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/pjs/expr.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/src/pjs/stmt.hpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/test/benchmark/baseline/main.cpp>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/intro/overview.mdx>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/intro/concepts.mdx>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/reference/pjs.mdx>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/reference/pjs/1-language.mdx>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/getting-started/build-install.mdx>
  - <https://raw.githubusercontent.com/flomesh-io/pipy/main/docs/guides/16-serve-static.mdx>
  - <https://github.com/flomesh-io/pipy/releases>
  - <https://github.com/flomesh-io/pipy/commits/main>
  - <https://github.com/flomesh-io/pipy/issues/172>
  - <https://github.com/flomesh-io/pipy/issues/187>
  - <https://github.com/flomesh-io/pipy/issues/200>
  - <https://github.com/flomesh-io/pipy/issues>
  - <https://nginx.org/en/docs/http/ngx_http_core_module.html>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=pipy>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=flomesh>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/flomesh-io/pipy`) · [data/wave5/enrich/raw/github_com_flomesh_io_pipy.json](../../../data/wave5/enrich/raw/github_com_flomesh_io_pipy.json) (enrichment confidence 0.8)

</details>
