# HyperJet (hyper-dual number automatic differentiation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++23 hyper-dual numbers giving value, gradient and dense Hessian in one pass; 1.2-3.3x faster than Eigen AutoDiffScalar/autodiff.

| | |
|---|---|
| **Beats** | Eigen AutoDiffScalar (nested), autodiff (dual2nd) and ceres::Jet |
| **Claimed result** | Second order, static size: HyperJet 101 ns vs Eigen AutoDiffScalar nested 328 ns and autodiff dual2nd 375 ns at n=6 (3.3x vs the faster of the two); 921 vs 2888 and 2425 ns at n=12 (2.6x); 12,214 vs 22,105 and 17,679 ns at n=24 (1.5x); 15 vs 18 and 127 ns at n=3 (1.2x). First order (gradient only) there is no winner: HyperJet 244 ns vs AutoDiffScalar 245 ns vs ceres::Jet 304 ns at n=24. |
| **Workload** | Value, gradient and dense Hessian of a cable strain-energy sum (n = 3, 6, 12, 24 variables), median ns per evaluation over 7 repetitions with Google Benchmark. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro, macOS 26.5; Eigen 3.4.0, autodiff v1.1.2, Ceres 2.2.0 |
| **Compiler and flags** | Apple clang 21.0.0, -O3 -DNDEBUG (Release CMake build; benchmark verifies identical values, gradients and Hessians before timing) |
| **Adoption** | 17 stars |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/oberbichler/HyperJet) · [benchmark](https://github.com/oberbichler/HyperJet#performance) |

## Verdict

The author's Google Benchmark harness (benchmark/compare/compare.cpp, Apple clang 21.0.0 -O3 -DNDEBUG on an Apple M1 Pro, Eigen 3.4.0, autodiff v1.1.2, Ceres 2.2.0) times value, gradient and dense Hessian of a cable strain-energy sum: static HyperJet takes 15/101/921/12,214 ns at n=3/6/12/24 against 18/328/2,888/22,105 ns for nested Eigen AutoDiffScalar and 127/375/2,425/17,679 ns for autodiff dual2nd, after checking all contenders agree bit-for-bit. For gradients alone it ties Eigen AutoDiffScalar and is about 1.25x faster than ceres::Jet at n=24.

## Use it when

- Element-level Hessians in nonlinear finite-element, isogeometric or cable/shell mechanics codes, where each element has a small, compile-time-known number of DOFs (roughly 3-24).
- Newton-type solvers that need exact local Hessians of small dense functions evaluated many times (strain energies, constitutive laws).
- Python prototyping of second-derivative code: static types back a NumPy dtype, which the README measured at 52x-246x faster than dtype=object arrays for elementwise ops.
- Assembly code that wants derivatives keyed by variable name and projected onto a caller-chosen global ordering (SSScalar g(names)/hm(names)).

## Skip it when

- Gradient-only work: the README's own first-order table shows no gain over Eigen AutoDiffScalar (244 vs 245 ns at n=24), and Ceres Jet comes with a solver.
- Variable counts unknown at compile time: the dynamic variant allocates per operation and was 43x slower than static at n=3, and slower than both Eigen AutoDiffScalar nested and autodiff dual2nd at every tested size in the second-order table.
- Many inputs or large n: forward-mode cost and the dense Hessian grow quadratically, and the speedup already narrows to 1.5x at n=24; reverse-mode tools (Adept, XAD) suit scalar functions of hundreds of inputs.
- Toolchains older than GCC 14 / Clang 18 / MSVC 19.38: the header uses C++23 explicit object parameters ('deducing this').
- Projects needing third derivatives or sparse Hessians within a set of variables: only first and second order are provided, and SSScalar's Hessian is dense over the names it carries.

## How it is fast

Hyper-dual (truncated second-order Taylor) arithmetic propagates the gradient and Hessian through each operation via the chain rule, so the Hessian comes from one evaluation rather than nested first-order duals (Eigen AutoDiffScalar of AutoDiffScalar) or n(n+1)/2 re-evaluations (autodiff dual2nd's hessian()). The Hessian is stored as a packed upper triangle in a fixed-size std::array, all operators are force-inlined, and constant partials (zero, one, minus one) are compile-time tags that fold away. Above 8 variables the gradient and Hessian are updated in one fused pass over the data array, a threshold the source comments say was measured on an M1 Pro (n=16 35% faster fused, n=6 14% slower).

## Compared with alternatives

Pick HyperJet over Adept-2, XAD or FastAD when you need exact dense Hessians of small fixed-size functions, since those tape-based tools target first-order reverse mode over many inputs (Adept has no higher-order mode). Sleipnir bundles its own AD with an NLP solver and Enzyme needs an LLVM plugin; neither is a lightweight per-element Hessian scalar.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for C++ (standard library only); Python bindings need pybind11, scikit-build-core and NumPy &gt;= 2.0 |
| **Minimum toolchain** | C++23; GCC 14+, Clang 18+, MSVC 19.38+ (README); CMake 3.14+ for the provided target |
| **Platforms** | any (portable C++; benchmarks only on Apple M1 Pro) |
| **Thread safety** | not documented (scalars are value types with no shared state in the header) |
| **Drop-in for the baseline** | partial — same template-scalar style as Eigen AutoDiffScalar or ceres::Jet, so a templated function can switch types, but the accessors (f(), g(i), h(i,j), variables()) differ and Eigen-specific traits are not provided. |

## Gotchas

- pip install hyperjet installs 1.5.0 from August 2023, not the benchmarked C++23 code; the README's CPM line pins HyperJet@2.0.0, but the tags page shows no 2.0.0 tag (latest v1.5.0), so pin a commit on main to get the rewrite (C++23 switch landed May 2026, benchmark July 2026).
- C++ accessors g(i), h(i), h(i,j) are only checked by assert in debug builds; constructors and resize/eval paths throw std::runtime_error unless HYPERJET_NO_EXCEPTIONS is defined.
- References returned by data() from a temporary expression are valid only within the full expression, as with std::vector::operator[].
- Performance depends on inlining: the README measured a 1.56x penalty for HyperJet (similar for Eigen and Ceres) when the enclosing expression is not inlined, and writing acc += term instead of acc = acc + term saved 8% at n=24.

## Known shortcomings

- No gain for gradient-only work (the win is in second derivatives).
- 'pip install hyperjet' gives 1.5.0 (2023), not the benchmarked C++23 code; README's CPM pin @2.0.0 points at a tag that does not exist (latest v1.5.0), and the rewrite is untagged on main; single-machine author benchmark.

## Caveats and trade-offs

Author-run benchmark on a single Apple Silicon machine, but the benchmark code (benchmark/compare/compare.cpp) is in the repository, pins dependency versions, and verifies that every contender produces the same value, gradient and Hessian before timing. The README is candid that there is no gain for gradient-only work (HyperJet 244 vs AutoDiffScalar 245 vs ceres::Jet 304 ns at n=24) and that the dynamic-size HyperJet variant is far slower (644 ns at n=3, 22,777 ns at n=24). The Eigen baseline is AutoDiffScalar from Eigen's unsupported module, not Eigen Tensor. compare.cpp forces always_inline uniformly for all contenders because inlining decisions change absolute times by about 1.6x. Small project (17 stars); library requires C++23.

Header-only C++23 (Python bindings via pybind11); the fast variant needs the variable count at compile time, while the dynamic-size variant is 1.9x to 43x slower than the static one in the README's own text and, in its second-order table, is slower than both Eigen AutoDiffScalar and autodiff dual2nd at every size tested (n=3 to 24).

## Maintenance

Actively developed by a single author (C++23 rewrite in May 2026, last commit 2026-07-28, 17 stars) under MIT, small enough to vendor as one header, but the rewritten version has no tagged release or PyPI package yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance section gives the second-order table (HyperJet static 15/101/921/12,214 ns vs Eigen AutoDiffScalar nested 18/328/2,888/22,105 and autodiff dual2nd 127/375/2,425/17,679) and the first-order table, measured on an Apple M1 Pro with Apple clang 21.0.0 -O3 -DNDEBUG; the benchmark code is public at benchmark/compare/compare.cpp (Compare target in benchmark/CMakeLists.txt, Google Benchmark 1.9.1, Eigen 3.4.0, autodiff v1.1.2, Ceres 2.2.0) and checks all contenders agree before timing.
- **Verifier notes:** All claimed numbers match the README tables exactly; ratios 3.3x (n=6), 2.6x (n=12), 1.5x (n=24), 1.2x (n=3) are the README's own. Metadata checked on github.com: MIT, 17 stars, not archived, not a fork, last commit 2026-07-28 (benchmark added that day in PR #90).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/README.md>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/benchmark/compare/compare.cpp>
  - <https://github.com/oberbichler/HyperJet>
  - <https://github.com/oberbichler/HyperJet/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/README.md>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/include/hyperjet/hyperjet.h>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/benchmark/compare/compare.cpp>
  - <https://raw.githubusercontent.com/oberbichler/HyperJet/HEAD/benchmark/CMakeLists.txt>
  - <https://github.com/oberbichler/HyperJet>
  - <https://github.com/oberbichler/HyperJet/issues?q=is%3Aissue>
  - <https://github.com/oberbichler/HyperJet/issues/59>
  - <https://github.com/oberbichler/HyperJet/tags>
  - <https://github.com/oberbichler/HyperJet/commits>
  - <https://pypi.org/pypi/hyperjet/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/oberbichler/hyperjet`) · [data/wave8/enrich/raw/github_com_oberbichler_hyperjet.json](../../../data/wave8/enrich/raw/github_com_oberbichler_hyperjet.json) (enrichment confidence 0.8)

</details>
