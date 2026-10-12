# SicHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Cuckoo-hashing-plus-retrieval (minimal) perfect hash for static key sets: about 2.1 bits/key against BBHash's 3.3-3.7, with faster queries.

| | |
|---|---|
| **Beats** | BBHash |
| **Claimed result** | Paper (ALENEX 2023): SicHash 'dominates the Pareto front for load factors from 0.85 to 0.97' in construction throughput vs space for N=5M and N=20M. The competitors are BBHash, cmph's CHD, BDZ, BMZ and FCH, PTHash, RecSplit and WBPM. The paper says: 'For some space requirements, SicHash can be constructed up to 3 times faster than the next best competitor.' Appendix Table 1 (N/M=0.95): SicHash uses 1.75 bits/object at 3.27 MObjects/s. PTHash uses 1.76 at 0.61 and RecSplit 1.78 at 0.76, so SicHash builds about 4.3-5.4x faster at the same space (derived from page data). Against BBHash the comparison is only in plots. BBHash is configured at 3.5-4.0 bits/object, against 1.8 for the PHFs (Figure 5). In the Figure 5 query plot, SicHash has higher query throughput than BBHash at every N from 10^6 to 2x10^8. |
| **Workload** | Construction throughput vs bits/object Pareto fronts for N = 1M, 5M and 20M keys at load factors 0.8-0.97 and for minimal perfect hashing. Query throughput is measured for N = 10^6 to 2x10^8. Keys are random strings of length 10-50. All runs are single-threaded. The competitors are BBHash, cmph (CHD, BDZ, BMZ, FCH), PTHash, RecSplit and WBPM. |
| **Metric** | memory |
| **Hardware** | Intel Xeon E5-2670 v3 @ 2.3 GHz, Ubuntu 20.04, Linux 5.10.0. The appendix also shows an AMD Ryzen 3950X and an ARM Neoverse-N1. |
| **Compiler and flags** | GCC 11.1.0, -O3 -march=native |
| **Adoption** | 20 stars |
| **Last commit** | 2025-09-30 |
| **Links** | [repository](https://github.com/ByteHamster/SicHash) · [benchmark](https://arxiv.org/pdf/2210.01560) |

## Verdict

The ALENEX'23 paper ran single-threaded on random 10-50-byte strings, on a dual-socket Xeon E5-2670 v3 with GCC 11.1 -O3 -march=native. SicHash leads the construction-throughput-vs-space Pareto front at load factors 0.85-0.97 for 5M/20M keys (for example 1.75 bits/key built at 3.27 MKeys/s, against PTHash's 0.61 and RecSplit's 0.76 at 1.76-1.78 bits). BBHash appears only in plots, at 3.5-4.0 bits/key, where it builds faster but queries slower at every N from 10^6 to 2x10^8. The author's thesis re-ran it on an i7-11700 with GCC 11.2 and 100M keys, and gives the BBHash gap in numbers: 2.197 vs 3.288 bits/key, 148 vs 172 ns/key to build, and 66 vs 93 ns/query. No std:: container was compared.

## Use it when

- Replacing BBHash on static sets of millions to hundreds of millions of keys to cut memory by about a third. At 100M keys the author measured 2.08-2.20 vs 3.29-3.71 bits/key, faster lookups (64-66 vs 85-93 ns) and similar single-thread build time (148-180 vs 135-172 ns/key).
- Non-minimal PHFs at load factor 0.85-0.97, such as slot indexes into a slightly oversized array. The paper puts it on the construction-vs-space Pareto front for 5M-20M keys: 1.61 bits/key at 0.85 and 1.75 bits/key at 0.95.
- Key sets that are rebuilt often (index rebuilds, batch pipelines), where build cost matters as much as lookups. The author's thesis reports builds up to about 2x faster than PTHash/PHOBIC at comparable space.
- String keys, or keys you already hash to 64 bits, in a GPL-compatible C++20/CMake project on Linux with GCC 11+ or Clang 16+.

## Skip it when

- You need the smallest MPHF. The minimal variant bottoms out near 2.0-2.1 bits/key, while ShockHash, SIMDRecSplit and RecSplit reach 1.49-1.81 bits/key. The paper itself says that for MPHFs, RecSplit produces the smallest data structures.
- Lookup latency or build throughput is the only metric. PTHash/PHOBIC answer queries in 35-60 ns vs SicHash's 64-66 ns at 100M keys. Above 3 bits/key, fingerprinting builds (FiPS at 45-51 ns/key, and BBHash in the paper's heat map) construct faster.
- Closed-source or permissively licensed products. SicHash and its ByteHamster/Util dependency are plain GPL-3.0.
- Many-core builds or very large sets. Most build time goes to BuRR, which has no parallel implementation, so the partitioned build scaled poorly on a 64-core AMD machine. Construction is in-memory only (an external-memory build is only sketched in the paper), and the paper tested up to 2x10^8 keys.
- Tiny sets, or MSVC/Windows/macOS targets. Below about 1M keys it no longer dominates (paper Appendix B). The 4-key README example segfaulted until a Nov 2024 fix (issue #4). CI covers only Linux GCC/Clang.

## How it is fast

Keys are radix-sorted (ips2ra) into buckets of about 5000 keys. Each bucket becomes a small irregular cuckoo hash table: a hash threshold gives each key 2, 4 or 8 candidate slots, keys are placed with rattle kicking, and tables are filled past the asymptotic load threshold. Small tables vary in how full they can get, so a retry with a new 16-bit seed usually succeeds. Only the chosen slot index is kept (1, 2 or 3 bits per key), in three BuRR bumped-ribbon retrieval structures with about 1% overhead, plus one 64-bit offset/seed word per bucket; minimal PHFs remap slots &gt;= N into holes through an Elias-Fano list, the same trick PTHash uses. A query is one retrieval lookup, one bucket-metadata read and a hash. Those are three independent memory accesses that can be prefetched, with no BBHash-style per-level rank lookups and no RecSplit-style tree decoding.

## Compared with alternatives

Pick SicHash over PTHash when build time matters at about 2 bits/key. The thesis measured 148-180 vs 268 ns/key at 100M keys, and the paper shows 3.27 vs 0.61 MKeys/s at 1.75 bits/key; the cost is slower lookups (about 65 vs 35-60 ns/query). Pick it over the RecSplit family (RecSplit, SIMDRecSplit, ShockHash) when query latency matters more than 0.3-0.7 extra bits/key: 64-66 vs 118-157 ns/query at 2.08-2.20 vs 1.49-1.81 bits/key.

## Integration

| | |
|---|---|
| **Form** | header-only API (CMake INTERFACE target) that links a compiled shared lib (SimpleRibbon, a BuRR wrapper); consumed via add_subdirectory with recursive git submodules |
| **Dependencies** | SimpleRibbon/BuRR (Apache-2.0, built as a shared lib), ips2ra, ByteHamster/Util (GPL-3.0; Elias-Fano on pasta-bit-vector, MurmurHash64) and tlx, all as git submodules; the CI also installs libtbb-dev |
| **Minimum toolchain** | C++20, CMake 3.25+; CI tests GCC 11-14 and Clang 16-18 |
| **Platforms** | Linux x86-64 in CI; the paper also ran it on an AMD Ryzen 3950X and an ARM Neoverse-N1. Uses GCC/Clang builtins (__builtin_prefetch, __uint128_t). Windows/macOS/MSVC are not documented. -march=native is added only when SicHash is the top-level CMake project |
| **Thread safety** | Not documented. Lookups are const and touch no mutable state, so concurrent reads of a built object look safe. SicHash builds single-threaded; PartitionedSicHash builds one sub-function per thread, which adds a partition step to every query |
| **Drop-in for the baseline** | no |

## Gotchas

- Construction prints progress to std::cout by default; set `config.silent = true`. `spaceUsage()` on a minimal SicHash&lt;true&gt; always prints a 'Remap space' line.
- Keys must be std::string (hashed internally with MurmurHash64) or values you have already hashed. Raw integers passed to the uint64_t constructor trip a sanity check that throws invalid_argument. Every key collapses to one 64-bit hash, and there is no duplicate-key check, so duplicates or 64-bit collisions are not detected; the behavior is not documented.
- A loadFactor of 0.999 or more throws; use SicHash&lt;true&gt; to get a minimal PHF. For minimal PHFs, pick the minimalFanoLowerBits template argument (3/4/5 for load factor &lt;0.89/&lt;0.94/&lt;0.97). Thresholds that are too aggressive throw logic_error after 65,536 seed retries in one bucket.
- A SicHash object can be neither copied nor moved: its BuRR members are move-only, it has a user-declared destructor and it owns a raw Elias-Fano pointer. Hold it through a pointer, as the author's MPHF-Experiments wrapper does. `writeTo()` dumps raw structs, and the format tag is checked only by assert(), so files are not portable across compilers or endianness and are not validated in release builds.

## Caveats and trade-offs

Numbers against BBHash and cmph appear only as plots. The paper's only numeric table (Appendix C) compares SicHash with PTHash and RecSplit. In the construction plots, BBHash reaches the highest raw construction throughput, but at much larger space (3.5-4.0 bits/object). SicHash wins on space at comparable build throughput and on query throughput. The competitor benchmarks are in a separate repo (ByteHamster/MPHF-Experiments, GPL-3.0), which has changed since the 2022 paper. The license is GPL-3.0 (copyleft).

Depends on the BuRR retrieval data structure as a submodule; cuckoo-hashing-based construction with overloading needs careful parameter tuning; plain GPLv3 licensing (no stated runtime exception).

## Maintenance

The author still maintains it: last commit 2025-09-30, CI on GCC 11-14 and Clang 16-18, no open issues. Commits are sporadic, it has 20 stars, and GPL-3.0 plus the submodule-based CMake build limit vendoring to GPL-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The peer-reviewed ALENEX'23 paper compares SicHash against BBHash and cmph (CHD, BDZ, BMZ, FCH). It states the Intel Xeon E5-2670 v3 CPU, GCC 11.1.0 and the flags -O3 -march=native. The benchmark code is public: the paper and README point to github.com/ByteHamster/SicHash (src/sicHashBenchmark.cpp, Dockerfile) and to github.com/ByteHamster/MPHF-Experiments (contenders/fingerprinting/BBHashContender.cpp, contenders/bucketplacement/ChdContender.cpp).
- **Verifier notes:** The record's 'metric: memory' does not fit well. The paper's claim is construction throughput at a given space, plus query throughput, so 'throughput' fits better, but metric is not a correctable field. The claimed_speedup in the record had no numbers, so numbers_found_on_page is null. It has been replaced with figures stated in the paper.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2210.01560>
  - <https://github.com/ByteHamster/SicHash>
  - <https://github.com/ByteHamster/SicHash/blob/main/README.md>
  - <https://github.com/ByteHamster/SicHash/blob/main/Dockerfile>
  - <https://github.com/ByteHamster/SicHash/blob/main/scripts/dockerVolume/figure-1.sh>
  - <https://raw.githubusercontent.com/ByteHamster/SicHash/main/plots-construction.png>
  - <https://raw.githubusercontent.com/ByteHamster/SicHash/main/plots-query.png>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/ByteHamster/SicHash>
  - <https://github.com/ByteHamster/SicHash/blob/main/README.md>
  - <https://github.com/ByteHamster/SicHash/blob/main/include/SicHash.h>
  - <https://github.com/ByteHamster/SicHash/blob/main/include/PartitionedSicHash.h>
  - <https://github.com/ByteHamster/SicHash/blob/main/include/sichash/IrregularCuckooHashTable.h>
  - <https://github.com/ByteHamster/SicHash/blob/main/include/sichash/TinyBinaryCuckooHashTable.h>
  - <https://github.com/ByteHamster/SicHash/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/SicHash/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/SicHash/blob/main/Dockerfile>
  - <https://github.com/ByteHamster/SicHash/blob/main/.github/workflows/build.yml>
  - <https://github.com/ByteHamster/SicHash/blob/main/src/example.cpp>
  - <https://github.com/ByteHamster/SicHash/blob/main/src/sicHashBenchmark.cpp>
  - <https://github.com/ByteHamster/SicHash/blob/main/src/BenchmarkData.h>
  - <https://github.com/ByteHamster/SicHash/blob/main/CITATION.cff>
  - <https://github.com/ByteHamster/SicHash/issues?q=is%3Aissue>
  - <https://github.com/ByteHamster/SicHash/issues/2>
  - <https://github.com/ByteHamster/SicHash/issues/4>
  - <https://github.com/ByteHamster/SicHash/issues/5>
  - <https://github.com/ByteHamster/SicHash/commits/main>
  - <https://arxiv.org/pdf/2210.01560>
  - <https://publikationen.bibliothek.kit.edu/1000176432/155628357>
  - <https://github.com/ByteHamster/SimpleRibbon>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/include/SimpleRibbon.h>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/src/SimpleRibbon.cpp>
  - <https://github.com/ByteHamster/Util>
  - <https://github.com/ByteHamster/Util/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/Util/blob/main/include/bytehamster/util/EliasFano.h>
  - <https://github.com/ByteHamster/Util/blob/main/include/bytehamster/util/Function.h>
  - <https://github.com/lorenzhs/BuRR>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/retrievalbased/SicHashContender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/retrievalbased/SicHashContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/img/preview-dominance-map.png>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/bytehamster/sichash`) · [data/wave1-phf/enrich/raw/github_com_bytehamster_sichash.json](../../../data/wave1-phf/enrich/raw/github_com_bytehamster_sichash.json) (enrichment confidence 0.85)

</details>
