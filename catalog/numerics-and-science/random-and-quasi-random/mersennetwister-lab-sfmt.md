# SFMT (SIMD-oriented Fast Mersenne Twister)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Saito and Matsumoto's 128-bit SIMD variant of the Mersenne Twister; about 2.3-2.8x faster than MT19937-64 for bulk 64-bit output.

| | |
|---|---|
| **Beats** | MT19937-64 reference implementation (mt19937-64.c from the MT homepage; same algorithm as std::mt19937_64) |
| **Claimed result** | Intel Core i7-3770: SFMT19937-64 with SIMD 1.8457 s vs MT19937-64 5.1002 s per 1e9 numbers (about 2.8x, derived from page data); AMD Phenom II X6 1045T: 2.8806 s vs 6.6490 s (about 2.3x, derived from page data). SFMT19937-64 without SIMD: 4.2654 s and 5.6123 s (about 1.2x on both, derived from page data). |
| **Workload** | CPU time to generate 1e9 64-bit unsigned integers, SFMT19937-64 (with SIMD) vs MT19937-64, measured by a third party (Harase and Kimoto, ACM TOMS 2018) in the README of sharase/melg-64. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3770 3.40 GHz; AMD Phenom II X6 1045T 2.70 GHz |
| **Compiler and flags** | gcc -O3 on Linux (stated in the melg-64 README) |
| **Adoption** | 96 stars; widely used reference generator (also dSFMT for doubles in the same org) |
| **Last commit** | 2021-05-18 |
| **Links** | [repository](https://github.com/MersenneTwister-Lab/SFMT) · [benchmark](https://github.com/sharase/melg-64) |

## Verdict

In the README of Harase and Kimoto's ACM TOMS 2018 companion repo (melg-64), generating 1e9 64-bit integers with SIMD SFMT19937 took 1.8457 s vs 5.1002 s for the reference mt19937-64.c on a Core i7-3770, and 2.8806 s vs 6.6490 s on a Phenom II X6 1045T: about 2.8x and 2.3x (derived from page data). Both were built with gcc -O3 on Linux, gcc version not stated. Without SIMD, SFMT was only about 1.2x faster. The baseline is the original C reference, not libstdc++ std::mt19937_64.

## Use it when

- Bulk generation of 32-bit integers or doubles from an MT-family generator (Monte Carlo, simulation) where you can call sfmt_fill_array32/64 into a 16-byte-aligned buffer
- Codebases that want a peer-reviewed, long-period (2^19937-1 or larger) F2-linear generator with jump-ahead for parallel streams (jump/ directory)
- x86-64 with SSE2/AVX2 or AArch64 with NEON, where the SIMD path is enabled explicitly at build time
- Replacing std::mt19937 when the exact MT19937 sequence does not matter but MT-style period and equidistribution analysis do

## Skip it when

- You need std::mt19937 / std::mt19937_64 bit-identical output (use a vectorized MT19937 such as VMT19937 instead)
- 64-bit integer output where high-dimensional equidistribution matters: Harase and Kimoto give SFMT19937-64 Delta=14095 vs 7820 for MT19937-64 and 0 for MELG19937-64. SFMT is tuned for 32-bit output, and dSFMT is the variant meant for doubles
- Small-state or many-instance uses (per-thread or per-object generators): the 19937 state is SFMT_N = 156 128-bit words (about 2.5 KB), versus 256 bits for xoshiro256-class generators
- Applications that care about TestU01 linearity tests: like all F2-linear generators, SFMT fails MatrixRank/LinearComp (per a search snippet, 4 of 106 BigCrush tests; source page not opened)
- Big-endian or AltiVec targets: the README says these 'ARE NOT TESTED AT ALL'

## How it is fast

The recursion works on 128-bit words (four 32-bit lanes) using only shifts, ANDs with a mask and XORs, so one SIMD instruction sequence produces 128 bits per step. The pick-up position (POS1=122 for 19937) and the lag-1/lag-2 feedback words (r1, r2) are chosen to keep dependency chains short. The block functions (sfmt_fill_array32/64) generate directly into the output array without copying the state. Since 1.5.2 an AVX2 path (SFMT-avx256.h, contributed by Masaki Ota) does two 128-bit steps per 256-bit operation and uses vpternlog under AVX-512VL. This relies on SL1 &gt;= 16, so the dependent half-word term shifts out. A NEON path (SFMT-neon.h, optional SHA3 EOR3/BCAX) covers AArch64.

## Compared with alternatives

Pick SFMT over VMT19937 or pXart when you do not need the std::mt19937 sequence and want the original authors' peer-reviewed SIMD design with jump-ahead and many period choices. Pick MELG-64 instead for 64-bit output with full equidistribution, and xoshiro-family SIMD generators (simdrng, Xoshiro256PlusSIMD) for small state and no linearity-test failures.

## Integration

| | |
|---|---|
| **Form** | source-drop (SFMT.c + headers; CMakeLists.txt builds a static libSFMT.a) |
| **Dependencies** | none for the generator; the jump-ahead polynomial calculator (jump/calc-jump) needs NTL |
| **Minimum toolchain** | C99 (Makefile uses -std=c99); gcc 3.4+ for SSE2 per howto-compile.html; MSVC supported via SFMT-sse2-msc.h; callable from C++ via extern "C" |
| **Platforms** | any (portable C path); SIMD paths for x86 SSE2, AVX2, AVX-512VL (256-bit), ARM NEON (AArch64 and ARMv7 Makefiles), PowerPC AltiVec (untested) |
| **Thread safety** | not documented; since 1.4 all state is in a caller-owned sfmt_t, so one generator per thread is safe and sharing one needs external locking |
| **Drop-in for the baseline** | no |

## Gotchas

- SIMD is off by default: you must pass -DHAVE_SSE2 (or HAVE_NEON / HAVE_ALTIVEC) plus the ISA flag, otherwise the plain C recursion is compiled even on x86-64. The AVX2 path is chosen automatically when __AVX2__ is defined together with HAVE_SSE2. CMake's USE_SSE2 passes -msse rather than -msse2.
- SFMT_MEXP must be identical in every translation unit because it changes sizeof(sfmt_t); if it is missing, gcc warns and assumes 19937.
- sfmt_fill_array32/64 require a 16-byte-aligned buffer on SIMD builds, a size that is a multiple of 4 (or 2) and at least SFMT_N32 (624) or SFMT_N64 (312) elements, and a freshly initialized or fully consumed state. They cannot be mixed with sequential calls without re-initializing, and gen_rand64 must not follow gen_rand32 (enforced only by assert).
- howto-compile.html sample3 still uses the pre-1.4 global API (init_gen_rand, genrand_res53) that no longer exists; follow sample1/2 and SFMT.h instead.

## Known shortcomings

- Tier B rests on the MELG-64 TOMS table (SFMT homepage blocked here); check.sh diffs SIMD builds against scalar output, so the SIMD path is the same generator.
- SIMD is off unless -DHAVE_SSE2/NEON is passed; avx2-check covers M19937 only. SFMT19937 reportedly fails 4/106 BigCrush tests (MatrixRank/LinearComp; search snippet only). howto-compile sample3 uses the removed pre-1.4 API. Abandoned 2021; NEON PR #10 (2026-01) unmerged.

## Caveats and trade-offs

Numbers come from a third-party table in the melg-64 README (companion repo of Harase and Kimoto, ACM TOMS 44(3) 2018), measured on 2012-era CPUs with an unstated gcc version; the melg-64 repo holds only the MELG generators, not the timing harness for SFMT or MT19937-64. The baseline is the original mt19937-64.c, not libstdc++ std::mt19937_64. The SFMT README itself has no numbers, and the authors' homepage claim ('about twice as fast as MT') could not be opened (egress blocked). The SIMD path computes the same generator as the scalar one: the repo's check.sh diffs the std, sse2, avx2 and altivec test builds against the same reference outputs (SFMT.&lt;MEXP&gt;.out.txt). Quality trade-off noted on the same page: for 64-bit output SFMT19937 has a large equidistribution defect (Delta 14095 vs 7820 for MT19937-64), since SFMT is tuned for 32-bit output; dSFMT is the recommended variant for doubles. SFMT also produces a different sequence than MT19937, so it is a replacement generator, not a faster std::mt19937.

Produces a different sequence from MT19937, so it is not a drop-in for std::mt19937 output. Designed for 32-bit output; for 64-bit output the high-dimensional equidistribution is worse (Harase's table gives Delta=14095 vs 0 for MELG), and dSFMT is the variant meant for doubles. 128-bit SIMD blocks with SSE2, AVX2/AVX512 (added in 1.5.2), NEON (1.5.3) and Altivec backends; README warns big-endian and Altivec are not tested. C API with the state in a struct.

## Maintenance

Abandoned since 2021-05-18 (an open NEON update PR #10 from January 2026 is unmerged), but the 3-clause BSD code is small, stable since 2006 and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README of the ACM TOMS 2018 paper's companion repo (sharase/melg-64, by Harase and Kimoto, not the SFMT authors) has a table of CPU seconds for 1e9 64-bit outputs: SFMT19937-64 with SIMD 1.8457 s vs MT19937-64 5.1002 s (Core i7-3770) and 2.8806 s vs 6.6490 s (Phenom II X6 1045T), gcc -O3. That is a peer-reviewed third-party measurement, but the timing harness is not in the repo (only generator directories) and the gcc version is not given, so not A.
- **Verifier notes:** Numbers verified verbatim on the melg-64 README; derived ratios (2.8x Intel, 2.3x AMD) are correct. Repo metadata confirmed via the github.com page: BSD-3-Clause (LICENSE.txt), 96 stars, not archived, last commit 2021-05-18 (abandoned).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/sharase/melg-64>
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/README.md>
  - <https://github.com/MersenneTwister-Lab/SFMT>
  - <https://github.com/MersenneTwister-Lab/SFMT/commits>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/README.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/check.sh>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/test.c>
- **Sources the enricher read:**
  - <https://github.com/MersenneTwister-Lab/SFMT>
  - <https://github.com/MersenneTwister-Lab/SFMT/issues>
  - <https://github.com/MersenneTwister-Lab/SFMT/pulls?q=is%3Apr>
  - <https://github.com/MersenneTwister-Lab/SFMT/tree/master/jump>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/README.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/CHANGE-LOG.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/howto-compile.html>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/mainpage.txt>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT.c>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-params.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-params19937.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-common.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-sse2.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-avx256.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/SFMT-neon.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/check.sh>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/test.c>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/jump/SFMT-jump.h>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/SFMT/HEAD/jump/SFMT-jump.c>
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/README.md>
  - WebSearch: SFMT19937 TestU01 BigCrush LinearComp MatrixRank (snippets only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mersennetwister-lab/sfmt`) · [data/wave8/enrich/raw/github_com_mersennetwister_lab_sfmt.json](../../../data/wave8/enrich/raw/github_com_mersennetwister_lab_sfmt.json) (enrichment confidence 0.8)

</details>
