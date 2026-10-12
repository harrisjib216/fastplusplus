# SimdRecSplit / GpuRecSplit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0 WITH GCC-exception-3.1` · 🟢 active

> SIMD, multicore and GPU construction of RecSplit minimal perfect hashes; single-threaded builds about 4x faster than BBHash at similar space.

| | |
|---|---|
| **Beats** | BBHash |
| **Claimed result** | Single-threaded on 10M keys, SIMDRecSplit (l=5, b=5) builds in 49 ns/key at 2.96 bits/key. BBHash gamma=1.0 needs 208 ns/key at 3.059 bits/key, so SIMDRecSplit is about 4.2x faster and smaller (derived from page data). BBHash gamma=5.0 is about as fast (50 ns/key) but needs 6.871 bits/key. Against the original RecSplit, speedups reach 50x single-threaded SIMD, 239x with 16 threads and 5438x on an RTX 3090 GPU (l=18, b=50, 5M objects; paper Table 1). |
| **Workload** | Single-threaded MPHF construction for 10 million keys, which are random strings of uniform length 10-50 (not 64-bit integers). SIMDRecSplit is compared against BBHash, RecSplit, PTHash and SicHash on bits/key and construction/query ns per key (paper Table 3). The GPU and multi-core speedups come from paper Table 1 (5 million objects, random 128-bit master hash codes, relative to the original single-threaded RecSplit). |
| **Metric** | build-time |
| **Hardware** | Intel i7-11700 (8 cores/16 threads, 2.5GHz base, AVX-512); NVIDIA RTX 3090 for the GPU variant |
| **Compiler and flags** | GNU C++ (gcc) 11.2.0, -O3 -march=native; CUDA 11 for the GPU variant |
| **Adoption** | 16 stars |
| **Last commit** | 2026-01-04 |
| **Links** | [repository](https://github.com/ByteHamster/GpuRecSplit) · [benchmark](https://arxiv.org/abs/2212.09562) |

## Verdict

Paper Table 3 (arXiv 2212.09562v2) measures 10M random strings of length 10-50, single-threaded, with GCC 11.2 -O3 -march=native on an AVX-512 Intel i7-11700. SIMDRecSplit l=5,b=5 builds at 49 ns/key and 2.96 bits/key, against BBHash gamma=1.0 at 208 ns/key and 3.059 bits/key (about 4.2x, derived); BBHash gamma=5.0 matches the speed but needs 6.871 bits/key. The 50x/239x/5438x speedups over original RecSplit (SIMD 1 thread, 16 threads, RTX 3090) come from Table 1 (l=18, b=50, 5M random 128-bit keys), and there is no std baseline.

## Use it when

- Static sets of millions of string keys on x86-64 with AVX2/AVX-512, when build time and space both matter (1.81 bits/key at 107 ns/key build, single-threaded, 10M keys).
- Very compact MPHFs (about 1.56-1.7 bits/key) that original RecSplit takes hours to build. For 5M keys at 1.56 bits/key, the paper reports about 2 minutes on the CPU and 5 s on an RTX 3090, against 1.5 hours for the original code.
- Multi-core offline builds: buckets are split across threads without changing the query layout, and the paper shows good scaling on 8-core and 64-core machines.
- You have an NVIDIA GPU and want the most space-efficient settings: GPURecSplit reaches 1.496 bits/key with l=24.

## Skip it when

- Latency-bound lookups: queries take 71-110 ns/key, against 20-35 ns for PTHash and 36-51 ns for BBHash (Table 3). Queries run on the CPU and walk a Golomb-Rice-coded tree.
- Non-x86 CPUs, or CPUs without AVX2/AVX-512. SIMDRecSplit is x86-only and falls back to slow emulated SIMD without AVX2. On an AVX2-only AMD EPYC, sequential SIMDRecSplit took 4.6x longer than on the AVX-512 Intel machine. On ARM, only the non-SIMD variant reportedly builds, and CI does not test it.
- Dynamic key sets, or input with possible duplicate keys. The structure is static, and duplicate keys make construction never return.
- Projects that cannot take GPL-3.0 (even with the GCC Runtime Library Exception), or that must ship portable binaries, because the CMake targets force -march=native onto consumers.
- GPURecSplit in a process that uses CUDA for other work (see gotchas). The GPU also gains little for space-inefficient settings, where host-device transfers dominate.

## How it is fast

Rotation fitting splits a leaf's keys into two halves by one hash bit, then cyclically rotates one half's bit mask to fill the other's holes, so one hash evaluation tests up to m candidate bijections (up to 3x faster construction per the paper). The brute-force seed search is vectorized: each AVX2/AVX-512 lane (Vector Class Library) tests a different seed, and splitting counts use packed 8-bit counters. Independent buckets are radix-sorted with IPS2Ra and split across threads. On the GPU, each leaf or split runs as a CUDA thread block, and same-shaped trees are batched into one kernel.

## Compared with alternatives

On 10M string keys it builds 1.81 bits/key in 107 ns/key, against SicHash's 2.41 bits in 119 ns and PTHash's 3.31 bits in 199 ns, and it builds Sux RecSplit's \~1.8 bits/key 6.6x faster with about 7% slower lookups. Pick PTHash instead when lookups dominate (20-35 vs 71-110 ns), and ShockHash (1.489 bits/key, per the author) for space near the 1.44-bit bound.

## Integration

| | |
|---|---|
| **Form** | shared lib: header-only class templates, plus one small CMake-built shared library (Ips2raRecSplitSorter) that every target links. Consume it via git clone --recursive and add_subdirectory. |
| **Dependencies** | Git submodules: sux (ByteHamster fork), gcem, tlx, ips2ra, and vectorclass (SIMD only). System: Intel TBB, pthread and libatomic. The CUDA toolkit is needed for GPURecSplit. |
| **Minimum toolchain** | C++20 and CMake 3.25+. CI uses GCC 10-13 on Ubuntu 24.04. The paper used GCC 11.2 and CUDA 11, and a Jan 2026 commit fixes a newer nvcc. |
| **Platforms** | SIMDRecSplit: x86-64 only; the target needs SSE4.2, and full speed needs AVX2 or AVX-512 (tuned for AVX-512). GPURecSplit: NVIDIA GPU for construction, CPU for queries. Portable variant: reportedly builds on ARM. CI covers Linux only. |
| **Thread safety** | Not documented. Construction takes num_threads and parallelizes internally. operator() is non-const, but from reading the code, queries only read the built structure, so concurrent lookups on a finished instance look safe. |
| **Drop-in for the baseline** | false: the API is different. It accepts only std::string keys or 128-bit hashes, is configured by (bucket_size, num_threads), and hard-codes SpookyHash V2 with no custom hasher. |

## Gotchas

- Duplicate keys make the constructor loop forever, so deduplicate first. Leaf size is capped at 24, and the code comments say bucket size works with high probability only up to an average of about 2000 (MAX_BUCKET_SIZE=3000).
- The CMake targets set -march=native and -DSIMD as INTERFACE options, so your own target is compiled for the build machine's CPU.
- GPURecSplit calls cudaDeviceReset() at the end of construction and exit() on any CUDA error, which destroys other CUDA state in the process or the process itself.
- The output is not interchangeable. The functions differ from Sux RecSplit, and the portable variant differs from SIMD/GPU (a test checks those two for equivalence). Serialization is a raw native binary stream that checks only the leaf size.

## Caveats and trade-offs

The BBHash numbers were checked by hand against the Table 3 PDF (v2, 5 Jul 2023) and match. Table 3 runs BBHash single-threaded. BBHash is a parallel code, but Figure 6 shows it scales poorly, so this does not flip the result. SIMDRecSplit queries are slower than BBHash (71 vs 51 ns/key at the compared settings). The README's headline table compares only against RecSplit. The SIMD path targets x86 AVX-512/AVX2, and the GPU path needs CUDA.

GPU variant requires CUDA hardware/drivers; SIMD variant needs AVX support (falls back to slower emulated SIMD without it); licensed GPL-3.0 + GCC Runtime Library Exception (same terms as libstdc++), which is more restrictive than BBHash's/PTHash's permissive licenses.

## Maintenance

Active research code from KIT (last commit 2026-01-04 fixes nvcc compatibility; CI on GCC 10-13; 0 open issues, 16 stars), copyable as a git submodule plus add_subdirectory under GPLv3 with the GCC Runtime Library Exception, the same terms as libstdc++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Table 3 of arXiv 2212.09562v2 lists BBHash (gamma=1.0: 3.059 bits/key, 208 ns/key; gamma=5.0: 6.871, 50 ns) next to SIMDRecSplit l=5, b=5 (2.96, 49 ns). Figure 5 also plots CHD (CMPH). The paper states GNU C++ 11.2.0 -O3 -march=native, CUDA 11, i7-11700 and RTX 3090. The Table 3 driver is public: ByteHamster/MPHF-Experiments comparisonQueries.cpp at commit d12faa1dc2 has exactly these BBHash/RecSplit/SIMDRecSplit configurations, single-threaded by default (Contender::numThreads=1).
- **Verifier notes:** All claimed numbers (2.96/49 ns, 3.059/208 ns, 5438x) appear verbatim in the PDF. The '\~4x' ratio is derived and is now marked as such. Keys in the competitor comparison are strings, not 64-bit ints. Metadata checks out: GPL-3.0 (plus the GCC RLE per README), 16 stars, last commit 2026-01-04, active, not a fork.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2212.09562>
  - <https://arxiv.org/pdf/2212.09562>
  - <https://github.com/ByteHamster/GpuRecSplit>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/d12faa1dc2439b7ec93f4f52a498cfbaf1ee9c88/comparisonQueries.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/d12faa1dc2439b7ec93f4f52a498cfbaf1ee9c88/benchmark/BBHashContender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/d12faa1dc2439b7ec93f4f52a498cfbaf1ee9c88/benchmark/Contender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/d12faa1dc2439b7ec93f4f52a498cfbaf1ee9c88/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/ByteHamster/GpuRecSplit>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/README.md>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/.github/workflows/build.yml>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/Dockerfile>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/SIMDRecSplit.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/AbstractParallelRecSplit.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/GPURecSplit.cuh>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/RecSplitRotate.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/RiceBitVector.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/function/DoubleEF.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/util/SimdUtils.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/util/Hash128.h>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/util/Sorter.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/include/support/common.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/src/Sorter.cpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/test/correctness.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/test/correctness.cpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/test/GPUandSIMDequivalence.cu>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/benchmark/benchmark_construction.hpp>
  - <https://github.com/ByteHamster/GpuRecSplit/blob/main/benchmark/benchmark_construction.cpp>
  - <https://github.com/ByteHamster/GpuRecSplit/issues/1>
  - <https://github.com/ByteHamster/GpuRecSplit/issues/2>
  - <https://github.com/ByteHamster/GpuRecSplit/commits/main>
  - <https://arxiv.org/abs/2212.09562>
  - <https://arxiv.org/pdf/2212.09562>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/bytehamster/gpurecsplit`) · [data/wave1-phf/enrich/raw/github_com_bytehamster_gpurecsplit.json](../../../data/wave1-phf/enrich/raw/github_com_bytehamster_gpurecsplit.json) (enrichment confidence 0.85)

</details>
