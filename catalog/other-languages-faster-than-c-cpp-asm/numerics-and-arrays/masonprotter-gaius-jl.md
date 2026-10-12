# Gaius.jl (Julia multi-threaded divide-and-conquer BLAS-like matmul)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🔴 abandoned

> Pure-Julia recursive multithreaded matmul that beat 6-thread OpenBLAS on small and medium matrices in a 2020 run.

| | |
|---|---|
| **Beats** | OpenBLAS gemm (C and assembly) with 6 threads (BLAS.set_num_threads(6)); for integer matrices Julia's generic matmul, since OpenBLAS has no integer matmul |
| **Claimed result** | README: 104x104 Float64 mul!: LinearAlgebra/OpenBLAS 68.529 us vs Gaius 31.220 us (about 2.2x faster, derived from page data); A\*B 68.949 us vs Gaius.mul 32.950 us (about 2.1x, derived); 150x150 Complex{Float64}: Gaius on StructArrays 515.587 us vs OpenBLAS 546.481 us (about 1.06x, derived). Plots: 'Gaius outperforms OpenBLAS over a large range of matrix sizes, but does begin to appreciably fall behind around 800 x 800 matrices for Float64 and 650 x 650 matrices for Float32'; the plots also show OpenBLAS ahead at the smallest size (about 2x2). Integer plots compare with Julia's generic matmul, not C. |
| **Workload** | Square matrix multiplication for Float64, Float32 and Complex{Float64} (struct-of-arrays) across a range of sizes, shown as log-log plots. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 2600 six-core (Linux) |
| **Compiler and flags** | Julia 1.4.0-rc2.0 (LLVM 8.0.1, znver1), JULIA_NUM_THREADS=6; OpenBLAS version not stated; built on LoopVectorization.jl. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Divide-and-conquer task parallelism on Julia's depth-first task runtime with LoopVectorization.jl SIMD kernels (README). |
| **Adoption** | 119 stars |
| **Last commit** | 2023-05-05 |
| **Links** | [repository](https://github.com/MasonProtter/Gaius.jl) · [benchmark](https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/README.md) |

## Verdict

Author-run in 2020 on a 6-core Ryzen 5 2600 (Zen+, AVX2) with Julia 1.4.0-rc2 (LLVM 8) and 6 threads, against OpenBLAS (version unstated) set to 6 threads. 104x104 Float64 mul! took 31.2 us vs 68.5 us (about 2.2x, derived), 150x150 split-complex about 1.06x, and the log-log plots show OpenBLAS ahead at about 2x2 and beyond 800 (Float64) / 650 (Float32). All of this was measured with the pre-2021 blocked_mul! code, and no benchmark script is in the repo.

## Use it when

- Square-ish Float64 or Float32 products in roughly the 10-650 range (Float32) or 10-800 range (Float64), where the README plots show it ahead of 6-thread OpenBLAS
- Integer matrices (Int64, Int32, Int16): OpenBLAS has no integer GEMM and Julia's generic fallback is single-threaded, which is what the README's integer plots compare against
- Matmuls issued from inside already-parallel Julia code, where Gaius's task-based threading composes with the caller instead of oversubscribing cores like a separately threaded BLAS
- Complex products whose data already lives in StructArrays (split real and imaginary parts)
- Reading or teaching a compact recursive GEMM (about 1,200 lines of Julia)

## Skip it when

- Large matrices: the README plots show OpenBLAS ahead beyond about 800 (Float64) and 650 (Float32); in chriselrod's April 2020 multithreaded run (issue #11, AVX-512 machine) Gaius blocked_mul! took 5.516 s at 9737x9737 against 0.891 s for OpenBLAS 0.3.9 and 0.889 s for MKL
- Production code: the README says it is not stable or well tested and not actively maintained; Octavian.jl is the maintained, faster pure-Julia BLAS
- Anything beyond C = A\*B: no alpha/beta scaling, no gemv-style BLAS API, no trsm, syrk or LAPACK
- Interleaved Matrix{ComplexF64} or other element types (Rational, Dual, Float16): Gaius.mul! only accepts the five real types and StructArray complex
- Tiny matrices: the plots show OpenBLAS ahead around 2x2, and each threaded call allocates (80 allocations, about 10 KiB at 104x104 in the README)

## How it is fast

Recursive divide-and-conquer GEMM: C, A and B are split into 2x2 sub-blocks (k split in half), three quadrants are handed to Threads.@spawn tasks and the fourth runs on the caller, recursing until a block falls under a block size (64, or 96 with AVX-512F; 32 for small problems) or a per-task work budget of m\*n\*k/(8\*nthreads). Leaf blocks run a plain triple loop vectorised by LoopVectorization.jl's @avx, and Julia's depth-first task scheduler lets calls nest inside other threaded code. Complex products run as four real GEMMs on the split arrays; there is no packing of A and B as in OpenBLAS's GotoBLAS-style kernels.

## Compared with alternatives

No sibling in this category is a dense GEMM (TriangularSolve.jl does triangular solves on the same LoopVectorization stack, FFTA.jl does FFTs); for matmul, the catalog's Octavian.jl (wave 8) is the maintained and faster pure-Julia choice. Pick Gaius only for its simple recursive code, or for threaded integer matmul nested inside parallel Julia code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LoopVectorization 0.12.10+, VectorizationBase 0.20-0.21, StructArrays 0.5-0.6, UnsafeArrays 1.0.1, plus the LinearAlgebra and Random stdlibs |
| **Minimum toolchain** | Julia 1.5 per Project.toml (CI matrix: Julia 1.6, 1.8 and latest 1.x); the README benchmarks used Julia 1.4.0-rc2 |
| **Platforms** | Any CPU LoopVectorization supports; CI runs Linux, Windows and macOS on x64 and 32-bit x86; block size 96 with AVX-512F, else 64 |
| **Thread safety** | README: spawns tasks on Julia's depth-first scheduler so calls can be nested inside multithreaded programs; the Adjoint StructArray complex methods temporarily negate A's imaginary array in place, so A must not be read concurrently during such a call |
| **Drop-in for the baseline** | partial — Gaius.mul!(C, A, B) mirrors the 3-argument LinearAlgebra.mul! call for supported element types, but it is a separate unexported function (call it qualified), has no alpha/beta form and covers matmul only |

## Gotchas

- The README's first REPL example now calls an unqualified mul! on both the 'from LinearAlgebra' and the 'from Gaius' line; commit 2892760 shows the original line was blocked_mul!, renamed in a January 2021 README edit. Gaius does not export mul!, so as written both lines call LinearAlgebra.mul!. The published timings and plots come from the 2020 blocked_mul! code on Julia 1.4.0-rc2, before the January 2021 threading API change (#57, #63) and tkf's November 2021 rebalancing (#83, #88). The current release needs Julia 1.5+, so the numbers cannot be reproduced on it as published.
- Covector path: the CoVecTypes methods of _mul! and _mul_add! compute k = size(A, 1), which is 1 for an adjoint or transposed vector, so v'\*A never enters the blocked or threaded branch and always runs one single-threaded kernel; the unreachable branch passes Val(factor) to block_covec_mat_mul!/block_covec_vec_mul!, which have no such method. Issue #79 'Covector-matrix multiplication is broken' (bug) has been open since March 2021.
- Adjoint and transpose StructArray complex methods mutate inputs as an 'ugly hack' (source comment): A.parent.im is negated before the four real GEMMs and restored afterwards, and C.parent.im is negated at the end; an exception mid-call leaves A negated.
- sizecheck=false skips all dimension checks (README: 'bad, segfaulty things can happen'); zero-size dimensions are not special-cased before the @avx kernels, and LoopVectorization's README lists iterating an empty loop as undefined behaviour.

## Known shortcomings

- README numbers only (104x104 Float64: OpenBLAS 68.529 us vs Gaius 31.220 us, about 2.2x) with wins only at small and medium sizes; no bench script, OpenBLAS version unstated; last commit 2023-05-05.
- The numbers are 2020 blocked_mul! code on Julia 1.4.0-rc2 (commit 2892760); a later README edit made both REPL lines unqualified mul!, which Gaius does not export, so as written both call LinearAlgebra. The code has since been reworked (#57, #63, #83, #88). The covector _mul! takes k = size(A,1) = 1, so v'\*A is never blocked or threaded (#79 open); the complex adjoint path negates the input A in place. chriselrod's issue #11: at n=9737 Gaius 5.516 s vs OpenBLAS 0.891 s.

## Caveats and trade-offs

Author-run on Julia 1.4.0-rc2.0 (2020, LLVM 8.0.1, Ryzen 5 2600 Zen+, no AVX-512); the repo has no benchmark script, the OpenBLAS version is unstated, and the BLAS thread count for the REPL timings is not shown (the plots used BLAS.set_num_threads(6)). The lead is a small-to-medium size win (plots: OpenBLAS ahead at about 2x2 and beyond about 800 for Float64, 650 for Float32; Float32 is roughly level near 60-100), plausibly helped by OpenBLAS's threading overhead at small sizes (not measured). Different algorithm (recursive divide-and-conquer vs OpenBLAS's packed GEMM). Integer results compare with Julia's single-threaded generic matmul, not with C. The README calls Gaius unstable and unmaintained and points to Octavian.jl (already listed in wave 8) as the more performant pure-Julia BLAS; built on LoopVectorization.jl (also listed in wave 8). [retier] The numbers are 2020 blocked_mul! code on Julia 1.4.0-rc2 (commit 2892760); a later README edit made both REPL lines unqualified mul!, which Gaius does not export, so as written both call LinearAlgebra. The code has since been reworked (#57, #63, #83, #88); the covector _mul! takes k = 1, so v'\*A is never blocked or threaded (#79 open); the complex adjoint path negates the input A in place. Issue #11: at n=9737 Gaius 5.516 s vs OpenBLAS 0.891 s.

Matmul only (README: other BLAS routines not implemented); README says it is 'not stable or well tested' and 'not actively maintained' and points to Octavian.jl (already catalogued) and Tullio.jl as successors; Julia-only.

## Maintenance

Abandoned: the last commit (2023-05-05, v0.6.8) only fixed loading under Static.StaticInt, and the README says it is not maintained or well tested; it is MIT, registered and small enough to read, but use Octavian.jl when speed matters.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README: BenchmarkTools timings (104x104 Float64, 150x150 Complex) and log-log plots (assets/F64_mul.png, F32_mul.png, C64_mul.png) against OpenBLAS with 6 threads, with Julia 1.4.0-rc2.0 and the Ryzen 5 2600 named; no benchmark script in the repo and the OpenBLAS version is unstated, so not A.
- **Verifier notes:** Record accurate apart from the claim that no numbers are printed: the README has REPL timings (68.529 vs 31.220 us at 104x104 Float64), now in claimed_speedup. Metadata checked (MIT, 119 stars, last commit 2023-05-05, abandoned). Not a wrapper of OpenBLAS, so not a duplicate; related wave-8 entries are Octavian.jl and LoopVectorization.jl.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/README.md>
  - <https://github.com/MasonProtter/Gaius.jl>
  - <https://github.com/MasonProtter/Gaius.jl/commits>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/assets/F64_mul.png>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/assets/F32_mul.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/Gaius.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/global_constants.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/types.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/block_operations.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/check_compatible_sizes.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/choose_block_size.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/kernels.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/matmul.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/public_mul.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/src/init.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/runtests.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/test_suite_preamble.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/public_mul_main.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/matmul_main.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/public_mul_coverage.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/test/_public_mul.jl>
  - <https://raw.githubusercontent.com/MasonProtter/Gaius.jl/HEAD/.github/workflows/ci.yml>
  - <https://github.com/MasonProtter/Gaius.jl>
  - <https://github.com/MasonProtter/Gaius.jl/commits/master>
  - <https://github.com/MasonProtter/Gaius.jl/commits/master/README.md>
  - <https://github.com/MasonProtter/Gaius.jl/commit/2892760>
  - <https://github.com/MasonProtter/Gaius.jl/issues?q=is%3Aissue>
  - <https://github.com/MasonProtter/Gaius.jl/issues/79>
  - <https://github.com/MasonProtter/Gaius.jl/issues/11>
  - <https://github.com/MasonProtter/Gaius.jl/issues/85>
  - <https://github.com/MasonProtter/Gaius.jl/issues/91>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/HEAD/Project.toml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/masonprotter/gaius.jl`) · [data/wave14/enrich/raw/github_com_masonprotter_gaius_jl.json](../../../data/wave14/enrich/raw/github_com_masonprotter_gaius_jl.json) (enrichment confidence 0.75)

</details>
