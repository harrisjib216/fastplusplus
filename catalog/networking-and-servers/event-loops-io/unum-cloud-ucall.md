# UCall (formerly ujrpc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> JSON-RPC 2.0 server library in C++ with C and Python APIs; io_uring backend beats FastAPI/uvicorn on small-call latency and throughput.

| | |
|---|---|
| **Beats** | epoll |
| **Claimed result** | README table: UCall io_uring (C server, connection reused) 22us / 231,000 rps vs FastAPI over REST (no connection reuse) 1,203us / 3,184 rps (\~55x latency, \~72x throughput, derived from page data). Vs FastAPI over WebSocket (connection reused) 86us / 11,356 rps: \~3.9x latency, \~20x throughput (derived from page data). A closer like-for-like pair is UCall io_uring with a Python server, at 40us / 210,000 rps: \~2.2x latency and \~18x throughput vs FastAPI WebSocket (derived from page data). |
| **Workload** | JSON-RPC 'sum' call over a persistent TCP connection; latency measured with 1 client, throughput with 32 concurrent client processes on AWS c7g.metal (Graviton3) |
| **Metric** | throughput, latency |
| **Hardware** | AWS c7g.metal (Graviton 3), Ubuntu 22.10 AMI, Linux kernel 5.19; throughput clients run on the same machine as the server |
| **Compiler and flags** | CMake Release build with -O3 (CMakeLists.txt default). The compiler version is not stated; the reproduce steps in examples/login/README.md install g++ via apt. FastAPI/uvicorn versions are not stated. |
| **Adoption** | 1.3k stars |
| **Last commit** | 2025-09-16 |
| **Links** | [repository](https://github.com/unum-cloud/UCall) · [benchmark](https://github.com/unum-cloud/UCall/blob/main/README.md) |

## Verdict

The README table was measured in early 2023 on AWS c7g.metal (Graviton3), Ubuntu 22.10, Linux 5.19, with client processes on the same machine; examples/bench.py is the repo's Python harness. For a trivial 'sum' call, the C io_uring server does 22 us with one client and 231k rps with 32 clients. FastAPI/uvicorn does 1,203 us / 3,184 rps over REST (no connection reuse) and 86 us / 11,356 rps over WebSocket. The like-for-like, connection-reusing comparison is therefore about 3.9x latency and 20x throughput, not the 55x/72x headline. The build is CMake Release -O3; compiler, FastAPI and uvicorn versions are not stated.

## Use it when

- Very small, high-rate RPC calls (parameters and replies well under the 4 KiB per-connection fast-path buffer) where per-call overhead is most of the cost, such as internal lookup or scoring endpoints
- You control the clients and can speak JSON-RPC 2.0 over persistent TCP or HTTP/1.1 connections, which is the setup where the io_uring engine posts its 22 us / 231k rps numbers
- Linux 5.19+ hosts (the io_uring engine needs IORING_OP_SOCKET and accept_direct) where you can dedicate cores to busy-polling and the SQPOLL thread
- Exposing cheap Python or C functions (the README's 'sum'-style endpoints) with far less serving overhead than FastAPI/uvicorn
- Embedding a small JSON-RPC endpoint in a C/C++ service without taking on gRPC or protobuf tooling

## Skip it when

- Handlers that do heavy work, like model inference: serving overhead is noise there. Issue #108 measured flan-t5 behind UCall and FastAPI at about the same speed, and the maintainer confirmed that outcome is expected
- You need TLS on the io_uring engine (only the POSIX engine links mbedTLS, and open PR #100 proposes dropping TLS), HTTP/2, WebSockets, REST routing or IPv6 (both engines bind AF_INET only)
- You need concurrency off Linux 5.19+: the POSIX engine forces one thread, one connection at a time and one request per connection, using blocking accept/recv
- Production reliability matters. Open issue #94 reports the io_uring example hanging or core-dumping under wrk on kernels 6.0 and 6.5, and its fix (PR #104, a zero-length send completion confusing the state machine) was never merged. Open issue #106 reports release-build throughput far below the README
- Idle-CPU-sensitive or shared hosts: ucall_take_calls is an infinite busy loop with no shutdown path in the C API, and SQPOLL adds a spinning kernel thread

## How it is fast

The Linux engine is a completion-driven io_uring state machine. It uses an SQPOLL kernel submission thread, direct descriptors (io_uring_prep_socket_direct, accept_direct and register_files_sparse), read_fixed into pre-registered 4 KiB input and output buffers per connection, linked timeouts on receives, and send_zc on kernels that support it (6.0+). Request bodies are parsed with simdjson's DOM parser, preallocated per thread and helped by buffer padding that avoids copies. HTTP headers go through picohttpparser, and replies are written into preallocated per-connection buffers without heap allocation on the small-message path. Worker threads busy-poll the completion queue instead of sleeping. Most of the headline gap over FastAPI comes from removing the Python/ASGI stack. UCall's own io_uring backend beats its blocking POSIX backend by about 2.8x (22 vs 62 us, 231k vs 79k rps).

## Compared with alternatives

Pick UCall over uWebSockets or libhv only when a bare JSON-RPC endpoint with batch calls, callable from C or Python, is all you need and you run Linux 5.19+. Those two are more general, more maintained HTTP/WebSocket servers with TLS and portable event loops. monoio, aquatic and io_uring-echo-server are runtimes or single-purpose servers rather than RPC frameworks.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake FetchContent; separate ucall_server_uring / ucall_server_posix libraries) or Python wheel (pip install ucall) |
| **Dependencies** | simdjson v3.1.6, liburing 2.3 (Linux), mbedTLS 3.4.0 (POSIX engine), unum-cloud forks of picohttpparser and Turbo-Base64, and cxxopts for the examples, all fetched by CMake. The Python package also needs numpy and pillow |
| **Minimum toolchain** | C++17 (C99 header), CMake 3.20+ (pyproject asks for 3.22), built with -fno-exceptions. The io_uring engine needs Linux kernel 5.19+. Wheels need Python 3.9+ |
| **Platforms** | io_uring engine: Linux only (x86-64 and aarch64 wheels). POSIX engine: Linux, macOS (x86-64/arm64) and Windows (winsock, AMD64 wheel). IPv4 only |
| **Thread safety** | io_uring engine: one shared ring guarded by spinlocks. Up to max_threads threads may each call ucall_take_calls with a unique thread_idx, and only thread 0 accepts connections. The POSIX engine forces max_threads=1. Python's run() drives only thread 0, and callbacks run under the GIL |
| **Drop-in for the baseline** | false — it speaks a different protocol (JSON-RPC 2.0 envelopes, no REST routes, pydantic validation, OpenAPI or middleware). The Python decorator looks similar, but clients have to change |

## Gotchas

- The C API's io_uring defaults close a connection after 100 request/response exchanges (max_lifetime_exchanges=100) and cap connections at 1024, dismissing any beyond that. The shipped examples and the Python binding raise the exchange limit to UINT32_MAX. max_lifetime_micro_seconds is stored but never read
- Each connection has fixed 4 KiB input and output buffers. Bodies larger than a page fall off the fast path to dynamic allocation plus a fresh simdjson parser per request. Python handlers that return non-JSON-native objects get a JSON-RPC 'Out of memory' error (issue #89), and dict/list parameters are rejected (issue #111)
- ucall_add_procedure silently ignores registrations past max_callbacks-1, and method dispatch is a linear scan of the callback array
- PyPI still ships 0.5.4 (March 2024) while GitHub is at v0.5.8. The README's reproduce link (tree/dev/examples/sum) is dead, and the benchmark code now lives in examples/login

## Known shortcomings

- The \~55x/\~72x headline compares UCall reusing connections against FastAPI REST, which does not; the fairer WebSocket pair gives about 3.9x latency and 20x throughput. The README's reproduce link is dead and the measured example was refactored. C++ engines behind a C API. Stale since 2025-09.
- Open issue #94: the io_uring example hangs or core-dumps under wrk on kernels 6.0/6.5 (fix PR #104 unmerged). Open issue #106 reports Release builds at about 1.7k rps, far below the README, with no maintainer reply. io_uring engine has no TLS and is IPv4 only; the POSIX engine is blocking, one connection at a time. Connections close after 100 exchanges by default. PyPI lags GitHub tags; a redesigned v1 has not shipped. Enrichment confidence 0.40.

## Caveats and trade-offs

Cross-language, cross-framework comparison (C or Python-bound UCall vs a Python FastAPI/uvicorn app), not a controlled event-loop shootout. The \~55x/\~72x headline pairs a connection-reusing UCall server with FastAPI REST, which does not reuse connections. The like-for-like WebSocket pair gives \~3.9x latency and \~20x throughput. The numbers date from Feb-Mar 2023 and were measured on a 'sum' endpoint. That example was refactored into examples/login on 2023-03-21, and the README's reproduce link (tree/dev/examples/sum) is now dead. A cleaner internal comparison is UCall's POSIX backend (src/engine_posix.cpp: blocking accept/recv, no epoll) at 62us / 79,000 rps vs the io_uring backend at 22us / 231,000 rps (\~2.8x). That baseline is blocking sockets, not epoll.

io_uring path requires Linux 5.19+; POSIX/epoll fallback available on older kernels; project has been renamed (ujrpc -&gt; UCall) and appears to have slowed down; small pet-project scale (a few thousand LOC) vs mature frameworks like FastAPI/gRPC

## Maintenance

Stale: the last commit (2025-09-16, v0.5.8) was a logging and docs change, the maintainer points users to a redesigned v1 that has not shipped, and known io_uring bugs are still open with their fix unmerged. It is Apache-2.0 and only a few thousand lines of core code, so it is small enough to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party README table has FastAPI (REST and WebSocket), gRPC and UCall rows on AWS c7g.metal (Graviton 3), and all the quoted numbers appear there. The code is public (examples/login/\*, examples/bench.py) and CMakeLists.txt sets Release -O3. The compiler version is not stated, the README's reproduce link (tree/dev/examples/sum) is dead, and the measured 'sum' example was later refactored into examples/login, so the record falls short of A.
- **Verifier notes:** The numbers are exact and the ratios check out (1203/22 = 54.7x, 231000/3184 = 72.5x, 86/22 = 3.9x, 231000/11356 = 20.3x). The record's language 'C' is loose: the engines are C++ (src/engine_posix.cpp, src/engine_uring.cpp) behind a C API, plus Python bindings. Metadata is correct: Apache-2.0, 1334 stars, last commit 2025-09-16 (just over 12 months ago, so stale), not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/unum-cloud/ucall>
  - <https://github.com/unum-cloud/ucall/blob/main/README.md>
  - <https://github.com/unum-cloud/ucall/tree/main/examples>
  - <https://github.com/unum-cloud/ucall/tree/main/examples/login>
  - <https://github.com/unum-cloud/ucall/blob/main/examples/login/README.md>
  - <https://github.com/unum-cloud/ucall/blob/main/examples/bench.py>
  - <https://github.com/unum-cloud/ucall/blob/main/CMakeLists.txt>
  - <https://github.com/unum-cloud/ucall/blob/main/src/engine_posix.cpp>
  - <https://github.com/unum-cloud/ucall/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/unum-cloud/ucall>
  - <https://github.com/unum-cloud/ucall/blob/main/README.md>
  - <https://github.com/unum-cloud/ucall/blob/main/include/ucall/ucall.h>
  - <https://github.com/unum-cloud/ucall/blob/main/include/ucall/README.md>
  - <https://github.com/unum-cloud/ucall/blob/main/CMakeLists.txt>
  - <https://github.com/unum-cloud/ucall/blob/main/pyproject.toml>
  - <https://github.com/unum-cloud/ucall/blob/main/src/engine_uring.cpp>
  - <https://github.com/unum-cloud/ucall/blob/main/src/engine_posix.cpp>
  - <https://github.com/unum-cloud/ucall/blob/main/src/helpers/parse.hpp>
  - <https://github.com/unum-cloud/ucall/blob/main/src/helpers/shared.hpp>
  - <https://github.com/unum-cloud/ucall/blob/main/src/python.c>
  - <https://github.com/unum-cloud/ucall/blob/main/src/ucall/_server.py>
  - <https://github.com/unum-cloud/ucall/blob/main/examples/login/README.md>
  - <https://github.com/unum-cloud/ucall/blob/main/examples/login/ucall_server.cpp>
  - <https://github.com/unum-cloud/ucall/blob/main/examples/bench.py>
  - <https://github.com/unum-cloud/ucall/blob/main/docs/benchmarks.rst>
  - <https://github.com/unum-cloud/ucall/issues>
  - <https://github.com/unum-cloud/ucall/issues/89>
  - <https://github.com/unum-cloud/ucall/issues/94>
  - <https://github.com/unum-cloud/ucall/issues/106>
  - <https://github.com/unum-cloud/ucall/issues/107>
  - <https://github.com/unum-cloud/ucall/issues/108>
  - <https://github.com/unum-cloud/ucall/issues/111>
  - <https://github.com/unum-cloud/ucall/pulls>
  - <https://github.com/unum-cloud/ucall/pull/100>
  - <https://github.com/unum-cloud/ucall/pull/104>
  - <https://github.com/unum-cloud/ucall/commits/main>
  - <https://github.com/unum-cloud/ucall/releases>
  - <https://pypi.org/pypi/ucall/json>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/unum-cloud/ucall`) · [data/wave5/enrich/raw/github_com_unum_cloud_ucall.json](../../../data/wave5/enrich/raw/github_com_unum_cloud_ucall.json) (enrichment confidence 0.4)

</details>
