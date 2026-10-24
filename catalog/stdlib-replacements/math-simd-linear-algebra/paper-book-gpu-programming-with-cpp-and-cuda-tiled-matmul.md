# GPU Programming with C++ and CUDA: shared-memory tiled matrix multiply with unroll and fmaf (chapter 7)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `MIT` · 🟡 stale

> Textbook CUDA FP32 matrix multiply with 16x16 shared-memory tiles; about 1.42x faster than the book's own naive kernel.

| | |
|---|---|
| **Beats** | naive one-thread-per-element CUDA matrix multiply kernel (no cuBLAS comparison) |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): Release kernel time fell from 47.33 ms (naive) to 33.37 ms (all optimisations), which the book calls about a 42% improvement; about 1.42x (derived from the relayed numbers). |
| **Workload** | Single-precision 2000 x 2000 matrix multiply (N = 2000, 16 x 16 tiles) on the GPU: matrixMulKernel (shared-memory tiles, #pragma unroll, fmaf) against matrixMulKernel_naive, with the plain tiled matrixMulKernel_shared also in the file; kernel time from Nsight Compute in the book's Release build. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10750H and NVIDIA GeForce RTX 2060, per the book (relayed via lead; no hardware is listed on a repo page), profiled with Nsight Compute 2023.3 (per the repo README requirements) |
| **Compiler and flags** | ch7/CMakeLists.txt declares only the CUDA language; Release sets CMAKE_CUDA_FLAGS_RELEASE '-O3 -arch=sm_75 -rdc=false' (and CMAKE_CXX_FLAGS_RELEASE -O3, which does not apply to the .cu file), Debug sets CUDA '-G -g -O0'. No build type is set in the file and ch7/readme.md says only 'cmake ..' then 'make', so the book's Release figures need -DCMAKE_BUILD_TYPE=Release. sm_75 matches the RTX 2060 (Turing). Repo README lists g++ 9.4, CUDA Toolkit 12, CMake 3.16 and Nsight Compute 2023.3 as the environment. |
| **Adoption** | 117 stars; Packt companion repository of the book GPU Programming with C++ and CUDA (2025) |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA) · [benchmark](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch7/matrix_multiply_float.cu) |

## Verdict

Per the book (relayed via the seed lead; the repo has no results, hardware or profiler output), Nsight Compute kernel time for a 2000 x 2000 FP32 multiply on an NVIDIA GeForce RTX 2060 (Intel Core i7-10750H host, CUDA 12, Release flags -O3 -arch=sm_75) fell from 47.33 ms for the naive kernel to 33.37 ms for the tiled + unroll + fmaf kernel: 1.42x faster or 29% less time (derived), one profiler run per version. The baseline is the book's own naive kernel, not cuBLAS.

## Use it when

- Learning or teaching the first step of CUDA GEMM optimisation (naive kernel, then shared-memory tiles) on an NVIDIA GPU, with all variants side by side in one file.
- A dependency-free, MIT-licensed FP32 kernel for square row-major matrices of any size (edge tiles are zero-padded) in a small project that cannot link a vendor BLAS.
- A starting point to extend with register blocking, vector loads or a fused epilogue, measured against the naive kernel already in the file.
- Medium matrices (the sample uses N = 2000) that already live in device memory, so the 16 MB-per-matrix copies are not repeated per multiply.

## Skip it when

- Production GEMM: about 0.48 TFLOP/s (derived) is far below what a tuned library reaches; the repo never compares against cuBLAS or CUTLASS, so use a vendor library for real work.
- Non-square, column-major, transposed, batched, FP16/BF16/TF32 or Tensor Core multiplies: none are supported.
- Any launch shape other than 16 x 16 blocks: the shared tiles are fixed at TILE = 16 while the loops use blockDim, so other block sizes overflow or mis-index shared memory.
- GPUs older than compute capability 7.5: the Release flags build only for sm_75 (plus PTX for newer GPUs); there is no CPU fallback.
- Small matrices where host-device copies and launch overhead dominate the multiply.

## How it is fast

Shared-memory tiling (blocked GEMM): each 16 x 16 thread block loads one 16 x 16 tile of A and of B into __shared__ arrays, synchronises, and every thread accumulates 16 products from shared memory before the next tile, so each global element is read once per tile instead of once per output. Each thread still computes a single output and reads both operands from shared memory for every multiply-add; register blocking (several outputs per thread), vectorised loads and double-buffered tiles, which tuned GEMMs use, are absent, which is why the gain over the naive kernel is modest (about 0.48 TFLOP/s for the tiled kernel against 0.34 TFLOP/s naive, derived from the relayed book times). The explicit fmaf and the unroll pragma add little: nvcc already contracts 'sum += a \* b' to FMA by default, and the unrolled loop is bounded by the runtime blockDim.x.

## Compared with alternatives

The closest catalogued sibling, the cache-blocked dgemm from The C++ Programmer's Mindset, shows the same blocking idea on the CPU and, unlike this repo, measures OpenBLAS alongside (about 12x faster than its blocked code); pick this entry only to learn the CUDA shared-memory version on an NVIDIA GPU. Neither replaces a vendor BLAS; for small fixed-size matrices GLM is the catalogued choice.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .cu file; copy the __global__ kernel and its 16 x 16 launch configuration) |
| **Dependencies** | CUDA Toolkit runtime (cuda_runtime.h); no libraries |
| **Minimum toolchain** | CUDA Toolkit 12 per README; the repo's dev container uses Ubuntu 20.04, CUDA 12.0, g++ 9, CMake 3.16 and Nsight Compute 2023.3; ch7/CMakeLists.txt requires CMake 3.10 and sets Release CUDA flags '-O3 -arch=sm_75 -rdc=false' |
| **Platforms** | NVIDIA GPUs; Release build targets sm_75 (Turing, e.g. RTX 2060) with PTX for newer GPUs; README lists Ubuntu Linux 20 or later |
| **Thread safety** | not applicable (a kernel; the host program is single-threaded and does no CUDA error checking) |
| **Drop-in for the baseline** | partial — same signature (A, B, C, width) as matrixMulKernel_naive and the same 16 x 16 launch, so swapping the launch line is enough; it is not a drop-in for cuBLAS (different API, no transposes, no alpha/beta) |

## Gotchas

- The fmaf and '#pragma unroll' labels are mostly nominal: matrixMulKernel and matrixMulKernel_shared differ only by fmaf versus 'sum += a \* b', which nvcc contracts to FMA by default, and the unroll pragma sits on a loop bounded by the runtime blockDim.x rather than the TILE constant; expect the two to perform about the same in Release, with the whole gain coming from tiling.
- checkResults compares GPU and CPU outputs with an absolute 1e-4 tolerance, but each output is about 500 (2000 products of values in [0, 1]), where 1e-4 is about 3 float ulp. A float32 simulation run for this entry (sequential non-FMA host accumulation, as g++ emits for x86-64 without -march, against the GPU's sequential FMA in the same order) gave a 1.22e-4 (4 ulp) difference in about 0.04% of outputs, roughly 1,600 of the 4,000,000, so the program will probably print 'Results do not match!' for every GPU variant; use a relative tolerance.
- ch7/readme.md says only 'cmake ..' then 'make', which sets no build type, so neither the -O3 host flag nor -arch=sm_75 applies; the CMake 3.16 in the dev container has no CMAKE_CUDA_ARCHITECTURES, so nvcc's default target is used. Pass -DCMAKE_BUILD_TYPE=Release to match the book's setup.
- matrixMulKernel_row and matrixMulKernel_col index B with the macro N instead of their width argument, so they are only correct when width == N; they also need the commented-out 1-D launch configuration.

## Known shortcomings

- Book numbers only. The CXX Release flags do not apply to .cu files and the readme's 'cmake ..' sets no build type; the baseline is a naive kernel, not cuBLAS. The unroll bound is the runtime blockDim.x and nvcc contracts to FMA by default, so the fmaf variant is mostly nominal.
- Enricher: the gain is all tiling (the fmaf difference is fused by default anyway); checkResults' 1e-4 absolute tolerance probably reports a mismatch for every GPU variant; only a 16x16 launch is safe.

## Caveats and trade-offs

The baseline is the book's own naive kernel, not cuBLAS or any library: 2000^3 x 2 FLOP in 33.37 ms is about 0.48 TFLOP/s (derived from the relayed numbers), far from what a tuned library reaches on the same card. The repo's main() launches only matrixMulKernel; the naive and plain shared kernels are swapped in by editing the file, and the 47.33 ms and 33.37 ms figures come from the book's profiler runs (one run per version), not from any repo file. Two of the named optimisations probably add little: '#pragma unroll' sits on a loop bounded by the runtime blockDim.x, so it cannot be fully unrolled (the TILE constant would allow it), and nvcc already contracts 'sum += a \* b' into FMA by default (--fmad=true), so the explicit fmaf likely matches matrixMulKernel_shared in Release; the gain over naive comes from shared-memory tiling. The book's 42% compares times as 47.33/33.37 (speed gain), not as a reduction in time (about 29%). Following the readme ('cmake ..', no build type) builds without the Release flags. A checkResults pass compares the GPU result with a CPU triple loop at an absolute 1e-4 tolerance. Last commit 2025-12-15 is a README banner change; the last code change is 2025-08-20. Tier C: first-party, hardware named only in the book.

Standard CUDA optimisation ladder (shared-memory tiling, loop unroll, fused multiply-add); fmaf changes rounding slightly so results are checked against the CPU with a 1e-4 tolerance. Needs an NVIDIA GPU, sm_75 target in the CMake file.

## Maintenance

MIT-licensed companion code for a 2025 Packt book: ch7 was added on 2025-05-16, the last code commit is 2025-08-20 and the 2025-12-15 commit only changed the README banner; the one open issue (ch6) and one open pull request (a cosmetic initializer change in ch4, ch6 and ch8) do not touch ch7, so treat it as a small teaching sample to copy, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** ch7/matrix_multiply_float.cu holds the naive, shared-memory and shared+unroll+fmaf kernels (main() launches only matrixMulKernel) and ch7/CMakeLists.txt states Release flags, but the 47.33 ms and 33.37 ms kernel times and the hardware come only from the book's Nsight Compute runs, so first-party C.
- **Verifier notes:** Code and flags match the record; added the readme build without a build type, the runtime-bounded unroll and nvcc's default FMA contraction, which make the 'unroll + fmaf' label mostly nominal. A small textbook gain over a naive kernel; no library baseline.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-80 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch7/matrix_multiply_float.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/matrix_multiply_float.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/readme.md>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/matrix_multiply_float.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/ch7/readme.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/.devcontainer/devcontainer.json>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/main/.devcontainer/DockerfileUbuntu>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/tree/main/ch7>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/issues>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pulls>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pull/1/files>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-gpu-programming-with-cpp-and-cuda-tiled-matmul`) · [data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_tiled_matmul.json](../../../data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_tiled_matmul.json) (enrichment confidence 0.6)

</details>
