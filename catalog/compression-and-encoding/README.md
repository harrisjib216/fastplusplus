# Compression and encoding

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Lossless compressors, entropy coders, integer bit-packing and succinct structures that beat zlib, zstd, lz4 and SDSL.

**154 entries in 5 categories:** 38 tier A · 24 tier B · 81 tier C · 11 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Entropy coders](entropy-coders/README.md) | 26 | 2 | 5 | 19 | 0 | Huffman, rANS baselines the benchmark names |
| [Erasure codes](erasure-codes/README.md) | 1 | 0 | 0 | 1 | 0 | CM256 (catid/cm256, O(N^2) Cauchy-matrix MDS Reed-Solomon… |
| [General-purpose lossless compression](general-lossless/README.md) | 73 | 26 | 10 | 31 | 6 | zlib, zstd, lz4, brotli, xz |
| [Integer compression and bit-packing](integer-bitpacking/README.md) | 24 | 2 | 2 | 19 | 1 | varint, Simple8b, FastPFor |
| [Succinct data structures](succinct-structures/README.md) | 30 | 8 | 7 | 11 | 4 | SDSL, sux |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**Snappy**](general-lossless/google-snappy.md) | Google's byte-oriented LZ77 codec: about 5x faster compression and 3x faster decompression than zlib -1, with larger output. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C++ | BSD-3-Clause | 🟢 active |
| 2 | [**Wuffs deflate/zlib/gzip decoder**](general-lossless/google-wuffs.md) | Memory-safe deflate, gzip and zlib decoder shipped as single-file C; 1.2x-1.9x faster than zlib 1.2.11 inflate on 10-100 KB inputs. | [General-purpose lossless compression](general-lossless/README.md) | **A** | Wuffs | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**LZMA (7-Zip LZMA SDK)**](general-lossless/ip7z-7zip.md) | Igor Pavlov's public-domain LZMA/LZMA2 codec behind 7-Zip: 11% smaller than bzip2 -9, 2.2x faster decoding, 5x slower compression. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C | LicenseRef-PublicDomain | 🟢 active |
| 4 | [**bzip3**](general-lossless/kspalaiologos-bzip3.md) | BWT plus context-mixing compressor (bzip2 successor) that compresses text 3-4x faster than xz -9 at slightly smaller size. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C | LGPL-3.0 (bundled… | 🟢 active |
| 5 | [**FastPFor (SIMD-FastPFOR, SIMD-BP128)**](integer-bitpacking/lemire-fastpfor.md) | C++11 library of SIMD integer codecs (SIMD-FastPFOR, SIMD-BP128) decoding 32-bit integer arrays 2-3x faster than Simple-8b and VByte. | [Integer compression and bit-packing](integer-bitpacking/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 6 | [**tsl::htrie_map (hat-trie)**](succinct-structures/tessil-hat-trie.md) | Header-only C++11 HAT-trie string map/set using about 3x less memory than std::unordered_map&lt;std::string, T&gt;. | [Succinct data structures](succinct-structures/README.md) | **A** | C++ | MIT | 🟢 active |
| 7 | [**lz4_flex**](general-lossless/pseitz-lz4-flex.md) | Pure-Rust LZ4 block and frame codec that matches or slightly beats the C reference lz4 when built with its unsafe paths. | [General-purpose lossless compression](general-lossless/README.md) | **A** | Rust | MIT | 🟢 active |
| 8 | [**LZAV**](general-lossless/avaneev-lzav.md) | Single-header C99 LZ77 codec: about 16% smaller output than LZ4/Snappy at Snappy-class compress speed. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C | MIT | 🟢 active |
| 9 | [**FSST (Fast Static Symbol Table)**](general-lossless/cwida-fsst.md) | Symbol-table string compressor with per-string random access; beats LZ4 on ratio and compression speed for short database strings. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C++ | MIT | 🟢 active |
| 10 | [**ZXC**](general-lossless/hellobertrand-zxc.md) | Asymmetric LZ77 codec in C that decodes faster than LZ4, LZ4HC and zstd -1 at equal or smaller output. | [General-purpose lossless compression](general-lossless/README.md) | **A** | C | BSD-3-Clause | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
