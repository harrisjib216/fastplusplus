# RecursiveFactorization.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia recursive LU (Toledo's algorithm) that beats OpenBLAS and often MKL getrf on dense matrices up to about 500x500.

| | |
|---|---|
| **Beats** | OpenBLAS (Julia LUFactorization default) and Intel MKL (MKLLUFactorization) |
| **Claimed result** | README: 'For small to medium sized matrices, it is beneficial to use RecursiveFactorization over OpenBLAS'. The SciMLBenchmarks page has only a plot (N = 4..500). Read off it (approximate, derived from page data), RFLUFactorization reaches about 33 GFLOPs at N=500, against about 18 for OpenBLAS LUFactorization and about 23 for MKLLUFactorization. It is roughly 2x OpenBLAS around N=100-250 (about 19-21 vs 10-11 near N=200-240). MKL's noisy curve spikes above RF at a few sizes (about 34 vs about 29 near N=440). |
| **Workload** | LU factorization of dense NxN Float64 matrices, N = 4..500 in steps of 8, GFLOPs, SciMLBenchmarks LinearSolve LU benchmark. |
| **Metric** | throughput |
| **Hardware** | 128 x AMD EPYC 7502 32-Core Processor (SciML CI runner) |
| **Compiler and flags** | Julia 1.12.7 official release (LLVM 18.1.7 ORCJIT, znver2), default JIT optimization, JULIA_NUM_THREADS=auto (128 threads on 128 virtual cores). LinearSolve v5.5.0, RecursiveFactorization v0.2.26, OpenBLAS_jll 0.3.29, MKL_jll 2025.2.0. BenchmarkTools @belapsed with 0.5 s per sample. BLAS.set_num_threads(min(VectorizationBase.num_cores(), Threads.nthreads())); the page does not print the resulting count. |
| **Adoption** | 83 stars; backs RFLUFactorization in Julia's LinearSolve.jl |
| **Last commit** | 2026-08-09 |
| **Links** | [repository](https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl) · [benchmark](https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/LinearSolve/LUFactorization.md) |

## Verdict

On SciML's CI runner (128-thread AMD EPYC 7502, Julia 1.12.7, RecursiveFactorization v0.2.26 via LinearSolve 5.5.0, OpenBLAS_jll 0.3.29, MKL_jll 2025.2.0, BLAS threads set to min(cores, nthreads)), RFLUFactorization reached roughly 33 GFLOPS at N=500 against about 18 for OpenBLAS and 23 for MKL, and about 2x OpenBLAS near N=200-240; values are read off a plot, and MKL beats it at a few noisy sizes.

## Use it when

- Repeated dense LU solves of square Float64/Float32 matrices from roughly 10x10 to 500x500 in Julia (ODE/DAE Jacobians, Newton steps, small FEM blocks).
- On x86-64 with OpenBLAS as Julia's default BLAS, where SciMLBenchmarks shows about 2x OpenBLAS around N=100-250 on an EPYC 7502.
- Inside LinearSolve.jl: load the package and the default algorithm already routes small square systems to RFLUFactorization.
- When you want pure-Julia code that also handles ComplexF32/ComplexF64 and non-BLAS element types through the same API (tested in runtests.jl, via the generic recursion path).

## Skip it when

- Large matrices (well above N=500): the only benchmark stops at 500 and LinearSolve itself hands larger sizes back to BLAS/MKL.
- From C or C++: it is a Julia package with no C ABI; use a LAPACK getrf (or ReLAPACK) instead.
- On Apple Silicon, where LinearSolve's own default prefers Apple Accelerate LU over RFLU.
- When you need other factorizations: only LU is implemented (Cholesky and QR are not; issue #74 asks about QR).
- Inside an outer Threads.@threads loop with thread=Val(true): issue #48 reports Julia exiting silently on Windows 10; pass Val(false) for the thread argument.

## How it is fast

Sivan Toledo's recursive left-looking LU (SIAM J. Matrix Anal. Appl., DOI 10.1137/S0895479896297744) splits the column panel in two, factors the left half recursively, applies the pivots, does a unit-lower triangular solve (TriangularSolve.jl) and a Schur-complement update, then recurses on the right half; this keeps working sets cache-sized without hand-picked block sizes. The Schur update and the base-case kernels are LoopVectorization @turbo loops that JIT-compile SIMD micro-kernels for the host CPU, so there is no BLAS call and none of the threading or dispatch overhead that dominates OpenBLAS at small N. Threading (Polyester @batch / @tturbo) only switches on when the matrix exceeds about 92% of L2 cache.

## Compared with alternatives

Pick it over Octavian.jl or PureBLAS.jl when your bottleneck is solving small dense systems (LU) rather than GEMM, and over ReLAPACK or BLASFEO when you are already in Julia and want a recursive getrf without linking a C/Fortran LAPACK; from C++ those two are the relevant choices.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LinearAlgebra, LoopVectorization, Polyester, PrecompileTools, SparseBandedMatrices, StrideArraysCore, TriangularSolve, VectorizedRNG |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat) |
| **Platforms** | any platform LoopVectorization supports; recursion threshold is tuned for AVX2 vs AVX-512 (40 vs 48 columns) |
| **Thread safety** | not documented; separate matrices can be factored from different tasks, but nested threading with thread=Val(true) has a crash report on Windows (issue #48) |
| **Drop-in for the baseline** | partial — returns a LinearAlgebra.LU usable wherever LinearAlgebra.lu! output is, but you call RecursiveFactorization.lu! explicitly (or select RFLUFactorization in LinearSolve); it does not replace the BLAS/LAPACK library |

## Gotchas

- Direct calls default to single-threaded (thread = Val(false)) while LinearSolve's RFLUFactorization defaults to thread = Val(true); timings differ accordingly, and threading only engages above about 0.92x the L2 cache size.
- Fast path needs a StridedArray of Float32/Float64; other array types or element types fall back to a generic (slower) recursion, and pivoted matrices with min(m,n) &lt; 10 go straight to LinearAlgebra.generic_lufact!.
- pivot = Val(false) (and the butterfly path) trades stability for speed; LinearSolve's docs say the butterfly variant is less robust for matrices that need pivoting.
- A commit of 2026-08-08 ('Initialize a user-supplied ipiv in pivot-free lu!') fixed no-pivot mode returning a user-supplied ipiv full of uninitialized memory; the benchmarked v0.2.26 may predate it (HEAD Project.toml is v0.2.30; which release first carries the fix is not documented). First calls also pay JIT/precompile latency.

## Known shortcomings

- Not independent (SciML runs both sides of SciMLBenchmarks); many-thread BLAS at N&lt;=500 inflates the gap; Julia.
- Issue #48: nested threading with thread=Val(true) makes Julia exit silently on Windows; a 2026-08-08 fix (pivot-free lu! returned the user's ipiv uninitialized) may postdate the benchmarked v0.2.26; LinearSolve picks it only for small N (&lt;=100, &lt;=500 on OpenBLAS, &lt;=200 on MKL).

## Caveats and trade-offs

The numbers exist only as a plot, so the values above are approximate. The suite is run by the SciML organization, whose maintainers also maintain this package (recent commits come from SciML), so it is not independent. BLAS threads were set to min(num_cores, nthreads) on a 128-virtual-core EPYC runner for matrices of at most 500x500. Threading overhead in OpenBLAS and MKL may therefore inflate the gap, and the page says neither how many BLAS threads resulted nor how many threads RFLU used. MKL needed the LoadMKL_JLL preference to run on this AMD EPYC and may not use its fastest code paths there. Only N &lt;= 500 is measured, matching the README's own 'small to medium' claim. The README's embedded plot is an older image. I did not open docs.sciml.ai; I used the raw markdown and figure from SciMLBenchmarksOutput.

Pure Julia implementation of Toledo's recursive left-looking LU; only Base Array Float32/Float64; best for roughly N &lt; 500; LU only; no C ABI.

## Maintenance

Actively maintained by the SciML/JuliaLinearAlgebra maintainers (v0.2.30, last commit 2026-08-09) and MIT-licensed; usable from Julia only, and it depends on LoopVectorization, which is kept alive through SciML small grants.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The full benchmark code is printed on the page and lives in SciMLBenchmarks.jl (benchmarks/LinearSolve/LUFactorization.jmd). The page states the compiler (official Julia 1.12.7, LLVM 18.1.7, znver2, default JIT optimization), the complete package manifest (RecursiveFactorization v0.2.26, OpenBLAS_jll 0.3.29, MKL_jll 2025.2.0) and the CPU (AMD EPYC 7502), which meets A. The numbers are plot readings only.
- **Verifier notes:** The raw benchmark markdown and figure LUFactorization_1_1.png were opened, and the record's plot readings are consistent with them. The page confirms MIT (LICENSE.md), 83 stars and the last commit on 2026-08-09. I left the record's '128 threads' claim out: the page does not show the value that num_cores() returned.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl>
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl/commits/master>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/LinearSolve/LUFactorization.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/LinearSolve/figures/LUFactorization_1_1.png>
- **Sources the enricher read:**
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl>
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl/issues>
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl/issues/82>
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl/issues/48>
  - <https://github.com/JuliaLinearAlgebra/RecursiveFactorization.jl/commits/master>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/src/RecursiveFactorization.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/src/lu.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/src/butterflylu.jl>
  - <https://raw.githubusercontent.com/JuliaLinearAlgebra/RecursiveFactorization.jl/HEAD/test/runtests.jl>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/LinearSolve/LUFactorization.md>
  - <https://raw.githubusercontent.com/SciML/LinearSolve.jl/HEAD/src/extension_algs.jl>
  - <https://raw.githubusercontent.com/SciML/LinearSolve.jl/HEAD/src/default.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/julialinearalgebra/recursivefactorization.jl`) · [data/wave8/enrich/raw/github_com_julialinearalgebra_recursivefactorization_jl.json](../../../data/wave8/enrich/raw/github_com_julialinearalgebra_recursivefactorization_jl.json) (enrichment confidence 0.8)

</details>
