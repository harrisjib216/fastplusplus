# LZO (lzo1x)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-2.0-or-later` · 🔴 abandoned

> LZO1X-1: byte-aligned LZ77 block codec; 5.6x faster compression, 1.9x faster decompression than zlib -1, 30% larger output.

| | |
|---|---|
| **Beats** | zlib (level 1, fastest mode) |
| **Claimed result** | lzbench 2.4 README table: lzo1x 2.10 -1 compresses at 500 MB/s and decompresses at 561 MB/s (ratio 47.45%); zlib 1.3.2 -1 compresses at 89.0 MB/s and decompresses at 297 MB/s (ratio 36.45%). About 5.6x faster compression and 1.9x faster decompression (derived from page data), at an output about 30% larger. First-party doc/LZO.TXT (mirror): 'The C version of LZO1X-1 is about 4-5 times faster than the fastest zlib compression level' (Calgary Corpus, 256 KiB blocks, Pentium 133). |
| **Workload** | In-memory compress and decompress of silesia.tar (211,947,520 bytes), single thread, lzo1x 2.10 level -1 against zlib 1.3.2 level -1, via the lzbench 2.4 results table. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -ffast-math -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 49 stars, 44 forks on the unofficial nemequ/lzo GitHub mirror (11 commits, one per release 2.00 to 2.10); LZO ships as liblzo2 in many Linux distributions, the Linux kernel carries its own LZO1X port, and lzbench bundles lzo 2.10 |
| **Last commit** | 2017-03-01 |
| **Links** | [repository](https://github.com/nemequ/lzo) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary building both codecs at -O3, fastest of runs with at least 8 s per phase, one thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar of 211,947,520 bytes) measured lzo1x 2.10 -1 at 500 MB/s compression and 561 MB/s decompression with 47.45% output, against zlib 1.3.2 -1 at 89.0 and 297 MB/s with 36.45%: about 5.6x and 1.9x faster for about 30% more bytes (derived from page data). The LZO decompression figure is for the unchecked lzo1x_decompress, the zlib figure for checked uncompress including Adler-32 verification.

## Use it when

- You must read or write existing LZO1X data or interoperate with liblzo2 users (the record notes liblzo2 ships in many Linux distributions and the Linux kernel carries its own LZO1X port), so changing format is not an option.
- A GPL-compatible C or C++ program that currently calls zlib at level 1 for in-memory blocks and cares more about CPU than bytes: lzbench 2.4 shows 500 vs 89.0 MB/s compression and 561 vs 297 MB/s decompression on silesia.tar for 47.45% vs 36.45% output.
- Memory-starved or embedded targets: decompression needs no work memory, LZO1X-1(11) needs only a 2,048-entry dictionary, and miniLZO compiles to about 6 KiB on i386 (minilzo/README.LZO).
- Executable packers and similar tools that need overlapping (in-place) decompression, which LZO documents and demonstrates in examples/overlap.c.

## Skip it when

- Any new format where you can pick the codec: on the same lzbench 2.4 table LZ4 1.10.0 compresses faster (550 MB/s) at the same ratio (47.60%) and decompresses 6.8x faster (3832 MB/s), and zstd 1.5.7 -1 gives a 27% smaller output (34.53%) at 411 / 1351 MB/s (derived from page data).
- Pre-compressed assets: LZO1X-999 (7.40 MB/s compress, 531 MB/s decompress, 35.53%) is dominated by lz4hc 1.10.0 -12 (10.4 / 3813 MB/s, 36.45%) and by zstd -1 on both size and decode speed.
- Proprietary or permissively licensed products: the code is GPL-2.0-or-later and a non-GPL licence must be bought from the author.
- Untrusted or possibly corrupted input through lzo1x_decompress(): LZO.FAQ says the standard decompressor 'will probably crash your application' on bad data, and even the safe variant does not detect all corruption without your own checksum.
- You need gzip/zlib-compatible output or a streaming API: LZO is block-only and not deflate; libdeflate 1.26 -1 (202 / 783 MB/s, 34.68%) or zlib-ng 2.3.3 -1 (196 / 466 MB/s, 44.41%) stay deflate-compatible.

## How it is fast

LZO1X-1 is a greedy, single-probe LZ77 parser: it hashes the next four bytes with a multiplicative hash (0x1824429d) into a 16,384-entry table of 16-bit positions, accepts a candidate only if the 4-byte word compares equal, extends matches 8 bytes at a time with XOR plus count-trailing-zeros on 64-bit little-endian builds, and on a miss advances 1 + (pending literal run &gt;&gt; 5) bytes so incompressible stretches are skipped quickly. Output tokens are strictly byte aligned (LZO.FAQ), with 2-byte codes for short matches within 2 KiB and 3-4 byte codes up to a 48 KiB window and no entropy-coding stage, so decoding is a token loop of unaligned 8- and 4-byte copies that needs no work memory. The missing entropy stage is also why the output is about 30% larger than zlib -1 on silesia.tar.

## Compared with alternatives

Pick LZO over LZ4, Snappy or zstd only when you must stay compatible with existing LZO1X data or tooling: on lzbench 2.4, LZ4 matches its ratio with faster compression and 6.8x faster decompression, and zstd -1 is close on compression speed with a 27% smaller output. Against the deflate siblings (zlib-ng, libdeflate, libslz) LZO compresses faster but gives up deflate compatibility and writes 1% (libslz -1) to 37% (libdeflate -1) more bytes (derived from page data).

## Integration

| | |
|---|---|
| **Form** | static lib (CMake or Autotools; shared optional) or source-drop (miniLZO: minilzo.c, minilzo.h, lzoconf.h, lzodefs.h) |
| **Dependencies** | none |
| **Minimum toolchain** | ANSI C (C90) compiler, also compiles as C++ per LZO.TXT; CMake 3.0+ (3.4.3 for Windows shared builds) or Autoconf |
| **Platforms** | any flat 32- or 64-bit memory model (LZOAPI.TXT); portable C with unaligned 4/8-byte copy fast paths when LZO_OPT_UNALIGNED32/64 are enabled; optional legacy i386 assembler decompressors |
| **Thread safety** | LZO.TXT: 'Algorithm is thread safe'; no shared state after lzo_init(), but each concurrent compress call needs its own wrkmem buffer. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the decompression number: lzbench 2.4 (bench/lz_codecs.cpp) times lzo1x_decompress, the unchecked decoder, while the rival rows run checked decoders (LZ4_decompress_safe, zlib uncompress, which also verifies the Adler-32 trailer, libdeflate, ZSTD_decompressDCtx). lzbench never times lzo1x_decompress_safe, the variant you need for external data; a 2007 LKML thread, seen only as a search snippet, put the unchecked path about 1-8% ahead. The 1.9x lead over zlib -1 survives, but it is an upper bound.
- Decompression speed is build-sensitive: the earlier lzbench 2.0.1 table (gcc 14.2.0, EPYC 9554) listed lzo1x 2.10 -1 at 513 / 696 MB/s versus 500 / 561 MB/s in lzbench 2.4 (gcc 15.2.0, EPYC 9555P), a 19% decompression drop while LZ4 rose 3% and zlib -1 fell 8% (derived from page data).
- LZO1X-1 compresses in independent 49,152-byte pieces: lzo1x_1.c switches the dictionary to 16-bit positions, which turns on LZO_DETERMINISTIC in lzo1x_c.ch, so the hash table is cleared for every piece and matches never reach back across a piece boundary; incompressible input can grow to len + len/16 + 64 + 3 bytes (LZO.FAQ).
- The shipped examples/simple.c decompresses with the unchecked lzo1x_decompress, so code copied from it is unsafe on external data; CVE-2014-4607 (integer overflow in the safe decompressor on 32-bit with more than 16 MiB per call) was fixed in 2.07. A format-compatible MIT-licensed C++14 reimplementation exists (jackoalan/lzokay) but it mirrors LZO1X-999 and publishes no speed numbers.

## Known shortcomings

- lzbench 2.4 (gcc -O3 -ffast-math for both codecs): only beats stock zlib -1 (500/561 vs 89.0/297 MB/s) at 30% larger output; on the same table LZ4, Snappy, zstd -1 and libdeflate -1 (783 MB/s decompress, 34.68%) match or beat it. GPL-2.0-or-later (commercial licence sold by the author), unofficial mirror of oberhumer.com (blocked), no release since 2.10 (2017-03-01); the first-party 4-5x claim is Pentium 133 prose with no zlib row.
- Enricher: lzbench 2.4 bench/lz_codecs.cpp times the unchecked lzo1x_decompress while rivals run checked decoders (LZ4_decompress_safe, zlib uncompress with Adler-32, libdeflate, zstd), so 561 MB/s is an upper bound (lzo1x_decompress_safe is never timed; the 1.9x over zlib -1 still holds); decompression is build-sensitive (lzbench 2.0.1 gcc 14.2.0: 513/696 MB/s vs 2.4 gcc 15.2.0: 500/561). LZO1X-1 compresses in independent 49,152-byte pieces with the hash table cleared each piece; examples/simple.c uses the unchecked decoder. LZ4 1.10.0 dominates on the same table (550/3832 MB/s, 47.60%) and LZO1X-999 is dominated by lz4hc -12.

## Caveats and trade-offs

Tier A rests on the lzbench 2.4 README run (public Makefile, gcc 15.2.0, EPYC 9555P), where lzbench builds LZO 2.10 and zlib 1.3.2 itself with the same -O3 -ffast-math flags. The win is over stock zlib only: on the same table LZ4 1.10.0 (550 / 3832 MB/s at 47.60%) compresses slightly faster at a similar ratio and decompresses about 6.8x faster, Snappy 1.3.1 (457 / 976 MB/s, 47.85%) decompresses faster, zstd 1.5.7 -1 (411 / 1351 MB/s, 34.53%) is close on compression speed with a much smaller output, and libdeflate 1.26 -1 (202 / 783 MB/s, 34.68%) produces deflate-compatible output that decompresses about 1.4x faster than lzo1x -1 (derived from page data); zlib-ng 2.3.3 -1 runs at 196 / 466 MB/s, 44.41%. lzo1x -1 output is about 30% larger than zlib -1 (100,572,537 vs 77,259,029 bytes). The first-party figure ('about 4-5 times faster than the fastest zlib compression level') is prose in doc/LZO.TXT next to a Calgary Corpus table from a Pentium 133 that has no zlib row. License is GPL-2.0-or-later (source headers: 'either version 2 of the License, or (at your option) any later version'), so linking it into non-GPL software needs a separate commercial license, which doc/LZO.TXT says the author offers. The canonical site http://www.oberhumer.com/opensource/lzo was not opened (egress block); repo, license and release data come from the unofficial nemequ/lzo mirror, whose last commit is the 2.10 release (2017-03-01); lzbench 2.4 also bundles 2.10 dated 2017-03-01. [retier] lzbench 2.4 (gcc 15.2.0 -O3 -ffast-math for both codecs, EPYC 9555P, silesia.tar): only beats stock zlib -1 (500/561 vs 89.0/297 MB/s) at 30% larger output; LZ4 1.10.0 (550/3832 MB/s, 47.60%), Snappy, zstd -1 and libdeflate -1 match or beat it and LZO1X-999 is dominated by lz4hc -12. bench/lz_codecs.cpp times the unchecked lzo1x_decompress while the rivals run checked decoders (LZ4_decompress_safe, zlib uncompress with Adler-32, libdeflate, zstd), so 561 MB/s is an upper bound and lzo1x_decompress_safe is never timed; decompression is build-sensitive (lzbench 2.0.1 gcc 14.2.0: 513/696 MB/s). LZO1X-1 compresses in independent 49,152-byte pieces with the hash table cleared each piece. GPL-2.0-or-later (commercial licence sold by the author), unofficial mirror of oberhumer.com, no release since 2.10 (2017-03-01); the first-party 4-5x claim is Pentium 133 prose with no zlib row.

GPL-2.0-or-later (the author sells commercial licences), so copyleft; block format with no framing or checksum in the core API; compression ratio at -1 is about 30% worse than zlib -1; many algorithm variants (LZO1, 1A, 1B, 1C, 1F, 1X, 1Y, 1Z, 2A) and a minilzo subset for easy embedding; the doc says it is free of known bugs, but CVE-2014-4607 (integer overflow in the safe decompressor on 32-bit) was fixed in 2.07.

## Maintenance

Upstream has not released since LZO 2.10 (2017-03-01) and the GitHub copy is an unofficial release-per-commit mirror with no issues and one open pull request, but the code is mature, dependency-free and easy to vendor via miniLZO, provided GPL-2.0-or-later or a purchased commercial licence fits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The independent lzbench 2.4 README table (public harness inikep/lzbench, tag v2.4; release binary lzbench24_x86_64-linux-gnu-gcc15 built with gcc 15.2.0; single thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar, -eALL -t8,8 -o1c4) lists lzo1x 2.10 -1 at 500 / 561 MB/s, 47.45% next to zlib 1.3.2 -1 at 89.0 / 297 MB/s, 36.45%. The v2.4 Makefile builds both lz/lzo (LZO_FILES rule, line 1364) and lz/zlib (ZLIB_FILES rule, line 1400) with CFLAGS = -fomit-frame-pointer -fstrict-aliasing -ffast-math -O3 -DNDEBUG under gcc, so code, compiler, flags and CPU model are all public, consistent with the retier-02 A verdicts for FastLZ, BriefLZ and memlz on the same table.
- **Verifier notes:** All quoted numbers match the lzbench 2.4 README rows for lzo1x 2.10 -1 and zlib 1.3.2 -1; the 5.6x compression and 1.9x decompression ratios are correctly marked as derived. The compile flags in the record (including -ffast-math) match the v2.4 Makefile for a gcc build. Shortcomings to record: only beats stock zlib (LZ4, Snappy, zstd -1 and libdeflate -1 match or beat it on the same table), 30% larger output than zlib -1, GPL-2.0-or-later copyleft, unofficial mirror with no release since 2017. Not a duplicate of any listed entry.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** lzbench 2.4 (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/Makefile>
  - <https://github.com/nemequ/lzo>
  - <https://github.com/nemequ/lzo/commits>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/doc/LZO.TXT>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_1.c>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/README>
- **Sources the enricher read:**
  - <https://github.com/nemequ/lzo>
  - <https://github.com/nemequ/lzo/commits>
  - <https://github.com/nemequ/lzo/pulls?q=is%3Apr>
  - <https://github.com/nemequ/lzo/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/README>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/doc/LZO.TXT>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/doc/LZOAPI.TXT>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/doc/LZO.FAQ>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/NEWS>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/minilzo/README.LZO>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/include/lzo/lzo1x.h>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/include/lzo/lzoconf.h>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_1.c>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_c.ch>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_d.ch>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_d1.c>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo1x_d2.c>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/config1x.h>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo_conf.h>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/src/lzo_dict.h>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/examples/simple.c>
  - <https://raw.githubusercontent.com/nemequ/lzo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/bench/lz_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/bench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/bench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/bench/codecs.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/lz/lzo/lzo1x_d.ch>
  - <https://raw.githubusercontent.com/inikep/lzbench/v2.4/lz/lzo/lzo1x_c.ch>
  - <https://github.com/jackoalan/lzokay>
  - <https://raw.githubusercontent.com/jussyDr/lzo1x/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/nemequ/lzo`) · [data/wave9/enrich/raw/github_com_nemequ_lzo.json](../../../data/wave9/enrich/raw/github_com_nemequ_lzo.json) (enrichment confidence 0.85)

</details>
