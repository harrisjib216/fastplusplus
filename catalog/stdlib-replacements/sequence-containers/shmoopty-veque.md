# veque

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++20 double-ended vector: std::vector's contiguous storage plus std::deque's fast front growth.

| | |
|---|---|
| **Beats** | std::vector; std::deque |
| **Claimed result** | g++-9 -O3 totals (lower=better, microseconds): veque 2,492,954us vs std::vector 10,248,719us (\~4.1x, derived from page data) and std::deque 3,480,344us (\~1.4x, derived from page data); largest single-op gap is front growth: std::vector 6,685,217us vs veque 30,739us (\~217x, derived from page data) |
| **Workload** | Seven operation benchmarks (resize, back growth via push/pop_back, front growth via push/pop_front, arbitrary-position insertion, iteration over 2M elements, mixed random operations, copy/move reassignment), each run 3 times, per the project's performance/main.cpp harness |
| **Metric** | latency |
| **Compiler and flags** | g++-9 -O3 (per benchmark source); CPU/hardware not stated |
| **Adoption** | 128 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/Shmoopty/veque) · [benchmark](https://raw.githubusercontent.com/Shmoopty/veque/master/performance/main.cpp) |

## Verdict

In the project's own performance/main.cpp harness (g++-9 -O3, CPU/hardware unstated), veque totaled 2,492,954us across seven operations vs std::vector's 10,248,719us (\~4.1x) and std::deque's 3,480,344us (\~1.4x); the largest single gap was front growth, where std::vector's O(n)-per-op reallocation cost 6,685,217us vs veque's 30,739us (\~217x), while veque itself was slower than std::deque on both front growth (30,739 vs 16,386us) and back growth (552,027 vs 342,218us) in the same run.

## Use it when

- Vector-like contiguous container that also needs frequent push_front/pop_front or resize_front, not just back growth
- Insert/erase happen near either end of the sequence, not predominantly in the middle, so closest-side shifting pays off
- C++20 codebase (concepts/ranges already required) that can take a single dependency-free header
- Want tunable memory-vs-invalidation behavior per container instantiation via the ResizeTraits template parameter
- Want a strong-exception-guarantee pop-and-return primitive (pop_back_element/pop_front_element)

## Skip it when

- Toolchain is pre-C++20 (header requires &lt;concepts&gt; and &lt;ranges&gt;); no C++14/17 build exists despite a README wishlist entry
- Memory is tight: veque reserves slack at both front and back by default, so its footprint exceeds std::vector's at the same size()
- Workload is back-growth-heavy: in the project's own benchmark veque was slower than std::deque on back growth (552,027 vs 342,218us) and front growth (30,739 vs 16,386us)
- Code depends on std::vector's partial iterator-invalidation guarantees on insert/erase; the default fast_resize_traits invalidates all iterators/references on those ops (opt into vector_compatible_resize_traits to get std::vector's rules back, at the cost of the closest-side speedup)
- Need std::vector&lt;bool&gt;'s bit-packed specialization; veque&lt;bool&gt; is explicitly not specialized
- Project is small and thinly used (128 stars, \~10 forks, effectively one author) with a past heap-corruption bug in assign() (fixed 2023) — worth vetting before production use

## How it is fast

Unused capacity is kept on both sides of the live elements instead of only at the back, so front insertion/growth is amortized O(1) like std::deque instead of std::vector's O(n) full-buffer shift. Arbitrary-position insert/erase can shift elements toward whichever end (front or back) is closer, roughly halving the average number of elements moved compared to std::vector's always-shift-to-back behavior. A ResizeTraits policy (fast_resize_traits by default) controls this trade-off and lets callers dial down to std::vector-style behavior (vector_compatible_resize_traits, std_vector_traits, no_reserve_traits) when they need std::vector's iterator-invalidation guarantees instead.

## Compared with alternatives

Pick veque over the catalogued siblings (plf::colony/hive, plf::list, eastl::vector, fast_vector) when you need std::vector's contiguous, ordered, drop-in-ish interface but also do real front-side growth (push_front/pop_front/resize_front): eastl::vector and fast_vector only optimize back-end std::vector operations, and plf::colony/plf::list trade away contiguous ordered storage entirely.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only: &lt;algorithm&gt;, &lt;concepts&gt;, &lt;cstddef&gt;, &lt;cstring&gt;, &lt;iterator&gt;, &lt;limits&gt;, &lt;ranges&gt;, &lt;ratio&gt;, &lt;string&gt;, &lt;type_traits&gt;, &lt;stdexcept&gt;, &lt;utility&gt;) |
| **Minimum toolchain** | C++20 (uses &lt;concepts&gt; and &lt;ranges&gt;); the benchmark's sample-output comment is labelled g++-9, which predates full &lt;ranges&gt; support, so that sample may be stale relative to current code |
| **Platforms** | not documented; no platform-specific code observed, standard C++20 only |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — matches std::vector's full API (and adds std::deque's front operations), but the default fast_resize_traits changes iterator/reference invalidation rules on insert/erase to always-invalidate; true std::vector-compatible invalidation requires switching to vector_compatible_resize_traits |

## Gotchas

- Default ResizeTraits (fast_resize_traits) invalidates ALL iterators and references on any insert/erase, unlike std::vector's partial invalidation — use vector_compatible_resize_traits for std::vector's guarantees
- veque&lt;bool&gt; is not specialized/bit-packed, unlike std::vector&lt;bool&gt;
- Closed issue #9 reported heap corruption after veque destruction, triggered via assign(); maintainer marked it fixed in a later release (2023-06-20) — pin a recent commit rather than an old tag
- fast_resize_traits preallocates slack at both ends by default, so memory use is higher than std::vector even at equal size(); no_reserve_traits removes that at the cost of resize speed

## Caveats and trade-offs

First-party sample output in a source comment, with no CPU model. The stdlib vendor is not named (presumably libstdc++ via g++-9). The sample is labelled g++-9, while current code targets C++20/23, so it may be stale. veque is slower than std::deque on back growth (552,027 vs 342,218us) and front growth (30,739 vs 16,386us), and roughly equal to std::vector on iteration (207,987 vs 203,040us). The 217x front-growth ratio is an algorithmic worst case for std::vector.

Contiguous storage like vector but reserves slack at both ends, so higher memory overhead than std::vector; the \~217x front-growth figure mostly reflects std::vector's known O(n)-per-op front-insertion pathology rather than a uniform win; arbitrary-insertion and mixed-op wins are more modest (\~1.4-1.9x)

## Maintenance

Actively maintained (last commit 2026-09-15, BSL-1.0 license) but small and effectively single-author (128 stars, \~10 forks); a past heap-corruption bug in assign() was reported and fixed, so use a current commit rather than an old release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** performance/main.cpp is public benchmark code with a sample-output comment labelled 'g++-9 -O3' comparing std::deque, std::vector and veque. No CPU model is stated, so it is not A.
- **Verifier notes:** All totals and per-test numbers match the source comment, and the derived ratios (\~4.1x, \~1.4x, \~217x) are correct. The workload (7 tests, each run 3 times per container, 2M-element iteration) matches main(). BSL-1.0, 128 stars, last commit 2026-09-15.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Shmoopty/veque/master/performance/main.cpp>
  - <https://github.com/Shmoopty/veque>
- **Sources the enricher read:**
  - <https://github.com/Shmoopty/veque>
  - https://raw.githubusercontent.com/Shmoopty/veque/master/README.md (via gh api repos/Shmoopty/veque/readme)
  - https://raw.githubusercontent.com/Shmoopty/veque/master/API.md (via gh api repos/Shmoopty/veque/contents/API.md)
  - https://raw.githubusercontent.com/Shmoopty/veque/master/include/veque.hpp (via gh api repos/Shmoopty/veque/contents/include/veque.hpp)
  - <https://raw.githubusercontent.com/Shmoopty/veque/master/performance/main.cpp>
  - <https://github.com/Shmoopty/veque/issues/9>
  - <https://github.com/Shmoopty/veque/issues/7>
  - https://github.com/Shmoopty/veque/issues (search, open+closed)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/shmoopty/veque`) · [data/wave1/enrich/raw/github_com_shmoopty_veque.json](../../../data/wave1/enrich/raw/github_com_shmoopty_veque.json) (enrichment confidence 0.6)

</details>
