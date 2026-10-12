# nanobench::Rng (RomuDuoJr)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> nanobench's built-in RomuDuoJr generator: a drop-in &lt;random&gt;-style 64-bit PRNG, \~1.3-3.9x faster than std::mt19937_64.

| | |
|---|---|
| **Beats** | std::mt19937_64 |
| **Claimed result** | Interleaved compare() table: nanobench::Rng 0.49 ns/uint64_t vs std::mt19937 1.71 ns ('3.48x ahead of std::mt19937', 95% CI 3.46-3.50) and vs std::mt19937_64 1.90 ns (\~3.9x, derived from page data). Older relative() table: ankerl::nanobench::Rng 1.57 ns vs std::mt19937_64 2.03 ns (\~1.3x) and vs std::default_random_engine 35.87 ns (\~22.8x) (derived from page data). Header doc comment claims '\~46 times faster than std::default_random_engine ... [vs] std::mt19937_64 ... 2-3 times as fast.' |
| **Workload** | Generating 64-bit random values via Rng::operator(); author's own in-header micro-benchmark comparing nanobench's built-in RomuDuoJr-based Rng against std::default_random_engine and std::mt19937_64. |
| **Metric** | throughput |
| **Adoption** | 1,738 stars; widely used C++ micro-benchmarking library |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/martinus/nanobench) · [benchmark](https://github.com/martinus/nanobench/blob/master/src/docs/tutorial.rst) |

## Verdict

Nanobench's own tutorial.rst shows two different first-party runs, neither stating compiler, flags, or CPU: a relative()-table run has ankerl::nanobench::Rng at 1.57 ns/uint64_t vs std::mt19937_64 at 2.03 ns (\~1.3x) and vs std::default_random_engine at 35.87 ns (\~22.8x); a separate compare()-table run (with 95% CI) has nanobench::Rng at 0.49 ns/uint64_t vs std::mt19937 at 1.71 ns (3.48x, CI 3.46-3.50x) and vs std::mt19937_64 at 1.90 ns (\~3.9x). The two runs disagree by roughly 3x on the margin over mt19937_64, and the second table's exact RNG lineup (includes an unlabeled 'lcg by hand') has no corresponding source file checked into the repo.

## Use it when

- Feeding random inputs to a nanobench benchmark loop where RNG overhead must stay well below the measured operation's own cost
- Non-cryptographic hot loops needing a fast 64-bit value or ranged integer where std::mt19937/mt19937_64 throughput is the bottleneck
- Already depending on nanobench and wanting to avoid pulling in a second PRNG library for lightweight randomness
- Need a fast, slightly-biased container shuffle (shuffle()) instead of std::shuffle
- Deterministic-but-throwaway sequences within a single build (seed via Rng(seed)) where cross-version reproducibility isn't required

## Skip it when

- Anything security- or cryptography-adjacent - the header states outright it is not cryptographically secure
- Large-scale simulation or Monte Carlo work - the author's own doc comment caps estimated capacity at \~2^51 bytes and calls it 'not enough for large jobs'
- Code that must reproduce the same sequence across nanobench upgrades - the header warns the underlying algorithm may change between releases
- Multi-threaded code sharing one generator instance - thread safety isn't documented and Rng is move-only (copy disabled), implying one instance per thread
- Workloads needing an unbiased bounded-integer distribution - bounded() uses a fast biased reduction, not rejection sampling

## How it is fast

Implements RomuDuoJr (Mark Overton's Romu family), a non-cryptographic generator with only 128 bits of state (two uint64_t words) and a per-call update of one 64-bit multiply plus a subtract-then-rotate, far cheaper than Mersenne Twister's large state array and tempering step. operator() is declared inline in the header so it can fully inline at the call site. The design trades statistical rigor and state size for minimal instructions per call.

## Compared with alternatives

Pick it only if you're already using nanobench and want a zero-dependency fast RNG for generating benchmark inputs. For general-purpose or higher-throughput random number generation, PCG (pcg-cpp/wjakob pcg32) or xoshiro_cpp are better studied, and the tutorial's own numbers show nanobench::Rng's edge over std::mt19937_64 (\~1.3-3.9x, inconsistent across two runs) is smaller and shakier than PCG's (\~3.5-4x) or xoshiro256++'s (\~3.2x) measured margins.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++11 (CMake target_compile_features cxx_std_11; repo advertises C++11/14/17/20 support) |
| **Platforms** | platform-independent - pure integer/multiply ops, no SIMD or ISA requirement |
| **Thread safety** | not documented; Rng is move-only (copy constructor/assignment deleted) and holds unsynchronized mutable state, implying one instance per thread |
| **Drop-in for the baseline** | partial - explain: matches the UniformRandomBitGenerator interface so it works with std::uniform_int_distribution etc., but unlike std::mt19937_64 it cannot be copied (only moved, or cloned via .copy()) and it adds extra non-standard methods (bounded, uniform01, shuffle, state) |

## Gotchas

- Copy constructor and copy-assignment are deleted; use .copy() or move semantics instead of copying by value
- The algorithm may change between nanobench releases (documented in the header), so seeded sequences aren't guaranteed stable across upgrades
- bounded(range) uses a fast, slightly biased reduction rather than rejection sampling
- Using it outside nanobench still requires building the one translation unit compiled with ANKERL_NANOBENCH_IMPLEMENT, like the rest of the header-only library

## Caveats and trade-offs

First-party numbers. Tutorial tables (src/docs/tutorial.rst) come from public code (src/test/example_random_number_generators.cpp) but state no compiler, flags, or CPU. The two tutorial tables disagree on the mt19937_64 margin (\~1.3x in the relative() table vs \~3.9x in the interleaved compare() table), and the header's '\~46x vs default_random_engine' is higher than the tutorial's \~22.8x.

Rng is not cryptographically secure and has a modest estimated capacity (\~2^51 bytes); designed for benchmarking workloads rather than general-purpose simulation where xoshiro/PCG-class statistical guarantees may be wanted; author notes the underlying algorithm may change between nanobench releases.

## Maintenance

Active (last commit 2026-09-06) and MIT-licensed; the whole library is one header plus a one-line implementation .cpp, trivial to vendor even if development ever stalls.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The header quote is verbatim, and the repo also publishes measured tables in src/docs/tutorial.rst with public benchmark code (src/test/example_random_number_generators.cpp). No compiler, flags, or CPU are stated for those tables, so this is first-party C.
- **Verifier notes:** Record's caveat that no benchmark code or numbers table exists was wrong. Tutorial has both, so benchmark_url was repointed there. Last commit author date is 2026-09-06 and committer date is 2026-09-07; the record's date was left as is. MIT, 1,738 stars, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/martinus/nanobench>
  - <https://github.com/martinus/nanobench/blob/master/src/include/nanobench.h>
  - <https://github.com/martinus/nanobench/blob/master/src/docs/tutorial.rst>
  - <https://github.com/martinus/nanobench/blob/master/src/test/example_random_number_generators.cpp>
  - <https://github.com/martinus/nanobench/blob/master/src/test/tutorial_compare.cpp>
- **Sources the enricher read:**
  - <https://github.com/martinus/nanobench>
  - <https://github.com/martinus/nanobench/blob/master/README.md>
  - <https://github.com/martinus/nanobench/blob/master/src/docs/tutorial.rst>
  - <https://github.com/martinus/nanobench/blob/master/src/test/example_random_number_generators.cpp>
  - <https://github.com/martinus/nanobench/blob/master/src/include/nanobench.h>
  - <https://github.com/martinus/nanobench/blob/master/src/test/tutorial_compare.cpp>
  - <https://github.com/martinus/nanobench/blob/master/CMakeLists.txt>
  - <https://github.com/martinus/nanobench/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/martinus/nanobench`) · [data/wave1/enrich/raw/github_com_martinus_nanobench.json](../../../data/wave1/enrich/raw/github_com_martinus_nanobench.json) (enrichment confidence 0.5)

</details>
