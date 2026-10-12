# FiniteStateEntropy (FSE and Huff0)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟡 stale

> Yann Collet's standalone tANS (FSE) and 4-stream Huffman (Huff0) block coders, the entropy stage later built into zstd.

| | |
|---|---|
| **Beats** | zlibh (the Huffman encoder inside zlib, as packaged by Frederic Kayser) |
| **Claimed result** | Proba80: Huff0 1350 MB/s decode and 600 MB/s encode vs zlibh 300 / 265 MB/s (about 4.5x decode, 2.3x encode, derived); FSE 440 / 325 MB/s with ratio 8.84 vs 6.38 for Huffman and zlibh. Proba14: Huff0 860 vs zlibh 250 MB/s decode. Proba02: Huff0 555 vs zlibh 210 MB/s decode. |
| **Workload** | Compression and decompression of generated probability-distribution files (Proba80, Proba14, Proba02, made with the repo's probagen), 32 KB blocks. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-5600U, Linux Mint 64-bit |
| **Compiler and flags** | GCC 4.8.4, 64-bit mode (optimisation flags not stated) |
| **Adoption** | 1.5k stars; FSE and Huff0 are the entropy stage of zstd |
| **Last commit** | 2024-03-10 |
| **Links** | [repository](https://github.com/Cyan4973/FiniteStateEntropy) · [benchmark](https://github.com/Cyan4973/FiniteStateEntropy/blob/dev/README.md) |

## Verdict

On an Intel Core i7-5600U (Linux Mint, GCC 4.8.4, 64-bit, flags not stated; the programs Makefile defaults to -O3), the author's README splits probagen-generated files into 32 KB blocks: Huff0 decodes 1350/860/555 MB/s on Proba80/14/02 versus zlibh's 300/250/210 MB/s and encodes 600/595/525 versus 265/255/180 MB/s, while FSE runs 325-330 MB/s encode and 440-460 MB/s decode with the best ratio on Proba80. The baseline is zlib's Huffman stage as packaged by Frederic Kayser, on synthetic data only.

## Use it when

- You are building your own compressor format and need an order-0 entropy stage after LZ, BWT or transform coding, with per-block (up to 128 KB for Huff0) static statistics
- Skewed byte distributions where Huffman's 1-bit-per-symbol floor costs ratio: FSE reached 8.84x on Proba80 versus 6.38x for Huff0 and zlibh
- Flat or moderately skewed data where decode speed matters more than the last percent of ratio: Huff0 decoded 2.9-4.5x faster than zlibh in the README tests
- You want to study or prototype with the upstream reference of the coders inside zstd, in a small set of files that compile independently for compression or decompression

## Skip it when

- Untrusted input or fuzz-exposed services: four open memory-safety reports from 2025-2026 (#121 heap write overflow in FSE_compress_usingCTable on single-symbol input, #122 stack underflow in FSE_compress2, #123 segfault in FSE_decompress_usingDTable on a 6-byte round trip, #124 1-byte out-of-bounds write in HUF_decompress4X1 when dstSize is small and not a multiple of 4) have no maintainer reply
- Production use where you can take zstd instead: zstd's lib/common and lib/compress carry the maintained, fuzzed copies of the same FSE and Huff0 code, while this repo's library code has had no functional change since 2020
- Peak entropy-decode throughput on current CPUs: later SIMD rANS and Huffman decoders (hypersonic-rANS, htscodecs, PIVCO-Huffman) report several times FSE's and Huff0's decode speed
- Alphabets above 256 symbols with Huff0 (HUF_SYMBOLVALUE_MAX 255); FSE has a separate fseU16 variant, with an open clipping bug (#97)
- Adaptive or context-mixing models: both coders assume one static distribution per block, sent as a header

## How it is fast

FSE is Jarek Duda's tANS: symbol probabilities are normalized to a power of two (2^tableLog, default 2^13 table) and each symbol becomes one table lookup plus a variable bit read or write, with no multiplication or division; the decoder runs two interleaved states over one bitstream so the CPU overlaps their dependency chains. Huff0 splits each block into four independently decodable streams behind a jump table and decodes them in one loop for instruction-level parallelism, with single-symbol (X1) and double-symbol (X2) lookup tables limited to 11-12 bits and an optional BMI2 code path. Both use a 64-bit branch-light bit container (bitstream.h) that refills with unaligned word loads.

## Compared with alternatives

Pick it when you need a portable, plain-C pair of block coders with a precise tANS option and no SIMD requirement, or the upstream reference for zstd's entropy stage; for raw decode speed hypersonic-rANS (enwik8 decode about 3.1x FSE) and PIVCO-Huffman (5.9x huf0 X2 on Apple M4 Max) win, and htscodecs gives a maintained interleaved rANS library.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc malloc/free only for the create/free table helpers; workspace variants avoid allocation) |
| **Minimum toolchain** | C89-compatible with C99 stdint.h used when available; a 2024 PR updated the programs/ build for current compilers; README benchmark used GCC 4.8.4 |
| **Platforms** | any; little- and big-endian handled through MEM_isLittleEndian; BMI2 decode path on x86-64 when enabled; GitHub Actions builds all supported platforms |
| **Thread safety** | Not documented; functions work on caller-supplied tables, buffers and workspaces with no global state seen in the sources, so separate contexts per thread is the safe assumption |
| **Drop-in for the baseline** | no |

## Gotchas

- Return value 0 means incompressible (nothing written) and FSE_compress returns 1 for single-symbol input (use RLE); FSE_decompress cannot decode either case, so your format must flag them
- HUF_decompress needs the exact original size, and HUF_compress rejects blocks larger than 128 KB
- Everything under HUF_STATIC_LINKING_ONLY / FSE_STATIC_LINKING_ONLY (table sizes, workspace and X1/X2 APIs) is marked unstable and not for dynamic libraries
- lib/ is dual BSD-2-Clause or GPLv2 at your option, but the programs/ benchmark and fuzzer tools are GPLv2 only

## Known shortcomings

- Tier C: README numbers reproduce but optimisation flags are not stated. lib/ is dual BSD-2-Clause/GPLv2 while programs/ is GPLv2 only. Last commit 2024-03-10, stale.
- Four open memory-safety issues (2025-2026), none answered: #121 heap write overflow in FSE_compress_usingCTable on single-symbol input, #122 stack underflow in FSE_compress2, #123 segfault in FSE_decompress_usingDTable, #124 1-byte out-of-bounds write in HUF_decompress4X1. The library code has not been synced with zstd since 2020 (the 2024 commits are CI/build only); use zstd's copy for untrusted input.

## Caveats and trade-offs

Benchmark is old (GCC 4.8.4, Broadwell laptop, optimisation flags not stated) and uses only synthetic generated distributions with 32 KB blocks. Baseline zlibh is a weak Huffman. Better modern Huffman decoders exist (see PIVCO-Huffman and hypersonic-rANS entries). zstd itself (facebook/zstd) is on the known list; this entry is the standalone upstream FSE/Huff0 repo, whose dev branch last changed 2024-03-10. The lib/ sources are dual BSD-2-Clause/GPLv2; the test and benchmark tools in programs/ are GPLv2 only.

FSE is a table-based tANS coder (precise like arithmetic coding, but slower than Huff0); Huff0 is Huffman with 4-stream interleaving, loses ratio on skewed distributions (cannot go below 1 bit per symbol). Both are block-oriented with a header describing the distribution.

## Maintenance

Stale: the last commits (March 2024) touched only CI and the benchmark build, the library code last synced with zstd in 2020, and four memory-safety issues are unanswered; BSD-2-Clause library code is easy to vendor, but take zstd's copy for anything exposed to untrusted data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchmark table compares Huff0 and FSE against zlibh with the exact numbers in the record, on an i7-5600U with GCC 4.8.4; benchmark code is public (programs/bench.c, programs/zlibh.c, probaGenerator.c) but optimisation flags for the README run are not stated, so first-party C.
- **Verifier notes:** README numbers match the record exactly; derived ratios (4.5x decode, 2.3x encode) check out. BSD-2-Clause, 1.5k stars, 166 forks, not archived, last commit 2024-03-10 (stale is right).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Cyan4973/FiniteStateEntropy>
  - <https://github.com/Cyan4973/FiniteStateEntropy/commits/dev>
  - <https://github.com/Cyan4973/FiniteStateEntropy/tree/dev/programs>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/README.md>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/LICENSE>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/fse.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/programs/fullbench.c>
- **Sources the enricher read:**
  - <https://github.com/Cyan4973/FiniteStateEntropy>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/README.md>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/README.md>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/LICENSE>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/fse.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/huf.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/fse_compress.c>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/fse_decompress.c>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/huf_decompress.c>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/bitstream.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/mem.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/lib/compiler.h>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/programs/Makefile>
  - <https://github.com/Cyan4973/FiniteStateEntropy/issues?q=is%3Aissue>
  - <https://github.com/Cyan4973/FiniteStateEntropy/issues/124>
  - <https://github.com/Cyan4973/FiniteStateEntropy/issues/123>
  - <https://github.com/Cyan4973/FiniteStateEntropy/issues/121>
  - <https://github.com/Cyan4973/FiniteStateEntropy/issues/112>
  - <https://github.com/Cyan4973/FiniteStateEntropy/commits/dev>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/cyan4973/finitestateentropy`) · [data/wave9/enrich/raw/github_com_cyan4973_finitestateentropy.json](../../../data/wave9/enrich/raw/github_com_cyan4973_finitestateentropy.json) (enrichment confidence 0.85)

</details>
