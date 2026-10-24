# liburing4cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++20 coroutine wrapper over liburing; its echo server roughly matches the author's raw C io_uring server.

| | |
|---|---|
| **Beats** | raw liburing C echo server (CarterLi/io_uring-echo-server, io_uring RECV-SEND); epoll echo server only indirectly |
| **Claimed result** | Not faster like for like. Echo server README rows (medians of 3 runs): C++ POLL-RECV-SEND 111,210 req/s vs the C server's POLL-RECV-SEND 114,893, about 96.8% (derived from page data). The headline row, C++ RECV-SEND 120,239 vs C RECV-SEND 114,461 (105.05%, README column 'rate'), is asymmetric: the C baseline sets IOSQE_ASYNC on its recv while the C++ server does not, so the two rows run different submission paths. SPLICE-SPLICE variants 77.84% to 81.63%. Yield microbench: service.yield 5436209973 vs plain IORING_OP_NOP 5268565967, 'About 3% overhead'. |
| **Workload** | TCP echo server driven by rust_echo_bench (cargo run --release), requests per second, three runs and median; C++ coroutine demo/echo_server vs the C io_uring echo server; plus a yield-path microbench (demo/bench) vs plain IORING_OP_NOP. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2620 v4 @ 2.10GHz |
| **Compiler and flags** | clang version 10.0.0-4ubuntu1 on Ubuntu 20.04.1, kernel 5.9.0-050900rc6; build flags for the measured binaries not stated (README build instructions use CMAKE_BUILD_TYPE=Release, and the CMakeLists only adds -fcoroutines for GCC, but neither is tied to the numbers; the load-tool command is cargo run --release). |
| **Adoption** | 349 stars |
| **Last commit** | 2024-07-30 |
| **Links** | [repository](https://github.com/CarterLi/liburing4cpp) · [benchmark](https://github.com/CarterLi/liburing4cpp) |

## Verdict

The author's README (Xeon E5-2620 v4, Ubuntu 20.04.1, kernel 5.9.0-rc6, clang 10, build flags not stated) drives each echo server with rust_echo_bench and takes the median of 3 runs: C++ RECV-SEND 120,239 req/s vs the C io_uring server's RECV-SEND 114,461 (105.05%). The C server's RECV-SEND mode submits every recv with IOSQE_ASYNC (forcing a worker-thread punt) while the C++ server does not, so the like-for-like row is POLL-RECV-SEND, where C++ reaches 111,210 vs C 114,893 req/s, about 96.8% (derived from page data); splice variants are 78-82%, and the yield path is about 3% slower than a raw IORING_OP_NOP loop (about 544 vs 527 ns per op, derived from page data).

## Use it when

- Single-threaded Linux programs (or one ring per thread) that want co_await over raw io_uring opcodes with almost no abstraction cost.
- Learning or prototyping io_uring patterns in C++20: echo servers, file servers, link-chained copies (demo/link_cp.cpp).
- Code that needs io_uring-only operations such as splice, tee, statx, openat or msg_ring as awaitables rather than through a portable runtime.
- Small tools where vendoring a few MIT headers beats pulling in Asio or Seastar.

## Skip it when

- Anything needing cancellation or timeouts on in-flight operations: there is no cancel API (the author removed it as slow and hard to use safely, issue #27), and a dropped task does not cancel the kernel operation.
- Production servers: two crash reports remain open (SIGSEGV in file_server #9, heap-use-after-free in the test app #8) and the last commit is from July 2024.
- Non-Linux targets or old kernels: Linux io_uring only, and the README says old kernel support is dropped as new kernels ship.
- Multi-threaded use of one loop: io_service is documented as not thread safe; you need one io_service per thread (optionally sharing workers via IORING_SETUP_ATTACH_WQ).
- If you need a measured win over epoll: the repo's only comparison is against the author's own C io_uring server, not epoll.

## How it is fast

Every operation is a single io_uring SQE with the awaiting coroutine's resolver stored in user_data, so a completion resumes the coroutine directly with no callback queue, executor layer or per-operation heap allocation (the awaiter lives in the coroutine frame). Submission is batched: SQEs are only submitted by the run loop (or when the SQ fills), and the loop drains all available CQEs before advancing the CQ head. Fixed files, fixed buffers, IOSQE_IO_LINK chains and splice are exposed for zero-copy paths.

## Compared with alternatives

Pick it over Condy or uring_exec only when you want the thinnest possible coroutine layer over raw liburing calls and can live without cancellation or maintenance; those siblings carry measured wins over epoll or Asio's io_uring backend, while liburing4cpp only shows parity with a hand-written C io_uring server. For portable multi-backend code COROIO or the Asio io_uring backend fit better.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | liburing (linked), pthreads; the CMake target also links fmt, fetched from fmt's master branch if not found |
| **Minimum toolchain** | C++20 coroutines (&lt;coroutine&gt;); README recommends GCC 10.3+ or Clang 10+; liburing headers new enough to define IORING_OP_SENDMSG_ZC, IORING_FEAT_REG_REG_RING and io_uring_prep_msg_ring (exact liburing version not documented) |
| **Platforms** | Linux with io_uring (README: 'requires the latest kernel'; benchmark run on 5.9.0-rc6); opcodes are probed at runtime |
| **Thread safety** | io_service is not thread safe; use one io_service per thread (header comment recommends IORING_SETUP_ATTACH_WQ to share the kernel worker pool) |
| **Drop-in for the baseline** | no |

## Gotchas

- Tasks start eagerly and destroying an unfinished task only detaches it; the kernel operation keeps running, so a stack buffer passed to read/recv can be written after it goes out of scope (README's own warning).
- utils.hpp defines uio::panic as a non-inline function in a header, so including the library from more than one translation unit of the same program should give a duplicate-symbol link error.
- Errors surface as std::system_error thrown by panic_on_err (and rethrown from task&lt;T&gt; results); task&lt;T, true&gt; is the nothrow variant.
- The README still says it compiles in clang C++17 mode with -fcoroutines-ts, but task.hpp now includes &lt;coroutine&gt; and CMakeLists forces C++20; on GCC the CMakeLists overwrites CMAKE_CXX_FLAGS with -fcoroutines, dropping user flags.

## Known shortcomings

- Parity, not a win: 105.05% of the author's own C io_uring server (3 runs, kernel 5.9-rc6 in 2020, flags not stated); the epoll comparison is indirect (non-poll SEND-RECV at 51-57% of epoll on kernel 5.5 in a sibling README). Stale (last commit 2024-07-30).
- not faster like for like: the 105% RECV-SEND row is asymmetric (C baseline sets IOSQE_ASYNC on recv); POLL-RECV-SEND C++ 111,210 vs C 114,893 req/s is about 96.8%

## Caveats and trade-offs

The 105% is an abstraction-parity result against a raw io_uring C server written by the same author, not a win over epoll; 3 runs on one machine (run ranges do not overlap: C RECV-SEND 112,112-116,797 vs C++ 117,519-121,139 req/s) and the numbers appear to date from late 2020 (kernel 5.9.0-rc6 build of 2020-09-23, clang 10); the repo has been restructured since, and where the load generator ran is not stated. The C server (CarterLi/io_uring-echo-server) in its own README reports io_uring POLL-RECV-SEND at 106.70% (-c 50) and 101.79% (-c 200) of its epoll POLL-RECV-SEND server on a 4-vCPU VMware guest (kernel 5.5.0, MacBook Pro i7 2.5GHz host) with clang 9.0.1, so the epoll comparison is indirect, run on different hardware, and within a few percent; in that README the non-poll SEND-RECV mode (the mode of the C++ 105% row) was only 57.34% (-c 50) and 51.40% (-c 200) of epoll on kernel 5.5, so there is no like-for-like epoll figure for the winning row. The other C++ configurations (POLL, SPLICE) are slower than C, and the yield path is about 3% slower than plain NOP. The yield microbench prints std::chrono::high_resolution_clock tick counts for 10,000,000 iterations (nanoseconds on Linux libstdc++/libc++, i.e. about 544 vs 527 ns per operation, derived from page data); units are not printed. First-party with flags not stated, so tier C. [retier] Enricher: the RECV-SEND comparison is asymmetric (the C io_uring-echo-server flags its recv IOSQE_ASYNC, forcing io-wq punting, while the C++ server submits plain recv), so the 105% row does not show the coroutine layer beating hand-written C; the like-for-like POLL-RECV-SEND pair is about 96.8% (derived from page data). Library gotchas: uio::panic is a non-inline function defined in a header (duplicate-symbol link error from two translation units); the README still describes C++17 -fcoroutines-ts while the code needs C++20 &lt;coroutine&gt;; on GCC the CMakeLists overwrites CMAKE_CXX_FLAGS with -fcoroutines. Last commit July 2024; open crash issues.

Header-only binding needing a recent Linux kernel and liburing, C++20 coroutines; tasks are eagerly started (not lazy) and a dropped task does not cancel the kernel operation, so stack buffers can be written after scope exit.

## Maintenance

Stale (last commit July 2024, numbers from late 2020) with open crash issues, but MIT-licensed and a handful of headers, so it is easy to vendor as a reference or starting point.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks section gives CPU (Xeon E5-2620 v4), kernel and clang 10 with the rust_echo_bench table (C++ RECV-SEND 120,239 vs C 114,461 req/s, 105.05%) and demo/bench.cpp is public, but build flags for the measured binaries are not stated and both servers are the author's own: first-party partial methodology, C.
- **Verifier notes:** Table and yield numbers match README verbatim. Metadata matches: MIT, 349 stars, last commit 2024-07-30 (stale vs 2026-09-26), default view branch async. Baseline is the io_uring baseline the benchmark names, which spec Part 4 lists for event-loops-io.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-83 (wave 5 book seed pass, 2026-10-24); enrichment (wave 5 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/CarterLi/liburing4cpp>
  - <https://github.com/CarterLi/liburing4cpp/commits>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/demo/bench.cpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CarterLi/io_uring-echo-server/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/CarterLi/liburing4cpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/include/liburing/io_service.hpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/include/liburing/task.hpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/include/liburing/sqe_awaitable.hpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/include/liburing/utils.hpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/demo/echo_server.cpp>
  - <https://raw.githubusercontent.com/CarterLi/liburing4cpp/HEAD/demo/bench.cpp>
  - <https://github.com/CarterLi/liburing4cpp/issues?q=is%3Aissue>
  - <https://github.com/CarterLi/liburing4cpp/issues/27>
  - <https://github.com/CarterLi/liburing4cpp/commits/async/demo/echo_server.cpp>
  - <https://raw.githubusercontent.com/CarterLi/io_uring-echo-server/HEAD/README.md>
  - <https://raw.githubusercontent.com/CarterLi/io_uring-echo-server/HEAD/io_uring_echo_server.c>
  - <https://raw.githubusercontent.com/CarterLi/io_uring-echo-server/HEAD/global.h>
  - <https://github.com/CarterLi/io_uring-echo-server/commits/master/io_uring_echo_server.c>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/carterli/liburing4cpp`) · [data/wave5/enrich/raw/github_com_carterli_liburing4cpp.json](../../../data/wave5/enrich/raw/github_com_carterli_liburing4cpp.json) (enrichment confidence 0.8)

</details>
