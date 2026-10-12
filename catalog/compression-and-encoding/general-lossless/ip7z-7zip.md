# LZMA (7-Zip LZMA SDK)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `LicenseRef-PublicDomain` · 🟢 active

> Igor Pavlov's public-domain LZMA/LZMA2 codec behind 7-Zip: 11% smaller than bzip2 -9, 2.2x faster decoding, 5x slower compression.

| | |
|---|---|
| **Beats** | bzip2 1.0.8 |
| **Claimed result** | lzma 26.03 -9: 2.55 MB/s compress, 78.2 MB/s decompress, 48,682,482 bytes (22.97%); bzip2 1.0.8 -9: 12.7 MB/s compress, 35.5 MB/s decompress, 54,572,811 bytes (25.75%). Decompression about 2.2x faster with 10.8% smaller output, but compression about 5.0x slower (derived from page data). At matching output size: lzma 26.03 -0 29.5 / 62.3 MB/s, 60,520,844 bytes (28.55%) against bzip2 1.0.8 -1 13.5 / 41.1 MB/s, 60,484,813 bytes (28.54%): about 2.2x faster compress and 1.5x faster decompress (derived from page data). |
| **Workload** | lzbench 2.4, in-memory, single thread, whole silesia.tar (211,947,520 bytes): compress speed, decompress speed and output size of 'lzma 26.03' (the 7-Zip LZMA SDK code as built in lzbench; the glue in bench/lz_entropy_codecs.cpp actually encodes an LZMA2 stream with Lzma2Enc_Encode2 at the given level and decodes it with Lzma2DecMt_Decode through memcpy-based in-memory ISeqInStream/ISeqOutStream adapters) against bzip2 1.0.8 (BZ2_bzBuffToBuffCompress/Decompress) at several levels. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P @ 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench24_x86_64-linux-gnu-gcc15 release binary), lzbench options -eALL -t8,8 -o1c4; per the public lzbench Makefile and mk/lzma.mk the 7-Zip objects in misc/7-zip (CpuArch, LzFind, LzFindOpt, LzFindMt, LzmaDec, LzmaEnc, Threads, 7zStream, Alloc, Lzma2Dec, Lzma2DecMt, Lzma2Enc, MtCoder, MtDec) are built as C only at -O3 -DNDEBUG -fomit-frame-pointer -fstrict-aliasing -ffast-math -std=gnu99, without 7-Zip's x86 assembler decoder (Asm/x86 LzmaDecOpt, Z7_LZMA_DEC_OPT); bzip2 1.0.8 (mk/bzip2.mk) uses the same flags. |
| **Adoption** | ip7z/7zip GitHub repo 4.1k stars, 441 forks, 17 commits each a release snapshot by user ip7z (latest '26.04', 2026-10-06), and its GitHub releases carry the official 7-Zip binaries and source archives (7z2604-x64/arm64 installers, 7z2604-linux-x64.tar.xz, 7z2604-src.tar.xz); 7-Zip 26.04 released 2026-10-06 (the 7,243 weekly SourceForge downloads figure is from the search record and was not re-checked); LZMA/LZMA2 are the default methods of the 7z and xz formats |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ip7z/7zip) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (release binary built with gcc 15.2.0 at -O3, one thread of an AMD EPYC 9555P at 3.20 GHz with turbo off, silesia.tar of 211,947,520 bytes) measured lzma 26.03 -9 at 2.55 MB/s compress and 78.2 MB/s decompress with 48,682,482 bytes of output, against bzip2 1.0.8 -9 at 12.7 / 35.5 MB/s and 54,572,811 bytes: 2.2x faster decoding, 10.8% smaller output and 5.0x slower compression. At matched size, lzma -0 against bzip2 -1 is 2.2x faster to compress and 1.5x faster to decode (derived from page data). lzbench encodes an LZMA2 stream with Lzma2Enc_Encode2 (numTotalThreads = 1) and decodes it with Lzma2DecMt_Decode using the C decoder only; every run is memcmp-checked against the input.

## Use it when

- Compress-once, read-many artifacts where size matters more than decode speed: in lzbench 2.4, lzma -9 is 10.8% smaller than bzip2 -9 and 28% smaller than zlib -9 on silesia.tar, and it decodes at 78 MB/s.
- Replacing bzip2 when you can change the format: at equal output size, lzma -0 compresses 2.2x and decompresses 1.5x faster than bzip2 -1, and lzma -4 is 1.07x and 2.1x faster than bzip2 -9 at 2.5% larger output (derived from page data). lzma -6 is the usual sweet spot (3.13 / 78.4 MB/s, only 1.8% larger than -9).
- When you need dependency-free, public-domain code to read or write raw LZMA, LZMA2 or .7z streams inside a C or C++ program. The decoder is LzmaDec.c plus four headers, uses 200-400 bytes of stack and 16 KB of state plus the dictionary.
- Embedded or installer decompression where code size and decoder memory matter more than throughput (Z7_LZMA_SIZE_OPT shrinks the decoder further).
- Builds where you can assemble 7-Zip's LzmaDecOpt (x64 via asmc or UASM, arm64 via GNU as) to recover the roughly 30-50% decode speed that a C-only build gives up.

## Skip it when

- Decode-heavy workloads: in the same lzbench table zstd 1.5.7 -18 decodes 15x faster (1175 vs 78.2 MB/s) at 9.5% larger output, brotli -11 4.9x faster at 3.5% larger, zlib -9 4.1x faster at 39% larger, and LZHAM -1 3.5x faster at 12% larger (derived from page data).
- Compression throughput: -9 runs at 2.55 MB/s on one thread. bzip3 -5 compresses 4.7x faster with 3% smaller output, though it decodes 6.3x slower. Fast LZMA2 -10 writes the same LZMA2 format at the same size 1.33x faster.
- Memory-limited encoders: the encoder needs about dictSize x 11.5 + 6 MB, which is about 2.9 GB at the 64-bit -9 default (256 MB dictionary). The decoder needs the whole dictionary unless it decodes straight into a full-size output buffer with LzmaDecode.
- Plain .xz handling: liblzma (xz 5.8.4) writes and reads the container with integrity checks and decodes faster in lzbench (122 vs 78.2 MB/s, partly an asm-versus-C build difference). The raw .lzma format has no checksum.
- Projects that cannot audit licences file by file: the repository is LGPL-2.1+ with BSD and unRAR-restricted parts; only the files whose header says 'Public domain' are free to copy.

## How it is fast

Against bzip2 the decoder wins because it does no block sort to undo: it decodes one bit at a time with a range coder against context-selected probabilities (literal context bits lc/lp, position bits pb, rep-match state machine) and copies matches out of a window of up to 256 MB at the default -9 on 64-bit. The ratio comes from that large window plus near-optimal parsing over a binary-tree (bt4) match finder at levels 5-9 (hash chains and a fast parser at 0-4). The per-bit range decoding is also why it tops out near 60-80 MB/s single-threaded. Speed-ups beyond the portable C: SSE4.1/AVX2/NEON match-finder normalisation, a second match-finder thread (LzFindMt), and hand-written x64 and arm64 decoders (LzmaDecOpt), which src-history 18.03 says run about 30% faster than the C decoder.

## Compared with alternatives

Pick the LZMA SDK over libbzip2 or lbzip2 whenever the format is yours to choose (11% smaller and 2.2x faster decoding at -9), and over xz/liblzma when you need public-domain raw LZMA, LZMA2 or .7z code or the smallest embeddable decoder. For .xz files prefer liblzma; for faster compression to the same LZMA2 stream prefer Fast LZMA2; for decode speed at a similar ratio prefer LZHAM or zstd -18.

## Integration

| | |
|---|---|
| **Form** | source-drop (C files from C/: LzmaDec, LzmaEnc, LzFind, LzFindMt, LzFindOpt, Lzma2\*, Threads, CpuArch plus headers; 7-Zip's site also ships them as a separate LZMA SDK archive) |
| **Dependencies** | none; POSIX or Win32 threads for LzFindMt, Lzma2DecMt and MtCoder unless built with Z7_ST |
| **Minimum toolchain** | Portable C; DOC/readme.txt lists MSVC 6.0 through VS2022, GCC and Clang; lzbench builds it with gcc 15.2.0 -std=gnu99. The optional asm decoder needs asmc or UASM for x64 MASM syntax, or GNU as for arm64. |
| **Platforms** | any (x86, x86-64, ARM, ARM64 and others); SSE4.1/AVX2/NEON match-finder paths chosen at run time; asm decoders for x64 and arm64 only |
| **Thread safety** | Each CLzmaEnc, CLzmaDec or Lzma2 handle is independent and allocators are passed per call. The only process global is the SIMD function pointer that LzFindPrepare() sets. By default the encoder starts its own match-finder thread at levels 5-9. |
| **Drop-in for the baseline** | no |

## Gotchas

- Defaults differ from the header docs. LzmaLib.h (dated 2023-04-02) still lists 64 MB for level 9, but LzmaEncProps_Normalize (changed in 24.09 per src-history) gives 32/64/128/256/256 MB for levels 5-9 on 64-bit. Unless reduceSize or Lzma2Enc_SetDataSize is set, the stream advertises that dictionary and the decoder allocates all of it. lzbench never sets it, so its -9 row uses a 256 MB window, against 64 MiB for xz -9.
- LzmaEncode and LzmaCompress default to numThreads = 2 in normal mode (levels 5-9), so a 'single-threaded' call spawns a match-finder thread. Set numThreads = 1 or build with Z7_ST. lzbench forces one thread through numTotalThreads = 1, so its compression figures are truly single-threaded.
- Harness asymmetry in lzbench: the lzma row is the C decoder (no Z7_LZMA_DEC_OPT or LzmaDecOpt.asm), while the xz 5.8.4 row gets liblzma's x86-64 inline-asm range decoder by default (range_decoder.h picks LZMA_RANGE_DECODER_CONFIG 0x1F0 for GCC/Clang, and lzbench's hand-written config.h does not override it). ip7z/7zip issue #11 measured the asm decoder 1.53x faster than C (7z b on an Intel N100: 68.6 vs 44.9 MB/s), so most of the 122 vs 78.2 MB/s gap to xz is a build difference. The bzip2 comparison is C against C and stands. Decode timing also includes a per-call dictionary allocation and an extra memcpy of input and output through Lzma2DecMt's 1 MB stream buffers: a small cost at 78 MB/s (estimate).
- The .lzma 'alone' header (properties, dictionary size, uncompressed size) carries no checksum, so verify integrity yourself or use .xz/.7z. Vendored copies do not get 7-Zip's security fixes: 26.02 fixed CVE-2026-14266, a heap overflow in XZ chunked-data handling (from search snippets; which file was fixed is not documented in src-history). LzFindPrepare() must be called once by the application to enable the SIMD match-finder normalisation; the library never calls it.

## Known shortcomings

- lzbench 2.4 win is off-baseline (bzip2 is not a general-lossless baseline); loses to in-list xz 5.8.4 on both speeds at the same size; decodes far slower than zstd and brotli; compresses 5.0x slower than bzip2 -9. lzbench builds the C-only decoder without the 7-Zip asm LzmaDecOpt, so decode is likely understated; the row is really LZMA2 (Lzma2Enc/Lzma2DecMt) through memcpy stream adapters; one corpus, one machine. LZMA SDK files are public domain (no patent grant), the rest of the repo LGPL-2.1+ / BSD / unRAR restriction. 7-Zip itself publishes no speed claims (www.7-zip.org ENOTFOUND).
- Enricher: lzbench builds the lzma row with the C decoder only (no Z7_LZMA_DEC_OPT or LzmaDecOpt.asm) while the same table's xz 5.8.4 row gets liblzma's x86-64 inline-asm range decoder (LZMA_RANGE_DECODER_CONFIG 0x1F0 default); ip7z/7zip issue #11 measured the asm decoder 1.53x faster than C (68.6 vs 44.9 MB/s on an N100), so most of the decode gap to xz (122 vs 78.2 MB/s) is a build difference. lzbench never sets the data size, so lzma -9 runs a 256 MB dictionary against xz -9's 64 MiB; decode timing includes a per-call dictionary allocation and memcpy through 1 MB stream buffers. Encoder needs about 2.9 GB at -9 (LzmaLib.h still says 64 MB), starts a second match-finder thread by default, and the raw .lzma format has no checksum. 26.02 fixed CVE-2026-14266 (heap overflow in XZ chunked data, snippet only). The bzip2 claim itself stands (C vs C, memcmp-checked, single-threaded).

## Caveats and trade-offs

Off-baseline win: bzip2 is not one of the spec's general-lossless baselines (zlib, zstd, lz4, brotli, xz), and against the in-list baseline xz 5.8.4 the LZMA SDK row loses on both speeds at about the same size in the same table (xz -9: 2.75 MB/s compress, 122 MB/s decompress, 23.01%, against lzma -9: 2.55 / 78.2 MB/s, 22.97%); zstd 1.5.7 -18 (4.13 / 1175 MB/s, 25.14%) and brotli 1.2.0 -11 (0.56 / 383 MB/s, 23.78%) decode far faster. Against bzip2 -9 compression is about 5.0x slower (derived from page data). The 7-Zip project makes no numeric speed claim for LZMA: DOC/lzma.txt only says LZMA keeps 'high decompression speed and low memory requirements' and compares to nothing; the numbers come from the third-party lzbench README. The lzbench 'lzma' row is not a 7-Zip release binary: lzbench compiles the SDK's portable C code itself (mk/lzma.mk) and leaves out 7-Zip's x86 assembler LZMA decoder (Asm/x86 LzmaDecOpt, enabled by Z7_LZMA_DEC_OPT in C/LzmaDec.c; DOC/readme.txt says 'if you compile the version with Assembler code, you will get faster 7-Zip binary'), so the decode figures likely understate 7-Zip's own builds, and the row is really an LZMA2 stream (Lzma2Enc_Encode2 / Lzma2DecMt_Decode) fed through memcpy-based stream adapters rather than raw LzmaEnc/LzmaDec on buffers. One corpus (silesia.tar), one machine; the lzbench Makefile compiles everything with -ffast-math (irrelevant for integer codecs but non-default). www.7-zip.org does not resolve from this environment (ENOTFOUND), so the SDK page was not read; the ip7z/7zip repo is the official source home in practice (commits by ip7z are the version snapshots and its releases carry the official 7z2604 binaries and source archives) though its README only says '7-Zip on GitHub' and links 7-zip.org. Licence: DOC/readme.txt says the LZMA SDK 'is written and placed in the public domain by Igor Pavlov' and the file headers of C/LzmaDec.c, C/LzmaEnc.c and C/LzFind.c say 'Igor Pavlov : Public domain' (no patent grant); DOC/License.txt puts the rest of 7-Zip under GNU LGPL 2.1 or later, with BSD 3-clause (LzfseDecoder.cpp, C/ZstdDec.c), BSD 2-clause (C/Xxh64.c) and the unRAR licence restriction on the Rar files, so copy only the public-domain LZMA SDK files. [retier] lzbench lzma row: C decoder only (no Z7_LZMA_DEC_OPT), asm decoder about 1.53x faster per ip7z/7zip issue #11; lzma -9 uses a 256 MB dictionary vs xz -9's 64 MiB; decode timing includes per-call dictionary allocation and 1 MB stream-buffer memcpy; encoder needs about 2.9 GB at -9 and starts a second match-finder thread by default; raw .lzma has no checksum; win over bzip2 is off-baseline.

LZ77 plus range coder aimed at maximum ratio with small decoder memory (lzma.txt: 'maximum increasing of compression ratio, keeping high decompression speed and low memory requirements for decompressing'). Compression is slow (2.55 MB/s at -9 on one thread). Decompression is about twice bzip2's but about a quarter of zlib's: zlib 1.3.2 -9 decodes at 318 MB/s against 78.2 MB/s, so LZMA trades roughly 4x slower decoding for a 28% smaller file than zlib -9 (22.97% against 31.92%, derived from page data). The ANSI-C decoder (C/LzmaDec.c) is small and portable; the SDK encoder is C as well (C/LzmaEnc.c).

## Maintenance

Actively maintained: 7-Zip 26.04 is dated 2026-10-05 in C/7zVersion.h and ip7z/7zip mirrors each release as one commit (4.1k stars, 169 open issues). The LZMA SDK files are public domain and easy to vendor, but the rest of the repository is LGPL-2.1+ with BSD and unRAR parts, so copy only files whose header says 'Public domain'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The lzbench 2.4 README single-thread table has both the 'lzma 26.03' and 'bzip2 1.0.8' rows with exactly the quoted numbers, and states the binary (gcc 15.2.0 release build), options (-eALL -t8,8 -o1c4) and CPU (AMD EPYC 9555P, single thread, turbo off); the benchmark code is public (bench/lz_entropy_codecs.cpp lzbench_lzma_compress/decompress, bench/symmetric_codecs.cpp bzip2) and the flags are in the public Makefile and mk/lzma.mk, consistent with the wave 9 retier-02 treatment of lzbench 2.4 entries.
- **Verifier notes:** All quoted lzbench 2.4 numbers match the README rows exactly (lzma -9 2.55/78.2 MB/s 48,682,482; bzip2 -9 12.7/35.5 MB/s 54,572,811; lzma -0 29.5/62.3 MB/s 60,520,844; bzip2 -1 13.5/41.1 MB/s 60,484,813) and the derived ratios are correct; tier A kept for consistency with the other lzbench 2.4 entries. Shortcomings to record: off-baseline win (bzip2 not in the general-lossless baseline list), slower than the in-list xz 5.8.4 on both speeds at equal size and far slower to decode than zstd/brotli, compression 5x slower than bzip2 -9, no first-party speed claim, lzbench builds the C-only decoder without 7-Zip's assembler LZMA decoder and wraps it as LZMA2 with memcpy stream adapters, one corpus and machine. Not a duplicate: fast-lzma2 (already verified) is a separate LZMA2 encoder, and xz/liblzma is the separate tukaani implementation and a category baseline.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 9); enricher w9 pair-014
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzma.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/bzip2.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/xz.mk>
  - <https://github.com/inikep/lzbench/tree/master/bench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lz_entropy_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/symmetric_codecs.cpp>
  - <https://github.com/ip7z/7zip>
  - <https://github.com/ip7z/7zip/commits>
  - <https://github.com/ip7z/7zip/releases>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/README.md>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/License.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/lzma.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/readme.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaDec.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaEnc.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFind.c>
- **Sources the enricher read:**
  - <https://github.com/ip7z/7zip>
  - <https://github.com/ip7z/7zip/issues>
  - <https://github.com/ip7z/7zip/issues?q=is%3Aissue%20lzma>
  - <https://github.com/ip7z/7zip/issues/11>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/README.md>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/lzma.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/readme.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/License.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/Methods.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/7zC.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/7zFormat.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/DOC/src-history.txt>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaDec.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaDec.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaEnc.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaEnc.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaLib.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzmaLib.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFind.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFind.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFindMt.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFindMt.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/LzFindOpt.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Lzma2Enc.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Lzma2Enc.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Lzma2Dec.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Lzma2DecMt.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Lzma2DecMt.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Compiler.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/CpuArch.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/7zVersion.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/7zTypes.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Threads.h>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/C/Util/Lzma/LzmaUtil.c>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/CPP/7zip/7zip_gcc.mak>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/CPP/7zip/cmpl_gcc_x64.mak>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/CPP/7zip/var_gcc_x64.mak>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/Asm/x86/LzmaDecOpt.asm>
  - <https://raw.githubusercontent.com/ip7z/7zip/HEAD/Asm/arm64/LzmaDecOpt.S>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/lzma.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/xz.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/mk/bzip2.mk>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lz_entropy_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/codecs.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/lzbench.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/bench/symmetric_codecs.cpp>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/xz/src/config.h>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/lz%2Bentropy/xz/src/liblzma/rangecoder/range_decoder.h>
  - <https://raw.githubusercontent.com/tukaani-project/xz/HEAD/src/xz/xz.1>
  - <https://raw.githubusercontent.com/tukaani-project/xz/HEAD/NEWS>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ip7z/7zip`) · [data/wave9/enrich/raw/github_com_ip7z_7zip.json](../../../data/wave9/enrich/raw/github_com_ip7z_7zip.json) (enrichment confidence 0.82)

</details>
