# Kokkos

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Performance-portability programming model (Views plus parallel dispatch); a Kokkos PIC port beat its OpenMP variant 1.4-1.6x on Xeon.

| | |
|---|---|
| **Beats** | OpenMP (hand-written OpenMP variant of the same particle-in-cell plasma code) |
| **Claimed result** | Kokkos particle movement rate 1.4x the OpenMP variant on Kabre's Intel Xeon Gold 6354, 1.6x on Raven's Intel Xeon Platinum 8360Y; performance-portability metric 100% (Kokkos) vs 67% (OpenMP) (snippet only, paper not opened) |
| **Workload** | Particle movement rate of a particle-in-cell plasma physics code ported to Kokkos versus its OpenMP variant, on server CPUs. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6354 (Kabre); Intel Xeon Platinum 8360Y (Raven); the paper also used AMD EPYC CPUs and NVIDIA and AMD GPUs |
| **Adoption** | 2.7k stars; Linux Foundation / HPSF established project |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/kokkos/kokkos) · [benchmark](https://arxiv.org/pdf/2411.05009) |

## Verdict

Per web-search snippets of Ruzicka, Asch, Meneses, Rampp and Laure (CARLA 2024 preprint, arXiv 2411.05009; the paper itself was not opened), a Kokkos port of a plasma particle-in-cell code moved particles 1.4x faster than the code's own OpenMP variant on an Intel Xeon Gold 6354 (Kabre) and 1.6x faster on a Xeon Platinum 8360Y (Raven), and scored 100% vs 67% on a performance-portability metric for the geometric initialization case; the authors attribute the gap to the OpenMP variant's one-dimensional grid storage chosen for GPU offload versus Kokkos's automatic layout. Compiler, flags, Kokkos version and the Kokkos CPU backend were not seen, and the repo's own benchmarks/ directory (stream, gups, launch_latency, atomic, policy_performance and others) publishes no result tables.

## Use it when

- One C++ code base (typically MPI+X HPC) that must run on Xeon/EPYC CPUs and on NVIDIA, AMD or Intel GPUs without maintaining separate OpenMP and CUDA/HIP variants.
- Grid, stencil and particle kernels over multidimensional arrays where letting View pick LayoutRight on host and LayoutLeft on GPU replaces hand-flattened, GPU-oriented 1D arrays (the source of the 1.4-1.6x CPU gain in the PIC study).
- Data-parallel loops that need reductions, scans, multidimensional ranges (MDRangePolicy) or hierarchical team parallelism with per-team scratch memory.
- Projects already built on the Kokkos ecosystem (kokkos-kernels, Trilinos) that want the same View and dispatch types end to end.

## Skip it when

- CPU-only code that already has a well-laid-out OpenMP loop: the OpenMP backend runs the same omp pragma, so there is no scheduling gain, and third-party studies report overhead instead (FESOM2 ocean-model port: Kokkos-CPU 13-18% slower than the C port; LArTPC study: about 4x speedup from Kokkos OpenMP where about 20x was expected; both seen as search snippets only).
- Task graphs, futures or recursive fork-join: the task DAG scheduler was removed in 5.0.0 (#8390), so there is no work-stealing task pool left in Kokkos core.
- A general-purpose thread pool for heterogeneous asynchronous jobs: there is no submit/future API, only bulk parallel dispatch on execution-space instances.
- Small projects that cannot take a C++20 toolchain, CMake 3.22+ (3.25.2 for the CUDA language) and configure-time backend selection; makefile builds were dropped in 5.0.0.
- Latency-critical tiny dispatches: each OpenMP-backend kernel takes a per-instance std::mutex before entering the parallel region; dedicated fork-join pools target lower per-dispatch cost.

## How it is fast

Kokkos does not bring a faster CPU scheduler: on the OpenMP backend a RangePolicy parallel_for is a native '#pragma omp parallel for schedule(static)' (schedule(dynamic) with Schedule&lt;Dynamic&gt;), and the C++ threads backend uses static partitioning plus chunk stealing from a neighbouring thread's range (HostThreadTeamData / ThreadsInternal::get_work_index). The gains come from the data abstraction: Kokkos::View chooses the layout per execution space (LayoutRight on host so each thread walks contiguous memory and avoids false sharing, LayoutLeft on GPUs for coalesced access) and may pad dimensions, so one source gets a target-appropriate layout without hand-written architecture-specific structures; the PIC paper credits exactly this for its CPU result. Functors and lambdas are template arguments, so the loop body is inlined into the backend loop.

## Compared with alternatives

Pick Kokkos over Fork Union, citor or nexus only when the same source must also run on GPUs or you want backend-chosen multidimensional View layouts; for CPU-only fork-join dispatch Fork Union (claims 3-6x lower per-dispatch cost than OpenMP) or citor are lighter, and for task graphs nexus or dpuyda/scheduling fit better because Kokkos 5 has no task scheduler.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake build; also consumable via add_subdirectory or 'spack install kokkos') |
| **Dependencies** | none required for the Serial and C++ threads backends; the compiler's OpenMP runtime for the OpenMP backend; CUDA, ROCm/HIP, SYCL (IntelLLVM), NVC++ or HPX toolchains for those backends; optional hwloc for thread binding; third-party code embedded under tpls/ |
| **Minimum toolchain** | C++20 and CMake 3.22 (Kokkos 5.x); minimum compilers GCC 10.4.0, Clang 14 (CPU), Clang 15 + CUDA 11.8 (CUDA), NVCC 12.2, IntelLLVM 2022.0.0 (CPU) or 2024.2.1 (SYCL), NVC++ 22.3, ROCm 6.2.0, MSVC 19.30; Kokkos 4.x still covers C++17 toolchains |
| **Platforms** | x86-64, aarch64 (NEON and SVE SIMD types), RISC-V; Linux, Windows (MSVC, shared libs since 5.0) and macOS; NVIDIA, AMD (incl. MI300A) and Intel GPUs; NextSilicon execution space added in 5.2.0 |
| **Thread safety** | Kernels dispatched to the same execution-space instance are serialized by a per-instance mutex (OpenMP backend source); execution-space instances may only be created after Kokkos::initialize and must be destroyed before finalize (5.1.0), and creating Kokkos::OpenMP instances inside an omp parallel region is deprecated; thread-safety fixes are still landing (Serial and OpenMP in 4.4, parallel_scan #9300 in 5.2.0). |
| **Drop-in for the baseline** | partial — a RangePolicy parallel_for on the OpenMP backend compiles to the same '#pragma omp parallel for', so loops can be ported one at a time, but arrays must become Kokkos::View, the program needs initialize/finalize, and OpenMP features outside the dispatch patterns (tasks, sections, arbitrary pragmas) have no direct equivalent. |

## Gotchas

- Backends are chosen at configure time and default OFF: if no host backend is enabled, CMake turns on Serial only (cmake/kokkos_enable_devices.cmake), so a default build runs single-threaded until Kokkos_ENABLE_OPENMP or Kokkos_ENABLE_THREADS is set.
- The default RangePolicy schedule is Static (Kokkos_ScheduleTrait.hpp); work stealing only happens with Schedule&lt;Dynamic&gt;, and on the OpenMP backend that maps to OpenMP's own schedule(dynamic) for range loops. With GCC the RangePolicy chunk size is ignored for static schedules (source comment: specifying it caused a performance regression).
- Views are reference-counted shallow handles, but allocation and reference counting are switched off inside parallel regions, nested Views must be built in host code, and the default layout differs by memory space, so deep_copy between a LayoutLeft CudaSpace View and a LayoutRight HostSpace View does not compile.
- Harness flaw behind the catalogued numbers: the 1.4x/1.6x comes from one PIC application (Kokkos port vs its own OpenMP variant), and since Kokkos's OpenMP-backend parallel_for is the same native omp pragma, the gain cannot come from the threading runtime; per the paper snippets it comes from the OpenMP variant storing the grid as a one-dimensional, GPU-oriented array. Which Kokkos host backend, version, compiler and flags were used was not seen (arXiv is blocked here).

## Known shortcomings

- Paper evidence (arXiv 2411.05009) seen only as search snippets (arxiv.org blocked): 1.4x on Xeon Gold 6354 and 1.6x on Platinum 8360Y over OpenMP in one particle-in-cell code, an application-level comparison the paper credits to data layout rather than the scheduler; the OpenMP baseline may use GPU-oriented 1D arrays that underperform on CPU (unverified). No compiler or flags. Loose fit for thread-pools-work-stealing. Paper-access retier candidate (could reach B once the PDF is readable).
- Enricher: the OpenMP backend's RangePolicy parallel_for is a native #pragma omp parallel for schedule(static) plus a per-instance mutex (core/src/OpenMP/Kokkos_OpenMP_Parallel_For.hpp, since 3.7), so the PIC 1.4x/1.6x cannot come from the runtime; it comes from data layout (the OpenMP variant used a 1D GPU-oriented grid while Kokkos View picks LayoutRight on host). Poor category fit: the task DAG was removed in 5.0.0 (#8390) and only Schedule&lt;Dynamic&gt; chunk stealing remains (default Static); the default CMake build is Serial only. Third-party overhead snippets: FESOM2 Kokkos-CPU 13-18% slower than a C port (arXiv 2606.11356), LArTPC Kokkos OpenMP about 4x where 20x was expected (arXiv 2203.02479).

## Caveats and trade-offs

Snippet only: arxiv.org, themoonlight.io and orion.tec.ac.cr are blocked in this environment, so the numbers come from web search summaries of 'A Study of Performance Portability in Plasma Physics Simulations' (Ruzicka, Asch, Meneses, Rampp, Laure; CARLA 2024 proceedings preprint) and could not be checked against the paper's tables; compiler, flags and benchmark code were not seen. The comparison is application-level (one PIC code, a Kokkos port against its own OpenMP variant) and the paper credits Kokkos's automatic memory layout and data-access patterns, not its scheduler; a snippet also says the OpenMP code had been converted to one-dimensional arrays for GPU offload and that this variant underperformed on CPUs, so the CPU win may partly measure a GPU-oriented data layout in the OpenMP baseline (unverified which OpenMP variant the CPU rows used). Other third-party studies report Kokkos overheads of 13-18% (ocean model, CPU) and about 70% of native CUDA throughput (CMS pixel reconstruction), so Kokkos is not generally faster than native code. It is a performance-portability programming model rather than a thread pool, so the thread-pools-work-stealing category is a loose fit. The repo's own core/perf_test and benchmarks/ directories (stream, gups, launch_latency, atomic, ...) publish no result tables. The README still names 5.1.0 as current, but the releases page shows v5.2.2 (2026-09-10); last commit 2026-10-07 from the develop branch commit feed.

Performance-portability programming model (CUDA, HIP, SYCL, HPX, OpenMP and C++ threads backends), not a drop-in thread pool; requires C++20; code must be written against Kokkos Views and parallel dispatch.

## Maintenance

Actively maintained Linux Foundation / HPSF project (release 5.2.2 on 2026-09-10, 325 develop commits since, 2.7k stars), Apache-2.0 WITH LLVM-exception and copyable; the catalogued win is snippet-only and reflects data layout in one application rather than a faster scheduler, so it is a loose fit for thread-pools-work-stealing (README still names 5.1.0 as current).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark_url (arXiv 2411.05009, CARLA 2024 preprint) is EGRESS_BLOCKED, as are the themoonlight.io review and the TEC orion publication page; two WebSearch snippets of the paper repeat the 1.4x (Kabre, Xeon Gold 6354), 1.6x (Raven, Xeon Platinum 8360Y) and 100% vs 67% performance-portability figures, but compiler, flags and benchmark code were not seen, so snippet-only evidence stays at C. The paper is a peer-reviewed proceedings preprint, so it could reach B once the PDF is opened (paper-access retier candidate).
- **Verifier notes:** Kokkos core is not yet listed (only kokkos-kernels, wave 8, sparse-and-solvers), so not a duplicate. Shortcomings for the orchestrator: snippet-only evidence from a blocked arXiv paper; application-level PIC comparison whose gain is credited to data layout, with an OpenMP baseline that may use a GPU-oriented 1D-array layout on CPU; no compiler or flags seen; loose category fit. License verified from LICENSE (Apache-2.0 with LLVM exceptions); 2.7k stars, 525 forks, not archived, not a fork.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Shortcomings recorded by:** arXiv snippet (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/kokkos/kokkos>
  - <https://github.com/kokkos/kokkos/commits/develop.atom>
  - <https://github.com/kokkos/kokkos/releases>
  - <https://github.com/kokkos/kokkos/releases/latest>
  - <https://raw.githubusercontent.com/kokkos/kokkos/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kokkos/kokkos/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/kokkos/kokkos>
  - <https://raw.githubusercontent.com/kokkos/kokkos/HEAD/README.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/CHANGELOG.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/OpenMP/Kokkos_OpenMP_Parallel_For.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/Threads/Kokkos_Threads_ParallelFor_Range.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/Threads/Kokkos_Threads_Instance.cpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/impl/Kokkos_HostThreadTeam.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/impl/Kokkos_HostThreadTeam.cpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/traits/Kokkos_ScheduleTrait.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/core/src/Kokkos_Macros.hpp>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kokkos/kokkos/develop/cmake/kokkos_enable_devices.cmake>
  - <https://raw.githubusercontent.com/kokkos/kokkos-core-wiki/main/docs/source/get-started/requirements.rst>
  - <https://raw.githubusercontent.com/kokkos/kokkos-core-wiki/main/docs/source/ProgrammingGuide/ParallelDispatch.md>
  - <https://raw.githubusercontent.com/kokkos/kokkos-core-wiki/main/docs/source/ProgrammingGuide/View.rst>
  - <https://raw.githubusercontent.com/kokkos/kokkos-core-wiki/main/docs/source/API/core/policies/RangePolicy.rst>
  - <https://github.com/kokkos/kokkos/tree/develop/benchmarks>
  - <https://github.com/kokkos/kokkos/issues?q=is%3Aissue+openmp+slower+performance>
  - <https://github.com/kokkos/kokkos/issues?q=is%3Aissue+is%3Aopen+label%3A%22Performance%22>
  - <https://github.com/kokkos/kokkos/issues/6480>
  - <https://github.com/kokkos/kokkos/releases/latest>
  - https://arxiv.org/abs/2411.05009 (EGRESS_BLOCKED; numbers taken from WebSearch snippets of arxiv.org/pdf/2411.05009 and arxiv.org/html/2411.05009v1)
  - WebSearch snippets of arXiv 2606.11356 (FESOM2 Kokkos port) and arXiv 2203.02479 (LArTPC portable programming models), not opened
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/kokkos/kokkos`) · [data/wave11/enrich/raw/github_com_kokkos_kokkos.json](../../../data/wave11/enrich/raw/github_com_kokkos_kokkos.json) (enrichment confidence 0.5)

</details>
