# Marl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> C++11 hybrid thread/fiber task scheduler from Google; tasks that block on marl primitives yield their worker instead of stalling it.

| | |
|---|---|
| **Beats** | The repo's own std::thread plus std::mutex SingleQueue and MultiQueue executors (non_marl_bench.cpp); not oneTBB or a known library pool |
| **Claimed result** | Parity on Ubuntu (0.293 s vs 0.297 s at 128 threads), about 6% faster on macOS (3.35 vs 3.55 s at 12 threads), 1.9-2.2x on Windows 10 (0.295 s vs 0.565/0.651 s at 128 threads); measured 2020-06 on a 2018 MacBook Pro and a Threadripper 3990X |
| **Workload** | Hybrid thread and fiber task scheduler microbenchmarks (graphs on google.github.io/marl/benchmarks, blocked in this session). |
| **Metric** | latency |
| **Adoption** | 2.0k stars; used in SwiftShader; archived 2026-04-27 |
| **Last commit** | 2026-04-27 |
| **Links** | [repository](https://github.com/google/marl) · [benchmark](https://github.com/google/marl) |

## Verdict

The README itself has no numbers, but the gh-pages branch carries google-benchmark JSON (2020-06, release builds) for a MacBook Pro 15in 2018 (12 threads), Ubuntu and Windows 10 on a Threadripper 3990X; compiler and flags are not recorded. Against the repo's own non-marl reference executors (std::thread + std::mutex single queue, and pre-split per-thread queues) running 262144 doSomeWork tasks, marl is roughly at parity on Ubuntu (e.g. 0.293 s vs 0.297 s at 128 threads) and about 6% faster on the MacBook at 12 threads (3.35 s vs 3.55 s), but on Windows at 128 threads it takes 0.295 s vs 0.565 s single-queue and 0.651 s multi-queue (about 1.9x-2.2x, derived from page data); EventBaton task ping-pong costs about 216 ns per pass on Ubuntu, 410 ns on macOS and 635 ns on Windows (derived from page data).

## Use it when

- CPU-bound task graphs where tasks wait on each other (events, wait groups) and you want a fixed number of OS threads, e.g. SwiftShader-style rendering or shader compilation pipelines.
- Many-core machines (64-128 hardware threads) where a single mutex-protected queue starts to contend; the published Windows Threadripper 3990X run shows the gap opening at 128 threads.
- Cross-platform code that must run on Windows, macOS, Linux, Android, iOS, Fuchsia and Emscripten with the same scheduler.
- Code that needs Go-style WaitGroup/Event semantics in C++11 without pulling in Boost or TBB.

## Skip it when

- I/O-bound servers: there is no event loop or async I/O; non-marl blocking calls (accept, std::mutex held across waits, std::condition_variable) stall a worker, and blocking_call() spawns a std::thread per call (about 17-84 us in the published runs).
- Coarse-grained tasks on a few cores: the published SomeWork runs show marl within about 1-6% of a plain std::thread + std::mutex queue at 1-64 threads, so it buys little there.
- New projects that need upstream fixes: the repository was archived read-only on 2026-04-27.
- Workloads wanting more than 256 worker threads (MaxWorkerThreads = 256) or tiny-memory fibers: default fiber stack is 1 MiB unless changed with setFiberStackSize.
- If you want stackless C++20 coroutines or a structured-concurrency API; marl is stackful and callback-based.

## How it is fast

Per-worker task and fiber queues with work stealing (Scheduler::stealWork, random victim) and a 1 ms spin-for-work loop of nop batches before sleeping, so idle workers pick up new tasks without a kernel wake-up. Blocked tasks are parked as fibers and resumed via a hand-written register-swap routine (marl_fiber_swap in per-architecture assembly; ucontext optional via MARL_FIBERS_USE_UCONTEXT), with idle fibers pooled for reuse.

## Compared with alternatives

Pick marl over libco/libaco/libgo-style coroutine libraries when you want a multi-threaded work-stealing task scheduler with fiber-aware blocking primitives rather than raw context switches; pick Coros or Boost.Cobalt when you want C++20 coroutines, or minicoro/libaco when the cost of a single switch is what matters.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_subdirectory or vcpkg; MARL_BUILD_SHARED for a shared lib) |
| **Dependencies** | none (googletest and google benchmark only for tests/benchmarks) |
| **Minimum toolchain** | C++11; CI moved to clang-18 on Linux in the final commit; VS2019 CMake integration on Windows |
| **Platforms** | Windows, macOS, Linux, FreeBSD, Fuchsia, Emscripten, Android, iOS on arm, aarch64, loongarch64, mips64, ppc64, rv64, x86, x64 |
| **Thread safety** | Scheduler may be bound to any number of threads; calling marl::schedule() from an unbound thread is undefined behavior; primitives are thread-safe and should be captured by value (except ConditionVariable). |
| **Drop-in for the baseline** | no |

## Gotchas

- Forgetting scheduler.unbind() before a bound thread exits makes the Scheduler destructor block forever.
- Holding a std::mutex while waiting on a marl primitive can deadlock: the fiber yields with the lock held.
- Multiple Scheduler instances compete for cores; README recommends one per process, and its constructor is expensive (spawns threads).
- Idle workers spin for up to 1 ms before sleeping, which shows up as CPU usage on otherwise idle machines.

## Caveats and trade-offs

Repository archived by Google on 2026-04-27 (last commit 'kokoro: Linux uses clang-18 (#283)' the same day); README does not say the project is finished. Benchmark graphs live on google.github.io (egress blocked), so no number or baseline was verified; no comparison against std::thread or another incumbent appears in the README.

C++11; platforms include Windows, macOS, Linux, FreeBSD, Fuchsia, Emscripten, Android, iOS on arm, aarch64, loongarch64, mips64, ppc64, rv64, x86, x64; blocking non-marl calls stall a worker; repository archived read-only.

## Maintenance

Archived read-only by Google on 2026-04-27 with no 'finished' statement, but Apache-2.0, dependency-free and still packaged in vcpkg, so vendoring a pinned copy is reasonable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** README's Benchmarks section only links graphs on google.github.io/marl/benchmarks (blocked here); no numbers or named baseline on the repo page. Kept at D because the project is notable (2.0k stars, used by SwiftShader).
- **Retiered** D to C: Raised from D to C: the gh-pages benchmark JSON is reachable (raw.githubusercontent.com/google/marl/gh-pages/benchmarks/results/\*.json, 2020-06; MacBook Pro 2018 and Threadripper 3990X on Ubuntu and Windows 10; compiler and flags not recorded) and the baseline is the repo's own std::thread plus std::mutex SingleQueue and MultiQueue executors (non_marl_bench.cpp). Marl is at parity on Ubuntu (0.293 s vs 0.297 s at 128 threads), about 6% faster on Mac (3.35 vs 3.55 s at 12 threads) and 1.9-2.2x faster only on Windows 10 at 128 threads (0.295 vs 0.565/0.651 s). The reference executors fill their queue with timing paused while marl's enqueue is timed, which favours the baseline.
- **Verifier notes:** D but notable (2.0k stars), so not rejected under not-notable-tier-d. maintenance_status changed from finished to abandoned because the repo is archived and the author never declared it complete.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `caveats`, `baseline`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/marl/HEAD/README.md>
  - <https://github.com/google/marl>
  - <https://github.com/google/marl/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/marl/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/marl/HEAD/include/marl/scheduler.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/include/marl/task.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/include/marl/event.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/include/marl/waitgroup.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/include/marl/blockingcall.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/scheduler.cpp>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/osfiber_asm_x64.S>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/scheduler_bench.cpp>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/event_bench.cpp>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/non_marl_bench.cpp>
  - <https://raw.githubusercontent.com/google/marl/HEAD/src/marl_bench.h>
  - <https://raw.githubusercontent.com/google/marl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/marl/gh-pages/benchmarks/index.html>
  - <https://raw.githubusercontent.com/google/marl/gh-pages/benchmarks/metadata.json>
  - <https://raw.githubusercontent.com/google/marl/gh-pages/benchmarks/results/macbookpro-15in-2018.json>
  - <https://raw.githubusercontent.com/google/marl/gh-pages/benchmarks/results/ubuntu-tr3-3990x.json>
  - <https://raw.githubusercontent.com/google/marl/gh-pages/benchmarks/results/win10-tr3-3990x.json>
  - <https://github.com/google/marl/issues?q=is%3Aissue+deadlock+OR+crash+OR+performance>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/google/marl`) · [data/wave11/enrich/raw/github_com_google_marl.json](../../../data/wave11/enrich/raw/github_com_google_marl.json) (enrichment confidence 0.7)

</details>
