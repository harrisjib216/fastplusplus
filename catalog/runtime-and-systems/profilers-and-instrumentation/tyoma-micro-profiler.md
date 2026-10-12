# MicroProfiler (micro-profiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Low-overhead real-time instrumenting C/C++ profiler; README chart shows 6-7x less slowdown than AQtime and the VS instrumenting profiler.

| | |
|---|---|
| **Beats** | AQtime Performance Profiler and Visual Studio Instrumenting Profiler (instrumenting profilers) |
| **Claimed result** | README chart '7-Zip Compression Performance': unprofiled 3,140 KB/s; MicroProfiler 840 KB/s; AQtime 135 KB/s; Visual Studio Instrumenting Profiler 116 KB/s. That makes the profiled 7-Zip about 6.2x faster than under AQtime and 7.2x faster than under the VS instrumenting profiler, but 3.7x slower than unprofiled (derived from page data). A second chart, 'Relative Profilers Performance', shows the same ratio normalized to 1. Changelog: up to 35% (x86) and 42% (x64) less overhead than its own earlier version. |
| **Workload** | 7-Zip compression throughput while instrumented by each profiler, shown as a bar chart in the README. |
| **Metric** | other |
| **Compiler and flags** | /GH /Gh (MSVC) or -finstrument-functions (Linux) |
| **Adoption** | 264 stars |
| **Last commit** | 2026-03-16 |
| **Links** | [repository](https://github.com/tyoma/micro-profiler) · [benchmark](https://github.com/tyoma/micro-profiler/blob/master/README.md) |

## Verdict

A first-party README chart shows 7-Zip compressing at 3,140 KB/s unprofiled, 840 KB/s under MicroProfiler, 135 KB/s under AQtime and 116 KB/s under the Visual Studio instrumenting profiler (about 6.2x and 7.2x faster than those profilers, 3.7x slower than unprofiled, derived from page data); 7-Zip version, input, compiler flags and CPU are not documented.

## Use it when

- Windows/MSVC C++ applications that must stay interactive while profiled (GUI, games, servers) where AQtime or the VS instrumenting profiler make them unusable
- You want exact call counts and per-function inclusive/exclusive times live, without recording and post-processing large trace files
- Profiling a selected subset of translation units: add /GH /Gh (or -finstrument-functions) only to the .cpp files of interest
- Remote profiling of a Linux or Windows process from a frontend on another machine over sockets
- Legacy targets: the README says it runs on Windows XP and supports Visual Studio 2005 onward

## Skip it when

- Overall overhead still matters: on the README's 7-Zip chart throughput drops from 3,140 KB/s to 840 KB/s (about 3.7x slower, derived from page data); sampling profilers (perf, VTune, Tracy sampling) cost far less on call-heavy code
- Code dominated by tiny non-inlined functions, where hook cost dominates and times can come out distorted or negative (open issue #57; issue #64 opened to discuss instrumentation distortion)
- Builds you cannot recompile; the 'Profile Process...' attach mode needs /hotpatch and /functionpadmin or -fpatchable-function-entry builds and was labelled very beta
- Teams on recent Visual Studio 2022: open issues report freezes on attach (#86), non-working context menu (#83), build failure on VS 2022 17.4 LTSC (#85) and a deadlock at start (#87)
- You need a timeline/trace view of individual events; it aggregates statistics (flat list plus callstack view since v2.0.651) rather than recording a frame timeline like Tracy

## How it is fast

The enter/exit hooks (_penter/_pexit or __cyg_profile_func_enter/exit, hand-written assembler on MSVC x86/x64) only append a (timestamp, callee) record into a per-thread buffer; a per-thread shadow return stack handles nesting and tail calls. Full buffers are handed through a lock-free circular queue to a separate analyzer thread that aggregates statistics, so the profiled thread never builds call trees itself (the v1.7 queue rewrite cut atomic bus-locking about 250x and overhead by up to 35% x86 / 42% x64). A start-up calibration times instrumented vs plain empty calls and subtracts the measured per-call overhead from reported times.

## Compared with alternatives

Pick it over Tracy when you want automatic per-function statistics for every function in chosen files without adding zone macros, and over funtrace when you need live aggregated statistics in a Visual Studio pane on Windows rather than a trace file; pick funtrace or Tracy when per-call cost (under 10 ns or 2.25 ns per zone documented there) or timelines matter more.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none at runtime (collector DLL/.so plus debug symbols); building from source needs MSVC 2010+ and the Visual Studio SDK on Windows, CMake/conan files are present for other builds |
| **Minimum toolchain** | MSVC 2010+ (/GH /Gh); GCC or Clang with -finstrument-functions on Linux; VS integration for Visual Studio 2005-2022 |
| **Platforms** | Windows x86 and x64 (XP and later), Linux collector; frontend also builds on macOS |
| **Thread safety** | Multithreaded targets supported: per-thread trace buffers, per-thread statistics and thread filter in the UI |
| **Drop-in for the baseline** | partial - same workflow as other compiler-hook instrumenting profilers (recompile with /GH /Gh), but its own collector library and frontend replace AQtime or the VS profiler UI |

## Gotchas

- When the analyzer thread falls behind and no empty trace buffer is free, buffers_queue::flush() blocks the profiled thread until one is returned, so overhead can spike under heavy call rates
- On Linux some binaries do not bind the hook functions; the README says to run with LD_PRELOAD=&lt;profiler .so&gt; and to set LD_LIBRARY_PATH to the collector directory
- calls_collector.cpp must be compiled without SSE/SSE2 code generation (comment in the source) if you build it yourself
- Windows services or other-user processes need the MICROPROFILERFRONTEND="sockets|127.0.0.1:6100" environment variable and the profiler directory on the system PATH

## Known shortcomings

- The README chart has no methodology and the profiler is still 3.7x slower than an unprofiled run (derived). Open VS2022 freeze and deadlock issues (83, 85, 86, 87) and negative times (57); buffers_queue::flush blocks the profiled thread when the analyzer lags.

## Caveats and trade-offs

First-party chart with no methodology (no 7-Zip version, input, CPU, compiler or flags). It compares against AQtime and the VS instrumenting profiler, not against gprof, Valgrind or VTune. Instrumentation still costs about 3.7x throughput on this workload. Results are Windows-era; Linux support (-finstrument-functions) came later.

Instrumentation (compiler hook) profiler, needs recompilation; Visual Studio integration; Windows and Linux.

## Maintenance

Active (last commit 2026-03-16, latest release v2.0.651) and MIT-licensed, but 18 open issues include several Visual Studio 2022 freezes and integration failures.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README embeds a first-party chart 'profiled-7-zip-performance.png': 7-Zip compression at 3,140 KB/s unprofiled, 840 KB/s under MicroProfiler, 135 KB/s under AQtime and 116 KB/s under the Visual Studio instrumenting profiler. No benchmark code, compiler, flags or CPU are given, so C.
- **Verifier notes:** The record named gprof/Valgrind/VTune as the baseline, but the chart shows AQtime and the VS instrumenting profiler; corrected. Is baseline_in_list still true? The orchestrator should check whether these profilers are listed incumbents. Metadata matches: MIT, 264 stars, last commit 2026-03-16.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party chart
- **Pages the verifier opened:**
  - <https://github.com/tyoma/micro-profiler>
  - <https://github.com/tyoma/micro-profiler/commits/master>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/master/content/profiled-7-zip-performance.png>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/master/content/relative-profilers-performance.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/README.md>
  - <https://github.com/tyoma/micro-profiler>
  - <https://github.com/tyoma/micro-profiler/issues>
  - <https://github.com/tyoma/micro-profiler/issues/64>
  - <https://github.com/tyoma/micro-profiler/tree/master/collector/src>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/collector/src/calls_collector.cpp>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/collector/src/calls_collector_thread.cpp>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/collector/src/calibration.cpp>
  - <https://raw.githubusercontent.com/tyoma/micro-profiler/HEAD/collector/buffers_queue.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tyoma/micro-profiler`) · [data/wave11/enrich/raw/github_com_tyoma_micro_profiler.json](../../../data/wave11/enrich/raw/github_com_tyoma_micro_profiler.json) (enrichment confidence 0.7)

</details>
