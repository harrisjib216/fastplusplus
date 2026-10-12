# Cuckoo-GPU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only CUDA cuckoo filter with lock-free batched insert/query/delete; outpaces multi-threaded CPU cuckoo filters and GPU TCF/GQF.

| | |
|---|---|
| **Beats** | cuckoo filter |
| **Claimed result** | vs CPU Partitioned Cuckoo Filter (PCF): 175x faster insert / 351x faster query (L2-resident, 4M items) and 69x / 143x faster (DRAM-resident, 268M items); also up to 378x faster insert, 6x faster query, 258x faster delete than GPU Counting Quotient Filter (GQF), and up to 108x faster delete than GPU Two-Choice Filter (TCF) |
| **Workload** | Batch insert/query/delete of 4M (L2-resident) and 268M (DRAM-resident) items at 95% load factor with 16-bit fingerprints, vs a CPU Partitioned Cuckoo Filter (PCF) and other GPU AMQ baselines (TCF, GQF, Blocked Bloom, BCHT) |
| **Metric** | throughput |
| **Hardware** | README tables: NVIDIA GH200 Grace Hopper (72 ARM Neoverse V2 cores, H100 with 96 GB HBM3 at 3.4 TB/s, Ubuntu 24.04.3, CUDA 13.0); CPU PCF baseline on an Intel Xeon W9-3595X (60 cores / 120 threads, 256 GB DDR5, AlmaLinux 10.1). The paper also evaluates an RTX PRO 6000 Blackwell (96 GB GDDR7, 1.8 TB/s) hosted by an AMD EPYC 7713P (CUDA 12.9). |
| **Compiler and flags** | nvcc from CUDA 13.0 (GH200 system) / CUDA 12.9 (RTX PRO 6000 system) per the paper; meson.build defaults optimization=3, cpp_std=c++20, cuda_args -std=c++20 --expt-extended-lambda --expt-relaxed-constexpr -gencode sm_80/sm_90/sm_120; PCF baseline built as a CMake subproject with CMAKE_BUILD_TYPE=Release; the host C++ compiler version is not stated |
| **Adoption** | 40 stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/tdortman/Cuckoo-GPU) · [benchmark](https://github.com/tdortman/Cuckoo-GPU#performance) |

## Verdict

On an NVIDIA GH200 (H100, 96 GB HBM3, CUDA 13.0; Meson -O3, C++20; host compiler unstated) at 95% load with 16-bit fingerprints and uniform random 64-bit keys already in device memory, Cuckoo-GPU inserted 175x faster and answered positive queries 351x faster than the 120-thread Partitioned Cuckoo Filter on a Xeon W9-3595X at 4M items (L2-resident), and 69x and 143x faster at 268M items (DRAM-resident); the CPU side times a bulk construct(), GPU timings exclude host-to-device transfer, and negative queries run at roughly half the positive-query rate in the DRAM case. Against GPU filters on the same GH200 it was 2.1-378x faster than TCF and GQF but slower than the append-only Blocked Bloom filter on inserts.

## Use it when

- Your keys are fixed-size integers (for example 64-bit IDs or 2-bit-packed 31-mers), they are already in GPU memory, and you need approximate membership with deletions in batches of millions of keys or more.
- You now use a dynamic GPU filter such as GQF or TCF. On the same GH200 the README reports 2.1-4x faster inserts and 9.9-35x faster queries than TCF, and 2.6-378x faster operations than GQF, at 16-bit fingerprints and 95% load.
- The filter ranges from a few MiB (L2-resident) up to tens of GiB on a high-bandwidth GPU (H100/GH200 HBM3, RTX PRO 6000 GDDR7), or is spread over several GPUs with FilterMultiGPU.
- The pipeline is throughput-oriented, such as k-mer indexing, GPU join/semi-join prefiltering or deduplication, and one kernel launch plus a stream sync per batch is acceptable.
- You run near capacity (about 95% load) and still want steady insert throughput. The BFS eviction policy is designed for this case.

## Skip it when

- You have no NVIDIA GPU. The library is CUDA-only, and most of the quoted 69-351x gain over the CPU filter comes from the GH200 vs Xeon hardware jump.
- Your workload only inserts and queries. The append-only cuCollections Blocked Bloom filter inserts faster (Cuckoo-GPU runs at 0.35x of its speed L2-resident and 0.7x DRAM-resident) and roughly matches on DRAM-resident queries, though its FPR is much higher (2.5-6% vs about 0.045%).
- Keys start on the host or arrive in small batches. The benchmarks keep keys in device memory, excluding transfer time, and every API call ends in cudaStreamSynchronize, so small batches pay launch and sync overhead.
- You need a very low or finely tuned FPR per bit. The default 16-bit tags in 16-slot buckets give about 0.045% FPR vs about 0.005-0.011% for the CPU partitioned cuckoo filter with 4-slot buckets, and tags can only be 8/16/32 bits with power-of-two bucket sizes.
- You need queries to run at the same time as inserts or deletes (the paper warns of torn reads), variable-length or string keys, Windows support, or a versioned stable release. The Meson project version is 0.1 and there are no tags.

## How it is fast

Each key gets one thread that does partial-key cuckoo hashing with xxHash64: the upper 32 bits give the fingerprint and the lower 32 bits give the primary bucket; buckets hold 16 slots packed into 64-bit words, so SWAR bit tricks find empty or matching slots and each insert or delete is a single-word atomic compare-and-swap, with no locks. Unlike GQF and TCF, which organise memory for cache locality, it accepts random access and relies on HBM/GDDR bandwidth. Queries use non-atomic 128-bit vector loads (256-bit ld.global.nc on compute capability 10.0+), so a positive hit often needs one memory transaction. At high load a breadth-first eviction heuristic first checks up to bucketSize/2 candidates for a free alternate slot before extending a chain, which the paper says cut tail eviction lengths and gave up to 25% higher insert throughput than greedy DFS on GH200.

## Compared with alternatives

Every catalogued sibling (Prefix Filter, Xor/xor_singleheader, BuRR, Morton, Vacuum, Windowed Cuckoo, Ada-BF, SuRF, ChainedFilter) runs on the CPU. Pick Cuckoo-GPU when both the keys and the code that consumes the filter are already on an NVIDIA GPU and you need deletes at billions of operations per second. If keys live on the host, a CPU cuckoo variant such as Morton or Vacuum avoids the transfer and the GPU dependency, and Xor/BuRR/Prefix target lower space or faster builds.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | The single-GPU filter needs only the CUDA Toolkit (Thrust, CUB, libcu++). FilterMultiGPU needs gossip (Funatiq/gossip), and the top-level meson.build always pulls it in. The experimental IPC server uses POSIX shared memory, semaphores and cudaIpcMemHandle. Tests and benchmarks also pull cuCollections, BGHT, saltsystemslab gpu-filters (TCF/GQF), tum-db partitioned-filters, Google Benchmark, GoogleTest, CLI11 and KMC as Meson wraps. |
| **Minimum toolchain** | The README requires CUDA Toolkit 12.9+, a C++20 compiler and Meson 1.3+ if you use its build. The dev shell moved to CUDA 13.2 in June 2026, and the paper used CUDA 12.9 and 13.0. The project compiles with -std=c++20 --expt-relaxed-constexpr --expt-extended-lambda, so mirror those flags. The host compiler version is not documented. |
| **Platforms** | NVIDIA GPUs only. The build targets sm_80, sm_90 and sm_120 plus compute_75 PTX, and 256-bit loads are used only on compute capability 10.0+. Evaluated on Linux x86-64 (EPYC 7713P + RTX PRO 6000 Blackwell) and aarch64 (GH200). Windows is not documented, and the IPC path is POSIX-only. Single-GPU kernels appear to need HMM or ATS (see gotchas). |
| **Thread safety** | Concurrent inserts and deletes on the device are lock-free through per-word CAS. Queries use non-atomic vector loads and, per the paper, must not run at the same time as inserts or deletes because of torn reads. The host Filter object cannot be copied and has no internal locking; using it from several host threads or streams is not documented. |
| **Drop-in for the baseline** | partial — it keeps cuckoo-filter semantics (insert, contains and delete, false positives, rare false deletes from fingerprint collisions), but the API is batched over GPU device pointers or thrust vectors instead of a per-key host API, and the headers have no serialization. |

## Gotchas

- Kernels receive `this`, the host-side Filter object (the README and tests create it on the stack), and read numBuckets and d_buckets through that pointer. This only works if the GPU can read pageable host memory: ATS on Grace Hopper, or HMM (per NVIDIA: Linux with the open r535+ driver, CUDA 12.2+, kernel 6.1.24+, x86-64). Elsewhere you should expect illegal-address faults. FilterMultiGPU avoids the problem by placing each Filter in cudaMallocManaged memory. This is inferred from the code and not documented.
- A failed insert (after maxEvictions, default 500) is not rolled back. The new fingerprint has already been swapped in, and the one being carried, which belongs to a previously stored key, is dropped, so a reported failure can cause a false negative for a different key. There is no victim stash. The repo's own NearCapacityInsertion test only requires 99% of inserted keys to be found, and the paper lists insertion failures at extreme load as a limitation that needs a fallback.
- Every CUDA error inside the library, including a failed cudaMalloc in the constructor, goes through CUCKOO_CUDA_CALL, which prints and calls exit(). There are no exceptions or error codes to handle.
- The default XorAltBucketPolicy rounds the bucket count up to a power of two, so memory can almost double just past a 2^n boundary. OffsetAltBucketPolicy avoids this at the cost of one fingerprint bit; it has about 34% slower positive queries when L2-resident and equal speed when DRAM-resident. Keys are hashed as raw bytes (xxHash64 over sizeof(T)), so use trivially copyable key types without padding. Thread indices are 32-bit, so keep each batch under 2^32 keys.

## Known shortcomings

- The \~350x is mostly the GPU-vs-CPU hardware jump (GH200 / RTX PRO 6000 Blackwell vs a partitioned cuckoo filter on a 120-thread Xeon W9-3595X); against the GPU Bloom filter GBBF in DRAM it is 0.7x on inserts and 0.9x on queries. Host compiler version unstated.
- Kernels receive the host-side filter object pointer, so they likely need HMM/ATS unified memory and fault elsewhere (inferred from code, undocumented). A failed insert (&gt;500 evictions) drops a carried fingerprint of an older key, causing false negatives (no stash); errors call exit(); every call synchronizes the stream; concurrent query with insert/delete gives torn reads.
- Benchmarks time keys already on the device (no transfers) and bulk-construct the CPU baseline. Slower than cuCollections' blocked Bloom filter on inserts (0.35x/0.7x); FPR 0.045% vs 0.011% for the CPU partitioned cuckoo filter; the XOR placement policy forces power-of-two sizing. CUDA/Linux only, v0.1 with no tags.

## Caveats and trade-offs

Companion code for arXiv:2603.15486 (v1 2026-03-16; Dortmann, Vieth, Schmidt, JGU Mainz; the id resolves), with DOI 10.1145/3832810.3832822 resolving to the ACM DL. The CPU baseline is the partitioned cuckoo filter of Schmidt et al. (VLDB 2021, tum-db/partitioned-filters) at 120 threads, not the original Fan et al. cuckoofilter. The CPU-vs-GPU speedups mix hardware (GH200 vs Xeon W9-3595X), so much of the 69-351x comes from the platform jump rather than the algorithm alone. Against the append-only GPU Blocked Bloom filter (cuCollections) it is slower: 0.35x insert (L2) and 0.7x insert / 0.9x query (DRAM).

Requires a CUDA-capable NVIDIA GPU vs a CPU-only cuckoo filter; deliberately sacrifices cache locality to saturate GPU memory bandwidth, which would be a poor strategy on CPU

## Maintenance

Actively maintained research companion code for an ACM-published paper: last commit 2026-09-13, 40 stars, one merged PR, no open issues, no tagged releases. It is BSL-1.0 and header-only, so vendoring include/cuckoogpu/ is easy, but expect research-grade APIs that call exit() on errors.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance tables show 175x/351x (L2) and 69x/143x (DRAM) vs the CPU Partitioned Cuckoo Filter plus the GQF/TCF numbers exactly as claimed; the benchmark code is public (benchmarks/cuckoo_vs_partitioned.cu, benchmarks/load_factor_benchmark.cu), flags are in meson.build (optimization=3, C++20, sm_80/90/120 gencode; PCF built as a CMake Release subproject), and the arXiv paper states the CUDA versions (13.0 on GH200, 12.9 on RTX PRO 6000) and CPU models (Grace Neoverse V2, Xeon W9-3595X, EPYC 7713P).
- **Verifier notes:** The arXiv id is valid and its abstract matches the README: up to 378x/6x/258x insert/query/delete vs GQF, 4.1x/34.7x/107x vs TCF, and up to 350x vs the fastest multi-threaded CPU cuckoo filter, measured on GH200 and RTX PRO 6000 Blackwell. Tier A is kept, with one gap: the host gcc/clang version is unstated, but nvcc versions and build flags are explicit.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tdortman/Cuckoo-GPU>
  - <https://github.com/tdortman/Cuckoo-GPU#performance>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/meson.build>
  - <https://github.com/tdortman/Cuckoo-GPU/tree/main/benchmarks>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/benchmarks/meson.build>
  - <https://arxiv.org/abs/2603.15486>
  - <https://arxiv.org/pdf/2603.15486>
  - <https://doi.org/10.1145/3832810.3832822>
- **Sources the enricher read:**
  - <https://github.com/tdortman/Cuckoo-GPU>
  - <https://github.com/tdortman/Cuckoo-GPU#performance>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/CuckooFilter.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/bucket_policies.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/hashutil.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/helpers.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/CuckooFilterMultiGPU.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/include/cuckoogpu/CuckooFilterIPC.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/meson.build>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/meson.options>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/tests/test_cuckoo_filter.cu>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/examples/main.cu>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/benchmarks/cuckoo_vs_partitioned.cu>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/benchmarks/benchmark_common.cuh>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/.gitlab-ci.yml>
  - <https://github.com/tdortman/Cuckoo-GPU/blob/main/nix/shells/default/default.nix>
  - <https://github.com/tdortman/Cuckoo-GPU/commits/main>
  - <https://github.com/tdortman/Cuckoo-GPU/commit/b0a317a119521724edb8eaefa870082d344d236a>
  - <https://github.com/tdortman/Cuckoo-GPU/pull/1>
  - <https://github.com/tdortman/Cuckoo-GPU/issues>
  - <https://arxiv.org/pdf/2603.15486>
  - <https://developer.nvidia.com/blog/simplifying-gpu-application-development-with-heterogeneous-memory-management/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tdortman/cuckoo-gpu`) · [data/wave6/enrich/raw/github_com_tdortman_cuckoo_gpu.json](../../../data/wave6/enrich/raw/github_com_tdortman_cuckoo_gpu.json) (enrichment confidence 0.8)

</details>
