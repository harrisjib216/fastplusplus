# Data Structures and Algorithms with the C++ STL: std::vector reserve() preallocation

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book sample timing std::vector&lt;int&gt;::reserve(n) before 100,000 push_back calls against the same loop without reserve.

| | |
|---|---|
| **Beats** | std::vector&lt;int&gt; filled by push_back without reserve() |
| **Claimed result** | Book sample output (relayed via the seed lead from the book, not shown on any repo page I opened): 0.01195 s without reserve against 0.003685 s with reserve; the book says reserve was more than 3x faster. About 3.2x (derived from the relayed numbers). |
| **Workload** | 100,000 push_back calls of an int into a std::vector&lt;int&gt;, timed once with std::chrono::high_resolution_clock, first on a fresh vector and then on a fresh vector after reserve(100000). |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the book run. The repo root CMakeLists.txt sets CMAKE_CXX_STANDARD 23, offers Debug and Release configurations and defaults CMAKE_BUILD_TYPE to Debug when none is given; it adds only -Wall -fPIC for GCC, AppleClang and non-Windows Clang (warning suppressions plus -Xclang -std=c++20 for Clang on Windows; /wd4251 /MP /D_SCL_SECURE_NO_WARNINGS /permissive- for MSVC). No optimisation flag is set in the file, so a default build is unoptimised unless Release is chosen. |
| **Adoption** | 63 stars; Packt companion repository of the book Data Structures and Algorithms with the C++ STL (2024) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL) · [benchmark](https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/blob/main/chapter03/03_reserve.cpp) |

## Verdict

The book reports one run of chapter03/03_reserve.cpp: 0.01195 s for 100,000 push_back calls into a std::vector&lt;int&gt; without reserve against 0.003685 s after reserve(100000), about 3.2x (derived from the relayed numbers). Compiler, standard library, flags and CPU are not stated, the repo holds no result files and its CMake defaults to an unoptimised Debug build; the numbers come from the book via the seed lead and appear on no repo page.

## Use it when

- Filling a vector whose final size is known or cheaply bounded before the loop: transforming another container, decoding a record count read from a header, back_inserter output of known length.
- Hot paths that build many medium or large vectors, where the reallocation chain (allocate, relocate all elements, free) shows up in a profile.
- Element types that are expensive to move or copy, since every reallocation relocates everything stored so far.
- Code that keeps pointers, references or iterators into the vector while filling it: after reserve(n), push_back does not reallocate until size exceeds n.
- Latency-sensitive loops where one mid-loop spike (a large allocation plus a copy of all existing elements) is unacceptable.

## Skip it when

- The final count is unknown and the guess may be far too large: the excess capacity is held until destruction or shrink_to_fit, which is only a request (the repo's 04_shrinktofit.cpp demonstrates it).
- Repeated small reserve calls in a loop, such as reserve(size() + 1): common implementations allocate exactly the requested capacity, which defeats geometric growth and can make n inserts quadratic.
- A handful of elements: the single heap allocation still dominates, and a small-buffer vector that stores elements inline avoids the heap altogether.
- Expecting the book's 3.2x in production: it comes from one run of a build that was most likely unoptimised; with optimisation the growth cost is a few bulk copies of the data and the gain can be smaller (not measured here).

## How it is fast

Without reserve, std::vector grows geometrically: each push_back that exceeds capacity allocates a larger buffer, relocates every element already stored and frees the old buffer, so 100,000 inserts pass through a chain of reallocations (about 17 if capacity doubles; the growth factor is implementation-defined). reserve(n) makes one allocation up front, so every push_back in the loop takes the in-capacity path: a capacity check, a store and a size increment. The technique is plain preallocation; nothing else is involved.

## Compared with alternatives

Use reserve first whenever you already have a std::vector and know the count: it costs one line and no dependency. The Qt 6 Cookbook raw-array sibling beats a vector filled without reserve, so apply reserve before concluding a raw array is needed; fast_vector still reports about 2x over std::vector when both reserve (12,991 ns vs 6,416 ns), and ankerl::svector or sfl::small_vector avoid the heap for small inline counts, so pick those when growth is not the bottleneck.

## Integration

| | |
|---|---|
| **Form** | source-drop (one std::vector member call; nothing to install) |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | Any C++ standard library (std::vector::reserve is part of every standard); the sample uses a digit separator (100'000, C++14) and the repo's CMake sets CMAKE_CXX_STANDARD 23 |
| **Platforms** | any |
| **Thread safety** | Same as std::vector: reserve and push_back modify the container and need external synchronisation; the sample does not discuss threads |
| **Drop-in for the baseline** | partial — the same std::vector type and API with one added reserve(n) call; you need n, or an upper bound, before filling |

## Gotchas

- reserve changes capacity, not size: elements must still be added with push_back or emplace_back, and indexing with operator[] up to n after reserve(n) is undefined behaviour; use resize or the count constructor when you want n elements in place.
- Harness asymmetry: the reserve(100000) allocation sits before start2, so the with-reserve time excludes its one allocation while the no-reserve time includes all of its growth; the no-reserve loop also always runs first in a fresh process (the order is never swapped), so any first-use costs land on the baseline side. One run, no repetitions, no warm-up.
- Neither vector is read after its timed loop and no optimisation barrier is used, so an optimising build is free to shrink the timed work; the repo's CMake defaults CMAKE_BUILD_TYPE to Debug and adds no -O flag, the likely build behind the book's roughly 120 ns and 37 ns per push_back.
- Timing uses std::chrono::high_resolution_clock, which is not required to be a steady clock; steady_clock is the usual choice for intervals.

## Known shortcomings

- Book numbers only; the CMake project defaults to a Debug build with no -O flag (a Release config exists). The reserve() call sits outside the timed region.
- Enricher: the no-reserve loop always runs first in a fresh process (first-use costs on the baseline side), no optimisation barrier and the vectors are never read, high_resolution_clock.

## Caveats and trade-offs

The timings are the book's own single run (the repo holds the source, no result files), so the numbers could not be checked against a page. Absolute times of about 120 ns and 37 ns per push_back are far slower than an optimised build normally gives for int push_back, and the repo's CMake default build type is Debug with no -O flag, so the run was most likely unoptimised; an unoptimised build inflates the call overhead of push_back on both sides and the ratio in an optimised build can differ (not measured here). One run, no repetitions, compiler, flags and CPU not stated; the two loops run back to back in one process, the second on freshly allocated memory. The reserve(100000) call itself sits before start2, so the one up-front allocation is outside the timed region while the no-reserve loop's roughly 17 reallocations and element copies are inside it; that is the effect being shown, but the with-reserve figure omits its own allocation cost. Tier C: first-party, methodology incomplete. Files opened: chapter03/03_reserve.cpp, root CMakeLists.txt, README.md. [retier] Enricher: harness defects: the no-reserve loop always runs first in a fresh process and the order is never swapped, so first-use costs (page faults, allocator warm-up) land on the baseline side; neither vector is read after timing and there is no optimisation barrier, so an optimised build may shrink the timed work; timing uses high_resolution_clock rather than steady_clock.

reserve() needs the final element count (or a good upper bound) up front; over-reserving wastes memory, and the gain is limited to avoiding reallocation and element moves during growth. It is a standard std::vector usage idiom, not a library.

## Maintenance

Stale Packt companion repo (15 commits, last on 2024-08-29 adding README errata; no issues filed) under MIT; there is nothing to vendor beyond the reserve call, which every standard library provides.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter03/03_reserve.cpp times 100,000 push_back calls into a std::vector&lt;int&gt; without and with reserve(100000) using std::chrono::high_resolution_clock, but the repo holds code only; the 0.01195 s versus 0.003685 s figures are the book's single run, with no compiler, flags or CPU stated and a root CMakeLists.txt that defaults to a Debug build, so first-party with incomplete methodology.
- **Verifier notes:** Source, CMake defaults, MIT license, 63 stars and last commit 2024-08-29 (stale) all confirmed; README errata do not touch this example. A textbook technique rather than a library, kept as a book seed at tier C like earlier book records.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/chapter03/03_reserve.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/README.md>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/chapter03/03_reserve.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/chapter03/01_sizevscapacity.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/chapter03/04_shrinktofit.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/main/README.md>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/tree/main/chapter03>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/commits/main>
  - <https://github.com/PacktPublishing/Data-Structures-and-Algorithms-with-the-CPP-STL/issues?q=is%3Aissue>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-data-structures-and-algorithms-with-the-cpp-stl-vector-reserve`) · [data/wave1/enrich/raw/paper_book_data_structures_and_algorithms_with_the_cpp_stl_vector_reserve.json](../../../data/wave1/enrich/raw/paper_book_data_structures_and_algorithms_with_the_cpp_stl_vector_reserve.json) (enrichment confidence 0.6)

</details>
