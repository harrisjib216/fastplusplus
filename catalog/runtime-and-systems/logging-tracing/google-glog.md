# glog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Google's synchronous C++ stream logger (LOG, CHECK, VLOG); about 4x faster than Boost.Log 1.56 file logging in 2014 tests.

| | |
|---|---|
| **Beats** | Boost.Log 1.56 (trivial severity logger, text file sink) |
| **Claimed result** | spdlog v0.x README table: Boost.Log v1.56 4.207s single thread / 6.592s 10 threads vs glog v0.3.3 1.077s / 1.678s, about 3.9x faster for glog in both cases (derived from page data); spdlog itself 0.975s / 0.961s, i.e. glog is slightly slower than spdlog. |
| **Workload** | Wall time to write 1,000,000 log lines to files in a logs directory, from a single thread and from 10 threads sharing one logger; glog uses LOG(INFO) &lt;&lt; 'glog message # ' &lt;&lt; i with FLAGS_logtostderr=0. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 64 bit, Intel i7-4770 CPU @ 3.40GHz |
| **Compiler and flags** | g++ (version not stated) with -march=native -Wall -Wextra -Wshadow -pedantic -std=c++11 -pthread -O3 -flto, from bench/Makefile at spdlog commit dc198a5 (bench/glog-bench.cpp, glog-bench-mt.cpp, boost-bench.cpp, boost-bench-mt.cpp); timed with `time ./binary` in bench/run_all.sh with 3 s sleeps between runs; glog linked as a prebuilt system -lglog and Boost.Log 1.56 from /home/gabi/devel/boost_1_56_0 (library build flags not stated) |
| **Adoption** | 7.4k stars; archived by Google on 2025-06-30 |
| **Last commit** | 2025-03-31 |
| **Links** | [repository](https://github.com/google/glog) · [benchmark](https://github.com/gabime/spdlog/blob/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/README.md) |

## Verdict

In spdlog's 2014 benchmark (Ubuntu 64-bit, Intel i7-4770, bench programs built with g++ -O3 -flto -march=native, system libglog 0.3.3, Boost.Log 1.56), writing 1M lines to files took glog 1.077 s vs Boost.Log 4.207 s on one thread and 1.678 vs 6.592 s on 10 threads (3.9x). Later runs on the same machine gave 1.115 vs 4.430 s and 2.027 vs 13.985 s (bench/results.txt at def6fc6) and best-of-3 1.109 vs 4.779 s and 3.546 vs 15.151 s, so 4.0-4.3x on one thread and 3.9-6.9x on 10 threads (ratios derived from page data); spdlog's synchronous logger beat glog on one thread in every run.

## Use it when

- Existing glog code bases, or code that relies on CHECK/DCHECK, VLOG with --vmodule and InstallFailureSignalHandler stack traces as one package.
- Moderate-rate application logging to local files where a synchronous call of a microsecond or so is acceptable and Boost.Log's setup and per-record cost are not.
- Low-level code that needs a lock-free, allocation-free path: RAW_LOG in &lt;glog/raw_logging.h&gt;.
- Migration work: keep the glog API and move to ng-log, which describes itself as API-compatible.

## Skip it when

- New projects: the repository was archived on 2025-06-30; its README points to ng-log or Abseil Logging.
- Latency-critical hot paths: every LOG call formats and writes synchronously under a global mutex, while async loggers in this category report single-digit to low hundreds of nanoseconds per call.
- Many threads logging heavily: in the spdlog runs, 10 threads were slower than 1 (1.68-3.55 s vs about 1.1 s wall) and the 10-thread run spent 6.2 s of system time.
- Crash-sensitive audit logs: buffered INFO lines (up to 30 s or 1 MB) are lost on a hard crash unless FLAGS_logbuflevel is set to -1, which flushes every line and gives up most of the measured speed.
- Format-string or structured logging: the API is ostream-only, and messages longer than 30,000 bytes are truncated.

## How it is fast

Each message is formatted into a preallocated per-thread buffer (thread_local LogMessageData holding a fixed 30,000-byte array), then written under one global std::mutex with fwrite to a stdio FILE\*. INFO lines are buffered by default (logbuflevel=0) and flushed only every 1,000,000 bytes or every logbufsecs=30 seconds, and on Linux written log pages are dropped from the page cache with posix_fadvise. The Boost.Log side of the benchmark did more work per record: it added common attributes (line id, timestamp, process and thread id), ran a severity filter and a timestamp formatter.

## Compared with alternatives

Pick glog (or its successor ng-log) for the CHECK/VLOG/failure-handler bundle or an existing code base, not for speed: loguru's own benchmark has it about 1.8x faster than glog 0.6.0, BqLog and Coost report glog far behind, and Quill, NanoLog or fmtlog cut call-site latency to nanoseconds. Over Boost.Log, glog is the simpler and, in these old tests, about 4x faster synchronous file logger.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake or Bazel) |
| **Dependencies** | Threads; optional gflags 2.2.2, libunwind or unwind for stack traces, dbghelp on Windows; GTest only for tests |
| **Minimum toolchain** | C++14 (CMake target_compile_features cxx_std_14 at HEAD; the measured 0.3.3 release predates that) |
| **Platforms** | Linux and other Unix-likes, macOS, Windows and Cygwin (platform branches in CMakeLists.txt); stack traces need libunwind, unwind or dbghelp |
| **Thread safety** | LOG/CHECK are thread-safe and serialised by a global std::mutex; AddLogSink/RemoveLogSink are thread-safe; LogSink::send must not call LOG or CHECK (deadlock); EnableLogCleaner thread safety is questioned in open issue #753 |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness flaw (spdlog bench at dc198a5): the two sides were not set up alike. glog wrote its full prefix (date, microseconds, thread id, file:line) and used default buffering. Boost.Log wrote '[timestamp]: message' through a filter, a formatter and a 10 MiB rotating sink with auto_flush=false. Wall time came from `time ./binary`, so process start-up is included, and Boost 1.56 was linked dynamically from a personal build with unstated flags.
- Default INFO buffering (logbuflevel=0, logbufsecs=30, flush every 1,000,000 bytes) is part of why the numbers look good; the tail of the log is lost on SIGKILL or power loss.
- Flags are process-global: FLAGS_log_dir must be set before InitGoogleLogging, and if the log file cannot be created glog prints 'COULD NOT CREATE LOGFILE' to stderr.
- Messages logged before InitGoogleLogging() go to stderr with a one-time warning.

## Known shortcomings

- 2014 numbers measured by the spdlog author (spdlog README at dc198a5: Boost.Log 1.56 4.207 s and 6.592 s vs glog 0.3.3 1.077 s and 1.678 s, 1M lines, i7-4770, -O3 -flto): g++ version unstated, prebuilt libglog and Boost flags unknown; glog is slower than spdlog in the same table. Repo archived 2025-06-30.
- Enricher: the 2014 spdlog harness is unequal (different line formats; Boost with filter, formatter and 10 MiB rotating sink; glog default INFO buffering of 30 s or 1 MB; time includes startup; Boost from a personal build with unknown flags). Later runs on the same machine (spdlog bench/results.txt at def6fc6, README e166fad) have Boost.Log 4.0-4.3x slower on 1 thread and 3.9-6.9x on 10; glog's 10-thread wall 1.68-3.55 s with 6.2 s sys shows global-mutex contention; spdlog sync beat glog on 1 thread in every run. ng-log is the API-compatible successor (would be a duplicate).

## Caveats and trade-offs

Measured by the maintainer of a competing library (spdlog) in 2014 on glog v0.3.3 and Boost.Log 1.56, both long superseded, and the table is no longer in the current spdlog README. Compiler version and the build flags of the prebuilt libglog (-lglog) and of Boost.Log (built from a personal path in the Makefile) are not stated; the Makefile flags apply only to the benchmark programs. The two sides are not configured identically (glog default buffering and its own file naming, Boost.Log with auto_flush=false and a 10 MiB rotating sink), and the time includes process start-up and log-directory file creation. The seed list gave no performance claim for glog; this is the only numeric comparison found where glog beats a named logger. The RafaGago/logger-bench page (opened) lists glog among its compared libraries but states no results.

Synchronous logging behind a global mutex: threads serialise, so 10 threads were slower than one in the table (1.678s vs 1.077s). Buffered file output (default flush interval and level) means lines can be lost on a crash unless FLAGS_logbuflevel is changed; global flags and singleton state; no asynchronous mode; the repository is archived and read-only.

## Maintenance

Abandoned: archived read-only on 2025-06-30 (last release 0.7.1, June 2024; HEAD CMake says 0.8.0). It is still BSD-3-Clause, widely packaged and copyable, but new work should go to ng-log (community, API-compatible) or Abseil Logging.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The spdlog README at commit dc198a5 (22 Nov 2014) shows boost log v1.56 4.207s/6.592s vs glog v0.3.3 1.077s/1.678s, and the same commit carries the benchmark code (bench/glog-bench.cpp, glog-bench-mt.cpp, boost-bench.cpp, boost-bench-mt.cpp, run_all.sh timing each binary with `time`), bench/Makefile flags (g++ -march=native -std=c++11 -pthread -O3 -flto) and the CPU (i7-4770 @ 3.40GHz). Borderline A in the pdqsort sense: g++ version unstated, and the glog and Boost.Log libraries were prebuilt with unstated flags (-lglog from the system, Boost from a personal build path).
- **Verifier notes:** Numbers, hardware and benchmark sources all match the record; the ratios (3.9x single thread, 3.9x 10 threads) are correctly marked as derived. The table is gone from the current spdlog README, the measurement is from November 2014 on glog 0.3.3 and Boost 1.56, glog is slightly slower than spdlog in the same table, and google/glog is archived (2025-06-30, last commit 2025-03-31; README points to ng-log or Abseil Logging), so keep the abandoned tag and these shortcomings.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-60 (wave 11); enricher w11 pair-024
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/Makefile>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/glog-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/glog-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/boost-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/boost-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/run_all.sh>
  - <https://github.com/gabime/spdlog/tree/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench>
  - <https://github.com/gabime/spdlog/commits/dc198a5e64a1c66f53774c6ecf7f482dbd09758e>
  - <https://raw.githubusercontent.com/gabime/spdlog/HEAD/README.md>
  - <https://github.com/google/glog>
  - <https://github.com/google/glog/commits>
- **Sources the enricher read:**
  - <https://github.com/google/glog>
  - <https://github.com/google/glog/issues?q=is%3Aissue+performance>
  - <https://raw.githubusercontent.com/google/glog/HEAD/README.rst>
  - <https://raw.githubusercontent.com/google/glog/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/google/glog/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/glog/HEAD/src/logging.cc>
  - <https://raw.githubusercontent.com/google/glog/HEAD/src/flags.cc>
  - <https://raw.githubusercontent.com/google/glog/HEAD/src/glog/flags.h>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/flags.md>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/logging.md>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/sinks.md>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/failures.md>
  - <https://raw.githubusercontent.com/google/glog/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/Makefile>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/glog-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/glog-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/boost-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/boost-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/run_all.sh>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/spdlog-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench/spdlog-bench-mt.cpp>
  - <https://github.com/gabime/spdlog/tree/dc198a5e64a1c66f53774c6ecf7f482dbd09758e/bench>
  - <https://github.com/gabime/spdlog/commit/def6fc62f4817985cde269c53805d426d4b2b2ae>
  - <https://raw.githubusercontent.com/gabime/spdlog/def6fc62f4817985cde269c53805d426d4b2b2ae/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/def6fc62f4817985cde269c53805d426d4b2b2ae/bench/results.txt>
  - <https://github.com/gabime/spdlog/commit/e166fadeb9a35e671ec43913b0b2423b28635dbb>
  - <https://raw.githubusercontent.com/gabime/spdlog/e166fadeb9a35e671ec43913b0b2423b28635dbb/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/a46e967dafe02a837fffaa4f07638e614988fe71/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/2a6596c2c04c6106ce683898a9cbad5d49d7ecda/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/7900b83d1a79a7976166b2d92fc5074ecf3b0dcc/README.md>
  - <https://github.com/ng-log/ng-log>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/google/glog`) · [data/wave11/enrich/raw/github_com_google_glog.json](../../../data/wave11/enrich/raw/github_com_google_glog.json) (enrichment confidence 0.75)

</details>
