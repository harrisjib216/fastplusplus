# NonuniformFFTs.jl (Julia NUFFT, CPU and GPU) vs FINUFFT and cuFINUFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia NUFFT library for CPU, CUDA and AMD GPUs; its shared-memory GPU spreading beats cuFINUFFT on dense 3D type-1 transforms.

| | |
|---|---|
| **Beats** | FINUFFT v2.4.1 (C++, CPU) and cuFINUFFT (CUDA C++, GPU), both compiled locally and called through FINUFFT.jl v3.4.0 |
| **Claimed result** | Docs and README text match the record (CPU 'comparable'; GPU default method 'slightly faster than CuFINUFFT at low point densities, but slightly slower at large ones'; shared-memory method gives 'important gains'). Numbers come from the raw medians in benchmark/CPU+CUDA/results.H100_jean-zay/\*.dat (ComplexF64, 256^3, tol 1e-6, set_points plus exec; all ratios derived from page data). GPU type 1: at density 1e-4 (1,678 points) NonuniformFFTs global-memory 0.00322 s vs CuFINUFFT 0.00536 s (1.66x faster); at density 1 (16.8M points) NonuniformFFTs shared-memory 0.0415 s vs CuFINUFFT's best 0.1774 s (4.27x faster) while the default global-memory method is 0.2809 s vs 0.1809 s (1.55x slower); at density 10 (167.8M points) shared-memory 0.300 s vs CuFINUFFT's best (its own SM method) 0.822 s (2.74x faster; 6.97x against CuFINUFFT GM 2.089 s) while the default method is 3.187 s (1.53x slower than CuFINUFFT GM). GPU type 2: 1.92x faster at density 1e-4 (0.00280 s vs 0.00538 s) but slower at high density with either method (best 0.0295 s vs 0.0223 s at density 1, 1.32x slower; 0.2166 s vs 0.1087 s at density 10, 1.99x slower). CPU (24 threads): type 1 ranges from 1.93x faster (atomics variant, 0.105 s vs 0.202 s at density 1e-4) to 1.78x slower (atomics, 1.273 s vs 0.717 s at density 1), and 1.03-1.17x faster at density 10; type 2 is 1.84x faster at density 1e-4 (0.0867 s vs 0.1598 s) and 1.56x at 1e-3 (FFT-dominated cases), 0.89-0.96x at densities 0.1 and 1, and 1.05x at density 10. |
| **Workload** | Type-1 and type-2 3D non-uniform FFTs on a uniform 256^3 grid, random points in [0, 2\*pi)^3 with point density N/M^3 from 1e-4 to 10, tolerance 1e-6, Float64 complex data; each time includes set_points plus the transform. |
| **Metric** | throughput |
| **Hardware** | Jean Zay (IDRIS): 2x Intel Xeon Platinum 8468 (24 cores used) and one NVIDIA H100 SXM5 80 GB (1/4 of a node). A second run on one AMD Instinct MI300A (Adastra) compares only the CPU against FINUFFT. |
| **Compiler and flags** | FINUFFT v2.4.1 built with Nvidia nvc++ (version not stated) via CMake 'Release' with default flags (actual flags not printed); cuFINUFFT built with nvcc from CUDA 12.8, CMAKE_CUDA_ARCHITECTURES=90; both called through FINUFFT.jl v3.4.0 with locally compiled binaries. FINUFFT options: tol 1e-6, modeord=1, spread_sort=1, spread_kerevalmeth=1, FFTW.ESTIMATE, nthreads = Julia thread count (24); cuFINUFFT gpu_sort=1, gpu_kerevalmeth=1, gpu_method 1 and 2; upsampfac left at the library default (only the 1e-14 reference plans set 2.0). NonuniformFFTs.jl v0.8.3 (2025-07-11), sigma=1.5, HalfSupport(4), FFTW.ESTIMATE, KernelAbstractions/CUDA.jl; Julia version not stated (benchmark Project.toml has no Manifest or compat). BenchmarkTools @benchmark medians. Script: benchmark/CPU+CUDA/run_benchmarks.jl. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Docs, GPU only and hedged: the shared-memory variant 'completely avoids atomic operations on shared memory', which 'seems to speed up things quite a bit and might explain the important gains' over cuFINUFFT. The implementation is described as 'heavily inspired' by the cuFINUFFT paper, so the algorithm family is the same but not identical. |
| **Adoption** | 26 stars; Julia General registry package |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/jipolanco/NonuniformFFTs.jl) · [benchmark](https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/docs/src/benchmarks.md) |

## Verdict

The author benchmarked NonuniformFFTs.jl v0.8.3 (σ = 1.5, width-8 KB kernel) against FINUFFT v2.4.1 (nvc++ Release) and cuFINUFFT (nvcc from CUDA 12.8, sm_90) called through FINUFFT.jl v3.4.0, on one Jean Zay node share (2x Xeon Platinum 8468 with 24 cores used, one H100 80 GB), for 3D 256^3 ComplexF64 transforms at tol 1e-6. Times are BenchmarkTools medians of set_points plus exec. The GPU type-1 shared-memory method was 2.7-4.3x faster than cuFINUFFT's best at densities of 1-10, while the default method was 1.5x slower there and type 2 was slower at high density; CPU results were within about 2x either way, and the Julia version is not stated.

## Use it when

- Dense 3D type-1 NUFFTs on NVIDIA GPUs (about one or more points per grid cell) with gpu_method = :shared_memory: on an H100 at 256^3 and tol 1e-6 it ran 2.7-4.3x faster than cuFINUFFT's best method (0.300 s vs 0.822 s at 168M points).
- Real-valued non-uniform data such as particle densities or vortex filaments, where the r2c/c2r path halves spreading and FFT work; FINUFFT has no such path.
- Julia codes that want one NUFFT implementation for CPU threads, CUDA and AMD GPUs, or that need callbacks to modify input and output on the fly.
- Memory-constrained 3D GPU jobs: with σ = 1.5 the oversampled 256^3 grid is 384^3 (about 0.9 GB of ComplexF64) against cuFINUFFT's 512^3 (about 2.1 GB) at its default upsampfac of 2.0.

## Skip it when

- 2D (and probably 1D) GPU transforms. Open issue #69 shows it up to 11.5x slower than cuFINUFFT on a 128x128 grid (shared memory at 163,840 points: 0.0202 s vs 0.00175 s); the maintainer says the package is 'mostly optimised for 3D'.
- Type-2 (interpolation) at high point density on the GPU, where it is 1.3-2.0x slower than cuFINUFFT with either method; type-1 with the default :global_memory method is about 1.5x slower at densities of 1 and above.
- CPU-only work where FINUFFT is already available: the H100-node CPU rows range from about 1.9x faster to 1.8x slower depending on density and on the use_atomics setting.
- AMD GPUs with many points on the default method: the docs say :global_memory 'scales very poorly' there, so switch to :shared_memory.
- C, C++, Python or MATLAB callers: it needs a Julia runtime, while FINUFFT ships native interfaces for all of these.

## How it is fast

It is the standard gridding NUFFT: spread each point onto an oversampled grid with a compact (backwards) Kaiser-Bessel kernel, run FFTW or cuFFT, then deconvolve; type 2 runs the steps in reverse. On the CPU, points are partitioned into spatial blocks for multithreading, and kernel weights use a piecewise FastApproximation. On the GPU there are two methods. The default :global_memory method sorts points into blocks and adds atomically into global memory. The :shared_memory method stages each grid block in workgroup shared memory and processes points in batches so that no shared-memory atomics are needed; the docs credit this for the gains over cuFINUFFT's SM method, which is based on Shih et al. 2021. Real-valued data use r2c/c2r FFTs and spread half as much data.

## Compared with alternatives

The catalogued siblings in runtime-jit-beats-aot are language-runtime microbenchmarks (.NET JIT, Bun, ClangJIT) rather than libraries; the realistic alternative is the listed baseline FINUFFT/cuFINUFFT. Pick NonuniformFFTs.jl over it for dense 3D type-1 GPU work with the shared-memory method, or for real-valued data in Julia. Stay with FINUFFT for 2D GPU, high-density type 2, CPU-only work or non-Julia callers.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages FFTW, KernelAbstractions, AcceleratedKernels, OhMyThreads, Atomix, Bessels, StaticArrays, AbstractFFTs, AbstractNFFTs, Adapt, TimerOutputs; package extensions for CUDA (CUDACore.jl v6 + cuFFT.jl v6), AMDGPU.jl (v1.0.5 or v2) and StructArrays |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat); the CUDA extension requires the CUDA.jl v6 package split (since v0.9.2) |
| **Platforms** | CPU on any Julia platform (multithreaded), NVIDIA GPUs through CUDA.jl, AMD GPUs through AMDGPU.jl; other KernelAbstractions backends in principle |
| **Thread safety** | not documented; the plan holds point and buffer state that set_points! and exec_\* overwrite, and multithreading happens inside each call (Julia threads on CPU) |
| **Drop-in for the baseline** | partial — implements the AbstractNFFTs.jl (NFFT.jl-style) interface for complex data only, not FINUFFT's or FINUFFT.jl's makeplan/setpts/exec API; mode ordering and the kernel and σ parameters differ |

## Gotchas

- Harness parameter asymmetry explains most of the GPU result. The script fixes σ = 1.5 with HalfSupport(4), a width-8 kernel on a 384^3 grid, but never sets upsampfac for cuFINUFFT. cufinufft's auto choice (include/cufinufft/impl.h, v2.4.1) gives 2.0 for types 1 and 2, so ns = ceil(-log10(tol/10)) = 7 on a 512^3 grid. NonuniformFFTs therefore does a 2.37x smaller FFT but 1.49x more kernel evaluations per point (512 vs 343). Its low-density wins (1.66x type 1, 1.92x type 2 at 1,678 points) and its default-method losses at high density (1.53-1.55x on type 1) track those two ratios. cuFINUFFT has supported upsampfac = 1.25 on GPU since v2.3, and the script did not try it. Only the shared-memory type-1 rows win despite doing more kernel work per point.
- On the CPU the two libraries also run different accuracy and work settings. FINUFFT 2.4.1 auto-picks upsampfac from heuristics.hpp with the density hard-coded to 1 (finufft_core.cpp), which gives 1.25 here at 24 threads and tol 1e-6. That means ns = 10 (1000 kernel evaluations per point vs 512) on a 320^3 grid, and FINUFFT's measured type-1 error is 3.73e-6, missing the requested 1e-6, against 1.28e-6 for NonuniformFFTs. Separately, the benchmark's σ = 1.5 is not the package default: PlanNUFFT defaults to σ = 2.0, which gives a 512^3 grid with a width-8 kernel, so an untuned plan will not reproduce the published curves.
- The docs say the points are uniform in [0, 2π)^3, but run_benchmarks.jl draws standard-normal coordinates (randn with Xoshiro(42)) for both libraries. The cloud is clustered around the origin corner of the periodic box, which changes atomic contention during spreading, so results for genuinely uniform points may differ (not measured). Both libraries receive identical points and agree on accuracy to within about 25% on the GPU (type-1 error 1.74e-6 vs 1.39e-6).
- Open bug #95 (2026-10-07): on the GPU, Float32 points slightly below 0 fold to exactly 2π and index one past the grid, which gives intermittent wrong results or CUDA illegal-memory-access errors. The CPU path is not affected; the workaround is to fold points into [0, 2π) yourself. v0.9.5 fixed a related out-of-bounds bug for points near L on certain grid sizes, and the benchmarked v0.8.3 predates that fix. The README GPU example also passes an undefined xp to set_points! (it should pass points).

## Known shortcomings

- Julia version, nvc++ version and FINUFFT flags unstated; the raw .dat medians show a narrow GPU win (type 1, non-default shared-memory method, 2.7-4.3x over cuFINUFFT's best at density 1 and above) while the default method is 1.5x slower at high density, type 2 at high density is 1.99x slower and the CPU is parity; docs say uniform points but the script draws randn; the win comes from design and parameters (sigma 1.5, no shared-memory atomics), not the JIT.
- Harness flaw: parameters differ between libraries. cuFINUFFT auto-selects upsampfac 2.0, ns 7 and a 512^3 grid while NonuniformFFTs ran sigma 1.5, width 8 and a 384^3 grid (2.37x smaller FFT, 1.49x more kernel work per point); the GPU low-density wins (1.66x/1.92x) and default-method losses (1.53-1.55x) track those ratios, and only the shared-memory type 1 wins on its own merit. CPU FINUFFT 2.4.1's heuristic hard-codes density 1 and picks upsampfac 1.25, ns 10, and its error 3.73e-6 misses tol 1e-6 (NonuniformFFTs 1.28e-6). The package default sigma is 2.0, not the benchmarked 1.5. Open issue #95: GPU Float32 points just below 0 index out of bounds; open issue #69: up to 11.5x slower than cuFINUFFT in 2D on GPU.

## Caveats and trade-offs

Author's own benchmark; the docs show only SVG plots, numbers exist only in the raw .dat files. The CPU result is parity (wins and losses by up to about 2x either way depending on density), not a win. The GPU win is limited to type 1 with the non-default shared-memory method at densities of about 1 and above, or to very sparse problems; the default global-memory method is about 1.5x slower than CuFINUFFT at high density, and type 2 at high density is slower than CuFINUFFT with either method. The docs say CuFINUFFT's gpu_method=2 'seems to be considerably slower in nearly all cases', but the raw data show it beating CuFINUFFT's method 1 for type 1 at densities of 1 and above (0.822 s vs 2.089 s at density 10), so fair comparisons must use CuFINUFFT's SM curve. The two libraries do not do the same work: NonuniformFFTs uses sigma=1.5 with a width-8 Kaiser-Bessel-type kernel while (Cu)FINUFFT uses its own kernel with its default upsampling factor (not set by the script); measured errors are of the same order (type 1 about 1.7e-6 vs 1.4e-6 on GPU, 1.3e-6 vs 3.7e-6 on CPU). The docs say points are uniform in [0, 2\*pi)^3, but run_benchmarks.jl draws standard-normal coordinates (randn, Xoshiro(42)) for both libraries, so the point cloud is clustered. FINUFFT was built with nvc++ rather than GCC or Clang, and the CPU sides probably use different FFTW builds (locally built FINUFFT vs FFTW.jl), which would dominate the sparse-point CPU rows (not verified). The 'real data' gains solve a different (real-valued) problem. On AMD GPUs the default method scales badly. Only one GPU model (H100), one grid size and one tolerance (1e-6); Julia version not stated. Not a JIT-versus-AOT effect: the GPU gains come from a different shared-memory spreading design. [retier] Parameters differ between libraries: cuFINUFFT auto-selects upsampfac 2.0, ns 7 and a 512^3 grid while NonuniformFFTs ran sigma 1.5, width 8 and a 384^3 grid (2.37x smaller FFT, 1.49x more kernel work per point); the GPU low-density wins (1.66x/1.92x) and default-method losses (1.53-1.55x) track those ratios, and only the shared-memory type 1 wins on its own merit. CPU FINUFFT 2.4.1's heuristic picks upsampfac 1.25, ns 10, and its error 3.73e-6 misses tol 1e-6 (NonuniformFFTs 1.28e-6). The package default sigma is 2.0, not the benchmarked 1.5. Open #95 (GPU Float32 points just below 0 index out of bounds) and #69 (up to 11.5x slower than cuFINUFFT in 2D on GPU).

Julia package; one KernelAbstractions.jl code base targets CUDA, AMD and other GPUs. Also offers real-valued non-uniform data transforms (extra gains, not available in FINUFFT).

## Maintenance

Actively maintained by a single author (v0.9.7 in Project.toml, last commit 2026-10-01, MIT, 26 stars, registered in the Julia General registry). It is usable from Julia today, but it has an open GPU out-of-bounds bug for Float32 points just below 0 and weak 2D GPU performance, and the published numbers come from v0.8.3 with tuned σ = 1.5, not the default 2.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The docs page benchmarks.md, the script benchmark/CPU+CUDA/run_benchmarks.jl and the raw medians in benchmark/CPU+CUDA/results.H100_jean-zay/\*.dat are public and name the CPU (Xeon Platinum 8468) and GPU (H100), but the Julia version is not stated anywhere (the benchmark Project.toml has no Manifest or compat bounds), the nvc++ version is not given and the actual FINUFFT Release flags are not printed, so it falls short of A (same rule as the wave-14 AcceleratedKernels verdict); first-party, hence C.
- **Verifier notes:** Downgrade A to C: Julia version and nvc++ version/flags are not stated, and the evidence is first-party. Real but narrow GPU win (type 1, non-default shared-memory method, density of about 1 and above: 2.7-4.3x over CuFINUFFT's best), CPU parity, type 2 slower at high density; the win is an implementation and parameter difference, not a Julia-vs-C++ codegen effect, so it fits runtime-jit-beats-aot poorly. Baseline FINUFFT is already listed (wave 8, https://github.com/flatironinstitute/finufft).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/README.md>
  - <https://github.com/jipolanco/NonuniformFFTs.jl>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/commits/master>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/tree/master/benchmark/CPU+CUDA>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/commits/master/benchmark/CPU+CUDA/run_benchmarks.jl>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/tree/master/benchmark/CPU+CUDA/results.H100_jean-zay>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/run_benchmarks.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/Project.toml>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/README.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/plots/plot_benchmarks.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/CuFINUFFT_256_ComplexF64_global_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/CuFINUFFT_256_ComplexF64_shared_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/FINUFFT_256_ComplexF64_CPU.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CPU.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CPU_atomics.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CUDABackend_global_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CUDABackend_shared_memory.dat>
- **Sources the enricher read:**
  - <https://github.com/jipolanco/NonuniformFFTs.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/README.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/Project.toml>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/docs/src/accuracy.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/src/NonuniformFFTs.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/src/plan.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/src/gpu_common.jl>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/tree/master/src>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/run_benchmarks.jl>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/Project.toml>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/README.md>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/CuFINUFFT_256_ComplexF64_global_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/CuFINUFFT_256_ComplexF64_shared_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/FINUFFT_256_ComplexF64_CPU.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CPU.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CUDABackend_global_memory.dat>
  - <https://raw.githubusercontent.com/jipolanco/NonuniformFFTs.jl/master/benchmark/CPU%2BCUDA/results.H100_jean-zay/NonuniformFFTs_256_ComplexF64_CUDABackend_shared_memory.dat>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/issues?q=is%3Aissue>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/issues/95>
  - <https://github.com/jipolanco/NonuniformFFTs.jl/issues/69>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/src/finufft_core.cpp>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/include/finufft/heuristics.hpp>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/src/spreadinterp.cpp>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/include/cufinufft/impl.h>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/src/cuda/cufinufft.cu>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/src/cuda/common.cu>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/v2.4.1/CHANGELOG>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/jipolanco/nonuniformffts.jl`) · [data/wave14/enrich/raw/github_com_jipolanco_nonuniformffts_jl.json](../../../data/wave14/enrich/raw/github_com_jipolanco_nonuniformffts_jl.json) (enrichment confidence 0.75)

</details>
