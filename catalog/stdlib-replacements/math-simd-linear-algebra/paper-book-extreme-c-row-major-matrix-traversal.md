# Extreme C: cache-friendly row-major matrix summation (chapter 5, example 5.6)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Book example: summing a row-major C int matrix in memory order instead of column by column, for cache locality.

| | |
|---|---|
| **Beats** | column-major (cache-unfriendly) traversal of the same row-major int matrix |
| **Claimed result** | Book run (relayed via the seed lead from the book, not shown on any repo page I opened): about 5.2 s row-major against about 15.4 s column-major, a gap the book puts at about 10 seconds. About 3.0x (derived from the relayed numbers). |
| **Workload** | Sum of a 20,000 x 20,000 int matrix (1.6 GB, malloc'd flat array) walked in memory order (friendly-sum) against walked column by column (not-friendly-sum); timed with the shell time command, so the matrix allocation and fill are included. |
| **Metric** | latency |
| **Compiler and flags** | Book run reported as built with clang on macOS, no optimisation flags stated (relayed via lead). The repo's ch05-stack-and-heap/CMakeLists.txt sets no flags or build type (a typo'd CMAKE_EXPORT_5OMPILE_COMMANDS line and add_executable only). |
| **Adoption** | 411 stars; Packt companion repository of the book Extreme C (2019) |
| **Last commit** | 2023-01-18 |
| **Links** | [repository](https://github.com/PacktPublishing/Extreme-C) · [benchmark](https://github.com/PacktPublishing/Extreme-C/blob/master/ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c) |

## Verdict

The book reports one run of example 5.6 on a 20,000 x 20,000 int matrix built with clang on macOS, flags and CPU not stated: about 5.2 s for the row-order sum against about 15.4 s column by column, about 3.0x (derived from the relayed numbers), each timed with the shell's time around a whole process that also allocates and fills the 1.6 GB matrix. The numbers come from the book via the seed lead; no repo page carries them.

## Use it when

- Any loop nest over a row-major buffer (C 2-D arrays, a flat std::vector indexed i\*cols+j, image rows, row-major tensors): make the last index the innermost loop.
- Matrices or images much larger than the caches, where a strided walk costs a cache miss and often a TLB miss per element; the example's 1.6 GB matrix is the extreme case.
- Builds where the compiler will not reorder the loops for you: unoptimised builds, or optimised builds without loop interchange (GCC turns -floop-interchange on only at -O3).
- Column-major data (Fortran and BLAS/LAPACK conventions): the same rule applies with the roles swapped, so the row index goes innermost.

## Skip it when

- Algorithms that must read the same data in both orders (transpose, matrix multiply, column reductions alongside row reductions): interchange alone cannot make both sides sequential; use tiling or a tuned BLAS from the catalog's blas-lapack category.
- Matrices that fit in L1 or L2: the gap comes from cache and TLB misses, so it shrinks once the data stays cached (the example does not measure small sizes).
- As copyable code: the sample accumulates into a signed int that overflows at the book's size, never checks malloc, does its size and index arithmetic in int (overflow above about 2.1 billion elements) and fills each row with its row number rather than a running counter.
- Floating-point reductions where bit-exact results matter: interchanging the loops changes the summation order and can change the rounding.

## How it is fast

Spatial locality: the row-order walk uses every int of each cache line it loads (16 per 64-byte line) and gives the hardware prefetcher one sequential stream. The column-order walk on a 20,000-column matrix strides 80,000 bytes per step, so every access lands on a different cache line and a different 4 KB page; the roughly 1.3 MB of lines one column touches exceed the inner caches before the next column reuses them, and 20,000 distinct pages per column overflow the TLB. The fix is loop interchange; for patterns that must walk both ways (transpose, matrix multiply) the standard follow-up is loop tiling (blocking).

## Compared with alternatives

The siblings are container libraries (EASTL, plf::colony, veque) that replace data structures; this entry is a zero-cost loop-order fix for code that already holds a contiguous row-major buffer. It pairs with The Art of Writing Efficient Programs vector-versus-list entry: that one makes the data contiguous, this one walks contiguous data in memory order.

## Integration

| | |
|---|---|
| **Form** | source-drop (a loop-order idiom; the example is one C file) |
| **Dependencies** | none (C standard library: stdio.h, stdlib.h, string.h) |
| **Minimum toolchain** | C99 (declarations inside for statements); the chapter's CMakeLists.txt sets no standard, build type or flags, and the root CMakeLists.txt never builds chapter 5 (its add_subdirectory(ch05) line is commented out and names a folder that is actually ch05-stack-and-heap), so it is compiled by hand |
| **Platforms** | any; the size of the gap depends on cache line size, cache sizes, TLB reach and the prefetchers |
| **Thread safety** | not applicable (single-threaded example; the sums only read the matrix) |
| **Drop-in for the baseline** | partial — swap the two loops over the same data; integer results stay the same (absent overflow), floating-point reductions may round differently |

## Gotchas

- The book's figures time the whole process with the shell, so the 1.6 GB malloc, its page faults and a row-order fill() pass are inside both timings; since that setup is the same in both modes, the traversal-only ratio is larger than the relayed about 3.0x.
- The sum of the 20,000 x 20,000 matrix is about 4.0e12, far beyond a 32-bit int; signed overflow is undefined behaviour in C, which an optimiser may exploit. Use a 64-bit accumulator.
- One shell-timed run per mode, no repetitions, flags or CPU stated; with an optimising compiler that performs loop interchange (GCC at -O3) not_friendly_sum may be rewritten into the friendly order and the gap can vanish (not measured here).
- The usage path is broken: the first printf has a %s with no argument and argv[0] is passed to the second printf, which has no conversion; it only runs when arguments are missing.

## Known shortcomings

- Book numbers only. The baseline is column-major traversal of a raw C array, not a listed std container; the row-order fill() is timed in both runs, so the ratio understates the gap, and GCC -O3 loop interchange can erase it. The code has signed int overflow.
- Enricher: the chapter is never built by the repo's CMake (commented out, wrong folder name); int index arithmetic overflows above about 2.1e9 elements and malloc is unchecked; fill() writes the row number, not a counter. Category moved from sequence-containers to math-simd-linear-algebra (matrix traversal order).

## Caveats and trade-offs

Single run each, timed by the shell around the whole program, so it includes malloc of 1.6 GB and the fill pass; fill() walks the matrix in row order in both modes, so the measured ratio understates the gap between the two traversals themselves. Compiler flags and CPU not stated and the repo carries no result files. The program accumulates into a signed int, which overflows at this size (about 4e12 expected) and is undefined behaviour in C, though both loops do the same arithmetic. The build is probably unoptimised (no flags in the repo), where the gap is dominated by cache and TLB misses and can differ when a compiler interchanges loops (GCC enables -floop-interchange at -O3). The usage message in main() has a printf format bug (argv[0] passed to the wrong printf) that does not affect the timing. The baseline is a loop order over a raw C array, not one of the category's listed std containers. Tier C: first-party book measurement. Files opened: ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c and CMakeLists.txt, root LICENSE and repository page. [retier] Enricher: the root CMakeLists.txt never builds this chapter (#add_subdirectory(ch05) is commented out and the real folder is ch05-stack-and-heap), so the book's build was by hand. fill() writes the row number into each row, not a running counter. Size and index arithmetic in int overflows above about 2.1e9 elements, and malloc is unchecked. Setup is identical in both modes, so the traversal-only ratio must exceed the relayed 3.0x.

Loop order only: both versions run the same additions over the same flat array; the friendly one follows memory order. A teaching example of cache locality, not a library; applicable to any row-major buffer.

## Maintenance

Abandoned Packt companion repo (last commit 2023-01-18 on book-promotion notices; this file unchanged since its 2019-08-16 import), MIT-licensed; the idea needs no code, and the sample should not be vendored as-is because of its overflow and unchecked-malloc bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c implements friendly_sum (row order) and not_friendly_sum (column order) over the same malloc'd row-major int matrix, selected by a command-line argument, but the repo holds code only; the 5.2 s versus 15.4 s figures are the book's single shell-timed run with no flags or CPU model, so first-party with incomplete methodology.
- **Verifier notes:** Code, CMake (no flags, typo'd CMAKE_EXPORT_5OMPILE_COMMANDS), MIT license, 411 stars and last commit 2023-01-18 (abandoned) confirmed. baseline_in_list set false: column-major traversal of a malloc'd C array is not std::vector/deque/list/array; the entry is a cache-locality technique in C and fits sequence-containers loosely, so the orchestrator may want a category override.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c>
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/ch05-stack-and-heap/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/LICENSE>
  - <https://github.com/PacktPublishing/Extreme-C>
  - <https://github.com/PacktPublishing/Extreme-C/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c>
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/ch05-stack-and-heap/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Extreme-C/master/README.md>
  - <https://github.com/PacktPublishing/Extreme-C>
  - <https://github.com/PacktPublishing/Extreme-C/commits/master>
  - <https://github.com/PacktPublishing/Extreme-C/commits/master/ch05-stack-and-heap/ExtremeC_examples_chapter5_6.c>
  - <https://github.com/PacktPublishing/Extreme-C/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Extreme-C/issues/4>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-extreme-c-row-major-matrix-traversal`) · [data/wave1/enrich/raw/paper_book_extreme_c_row_major_matrix_traversal.json](../../../data/wave1/enrich/raw/paper_book_extreme_c_row_major_matrix_traversal.json) (enrichment confidence 0.6)

</details>
