# CRoaring (Roaring Bitmaps)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0 OR MIT` · 🟢 active

> Compressed bitmap for sparse 32/64-bit integer sets; set-algebra ops beat std::unordered_set/vector by 3x-800x, loses on dense data.

| | |
|---|---|
| **Beats** | std::unordered_set&lt;uint32_t&gt; and sorted std::vector&lt;uint32_t&gt; with STL set algorithms (std::set_intersection/union/difference, std::binary_search) from the standard library bundled with GCC 5.4; also an uncompressed bitset (the authors' portable C 'cbitset', same word-array layout as std::bitset/std::vector&lt;bool&gt;) |
| **Claimed result** | Mixed by dataset and operation (CPU cycles per input value, Tables 4/6/7). vs C++ standard library containers: two-by-two intersections (Table 7a), sorted std::vector + std::set_intersection 7.84 vs Roaring 0.220 on CensusInc (\~36x, derived from page data), 3.28 vs 0.090 on Census1881 (\~36x, derived from page data), 4.15 vs 1.43 on Wikileaks (\~2.9x, derived from page data); std::unordered_set 55.3 vs 0.220 on CensusInc (\~251x, derived from page data), 0.480 vs 0.090 on Census1881 (\~5.3x, derived from page data); unions (Table 7b) std::unordered_set 210 vs 0.270 on CensusInc (\~778x, derived from page data). Membership queries (Table 6): Roaring beats std::vector + std::binary_search on every dataset (e.g. 63.6 vs 415 cycles on CensusInc), but std::unordered_set is faster than Roaring on CensusInc, CensusInc-sorted, Weather and Weather-sorted (e.g. 49.2 vs 63.6) and slower on Census1881 (38.2 vs 17.4). vs uncompressed bitset (cbitset): intersections 19.5 vs 0.090 on Census1881 (\~217x, derived from page data), 33.0 vs 0.140 on Census1881-sorted (\~236x, derived from page data), 26.4 vs 1.43 on Wikileaks (\~18x, derived from page data); but on CensusInc/CensusInc-sorted/Weather the bitset is faster (CensusInc: bitset 0.120-0.130 vs Roaring 0.220-0.370 across the four set operations, \~1.7-3.1x, derived from page data). Bitset wins every membership query (2.36-3.74 vs Roaring 17.4-76.8 cycles). Memory (Table 4, bits/value): Roaring 15.1 vs bitset 524 on Census1881, 2.60 vs 5.66 on CensusInc, 0.340 vs 11.4 on Weather-sorted; std::vector uses 32 and std::unordered_set 195 bits/value on every dataset. |
| **Workload** | 8 realistic integer-set datasets (CensusInc, CensusInc-sorted, Census1881, Census1881-sorted, Weather, Weather-sorted, Wikileaks, Wikileaks-sorted; 200 sets each, universe sizes 200K-4.3M): sequential iteration/cardinality, random-access membership queries at n/4, n/2, 3n/4, and 199 pairwise intersections/unions/differences/symmetric differences between successive sets. Reported as CPU cycles per input value. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6700 (Skylake, 3.4 GHz, 32KB L1d, 256KB L2/core, 8MB L3), 32GB DDR4-2133 dual-channel, single-threaded, Turbo Boost disabled, timed with rdtsc, results reproducible within 5% |
| **Compiler and flags** | GNU GCC 5.4, compiled with -O3 -march=native |
| **Adoption** | 1,887 stars; used by Apache Doris, ClickHouse, Alibaba Tair, Redpanda, YDB, StarRocks |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/RoaringBitmap/CRoaring) · [benchmark](https://arxiv.org/pdf/1709.07821) |

## Verdict

Paper (Lemire et al., Software: Practice and Experience 2018, arXiv:1709.07821) benchmarked CRoaring single-threaded on an Intel i7-6700 (Skylake, Turbo off) against GCC 5.4 libstdc++ std::vector+STL set algorithms, std::unordered_set, and the authors' own uncompressed 'cbitset', compiled with -O3 -march=native, across 8 real 32-bit integer-set datasets (200 sets each, timed with rdtsc). Roaring's pairwise intersections beat sorted-vector+std::set_intersection by \~3-36x and std::unordered_set by up to \~250x while using 15.1 bits/value on Census1881 vs 195 for std::unordered_set and 32 for std::vector, but a plain uncompressed bitset beat Roaring on every membership query and on set algebra for dense/small-universe datasets.

## Use it when

- Sets of 32-bit (or 64-bit) integers with variable, often sparse cardinality where you repeatedly compute intersections/unions/differences (search-index posting lists, ID filtering, join pushdown)
- Memory is a constraint: paper Table 4 shows Roaring at 15.1 bits/value on Census1881 and 2.60 on CensusInc vs 195 for std::unordered_set and 32 for std::vector on every dataset
- Throughput-oriented batch set algebra rather than single-key latency-sensitive lookups
- x86-64 (gets AVX2/AVX-512 runtime dispatch) or ARM/POWER/big-endian/RISC-V via the generic scalar path
- Need cross-language interop: portable serialization format shared with the Java, Go, Python, and Rust Roaring implementations

## Skip it when

- Fixed-size dense bit flags: a plain uncompressed bitset (the authors' own cbitset) beats Roaring by \~1.7-3x on dense/small-universe datasets and by roughly an order of magnitude on every membership query in the paper's Tables 6/7
- Membership-query-heavy workloads on clustered/dense data: std::unordered_set was faster than Roaring on 4 of 8 paper datasets for random-access contains()
- Multithreaded mutation: no built-in locking; a bitmap being modified must not be queried on another thread, and safe sharing requires passing copies (optionally with copy-on-write enabled)
- 64-bit sets via Roaring64Map specifically — issue #225 (open) reports poor read/write performance for its std::map-of-32-bit-buckets design; the ART-based Roaring64 alternative is marked experimental
- Untrusted input handled carelessly: the 32-bit API's unsafe portable_deserialize can read out of bounds on malformed data; must use the \*_safe variant plus roaring_bitmap_internal_validate

## How it is fast

Values are bucketed by their high 16 bits into 'containers' that switch representation per bucket: a sorted array for sparse chunks, a plain bitset for dense chunks, or a run-length list for consecutive runs (include/roaring/containers/{array,bitset,run}.h), so every 65536-value chunk stores whatever layout is smallest. Set operations dispatch per-container based on both operands' types (mixed_intersection.h, mixed_union.h, etc.) and use runtime-dispatched AVX2/AVX-512 SIMD on x86-64 for bitset and array operations. This adaptivity is what produces both the \~35x memory reduction over an uncompressed bitset and the win over linear STL set algebra on sparse/clustered data.

## Compared with alternatives

Pick CRoaring over plf::bitset, better_bitset, BitLib, or sul::dynamic_bitset when the domain is a sparse, dynamically-sized 32/64-bit integer \*set\* with heavy AND/OR/XOR/ANDNOT algebra — those siblings instead accelerate fixed-width std::bitset/std::vector&lt;bool&gt;-style dense bit-vector ops like shift/test/reset. Prefer pasta::bit_vector or a plain uncompressed bitset instead of CRoaring for succinct rank/select or dense small-universe bitsets, where CRoaring's per-container overhead loses on both memory and membership-query latency.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated single-file roaring.c/roaring.h/roaring.hh via amalgamation.sh) or static/shared lib via CMake |
| **Dependencies** | none for the C library; C++11-capable compiler only if using the optional roaring.hh/roaring64map.hh wrapper |
| **Minimum toolchain** | C11 (GCC 7+, clang 8+, MSVC 2022+, Xcode 11+, Intel oneAPI 2023.2+); C++11+ for the C++ wrapper |
| **Platforms** | x86-64 (AVX2/AVX-512 runtime-dispatched, no special build flags needed), ARM, POWER, big-endian, generic scalar path for others including RISC-V |
| **Thread safety** | No built-in locking, same posture as STL containers per README: concurrent reads of an unmodified bitmap are safe, but a bitmap being modified must not be read elsewhere; safe cross-thread use means passing copies, with copy-on-write (off by default) making those copies cheap via atomic-refcounted shared containers |
| **Drop-in for the baseline** | false — opaque handle + explicit free() in C, or a distinct RAII class with operator overloads in C++; not a header substitution for std::unordered_set or std::vector&lt;uint32_t&gt; |

## Gotchas

- roaring_bitmap_portable_deserialize (32-bit, unsafe variant) reads out of bounds on malformed input; use the \*_deserialize_safe variant plus roaring_bitmap_internal_validate for untrusted data (the 64-bit API only exposes the safe form)
- Two distinct 64-bit classes exist: Roaring64Map (std::map-keyed 32-bit Roaring buckets, flagged as having bad read/write performance in open issue #225) vs Roaring64 (ART-based, wraps roaring64.h, marked experimental)
- Copy-on-write is opt-in and off by default; mixing bitmaps with different COW settings was flagged unsafe in a still-open issue (#97) — set it consistently before sharing bitmaps across threads
- Run-container compression (runOptimize()/runOptimize) is not automatic — a bitmap built by looping add() over consecutive ranges keeps its original array/bitset containers until you explicitly call it

## Caveats and trade-offs

Results depend heavily on dataset and operation: Roaring loses to a plain bitset on dense datasets and on all membership queries, and loses to std::unordered_set on membership queries for 4 of 8 datasets. The bitset baseline is the authors' own 'cbitset' C library, not std::bitset/std::vector&lt;bool&gt;. The STL containers are literally the standard library that ships with GCC 5.4 (libstdc++ inferred from 'the standard C++ library bundled with our compiler' on Linux), which is from 2016. The paper's authors also maintain the library (Lemire et al., Software: Practice and Experience 2018), but the code, compiler, flags and CPU are all public.

Roaring wins decisively on memory and on set-algebra over sparse/clustered 32-bit integer sets, but loses to a plain uncompressed bitset on random-access membership queries (bitset has roughly an order of magnitude lower latency) and can lose on set-algebra for dense/small-universe datasets. Targets dynamic sparse 32-bit integer sets, not fixed-size dense bit flags, so it is not a general drop-in for std::bitset&lt;N&gt; or std::vector&lt;bool&gt;.

## Maintenance

Actively maintained (push activity as of today, 1,887 stars, used in production by ClickHouse, Apache Doris, Redpanda, YDB, Alibaba Tair, and StarRocks); dual Apache-2.0/MIT licensed, so the amalgamated single-file build is safe to vendor regardless of future upstream changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** Paper sec. 5 states GCC 5.4, -O3 -march=native, Intel i7-6700 (Skylake), and the benchmark code is public at github.com/RoaringBitmap/CBitmapCompetition (src/roaring_benchmarks.c, src/bitset_benchmarks.c, src/stl_vector_benchmarks.cpp, src/stl_hashset_benchmarks.cpp); it benchmarks the compiler's own C++ standard library containers (std::vector, std::unordered_set) as well as an uncompressed bitset.
- **Verifier notes:** Tier A stands. Downgraded because claimed_speedup mis-transcribed Table 4: Roaring on Census1881 uses 15.1 bits/value, not 2.60 (2.60 is CensusInc), so the memory win was overstated about 6x (\~35x, not \~200x). Also the 0.380 in the CensusInc Roaring range belongs to BitMagic. Added the paper's direct libstdc++ std::vector/std::unordered_set comparisons, a stronger stdlib baseline than cbitset. License (Apache-2.0 OR MIT, from LICENSE since spdx=NOASSERTION), stars and last commit 2026-09-23 all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `baseline_stdlib`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** With two 10k-value sets over a 0..100M domain, AND took 104,928 ns vs 2,303,116 ns for std::bitset&lt;100000000&gt; (21.95x) at 32 KB vs 12.5 MB per bitmap (388x smaller), and iterating was 2782.7x faster (34,163 vs 95,069,724 ns). and_cardinality() answered |A&B| in 36,572 ns, and std::set&lt;uint32_t&gt; also beat the bitset here (325,412 ns). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, min of 3 samples, run 2026-09-03-third-party); Inversion on 50%-dense data (5M values over 0..10M): an in-place std::bitset &= beat Roaring's AND (147,744 vs 165,892 ns, 1.12x), Roaring's iterator was 2.7x slower than scanning a bitset (24.4 vs 9.2 ms), and its footprint was slightly larger than the raw bits (1.204 vs 1.192 MB). Only and_cardinality() still won clearly (46,809 ns, 3.2x the best bitset formulation). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, min of 3 samples, run 2026-09-03-third-party); Point queries lost in both regimes: 200k probes at \~50% hit rate cost 22.849 ns per contains() on dense data vs 1.07 ns for std::bitset (21.35x slower; 15x slower on sparse data). Sorting the probes for containsBulk() only brought it to 2.053 ns. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/1709.07821>
  - <https://github.com/RoaringBitmap/CRoaring>
  - <https://github.com/RoaringBitmap/CBitmapCompetition>
- **Sources the enricher read:**
  - <https://github.com/RoaringBitmap/CRoaring>
  - <https://github.com/RoaringBitmap/CRoaring/blob/master/README.md>
  - <https://github.com/RoaringBitmap/CRoaring/blob/master/LICENSE>
  - <https://github.com/RoaringBitmap/CRoaring/tree/master/include/roaring>
  - <https://github.com/RoaringBitmap/CRoaring/tree/master/include/roaring/containers>
  - <https://github.com/RoaringBitmap/CRoaring/tree/master/src>
  - <https://github.com/RoaringBitmap/CRoaring/issues>
  - <https://arxiv.org/pdf/1709.07821>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/roaringbitmap/croaring`) · [data/wave1/enrich/raw/github_com_roaringbitmap_croaring.json](../../../data/wave1/enrich/raw/github_com_roaringbitmap_croaring.json) (enrichment confidence 0.6)

</details>
