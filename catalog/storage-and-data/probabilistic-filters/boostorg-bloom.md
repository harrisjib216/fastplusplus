# Boost.Bloom (block / multiblock filter configurations)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++11 Boost filter template whose cache-local block and SIMD multiblock subfilters run 2.6-5x faster than a classical Bloom filter.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | The quoted numbers belong to the block&lt;uint64_t,K&gt; configurations, not multiblock. GCC 14 x64, N=1M, same bits/element: at c=8, block insertion is 3.99 ns (5.07 ns for block&lt;...&gt;,1) vs 11.04 ns for the classical filter&lt;int,K&gt;, and lookup is 4.60-5.12 ns vs 12.08-19.38 ns. At c=16, insertion is 5.02/5.55 ns vs 20.28 ns and lookup 5.62-6.02 ns vs 18.12-22.04 ns. That is about 2.6-4x (derived from page data). fast_multiblock32 (AVX2) reaches 2.72-3.22 ns at c=8/12. At N=10M, c=16, the classical filter takes 85.98 ns to insert and 95.66 ns per successful lookup vs 16.90/18.69 ns for block, about 5x (derived from page data). Plain multiblock is slower than block, e.g. 9.18 ns insertion and 11.79 ns lookup at c=16, N=1M. |
| **Workload** | Insertion and successful/unsuccessful/mixed lookup of int keys (N=1M) comparing boost::bloom::filter's classical single-array configuration (filter&lt;int,K&gt;) against its block/multiblock/fast_multiblock32 configurations at equal bits-per-item budgets. |
| **Metric** | throughput |
| **Compiler and flags** | g++-14 -m64 -march=native -std=c++2b -O3 -DNDEBUG (from boost_bloom_benchmarks/.github/workflows/benchmarks.yml). The page also tabulates Clang 18 x64, Clang 15 ARM64, VS2022 (/arch:AVX2) and x86 builds. |
| **Adoption** | 37 stars; official Boost library since Boost 1.89, distributed via vcpkg (boost-bloom) and Conan |
| **Last commit** | 2026-06-19 |
| **Links** | [repository](https://github.com/boostorg/bloom) · [benchmark](https://github.com/boostorg/boost_bloom_benchmarks#readme) |

## Verdict

In the project's own boost_bloom_benchmarks (GCC 14 x64, -O3 -march=native, unique random ints from splitmix64, single-threaded element-at-a-time loops, self-hosted runner with an unnamed CPU), at N=1M and equal bits/element (c=8-16) block&lt;uint64_t,K&gt; inserts in 3.99-5.55 ns vs 11.04-20.28 ns and looks up in 4.6-6.0 ns vs 12.1-22.0 ns for the classical filter&lt;int,K&gt; (about 2.6-4x), rising to about 5x for insert and successful lookup at N=10M, c=16 but only about 1.8x for unsuccessful lookup (18.7 vs 34.2 ns). The baseline is the library's own classical configuration, not another library, and block pays about 10x the FPR at c=16.

## Use it when

- Filtering negative lookups in front of disk, network or database accesses, when you need tens to hundreds of millions of inserts or probes per second per core and can accept a higher FPR at the same bits/key (or spend a few extra bits/key to get it back).
- Filters much larger than the CPU cache (N of 1M and up, tens of MB): the gap grows with size. At N=10M, c=16, GCC 14 x64, the classical filter takes 86.0 ns to insert and 95.7 ns per successful lookup vs 16.9/18.7 ns for block&lt;uint64_t,6&gt;.
- Builds with AVX2 enabled (-mavx2, -march=native or /arch:AVX2), or AArch64 with Neon: fast_multiblock32&lt;K'&gt; gives the best speed/FPR mix. At N=1M on GCC 14 x64 it runs at 2.7-3.2 ns per operation at c=8-12 with 0.54% FPR at c=12, vs 1.05% for block&lt;uint64_t,5&gt;.
- Batch workloads that can use insert(first,last) or bulk may_contain: the docs' GCC 14 x64 table at N=10M shows a further 1.2-3.5x for most configurations.
- Projects already on Boost 1.89+ (or vcpkg boost-bloom or Conan) that want a maintained, allocator-aware, header-only C++11 filter with built-in capacity_for/fpr_for sizing helpers.

## Skip it when

- When FPR per bit is the priority: at c=16, block&lt;uint64_t,6&gt; has 0.42% FPR vs 0.045% for the classical filter&lt;int,11&gt;. Use the classical config, a wider multiblock, or more bits/key.
- When you need deletion, counting, growth, an element count, try_insert or a runtime K. The filter is insert-only with a fixed capacity and no size(); try_insert, size estimation and runtime K are listed only as future work.
- Static key sets built once: the library's own future-work page says cuckoo and xor filters are 'more space efficient and potentially faster', and it offers neither.
- Many threads writing to one filter: there are no atomic or concurrent insert operations, and thread safety is not documented.
- When memory is not the constraint and keys are small: in the same benchmark, an exact boost::unordered_flat_set&lt;int&gt; looks up in 5.63/4.24 ns (successful/unsuccessful) at N=1M and 23.11/14.68 ns at N=10M. That is comparable to block filters (4.6 ns at c=8, N=1M; 18.7 ns at c=16, N=10M), though its inserts are much slower (38.9 and 58.1 ns).

## How it is fast

It uses blocked Bloom filtering: block&lt;Block,K'&gt; sets all K' bits inside one hash-chosen Block (a uint64_t, or a 64-byte uint64_t[8]), so an operation touches one cache line instead of K scattered ones, while multiblock sets one bit in each of K' consecutive words (split-block layout; fast_multiblock32&lt;8&gt; matches the Impala uint32_t[8] bucket). Each element is hashed once: Lemire's fastrange picks the subarray, a multiplicative congruential generator (Steele-Vigna constant) re-mixes the hash, bit positions are sliced from it, and a 128-bit multiply-xor mix is applied first for hashes that do not avalanche, such as boost::hash&lt;int&gt;. The fast_multiblock variants build the bit masks with SIMD (AVX2 _mm256_sllv_epi32, an SSE2 float-exponent trick, or little-endian Neon). The core issues software prefetches for the target cache lines, and since Boost 1.90 bulk insert and bulk may_contain pipeline hashing and prefetching over batches of up to 64 elements, with branchless lookups for block and fast_multiblock.

## Compared with alternatives

Against the Impala-derived SIMD Blocked Bloom in efficient/cuckoofilter (one fixed AVX2-only uint32_t[8] bucket), pick this when you want the same layout via fast_multiblock32&lt;8&gt; plus SSE2, Neon and scalar fallbacks, a tunable K', allocator support and Boost/vcpkg/Conan packaging. Against Xor Filter, BuRR or other static filters, pick it when keys arrive incrementally and extra bits/key are acceptable.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Assert, Boost.Config, Boost.ContainerHash, Boost.Core, Boost.ThrowException, Boost.TypeTraits (all header-only, per CMakeLists.txt) |
| **Minimum toolchain** | C++11. The docs say it is verified with GCC 4.8, Clang 3.9, VS2015 and later. It ships in Boost 1.89+, and bulk operations and branchless lookups need Boost 1.90+. |
| **Platforms** | Any (scalar fallback). SIMD paths are selected at compile time, with no runtime CPU dispatch: AVX2 for fast_multiblock32/64, SSE2 for fast_multiblock32, and little-endian Neon for fast_multiblock32. Benchmarks were published for x64, x86 and ARM64 (macOS). |
| **Thread safety** | Not documented. The core uses no atomics, so concurrent inserts need external locking. |
| **Drop-in for the baseline** | partial: filter&lt;T,K&gt; is itself a classical Bloom filter with insert/may_contain semantics, and moving to block or multiblock is a one-line typedef change. You must re-tune K' and capacity for the target FPR, the capacity argument is in bits, and saved bit arrays cannot be exchanged between configurations. |

## Gotchas

- The single-argument constructor takes bits, not elements: filter f(1'000'000) is 1M bits. The (n, fpr) overload with a tiny FPR can throw std::bad_alloc; the docs' example with 1E-50 needs about 1.4E12 bits.
- SIMD selection depends on compile flags (__AVX2__, __SSE2__, little-endian __ARM_NEON). Without -mavx2 or -march=native, an x64 build falls back to the SSE2 fast_multiblock32 and to scalar multiblock&lt;uint64_t&gt; for fast_multiblock64. The AVX2 and SSE2 fast_multiblock32 code take different hash bits (per source), so an array saved from one build is not valid in another. The docs warn only that endianness must match.
- fpr_for is an a-priori estimate that assumes n distinct inserts. Duplicates make it pessimistic (issue #19), and the docs say not to trust it after &= intersection.
- Not every fast-looking option is faster. Plain multiblock&lt;uint64_t,11&gt; is slower than block&lt;uint64_t,6&gt; at c=16, N=1M (9.18 vs 5.02 ns insert). A Stride below the block size lowers FPR but allows unaligned accesses. Bulk mode can lose: 0.78x for classical successful lookup at c=8 in the docs' GCC 14 table.

## Known shortcomings

- The numbers are for block&lt;uint64_t,K&gt; configurations, not multiblock; block filters have \~10x worse FPR at c=16; self-hosted CI runner with no CPU stated.
- First-party numbers vs its own classical configuration on an unnamed self-hosted CPU. At N=10M, c=16 unsuccessful lookups are only \~1.8x faster (18.7 vs 34.2 ns; inserts/successful lookups \~5x), and boost::unordered_flat_set&lt;int&gt; lookups are in the same ballpark in its own bench, so the win is memory rather than speed. SIMD is chosen at compile time and AVX2 vs SSE2 fast_multiblock32 use different hash bits, so saved arrays are not portable across builds.
- Insert-only with fixed capacity (no size/delete/try_insert/runtime K); thread safety undocumented (no atomics); the capacity argument is in bits.

## Caveats and trade-offs

The benchmark workflow runs on a self-hosted runner ([self-hosted, linux, x64]) and never names the CPU model. The numbers are the project's own and have not been reproduced independently. The baseline is the library's own classical Bloom configuration. At equal bits/element, block filters trade FPR for speed: at c=16, N=1M, the FPR is 0.42% for block vs 0.045% for classical, about 10x worse. The workflow builds the author's joaquintides/bloom develop branch. There is no LICENSE file at the repo root; the headers and README badge state BSL-1.0.

Header-only, C++11. Block/multiblock variants trade a small FPR increase (at matched c) for large speed gains by confining all K bit-sets to one or few cache lines; classical filter&lt;int,K&gt; remains available for lowest FPR at a given c.

## Maintenance

Active: it went through Boost peer review in May 2025, first shipped in Boost 1.89 and gained bulk operations in 1.90, its last commit (2026-06-19) was CI upkeep with no bug issues open, and it is BSL-1.0 (stated in headers and README, with no root LICENSE file) and header-only via Boost, vcpkg or Conan.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party numbers from public benchmark code: boostorg/bloom benchmark/comparison_table.cpp, run by boost_bloom_benchmarks/.github/workflows/benchmarks.yml. The compiler and flags are stated, but the run happens on a self-hosted runner and no CPU model is named anywhere, so the entry cannot be A.
- **Verifier notes:** The record was accurate apart from calling the quoted numbers 'block/multiblock': the ranges fit only the two block&lt;uint64_t,K&gt; columns, so the claim was rewritten. The main tradeoff to flag is that block filters have a higher FPR at the same c. License is BSL-1.0 (GitHub API returns null because there is no root LICENSE file). 37 stars; last commit 2026-06-19 on both master and develop.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/bloom>
  - <https://github.com/boostorg/bloom/blob/develop/README.md>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/filter.hpp>
  - <https://github.com/boostorg/boost_bloom_benchmarks#readme>
  - <https://github.com/boostorg/boost_bloom_benchmarks/blob/main/.github/workflows/benchmarks.yml>
- **Sources the enricher read:**
  - <https://github.com/boostorg/bloom>
  - <https://github.com/boostorg/bloom#readme>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/intro.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/primer.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/tutorial.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/configuration.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/implementation_notes.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/release_notes.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/future_work.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/benchmarks.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/doc/bloom/reference/filter.adoc>
  - <https://github.com/boostorg/bloom/blob/develop/CMakeLists.txt>
  - <https://github.com/boostorg/bloom/blob/develop/meta/libraries.json>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/detail/core.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/fast_multiblock32.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/multiblock.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/detail/avx2.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/detail/neon.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/detail/fast_multiblock32_avx2.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/include/boost/bloom/detail/fast_multiblock32_sse2.hpp>
  - <https://github.com/boostorg/bloom/blob/develop/benchmark/comparison_table.cpp>
  - <https://github.com/boostorg/bloom/issues?q=is%3Aissue>
  - <https://github.com/boostorg/bloom/pulls?q=is%3Apr>
  - <https://github.com/boostorg/bloom/issues/19>
  - <https://github.com/boostorg/bloom/issues/20>
  - <https://github.com/boostorg/bloom/issues/22>
  - <https://github.com/boostorg/bloom/issues/31>
  - <https://github.com/boostorg/boost_bloom_benchmarks#readme>
  - <https://github.com/boostorg/boost_bloom_benchmarks/blob/main/.github/workflows/benchmarks.yml>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/simd-block.h>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/boostorg/bloom`) · [data/wave6/enrich/raw/github_com_boostorg_bloom.json](../../../data/wave6/enrich/raw/github_com_boostorg_bloom.json) (enrichment confidence 0.85)

</details>
