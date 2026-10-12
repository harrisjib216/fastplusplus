# low-latency-log

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 (some code from logflume under MIT, LICENSE-LOGFLUME)` · 🟡 stale

> Small async Rust file logger with deferred formatting; higher backend throughput than spdlog-rs, fast_log, ftlog in its own harness.

| | |
|---|---|
| **Beats** | quill (C++), spdlog-rs, fast_log, ftlog |
| **Claimed result** | M3 Max: throughput 4.563 M msgs/s vs C++ quill 2.88, spdlog-rs 2.605, fast_log 1.741, ftlog 1.688; median hot-path 58 ns vs spdlog-rs 252 ns but quill 22 ns. Xeon Gold 6231C: 2.609 M msgs/s vs quill 2.24 and spdlog-rs 1.478; median 112 ns vs spdlog-rs 592 ns, quill 36 ns |
| **Workload** | Hot-path latency percentiles and backend throughput, 2M messages per thread, 1 and 4 threads. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro M3 Max 48GB; Xeon Gold 6231C |
| **Compiler and flags** | Rust 1.78.0 (M3 Max) and Rust 1.79.0 (Xeon) release builds; quill compiler/flags not stated |
| **Adoption** | 2 stars |
| **Last commit** | 2024-08-22 |
| **Links** | [repository](https://github.com/WANG-lp/low-latency-log) · [benchmark](https://github.com/WANG-lp/low-latency-log/blob/main/BENCHMARK.md) |

## Verdict

First-party runs in BENCHMARK.md: median per-call cost 58 ns (1 thread) on an M3 Max with Rust 1.78.0, against spdlog-rs 252 ns, fast_log 275 ns, ftlog 341 ns and C++ quill 22 ns, and drain throughput of 4.563 M msgs/s against quill 2.88, spdlog-rs 2.605, fast_log 1.741 and ftlog 1.688; on a 4-core Tencent Cloud Xeon Gold 6231C (Rocky 9.3, Rust 1.79.0), 112 ns median and 2.609 M msgs/s against spdlog-rs 592 ns / 1.478 and quill 36 ns / 2.24. All logs went to /dev/shm, single runs, quill compiler and flags not stated.

## Use it when

- Rust services that log moderate rates (a few million lines per second at most) to local files and want the formatting cost moved off the request thread.
- When spdlog-rs, fast_log or ftlog is your current choice and its 250-600 ns median call cost shows up in profiles; this crate measured 58 ns (M3 Max) and 112 ns (Xeon Gold 6231C) median in the same harness.
- Single-process tools where a fixed line format and file rolling by time or size are all you need.
- As a small (about 900 lines) reference to read or vendor for a deferred-formatting logger in Rust.

## Skip it when

- If you need the lowest hot-path latency: C++ Quill was 2-3x faster at the median (22 vs 58 ns on M3 Max, 36 vs 112 ns on Xeon) and the README itself only claims comparable p99.9.
- Strict allocation-free or bounded-latency hot paths: every call heap-allocates a boxed closure, and a full bounded queue makes the caller block in crossbeam send rather than drop.
- Structured or JSON logging, multiple sinks, runtime level changes, custom line formats or non-file outputs: none exist (fixed format, compile-time level features).
- Arguments that borrow non-'static data: the macro moves arguments into a 'static closure, so references to locals do not compile and large values are moved into the queue.
- Long-lived projects needing maintenance: 26 commits, 2 stars, no activity since 2024-08-22, README TODOs (format! optimization, custom formats) still open.

## How it is fast

The calling thread does no formatting: the macro reads SystemTime and a cached thread-id string, boxes a closure that captures the arguments by move, and pushes it on a bounded crossbeam channel (128K entries by default). The background thread runs `format!` inside that closure, caches the seconds part of the time stamp so chrono formatting happens once per second, writes through a 1 MiB BufWriter with ufmt, and busy-polls with a 1 us (500 ns in the bench) sleep when the queue is empty. The design follows logflume and Quill's deferred-formatting idea, but with a heap-allocated closure per message rather than Quill's encoded argument buffer.

## Compared with alternatives

The catalogued siblings (Quill, BqLog, fmtlog, NanoLog, XTR, binlog) are C or C++ and all report lower per-call latency; pick low-latency-log only when you are in Rust and want something simpler than wrapping a C++ logger, accepting that Quill itself measured faster at the median in this repo's own table.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | chrono, core_affinity, crossbeam-channel, log, once_cell, ufmt, symlink, gettid, cfg-if |
| **Minimum toolchain** | Rust 2021 edition; benchmarks built with Rust 1.78.0 and 1.79.0 |
| **Platforms** | Linux and macOS measured; uses a symlink to the latest file and gettid, other platforms not documented |
| **Thread safety** | Global logger; any thread may log through a multi-producer crossbeam channel with one consumer thread. Logger::flush only sets a flag and does not wait; Logger::finish (guard drop) blocks until the queue is drained and is one-shot. |
| **Drop-in for the baseline** | partial: with .std_log(true) it serves the `log` crate facade (README TODO says that path is not yet optimized); the fast path needs its own macros and API, not spdlog-rs's |

## Gotchas

- Time stamp bug in src/lib.rs write_date_time_str: the sub-second part is written as `.{}` of the nanosecond remainder without zero padding, so 5,000,000 ns after a second prints ".5000000" (reads as 0.5 s); lines cannot be sorted or parsed by fractional time.
- open_writer_if_needed reads the existing file size with metadata(&p) on the bare file name instead of the folder-joined path, so size-based rollover starts from 0 after a restart unless the process cwd is the log folder; rollover is also only checked when the second changes.
- The guard returned by init() must be kept; dropping it stops the logger for the whole process, and finish() can run only once, so the logger cannot be restarted.
- Throughput numbers come from different harnesses: the Rust crates share bench/src/common (4M messages, tcmalloc global allocator, LLL with a 1M-entry queue and Logger::finish to drain), while quill was run from its own backend_throughput binary with an unstated build and message format.

## Known shortcomings

- Correctness bug in the output, not in the measured numbers: the sub-second timestamp is written without zero padding (src/lib.rs write_date_time_str, '.{}'), and the size-rollover check uses metadata(&p) with a bare filename. Quill has the faster median on both machines; the throughput numbers come from different harnesses (tcmalloc, a 1M queue for low-latency-log). Rust, not C++.

## Caveats and trade-offs

First-party. Does not beat spdlog or glog directly (compared to spdlog-rs and C++ quill). Quill has lower hot-path latency at every percentile up to p99 on both machines; the win is backend throughput only, measured by different harnesses (quill's backend_throughput binary vs this crate's bench_it). Includes MIT code from logflume.

Part of the code derives from logflume under a separate license; Rust only.

## Maintenance

Stale since 2024-08-22 with 2 stars, but Apache-2.0 (plus MIT-licensed logflume code) and small enough to vendor and fix the time-stamp padding yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARK.md has first-party runs (bench crate in repo, Rust release builds, M3 Max and Xeon Gold 6231C) against quill and spdlog-rs, but quill was run from its own benchmark binaries with unstated build flags and the throughput figures come from different harnesses, so not A.
- **Verifier notes:** Numbers verified in BENCHMARK.md; added Xeon results. 2 stars, last commit 2024-08-22 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/README.md>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/LICENSE-LOGFLUME>
  - <https://github.com/WANG-lp/low-latency-log>
  - <https://github.com/WANG-lp/low-latency-log/commits>
- **Sources the enricher read:**
  - <https://github.com/WANG-lp/low-latency-log>
  - <https://github.com/WANG-lp/low-latency-log/tree/main/src>
  - <https://github.com/WANG-lp/low-latency-log/tree/main/bench>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/README.md>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/LICENSE-LOGFLUME>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/macros.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/internal.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/log_proxy.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/consts.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/src/fmt_utils.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/src/bench_it.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/src/bench_spdlog.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/src/common/mod.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/src/common/low_latency_log_bench.rs>
  - <https://raw.githubusercontent.com/WANG-lp/low-latency-log/HEAD/bench/src/common/spdlog_bench.rs>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/wang-lp/low-latency-log`) · [data/wave11/enrich/raw/github_com_wang_lp_low_latency_log.json](../../../data/wave11/enrich/raw/github_com_wang_lp_low_latency_log.json) (enrichment confidence 0.8)

</details>
