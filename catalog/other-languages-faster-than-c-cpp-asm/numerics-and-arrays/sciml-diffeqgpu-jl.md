# DiffEqGPU.jl (GPU ensemble ODE solvers in Julia, GPUTsit5) vs MPGOS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia GPU ensemble ODE/SDE solvers that compile one trajectory per thread; against MPGOS (CUDA C++) results are mixed.

| | |
|---|---|
| **Beats** | MPGOS (Massively Parallel GPU ODE Solvers), a CUDA C++ ensemble ODE solver library: RK4 (fixed step) and RKCK45 (adaptive), built with nvcc -O3 |
| **Claimed result** | No speedup numbers in the READMEs. The DiffEqGPU README says: 'See GPUODEBenchmarks for comparison of our GPU solvers against CPUs and GPUs implementation in C++, JAX and PyTorch'. Ratios below are MPGOS ms / Julia ms (derived from page data). Tesla_V100, fixed step: 8.5x to 10.0x for n=8 to 8192 (2.118/0.2317 = 9.1x at n=8), 2.8x at n=32768, then 0.88x at n=131072 and 0.65x at n=8,388,608 (94.157 vs 145.317 ms). Tesla_V100, adaptive: 6.9x at n=8, 1.4x at n=131072, 0.77x at n=524288, 0.70x at n=8,388,608 (48.808 vs 69.451 ms). RTX_5000, fixed step: 2.2x to 2.5x for n&lt;=2048, 5.4x at n=2,097,152 and 4.8x at n=8,388,608 (886.082 vs 183.920 ms). RTX_5000, adaptive: 0.52x to 0.66x for n&lt;=8192 (0.144 vs 0.253 ms at n=8), 1.08x at n=32768, 2.3x at n=8,388,608 (191.764 vs 83.490 ms). |
| **Workload** | Lorenz system (3 states, float32), ensemble of 8 to 8,388,608 parameter sets (R from 0 to 21) integrated over t in [0,1] with dt 0.001 on one GPU; fixed-step and adaptive (Julia reltol=abstol=1e-8) variants; wall time per whole ensemble solve in ms. |
| **Metric** | throughput |
| **Hardware** | NVIDIA Tesla V100 and an RTX 5000 (data folder names Tesla_V100 and RTX_5000; probably the Turing Quadro RTX 5000, but the files read do not say). Host CPU model, driver and CUDA toolkit version not stated. |
| **Compiler and flags** | MPGOS: nvcc -o Lorenz.exe -O3 -std=c++11 --ptxas-options=-v --gpu-architecture=sm_70 -lineinfo -maxrregcount=128 (GPU_ODE_MPGOS/makefile), BlockSize 1024, PRECISION float. runner_scripts/gpu/run_ode_cpp.sh rewrites Lorenz.cu to SOLVER RK4 for the fixed-step run and SOLVER RKCK45 for the adaptive run, and rebuilds for each n. Julia: DiffEqGPU.vectorized_solve (fixed dt 0.001f0) and vectorized_asolve (dt 0.001f0, reltol = abstol = 1f-8), both with GPUTsit5(), timed as the BenchmarkTools minimum of CUDA.@sync (GPU_ODE_Julia/bench_lorenz_gpu.jl). GPU_ODE_Julia/Manifest.toml pins Julia 1.8.5 and DiffEqGPU 2.1.0. The CUDA toolkit and CUDA.jl versions are not stated; the README recommends CUDA &gt;= 11. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 329 stars (DiffEqGPU.jl); 27 stars (GPUODEBenchmarks); part of the DifferentialEquations.jl ecosystem |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/SciML/DiffEqGPU.jl) · [benchmark](https://github.com/utkarsh530/GPUODEBenchmarks/tree/main/paper_artifacts/data) |

## Verdict

First-party GPUODEBenchmarks data: Float32 Lorenz ensembles (8 to 8.4M trajectories, t in [0,1], dt 0.001, tolerances 1e-8) with DiffEqGPU 2.1.0 GPUTsit5 on Julia 1.8.5 against MPGOS RK4/RKCK45 built with nvcc -O3 for sm_70, on a Tesla V100 and an RTX 5000 (host CPU and CUDA version not stated). Julia was 6-10x faster for small ensembles on the V100 and 2.3-4.8x faster at 8.4M on the RTX 5000, but 0.65-0.70x as fast at 8.4M on the V100. The C++ side was timed cold once and its RHS is promoted to FP64.

## Use it when

- 10^4 to 10^7 independent small non-stiff ODEs (a handful of states, Float32) on one GPU from Julia, e.g. parameter sweeps or Monte Carlo over u0/p.
- You need per-trajectory adaptive stepping, callbacks or events, stiff integrators (Rodas5P, Kvaerno5) or SDE methods (GPUEM, GPUSIEA) inside the kernel.
- Non-NVIDIA hardware: the same code targets CUDA, AMD ROCm, Intel oneAPI, Apple Metal and OpenCL backends, whereas MPGOS is CUDA-only.
- Code already written against the SciML EnsembleProblem API, where switching from EnsembleThreads to EnsembleGPUKernel is a one-line change.

## Skip it when

- Maximum throughput on a datacenter NVIDIA GPU at very large ensembles: in the authors' own data MPGOS was faster on the V100 from 131,072 trajectories up (0.65x fixed step and 0.70x adaptive for Julia at 8.4M).
- One large ODE whose cost is in a big structured f: use a CuArray state with OrdinaryDiffEq instead.
- Short jobs where latency to the first result matters: Julia JIT compile time was excluded from every timing, and the high-level solve() transfers problems to the GPU and results back on every call (lower-level API tutorial).
- Trajectories with very different costs (warp divergence; open issue #376), ContinuousCallback at high thread counts (out of dynamic GPU memory, open issue #219), SDEs with non-diagonal noise (open issue #331), or a RHS that needs generic linear algebra or allocations (#110).
- Float64 on consumer GPUs: the docs recommend Float32, and only Float32 was benchmarked.

## How it is fast

`EnsembleGPUKernel` generates one KernelAbstractions kernel (`ode_solve_kernel`, ndrange = number of trajectories) in which each GPU thread runs a complete integrator on its own problem: GPUTsit5 (FSAL, 6 RHS evaluations per step), GPUVern7/9, or Rosenbrock23, Rodas4/5P and Kvaerno3/5 for stiff problems. The state lives in StaticArrays, `@muladd` fuses multiply-adds, and Julia's GPU compiler inlines the user's RHS into the kernel. This removes the per-step kernel launches that make JAX or PyTorch vmap solvers slow. It is the same thread-per-system design MPGOS uses in CUDA C++, so against MPGOS there is no structural advantage: on the V100 at 8.4M trajectories the fixed-step time ratio (145.3 / 94.2 ms = 1.54) almost exactly matches Tsit5's 6 RHS evaluations per step over RK4's 4 (derived from page data).

## Compared with alternatives

OrdinaryDiffEq.jl is the CPU sibling and the right choice for one ODE or a few hundred trajectories; pick DiffEqGPU when you have thousands to millions of small independent ODEs and a GPU, or need AMD/Intel/Apple GPU support that MPGOS (CUDA C++) lacks, but not on the strength of a speed win over MPGOS.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | KernelAbstractions, SciMLBase, DiffEqBase, StaticArrays, Adapt, ForwardDiff, LinearSolve, SimpleDiffEq, SimpleNonlinearSolve and others; one GPU backend package loaded as a weak-dependency extension (CUDA.jl 6, AMDGPU.jl 2, oneAPI.jl 2, Metal.jl 1 or OpenCL.jl 0.10) |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat, DiffEqGPU 3.21.4); the MPGOS comparison used Julia 1.8.5 and DiffEqGPU 2.1.0 |
| **Platforms** | NVIDIA (CUDA), AMD (ROCm), Intel (oneAPI), Apple M-series (Metal), CPU via OpenCL/pocl |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the solver set replaces an MPGOS-style CUDA C++ ensemble solve, but the API is the Julia SciML EnsembleProblem interface, not MPGOS's ProblemSolver C++ class; RHS functions must be rewritten in Julia |

## Gotchas

- Crippled baseline (enricher finding, source-confirmed plus derived): GPU_ODE_MPGOS/Lorenz_SystemDefinition.cuh computes `10.0*( X[1]-X[0] )` and `X[0]*X[1] - 2.666 * X[2]` with double literals on float state, so every MPGOS RHS evaluation does FP64 multiplies and conversions; the Julia RHS uses 10.0f0 and 2.666f0. From the V100 to the RTX 5000, MPGOS slows 9.4x fixed step (94.157 to 886.082 ms at n=8,388,608) and 3.9x adaptive, while Julia slows only 1.27x and 1.20x (derived from page data). This is consistent with an FP64 bottleneck on the FP64-weak RTX 5000, so the RTX 5000 large-n wins (4.8x fixed, 2.3x adaptive) do not show faster code generation (inference; not rerun).
- Where the baseline is not FP64-bound (V100, n of 131,072 or more), MPGOS wins, and the 1.54x fixed-step gap matches the 6-versus-4 RHS evaluation count of Tsit5 against RK4, so per-evaluation cost is a wash; the integrators were never matched (Tsit5 against RK4 and RKCK45).
- Asymmetric timing: Lorenz.cu times one cold Solve() per process with clock() (process CPU time, which equals wall time only if the CPU spins during the synchronise), while bench_lorenz_gpu.jl reports the BenchmarkTools minimum of warm repeated `vectorized_solve` calls, with problem construction and the host-to-device copy outside the timed region. MPGOS's flat \~2 ms on the V100 for n up to 8192 produces the small-n 6-10x Julia lead.
- Stale, fragile harness: data pin DiffEqGPU 2.1.0 and Julia 1.8.5 (current 3.21.4, which merged 'Reduce EnsembleGPUKernel CPU host overhead' #560 on 2026-10-04). run_ode_cpp.sh rewrites Lorenz.cu lines 15 and 17 with sed. MPGOS appends to ./data/cpp while run_benchmark.sh clears ./data/CPP, so repeated runs accumulate rows. MPGOS is built for sm_70 only, so the RTX 5000 ran JIT-compiled PTX.

## Known shortcomings

- First-party asymmetric harness: MPGOS timed with one cold clock() launch against a warm BenchmarkTools minimum for Julia; methods differ (Tsit5 vs RK4/RKCK45); the C++ Lorenz RHS uses double literals 10.0 and 2.666 (Lorenz_SystemDefinition.cuh lines 11 and 13), probably crippling MPGOS on the FP64-weak RTX 5000 where Julia's large-n win sits; Julia loses on the V100 at large n (0.65x).
- Crippled baseline: MPGOS's Lorenz_SystemDefinition.cuh promotes to FP64 (10.0 and 2.666 double literals); from V100 to RTX 5000 at n=8.4M MPGOS slows 9.4x (fixed) and 3.9x (adaptive) while Julia slows only 1.27x and 1.20x, which fits an FP64 bottleneck, so the RTX 5000 wins of 4.8x and 2.3x come from the crippled baseline; the V100 fixed-step gap of 1.54x matches Tsit5's 6 against RK4's 4 right-hand-side evaluations, so per-evaluation cost is equal. The small-n win comes from cold clock() timing of one MPGOS launch against a warm BenchmarkTools minimum. The benchmark used DiffEqGPU 2.1.0 (current 3.21.4); the run scripts have a data/cpp vs data/CPP path mismatch.

## Caveats and trade-offs

Mixed result, not a uniform win, and the harness favours Julia in three ways. (1) Asymmetric timing: MPGOS runs once per process (one Solve() kernel launch timed with clock(), which measures process CPU time, plus cudaEventSynchronize), with no warm-up and no repetition. Julia reports the BenchmarkTools minimum over many warm runs. The MPGOS floor of about 2 ms for every n&lt;=8192 on the V100 (0.42 ms on the RTX 5000) looks like fixed first-launch or idle-clock overhead, and Julia's 6x to 10x V100 lead at small n probably comes from it (inference). (2) Unequal arithmetic in the C++ problem definition: GPU_ODE_MPGOS/Lorenz_SystemDefinition.cuh lines 11 and 13 use the double literals 10.0 and 2.666 with float state, so part of every right-hand-side evaluation runs in FP64 with float/double conversions. The Julia RHS uses 10.0f0 and 2.666f0. The RTX 5000 is probably the Quadro RTX 5000 (Turing), which runs FP64 at a small fraction of its FP32 rate, while the V100 runs it at half rate. This plausibly explains why MPGOS beats Julia 1.5x at n=8.4M on the V100 but loses 4.8x on the RTX 5000 (inference, not measured). (3) MPGOS is built for sm_70 only, so on the RTX 5000 (sm_75) it ran JIT-compiled PTX, also built with -maxrregcount=128. The methods also differ. Julia runs Tsit5 in both modes, while MPGOS runs RK4 (fixed step) and RKCK45 (adaptive). At fixed dt=0.001, Tsit5 makes about 6 RHS evaluations per step against RK4's 4. The tolerances do match: MPGOS defaults RelativeTolerance and AbsoluteTolerance to 1e-8 (SourceCodes/SingleSystem_PerThread_Interface.cuh, line 482), as Julia sets them. On the V100, Julia is slower than MPGOS for the largest ensembles (0.65x to 0.88x from n=131072 fixed step, 0.62x to 0.77x from n=524288 adaptive). On the RTX 5000 adaptive runs it is slower for n&lt;=8192. The host CPU and the exact RTX 5000 model are not stated. Only float32 was tested. The benchmark repo was last committed 2024-01-04 and pins DiffEqGPU 2.1.0, so the data predate current DiffEqGPU.jl. The CMAME 2024 paper (Utkarsh et al., 'Automated translation and accelerated solving of differential equations on multiple GPU platforms') was not opened (journal and arXiv blocked). GPUODEBenchmarks only holds the scripts and data; the solver lives in DiffEqGPU.jl. [retier] MPGOS's Lorenz_SystemDefinition.cuh promotes to FP64 (10.0 and 2.666 double literals): from V100 to RTX 5000 at n=8.4M MPGOS slows 9.4x (fixed) and 3.9x (adaptive) while Julia slows 1.27x and 1.20x, so the RTX 5000 wins of 4.8x and 2.3x come from the crippled baseline; the V100 fixed-step gap of 1.54x matches Tsit5's 6 against RK4's 4 right-hand-side evaluations (equal per-evaluation cost). The small-n win comes from cold clock() timing of one MPGOS launch against a warm BenchmarkTools minimum. Benchmarked DiffEqGPU 2.1.0 (current 3.21.4).

Specialised to many small independent ODEs (one trajectory per GPU thread); not a solver for one large ODE. Needs CUDA.jl (the only backend that the JAX, PyTorch and MPGOS comparison supports). Julia startup and compile time are excluded from the timings.

## Maintenance

Actively maintained (1,274 commits, Project.toml v3.21.4, newest commit 2026-10-08, 38 open issues) and MIT-licensed, so it is usable today. The MPGOS evidence is first-party and two major versions old, and its Julia wins trace to a cold-timed baseline (small n) and an FP64-promoted C++ RHS on an FP64-weak GPU (large n), so tier D under the crippled-baseline precedent is defensible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now D.
- **Tier reason:** All quoted times are in paper_artifacts/data/{Tesla_V100,RTX_5000}/{CPP,Julia}/\*_times_\*.txt, and the derived ratios check out. The code (GPU_ODE_MPGOS/Lorenz.cu, makefile, GPU_ODE_Julia/bench_lorenz_gpu.jl, runner_scripts/gpu/run_ode_{cpp,julia}.sh) is public. It is first-party, though: the scripts are by the DiffEqGPU authors. The host CPU and CUDA toolkit version are not stated, and the harness is asymmetric. MPGOS is timed once, cold, with clock() around one kernel launch, while Julia takes the BenchmarkTools warm minimum. The methods also differ: Tsit5 against RK4 and RKCK45. Finally, the C++ Lorenz right-hand side promotes float to double. Together these keep it below A and B.
- **Retiered** C to D: Enricher: the MPGOS baseline promotes its Lorenz system to FP64 and is timed cold with a single clock() launch against a warm BenchmarkTools minimum, so the RTX 5000 wins come from a crippled baseline and the small-n wins from the timing asymmetry; crippled-baseline precedent with no valid like-for-like row: C to D.
- **Verifier notes:** Downgraded A to C. The numbers are real and match the data files, but the evidence is first-party, the harness is asymmetric (one cold clock() launch against a warm BenchmarkTools minimum), the integrators differ, and the C++ Lorenz RHS uses double literals (10.0, 2.666), which probably cripples MPGOS on the FP64-weak RTX 5000, where Julia's large-n win appears. On the V100, Julia loses at large n (0.65x). If an enricher confirms the FP64-promotion effect, D under the crippled-baseline precedent is arguable. Corrected the caveat claiming tolerances were unset: MPGOS defaults to 1e-8, matching Julia. Metadata checked: MIT, 329 stars, last commit 2026-10-08, active; GPUODEBenchmarks has 27 stars and was last committed 2024-01-04.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-60 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/utkarsh530/GPUODEBenchmarks/tree/main/paper_artifacts/data>
  - <https://github.com/utkarsh530/GPUODEBenchmarks/tree/main/paper_artifacts/data/Tesla_V100>
  - <https://github.com/utkarsh530/GPUODEBenchmarks/tree/main/paper_artifacts/data/RTX_5000>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/CPP/MPGOS_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/CPP/MPGOS_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/Julia/Julia_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/Julia/Julia_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/CPP/MPGOS_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/CPP/MPGOS_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/Julia/Julia_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/Julia/Julia_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/README.md>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/run_benchmark.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/runner_scripts/gpu/run_ode_cpp.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/runner_scripts/gpu/run_ode_julia.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/makefile>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/Lorenz.cu>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/Lorenz_SystemDefinition.cuh>
  - <https://github.com/utkarsh530/GPUODEBenchmarks/tree/main/GPU_ODE_MPGOS/SourceCodes>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/SourceCodes/SingleSystem_PerThread_Interface.cuh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/SourceCodes/SingleSystem_PerThread_ExplicitRungeKutta_Steppers.cuh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/SourceCodes/SingleSystem_PerThread_Solver.cuh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_Julia/bench_lorenz_gpu.jl>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_Julia/Manifest.toml>
  - <https://github.com/utkarsh530/GPUODEBenchmarks>
  - <https://github.com/utkarsh530/GPUODEBenchmarks/commits>
  - <https://github.com/SciML/DiffEqGPU.jl>
  - <https://github.com/SciML/DiffEqGPU.jl/commits>
- **Sources the enricher read:**
  - <https://github.com/SciML/DiffEqGPU.jl>
  - <https://github.com/SciML/DiffEqGPU.jl/commits/master>
  - <https://github.com/SciML/DiffEqGPU.jl/issues?q=is%3Aissue+is%3Aopen+performance+OR+slow+OR+wrong>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/src/DiffEqGPU.jl>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/src/ensemblegpukernel/lowerlevel_solve.jl>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/src/ensemblegpukernel/kernels.jl>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/src/ensemblegpukernel/perform_step/gpu_tsit5_perform_step.jl>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/docs/src/tutorials/lower_level_api.md>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/docs/src/getting_started.md>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/docs/src/manual/ensemblegpukernel.md>
  - <https://raw.githubusercontent.com/SciML/DiffEqGPU.jl/HEAD/docs/src/index.md>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/README.md>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/run_benchmark.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/runner_scripts/gpu/run_ode_cpp.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/runner_scripts/gpu/run_ode_julia.sh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/makefile>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/Lorenz.cu>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_MPGOS/Lorenz_SystemDefinition.cuh>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_Julia/bench_lorenz_gpu.jl>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/GPU_ODE_Julia/Project.toml>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/CPP/MPGOS_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/CPP/MPGOS_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/Julia/Julia_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/Tesla_V100/Julia/Julia_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/CPP/MPGOS_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/CPP/MPGOS_times_adaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/Julia/Julia_times_unadaptive.txt>
  - <https://raw.githubusercontent.com/utkarsh530/GPUODEBenchmarks/main/paper_artifacts/data/RTX_5000/Julia/Julia_times_adaptive.txt>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sciml/diffeqgpu.jl`) · [data/wave14/enrich/raw/github_com_sciml_diffeqgpu_jl.json](../../../data/wave14/enrich/raw/github_com_sciml_diffeqgpu_jl.json) (enrichment confidence 0.75)

</details>
