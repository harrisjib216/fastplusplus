# TriangularSolve.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia SIMD triangular solves (trsm-style) that beat MKL by 9-11% single-threaded at N=100 in a 2021 README run.

| | |
|---|---|
| **Beats** | Intel MKL (libmkl_rt.so loaded through MKL.jl; MKL version not stated) triangular solve called through Julia LinearAlgebra: rdiv!(copyto!(C, A), UpperTriangular(B)) and the 3-argument ldiv!(C, LowerTriangular(B), A) on the Intel run. The M1 run prints no BLAS configuration or versioninfo, so its BLAS is not named. |
| **Claimed result** | README medians (BenchmarkTools, 10000 samples, N=100 random dense matrices, 100 right-hand sides). i7-1165G7 single thread (BLAS.set_num_threads(1); TriangularSolve with Val(false)): rdiv! UpperTriangular 17.916 us vs MKL rdiv!(copyto!(C, A), UpperTriangular(B)) 19.852 us (1.11x, derived from page data); ldiv! LowerTriangular 19.694 us vs MKL ldiv!(C, LowerTriangular(B), A) 21.561 us (1.09x, derived from page data). Multithreaded (JULIA_NUM_THREADS=8; the README sets MKL to min(Threads.nthreads(), num_cores()) threads, which is 4 on this 4-core/8-thread CPU): rdiv! 8.769 us vs 14.163 us (1.62x, derived from page data); ldiv! 9.871 us vs 15.258 us (1.55x, derived from page data). Apple M1 single thread, BLAS not named: rdiv! 21.624 us vs 46.166 us (2.13x, derived from page data); ldiv! 34.375 us vs 49.124 us (1.43x, derived from page data), and a second ldiv! run of 23.875 us against the same 49.124 us baseline (2.06x, derived from page data). |
| **Workload** | 100x100 Float64 triangular solves with 100 right-hand sides (rdiv! UpperTriangular, ldiv! LowerTriangular), median of 10000 samples, single and multi-threaded. |
| **Metric** | latency |
| **Hardware** | 11th Gen Intel Core i7-1165G7 @ 2.80GHz (Linux); Apple M1 Mac (single-threaded only). |
| **Compiler and flags** | Julia 1.8.0-DEV.438 (commit 88a6376e99, 2021-08-28), libLLVM 12.0.1 ORCJIT with tigerlake target, JULIA_NUM_THREADS=8, no julia command-line options stated (Julia JIT, no compile flags). BLAS.set_num_threads(1) for the single-thread rows and BLAS.set_num_threads(min(Threads.nthreads(), num_cores())) for the multithreaded rows. MKL, MKL.jl and TriangularSolve versions not stated. The M1 run gives no Julia version or versioninfo. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 12 stars; part of the JuliaSIMD/LoopVectorization ecosystem |
| **Last commit** | 2026-08-15 |
| **Links** | [repository](https://github.com/JuliaSIMD/TriangularSolve.jl) · [benchmark](https://github.com/JuliaSIMD/TriangularSolve.jl) |

## Verdict

One BenchmarkTools REPL session (median of 10000 samples, 100x100 Float64 with 100 right-hand sides, Julia 1.8.0-DEV.438 on an i7-1165G7) gives TriangularSolve 17.9/19.7 us against MKL's 19.9/21.6 us single-threaded (rdiv! upper, ldiv! lower) and 8.8/9.9 us against 14.2/15.3 us with 4 threads on each side. The Apple M1 single-thread rows (21.6 and 23.9-34.4 us against 46.2 and 49.1 us) name no BLAS and give no versioninfo.

## Use it when

- Julia code doing many small to medium Float64/Float32 triangular solves with a matrix right-hand side (the published run is 100x100 with 100 right-hand sides), e.g. inside an LU-based solver; RecursiveFactorization.jl and LinearSolve.jl already depend on it.
- Latency-bound small solves where MKL or OpenBLAS threading overhead dominates: the README's 4-thread rows are 1.55-1.62x faster than MKL at N=100.
- Apple M1 or other machines where the default BLAS trsm is weak at small sizes (README M1 rows: 1.4-2.1x against an unnamed BLAS).
- Vector right-hand sides in Julia where you want a BLAS-free forward/back substitution (author-measured 1.14-7.42x over OpenBLAS trsv on one AVX2 EPYC 7502, single-threaded).

## Skip it when

- Element types other than Float32/Float64 (complex, BigFloat, Dual numbers): those calls just forward to LinearAlgebra.
- When you need results bit-identical to BLAS trsm/trsv: the kernels reassociate and use fused multiply-adds, and PR #48 notes vector results differ from trsv in rounding.
- Large solves where a tuned multithreaded BLAS trsm scales better: no published comparison exists above N=100 against MKL, and the 2026 numbers (PR #41) go to N=1000 only against single-threaded OpenBLAS on one AMD EPYC 7502.
- Code that already runs inside an outer threaded region or alongside multithreaded BLAS: the default call is threaded (Polyester), and Polyester's README suggests disabling its inner threads when parallelising at the outer level.
- Projects that cannot follow Julia-version churn in LoopVectorization/VectorizationBase: past issues include segfaults (#13, #18 on Julia 1.6.5), load failure on 1.8.0-beta1 (#20) and a precompile hang on 1.8 (#21).

## How it is fast

Hand-written @generated kernels on VectorizationBase solve register-resident W x W blocks (W = SIMD width) with fused negative multiply-adds, unrolled over U SIMD vectors of rows chosen so the blocks fit the register file. Larger problems are blocked to an L2-sized panel (block_size from cache_size(2)) with a LoopVectorization @turbo update between panels, and the threaded path splits the right-hand-side rows into independent blocks run on Polyester tasks capped at min(physical cores, Julia threads). Everything is JIT-specialized for the host CPU, so small sizes avoid BLAS call and threading overhead; ldiv! with LowerTriangular reuses the rdiv! kernels on transposed views.

## Compared with alternatives

Pick it for triangular solves the way you would pick Gaius.jl for small gemm: both are pure-Julia kernels that beat a vendor BLAS only at small sizes. Unlike FFTA.jl or Bessels.jl, which replace FFTW or openlibm calls, TriangularSolve's baseline is MKL itself, and its margin is small single-threaded (about 10%) but larger multithreaded or on M1.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LoopVectorization 0.12.30+, VectorizationBase 0.21, Polyester, LayoutPointers, Static, CloseOpenIntervals, IfElse, PrecompileTools, LinearAlgebra |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat); tests reported passing on Julia 1.10.11 and 1.12.4 in PR #41/#48 |
| **Platforms** | any CPU Julia and VectorizationBase support (README timings on x86-64 AVX-512 Tiger Lake and Apple M1; 2026 PR timings on AVX2 Zen 2 only) |
| **Thread safety** | not documented; the current source has no global buffers or other module-level mutable state (the 2021 code kept per-thread LDIVBUFFERS), and the threaded path runs on Polyester's shared task pool |
| **Drop-in for the baseline** | partial: same argument order as LinearAlgebra.rdiv!/ldiv!, but they are separate unexported functions (call TriangularSolve.ldiv!), take an extra threading flag, and only accelerate Float32/Float64 strided arrays |

## Gotchas

- The README numbers are from a 2021 author REPL session (Julia 1.8.0-DEV.438, i7-1165G7, MKL of unstated version) on v0.1-era code. All of the August 2026 kernel work (native left-upper/right-lower kernels, shortened backward chains, the vector path) came in PRs #41-#49 from the ChrisRackauckas-Claude account; #41 and #48 opened with a 'Draft, please ignore until reviewed' banner and were merged within about a day with no formal review. Those PRs were benchmarked only on an AVX2 AMD EPYC 7502 against single-threaded OpenBLAS (PR #41 also lists threaded TriangularSolve against single-threaded BLAS); AVX-512, aarch64 and MKL are untested per the PR text.
- Harness check: the README benchmark solves against unshifted rand(N,N) triangles. A numpy simulation of that distribution (200 draws, N=100) gives cond(U) about 1e16 and solution entries of 1e11-1e19. Results stay finite, so the timings are not affected, but the run shows nothing about accuracy. The test suite instead adds 1 or n to the diagonal.
- Thread counts were equal in the Intel run: the 2021 v0.1.4 source already capped TriangularSolve at min(num_cores, num_threads) = 4, the same as the MKL setting in the README. The README's copy-paste script, though, sets BLAS to Threads.nthreads() before the single-thread pair, unlike the session it reproduces. The README still ends with the stale line that only rdiv!/UpperTriangular and ldiv!/LowerTriangular are supported; that was true of the 2021 code (other cases fell back to LinearAlgebra) but not since v0.2.2.
- Issue #26 (closed December 2022): some ldiv! paths passed nthreads == static(0) into m_thread_block_size, an integer division by zero that LLVM can turn into a poison value. The maintainer agreed it should be 1. The current source passes static(1) for serial calls.

## Known shortcomings

- Baseline is closed MKL with no version (the M1 BLAS unnamed); a 2021 run on Julia 1.8-DEV whose code has since been rewritten; one size (N=100); single-thread margin about 10%; MKL ran on 4 threads, not 8.
- README numbers come from 2021 v0.1 code and were never re-run; all August 2026 kernel work arrived through PRs #41-#49 from the ChrisRackauckas-Claude account (#41 and #48 carried a Draft banner, merged within about a day with no review), benchmarked only on an EPYC 7502 (AVX2) against 1-thread OpenBLAS, with #41 comparing threaded TriangularSolve against 1-thread BLAS. The README solves unshifted rand(N,N) triangles with condition number about 1e16 (numpy simulation), so timing is unaffected but accuracy is unshown; the 2021 v0.1.4 source also capped TriangularSolve at 4 threads, equal to MKL. Old issue #26 (division-by-zero UB in m_thread_block_size) is fixed.

## Caveats and trade-offs

Single matrix size (N=100) from a 2021 author REPL session on a Julia 1.8 development build, on a package version that has since been substantially rewritten (August 2026 kernel changes: native left-upper/right-lower kernels, shortened backward-substitution chains, inlined backward panel kernels), with no re-run; the README still ends with a stale line saying only rdiv!/UpperTriangular and ldiv!/LowerTriangular are supported. The baseline is closed-source, hand-tuned MKL (not a C/C++ -O3 build of the same algorithm), its version is not stated, and the M1 rows compare against an unnamed BLAS with no versioninfo. The single-thread Intel advantage is only about 9-11%; the larger multithreaded and M1 gaps are where small-size threading and call overhead matter most. The README's copy-paste script calls BLAS.set_num_threads(Threads.nthreads()) before the single-thread pair, unlike the REPL session it reproduces. The README gives no mechanism, and the baseline timings include LinearAlgebra's copy of A into C, which is equal work because TriangularSolve's 3-argument form also writes out of place. Not a language-level claim: TriangularSolve is a pure-Julia library (no BLAS call in the matrix path) that beats one vendor library at one small size. Source comments claim the vector right-hand-side path beats BLAS trsv by up to 7x below n=256, but no published harness backs that. [retier] README numbers are from 2021 v0.1 code and were never re-run; the August 2026 kernel PRs #41-#49 (ChrisRackauckas-Claude account; #41 and #48 merged within about a day as drafts, no review) were benchmarked only on an EPYC 7502 against 1-thread OpenBLAS, #41 comparing threaded TriangularSolve against 1-thread BLAS. The README solves unshifted rand(N,N) triangles with condition number about 1e16, so accuracy is unshown; the 2021 v0.1.4 source capped TriangularSolve at 4 threads, equal to MKL.

Only Float32/Float64 with at least two right-hand sides, and the README says only rdiv! with UpperTriangular and ldiv! with LowerTriangular are the supported configurations on the benchmarked paths; vector right-hand sides use pure-Julia sweeps.

## Maintenance

Active (last commit 2026-08-15, v0.2.6, MIT). The code was substantially rewritten in August 2026 and the README numbers were never re-run; it is a dependency of RecursiveFactorization.jl and LinearSolve.jl, so it is maintained alongside the SciML stack.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README REPL session (BenchmarkTools medians, N=100) prints the benchmark code, Julia 1.8.0-DEV.438 with LLVM 12.0.1 and the i7-1165G7 CPU, but the baseline is closed-source MKL with no MKL or MKL.jl version, and the M1 half prints no versioninfo and does not name its BLAS. That fails the wave-14 A bar (public code, compiler, flags and CPU for both sides). It is a first-party author run from 2021 with no stated mechanism, so C.
- **Verifier notes:** Numbers match the README exactly; the record's '8 threads' was wrong: MKL ran on min(8, num_cores()) = 4 threads on the 4-core i7-1165G7, and the current source caps TriangularSolve at the same count (the 2021 code was not checked). Downgraded A to C because the baseline side (closed MKL, no version; M1 BLAS unnamed) does not meet the wave-14 both-sides A bar and no mechanism is stated. Under the older wave-8 reading (Octavian.jl, also MKL with no version) the Intel half would be A, so the orchestrator may choose that instead. Shortcomings to record: one size (N=100), 2021 dev-build numbers on since-rewritten code, closed vendor baseline with no version, unnamed M1 BLAS, single-thread margin about 10%, no mechanism stated. Metadata (MIT, 12 stars, 4 forks, last commit 2026-08-15, active) checks out; same_algorithm and same_opt_level stay null (MKL internals and build closed).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-22 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JuliaSIMD/TriangularSolve.jl>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/commits>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/commits?after=92d14e7097a4857aa45726788af0c1551439dfdd+34>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/src/TriangularSolve.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/src/TriangularSolve.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/HEAD/test/runtests.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/v0.1.4/src/TriangularSolve.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/v0.1.5/src/TriangularSolve.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/v0.1.6/src/TriangularSolve.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/TriangularSolve.jl/v0.1.8/src/TriangularSolve.jl>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/issues/26>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/commits>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/pull/41>
  - <https://github.com/JuliaSIMD/TriangularSolve.jl/pull/48>
  - <https://github.com/JuliaSIMD/LoopVectorization.jl>
  - <https://github.com/JuliaSIMD/Polyester.jl>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/juliasimd/triangularsolve.jl`) · [data/wave14/enrich/raw/github_com_juliasimd_triangularsolve_jl.json](../../../data/wave14/enrich/raw/github_com_juliasimd_triangularsolve_jl.json) (enrichment confidence 0.55)

</details>
