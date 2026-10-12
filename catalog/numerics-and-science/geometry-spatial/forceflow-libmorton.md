# libmorton (Forceflow)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ 2D/3D Morton (Z-order) encode/decode; its BMI2 pdep/pext path beats its own lookup-table and magic-bits code.

| | |
|---|---|
| **Beats** | libmorton's shipped non-BMI default (LUT Shifted) and its other LUT methods, as measured in morton-nd's fork of the libmorton test harness |
| **Claimed result** | 32-bit 3D encode: BMI2 530.421 ms (linear) and 536.726 ms (random) against LUT 668.371 and 665.673 ms, about 1.26x and 1.24x. 32-bit 3D decode: BMI2 560.478 and 3159.143 ms against LUT 1033.880 and 3605.081 ms, about 1.84x and 1.14x. 64-bit 3D encode: BMI2 524.044 and 563.434 ms against LUT 909.336 and 929.829 ms, about 1.74x and 1.65x (all ratios derived from page data). README prose: BMI2 'is definitely a faster method when compared to the standard case'. |
| **Workload** | 3D Morton encode and decode of 512^3 = 134,217,728 codes, 32-bit and 64-bit, with linearly increasing and random inputs, averaged over 5 runs, using libmorton's own test harness (kevinhartman/libmorton fork) as reported in the morton-nd README. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9980HK |
| **Compiler and flags** | GCC 11.1.0 on macOS 11.1 with -O3 -DNDEBUG (morton-nd README); the kevinhartman/libmorton fork README states its CMakeLists.txt sets -mbmi2 to enable the BMI2 test paths (the CMakeLists.txt itself was not found at the fork's root) |
| **Adoption** | 667 stars; cited as used by Esri, Cesium Ion and CLAIRE |
| **Last commit** | 2026-06-16 |
| **Links** | [repository](https://github.com/Forceflow/libmorton) · [benchmark](https://raw.githubusercontent.com/morton-nd/morton-nd/main/README.md) |

## Verdict

Third-party numbers only: the morton-nd README (Intel Core i9-9980HK, GCC 11.1.0, macOS 11.1, -O3 -DNDEBUG plus -mbmi2 from the fork's test CMakeLists.txt, 512^3 codes, 5-run average) shows libmorton's BMI2 path ahead of its own shifted LUT, which is the actual non-BMI default in morton.h: 32-bit 3D encode 530 vs 630 ms (about 1.19x), 64-bit 3D encode 524 vs 829 ms (about 1.58x), 32-bit 3D decode 560 vs 871 ms (about 1.55x) and 64-bit 3D decode 560 vs 1300 ms (about 2.32x) on linear input (derived from page data); the plain-LUT ratios in the record (1.14x to 1.84x) are against a non-default method. No external incumbent, loop or magic-bits baseline is measured, morton-nd's own BMI2 and 1-chunk LUT rows tie libmorton, the harness timer overhead described under gotchas distorts the random columns, and PR #40's release-mode run on an i7-1065G7 shows the AVX-512 path about 10 to 20 percent slower than BMI2 (64-bit 1.060 vs 0.915 ms), not equal.

## Use it when

- Building octrees, sparse voxel grids, BVH/LBVH sorts or Z-order point sorting where you need millions of 2D/3D Morton codes per second on Intel Haswell+ or AMD Zen 3+ compiled with -mbmi2 or -march=haswell.
- You want a dependency-free header you can vendor (MIT, a handful of headers, vcpkg port available).
- Coordinates fit 10 bits per axis (3D 32-bit codes) or 21 bits per axis (3D 64-bit codes), or 16/32 bits per axis in 2D.
- Portable builds where you cannot assume BMI2: the shifted-LUT default is still a reasonable table-based baseline with a few KB of tables.

## Skip it when

- AMD Zen 1, Zen+ and Zen 2: PDEP/PEXT are microcoded there with data-dependent latency far above Intel's 3 cycles, so the BMI2 path the README recommends via -march=znver2 is likely slower than the LUT default; benchmark before enabling it on those CPUs.
- More than three dimensions, or field widths other than 16/32/64-bit codes: libmorton is 2D/3D only (morton-nd covers N dimensions with BMI2 and compile-time LUTs at parity in its own table).
- WebAssembly, 32-bit targets or Clang on Windows: open issues #86 (fails on WASM and 32-bit builds) and #87 (Clang compilation fails on Windows); the test suite build on macOS is also an open issue (#49).
- You need range-checked input or Morton arithmetic (neighbor, add, parent): there is no bounds checking and the Morton-operations item is still on the README TODO list.
- Batch/SIMD encoding of arrays: the API is one code per call; there is no vectorized bulk interface outside the experimental AVX-512 path.

## How it is fast

With __BMI2__ (or __AVX2__) defined, each coordinate is scattered into its bit lane with one PDEP and gathered back with one PEXT against fixed masks (0x9249... for 3D), so a 3D encode is three pdep plus two ORs. Without BMI2 the 3D default is a pre-shifted 256-entry lookup table per axis processed one byte at a time (encode) and a 512-entry table over 9-bit chunks (decode); 2D 32-bit uses magic-bits shift-and-mask. An experimental AVX-512 BITALG path uses _mm512_bitshuffle_epi64_mask.

## Compared with alternatives

Pick libmorton when you need plain Z-order keys and want a vendorable header; choose rawrunprotected/hilbert_curves when you need Hilbert order's better locality (it is a 2D Hilbert index, not Morton), while the kd-tree and R-tree siblings (nanoflann, PH-tree, Bonxai) are whole spatial indexes rather than key encoders, so libmorton complements rather than replaces them.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard headers; immintrin.h for the BMI2 and AVX-512 paths) |
| **Minimum toolchain** | C++11; README suggests GCC 9+ for -march=haswell / -march=icelake-client; CMake 3.15+ for the optional CMake package |
| **Platforms** | any (portable LUT and magic-bits paths); x86-64 with BMI2 for the fast path (Intel Haswell+, AMD Zen 3+ for fast pdep/pext); experimental AVX-512 BITALG (Ice Lake+); known build failures on WASM, 32-bit and Clang-on-Windows |
| **Thread safety** | not documented; the functions are stateless and only read static tables, so concurrent calls should be safe |
| **Drop-in for the baseline** | partial — the baselines are hand-written loop or magic-bits interleaving; libmorton replaces them with function calls, but coordinate types are uint_fast16_t/uint_fast32_t and must be masked to the per-axis bit budget by the caller |

## Gotchas

- The only published numbers (morton-nd README, i9-9980HK, GCC 11.1, macOS) come from the kevinhartman/libmorton fork harness, which calls every method through a function pointer and brackets every 8-code block (every single code in the random-decode test) with two clock_gettime(CLOCK_REALTIME) calls inside the accumulated timer. All random-decode rows sit at 3.1 to 4.5 s against 0.5 to 1.6 s linear, so that column is dominated by clock-read overhead (about 268 million clock reads for 134 million codes) and its 1.14x BMI2-vs-LUT ratio says little about decode cost; the linear rows share a floor near 516 to 540 ms that likely compresses ratios too.
- morton.h tests __BMI2__ || __AVX2__ before __AVX512BITALG__, so a -march=icelake-client build (which defines all three) always gets the BMI2 path; the AVX-512 path is reachable only if BMI2 is not defined. Selecting the pdep path on __AVX2__ alone also means GCC/Clang builds with -mavx2 but without -mbmi2 hit the BMI2 intrinsics without the bmi2 target enabled.
- Function types are uint_fast16_t/uint_fast32_t, which glibc on x86-64 makes 8 bytes wide (macOS and MSVC use 2 and 4). On Linux the '32-bit' calls therefore run 64-bit code: the shifted-LUT encode loops sizeof(coord) = 8 times instead of 2, the LUT decode loops 7 times instead of 4, and out-of-range coordinate bits can spill above bit 31 instead of being truncated, so the macOS benchmark numbers do not transfer to Linux.
- No range checks: 3D codes hold 11/11/10 bits per axis in 32 bits and 22/21/21 in 64 bits under the BMI2 and LUT paths, while the 3D magic-bits helper masks to 10 or 21 bits first, so oversized inputs give method-dependent codes; mask coordinates yourself.

## Known shortcomings

- The only numbers are morton-nd's README comparing libmorton's BMI2 path against its own LUT (1.14-1.84x, i9-9980HK, GCC 11.1.0 -O3, -mbmi2), and morton-nd matches it; no external loop or magic-bits baseline. The author's own numbers are in blocked blog posts.
- Enricher: harness flaw in the kevinhartman/libmorton fork behind every morton-nd number: calls go through function pointers and two clock_gettime(CLOCK_REALTIME) calls wrap every 8-code block and every single code in random decode, so the random-decode rows (3.1-4.5 s for every method) mostly time about 268M clock reads and their 1.14x is meaningless. The shipped non-BMI default is LUT Shifted, against which BMI2 gives 1.19x and 1.58x encode and 1.55x and 2.32x decode (32/64-bit, linear). morton.h picks BMI2 before AVX512, so the AVX512 path is unreachable with -march=icelake-client (PR #40 shows it 10-20% slower than BMI2); the README advises -march=znver2 although pdep/pext are slow on Zen 1 and 2; glibc's uint_fast16_t and uint_fast32_t are 8 bytes, so the '32-bit' calls run 64-bit loops on Linux; code untouched since 2023-08-26.

## Caveats and trade-offs

The repo README contains no numbers; it points to three forceflow.be blog posts (2013 bit-interleaving, 2016 libmorton, 2016 BMI2) that hold the real benchmarks, and that host does not resolve here. The only numbers found are third-party (morton-nd README) and compare libmorton's BMI2 path with libmorton's own LUT paths, so no external incumbent and none of the loop or magic-bits baselines is measured. The same table shows morton-nd's generated code at parity with or slightly ahead of libmorton (32-bit 3D encode: morton-nd 1-chunk 10-bit LUT 524.178 ms linear vs libmorton BMI2 530.421 ms). The 'definitely a faster method' line is libmorton's own README prose about BMI2, without numbers. PR #40 (AVX512 vs BMI2 on an i7-1065G7, compiler not stated) shows the experimental AVX512 path roughly equal to BMI2. [retier] Enricher: the kevinhartman/libmorton harness wraps every 8-code block, and every single code in random decode, in two clock_gettime calls through function pointers, so the random-decode rows (3.1-4.5 s for all methods) time clock reads and their 1.14x is meaningless; against LUT Shifted BMI2 gives 1.19x/1.58x encode and 1.55x/2.32x decode (32/64-bit, linear). The AVX512 path is unreachable when BMI2 is available; pdep/pext are slow on Zen 1 and 2; glibc uint_fast32_t is 8 bytes, so 32-bit calls run 64-bit loops on Linux.

Header-only C++11 with 2D and 3D, 16/32/64-bit coordinates. The fast path needs BMI2 (Intel Haswell or newer, AMD Zen or newer) enabled at compile time; AVX512 BITALG support is experimental. Lookup-table methods use memory and cache that the magic-bits and BMI2 paths avoid.

## Maintenance

The record's 'active' is generous: the last code change is 2023-08-26 (MSVC lean-and-mean headers) and the 2026-06-16 commits only touch the README and badge, with build issues #86 and #87 open; still MIT, header-only and small enough to vendor, so it remains copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The morton-nd README numbers (GCC 11.1.0, -O3 -DNDEBUG, i9-9980HK, harness in the kevinhartman/libmorton fork, whose README says its CMakeLists.txt adds -mbmi2) are reproducible, but they only compare libmorton's BMI2 path with libmorton's own LUT paths and with morton-nd (parity), never with an external incumbent or the loop and magic-bits baselines, whose numbers sit in unreachable forceflow.be posts; an intra-library comparison stays at C.
- **Verifier notes:** Shortcoming: only intra-library BMI2-vs-LUT numbers (1.14x to 1.84x, derived) from a third-party README, no external incumbent or loop/magic-bits baseline measured; blog benchmarks unreachable. All claimed_speedup numbers match the morton-nd README rows; metadata checked (667 stars, MIT, last commit 2026-06-16, active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-180 (wave 8 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/morton-nd/morton-nd/main/README.md>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/README.md>
  - <https://raw.githubusercontent.com/kevinhartman/libmorton/HEAD/README.md>
  - <https://github.com/Forceflow/libmorton>
  - <https://github.com/Forceflow/libmorton/commits>
- **Sources the enricher read:**
  - <https://github.com/Forceflow/libmorton>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/README.md>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton3D.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton3D_LUTs.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton_BMI.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton_common.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/include/libmorton/morton_AVX512BITALG.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/test/libmorton_test.cpp>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/test/libmorton_test.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/test/test3D_performance.h>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/test/makefile>
  - <https://raw.githubusercontent.com/Forceflow/libmorton/HEAD/CMakeLists.txt>
  - <https://github.com/Forceflow/libmorton/issues?q=is%3Aissue>
  - <https://github.com/Forceflow/libmorton/issues?page=2&q=is%3Aissue>
  - <https://github.com/Forceflow/libmorton/issues/27>
  - <https://github.com/Forceflow/libmorton/issues/71>
  - <https://github.com/Forceflow/libmorton/pull/40>
  - <https://github.com/Forceflow/libmorton/commits>
  - <https://raw.githubusercontent.com/morton-nd/morton-nd/main/README.md>
  - <https://github.com/kevinhartman/libmorton>
  - <https://raw.githubusercontent.com/kevinhartman/libmorton/HEAD/test/libmorton_test.cpp>
  - <https://raw.githubusercontent.com/kevinhartman/libmorton/HEAD/test/libmorton_test_3D.h>
  - <https://raw.githubusercontent.com/kevinhartman/libmorton/HEAD/test/timer.h>
  - <https://raw.githubusercontent.com/kevinhartman/libmorton/HEAD/test/CMakeLists.txt>
  - https://phoronix.com/news/LLVM-Improve-AMD-PDEP-PEXT (WebSearch snippet only: Zen 1/Zen+/Zen 2 PDEP/PEXT 'notoriously bad')
  - https://bugs.dolphin-emu.org/issues/12332 (WebSearch snippet only: AMD Family 19h guide quoted as 3-cycle latency, one per cycle)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/forceflow/libmorton`) · [data/wave8/enrich/raw/github_com_forceflow_libmorton.json](../../../data/wave8/enrich/raw/github_com_forceflow_libmorton.json) (enrichment confidence 0.72)

</details>
