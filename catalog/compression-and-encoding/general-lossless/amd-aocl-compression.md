# AOCL-Compression

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `BSD-3-Clause AND MIT AND NCSA (file-by-file per LICENSE.txt)` · 🟢 active

> AMD's Zen-tuned forks of zlib, zstd, lz4, snappy, bzip2 and lzma behind one C API; level-9 zlib compresses about 3.7x faster.

| | |
|---|---|
| **Beats** | zlib; also bzip2, snappy, zstd, lz4, xz/lzma upstream implementations |
| **Claimed result** | Level 9: aocl-zlib 27.47 MB/s compress, 439.38 MB/s decompress, ratio 32.21% versus zlib 1.3.2 7.37 MB/s, 212.55 MB/s, 31.91% (about 3.7x and 2.1x, derived from page data). PR summary: zlib up to 3.7x compression and 2x decompression, bzip2 2.1-2.3x compress and +60-69% decompress, snappy +20% compress and 2x decompress, zstd +14-21% compress and +8-10% decompress. lz4 1.10.0 381.25 / 2499.41 MB/s versus aocl-lz4 400.32 / 2550.71 MB/s, about +5% and +2% (derived from page data). |
| **Workload** | Silesia corpus (211.9 MB tar), single core pinned to CPU 0, five runs; AMD-tuned builds of seven codecs compared with the stock lzbench builds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI 9 HX PRO 370 |
| **Compiler and flags** | GCC 15.2.0; compile flags not stated |
| **Adoption** | 44 stars; AMD library |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/amd/aocl-compression) · [benchmark](https://github.com/inikep/lzbench/pull/321) |

## Verdict

In an AMD developer's lzbench pull request (#321, unmerged, changes requested), single-threaded on an AMD Ryzen AI 9 HX PRO 370 with boost off, GCC 15.2.0, silesia.tar, aocl-zlib 5.3.0 -9 compressed at 27.47 MB/s and decompressed at 439.38 MB/s versus zlib 1.3.2 at 7.37 and 212.55 MB/s (ratio 32.21% versus 31.91%); aocl-bzip2 -9 ran 20.58 / 37.65 versus 8.92 / 23.16 MB/s and aocl-snappy 413 / 1434 versus 343 / 719 MB/s. The run used AOCL 5.3.0, which the 5.3.2 release notes say had GCC 15 decompression regressions in zlib and zstd, so the numbers may not match the fixed release.

## Use it when

- Server or HPC code on AMD Zen (or other x86-64) that already links zlib, bzip2 or snappy and wants faster output in the same format without changing callers: level 6-9 deflate (about 2.5-3.7x faster compress, 2x faster inflate in the vendor run) and bzip2 (about 2x compress, 1.6x decompress).
- Applications that use several codecs and want one dependency with one dispatch layer and one test suite instead of seven separately tuned libraries.
- Bulk compression of large buffers or files where the OpenMP build can split work across cores and the consumer either uses AOCL or skips the RAP header.
- Teams that need AMD-supported builds with fuzz, ASAN and Valgrind test targets on Linux and Windows.

## Skip it when

- Non-x86 targets: the optimised paths are x86-only (SSE2 to AVX512), and lzbench's reviewer asked for the Linux/x86-64 and GNU binutils restriction to be documented.
- When lz4 or zstd speed is what you need: the vendor's own run shows only +5% / +2% for lz4 and +14-21% / +8-10% for zstd, with a small ratio loss (zstd -3 31.94% versus 31.20%).
- When you need the fastest deflate regardless of library: zlib-ng, ISA-L igzip or libdeflate have independent numbers and wider platform support; AOCL has no published head-to-head with them.
- Many small blocks: Lzma_compressBound reserves a constant 16 KB pad per call (open issue #5), so chunked LZMA output buffers can be far larger than with peer codecs.
- Projects that cannot track a vendored-codec fork: AOCL re-releases upstream security fixes on its own schedule (5.3.0 shipped zlib 1.3.1-based code; 5.3.2 moved to zlib 1.3.2 'addressing known security vulnerabilities').

## How it is fast

Each codec gets algorithmic and SIMD changes chosen at run time by a function-multiversioning dispatcher (SSE2, AVX, AVX2, AVX512). In zlib this means Intel's deflate_medium strategy, Konstantin Nosov's fast_zlib longest_match, x86 slide_hash, a hash table 4x larger (AOCL_ADDITIONAL_HASH_BITS 2), PCLMUL/VPCLMULQDQ CRC-32 and Chromium/zlib-ng chunk-copy inflate (chunkset_sse2/avx512). Other codecs get match-skipping heuristics (lz4, zstd, snappy), branchless snappy decompression, LZ4HC pattern analysis and fewer bzip2 Huffman refinement passes; several of these are build-time options that trade ratio for speed.

## Compared with alternatives

Pick it over zlib-ng or the Cloudflare zlib fork when you also want bzip2 and snappy speedups and AMD support from one library; pick zlib-ng, libdeflate or ISA-L igzip when you only need deflate, need ARM, or want independently measured numbers. For bzip2-compatible output it is faster per thread in the vendor run (about 2.1x) than lbzip2's catalogued 1.6x, though the two were measured on different machines.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (CMake 3.13+, also GNU Make; CMake OBJECT target for embedding) |
| **Dependencies** | none at run time for the single-threaded build; OpenMP for AOCL_ENABLE_THREADS; GoogleTest for the test suite; Doxygen/Sphinx only for docs |
| **Minimum toolchain** | C11; GCC 8.5+ or Clang 11.0+ on Linux; Visual Studio with ClangCl on Windows |
| **Platforms** | x86-64 Linux and Windows (multi-threaded mode experimental on Windows); optimised paths need SSE2 at minimum and scale to AVX512 |
| **Thread safety** | Codec calls on separate handles/streams are independent; the dispatcher setup is global and guarded by an atomic flag or critical section, but the README warns that changing optOff/optLevel between threads calling aocl_llc_setup() is undefined behaviour, and aocl_llc_destroy resets process-wide dispatch state. |
| **Drop-in for the baseline** | partial — the native zlib/bzip2/snappy/lz4/zstd APIs keep upstream names and formats, so relinking works, but symbols clash with a system zlib or zstd in the same process unless built with AOCL_LLC_PREFIX, and multi-threaded output carries a non-standard RAP frame header that stock decoders must skip. |

## Gotchas

- Behaviour depends on environment variables read at first use: AOCL_DISABLE_OPT=ON forces reference paths, AOCL_ENABLE_INSTRUCTIONS caps the ISA, AOCL_ZLIB_QUICK_MODE=ON switches zlib levels 1, 2, 3 and 5 to faster settings with a worse ratio.
- On Windows the CMake Release build compiles everything with /arch:AVX2, and on Linux the Snappy sources are compiled with -msse4.1 and SNAPPY_HAVE_X86_CRC32=1, so not every path honours the 'portable down to SSE2' dispatch claim.
- GCC 15 needs per-file workaround flags (-fno-schedule-insns2 and others) on zlib chunkset_avx512.c and zstd_decompress_block.c; 5.3.2 notes fix 'GCC 15 decompression regressions in ZLIB and ZSTD' and 'LZ4 multi-threaded decompression data corruption', so pin 5.3.2 or later.
- aocl_llc_setup() only reports excluded or unsupported codecs, not allocation failures (lzbench review concern 4), and aocl_lzma_compress() does not check the output size up front and can underflow when outsize &lt; LZMA_PROPS_SIZE (issue #5).

## Known shortcomings

- Tier C: numbers come from the open, unmerged lzbench PR #321 by an AMD developer, where the maintainer requested changes; lz4 gains are derived from page data.
- lzbench PR #321 numbers ran AOCL 5.3.0 built with GCC 15.2.0; the 5.3.2 release notes fix 'GCC 15 decompression regressions in ZLIB and ZSTD' and 'LZ4 multi-threaded decompression data corruption', so the measured code later got correctness fixes (already tier C). Open issue #5: aocl_lzma_compress has no outsize check (underflow when outsize &lt; LZMA_PROPS_SIZE) and Lzma_compressBound pads 16 KB per call. aocl_llc_setup does not report allocation failure; dispatch state is global and destroy resets it. Windows Release builds with /arch:AVX2 globally; Linux Snappy with -msse4.1. Symbols clash with system zlib/zstd unless built with AOCL_LLC_PREFIX. Multi-threaded output carries a non-standard RAP header. x86-64 only; no head-to-head vs zlib-ng or libdeflate.

## Caveats and trade-offs

Numbers come from an open (unmerged) lzbench pull request written by an AMD developer, not a neutral run; inikep requested changes on 2026-09-19 citing seven concerns including buffer allocation impacts, symbol linking and outdated vendored code (5.3.0 versus 5.3.2). The repo README itself carries no numbers. The compress speedup is for level 9 where stock zlib is slow, and aocl-zlib ratio is slightly worse (32.21% versus 31.91%); aocl-zstd also loses some ratio (31.94% versus 31.20% at -3). Not compared against zlib-ng or libdeflate on that page. Gains are small on lz4 (+5% / +2%) and moderate on zstd. Tuned for AMD Zen CPUs. Mixed per-file licenses (BSD-3-Clause, MIT, NCSA, all OSI) plus upstream zlib, zstd, bzip2 licenses.

Tuned for AMD Zen with dynamic dispatch (SSE2 to AVX512); minor compression ratio loss in fast modes; one API for LZ4, zlib, zstd, bzip2, snappy, lzma. Vendors modified copies of the upstream codecs.

## Maintenance

Actively maintained by AMD (v5.3.2 released 2026-08-20, regular releases since 4.1) under file-by-file BSD-3-Clause, MIT and NCSA plus upstream codec licences; usable as a library, but it is a vendor fork that lags upstream codec releases and has little outside adoption (44 stars).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** lzbench PR #321 (opened 2026-08-21 by BiplabRaut, who also commits to amd/aocl-compression) gives the full lzbench command (taskset -c 0, -t3,3 -i3,3 -p1 -o4, silesia.tar), GCC 15.2.0 and an AMD Ryzen AI 9 HX PRO 370 with boost off, and shows aocl-zlib -9 at 27.47 / 439.38 MB/s, 32.21% versus zlib 1.3.2 -9 at 7.37 / 212.55 MB/s, 31.91%. It is a vendor-run measurement on an unmerged PR branch (maintainer requested changes, citing buffer allocation and linking issues among seven concerns), so it stays C under the vendor rule rather than A.
- **Verifier notes:** Every number checks against the PR page; the lz4 percentages are not in the PR's own summary, so they are now marked as derived. Repo: 44 stars, 15 forks, not archived, default branch amd-main, last commit 2026-08-20 (merge of tag v5.3.2); LICENSE.txt confirms BSD-3-Clause/MIT/NCSA file-by-file, so copyable stands.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; lzbench 2.4 (PR #321)
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench/pull/321>
  - <https://github.com/amd/aocl-compression>
  - <https://github.com/amd/aocl-compression/commits>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/LICENSE.txt>
  - <https://raw.githubusercontent.com/amd/aocl-compression/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/README.md>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/LICENSE.txt>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/api/aocl_compression.h>
  - <https://github.com/inikep/lzbench/pull/321>
  - <https://github.com/amd/aocl-compression/releases>
  - <https://github.com/amd/aocl-compression/issues?q=is%3Aissue>
  - <https://github.com/amd/aocl-compression/issues/5>
  - <https://github.com/amd/aocl-compression/issues/4>
  - <https://github.com/amd/aocl-compression/tree/amd-main/algos/zlib>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/algos/zlib/deflate_medium.c>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/algos/zlib/longest_match_x86.c>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/algos/zlib/chunkcopy.h>
  - <https://raw.githubusercontent.com/amd/aocl-compression/amd-main/algos/zlib/deflate.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/amd/aocl-compression`) · [data/wave9/enrich/raw/github_com_amd_aocl_compression.json](../../../data/wave9/enrich/raw/github_com_amd_aocl_compression.json) (enrichment confidence 0.7)

</details>
