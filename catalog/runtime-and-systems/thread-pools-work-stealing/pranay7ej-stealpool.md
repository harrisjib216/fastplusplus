# stealpool

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Small C++17 work-stealing fork-join scheduler (Chase-Lev deques, eventcount parking). It beats a mutex-queue pool on fine-grained tasks.

| | |
|---|---|
| **Beats** | self-written central-queue thread pool (std::deque behind a mutex), serial code, and std::sort (not TBB/OpenMP/Rayon) |
| **Claimed result** | Best of 5 on a 4-vCPU GitHub runner: fib(36) cutoff 20 serial 28.5 ms, central queue 19.2 ms, stealpool 14.1 ms (2.02x vs serial, \~1.36x vs central queue derived from page data); unbalanced tree 90.6 / 25.7 / 23.4 ms (3.86x vs serial); 1M empty tasks central queue 526.2 ms vs stealpool 145.9 ms (3.6x); reduce 16M doubles 165.8 vs 56.4 ms (2.94x vs serial); parallel quicksort 20M ints 589 ms vs 1507 ms for std::sort. |
| **Workload** | fib(36) cutoff 20, unbalanced tree, 1M empty tasks, reduce 16M doubles, parallel quicksort 20M ints. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions runner, 4 vCPUs |
| **Adoption** | 0 stars |
| **Last commit** | 2024-05-04 |
| **Links** | [repository](https://github.com/Pranay7ej/stealpool) · [benchmark](https://github.com/Pranay7ej/stealpool) |

## Verdict

The CI bench job (CMake Release on an ubuntu-24.04 GitHub runner with 4 vCPUs, compiler version not printed, best of 5) reports stealpool against serial code and its own mutex-plus-std::deque pool. fib(36) with cutoff 20: 14.1 ms vs 19.2 ms central (about 1.36x, derived from page data) and 28.5 ms serial (2.02x). Unbalanced tree: 23.4 vs 25.7 vs 90.6 ms. 1M empty tasks: 145.9 vs 526.2 ms. 16M-double reduce: 56.4 vs 165.8 ms serial. Parallel quicksort on 20M ints: 589 ms vs 1507 ms for single-threaded std::sort. The fib and tree results are checked against the serial answers, and the quicksort output is compared with std::sort's.

## Use it when

- Reading or vendoring a compact, commented reference implementation of a Chase-Lev deque plus eventcount parking (about 600 lines of code)
- Recursive fork-join with many small tasks (fib-style recursion, quicksort, unbalanced trees) where a single mutex queue is the bottleneck: 3.6x faster than the central queue on 1M empty tasks at 4 threads
- Data-parallel loops via ParallelFor or ParallelReduce with a grain of about 1024 or more, measured 6x faster than spawning the same items in a flat loop
- Hobby or internal tools where you can accept unlicensed code only as a design reference

## Skip it when

- Anything you plan to ship or copy: there is no LICENSE file, so all rights are reserved by default and the code is reference only
- Production schedulers: it has 0 stars, 6 commits, no releases, and none of TBB's or Taskflow's features (priorities, affinity, cancellation)
- Task-heavy code where allocation matters: each task is a new/delete of a virtual FnTask, and the README names that as the main per-task cost with no per-worker allocator
- Comparisons against real schedulers: it was never benchmarked against TBB, OpenMP, Rayon, Taskflow or any catalogued sibling
- Long-running pools where a deque can grow very large: grown arrays are kept until the deque is destroyed

## How it is fast

Each worker owns a Chase-Lev deque (the C11 version from Le et al., PPoPP 2013, with seq_cst loads and stores in place of fences). The owner pushes and pops LIFO at the bottom and thieves steal FIFO from the top, so only the last element is contended, through one CAS. A waiting worker runs other tasks instead of blocking (help-first waiting), so recursive fork-join neither deadlocks nor idles. ParallelFor splits ranges recursively in halves, so a single steal takes half the remaining work. Idle workers spin 64 rounds and then park on an eventcount, which avoids lost wakeups.

## Compared with alternatives

Pick it only as a readable reference for the deque and parking logic. For real use pick citor, Fork Union or dp::thread_pool, which are licensed and benchmarked against TBB, OpenMP or other pools; Staccato and Nowa if you want published work-stealing comparisons against TBB and Cilk.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target stealpool from src/scheduler.cc plus include/stealpool/\*.h) |
| **Dependencies** | none (Threads); googletest v1.14.0 fetched for tests |
| **Minimum toolchain** | C++17, CMake 3.16; CI uses the ubuntu-24.04 runner's default compiler |
| **Platforms** | any platform with std::thread and C++17 atomics; CI runs Linux x86-64 only |
| **Thread safety** | Submit, Spawn and Async may be called from any thread (outside threads go through a mutex-protected injection queue). Each deque's Push and Pop are owner-only. Tests run under ASan and TSan with the suite repeated 20 times |
| **Drop-in for the baseline** | no |

## Gotchas

- Scheduler::Spawn tasks must not throw (the README says so). Only TaskGroup and Async capture exceptions
- While waiting, a worker runs any available task, not only its own group's, so deep recursion can stack unrelated tasks on one thread's stack (help-first waiting, no depth bound)
- Benchmark fairness: in bench.cc the central-queue baseline's Wait() also runs tasks on the main thread (5 threads), while stealpool's work runs inside sp.Async with the main thread blocked (4 workers). This favors the baseline. The quicksort example times a single run, includes Scheduler construction and thread start-up, and compares 4 threads against single-threaded std::sort
- Fib stops scaling at 2 threads (14.4 ms at 2, 14.1 ms at 4). The author guesses the 4 vCPUs are 2 physical cores with hyperthreading, which is unverified

## Known shortcomings

- Bench quirks that do not invalidate the numbers: the central-queue baseline's Wait() also runs tasks on the main thread (5 threads against stealpool's 4), which favours the baseline; the quicksort result is a single run whose timing includes scheduler start-up, against a single-threaded std::sort. All 6 commits are dated 2024-05-04 although ci.yml uses actions/checkout@v5, so the dates look inconsistent. No LICENSE. The CI bench job is CMake Release on ubuntu-24.04, compiler version not printed.

## Caveats and trade-offs

Baselines are a strawman mutex-queue pool, serial code and single-threaded std::sort; no comparison with TBB, OpenMP or Rayon. Noisy shared CI runner, compiler/flags not stated, std library not stated. No license file, so reference only. 0 stars, 6 commits; low-confidence data point.

C++17 Chase-Lev deque work-stealing scheduler, small hobby project.

## Maintenance

Stale (six commits all dated 2024-05-04, though the CI file uses actions/checkout@v5, so those dates look inconsistent) and unlicensed, so reference only; small and well tested under sanitizers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README table from the project's CI bench job (bench/ code public) on a 4-vCPU GitHub runner; no compiler, flags or CPU model, baselines are its own mutex-queue pool, serial code and std::sort.
- **Verifier notes:** Record's '2.02x fib over central queue' was wrong: 2.02x is vs serial; vs central queue it is \~1.36x. Tier unchanged at C; downgrade for the misattributed claim. No LICENSE file found (LICENSE, LICENSE.md, LICENSE.txt all 404).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compared_against_cpp_std_directly`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/Pranay7ej/stealpool>
  - <https://github.com/Pranay7ej/stealpool/commits>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Pranay7ej/stealpool>
  - <https://github.com/Pranay7ej/stealpool/commits/main>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/README.md>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/include/stealpool/deque.h>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/include/stealpool/scheduler.h>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/src/scheduler.cc>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/bench/bench.cc>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/examples/quicksort.cc>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Pranay7ej/stealpool/HEAD/.github/run_and_report.sh>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/pranay7ej/stealpool`) · [data/wave11/enrich/raw/github_com_pranay7ej_stealpool.json](../../../data/wave11/enrich/raw/github_com_pranay7ej_stealpool.json) (enrichment confidence 0.7)

</details>
