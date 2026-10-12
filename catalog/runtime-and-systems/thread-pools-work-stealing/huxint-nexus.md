# nexus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++26 work-stealing thread pool with about 3x to 7x lower scheduling overhead than Taskflow and BS::thread_pool on tiny tasks.

| | |
|---|---|
| **Beats** | Taskflow, BS::thread_pool |
| **Claimed result** | README table (8 workers, best of three): fire-and-forget 8.39 M tasks/s vs Taskflow 1.24 and BS::thread_pool 0.40; submit-and-get 2.09 vs 0.38 and 0.27; recursive fork-join 28.40 M leaf tasks/s vs 8.62 and 1.23; 8x multi-producer 7.60 vs 2.76 and 1.36; round-trip P50/P99 0.44/0.87 us vs Taskflow 2.66/7.44 and BS 3.75/6.01. docs/build.md extended run vs oneTBB: fire-and-forget 8.40 vs 3.65, fork-join 27.39 vs 25.69 (about 1.07x, derived from page data), multi-producer 7.31 vs 6.53. |
| **Workload** | Single-producer fire-and-forget, submit-and-get, recursive fork-join leaf tasks, 8x multi-producer, and round-trip latency, with 8 workers. |
| **Metric** | throughput |
| **Hardware** | Intel i7-12650H, 8 worker threads |
| **Compiler and flags** | GCC 16.2.1, C++26, CMake Release (-O3 -DNDEBUG) plus -fcontracts -fcontract-evaluation-semantic=ignore and -Wall -Wextra -Wshadow from CMakeLists.txt; no -march |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/huxint/nexus) · [benchmark](https://raw.githubusercontent.com/huxint/nexus/HEAD/docs/build.md) |

## Verdict

The author ran benchmarks/bench.cpp on an Intel i7-12650H with 8 workers, GCC 16.2.1, CMake Release (-O3, no -march), taking the best of three runs on 2026-09-30. nexus reached 8.39 M tasks/s single-producer fire-and-forget vs Taskflow 1.24 and BS::thread_pool 0.40, 28.40 vs 8.62 vs 1.23 M leaves/s on depth-18 fork-join, and P50/P99 round trip 0.44/0.87 us vs 2.66/7.44 and 3.75/6.01. The same run against oneTBB was much closer (fork-join 27.39 vs 25.69, 8-producer 7.31 vs 6.53), and on a compute-bound workload at 4 threads nexus was slower than Taskflow.

## Use it when

- Many sub-microsecond tasks where per-task scheduling cost dominates, such as fire-and-forget event fan-out (8.39 M tasks/s vs Taskflow 1.24 in the author's run).
- Latency-sensitive submit-then-wait round trips on a pool kept warm: P50 0.44 us vs 2.66 us (Taskflow) when workers are still spinning.
- Recursive divide-and-conquer with tiny leaves, where it roughly matches oneTBB (27.39 vs 25.69 M leaves/s) and beats Taskflow about 3x.
- New C++26 codebases on GCC 16.2+ that want std::expected-based error handling, no exceptions escaping fire-and-forget tasks, and optional priorities or cancellation.

## Skip it when

- Anything not on GCC 16.2+ with -std=c++26 -fcontracts: Clang, MSVC and older GCC are not supported (it uses contracts and &lt;inplace_vector&gt;).
- Compute-bound chunks: the author's own fixed-workload test at 4 threads has nexus at 3.26 ms vs Taskflow 2.59 ms (slower).
- Sparse or bursty service traffic on shared machines: the 64 us spin budget keeps idle workers burning cores, and the latency win depends on it (lower spin_budget for such pools).
- Task-graph dependencies (Taskflow's DAG model) or production use that needs maturity: the project is about one month old (first commit 2026-08-27), has 1 star and its docs are in Chinese only.

## How it is fast

Each worker has a Chase-Lev work-stealing deque. External submissions go to a bounded global MPMC ring with an overflow chain, and task nodes come from per-thread node caches, so the hot path avoids allocation. Submit/complete accounting is sharded per thread on separate cache lines. Idle workers spin for a time budget (64 us by default) before sleeping on a futex-style atomic wait, and a wake wakes one sleeper only when no spinner is active. fork_join is work-first: it enqueues one branch and runs the other inline.

## Compared with alternatives

Pick nexus over dpuyda/scheduling or ThunderBolt-HT when you also want futures, combinators and priorities on top of low-overhead stealing; pick Fork Union or citor for parallel-for dispatch on large many-core machines, and oneTBB when you need a mature, portable runtime (nexus's fork-join lead over it is only about 7%).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Threads; optional oneTBB, Taskflow and stdexec for benchmarks and tests) |
| **Minimum toolchain** | C++26, GCC 16.2+, CMake 3.28+ with Ninja for the CMake build; -fcontracts is required at compile and link time |
| **Platforms** | Not documented beyond the author's Linux x86-64 run (i7-12650H); uses standard atomics and std::jthread only |
| **Thread safety** | submit/execute are safe from any thread, including workers (nested submits go to the local deque); pool wait()/shutdown() must not be called from inside a pool task (deadlock, contract-checked in Debug) |
| **Drop-in for the baseline** | no |

## Gotchas

- execute() and the f branch of fork_join require noexcept callables; submit() routes exceptions into the expected result channel, and a successful result can be taken only once.
- fork_join does not join: both branches stay in flight after it returns, and you sync with pool wait() or your own counter, as the benchmark does with an atomic leaf count.
- The constructor may throw on thread creation; pool::try_create() is the no-throw path. The default queue_cap is 65536 global / 256 local, and full rings spill into an overflow chain rather than rejecting work.
- The benchmarks time empty tasks that bump one shared atomic counter, so they measure scheduler overhead, not useful throughput; 8 producers plus 8 workers on a 10-core/16-thread laptop also oversubscribe it.

## Known shortcomings

- The workloads are empty tasks plus one shared atomic counter, so they measure scheduler overhead only. The latency win relies on the default 64 us spin_budget (idle workers burn cores); 8 producers plus 8 workers oversubscribe the 10-core i7-12650H; the compute-bound test at 4 threads is slower than Taskflow (3.26 vs 2.59 ms). Needs GCC 16.2+ with -fcontracts. Project about 1 month old (first commit 2026-08-27, 34 commits).

## Caveats and trade-offs

First-party, best of three runs on one laptop CPU (i7-12650H), README and docs in Chinese. A oneTBB comparison does exist in docs/build.md (oneTBB linked only if found at configure time): nexus leads clearly on fire-and-forget but only about 7% on recursive fork-join and 12% on multi-producer. The workloads hit a shared atomic counter, so they mostly measure scheduling overhead; docs/build.md says that on a fixed compute workload at 4 threads nexus takes 3.26 ms vs Taskflow 2.59 ms (slower). Requires GCC 16.2+ with C++26 contracts. Very new project with 1 star.

C++26 and GCC 16.2+ required; header-only, work stealing plus lock-free MPMC, P2300 scheduler compatible.

## Maintenance

Active (34 commits from 2026-08-27 to 2026-09-30) and MIT-licensed header-only code that is easy to vendor, but it is very young, has a single author and needs a bleeding-edge GCC 16.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: benchmark code is public (benchmarks/bench.cpp, driven as ./build/nexus_bench per docs/build.md), compiler GCC 16.2.1, CPU Intel i7-12650H, and flags are derivable from the public CMakeLists.txt (CMake Release, i.e. -O3 -DNDEBUG, plus -fcontracts -fcontract-evaluation-semantic=ignore, no -march), as with the lzbench Makefile-flags precedent. Numbers are first-party, best of three runs.
- **Verifier notes:** README numbers match exactly. Record caveat claiming no oneTBB row was wrong; docs/build.md has one. Metadata (MIT, 1 star, not a fork, active) confirmed on the github.com page and the LICENSE file; last commit date taken from the record (benchmark dated 2026-09-30), not re-checked commit by commit.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/README.md>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/LICENSE>
  - <https://github.com/huxint/nexus>
  - <https://github.com/huxint/nexus/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/README.md>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/docs/api.md>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/benchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/include/nexus/pool.hpp>
  - <https://raw.githubusercontent.com/huxint/nexus/HEAD/include/nexus/execution.hpp>
  - <https://github.com/huxint/nexus/tree/main/include/nexus>
  - <https://github.com/huxint/nexus/commits/main>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/huxint/nexus`) · [data/wave11/enrich/raw/github_com_huxint_nexus.json](../../../data/wave11/enrich/raw/github_com_huxint_nexus.json) (enrichment confidence 0.75)

</details>
