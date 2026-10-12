# Lizard

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> LZ4-derived C codec (formerly LZ5) with optional Huffman; decompresses 4-5x faster than zlib -9 at similar ratio.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | lzbench 2.4 (EPYC 9555P, gcc 15.2.0): lizard 2.1 -29 decompress 1470 MB/s at ratio 32.41% (compress 2.08 MB/s) vs zlib 1.3.2 -9 318 MB/s at 31.92% (4.6x, derived from page data); vs zstd 1.5.7 -1 1351 MB/s at 34.53% (1.09x, derived from page data). Lizard README (lzbench 2.0, EPYC 9554, GCC 14.2.0, Ubuntu 24.04.1): lizard 2.1 -10 2161 MB/s at 48.79% vs zstd 1.5.6 -1 1342 MB/s at 34.64%. |
| **Workload** | Decompression of silesia.tar vs zlib/zstd/LZ4, single thread. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; README: AMD EPYC 9554 at 3.10 GHz |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); compiler flags not listed in README; options -eALL -t8,8 -o1c4; README: GCC 14.2.0 |
| **Adoption** | 711 stars |
| **Last commit** | 2025-10-09 |
| **Links** | [repository](https://github.com/inikep/lizard) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 (gcc 15.2.0 release binary, one thread of an EPYC 9555P at 3.2 GHz, turbo off, silesia.tar), lizard 2.1 -29 decompresses at 1470 MB/s to 32.41% vs zlib 1.3.2 -9 at 318 MB/s to 31.92% (4.6x, derived from page data), but compresses at only 2.08 MB/s. lzbench and Lizard share a maintainer (inikep), so this is first-party evidence.

## Use it when

- Write-once, read-many data (game assets, packaged read-only blobs, archives decoded at load time) where only decode speed and ratio matter and compression can run offline at about 2 MB/s.
- Replacing zlib -9 for read-heavy blobs when you control both ends: in lzbench 2.4 lizard -29 decodes silesia.tar at 1470 MB/s at 32.41% vs zlib 1.3.2 -9 at 318 MB/s at 31.92%.
- A ratio band around 32-34% where it decodes somewhat faster than zstd at matched ratio: lizard -29 1470 MB/s at 32.41% vs zstd 1.5.7 -2 1257 MB/s at 32.70% in lzbench 2.4 (about 1.17x, derived from page data); the Lizard README's lzbench 2.0 run on an EPYC 9554 showed 1818 vs 1241 MB/s.
- Projects that already embed the LZ4 API and want a higher-ratio variant with the same call shape, within one C library.

## Skip it when

- New designs in general: the author's own 2025 README update calls Lizard outdated and effectively obsolete because LZ4 and zstd have since improved.
- Fast levels: lz4 1.10.0 compresses at 550 MB/s and decodes at 3832 MB/s at 47.60% in lzbench 2.4, beating lizard -10 (464 / 1911 MB/s, 48.79%) on every axis; lz4hc -12 decodes 3813 MB/s at 36.45%.
- High-ratio levels: zstd 1.5.7 -8 decodes at 1301 MB/s at 28.17% and compresses at 61.8 MB/s, while lizard -49 reaches 28.63% at 1058 MB/s decode and 1.99 MB/s compress.
- Interoperability: the format is read only by Lizard itself (no browser, HTTP or OS support), unlike zlib/gzip.
- Memory-constrained compression at high levels: level 29/49 allocates a 2^25-entry chain table and 2^23-entry hash table of U32 (about 160 MB) per stream.

## How it is fast

Decoding is byte-oriented LZ77: each 128 KB block is split into five separate streams (tokens, literals, lengths, 16-bit offsets, 24-bit offsets), and a one-byte token tells the decoder how many literals to copy and where to take the offset from, including a last-offset (repeat match) code, so the hot loop is table-free memcpy work like LZ4's. Ratio comes from larger windows (up to 2^24 at levels 29/49), repeat offsets and, at the high levels, optimal parsing with a binary-tree match finder (Lizard_parser_optimalPriceBT), with all the cost paid at compression time. Levels 30-49 add Huffman coding of the streams (FiniteStateEntropy's huf), which trims size at some decode speed. The README notes no SSE/AVX intrinsics are used.

## Compared with alternatives

Pick Lizard over Zstandard only when decode speed in the 32-34% ratio band matters more than compression speed and the format is private to your system; otherwise zstd (better ratio and compression speed at similar decode) or LZ4 (much faster decode at lower ratio) dominate it, and LZSSE is the sibling for maximum decode speed at about 35% when compression time does not matter.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib \| source-drop (lib/ directory; Makefile, CMake and Visual Studio projects provided) |
| **Dependencies** | none external; bundled FiniteStateEntropy (huf) under lib/entropy for levels 30-49 (build with -DLIZARD_NO_HUFFMAN to limit to levels 10-29) and bundled xxhash for the frame API |
| **Minimum toolchain** | C (CI covers gcc 7.5-14.2, clang 6.0-19, Apple LLVM 15, mingw-gcc 14.2, Visual Studio 2019/2022) |
| **Platforms** | any; CI covers x86/x86-64 Linux, macOS, Windows and cross builds for ARM (32/64-bit) and PowerPC (32/64-bit); no SIMD required |
| **Thread safety** | Not documented; each Lizard_stream_t / Lizard_streamDecode_t is a separate context and Lizard_compress() allocates its own state per call, so independent contexts on separate threads appear safe (inferred from API and source). |
| **Drop-in for the baseline** | no |

## Gotchas

- Lizard_compress() mallocs and frees a full compression state on every call (up to about 160 MB at levels 29/49); reuse a state via Lizard_compress_extState() or the streaming API for repeated calls. Out-of-range levels silently become level 17, and an allocation failure prints to stdout from inside the library.
- Memory-safety history: Jan 2025 commits fixed a heap-buffer-overflow when decoding variable literal lengths and uninitialised reads in Lizard_decompress_LIZv1; issue #41 (Sept 2025) reported LizardF_compressFrameBound underestimating tiny inputs, giving a heap overflow in LizardF_compressFrame, and is closed alongside the 2025-10-09 commit fixing Lizard_writeBlock() for a one-byte input. That fix landed after the v2.1 release, so build from current master and fuzz untrusted input paths.
- Licensing is split: lib/ is BSD-2-Clause, but the CLI and other files outside lib/ are GPLv2.
- Issue #40 (open) reports GCC -O3 decoding 20-25% slower than -O2 (lizard -10: 4536 vs 6118 MB/s), and lzbench 2.4 shows lower decode numbers than the README's lzbench 2.0 run (1470 vs 1818 MB/s at -29); benchmark with your own compiler flags before relying on the margins.

## Known shortcomings

- Downgraded B to C: lzbench is maintained by Lizard's own author (inikep), so its table (1470 vs zlib -9 318 MB/s, flags not on page) is first-party; lz4 decodes faster than every Lizard level. Active (last commit 2025-10-09).
- The author calls it obsolete; in lzbench 2.4 lz4 dominates lizard -10 and zstd -8 (1301 MB/s, 28.17%) beats lizard -49 (1058 MB/s, 28.63%), leaving a niche only at -29 vs zstd -2 (1470 vs 1257 MB/s, 1.17x derived). A heap overflow in variable-literal-length decode was fixed Jan 2025; issue #41 (LizardF_compressFrameBound heap out-of-bounds on 1-byte input) was fixed in the 2025-10-09 commit after the v2.1 tag, so use master; issue #40: -O3 decodes 20-25% slower than -O2; levels 29/49 allocate about 160 MB per stream. CLI is GPLv2, library BSD-2.

## Caveats and trade-offs

README admits LZ4 and zstd have advanced so much that Lizard is outdated and effectively obsolete; lz4 1.10.0 decompresses faster (3832 MB/s in lzbench 2.4) than every Lizard level. The margin over zstd -1 is small and the high-ratio levels compress at about 2 MB/s; the real win is decompression vs zlib. The benchmark suite is maintained by Lizard's own author.

Very slow compression at high levels (-29 compresses at 2.08 MB/s in lzbench); formerly LZ5.

## Maintenance

The author calls it obsolete but still patches it (Jan 2025 sanitizer and overflow fixes, a 2025-10-09 single-byte input fix); the BSD-2 lib is easy to vendor, though issue #36 about the project's status (2021) is unanswered.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The lzbench 2.4 table does list lizard 2.1 -29 at 1470 MB/s decompress, 32.41% vs zlib 1.3.2 -9 at 318 MB/s, 31.92% (gcc 15.2.0, EPYC 9555P, single thread), but lzbench and Lizard share one maintainer (inikep), so this is not an independent third-party measurement; the Lizard README table (lzbench 2.0, gcc 14.2.0, EPYC 9554) is first-party too, and neither page states compile flags (only implicit in the public lzbench Makefile), so C rather than B or A.
- **Verifier notes:** Last commit 2025-10-09 (fix for Lizard_writeBlock with a one-byte input), within 12 months of today, so maintenance_status corrected from stale to active despite the author calling the codec obsolete. License BSD-2-Clause and 711 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://github.com/inikep/lizard>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/README.md>
  - <https://github.com/inikep/lizard/commits/lizard>
- **Sources the enricher read:**
  - <https://github.com/inikep/lizard>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/LICENSE>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/README.md>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/Makefile>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/lizard_compress.h>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/lizard_decompress.h>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/lizard_common.h>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/lib/lizard_compress.c>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/doc/lizard_Block_format.md>
  - <https://raw.githubusercontent.com/inikep/lizard/HEAD/doc/lizard_Frame_format.md>
  - <https://github.com/inikep/lizard/commits/lizard>
  - <https://github.com/inikep/lizard/issues?q=is%3Aissue>
  - <https://github.com/inikep/lizard/issues/36>
  - <https://github.com/inikep/lizard/issues/40>
  - <https://github.com/inikep/lizard/issues/41>
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/inikep/lizard`) · [data/wave9/enrich/raw/github_com_inikep_lizard.json](../../../data/wave9/enrich/raw/github_com_inikep_lizard.json) (enrichment confidence 0.85)

</details>
