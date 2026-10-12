# Lace (trolando)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `Apache-2.0` · 🟢 active

> C11 fork-join work-stealing runtime (split deque, leapfrogging) from the Sylvan BDD author; claims Wool-level overhead, no reproducible numbers against TBB, Cilk or OpenMP.

| | |
|---|---|
| **Beats** | Intel TBB, Cilk Plus (Cilk++), OpenMP and Wool (Wool is the parity target, not a claimed loss) |
| **Claimed result** | No numbers seen. Paper abstract (search snippet): the split deque and the private-deque variant implemented in Lace have 'similar low overhead and high scalability as Wool', i.e. parity with Wool, not faster. Third-party 2020 University of Twente thesis (search snippet): on Unbalanced Tree Search, Fibonacci and Strassen, Lace performs best, CilkPlus and TBB intermediate, OpenMP worst by far; no figures seen. |
| **Workload** | Fine-grained fork-join benchmarks (fib, UTS, N-Queens, matmul, strassen, cilksort and others from the Cilk-5 suite) timed on multi-core machines; the exact paper table was not seen. |
| **Metric** | throughput |
| **Compiler and flags** | Repo benchmarks (benchmarks/CMakeLists.txt): C11/C++11, Release builds add -flto, optional -march=native via LACE_NATIVE_OPT; the paper's flags were not seen |
| **Adoption** | 61 stars; README cites the author's Sylvan multi-core decision diagram thesis as a user |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/trolando/lace) |

## Verdict

No reproducible comparison exists: the repo's bench.py and benchmarks/CMakeLists.txt build only Lace and sequential versions of the Cilk-5/Nowa-derived programs, the Euro-Par 2014 paper claims only parity with Wool (abstract seen as a snippet), and the 2020 Twente essay ranking Lace ahead of Cilk Plus, TBB and OpenMP on UTS, Fibonacci and Strassen was seen only as a snippet. The only numbers seen are informal ones in issue #7 (2022, Lace v1, 6 threads, CPU and compiler not stated): fib(41) 0.188 s for Lace against 2.663 s for Weave with eager heap-allocated futures, and N-Queens 15 at 23.01 s against Weave's 24365.96 printed under a 'Time(us)' label that the author read as 24.37 s; the Weave author's own 18-core i9-9980XE rerun reported '2x to 2.5x faster on nqueens but 2.5x to 10x slower on fibonacci' without naming the subject, and noted that Weave's lazy futures cut the fib overhead.

## Use it when

- Recursive divide-and-conquer in C or C++ with very small tasks (fib-style spawn/sync, tree or decision-diagram traversal, UTS, N-Queens, recursive matmul) where per-task overhead dominates.
- Programs that cannot rely on a Cilk compiler (OpenCilk) or on TBB but want Cilk-style SPAWN/SYNC on GCC, Clang or MSVC across Linux, macOS, Windows and FreeBSD.
- Long-running parallel engines that need stop-the-world points: NAME_NEWFRAME suspends all workers to run one task (e.g. garbage collection, table resize) and NAME_TOGETHER runs a copy on every worker, as Sylvan uses them.
- Multi-socket machines where you can enable LACE_USE_HWLOC so workers are pinned and their stacks and deques are NUMA-local.

## Skip it when

- General task-pool needs (fire-and-forget jobs, futures that escape their scope, async I/O, parallel_for over ranges): use TBB, Taskflow or a thread pool instead.
- Processes that share cores with other parallel runtimes or need an elastic worker count: the pool size is fixed at lace_start, changing it means stop and restart (issue #9), and the author says it targets research programs running alone on a large machine.
- Unbounded or very deep spawn chains: each worker's deque defaults to 100,000 slots and overflow terminates the process; worker stacks are clamped to 16-64 MB.
- Tasks whose arguments plus result exceed 48 bytes (lace.h), 16 bytes (lace32.h) or 112 bytes (lace128.h); larger data must be passed by pointer.
- Choosing on proven speed: no repo, paper or third-party table opened here shows Lace beating TBB, Cilk Plus or OpenMP with numbers.

## How it is fast

Each worker owns a split deque (van Dijk and van de Pol, Euro-Par 2014 workshops): the owner pushes and pops the private end wait-free with no atomics on the SYNC fast path, thieves CAS a packed 64-bit tail/split word, and the split point moves only on request (a movesplit flag), so fences are needed only when the shared part shrinks. Tasks live in fixed-size 32/64/128-byte deque slots instead of heap objects, and a worker whose stolen task is not finished steals back from the thief (leapfrogging) instead of blocking. Idle workers yield for 256 attempts, then futex-sleep with a 100 us to 1 ms ramp, and a per-worker bump arena replaces malloc and alloca for task-local scratch memory.

## Compared with alternatives

Pick Lace over OpenCilk when you cannot switch compilers but want the same spawn/sync model in plain C, and over Staccato or Weave when you need C (not C++ templates or Nim) plus stop-the-world NEWFRAME/TOGETHER interrupts and NUMA pinning; pick Staccato, Nowa or OpenCilk if you want a published comparison against TBB and Cilk Plus with numbers, which Lace's repo does not provide.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake targets lace::lace, lace::lace32, lace::lace128; shared build possible but warned against) |
| **Dependencies** | pthreads (or Windows threads); optional hwloc; Synchronization.lib on Windows |
| **Minimum toolchain** | C11 compiler (GCC, Clang, or MSVC with /experimental:c11atomics); CMake 3.23 per CMakeLists.txt (the getting-started page still says 3.15); header also compiles as C++ (benchmarks build fib-lace.cpp as C++11) |
| **Platforms** | Linux, macOS (os_sync wait/wake on 14.4+, __ulock below), Windows 8+, FreeBSD; x86-64 and aarch64, with i386 and armv7 builds tested in CI via QEMU since 2.1.0 |
| **Thread safety** | Tasks run on Lace workers; any non-Lace thread may call NAME(...), which posts into one of 64 external slots and blocks until done (multiple submitters allowed). One Lace instance per process; SPAWN/SYNC/DROP must be used by the owning worker in LIFO order. |
| **Drop-in for the baseline** | no |

## Gotchas

- LACE_NATIVE_OPT defaults to ON, so the library and benchmarks build with -march=native and the binaries may not run on other CPUs; the building docs say to turn it off for distributed builds. The library also compiles with -Werror plus -Wconversion/-Wsign-conversion, which broke a downstream build in 2.2.2 (issue #20, fixed).
- Fixed sizes: lace_start(.., 0, ..) gives 100,000 deque slots per worker (the source's static 1M default and the design page's '1M task slots x 64 bytes' are overwritten), and exceeding it prints 'lace_task stack overflow' and exits; requested stack sizes are silently clamped to 16-64 MB, unlike the header comment that describes the default as the minimum of 16 MB and the caller's stack size.
- SPAWN/SYNC must match in strict LIFO order (out-of-order SYNC is undefined behaviour) and every spawned task must be synced or dropped before the frame returns; scratch-arena allocations need a matching lace_scratch_reset on every return path (leaks are only reported at the next deep idle).
- Weak-memory confidence: in still-open issue #16 (32-bit builds, latest comment 2026-04-26) the FreeBSD port works around suspected ordering bugs by rewriting every memory_order_\* to seq_cst, and test_together segfaulted on armv7 and arm64 with no confirmed root cause; the 2.x design page now documents the release/acquire/seq_cst points for ARM and POWER, but the port workaround had not been dropped.

## Known shortcomings

- No figures anywhere: the Euro-Par paper abstract claims only parity with Wool, the Twente essay ranking Lace first was seen as a snippet only, and the repo's benchmarks build only Lace and sequential versions. Downgraded to D; retier possible once the papers are reachable.
- Enricher: the only numbers seen are issue #7 (2022, Lace v1, 6 threads, CPU unstated): fib(41) Lace 0.188 s vs Weave 2.663 s with Weave in its heap-allocating eager-future mode, and NQueens 15 with mislabelled units; Weave's author reports 2-2.5x faster on nqueens and 2.5-10x slower on fib on an i9-9980XE without naming the subject. LACE_NATIVE_OPT defaults ON (-march=native), the deque defaults to 100,000 slots per worker and exits on overflow, the stack is clamped to 16-64 MB unlike the header comment, and issue #16 is open (the FreeBSD port forces all memory orders to seq_cst; test_together segfaults on armv7 and arm64).

## Caveats and trade-offs

No performance numbers on any page opened: the README has none (only 'low-overhead, lock-free work-stealing' and a pointer to docs on the blocked GitHub Pages site), docs/benchmarks.rst lists 17 benchmark programs (fib, uts, nqueens, pi, integrate, cilksort, quicksort, dfs, matmul, rectmul, strassen, lu, cholesky, heat, fft, knapsack), mostly adapted from Nowa (Schmaus et al., IPDPS 2021), with run instructions and a bench.py driver but no results, and benchmarks/CMakeLists.txt builds only Lace and sequential variants (C11/C++11, Release adds -flto, optional -march=native), not TBB, Cilk or OpenMP versions, so the repo alone cannot reproduce a comparison. The Euro-Par 2014 / MuCoCoS paper 'Lace: Non-blocking Split Deque for Work-Stealing' (van Dijk and van de Pol, LNCS 8806 pp. 206-217, DOI 10.1007/978-3-319-14313-2_18) claims, per its abstract (search snippet), that the split deque and a private-deque variant have similar low overhead and scalability as Wool, i.e. parity with Wool rather than a win; its tables, van Dijk's PhD thesis (tvandijk.nl/pdf/thesis.pdf) and the 2020 University of Twente essay 'Load balancing framework comparison' by L.A. van der Gugten (essay.utwente.nl/essays/82071; per snippet: UTS, Fibonacci and Strassen built with the Intel and GNU compilers, Lace best, Cilk Plus slightly ahead of TBB, OpenMP worst by far) were all unreachable here, so no figure, core count, CPU or flag was read. Tier D (directional only) until the paper tables or the essay are read; the essay would support B or C. The 2.x releases (2.4.0 on 2026-06-07) rewrote parts of the library, so 2014 and 2020 numbers may not describe the current code. [retier] Enricher: only numbers seen are issue #7 against Weave in its heap-allocating eager-future mode (fib(41) 0.188 s vs 2.663 s, 6 threads, CPU unstated); LACE_NATIVE_OPT defaults to -march=native; open issue #16 (FreeBSD seq_cst override, arm segfault).

C API for fork-join only: tasks are declared with TASK macros and use SPAWN/SYNC/CALL, so it is not a general thread pool with futures. Fixed-size deque and stack set at lace_start. Per-task slot is fixed size (lace32 and lace128 variants trade task size). Workers sleep with exponential backoff when idle, optional hwloc pinning, optional per-worker statistics. Builds on Linux, macOS, Windows (MSVC, MinGW) and FreeBSD.

## Maintenance

Actively maintained (2.4.0 released 2026-06-07 with the scratch arena, 2.3.x in April 2026; CI on Linux, macOS, Windows and FreeBSD), Apache-2.0 and small (one .c and one generated-macro header per variant), so it is copyable; the performance claim stays directional, since the repo's harness has no baseline builds and the 2022 Weave comparison in issue #7 pitted Lace's slot-based tasks against Weave's heap-allocating eager-future mode on an unstated CPU.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** No figure against any baseline was seen anywhere: README and docs/benchmarks.rst carry no results, benchmarks/CMakeLists.txt builds only Lace and sequential variants, the 2014 paper abstract (snippet) claims only parity with Wool, and the 2020 Twente essay ranking Lace ahead of Cilk Plus, TBB and OpenMP was seen only as a snippet without numbers; benchmark_url is null and no numbers page could be opened, so the tier cannot stay above D.
- **Verifier notes:** Downgraded C to D: every comparison (paper, thesis, Twente essay) was seen only as search snippets with no figures, and the paper's own claim is parity with Wool. Metadata confirmed: Apache-2.0 (README), 61 stars, 11 forks, not a fork, 335 commits, last commit 2026-06-07 'Version 2.4.0'. Lead for a retier: the Twente essay PDF and the Nowa IPDPS 2021 paper (possible Lace comparison).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 11 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/trolando/lace>
  - <https://github.com/trolando/lace/commits>
  - <https://github.com/trolando?tab=repositories>
  - <https://raw.githubusercontent.com/trolando/lace/master/README.md>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/benchmarks.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/index.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/benchmarks/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/trolando/lace/master/README.md>
  - <https://raw.githubusercontent.com/trolando/lace/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/index.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/benchmarks.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/design.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/variants.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/tasks.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/migrating.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/getting-started.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/docs/building.rst>
  - <https://raw.githubusercontent.com/trolando/lace/master/src/lace.h>
  - <https://raw.githubusercontent.com/trolando/lace/master/src/lace.c>
  - <https://raw.githubusercontent.com/trolando/lace/master/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/trolando/lace/master/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/trolando/lace/master/benchmarks/fib/fib-lace.c>
  - <https://raw.githubusercontent.com/trolando/lace/master/benchmarks/fib/fib-seq.c>
  - <https://github.com/trolando/lace/issues?q=is%3Aissue>
  - <https://github.com/trolando/lace/issues/7>
  - <https://github.com/trolando/lace/issues/9>
  - <https://github.com/trolando/lace/issues/16>
  - <https://github.com/trolando/lace/commits/master>
  - https://essay.utwente.nl/82071/ (DNS blocked)
  - https://fmt.ewi.utwente.nl/media/89.pdf (DNS blocked)
  - https://www.tvandijk.nl/pdf/thesis.pdf (DNS blocked)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/trolando/lace`) · [data/wave11/enrich/raw/github_com_trolando_lace.json](../../../data/wave11/enrich/raw/github_com_trolando_lace.json) (enrichment confidence 0.65)

</details>
