# ankerl::svector (martinus/svector)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++17 small vector packing 7 inline bytes into an 8-byte object; avoids std::vector's heap allocation for tiny sequences.

| | |
|---|---|
| **Beats** | std::vector |
| **Claimed result** | Build 7 inline elements: 1.26 ns per element vs std::vector 3.85 ns (about 3.1x, derived from page data); insert at front of std::string vector 1320.2 ns vs 1415.2 ns (about 7%); shuffle plus sort of 1000 std::string 31305 ns vs 35435 ns (12%, the only gap the README says exceeds run-to-run noise); emplace_back std::string 22.64 ns vs 23.52 ns (within noise). Slower than std::vector at push_back uint8_t (0.66 vs 0.30 ns, 2.2x), random operator[] (0.67 vs 0.57 ns) and swap of 7 inline uint64_t (2.15 vs 1.66 ns). Object size 8 bytes with 7 inline uint8_t vs 24 bytes with none for std::vector. |
| **Workload** | Small-vector micro-benchmarks with nanobench, one container per process, median of 9 processes: building 7 inline elements, push_back, emplace_back and insert of std::string, random access, swap, shuffle and sort of 1000 std::string; also object size (sizeof 8 bytes holding 7 inline uint8_t). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, pinned to one core with taskset |
| **Compiler and flags** | gcc 16.1.1, -std=c++17 -O3 -DNDEBUG, boost 1.90.0, abseil 20260107.1; meson release build |
| **Adoption** | 122 stars, 14 forks |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/martinus/svector) · [benchmark](https://github.com/martinus/svector) |

## Verdict

Measured with nanobench in test/bench/solo.cpp, one container per process and the median of 9 processes, gcc 16.1.1 -std=c++17 -O3 -DNDEBUG with libstdc++ on an AMD Ryzen 9 7950X pinned with taskset: building 7 inline uint8_t costs 1.26 ns per element versus 3.85 ns for an unreserved std::vector (about 3.1x, derived from page data), with smaller or noise-level gains on std::string emplace, front insertion and shuffle+sort, and losses on push_back (2.2x), random operator[] (about 18%) and swap.

## Use it when

- Many short-lived or numerous sequences that usually hold 1-7 small elements (adjacency lists, token lists, per-node children) where std::vector's first allocation dominates.
- Memory-bound structures holding millions of tiny vectors of 1-byte elements: svector&lt;uint8_t, 7&gt; is 8 bytes versus 24 for an empty std::vector and 24 for absl::InlinedVector.
- Code that needs a small vector with a custom or std::pmr allocator (added in August 2026, present from v1.3.0) and wants std::vector semantics for propagate_on_container_\* traits.
- Element-heavy workloads such as emplace_back or front insertion of std::string, where the README measures it level with or slightly ahead of std::vector.

## Skip it when

- Hot loops of push_back or operator[] on trivially copyable elements: the mode check costs 15.3 vs 8.5 instructions per push_back (2.2x slower) and 16.8 vs 10.0 per random subscript (about 18% slower).
- When absl::InlinedVector is acceptable: it fills inline storage 2.6x faster (0.48 vs 1.26 ns per element) and appends faster (0.51 vs 0.66 ns).
- Containers that are swapped or moved often while inline: swap is element-wise (2.15 ns for 7 uint64_t, 35.6 ns for 7 short std::string) where std::vector is always three pointer exchanges (1.66 ns).
- Big-endian targets, allocators with fancy pointers, over-aligned element types (static_assert caps alignment at __STDCPP_DEFAULT_NEW_ALIGNMENT__), or more than 127 inline elements: all rejected at compile time.
- Projects pinned to v1.0.x (the only versions on Conan Center): see the data-corruption bugs fixed in v1.1.0 below.

## How it is fast

Small-buffer optimization (SBO/SVO) with a tagged pointer: bit 0 of the first byte says direct (inline) or indirect (heap) mode, in direct mode the other 7 bits are the size, and in indirect mode the first word is a pointer to a heap block holding size, capacity and elements. Staying inline skips malloc/free entirely, which is where the measured gains come from. Trivially copyable elements are relocated with memcpy, small trivially copyable inline buffers are moved and swapped by copying the whole buffer, and the capacity doubles starting from the inline capacity rather than from 1.

## Compared with alternatives

Among the catalogued sequence containers it is the only small-buffer vector: pick it over fast_vector, eastl::vector or veque when most vectors stay tiny and object size or allocation count matters, and pick those (or std::vector) when vectors are large and appends or indexing dominate, where svector's mode check makes it slower.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (boost and abseil only for the optional comparison benchmarks) |
| **Minimum toolchain** | C++17; CI builds C++17 and C++20 on Linux, macOS and Windows (MSVC) and C++23 on Linux, plus a 32-bit build |
| **Platforms** | little-endian only (static_assert where __BYTE_ORDER__ is defined); 32-bit and 64-bit; CI on Linux, macOS and Windows |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: same API plus extras, but needs the inline capacity template argument, iterators are T\*, move is noexcept only when T's move is, no fancy-pointer allocators |

## Gotchas

- The headline 3.1x 'build 7 inline' win (1.26 vs 3.85 ns per element) is against a std::vector that is never reserved: test/bench/solo.cpp's build_inline starts from an empty std::vector and emplaces 7 elements, so libstdc++ reallocates at capacities 1, 2, 4 and 8 (4 allocations and 4 frees per vector, consistent with the README's 61.6 instructions per element). A reserve(7) baseline, which would do one allocation, is not measured, so the gap against carefully written std::vector code is smaller than shown.
- Versions before v1.1.0 (2026-07-28) had serious correctness bugs: push_back(v[0]) or assign(n, v[0]) could segfault on reallocation (#50, open from 2023-04 to 2026-07), erase(it, it) and insert of an empty range silently blanked every element from that position onwards (#65, #66), a throwing element constructor caused a double destroy in insert() (#68) and leaks in resize() and growth (#70, #74), and move was unconditionally noexcept (#63). Conan Center's recipe still lists only 1.0.2 and 1.0.3; vendor v1.4.0 or later instead.
- The '1 byte overhead' figure applies to 1-byte elements: inline data starts at offset alignof(T), so for 8-byte-aligned T (uint64_t, std::string) the direct-mode overhead is 8 bytes, and svector&lt;std::string, 7&gt; is 232 bytes.
- Two of the README's bolded wins over std::vector are inside the run-to-run spread it states (about 7% for std::string workloads): emplace_back std::string (22.64 vs 23.52 ns, 3.9%) and insert at front std::string (1320.2 vs 1415.2 ns, 6.7%); the emplace_back gap also reflects svector's growth starting at capacity 7 (11 reallocations for 10000 elements versus 15 for std::vector). The 12% shuffle+sort lead runs std::sort over raw contiguous storage in every container, so it is not explained by the container design, which the README itself says stops mattering once the work is on the elements.

## Known shortcomings

- Own harness (test/bench/solo.cpp, gcc 16.1.1 -O3, Ryzen 9 7950X): wins only inline-storage and string work (build-7-inline 3.1x, shuffle+sort 12%); the two bolded wins (emplace_back string 3.9%, insert-front string 6.7%) sit inside the stated \~7% noise, and it is slower than std::vector on push_back (2.2x), subscript (18%) and swap.
- Enricher: the headline 3.1x build-7-inline win is against a std::vector that is never reserved (test/bench/solo.cpp starts it empty, 4 mallocs per vector; a reserve(7) baseline is not measured), and the 12% shuffle+sort lead runs std::sort on raw storage. v1.0.x had data-corruption bugs fixed in v1.1.0 (2026-07-28): push_back(v[0]) segfault #50, erase and empty-range insert blanking elements #65/#66, double destroy #68; Conan Center still lists only 1.0.2 and 1.0.3. The 1-byte overhead holds only for 1-byte T.

## Caveats and trade-offs

The win over std::vector is concentrated in workloads that stay inside the inline storage (std::vector must allocate) and in std::string element work; on pure bookkeeping with trivially copyable elements svector loses to std::vector (push_back 2.2x slower, subscript about 18% slower, swap slower) and loses to absl::InlinedVector at filling inline storage (0.48 ns per element). Several differences are inside the stated run-to-run spread (under 3%, about 6-7% for std::string workloads): the bolded emplace_back std::string win (22.64 vs 23.52 ns, 3.9%) and the insert-at-front std::string win (1320.2 vs 1415.2 ns, 6.7%) are within or at the edge of that spread even though the README bolds them; only build-7-inline (3.1x) and shuffle+sort (12%) clearly exceed it. The last commit date is a dependabot bump; the last functional commit is 2026-08-05. libstdc++ is implied by gcc (test/bench/solo.cpp comments refer to libstdc++ string swapping), not stated as a version. Young container maintained by one person. [retier] Own harness (test/bench/solo.cpp, gcc 16.1.1 -O3, Ryzen 9 7950X): wins only inline-storage and string work. The headline 3.1x build-7-inline row is against a std::vector that is never reserved (it starts empty and reallocates at 1/2/4/8, 4 mallocs per vector; no reserve(7) baseline is measured), and the 12% shuffle+sort lead runs std::sort on raw storage, so the container design does not explain it; the two bolded wins (emplace_back string 3.9%, insert-front string 6.7%) sit inside the stated \~7% noise. Slower than std::vector on push_back (2.2x), subscript (18%) and swap. v1.0.x had data-corruption bugs fixed in v1.1.0 (2026-07-28): push_back(v[0]) segfault #50, erase(it,it) and empty-range insert blanking elements #65/#66, double destroy #68; Conan Center still lists only 1.0.2 and 1.0.3. The 1-byte overhead holds only for 1-byte T (8 bytes when alignof(T) is 8).

Tagged-pointer design: one byte of overhead, 7 inline bytes in an 8-byte object, at most 127 inline elements, little-endian targets only, no fancy-pointer allocators, move is noexcept only when the element move is, insert of several elements gives only the basic guarantee. Every operation branches on direct or indirect mode, which costs instructions on bookkeeping-only operations. Swap is element-wise for inline storage, not three pointer exchanges.

## Maintenance

Active single-maintainer project (v1.4.0 tagged 2026-08-05, last commit 2026-09-02 a dependabot bump, 0 open issues) with a large July-August 2026 rework largely co-authored with an AI assistant that added allocator support, C++23 range members, CMake/meson install and fuzzing in CI; MIT and a single header, easy to vendor at a pinned version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README benchmark tables compare directly against std::vector with public harness code (test/bench/solo.cpp driven by scripts/bench/render_charts.py, one container per process, median of 9), and state gcc 16.1.1, -std=c++17 -O3 -DNDEBUG, boost 1.90.0, abseil 20260107.1 and an AMD Ryzen 9 7950X pinned with taskset.
- **Verifier notes:** All quoted numbers match the README tables and the harness (test/bench/solo.cpp) looks sound: every workload keeps its result alive with doNotOptimizeAway and the build_inline workload sums the elements to stop the optimizer deleting inline vectors. Shortcomings: wins only in inline-storage and std::string workloads, slower than std::vector on push_back (2.2x), subscript (18%) and swap; two of the bolded wins are within the stated noise. Metadata checked: MIT, 122 stars, 14 forks, last commit 2026-09-02 (dependabot), last functional commit 2026-08-05, not archived, not a fork.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party public harness (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/README.md>
  - <https://github.com/martinus/svector>
  - <https://github.com/martinus/svector/commits>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/test/bench/solo.cpp>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/scripts/bench/render_charts.py>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/meson.build>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/README.md>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/include/ankerl/svector.h>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/test/bench/solo.cpp>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/scripts/bench/render_charts.py>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/meson.build>
  - <https://raw.githubusercontent.com/martinus/svector/HEAD/LICENSE>
  - <https://github.com/martinus/svector>
  - <https://github.com/martinus/svector/commits>
  - <https://github.com/martinus/svector/tags>
  - <https://github.com/martinus/svector/issues>
  - <https://github.com/martinus/svector/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/martinus/svector/issues/50>
  - <https://github.com/martinus/svector/issues/66>
  - <https://github.com/martinus/svector/issues/74>
  - <https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/svector/config.yml>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/svector/vcpkg.json>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/martinus/svector`) · [data/wave1/enrich/raw/github_com_martinus_svector.json](../../../data/wave1/enrich/raw/github_com_martinus_svector.json) (enrichment confidence 0.85)

</details>
