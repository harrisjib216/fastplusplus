# BriefLZ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Zlib` · 🟡 stale

> Tiny C LZ77 compressor with gamma-coded lengths/offsets; at -6 it matches zlib -9's ratio with about 2x faster compression.

| | |
|---|---|
| **Beats** | zlib (zlib 1.2.11 in the README table, zlib 1.3.2 in lzbench 2.4) |
| **Claimed result** | README table (Core i5-4570 at 3.2 GHz): brieflz 1.3.0 -6 compresses at 17 MB/s and decompresses at 400 MB/s with ratio 31.71; zlib 1.2.11 -9 does 11 MB/s and 320 MB/s with ratio 31.92 (about 1.5x faster compression and 1.25x faster decompression, derived from page data). lzbench 2.4 (EPYC 9555P): brieflz -6 22.8 MB/s and 328 MB/s versus zlib -9 11.3 MB/s and 318 MB/s (2.0x compression, 1.03x decompression, derived). |
| **Workload** | Silesia corpus through lzbench, compression and decompression speed and ratio at several levels, compared with brotli, zstd, zlib, lz4hc and lzo. |
| **Metric** | throughput |
| **Hardware** | README table: Core i5-4570 at 3.2 GHz. lzbench 2.4 table (https://github.com/inikep/lzbench): AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; silesia.tar (211,947,520 bytes) |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 111 stars |
| **Last commit** | 2024-02-02 |
| **Links** | [repository](https://github.com/jibsen/brieflz) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P at 3.2 GHz with turbo off, silesia.tar), brieflz 1.3.0 -6 compresses at 22.8 MB/s and decompresses at 328 MB/s to 31.71%, against zlib 1.3.2 -9 at 11.3 and 318 MB/s to 31.92%: about 2x faster compression and similar decompression at a slightly better ratio; versus zlib -6 it compresses slower (22.8 vs 26.8 MB/s). The README's own 2020 table on a Core i5-4570 shows 17 vs 11 MB/s and 400 vs 320 MB/s against zlib 1.2.11 -9.

## Use it when

- Code size of the decompressor matters: blz_depack is 61 lines of C, which the README says fits in 103 bytes of x86 machine code (boot loaders, executable packers, firmware, demos).
- Compress-once, decompress-many assets where you want a ratio near zlib -9 (31.71% vs 31.92% on Silesia) without carrying zlib's inflate.
- Small embedded or C89 targets that need a permissively licensed (Zlib) single-file compressor with no dependencies and caller-provided memory.
- Buffers whose full size is known up front, since the format has no window limit and matches can reach back across the whole buffer.

## Skip it when

- Throughput-sensitive code on desktop or server CPUs: libdeflate 1.26 -6 in the same lzbench 2.4 run gives 31.85% at 82.1 MB/s compress and 820 MB/s decompress versus brieflz -6 at 31.71%, 22.8 and 328 MB/s, and zstd beats both.
- Anything that needs the deflate/gzip/zlib format, streaming, or interoperability with other tools; BriefLZ has its own raw format with no streaming API.
- Untrusted input to the plain decoder: blz_depack does no bounds checking, so use blz_depack_safe for data you did not produce.
- Level 10 (--optimal) or other high levels on attacker-controlled or highly repetitive data: open issue #12 reports about 1000x slowdowns on runs of a single byte, and issue #11 reports unpredictable speed.
- Very large buffers: workmem grows with input (levels 5-7 need about 3x src_size words, levels 8-10 about 5x src_size words plus the hash table), and sizes are unsigned long, which is 32-bit on 64-bit Windows.

## How it is fast

LZSS-style matching with an Elias-gamma (gamma2) universal code for lengths and offsets and 16-bit tag words for literal/match flags, so there is no Huffman stage to build or decode. Levels pick the match finder: a single-entry hash table (level 1), lazy matching (2), hash buckets (3-4), a backwards dynamic-programming parse with left-extension of matches (5-7) and a binary-tree optimal parse (8-10). The decoder uses a 256-entry lookup table to read up to 8 bits of gamma code at a time; decode stays around 300-400 MB/s because the bit-level format is serial.

## Compared with alternatives

Pick BriefLZ over zlib, libdeflate or zstd only when decoder footprint and a tiny, dependency-free, Zlib-licensed codebase matter more than speed; for raw speed LZ4 or libdeflate win, and for ratio-per-second zstd wins. Against FastLZ and LZ4 it trades speed for ratio (31.71% at -6 vs about 47-49%).

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib \| source-drop (src/brieflz.c, src/depack.c or src/depacks.c, include/brieflz.h) |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | ANSI C (C89); CMake 2.8.11+ for the provided build |
| **Platforms** | any; 16-bit targets need BLZ_HASH_BITS and the block size lowered |
| **Thread safety** | not documented; functions keep no global state and all scratch is in the caller's workmem, so separate workmem buffers per thread should be safe (inferred from source) |
| **Drop-in for the baseline** | no |

## Gotchas

- The compressed stream does not store the original size; you must keep it yourself and pass it to blz_depack.
- dst must be at least blz_max_packed_size(n) = n + n/8 + 64 bytes, and workmem must be blz_workmem_size_level(n, level) bytes, which differs by level.
- The README notes its benchmark 'is not entirely fair because BriefLZ has no window size limit'; with blzpack's 1 MiB blocks, real ratios are lower than whole-file numbers.
- Interfaces use unsigned long for sizes (C89); the blzpack example misreports totals above 4 GiB where unsigned long is 32-bit (issue #1, wontfix).

## Known shortcomings

- Tier B on lzbench 2.4; brieflz -6 compresses slower than zlib -6.
- libdeflate 1.26 beats it outright in the same lzbench 2.4 run (-6: 82.1/820 MB/s at 31.85% vs brieflz -6 22.8/328 at 31.71%). Open issue #12: --optimal (level 10) is about 1000x slower on repetitive data (a denial-of-service risk), no reply; #11 unpredictable optimal speed. blz_depack is not bounds-checked (use blz_depack_safe); the raw format stores no size or checksum.

## Caveats and trade-offs

Decompression gain over zlib is marginal (3% in lzbench 2.4, 25% in the 2020 README table). At matched levels the picture is mixed: brieflz -6 (22.8 MB/s, 31.71%) compresses slower than zlib -6 (26.8 MB/s, 32.19%) for a 1.5% smaller output; the clear wins are brieflz -6 vs zlib -9 and brieflz -3 (124 / 301 MB/s, 35.65%) vs zlib -1 (89.0 / 297 MB/s, 36.45%), derived from page data. The README says its comparison 'is not entirely fair because BriefLZ has no window size limit'. zstd and brotli beat it at similar ratios, and zlib-ng/libdeflate are not compared. Tier B rests on the third-party lzbench 2.4 table; the README table is first-party and lacks compiler flags.

Very small code (compressor 147 lines, decompressor 61 lines); no entropy coding; has no window size limit, so it needs the whole buffer.

## Maintenance

Version 1.3.0 (2020) with only CI updates since (last commit 2024-02-02) and two open performance issues unanswered; it is small, Zlib-licensed and easy to vendor, so staleness matters little for a frozen format.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench 2.4 table (public code, inikep/lzbench; gcc 15.2.0 release binary; single thread of an AMD EPYC 9555P, turbo off, silesia.tar) lists brieflz 1.3.0 -6 at 22.8 / 328 MB/s, 31.71% vs zlib 1.3.2 -9 at 11.3 / 318 MB/s, 31.92%; compile flags are not stated on the README, so B, consistent with other lzbench-based entries in this wave. The BriefLZ README table (17 / 400 vs 11 / 320 MB/s, Core i5-4570) matches the record but is first-party with no compiler or flags.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All quoted numbers match both pages. benchmark_url moved to the lzbench README, which carries the tier-B evidence; the BriefLZ README remains the first-party source. Last commit 2024-02-02 (CI update), 111 stars, Zlib license, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/jibsen/brieflz>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/jibsen/brieflz/commits>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/jibsen/brieflz>
  - <https://github.com/jibsen/brieflz/issues?q=is%3Aissue>
  - <https://github.com/jibsen/brieflz/issues/12>
  - <https://github.com/jibsen/brieflz/issues/1>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/README.md>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/include/brieflz.h>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/src/brieflz.c>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/src/depack.c>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/src/depacks.c>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/src/brieflz_leparse.h>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/src/brieflz_btparse.h>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jibsen/brieflz/HEAD/example/blzpack.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jibsen/brieflz`) · [data/wave9/enrich/raw/github_com_jibsen_brieflz.json](../../../data/wave9/enrich/raw/github_com_jibsen_brieflz.json) (enrichment confidence 0.8)

</details>
