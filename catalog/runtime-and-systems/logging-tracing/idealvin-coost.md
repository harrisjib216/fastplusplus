# Coost co/log

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Asynchronous double-buffered logger inside the coost C++17 base library; first-party numbers claim it beats glog and synchronous spdlog.

| | |
|---|---|
| **Beats** | glog (single thread) and spdlog (1-8 threads) |
| **Claimed result** | vs glog (1 thread, 1 million logs, write speed): win2012 HDD 1.6MB/s vs 180MB/s (112.5x), win10 SSD 3.7MB/s vs 560MB/s (151.3x), mac SSD 17MB/s vs 450MB/s (26.4x), linux SSD 54MB/s vs 1023MB/s (18.9x). vs spdlog (seconds for 1 million logs): linux 1 thread 0.087235 vs 2.076172 (23.8x), 8 threads 0.302088 vs 3.963644 (13.1x); windows 1 thread 0.117704 vs 0.461156 (3.9x), 8 threads 0.406025 vs 1.417387 (3.5x). |
| **Workload** | Time or write speed for continuously printing 1 million log lines, single thread against glog on four platforms, and 1, 2, 4 and 8 threads against spdlog on Linux and Windows. |
| **Metric** | throughput |
| **Hardware** | Platforms named only as win2012 HDD, win10 SSD, mac SSD, linux SSD; CPU models not stated |
| **Adoption** | 4.2k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/idealvin/coost) · [benchmark](https://raw.githubusercontent.com/idealvin/coost/HEAD/readme.md) |

## Verdict

The spdlog rows come from benchmark/log_bm.cc on the 'benchmark' branch: 1 million lines (32 'x' characters plus an integer) split across 1-8 threads, co/log's asynchronous logger against spdlog 1.8.5's synchronous basic_logger_mt file sink, benchmark target built with xmake 'fastest' (-O3); Linux rows ran under the Windows Subsystem for Linux (0.087 s vs 2.08 s at 1 thread, 23.8x), native Windows rows show 3.9x at 1 thread, and no CPU, compiler or storage is named. The glog write-speed table (18.9x-151x on four platform/disk combinations) has no harness anywhere in the repository, and the co/json-vs-rapidjson table comes from benchmark/json_bm.cc, which also times simdjson but the README leaves those rows out and times stringify with a single call.

## Use it when

- You already build on coost (its flags, coroutines or RPC) and want logging that matches its conventions with no extra dependency.
- Bursty single-process logging where hot-path cost matters more than per-line timestamp precision and an occasional dropped burst is acceptable.
- Services that want crash reporting built in: co/log installs signal handlers (SIGSEGV, SIGABRT, SIGFPE, SIGBUS, SIGILL) and dumps a stack trace into the log and a .fatal file.
- Linux, macOS, Windows or FreeBSD on x86/x64/ARM/ARM64 with a C++17 compiler, where a glog-style check/fatal API is wanted.

## Skip it when

- You need guaranteed delivery: when the shared buffer exceeds max_log_buffer_size (32 MB by default) co/log discards the oldest half of the buffer and writes a '......' marker instead of blocking.
- Many threads logging concurrently at high rates: every line takes the same global std::mutex, and the project's own numbers show 8 threads taking about 3.5x as long as 1 thread for the same 1 million lines.
- You need multiple loggers, multiple sinks, structured or JSON output, or format strings; there is one global logger, one file and one optional callback.
- You do not want a whole framework: co/log needs coost's flag::parse, co::string, fs and thread code, and it changes process-wide signal handling.
- Lowest-latency logging: the catalogued Quill, fmtlog, NanoLog and XTR publish single-digit-nanosecond hot paths with reproducible harnesses.

## How it is fast

Each thread formats its line into a thread-local co::string by appending arguments with coost's own integer/float conversion (no format-string parsing) and copies a pre-rendered timestamp string instead of calling strftime per line. The finished line is appended under one std::mutex to a shared in-memory buffer, and a background thread wakes every log_flush_ms (128 ms by default) or when the buffer passes half its capacity, swaps it with a second buffer and writes it to the file in one call (double buffering). The caller never touches the file, so the measured cost is mostly a memcpy plus a mutex.

## Compared with alternatives

Pick co/log only when you already use coost and want its integrated flags, check macros and crash stack traces; for standalone low-latency logging Quill, fmtlog or binlog are better documented and have reproducible harnesses, and BqLog or slick-logger publish multi-threaded comparisons against spdlog's async mode rather than its synchronous file sink.

## Integration

| | |
|---|---|
| **Form** | static lib (libco, built with xmake or CMake; shared build possible) |
| **Dependencies** | none required (libbacktrace optional for stack traces on Linux/macOS); log pulls in the rest of coost (flag, string, fs, time, thread) |
| **Minimum toolchain** | C++17 (gcc, clang, MSVC); default builds use -O2 (xmake 'faster', CMake -O2 -g) |
| **Platforms** | Linux, macOS, Windows, FreeBSD; x86, x64, ARM, ARM64 (CI covers Linux, macOS, Windows, Windows-arm64, FreeBSD) |
| **Thread safety** | Thread-safe: per-thread formatting buffer, one global mutex around the shared buffer, single background writer thread. |
| **Drop-in for the baseline** | partial — glog-like severity and check macros, but a different call syntax (variadic concatenation instead of LOG(INFO) &lt;&lt; or fmt strings), configuration through coost flags, and a single global logger instead of spdlog's named loggers and sinks |

## Gotchas

- Harness flaw behind the spdlog table: the harness lives on the separate 'benchmark' branch (benchmark/log_bm.cc, linked only from readme_cn.md). It times co/log's asynchronous in-memory path against spdlog 1.8.5 basic_logger_mt, a synchronous mutex-protected file sink, not spdlog's async logger; the Linux rows were run under the Windows Subsystem for Linux (stated in benchmark/readme.md), where spdlog took 2.08 s versus 0.46 s on native Windows, so the 13-24x Linux ratios mostly measure WSL file I/O for the synchronous side. The harness uses the old LOG &lt;&lt; / log::exit() / flag::init API, so the numbers predate the current code, and the main README's Windows row (0.117704 vs 0.461156) differs from the branch readme's (0.104795 vs 0.534900). No glog harness exists in either branch.
- Lossy under overload: a burst larger than max_log_buffer_size (32 MB, minimum 1 MB) before the writer drains drops the oldest half of the buffered lines; neither benchmark counts the lines written, and a 1 million-line run of roughly 40-80-byte lines is about the size of that buffer.
- The logging thread is started from a flag::parse after-parse hook; if the program never calls flag::parse, lines accumulate in memory and are never written (log::close() then returns without flushing because the thread never started).
- Timestamps are copied from a string the background thread refreshes on each wake-up (every 128 ms by default, sooner under load), so a line's time can lag the real time by up to log_flush_ms; the logger also installs handlers for SIGINT, SIGTERM, SIGQUIT, SIGSEGV, SIGABRT, SIGFPE, SIGBUS and SIGILL and sets SIGPIPE to ignored at static initialization.

## Known shortcomings

- The repo has no glog, spdlog or rapidjson harness: test/log.cc and test/jbm.cc time only co/log and co/json; co/log buffers and flushes asynchronously while the spdlog mode is not stated, so the comparison may be async vs sync; no hardware or flags; the 151x figure is capped at C. Filed under runtime-and-systems/logging-tracing by override although mined into wave 1.
- Enricher found the spdlog harness on the separate benchmark branch (benchmark/log_bm.cc, linked only from readme_cn.md): co/log's async in-memory path is timed against spdlog 1.8.5 basic_logger_mt, a synchronous mutex file sink; the Linux rows ran under WSL (spdlog 2.08 s WSL vs 0.46 s native Windows), so the 13-24x is mostly WSL file I/O; the numbers use the old LOG&lt;&lt; API and the Windows row differs between READMEs; no glog harness exists anywhere. co/log drops the oldest half of its buffer past 32 MB under overload (the benchmark never counts lines), its logger thread starts only from the flag::parse hook, timestamps lag up to 128 ms, and it installs process-wide signal handlers.

## Caveats and trade-offs

First-party README numbers only: no compiler, flags, library versions or CPU models. The benchmark/ directory (atomic, idgen, main, mem, rand, string, time, xtoa) has no log test; test/log.cc -perf times 1 million single-threaded log::info calls and reports separately the time to the in-memory cache and the time after log::close() flushes to file, and test/jbm.cc times co/json only (str() measured once, parse averaged over -n runs), so neither the glog, spdlog nor rapidjson side, nor the 2-8 thread runs, can be reproduced from the repo, and the README does not say whether co/log's figures are cache time or file time. co/log buffers and flushes asynchronously (per test/log.cc), while spdlog's configuration (sink, sync or async mode, version) is not stated, so the spdlog rows may compare async against sync logging. The glog rows are write speeds on different storage (HDD/SSD) and OS combinations. Coost also publishes co/json vs rapidjson (twitter.json minified, stringify/parse in microseconds: win 569/924 vs 2089/2495, mac 783/1097 vs 1289/1658, linux 468/764 vs 1359/1070, claimed 1.4-3.6x) with the same tier-C caveats. [retier] First-party numbers; the spdlog harness lives on the separate `benchmark` branch (benchmark/log_bm.cc, linked only from readme_cn.md). It times co/log's asynchronous in-memory path against spdlog 1.8.5 basic_logger_mt, a synchronous mutex file sink (not spdlog's async logger), and the Linux rows ran under WSL per benchmark/readme.md (spdlog 2.08 s on WSL vs 0.46 s native Windows), so the 13-24x over spdlog is mostly WSL file I/O plus async-vs-sync. Numbers predate the current API (old LOG&lt;&lt; / log::exit), the Windows row differs between the two READMEs, no glog harness exists anywhere, and json_bm.cc also times simdjson but the README omits those rows. co/log is lossy under overload (drops the oldest half of its buffer past max_log_buffer_size 32 MB; the benchmark never counts written lines), the logger thread starts only from the flag::parse hook, timestamps lag up to 128 ms, and it installs process-wide signal handlers. Also publishes co/json vs rapidjson (1.4-3.6x) with the same tier-C caveats.

co/log is part of the coost base library (flags, coroutines, JSON, RPC, allocator in one package), so using it means pulling in coost's flag system and runtime; requires a C++17 compiler.

## Maintenance

Actively maintained (commits through 2026-09-28, CI on five platforms, paid commercial support offered), MIT-licensed with some bundled code under Apache-2.0/Boost, BSD-2-Clause and public-domain terms, but co/log cannot be vendored on its own without coost's flag, string, fs and thread modules.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README tables (glog write speed, spdlog seconds for 1 million logs, rapidjson microseconds) are first-party with no compiler, flags, CPU models or library versions, and only the co/log and co/json halves of the harness exist (test/log.cc, test/jbm.cc), with no glog, spdlog or rapidjson code; the &gt;50x rows (112.5x, 151.3x) with unstated flags are capped at C.
- **Verifier notes:** All log and json numbers match readme.md. Metadata via github.com: MIT, 4.2k stars, 592 forks, not archived or a fork, last commit 2026-09-28. Shortcomings: no baseline harness in the repo (only co/log and co/json halves in test/), unstated spdlog/glog configuration and likely async-vs-sync comparison, no hardware or flags.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** published harness with spdlog in the same mode; enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/readme.md>
  - <https://github.com/idealvin/coost>
  - <https://github.com/idealvin/coost/commits/master>
  - <https://github.com/idealvin/coost/tree/master/benchmark>
  - <https://github.com/idealvin/coost/tree/master/test>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/test/log.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/test/jbm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/log.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/readme_cn.md>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/log.h>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/src/log.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/test/log.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/LICENSE.md>
  - <https://github.com/idealvin/coost>
  - <https://github.com/idealvin/coost/tree/master/src>
  - <https://github.com/idealvin/coost/commits/master>
  - <https://github.com/idealvin/coost/issues?q=is%3Aissue+spdlog>
  - <https://github.com/idealvin/coost/issues?q=is%3Aissue+%E6%97%A5%E5%BF%97>
  - <https://github.com/idealvin/coost/issues/294>
  - <https://github.com/idealvin/coost/tree/benchmark>
  - <https://github.com/idealvin/coost/tree/benchmark/benchmark>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/log_bm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/json_bm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/rapidjson.h>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/spdlog/version.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/idealvin/coost`) · [data/wave1/enrich/raw/github_com_idealvin_coost.json](../../../data/wave1/enrich/raw/github_com_idealvin_coost.json) (enrichment confidence 0.8)

</details>
