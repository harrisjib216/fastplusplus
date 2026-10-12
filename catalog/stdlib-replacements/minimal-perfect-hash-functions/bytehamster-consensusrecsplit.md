# ConsensusRecSplit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Minimal perfect hash function close to the 1.443 bits/key bound; builds about 100x faster than RecSplit at lower space.

| | |
|---|---|
| **Beats** | RecSplit |
| **Claimed result** | Against RecSplit (paper Table 1, 100M random string keys, single-threaded): RecSplit l=12,b=2000 reaches 1.613 bits/key at 25,667 ns/key construction. ConsensusRecSplit k=256,eps=0.1 reaches 1.578 bits/key at 248 ns/key, about 103x faster construction at lower space (derived from page data). ConsensusRecSplit k=32768,eps=0.0005 reaches 1.444 bits/key at 30,245 ns/key, roughly the same time RecSplit needs for 1.613 bits/key. The paper's '&gt;350x faster at 1.489 bits/key' is against bipartite ShockHash-RS (the previous most space-efficient approach), not RecSplit. The project README separately states that on 100M keys, with about an hour of construction, it reaches 1.4448 bits/key (lower bound 1.4427) where RecSplit reaches 1.6127 bits/key. |
| **Workload** | Single-threaded construction of MPHFs over 100 million random string keys (uniform random length 10-50), plotting space overhead (bits/key) against construction throughput for ConsensusRecSplit versus RecSplit, SIMDRecSplit, ShockHash-RS and bipartite ShockHash-RS/-Flat. |
| **Metric** | build-time |
| **Hardware** | Intel i7-11700, 2.5GHz base clock, 48KiB/512KiB L1/L2 per core, 16MiB L3 |
| **Compiler and flags** | GNU C++ 11.2.0, -O3 -march=native |
| **Adoption** | 11 stars |
| **Last commit** | 2025-06-23 |
| **Links** | [repository](https://github.com/ByteHamster/ConsensusRecSplit) · [benchmark](https://arxiv.org/abs/2502.05613) |

## Verdict

The authors' single-threaded benchmark (MPHF-Experiments, 100M random strings of 10-50 bytes, GCC 11.2 -O3 -march=native, Intel i7-11700) puts ConsensusRecSplit k=256, epsilon=0.1 at 1.578 bits/key and 248 ns/key build, against RecSplit l=12, b=2000 at 1.613 bits/key and 25,667 ns/key: about 103x faster construction at slightly lower space. For about the same build time as that RecSplit setting (30,245 ns/key), it reaches 1.444 bits/key. No standard-library baseline is involved, and the paper's '&gt;350x' figure compares against bipartite ShockHash-RS at 1.489 bits/key, not RecSplit.

## Use it when

- Large static key sets where MPHF size is the main constraint and you want 1.44-1.53 bits/key, a range where earlier methods need 30-360x more build time per the paper's Table 1.
- As a replacement for RecSplit at roughly 1.6 bits/key: k=256, epsilon=0.1 gives 1.578 bits/key at 248 ns/key build (about 25 s for 100M keys), while RecSplit l=12 needs 25,667 ns/key for 1.613 bits/key.
- Build-once, query-many workloads that can pay for one single-threaded construction of seconds (k=256) up to about 50 minutes (k=32768, epsilon=0.0005, 100M keys) in the process that will run the queries.
- String keys, or 64-bit keys that are already uniformly hashed, on 64-bit Linux with GCC 12+ in a project that is GPL-3.0-compatible.
- Research and benchmarking of near-space-optimal perfect hashing: it is the reference implementation of arXiv 2502.05613.

## Skip it when

- Latency-critical lookups. Queries take 140-217 ns on 100M keys, compared with 78-84 ns for bipartite ShockHash-Flat and 139-156 ns for RecSplit in the same table. PTHash reports 37-55 ns at about 3 bits/key in its own benchmark.
- You need to save the function and load it later. There is no serialization API, so every process must rebuild it, which takes up to an hour at the most compact settings.
- Proprietary or closed-source distribution. The license is plain GPL-3.0 with no runtime exception (unlike ShockHash), and the Util, FiPS and pasta bit_vector dependencies are also GPL-3.0.
- Fast or parallel builds at 2-3 bits/key. Construction is single-threaded, the paper leaves parallelization as future work, and it compares only against methods below 1.6 bits/key. At that space budget PTHash or SIMDRecSplit are the tested choices.
- Memory-constrained builds or production use that needs a maintained library. Build memory is not documented; the code keeps roughly 40 bytes per key of temporaries: 64-bit hashes, a 16-byte-per-key sort array and an unused copy of that array. The repo has 11 stars, no issues filed and no code commits since 2025-06-23.

## How it is fast

It keeps RecSplit's recursive splitting but uses only balanced 2-way splits and finds their seeds with Consensus (Combined Search and Encoding of Successful Seeds). Each split gets a fixed-width field in one bit stream, and its effective seed is the 64-bit window ending at that field, so it includes the bits of the seeds before it. A depth-first search backtracks when a later split has no working seed. This brings the overhead down to about epsilon bits per seed for O(1/epsilon) expected work, so build time grows linearly in 1/epsilon rather than exponentially as in RecSplit and ShockHash. First, a threshold-based minimal k-perfect hash function (k = 256-32768, with a FiPS fallback for bumped keys) sorts the keys into buckets of exactly k. That skips the expensive, cache-unfriendly top splits.

## Compared with alternatives

Pick it when bits/key matters most. At about 1.5 bits/key it builds about 30x faster than bipartite ShockHash-RS from the ShockHash repo (584 vs 17,736 ns/key), and at 1.53-1.56 bits/key about 360x faster than SIMDRecSplit. Choose PTHash or bipartite ShockHash-Flat instead when query latency matters or 3 bits/key is fine, and ShockHash when you need its GPL runtime exception.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target added with add_subdirectory; no install or package-config rules) |
| **Dependencies** | Git submodules tlx (BSL-1.0, compiled), ips2ra (BSD-2-Clause), ByteHamster/Util (GPL-3.0, pulls pasta bit_vector, GPL-3.0) and FiPS (GPL-3.0). It also needs TBB, pthread and libatomic linked through ips2ra, even though ips2ra's parallel mode is off. At configure time, pasta bit_vector uses FetchContent to download pasta_utils and tlx from GitHub at origin/main. |
| **Minimum toolchain** | C++20 (double non-type template parameter, std::span, std::bit_width), CMake 3.25+; CI builds with GCC 12, 13 and 14; the paper used GCC 11.2; Clang is not tested in CI |
| **Platforms** | 64-bit Linux; CI runs only on x86-64 Ubuntu 24.04. No specific ISA is required: pasta uses BMI2 pdep only when it is enabled. The code assumes a 64-bit `unsigned long` (`~0ul` masks, `1ul << 63`), so Windows/MSVC (LLP64) is not expected to work. |
| **Thread safety** | Not documented. `operator()` is const and only reads immutable bit vectors, so concurrent queries on a built object look safe. Construction is single-threaded. |
| **Drop-in for the baseline** | partial — it fills the same role as Sux RecSplit (keys in, index in [0, n) out), but it uses a different class, tuning parameters (k and epsilon instead of leaf and bucket size) and key hashing, and it has no serialization. |

## Gotchas

- The object owns a raw `bucketingPhf` pointer and has a user-declared destructor but no copy or move operations. Copying it double-frees, and so does `std::move`, which falls back to the copy. Build it in place or on the heap, as the MPHF-Experiments harness does. The internal k-perfect hash function also never frees its rank/select structure.
- The `uint64_t` constructor uses the keys directly as hashes: the low 32 bits pick the bucket and the high 32 bits the threshold. Hash non-random integer keys first. String keys are reduced to a 64-bit MurmurHash64, and nothing checks for duplicates. Duplicate keys or 64-bit hash collisions (about 2.7% likely at 1B keys) can never be split, so the default level-wise search appears to loop forever. This is inferred from the code, not documented.
- `k` (a power of two) and `overhead` (epsilon) are template parameters. Every setting you want to try must be instantiated at compile time, as the benchmark's dispatch shows.
- The default level-wise constructor prints a timing line per tree level to `std::cout`, and the query-optimized one prints its tree size. The project adds `-march=native` only when it is the top-level CMake project.

## Caveats and trade-offs

The comparison is by the ConsensusRecSplit authors (their MPHF-Experiments framework), single-threaded, on 100M string keys. The headline '&gt;350x' figure is against bipartite ShockHash-RS, not RecSplit. Queries are not faster: 140-217 ns vs RecSplit's 139-156 ns in Table 1. The paper includes only approaches below 1.6 bits/key, so it has no BBHash/CMPH/PTHash comparison. The latest GitHub release (tag 2026-01-04) points at the 2025-06-23 commit.

Very slow in absolute terms at maximum space-efficiency settings (\~1 hour for 100M keys); needs a large bucket size (e.g. k=32768) for the best trade-off; combines with a separate threshold-based k-perfect hash layer for cache locality, adding implementation complexity; GPL-3.0 + runtime exception licensing.

## Maintenance

Stale research code from KIT: the last code commit is 2025-06-23 (the 2026-01-04 release tag points to it) and no issues have ever been filed. It builds with GCC 12-14 CI and can be vendored with add_subdirectory plus submodules, but only into GPL-3.0-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** arXiv 2502.05613 (Sec. 5.4, Fig. 5, Table 1) benchmarks ConsensusRecSplit against RecSplit and others. The code is public in ByteHamster/MPHF-Experiments (src/comparison.cpp, contenders/recsplit/ConsensusContender.cpp, contenders/recsplit/RecSplitContender.cpp), and the paper states GNU C++ 11.2.0, -O3 -march=native and an Intel i7-11700.
- **Verifier notes:** The claim credited the '&gt;350x at 1.489 bits/key' result to RecSplit, but both arXiv v1 and v2 say it is against bipartite ShockHash-RS; against RecSplit the page supports about 100x at lower space. The 1.4448/1.6127 figures come from the repo README, not the arXiv page (the paper's Table 1 gives 1.444/1.613). The last commit is 2025-06-23 (the 2026-01-04 date is a release tag on that same commit), so the repo is stale, not active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2502.05613>
  - <https://arxiv.org/pdf/2502.05613>
  - <https://arxiv.org/pdf/2502.05613v1>
  - <https://github.com/ByteHamster/ConsensusRecSplit>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/README.md>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/LICENSE>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/plot.png>
  - <https://github.com/ByteHamster/ConsensusRecSplit/tree/main/benchmark>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/README.md>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/recsplit/ConsensusContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/recsplit/RecSplitContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/ByteHamster/ConsensusRecSplit>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/README.md>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/include/ConsensusRecSplit.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/include/ConsensusRecSplitQueryOptimized.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/include/consensus/BumpedKPerfectHashFunction.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/include/consensus/UnalignedBitVector.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/include/consensus/SplittingTreeStorageLevelwise.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/.gitmodules>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/.github/workflows/build.yml>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/LICENSE>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/CITATION.cff>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/scripts/parameters.sh>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/benchmark/benchmark_construction.cpp>
  - <https://github.com/ByteHamster/ConsensusRecSplit/blob/main/benchmark/BenchmarkData.h>
  - <https://github.com/ByteHamster/ConsensusRecSplit/issues>
  - <https://github.com/ByteHamster/ConsensusRecSplit/releases>
  - <https://github.com/ByteHamster/ConsensusRecSplit/commits/main>
  - <https://github.com/ByteHamster/Util>
  - <https://github.com/ByteHamster/Util/blob/57b32e868bf54e4c31fd8498dbe4f0454e83f008/include/bytehamster/util/Function.h>
  - <https://github.com/ByteHamster/Util/blob/57b32e868bf54e4c31fd8498dbe4f0454e83f008/CMakeLists.txt>
  - <https://github.com/ByteHamster/FiPS>
  - <https://github.com/ByteHamster/FiPS/blob/b8bb74213147bac832200f81c5383084cda5fe7d/include/Fips.h>
  - <https://github.com/pasta-toolbox/bit_vector>
  - <https://github.com/pasta-toolbox/bit_vector/blob/3ffb6e5a2e58c76425de8197bfe554eb1bf9fd94/CMakeLists.txt>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/select.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/flat_rank_select.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/find_l2_flat_with.hpp>
  - <https://github.com/ips4o/ips2ra>
  - <https://github.com/tlx/tlx>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/recsplit/ConsensusContender.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/recsplit/ConsensusContender.h>
  - <https://github.com/ByteHamster/ShockHash>
  - <https://arxiv.org/abs/2502.05613>
  - <https://arxiv.org/html/2502.05613v2>
  - <https://arxiv.org/pdf/2502.05613v2>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/bytehamster/consensusrecsplit`) · [data/wave1-phf/enrich/raw/github_com_bytehamster_consensusrecsplit.json](../../../data/wave1-phf/enrich/raw/github_com_bytehamster_consensusrecsplit.json) (enrichment confidence 0.85)

</details>
