# Integer compression and bit-packing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md)</sub>

**What these beat:** varint, Simple8b, FastPFor  
**24 entries:** 2 tier A · 2 tier B · 19 tier C · 1 tier D · 22 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**FastPFor (SIMD-FastPFOR, SIMD-BP128)**](lemire-fastpfor.md) | C++11 library of SIMD integer codecs (SIMD-FastPFOR, SIMD-BP128) decoding 32-bit integer arrays 2-3x faster than Simple-8b and VByte. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**opt_vbyte**](jermp-opt-vbyte.md) | Research code that partitions posting lists into VByte and bitmap blocks, cutting VByte index space 30-47% at equal query speed. | **A** | C++ | MIT | 🔴 abandoned |
| 3 | [**Sprintz**](dblalock-sprintz.md) | Research codec for 8/16-bit multivariate integer time series; beats Simple8b, FastPFor and SIMD-BP128 on ratio at GB/s decode. | **B** | C++ | Apache-2.0 | 🔴 abandoned |
| 4 | [**LeCo (Learn-to-Compress)**](yhliu918-learn-to-compress.md) | Research codec (SIGMOD'24): per-block linear regression plus bit-packed residuals for integer columns; better ratio than FOR and Elias-Fano, faster random access than… | **B** | C++ | no license (study only) | 🟡 stale |
| 5 | [**TurboPFor Integer Compression**](powturbo-turbopfor-integer-compression.md) | GPL C library of SIMD bit packing, PFor, variable-byte and Elias-Fano integer codecs; README tables beat Simple-8b, FastPFor and VByte. | **C** | C | GPL-2.0 | 🟢 active |
| 6 | [**Apache ORC C++ AVX-512 RLE bit-unpacking (ORC-1356)**](apache-orc.md) | Apache ORC's C++ reader with opt-in AVX-512 (and RVV) RLEv2 bit-unpacking, claimed 6-7x over ORC's scalar generic unpacker. | **C** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**JavaFastPFOR**](lemire-javafastpfor.md) | Java integer-array codecs (FastPFOR, binary packing, OptPFD, Simple9) that decode 2.7x-4x faster than VariableByte and Kamikaze PForDelta. | **C** | Java | Apache-2.0 | 🟢 active |
| 8 | [**simdcomp**](lemire-simdcomp.md) | C library for SIMD binary packing of 128-integer blocks (SIMD-BP128); decodes several times faster than Simple-8b and scalar VByte. | **C** | C | BSD-3-Clause | 🟢 active |
| 9 | [**Stream VByte (streamvbyte)**](lemire-streamvbyte.md) | Small C99 library for byte-oriented uint32 compression (SIMD Group Varint variant) that decodes faster than VByte, MaskedVByte and varint-G8IU. | **C** | C | Apache-2.0 | 🟢 active |
| 10 | [**MaskedVByte**](lemire-maskedvbyte.md) | SIMD decoder for standard 32-bit VByte/varint streams; about 1.7-2.2x faster decode than scalar VByte in third-party tables. | **C** | C | Apache-2.0 | 🟢 active |
| 11 | [**zint**](steelcake-zint.md) | Zig FastLanes bitpacking, FOR and delta codecs for u8-u256 arrays; decodes several times faster than lz4 or zstd -1. | **C** | Zig | Apache-2.0 OR MIT | 🟢 active |
| 12 | [**dennwc/varint**](dennwc-varint.md) | Fully unrolled Go LEB128/protobuf varint decoder, roughly 1.3x-2.9x faster per call than encoding/binary.Uvarint on Go 1.17.3. | **C** | Go | MIT | 🟢 active |
| 13 | [**upack (μpack)**](lnx-search-upack.md) | Rust SIMD bitpacking of 128-integer u32/u16 blocks; beats the bitpacking crate's BitPacker4x on x86, loses on ARM. | **C** | Rust | Apache-2.0 | 🟢 active |
| 14 | [**SIMDCompressionAndIntersection**](lemire-simdcompressionandintersection.md) | C++ research library of SIMD codecs (S4-BP128, SIMD-FastPFOR) for sorted uint32 lists, plus SIMD sorted-list intersection. | **C** | C++ | Apache-2.0 | 🟢 active |
| 15 | [**varint-simd**](as-com-varint-simd.md) | Rust crate: branchless SSSE3/BMI2 protobuf-LEB128 varint encode/decode, 2-6x prost and rustc LEB128 on the author's benchmarks. | **C** | Rust | MIT OR Apache-2.0 | 🟡 stale |
| 16 | [**chmike/varint**](chmike-varint.md) | Go prefix-code varint for uint64; about 2x faster than encoding/binary Uvarint for values above 35 bits. | **C** | Go | BSD-3-Clause | 🟡 stale |
| 17 | [**NeaTS**](and-gue-neats.md) | Research C++23 learned compressor for 64-bit integer time series with constant-time random access; paper claims xz-like ratios, faster decompression. | **C** | C++ | GPL-3.0 | 🟡 stale |
| 18 | [**kalcutter/bitshuffle**](kalcutter-bitshuffle.md) | C99 rewrite of the Bitshuffle bit-transpose filter with SSE2/AVX2/AVX-512/GFNI kernels; claims 1.3x-10x over classic bitshuffle. | **C** | C | Apache-2.0 OR MIT | 🟡 stale |
| 19 | [**dictionary (AVX2/AVX-512 fused bit-unpack plus dictionary…**](lemire-dictionary.md) | Research demo that fuses bit-unpacking and dictionary lookup with AVX2/AVX-512 gathers; about 2x its own scalar decoder. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 20 | [**VTEnc**](vteromero-vtenc.md) | C codec for sorted unsigned integer lists that beats Delta+FastPFor on compression ratio, and on speed only for clustered data. | **C** | C | MIT | 🔴 abandoned |
| 21 | [**streamvbyte-simdgo**](thempatel-streamvbyte-simdgo.md) | Go port of Stream VByte with avo-generated AVX/AVX2 assembly; decodes uint32 arrays 8-14x faster than encoding/binary Uvarint loops. | **C** | Go | Apache-2.0 | 🔴 abandoned |
| 22 | [**ledbit/varint (PrefixVarint, leSQLite, leSQLite2 vs LEB128)**](ledbit-varint.md) | Benchmark study of three byte-oriented varint formats (PrefixVarint, leSQLite, leSQLite2) that decode 2-2.9x faster than a naive LEB128 loop. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 23 | [**SFVInt**](paper-sfvint.md) | DaMoN 2024 paper: BMI2 PEXT/PDEP LEB128 varint decoder claiming up to 2x over Folly and Protobuf; no public code. | **C** | C++ | no license (study only) | ⚪ unknown |
| 24 | [**ds2i (Partitioned Elias-Fano and OptPFor indexes)**](ot-ds2i.md) | Research C++ library of compressed posting-list encodings (partitioned Elias-Fano, OptPFD, Varint-G8IU, Interpolative, QMX) for inverted-index query experiments. | **D** | C++ | Apache-2.0 | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
