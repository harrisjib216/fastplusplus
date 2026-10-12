# FastNoiseSIMD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> SIMD 3D coherent-noise generator (Perlin, simplex, value, cellular, cubic) filling float grids 4-45x faster than libnoise.

| | |
|---|---|
| **Beats** | libnoise (also the author's scalar FastNoise) |
| **Claimed result** | Times in x1000 ns. Perlin: AVX512 147, AVX2 324, SSE4.1 592, SSE2 795 versus FastNoise 1002 and LibNoise 1368. Cellular: AVX512 851, AVX2 1283, SSE4.1 2679, SSE2 2959 versus FastNoise 2979 and LibNoise 58125. Simplex: AVX512 129, AVX2 294 versus FastNoise 1194. Cubic SSE2 3516 versus FastNoise 2979 (slower). Versus LibNoise (derived from page data): Perlin 9.3x (AVX512), 4.2x (AVX2), 1.7x (SSE2); cellular 68x (AVX512), 45x (AVX2), 20x (SSE2). README text: 'increasing performance by 700% in some cases (Simplex)'. |
| **Workload** | Time to generate 32x32x32 points of 3D noise on a single thread, default noise settings, for white, value, Perlin, simplex, cellular and cubic noise; libnoise has Perlin and cellular rows only. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Skylake @ 2.0 GHz, single thread |
| **Compiler and flags** | Intel 17.0 x64; flags not stated |
| **Adoption** | 635 stars (archived) |
| **Last commit** | 2021-03-20 |
| **Links** | [repository](https://github.com/Auburn/FastNoiseSIMD) · [benchmark](https://github.com/Auburn/FastNoiseSIMD#performance-comparisons) |

## Verdict

The author's README table times one thread of a 2.0 GHz Skylake Xeon (Intel C++ 17.0 x64, flags not given) filling a 32x32x32 3D grid: AVX2 Perlin 324 us versus libnoise 1368 us (4.2x) and the scalar FastNoise 1002 us (3.1x), AVX2 cellular 1283 us versus libnoise 58125 us (45x), with AVX-512 another 1.3-2.3x over AVX2; the benchmark program was never published. As a consistency check, the FastNoise2 README's NoiseBenchmarking table (clang-cl 10, i7-7820X) shows FastNoise legacy over libnoise by 1.38x (Perlin) and 20.4x (cellular), close to the 1.37x and 19.5x implied by the FastNoiseSIMD table (derived from page data); that harness builds FastNoiseSIMD (AVX2) and libnoise (Perlin at 1 octave, QUALITY_BEST) but publishes no FastNoiseSIMD row.

## Use it when

- Voxel or terrain generation that fills dense 3D chunks (e.g. 32^3 or 64^3) of float noise per call on x86-64 with AVX2 or on ARM NEON
- Cellular/Worley noise in bulk, where the gap over libnoise is largest (README: 20x on SSE2, 45x on AVX2)
- Existing code already built on FastNoiseSIMD that needs a stable, MIT-licensed, vendorable library rather than migrating to FastNoise2
- You want one binary that runs the best ISA path on each user's CPU without separate builds

## Skip it when

- New projects: the repository was archived on 2021-04-02 and the author points users to FastNoise2, which has a node graph, 2D/4D support and a public benchmark harness
- You need 2D or 4D noise, double precision, or tileable noise: only 3D float sets are provided (issues #44 double, #33 4D, #39 tileable were never implemented)
- You need bit-identical output with libnoise or the scalar FastNoise, or across SIMD levels: the readme says outputs differ from FastNoise, and the header warns FMA paths give minute variations versus other levels
- SSE2-only machines running cubic noise: the README table shows SSE2 cubic (3516) slower than the scalar FastNoise (2979), and SSE2 cellular (2959) no faster
- Targets beyond x86 and ARM: ppc64 and s390x fail to build because cpuid.h is missing (issue #22, still open)

## How it is fast

Each noise function is written once against SIMD macros and compiled per instruction set (SSE2, SSE4.1, AVX2+FMA3, AVX-512, NEON); a CPUID/XGETBV check picks the widest path at run time, so 4, 8 or 16 points are evaluated per call. Permutation lookup tables are replaced by an integer multiply-xorshift hash of the lattice coordinates, gradients are chosen with blend masks (or a 16-entry vpermps table on AVX-512), and the grid fill vectorises along z while reusing per-row x/y work. Cellular noise searches only the 3x3x3 neighbourhood in float.

## Compared with alternatives

None of the catalogued siblings generate procedural noise; SLEEF, VDT, fmath and xsimd accelerate elementwise math you would still have to assemble into a noise function yourself. Pick FastNoiseSIMD only for ready-made 3D noise on an existing codebase; for new work its successor FastNoise2 (not yet catalogued) is the author's recommendation.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (bundled Android cpu-features code only for 32-bit ARM) |
| **Minimum toolchain** | C++11 (nullptr, in-class member initialisers, &lt;cstdint&gt;); header lists MSVC v120/v140, Intel 16.0, GCC 4.7 and Clang on macOS as tested; per-file ISA flags required |
| **Platforms** | x86 and x86-64 (SSE2, SSE4.1, AVX2+FMA3 on by default; AVX-512 opt-in), ARM NEON (aarch64 always NEON; 32-bit Android via cpu-features); the scalar fallback is only compiled for 32-bit or _DEBUG builds |
| **Thread safety** | not documented; from the source, the first construction initialises static SIMD constants behind a plain bool flag and writes the global SIMD level, so create one instance before spawning threads; afterwards FillNoiseSet on separate instances and output buffers shares no mutable state |
| **Drop-in for the baseline** | no |

## Gotchas

- Build setup is part of correctness: only FastNoiseSIMD_avx2.cpp / _avx512.cpp may get AVX flags, and the source says to disable MSVC whole-program optimisation for those files; building the whole project with -mavx2/-march=native or LTO lets AVX code leak into shared paths and crash older CPUs (issue #20, 'Illegal instruction'). AVX-512 is disabled by default, and the #error hint in FastNoiseSIMD_avx512.cpp suggests -march=core-avx2, which does not enable the AVX-512 intrinsics on GCC (the author's later NoiseBenchmarking CMake uses -mavx512f -mavx512dq).
- The AVX-512 path uses _mm512_and_ps/_andnot_ps/_xor_ps, which are AVX512DQ instructions, but run-time dispatch checks only the AVX512F CPUID bit (leaf 7 EBX bit 16), so a CPU with AVX-512F but no DQ (Xeon Phi Knights Landing/Mill) would be sent down a path that faults.
- With FN_ALIGNED_SETS (the default) results are written with aligned SIMD stores and the last vector is stored whole, so output buffers must come from GetEmptySet (aligned and padded to the vector width); a plain std::vector&lt;float&gt; of exactly x\*y\*z floats can fault or be overrun by up to 15 floats.
- The libnoise cellular gap is mostly algorithmic: libnoise's Voronoi module searches a 5x5x5 = 125-cell neighbourhood in double with three ValueNoise3D calls per cell, versus FastNoiseSIMD's 27 cells in float; the 68x/45x/20x cellular ratios are not a SIMD-only effect.

## Known shortcomings

- First-party table with flags and libnoise version unstated and no benchmark code; the 68x cellular gap is likely algorithmic; cubic SSE2 is slower than scalar FastNoise, and FastNoise cubic and cellular both read 2979 (possible copy error). Archived 2021-04-02, deprecated in favour of FastNoise2.
- Enricher: libnoise's Voronoi searches 125 cells in double vs FastNoiseSIMD's 27 in float, so the cellular 68x/45x/20x is mostly algorithm, not SIMD; the table harness was never published (Auburn/NoiseBenchmarking builds FastNoiseSIMD AVX2 but publishes no row for it). The AVX-512 path uses AVX512DQ intrinsics while dispatch checks only the AVX512F bit (would fault on Xeon Phi KNL); the #error hint gives the wrong GCC flag; aligned padded output buffers are required. FastNoise2 (Auburn/FastNoise2) is the successor with a public harness.

## Caveats and trade-offs

First-party table from an ICC-built binary on one Skylake Xeon; the benchmark program is a separate preview app in Releases and its code, compiler flags and the libnoise version are not stated. The cellular row against libnoise (68x) is above 50x and likely reflects libnoise's cellular implementation rather than SIMD alone. The scalar FastNoise baseline is the same author's library, and cubic SSE2 (3516) is slower than it (2979); the FastNoise cubic value is identical to the FastNoise cellular value (2979), which may be a copy error in the table. The wiki 'In-depth SIMD level' page compares only SIMD levels within the library, not libnoise. The last commit (2021-03-20, 'Fix noise output error') postdates the table. Repository archived 2 April 2021 and marked deprecated in favour of FastNoise2; AVX-512 numbers need a Skylake-X class CPU.

Runtime detection of the best instruction set (AVX-512F, AVX2 with FMA3, SSE4.1, SSE2, ARM NEON) with a scalar fallback; 3D noise sets only; noise values differ from the scalar FastNoise implementation; the author deprecated it in favour of FastNoise 2.

## Maintenance

Archived on 2021-04-02 and deprecated in favour of FastNoise2; the final commit (2021-03-20) only added missing perturbation for the unaligned tail of vector-set fills; MIT-licensed and about 3,600 lines across 9 source files, so vendoring is easy if you pin your ISA build flags.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table naming CPU (Intel Xeon Skylake @ 2.0 GHz) and compiler (Intel 17.0 x64) but no flags, no libnoise version and no public benchmark code (the preview app is a release binary; the repo holds only the library), and the 68x cellular gap over libnoise exceeds 50x with flags unstated, so C.
- **Verifier notes:** README table matches the record exactly and the derived ratios check out (Perlin 9.3x/4.2x/1.7x, cellular 68x/45x/20x versus LibNoise). Shortcomings to record: first-party, flags and libnoise version unstated, no benchmark code, cellular gap likely algorithmic, cubic SSE2 slower than scalar FastNoise, archived and deprecated for FastNoise2.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/Auburn/FastNoiseSIMD>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/LICENSE>
  - <https://github.com/Auburn/FastNoiseSIMD/wiki/In-depth-SIMD-level>
  - <https://github.com/Auburn/FastNoiseSIMD/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/Auburn/FastNoiseSIMD>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/LICENSE>
  - <https://github.com/Auburn/FastNoiseSIMD/tree/master/FastNoiseSIMD>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD.h>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_internal.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_internal.h>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_avx2.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_avx512.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_sse2.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoiseSIMD/HEAD/FastNoiseSIMD/FastNoiseSIMD_neon.cpp>
  - <https://github.com/Auburn/FastNoiseSIMD/wiki/In-depth-SIMD-level>
  - <https://github.com/Auburn/FastNoiseSIMD/commits/master>
  - <https://github.com/Auburn/FastNoiseSIMD/commit/19dc220>
  - <https://github.com/Auburn/FastNoiseSIMD/issues?q=is%3Aissue>
  - <https://github.com/Auburn/FastNoiseSIMD/issues/20>
  - <https://raw.githubusercontent.com/qknight/libnoise/master/src/module/voronoi.cpp>
  - <https://raw.githubusercontent.com/qknight/libnoise/master/src/noise/module/perlin.h>
  - <https://raw.githubusercontent.com/qknight/libnoise/master/src/noisegen.cpp>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/README.md>
  - <https://github.com/Auburn/NoiseBenchmarking>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/main.cpp>
  - <https://github.com/Auburn/NoiseBenchmarking/tree/master/FastNoiseSIMD>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseSIMD/Benchmark_FastNoiseSIMD.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseSIMD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/libnoise/Benchmark_libnoise.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/auburn/fastnoisesimd`) · [data/wave1/enrich/raw/github_com_auburn_fastnoisesimd.json](../../../data/wave1/enrich/raw/github_com_auburn_fastnoisesimd.json) (enrichment confidence 0.6)

</details>
