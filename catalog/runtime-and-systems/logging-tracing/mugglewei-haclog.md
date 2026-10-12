# haclog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Plain C async printf-style logger; producer-side calls about 3.5x faster than spdlog when buffers are not full.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Scenario 2 (iterations x repeats), 1 thread median 148 ns vs spdlog async 518 ns (3.5x) and spdlog sync 587 ns (4.0x) (derived from page data); 12 threads median 29.8 ns vs spdlog async 1802 ns and sync 1266 ns (google-benchmark Time averaged over threads) |
| **Workload** | Google Benchmark, 2000 iterations x 5 repeats, write of a struct (u64,u32,i64,i32 and 128-char string) with full pattern, 1 and more threads. |
| **Metric** | latency |
| **Hardware** | Intel i7-10710U, frequency fixed to 3.2 GHz, Arch Linux |
| **Compiler and flags** | GCC 14.2.1 20240910; build.sh configures CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG) with -Wall -Wextra; BUILD_SHARED_LIBS=ON |
| **Adoption** | 82 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/MuggleWei/haclog) · [benchmark](https://github.com/MuggleWei/cc_log_benchmark) |

## Verdict

In the author's public cc_log_benchmark (Google Benchmark, 2000 iterations x 5 repetitions, struct of four integers plus a 128-char string with full metadata pattern, file output, 4 MiB per-thread buffer, GCC 14.2.1 Release, i7-10710U fixed at 3.2 GHz), haclog v0.4.0 measured 148 ns median per call at 1 thread vs spdlog v1.12.0 async 518 ns and sync 587 ns. That run never fills the buffer; in the same report's sustained min-time scenario haclog is 2-3x slower than spdlog at 1, 2 and 8 threads and only ahead at 4 threads (1495 vs 1752 ns async).

## Use it when

- C or mixed C/C++ code bases that want an async logger without a C++ dependency
- Bursty logging where the per-thread buffer rarely fills, so the producer only pays the enqueue cost (about 148 ns per call in the author's run, vs 518 ns for spdlog async)
- Latency-sensitive threads that must not lose log lines: a full buffer blocks the producer instead of dropping
- Applications needing printf-style formatting with plain-text output readable by tail (unlike PlatformLab NanoLog's binary log)

## Skip it when

- Sustained high-rate logging: in the same benchmark's min-time scenario (buffers full) haclog takes 1590 ns per call at 1 thread vs spdlog async 606 ns and spdlog sync 556 ns, and 2684 ns vs 1872 and 1235 ns at 8 threads (derived from page data), so it is slower than spdlog once the buffer fills
- When you want the fastest async logger available: in the same shootout NanoLog (60 ns at 1 thread in scenario 2, 161 ns in scenario 1) and Quill bounded dropping (52 ns in scenario 1) beat it
- Code that builds format strings at run time: the format must be a string literal, enforced only in C++ builds
- Many short-lived threads: each thread allocates its own ring buffer (1 MiB minimum, 4 MiB in the benchmark) and cleanup polls in 1 ms sleeps until the backend drains it
- Programs that need a clean shutdown of the logger: the backend thread is detached and loops forever with no stop API

## How it is fast

Each producer thread owns a single-producer/single-consumer byte ring buffer (default 1 MiB, minimum 1 MiB) and writes only a header, the raw binary arguments and copies of %s strings into it; formatting is deferred to the backend thread. The format string is parsed once per call site into a cached 'printf primitive' (static pointer guarded by a spinlock on first use), so the hot path is a timestamp, a switch over the precomputed argument types and memcpy. The backend thread polls every thread's buffer, formats with its own vsprintf reimplementation, and sleeps 100 ns when idle.

## Compared with alternatives

Pick haclog over fmtlog, Quill or BinLog when the project must stay plain C or wants printf-style calls without a C++ toolchain dependency; if C++ is fine, the same author's benchmark shows NanoLog, Quill and fmtlog as fast or faster, especially under sustained load.

## Integration

| | |
|---|---|
| **Form** | shared lib (default BUILD_SHARED_LIBS=ON) or static lib; CMake and Meson builds |
| **Dependencies** | none (Google Benchmark and a test library are downloaded only when benchmarks or tests are enabled) |
| **Minimum toolchain** | C11 (CMake sets C and C++ standard 11); CMake 3.18.6+ or Meson |
| **Platforms** | Linux, Windows (MSVC), macOS, Android per CI badges; x86-64 benchmarked only |
| **Thread safety** | Logging from many threads is supported via per-thread SPSC buffers; each thread must init/clean up its context (auto-init on first log is on by default). Adding handlers is not synchronized and should happen before haclog_backend_run(). |
| **Drop-in for the baseline** | no |

## Gotchas

- A message larger than half the per-thread buffer minus 128 bytes fails haclog_bytes_buffer_w_fc and the serializer calls haclog_debug_break() and returns, so the line is dropped (and a debug build traps).
- Memory ordering is thin: the reader publishes its position with a relaxed store and producers read it relaxed, and the per-call-site primitive pointer uses double-checked locking on a plain (non-atomic) static; fine on x86's strong ordering, but formally a data race and worth auditing before use on ARM.
- With more than 128 %s arguments in one message the serializer substitutes '(haclog str cache full)' without consuming the va_arg, which shifts the remaining arguments.
- The README's hello sample calls haclog_thread_context_init() a second time where it means haclog_thread_context_cleanup(); the benchmark used tag v0.4.0 while the repo is at 0.4.5.

## Known shortcomings

- The scenario 2 claim holds (148 vs 518 ns, buffer never fills), but in scenario 1 of the same report (buffer full) haclog is slower than spdlog: 1 thread 1590 ns against 606 (async) and 556 (sync); 8 threads 2684 against 1872 and 1235; ahead only at 4 threads (1495 vs 1752). The benchmark ran v0.4.0 (repo now 0.4.5); NanoLog (60 ns) and Quill (52 ns) beat it. Gotchas not behind the numbers: relaxed reader-position store and a non-atomic double-checked-lock pointer (risky on ARM; the x86 run is unaffected), more than 128 %s arguments shift va_args, an oversized message is dropped via haclog_debug_break.

## Caveats and trade-offs

Benchmark repo is by haclog's author (first-party run, but code and setup are public); haclog's 1-thread run has cv 49% (first two repeats 375 and 257 ns, mean 212 ns). The author's own analysis says haclog is fast only in the non-stress scenario 2: in scenario 1 (min-time, buffer full) it blocks and its efficiency drops significantly. Multi-thread Time is the benchmark's per-thread-averaged figure, not per-call latency. Same shootout ranks fmtlog, NanoLog and quill as fast or faster.

Plain C API, async, blocking when ring buffer full; efficiency drops under overload.

## Maintenance

Active (last commit 2026-09-08, version 0.4.5, 82 stars, no open issues), MIT-licensed, small (about 30 source files) and easy to vendor, but a one-author project with first-party benchmarks only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: benchmark code is public (MuggleWei/cc_log_benchmark, Google Benchmark fixtures, build.sh sets CMAKE_BUILD_TYPE=Release so CMake's default -O3 -DNDEBUG plus -Wall -Wextra from CMakeLists.txt), compiler GCC 14.2.1 20240910 and CPU Intel i7-10710U fixed at 3.2 GHz are stated. report/benchmark_20250221/benchmark/benchmark_haclog.txt shows 1-thread median 148 ns; benchmark_spdlog_async.txt 518 ns and benchmark_spdlog_sync.txt 587 ns.
- **Verifier notes:** Numbers match the report files exactly. Upgrade rests on build.sh Release build type standing in for explicit flags (lzbench precedent of public build files); downgrade to C if the orchestrator wants explicit -O flags printed.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/README.md>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/README.md>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/report/benchmark_20250221/benchmark>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_haclog.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_spdlog_async.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_spdlog_sync.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/build.sh>
  - <https://github.com/MuggleWei/haclog>
  - <https://github.com/MuggleWei/haclog/commits>
- **Sources the enricher read:**
  - <https://github.com/MuggleWei/haclog>
  - <https://github.com/MuggleWei/haclog/tree/master/haclog>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/README.md>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/version.txt>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog.h>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_macro.h>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_bytes_buffer.h>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_bytes_buffer.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_context.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_thread_context.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_log.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_log.h>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_spinlock.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_sleep.c>
  - <https://raw.githubusercontent.com/MuggleWei/haclog/HEAD/haclog/haclog_vsprintf.c>
  - <https://github.com/MuggleWei/cc_log_benchmark>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/CMakeLists.txt>
  - <https://github.com/MuggleWei/cc_log_benchmark/tree/master/gbenchmark/c/haclog>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/c/haclog/gbenchmark_haclog.cpp>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/gbenchmark/log_gbenchmark.h>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_haclog.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_spdlog_async.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_spdlog_sync.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_nanolog.txt>
  - <https://raw.githubusercontent.com/MuggleWei/cc_log_benchmark/HEAD/report/benchmark_20250221/benchmark/benchmark_quill_bounded_dropping.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mugglewei/haclog`) · [data/wave11/enrich/raw/github_com_mugglewei_haclog.json](../../../data/wave11/enrich/raw/github_com_mugglewei_haclog.json) (enrichment confidence 0.75)

</details>
