# TurboFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `CUDA/C++` · `Apache-2.0` · 🟡 stale

> Code-generated batched 1D FP32/FP64 GPU FFT kernels with fused ABFT fault tolerance; matches or beats cuFFT, beats VkFFT.

| | |
|---|---|
| **Beats** | NVIDIA cuFFT (also VkFFT) |
| **Claimed result** | Up to 300% faster than cuFFT on certain sizes (especially small problems &lt; 2 MB); 7-15% overhead with online fault tolerance (arXiv abstract/Figure 1) |
| **Workload** | GPU FFTs on NVIDIA A100 and Tesla T4, fault-tolerance on and off |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7713 + NVIDIA A100-40GB; Intel Xeon Silver 4216 + NVIDIA Tesla T4 |
| **Compiler and flags** | GCC &gt;= 11.2.0, CUDA 12.0 (A100) / 11.6 (T4), nvcc -O3 -lineinfo, CMAKE_CUDA_ARCHITECTURES 80 or 75 (TurboFFT/CMakeLists.txt) |
| **Adoption** | 9 stars, 4 forks; PPoPP 2025 paper |
| **Last commit** | 2026-06-24 |
| **Links** | [repository](https://github.com/shixun404/TurboFFT) · [benchmark](https://arxiv.org/html/2412.05824v1) |

## Verdict

The PPoPP 2025 paper (arXiv 2412.05824) reports that TurboFFT without fault tolerance is comparable to, or on certain sizes up to 300% faster than, cuFFT and faster than VkFFT, and that its fault tolerance costs 7-15% even under hundreds of injected errors per minute, for FP32 and FP64 batched 1D C2C FFTs. The artifact README gives the setup: A100-SXM4-40GB with AMD EPYC 7713, GCC 12.3.0, CUDA 12.0; and Tesla T4 with Xeon Silver 4216, GCC 11.2.0, CUDA 11.6; nvcc -O3 -lineinfo with sm_80/sm_75; timings are cudaEvent averages over 10 runs.

## Use it when

- Batched small 1D power-of-two C2C FFTs (the paper's best case is problems under about 2 MB) on an A100 or T4, where cuFFT kernel choice is weak and launch-bound sizes dominate.
- Long-running HPC or ML jobs on GPUs where silent data corruption matters and you want error detection and correction inside the FFT at the 7-15% overhead the paper reports, instead of offline recomputation.
- As a starting point for your own fused FFT kernels (the code generator is about 780 lines of Python and the later commits fuse FFT with GEMM for Fourier neural operators).
- Reproducing or extending the PPoPP 2025 TurboFFT experiments against cuFFT and VkFFT.

## Skip it when

- You need a drop-in cuFFT replacement: there is no plan/exec API, no inverse or real-to-complex transform, no 2D/3D, no strides, and only power-of-two lengths up to 2^25 ('We currently only support radix-2').
- GPUs other than A100 and T4 or architectures other than sm_75/sm_80: CMake rejects any other ARCH_SM value and tuning tables exist only for those two GPUs.
- Large transforms where cuFFT is already bandwidth-bound: the claim is 'comparable to or up to 300% faster', with the big gains limited to certain small sizes.
- Production use without a maintainer: 9 stars, no releases, no issues filed; the last code commit is from February 2025 (TurboFNO work) and the June 2026 commit only added the Apache-2.0 LICENSE.
- Builds without Python: kernels must be generated with Python &gt;= 3.9 and PyTorch before compiling.

## How it is fast

Each size gets its own generated kernel chain (one launch up to 2^12 or 2^13 depending on the tuning table, two for mid sizes, three for 2^23-2^25): every thread runs an 8-, 16- or 32-point radix-2 sub-FFT in registers with twiddles emitted as compile-time constants, threads exchange data through shared memory, and the large sizes split into multiple kernels with table twiddles between passes. The paper calls the design architecture-aware, padding-free and template-based, with tile sizes and batch-per-block chosen per GPU from a CSV. Fault tolerance is fused into the same kernels: DFT-matrix checksums are reduced with warp shuffles (two-side ABFT with location encoding), so detection and correction add no extra pass over memory.

## Compared with alternatives

Pick TurboFFT over VkFFT when you need FP32/FP64 power-of-two batched FFTs on A100/T4 with built-in fault tolerance or the last bit of small-size throughput; pick VkFFT for arbitrary sizes, R2C, inverse, multi-dimensional transforms or non-NVIDIA GPUs, and tcFFT only for FP16 tensor-core work.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (cudart; the driver also links cuFFT and cuBLAS), NVIDIA cuda-samples Common helpers via the CUDA_SAMPLES_COMMON environment variable, Python &gt;= 3.9 with PyTorch &gt;= 2.4 and NumPy for code generation; Matplotlib/Seaborn only for plots |
| **Minimum toolchain** | GCC &gt;= 11.2.0, CMake &gt;= 3.24.3 (README; CMakeLists asks for 3.17), CUDA 12.0 for A100 or 11.6 for T4 |
| **Platforms** | NVIDIA GPUs, sm_80 (A100) or sm_75 (T4) only; Linux shell scripts |
| **Thread safety** | not documented; kernels are stateless launches on the default stream (no stream parameter in the driver) |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark asymmetry: test_turbofft launches the kernel chain once as a warm-up before the timed loop, but test_cufft starts timing on the first cufftExecC2C/Z2Z with no warm-up, and both average over only ntest = 10 runs; any first-call cost lands in cuFFT's number, which matters most for the small sizes where the up-to-300% gains are claimed.
- Both timing loops call cudaDeviceSynchronize after every launch inside the event-timed region, and TurboFFT does so after each of its 1-3 kernels, so per-launch host latency is included in all reported times.
- At HEAD, run_A100.sh has the codegen, build, 24 benchmark runs, VkFFT build and plotting all commented out (only the newer fft_codegen_stride scripts run); reproducing the paper's A100 figures needs the PPoPP artifact archive (Zenodo record 14220293) or manual uncommenting. run_T4.sh is still complete.
- Correctness check in the driver compares against cuFFT with a 1e-4 bound on |diff| / (1 + |ref|), so small-magnitude outputs are effectively checked in absolute rather than relative error.

## Known shortcomings

- 'Up to 300%' only for some small sizes, otherwise on par with cuFFT; 7-15% overhead with fault tolerance; Apache-2.0 license added only in June 2026.
- Benchmark tilt: TurboFFT gets one warm-up launch, cuFFT none, and both average only 10 runs; this favours TurboFFT exactly at the small sizes behind the 'up to 300%' claim.
- At HEAD the A100 script (run_A100.sh) has its build and benchmark steps commented out, so the paper's A100 figures need the Zenodo artifact; run_T4.sh still works.
- Last code commit Feb 2025 (Jun 2026 commit only added the license), so 'active' overstates it; benchmark driver only, no library API; tuned for A100/T4 only.

## Caveats and trade-offs

Peer-reviewed at PPoPP 2025; 'up to 300%' is a best case on certain (small) sizes, otherwise comparable to cuFFT; baseline is cuFFT not FFTW/MKL; 7-15% overhead with online fault tolerance; most bench lines in run_A100.sh are commented out by default. Apache-2.0 LICENSE added only in June 2026. [retier] TurboFFT gets one warm-up launch and cuFFT none, both averaged over 10 runs, which favours TurboFFT at small sizes; run_A100.sh build and benchmark steps are commented out at HEAD; last code commit Feb 2025.

NVIDIA GPU only; adds algorithm-based fault tolerance; research prototype

## Maintenance

Dormant research artifact (last code commit February 2025, Apache-2.0 LICENSE added June 2026); permissively licensed and copyable, but expect to adapt the generator and driver yourself rather than link a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded: PPoPP 2025 paper (arXiv 2412.05824) reports up to 300% faster than cuFFT; the artifact repo has the cuFFT-vs-TurboFFT benchmark (main.cu --if_bench, run_A100.sh/run_T4.sh), GCC &gt;= 11.2 + CUDA 12.0/11.6, CMake flags -O3 -lineinfo sm_80/sm_75, and hardware AMD EPYC 7713 + A100-40GB / Xeon Silver 4216 + T4.
- **Verifier notes:** Record called it an unconfirmed preprint; it is the PPoPP'25 paper. Upgraded B-&gt;A based on artifact repo methodology.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2412.05824v1>
  - <https://github.com/shixun404/TurboFFT>
  - <https://github.com/shixun404/TurboFFT/commits>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/run_A100.sh>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/shixun404/TurboFFT>
  - <https://github.com/shixun404/TurboFFT/commits/main>
  - <https://github.com/shixun404/TurboFFT/issues?q=is%3Aissue>
  - <https://github.com/shixun404/TurboFFT/tree/main/TurboFFT>
  - <https://github.com/shixun404/TurboFFT/tree/main/TurboFFT/include>
  - <https://github.com/shixun404/TurboFFT/tree/main/TurboFFT/include/param>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/readme.md>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/run_A100.sh>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/run_T4.sh>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/readme.md>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/main.cu>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/.gitignore>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/TurboFFT.h>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/TurboFFT_radix_2_template.h>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/cufft/cufft.h>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/code_gen/scripts/fft_codegen.py>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/utils/compareData.h>
  - <https://raw.githubusercontent.com/shixun404/TurboFFT/HEAD/TurboFFT/include/utils/initializeData.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/shixun404/turbofft`) · [data/wave8/enrich/raw/github_com_shixun404_turbofft.json](../../../data/wave8/enrich/raw/github_com_shixun404_turbofft.json) (enrichment confidence 0.75)

</details>
