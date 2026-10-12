# MatX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++ (CUDA)` · `BSD-3-Clause` · 🟢 active

> NumPy-style C++20 GPU array library whose JIT fusion of a cuFFT pipeline ran 1.61x faster than handwritten CUDA + cuFFT.

| | |
|---|---|
| **Beats** | handwritten CUDA kernels + cuFFT (FFT pipeline); also CuPy 14.1.1 eager and NumPy 2.5.1 + SciPy 1.18.0 (Black-Scholes) |
| **Claimed result** | FFT pipeline: MatX CUDAJITExecutor 0.1114 ms vs handwritten CUDA + cuFFT 0.1792 ms = 1.61x faster (MatX cudaExecutor 0.1848 ms = 0.97x, i.e. slightly slower than the handwritten version). Black-Scholes 100M FP32: MatX 16.07 ms vs CuPy 14.1.1 eager 90.32 ms = 5.62x faster, vs NumPy 2.5.1 + SciPy 1.18.0 on CPU 2965.66 ms = 184.5x faster. |
| **Workload** | 256 batched 4096-point complex FP32 FFTs with fused input normalization and calibrated-magnitude/dB post-processing (median kernel time), plus 100M FP32 Black-Scholes option prices (median time, transfers excluded). |
| **Metric** | latency |
| **Hardware** | NVIDIA DGX Spark (GB10 GPU), 20-core Arm CPU (10 Cortex-X925 + 10 Cortex-A725), driver 580.159.03 (stated for the Black-Scholes run) |
| **Compiler and flags** | CUDA 13.0 (nvcc) with MathDx 26.03 for the JIT case; FFT reproduce command: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DMATX_BUILD_EXAMPLES=ON -DMATX_EN_MATHDX=ON, cmake --build build --target fft_benchmark, ./build/examples/fft_benchmark 256 4096 2000 (CMAKE_CUDA_ARCHITECTURES defaults to native; MATX_CUDA_FLAGS adds --threads 0 --extended-lambda). The Black-Scholes reproduce command omits CMAKE_BUILD_TYPE (MatX then adds -lineinfo). Host C++ compiler and version not stated. |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/NVIDIA/MatX) · [benchmark](https://github.com/NVIDIA/MatX) |

## Verdict

On one NVIDIA DGX Spark (GB10, CUDA 13.0, MathDx 26.03), the public examples/fft_benchmark.cu (10 warmups, seven interleaved trials of 2,000 iterations timed with CUDA events, median of five executions) ran 256 batched 4096-point complex FP32 FFTs with normalization before and calibration, magnitude and dB after: handwritten CUDA kernels + cuFFT took 0.1792 ms, MatX cudaExecutor 0.1848 ms, and MatX CUDAJITExecutor 0.1114 ms (1.61x). A separate 100M-option FP32 Black-Scholes run took 16.07 ms in MatX vs 90.32 ms for eager CuPy 14.1.1 on the same GPU and 2965.66 ms for single-threaded NumPy 2.5.1 + SciPy 1.18.0.

## Use it when

- Memory-bound GPU signal-processing chains: element-wise pre- and post-processing around batched 1-D power-of-two FFTs that cuFFTDx can run in one block (the benchmark used 256 x 4096 complex FP32).
- C++ code that wants NumPy-like array expressions on NVIDIA GPUs without writing kernels; cudaExecutor came within 3% of a handwritten CUDA + cuFFT pipeline.
- Long-running processes that reuse the same expression shapes, so the per-operator JIT compile is paid once and then cached.
- Large element-wise formulas (Black-Scholes style) that an eager array library such as CuPy would split into many kernels with materialized temporaries.
- Grace or DGX Spark systems where the same expression should also run on the Arm host through NVPL.

## Skip it when

- You need a faster FFT by itself: MatX's non-JIT FFT path is cuFFT and measured 3% slower than handwritten CUDA + cuFFT; all of the gain comes from fusing surrounding work.
- FFT sizes or expressions the JIT path cannot lower: non-power-of-two sizes, transforms too large for one cuFFTDx block, or operators with incompatible elements-per-thread needs (the fusion guide's fftshift1D(fft(b)) example). CUDAJITExecutor throws on these instead of falling back.
- Short-lived processes or many distinct shapes: the fusion guide puts first-run JIT compilation at milliseconds to seconds, and the README does not publish the compile time the benchmark prints.
- Non-NVIDIA GPUs, or Windows deployments that need JIT or multi-GPU (Windows support is alpha, with no JIT and no multi-GPU).
- Pipelines already fused with cuFFT load/store callbacks, the incumbent's own fusion route, which the benchmark does not compare against.

## How it is fast

Expression templates: each operator returns a lazy type, so a chain of element-wise operations compiles into one kernel with no intermediate arrays, and transforms such as fft and matmul can sit inside expressions. With -DMATX_EN_MATHDX=ON, CUDAJITExecutor uses NVRTC and libmathdx-generated LTOIR to compile the whole expression, including a block-level cuFFTDx FFT, into one runtime-generated kernel. In the benchmark, normalization then runs on load and calibration, magnitude and dB on store, which removes two 8.4 MB temporaries and two extra launches. The plain cudaExecutor path still calls cuFFT between generated pre- and post-kernels and is no faster than handwritten code.

## Compared with alternatives

Pick MatX when the FFT is one stage of a larger GPU pipeline and the cost is in pre- and post-processing traffic; VkFFT (cross-vendor, roughly cuFFT parity on radix 2-13), TurboFFT and tcFFT target the standalone FFT kernel, FlashFFTConv is the choice for FFT convolutions inside PyTorch models, and the CPU siblings (FFTW-class libraries, PocketFFT, KFR) do not compete on GPU.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake interface target matx::matx via add_subdirectory, or the Conan Center package) |
| **Dependencies** | CUDA Toolkit (cuFFT, cuBLAS and other CUDA libraries); optional MathDx/libmathdx (downloaded by CMake with MATX_EN_MATHDX=ON) for JIT fusion; optional NVPL, FFTW, OpenBLAS or BLIS for host executors; cuTENSOR/cuTensorNet for einsum and cuDSS for sparse solve |
| **Minimum toolchain** | C++20; Linux: CUDA 12.2.1+ with g++ 9.3+, clang 17+ or nvc++ 24.5 as host compiler (Conan matx/1.0.0 requires CUDA 13.x); CMake 3.30.4+ for examples, tests and benchmarks; Windows: Visual Studio 2026 and CUDA 13.3+ |
| **Platforms** | Linux on NVIDIA GPUs (full support); Windows alpha without JIT or multi-GPU; host executors on x86 (FFTW, OpenBLAS, BLIS) and NVIDIA Arm CPUs (NVPL) |
| **Thread safety** | Not documented in general; issue #1039 showed the FFT plan cache was shared across host threads, so the same FFT on a second thread failed in cuFFT; fixed by PR #1040 (August 2025) |
| **Drop-in for the baseline** | no |

## Gotchas

- The 1.61x is a memory-traffic result on a low-bandwidth GPU (derived from page data and the harness's buffer sizes). The handwritten path moves about 50 MB per call (8.4 MB signal read, two 8.4 MB temporaries each written and read, 4.2 MB calibration read, 4.2 MB output write), which is about 281 GB/s at 0.1792 ms, at or above the 273 GB/s LPDDR5x figure on NVIDIA's DGX Spark hardware page (WebSearch snippet). The fused kernel moves about 16.8 MB, about 151 GB/s at 0.1114 ms. The ratio on HBM GPUs is unmeasured.
- The validation check is loose: outputs are compared in dB with a 2e-3 relative tolerance and a max(1, |ref|) denominator, which allows about 0.14 dB (about 1.7% in magnitude) near the 72 dB peak. The README does not publish the achieved error or the JIT compile time that the harness prints.
- make_tensor defaults to managed memory (MATX_MANAGED_MEMORY). That is harmless on DGX Spark's unified memory, but on discrete GPUs, touching results from the host causes page migration unless you choose another memory space.
- JIT fusion is labelled experimental ('may contain bugs that don't occur with JIT disabled'). Black-Scholes caveat: the four MatX variants are checked only against each other (1e-6), never against the CuPy/NumPy outputs, whose inputs are generated differently (cuRAND uniform vs NumPy default_rng clamped to 1e-6).

## Known shortcomings

- README FFT table reproduced exactly from public examples/fft_benchmark.cu (CUDA 13.0, MathDx 26.03, Release, GB10). Authors wrote the cuFFT baseline without LTO callbacks; the 1.61x comes from fusing via cuFFTDx, not a faster FFT; plain cudaExecutor is 3% slower than cuFFT; one machine; no FFTW, MKL or KissFFT rows. Black-Scholes rows weak: no build type, MatX row ambiguous among 4 variants, eager CuPy and single-thread NumPy baselines.
- Enricher: the handwritten baseline moves about 50 MB per call (about 281 GB/s, at or above DGX Spark's 273 GB/s LPDDR5x spec) while the fused kernel moves about 16.8 MB (about 151 GB/s), so the 1.61x is a traffic cut on the bandwidth-starved GB10 and HBM GPUs are unmeasured; validation is loose (dB domain, 2e-3 relative, up to about 0.14 dB at peak); the README omits JIT compile time; Black-Scholes MatX outputs are never compared with CuPy or NumPy outputs; make_tensor defaults to managed memory. FFT plan-cache thread bug #1039 fixed by PR #1040.

## Caveats and trade-offs

First-party NVIDIA numbers on one machine (DGX Spark GB10); the README says performance depends on GPU, clocks, shape and software versions. The FFT baseline is a 59-line handwritten CUDA + cuFFT pipeline written by the MatX authors (separate normalize kernel, out-of-place cufftExecC2C, separate calibrate/magnitude/dB kernel, two cudaMalloc temporaries); the plain cudaExecutor path is 3% slower than it, so the 1.61x comes only from fusing pre- and post-processing into one cuFFTDx kernel via CUDAJITExecutor, not from a faster FFT. The baseline does not use cuFFT's own load/store (LTO) callbacks, the incumbent's native way to fuse such pre/post work, so the gap against a best-practice cuFFT pipeline is unmeasured. JIT compile time is reported separately and excluded from steady-state timing. No comparison against the fft category's baselines (FFTW, MKL FFT, KissFFT): the harness can print an optional MatX host result through NVPL or FFTW, but the README publishes none. Black-Scholes rows (off-category, tier C on their own): the reproduce command omits CMAKE_BUILD_TYPE, which in MatX's CMakeLists adds -lineinfo and leaves host flags unoptimized (device code still gets nvcc's default optimization); examples/black_scholes.cu prints four MatX variants (plain expression, custom operator, apply() lambda, apply_idx() lambda) with no warmup before the first, and the README does not say which row gives 16.07 ms (the Python companion's docstring says it matches the apply() case); MatX inputs are unclamped uniform [0,1) while the Python harness clamps to 1e-6; MatX is timed by CUDA events in C++ and CuPy/NumPy by a separate Python script; the CuPy baseline is an eager expression with materialized intermediates, not a fused cupy.fuse or ElementwiseKernel; NumPy/SciPy runs single-threaded on the CPU, so 184.5x compares a GPU with one CPU thread. The README FFT benchmark was added on 2026-07-22 (#1208). [retier] Gain is cuFFTDx fusion cutting traffic from about 50 MB to about 16.8 MB per call on GB10 (LPDDR5x 273 GB/s); plain cudaExecutor 3% slower than cuFFT; validation loose (2e-3 relative in dB domain); JIT compile time omitted; Black-Scholes rows uncompared for correctness; make_tensor defaults to managed memory; FFT plan-cache thread bug #1039 fixed by #1040.

GPU-first (NVIDIA) header-only C++20 library; the fused-kernel speedup needs the optional MathDx (cuFFTDx) backend, a supported FFT shape and the CUDAJITExecutor, and JIT compilation cost is excluded from the steady-state timing. Linux fully supported, Windows alpha. CPU executors (OpenMP, NVPL, FFTW) exist but the README gives no CPU numbers.

## Maintenance

Actively developed NVIDIA project (1,139 commits, last commit 2026-10-10, 1.4k stars, 11 open issues), BSD-3-Clause and header-only, so it is easy to vendor; the JIT fusion behind the headline number is new (cuFFTDx support issue #976 closed April 2026, README benchmark added July 2026) and still marked experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README FFT table (CUDA + cuFFT 0.1792 ms, MatX cudaExecutor 0.1848 ms, MatX CUDAJITExecutor 0.1114 ms = 1.61x) comes from the public harness examples/fft_benchmark.cu (interleaved trials, 10 warmups, 2000 iterations x 7 trials, median, outputs validated against the cuFFT reference at 2e-3 relative tolerance), with CUDA 13.0 + MathDx 26.03, a stated Release CMake configure (flags in the public CMakeLists.txt) and the DGX Spark GB10 GPU plus its named 20-core Arm CPU. Host compiler version is not stated, but the timed work is device code built by the named nvcc.
- **Verifier notes:** Numbers match the README exactly and come from a public, validated, interleaved harness, so A stands for the FFT pipeline; the Black-Scholes rows are a weaker, off-category comparison (unfused CuPy, single-thread NumPy, ambiguous MatX row). Shortcomings: baseline written by the MatX authors and not using cuFFT callbacks, speedup comes from kernel fusion via cuFFTDx rather than a faster FFT, cudaExecutor alone is 3% slower than handwritten CUDA + cuFFT, single machine (GB10), no FFTW/MKL/KissFFT comparison; experimental JIT fusion rejects unsupported shapes.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-172 (wave 8); enricher w8 pair-034
- **Pages the verifier opened:**
  - <https://github.com/NVIDIA/MatX>
  - <https://github.com/NVIDIA/MatX/commits/main>
  - <https://github.com/NVIDIA/MatX/commits/main/examples/fft_benchmark.cu>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/fft_benchmark.cu>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/black_scholes.cu>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/black_scholes_benchmark.py>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/NVIDIA/MatX>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/fft_benchmark.cu>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/black_scholes.cu>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/black_scholes_benchmark.py>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/docs_input/build.rst>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/docs_input/basics/fusion.rst>
  - <https://raw.githubusercontent.com/NVIDIA/MatX/HEAD/include/matx/core/make_tensor.h>
  - <https://github.com/NVIDIA/MatX/issues?q=is%3Aissue+fft>
  - <https://github.com/NVIDIA/MatX/issues/1039>
  - <https://github.com/NVIDIA/MatX/issues/1107>
  - https://docs.nvidia.com/dgx/dgx-spark/hardware.html (WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvidia/matx`) · [data/wave8/enrich/raw/github_com_nvidia_matx.json](../../../data/wave8/enrich/raw/github_com_nvidia_matx.json) (enrichment confidence 0.8)

</details>
