# Sleipnir

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++23 reverse-mode autodiff plus Newton/SQP/interior-point NLP solver DSL; sets up and solves small optimal-control problems faster than CasADi+Ipopt.

| | |
|---|---|
| **Beats** | CasADi 3.8.0 (autodiff and NLP frontend) with Ipopt 3.14.20 and MUMPS 5.8.1 |
| **Claimed result** | Flywheel (ratios derived from page data CSVs): at 1000 samples solve 11.088 ms vs 59.015 ms (about 5.3x) and setup 0.368 ms vs 19.184 ms; at 5000 samples solve 75.124 ms vs 339.385 ms (about 4.5x) and setup 1.961 ms vs 91.157 ms. Cart-pole: setup 2.147 ms vs 194.851 ms at 300 samples, but solve is NOT faster there (2683.45 ms vs 1251.01 ms at 300 samples). |
| **Workload** | Optimal-control NLP scalability benchmarks (flywheel with 100-5000 samples, cart-pole with 100-300 samples): problem setup time and solve time of Sleipnir's reverse-mode autodiff plus interior-point solver versus CasADi plus Ipopt. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 7840U, 64 GB DDR5-5600 |
| **Compiler and flags** | g++ (GCC) 16.2.1 20260810. The README build command (cmake -B build -S . -DSLEIPNIR_BUILD_BENCHMARKS=ON) sets no build type, so the root CMakeLists.txt default RelWithDebInfo applies (CMake's GCC default -O2 -g -DNDEBUG), with -Wall -Wextra -pedantic and C++23 from cmake/CompilerFlags.cmake; no -march. The build flags of the CasADi, Ipopt and MUMPS binaries are not stated. |
| **Adoption** | 80 stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/SleipnirGroup/Sleipnir) · [benchmark](https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/README.md) |

## Verdict

The project's own scalability benchmark (g++ 16.2.1, CMake default RelWithDebInfo, AMD Ryzen 7 7840U) compares Sleipnir with default options against CasADi 3.8.0 + Ipopt 3.14.20 + MUMPS 5.8.1 with tuned options: on the flywheel problem, solve is about 5.3x faster at 1000 samples (11.1 vs 59.0 ms) and 4.5x at 5000 (75.1 vs 339.4 ms) with setup 40-50x faster, but on cart-pole only setup wins and the solve is about 2x slower at 300 samples (2683 vs 1251 ms). This times a whole modelling+AD+solver stack, not AD alone.

## Use it when

- Small to medium trajectory-optimization or model-predictive-control NLPs (hundreds to a few thousand stages) where problem setup time matters, e.g. re-building and solving each control cycle; flywheel setup was 0.37 ms vs 19.2 ms for CasADi at 1000 samples.
- Robotics code (the project comes out of the FRC robotics community) that wants a permissively licensed, dependency-light solver that cross-compiles via CMake toolchain files, since Eigen is the only heavy dependency.
- Problems with many linear or quadratic constraints, where cached constant derivatives remove most per-iteration AD work.
- When you want one modelling-plus-solver API in both C++ and Python, or need a non-double scalar type (the C++ API is templated for higher-precision types).

## Skip it when

- Harder nonlinear problems where solver robustness dominates: on cart-pole Sleipnir's solve time was slower than CasADi+Ipopt+MUMPS from 150 samples up (3065 vs 974 ms at 250 samples; 2683 vs 1251 ms at 300).
- If you need fast standalone derivatives: the AD is tree-based with dynamic dispatch and an open issue (#660) calls it too slow for embedded use; the benchmark never isolates AD speed.
- Large-scale NLPs that benefit from commercial sparse linear solvers (HSL MA27/MA57) in Ipopt; the benchmark README notes those may make Ipopt much faster than with MUMPS.
- Toolchains older than GCC 14 / Apple Clang 16 / Visual Studio 2022 17.13: the library requires C++23.
- Projects that need a stable versioned API: the README's FetchContent snippet tracks GIT_TAG main and PyPI is on 0.6.x with frequent dev builds.

## How it is fast

The autodiff graph records the linearity of every node (constant, linear, quadratic, nonlinear), so constant first and second derivatives are computed once at initialization and only nonlinear subgraphs are re-evaluated each iteration; quadratic problems get their Lagrangian Hessian and constraint Jacobians once without user hints. Expression nodes come from a thread-local pool allocator and are freed through intrusive reference counts with an iterative (non-recursive) teardown. Equality and inequality constraints are distinct types so setup dispatch happens at compile time, and Eigen's sparse matrices and a regularized LDLT factorization handle the KKT systems.

## Compared with alternatives

Pick Sleipnir when the job is solving a constrained NLP end to end; Adept-2, XAD, FastAD and Enzyme only give you derivatives and leave the solver to you, and HyperJet gives dense small Hessians. If you only need gradients inside your own code, those siblings are the better fit.

## Integration

| | |
|---|---|
| **Form** | shared lib (BUILD_SHARED_LIBS defaults ON; static possible) via CMake FetchContent |
| **Dependencies** | Eigen (fetched at a pinned commit unless SLEIPNIR_USE_SYSTEM_EIGEN), gharveymn/small_vector; nanobind for Python bindings; Catch2 for tests |
| **Minimum toolchain** | C++23; GCC 14 libstdc++ (Ubuntu 24.04), Apple Clang 16.0.0 (Xcode 16.2), MSVC from Visual Studio 2022 17.13; CMake 3.21+ |
| **Platforms** | Windows 11, Ubuntu 24.04, macOS 14.5 (universal arm64/x86_64); PyPI wheels for Linux x86_64/aarch64, macOS universal2, Windows amd64/arm64 |
| **Thread safety** | not documented; the source shows a thread-local expression pool (disabled on Windows because thread-local statics are not reliably initialized across DLL boundaries) and non-atomic node reference counts, so build and solve each Problem on one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- The default CMake build type is RelWithDebInfo (-O2 -g), which is also what the published benchmark used; set CMAKE_BUILD_TYPE=Release explicitly if you want -O3.
- solve() returns an ExitStatus (e.g. LOCALLY_INFEASIBLE, FACTORIZATION_FAILED, LINE_SEARCH_FAILED, DIVERGING_ITERATES, MAX_ITERATIONS_EXCEEDED, TIMEOUT) instead of throwing; check it. Defaults are tolerance 1e-8 and 5000 max iterations.
- Memory-safety history: issue #1193 (May 2026) found heap corruption in RegularizedLDLT::compute_sparse when two KKT matrices had the same nnz but different sparsity patterns (symbolic factorization cached by nnz only), fixed in PR #1198; aarch64-only test failures ('factorization failed', 'diverging iterates', issues #803/#804) were closed in March 2026.
- The benchmark README tells you to run ./tools/generate-scalability-results.sh, but the script lives at benchmarks/generate-scalability-results.sh.

## Known shortcomings

- Cart-pole solve is slower than CasADi from 150 samples up; flags come from the CMake RelWithDebInfo default (-O2 -g); baseline CasADi is not a category incumbent.
- Heap corruption in RegularizedLDLT::compute_sparse (issue #1193, May 2026, fixed in PR #1198); AD speed is not isolated and open issue #660 says the AD is too slow for embedded use; cart-pole solve about 2x slower than CasADi; measured workload is a full NLP solve.

## Caveats and trade-offs

Compares a full AD plus interior-point stack against CasADi plus Ipopt plus MUMPS, so AD speed alone is not isolated. CasADi uses tuned options (expand=true, constant Hessian/Jacobian hints on flywheel) while Sleipnir uses defaults. Sleipnir's cart-pole solve times are slower than CasADi from 150 samples up (for example 3065.18 ms vs 973.846 ms at 250 samples; the Sleipnir cart-pole CSV has no 200-sample row), possibly because of different iteration counts. Flags come from the CMake default build type rather than a listed flag string, and the README's run step names ./tools/generate-scalability-results.sh while the script actually lives at benchmarks/generate-scalability-results.sh. Author's own benchmark; the README notes commercial linear solvers could make Ipopt much faster.

C++23 with Python bindings; pool-allocated expression-node reverse-mode autodiff that records linearity to cache constant derivatives; uses Eigen sparse solvers; the NLP DSL picks the solver from problem structure. It is an AD-plus-NLP-solver stack, not a general tensor autodiff library.

## Maintenance

Very active (last commit 2026-09-27, dev wheels weekly, 80 stars, BSD-3-Clause), with a pre-1.0 API and tracking of main recommended by the README, so pin a commit when vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/README.md links per-size CSVs for Sleipnir and CasADi+Ipopt+MUMPS, generated by benchmarks/generate-scalability-results.sh from public sources in benchmarks/scalability/{flywheel,cart_pole}; it states g++ (GCC) 16.2.1 and an AMD Ryzen 7 7840U, and its build command sets no build type, so the root CMakeLists.txt default RelWithDebInfo (CMake GCC default -O2 -g -DNDEBUG) plus -Wall -Wextra -pedantic and C++23 from cmake/CompilerFlags.cmake fixes the flags. This follows the wave-1 precedent that a CMake default build type counts as stated flags.
- **Verifier notes:** All eight claimed numbers match the CSVs exactly (flywheel 1000 and 5000 samples, cart-pole 300 samples). Metadata checked on github.com: BSD-3-Clause (LICENSE.txt), 80 stars, not a fork or archived, last commit 2026-09-27. Fits autodiff-and-ml-kernels as an AD library, though the measured workload is a full NLP solve (sparse-and-solvers would also fit).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/flywheel-scalability-results-casadi.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/flywheel-scalability-results-sleipnir.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/cart-pole-scalability-results-casadi.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/cart-pole-scalability-results-sleipnir.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/cmake/BuildTypes.cmake>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/cmake/CompilerFlags.cmake>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/generate-scalability-results.sh>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/LICENSE.txt>
  - <https://github.com/SleipnirGroup/Sleipnir>
  - <https://github.com/SleipnirGroup/Sleipnir/commits>
  - <https://github.com/SleipnirGroup/Sleipnir/tree/main/benchmarks/scalability>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/README.md>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/flywheel-scalability-results-casadi.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/flywheel-scalability-results-sleipnir.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/cart-pole-scalability-results-casadi.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/benchmarks/cart-pole-scalability-results-sleipnir.csv>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/cmake/CompilerFlags.cmake>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/include/sleipnir/autodiff/expression.hpp>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/include/sleipnir/autodiff/variable.hpp>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/include/sleipnir/optimization/problem.hpp>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/include/sleipnir/optimization/solver/options.hpp>
  - <https://raw.githubusercontent.com/SleipnirGroup/Sleipnir/HEAD/include/sleipnir/optimization/solver/exit_status.hpp>
  - <https://github.com/SleipnirGroup/Sleipnir>
  - <https://github.com/SleipnirGroup/Sleipnir/issues?q=is%3Aissue>
  - <https://github.com/SleipnirGroup/Sleipnir/issues/1193>
  - <https://github.com/SleipnirGroup/Sleipnir/issues/660>
  - <https://pypi.org/pypi/sleipnirgroup-jormungandr/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sleipnirgroup/sleipnir`) · [data/wave8/enrich/raw/github_com_sleipnirgroup_sleipnir.json](../../../data/wave8/enrich/raw/github_com_sleipnirgroup_sleipnir.json) (enrichment confidence 0.8)

</details>
