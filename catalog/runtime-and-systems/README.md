# Runtime and systems

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Allocators, coroutines, thread pools, logging, profilers and file I/O measured against malloc, spdlog, TBB and the POSIX defaults.

**176 entries in 6 categories:** 25 tier A · 25 tier B · 106 tier C · 20 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Allocators and garbage collectors](allocators-gcs/README.md) | 32 | 4 | 4 | 21 | 3 | malloc, jemalloc, mimalloc, Boehm GC |
| [Coroutines and fibers](coroutines-fibers/README.md) | 23 | 1 | 1 | 18 | 3 | Boost.Context, Boost.Coroutine, libco |
| [Filesystems and I/O](filesystems-and-io/README.md) | 50 | 1 | 11 | 34 | 4 | POSIX read/write, mmap, io_uring baselines |
| [Logging and tracing](logging-tracing/README.md) | 25 | 14 | 1 | 9 | 1 | spdlog, glog, OpenTelemetry SDK |
| [Profilers and instrumentation](profilers-and-instrumentation/README.md) | 22 | 0 | 5 | 12 | 5 | perf, gprof, Valgrind |
| [Thread pools and work stealing](thread-pools-work-stealing/README.md) | 24 | 5 | 3 | 12 | 4 | Intel TBB, OpenMP, Rayon |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**Quill**](logging-tracing/odygrd-quill.md) | Asynchronous C++17 logger whose LOG_INFO call site costs single-digit nanoseconds, about 45x below async spdlog at p50. | [Logging and tracing](logging-tracing/README.md) | **A** | C++ | MIT | 🟢 active |
| 2 | [**loguru**](logging-tracing/emilk-loguru.md) | Two-file synchronous C++ logger with printf-style LOG_F; 1.8x lower per-line cost than glog 0.6.0 single-threaded, mixed under contention. | [Logging and tracing](logging-tracing/README.md) | **A** | C++ | Unlicense | 🟢 active |
| 3 | [**G3log**](logging-tracing/kjellkod-g3log.md) | Public-domain asynchronous C++ logger with crash-safe flush; \~3x lower call-site latency than Boost.Log, 3-4x slower than spdlog. | [Logging and tracing](logging-tracing/README.md) | **A** | C++ | Unlicense | 🟢 active |
| 4 | [**phuslu/log**](logging-tracing/phuslu-log.md) | Zero-allocation structured JSON logger for Go, faster than zerolog, zap and log/slog in its own benchmarks. | [Logging and tracing](logging-tracing/README.md) | **A** | Go | MIT | 🟢 active |
| 5 | [**Intel Parallel STL**](thread-pools-work-stealing/intel-parallelstl.md) | Intel's C++17 parallel algorithms (now oneDPL; libstdc++'s &lt;execution&gt;): std::reduce(par) on oneTBB beats serial std::accumulate \~98x. | [Thread pools and work stealing](thread-pools-work-stealing/README.md) | **A** | C++ | Apache-2.0 WITH… | 🟢 active |
| 6 | [**BqLog**](logging-tracing/tencent-bqlog.md) | Tencent's C++ async logger with a real-time compressed binary format; much higher end-to-end throughput than spdlog async and glog. | [Logging and tracing](logging-tracing/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**SGCL**](allocators-gcs/pebal-sgcl.md) | Header-only C++20 concurrent garbage collector whose allocation path beats malloc-backed unique_ptr/shared_ptr for small objects on macOS. | [Allocators and garbage collectors](allocators-gcs/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**zlob**](filesystems-and-io/dmtrkovalenko-zlob.md) | Zig glob(3)-compatible globbing and parallel file walker with C/Rust APIs; about 2-3x faster than Rust glob crate and walkdir. | [Filesystems and I/O](filesystems-and-io/README.md) | **A** | Zig | MIT | 🟢 active |
| 9 | [**haclog**](logging-tracing/mugglewei-haclog.md) | Plain C async printf-style logger; producer-side calls about 3.5x faster than spdlog when buffers are not full. | [Logging and tracing](logging-tracing/README.md) | **A** | C | MIT | 🟢 active |
| 10 | [**XTR**](logging-tracing/choll-xtr.md) | C++20 low-latency logger: per-thread SPSC ring buffer plus background {fmt} consumer; about 6-10 ns call-site latency vs spdlog async's 271-360 ns. | [Logging and tracing](logging-tracing/README.md) | **A** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
