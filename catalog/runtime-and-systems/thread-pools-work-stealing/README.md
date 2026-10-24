# Thread pools and work stealing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** Intel TBB, OpenMP, Rayon  
**25 entries:** 5 tier A · 3 tier B · 13 tier C · 4 tier D · 23 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Intel Parallel STL**](intel-parallelstl.md) | Intel's C++17 parallel algorithms (now oneDPL; libstdc++'s &lt;execution&gt;): std::reduce(par) on oneTBB beats serial std::accumulate \~98x. | **A** | C++ | Apache-2.0 WITH… | 🟢 active |
| 2 | [**citor**](lallapallooza-citor.md) | Header-only C++20 thread pool with Chase-Lev fork-join and sub-microsecond parallelFor; tops oneTBB and Taskflow on recursive fork-join. | **A** | C++ | MIT | 🟢 active |
| 3 | [**nexus**](huxint-nexus.md) | Header-only C++26 work-stealing thread pool with about 3x to 7x lower scheduling overhead than Taskflow and BS::thread_pool on tiny tasks. | **A** | C++ | MIT | 🟢 active |
| 4 | [**ThunderBolt-HT**](ankitlinkesh-thunderbolt-ht.md) | C++20 dependency-aware work-stealing task runtime that measures \~1.5x lower per-task cost than Taskflow 3.7 on a 4-core laptop. | **A** | C++ | Apache-2.0 | 🟢 active |
| 5 | [**concurrencpp**](david-haim-concurrencpp.md) | C++20 coroutine task/executor framework whose thread pool beats libcoro on fork-join, but trails TBB by about 90x. | **A** | C++ | MIT | 🔴 abandoned |
| 6 | [**OpenCilk (opencilk-project)**](opencilk-opencilk-project.md) | LLVM/Clang fork compiling Cilk fork-join C/C++ onto a work-stealing runtime; paper reports beating oneTBB, OpenMP and Cilk Plus runtimes. | **B** | C++ | Apache-2.0 WITH… | 🟢 active |
| 7 | [**NVthreads**](hewlettpackard-nvthreads.md) | pthreads replacement that makes lock-based C/C++ programs crash-consistent on NVM; beats Atlas and Mnemosyne, slower than pthreads. | **B** | C/C++ | GPL-2.0 | 🔴 abandoned |
| 8 | [**Nowa**](black7375-nowa.md) | Research C runtime for wait-free continuation-stealing fork/join, reported faster than lock-based Cilk Plus/TBB and OpenMP tasks. | **B** | C | MIT | 🔴 abandoned |
| 9 | [**Rayon**](rayon-rs-rayon.md) | Rust work-stealing data-parallelism crate (par_iter, join, scope); beats OpenMP only in fine-grained dynamic-schedule cells of a competitor's benchmark. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 10 | [**Kokkos**](kokkos-kokkos.md) | Performance-portability programming model (Views plus parallel dispatch); a Kokkos PIC port beat its OpenMP variant 1.4-1.6x on Xeon. | **C** | C++ | Apache-2.0 WITH… | 🟢 active |
| 11 | [**Spice**](judofyr-spice.md) | Zig fork/join library using heartbeat scheduling; sub-nanosecond fork/join overhead versus Rayon's \~15 ns per join. | **C** | Zig | 0BSD | 🟢 active |
| 12 | [**Fork Union**](ashvardanian-fork-union.md) | NUMA-aware fork-join thread pool for C++/C/Rust/Zig with lower parallel-for dispatch latency than OpenMP, Rayon and Taskflow. | **C** | C++ | Apache-2.0 | 🟢 active |
| 13 | [**chili**](dragostis-chili.md) | Rust port of Spice: heartbeat-scheduled fork-join join() with far lower per-join overhead than rayon::join on fine-grained recursion. | **C** | Rust | MIT OR Apache-2.0 | 🟡 stale |
| 14 | [**Weave**](mratsim-weave.md) | Nim task- and data-parallel runtime that uses message-passing work-requesting; claims 3-10x less scheduling overhead than TBB and GCC OpenMP. | **C** | Nim | MIT OR Apache-2.0 | 🟡 stale |
| 15 | [**Scheduling (dpuyda)**](dpuyda-scheduling.md) | Header-only C++20 work-stealing thread pool and task-graph runner, under 600 lines, benchmarked faster than Taskflow on fine-grained tasks. | **C** | C++ | MIT OR Apache-2.0 | 🟡 stale |
| 16 | [**poolSTL**](alugowski-poolstl.md) | Header-only thread-pool implementation of the C++17 parallel algorithms; about 5x over sequential and roughly on par with TBB-backed std::execution::par. | **C** | C++ | BSD-2-Clause OR BSL-1.0 OR… | 🟡 stale |
| 17 | [**inkooboo/thread-pool-cpp**](inkooboo-thread-pool-cpp.md) | Header-only C++11 thread pool with per-worker Vyukov MPMC queues; reposts jobs about 20x faster than an asio io_service pool. | **C** | C++ | MIT (MPMCBoundedQueue is… | 🔴 abandoned |
| 18 | [**riften::Thiefpool (ConorWilliams/Threadpool)**](conorwilliams-threadpool.md) | Small C++20 work-stealing thread pool on Chase-Lev deques; about 8% faster than BS::thread_pool in one third-party matmul benchmark. | **C** | C++ | MPL-2.0 | 🔴 abandoned |
| 19 | [**Staccato**](rkuchumov-staccato.md) | Header-only C++11 work-stealing scheduler storing task objects inside its deques; lower spawn overhead than TBB 4.3 and Cilk Plus. | **C** | C++ | MIT | 🔴 abandoned |
| 20 | [**stealpool**](pranay7ej-stealpool.md) | Small C++17 work-stealing fork-join scheduler (Chase-Lev deques, eventcount parking). It beats a mutex-queue pool on fine-grained tasks. | **C** | C++ | no license (study only) | 🟡 stale |
| 21 | [**Heartbeat Scheduling (deepsea-inria/heartbeat)**](deepsea-inria-heartbeat.md) | Research prototype of Heartbeat Scheduling (PLDI 2018): amortizes task creation against Cilk Plus-style eager spawning without manual grain-size tuning. | **C** | C++ | no license (study only) | 🔴 abandoned |
| 22 | [**dp::thread_pool (DeveloperPaul123/thread-pool)**](developerpaul123-thread-pool.md) | Header-only C++20 thread pool with per-worker mutex queues and stealing; first-party bench shows \~7% over BS::thread_pool 3.5. | **D** | C++ | MIT | 🟢 active |
| 23 | [**Lace (trolando)**](trolando-lace.md) | C11 fork-join work-stealing runtime (split deque, leapfrogging) from the Sylvan BDD author; claims Wool-level overhead, no reproducible numbers against TBB, Cilk or… | **D** | C | Apache-2.0 | 🟢 active |
| 24 | [**ThreadPool (progschj)**](progschj-threadpool.md) | Single-header C++11 fixed-size thread pool returning futures; not shown to beat std::async thread-per-task overall. | **D** | C++ | Zlib | 🔴 abandoned |
| 25 | [**FastThreadPool (komrad36)**](komrad36-fastthreadpool.md) | 183-line header: an unbounded MPMC work queue of plain function pointers with spin-bit locking; no benchmark against any thread pool. | **D** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
