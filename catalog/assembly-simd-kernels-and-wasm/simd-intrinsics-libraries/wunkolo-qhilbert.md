# qHilbert

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Batch Hilbert-curve index-to-point mapping (Hacker's Delight parallel prefix, SSE/AVX2/AVX-512); 10-50x over Wikipedia's d2xy loop.

| | |
|---|---|
| **Beats** | Wikipedia d2xy/rot C implementation (in source/qHilbert.cpp), called once per index from tests/benchmark.cpp; the README table does not label it |
| **Claimed result** | README table, speedup over the Wikipedia d2xy loop: i9-7900x x42.5 to x50.4, i7-7500u x30.6 to x39.7, i3-6100 x31.1 to x36.2, E5-2697 v4 x20.5 to x24.2, E3-1240 v5 x9.7 to x11.0 across the Serial/BMI2, SSE4.2, AVX2 and AVX512 columns; README text: around 50 times faster. With the public CMake the library target gets no ISA flags, so all four columns run the same generic scalar code and the gain is the Hacker's Delight parallel-prefix rewrite (9.7x to 50x), not SIMD. |
| **Workload** | tests/benchmark.cpp: map all 16,384 indices of an order-7 (128x128) Hilbert curve to 2D points, 10 trials averaged with std::chrono::high_resolution_clock, output checked against d2xy (PASS/FAIL). qHilbert2D uses the Hacker's Delight (Lam-Shapiro/Steele) parallel-prefix method, with pext under BMI2 and SSE4.2/AVX2/AVX-512 paths. |
| **Metric** | throughput |
| **Hardware** | Intel i9-7900x, i7-7500u, i3-6100, Xeon E5-2697 v4, Xeon E3-1240 v5 |
| **Compiler and flags** | CMakeLists.txt: -Ofast -Wall -Wextra on the GCC branch, plus -mbmi2 / -msse4.2 / -mavx2 / -mavx512f per Benchmark-\* executable; compiler and version not stated |
| **Adoption** | 38 stars |
| **Last commit** | 2018-12-31 |
| **Links** | [repository](https://github.com/Wunkolo/qHilbert) · [benchmark](https://github.com/Wunkolo/qHilbert) |

## Verdict

The README table (2018, compiler not stated) divides Wikipedia d2xy time by qHilbert time for all 16,384 points of an order-7 curve, averaged over 10 trials: 42.5x to 50.4x on an i9-7900X, down to 9.7x to 11.0x on a Xeon E3-1240 v5. Because the published CMake build compiles the library without ISA flags, these effectively measure the scalar Hacker's Delight parallel-prefix rewrite against d2xy; the 'Serial/BMI2' pext path would fail the benchmark's own check at order 7.

## Use it when

- Generating many Hilbert-order coordinates at once (tile or texture swizzles, cache-friendly traversal orders, spatial sort keys) for orders up to 15, when a d2xy-style loop shows up in profiles.
- As a copyable reference for the constant-time Hacker's Delight d2xy: the generic scalar path alone accounts for most of the measured gain.
- x86-64 builds where you control the flags of source/qHilbert.cpp itself and can enable -msse4.2/-mavx2/-mavx512f without -mbmi2 (see gotchas).
- Batches whose size is a multiple of 16, so every point goes through the vector paths.

## Skip it when

- Any build where source/qHilbert.cpp sees __BMI2__ (for example -march=native on Haswell or later): the pext serial path, which handles whole batches in a BMI2-only build and the Count % 4 tail otherwise, returns wrong coordinates for every order except 8 (at order 7, y is off by 128 for every point).
- MSVC: every path is enabled under _MSC_VER and the MSVC CMake branch sets no /arch, so the binary executes AVX-512F instructions on all CPUs (illegal instruction without AVX-512) and uses the broken pext path for tails.
- Order 16 (65536 x 65536) or larger: 0x55555555 &lt;&lt; 2\*Order and 1 &lt;&lt; 2\*Order shift by 32 (undefined; on x86 the unpad mask becomes 0), so even the generic and SIMD paths return wrong points, although the benchmark's static_assert accepts 16. Only orders 1-15 are correct.
- Needing xy2d (point to index), 3D curves, ARM SIMD (the README's NEON code is an illustration; the source has no NEON path, so ARM gets generic scalar code) or a maintained dependency.
- Choosing it for the SIMD columns of the README table: the public build compiles the library without ISA flags, so those columns are not evidence for SIMD gains over the scalar rewrite.

## How it is fast

Instead of d2xy's per-level loop (a branchy rot() call and signed divisions for every level), it uses the Lam-Shapiro method as rewritten by Guy Steele in Hacker's Delight: pad the index with 01 pairs, get the complement and swap bits from one add plus a parallel-prefix XOR, then unshuffle odd and even bits into x and y, in constant time whatever the order. The same bit operations are written for 4, 8 and 16 lanes with SSE, AVX2 and AVX-512 (vpternlogd fuses the XOR/AND steps), and a BMI2 variant replaces the unshuffle with two pext instructions. Paths are picked at compile time by recursive template specialisation, with remainders falling through to narrower widths.

## Compared with alternatives

No catalogued sibling maps Hilbert indices; beside qAverageColor and qReverse (same author, same write-up style) it is the one for space-filling-curve coordinates. Take it as a reference for the constant-time d2xy, not for its SIMD columns.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | GLM (git submodule dependencies/glm, for glm::u32vec2) |
| **Minimum toolchain** | C++17 with GNU extensions, CMake 3.2.2; compiler and version behind the README numbers not stated |
| **Platforms** | x86-64 for the SSE4.2, AVX2, AVX-512F and BMI2 paths; generic scalar C++ elsewhere (no NEON implementation in the source) |
| **Thread safety** | not documented; a pure function over caller-owned arrays with no shared state, so reentrant by construction |
| **Drop-in for the baseline** | partial — on the non-BMI2 paths it computes the same points as d2xy for orders 1-15, but as a batch call that takes the order (log2 width) and writes glm::u32vec2 instead of per-point d2xy(n, d, &x, &y) |

## Gotchas

- Correctness bug in the pext (BMI2) serial path: commit 'Remove un-needed mask-cleanup in favor of pext' (2018-11-12) dropped the s &= (1 &lt;&lt; 2\*Order) - 1 unpad step, but _pext_u32 with masks 0xAAAA/0x5555 still reads padding bits below bit 16 and ignores coordinate bits above it. A Python emulation of the source (this session) matches d2xy at every order 1-15 on the generic path, but on the pext path mismatches every point for orders 1-7 and 75-100% of sampled points for orders 9-15; at the benchmark's order 7, d = 0 gives (0, 128) instead of (0, 0). The README credits pext for its 'around 50 times faster' headline and labels the first column 'Serial/BMI2'; had that column really run the pext path, the benchmark's own check would have printed FAIL.
- Harness flaw: CMakeLists.txt (last changed 2018-12-29 in 'Add multiple benchmark variants', before every table row was added from 2018-12-29 to 2018-12-31, with no later source change) passes -mbmi2/-msse4.2/-mavx2/-mavx512f only to the Benchmark-\* executables, not to the qHilbert library that holds the paths, so a GCC build runs the same generic scalar code in all four columns. The column differences (AVX2 below SSE4.2 on the E5-2697 v4 and E3-1240 v5) look like run-to-run noise; what the table supports is Hacker's Delight scalar code against d2xy, 9.7x to 50x.
- Timing is 10 back-to-back trials of 16,384 points (microsecond-scale per qHilbert trial), d2xy first, std::chrono::high_resolution_clock, no warm-up; the d2xy baseline is a non-inlined cross-translation-unit call per point with signed division and no LTO. The benchmark prints PASS/FAIL but continues on FAIL, and the d2xy FAIL string has a malformed escape code ('\033[0;31FAIL').
- Remainders fall through the template chain to the serial path, so in a -march=native build most of a batch is right and only the last Count % 4 points are wrong: a silent, size-dependent error rather than a crash.

## Known shortcomings

- Unlabelled baseline is the Wikipedia d2xy (tests/benchmark.cpp, 16,384 points) and the gain is mostly algorithmic (Hacker's Delight parallel prefix); per-target ISA flags in CMakeLists.txt never reach the qHilbert library, so how the table columns were built is not public; compiler unstated; abandoned 2018.
- The BMI2 pext serial path dropped its unpad mask on 2018-11-12 and is wrong for every order except 8 (order 7: y off by 128), yet the README credits pext for the 'about 50x'; the public CMakeLists gives the library target no ISA flags, so all four README columns run the same generic Hacker's Delight code against the Wikipedia d2xy loop (the claim reduces to 9.7-50x algorithmic, with no SIMD contribution shown). Order 16 is broken and MSVC builds run the AVX-512 path on any CPU. Abandoned since 2018-12-31.

## Caveats and trade-offs

The table's baseline (Wikipedia d2xy, branchy loop with one cross-translation-unit call per point and no LTO) is not labelled on the README; it is identified from tests/benchmark.cpp. Most of the gain is algorithmic (Hacker's Delight parallel-prefix rewrite): the Serial/BMI2 column is already x42.5 on i9-7900x, AVX-512 adds about 1.19x over it (derived from page data), and AVX2 is slower than SSE4.2 on E5-2697 v4. In the public CMakeLists.txt the per-target ISA flags are PRIVATE to the Benchmark-\* executables (tests/benchmark.cpp) and do not reach the qHilbert static library (source/qHilbert.cpp) that holds the SIMD paths, so a build as written runs the same generic serial code in every target; the flags actually used for the table's columns are not public. Each trial is only 16,384 points (microsecond-scale timing). Compiler not stated. 2018 numbers; repo abandoned since 2018-12-31. [retier] The table's baseline (Wikipedia d2xy, branchy loop with one cross-translation-unit call per point and no LTO) is identified from tests/benchmark.cpp, not labelled on the README. The gain is algorithmic: the public CMakeLists.txt applies ISA flags only to the Benchmark-\* executables, so the library's generic path is what every column timed (AVX2 is even slower than SSE4.2 on E5-2697 v4). The BMI2 pext serial path dropped its unpad mask on 2018-11-12 and is wrong for every order except 8 (order 7: y off by 128), so a real pext run would fail; order 16 is broken; MSVC builds run the AVX-512 path on any CPU. Abandoned since 2018-12-31.

x86 SIMD (SSE4.2, AVX2, AVX-512 plus BMI2 pext); a NEON version is shown in the README as illustration. Uses glm::u32vec2 for output points.

## Maintenance

Abandoned since 2018-12-31 (master and develop both last updated then; 38 stars, MIT); small enough to vendor, but use the generic or SSE/AVX paths only, restore the unpad mask before using the pext path, and treat orders above 15 as unsupported.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table with CPU models; the benchmark code (tests/benchmark.cpp) is public and shows the unlabelled baseline is the Wikipedia d2xy implementation, but the compiler and version are not stated and the per-ISA build flags behind the columns cannot be reproduced from the public CMakeLists.txt, so not A.
- **Verifier notes:** Numbers match the README exactly; baseline is the Wikipedia d2xy loop, so the 9.7x-50.4x speedups are mostly an algorithm change (constant-time parallel prefix) rather than SIMD. Metadata confirmed: MIT, 38 stars, 10 forks, last commit 2018-12-31, abandoned. Category fit is loose (Hilbert-curve index mapping, not a general SIMD intrinsics library).
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-26 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/README.md>
  - <https://github.com/Wunkolo/qHilbert>
  - <https://github.com/Wunkolo/qHilbert/commits>
  - <https://github.com/Wunkolo/qHilbert/tree/master/tests>
  - <https://github.com/Wunkolo/qHilbert/tree/master/source>
  - <https://github.com/Wunkolo/qHilbert/tree/master/scripts>
  - <https://github.com/Wunkolo/qHilbert/commits/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/tests/TestBed.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/include/qHilbert.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/source/qHilbert.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/Wunkolo/qHilbert>
  - <https://github.com/Wunkolo/qHilbert/commits/master>
  - <https://github.com/Wunkolo/qHilbert/commits/master/CMakeLists.txt>
  - <https://github.com/Wunkolo/qHilbert/commits/master/source/qHilbert.cpp>
  - <https://github.com/Wunkolo/qHilbert/branches/all>
  - <https://github.com/Wunkolo/qHilbert/issues?q=is%3Aissue>
  - <https://github.com/Wunkolo/qHilbert/tree/master/scripts>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/include/qHilbert.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/source/qHilbert.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/tests/TestBed.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qHilbert/HEAD/scripts/Hilbert.py>
  - <https://github.com/rawrunprotected/hilbert_curves>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wunkolo/qhilbert`) · [data/wave13/enrich/raw/github_com_wunkolo_qhilbert.json](../../../data/wave13/enrich/raw/github_com_wunkolo_qhilbert.json) (enrichment confidence 0.8)

</details>
