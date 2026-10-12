# lwlog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++17 policy-based logger with allocation-free log calls and an SPSC/MPSC ring-buffer async mode; README claims 2.5-20x over spdlog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Sync: 12268.1 vs 1651.5 ops/s at 8 msgs (7.4x), 2.5x at 8192; sync buffered (lwlog) vs spdlog sync 319x at 8 msgs, 237x at 8192; async blocking 16.3x at 8 msgs and 539.9x at 4096 (spdlog row 565498 ns/op); async nonblocking 20.7x at 8 msgs falling to 2.4x at 8192. |
| **Workload** | picobench of synchronous, buffered, and asynchronous loggers over 8 to 8192 messages. |
| **Metric** | latency |
| **Adoption** | 353 stars |
| **Last commit** | 2025-12-25 |
| **Links** | [repository](https://github.com/ChristianPanov/lwlog) · [benchmark](https://github.com/ChristianPanov/lwlog#benchmarks) |

## Verdict

First-party picobench tables in the README compare lwlog with spdlog in four modes over 8 to 8192 messages: sync 7.4x at 8 messages falling to 2.5x at 8192; async blocking 16x at 8 messages and 540x at 4096, where spdlog's row jumps to 565 us/op, which suggests queue saturation rather than steady state; async nonblocking 20.7x falling to 2.4x. The 237-319x 'buffered' table pits buffered lwlog against unbuffered spdlog. No compiler, flags, CPU or benchmark source is published.

## Use it when

- Single-producer async logging to console or file where call-site latency matters and messages fit the static buffer limits
- Embedded or real-time code that must avoid heap allocation in the logging path
- Projects that already pick sinks and policies at compile time and want spdlog-like {} formatting without the fmt dependency
- Buffered sync logging to a stream where losing unflushed lines on crash is acceptable

## Skip it when

- Messages or arguments longer than the configured limits (128-byte message, 64-byte argument, 4 arguments by default); the limits are fixed at compile time
- Many producer threads: the MPSC queue is a spinlock around a ring buffer, not a lock-free multi-producer queue, and no multi-thread benchmark is published
- When you need reproducible evidence: the picobench harness used for the README tables is not in the repository (Sandbox/ holds only a timer demo), and no compiler, flags or CPU are given
- Drop-in replacement for spdlog call sites or for nanosecond-class loggers such as Quill, fmtlog or NanoLog
- Package-manager consumers: no Conan or vcpkg package (open issue #39)

## How it is fast

Log calls format into fixed-size pre-allocated buffers whose sizes are template parameters (pattern 256, message 128, argument 64, 4 args by default), so no heap allocation per call. The pattern is parsed once when set and compiled into a list of formatters, so the call site only substitutes values. Async mode is a bounded ring buffer (default 1024 slots) with cache-line-aligned read/write indices; SPSC uses plain atomics, the thread-safe variant takes an atomic_flag spinlock on enqueue (MPSC), and the worker thread spins with an adaptive waiter. Producers enqueue only the format-string pointer, source metadata and argument strings converted to chars; formatting happens on the worker.

## Compared with alternatives

Pick lwlog over Quill, fmtlog or NanoLog when you want a small, readable, allocation-free codebase with spdlog-like patterns and compile-time policies, and can live without their published, reproducible nanosecond-level latency numbers. For multi-threaded hot paths, Quill or fmtlog have better evidence.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (Threads only) |
| **Minimum toolchain** | C++17, CMake 3.16 |
| **Platforms** | Windows x64 (MSVC, MinGW, Clang), Linux x64 (GCC, Clang, Intel icx) and arm64 (GCC, Clang), macOS x64 (Apple Clang), per README CI table |
| **Thread safety** | Per policy: single_threaded_policy (default aliases) is not thread-safe; multi_threaded_policy and _mt aliases lock sinks with a mutex; async thread-safe mode uses a spinlock-guarded MPSC ring buffer |
| **Drop-in for the baseline** | no |

## Gotchas

- Async mode queues the raw const char\* format string, not a copy, so a format string built at runtime (for example std::string::c_str()) must outlive the worker thread processing it
- Default flush policy is immediate_flush_policy (fflush after every log); the large README sync speedups come from buffered_flush_policy (4 MiB stream buffer) and lose unflushed lines on a crash
- overwrite_last_overflow_policy advances the read index from the producer while the worker may be extracting the same slot; from code reading this looks racy, so prefer block or discard_new
- The default overflow policy busy-waits with CPU pause when the 1024-slot queue is full, and the worker spins via an adaptive waiter, so expect a burning core under load

## Known shortcomings

- The picobench harness is missing from the repo (Sandbox has only a timer demo); the big sync ratios come from buffered_flush_policy (4 MiB) against the default fflush per call. The async queue keeps a raw const char\* format pointer, so runtime strings can dangle, and the overwrite_last policy looks racy from code reading.

## Caveats and trade-offs

No compiler, flags or hardware stated; the 539x row is async blocking at 4096 msgs, where spdlog's queue appears to saturate; buffered lwlog is compared against unbuffered spdlog, so the 237-319x ratios compare different buffering semantics; sync ns/op values (81-112 us per message) suggest a flushing sink; not independently reproduced.

C++17, compile-time sink config, static buffer for formatting (no allocation per call).

## Maintenance

Active (last commit 2025-12-25, v1.3.0 in CMakeLists, 353 stars), MIT-licensed, five open issues and none of them bugs; small enough to vendor, but its performance claims are unreproducible first-party numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks section has first-party picobench tables of lwlog vs spdlog for sync, sync-buffered, async blocking and async nonblocking modes; no compiler, flags or CPU are stated, so C.
- **Verifier notes:** Numbers match the README. The 539x figure belongs to the async blocking table, not async nonblocking as the record said. Last commit 2025-12-25 is under 12 months old, so active rather than stale.
- **Fields the verifier corrected:** `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/ChristianPanov/lwlog>
  - <https://github.com/ChristianPanov/lwlog#benchmarks>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/LICENSE>
  - <https://github.com/ChristianPanov/lwlog/commits>
- **Sources the enricher read:**
  - <https://github.com/ChristianPanov/lwlog>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/README.md>
  - <https://github.com/ChristianPanov/lwlog/issues>
  - <https://github.com/ChristianPanov/lwlog/tree/master/Sandbox>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/Sandbox/Benchmark.h>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/Sandbox/Sandbox.cpp>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/CMakeLists.txt>
  - <https://github.com/ChristianPanov/lwlog/tree/master/lwlog/include>
  - <https://github.com/ChristianPanov/lwlog/tree/master/lwlog/include/details>
  - <https://github.com/ChristianPanov/lwlog/tree/master/lwlog/include/policy>
  - <https://github.com/ChristianPanov/lwlog/tree/master/lwlog/include/details/bounded_queue>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/lwlog/include/logger_impl.h>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/lwlog/include/policy/log_policy_impl.h>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/lwlog/include/policy/concurrency_policy.h>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/lwlog/include/policy/flush_policy.h>
  - <https://raw.githubusercontent.com/ChristianPanov/lwlog/HEAD/lwlog/include/details/bounded_queue/bounded_queue_impl.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/christianpanov/lwlog`) · [data/wave11/enrich/raw/github_com_christianpanov_lwlog.json](../../../data/wave11/enrich/raw/github_com_christianpanov_lwlog.json) (enrichment confidence 0.7)

</details>
