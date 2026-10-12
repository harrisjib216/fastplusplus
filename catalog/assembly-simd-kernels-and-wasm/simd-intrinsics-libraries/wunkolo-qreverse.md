# qReverse

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only SIMD/bswap array reversal for 1-16-byte elements; 8-16x faster than scalar libstdc++ std::reverse on bytes.

| | |
|---|---|
| **Beats** | std::reverse (serial element-swapping reversal) |
| **Claimed result** | i3-6100, g++ -m64 -Ofast -march=native, 1-byte elements vs std::reverse: 1000 elements 290 ns vs 36 ns (8.1x); 10000: 2740 vs 191 ns (14.3x); 100000: 27511 vs 1739 ns (15.8x); 1,000,000: 279525 vs 24710 ns (11.3x); 8 elements 19 vs 19 ns (1.0x). The 'bswap' and 'AVX2' tables are nearly identical (191 vs 189 ns, 875 vs 875 ns) and the bswap row is below the 8-byte store floor, so the x15.8 most likely measured the AVX2 path that -march=native also compiles; SSSE3 peaks at 10.5x and AVX2 at 16.1x (100000 elements). AVX512 on i9-7900x (VS2017 x64 Release) 22.4x at 100000 elements, against an MSVC STL that has since vectorised std::reverse. |
| **Workload** | Reversing arrays of 1-byte elements (ELEMENTSIZE=1 struct of one uint8_t) of 8 to 1,000,000 elements; each size gets 10,000 back-to-back reversals of the same in-cache array, each call timed individually with high_resolution_clock and averaged, std::reverse vs qReverse&lt;1&gt;. |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-6100 (8 GB DDR4), Core i9-7900X, Core i5-8600K, Xeon E5-2697 v4, Broadcom BCM2837 (Raspberry Pi) |
| **Compiler and flags** | i3-6100 run: g++ -m64 -Ofast -march=native; i9-7900X AVX-512 run: Visual Studio 2017 x64 Release |
| **Adoption** | 181 stars |
| **Last commit** | 2018-12-19 |
| **Links** | [repository](https://github.com/Wunkolo/qreverse) · [benchmark](https://github.com/Wunkolo/qreverse) |

## Verdict

On an i3-6100 (Skylake, 3.7 GHz) built with g++ -m64 -Ofast -march=native (GCC version unstated), qReverse&lt;1&gt; reversed in-cache byte arrays 8-16x faster than scalar libstdc++ std::reverse at 1,000-100,000 elements (2,740 vs 191 ns at 10,000) and 11.3x at 1,000,000, with no gain at 8-32 elements; an MSVC 2017 build on an i9-7900X peaked at 22.4x at 10,000 against the then-scalar MSVC STL. Each figure is the mean of 10,000 individually timed calls on the same zero-filled array, measured in October 2018 just before a performance-only fix to the later loops' block counters; only 1-byte elements are tabulated, and the bswap, SSSE3 and AVX2 columns probably do not each isolate one instruction set (see gotchas).

## Use it when

- Reversing large contiguous byte buffers (roughly 1,000 to 1,000,000 uint8_t, e.g. flipping raw rows or byte strings) where your toolchain's std::reverse is still a scalar loop (GCC/libstdc++ in the measured setup; check your own compiler's output first).
- Builds for a known ISA (-march=native, a fixed -mavx2 or AVX-512 fleet, ARM NEON boards) where compile-time ISA selection is acceptable.
- 2, 4 and 8-byte trivially copyable arrays (uint16_t, int32_t/float, uint64_t/double) only after measuring: the README tabulates 1-byte elements alone and a user report shows no gain or a loss at wider sizes.
- As a worked teaching example of shuffle-based reversal: the README walks each ISA step with intrinsics and emitted assembly.

## Skip it when

- 16-byte elements on any AVX2 build: the AVX2 path scrambles element contents (see gotchas).
- Current MSVC: microsoft/STL now ships a runtime-dispatched AVX2/SSE4.2 std::reverse for 1, 2, 4 and 8-byte trivially swappable types (__std_reverse_trivially_swappable_N in stl/src/vector_algorithms.cpp), so the VS2017 22.4x baseline is obsolete.
- 2/4/8-byte elements without your own benchmark: issue #2 (Clang 6, SSSE3, CPU not stated, 2019) measured 4,348 vs 3,911 ns at 10,000 uint16_t, 9,114 vs 3,962 ns for uint32_t and 18,955 vs 4,468 ns for uint64_t (qReverse vs std::reverse), closed by the reporter with no explanation.
- Portable x86-64 binaries for unknown CPUs: without runtime dispatch you either compile with -mavx2 (illegal instruction on older CPUs) or get only the bswap path, since baseline x86-64 has no SSSE3.
- Tiny arrays (8-32 bytes: 1.0-1.3x, within per-call timer overhead), non-trivially-copyable types, iterator-based generic code, or anything needing a maintained dependency (no commits since 2018-12-19).

## How it is fast

Instead of swapping one element pair per iteration, it loads a full vector from each end, reverses it in-register and stores it at the opposite end: pshufb (SSSE3), vpshufb plus a vperm2i128 lane swap (AVX2), vpshufb plus vpermq (AVX-512BW), vrev64q plus vext (NEON). The loops form a greedy cascade (widest vector first, then 64/32/16-bit bswap loops, then a scalar tail), and the ISA is chosen at compile time from predefined macros (__AVX512BW__, __AVX2__, __SSSE3__, __ARM_NEON) with no runtime dispatch. The scalar libstdc++ std::reverse it beats moves one byte pair per iteration and is bound by one store per cycle.

## Compared with alternatives

No sibling reverses arrays; vectorized_find, FastArrayOps and Leftpack are comparable single-purpose SIMD kernels for find, min/max and left-packing. Pick qReverse when std::reverse on byte (or, after measuring, 2/4/8-byte) buffers is a hot spot under GCC or Clang; on current MSVC the STL's own vectorized std::reverse covers the same ground.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard headers plus x86intrin.h or arm_neon.h) |
| **Minimum toolchain** | C++11 (CMakeLists.txt sets CMAKE_CXX_STANDARD 11); GCC or Clang with -mssse3/-mavx2/-mavx512bw or -march=native to enable the SIMD paths; MSVC support is fragile (see gotchas) |
| **Platforms** | x86/x86-64 (SSSE3, AVX2 and AVX-512F+BW paths, compile-time selected), 32/64-bit ARM with NEON, portable shift-and-mask fallback elsewhere |
| **Thread safety** | not documented; the function keeps no state and writes only the caller's buffer, so concurrent calls on disjoint arrays are safe |
| **Drop-in for the baseline** | partial — takes (void\*, element count) plus the element size as a template argument instead of iterators, and is only valid for trivially copyable contiguous data |

## Gotchas

- Correctness bug (code reading, not executed): the qReverse&lt;16&gt; AVX2 loop calls _mm256_permute4x64_epi64(x, _MM_SHUFFLE(0,1,2,3)), which reverses all four 64-bit quadwords, so besides swapping the two 16-byte elements it also swaps the two 8-byte halves inside each element; the correct mask is _MM_SHUFFLE(1,0,3,2) (the AVX-512 path's _mm512_set_epi64(1,0,3,2,5,4,7,6) is right). tests/verify.cpp fills every byte of an element with the same value, so the half-swap is invisible and the Verify16 CTest cases pass. Every AVX2-enabled build corrupts 16-byte elements; the benchmarked 1-byte numbers are unaffected.
- The per-ISA tables do not isolate the ISA: the i3-6100 'bswap' and 'AVX2' tables are nearly identical row by row (191 vs 189 ns at 10,000; 1,739 vs 1,714 at 100,000; 127 vs 127 at 6,133; 875 vs 875 at 50,432), the header compiles its AVX2 loop whenever -march=native defines __AVX2__, and 191 ns for 10,000 bytes is below the floor for 8-byte bswap stores at one store per cycle (about 338 ns at the i3-6100's fixed 3.7 GHz), while std::reverse's 2,740 ns matches one byte store per cycle (about 2,703 ns) (derived from page data). The 'bswap x15.8' column is most likely the AVX2 path, not a bswap-only result.
- MSVC: the header's x86 branch tests __i386__/__x86_64__, which MSVC does not define, so MSVC builds fall through to the shift-and-mask Swap functions and include no intrinsics header (the SIMD paths then rely on intrinsics declared by some other include); MSVC does not traditionally define __SSSE3__, and CMakeLists.txt passes only /arch:AVX2, so reproducing the i9-7900X AVX-512 table needs /arch:AVX512 added by hand (its flags are not stated).
- The bswap and scalar tail loops dereference the caller's buffer through uint16_t\*/uint32_t\*/uint64_t\* at arbitrary byte offsets (misaligned, type-punned access, undefined behaviour in ISO C++): it works with GCC/Clang/MSVC on x86 and ARMv8, but UBSan's alignment check fires, and float or struct arrays reinterpreted as integers can in principle be reordered by type-based alias analysis when the call is inlined.

## Known shortcomings

- g++ version unstated, 2018 numbers, small-size rows mostly clock overhead, no output check in the bench; the i9 AVX-512 table was built with VS2017 (MSVC STL); other CPUs' speedups have no table behind them; three std::reverse tables, not only bswap; abandoned.
- qReverse&lt;16&gt;'s AVX2 path uses _mm256_permute4x64_epi64(x, _MM_SHUFFLE(0,1,2,3)) instead of _MM_SHUFFLE(1,0,3,2), so it also swaps the two 8-byte halves inside every 16-byte element; tests/verify.cpp fills each element with one byte value and cannot see it (1-byte rows unaffected). The i3-6100 bswap and AVX2 tables are nearly identical row by row (191 vs 189 ns, 875 vs 875 ns) and the bswap row sits below the 8-byte store floor, so the headline 'bswap x15.8' most likely timed the AVX2 path that -march=native also compiles in. MSVC's STL now vectorises std::reverse (the VS2017 22.4x baseline is obsolete), the header keys on __x86_64__ which MSVC never defines, issue #2 reports no gain or 2-4x slowdowns for 2/4/8-byte elements on Clang 6, and the bswap loops type-pun (UB).

## Caveats and trade-offs

Numbers are from 2017-2018 (last README benchmark update 2018-10-30) with an unstated g++ version; newer GCC/Clang may vectorize std::reverse better. Per-call timing with high_resolution_clock means rows under about 30 ns are dominated by clock overhead (8 elements: 19 ns vs 19 ns). The benchmark does not check the reversed output (correctness is covered by the separate tests/verify.cpp). The AVX512 table on i9-7900x was built with Visual Studio 2017 x64-Release (MSVC STL baseline, exact flags not given); the i5-8600K, E5-2697 v4 and Raspberry Pi BCM2837 speedups are listed without tables or flags. Only 1-byte elements are tabulated, although the harness supports 1, 2, 4, 8 and 16-byte elements. Abandoned since 2018-12-19. [retier] Numbers are from 2017-2018 (last README benchmark update 2018-10-30) with an unstated g++ version. Per-call timing with high_resolution_clock means rows under about 30 ns are clock overhead. The benchmark does not check the reversed output. Correctness bug (code reading): qReverse&lt;16&gt;'s AVX2 loop uses _mm256_permute4x64_epi64(x, _MM_SHUFFLE(0,1,2,3)) instead of _MM_SHUFFLE(1,0,3,2), so it also swaps the two 8-byte halves inside every 16-byte element; tests/verify.cpp fills each element with one byte value and cannot see it (1-byte rows unaffected). Under -march=native the header compiles its AVX2 loop too, and the bswap and AVX2 tables on the i3-6100 agree row by row, so the bswap column likely timed AVX2. MSVC's STL now vectorises std::reverse (VS2017 22.4x obsolete); the x86 branch keys on __x86_64__, which MSVC never defines; issue #2 reports no gain or 2-4x slowdowns for 2/4/8-byte elements on Clang 6; the bswap loops type-pun (UB).

Per-architecture intrinsic kernels (SSSE3, AVX2, AVX-512BW, NEON) plus a bswap-based path; treats elements as raw bytes, so only suitable for trivially copyable element types. Headers only (include/), CMake build.

## Maintenance

Abandoned since 2018-12-19 (last code change 2018-10-29) but MIT-licensed and a single \~900-line header that is easy to vendor; fix the 16-byte AVX2 shuffle mask and make tests/verify.cpp check bytes inside elements before relying on it, and on current MSVC prefer std::reverse.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README tables time qReverse against std::reverse with the public harness tests/benchmark.cpp (CMakeLists.txt builds it with -march=native -Ofast for GCC), on an Intel Core i3-6100 compiled with g++ -m64 -Ofast -march=native. The g++ version is not stated, which weakens but does not remove reproducibility.
- **Retiered** A to C: Enricher: the i3-6100 bswap and AVX2 tables are nearly identical row by row and the bswap row is below the 8-byte store floor, so the headline 'bswap x15.8' most likely timed the AVX2 path (mislabelled column); the 16-byte AVX2 path has a wrong shuffle mask; the VS2017 MSVC baseline is obsolete. Mislabelled-measurement precedent: A to C.
- **Verifier notes:** All claimed numbers are on the README; there are three i3-6100 std::reverse tables (bswap, SSSE3, AVX2) plus an MSVC i9-7900x AVX512 table, not only the bswap one. Shortcomings: unstated g++ version, 2018-era numbers, per-call timing noise at small sizes, other CPUs' speedups have no backing table, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-24 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Wunkolo/qreverse>
  - <https://github.com/Wunkolo/qreverse/commits>
  - <https://github.com/Wunkolo/qreverse/tree/master/scripts>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/Wunkolo/qreverse>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/include/qreverse.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/tests/verify.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qreverse/HEAD/LICENSE>
  - <https://github.com/Wunkolo/qreverse/issues?q=is%3Aissue>
  - <https://github.com/Wunkolo/qreverse/issues/2>
  - <https://github.com/Wunkolo/qreverse/commits/master>
  - <https://github.com/Wunkolo/qreverse/commit/9c039b2b7a5a7c9fda961630e907f190c628e46d>
  - <https://github.com/Wunkolo/qreverse/commit/a2eb343615ebed71f7c4309f261f01d3d6b4bbab>
  - <https://github.com/Wunkolo/qreverse/commit/715e54fc4c9c46a101f345da1a7b9ff21f5521b2>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/src/vector_algorithms.cpp>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/xutility>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/algorithm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wunkolo/qreverse`) · [data/wave13/enrich/raw/github_com_wunkolo_qreverse.json](../../../data/wave13/enrich/raw/github_com_wunkolo_qreverse.json) (enrichment confidence 0.8)

</details>
