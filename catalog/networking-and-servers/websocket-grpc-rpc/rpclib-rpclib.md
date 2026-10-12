# rpclib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small C++11/14 msgpack-rpc client and server with no IDL; its author's 2017 benchmark has small calls 2.5x faster than gRPC 1.1.0.

| | |
|---|---|
| **Beats** | gRPC (also Apache Thrift and Cap'n Proto RPC in the same suite) |
| **Claimed result** | get_answer: rpclib 22,115 ns vs gRPC 54,841 ns (about 2.5x faster, derived from page data), vs Cap'n Proto 36,292 ns (about 1.6x); get_structs: rpclib 8,305,870 ns vs gRPC 17,676,102 ns (about 2.1x faster, derived from page data) and vs Thrift 11,648,059 ns (about 1.4x). Not faster than Thrift on get_answer (10,285 ns) nor Cap'n Proto on get_structs (183,415 ns). |
| **Workload** | Google Benchmark microbenchmarks of one RPC call over a local TCP socket: get_answer (return an int) and get_structs (return a large nested struct with bad alignment), five repetitions of at least 3 s each. |
| **Metric** | latency |
| **Hardware** | 4 CPUs at 2807 MHz with CPU frequency scaling enabled (benchmark.json context, run 2017-02-20); CPU model and the run's OS not stated (README says the suite was tested on Arch Linux and Ubuntu 16.04). |
| **Compiler and flags** | Not stated for the published run. README requires g++ 5.4 or later or clang 3.8 or later and builds with plain 'cmake ..' (no CMAKE_BUILD_TYPE), while CMakeLists.txt only warns 'Not building in release mode!' outside Release (Release uses CMake's default -O3, -O2 via USE_O2); C++14. The JSON field library_build_type 'release' describes the Google Benchmark library, not the benchmark binary. Libraries from conan: rpclib 1.0.0, grpc 1.1.0 and thrift 0.9.3 (packaged by the rpclib author in sztomi/testing), capnproto 0.5.3, google-benchmark 1.1.0; rpclib logging disabled. |
| **Adoption** | 1.8k stars; used by Microsoft AirSim |
| **Last commit** | 2022-11-22 |
| **Links** | [repository](https://github.com/rpclib/rpclib) · [benchmark](https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/benchmark.json) |

## Verdict

The rpclib author's Google Benchmark suite (rpclib/benchmarks, run 2017-02-20, 5 repetitions of at least 3 s each, 4 CPUs at 2.8 GHz, compiler not stated) timed one synchronous localhost TCP round trip per iteration. rpclib 1.0.0 (pre-release) took 22,115 ns for get_answer vs gRPC 1.1.0's 54,841 ns (2.5x), and 8.31 ms vs 17.68 ms for get_structs, a large nested struct (2.1x). Thrift 0.9.3 with TSimpleServer won get_answer at 10,285 ns, and Cap'n Proto's faster get_structs row sent far less data.

## Use it when

- In-house C++ services, simulators or tools (AirSim is the listed user) that need a quick request/response RPC between processes on one host or a trusted LAN, with almost no boilerplate.
- Many small, latency-sensitive calls over one persistent connection, where the benchmark measured about 22 µs per round trip vs about 55 µs for gRPC 1.1.0.
- Talking to Python, Node, Go or other msgpack-rpc peers without maintaining .proto or .thrift files.
- Old toolchains or C++11 codebases that cannot pull in gRPC's dependency tree: Asio, msgpack-c and fmt are vendored, and the build is a single CMake static library.

## Skip it when

- You need a maintained library: the README says 'rpclib is looking for maintainers' and points to packio, and the last commit was 2022-11-22.
- Large payloads: in the same suite Thrift was faster at most blob sizes (1 KB: 14,362 ns vs 23,608 ns) and both Thrift and Cap'n Proto were faster from 256 KB to 16 MB. gRPC's blob rows were never run.
- Untrusted networks or public endpoints: there is no TLS or authentication, no documented maximum message size, and the 1 MiB per-connection buffer grows by doubling.
- Streaming, cancellation, deadlines, schema evolution or polyglot code generation: none of these exist.
- Multithreaded servers whose clients may disconnect mid-call: issue #231 (open since 2019) reports async_run servers crashing when they reply to a client that has gone.

## How it is fast

It does far less per call than gRPC. A call is one msgpack array [type, msgid, method, params] written over a persistent plain TCP connection, with no HTTP/2 framing, HPACK or protobuf message objects. Standalone Asio reads into a streaming msgpack unpacker that reserves a 1 MiB buffer per connection, the server finds the function by name in a std::unordered_map, converts the result to a msgpack object and packs it into one sbuffer written on an Asio strand. Most of the work runs on the client's I/O thread and the server worker, so the calling thread used only 4.7 µs of CPU per get_answer call against 22.1 µs of wall time.

## Compared with alternatives

Pick rpclib over brpc or SRPC when you want a tiny, dependency-free C++11 library and msgpack-rpc interoperability rather than a production RPC platform, and over rest_rpc (also msgpack-based, benchmarked against brpc) when existing peers already speak standard msgpack-rpc. If you need to stay wire-compatible with gRPC while going faster, grpcxx is the catalogued choice.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake project; Asio, msgpack-c and fmt vendored under the clmdep_ namespaces) |
| **Dependencies** | none external (standalone Asio, msgpack-c and fmt ship in dependencies/); pthreads on POSIX |
| **Minimum toolchain** | C++11 (RPCLIB_CXX_STANDARD 11 by default, 14 allowed) and CMake &gt;= 3.5.1. The changelog lowered the minimum g++ to 4.8 in 2.1.0, while the benchmark suite asks for g++ 5.4 or clang 3.8. |
| **Platforms** | Linux, macOS and Windows (MSVC) via Asio; MinGW support is an open request (issue #206) |
| **Thread safety** | With run(), handlers execute on the thread that called run(). With async_run(n), each decoded call is posted to the io_service, so any worker can run it: calls from one connection can execute concurrently and finish out of order, and bound functions must be thread-safe. The client gives each call an atomic id and serializes writes on a strand, and its own I/O thread completes the futures. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw that matters for the caveats: the Cap'n Proto get_structs row is not like for like. capnp_code::fill_struct_cache calls initSchools(item_count) but never fills the schools (its random_School lambda is unused). rpclib, Thrift and gRPC each send 34 students with 34 schools of 34 37-character e-mail addresses, which we estimate at about 1.5 MB of the payload. Cap'n Proto's 183,415 ns is 21x faster than the in-process direct_bench deep copy of the same data (3,859,058 ns), so 'rpclib is not faster than Cap'n Proto on get_structs' should not be cited.
- The measured build is not a release. benchmark.json is dated 2017-02-20, three weeks before the 1.0.0 tag (2017-03-11), whose changelog lists 'A buffer overflow bug was fixed in the server'. The conan package rpclib/1.0.0@sztomi/testing was a pre-release snapshot of unknown commit, run on a 4-CPU machine with frequency scaling on and no CPU model. The win over gRPC is against gRPC 1.1.0 (January 2017) in its synchronous API, and gRPC's blob benchmark was commented out over grpc issue 9510.
- No default client timeout (removed in 2.1.0): call() blocks until a reply arrives unless set_timeout() is used. A timed-out call is not cancelled on the server, because msgpack-rpc has no cancellation.
- Each rpc::client starts its own I/O thread, and every client and server session reserves a 1 MiB unpacker buffer (DEFAULT_BUFFER_SIZE = 1024 &lt;&lt; 10). Thousands of connections therefore cost gigabytes of reserved buffers, and the CMake option RPCLIB_DEFAULT_BUFFER_SIZE is the only knob.

## Known shortcomings

- Tier C: the author's own 2017 benchmark.json (2.5x faster than gRPC 1.1.0 on get_answer, 2.1x on get_structs, derived from page data) against Thrift 0.9.3 and Cap'n Proto 0.5.3 with no CPU model and a plain 'cmake ..' build (Release unconfirmed); slower than Thrift and Cap'n Proto on most get_blob sizes and on every size from 256 KB to 16 MB. MIT; abandoned (last commit 2022-11-22).
- Enricher: the Cap'n Proto get_structs row is invalid because capnp fill_struct_cache never fills schools (the random_School lambda is unused), so its 183,415 ns is 21x under an in-process direct deep copy (3,859,058 ns); the 'not faster than Cap'n Proto on get_structs' caveat is dropped. The run (2017-02-20) predates the 1.0.0 tag (2017-03-11) whose changelog lists a server buffer-overflow fix; conan snapshot commit unknown. No default client timeout, 1 MiB buffer per connection, async_run crash on client disconnect (#231 open); abandoned.

## Caveats and trade-offs

First-party benchmark (rpclib/benchmarks, written by the rpclib author, whose README FAQ says 'I'm not an expert in the other libraries, so it's entirely possible that I used them wrong') with public code but no CPU model, no exact compiler version and no confirmed Release build of the benchmark binary, so tier C. Numbers date from 2017-02-20 and use gRPC 1.1.0, Thrift 0.9.3 and Cap'n Proto 0.5.3 from conan (gRPC and Thrift packaged by the rpclib author), so the gRPC gap may not hold for current gRPC. gRPC has no get_blob rows: the gRPC get_blob benchmark is commented out in src/benchmark.cc, citing grpc issue 9510 on message size. Against the other libraries rpclib mostly loses: on get_blob it is slower than Thrift at every size except 64 KB and 128 KB (1 KB: 23,608 ns vs 14,362 ns) and slower than both Thrift and Cap'n Proto at every size from 256 KB to 16 MB (16 MB: 16,482,465 ns vs Thrift 15,126,944 ns and Cap'n Proto 13,364,192 ns); on get_answer Thrift is faster (10,285 ns); on get_structs Cap'n Proto is faster (183,415 ns). The gRPC comparison is the only one rpclib wins across the board. Wall time includes the in-process server thread; rpclib's calling-thread CPU time is much lower than its wall time (get_answer 4,725 ns CPU vs 22,115 ns real). The accompanying blog post (szelei.me) is blocked here and was not read. The project README says 'rpclib is looking for maintainers'; last commit 2022-11-22. [retier] Cap'n Proto get_structs row invalid (empty payload); run 2017-02-20 predates 1.0.0 (2017-03-11) buffer-overflow fix; conan snapshot commit unknown; no default client timeout; 1 MiB buffer per connection; async_run crash on client disconnect (#231); abandoned.

msgpack-RPC wire protocol (interoperable with any msgpack-rpc implementation), no IDL and no code generation. The README says the library is looking for maintainers and points to packio for JSON-RPC and async. No streaming, no TLS.

## Maintenance

Abandoned in practice: latest release v2.3.0, last commit 2022-11-22, and an open 'looking for maintainers' notice (issue #273) that recommends packio. It is MIT-licensed, has no external dependencies and is small enough to vendor for trusted-network use, but multithreaded-server crash reports (#175, #231) remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark.json in rpclib/benchmarks (author's own suite, code in src/benchmark.cc and include/\*/fixture.h) contains the claimed means exactly (rpclib get_answer 22,115 ns vs gRPC 54,841 ns; get_structs 8,305,870 vs 17,676,102 ns), but no CPU model, no exact compiler version and no confirmed build type, so first-party tier C.
- **Verifier notes:** All claimed means match benchmark.json exactly and the gRPC fixture is a fair synchronous round trip over localhost with one persistent channel, so the 2.5x and 2.1x wins over gRPC 1.1.0 stand as first-party evidence. Repo: 1.8k stars, MIT (LICENSE.md, Copyright 2015-2017 Tamas Szelei), not archived, not a fork, last commit 2022-11-22 (abandoned by the 3-year rule), AirSim listed as a user. No duplicate found.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 5); enricher w5 pair-032
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/benchmark.json>
  - <https://github.com/rpclib/benchmarks>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/conanfile.txt>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/benchmark.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/grpc/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/rpclib/fixture.h>
  - <https://github.com/rpclib/rpclib>
  - <https://github.com/rpclib/rpclib/commits/master>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/rpclib/rpclib/releases>
  - <https://github.com/rpclib/rpclib/issues?q=is%3Aissue+is%3Aopen+sort%3Acomments-desc>
  - <https://github.com/rpclib/rpclib/issues/231>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/README.md>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/server.h>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/client.h>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/client.inl>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/config.h>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/dispatcher.h>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/dispatcher.inl>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/include/rpc/detail/async_writer.h>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/lib/rpc/server.cc>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/lib/rpc/client.cc>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/lib/rpc/dispatcher.cc>
  - <https://raw.githubusercontent.com/rpclib/rpclib/HEAD/lib/rpc/detail/server_session.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/benchmark.json>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/conanfile.txt>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/benchmark.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/target_code.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/target_code.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/rpclib/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/grpc/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/thrift/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/capnp/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/direct/fixture.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/include/rpclib/struct_helpers.h>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/rpclib/struct_helpers.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/grpc/struct_helpers.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/thrift/struct_helpers.cc>
  - <https://raw.githubusercontent.com/rpclib/benchmarks/HEAD/src/capnp/struct_helpers.cc>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/rpclib/rpclib`) · [data/wave5/enrich/raw/github_com_rpclib_rpclib.json](../../../data/wave5/enrich/raw/github_com_rpclib_rpclib.json) (enrichment confidence 0.75)

</details>
