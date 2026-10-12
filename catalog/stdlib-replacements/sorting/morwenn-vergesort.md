# vergesort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Presortedness-detecting merge layer over pdqsort; beats std::sort/std::stable_sort when input has long sorted runs.

| | |
|---|---|
| **Beats** | std::sort, std::stable_sort |
| **Claimed result** | Approximate, read from the README random-access chart (10^6 ints, cycles per element) (derived from page data). Vergesort beats libstdc++ std::sort on every distribution shown: shuffled \~365 vs \~713 (\~2x, via its pdqsort fallback), pipe organ \~22 vs \~885, push front \~15 vs \~858, ascending and descending sawtooth \~63 vs \~325 (\~5x). It beats std::stable_sort on most patterns (sawtooth \~63 vs \~165-198) but is slower on 'Alternating' (\~307 vs \~185). The author notes the sawtooth patterns are biased toward vergesort. |
| **Workload** | Cycles per element (rdtsc, bench/bench.cpp) sorting a std::vector&lt;int&gt; of one million ints under 12 distributions (shuffled, shuffled 16 values, all equal, ascending, descending, pipe organ, push front, push middle, ascending/descending sawtooth, alternating, alternating 16 values). The random-access version is compared against std::sort, std::stable_sort, heapsort and pdqsort. A second chart compares the bidirectional version against std::list::sort, and fallbacks.md compares with/without-vergesort runs over std::sort and std::stable_sort (libstdc++ MinGW 6.1.0), timsort, spreadsort, pdqsort and ska_sort. |
| **Metric** | throughput |
| **Compiler and flags** | MinGW g++ 6.1.0 -std=c++1z -O2 -march=native |
| **Adoption** | 73 stars |
| **Last commit** | 2025-11-07 |
| **Links** | [repository](https://github.com/morwenn/vergesort) · [benchmark](https://github.com/morwenn/vergesort) |

## Verdict

Chart-derived cycles-per-element numbers (std::vector&lt;int&gt;, 10^6 elements, MinGW g++ 6.1.0 -std=c++1z -O2 -march=native, libstdc++, no CPU model stated) show vergesort's pdqsort-backed random-access version beating libstdc++ std::sort on every distribution charted (e.g. shuffled \~365 vs \~713, pipe organ \~22 vs \~885, push front \~15 vs \~858) and beating std::stable_sort on most patterns, but losing to std::stable_sort on the 'Alternating' pattern (\~307 vs \~185).

## Use it when

- Large std::vector-like collections of comparison-sortable types that frequently contain long sorted or reverse-sorted runs (&gt;= n/log n), e.g. pipe-organ, push-front/push-middle, or nearly-sorted-log patterns
- You already use (or would use) pdqsort/std::sort and want a near-zero-cost presortedness check layered on top, since the fallback triggers in O(log n) comparisons on random data
- std::list or other bidirectional-only sequences where std::list::sort could benefit from run detection, if you can accept the bidirectional overload's O(n^2) worst case
- Header-only, dependency-free, C++03-compatible environments where vendoring one file is preferable to adding a library
- One-shot throughput sorts of 10^6+ elements where instability is acceptable

## Skip it when

- You need a stable sort: vergesort reverses descending runs in place, which makes it unstable even though its fallback (pdqsort) is also unstable
- Data is uniformly random/shuffled with no long runs: the win over calling pdqsort directly is essentially just avoiding vergesort's own scan overhead, not a speedup over pdqsort
- Bidirectional-iterator use (e.g. std::list) where adversarial input could hit the documented O(n^2) worst case from the median-of-9 quicksort fallback
- Workloads resembling the README's 'Alternating' pattern, where the shown benchmark has vergesort slower than std::stable_sort (\~307 vs \~185 cycles/element)
- Serious/production integer-sorting workloads chasing maximum speed: the repo's own maintainer calls this standalone header 'more of a demonstrator' and points to the same author's cpp-sort library (cppsort::verge_sort) as the tuned, faster version

## How it is fast

The random-access overload jumps n/log n elements at a time instead of scanning one by one, so it can decide a run is not 'big enough' after O(log n) comparisons and bail out to pdqsort almost immediately on random data. When a big-enough run is found it records its bounds (reversing descending runs) instead of sorting it, and once the whole range is scanned it k-way-merges the collected runs with std::inplace_merge. The bidirectional overload lacks the jump-scan (it must walk linearly) and falls back to plain median-of-9 quicksort instead of pdqsort, which is why the README documents it as slower and O(n^2) worst case.

## Compared with alternatives

Pick vergesort over pdqsort when your data regularly contains long sorted/reverse-sorted runs (pipe-organ, push-front/middle, nearly-sorted-log shapes) and unstable output is acceptable — pdqsort alone is the safer default for uniformly random data since vergesort only adds a fast-fail scan there. Prefer ska_sort or Highway's vqsort instead when the win you need comes from key-type specialization (integer radix) or SIMD partitioning rather than run detection, since vergesort's fallbacks.md shows it still beats raw ska_sort on presorted patterns but the 'vergesort killer' pattern narrows that gap (139 vs 127 cycles/element).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none — bundles its own pdqsort, insertion sort, iter_sort3, log2 and quicksort helper headers; standard library only |
| **Minimum toolchain** | C++03 for the standalone header (README: 'Everything should work with even C++03'); benchmarks were built with MinGW g++ 6.1.0 -std=c++1z -O2 -march=native |
| **Platforms** | any (portable C++, no platform-specific intrinsics in the header); benchmark hardware itself is undocumented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same call signature as std::sort (iterators, optional comparator), but it is unstable, and the bidirectional overload for std::list-like containers is a separate, slower code path with an O(n^2) worst case |

## Gotchas

- Unstable by design: it uses std::reverse on descending runs before merging, which discards relative order of equal elements even when the fallback sorter is stable
- A real 2020 bug (issue #13) had the standalone header's random-access overload silently misnamed/uncalled, so it fell through to the much slower bidirectional path — fixed after report, but shows the single-header demo has drifted out of sync with cpp-sort's verge_sort before
- The 'big enough' run threshold is a fixed n/log n heuristic with no tuning parameter; the author notes it is sometimes suboptimal versus always falling back
- The bidirectional-iterator variant cannot use the jump-scan optimization and falls back to a plain median-of-9 quicksort, giving it O(n^2) worst case (vs O(n log n) worst case for the random-access version)

## Caveats and trade-offs

Numbers appear only as chart images (imgur), so the values are approximate readings. No CPU model is stated anywhere, which caps the tier at C. Built with the old MinGW GCC 6.1.0. The win over std::sort on random data comes from the pdqsort fallback. Slower than std::stable_sort on the 'Alternating' pattern. The bidirectional version is slower than std::list::sort on the sawtooth and alternating patterns.

Not stable; best case relies on data containing sorted runs of size &gt; n/log n; the bidirectional-iterator variant's worst case is O(n^2) since it falls back to a median-of-9 quicksort instead of pdqsort.

## Maintenance

Actively maintained (pushed 2025-11-07) and MIT-licensed, but the author has stated on the issue tracker that this standalone single-header version is 'more of a demonstrator' favoring small code size and C++03 backward compatibility over raw speed — the actively tuned, faster implementation is cppsort::verge_sort in the same author's cpp-sort project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** Code is public (bench/bench.cpp, bench/bars.py). The README states MinGW g++ 6.1.0 -std=c++1z -O2 -march=native, and fallbacks.md says libstdc++ was used, but no CPU model appears in the README, fallbacks.md or the chart axis (bars.py prints only 'Cycles per element'). Tier C.
- **Verifier notes:** The record is accurate. claimed_speedup and workload were enriched with approximate chart readings, which show one loss vs std::stable_sort. The metadata checks out: MIT, 73 stars, last commit 2025-11-07 (active), not a fork, not archived. The canonical owner casing is Morwenn/vergesort, default branch trunk.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/morwenn/vergesort>
  - <https://github.com/Morwenn/vergesort/blob/trunk/fallbacks.md>
  - <https://github.com/Morwenn/vergesort/blob/trunk/bench/bars.py>
  - <https://github.com/Morwenn/vergesort/blob/trunk/bench/bench.cpp>
  - <https://github.com/Morwenn/vergesort/blob/trunk/license.txt>
  - <https://i.imgur.com/Qgsga47.png>
  - <https://i.imgur.com/hDTScAb.png>
- **Sources the enricher read:**
  - <https://github.com/Morwenn/vergesort>
  - <https://github.com/Morwenn/vergesort/blob/trunk/readme.md>
  - <https://github.com/Morwenn/vergesort/blob/trunk/fallbacks.md>
  - <https://github.com/Morwenn/vergesort/blob/trunk/license.txt>
  - <https://github.com/Morwenn/vergesort/tree/trunk/include/vergesort>
  - <https://github.com/Morwenn/vergesort/issues/13>
  - <https://github.com/Morwenn/vergesort/issues>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/morwenn/vergesort`) · [data/wave0-seed/enrich/raw/github_com_morwenn_vergesort.json](../../../data/wave0-seed/enrich/raw/github_com_morwenn_vergesort.json) (enrichment confidence 0.55)

</details>
