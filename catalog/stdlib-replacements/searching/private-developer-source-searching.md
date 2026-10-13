# fastcpp::algo::lower_bound (branchless / Eytzinger) (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Three header-only lower_bound variants (branchless cmov, cmov+prefetch, Eytzinger layout); 5.8x std::lower_bound in L1, 1.9x from DRAM on ints.

| | |
|---|---|
| **Beats** | std::lower_bound |
| **Claimed result** | 5.83x on the L1-resident array (branchless cmov: 11.562ns vs std::lower_bound's 67.401ns, 4096 ints). 1.91x on the DRAM-sized array (explicit-prefetch variant: 224.04ns vs std::lower_bound's 427.706ns, 4.2M ints). Eytzinger layout measured 80.132ns on that same 4.2M-int DRAM workload, i.e. 5.34x vs std::lower_bound's 427.706ns (derived from page data: the Eytzinger row's own recorded baseline is 'branchless cmov, sorted layout' at 317.093ns, a 3.96x win, not std::lower_bound directly, but both rows share the same run and workload size). |
| **Workload** | bench/bench_doing_less.cpp bench_binary_search(): 20,000 random-key lower_bound queries over sorted int arrays of 4096 ints (16 KiB, L1-resident) and 4,194,304 ints (16 MiB, exceeds L2). Compares a branchless-cmov lower_bound, a branchless+prefetch variant and an Eytzinger (breadth-first, with prefetch) layout against std::lower_bound; gcc 13.3.0 -O2 -march=native, min of 7 samples. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores, Ubuntu 24.04, Linux 6.18, shared cloud VM |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo; run label 2026-09-02-core) |
| **Adoption** | 0 stars (private repository) |
| **Last commit** | 2026-09-04 |
| **Links** | private repository, not published yet |

## Verdict

The repo's own bench_doing_less (20,000 random-key queries per pass, minimum of 7 samples) compares against libstdc++ std::lower_bound on gcc 13.3.0 -O2 -march=native on a shared 4-core Intel Xeon 2.1 GHz VM: branchless takes 11.6 vs 67.4 ns per query on 4,096 ints (5.83x), and the prefetch variant 224.0 vs 427.7 ns on 4,194,304 ints (1.91x). On that same 4.2M array the Eytzinger layout took 80.1 ns, 3.96x faster than the branchless search it was timed next to. That puts it about 5.3x ahead of std::lower_bound, but the 5.3x comes from comparing two tables in the same run, not from one direct measurement.

## Use it when

- Hot lower_bound calls on a read-only sorted array of small, cheaply compared keys that fits in cache: plain branchless measured 11.6 ns vs 67.4 ns per query on 4,096 ints (16 KiB).
- Sorted arrays larger than cache where you must keep sorted order and get a position back: use lower_bound_prefetch, the only variant the repo records as a stable win there (1.91x in the published row; the header comment says 'a stable 1.6x').
- Build-once, search-many lookup tables larger than cache where you can give up sorted order: on the same 4.2M-int array the Eytzinger layout measured 80.1 ns against 317.1 ns for branchless, about 5.3x std::lower_bound's 427.7 ns in that run.
- Batches of independent lookups (the benchmark's shape: 20,000 unrelated random keys per pass) built with GCC on x86-64, the only toolchain and ISA the numbers cover.

## Skip it when

- Memory-bound searches with the plain branchless function: the repo records it at 0.72x-1.49x of std::lower_bound on the 16 MiB array across five runs, so it can lose.
- Cache-resident arrays with the prefetch variant: there it was slower than plain branchless (14.9 vs 11.6 ns), because the wasted prefetches still use load slots.
- Exact-match lookups where ordering doesn't matter: on a 92-keyword set the same repo measured a sorted array plus binary search at 69.7 ns, its flat_hash_map at 8.9 ns and its perfect hash table at 3.3 ns.
- Data that changes between searches, or callers who need an iterator or rank from the Eytzinger search: the layout leaves the array unsorted, must be rebuilt after any change, and returns a tree index.
- Other compilers, clang, MSVC or non-int keys without re-measuring: the header warns the cmov codegen 'is not stable across compilers or versions', FASTCPP_PREFETCH_READ is a no-op outside GCC/Clang, and only gcc 13.3 with libstdc++ on one Xeon VM was benchmarked.

## How it is fast

Branchless binary search: the step is spelled `base += size_t(less(base[half-1], key)) * half`, which gcc 13 compiles to cmovge. That removes the \~log2(n) unpredictable branches that std::lower_bound mispredicts. The prefetch variant also __builtin_prefetch-es both candidate next probes, which restores the free prefetching that a branchy search gets from speculatively loading wrong-path elements; that is why it still wins once the array misses to DRAM. The Eytzinger layout (Khuong & Morin, 'Array layouts for comparison-based searching') stores the implicit search tree breadth-first so the top levels share cache lines, prefetches tree[index\*16] (the node's descendants four levels down) and recovers the answer from the final index's trailing ones with std::countr_one.

## Compared with alternatives

No siblings catalogued yet.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond fastcpp/core/macros.hpp (for FASTCPP_ALWAYS_INLINE and FASTCPP_PREFETCH_READ) and &lt;bit&gt;, &lt;cstddef&gt;, &lt;functional&gt;, &lt;iterator&gt;. The two files total 268 lines and can be copied out if you have access to the private repo. |
| **Minimum toolchain** | C++20 for this header (std::countr_one from &lt;bit&gt;). The repo itself builds as C++23 and lists gcc 13+, clang 17+ or MSVC 19.35+. Published numbers exist only for gcc 13.3.0. |
| **Platforms** | Portable C++. Explicit prefetch exists only on GCC/Clang (__builtin_prefetch) and is a no-op on MSVC. Benchmarked only on an x86-64 Intel Xeon (AVX2) cloud VM. The CI matrix includes macOS clang, but at HEAD that job fails to compile an unrelated xsimd benchmark, so the search tests don't run there. |
| **Thread safety** | Not documented. All three searches are noexcept pure reads of a caller-owned const array with no internal state, so concurrent searches of an unchanging array share nothing mutable. |
| **Drop-in for the baseline** | partial — lower_bound_branchless and lower_bound_prefetch return the same element as std::lower_bound (tested per key), but they take a raw pointer plus count instead of an iterator pair and return const T\*, so they work only on contiguous storage. The Eytzinger search needs a separately built array and returns a tree index, not a position. |

## Gotchas

- The win depends on how the step is spelled. `base = less(...) ? base + half : base` compiles to a branch (jle) on gcc 13 and is no faster than std::lower_bound; only the multiply-by-bool form emits cmov. If you edit, port or upgrade the compiler, check the disassembly.
- Every function is noexcept whatever Compare or T is, so a throwing comparator (or a throwing copy-assignment inside build_eytzinger) calls std::terminate.
- lower_bound_eytzinger prefetches &tree[index \* 16], which for the deeper levels points far past the end of the array. The prefetch doesn't fault, but the pointer arithmetic is out of bounds. The distance is fixed at 16 elements whatever sizeof(T) is (one 64-byte line only for 4-byte keys), and build_eytzinger doesn't cache-line-align its output. Only int was benchmarked.
- The published ns are per-query averages over the same 20,000 independent keys replayed every pass, so the CPU can overlap consecutive searches; the latency of a single dependent lookup is not measured. These rows also come from the -O2 run (2026-09-02-core) and weren't re-measured after the repo moved its benchmarks to -O3 on 2026-09-03.

## Caveats and trade-offs

Developer source is a PRIVATE repo, readable only via authenticated `gh api`, so it is capped below tier A despite full compiler/flags/CPU disclosure in results/fastest.json. include/fastcpp/algo/binary_search.hpp documents the same cmov-vs-branch finding, and the win depends on exact source spelling: `cond ? base+half : base` compiles to a branch on gcc 13 and gains nothing. Only libstdc++/gcc was tested; no libc++ or MSVC STL run. First-party benchmark, not independently reproduced. The repo labels the DRAM row 'UNSTABLE ROW': plain branchless measured 0.72x-1.49x of std::lower_bound over five runs. binary_search.hpp's own comment records the prefetch variant as 'a stable 1.6x', against 1.91x in this row, so the DRAM ratio varies from run to run. Prefetch is a loss on the L1 array (14.877 vs 11.562ns). The Eytzinger-vs-std::lower_bound 5.34x is a cross-row derived ratio. Both rows share run 2026-09-02-core and the identical 4.2M-int workload, but the bench times Eytzinger separately and does not checksum it against std::lower_bound, because it returns a tree index. Eytzinger ties branchless on the 16 KiB array (11.387 vs 11.577ns), needs a build step, and leaves the array unsorted.

Plain branchless search (no prefetch) is UNSTABLE on DRAM-sized data: across five runs it measured 0.72x-1.49x of std::lower_bound, i.e. no reliable win, because going branchless discards the free prefetch a mispredicted branch would otherwise give the wrong-path cache line; only the explicit-prefetch variant is a stable win when memory-bound. Eytzinger layout requires a build/reorder step, leaves the array unsorted (build-once/search-many only), and merely ties plain branchless on cache-resident (16 KiB) arrays. The exact C++ spelling of the branchless step decides whether gcc emits cmov or a branch (`base += size_t(cond) * half` vs a ternary) -- verified by disassembly, not portable across compilers/versions per the source comments.

## Maintenance

The repo is private (0 stars; only readable with access) and saw a single 13-commit burst on 2026-09-02..04, with the header unchanged since the first commit; the code is MIT and 268 lines to vendor, but all 21 CI runs failed — at HEAD the search tests pass in the asan+ubsan and gcc-native jobs, and the failures are in unrelated targets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** results/fastest.json rows binary_search_cached, binary_search_dram and eytzinger_layout (run 2026-09-02-core) give exact ns vs std::lower_bound with gcc 13.3.0, flags and CPU stated. The bench code (bench/bench_doing_less.cpp bench_binary_search) is in a PRIVATE repo, so this cannot be A, and there is no paper or independent suite for B. First-party numbers, so C.
- **Verifier notes:** All numbers (5.83x, 1.91x, 80.132ns, 3.96x vs 317.093ns, derived 5.34x) match results/fastest.json and the bench source. I only added the repo's own instability flags and the missing Eytzinger checksum validation to caveats, and made the workload precise (20k queries, n = 4,194,304).
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - private:developer-source
  - private:developer-source/commits/main
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/bench/bench_doing_less.cpp
  - private:developer-source/blob/main/bench/bench_harness.hpp
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/blob/main/include/fastcpp/algo/binary_search.hpp
- **Sources the enricher read:**
  - private:developer-source
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/include/fastcpp/algo/binary_search.hpp
  - private:developer-source/blob/main/include/fastcpp/core/macros.hpp
  - private:developer-source/blob/main/bench/bench_doing_less.cpp
  - private:developer-source/blob/main/bench/bench_harness.hpp
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/tests/test_containers.cpp
  - private:developer-source/blob/main/tests/test_core.cpp
  - private:developer-source/blob/main/tests/test_sort.cpp
  - private:developer-source/blob/main/tests/test_strings.cpp
  - private:developer-source/blob/main/tests/test_phf.cpp
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/.github/workflows/ci.yml
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/issues
  - private:developer-source/commits/main
  - private:developer-source/commits/main/include/fastcpp/algo/binary_search.hpp
  - private:developer-source/commit/6c81a90
  - private:developer-source/actions
  - private:developer-source/actions/runs/33828450197
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#searching`) · [data/wave1-phf/enrich/raw/private_developer_source_searching.json](../../../data/wave1-phf/enrich/raw/private_developer_source_searching.json) (enrichment confidence 0.85)

</details>
