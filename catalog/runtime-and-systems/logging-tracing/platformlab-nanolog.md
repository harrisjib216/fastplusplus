# NanoLog (PlatformLab)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `ISC` · 🟡 stale

> Binary, printf-style C++ logger from Stanford PlatformLab with about 7-14 ns call-site latency, 20-40x below spdlog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Quill harness: 1 thread 8/9/11 ns vs spdlog 271/296/360 ns (50th/90th/99.9th); 4 threads 14/14/21 vs spdlog 557/614/1106. Own README: staticString 7/37 ns (50th/99.9th) vs spdlog v1.1.0 214/2546, glog 1198/5968, Boost 1764/3772, Log4j2 174/3364. |
| **Workload** | Call-site latency with compile-time extraction of static log data, binary log output, formatting deferred offline; also throughput up to 16 threads. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-12600 @ 4.8 GHz, tuned system (isolcpus, nohz_full, mitigations=off), RHEL 9.4 |
| **Compiler and flags** | GCC 14.2, Release, -march=x86-64-v3 |
| **Adoption** | 3.4k stars; USENIX ATC'18 paper |
| **Last commit** | 2020-12-22 |
| **Links** | [repository](https://github.com/PlatformLab/NanoLog) · [benchmark](https://github.com/odygrd/quill#-performance) |

## Verdict

Quill v13.0.0 latency harness (odygrd/logger_benchmarks, GCC 14.2 Release -march=x86-64-v3, i5-12600 on a tuned RHEL 9.4 box) logs two ints and a double. PlatformLab NanoLog measured 8/9/11 ns (p50/p90/p99.9) on 1 thread vs spdlog 271/296/360, and 14/14/21 on 4 threads vs 557/614/1106. NanoLog's own README reports 7/37 ns vs spdlog v1.1.0 214/2546 for a static string, with no compiler or CPU listed.

## Use it when

- Latency-critical Linux x86-64 services (trading, storage, RPC servers) where a log call has to cost about 10 ns at p50 and stay near 11-21 ns at p99.9
- Very high log volume where small binary files and an offline decompress step are acceptable
- Codebases already using printf-style format strings that want the C++17 library mode with no build changes beyond linking -lNanoLog -lrt -pthread
- Multi-threaded producers: the Quill harness shows 4-thread p99.9 at 21 ns against 1106 ns for spdlog

## Skip it when

- You need readable text logs live (tail -f, stdout, log shippers): output is binary only, and stdout and uncompressed output are open feature requests (#51, #52)
- Windows, macOS or ARM64 targets: the README says Linux only, the timestamps use rdtsc, and ARM64 and Windows are open issues (#69, #67)
- You want fmt-style formatting, sinks, file rotation or multiple log files: none of these exist (rotation #63 and multiple files #62 are open requests)
- You need an actively maintained dependency: the last commit was December 2020, and issue #70 (2023) asks whether the project is dead
- CMake, vcpkg or Conan builds: it builds with GNU Make only, and a CMake request (#37) and package-manager request (#55) are open

## How it is fast

Static log information (format string, file, line, argument types) is pulled out at compile time, either by a Python preprocessor pass or by C++17 constexpr parsing of the format string. The hot path then copies only the dynamic arguments and an rdtsc timestamp into a lock-free per-thread staging buffer (1 MB by default). A background thread compresses and deduplicates those records and writes them out with POSIX AIO, and all formatting happens offline in the decompressor (USENIX ATC'18 paper).

## Compared with alternatives

Pick it over fmtlog, Quill or XTR when you want printf format strings and the smallest binary logs, and accept Linux-only, binary output and no maintenance; those three match or beat its latency (6-9 ns p50) in the same harness, are maintained and write text. Against MS BinLog it has lower tail latency (11 vs 119 ns p99.9 at 1 thread), but BinLog is maintained and has the published throughput number (61.79M msg/s), while NanoLog is absent from Quill's throughput table.

## Integration

| | |
|---|---|
| **Form** | static lib (libNanoLog.a plus decompressor); the Preprocessor mode instead generates per-build library code through a Python script and NanoLogMakeFrag |
| **Dependencies** | pthreads, POSIX AIO (librt); Python 3.4.2+ and GNU Make 4.0+ to build; googletest submodule for unit tests |
| **Minimum toolchain** | C++17, GNU g++ 7.5.0 or newer |
| **Platforms** | Linux only (x86-64 in practice: rdtsc timestamps; ARM64 is open issue #69) |
| **Thread safety** | Thread-safe: each thread logs into its own __thread StagingBuffer, which a single background thread drains; the producer blocks when its buffer is full |
| **Drop-in for the baseline** | no |

## Gotchas

- Compile with -Werror=format: the README warns that format errors may silently corrupt the log file at runtime. The %n specifier is rejected, and "%\*.d" is reported unsupported (#74)
- The Preprocessor mode builds a library that is non-portable even between compilations of the same application, so the decompressor must come from the same build as the binary that wrote the log
- A logging thread blocks (it does not drop records) when its 1 MB staging buffer fills. The log file is opened with O_DSYNC, so throughput depends on disk
- Open bug reports: 'Internal Error: Corrupted BufferExtend' (#64), and the nanosecond field in formatted timestamps can be negative or drift from system time (#28)

## Known shortcomings

- Not in Quill's throughput table. Format errors can silently corrupt the log (needs -Werror=format); open bugs 64 (corrupted BufferExtend) and 28 (negative ns timestamps). Linux only, rdtsc, no ARM64 (issue 69). Last commit 2020-12-22.

## Caveats and trade-offs

Own README compares against spdlog v1.1.0, glog v0.3.5 and Boost 1.55, which are old; the Quill harness uses current spdlog. Last commit Dec 2020, which is stale by the 1-3 year rule if counted from Oct 2026 (nearly 6 years, so closer to abandoned).

Binary log needs the decompressor to read; Linux only; needs a build-time preprocessor step; custom runtime and compile pipeline.

## Maintenance

Stale (last commit 2020-12-22, nearly 6 years, about 30 open issues with no replies, so effectively abandoned), but ISC-licensed and small enough to vendor and patch; last documented toolchain is g++ 7.5.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Quill README harness (public code at odygrd/logger_benchmarks, CMake Release, GCC 14.2, -march=x86-64-v3, i5-12600) shows PlatformLab NanoLog 8/11 ns vs spdlog 271/360 ns (50th/99.9th, 1 thread); own README table (staticString 7/37 vs spdlog 214/2546) lacks compiler and CPU, so on its own it would be C (USENIX ATC'18 paper not opened).
- **Verifier notes:** ISC license confirmed from LICENSE; 3.4k stars; last commit 2020-12-22 (&gt;3 years before today, so abandoned is arguably correct; left as recorded since author does not say). Binary log output needs offline decompressor, so not directly comparable with text loggers in throughput.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/README.md>
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/LICENSE>
  - <https://github.com/PlatformLab/NanoLog>
  - <https://github.com/PlatformLab/NanoLog/commits/master>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
  - <https://github.com/odygrd/logger_benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/README.md>
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/runtime/NanoLogCpp17.h>
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/runtime/RuntimeLogger.h>
  - <https://raw.githubusercontent.com/PlatformLab/NanoLog/HEAD/runtime/Config.h>
  - <https://github.com/PlatformLab/NanoLog/issues>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/platformlab/nanolog`) · [data/wave11/enrich/raw/github_com_platformlab_nanolog.json](../../../data/wave11/enrich/raw/github_com_platformlab_nanolog.json) (enrichment confidence 0.85)

</details>
