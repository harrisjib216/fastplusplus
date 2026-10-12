# EASTL sort algorithms (eastl::sort / quick_sort, eastl::radix_sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> EA's introsort (eastl::sort) plus an LSD radix_sort; beat the VC++ 7.1 Dinkumware std::sort 1.7-1.9x on random 10k arrays.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | EASTL 0.96 release table, quick_sort vs VC++ 7.1 (Dinkumware) std::sort (ratio = std time / EASTL time, above 1 means EASTL faster). Random input: vector&lt;uint32&gt; 1.87x, vector&lt;ValuePair&gt; 1.84x, vector&lt;TestObject&gt; 1.78x, TestObject[] 1.72x. Already-sorted input: vector&lt;uint32&gt; 1.28x, vector&lt;ValuePair&gt; 1.25x, but vector&lt;TestObject&gt; 0.55x and TestObject[] 0.59x (EASTL slower). vector&lt;uint64&gt;/sort 1.02x. No radix_sort or std::stable_sort numbers are published. |
| **Workload** | Stopwatch (CPU cycles) comparison of eastl::quick_sort (what eastl::sort maps to) against std::sort on arrays and vectors of about 10,000 uint32_t, 8-byte ValuePair and TestObject elements, for random input and for already-sorted input. |
| **Metric** | throughput |
| **Hardware** | doc/Benchmarks.md gives no CPU. N2271 lists Pentium 4 x86 for the Windows and Linux columns, without an exact model. |
| **Compiler and flags** | doc/Benchmarks.md: Microsoft Visual C++ 7.1 (version 1310), Release 'Full optimization. Inlining enabled.' (exact flags not given), PPMalloc::GeneralAllocator; also a VC++ 7.1 + STLport column. N2271 appendix 20: Windows column VC8 -Og -Oi -Ot -Oy -Ob2 -GF -Gy with the compiler-supplied STL; console column VC7 -Ox -Ob2 -Oi -Os on 64-bit PowerPC; Linux column GCC 4.1 -O3 with libstdc++; Mac column GCC 4.0 -Os with libstdc++ on a G5. |
| **Adoption** | 9.4k stars, 1.0k forks; Electronic Arts' in-house STL replacement, open-sourced |
| **Last commit** | 2025-10-29 |
| **Links** | [repository](https://github.com/electronicarts/EASTL) · [benchmark](https://github.com/electronicarts/EASTL/blob/master/doc/Benchmarks.md) |

## Verdict

EA's doc/Benchmarks.md (EASTL 0.96, Windows x86, VC++ 7.1 Release, no CPU model) times one sort of 10,000 elements: eastl::quick_sort beat the Dinkumware std::sort 1.84x-1.87x on random uint32 and ValuePair vectors and 1.78x on TestObject, but lost 0.55x on already-sorted TestObject. The same EASTL code ran at about the same speed in the STLport table (2,943,627 vs 2,916,146 cycles for vector&lt;uint32&gt;), where std::sort was only 1.12x slower, so the 1.87x reflects the old Dinkumware sort (derived from page data). radix_sort has no published numbers.

## Use it when

- You already build against EASTL (game or console code) and want one sort that behaves the same on every platform and stays fast in debug builds (VC7.1 Debug table: 5.8x-19.7x over the Debug std::sort)
- Stable sorting of unsigned integer keys, or structs keyed by an unsigned integer, when you can spare an n-element scratch buffer: radix_sort
- You need a stable sort with no heap allocation: tim_sort_buffer or merge_sort_buffer with your own buffer
- You want to swap the sort used across a whole codebase from one place via EASTL_DEFAULT_SORT_FUNCTION / EASTL_DEFAULT_STABLE_SORT_FUNCTION

## Skip it when

- Expecting a speedup over a current libstdc++, libc++ or MSVC std::sort: every published number is from 2005-2007, and against STLport (Release) the random-input gain was only 1.00x-1.12x, against GCC 4.1 libstdc++ 0.96x on vector&lt;uint32&gt;
- Sorting move-only element types such as unique_ptr: the pivot stays a reference into the array during partitioning (see gotchas), which in a model of the code makes the final insertion pass do roughly quadratic work
- Signed or floating-point keys with radix_sort: it orders by raw bits, so negative ints land after positive ones, and float keys are not accepted
- Large integer or float arrays where throughput matters: pdqsort, vqsort, ips4o and ska_sort have published benchmarks against std::sort; EASTL has none newer than 2007
- Already-sorted heavy objects: EASTL was 0.55x (slower) on sorted vector&lt;TestObject&gt; against the Dinkumware sort in the release table

## How it is fast

quick_sort is a classic SGI-style introsort: median-of-three pivot, unguarded Hoare partition, a depth limit of 2\*log2(n) after which it heap-sorts the range (partial_sort), and one final insertion pass with a cutoff of 28 elements on x86/x86-64 and 16 elsewhere (guarded over the first 28, unguarded after). There is no pattern-defeating, branchless or SIMD partitioning, so the published gains came from a weak VC++ 7.1-era baseline, not a new algorithm: EASTL's own time is about the same in the Dinkumware and STLport tables. radix_sort is LSD with 8-bit digits by default; it computes the next digit's histogram during the current scatter and skips passes where every key has the same digit.

## Compared with alternatives

Pick it only when you are already standardised on EASTL and want its sort family (introsort, tim_sort_buffer, merge_sort_buffer, radix_sort) without another dependency. For speed, pdqsort has current numbers against GCC's std::sort, vqsort (Highway) and x86-simd-sort cover SIMD key sorting, and ska_sort or Boost spreadsort are radix-style sorts with published measurements.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | EABase (CMakeLists.txt fetches it with FetchContent); stable_sort/merge_sort also need EASTL's default allocator and the operator new[] overloads the application must supply |
| **Minimum toolchain** | C++14 (CMakeLists.txt: target_compile_features cxx_std_14) |
| **Platforms** | any; insertion-sort cutoff kQuickSortLimit is 28 on x86/x86-64 and 16 on other CPUs |
| **Thread safety** | doc/FAQ.md: algorithms have no instance data and run on the stack, so concurrent calls on separate ranges are safe; note that stable_sort/merge_sort allocate through the shared default allocator, although the FAQ claims no EASTL function allocates |
| **Drop-in for the baseline** | partial — eastl::sort and eastl::stable_sort take the same arguments as std::sort/std::stable_sort and accept std iterators; radix_sort needs a key extractor and an external buffer, and stable_sort allocates through EASTL's allocator |

## Gotchas

- Move-only types: for non-copy-constructible elements quick_sort passes the median-of-three result as an rvalue reference into the array (get_partition T&& overload; the copyable path copies it into pivotCopy), so the pivot value changes whenever iter_swap moves that slot. A Python model of HEAD sort.h still sorts correctly with no out-of-bounds access in 6,000 trials, but the final unguarded insertion pass grew from about 4.5n element moves to about 0.012-0.02 n^2 (4.8M vs 73k moves at n = 16,000); the test suite has no move-only sort test. This path was added for issue #92 (2017).
- radix_sort sorts raw bit patterns: with the header's own example key type (typedef int radix_type) negative keys sort after positive ones (model: [5,-1,3,-200,0,100000,-7] becomes [0,3,5,100000,-200,-7,-1]); TestSort.cpp only tests uint8/16/32 keys.
- radix_sort has no first == last guard: on an empty range it evaluates extractKey(\*srcFirst) one past the end (a null dereference for a default-constructed eastl::vector, whose mpBegin is NULL). DigitBits equal to the key width (allowed by the static_assert) makes 1 &lt;&lt; DigitBits overflow for 32-bit keys, and each pass uses two 2^DigitBits uint32 stack arrays.
- Harness behind the published rows (benchmark/source/BenchmarkSort.cpp, BenchmarkSort()): each row is one timed sort of 10,000 elements (the second of two iterations) with no repeats or variance, the '/sorted' rows re-sort the previous call's output, and the 'TestObject[]' rows reset and re-sort the same std::vector/eastl::vector&lt;TestObject&gt; rather than a C array, so they repeat the vector&lt;TestObject&gt; rows (published 1.72x vs 1.78x, 0.59x vs 0.55x).

## Known shortcomings

- First-party 2005-07 q_sort rows: sorted TestObject 0.55x/0.59x (slower), about 0.96-1.38x vs STLport and libstdc++ 4.1; no radix_sort numbers.
- Enricher: the gains are only against VC++ 7.1 Dinkumware std::sort (EASTL's own time is the same in the Dinkumware and STLport tables, 2,916,146 vs 2,943,627 cycles, and STLport std::sort is only 1.12x slower); a Python model of HEAD sort.h shows that for move-only types the pivot stays a reference into the array so the final insertion pass goes about quadratic (4.8M vs 73k moves at n=16,000; output still sorted, path added for issue #92); radix_sort puts negative signed keys after positive ones although the header's own example uses int, and on an empty range dereferences \*last; the TestObject[] rows re-sort the same vectors as the vector&lt;TestObject&gt; rows; every row is a single timed run.

## Caveats and trade-offs

The only published tables are doc/Benchmarks.md (EASTL version 0.96.00, Windows x86, Microsoft Visual C++ 7.1 with the Dinkumware STL or STLport, custom PPMalloc allocator, no CPU model stated) and the 2007 WG21 paper N2271 (doc/EASTL-n2271.pdf, written by EASTL's author), so all numbers are first-party and roughly 20 years old. Ratios are other-STL time divided by EASTL time from a single stopwatch run in CPU cycles, with no variance reported. Against STLport's std::sort in Release the gain is small: random input 1.00x-1.12x, already-sorted 1.25x-1.38x. N2271 columns: Linux (Pentium 4, GCC 4.1 -O3, libstdc++) 0.96x (vector&lt;uint32&gt; random) to 1.34x (vector&lt;TestObject&gt; sorted); Windows VC8 1.25x-1.50x; Mac G5 GCC 4.0 -Os 1.14x-1.75x; console PowerPC VC7 1.49x-3.53x. Against libstdc++'s sort the gain was small. The std::sort implementations of 2005-2007 are far behind current libstdc++, libc++ and MSVC introsorts, so the 1.7-1.9x vs Dinkumware does not transfer. radix_sort: include/EASTL/sort.h only says it is 'typically faster than any other sort' and 'faster than all others' for integral data (qualitative). The current benchmark/source/BenchmarkSort.cpp compares eastl::sort (quick_sort), radix_sort, tim_sort, merge_sort, heap_sort and others against std::sort and std::stable_sort at sizes 10, 100, 1000 and 10000 over random, random-sorted, ordered and mostly-ordered input, but only at verbosity 3, it prints its tables at run time and no results are checked in; no independent radix_sort measurement was found. eastl::copy is in the same family: Benchmarks.md release rows give algorithm/copy/vector&lt;LargePOD&gt; 1.30x and copy/vector&lt;uint32_t&gt; 0.91x (EASTL slower), so no copy win is claimed.

eastl::sort maps to quick_sort, an unstable introsort needing random-access iterators; eastl::stable_sort maps to merge_sort. eastl::radix_sort is an LSD radix sort for integral keys only: elements need a radix_type key (or a key-extractor functor), it is stable, and it needs a caller-supplied scratch buffer as large as the input. The benchmark source notes it performs poorly on contiguous ordered keys (kOrdered).

## Maintenance

EASTL is actively maintained (BSD-3-Clause, 9.4k stars, 79 open issues) and usable as a library, but its sort code is a classic median-of-three introsort with no published measurement against any modern standard library. This enrichment found three issues the verifier did not record: the move-only pivot aliasing (quadratic final pass in a model of the code), radix_sort misordering signed keys, and radix_sort reading past the end of an empty range. The published TestObject[] rows duplicate the vector&lt;TestObject&gt; rows in today's harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/Benchmarks.md (Win32.VC71.MS.Release, sort/q_sort rows) is a first-party EA table of eastl::quick_sort against VC++ 7.1 std::sort, and all claimed ratios appear in it; no CPU model, exact flags or variance are given. N2271 adds flags but only the CPU family, and the 0.96-era harness is not the code in today's repo, so not A.
- **Verifier notes:** All claimed ratios match the Win32.VC71.MS.Release sort/q_sort rows; the harness calls std::sort vs eastl::quick_sort on 10000-element inputs (BenchmarkSort.cpp), and eastl::sort maps to quick_sort unless EASTL_DEFAULT_SORT_FUNCTION is set. Shortcomings to record: first-party 2005-2007 numbers vs Dinkumware std::sort; EASTL slower on already-sorted TestObject (0.55x/0.59x); vs STLport and libstdc++ 4.1 roughly 1.0x-1.3x; no radix_sort numbers. Metadata: BSD-3-Clause, 9.4k stars, last commit 2025-10-29 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/commits/master>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/EASTL-n2271.pdf>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkSort.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/sort.h>
- **Sources the enricher read:**
  - <https://github.com/electronicarts/EASTL>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/README.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/sort.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/algorithm.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/vector.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkSort.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/test/source/TestSort.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/EASTL-n2271.pdf>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/FAQ.md>
  - <https://github.com/electronicarts/EASTL/issues?q=is%3Aissue+sort>
  - <https://github.com/electronicarts/EASTL/issues?q=is%3Aissue+radix>
  - <https://github.com/electronicarts/EASTL/issues/92>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:eastl-sort-radix-sort`) · [data/wave1/enrich/raw/paper_eastl_sort_radix_sort.json](../../../data/wave1/enrich/raw/paper_eastl_sort_radix_sort.json) (enrichment confidence 0.7)

</details>
