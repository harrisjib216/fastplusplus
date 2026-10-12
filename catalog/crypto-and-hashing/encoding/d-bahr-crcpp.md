# CRC++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Single-header generic C++ CRC library (any width, 60 catalogue CRCs); roughly ties Boost.CRC in its own 2016 table.

| | |
|---|---|
| **Beats** | Boost.CRC (boost::crc) |
| **Claimed result** | x64: CRC++ 2050 ms vs boost 2250 ms (\~1.10x faster, derived from page data), pycrc 2050 ms (tie), mhash 2250 ms (\~1.10x, derived). x86: CRC++ 2200 ms vs boost 2000 ms (boost \~1.10x faster, derived), pycrc 2240 ms, mhash 2400 ms. README wording: 'one of the fastest and most memory efficient generic CRC implementation available'. |
| **Workload** | README comparison table: wall time in milliseconds for 100 million iterations of a CRC computation on an x64 and an x86 build, against boost, pycrc and mhash; input size, CRC variant and table-versus-bitwise mode are not stated. |
| **Metric** | throughput |
| **Adoption** | 414 stars, 104 forks |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/d-bahr/CRCpp) · [benchmark](https://github.com/d-bahr/CRCpp) |

## Verdict

The README reports 100 million iterations of an unstated CRC computation taking 2050 ms with CRC++ versus 2250 ms with Boost.CRC on x64 (about 1.10x, derived from page data) but 2200 ms versus 2000 ms on x86 (Boost about 1.10x faster), with pycrc and mhash in the same range; no hardware, compiler, flags, input size or benchmark code is given, and the table has not been updated since 2016.

## Use it when

- You need an unusual CRC (CRC-5/USB, CRC-11/NR, CRC-17/CAN, CRC-24/LTE, CRC-40/GSM, custom polynomials) with correct reflect/init/xorout handling and want one header instead of Boost.
- Embedded or legacy C++03 toolchains, or targets where CHAR_BIT is not 8.
- Short messages (packets, frames, records) where a 256-entry table lookup per byte is fast enough and SIMD setup cost would not pay off.
- Incremental CRCs over fragmented buffers (multipart Calculate with the previous crc) or bit-granular inputs (CalculateBits).

## Skip it when

- Bulk CRC-32 or CRC-32C over large buffers: the catalogued SIMD and hardware libraries (crc-fast, corsix fast-crc32, Fast CRC32 slicing-by-16, crc32c with SSE4.2) are many times faster than a byte-wise table.
- Migrating from Boost.CRC for speed: a user reported Boost's crc_optimal about 45% faster than CRC++ for CRC-32C even with CRCPP_USE_CPP11 and CRCPP_BRANCHLESS (issue #8, closed without a reply), and the README's own x86 column has Boost about 10% faster.
- Code pinned to a release before mid-2026 that uses custom reflected parameters with a non-palindromic initial value or continued CalculateBits calls: both returned wrong CRCs until fixes in June and July 2026.
- Compile-time CRCs: tables are built at runtime in Table's constructor (constexpr is only used for small internal constants).

## How it is fast

The table path is the classic one-table-lookup-per-byte Sarwate algorithm with a 256-entry table of CRCType built at runtime when a Table is constructed; the bitwise path keeps the reflected or shifted polynomial out of the inner loop and can be made branchless with CRCPP_BRANCHLESS (one multiply per bit instead of a conditional). There is no slicing-by-N, SIMD, PCLMULQDQ/PMULL folding or hardware CRC32 instruction path, so throughput is in the same class as Boost.CRC's table-driven crc_optimal, not the SIMD CRC libraries.

## Compared with alternatives

Pick CRC++ over crc-fast, corsix fast-crc32, Fast CRC32 or crc32c only when you need arbitrary widths or parameters, C++03 or CHAR_BIT != 8 portability, or a dependency-free header for small messages; for CRC-32/CRC-32C/CRC-64 throughput on x86-64 or aarch64 the SIMD siblings win by an order of magnitude or more.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard headers only); vcpkg and AUR packages exist; CMake INTERFACE target and pkg-config file for installation |
| **Minimum toolchain** | C++03 for the header (C++11 recommended and auto-detected); the CMake target propagates cxx_std_11 and needs CMake 3.14+ |
| **Platforms** | any; portable C++ with no architecture-specific code; MSVC, GCC and Clang project files and CMake |
| **Thread safety** | not documented (issue #20 asked and got no visible answer); the computation functions are stateless, a constructed Table is read-only, and the built-in Parameters are function-local statics whose initialization is thread-safe only under C++11 |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the README comparison table was added in the 2016-05-03 commit 'Added lookup tables' and the repo holds no timing code, CPU, compiler, flags, input size or CRC variant, so even which path (bitwise or table) was timed is unstated; the 10% x64 win is within typical codegen variation and reverses on x86.
- The first README example, CRC::Calculate(data, size, CRC::CRC_32()), is the bit-by-bit path (eight shift/xor steps per byte); you must build a CRC::Table (or MakeTable()) once and reuse it to get table speed, and building one per call costs 256 bitwise byte computations.
- Only 13 CRC definitions are compiled by default; CRC-32C, CRC-64, CRC-16/MODBUS, CRC-16/USB and 43 others need #define CRCPP_INCLUDE_ESOTERIC_CRC_DEFINITIONS before the include.
- Correctness fixes landed recently: 'Fix Issue #23: Reflect initial value when reflectInput is true' (2026-06-18; built-in definitions all have palindromic inits so only custom parameters were affected) and 'Fix CalculateBits continuation overloads discarding previous CRC state' (2026-07-17).

## Known shortcomings

- First-party README table with no CPU, compiler, flags or input size and no timing code in the repo. About 1.10x over boost and mhash on x64, a tie with pycrc, and boost is about 1.10x faster on x86.
- Enricher: the README table dates from the 2016-05-03 'Added lookup tables' commit with no timing code; independent issue #8 reports Boost crc_optimal about 45% faster on CRC-32C; the README's default call is the bit-by-bit path and CRC-32C/CRC-64 need CRCPP_INCLUDE_ESOTERIC_CRC_DEFINITIONS. Correctness fixes landed 2026-06-18 (reflected init, issue #23) and 2026-07-17 (CalculateBits continuation).

## Caveats and trade-offs

First-party table with no CPU, compiler, flags, input size or CRC polynomial, and no benchmark code in the repo (test/src/main.cpp holds unit tests only; no timing code found), so it cannot be reproduced. The win is about 10% on x64 over boost and mhash, a tie with pycrc, and a loss to boost on x86. Baselines are generic CRC libraries; SIMD and hardware-instruction CRC32 libraries (zlib, libdeflate, crc32fast, ISA-L style PCLMUL code) are not compared and are typically much faster on large buffers.

Single header (inc/CRC.h), C++03 or C++11, any CRC width including odd ones, 40+ built-in CRC definitions, bit-by-bit or lookup-table modes, optional branchless bitwise mode, multipart CRCs. The README describes only bitwise and table-driven code; no SIMD or hardware CRC32 path is mentioned.

## Maintenance

Active (version 1.2.3.0 released 2026-08-31, last commit 2026-09-03), BSD-3-Clause and a single header, so trivial to vendor; treat it as a convenience and correctness library rather than a speed upgrade over Boost.CRC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (CRC++ 2050/2200 ms, boost 2250/2000 ms, pycrc 2050/2240 ms, mhash 2250/2400 ms for 100 million iterations on x64/x86) matches the record exactly, but it is first-party with no CPU, compiler, flags, input size or CRC variant, and the repo holds no timing code (test/src contains only main.cpp, a unit test with no clock or timing calls), so it is C.
- **Verifier notes:** Record is accurate: BSD-3-Clause (LICENSE checked), 414 stars, 104 forks, not archived or a fork, last commit 2026-09-03 (active). Shortcomings: unreproducible first-party table with no methodology or benchmark code; win is only about 1.10x over boost and mhash on x64 (derived from page data), a tie with pycrc, and boost is about 1.10x faster on x86; no comparison with SIMD/PCLMUL or hardware CRC32 implementations. A WebSearch found no independent CRC++ vs boost::crc measurement.
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/d-bahr/CRCpp>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/test/src/main.cpp>
  - <https://github.com/d-bahr/CRCpp/tree/master/test/src>
  - <https://github.com/d-bahr/CRCpp/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/inc/CRC.h>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/test/src/main.cpp>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/d-bahr/CRCpp/HEAD/LICENSE>
  - <https://github.com/d-bahr/CRCpp>
  - <https://github.com/d-bahr/CRCpp/issues?q=is%3Aissue>
  - <https://github.com/d-bahr/CRCpp/issues/8>
  - <https://github.com/d-bahr/CRCpp/issues/16>
  - <https://github.com/d-bahr/CRCpp/issues/20>
  - <https://github.com/d-bahr/CRCpp/issues/23>
  - <https://github.com/d-bahr/CRCpp/commits/master>
  - <https://github.com/d-bahr/CRCpp/blame/master/README.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/d-bahr/crcpp`) · [data/wave7/enrich/raw/github_com_d_bahr_crcpp.json](../../../data/wave7/enrich/raw/github_com_d_bahr_crcpp.json) (enrichment confidence 0.75)

</details>
