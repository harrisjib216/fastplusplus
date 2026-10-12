# libbzip2 (bzip2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C` · `bzip2-1.0.6 (the 'bzip2 and libbzip2 License v1.0.6', a permissive BSD-style licence, as shown on the GitLab page and API); the SPDX licence list (3.29) marks bzip2-1.0.6 as not OSI-approved; no patent grant` · 🔴 abandoned

> Reference bzip2/libbz2: Burrows-Wheeler compressor whose decoder is 2.5-14x faster than PPMd at a similar ratio, but slow by modern standards.

| | |
|---|---|
| **Beats** | ppmd8 (7-Zip PPMd var.I, ppmd8 26.03 as built in lzbench), the PPM family the bzip2 manual compares itself with |
| **Claimed result** | bzip2 1.0.8 -9: 12.7 MB/s compress, 35.5 MB/s decompress, 54,572,811 bytes (25.75%). ppmd8 26.03 -4: 12.8 / 11.5 MB/s, 51,241,932 bytes (24.18%); ppmd8 -1: 15.7 / 14.0 MB/s, 55,803,295 bytes (26.33%); ppmd8 -9: 2.61 / 2.55 MB/s, 48,207,763 bytes (22.75%). Decompression is about 3.1x faster than ppmd8 -4, 2.5x faster than ppmd8 -1 (with 2% smaller output) and 13.9x faster than ppmd8 -9 (derived from page data); compression is level with ppmd8 -4, 4.9x faster than -9 and 1.2x slower than -1. Against lzma 26.03 -9 (2.55 / 78.2 MB/s, 22.97%) bzip2 -9 compresses about 5x faster but decompresses 2.2x slower and is 12% larger (derived). |
| **Workload** | lzbench 2.4, in-memory, single thread, silesia.tar (211,947,520 bytes): compress and decompress speed and output size of bzip2 1.0.8 against ppmd8 26.03 (and lzma 26.03). |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P @ 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench24_x86_64-linux-gnu-gcc15 release binary), lzbench options -eALL -t8,8 -o1c4; the public lzbench Makefile builds with -O3 |
| **Adoption** | GitLab project bzip2/bzip2 (now titled 'bzip2-archived', archived): 93 stars, 27 forks; GitHub mirror libarchive/bzip2 (a clone of an earlier GitLab repo) has 64 stars and 34 forks; bzip2 1.0.8 tag dated 2019-07-13; the system bzip2 library of essentially every Linux distribution |
| **Last commit** | 2023-05-31 |
| **Links** | [repository](https://gitlab.com/bzip2/bzip2) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 -O3 release binary, one thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar) measured bzip2 1.0.8 -9 at 12.7 MB/s compress, 35.5 MB/s decompress and 54,572,811 bytes, versus 7-Zip ppmd8 26.03 -4 at 12.8/11.5 MB/s and 51,241,932 bytes and ppmd8 -1 at 15.7/14.0 MB/s and 55,803,295 bytes: about 3.1x and 2.5x faster decoding with equal or slower compression (derived from page data). lzbench's ppmd8 levels map to small models (level L uses order 3+L and 2^(L-1) MB, so -1 is an order-4, 1 MB model reset whenever memory fills), and every run is checked by memcmp against the input.

## Use it when

- You must read or write .bz2 (tarballs, archives, scientific and genomics files, legacy pipelines); libbz2 is the system library on essentially every Linux distribution.
- Text-like data where you want a better ratio than zlib (25.75% vs 31.92% for zlib 1.3.2 -9 on silesia.tar) with small, bounded memory: about 7.6 MB to compress and 3.7 MB to decompress at -9, or 2.3 MB with the small decoder.
- When you are choosing between bzip2 and a PPM codec and decode speed matters: bzip2 -9 decodes 3.1x faster than ppmd8 -4 and 2.5x faster than ppmd8 -1 at a 2% smaller output than the latter (lzbench 2.4, derived from page data).
- Embedded or constrained builds: the low-level interface is plain C89 with no globals and can be built with -DBZ_NO_STDIO.

## Skip it when

- Any new format choice: in the same lzbench 2.4 table zstd 1.5.7 -18 is 2.4% smaller and decodes 33x faster (1175 vs 35.5 MB/s, though it compresses 3.1x slower), lzma 26.03 -4 is 2.5% larger but compresses 1.07x and decodes 2.1x faster, and lzma -9 is 10.8% smaller and decodes 2.2x faster (derived from page data).
- When you need the best BWT ratio: bsc 3.3.12 -m0 -e1 is 9.7% smaller and compresses 1.5x faster, bzip3 1.5.4 -5 is 13.4% smaller (both decode slower than bzip2).
- When you need bzip2-format speed: lbzip2 2.6.5 -9 writes the same format at the same size and is 1.76x faster to compress and 1.32x faster to decompress on one thread, and it parallelizes.
- Multi-core or random access: libbz2 is single-threaded and the format does not record compressed block sizes, so parallel decoding means scanning for block magic (the manual names this as a format flaw; GitLab issues #11 parallel compression and #12 faster BWT stay open).
- Small messages or latency-sensitive paths: blocks are 100-900 KB and the BWT needs the whole block before output.

## How it is fast

Against PPM the speed comes from the transform, not tuning: an initial run-length pass, a Burrows-Wheeler transform (radix pre-sort plus multikey quicksort in mainSort, with a fallbackSort when a work budget runs out on repetitive data), move-to-front, zero-run coding and up to 6 canonical Huffman tables switched every 50 symbols. Decoding is Huffman decoding plus an inverse BWT that walks one 4-bytes-per-symbol array (BZ_GET_FAST), which is far cheaper than PPMd's per-symbol context modelling and range decoding, so the decoder wins even though PPM is symmetric. The decoder still looks up Huffman code lengths bit by bit and chases cache-missing pointers, which is why it decodes at 35.5 MB/s while LZ decoders run at hundreds.

## Compared with alternatives

Pick libbz2 only when the .bz2 format is required and you want the canonical, distro-shipped implementation; for bzip2-format speed lbzip2 is faster on one core and scales across cores, and for anything format-free zstd, xz/LZMA or bzip3/libbsc beat it on ratio, speed or both.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libbz2; Meson or CMake on the 1.1 master branch, classic Makefile in the 1.0.8 release) |
| **Dependencies** | none |
| **Minimum toolchain** | C89 (meson default c_std=c89); Meson 0.56+ or CMake 3.12+ for the 1.1 master build |
| **Platforms** | any (portable C; Unix, Windows via CMake/nmake, MinGW with open build issues) |
| **Thread safety** | Low-level BZ2_bzCompress/BZ2_bzDecompress interface has no globals and is thread-safe per stream (manual); the high-level stdio layer reports I/O errors through errno, and the zlib-compatible bzopen/bzread/bzwrite functions are marked untested and not checked for thread safety. |
| **Drop-in for the baseline** | no |

## Gotchas

- Use 1.0.8 or later: 1.0.7 fixed CVE-2019-12900 (nSelectors out of range in the decoder, found by fuzzing) and CVE-2016-3189 (use-after-free in bzip2recover); the 1.0.7 fix rejected some lbzip2-written files and 1.0.8 relaxed it (GitLab issue #24).
- BZ2_bzBuffToBuffCompress/Decompress take unsigned int lengths, so one-shot calls are limited to under 4 GB; use the streaming API for larger data.
- Highly repetitive input can make compression up to about 10x slower than average (manual); the fallback sort is about 3x slower than the main sort, and workFactor (default 30) controls when it kicks in. Decompression speed is unaffected.
- The 1.1 master branch changes the Linux SONAME to libbz2.so.1 (1.0 used libbz2.so.1.0; CMake -DUSE_OLD_SONAME=ON builds both) and ships no Makefile (open issue #60); the archived GitLab fork will not get fixes, so take release code from sourceware.

## Known shortcomings

- lzbench 2.4 rows: compression is not faster than ppmd8 and the codec is slower or larger than lbzip2, lzma and zstd; the manual claims only that the ratio approaches the PPM family. The bzip2-1.0.6 licence is BSD-style but not OSI-approved, so usability is reference (BSD-3-Clause-Clear precedent). Repo archived, last commit 2023-05-31.
- Enricher: the lzbench ppmd8 baseline is small (level L is order 3+L with 2^(L-1) MB, so -1 is order 4 with a 1 MB model reset when memory fills); lzma -4 decodes 2.1x faster at 2.5% larger output and lbzip2 (same format) compresses 1.76x and decompresses 1.32x faster. Unmerged GitLab issue #40 (mainGtU patch) claims 10-20% faster compression. Lead: libbzip2-rs (trifectatechfoundation, c2rust port, about 14% faster level-1 compress and 4-8% faster decode per snippet) is a port, so the duplicate rule applies if found.

## Caveats and trade-offs

The speed claim against PPM is not in the code repository: the manual in this repo (docs/manual.xml) only says compression 'approaches the performance of the PPM family of statistical compressors' and itself recommends zlib or LZO for anyone wanting something faster. The figures 'within 10% to 15% of the best available techniques (the PPM family), whilst being around twice as fast at compression and six times faster at decompression' come from the bzip.org project description, seen only as a WebSearch snippet repeated on HPC documentation sites (bzip.org and sourceware.org are blocked here). lzbench reproduces the decompression half (2.5x to 14x faster than ppmd8 depending on level) but not the compression half (level with ppmd8 -4, 1.2x slower than ppmd8 -1 at similar size). The comparison is against one PPMd implementation (7-Zip PPMd var.I), and ppmd8 -4 gives a 6% smaller output. bzip2 is slower or larger than modern codecs in the same table (lbzip2 2.6.5 -9 compresses 22.4 MB/s and decompresses 47.0 MB/s at the same size; lzma 26.03 -4 and zstd 1.5.7 -18 reach similar or smaller outputs at 26.39% and 25.14% while decompressing 73.7 and 1175 MB/s, though zstd -18 compresses at only 4.13 MB/s). The GitLab repository is the archived 1.1+ development fork ('archived due to lack of interest, and because there are better options available through the Rust ecosystem'); its last commit is 2023-05-31 and it carries the bzip2-1.0.8 tag (2019-07-13), so the benchmarked 1.0.8 sources are in this repo as well as at sourceware.org. Licence is a permissive BSD-style text that SPDX does not list as OSI-approved, so usability follows the non-OSI rule (reference); no patent grant. The record fills the project's slot; its value is as the reference implementation, not as a fast codec.

Block-sorting (Burrows-Wheeler) compressor with a better ratio than zlib (25.75% at -9 vs 31.92% for zlib 1.3.2 -9 in the same table) but slow decoding (35.5 MB/s vs 318 MB/s for zlib -9) and a single-threaded reference implementation. The patent-free, library-callable (libbz2) incumbent that lbzip2 and bzip3 are measured against.

## Maintenance

The GitLab 1.1 fork is archived ('lack of interest, and because there are better options available through the Rust ecosystem', last commit 2023-05-31) while 1.0.8 (2019) lives on at sourceware; usability is reference because SPDX marks the permissive BSD-style bzip2-1.0.6 licence as not OSI-approved, though it is free to use, small C89 and universally packaged.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** lzbench 2.4 README table (public benchmark code github.com/inikep/lzbench, bench/lzbench.h codec table) lists bzip2 1.0.8 -1/-5/-9 next to ppmd8 26.03 -1/-4/-9 and lzma 26.03, run with the gcc 15.2.0 release binary on a single thread of an AMD EPYC 9555P; the public Makefile builds bzip2, ppmd and lzma objects with -O3 -DNDEBUG (mk/bzip2.mk and mk/ppmd.mk set no -O2 override). Same A treatment as the other lzbench 2.4 entries (wave 9 retier-02).
- **Verifier notes:** Numbers match the lzbench 2.4 README rows exactly and the derived ratios check out (35.5/11.5 = 3.1x, 35.5/14.0 = 2.5x, 35.5/2.55 = 13.9x decode; 12.7 vs 12.8 MB/s compress). Fixed last_commit (2023-05-31 from the GitLab API; the repo also holds the 1.0.8 tag) and set usability to reference because SPDX marks bzip2-1.0.6 not OSI-approved (precedent: BSD-3-Clause-Clear set to reference); the orchestrator may override that since the licence is BSD-style permissive. Shortcomings: archived repo, compression not faster than PPMd, slower or larger than lbzip2, lzma and zstd in the same table, 2x/6x project claim seen as snippet only.
- **Fields the verifier corrected:** `last_commit`, `license`, `usability`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** lzbench 2.4 (verifier); enricher lzbench reading
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/bzip2.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/ppmd.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzma.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://gitlab.com/bzip2/bzip2>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2?license=true>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2/repository/commits?per_page=3>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2/repository/tags?per_page=20>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2/repository/tree?per_page=100&recursive=true>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/README.md>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/docs/manual.xml>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/man/bzip2.1>
  - <https://github.com/libarchive/bzip2>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/README.md>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/NEWS.md>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/COPYING>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/COMPILING.md>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/patches-not-included.txt>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/bzlib.h>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/bzlib.c>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/bzlib_private.h>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/blocksort.c>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/compress.c>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/decompress.c>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/huffman.c>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/docs/manual.xml>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/meson.build>
  - <https://gitlab.com/bzip2/bzip2/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2?license=true>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2/repository/tree?per_page=100&recursive=true>
  - <https://gitlab.com/api/v4/projects/bzip2%2Fbzip2/issues?state=all&per_page=100>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/bzip2.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/ppmd.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/symmetric_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/blocksort.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/decompress.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/compress.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/huffman.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/bzlib.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bwt/bzip2/bzlib_private.h>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://gitlab.com/bzip2/bzip2`) · [data/wave9/enrich/raw/gitlab_com_bzip2_bzip2.json](../../../data/wave9/enrich/raw/gitlab_com_bzip2_bzip2.json) (enrichment confidence 0.8)

</details>
