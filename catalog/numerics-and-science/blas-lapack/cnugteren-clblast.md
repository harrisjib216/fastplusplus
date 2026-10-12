# CLBlast

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Auto-tuned OpenCL BLAS (levels 1-3, FP16, batched) for GPUs and accelerators; beats clBLAS GEMM, trails cuBLAS on NVIDIA.

| | |
|---|---|
| **Beats** | clBLAS 2.12 (cuBLAS also tested; it is faster) |
| **Claimed result** | Significantly better overall GEMM performance than clBLAS 2.12, especially for irregular sizes (multiples of 129) and on Skylake/NVIDIA (graphs only, no numeric ratio in text); cuBLAS remains faster than CLBlast |
| **Workload** | OpenCL GEMM and batched BLAS on GPUs, incl. FP16 and small batched matrices |
| **Metric** | throughput |
| **Hardware** | GTX 750Ti, Titan X, Radeon HD7970, M370X, Skylake GT2, Core i5-6200U, Mali T628 |
| **Compiler and flags** | C++11 host, OpenCL C kernels |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/CNugteren/CLBlast) · [benchmark](https://arxiv.org/pdf/1705.05249) |

## Verdict

The peer-reviewed IWOCL '18 paper benchmarks CLBlast 1.3.0 GEMM against clBLAS 2.12 (and cuBLAS on NVIDIA) on seven devices (GTX 750 Ti, Titan X, Radeon HD 7970, Radeon M370X, Intel Skylake GT2, Core i5-6200U CPU, Mali T628) and reports better overall GEMM throughput than clBLAS, most visibly at irregular sizes (multiples of 129) and on Skylake and NVIDIA, shown in graphs without a numeric ratio; cuBLAS remained faster. The \~2x FP16 and up-to-10x batched figures compare CLBlast with its own FP32 and non-batched calls, not with another library.

## Use it when

- You need GEMM or other BLAS on non-NVIDIA GPUs (AMD, Intel integrated or Arc, Arm Mali, Qualcomm Adreno, Apple M-series) through OpenCL, and clBLAS is the alternative.
- Irregular or rectangular matrix sizes where clBLAS loses badly; you can tune for your exact shapes with the tuners or the tuning API and OverrideParameters.
- Mobile and embedded GPUs where half precision (cl_khr_fp16) is accelerated, e.g. deep-learning inference on Mali or Intel GPUs.
- Many small matrices at once: GEMMBATCHED or the faster GEMMSTRIDEDBATCHED instead of a loop of single GEMM calls.
- Portable code that must run across vendors, or OpenCL 1.1-era hardware.

## Skip it when

- NVIDIA-only deployments: the README itself says to use cuBLAS there, and the IWOCL '18 paper shows cuBLAS still faster.
- CPU BLAS work (it is not a replacement for OpenBLAS, MKL, BLIS or Eigen); Intel CPUs are only reachable through an OpenCL CPU runtime.
- You need LAPACK (factorisations, solvers, eigenvalues): only BLAS is implemented, and xROTG, xROTMG, xROT, xROTM, xTBSV and xTPSV are missing.
- Untuned devices where you cannot run the tuners: the README warns out-of-the-box performance can be poor and falls back to family defaults.
- Correctness-critical work on devices with open accuracy reports (e.g. CGEMM errors on AMD RX 5700 in issue #669, SSYRK/SSYR2K error on Apple M1 in #668, FP16 GEMV in #561) unless you run the bundled correctness tests on your device first.

## How it is fast

Every kernel is parameterised (the GEMM kernel has 14 parameters: work-group tile sizes MWG/NWG, 2D register tiling MWI/NWI, vector widths VWM/VWN, unroll factor KWI, local-memory use) and auto-tuned per device in the style of CLTune, with a shipped database of best values for many NVIDIA, AMD, Intel, Arm Mali, Qualcomm Adreno and Apple GPUs. GEMM has two paths: an indirect path that pads/transposes inputs with pre- and post-processing kernels so a fast main kernel can assume tile-multiple sizes, and a single 'direct' kernel for small matrices; a routine-level tuner picks the size at which to switch. FP16 routines and batched GEMM give further gains on hardware with fast half precision or many small problems.

## Compared with alternatives

It is the only GPU/OpenCL library among the catalogued blas-lapack siblings: pick it when the matrices live on a GPU or mobile accelerator; pick BLASFEO, LibShalom or Eigen for small or medium matrices on CPUs, and FT-BLAS or GEMMFIP when you need a CPU BLAS replacement for OpenBLAS/MKL.

## Integration

| | |
|---|---|
| **Form** | shared lib (static via -DBUILD_SHARED_LIBS=OFF); packages in Debian/Ubuntu (libclblast-dev), Homebrew, Windows release zips; Python binding pyclblast |
| **Dependencies** | OpenCL 1.1+ runtime and headers (or CUDA 7.5+ with NVRTC for the CUDA build); nothing else |
| **Minimum toolchain** | C++11 (GCC 4.7+, Clang 3.3+, MSVC 2013+ per docs); CMakeLists now requires CMake 3.14 although installation.md still says 2.8.10 |
| **Platforms** | Any OpenCL 1.1+ device: NVIDIA, AMD, Intel GPUs and CPUs, Arm Mali, Qualcomm Adreno, Apple M1/M2, Intel MIC; Linux, macOS, Windows, Android (cross-compile) |
| **Thread safety** | Library made thread-safe in 0.7.0; a multithreading bug in the compiled-kernel cache was fixed in 1.6.1, so use 1.6.1 or newer for multithreaded callers |
| **Drop-in for the baseline** | partial — the main API mirrors clBLAS argument order (cl_mem buffers, offsets, queue, event) so porting from clBLAS is mostly renaming; not link-compatible with clBLAS, and the CBLAS-named Netlib layer works but copies host data each call and is documented as not for full performance control |

## Gotchas

- First call of each routine compiles its OpenCL kernel at run time, so first-call latency is high; use FillCache(device) to precompile, and ClearCache to free the binaries.
- Indirect GEMM may allocate a temporary device buffer (error -4 on memory-tight devices); query GemmTempBufferSize and pass your own buffer, or raise the direct/indirect switch point with OverrideParameters.
- Versions 1.6.2 and older give wrong results on Intel Arc A770 and some other devices (GEMMK=1 kernel bug when MWG!=NWG, fixed in 1.6.3); distro packages may ship an older version.
- GemmStridedBatched with a C stride of 0 does not accumulate into one matrix (open issue #578); FP16 tests can fail on operation order, and integer-returning half routines (IHAMAX etc.) are not properly tested.

## Known shortcomings

- Paper says cuBLAS is still faster; \~2x FP16 figure is vs CLBlast's own FP32; 10x batched figure is vs non-batched calls; win over clBLAS 2.12 only in graphs.
- Open correctness issues: #669 CGEMM wrong on AMD RX 5700, #668 SSYRK/SSYR2K error on Apple M1, #561 FP16 GEMV wrong; installation.md says CMake 2.8.10 but CMakeLists needs 3.14.

## Caveats and trade-offs

Baselines are GPU BLAS libraries, not OpenBLAS/MKL/Eigen/BLIS; NVIDIA cuBLAS beats CLBlast in the paper; the \~2x FP16 figure is vs CLBlast's own FP32 and the up-to-10x batched figure is vs non-batched calls, neither is vs a baseline library; versions &lt;=1.6.2 had correctness issues on Intel Arc A770 and other devices (fixed in 1.6.3)

GPU/OpenCL; needs tuning per device

## Maintenance

Actively maintained (1.7.0 is the latest release, commits into September 2026, tuning results still being added), Apache-2.0 and packaged by major distros, so it is usable as-is; plan to run the tuners and correctness tests on devices outside its tuned list.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IWOCL '18 paper compares CLBlast 1.3.0 GEMM against clBLAS 2.12 on 7 devices and shows it significantly better overall, but gives the win qualitatively and in graphs, without a numeric ratio vs clBLAS; tier B stays, the claim was overstated.
- **Verifier notes:** Record said 'approaching cuBLAS' but the paper says cuBLAS is still superior; the 2x/10x numbers are self-comparisons. Metadata (Apache-2.0, 1.2k stars, last commit 2026-09-28) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1705.05249>
  - <https://arxiv.org/pdf/1705.05249>
  - <https://github.com/CNugteren/CLBlast>
  - <https://github.com/CNugteren/CLBlast/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/README.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/installation.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/details_gemm.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/faq.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/tuning.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/benchmarking.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/api.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/doc/routines.md>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/include/clblast.h>
  - <https://raw.githubusercontent.com/CNugteren/CLBlast/HEAD/include/clblast_netlib_c.h>
  - <https://github.com/CNugteren/CLBlast>
  - <https://github.com/CNugteren/CLBlast/releases>
  - <https://github.com/CNugteren/CLBlast/issues?q=is%3Aissue+is%3Aopen+wrong+OR+incorrect+OR+crash>
  - <https://github.com/CNugteren/CLBlast/issues/578>
  - <https://github.com/CNugteren/CLBlast/issues/669>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cnugteren/clblast`) · [data/wave8/enrich/raw/github_com_cnugteren_clblast.json](../../../data/wave8/enrich/raw/github_com_cnugteren_clblast.json) (enrichment confidence 0.8)

</details>
