# fast-containers (SIMD/hugepage B+Tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++23 B+tree with SIMD search and hugepage allocators, 2-5x faster than std::map on large trees.

| | |
|---|---|
| **Beats** | std::map |
| **Claimed result** | \~2.1-4.8x faster insert/find/erase (P50 and P99.9) than std::map at 10M elements across both value sizes (e.g. INSERT P99.9 1023ns vs 3587ns, FIND P99.9 864ns vs 2312ns); at 10K elements std::map becomes competitive and wins some tail-latency cases (e.g. ERASE P99.9) |
| **Workload** | 10M-element trees (8-byte int64 key + 32-byte or 256-byte value); mixed insert/find/erase steady-state ops timed via RDTSC, P50 and P99.9 latency reported; also tested at 10K elements |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5950X (16-core), hyperthreading disabled, core 15 isolated via kernel boot params, Linux 6.16.3 |
| **Compiler and flags** | Clang, CMake Release build. CMakeLists.txt (at HEAD) sets -O3 -march=haswell -mtune=native -ffast-math -funroll-loops -fno-trapping-math plus ThinLTO (-flto=thin) and -mavx2 -mfma. Clang version not stated. |
| **Adoption** | 75 stars |
| **Last commit** | 2026-01-06 |
| **Links** | [repository](https://github.com/kressler/fast-containers) · [benchmark](https://github.com/kressler/fast-containers/blob/main/results/btree_benchmark_results.md) |

## Verdict

On an isolated core of an AMD Ryzen 9 5950X (Linux 6.16.3, Clang Release build with -O3 -march=haswell -mavx2 -mfma -flto=thin), the repo's own RDTSC-timed benchmark shows the SIMD+hugepage btree beating std::map by roughly 2.1-4.8x on P50/P99.9 insert/find/erase at 10M elements with 8-byte keys and 32B or 256B values; at 10K elements the advantage shrinks and std::map wins ERASE P99.9 with 256B values (213.6ns vs 245.7ns).

## Use it when

- Ordered int64-keyed maps with 32-256 byte values at large scale (roughly 1M-10M+ elements) where TLB misses and allocator overhead dominate runtime
- You need both P50 and P99.9 latency wins over std::map for insert/find/erase, not just throughput
- You control an x86-64 Linux environment with AVX2 (Haswell/Excavator or newer) and can configure OS hugepages
- You're willing to tune node size, SearchMode, and allocator per key/value size instead of relying on one default
- You're also considering Abseil's btree: this implementation beats absl+hugepages by 20-135% in the repo's own benchmarks

## Skip it when

- Trees under roughly 10K elements: std::map becomes competitive and even wins some tail-latency cases (e.g. ERASE P99.9 with 256B values: 213.6ns vs 245.7ns)
- Non-x86-64 or non-Linux targets — SIMD paths and RDTSC timing are x86-64-specific, and the README states Windows is untested
- Workloads relying on std::map's pointer/iterator stability across mutations; the header documents that some operations invalidate all iterators
- Environments where OS hugepages can't be configured/administered — losing hugepages removes most of the measured advantage
- Risk-averse adoption: single-author, explicitly AI-agent-assisted, actively-changing work-in-progress with self-reported, not independently reproduced benchmarks

## How it is fast

Fixed-size leaf/internal nodes (heuristically sized to \~1-2KB, 16-32 cache lines) replace the per-node pointer-chasing of a red-black tree. Node search uses AVX2 SIMD linear scans (`SearchMode::SIMD`) over a dense sorted array (`dense_map`) instead of branchy binary search. A pooling `HugePageAllocator` backs node storage with 2MB hugepages, cutting TLB misses and making allocation near-free compared to the default allocator; the README calls this 'the single most important optimization,' giving a 2-3x speedup on its own.

## Compared with alternatives

Pick this over tlx::btree_map or boost::container::flat_map/flat_set when the workload is specifically very large (multi-million element), int64-keyed trees on x86-64 Linux and hugepages are available to configure; its P99.9 gains at 10M elements are larger than tlx's reported multiset comparisons and target a size range boost's flat_set (best at 2-256 elements) doesn't cover. Prefer tlx or boost instead for portability, small-to-mid-size trees, or a longer track record than a single-author work-in-progress.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself; tests/benchmarks pull in Abseil, Google Benchmark, Catch2, lyra, unordered_dense, and a histograms library as git submodules |
| **Minimum toolchain** | C++23, GCC 14+ or Clang 19+, CMake 3.30+ |
| **Platforms** | x86-64 with AVX2 (Intel Haswell 2013+ / AMD Excavator 2015+); built and tested on Linux only |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — insert/find/erase/iteration match std::map's shape, but the template signature, iterator value_type (pair&lt;Key,Value&gt;, not pair&lt;const Key,Value&gt;), and full method surface differ; a closed issue ('Add missing std::map interface methods to btree') indicates parity work is ongoing, not complete |

## Gotchas

- Header docs state some operations invalidate all iterators — no red-black-tree-style iterator/pointer stability like std::map
- A closed bug (issue #47) found incorrect SIMD comparison semantics for composite and unsigned key types — fixed, but signals SIMD comparator correctness needs care for non-trivial key types
- The hugepage allocator needs OS-level hugepage configuration; without it the library is still faster than std::map but by a much smaller margin than the headline numbers
- The benchmarked 'winner' configuration (SIMD search + hugepage allocator, specific leaf/internal node sizes) is one tuned instantiation — other node-size/SearchMode combinations are meaningfully slower

## Caveats and trade-offs

Single-author work-in-progress project explicitly built with heavy AI-agent assistance per README; benchmark is self-reported and not independently reproduced; which std::map/libstdc++ or libc++ variant was tested is not stated; advantage shrinks or reverses at small (10K) tree sizes

Requires C++23 (GCC14+/Clang19+) and x86-64 AVX2; SIMD search paths and RDTSC timing are x86-64 specific; hugepage allocator needs OS hugepage configuration; no pointer/iterator stability guarantee like std::map; only built/tested on Linux

## Maintenance

Actively developed (last commit 2026-01-06, all filed issues closed) but explicitly a single-author work-in-progress built with heavy AI-agent assistance; BSD-3-Clause and header-only make it cheap to vendor, but expect API and behavior churn before treating it as stable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** results/btree_benchmark_results.md compares directly against std::map (map_8_32, map_8_256) using in-repo code src/binary/btree_benchmark.cpp and scripts/interleaved_btree_benchmark.py. It states the hardware (Ryzen 9 5950X, isolated core, Linux 6.16.3) and compiler (Clang Release), and CMakeLists.txt pins the Release flags.
- **Verifier notes:** All claimed numbers match the page. 10M-element ratios vs std::map range from \~2.1x (ERASE P99.9, 32B) to \~4.8x (INSERT P99.9, 256B). The top config uses the hugepage allocator. At 10K elements with 256B values, std::map wins ERASE P99.9 (213.6 vs 245.7 ns). The README confirms that development was AI-assisted (Claude) and that the project is a work in progress. Metadata checked: BSD-3-Clause, 75 stars, last commit 2026-01-06.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/kressler/fast-containers>
  - <https://github.com/kressler/fast-containers/blob/main/results/btree_benchmark_results.md>
  - <https://github.com/kressler/fast-containers/blob/main/README.md>
  - <https://github.com/kressler/fast-containers/blob/main/CMakeLists.txt>
  - <https://github.com/kressler/fast-containers/blob/main/CMakePresets.json>
  - <https://github.com/kressler/fast-containers/blob/main/src/binary/btree_benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/kressler/fast-containers>
  - <https://github.com/kressler/fast-containers/blob/main/README.md>
  - <https://github.com/kressler/fast-containers/blob/main/results/btree_benchmark_results.md>
  - <https://github.com/kressler/fast-containers/blob/main/include/fast_containers/btree.hpp>
  - <https://github.com/kressler/fast-containers/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/kressler/fast-containers`) · [data/wave1/enrich/raw/github_com_kressler_fast_containers.json](../../../data/wave1/enrich/raw/github_com_kressler_fast_containers.json) (enrichment confidence 0.72)

</details>
