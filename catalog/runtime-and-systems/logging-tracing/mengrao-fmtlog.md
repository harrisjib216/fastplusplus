# fmtlog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Asynchronous fmt-syntax C++ logger with about 6 ns caller-side latency per call, versus 150-400 ns for synchronous spdlog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | README (bench/bench.cc, Xeon Gold 6144, spdlog basic_logger_st): staticString 6.4 ns vs spdlog 156.4 ns; stringConcat 6.4 vs 209.4; singleInteger 6.3 vs 202.3; twoIntegers 6.4 vs 257.2; singleDouble 6.2 vs 225.0; complexFormat 6.4 vs 390.9 ns. Quill README (int,int,double, 1 thread): fmtlog 6 ns vs spdlog 271 ns at p50; 4 threads 8 vs 557 ns; std::vector&lt;std::string&gt; 1 thread 774 vs 6906 ns. Backend throughput in quill's table is near parity: fmtlog 2.69M msg/s vs spdlog 2.57M msg/s. |
| **Workload** | Caller-thread latency per log call for six message types (static string, string concat, integers, double, complex format) using spdlog default header pattern, with throughput also reported. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-12600 @ 4.8 GHz, RHEL 9.4, isolated cores, tuned for benchmarking; own README run on Intel Xeon Gold 6144 @ 3.50GHz |
| **Compiler and flags** | GCC 14.2, Release, -march=x86-64-v3 (per quill README); own README says GCC 10.2 tested |
| **Adoption** | 1.0k stars |
| **Last commit** | 2025-02-13 |
| **Links** | [repository](https://github.com/MengRao/fmtlog) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

In quill's logger_benchmarks harness (GCC 14.2, Release -march=x86-64-v3, Intel Core i5-12600 with isolated cores), the caller-thread p50 for an int,int,double message was 6 ns for fmtlog vs 271 ns for spdlog with 1 thread, and 8 vs 557 ns with 4 threads; a 16-string vector cost 774 vs 6906 ns. fmtlog's own bench.cc on a Xeon Gold 6144 (flags not stated) gives about 6.4 ns vs 156-391 ns against synchronous spdlog basic_logger_st, but backend file throughput is about the same as spdlog's (2.69 vs 2.57M msg/s).

## Use it when

- Latency-critical x86-64 threads (trading, market data, game servers) where a single-digit-ns log call matters more than when the message reaches disk
- Code already using fmt-style format strings that wants human-readable text logs, not NanoLog's binary format that needs a decompressor
- Apps that want to control the backend thread themselves: call poll() from an existing event loop or housekeeping thread
- Many logging threads: per-thread SPSC queues avoid the shared-queue contention that slows spdlog async as thread count grows (quill harness: 8 ns at 4 threads vs spdlog 557 ns p50)

## Skip it when

- Backend throughput is what limits you: quill's table has fmtlog writing 2.69M msg/s, about the same as spdlog's 2.57M and well behind XTR (7.73M) and Quill (6.44M)
- Every message must survive: by default a full queue silently drops new messages (FMTLOG_BLOCK=1 blocks instead), and open issues #109 and #117 report lost logs in multithreaded tests
- You need recent fmt or MSVC/LLVM toolchains: issue #98 (fmt 10.1 compile error), #71 (VS2022) and #91 (LLVM COMDAT) are open; the code reaches into fmt::detail internals
- Non-x86 targets: the SPSC queue publishes through volatile stores with no release/acquire fences, which is fine under x86 TSO but not guaranteed on weakly ordered CPUs such as aarch64, and the TSC clock falls back to a system clock call there
- You need active maintenance: last commit 2025-02-13, 31 open issues including segfault (#115) and destructor core dump (#112) reports with no maintainer reply

## How it is fast

It borrows NanoLog's two ideas. First, each logging thread gets its own variable-size single-producer/single-consumer ring (SPSCVarQueueOPT, 1 MB by default), so producers never contend. Second, a log site's static data (format string, level, location) is registered once in a table, and each call pushes only the table index, an rdtsc timestamp and the raw argument bytes; a per-site decode function formats the message later in poll(). Timestamps are raw TSC values that a calibrated TSCNS clock converts to nanoseconds on the backend.

## Compared with alternatives

Pick fmtlog over Quill or XTR when you want a small two-header fmt-based logger whose backend runs only when you call poll(); Quill matches its caller latency (6 ns p50), has higher backend throughput and is maintained, so choose Quill for production. Pick it over PlatformLab NanoLog when you want fmt syntax and readable text output and do not need a binary log plus decompressor.

## Integration

| | |
|---|---|
| **Form** | header-only (define FMTLOG_HEADER_ONLY or include fmtlog-inl.h once) or static/shared lib via CMake |
| **Dependencies** | fmtlib (bundled as a git submodule at a pinned commit), pthread |
| **Minimum toolchain** | C++17; README says GCC 10.2 and MSVC 2019 tested |
| **Platforms** | Linux and Windows documented; x86/x86-64 for the rdtsc fast path; other architectures compile against a system clock fallback, but the queue's memory ordering there is not documented |
| **Thread safety** | Any number of threads may log; only one thread may call poll(), and not while startPollingThread is running |
| **Drop-in for the baseline** | no |

## Gotchas

- Arguments passed by pointer (including std::string\*, shared_ptr, unique_ptr) are read when poll() runs, not when the log call runs: a value changed in between gets logged with its new value, and a freed object leaves a dangling pointer
- The first log call on a thread allocates its 1 MB queue; call fmtlog::preallocate() at thread start or that first call pays the allocation cost
- Each log site costs about 50 bytes of code for its decode function plus about 50 bytes of runtime table memory; use FMTLOG_ONCE (logio etc.) for cold logs
- FMTLOG_ACTIVE_LEVEL compile-time filtering applies only to the short macros (logi, logd...), not to FMTLOG(); the README says the default is INF but fmtlog.h defines FMTLOG_LEVEL_DBG

## Known shortcomings

- Backend throughput is only at parity with spdlog (2.69 vs 2.57M msg/s); the win is caller latency. Open issues 109 and 117 (lost logs), 98 (fmt 10.1 compile failure), 115 (segfault) and 112 (destructor coredump), with no maintainer replies. The SPSC queue uses volatile with no fences, so it is safe on x86 TSO only and aarch64 ordering is unsafe. README says the default level is INF but the header defines DBG.

## Caveats and trade-offs

Own README table at https://github.com/MengRao/fmtlog (compiler flags not stated there; spdlog run as synchronous basic_logger_st, so its latency includes formatting and I/O). Tier A relies on quill's harness (odygrd/logger_benchmarks, quill is a competing logger). The gain is caller-thread latency only: backend throughput to file is roughly equal to spdlog (2.69 vs 2.57M msg/s in quill's table).

Requires fmtlib and C++17; user must call fmtlog::poll() to drain queues; default drops messages when the 1 MB per-thread queue is full (FMTLOG_BLOCK=1 blocks instead); Linux/GCC tested.

## Maintenance

Stale since 2025-02-13, with open crash, lost-message and fmt-compatibility issues and no maintainer replies; MIT-licensed and small (two headers) enough to vendor with its pinned fmt submodule.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Quill README performance section (benchmark code in odygrd/logger_benchmarks, GCC 14.2, Release with -march=x86-64-v3, Intel Core i5-12600) shows fmtlog 6 ns vs spdlog 271 ns p50 on 1-thread numbers; fmtlog's own bench/bench.cc table on Xeon Gold 6144 matches the record's numbers but states no flags.
- **Verifier notes:** Numbers confirmed on both pages. Last commit 2025-02-13 (stale), MIT, 1.0k stars, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/odygrd/quill#-performance>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/README.md>
  - <https://github.com/MengRao/fmtlog>
  - <https://github.com/MengRao/fmtlog/commits/main>
  - <https://github.com/odygrd/logger_benchmarks>
- **Sources the enricher read:**
  - <https://github.com/MengRao/fmtlog>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/fmtlog.h>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/fmtlog-inl.h>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/fmtlog.cc>
  - <https://raw.githubusercontent.com/MengRao/fmtlog/HEAD/CMakeLists.txt>
  - <https://github.com/MengRao/fmtlog/issues>
  - <https://github.com/MengRao/fmtlog/issues/117>
  - <https://github.com/MengRao/fmtlog/issues/105>
  - <https://github.com/MengRao/fmtlog/issues/98>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mengrao/fmtlog`) · [data/wave11/enrich/raw/github_com_mengrao_fmtlog.json](../../../data/wave11/enrich/raw/github_com_mengrao_fmtlog.json) (enrichment confidence 0.85)

</details>
