# Boost.Log

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Boost's attribute-based logging framework; beats a flush-every-line std::fstream only under multithreaded or disk-stalled load.

| | |
|---|---|
| **Beats** | std::fstream with std::flush after every line (also stdio fprintf+fflush and g3log 1.3.2) |
| **Claimed result** | Mixed, and slower than the named baseline in most scenarios. Lower overhead than std::fstream only in multithreaded Mandelbrot and the disk-I/O scenario: 4 threads 13.17 vs fstream 15.66 and stdio 15.03 (about 1.19x lower than fstream, derived from page data), 8 threads 1.82 vs fstream 4.62 and stdio 3.70 (about 2.5x lower, derived from page data), disk I/O 46.03 vs fstream 5719.93 relative call latency (about 124x, derived from page data; fstream flushes every line and hits multi-second kernel stalls while the Boost.Log adapter does not flush). Beats g3log 1.3.2 in periodic calls (67.42 vs 78.19) and call bursts (3.84 vs 4.20). Slower than std::fstream, stdio and spdlog in periodic calls (67.42 vs 41.32, 43.77, 40.85), call bursts (3.84 vs 2.36, 2.55, 1.93) and 1-thread Mandelbrot (15.21 vs 10.73, 12.21, 9.21; slowest of all). All values are relative to reckless (1.00). |
| **Workload** | Third-party logging benchmark by the author of the reckless logger: per-call latency for periodic calls, call bursts and calls interleaved with heavy disk I/O, plus total overhead of logging about one million lines from a multithreaded Mandelbrot computation, all with a synchronous Boost.Log text file sink writing to log.txt. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 2700X 3.7 GHz, 8 cores, SMT off; Samsung 970 EVO 1TB NVMe SSD; WD Red 3TB HDD on a Synology DS216j for the disk-I/O scenario; 32 GiB RAM; Linux 4.14.65 |
| **Compiler and flags** | gcc 7.3.0 and Boost 1.65.0 per the page; the optimisation flags of the published run are not stated (the benchmark build rules use -O3 when CONFIG_DEBUG is not 'yes', while tup.config.template defaults to CONFIG_DEBUG=yes). |
| **Adoption** | 212 stars; part of the Boost C++ Libraries |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/boostorg/log) · [benchmark](https://github.com/mattiasflodin/reckless/blob/master/doc/performance.md) |

## Verdict

Third-party benchmark by the reckless author (doc/performance.md; gcc 7.3.0, Boost 1.65.0, Ryzen 7 2700X, flags of the run unstated): a synchronous Boost.Log text-file sink without auto_flush had lower overhead than a mutex-guarded std::fstream flushed every line in 4-thread Mandelbrot (13.17 vs 15.66), 8-thread Mandelbrot (1.82 vs 4.62) and the disk-I/O scenario (46.03 vs 5719.93), all relative to reckless = 1, but was slower than fstream, stdio and spdlog in periodic calls, call bursts and 1-thread Mandelbrot. Quill's newer harness (Quill v13.0.0, GCC 14.2, i5-12600, async sink) puts it last on number and string latency and throughput, ahead of spdlog only for vector-of-strings records.

## Use it when

- Applications already built on Boost that need structured attributes, run-time filtering and several sinks (rotating files, syslog, Windows event log, IPC queue) from one configuration.
- Multithreaded programs that log heavily to one file and would otherwise use a mutex-guarded std::ofstream flushed each line: in the reckless Mandelbrot run with 8 threads Boost.Log's overhead was 1.82 vs 4.62 for fstream and 3.70 for stdio (relative to reckless = 1).
- Logging on a slow or busy disk where losing the last buffered lines on a crash is acceptable: the buffered sink avoided the multi-second flush stalls that made fstream 124x worse in the reckless disk-I/O scenario (46.03 vs 5719.93).
- Records that stream whole containers through operator&lt;&lt;: in Quill's vector-of-strings table Boost.Log (async sink) beat spdlog at the 90th percentile (4,145 vs 7,120 ns with 1 thread, 4,342 vs 7,581 ns with 4).

## Skip it when

- Latency-critical hot paths: Quill's harness (GCC 14.2, i5-12600) measured 3,093 ns median per call for three numbers vs 271 ns for spdlog, 1,066 ns for g3log and 6 ns for Quill or fmtlog; throughput was 0.33 M msg/s vs 2.57 M for spdlog.
- Single-threaded or low-volume logging: in the reckless run it was slower than plain fstream and stdio in periodic calls (67.42 vs 41.32 and 43.77), call bursts (3.84 vs 2.36 and 2.55) and 1-thread Mandelbrot (15.21 vs 10.73 and 12.21, slowest of all).
- Code with many disabled debug statements: filtered-out records still build a record and allocate (open issue #202 measured about 14 s for 100 million rejected BOOST_LOG_SEV calls); wrap calls in your own level-check macro.
- Crash-forensics logging: without auto_flush the last records sit in the stream buffer, and the docs say enabling auto_flush degrades performance; the default asynchronous queue is unbounded and the docs warn it can grow without limit.
- Builds that cannot take compiled Boost libraries, RTTI-off code or LTO: it needs Boost.Filesystem, System, DateTime and Thread binaries, requires RTTI, and does not support LTO.

## How it is fast

It is not built for low call-site latency. Its advantages in third-party runs come from structure rather than a fast path: the file backend writes through a buffered stream and flushes only when auto_flush is enabled, formatting happens before the backend lock so several threads can format concurrently, and the severity level is kept in thread-local storage so that severity loggers avoid the logger mutex. An asynchronous_sink frontend moves the write to a dedicated thread through a FIFO or ordering queue (bounded or unbounded, block or drop on overflow).

## Compared with alternatives

Pick Boost.Log over the catalogued fast loggers (Quill, fmtlog, PlatformLab NanoLog, binlog, XTR) only when you need its attribute, filter and sink framework and already ship Boost; for call-site latency those siblings are roughly 170x to 500x faster in Quill's tables, g3log beats it there too (though not in reckless's periodic and burst runs), and glog beat it about 3.9x in an old spdlog table.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (must be shared when several modules of one application log) |
| **Dependencies** | Boost.Filesystem, Boost.System, Boost.DateTime, Boost.Thread, Boost.Regex in some configurations, Boost.Asio unless BOOST_LOG_WITHOUT_ASIO; boost_log_setup for settings parsers |
| **Minimum toolchain** | C++11 (C++03 dropped in Boost 1.84); GCC 5+, Clang 3.5+, MSVC 14.0+; RTTI required; LTO not supported |
| **Platforms** | Linux, Windows 10, Cygwin, other POSIX systems Boost supports (OpenBSD process-name support added for Boost 1.93); any architecture Boost supports, i586+ on 32-bit x86 |
| **Thread safety** | _mt loggers and the synchronous and asynchronous sink frontends are thread-safe; records from one thread keep their order but records from different threads are only weakly ordered; forking a multithreaded process can leave Boost.Log locks broken |
| **Drop-in for the baseline** | no |

## Gotchas

- The reckless comparison is unequal: its Boost.Log adapter calls add_file_log without auto_flush (buffered) while the fstream and stdio adapters flush every line, and the fstream adapter writes no timestamp or severity while Boost.Log formats both, so the wins come from the flush policy and the losses partly from extra formatting. The page also says spdlog was put in force-flush mode, but its adapter passes true as the third argument of basic_logger_mt, which in spdlog 1.3.1 is truncate, so spdlog ran buffered too.
- The published reckless run states gcc 7.3.0 and Boost 1.65.0 but not its flags, and the public tup.config.template defaults to CONFIG_DEBUG=yes, which Tuprules.lua builds at -O0; the numbers are also about eight years and roughly 28 Boost releases old (the C++ std threading switch in 1.87 changed internals).
- Shared global loggers are a contention point: the maintainer advises per-thread non-_mt loggers and avoiding global loggers (issue #144: severity_channel_logger_mt was 7.9x slower than severity_logger_mt with 10 threads); the reckless adapter uses one global severity_logger_mt.
- Boost.Log's win over spdlog in Quill's vector-of-strings table compares a hand-written loop that streams each string with quotes (logger_benchmarks benchmark_boost_log_call_site_latency.cpp) against spdlog formatting the vector through fmt's range formatter, so the two do different work.

## Known shortcomings

- Downgraded B to C: in reckless doc/performance.md Boost.Log is slower than fstream, stdio and spdlog in 3 of 5 scenarios; its wins over fstream (4-thread and 8-thread Mandelbrot, disk I/O 124x) come from setup, since the Boost.Log adapter has no auto_flush while the fstream adapter flushes every line; published-run flags unstated and tup.config.template defaults to CONFIG_DEBUG=yes (-O0). The record missed the 4-thread table (13.17 vs 15.66).
- Enricher: in reckless, Boost.Log is buffered while fstream and stdio flush every line and the fstream line has no timestamp or severity; the reckless spdlog adapter passes true as truncate in spdlog 1.3.1 basic_logger_mt, not force-flush as the page claims, so spdlog is also buffered there; the shared global severity_logger_mt is a contention point (maintainer, issue #144); filtered records cost about 14 s per 100M calls (open #202). Quill tables: 3093 ns median, 0.33M msg/s; Quill's vector win over spdlog (4145 vs 7120 ns p90) compares a hand loop with fmt's range formatter.

## Caveats and trade-offs

Boost.Log is not claimed to be fast by its authors, and the numbers come from a competitor's benchmark (reckless) in which Boost.Log is slower than reckless, spdlog and often plain stdio and std::fstream. Its only wins against std::fstream (4- and 8-thread Mandelbrot, disk I/O) are tilted by configuration: the reckless adapter (benchmarks/boost_log.hpp) uses add_file_log without keywords::auto_flush, so Boost.Log writes through a buffer and does not flush per record, while the fstream adapter ends every line with std::endl or std::flush and the stdio adapter calls fflush; the 124x disk-I/O ratio is driven by multi-second synchronous flush stalls in fstream, which a buffered ofstream would avoid. Results are from Boost 1.65.0 and gcc 7.3.0 (about 2018), the flags of the published run are not stated (tup.config.template defaults to CONFIG_DEBUG=yes, which Tuprules.lua builds at -O0; release is -O3), and the page gives charts plus relative-time tables with IQR only. Other third-party shootouts show Boost.Log slower than the incumbents they list: NanoLog README latency table (Boost 1.55 1764 ns vs glog 1198 ns vs spdlog 214 ns, static string, 50th percentile) and an older spdlog README table (boost log 1.54 4.169 s vs glog 1.066 s vs spdlog 0.302 s for 1M lines, single thread; snippet only, page not opened, row no longer in the current README). Boost.org documentation was not reachable from this environment.

Large, highly modular and extensible library (sources, filters, formatters, many sink backends) with a heavy abstraction level and Boost dependencies. The library's own README and docs (rationale, intro) state performance as a goal but publish no numbers; repo test/performance holds only internal timing programs (record_emission.cpp, dump.cpp) with no external baseline.

## Maintenance

Actively maintained by Andrey Semashev as part of Boost (develop commits through 2026-10-02, changelog at Boost 1.93, 13 open issues) under BSL-1.0, but it is a feature-rich framework rather than a fast logger: choose it for flexibility, not speed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** Third-party benchmark code is public (reckless benchmarks/\*.cpp, adapters benchmarks/boost_log.hpp and fstream.hpp) with gcc 7.3.0 and a Ryzen 7 2700X stated, but the flags of the published run are not stated and the public tup.config.template defaults to CONFIG_DEBUG=yes, which Tuprules.lua maps to -O0, so the build flags are absent from public sources (tier C rule). The wins over the named baseline also come from an unequal setup: the Boost.Log adapter calls add_file_log without auto_flush (buffered), while the fstream adapter flushes after every line.
- **Verifier notes:** Numbers on reckless doc/performance.md match the record, but the record missed the 4-thread Mandelbrot table (Boost.Log 13.17 beats fstream 15.66 there too). Shortcomings for the orchestrator: slower than std::fstream and stdio in 3 of 5 scenarios; wins over fstream come from a buffered (no auto_flush) Boost.Log sink against a flush-every-line fstream; published-run flags unstated with a -O0 default in the public config; Boost 1.65 era numbers. Metadata checked: BSL-1.0, 212 stars, last commit 2026-10-02 on develop, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 11); enricher w11 pair-018
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/doc/performance.md>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/boost_log.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/fstream.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/Tupfile.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/Tuprules.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/tup.config.template>
  - <https://github.com/boostorg/log>
  - <https://github.com/boostorg/log/commits>
- **Sources the enricher read:**
  - <https://github.com/boostorg/log>
  - <https://github.com/boostorg/log/commits/develop>
  - <https://raw.githubusercontent.com/boostorg/log/develop/README.md>
  - <https://github.com/boostorg/log/tree/develop/doc>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/install.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/intro.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/rationale.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/changelog.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/sink_backends.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/doc/sink_frontends.qbk>
  - <https://raw.githubusercontent.com/boostorg/log/develop/test/performance/record_emission.cpp>
  - <https://github.com/boostorg/log/issues?q=is%3Aissue%20performance>
  - <https://github.com/boostorg/log/issues/202>
  - <https://github.com/boostorg/log/issues/144>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/doc/performance.md>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/boost_log.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/fstream.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/stdio.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/spdlog.hpp>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/benchmarks/Tupfile.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/Tuprules.lua>
  - <https://raw.githubusercontent.com/mattiasflodin/reckless/master/tup.config.template>
  - <https://raw.githubusercontent.com/gabime/spdlog/v1.3.1/include/spdlog/sinks/basic_file_sink.h>
  - <https://raw.githubusercontent.com/odygrd/quill/master/README.md>
  - <https://github.com/odygrd/logger_benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks/call_site_latency>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_boost_log_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_spdlog_call_site_latency.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/boostorg/log`) · [data/wave11/enrich/raw/github_com_boostorg_log.json](../../../data/wave11/enrich/raw/github_com_boostorg_log.json) (enrichment confidence 0.65)

</details>
