# Turbo-Histogram (TurboHist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Scalar C byte-histogram routines for entropy-coder front ends; 1.5x the naive loop on text, up to 22x on runs.

| | |
|---|---|
| **Beats** | Naive single-table byte histogram loop (hist_1_8), plus Ryg's histogram variants and Countbench; the histogram is the counting stage of Huffman, FSE and rANS encoders |
| **Claimed result** | Up to 22 times faster than the naive solution (README headline). Table: on enwik9 hist_8_64 4053.37 MB/s (0.9035 cycles/byte) vs naive hist_1_8 2761.01 MB/s (1.3423); on enwik9.bwt histr_8_64 5135.29 MB/s (0.7229) vs naive 1170.89 MB/s (3.0642); all-zeros histr_8_64 reaches 19629.28 MB/s vs naive 877.27 MB/s. |
| **Workload** | Byte-frequency histogram construction over 1 GB inputs (enwik9 text, enwik9 after BWT, and all zeros), single thread, large-file benchmark rather than cache-resident. |
| **Metric** | throughput |
| **Hardware** | Intel i7-9700K 3.6GHz |
| **Compiler and flags** | gcc 11.2 (README); the makefile builds with -O3 -fstrict-aliasing -falign-loops plus -march=corei7-avx by default or -march=haswell with AVX2=1, but the README does not say which configuration produced the table |
| **Adoption** | 74 stars |
| **Last commit** | 2021-12-29 |
| **Links** | [repository](https://github.com/powturbo/Turbo-Histogram) · [benchmark](https://github.com/powturbo/Turbo-Histogram) |

## Verdict

First-party single-thread benchmark on an Intel i7-9700K with gcc 11.2 over 1 GB inputs, every variant checked against the naive count: hist_8_64 4053 MB/s vs naive 2761 MB/s on enwik9, histr_8_64 5135 vs 1171 MB/s on enwik9.bwt and 19629 vs 877 MB/s on all zeros (the 22x headline). Against Ryg's assembly histograms the lead is small: 4053 vs 4133 MB/s (Ryg var3 is faster on enwik9), 5135 vs 4642 MB/s on BWT and 19629 vs 14076 MB/s on zeros.

## Use it when

- The counting pass in front of a block entropy coder (Huffman, FSE, rANS) on blocks of KB to GB, single thread
- Skewed or run-heavy data (BWT output, sparse images, zero-filled regions): histr_8_64 measured 5135 MB/s vs 1171 MB/s naive on enwik9.bwt and 19629 vs 877 MB/s on zeros
- Portable C without SIMD or assembly requirements: the fastest rows are plain scalar C, so the same code serves x86-64, aarch64 and ppc64le builds
- As a reference when tuning your own histogram loop: the driver checks every variant against the naive count and reports MB/s and cycles/byte

## Skip it when

- Uniform, high-entropy data where the gain is modest: on enwik9 text hist_8_64 is 4053 MB/s vs 2761 MB/s naive (about 1.47x, derived from page data)
- Inputs of 4 GiB or more in one call, or counts above 2^32-1: lengths and counters are 32-bit unsigned
- Small buffers (a few hundred bytes): each call zeroes and later sums 8 x 264 counters (about 8.4 KB of stack), which can outweigh the counting; the 64-bit variants only enter the fast loop for inlen &gt;= 72-80 bytes
- Multi-threaded or 16-bit-symbol histograms: only single-thread 8-bit symbol counting is implemented
- Projects that need a maintained, versioned library: no releases, no header, last commit 2021-12-29

## How it is fast

It spreads increments over 4 or 8 separate count tables so consecutive equal bytes do not serialize on a store-to-load forwarding dependency, then sums the tables at the end in an auto-vectorizable loop. It reads 32- or 64-bit words and extracts bytes with shifts (x86 uses the high-byte trick via unsigned short casts), prefetches 512 bytes ahead, and pads each table to 256+8 counters to avoid 4K aliasing between tables (issue #2). The histr_\* variants compare two 64-bit words and, when 16 bytes are one repeated value, add 16 to a single counter, which is where the 19.6 GB/s all-zeros figure comes from.

## Compared with alternatives

The sibling entries (FiniteStateEntropy, hypersonic-rANS, htscodecs, rans_static) are coders, not histogram routines; use TurboHist as their counting stage when profiling shows the frequency pass matters, especially on BWT or run-heavy blocks where its run-aware histr_8_64 is 1.1x Ryg's best asm and 4.4x the naive loop.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the functions (conf.h supplies ctou32/ctou64, likely and ALWAYS_INLINE macros; sse_neon.h only for the SSE/NEON variants) |
| **Minimum toolchain** | GCC &gt;= 4.6 or Clang &gt;= 3.2 on Linux, MinGW-w64 on Windows, Xcode &gt;= 9 on macOS, gcc &gt;= 6.3 on aarch64, gcc &gt;= 8.0 on ppc64le (README); C99 with GCC builtins |
| **Platforms** | x86-64 and i386 (default build -march=corei7-avx; AVX2=1 uses -march=haswell), aarch64, Apple M1, ppc64le; hist_8_64a inline-asm variant is x86-64 only |
| **Thread safety** | Not documented; the code keeps all count tables on the stack and has no global state, so separate calls on separate buffers do not share data |
| **Drop-in for the baseline** | partial: same signature shape as a naive count loop (input, length, 256-entry counts), but you must copy the static function and the conf.h load macros |

## Gotchas

- The README advertises a 'C++ compatible header', but no header exists in the repo (turbohist.h returns 404); the functions are static in turbohist_.c.
- Table rows came from a build whose flags are not stated (default -march=corei7-avx or AVX2=1 -march=haswell), so expect different ratios with other flags; the SSE4.1 and AVX2 variants were slower than the scalar 64-bit ones on the i7-9700K.
- hist_8_64a is declared to return unsigned but has no return statement; do not use its return value.
- The disabled '#else' table-reduction path mixes _mm256_add_epi32 with __m128i in its SSE branch and would not compile if enabled; leave the default '#if 1' summation.

## Known shortcomings

- Tier C: a byte-histogram stage, off-centre for the category, with its own naive loop as the only baseline; the makefile gives -O3 with -march corei7-avx or haswell but the README does not say which build made the table. Last commit 2021-12-29, abandoned.
- README promises a C++-compatible header but none exists (turbohist.h 404; functions are static in turbohist_.c). Lengths and counters are 32-bit (max 4 GiB). Ryg's var3 asm beats hist_8_64 on enwik9 (4133 vs 4053 MB/s). hist_8_64a is declared unsigned but has no return. The disabled #else SSE reduction would not compile. Issue #2 (4K aliasing) was fixed by table padding.

## Caveats and trade-offs

Off-center for the category: it speeds up the histogram stage of an entropy coder, and the 'naive' baseline is the project's own scalar loop, so the headline 22x is on skewed or constant data where the naive loop stalls on store-to-load dependencies. On ordinary text the gain over naive is about 1.5x (derived from page data: 4053 vs 2761 MB/s). Flags not stated; README is first-party. Its fastest listed row is an inline-asm variant (hist_8_64asm 4161.87 MB/s) and Ryg asm variants reach 4132.54 MB/s, so the portable C win over the best third-party asm is small. License file is the two-clause BSD text without an SPDX header; the SPDX id is inferred from the text.

C with a C++-compatible header, no inline assembly in the main functions (an optional inline-asm variant is also provided). Counts bytes only; it is a building block for entropy coders, not a coder itself.

## Maintenance

Abandoned since 2021-12-29 (102 commits, 74 stars, no releases, no open issues) but BSD-2-Clause and a few dozen lines per function, so easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (i7-9700K, gcc 11.2) compares against the project's own naive loop plus Ryg's and Countbench's histogram code, and the benchmark driver (turbohist.c, makefile) is public; but the README does not say which makefile options (AVX2=1 or default, RDTSC) produced the table, so the flags used are not stated and the tier stays C.
- **Verifier notes:** All quoted numbers check out (enwik9: hist_1_8 2761.01, hist_8_64 4053.37, hist_8_64asm 4161.87, Ryg var3 4132.54 MB/s; enwik9.bwt histr_8_64 5135.29 vs 1170.89; zeros 19629.28 vs 877.27). Last commit 2021-12-29 is more than 3 years ago, so maintenance_status moves from stale to abandoned. On enwik9.bwt Ryg's histo_asm_scalar8_var5 reaches 4642.10 MB/s and on zeros 14076.09 MB/s, so TurboHist's lead over the best third-party code there is about 1.1x and 1.4x (derived from page data).
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; first-party benchmark; driver checks every variant against a naive count
- **Pages the verifier opened:**
  - <https://github.com/powturbo/Turbo-Histogram>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/README.md>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/makefile>
  - <https://github.com/powturbo/Turbo-Histogram/commits>
- **Sources the enricher read:**
  - <https://github.com/powturbo/Turbo-Histogram>
  - <https://github.com/powturbo/Turbo-Histogram/issues?q=is%3Aissue>
  - <https://github.com/powturbo/Turbo-Histogram/issues/2>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/README.md>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/makefile>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/turbohist.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/turbohist_.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/conf.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Histogram/HEAD/turbohist.h>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/powturbo/turbo-histogram`) · [data/wave9/enrich/raw/github_com_powturbo_turbo_histogram.json](../../../data/wave9/enrich/raw/github_com_powturbo_turbo_histogram.json) (enrichment confidence 0.8)

</details>
