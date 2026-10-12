# Prefix Filter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Insert-only AVX-512 filter with a fixed \~0.37% false-positive rate; builds over 3.2x faster than cuckoo filters in similar space.

| | |
|---|---|
| **Beats** | Bloom filter, cuckoo filter |
| **Claimed result** | Build time for n=0.94\*2^28 (\~252M) keys: the prefix filter is faster than every cuckoo filter configuration by more than 3.2x (abstract: 3.2-3.5x) and faster than the vector quotient filter (TwoChoicer) by 1.39-1.46x. Cuckoo filter insertions slow down more than 27x as load grows, so its build time is close to that of a plain Bloom filter BF-16[k=11]. Negative-query throughput is higher than CF-12 at every load up to 95% (+55%, +40% and +2.8% at 50%, 70% and 90% load). Positive queries at 100% load are 28-40% slower than CF-12-Flex and 46-60% slower than CF-12. The plain Bloom filter is the slowest filter for queries. The blocked Bloom filter is about 2x faster than the prefix filter for all operations, but its false-positive rate is 3-6x higher. Space is 11.55-12.13 bits/key at a 0.37-0.39% false-positive rate (Table 3). |
| **Workload** | Space usage, false-positive rate, operation throughput at varying load, and build time for 0.94\*2^28 (\~252M) random 64-bit keys at false-positive rate \~2^-8, single-threaded, on an Intel Ice Lake server (PVLDB 15(7), 2022) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6336Y (Ice Lake) @ 2.40GHz, 64GiB RAM, 48KiB L1d/1.25MiB L2 per core, 36MiB shared L3 |
| **Compiler and flags** | GCC 10.3.0 on Ubuntu 20.04 (paper Sec. 7.1). The artifact repo's CMakeLists.txt builds the benchmark targets measure_perf, measure_built and measure_fpp with -Ofast -DNDEBUG, and CMAKE_CXX_FLAGS is -march=native. |
| **Adoption** | 50 stars; PVLDB 15(7), 2022 |
| **Last commit** | 2022-09-12 |
| **Links** | [repository](https://github.com/TomerEven/Prefix-Filter) · [benchmark](https://arxiv.org/abs/2203.17139) |

## Verdict

The paper's authors measured single-threaded runs on one Xeon Gold 6336Y (Ice Lake) core, built with GCC 10.3 using -Ofast -march=native, inserting 0.94\*2^28 (about 252M) random 64-bit keys. The prefix filter built more than 3.2x faster than every cuckoo filter setup (Fan et al.'s own code and a flexible variant) and 1.39-1.46x faster than the authors' vector quotient filter, using 11.55-12.13 bits/key at a 0.37-0.39% false-positive rate. It won on negative queries against CF-12 at every load up to 95% (+55% at 50% load, +2.8% at 90%), but lost 46-60% to CF-12 on positive queries at full load. There is no C++ standard library baseline for this kind of structure.

## Use it when

- Filters built once for immutable data, such as per-run filters in an LSM tree, where build time matters and about 12 bits/key at about 0.4% false positives is acceptable.
- Keys arrive one at a time and the filter fills to 90-95% of capacity. In the paper's tests, cuckoo filter inserts slow down more than 27x at high load, while prefix filter inserts decline only 1.9-2.8x from their plateau.
- Mostly-negative lookups in front of a slow store, on filters larger than the last-level cache. Negative queries were 55% and 40% faster than CF-12 at 50% and 70% load.
- Keys cannot all be gathered before building, which rules out static xor, binary fuse and ribbon filters.
- Single-threaded use on Linux, on an Intel server CPU with full AVX-512 including VBMI (the paper used Ice Lake).

## Skip it when

- You need deletions or counting. The Prefix Invariant makes deletion impossible (paper Sec. 4.1), and Remove throws.
- No AVX-512: AVX2-only x86, ARM or Apple Silicon. There is no scalar fallback, and the build fails with 'target specific option mismatch' on _mm256_permutexvar_epi8 (issue #1, open since 2024-01 with no fix).
- Mostly-positive lookups on a full filter. At 100% load, positive queries are 28-40% slower than CF-12-Flex and 46-60% slower than CF-12. If raw speed matters more than space, the blocked Bloom filter is about 2x faster on every operation, at a 3-6x higher false-positive rate in the paper's configuration.
- You need a tunable false-positive rate, or you don't know the key count. The 8-bit remainder fixes the rate near 0.37-0.39%. The spare is sized for the declared capacity, so going past it makes the spare insert fail and throw std::logic_error.
- Concurrent writers. The code has no synchronization. The paper (Sec. 4.4) sketches per-bin locking but did not implement it.

## How it is fast

It has two levels, following the Bercea-Even (BE) filter. The first level is a table of 32-byte pocket dictionaries (Elias-Fano/quotienting encoding: Q=25 lists, 8-bit remainders, 25 slots per bin), which holds about 94% of the fingerprints. A small second-level 'spare' filter holds the rest; by default the spare is TwoChoicer, the authors' own vector quotient filter. When a bin is full, an insert evicts the largest fingerprint among the bin and the new key to the spare. This keeps the 'Prefix Invariant': each bin holds the smallest fingerprints mapped to it, so a query can tell from the bin alone whether it needs the spare. As a result, about 92% of negative queries touch one cache line; cuckoo filters and vector quotient filters touch two. Inside a bin, a query broadcasts the 8-bit remainder and runs one AVX-512 byte compare over the body. That answers most negatives without a Select (PDEP/TZCNT) on the 50-bit header.

## Compared with alternatives

Pick it over xor/binary fuse (xor_singleheader) or BuRR only when keys must be inserted one at a time. Those two are static and need the whole key set before building. When the key set is known up front, they are smaller: Xor8 is 9.8 bits/key and BuRR is under 1.5% over the optimum, while the prefix filter is 11.55-12.13 bits/key, about 3.6 bits over the optimum. They also run without AVX-512.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | No external libraries. Tests/wrappers.hpp, which holds the Prefix_Filter class, also #includes the bundled Bloom, blocked Bloom and cuckoo filter headers. Python (matplotlib, pandas, brokenaxes) is needed only to plot results. |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17) and CMake 3.10+. The paper used GCC 10.3; the README says GCC 9.3 works, recommends newer releases, and names Clang as an option. CMake sets -march=native for everything. |
| **Platforms** | x86-64 Linux only. It needs AVX-512F/BW/VL plus VBMI (512-bit ops in the TwoChoicer spare, the 256-bit byte permute in the pocket dictionary) and BMI2 (PDEP/TZCNT/BZHI). The README says 'Intel. Support of AVX512 is a must.' Hash seeds are read from /dev/urandom. |
| **Thread safety** | Not documented. The Add path has no locks or atomics, so treat each instance as single-writer. The paper's concurrent per-bin-locking design is not implemented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Prefix_Filter and TC_shortcut own a raw posix_memalign buffer, free it in the destructor, and define no copy or move constructors. Copying one, for example by pushing it into a std::vector that reallocates, double-frees. Construct it in place or hold it through a pointer.
- Capacity is a hard limit. The spare holds 1.08 x 5.86% / 0.935 of max_items. Once it is full, Add prints to stdout and throws std::logic_error. If allocation fails, Prefix_Filter calls exit(-3). TC_shortcut instead returns with an uninitialized buffer (its assert is compiled out under -DNDEBUG).
- Add does not deduplicate: the paper assumes distinct keys, and inserting the same key twice uses two slots. Each instance seeds its Dietzfelbinger multiply-shift hash from /dev/urandom, so two filters over the same keys differ, and there is no way to persist or reload a filter.
- The README's build steps clone TheHolyJoker/Prefix-Filter with -b master. That repo returns 404; the real source is TomerEven/Prefix-Filter, and its only branch is main.

## Known shortcomings

- Needs AVX-512 including VBMI, x86 Linux only, no fallback (build failure #1 open since 2024). No delete (Remove throws), fixed \~0.37% FPR, no serialization, per-instance /dev/urandom hash seed. Hard capacity: a full spare throws logic_error; allocation failure calls exit(-3). No copy/move constructors but frees a raw buffer in the destructor, so copying double-frees; no duplicate-key check. Not packaged as a library (class lives in Tests/wrappers.hpp with bundled Bloom/cuckoo headers; README clone URL 404s). Positive queries at full load 46-60% slower than CF-12; blocked Bloom is 2x faster at 3-6x the FPR. Last commit 2022-09; a copy also lives in FastFilter/fastfilter_cpp.

## Caveats and trade-offs

The paper's 52%/79% figure is the cuckoo filter's query-throughput lead over the vector quotient filter at high load. It is not a lead over the prefix filter, so the earlier record misattributed it. The prefix filter beats CF-12 on negative queries at every load up to 95%, but it trails cuckoo filters on positive queries at full load (by 28-60%). The blocked Bloom filter is about 2x faster than the prefix filter for all operations, at a much higher space and false-positive cost. The README requires an Intel CPU with AVX-512. All numbers come from single-threaded runs on one Ice Lake machine. The license is Apache-2.0 per LICENSE.md, although GitHub's detector reports NOASSERTION. The paper is PVLDB 15(7) 2022 (the arXiv version is the full version). There have been no commits since 2022-09-12.

Requires AVX-512 hardware for the fast path; is an incremental filter (supports insertion but the paper focuses on a fixed configured capacity); this is a mixed win, not a strict speed win across every metric.

## Maintenance

This is an abandoned research artifact: the last commit was 2022-09-12, and the one open issue (an AVX-512 build failure) has had no fix since 2024. It is Apache-2.0 per LICENSE.md (GitHub reports NOASSERTION) and about 4k lines, so it can be vendored. FastFilter/fastfilter_cpp carries a copy in its benchmark harness (added 2022-07-11), compiled only when AVX512BW/VL/CD/DQ are enabled.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Artifact repo is public with benchmark drivers main-perf.cpp, main-built.cpp, main-fpp.cpp and RunAll.sh. The paper (Sec. 7.1) states GCC 10.3.0 and a Xeon Gold 6336Y, and the repo's CMakeLists.txt sets the flags (-Ofast -DNDEBUG, -march=native). Measured against plain Bloom, blocked Bloom and the cuckoo filter authors' own implementation.
- **Verifier notes:** Tier A holds. The 1.39-1.46x, 3.2-3.5x and 27x figures are on the arXiv page. The record said the prefix filter was 52%/79% behind cuckoo on queries, but that figure is cuckoo versus the vector quotient filter, so claimed_speedup and caveats are rewritten from Sec. 7.3-7.4. Metadata (Apache-2.0, 50 stars, last commit 2022-09-12, abandoned) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2203.17139>
  - <https://arxiv.org/pdf/2203.17139>
  - <https://github.com/TomerEven/Prefix-Filter>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/LICENSE.md>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/CMakeLists.txt>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/TomerEven/Prefix-Filter>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/README.md>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/CMakeLists.txt>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/LICENSE.md>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/example.cpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/Tests/wrappers.hpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/Prefix-Filter/min_pd256.hpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/Prefix-Filter/min_pd256.cpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/TC-Shortcut/TC-shortcut.hpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/TC-Shortcut/tc-sym.hpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/hashutil.h>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/main-built.cpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/RunAll.sh>
  - <https://github.com/TomerEven/Prefix-Filter/issues/1>
  - <https://github.com/TomerEven/Prefix-Filter/commits/main>
  - <https://github.com/TheHolyJoker/Prefix-Filter>
  - <https://arxiv.org/pdf/2203.17139>
  - <https://github.com/FastFilter/fastfilter_cpp>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/src/prefix/min_pd256.hpp>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/benchmarks/filterapi.h>
  - <https://hn.algolia.com/api/v1/search?query=%22prefix%20filter%22&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tomereven/prefix-filter`) · [data/wave6/enrich/raw/github_com_tomereven_prefix_filter.json](../../../data/wave6/enrich/raw/github_com_tomereven_prefix_filter.json) (enrichment confidence 0.86)

</details>
