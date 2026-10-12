# Fast CRC32 (Sarwate / Slicing-by-8 / Slicing-by-16)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🔴 abandoned

> Portable table-driven CRC-32 (zlib polynomial) in C++. Slicing-by-8/16 runs about 3.7-8.5x faster than a byte-wise Sarwate loop.

| | |
|---|---|
| **Beats** | Classic byte-wise Sarwate table-lookup CRC32 (the author's own crc32_1byte reimplementation). The page says zlib and PHP use this algorithm, but zlib's crc32() itself is not benchmarked. |
| **Claimed result** | Core i7 860, CRC32 of 1 GByte, figures given as GCC 4.7 / Visual C++ 2010: Slicing-by-8 1800 / 1400 MByte/s; Slicing-by-16 3000 / 2000 MByte/s; Slicing-by-16 4x unrolled with prefetch 3200 / 2000 MByte/s; Slicing-by-4 1050 / 840 MByte/s. The standard Sarwate byte-table implementation runs at 375 MByte/s, so Slicing-by-8 and Slicing-by-16 are about 3.7-8.5x faster than it, and Slicing-by-4 about 2.2-2.8x (derived from page data). The original bitwise version runs at 35 MByte/s. |
| **Workload** | CRC32 checksum of a 1 GiB in-memory buffer, single-threaded, x86-64 desktop |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 860 (2.8 GHz, Turbo Boost 3.2 GHz) |
| **Compiler and flags** | GCC 4.7 and Visual C++ 2010. For VC++ the page only says 'full optimization is enabled', and it mentions that GCC -O2 and up unrolls the loop. Exact flags for the published table are not stated. The repo Makefile, added in 2016 after the measurements, uses -O3 -Wall -Wextra -pedantic -s. |
| **Adoption** | 194 stars |
| **Last commit** | 2021-09-29 |
| **Links** | [repository](https://github.com/stbrumme/crc32) · [benchmark](https://create.stephan-brumme.com/crc32/) |

## Verdict

The author's blog table times CRC-32 over a 1 GiB buffer on a Core i7 860 (2.8/3.2 GHz) with GCC 4.7 and Visual C++ 2010 (exact flags not stated): 1,800/1,400 MB/s for slicing-by-8, 3,000/2,000 for slicing-by-16 and 3,200/2,000 with prefetch. The reference is his own byte-wise Sarwate loop at 375 MB/s, about 3.7-8.5x (derived). zlib's actual crc32() was never benchmarked.

## Use it when

- Portable software CRC-32 (zlib/PNG/gzip-compatible) with no intrinsics, assembler or SIMD, on any ISA including big-endian, when PCLMULQDQ/ARMv8-CRC code paths are unavailable or not allowed
- Embedded or memory-tight targets where you trade table size for speed: half-byte needs 64 bytes of table, Sarwate 1 KB, slicing-by-4/8/16 4/8/16 KB; there are Arduino sketches and blog cycle counts for the ATmega
- Replacing a hand-rolled byte-wise CRC loop in legacy C++: slicing-by-16 was about 8x faster on a 2010-era x86 desktop (375 MB/s to 3,000 MB/s with GCC 4.7)
- Chunked or multi-threaded CRC of large buffers, using crc32_combine() to merge per-chunk CRCs (the repo includes a std::thread example)
- Learning or teaching CRC implementation tradeoffs: the blog documents each algorithm step by step with code and measurements

## Skip it when

- Modern x86-64 or ARMv8 servers and desktops: carry-less-multiply or hardware CRC libraries (crc32fast pclmulqdq, corsix fast-crc32, zlib-ng, Chromium zlib) run many times faster, and this library has no hardware path at all
- As a claimed upgrade over zlib's crc32(): zlib has used a four-bytes-at-a-time (BYFOUR) loop since 1.2.0 (2003) and braided CRC since 1.2.12 (2022, '1.5 to 3' times faster per its ChangeLog). The page's 'zlib' baseline is really a Sarwate loop, and no comparison against actual zlib exists
- CRC-32C (Castagnoli, iSCSI/ext4/SSE4.2) or any other polynomial: the tables are hard-coded for 0xEDB88320
- Small-core ARM without verification: a user's Raspberry Pi 2 (ARMv7) run in issue #16 measured 101 MB/s for Sarwate vs only 172-218 MB/s for the slicing variants (about 1.7-2.2x), and slicing-by-16 without prefetch was slower than slicing-by-8 there
- Projects that need an actively maintained dependency: no commits since 2021-09-29, and seven issues/PRs are open without response, including build and portability fixes

## How it is fast

Slicing-by-N (Intel's slicing-by-8 generalized to 16 by Bulat Ziganshin) replaces Sarwate's one serial table lookup per byte with N independent lookups into N precomputed 256-entry tables per 4/8/16-byte word. That breaks the byte-to-byte dependency chain, so the CPU can issue the loads in parallel: about 1-1.5 cycles/byte vs about 8 for Sarwate on a Core i7 860. The slicing-by-16 loop is unrolled 4x, and a variant issues __builtin_prefetch/_mm_prefetch 256 bytes ahead, which the page credits with a little under 10% on that CPU. The tables are compile-time constants (up to 16 KB), so there is no runtime initialization.

## Compared with alternatives

Pick it over crc32fast, corsix fast-crc32, komrad36/CRC or the dougallj PMULL kernel only when you need plain portable C++ with no SIMD or hardware dependency, or a tiny-table variant for microcontrollers. Chorba is the newer table-less software alternative that beats zlib's braided CRC. htot/crc32c computes the different CRC-32C polynomial.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdint.h, cstddef; sys/param.h on non-Windows for __BYTE_ORDER; xmmintrin.h for prefetch under MSVC with SSE2) |
| **Minimum toolchain** | Any C++ compiler for the library, which uses no C++11 features in Crc32.cpp (default arguments and &lt;cstddef&gt; make it C++-only). Measured with GCC 4.7 and Visual C++ 2010; the multithreaded test needs C++11 (std::thread, auto) |
| **Platforms** | any; little- and big-endian paths for slicing-by-4/8/16; Windows ARM64 fixed in 2021; Arduino sketch ports; no SIMD or hardware-CRC path on any architecture |
| **Thread safety** | Not documented explicitly; all functions are pure and the lookup tables are static const, so concurrent calls are safe. The README advertises multi-threaded computation via crc32_combine() |
| **Drop-in for the baseline** | partial — produces the same CRC-32 values as zlib's crc32() and a byte-wise Sarwate loop, and chains through previousCrc32, but argument order differs (data, length, previousCrc vs zlib's crc, buf, len) and the header has no extern "C" (the PR adding it was closed unmerged) |

## Gotchas

- The slicing functions cast the void\* input straight to const uint32_t\* with no alignment prologue. Misaligned buffers (for example from chunked processing) rely on the CPU tolerating unaligned loads, which is UB in C++ and can fault on strict-alignment cores; the author only warns that 'performance might suffer'
- Non-Windows builds need __BYTE_ORDER from &lt;sys/param.h&gt; or stop with #error; an open 2022 PR reports macOS failing this way and proposes falling back to __BYTE_ORDER__
- Crc32.h itself #defines all four CRC32_USE_LOOKUP_TABLE_\* switches, so shrinking the 16 KB table for embedded use means editing the header, not passing -U flags
- crc32_combine() uses the older pigz/zlib GF(2) matrix-squaring method on every call; zlib 1.2.12 made combines about 200x faster with precomputed tables. The bundled Crc32Test allocates 1 GiB and throws std::bad_alloc on 32-bit boards (issue #16)

## Known shortcomings

- Baseline is the author's own bytewise Sarwate loop, not zlib's crc32() (which has used slicing since 1.2.0 in 2003 and braiding since 1.2.12), so the 3.7-8.5x does not apply against zlib. Table predates the Makefile's -O3 (added 2016); flags unstated. Abandoned since 2021-09-29; hardware CRC (SSE4.2/PCLMUL) implementations are much faster.
- Unaligned uint32_t\* casts (UB; faults on strict-alignment cores); `__BYTE_ORDER` #error on macOS (PR #12 open); no extern "C". On a Pi 2 (ARMv7) only 1.7-2.2x over bytewise, and slicing-by-16 without prefetch is slower than slicing-by-8. 7 issues/PRs unanswered; the test allocates 1 GiB (bad_alloc on 32-bit).

## Caveats and trade-offs

The baseline is a textbook Sarwate byte-table loop, not real zlib. zlib's crc32() has processed four bytes at a time since 1.2.0 in 2003 (the BYFOUR code from Rodney Brown, similar to slicing-by-4, which this page measures at 840-1050 MByte/s). Since 1.2.12 in 2022 zlib uses braided CRC, which its ChangeLog says is 1.5-3x faster again. The speedup over an actual zlib build is therefore much smaller than 3.7-8.5x, and it was never measured. Hardware and compilers are from 2011-2015 (Core i7 860, GCC 4.7, VC++ 2010). There is no PCLMUL/SIMD path, so modern implementations such as zlib-ng and Chromium's zlib are faster. There have been no commits since 2021-09-29.

Slicing-by-N trades table memory (up to 16KB) for speed; purely software/table-based, no PCLMULQDQ/SSE4.2 hardware CRC path, so slower than hardware-accelerated CRC32C libraries; single-header C++ library, usable from C via a thin wrapper

## Maintenance

Abandoned (last commit 2021-09-29, open PRs unanswered). The code is Zlib-licensed, two files, dependency-free and trivially vendorable, but it predates hardware-accelerated CRC and was last tuned for 2010-2015 compilers and CPUs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party blog table (CRC32 of 1 GByte, Core i7 860, GCC 4.7 vs Visual C++ 2010) measured with public benchmark code (Crc32Test.cpp in the repo, which times crc32_1byte against crc32_4bytes/8bytes/16bytes). It is not A for two reasons: the flags used for the 2011-2015 table are never stated (the repo Makefile with -O3 was only added in 2016), and the baseline that was measured is the author's own Sarwate byte-table reimplementation, not zlib's crc32().
- **Verifier notes:** Numbers on the page match the record, except that the record's lower ratio bound (\~4.3x) is wrong: 1400/375 is about 3.7x, and the record left out the VC++ Slicing-by-16 figure of 2000 MByte/s. Metadata checked via gh: Zlib license, 194 stars, not a fork, not archived, last commit 2021-09-29, so abandoned. The main correction is the baseline: the page equates Sarwate with zlib, but zlib's crc32() has not been byte-wise Sarwate since 2003.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://create.stephan-brumme.com/crc32/>
  - <https://github.com/stbrumme/crc32>
  - <https://github.com/stbrumme/crc32/commits>
  - <https://raw.githubusercontent.com/stbrumme/crc32/master/Makefile>
  - <https://raw.githubusercontent.com/stbrumme/crc32/master/readme.md>
  - <https://raw.githubusercontent.com/stbrumme/crc32/master/Crc32Test.cpp>
  - <https://raw.githubusercontent.com/madler/zlib/master/ChangeLog>
  - <https://raw.githubusercontent.com/madler/zlib/v1.2.11/crc32.c>
- **Sources the enricher read:**
  - <https://github.com/stbrumme/crc32>
  - <https://github.com/stbrumme/crc32/blob/master/readme.md>
  - <https://github.com/stbrumme/crc32/blob/master/Crc32.h>
  - <https://github.com/stbrumme/crc32/blob/master/Crc32.cpp>
  - <https://github.com/stbrumme/crc32/blob/master/Crc32Test.cpp>
  - <https://github.com/stbrumme/crc32/blob/master/Crc32TestMultithreaded.cpp>
  - <https://github.com/stbrumme/crc32/blob/master/Makefile>
  - <https://github.com/stbrumme/crc32/blob/master/changelog.md>
  - <https://github.com/stbrumme/crc32/commits/master>
  - <https://github.com/stbrumme/crc32/issues?q=is%3Aissue>
  - <https://github.com/stbrumme/crc32/issues/12>
  - <https://github.com/stbrumme/crc32/pull/15>
  - <https://github.com/stbrumme/crc32/issues/16>
  - <https://github.com/stbrumme/crc32/issues/17>
  - <https://github.com/stbrumme/crc32/issues/18>
  - <https://create.stephan-brumme.com/crc32/>
  - <https://raw.githubusercontent.com/madler/zlib/master/ChangeLog>
  - <https://raw.githubusercontent.com/madler/zlib/v1.2.11/crc32.c>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/stbrumme/crc32`) · [data/wave7/enrich/raw/github_com_stbrumme_crc32.json](../../../data/wave7/enrich/raw/github_com_stbrumme_crc32.json) (enrichment confidence 0.8)

</details>
