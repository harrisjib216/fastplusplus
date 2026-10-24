# uberlog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Two-process C++ logger: callers format into a shared-memory ring that a child process drains, avoiding one write() per message.

| | |
|---|---|
| **Beats** | synchronous write-per-message file logging (a 'naive logging system' that issues one OS write call per message) |
| **Claimed result** | README: 200 ns (Windows) and 280 ns (Linux) per formatted message, 350 MB/s and 465 MB/s throughput, versus about 2500 ns per message for a naive write-per-message logger, 'a 10x speedup over a naive system'; at 100000 messages per second the naive logger spends 25% of time logging against 2% for uberlog. Ratios derived from page data: 2500/280 is about 8.9x on Linux and 2500/200 is 12.5x on Windows. |
| **Workload** | README Benchmarks: time taken inside the calling program to format a roughly 200-byte message and push it into the shared-memory ring buffer (200 ns Windows, 280 ns Linux), against a hypothetical naive logger costing about 1500 ns for a 100-byte write() plus an assumed 1000 ns of formatting. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-6700K (Windows and Linux) |
| **Compiler and flags** | Not stated for the README numbers. The repo build script uses clang++ -O2 -ggdb -std=c++11 on Linux and macOS; an msvc/ project covers Windows. |
| **Adoption** | 18 stars, 10 forks |
| **Last commit** | 2020-04-08 |
| **Links** | [repository](https://github.com/IMQS/uberlog) · [benchmark](https://github.com/IMQS/uberlog) |

## Verdict

The README reports 200 ns (Windows) and 280 ns (Linux) per formatted message and 350/465 MB/s throughput on an i7-6700K with no compiler or flags, against a naive write()-per-message logger whose about 2500 ns per message is an estimate (a quoted 1500 ns 100-byte write() plus an assumed 1000 ns of formatting), not a measured run. The current test.cpp measures mean enqueue latency only (no percentiles, writer-process work excluded) with formatted lines of about 108-114 bytes rather than the 200 bytes the README states; its throughput bench pushes unformatted 200-byte LogRaw messages, its write() bench uses 5-byte writes, and its 'spd comparison' contains no spdlog code.

## Use it when

- Application or service logs at thousands to tens of thousands of messages per second, where a write() per message is measurable and you want the log tail to survive a crash of the main process.
- Cross-platform (Windows, Linux, macOS) programs that want one small MIT-licensed logger with no dependencies and built-in size-based rolling.
- Kernels with costly syscalls (KPTI mitigations), where moving file writes to another process helps; the README argues this but did not measure it.
- Single-threaded or lightly threaded producers whose messages fit the 200-byte stack buffer.

## Skip it when

- Hot-path or low-latency logging: its 200-280 ns enqueue (README, i7-6700K) is far above in-process asynchronous loggers such as Quill, fmtlog or PlatformLab NanoLog, which report single-digit nanoseconds in their catalog entries.
- Many threads logging at once: every LogRaw call takes a single std::mutex per Logger, and no multithreaded numbers exist.
- Deployments that cannot ship and launch a second executable (uberlogger must sit next to the program or be named with SetLoggerProgramPath), or sandboxes that forbid process spawning or POSIX shared memory.
- Durability against power loss or OS crashes: the writer calls write() with no fsync, so only crashes of the main process are covered.
- Projects that need a maintained dependency: no commits since 2020-04-08, no releases and no CI configuration.

## How it is fast

The calling thread only formats into a 200-byte stack buffer, stamps a cached date string (TimeKeeper rebuilds the YYYY-MM-DD part once a day and formats only the time-of-day digits per message), takes a mutex and memcpys a header plus payload into the shared-memory ring, then publishes with an atomic write-pointer store. All file syscalls happen in the uberlogger process, which batches small messages into a 1 KB write buffer and backs off its polling (up to 1024 ms sleeps) when idle. The README attributes about 40 ns to the ring copy and 130 ns to the date string, the rest to message formatting.

## Compared with alternatives

Pick uberlog over Quill, fmtlog or PlatformLab NanoLog only when keeping the log tail after a main-process crash (a separate process drains the shared ring once the parent dies) matters more than hot-path cost, which is 200-280 ns here against single-digit nanoseconds for those in-process loggers. Against a plain write()-per-message logger, its own README says it only pays off above several thousand messages per second.

## Integration

| | |
|---|---|
| **Form** | source-drop (uberlog.cpp and tsf.cpp in your program, plus a separately built uberlogger executable) |
| **Dependencies** | none (tsf is embedded; -lrt on Linux) |
| **Minimum toolchain** | C++11 (build script uses clang++ -O2 -std=c++11; an MSVC project covers Windows) |
| **Platforms** | Windows, Linux, macOS |
| **Thread safety** | Logging calls may come from any thread: formatting runs outside the lock and LogRaw serializes ring writes on one std::mutex per Logger. At midnight the cached date string is rewritten under its own mutex while other threads may read it unlocked. |
| **Drop-in for the baseline** | partial: replaces a hand-rolled write()-per-message logger, but needs the uberlogger helper binary, its fixed line format and its own printf-compatible API |

## Gotchas

- Off-by-two in the embedded tsf no-argument fast path: fmt_core accepts len &lt;= staticbuf_size + 1 and then copies len + 1 bytes, so a log call with no format arguments whose text is 157 or 158 characters on Linux (156 or 157 on Windows) with the default 42-byte date prefix writes up to 2 bytes past Log()'s 200-byte stack buffer, and LogRaw then reads past it. Calls with arguments go through a bounds-checked buffer.
- On Linux every formatted message calls syscall(__NR_gettid) for the thread-id column, so formatted logging is not syscall-free despite the README's KPTI argument; TeeStdOut adds a write() per message.
- The producer never drops: when the ring is full it sleeps in a loop (0, then 1, then 5 ms) until the writer catches up, and the writer may be in an idle backoff sleep of up to 1024 ms. The first message after Open waits up to 10 s for the child to drain it, and a message larger than the ring (default 1 MB) is truncated with an out-of-band warning.
- Timestamps use the standard-time UTC offset from libc's timezone variable (ftime on Windows) read once at Logger construction, so during daylight saving time lines show standard time, not wall-clock time.

## Known shortcomings

- README numbers (i7-6700K, 200/280 ns) compare against an estimated naive write-per-message logger (about 2500 ns), not a measured run; no compiler or flags and no stored results; the repo's spdlog comparison bench has no spdlog code. Last commit 2020-04-08.
- security bug: tsf no-argument fast path writes up to 2 bytes past Log()'s 200-byte stack buffer for 157-158 character messages

## Caveats and trade-offs

The baseline is hypothetical, not a measured run: the 2500 ns figure adds a quoted \~1500 ns write() cost to an assumed 1000 ns of formatting. test.cpp does time a 5-byte write() (BenchFileWriteLatency, 200000 iterations) and the logger latency modes (raw, simple fmt, param fmt; 50000 messages after 100 warmup into a 32 MB ring sized never to stall), but no result file is stored and the README numbers name no compiler or flags. test.cpp also has a 'spd comparison' benchmark that only times 1M uberlog Info() calls and contains no spdlog code; there are no spdlog numbers anywhere in the repo. Third-party logging shootouts found (MuggleWei cc_log_benchmark) do not list uberlog. Latency counts only the in-program cost, not the writer process's work. README itself says a naive logger is fine below many thousands of messages per second, and the 2018 Meltdown/KPTI benefit is 'not measured'. The seed lead (from a C++ book) says it is not as fast as specialized low-latency loggers. No commits since 2020-04-08 (over 6 years); no releases. [retier] Enricher, security bug: the embedded tsf no-argument fast path checks len &lt;= staticbuf_size + 1 and then copies len + 1 bytes, so a no-argument message of 157 or 158 characters on Linux (156 or 157 on Windows) with the date prefix writes up to 2 bytes past Log()'s 200-byte stack buffer. Harness mismatch: the README cites \~200-byte formatted messages, but test.cpp's latency bench uses \~108-114 bytes and reports the mean only; the throughput bench sends raw 200-byte LogRaw messages with no formatting; the write() bench uses 5-byte writes. Each formatted message makes a syscall(__NR_gettid) on Linux, which undercuts the README's few-syscalls argument. One mutex per Logger; producers sleep-spin when the ring is full; the writer's idle backoff grows to 1024 ms; no fsync; timestamps use the standard-time offset, one hour off during DST.

Multi-process design: a spawned child process (uberlogger) drains a shared-memory ring buffer and writes the file, so a crash in the main process still flushes earlier messages; the caller stalls only when the ring is full. Adds a second process and shared memory; fixed log line format unless you derive from Logger; printf-compatible type-safe formatting (tsf); log rolling built in; C++11.

## Maintenance

Abandoned since 2020-04-08 (68 commits, 18 stars, no releases, one closed issue) but MIT-licensed and about 2,400 lines, so it can be vendored after fixing the tsf no-argument buffer check.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Benchmarks table (i7-6700K: 200 ns / 350 MB/s Windows, 280 ns / 465 MB/s Linux) with no compiler, flags or stored results for those runs; the 2500 ns naive-logger baseline is an estimate (quoted \~1500 ns write() plus an assumed 1000 ns of formatting), not a measured run. test.cpp holds latency and write() benches but no results, so C.
- **Verifier notes:** README, LICENSE (MIT, IMQS Software 2016), build script (clang++ -O2 -ggdb -std=c++11) and test.cpp benches checked; repo page shows 18 stars, 10 forks, 68 commits, last commit Apr 8 2020. Record accurate apart from the age wording in caveats.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/IMQS/uberlog>
  - <https://github.com/IMQS/uberlog/commits>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/build>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/IMQS/uberlog>
  - <https://github.com/IMQS/uberlog/commits/master>
  - <https://github.com/IMQS/uberlog/issues?q=is%3Aissue>
  - <https://github.com/IMQS/uberlog/issues/2>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/build>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/uberlog.h>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/uberlog.cpp>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/uberlogger.cpp>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/tsf.h>
  - <https://raw.githubusercontent.com/IMQS/uberlog/HEAD/tsf.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/imqs/uberlog`) · [data/wave11/enrich/raw/github_com_imqs_uberlog.json](../../../data/wave11/enrich/raw/github_com_imqs_uberlog.json) (enrichment confidence 0.75)

</details>
