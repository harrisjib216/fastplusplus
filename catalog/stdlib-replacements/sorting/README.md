# Sorting

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::sort, std::stable_sort, std::partial_sort, std::nth_element  
**29 entries:** 7 tier A · 0 tier B · 21 tier C · 1 tier D · 29 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Highway (vqsort)**](google-highway.md) | SIMD-dispatched vectorized quicksort/quickselect for built-in key types; \~10x faster than LLVM std::sort on large arrays. | **A** | C++ | Apache-2.0 OR BSD-3-Clause | 🟢 active |
| 2 | [**Boost.Sort — spreadsort**](boostorg-sort.md) | Hybrid radix/comparison sort in Boost; beats std::sort on large random integers, strings, and objects. | **A** | C++ | BSL-1.0 | 🟢 active |
| 3 | [**CAFS (cache-aware frequency sort)**](kexibq-official-cafs-lib.md) | Header-only AVX2 hash-count sort for integer vectors with few distinct values; beats pdqsort, IPS4o and vqsort while K stays far below N. | **A** | C++ | MIT | 🟢 active |
| 4 | [**IPS⁴o (In-place Parallel Super Scalar Samplesort)**](ips4o-ips4o.md) | In-place parallel/sequential comparison sort beating std::sort via cache-efficient block-based samplesort partitioning. | **A** | C++ | BSD-2-Clause | 🟡 stale |
| 5 | [**pdqsort**](orlp-pdqsort.md) | Header-only C++ drop-in std::sort replacement: pattern-defeating quicksort with branchless partitioning and a guaranteed O(n log n) worst case. | **A** | C++ | Zlib | 🔴 abandoned |
| 6 | [**LearnedSort**](anikristo-learnedsort.md) | CDF-model-based sort for numeric arrays, \~4x faster than std::sort on random data, \~15-20x on sorted/duplicate data. | **A** | C++ | GPL-3.0 | 🔴 abandoned |
| 7 | [**BlockQuicksort**](weissan-blockquicksort.md) | In-place Quicksort using block-buffered Hoare partitioning to avoid branch mispredictions; \~88% more elements/s than GCC std::sort on random ints. | **A** | C++ | GPL-3.0 | 🔴 abandoned |
| 8 | [**EASTL sort algorithms (eastl::sort / quick_sort…**](paper-eastl-sort-radix-sort.md) | EA's introsort (eastl::sort) plus an LSD radix_sort; beat the VC++ 7.1 Dinkumware std::sort 1.7-1.9x on random 10k arrays. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 9 | [**Thrust (thrust::sort)**](nvidia-cccl.md) | Header-only CUDA algorithms library; thrust::sort's GPU radix sort beat single-threaded std::sort 80-320x on large int arrays. | **C** | C++ | Apache-2.0 (Thrust, with… | 🟢 active |
| 10 | [**x86-simd-sort (numpy/x86-simd-sort)**](numpy-x86-simd-sort.md) | AVX-512/AVX2 SIMD quicksort/select library beating std::sort on primitive arrays and key-derived struct sorts (object_qsort). | **C** | C++ | BSD-3-Clause | 🟢 active |
| 11 | [**libsrt (srt_vector sort)**](faragon-libsrt.md) | C container/string library whose srt_vector sort uses counting sort for 8-bit elements, about 5x faster than libstdc++ std::sort. | **C** | C | BSD-3-Clause | 🟢 active |
| 12 | [**voracious_radix_sort**](lakwet-voracious-sort.md) | Rust MSD/LSD radix-sort crate for primitive types and custom structs, several times faster than Rust's own sort on large arrays. | **C** | Rust | MIT | 🟢 active |
| 13 | [**vergesort**](morwenn-vergesort.md) | Presortedness-detecting merge layer over pdqsort; beats std::sort/std::stable_sort when input has long sorted runs. | **C** | C++ | MIT | 🟢 active |
| 14 | [**Indiesort (plf::indiesort)**](mattreecebentley-plf-indiesort.md) | Indirect sort wrapper: sorts indices or pointers, then permutes once; beats std::sort on structs over \~152 bytes. | **C** | C++ | Zlib | 🟢 active |
| 15 | [**fastcpp::algo::sort / radix_sort (developer source)**](private-developer-source-sorting.md) | Header-only pdqsort-style quicksort and LSD radix sort; 2.3x libstdc++ std::sort on random int64, 6.6x sorted, loses nearly-sorted. | **C** | C++ | MIT | 🟢 active |
| 16 | [**PTMS (Parallel Tournament Merge Sort)**](tylerburger777-ptms.md) | OpenMP-task parallel merge sort for int arrays with AVX2/AVX-512 bitonic base cases; claims about 2.2x over tbb::parallel_sort. | **C** | C++ | MIT | 🟢 active |
| 17 | [**quadsort**](scandum-quadsort.md) | Stable branchless bottom-up adaptive merge sort in C, beating std::stable_sort on random and partially ordered arrays. | **C** | C | Unlicense | 🟡 stale |
| 18 | [**fluxsort**](scandum-fluxsort.md) | Stable branchless quicksort/mergesort hybrid with a qsort-style C interface, claimed \~3x faster than std::stable_sort on random ints. | **C** | C | Unlicense | 🟡 stale |
| 19 | [**blitsort**](scandum-blitsort.md) | In-place, stable, adaptive C sort beating std::stable_sort via rotations instead of an O(n) swap buffer. | **C** | C | Unlicense | 🟡 stale |
| 20 | [**swenson/sort (sort.h)**](swenson-sort.md) | Single C89 header that macro-generates type-specialised quick, heap, tim, merge and shell sorts that beat libc qsort. | **C** | C | MIT | 🟡 stale |
| 21 | [**The Art of Writing Efficient Programs: signed int loop…**](paper-book-the-art-of-writing-efficient-programs-signed-int-loop-index.md) | Book idiom: signed int index in a hand-written string-compare loop beats unsigned-index versions inside a std::sort benchmark. | **C** | C++ | MIT | 🟡 stale |
| 22 | [**crumsort**](scandum-crumsort.md) | Branchless in-place unstable C quicksort/quadsort hybrid, \~1.4-1.5x faster than pdqsort on random 32/64-bit ints. | **C** | C | Unlicense | 🟡 stale |
| 23 | [**Timsort (gfx::timsort, cpp-TimSort)**](gfx-cpp-timsort.md) | Header-only C++20 TimSort and TimSort-merge; beats std::sort/std::stable_sort only on presorted, reversed or run-structured input. | **C** | C++ | MIT | 🟡 stale |
| 24 | [**gridsort**](scandum-gridsort.md) | Stable C sort using a cache-friendly bucketed grid; qsort-compatible interface; 1.4x-2.6x faster than std::stable_sort on 1M-int arrays. | **C** | C | Unlicense | 🟡 stale |
| 25 | [**ska_sort**](skarupke-ska-sort.md) | Header-only radix/American-flag sort beating std::sort by \~2x on ints, floats, structs and strings via key extraction. | **C** | C++ | BSL-1.0 | 🔴 abandoned |
| 26 | [**poor-circle/radix_sort**](poor-circle-radix-sort.md) | Header-only C++20 LSD byte-radix sort for ints/floats/pointers/pairs/structs; drop-in call syntax beats std::sort. | **C** | C++ | GPL-3.0 | 🔴 abandoned |
| 27 | [**vxsort-cpp**](damageboy-vxsort-cpp.md) | AVX2/AVX-512 vectorized quicksort for primitive arrays; beats a ported .NET GC introsort, not std::sort. | **C** | C++ | MIT | 🔴 abandoned |
| 28 | [**Ultra-Sort (SIMD sorting DSL for AVX2 and AVX-512)**](patwinchir-ultra-sort.md) | 2018 course-project AVX-512/AVX2 bitonic merge sort for power-of-two numeric arrays; 7.7x std::sort on 1M 32-bit ints in its own report. | **C** | C++ | MIT | 🔴 abandoned |
| 29 | [**dietlibc (qsort and bsearch)**](ensc-dietlibc.md) | dietlibc's in-place 3-way quicksort and binary search; a 2001 changelog claimed 2.3x and 6.1x fewer cycles than glibc. | **D** | C | GPL-2.0-or-later | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
