# The Art of Writing Efficient Programs: contiguous std::vector instead of std::list for sequential traversal

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book benchmark: traverse a contiguous std::vector instead of a node-based std::list; about 8x faster sequential reads.

| | |
|---|---|
| **Beats** | std::list&lt;unsigned long&gt; |
| **Claimed result** | Book: list access just over 5 ns per value versus about 0.6 ns per value for the vector, almost an order of magnitude (about 8x, derived from the book figures); footprint 8 MB versus 24 MB. |
| **Workload** | Chapter04/03_list_vector.C (Google Benchmark): sequential iterator read and write of 1,048,576 unsigned long elements in std::vector versus std::list, 32x unrolled loop with DoNotOptimize on each access. |
| **Metric** | throughput |
| **Hardware** | x86; CPU model not stated, caches 32 KB L1, 256 KB L2, 8 MB L3 per the book |
| **Compiler and flags** | Not stated for the book's run. The repo's generic build command (Chapter02/ReadMe.md) is \$CXX (GCC or Clang) -g -O3 --std=c++17 linked against Google Benchmark with -lpthread -latomic -lrt -lm; compiler and version unnamed. |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter04/03_list_vector.C) |

## Verdict

The book's own run, relayed by the seed lead and not printed in the repo, reports just over 5 ns per element for std::list against about 0.6 ns per element for std::vector when reading 1,048,576 unsigned long values (about 8x, derived from those figures), on an unnamed x86 CPU with 32 KB L1, 256 KB L2 and 8 MB L3; compiler, version and standard library are not stated beyond the repo's generic -O3 --std=c++17 build line. The repo holds the matching Google Benchmark source but no results.

## Use it when

- Hot loops that walk the whole sequence front to back (sums, filters, rendering, simulation steps) over small trivially-copyable elements such as integers, floats or small PODs.
- Containers of thousands to millions of elements whose footprint exceeds L1/L2, where per-node pointer chasing turns into cache or DRAM latency on every step.
- Append-mostly or rebuild-then-read workloads where elements are added at the back and rarely inserted or erased in the middle.
- Code that only uses std::list for push_back and iteration out of habit, with no reliance on iterator or reference stability.

## Skip it when

- Code that keeps iterators, pointers or references to elements across insertions: a vector invalidates them on reallocation and on insert or erase before them, a list never does.
- Frequent insert or erase in the middle of large sequences of large or expensive-to-move elements, where shifting the tail costs O(n) per operation.
- Algorithms built on list-only operations: splice, merge, O(1) node transfer between lists, or list::sort that relinks nodes without moving the elements.
- Very large elements (hundreds of bytes and up) traversed sparsely: each node then fills whole cache lines anyway, so the gap measured here for 8-byte values does not carry over.

## How it is fast

Contiguous storage: the vector packs 8 values per 64-byte cache line at addresses the core can compute in advance, so the hardware prefetcher streams them and many loads are in flight at once. Each std::list step is a dependent load (pointer chasing): the next node's address is unknown until the current node arrives, and each 8-byte value travels in a 24-byte node (two links plus the value), so the list moves about 3x the bytes with little memory-level parallelism. Both loops are 32x unrolled with benchmark::DoNotOptimize on every element, which keeps both sides scalar, so the gap comes from the memory access pattern rather than SIMD.

## Compared with alternatives

Pick the plain vector when you only append and iterate and can tolerate invalidation; pick plf::list if you need real list semantics (stable iterators, splice, O(1) middle insert) with faster insertion than std::list, or plf::colony/plf::hive if you need stable pointers plus fast iteration and erasure but not ordering.

## Integration

| | |
|---|---|
| **Form** | source-drop (an idiom; the repo file is a standalone Google Benchmark program) |
| **Dependencies** | none for the idiom; the benchmark needs Google Benchmark (libbenchmark, -lpthread) and includes &lt;emmintrin.h&gt; and &lt;immintrin.h&gt; |
| **Minimum toolchain** | C++98 for std::vector; the repo's generic build line (Chapter02/ReadMe.md) uses --std=c++17 -O3 with GCC or Clang |
| **Platforms** | any for the idiom; the benchmark file as written is x86-only because it includes the SSE/AVX intrinsics headers unconditionally |
| **Thread safety** | standard library rules: concurrent const access is safe, any concurrent modification needs external synchronisation (same as std::list) |
| **Drop-in for the baseline** | partial — same sequence interface for iteration, push_back, insert and erase, but no push_front/pop_front, splice, merge, remove or member sort, and different iterator invalidation rules |

## Gotchas

- The list in this benchmark is the friendliest case: 1M nodes allocated back to back in a fresh process, so they most likely sit in address order where the prefetcher can follow them; a list built by interleaved inserts and erases in a long-running program is scattered and slower, so the measured gap understates the usual one.
- The timed loop tests it != end only once per 32 unrolled accesses, so the harness is only valid for element counts that are multiples of 32 (1&lt;&lt;20 and the commented-out 1&lt;&lt;6..1&lt;&lt;16 range are); other sizes walk past the end.
- SetBytesProcessed counts sizeof(unsigned long) per element for both containers, so the list's reported bytes per second understate the memory it actually moves (24-byte nodes in what glibc malloc serves as 32-byte chunks).
- Chapter04 has no build comment or ReadMe (Chapter04/ReadMe.md returns 404); the only build instructions are the repo-wide ones in Chapter02/ReadMe.md, and no results file is committed.

## Known shortcomings

- Book numbers only; the repo gives a generic '\$CXX -g -O3 --std=c++17' and no CPU. List nodes take 32-byte malloc chunks (about 32 MB) while the 8 MB vector about equals an 8 MB L3; the __m128i/__m256i registrations are commented out.
- Enricher: best-case list (address-ordered nodes in a fresh process), so the 8x likely understates the gap; end check once per 32 accesses (undefined behaviour for other counts); x86-only include.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. Library and compiler not stated, so the result is for one unnamed standard library. The list is built by consecutive allocations in a fresh process, so its nodes are probably laid out nearly in order; a fragmented list from a long-running program would be slower. Well-known result, so this is an example of the idiom rather than new evidence; the file also defines but does not register the __m128i and __m256i vector variants. [verifier] Correction: the __m128i and __m256i variants are generic template instantiations whose BENCHMARK_TEMPLATE1 lines are commented out. The 1M-element vector (8 MB) is about the size of the book's 8 MB L3 while the list (24-byte nodes, which glibc malloc places in 32-byte chunks, so about 32 MB in practice) is not, so part of the gap is cache-level residency as well as pointer chasing. DoNotOptimize on every element blocks vectorisation of the vector loop, which keeps the traversal comparison fair. [retier] Enricher: the harness checks out (both sides scalar, DoNotOptimize symmetric), but the list is a best case: 1M nodes allocated back to back in a fresh process are likely address-ordered, so the 8x understates the usual gap. The timed loop checks for the end once per 32 accesses, valid only for element counts that are multiples of 32 (undefined behaviour otherwise). SetBytesProcessed counts 8 bytes per element for the list too, understating its memory traffic. The file includes immintrin.h unconditionally (x86 only); Chapter04 has no ReadMe.

Vector loses O(1) middle insert and erase and pointer stability on growth; the 3x memory footprint of the list (node headers) is part of the gain.

## Maintenance

Stale Packt companion repo (last commit 2024-05-13, 405 stars, one open question issue about Chapter07), MIT-licensed; the idiom needs no code, and the benchmark file is small enough to copy for a local re-run on x86.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter04/03_list_vector.C registers BM_read_vector, BM_read_list, BM_write_vector and BM_write_list for unsigned long at Arg(1&lt;&lt;20) with Google Benchmark, but the repo holds code only; the 5 ns versus 0.6 ns figures are the book's own run relayed by the lead, and the repo states only a generic GCC-or-Clang -O3 build command and no CPU model, so first-party tier C.
- **Verifier notes:** Code matches the record (1&lt;&lt;20 unsigned long, 32x REPEAT with DoNotOptimize, read and write variants for both containers). Well-known idiom kept at C. Metadata checked on github.com: MIT, 405 stars, 62 commits, last 2024-05-13, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter04/03_list_vector.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter04/03_list_vector.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter02>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter04/03_list_vector.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter02/ReadMe.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter04/ReadMe.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/LICENSE>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter04>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue+is%3Aclosed>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-vector-instead-of-list`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_vector_instead_of_list.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_vector_instead_of_list.json) (enrichment confidence 0.65)

</details>
