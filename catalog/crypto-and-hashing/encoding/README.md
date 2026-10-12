# Encoding (base64, hex, CRC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md)</sub>

**What these beat:** base64, hex, CRC32 baselines the benchmark names  
**26 entries:** 8 tier A · 1 tier B · 17 tier C · 0 tier D · 24 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**aklomp/base64 (SIMD Base64 C99 library)**](aklomp-base64.md) | Portable C99 SIMD base64 codec with runtime CPU dispatch; the Muła–Lemire paper measured its decoder about 4x faster than Chrome's. | **A** | C | BSD-2-Clause | 🟢 active |
| 2 | [**pybase64**](mayeut-pybase64.md) | Python base64 module replacement backed by the SIMD libbase64 codec; roughly 6.6x faster encode than the stdlib. | **A** | Python | BSD-2-Clause | 🟢 active |
| 3 | [**fast-crc32 (corsix) — novel CRC32/CRC32C SIMD kernels**](corsix-fast-crc32.md) | Code generator emitting tuned CRC32/CRC32C C kernels (PCLMUL/VPCLMULQDQ/PMULL plus crc32 instruction) that beat Chromium zlib's SIMD CRC32. | **A** | C | MIT OR Zlib | 🟢 active |
| 4 | [**const-hex**](danipopes-const-hex.md) | Rust hex codec with runtime-dispatched SIMD and const-fn API; near drop-in for `hex`, 6–100x faster on README benches. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 5 | [**GaspardPetit SIMD base64**](gaspardpetit-base64.md) | Small BSD-3 C/C++ Base64 codec with AVX2/NEON kernels; edges out aklomp/base64, simdutf and Turbo-Base64 at 32 KiB. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 6 | [**base64-avx512 (Muła & Lemire)**](wojciechmula-base64-avx512.md) | C artifact of the Muła–Lemire AVX-512 VBMI base64 codec; 10–20x faster than Chrome's table-driven codec. | **A** | C | BSD-3-Clause | 🔴 abandoned |
| 7 | [**crc32c (htot)**](htot-crc32c.md) | C++ port of Intel's 3-way crc32q+pclmulqdq CRC-32C kernel that also runs on 32-bit x86; \~11x faster than slicing-by-8. | **A** | C | BSD-3-Clause… | 🔴 abandoned |
| 8 | [**fastbase64 (lemire)**](lemire-fastbase64.md) | Archived research AVX2 base64 codec from the Muła–Lemire paper; roughly 7-11x faster than Chrome's scalar codec on Skylake. | **A** | C | no license (study only) | 🔴 abandoned |
| 9 | [**Faster Base64 Encoding/Decoding using AVX2 (base64simd)**](wojciechmula-base64simd.md) | Muła's research harness of SSE/AVX2/AVX-512/NEON/RVV base64 kernels; origin of the AVX2 algorithm measured 7-11x faster than Chrome's. | **B** | C++ | BSD-2-Clause | 🟡 stale |
| 10 | [**simdutf Base64 (WHATWG forgiving-base64…**](simdutf-simdutf.md) | SIMD WHATWG forgiving-base64 codec in the simdutf C++ library; its fastbase64 CLI decodes 100 MB 3.5–27x faster than system base64. | **C** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 11 | [**CRC++**](d-bahr-crcpp.md) | Single-header generic C++ CRC library (any width, 60 catalogue CRCs); roughly ties Boost.CRC in its own 2016 table. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 12 | [**Turbo-Base64**](powturbo-turbo-base64.md) | GPL-3 C base64 codec with SSSE3/AVX2/AVX-512 VBMI/Neon kernels; author's tables beat Chrome's codec 7-11x, aklomp 11-70%. | **C** | C | GPL-3.0 | 🟢 active |
| 13 | [**crc32fast (Rust CRC32 SIMD)**](srijs-rust-crc32fast.md) | Rust CRC-32 (IEEE) crate that picks PCLMULQDQ, VPCLMULQDQ or ARMv8 CRC32 kernels at runtime; beats the table-driven `crc` crate. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 14 | [**crc-fast (Rust core, C/C++ compatible) — generic SIMD…**](awesomized-crc-fast-rust.md) | Rust SIMD CRC library with a C ABI, covering every catalogued CRC-16/32/64 variant plus custom parameters; beats table-driven CRC crates. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 15 | [**fast-hex (zbjornson)**](zbjornson-fast-hex.md) | AVX2 hex encoder/decoder for C++ and Node.js, self-reported \~11-12x faster than its own scalar lookup-table codec. | **C** | C++ | MIT | 🟢 active |
| 16 | [**fasthex**](callmealphabet-fasthex.md) | Rust CLI hex dumper that uses multiple threads, SIMD and mmap to dump large files far faster than xxd, hexyl and hexdump. | **C** | Rust | Apache-2.0 | 🟢 active |
| 17 | [**base64-turbo (hacer-bark)**](hacer-bark-base64-turbo.md) | 0BSD Rust base64 crate with AVX2/AVX-512 VBMI/NEON kernels; 2.7-6x the default base64 crate, roughly ties Turbo-Base64. | **C** | Rust | 0BSD | 🟢 active |
| 18 | [**vb64 (Rust std::simd Base64 codec)**](mcy-vb64.md) | Nightly-only std::simd Base64 codec that decodes 2-2.5x faster than the base64 crate on AVX2. It no longer builds. | **C** | Rust | Apache-2.0 | 🟡 stale |
| 19 | [**klauspost/crc32 (2025 AVX-512 revival)**](klauspost-crc32.md) | Fork of Go's hash/crc32 adding an AVX-512 VPCLMULQDQ path that roughly doubles IEEE CRC32 throughput on inputs of 1 KB and up. | **C** | Go | BSD-3-Clause | 🟡 stale |
| 20 | [**Chorba (table-less CRC32)**](samrussell-chorba.md) | Table-less software CRC-32 using sparse zero polynomials; about 2x zlib 1.3.1.1's braided CRC on large buffers. | **C** | C | Zlib | 🟡 stale |
| 21 | [**komrad36/CRC ("Golden" hardware-accelerated CRC32)**](komrad36-crc.md) | x86-64 CRC-32C in one function: three interleaved SSE4.2 crc32 streams recombined with PCLMULQDQ, \~2.9x a single-stream crc32 loop. | **C** | C++ | MIT | 🔴 abandoned |
| 22 | [**Fast CRC32 (Sarwate / Slicing-by-8 / Slicing-by-16)**](stbrumme-crc32.md) | Portable table-driven CRC-32 (zlib polynomial) in C++. Slicing-by-8/16 runs about 3.7-8.5x faster than a byte-wise Sarwate loop. | **C** | C++ | Zlib | 🔴 abandoned |
| 23 | [**sse4_crc32**](anandsuresh-sse4-crc32.md) | Node.js native addon computing CRC-32C with the SSE4.2 crc32 instruction, 2.5-3.7x faster than its own slice-by-8 fallback. | **C** | C++ | MIT | 🔴 abandoned |
| 24 | [**fast-base64 (mitschabaude)**](mitschabaude-fast-base64.md) | Hand-written WebAssembly SIMD base64 codec for JS (browser/Node/Deno); beats pure-JS base64 loops, not native Buffer. | **C** | JavaScript/WebAssembly | MIT | 🔴 abandoned |
| 25 | [**hx (binary-to-hex-simd, NEON table lookup)**](eddieantonio-binary-to-hex-simd.md) | Hobby Rust crate that hex-encodes bytes with an AArch64 NEON tbl lookup in inline asm, \~7.9x its own scalar loop. | **C** | Rust | GPL-3.0 | 🔴 abandoned |
| 26 | [**Faster CRC32 on Apple M1 (dougallj, PMULL multi-chain)**](gist-github-com-dougallj-263f132023f590aec31a11bbc746b897.md) | Single-file C++17 AArch64 CRC-32/CRC-32C kernel with 12 PMULL folding chains; about 2.5x zlib's crc32 on Apple M1. | **C** | C++ | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
