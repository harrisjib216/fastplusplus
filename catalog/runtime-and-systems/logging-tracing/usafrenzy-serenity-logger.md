# Serenity Logger

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Alpha C++20 synchronous logger (console, file, rotating targets) whose own crude benchmark beats spdlog's single-threaded sinks.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | README: file target 215.981 ns vs spdlog basic file sink 1125.735 ns; rotating 627.968 vs 2919.572 ns; console 5.656 vs 10.837 ns. README says console \~40-42%, file \~79-81% and rotating \~78-79% faster (about 5.2x, 4.6x and 1.9x derived from page data). |
| **Workload** | Single-threaded, 400-byte C-string message, 1,000,000 iterations, console (output disabled), file and rotating-file targets. |
| **Metric** | latency |
| **Adoption** | 3 stars |
| **Last commit** | 2023-03-25 |
| **Links** | [repository](https://github.com/USAFrenzy/Serenity_Logger) · [benchmark](https://github.com/USAFrenzy/Serenity_Logger#statistics) |

## Verdict

First-party README table dated 05Jul22: one thread logging a 400-byte string, Serenity FileTarget 215.981 ns vs spdlog basic_file_sink_st 1125.735 ns (about 5.2x), RotatingTarget 627.968 vs spdlog rotating_file_sink_st 2919.572 ns (about 4.6x), console 5.656 vs 10.837 ns (about 1.9x, but with both loggers at level off) (ratios derived from page data); compiler, flags, CPU and spdlog version not stated, and the harness was apparently built with MSVC on Windows.

## Use it when

- Single-threaded Windows/MSVC program that logs large volumes of text to one file and can tolerate up to several MB of unwritten log on a crash
- Learning or experimenting with a small, readable logger codebase built on C++20 concepts and jthread
- Writing a home-grown sink and wanting a reference for buffer-then-bulk-write file output

## Skip it when

- Any production use: the README calls it an alpha learning project and the last commit was 2023-03-25
- Linux or macOS builds: FileHelper.cpp defines a 'Write' macro for non-Windows while the code calls WRITE, uses Windows-only _O_WRONLY/_O_BINARY flags and the MSVC STL internal path::_Remove_filename_and_separator, and CI is a single msvc.yml workflow
- Latency-critical or multi-threaded hot paths: logging is synchronous on the calling thread; async front ends such as Quill, fmtlog, NanoLog or XTR are an order of magnitude cheaper per call
- Crash-safe logging: with the default never-flush policy up to a full page buffer (4 MB on Win64) is lost if the process dies
- Code that already depends on spdlog's API, sinks, registry or pattern flags

## How it is fast

The file targets format straight into a std::vector&lt;char&gt; owned by the target and only issue a raw _write/write call when that buffer reaches pageSize (4 MB on Win64, 2 MB on Win32, 64 KB elsewhere), so syscalls are rare compared with spdlog's FILE\*-based basic_file_sink. The pattern is pre-compiled once into a format string, the time breakdown is cached and refreshed only when the second changes, and the level check is a plain enum compare before any work.

## Compared with alternatives

Rarely: lwlog and fmtlog also beat spdlog with maintained code and published harnesses, and Quill, XTR or PlatformLab NanoLog are far cheaper on the hot path via async back ends. Choose Serenity only as a small synchronous single-threaded Windows file logger to study or vendor.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none by default (bundled ArgFormatter); optional fmtlib or MSVC &lt;format&gt;; CMake with CPM for benchmarks |
| **Minimum toolchain** | C++20; MSVC is the only toolchain exercised by CI (msvc.yml); &lt;format&gt; backend needs MSVC |
| **Platforms** | Windows (MSVC); Linux/macOS code paths present but the non-Windows file I/O macros do not match the call sites |
| **Thread safety** | Opt-in per target via EnableMultiThreadingSupport (mutex around format and write); off by default |
| **Drop-in for the baseline** | no |

## Gotchas

- The console benchmark rows measure nothing but the disabled-level check: both Serenity and spdlog console loggers were set to level off, so 5.656 ns vs 10.837 ns is a branch, not output
- The current bench/src/Benchmark.cpp runs 2,000,000 iterations and passes a std::string_view (its comment says string_view is faster than the C string), whereas the README table says 1,000,000 iterations of a C-style string, so the published numbers predate the checked-in harness
- The file speedup largely compares buffer sizes: Serenity holds up to 4 MB (Win64) in a vector before one _write, versus spdlog's stdio-buffered fwrite; front-erasing the vector after each page write is a memmove
- FileHelper::CloseImpl tests close() != 1, so close errors are never reported

## Known shortcomings

- Harness flaw: the console rows (5.656 vs 10.837 ns) time only the disabled-level check, with both loggers set to level off. The README table (1M iterations, C string) predates the checked-in Benchmark.cpp (2M iterations, string_view). The file win is mostly a 4 MB vector buffer (Win64) against spdlog's stdio fwrite. Effectively Windows and MSVC only: FileHelper.cpp defines Write for non-Windows but calls WRITE, uses _O_BINARY and the MSVC-internal path::_Remove_filename_and_separator; CloseImpl checks close() != 1, so errors are never reported.

## Caveats and trade-offs

Numbers dated 05Jul22; compiler, flags and CPU not stated; single thread only; author calls the test 'very crude' and the project a learning project; console figures had output disabled; spdlog version not stated; last commit 2023-03-25.

C++20; built-in formatter or std::format (MSVC) or fmtlib; alpha, README calls it a learning project.

## Maintenance

Abandoned alpha (last commit 2023-03-25, 3 stars) under MIT; copyable in principle but effectively Windows/MSVC-only and not production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Statistics section gives first-party per-message timings against spdlog sinks with no compiler, flags, CPU or published benchmark harness details, so C.
- **Verifier notes:** Record mapped the README percentages to the wrong targets (console is the \~40-42% one, file \~79-81%); fixed. License is MIT (repo page; file is named License, so /LICENSE 404s). Last commit 2023-03-25 is over 3 years ago: abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/USAFrenzy/Serenity_Logger>
  - <https://github.com/USAFrenzy/Serenity_Logger#statistics>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/HEAD/README.md>
  - <https://github.com/USAFrenzy/Serenity_Logger/commits>
- **Sources the enricher read:**
  - <https://github.com/USAFrenzy/Serenity_Logger>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/HEAD/README.md>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/bench>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/bench/src>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/bench/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/CMakeLists.txt>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/Serenity>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/Serenity/src>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/Serenity/include/serenity>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/include/serenity/Targets/Target-impl.h>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/Targets/Target.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/Targets/FileTarget.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/Targets/RotatingTarget.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/Utilities/FileHelper.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/include/serenity/Utilities/FileHelper.h>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/Utilities/TargetHelper.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/src/MessageDetails/Message_Formatter.cpp>
  - <https://raw.githubusercontent.com/USAFrenzy/Serenity_Logger/v1.0.0-Alpha/Serenity/include/serenity/Defines.h>
  - <https://github.com/USAFrenzy/Serenity_Logger/tree/v1.0.0-Alpha/.github/workflows>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/usafrenzy/serenity_logger`) · [data/wave11/enrich/raw/github_com_usafrenzy_serenity_logger.json](../../../data/wave11/enrich/raw/github_com_usafrenzy_serenity_logger.json) (enrichment confidence 0.75)

</details>
