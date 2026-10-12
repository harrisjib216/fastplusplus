# mutable_rank_select

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> SIMD b-ary Segment-Tree index for rank/select/flip on mutable bitmaps; paper reports it beats Marchini-Vigna compact Fenwick trees.

| | |
|---|---|
| **Beats** | Fenwick-tree based rank/select over mutable bitmaps (Marchini and Vigna, now part of sux) |
| **Claimed result** | Snippets of the paper's abstract (not opened): the SIMD b-ary Segment-Tree answers rank and select in tens of nanoseconds, supports flip at similar cost, uses about 7.2% or 3.6% extra space, and beats compact Fenwick-tree solutions (Marchini and Vigna) in runtime; it is consistently faster than Fenwick-tree solutions. No ratio seen. Snippets also say the experiments ran on an Intel i9-9940X at 3.30 GHz and that AVX-512 roughly doubles search speed over AVX2. |
| **Workload** | rank, select, flip and access on a mutable bitmap, using a SIMD (AVX2/AVX-512) b-ary Segment-Tree index over 256- or 512-bit blocks. |
| **Metric** | latency |
| **Hardware** | Intel i9-9940X at 3.30 GHz (paper, search snippet only) |
| **Compiler and flags** | CMakeLists.txt: -std=c++17 -O3 -march=native -ggdb, plus -mbmi2 -mavx512f -mavx512bw -mavx512vl -mavx512vpopcntdq -DAVX512 when AVX512=On (-stdlib=libc++ on Clang); README says it was tested with gcc 7.4 and 9.2.1 and with clang 10.0.0 and 11.0.0. |
| **Adoption** | 36 stars |
| **Last commit** | 2023-01-08 |
| **Links** | [repository](https://github.com/jermp/mutable_rank_select) |

## Verdict

Search snippets of the Information Systems 2021 paper (the paper itself was not opened) say the SIMD b-ary Segment-Tree is consistently faster than Marchini and Vigna's compact Fenwick trees for rank, select and flip on random workloads, at 3.6-7.2% extra space, measured on an Intel i9-9940X at 3.30 GHz with -O3 -march=native. No ratio was seen. Contrary to the verifier's note, the repo does build the Fenwick competitor, but only at the prefix-sum level: src/perf_hft.cpp benchmarks the hft ByteF/BitF/FixedF/ByteL/BitL/FixedL classes against src/perf_prefix_sum.cpp, not at the full-bitmap level.

## Use it when

- Bitmaps whose bits change often (flip-heavy workloads such as dynamic sets, deletion markers, or dynamic FM-index or wavelet-tree components) where you still need rank/select in tens of nanoseconds.
- x86-64 servers with AVX2, ideally AVX-512 (VL, BW, VPOPCNTDQ), where the paper says the AVX-512 build roughly doubles search speed over AVX2.
- Fixed-capacity bitmaps of up to 2^32 bits (256-bit blocks) or 2^33 bits (512-bit blocks), where about 3.6-7.2% extra space is acceptable.
- Research or benchmarking of dynamic rank/select, since the repo also ships Marchini and Vigna's hybrid Fenwick trees (include/hft) and their benchmark driver (src/perf_hft.cpp).

## Skip it when

- Static bitmaps: an immutable rank/select directory (rank9/poppy-style, pasta, SPIDER, 3\*) uses less space and needs no update path.
- Bitmaps that must grow, shrink, or take inserts and deletes; only flip is supported, and the size is fixed at build.
- Non-x86 targets: access() is x86 inline assembly (bt/sbb), and the SIMD paths need AVX2 or AVX-512 intrinsics. -DDISABLE_AVX swaps the SIMD node code for scalar loops, but the inline assembly stays.
- Bitmaps larger than 2^24 blocks: build() rejects them only through assert, which compiles out in release builds.
- Production code that needs a maintained, packaged dependency: last commit January 2023, no releases, no issues filed, and the README describes it as a research artifact for the paper.

## How it is fast

The bitmap is split into 256- or 512-bit blocks. Per-block popcounts go into a b-ary Segment-Tree of searchable prefix sums with fanout 128 at the leaves, then 64, 64 and 32, so at most 4 levels cover 2^24 blocks. Each node stores 8-way segment summaries plus in-segment prefix sums, so a sum is two loads, a search is two SIMD compares (_mm256_cmpgt_epi32 plus a first-set scan), and an update is two SIMD adds of a precomputed +1/-1 table row. Within a block, rank uses unrolled or looped popcount and select uses popcount plus PDEP/TZCNT, with an optional AVX-512 VPOPCNTDQ path.

## Compared with alternatives

Pick it over static rank/select siblings (SPIDER, 3\*-rankselect, rankselect/PTSelect, succinct-bitvec-cpp, QuadRank) when bits change after construction, which those do not support. Prefer them for read-only bitmaps, where they are smaller and need no update path.

## Integration

| | |
|---|---|
| **Form** | header-only (include/), with git submodules |
| **Dependencies** | essentials (jermp/essentials, used by segment_tree::bytes()); the tests and benchmarks also use doctest and cmd_line_parser. The top-level CMakeLists requires Boost (unit_test_framework, iostreams, system, filesystem), and its succinct and sdsl-lite submodules are only for the immutable-bitmap benchmark. |
| **Minimum toolchain** | C++17 (if constexpr, structured bindings); README tested gcc 7.4 and 9.2.1, clang 10.0.0 and 11.0.0; CMake 2.8+; builds with -march=native by default |
| **Platforms** | x86-64 only (inline bt/sbb asm in access(); AVX2 by default, AVX-512F/BW/VL/VPOPCNTDQ plus BMI2 with -DAVX512=On); tested on Linux and macOS 10.14 |
| **Thread safety** | not documented; queries are const members with no internal state, so concurrent reads look safe, but flip is unsynchronized |
| **Drop-in for the baseline** | partial: it covers the same operations as a Fenwick-tree mutable bitmap (rank, select, flip), but has its own API and compile-time Height parameter, and is not interchangeable with sux classes |

## Gotchas

- Height is a template parameter that must match the number of blocks (segment_tree::height(n) gives it). A mismatch is caught only by assert, and in release builds a too-small Height makes build() index num_nodes_per_level with a negative level, which is out-of-bounds.
- select(i) only asserts i &lt; size() (bits), not i &lt; number of ones; asking for a select past the popcount is undefined in release builds.
- Benchmark harness bug: src/perf_prefix_sum.cpp and src/perf_hft.cpp test operation == "sarch" (typo) when choosing search queries, so 'search' benchmarks draw targets from [0, n) instead of [0, total sum). Both the Segment-Tree and the Fenwick prefix-sum search timings therefore query only a small prefix of the sums. The bitmap-level benchmark (perf_mutable_bitmap select) draws queries correctly from [0, num_ones).
- Headers are not self-contained (util.hpp has no includes; mutable_bitmap.hpp uses std::memcpy and std::ceil without &lt;cstring&gt;/&lt;cmath&gt;), so include order matters if you vendor them.

## Known shortcomings

- Downgraded B to D: the repo bench (src/perf_mutable_bitmap.cpp) has no Fenwick competitor and the paper (arXiv 2009.12809) is blocked everywhere; snippets say only 'consistently faster' than a Fenwick tree with no ratio (i9-9940X, -O3 -march=native). Paper-access retier candidate.
- The repo builds the Marchini-Vigna Fenwick competitor (include/hft, src/perf_hft.cpp) but only at prefix-sum level, not as a full bitmap. Benchmark bug: perf_prefix_sum.cpp and perf_hft.cpp test operation == 'sarch' (typo), so search queries are drawn from [0,n) rather than [0,total sum) on both sides. A wrong compile-time Height or more than 2^24 blocks is caught only by assert; a release build indexes num_nodes_per_level out of bounds. select(i) past the popcount is UB. x86-only (inline bt/sbb asm). Headers not self-contained; CMake needs Boost for the benchmarks. Paper blocked here.

## Caveats and trade-offs

The claim comes from the peer-reviewed Information Systems 2021 paper (arXiv 2009.12809), which could not be opened here; the speedup over the Fenwick tree is qualitative in snippets. The repo's benchmark does not include the Fenwick-tree baseline, so the comparison cannot be reproduced from this repo alone. The baseline (Marchini and Vigna's compact Fenwick trees) is now part of the already-listed vigna/sux. Last commit January 2023. Good candidate for a paper-access retier (B is likely once the paper's tables are read).

Supports updates (flip), unlike static SDSL/pasta structures. Needs AVX2 or AVX-512 for best speed. Space is higher than a static rank/select directory.

## Maintenance

Abandoned since January 2023 (123 commits, no releases, no issues), but MIT-licensed and a small header set that can be vendored with essentials; x86-only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now D.
- **Tier reason:** The README and the repo's benchmark (src/perf_mutable_bitmap.cpp) time only the Segment-Tree variants; no Fenwick-tree competitor is built. The Information Systems 2021 paper that carries the comparison (arXiv 2009.12809, ScienceDirect, ISTI preprint, unipi.it copy) is blocked here, and search snippets only say it is 'consistently faster' than Fenwick-tree solutions, with no ratio.
- **Verifier notes:** Real and cited peer-reviewed work, but no numbers could be seen because every host of the paper is blocked; downgraded to D pending a paper-access retier. Metadata confirmed: MIT, 36 stars, 5 forks, not a fork, not archived, last commit 2023-01-08 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; peer-reviewed paper
- **Pages the verifier opened:**
  - <https://github.com/jermp/mutable_rank_select>
  - <https://github.com/jermp/mutable_rank_select/commits>
  - <https://github.com/jermp/mutable_rank_select/tree/master>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/types.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/perf_mutable_bitmap.cpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/jermp/mutable_rank_select>
  - <https://github.com/jermp/mutable_rank_select/tree/master/include>
  - <https://github.com/jermp/mutable_rank_select/tree/master/include/hft>
  - <https://github.com/jermp/mutable_rank_select/tree/master/include/segment_tree>
  - <https://github.com/jermp/mutable_rank_select/tree/master/src>
  - <https://github.com/jermp/mutable_rank_select/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/types.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/mutable_bitmap.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/util.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/segment_tree/avx2/segment_tree.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/segment_tree/avx2/node64.hpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/include/hft/README.md>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/perf_mutable_bitmap.cpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/perf_hft.cpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/perf_prefix_sum.cpp>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/src/collect_results.sh>
  - <https://raw.githubusercontent.com/jermp/mutable_rank_select/HEAD/test/test_mutable_bitmap.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jermp/mutable_rank_select`) · [data/wave9/enrich/raw/github_com_jermp_mutable_rank_select.json](../../../data/wave9/enrich/raw/github_com_jermp_mutable_rank_select.json) (enrichment confidence 0.75)

</details>
