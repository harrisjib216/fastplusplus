# Palanteer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `MIT (instrumentation libraries); AGPL-3.0-or-later (viewer and scripting module)` · 🟡 stale

> Single-header C++11 tracing/logging instrumentation plus viewer; enqueues a log in \~19 ns versus 1250 ns measured for spdlog.

| | |
|---|---|
| **Beats** | spdlog (logging) and NanoLog; profiler instrumentation cost |
| **Claimed result** | Docs table (1M-iteration loop logging one parameter, queue write only, AMD Ryzen 7 5700U): runtime cost per log is Palanteer 19.2 ns, NanoLog 10.7 ns, spdlog 1250 ns (the author says spdlog's own figures could not be reproduced). That is about 65x faster than spdlog and 1.8x slower than NanoLog (derived from page data); the README rounds this to \~50x. Compilation: 2800 logs/s versus 470 (spdlog, about 6x) and 265 (NanoLog, about 10.6x). The self-test on a Core i7-7600U (gcc, Linux) reports 6.1 ns per event trace; the README says \~25 ns per event and up to \~5M events/s recording. |
| **Workload** | Runtime cost and compile time of a logging call in the instrumentation library. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 5700U (logger comparison); Intel Core i7-7600U (self-test suite) |
| **Compiler and flags** | gcc on Debian 10 for the self-tests (-O2 noted for code size and compile speed); flags for the logger comparison are not stated |
| **Adoption** | 2.2k stars |
| **Last commit** | 2025-05-12 |
| **Links** | [repository](https://github.com/dfeneyrou/palanteer) · [benchmark](https://github.com/dfeneyrou/palanteer/blob/main/docs/index.html) |

## Verdict

First-party docs table on an AMD Ryzen 7 5700U: 1M-iteration loop logging one integer parameter, queue write only, gives Palanteer 19.2 ns, NanoLog 10.7 ns and spdlog 1250 ns per log (about 65x versus spdlog and 1.8x slower than NanoLog, derived from page data), plus compile speed of 2800 vs 470 (spdlog) and 265 (NanoLog) logs/s; the comparison harness and flags are not public. Separate self-tests on a Core i7-7600U report 6.1 ns (gcc, Debian 10) and 4.3 ns (MSVC 2019) per traced event, and the connected testprogram reports \~19-21 ns per event with \~4.7-4.9M events/s server processing.

## Use it when

- Debug/performance observation of C++11+ programs on Linux or Windows where you want timeline, flame graph, plots and logs from one instrumentation pass.
- Hot-path logging where you can accept binary logs read through a viewer; enqueue cost is tens of ns, not microseconds.
- Test automation that drives a program through Python scripts (CLI calls, freeze points, event collection).
- Builds that need instrumentation compiled out per group or static strings stripped (external string mode) for shipping binaries.

## Skip it when

- Production logging that needs human-readable files, rotation or multiple sinks: only one binary file, and the author says this rules out permanent logging.
- macOS or Windows on ARM64: OS support is Linux and Windows 10; issue #49 reports Windows ARM64 failing to build on __rdtsc.
- Heavy use of dynamic (runtime) names: issue #47 reports plBeginDyn/plEndDyn are very slow because of the string pool, and pool exhaustion busy-waits.
- Burst rates above the collection buffer (default \~5 MB, \~100K events per \~5 ms period): instrumented threads busy-wait and a SATURATION log is emitted.
- Shipping the viewer or Python scripting module in proprietary tools: they are AGPL-3.0-or-later; project is beta and stale since May 2025, with protocol and record formats not stable across versions.

## How it is fast

Static strings (file names, event names, log formats) are hashed at compile time and sent once, so a log call writes only hashes, an RDTSC timestamp and raw arguments; formatting is deferred to the viewer side. Events go into a preallocated double-banked global buffer claimed with a single atomic fetch_add on a cache-line-aligned bank/index word, and a collection thread swaps banks and ships them (zstd-compressed records). Instrumentation groups compile out to zero instructions when disabled.

## Compared with alternatives

Pick Tracy (2.25 ns per zone, actively developed, wider platform support) for general frame/zone profiling; pick Palanteer when you also want low-cost printf-style logs with graphable arguments and Python-scripted remote control and testing of the program in the same tool. funtrace is the choice for automatic function-level tracing with lower per-call cost.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the C++ instrumentation (optional libunwind and libdw on Linux for stack trace dumps); viewer needs OpenGL 3.3+ and bundles Dear ImGui, stb, zstd; Python modules need CPython 3.7+ |
| **Minimum toolchain** | C++11 for the instrumentation header; C++14 for viewer and scripting module |
| **Platforms** | Linux 32/64-bit (tested x64 and armv7l) and Windows 10; RDTSC on x86-64, std::chrono steady_clock fallback elsewhere; viewer Linux 64-bit and Windows 10 only |
| **Thread safety** | Instrumentation calls are multithread-safe (shared buffer claimed by atomic fetch_add); threads busy-wait when the buffer or dynamic-string pool is exhausted |
| **Drop-in for the baseline** | partial — printf-style plLog API replaces spdlog/NanoLog call sites, but output is binary records for the viewer, not formatted text sinks |

## Gotchas

- The 19.2 ns vs 1250 ns spdlog comparison times only the write into each logger's internal queue (no formatting or output); only Palanteer's test program is published, and the author notes spdlog's own published figures could not be reproduced, so the \~50-65x margin is unverified. NanoLog was faster (10.7 ns) and produced smaller files (7 MB vs 18 MB).
- All threads share one atomic bank/index counter, so per-event cost under many concurrently logging threads is not documented; the 6.1 ns self-test figure is called 'very optimistic' by the author (small loop).
- Exceeding compile-time resource limits (CLI count, request buffer) triggers assertion failures rather than graceful degradation.
- Servers and instrumentation library versions must match; older records may become unreadable after upgrades.

## Known shortcomings

- The comparison times only the queue write; the spdlog and NanoLog harness is unpublished. Open issues: 47 (dynamic strings are slow) and 49 (Windows ARM64 build fails on __rdtsc). The viewer is AGPL.

## Caveats and trade-offs

First-party comparison. Only Palanteer's test program is public; the spdlog and NanoLog harness is not. It measures only the enqueue into the internal queue (no formatting or output). The spdlog figure is far from spdlog's own published numbers, as the author notes. The baseline is a logger, so the record fits the profilers category only in part. The viewer and Python module are AGPL-3.0-or-later; the instrumentation libraries are MIT.

Beta state; evolving protocol and storage formats; viewer is AGPL.

## Maintenance

Stale (last commit 2025-05-12, beta, 2.2k stars, open build and performance issues); the MIT single header is easy to vendor, but the viewer and scripting tools are AGPL-3.0-or-later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** In docs/index.html (the source of the github.io page) a first-party table gives the runtime cost per log as Palanteer 19.2 ns, NanoLog 10.7 ns and spdlog 1250 ns, and compilation speed as 2800, 265 and 470 logs/s, all on an AMD Ryzen 7 5700U. The spdlog and NanoLog harness is not published and flags are not stated, so C.
- **Verifier notes:** The README's \~50x and 6x match the docs table, whose exact figures give \~65x. The github.io docs are blocked, so I read the same file from the repo's docs/ folder via raw.githubusercontent.com. Last commit 2025-05-12, so stale is correct.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/HEAD/README.md>
  - <https://github.com/dfeneyrou/palanteer/tree/main/docs>
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/main/docs/index.html>
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/main/docs/more.md.html>
  - <https://github.com/dfeneyrou/palanteer/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/HEAD/README.md>
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/main/docs/index.html>
  - <https://raw.githubusercontent.com/dfeneyrou/palanteer/HEAD/c++/palanteer.h>
  - <https://github.com/dfeneyrou/palanteer/issues>
  - <https://github.com/dfeneyrou/palanteer/issues/47>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dfeneyrou/palanteer`) · [data/wave11/enrich/raw/github_com_dfeneyrou_palanteer.json](../../../data/wave11/enrich/raw/github_com_dfeneyrou_palanteer.json) (enrichment confidence 0.7)

</details>
