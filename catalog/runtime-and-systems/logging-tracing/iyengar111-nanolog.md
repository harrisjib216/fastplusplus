# NanoLog (Iyengar111)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT (full text in NanoLog.hpp and NanoLog.cpp, Copyright 2016 Karthik Iyengar)` · 🔴 abandoned

> Small asynchronous C++11 stream-style logger; lower median caller latency than spdlog async, far behind Quill/fmtlog/PlatformLab NanoLog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Quill harness, 1 thread, LOG_INFO two ints and a double: Iyengar NanoLog 106/155/491 ns vs spdlog 271/296/360 ns (50th/90th/99.9th); 4 threads 73/267/1419 vs spdlog 557/614/1106 (99.9th worse than spdlog). Own README (1 thread, us): guaranteed average 0.347930 vs spdlog 2.588590, 50th 0 vs 3. |
| **Workload** | Caller latency percentiles in microseconds for guaranteed and non-guaranteed loggers, 1-4 threads, vs spdlog, g3log and reckless. |
| **Metric** | latency |
| **Hardware** | Intel i7-2630QM @ 2.00GHz, Linux Mint 17 |
| **Compiler and flags** | g++ 4.8.4 (README) |
| **Adoption** | 753 stars |
| **Last commit** | 2017-03-08 |
| **Links** | [repository](https://github.com/Iyengar111/NanoLog) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

In the independent Quill benchmark (odygrd/logger_benchmarks, GCC 14.2, -march=x86-64-v3, i5-12600, logging two ints and a double) Iyengar NanoLog's caller latency is 106/155/491 ns at the 50th/90th/99.9th percentile with 1 thread versus spdlog 271/296/360 ns, and 73/267/1419 ns versus 557/614/1106 ns with 4 threads, so it wins the median but loses the 1-thread and 4-thread 99.9th percentile. Its own README (g++ 4.8.4, i7-2630QM, flags not given, microsecond timer) shows a 0.35 us average versus spdlog async 2.59 us at 1 thread.

## Use it when

- Legacy or C++11-only codebases that want an async file logger in two source files with no dependencies
- Moderate-rate logging of short lines (under about 256 bytes, so no heap allocation per line) where median caller latency matters more than tail latency
- As a readable reference design for deferred-formatting loggers (binary encode on the hot path, stringify on a worker)
- When you can tolerate dropped lines and want a producer that never blocks on a full queue (NonGuaranteedLogger)

## Skip it when

- Latency-critical work today: in the Quill harness it trails Quill, fmtlog, XTR, MS BinLog and PlatformLab NanoLog by roughly 10x at the median, and its 4-thread 99.9th percentile (1419 ns) is worse than spdlog's (1106 ns)
- When you need console sinks, custom formatting, local-time timestamps, appending to an existing file, or structured output: none are provided
- Bursty high-volume logging in guaranteed mode: the producer that fills a buffer allocates the next 8 MB buffer in its own call, other producers spin, and memory grows without bound if the writer falls behind
- Production systems that need a maintained project: abandoned since 2017-03-08 with 18 open issues, including #39 (2025) reporting producer blocking in NonGuaranteedLogger and lost final lines at shutdown in GuaranteedLogger

## How it is fast

The calling thread only encodes raw binary arguments (timestamp, thread id, file/function pointers, then typed values) into a 256-byte NanoLogLine with an inline stack buffer, so string literals are stored as pointers (zero copy) and integer/double-to-text conversion is deferred to the consumer thread. The guaranteed mode pushes into a chain of 8 MB buffers of 32768 slots claimed with one relaxed fetch_add and a per-slot release flag; the non-guaranteed mode is a fixed MPSC ring of 256-byte cache-aligned slots, each guarded by a per-slot atomic_flag spinlock. Formatting with std::ostream, timestamp printing and file I/O all happen on the single background thread.

## Compared with alternatives

Pick it only when you want the smallest possible C++11 async logger to vendor or study; for real speed choose PlatformLab NanoLog, Quill or fmtlog, which beat it by about 10x at the median in the same Quill harness and are maintained.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard library only; std::thread needs -pthread) |
| **Minimum toolchain** | C++11 (README benchmark built with g++ 4.8.4) |
| **Platforms** | any platform with a C++11 standard library; README numbers from Linux Mint 17 on x86-64 |
| **Thread safety** | Logging macros are safe to call from many threads after initialize(); one background thread consumes. Calling a LOG_ macro before initialize() dereferences a null logger pointer. |
| **Drop-in for the baseline** | no |

## Gotchas

- License: GitHub shows none and no LICENSE file exists (issue #32), but both NanoLog.hpp and NanoLog.cpp open with the full MIT License text, Copyright (c) 2016 Karthik Iyengar, so the code is copyable under MIT with that notice kept.
- Every log line is terminated with std::endl, which flushes the ofstream per line on the writer thread (issue #31); this caps writer throughput and was not part of the caller-latency benchmark.
- The writer thread sleeps 50 us whenever the queue is empty, timestamps come from std::chrono::high_resolution_clock at microsecond resolution and are printed in UTC via std::gmtime (issues #11, #24, #39).
- The README benchmark timed each call with a microsecond clock, so the 50th percentile of 0 us and the 0.35 us average are quantized; the Quill harness, which reports nanoseconds, is the more reliable comparison.

## Known shortcomings

- Own README timer has only microsecond resolution (p50 quantized to 0 us); std::endl flushes every line (issue 31); guaranteed mode mallocs 8 MB on the producer with unbounded growth; issue 39 reports shutdown line loss and NonGuaranteed producer blocking. The Quill-harness numbers behind tier A are unaffected.

## Caveats and trade-offs

No LICENSE file and GitHub shows none, so reference only. Own README benchmark gives no compiler flags and uses g++ 4.8.4 on an i7-2630QM; tier A rests on the Quill author's public harness. In that harness it beats spdlog at median and 90th but its 4-thread 99.9th (1419 ns) is worse than spdlog (1106 ns), and it is far slower than Quill, fmtlog, XTR and PlatformLab NanoLog. Unrelated to PlatformLab NanoLog.

Header plus source, standard C++11 only; no license file found, so code cannot be assumed copyable.

## Maintenance

Abandoned since 2017-03-08 (753 stars, 18 open issues); the MIT notice in both source files makes it copyable despite GitHub showing no license, and it is small enough to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Own README (nano_vs_spdlog_vs_g3log_vs_reckless.cpp, g++ 4.8.4, i7-2630QM) lacks flags, so alone it is C; the independent Quill README harness (public code at odygrd/logger_benchmarks, CMake Release, GCC 14.2, -march=x86-64-v3, i5-12600) lists Iyengar NanoLog 106/491 ns vs spdlog 271/360 ns (50th/99.9th, 1 thread), which meets A.
- **Verifier notes:** Numbers on both pages match. Repo: 753 stars, not archived or forked, last commit 2017-03-08 (abandoned), no license.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`, `license`, `usability`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Iyengar111/NanoLog/HEAD/README.md>
  - <https://github.com/Iyengar111/NanoLog>
  - <https://github.com/Iyengar111/NanoLog/commits/master>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://github.com/odygrd/logger_benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Iyengar111/NanoLog/HEAD/README.md>
  - <https://raw.githubusercontent.com/Iyengar111/NanoLog/HEAD/NanoLog.hpp>
  - <https://raw.githubusercontent.com/Iyengar111/NanoLog/HEAD/NanoLog.cpp>
  - <https://raw.githubusercontent.com/Iyengar111/NanoLog/HEAD/nano_vs_spdlog_vs_g3log_vs_reckless.cpp>
  - <https://github.com/Iyengar111/NanoLog>
  - <https://github.com/Iyengar111/NanoLog/issues>
  - <https://github.com/Iyengar111/NanoLog/issues/39>
  - <https://github.com/Iyengar111/NanoLog/issues/32>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/iyengar111/nanolog`) · [data/wave11/enrich/raw/github_com_iyengar111_nanolog.json](../../../data/wave11/enrich/raw/github_com_iyengar111_nanolog.json) (enrichment confidence 0.8)

</details>
