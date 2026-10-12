# Condy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 coroutine runtime over io_uring: \~1.22x epoll TCP recv throughput, matches raw liburing, cheaper coroutines than Asio.

| | |
|---|---|
| **Beats** | epoll |
| **Claimed result** | Network recv single-shot at 2048B: Condy 2110 MB/s vs Epoll 1734 MB/s (\~1.22x, derived from page data) and vs Asio 1588 MB/s (\~1.33x, derived from page data); multi-shot 2610 MB/s vs raw io_uring 2560 MB/s (parity). 4KB random read at QD=128: best Condy config (fixed+direct+IOPoll) 598K IOPS, which the page calls roughly 2x Monoio/Compio (310K/297K were their Direct IO results) and 3x libaio (\~200K); under the same Direct IO config Condy 345K vs Monoio 310K (1.11x). Channel 15x faster than Asio (2M messages: 39ms vs 598ms); coroutine spawn 6.6x over Asio (4M tasks: 236ms vs 1566ms); coroutine switch 16x over Asio (8M switches: 28ms vs 449ms). |
| **Workload** | Single-machine TCP recv throughput, varying message sizes, single-shot and multi-shot io_uring modes, vs Asio, Epoll, raw liburing, Monoio, Compio; also 4KB random file read IOPS, channel messaging, coroutine spawn/switch microbenchmarks |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7945HX x16, SK Hynix HFS001TEJ9X115N NVMe SSD 1TB PCIe4, Linux Mint 22 Cinnamon, kernel 7.0.0-14-generic |
| **Compiler and flags** | clang 18.1.3; CMAKE_BUILD_TYPE=Release (-O3 -DNDEBUG) per the condy-bench README build instructions; Rust baselines built with cargo --release |
| **Adoption** | 22 stars |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/condy-cpp/condy) · [benchmark](https://github.com/condy-cpp/condy/blob/master/docs/bench.md) |

## Verdict

On one Ryzen 9 7945HX machine (Linux 7.0, clang 18.1.3, Release build), a loopback TCP recv server pinned to one core with 16 client connections reached 2110 MB/s with Condy single-shot recv at 2048 B messages. That compares with 1734 MB/s for a plain level-triggered epoll+recv server (\~1.22x), 1588 MB/s for Asio without io_uring (\~1.33x), and near-parity between Condy multishot (2610 MB/s) and raw liburing (2560 MB/s). For 4 KB random O_DIRECT reads at QD 128, Condy reached 345K IOPS vs Monoio's 310K, and 598K with fixed files, registered buffers and IOPOLL, vs 601K for raw liburing and \~200K for libaio.

## Use it when

- Linux TCP servers or proxies where you would otherwise hand-write an epoll loop and want straight-line coroutine code; the published recv test used 16 connections with 64 B to 2 KB messages.
- High queue-depth NVMe reads with O_DIRECT, where fixed files, registered buffers and IOPOLL take Condy to raw-liburing IOPS (598K vs 601K for 4 KB random reads at QD 128).
- Code that needs io_uring-only features (multishot accept/recv, provided-buffer rings, linked ops, zero-copy tx/rx, uring_cmd for ublk or NVMe passthrough) without hand-rolling liburing state machines.
- Thread-per-core designs: one Runtime per core, with Channel and co_switch for handoff between cores.
- Task-heavy code where Asio's coroutine overhead shows: 56 ns per spawn vs 373 ns for Asio, about 3.3 ns per switch, and 15x faster channel messaging than Asio in the author's benchmarks.

## Skip it when

- Cross-platform code (macOS, Windows, BSD) or Linux older than 6.0: it is io_uring-only, and the Runtime constructor throws if the ring cannot be created.
- If you want a multithreaded, work-stealing executor. Each Runtime is single-threaded, and the author says to start one per core and shard the work yourself.
- If you need a long production track record. The project has 22 stars, reached v1.0 in January 2026, and fixed deadlocks in August 2026 (#188 allow_exit+join, #189 CancelRequest) plus a nested-runtime panic (#177).
- If you already use raw liburing and are happy with it. Condy only matches it (2610 vs 2560 MB/s multishot recv; 598K vs 601K IOPS), so you would gain ergonomics, not speed.
- If you need protocol layers. It is a system-call layer, and the source tree has no HTTP, TLS or DNS support.

## How it is fast

It uses io_uring's completion model: the kernel performs the recv or read and posts a CQE, so there is no readiness notification followed by a separate recv syscall per event, as there is with epoll. Without SQPOLL, SQEs accumulate and go to the kernel in one io_uring_submit_and_wait call per loop iteration, and CQEs are reaped in batches. The ring is created with SINGLE_ISSUER and SUBMIT_ALL and its fd is registered. Each operation's state lives in its awaiter inside the coroutine frame, and the CQE's user_data is a tagged pointer to that state; the README says this removes nearly all heap allocations outside coroutine frames. The run queues are intrusive lists, and wakeups across runtimes use IORING_OP_MSG_RING. Most of the gain comes from exposing io_uring features (multishot recv with provided-buffer rings, fixed files, registered buffers, IOPOLL). Condy matches raw liburing rather than beating it.

## Compared with alternatives

Pick Condy over Asio's io_uring backend when you are Linux-only and want io_uring-specific features (multishot recv, provided-buffer rings, fixed files/buffers, linked SQEs, zero-copy rx/tx) behind C++20 coroutines. Pick it over uring_exec because that stdexec-based library has been effectively archived since 2025. Monoio is the Rust equivalent: Condy's bench puts Condy 1.12x ahead of Monoio on single-shot recv and about even on spawn and switch cost.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target `condy`; optional C++20 module target `condy_module`) |
| **Dependencies** | liburing &gt;= 2.3. By default CMake downloads liburing 2.15 with FetchContent and links it statically; CONDY_LINK_LIBURING=OFF uses the system copy. |
| **Minimum toolchain** | C++20, GCC or Clang. CI builds with GCC 14 and Clang, and pins GCC 14 because of a GCC 15 regression. CMake 3.13+ (the module needs CMake 3.28+ with Ninja and GCC 14+ or Clang 16+). In practice it needs Linux 6.0+, because IORING_SETUP_SINGLE_ISSUER is always set; no minimum kernel is documented. |
| **Platforms** | Linux only (io_uring). CI runs on x86-64 Ubuntu runners plus a QEMU x86-64 job on the latest kernel (7.2); other architectures are not documented. |
| **Thread safety** | Each Runtime is single-threaded, and run() may only ever be called from one thread (it throws otherwise). co_spawn onto another runtime, Task wait/detach, allow_exit() and Channel (mutex-based) are thread-safe; wakeups across runtimes go through IORING_OP_MSG_RING. |
| **Drop-in for the baseline** | no |

## Gotchas

- The program terminates if a spawned Task is neither awaited nor detached, or if a detached task throws. Internal ring errors call panic_on instead of returning an error.
- Runtime::run() does not return when idle unless allow_exit() has been called (sync_wait does this for you). Multishot operations deliver every result except the last to a callback, and only the final result resumes the coroutine.
- Kernel/liburing skew: build.md warns that features compiled in from a newer liburing can fail at runtime on an older kernel, and SINGLE_ISSUER (Linux 6.0+) is set unconditionally.
- Build: the default configure step downloads and builds liburing, which needs network access and make. The FetchContent snippet in build.md pins tag v1.9, but the newest tag is v1.8 (2026-07-24).

## Known shortcomings

- Margins are modest (about 1.22x over epoll, 1.33x over Asio on recv); the '2x over Monoio' compares different setups (1.11x like-for-like). io_uring only, so Linux-only.
- Effectively Linux 6.0+ (always sets IORING_SETUP_SINGLE_ISSUER). Only matches raw liburing, so the gain over epoll is io_uring's; the epoll baseline is a plain one-recv-per-event loop and Asio ran without its io_uring backend. Single-threaded runtimes (one per core, shard yourself). GCC 15 regression (CI pins GCC 14); build.md pins a nonexistent v1.9 tag. 22 stars, v1.0 in 2026-01.

## Caveats and trade-offs

Flags come from the condy-bench README (Release build type), not from docs/bench.md itself. Results are shown as chart images (.png) with numeric callouts in prose; raw CSVs are produced by the scripts but not published. The 2x-over-Monoio figure compares Condy's best config (fixed files, registered buffers, IOPoll) with Monoio's Direct IO result; like-for-like Direct IO is 1.11x. Against raw liburing Condy is at parity, so the win over epoll comes from io_uring itself. Author-run, single machine; project is new with low adoption.

Linux-only (io_uring); requires liburing &gt;= 2.3; small young project with few stars; benchmark repo (condy-bench) is separate from main repo so numbers not reproduced inline

## Maintenance

Actively developed and MIT-licensed. v1.0 shipped January 2026, v1.8 July 2026, and master is at v1.9 with commits through 2026-09-05, and std::execution support is in open PRs. It is header-only and easy to vendor, but young and lightly adopted (22 stars, one filed issue).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/bench.md compares Condy with a plain epoll server, Asio, raw liburing, libaio, Monoio and Compio, and states the CPU (AMD Ryzen 9 7945HX) and the compiler (clang 18.1.3). The linked benchmark code is public in condy-cpp/condy-bench (benchmarks/recv/{condy,epoll,asio,uring}.cpp, driven by scripts/recv.py), and its README fixes the flags with -DCMAKE_BUILD_TYPE=Release (CMake's -O3 -DNDEBUG), so all A criteria are met.
- **Verifier notes:** All numbers match docs/bench.md; the epoll and Asio ratios were computed by the search agent, so they are now marked as derived. last_commit corrected to the master-branch head (2026-09-05); the 2026-09-23 date is a push to the integrate-std-execution branch. Metadata checked: MIT, not a fork, not archived, 22 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/condy-cpp/condy>
  - <https://github.com/condy-cpp/condy/blob/master/docs/bench.md>
  - <https://github.com/condy-cpp/condy-bench>
  - <https://github.com/condy-cpp/condy-bench/blob/master/README.md>
  - <https://github.com/condy-cpp/condy-bench/blob/master/CMakeLists.txt>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/condy-cpp/condy-bench/blob/master/.github/workflows/build.yml>
  - <https://github.com/condy-cpp/condy-bench/blob/master/scripts/recv.py>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/recv/epoll.cpp>
- **Sources the enricher read:**
  - <https://github.com/condy-cpp/condy>
  - <https://github.com/condy-cpp/condy/blob/master/README.md>
  - <https://github.com/condy-cpp/condy/blob/master/docs/bench.md>
  - <https://github.com/condy-cpp/condy/blob/master/docs/build.md>
  - <https://github.com/condy-cpp/condy/blob/master/docs/guide.md>
  - <https://github.com/condy-cpp/condy/blob/master/docs/ops.md>
  - <https://github.com/condy-cpp/condy/blob/master/CMakeLists.txt>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/runtime.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/detail/ring.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/detail/coro.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/detail/op_states.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/channel.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/senders.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/include/condy/version.hpp>
  - <https://github.com/condy-cpp/condy/blob/master/.github/workflows/ci-main.yml>
  - <https://github.com/condy-cpp/condy/blob/master/.github/workflows/ci-toolchain.yml>
  - <https://github.com/condy-cpp/condy/blob/master/.github/workflows/ci-latest-kernel.yml>
  - <https://github.com/condy-cpp/condy/issues>
  - <https://github.com/condy-cpp/condy/issues/32>
  - <https://github.com/condy-cpp/condy/pulls>
  - <https://github.com/condy-cpp/condy/releases>
  - <https://github.com/condy-cpp/condy/tags>
  - <https://github.com/condy-cpp/condy/commits/master>
  - <https://github.com/condy-cpp/condy-bench>
  - <https://github.com/condy-cpp/condy-bench/blob/master/README.md>
  - <https://github.com/condy-cpp/condy-bench/blob/master/CMakeLists.txt>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/recv/epoll.cpp>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/recv/condy.cpp>
  - <https://github.com/condy-cpp/condy-bench/blob/master/benchmarks/recv/asio.cpp>
  - <https://github.com/condy-cpp/condy-bench/blob/master/scripts/recv.py>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_setup.2>
  - <https://github.com/Caturra000/uring_exec>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/condy-cpp/condy`) · [data/wave5/enrich/raw/github_com_condy_cpp_condy.json](../../../data/wave5/enrich/raw/github_com_condy_cpp_condy.json) (enrichment confidence 0.85)

</details>
