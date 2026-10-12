# LoopVectorization.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia @turbo macro that SIMD-vectorizes plain loops; its triple-loop gemm edges single-threaded MKL on small matrices.

| | |
|---|---|
| **Beats** | Intel MKL dgemm (single-threaded, via Julia LinearAlgebra.mul!) |
| **Claimed result** | README example: @turbo triple-loop gemm minimum 111.722 microseconds (110.5 GFLOPS) vs MKL mul! (BLAS.set_num_threads(1), vendor :mkl) minimum 117.221 microseconds (105.3 GFLOPS) at M=191, K=189, N=171, about 5% faster (derived from page data); the same loop with only @inbounds @fastmath took 4.891 ms (about 44x slower than @turbo, derived from page data). The project's own docs (docs/src/examples/matrix_multiplication.md) say that for C = A\*B LoopVectorization 'falls behind MKL's gemm beyond 70x70 or so', and for A'\*B it is 'well behind MKL and OpenBLAS' because it does not pack. |
| **Workload** | Float64 matrix multiply C = A\*B with M=191, K=189, N=171, written as a plain triple loop under the @turbo macro, single thread, BenchmarkTools minimum time. |
| **Metric** | latency |
| **Compiler and flags** | Julia (version not stated) with the @turbo macro; MKL selected with BLAS.set_num_threads(1) and BLAS.vendor() == :mkl. |
| **Adoption** | 790 stars |
| **Last commit** | 2026-05-31 |
| **Links** | [repository](https://github.com/JuliaSIMD/LoopVectorization.jl) · [benchmark](https://github.com/JuliaSIMD/LoopVectorization.jl) |

## Verdict

README example on an unnamed AVX-512 CPU, Julia version not stated: a @turbo triple-loop Float64 gemm at M=191, K=189, N=171 has a minimum of 111.7 us (110.5 GFLOPS) against 117.2 us (105.3 GFLOPS) for single-threaded MKL mul!, about 5% faster, and 44x faster than the same loop under @inbounds @fastmath. The project's own docs say the advantage disappears beyond roughly 70x70 for square C = A\*B, so this is a narrow small-matrix win.

## Use it when

- Julia code with small dense Float64/Float32/Int matrix kernels (roughly up to 70x70 for C = A\*B per the docs; the README's 191x189x171 example is about 5% ahead of 1-thread MKL) where BLAS call overhead dominates
- Custom fused loop kernels that BLAS cannot express, e.g. gemm plus an elementwise epilogue, tropical/max-plus products, or reductions with special functions (sincos_turbo 614 ns vs 3.9 us for the plain loop in the docs' 512-element example)
- Loops that LLVM vectorizes poorly because of remainders (README dot product: 12.2 ns vs 36.5 ns at length 255)
- As the kernel generator under a larger library: Octavian.jl, RecursiveFactorization.jl, Tullio.jl and TropicalGEMM.jl build on it

## Skip it when

- Matrix multiply beyond about 70x70: the project's own docs say it falls behind MKL gemm there, and for A'\*B it is well behind MKL and OpenBLAS because it does not pack
- From C++: it is a Julia macro, so there is nothing to link; using it means embedding Julia
- Loops that depend on execution order (cumsum, loop-carried dependencies), triangular/ragged iteration spaces, multiple loops at the same nest level, or arrays of structs/Complex without StructArrays
- Code that must be bounds-checked or bit-reproducible: @turbo does no bounds checking, reorders operations and swaps in faster special functions (about 3 ULP per the docs)
- Projects needing a well-staffed dependency: 116 open issues including wrong-result reports (#542, #539, #512, #507) and a memory-corruption report (#510); maintenance runs through SciML Small Grants

## How it is fast

The macro builds a LoopSet model of the loop nest and runs a cost model (determinestrategy.jl, instruction latency/reciprocal-throughput/register-pressure tables mostly from Agner Fog's Skylake-X numbers) over loop orders, choosing which loop to vectorize and which one or two loops to unroll; this yields register-blocked micro-kernels with multiple independent accumulators. It handles loop remainders with masked SIMD instead of LLVM's slow scalar tails, uses FMA, and substitutes SIMD-able special functions. There is no cache blocking, packing or memory modelling, which is why it wins only at small sizes.

## Compared with alternatives

Pick it over Octavian.jl when you need a custom or fused small kernel rather than a full gemm (Octavian builds on LoopVectorization and is the one that beats MKL at 1000x1000); in C or C++, BLASFEO or Eigen are the small-matrix equivalents, and LoopVectorization is only relevant if the code is already in Julia.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages: VectorizationBase, SLEEFPirates, ArrayInterface, StaticArrayInterface, LayoutPointers, HostCPUFeatures, CPUSummary, PolyesterWeave, ThreadingUtilities, OffsetArrays, SpecialFunctions, ForwardDiff/ChainRulesCore and others (Project.toml); optional extensions for ForwardDiff, NNlib, SpecialFunctions |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat julia = "1.10"; the README's 'Julia 1.1 and later' is out of date); version 0.12.174 |
| **Platforms** | CPUs supported by Julia/LLVM (x86-64, aarch64); performance depends on SIMD width, and the README benchmarks used an AVX-512 machine (Float64 vector width 8, CPU not named). Some tests are reported broken on macOS ARM (#564). |
| **Thread safety** | Single-threaded by default; @tturbo or @turbo thread=N uses Polyester-style threads up to min(N, Threads.nthreads(), physical cores). Thread safety of user loops not otherwise documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- No bounds checking and iterating an empty collection is undefined behaviour; misuse can segfault or corrupt memory (README warning). Issue #510 reports intermittent heap corruption from a @turbo A'\*A loop on Julia 1.10-beta.
- Broadcasting an Array whose size(A,1) == 1 is not supported unless known at compile time and will probably crash Julia (getting_started.md); use LowDimArray.
- Performance is much higher when matrix dimensions are multiples of the SIMD width (docs); padding columns (PaddedMatrices.jl) helps.
- Keyword arguments inside @turbo calls fail with a TypeError; wrap the call in a functor. Issue #540 reports the same TypeError for plain broadcasts on Julia 1.12 nightly (Dec 2024); a later commit fixes 1.12 precompile warnings, but whether #540 is fully resolved is not documented.

## Known shortcomings

- Julia, not callable from C++. Its own docs say it falls behind MKL gemm beyond about 70x70, so the win holds only for small matrices. CPU not named.
- 116 open issues, several reporting wrong results (#542, #539, #512, #507); #510 reports intermittent heap corruption from a @turbo A'\*A loop. Project.toml needs Julia 1.10 while the README says 1.1.

## Caveats and trade-offs

Single-shape, single-thread micro-benchmark with a margin of about 5%; the CPU is not named (README: 'the CPU I'm running these benchmarks on', Float64 SIMD width 8, which implies AVX-512) and the Julia version is not stated. The project's own documentation (docs/src/examples/matrix_multiplication.md, read from the repo source since JuliaSIMD.github.io is egress-blocked) says LoopVectorization falls behind MKL's gemm beyond about 70x70 for C = A\*B and is well behind MKL and OpenBLAS for A'\*B (no packing, no memory modelling), so the README win does not generalize to larger matrices; its main measured advantage is over compiled loops (Clang, gfortran, icc, ifort, Eigen). The benchmark harness in benchmark/ (loadsharedlibs.jl, looptests.c/.f90, looptestseigen.cpp) lists flags such as clang -Ofast -march=native and g++ -O3 -march=native for Eigen. @turbo performs no bounds checking and may reorder operations; misuse gives wrong results. The package is in maintenance mode under the SciML Small Grants programme. Julia-only, so it fits the 'then any' language filter rather than C++. Larger-size Julia work with this approach is Octavian.jl (already catalogued).

Julia only, not callable from C++ without embedding Julia. It is a loop-vectorizing macro, not a BLAS: @turbo reorders loops, does no bounds checking (misuse can segfault), supports only simple loop nests, and does no cache blocking or packing, so the README says parallelism and cache efficiency are left to the user and the gemm kernel suits small to medium matrices.

## Maintenance

Active but in maintenance mode (last commit 2026-05-31, version 0.12.174, Julia 1.10+ with CI on LTS/latest/pre/nightly), funded through SciML Small Grants with no original-author development; MIT-licensed and usable only from Julia.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README example: @turbo gemm 111.722 us vs single-threaded MKL mul! 117.221 us at 191x189x171, with the benchmark code inline but no CPU model or Julia version; the repo's benchmark/ harness (loadsharedlibs.jl) states compilers and flags but no CPU was named in anything opened, so it falls short of A.
- **Verifier notes:** README numbers match exactly; license MIT (LICENSE: Copyright (c) 2019 Chris Elrod, Eli Lilly & Co), 790 stars, 73 forks, last commit 2026-05-31, not archived. Worth recording: own docs say it loses to MKL gemm beyond about 70x70, so the win is narrow (small matrices only).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/JuliaSIMD/LoopVectorization.jl>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/commits/main>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/LICENSE>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/tree/main/docs/src/examples>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/examples/matrix_multiplication.md>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/tree/main/benchmark>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/benchmark/loadsharedlibs.jl>
- **Sources the enricher read:**
  - <https://github.com/JuliaSIMD/LoopVectorization.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/index.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/getting_started.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/examples/matrix_multiplication.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/examples/multithreading.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/devdocs/overview.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/devdocs/evaluating_loops.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/devdocs/lowering.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/performance_accuracy.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/docs/src/future_work.md>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/issues>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/issues/540>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/issues/510>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/juliasimd/loopvectorization.jl`) · [data/wave8/enrich/raw/github_com_juliasimd_loopvectorization_jl.json](../../../data/wave8/enrich/raw/github_com_juliasimd_loopvectorization_jl.json) (enrichment confidence 0.8)

</details>
