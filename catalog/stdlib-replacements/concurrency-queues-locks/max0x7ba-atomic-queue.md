# atomic_queue

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only lock-free MPMC/SPSC ring-buffer queues beating std::mutex-guarded queues by 4-10x in latency and throughput.

| | |
|---|---|
| **Beats** | std::mutex |
| **Claimed result** | Ping-pong latency on Ryzen 5950X (SMT): AtomicQueue mean 42ns vs std::mutex 320ns (\~7.6x lower); OptimistAtomicQueue 33ns (\~9.7x lower). 1-producer/1-consumer throughput on 5950X: AtomicQueue \~142.7M msg/s vs std::mutex \~4.1M msg/s (\~34x); OptimistAtomicQueue mean \~1.23B msg/s (stdev \~136M, max \~2.04B). With 2-16 producer/consumer pairs, OptimistAtomicQueue stays \~4-24x ahead of std::mutex (52.9M vs 13.0M msg/s at 2; 55.3M vs 2.3M at 16), while plain AtomicQueue is roughly at parity with std::mutex. |
| **Workload** | SPSC round-trip ping-pong: 2 threads exchange a 4-byte int counter 1,000,000 times via two queue instances (lowest-contention case); also an N-producer/N-consumer throughput scalability test moving 1,000,000 messages through one queue, run across AMD Ryzen 5950X, Ryzen 5825U, Intel i9-9900KS and Intel Xeon Gold 6132. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5950X and Ryzen 5825U (KDE Neon/Ubuntu 24.04, kernel 6.8, mitigations=off); legacy: Intel i9-9900KS (Kubuntu 18.04) and Intel Xeon Gold 6132 (RHEL 6.10) |
| **Compiler and flags** | gcc-14.2.0 (Ryzen 5950X/5825U); gcc-8.4.0 (legacy i9-9900KS/Xeon Gold 6132). Current Makefile gcc release flags: -O3 -march=native -mtune=native -falign-functions=64 -DNDEBUG -fno-stack-protector -fno-stack-clash-protection -fno-tree-ch -fno-move-loop-invariants -fno-plt -fno-math-errno -ffinite-math-only -pthread; benchmarks.cc is compiled with -std=c++17, which is appended after the base -std=c++14. |
| **Adoption** | 1.9k stars; packaged in Conan Center and vcpkg |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/max0x7ba/atomic_queue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html) |

## Verdict

On the author's own shootout (gcc-14.2.0, libstdc++, Ryzen 5950X with SMT on), AtomicQueue's SPSC ping-pong round-trip latency is 42ns versus 320ns for a std::mutex-guarded ring buffer baseline (\~7.6x lower), and OptimistAtomicQueue reaches 33ns (\~9.7x lower); 1-producer/1-consumer throughput is \~142.7M msg/s for AtomicQueue and a highly variable \~1.23B msg/s for OptimistAtomicQueue versus \~4.1M msg/s for std::mutex, though with 2-16 producer/consumer pairs only OptimistAtomicQueue keeps a large (4-24x) lead while plain AtomicQueue is roughly at parity with std::mutex.

## Use it when

- Fixed/bounded number of in-flight small, cheaply copyable/movable messages (integers, pointers, small PODs) between a known set of threads.
- Sub-microsecond push-to-pop latency matters more than avoiding CPU spin, and dedicated cores/threads are available to spin.
- SPSC hot path (e.g. one I/O thread feeding one processing thread) where the SPSC-tuned mode avoids read-modify-write atomics entirely.
- Shared-memory IPC between processes: non-B variants are position-independent and can be placement-new'd into mmap/shm_open segments.
- Need back-pressure signaling via try_push failure rather than letting a queue grow unbounded.

## Skip it when

- Need unbounded or dynamically-growing capacity; maximum size must be fixed at compile time (array buffer) or construction time (B variants).
- Threads should sleep/block instead of spinning; there is no OS-blocking wait, so waiting threads pin a CPU core at 100%.
- Elements are large or expensive to copy/move, since push/pop always copies or moves the element and no in-place references are exposed.
- Need per-element priorities or ordering guarantees beyond FIFO/the optional totally-ordered mode.
- Atomic-element queues: pushing the reserved NIL sentinel is undefined behavior in release builds (only debug asserts catch it), so element type/value range must exclude it.

## How it is fast

A ring buffer with compile-time or construction-time fixed capacity avoids heap allocation and pointer chasing after construction, and value semantics (no references into the buffer) avoid pointer aliasing. It issues the bare minimum of atomic instructions per push/pop, explicitly pads to avoid false sharing, and its SPSC mode drops expensive atomic read-modify-write ops in favor of plain atomic loads/stores. There is no OS-blocking wait path: push/pop either fail fast (try_ variants) or busy-spin (optimist push/pop), avoiding the roughly 1-3us syscall/wake-up latency of a blocked thread.

## Compared with alternatives

Pick atomic_queue's OptimistAtomicQueue when the workload has contention from multiple producer/consumer pairs, since it is the only queue in this shootout that keeps a large (4-24x) throughput lead over std::mutex from 2 to 16 pairs, or when queue objects must be position-independent for shared-memory IPC. For a pure low-contention SPSC channel, moodycamel::ReaderWriterQueue (43ns) and Boost.Lockfree spsc_queue (51ns) post comparable ping-pong latency with smaller, more established codebases, and plain (non-optimist) AtomicQueue itself is only at parity with std::mutex once several producer/consumer pairs contend.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none to use the library; Boost.Test is needed only to build its own unit tests |
| **Minimum toolchain** | C++14; also builds under C++20/C++23 as of v1.9.4 (v1.9.3 had a C++20 AtomicQueueB2 constructor bug on Apple clang, fixed in v1.9.4) |
| **Platforms** | Linux x86_64 (primary dev/benchmark target); CI also covers Linux ARM, RISC-V, PowerPC, S390, LoongArch (via QEMU), Windows x86_64, and macOS ARM |
| **Thread safety** | Lock-free MPMC and SPSC-tuned modes built on std::atomic; queue objects are safe to share across threads or processes, but pushing the NIL sentinel on atomic-element queues is undefined behavior |
| **Drop-in for the baseline** | partial — explain: same push/pop role as a std::mutex-guarded queue, but a different API (try_push/try_pop, fixed capacity, value semantics, NIL sentinel for atomic variants); not source-compatible with std::queue |

## Gotchas

- NIL sentinel (default 0) must never be pushed into atomic-element queues; release builds have no runtime check and violation causes UB such as deadlocks or lost elements.
- No OS-blocking push/pop: busy-spin waiting consumes a full CPU core, unsuitable for threads that should yield or sleep.
- v1.9.3 broke AtomicQueueB2's constructor under -std=c++20 on Apple clang (issue #109, fixed in v1.9.4, released 2026-09-16); use &gt;=1.9.4.
- Capacity is fixed once (compile time for array buffers, construction time for heap/B-variant buffers) and cannot grow; undersizing it makes try_push start failing under load.

## Caveats and trade-offs

The 'std::mutex' baseline is atomic_queue's own fixed-size ring buffer guarded by std::mutex (AtomicQueueMutex), polled through try_push/try_pop retry loops. It is not std::queue with a condition variable. The \~1.23B msg/s 1P/1C OptimistAtomicQueue figure varies a lot (stdev \~136M, max \~2.04B). The page says throughput exceeds the inverse of latency on purpose, because the throughput loop has no dependency chains. Treat the 7.6-9.7x latency figures as the conservative claim. With 2+ producer/consumer pairs on the 5950X, plain AtomicQueue is roughly at parity with std::mutex: std::mutex leads at 2 pairs (13.0M vs 10.1M msg/s) and ties at 4. Only OptimistAtomicQueue keeps a large throughput lead under contention.

Fixed capacity set at compile/construction time (ring buffer, no heap growth); no OS-blocking wait, only busy-spin (push/pop can't sleep, unsuitable for non-latency-critical code that wants to yield the CPU); atomic-element variants reserve a NIL sentinel value that must never be pushed; value-semantics only (copies/moves elements, no in-place references).

## Maintenance

Actively maintained (recent commits and the v1.9.4 point release as of September 2026) under the MIT license; header-only and small enough to vendor directly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** src/benchmarks.cc in the repo runs the ping-pong latency and N-producer/N-consumer throughput benchmarks against a ring buffer guarded by std::mutex (AtomicQueueMutex&lt;unsigned, C, std::mutex&gt;). The page names the compilers (gcc-14.2.0, and gcc-8.4.0 on the legacy boxes), CPUs, OS and kernel, and the Makefile holds the release flags.
- **Verifier notes:** All claimed numbers match the page's results.js: 5950X SMT latency 42/33/320 ns and 1P/1C throughput 142.7M/1227.1M/4.1M msg/s. I removed the record's unsupported claim that the 1.23B figure is 'almost certainly' a compiler artifact, because the author attributes it to the benchmark design. Metadata checked: MIT, 1894 stars, not a fork, last commit 2026-09-22, Conan Center and vcpkg listed in the README.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
  - <https://max0x7ba.github.io/atomic_queue/html/results.js>
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.js>
  - <https://github.com/max0x7ba/atomic_queue>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/Makefile>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/src/benchmarks.cc>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/include/atomic_queue/atomic_queue_mutex.h>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/max0x7ba/atomic_queue>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/README.md>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/src/example.cc>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/CHANGELOG.md>
  - <https://github.com/max0x7ba/atomic_queue/issues/109>
  - <https://github.com/max0x7ba/atomic_queue/issues?q=is%3Aissue>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/max0x7ba/atomic_queue`) · [data/wave1/enrich/raw/github_com_max0x7ba_atomic_queue.json](../../../data/wave1/enrich/raw/github_com_max0x7ba_atomic_queue.json) (enrichment confidence 0.85)

</details>
