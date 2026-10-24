# General-purpose lossless compression

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md)</sub>

**What these beat:** zlib, zstd, lz4, brotli, xz  
**73 entries:** 26 tier A · 10 tier B · 31 tier C · 6 tier D · 69 copyable, 4 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Snappy**](google-snappy.md) | Google's byte-oriented LZ77 codec: about 5x faster compression and 3x faster decompression than zlib -1, with larger output. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 2 | [**Wuffs deflate/zlib/gzip decoder**](google-wuffs.md) | Memory-safe deflate, gzip and zlib decoder shipped as single-file C; 1.2x-1.9x faster than zlib 1.2.11 inflate on 10-100 KB inputs. | **A** | Wuffs | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**LZMA (7-Zip LZMA SDK)**](ip7z-7zip.md) | Igor Pavlov's public-domain LZMA/LZMA2 codec behind 7-Zip: 11% smaller than bzip2 -9, 2.2x faster decoding, 5x slower compression. | **A** | C | LicenseRef-PublicDomain | 🟢 active |
| 4 | [**bzip3**](kspalaiologos-bzip3.md) | BWT plus context-mixing compressor (bzip2 successor) that compresses text 3-4x faster than xz -9 at slightly smaller size. | **A** | C | LGPL-3.0 (bundled… | 🟢 active |
| 5 | [**lz4_flex**](pseitz-lz4-flex.md) | Pure-Rust LZ4 block and frame codec that matches or slightly beats the C reference lz4 when built with its unsafe paths. | **A** | Rust | MIT | 🟢 active |
| 6 | [**LZAV**](avaneev-lzav.md) | Single-header C99 LZ77 codec: about 16% smaller output than LZ4/Snappy at Snappy-class compress speed. | **A** | C | MIT | 🟢 active |
| 7 | [**FSST (Fast Static Symbol Table)**](cwida-fsst.md) | Symbol-table string compressor with per-string random access; beats LZ4 on ratio and compression speed for short database strings. | **A** | C++ | MIT | 🟢 active |
| 8 | [**ZXC**](hellobertrand-zxc.md) | Asymmetric LZ77 codec in C that decodes faster than LZ4, LZ4HC and zstd -1 at equal or smaller output. | **A** | C | BSD-3-Clause | 🟢 active |
| 9 | [**libbsc**](ilyagrebnov-libbsc.md) | Block-sorting (BWT/ST + LZP + QLFC) compressor library that reaches xz -5 ratios with 5x faster single-thread compression. | **A** | C++ | Apache-2.0 | 🟢 active |
| 10 | [**Fast LZMA2 (fast-lzma2)**](conor42-fast-lzma2.md) | LZMA2 encoder with a radix match finder: 1.3-1.6x faster than xz or the LZMA SDK at matching ratio, multithreaded, standard LZMA2 output. | **A** | C | BSD-3-Clause OR GPL-2.0-only | 🟢 active |
| 11 | [**Kanzi (kanzi-cpp)**](flanglet-kanzi-cpp.md) | Multithreaded BWT/context-mixing/LZ compressor with nine presets; beats xz -9 on compress speed at similar or better ratio. | **A** | C++ | Apache-2.0 | 🟢 active |
| 12 | [**misa77**](welcome-to-the-sunny-side-misa77.md) | LZ77 codec built for decode speed: about 2x LZ4's decompression throughput on Silesia at a better ratio, with slow compression. | **A** | C++ | MIT | 🟢 active |
| 13 | [**lbzip2 (maintained fork)**](caius72-lbzip2.md) | Maintained fork of lbzip2, a parallel bzip2-compatible compressor; single-threaded it already beats bzip2 1.0.8 by about 1.3x to 1.8x. | **A** | C | GPL-3.0-or-later | 🟢 active |
| 14 | [**memlz**](rrrlasse-memlz.md) | Header-only C/C++ word-hash compressor that compresses about 4.8x faster than LZ4 --fast -17 at similar ratio; decompresses slower. | **A** | C | MIT | 🟢 active |
| 15 | [**libslz (SLZ)**](wtarreau-libslz.md) | Stateless deflate/zlib/gzip compressor in C, about 3.5x faster than zlib -1 at a much lower ratio. | **A** | C | X11 | 🟢 active |
| 16 | [**liblzraven**](anat0m1a-liblzraven.md) | Clean-room C11 codec for Apple's LZRAVEN format (LZMA-class model, adaptive rANS); decodes about 1.7-2x faster than xz -6. | **A** | C | 0BSD | 🟢 active |
| 17 | [**lzvolt**](macstab-lzvolt.md) | LZ77 codec for small cache/record values whose hand-written per-CPU decoders read 14-83% faster than liblz4. | **A** | Rust | Apache-2.0 | 🟢 active |
| 18 | [**Density (density-rs)**](g1mv-density.md) | Pure-Rust block compressor using 4-byte hashed dictionary units; compresses faster than LZ4 at matching ratios, decompresses slower. | **A** | Rust | MIT OR Apache-2.0 | 🟡 stale |
| 19 | [**FastLZ**](ariya-fastlz.md) | Two-file ANSI C byte-aligned LZ77 block compressor; about 3x zlib -1 compression speed and 2x decompression, at a worse ratio. | **A** | C | MIT | 🟡 stale |
| 20 | [**BriefLZ**](jibsen-brieflz.md) | Tiny C LZ77 compressor with gamma-coded lengths/offsets; at -6 it matches zlib -9's ratio with about 2x faster compression. | **A** | C | Zlib | 🟡 stale |
| 21 | [**LZFSE (Apple reference implementation)**](lzfse-lzfse.md) | Apple's LZ77 + finite-state-entropy codec in plain C99; zlib -6 ratio at about 3.4x the compress and 2.3x the decompress speed. | **A** | C | BSD-3-Clause | 🔴 abandoned |
| 22 | [**LZHAM (lzham_codec)**](richgel999-lzham-codec.md) | Asymmetric LZ77 codec with near-LZMA ratio whose decoder runs about 3.5x faster than 7-Zip LZMA; compression is slow. | **A** | C++ | Public domain (LICENSE… | 🔴 abandoned |
| 23 | [**LZSSE**](conorstokes-lzsse.md) | LZSS codec whose format is built for branchless SSE4.1 decoding; decodes about 1.3x faster than LZ4HC at similar ratio. | **A** | C++ | BSD-2-Clause | 🔴 abandoned |
| 24 | [**libzling**](richox-libzling.md) | Small C++ ROLZ + Huffman compressor (Baidu, archived) that compresses about 3x faster than zlib -6 with a better ratio. | **A** | C++ | BSD-3-Clause | 🔴 abandoned |
| 25 | [**LZO (lzo1x)**](nemequ-lzo.md) | LZO1X-1: byte-aligned LZ77 block codec; 5.6x faster compression, 1.9x faster decompression than zlib -1, 30% larger output. | **A** | C | GPL-2.0-or-later | 🔴 abandoned |
| 26 | [**libbzip2 (bzip2)**](gitlab-com-bzip2-bzip2.md) | Reference bzip2/libbz2: Burrows-Wheeler compressor whose decoder is 2.5-14x faster than PPMd at a similar ratio, but slow by modern standards. | **A** | C | bzip2-1.0.6 (the 'bzip2 and… (study only) | 🔴 abandoned |
| 27 | [**Zstandard (zstd)**](facebook-zstd.md) | General-purpose lossless compressor beating zlib/deflate on speed and ratio, with tunable levels and negative fast modes. | **B** | C | BSD-3-Clause OR GPL-2.0-only | 🟢 active |
| 28 | [**LZ4**](lz4-lz4.md) | In-memory block/frame compressor beating zlib deflate on speed, trading compression ratio for GB/s decode. | **B** | C | BSD-2-Clause | 🟢 active |
| 29 | [**zlib-ng**](zlib-ng-zlib-ng.md) | Maintained zlib fork with SIMD deflate, inflate and CRC32/Adler32; about 2.2-2.5x faster compression and 1.5x faster decompression than zlib. | **B** | C | Zlib | 🟢 active |
| 30 | [**ISA-L (igzip)**](intel-isa-l.md) | Intel's assembly-tuned deflate/gzip/zlib codec (igzip): about 4.8x zlib -1 compression speed and 2.3x its decompression speed. | **B** | C | BSD-3-Clause | 🟢 active |
| 31 | [**Cloudflare zlib fork**](cloudflare-zlib.md) | Deprecated Cloudflare fork of zlib 1.2.8 with SSE4.2/NEON hashing and SIMD checksums; about 4x faster deflate than stock zlib. | **B** | C | Zlib | 🟢 active |
| 32 | [**Rapidgzip**](mxmlnkn-rapidgzip.md) | Parallel decompressor and random-access reader for ordinary gzip files; 7-20x faster than GNU gzip on 12 cores. | **B** | C++ | Apache-2.0 AND MIT (repo… | 🟢 active |
| 33 | [**fdeflate**](image-rs-fdeflate.md) | Safe-Rust zlib/deflate codec tuned for PNG data; decoder claimed on par with zlib-ng and zlib-rs, encoder still preliminary. | **B** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 34 | [**pigz**](madler-pigz.md) | Multithreaded gzip/zlib/zip compressor by zlib's co-author; beats single-threaded GNU gzip on multicore machines. | **B** | C | Zlib | 🔴 abandoned |
| 35 | [**jtkukunas/zlib (Intel zlib fork)**](jtkukunas-zlib.md) | Archived Intel fork of zlib with SSE4.2 hashing and new quick/medium deflate strategies; about 1.8x stock zlib at mid levels. | **B** | C | Zlib | 🔴 abandoned |
| 36 | [**pugz**](piezoid-pugz.md) | Research prototype that decompresses one gzip stream of ASCII text on many threads; beats single-threaded GNU gunzip and libdeflate. | **B** | C++ | MIT | 🔴 abandoned |
| 37 | [**Chromium zlib (third_party/zlib fork)**](chromium-chromium.md) | Chromium's zlib fork with SIMD CRC-32, Adler-32, chunk-copy inflate and a faster deflate hash; API-compatible, faster than madler/zlib. | **C** | C | Zlib | 🟢 active |
| 38 | [**OpenZL**](facebook-openzl.md) | Meta's graph-of-codecs compression framework: format-aware compressors for structured data plus a native LZ that decodes about 2.3x faster than zstd -1. | **C** | C / C++ | BSD-3-Clause | 🟢 active |
| 39 | [**fflate**](101arrowz-fflate.md) | Pure-JavaScript DEFLATE/gzip/zlib/ZIP codec, up to 25% faster decode and 50% faster encode than pako. | **C** | TypeScript | MIT | 🟢 active |
| 40 | [**libdeflate**](ebiggers-libdeflate.md) | Whole-buffer DEFLATE/zlib/gzip C library: about 2.6x zlib's decompression speed and 3.3x its level-6 compression, plus faster CRC-32. | **C** | C | MIT | 🟢 active |
| 41 | [**rust-brotli (Dropbox Rust port of Brotli)**](dropbox-rust-brotli.md) | Safe, no_std-capable Rust port of Google's Brotli encoder and decoder; slower than the C reference, not faster. | **C** | Rust | BSD-3-Clause AND MIT | 🟢 active |
| 42 | [**orz**](richox-orz.md) | Rust ROLZ compressor: near-xz -6 ratio on enwik8 text with about 13x faster single-threaded encode; decode slower than zstd. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 43 | [**Efficient Compression Tool (ECT)**](fhanau-efficient-compression-tool.md) | Command-line PNG/JPEG/gzip/ZIP optimizer whose modified-zopfli deflate matches zopfli -i30 output size about 15x faster. | **C** | C++ | Apache-2.0 | 🟢 active |
| 44 | [**Lizard**](inikep-lizard.md) | LZ4-derived C codec (formerly LZ5) with optional Huffman; decompresses 4-5x faster than zlib -9 at similar ratio. | **C** | C | BSD-2-Clause | 🟢 active |
| 45 | [**lrzip**](ckolivas-lrzip.md) | Command-line compressor that removes long-distance duplicates (rzip) before multithreaded LZMA; beats xz/7z on large redundant files. | **C** | C | GPL-2.0 | 🟢 active |
| 46 | [**c-blosc2 (Blosc2 shuffle+lz4)**](blosc-c-blosc2.md) | Blocked, multithreaded meta-compressor (shuffle/bitshuffle filters plus LZ4, Zstd, zlib or BloscLZ) for typed binary arrays; outruns memcpy on compressible data. | **C** | C | BSD-3-Clause | 🟢 active |
| 47 | [**ZipNN (Huffman-based lossless compression of AI model…**](zipnn-zipnn.md) | Lossless compressor for floating-point model weights; byte grouping plus Huffman beats plain zstd on bfloat16 speed and ratio. | **C** | Python | MIT | 🟢 active |
| 48 | [**TurboRLE (TRLE and SRLE)**](powturbo-turborle.md) | Block run-length encoder (TRLE, plus escape-based SRLE for 8/16/32/64-bit runs) that out-compresses and out-runs rle8 and Mespotine RLE. | **C** | C | GPL-2.0-or-later | 🟢 active |
| 49 | [**Zippy (Nim deflate/zlib/gzip)**](guzba-zippy.md) | Pure-Nim deflate/zlib/gzip codec (plus zip and tar readers) that the author times as faster than zlib on small files. | **C** | Nim | MIT | 🟢 active |
| 50 | [**MinLZ**](minio-minlz.md) | Go LZ77 compressor (new byte-aligned format, Snappy/S2 successor) that compresses faster and smaller than LZ4's fastest mode. | **C** | Go | Apache-2.0 | 🟢 active |
| 51 | [**Stenos**](thermadiag-stenos.md) | C/C++ compressor for arrays of fixed-size numeric elements that picks its own filter; claims better ratio and speed than Blosc2+Zstd. | **C** | C++ | MIT | 🟢 active |
| 52 | [**pigzpp**](thammegowda-pigzpp.md) | C++23 rewrite of pigz as a thread-safe library and CLI on ISA-L/zlib-ng; 2.1x to 8.5x pigz compression throughput. | **C** | C++ | Zlib | 🟢 active |
| 53 | [**ACEAPEX**](yasha1971-coder-aceapex.md) | Block-independent LZ77 with zstd-coded token streams; decodes in parallel on CPU/GPU and supports random-access reads, aimed at genomic archives. | **C** | C++ | MIT | 🟢 active |
| 54 | [**pixz**](vasi-pixz.md) | Parallel, block-indexed xz compressor CLI; roughly ties multi-threaded xz on speed, adds random access into .tpxz tarballs. | **C** | C | BSD-2-Clause | 🟡 stale |
| 55 | [**blz4**](jibsen-blz4.md) | Experimental LZ4 legacy-format encoder using BriefLZ's optimal parser; output matches lz4 -12 or is a few bytes smaller, at much lower speed. | **C** | C | Zlib | 🟡 stale |
| 56 | [**bzip2gpu (weissenberger)**](weissenberger-bzip2gpu.md) | Research CUDA decompressor for standard .bz2 streams that runs every stage except parsing on the GPU; reported faster than multicore CPU bzip2. | **C** | CUDA C++ | MIT | 🟡 stale |
| 57 | [**LZSA**](emmanuel-marty-lzsa.md) | Byte-aligned LZ formats with an optimal packer: better ratio than LZ4_HC, and decompression as fast as LZ4 on 8-bit CPUs. | **C** | C | Zlib | 🔴 abandoned |
| 58 | [**fast_zlib**](gildor2-fast-zlib.md) | Drop-in replacement for zlib's longest_match() that makes level 6-9 deflate about 2.5-10x faster on the author's data, output still standard deflate. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 59 | [**Gipfeli**](google-gipfeli.md) | Archived Google LZ77 compressor with a light static entropy stage, claimed about 5x faster than zlib. | **C** | C++ | BSD-3-Clause | 🔴 abandoned |
| 60 | [**em_inflate**](emmanuel-marty-em-inflate.md) | Single-file, one-call memory-to-memory inflate for zlib, gzip and raw deflate; 11-16% faster than zlib 1.2.11 with checksums on. | **C** | C | Zlib | 🔴 abandoned |
| 61 | [**lz4ultra**](emmanuel-marty-lz4ultra.md) | Offline optimal-parse LZ4 encoder whose standard LZ4 output decodes 1.45-1.54x faster than lz4 -12 output on enwik9. | **C** | C | Zlib (src/matchfinder.c is… | 🔴 abandoned |
| 62 | [**smallz4**](stbrumme-smallz4.md) | Small C++ optimal-parse LZ4 encoder: standard .lz4 output about 0.2-0.9% smaller than lz4 -9/-12, but slower to compress. | **C** | C++ | MIT | 🔴 abandoned |
| 63 | [**Inflate++ (inflatecpp)**](artexety-inflatecpp.md) | Small C++ one-shot zlib/gzip/raw-deflate decoder; a port of em_inflate, about 1.1-1.3x faster than zlib 1.2.11 inflate. | **C** | C++ | MIT | 🔴 abandoned |
| 64 | [**LZMAT**](nemequ-lzmat.md) | Abandoned 2008 nibble-packed LZ77 codec; decompresses about 1.2x faster than zlib at zlib -1 ratio, compresses 3x slower. | **C** | C | GPL-2.0-or-later | 🔴 abandoned |
| 65 | [**matbech/zlib (optimized zlib 1.2.11 fork, MSVC)**](matbech-zlib.md) | Archived Windows/MSVC zlib fork with SIMD hashing, CRC and match patches; about 1.3-1.9x zlib 1.2.11 level-6 compression. | **C** | C | Zlib | 🔴 abandoned |
| 66 | [**AOCL-Compression**](amd-aocl-compression.md) | AMD's Zen-tuned forks of zlib, zstd, lz4, snappy, bzip2 and lzma behind one C API; level-9 zlib compresses about 3.7x faster. | **C** | C | BSD-3-Clause AND MIT AND… (study only) | 🟢 active |
| 67 | [**Firetrail (formerly skim)**](vantorrewannes-firetrail.md) | Zig word-hash codec (Density-style) that encodes faster than lz4 --fast=20 and zstd --fast=5, at a lower ratio. | **C** | Zig | no license (study only) | 🟢 active |
| 68 | [**miniz**](richgel999-miniz.md) | Single-file MIT zlib/Deflate replacement with ZIP and PNG helpers; measured slower than zlib, chosen for portability, not speed. | **D** | C | MIT | 🟢 active |
| 69 | [**Blosc (c-blosc)**](blosc-c-blosc.md) | Blocked, multithreaded meta-compressor (shuffle/bitshuffle plus BloscLZ, LZ4, Zstd, zlib) for typed numeric arrays; can outrun memcpy on compressible data. | **D** | C | BSD-3-Clause | 🟢 active |
| 70 | [**Intel QPL (IAA hardware deflate path)**](intel-qpl.md) | Intel's C library that offloads Deflate (4 KB window) to the IAA accelerator on Sapphire Rapids Xeons, beating Snappy, zstd and zlib-ng in database pipelines. | **D** | C++ | MIT | 🟢 active |
| 71 | [**mmx sdefl/sinfl (single-header deflate)**](vurtun-lib.md) | Two tiny single-header C files for raw deflate and zlib: compressor about 1.8x zlib 1.2.11, decoder 1.2-1.4x (first-party). | **D** | C | MIT OR Unlicense | 🟡 stale |
| 72 | [**libzbitmap**](eafer-libzbitmap.md) | Clean-room C reimplementation of Apple's closed LZBITMAP codec; format compatibility only, self-described as much slower than Apple's. | **D** | C | MIT | 🔴 abandoned |
| 73 | [**DeLZSA (ivagorRetrocomp)**](ivagorretrocomp-delzsa.md) | Intel 8080 and PDP-11 assembly decompressors for the LZSA1/LZSA2 formats; code no longer publicly reachable, no speed figures. | **D** | Assembly | no license (study only) | ⚪ unknown |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
