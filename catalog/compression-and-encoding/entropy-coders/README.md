# Entropy coders

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md)</sub>

**What these beat:** Huffman, rANS baselines the benchmark names  
**26 entries:** 2 tier A · 5 tier B · 19 tier C · 0 tier D · 21 copyable, 5 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**PIVCO-Huffman (pivco-huffman)**](marcinzukowski-pivco-huffman.md) | Block-SIMD Huffman decoder (pivoted coding) that decodes 2-6x faster than zstd's huf0 on most byte distributions. | **A** | C | Apache-2.0 | 🟢 active |
| 2 | [**Glyd**](surya-koritala-glyd.md) | Rust LZ/entropy codec with a C ABI whose blocks decode in parallel; mixed one-core result against zstd -3, wins multicore reads. | **A** | Rust | BSD-3-Clause OR GPL-2.0… (study only) | 🟢 active |
| 3 | [**CUHD / gpuhd (massively parallel Huffman decoding on GPUs)**](weissenberger-gpuhd.md) | CUDA Huffman decoder (CUHD) that splits one unpartitioned bitstream across GPU threads by self-synchronization; reported 10x+ over zstd's CPU huff0. | **B** | CUDA/C++ | LGPL-3.0 | 🔴 abandoned |
| 4 | [**FPC (Fast Prefix Coder)**](kagiannis-fpc.md) | Single-file ISC C Huffman (prefix) coder decoding silesia.tar about 1.25x faster than FSE's Huff0 and 3.7x faster than zlib's Huffman. | **B** | C | ISC | 🔴 abandoned |
| 5 | [**multians (massively parallel ANS decoding on GPUs)**](weissenberger-multians.md) | CUDA research decoder for a single unpartitioned tANS bitstream; paper claims up to 17x over 64 CPU threads. | **B** | CUDA/C++ | LGPL-3.0 | 🔴 abandoned |
| 6 | [**Huffman_coding_Gap_arrays (gap-array GPU Huffman)**](daisuke-takafuji-huffman-coding-gap-arrays.md) | Research CUDA Huffman encoder/decoder (ICPP 2020) whose gap array lets every GPU thread start decoding at a known bit offset. | **B** | CUDA/C | no license (study only) | 🔴 abandoned |
| 7 | [**ipdps22-opthuffdec (optimized GPU Huffman decoders)**](codyjrivera-ipdps22-opthuffdec.md) | IPDPS 2022 artifact: optimized CUDA self-synchronizing and gap-array Huffman decoders, reported 3.64x faster than cuSZ's GPU Huffman decoder. | **B** | CUDA/C++ | no license (study only) | 🔴 abandoned |
| 8 | [**klauspost/compress fse and huff0 packages (Go tANS and…**](klauspost-compress.md) | Pure-Go deflate/gzip/zlib/zip, zstd and S2 packages; deflate about 2x Go stdlib, S2 beats Go Snappy. | **C** | Go | BSD-3-Clause | 🟢 active |
| 9 | [**constriction**](bamler-lab-constriction.md) | Rust/Python rANS and range coders with near-optimal bit rates; decodes 6-14x faster than the arcode arithmetic coder. | **C** | Rust | MIT OR Apache-2.0 OR BSL-1.0 | 🟢 active |
| 10 | [**TurboRC (Turbo Range Coder)**](powturbo-turbo-range-coder.md) | GPL C library of adaptive range coders, adaptive-CDF rANS and a BWT compressor that beats bzip2 on ratio everywhere and on speed on some files. | **C** | C | GPL-3.0 | 🟢 active |
| 11 | [**htscodecs (32-way interleaved SIMD rANS)**](samtools-htscodecs.md) | CRAM 3.1 codec library whose 32-way SIMD rANS decodes about 2.7x faster than its 4-way rANS and 3.8x faster than FSE. | **C** | C | BSD-3-Clause | 🟢 active |
| 12 | [**Recoil (parallel rANS decoding)**](lin-toto-recoil.md) | Header-only C++20 rANS library that splits one interleaved stream for parallel decode on AVX2/AVX-512 CPUs and CUDA GPUs. | **C** | C++ | GPL-3.0 | 🟢 active |
| 13 | [**MANS (Multi-byte ANS compressor)**](hpdps-group-mans.md) | ANS pipeline for 16/32-bit integer arrays on CPU, CUDA and HIP; reports 1.92x/2.04x faster than FSE on CPU. | **C** | C++ | MIT | 🟢 active |
| 14 | [**torch_ans**](worldlife123-torch-ans.md) | PyTorch C++/CUDA extension for batched parallel rANS coding, pitched as a faster replacement for torchac and CompressAI range coding. | **C** | C++ | MIT | 🟢 active |
| 15 | [**RGC (Recursive Group Coding)**](mykola-ponomarenko-ua-rgc.md) | Tiny MIT C entropy coder (Recursive Group Coding) that compresses large-alphabet data better than static AC, claiming about 2x its speed. | **C** | C | MIT | 🟢 active |
| 16 | [**ryg_rans**](rygorous-ryg-rans.md) | Public-domain reference rANS coders in C/C++ headers; interleaved and SSE 4.1 decoders run 1.6-3.7x the scalar decode. | **C** | C++ | CC0-1.0 | 🔵 finished |
| 17 | [**FiniteStateEntropy (FSE and Huff0)**](cyan4973-finitestateentropy.md) | Yann Collet's standalone tANS (FSE) and 4-stream Huffman (Huff0) block coders, the entropy stage later built into zstd. | **C** | C | BSD-2-Clause | 🟡 stale |
| 18 | [**hypersonic-rANS**](rainerzufalldererste-hypersonic-rans.md) | Research C++ rANS codecs with AVX2/AVX-512 decoders reaching about 3 GiB/s, about 3.1x FSE and 1.27x htscodecs. | **C** | C++ | BSD-2-Clause | 🟡 stale |
| 19 | [**DietGPU (GPU rANS codec)**](facebookresearch-dietgpu.md) | CUDA byte-wise rANS encoder/decoder at 250-410 GB/s on A100; open alternative to nvCOMP's proprietary ANS codec. | **C** | C++ | MIT | 🔴 abandoned |
| 20 | [**Turbo-Histogram (TurboHist)**](powturbo-turbo-histogram.md) | Scalar C byte-histogram routines for entropy-coder front ends; 1.5x the naive loop on text, up to 22x on runs. | **C** | C | BSD-2-Clause | 🔴 abandoned |
| 21 | [**sserangecoding (SSE 4.1 interleaved range coder)**](richgel999-sserangecoding.md) | SSE 4.1 16-stream interleaved 24-bit range decoder for order-0 bytes; on book1 it decodes about 1.6x faster than FSE tANS. | **C** | C++ | Unlicense | 🔴 abandoned |
| 22 | [**rans-tricks**](loxxous-rans-tricks.md) | Branchless 16-bit-renormalizing variant of ryg's rans_byte.h; README reports about 1.5-1.7x over standard 4-way interleaved rANS. | **C** | C++ | Public domain (dedication… | 🔴 abandoned |
| 23 | [**length-limited-prefix-codes (modified Kraft)**](stbrumme-length-limited-prefix-codes.md) | Heap-driven Kraft-inequality heuristic for length-limited Huffman code lengths, about 3x faster than Package-Merge at near-optimal size. | **C** | C | Zlib | 🔴 abandoned |
| 24 | [**qbc (Quick adaptive Binary Arithmetic Coder)**](ec-qbc.md) | Tiny adaptive order-0 binary arithmetic coder for short strings, pitched as a replacement for Quake 3's adaptive Huffman Huff_ functions. | **C** | C++ | MIT | 🔴 abandoned |
| 25 | [**rans_static (rANS_static4x16, r32x16b_avx2 SIMD rANS…**](jkbonfield-rans-static.md) | James Bonfield's 2014-2018 static rANS experiments; the 32-way AVX2 decoder runs about 4x faster than the CRAM rANS_static4c codec. | **C** | C | no license (study only) | 🔴 abandoned |
| 26 | [**zune-entropy**](etemesi254-zune-entropy.md) | Rust order-0 Huffman and tANS block coders that out-decode FSE/Huff0 on enwik8 at slightly worse ratio. | **C** | Rust | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
