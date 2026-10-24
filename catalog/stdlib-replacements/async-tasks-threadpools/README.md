# Async tasks and thread pools

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::async, std::thread, std::future  
**10 entries:** 5 tier A · 1 tier B · 3 tier C · 1 tier D · 9 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**libfork**](conorwilliams-libfork.md) | Header-only C++20/23 coroutine fork-join library beating oneTBB and OpenMP on fine-grained task throughput and memory. | **A** | C++ | MPL-2.0 | 🟢 active |
| 2 | [**Boost.Fiber**](boostorg-fiber.md) | Cooperative user-space fibers with a std::thread-like API, spawning and context-switching orders of magnitude cheaper than std::thread/std::async. | **A** | C++ | BSL-1.0 | 🟢 active |
| 3 | [**utl::parallel (UTL ThreadPool)**](dmitribogdanov-utl.md) | Header-only C++17 work-stealing thread pool with recursion-safe futures; beats std::async on small and recursive tasks. | **A** | C++ | MIT | 🟢 active |
| 4 | [**dispenso**](facebookincubator-dispenso.md) | Meta's work-stealing C++ thread pool and parallel-algorithms library, faster than oneTBB on small/medium parallel-for loops. | **A** | C++ | MIT | 🟢 active |
| 5 | [**TooManyCooks (TMC)**](tzcnt-toomanycooks.md) | Header-only C++20 coroutine thread pool with continuation-stealing scheduling; 1.1-3.8x faster than oneTBB on fork-join workloads. | **A** | C++ | BSL-1.0 | 🟢 active |
| 6 | [**Taskflow**](taskflow-taskflow.md) | Header-only C++ task-graph library that beats oneTBB FlowGraph on heterogeneous CPU+GPU DAG workloads. | **B** | C++ | MIT | 🟢 active |
| 7 | [**Modern C++ Programming Cookbook 3rd ed.: parallel map and…**](paper-book-modern-cpp-programming-cookbook-third-edition-parallel-map-ce51c5af.md) | Cookbook recipe: chunked parallel map and fold with std::async tasks, beating sequential std::transform and std::accumulate on large vectors. | **C** | C++ | MIT | 🟡 stale |
| 8 | [**Modern C++ Programming Cookbook 3rd ed.: parallel map and…**](paper-book-modern-cpp-programming-cookbook-third-edition-parallel-map-5b64356b.md) | Book recipe running std::transform and std::accumulate on one std::thread per hardware thread; about 2.2x at 50M ints. | **C** | C++ | MIT | 🟡 stale |
| 9 | [**meet1214/thread-pool**](meet1214-thread-pool.md) | Header-only C++17 fixed-size thread pool with typed futures and exception propagation, beats std::async by reusing worker threads. | **C** | C++ | no license (study only) | 🟢 active |
| 10 | [**BS::thread_pool**](bshoshany-thread-pool.md) | Single-header C++17/20/23 thread pool that reuses worker threads to avoid std::thread's per-task creation overhead. | **D** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
