# pasta::bit_vector

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Header-only C++20 rank/select bit vector: 8% faster rank, 16.5% faster select than cs-poppy.

| | |
|---|---|
| **Beats** | cs-poppy (Zhou, Andersen & Kaminsky, SEA'13 compact rank/select bit-vector structure) |
| **Claimed result** | up to 8% faster rank and up to 16.5% faster select vs cs-poppy, at equal space overhead |
| **Workload** | rank and select queries on a length-n uncompressed bit vector, at \~3.51% space overhead |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3950X (16 cores, up to 3.5 GHz), 64 GiB DDR4 RAM, Ubuntu 20.04.2 LTS; single core used (sequential experiments) |
| **Compiler and flags** | GCC 10.2, -O3 -march=native -DNDEBUG (CMake 3.22.1) |
| **Adoption** | 36 stars |
| **Last commit** | 2025-04-07 |
| **Links** | [repository](https://github.com/pasta-toolbox/bit_vector) · [benchmark](https://arxiv.org/abs/2206.01149) |

## Verdict

In the SPIRE 2022 paper (arXiv:2206.01149), pasta-flat/pasta-poppy rank is up to 8% faster and pasta-flatSIMD select up to 16.5% faster than cs-poppy (Zhou, Andersen & Kaminsky, SEA'13) at matching \~3.51% space overhead, measured single-core on an AMD Ryzen 9 3950X with GCC 10.2, -O3 -march=native -DNDEBUG. Not compared directly against any C++ stdlib facility, since none offers rank/select.

## Use it when

- Need succinct rank/select over a static, uncompressed bit vector (e.g., building an FM-index or other compact text index)
- Already using or evaluating cs-poppy-style compact rank/select structures and want the same space overhead with somewhat faster queries
- Target is x86-64 and can compile with -march=native to get the SIMD-accelerated select path
- Single-threaded/sequential query workload (paper's benchmarks are single-core)
- C++20 codebase where GPL-3.0 header-only vendoring is acceptable

## Skip it when

- Need a std::bitset/std::vector&lt;bool&gt;-compatible API — this is a separate type with its own construction and query interface, not a drop-in replacement
- License must be MIT/BSD-permissive — this is GPL-3.0, more restrictive than the sibling libraries in this category
- Rank-only workload where extra memory is acceptable — sdsl-v and rank9select answer rank faster but use 1.75-6.98x more space (per verification notes)
- Stuck on C++17 or earlier, or on a non-x86-64 platform where the SIMD select path is unavailable
- Need an actively maintained dependency — single-author project, last commit 2025-04-07, only 36 stars

## How it is fast

Uses a two-level (L1/L2) block metadata layout in the lineage of cs-poppy (Zhou, Andersen & Kaminsky, SEA'13), with 512-bit L2 blocks, tuned to hold the same \~3.51% space overhead while improving cache-friendliness of the 'flat' layout. The select path can locate the target L2 block with x86-64 SIMD intrinsics (FindL2FlatWith::INTRINSICS, compiled under __x86_64__) instead of linear or binary search over block summaries, which is where most of the select speedup comes from.

## Compared with alternatives

None of the catalogued siblings (CRoaring, plf::bitset, better_bitset, BitLib, sul::dynamic_bitset) implement rank/select at all — they speed up direct std::bitset/std::vector&lt;bool&gt; operations like shifts, iteration, and set algebra. Pick pasta::bit_vector when the workload specifically needs succinct rank/select queries; for plain bit-twiddling workloads without that need, a sibling that benchmarks directly against std is the safer, lower-friction choice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | tlx (github.com/tlx/tlx) and pasta-toolbox/utils, both pulled automatically via CMake FetchContent when building tests/benchmarks; no git submodules |
| **Minimum toolchain** | C++20; CMake 3.25 to build tests/benchmarks via the provided presets (paper's benchmarks used GCC 10.2) |
| **Platforms** | x86-64 for the SIMD-accelerated select path (FindL2FlatWith::INTRINSICS, gated on __x86_64__); a non-intrinsic linear/binary-search fallback exists for other architectures but is not the configuration benchmarked in the paper |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false — cs-poppy itself isn't a stdlib facility, and this library's API (separate BitVector + support-structure wrapper) differs from cs-poppy's; std::bitset/std::vector&lt;bool&gt; have no rank/select at all, so there's no drop-in relationship there either |

## Gotchas

- Support structures (e.g. FlatRankSelect) are constructed from an existing BitVector instance and query through that wrapper; build the bit vector first, then attach the rank/select structure you need
- Multiple rank/select variants exist (Rank/RankSelect, FlatRank/FlatRankSelect, WideRank/WideRankSelect) with WideRank explicitly meant for vectors up to 2^40 bits; the docs don't give a clear size crossover for picking one over another
- Building tests/benchmarks requires network access at configure time for CMake FetchContent to pull tlx and pasta-toolbox/utils
- The headline select speedup depends on -march=native and x86-64 SIMD intrinsics being enabled; behavior without that flag isn't the benchmarked configuration

## Caveats and trade-offs

std::bitset and std::vector&lt;bool&gt; have no native rank/select, so there is no direct std baseline for this functionality. The recorded baseline (cs-poppy, Zhou et al. SEA'13) is the field's standard compact rank/select structure, not a stdlib facility, which caps confidence. The gains are small: rank is roughly 8% faster (pasta-poppy and pasta-flat) and select is 16.5% faster (pasta-flatSIMD) vs cs-poppy at the same \~3.51% space overhead. Rank-only structures such as sdsl-v and rank9select answer rank faster but use 1.75-6.98x more space. The paper is peer-reviewed (SPIRE 2022, DOI 10.1007/978-3-031-20643-6_19), and reproduction scripts are public at github.com/pasta-toolbox/bit_vector_experiments. GPL-3.0 is a copyleft license.

Header-only C++20; GPL-3.0 is more restrictive than MIT/BSD peers; adds rank/select operations that std::bitset/std::vector&lt;bool&gt; lack entirely, so it's an additive capability rather than a drop-in replacement; fastest variant relies on SIMD and -march=native.

## Maintenance

Maintenance is stale (single-author, last commit 2025-04-07, 36 stars), but it's header-only and small enough to read fully and vendor; GPL-3.0 licensing is the main adoption friction, not code quality.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The paper (SPIRE 2022, arXiv 2206.01149) compares pasta-flat/pasta-poppy directly against cs-poppy and cs-poppy-fs. It states GCC 10.2 with -O3 -march=native -DNDEBUG on an AMD Ryzen 9 3950X. The reproduction code is public at github.com/pasta-toolbox/bit_vector_experiments (run_benchmarks.sh).
- **Verifier notes:** The 8%/16.5% numbers and the 3.51% overhead appear in the abstract and the evaluation section. The full-text experimental setup provides the compiler, flags, and CPU model, so the tier moves from B to A. GPL-3.0, 36 stars, and last commit 2025-04-07 (stale) were checked and are correct.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pasta-toolbox/bit_vector>
  - <https://github.com/pasta-toolbox/bit_vector_experiments>
  - <https://arxiv.org/abs/2206.01149>
  - <https://arxiv.org/pdf/2206.01149>
- **Sources the enricher read:**
  - <https://github.com/pasta-toolbox/bit_vector>
  - https://github.com/pasta-toolbox/bit_vector (README via gh api)
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/CMakeLists.txt>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/optimized_for.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/wide_rank.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/popcount.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/include/pasta/bit_vector/support/find_l2_flat_with.hpp>
  - <https://github.com/pasta-toolbox/bit_vector/blob/main/.gitmodules>
  - <https://github.com/pasta-toolbox/bit_vector/issues>
  - <https://arxiv.org/abs/2206.01149>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pasta-toolbox/bit_vector`) · [data/wave1/enrich/raw/github_com_pasta_toolbox_bit_vector.json](../../../data/wave1/enrich/raw/github_com_pasta_toolbox_bit_vector.json) (enrichment confidence 0.55)

</details>
