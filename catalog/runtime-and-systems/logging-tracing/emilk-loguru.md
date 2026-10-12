# loguru

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Unlicense` · 🟢 active

> Two-file synchronous C++ logger with printf-style LOG_F; 1.8x lower per-line cost than glog 0.6.0 single-threaded, mixed under contention.

| | |
|---|---|
| **Beats** | glog (google/glog v0.6.0) |
| **Claimed result** | All ratios derived from page data (Time column, loguru vs glog). Iterations scenario (mean of 5): 1 thread 2392 vs 4324 ns (1.81x faster); 3 threads 4383 vs 3734 ns (glog 1.17x faster); 6 threads 4134 vs 5022 ns (1.21x); 12 threads 5398 vs 5927 ns (1.10x); 24 threads 4264 vs 5932 ns (1.39x). min_time 3 s scenario: 1 thread 2357 vs 4378 ns (1.86x); 2 threads 3265 vs 3674 ns (1.13x); 4 threads 4029 vs 4196 ns (1.04x); 8 threads 3434 vs 5357 ns (1.56x). CPU-time column favours loguru at every thread count (e.g. 24 threads 8284 vs 19366 ns). The project's own README claims 25%-75% faster than GLOG on a MacBook Pro (Clang), about the same on a Linux desktop (GCC) in unbuffered mode, and about twice as fast with \~100 ms buffered flushing. |
| **Workload** | Google Benchmark, one synchronous formatted INFO log call per iteration written to a log file with stderr output disabled: a message struct of four integers (u64, i64, u32, i32) and a 128-byte char string, cycling through pre-generated random messages. loguru uses printf-style LOG_F with its default unbuffered mode (g_flush_interval_ms = 0, flush per line); glog uses stream LOG(INFO) &lt;&lt; with a custom prefix function and FLAGS_logbufsecs=0. Two scenarios: iterations:2000 x 5 repetitions at 1, 3, 6, 12 and 24 threads, and min_time 3 s at 1, 2, 4 and 8 threads. loguru v2.1.0 vs glog v0.6.0; report run 2025-02-21. |
| **Metric** | latency |
| **Hardware** | Intel i7-10710U (12 threads), ThinkPad X1 Carbon 7th, Arch Linux kernel 6.11.9, frequency pinned to 3.2 GHz with scripts/set_cpu_freq.sh, 15659 MiB RAM (report dated 2025-02-21) |
| **Compiler and flags** | gcc (GCC) 14.2.1 20240910, glibc 2.40; build.sh passes -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON (CMake's Release default for GCC is -O3 -DNDEBUG; not echoed in the report); CMakeLists.txt adds -Wall -Wextra and C++17; Google Benchmark v1.8.3 |
| **Adoption** | 1.9k stars, 282 forks |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/emilk/loguru) · [benchmark](https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_loguru.txt) |

## Verdict

In MuggleWei/cc_log_benchmark (report 2025-02-21; GCC 14.2.1, CMake Release, Google Benchmark 1.8.3, i7-10710U pinned at 3.2 GHz, Arch Linux), one synchronous INFO line with four integers and a 128-byte string written to a file and flushed per line took 2392 ns with loguru v2.1.0 vs 4324 ns with glog v0.6.0 at one thread (1.81x) and 2357 vs 4378 ns in the 3-second run (1.86x). With 2-24 threads the wall-time-per-line column ranges from glog 1.17x faster (3 threads) to loguru 1.56x faster (8 threads), while loguru used less CPU per line at every thread count.

## Use it when

- Applications logging up to tens of thousands of lines per second that want every line on disk before the next statement (flush per line) without an async queue.
- Replacing glog in a C++11 codebase to cut build times (README: about 10% faster compilation in a medium project) while keeping CHECK-style assertions and glog-like macros via LOGURU_REPLACE_GLOG.
- Single-threaded or lightly threaded tools: in the independent shootout one INFO line cost 2.4 us vs glog 0.6.0's 4.3 us at one thread.
- Games and developer tools that need log callbacks (on-screen messages), indented scopes and error context dumped on a crash.
- Projects that want a no-dependency, public-domain logger they can vendor as two files.

## Skip it when

- Latency-sensitive hot paths: every call formats on the caller thread, allocates (vasprintf), locks a global mutex and issues a write(); async loggers cost single- to low double-digit nanoseconds per call on the producer.
- Many threads logging heavily: the global mutex serializes all lines; in the shootout loguru's wall time per line rose from 2.4 us (1 thread) to 4-5.4 us at 3-24 threads, glog 0.6.0 was faster at 3 threads (3734 vs 4383 ns) and the lead was 1.04x at 4 threads.
- Programs with their own handlers for SIGINT, SIGTERM, SIGSEGV and similar: loguru::init installs handlers for seven signals by default and runs a non-async-signal-safe logging path inside them unless SignalOptions turn it off.
- Needs for size- or time-based log rotation, structured/JSON output or binary logging: none is documented in the README.
- Organisations that require an OSI licence with an explicit patent grant: Loguru is a public-domain dedication with an Unlicense fallback.

## How it is fast

There is no special fast path: each call formats the message with vasprintf, builds a preamble (date, time, uptime, thread name from pthread TLS, file:line, level) with snprintf, takes one global std::recursive_mutex and writes every sink with fprintf. With the default g_flush_interval_ms = 0 each line is fflush'ed, i.e. one write() per line; setting it above 0 moves flushing to a background thread. Against glog it wins by doing less per line (no iostream formatting, one fflush per sink, header-light build), not by batching or async queues.

## Compared with alternatives

Pick loguru over Quill, fmtlog, NanoLog or XTR when you want synchronous, flushed-per-line logs and a two-file public-domain drop-in with CHECK macros and crash context, and per-line microsecond cost is acceptable; pick it over glog (archived) when migrating off glog with minimal macro churn and you log mostly from one or a few threads.

## Integration

| | |
|---|---|
| **Form** | source-drop (loguru.hpp + loguru.cpp; CMake add_subdirectory/FetchContent/find_package and vcpkg also supported) |
| **Dependencies** | none; link -lpthread and -ldl on Linux (dladdr/backtrace for stack traces); fmtlib only if LOGURU_USE_FMTLIB |
| **Minimum toolchain** | C++11 (README: compile with -std=c++11 -lpthread -ldl); CMake 3.12 for the CMake build |
| **Platforms** | Linux, macOS, Windows (including MinGW), FreeBSD, OpenBSD; stack traces only with glibc |
| **Thread safety** | README: thread-safe. Every log line is written under one global std::recursive_mutex, so concurrent loggers serialize. |
| **Drop-in for the baseline** | partial — LOGURU_REPLACE_GLOG maps LOG(INFO) &lt;&lt;, VLOG and CHECK_\* macros, but initialisation, flags (FLAGS_\*) and per-severity log files differ from glog |

## Gotchas

- The author's own README comparison is uneven: glog_bench logs LOG(WARNING) with FLAGS_alsologtostderr, and glog 0.6.0 writes each WARNING line to both its WARNING and INFO files (LogToAllLogfiles loops from the message severity down to 0) and force-flushes the WARNING file on every line even in the 'buffered' rows, while loguru_bench writes one file plus stderr; the 'about twice as fast as GLOG' buffered claim therefore compares unequal work. The independent shootout (INFO lines, one file each, flush per line) does not have this flaw.
- In the shootout's 6-thread iterations run, loguru's mean (4134 ns) is pulled down by one outlier repetition (3315 ns, cv 12.76%); medians are 4481 vs glog 4827 ns, 1.08x rather than 1.21x (derived from page data).
- Default unsafe_signal_handler = true: on a fatal signal loguru flushes and logs through the mutex-taking, allocating path; the source comments warn this can deadlock if the signal came from inside the allocator.
- With g_flush_interval_ms &gt; 0 a background flush thread is created lazily on the first log call, and lines written in the last interval are lost on SIGKILL or power loss; unnamed threads show as a hex pthread_self id.

## Known shortcomings

- MuggleWei/cc_log_benchmark (GCC 14.2.1, i7-10710U) numbers match, but glog is 1.17x faster at 3 threads and loguru's lead shrinks to 1.04x at 4 and 1.10x at 12 threads; baseline glog pinned at v0.6.0 (repo archived 2025-06-30); glog uses iostream through a shared library while loguru's printf path is compiled into the same file.
- Enricher: the cc_log_benchmark harness is fair (INFO, one file each, flush per line) but the 6-thread mean is skewed by an outlier repetition (cv 12.76%; medians 4481 vs 4827 ns, 1.08x not 1.21x); a global recursive mutex plus write() per line gives no scaling; the author's own README glog comparison is flawed (glog_bench logs WARNING, so glog 0.6.0 writes WARNING plus INFO files and force-flushes the WARNING file even in 'buffered' rows). Dormant Apr 2023 to Jul 2026, v2.2.0 2026-09-10; benchmarked v2.1.0 from 2019; default unsafe signal handlers on 7 signals.

## Caveats and trade-offs

Benchmark is a third-party logger shootout (MuggleWei/cc_log_benchmark, 34 stars), not the loguru author's. The baseline glog v0.6.0 is old and google/glog itself was archived on 2025-06-30 (README points to ng-log and Abseil logging); loguru is v2.1.0 while the repo's latest commit bumps the version to 2.2.0. Per-line work is not identical: glog formats with iostreams and a custom prefix function and is built as a shared library (BUILD_SHARED_LIBS=ON), while the loguru benchmark #includes loguru.cpp into the same translation unit and prints its default prefix with uptime and thread name. The Time column for multithreaded runs is (sum of per-thread time / threads) / total calls, not single-call latency; glog wins at 3 threads (4383 vs 3734 ns) and the 4-thread min_time margin is only 1.04x. Single laptop, one run per configuration; stddev only for the iterations rows. The shootout's own conclusions single out fmtlog, haclog, Nanolog and quill as the faster libraries, not loguru. The project's own bench dirs (loguru_bench, glog_bench) are public but its README numbers give no CPU model, compiler version or glog version. Unlicense: public-domain dedication, no patent grant.

Single loguru.hpp/loguru.cpp pair with no #includes in the header (README: about 10% faster compilation than including glog in a medium project). printf-style by default, optional streams (LOGURU_WITH_STREAMS) and fmtlib. In the independent run neither logger scales with thread count and the lead over glog shrinks or flips under contention. Public-domain dedication carries no patent grant.

## Maintenance

Revived rather than steadily active: no commits from April 2023 to July 2026, then 17 commits ending in v2.2.0 on 2026-09-10; the benchmarked v2.1.0 dates from 2019-09-23; Unlicense/public domain, 1.9k stars, two files, copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party shootout MuggleWei/cc_log_benchmark: public harness (gbenchmark/log_gbenchmark.h, gbenchmark/cpp/loguru/gbenchmark_loguru.cpp, gbenchmark/cpp/glog/gbenchmark_glog.cpp), flags from public build.sh/CMakeLists.txt (CMake Release, -std=c++17 -Wall -Wextra, pinned loguru v2.1.0, glog v0.6.0, Google Benchmark v1.8.3), compiler GCC 14.2.1 and CPU i7-10710U pinned at 3.2 GHz stated in the README. Both result files (benchmark_loguru.txt, benchmark_glog.txt) are in the same report directory.
- **Verifier notes:** All numbers match benchmark_loguru.txt and benchmark_glog.txt line for line; I rewrote claimed_speedup to list every thread count, since the old text put the 4-thread loguru win (1.04x) under 'not uniformly faster'. Metadata checks out (Unlicense, 1.9k stars, last commit 2026-09-10 'Bump version to 2.2.0', active). Shortcomings to record: not faster at 3 threads, small margins at 4 and 12 threads, baseline glog archived and pinned to v0.6.0, unequal formatting paths (iostream glog in a shared library vs printf loguru compiled inline).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-61 (wave 11); enricher w11 pair-022
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_loguru.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_glog.txt>
  - <https://github.com/MuggleWei/cc_log_benchmark>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/report/benchmark_20250221>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/gbenchmark/cpp>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/gbenchmark/cpp/loguru>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/gbenchmark/cpp/glog>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/build.sh>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/run_benchmark.sh>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/log_gbenchmark.h>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/cpp/loguru/gbenchmark_loguru.cpp>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/cpp/glog/gbenchmark_glog.cpp>
  - <https://github.com/emilk/loguru>
  - <https://github.com/emilk/loguru/commits>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/loguru.hpp>
  - <https://github.com/google/glog>
- **Sources the enricher read:**
  - <https://github.com/emilk/loguru>
  - <https://github.com/emilk/loguru/commits>
  - <https://github.com/emilk/loguru/commits/master>
  - <https://github.com/emilk/loguru/pull/278>
  - <https://github.com/emilk/loguru/pull/278/files>
  - <https://github.com/emilk/loguru/issues?q=is%3Aissue+deadlock+OR+slow+OR+performance+OR+crash>
  - <https://github.com/emilk/loguru/issues/182>
  - <https://github.com/emilk/loguru/issues/224>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/README.md>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/loguru.hpp>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/loguru.cpp>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/loguru_bench/loguru_bench.cpp>
  - <https://raw.githubusercontent.com/emilk/loguru/HEAD/glog_bench/glog_bench.cpp>
  - <https://raw.githubusercontent.com/google/glog/v0.6.0/src/logging.cc>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/build.sh>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/run_benchmark.sh>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/log_gbenchmark.h>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/cpp/loguru/gbenchmark_loguru.cpp>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/cpp/glog/gbenchmark_glog.cpp>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_loguru.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_glog.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/emilk/loguru`) · [data/wave11/enrich/raw/github_com_emilk_loguru.json](../../../data/wave11/enrich/raw/github_com_emilk_loguru.json) (enrichment confidence 0.85)

</details>
