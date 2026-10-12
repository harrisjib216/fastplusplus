# libfork

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only C++20/23 coroutine fork-join library beating oneTBB and OpenMP on fine-grained task throughput and memory.

| | |
|---|---|
| **Beats** | oneTBB (Intel Threading Building Blocks) and OpenMP (libomp) |
| **Claimed result** | Paper conclusion: up to 7.5x faster and 19x less memory than oneTBB, up to 24x faster and 24x less memory than OpenMP (libomp), and up to 100x faster and several orders of magnitude less memory than taskflow. The 7.5x/24x peaks are for fib at 112 cores; integrate gives 4.5x vs TBB and 14x vs OpenMP. Abstract averages: 2.7x faster and 6.2x less memory than TBB; 7.2x faster and 10x less memory than libomp. |
| **Workload** | Fork-join benchmarks: recursive fib(42), numerical integration, matmul, nqueens(14), and UTS geometric (T1L, T1XXL) and binomial (T3L, T3XXL) trees. Execution time (Google Benchmark, median of 5 runs) and peak RSS (GNU time) are measured, swept over 1-112 cores. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon Platinum 8480+ (2.0 GHz, boost to 3.8 GHz), 112 cores across 2 NUMA nodes, 500 GiB RAM |
| **Compiler and flags** | Clang 18.0.0 (LLVM commit c4b795df) at the 'highest optimization setting' with runtime asserts disabled (exact flag string not listed). Uses libomp bundled with Clang, TBB 2021.10.0, taskflow 3.6.0 and libfork 3.5.0. |
| **Adoption** | 901 stars; also appears as a top performer (1.18x mean ratio to best) in the independent tzcnt/runtime-benchmarks shootout |
| **Last commit** | 2026-01-17 |
| **Links** | [repository](https://github.com/ConorWilliams/libfork) · [benchmark](https://arxiv.org/abs/2402.18480) |

## Verdict

The arXiv:2402.18480 preprint (Williams & Elliott) benchmarked libfork 3.5.0 against oneTBB 2021.10.0, Clang-bundled OpenMP/libomp, and Taskflow 3.6.0 on fib(42), integration, matmul, nqueens(14), and UTS tree-search, compiled with Clang 18.0.0 at the paper's 'highest optimization setting,' on 2x Intel Xeon Platinum 8480+ (112 cores, 2 NUMA nodes, 500GiB RAM), swept from 1-112 cores. Abstract-stated averages are 2.7x faster / 6.2x less memory than oneTBB and 7.2x faster / 10x less memory than OpenMP; the frequently quoted 7.5x/19x (vs TBB) and 24x/24x (vs OpenMP) figures are peak ratios on the fib benchmark specifically at 112 cores, not typical-case numbers.

## Use it when

- Very fine-grained recursive divide-and-conquer workloads (fib-style, tree search, numerical integration) where oneTBB/OpenMP per-task overhead dominates runtime
- Codebases willing to rewrite hot-path functions as C++20 coroutines (lf::task&lt;T&gt;) rather than keep existing std::async/TBB/OpenMP call sites unchanged
- Multi-socket/NUMA machines with high core counts (paper benchmarked 1-112 cores, 2 NUMA nodes) where linear time/memory scaling matters
- Workloads where peak RSS is as important as speed - libfork's memory footprint was measured far below TBB/OpenMP/Taskflow on the UTS tree-search benchmark
- Projects that can pin a recent compiler (current main requires C++23 per CMakeLists) via CMake, vcpkg, or Conan

## Skip it when

- Any deployment target still on MSVC: BUILDING.md states libfork compiles on MSVC 19.35-19.37 but seg-faults at runtime due to an open Visual Studio symmetric-transfer/coroutine codegen bug
- Coarser-grained parallel loops: a real integration into BLIS's GEMM (issue #113) showed libfork's busy_pool at only 55% of OpenMP's GFLOPS at matrix dim=512, only beating OpenMP once dim &gt;= 2048, partly because libfork lacks a flat bulk-spawn/parallel_invoke API
- Teams unwilling to convert call sites to coroutine-returning lf::task&lt;T&gt; and to handle its exception_before_join + rethrow-on-join exception model
- Older/unpatched compilers: Clang &lt;=16 needs a thread_local workaround with a performance penalty, and GCC below -O2 can stack-overflow because it doesn't guarantee coroutine symmetric-transfer tail calls
- Anyone requiring peer-reviewed evidence: the only performance writeup is an arXiv v1 preprint (Feb 2024) with no journal/conference publication, and its headline 'up to' ratios are peak fib/integrate figures at 112 cores, well above the abstract's stated averages (2.7x/7.2x)

## How it is fast

A continuation-stealing work-stealing scheduler lets the worker that forks a task keep running the child immediately while only the continuation is exposed to be stolen, minimizing deque traffic on the common path. Coroutine frames are placed on an (almost) non-allocating 'cactus stack' built from segmented stacks instead of being heap-allocated per task, giving fork/call overhead about 10x a bare function call. NUMA-aware pools (optionally using hwloc for topology detection) reduce cross-socket stealing cost, which the paper credits for near-linear time and memory scaling up to 112 cores.

## Compared with alternatives

Pick libfork over TooManyCooks/dispenso/Taskflow when the workload is extremely fine-grained recursive fork-join (fib-like or UTS-style tree search) run across dozens to 100+ cores and peak memory matters as much as latency; TMC and dispenso report comparable 'beats oneTBB' wins with a simpler non-coroutine API and less compiler sensitivity, so prefer them if you don't want to rewrite call sites as C++20/23 coroutines or can't guarantee a modern compiler.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required beyond a compiler and Threads; optional hwloc &gt;=2.5.0 for NUMA topology detection (LF_USE_HWLOC) |
| **Minimum toolchain** | C++20 per docs (C++23 preferred); current main CMakeLists.txt sets target_compile_features(... cxx_std_23) on the library interface target. Compiler support table: Clang 15-18 (16 and below need a thread_local workaround with a perf penalty due to LLVM bugs #63022/#47179), GCC 11-13 (needs &gt;= -O2 for guaranteed coroutine tail calls), Apple Clang (Xcode-shipped, with the same old-Clang mitigations), MSVC 19.35-19.37 compiles but seg-faults at runtime |
| **Platforms** | Linux, macOS, Windows CI configured (linux.yml/macos.yml/windows.yml), any arch with a conforming C++20/23 coroutine compiler; NUMA-aware scheduling is opt-in via hwloc |
| **Thread safety** | not documented as a single formal guarantee; README describes the core as 'lock-free, wait-free, continuation-stealing'; schedulers (lazy_pool/busy_pool) are multi-threaded work-stealing pools meant for concurrent task submission, and lf::sync_wait blocks the calling thread until the pool drains |
| **Drop-in for the baseline** | false - requires rewriting functions as C++20 coroutines returning lf::task&lt;T&gt; using lf::fork/lf::call/lf::join instead of oneTBB task_group calls or OpenMP pragmas |

## Gotchas

- Strict fork-join is enforced: every forked/called child must be joined with co_await lf::join before the parent task returns - there is no fire-and-forget
- Exceptions from a child surfaced before the join point arrive as exception_before_join; you must catch it and still call join, which then rethrows the child's real exception (include/libfork/core/exceptions.hpp)
- Current main branch requires C++23 (cxx_std_23 in CMakeLists.txt) even though the README/BUILDING.md prose still advertises 'C++20 coroutines' - check your compiler before adopting HEAD
- MSVC builds compile but crash at runtime (known upstream MSVC coroutine codegen bug); do not ship an MSVC build without testing

## Caveats and trade-offs

arXiv preprint (v1, 28 Feb 2024) with no journal or conference reference listed. The 'up to' headline figures are peak ratios on the very fine-grained fib/integrate benchmarks at 112 cores. The averages in the abstract are lower: 2.7x vs TBB, 7.2x vs libomp. The paper describes flags only as 'highest optimization setting'. Independent corroboration with explicit -O3 -march=native comes from tzcnt/runtime-benchmarks, where libfork beats tbb 1.14x-3.9x. The baseline beaten is oneTBB/OpenMP/Taskflow, not std::async/std::thread/std::future.

C++20 coroutines only, portability/compiler-bug workarounds needed on some Clang/GCC/MSVC versions; NUMA-aware scheduler adds complexity vs a plain std::async call.

## Maintenance

Actively maintained - default-branch last commit 2026-01-17 - and header-only/copyable under MPL-2.0, so it can be vendored without a package manager, but current HEAD needs a C++23-capable compiler, MSVC support is presently broken at runtime, and the last tagged release (v3.8.0) is from 2024-05-10 with substantial unreleased work since.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The paper's methodology (Sec. V-A) names 2x Xeon Platinum 8480+ (112 cores), Clang 18.0.0 at the highest optimization setting with asserts disabled, and pinned library versions. The artifact code is in libfork bench/source/{fib,integrate,matmul,nqueens,uts}/{libfork,tbb,omp,taskflow}.cpp. The independent tzcnt/runtime-benchmarks suite (Clang 21.1.7 -O3 -march=native, EPYC 7742) corroborates it with explicit flags: libfork 36,519us vs tbb 142,887us on skynet.
- **Verifier notes:** The record's 'up to' numbers are verbatim from the paper's conclusion (and the README). Hardware and compiler were in the PDF, which was the reason for the earlier Tier C cap, so the tier moves up to A. The default-branch (main) last commit is 2026-01-17; pushed_at 2026-05-25 reflects non-default branches (dev-v4, modules, etc.). It is still active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2402.18480>
  - <https://arxiv.org/pdf/2402.18480>
  - <https://github.com/ConorWilliams/libfork>
  - <https://github.com/tzcnt/runtime-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/ConorWilliams/libfork>
  - <https://github.com/ConorWilliams/libfork/blob/main/README.md>
  - <https://github.com/ConorWilliams/libfork/blob/main/BUILDING.md>
  - <https://github.com/ConorWilliams/libfork/blob/main/vcpkg.json>
  - <https://github.com/ConorWilliams/libfork/blob/main/CMakeLists.txt>
  - <https://github.com/ConorWilliams/libfork/blob/main/include/libfork/core/exceptions.hpp>
  - <https://github.com/ConorWilliams/libfork/blob/main/docs/api/schedule.rst>
  - <https://github.com/ConorWilliams/libfork/issues/113>
  - <https://github.com/ConorWilliams/libfork/releases>
  - <https://github.com/ConorWilliams/libfork/tags>
  - <https://arxiv.org/abs/2402.18480>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/conorwilliams/libfork`) · [data/wave1/enrich/raw/github_com_conorwilliams_libfork.json](../../../data/wave1/enrich/raw/github_com_conorwilliams_libfork.json) (enrichment confidence 0.75)

</details>
