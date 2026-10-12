# rest_rpc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 coroutine RPC over raw TCP; its 2019 C++11 version beat brpc 1.2-1.9x on same-machine echo.

| | |
|---|---|
| **Beats** | brpc (Apache bRPC); gRPC only transitively, via brpc's own benchmark page |
| **Claimed result** | Higher QPS than brpc on a same-machine echo test. Single-thread client: 52631 vs 41667 QPS at 1K (\~1.26x), \~1.24x at 8K, \~1.26x at 16K, 16949 vs 8982 at 64K (\~1.89x). Multi-thread 1K: 200000 vs 103448 at 6 threads (\~1.93x), \~1.50x at 10, \~1.19x at 20. Multi-thread 64K: \~1.72x/1.92x/1.69x at 6/10/20 threads (ratios derived from page data). The page says rest_rpc is almost 2x brpc at 64K. The README's 'far exceeds gRPC' is not measured anywhere; it rests on brpc's own benchmark ranking gRPC last. |
| **Workload** | Echo RPC with client and server on one bare-metal machine. The client loops sending 1K/8K/16K/64K strings of 'A', and the server echoes them back with no processing. Server threads equal CPU cores; clients ran single-threaded and with 6/10/20 threads. QPS is the average of several runs. This tested the 2019 C++11 rest_rpc (now the cpp11 branch), not the current C++20 master. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-9400F @ 2.90GHz (6 cores), 16 GB RAM, Ubuntu 18.04.1, bare metal; client and server on the same machine |
| **Compiler and flags** | g++ (Ubuntu 8.2.0-1ubuntu2\~18.04) 8.2.0; both projects built with cmake -DCMAKE_BUILD_TYPE=Release (explicit flags not listed) |
| **Adoption** | 2.0k stars |
| **Last commit** | 2026-06-23 |
| **Links** | [repository](https://github.com/qicosmos/rest_rpc) · [benchmark](https://github.com/qicosmos/rest_rpc/blob/cpp11/doc/%E5%8D%95%E6%9C%BA%E4%B8%8Arest_rpc%E5%92%8Cbrpc%E6%80%A7%E8%83%BD%E6%B5%8B%E8%AF%95.md) |

## Verdict

A 2019 first-party doc on the cpp11 branch tested the old C++11 rest_rpc against Apache brpc with echoes of 1K-64K strings, client and server on one i5-9400F 6-core machine (Ubuntu 18.04, g++ 8.2.0, CMake Release). With a single-thread client rest_rpc got 52,631 vs 41,667 QPS at 1K (\~1.26x) and 16,949 vs 8,982 at 64K (\~1.89x); with 6-20 client threads, in an undefined 'high-efficiency mode', it was 1.19-1.93x. Elapsed time was measured in whole seconds (200,000 QPS works out to 600,000 calls in 3 s), the benchmark code exists only as partial snippets, current master has no comparative numbers, and the README's 'far exceeds gRPC' was never measured.

## Use it when

- Both client and server are C++20 code you own, and you want to turn existing functions into RPCs without .proto files, codegen or a build step.
- Trusted-LAN or same-host links that move large strings or blobs, where passing `std::string_view` avoids serialization and copies (the README says multi-GB payloads are sent this way).
- Internal tools, test harnesses or device-control links where you want to vendor headers only: asio and struct_pack ship in thirdparty/, so there is no brpc/protobuf/gflags dependency stack to build.
- Simple server-to-client notifications, using the built-in topic publish/subscribe.

## Skip it when

- Across untrusted networks. Master has no TLS ('support ssl' is an unchecked TODO in C++20 rewrite PR #169) and no authentication, and the server allocates whatever uint64 `body_len` a request header claims, with no size cap.
- Polyglot or interop setups. It is C++-only with a custom protocol and speaks neither gRPC nor brpc (a Python-support request, #158, is still open).
- Many concurrent requests on one connection. Master runs one call at a time per connection: the client writes, then waits for the reply, and the server reads, runs the handler, writes, then reads again. A slow handler therefore blocks later calls on that connection, and sequence-number multiplexing exists only in unmerged PR #177.
- Production-RPC needs such as load balancing, a client connection pool (also a TODO in #169), streaming (unmerged stream_api PR #173), service discovery or metrics.
- If you picked it for the published speedup: those numbers are for the retired C++11 code (msgpack, future-based client), not current master. Master also needs GCC 12+, Clang 15+ or MSVC 2022.

## How it is fast

The wire format is a fixed 32-byte binary header (magic, message type, 32-bit function id, sequence number, body length) plus the body, sent with one scatter-gather `async_write`. Function ids are compile-time 32-bit MD5 hashes of the function name, dispatched through an `unordered_map`. A single `std::string_view` argument or return value skips serialization and copying, and receive buffers grow without zero-fill (`resize_and_overwrite`, or a std::string private-member hack on older libraries). The server runs one asio `io_context` per thread with one C++20 coroutine per connection and TCP_NODELAY on by default. All of this describes current master; the 2019 benchmark ran the older C++11/msgpack code.

## Compared with alternatives

Pick rest_rpc over brpc or SRPC when both ends are C++20 code you control and you want header-only, IDL-free function registration with nothing to build. Pick brpc (single/pooled/short connections, load balancers, protobuf services) or SRPC (SRPC/bRPC/Thrift/tRPC protocols, protobuf/Thrift IDL, HTTP+JSON, OpenTelemetry tracing) for production multi-service systems, and grpcxx when clients must speak standard gRPC.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | standalone asio 1.36.0 and the yalantinglibs struct_pack/reflection headers (both vendored under thirdparty/); a threads library |
| **Minimum toolchain** | C++20; GCC 12+, Clang 15+, MSVC 2022 per the README |
| **Platforms** | Linux, macOS and Windows (CI runs Ubuntu gcc/clang, macOS clang, and Windows MSVC in Debug only); architecture not restricted by the code. The wire header is host-endian unless both sides call enable_cross_ending(true). |
| **Thread safety** | Server: one io_context per thread and a mutex-guarded connection map. Handlers for different connections run concurrently, so shared handler state needs your own locking. Client: each rpc_client owns one socket and one receive buffer and runs on a lazily started global io_context pool (hardware_concurrency threads). It supports one outstanding call at a time; concurrent calls on one client are not documented, so use one client per concurrent caller, as tests/bench.cpp does. |
| **Drop-in for the baseline** | no |

## Gotchas

- A lone numeric argument or return value is sent as text: std::to_string going out, std::from_chars coming back (codec.h). Under C++20, a single double is therefore rounded to 6 decimal places (1e-9 arrives as 0). Multi-argument calls and structs use binary struct_pack.
- A timed-out call (`call_for`; plain `call` defaults to 5 s) makes the watchdog close the socket, so every later call on that client fails until you reconnect.
- The client decodes the response body as the declared return type even when the server reports an error such as no_such_function or function_exception. For non-string return types the error text fails to parse, so `co_await call` throws std::invalid_argument instead of returning `r.ec`. This comes from reading rpc_client.hpp; tests cover these error paths only at the router level.
- Function ids are 32-bit MD5 hashes of the compiler-derived qualified name (__PRETTY_FUNCTION__/__FUNCSIG__). Both sides must declare the function with the same name and namespace, and a duplicate or colliding id throws std::invalid_argument at registration. Whether ids match across different compilers is not documented.

## Known shortcomings

- No direct measurement against gRPC: the README's 'far exceeds gRPC' leans on brpc's own benchmark. The only numbers are a 2019 first-party echo test against brpc (about 1.2-1.9x, i5-9400F, g++ 8.2.0) on the old C++11 branch, not the current C++20 master, and master's link to that doc is dead.
- Current master (a 2025 C++20 coroutine rewrite) has no benchmark numbers, no TLS or auth, allocates any claimed body length (memory-exhaustion risk), and serves one call at a time per connection. Numeric arguments travel as text (a lone double loses precision), a timed-out call closes the socket, and error responses throw instead of returning codes (source reading).

## Caveats and trade-offs

The only numbers are a 2019 first-party rest_rpc-vs-brpc doc on the cpp11 branch, which tested the old C++11 version. The link to it from master's README is dead (404), because the doc/ folder is gone from master. The current master README links tests/bench.cpp, which only runs rest_rpc's own echo QPS loop (no gRPC/brpc code, no results). No direct gRPC measurement exists anywhere; 'far exceeds gRPC' is transitive, via brpc's docs/cn/benchmark.md. The benchmark code is partial snippets, and the rest_rpc 'high-efficiency mode' used in the multi-thread runs is undefined. Client timing uses duration_cast&lt;seconds&gt;, so elapsed time has whole-second resolution. The rest_rpc single-thread client uses async_call plus future.wait_for per call.

Modern header-heavy C++ template design; smaller ecosystem/tooling than gRPC (no multi-language codegen, no official service-mesh integrations).

## Maintenance

Active (master last commit 2026-06-23; multiplexing PR #177 opened 2026-09-03), MIT-licensed and header-only, so easy to vendor. The October 2025 C++20 rewrite (PR #169) changed the API and dropped SSL, so treat master as young code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded D-&gt;C: the cpp11-branch doc 'doc/单机上rest_rpc和brpc性能测试.md' (2019) publishes first-party same-machine echo QPS tables for rest_rpc vs Apache brpc, and states the CPU (i5-9400F), compiler (g++ 8.2.0) and CMake Release build. It is not A because the benchmark code exists only as partial modification snippets inside the doc (the rest_rpc multi-thread client_thread and its 'high-efficiency mode' are not shown, and there is no runnable bench file), explicit flags are not listed, and the comparison is against brpc, not gRPC.
- **Verifier notes:** The record's claimed_speedup had no numbers, so numbers_found_on_page is null. The README quote was checked word for word on master, and the rest_rpc-vs-brpc numbers above come from the cpp11-branch doc. If the orchestrator insists on gRPC as the baseline, the tier against gRPC itself stays D. Master's last commit is 2026-06-23; the record's 2026-09-08 came from the feature branch feat/client-seq-multiplexing. Status is still active; MIT license, not a fork, not archived, 2014 stars.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/qicosmos/rest_rpc>
  - <https://github.com/qicosmos/rest_rpc/blob/master/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/master/tests/bench.cpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/tests/CMakeLists.txt>
  - <https://github.com/qicosmos/rest_rpc/blob/cpp11/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/cpp20/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/stream_api/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/cpp11/doc/%E5%8D%95%E6%9C%BA%E4%B8%8Arest_rpc%E5%92%8Cbrpc%E6%80%A7%E8%83%BD%E6%B5%8B%E8%AF%95.md>
  - <https://github.com/qicosmos/rest_rpc/blob/master/doc/%E5%8D%95%E6%9C%BA%E4%B8%8Arest_rpc%E5%92%8Cbrpc%E6%80%A7%E8%83%BD%E6%B5%8B%E8%AF%95.md>
  - <https://github.com/apache/brpc/blob/master/docs/cn/benchmark.md>
- **Sources the enricher read:**
  - <https://github.com/qicosmos/rest_rpc>
  - <https://github.com/qicosmos/rest_rpc/blob/master/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/rpc_client.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/rpc_server.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/rpc_connection.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/rpc_router.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/codec.h>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/rest_rpc_protocol.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/function_name.h>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/io_context_pool.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/asio_util.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/string_resize.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/error_code.h>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/traits.h>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/use_asio.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/include/rest_rpc/util.hpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/tests/bench.cpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/tests/CMakeLists.txt>
  - <https://github.com/qicosmos/rest_rpc/blob/master/tests/test_rest_rpc.cpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/CMakeLists.txt>
  - <https://github.com/qicosmos/rest_rpc/blob/master/cmake/build.cmake>
  - <https://github.com/qicosmos/rest_rpc/blob/master/examples/client.cpp>
  - <https://github.com/qicosmos/rest_rpc/blob/master/.github/workflows/linux_gcc.yml>
  - <https://github.com/qicosmos/rest_rpc/blob/master/.github/workflows/linux_clang.yml>
  - <https://github.com/qicosmos/rest_rpc/blob/master/.github/workflows/mac.yml>
  - <https://github.com/qicosmos/rest_rpc/blob/master/.github/workflows/windows.yml>
  - <https://github.com/qicosmos/rest_rpc/blob/cpp11/README.md>
  - <https://github.com/qicosmos/rest_rpc/blob/cpp11/doc/%E5%8D%95%E6%9C%BA%E4%B8%8Arest_rpc%E5%92%8Cbrpc%E6%80%A7%E8%83%BD%E6%B5%8B%E8%AF%95.md>
  - <https://github.com/qicosmos/rest_rpc/issues>
  - <https://github.com/qicosmos/rest_rpc/issues/113>
  - <https://github.com/qicosmos/rest_rpc/issues/144>
  - <https://github.com/qicosmos/rest_rpc/issues/166>
  - <https://github.com/qicosmos/rest_rpc/issues/174>
  - <https://github.com/qicosmos/rest_rpc/pulls>
  - <https://github.com/qicosmos/rest_rpc/pull/169>
  - <https://github.com/qicosmos/rest_rpc/pull/173>
  - <https://github.com/qicosmos/rest_rpc/pull/177>
  - <https://github.com/qicosmos/rest_rpc/commits/master>
  - <https://github.com/sogou/srpc/blob/master/README.md>
  - <https://github.com/uatuko/grpcxx/blob/main/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/qicosmos/rest_rpc`) · [data/wave5/enrich/raw/github_com_qicosmos_rest_rpc.json](../../../data/wave5/enrich/raw/github_com_qicosmos_rest_rpc.json) (enrichment confidence 0.6)

</details>
