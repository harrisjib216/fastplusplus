# Julia 1.6 density-gradient kernel vs C++ at g++ -O3: zyth0s/bench_density_gradient_wfn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `MIT` · 🔴 abandoned

> Four-language port of one electron-density-gradient kernel where Julia 1.6 lands within about 9% of an Eigen C++ build, both directions.

| | |
|---|---|
| **Beats** | C++ port of the same density-gradient routine (cpp/lib.cpp, written with Eigen Map/VectorXd/MatrixXd/TensorMap over the caller's arrays; &lt;valarray&gt; is included but unused), called from Julia through @ccall in bench.jl. The published C++ timings were built by the cpp/Makefile of commit 0ebe405 with g++ (Apple clang 11.0.3) -Wall --std=c++11 -O3 -march=native; the current Makefile also passes -fPIC -funroll-loops, which were added later. |
| **Claimed result** | imidazol: Julia 112.843 us vs C++ 123.619 us; C2H4: Julia 41.737 us vs C++ 45.770 us (each about 9% faster, derived from page data). CH4: Julia 20.021 us vs C++ 19.656 us (C++ about 2% faster). Fortran (66.975 us on imidazol) and Rust (109.139 us) beat Julia. |
| **Workload** | Evaluate the electron-density gradient of a wavefunction at one point, 10 evaluations per sample, for CH4, C2H4 and imidazol (BenchmarkTools timings). |
| **Metric** | latency |
| **Hardware** | Intel Core i5-7360U @ 2.30GHz, macOS (x86_64-apple-darwin19.6.0) |
| **Compiler and flags** | C++: g++ is Apple clang 11.0.3 (clang-1103.0.32.62). The published timings (commit 0ebe405, 2021-05-17) used -Wall --std=c++11 -O3 -march=native with vendored Eigen headers; -fPIC (2021-05-19) and -funroll-loops (2021-05-22) were added afterwards without re-timing (the author reports no effect). Julia 1.6.0 (LLVM 11.0.1) was run with -O3 -C skylake --check-bounds=no and JULIA_NUM_THREADS=1. The published Julia timings (commit 5e99401, 2021-05-22) timed ChemInt.jl's jl_density_gradient!, not the in-repo julia/eval_gradrho.jl; that file (StaticArrays, @views, @inbounds) was added in commit 302ee4b and was never timed in the README. Fortran: gfortran 10.2.0 -O3 -march=native -funroll-loops -fPIC; Rust: rustc 1.52.1 with target-cpu=native, LTO and 1 codegen unit. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 5 stars |
| **Last commit** | 2021-05-29 |
| **Links** | [repository](https://github.com/zyth0s/bench_density_gradient_wfn) · [benchmark](https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/README.md) |

## Verdict

On a 2.3 GHz Core i5-7360U MacBook, BenchmarkTools minima for 10 density-gradient evaluations at one point were 20.021 / 41.737 / 112.843 us for Julia 1.6.0 (ChemInt.jl function, -O3 -C skylake --check-bounds=no) against 19.656 / 45.770 / 123.619 us for the Eigen C++ port (Apple clang 11.0.3, -O3 -march=native, asserts on) on CH4 / C2H4 / imidazol, timed five days apart; gfortran 10.2 was fastest at 17.897 / 26.353 / 66.975 us.

## Use it when

- As a worked example of porting a Fortran quantum-chemistry inner loop to Julia and the idioms (StaticArrays, @views, @inbounds, --check-bounds=no) that close most of the gap to compiled ports.
- As a ready-made harness for calling Fortran, C++ and Rust kernels from Julia with @ccall and timing them side by side on the same wavefunction data.
- For small-molecule, single-point density-gradient evaluation where a Julia code base wants to avoid a compiled dependency and can accept parity with, not a lead over, C++ and about 1.7x behind gfortran.

## Skip it when

- As evidence that Julia beats C++: the margins are about 9% faster on C2H4 and imidazol and about 2% slower on CH4, taken in runs five days apart, against a C++ build with Eigen range checks on.
- When you need the fastest kernel: the gfortran 10.2 port is 1.68x faster than Julia on imidazol (66.975 vs 112.843 us) and Rust also beats Julia there (109.139 us).
- For grid-scale or multithreaded density evaluation: the Julia kernel heap-allocates 2 + 2 x natm arrays per call (the orbital buffers plus two 3-vectors per atom), which adds GC pressure; issue #1 'Try with a larger system' was never done.
- As a general wavefunction library: no package, no API beyond one function, a hard-coded 56-row nlm table (Cartesian powers up to 5), Hartree-Fock .wfn input only, one fixed point (1,1,1).

## How it is fast

No special technique: every language runs the same loop nest. The Julia port gets to C++ parity with StaticArrays MVector scratch for the 3-component Gaussian factors, @views to avoid slice copies, @inbounds, and julia -O3 -C skylake --check-bounds=no. The README-only commit 5e99401, titled 'Added @inbounds', moved the Julia rows from 26.988/61.065/167.094 us to 20.021/41.737/112.843 us; since --check-bounds=no already removes bounds checks, part of that 1.35-1.48x change probably came from edits to the external ChemInt.jl code or run-to-run variation, which also shows how noisy a 9% margin is here. The C++ side reads every element through Eigen's checked operator() with assertions left on, which is the likeliest source of its small deficit; the effect was never measured.

## Compared with alternatives

Pick this over the other Julia-versus-C++ ports in the category (aaronang/stl-benchmark ParseStl, jlapeyre/ranwalk-Julia-vs-Cxx) only for a floating-point scientific kernel with Fortran and Rust ports alongside; its result is parity, not a win, and for a reproducible same-run comparison the kostya/benchmarks Julia matmul row is better evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop (julia/eval_gradrho.jl plus the AIMWFN struct defined in bench.jl) |
| **Dependencies** | Julia: StaticArrays (kernel); BenchmarkTools, Serialization and Libdl for the harness. Baselines: vendored Eigen 3.3.91 with its unsupported Tensor module (C++), ndarray 0.15 and mimalloc (Rust), gfortran (Fortran) |
| **Minimum toolchain** | Julia 1.6.0 as measured (@ccall needs 1.5 or later); C++11 for the baseline |
| **Platforms** | any platform Julia runs on for the kernel; measured only on x86-64 macOS (i5-7360U) |
| **Thread safety** | density_gradient! allocates its own scratch and writes only to the passed ∇ρ, so concurrent calls need separate output vectors; not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Crippled baseline, not noted by the verifier: cpp/Makefile passes no -DNDEBUG or -DEIGEN_NO_DEBUG and lib.cpp reads every Map, VectorXd and MatrixXd element through operator(), which in the vendored Eigen 3.3.91 runs eigen_assert(row &gt;= 0 && row &lt; rows() && ...) mapped to assert(); six checked accesses (coef, gun twice, gun1 three times) sit in the innermost orbital loop. Julia ran with --check-bounds=no plus @inbounds and Rust with unchecked uget (commit 3b3267a), so only the C++ side is bounds-checked, and that alone can plausibly cover a 9% gap.
- Cross-run and unpublished Julia code: C++ numbers come from commit 0ebe405 (2021-05-17), Julia numbers from the README-only commit 5e99401 (2021-05-22), which timed ChemInt.jl's jl_density_gradient! (repo now 404); commit 302ee4b swapped in the in-repo julia/eval_gradrho.jl without re-timing. Its allocation pattern (2 + 2 x natm per call) reproduces the README counts exactly (122, 142, 202 for 5, 6 and 9 atoms x 10 calls plus 2 wrapper arrays), so the measured function was probably the same code, but that is inferred, not measured.
- BenchmarkTools only counts Julia GC allocations: the '2 allocations: 224 bytes' on the C++, Rust and Fortran rows are the wrapper's point and ∇ρ arrays, while the C++ kernel also mallocs gun and gun1 through Eigen and the Rust kernel six ndarray buffers per call, so the record's 'C++ and Fortran allocate 2' tradeoff compares unlike counts.
- The four ports are not equivalent and their outputs are never cross-checked in bench.jl: in fortran/eval_gradrho.f90 'if (dis2 &gt; rcutte(ic,m)\*\*2) continue' is a no-op (Fortran's loop skip is cycle), so the fastest entrant evaluates every shell, including those the C++, Rust and Julia ports skip; only the Rust crate has a CH4 unit test with expected values.

## Known shortcomings

- Cross-run comparison: C++ timed at commit 0ebe405 (2021-05-17), Julia at 5e99401 (2021-05-22) using the external ChemInt.jl jl_density_gradient! (repo now 404); the in-repo julia/eval_gradrho.jl was never timed; the C++ side uses Eigen; the author calls the result parity and blames implementation differences.
- Crippled baseline in addition to the cross-run: cpp/Makefile passes no -DNDEBUG or -DEIGEN_NO_DEBUG, so every Eigen operator() in lib.cpp keeps its range-check assert (six checked accesses in the innermost orbital loop, vendored Eigen 3.3.91), while Julia ran with --check-bounds=no plus @inbounds and Rust used unchecked uget. The Fortran port's `if (...) continue` is a no-op (it should be `cycle`), so Fortran evaluates every shell and the ports are not equivalent; bench.jl never compares outputs. The record's 'C++ 2 allocations' tradeoff is wrong: BenchmarkTools counts only Julia allocations (2 + 2 x natm per call, matching the untimed in-repo port), and Eigen and Rust malloc per call too.

## Caveats and trade-offs

This is a cross-run comparison. The C++ timings (19.656/45.770/123.619 us) date from commit 0ebe405 (2021-05-17) and the Julia timings (20.021/41.737/112.843 us) from commit 5e99401 (2021-05-22), and the two were never re-measured together. The Julia numbers were taken with the external ChemInt.jl package's jl_density_gradient!, whose repo github.com/zyth0s/ChemInt.jl returns 404. The in-repo Julia port, julia/eval_gradrho.jl (StaticArrays version, commit 302ee4b), was never timed. The C++ timings predate the -fPIC and -funroll-loops flags in the current Makefile. The C++ port uses Eigen dynamic matrices, not std::valarray. The margin is small: about 9% on C2H4 and imidazol, while C++ is about 2% faster on CH4. Fortran is 1.68x faster than Julia on imidazol (derived from page data), and Rust also beats Julia there. The author writes that differences between compiled languages should be due to implementation differences, and titled the commit that produced these Julia numbers 'Julia is == Rust & C++'. Each case is one BenchmarkTools minimum (10 evaluations per sample) on a macOS laptop. The repo has had no commits since 2021-05-29 and has 5 stars. [retier] Enricher: crippled C++ baseline in addition to the cross-run; cpp/Makefile passes no -DNDEBUG or -DEIGEN_NO_DEBUG, so every Eigen operator() in lib.cpp keeps its range-check assert (six checked accesses in the innermost orbital loop, vendored Eigen 3.3.91), while Julia ran with --check-bounds=no plus @inbounds and Rust used unchecked uget. The Fortran port's `if (...) continue` is a no-op (it should be `cycle`), so Fortran evaluates every shell and the ports are not equivalent, and bench.jl never compares outputs. The 'C++ 2 allocations' tradeoff is wrong: BenchmarkTools counts only Julia allocations (2 + 2 x natm per call), and Eigen and Rust malloc per call too.

Julia allocates more (122 to 202 allocations, 14-27 KiB per call) than the C++ and Fortran versions (2 allocations, 224 bytes) and needs the JIT warm-up that BenchmarkTools excludes.

## Maintenance

Abandoned since 2021-05-29 with 5 stars and an open TODO issue, MIT-licensed and small enough to copy, but its Julia-over-C++ margin rests on a cross-run, assert-enabled C++ baseline, hence tier D.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README numbers match and bench.jl, cpp/Makefile, compiler versions and the CPU (i5-7360U) are public, but the C++ timings come from commit 0ebe405 (2021-05-17) and the Julia timings from commit 5e99401 (2021-05-22), when bench.jl timed the external ChemInt.jl function jl_density_gradient! (github.com/zyth0s/ChemInt.jl returns 404), so the measured Julia code is not public and was never re-timed against C++ in one run. Under the cross-run precedent a \~9% gap between runs goes to D; without that precedent it would be C at most, because the measured Julia code is not public.
- **Verifier notes:** Downgrade C to D. The numbers on the page are accurate, but C++ and Julia were timed in different runs five days apart, and the Julia figure measured an external, unpublished ChemInt.jl function rather than the repo's own Julia port. The author describes the result as parity ('Julia is == Rust & C++') and attributes the gaps to implementation. The baseline correction: the C++ side is Eigen-based, not std::valarray. MIT, 5 stars, abandoned (last commit 2021-05-29).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/master/README.md>
  - <https://github.com/zyth0s/bench_density_gradient_wfn>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commits>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/tree/main/cpp>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/bench.jl>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/Makefile>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/lib.cpp>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/julia/eval_gradrho.jl>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/fortran/Makefile>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/LICENSE>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commits/main/README.md>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commits/main/cpp/lib.cpp>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/54d3cf6>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/787cbcc>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/3b3267a>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/302ee4b>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/5e99401>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/a3278f6>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/0ebe405>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/tree/0ebe405/cpp>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/0ebe405b0593ec8e3ad750468c02da14c3547f2e/cpp/Makefile>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/0ebe405b0593ec8e3ad750468c02da14c3547f2e/bench.jl>
  - <https://github.com/zyth0s/ChemInt.jl>
- **Sources the enricher read:**
  - <https://github.com/zyth0s/bench_density_gradient_wfn>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commits/main>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/5e99401>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/commit/302ee4b>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/tree/main/cpp>
  - <https://github.com/zyth0s/bench_density_gradient_wfn/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/README.md>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/bench.jl>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/LICENSE>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/lib.cpp>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/Makefile>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/test.cpp>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/Eigen/src/Core/DenseCoeffsBase.h>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/Eigen/src/Core/util/Macros.h>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/cpp/Eigen_unsupported/Eigen/CXX11/src/Tensor/TensorMap.h>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/julia/eval_gradrho.jl>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/fortran/eval_gradrho.f90>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/fortran/Makefile>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/zyth0s/bench_density_gradient_wfn/main/rust/Makefile>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/zyth0s/bench_density_gradient_wfn#density-gradient`) · [data/wave14/enrich/raw/lang_julia_zyth0s_bench_density_gradient_wfn_density_gradient.json](../../../data/wave14/enrich/raw/lang_julia_zyth0s_bench_density_gradient_wfn_density_gradient.json) (enrichment confidence 0.8)

</details>
