# Nowa

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Research C runtime for wait-free continuation-stealing fork/join, reported faster than lock-based Cilk Plus/TBB and OpenMP tasks.

| | |
|---|---|
| **Beats** | Cilk Plus and TBB lock-based continuation stealing; OpenMP tasks (libomp) |
| **Claimed result** | Wait-free runtime up to 1.64x faster than lock-based runtimes at 256 threads, 1.17x on average; 8.68x faster than OpenMP tasks (clang libomp) on average (snippet only, paper PDF not opened). |
| **Workload** | Fork/join benchmark suite on up to 256 hardware threads (IPDPS 2021 paper). |
| **Metric** | throughput |
| **Adoption** | 0 stars (GitHub mirror of the Zenodo artifact) |
| **Last commit** | 2022-10-01 |
| **Links** | [repository](https://github.com/black7375/nowa) · [benchmark](https://www4.cs.fau.de/Publications/2021/schmaus2021nowa.pdf) |

## Verdict

According to WebSearch snippets of the IPDPS 2021 paper (the PDF on www4.cs.fau.de is EGRESS_BLOCKED), Nowa is up to 1.64x faster than the lock-based Cilk Plus and TBB runtimes on a 256-hardware-thread machine, 1.17x on average, and 8.68x faster on average than OpenMP tasks under Clang's libomp, over a 12-benchmark fork/join suite. CPU model and compiler flags were not readable this session; run_benchmarks.sh shows 50 runs plus 1 warm-up per configuration, swept over 9 core counts.

## Use it when

- Research or benchmarking of fork/join schedulers on many-core x86-64 Linux (the paper's headline is at 256 hardware threads)
- Recursive divide-and-conquer C/C++ kernels (fib, nqueens, cholesky, strassen, quicksort) where spawn and join overhead and join contention dominate
- As a reference implementation of wait-free continuation-stealing join to port into another runtime
- Reproducing the IPDPS 2021 comparison against Cilk Plus, TBB and libomp with the bundled run_benchmarks.sh

## Skip it when

- Anything other than x86-64 with GCC: the fork and join paths use inline asm on rbp/rsp/r15, the C API relies on GCC nested functions, and it uses GCC optimize attributes
- Production code: research prototype, a 0-star mirror of a Zenodo artifact, abandoned since 2022
- Programs that need futures, task graphs, parallel-for or async I/O; it only supports fully-strict fork/join
- Deep spawn nesting: the per-worker deque is a fixed 1024-slot ring (DEQUE_SIZE) with no overflow check in fibrili_push
- Shared or oversubscribed machines: idle workers spin on random steals with sched_yield and never sleep

## How it is fast

It uses continuation stealing (work-first, as in Cilk): the parent's continuation sits in a per-worker deque and thieves resume it on a fresh stack from a pool, handled with a cactus-stack technique that swaps rsp/rbp in inline asm. Nowa's change over Fibril is replacing the lock-based THE deque protocol and the join arbitration with atomic counters, swap and CAS (the wait-free strand arbitration of the IPDPS 2021 paper), so the owner never takes a lock on pop or join. The lock-based THE protocol is kept behind -DDEQUE_USE_THE for comparison.

## Compared with alternatives

Pick it over Staccato or Heartbeat Scheduling when you want to study continuation stealing with wait-free joins at very high core counts, rather than a usable library. For real C++ projects, Weave (Nim) is not an option, and a maintained pool such as citor or Fork Union is the practical choice.

## Integration

| | |
|---|---|
| **Form** | static/shared lib (libfibril via autotools) plus headers |
| **Dependencies** | pthreads; Cilk Plus, TBB, OpenMP/libomp only for the comparison benchmarks; Fibril submodule for the baseline runtime |
| **Minimum toolchain** | GCC 4.8+ (uses __atomic builtins, nested functions in C, C++ lambdas in the C++ path); autoconf 2.69, libtool |
| **Platforms** | x86-64 Linux only (inline asm, mmap/madvise, pthread_attr_setstack) |
| **Thread safety** | Multi-worker runtime by design; fibril_rt_init must be called once from the main thread, and the worker count comes from the argument or the FIBRIL_NPROCS environment variable |
| **Drop-in for the baseline** | no |

## Gotchas

- build.sh runs 'git submodule update --init --remote' on an SSH URL (git@gitlab.cs.fau.de:i4/manycore/fibril.git), so the Fibril baseline build fails for anyone without FAU GitLab access; the Nowa library in src/ builds independently.
- Functions that fork must carry the 'fibril' attribute (no-omit-frame-pointer), and stolen continuations run on pooled stacks of 1 MiB (PARAM_STACK_SIZE 0x100000), so deep recursion inside one strand can overflow.
- The steal path retries a CAS in a loop (deque_steal), so the wait-free property applies to the owner's pop and the join arbitration, not to thieves.
- The repo has no published result numbers; plots/ holds only plotting scripts, so the speedups must be taken from the paper.

## Known shortcomings

- x86-64 GCC only (inline asm, nested functions); fixed 1024-slot deque with no overflow check; build.sh submodule uses SSH to gitlab.cs.fau.de, which fails for outsiders; no result data in the repo, and the paper numbers are snippet only (IPDPS PDF blocked).

## Caveats and trade-offs

Paper (IEEE IPDPS 2021, www4.cs.fau.de PDF) and Zenodo are EGRESS_BLOCKED; numbers come from WebSearch snippets. The mirror repo has a benchmark directory and run_benchmarks.sh but no numbers in its README. Based on Fibril (chaoran/fibril); the LICENSE is MIT (Chaoran Yang 2014, Pfeiffer and Schmaus 2020). The GitHub mirror has 0 stars; the original artifact is Zenodo record 4541475. Last commit 2022-10-01. Cilk Plus is obsolete.

Built on Fibril (cactus stack, continuation stealing, custom stack switching); research prototype; build via ./build.

## Maintenance

Abandoned research artifact (mirror last touched 2022-10-01, 276 commits, MIT); small enough to vendor on x86-64 Linux with GCC, but treat it as a reference design rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IPDPS 2021 paper (cited in the README) compares Nowa against lock-based Cilk Plus and TBB and against OpenMP tasks (libomp). WebSearch snippets match the record exactly: up to 1.64x and 1.17x on average at 256 hardware threads, and 8.68x on average over OpenMP. The paper PDF (www4.cs.fau.de) is EGRESS_BLOCKED, so the numbers come from snippets.
- **Verifier notes:** The MIT license was confirmed from the LICENSE file. A retier could reach A if the paper states compiler, flags and CPU, since the benchmark code is public.
- **Fields the verifier corrected:** `benchmark_url`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/black7375/nowa>
  - <https://github.com/black7375/nowa/commits/master>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/black7375/nowa>
  - <https://github.com/black7375/nowa/tree/master/plots>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/README.md>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/build.sh>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/Makefile.am>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/test/Makefile.am>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/benchmark/Makefile.am>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/fibril.h>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/fibrile.h>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/fibrili.h>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/fibrili.c>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/deque.c>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/deque.h>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/runtime.c>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/stack.c>
  - <https://raw.githubusercontent.com/black7375/nowa/HEAD/src/param.c>
  - https://www4.cs.fau.de/Publications/2021/schmaus2021nowa.pdf (EGRESS_BLOCKED, 403)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/black7375/nowa`) · [data/wave11/enrich/raw/github_com_black7375_nowa.json](../../../data/wave11/enrich/raw/github_com_black7375_nowa.json) (enrichment confidence 0.55)

</details>
