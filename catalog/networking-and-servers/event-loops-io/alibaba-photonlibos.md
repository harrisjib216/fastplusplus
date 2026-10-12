# PhotonLibOS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Alibaba's stackful-coroutine C++ I/O runtime (epoll/io_uring/kqueue); its echo server beats boost::asio on single-core QPS.

| | |
|---|---|
| **Beats** | boost::asio |
| **Claimed result** | Ping-pong (1,000 conns, 512B): Photon 412K QPS / 1.57Gb vs boost::asio 393K QPS / 1.49Gb (\~1.05x, derived from page data); streaming (4 conns, 512B): Photon 1604K QPS / 6.12Gb vs boost::asio 634K QPS / 2.42Gb (\~2.5x, derived from page data) |
| **Workload** | TCP ping-pong test (1,000 connections, 512-byte buffers) and streaming test (4 connections, 512-byte buffers), measuring per-core QPS and bandwidth |
| **Metric** | throughput |
| **Hardware** | Cloud VMs for server and client, 64 cores, 128GB RAM, 'Intel Platinum CPU 2.70GHz' (exact CPU model not stated), Linux kernel 6.x, 32Gb network bandwidth; per-core test with thread count limited to 1 |
| **Compiler and flags** | CMake Release build type (exact compiler/optimization flags not stated) |
| **Adoption** | 1.2k stars; used in production at Alibaba, Ant Group, ByteDance, Xiaomi, XSKY (e.g. overlaybd, OSSFSv2) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/alibaba/PhotonLibOS) · [benchmark](https://photonlibos.github.io/docs/performance/network-performance) |

## Verdict

Photon's first-party TCP echo test ran one server thread, 512-byte buffers, on 64-core 'Intel Platinum 2.70GHz' cloud VMs with kernel 6.x and a 32Gb network. With 4 streaming connections Photon reached 1604K QPS vs boost::asio's 634K (\~2.5x); with 1000 ping-pong connections it reached 412K vs 393K (\~1.05x). Photon used its default tcp socket on epoll and a CMake Release build (-O2 -DNDEBUG, plus SSE4.2 flags on x86-64 per CMakeLists.txt). The asio server code, the asio version and the compiler are not published.

## Use it when

- Moving thread-per-connection or blocking-style C++ server or storage code to high concurrency without rewriting it into callbacks. photon_std::thread, mutex and condition_variable are namespace-swap replacements for the std:: versions.
- Linux TCP services where one core pushes a few high-throughput streams (multiplexed RPC or HTTP/2-like traffic): Photon's page shows about 2.5x boost::asio's per-core QPS in its 512-byte streaming echo test.
- Storage or data-plane services that mix network and disk I/O (libaio/O_DIRECT, io_uring) and want one scheduler for both. This is its production origin at Alibaba Cloud storage (overlaybd, OSSFSv2).
- You want to try io_uring, zero-copy TCP, RDMA (SMC-R/rsocket) or F-Stack/DPDK and SPDK backends without changing application code, since they sit behind the same socket and file interfaces.
- Linux or macOS on x86-64 or ARM64, built with GCC 8-14 or Clang in C++14 or later.

## Skip it when

- Windows or RISC-V targets. The README lists only Linux and macOS; IOCP and MinGW code exists, but Windows support is still an open request (#396) and RISC-V is an open question (#1094).
- You depend on the asio ecosystem (Beast, strands, completion tokens, C++20 awaitables, executors). Photon has no asio compatibility layer, so switching means a rewrite of the I/O layer.
- Clients that must verify TLS certificates: open issue #457 says Photon's TLS adaptors do not validate the certificate chain.
- Workloads with many connections and small request/response traffic, where the measured gain over asio is about 5% (412K vs 393K QPS). That is too small on its own to justify a runtime switch.
- Code bases with heavy use of third-party blocking libraries, OpenMP or std::thread interop. Blocking calls stall every coroutine on that vCPU, and mixing threading models has caused crashes (#137). The library is also pre-1.0 (v0.9.6); recent fixes include critical work-stealing scheduler bugs (#1245) and an io_uring use-after-free (#1270), and a rare crash in prelocked_thread_interrupt is still open (#1093).

## How it is fast

The context switch uses context-aware context switching (CACS), described in the project's 'Stackful Coroutine Made Fast' paper. The x86-64 assembly saves only rbp and rsp, and the inline-asm call lists every other register as clobbered, so the compiler spills only the registers that are live at that call site. Each vCPU keeps a private, lock-free run queue (an intrusive list) and a min-heap sleep queue. The epoll, io_uring and kqueue backends register one-shot interests whose event data is the waiting coroutine's pointer, so an event wakes it through thread_interrupt() with no lookup. Sockets are non-blocking and try the syscall first, waiting only on EAGAIN (doio_once in net/basic_socket.h). Optional io_uring sockets, zero-copy send and F-Stack/DPDK backends sit behind the same interface.

## Compared with alternatives

Pick Photon over libhv when you want blocking-style coroutine code plus disk I/O, RPC and HTTP in one C++ runtime rather than a callback event loop. Pick it over monoio when your code is C++; on Photon's own page it leads monoio per core (1604K vs 610K QPS streaming, 412K vs 400K ping-pong). io_uring-echo-server is a demo, not a library.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib: the CMake targets photon_static and photon_shared, pulled in with FetchContent or a git submodule |
| **Dependencies** | openssl, zlib, libcurl (on by default) and libaio on Linux; liburing, libfuse, libgsasl, e2fs, F-Stack/DPDK, SPDK and rdma-core are optional; tests need gflags and googletest. PHOTON_BUILD_DEPENDENCIES=ON builds these from source. |
| **Minimum toolchain** | C++14 (PHOTON_CXX_STANDARD defaults to 14) and CMake 3.14+. CI runs GCC 8-14 on Linux (C++14 to C++23) and Apple Clang on macOS 15 (C++17). |
| **Platforms** | Linux and macOS on x86-64 and ARM64. The x86-64 build passes -msse4.2 -mpopcnt -mcx16. The ARM64 build passes -mcpu=generic+crc+crypto+lse, except in MinSizeRel. The io_uring engine needs kernel 5.8+ and PHOTON_ENABLE_URING=ON. Windows is not listed as supported. |
| **Thread safety** | Each OS thread that calls photon::init() becomes a vCPU, and its coroutines are cooperatively scheduled and can be migrated. The docs say Photon's sync primitives and thread_interrupt are thread-safe across vCPUs. std:: locks and blocking syscalls block the whole vCPU, and non-Photon threads should hand work over through Executor or WorkPool. |
| **Drop-in for the baseline** | false: it uses a different programming model (blocking-style coroutines over ISocketServer/ISocketStream instead of io_context plus completion handlers). photon_std:: replaces std::thread and std::mutex, not asio. |

## Gotchas

- The default coroutine stack is 8 MB (virtual memory, committed lazily), with a minimum of 16 KB plus a guard page. The docs warn that stack overflow is not detected immediately and can trample memory, so avoid deep recursion. thread_create() mallocs a stack every time; use ThreadPool or pooled_stack_allocator for short-lived coroutines.
- After photon::init(), do not make blocking calls on that OS thread. One blocking read() or std::mutex wait freezes every coroutine on the vCPU.
- Join is off by default, and joinable threads leak if never joined. Calling thread_join() or thread_interrupt() on a thread that has already exited core-dumps.
- Build your app and Photon with the same C++ standard. Open issue #277 notes that C++14 builds make the std library act as if it were in C++17 mode (to get string_view), which causes ABI inconsistency between binaries.

## Known shortcomings

- Ping-pong is only about 1.05x boost::asio (streaming about 2.5x). Only Photon's own test program is published, not the asio server; no compiler, flags or CPU model (cloud VMs).
- The benchmark used Photon's default epoll socket although its docs recommend io_uring for ping-pong. TLS adaptors do not validate certificate chains (#457, open). Pre-1.0 with recent serious scheduler and io_uring use-after-free bugs (fixed) and an open crash (#1093). Large CMake library needing openssl, zlib, libcurl and libaio; Linux/macOS only.

## Caveats and trade-offs

First-party benchmark. Only Photon's test program (examples/perf/net-perf.cpp; default socket type tcp on the default epoll engine) is published, and the boost::asio echo server code is not. The CPU model number, compiler and optimization flags are not stated, only a CMake Release build. The test measures single-thread (per-core) QPS on cloud VMs. In the ping-pong test the win over boost::asio is small (\~1.05x). The same page also shows Photon at 114K QPS vs Nginx (1 worker) at 97K QPS when serving 4KB static files.

Stackful-coroutine model; also compares against cocoyaxi, tokio, monoio, Go, libco and others on the same page (Photon leads on per-core QPS in both tests)

## Maintenance

Actively maintained: v0.9.6 came out on 2026-08-21, the last commit was on 2026-09-25, and it has used stable release branches since 0.7. It is Apache-2.0 but still pre-1.0, and it is a large CMake-built library with OpenSSL, zlib, libcurl and libaio dependencies, not something you copy in as a few files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party page with Photon and boost::asio rows in the same streaming and ping-pong tables. The numbers match. Only Photon's own test program (examples/perf/net-perf.cpp) is published, not the boost::asio server. The compiler and flags are not stated beyond CMAKE_BUILD_TYPE=Release, and the CPU is given only as 'Intel Platinum CPU 2.70GHz' with no model number, so the record falls short of A.
- **Verifier notes:** All claimed numbers match the page (docs source doc/docs/performance/network-performance.md), and both ratios check out (412/393 = 1.05x, 1604/634 = 2.53x). The README lists production users Alibaba, Ant Group, ByteDance, Xiaomi and XSKY, and projects such as overlaybd and OSSFSv2. Metadata is correct: Apache-2.0, 1232 stars, last commit 2026-09-25, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://photonlibos.github.io/docs/performance/network-performance>
  - <https://github.com/alibaba/PhotonLibOS>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/performance/network-performance.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/i18n/cn/docusaurus-plugin-content-docs/current/performance/network-performance.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/examples/perf/net-perf.cpp>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/alibaba/PhotonLibOS>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/README.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/performance/network-performance.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/introduction/how-to-build.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/introduction/how-to-integrate.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/introduction/what-is-photon.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/introduction/photon-architecture.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/env.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/thread.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/std-compatible-api.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/vcpu-and-multicore.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/network.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/docs/api/lock-and-synchronization.md>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/CMakeLists.txt>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/examples/perf/net-perf.cpp>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/thread/thread.cpp>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/net/basic_socket.h>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/.github/workflows/ci.linux.x86_64.yml>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/.github/workflows/ci.linux.arm.yml>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/.github/workflows/ci.macos.yml>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/blog/2024-10-14-stackful-coroutine-made-fast.mdx>
  - <https://github.com/alibaba/PhotonLibOS/blob/main/doc/static/blog-20241014/stackful-coroutine-made-fast.html>
  - <https://github.com/alibaba/PhotonLibOS/issues>
  - <https://github.com/alibaba/PhotonLibOS/releases>
  - <https://github.com/alibaba/PhotonLibOS/issues/457>
  - <https://github.com/alibaba/PhotonLibOS/issues/1093>
  - <https://github.com/alibaba/PhotonLibOS/issues/748>
  - <https://github.com/alibaba/PhotonLibOS/issues/277>
  - <https://github.com/alibaba/PhotonLibOS/issues/137>
  - <https://github.com/alibaba/PhotonLibOS/issues/486>
  - <https://github.com/alibaba/PhotonLibOS/issues/396>
  - <https://github.com/alibaba/PhotonLibOS/issues/350>
  - <https://github.com/alibaba/PhotonLibOS/issues/1245>
  - <https://github.com/alibaba/PhotonLibOS/issues/1270>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/alibaba/photonlibos`) · [data/wave5/enrich/raw/github_com_alibaba_photonlibos.json](../../../data/wave5/enrich/raw/github_com_alibaba_photonlibos.json) (enrichment confidence 0.8)

</details>
