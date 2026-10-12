# radix-heap (pair_radix_heap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Priority queues and heaps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++ monotone radix heap: 1.2-1.7x faster than std::priority_queue on Dijkstra shortest-path workloads.

| | |
|---|---|
| **Beats** | std::priority_queue |
| **Claimed result** | Pure priority-queue workload: 1.40-1.74x faster (e.g. USA-road-t.USA.gr: rheap 1.302186 vs stl 2.266316; USA-road-d.USA.gr: 1.222667 vs 2.119727). Overall Dijkstra time including edge traversal: \~1.12-1.29x faster (e.g. NY-d 0.024032 vs 0.027614, USA-t 3.817832 vs 4.934690). (derived from page data) |
| **Workload** | Dijkstra's shortest-path algorithm on real USA road networks (264K to 24M vertices, DIMACS challenge-9 datasets), averaged over 100 random sources; measures both pure priority-queue time and overall algorithm time |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-2690 0 @ 2.90GHz, 256GB RAM, Linux 3.2.0 |
| **Compiler and flags** | gcc 4.6.3, -O3 |
| **Adoption** | 67 stars |
| **Last commit** | 2015-05-16 |
| **Links** | [repository](https://github.com/iwiwi/radix-heap) · [benchmark](https://github.com/iwiwi/radix-heap/blob/master/example/README.md) |

## Verdict

Benchmarked as pair_radix_heap vs. libstdc++'s std::priority_queue inside a standard Dijkstra implementation over DIMACS challenge-9 real USA road networks (264K to 24M vertices), compiled with gcc 4.6.3 -O3 on an Intel Xeon E5-2690 0 @ 2.90GHz / 256GB RAM / Linux 3.2.0, averaged over 100 random sources per graph. Pure priority-queue time was 1.40-1.74x faster (e.g. USA-road-t.USA.gr: 1.302186s vs 2.266316s); overall Dijkstra time including edge traversal was 1.12-1.29x faster (e.g. USA-road-t.USA.gr: 3.817832s vs 4.934690s), with the speedup shrinking on the smallest (264K-vertex NY) graphs.

## Use it when

- Dijkstra's algorithm or other monotone-priority-queue algorithms over non-negative edge/cost weights
- Keys are native signed/unsigned integers or float/double (32- or 64-bit) that internal::encoder already handles
- Graph/grid search at the sizes benchmarked here (roughly 264K to 24M vertices), where the per-pop constant factor on the hot path matters
- Willing to vendor a single \~250-line header rather than pull in a build dependency
- Building with GCC or Clang (the bucket-index trick relies on their __builtin_clz/__builtin_clzll builtins)

## Skip it when

- Need a general-purpose priority queue where extracted keys can decrease (A\*, event simulation with re-priority, negative edge weights) -- violates the monotonicity assert and corrupts the heap silently in release builds
- Need a custom comparator or non-numeric/composite keys -- there is no comparator template parameter, only the built-in integer/float encoders
- Need MSVC support out of the box -- code depends on GCC/Clang builtins, not verified against MSVC's intrinsics
- Need active maintenance -- no commits since 2015-05-16, single closed issue (a README-language request), CI last validated on gcc 4.8/clang 3.4
- Need in-place decrease-key/update or erase of a pushed element -- not exposed; only push, pop, and clear

## How it is fast

Instead of a binary heap's comparison tree, it XOR-encodes keys into an order-preserving unsigned representation (internal::encoder, specialized for signed ints and IEEE float/double) and buckets each pushed key by the index of the highest bit where it differs from the last-extracted key (internal::find_bucket, via __builtin_clz/__builtin_clzll). Because extraction is monotone, popping only needs to redistribute the single lowest non-empty bucket into finer buckets one level at a time, rather than the O(log n) sift-down a binary heap performs on every pop -- giving O(1) amortized push and O(b) amortized pop where b is the key's bit width. This is the classic Ahuja/Mehlhorn/Orlin/Tarjan (1990) radix-heap algorithm.

## Compared with alternatives

Pick radix-heap when the workload is specifically a monotone shortest-path search (Dijkstra-style, non-negative weights) over integer/float keys in C++ -- prio_queue (rollbear) and Superscalar Sample Queue (S3Q) are general-purpose std::priority_queue replacements without the monotonicity restriction and are the better choice when keys can decrease or aren't numeric. If the same monotone-Dijkstra pattern is needed in Rust, use radix_heap_rust instead, since this library has no Rust port.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library (&lt;algorithm&gt;, &lt;array&gt;, &lt;cassert&gt;, &lt;climits&gt;, &lt;cstdint&gt;, &lt;limits&gt;, &lt;type_traits&gt;, &lt;utility&gt;, &lt;vector&gt;) |
| **Minimum toolchain** | C++11 (std::array, constexpr, variadic templates, std::piecewise_construct); CI-tested with gcc 4.8 and clang 3.4 per README/Travis badge |
| **Platforms** | GCC/Clang (uses __builtin_clz/__builtin_clzll); not documented or tested on MSVC |
| **Thread safety** | not documented; no locks/atomics in the source, assume single-threaded like std::priority_queue |
| **Drop-in for the baseline** | partial — explain: push/pop/top/size/empty/swap match std::priority_queue's shape and pair_radix_heap mirrors priority_queue&lt;pair&lt;K,V&gt;&gt; usage, but keys must be numeric and non-decreasing (monotone), there is no comparator template parameter, and top() returns by value with no operator&lt; customization point |

## Gotchas

- push() enforces monotonicity only via assert(last_ &lt;= x); in a release build compiled with NDEBUG a non-monotone push is silently accepted and produces wrong pop order rather than an error
- Each radix_heap/pair_radix_heap instance holds a fixed std::array of digits+1 std::vector buckets as members (33 buckets for 32-bit keys, 65 for 64-bit) -- more per-instance state than std::priority_queue's single vector, though the extra vectors are empty until pushes land in them
- No decrease-key, update, or erase of an already-pushed element -- only push/emplace, pop, top, clear
- Floating-point and signed-integer keys pass through an XOR bit-transform (internal::encoder) before bucketing; this is transparent through the public API but means the class is not usable with arbitrary user-defined key types, only the specializations provided

## Caveats and trade-offs

Benchmark dates from 2015 on hardware and a compiler of that era. There is no standalone LICENSE file, but the root README.md contains the full MIT License text ('Copyright (c) 2015 Takuya Akiba'). The root README's 'about 2X faster' is rounded up from the measured maximum of \~1.74x. Speedup grows with graph size (smallest on the 264K-vertex NY graph). No commits since 2015.

radix heap is a monotone priority queue: popped keys must be non-decreasing, so it only supports algorithms like Dijkstra with non-negative edge weights, not general priority-queue use; not a drop-in std::priority_queue replacement

## Maintenance

Abandoned since its last commit on 2015-05-16, but MIT-licensed (full license text in README.md, no separate LICENSE file) and a single \~250-line header, so it's cheap to vendor, read in full, and maintain yourself without upstream support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** example/README.md states gcc 4.6.3 -O3 on an Intel Xeon E5-2690 and tables rheap vs std::priority_queue on DIMACS USA road graphs. The benchmark code is public (example/benchmark_dijkstra_main.cc: 100 random sources, averaged).
- **Verifier notes:** The overall-time range was misstated: the smaller graphs show only \~1.12-1.15x, so the range is 1.12-1.29x, not 1.25-1.29x. The license is MIT (full text in README), so usability becomes copyable. All other metadata checks out: 67 stars, last commit 2015-05-16, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/iwiwi/radix-heap>
  - <https://github.com/iwiwi/radix-heap/blob/master/example/README.md>
  - <https://github.com/iwiwi/radix-heap/blob/master/example/benchmark_dijkstra_main.cc>
  - <https://github.com/iwiwi/radix-heap/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/iwiwi/radix-heap>
  - <https://github.com/iwiwi/radix-heap/blob/master/README.md>
  - <https://github.com/iwiwi/radix-heap/blob/master/example/README.md>
  - <https://github.com/iwiwi/radix-heap/blob/master/radix_heap.h>
  - https://github.com/iwiwi/radix-heap (repo file tree)
  - <https://github.com/iwiwi/radix-heap/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/iwiwi/radix-heap`) · [data/wave1/enrich/raw/github_com_iwiwi_radix_heap.json](../../../data/wave1/enrich/raw/github_com_iwiwi_radix_heap.json) (enrichment confidence 0.9)

</details>
