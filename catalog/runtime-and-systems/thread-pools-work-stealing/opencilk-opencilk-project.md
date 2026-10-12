# OpenCilk (opencilk-project)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> LLVM/Clang fork compiling Cilk fork-join C/C++ onto a work-stealing runtime; paper reports beating oneTBB, OpenMP and Cilk Plus runtimes.

| | |
|---|---|
| **Beats** | Intel oneTBB, OpenMP and the Intel Cilk Plus runtime, each reached by OpenCilk's own compiler lowering the same Cilk programs to that runtime (the PMAM 2023 program, seen as a search snippet, says OpenCilk was extended to support Cilk Plus, OpenMP and oneTBB with fewer than 2000 new lines each; the abstract itself says only 'the other runtimes') |
| **Claimed result** | Geometric mean 4%-26% faster than the other runtimes on 1 core and 10%-120% faster on 48 cores across 15 benchmark Cilk programs (PPoPP 2023 abstract, seen as a search-result snippet only; per-runtime split and per-benchmark rows not seen). |
| **Workload** | 15 benchmark Cilk programs run on the OpenCilk work-stealing runtime (cheetah) versus the other task-parallel runtimes the paper extended OpenCilk to target, geometric mean over the 15 programs at 1 core and at 48 cores. |
| **Metric** | throughput |
| **Hardware** | 48-core machine per the abstract; CPU model not seen |
| **Adoption** | 132 stars, 39 forks; compiler of the OpenCilk platform (MIT) |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/OpenCilk/opencilk-project) · [benchmark](https://doi.org/10.1145/3572848.3577509) |

## Verdict

The PPoPP 2023 paper by the project's authors reports the OpenCilk runtime faster than the Cilk Plus, OpenMP and oneTBB runtimes by a geometric mean of 4%-26% on 1 core and 10%-120% on 48 cores across 15 Cilk benchmark programs, all compiled by OpenCilk and lowered to each runtime; the paper was unreachable here (DSpace, ACM, scispace, NSF PAR and the conference site all failed DNS), so the per-runtime split, CPU model and flags remain unseen, and the only independent data opened (issue #135) shows OpenCilk slower than ParlayLib on a fine-grained 2^20 sum.

## Use it when

- Recursive or nested fork-join C/C++ code (divide-and-conquer, parallel loops nested inside parallel loops) where you control the compiler and can build with OpenCilk's clang.
- You want a deterministic-by-construction programming model with tools: Cilksan to prove a run free of determinacy races and Cilkscale to measure work, span and parallelism before tuning.
- Parallel reductions that must be deterministic (reducer hyperobjects) or repeatable parallel random numbers (DotMix DPRNG via -lopencilk-pedigrees).
- Linux, macOS or FreeBSD on x86-64 or 64-bit ARM, including teaching and research settings (MIT 6.106 uses it).

## Skip it when

- You must build with GCC, MSVC or a stock Clang, or ship a library to users who do: Cilk keywords need the OpenCilk compiler, and Windows is not listed among supported systems.
- Very fine-grained or low-parallelism workloads where little is stolen: in open issue #135 a 2^20-element recursive sum took about 600 us under OpenCilk versus about 120 us with ParlayLib par_do on two Xeon Platinum 8375C sockets (maintainers attribute it to scheduling overhead, NUMA and hyperthreading).
- Projects relying on LTO or LLD LTO: open bugs #337 (LTO linker errors) and #313 (LLD LTO crash), plus #331 (cyclic dependency building shared libraries).
- Job-queue or asynchronous task submission (fire-and-forget, futures, I/O-bound tasks): the model is strict fork-join, so a pool such as BS::thread_pool or concurrencpp fits better.
- Code that needs the pedigree runtime: open issue #476 reports memory corruption on return from a steal with pedigrees.

## How it is fast

The compiler keeps spawns and syncs visible in the IR (Tapir), so ordinary LLVM optimizations work across parallel control flow, and it lowers them to Cheetah calls whose fast paths ship as an LLVM bitcode ABI file that is linked and inlined into user code. Cheetah is a work-first, continuation-stealing scheduler in the Cilk-5 tradition: a per-worker deque guarded by the THE protocol, randomized victim selection, provably-good steals, per-worker fiber pools for the cactus stack, and adaptive thief sleep based on steal-success history (worker_sleep.cpp). cilk_for is lowered to recursive divide-and-conquer spawning (requires -O1 or higher).

## Compared with alternatives

Pick OpenCilk over library schedulers such as citor, Lace or Fork Union when you can adopt its compiler and want language-level fork-join with race detection, scalability analysis and deterministic reducers; prefer a library sibling (citor, Fork Union, Taskflow-style pools) when you must stay on a stock GCC, Clang or MSVC toolchain or need non-fork-join task graphs.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (LLVM/Clang fork) plus runtime library (OpenCilk/cheetah); prebuilt release binaries for select systems |
| **Dependencies** | the OpenCilk compiler and its bundled Cheetah runtime; building from source needs a full LLVM build (infrastructure scripts provided) |
| **Minimum toolchain** | OpenCilk clang with -fopencilk (OpenCilk 3.0 is based on LLVM 19.1.7; the dev/21.x branch carries the 4.0 release candidates); cilk_for needs -O1 or higher |
| **Platforms** | x86-64 and 64-bit ARM on Linux, macOS (via xcrun) and FreeBSD per the README; Android beta in 3.0; Windows not listed |
| **Thread safety** | Runtime schedules spawned tasks across CILK_NWORKERS workers; user code must be free of determinacy races (checkable with Cilksan), reducers give race-free reductions |
| **Drop-in for the baseline** | partial — the same Cilk source can be lowered to other runtimes, but replacing oneTBB or OpenMP code means rewriting it with Cilk keywords and switching compilers |

## Gotchas

- The paper's oneTBB and OpenMP baselines are not native TBB or OpenMP programs: the same Cilk source is lowered by OpenCilk's Tapir back ends to each runtime, so the comparison measures schedulers under OpenCilk's own front end. In dev/21.x the Tapir targets are Serial, Cheetah, CilkPlus, Lambda, OMPTask, OpenCilk and Qthreads; no oneTBB target ships, and the generic Lambda ABI needs an external bitcode ABI file, so the oneTBB comparison cannot be rerun from this repository alone.
- A standalone CMake build of OpenCilk/cheetah defaults to CMAKE_BUILD_TYPE=Debug with all assertions enabled (cheetah README); benchmark against a Release build.
- C++ exceptions are supported, but open issue #347 says out-of-order exceptions may call std::terminate, and several compiler crashes in Cilk exception handling and taskframe logic were fixed only recently (#483, #484, Aug 2026 commits).
- Maintainers note in issue #135 that cilk_for with a reducer currently vectorizes poorly, so a reducer-based loop can be slower than a hand-written spawn tree.

## Known shortcomings

- Numbers seen only as PPoPP 2023 abstract snippets (geomean 4-26% at 1 core, 10-120% at 48 cores), per-baseline margins unknown; the baselines are Cilk programs compiled by OpenCilk's own compiler onto the oneTBB, OpenMP and Cilk Plus runtimes, not native TBB or OpenMP code. The measured runtime lives in OpenCilk/cheetah, not this repo. Paper hosts (dspace.mit.edu and others) unreachable here.
- Enricher: the paper is still unreachable, so the evidence stays snippet-only; dev/21.x has no oneTBB Tapir target and the generic LambdaABI needs an external bitcode file, so the oneTBB comparison cannot be rerun from the repo. Open issue #135 shows OpenCilk about 600 us vs ParlayLib par_do about 120 us on a 2^20 sum (2x Xeon 8375C); open bugs #347 (exceptions may call std::terminate), #476 (pedigree memory corruption), #337 and #313 (LTO); cheetah's standalone CMake build defaults to Debug.

## Caveats and trade-offs

Numbers come from the abstract of 'OpenCilk: A Modular and Extensible Software Infrastructure for Fast Task-Parallel Code' (Schardl and Lee, PPoPP '23, pp. 189-203, DOI 10.1145/3572848.3577509), seen only as search-result snippets; the paper (MIT DSpace handle 1721.1/148273, cesmix.mit.edu, neboat.mit.edu, ACM) was unreachable in this environment, so tables, CPU model, compiler flags and the per-runtime geomeans are unseen. Tier B rests on peer review only; no artifact repository was found (the OpenCilk GitHub org has 14 repos: smallapps and applications are regression tests and examples, nothing labelled as the paper's artifact), so A is not supported. The baselines are not hand-written oneTBB or OpenMP code: the same Cilk source is lowered by OpenCilk's Tapir compiler to call the oneTBB, OpenMP or Cilk Plus runtime, so the comparison isolates the runtime scheduler (cheetah) under a front end the authors built, and a native TBB or OpenMP port could behave differently. The 4%-26% and 10%-120% ranges span the three baselines, so the margin against oneTBB or OpenMP alone is unknown and may be the small end. The authors own the system, so this is first-party-authored though peer reviewed. Cilk Plus is deprecated and gone from current GCC and ICC, so that baseline is historical. The measured runtime lives in the separate OpenCilk/cheetah repository; this repo is the compiler (an LLVM fork adding Tapir and Cilk support), and its README makes no numeric comparison (only 'optimize task-parallel programs more effectively than mainstream compilers'). Weak independent hint, snippet only: Los and Petushkov (arXiv 2410.01222, i7-8700, fine-grained SMT kernels) report their Relic framework 30.1% faster than oneTBB and 21.4% faster than OpenCilk, which implies OpenCilk ahead of oneTBB there (derived, not checked). Licence: LLVM parts are Apache-2.0 with LLVM exception (LICENSE.TXT); MIT_LICENSE.TXT says OpenCilk's modifications are MIT with an OpenCilk Addendum allowing distribution under the LLVM licence instead. Retier once the paper PDF is readable. [retier] Enricher: the oneTBB comparison cannot be rerun from the repo (no oneTBB Tapir target on dev/21.x); open issue #135 shows OpenCilk about 600 us vs ParlayLib par_do about 120 us on a 2^20 sum; open bugs #347, #476, #337, #313; cheetah's standalone build defaults to Debug.

Not a drop-in library: needs the OpenCilk compiler (an LLVM/Clang fork implementing Tapir) and the Cilk language extensions (cilk_spawn, cilk_sync, cilk_for) in C/C++ source. The runtime is a separate repository (OpenCilk/cheetah). The monorepo is a full LLVM tree (546k commits), so building from source is heavy; prebuilt releases exist. Ships Cilksan (race detector) and Cilkscale (scalability analyzer) as companion tools.

## Maintenance

Actively maintained (last commit 2026-08-17 on dev/21.x, OpenCilk 3.0 released on LLVM 19.1.7, 4.0 release candidates out) with 22 open issues; the compiler is an LLVM fork under Apache-2.0 with LLVM exception plus MIT for OpenCilk changes, so usable but only as a whole toolchain, not as code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PPoPP '23 paper (Schardl and Lee, pp. 189-203, DOI 10.1145/3572848.3577509, cited in the repo README) reports the OpenCilk runtime 4%-26% faster on 1 core and 10%-120% faster on 48 cores (geometric mean, 15 Cilk programs) than the other runtimes; the abstract figures were confirmed twice via search snippets but the PDF hosts (MIT DSpace, cesmix.mit.edu, neboat.mit.edu) do not resolve here, and no artifact repo with code, compiler, flags and CPU model exists, so not A.
- **Verifier notes:** Metadata confirmed on github.com: 132 stars, 39 forks, branch dev/21.x, last commit 2026-08-17 (TapirUtils/SimplifyCFG taskframe fixes), description 'Forked from llvm/llvm-project and based on Tapir/LLVM', MIT_LICENSE.TXT addendum read. Shortcomings for the orchestrator: abstract-snippet-only evidence, baselines are OpenCilk-compiled Cilk programs on other runtimes rather than native TBB/OpenMP code, per-baseline margin unknown, first-party authors, measured runtime is in OpenCilk/cheetah not this repo; benchmark_url set to the DOI cited in the README (not openable here).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 11 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/OpenCilk/opencilk-project>
  - <https://github.com/OpenCilk/opencilk-project/commits>
  - <https://github.com/orgs/OpenCilk/repositories>
  - <https://github.com/OpenCilk/www.opencilk.org>
  - <https://raw.githubusercontent.com/OpenCilk/opencilk-project/dev/21.x/README.md>
  - <https://raw.githubusercontent.com/OpenCilk/opencilk-project/dev/21.x/MIT_LICENSE.TXT>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/OpenCilk/opencilk-project/dev/21.x/README.md>
  - <https://github.com/OpenCilk/opencilk-project/releases>
  - <https://github.com/OpenCilk/opencilk-project/releases/tag/opencilk/v3.0>
  - <https://github.com/OpenCilk/opencilk-project/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/OpenCilk/opencilk-project/issues?q=is%3Aissue+performance>
  - <https://github.com/OpenCilk/opencilk-project/issues/135>
  - <https://github.com/OpenCilk/opencilk-project/commits/dev/21.x>
  - <https://github.com/OpenCilk/opencilk-project/tree/dev/21.x/llvm/lib/Transforms/Tapir>
  - <https://raw.githubusercontent.com/OpenCilk/opencilk-project/dev/21.x/llvm/include/llvm/Transforms/Tapir/TapirTargetIDs.h>
  - <https://raw.githubusercontent.com/OpenCilk/opencilk-project/dev/21.x/llvm/lib/Transforms/Tapir/LambdaABI.cpp>
  - <https://github.com/orgs/OpenCilk/repositories>
  - <https://github.com/OpenCilk/smallapps>
  - <https://github.com/OpenCilk/cheetah>
  - <https://github.com/OpenCilk/cheetah/tree/dev/runtime>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/HEAD/README.md>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/dev/runtime/scheduler.cpp>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/dev/runtime/rts-config.h>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/dev/runtime/worker_sleep.cpp>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/dev/runtime/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OpenCilk/cheetah/dev/config.mk>
  - <https://raw.githubusercontent.com/OpenCilk/infrastructure/HEAD/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/opencilk/opencilk-project`) · [data/wave11/enrich/raw/github_com_opencilk_opencilk_project.json](../../../data/wave11/enrich/raw/github_com_opencilk_opencilk_project.json) (enrichment confidence 0.6)

</details>
