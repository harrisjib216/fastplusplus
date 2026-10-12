# PGM-index (Piecewise Geometric Model index)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only learned index over sorted integer arrays that matches B+-tree lookup latency with an index orders of magnitude smaller.

| | |
|---|---|
| **Beats** | STX B+-tree (v0.9) and cache-efficient CSS-tree (authors' implementation), plus a 2-stage RMI (Recursive Model Index) |
| **Claimed result** | Static: PGM-index matches the fastest STX B+-tree's query latency using \~10,000x less space (87 KiB vs 874 MiB, 'four orders of magnitude') and matches the fastest CSS-tree using 82.7x less space (4 MiB vs 341 MiB); it dominates the 2-stage RMI in the space-time trade-off (RMI MAE 892±3729 vs 226±139 for PGM; RMI built 14.5x slower). Dynamic: the Dynamic PGM-index was 13-71% faster than the STX B+-tree for most query/update mixes (1.0% and 15.2% slower at 0.8 and 0.9 query fractions), using 611-3891x less space. |
| **Workload** | Point queries on a Web Logs dataset (\~715M timestamps, 8-byte keys, 128-byte payload), 10M random queries against an in-memory sorted array index |
| **Metric** | latency |
| **Hardware** | 2.3 GHz Intel Xeon Gold CPU, 192 GiB memory |
| **Adoption** | 874 stars; basis for the PyGM Python wrapper, widely cited in follow-on learned-index papers |
| **Last commit** | 2024-11-28 |
| **Links** | [repository](https://github.com/gvinciguerra/PGM-index) · [benchmark](http://www.vldb.org/pvldb/vol13/p1162-ferragina.pdf) |

## Verdict

In the authors' own PVLDB'20 experiments (2.3 GHz Xeon Gold with no model stated, compiler and flags not given, no stdlib baseline), on 715M 8-byte Web-log keys with 128-byte payloads and 10M random queries, PGM matched the fastest STX B+-tree v0.9 latency with an 87 KiB index against 874 MiB and matched the fastest CSS-tree with 4 MiB against 341 MiB. The Dynamic PGM (epsilon 64, 1B keys, 10M mixed operations) was 13-71% faster than the STX B+-tree except at 0.8 and 0.9 query fractions. The independent SOSD benchmark (Xeon Gold 6230) confirms PGM beats a B-tree (326 vs 482 ns, 14 vs 166 MB) but contradicts the paper's claim that it dominates RMI, blaming the paper's weaker RMI implementation.

## Use it when

- Read-mostly sorted arrays of 32/64-bit integer (or float/double) keys that need point, predecessor/lower_bound or range queries at B+-tree-like latency, with the index taking KiB-MiB instead of hundreds of MiB (paper: 87 KiB vs 874 MiB on 715M keys).
- Keys with a smooth or locally linear distribution, such as timestamps, log offsets or mostly sequential IDs, where few segments are needed and the index fits in L2/L3.
- Memory-constrained services or large mmap'd sorted key files (MappedPGMIndex), where a per-key index structure would not fit in RAM.
- You need a guaranteed worst-case search window (a fixed epsilon bound) rather than the data-dependent error of an RMI.
- Write-heavy integer key/value workloads on a single thread, where DynamicPGMIndex's LSM-style merging gave the highest insert throughput in the independent GRE benchmark at 100% writes.

## Skip it when

- Point-lookup latency matters more than memory: in the independent SOSD benchmark (200M 32-bit amzn keys) PGM took 326 ns, against 181 ns for RMI, 267 ns for RadixSpline and about 94-115 ns for hash tables that use far more memory.
- Read-heavy dynamic workloads: in the authors' own paper the Dynamic PGM was 1.0% and 15.2% slower than the best B+-tree at 0.8 and 0.9 query fractions, and GRE found its lookups dominated by ALEX and LIPP.
- String, composite or wider-than-word keys: the author says it is made for integers that fit in a machine word (issue #8), and key differences are converted to double for prediction.
- Builds with MSVC (the __int128 use breaks it, issue #19 still open), with -fno-exceptions (issue #56 open), or with concurrent writers (DynamicPGMIndex has no synchronisation).
- Hard-to-learn distributions, such as SOSD's Hilbert-projected osm cell IDs, where learned indexes lost to a simple radix lookup table and gave little gain over binary search.

## How it is fast

It computes an optimal piecewise linear epsilon-approximation (a convex-hull streaming algorithm) of the key-to-rank function, so each segment of (first key, float slope, uint32 intercept) predicts a position within +/-Epsilon. It then indexes the segment keys recursively with the same method (EpsilonRecursive defaults to 4), which gives a short tree with a linear scan over a few segments at each level instead of storing every key in inner nodes the way a B+-tree does. Because the index has m segments with m often 2-5 orders of magnitude below n, it stays in cache, and construction is one linear pass per level, parallelised with OpenMP when available.

## Compared with alternatives

Pick PGM over CARMI when index footprint and a provable epsilon-bounded search window matter more than raw lookup speed: CARMI claims an average 2.2x over the STX B+Tree but still uses about 0.77x the B+Tree's memory, while PGM's index is KiB-MiB. Pick rafaelkallis ART instead for a general mutable ordered map with byte-string keys; libmdbx, redb and TerarkDB are persistent transactional stores, not in-memory search indexes, so they do not substitute.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | None required. OpenMP is optional and parallelises construction (without it you get a '#pragma message' warning). A BSD-licensed SDSL subset (sdsl.hpp) is bundled for the compressed and Elias-Fano variants. MultidimensionalPGMIndex needs BMI2/AVX2, and MappedPGMIndex uses POSIX mmap. |
| **Minimum toolchain** | C++17 (CMake sets CMAKE_CXX_STANDARD 17; README uses g++ -std=c++17); GCC or Clang, because it uses __int128, __builtin_clzll and __builtin_prefetch. CI builds gcc and clang on ubuntu-22.04 and macos-12, with a gcc 13.2 fix in 2024. MSVC is not supported. |
| **Platforms** | Linux and macOS on x86-64 and arm64 (an Apple arm64 compile issue was fixed in 2021). On Windows only MinGW-w64 is reported to work. The multidimensional variant is x86-only (BMI2 _pdep/_pext). The bundled CMake adds -march=native. |
| **Thread safety** | The author says in issue #16 that all classes except DynamicPGMIndex are read-only after construction and safe for concurrent reads without synchronisation. DynamicPGMIndex has no internal locking, and concurrent use is not documented. |
| **Drop-in for the baseline** | partial — PGMIndex replaces only the search structure over a sorted array you already keep, not the B+-tree container itself. DynamicPGMIndex is a map-like container, but its API differs from STX btree_map/std::map: no operator[], size() is O(n), and iterators are forward-only. |

## Gotchas

- Sentinel values: std::numeric_limits&lt;K&gt;::max() (or infinity for floating-point keys) is reserved. Building on data that contains it throws, and querying it in DynamicPGMIndex segfaulted (issue #36); the GRE benchmark had to shift Facebook keys by -1. In DynamicPGMIndex with an arithmetic value type, numeric_limits&lt;V&gt;::max() is the delete tombstone and cannot be stored.
- Floating-point precision: slopes default to float (the paper used double). Users saw keys fall outside the returned [lo, hi) window on the SOSD books and GRE eth datasets (issues #30 and #45), and the author's fix was Floating=double or a wider search window. Results can differ across CPUs and compilers.
- Segment intercepts are uint32_t, so indexing more than about 4.29 billion positions throws overflow_error('Change the type of Segment::intercept to uint64'), which means editing the header.
- Errors are reported by throwing exceptions (unsorted input, the sentinel value, the tombstone value). DynamicPGMIndex::lower_bound tracks tombstoned keys in a std::set while scanning levels, so delete-heavy data slows it. An untriaged 2025 comment on issue #63 reports a wrong lookup for a duplicate-heavy uint64 array built on 2 cores.

## Known shortcomings

- The paper's own dynamic test has it 1-15% slower than a B+-tree at 0.8/0.9 query fractions; in GRE its lookups are beaten by ALEX and LIPP. The max key value is reserved as a sentinel (throws), and DynamicPGM uses the max value as a delete tombstone. Default float slopes miss keys on some datasets (#30, #45; use double). uint32 intercept throws above \~4.29B keys; MSVC breaks (__int128); no -fno-exceptions build; DynamicPGM has no locking. Stale since 2024-11, 12 open issues.

## Caveats and trade-offs

The VLDB'20 paper states only '2.3 GHz Intel Xeon Gold' (no model), with no compiler or flags. The static comparisons against the B+-tree and CSS-tree are same-speed at far less space rather than strictly faster. The strictly-faster wins are against RMI and, in the dynamic setting, 13-71% over the STX B+-tree on most (not all) workload mixes. All numbers come from the authors' own experiments.

Base structure targets static/append-friendly data (a dynamic variant exists but adds complexity); requires a sorted key array; the headline win vs traditional trees is space at matched latency, not a raw query-latency multiplier

## Maintenance

Stale: the last commit was 2024-11-28 (edge-case fixes for float and one-element inputs), and 12 issues are open, including MSVC and noexcept requests. It is Apache-2.0 and header-only, and the core static index is two headers of about 630 lines, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 13(8) 2020 paper compares PGM-index against the STX B+-tree v0.9, the authors' CSS-tree and a 2-stage RMI, and reports the 874 MiB vs 87 KiB and 341 MiB vs 4 MiB (82.7x) figures. The CPU is only '2.3 GHz Intel Xeon Gold' (no model) and no compiler or flags are given, so it cannot be A.
- **Verifier notes:** The claimed numbers appear verbatim in the paper (Sections 7.2 and 7.3). I added the dynamic-PGM 13-71% latency win over the STX B+-tree, a genuine speed claim the record missed. GitHub metadata was verified: Apache-2.0, 874 stars, not a fork, last commit 2024-11-28, so stale is correct.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** SOSD benchmark (independent): PGM-index 326 ns vs B-tree 482 ns lookups with 14 vs 166 MB, but behind RMI (181 ns) and RadixSpline (267 ns), contradicting the paper's 'dominates RMI'.
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol13/p1162-ferragina.pdf>
  - <https://github.com/gvinciguerra/PGM-index>
- **Sources the enricher read:**
  - <https://github.com/gvinciguerra/PGM-index>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/README.md>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/pgm_index.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/pgm_index_dynamic.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/pgm_index_variants.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/piecewise_linear_model.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/morton_nd.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/include/pgm/sdsl.hpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/CMakeLists.txt>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/.github/workflows/build.yml>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/c-interface/cpgm.h>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/examples/multiset.cpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/benchmark/benchmark.cpp>
  - <https://github.com/gvinciguerra/PGM-index/blob/master/test/tests.cpp>
  - <https://github.com/gvinciguerra/PGM-index/issues>
  - <https://github.com/gvinciguerra/PGM-index/issues/65>
  - <https://github.com/gvinciguerra/PGM-index/issues/64>
  - <https://github.com/gvinciguerra/PGM-index/issues/63>
  - <https://github.com/gvinciguerra/PGM-index/issues/62>
  - <https://github.com/gvinciguerra/PGM-index/issues/56>
  - <https://github.com/gvinciguerra/PGM-index/issues/51>
  - <https://github.com/gvinciguerra/PGM-index/issues/49>
  - <https://github.com/gvinciguerra/PGM-index/issues/45>
  - <https://github.com/gvinciguerra/PGM-index/issues/44>
  - <https://github.com/gvinciguerra/PGM-index/issues/36>
  - <https://github.com/gvinciguerra/PGM-index/issues/34>
  - <https://github.com/gvinciguerra/PGM-index/issues/30>
  - <https://github.com/gvinciguerra/PGM-index/issues/19>
  - <https://github.com/gvinciguerra/PGM-index/issues/16>
  - <https://github.com/gvinciguerra/PGM-index/issues/12>
  - <https://github.com/gvinciguerra/PGM-index/issues/10>
  - <https://github.com/gvinciguerra/PGM-index/issues/8>
  - <https://github.com/gvinciguerra/PGM-index/commits/master>
  - <http://www.vldb.org/pvldb/vol13/p1162-ferragina.pdf>
  - <https://pgm.di.unipi.it/docs/>
  - <https://pgm.di.unipi.it/docs/computational-complexities/>
  - <https://pgm.di.unipi.it/docs/building-the-code/>
  - <https://pgm.di.unipi.it/docs/tuner/>
  - <https://arxiv.org/pdf/2006.12804>
  - <https://arxiv.org/pdf/2207.02900>
  - <https://news.ycombinator.com/item?id=25899286>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/gvinciguerra/pgm-index`) · [data/wave6/enrich/raw/github_com_gvinciguerra_pgm_index.json](../../../data/wave6/enrich/raw/github_com_gvinciguerra_pgm_index.json) (enrichment confidence 0.85)

</details>
