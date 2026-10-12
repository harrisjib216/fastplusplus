# sse-popcount

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Reference SIMD popcount kernels (Harley-Seal, PSHUFB lookup) that beat the POPCNT loop 1.8x to 3.6x on kilobyte buffers.

| | |
|---|---|
| **Beats** | scalar hardware POPCNT instruction loop (cpu / builtin-popcnt via __builtin_popcountll), plus lookup-table and bit-parallel scalar versions |
| **Claimed result** | Cascade Lake Xeon Gold 6240, gcc 8.3.0, 4096 B: avx512-harley-seal 0.04826 s versus cpu (64-bit POPCNT loop) 0.17391 s and builtin-popcnt 0.25037 s, about 3.6x and 5.2x; avx2-harley-seal 0.09748 s versus cpu 0.17391 s, about 1.8x; against the fastest scalar row (builtin-popcnt-unrolled-errata 0.16751 s) about 3.5x for AVX-512 and 1.7x for AVX2 (all derived from page data). The POPCNT loop wins up to 512 B: avx512-harley-seal 2.99407 s versus cpu 0.30912 s at 32 B and 0.25122 s versus 0.16864 s at 512 B; the AVX-512 version first wins at 1024 B (0.09325 s versus 0.19950 s). Haswell i7-4770, gcc 5.3.0: avx2-harley-seal 0.11145 s versus cpu 0.19857 s at 4096 B, about 1.8x (derived from page data). |
| **Workload** | Population count over 32 B to 4096 B buffers, repeated a fixed number of times (5 runs), times reported in seconds per procedure; AVX2/AVX-512 Harley-Seal and PSHUFB-lookup versus scalar POPCNT. |
| **Metric** | throughput |
| **Hardware** | Cascade Lake Xeon Gold 6240 @ 2.6 GHz (AVX512BW), generated 2021-02-24; the repo also has Haswell i7-4770, Skylake i7-6700, Skylake-X, Cannon Lake i3-8121U, Sandy Bridge-E, Westmere, Bulldozer and ARM result files |
| **Compiler and flags** | GCC 8.3.0 (crosstool-NG 1.24.0) for the Cascade Lake run (2021-02-24). Flags are not printed in the result file; the Makefile in force at that date (commit ba36276, 2019-12-08; next Makefile change 2023-08-20) sets -std=c++11 -O2 -Wall -pedantic -Wextra -Wfatal-errors -mpopcnt -fabi-version=6 plus -mavx512bw -DHAVE_AVX512BW_INSTRUCTIONS for the AVX512BW target (the current Makefile uses -std=c++17). |
| **Adoption** | 357 stars; companion repo of the Muła, Kurz and Lemire paper 'Faster Population Counts Using AVX2 Instructions' (arXiv 1611.07612, Computer Journal 2018) |
| **Last commit** | 2024-04-01 |
| **Links** | [repository](https://github.com/WojciechMula/sse-popcount) · [benchmark](https://github.com/WojciechMula/sse-popcount/blob/master/results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.rst) |

## Verdict

In the authors' Cascade Lake file (Xeon Gold 6240, GCC 8.3.0 crosstool-NG, flags from the Makefile of the time -std=c++11 -O2 -mpopcnt -mavx512bw; run.sh pins core 0 with taskset and keeps the minimum of 5 runs of a std::chrono-timed loop over one 64-byte-aligned L1-resident buffer), avx512-harley-seal took 0.04826 s and avx2-harley-seal 0.09748 s against 0.17391 s for the 4x-unrolled _popcnt64 loop at 4096 B (3.6x and 1.8x, derived), and 0.09325 s against 0.19950 s at 1024 B (2.1x), while POPCNT-based rows win from 32 to 256 B and AVX-512 still loses at 512 B. The Haswell i7-4770 GCC 5.3.0 file shows 0.11145 s against 0.19857 s at 4096 B (1.8x); the paper abstract, seen only as a WebSearch snippet because arXiv is blocked here, claims up to twice the speed of POPCNT on recent Intel processors.

## Use it when

- Bit counting over buffers of about 1 KB or more on x86 with AVX-512BW or AVX2 (bitset cardinality, bitmap indexes, Hamming or Jaccard similarity over fingerprints): AVX-512 Harley-Seal is 2.1x the POPCNT loop at 1 KB and 3.6x at 4 KB on Cascade Lake; AVX2 Harley-Seal is about 1.8x at 4 KB on Haswell and Cascade Lake.
- Buffers around 512 B on AVX2 machines, where the unrolled PSHUFB kernel (avx2-lookup) was the fastest row on both Haswell and Cascade Lake: about 17% ahead of the POPCNT loop on Haswell (0.17204 s against 0.20636 s) but only about 3.5% on Cascade Lake (0.16273 s against 0.16864 s), derived from page data.
- Reading or porting a reference implementation: each kernel is 50 to 100 lines of intrinsics under BSD-2-Clause.
- Measuring popcount strategies on a new CPU: results/\*/run.sh, speed --csv and scripts/report.py regenerate the published tables.

## Skip it when

- Buffers under about 512 B: the POPCNT loop or an unrolled __builtin_popcountll with separate accumulators wins; AVX-512 Harley-Seal is 9.7x slower at 32 B (2.99407 s against 0.30912 s) and still slower at 512 B (0.25122 s against 0.16864 s).
- When you want a packaged library with runtime CPU dispatch and a stable API: kimwalisch/libpopcnt (catalogued in wave 11) ships these algorithms that way.
- CPUs with AVX-512 VPOPCNTDQ (the repo's avx512-vpopcnt kernel targets it): the repo publishes no numbers for that kernel, and its tail handling is wrong for sizes that are not multiples of 64 (see gotchas).
- Data far larger than cache: the published tables re-count one L1-resident buffer of 32 B to 4 KB millions of times, so they say nothing about memory-bound streaming, where the gap to POPCNT should shrink.

## How it is fast

The Harley-Seal kernels treat 16 consecutive vectors as bit-sliced inputs to a tree of carry-save adders (CSA, built from AND/OR/XOR on AVX2 and from two vpternlogd per adder on AVX-512), so only one vector in 16 needs a real per-byte count (SWAR nibble arithmetic, then vpsadbw to sum bytes into 64-bit lanes); leftover ones/twos/fours/eights accumulators are counted once at the end. The PSHUFB kernels split each byte into nibbles and use pshufb as a 16-entry lookup table, summing with vpsadbw. Either way one short instruction sequence handles 32 or 64 bytes, while the scalar loop issues one POPCNT per 8-byte word.

## Compared with alternatives

libalgebra packages similar AVX2/AVX-512 popcount and set-algebra kernels but reports speedups against an 8-bit-lookup scalar baseline with auto-vectorization disabled, and positional-popcount solves a different problem (per-bit-position counts over 16-bit words); pick sse-popcount when you want the original single-file kernels with an honest comparison against the hardware POPCNT loop, or libpopcnt (wave 11) when you want them packaged with dispatch.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond &lt;immintrin.h&gt;/&lt;x86intrin.h&gt; (or arm_neon.h, riscv_vector.h); tails use the lookup8bit table from popcnt-lookup.cpp and config.h's FORCE_INLINE |
| **Minimum toolchain** | Current Makefile: -std=c++17 -O2 -mpopcnt -fabi-version=6 plus -mssse3, -mavx2, -mavx512bw, -mavx512vbmi or -mavx512bw -mavx512vpopcntdq per target (C++11 until the 2023-08-20 switch); published results were built with GCC 4.8.4 to 8.3.1 and Clang 3.8.0 |
| **Platforms** | x86-64 (SSSE3, AVX, AVX2, AVX-512BW, AVX-512VBMI, AVX-512VPOPCNTDQ variants chosen at compile time), ARMv7 NEON, AArch64, RISC-V Vector (added 2024-04-01, tested under the Spike emulator) |
| **Thread safety** | not documented; the kernels are pure functions over const input that only read global lookup tables, so concurrent calls on separate or shared read-only buffers are safe by code reading |
| **Drop-in for the baseline** | partial — replaces a loop of _popcnt64/__builtin_popcountll over a buffer with one call f(const uint8_t\*, size_t), but there is no runtime dispatch, so you must pick the kernel matching your build flags and keep a POPCNT path for short buffers |

## Gotchas

- AVX-512 VPOPCNTDQ tail bug (code reading, not run): the masked tail added on 2024-03-26 (PR #22) builds an 8-lane uint64 mask from the remaining byte count, (__mmask8)_bzhi_u32(0xFFFFFFFF, end - ptr), so for any size that is not a multiple of 64 it loads and counts whole 8-byte lanes past the end of the buffer (all 8 lanes, 64 bytes, whenever 8 or more bytes remain): wrong totals plus an over-read. verify only tests one 1024-byte buffer, so it cannot catch this; none of the published result files include this kernel.
- The AVX2 and AVX-512 Harley-Seal kernels cast the byte pointer to __m256i\* or __m512i\* and dereference it, which is an aligned-type access: give them 32- or 64-byte-aligned buffers (speed and verify allocate 64-byte-aligned memory); misaligned input is undefined behaviour and can fault if the compiler emits an aligned move.
- Below 1024 B the 'avx512-harley-seal' row is not Harley-Seal: the carry-save loop needs 16 x 64 B, so smaller buffers go through a per-vector SWAR loop, and buffers under 64 B through the 8-bit lookup table, which explains its 32 B result; AVX2 Harley-Seal likewise needs 512 B.
- results/cascadelake/run.sh times 3.2 GB per cell for 32 to 256 B (for example 32 B x 100,000,000 calls) but 5.12 GB per cell for 512 to 4096 B (512 B x 10,000,000), so times compare within a column but not across the 256/512 boundary; at 4096 B the cells work out to about 106 GB/s for avx512-harley-seal, 52.5 GB/s for avx2-harley-seal and 29.4 GB/s for the POPCNT loop (derived from page data).

## Known shortcomings

- Cascade Lake and Haswell numbers match (2019 Makefile ba36276: -std=c++11 -O2 -mpopcnt -mavx512bw) but are old L1-hot runs by the authors; the POPCNT loop wins through 512 B and AVX-512 first wins at 1024 B. libpopcnt (wave 11) is the library form.
- Tier A numbers sound (public run.sh, CSV, taskset, min of 5). run.sh times 3.2 GB per cell at 32-256 B but 5.12 GB at 512-4096 B, so columns are not comparable across that boundary; below 1024 B the 'avx512-harley-seal' row runs SWAR or the byte LUT, not Harley-Seal. Code-reading bug: the avx512-vpopcnt tail (PR #22, 2024-03-26) uses the leftover byte count as an 8-lane mask, giving wrong totals and an over-read when size % 64 != 0 (no published numbers use that kernel); the Harley-Seal kernels dereference aligned __m256i and __m512i pointers.

## Caveats and trade-offs

Result files are old (Haswell 2016-03-26 with GCC 5.3.0; Cascade Lake 2021-02-24 with GCC 8.3.0) and were run by the authors; flags are inferred from the Makefile of the time, not printed in the result file. The speed.cpp harness re-counts one cache-resident buffer filled with i & 0xFF for a fixed iteration count, so the tables measure L1-hot throughput. Baseline is the scalar POPCNT instruction loop, a strong baseline; SIMD wins only from about 1 KB on Cascade Lake (AVX-512 Harley-Seal is about 10x slower than POPCNT at 32 B and still slower at 512 B). This repo is sample/benchmark code for the Mula, Kurz and Lemire paper 'Faster Population Counts Using AVX2 Instructions' (arXiv 1611.07612, Computer Journal 2018; paper not opened, arXiv blocked); the packaged library form is kimwalisch/libpopcnt (already listed in wave 11).

x86-specific sample programs (SSSE3/AVX2/AVX-512BW/VBMI), not a packaged library; needs a CPU with the matching extension and loses to the POPCNT instruction below roughly 512 B; kimwalisch/libpopcnt is the packaged, runtime-dispatched version of the same ideas.

## Maintenance

Stale (last commit 2024-04-01 added a RISC-V Vector kernel; 2023 and 2024 changes came from outside pull requests), BSD-2-Clause sample code that is easy to vendor kernel by kernel; the catalogued numbers are sound (public run.sh, CSV and Makefile), but copy kernels with care because the aligned-pointer casts and the 2024 VPOPCNTDQ tail mask bug (byte count used as a lane mask, found in code reading) are outside verify's single 1024-byte test.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.rst states the CPU (Xeon Gold 6240), compiler (gcc 8.3.0) and instruction set, and its table shows avx512-harley-seal 0.04826 s and avx2-harley-seal 0.09748 s against the scalar POPCNT loop (cpu) 0.17391 s at 4096 B; the harness is the public speed.cpp and the flags come from the public Makefile in force when the file was generated (ba36276, Dec 2019, unchanged until Aug 2023: -std=c++11 -O2 -mpopcnt -fabi-version=6 -mavx512bw).
- **Verifier notes:** Numbers verified on the Cascade Lake and Haswell result files; the record's crossover was slightly off (POPCNT wins through 512 B, not only 32-256 B) and is corrected. Not a duplicate of libpopcnt (wave 11): this is the original harness and algorithm source, libpopcnt is the library that adopted the algorithms; the orchestrator may want to cross-link them. Last commit 2024-04-01 (RISC-V Vector implementation), 357 stars, BSD-2-Clause confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WojciechMula/sse-popcount>
  - <https://github.com/WojciechMula/sse-popcount/commits/master>
  - <https://github.com/WojciechMula/sse-popcount/commits/master/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/haswell/haswell-i7-4770-gcc5.3.0-avx2.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/ba36276948036517beb593b01e55efc931bb960a/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/LICENSE>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-cpu.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-builtin.cpp>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/sse-popcount>
  - <https://github.com/WojciechMula/sse-popcount/commits/master>
  - <https://github.com/WojciechMula/sse-popcount/commits/master/popcnt-avx512-vpopcnt.cpp>
  - <https://github.com/WojciechMula/sse-popcount/issues?q=is%3Aissue>
  - <https://github.com/WojciechMula/sse-popcount/tree/master/scripts>
  - <https://github.com/WojciechMula/sse-popcount/tree/master/results/cascadelake>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/ba36276948036517beb593b01e55efc931bb960a/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/verify.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/config.h>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-all.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/function_registry.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/sse_operators.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-lookup.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-cpu.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-builtin.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-harley-seal.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-avx2-harley-seal.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-avx512-harley-seal.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-avx2-lookup.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-sse-lookup.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/popcnt-avx512-vpopcnt.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.csv>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/cascadelake/cascadelake-Xeon-Gold-6240-gcc-8.3.0.metadata>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/cascadelake/run.sh>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/results/haswell/haswell-i7-4770-gcc5.3.0-avx2.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/scripts/report.py>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/scripts/data.py>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/scripts/metadata.py>
  - <https://raw.githubusercontent.com/WojciechMula/sse-popcount/master/scripts/main-pattern.rst>
  - WebSearch snippet: arXiv 1611.07612 abstract (Faster Population Counts Using AVX2 Instructions)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wojciechmula/sse-popcount`) · [data/wave13/enrich/raw/github_com_wojciechmula_sse_popcount.json](../../../data/wave13/enrich/raw/github_com_wojciechmula_sse_popcount.json) (enrichment confidence 0.88)

</details>
