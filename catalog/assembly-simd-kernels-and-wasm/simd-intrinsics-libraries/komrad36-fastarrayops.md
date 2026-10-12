# FastArrayOps

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Hand-written AVX2 assembly for find, contains, min/max and argmin/argmax over plain arrays; claims to beat scalar compiler loops.

| | |
|---|---|
| **Beats** | unspecified 'best compiler output' scalar loops (the README headline also says 'compiler or STL', but no std::find / std::min_element / std::max_element baseline code or compiler is identified) |
| **Claimed result** | README table 'Approx. speedup vs. best compiler output' for large n: contains/find 22x (I8/U8), 18x (I16/U16), 12x (I32/U32), 7.0x (I64/U64), 13.0x (float), 7.0x (double); min/max element 2.3x, 2.1x, 1.1x, 1.3x, 28x (float), 14x (double); min/max index 35x, 19x, 8.5x, 3.1x, 8.9x, 5.0x. Headline: 'up to 35x faster than compiler or STL'. |
| **Workload** | AVX2 contains/find, min/max element and min/max index over arrays of I8/U8 to I64/U64, float and double, large n; the README says proportional speedup is higher for small n. |
| **Metric** | throughput |
| **Adoption** | 43 stars, 4 forks, 18 commits |
| **Last commit** | 2025-12-11 |
| **Links** | [repository](https://github.com/komrad36/FastArrayOps) · [benchmark](https://github.com/komrad36/FastArrayOps) |

## Verdict

The only first-party numbers are the README's approximate large-n speedups over unnamed 'best compiler output' scalar loops (contains/find 7-22x, min/max element 1.1-28x, argmin/argmax 3.1-35x) with no CPU, compiler, flags, sizes or benchmark code, measured on code before the 2025-12-11 correctness fix. The one third-party data point (fatihtsp/FastArrayOps Delphi wrapper, 10M elements, CPU unstated) shows FastMin on an Int64 array at 11 ms versus a classical Delphi loop at 13 ms (about 1.2x, derived from page data).

## Use it when

- Hot linear scans over contiguous arrays of plain integers on x86-64 CPUs that are guaranteed to have AVX2, e.g. membership tests on arrays of tens to a few hundred elements instead of a hash set (the README's main argument).
- argmin/argmax over uint8/int8/int16 data, where the README claims its largest gains (35x and 19x) and compilers emit scalar code.
- float/double min/max of data known to be NaN-free when you cannot enable -ffast-math for the whole translation unit.
- Small array-backed priority queues or decrease-key structures whose operations reduce to find/min/argmin, as the README suggests.
- GCC or Clang builds where you have measured std::find or std::min_element as the bottleneck and want a drop-in C ABI routine.

## Skip it when

- Data or queries that can be NaN: the float/double small-n find/contains paths report false matches and min/max/argmin results with NaN depend on element position.
- Any target without AVX2 (no runtime dispatch or scalar fallback, so older x86 crashes with an illegal instruction), and AArch64 or other architectures; no macOS build either (symbols lack the leading underscore Mach-O expects).
- MSVC builds: the MSVC STL already ships runtime-dispatched manual vectorization of find, min_element and max_element (including float and double) on x64/x86 by default, so measure std:: first; the README table is against scalar compiler output, not that.
- Large DRAM-resident arrays, where the scan is memory-bound: a third-party Delphi wrapper timing 10M elements found the classical loop 'not so much different' (int64 min 13 ms vs 11 ms).
- Arrays over 2^32 - 1 elements for the min/max/index routines (uint32_t count), or code that relies on std::min_element's first-index tie rule.

## How it is fast

Large inputs run in 256-byte blocks: contains/find broadcast the query, OR together eight 32-byte vpcmpeq results and test once per block, and min/max keep eight independent vpmin/vminps accumulators; the tail is handled by re-running one overlapping final block rather than a scalar loop. Small inputs (below 32 to 256 elements depending on type) dispatch through a byte jump table to straight-line code for that size class. Argmin/argmax track per-lane best values plus a parallel index vector updated with vpcmpeq + vpblendvb, and the 8- and 16-bit versions nest 8/16/32-bit counters so narrow lanes do not overflow. The float/double min/max kernels reassociate the reduction, which compilers do only under -ffast-math, and that most likely explains the 28x and 14x rows.

## Compared with alternatives

Pick it over argminmax (Rust crate, SSE to AVX-512 and NEON with 3-20x claimed vs scalar) only when you call from C or C++ on AVX2 x86 and also want find/contains for every integer width; over vectorized_find (AVX2 find experiments against std::find) because it covers min/max and argmin/argmax too. On MSVC, try the STL's own vectorized std::find and std::min_element before either.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at runtime; NASM to assemble the Linux/\*.s files (NASM syntax: bits 64, yword, times db), ml64 (MASM) for Windows/\*.asm |
| **Minimum toolchain** | Any C++11 compiler for the header (&lt;cstdint&gt;, extern "C"); NASM or ml64 for the kernels; no build files, tests or CMake in the repo |
| **Platforms** | x86-64 only, AVX2 required (Haswell or later, Zen or later); System V (Linux) and Win64 ABIs |
| **Thread safety** | Not documented; the routines only read caller memory and constant tables and keep no global state, so concurrent calls are safe by construction. |
| **Drop-in for the baseline** | partial: pointer+count C API instead of iterators; find returns an index (\~0ULL when absent) rather than an iterator; min/max index tie-breaking is unspecified (std::min_element returns the first); NaN and empty-array behavior differ |

## Gotchas

- NaN false matches (code bug, both Linux and Windows): FastFindFloat/FastFindDouble for n &lt; 4 and FastContainsFloat/FastContainsDouble for n &lt; 8 compare with vucomiss/vucomisd followed by je/sete/cmove and never check the parity flag, so an unordered compare counts as equal; a NaN element or NaN query reports a match (FastContainsFloat on {NaN, 2, 3} for query 5 returns true; FastFindFloat on {NaN, 1, 2} for query 1 returns 0), while the vector paths for larger n (vcmpeqps, ordered) never match NaN.
- FastMin/FastMax for float and double return an all-ones NaN bit pattern on empty arrays (the accumulator is seeded with vpcmpeqd), not the min/max representable value the README promises; the integer versions do return INT_MAX/INT_MIN-style sentinels.
- None of the 52 kernels executes vzeroupper, so they return with dirty upper YMM state; non-VEX SSE code that runs next (callers built without -mavx/-mavx2) pays AVX-SSE transition or false-dependency penalties on Intel cores, which a microbenchmark loop would not show.
- The Windows MASM procedures that adjust rsp (e.g. sub rsp,104 in FastMinIdxI32.asm) are plain PROCs without FRAME/unwind directives, so a fault inside them cannot be unwound by SEH; the Linux sources are NASM-only and 11 of them still use bare-CR line breaks in their header lines (the 2025-12-11 commit normalized only FastFind64.s).

## Known shortcomings

- No bench driver, CPU, compiler or flags in the repo; the table predates the 2025-12-11 correctness fix (FastFind64 32-bit compare, 16-bit index vpbroadcastd, U8 min-index sentinel 127); the tie index differs from std::min_element.
- Code bug in both the Linux .s and Windows .asm kernels: FastFindFloat/Double for n &lt; 4 and FastContainsFloat/Double for n &lt; 8 use vucomiss/vucomisd with je/sete/cmove and no parity check, so a NaN element or NaN query counts as a match (contains {NaN, 2, 3} query 5 returns true); the vector paths never match NaN. Empty float/double min/max return NaN, not the README's 'min/max representable value'; none of the 52 kernels executes vzeroupper; the Windows procs that adjust rsp have no unwind info; the Linux .s files are NASM syntax, not GAS. MSVC's STL already vectorizes find/min_element/max_element. The only third-party number is the fatihtsp/FastArrayOps Delphi wrapper (a duplicate): 10M int64 min 11 vs 13 ms, about 1.2x.

## Caveats and trade-offs

First-party table with no CPU, compiler, flags, array sizes or timing method, and no benchmark driver in the repo: the Linux/ (GAS .s) and Windows/ (MASM .asm) folders hold only the hand-written x86 AVX2 assembly kernels, and fast-array-ops.h is just extern "C" declarations plus overloads, so the core is assembly, not C++. The 'best compiler output' baseline is not identified. The table dates from 2020-2021; the last commit (2025-12-11, 'bugfix FastFind64, FastIdx16') fixed correctness bugs: FastFind64's small-n path compared only 32 bits (dword cmp instead of qword), the 16-bit min/max-index kernels broadcast the index vector with vpbroadcastd instead of vpbroadcastw, and FastMinIdxU8 started from a 127 sentinel instead of 0xFF, so earlier builds could return wrong results. Min/max index does not guarantee which index is returned on ties, unlike std::min_element/std::max_element, which return the first. Float/double min/max rows (28x, 14x) likely benefit from NaN semantics a compiler must preserve without -ffast-math; NaN handling is not documented. Several rows are small (32-bit integer min/max 1.1x, 64-bit 1.3x). x86-64 AVX2 only. [retier] First-party table with no CPU, compiler, flags, array sizes or timing method, and no benchmark driver in the repo: the Linux/ (NASM-syntax .s, not GAS) and Windows/ (MASM .asm) folders hold only the hand-written x86 AVX2 assembly kernels, and fast-array-ops.h is extern 'C' declarations plus overloads. The 'best compiler output' baseline is not identified; MSVC's STL already vectorizes find, min_element and max_element. The table dates from 2020-2021 and the last commit (2025-12-11) fixed correctness bugs in FastFind64 and the 16-bit min/max-index kernels. Remaining code bugs: FastFindFloat/Double for n &lt; 4 and FastContainsFloat/Double for n &lt; 8 compare with vucomiss/vucomisd followed by je/sete/cmove and never check the parity flag, so a NaN element or NaN query counts as a match (FastContainsFloat on {NaN, 2, 3} for query 5 returns true) while the vector paths never match NaN; FastMin/FastMax for float and double return an all-ones NaN bit pattern on empty arrays, not the README's min/max representable value; none of the 52 kernels executes vzeroupper, so callers built without -mavx pay AVX-SSE transition penalties; the Windows procedures that adjust rsp have no FRAME/unwind directives. The only third-party number is the fatihtsp/FastArrayOps Delphi wrapper: 10M int64 min 11 vs 13 ms, about 1.2x (derived from page data).

x86 AVX2 only; single header fast-array-ops.h with Linux and Windows build folders. Min/max index does not say which index is returned among equal minima; find-element does return the lowest index; empty arrays and not-found return \~0U/\~0ULL. The README argues linear scans beat hash tables or heaps up to hundreds or thousands of elements.

## Maintenance

Dormant from 2021 until a single 2025-12-11 bugfix commit (FastFind64 32-bit compare, 16-bit idx broadcast, U8 min-index sentinel); MIT and copyable, but it ships no tests, benchmark or build files and its float/double small-n paths still mishandle NaN, so vendor it only behind your own tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table ('Approx. speedup vs. best compiler output') with no benchmark code in the repo (only Linux/\*.s, Windows/\*.asm, fast-array-ops.h, LICENSE, README), no CPU, compiler, flags or array sizes; the numbers also predate a 2025-12-11 correctness fix to several kernels, which caps them at C regardless.
- **Verifier notes:** README numbers match the record. No benchmark code exists in the repo, and the table predates the 2025-12-11 fix of real correctness bugs (32-bit compare in FastFind64, wrong broadcast in 16-bit idx kernels, wrong U8 min-index sentinel), so tier C stands with those shortcomings; tie-breaking differs from std::min_element.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/FastArrayOps>
  - <https://github.com/komrad36/FastArrayOps/commits>
  - <https://github.com/komrad36/FastArrayOps/commit/d326fd1>
  - <https://github.com/komrad36/FastArrayOps/tree/master/Linux>
  - <https://github.com/komrad36/FastArrayOps/tree/master/Windows>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/fast-array-ops.h>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/komrad36/FastArrayOps>
  - <https://github.com/komrad36/FastArrayOps/commits>
  - <https://github.com/komrad36/FastArrayOps/commit/d326fd1>
  - <https://github.com/komrad36/FastArrayOps/tree/master/Linux>
  - <https://github.com/komrad36/FastArrayOps/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/fast-array-ops.h>
  - <https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/LICENSE>
  - https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/Linux/ (all 52 .s kernels, e.g. FastContainsFloat.s, FastFindFloat.s, FastFind64.s, FastContains16.s, FastMinFloat.s, FastMinIdxFloat.s, FastMinIdxU8.s)
  - https://raw.githubusercontent.com/komrad36/FastArrayOps/HEAD/Windows/ (all 52 .asm kernels, e.g. FastFindFloat.asm, FastContainsDouble.asm, FastMinIdxI32.asm)
  - <https://github.com/fatihtsp/FastArrayOps>
  - <https://raw.githubusercontent.com/MicrosoftDocs/cpp-docs/main/docs/standard-library/vectorized-stl-algorithms.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/komrad36/fastarrayops`) · [data/wave13/enrich/raw/github_com_komrad36_fastarrayops.json](../../../data/wave13/enrich/raw/github_com_komrad36_fastarrayops.json) (enrichment confidence 0.8)

</details>
