# fastcpp::arena (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only bump/arena allocator for same-lifetime objects; 5.4x faster than glibc new/delete when a whole batch is freed at once.

| | |
|---|---|
| **Beats** | new/delete |
| **Claimed result** | 5.41x on bulk allocate+fill+free of 200k 48-byte nodes (3.451ns vs 18.682ns new/delete, results/fastest.json) / 5.4x in docs/allocators.md's own table (3.45ns vs 18.68ns); 4.75x on post-allocation list-walk locality (2.742ns vs 13.028ns for new fragmented by interleaved allocations). Cannot serve the churn workload (unrelated alloc/free order) at all; there the only lever is swapping the system allocator via LD_PRELOAD=jemalloc, which gives 2.71x over glibc new/delete and is not attributable to the arena. |
| **Workload** | Three microbenchmarks vs glibc new/delete on 200k 48-byte nodes: (A) bulk lifetime - allocate, fill, and free all nodes at once; (B) walk the list after allocation, measuring layout/locality only, no allocator calls; (C) churn - 200k allocate/free pairs in unrelated order with a bounded live set, a workload an arena structurally cannot serve. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz, 4 cores (SSE4.2, AVX2, BMI2, AVX-512F/VL, PCLMULQDQ); Ubuntu 24.04, Linux 6.18 (shared cloud VM) |
| **Compiler and flags** | gcc 13.3.0, -O2 -march=native (docs/allocators.md); results/fastest.json run 2026-09-03-third-party used -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo) |
| **Adoption** | 0 stars (private repo) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](private:developer-source) · [benchmark](private:developer-source/blob/main/docs/allocators.md) |

## Verdict

On a shared 4-core Intel Xeon 2.10GHz VM (Ubuntu 24.04, gcc 13.3, -O2 -march=native, libstdc++ and glibc malloc), allocating, filling and freeing 200k 48-byte nodes took 3.45 ns/node with the arena vs 18.68 ns with new/delete (5.41x), and walking the resulting list afterwards took 2.74 vs 13.03 ns (4.75x). Under LD_PRELOAD jemalloc, new/delete only improves to 12.63 ns on the bulk case, but the walk gap shrinks to about 1.45x. These are first-party minimum-of-samples numbers: the recorded run commit predates bench_allocator.cpp, and HEAD now builds benchmarks at -O3.

## Use it when

- Build-then-drop batches of many small, trivially destructible objects that die together: AST/IR nodes for one file, per-frame renderer scratch, one parse or one request. Measured: 200k 48-byte nodes allocated, filled and freed at 5.41x the speed of glibc new/delete.
- Repeated cycles of the same shape (per frame, per request): reset() keeps every block, so steady-state rounds make no further operator new calls. A unit test checks that bytes_reserved() and block_count() stay constant across reset().
- Pointer-linked structures (lists, trees, graphs) that are walked long after they are built, on glibc malloc: contiguous placement made a post-build list walk 4.75x faster than a heap fragmented by interleaved allocations.
- Interning strings or byte ranges that live as long as the batch, via copy().
- Backing a std::vector or another std container in code you do not own, via arena_allocator&lt;T&gt;, when its contents can be dropped with the arena and its final size can be reserved up front.

## Skip it when

- Objects freed in an order unrelated to their creation (caches, pools, graphs with deletions): no single object can be freed, so memory only grows until reset(). For this churn case the repo's own measurement says to swap malloc instead, e.g. LD_PRELOAD jemalloc at 2.71x over glibc new/delete.
- Types with non-trivial destructors (std::string, containers, RAII handles): create&lt;T&gt; and create_array&lt;T&gt; reject them with a static_assert because the arena never runs destructors.
- When std::pmr::monotonic_buffer_resource is acceptable. It has been in the standard since C++17 and was only about 25% slower (4.32 vs 3.45 ns/node) on the same bulk workload. The repo's own doc says to reach for a bump pointer, not a dependency.
- Allocating from one arena on several threads: the class has no locking or atomics, and thread safety is not documented.
- When allocation is a small share of runtime: the doc's own Amdahl table puts the saving from a 5x arena at 0.8% of runtime when allocation is 1% of it. It is also an immature component: arena.hpp is from a single 2026-09-02 commit (author 'Claude'), has 5 unit tests, and sits in a private repo with 0 stars and no issue history.

## How it is fast

It is bump-pointer (region) allocation. The force-inlined fast path aligns the cursor, checks it against the block end and moves it forward. There is no size-class lookup, per-object header or free list, and running out of a block goes to a separate noinline slow path. Freeing n objects is one O(1) cursor reset instead of n delete calls, and blocks kept across reset() are reused without calling operator new again. Consecutive allocations sit next to each other in order, which is why a linked list built in the arena walked 4.75x faster than one that glibc malloc spread out between other allocations.

## Compared with alternatives

No siblings catalogued yet. Against the standard library's own arena, std::pmr::monotonic_buffer_resource, it measured 3.45 vs 4.32 ns/node (about 1.25x) in the same suite, so pick it only when that margin matters more than using a standard type.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the standard library and the repo's own include/fastcpp/core/bits.hpp and core/macros.hpp (3 headers, \~550 lines). The CMake target fastcpp::fastcpp, however, links all ten vendored third-party libraries (simdjson, yyjson and CRoaring are compiled static libs, the last two in C) and requests cxx_std_23, so copy the three headers rather than using add_subdirectory if you only want the arena. |
| **Minimum toolchain** | C++20 (std::span, &lt;bit&gt;, std::is_constant_evaluated). The arena was benchmarked with gcc 13.3 at -std=c++20. The repo as a whole now targets C++23 and lists gcc 13+, clang 17+ or MSVC 19.35+, with CMake 3.20+. |
| **Platforms** | any. The arena has no ISA-specific code. CI builds on Linux (gcc, clang) and macOS (clang), and core/macros.hpp has MSVC branches, but MSVC is not in CI. Performance numbers exist only for x86-64 Linux. |
| **Thread safety** | not documented; the class holds plain cursor/end pointers with no synchronization, so use one arena per thread |
| **Drop-in for the baseline** | partial — it does not replace new/delete. You call a.create&lt;T&gt;(...) and never delete, and objects must be trivially destructible. arena_allocator&lt;T&gt; is a std::allocator-compatible adapter for std containers, but its deallocate is a no-op. |

## Gotchas

- Lifetime is manual and unchecked: reset(), release() or destroying the arena while a pointer or an arena_allocator-backed container still refers to its memory leaves dangling pointers, and there is no diagnostic. arena_allocator also skips the trivially-destructible check that create&lt;T&gt; enforces.
- arena_allocator::deallocate does nothing, so a std::vector grown with push_back leaves every outgrown buffer in the arena until reset(). Call reserve() first.
- Waste in the slow path: a request larger than the block size gets its own block of next_pow2(bytes + alignment), so allocate(1 MiB) reserves 2 MiB. Moving to a new block abandons the tail of the current one. After reset(), a request too big for the next kept block walks past and strands each such block until the next reset().
- alignment must be a power of two, and nothing checks it (align_up is mask arithmetic). create_array&lt;T&gt; returns uninitialized storage. allocate() is not noexcept: a new block comes from aligned ::operator new, which can throw std::bad_alloc.

## Caveats and trade-offs

Repo private:developer-source is PRIVATE and readable only via authenticated gh CLI, so despite full compiler/flags/CPU/commit disclosure this is capped below tier A per orchestrator instruction. Much of the locality win (suite B) is a glibc fragmentation artifact rather than an arena advantage: under LD_PRELOAD=jemalloc the same comparison shrinks from 4.75x to about 1.45x (3.965ns). The standard library's own arena, std::pmr::monotonic_buffer_resource (libstdc++), is within 25% of fastcpp::arena on the bulk workload (4.318ns vs 3.451ns), so most of the 5.41x is available from &lt;memory_resource&gt; without this library. Numbers are from a shared cloud VM; the results file's own caveat says absolute nanoseconds are not a reproducible spec, only within-row ratios are meaningful. The allocator rows are tagged run 2026-09-03-third-party, whose recorded commit (0711657) predates bench/bench_allocator.cpp (first committed in 9f5650f); that run's metadata also says bench_allocator used 3 samples, but the source uses the harness default of 7 (docs/allocators.md also says 7). Since commit 6c81a90 (2026-09-03) the benchmarks are forced to -O3 (fastcpp_bench_opt in CMakeLists.txt), so a rebuild at HEAD does not reproduce the -O2 flags these numbers were taken with. docs/allocators.md separately argues, from the same data, that no allocator library should be vendored at all.

Individual objects can never be freed, only the whole arena at once (cursor reset), so it only suits objects that share one lifetime, e.g. one AST, one render frame, one parse. create&lt;T&gt; is static_assert'd to trivially-destructible types only because the arena never runs destructors. Cannot serve churn workloads (unrelated allocate/free order) at all. std::pmr::monotonic_buffer_resource, in the standard library since C++17, gets within about 25% of the arena on the bulk-lifetime case (4.32ns vs 3.45ns).

## Maintenance

The repo (private:developer-source) is PRIVATE, readable only with granted access, and has 0 stars. arena.hpp has not changed since its single 2026-09-02 commit, and the repo was last pushed 2026-09-04. It is MIT-licensed and small enough to copy: 247 lines plus two core headers. CI at HEAD is red for unrelated reasons (an xsimd bench build and a UBSan hit in string/parse.hpp), but test_containers, which holds the arena tests, passes under ASan+UBSan.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/allocators.md and results/fastest.json (rows allocator_bulk_lifetime, allocator_locality, allocator_churn) compare fastcpp::arena against glibc new/delete and the std::pmr resources, and state gcc 13.3.0, flags and the Xeon CPU. The code (bench/bench_allocator.cpp) is in a PRIVATE repo, so it is not public and cannot be A. There is no paper or independent suite for B, so these are first-party numbers: C.
- **Verifier notes:** Every number checks out. docs/allocators.md has 3.45 vs 18.68 (5.4x), 2.74 vs 13.03 (the page says 4.8x) and 11.74 vs 4.33 (2.7x); results/fastest.json has 3.451/18.682 (5.41x), 2.742/13.028 (4.75x), 3.965 under jemalloc and 11.738/4.33 (2.71x). An older, independent row (arena_allocator, bench_doing_less.cpp, run 2026-09-02-core) corroborates the result: 3.76 vs 17.777ns (4.73x) on a 20k-node list. I added libstdc++ to baseline_stdlib (gcc 13.3 on Ubuntu, new/delete and std::pmr), plus the std::pmr near-parity, the run provenance mismatch and the -O3 drift to caveats. MIT, last commit 2026-09-04, 0 stars, private: all confirmed.
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <private:developer-source>
  - <private:developer-source/commits/main>
  - <private:developer-source/blob/main/docs/allocators.md>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_allocator.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/include/fastcpp/memory/arena.hpp>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/commits/main/bench/bench_allocator.cpp>
  - <private:developer-source/commits/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <private:developer-source>
  - <private:developer-source/tree/main>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/docs/allocators.md>
  - <private:developer-source/blob/main/include/fastcpp/memory/arena.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/macros.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/bits.hpp>
  - <private:developer-source/blob/main/bench/bench_allocator.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/CMakeLists.txt>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/tests/test_containers.cpp>
  - <private:developer-source/blob/main/tests/test_core.cpp>
  - <private:developer-source/blob/main/tests/test_strings.cpp>
  - <private:developer-source/blob/main/tests/test_sort.cpp>
  - <private:developer-source/blob/main/tests/test_phf.cpp>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/blob/main/.github/workflows/ci.yml>
  - <private:developer-source/blob/main/third_party/simdjson/CMakeLists.txt>
  - <private:developer-source/blob/main/third_party/yyjson/CMakeLists.txt>
  - <private:developer-source/blob/main/third_party/croaring/CMakeLists.txt>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/commits/main>
  - <private:developer-source/commits/main/include/fastcpp/memory/arena.hpp>
  - <private:developer-source/commits/main/bench/bench_allocator.cpp>
  - <private:developer-source/issues?q=is%3Aissue>
  - <private:developer-source/pulls?q=is%3Apr>
  - <private:developer-source/actions>
  - <private:developer-source/actions/runs/33828450197>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#allocators`) · [data/wave1-phf/enrich/raw/private_developer_source_allocators.json](../../../data/wave1-phf/enrich/raw/private_developer_source_allocators.json) (enrichment confidence 0.88)

</details>
