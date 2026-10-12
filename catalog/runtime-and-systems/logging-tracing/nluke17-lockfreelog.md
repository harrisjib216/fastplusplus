# lockfreelog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🟢 active

> Tiny header-only C++20 SPSC ring-buffer logger; about 5.3x spdlog async throughput to /dev/null on an Apple M3.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | about 28M msg/s vs spdlog async about 5M msg/s (5.3x); about 50M msg/s on Xeon Gold 6348 |
| **Workload** | 5M messages formatted and written to /dev/null, async lock-free SPSC logger vs spdlog async, fmt, printf and iostream. |
| **Metric** | throughput |
| **Hardware** | Apple M3 (also Intel Xeon Gold 6348 for standalone figure) |
| **Compiler and flags** | clang++ -std=c++20 -O2 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/NLuke17/lockfreelog) · [benchmark](https://github.com/NLuke17/lockfreelog) |

## Verdict

bench/benchmark.cpp logs 5M "log line {} value={}" messages to /dev/null on an Apple M3 with clang++ -std=c++20 -O2: about 28M msg/s for this logger (spinning on a full 8192-slot, 128-byte ring) versus about 5M msg/s for spdlog create_async with basic_file_sink_mt, an 8192-entry blocking queue and one worker (5.3x); spdlog is the prebuilt Homebrew build and the timer stops before either queue is fully drained (at most 8192 messages each). The \~50M msg/s Xeon Gold 6348 figure has no spdlog row and no compiler stated.

## Use it when

- Exactly one hot thread emitting short integer/C-string log lines where the enqueue cost must stay in the tens of nanoseconds.
- Learning or teaching material for an acquire/release SPSC ring with compile-time format checking.
- A starting point to vendor and extend inside your own code base, once the author adds a license.
- Workloads that tolerate dropped lines under bursts (the producer never blocks).

## Skip it when

- Multiple producer threads: it is SPSC only, and calling log() from two threads is a data race.
- Anything needing floats, std::string, std::string_view, bool, user types, levels, timestamps or rotation: emit_arg only handles integral types and const char\*.
- Production use or redistribution: the repo has no license file, 0 stars and 3 commits.
- Battery- or CPU-constrained systems: the consumer spins with std::this_thread::yield() whenever the ring is empty.
- Thread stacks smaller than a few MB: the whole ring lives inside the Logger object (about 2.1 MB at the defaults), so a stack-allocated Logger can overflow.

## How it is fast

Classic Lamport SPSC queue: monotonic 64-bit head and tail indices, each with a single writer, published with release stores and read with acquire loads, so no mutex or CAS; the two indices are alignas(128) to avoid false sharing. The producer formats in place into the slot with std::to_chars and memcpy (no heap, no locale), and the consumer coalesces every pending slot into a 64 KiB stack buffer written with one fwrite per pass. spdlog async, by contrast, formats into a heap-backed message, pushes through a mutex-guarded MPMC queue and writes through a mutex sink.

## Compared with alternatives

Only when you want a minimal, dependency-free SPSC enqueue you can read in one sitting; Quill, fmtlog, PlatformLab NanoLog and XTR are mature, multi-producer, licensed, and measured at single-digit ns per call in independent harnesses, so they are the default choices for real logging.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (benchmark needs fmt and spdlog) |
| **Minimum toolchain** | C++20 (class-type NTTPs, consteval); README builds with clang++ -std=c++20 -O2 |
| **Platforms** | any with std::thread and a FILE\* sink; measured on Apple M3 macOS and Intel Xeon Gold 6348 Linux |
| **Thread safety** | one producer thread and the internal consumer thread only |
| **Drop-in for the baseline** | no |

## Gotchas

- On a full ring log() drops and increments dropped(); the benchmark spins on log() until it succeeds, so its dropped() figure counts retries, not lost lines.
- Integer truncation bug: when std::to_chars does not fit, it returns ptr == end with the range in an unspecified state, but emit_arg advances to res.ptr (the comment says it returns p), so truncated lines can contain garbage bytes.
- No fflush: output reaches the FILE\* buffer only; you must fflush/fclose the sink yourself after the Logger is destroyed. {{ escapes are not supported and extra {} pairs are treated as placeholders.
- The README cites a 5M-message SPSC hash correctness test, but no test file is in the repository (only bench/ and examples/).

## Known shortcomings

- Outside the bench: emit_arg advances to a to_chars ptr==end on overflow, so truncated integers emit unspecified bytes. Only integral and const char\* arguments, no fflush, about 2.1 MB ring inside the object (stack overflow risk), the README's SPSC hash test is missing from the repo, no license. The benchmark spins on a full ring, so dropped() counts retries; both timers stop before the queue is drained (at most 8192 messages each).

## Caveats and trade-offs

No LICENSE file (LICENSE, LICENSE.txt, LICENSE.md all 404), so reference only. Single-producer only (SPSC); sink is /dev/null, so no real I/O. spdlog side is the prebuilt Homebrew library (build flags not stated) using create_async with basic_file_sink_mt, a mutex sink, and an 8192-entry queue with the default blocking policy; the own logger retries on full. The Xeon Gold 6348 \~50M msg/s figure is the engine alone, with no spdlog row and no compiler given. New 3-commit, 0-star repo.

SPSC only; drops messages on a full buffer; consumer spins; C++20 header-only.

## Maintenance

Active but brand new (3 commits, last 2026-09-22, 0 stars) and unlicensed, so reference only; small enough to rewrite from the README's design notes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README throughput table (\~28M vs spdlog async \~5M msg/s, 5.3x) comes from public bench/benchmark.cpp, built with clang++ -std=c++20 -O2 on an Apple M3, all stated; the Xeon Gold 6348 \~50M figure has no spdlog comparison and no compiler stated.
- **Verifier notes:** Benchmark code verified to match the README description. Last commit 2026-09-22 (active).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/NLuke17/lockfreelog>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/bench/benchmark.cpp>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/LICENSE>
  - <https://github.com/NLuke17/lockfreelog/commits/main>
- **Sources the enricher read:**
  - <https://github.com/NLuke17/lockfreelog>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/bench/benchmark.cpp>
  - <https://raw.githubusercontent.com/NLuke17/lockfreelog/HEAD/include/lockfree_logger.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/nluke17/lockfreelog`) · [data/wave11/enrich/raw/github_com_nluke17_lockfreelog.json](../../../data/wave11/enrich/raw/github_com_nluke17_lockfreelog.json) (enrichment confidence 0.75)

</details>
