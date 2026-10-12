# Fast LZMA2 (fast-lzma2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause OR GPL-2.0-only` · 🟢 active

> LZMA2 encoder with a radix match finder: 1.3-1.6x faster than xz or the LZMA SDK at matching ratio, multithreaded, standard LZMA2 output.

| | |
|---|---|
| **Beats** | xz |
| **Claimed result** | README: 20% to 100% speed gain at the higher levels over the default LZMA2 encoder in 7-Zip 19.00, for a small ratio loss (two threads, Silesia, chart only). lzbench 2.4 single thread (EPYC 9555P, silesia.tar): fastlzma2 1.0.1 -8 compress 4.52 MB/s at 23.18% vs xz 5.8.4 -7 3.01 MB/s at 23.15% (1.5x at matched ratio, derived from page data) and vs xz -9 2.75 MB/s at 23.01% (1.6x, derived from page data); -10 3.38 MB/s at 22.96% vs lzma 26.03 -9 2.55 MB/s at 22.97% (1.3x, derived from page data). |
| **Workload** | LZMA2 compression of silesia.tar vs reference LZMA2 (7-Zip 19.00 in the README; xz and LZMA SDK in lzbench). |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 347 stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/conor42/fast-lzma2) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P with turbo off, silesia.tar) shows fastlzma2 1.0.1 -8 compressing at 4.52 MB/s to 23.18% vs xz 5.8.4 -7 at 3.01 MB/s to 23.15% (1.5x, derived from page data), and -10 at 3.38 MB/s to 22.96% vs lzma 26.03 -9 at 2.55 MB/s to 22.97% (1.3x, derived from page data); decompression in the same run is 79 MB/s vs xz's 122-124 MB/s. The README's 20%-100% gain over 7-Zip 19.00's LZMA2 encoder is a first-party two-thread chart with no numbers.

## Use it when

- Building .xz/.7z-style archives, package payloads or backups at high LZMA2 levels where compression time dominates and decoders must stay standard LZMA2.
- Multi-core compression of large single inputs: the radix match finder threads within one stream instead of splitting the file into independent chunks, so ratio holds up as thread count rises.
- Replacing the LZMA SDK or liblzma encoder in a C or C++ tool that already handles raw LZMA2 or 7z containers (or through FXZ Utils when the .xz format and a liblzma-like API are needed).
- Inputs of tens to hundreds of MB, where dictionaries of 16-128 MB and the higher levels (5-10) give the largest speed gain over the reference encoder.

## Skip it when

- Decode-bound workloads: decompression is no faster than LZMA SDK (lzbench 2.4: 78.5-79.1 MB/s vs lzma 26.03 at about 78 MB/s) and slower than xz 5.8.4's decoder in the same run (122-124 MB/s).
- Low levels: at -1 the single-thread gain over xz -1 is small (21.8 vs 19.2 MB/s at 27.85% vs 27.75%); zstd or bzip3 cover the fast-but-strong range better.
- Memory-constrained decoders: matching 7-Zip's ratio needs about twice the dictionary (README), and the lzbench rows that beat xz use large dictionaries (level 8: 64 MB, level 10: 128 MB per the level table in fl2_compress.c), which sets the decompressor's memory.
- Projects that need an actively released library: the last tag is v1.0.1 (2019); development was idle from Aug 2020 to Oct 2025, and two later encoder memory-safety fixes exist only on master.
- Callers expecting a drop-in .xz file writer from this repository alone: the native output is a raw LZMA2 stream with a property byte, not an .xz container.

## How it is fast

The core is a block-based radix match finder: it builds a match table for a whole dictionary-sized block by bucketing positions on their first one or two bytes and recursively lengthening and splitting the buffered chains up to a search depth, which parallelizes across threads without splitting the input into independent chunks or duplicating hash chains (extra memory per thread is a few MB, per the README). Higher levels add a hybrid mode with a small HC3 hash chain for short matches, and the encoder uses 7-Zip's optimal-parse LZMA2 encoder with some of Igor Pavlov's 18.05 improvements plus zstd-derived threading code. On x86-64 the Makefile also builds Igor Pavlov's assembler-optimized LZMA decoder (LZMA2_DEC_OPT), and multi-threaded decoding is possible because the encoder inserts dictionary resets every 4 dictionary sizes by default.

## Compared with alternatives

Pick Fast LZMA2 over xz/liblzma when you must emit standard LZMA2 for existing decoders and want the encode faster (1.5x at matched ratio single-threaded, more with threads); pick bzip3 or Kanzi instead when the format is free to change, since lzbench shows bzip3 -5 at 11.9 MB/s and a better ratio than any fastlzma2 level.

## Integration

| | |
|---|---|
| **Form** | static lib / shared lib (GNU make builds both; VS2015 solution for a DLL) |
| **Dependencies** | none beyond pthreads (bundled xxhash, optional via NO_XXHASH) |
| **Minimum toolchain** | C compiler with GNU make (gcc -O2 -pthread by default) or Visual Studio 2015; no CMake file in current releases |
| **Platforms** | portable C, 32- and 64-bit (32-bit dictionaries capped at 128 MB, 64-bit at 1 GB); x86-64 gets an optional assembler decoder |
| **Thread safety** | not documented as such; state lives in per-call or caller-owned FL2_CCtx/FL2_DCtx/stream objects (zstd-style), and the library manages its own worker threads (up to 200) |
| **Drop-in for the baseline** | partial — output is standard LZMA2 that liblzma's raw LZMA2 decoder and 7-Zip can read (FL2_p_omitProperties and FL2_getCCtxDictProp exist for 7-Zip/XZ embedding), but the API differs from liblzma and .xz containers need FXZ Utils |

## Gotchas

- Default levels use the same dictionary as 7-Zip and give output 1%-5% larger; FL2_p_highCompression selects a separate level table that compresses better on smaller dictionaries at a worse speed/ratio trade-off.
- Multi-threaded decompression only works on streams that contain dictionary resets (FL2_p_resetInterval, default every 4 dictionary sizes); streams from xz or 7-Zip decode on one thread.
- Out-of-bounds read in RMF_handleRepeat (issue #9, reported 2022, multi-threaded compression crash) was fixed only in January 2026 by PR #14, and an unsafe match-table access in LZMA2_ECtx_s was fixed in October 2025; neither is in a tagged release.
- Build defaults differ by entry point: the root Makefile enables the x86-64 asm decoder, but embedders compiling the sources directly must define LZMA2_DEC_OPT and assemble lzma_dec_x86_64 themselves to get it.

## Known shortcomings

- Tier B on lzbench (flags not stated): at matched ratio -8 vs xz -7 is 1.5x, but the FL2 decoder is slower than xz (78.5 vs 122 MB/s).
- 'Active' is generous: last tag v1.0.1 (2019), idle from Aug 2020 to Oct 2025, with two encoder memory-safety fixes on master only (out-of-bounds read in RMF_handleRepeat, issue #9 / PR #14, Jan 2026; unsafe LZMA2_ECtx_s match-table access, Oct 2025). The gain at -1 is tiny (21.8 vs 19.2 MB/s); native output is raw LZMA2, not an .xz container (FXZ Utils needed); the decoder runs 79 MB/s vs xz 122-124 MB/s.

## Caveats and trade-offs

Compression-only speedup. In lzbench the fast-lzma2 decoder (78.5-79.1 MB/s) is slower than xz 5.8.4's decoder (122-124 MB/s) on the same data; streams remain standard LZMA2, so they can be decoded with xz/liblzma. Matching 7-Zip's ratio needs double the dictionary size, which raises decompression memory. The README baseline is 7-Zip's LZMA2 encoder rather than xz itself; FXZ Utils is the xz-compatible wrapper. Dual-licensed BSD-3-Clause or GPL-2.0.

Needs about twice the dictionary size in memory to reach the ratio of LZMA2; output 1%-5% larger than 7-Zip's at default; decompression speed is the same as LZMA2 (\~79 MB/s in lzbench).

## Maintenance

Dual BSD-3-Clause/GPL-2.0 and production-proven in several 7-Zip forks, but effectively in maintenance mode: v1.0.1 is from 2019, master gained two memory-safety fixes (2025-10, 2026-01), a CI workflow (2026-08) and a doc fix (2026-09-12), and issues asking whether the project is maintained (#13) or documented (#7) remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The well-known independent lzbench suite (public code, inikep/lzbench) lists fastlzma2 1.0.1 alongside xz 5.8.4 and lzma 26.03 on silesia.tar with gcc 15.2.0 on a single thread of an EPYC 9555P; all quoted rows match. Compile flags are not on the page (only implicit in the Makefile), so B, consistent with earlier lzbench-based verdicts. The README's 20-100% claim vs 7-Zip 19.00 is first-party, chart only.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** Rows verified on the lzbench README. Added the matched-ratio comparison (-8 vs xz -7) and the decompression-speed regression to caveats. Metadata (347 stars, last commit 2026-09-12, dual BSD-3-Clause/GPLv2) matches.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/conor42/fast-lzma2>
  - <https://github.com/conor42/fast-lzma2/commits/master>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/README.md>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/conor42/fast-lzma2>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/README.md>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/fast-lzma2.h>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/Makefile>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/radix_mf.c>
  - <https://raw.githubusercontent.com/conor42/fast-lzma2/HEAD/fl2_compress.c>
  - <https://github.com/conor42/fast-lzma2/commits/master>
  - <https://github.com/conor42/fast-lzma2/issues?q=is%3Aissue>
  - <https://github.com/conor42/fast-lzma2/issues/9>
  - <https://github.com/conor42/fast-lzma2/issues/10>
  - <https://github.com/conor42/fast-lzma2/pull/14>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/conor42/fast-lzma2`) · [data/wave9/enrich/raw/github_com_conor42_fast_lzma2.json](../../../data/wave9/enrich/raw/github_com_conor42_fast_lzma2.json) (enrichment confidence 0.85)

</details>
