# TurboRC (Turbo Range Coder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟢 active

> GPL C library of adaptive range coders, adaptive-CDF rANS and a BWT compressor that beats bzip2 on ratio everywhere and on speed on some files.

| | |
|---|---|
| **Beats** | Other range/arithmetic and adaptive ANS coders (unnamed in the README; listed only on an external benchmark page); BWT section compares head-to-head with bzip2, bsc and bzip3 |
| **Claimed result** | README text: 'up to 3 times faster than the next fastest range coder with similar compression ratio' (competitor numbers only on the external Entropy Coder Benchmark page). enwik8bwt table (own variants only): ans auto 116.76 MB/s encode / 202.27 MB/s decode at 24.85%; static interleaved cdfsb 628.18 MB/s encode / 92.24 MB/s decode at 63.54%. BWT section (2026-10), head-to-head vs bzip2, bsc, bzip3: NASA access log, TurboRC 20e8 38.69 MB/s compress / 106.37 MB/s decompress at 4.40% vs bzip2 15.71 / 83.16 MB/s at 5.8% (2.5x faster compress, 1.3x faster decompress, smaller output; derived from page data); enwik8, TurboRC 20e8 17.42 / 36.21 MB/s at 20.98% vs bzip2 20.72 / 43.39 MB/s at 29.0% (better ratio, slower than bzip2) and vs bzip3 10.70 / 9.19 MB/s at 20.75% (derived from page data: 1.6x compress, 3.9x decompress at slightly worse ratio). |
| **Workload** | Benchmarks of range coder and rANS variants on BWT-transformed enwik8 (100 MB), plus BWT compressor comparison on enwik8 and Silesia. |
| **Metric** | throughput |
| **Adoption** | 96 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/powturbo/Turbo-Range-Coder) · [benchmark](https://github.com/powturbo/Turbo-Range-Coder) |

## Verdict

The README's enwik8bwt table compares only TurboRC's own coders (for example 'ans auto' 116.76 MB/s encode and 202.27 MB/s decode at 24.85%; o0 range coder 88.20/88.54 MB/s at 23.33%); the 2026-10 BWT tables show TurboRC beating bzip2 on ratio everywhere and on both speeds on the NASA log (2.5x compress, 1.3x decompress, derived from page data), while trading wins with bsc. No CPU, compiler or flags are stated, and the '3x faster than the next fastest range coder' headline is backed only by an external sites.google.com page that is blocked here.

## Use it when

- You need an adaptive (per-symbol updated) entropy coder, bitwise or multi-symbol, with context models or mixing, and want a fast tested implementation instead of writing your own range coder
- Coding integer streams (gamma, Rice, large-integer VLC, zigzag delta) or 8/16/32-bit data where adaptive range coding beats static Huffman or tANS on ratio
- A BWT compressor that outperforms bzip2 on ratio on every listed corpus and on speed on logs: NASA access log at level 20e8 gives 4.40% at 38.69/106.37 MB/s vs bzip2 5.8% at 15.71/83.16 MB/s
- Adaptive-CDF rANS when decode speed matters more than encode: 'ans auto' on enwik8bwt decodes at 202.27 MB/s vs 88.54 MB/s for the order-0 range coder at about 1.5 points worse ratio
- GPL-3.0 projects, or commercial projects willing to buy the offered commercial license

## Skip it when

- Static order-0 entropy coding at maximum throughput: README rANS/CDF rows are in the 100-630 MB/s range, while siblings hypersonic-rANS (about 3 GB/s enwik8 decode), FSE/Huff0 and pivco-huffman are an order of magnitude faster
- Proprietary code without a commercial license: GPL-3.0 applies to the library as well as the CLI
- When you need a documented stable container format or API reference: usage is 'see examples in turborc.c', raw codecs have no framing and the caller must keep the original length
- Fast BWT decompression on general text: bzip2 decompresses faster than TurboRC 20e8 on enwik8 (43.39 vs 36.21 MB/s), Silesia (52.14 vs 34.69) and enwik9 (46.46 vs 37.90), and bsc 0e0 is slightly faster on enwik8 and Silesia at a slightly larger size
- If you need independently reproduced numbers: no CPU, compiler or flags are given for the README tables and the '3x faster than the next fastest range coder' claim lives only on an external page

## How it is fast

The range coder is written branchless (renormalization and bit coding without data-dependent branches) and offers 8/16/32-bit renormalization output; adaptive models are simple shift-based probability counters. The rANS path updates an adaptive CDF and is compiled three times (scalar, SSE, AVX2) with a runtime dispatcher (anscdfini), plus 2-way interleaved static CDF coders. The BWT pipeline uses libsais for the suffix array, optional 16-bit BWT, LZP and UTF-8 preprocessing, and QLFC (quantized local frequency coding) feeding the range coder instead of MTF plus Huffman as in bzip2.

## Compared with alternatives

Pick TurboRC when you need adaptive or context-modelled coding (bitwise, order-1/2, mixing, integer VLC) or a ready BWT compressor; for static order-0 throughput, hypersonic-rANS, htscodecs, FSE/Huff0 or ryg_rans-style interleaved rANS are faster and more permissively licensed.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | libsais (git submodule, clone with --recursive) for BWT; bundled libdivsufsort optional; pthread and libm on Linux |
| **Minimum toolchain** | C; README lists GCC &gt;= 4.6, Clang &gt;= 3.2, Visual C++ 2022, MinGW-w64, Xcode &gt;= 9 |
| **Platforms** | x86-64 (default build uses -mavx -mpopcnt; make AVX2=1 adds -march=haswell), aarch64, RISC-V (rv64gcv), ppc64le, s390x, Apple M-series; 32 and 64-bit |
| **Thread safety** | not documented; anscdfini() sets global function pointers for SIMD dispatch, so call it once before using codecs from several threads. rcbwtenc takes a thread-count argument, but the BWT path read in rcbwt.c calls libsais single-threaded |
| **Drop-in for the baseline** | partial: the turborc CLI compresses files like bzip2 but uses its own format (no bzip2 compatibility); library codecs are a custom buffer API, not zlib/bzip2-compatible |

## Gotchas

- Output buffers must be at least inlen bytes; if the result equals inlen the input was incompressible and was copied verbatim, so the caller must record that and the original length
- Default x86-64 make adds -mavx, so a default build will not run on pre-AVX CPUs; pick SIMD level at build time
- Open issue #7 (Dec 2023, no maintainer reply) reports errors in the ans codecs on Linux ARMv8 with attached data; closed issue #2 was a level 25 decompression failure on enwik8 (2020); build failures on macOS were reported in #5 and #6 (closed)
- include/anscdf.h uses cdf_t, which is defined in include/turborc.h, so include turborc.h first

## Known shortcomings

- Tier C: the '3x faster' headline is unbacked in the README (its sites.google.com source is blocked); the BWT section's head-to-head gives NASA log 20e8 38.69/106.37 MB/s vs bzip2 15.71/83.16 but it is slower than bzip2 on enwik8 and Silesia. No CPU, compiler or flags.
- Issue #7 ('Some errors in ans' on ARMv8) open since Dec 2023 with no reply; the default x86 build needs AVX; no CPU, compiler or flags for any table. bzip2 decompresses faster than TurboRC 20e8 on enwik8, Silesia and enwik9. The '3x faster' claim exists only on a blocked sites.google.com page. rcbwtenc accepts a thread count but the BWT path calls libsais single-threaded.

## Caveats and trade-offs

Headline '3x faster than the next fastest range coder' is not backed by a competitor table in the README; the linked sites.google.com benchmark page is blocked here and was not read. No CPU, compiler or flags stated for any table. Marketing wording ('no other ... faster'). In the BWT section TurboRC beats bzip2 on ratio everywhere but is slower than bzip2 on enwik8, Silesia and enwik9; its speed-and-ratio win over bzip2 is clearest on the NASA log and html8 at the 20e8 level. GPL-3.0 with a commercial license on offer.

GPL-3.0 with a commercial license offered; build via make; suffix-array dependencies (libsais, libdivsufsort) for the BWT part; supports SSE, AVX2, NEON, RVV.

## Maintenance

Actively maintained (README updated 1 Oct 2026, last commit 2026-10-02) by a single author since 2013; GPL-3.0 with a commercial license on request, built via make or Visual Studio projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables: the enwik8bwt table lists only TurboRC's own coder variants (the '3x faster' range-coder claim points to an external sites.google.com page, EGRESS_BLOCKED here), while the 2026-10 BWT section compares TurboRC head-to-head with bzip2, bsc and bzip3; no CPU, compiler or flags are stated, so C.
- **Verifier notes:** Metadata confirmed (GPL-3.0, 96 stars, last commit 2026-10-02, not a fork). The BWT tables give the entry a recognizable incumbent (bzip2) even though the range-coder headline is unbacked on the page.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/powturbo/Turbo-Range-Coder>
  - <https://github.com/powturbo/Turbo-Range-Coder/commits>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/README.md>
  - <https://github.com/powturbo/Turbo-Range-Coder>
  - <https://github.com/powturbo/Turbo-Range-Coder/tree/master/include>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/include/turborc.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/include/anscdf.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/makefile>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/rcbwt.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Range-Coder/HEAD/turborc.c>
  - <https://github.com/powturbo/Turbo-Range-Coder/issues?q=is%3Aissue>
  - <https://github.com/powturbo/Turbo-Range-Coder/issues/7>
  - <https://github.com/powturbo/Turbo-Range-Coder/issues/4>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/powturbo/turbo-range-coder`) · [data/wave9/enrich/raw/github_com_powturbo_turbo_range_coder.json](../../../data/wave9/enrich/raw/github_com_powturbo_turbo_range_coder.json) (enrichment confidence 0.75)

</details>
