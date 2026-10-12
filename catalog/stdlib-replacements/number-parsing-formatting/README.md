# Number parsing and formatting

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::to_chars, std::from_chars, std::stod, std::format, iostreams  
**22 entries:** 9 tier A · 2 tier B · 11 tier C · 0 tier D · 21 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**{fmt}**](fmtlib-fmt.md) | Type-safe C++ formatting library beating printf/iostreams; its Dragonbox-based float formatter is the speed driver here. | **A** | C++ | MIT | 🟢 active |
| 2 | [**fast_float**](fastfloat-fast-float.md) | Header-only C++ from_chars for float/double/int; 3-5x faster than glibc strtod, exact IEEE rounding. | **A** | C++ | Apache-2.0 OR MIT OR BSL-1.0 | 🟢 active |
| 3 | [**Ryu**](ulfjack-ryu.md) | Shortest round-trip float/double-to-string conversion beating sprintf, plus a faster %f/%e printf replacement. | **A** | C | Apache-2.0 OR BSL-1.0 | 🟢 active |
| 4 | [**simditoa**](simditoa-simditoa.md) | AVX-512 IFMA int64/uint64-to-decimal conversion; 2.8x std::to_chars throughput on 12-19 digit integers, slower at 1-4 digits. | **A** | C++ | MIT OR Apache-2.0 | 🟢 active |
| 5 | [**yy_itoa (itoa_yy.c in ibireme/c_numconv_benchmark)**](ibireme-c-numconv-benchmark.md) | yy_itoa: a 200-byte-table ANSI C integer-to-decimal routine (yyjson's) that formats u32/u64/i32/i64 about 1.7-2.5x faster than fmt's compiled format_to. | **A** | C | MIT | 🟢 active |
| 6 | [**xjb**](xjb714-xjb.md) | Schubfach-derived shortest double/float-to-string converter, about 2.4x faster than Ryu (the algorithm behind std::to_chars) on random doubles. | **A** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**Boost.Charconv**](boostorg-charconv.md) | Portable std::to_chars/from_chars reimplementation for pre-C++17 toolchains and MSVC, winning there and near-parity on GCC. | **A** | C++ | BSL-1.0 | 🟢 active |
| 8 | [**Dragonbox**](jk-jeon-dragonbox.md) | Shortest round-trip double/float-to-decimal conversion, faster than std::to_chars. | **A** | C++ | Apache-2.0 WITH… | 🟡 stale |
| 9 | [**fast_double_parser**](lemire-fast-double-parser.md) | Header-only C++11 double parser using the Eisel-Lemire algorithm; 2.5-9.5x strtod throughput, superseded by fast_float. | **A** | C++ | Apache-2.0 | 🟡 stale |
| 10 | [**google/double-conversion**](google-double-conversion.md) | Grisu3-based double&lt;-&gt;string library extracted from V8; beats sprintf/ostringstream, covers both to_chars- and from_chars-like directions. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 11 | [**fpconv (night-shift)**](night-shift-fpconv.md) | Tiny Grisu2 C library converting doubles to shortest round-trip strings, \~10x faster than std::ostringstream. | **B** | C | BSL-1.0 | 🟡 stale |
| 12 | [**stb_sprintf (nothings/stb)**](nothings-stb.md) | Single-header, public-domain sprintf/snprintf replacement claiming 4-35x faster formatting than MSVC 2008's CRT. | **C** | C | MIT OR Unlicense | 🟢 active |
| 13 | [**musl**](kraj-musl.md) | Small MIT Linux libc; in one zig-built run its atoi (2.3x) and sprintf %f (1.2x) beat glibc, strtod loses 4.3x. | **C** | C | MIT | 🟢 active |
| 14 | [**emio**](viatorus-emio.md) | Header-only C++20 format/scan library for embedded targets; claims integer scanning about 2x sscanf, binary about 38x smaller than {fmt}. | **C** | C++ | MIT | 🟢 active |
| 15 | [**c4core (charconv/xtoa/atox module)**](biojppm-c4core.md) | Low-level C++ utility library whose charconv module (xtoa/atox) beats std::to_chars and std::from_chars on integers. | **C** | C++ | MIT | 🟢 active |
| 16 | [**FastFormat**](synesissoftware-fastformat.md) | Type-safe C++ formatting library (positional fmt and concatenating write) that beats IOStreams and Boost.Format; mixed against printf. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 17 | [**fastcpp::str::parse_u64 / u64_to_chars (developer source)**](private-developer-source-number-parsing-formatting.md) | Header-only uint64 decimal parse (SWAR) and format (two-digit table): \~3x strtoull/snprintf, 1.5x from_chars, 1.2x to_chars. | **C** | C++ | MIT | 🟢 active |
| 18 | [**SSE2 itoa (Muła algorithm, via miloyip/itoa-benchmark)**](miloyip-itoa-benchmark.md) | SSE2-vectorized itoa for uint32/int32/uint64/int64 in Milo Yip's benchmark repo; 25.51x faster than sprintf on 9-10 digit values. | **C** | C++ | MIT | 🟡 stale |
| 19 | [**CharConv.h (rigtorp)**](rigtorp-charconv.md) | Header-only base-10 int32/int64 to/from-string conversion; beats stringstream, to_string, atoi/strtol, stoi. | **C** | C++ | MIT | 🟡 stale |
| 20 | [**milo Grisu2 (header-only, via miloyip/dtoa-benchmark)**](miloyip-dtoa-benchmark.md) | Header-only Grisu2 double-to-string routine; fastest entry in its author's own benchmark, beating std::ostringstream and sprintf(). | **C** | C++ | MIT | 🔴 abandoned |
| 21 | [**jeaiii/itoa**](jeaiii-itoa.md) | Header-only branchless integer-to-ASCII conversion, \~7-9x faster than sprintf/MSVC _itoa, \~1.6-1.8x vs {fmt}. | **C** | C++ | MIT | 🔴 abandoned |
| 22 | [**fast_io**](cppfastio-fast-io.md) | Header-only C++20 I/O library replacing iostream/cstdio and std::to_chars with buffered, syscall-near I/O. | **C** | C++ | Anti-Tivo License (ATL)… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
