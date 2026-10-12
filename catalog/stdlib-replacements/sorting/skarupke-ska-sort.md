# ska_sort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Header-only radix/American-flag sort beating std::sort by \~2x on ints, floats, structs and strings via key extraction.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | Blog post: 'I wrote a sorting algorithm that's twice as fast as std::sort for many inputs'. On ints from std::geometric_distribution(0.001) it is 'many times faster than std::sort'. For small collections it is 'never slower than std::sort (because it uses std::sort when the collection is too small)', because it stops recursing below 128 elements. Per-type results appear only as ns/item chart images. |
| **Workload** | Nanoseconds-per-item sorting of integers, floats, structs (128-1024 bytes), and strings via radix sort / American flag sort (ska_sort), compared against std::sort across increasing array sizes and skewed distributions. |
| **Metric** | throughput |
| **Adoption** | 248 stars |
| **Last commit** | 2017-05-15 |
| **Links** | [repository](https://github.com/skarupke/ska_sort) · [benchmark](https://probablydance.com/2016/12/27/i-wrote-a-faster-sorting-algorithm/) |

## Verdict

The only benchmark is the author's 2016 blog post (Google Benchmark, ns/item charts) reporting ska_sort about 2x faster than std::sort on uniform-distribution integers and 'many times faster' on skewed (std::geometric_distribution(0.001)) integers, with similar or better results for (bool,float) pairs, 128-1024 byte structs, and short strings; no compiler, flags, or CPU model are stated, and the post itself notes performance degrades toward std::sort's O(n log n) on long strings with shared prefixes.

## Use it when

- Large arrays (roughly &gt;128 elements) of integers, IEEE-754 floats, bools, or other types with a cheap ExtractKey returning a radix-sortable value
- Structs/tuples sorted by a fixed-width key (128-1024 byte records in the author's benchmarks), via an ExtractKey with operator[]
- Skewed/low-entropy integer distributions, where the author reports the largest wins ('many times faster' on std::geometric_distribution(0.001))
- Throughput-focused batch sorts where instability and an optional O(n) auxiliary buffer (ska_sort_copy) are acceptable
- Header-only C++ codebases that want to vendor one file rather than add a build dependency

## Skip it when

- You need a stable sort — ska_sort is not stable
- Keys aren't radix-extractable, or the container isn't random-access — this fails to compile rather than silently falling back to std::sort
- Very large collections: one blog-comment reader reports ska_sort slower than std::sort on 1.2 billion uint64_t (unverified, possibly paging-related)
- Long, variable-length strings with many shared prefixes — the author says it degrades toward O(n log n) behavior there
- Strict C++20 builds: the header uses std::result_of (deprecated C++17, removed C++20), and the repo has been unmaintained since 2017 so this is unlikely to be patched upstream

## How it is fast

Recursively partitions elements byte-by-byte into 256 buckets (LSD-style radix sort) instead of comparing elements, giving roughly O(n\*b) behavior for b key bytes versus std::sort's O(n log n). For partitions under the American-flag-sort threshold (1024 elements) it uses an in-place American flag sort whose inner loop ('ska byte sort') processes swaps for many not-yet-placed elements at once rather than completing one swap chain at a time, improving instruction-level parallelism. Partitions under 128 elements, or string keys whose recursion exceeds 16 levels (pathological shared prefixes), fall back to std::sort.

## Compared with alternatives

Pick ska_sort over pdqsort/vergesort when your keys are natively radix-extractable (fixed-width ints/floats, short strings, small structs) and you want a small single-header drop-in with no build dependency; pdqsort and vergesort are comparison sorts with broader type support and adaptivity to existing order, and Highway's vqsort needs AVX-512/SIMD hardware plus a real build dependency, both heavier asks than ska_sort's plain C++14 header.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for ska_sort.hpp (STL only: &lt;cstdint&gt;, &lt;algorithm&gt;, &lt;type_traits&gt;, &lt;tuple&gt;, &lt;utility&gt;); the bundled ska_sort_tests_and_benchmarks.cpp additionally needs GTest and Google Benchmark to build, but that file is not required to use the sort |
| **Minimum toolchain** | C++14 (generic lambdas); std::result_of usage makes strict C++20 mode risky without patching |
| **Platforms** | any (plain C++, no SIMD/intrinsics); float/double keys assume IEEE-754 representation |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: ska_sort(begin, end) is a near drop-in in-place replacement for std::sort(begin, end) on random-access iterators, but non-identity keys need an ExtractKey returning a radix-sortable value (not an arbitrary comparator), and the faster ska_sort_copy path requires a caller-managed same-size buffer plus checking its bool return to know which buffer holds the sorted result |

## Gotchas

- ska_sort_copy's bool return says whether the sorted output landed in buffer_begin (true) or the original range (false); using the wrong one silently gives unsorted/stale data
- Float/double keys are reinterpreted as unsigned integers through a union, which is undefined behavior in standard C++, with no compile-time IEEE-754 (is_iec559) guard — flagged in open issue #2, never fixed
- Types without a usable ExtractKey/subscript operator fail to compile rather than falling back to std::sort
- Open issue #3 (2017) reports MSVC/VS2015 'class template has already been defined' compile errors for some custom key types; the repo's last two commits addressed similar SFINAE issues but the issue was never closed

## Caveats and trade-offs

The repo ships only ska_sort.hpp and ska_sort_tests_and_benchmarks.cpp, with no README and no numbers. The claim lives in the author's 2016 blog post, which states no compiler, flags or CPU model (tier C). The post admits it degrades toward O(n log n) behavior on millions of long strings, and a reader comment reports it slower than std::sort on 1.2 billion uint64_t (unverified). The license (BSL-1.0) is stated only in the file headers; there is no LICENSE file and GitHub reports none. No commits since 2017-05-15.

Not a comparison sort; requires an extractable radix key (integers, bit-tricked floats, strings, tuples); not stable; needs O(n) auxiliary buffer memory; benefit shrinks for very large keys or non-radix-friendly types.

## Maintenance

Abandoned since the last commit on 2017-05-15 (5 open issues, no README, no LICENSE file though BSL-1.0 is stated in the file headers); it is a single copy-pasteable header, so age is low-risk to vendor, but expect to patch std::result_of yourself for a C++20 toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party blog post with ns/item charts against std::sort. Benchmark code is public (ska_sort_tests_and_benchmarks.cpp), but the post gives no compiler, flags or CPU model, so the tier is C.
- **Verifier notes:** The quotes match the post. The record's 'once arrays exceed roughly 128 elements' misplaced the 128-element threshold, which is the std::sort fallback cutoff, so claimed_speedup was reworded. The metadata checks out: BSL-1.0 from the file headers, 248 stars, last commit 2017-05-15, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://probablydance.com/2016/12/27/i-wrote-a-faster-sorting-algorithm/>
  - <https://github.com/skarupke/ska_sort>
  - <https://github.com/skarupke/ska_sort/blob/master/ska_sort.hpp>
  - <https://github.com/skarupke/ska_sort/blob/master/ska_sort_tests_and_benchmarks.cpp>
- **Sources the enricher read:**
  - <https://probablydance.com/2016/12/27/i-wrote-a-faster-sorting-algorithm/>
  - <https://github.com/skarupke/ska_sort>
  - <https://github.com/skarupke/ska_sort/blob/master/ska_sort.hpp>
  - <https://github.com/skarupke/ska_sort/blob/master/ska_sort_tests_and_benchmarks.cpp>
  - <https://github.com/skarupke/ska_sort/commits/master>
  - <https://github.com/skarupke/ska_sort/issues>
  - <https://github.com/skarupke/ska_sort/issues/2>
  - <https://github.com/skarupke/ska_sort/issues/3>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/skarupke/ska_sort`) · [data/wave0-seed/enrich/raw/github_com_skarupke_ska_sort.json](../../../data/wave0-seed/enrich/raw/github_com_skarupke_ska_sort.json) (enrichment confidence 0.5)

</details>
