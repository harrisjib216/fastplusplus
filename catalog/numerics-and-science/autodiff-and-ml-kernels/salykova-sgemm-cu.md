# sgemm.cu (hand-tuned FP32 GEMM for NVIDIA GA102/Ampere GPUs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `CUDA C++` · `MIT` · 🟡 stale

> Hand-tuned row-major FP32 SGEMM kernels for Ampere; about 4-7% above cuBLAS SGEMM at large square sizes on an RTX 3090.

| | |
|---|---|
| **Beats** | cuBLAS SGEMM (CUDA 12.6) |
| **Claimed result** | The README gives no text numbers, only two plots (assets/perf.png, perf_locked.png). Reading them by eye at m=n=k near 12800: about 25,300-25,500 GFLOP/s vs cuBLAS about 24,300 with unlocked clocks (about 4-5% faster), and about 23,000-23,500 vs about 21,800 with locked 1395 MHz clocks (about 6-7% faster); approximate, derived from page data. The HN title claims 'up to 24% faster than cuBLAS on a 4090' (snippet only, not on the repo page). |
| **Workload** | FP32 SGEMM, NN layout, square m=n=k from 1024 to about 12800 in steps of 128, RTX 3090, with clocks unlocked and with clocks locked at 1395 MHz, both at 350 W. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 (driver 550.120), Ubuntu 24.04.1 LTS; host CPU model not stated. |
| **Compiler and flags** | nvcc V12.6.85 (CUDA Runtime 12.6, CUDA Driver 12.4), g++ 13.3, CMake 3.28.3; the build is fixed by CMakeLists.txt: CUDA_ARCHITECTURES=86, CUDA_SEPARABLE_COMPILATION ON, -DGPUCC=86 -DCUBLAS=0/1, no CMAKE_BUILD_TYPE and no explicit -O flags (the -O3 lines are commented out). |
| **Adoption** | 130 stars |
| **Last commit** | 2025-01-21 |
| **Links** | [repository](https://github.com/salykova/sgemm.cu) · [benchmark](https://github.com/salykova/sgemm.cu) |

## Verdict

Two README plots, with no numbers in text: RTX 3090 at 350 W, CUDA 12.6 (driver 550.120), square row-major NN SGEMM at m=n=k 1024 to 12800 in steps of 128, sgemm.cu vs cublasSgemm in the same harness. By eye, sgemm.cu sits at about 25,000-25,500 GFLOP/s against cuBLAS at about 24,000-24,500 at large sizes (about 4-5%), and at about 23,000-23,500 vs 21,600-22,000 with clocks locked at 1395 MHz (about 6-7%). Each point is the mean of the second half of the timed calls (CUDA events, L2 flushed between calls) after 500 warm-up runs at 4096.

## Use it when

- Large FP32 GEMMs (m or n above about 4,000) on GA102-class Ampere (RTX 3080/3090, A10, A40, A6000) where results must stay strict FP32 rather than TF32.
- Power-limited or clock-locked GPUs: the margin over cuBLAS grew from about 4-5% to about 6-7% with clocks locked at 1395 MHz.
- When you want a small, readable, MIT-licensed SGEMM to vendor or study instead of linking cuBLAS, with row-major operands and ldc == n.
- As a starting point for tuning SGEMM on Ada or Turing, which the README expects to perform well but which are untested.

## Skip it when

- Small and mid-size GEMMs (below about 2,500): the curves cross, and cuBLAS wins at several sizes (near m=n=k=1280, about 17,000 vs 19,300 GFLOP/s).
- Calls that need transposes, batched or strided-batched GEMM, a non-default stream, error reporting, or a C stride different from n.
- When TF32, FP16 or BF16 tensor cores are acceptable: this is an FFMA kernel with single-digit gains, and tensor-core GEMMs are a different performance class.
- Hopper, Blackwell or non-NVIDIA hardware: the only published results are from one RTX 3090, and the tile choice is tuned for GA102.
- Long-lived production use: 10 commits, last on 2025-01-21, and an issue about the benchmark methodology left unanswered.

## How it is fast

Register-blocked SGEMM. On sm_80+, m or n above 2500 selects a 128x256x8 CTA tile with 256 threads, 64x64 warp tiles and a 16x8 accumulator per thread. Global-to-shared copies use cp.async into double-buffered shared memory, A is stored transposed with padding (ld 132), fragments are double-buffered in registers and read with 128-bit shared loads, and the hot paths are inline PTX. Smaller sizes use a 128x128x8 kernel (2 blocks per SM) with predicated LDG staging; pre-Ampere GPUs use a texture-fetch variant when operands are 16-byte aligned. The epilogue goes through shared memory and edges are handled with predicated loads and stores.

## Compared with alternatives

Pick it over fast.cu (BF16 tensor-core matmul for H100) and bare-metal (FP16 HGEMM tuned for an RTX 3070 Ti Laptop) when the GEMM must stay in FP32 on an Ampere or Ada consumer or workstation card. For int8 use nanoinfer; for CPUs, the AVX-512 DGEMM tutorial.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA runtime only for the kernels (src/sgemm.cuh, src/kernels/\*.cuh, common/'helper_cuda ptx.h'); cuBLAS and CMake 3.18+ only for the bundled benchmark and test |
| **Minimum toolchain** | C++17; CUDA 11.5+ for sm_80+ (static_assert in sgemm.cuh); published results used nvcc V12.6.85, g++ 13.3 and CMake 3.28.3 |
| **Platforms** | NVIDIA GPUs; the arch is a build-time macro (GPUCC, CUDA_ARCHITECTURES). sm_80+ uses the cp.async kernels and sm_7x uses the texture-load kernel; only the RTX 3090 (sm_86) is benchmarked; the README advises native Linux rather than WSL for measurements |
| **Thread safety** | not documented; sgemm() launches on the default stream, and on sm&lt;80 it builds texture objects in namespace-scope globals on every call, so concurrent host calls are unsafe there |
| **Drop-in for the baseline** | false - row-major sgemm() with host alpha/beta pointers and no handle, transpose, stream or status return; ldc is honored only for the first row of each tile (see gotchas) |

## Gotchas

- C-stride bug: all three kernels set the C pointer with m_idx \* ldc but step between rows with n (stg_c_ptr + (i\*16+p)\*n), so any ldc != n writes to the wrong addresses. test.cu and benchmark.cu always pass ldc = n, so the tests never catch it.
- sgemm.cuh defines non-inline functions (and, for sm&lt;80, global cudaResourceDesc/texture handles) in a header. Include it from only one translation unit or you get duplicate-symbol link errors.
- Reproducing the plots takes edits: benchmark.sh defaults to CUBLAS=0 and lock_clocks=0, and cuBLAS is a separate -DCUBLAS=1 build of benchmark.cu (default handle, no cublasSetMathMode call). benchmark.sh and test.sh also run sudo (rm -rf build).
- Correctness coverage is narrow: test.sh checks square sizes 2-3072 against a naive 16x16 kernel at 1e-4 tolerance, with no non-square shapes, strides or nonzero-offset submatrices.

## Known shortcomings

- Gain over cuBLAS is about 4-7% at large sizes and it is slower at some small sizes; the HN title's '24% on 4090' is not in the repo.
- All three kernels step C rows by n rather than ldc, so any ldc != n gives wrong output (tests always use ldc = n). sgemm.cuh puts non-inline functions in a header (single translation unit only). benchmark.sh defaults to CUBLAS=0: cuBLAS is a separate -DCUBLAS=1 build, not the same binary. Plot readings confirmed at about 4-5% over cuBLAS unlocked and 6-7% locked at large sizes.

## Caveats and trade-offs

Numbers exist only as two plot images (assets/perf.png unlocked clocks, assets/perf_locked.png at 1395 MHz, both 350 W); values are read by eye. Margins are single-digit percent at large sizes (about 4-5% unlocked, about 6-7% locked near m=n=k=12800), and sgemm.cu is slower than cuBLAS at several small sizes (near m=n=k=1280 about 17,000 vs about 19,300 GFLOP/s unlocked). Square FP32 NN only, tuned for the RTX 3090 (GA102); other GPUs untested in the repo. The host CPU is not stated (immaterial for a device-bound GEMM; A rests on the GPU-kernel precedent). The last commit (2025-01-21) swapped m and n in the cublasSgemm calls; for the square sizes plotted this does not change the cuBLAS work. The 'up to 24% faster than cuBLAS on a 4090' figure from the HN title is not on the repo page (snippet only); the project page salykova.github.io/sgemm-gpu was not opened (blocked). The plots also show a 'Simon Boehm | tinyBLAS' kernel well below cuBLAS. Repo identity inferred from the HN title and README (HN thread not opened).

FP32 SGEMM only, and the README documents only the NN case; tuned and tested for RTX 3090 (GA102), expected to be fast on Ada/Ampere/Volta/Turing; it is a benchmark and test harness rather than a packaged library.

## Maintenance

Stale since 2025-01-21 (10 commits, one unanswered issue, one unmerged Docker PR), but MIT-licensed and small enough (three kernel headers plus a PTX helper) to vendor. Fix or avoid the ldc != n bug first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C under the wave's GPU-kernel precedent (GPU named in place of a host CPU; flags fixed by a public CMakeLists.txt, as for blackwell-tensorcore-kernels and cuspfft): the public harness benchmark.cu, driven by benchmark.sh, times sgemm.cu and cublasSgemm in the same binary (-DCUBLAS=1) with 500 warm-up iterations, CUDA events and an L2 flush; the README states nvcc V12.6.85, g++ 13.3, CMake 3.28.3, driver 550.120 and the RTX 3090, and CMakeLists.txt fixes the build (CUDA_ARCHITECTURES 86, separable compilation, no extra -O flags). The README plots show sgemm.cu above cuBLAS at large sizes.
- **Verifier notes:** Plot readings in claimed_speedup checked against assets/perf.png and perf_locked.png and match. Harness is sound (warm-up, CUDA events, L2 flush, mean of the second half of iterations, same binary for cuBLAS). Metadata on github.com: MIT (LICENSE: Copyright (c) 2024 Aman Salykov), 130 stars, 8 forks, not a fork or archived, 10 commits, last commit 2025-01-21 (stale is right).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/salykova/sgemm.cu>
  - <https://github.com/salykova/sgemm.cu/commits>
  - <https://github.com/salykova/sgemm.cu/commit/a94d769bf5a020547271bd86e5643cc3cfc19430>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/README.md>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/benchmark.cu>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/assets/perf.png>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/assets/perf_locked.png>
- **Sources the enricher read:**
  - <https://github.com/salykova/sgemm.cu>
  - <https://github.com/salykova/sgemm.cu/tree/main/src>
  - <https://github.com/salykova/sgemm.cu/issues?q=is%3Aissue>
  - <https://github.com/salykova/sgemm.cu/issues/2>
  - <https://github.com/salykova/sgemm.cu/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/README.md>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/benchmark.cu>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/test.cu>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/test.sh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/src/sgemm.cuh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/src/kernels/128x256x8.cuh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/src/kernels/128x128x8.cuh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/src/kernels/128x128x8_texld.cuh>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/common/helper_cuda%20ptx.h>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/assets/perf.png>
  - <https://raw.githubusercontent.com/salykova/sgemm.cu/HEAD/assets/perf_locked.png>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/salykova/sgemm.cu`) · [data/wave8/enrich/raw/github_com_salykova_sgemm_cu.json](../../../data/wave8/enrich/raw/github_com_salykova_sgemm_cu.json) (enrichment confidence 0.8)

</details>
