# FastAD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 expression-template AD library; author reports 2-10x over Adept and 2-19x over Stan Math gradients.

| | |
|---|---|
| **Beats** | Adept, Stan Math, ADOL-C, CppAD, Sacado (C++ AD libraries) |
| **Claimed result** | Paper abstract: '2-10 times faster than Adept and 2-19 times faster than Stan across various test cases'; e.g. sum: Adept \~10x and Stan \~15x slower; normal log-PDF: Adept \~9x, Stan \~19x slower; Bayesian linear regression: 8.6x vs Stan and 10x vs Adept at largest N. README: 'over orders of magnitude improvement' (not supported by the paper's 2-19x). |
| **Workload** | Forward and reverse-mode gradient evaluation of expression-template AD on sum, product, log-sum-exp, matrix ops, normal log-pdf, regression and stochastic-volatility models. |
| **Metric** | throughput |
| **Hardware** | Google Cloud VM, Ubuntu 18.04.1, 'Intel Xeon Processor', 8 cores (model not stated) |
| **Compiler and flags** | GCC10, C++17, -O3 -march=native (per arXiv 2102.03681); ADBenchmark README says it was tested on macOS Catalina with GCC10 |
| **Adoption** | 122 stars |
| **Last commit** | 2023-09-27 |
| **Links** | [repository](https://github.com/JamesYang007/FastAD) · [benchmark](https://arxiv.org/abs/2102.03681) |

## Verdict

In the author's unrefereed arXiv preprint (2102.03681), built with GCC 10, C++17, -O3 -march=native on an 8-core Google Cloud Xeon VM (model not stated), FastAD's gradient time beat Adept 2.0.8 and Stan Math 3.3.0 by about 10x/15x (sum), 2.5x/7.7x (log-sum-exp), 9x/19x (normal log-pdf), 10x/8.6x (Bayesian regression) and 2x/2.6x (stochastic volatility). Matrix product was roughly a tie with Adept. The harness is public (JamesYang007/ADBenchmark, tested only on macOS Catalina). The README's 'orders of magnitude' claim is not supported by these numbers.

## Use it when

- Repeated gradient evaluation of a fixed-structure scalar objective (MCMC/HMC log-densities, MLE, regression likelihoods) where the graph is built once and re-evaluated with new inputs.
- Vectorized objectives over Eigen vectors/matrices (sums, log-sum-exp, normal log-pdf), where the paper shows the largest gaps (about 9-19x vs Stan, 9-10x vs Adept).
- Projects already using Eigen 3.3 and C++17 that want a small, MIT-licensed header-only AD dependency.
- First-order gradients only, on x86-64 with -O3 -march=native.

## Skip it when

- Data-dependent dynamic graphs (graph shape changes per call, arbitrary loops/branches on runtime values): you must restate them with if_else/for_each, which a tape-based library (Adept, XAD, CppAD) handles naturally.
- Higher-order derivatives, Jacobians of vector functions, sparse matrices or checkpointing: not supported (open issues #75, #101, #109, #28; the paper calls higher order 'a great challenge').
- Workloads dominated by dense matrix products: the paper shows FastAD only comparable to Adept and about 2x over Stan there.
- Production use needing a maintained library: last commit Sept 2023, and the paper says function/distribution/decomposition coverage is incomplete.
- Builds with GCC 16 at -O3 until PR #111 lands (see gotchas).

## How it is fast

There is no runtime tape. The computation graph is a compile-time expression template (no virtual calls, no per-node heap allocation), and the exact value/adjoint storage size is computed up front so one contiguous block is allocated ('lazy allocation'). Vector/matrix variables store 'a pair of pointers to a matrix of doubles' instead of a matrix of (value, adjoint) pairs, so Eigen can emit packed SIMD (the paper shows vaddpd vs Stan's scalar vaddsd). C++17 if constexpr/SFINAE detects constant arguments and precomputes things like sufficient statistics in normal log-pdf.

## Compared with alternatives

Pick FastAD over XAD when the objective is a fixed, Eigen-vectorized statistical model and you want the smallest header-only dependency. Pick XAD when you need a maintained, tape-based library that handles arbitrary C++ control flow, higher-order modes and checkpointing.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen 3.3 (GoogleTest and Google Benchmark for dev builds only) |
| **Minimum toolchain** | C++17; benchmarks used GCC 10; developed mainly with Clang; CMake package (FastAD::FastAD) or FetchContent of tag v3.2.1 |
| **Platforms** | any platform Eigen supports; CI on Linux and macOS; benchmarked on x86-64 only |
| **Thread safety** | not documented; expressions bind to mutable value/adjoint buffers, so treat each bound expression and its Vars as single-threaded |
| **Drop-in for the baseline** | partial — the arithmetic syntax resembles Adept/Stan, but code must be rewritten into bound expression objects with explicit placeholders and seeds |

## Gotchas

- Evaluating an expression that was never bound to storage segfaults (README warns explicitly); use ad::bind(...) unless you manage buffers yourself.
- Adjoints accumulate: call reset_adj() on every Var, placeholders included, before differentiating again or gradients are wrong.
- Open issue #110 (2026): with g++-16 at -O3, RcppFastAD examples segfault in memcpy or hit Eigen's 'DenseBase::resize() does not actually allow to resize' assertion; it goes away with -fno-inline or Clang. Unmerged PR #111 (Sept 2026) fixes Eigen::Map rebinding in ValueView::bind().
- && and || are undefined behavior on multi-dimensional non-boolean expressions; setting several forward-mode adjoints gives a scaled directional derivative.

## Known shortcomings

- First-party arXiv preprint, no review venue; CPU model missing (unnamed GCP Xeon VM); README's 'orders of magnitude' overstates the paper's 2-19x.
- Open issue #110 (2026): GCC 16 -O3 miscompile (segfault / Eigen resize assertion in RcppFastAD), fix PR #111 unmerged; no commits since 2023-09; no higher-order derivatives, Jacobians, sparse matrices or checkpointing; ties Adept on matrix products.

## Caveats and trade-offs

First-party benchmarks (author's arXiv preprint, no peer-review venue found, plus the author's ADBenchmark repo). CPU model not stated (an unnamed GCP Xeon VM). README's 'orders of magnitude' claim overstates the paper's 2-19x. Baselines are AD libraries (Adept, Stan Math, ADOL-C, CppAD, Sacado), not the category baselines. Last commit Sept 2023.

Header-only, C++17, depends on Eigen 3.3; expression templates and static graph structure limit dynamic control flow.

## Maintenance

Stale since Sept 2023 (one community PR open for a GCC 16 miscompile), but MIT-licensed and header-only, so it can be vendored; the R package RcppFastAD still depends on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** Numbers come from the author's own arXiv preprint (no peer-review venue shown) and the author's ADBenchmark repo. The paper states GCC10, -O3 -march=native, C++17, on a Google Cloud VM with an unnamed 'Intel Xeon Processor' (8 cores). The CPU model is missing, so it is not A, and first-party partial methodology is C, not B.
- **Verifier notes:** The paper does give compiler and flags (GCC10, -O3 -march=native) but no CPU model, and it is the author's own unrefereed preprint, so B becomes C. Benchmark code is public at JamesYang007/ADBenchmark. Metadata (MIT, 122 stars, last commit 2023-09-27, stale) confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JamesYang007/FastAD>
  - <https://github.com/JamesYang007/FastAD/commits>
  - <https://raw.githubusercontent.com/JamesYang007/FastAD/HEAD/README.md>
  - <https://raw.githubusercontent.com/JamesYang007/FastAD/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JamesYang007/ADBenchmark/HEAD/README.md>
  - <https://arxiv.org/abs/2102.03681>
  - <https://arxiv.org/html/2102.03681>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/JamesYang007/FastAD/HEAD/README.md>
  - <https://raw.githubusercontent.com/JamesYang007/ADBenchmark/HEAD/README.md>
  - <https://arxiv.org/html/2102.03681>
  - <https://github.com/JamesYang007/FastAD/issues>
  - <https://github.com/JamesYang007/FastAD/issues/110>
  - <https://github.com/JamesYang007/FastAD/commits>
  - <https://github.com/JamesYang007/FastAD/pulls>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jamesyang007/fastad`) · [data/wave8/enrich/raw/github_com_jamesyang007_fastad.json](../../../data/wave8/enrich/raw/github_com_jamesyang007_fastad.json) (enrichment confidence 0.8)

</details>
