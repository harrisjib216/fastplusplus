# LZHAM (lzham_codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Public domain (LICENSE dedication dated 2020-09-15; no SPDX id)` · 🔴 abandoned

> Asymmetric LZ77 codec with near-LZMA ratio whose decoder runs about 3.5x faster than 7-Zip LZMA; compression is slow.

| | |
|---|---|
| **Beats** | LZMA (lzma 26.03 as built in lzbench) |
| **Claimed result** | lzham 1.0 -d26 -1: 3.16 MB/s compress, 273 MB/s decompress, 54,740,589 bytes (25.83%). lzma 26.03 -4: 13.6 MB/s, 73.7 MB/s, 55,936,064 bytes (26.39%); lzma -2: 23.0 / 70.2 MB/s, 57,082,443 bytes (26.93%). So about 3.7x faster decompression than lzma -4 with 2% smaller output (derived from page data), at about 4.3x slower compression. LZHAM -0: 11.1 / 200 MB/s, 64,089,870 bytes (30.24%). LZMA at -6 and -9 is smaller (49,551,059 and 48,682,482 bytes) and decodes at 78.4 and 78.2 MB/s. |
| **Workload** | lzbench 2.4, in-memory, single thread, silesia.tar (211,947,520 bytes): decompression speed and output size of lzham 1.0 -d26 against lzma 26.03 at comparable ratio. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P @ 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench24_x86_64-linux-gnu-gcc15 release binary), lzbench options -eALL -t8,8 -o1c4; the public lzbench Makefile builds with -O3 |
| **Adoption** | 729 stars, 87 forks; shipped as a 7-Zip codec plugin per the README; built into lzbench |
| **Last commit** | 2022-01-03 |
| **Links** | [repository](https://github.com/richgel999/lzham_codec) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 -O3 release binary, one thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar) measured lzham 1.0 -d26 -1 at 3.16 MB/s compress, 273 MB/s decompress and 54,740,589 bytes, versus 7-Zip lzma 26.03 -4 at 13.6/73.7 MB/s and 55,936,064 bytes (3.7x faster decode, 2% smaller) and lzma -6 at 3.13/78.4 MB/s and 49,551,059 bytes (3.5x faster decode, 10.5% larger; derived from page data). The README's 3.1x faster archive test on the 10 GB benchmark (7-Zip 9.38 plugin, 64 MB dictionary) is first-party with no hardware or compiler stated.

## Use it when

- Compress-once, decompress-many distribution (game data, patches, downloadable content) where you want an LZMA-class ratio but client decode time or CPU/power matters: lzbench 2.4 shows 273 MB/s decode vs 78.4 MB/s for lzma -6 at the same 64 MB dictionary.
- Large solid blocks: README says the decoder only beats LZMA above roughly 1,000-13,000 compressed bytes and wants 10-15 KB+ blocks.
- Data with many literals or incompressible stretches, where LZMA's decoder bogs down and LZHAM stores raw blocks.
- x86/x64 Linux and Windows, macOS/iOS builds you control end to end (you pick and store the dictionary size and table update rate yourself).

## Skip it when

- When a modern codec fits: in the same lzbench 2.4 table zstd 1.5.7 -18 is 2.7% smaller (25.14% vs 25.83%), compresses 1.3x faster (4.13 vs 3.16 MB/s) and decodes 4.3x faster (1175 vs 273 MB/s); brotli -11 is 7.9% smaller and decodes 1.4x faster (derived from page data).
- When compression speed or memory matters: LZHAM -1 compresses at 3.16 MB/s, 4.3x slower than lzma -4, and the README puts compressor memory at about 982 MB for a 64 MB dictionary and 5 GB at 512 MB.
- Small blocks or per-record compression: the decoder has a high init cost and the README calls it 'not a good small block compressor'.
- When you need the fastest decode at any ratio: it decodes slower than zlib (273 vs 318 MB/s for zlib 1.3.2 -9 in lzbench), and xz 5.8.4's decoder (105-124 MB/s) narrows its lead over LZMA to about 2.2-2.6x.
- Inputs above about 2 GB per call, or a need for maintenance: issue #19 reports an assertion and core dump compressing a UINT32_MAX-byte chunk (vector capacity overflow), issue #22 reports lzham_z_compress2 failing on small buffers; 14 issues are open with no maintainer replies.

## How it is fast

The encoder does LZMA-style near-optimal parsing (greedy at level 0), but the decoder swaps most of LZMA's bitwise range decoding for quasi-adaptive Huffman tables (literals, delta literals, main match symbol, rep and large lengths, distance low bits) that are rebuilt on a slowing schedule set by m_table_update_rate; only the is_match/is_rep style flags use adaptive binary models. Huffman literal decoding is much cheaper than LZMA's per-bit literal coding, and 512 KB blocks found incompressible are stored raw. The decoder is a switch-based coroutine, and the memory-to-memory API forces unbuffered mode, which writes straight into the caller's buffer with no dictionary copy.

## Compared with alternatives

Over Fast LZMA2 or xz only when you specifically need LZMA-class ratio with a decoder that is 2-4x faster than LZMA's and you control both ends (Fast LZMA2 speeds up the encoder, not the decoder). Otherwise zstd at -18 to -22 beats it on ratio, encode speed and decode speed in the same lzbench run, and zstd, LZ4 or zlib-ng are the safer, maintained choices for small blocks.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake on Linux, VS2010 solution on Windows; separate lzhamdecomp and lzhamcomp libraries plus lzhamdll) |
| **Dependencies** | none (pthreads on POSIX, Win32 API on Windows, for threaded compression) |
| **Minimum toolchain** | C++03; tested by the author with gcc, clang and MSVC 2008/2010/2013; must be compiled with -fno-strict-aliasing on gcc/clang |
| **Platforms** | x86/x64 Linux, Windows x86/x64, macOS, iOS; FreeBSD/NetBSD and non-x86 Linux (e.g. aarch64) fall back to the ANSI C++ path without unaligned loads, atomics or threaded compression; dictionary 2^15 to 2^26 on 32-bit, up to 2^29 on 64-bit |
| **Thread safety** | Separate state objects per stream; the compressor spawns its own helper threads (m_max_helper_threads, -1 = max practical). No other thread-safety statement documented. |
| **Drop-in for the baseline** | partial - the zlib-style API eases porting, but there is no liblzma/xz or 7-Zip LZMA API and the bitstream is LZHAM-only, so it replaces LZMA only where you control both encoder and decoder |

## Gotchas

- Dictionary size and m_table_update_rate (and the finer table-interval settings) are not stored in the stream; the decoder must be given the same values the encoder used or it fails, usually with LZHAM_DECOMP_STATUS_FAILED_BAD_CODE.
- Harness note: lzbench builds its LZHAM copy (identical to upstream except Windows threading macros) with -O3 -fstrict-aliasing -ffast-math and no -fno-strict-aliasing, although the README says -fno-strict-aliasing is required and the author never tested strict aliasing; the silesia output still passed lzbench's memcmp check, so the numbers stand, but the measured build is one the author calls untested.
- Harness note: the lzham -1 vs lzma -4 size win is not like for like: lzbench gives LZHAM a 64 MB dictionary (m_dict_size_log2=26) while 7-Zip LZMA level 4 uses 16 MB in fast hash-chain mode (level 2: 1 MB); at the matching 64 MB dictionary (lzma -6) LZHAM -1 is 10.5% larger but still decodes 3.5x faster. Only levels -0 and -1 were run (lzbench registers 0-4), and the lzbench wrapper ignores lzham_decompress_memory's status code and never sets LZHAM_DECOMP_FLAG_COMPUTE_ADLER32, so the timed decode skips the Adler-32 check (lzbench verifies with memcmp outside the timer; LZMA2 has no checksum there either).
- Public-domain dedication (2020-09-15) with no patent grant; v1.x streams are not compatible with the old Google Code alpha streams, and lzbench disables LZHAM on macOS and 32-bit x86 builds because the 64 MB dictionary overflows the address space.

## Known shortcomings

- lzbench 2.4 rows; lzbench registers levels 0-4 and the -eALL run covered only -0/-1. lzma -6/-9 compresses 9.5-11.1% smaller and LZHAM compresses about 4.3x slower; the win is decompression speed at near-LZMA ratio. Public domain with no patent grant.
- Enricher: lzbench builds LZHAM with -O3 -fstrict-aliasing -ffast-math and never adds the -fno-strict-aliasing the README calls required (output still passes lzbench's memcmp check); the size win over lzma -4 is not like-for-like (64 MB dictionary vs LZMA's 16 MB fast hash-chain mode; against lzma -6 at 64 MB LZHAM -1 is 10.5% larger, still 3.5x faster to decode). zstd 1.5.7 -18 beats LZHAM -1 on every axis in the same table (2.7% smaller, 1.3x faster compress, 4.3x faster decode). The lzbench wrapper ignores decode status and skips Adler-32; open issue #19 (core dump on UINT32_MAX chunk); 14 open issues without replies.

## Caveats and trade-offs

The lzbench 2.4 README run (-eALL preset) includes only LZHAM levels -0 and -1, although lzbench registers levels 0-4 (bench/lzbench.h); the default uber level and the extreme parser were not run, so the README's 'ratio similar to LZMA with 1.5x-8x faster decompression' is only partly reproduced: LZHAM -1 beats lzma -4 and -2 on size and decode speed, but lzma -6 and -9 outputs are 9.5% and 11.1% smaller than LZHAM -1 (LZHAM -1 is 10.5% and 12.4% larger; derived from page data), and LZHAM -1 compresses 4.3x slower than lzma -4. The README's own 10GB-benchmark figures (7zip-LZHAM 9.38 32-bit, 64 MB dictionary: LZHAM -mx=9 3,573,782,721 bytes with archive test time 71.292 s vs LZMA -mx=9 3,560,052,414 bytes at 223.050 s, about 3.1x) carry no hardware or compiler and mattmahoney.net is blocked here. The README also says the decoder is slower than zlib's and only overtakes LZMA's above roughly 1,000-13,000 compressed bytes, so it is a poor fit for small blocks. The improved branch richgel999/lzham_codec_devel is already in the catalogue at tier C on that README evidence; this record is the stable v1.x repository, the one lzbench links and builds. The most recent commits (2022-01-03) only edit README.md; code last changed around the 2020-09-15 public-domain relicensing. Public-domain dedication (LICENSE, 2020-09-15): no patent grant. The listed code.google.com/p/lzham URL is the old alpha and was not opened.

Very asymmetric: slow, memory-hungry compressor aimed at offline use (README: about 982 MB for a 64 MB dictionary) and a decoder with a high start-up cost, only faster than LZMA beyond roughly 1-13 KB of compressed input. Decodes slower than zlib (lzbench: 273 MB/s vs zlib 1.3.2 -9 at 318 MB/s). C++03, no strict aliasing required (-fno-strict-aliasing). Public-domain dedication carries no patent grant.

## Maintenance

Abandoned: code untouched since the 2020-09-15 public-domain relicensing, last commits only edit the README, 14 open issues with no replies; small public-domain C++03 that is practical to vendor for x86/x64 if you pin the format parameters yourself and compile with -fno-strict-aliasing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** lzbench 2.4 README table (public code github.com/inikep/lzbench; LZHAM wrapper in bench/lz_entropy_codecs.cpp, which uses 0 helper threads in single-thread runs) lists lzham 1.0 -d26 -0/-1 next to lzma 26.03 -0..-9, built with gcc 15.2.0 at -O3 -DNDEBUG (public Makefile, mk/lzham.mk and mk/lzma.mk set no override) and run on one thread of an AMD EPYC 9555P. Same A treatment as the other lzbench 2.4 entries.
- **Verifier notes:** lzbench rows match exactly (lzham -1: 3.16 / 273 MB/s, 54,740,589 bytes; lzma -4: 13.6 / 73.7 MB/s, 55,936,064 bytes; 273/73.7 = 3.7x). Corrected two caveat details: lzbench supports LZHAM levels 0-4 (only the -eALL README run is limited to -0/-1), and the lzma -6/-9 size gap is 9.5-11.1% smaller rather than '10-12% smaller'. Same project as already-verified richgel999/lzham_codec_devel (tier C, README evidence only); the orchestrator may fold the devel id into this one (or record duplicate on one of them), since this id carries the stronger lzbench evidence.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** lzbench 2.4 (verifier); enricher lzbench harness reading
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzham.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzma.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lz_entropy_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/codecs.h>
  - <https://github.com/richgel999/lzham_codec>
  - <https://github.com/richgel999/lzham_codec/commits>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/richgel999/lzham_codec>
  - <https://github.com/richgel999/lzham_codec/issues>
  - <https://github.com/richgel999/lzham_codec/issues/19>
  - <https://github.com/richgel999/lzham_codec/issues/22>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/include/lzham.h>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/lzhamdecomp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/lzhamdecomp/lzham_core.h>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/lzhamdecomp/lzham_lzdecomp.cpp>
  - <https://raw.githubusercontent.com/richgel999/lzham_codec/HEAD/lzhamcomp/lzham_lzcomp.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzham.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lz_entropy_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/codecs.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/misc/7-zip/LzmaEnc.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/lzham/lzhamdecomp/lzham_lzdecomp.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/lzham/lzhamdecomp/lzham_core.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/lzham/include/lzham.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/lzham/lzhamcomp/lzham_lzcomp.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/richgel999/lzham_codec`) · [data/wave9/enrich/raw/github_com_richgel999_lzham_codec.json](../../../data/wave9/enrich/raw/github_com_richgel999_lzham_codec.json) (enrichment confidence 0.8)

</details>
