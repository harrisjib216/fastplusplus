# Thrust (thrust::sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 (Thrust, with portions under BSL-1.0 and a FreeBSD-derived licence); CUB, which supplies thrust::sort's CUDA radix sort, is BSD-3-Clause; libcu++ is Apache-2.0 WITH LLVM-exception` · 🟢 active

> Header-only CUDA algorithms library; thrust::sort's GPU radix sort beat single-threaded std::sort 80-320x on large int arrays.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | thrust::sort vs std::sort on int arrays, medians of 7 runs after a warm-up in ms (perf/data/sort.csv column median_ms; README sort table): 1,048,576 elements in [0,1000): 0.67 vs 54.6 ms (about 81x, derived from page data); 16,777,216 in [0,1000): 3.73 vs 912.7 ms (about 245x, derived from page data); 1,048,576 any int: 0.90 vs 88.8 ms (about 99x, derived from page data); 8,388,608 any int: 2.52 vs 801.6 ms (about 318x, derived from page data). GPU (Tesla T4) vs one CPU thread, host/device transfers excluded. |
| **Workload** | CIS 565 student project sorts int arrays of 1,048,576 to 16,777,216 elements (values in [0,1000) or full int range) with std::sort on the CPU and thrust::sort on a Tesla T4, host/device transfers excluded. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon @ 2.30GHz (4 vCPUs, Google Cloud VM), NVIDIA Tesla T4 16 GB |
| **Compiler and flags** | CMake Release build (the project's CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release), CUDA 13.3, driver 610.57, Ubuntu 22.04.5; host compiler and its flags not stated |
| **Adoption** | NVIDIA/thrust (archived 2024-03-21) 5.0k stars; NVIDIA/cccl 2.5k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/NVIDIA/cccl) · [benchmark](https://github.com/Josh0323/Project2-Stream-Compaction) |

## Verdict

A third-party CUDA course project (Josh0323/Project2-Stream-Compaction) timed thrust::sort on a Tesla T4 (CUDA 13.3, CUDA events) against single-threaded std::sort on a 2.30 GHz Xeon cloud vCPU (std::chrono, nvcc Release build, host compiler unstated). Medians of 7 runs after a warm-up, copies to and from the device outside the timers: 0.67 vs 54.6 ms at 1M ints in [0,1000), 3.73 vs 912.7 ms at 16M, and 0.90 vs 88.8 ms and 2.52 vs 801.6 ms at 1M and 8M full-range ints. Its --stress mode checks thrust::sort against std::sort on 61 sizes (0 failures reported), but at 256 elements Thrust was about 13x slower than std::sort (derived from page data).

## Use it when

- The keys are already on an NVIDIA GPU, e.g. as part of a CUDA pipeline: sorting there avoids two PCIe transfers and beats any CPU sort from a few thousand elements up.
- Large arrays (about 10^5 to 10^8+) of int, unsigned, float, double, __half or bfloat16 with ascending or descending order: these take the radix path.
- Key-value sorts (thrust::sort_by_key) of primitive keys, e.g. building sort-based groupings or compaction indices on the GPU.
- Code that also needs a CPU fallback: the same Thrust calls can be built against the OpenMP, TBB or serial backends by changing THRUST_DEVICE_SYSTEM, with lower speed (see when_not_to_use).

## Skip it when

- Small arrays: in the measured run thrust::sort cost about 0.037 ms even for 256 ints, where std::sort took 0.003 ms; it only pulled ahead at about 2,048 elements (derived from page data).
- Data that lives on the host and is sorted once: the benchmark excluded the host-to-device and device-to-host copies, which the speedup does not account for.
- Custom comparators or struct keys: these use the merge-sort fallback. Issue #754 reported large slowdowns and code bloat from forced unrolling with complex comparators (closed in April 2025; the workaround was a __noinline__ operator()).
- CPU-only machines: with the OpenMP backend, thrust::sort on 100M floats took 80-117 s versus 31-34 s for std::sort, because the final merge runs on one thread (issue #1244, still open).
- Memory-tight GPUs: the radix path allocates a second key buffer of n\*sizeof(Key), plus CUB's scratch space, on every call.

## How it is fast

For arithmetic keys (and __half or __nv_bfloat16) with the default less or greater comparator, Thrust's CUDA backend picks at compile time (CUB __can_use_radix_sort) a CUB DeviceRadixSort, an LSD radix sort. In current CCCL this is the 'onesweep' variant: one histogram kernel, then one kernel per digit pass that scatters with decoupled look-back prefix sums. Thousands of GPU threads work on the data in device memory, so a pass runs at close to memory bandwidth. Any other key type or comparator falls back to CUB's DeviceMergeSort, a comparison sort that the benchmark did not measure.

## Compared with alternatives

Pick Thrust when the data already lives on an NVIDIA GPU or the batch is large enough to repay the PCIe copies. On the CPU, Highway vqsort or x86-simd-sort (SIMD, about 4-10x std::sort) and IPS4o (parallel) avoid the GPU dependency and the transfer cost, and they win on small or host-resident inputs.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA Toolkit (nvcc or another CUDA compiler) for the GPU backend; optional OpenMP or TBB for the CPU backends. Thrust ships inside the CUDA Toolkit and can also be used from a newer CCCL checkout via -I. |
| **Minimum toolchain** | CCCL 3.x: C++17, CUDA Toolkit 12.x or 13.x, GCC 7+ on Linux (CCCL 2.x supports CTK 11.1-12.x) |
| **Platforms** | NVIDIA GPUs supported by the CUDA Toolkit (CTK 13.x: sm_75 and newer; CTK 12.x: sm_50 and newer); Linux and Windows host compilers that the CTK supports |
| **Thread safety** | Each call runs on the stream carried by its execution policy and synchronizes before returning with the default policy. Concurrent calls from several host threads are not documented in the README. |
| **Drop-in for the baseline** | partial: same (first, last[, comp]) signature, but the GPU speedup requires device-resident data (device_vector or thrust::device policy) and an explicit copy in and out; std::vector iterators run on the host backend |

## Gotchas

- Each thrust::sort call allocates and frees its temporary storage with cudaMalloc/cudaFree unless a caching allocator is passed through the execution policy. In the benchmark's Nsight trace this allocation was up to about 70% of a 1M-element Thrust call, and the measured time jumped from 0.09 to 0.32 ms between 131,072 and 262,144 elements.
- The radix path sorts all sizeof(Key)\*8 bits; thrust::sort cannot be told that values are small, so [0,1000) keys took about the same passes as full-range ints (0.67 vs 0.90 ms at 1M). Use cub::DeviceRadixSort with begin_bit/end_bit for that.
- Floats are sorted by bit pattern: -0.0 and +0.0 compare equal (stable order kept), and NaNs are placed by their bits (negative NaNs first, positive NaNs last), where std::sort with NaNs has undefined behaviour.
- Errors surface as exceptions (thrust::system_error from throw_on_error, bad_alloc when the temporary allocation fails), and the default policy blocks until the sort finishes; use thrust::cuda::par_nosync to avoid the sync.

## Known shortcomings

- thrust::sort numbers come from a student project README and perf/data/sort.csv (Tesla T4, medians of 7 runs): GPU against one CPU core running std::sort, transfers excluded, no host compiler or CPU model. Licence composite: Apache-2.0 (Thrust) and BSD-3-Clause (CUB).
- Enricher: thrust::sort numbers check out (sort.csv medians, --stress mode verifies against std::sort with 0 failures) but per-call cudaMalloc/cudaFree temp storage sits inside the timer (up to about 70% of a 1M call), Thrust is about 13x slower at 256 elements and wins only from about 2048 (derived from page data); the radix path sorts all 32 bits whatever the value range; non-primitive keys or custom comparators fall back to merge sort (#754); the OMP backend takes 80-117 s vs std::sort 31-34 s on 100M floats (#1244, open).

## Caveats and trade-offs

This compares a GPU radix sort (Thrust dispatching to CUB) with single-threaded std::sort on one vCPU, so it measures GPU vs one CPU core and excludes host/device transfers (std::copy and device_vector construction sit outside the timers); it is not a library-to-library win. The thrust::sort timing includes CUB's per-call temporary-storage cudaMalloc/cudaFree. The evidence is a student project README (Josh0323/Project2-Stream-Compaction, fork of the course template, 0 stars, no licence; one machine, host compiler and standard library not stated, CPU model only 'Xeon @ 2.30GHz', 16M full-range run missing because of a VM restart), so tier C. The Thrust project README and NVIDIA/cccl contain no performance numbers; a vendor claim that thrust::sort is '5x to 100x faster than STL and TBB' was seen only as a search-result snippet and is not used. Thrust development moved into NVIDIA/cccl (standalone NVIDIA/thrust archived 2024-03-21); last_commit and star counts for the live repo are from NVIDIA/cccl. Category changed from the guessed thread-pools-work-stealing because the only numeric comparison is a sort.

Requires a CUDA GPU for the speedups (Thrust also has TBB, OpenMP and serial CPU backends, but the benchmark measured the CUDA backend). Header-only; device memory and transfer costs are not included in the sorted time; CUDA backend uses CUB radix sort for primitive keys with the default comparator and falls back to merge sort otherwise.

## Maintenance

Actively developed inside NVIDIA/cccl (14,947 commits, 2.5k stars; the standalone NVIDIA/thrust repo was archived in 2024) and shipped with every CUDA Toolkit; Thrust is Apache-2.0 and CUB is BSD-3-Clause, so it is copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party student project (0 stars, fork of the CIS5650-Fall-2026 course template) with public benchmark code (src/perf.cpp, stream_compaction/cpu.cu, stream_compaction/thrust.cu) and raw CSV, but the host compiler and its flags are not stated and the CPU is only 'Intel Xeon @ 2.30GHz (4 vCPUs)', so not A; not a peer-reviewed paper or well-known suite, so not B.
- **Verifier notes:** All four table rows match the README and perf/data/sort.csv (units are ms, medians of 7 runs); timers checked in cpu.cu and thrust.cu exclude copies. Evidence stays C: obscure student project, GPU vs one CPU core, no host compiler or CPU model. Metadata confirmed: NVIDIA/cccl 2.5k stars, last commit 2026-10-09, not archived; licence is a composite (Apache-2.0 Thrust, BSD-3-Clause CUB).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 11); enricher w11 pair-028
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/README.md>
  - <https://github.com/Josh0323/Project2-Stream-Compaction>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/src/perf.cpp>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/perf/data/sort.csv>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/cpu.cu>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/thrust.cu>
  - <https://github.com/NVIDIA/cccl>
  - <https://github.com/NVIDIA/cccl/commits/main>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/README.md>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/src/perf.cpp>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/perf/data/sort.csv>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/cpu.cu>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/thrust.cu>
  - <https://raw.githubusercontent.com/Josh0323/Project2-Stream-Compaction/HEAD/stream_compaction/common.h>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/thrust/thrust/system/cuda/detail/sort.h>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/cub/cub/device/device_radix_sort.cuh>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/cub/cub/device/dispatch/dispatch_radix_sort.cuh>
  - <https://raw.githubusercontent.com/NVIDIA/cccl/main/cub/cub/util_type.cuh>
  - <https://github.com/NVIDIA/cccl>
  - <https://github.com/NVIDIA/cccl/issues?q=is%3Aissue%20thrust%3A%3Asort%20performance>
  - <https://github.com/NVIDIA/cccl/issues/1244>
  - <https://github.com/NVIDIA/cccl/issues/754>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/nvidia/cccl`) · [data/wave11/enrich/raw/github_com_nvidia_cccl.json](../../../data/wave11/enrich/raw/github_com_nvidia_cccl.json) (enrichment confidence 0.75)

</details>
