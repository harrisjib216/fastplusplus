# PureBLAS.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia BLAS 1-3 plus LAPACK that matches or beats single-threaded OpenBLAS and AOCL on AMD Zen3/4/5.

| | |
|---|---|
| **Beats** | OpenBLAS (Julia's bundled build) and AOCL-BLIS (AMD's BLIS fork); the repo's gate is max(OpenBLAS, AOCL) |
| **Claimed result** | README: about 87% of benchmarked cells are at or above max(OpenBLAS, AOCL), single-threaded. Median PureBLAS/OpenBLAS ratios (Zen3/Zen4/Zen5) from bench/gen_table.md: gemm 1.17/1.08/1.23, potrf 1.11/1.46/1.49, geqrf 1.55/1.79/1.66, getrf 1.17/1.20/1.31, gesvd 1.30/1.27/1.30, syev 1.40/1.44/1.34. Versus AOCL (gen_table_aocl.md): gemm 1.06/1.08/1.07, potrf 1.72/1.37/1.20, geqrf 1.64/1.30/1.24. notes.md: gemm at n=4096 is 1.252/1.280/1.308 (Zen4/Zen3/Zen5) against the faster of OpenBLAS and AOCL. |
| **Workload** | Single-threaded Float64 and ComplexF64 BLAS 1-3 and LAPACK routines across sizes on three AMD microarchitectures (2619 op/size/machine cells), measured with ABBA-interleaved rounds at locked clock frequency and the median ratio reported. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X (Zen3), Ryzen 5 7640U (Zen4), Ryzen AI 5 340 (Zen5); measured 2026-09-23 (bench/provenance.md) |
| **Compiler and flags** | Julia 1.13: Project.toml compat julia = "1.13" and LinearAlgebra = "1.13.0", and CI tests only 1.13. The exact patch release, LLVM and OpenBLAS_jll versions used for the sweep are not stated. Default JIT optimization (no custom flags). The harness is bench/plots.jl with BLAS.set_num_threads(1), BLIS_NUM_THREADS/OMP_NUM_THREADS pinned to 1 before AOCL loads, and PureBLAS called through its native API against LinearAlgebra.BLAS. Frequency is locked with bench/fleet_freqlock.sh (boost off, base clock) and runs use ABBA-interleaved rounds with the median ratio reported. Reproduce: taskset -c N julia --project=bench bench/plots.jl bench. AOCL comes from AOCL_jll (amd-main). |
| **Adoption** | 9 stars, 1,368 commits |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/el-oso/PureBLAS.jl) · [benchmark](https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/gen_table.md) |

## Verdict

The author's harness (bench/plots.jl, single thread, frequency-locked, ABBA-interleaved rounds, median ratio) on a Ryzen 9 5900X (Zen3), Ryzen 5 7640U (Zen4) and Ryzen AI 5 340 (Zen5) laptop under Julia 1.13 against Julia's bundled OpenBLAS and AOCL_jll shows per-op median ratios such as gemm 1.17/1.08/1.23 and geqrf 1.55/1.79/1.66 vs OpenBLAS, with about 87% of 2619 cells at or above max(OpenBLAS, AOCL); worst cells lose (gemm 0.94 on Zen4, 0.90 on Zen5) and about 30% of cells sit within +-5% of parity.

## Use it when

- Julia code on AMD Zen3/Zen4/Zen5 that is dominated by single-threaded dense factorizations: the project's own tables show median 1.1-1.8x over OpenBLAS for potrf, geqrf, getrf, gesvd and syev
- Forward-mode AD through linear algebra in Julia: ForwardDiff duals run through the generic kernels, 1.1-50x faster than LinearAlgebra's generic fallback in the dual tables
- Large real or complex gemm (n &gt;= 256) where Strassen-Winograd or 3M rounding behaviour is acceptable
- Swapping BLAS backends in an existing Julia program with one activate() call to A/B test against OpenBLAS

## Skip it when

- Production C/C++ code: the libpureblas.so path depends on experimental juliac --trim, embeds a Julia runtime, exports only ILP64 Fortran symbols (no CBLAS header documented), and the shared library is single-threaded because juliac builds with handle-signals=no
- Apple Silicon: the roadmap measures PureBLAS gemm at about 0.68x OpenBLAS at n=2048 on an M-series part, and Accelerate's SME path is about 7x faster than any NEON code; SME work is still a campaign
- Intel or Arm servers in general: every published gate number is from three AMD Ryzen machines; no Intel results exist
- Code that needs classical O(n^3) gemm error bounds or bitwise agreement with reference BLAS: large gemm/zgemm use fast algorithms
- Multi-threaded throughput against threaded vendor BLAS: threading is opt-in and recent, and the threaded-gate plots for Zen4 are flagged as not yet adjudicable

## How it is fast

Block sizes (MC/NC/KC, panel widths, crossovers) are derived at load time from detected cache sizes, vector width and register count instead of per-CPU hand-tuned tables, feeding a GotoBLAS-style packed GEMM engine with SIMD.jl microkernels. Above about min(m,n,k) &gt;= 256, real gemm switches to Strassen-Winograd and complex gemm to Karatsuba 3M (three real products, 25% fewer flops), which is where much of the large-n BLAS-3 lead comes from. LAPACK routines are blocked ports (dlatrd/syr2k reduction, compact-WY back-transform, divide-and-conquer stedc, blocked dlaqps, dlasyf/zlahef) with fixes for power-of-two leading-dimension cache-set aliasing, and nrm2 scales only on overflow/underflow rather than always (hence 7-11x over OpenBLAS there).

## Compared with alternatives

Pick PureBLAS over Octavian.jl when you need full BLAS plus LAPACK in Julia rerouted through libblastrampoline rather than a threaded gemm alone, and over RecursiveFactorization.jl when you want every factorization, not just LU, replaced. For small cache-resident matrices in C, BLASFEO is the mature choice; for C++ code that just needs a faster BLAS, Eigen or a vendor BLAS is far less risky than PureBLAS's experimental shared library.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages CPUSummary, CpuId, SIMD, PrecompileTools, Preferences, StrictMode, TypeContracts (LinearAlgebra stdlib); ForwardDiff optional extension. Not registered in the General registry; install from the git URL. |
| **Minimum toolchain** | Julia 1.13 (the only supported and CI-tested release) |
| **Platforms** | x86-64 with AVX2 or AVX-512 (benchmarked only on AMD Zen3/4/5); runs on Apple Silicon/aarch64 via NEON but slower than OpenBLAS there; shared library built on Linux in CI, macOS .dylib path exists |
| **Thread safety** | Per-thread scratch (Base.OncePerThread) and allocation-free ! entries at steady state; internal threading of gemm/symm/syrk/syr2k/trsm (and getrf/potrf through them) is off by default and enabled with PureBLAS.set_num_threads(n). Not available in the .so. |
| **Drop-in for the baseline** | partial — inside Julia, PureBLAS.activate() reroutes every LinearAlgebra BLAS/LAPACK symbol (enforced by a test); outside Julia, libpureblas.so exports ILP64 Fortran symbols (dgemm_64_ etc.) like an ILP64 OpenBLAS, but LP64 and CBLAS interfaces are not documented and the route is experimental |

## Gotchas

- Do not load libpureblas.so into a running Julia process (or lbt_forward to it): the embedded libjulia double-initializes and aborts; use activate() instead
- Calls routed through activate() go through the C ABI, so Dual numbers cannot pass; call PureBLAS.\* directly for AD (reverse mode is not supported at all)
- Singular vectors are only available for Float64 and complex; the generic path raises an error rather than returning less
- v0.1.2 fixed a MethodError in complex gemv trans='T'/'C' for any A larger than L2 (which could make eigen() on complex Hermitian matrices throw); live 2026-08-08 to 2026-08-29, so pin to v0.1.2 or later

## Known shortcomings

- gemm switches to Strassen-Winograd from n&gt;=256, so it is not like-for-like with classical BLAS; notes.md 'gemm gates every size' contradicts the table's worst 0.90/0.94; Julia 1.13 patch unstated.
- Large gemm uses Strassen-Winograd and zgemm uses Karatsuba 3M (not like-for-like numerics); Apple Silicon gemm runs about 0.68x OpenBLAS (ROADMAP); correctness bug fixed in v0.1.2: complex gemv trans T/C threw MethodError for A larger than L2, breaking complex eigen() (live 2026-08-08 to 2026-08-29); the shared library cannot thread (juliac handle-signals=no); unregistered package.

## Caveats and trade-offs

This is a very young project (9 stars). The benchmarks are the project's own and run only on three AMD Zen machines; the Zen5 box is a laptop whose worst cells move by several points between runs, and there are no Intel or Arm results in the table. The table shows a per-op median with the worst cell, so some cells lose: gemm worst 0.94 on Zen4 and 0.90 on Zen5, and docs/src/notes.md lists trmm on AVX2 at 0.84 as still open. That notes page also says gemm 'gates at every size on all three boxes', which conflicts with the table's worst cells. Above about min(m,n,k) &gt;= 256, gemm uses Strassen-Winograd (notes.md, ROADMAP.md), so the gemm and BLAS-3 ratios compare a fast-matrix-multiplication algorithm with weaker error bounds against OpenBLAS's classical gemm. Some large ratios reflect weak reference implementations rather than kernel speed: nrm2 runs at 8-11x, and methodology.md itself warns about packed Cholesky and small-n AOCL. The README says about 87% of benchmarked cells are at or above max(OpenBLAS, AOCL). methodology.md gives per-cell drift of 1-6% and says about 30% of cells sit within +-5% of parity. notes.md compares potrf against BLASFEO as an MKL proxy (0.87-1.04x), not against MKL directly. All code is single-threaded. The C-callable shared library depends on experimental juliac --trim.

Pure Julia BLAS and LAPACK (about 36k lines) that derives block sizes from detected cache and vector sizes. Inside Julia it reroutes LinearAlgebra through libblastrampoline with PureBLAS.activate(). It can also build libpureblas.so (ILP64 BLAS symbols, embedded Julia runtime) via juliac --trim, which the README calls experimental; that route makes it linkable from C/C++/Rust. Single-threaded only (multithreading deliberately on hold). Singular vectors only for Float64 and complex.

## Maintenance

Very active (1,368 commits, last 2026-09-30) but weeks-to-months old, 9 stars, tagged v0.1.2 and deliberately unregistered; MIT-licensed, so it is easy to try inside Julia, while the C-callable library is experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** bench/plots.jl is public and has a stated reproduce command. bench/provenance.md gives the CPU models (Ryzen 9 5900X, Ryzen 5 7640U, Ryzen AI 5 340), commits and timestamps. The toolchain is Julia 1.13, required by Project.toml compat and the only CI version, with default JIT optimization, single thread and locked frequency. The exact Julia patch release is not stated, which makes this borderline, but it is kept at A.
- **Verifier notes:** Every gemm, potrf, getrf and geqrf figure in the record matches bench/gen_table.md. The page confirms MIT, 9 stars and the last commit on 2026-09-30. The main new shortcoming is that gemm uses Strassen-Winograd at large sizes, so it is not like-for-like with classical BLAS on numerics.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/el-oso/PureBLAS.jl>
  - <https://github.com/el-oso/PureBLAS.jl/commits/master>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/gen_table.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/provenance.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/methodology.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/notes.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/Project.toml>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/plots.jl>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/.github/workflows/CI.yml>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/el-oso/PureBLAS.jl>
  - <https://github.com/el-oso/PureBLAS.jl/issues>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/gen_table.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/gen_table_aocl.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/bench/provenance.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/methodology.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/notes.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/docs/src/threading.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/juliac/ctest.c>
  - <https://raw.githubusercontent.com/el-oso/PureBLAS.jl/HEAD/juliac/build.jl>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/el-oso/pureblas.jl`) · [data/wave8/enrich/raw/github_com_el_oso_pureblas_jl.json](../../../data/wave8/enrich/raw/github_com_el_oso_pureblas_jl.json) (enrichment confidence 0.8)

</details>
