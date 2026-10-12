# simdcomp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> C library for SIMD binary packing of 128-integer blocks (SIMD-BP128); decodes several times faster than Simple-8b and scalar VByte.

| | |
|---|---|
| **Beats** | Simple-8b, VByte (FP_Vbyte) |
| **Claimed result** | Third-party table: SC_SIMDPack128 6952 MB/s encode / 9488 MB/s decode vs Simple-8b 836 / 3296 and FP_Vbyte 1888 / 1980 (derived from page data: \~8.3x encode and \~2.9x decode vs Simple-8b; \~3.7x and \~4.8x vs FP_Vbyte). Compression ratio 21.8% vs Simple-8b 18.9%. Repo README: 'decode at least 4 billions of compressed integers per second' and '0.3 cycles per integer on a Skylake'. |
| **Workload** | gov2.sorted docid set, block 128 with delta coding, single thread (TurboPFor README table row SC_SIMDPack128) |
| **Metric** | throughput |
| **Hardware** | Skylake i7-6700 3.4GHz (TurboPFor issue #47; table itself names no CPU) |
| **Adoption** | 538 stars; used by upscaledb, EventQL, ManticoreSearch |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/lemire/simdcomp) · [benchmark](https://github.com/powturbo/TurboPFor-Integer-Compression) |

## Verdict

In the TurboPFor README gov2.sorted table (dated 2019.11, block 128 with delta coding, run by the TurboPFor author; issue #47 names a Skylake i7-6700 3.4 GHz and gcc 9.2 but no flags), SC_SIMDPack128 encoded at 6952 MB/s and decoded at 9488 MB/s vs Simple-8b 836/3296 and FastPFor's scalar VByte 1888/1980, while storing 21.8% of raw size vs 18.9% and 28.0%. The README's own claims (4 billion integers/s, 0.3 cycles per integer on Skylake) compare only against gzip, LZO, Snappy and LZ4 and come with no published run.

## Use it when

- Large arrays of small or slowly growing 32-bit integers (posting lists, column chunks, sorted docids) where decode throughput matters more than squeezing the last bits.
- Sorted lists that need delta decode plus fast lower-bound search or select inside a packed block without fully unpacking (simdsearchd1, simdselectd1).
- Building your own compressed format or index (as upscaledb, EventQL and ManticoreSearch do) where you want permissively licensed (BSD-3-Clause) kernels instead of a GPL codec.
- x86-64 with SSE4.1 or better, or AArch64 with NEON, and data lengths that are mostly multiples of 128.

## Skip it when

- Skewed data with occasional large outliers: one big value sets the bit width for the whole 128-block; on gov2 it stores 21.8% of raw size vs 18.9% for Simple-8b and about 14% for PFor-style codecs (TurboPFor, OptPFD) in the TurboPFor table.
- Short arrays (under 128 values): the \*_shortlength paths are documented as much slower; LittleIntPacker targets that case.
- 64-bit integers: the API is 32-bit only (issue #34 asks about uint64_t and is open).
- Untrusted compressed input: there is no format and no validation; a libFuzzer heap-buffer-overflow report (issue #21, 2018) is closed without a visible fix, and the bit width and length come from the caller.
- If the fastest decode is all that matters and GPL is acceptable, TurboPFor's TurboPackV256 beats it in the same gov2 table (11902 vs 9488 MB/s decode, 14466 vs 6952 MB/s encode).

## How it is fast

SIMD-BP128 (Lemire and Boytsov, 'Decoding billions of integers per second through vectorization', SPE 2015) lays integers out vertically across the four 32-bit lanes of an SSE register, so 4 values are shifted, masked and ORed per instruction with no per-value branches. There is one fully unrolled pack/unpack kernel per bit width 0-32 selected by a switch, and the d1 variants fuse the delta prefix sum into the unpack. AVX2 (256-integer) and AVX-512 (512-integer) kernels exist when compiled with those ISAs, and a small in-tree NEON shim maps the SSE intrinsics on AArch64.

## Compared with alternatives

Choose simdcomp over FastPFor or SIMDCompressionAndIntersection when you want a small C library with just the bit-packing kernels and your own block format; choose those C++ libraries for complete codecs with PFor exception handling (better ratio on skewed data) or list intersection. Over TurboPFor, pick it for the BSD license; over Stream VByte or MaskedVByte, pick it when data is blockable and you want both faster decode and smaller output.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake target simdcomp::simdcomp, pkg-config file, FetchContent supported) |
| **Dependencies** | none for the library; the optional benchmarks fetch lemire/counters over the network and need C++17 |
| **Minimum toolchain** | C89/C90 compiler with extensions (GCC, Clang, MSVC); CMake 3.14 |
| **Platforms** | x86/x86-64 (SSE2 for core packing, SSE4.1 for some helpers, optional AVX2/AVX-512 kernels); AArch64/ARM NEON via include/neon128.h (added June 2026) |
| **Thread safety** | not documented; functions are stateless and operate on caller buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- The CMake option SIMDCOMP_NATIVE defaults to ON and compiles with -march=native, so a library built on one machine may crash with illegal instructions on an older CPU; set -DSIMDCOMP_NATIVE=OFF for distributed binaries.
- The AVX2 and AVX-512 functions (avxpack/avxunpack, avx512pack/avx512unpack) are only declared when the build enables those ISAs, use 256/512-integer blocks and produce a different layout from the 128-integer SSE format; do not mix them.
- simdpackwithoutmask and simdpackwithoutmaskd1 assume every value (or delta) fits in b bits; an oversized value silently corrupts its neighbors. simdunpack with a bit width above 32 silently writes nothing.
- The interleaved 4-lane layout is not the same as scalar sequential bit packing, so other libraries can read it only if they implement the same layout (the Rust bitpacking crate is a port).

## Known shortcomings

- Tier C: SC_SIMDPack128 6952/9488 MB/s vs Simple-8b 836/3296 come from the competing TurboPFor README (i7-6700, gcc 9.2, no flags); the SPE 2015 paper (blocked) could raise it to B.
- CMake SIMDCOMP_NATIVE defaults ON (-march=native), so built binaries are not portable; libFuzzer heap-buffer-overflow issue #21 (2018) closed with no visible fix; no container format and no validation. Worse ratio than Simple-8b on gov2 (21.8% vs 18.9%) and TurboPackV256 decodes faster in the same table (11902 vs 9488 MB/s). The NEON shim is new (2026-06-07).

## Caveats and trade-offs

Numbers come from the TurboPFor README (gov2 table labelled 2019.11), written by the author of a competing library; the table gives no CPU or flags, and the linked issue #47 ('Skylake i7-6700 3.4GHz gcc 9.2') names CPU and compiler but no flags and does not itself contain an SC_SIMDPack128 row. SIMDPack128 compresses gov2 less well than Simple-8b (21.8% vs 18.9%). The repo's own bitpackingbenchmark reports cycles per integer but the README gives no baseline comparison; the 15 GB/s claim compares to gzip/LZO/Snappy/LZ4. The underlying SIMD-BP128 scheme is evaluated in the peer-reviewed SPE 2015 paper (arXiv 1209.2137), not opened (arXiv blocked).

Binary packing of 128-integer blocks, so worse compression than Simple-8b / PFor on skewed data; needs SSE2/SSE4.1 or NEON; C API usable from C++; the 128-block unit is bad for short arrays (LittleIntPacker targets that).

## Maintenance

Mature (2019-2023 commits are mostly README and warning fixes) and still maintained by Daniel Lemire in the fast-pack org, with a CMake package and NEON support added on 2026-06-07; BSD-3-Clause and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** TurboPFor README gov2.sorted table shows SC_SIMDPack128 6952 / 9488 MB/s (ratio 21.8%) vs Simple-8b 836 / 3296 (18.9%) and FP_Vbyte 1888 / 1980, matching the claim and its derived ratios; no flags stated and the run is by a competitor, so C. The repo's own README claims (0.3 cycles/integer on Skylake, 15 GB/s) have no baseline beyond gzip/LZO/Snappy/LZ4.
- **Verifier notes:** Numbers match the SC_SIMDPack128 row. Metadata confirmed: BSD-3-Clause, 538 stars, not archived or fork, last commit 2026-06-07 ('pages'); README confirms upscaledb, EventQL, ManticoreSearch usage.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/powturbo/TurboPFor-Integer-Compression>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
  - <https://github.com/lemire/simdcomp>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/LICENSE>
  - <https://github.com/lemire/simdcomp/commits/master>
- **Sources the enricher read:**
  - <https://github.com/lemire/simdcomp>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/simdcomp.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/simdbitpacking.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/simdcomputil.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/simdintegratedbitpacking.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/avxbitpacking.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/avx512bitpacking.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/simdfor.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/portability.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/include/neon128.h>
  - <https://raw.githubusercontent.com/lemire/simdcomp/HEAD/src/simdbitpacking.c>
  - <https://github.com/lemire/simdcomp/issues?q=is%3Aissue>
  - <https://github.com/fast-pack/simdcomp/issues/21>
  - <https://github.com/fast-pack/simdcomp/issues/36>
  - <https://github.com/fast-pack/simdcomp/commits/master>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/simdcomp`) · [data/wave9/enrich/raw/github_com_lemire_simdcomp.json](../../../data/wave9/enrich/raw/github_com_lemire_simdcomp.json) (enrichment confidence 0.8)

</details>
