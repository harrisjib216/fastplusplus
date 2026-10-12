# PHOBIC-GPU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Vulkan GPU builder for PHOBIC minimal perfect hash functions; builds about 62x faster than 8-thread CPU PHOBIC.

| | |
|---|---|
| **Beats** | PHOBIC (CPU construction, part of jermp/pthash) |
| **Claimed result** | PHOBIC-GPU constructs an MPHF at 2.17 bits/key in 28 ns/key (GPU + 8 CPU threads), and the MPHF answers queries in 37 ns on the CPU (abstract, Table 1). At lambda=9.0 with interleaved Rice coding, PHOBIC-GPU gives 1.76 bits/key, 52 ns/query and 27 ns/key construction. CPU PHOBIC gives 1.74 bits/key, 50 ns/query, 9,171 ns/key (1 thread) and 1,781 ns/key (8 threads). The paper states a 62x construction speedup over the multithreaded CPU implementation and about 30x lower energy (Table 1, Sec. 5.2 of arXiv:2404.18497). |
| **Workload** | MPHF construction on 100 million random string keys (random length 10-50 characters). GPU construction (plus 8 CPU threads) is compared with CPU PHOBIC at 1 and 8 threads, for the same configurations (lambda=9, 13, 14; interleaved Rice/Compact coding). All queries run on the CPU. |
| **Metric** | build-time |
| **Hardware** | Intel Core i7-11700 (48 KiB L1d and 512 KiB L2 per core), 64 GiB DDR4, Ubuntu 22.04.1; GPU: Nvidia RTX 3090 |
| **Compiler and flags** | GCC 11.4.0, -march=native -O3; GPU accessed via Vulkan 1.3.236 |
| **Adoption** | 4 stars |
| **Last commit** | 2025-07-03 |
| **Links** | [repository](https://github.com/stefanfred/PHOBIC-GPU) · [benchmark](https://arxiv.org/abs/2404.18497) |

## Verdict

The authors' PHOBIC paper (arXiv 2404.18497, ESA 2024, Table 1) built MPHFs on 100M random 10-50 character strings. PHOBIC-GPU (RTX 3090 via Vulkan 1.3.236, plus 8 CPU threads) took 27 ns/key at lambda=9 with interleaved Rice coding (1.76 bits/key, 52 ns CPU query). The authors' own CPU PHOBIC took 1,781 ns/key with 8 threads and 9,171 ns/key with 1 thread on an i7-11700 (GCC 11.4.0 -O3 -march=native). The text calls this a 62x speedup (the table itself gives about 66x) and about 30x less energy (405 W vs 195 W draw). No std:: baseline is involved: this compares the same algorithm on a GPU and on a CPU.

## Use it when

- Rebuilding large MPHFs (the paper benchmarks 10^8 string keys) where build time dominates and a desktop GPU is idle: 27-28 ns/key vs 1,781 ns/key for 8-thread CPU PHOBIC at lambda=9.
- Space-efficient settings (lambda 9-14, about 1.67-1.76 bits/key) that are too slow to build on a CPU. For example, lambda=13 gives 1.68 bits/key at 560 ns/key on the GPU, and the paper says much larger lambda is not feasible on the CPU.
- Query-heavy lookup tables that need PTHash-class CPU query latency (37-52 ns) but GPU-speed builds. RecSplit-GPU builds equally fast but queries in 126-147 ns.
- Linux machines with a Vulkan 1.3 GPU that supports VK_KHR_maintenance4, where build energy matters: the paper measures about 30x less energy per build than the 8-thread CPU.

## Skip it when

- Small inputs or small lambda. Moving the keys to the GPU dominates there: Fig. 6 in the paper shows the GPU needs large n (many partitions) and large lambda to pay off.
- When you need faster queries. Queries run the same CPU code as PHOBIC, so only construction gets faster.
- When you need to save and load the function, build in external memory, or go past 2^32 keys. The MPHF class has no serialization, the key count is a uint32_t, and all keys are uploaded to the device at once (16 bytes/key for the key buffer alone). pthash covers these cases.
- Machines without a Vulkan GPU and driver. Only an Nvidia RTX 3090 on Linux was benchmarked, and CI only builds on Ubuntu 22.04 without running anything.
- Production use without in-house maintenance: this is research code with 4 stars, one merged PR, no issues filed, and GPL-3.0 copyleft.

## How it is fast

It runs the PHOBIC algorithm: PTHash-style bucket placement with an optimized bucket-size distribution (OptBucketer), tiny partitions of about 2,048-2,500 keys, and interleaved coding of the seeds. Each partition maps to one Vulkan compute workgroup, and that partition's occupancy bitmap fits in fast shared memory. A per-partition counting-sort shader orders buckets by decreasing size. All threads in the workgroup then search seeds together with a single-loop version of the usual seed/key nested loop: a shared atomicAdd hands out the next candidate, and atomicMin keeps the smallest working seed, which avoids warp divergence. Seeds encode p = s\*m + d (an additive displacement), so trying the next candidate only adds 1 to cached positions. The CPU uses OpenMP for the xxHash3-128 master hashing and the final Rice/Compact encoding.

## Compared with alternatives

Choose this over PTHash, whose master branch now ships CPU PHOBIC as pthash::phobic, only when you have a Vulkan GPU and build time on about 10^8 keys dominates; PTHash gives the same query path plus serialization and multithreaded or external-memory builds. Choose it over GpuRecSplit (CUDA) when query latency matters: build speed is similar (27 vs 24 ns/key at about 1.8 bits/key) but CPU queries take 52 ns vs 126 ns; GpuRecSplit is the better choice below 1.6 bits/key (1.58 bits/key at 80 ns/key).

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Vulkan SDK (libvulkan, headers, glslc shader compiler), OpenMP; git submodules xxHash, jermp/essentials, tlx (benchmark CLI only); bundled fastmod.h |
| **Minimum toolchain** | C++17, CMake 3.19+, Vulkan 1.3 (shaders compiled with --target-env=vulkan1.3, SPIR-V 1.5); the paper used GCC 11.4.0 |
| **Platforms** | Linux with a Vulkan 1.3 GPU that has VK_KHR_maintenance4 (prefers a discrete GPU; benchmarked only on an Nvidia RTX 3090); the query-side code is plain C++ |
| **Thread safety** | Not documented. The builder shares a process-wide Vulkan singleton (App::getInstance()) and one compute queue, so assume one build at a time. Queries use a const, read-only operator(). |
| **Drop-in for the baseline** | partial — same algorithm with nearly the same space and query time as CPU PHOBIC (1.76 vs 1.74 bits/key, 52 vs 50 ns at lambda=9), but it is a separate phobicgpu::MPHF type with its own encoders and no save/load, so it is not interchangeable with pthash::phobic / dense_partitioned_phf |

## Gotchas

- Compiled shaders are loaded at runtime from the relative path "shaders/&lt;name&gt;.comp.spv" under the current working directory, but the build writes them to \${CMAKE_BINARY_DIR}/shaders. A process started from any other directory throws "failed to open file".
- The README says to link `PHOBIC-GPU`, but the CMake target is actually `GpuPTHash` (MPHF-Experiments links `GpuPTHash`).
- Debug builds (NDEBUG unset) turn on VK_LAYER_KHRONOS_validation and throw std::runtime_error if the layer is not installed. All Vulkan failures, including out-of-memory on the device, are reported as std::runtime_error.
- The example says the partition size should be tuned for your GPU (defaults: 2,048 in MPHFconfig, 2,500 in the paper). MPHF-Experiments has to `#undef MAX_BUCKET_SIZE` between including pthash.hpp and phobic_gpu_mphf.hpp.

## Caveats and trade-offs

The speedup compares an RTX 3090 GPU with an 8-thread i7-11700 CPU, so it depends on the hardware. The paper notes the GPU only wins for large n and large lambda; at small lambda, transferring the input to the GPU dominates. Queries are not faster: they run on the CPU and are the same as CPU PHOBIC. The system draws about 405 W during the GPU search vs 195 W for the multithreaded CPU. Needs a Vulkan-capable GPU. The baseline is the authors' own CPU PHOBIC (jermp/pthash phobic branch), not std::unordered_map, CMPH or BBHash. Only 4 GitHub stars, and the last commit was 2025-07-03.

Requires Vulkan-capable GPU for construction; only construction is GPU-accelerated, queries still run on CPU; the CPU PHOBIC implementation it accelerates lives inside the already-catalogued jermp/pthash repo (branch 'phobic'), so this repo only supplies the GPU construction path

## Maintenance

Stale research code: the last commit (2025-07-03) only edited the README, and the last code change was 2025-03-20. It has 4 stars and is GPL-3.0 (but CITATION.cff says AGPL-3.0-or-later). You can use it via CMake add_subdirectory, but expect to fix things yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The full PHOBIC paper (ESA 2024) compares PHOBIC-GPU against CPU PHOBIC in Table 1 and Fig. 6a. It states the CPU (Intel Core i7-11700), the GPU (Nvidia RTX 3090, Vulkan 1.3.236), the compiler (GCC 11.4.0) and the flags (-march=native -O3). The benchmark code is public: ByteHamster/MPHF-Experiments src/tablePhobic.cpp (a 'CPU vs GPU' block plus GpuPhobicContender and PhobicContender rows), and stefanfred/PHOBIC-GPU benchmark.cpp.
- **Verifier notes:** The full PDF was readable. The abstract numbers are verbatim and Table 1 supports the CPU-vs-GPU speedup. The ratio derived from Table 1 (1,781/27, about 66x) differs slightly from the 62x stated in the text, so the claim cites the paper's own 62x. I upgraded the tier to A because the paper states the compiler, flags, CPU and GPU, and the benchmark code is public.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2404.18497>
  - <https://arxiv.org/pdf/2404.18497>
  - <https://github.com/stefanfred/PHOBIC-GPU>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/CMakeLists.txt>
  - <https://github.com/stefanfred/PHOBIC-Scripts>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tablePhobic.cpp>
- **Sources the enricher read:**
  - <https://github.com/stefanfred/PHOBIC-GPU>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/README.md>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/CMakeLists.txt>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/example.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/benchmark.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/.gitmodules>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/.github/workflows/build.yml>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/LICENSE>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/CITATION.cff>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobic_gpu_mphf.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/mphf.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/mphf_builder.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/mphf_config.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/hasher.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/bucketers.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/phobicGpu/shader_constants.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/app/app.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/app/check.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/app/ioutil.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/app/utils.h>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/encoders/pilotEncoders/interleaved_encoder.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/encoders/pilotEncoders/interleaved_encoder_dual.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/include/encoders/partitionOffsetEnocders/diff_partition_offset_encoder.hpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/src/app/app.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/src/app/shader.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/src/app/memory.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/src/search_stage.cpp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/search.comp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/sort_sum.comp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/bucket_sizes.comp>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/key_mapping.glsl>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/hashing.glsl>
  - <https://github.com/stefanfred/PHOBIC-GPU/blob/main/shaders/constants.glsl>
  - <https://github.com/stefanfred/PHOBIC-GPU/commits/main>
  - <https://github.com/stefanfred/PHOBIC-GPU/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://arxiv.org/abs/2404.18497>
  - <https://arxiv.org/pdf/2404.18497>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tablePhobic.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/bucketplacement/GpuPhobicContender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/bucketplacement/GpuPhobicContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/CMakeLists.txt>
  - <https://github.com/jermp/pthash>
  - <https://github.com/jermp/pthash/blob/master/README.md>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/stefanfred/phobic-gpu`) · [data/wave1-phf/enrich/raw/github_com_stefanfred_phobic_gpu.json](../../../data/wave1-phf/enrich/raw/github_com_stefanfred_phobic_gpu.json) (enrichment confidence 0.82)

</details>
