# Taskflow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ task-graph library that beats oneTBB FlowGraph on heterogeneous CPU+GPU DAG workloads.

| | |
|---|---|
| **Beats** | Intel oneTBB (FlowGraph task scheduler) |
| **Claimed result** | up to 29% faster runtime, 1.5x less memory, and 1.9x higher throughput than oneTBB on the ML workload |
| **Workload** | MIT/Amazon Large Sparse Deep Neural Network (LSDNN) Inference Challenge: 1920-layer sparse DNN (4096 or 65536 neurons per layer) run as a heterogeneous CPU+GPU task graph (up to 4 cudaFlows) by Taskflow vs oneTBB (2021.1) FlowGraph and StarPU. Throughput is weighted speedup across up to 9 co-running processes on 40 CPUs and 4 GPUs. |
| **Metric** | throughput |
| **Hardware** | 40 Intel Xeon CPU cores at 2.00 GHz (exact model not stated), 4 GeForce RTX 2080 GPUs, 256 GB RAM, Ubuntu Linux 5.0.0-21-generic |
| **Compiler and flags** | clang++ v10 as the host compiler under Nvidia CUDA v11, -std=c++17 -O2 (paper says no significant difference vs -O3) |
| **Adoption** | 12.2k stars |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/taskflow/taskflow) · [benchmark](https://arxiv.org/abs/2004.10908) |

## Verdict

On a 1920-layer sparse DNN inference task graph (LSDNN challenge) run as a CPU+GPU task graph with up to 4 cudaFlows, across up to 9 co-running processes on 40 Intel Xeon CPU cores plus 4 GeForce RTX 2080 GPUs (clang++ v10 host compiler, CUDA 11, -std=c++17 -O2), Taskflow's IEEE TPDS 2021 paper (arXiv 2004.10908) reports up to 29% faster runtime, 1.5x less memory, and 1.9x higher weighted throughput than Intel oneTBB 2021.1 FlowGraph.

## Use it when

- Workload is itself an irregular task DAG mixing CPU and GPU kernels in one graph, not a flat parallel-for
- Graph structure is dynamic or recursive at runtime (subflows) rather than declared statically up front like TBB FlowGraph
- Multiple taskflows/processes co-run on the same CPU+GPU node and you care about aggregate throughput under contention, not just single-run latency
- You want built-in parallel algorithms (for_each/reduce/sort/pipeline) and a graph profiler (TFProf) bundled with the scheduler
- A C++20 toolchain is already available (GCC 11+/Clang 12+/MSVC 19.29+/NVCC 12.0+)

## Skip it when

- You just need flat parallel loops or fire-and-forget async calls; a simple thread pool or std::async has far less API surface
- You're pinned to C++17 or an older compiler; the current release (v4.0.0) requires C++20
- Tasks throw exceptions heavily: open issues report tf::Semaphore combined with exceptions can deadlock (#732) and throwing many exceptions is UB that can crash or silently lose the exception (#724)
- You need evidence measured against std::async/std::thread directly; this benchmark is tier B and compares against oneTBB FlowGraph, one step removed from the std baseline
- You want a minimal header with no GPU-adjacent code paths; the repo ships a full CUDA task-graph subsystem (taskflow/cuda/\*) even if you never touch a GPU

## How it is fast

Each worker has a bounded lock-free work-stealing queue (ring buffer, default 256 slots, log2-sized via TF_DEFAULT_BOUNDED_TASK_QUEUE_LOG_SIZE) backed by an unbounded overflow queue, so idle workers steal ready tasks instead of waiting on a central scheduler like FlowGraph's. Worker wakeup uses a non-blocking/atomic notifier rather than plain condition variables. GPU offload is captured as an Nvidia CUDA Graph and replayed via a single graph-exec launch, avoiding per-kernel CPU launch overhead, which is the mechanism behind the paper's reported gains on a mixed CPU+GPU task graph.

## Compared with alternatives

dispenso, TooManyCooks, and libfork also beat oneTBB, but against its flat parallel_for/task-group APIs on CPU-only workloads. Pick Taskflow over them (and over Boost.Fiber/utl::parallel/meet1214/BS::thread_pool, which target std::thread/std::async) when the job is a DAG with heterogeneous CPU+GPU tasks, subflows, or conditional/cyclic control flow rather than a flat thread-pool or fiber replacement.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for CPU tasking; optional Nvidia CUDA Toolkit 12.0+ (nvcc) for cudaFlow GPU tasking |
| **Minimum toolchain** | C++20: GCC 11+, Clang 12+, MSVC 19.29+ (VS2019), Apple Clang 13+, NVCC 12.0+, Intel oneAPI DPC++ 2022.0+ (current README; the cited paper's benchmark used an earlier Taskflow with clang++ v10 and -std=c++17) |
| **Platforms** | Linux, Windows, macOS; x86-64 and other C++20-capable targets; optional Nvidia CUDA GPU offload via taskflow/cuda |
| **Thread safety** | README states tf::Executor's run/run_n/run_until/wait_for_all methods are thread-safe; building/mutating a tf::Taskflow graph concurrently from multiple threads is not documented as safe |
| **Drop-in for the baseline** | false — different API from oneTBB FlowGraph; graphs are built with tf::Taskflow::emplace/precede/succeed and run by tf::Executor, with no tbb::flow::graph node types |

## Gotchas

- Exception handling in tasks is a known weak spot: tf::Semaphore plus exceptions can deadlock (issue #732), and throwing many exceptions is undefined behavior that can crash or drop the exception (issue #724)
- Past releases had real throughput regressions (reported in 3.8 and 3.10, since fixed) — verify the specific version before trusting a benchmark number
- Per-worker bounded work-stealing queue defaults to 256 tasks; graphs with very deep/bursty fan-out spill into the slower unbounded overflow queue
- v4.0.0 raised the minimum standard to C++20, up from C++17 in earlier major versions — code and CI written for older Taskflow may not compile as-is

## Caveats and trade-offs

This benchmark measures Taskflow against Intel oneTBB FlowGraph (and StarPU, HPX, OpenMP), not against std::async/std::thread/std::future directly. oneTBB is already catalogued separately, so this result shows Taskflow beating another fast library, one step removed from the std baseline. The 1.9x throughput figure is the best case (5 co-runs, 1920x4096 network); memory use is 1.5-1.7x lower than oneTBB and StarPU. The paper states clang++ v10 -O2 but not the exact Xeon model, and public code for the LSDNN experiment was not confirmed, so the record is tier B, not A. GitHub's license detector reports NOASSERTION, but the LICENSE file is the standard MIT text (headed 'TASKFLOW MIT LICENSE'). The repo's benchmarks/ directory compares Taskflow to OpenMP tasking and TBB FlowGraph, not to std::async/std::thread.

Header-only but requires C++17/20; DAG/graph-based task model differs from raw std::async/std::thread call sites, so adopting it means restructuring code around tf::Taskflow/tf::Executor; larger API surface than a simple thread pool.

## Maintenance

Actively maintained (commit as recent as 2026-09-14, 12.2k stars, 36 open issues); MIT-licensed and header-only so it's easy to vendor, but GitHub's license detector shows NOASSERTION even though the LICENSE file is standard MIT text, and the current release requires a C++20 toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed paper (IEEE TPDS 2021, arXiv 2004.10908). In its abstract and Section 7.4 it reports up to 29% faster runtime, 1.5x less memory, and 1.9x higher corun throughput than oneTBB FlowGraph on LSDNN inference. The full text states clang++ v10 with -O2, but the CPU is only '40 Intel Xeon CPU cores at 2.00 GHz' with no model number, and public code for the LSDNN experiment was not confirmed, so the record falls short of A.
- **Verifier notes:** The claim matches the paper's abstract verbatim. The full paper supplies the compiler, flags, and generic hardware that the record had left null. The LICENSE file is MIT; 12,183 stars and last commit 2026-09-14 were checked and are correct.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/taskflow/taskflow>
  - <https://github.com/taskflow/taskflow/blob/master/LICENSE>
  - <https://arxiv.org/abs/2004.10908>
  - <https://arxiv.org/pdf/2004.10908>
- **Sources the enricher read:**
  - <https://github.com/taskflow/taskflow>
  - <https://github.com/taskflow/taskflow/blob/master/README.md>
  - <https://github.com/taskflow/taskflow/blob/master/LICENSE>
  - <https://github.com/taskflow/taskflow/blob/master/taskflow/core/wsq.hpp>
  - <https://github.com/taskflow/taskflow/issues>
  - <https://arxiv.org/abs/2004.10908>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/taskflow/taskflow`) · [data/wave1/enrich/raw/github_com_taskflow_taskflow.json](../../../data/wave1/enrich/raw/github_com_taskflow_taskflow.json) (enrichment confidence 0.6)

</details>
