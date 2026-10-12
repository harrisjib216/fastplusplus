# G3log

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Unlicense` · 🟢 active

> Public-domain asynchronous C++ logger with crash-safe flush; \~3x lower call-site latency than Boost.Log, 3-4x slower than spdlog.

| | |
|---|---|
| **Beats** | Boost.Log (asynchronous_sink with text_ostream_backend, auto_flush off) in the Quill logger_benchmarks latency tables; also std::fstream with std::flush after every line and Boost.Log in the reckless doc/performance.md Disk I/O scenario (g3log is not faster than stdio fprintf+fflush there) |
| **Claimed result** | 1 thread: 2.9-3.2x lower latency than Boost.Log (derived from page data); 4-thread Boost.Log rows invalid (data race in the harness); g3log second-slowest in the table and 3-4x slower than spdlog. |
| **Workload** | Quill logger_benchmarks call-site latency: each observation is the average of 20 log calls made in a tight loop ('Logging int: {}, int: {}, double: {}' and a variant with a std::string over 35 characters), about 2 ms between observations, 1 and 4 caller threads, backend thread pinned to CPU 5; g3log LOG(INFO) to its default file logger vs Boost.Log BOOST_LOG_SEV to an asynchronous text sink. reckless Disk I/O: average latency of 2048 log calls, each interleaved in the same thread with writing 32 MiB to a new file (64 GiB over 2048 files), every library flushing to the OS per call; plus Mandelbrot total-overhead rows with 4 and 8 worker threads. |
| **Metric** | latency |
| **Hardware** | Quill tables: Intel Core i5-12600 (12th Gen) @ 4.8 GHz, RHEL 9.4, benchmark-tuned kernel (isolcpus=1-5, nohz_full, mitigations=off). reckless doc: AMD Ryzen 7 2700X 3.7 GHz, 8 cores, SMT off, 32 GiB RAM, Samsung 970 EVO SSD, Linux 4.14.65; its Disk I/O scenario wrote to a WD Red WD30EFRX 3 TB mechanical disk in a Synology DS216j NAS. |
| **Compiler and flags** | Quill tables: GCC 14.2, CMake Release with CMAKE_CXX_FLAGS -m64 -march=x86-64-v3 (logger_benchmarks CMakeLists.txt), C++20, static libraries, g3log built from source at commit 8217b08 per vendor_manifest.json (the README does not say which g3log commit produced the table). reckless doc: gcc 7.3.0, -O3 -ggdb3 -std=c++11 from Tuprules.lua; g3log 1.3.2 library build flags not stated. |
| **Adoption** | 965 stars |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/KjellKod/g3log) · [benchmark](https://github.com/odygrd/quill/blob/master/README.md) |

## Verdict

In odygrd/logger_benchmarks (Quill v13.0.0 README tables; GCC 14.2, -m64 -march=x86-64-v3, C++20, Intel Core i5-12600 with isolated cores), g3log's LOG(INFO) to its default file sink took 1066/1095/1143 ns at the 50th/90th/99.9th percentile versus 3093/3259/3621 ns for Boost.Log's asynchronous text sink with one caller thread (about 2.9-3.2x lower, derived from page data), and 838 versus 2844 ns at the median for large strings; g3log was slower than spdlog and every other logger in those tables. The reckless benchmark (gcc 7.3.0, Ryzen 7 2700X, g3log 1.3.2) shows g3log far below std::fstream with a flush per line under heavy disk I/O but slower than stdio fprintf+fflush.

## Use it when

- Applications that need the last log lines before a crash: queued messages and a stack dump reach the sink on SIGSEGV, SIGABRT, SIGFPE, SIGILL, SIGTERM, LOG(FATAL) or a failed CHECK.
- Moderate log rates (thousands to low hundreds of thousands of messages per second) where roughly 1 us per call is acceptable and disk stalls must not block the caller.
- Replacing Boost.Log, glog-style synchronous logging or std::fstream with a flush per line in code that already uses stream-style LOG(INFO) &lt;&lt; syntax.
- Projects that want public-domain (Unlicense) source with no third-party dependency for the default file sink, plus custom sinks (log rotation, syslog, colour terminal in g3sinks) added or removed at run time.

## Skip it when

- Latency-critical hot paths: in the Quill benchmark g3log's median call is 1066 ns (1 thread) and 1188 ns (4 threads), versus 271/557 ns for spdlog and 6-29 ns for fmtlog, Quill, XTR, PlatformLab NanoLog and binlog.
- Bursty high-volume logging: the queue is an unbounded mutex-protected std::queue with no back-pressure or drop policy, so memory grows while the sink falls behind, and all messages pass through one LogWorker thread.
- Processes that own their signal handling (PID 1, JVM or Python hosts, crash reporters, sanitizers): g3log installs its own fatal handlers by default, treats SIGTERM as fatal, and re-raises the signal after restoring the previous handler; disable it with ENABLE_FATAL_SIGNALHANDLING=OFF or overrideSetupSignals.
- Programs that leave through exit() or need structured or binary logs: the docs state queued entries are not flushed on exit(), and output is plain text only.

## How it is fast

Nothing is written to disk on the caller's thread: LogCapture formats into a std::ostringstream, copies the text into a heap-allocated LogMessage (timestamp, thread id, file, function) and pushes a std::function onto an Active object, a mutex-protected unbounded std::queue with a condition variable (shared_queue.hpp). The LogWorker thread then posts the message to each sink's own Active thread, and the default FileSink appends to a string buffer and flushes the std::ofstream every 100 messages. This beats loggers that format and write synchronously or take heavier locks, but every call still pays iostream formatting, two or more allocations, a mutex and a notify, about 1 us on a modern core.

## Compared with alternatives

Pick g3log over glog or loguru when you want logging off the caller's thread plus crash-time flushing and CHECK macros in a public-domain, dependency-free package; if call-site latency matters, Quill (which also lists a built-in crash signal handler), fmtlog or binlog run at 6-29 ns in the same harness and Iyengar NanoLog at 106 ns, 10-170x below g3log's 1066 ns median.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake; G3_SHARED_LIB defaults ON) |
| **Dependencies** | none for the default file sink (C++ standard library and pthreads); extra sinks live in KjellKod/g3sinks |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17 in CMakeLists.txt), CMake |
| **Platforms** | Linux, macOS and Windows (MSVC and MinGW) per docs/building.md; iOS build option; fatal-signal handling is POSIX-signal based on Unix and vectored exceptions on Windows |
| **Thread safety** | Thread-safe LOG calls from any thread (docs/API.md); initialize the logger before other threads log and destroy it after they stop |
| **Drop-in for the baseline** | no |

## Gotchas

- The fatal-signal handler is not async-signal-safe: it builds std::ostringstream text, calls backtrace_symbols and pushes the message through the same mutex queue, so a crash inside malloc or while a thread holds the queue lock can hang instead of flushing.
- Messages logged before initializeLogging are dropped; only the first one is printed to stderr as 'LOGGER NOT INITIALIZED'. Run-time level filtering needs USE_DYNAMIC_LOGGING_LEVELS=ON (default OFF), and the DEBUG level name can clash with other macros unless CHANGE_G3LOG_DEBUG_TO_DBUG=ON.
- Each sink runs its own background thread in addition to the LogWorker thread, so the default setup creates two threads, and messages hop two mutex queues before reaching the file.
- Benchmark harness flaw in the baseline: logger_benchmarks' Boost.Log harness shares one non-thread-safe src::severity_logger across all caller threads (Boost.Log documents the _mt variants as the thread-safe ones), so the 4-thread Boost.Log rows measure a data race; the 1-thread comparison (g3log about 2.9-3.2x lower latency) is unaffected.

## Known shortcomings

- Upgraded B to A on the Quill README benchmark (harness odygrd/logger_benchmarks, GCC 14.2, -march=x86-64-v3, i5-12600): 2.9-3.7x lower latency than Boost.Log on 1 thread, 1.3x median on 4 threads (derived from page data), but g3log is second-slowest there and about 3-4x slower than spdlog. In the reckless doc it is slower than stdio and the 186x over fstream comes from a NAS-disk write storm; reckless g3log.hpp is 404. Unlicense, no patent grant.
- Enricher: the call site costs about 1 us (ostringstream, heap LogMessage, std::function, then a mutex+condvar unbounded std::queue with no backpressure) and each sink adds its own thread; the fatal handler is not async-signal-safe (allocates and locks inside the handler) and SIGTERM is treated as fatal; messages before initializeLogging are dropped. The logger_benchmarks Boost.Log harness shares a non-thread-safe src::severity_logger across 4 threads (data race), so the 4-thread Boost.Log rows are invalid; the 1-thread rows (2.9-3.2x) stand.

## Caveats and trade-offs

g3log beats only the slowest or synchronous baselines. In the Quill tables it is second-slowest, ahead of Boost.Log only, and roughly 3-4x slower than spdlog at every percentile; it is absent from Quill's complex-type and throughput tables. Both benchmark pages are written by authors of competing libraries (Quill, reckless). In the reckless doc the 186x figure is std::fstream with std::flush blocking behind a 64 GiB write storm to a NAS mechanical disk, and g3log is slower than plain stdio fprintf+fflush in that same table; across the other reckless scenarios g3log is slow: periodic calls 78.19 vs stdio 43.77, fstream 41.32, spdlog 40.85, boost_log 67.42 (slowest listed), call burst 4.20 vs stdio 2.55, fstream 2.36, boost_log 3.84, Mandelbrot single thread 13.40 vs stdio 12.21, fstream 10.73. The reckless g3log wrapper benchmarks/g3log.hpp is not in the repo (404 at master), so those rows cannot be rebuilt from public code, and they use g3log 1.3.2 with gcc 7.3.0. The README's \~2 us figure is first-party on 2010 hardware with no baseline; the author's worst-case-latency blog post was not reachable. Unlicense public-domain dedication: no patent grant. [retier] Call site about 1 us; unbounded queue with no backpressure; one thread per sink; fatal handler not async-signal-safe, SIGTERM treated as fatal; messages before initializeLogging dropped; reckless 186x over fstream is a NAS write storm; Unlicense, no patent grant.

Asynchronous logger: log calls format the message at the call site and push it to a queue serviced by a background sink thread, with dynamic sinks and crash-safe flush on fatal signals. Messages queued at a crash are written by the signal handler; throughput is bounded by the single background thread. Unlicense/public domain gives no patent grant.

## Maintenance

Active (last commit 2026-09-04, 965 stars, no open issues listed), Unlicense public domain with no patent grant, and a small dependency-free codebase that is easy to vendor; its queue design dates from 2010 and has not been modernised for low latency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A on stronger evidence: the Quill README Performance section times g3log against Boost.Log with public harness code (odygrd/logger_benchmarks benchmarks/call_site_latency/benchmark_g3log_call_site_latency.cpp and benchmark_boost_log_call_site_latency.cpp, g3log built from source at pinned commit 8217b08), GCC 14.2, CMake Release with -m64 -march=x86-64-v3, on an Intel Core i5-12600; same harness that gave Iyengar NanoLog its A in wave 11 batch-33. The reckless doc alone would stay B because its g3log wrapper benchmarks/g3log.hpp is missing (404).
- **Verifier notes:** Reckless numbers in the record are accurate, but its workload said the 64 GiB were written 'in parallel' (they are interleaved in the logging thread) and its hardware omitted the NAS disk used for the Disk I/O scenario; both corrected. Found a stronger third-party source: the Quill README (code in odygrd/logger_benchmarks) shows g3log 2.9-3.7x lower latency than Boost.Log, so benchmark_url and baseline now point there; the main shortcoming to record is that g3log is slower than spdlog, stdio and every async logger except Boost.Log. Metadata checked: Unlicense (LICENSE file), 965 stars, not archived, last commit 2026-09-04.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 11); enricher w11 pair-026
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/doc/performance.md>
  - <https://github.com/mattiasflodin/reckless/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/write_files.cpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/Tupfile.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/Tuprules.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/g3log.hpp>
  - <https://raw.githubusercontent.com/odygrd/quill/master/README.md>
  - <https://github.com/odygrd/logger_benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks/call_site_latency>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/vendor_manifest.json>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_g3log_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_boost_log_call_site_latency.cpp>
  - <https://github.com/KjellKod/g3log>
  - <https://github.com/KjellKod/g3log/commits>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/KjellKod/g3log>
  - <https://github.com/KjellKod/g3log/issues>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/README.md>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/active.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/shared_queue.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/sink.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/filesink.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/filesink.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/logcapture.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/logworker.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/logworker.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/logmessage.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/g3log/g3log.hpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/src/crashhandler_unix.cpp>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/Options.cmake>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/docs/building.md>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/docs/API.md>
  - <https://raw.githubusercontent.com/KjellKod/g3log/master/docs/g3log_usage.md>
  - <https://raw.githubusercontent.com/odygrd/quill/master/README.md>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_g3log_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_boost_log_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/call_site_latency_bench.h>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/vendor_manifest.json>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/sources.qbk>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/kjellkod/g3log`) · [data/wave11/enrich/raw/github_com_kjellkod_g3log.json](../../../data/wave11/enrich/raw/github_com_kjellkod_g3log.json) (enrichment confidence 0.6)

</details>
