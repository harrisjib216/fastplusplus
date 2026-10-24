# The Art of Writing Efficient Programs: signed int loop index in substring comparison

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book idiom: signed int index in a hand-written string-compare loop beats unsigned-index versions inside a std::sort benchmark.

| | |
|---|---|
| **Beats** | std::sort with a hand-written substring comparison that uses an unsigned int index (bounded and unbounded variants) |
| **Claimed result** | Book-reported (relayed via the seed lead; no numbers anywhere in the repository): the sort takes 98 ms with the bounded unsigned compare, 210 ms with the unsigned compare without the bound check, and 74 ms with the signed int index compare, so the signed version is about 1.3x faster than the bounded unsigned one and about 2.8x faster than the unbounded unsigned one (both derived from the relayed book figures). |
| **Workload** | Chapter02 01/03/04_substring_sort.C with the shared setup 00_substring_sort_prep.C (option C): std::sort of 2^14 pointers to random offsets in a 2^18-byte NUL-terminated string that is all 'a' except 256 randomly placed random letters (about one per 1024 chars), using a lambda that counts comparisons and calls compare() defined in a separate translation unit; wall time of the sort only, by std::chrono::system_clock, single run. |
| **Metric** | latency |
| **Hardware** | CPU model not stated |
| **Compiler and flags** | \$CXX, unspecified (Chapter02/ReadMe.md: 'usually GCC or CLANG'), with -g -O3 -I. --std=c++17 per the build comment in each Chapter02 0N_substring_sort.C; no LTO, so compare() in its own translation unit is not inlined |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter02) |

## Verdict

The book, relayed by the seed lead (the repo has no numbers), reports 98 ms with the bounded unsigned compare, 210 ms with the unbounded unsigned compare and 74 ms with the unbounded int compare for std::sort of 16,384 suffix pointers into a 256 KiB mostly-'a' string, about 1.3x and 2.8x (derived from those figures). The compiler is only 'GCC or Clang' at -O3, the CPU and run count are not stated, and the setup file was corrected in 2022, so it is unknown which version of the workload produced the numbers.

## Use it when

- Hot hand-written loops on a 64-bit target that index a buffer with a 32-bit counter and stop on a sentinel or mismatch rather than on a bound the compiler can see.
- Comparators for suffix or substring sorting where you can guarantee every comparison ends on a mismatch long before the index reaches INT_MAX (here: distinct suffixes of one buffer with a single NUL at the end).
- As a code-review rule for performance-sensitive loops: prefer int or a pointer-width index (std::ptrdiff_t, std::size_t) over unsigned int; the pointer-width types avoid the 32-bit wrap without relying on undefined overflow (not measured in the repo).
- Reading compiler output: Chapter11/04a_compare1.C and 04b_compare2.C hold the unsigned and int versions alone, ready to paste into a disassembler.

## Skip it when

- As a general string comparison: compare() never stops at the NUL terminator, so two equal strings at different addresses are read past their ends. Use std::strcmp, std::memcmp or std::string_view::compare, none of which the repo benchmarks, and which may beat all three loops.
- Buffers or loop counts that can reach 2^31: signed int overflow is undefined behaviour, so the int version is only valid while the index stays below INT_MAX.
- When the loop already carries a bound: the gain against the bounded unsigned loop is about 1.3x in the book figures; the 2.8x is against a variant the book made slower by removing the bound.
- When you need a faster sort: only the comparator changes and std::sort is untouched; the algorithmic gains are in the sibling sort libraries.
- Toolchains you have not checked: the repo names no compiler version, and the direction of the effect depends on code generation (issue #2's title says 04 was slower than 03, but it gives no numbers and was closed by its reporter with a pointer to the book's undefined-behaviour chapter).

## How it is fast

Unsigned int arithmetic must wrap modulo 2^32, so in the unbounded loop the compiler has to keep a 32-bit index and zero-extend it into each 64-bit address; signed int overflow is undefined behaviour, so the compiler may widen the index to a 64-bit offset or walk the pointers directly (induction-variable widening). The bounded unsigned loop sits in between, presumably because i1 &lt; l lets the compiler prove the index never wraps. This mechanism is inferred from the source; no disassembly or measurement was done for this entry. The extra per-byte instructions matter here because each comparison scans a long equal prefix (one non-'a' letter per about 1024 bytes, derived from the setup code).

## Compared with alternatives

Not an alternative to pdqsort, ska_sort or Highway vqsort: it changes only the comparator's inner loop and keeps std::sort. If a profile shows a hand-written byte comparator dominating a string or suffix sort, fix its index type (or call std::memcmp/std::strcmp) first; the sibling sorts are where the gains are for integer keys or a slow sort algorithm.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the sort programs (standard library only); the Chapter02 microbenchmarks (10a, 11, 12_\*) need Google Benchmark |
| **Minimum toolchain** | the idiom works in any C++ version; the build comments use --std=c++17 with \$CXX 'usually GCC or CLANG' at -O3 (Chapter02/ReadMe.md) |
| **Platforms** | any; the effect is specific to targets where int is 32 bits and pointers are 64 bits (x86-64 and similar) |
| **Thread safety** | pure function over read-only data; safe to call concurrently |
| **Drop-in for the baseline** | partial — same signature as the unbounded unsigned version (03); the bounded version (01) takes a length argument that the int version drops, so the call site changes |

## Gotchas

- The shared setup 00_substring_sort_prep.C was fixed on 2022-02-09 (commit ac595cb, 'Fixed typo in initialization of the string'): before it, memset filled only N = 2^14 bytes of the 2^18-byte buffer with 'a' and the rest stayed uninitialised, so the 'every comparison ends on a mismatch inside the buffer' property did not hold. Which version produced the book's figures is not documented.
- The build comments in 03_substring_sort.C and 04_substring_sort.C both write -o 01_substring_sort, so following them literally overwrites the 01 binary and can time the wrong variant.
- Each program times one std::sort with std::chrono::system_clock (one run, fixed default minstd_rand seed); the comparator returns s1 &gt; s2, so the order is descending (harmless). Because all three variants return the same results on this data, std::sort makes identical comparisons and the printed comparison count should match across 01/03/04, a cheap sanity check.
- The microbenchmarks compare a 1 MiB all-'a' scan whose only mismatch is the terminator; 12_compare_mbm_c.C (int index with an int bound) against 12_compare_mbm_d.C (unsigned index with an unsigned bound) isolates signedness with a bound, a cleaner pairing than the sort programs offer. No results are checked in for any of them.

## Known shortcomings

- Book numbers only (98/210/74 ms), no CPU; compiler given only as '\$CXX, usually GCC or CLANG'. The loop bound is the whole string length L, so the check never ends the loop and is pure overhead; 01 vs 04 changes two things and only 03 vs 04 isolates signedness. The build comments in 03 and 04 write to 01_substring_sort, overwriting the 01 binary; single run with system_clock. A loop-index micro-optimisation filed under sorting, a loose category fit. Stale (last commit 2024-05-13).
- Enricher: a 2022 fix (ac595cb) changed the buffer initialisation from 2^14 to 2^18 bytes and the book's figures may predate it; issue #2 reports the opposite direction on another toolchain (no numbers); compare() over-reads past NUL; no strcmp/memcmp baseline.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. Compiler is only 'GCC or Clang'. Baseline is a hand-written byte loop, not std::memcmp or std::strcmp, which would probably beat all three variants and was not tried. It is odd that the unbounded unsigned loop (210 ms) is slower than the bounded one (98 ms); the explanation is compiler-specific code generation, so another compiler or version may show a different ordering. Single timed run with a deterministic minstd_rand seed; the data are almost constant, so many comparisons run to the end of a long equal prefix. [verifier] By reading the source (not compiled or run here): the bounded variant's limit is L, the whole 2^18-byte string length, not the remaining length; the buffer ends in a single NUL and compare() returns early when s1 == s2, so every call ends on a mismatch before the limit, all three variants return the same result, and the bound check is pure per-byte overhead. 01 against 04 changes two things (drops the bound and its parameter, and switches to a signed index); 03 against 04 isolates the signedness. A likely mechanism, not confirmed by disassembly here: signed overflow is undefined, so the compiler may widen the int index to a 64-bit pointer offset, while an unbounded unsigned int index must wrap modulo 2^32 and needs per-step zero-extension; the bound i1 &lt; l lets the compiler prove no wrap, which would explain why the bounded unsigned loop beats the unbounded one. Chapter02 also carries Google Benchmark microbenchmarks of the same three compare functions (10a_compare_mbm.C, and 11_compare_mbm.C with compare() in separate files 11_compare_mbm_a/b/c.C, plus the 12_compare_mbm_\* variants) on a 2^20-byte all-'a' buffer, but no results for them either. The build comments in 03_substring_sort.C and 04_substring_sort.C both name the output binary 01_substring_sort (copy-paste), so building as written overwrites the 01 binary. Timing uses system_clock rather than steady_clock, and the timed lambda also increments a comparison counter (same in all variants). [retier] Enricher: commit ac595cb (2022-02-09, 'Fixed typo in initialization of the string') changed the 00_substring_sort_prep.C memset length from N to L; before it only 2^14 of the 2^18 bytes were initialised, so suffixes were not guaranteed to differ inside the buffer, and it is unknown whether the book's 98/210/74 ms came from pre-fix or post-fix code. Issue #2 (closed by its reporter, no numbers) is titled '04 slower than 03', so the direction of the effect is unconfirmed on other toolchains. compare() never stops at NUL, so it over-reads on equal strings at different addresses; 12_compare_mbm_c/d isolate signedness with a bound. No strcmp or memcmp baseline anywhere in Chapter02.

Relies on signed overflow being undefined so the compiler can assume the index never wraps; strings or loops past INT_MAX characters would be undefined behaviour. Chapter11 (04a_compare1.C and 04b_compare2.C) repeats the idea with no numbers in the text.

## Maintenance

Book companion code under MIT (Copyright (c) 2020 Packt); Chapter02 last changed in April-May 2024 (file uploads and a README update) with no ongoing maintenance, so copy the six-line idiom, not the harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter02/01_substring_sort.C, 03_substring_sort.C and 04_substring_sort.C (shared setup 00_substring_sort_prep.C, compare() in the matching _a.C files) are public and differ only in the compare() loop (bounded unsigned, unbounded unsigned, unbounded int), with -g -O3 build comments, but the compiler is only '\$CXX, usually GCC or CLANG' (Chapter02/ReadMe.md), no CPU is named and no results exist in the repo; the 98/210/74 ms figures are the book's own (first-party), so C.
- **Verifier notes:** Code matches the record: 01/03/04 differ only in compare() (bounded unsigned, unbounded unsigned, unbounded int), setup and timing as described; numbers are book-only, so tier C stands. benchmark_url moved from the 8-line 04_substring_sort_a.C to the Chapter02 directory, which holds all three variants, the main programs and the build ReadMe. Metadata confirmed on github.com: MIT (Copyright (c) 2020 Packt), 405 stars, 91 forks, not fork or archived, last commit 2024-05-13 'Update README.md' (stale); category 'sorting' is arguable since the technique is an integer index type in a comparison loop, so the orchestrator may want a category override.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter02/04_substring_sort_a.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter02>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/ReadMe.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/00_substring_sort_prep.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/02_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/03_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/03_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/04_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/04_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/10a_compare_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_b.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_c.C>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter02>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master/Chapter02>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commit/ac595cb>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues/2>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/ReadMe.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/00_substring_sort_prep.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01a_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01a_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01a_substring_sort_b.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/01a_substring_sort_c.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/02_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/03_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/03_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/04_substring_sort.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/04_substring_sort_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/05_compare_timer.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/10a_compare_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_b.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/11_compare_mbm_c.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_a.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_b.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_c.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_d.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_e.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_f.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/12_compare_mbm_g.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter11/04a_compare1.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter11/04b_compare2.C>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-signed-int-loop-index`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_signed_int_loop_index.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_signed_int_loop_index.json) (enrichment confidence 0.6)

</details>
