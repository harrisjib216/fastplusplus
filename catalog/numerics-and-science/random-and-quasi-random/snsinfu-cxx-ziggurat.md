# cxx-ziggurat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Single-header C++11 ziggurat sampler meant to replace std::normal_distribution; the repo publishes no speed numbers.

| | |
|---|---|
| **Beats** | std::normal_distribution |
| **Claimed result** | No numbers on the repo page as fetched; repo has a benchmark folder |
| **Workload** | Normal variate generation via ziggurat as drop-in alternative to std::normal_distribution |
| **Metric** | throughput |
| **Adoption** | 4 stars, 0 forks |
| **Last commit** | 2018-11-14 |
| **Links** | [repository](https://github.com/snsinfu/cxx-ziggurat) |

## Verdict

No measurement is published. The repo includes a benchmark that times 10 million draws (ns/gen) of std::normal_distribution against the ziggurat for mt19937_64, mt19937 and JSF64 with double and float, built with C++11 -O2 -mtune=native -funsafe-math-optimizations, but it records no results, compiler or hardware.

## Use it when

- Hot loops that draw many N(mu, sigma) doubles or floats from a 64-bit engine (mt19937_64 or a fast 64-bit PRNG) and are bound by std::normal_distribution's cost
- Projects that want a tiny, dependency-free, Boost-licensed header and an API identical to std::normal_distribution
- Monte Carlo, Brownian or Langevin dynamics, and noise injection, where sample-for-sample reproducibility against libstdc++ is not required

## Skip it when

- When you need published, verified speedups: the repo has a benchmark program (benchmark/bench_normal_distribution.cc) but no results anywhere
- With 32-bit engines (std::mt19937): it then draws only 31 bits, and the uniform's low bits are the same bits that pick the layer and sign, so samples have coarse resolution and correlation between layer and value
- When you need other distributions (exponential, gamma); only the normal is provided
- When you need sequences identical to std::normal_distribution, for example regression tests seeded against libstdc++ output
- When you need long-term maintenance: last commit 2018, 14 commits, 4 stars, CI on the defunct travis-ci.org

## How it is fast

Marsaglia-Tsang style ziggurat with a precomputed 129-edge (128-layer) table. A single URNG draw supplies the uniform, the layer index (low 7 bits) and the sign (bit 7). Most samples are accepted with one multiply and compare, marked __builtin_expect-likely. Only rare wedge rejections call exp(), and only the base layer falls back to a log-based tail sampler (both noinline).

## Compared with alternatives

Pick it over Randompack when you want a single header that keeps your existing std URNG and std::normal_distribution call sites; Randompack is a larger library with its own engines but has published measurements. Randen, Romu, SIMDxorshift and Squares are uniform bit generators, not normal samplers, so they pair with this rather than compete with it.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | C++11 |
| **Platforms** | any (portable C++; GCC-specific __builtin_expect/noinline guarded by __GNUC__) |
| **Thread safety** | Not documented; the distribution object is stateless apart from its parameters (reset() is a no-op), so sharing it is safe as long as each thread uses its own URNG |
| **Drop-in for the baseline** | yes |

## Gotchas

- Bit budget comes from log2(URNG::max()-URNG::min()), so a 64-bit engine yields 63 bits and std::mt19937 yields 31; with doubles from a 32-bit engine, canonicalize uses all 31 bits, including the 8 bits that also choose the layer and sign
- The benchmark Makefile builds with -funsafe-math-optimizations -mtune=native -O2, so any number you measure with it is not under default flags
- The license is stated in the header and README badge; the README's LICENSE.txt link returns 404, so keep the header notice when vendoring

## Known shortcomings

- Verifier rejected as not notable (tier D): 4 stars, no published numbers, last commit 2018-11-14. Kept per keep-and-document rule.
- Benchmark exists but no recorded results; its Makefile uses -funsafe-math-optimizations; with 32-bit engines (std::mt19937) it draws only 31 bits and the same low bits pick layer, sign and part of the value; README's LICENSE.txt link 404s (Boost licence only in the header).

## Caveats and trade-offs

No performance numbers confirmed; tier D allowed only for notable projects (4 stars, not notable) so likely to be dropped by orchestrator

Header-only C++11; normal distribution only

## Maintenance

Abandoned since November 2018, but a single Boost-licensed header with no dependencies, so it is easy to vendor and audit; treat the speedup as unverified.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** README has no performance numbers; benchmark/ holds only a bench_normal_distribution target (Makefile, -O2 -mtune=native -funsafe-math-optimizations) with no published results.
- **Verifier notes:** Real BSL-1.0 header-only drop-in for std::normal_distribution, but tier D with 4 stars is not notable. License file is LICENSE.txt (Boost).
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/README.md>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/benchmark/Makefile>
  - <https://github.com/snsinfu/cxx-ziggurat>
  - <https://github.com/snsinfu/cxx-ziggurat/commits>
- **Sources the enricher read:**
  - <https://github.com/snsinfu/cxx-ziggurat>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/README.md>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/include/ziggurat.hpp>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/benchmark/bench_normal_distribution.cc>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/snsinfu/cxx-ziggurat/HEAD/LICENSE.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/snsinfu/cxx-ziggurat`) · [data/wave8/enrich/raw/github_com_snsinfu_cxx_ziggurat.json](../../../data/wave8/enrich/raw/github_com_snsinfu_cxx_ziggurat.json) (enrichment confidence 0.6)

</details>
