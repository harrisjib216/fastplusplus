# pdqsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Zlib` · 🔴 abandoned

> Header-only C++ drop-in std::sort replacement: pattern-defeating quicksort with branchless partitioning and a guaranteed O(n log n) worst case.

| | |
|---|---|
| **Beats** | std::sort, std::stable_sort |
| **Claimed result** | Approximate, read from the README bar chart (sorting 10^6 ints, cycles per element, i5-4670k @ 3.4GHz) (derived from page data). Vs GCC std::sort, pdqsort is faster on all 8 distributions: shuffled \~113 vs \~220 (\~1.9x), shuffled 16 values \~20 vs \~84 (\~4x), descending \~7 vs \~34 (\~5x), pipe organ \~118 vs \~266 (\~2.2x), push front \~45 vs \~319 (\~7x), and more than 10x on all equal, ascending and push middle (\~3-4 vs \~38-179). Vs std::stable_sort it is faster on shuffled (\~113 vs \~273, \~2.4x) and most patterns, but slower on pipe organ (\~118 vs \~51) and about equal on push front (\~45 vs \~45). |
| **Workload** | Median cycles per element (rdtsc, bench/bench.cpp) sorting a std::vector&lt;int&gt; of 10^6 elements under 8 distributions (shuffled, shuffled 16 values, all equal, ascending, descending, pipe organ, push front, push middle), compared to GCC libstdc++ std::sort and std::stable_sort. |
| **Metric** | throughput |
| **Hardware** | i5-4670k @ 3.4GHz (stated in the x-axis label of the README benchmark chart) |
| **Compiler and flags** | g++ (GCC, version unstated) -std=c++11 -O2 -m64 -march=native (README and bench/readme.txt) |
| **Adoption** | 2.5k stars; algorithm concepts adopted in Rust's sort_unstable and referenced widely in later stdlib sort redesigns |
| **Last commit** | 2021-03-14 |
| **Links** | [repository](https://github.com/orlp/pdqsort) · [benchmark](https://github.com/orlp/pdqsort) |

## Verdict

Per the record's verified README bar chart (std::vector&lt;int&gt;, 10^6 elements, i5-4670k @ 3.4GHz, g++ -std=c++11 -O2 -m64 -march=native), pdqsort beat GCC libstdc++ std::sort on all 8 tested distributions, from \~1.9x on shuffled ints to over 10x on ascending/all-equal/push-middle patterns. Against std::stable_sort it was faster on most patterns (\~2.4x on shuffled) but \~2.3x slower on pipe organ and about tied on push front.

## Use it when

- Sorting std::vector/array of built-in arithmetic types (int, float, double) with the default comparator, where the branchless fast path auto-activates
- Data likely to contain patterns: nearly-sorted, reverse-sorted, many duplicate keys, or one misplaced element in an otherwise sorted run
- Header-only C++03/C++11 codebases that want a drop-in std::sort replacement without adding a build/link dependency
- Large arrays (1000+ elements) where branch-misprediction overhead in a naive quicksort partition loop matters
- Need a guaranteed O(n log n) worst case (heapsort fallback) without giving up quicksort's average-case speed

## Skip it when

- Need a stable sort (equal elements keep relative order) — no stable variant is provided, unlike std::stable_sort
- Comparator itself is expensive (e.g. calls into an interpreted-language callback) — issue #20 shows pdqsort can invoke the comparator more often than glibc qsort/introsort, making it slower than std::sort or qsort when comparison cost dominates
- Data shaped like a 'pipe organ' (ascending then descending) sorted against libstdc++ std::stable_sort — the verified README chart shows pdqsort \~2.3x slower there, and roughly tied on 'push front'
- Need MSVC 64-bit builds warning-clean — open issue #22 (int64-&gt;int conversion warnings) is unresolved
- Need std::execution parallel policies or a maintained upstream — no commits since 2021-03-14 and issue #16 (C++17 parallel execution) is still open

## How it is fast

Quicksort with median-of-3 pivoting (Tukey's ninther above 128 elements), switching to insertion sort below 24 elements, and falling back to std::make_heap/std::sort_heap after O(log n) highly unbalanced (&lt;12.5% or &gt;87.5%) partitions, which bounds the worst case at O(n log n) like introsort. After every partition it checks whether the sequence was already partitioned and, if so, attempts a move-bounded insertion sort, giving linear time on sorted/equal/nearly-sorted patterns. For arithmetic types with a default comparator it uses the branchless partitioning technique from Edelkamp & Weiss's BlockQuicksort paper, filling small index buffers with unconditional stores to avoid branch mispredictions during partitioning.

## Compared with alternatives

Prefer pdqsort over Highway (vqsort) when you can't require AVX2/AVX3 hardware or want to avoid a SIMD library dependency, and over ska_sort when your keys aren't specifically skewed/geometric-distributed integers. vergesort is the closest comparison (same libstdc++ pattern-detection premise, also unstable-vs-stable tradeoffs), but pdqsort additionally documents a branchless partitioning fast path for arithmetic types with default comparators.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only: &lt;algorithm&gt;, &lt;cstddef&gt;, &lt;functional&gt;, &lt;utility&gt;, &lt;iterator&gt;, plus &lt;cstdint&gt;/&lt;type_traits&gt; under C++11) |
| **Minimum toolchain** | C++03 compiles (branch-based path only); C++11+ enables automatic branchless dispatch and move semantics |
| **Platforms** | any (portable C++, no SIMD/architecture-specific intrinsics); MSVC 64-bit builds emit C4244 int64-&gt;int conversion warnings (open issue #22) |
| **Thread safety** | not documented — stateless free template functions with no shared/global state; ordinary iterator-range algorithm semantics apply |
| **Drop-in for the baseline** | partial — matches std::sort's call signature exactly (pdqsort(begin, end[, comp])), but it is unstable, so it is a drop-in only for std::sort, not for std::stable_sort |

## Gotchas

- Branchless auto-dispatch only triggers for arithmetic value types compared with std::less/std::greater under C++11; custom structs or comparators always take the slower branch-based path unless you call pdqsort_branchless explicitly
- Can make more comparator calls than a plain qsort/introsort in some cases (issue #20), so it loses to std::sort/qsort when the comparator itself is costly, even though it does fewer swaps
- Switches to std::make_heap/std::sort_heap after O(log n) highly unbalanced partitions, so pathological inputs degrade to heapsort speed, not quicksort speed
- Comparator ordering requirements (strict weak ordering vs. total order) are not documented in the README (issue #28, open question, unanswered as of last commit)

## Caveats and trade-offs

Numbers appear only in a bar-chart image (i.imgur.com/1RnIGBO.png), so the values are approximate readings. The CPU is printed in the chart's axis label (bars.py writes its cpu argument into the xlabel). Not faster than std::stable_sort on pipe organ (\~2.3x slower) and about equal on push front. Only 10^6 ints are charted. GCC version and run date are unstated, so the libstdc++ tested is old. No commits since 2021-03-14 (more than 3 years), so abandoned.

Not stable (no stable variant provided); branchless fast path only applies to arithmetic types with default std::less/std::greater; falls back to heapsort on adversarial inputs.

## Maintenance

Abandoned: no commits since 2021-03-14, the same day an integer-overflow fix (issue #13) landed; a later MSVC-warning issue (#22, 2022) and a C++17 parallel-execution request (#16, 2024) remain open and unaddressed. zlib-licensed and a single \~350-line header, so it's cheap to vendor and patch yourself if needed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now A.
- **Tier reason:** Benchmark code is public (bench/bench.cpp, plotted by bench/bars.py). The README names GCC and the flags -std=c++11 -O2 -m64 -march=native, and the README chart's x-axis names the CPU ("Cycles per element (i5-4670k @ 3.4GHz)"), so code, compiler, flags and CPU are all stated; upgraded from C. The GCC version is not stated.
- **Verifier notes:** Tier upgraded C-&gt;A: the CPU the record called unstated is printed on the README chart axis. claimed_speedup overstated the win over std::stable_sort (slower on pipe organ, tie on push front) and was corrected with approximate chart readings. The Rust sort_unstable adoption claim in stars_or_usage was not verified (Rust docs fetch did not show it) and was left unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/orlp/pdqsort>
  - <https://github.com/orlp/pdqsort/blob/master/bench/readme.txt>
  - <https://github.com/orlp/pdqsort/blob/master/bench/bars.py>
  - <https://github.com/orlp/pdqsort/blob/master/bench/bench.cpp>
  - <https://i.imgur.com/1RnIGBO.png>
  - <https://doc.rust-lang.org/1.79.0/std/primitive.slice.html>
- **Sources the enricher read:**
  - <https://github.com/orlp/pdqsort>
  - <https://github.com/orlp/pdqsort/blob/master/pdqsort.h>
  - <https://github.com/orlp/pdqsort/blob/master/bench/readme.txt>
  - <https://github.com/orlp/pdqsort/issues/20>
  - <https://github.com/orlp/pdqsort/issues/13>
  - <https://github.com/orlp/pdqsort/issues/22>
  - <https://github.com/orlp/pdqsort/issues/28>
  - <https://github.com/orlp/pdqsort/issues/3>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/orlp/pdqsort`) · [data/wave0-seed/enrich/raw/github_com_orlp_pdqsort.json](../../../data/wave0-seed/enrich/raw/github_com_orlp_pdqsort.json) (enrichment confidence 0.8)

</details>
