# ShockHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0 WITH GCC-exception-3.1` · 🟡 stale

> C++ minimal perfect hash: RecSplit with cuckoo-hashing leaves, building 1.56-1.58 bits/key MPHFs 15-160x faster than RecSplit/SIMDRecSplit.

| | |
|---|---|
| **Beats** | RecSplit |
| **Claimed result** | At 1.56 bits/key, ShockHash-RS (n=39, b=2000) builds at 1,805 ns/key (1.556 bits/key), which the paper calls 'about 75 times faster than the next competitor' (SIMDRecSplit n=16, b=2000: 1.560 bits/key at 137,902 ns/key). Against plain RecSplit (n=14, b=2000: 1.585 bits/key, 125,521 ns/key), ShockHash-RS n=30, b=2000 builds at 787 ns/key for 1.583 bits/key, about 160x faster at equal space (derived from page data). Queries are slightly slower (114-118 ns vs 97 ns). |
| **Workload** | Single-threaded construction of MPHFs for 10 million keys, which are random strings of uniform length 10-50 (not 64-bit integers). ShockHash-RS, RecSplit, SIMDRecSplit and others are compared at matched space (\~1.56-1.59 bits/key) on construction ns/key and query ns/key (paper Table 1). |
| **Metric** | build-time |
| **Hardware** | Intel i7-11700, 8 cores, 2.5GHz base, Ubuntu 22.04 |
| **Compiler and flags** | GNU C++ 11.2.0, -O3 -march=native |
| **Adoption** | 15 stars |
| **Last commit** | 2025-03-31 |
| **Links** | [repository](https://github.com/ByteHamster/ShockHash) · [benchmark](https://arxiv.org/abs/2308.09561) |

## Verdict

The paper's Table 1 (arXiv 2308.09561v2) measures 10M random strings of length 10-50, single-threaded, compiled with GCC 11.2.0 -O3 -march=native on an Intel i7-11700 with AVX-512, running SIMDShockHash with rotation fitting. At \~1.56 bits/key, ShockHash-RS n=39 builds at 1,805 ns/key against SIMDRecSplit's 137,902 ns/key (\~76x). At \~1.585 bits/key, n=30 builds at 787 ns/key against sux RecSplit's 125,521 ns/key (\~160x), but only \~15x against SIMDRecSplit's 11,749 ns/key. Queries are 114-118 ns against 97-108 ns.

## Use it when

- Static key sets (millions to hundreds of millions of string keys) where the MPHF must sit close to the 1.44 bits/key lower bound. Table 1 configurations reach 1.52-1.58 bits/key.
- You already use RecSplit or SIMDRecSplit at b=2000 with leaf 14-16 and build time is the bottleneck. At matched space, ShockHash-RS builds in 787-1,805 ns/key; RecSplit and SIMDRecSplit take 11,749-137,902 ns/key.
- Processes that build the function once and keep it in RAM, where a \~115 ns query is acceptable. For example, 10M keys with n=30, b=2000 is about 8 s of single-threaded construction.
- x86-64 Linux with GCC 11+ and AVX2 or AVX-512, using SIMDShockHash with rotation fitting. This is the configuration the paper measured.
- To go below \~1.52 bits/key, use `ShockHash2` (bipartite ShockHash, arXiv 2310.14959) from the same repo. Its abstract reports 1.489 bits/key for 10M keys in about half an hour.

## Skip it when

- Lookup latency is the constraint. In the same Table 1, queries take 114-118 ns; PTHash takes 20-34 ns and FMPHGO 53-69 ns, at 2.2-4.4 bits/key.
- You need to save the function to disk and load it later. ShockHash, SIMDShockHash and ShockHash2 have no serialization API (sux RecSplit has `operator<<`/`operator>>`), so every run must rebuild.
- Dynamic key sets, or code that must detect foreign keys. The function is static and returns an arbitrary index for keys it was not built on, so you need a separate key or fingerprint store.
- Clang, MSVC, Windows, macOS or ARM toolchains. CI covers only GCC 11/12/13 on Ubuntu, the code uses `<experimental/simd>`, raw x86 intrinsics in the SIMD path and `1ul` shifts of up to 60 bits, and CMake links Intel TBB.
- The most compact ShockHash-RS setting (n=58, 1.523 bits/key) costs 111,593 ns/key, about 19 minutes single-threaded for 10M keys. The newer ConsensusRecSplit reports getting much closer to the bound.

## How it is fast

It keeps RecSplit's recursive splitting tree but replaces the brute-force bijection search in each leaf (about e^n seed trials) with ShockHash ('small, heavily overloaded cuckoo hash tables'): each seed gives every key two candidate cells in an n-cell table, and the seed is accepted if the random graph is a pseudoforest, meaning the table can be filled completely by cuckoo insertion. A 1-bit BuRR ribbon retrieval structure records which of the two cells each key uses, and this cuts the expected trials to (e/2)^n·poly(n), almost 2^n fewer, so leaves can have n=30-58 instead of RecSplit's \~8-16. Most seeds are rejected early by a bit-mask filter that checks every cell is hit; the filter runs in registers with AVX2/AVX-512 SIMD, and rotation fitting tries n cyclic rotations of half the keys per hash evaluation.

## Compared with alternatives

Pick it over RecSplit (sux) or SimdRecSplit when you want 1.52-1.59 bits/key without their 11,749-137,902 ns/key builds, and can accept up to \~20% slower queries (114-118 vs 97-108 ns) and no serialization. Prefer ConsensusRecSplit (same group, 2025; 1.4448 bits/key on 100M keys in about an hour) for minimum space, and PTHash or SicHash when 2-4.4 bits/key is acceptable in return for builds and queries several times faster.

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake add_subdirectory of the repo with submodules; header-only INTERFACE target plus compiled shared libs ShockHash2Precompiled, Ips2raShockHashSorter, SimpleRibbon, RibbonSorter) |
| **Dependencies** | Git submodules: sux (ByteHamster fork), SimpleRibbon (BuRR, ips2ra, tlx), tlx, ByteHamster/Util (pasta-bit-vector), and vectorclass (SIMD variant only). Intel TBB from the system (CI installs libtbb-dev). CMake 3.25+. |
| **Minimum toolchain** | C++20; GCC 11+ (CI tests GCC 11/12/13; a commit notes GCC 10 lacks &lt;experimental/simd&gt;); CMake 3.25 |
| **Platforms** | Tested only on Linux x86-64 (Ubuntu CI). SIMDShockHash needs AVX2, uses AVX-512 when available, and must be compiled with -DSIMD. Clang, macOS, Windows and aarch64 are not documented. The code assumes 64-bit unsigned long, and keys beyond 2^32 need __int128 support. |
| **Thread safety** | Construction can use several threads through the num_threads constructor argument (the paper's benchmarks used 1). Thread safety of concurrent queries is not documented. `ShockHash::operator()` is non-const, while `ShockHash2::operator()` is const. |
| **Drop-in for the baseline** | partial — the constructor (keys, bucket_size) and operator()(key) match sux RecSplit, but the namespace differs, LEAF_SIZE goes up to 60 (128 for ShockHash2), there is an extra num_threads argument, there is no stream serialization, and the returned indices differ. |

## Gotchas

- Duplicate keys make the constructor loop forever. This is documented in SIMDShockHash's doc comment, as in sux RecSplit. Deduplicate keys before building.
- MAX_BUCKET_SIZE is 3000, and the header says it 'works with high probability up to average bucket size \~2000'. Only an assert guards the limit, so keep bucket_size at 2000 or below.
- CMake compiles Ips2raShockHashSorter and ShockHash2Precompiled with -march=native unconditionally, and the ShockHashSIMD target passes -march=native on to consumers. Binaries may not run on CPUs older than the build host.
- The Table 1 numbers come from `SIMDShockHash<n, true>` (SIMD plus rotation fitting, via the MPHF-Experiments ShockHashContender). The README example `ShockHash<30, false>` is the slower scalar path without rotation fitting. SIMDShockHash stops with #error unless built with -DSIMD (link the ShockHashSIMD target).

## Caveats and trade-offs

The main numeric win is against RecSplit/SIMDRecSplit, not the category incumbents. CHD (CMPH) appears only as a curve in the Figure 5 Pareto plot, with no tabulated numbers. BBHash is omitted because FMPH (Rust) 'significantly outperforms' it. All runs are single-threaded. The MPHF-Experiments harness has since been updated for the bipartite-ShockHash paper (src/tableShockHash.cpp), so reproducing Table 1 exactly needs the 2023 commit.

Base case is exponential-time in theory (mitigated by integrating into RecSplit-style partitioning); space-optimal configurations still take much longer to build than fingerprinting methods in absolute terms; SIMD variants need AVX support; GPL-3.0 + runtime exception licensing.

## Maintenance

Stale: the last commit was 2025-03-31, there are no releases or tags, no GitHub issues have ever been filed, and it has 15 stars. The research code uses GPL-3.0 with the GCC Runtime Library Exception, which the README says permits use like libstdc++. Vendoring it means vendoring six submodules and depending on system TBB.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Table 1 of arXiv 2308.09561v2 compares ShockHash-RS against RecSplit (sux), SIMDRecSplit, PTHash, SicHash and FMPHGO, and Figure 5 also plots CHD from CMPH. The paper states GNU C++ 11.2.0 -O3 -march=native on an Intel i7-11700. The benchmark code is public in ByteHamster/MPHF-Experiments: comparisonQueries.cpp at commit 8e7f87aee3 has the Table 1 configurations (ShockHash n=30/39/58, RecSplit n=8/14, SIMDRecSplit), plus the ShockHash repo's benchmark/ dir.
- **Verifier notes:** All Table 1 numbers and the '75 times' quote match the PDF (v2, 13 Nov 2023, the latest version). The old caveat 'CMPH is not compared at all' was wrong, because CHD [2] is plotted in Figure 5. Keys are strings, not 64-bit ints. baseline RecSplit with baseline_in_list=false is correct against the wave baselines (std::unordered_map, CMPH, BBHash). The README says the license is GPLv3 + GCC Runtime Library Exception. Last commit 2025-03-31 makes it stale.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2308.09561>
  - <https://arxiv.org/pdf/2308.09561>
  - <https://github.com/ByteHamster/ShockHash>
  - <https://github.com/ByteHamster/ShockHash/blob/main/README.md>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/ShockHash.h>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tableShockHash.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/8e7f87aee3d235678e9a0a8523dc4b31047a70fc/comparisonQueries.cpp>
- **Sources the enricher read:**
  - <https://github.com/ByteHamster/ShockHash>
  - <https://github.com/ByteHamster/ShockHash/blob/main/README.md>
  - <https://github.com/ByteHamster/ShockHash/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/ShockHash/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/ShockHash/blob/main/.github/workflows/build.yml>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/ShockHash.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/SIMDShockHash.hpp>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/ShockHash2.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/ShockHash2Flat.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/TinyBinaryCuckooHashTable.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/Sorter.hpp>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/SimdUtils.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/ShockHash2-internal.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/ShockHash2-precompiled.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/include/shockhash/ShockHash2FlatBase.h>
  - <https://github.com/ByteHamster/ShockHash/blob/main/src/Sorter.cpp>
  - <https://github.com/ByteHamster/ShockHash/blob/main/src/ShockHash2-precompiled.cpp>
  - <https://github.com/ByteHamster/ShockHash/issues?q=is%3Aissue>
  - <https://github.com/ByteHamster/ShockHash/commits/main>
  - <https://arxiv.org/abs/2308.09561>
  - <https://arxiv.org/pdf/2308.09561>
  - <https://arxiv.org/abs/2310.14959>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/Util/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/8e7f87aee3d235678e9a0a8523dc4b31047a70fc/comparisonQueries.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/8e7f87aee3d235678e9a0a8523dc4b31047a70fc/benchmark/ShockHashContender.h>
  - <https://github.com/vigna/sux/blob/master/sux/function/RecSplit.hpp>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/bytehamster/shockhash`) · [data/wave1-phf/enrich/raw/github_com_bytehamster_shockhash.json](../../../data/wave1-phf/enrich/raw/github_com_bytehamster_shockhash.json) (enrichment confidence 0.82)

</details>
