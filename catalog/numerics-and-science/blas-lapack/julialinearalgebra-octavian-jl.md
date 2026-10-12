# Octavian.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia multithreaded GEMM built on LoopVectorization; median 1816 GFLOPS at 1000^3 vs OpenBLAS 1254 and MKL 1348.

| | |
|---|---|
| **Beats** | OpenBLAS and Intel MKL (also BLIS) |
| **Claimed result** | 1000x1000x1000: Octavian median 1816 GFLOPS (max 1895) vs OpenBLAS median 1254 (max 1385), MKL median 1348 (max 1589), BLIS median 1051 (max 1476). README states 'Octavian has the fastest CPU performance' among the listed Julia packages. |
| **Workload** | Dense matrix multiplication GFLOPS across sizes 10 to 1000 (square), run with BLASBenchmarksCPU.jl; headline row is 1000x1000x1000 with 36 threads. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-10980XE @ 3.00GHz |
| **Compiler and flags** | Julia 1.7.0-DEV.1124 (2021-05-19), LLVM 11.0.1 ORCJIT cascadelake, JULIA_NUM_THREADS=36; benchmark via BLASBenchmarksCPU.jl (public) |
| **Adoption** | 255 stars |
| **Last commit** | 2025-10-21 |
| **Links** | [repository](https://github.com/JuliaLinearAlgebra/Octavian.jl) · [benchmark](https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/README.md) |

## Verdict

One 2021 run of BLASBenchmarksCPU.jl (sizes 10-1000, 2h25m sweep) on an 18-core Intel Core i9-10980XE (Cascade Lake-X, AVX-512) with Julia 1.7.0-DEV.1124, LLVM 11.0.1 and 36 threads. At 1000x1000x1000 the median GFLOPS were Octavian 1816, MKL 1348, OpenBLAS 1254 and BLIS 1051, i.e. 1.35x MKL and 1.45x OpenBLAS (derived from page data). The README does not state the baseline library versions or the element type, and other sizes appear only in a plot.

## Use it when

- Julia code doing dense real matmul on a many-core x86 CPU, where you call matmul! explicitly. At 1000^3 on 18 cores / 36 threads it was 1.45x OpenBLAS and 1.35x MKL by median (derived from page data).
- Element types a binary BLAS cannot take, such as integer matrices or ForwardDiff/HyperDualNumbers duals (through package extensions), while keeping a blocked, vectorized kernel.
- Inside your own Polyester- or LoopVectorization-threaded code, using matmul_serial! (Octavian does not start threads when nested in threaded code).
- Pure-Julia stacks that want to avoid OpenBLAS/MKL threading overhead on small and medium sizes.

## Skip it when

- C++ projects: there is no C/BLAS ABI, so you would have to embed the Julia runtime. Use a native sibling instead.
- Correctness-critical work on current Julia without your own tests. Open issue #193 (October 2024, no maintainer reply) reports wrong results and segfaults for matmul!(c, a, b) with 10x3000 by 3000x10 inputs on Julia 1.10.5/1.11, single-threaded, on Intel and AMD. Issue #191 reports a ReadOnlyMemoryError with 30 threads on a 271x24 product.
- Code that also uses Base.Threads @spawn/@threads. The docs warn that Octavian's tasks interfere with them and make execution much slower.
- More than 64 threads (#153), dual-socket machines (#151), or large unbalanced problems (#104; #152 reports the wrong strategy for large matrices on Zen3). All four issues are open.
- Long-term dependency risk. Commits in the last year are CI and dependency bumps only, LoopVectorization's upkeep depends on the SciML Small Grants program, and 32-bit Julia support was dropped.

## How it is fast

It runs a Goto/BLIS-style blocked GEMM. Block sizes Mc/Kc/Nc are solved in closed form from L1/L2 cache sizes reported by CPUSummary (hwloc), with weights tuned per architecture: AVX-512, Zen1-3, a generic fallback and Apple aarch64. Depending on size and alignment it packs nothing, only A, or both A and B into page-aligned buffers preallocated at load time. LoopVectorization's @turbo generates the register-blocked micro-kernels. Threads are dispatched through PolyesterWeave/ThreadingUtilities spinning workers rather than Base.Threads tasks, which keeps per-call threading overhead low at small and mid sizes.

## Compared with alternatives

Choose Octavian over PureBLAS.jl, the other pure-Julia BLAS in the catalog, for multithreaded GEMM and generic element types. PureBLAS.jl's comparisons against OpenBLAS/AOCL are single-threaded. For C++ users, Eigen or a native BLIS-style sibling is the practical choice, since Octavian is not callable from C++.

## Integration

| | |
|---|---|
| **Form** | module (registered Julia package, v0.3.29) |
| **Dependencies** | LoopVectorization, VectorizationBase, PolyesterWeave, ThreadingUtilities, CPUSummary, StaticArrayInterface, Static, ManualMemory, IfElse, PrecompileTools; ForwardDiff and HyperDualNumbers as weak dependencies |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat), 64-bit only |
| **Platforms** | 64-bit x86-64 (tuned constants for AVX-512, Zen1-3, generic) and aarch64 (tuned constants for Apple) |
| **Thread safety** | Not documented, apart from two notes: it will not use threads when nested in other threaded code, and its tasks interfere with Base.Threads tasks. Internally a global spin lock guards a shared B-packing buffer, and the A buffers are indexed by Threads.threadid(). |
| **Drop-in for the baseline** | partial: matmul!(C, A, B, alpha, beta) has the same argument order as LinearAlgebra.mul!, but it is a separate function that does not replace BLAS calls and skips mul!'s dimension checks (#109) |

## Gotchas

- matmul! does not check dimensions (#109, open). Mismatched sizes proceed silently where LinearAlgebra.mul! throws DimensionMismatch, and LoopVectorization's @turbo kernels do no bounds checking.
- The B-buffer lock is taken without try/finally. If a matmul throws, later calls can spin until you call Octavian.reset_bcache_lock!() (per its docstring).
- The thread count is min(Threads.nthreads(), physical cores), optionally lowered by OCTAVIAN_NUM_TASKS. It is read in __init__ along with the size of the preallocated pack buffers, so start Julia with -t before loading.
- Block sizes depend on correct cache sizes. The README asks for CPUSummary.use_hwloc(true), the default, for accurate hardware information.

## Known shortcomings

- Single 2021 36-thread run; the last year's commits are CI bumps only; depends on LoopVectorization (grant-funded upkeep); Julia.
- Correctness bug: open issue #193 (Oct 2024, no maintainer reply) reports wrong results and segfaults from matmul! on 10x3000 by 3000x10 inputs (Julia 1.10/1.11, single thread); also open #191 (ReadOnlyMemoryError with 30 threads) and #109 (no dimension check); the B-buffer spin lock has no try/finally, so later calls can hang after an error.

## Caveats and trade-offs

The headline figure is from one 2021 run with a Julia 1.7 development build on an 18-core/36-thread i9-10980XE (Cascade Lake-X) using 36 threads. Only the 1000x1000x1000 row is printed as numbers; other sizes appear only in an SVG plot. MKL, OpenBLAS and BLIS versions are not stated, and newer versions of them, or of Julia and LoopVectorization, may change the ranking. The result is multi-threaded; single-thread results and other CPUs are not shown. Commits in the last year are CI and dependency bumps only (latest 2025-10-21). Octavian depends on LoopVectorization.jl, whose maintenance now relies on the SciML Small Grants program. It is pure Julia, not a C++-callable library. The README says the full size sweep took 2h25m.

Pure Julia, built on LoopVectorization.jl; BLAS-like gemm-style API (matmul) rather than a full BLAS/LAPACK ABI, so it is not directly callable from C++. Task scheduling can interfere with Base.Threads tasks (README docs note).

## Maintenance

MIT, 255 stars and registered, but effectively in maintenance mode: the last commit (2025-10-21) was a CI bump, and correctness issue #193 has gone unanswered since October 2024.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public: the README shows the BLASBenchmarksCPU.jl call runbench(sizes = logspace(10, 1_000, 200)). It states Julia 1.7.0-DEV.1124 (LLVM 11.0.1 ORCJIT, cascadelake target, default JIT optimization), JULIA_NUM_THREADS=36 and the CPU (Intel Core i9-10980XE). That meets A, even though the versions of the baseline libraries are not given.
- **Verifier notes:** The README numbers match the record exactly: at 1000^3, median GFLOPS were 1816 for Octavian, 1254 for OpenBLAS, 1348 for MKL and 1051 for BLIS. The page confirms MIT, 255 stars and the last commit on 2025-10-21; that commit was a dependabot CI bump.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl>
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl/commits/master>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/Octavian.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/matmul.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/block_sizes.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/macrokernels.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/memory_buffer.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/global_constants.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/src/init.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/docs/src/index.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/docs/src/getting-started.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/Octavian.jl/HEAD/docs/make.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl/issues>
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl/issues/193>
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl/issues/191>
  - <https://github.com/JuliaLinearAlgebra/Octavian.jl/issues/109>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/julialinearalgebra/octavian.jl`) · [data/wave8/enrich/raw/github_com_julialinearalgebra_octavian_jl.json](../../../data/wave8/enrich/raw/github_com_julialinearalgebra_octavian_jl.json) (enrichment confidence 0.8)

</details>
