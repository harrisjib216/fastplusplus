# Weave

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT OR Apache-2.0` · 🟡 stale

> Nim task- and data-parallel runtime that uses message-passing work-requesting; claims 3-10x less scheduling overhead than TBB and GCC OpenMP.

| | |
|---|---|
| **Beats** | Intel TBB, GCC OpenMP, Cilk |
| **Claimed result** | 'as low as 3x to 10x less overhead than Intel TBB and GCC OpenMP on overhead-bound benchmarks' (README, no table opened) |
| **Workload** | Overhead-bound task-parallel benchmarks (fibonacci, nqueens, DFS, BPC, SPC, heat, matmul) and data-parallel loops. |
| **Metric** | throughput |
| **Adoption** | 586 stars; FOSDEM 2020 talk |
| **Last commit** | 2023-12-09 |
| **Links** | [repository](https://github.com/mratsim/weave) · [benchmark](https://github.com/mratsim/weave) |

## Verdict

Only the README headline was found: 'as low as 3x to 10x less overhead than Intel TBB and GCC OpenMP on overhead-bound benchmarks', backed by a public benchmark suite (fibonacci, DFS, nqueens, heat, matmul, BPC, SPC, ...) but no result tables, compiler versions or CPU models in the repo pages read.

## Use it when

- Nim programs with very fine-grained recursive parallelism (fib, DFS, nqueens style trees) where TBB-like runtimes need about 10,000 cycles per task to break even; Weave targets tasks from about 2,000 cycles
- Nested parallel loops where you do not want to tune grain size or partitioning (lazy splitting handles it)
- Dataflow or pipeline graphs expressed with FlowEvents on top of the same scheduler
- Research or teaching on message-passing schedulers, or targets without good atomics (the design only needs channels)

## Skip it when

- C++ codebases: there is no C++ API; you would have to write the parallel code in Nim
- Nim 2.x: open issues #201 (task compilation fails for Nim &gt;= 2.0.0, type mismatch on gcsafe), #200 (README examples do not compile) and #171 (recent Nim makes Weave crash)
- Code that blocks or sleeps inside tasks: scheduling is cooperative, so a blocked worker starves steal requests and others spin
- Production systems that need proven correctness: README marks it experimental, only one of two complex sync primitives was formally verified, and there are open livelock/deadlock bugs (#130 parallelFor livelock, #149 syncScope stall, #161 background submits go missing)
- GC-managed Nim types in tasks: not tested; pass raw pointers instead

## How it is fast

It follows Andreas Prell's Tasking 2.0 design: idle workers send steal requests over SPSC/MPSC channels and busy workers answer them (work-requesting), instead of thieves touching shared Chase-Lev deques. Thieves adapt between steal-one and steal-half, loops are split lazily only when a steal request arrives (adaptive lazy loop splitting, no grain size), and task memory comes from a thread-local pool with a lookaside buffer modelled on mimalloc/snmalloc, with lock-free batching MPSC channels. Optional lazy Flowvar allocation (-d:WV_LazyFlowvar) cuts overhead by at least 2x more on very fine-grained tasks, per the README.

## Compared with alternatives

Pick Weave only if you write Nim and want TBB/Cilk-class task parallelism with dataflow tasks; for C++ work, Staccato and Nowa compare against TBB/Cilk with published numbers, and Fork Union covers low-overhead parallel-for.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Nim stdlib plus the synthesis nimble package |
| **Minimum toolchain** | Nim &gt;= 1.2.0 (nimble); broken on Nim &gt;= 2.0.0 per issue #201 |
| **Platforms** | Linux, macOS, Windows on x86, x86-64, ARM64 (CI-tested with C and C++ backends); any pthread target; Windows 32-bit needs MSVC, not MinGW |
| **Thread safety** | Tasks spawned only from Weave worker threads; foreign threads must use setupSubmitterThread/submit/waitFor (experimental) |
| **Drop-in for the baseline** | no |

## Gotchas

- Forgetting init(Weave)/exit(Weave) gives nil pointer exceptions on spawn
- With -d:WV_LazyFlowvar, Flowvars must be at most machine-word size and cannot be returned, or you hit stack smashing or crashes
- syncScope does not compile in C++ backend mode inside a for loop (Nim issue 14118); awaitable loops are not barriers for grandchildren tasks
- benchmarks/README lists histogram and logsumexp parallel reductions as pathological cases with a suspected bug in parallel reductions

## Known shortcomings

- Nim only, no C++ API; only the README headline claim, no tables. Open issues: 201 (fails on Nim 2.0.0 and later), 171 (crash on recent Nim), 130 and 149 (livelocks).

## Caveats and trade-offs

Quantitative per-benchmark numbers are not in the benchmarks/ READMEs (fibonacci README only gives an OpenMP comparison recipe with clang/gcc -O3 -fopenmp, no results; dfs and nqueens READMEs are stubs); FOSDEM 2020 slides not reachable. Only the README headline claim is recorded. Nim library (C and C++ backends), not usable directly from C++.

Nim runtime (C/C++ backend); message-passing work-requesting instead of shared deques; needs to be called from Nim; only partially formally verified.

## Maintenance

Stale since 2023-12-09 with open compile failures on Nim 2.x; MIT or Apache-2.0, useful mainly as a Nim library or a reference design for work-requesting schedulers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README states 'as low as 3x to 10x less overhead than Intel TBB and GCC OpenMP on overhead-bound benchmarks' with a public benchmark suite (benchmarks/ fibonacci, dfs, nqueens, heat, matmul, ...) but no result tables, compiler flags or CPU model on the pages opened; first-party headline claim only.
- **Verifier notes:** github.com: 586 stars, MIT or Apache-2.0 dual license, not archived, last commit 2023-12-09 (stale). Claim matches README wording verbatim.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party headline only
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/README.md>
  - <https://github.com/mratsim/weave>
  - <https://github.com/mratsim/weave/commits/master>
  - <https://github.com/mratsim/weave/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/benchmarks/fibonacci/README.md>
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/benchmarks/dfs/README.md>
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/benchmarks/nqueens/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/README.md>
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/mratsim/weave/HEAD/weave.nimble>
  - <https://github.com/mratsim/weave/tree/master/benchmarks>
  - <https://github.com/mratsim/weave/issues>
  - <https://github.com/mratsim/weave/issues/201>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mratsim/weave`) · [data/wave11/enrich/raw/github_com_mratsim_weave.json](../../../data/wave11/enrich/raw/github_com_mratsim_weave.json) (enrichment confidence 0.65)

</details>
