# llcpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++17 synchronous binary logger: writes format string plus raw argument bytes, about 4x lower median latency than spdlog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | 1 thread: 165 ns median (timestamp) vs spdlog 729 ns (about 4.4x, derived from page data); 4 threads: 173 ns vs spdlog 1100 ns (about 6.4x, derived from page data). Total time 0.42 s vs 0.95 s (1 thread). |
| **Workload** | Single-thread and 4-thread logging of lines to /tmp on SSD; per-call latency percentiles vs mini-async-logger, NanoLog, spdlog and g3log. |
| **Metric** | latency |
| **Compiler and flags** | Clang 5.0.1, --std=c++1z -flto -O3, Ubuntu 16.04.03 |
| **Adoption** | 85 stars |
| **Last commit** | 2017-11-03 |
| **Links** | [repository](https://github.com/blapid/llcpp) · [benchmark](https://github.com/blapid/llcpp) |

## Verdict

Author's README, Ubuntu 16.04.03, Clang 5.0.1 with --std=c++1z -flto -O3, logging to /tmp on an SSD, CPU not stated: median per-call 165 ns vs spdlog 729 ns at 1 thread and 173 vs 1100 ns at 4 threads, total 0.42 s vs 0.95 s (1 thread) and 1.61 s vs 1.91 s (4 threads), while spdlog has the better 99th percentile; spdlog wrote formatted text and llcpp wrote binary, and the harness lives only in a blog post that is blocked here.

## Use it when

- Linux/macOS service where logs are shipped through a pipeline anyway and a post-processing decode step is acceptable.
- Single-threaded hot paths that log a few integers and short strings per line and want sub-200 ns median call cost without a background thread.
- Embedded or constrained code that needs zero allocation per log call and compile-time format/argument type checking.
- As a small reference design for compile-time format parsing with UDL templates, to copy and harden.

## Skip it when

- Multi-threaded logging to one file: the per-thread 4 KB buffer is flushed mid-line when the next part does not fit, so pieces of a line from different threads can interleave in the shared FILE\*, which breaks the sequential binary stream the parser expects (from reading logging.hpp; not run).
- When tail latency matters: its own table shows 99th percentile 2058 ns vs spdlog 973 ns (1 thread) and 7501 vs 1373 ns (4 threads), because the thread that fills the buffer pays the fwrite.
- When you need human-readable logs on disk, floating-point or %p/%c specifiers (only %d, %u, %x, %s), log-level filtering, rotation, or async sinks.
- MSVC or any compiler without the GNU string-literal operator template extension; prefix code also uses POSIX localtime_r/gmtime_r.
- Production use in general: README says proof-of-concept, last commit 2017-11-03, error handling is marked TODO.

## How it is fast

The format string is captured at compile time through a GNU string-literal operator template, parsed by constexpr template metaprogramming into a tuple of per-argument serializers, and type-checked statically, so the call site does no parsing, no allocation and no number-to-text conversion. Each call memcpy's the format bytes and argument bytes into a 4 KB thread_local buffer in file_logger and only calls fwrite when that buffer fills. The speed is mostly from skipping text formatting (binary vs text comparison) and from batching writes.

## Compared with alternatives

Pick it only if you want a tiny, synchronous, allocation-free header to study or fork; for real use, Quill, fmtlog, PlatformLab NanoLog or binlog are maintained, thread-safe, async, and report far lower call-site latency (single-digit to tens of ns) on the same spdlog comparison.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Python for the decoder script) |
| **Minimum toolchain** | C++17; tested on Clang 5.0.1 (Ubuntu) and Apple Clang 900; needs GNU UDL template extension |
| **Platforms** | Linux, macOS (POSIX time functions); little-endian assumed by the binary format |
| **Thread safety** | Not documented. Buffers are static thread_local per logger type, so writes do not race, but lines from different threads can be split across fwrite calls and interleave; caches of threads other than the one destroying the logger are never flushed. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 4 KB cache is a static thread_local member per file_logger template instantiation, so two loggers of the same type on one thread share one buffer and a flush goes to whichever logger's file triggered it.
- Only the destroying thread's buffer is flushed in \~file_logger; up to 4 KB of each other thread's last lines is lost at exit unless that thread logs enough to trigger a flush.
- The full format string is written for every line (no string-table id), so files are larger than NanoLog-style dictionary logs; %s writes a 4-byte length plus bytes, %Ns pads or truncates to N bytes.
- %ld/%lld widths are derived from the count of 'l' (4 bytes per 'l'), which assumes LP64 long; the decoder must match the writer's platform.

## Known shortcomings

- Likely log corruption behind the 4-thread numbers: the 4 KB thread_local cache flushes mid-line into a shared FILE\*, so lines from several threads can interleave. Other threads' caches are never flushed at destruction (up to 4 KB lost each), same-type loggers share one cache per thread, and p99 is worse than spdlog. Read from logging.hpp, not run.

## Caveats and trade-offs

README marks it proof-of-concept; benchmarks from 2017 on old Clang with no CPU model stated; the benchmark harness is described in a blog post that is not reachable here (blapid.github.io blocked); spdlog was measured at default text formatting so the comparison is binary versus text output. Its own table shows spdlog with a better 99th percentile (973 ns vs 2058 ns, 1 thread).

Writes a binary log (format string plus raw argument bytes) that needs a separate script to turn into text; synchronous, no async backend; requires C++17 and a GNU user-defined string literal extension.

## Maintenance

Abandoned proof-of-concept (last commit 2017-11-03, 2 open feature-request issues) but MIT-licensed and about ten small headers, so easy to vendor and fix if the binary-log model fits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README tables give first-party percentiles vs spdlog with compiler and flags (Clang 5.0.1, --std=c++1z -flto -O3) but no CPU model and no benchmark code in the repo (only include/ and scripts/; harness described in a blocked blog post), so C.
- **Verifier notes:** All numbers verified: 1 thread llcpp (timestamp) p50 165 ns vs spdlog 729, total 0.42 s vs 0.95 s; 4 threads 173 vs 1100 ns; spdlog p99 973 vs llcpp 2058 (1 thread). Note 4-thread total time llcpp 1.61 s vs spdlog 1.91 s, and llcpp is synchronous. MIT, 85 stars, last commit 2017-11-03, not archived.
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/README.md>
  - <https://github.com/blapid/llcpp>
  - <https://github.com/blapid/llcpp/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/README.md>
  - <https://github.com/blapid/llcpp/tree/master/include/llcpp>
  - <https://github.com/blapid/llcpp/tree/master/include/llcpp/detail>
  - <https://github.com/blapid/llcpp/tree/master/scripts>
  - <https://github.com/blapid/llcpp/issues>
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/include/llcpp/llcpp.hpp>
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/include/llcpp/detail/logging.hpp>
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/include/llcpp/detail/log_line.hpp>
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/include/llcpp/detail/terminators.hpp>
  - <https://raw.githubusercontent.com/blapid/llcpp/HEAD/include/llcpp/detail/prefix.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/blapid/llcpp`) · [data/wave11/enrich/raw/github_com_blapid_llcpp.json](../../../data/wave11/enrich/raw/github_com_blapid_llcpp.json) (enrichment confidence 0.75)

</details>
