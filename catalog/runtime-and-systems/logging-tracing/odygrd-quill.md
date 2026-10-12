# Quill

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Asynchronous C++17 logger whose LOG_INFO call site costs single-digit nanoseconds, about 45x below async spdlog at p50.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Bounded dropping queue 6/9 ns vs spdlog 271/360 ns (50th/99.9th, 1 thread); 8/18 vs spdlog 557/1106 (4 threads). Throughput 6.44M msg/s vs spdlog 2.57M (README). Beats g3log (1066 ns) and Boost.Log (3093 ns) at 1 thread; fmtlog and XTR are about equal. |
| **Workload** | Call-site latency of LOG_INFO with two ints and a double, 1 and 4 producer threads, asynchronous file logging. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-12600 @ 4.8 GHz, tuned system (isolcpus, nohz_full, mitigations=off), RHEL 9.4 |
| **Compiler and flags** | GCC 14.2, Release, -march=x86-64-v3 |
| **Adoption** | 3.0k stars; packaged in vcpkg, Conan, Homebrew |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/odygrd/quill) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

In the author's public logger_benchmarks harness (GCC 14.2, Release, -march=x86-64-v3, Intel Core i5-12600 on a tuned RHEL 9.4 with isolcpus and mitigations=off), a LOG_INFO with two ints and a double costs 6/9 ns (p50/p99.9) on one thread with Quill's bounded dropping queue versus 271/360 ns for spdlog's async_logger (8M-slot thread pool, block overflow policy, basic_file_sink_st), and 8/18 versus 557/1106 ns with 4 threads; each observation averages 20 back-to-back calls timed with serialized rdtsc. Backend throughput writing 4M messages to a file was 6.44M msg/s versus spdlog's 2.57M.

## Use it when

- Latency-critical hot paths (trading, real-time control, game servers) where the caller thread must spend under \~20 ns per log call with ints, doubles and short strings.
- Multi-threaded producers: per-thread SPSC queues keep p99.9 at 17-18 ns with 4 threads in the author's harness, where async spdlog reaches 1106 ns.
- Logging STL containers and large strings on the hot path: vector&lt;string&gt; of 16 strings costs 53 ns p50 versus 6906 ns for spdlog and about 750 ns for fmtlog/XTR.
- Projects that want human-readable text logs plus a broad feature set (rotation, JSON, backtrace ring buffer, MDC, filters, Prometheus metrics) rather than a binary log format.
- Linux, macOS, Windows, BSD or Android targets with a C++17 compiler and packaging through vcpkg, Conan, Homebrew, Meson, Bazel or Conda.

## Skip it when

- Raw text throughput is the goal: in the same harness XTR writes 7.73M msg/s versus Quill's 6.44M, and MS BinLog (61.79M) and BqLog (12.86M) binary modes are far ahead if you accept offline decoding.
- Memory-constrained processes with many logging threads: every thread gets its own queue (131,072 bytes default, growing in unbounded mode), and a third-party BqLog benchmark reported multi-GB peak use at 10 threads.
- You need every message delivered under overload without blocking: the bounded dropping queue (used for the headline numbers) discards messages when full, and the unbounded queue trades that for memory growth.
- Programs that log from static/global destructors or fork() after starting the backend: the README documents both as unsafe.
- Synchronous logging where the message must be on disk before the call returns; Quill is built around a background worker and an explicit flush_log().

## How it is fast

Each producer thread owns a lock-free single-producer/single-consumer queue, so there is no shared state or contention between logging threads. The call site stores only a timestamp (rdtsc by default), a pointer to static constexpr metadata (format string, source location), a logger pointer, a pointer to a templated decode function and a raw binary copy of the arguments; all {fmt} formatting, pattern formatting and I/O is deferred to the backend thread, which merges the per-thread queues in timestamp order. spdlog's async logger, by contrast, formats the message on the caller before queueing it.

## Compared with alternatives

Pick Quill over fmtlog or XTR when you log containers or long strings (53 ns vs about 750 ns for vector&lt;string&gt;) or want rotation, JSON, MDC and metrics in one maintained package; pick MS BinLog or BqLog binary mode instead for maximum throughput if offline decoding is acceptable, and PlatformLab NanoLog only if you can live with its binary log and preprocessor.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none external (bundles {fmt} as the fmtquill namespace; links Threads; stdc++fs on GCC &lt; 9) |
| **Minimum toolchain** | C++17, CMake 3.12+ (experimental C++20 named module optional) |
| **Platforms** | Linux, macOS, Windows, FreeBSD/BSD, Android; rdtsc clock on x86 with chrono/system clock alternatives |
| **Thread safety** | Logging from any thread is safe; each thread gets its own SPSC queue and one backend thread consumes them all. |
| **Drop-in for the baseline** | partial — same {fmt} format-string syntax as spdlog, but a different setup API (Frontend/Backend, sinks) and LOG_\* macros taking a logger pointer; user-defined types need codecs or the quill/std/\*.h headers for STL types. |

## Gotchas

- Arguments are copied at the call site and formatted later on the backend thread, so user-defined types need a codec (or must be formatted to a string first) and STL types need their quill/std/\*.h include.
- Queue type and capacity are compile-time FrontendOptions; the README benchmark ran the bounded dropping queue at 262,144 bytes, twice the default, and benchmark builds use the macro API, which is faster than the function API (11 versus 6 ns p50).
- Quill's own singletons are function-local statics: logging from destructors of static objects can touch destroyed state, and calling Backend::start() before fork() breaks the child.
- Messages from different threads are reordered by timestamp on the backend with a configurable grace window, so late producers can appear out of strict order unless that window is tuned.

## Known shortcomings

- The headline uses a bounded dropping queue at 262,144 B (2x the default), which can drop messages. Throughput is not the leader: XTR reaches 7.73M msg/s against Quill's 6.44M.

## Caveats and trade-offs

Benchmark run and published by the Quill author, though code is public at odygrd/logger_benchmarks. Latency measures the call site only (each observation averages 20 calls); spdlog was in its default configuration. fmtlog and XTR tie or beat Quill on several latency tables; MS BinLog and BqLog binary modes exceed it on throughput.

Formatting deferred to a backend thread; bounded dropping queue may drop messages; unbounded queue can grow to 64 MiB per thread (BqLog benchmark saw 2.7 GB peak at 10 threads).

## Maintenance

Actively maintained (v13 line, 3.0k stars, last commit 2026-10-04, CI on Linux/macOS/Windows/BSD with sanitizers and fuzzing), MIT-licensed and header-only, so it is easy to adopt through any major package manager.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance section states Quill v13.0.0, GCC 14.2, Release with -march=x86-64-v3, Intel Core i5-12600, tuned RHEL 9.4 kernel cmdline, and links public benchmark code at odygrd/logger_benchmarks; numbers vs spdlog match the record.
- **Verifier notes:** MIT confirmed from LICENSE; 3.0k stars; last commit 2026-10-04 (active). dev.to throughput claim superseded by README throughput table.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/LICENSE>
  - <https://github.com/odygrd/quill>
  - <https://github.com/odygrd/quill/commits/master>
  - <https://github.com/odygrd/logger_benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/CMakeLists.txt>
  - <https://github.com/odygrd/quill>
  - <https://github.com/odygrd/quill/issues?q=is%3Aissue+label%3Abug>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/README.md>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks/call_site_latency>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/benchmarks/call_site_latency/benchmark_spdlog_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/benchmarks/call_site_latency/benchmark_quill_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/benchmarks/call_site_latency/benchmark_quill_frontend_options.h>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/benchmarks/call_site_latency/call_site_latency_bench.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/odygrd/quill`) · [data/wave11/enrich/raw/github_com_odygrd_quill.json](../../../data/wave11/enrich/raw/github_com_odygrd_quill.json) (enrichment confidence 0.88)

</details>
