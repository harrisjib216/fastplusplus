# Zest (generalized Ziggurat sampler: normal, gamma, Student t, etc.)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Header-only generalized Ziggurat sampler for gamma, Student t, F, Weibull and custom unimodal densities; 2.5-10x faster than STL distributions.

| | |
|---|---|
| **Beats** | STL &lt;random&gt; distributions (std::normal_distribution and the other std distributions) and Boost.Random |
| **Claimed result** | Relative speed of Zest versus STL / Boost: normal 3.6 / 1.0, log-normal 3.1 / 1.0, Cauchy 4 / 4, exponential 3.3 / 0.67 (slower than Boost), gamma alpha&gt;1 2.5 / 7, Weibull alpha&gt;1 3.3 / 3.3, Student's t nu&gt;1 10 / 20, Fisher's f d1,d2&gt;1 6 / 11-14. README summary: 'faster than both STL and Boost in most cases, sometimes by a factor of more than 10'. |
| **Workload** | Approximate relative speed of generating variates from each distribution with Zest (1024 regions) versus the STL and Boost implementations. |
| **Metric** | throughput |
| **Adoption** | 3 stars |
| **Last commit** | 2020-01-25 |
| **Links** | [repository](https://github.com/DiscreteLogarithm/Zest) · [benchmark](https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/README.md) |

## Verdict

The README gives 'approximate' relative speeds of Zest with 1024 regions vs STL / Boost: normal 3.6 / 1.0, exponential 3.3 / 0.67, gamma alpha&gt;1 2.5 / 7, Student's t nu&gt;1 10 / 20, Fisher's F d1,d2&gt;1 6 / 11-14. No CPU, compiler, flags, URBG or benchmark code is given, and a search snippet of the arXiv preprint says the STL was GCC's libstdc++.

## Use it when

- Hot loops drawing millions of variates from a fixed-parameter Student's t, Fisher's F, gamma or Weibull distribution, where the README reports 2.5-10x over libstdc++ and 3.3-20x over Boost.
- Exact sampling from your own unimodal or monotone density, including ones unbounded at the mode or with infinite tails, without hand-writing a Ziggurat: supply pdf, strip_area and a tail category.
- GPL-compatible C++14+ projects that already depend on Boost (zest.hpp includes Boost.Math headers).
- Monte Carlo code paired with a 64-bit URBG (std::mt19937_64 or any generator whose range is exactly 2^64) when you want full double resolution.

## Skip it when

- Proprietary or permissively licensed code: it is GPL-3.0, so vendoring the header puts your program under the GPL.
- Parameters that change on every draw (for example a per-sample gamma shape in Dirichlet or Gibbs samplers): each parameter set needs a new Ziggurat object whose constructor runs N (default 1024) root searches, using Boost special functions for gamma/t/F, and the setup cost is not documented.
- Normal or exponential only: per the README it only ties Boost for normal and log-normal (1.0) and is slower than Boost for exponential (0.67), so Boost or a small dedicated Ziggurat is simpler.
- Multimodal densities, which the algorithm does not support.
- Bulk or SIMD generation, or when you need tests and maintenance: it is a scalar, one-variate-at-a-time sampler with no test suite, CI or benchmark code in the repo, and it has been inactive since 2020.

## How it is fast

It uses Marsaglia-Tsang's Ziggurat idea, generalized: the constructor precomputes N equal-area horizontal strips (by bisection on strip_area), so most draws are one URBG call, a table lookup by the low index bits and one compare, with no log, exp or special-function evaluation. Only draws that land in a strip edge, the tail (mapping or mapping-plus-rejection) or an unbounded peak take the slow path. The README's largest ratios (6-20x) are for Student's t and Fisher's F, where this fast path skips all per-draw transcendental work.

## Compared with alternatives

Pick Zest over normaldist-benchmark, cxx-ziggurat or zigg when you need Ziggurat speed for non-normal shapes (t, F, gamma, Weibull) or a custom unimodal pdf. Those siblings cover only the normal (plus exponential and uniform in zigg). For vectorized bulk normal or uniform fills, EigenRand or Randompack fit better.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Math headers (boost/math/special_functions/gamma.hpp, boost/math/distributions.hpp); ships with canonical_float_random.hpp alongside zest.hpp |
| **Minimum toolchain** | C++14 (enforced by #error), but the header uses message-less static_assert, a C++17 feature, so expect warnings in C++14 mode (errors with -pedantic-errors) |
| **Platforms** | any platform with a C++14 compiler and Boost; no SIMD or OS-specific code in the headers |
| **Thread safety** | Not documented. operator() is const and only reads tables built in the constructor, so one object shared across threads with a separate URBG per thread looks safe from the code. |
| **Drop-in for the baseline** | partial — call syntax matches a std:: distribution (zig(urbg)), but the URBG type is a template parameter, its range must be exactly 2^32 or 2^64 (std::minstd_rand fails a static_assert), and there is no param_type, reset(), min() or max(); output sequences differ from std:: |

## Gotchas

- With a 32-bit URBG (the README example uses std::mt19937), each fast-path variate comes from one 32-bit draw whose low 10 bits pick the region, so body values carry only about 22 random bits (from reading operator()). Use a 64-bit URBG when double resolution matters.
- Each object is large: with N=1024, double and a 64-bit URBG, the symmetric implementation holds four (N+1)-entry double tables, an N-entry int64 table and a 4096-double table, about 72 KB (derived from the class layout). Asymmetric distributions hold two monotone sides. Avoid putting many of them on the stack.
- The constructor throws std::logic_error on bad parameters or very low rejection efficiency, and it prints WARNING lines to std::cerr for low-efficiency regions. zest.hpp uses std::cerr without including &lt;iostream&gt; and relies on Boost's includes.
- Ziggurat is declared in the global namespace (only the distributions are in zest::), and ChiSquared takes its degrees of freedom as a compile-time template argument.

## Known shortcomings

- README numbers are 'approximate' and the repo has no benchmark code; needs Boost.Math; slower than Boost on exponential; last touched 2020-01-25; arXiv paper unreadable here.
- With a 32-bit URBG (README example std::mt19937) each body variate gets only \~22 random bits. Objects are \~72 KB each; tables are rebuilt per parameter set with undocumented setup cost. Message-less static_assert (C++17) despite a C++14 check; Ziggurat class in the global namespace.

## Caveats and trade-offs

The README numbers are labelled 'approximate' and give no CPU, compiler, flags, standard-library version or URBG. The repo contains no benchmark code (only zest.hpp, canonical_float_random.hpp, example.cpp and a developer guide), so the table cannot be reproduced from the repo. Details are in the arXiv preprint 1810.04744 (not opened, arxiv.org blocked here); search snippets of it say the comparison was against GCC's STL (libstdc++) and Boost.Random, and no journal version was found. Normal and log-normal are only on par with Boost (1.0), and exponential is slower than Boost (0.67). zest.hpp requires C++14 and includes Boost.Math headers (gamma and distributions). GPL-3.0 (copyleft) for a single header. Issue #1 (an example crashing with std::logic_error for Exponential with mode -1) was fixed in the last commit, 2020-01-25; there are 6 commits in total.

Single header zest.hpp; GPL-3.0 copyleft; supports only unimodal densities; needs a URBG producing 32- or 64-bit unsigned values; table size (regions) must be a power of two and is a runtime/memory tuning knob.

## Maintenance

Abandoned since 2020-01-25 (6 commits; its one issue, an Exponential example crash, was fixed then). It is a self-contained header pair, but GPL-3.0 limits it to GPL-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README has a first-party table of 'approximate' relative speeds against STL and Boost with no CPU, compiler, flags or URBG, and the repo has no benchmark code (only zest.hpp, canonical_float_random.hpp and example.cpp); the linked arXiv preprint 1810.04744 could not be opened and is not shown to be peer-reviewed, so C.
- **Verifier notes:** The README table matches the claimed numbers, which are a subset of its rows (the 0.1&lt;alpha&lt;1 and 0.2&lt;d&lt;1 rows give ranges such as Student's t 6-16 vs STL). baseline_stdlib is set to libstdc++ from a WebSearch snippet of the arXiv abstract ('GCC's implementation of STL'); the arXiv page itself was EGRESS_BLOCKED, as were ResearchGate and the Stan forum thread. Metadata checked: GPL-3.0 LICENSE, 3 stars, last commit 2020-01-25, abandoned.
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/README.md>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/zest.hpp>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/example.cpp>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/reviewr_developer_guide.md>
  - <https://github.com/DiscreteLogarithm/Zest>
  - <https://github.com/DiscreteLogarithm/Zest/commits>
  - <https://github.com/DiscreteLogarithm/Zest/issues/1>
- **Sources the enricher read:**
  - <https://github.com/DiscreteLogarithm/Zest>
  - <https://github.com/DiscreteLogarithm/Zest/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/README.md>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/zest.hpp>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/canonical_float_random.hpp>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/example.cpp>
  - <https://raw.githubusercontent.com/DiscreteLogarithm/Zest/HEAD/reviewr_developer_guide.md>
  - https://arxiv.org/abs/1810.04744 (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/discretelogarithm/zest`) · [data/wave8/enrich/raw/github_com_discretelogarithm_zest.json](../../../data/wave8/enrich/raw/github_com_discretelogarithm_zest.json) (enrichment confidence 0.7)

</details>
