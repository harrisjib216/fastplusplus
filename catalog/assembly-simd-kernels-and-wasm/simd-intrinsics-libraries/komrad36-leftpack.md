# Leftpack (komrad36)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header AVX2+BMI2 left-pack (compress) of one 32-byte register; author claims 1.6-5.3x over a branchless scalar loop.

| | |
|---|---|
| **Beats** | naive scalar left-pack loop (branchy, 'super naive') and branchless naive scalar loop, both listed in the README |
| **Claimed result** | README 'Approx. speedup vs. naive methods': 8-bit 39x versus super naive and 5.3x versus branchless naive; 16-bit 31x and 3.8x; 32-bit 14x and 2.2x; 64-bit 7.8x and 1.6x. README also says it beats the AVX-512 VCOMPRESS instructions for the bitmask case (no number given). |
| **Workload** | AVX2 left-pack (compress) of one 256-bit vector per call (32 8-bit, 16 16-bit, 8 32-bit or 4 64-bit elements), driven by an integer bitmask or a vector mask; needs AVX2 plus BMI2 (PDEP/PEXT) and POPCNT, with \*_Zen2 variants that avoid PDEP/PEXT for AMD Zen1/Zen2. |
| **Metric** | throughput |
| **Compiler and flags** | README: supports clang, gcc and MSVC, and its simple correctness tests (test.cpp) were exercised on all three; no compiler versions, flags or CPU are given for the speedup table, and the repo has no benchmark code. |
| **Adoption** | 4 stars |
| **Last commit** | 2023-10-04 |
| **Links** | [repository](https://github.com/komrad36/Leftpack) · [benchmark](https://github.com/komrad36/Leftpack) |

## Verdict

The only numbers are the author's README table: 39x, 31x, 14x and 7.8x over a branchy scalar loop and 5.3x, 3.8x, 2.2x and 1.6x over a branchless scalar loop for 8-, 16-, 32- and 64-bit elements, with no CPU, compiler, flags, input size or mask distribution given and no benchmark code in the repo (test.cpp checks correctness only). The branchless loop is the fair baseline; the branchy column mostly measures branch mispredictions on random masks.

## Use it when

- Stream compaction or filtering inner loops on x86-64 (Haswell or later, AMD Zen3 or later) where a compare already yields a 32-byte mask: selection vectors in column scans, removing delimiters or spaces from byte buffers, sparse-to-dense packing.
- 8- and 16-bit elements, where the claimed gain over the branchless scalar loop is largest (5.3x and 3.8x).
- Targets without AVX-512 (or without AVX512_VBMI2 for byte/word compress), where VPCOMPRESS is unavailable.
- AMD Zen1/Zen2 fleets, using the \*_Zen2 variants that avoid microcoded PDEP/PEXT.
- Code that can over-allocate the output buffer by 32 bytes and pad the input to whole 32-byte blocks.

## Skip it when

- Anything not x86-64 with AVX2, BMI2 and POPCNT: there is no scalar, SSE, NEON or SVE fallback and no runtime dispatch.
- 64-bit and 32-bit elements if the extra code is not worth 1.6x and 2.2x (the README's own figures against the branchless loop).
- Zen1/Zen2 with the default Leftpack8/Leftpack32: the choice between PDEP and table variants is compile-time and wrong picks are very slow there.
- When you need audited performance numbers: the repo has no benchmark code, and the claim that it beats AVX-512 VCOMPRESS for the bitmask case has no published measurement.
- When you want a whole-array API with tail handling; this is one register per call and always reads and writes 32 bytes.

## How it is fast

The bitmask is turned into a shuffle control without branches: the 8- and 32-bit paths build packed nibble or byte indices with PDEP/PEXT (the classic BMI2 left-pack trick) and then apply PSHUFB or VPERMD; the 16- and 64-bit paths and the Zen2 variants look the index pattern up in 256- or 16-entry nibble tables, expand it with unpack/variable shifts and apply the shuffle. The 8- and 16-bit versions compact each 128-bit half separately and store the two halves with overlapping unaligned stores at pOut and pOut + popcount(low half), so no cross-lane byte permute is needed. Counts come from POPCNT; there is no per-element branch, so random masks do not cause mispredictions.

## Compared with alternatives

Pick it over lemire/despacer when you need a generic compress primitive for 8/16/32/64-bit lanes with an arbitrary integer or vector mask rather than a ready-made whitespace remover with its own benchmark; pick it over EVE's compress_store when you want one dependency-free x86 header instead of a large portable template library that also covers NEON and AVX-512.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (immintrin.h only) |
| **Minimum toolchain** | Header uses C++11 features (alignas, raw-string inline asm); test.cpp needs C++17 (if constexpr). Must be built with AVX2, BMI2 and POPCNT enabled (e.g. -mavx2 -mbmi2 -mpopcnt or -march=haswell). README says GCC, Clang and MSVC; versions not documented. |
| **Platforms** | x86-64 only (AVX2 + BMI2 + POPCNT required, including the _Zen2 variants, whose GCC/Clang path uses SHLX); GCC/Clang get an inline AT&T-asm path for Leftpack8_Zen2, MSVC gets the intrinsics path. |
| **Thread safety** | Not documented; the functions are pure, touch only caller buffers and read-only static constexpr tables, so concurrent calls are safe. |
| **Drop-in for the baseline** | partial: replaces the body of a hand-written 32-byte compaction loop (void\* in/out, mask, returns count), not a library call; the caller supplies the outer loop, 32 bytes of output slack and a padded tail. |

## Gotchas

- Every call loads a full 32 bytes from p and stores a full 32 bytes at pOut regardless of the kept count (8/16-bit versions store at pOut and pOut + popcount(low half)), so the last call in a loop overruns an exact-size output by up to 32 bytes and reads past a short input.
- Mask contracts are not enforced: Leftpack16 indexes its 256-entry table with m &gt;&gt; 8, Leftpack32_Zen2 and Leftpack64 index with m directly, so stray bits above the 16/8/4 valid bits read past the static tables (undefined behaviour); Leftpack32 (PDEP) ignores them for the shuffle but popcounts all 32 bits and returns a wrong count. The 8-bit vector-mask versions need every mask byte to be exactly 0x00 or 0xFF (PEXT uses all bits), while the 16/32/64-bit vector versions read only the sign bit.
- Latent inline-asm defect (found reading leftpack.h, not observed in tests): the GCC/Clang asm in the bitmask Leftpack8_Zen2 reads the 32 input bytes through a plain register operand ("r"(p)) with no "m" input or "memory" clobber, so the compiler may legally sink or drop the caller's preceding stores into that buffer after inlining; test.cpp does not catch this because the reference loop reads the input first. The vector-mask Leftpack8 also passes an uninitialised c1 as a "+r" operand (harmless in practice).
- test.cpp is exhaustive for 16/32/64-bit masks but for the 8-bit versions checks every mask only up to 2^22 and then every 1009th mask; it times nothing, so the README speedup table has no public harness, CPU, compiler, flags or mask distribution behind it.

## Known shortcomings

- No benchmark code (test.cpp is correctness only), no CPU, flags or mask distribution; the VCOMPRESS claim has no numbers; writes 32 bytes at pOut regardless of count.
- No benchmark code; the README table is unreproducible. Latent defects in leftpack.h: the GCC/Clang asm in Leftpack8_Zen2 reads the input through a plain register operand with no 'm' input or 'memory' clobber, so the compiler may sink or drop the caller's stores; Leftpack16, Leftpack32_Zen2 and Leftpack64 index their tables with an unmasked m (out-of-bounds read if high bits are set); Leftpack32 popcounts all 32 bits (wrong count). test.cpp is not exhaustive for the 8-bit versions (every mask to 2^22, then every 1009th).

## Caveats and trade-offs

First-party table only. The repo holds leftpack.h and test.cpp, and test.cpp checks every mask exhaustively against the branchless scalar loop for correctness but times nothing, so the speedups cannot be reproduced from public code. No CPU, compiler, flags, input size or mask distribution are stated. The 'super naive' branchy loop mispredicts on random masks, so the 39x end flatters the result; the branchless loop (1.6x to 5.3x) is the fairer scalar baseline. The claim that it beats AVX-512 VCOMPRESS has no numbers. Every call writes a full 32 bytes at pOut whatever the kept count, so the caller must provide slack. The PDEP/PEXT versions are very slow on Zen1/Zen2. Last commit 2023-10-04, three years and one week before the run date.

x86 AVX2 (8-bit and 32-bit versions use BMI2 PDEP/PEXT, very slow on AMD Zen 1 and Zen 2, so alternative slightly slower implementations are provided); header leftpack.h with test.cpp.

## Maintenance

Nine commits between 2023-09-03 and 2023-10-04, no issues, no releases and 4 stars, so effectively abandoned, but MIT-licensed and a single \~30 KB header that is easy to vendor and audit (fix the asm memory operand and mask the bitmask inputs if you do).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README speedup table (39x/5.3x, 31x/3.8x, 14x/2.2x, 7.8x/1.6x) is first-party with no benchmark code in the repo (test.cpp is a correctness test only) and no CPU, compiler version, flags, sizes or mask distribution.
- **Verifier notes:** Numbers match the README exactly; tier C stays because no benchmark harness exists in the repo. Baseline is the scalar C++ reference loop, which is in the category's baseline list. Small, 4 stars, MIT, header-only.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/Leftpack>
  - <https://github.com/komrad36/Leftpack/commits>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/leftpack.h>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/komrad36/Leftpack>
  - <https://github.com/komrad36/Leftpack/commits>
  - <https://github.com/komrad36/Leftpack/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/leftpack.h>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/komrad36/Leftpack/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemire/despacer/HEAD/README.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/main/include/eve/module/core/compress/compress_store.hpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/komrad36/leftpack`) · [data/wave13/enrich/raw/github_com_komrad36_leftpack.json](../../../data/wave13/enrich/raw/github_com_komrad36_leftpack.json) (enrichment confidence 0.7)

</details>
