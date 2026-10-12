# LearnedSort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> CDF-model-based sort for numeric arrays, \~4x faster than std::sort on random data, \~15-20x on sorted/duplicate data.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | Approximately 4.3x faster than GCC std::sort on Uniform data (\~1150ms vs \~5000ms) and similarly \~4x on Exponential/Gaussian/Zipf/TwoDups distributions; roughly 15-20x faster on Sorted/ReverseSorted/Identical data (\~50-60ms vs \~750-1000ms), per the README's bar chart |
| **Workload** | Sorting 50 million double-precision keys drawn from 8 distributions (Uniform, Exponential, Mixture of Gaussians, Zipf 0.75, TwoDups, Sorted, ReverseSorted, Identical), measured with Google Benchmark, comparing LearnedSort (a CDF-model-based sort) against std::sort, SkaSort, IS4o, BlockQuicksort, and Radix Sort. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6150 CPU @ 2.70GHz, 376GB RAM, Ubuntu 20.04 (kernel 5.4.0-26-generic) |
| **Compiler and flags** | GCC 9.3.0-10ubuntu2; CMake Release build with -O3 -march=native -fno-strict-overflow -mavx (CMakeLists.txt) |
| **Adoption** | 81 stars; published as 'The Case for a Learned Sorting Algorithm', SIGMOD 2020 |
| **Last commit** | 2021-08-20 |
| **Links** | [repository](https://github.com/anikristo/LearnedSort) · [benchmark](https://github.com/anikristo/LearnedSort/blob/master/plots/perf_charts.png) |

## Verdict

On 50M double-precision keys via Google Benchmark (GCC 9.3.0-10ubuntu2, CMake Release with -O3 -march=native -mavx, Intel Xeon Gold 6150), LearnedSort ran \~1080-1150ms vs std::sort's \~4850-5030ms (\~4.2-4.6x) across Uniform, Exponential, Mixture-of-Gaussians, Zipf-0.75, and TwoDups, and \~50-60ms vs std::sort's \~750-1000ms (\~15-20x) on Sorted, ReverseSorted, and Identical -- all read off the README's bar chart (plots/perf_charts.png), which prints no exact numeric labels.

## Use it when

- Large batches (tens of millions+) of primitive numeric keys (double/int/long) with no attached payload
- Data from a reasonably smooth/well-behaved distribution (uniform, exponential, Gaussian mixture, Zipfian, moderate duplicates) where the RMI's CDF approximation is accurate
- One-off or batch/offline sorts where the model-training cost amortizes over a large input, not per-call microsorts
- You can vendor a small header-only GPL-3.0 dependency and your project tolerates copyleft
- x86-64 Linux/GCC builds with AVX and -march=native, matching the environment this was actually benchmarked on

## Skip it when

- Sorting records/structs with payloads or string keys -- explicitly unsupported per the README's Limitations section
- Small inputs -- below roughly fanout x threshold (1000 x 100 = 100,000 elements by default) it just calls std::sort, so there's no upside
- GPL-3.0 is unacceptable for the target codebase -- heavier copyleft than most sibling sort libraries in this catalog
- Need active maintenance -- no commits since August 2021, all filed issues closed, unmaintained academic prototype
- Sorted, reverse-sorted, or all-duplicate inputs where you want a general-purpose winner -- the project's own chart shows IS4o matching or beating LearnedSort there

## How it is fast

Builds a two-layer 'recursive model index' (RMI): a root linear model plus, by default, 1000 leaf linear models trained on a 1% sample of the keys, which together approximate the empirical CDF. Each key's model-predicted CDF value picks one of \~1000 buckets directly (O(1) per key instead of O(log n) comparisons), the array is partitioned into those buckets in one pass, and each bucket is finished with std::sort/insertion sort. Separately, sort() first does a linear is_sorted/is_reverse_sorted check and returns immediately if it hits, which is why Sorted/ReverseSorted/Identical inputs are \~15-20x faster than std::sort -- that path bypasses the CDF model entirely.

## Compared with alternatives

Pick LearnedSort over IPS4o/BlockQuicksort/x86-simd-sort/radix_sort when you have large batches (10M+) of doubles or ints from a smooth distribution and accept GPL-3.0 plus an unmaintained codebase for the \~4x win; for sorted/duplicate-heavy or adversarial data, or if you need ongoing support, IS4o matches or beats it on those inputs per LearnedSort's own benchmark chart.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the sort itself (STL only, include/learned_sort.h + rmi.h + utils.h); the repo's benchmark/test harness additionally pulls in Google Benchmark, Google Test, and several third-party sort implementations, but those aren't needed to call learned_sort::sort |
| **Minimum toolchain** | C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20); benchmarked with GCC 9.3.0-10ubuntu2 |
| **Platforms** | Only tested on Linux (RHEL 7, Ubuntu 20.04); Release flags include -march=native -mavx, so x86-64 with AVX is assumed. A Windows/MinGW-w64 GCC10 user hit a correctness bug (issue #16), since fixed |
| **Thread safety** | not documented; sort() is single-threaded with no synchronization primitives in the header, and no stated guarantee for concurrent calls on different ranges |
| **Drop-in for the baseline** | partial -- explain: learned_sort::sort(begin, end) mirrors std::sort's iterator-pair signature exactly, but it lives in its own namespace, so every call site must change from std::sort to learned_sort::sort rather than being a transparent alias |

## Gotchas

- Automatically short-circuits to std::sort for inputs at or below \~fanout\*threshold elements (100,000 by default) or when RMI training fails, so the learned path silently never runs on small inputs
- The huge Sorted/ReverseSorted speedups come from an explicit is_sorted()/is_reverse_sorted() linear-scan pre-check with early return, not from the CDF model doing work
- Historically had several correctness bugs specific to integer key types (slope underflow, int-division in RMI training, failures with many repeated keys) -- all filed as issues and fixed via PRs by mid-2021, but there's been no activity since to catch anything similar
- No payload/tuple or string-key support (README 'Limitations'); only bare numeric arrays are sortable

## Caveats and trade-offs

The README gives no benchmark numbers in text. The speedups were read off the bar chart (plots/perf_charts.png), so they are visual estimates, not exact printed figures. On Sorted, ReverseSorted and Identical inputs, IS4o is as fast as or faster than LearnedSort. The README says LearnedSort handles only numeric keys: no payloads (records) and no string keys. No commits since 2021; this is an unmaintained academic research prototype.

GPL-3.0 is a heavier copyleft obligation than most sort peers here; only supports numeric keys without payloads or string keys per the README's stated Limitations; training the CDF model adds setup cost that is not amortized on small inputs.

## Maintenance

Abandoned academic prototype: no commits since August 2021 and every filed issue is closed with no further activity, but it's a small header-only, GPL-3.0 library, so it's easy to vendor and freeze at the last known-good GCC 9/10 toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** perf_charts.png plots LearnedSort vs Std::sort on 50M keys. The in-repo benchmark src/main_synth.cc (Google Benchmark, StdSort target) is built by CMakeLists.txt in Release with -O3 -march=native -mavx. The README states GCC 9.3.0 and the Xeon Gold 6150 machine; the work was also peer-reviewed at SIGMOD 2020.
- **Verifier notes:** The chart confirms the estimates: Uniform \~1130ms vs \~5000ms (\~4.4x), other random distributions \~4.2-4.6x, and Sorted/Reverse/Identical \~50ms vs \~750-1000ms. The repo was transferred from learnedsystems/LearnedSort (that URL redirects here). Metadata verified: GPL-3.0, 81 stars, not a fork, last commit 2021-08-20 (abandoned).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/anikristo/LearnedSort>
  - <https://raw.githubusercontent.com/anikristo/LearnedSort/master/plots/perf_charts.png>
  - <https://github.com/anikristo/LearnedSort/blob/master/CMakeLists.txt>
  - <https://github.com/anikristo/LearnedSort/blob/master/src/main_synth.cc>
  - <https://github.com/learnedsystems/LearnedSort>
- **Sources the enricher read:**
  - <https://github.com/anikristo/LearnedSort>
  - <https://github.com/anikristo/LearnedSort/blob/master/CMakeLists.txt>
  - <https://github.com/anikristo/LearnedSort/blob/master/include/learned_sort.h>
  - <https://github.com/anikristo/LearnedSort/blob/master/include/rmi.h>
  - <https://github.com/anikristo/LearnedSort/issues>
  - <https://github.com/anikristo/LearnedSort/issues/16>
  - <https://github.com/anikristo/LearnedSort/issues/8>
  - <https://raw.githubusercontent.com/anikristo/LearnedSort/master/plots/perf_charts.png>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/anikristo/learnedsort`) · [data/wave1/enrich/raw/github_com_anikristo_learnedsort.json](../../../data/wave1/enrich/raw/github_com_anikristo_learnedsort.json) (enrichment confidence 0.75)

</details>
