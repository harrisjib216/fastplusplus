# libsrt (srt_vector sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> C container/string library whose srt_vector sort uses counting sort for 8-bit elements, about 5x faster than libstdc++ std::sort.

| | |
|---|---|
| **Beats** | std::sort (GNU/Clang std::vector sort) and C qsort() |
| **Claimed result** | Current README (no numbers): 8-bit elements by counting sort 'up to 5x faster than GNU/Clang std::vector sort (C++)'; 16/32/64-bit elements by MSD binary radix sort '2x-3x faster than GNU/Clang qsort() (C), performing similar to GNU/Clang std::vector sort (C++)'. The author's 2017 tables (doc/benchmarks.md at commit e678325, 64-bit g++ 5.2.1, i5-3330, 1M elements inserted in ascending order then sorted 10 times, insert and cleanup included): libsrt_vector_i8 0.027646 s vs cxx_vector_i8 (std::sort) 0.137919 s, about 5.0x; u8 0.026851 vs 0.150012 s, about 5.6x; i16 0.145145 vs 0.145665 s, 1.0x; u16 0.132487 vs 0.171347 s, 1.29x; i32 0.183137 vs 0.150832 s, libsrt about 0.82x (slower); u32 0.90x; i64 and u64 0.85x (slower); 32-byte generic elements via qsort 1.265519 vs 2.052374 s, 1.62x; reverse-order input gives the same pattern; 100 elements sorted 10000 times: u8 1.85x, i8 1.15x, 16/32/64-bit libsrt 0.65x-0.83x (slower). Ratios derived from page data. No qsort() timings are published, so the 2x-3x versus qsort() has no numbers. |
| **Workload** | examples/bench.cpp (now test/bench.cc): push 1,000,000 elements in ascending (or reversed) order into an srt_vector or std::vector, call sv_sort or std::sort 10 times (9 of the 10 calls sort already-sorted data), cleanup; whole sequence timed. Also 100 elements sorted 10,000 times. 8-bit values wrap to a 256-value sawtooth. No random input is ever timed. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-3330 @3GHz, 6MB L3 (sort tables exist only for the 64-bit x86_64 run; the 32-bit and Allwinner A64 runs have no sort tables). |
| **Compiler and flags** | g++ 5.2.1 on Ubuntu 15.10 x86_64 (64-bit build); the doc only says the bench executable is built with 'make', which at commit e678325 means Makefile.inc defaults -pipe -O2 -fomit-frame-pointer (flags inferred from the public Makefile, not stated on the page). |
| **Adoption** | 558 stars |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/faragon/libsrt) · [benchmark](https://github.com/faragon/libsrt/blob/e678325/doc/benchmarks.md) |

## Verdict

The author's 2017 first-party table (g++ 5.2.1 x86-64, Intel Core i5-3330, Makefile -O2, examples/bench.cpp) times insert 1M ascending values, sort 10 times, free: int8 0.028 s vs libstdc++ std::sort 0.138 s (about 5x) and uint8 about 5.6x, but int16 1.0x, uint16 1.29x and int32/uint32/int64/uint64 0.82-0.90x (libsrt slower); the tables were removed from doc/benchmarks.md in 2018 and never re-run.

## Use it when

- C code that already uses srt_vector and needs to sort int8/uint8 data (histogram-like byte arrays, small enums): counting sort, O(n), correct.
- Embedded or hard real-time C where one allocation per container and predictable O(n) byte sorting matter more than peak speed.
- Code bases that need C89/C99 portability back to GCC 2.95 and big-endian targets, where pulling in a C++ sorter is not an option.

## Skip it when

- Any 16/32/64-bit sort of non-trivially ordered data: the HEAD radix sort returns unsorted output on random input (see gotchas).
- General C++ sorting: the author's own 2017 table had libsrt 10-18% slower than libstdc++ std::sort on 1M int32/int64, and 17-35% slower on 100-element vectors.
- Floats, doubles or structs: these go to qsort(), so there is no speedup over plain C.
- MINIMAL=1 builds (-Os -DS_MINIMAL): every type, including 8-bit, falls back to qsort().
- Concurrent writers: the README says read/write concurrency must be locked by the caller.

## How it is fast

8-bit vectors use an in-place counting sort (256 counters, then memset runs), which is O(n) and beats any comparison sort on byte data. 16/32/64-bit vectors use an in-place MSD binary radix sort: it ORs the XOR of neighbouring keys to find which bits vary, partitions on one bit at a time with a two-pointer swap, and hands partitions of 2-4 elements to small sorting networks. Floats, doubles and generic elements fall through to the C library qsort().

## Compared with alternatives

Only for byte-sized keys inside a C program already built on libsrt; for 16-64-bit integers pdqsort, ska_sort or Boost spreadsort (C++) and crumsort or swenson/sort (C) are faster or at least correct, and vqsort is far ahead on SIMD hardware.

## Integration

| | |
|---|---|
| **Form** | static lib (Makefile.posix, autotools, or the new CMake build, which can also build a shared lib) |
| **Dependencies** | none beyond the C library; requires alloca() |
| **Minimum toolchain** | C99 or C++11 (C89 with __VA_ARGS__ and alloca extensions); README says GCC 2.95.2+ and any Clang |
| **Platforms** | any; README lists tests on x86/x86-64 Linux, Windows (VS), FreeBSD, macOS, ARMv5-v8, MIPS, PowerPC, big and little endian |
| **Thread safety** | concurrent reads are safe; concurrent read/write must be locked by the caller (README) |
| **Drop-in for the baseline** | partial: sv_sort works only on libsrt srt_vector objects; ssort_i8/ssort_u8 in src/saux/ssort.h take a raw array and are safe to call directly, the 16/32/64-bit ssort_\* functions are not (correctness bug) |

## Gotchas

- Correctness bug 1 (HEAD src/saux/ssort.c): BUILD_SORT3 never compares b[1] with b[2] and BUILD_SORT4 is not a valid network, so [1,3,2] stays unsorted and [3,4,1,2] becomes [1,3,2,4]. A hand-written C reproduction of the HEAD macros (compiled with gcc -O2 this session, not the project build) left 114,986 of 1,000,000 random uint32 positions wrong (57,493 descents), about 11.5% for int32 and uint64 too, every one of 1,000 random 100-element uint32 arrays unsorted, and 106 of 1,000 random uint16.
- Correctness bug 2 (HEAD src/saux/scommon.h BUILD_S_MSB): the bit-smear loop stops one shift short (i &lt; bits/2), so s_msb32(0x80000001) returns 0x80000001 and s_msb64((1&lt;&lt;40)|2) returns two bits. The radix sort then partitions on two bits at once: uint32 [0,0x20000,1,0x20001] comes back unchanged, and 1M uint64 keys drawn from {0..7} and {2^40+0..7} came out 67% misplaced in the reproduction. Clustered keys (for example IDs plus a large offset) trigger it even when the sorting networks are not reached. The same loop (i &lt; NBITS / 2) was already in scommon.h at the 2017 benchmark commit e678325.
- Both bugs hide from the project's own checks: test/bench.cc only times ascending or reversed input (then re-sorts sorted data 9 times), and stest.c sorts a 9-element three-value vector and evens-then-odds 0..999, all of which come out sorted. Random 16-bit input of 1M elements also happens to sort correctly because duplicates keep partitions large.
- The timed rows include vector insertion and cleanup, and for 8-bit the bench pushes (int32_t)i, so it sorts a 256-value sawtooth; no random input is ever timed for either side.

## Known shortcomings

- Claim overstated: the only real numbers are the author's 2017 tables (doc/benchmarks.md at commit e678325, g++ 5.2.1, i5-3330, -O2, removed from the doc in 2018): 8-bit counting sort about 5.0x (i8) and 5.6x (u8) vs libstdc++ std::sort, while 32/64-bit libsrt sorts run 0.82-0.90x, i.e. slower. Correctness bug: HEAD src/saux/ssort.c 3- and 4-element sort networks are wrong (hand trace of [1,3,2,8,9,10,11,12] comes out unsorted; a Python port misplaces 114,854 of 1M random 32-bit values); the bench and stest.c use only ascending, reversed or evens-then-odds input so it never shows; the 2017 SORT4 read past its 4-element block. The counting-sort win does not run through the buggy networks, so kept at C with the bug documented.
- Enricher: second sort bug: s_msb16/32/64 in scommon.h (BUILD_S_MSB) stop one shift short (i &lt; bits/2), so s_msb32(0x80000001) returns 0x80000001 and the radix sort splits on two bits at once (uint32 [0,0x20000,1,0x20001] comes back unchanged; uint64 clusters 2^40 apart: 666,585 of 1M misplaced), already present in the 2017 benchmark code (e678325); the SORT3/SORT4 network bug reproduced with a C copy of the HEAD macros (114,986 of 1M random uint32 misplaced, all 1,000 random 100-element arrays unsorted). Only the 8-bit counting sort is usable; ssort.c untouched since 2019, no issue filed upstream.

## Caveats and trade-offs

First-party only. The README claim has no numbers; the only timings are 2017 tables (doc/benchmarks.md at commit e678325) that the author removed from the doc in January 2018 and never re-ran on the current code. Those tables support the 8-bit counting-sort claim (about 5x on i8, 5.6x on u8 against libstdc++ std::sort, an O(n) counting sort against a comparison sort), but contradict 'performing similar to std::vector sort' for 32/64-bit: libsrt was 10-18% slower there, and 16/32/64-bit was 17-35% slower on 100-element vectors. The benchmark only sorts ascending or reversed input and re-sorts already-sorted data 9 times, and the time includes insertion and cleanup. Correctness bug: the 3-element and 4-element sorting networks used by the 16/32/64-bit MSD radix sort in src/saux/ssort.c are wrong at HEAD. BUILD_SORT3 leaves [1,3,2] unchanged, BUILD_SORT4 turns [3,4,1,2] into [1,3,2,4], and sv_sort on the i32 vector [1,3,2,8,9,10,11,12] returns it unsorted (hand trace). A Python port of the HEAD algorithm misplaces 114,854 of 1,000,000 random 32-bit values, while ascending, reversed and evens-then-odds inputs (the only ones the bench and stest.c use) come out sorted. This was checked on a port, not the compiled C. The 2017 code that produced the tables had a different BUILD_SORT4 that swaps b[0]/b[3] and b[1]/b[4], reading past a 4-element block. 8-bit counting sort is correct. Generic elements fall back to qsort(). Lead URL faragon.github.io/libsrt.html is API docs only (checked via the faragon/faragon.github.io repo). Filed under sorting; the project is a general C data-structure and string library. [retier] 8-bit counting sort about 5.0-5.6x vs libstdc++ std::sort (2017 tables, g++ 5.2.1, i5-3330, -O2); 32/64-bit libsrt sorts 0.82-0.90x and incorrect (s_msb stops one shift short; SORT3/SORT4 networks wrong); bench and stest use only ascending, reversed or evens-then-odds input; ssort.c untouched since 2019; no upstream issue filed.

C library with its own string, vector, bitset, set, map and hash map types; vector sort is only specialised for 8, 16, 32 and 64-bit element types, generic elements fall back to qsort(); concurrent read/write needs user locking; maps keep nodes in one linear block with index links; deletion is slower than insertion.

## Maintenance

BSD-3-Clause, 558 stars, self-described beta; sporadic maintenance (three commits on 2026-08-02 after a gap since September 2021, ssort.c untouched since January 2019) and no issue filed about the sort bugs, so treat only the 8-bit counting sort as usable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** The current README only states 'up to 5x faster than GNU/Clang std::vector sort' for 8-bit elements with no table or method; the only timings are first-party tables in doc/benchmarks.md at commit e678325 (Jan 2017, removed from the doc in Jan 2018): g++ 5.2.1 x86_64, Intel Core i5-3330, Makefile default -O2, code examples/bench.cpp at that commit. That would be reproducible, but the measured 2017 radix-sort code had a 4-element sorting network that indexes b[4] (out of bounds) and was later rewritten, and the 16/32/64-bit path is still incorrect at HEAD, so the numbers-on-later-fixed-code rule caps it at C.
- **Verifier notes:** Keep with shortcomings: the 8-bit counting-sort 5x against libstdc++ std::sort is backed by the author's 2017 table (g++ 5.2.1, i5-3330), but 16/32/64-bit libsrt was slower than std::sort in that same table, and the HEAD radix sort's 3- and 4-element networks produce unsorted output on random input (found by hand trace and a Python port, not a compiled run; the bench and unit tests only use sorted, reversed or evens-then-odds input). Not a reject because the headline 8-bit path is correct and the timed runs sorted correctly. Metadata checked: BSD-3-Clause, 558 stars, not a fork, last commit 2026-08-02, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline_stdlib`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 11); enricher w11 pair-024
- **Pages the verifier opened:**
  - <https://github.com/faragon/libsrt>
  - <https://github.com/faragon/libsrt/commits>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/README.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/Makefile.posix>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/test/bench.cc>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/test/stest.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/saux/ssort.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/svector.c>
  - <https://github.com/faragon/libsrt/commits/master/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/doc/benchmarks.md>
  - <https://github.com/faragon/libsrt/blob/e678325/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/Makefile>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/Makefile.inc>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/examples/bench.cpp>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/src/saux/ssort.c>
  - <https://github.com/faragon/libsrt/commit/3dc7ec9>
  - <https://github.com/faragon/libsrt/tree/master/doc>
  - <https://github.com/faragon/libsrt/issues?q=sort>
  - <https://raw.githubusercontent.com/faragon/faragon.github.io/HEAD/libsrt.html>
- **Sources the enricher read:**
  - <https://github.com/faragon/libsrt>
  - <https://github.com/faragon/libsrt/commits>
  - <https://github.com/faragon/libsrt/commits/master/src/saux/ssort.c>
  - <https://github.com/faragon/libsrt/issues>
  - <https://github.com/faragon/libsrt/issues?q=is%3Aissue+sort>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/README.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/saux/ssort.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/saux/ssort.h>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/saux/scommon.h>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/svector.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/svector.h>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/src/libsrt.h>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/test/bench.cc>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/test/stest.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/Makefile.posix>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/src/saux/ssort.c>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/src/saux/scommon.h>
  - <https://raw.githubusercontent.com/faragon/libsrt/e678325/examples/bench.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/faragon/libsrt`) · [data/wave11/enrich/raw/github_com_faragon_libsrt.json](../../../data/wave11/enrich/raw/github_com_faragon_libsrt.json) (enrichment confidence 0.8)

</details>
