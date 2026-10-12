# fastcpp::small_vector (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++ vector with N inline slots (default 8). It skips std::vector's heap allocation while the vector stays small.

| | |
|---|---|
| **Beats** | std::vector |
| **Claimed result** | 21.34x faster (1.856ns vs 39.6ns per vector, gcc 13.3.0, -O2 -march=native, min of 7 samples) |
| **Workload** | 50,000 short-lived vectors of 4 int elements each, built and destroyed, comparing fastcpp::small_vector&lt;int,8&gt; (inline storage) against std::vector&lt;int&gt; (always heap-allocates). |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores; Ubuntu 24.04, Linux 6.18 (shared cloud VM) |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo), commit dfa74f2 (run id '2026-09-02-core') |
| **Adoption** | 0 stars (private repo) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](private:developer-source) · [benchmark](private:developer-source/blob/main/results/fastest.json) |

## Verdict

In the repo's own bench_doing_less, building, summing and destroying 50,000 vectors of 4 ints cost 1.856 ns per vector with small_vector&lt;int, 8&gt; and 39.6 ns with a std::vector&lt;int&gt; that was not reserve()d (libstdc++, 21.3x). The build was gcc 13.3.0 at -O2 -march=native on a shared 4-core Xeon @ 2.10GHz VM, minimum of 7 samples. Under 1-&gt;2-&gt;4 growth the baseline pays three malloc/free pairs and two reallocations per vector, so the figure is no allocation against un-reserved growth, not one allocation against none. The row (run 2026-09-02-core, commit dfa74f2) was recorded before the repo switched its benchmarks to -O3 and has not been re-measured since.

## Use it when

- Hot loops that create and destroy many short-lived vectors whose size is usually at or below a known small bound (e.g. a few ints or pointers per item), where malloc/free is most of the cost
- Function-local temporaries on the stack, where the extra N\*sizeof(T) bytes are not kept and the elements share cache lines with the rest of the frame
- Trivially copyable element types (ints, pointers, small PODs): destruction does no per-element work and an inline copy or move is a short element loop
- Call sites that only append, pop, resize, index and iterate, and never insert or erase in the middle
- When you want tests or debug asserts to prove the hot path never allocates, via is_inline()

## Skip it when

- Vectors that often grow past N. After the first overflow it is an ordinary doubling heap vector that still carries the unused inline buffer. No row in results/fastest.json measures the overflow or crossover case
- Vectors stored in bulk (array elements, hash-map values, long-lived struct members). From the member layout, small_vector&lt;int, 8&gt; is 56 bytes against std::vector's 24, and an empty one costs the same
- Code that moves or swaps vectors a lot. Moving an inline vector moves each element instead of stealing a pointer, and without a swap member std::swap does three O(size) moves
- Code that needs the rest of the std::vector API (insert, erase, assign, comparisons, resize(n, value), (n, value) or iterator-range constructors, custom allocators) or exception safety while growing
- Teams that need a reviewed, supported dependency. The code is in a private single-author repo. The header has one commit and 4 unit tests (inline-until-overflow, std::string elements, move of inline storage, resize/pop), and the tracker has no issues

## How it is fast

It uses the small-buffer optimization (inline storage). An alignas(T) byte array of N\*sizeof(T) is a member, and data_ points into it until the first overflow. Construction, pushes below N and destruction make no allocator calls, and the elements sit in the object's own cache lines, which are usually on the stack. The push_back fast path is one always-inlined size==capacity compare marked unlikely, followed by a placement-new. Growth is in a separate noinline grow() that doubles the capacity. For trivially destructible T, `if constexpr` skips the destructor loop.

## Compared with alternatives

No siblings catalogued yet.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library for this header, which includes only fastcpp/core/bits.hpp and fastcpp/core/macros.hpp. Copy those three files. add_subdirectory plus fastcpp::fastcpp is much heavier, because the INTERFACE target links all ten vendored libraries (fmt, phmap, xsimd, zpp_bits, the two queues, simdjson, yyjson, CRoaring, pocketfft) |
| **Minimum toolchain** | C++20 for this header (bits.hpp uses &lt;bit&gt;/std::countl_zero and std::is_constant_evaluated). The repo's CMake requires C++23, and its README lists gcc 13+, clang 17+ or MSVC 19.35+. The benchmark was built with gcc 13.3 at -std=c++20 |
| **Platforms** | any: portable C++ with no intrinsics in this header. CI builds and tests with gcc and clang on Linux and clang on macOS, plus ASan+UBSan on Linux. The macros have MSVC branches, but MSVC is not in CI |
| **Thread safety** | not documented; the class has no internal synchronization |
| **Drop-in for the baseline** | partial — the type is small_vector&lt;T, N&gt; rather than std::vector&lt;T&gt;, and only a subset of the API exists (push_back/emplace_back/pop_back/clear/resize(n)/reserve/[]/at/front/back/data/begin/end/size/capacity/empty). There is no insert, erase, emplace(pos), assign, swap, shrink_to_fit, ==/&lt;, cbegin or rbegin, const at(), count/range constructors or Allocator parameter |

## Gotchas

- Pushing an element of the same vector when it is full is unsafe. emplace_back calls grow() before building the new element, and grow() moves the old elements out, destroys them and frees the old heap buffer. So v.push_back(v[0]) at size()==capacity() reads a moved-from or freed object, a case std::vector handles. This comes from reading grow()/emplace_back; no test covers it.
- Moving an inline small_vector invalidates pointers, references and iterators to its elements, because they are rebuilt in the destination; a std::vector move keeps element addresses. The moved-from vector is cleared.
- grow() gives no exception safety. If an element's copy or move throws partway through, the new buffer leaks and the already-destroyed source elements stay counted in size(), so the destructor destroys them a second time.
- Once it spills to the heap it never goes back inline. clear(), resize() and copy-assignment keep the heap buffer and there is no shrink_to_fit; only move-assigning into it frees the buffer.

## Caveats and trade-offs

Repo private:developer-source is PRIVATE and readable only via the authenticated gh CLI, so it is capped below tier A despite full compiler/flags/CPU disclosure. The 4-element workload is close to the best case for inline storage (well under the 8-slot inline capacity), and the results file has no row testing the crossover point where elements overflow to the heap. The baseline is not reserve()d: bench_small_vectors push_backs 4 ints into an empty std::vector&lt;int&gt;, which under libstdc++'s 1-&gt;2-&gt;4 growth costs 3 heap allocations and 2 relocations per vector, where small_vector does none. So the 21.34x measures malloc avoidance plus regrowth, not one allocation versus none; a reserve(4) or std::array/pmr baseline was not measured. Timings are ns per vector (ops_per_iteration = 50,000), min of 7 samples, on a shared cloud VM where absolute ns are not stable across runs.

sizeof(small_vector&lt;T,N&gt;) is N\*sizeof(T) larger than std::vector; moving a small_vector is O(size) rather than O(1) while it is still inline; overflow past the inline capacity (8 elements by default) falls back to a normal heap allocation, at which point the advantage disappears.

## Maintenance

The repo is PRIVATE (private:developer-source, 0 stars, readable only with access). It was last pushed 2026-09-04, but this header has had one commit since it was added on 2026-09-02. It is MIT-licensed and small (227 lines plus two helper headers), so copying it into your tree is the practical way to use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The results/fastest.json row small_vector (run 2026-09-02-core) gives 1.856 vs 39.6 ns (21.34x) against std::vector&lt;int&gt; with gcc 13.3.0, flags and CPU stated. The bench code (bench/bench_doing_less.cpp bench_small_vectors) is in a PRIVATE repo, so this cannot be A, and there is no paper or independent suite for B. First-party, so C.
- **Verifier notes:** The 1.856 vs 39.6ns (21.34x) figure matches results/fastest.json and bench/bench_doing_less.cpp exactly. I added the un-reserved std::vector growth caveat (3 mallocs per baseline vector) and the run commit to compiler_and_flags; nothing else needed changing.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <private:developer-source>
  - <private:developer-source/commits/main>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/blob/main/include/fastcpp/container/small_vector.hpp>
- **Sources the enricher read:**
  - <private:developer-source>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/blob/main/include/fastcpp/container/small_vector.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/bits.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/macros.hpp>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/tests/test_containers.cpp>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/.github/workflows/ci.yml>
  - <private:developer-source/blob/main/include/fastcpp/io/format.hpp>
  - <private:developer-source/blob/main/include/fastcpp/container/flat_hash_map.hpp>
  - <private:developer-source/blob/main/include/fastcpp/memory/arena.hpp>
  - <private:developer-source/issues>
  - <private:developer-source/pulls>
  - <private:developer-source/commits/main>
  - <private:developer-source/commits/main/include/fastcpp/container/small_vector.hpp>
  - <private:developer-source/commit/dfa74f2>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#small-buffer-and-strings`) · [data/wave1-phf/enrich/raw/private_developer_source_small_buffer_and_strings.json](../../../data/wave1-phf/enrich/raw/private_developer_source_small_buffer_and_strings.json) (enrichment confidence 0.85)

</details>
