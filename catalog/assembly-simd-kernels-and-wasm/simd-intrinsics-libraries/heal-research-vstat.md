# vstat (SIMD descriptive statistics on EVE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 SIMD mean/variance/covariance/correlation on EVE; plots show 14-130x over GSL and Boost.Accumulators, near linasm.

| | |
|---|---|
| **Beats** | Boost.Accumulators 1.69, GNU Scientific Library 2.6, NumPy 1.19.4 and linasm statistics 1.13 |
| **Claimed result** | Plots only (log-scale op/s vs size, no numeric table); approximate readings at 1M elements, read from the plots, not page text: variance double vstat \~4.4e9 op/s, linasm \~4.4e9 (parity), Boost.Accumulators \~2.5e8 (\~17x), NumPy \~1.6e8 (\~27x), GSL \~8.5e7 (\~50x); variance float vstat \~1.1e10, linasm \~9e9 (\~1.2-1.3x), Boost \~2.8e8 (\~40x), NumPy \~1.6e8 (\~70x), GSL \~8.5e7 (\~130x); covariance double vstat \~3.2e9, linasm \~2.3e9 (\~1.4x), Boost \~2.3e8 (\~14x), GSL \~5.5e7 (\~60x), NumPy \~2.9e7 (\~110x); covariance float vstat \~6.5e9, linasm \~4.6e9 (\~1.4x), Boost \~1.8e8 (\~36x), GSL \~5.6e7 (\~115x), NumPy \~3e7 (\~220x). |
| **Workload** | Variance (univariate) and covariance (bivariate) of 1M uniform random float and double values, data size increased in 100k steps, nanobench ops per second. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X |
| **Adoption** | 20 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/heal-research/vstat) · [benchmark](https://raw.githubusercontent.com/heal-research/vstat/HEAD/README.md) |

## Verdict

First-party nanobench plots on an AMD Ryzen 9 5950X (2021, VCL-based implementation, compiler and flags not stated, uniform data in [-1, 1]) show, read off log-scale axes at 1M elements: double variance about equal to linasm 1.13 and about 17x Boost.Accumulators 1.69, 27x NumPy 1.19.4 (no MKL) and 50x GSL 2.6; float variance about 1.2-1.3x linasm, 40x Boost, 70x NumPy and 130x GSL; covariance about 1.4x linasm, 14-36x Boost, 60-115x GSL and 110-220x NumPy. No numeric table exists, and the current benchmark code (sizes 1,000 to 1M doubling, data in [0, 1), boost.math added, NumPy dropped) cannot regenerate the plots.

## Use it when

- Variance, covariance or correlation of large contiguous float or double arrays (thousands to millions of elements) in C++20 code that currently calls GSL gsl_stats_\* or loops a Boost.Accumulators accumulator_set.
- When you need a single pass with a numerically stable algorithm (Youngs-Cramer per lane plus Schubert-Gertz merging) rather than a naive sum-of-squares, e.g. data with a large mean relative to its spread.
- Weighted statistics: weighted mean, variance and covariance run on the same SIMD path, whereas Boost.Accumulators and GSL provide them only as scalar code and the repo's linasm wrapper has no weighted variant.
- Streaming or chunked data: SIMD accumulator objects can be fed vectors as data arrives and merged, with a scalar accumulator for left-over elements.
- Regression or ML evaluation loops needing MSE, MAE or Gaussian/Poisson negative log-likelihood with nan_policy::omit to skip non-finite pairs.

## Skip it when

- When you need long-double-grade accuracy: accumulate&lt;float&gt; keeps per-lane counts, sums and squared deviations in float, whereas GSL accumulates in long double; use accumulate&lt;double&gt; or GSL when the last digits matter.
- Very large float inputs: each float lane counts elements in a float, which stops incrementing at 2^24 = 16,777,216 per lane (about 134M elements with 8 float lanes, 67M with 4), after which count, mean and variance are wrong; correctness tests only go up to 100,000 elements.
- Toolchains without C++20: EVE needs g++ 13+, clang++ 16+ or MSVC 19.44+, despite the README still saying C++17 (acknowledged in open issue #1).
- If you already use linasm on x86-64: the plots show a tie on double variance and only about 1.2-1.4x on float variance and covariance.
- If you need published numbers for the code you will actually ship: the only benchmark data predates the 2026 EVE rewrite and was produced by the earlier Vector Class Library implementation.

## How it is fast

Each SIMD lane runs its own Youngs-Cramer update (running weighted sum plus a sum of squared deviations updated with dx\*dx/(n\*(n-1))), so the whole array is processed in one pass of vector adds, multiplies and one vector divide per element group, with no separate mean pass. At the end the per-lane partial results are merged with the Schubert-Gertz pairwise combination formula and the tail is finished by a scalar accumulator seeded from the merged state. The baselines it beats by large factors are scalar and precision-first: GSL's float and double routines run a long-double recurrence with a division per element in each of two passes, and Boost.Accumulators' tag::variance does two divisions per sample; linasm, the hand-vectorised competitor, is close.

## Compared with alternatives

Pick vstat when you want ready-made, numerically stable variance/covariance/correlation reductions; EVE and the Vector Class Library are the general SIMD layers it is built on (now and formerly) and ship no statistics, while ParallelReductionsBenchmark only covers plain sums against std::accumulate.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | EVE (find_package(eve REQUIRED), C++20 SIMD library). Tests and benchmarks additionally need Catch2 3, GSL, Boost (Accumulators and Math), linasm (x86-64 only, via pkg-config) and the vendored nanobench header; the optional Python module needs nanobind. |
| **Minimum toolchain** | C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20); EVE minimums g++ 13, clang++ 16, MSVC 19.44; CMake 3.20. |
| **Platforms** | Whatever EVE targets: x86 SSE2 to AVX2/FMA3 and AVX-512 (Skylake-AVX512), ARM NEON/ASIMD and fixed-size SVE, partial PowerPC VMX/VSX. Vector width is a compile-time constant (eve::wide&lt;T&gt;::size()), so it follows your -march flags; the project's presets set none and its Nix package builds with -march=x86-64 (SSE2 only). |
| **Thread safety** | not documented; the accumulate() functions only read their inputs and keep state in local accumulators, while accumulator objects are plain unsynchronised value types |
| **Drop-in for the baseline** | partial — the same statistics in a few lines, but the API differs from GSL, Boost.Accumulators and NumPy: results come back as a struct, the 'variance' field is the population variance (sample_variance is separate, whereas gsl_stats_variance returns the sample variance) and float inputs are accumulated in float rather than GSL's long double. |

## Gotchas

- Stale and mismatched evidence: the four README plots were committed on 2021-11-15 (commit 2796c53), when vstat was built on the Vector Class Library with hard-coded Vec8f/Vec4d types (include/vstat/combine.hpp included vectorclass/vectorclass.h and README reference [1] was VCL). The current README credits EVE for the same unchanged plots, and the 2026 EVE code, whose width depends on compile flags, has never had published numbers.
- Precision asymmetry behind the large ratios: the 50-130x over GSL and 14-40x over Boost.Accumulators compare a vectorised one-pass float or double accumulator against scalar code that does per-element divisions (GSL in long double, over two passes; Boost with two fdiv per sample). linasm's timing includes one or two extra mean passes (three passes for covariance), and the NumPy rows have no harness in test/ at the plot commit or at HEAD, so how NumPy was called is not documented.
- The Python binding (src/vstat.cpp) routes double arrays through accumulate&lt;float&gt;, so NumPy float64 input is computed in single precision, and its weighted mean, variance and sample_variance overloads return the whole statistics object rather than the scalar.
- The current benchmark TEST_CASE adds each result to a local double m that is never passed to nanobench's doNotOptimizeAway; GSL and linasm are opaque library calls, but the header-only vstat and Boost paths are only kept alive by the compiler not seeing through nanobench's run loop. The plotted 2021 harness had the same pattern (results added to a local var).

## Known shortcomings

- Plots only (approximate readings: about 17-40x Boost.Accumulators, 27-220x NumPy, 50-130x GSL) and it ties linasm on double variance, about 1.2-1.4x ahead on the other three plots; no compiler or flags; the November 2021 plots cannot be regenerated from the current benchmark (no NumPy, different sizes and data range).
- Provenance flaw: the README plots come from commit 2796c53 (2021-11-15), a Vector Class Library build with hard-coded Vec8f/Vec4d, while the README now credits EVE for the same plots; the 2026 EVE code has no published numbers. The 14-130x ratios are against scalar per-element-division baselines (GSL in long double over two passes, Boost.Accumulators with two fdiv per sample); no NumPy harness exists; results are added to a local double never passed to doNotOptimizeAway; the float accumulator saturates at 2^24 per lane; the Python binding computes float64 arrays as accumulate&lt;float&gt;.

## Caveats and trade-offs

README gives methodology and CPU but no compiler, flags or numeric table; the four PNG plots are the only results and the figures are approximate readings of log-scale axes. The plots were last committed in November 2021 (Boost 1.69, NumPy 1.19.4 era) and predate the 2026 rewrites of the EVE code; the current benchmark TEST_CASE in test/source/vstat_test.cpp no longer includes NumPy, adds boost.math, uses sizes 1000 to 1M doubling and data in [0,1) rather than the README's 100k steps over [-1,1], so the plots cannot be regenerated from the current code. The presets set no -march flag (Release defaults only), so the SIMD width used for the plots is unknown. vstat ties linasm on double variance and is about 1.2-1.4x faster on the other three plots. MKL was not used for NumPy and GSL (README note); NumPy is measured through Python call overhead; linasm needs precomputed means that were included in its timing; Boost.Accumulators variance is a scalar streaming accumulator. README says C++17 but CMakeLists.txt now requires C++20. [retier] README gives methodology and CPU but no compiler, flags or numeric table; the four PNG plots are the only results and the figures are approximate readings of log-scale axes. Provenance: the plots were committed on 2021-11-15 (commit 2796c53) when vstat was built on the Vector Class Library with hard-coded Vec8f/Vec4d types; the README now credits EVE for the same unchanged plots, and the 2026 EVE code (width set by compile flags, no -march in the presets) has no published numbers. The 50-130x over GSL and 14-40x over Boost.Accumulators compare a vectorised one-pass accumulator against scalar code doing per-element divisions (GSL in long double over two passes, Boost with two fdiv per sample); linasm's timing includes its extra mean passes; no NumPy harness exists in test/ at the plot commit or at HEAD; MKL was not used. The benchmark adds results to a local double never passed to nanobench's doNotOptimizeAway. The float accumulator saturates at 2^24 elements per lane. The Python binding computes float64 arrays as accumulate&lt;float&gt;. vstat ties linasm on double variance and is about 1.2-1.4x faster on the other three plots. README says C++17 but CMakeLists.txt requires C++20.

C++20; built on the EVE SIMD library (itself catalogued); header-only; data-parallel Youngs-Cramer sums combined with Schubert-Gertz; scalar accumulators available when no SIMD type is used.

## Maintenance

Actively maintained (commits through 2026-09-16, with stats-level flags, nan_policy and NLL metrics added in 2026) and MIT-licensed header-only code that is easy to vendor, but the README's C++17 claim is wrong (C++20 plus EVE needed) and the only performance evidence is the 2021 pre-EVE plots.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party plots in the README (test/benchmarks/\*.png) compare vstat against Boost.Accumulators, GSL, NumPy and linasm on a stated CPU (Ryzen 9 5950X), but no compiler or flags are given, there is no numeric table, and the current benchmark code (TEST_CASE "benchmarks" in test/source/vstat_test.cpp) no longer matches the plotted runs, so it cannot be A.
- **Verifier notes:** Real first-party comparison against Boost.Accumulators, GSL and NumPy with large ratios; tier C stands (no compiler or flags, stale plots that the current benchmark code does not reproduce). Corrected claimed_speedup to cover all four plots: vstat is not only tied with linasm, it is about 1.2-1.4x ahead except on double variance. Metadata checked: MIT (copyable), 20 stars, 3 forks, last commit 2026-09-16 (active), not a fork or archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-113 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/README.md>
  - <https://github.com/heal-research/vstat>
  - <https://github.com/heal-research/vstat/commits>
  - <https://github.com/heal-research/vstat/commits/main/test/benchmarks>
  - <https://github.com/heal-research/vstat/tree/main/test>
  - <https://github.com/heal-research/vstat/tree/main/test/source>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/benchmarks/var_double.png>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/benchmarks/var_float.png>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/benchmarks/cov_double.png>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/benchmarks/cov_float.png>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/cmake/dev-mode.cmake>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/source/vstat_test.cpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/source/stat_other.hpp>
- **Sources the enricher read:**
  - <https://github.com/heal-research/vstat>
  - <https://github.com/heal-research/vstat/commits>
  - <https://github.com/heal-research/vstat/commits/main/test/benchmarks>
  - <https://github.com/heal-research/vstat/issues?q=is%3Aissue>
  - <https://github.com/heal-research/vstat/issues/1>
  - <https://github.com/heal-research/vstat/tree/main/include/vstat>
  - <https://github.com/heal-research/vstat/tree/2796c53/test>
  - <https://github.com/heal-research/vstat/tree/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/test/benchmarks>
  - <https://github.com/heal-research/vstat/tree/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/test/source>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/README.md>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/.github/workflows/build-linux.yml>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/cmake/dev-mode.cmake>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/source/vstat_test.cpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/test/source/stat_other.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/vstat.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/univariate.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/bivariate.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/combine.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/compensated_sum.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/include/vstat/util.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/HEAD/src/vstat.cpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/README.md>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/test/source/vstat_test.cpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/include/vstat/vstat.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/include/vstat/univariate.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/include/vstat/util.hpp>
  - <https://raw.githubusercontent.com/heal-research/vstat/2796c5358c74bfcbeaf8d0411f7d6452b55cf912/include/vstat/combine.hpp>
  - <https://raw.githubusercontent.com/ampl/gsl/master/statistics/mean_source.c>
  - <https://raw.githubusercontent.com/ampl/gsl/master/statistics/variance_source.c>
  - <https://raw.githubusercontent.com/ampl/gsl/master/statistics/covariance_source.c>
  - <https://raw.githubusercontent.com/boostorg/accumulators/develop/include/boost/accumulators/statistics/variance.hpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/README.md>
  - <https://pypi.org/pypi/vstat/json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/heal-research/vstat`) · [data/wave13/enrich/raw/github_com_heal_research_vstat.json](../../../data/wave13/enrich/raw/github_com_heal_research_vstat.json) (enrichment confidence 0.8)

</details>
