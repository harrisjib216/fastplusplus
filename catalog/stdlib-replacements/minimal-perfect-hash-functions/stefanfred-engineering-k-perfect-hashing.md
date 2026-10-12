# Engineering Minimal/k-Perfect Hash Functions (stefanfred implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Four minimal k-perfect hash functions; at k=10 threshold-based bumping builds 6.4x and queries 1.7x faster than cmph CHD.

| | |
|---|---|
| **Beats** | CMPH CHD (cmph library, run as non-minimal k-perfect with load factor 0.97, because cmph CHD supports only non-minimal k-perfect hashing) and the ad-hoc threshold-based bumping kPHF from CONSENSUS-RecSplit [30]; no BBHash, PTHash or 1-perfect RecSplit comparison |
| **Claimed result** | Abstract: 'Our implementations simultaneously dominate older approaches in space consumption, construction time, and query time.' Table 2, k = 10: CHD (load factor 0.97) 0.627 bits/key, 495 ns/key construction, 96 ns/query; Threshold-Based 0.716 bits/key, 77 ns/key, 56 ns/query; Bucket Placement (Compact) 1.917 bits/key, 584 ns/key, 47 ns/query; Threshold-Based + Consensus 0.450 bits/key, 233 ns/key, 57 ns/query (better than CHD on all three). That is about 6.4x faster construction (Threshold-Based vs CHD) and 1.7x-2.0x faster queries (derived from page data). Text: up to 3 times smaller space overhead than the ad-hoc threshold-based implementation, and up to 50% faster construction than the next best technique. The CHD implementation crashes for k = 1000. Query times are 22-291 ns/query, not single-digit nanoseconds. |
| **Workload** | Minimal k-perfect hash function construction and queries for k = 10, 100 and 1000 on 100 million random strings of uniform random length in [10, 50]. Figure 5 plots space vs construction and query throughput; Table 2 lists representative configurations for k = 10 and k = 1000. There are no k = 1 (standard MPHF) experiments. |
| **Metric** | other |
| **Hardware** | Intel i7 11700 (8 cores, 2.5 GHz base clock), Rocky Linux 9.5, Linux 5.14.0 |
| **Compiler and flags** | GCC 11.2.0, -O3 -march=native |
| **Adoption** | 1 star |
| **Last commit** | 2025-07-03 |
| **Links** | [repository](https://github.com/stefanfred/engineering-k-perfect-hashing) · [benchmark](https://arxiv.org/pdf/2504.20001) |

## Verdict

Paper Table 2 (ESA 2025) measures 100M random strings of length 10-50 with a single-threaded harness, GCC 11.2 -O3 -march=native, on an Intel i7-11700 running Rocky Linux 9.5. At k=10, Threshold-Based builds in 77 vs 495 ns/key and queries in 56 vs 96 ns against cmph CHD, which was run non-minimal at load factor 0.97 and is slightly smaller (0.627 vs 0.716 bits/key); Threshold-Based + Consensus beats CHD on all three axes (0.450 bits/key, 233 ns/key, 57 ns/query). CHD crashed at k=1000, and there are no k=1, BBHash/PTHash or std:: comparisons.

## Use it when

- You need a static set of string keys split into ceil(n/k) bins of exactly k keys. The paper's examples are a page index for an external-memory hash table, a completely filled bucketized in-memory table, and equal-size partitions for building 1-perfect hash functions.
- Large k (100-1000) where index size matters. At k=1000, Threshold-Based uses 0.010-0.011 bits/key (lower bound 0.006) with 44-45 ns/key construction and 24-25 ns queries on 100M keys.
- You currently use cmph CHD_PH in k-perfect mode. At k=10, Threshold-Based builds in 77 vs 495 ns/key and queries in 56 vs 96 ns, and it works at k=1000, where the authors report CHD crashes.
- Space-critical k=10 indexes. Threshold-Based + Consensus reaches 0.450 bits/key with 57 ns queries; k-RecSplit reaches 0.445 bits/key if 291 ns queries are acceptable.
- Benchmarking new kPHF designs: the repo's contenders/ and benchmarklib/ harness already wraps all constructions plus cmph CHD and the older ad-hoc threshold-based bumping.

## Skip it when

- You need an ordinary MPHF (k=1). No k=1 experiments exist, so use a 1-perfect sibling such as PTHash, PtrHash or ConsensusRecSplit.
- The key set changes, or the function must be persisted and reloaded. The structures are static, and none has save/load support (k-RecSplit's stream operators are compiled out with #if 0).
- You need a permissive license. The code is GPL-3.0, and its FiPS dependency is GPLv3 too.
- You use MSVC/Windows or a pre-C++23 toolchain. The targets require cxx_std_23, and the code relies on unsigned __int128, __builtin_ctzll and a 64-bit unsigned long (\~0ul, 1ul &lt;&lt; n). It was only tested on Linux x86-64.
- You need production maturity, non-string keys or a custom hasher. It is research code with 1 star, no releases and no unit tests beyond the benchmark's validity check. Keys must be std::string (hashed with SpookyHash), except that Threshold-Based also accepts pre-computed 128-bit hashes. Construction is single-threaded.

## How it is fast

Threshold-based bumping hashes keys into ceil(n/(k\*gamma)) overloaded bins (gamma &gt; 1). Each bin stores a few-bit index into a small table of fingerprint thresholds, chosen to minimize expected empty slots under a gamma-distribution model, so most queries cost one bin hash and one comparison; bumped keys go to further layers, and a small FiPS 1-PHF plus an Elias-Fano list places the last few keys into leftover slots. Construction only radix-partitions keys by bin (ips2ra) and runs quickselect to find the k-th fingerprint instead of fully sorting, which the paper credits for being up to 50% faster to build than the next-best technique; optional 1-bit BuRR retrieval packing and CONSENSUS-coded thresholds trade some speed for space. The other three are k-perfect ports of known ideas: hash-and-displace with a k-specific optimal bucket-assignment function (CHD/PHOBIC style), RecSplit with leaves of size k, and PaCHash (an Elias-Fano predecessor search plus retrieval).

## Compared with alternatives

Every catalogued sibling (PTHash, PtrHash, PHast, RecSplit, ConsensusRecSplit, ShockHash and others) is a 1-perfect MPHF, so pick this only when you need bins of exactly k&gt;1 keys. Its Threshold-Based variant is the tuned successor of the ad-hoc threshold-based bumping in ConsensusRecSplit (1.293 -&gt; 0.716 bits/key at k=10, 137 -&gt; 56 ns queries), and k-RecSplit is the k&gt;1 port of Sux RecSplit.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake add_subdirectory + git submodules; the ThresholdBasedBumping and PaCHash targets also build the SimpleRibbon/BuRR shared library) |
| **Dependencies** | Submodules: sux, ByteHamster/Util (with pasta-bit-vector), SimpleRibbon (BuRR, ips2ra, tlx), FiPS, gcem, tlx. cmph and ConsensusRecSplit are needed only for the benchmarks. HashDisplace.hpp includes a header by relative path from inside the simple-ribbon submodule. |
| **Minimum toolchain** | C++23 (cxx_std_23), CMake 3.24+ (the SimpleRibbon, FiPS and Util submodules declare 3.25). Paper builds used GCC 11.2 with -O3 -march=native; spack.yaml pins GCC 14.2 and CMake 3.30. GCC/Clang only. |
| **Platforms** | Tested only on x86-64 Linux (Intel i7-11700). There are no SIMD intrinsics in the kphf headers, but the code assumes LP64 and GCC/Clang extensions. -march=native is added only when the project is built top-level. |
| **Thread safety** | Not documented. Queries for Threshold-Based, Bucket Placement and k-PaCHash are const methods and only read state (the sux select calls behind `mutable` do not mutate), so concurrent reads look safe. k-RecSplit's operator() is non-const. Construction is single-threaded (ips2ra parallelism is disabled). |
| **Drop-in for the baseline** | no |

## Gotchas

- optimalThresholds.hpp and consensus.hpp define non-inline functions and a global (gammapdf, compute_thresholds_normalized, `uint64_t backtracks`). Including the threshold-based headers in more than one translation unit of a single binary therefore gives multiple-definition link errors, so confine them to one .cpp.
- Duplicate keys are never checked. k-RecSplit documents that duplicates make construction never return, and the other constructions do no deduplication either.
- Parameters must be tuned per k. The paper's Table 2 uses gamma=2.0 with 2^4-2^5 thresholds for k=10 and gamma=1.2 with 2^7-2^9 thresholds for k=1000. The benchmark binaries only instantiate k in {2, 4, 8, 10, 100, 1000}.
- k-PaCHash's build prints 'Num ribbon: ...' to stdout on every construction. Its bucket-scan loop also evaluates keys[offset] with offset == keys.size() after the last key, which is an out-of-bounds read (undefined behavior that sanitizers would flag).

## Caveats and trade-offs

ESA 2025 paper (LIPIcs vol. 351, 99:1-99:18, DOI 10.4230/LIPIcs.ESA.2025.99; software artifact DOI 10.4230/artifacts.24698). This is a k-perfect hashing library (k = 10/100/1000 evaluated), not a 1-perfect MPHF. It is not compared against BBHash, PTHash or 1-perfect RecSplit. The only external baselines are cmph CHD, run non-minimal at load factor 0.97 and crashing at k = 1000, and the ad-hoc threshold-based bumping from CONSENSUS-RecSplit. CHD is slightly smaller than plain Threshold-Based at k = 10 (0.627 vs 0.716 bits/key), but Threshold-Based + Consensus beats CHD on space, construction and query. Table 2 is plain text in the PDF, not images. GPL-3.0 applies.

Very new, low-adoption research code (1 star); generalizes to k-perfect hashing (buckets may hold up to k keys), of which minimal perfect hashing is the k=1 special case; GPL-3.0 is copyleft.

## Maintenance

Frozen research code since the ESA 2025 paper (last commit 2025-07-03, 1 star, no issues, no releases, only a 'zenodo' tag). It is usable via CMake add_subdirectory with 8 submodules, but GPL-3.0 copyleft and unserializable structures limit production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The paper (ESA 2025, arXiv v2) benchmarks against CMPH CHD, a category baseline, and states the CPU (Intel i7 11700), compiler (GCC 11.2.0) and flags (-O3 -march=native). The benchmark code is public in the repo: src/table.cpp (Table 2), src/comparison.cpp (Figure 5), contenders/ChdContender.hpp (cmph CHD through the extlib/cmph submodule) and scripts/table.sh.
- **Verifier notes:** The original claimed_speedup was substantially wrong. It said k = 1 single-digit-ns queries with explicit BBHash/PTHash/RecSplit/CHD comparisons, but the paper has no k = 1 experiments and compares only against cmph CHD and the ad-hoc threshold-based bumping. The corrected claim uses Table 2. The claim was overstated, but the tier went up (B to A) because the code, compiler, flags and CPU are all present. The last commit on master (the only branch) is 2025-07-03; pushed_at is 2025-11-13 but has no newer commit, so the status is stale (about 14.7 months).
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2504.20001>
  - <https://arxiv.org/abs/2504.20001>
  - <https://doi.org/10.4230/LIPIcs.ESA.2025.99>
  - <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESA.2025.99>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/README.md>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/CMakeLists.txt>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/.gitmodules>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/src/table.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/src/comparison.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ChdContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/scripts/table.sh>
- **Sources the enricher read:**
  - <https://github.com/stefanfred/engineering-k-perfect-hashing>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/README.md>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/CMakeLists.txt>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/.gitmodules>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/spack.yaml>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/CITATION.cff>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/plot.png>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/threshold-based-bumping/ThresholdBasedBumping.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/threshold-based-bumping/ThresholdBasedBumpingConsensus.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/threshold-based-bumping/consensus.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/threshold-based-bumping/optimalThresholds.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/threshold-based-bumping/optimalThresholdsAsymp.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/common/hash128.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/hash-displace/HashDisplace.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/hash-displace/CompactEncoding.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/hash-displace/RiceEncoding.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/hash-displace/UniformBucketFunction.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/hash-displace/OptimalBucketFunction.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/pachash/PaCHash.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/include/recsplit/kRecSplit.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ChdContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ChdContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ThresholdBasedBumpingContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ThresholdBasedBumpingContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ThresholdBasedBumpingConsensusContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ThresholdBasedBumpingConsensusContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/ThresholdBasedBumpingOldContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/HashDisplaceContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/HashDisplaceContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/KRecSplitContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/KRecSplitContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/PaCHashContender.hpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/contenders/PaCHashContender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/src/table.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/src/comparison.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/scripts/table.sh>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/scripts/scatterplot.sh>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/benchmarklib/Contender.h>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/benchmarklib/Contender.cpp>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/blob/master/benchmarklib/DispatchK.h>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/commits/master>
  - <https://github.com/stefanfred/engineering-k-perfect-hashing/issues>
  - <https://arxiv.org/pdf/2504.20001>
  - <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESA.2025.99>
  - <https://github.com/vigna/sux/blob/HEAD/sux/bits/EliasFano.hpp>
  - <https://github.com/vigna/sux/blob/HEAD/sux/bits/SimpleSelect.hpp>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/HEAD/CMakeLists.txt>
  - <https://github.com/ByteHamster/SimpleRibbon/blob/HEAD/include/SimpleRibbon.h>
  - <https://github.com/ByteHamster/FiPS/blob/HEAD/CMakeLists.txt>
  - <https://github.com/ByteHamster/FiPS/blob/HEAD/README.md>
  - <https://github.com/ByteHamster/Util/blob/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/stefanfred/engineering-k-perfect-hashing`) · [data/wave1-phf/enrich/raw/github_com_stefanfred_engineering_k_perfect_hashing.json](../../../data/wave1-phf/enrich/raw/github_com_stefanfred_engineering_k_perfect_hashing.json) (enrichment confidence 0.8)

</details>
