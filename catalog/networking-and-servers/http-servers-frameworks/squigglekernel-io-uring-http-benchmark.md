# uhttp (io_uring-http-benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Single-route io_uring static HTTP server in C++20; 40-54% more req/s than tuned nginx serving one 10 KB file on loopback.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | 40-54% more requests/sec than tuned nginx at the same connection counts (64 conns: 358,428 vs 256,046 req/s = +40%; 1024 conns: 315,095 vs 204,644 = +54%; 4096 conns: 276,195 vs 184,395 = +50%); 28-34% less CPU per request (5.8-7.5us vs nginx's 8.1-11.1us); half the instructions per request (17,583 vs 35,831) (verbatim from README table) |
| **Workload** | Serving a single 10,240-byte static HTML file over loopback on 2 physical cores; wrk from 6 separate client cores, 45s runs x3 repetitions, interleaved targets, at 64/256/1024/4096 connections, plus perf-measured instructions/cycles/IPC per request. |
| **Metric** | throughput |
| **Hardware** | Unspecified 'mobile CPU' with SMT (physical cores 0,2,...,14 per bench/run_bench.py, i.e. 8 physical cores); server on 2 physical cores (0,2), wrk on 6 client cores (4-14); exact CPU model not stated; kernel built with CONFIG_INIT_ON_ALLOC_DEFAULT_ON=y; loopback only |
| **Compiler and flags** | CMake Release (Ninja) with explicit Release flags from CMakeLists.txt: -O3 -march=native -fno-plt -fno-semantic-interposition, plus LTO (INTERPROCEDURAL_OPTIMIZATION_RELEASE when supported); needs liburing &gt;= 2.5 and a C++20 compiler; compiler name/version not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/SquiggleKernel/io_uring-http-benchmark) · [benchmark](https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/README.md) |

## Verdict

On loopback, with 2 server workers pinned to 2 physical cores of an unnamed 8-core SMT 'mobile CPU' and wrk on the other 6, uhttp served a 10,240-byte file at 276-358k req/s against 184-256k for tuned nginx (reuseport, sendfile on or off, open_file_cache, logging off, same cores), +40% to +54% at 64-4,096 connections, as medians of 3 interleaved 45 s runs after a 15 s warmup. The build was CMake Release (-O3 -march=native, LTO) on a kernel with CONFIG_INIT_ON_ALLOC_DEFAULT_ON=y; compiler, kernel, nginx and wrk versions are not stated, and the raw CSVs are gitignored, so only the README's medians are published.

## Use it when

- Learning or prototyping io_uring networking: a small C++20 codebase (about 1,400 lines in src/) that shows multishot accept/recv, provided buffer rings, direct descriptors, DEFER_TASKRUN and generation-tagged user_data for recycled descriptor slots.
- Measuring io_uring against nginx on your own kernel and hardware: the harness interleaves targets, gives the client 3x the server's cores, flags client-bound runs and reports server CPU microseconds per request.
- A synthetic load-test target that must return one small fixed response at very high request rates on Linux 6.1+ where you control both ends.
- Ablation studies: structural io_uring options are compile-time switches in src/config.hpp and bench/ablation.sh rebuilds and measures each one.

## Skip it when

- Serving a real site or directory: one route, one file read at startup, GET only, exact path match (a query string gets 404), no MIME mapping, index files, Range or conditional requests.
- Anything that needs TLS, HTTP/2 or HTTP/3, request bodies, access logging, config reload, IPv6 (the listener is AF_INET only) or idle/read timeouts; none are implemented, so idle or slow clients hold connection slots (default 4,096 per worker) indefinitely.
- Shipping or vendoring code: there is no LICENSE file, and the repo has two commits (both 2026-08-17), no tests, no CI and 0 stars.
- Low-concurrency tail-latency work: nginx had the better p99 at 64 connections (333 us vs 360 us).
- As evidence that io_uring beats sendfile on a real network: every number is loopback, where nginx's sendfile zero-copy path gives no benefit, and the author says the NIC case was not tested.

## How it is fast

Shared-nothing worker threads each own one io_uring ring (SINGLE_ISSUER + DEFER_TASKRUN, registered ring fd, CQ 4x the SQ) and use multishot accept into direct (fixed-file) descriptors plus multishot recv over a provided buffer ring, so a connection is accepted and read repeatedly without new submissions and completions are drained and acknowledged in batches. Each response is pre-serialised into one buffer, kept as two copies so only the Date field is patched once a second; SO_REUSEPORT with a classic-BPF steering program keeps each connection on the core that handled its SYN; and per-connection state is a packed 20-byte struct. perf puts syscall entry/exit at 0.07% of uhttp's cycles against 8.71% for nginx, and instructions per request at 17,583 vs 35,831. nginx still has the higher IPC (0.86 vs 0.64), so the author's own summary is that the gain comes from doing less work, not from doing it faster.

## Compared with alternatives

Pick it over epoll-httpd when the question is specifically io_uring versus nginx's epoll model at 64-4,096 connections with perf-level attribution; epoll-httpd is the better base for real code because it is MIT-licensed and serves arbitrary files. For serving actual traffic, use H2O (static files, TLS, HTTP/2/3) or Sogou Workflow (C++ backend) instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | liburing (CMake asks for &gt;= 2.5, but the code needs 2.6; see gotchas), pkg-config, CMake &gt;= 3.20; wrk, nginx, perf and Python 3 only for the benchmark harness |
| **Minimum toolchain** | C++20 compiler (make_unique_for_overwrite, std::span), CMake 3.20; compiler and version not documented. Kernel minimum not documented; the default ring flags need DEFER_TASKRUN (Linux 6.1+), or 6.0+ with --no-defer |
| **Platforms** | Linux only (io_uring, SO_ATTACH_REUSEPORT_CBPF); the Release build uses -march=native, so binaries are tied to the build CPU |
| **Thread safety** | Not a library. Each worker thread owns its ring, connection table and buffers; the only shared state is an atomic stop flag |
| **Drop-in for the baseline** | no |

## Gotchas

- Build floor is wrong: CMakeLists.txt accepts liburing &gt;= 2.5, but server.cpp calls io_uring_register_napi(), which first appears in liburing 2.6's header (the 2.6 CHANGELOG adds NAPI busy-poll support), so a build against 2.5 should fail to compile.
- Pipelining is capped at 32 queued responses per connection. From reading server.cpp, bytes beyond that are carried over and only parsed when the next recv completes, so a client that pipelines more than 32 requests in one write and then waits for all of them can stall.
- It sends ETag, Last-Modified and 'Accept-Ranges: bytes' to match nginx's headers, but ignores If-None-Match, If-Modified-Since and Range and always returns a full 200. The file is never re-read, so edits need a restart.
- The harness's `sudo bench/tune_system.sh apply` sets kernel.perf_event_paranoid=-1 and kernel.kptr_restrict=0 system-wide (plus the performance governor and larger backlogs) until you run `restore`.

## Known shortcomings

- A benchmark server, not a library: serves one route from memory; nginx has the better p99 at 64 connections. No licence (reference only).
- No LICENSE file (reference only); two commits on 2026-08-17, no tests or CI. CMake accepts liburing 2.5 but the code calls io_uring_register_napi(), which needs 2.6; DEFER_TASKRUN needs Linux 6.1+ (undocumented). More than 32 pipelined requests in one write may stall (code reading). ETag/Last-Modified/Accept-Ranges are sent but conditional and Range requests are ignored; the file is read once at startup. Serves GET on one exact path, IPv4 only, no timeouts, TLS, HTTP/2, bodies or logging. Loopback-only numbers without CPU, compiler, kernel, nginx or wrk versions; raw CSVs gitignored; -march=native; results bimodal run to run (\~350k vs \~389k). bench/tune_system.sh lowers perf_event_paranoid and kptr_restrict system-wide until restored. nginx has the better p99 at 64 connections and higher IPC.

## Caveats and trade-offs

No LICENSE file in the repo (GitHub license API returns 404), so usability=reference despite public code. Exact CPU model and compiler are not stated (only 'mobile CPU'), so this is capped at Tier C even though methodology (warmup, 45 s x3 repetitions, interleaving, client-saturation checks, perf counters) is unusually rigorous for a first-party repo. Loopback only: the author says not to read it as 'io_uring beats sendfile on a real network'. uhttp serves one route from memory while nginx is a general-purpose server, and the author says some of the 2x instruction gap comes from that generality. nginx wins p99 latency at 64 connections (333 us vs 360 us). -march=native build. Per-feature attribution is inside the 3.4% noise floor; send_zc loses 6.6% at this payload size.

Serves exactly one static route from memory (not general-purpose like nginx); no TLS/HTTP2/CGI; loopback-only benchmark so sendfile's zero-copy advantage on real NICs was not tested; author explicitly documents nginx wins the p99 latency tail at low connection counts and that per-feature attribution of the io_uring gains is unresolved.

## Maintenance

A one-shot research dump (two commits on 2026-08-17, none since, no issues, releases or stars) with no LICENSE file, so it is reference-only: read it to learn the io_uring techniques, but do not copy or vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Results and perf tables compare uhttp against tuned nginx (bench/nginx.conf, harness bench/run_bench.py) and hold every quoted rps, percentage, us/request and instruction count. Flags are explicit in CMakeLists.txt, but no compiler is named and the CPU is only 'a mobile CPU', so not A; first-party, so C.
- **Verifier notes:** All claimed_speedup numbers match the README verbatim. compiler_and_flags was wrong: CMakeLists.txt sets explicit Release flags (-O3 -march=native -fno-plt -fno-semantic-interposition) plus LTO, so corrected. Hardware core layout added from bench/run_bench.py comments; license, stars and last commit (2026-08-17) confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/README.md>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/run_bench.py>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/tune_system.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/profile.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/ablation.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/nginx.conf>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/config.hpp>
- **Sources the enricher read:**
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/README.md>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/.gitignore>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/config.hpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/conn.hpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/util.hpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/server.hpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/server.cpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/http.hpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/http.cpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/src/main.cpp>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/run_bench.py>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/nginx.conf>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/ablation.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/profile.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/tune_system.sh>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/gen_payload.py>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/blob/main/bench/wrk_report.lua>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/commits/main>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark/issues>
  - <https://api.github.com/repos/SquiggleKernel/io_uring-http-benchmark/license>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_setup.2>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_recv.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_accept.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_setup_buf_ring.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_register_ring_fd.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_register_napi.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_send_zc.3>
  - <https://github.com/axboe/liburing/blob/master/CHANGELOG>
  - <https://github.com/axboe/liburing/blob/liburing-2.5/src/include/liburing.h>
  - <https://github.com/axboe/liburing/blob/liburing-2.6/src/include/liburing.h>
  - <https://hn.algolia.com/api/v1/search?query=io_uring-http-benchmark>
  - <https://hn.algolia.com/api/v1/search?query=SquiggleKernel>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/squigglekernel/io_uring-http-benchmark`) · [data/wave5/enrich/raw/github_com_squigglekernel_io_uring_http_benchmark.json](../../../data/wave5/enrich/raw/github_com_squigglekernel_io_uring_http_benchmark.json) (enrichment confidence 0.75)

</details>
