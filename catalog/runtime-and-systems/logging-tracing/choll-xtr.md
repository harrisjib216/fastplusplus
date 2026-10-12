# XTR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 low-latency logger: per-thread SPSC ring buffer plus background {fmt} consumer; about 6-10 ns call-site latency vs spdlog async's 271-360 ns.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Quill README 1-thread number logging: 6/10 ns at 50th/99.9th vs spdlog 271/360 ns; 4 threads 8/18 ns vs spdlog 557/1106 ns. Quill throughput table: XTR 7.73 M msg/s (517 ms for 4M messages) vs spdlog 2.57 M msg/s (1557 ms). Own README: 0.894 ns for an empty log call, 1.25 ns for one int (no baseline in README). |
| **Workload** | Call-site latency with ring-buffer producer and background formatter; formatting and I/O delegated to a consumer thread. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-12600 @ 4.8 GHz, tuned system (isolcpus, nohz_full, mitigations=off), RHEL 9.4 |
| **Compiler and flags** | GCC 14.2, Release, -march=x86-64-v3 |
| **Adoption** | 77 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/choll/xtr) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

The Quill author's harness (odygrd/logger_benchmarks; XTR via XTR_LOGL_TSC with io_uring off, spdlog as an async_logger with a 1-thread pool, block overflow policy and basic_file_sink_st), GCC 14.2 Release -march=x86-64-v3 on an i5-12600 with isolated cores, measured int/int/double call-site latency of 6/10 ns (p50/p99.9) for XTR against spdlog's 271/360 ns on 1 thread and 8/18 against 557/1106 ns on 4 threads, plus 7.73M against 2.57M msg/s throughput. XTR's own README shows 0.894 ns for an empty XTR_LOG (no timestamp read) and 9-10 ns for TSC variants on a Ryzen 5950X with g++ 15.3.0 and a CPU-scaling warning, with no spdlog row.

## Use it when

- Trading, real-time or other hot paths that need consistent single-digit-nanosecond log calls on Linux or FreeBSD x86-64, with a core to spare for the consumer.
- Logging scalars and short strings: in the Quill author's harness, int/int/double costs 6/10 ns at p50/p99.9 on 1 thread and large strings 7/15 ns, against spdlog's 271/360 and 247/290 ns.
- One sink per thread, so producers never contend with each other.
- You want built-in log-level control from outside the process (xtrctl), logrotate reopen, systemd journal output, or an io_uring file back-end.

## Skip it when

- Windows, macOS or ARM: only Linux and FreeBSD x86-64 are supported.
- Logging containers or other complex types: arguments are copied and formatted, and the Quill harness puts a std::vector of 16 large strings at 752-959 ns per call (1 thread), about 10x Quill's bounded queue (53-120 ns), though still about 9x faster than spdlog.
- Pre-C++20 toolchains (the Makefile builds with -std=c++20 and the header uses concepts).
- CPU-constrained or power-sensitive hosts: the consumer thread spins continuously because it cannot block without a system call on the producer side.
- You need spdlog's sink ecosystem or API compatibility.

## How it is fast

The call site only serializes a pointer to a type-specialized formatting function plus the arguments, by value, into a lock-free single-producer ring buffer (256 KiB per sink by default) owned by that sink; no allocations or system calls are made. The consumer thread busy-spins over all sinks, decodes, formats with {fmt} and writes, optionally batching through io_uring. The basic XTR_LOG macros skip the clock read entirely (the consumer stamps the record), which is where the sub-nanosecond README numbers come from.

## Compared with alternatives

Pick XTR over Quill or PlatformLab NanoLog when you are on Linux/FreeBSD x86-64, log mostly scalars and strings (where it ties Quill at 6-10 ns and edges NanoLog), and want io_uring, xtrctl and journal integration; pick Quill when you log STL containers (about 10x cheaper there) or need Windows/macOS.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | {fmt}; liburing optional (io_uring back-end); Catch2 and Google Benchmark only for tests and benchmarks |
| **Minimum toolchain** | C++20 (GCC; README benchmark uses g++ 15.3.0, Quill harness GCC 14.2) |
| **Platforms** | Linux x86-64, FreeBSD x86-64 |
| **Thread safety** | xtr::logger functions are thread-safe; xtr::sink functions are not (except level/set_level), so use one sink per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Plain XTR_LOG does not read a clock at the call site: the background thread timestamps the record when it dequeues it, so timestamps are late and can be reordered relative to real events. Use XTR_LOG_TSC (about 9-10 ns in the README) or XTR_LOG_RTC when accurate time matters; the Quill harness numbers use XTR_LOGL_TSC, so they are comparable to spdlog.
- Default macros block (spin with pause) when the sink's ring buffer is full; only the XTR_TRY_LOG variants drop, counting drops in dropped_count(). String arguments may be truncated when the sink is full, and vcopy records are dropped whole.
- Arguments are copied by value unless wrapped in xtr::nocopy, in which case the referenced data must outlive consumption; ring capacity is the compile-time XTR_SINK_CAPACITY (256 KiB default), and changing it requires rebuilding libxtr.
- A single-header form exists (single_include/xtr/logger.hpp), but the documented build is make/CMake through Conan and pkg-config; the logger destructor blocks until every sink created from it is destroyed.

## Known shortcomings

- README 0.894 ns is plain XTR_LOG with no call-site timestamp (the consumer stamps); with XTR_LOGL_TSC the Quill harness is fair. Logging a std::vector of strings costs 752-959 ns, about 10x Quill. Default macros spin when the sink is full. C++20, x86-64 Linux/FreeBSD only.

## Caveats and trade-offs

Own README numbers (Ryzen 5950X, g++ 15.3.0, CPU scaling enabled warning) have no spdlog row; the spdlog comparison comes from the Quill author's harness (a competing library's author). Sub-2 ns figures are enqueue-only in a tight loop. Linux and FreeBSD x86-64 only.

Linux x86-64 only; requires a consumer thread (or user-driven polling); supports io_uring and custom sinks; depends on fmt.

## Maintenance

Actively maintained single-author project (874 commits, last commit 2026-09-16, 77 stars, Conan Center package) under MIT, so copyable; small user base.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Quill README Performance section (third-party harness) shows XTR vs spdlog with GCC 14.2, Release -march=x86-64-v3, Intel Core i5-12600 stated; the code is public in odygrd/logger_benchmarks (benchmarks/call_site_latency/benchmark_xtr_call_site_latency.cpp and benchmark_spdlog_call_site_latency.cpp). Quoted percentile numbers match.
- **Verifier notes:** Benchmark code for XTR confirmed present in odygrd/logger_benchmarks. MIT, 77 stars, last commit 2026-09-16.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/README.md>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://github.com/choll/xtr>
  - <https://github.com/choll/xtr/commits>
  - <https://github.com/odygrd/logger_benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks/call_site_latency>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/README.md>
  - <https://github.com/choll/xtr>
  - <https://github.com/choll/xtr/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/docs-src/guide.rst>
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/docs-src/index.rst>
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/single_include/xtr/logger.hpp>
  - <https://raw.githubusercontent.com/choll/xtr/HEAD/Makefile>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_xtr_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_spdlog_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/choll/xtr`) · [data/wave11/enrich/raw/github_com_choll_xtr.json](../../../data/wave11/enrich/raw/github_com_choll_xtr.json) (enrichment confidence 0.85)

</details>
