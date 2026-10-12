# dispenso

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Meta's work-stealing C++ thread pool and parallel-algorithms library, faster than oneTBB on small/medium parallel-for loops.

| | |
|---|---|
| **Beats** | oneTBB (Intel Threading Building Blocks) |
| **Claimed result** | 1M elements, 1 thread: 279us (dispenso) vs 450us (tbb) = 1.61x; 1M elements, 8 threads: 50.6us vs 175.8us = 3.48x; 100M elements, 16 threads: 2.27ms vs 3.47ms = 1.53x (all derived from page data) |
| **Workload** | "summing_for" parallel-for microbenchmark summing 1M and 100M elements, swept 1-166 threads on a 166-core AMD EPYC Genoa server; dispenso::parallel_for vs tbb::parallel_for. |
| **Metric** | latency |
| **Hardware** | AMD EPYC-Genoa Processor, 166 cores, 224 GB RAM, Linux 6.16.1 |
| **Compiler and flags** | GNU 11.5.0, C++20, CMake Release build (cxx_flags: -I/tmp/folly-shim); explicit -O level not separately listed |
| **Adoption** | 305 stars; used in hundreds of projects at Meta |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/facebookincubator/dispenso) · [benchmark](https://facebookincubator.github.io/dispenso/benchmarks/) |

## Verdict

On Meta's public benchmark dashboard (GNU 11.5.0, C++20, CMake Release build, AMD EPYC-Genoa host: 166 cores, 224GB RAM, Linux 6.16.1, TBB 2023.1.0), the summing_for microbenchmark shows dispenso::parallel_for beating tbb::parallel_for at low-to-mid thread counts: 1.61x at 1M elements/1 thread (279us vs 450us), 3.48x at 1M elements/8 threads (50.6us vs 175.8us), and 1.53x at 100M elements/16 threads (2.27ms vs 3.47ms). I independently pulled results/linux_x64.json from the repo and confirmed its machine_info block (compiler, standard, build type, CPU, core count) matches the record exactly. The same sweep also has TBB ahead at 128+ threads and at several low-thread 100M-element points, so the claimed numbers are favorable picks from a mixed comparison, not a uniform win.

## Use it when

- Nested or many independent parallel_for calls that would oversubscribe threads under TBB/OpenMP
- Need thread-safe shared futures with then()/when_all()/when_any(), which TBB lacks
- Need ASAN/TSAN-clean concurrent C++ (TBB is not sanitizer-friendly)
- Small-to-medium parallel-for workloads at low-to-mid thread counts, where the project's own EPYC-Genoa benchmark shows 1.5-3.5x over tbb::parallel_for
- Codebase pinned to a C++14 baseline that still wants a modern TBB/OpenMP alternative

## Skip it when

- Very high thread counts on large cores: on the project's own 166-core EPYC data, TBB is faster at 128 and 166 threads for the 1M-element case, and at 1-4 and 32 threads for the 100M-element case
- I/O-bound workloads — the FAQ explicitly says pool threads that block on I/O waste scheduling capacity and points to Folly instead
- Need OpenMP-style '#pragma omp reduction' syntax — dispenso has no first-class reduction API, only manual per-thread accumulation
- Need GPU/CUDA task graphs — TaskFlow supports CUDA graph mapping, dispenso does not
- macOS builds needing explicit CPU-pinning — CpuSet::bindCurrentThread() is a documented no-op there

## How it is fast

A work-stealing ThreadPool underlies all scheduling; parallel_for supports static (equal up-front chunking, lowest overhead) or adaptive (stripe-based work-stealing that prefers same-L3-cache victims) chunking, tuned via minItemsPerChunk. Cascading parallel_for lets independent loops share the pool without oversubscription, which the project reports as a 32-50% win over TBB in production after porting. Lock-free primitives (a ChaseLevDeque work-stealing deque, MPMC/SPSC ring buffers, a bundled moodycamel::ConcurrentQueue) back the scheduler and containers with low per-task overhead.

## Compared with alternatives

Versus other oneTBB-beating siblings here (TooManyCooks, libfork, Taskflow — all coroutine/C++20-leaning with bigger peak ratios in their own benchmarks), pick dispenso when you need a C++14-compatible, sanitizer-clean, explicitly-controlled thread pool rather than a coroutine scheduler, or when your workload is many independent/nested parallel_for loops where dispenso's cascading scheduling avoids oversubscription. Versus the std::thread/std::async-only siblings (Boost.Fiber, utl::parallel, BS::thread_pool, meet1214/thread-pool), dispenso is the pick when your actual incumbent is TBB or OpenMP rather than bare std primitives.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | moodycamel::concurrentqueue (bundled by default under dispenso/third-party, or an installed copy via -DDISPENSO_USE_SYSTEM_CONCURRENTQUEUE=ON) |
| **Minimum toolchain** | C++14 (default, fully supported); C++17/C++20 swap in std facilities and add concept constraints but change no behavior; CMake 3.12+ |
| **Platforms** | Linux x86-64/ARM64, macOS x86-64/ARM64, Windows x86-64/ARM64, FreeBSD (full); Android ARM64 (partial CPU-affinity/topology) |
| **Thread safety** | ThreadPool and ConcurrentTaskSet support scheduling from multiple threads simultaneously; ConcurrentVector supports concurrent push_back with iterators/references that stay valid across growth, but 'not all operations are concurrent-safe' per the docs. Library is built and tested clean under ASAN/TSAN. |
| **Drop-in for the baseline** | false — explicit ThreadPool/TaskSet objects and its own parallel_for/Future API, not TBB's implicit global arena or std::async's per-call thread; the project ships separate TBB and OpenMP migration guides rather than calling itself a drop-in |

## Gotchas

- Exceptions thrown inside parallel_for/TaskSet lambdas are captured, not propagated immediately; the first one rethrows only when wait() runs (or the TaskSet destructor), and other in-flight tasks keep running
- Builds with -fno-exceptions call abort() instead of throwing
- moodycamel::ConcurrentQueue is a by-value member of ThreadPool, so it's part of dispenso's ABI — building the library against one concurrentqueue version while a consumer compiles against another is an undiagnosed ODR violation
- DISPENSO_SHARED_LIB defaults to ON, so a static build has to be requested explicitly

## Caveats and trade-offs

The claimed points are favorable picks from mixed results against TBB. On the same Genoa data TBB is faster at 1M elements with 128 threads (47.6us vs 47.8us) and 166 threads (44.2us vs 49.3us). It is also faster at 100M elements with 1-4 and 32 threads (e.g. 2 threads: 14.55ms vs 16.72ms; 32 threads: 2.47ms vs 2.69ms). OpenMP beats dispenso at many points. The 'Future/Async Tree Build' chart, the advertised std::async comparison, has zero data points on all four platforms. The dashboard does, however, hold direct std comparisons with real data: dispenso::RWLock vs std::shared_mutex (serial, 2 iterations: 6.07ms vs 11.52ms), OnceFunction vs std::function (small move: 20.8ns vs 148.4ns), and ConcurrentVector vs std::vector/std::deque. Flags are the CMake Release defaults (cxx_flags lists only -I/tmp/folly-shim), and the CPU is the VM string 'AMD EPYC-Genoa Processor' with no SKU. The 1K-element runs show &gt;50x gaps dominated by TBB dispatch overhead and were excluded.

Larger API surface than std::async (work-stealing pools, parallel_for, futures, task graphs, concurrent containers); explicitly positioned as a TBB/OpenMP alternative rather than a drop-in std::async replacement.

## Maintenance

Actively maintained by Meta (last commit 2026-09-02, current release v1.6.2, packaged for Conan/vcpkg/Homebrew/conda-forge/Fedora); MIT-licensed and small enough to vendor, but it is a built static/shared CMake library rather than header-only, with one bundled MIT/BSD-compatible dependency (moodycamel::concurrentqueue).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The dashboard's embedded data for the Genoa platform shows dispenso vs tbb in summing_for. The benchmark code is public (benchmarks/summing_for_benchmark.cpp), and the page states the compiler (GNU 11.5.0, C++20), the build (CMake Release) and the CPU (AMD EPYC-Genoa Processor, 166 cores). One weakness: the CPU is only a VM model string with no SKU.
- **Verifier notes:** All three claimed TBB data points match the embedded PLATFORMS JSON exactly. The page also has std::shared_mutex, std::function and std::vector comparisons (libstdc++ on Linux/GCC 11.5, MSVC STL on Windows, libc++ on macOS). The orchestrator may want separate stdlib-baseline records for those. The default-branch last commit is 2026-09-02 (pushed_at is 2026-09-03).
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://facebookincubator.github.io/dispenso/benchmarks/>
  - <https://github.com/facebookincubator/dispenso>
  - <https://github.com/facebookincubator/dispenso/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://github.com/facebookincubator/dispenso>
  - <https://github.com/facebookincubator/dispenso/blob/main/README.md>
  - <https://github.com/facebookincubator/dispenso/blob/main/docs/faq.md>
  - <https://github.com/facebookincubator/dispenso/blob/main/docs/building.md>
  - <https://github.com/facebookincubator/dispenso/blob/main/docs/getting_started.md>
  - <https://github.com/facebookincubator/dispenso/blob/main/CMakeLists.txt>
  - <https://github.com/facebookincubator/dispenso/blob/main/dispenso/thread_pool.h>
  - <https://github.com/facebookincubator/dispenso/blob/main/results/linux_x64.json>
  - <https://github.com/facebookincubator/dispenso/issues>
  - <https://facebookincubator.github.io/dispenso/benchmarks/>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/facebookincubator/dispenso`) · [data/wave1/enrich/raw/github_com_facebookincubator_dispenso.json](../../../data/wave1/enrich/raw/github_com_facebookincubator_dispenso.json) (enrichment confidence 0.75)

</details>
