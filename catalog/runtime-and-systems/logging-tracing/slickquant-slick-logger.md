# slick-logger

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 async logger: lock-free ring, formatting deferred to a writer thread; 2-5x spdlog async on producer-side throughput.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | Small messages 1 thread 7,669,915 ops/s vs spdlog_async 3,765,386 and spdlog_sync 1,298,350; 8 threads 10,960,620 vs 1,925,261 and 490,994. Medium 1 thread 4,750,287 vs 899,182 and 575,968. |
| **Workload** | Operations per second for small messages (literal only) and medium messages (int, double, string), 1-8 threads, vs spdlog 1.12.0 async and sync. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900HX, 32 GB, Windows 11 Pro, local NVMe |
| **Compiler and flags** | MSVC 19.44, /O2 /DNDEBUG, C++20 |
| **Adoption** | 5 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/SlickQuant/slick-logger) · [benchmark](https://github.com/SlickQuant/slick-logger/blob/main/benchmarks/README.md) |

## Verdict

In the author's suite (benchmarks/benchmark_main.cpp; MSVC 19.44 /O2 C++20, Ryzen 9 5900HX, Windows 11, local NVMe; 50,000 messages x 3 runs), producer-side throughput for literal-only messages was 7.67M ops/s against spdlog 1.12.0 async 3.77M and sync 1.30M at 1 thread, and 10.96M against 1.93M and 0.49M at 8 threads; for three-argument messages it was 4.75M against 0.90M (async) at 1 thread. Both async loggers used 65,536-slot queues and were timed until the producers returned; the README table says spdlog_async used an 8,192-slot queue, but the code uses 65,536.

## Use it when

- Latency-sensitive threads (trading, game loops, real-time services) where a log call should cost about 100-350 ns on the producer and never wait on disk.
- Many producer threads logging at once: in the author's scaling harness total enqueue throughput kept rising up to 16 threads, while spdlog_async fell.
- Several processes on one host that should write to one log through a shared-memory collector.
- C++20 code bases that already use std::format and want spdlog-like patterns and sinks without depending on fmt.

## Skip it when

- When every log line must be kept: both rings are lossy and have no backpressure, so producers that outrun the writer overwrite older entries (a loss counter exists only with SLICK_LOGGER_ENABLE_LOSS_DETECTION).
- Toolchains without C++20 std::format (needs GCC 11+, Clang 14+ or MSVC 19.29+).
- Code that passes const char array members or locals as the format string: the literal-detection heuristic stores only a pointer, which can dangle before the writer reads it.
- Projects that need a mature, widely deployed logger: 5 stars, 2 forks, single-vendor project.
- Custom formatter types passed through a pre-built std::format_args: they are logged as &lt;handle&gt;.

## How it is fast

The calling thread only stamps the entry (timestamp, thread id, source location) and copies the arguments into a slot of a lock-free MPMC ring (slick-queue), claimed with one CAS on a shared counter. String-literal format strings are stored as pointers, and dynamic strings are copied into a separate string ring in 64-byte (cache-line) units so producers do not false-share. All std::format work and sink I/O happens later on the writer thread, which flushes once per drained batch rather than per line. Pattern rendering uses pre-parsed op lists and a per-second cached broken-down time.

## Compared with alternatives

Pick it over Quill or fmtlog when you want std::format with no fmt dependency, Windows and MSVC as first-class targets, and a built-in multi-process shared-memory collector. Quill, NanoLog and XTR have far wider use and independent latency tables (Quill's harness), so prefer them when maturity or guaranteed delivery (Quill's blocking queue option) matters more.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | slick-queue 2.1.0+ (fetched by CMake); no fmt |
| **Minimum toolchain** | C++20 with std::format: GCC 11+, Clang 14+, MSVC 19.29+; CMake 3.20+ |
| **Platforms** | Windows, Linux, macOS |
| **Thread safety** | Safe for concurrent LOG_\* calls from any thread; sinks are touched only by the single writer thread; set_instance() must be called before plugin threads log. |
| **Drop-in for the baseline** | partial: macros and pattern flags resemble spdlog, but it uses a global Logger singleton with its own sink classes instead of spdlog logger objects, and its queue drops entries where spdlog_async blocks by default. |

## Gotchas

- Lossy rings: messages are dropped silently on overrun unless loss detection is compiled in. The thread-scaling table (9.36M vs 114K ops/s at 16 threads) pushes 100,000 messages per thread through a 65,536-entry ring, so slick-logger can overwrite entries while spdlog_async (default block policy) waits for its writer. That row compares lossy enqueue with lossless delivery.
- Throughput figures stop the timer when producers return; the writer's drain and flush are outside the timed region for both async loggers. The main suite's 50,000 messages fit in a 65,536-slot queue, so it measures enqueue cost and not sustained throughput.
- Each header-only binary (exe, .dll/.so) gets its own Logger unless you share it with Logger::set_instance(), and the host must flush() before dlclose/FreeLibrary because queued entries point at the plugin's string literals.
- Raising a sink's min_level also drops entries that are already queued; on POSIX, shared-memory segments are never shm_unlink'ed, so cleanup is manual.

## Known shortcomings

- Harness flaw: the thread-scaling table (9.36M vs 114K ops/s at 16 threads) pushes 100,000 messages per thread through a 65,536-slot lossy ring (overwrites, no backpressure) against the spdlog_async blocking queue, so that row is lossy against lossless, not like for like. In the main suite 50k messages fit in the queue and both async loggers are timed only until the producers return, so it measures enqueue cost. The bench README says spdlog_async has 8192 slots while the code uses 65536.

## Caveats and trade-offs

First-party Windows/MSVC benchmark dated 2026-09-22; measures producer-side ops/s, not time to durable disk; spdlog 1.12.0 is not the latest; default 3 runs, so P95/P99 equal the max; Windows clock resolution is 100 ns, so per-call latency figures are coarse; author warns numbers describe one machine and that a run on network storage flatters this library. Also beats spdlog_sync on P99 latency (300 ns vs 32,800 ns) and spdlog_async on thread scaling (9.36M vs 114K ops/s at 16 threads). [retier] Main suite times enqueue cost only (50k messages fit in the queue); the thread-scaling row (9.36M vs 114K ops/s at 16 threads) compares a 65,536-slot lossy overwriting ring with spdlog's lossless blocking async queue and is not like for like; bench README says spdlog_async has 8192 slots, code uses 65536; 3 runs, 100 ns clock resolution.

C++20 with std::format; header-only plus slick-queue dependency; lock-free MPMC ring, deferred formatting on writer thread, shared-memory multi-process mode.

## Maintenance

Actively maintained (v2.2.0 released 2026-09-28) and MIT-licensed, so copyable; adoption is very low (5 stars) and all numbers are first-party, from one Windows laptop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/README.md gives throughput tables against spdlog 1.12.0 sync and async from public code in benchmarks/ (benchmark_main.cpp, fetched spdlog/fmt via benchmarks/CMakeLists.txt), with MSVC 19.44 /O2 /DNDEBUG C++20 and AMD Ryzen 9 5900HX stated; all quoted numbers match the tables.
- **Verifier notes:** Numbers verified against benchmarks/README.md; metadata (MIT, 5 stars, last commit 2026-09-28 Release v2.2.0) matches github.com pages. Very low adoption.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/README.md>
  - <https://github.com/SlickQuant/slick-logger>
  - <https://github.com/SlickQuant/slick-logger/commits>
- **Sources the enricher read:**
  - <https://github.com/SlickQuant/slick-logger>
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/README.md>
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/benchmarks/benchmark_main.cpp>
  - <https://raw.githubusercontent.com/SlickQuant/slick-logger/HEAD/benchmarks/throughput_benchmark.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/slickquant/slick-logger`) · [data/wave11/enrich/raw/github_com_slickquant_slick_logger.json](../../../data/wave11/enrich/raw/github_com_slickquant_slick_logger.json) (enrichment confidence 0.8)

</details>
