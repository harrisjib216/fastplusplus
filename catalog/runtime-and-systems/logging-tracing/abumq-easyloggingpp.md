# Easylogging++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Archived feature-heavy synchronous C++ stream logger; 6-9% faster than glog at 1-10 threads in spdlog's old bench, 4x slower at 100.

| | |
|---|---|
| **Beats** | glog |
| **Claimed result** | From the spdlog v0.16.3 README benchmark table (seconds, lower is better): 1 thread 0.975s (Easylogging++) vs 1.066s (glog), about 1.09x faster (derived from page data); 10 threads 2.857s vs 3.032s, about 1.06x faster (derived from page data); 100 threads 4.512s vs 1.139s, i.e. Easylogging++ about 4.0x slower than glog (derived from page data). |
| **Workload** | Time to write 1,000,000 short text lines ('message #N: This is some text for your pleasure') to a log file, split across 1, 10 or 100 threads that share an atomic counter; best of 3 runs; Easylogging++ file output with default logger, format '[%datetime]: %msg', large flush threshold, against glog LOG(INFO) to a log directory. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 64 bit, Intel i7-4770 CPU @ 3.40GHz |
| **Compiler and flags** | bench/Makefile in gabime/spdlog v0.16.3: CXX ?= g++ (version not stated), -march=native -Wall -Wextra -pedantic -std=c++11 -pthread -O3 -flto -DNDEBUG; glog linked with -lglog (version not stated); Easylogging++ included from a local checkout (-I../../easylogging/src/) with config bench/easyl.conf (FORMAT '[%datetime]: %msg', TO_FILE true, TO_STANDARD_OUTPUT false, PERFORMANCE_TRACKING false, MAX_LOG_FILE_SIZE 10485760, Log_Flush_Threshold 10485760). _ELPP_THREAD_SAFE is defined only in easylogging-bench-mt.cpp, not in the single-thread easylogging-bench.cpp. The programs contain no timer, so whole-process wall time was presumably measured externally; no run script is in the bench directory. |
| **Adoption** | 3.9k stars, 942 forks |
| **Last commit** | 2025-07-06 |
| **Links** | [repository](https://github.com/abumq/easyloggingpp) · [benchmark](https://github.com/gabime/spdlog/blob/v0.16.3/README.md) |

## Verdict

In spdlog v0.16.3's README table (Ubuntu 64-bit, Intel i7-4770 @ 3.40GHz, g++ of unstated version with -O3 -flto -march=native, best of 3), writing 1,000,000 lines to a file took Easylogging++ 0.975 s vs glog 1.066 s on 1 thread and 2.857 s vs 3.032 s on 10 threads (about 1.06-1.09x, derived from page data), but 4.512 s vs 1.139 s on 100 threads. Easylogging++ was a pre-9.80 release with a short format, no flushing during the run and, in the 1-thread binary, no thread safety, while glog used its default prefix and locking.

## Use it when

- Existing code bases that already use Easylogging++ and only need it to keep working; MIT licence makes vendoring and patching easy.
- Single-threaded tools or small apps where you want config-file driven per-level formats and files, CHECK macros and built-in TIMED_FUNC/TIMED_SCOPE block timing without pulling in Boost or gflags.
- Moderate-rate file logging from a few threads where a synchronous call costing about a microsecond (about 1 s per million lines in the spdlog test) is acceptable.

## Skip it when

- New projects: the repository was archived on 2025-07-06 and its own README recommends spdlog instead; the last code changes were in 9.97.0 (December 2020).
- Many threads logging heavily: with ELPP_THREAD_SAFE every call serialises on several mutexes, and in the spdlog table 100 threads took 4.512 s against glog's 1.139 s.
- Latency-critical hot paths: asynchronous logging exists only behind ELPP_EXPERIMENTAL_ASYNC and the README says not to rely on it in production; Quill, fmtlog or NanoLog report nanosecond-scale call sites.
- Out-of-the-box use expecting the benchmark speed: the default configuration flushes the file after every entry (Log_Flush_Threshold 0) and also echoes every line to standard output.

## How it is fast

Nothing exotic: each message is streamed into a per-logger std::stringstream, a log line is built by substituting format specifiers (%datetime via gettimeofday plus custom formatting), and the line is written with std::fstream::write. Speed in the measured setup comes mostly from configuration: the bench set Log_Flush_Threshold to 10,485,760 entries, so the stream was never flushed explicitly during the 1M-line run, and the format was a short '[%datetime]: %msg'. Thread safety is compiled out unless ELPP_THREAD_SAFE is defined; when it is on, every LOG call takes the logger registry lock, holds the logger's own lock while the message is streamed, takes a global storage lock (unless ELPP_NO_GLOBAL_LOCK) and a per-file lock, which is why it fell behind at 100 threads.

## Compared with alternatives

Pick Easylogging++ only to keep an existing code base running or if you specifically want its config-file driven loggers and built-in block timing; for a glog-like synchronous logger with better numbers loguru reports about 1.8x faster than glog, and glog itself (or ng-log) scaled better here at 100 threads. For throughput or latency, spdlog, Quill or fmtlog are far ahead.

## Integration

| | |
|---|---|
| **Form** | source-drop (easylogging++.h + easylogging++.cc); optional CMake static library |
| **Dependencies** | none (pthread when ELPP_THREAD_SAFE is defined on Linux) |
| **Minimum toolchain** | C++11 (README: GCC 4.6.4+, Clang 3.1+, Visual C++ 11.0+; the repo's own CMake build uses C++14); v8.91 for C++98/03 |
| **Platforms** | Linux, macOS, Windows (MSVC, MinGW, Cygwin), FreeBSD, Android, Solaris, AIX, QNX and Emscripten per README and changelog; stack traces on GCC only |
| **Thread safety** | Off by default; define ELPP_THREAD_SAFE for every translation unit including easylogging++.cc. Without it, logging from more than one thread gives 'unexpected results' per the README. |
| **Drop-in for the baseline** | partial — LOG(INFO)/CHECK/VLOG call sites look like glog, but initialization (INITIALIZE_EASYLOGGINGPP, el::Configurations), flags and log-file layout differ and there is no gflags integration |

## Gotchas

- Benchmark harness asymmetry beyond what the verifier noted: Easylogging++ defaults to flushing after every entry and writing to stdout, and the bench overrode both (Log_Flush_Threshold 10,485,760 entries, TO_STANDARD_OUTPUT false), while glog ran with its full default prefix. The record's 'mostly default buffering' is not right for the Easylogging++ side; the measured configuration is tuned, not default.
- The bench uses _INITIALIZE_EASYLOGGINGPP and _ELPP_THREAD_SAFE, which v9.75 still uses and v9.80 already spells without the underscore, so a v9.7x-or-older single-header release was measured, not the current two-file 9.97.x. The same table has glog at 1.139 s for 100 threads but 3.032 s for 10, an odd inversion with no run script or repeat data in the bench directory.
- Configuration macros (ELPP_THREAD_SAFE, ELPP_NO_DEFAULT_LOG_FILE, ELPP_FEATURE_PERFORMANCE_TRACKING and others) must be passed as compiler flags so easylogging++.cc sees them too; a #define in main.cpp does not reach it (issue #590). Without ELPP_NO_DEFAULT_LOG_FILE a myeasylog.log file is created at start-up.
- Open, unanswered issues include a deadlock when the disk runs out of inodes during file rolling (#744), a crash with performance tracking in multiple threads (#790), a compile error with TIMED_FUNC in a method called from several threads (#853) and an async-logger deadlock on VS2017 (#779); they will not be fixed upstream.

## Known shortcomings

- Downgraded B to C: spdlog v0.16.3 harness is asymmetric (easyl.conf short '[%datetime]: %msg' vs glog full prefix; single-thread binary lacks _ELPP_THREAD_SAFE while glog locks), no timer in the code, versions unstated; loses 4x at 100 threads. Archived 2025-07-06.
- Enricher: the spdlog bench tuned Easylogging++ (no flush during the run, no stdout echo; its defaults flush every entry and echo to stdout) against default glog; v9.75 or older measured; glog's 100-thread time beats its 10-thread time with no run script to explain it; archived with open deadlock and crash issues.

## Caveats and trade-offs

Evidence is a competitor's benchmark (spdlog author) from about 2015-2016, with Easylogging++ and glog versions and the g++ version unstated and the Makefile pointing at a local checkout (-I../../easylogging/src/); the bench sources use the leading-underscore macros _INITIALIZE_EASYLOGGINGPP and _ELPP_THREAD_SAFE, which current Easylogging++ spells without the underscore, so an old release was measured. Mixed result: Easylogging++ wins by 6-9% at 1 and 10 threads but loses about 4x at 100 threads. Asymmetric configuration: Easylogging++ is set to a short '[%datetime]: %msg' line, while glog writes its full default prefix (severity, date, microsecond time, thread id, file:line) on every line and no FLAGS_log_prefix change is made, so glog formats and writes more bytes per message; the single-thread Easylogging++ binary is built without _ELPP_THREAD_SAFE (no locking) while glog always takes its mutex. The 6-9% wins are small enough that these differences can account for them. The programs contain no timer, so the timed region is the whole process including logger setup, and the measurement method is not in the repo. Both libraries write to file with mostly default buffering. The project's own README says only 'Extremely fast' with no numbers, and its maintainer notes third-party benchmarks of limited setups (links g3log issue #73). That issue (https://github.com/KjellKod/g3log/issues/73, null sink, unstated units, no compiler or CPU) shows Easylogging++ 410,725 vs glog 402,970 for 1 thread string, but glog ahead at 4 threads (196,734 vs 127,895 without the option); this is directional and not used for the tier. spdlog itself is about 3x faster than either in the same table. The repository was archived by its owner on 2025-07-06 and its README recommends spdlog for new projects. [retier] Enricher: the earlier note that both libraries write with mostly default buffering is wrong for Easylogging++: by default it flushes after every entry and echoes every line to stdout, and the bench turned both off (Log_Flush_Threshold 10,485,760 entries, so no flush during the run; TO_STANDARD_OUTPUT false), so a tuned configuration was measured against a default glog. The _ELPP_ macros show v9.75 or older was measured (v9.80 drops the underscore). glog at 100 threads (1.139 s) beat glog at 10 threads (3.032 s), an unexplained inversion with no run script or repeat data. Open, unanswered issues include a disk-full rolling deadlock (#744) and a multi-threaded performance-tracking crash (#790).

Single-header, many features (custom sinks, performance tracking, hierarchical loggers, macros that define global state, _INITIALIZE_EASYLOGGINGPP). Repo archived read-only on 2025-07-06; its own README now recommends spdlog for new projects. Heavy macro and global-state design.

## Maintenance

Abandoned: archived read-only on 2025-07-06 (last release 9.97.1 in July 2023 was a test-only chore; last functional release 9.97.0, December 2020), but MIT-licensed and two plain source files, so it is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** spdlog v0.16.3 README table matches the claim (1 thread 0.975s vs glog 1.066s, 10 threads 2.857s vs 3.032s, 100 threads 4.512s vs 1.139s) and the bench code is public, but the harness is asymmetric in Easylogging++'s favour: bench/easyl.conf gives it a minimal '[%datetime]: %msg' line while glog keeps its full default prefix (severity, microsecond time, thread id, file:line), and the single-thread easylogging-bench.cpp omits _ELPP_THREAD_SAFE while glog always locks. The 6-9% wins are within what that asymmetry can explain, versions and timing method are unstated, and Easylogging++ loses 4x at 100 threads.
- **Verifier notes:** Numbers and bench code verified at spdlog tag v0.16.3; downgraded B to C for the asymmetric format and thread-safety configuration behind a 6-9% margin. Repo archived 2025-07-06 (abandoned is correct); MIT, 3.9k stars, 942 forks confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/Makefile>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easyl.conf>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easylogging-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/glog-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easylogging-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/glog-bench.cpp>
  - <https://github.com/KjellKod/g3log/issues/73>
  - <https://github.com/abumq/easyloggingpp>
  - <https://github.com/abumq/easyloggingpp/commits/master>
- **Sources the enricher read:**
  - <https://github.com/abumq/easyloggingpp>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/HEAD/src/easylogging++.h>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/HEAD/src/easylogging++.cc>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/v9.80/src/easylogging++.h>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/v9.75/src/easylogging++.h>
  - <https://raw.githubusercontent.com/abumq/easyloggingpp/v9.60/src/easylogging++.h>
  - <https://github.com/abumq/easyloggingpp/issues?q=is%3Aissue+performance+OR+slow+OR+deadlock>
  - <https://github.com/abumq/easyloggingpp/issues/590>
  - <https://github.com/abumq/easyloggingpp/issues/744>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/README.md>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/Makefile>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easyl.conf>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easylogging-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/easylogging-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/glog-bench.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/glog-bench-mt.cpp>
  - <https://raw.githubusercontent.com/gabime/spdlog/v0.16.3/bench/latency/Makefile>
  - <https://github.com/gabime/spdlog/tree/v0.16.3/bench>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/abumq/easyloggingpp`) · [data/wave11/enrich/raw/github_com_abumq_easyloggingpp.json](../../../data/wave11/enrich/raw/github_com_abumq_easyloggingpp.json) (enrichment confidence 0.8)

</details>
