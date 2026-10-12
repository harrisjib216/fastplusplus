# EASTL string (eastl::basic_string / eastl::string, eastl::fixed_string)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> EA's non-COW, SSO basic_string and inline-buffer fixed_string; beat the VC++ 7.1 Dinkumware string on push_back and swap.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | EASTL 0.96 release table vs VC++ 7.1 (Dinkumware) std::basic_string (ratio = std time / EASTL time, above 1 means EASTL faster). string&lt;char8_t&gt;: push_back 10.41x, reserve 10.73x, swap 3.48x, operator[] 2.61x, find_first_of 2.23x, find_last_of 1.60x, rfind 1.32x. string&lt;char16_t&gt;: push_back 14.30x, reserve 4.87x, swap 3.48x, operator[] 2.98x, find 2.43x, compare 1.73x. Slower: char8_t find 0.74x and compare 0.82x. About 1.0x for erase, insert, replace, iteration and size. |
| **Workload** | Stopwatch (CPU cycles) comparison of eastl::basic_string against std::basic_string for 8-bit and char16_t strings, both pre-sized to 16 characters so initial reserve differences are removed, timing push_back, insert, erase, replace, reserve, operator[], the find family, compare, swap and iteration. |
| **Metric** | throughput |
| **Hardware** | doc/Benchmarks.md gives no CPU. N2271 lists Pentium 4 x86 for the Windows and Linux columns, without an exact model. |
| **Compiler and flags** | doc/Benchmarks.md: Microsoft Visual C++ 7.1 (version 1310), Release 'Full optimization. Inlining enabled.' (exact flags not given), PPMalloc::GeneralAllocator, thread safety enabled; also a VC++ 7.1 + STLport column. N2271 appendix 20: Windows column VC8 -Og -Oi -Ot -Oy -Ob2 -GF -Gy with the compiler-supplied STL; console column VC7 -Ox -Ob2 -Oi -Os on 64-bit PowerPC; Linux column GCC 4.1 -O3 with libstdc++; Mac column GCC 4.0 -Os with libstdc++ on a G5. |
| **Adoption** | 9.4k stars, 1.0k forks; Electronic Arts' in-house STL replacement, open-sourced |
| **Last commit** | 2025-10-29 |
| **Links** | [repository](https://github.com/electronicarts/EASTL) · [benchmark](https://github.com/electronicarts/EASTL/blob/master/doc/Benchmarks.md) |

## Verdict

doc/Benchmarks.md (EASTL 0.96, Windows x86, VC++ 7.1 Release, PPMalloc, no CPU model) times one loop per operation on strings pre-sized to 16 characters: against the Dinkumware string, push_back was 10.41x (char) and 14.30x (char16_t) faster and swap 3.48x, reserve 10.73x and 4.87x only because EASTL ignores shrink requests, while char find (0.74x) and compare (0.82x) were slower. EASTL's own times for identical code differ between the Dinkumware and STLport tables by up to 1.72x (char16_t compare 251,985,824 vs 432,760,228 cycles; find 165,298,157 vs 225,830,975), as large as many of the claimed ratios (derived from page data).

## Use it when

- Game, console or embedded code that already builds against EASTL and wants one string type with named allocators and exceptions disabled
- Debug builds where std::string overhead hurts: the VC7.1 Debug table shows char push_back 8.95x and iteration 11.05x over the Debug std::string (but find 0.26x)
- Bounded-length strings (names, paths, keys) kept inside an object or on the stack: fixed_string with a nodeCount that covers the common case
- You need set_capacity/force_size-style control over the buffer, such as writing into it with a C API and then fixing the size

## Skip it when

- Expecting a speedup over today's libstdc++, libc++ or MSVC std::string: no published comparison against them exists, and the baselines measured were the VC++ 7.1 Dinkumware string, STLport and GCC 4.1 libstdc++; against STLport (Release) most rows were 1.00x and char16_t compare and swap were slower (0.82x, 0.90x)
- Substring-search-heavy code: find(p, pos, n) is a plain eastl::search loop; char find was 0.74x against the VC++ 7.1 Dinkumware string in Release and 0.26x in Debug
- Code that mostly talks to std::string APIs: every crossing copies, and fixed_string is a different type again because its allocator is a template argument
- Small fixed_string with overflow enabled (roughly nodeCount 12 or less for char on 64-bit): the open overflow bug #454 corrupts the contents (see gotchas)
- Wide characters needing long inline strings: SSO holds only 11 char16_t or 5 char32_t

## How it is fast

Today's string keeps a short-string buffer inside the 24-byte (64-bit) three-word object: 23 chars for char, 11 for char16_t, 5 for char32_t. It never does copy-on-write, uses raw pointers as iterators, hand-inlines begin()/size() for debug builds, has no char_traits layer, and grows capacity by 2x. fixed_string avoids heap allocation altogether while it fits. The published EASTL 0.96 gains (push_back 10-14x, swap 3.5x) were measured on the 0.96 implementation against the Dinkumware VC7.1 string, not on this layout.

## Compared with alternatives

Pick it if you are already on EASTL and want a whole std-like string family (string, fixed_string, string16/32) with custom allocators and no exceptions. For a single fixed-capacity string without EASTL, ETL's etl::string offers the same inline-buffer idea with a truncation flag instead of a heap spill; for faster number-to-string or comparison helpers, to_static_string or MengRao/str target those operations directly.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | EABase (CMake FetchContent); in the default configuration the application must define EASTL's two operator new[] overloads (doc/FAQ.md Info.15) |
| **Minimum toolchain** | C++14 (CMakeLists.txt: cxx_std_14); the benchmark suite does not compile with C++20 char8_t enabled (benchmark/CMakeLists.txt) |
| **Platforms** | any; the SSO flag bit is the MSB of the capacity on little-endian and the LSB on big-endian targets |
| **Thread safety** | doc/FAQ.md: like std containers, a string instance is not safe for concurrent modification; reads from several threads are fine; a shared allocator needs its own locking |
| **Drop-in for the baseline** | partial — the std::basic_string member set is mostly present, but it is a different type (no char_traits, size_type is eastl_size_t, substr copies the allocator), reserve never shrinks, and the char\* constructor is implicit unless EASTL_STRING_EXPLICIT is set |

## Gotchas

- fixed_string overflow bug, issue #454 (open since 2021-12-17, no maintainer reply): fixed_string starts in the heap layout, so when a small one grows to a new capacity that still fits the SSO buffer, set_capacity takes its 'heap-&gt;sso' shrink path, copies n = new-capacity characters out of the smaller inline buffer (an out-of-bounds read) and sets the size to n; the HEAD code still has that path. fixed_string&lt;char, 8&gt; appended one char at a time stops at 'abbbbbb' in the issue's repro.
- fixed_string::swap uses fixed_swap, which moves contents instead of swapping pointers and, for objects of EASTL_MAX_STACK_USAGE bytes or more, heap-allocates a temporary; comparing a fixed_string with nullptr segfaults in CharStrlen (issue #546, open).
- reserve(n) never shrinks (C++20 semantics); use set_capacity or shrink_to_fit to release memory. The char\* constructor is implicit by default, so passing a literal to a const string& parameter builds a temporary (doc/Gotchas.md).
- Harness behind the published rows (benchmark/source/BenchmarkString.cpp, today's version): the 7-element pattern arrays pFind1_8/pFind1_16 have no terminating zero but go to insert(pos, const T\*), which runs CharStrlen past the array (undefined behaviour); a guard that is true only on MinGW with non-Clang compilers skips the pattern insert into the std::basic_string&lt;char16_t&gt;, so on MSVC, GCC/Linux and Clang the char16_t find, rfind, \*_of and compare rows search different strings; the reserve rows reward ignoring shrink requests; and each row is one timed loop with no repeats.

## Known shortcomings

- First-party 2005-07 numbers (doc/Benchmarks.md VC7.1 Release table and N2271, VC8 flags -Og -Oi -Ot -Oy -Ob2 -GF -Gy) against Dinkumware, STLport and libstdc++ 4.1 COW strings; the reserve wins come from the harness sending shrink requests that EASTL ignores; vs STLport about 1.0x except push_back 1.33x; 16-char pre-size means SSO was never measured; no fixed_string numbers.
- Enricher: in today's BenchmarkString.cpp pFind1_8/pFind1_16 lack a terminating zero yet reach insert(pos, const T\*), so CharStrlen reads out of bounds (UB); a guard true only on MinGW non-Clang skips the pattern insert into the std char16_t string, so the char16_t find/rfind/\*_of/compare rows search different strings; EASTL's own timings drift up to 1.72x between the two release tables (char16_t compare 251,985,824 vs 432,760,228 cycles); the fixed_string overflow corruption bug #454 (heap-to-SSO path, out-of-bounds read) is still in HEAD; basic_string&lt;T, Allocator&gt; takes the allocator as a template argument, so fixed_string is a distinct type.

## Caveats and trade-offs

The only published tables are doc/Benchmarks.md (EASTL version 0.96.00, Windows x86, Microsoft Visual C++ 7.1 with the Dinkumware STL or STLport, custom PPMalloc allocator, no CPU model stated) and the 2007 WG21 paper N2271 (doc/EASTL-n2271.pdf, written by EASTL's author), so all numbers are first-party and roughly 20 years old. Ratios are other-STL time divided by EASTL time from a single stopwatch run in CPU cycles, with no variance reported, and the ratio printer caps at 100.00 (the STLport and N2271 Linux/Mac reserve rows read exactly 100.00; e.g. STLport char8_t reserve is 672517501 vs 78387 cycles). The reserve rows (10.73x char8_t, 4.87x char16_t vs Dinkumware) measure a semantic difference rather than a faster reserve: benchmark/source/BenchmarkString.cpp calls reserve with capacity-2 .. capacity+1 in rotation, which the old Dinkumware, STLport and libstdc++ strings honoured as shrink or regrow requests (reallocating), while EASTL's reserve never shrinks. Against STLport in Release the string gains mostly vanish: push_back 1.33x/1.34x, find_first_not_of 2.41x/2.30x, find/find_first_of/find_last_of/operator[] about 1.00x, and char16_t compare 0.82x and swap 0.90x (EASTL slower). The harness pre-sizes every string to 16 characters, so it does not measure the small-string optimization that today's include/EASTL/string.h has (SSOLayout); the published rows describe the 0.96 implementation, not today's code. The baselines are the 2005 Dinkumware string, STLport and, in N2271's Linux column, the copy-on-write std::string of libstdc++ 4.1 (GCC 4.1 -O3), none of which is a modern libstdc++ new-ABI, libc++ or current MSVC string, so the speedups are probably much smaller today. N2271 Linux column (Pentium 4, GCC 4.1 -O3): char8_t push_back 2.28x, find 5.06x, find_first_of 10.11x, find_last_of 8.27x, rfind 8.70x, insert 0.77x. N2271 Windows column (VC8): char8_t push_back 2.28x but find 0.58x. char8_t in the benchmark source is EABase's 8-bit char typedef (the suite does not compile with C++20 char8_t, see benchmark/CMakeLists.txt). eastl::fixed_string has no published numbers. No comparison against folly fbstring exists in the repo, and no independent eastl::string vs std::string measurement was found (one WebSearch; a Stack Overflow anecdote reports EASTL slower for push_back of short strings into a vector, without methodology).

Current string.h implements the short string optimization inside the 3-pointer object: capacity (sizeof(HeapLayout)-1)/sizeof(char), i.e. 23 chars on 64-bit. Non-copy-on-write. The allocator is an instance member with a debug name, not a template argument of the type, so strings with different allocators share one type. eastl::fixed_string&lt;T, N, bEnableOverflow=true&gt; keeps N characters inline and falls back to the heap if allowed. A different type from std::string, so conversions at API boundaries copy. The default allocator needs the application to supply EASTL's operator new[] overloads.

## Maintenance

EASTL is actively maintained (BSD-3-Clause, 9.4k stars), but its string evidence is a single-run EASTL 0.96 table against Dinkumware/STLport. This enrichment found harness flaws the verifier did not record: an out-of-bounds read from unterminated pattern arrays, a MinGW-only guard that leaves the std char16_t string without the search pattern, and up to 1.72x run-to-run drift in EASTL's own timings. fixed_string carries an open heap-to-SSO overflow corruption bug (#454).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/Benchmarks.md (Win32.VC71.MS.Release table, EASTL 0.96.00) is a first-party EA table against the VC++ 7.1 Dinkumware std::basic_string, and every claimed ratio appears in it; no CPU model, exact flags or variance are given. N2271 (also first-party, by EASTL's author) names flags but only the CPU family (Pentium 4), and the 0.96-era harness is not the code in today's repo, so it falls short of A.
- **Verifier notes:** All claimed ratios match the Win32.VC71.MS.Release table and the N2271 Linux column exactly. Shortcomings to record: first-party 2005-2007 numbers against Dinkumware/STLport/libstdc++ 4.1 COW strings; the biggest reserve wins come from a harness that issues shrink requests EASTL ignores; gains vs STLport Release are about 1.0x except push_back (1.33x) and find_first_not_of (2.4x); harness pre-sizes to 16 chars so SSO is not measured. Metadata checked: BSD-3-Clause, 9.4k stars, 1.0k forks, last commit 2025-10-29 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/commits/master>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/EASTL-n2271.pdf>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkString.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/string.h>
- **Sources the enricher read:**
  - <https://github.com/electronicarts/EASTL>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/README.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/string.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/fixed_string.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/internal/fixed_pool.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/internal/config.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkString.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/EASTL-n2271.pdf>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/FAQ.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Gotchas.md>
  - <https://github.com/electronicarts/EASTL/issues?q=is%3Aissue+string+is%3Aopen>
  - <https://github.com/electronicarts/EASTL/issues/454>
  - <https://github.com/electronicarts/EASTL/issues/546>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:eastl-string-fixed-string`) · [data/wave1/enrich/raw/paper_eastl_string_fixed_string.json](../../../data/wave1/enrich/raw/paper_eastl_string_fixed_string.json) (enrichment confidence 0.7)

</details>
