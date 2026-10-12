# Unicode and UTF-8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** ICU, std::codecvt, simdutf as incumbent-fast  
**23 entries:** 7 tier A · 0 tier B · 14 tier C · 2 tier D · 22 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**utf8_range (SIMD Range-based UTF-8 validator)**](protocolbuffers-protobuf.md) | SIMD range-based UTF-8 validator bundled in protobuf; edges out Lemire's SSE/NEON validator, mostly on ARM. | **A** | C | MIT | 🟢 active |
| 2 | [**simdutf8**](rusticstuff-simdutf8.md) | SIMD-accelerated UTF-8 validator for Rust, a drop-in replacement for std::str::from_utf8, up to 23x faster. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**unicode-segmenter**](cometkim-unicode-segmenter.md) | Zero-dependency JavaScript UAX #29 grapheme segmenter, about 2x faster than built-in Intl.Segmenter on Node and Bun. | **A** | JavaScript | MIT | 🟢 active |
| 4 | [**ada-url/idna**](ada-url-idna.md) | C++20 IDNA to_ascii/to_unicode (UTS #46) domain-name encoder, about 1.26x faster than ICU. | **A** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 5 | [**SimdUnicode**](simdutf-simdunicode.md) | Drop-in faster UTF-8 validator for .NET, beating the runtime's private SIMD validator on non-ASCII text. | **A** | C# | MIT | 🟢 active |
| 6 | [**xutf**](can1357-xutf.md) | SIMD Rust UTF-8/16/32 transcoder beating simdutf on most inputs, plus allocation-free grapheme/width/wrap terminal-text primitives. | **A** | Rust | MIT | 🟢 active |
| 7 | [**go-simd/utf8**](go-simd-utf8.md) | Pure-Go SIMD UTF-8 validator and rune counter, byte-identical to unicode/utf8, faster on non-ASCII text. | **A** | Go | BSD-3-Clause | 🟢 active |
| 8 | [**ICU4X**](unicode-org-icu4x.md) | Unicode Consortium's Rust rewrite of ICU; a 2023 first-party post says its line and word segmenters beat ICU4C's break iterators by 19-52%. | **C** | Rust | Unicode-3.0 | 🟢 active |
| 9 | [**encoding_rs**](hsivonen-encoding-rs.md) | Rust implementation of the WHATWG Encoding Standard; beats ICU at UTF-8/UTF-16/legacy transcoding on Web-shaped text. | **C** | Rust | (Apache-2.0 OR MIT) AND… | 🟢 active |
| 10 | [**uax29 (graphemes and words)**](clipperhouse-uax29.md) | Zero-allocation Go UAX #29 grapheme/word/sentence segmenter (Unicode 17); 14x rivo/uniseg graphemes, 3.6x blevesearch/segment words, first-party. | **C** | Go | MIT | 🟢 active |
| 11 | [**unicode-transforms**](composewell-unicode-transforms.md) | Pure-Haskell Unicode NFC/NFKC/NFD/NFKD normalization for Text, beating ICU's C library binding on decomposition forms. | **C** | Haskell | BSD-3-Clause | 🟢 active |
| 12 | [**xxUTF**](dzfrias-xxutf.md) | Allocation-free C library for Unicode NFD/NFC/NFKD/NFKC and case folding; ARM NEON NFD runs about 3-4.5x ICU4C on non-ASCII UTF-8. | **C** | C | MIT | 🟢 active |
| 13 | [**fast-grapheme-segmenter**](cometkim-fast-grapheme-segmenter.md) | Forward-only Rust UAX #29 grapheme segmenter: 1.3-2.1x faster than ICU4X's icu_segmenter at splitting, 2.7-36x at counting. | **C** | Rust | MIT | 🟢 active |
| 14 | [**libidn**](gitlab-com-libidn-libidn.md) | GNU C library for IDNA2003, Stringprep and Punycode. One Ruby benchmark shows it \~1.47x faster than libidn2. | **C** | C | LGPL-3.0-or-later OR… | 🟢 active |
| 15 | [**libutf**](brazilofmux-utf.md) | Small malloc-free C11 library for NFC, DUCET collation and grapheme clusters on raw UTF-8; first-party numbers beat ICU on short strings. | **C** | C | MIT | 🟢 active |
| 16 | [**Boost.Text (tzlaine/text)**](tzlaine-text.md) | Boost-style C++ Unicode library (transcoding, normalization, text types) faster than ICU only in narrow, now-degraded cases. | **C** | C++ | BSL-1.0 | 🟡 stale |
| 17 | [**uni-algo**](uni-algo-uni-algo.md) | Header-only C++17 Unicode library (UTF conversion, case, normalization, UAX #29 segmentation); its grapheme iteration runs 2.7-3.0x faster than ICU's. | **C** | C++ | MIT OR Unlicense… | 🟡 stale |
| 18 | [**fastvalidate-utf-8**](lemire-fastvalidate-utf-8.md) | Header-only C99 SSE/AVX2 UTF-8 validator (2018) that validates at 0.45-0.7 cycles/byte versus about 11 for a branchy scalar loop. | **C** | C | Apache-2.0 OR BSL-1.0 OR MIT | 🟡 stale |
| 19 | [**ugrapheme**](z4jc-ugrapheme.md) | Cython UAX #29 grapheme splitter for CPython; about 8x faster than ICU's BreakIterator driven through PyICU on a short string. | **C** | Cython | 0BSD | 🟡 stale |
| 20 | [**utf8lut**](stgatilov-utf8lut.md) | SSSE3 lookup-table UTF-8/UTF-16/UTF-32 transcoder, 7-13x faster than its own Hoehrmann-DFA scalar path on BMP-heavy text. | **C** | C++ | BSL-1.0 | 🔴 abandoned |
| 21 | [**Parabix (bitstream UTF-16 validation kernel)**](parabix-parabix-devel-mirror.md) | Bitstream-parallel text-processing framework whose LLVM-JIT'd SIMD kernel beat a simdutf CLI wrapper on UTF-16 validation. | **C** | C++ | OSL-3.0 (study only) | 🔴 abandoned |
| 22 | [**ICU (ICU4C collation)**](unicode-org-icu.md) | ICU4C's RuleBasedCollator: locale-aware UCA/CLDR string comparison and sort keys, charted by its authors as faster than glibc strcoll. | **D** | C++ | Unicode-3.0 | 🟢 active |
| 23 | [**libgrapheme**](frign-libgrapheme.md) | Tiny freestanding C99 Unicode segmentation and case-mapping library; claims to beat libutf8proc, ICU and libunistring, with no published numbers. | **D** | C | ISC | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
