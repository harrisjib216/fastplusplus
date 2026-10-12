# libevhtp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Archived C HTTP/1.1 server library on libevent; about 1.15x Boost.Beast's async example on one plaintext wrk test.

| | |
|---|---|
| **Beats** | Boost.Beast |
| **Claimed result** | libevhtp 1.2.18 (on libevent 2.1.12): 254k req/s vs Boost.Beast 1.83: 220k req/s, about 1.15x higher throughput (derived from page data). Both are below nginx (336k/s) and Drogon (320k/s) in the same table. |
| **Workload** | Single plaintext-response endpoint in a 4-core Docker environment, wrk -c1000 -t10 -d30s with HTTP keep-alive, client running on a 12-core AMD 7840HS host. |
| **Metric** | throughput |
| **Hardware** | 4-core Docker containers on a 12-core AMD 7840HS host, LinuxMint 22.3 / Ubuntu 24.04, Docker userland-proxy disabled |
| **Compiler and flags** | gcc -O2 (libevhtp server) and g++ -O2 (beast server), built in ubuntu:24.04 with build-essential per libevhtp/Dockerfile and beast/Dockerfile; compiler version not stated; no LTO. libevhtp 1.2.18 and libevent 2.1.12 are Ubuntu's prebuilt apt packages (libevhtp-dev, libevent-dev), so the library build flags are Ubuntu's. |
| **Adoption** | 456 stars |
| **Last commit** | 2019-08-02 |
| **Links** | [repository](https://github.com/Yellow-Camper/libevhtp) · [benchmark](https://github.com/gonwan/webframework-benchmark) |

## Verdict

One homemade wrk run (-c1000 -t10 -d30s, keep-alive, GET /text returning 'Hello, World!') against 4-CPU-limited Docker containers on an AMD 7840HS host measured the Ubuntu-packaged libevhtp 1.2.18 on libevent 2.1.12 (4 workers plus a listener) at 254k req/s. On the same setup the Boost 1.83 Beast http_server_async example measured 220k req/s. Both test servers were built with gcc/g++ -O2 from ubuntu:24.04 build-essential. The Beast example runs 4 threads on one shared io_context with per-connection strands, so part of the 1.15x gap may come from how that example is set up.

## Use it when

- A C program already built around a libevent event_base needs an embedded HTTP/1.1 endpoint, such as an admin, metrics or small REST API.
- Many keep-alive connections get small fixed responses on a few cores: the benchmark measured 254k req/s on 4 cores against 220k for the Beast async example.
- Handlers can keep all per-connection work on the worker thread that owns the connection, like examples/thread_design.c does with async Redis on each worker's event_base.
- You are willing to vendor and patch a frozen, BSD-3-Clause codebase of about 8.3k lines (evhtp.c, parser.c, thread.c). On Ubuntu 24.04, libevhtp-dev 1.2.18 also installs from apt.

## Skip it when

- You need HTTP/2, WebSocket or server-sent events: evhtp_proto has only HTTP/1.0 and 1.1, WebSocket support was never merged (#116), and the SSE question (#166) has no answer.
- The server faces the internet without a hardened proxy in front. The repo is archived, so no security fixes will come. Parser issues are still open: #131, a URI split across two reads gains a stray character; #161, an invalid Content-Length gets an empty reply.
- You serve HTTPS with real response bodies: #160 (open) reports 42,484 req/s falling to 1,012 req/s after adding an 11-byte body over TLS, and a fragmented output buffer is the suspected cause.
- You want the highest throughput: in the same table nginx (336k), actix (334k), Drogon (320k) and gofiber with GOMAXPROCS=4 (272k) beat libevhtp, and bun ties it at 254k.
- You want idiomatic, header-only C++ with Asio integration, or you target Windows: MinGW build steps are in the README, but Windows build issues #103, #141 and #142 are still open.

## How it is fast

evhtp_use_threads_wexit() starts evthr workers, each running its own libevent event_base; the listener thread passes each accepted connection over an AF_UNIX socketpair to the worker with the smallest FIONREAD backlog, so a connection stays on one thread and takes no locks. Requests go through htparse, a byte-at-a-time state machine that checks URI characters against a 256-bit bitmap (usual[]) and acts on Connection, Content-Length and Transfer-Encoding while it parses the headers. Replies build the status line and headers with scatter-gather evbuffer iovecs and custom integer-to-ASCII code instead of printf formatting (tagged [PERF] in the ChangeLog). The benchmark server also set EVHTP_FLAG_ENABLE_ALL, which turns on SO_REUSEPORT, TCP_NODELAY and TCP_DEFER_ACCEPT.

## Compared with alternatives

Drogon is faster in the same gonwan table (320k vs 254k req/s) and gives a full C++ framework, so choose libevhtp over Drogon only when you need a plain C API that plugs into an existing libevent event_base. For a new C server, the H2O and Lwan entries have stronger published benchmarks and do not depend on an archived library.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake add_library; distro packages ship a shared lib) |
| **Dependencies** | libevent 2.x (required). Optional: OpenSSL (TLS), pthreads (evthr thread pool), Oniguruma with its POSIX API (regex routes), jemalloc or tcmalloc (EVHTP_ALLOCATOR). |
| **Minimum toolchain** | C99 gcc or clang, CMake 3.1+. The 1.2.18 CMakeLists calls find_package(LibEvent), which misses the CMake config of a self-built libevent 2.1.8 (#135). |
| **Platforms** | Linux and other POSIX systems (pthreads, AF_UNIX socketpairs, ioctl FIONREAD). No SIMD or architecture-specific code. Windows only via MinGW, with open build issues. |
| **Thread safety** | Each connection is pinned to one evthr worker and its event_base, so reply from that thread. Replying from another thread aborts under load (#139). evhtp_use_callback_locks() adds a mutex for changing callbacks and hooks at runtime. |
| **Drop-in for the baseline** | no |

## Gotchas

- Tag 1.2.18 (2019-02-06) is the version Ubuntu ships and the one benchmarked. It predates the develop-branch fixes for bytes skipped in long URIs (#128), and #131 reports that the develop fix adds a stray character instead. Pin a version and test long, fragmented request lines.
- By default there are no read/write timeouts and no body-size cap (max_body_size 0 means unlimited). Set evhtp_set_timeouts and evhtp_set_max_body_size, or slow or huge requests hold connections.
- EVHTP_FLAG_DEFAULTS turns on only 100-continue. SO_REUSEPORT, TCP_NODELAY and TCP_DEFER_ACCEPT stay off unless you enable them, and the benchmark enabled all of them.
- Regex routes need Oniguruma built with --enable-posix-api=yes for onig 6.9.5_rev1 and later (#162). Otherwise CMake prints 'ONIGURUMA NOT FOUND, DISABLING REGEX SUPPORT' and builds without regex routes. evhtp_use_threads() is marked DEPRECATED in favor of evhtp_use_threads_wexit().

## Known shortcomings

- Only evidence is a 0-star personal benchmark suite (gonwan/webframework-benchmark): 254k vs 220k req/s against Boost.Beast 1.83, about 1.15x, gcc -O2 with no compiler version.
- Archived with no maintained fork. The benchmarked 1.2.18 tag predates the long-URI parser fix (#128), and the develop fix adds a stray byte when a URI spans two reads (#131). Invalid Content-Length gets an empty reply (#161); cross-thread replies abort under load (#139); TLS with tiny bodies falls from 42,484 to 1,012 req/s (#160). No timeouts or body cap by default; the benchmark enabled every flag (SO_REUSEPORT, TCP_NODELAY, TCP_DEFER_ACCEPT). HTTP/1.x only. Build issues with self-built libevent and Oniguruma. The Beast baseline is the async example on one shared io_context, and libevhtp loses to nginx, actix, Drogon and gofiber in the same table.

## Caveats and trade-offs

Single-author homemade third-party benchmark (0-star repo gonwan/webframework-benchmark, Feb-Mar 2026), not independently reviewed; one wrk result per server, with no repeats or variance. Compiler version is not stated (ubuntu:24.04 build-essential, -O2), and libevhtp/libevent are distro-built binaries. The beast server is the Boost 1.83 http_server_async example: 4 threads share one io_context with per-connection strands, while libevhtp runs 4 worker threads plus a listener thread; the author says beast scaled poorly in an earlier run. The page says '12C host machine, AMD 7840HS', but the 7840HS is an 8-core/16-thread part, so the host core count is unclear. The gain is small (about 1.15x). libevhtp is archived, and its last commit is 2019-08-02.

C API (needs a C++ wrapper for idiomatic use); depends on libevent; archived by GitHub as read-only.

## Maintenance

The repo is archived and read-only: last commit 2019-08-02, last tag 1.2.18. The original author's fork (ellzey/libevhtp) only merged upstream in 2025 and added no fixes. The BSD-3-Clause license and small C codebase make it practical to vendor and patch, but you would own every security fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The gonwan/webframework-benchmark readme table has libevhtp 1.2.18 / libevent 2.1.12 at 254k/s and Boost.Beast 1.83 at 220k/s. The code is public (libevhtp/libevhtp_server.c, beast/beast_server.cpp, their Dockerfiles, docker-compose.yml), the flags are gcc/g++ -O2 and the CPU is an AMD 7840HS. It is not A: no compiler version is stated (only the ubuntu:24.04 build-essential base image), and it is not B: it is a 0-star homemade suite, not a well-known one.
- **Verifier notes:** The numbers and the Beast comparison check out. The only substantive fix: flags are stated in the Dockerfiles (-O2), not missing as the record said. The license (BSD-3-Clause), 456 stars, archived status, last commit 2019-08-02 and the 1.2.18 tag all match gh. The readme numbers have been stable since commit 21f8cbf (2026-03-07).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gonwan/webframework-benchmark>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/readme.md>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/docker-compose.yml>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/package_all.sh>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/Dockerfile>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/package.sh>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/libevhtp_server.c>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/Dockerfile>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/package.sh>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/beast_server.cpp>
  - <https://github.com/gonwan/webframework-benchmark/commits/main>
  - <https://github.com/Yellow-Camper/libevhtp>
  - <https://github.com/Yellow-Camper/libevhtp/commits/develop>
  - <https://github.com/Yellow-Camper/libevhtp/tags>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/README.md>
- **Sources the enricher read:**
  - <https://github.com/Yellow-Camper/libevhtp>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/README.md>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/CMakeLists.txt>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/cmake/options.cmake>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/.travis.yml>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/ChangeLog>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/include/evhtp/evhtp.h>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/include/evhtp/thread.h>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/include/evhtp/parser.h>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/evhtp.c>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/parser.c>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/thread.c>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/examples/thread_design.c>
  - <https://github.com/Yellow-Camper/libevhtp/blob/develop/examples/example_locality.c>
  - <https://github.com/Yellow-Camper/libevhtp/issues?q=is%3Aissue>
  - <https://github.com/Yellow-Camper/libevhtp/issues/41>
  - <https://github.com/Yellow-Camper/libevhtp/issues/116>
  - <https://github.com/Yellow-Camper/libevhtp/issues/128>
  - <https://github.com/Yellow-Camper/libevhtp/issues/131>
  - <https://github.com/Yellow-Camper/libevhtp/issues/133>
  - <https://github.com/Yellow-Camper/libevhtp/issues/135>
  - <https://github.com/Yellow-Camper/libevhtp/issues/139>
  - <https://github.com/Yellow-Camper/libevhtp/issues/160>
  - <https://github.com/Yellow-Camper/libevhtp/issues/161>
  - <https://github.com/Yellow-Camper/libevhtp/issues/162>
  - <https://github.com/Yellow-Camper/libevhtp/commits/develop>
  - <https://github.com/Yellow-Camper/libevhtp/tags>
  - <https://github.com/Yellow-Camper/libevhtp/compare/1.2.18...develop>
  - <https://github.com/Yellow-Camper/libevhtp/forks>
  - <https://github.com/ellzey/libevhtp>
  - <https://github.com/ellzey/libevhtp/commits/develop>
  - <https://github.com/gonwan/webframework-benchmark>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/readme.md>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/docker-compose.yml>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/libevhtp_server.c>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/Dockerfile>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/libevhtp/package.sh>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/beast_server.cpp>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/Dockerfile>
  - <https://github.com/gonwan/webframework-benchmark/blob/main/beast/package.sh>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=libevhtp>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=evhtp>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/yellow-camper/libevhtp`) · [data/wave5/enrich/raw/github_com_yellow_camper_libevhtp.json](../../../data/wave5/enrich/raw/github_com_yellow_camper_libevhtp.json) (enrichment confidence 0.35)

</details>
