# binlog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Asynchronous C++ logger writing structured binary logs; about 15x lower p50 call-site latency than async spdlog in Quill's harness.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Quill README 1-thread number logging: 18/119 ns at 50th/99.9th vs spdlog 271/360 ns; 4 threads 29/445 ns vs spdlog 557/1106 ns. Own README says tens of nanoseconds per event (8-38 ns in its own queue-only benchmark), with no baseline row. |
| **Workload** | Call-site latency of structured binary log event creation via lock-free queues, 1 and 4 threads (Quill harness). |
| **Metric** | latency |
| **Hardware** | Intel Core i5-12600 @ 4.8 GHz, tuned system (isolcpus, nohz_full, mitigations=off), RHEL 9.4 |
| **Compiler and flags** | GCC 14.2, Release, -march=x86-64-v3 |
| **Adoption** | 796 stars |
| **Last commit** | 2026-03-03 |
| **Links** | [repository](https://github.com/morganstanley/binlog) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

In Quill v13's harness (odygrd/logger_benchmarks, GCC 14.2, Release -march=x86-64-v3, Intel Core i5-12600 @ 4.8 GHz on a tuned RHEL 9.4 box), logging two ints and a double took 18/119 ns at p50/p99.9 on 1 thread vs 271/360 ns for async spdlog with a file sink, and 29/445 vs 557/1106 ns on 4 threads; a vector of 16 long strings took 60 vs 6906 ns p50. The 61.79M msg/s backend throughput vs spdlog's 2.57M compares binary output with text output, which Quill itself flags as not comparable.

## Use it when

- Latency-sensitive C++ services (trading, telemetry) where call-site cost matters and an offline decode step is acceptable
- High-volume logging where smaller raw files help: Quill measured 177 MB binary vs 448 MB text for the same messages (35 MB vs 47 MB zipped)
- Logging containers, tuples, optionals, enums and adapted structs without writing formatters; values (e.g. exact floats) are kept losslessly
- Applications with a main loop or a dedicated thread that can call consume() periodically, since the library runs no hidden backend thread
- Post-mortem debugging where recovering the last queued events from a coredump (brecovery) is valuable

## Skip it when

- When logs must be human-readable on disk or piped straight to text tools; every reader needs bread or the binlog reader library
- When tail latency is the target: Quill's harness shows p99.9 of 119 ns (1 thread) and 445 ns (4 threads), against 9-18 ns for Quill, XTR and fmtlog
- Long-lived dependency: the repository was archived read-only on 2026-07-01, with open issues such as a compile error on Ubuntu 24.04 (#189) and an ASAN-reported leak on std::exit (#159)
- Code that logs from global destructors through the default macros (documented undefined behavior from static init order)
- Bursty producers with a slow consumer: a full queue makes the writer allocate a new, larger channel under the session mutex on the hot path, so memory grows instead of dropping or blocking

## How it is fast

The hot path does no text formatting: it computes the serialized size, reserves contiguous space in a single-producer single-consumer byte queue (default 1 MiB per thread-local writer), memcpy-serializes the arguments with the bundled Mserialize library, and commits with one release store of the write index. Metadata goes through a mutex only the first time a call site fires, and the number of placeholders is checked at compile time. Formatting, timestamp rendering and sorting move offline to bread, which is also why the binary-log throughput (61.79M msg/s in Quill's table) is far above text loggers.

## Compared with alternatives

Pick binlog over Quill, XTR or fmtlog when you want a binary log with offline decoding, coredump recovery and lossless typed values, and can accept about 18 ns p50 instead of about 6 ns and a worse p99.9; pick it over BqLog when call-site latency matters (18 vs 125 ns p50 in the same harness). For an actively maintained text logger, Quill is the safer choice.

## Integration

| | |
|---|---|
| **Form** | header-only (producer side); static lib and bread executable for reading |
| **Dependencies** | none for logging (links -lrt on Linux); Boost optional for tests, Google Benchmark optional for perf tests |
| **Minimum toolchain** | C++14, CMake 3.1+; built and tested with recent GCC, Clang and MSVC |
| **Platforms** | Linux, macOS, Windows (per README); log files use host byte order |
| **Thread safety** | Session methods are thread-safe (mutex for metadata and consume); each SessionWriter is single-producer, and the default macros use a thread_local writer, so logging from many threads is safe |
| **Drop-in for the baseline** | no |

## Gotchas

- Getters of adapted structs are called twice per event (once for sizing, once for serializing) and must return the same value, or behavior is undefined
- char\* arguments are logged as a single character by default, not as strings; use const char\* or string_view, or opt in to treating char\* as a string
- Default timestamps use std::chrono::system_clock (about 34 ns per event in its own benchmark vs 9 ns with TSC); a TSC clock needs the _W/_C macro and session setup
- On log rotation you must call Session::reconsumeMetadata, or the new file cannot be decoded on its own

## Known shortcomings

- p99.9 is 119/445 ns, worse than Quill, XTR and fmtlog (9-18 ns); a full queue allocates a new channel under the session mutex on the hot path (unbounded growth); the default clock is system_clock. The 61.79M vs 2.57M msg/s throughput compares binary output with text and is not like for like. Repo archived 2026-07-01; open issues 189 (compile error on Ubuntu 24.04) and 159 (ASan leak on std::exit).

## Caveats and trade-offs

Repository archived and read-only since 2026-07-01 (archived counts as abandoned). Last commit 2026-03-03 (dependabot bump). Own README benchmark (test/perf, Google Benchmark, Xeon E5-2698) measures only event creation into an SPSC queue and says it is not for direct comparison. In the Quill harness its 99.9th percentile is worse than Quill/XTR. Binary log output needs bread to convert to text.

Structured binary log needs binlog tooling to read; recovers events from coredumps; sorted-by-time reading.

## Maintenance

Abandoned: archived read-only on 2026-07-01 after dependabot-only commits (last 2026-03-03), but Apache-2.0 and header-only on the producer side, so vendoring is easy; fixes for open issues will not come upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Quill README latency tables (benchmark code in github.com/odygrd/logger_benchmarks) include MS BinLog and spdlog rows, with GCC 14.2, Release -march=x86-64-v3 and Intel Core i5-12600 @ 4.8 GHz stated: 1 thread 18/119 ns (p50/p99.9) vs spdlog 271/360; 4 threads 29/445 vs 557/1106. Public code, compiler, flags and CPU all present, run by a third party.
- **Verifier notes:** All Quill-harness numbers matched the BinLog and spdlog rows exactly. Stars 796, Apache-2.0, not a fork.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/morganstanley/binlog>
  - <https://github.com/morganstanley/binlog/commits>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/morganstanley/binlog>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/doc/UserGuide.md>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/doc/Internals.md>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/SessionWriter.hpp>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/Session.hpp>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/default_session.hpp>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/detail/Queue.hpp>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/detail/QueueWriter.hpp>
  - <https://raw.githubusercontent.com/morganstanley/binlog/HEAD/include/binlog/basic_log_macros.hpp>
  - <https://github.com/morganstanley/binlog/issues?q=is%3Aissue>
  - <https://github.com/morganstanley/binlog/issues/171>
  - <https://github.com/morganstanley/binlog/issues/159>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://github.com/odygrd/logger_benchmarks>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/HEAD/README.md>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks>
  - <https://github.com/odygrd/logger_benchmarks/tree/master/benchmarks/call_site_latency>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_ms_binlog_call_site_latency.cpp>
  - <https://raw.githubusercontent.com/odygrd/logger_benchmarks/master/benchmarks/call_site_latency/benchmark_spdlog_call_site_latency.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/morganstanley/binlog`) · [data/wave11/enrich/raw/github_com_morganstanley_binlog.json](../../../data/wave11/enrich/raw/github_com_morganstanley_binlog.json) (enrichment confidence 0.85)

</details>
