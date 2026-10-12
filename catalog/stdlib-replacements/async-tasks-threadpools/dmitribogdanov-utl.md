# utl::parallel (UTL ThreadPool)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 work-stealing thread pool with recursion-safe futures; beats std::async on small and recursive tasks.

| | |
|---|---|
| **Beats** | std::async |
| **Claimed result** | Small non-recursive: utl::parallel::ThreadPool 573.3% vs std::async() 214.0% of serial speed (\~2.7x faster than std::async, derived from page data). Large non-recursive: 597.0% vs 564.2% (\~1.06x, roughly tied). Shallow recursive: 583.0% vs 161.1% (\~3.6x faster than std::async; BS::thread_pool and progschj/ThreadPool deadlock entirely on this workload). Deep recursive: 565.1% vs 154.7% (\~3.65x faster than std::async, derived from page data). |
| **Workload** | Four microbenchmark scenarios, 1000 tasks each: (1) small non-recursive tasks busy-waiting 0-100us, (2) large non-recursive tasks busy-waiting 1000-3000us, (3) shallow recursive tasks (0-100us with 70% chance of spawning+awaiting one more such task), (4) deep recursive tasks (0-100us with 49% chance of spawning+awaiting two more such tasks, averaging \~50 subtasks); reports ms/op and op/s relative to a serial baseline |
| **Metric** | throughput |
| **Hardware** | 6-core AMD Ryzen 5 5600H, hyper-threading disabled |
| **Compiler and flags** | g++ 11.4.0, -O2 |
| **Adoption** | 336 stars |
| **Last commit** | 2025-12-08 |
| **Links** | [repository](https://github.com/DmitriBogdanov/UTL) · [benchmark](https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_parallel.md) |

## Verdict

On a 6-core AMD Ryzen 5 5600H (hyper-threading off), g++ 11.4.0 -O2, against libstdc++: utl::parallel::ThreadPool reached 573.3% of serial throughput vs std::async's 214.0% on small (0-100us) tasks (\~2.7x faster) and 583.0%/565.1% vs 161.1%/154.7% on shallow/deep recursive tasks (\~3.6x faster), where BS::thread_pool and progschj/ThreadPool deadlocked entirely; on large (1-3ms) tasks the two were nearly tied (597.0% vs 564.2%, \~1.06x).

## Use it when

- Many small (well under 1ms) tasks where std::async's per-call thread-spawn overhead dominates runtime
- Recursive/scatter-gather workloads (divide-and-conquer, fan-out fibonacci-style spawning) that need awaitable subtasks without deadlocking
- Header-only C++17 codebases that want a single dependency-free, vendorable (\~600-900 LOC) thread pool instead of pulling in a framework
- Cross-platform targets (Windows, Linux, macOS, FreeBSD all CI-tested) needing a pool with no platform-specific code
- Parallel-for / parallel-reduce over containers or index ranges with automatic grain-size splitting

## Skip it when

- Large uniform non-recursive tasks (1-3ms+): advantage over std::async nearly vanishes (\~1.06x, roughly tied)
- Workloads wanting a vendor-optimized scheduler (OpenMP/TBB-class NUMA-aware or SIMD-tuned scheduling) — author explicitly disclaims superiority over those
- Code that needs a real std::future everywhere (generic code pattern-matching on std::future&lt;T&gt;); future_type is a custom wrapper, only constructible from std::future, not one itself
- Projects already committed to a C++20-only recursive pool (Leopard, riften::ThiefPool) if that ecosystem fits better; utl::parallel is intentionally capped at C++17
- High-stakes throughput decisions without your own validation: this is the project's single-machine (consumer laptop) benchmark with no independent third-party reproduction, and the library is small (336 stars) and young

## How it is fast

Work-stealing thread pool: each worker has a local LIFO deque fed by recursively spawned tasks (kept hot in cache) plus a global FIFO queue for externally submitted tasks; idle threads steal from the back of other workers' local deques. Recursive awaiting is made safe by a custom future_type wrapping std::future whose get()/wait() search for stealable work locally instead of blocking outright, which is what avoids both the thread-creation overhead of std::async and the deadlocks that plain std::future-based pools hit on nested awaits.

## Compared with alternatives

Pick utl::parallel over BS::thread_pool or meet1214/thread-pool when the workload has recursively-awaited subtasks — both siblings deadlock on that pattern per UTL's own benchmark, while utl::parallel stays correct and \~3.6x faster than std::async. For large-scale or NUMA-sensitive scatter-gather work, the oneTBB-class siblings (Taskflow, dispenso, TooManyCooks, libfork) are the more feature-complete choice; utl::parallel wins when you want a minimal, dependency-free, copy-pastable single header instead of a full framework.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only: &lt;thread&gt;, &lt;future&gt;, &lt;mutex&gt;, &lt;condition_variable&gt;, &lt;queue&gt;, &lt;optional&gt;, etc.) |
| **Minimum toolchain** | C++17 |
| **Platforms** | any (CI-tested on Windows, Ubuntu, macOS, FreeBSD); no platform-specific code |
| **Thread safety** | All ThreadPool methods (including set_thread_count, task submission) are thread-safe and callable concurrently from any number of external threads. Calling set_thread_count() from a thread that is itself inside the pool throws std::runtime_error instead of deadlocking. |
| **Drop-in for the baseline** | partial — explain: task submission API (detached_task/awaitable_task/blocking_loop) differs from std::async(), and awaitable_task returns a custom future_type (constructible from std::future, same method surface) rather than std::future itself, which is required specifically so recursive get()/wait() can steal work instead of deadlocking. |

## Gotchas

- future_type is not std::future; code that specifically requires std::future&lt;T&gt; (e.g. via type traits) won't accept it directly, only convert from one
- set_thread_count() blocks until all in-flight tasks finish before resizing, and throws std::runtime_error if invoked from inside the pool on itself
- Default grain size is hardware_concurrency()\*4 subranges; very unevenly-costed per-element work may need a manually tuned grain_size
- Only 4 of the module's benchmark scenarios include BS::thread_pool/progschj/ThreadPool as recursion baselines; those two deadlock outright once tasks await nested subtasks

## Caveats and trade-offs

Author explicitly disclaims superiority over vendor-optimized frameworks (OpenMP/TBB). On large non-recursive tasks the advantage over std::async almost disappears (\~1.06x) since thread-creation overhead is amortized; the large speedups are concentrated in small-task and recursive-task scenarios, exactly where std::async's per-call thread-spawn cost dominates. Benchmarked on a single consumer laptop CPU (Ryzen 5 5600H), not server-class hardware; this is the project's own README benchmark with no independent third-party reproduction found, though code, compiler, flags, and CPU model are all public and stated (meets Tier A bar on reproducibility grounds). Library itself is small (336 stars) and young.

Uses a custom future type instead of std::future so recursive awaiting doesn't deadlock, so it is not a drop-in std::future replacement; ships as one module inside a larger multi-module header-only utility collection (UTL) rather than a standalone package; explicitly a niche tool for recursive/scatter-gather workloads, not a general vendor-optimized scheduler like TBB/OpenMP.

## Maintenance

Actively maintained (last commit 2025-12-08 on master; 336 stars); MIT-licensed, header-only, small enough (\~600-900 LOC for this module) to vendor directly into a project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/module_parallel.md benchmarks utl::parallel::ThreadPool against std::async() and serial runs, with g++ 11.4.0 -O2 on an AMD Ryzen 5 5600H (6 cores, HT off). The benchmark code is public at benchmarks/module_parallel/thread_pool_comparison.cpp.
- **Verifier notes:** All four scenario percentages match the page, and the derived ratios (2.68x, 1.06x, 3.62x, 3.65x) are correct. The last commit on the default branch (master) is 2025-12-08. The 2026-09-19 date is a commit on the 'dev' branch, so the repo is active either way. MIT license and 336 stars were checked and are correct.
- **Fields the verifier corrected:** `last_commit`
- **Pages the verifier opened:**
  - <https://github.com/DmitriBogdanov/UTL>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_parallel.md>
  - <https://github.com/DmitriBogdanov/UTL/tree/master/benchmarks/module_parallel>
- **Sources the enricher read:**
  - <https://github.com/DmitriBogdanov/UTL>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/README.md>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_parallel.md>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/include/UTL/parallel.hpp>
  - <https://github.com/DmitriBogdanov/UTL/tree/master/benchmarks/module_parallel>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/dmitribogdanov/utl`) · [data/wave1/enrich/raw/github_com_dmitribogdanov_utl.json](../../../data/wave1/enrich/raw/github_com_dmitribogdanov_utl.json) (enrichment confidence 0.75)

</details>
