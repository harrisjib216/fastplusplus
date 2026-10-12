# FastPFor (SIMD-FastPFOR, SIMD-BP128)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++11 library of SIMD integer codecs (SIMD-FastPFOR, SIMD-BP128) decoding 32-bit integer arrays 2-3x faster than Simple-8b and VByte.

| | |
|---|---|
| **Beats** | Simple-8b and VByte (varint); also scalar FastPFOR/SimplePFOR |
| **Claimed result** | SPE 2015 paper Table V (ClueWeb09, decode, million ints/s): SIMD-FastPFOR 1200, SIMD-BP128 with vectorized delta 2300, Simple-8b 730, Variable Byte 540; 1.6x and 3.2x over Simple-8b (derived from page data). Bits per integer 8.1 (SIMD-FastPFOR) vs 7.5. The TurboPFor README (competitor-run, Skylake i7-6700, gcc 9.2, no flags) gives FP_SimdFastPFor 624/8748 MB/s vs Simple-8b 848/3832. |
| **Workload** | Decoding sorted/small 32-bit integer lists (posting lists, delta coded) in blocks of 128+ integers with SSE SIMD, measured in billions of integers per second. |
| **Metric** | throughput |
| **Hardware** | Core i7-2600 3.40 GHz (SPE paper); Skylake i7-6700 3.4 GHz for the TurboPFor README rows. |
| **Compiler and flags** | GCC 4.7 -O3 -mssse3 (SPE paper); gcc 9.2 with unstated flags for the TurboPFor rows. |
| **Adoption** | 978 stars; used in zsearch, GMAP/GSNAP; Lucene 4.6 format referenced; ports to Java, C#, Go |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/lemire/FastPFor) · [benchmark](https://paperhub.s3.amazonaws.com/ede067e14ecd522323725ac60dd15fcb.pdf) |

## Verdict

The SPE 2015 paper (arXiv 1209.2137v1, opened via a mirror) measured on an Intel Core i7-2600 at 3.40 GHz with GCC 4.7 -O3 (plus -mssse3), code in this repository: on ClueWeb09 posting lists weighted by AOL queries, SIMD-FastPFOR decoded 1,200 and SIMD-BP128 with vectorized delta 2,300 million integers/s vs Simple-8b 730 and Variable Byte 540, i.e. 1.6x and 3.2x Simple-8b (derived from page data), with SIMD-FastPFOR at 8.1 bits/int vs Simple-8b's 7.5. A later third-party TurboPFor table (Skylake i7-6700, 2019) shows FP_SimdFastPFor decoding at 8,748 MB/s vs Simple-8b 3,832 and FP_VByte 4,268, but encoding slower than Simple-8b (624 vs 848 MB/s).

## Use it when

- Decoding large arrays of small or delta-coded 32-bit integers (inverted-index posting lists, column stores, genome hash tables) where decode throughput in billions of integers per second matters more than encode speed.
- Blocks of 128 or more integers: SIMD-BP128 and SIMD-FastPFOR work per 128-integer block and per page, and the paper shows them slowing down most on short arrays.
- When you want to benchmark many codecs on your own data behind one interface: the factory exposes PFOR, NewPFD, OptPFD, Simple-8b/9/16, VByte, varint-G8IU, Stream VByte and others for side-by-side runs.
- x86-64 with SSE4.2 or aarch64 with NEON, from a C++11 codebase that can vendor an Apache-2.0 static library.

## Skip it when

- Untrusted or possibly corrupted input: the README states inputs are not validated before decoding, and issue #139 (a 4-byte input causing an ASan heap-buffer-overflow read in FastPFor::decodeArray) was closed as invalid without a fix.
- Best compression ratio at moderate speed: in the paper Simple-8b and OptPFD store fewer bits per integer than the fastest vectorized variants (ClueWeb09: Simple-8b 7.5 bits vs SIMD-FastPFOR with vectorized delta 9.9).
- Sorted lists needing intersection or fast delta handling: the README itself points to SIMDCompressionAndIntersection, since this library is generic and not optimized for differential coding.
- Short arrays (a few dozen integers) or 64-bit values: block codecs pad to 128 integers, and the 64-bit encodeArray/decodeArray overloads throw 'Not implemented!' in the IntegerCODEC base class unless a codec overrides them.
- Highest absolute speed today: later libraries in this category (TurboPFor, simdcomp, upack) report higher pack/unpack throughput than FP_SimdFastPFor in the same third-party table.

## How it is fast

Binary packing in blocks of 128 integers with SSE2 shifts and masks, so four integers are unpacked per instruction with no branches (SIMD-BP128). SIMD-FastPFOR is patched frame-of-reference: each block is packed at a bit width chosen to leave a few large values as exceptions, and the exceptions are stored per page in separate bit-packed arrays so they too decode with SIMD. The paper's fastest variants also vectorize delta decoding (prefix sum) and decode in chunks small enough to stay in cache, which it reports as an almost twofold gain.

## Compared with alternatives

Pick FastPFor over simdcomp or Stream VByte when you want a patched-FOR codec with a better ratio than plain binary packing, or a single C++ harness of many codecs; pick TurboPFor (GPL) or upack for maximum pack/unpack speed, SIMDCompressionAndIntersection for sorted lists with SIMD intersection, and ds2i or opt_vbyte when building a full inverted index.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target FastPFOR, installable); headers in headers/ |
| **Dependencies** | none for the library; Google Test for the tests (FASTPFOR_WITH_TEST, on by default); Snappy only for optional comparison binaries |
| **Minimum toolchain** | C++11; README lists GCC 4.7+, clang 3.2+, ICC 13.0.1+, MSVC 2012+ |
| **Platforms** | x86-64 with SSE4.2 (key schemes need only SSE2; some test binaries need SSE4.1), aarch64 via native NEON intrinsics; Linux, macOS, Windows |
| **Thread safety** | Codec objects are not thread safe; the README says to give each thread its own IntegerCODEC objects |
| **Drop-in for the baseline** | partial — it ships its own Simple-8b and VByte implementations behind the same interface, so switching codecs is a name change, but the encoded formats differ and it does not read data written by other Simple-8b or varint libraries |

## Gotchas

- CMakeLists.txt sets FASTPFOR_SIMD_MODE to native (-march=native) by default although its own comment and the README call portable (-msse4.2) the default; a default build can SIGILL on another CPU, so pass -DFASTPFOR_SIMD_MODE=portable for anything you distribute.
- The caller must size output buffers generously: some schemes expand incompressible data, and Simple-9/Simple-16 deliberately write past the logical end of the output buffer (README).
- varint-G8IU in the library is patented by its authors; the README says not to use it if you want to avoid patents.
- SIMDFastPFor encodeArray requires the length to be a multiple of its block size (checkifdivisibleby); use the composite codecs from the factory, which pair it with a variable-byte tail coder, for arbitrary lengths.

## Known shortcomings

- Tier C: the only comparison numbers come from the competing TurboPFor README (Skylake i7-6700 3.4 GHz, gcc 9.2 per issue #47, no flags), run by a competitor's author. The SPE 2015 paper (arXiv 1209.2137, blocked) could raise it to B. Repo now lives under fast-pack/FastPFOR.
- Raised C to A (retier-01) after the enricher opened the SPE paper via the paperhub.s3.amazonaws.com mirror. The decoder does no input validation (README); issue #139 (heap-buffer-overflow out-of-bounds read in FastPFor::decodeArray on 4-byte input) was closed 'invalid' without a fix; CMakeLists defaults FASTPFOR_SIMD_MODE=native (-march=native) although the README and the file's comment say portable, so a default build can SIGILL on another CPU; varint-G8IU is patented.

## Caveats and trade-offs

The repo README claims are against gzip/LZO/Snappy/LZ4 (not in the baseline list). The Simple-8b and VByte comparison is derived from a competitor's (TurboPFor) README table dated 2019.11; the linked issue #47 names Skylake i7-6700 3.4GHz and gcc 9.2 but no compiler flags. Encode speed of SimdFastPFor (624 MB/s) is lower than Simple-8b (848 MB/s) in that table. The peer-reviewed SPE 2015 paper 'Decoding billions of integers per second through vectorization' (arXiv 1209.2137) is the primary evidence and was not opened (arXiv blocked; no copy found on GitHub); opening it could justify tier B. FastPFor is itself the baseline other catalog entries beat. The repository now appears under the fast-pack organization (fast-pack/FastPFOR); lemire/FastPFor still resolves.

SIMD codecs need SSE2/SSSE3 (ARM64 NEON supported); best throughput on 128-integer blocks of 32-bit values; SIMD-FastPFOR trades some speed for 5-15% better ratio than SIMD-BP128; varint-G8IU in the library is patented.

## Maintenance

Active (last commit 2026-06-07, release 0.5.0), Apache-2.0, small C++11 code base with no runtime dependencies that is easy to vendor; its formats and benchmarks are the reference point other integer codecs in this category measure against.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** TurboPFor README ZIPF table (labelled 2019.11, ./icapp -a1.5 -m0 -M255 -n100M ZIPF) shows FP_SimdFastPFor 64Ki 624 MB/s encode / 8748 MB/s decode vs Simple-8b 848 / 3832 and FP_VByte 5200 / 4268, exactly as claimed; the icapp code is public and the linked issue #47 names Skylake i7-6700 3.4GHz and gcc 9.2, but no compiler flags are stated anywhere, so not A. The run is by a competing library's author, not an independent suite, and the peer-reviewed SPE 2015 paper (arXiv 1209.2137) could not be opened, so C stands.
- **Retiered** C to A: Raised C to A: the enricher opened the SPE paper (arXiv 1209.2137v1, via the paperhub.s3.amazonaws.com mirror), which states the machine (Core i7-2600 3.40 GHz), compiler and flags (GCC 4.7 -O3 -mssse3) and uses the public FastPFor code; Table V ClueWeb09 decode gives SIMD-FastPFOR 1200 and SIMD-BP128 with vectorized delta 2300 million ints/s against Simple-8b 730 and Variable Byte 540 (1.6x and 3.2x over Simple-8b, derived from page data).
- **Verifier notes:** All README-table numbers match the FP_SimdFastPFor 64Ki, Simple-8b and FP_VByte rows. Metadata confirmed: Apache-2.0, 978 stars, not archived or fork, last commit 2026-06-07 ('0.5.0'). Candidate for a paper-access retier to B.
- **Fields the verifier corrected:** `hardware`, `caveats`, `benchmark_url`, `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher read the SPE 2015 paper (arXiv 1209.2137v1)
- **Pages the verifier opened:**
  - <https://github.com/powturbo/TurboPFor-Integer-Compression>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
  - <https://github.com/lemire/FastPFor>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/LICENSE>
  - <https://github.com/lemire/FastPFor/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/headers/codecs.h>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/headers/simdfastpfor.h>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/headers/codecfactory.h>
  - <https://raw.githubusercontent.com/lemire/FastPFor/HEAD/src/codecfactory.cpp>
  - <https://github.com/lemire/FastPFor/issues?q=is%3Aissue>
  - <https://github.com/lemire/FastPFor/issues/139>
  - <https://paperhub.s3.amazonaws.com/ede067e14ecd522323725ac60dd15fcb.pdf>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/fastpfor`) · [data/wave9/enrich/raw/github_com_lemire_fastpfor.json](../../../data/wave9/enrich/raw/github_com_lemire_fastpfor.json) (enrichment confidence 0.85)

</details>
