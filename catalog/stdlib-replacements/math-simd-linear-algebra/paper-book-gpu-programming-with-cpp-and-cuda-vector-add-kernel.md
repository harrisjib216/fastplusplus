# GPU Programming with C++ and CUDA: CUDA vector addition kernel (chapter 4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `MIT` · 🟡 stale

> Textbook one-thread-per-element CUDA float vector add: 44x kernel-only over a scalar CPU loop, 1.02x once copies count.

| | |
|---|---|
| **Beats** | scalar CPU for-loop vector add (C[i] = A[i] + B[i], std::transform-equivalent) |
| **Claimed result** | Book tables (relayed via the seed lead from the book, not shown on any repo page I opened): kernel-only speedup reaches 44.04x at 100M elements; including host-to-device and device-to-host copies it falls to 1.02x (212.297 ms GPU against 218.270 ms CPU). |
| **Workload** | Element-wise addition of two float vectors, 10 thousand up to 100 million elements: CUDA kernel (1024 threads per block) against a single-threaded CPU loop; the repo's vector_add.cu uses N = 100,000,000 and reports kernel-only and with-copy speedups, GPU timed with CUDA events and CPU with std::chrono, one run. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10750H and NVIDIA GeForce RTX 2060, per the book (relayed via lead; no hardware is listed on a repo page) |
| **Compiler and flags** | Not stated for the book run. ch4/2_vector_add/CMakeLists.txt has only project(vector_add CUDA) and add_executable, no flags and no build type. Repo README lists g++ 9.4, CUDA Toolkit 12 and CMake 3.16 as the environment but no flags. |
| **Adoption** | 117 stars; Packt companion repository of the book GPU Programming with C++ and CUDA (2025) |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA) · [benchmark](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch4/2_vector_add/vector_add.cu) |

## Verdict

Per the book (relayed via the seed lead; the repo prints but does not record results, flags or hardware), on an Intel Core i7-10750H with an NVIDIA GeForce RTX 2060 and CUDA 12, adding two 100-million-float vectors ran 44.04x faster as a kernel than a single-threaded CPU loop built with no stated flags, but only 1.02x faster (212.297 ms against 218.270 ms) once the three host-device copies from pageable memory were counted; one run per size, results never checked.

## Use it when

- Vectors that already live in device memory as one step of a longer GPU pipeline, so no host-device copy is paid for this operation.
- Learning the basic CUDA flow (cudaMalloc, cudaMemcpy, launch configuration, CUDA event timing) on an NVIDIA GPU.
- A quick bandwidth sanity check: a minimal coalesced kernel to see what fraction of device memory bandwidth simple element-wise code reaches.

## Skip it when

- Host-resident data processed once: with the two host-to-device copies and the device-to-host copy counted, the book's run is 212.297 ms on the GPU against 218.270 ms on the CPU, 1.02x, which is no real gain.
- As evidence that a GPU beats std::transform: the CPU side is one scalar thread built with no flags, and no vectorised or multithreaded CPU version (std::transform with std::execution::par_unseq, OpenMP, a SIMD library) is measured.
- Element counts above INT_MAX: the kernel, the CPU loop and N all use int indices.
- Production code: there is no CUDA error checking and no result check.
- Machines without an NVIDIA GPU and the CUDA toolkit.

## How it is fast

Plain data parallelism on a memory-bound operation: each thread does two coalesced 4-byte loads and one store, so the kernel runs near device memory bandwidth, about 242 GB/s for the 1.2 GB moved in the book's roughly 4.96 ms kernel (derived from the relayed 218.270 ms CPU time and 44.04x), against about 5.5 GB/s for the single-threaded CPU loop. There is no further technique (no grid-stride loop, no vector loads, no pinned memory or streams). The advantage exists only for data already resident on the GPU: copying 1.2 GB over PCIe from pageable host memory took about 207 ms (derived), roughly what the CPU loop takes for the whole job.

## Compared with alternatives

The catalogued CPU siblings xsimd, Vc and NumKong (SimSIMD) speed up element-wise and reduction loops with SIMD and need no copies, so for host-resident vectors they are the better choice given this entry's 1.02x end-to-end result; pick this CUDA kernel only when the vectors already live on an NVIDIA GPU.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .cu file; a three-line __global__ kernel plus host scaffolding) |
| **Dependencies** | CUDA Toolkit runtime (cuda_runtime.h); no libraries |
| **Minimum toolchain** | nvcc in C++14 mode or later for the 100'000'000 digit separators; README lists CUDA Toolkit 12, g++ 9.4 and CMake 3.16, and the dev container uses Ubuntu 20.04 with CUDA 12.0 and g++ 9; ch4/2_vector_add/CMakeLists.txt sets no flags, architecture or build type |
| **Platforms** | NVIDIA GPUs (no -arch in the CMake file, so nvcc's default target applies, JIT-compiled from PTX on newer GPUs); README lists Ubuntu Linux 20 or later |
| **Thread safety** | not applicable (a kernel; the host program is single-threaded) |
| **Drop-in for the baseline** | no |

## Gotchas

- No result check and no CUDA error checks: the CPU loop writes into the same h_C that just received the GPU result, so the GPU output is never compared, and a failed allocation or launch would go unnoticed while the program still prints a kernel time and a speedup.
- The host buffers come from malloc (pageable), so cudaMemcpy stages every transfer; the about 5.8 GB/s copy rate derived from the book's figures is lower than pinned memory (cudaMallocHost) would give, which makes the end-to-end comparison look worse for the GPU than it needs to.
- The CPU baseline is probably unoptimised: the CMake file passes no -O flag, and NVIDIA-forum reports seen in search results say nvcc applies no host optimisation unless asked (not confirmed in nvcc documentation here); about 5.5 GB/s (derived) is low for a memory-bound loop. Build with -DCMAKE_BUILD_TYPE=Release or -Xcompiler -O3 before comparing.
- One run with no warm-up (the timed kernel is the process's first launch), and only N = 100,000,000 is in the repo; the book's 10-thousand-to-100-million sweep has to be recreated by editing N.

## Known shortcomings

- 44.04x is kernel-only; end to end the GPU is 1.02x. Pageable malloc copies; the CPU loop overwrites h_C so the GPU output is never checked; the readme build sets no flags; no warm-up.
- Enricher: CPU baseline built with no -O flag (unoptimised-baseline risk, D candidate if confirmed); 1.02x end to end; no CUDA error checks; single run, no warm-up.

## Caveats and trade-offs

The headline 44.04x is kernel-only and excludes the two host-to-device copies and the device-to-host copy, which the same program shows cost almost all of the time (end-to-end 1.02x, i.e. no net gain). The host buffers come from malloc (pageable, not pinned), so the copy times are larger than pinned transfers would give. The CPU baseline is one scalar loop on one core, and ch4/2_vector_add/CMakeLists.txt sets no flags and no build type (ch4/readme.md says only 'cmake ..' then 'make'), so it is probably unoptimised; 1.2 GB of traffic in 218.270 ms is about 5.5 GB/s (derived from the relayed book numbers), low for a vectorised memory-bound loop. Not compared with std::transform under a parallel policy or a vectorised loop. No correctness check: vectorAddCpu writes into the same h_C that received the GPU result, so the GPU output is overwritten unchecked. Single run, no warm-up: the timed kernel is the process's first launch. The book's 10-thousand-to-100-million sweep is not in the repo (only N = 100,000,000); numbers, compiler flags and the CPU and GPU models come only from the book. Last commit 2025-12-15 is a README banner change; the last code change is 2025-08-20. Tier C: first-party.

Memory-bandwidth-bound kernel: the end-to-end win disappears once PCIe copies are counted, so it pays only when data stays resident on the device or the work per byte is larger. Needs an NVIDIA GPU and CUDA toolkit.

## Maintenance

MIT-licensed companion code for a 2025 Packt book: ch4 was last updated on 2025-07-20, the last code commit is 2025-08-20 and the 2025-12-15 commit only changed the README banner; a teaching sample to copy, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** ch4/2_vector_add/vector_add.cu (N = 100,000,000, 1024 threads per block) times copies and kernel with CUDA events and the CPU loop with std::chrono, printing kernel-only and total speedups, but no repo page shows results, flags or hardware; the 44.04x and 1.02x figures are the book's own run, so first-party C.
- **Verifier notes:** Code matches the record. Added pageable-memory copies, the missing correctness check (h_C overwritten by the CPU loop) and the readme build without flags. The headline gain is kernel-only; end to end there is no gain.
- **Fields the verifier corrected:** `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-80 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch4/2_vector_add/vector_add.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/2_vector_add/vector_add.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/2_vector_add/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/readme.md>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/2_vector_add/vector_add.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/2_vector_add/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch4/readme.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/.devcontainer/devcontainer.json>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/.devcontainer/DockerfileUbuntu>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/issues>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pulls>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pull/1/files>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-gpu-programming-with-cpp-and-cuda-vector-add-kernel`) · [data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_vector_add_kernel.json](../../../data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_vector_add_kernel.json) (enrichment confidence 0.6)

</details>
