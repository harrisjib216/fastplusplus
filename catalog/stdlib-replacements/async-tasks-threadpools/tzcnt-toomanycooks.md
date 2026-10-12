# TooManyCooks (TMC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++20 coroutine thread pool with continuation-stealing scheduling; 1.1-3.8x faster than oneTBB on fork-join workloads.

| | |
|---|---|
| **Beats** | oneTBB (Intel/uxlfoundation Threading Building Blocks) |
| **Claimed result** | 3.77x faster than oneTBB on skynet (37,949us vs 142,887us); 1.79x on nqueens; 2.49x on fib(39); 1.12x on matmul(2048); mean-ratio-to-best across the four workloads: 1.32x (TMC) vs 3.25x (oneTBB) (derived from page data) |
| **Workload** | Recursive fork-join microbenchmarks (skynet 100M tasks, nqueens, fib(39), matmul(2048)) on a 64-core/64-thread AMD EPYC 7742 server, no SMT. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7742 64-core processor, 64 worker threads (no SMT), Debian 13 Server, linked against libtcmalloc_minimal.so.4 |
| **Compiler and flags** | Clang 21.1.7, Release, -O3 -march=native |
| **Adoption** | 281 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/tzcnt/TooManyCooks) · [benchmark](https://github.com/tzcnt/runtime-benchmarks) |

## Verdict

On a 64-core/64-thread AMD EPYC 7742 (Debian 13, Clang 21.1.7, -O3 -march=native, linked against libtcmalloc), TMC beat oneTBB by 3.77x on the skynet 100M-task benchmark (37,949us vs 142,887us), 1.79x on nqueens, 2.49x on fib(39), and 1.12x on matmul(2048), per the tzcnt/runtime-benchmarks suite that is maintained by TMC's own author but publishes reproducible code, compiler flags, and hardware specs.

## Use it when

- Recursive fork-join / divide-and-conquer workloads (skynet, nqueens, fib-style forking) on many-core machines (32-64+ threads) where oneTBB's per-task overhead dominates
- Codebase can standardize on C++20 coroutines and Clang 17+ (or GCC 14+ on Linux) for best codegen
- Need integrated async I/O (sockets, files, timers via Asio) alongside CPU task scheduling, not just a bare thread pool
- Want NUMA/topology-aware thread placement via hwloc on large multi-socket or many-core servers
- Fine vendoring a header-only library instead of linking a prebuilt TBB installation

## Skip it when

- Any code path that must build with MSVC: unsupported due to a documented compiler bug causing release-mode miscompilation (may run in Debug, crashes in Release)
- Workload is closer to matmul(2048)-style compute-bound with little forking, where the margin over oneTBB drops to \~1.1x - not worth an API rewrite
- Team can't or won't move to C++20 coroutines, or needs a signature-compatible replacement for std::async/std::thread
- Chasing best-in-class results specifically on this benchmark suite: citor (1.06x mean-ratio-to-best) and libfork (1.18x) beat TMC (1.32x) on the same four workloads
- Risk-averse on maturity: 281 stars, and a channel hazard-pointer crash was reported and only worked around (not code-fixed) as of August 2026

## How it is fast

Each worker owns a Chase-Lev lock-free work-stealing deque (own thread pushes/pops the tail, other threads steal from the head, buffer doubles on growth); when a coroutine's continuation is ready, the same worker keeps running it instead of handing back to a generic scheduler loop (continuation-stealing), avoiding round-trips through a central queue. Per-thread inboxes and a priority-bitmap scheduler reduce contention for load balancing, and hwloc integration lets thread placement follow real cache/NUMA topology on many-core servers.

## Compared with alternatives

Pick TMC over dispenso or Taskflow when the workload is naturally coroutine-shaped (co_await-driven recursive fork-join) and you also want built-in async I/O in the same runtime; libfork slightly beats TMC on this exact benchmark suite's mean ratio (1.18x vs 1.32x) if you don't need channels/Asio integration, so prefer libfork for pure recursive-task speed and TMC when the fuller feature set (channels, priorities, I/O) matters more than the last \~10% of throughput.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | hwloc (optional, required by default in the CMake target; disable with TMC_USE_HWLOC=OFF); Asio or Boost.Asio (only needed for the tmc/asio/\* network/file I/O headers) |
| **Minimum toolchain** | C++20 coroutines; Linux: Clang 17+ (recommended) or GCC 14+, kernel 5.16+ for futex_waitv; Windows: clang-cl 17+ (MSVC unsupported); macOS: Apple Clang 17+ with -fexperimental-library |
| **Platforms** | x86 (32/64-bit), AArch64, LoongArch LA64, riscv64 |
| **Thread safety** | The ex_cpu executor accepts concurrent task submission from any thread. Async data structures like channel are safe across distinct token copies, but a single token instance is not thread-safe - each concurrent task/thread needs its own token copy. |
| **Drop-in for the baseline** | partial — conceptually replaces oneTBB's task_group/flow-graph scheduling, but requires rewriting call sites to the coroutine-based tmc::task&lt;T&gt;/co_await API rather than a signature-compatible swap |

## Gotchas

- Per the project's own version notes, minor version bumps (not just majors) may include breaking API changes - pin a version rather than tracking main
- channel.hpp hazard-pointer issue reported in issue #275 (Aug 2026): reusing or sharing a single chan_tok across tasks/threads caused intermittent crashes; the maintainer's fix is disciplined per-task token copies, not a code patch, and a separate stale-hazard-pointer soundness edge case (extremely long token idle time) is acknowledged as theoretically possible but undocumented
- hwloc is a required dependency by default under the CMake target; must explicitly pass TMC_USE_HWLOC=OFF to drop it
- MSVC builds can appear to work in Debug but crash in Release due to a compiler thread_local-caching bug - do not rely on MSVC even for prototyping

## Caveats and trade-offs

The benchmark suite (tzcnt/runtime-benchmarks, 36 stars) is maintained by the TooManyCooks author, so it is not a fully independent third party, though its code, compiler, flags and CPU model are public and reproducible. GitHub reports the suite's license as NOASSERTION, but its LICENSE file is the Unlicense. TMC does not top this shootout: citor (1.06x) and libfork (1.18x) have better mean-ratio-to-best than TMC (1.32x). The baseline beaten is oneTBB, not std::async/std::thread/std::future. No head-to-head benchmark against raw std::async/std::thread was found for this project.

Requires C++20 coroutines; Clang recommended (best coroutine codegen), MSVC unsupported due to a compiler bug; optional hwloc dependency for NUMA-aware scheduling; steeper API than std::async.

## Maintenance

Actively maintained (commit as recent as 2026-09-22, currently v1.7.0) and BSL-1.0 licensed with Conan/vcpkg packaging, but still young (281 stars) - a channel hazard-pointer crash was still being triaged via GitHub issue as recently as August 2026, and the header-only form makes it cheap to vendor a pinned version if that matters.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The runtime-benchmarks README summary table has TooManyCooks and tbb columns with the exact numbers claimed. The benchmark code is public (cpp/TooManyCooks/\*.cpp vs cpp/tbb/\*.cpp, driven by build_and_bench_all.py). Compiler (Clang 21.1.7), flags (-O3 -march=native) and CPU (EPYC 7742) are all stated.
- **Verifier notes:** All four ratios and the mean-ratio figures match the TooManyCooks row and the tbb row. Metadata matches: BSL-1.0, 281 stars, last commit 2026-09-22, active. The only fix is the runtime-benchmarks license in caveats: the LICENSE file is the Unlicense, not an unidentified license.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tzcnt/runtime-benchmarks>
  - <https://github.com/tzcnt/runtime-benchmarks/blob/main/LICENSE>
  - <https://github.com/tzcnt/TooManyCooks>
- **Sources the enricher read:**
  - <https://github.com/tzcnt/TooManyCooks>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/README.md>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/include/tmc/ex_cpu.hpp>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/include/tmc/detail/qu_chase_lev64.hpp>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/include/tmc/version.hpp>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/include/tmc/channel.hpp>
  - <https://github.com/tzcnt/TooManyCooks/blob/main/LICENSE>
  - <https://github.com/tzcnt/TooManyCooks/issues>
  - <https://github.com/tzcnt/TooManyCooks/issues/275>
  - <https://github.com/tzcnt/runtime-benchmarks>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/tzcnt/toomanycooks`) · [data/wave1/enrich/raw/github_com_tzcnt_toomanycooks.json](../../../data/wave1/enrich/raw/github_com_tzcnt_toomanycooks.json) (enrichment confidence 0.85)

</details>
