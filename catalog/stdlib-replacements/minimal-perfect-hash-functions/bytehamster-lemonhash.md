# LeMonHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Learned monotone minimal perfect hash (key to sorted rank): about 3-5 bits/key and 7-19x faster queries than trie-based MMPHFs.

| | |
|---|---|
| **Beats** | Prior monotone MPHF implementations: the Grossi-Ottaviano C++ Centroid Hollow Trie, Hollow Trie and Path Decomposed Trie (ot/path_decomposed_tries), plus the Belazzougui et al. Java implementations from Sux4J of the Hollow Trie Distributor, Hollow Trie, ZFast Trie, LCP, LCP 2-step, PaCo, VLLCP and VLPaCo |
| **Claimed result** | Abstract: on synthetic random integers, 34% less space than the next larger competitor with about 16x faster queries; on real-world data, up to 19x faster queries than the next larger competitor at similar or better space; up to 2x faster construction than the competitor with the next best space usage (typically Hollow Trie variants); LeMonHash-VL (strings) is within 13% of the best competitors' space with up to 3x faster queries than the next larger competitor. Derived from page data (Table A.1): on uniform keys, 2718 vs 179 kQueries/s = 15.2x against the Java (Sux4J) Hollow Trie at 2.98 vs 4.54 bits/key; against the C++ Hollow Trie (351 kq/s, 4.61 bpk) it is 7.7x; on osm, 1338 vs 73 kq/s = 18.3x against the Java HTDist. |
| **Workload** | Rank queries (monotone minimal perfect hashing) over synthetic 64-bit integer datasets (uniform/normal/exponential, 100M keys) and real-world datasets (text, dna, urls, 5gram, fb, osm; 35M-800M keys), measuring query throughput, construction throughput, and bits/key vs prior MMPHF techniques |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2670 v3 @ 2.3GHz, Ubuntu 20.04, Linux 5.10.0, single-threaded |
| **Compiler and flags** | GNU C++ 11.1.0, -O3 -march=native |
| **Adoption** | 32 stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/ByteHamster/LeMonHash) · [benchmark](https://arxiv.org/pdf/2304.11012) |

## Verdict

The ESA 2023 paper (arXiv v3) ran single-threaded on an Intel Xeon E5-2670 v3 (2.3 GHz), with GCC 11.1.0 -O3 -march=native, and 5M random member queries per dataset. On 100M uniform 64-bit keys, LeMonHash (epsilon=31) answered 2.72M queries/s at 2.98 bits/key, against 0.35M at 4.61 for the Grossi-Ottaviano C++ Hollow Trie (7.7x) and 0.18M at 4.54 for Sux4J's Java Hollow Trie (15.2x). On 800M osm keys it answered 1.34M/s at 4.42 bits/key, against 0.073M for Sux4J's HTDist (18.3x) and 0.19M for the C++ Hollow Trie (7.2x). The Java baselines ran on OpenJDK 17 after one unmeasured JIT warm-up, each experiment ran twice and was averaged, and no std:: container, binary search or non-monotone MPHF was measured. The paper's own Table 2 reports 1.85M queries/s for the same uniform configuration, so per-query cost depends on the harness.

## Use it when

- Static, sorted sets of 64-bit integers (IDs, positions, cell IDs, timestamps) where you need each key's rank but cannot afford to store the keys. The paper measured 2.6-3.0 bits/key on uniform, normal, exponential and 5gram data and 4.4-4.9 bits/key on osm and fb, against 4.1-6.0 bits/key for the Hollow-Trie family and 6.1-7.9 for PaCo and ZFast.
- Query-heavy rank lookups on large sets (100M-800M keys). Single-threaded on a 2014 Xeon it answers 1.3-2.7M queries/s: about 7-8x the Grossi-Ottaviano C++ Hollow Trie and 12-21x the Sux4J Java Hollow Trie and HTDist, at the same or smaller space on every integer dataset except fb.
- Mapping a sorted key universe onto a dense value array while keeping locality. Consecutive keys land in consecutive slots, so range scans stay sequential. The paper notes this can make an MMPHF preferable to a plain MPHF for array indexing, because memory accesses in sorted order are cache-friendlier.
- Sorted string dictionaries (terms, k-mers) with LeMonHash-VL, when query speed matters more than the last 10-13% of space. On 35M web terms it answers 1.28M queries/s at 6.08 bits/key. The smallest competitor (HTDist) manages 0.09M/s at 5.40 bits/key, and the C++ Hollow Trie 0.35M/s at 5.84.
- Batch rebuilds where construction time counts. The default epsilon=31 integer build runs at 5.0-8.5 MKeys/s single-threaded (about 120-200 ns/key), up to 2x faster than the competitor with the next-best space.

## Skip it when

- You do not need sorted order. Every catalogued sibling is a non-monotone MPHF at about 1.5-3 bits/key, with catalogued query times in the tens of nanoseconds (on other hardware). In the paper's runs LeMonHash takes about 370-750 ns per integer query and 0.8-3 us per string query.
- Membership tests or changing key sets. Foreign keys get an arbitrary rank (there is no fingerprint), any insert means a full rebuild, and without serialization every process start rebuilds from the full in-memory key vector: 5-8.5 MKeys/s for integers, 2.3-2.7 MKeys/s for strings.
- Long URL-like strings, or when minimum space is the goal. On 106M URLs (average 105 bytes) LeMonHash-VL drops to 338K queries/s, and the C++ Centroid Hollow Trie is 18% faster there (399K/s at 8.36 vs 6.46 bits/key). On strings, LeMonHash-VL uses 10-13% more space than HTDist. On fb IDs, the Hollow tries and HTDist beat LeMonHash's 4.91 bits/key (4.50-4.84).
- Non-x86-64, non-GCC or non-Linux targets. support/util.h includes &lt;immintrin.h&gt; unconditionally, the string code assumes little-endian unaligned 64-bit loads, and CI covers only GCC 10-13 on x86-64 Ubuntu.
- Proprietary or permissively licensed products. LeMonHash is GPL-3.0 and links GPL-3.0 ByteHamster/Util.

## How it is fast

Trie-based MMPHFs walk a trie; LeMonHash instead learns the key distribution. A PGM-index (an error-bounded piecewise-linear model, epsilon=31 by default) gives each key an approximate rank, which is used directly as its bucket index, so most buckets hold 0 or 1 keys. The start rank of each bucket is kept as a unary bit vector with a pasta select structure (2n+o(n) bits). Only keys that collide get a local rank stored, in one of ten BuRR (bumped ribbon retrieval) structures picked by ceil(log2 bucket size); the paper puts BuRR's space overhead below 1%. A query is a predecessor search over the PGM segments, one linear-model evaluation, one select and at most one retrieval lookup. That is a small, flat number of memory accesses, where Hollow and ZFast tries chase pointers down O(log u) levels. LeMonHash-VL applies the same scheme recursively to strings. It strips each node's common prefix and turns the next 64-bit chunk into a key, compressing the chunk through a per-node reduced alphabet. It finds child nodes through a PTHash MPHF and per-level partitioned Elias-Fano offset arrays.

## Compared with alternatives

All catalogued siblings (PTHash, PtrHash, RecSplit, ShockHash, SicHash, PHast and others) are non-monotone MPHFs, so pick LeMonHash only when the output must be the key's rank in sorted order: range scans over a rank-indexed array, or rank queries on a static set without storing it. If any bijection to [0,n) will do, PTHash or PtrHash (about 3 bits/key and 37-45 ns queries in their entries) or ShockHash or RecSplit (1.56-1.8 bits/key) beat LeMonHash's 2.6-4.9 bits/key and roughly 0.37-0.75 us per integer query, though those numbers come from different hardware.

## Integration

| | |
|---|---|
| **Form** | header-only API (CMake INTERFACE target `LeMonHash`) that links small compiled shared libs: SimpleRibbon/BuRR, RibbonSorter and 4 sdsl-lite source files. It is consumed as a recursive git submodule via add_subdirectory; there are no install or package-config rules. |
| **Dependencies** | Git submodules: SimpleRibbon (Apache-2.0 BuRR wrapper, built as a shared lib, pulls ips2ra and tlx), ByteHamster/Util (GPL-3.0, pasta bit_vector, MurmurHash64), ds2i (partitioned Elias-Fano; its configuration.hpp uses boost::lexical_cast), sdsl-lite (bit utilities, partly compiled), PTHash (MIT, used by LeMonHash-VL for node lookup) and tlx. System: Boost (README requirement); CI also installs libtbb-dev. The PGM-index is re-implemented in-tree (include/bucket_mapping/support), not pulled as a dependency. |
| **Minimum toolchain** | C++20 (cxx_std_20) and CMake 3.25+. The README says GCC 11 or later, but the 2026-09-13 CI run built successfully on GCC 10, 11, 12 and 13. Clang and MSVC are not tested. The paper used GCC 11.1.0. |
| **Platforms** | x86-64 Linux as written. The integer variant pulls in &lt;immintrin.h&gt; through BucketOffsets.hpp -&gt; support/util.h. bextr uses BMI when __BMI__ is defined and falls back otherwise. ds2i is configured with SUCCINCT_USE_INTRINSICS, described as 'available on all x86-64'. -march=native is added only when LeMonHash is the top-level CMake project. The bundled benchmarks need glibc (mallinfo2). ARM, macOS and Windows are not documented. |
| **Thread safety** | Not documented, and operator() is non-const on every class. For integer LeMonHash the query path only reads: BucketOffsets::at and the PGM approximate_rank are const, and SimpleRibbon::retrieve is const, so concurrent queries through a shared non-const object look safe. LeMonHashVL is different: its query calls PartitionedEliasFano::at, which advances a ds2i enumerator stored as a member (move() writes m_position and the partition state). Concurrent queries on one LeMonHashVL object are therefore a data race; use one instance per thread or a lock. Construction is single-threaded. |
| **Drop-in for the baseline** | partial — it computes the same function (key -&gt; rank in [0,n)) as the Sux4J and Grossi-Ottaviano MMPHFs, but as a C++ class built from a sorted std::vector&lt;uint64_t&gt; or std::vector&lt;std::string&gt;. It has no Java API, no transformation strategies for arbitrary key types and no serialization. |

## Gotchas

- Input must be sorted and duplicate-free, and the whole set must be in a std::vector. The integer constructor throws std::invalid_argument('Data not sorted or duplicates found'), but LeMonHashVL checks order only through debug asserts, so sort and deduplicate strings yourself.
- Do not copy or move a built object. SimpleRibbon's MultiRetrievalDataStructure owns raw SimpleRibbon\* pointers and deletes them in a user-declared destructor, with no copy or move constructors. The implicit copy (which a move also falls back to) therefore creates two owners, and both delete the same pointers. Construct in place or behind new/unique_ptr, as the author's MMPHF-Experiments wrapper does.
- The defaults are the paper's tuned settings: LeMonHash&lt;&gt; uses SuccinctPGMBucketMapper&lt;31&gt;, and LeMonHashVL&lt;&gt; uses thresholds 128/128, alphabet reduction and UnalignedPGMBucketMapper&lt;63&gt;. epsilon=0 auto-tunes over 63/31/15 and roughly halves integer build speed (3.5 vs 6.5 MKeys/s on uniform keys) for little space gain. LinearBucketMapper and LeMonHashHeuristic only suit uniform data: on fb the linear mapper needs 34.35 bits/key and manages 0.8K queries/s.
- LeMonHashVL packs a node's common-prefix length into a 15-bit field and per-level offset indexes into 30 bits, and throws 'Increase offsetsOffsetBits' when the offsets overflow. Expect trouble with shared prefixes over 32 KB or with more than about 1B bucket offsets in one tree level. spaceBits() prints to stdout.

## Caveats and trade-offs

The headline 16x and 19x ratios are against Java (Sux4J) implementations, run on OpenJDK 17 with one unmeasured JIT warm-up run. Against the fastest C++ competitor at similar space, the gap is about 7-8x (derived from Table A.1). The comparison covers only academic MMPHF implementations, not BBHash, CMPH, PTHash, std::map or a sorted-array binary search. An MMPHF preserves key order (it returns the key's rank), so it is a different problem from a plain MPHF. The integer variant supports integer keys only; LeMonHash-VL covers strings. The Path Decomposed Trie crashes on integer inputs. Each experiment ran only twice and was averaged (the paper says variation is small).

GPLv3 is copyleft (no permissive reuse in proprietary code); like all MPHFs it returns arbitrary output for keys outside the original set; monotone MPHFs preserve key order (unlike plain MPHFs), which is a narrower guarantee that costs more space than a non-order-preserving MPHF; needs epsilon tuning for the PGM bucket mapper and depends on the BuRR retrieval structure and PGM-index as building blocks

## Maintenance

The code has barely changed since 2023: dependency and CMake upgrades in 2024-2025 and a SimpleRibbon/BuRR submodule bump on 2026-09-13, with CI green on GCC 10-13. It has 32 stars and has never had an issue or PR filed. GPL-3.0 and the submodule-based build limit it to GPL-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The paper (arXiv 2304.11012 v3, ESA 2023) compares LeMonHash with the named MMPHF baselines: Hollow Trie, Centroid Hollow Trie, Path Decomposed Trie, ZFast, PaCo and LCP variants. Section 8 states the Intel Xeon E5-2670 v3 CPU, GNU C++ 11.1.0 and -O3 -march=native. The benchmark code is public in ByteHamster/MMPHF-Experiments (cpp/comparison.cpp with cpp/benchmark/\*Contender.h, java/src/main/java/com/bytehamster/mmphfexperiments/Main.java, scripts/runExperiments.sh). That meets every Tier A condition.
- **Verifier notes:** All numbers in claimed_speedup appear in the abstract, and Table A.1 supports them: 15.2x uniform, 15.7x normal, 13.3x exponential, 18.3x osm, all against the next-larger-space competitor. The baseline field's claim about replacing std::map or binary search was not on the page, so I removed it. License GPL-3.0, 32 stars, last commit 2026-09-13 and not a fork all match gh.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2304.11012>
  - <https://github.com/ByteHamster/LeMonHash>
  - <https://github.com/ByteHamster/MMPHF-Experiments>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/cpp/comparison.cpp>
- **Sources the enricher read:**
  - <https://github.com/ByteHamster/LeMonHash>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/README.md>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/.github/workflows/build.yml>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/LeMonHash.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/LeMonHashVL.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/LeMonHashHeuristic.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/LeMonHashVLIndexed.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/support/util.h>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/support/sequence/BucketOffsets.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/support/sequence/PartitionedEliasFano.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/support/sequence/DuplicateFilter.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/bucket_mapping/SuccinctPGMBucketMapper.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/bucket_mapping/PGMBucketMapper.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/bucket_mapping/LinearBucketMapper.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/bucket_mapping/UnalignedPGMBucketMapper.hpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/include/bucket_mapping/support/SuccinctPGM.hpp>
  - <https://github.com/ByteHamster/LeMonHash/tree/main/include>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/benchmark/integerDistributions.cpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/benchmark/stringDistributions.cpp>
  - <https://github.com/ByteHamster/LeMonHash/blob/main/benchmark/simpleMmphfBenchmark.hpp>
  - <https://github.com/ByteHamster/LeMonHash/commits/main>
  - <https://github.com/ByteHamster/LeMonHash/issues?q=>
  - <https://github.com/ByteHamster/LeMonHash/actions>
  - <https://github.com/ByteHamster/LeMonHash/commit/3f6f2c1>
  - <https://github.com/ByteHamster/SimpleRibbon>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/include/MultiRetrievalDataStructure.hpp>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/include/SimpleRibbon.h>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/Util>
  - <https://github.com/ByteHamster/Util/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster-etc/ds2i/blob/master/partitioned_sequence.hpp>
  - <https://github.com/ByteHamster-etc/ds2i/blob/master/configuration.hpp>
  - <https://github.com/ByteHamster-etc/ds2i/blob/master/util.hpp>
  - <https://github.com/ByteHamster-etc/ds2i/blob/master/strict_sequence.hpp>
  - <https://github.com/simongog/sdsl-lite>
  - <https://github.com/jermp/pthash>
  - <https://github.com/lorenzhs/BuRR>
  - <https://github.com/ByteHamster/MMPHF-Experiments>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/cpp/benchmark/LeMonHashContender.h>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/cpp/benchmark/LeMonHashVLContender.h>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/cpp/benchmark/Contender.h>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/cpp/comparison.cpp>
  - <https://github.com/ByteHamster/MMPHF-Experiments/blob/main/scripts/runExperiments.sh>
  - <https://arxiv.org/pdf/2304.11012>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/bytehamster/lemonhash`) · [data/wave1-phf/enrich/raw/github_com_bytehamster_lemonhash.json](../../../data/wave1-phf/enrich/raw/github_com_bytehamster_lemonhash.json) (enrichment confidence 0.85)

</details>
