# Julia (@fastmath loop) in anicusan/AcceleratedKernels-Benchmark: Lennard-Jones-Gauss kernel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `GPL-3.0` · 🟡 stale

> Single-threaded Julia @fastmath Lennard-Jones-Gauss loop against -O2 C calling libm powf and expf: 5.7x faster on M3 Max, 1.4x on Xeon 8360Y.

| | |
|---|---|
| **Beats** | C version of the same kernel (arithmetic_kernel.c, ljg_cpu with powf) called from Julia via ccall, built with the repo Makefile at -O2; plus a C variant with hand-written integer powers (ljg_cpu2) and a C OpenMP variant |
| **Claimed result** | benchmarks.csv medians (ms): LJG Apple M3 Max, Julia Base 219.47 vs C 1253.0 (5.7x, derived from page data) vs C with hand-written powf 426.37 (1.9x, derived); LJG Intel 8360Y, Julia Base 335.80 vs C 470.61 (1.4x, derived) vs hand-written 381.33 (1.1x, derived). The RBF kernel goes the other way: C 210.57 vs Julia Base 318.35 on M3 Max and C 641.26 vs Julia 734.22 on Intel. AcceleratedKernels.jl on CPU against C OpenMP is parity: LJG 27.93 vs 28.53 (M3 Max), 49.46 vs 53.01 (Intel). |
| **Workload** | Lennard-Jones-Gauss potential on single-precision (Float32) atom position arrays of N = 100,000,000 points (potential_kernel.jl), one thread for 'CPU Base' (the ljg_cpu! function) and C, timings in ms (median with spread) on Apple M3 Max and Intel 8360Y; a radial basis function kernel is in the same table. |
| **Metric** | throughput |
| **Hardware** | Apple M3 Max (aarch64) and Intel Xeon 8360Y (Ice Lake, x86_64; rows labelled BBIceLake in benchmarks.csv); AMD MI210, NVIDIA A100-40 and Apple M3 GPU for the AcceleratedKernels GPU rows |
| **Compiler and flags** | C: Makefile FLAGS = -Wall -Werror -Wextra -fPIC -lm -O2 via \$(CC), built as a shared library and called from Julia with @ccall; compiler not named ('-Xclang -fopenmp' with Homebrew libomp suggests Apple clang on the M3). No -O3, -march=native or -ffast-math. The checked-in disassembly shows scalar x86_64 code calling powf, expf and sqrtf from libm per element, with ljg_cpu2 calling dist3 through the PLT (not inlined); the aarch64 build unrolls 4 lanes but still calls powf and expf per lane. Julia: ljg_cpu! ('CPU Base') uses @inbounds @fastmath; Julia version not stated (Project.toml lists deps only, no Manifest). Timing with BenchmarkTools @benchmark, N = 100,000,000. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Why it wins** | Not stated by the source. Inferred from the code: @fastmath plus literal integer powers (lowered to multiplications) in Julia versus libm powf at -O2 without fast-math in C. |
| **Adoption** | 2 stars (benchmark repo); the library JuliaGPU/AcceleratedKernels.jl has 203 stars |
| **Last commit** | 2024-09-22 |
| **Links** | [repository](https://github.com/anicusan/AcceleratedKernels-Benchmark) · [benchmark](https://github.com/anicusan/AcceleratedKernels-Benchmark) |

## Verdict

benchmarks.csv medians for one call over 100M Float32 pairs on one thread: Apple M3 Max Julia 219.47 ms vs C (-O2, libm powf) 1253.0 ms and C2 (integer powers by multiplication) 426.37 ms; Intel Xeon 8360Y Julia 335.80 ms vs C 470.61 ms and C2 381.33 ms, i.e. 5.7x and 1.9x on M3 and 1.4x and 1.1x on Xeon (derived from page data). At 10 threads, AK CPU and C OpenMP are at parity (27.93 vs 28.53 ms and 49.46 vs 53.01 ms). The C compiler is unnamed (probably Apple clang on the M3) and the Julia version is not stated.

## Use it when

- As a worked example of why C code with powf(x, 12) or powf(x, 6) should spell the powers as multiplications, or be built with -ffast-math or -fno-math-errno and a vector math library, before it is compared with Julia: the repo's own C2 row cuts the M3 gap from 5.7x to 1.9x and the Xeon gap from 1.4x to 1.1x.
- Single-threaded elementwise physics or potential kernels in Julia over large Float32 arrays, where @fastmath with literal integer exponents gives inlined powers and exp without hand-unrolling.
- As a pointer to AcceleratedKernels.jl when one Julia source must run on CPU threads and on CUDA, ROCm, oneAPI or Metal GPUs: its 10-thread CPU rows match C OpenMP on this kernel (27.93 vs 28.53 ms on M3 Max, 49.46 vs 53.01 ms on Xeon 8360Y).

## Skip it when

- As evidence that Julia beats optimised C: the C side is -O2 with no -ffast-math or -march and libm powf, and its only rewrite (C2) still calls expf per element; no -O3 -ffast-math build, vector math library or hand-vectorised C was measured.
- For the RBF kernel in the same table, where plain C wins: 210.57 vs 318.35 ms on M3 Max and 641.26 vs 734.22 ms on Xeon 8360Y.
- When @fastmath semantics are unacceptable (reassociation, no NaN or Inf guarantees, powi accuracy for large exponents); the benchmark never compares the Julia and C outputs.
- When a reproducible setup is needed: the Julia version and the Linux C compiler are not recorded, there is no Manifest, and the scripts are edited per machine (checked in with CUDA active, while the M3 rows needed Metal).

## How it is fast

Under @fastmath, Julia rewrites (sigma/r)^12, (sigma/r)^6 and sigma^2 to pow_fast(x, Val(p)), which lowers to llvm.powi with a constant exponent, i.e. a few multiplications (base/fastmath.jl). exp becomes Base.Math.exp_fast, an inlined Float32 polynomial with two range checks and no table (base/special/exp.jl), and sqrt becomes the LLVM intrinsic, so the loop body is inline arithmetic the compiler can vectorize. The C ljg_cpu, built at -O2 without -ffast-math, makes two libm powf calls and one expf call for each in-cutoff element. On the M3 build (otool output of the Mach-O .so) clang vectorized the loop 4-wide and if-converted the r &lt; cutoff branch, so it makes 8 powf and 4 expf calls for every 4 elements and then masks the result, although only about 7.9% of pairs fall inside the cutoff (Monte Carlo estimate for these inputs). That is why C takes 1253.0 ms on the M3 Max but 470.61 ms on the Xeon, whose scalar build branches around the calls.

## Compared with alternatives

Pick it only as an illustration of @fastmath integer-power and exp lowering against libm powf and expf. For a cleaner Julia-against-C scalar comparison, JuliaLang/Microbenchmarks userfunc_mandelbrot takes C's best of -O0 to -O3; for production portable CPU and GPU kernels, use AcceleratedKernels.jl itself, which reaches parity with C OpenMP here rather than beating it.

## Integration

| | |
|---|---|
| **Form** | source-drop (ljg_cpu! in ArithmeticBenchmark/potential_kernel.jl, GPL-3.0); the library behind it, AcceleratedKernels.jl, is a registered Julia package (MIT) |
| **Dependencies** | the plain ljg_cpu! loop needs only Julia Base; the benchmark scripts import BenchmarkTools, AcceleratedKernels, GPUArrays, CUDA (or Metal or AMDGPU), LoopVectorization (imported but unused by these kernels) and Random, and the C rows need arithmetic_kernel.so built with the repo Makefile |
| **Minimum toolchain** | Julia version not stated (Project.toml has no compat section and there is no Manifest); the scripts' Random.Xoshiro needs Julia 1.7 or later, and AcceleratedKernels.jl's CI lists Julia 1.10 and 1.11 for its GPU backends. C: any C99 compiler; the Makefile's OpenMP line (-Xclang -fopenmp with Homebrew libomp paths) only works with Apple clang. |
| **Platforms** | measured on Apple M3 Max (aarch64, macOS) and Intel 8360Y (Ice Lake, x86_64, Linux judging from the ELF objdump output) on single cores, with OpenMP and AK CPU rows at 10 threads; GPU rows on Apple M3 GPU, AMD MI210 and NVIDIA A100-40 |
| **Thread safety** | ljg_cpu! is single-threaded and writes only energies[i], so concurrent calls on disjoint outputs are safe; not otherwise documented |
| **Drop-in for the baseline** | partial: the Julia function takes the same arguments as the C ljg_cpu (energies, atoms1, atoms2, epsilon, sigma, A, r0, cutoff) on 3xN Float32 matrices with the same memory layout, but it is Julia code, not a C replacement |

## Gotchas

- Harness flaw behind the 5.7x M3 headline: the checked-in arithmetic_kernel.aarch64.s shows ljg_cpu vectorised with the cutoff branch if-converted, calling powf twice and expf once for every element (masked afterwards with and.16b), and ljg_cpu2 likewise calls expf for every element; with only about 7.9% of pairs inside the cutoff, the C rows on M3 do roughly 12 times more libm calls than the source's branch implies. The scalar x86_64 build branches around the calls, which is why the same C runs 2.7x faster on the Xeon (470.61 ms) than on the M3 (1253.0 ms).
- Even the 'fair' C2 row compares Julia's inlined exp_fast against a libm expf call, and on x86_64 ljg_cpu2 calls dist3 through the PLT instead of inlining it (an -fPIC build with endbr64 markers, which looks like GCC; the Linux compiler is not recorded), so the 1.9x and 1.1x C2 ratios still include call overhead.
- The Intel rows are probably partly memory-bound: each call streams 2.4 GB of atom coordinates and writes 0.4 GB of energies, so Julia's 335.80 ms is about 8.3 GB/s from one core (derived from page data), which compresses the x86 differences.
- The repo has no README and makes no Julia-beats-C claim; the paper (arXiv, blocked here) and its IEEE DataPort dataset description, seen only as search snippets, say arithmetic kernels perform on par with C and OpenMP. Project.toml lists Metal and CairoMakie but not BenchmarkTools or CUDA, which the scripts import.

## Known shortcomings

- Win comes from flags, not the language: the C side is built -O2 without -ffast-math and calls libm powf/expf per element (checked .s files) while the Julia kernel uses @fastmath; Julia loses on the RBF kernel. arXiv 2507.16710 unreachable, paper claim from a snippet only.
- Harness flaw behind the 5.7x M3 headline, found in the checked-in arithmetic_kernel.aarch64.s: clang vectorised ljg_cpu and if-converted the cutoff branch, so two powf plus one expf run for every element and are then masked; only about 7.9% of pairs are inside the cutoff (Monte Carlo estimate), so the C side does roughly 12x more libm calls than the source implies, and ljg_cpu2 likewise calls expf for every element. The scalar x86 build branches around the calls, hence C 470.61 ms on the Xeon against 1253.0 ms on the M3; the Intel rows run at about 8.3 GB/s from one core (derived), likely partly memory-bound. Julia's @fastmath lowering (powi, exp_fast) is confirmed in base/fastmath.jl and base/special/exp.jl. The Julia version and the Linux C compiler are not recorded.

## Caveats and trade-offs

Not like for like: the C code is built at -O2 without fast-math (wave 14 asks for -O3) and calls libm powf for the ^12 and ^6 terms and libm expf per element (confirmed in the checked-in .s files), while the Julia loop is compiled under @fastmath, where literal integer powers become multiplications and LLVM may vectorize exp; the repo's own 'C (hand-written powf)' row (ljg_cpu2, integer powers by multiplication) narrows the gap to 1.9x on M3 Max and 1.1x on Intel, and the remainder is plausibly fast-math vectorization (inference). Julia loses on the RBF kernel (318.35 vs 210.57 ms on M3 Max, 734.22 vs 641.26 ms on Intel). AcceleratedKernels.jl on CPU vs C OpenMP is parity. The repo has no README and makes no Julia-beats-C claim; the paper abstract (arXiv 2507.16710, snippet only, arXiv blocked here) says arithmetic kernels perform on par with C and OpenMP and that Julia is sometimes more consistent than conventional C compilers. Results also in ArithmeticBenchmarkTable.png and Benchmark.xlsx; the dataset is mirrored on IEEE DataPort (DOI 10.21227/94q9-p565, snippet only). [retier] In the checked-in arithmetic_kernel.aarch64.s clang vectorised ljg_cpu and if-converted the cutoff branch, so two powf plus one expf run for every element and are then masked; only about 7.9% of pairs are inside the cutoff (Monte Carlo estimate), so the C side does roughly 12x more libm calls than the source implies (ljg_cpu2 likewise calls expf for every element). The scalar x86 build branches around the calls (C 470.61 ms on the Xeon against 1253.0 ms on the M3); the Intel rows run at about 8.3 GB/s from one core, likely partly memory-bound. The Julia version and the Linux C compiler are not recorded.

Benchmark repo accompanies the AcceleratedKernels.jl paper; the Julia kernel code is not a reusable library.

## Maintenance

Paper artifact repo (GPL-3.0, 2 stars, 4 commits all on 2024-09-22, no README), stale but small enough to re-run; the maintained product is AcceleratedKernels.jl (MIT, 203 stars, release 0.4.3 of July 2025 per a registry snippet). Treat the 5.7x as an artifact of libm calls and if-conversion in the C build, not a language effect.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** Code (ArithmeticBenchmark/potential_kernel.jl, arithmetic_kernel.c), C flags (Makefile -O2) and CPUs (Apple M3 Max, Intel 8360Y in ArithmeticBenchmarkTable.png) are public, but the C compiler and the Julia version are not named, so not A; the numbers are the library author's own paper artifact (arXiv 2507.16710, a preprint), so C.
- **Retiered** C to D: Enricher: the checked-in aarch64 assembly shows clang if-converted the cutoff branch and runs two powf plus one expf for every pair while only about 8% are inside the cutoff, so the M3 C baseline does roughly 12x the libm work the source implies, and the x86 build does not; a crippled baseline behind the 5.7x headline with no like-for-like row: C to D.
- **Verifier notes:** Numbers match benchmarks.csv and the table image exactly. Keep at C with the flag mismatch documented: -O2 C without fast-math vs Julia @fastmath, so the win is a build-flag and libm-call effect, not a language effect; it is not -O0, so the crippled-baseline D rule was not applied, though the orchestrator may choose to. Metadata (GPL-3.0, 2 stars, 4 commits all 2024-09-22, stale) confirmed.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-39 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/anicusan/AcceleratedKernels-Benchmark>
  - <https://github.com/anicusan/AcceleratedKernels-Benchmark/tree/main/ArithmeticBenchmark>
  - <https://github.com/anicusan/AcceleratedKernels-Benchmark/commits/main>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/Makefile>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.c>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/benchmarks.csv>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/potential_kernel.jl>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/rbf_kernel.jl>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/Project.toml>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.x86_64.s>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.aarch64.s>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/ArithmeticBenchmarkTable.png>
- **Sources the enricher read:**
  - <https://github.com/anicusan/AcceleratedKernels-Benchmark>
  - <https://github.com/anicusan/AcceleratedKernels-Benchmark/tree/main/ArithmeticBenchmark>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/Makefile>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.c>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel_omp.c>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/benchmarks.csv>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/potential_kernel.jl>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/rbf_kernel.jl>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/Project.toml>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.x86_64.s>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/arithmetic_kernel.aarch64.s>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/disassemble_linux.sh>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/disassemble_apple.sh>
  - <https://raw.githubusercontent.com/anicusan/AcceleratedKernels-Benchmark/HEAD/ArithmeticBenchmark/plot.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/base/fastmath.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/base/special/exp.jl>
  - <https://github.com/JuliaGPU/AcceleratedKernels.jl>
  - https://arxiv.org/html/2507.16710v1 (ENOTFOUND, blocked)
  - WebSearch: '"AcceleratedKernels.jl" "Cross-Architecture Parallel Algorithms" arithmetic kernels C OpenMP Julia "more consistent"' (snippets from arXiv, IEEE DataPort, JuliaCon 2025 pretalx and the Julia package registry)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/anicusan/acceleratedkernels-benchmark#ljg-kernel`) · [data/wave14/enrich/raw/lang_julia_anicusan_acceleratedkernels_benchmark_ljg_kernel.json](../../../data/wave14/enrich/raw/lang_julia_anicusan_acceleratedkernels_benchmark_ljg_kernel.json) (enrichment confidence 0.65)

</details>
