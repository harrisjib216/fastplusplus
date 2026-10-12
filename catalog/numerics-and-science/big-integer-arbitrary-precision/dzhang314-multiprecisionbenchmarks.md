# MultiFloats.hpp (dzhang314/MultiprecisionBenchmarks)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Paper harness with an AVX-512 header of branch-free double- to quad-double add/multiply that outruns MPFR, QD and CAMPARY.

| | |
|---|---|
| **Beats** | MPFR (also GMP mpf, CLN, FLINT, Boost.Multiprecision, QD, CAMPARY, libquadmath in the same harness) |
| **Claimed result** | SC 2025 paper abstract (Zhang and Aiken, 'High-Performance Branch-Free Algorithms for Extended-Precision Floating-Point Arithmetic', pp. 695-710, published online 2025-11-15), confirmed on the author's publications page: up to 11.7x the peak performance of QD, 34.4x over CAMPARY, 35.6x over MPFR and 41.4x over FLINT. These are peak-vs-peak figures. The kernel, precision, thread count and CPU behind each peak were not seen, because the paper body could not be opened. The repo commits no result files. |
| **Workload** | Google Benchmark kernels axpy, dot, gemv and gemm on arrays of extended-precision numbers (axpy and dot 2^8 to 2^24 elements, gemm n = 8 to 512), OpenMP thread counts 1 to 32, at 1 to 4 double-word expansions (MPFR run at 53, 103, 156 and 208 bits) with MultiFloats.hpp using hand-vectorized (8-wide) code on split-array storage. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X (Zen 5) and Apple M3 Pro, per a search-result snippet of the paper (not opened); bench_linux.sh runs OMP_NUM_THREADS 32, 16, 8, 4, 2, 1 with OMP_PROC_BIND=spread, OMP_PLACES=threads. |
| **Compiler and flags** | g++-14 and clang++-20, -std=c++17 -fopenmp -ffp-contract=off -fno-math-errno -O3 -march=native -flto -fvisibility=hidden -fmerge-all-constants (-fwhole-program for GCC), linked with -lbenchmark; from build_linux.sh in the repo |
| **Adoption** | 2 stars (benchmark repo); the algorithms are also in MultiFloats.jl with 159 stars |
| **Last commit** | 2025-08-27 |
| **Links** | [repository](https://github.com/dzhang314/MultiprecisionBenchmarks) · [benchmark](https://dl.acm.org/doi/10.1145/3712285.3759876) |

## Verdict

The SC '25 paper abstract (seen only as search snippets; the paper hosts are blocked here) reports peak throughput up to 11.7x QD, 34.4x CAMPARY, 35.6x MPFR and 41.4x FLINT across axpy, dot, gemv and gemm at 2 to 4 doubles, with search snippets naming AMD Zen 5 (Ryzen 9 9950X) and Apple M3 Pro; the public harness builds with g++-14/clang++-20 at -O3 -march=native -flto and runs MPFR at 53, 103, 156 and 208 bits. Which kernel, precision and thread count produce each peak ratio is not documented in the repo.

## Use it when

- Bulk elementwise or BLAS-style kernels (axpy, dot, gemv, small gemm) where double is not accurate enough and roughly 106, 159 or 212 significand bits suffice.
- You can lay out data as one double array per limb (structure of arrays) so the add/multiply networks vectorize.
- x86-64 with AVX-512 (the harness hardware per the paper abstract snippet was an AMD Ryzen 9 9950X); a scalar ARM header exists for Apple Silicon.
- As a reference implementation of the paper's add and multiply networks to port into your own SIMD code, or to reproduce the paper's library comparison (MIT license).

## Skip it when

- You need arbitrary or runtime-selectable precision, correct rounding, or MPFR's exponent range: these types have the exponent range of double and are capped at 4 limbs.
- You need anything beyond + and \*: the C++ header has no subtraction, division, sqrt, transcendental functions, comparisons or string conversion (the full operation set is in the Julia package MultiFloats.jl).
- Your code must handle infinities or NaN-free overflow: TwoSum on an infinite input produces NaN error terms, and the Julia sibling documents that ±Inf inputs return NaN.
- Your target CPU lacks AVX-512: the x86 header defines __m512d overloads and uses _mm256_extractf64x2_pd (AVX-512DQ/VL) unconditionally, and the benchmark kernels call _mm512_loadu_pd directly.
- You want a maintained library: this is a 2-star benchmark repo with a one-line README and no tests beyond assert checks in the benchmarks.

## How it is fast

Numbers are unevaluated sums of 2 to 4 doubles (floating-point expansions), and each add or multiply is a fixed straight-line network of TwoSum, FastTwoSum and FMA-based TwoProd steps with no branches or renormalization loops (the paper calls these floating-point accumulation networks). With no data-dependent control flow, the same code instantiates on 2-, 4- and 8-wide SIMD registers; the dot and gemv kernels load 8 doubles per limb with _mm512_loadu_pd from split-array (one array per limb) storage, and axpy/gemm rely on '#pragma omp simd simdlen(8)'. The baselines (for example MPFR) are scalar per-element library calls on heap-allocated mpfr_t objects.

## Compared with alternatives

Pick this over DoubleFloats.jl or MPLAPACK's double-double/quad-double backends when you want C++ SIMD kernels at 2 to 4 doubles and can live with only + and \*; pick MultiFloats.jl if you work in Julia and need the full operation set, and MPFR-based tools (or LibBF, FLINT) when you need arbitrary precision or correct rounding.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for MultiFloats.hpp (x86 intrinsics headers only); the harness needs Google Benchmark, OpenMP, GMP, MPFR, CLN, FLINT, Boost.Multiprecision, QD and CAMPARY (fetched by download_campary.sh) |
| **Minimum toolchain** | C++17; the scripts use g++-14 and clang++-20 on Linux and Homebrew LLVM clang++ on macOS |
| **Platforms** | x86-64 with FMA and AVX-512F/DQ/VL for multifloats/MultiFloats.hpp; multifloats-arm/MultiFloats.hpp is a scalar-only variant (no NEON intrinsics) for aarch64 |
| **Thread safety** | Value types with no shared state; the benchmark kernels parallelize with OpenMP. Not otherwise documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The error-free transformations depend on exact IEEE evaluation order: the harness builds with -ffp-contract=off and never enables fast-math; reassociation would cancel the error terms.
- Results are not normalized or rounded like MPFR; equality operator== only compares against a scalar double (leading limb equal, lower limbs zero).
- The baseline MPFR runs use MPFR_RNDF (faithful rounding) with separate mpfr_mul and mpfr_add calls, so MPFR was not in correctly rounded mode in this harness either.
- The repo commits no benchmark output; bench_linux.sh writes Google Benchmark JSON per library at OMP_NUM_THREADS 32, 16, 8, 4, 2 and 1 for you to generate.

## Known shortcomings

- SC25 abstract claims up to 35.6x vs MPFR, but it compares peak against peak and MultiFloats is not correctly rounded like MPFR; CPUs (Ryzen 9 9950X, M3 Pro) known from a snippet only.
- The C++ header provides only + and \* (no sub/div/sqrt/compare/IO) and needs AVX-512F/DQ/VL unconditionally. Inf inputs turn into NaN. The MPFR baseline ran with MPFR_RNDF (faithful rounding), not correctly rounded. Paper unopened here.

## Caveats and trade-offs

Could not open the evidence: the SC '25 paper (Zhang and Aiken, 'High-Performance Branch-Free Algorithms for Extended-Precision Floating-Point Arithmetic', doi 10.1145/3712285.3759876, pp. 695-710) and its hosts (dl.acm.org, theory.stanford.edu, springer, dkzhang.com, purl.stanford.edu) were blocked; the speedup figures are from a search-result snippet of the abstract and the CPU model, thread count and kernel behind '35.6x' are unverified. The repo is only the harness: README is a one-line title and no benchmark JSON outputs are committed (bench_linux.sh writes MultiFloats-GCC-32.json style files at OMP_NUM_THREADS 32, 16, 8, 4, 2, 1 but none are in the tree), so a reader must build and run it (needs Google Benchmark, GMP, MPFR, CLN, FLINT, Boost, QD, CAMPARY via download_campary.sh) to reproduce. Comparison fairness: MultiFloats kernels are hand-vectorized on split arrays while MPFR and GMP are scalar per-element calls with per-thread temporaries; MPFR is correctly rounded with a huge exponent range. Tier B (peer-reviewed) rather than A because the CPU model and committed results could not be confirmed; if the paper states the CPU model and flags, A is justified since the harness and flags are public. The same algorithms are verified in Rocq (MultiFloatProofs) per the author profile.

Fixed expansions of 2 to 4 doubles (about 2x to 4x double precision, roughly 106 to 212 bits) with the exponent range of double; not arbitrary precision and not correctly rounded like MPFR. Header MultiFloats.hpp (multifloats/ folder) uses x86 SSE/AVX/AVX-512 intrinsics and an ARM variant (multifloats-arm) where NEON was disabled in the latest commits. Designed for data-parallel kernels; scalar single-operation latency gains are not the claim.

## Maintenance

Stale research harness (last commit 2025-08-27, 46 commits, 2 stars) under MIT, so the 373-line header is easy to vendor, but it is a paper artifact rather than a supported library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The numbers come from the peer-reviewed SC '25 paper (Zhang and Aiken, doi 10.1145/3712285.3759876); two independent search results quote its abstract (up to 11.7x QD, 34.4x CAMPARY, 35.6x MPFR, 41.4x FLINT) and name AMD Zen 5 (Ryzen 9 9950X) and Apple M3 Pro, but the paper hosts are blocked and the repo commits no results. The public harness (build_linux.sh: g++-14 / clang++-20 with stated flags; bench_linux.sh) would support A once the paper confirms CPU model and per-kernel numbers.
- **Verifier notes:** Repo metadata confirmed: MIT (LICENSE, 2025 David K. Zhang), 2 stars, 2 forks, last commit 2025-08-27 'disable small-number optimization in FLINT' (stale is right); README is one line; multifloats/ holds MultiFloats.hpp and main.cpp. dl.acm.org and theory.stanford.edu (author PDF) were blocked. Record shortcoming: speedups are peak-vs-peak from a blocked paper; MultiFloats is not correctly rounded and runs hand-vectorized split-array kernels while MPFR/FLINT run scalar per-element calls.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/dzhang314/MultiprecisionBenchmarks>
  - <https://github.com/dzhang314/MultiprecisionBenchmarks/commits>
  - <https://github.com/dzhang314/MultiprecisionBenchmarks/tree/main/multifloats>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/build_linux.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/bench_linux.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/dzhang314/MultiprecisionBenchmarks>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/build_linux.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/build_macos.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/bench_linux.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/download_campary.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats/MultiFloats.hpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats/main.cpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats-arm/MultiFloats.hpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/mpfr/main.cpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/README.md>
  - WebSearch: 'High-Performance Branch-Free Algorithms for Extended-Precision Floating-Point Arithmetic' SC25 (abstract snippets; theory.stanford.edu and dl.acm.org not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dzhang314/multiprecisionbenchmarks`) · [data/wave8/enrich/raw/github_com_dzhang314_multiprecisionbenchmarks.json](../../../data/wave8/enrich/raw/github_com_dzhang314_multiprecisionbenchmarks.json) (enrichment confidence 0.7)

</details>
