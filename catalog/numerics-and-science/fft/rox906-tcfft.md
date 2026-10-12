# tcFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA/C++` · `GPL-3.0` · 🔴 abandoned

> Research FP16 FFT kernels that run radix-16 butterflies on NVIDIA tensor cores; beats cuFFT half precision on V100/A100.

| | |
|---|---|
| **Beats** | NVIDIA cuFFT (half precision) |
| **Claimed result** | 1.29x-3.24x faster than cuFFT on V100, 1.10x-3.03x on A100 (arXiv abstract) |
| **Workload** | Batched 1D and 2D half-precision FFTs on NVIDIA tensor cores, V100 and A100 |
| **Metric** | throughput |
| **Hardware** | NVIDIA V100, A100 |
| **Compiler and flags** | nvcc (CUDA &gt;= 11.0), Makefile: -std=c++11 -gencode arch=compute_70,code=sm_70 -gencode arch=compute_80,code=sm_80 -lineinfo -Xcompiler -fopenmp (no explicit -O) |
| **Adoption** | 43 stars, 13 forks; IEEE conference paper (venue per search record, not re-checked) |
| **Last commit** | 2021-05-21 |
| **Links** | [repository](https://github.com/rox906/tcFFT) · [benchmark](https://arxiv.org/abs/2104.11471) |

## Verdict

The tcFFT paper (arXiv 2104.11471, IEEE CLUSTER 2021) reports average speedups of 1.29x-3.24x on V100 and 1.10x-3.03x on A100 over cuFFT 11.0 FP16 for batched 1D and 2D C2C FFTs; the repo's paired speed binaries time repeated in-place forward transforms with gettimeofday for at least 4 s per size, built by nvcc with -std=c++11 for sm_70/sm_80 and no explicit -O flag. The digit-reversal permutation is excluded from the tcFFT timing, and the host CPU and exact CUDA version are not stated in the repo.

## Use it when

- Large batches of forward FP16 complex FFTs whose size is exactly one of the hard-coded lengths (for example 1M batches of 256/512/1024 points) on a V100 or A100.
- Throughput-bound pipelines that already tolerate FP16 error (mixed-precision ML or signal pre-processing) and can produce input in the library's digit-reversed order for free.
- As a reference design if you are writing your own tensor-core FFT kernels; the code is about 2,600 lines of CUDA in two files.
- Reproducing or extending the CLUSTER 2021 tcFFT paper's experiments.

## Skip it when

- Anything needing accuracy: it accumulates in FP16 (half accumulator fragments), and open issue #5 reports a mean relative error of 1.9 for tcFFT versus 0.0185 for cuFFT FP16 on an RTX 3090 with the repo's own accuracy test; issue #2 reports NaN output after tcfftExec.
- Any size not in the switch table, inverse transforms, real-to-complex, 3D, FP32/FP64 or non-power-of-two lengths: none exist (issue #1 asked for sizes beyond 1k; the inverse is requested in #2 and unanswered).
- Production code: four commits in May 2021, no error checking on CUDA calls, no plan destructor (device twiddle buffers leak), five open/closed bug reports with no maintainer replies.
- Closed-source or permissively licensed products: the code is GPL-3.0.
- Non-NVIDIA GPUs or GPUs older than Volta: the Makefile builds sm_70 and sm_80 only and the kernels use nvcuda::wmma.

## How it is fast

Cooley-Tukey with radix 16: each radix-16 DFT stage is written as a 16x16 complex matrix product against the DFT matrix, split into four real FP16 WMMA mma_sync calls (real/imag parts) on tensor cores. Several radix-16 stages plus a final radix-2 or radix-4 step are fused into one kernel (256-, 512- or 1024-point 'mergings') that keeps data in shared memory, so a 2^27-point transform needs only three global-memory passes. Twiddle multiplication and the small radix-2/4 tails run as ordinary half2 CUDA-core arithmetic.

## Compared with alternatives

Pick tcFFT over VkFFT or TurboFFT only for batched forward FP16 transforms at its exact sizes where tensor-core throughput matters more than accuracy; VkFFT (FP16/32/64, any size, inverse, Vulkan/CUDA/HIP/OpenCL, MIT) and TurboFFT (FP32/FP64, fault tolerance) are maintained, general libraries and the safer choice otherwise.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA &gt;= 11.0 runtime (cuda_fp16/mma.h); the header also includes cublas_v2.h; FFTW &gt;= 3.3.8, cuFFT and OpenMP only for the test/benchmark binaries |
| **Minimum toolchain** | nvcc from CUDA 11.0+, -std=c++11; host compiler with OpenMP for the harness |
| **Platforms** | NVIDIA tensor-core GPUs, Makefile targets sm_70 (V100) and sm_80 (A100); Linux Makefile only |
| **Thread safety** | not documented; the plan is a plain struct passed by value and tcfftExec launches on the default stream with no stream parameter |
| **Drop-in for the baseline** | partial — same job as cufftXtExec with CUDA_C_16F forward C2C, but a different API, fixed size table, and the input must be pre-permuted into digit-reversed order |

## Gotchas

- Unsupported sizes fall through 'default: break' in tcfftCreate, leaving n_radices/n_mergings uninitialized; tcfftExec then launches with garbage values. In 2D, Nx = 1024 selects plan.layer_1[2], a function pointer that tcfftCreate never sets.
- The repo benchmark permutes the input into digit-reversed order on the host inside setup(), outside the timed loop, while cuFFT is timed on natural-order input; a real user has to pay for that permutation (an extra full read and write of the array) somewhere, so the published speedups are an upper bound.
- The \*_A100 kernel variants in tcfft_half.cu and tcfft_half_2d.cu are never bound by tcfftCreate (tcfftExec is commented '// V100'); how the paper's A100 runs selected them is not documented.
- Small sizes launch N\*batch/(n_cont\*RADIX) blocks (n_cont = 32, 16, 8 for 256, 512, 1024), so batch counts that are not a multiple of 32/16/8 leave trailing transforms unprocessed; test.sh only says the batch 'should bigger than 32 for short sizes'.

## Known shortcomings

- Half precision only; CUDA version only '11.0 or higher', CPU unnamed; Makefile sets no explicit -O flag; 4 commits, abandoned (2021-05-21).
- Unequal benchmark: tcFFT's input is put into digit-reversed order on the host outside the timed loop while cuFFT is timed on natural-order input, so the 1.29x-3.24x speedups are an upper bound.
- Accuracy: sums in FP16; open issue #5 reports error 1.9 for tcFFT vs 0.0185 for cuFFT FP16 on an RTX 3090 with the repo's own test; issue #2 reports NaN output.
- Crashes: sizes outside its fixed table run with uninitialized plan fields; 2D with Nx=1024 calls a never-set function pointer. The code never selects its A100 kernels, so how the paper's A100 runs were made is undocumented. GPL-3.0, no inverse transform, abandoned since May 2021.

## Caveats and trade-offs

Half precision accuracy tradeoff versus cuFFT; baseline is cuFFT not FFTW/MKL; the repo link was found via search results, and the paper abstract page does not state code link. [retier] Digit-reversal done on the host outside the timed loop (cuFFT timed on natural-order input); FP16 accumulation error (#5) and NaN output (#2) open; A100 kernels never selected by the code; abandoned since May 2021.

FP16 only, tensor-core GPUs only, 1D/2D only; GPL-3.0

## Maintenance

Abandoned research code (four commits, May 2021, no maintainer replies to issues); GPL-3.0 and small enough to vendor, but treat it as a reference implementation rather than a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** arXiv 2104.11471 abstract states tcFFT outperforms cuFFT 1.29x-3.24x (V100) and 1.10x-3.03x (A100); repo has public speed.cpp/cufft_doit_half.cpp benchmarks and nvcc flags in Makefile, but compiler version is only 'CUDA v11.0 or higher' and host CPU is not stated, so not A.
- **Retiered** B to C: Enrichment read the benchmark code: tcFFT's digit-reversal reordering runs on the host outside the timed loop while cuFFT is timed on natural-order input, so the peer-reviewed CLUSTER 2021 speedups (1.29x-3.24x) compare unequal work; the code never selects its A100 kernels, so the paper's A100 runs cannot be reproduced from public code; open issue #5 reports FP16 error 1.9 vs cuFFT FP16 0.0185 on RTX 3090. Measurement is not like-for-like, so C.
- **Verifier notes:** Repo has only 4 commits (May 2021), GPL-3.0 confirmed. Half-precision only; baseline is cuFFT half precision, compared via repo's paired tcfft/cufft speed binaries.
- **Fields the verifier corrected:** `compiler_and_flags`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2104.11471>
  - <https://github.com/rox906/tcFFT>
  - <https://github.com/rox906/tcFFT/commits>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/rox906/tcFFT>
  - <https://github.com/rox906/tcFFT/commits>
  - <https://github.com/rox906/tcFFT/issues?q=is%3Aissue>
  - <https://github.com/rox906/tcFFT/issues/1>
  - <https://github.com/rox906/tcFFT/issues/2>
  - <https://github.com/rox906/tcFFT/issues/3>
  - <https://github.com/rox906/tcFFT/issues/4>
  - <https://github.com/rox906/tcFFT/issues/5>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/Makefile>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_half.h>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_half.cu>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_half_2d.h>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_half_2d.cu>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/test.sh>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/speed.cpp>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/speed_2d.cpp>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/accuracy.cpp>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_doit_half.cpp>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/tcfft_doit_half_2d.cpp>
  - <https://raw.githubusercontent.com/rox906/tcFFT/HEAD/cufft_doit_half.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rox906/tcfft`) · [data/wave8/enrich/raw/github_com_rox906_tcfft.json](../../../data/wave8/enrich/raw/github_com_rox906_tcfft.json) (enrichment confidence 0.75)

</details>
