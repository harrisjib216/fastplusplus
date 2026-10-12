# LZMAT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-or-later` · 🔴 abandoned

> Abandoned 2008 nibble-packed LZ77 codec; decompresses about 1.2x faster than zlib at zlib -1 ratio, compresses 3x slower.

| | |
|---|---|
| **Beats** | zlib (1.2.11 -1 and -6) |
| **Claimed result** | lzmat 1.01: 38 MB/s compress, 479 MB/s decompress, 76,485,353 bytes (36.09%). zlib 1.2.11 -1: 119 MB/s, 383 MB/s, 77,259,029 bytes (36.45%); zlib -6: 35 MB/s, 407 MB/s, 68,228,431 bytes (32.19%). Decompression is about 1.25x faster than zlib -1 and 1.18x faster than zlib -6 (derived from page data) at a size close to -1; compression is about 3.1x slower than zlib -1 and roughly level with -6. It does not beat LZO: lzo1x -999 gives 75,301,903 bytes (35.53%) at 8.76 MB/s compress and 827 MB/s decompress, and lz4 1.9.2 decompresses at 4448 MB/s. |
| **Workload** | lzbench 1.8, in-memory, one core, silesia.tar (211,947,520 bytes), compress and decompress throughput and output size of lzmat 1.01 against zlib, LZO, LZ4 and Snappy. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700K, 1 core, Ubuntu 18.04.3 64-bit |
| **Compiler and flags** | clang 9.0.1; lzbench 1.8 run with -t16,16 -eall. Public Makefile at tag v1.8.1: OPT_FLAGS = -fomit-frame-pointer -fstrict-aliasing -ffast-math; lzmat_dec.c and lzmat_enc.c are built with -O2 -DNDEBUG under the Makefile's 'FIX for SEGFAULT on GCC 4.9+' rule, while zlib and most other codecs are built with -O3 -DNDEBUG. |
| **Adoption** | 10 stars, 8 forks (single-commit git mirror of the 2008 LZMAT 1.01 release); bundled in lzbench since at least v1.5 |
| **Last commit** | 2013-08-22 |
| **Links** | [repository](https://github.com/nemequ/lzmat) · [benchmark](https://github.com/inikep/lzbench/blob/v1.8.1/README.md) |

## Verdict

lzbench 1.8 (v1.8.1 README), clang 9.0.1, one core of an Intel Core i7-8700K on Ubuntu 18.04.3, -t16,16, whole silesia.tar (211,947,520 bytes) in one call: lzmat 1.01 compresses at 38 MB/s and decompresses at 479 MB/s to 36.09%, against zlib 1.2.11 -1 at 119 / 383 MB/s and 36.45% and zlib -6 at 35 / 407 MB/s and 32.19%, so decompression is about 1.25x faster than -1 and 1.18x faster than -6 and compression 3.1x slower than -1 (derived from page data). lzbench memcmp-checked the round trip, and lzmat was compiled at -O2 against zlib's -O3, which if anything favours zlib.

## Use it when

- Reading or producing existing LZMAT streams for compatibility with software that already uses the format.
- Trusted, write-once read-many data on x86 where a GPL dependency is acceptable and you want a decoder of about 140 lines of C with no tables, no heap and no work memory.
- Historical reference or benchmark completeness (lzbench carried it from v1.5 to v1.8.1).

## Skip it when

- Any performance-driven new design: in the same lzbench 1.8 table libdeflate 1.3 -1 compresses at 201 MB/s and decompresses at 865 MB/s to 34.59%, beating LZMAT's 38 / 479 MB/s at 36.09% on every axis while staying deflate-compatible; lzo1x -999 (827 MB/s at 35.53%), lzfse (934 MB/s at 31.91%) and lizard -25 (2853 MB/s at 35.80%) also decode faster at equal or better ratio.
- Untrusted or possibly corrupt input: lzbench has warned since v1.5 of decompression errors and GCC 4.9+ -O3 segfaults and lists it under 'security issues and/or no longer maintained', CompFuzz recorded issues found (2013-09-11, abandoned), and the decoder's raw-copy path does not bound-check its input (see gotchas).
- Fast compression: 38 MB/s is 3.1x slower than zlib -1 and about 5x slower than libdeflate -1 in the same run.
- Proprietary or permissively licensed products: GPL-2.0-or-later.
- Big-endian or strict-alignment targets: the GET_LE16/GET_LE32 macros are native-endian unaligned pointer loads, so streams are not portable and the code relies on undefined behaviour.

## How it is fast

It is a pure LZ77 coder with no entropy stage: flags come in 8-token tag bytes and every literal, distance and length is packed at 4-bit (nibble) granularity, with position-dependent distance classes (7/11-bit offsets in the first 2,176 bytes, then 6/10/14/18-bit classes, about a 273 KiB window), lengths from 3 up to 65,807, and raw 4-byte-word copy chunks for incompressible stretches. Decoding is therefore bit-twiddling plus byte copies instead of zlib's Huffman decoding, which is where the roughly 1.2x decompression lead comes from, while the larger window and nibble-sized fields keep the ratio near zlib -1. The encoder walks the full hash chain (4-byte hash, 32,768-entry head and chain tables) inside the window and special-cases byte runs, which makes it slow (38 MB/s).

## Compared with alternatives

Practically never for new work: libdeflate (catalogued) beats it on compression speed, decompression speed and ratio in the same lzbench run while staying zlib/deflate-compatible, and Lizard -25 and LZSSE8 -6 decode 6x and 9x faster at similar ratios (35.80% and 35.61%). Pick LZMAT only to interoperate with existing LZMAT data, and then from lzbench's patched copy.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc memset) |
| **Minimum toolchain** | ANSI C per the header (the header uses // comments, so C99 or a compiler extension); lzbench builds it at -O2 with a 'FIX for SEGFAULT on GCC 4.9+' rule instead of -O3 |
| **Platforms** | little-endian targets that tolerate unaligned 16/32-bit loads (x86, x86-64); on LP64 use lzbench's patched copy, since upstream truncates pointers to 32 bits |
| **Thread safety** | not documented; the code has no static or global state (the encoder's 256 KiB hash table lives on the stack, or in a caller buffer with LZMAT_SMALL_STACK), so concurrent calls on separate buffers appear safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The default decoder (the LZMAT_SAVE variant, the one lzbench measured) checks output bounds but not input bounds everywhere: the raw 'copy chunk' path copies up to about 64 KiB (r_cnt up to 16,390 four-byte words) from pbIn without comparing against cbIn, nibble field reads (LZMAT_GET_LE16, LZMAT_GET_U4) can touch 1-2 bytes past the end, and it returns LZMAT_STATUS_OK without checking that all input was consumed (the non-SAVE variant does). A crafted stream can therefore over-read the source buffer; lzbench's 'decompression error; returns 0' warning has no documented root cause.
- Upstream nemequ/lzmat is broken on 64-bit: lzmat_enc.c line 426 compares output pointers truncated to 32 bits ((MP_U32)pOut &gt;= (MP_U32)pEndOut), so the overflow guard misfires if the output buffer straddles a 4 GiB address boundary, and line 463 computes the size the same way; lzbench (v1.8.1 and master lz/lzmat) replaced both with plain pointer arithmetic and changed the MP_PTR typedef guard in lzmat.h, so vendor that copy.
- The encoder puts a 256 KiB hash table (two 32,768-entry int32 arrays) on the stack unless LZMAT_SMALL_STACK is defined and memsets it on every call, which can overflow small thread stacks and makes small-block compression expensive; it also loads 4-byte hash keys and 2-byte compare values past the end of the input on the last 1-3 bytes.
- Sizes are 32-bit (MP_U32), so one call handles under 4 GiB, and the stream carries no length or checksum: a wrong output size yields a short or failed decode rather than a detected integrity error.

## Known shortcomings

- lzbench v1.8.1 (clang 9.0.1, i7-8700K) decompression lead of about 1.25x over zlib -1 and 1.18x over zlib -6 only; compression loses to LZO, LZ4 and Snappy. lzmat was built -O2 against zlib -O3. The lzbench maintainer still flags 'decompression bugs', so capped at C despite the memcmp round-trip passing on silesia.tar. Upstream lzmat_enc.c truncates pointers through (MP_U32) casts on 64-bit (lines 426, 463); lzbench measured its fixed copy. Abandoned since 2013-08-22, 10 stars, GPL-2.0-or-later.
- Enricher: the measured decoder (LZMAT_SAVE) never checks the copy-chunk path against cbIn, so it can over-read the input by up to about 64 KiB, has small field over-reads and returns OK without checking leftover input; the encoder puts a 256 KiB table on the stack and memsets it every call. In the same lzbench 1.8 table libdeflate 1.3 -1 (201/865 MB/s, 34.59%) beats it on every axis. Leads: ebiggers/xpack, liblzg.

## Caveats and trade-offs

Tier capped at C although the harness is reproducible: lzbench lists lzmat under 'security issues and/or no longer maintained' and has warned since v1.5 that it contains decompression bugs (decompression error, returns 0) and can segfault with GCC 4.9+ -O3. The 2026 master README still says 'Decompression bugs' and CompFuzz lists LZMAT as abandoned with issues found (2013-09-11, no details). The measured silesia.tar run itself round-tripped: lzbench 1.8 checks the decompressed length and memcmp after every decompression and would print ERROR instead of a speed, and the decoder compiled in is the bounds-checked LZMAT_SAVE path. Build asymmetry: lzmat was compiled at -O2 and zlib at -O3 in the same binary, which, if anything, favours zlib. The code measured is lzbench's patched copy (identical in v1.8.1 and master lz/lzmat), not the upstream repo as-is: nemequ/lzmat's lzmat_enc.c casts pointers to 32-bit MP_U32 in the output-bound check (line 426) and the output-size computation (line 463), which lzbench fixed for 64-bit builds, and lzbench also changed the MP_PTR typedef guard in lzmat.h, so copy from lzbench's lz/lzmat on LP64 targets. The lead is narrow (decompression only, about 1.2x over zlib) and the codec loses to LZO, LZ4 and Snappy in the same table. lzbench 2.4 no longer prints a lzmat row; v1.8.1 is the last tag that does (v1.5 and v1.7.3 gave 24 MB/s compress and 294/288 MB/s decompress against zlib -1 at 244/250 and -6 at 263/267 on an i5-4300U with gcc 6.x, the same about 1.1-1.2x decompression lead). The author's own claims on matcode.com returned 403 and the mirror seen in search results (autohotkey.com) is blocked, so no first-party numbers were read; the GitHub repo carries no README or benchmarks.

GPL-2.0-or-later copyleft. Slow compressor (38 MB/s). Pointer arithmetic goes through 32-bit MP_U32 types, which lzbench had to patch for 64-bit builds. A single-commit mirror of release 1.01 (2008).

## Maintenance

Abandoned since the 2008 1.01 release (single-commit mirror dated 2013-08-22, no README, 10 stars), GPL-2.0-or-later, and dropped from current lzbench tables; usable only as a vendored source drop from lzbench's 64-bit-fixed copy on trusted little-endian data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The lzbench v1.8.1 README table has the lzmat 1.01 row (38 MB/s, 479 MB/s, 76,485,353, 36.09) next to zlib 1.2.11 -1 (119, 383) and -6 (35, 407), and the run is otherwise A-grade reproducible (public _lzbench/lzbench.cpp and compressors.cpp, Makefile flags at the v1.8.1 tag, clang 9.0.1, i7-8700K). It stays capped at C because the harness maintainer flags the measured decoder itself as buggy (v1.5 to 2026 master README: 'Decompression bugs', 'decompression error; returns 0'), following the uniwidth 'bug in hot path' precedent, even though lzbench's memcmp round-trip check passed on silesia.tar.
- **Verifier notes:** Numbers and derived ratios check out exactly (479/383 = 1.25x, 479/407 = 1.18x, 119/38 = 3.1x slower compress), and license GPL-2.0-or-later (header: version 2 or any later version), last commit 2013-08-22 and 10 stars are confirmed. Main shortcomings to record: the harness maintainer flags the decoder as buggy, the decompression-only lead is about 1.2x over zlib and it loses to LZO, LZ4 and Snappy, and upstream nemequ/lzmat truncates pointers to 32 bits in the encoder on 64-bit targets (the measured copy is lzbench's fixed one). If the orchestrator treats the passing round-trip check as enough, the evidence otherwise meets tier A, consistent with the wave 9 lzbench retier-02.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** lzbench v1.8.1 README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench/blob/v1.8.1/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/_lzbench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/_lzbench/compressors.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat_dec.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat_enc.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat_dec.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat_enc.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.5/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.7.3/README.md>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat.h>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat_dec.c>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat_enc.c>
  - <https://github.com/nemequ/lzmat>
  - <https://github.com/nemequ/lzmat/commits>
  - <https://github.com/nemequ/compfuzz/wiki/Results>
- **Sources the enricher read:**
  - <https://github.com/nemequ/lzmat>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat.h>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat_dec.c>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/lzmat_enc.c>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/test_lzmat.c>
  - <https://raw.githubusercontent.com/nemequ/lzmat/HEAD/test_lzmat.mak>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/_lzbench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/_lzbench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/_lzbench/compressors.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat_dec.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/v1.8.1/lzmat/lzmat_enc.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat_dec.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/master/lz/lzmat/lzmat_enc.c>
  - <https://github.com/nemequ/compfuzz/wiki/Results>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/nemequ/lzmat`) · [data/wave9/enrich/raw/github_com_nemequ_lzmat.json](../../../data/wave9/enrich/raw/github_com_nemequ_lzmat.json) (enrichment confidence 0.7)

</details>
