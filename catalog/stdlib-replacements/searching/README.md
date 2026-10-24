# Searching

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::lower_bound, std::binary_search, std::find, std::search  
**7 entries:** 2 tier A · 0 tier B · 5 tier C · 0 tier D · 5 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**FastBinarySearch**](fabiocannizzo-fastbinarysearch.md) | Header-only C++ library for O(1)/vectorized insertion-point search in sorted float arrays, beating std::lower_bound scalar and SIMD-batched. | **A** | C++ | MIT | 🟡 stale |
| 2 | [**SIMD Quad search (Lemire blog benchmark)**](lemire-code-used-on-daniel-lemire-s-blog.md) | SIMD quaternary-interpolation search over sorted 16-bit arrays in 16-element blocks; beats std::binary_search on Roaring-Bitmap-style containers. | **A** | C++ | no license (study only) | 🟢 active |
| 3 | [**Software Architecture with C++ 2E: binary search…**](paper-book-software-architecture-with-cpp-2e-binary-search-vs-linear-scan.md) | Book benchmark: std::ranges::lower_bound beats std::ranges::find on a sorted vector&lt;int&gt;, O(log n) against a linear scan. | **C** | C++ | MIT | 🟢 active |
| 4 | [**fastcpp::algo::lower_bound (branchless / Eytzinger)…**](private-developer-source-searching.md) | Three header-only lower_bound variants (branchless cmov, cmov+prefetch, Eytzinger layout); 5.8x std::lower_bound in L1, 1.9x from DRAM on ints. | **C** | C++ | MIT | 🟢 active |
| 5 | [**scandum/binary_search (monobound / boundless binary search)**](scandum-binary-search.md) | C binary-search variants; monobound_bsearch() is a bsearch()-compatible drop-in \~1.4-2.35x faster than libc bsearch(). | **C** | C | Unlicense | 🟡 stale |
| 6 | [**sb_lower_bound (Fastest Branchless Binary Search)**](mh-dm-sb-lower-bound.md) | Branchless drop-in-shaped replacement for std::lower_bound that relies on clang emitting cmov instead of a branch. | **C** | C++ | MIT | 🔴 abandoned |
| 7 | [**simdsearch (Needle-Hammer)**](lemire-simdsearch.md) | Header-only SIMD substring search with a linear-time worst-case fallback; \~30x libc memmem on Apple M-series. | **C** | C++ | no license (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
