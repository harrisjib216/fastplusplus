# TurboPFor Integer Compression

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> GPL C library of SIMD bit packing, PFor, variable-byte and Elias-Fano integer codecs; README tables beat Simple-8b, FastPFor and VByte.

| | |
|---|---|
| **Beats** | Simple-8b, FastPFor (FP_VByte/FP_SimdFastPFor), varint-style VByte |
| **Claimed result** | ZIPF table (100M integers, 2019.11): TurboPack scalar 11694 MB/s encode / 10138 decode vs Simple-8b 848 / 3832; TurboPackV sse 17357 / 12363; TurboVByte 11191 / 10333 vs FP_VByte 5200 / 4268. Ratios (derived from page data): TurboPackV decode \~3.2x Simple-8b, TurboVByte decode \~2.4x FP_VByte. gov2.sorted: TurboPackV 7064 / 10268 vs Simple-8b 836 / 3296 and FP_Vbyte 1888 / 1980. TurboPack compression (25.0%) equals fixed-width packing; Simple-8b is 24.0%, so Simple-8b packs slightly smaller there. |
| **Workload** | icapp benchmark on 100M Zipfian integers (block 128/256) and the gov2.sorted docid set, single thread, encode and decode MB/s |
| **Metric** | throughput |
| **Hardware** | Not stated beside the README tables; the README links issue #47 titled 'Skylake i7-6700 3.4GHz gcc 9.2', whose page is a different benchmark (test_collection) and states the CPU but no compiler or flags |
| **Adoption** | 848 stars; used by Debian Code Search |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/powturbo/TurboPFor-Integer-Compression) · [benchmark](https://github.com/powturbo/TurboPFor-Integer-Compression) |

## Verdict

The author's icapp benchmark (single thread, CPU, compiler and flags not stated beside the 2019.11 tables) on 100M Zipfian integers (alpha 1.5, range 0-255, 128/256-value blocks) shows TurboPackV (SSE) encoding at 17,357 MB/s and decoding at 12,363 MB/s against Simple-8b's 848/3,832 and TurboVByte at 11,191/10,333 against FastPFor's VByte at 5,200/4,268; on gov2.sorted with delta coding TurboPackV runs 7,064/10,268 MB/s versus Simple-8b 836/3,296. Simple-8b packs slightly smaller than plain TurboPack on Zipf (24.0% versus 25.0%), while TurboPFor256 packs smaller than both (15.7%).

## Use it when

- Inverted-index posting lists, docid/frequency/position arrays or column-store integer columns in blocks of 128 or 256 values, where decode speed and bits per integer both matter
- Sorted 32-bit ids: delta-fused SIMD unpack (TurboPackV256 about 11.9 GB/s decode on gov2.sorted) or TurboPFor256 (4.48 bits/int) depending on the size-versus-speed point
- Timestamps and other monotonic time series, where zigzag/delta-of-delta plus bit packing reached 0.008-0.2% of raw size in the README's ts.txt test
- Projects that can accept GPL-2.0, or buy the author's commercial license, on x86-64 (SSE4.1/AVX2), ARMv8 NEON or POWER9
- Random access to individual packed values without decompressing the block

## Skip it when

- Closed-source or permissively licensed products that will not buy a commercial license: the code is GPL-2.0; FastPFor, simdcomp, streamvbyte and MaskedVByte are Apache-2.0 or similar
- Decoding untrusted data: no bounds checks are documented beyond 'normally does not read outside the input buffers', a third-party analysis (Stapelberg 2019, snippet only) says it reads and writes as far as it needs and decode buffers need about 32 extra integers, and issue #133 showed p4nbound16 under-sizing an encode buffer by 2 bytes
- Code that needs a reviewable history: issue #122 reports a fix for uninitialized registers (#60) silently reverted, most commits have no message, and a batch of bug reports (#130 memory corruption in vlccomp32 on small inputs, #135 fpx32 decode bug, #141 1+ MB stack use) was closed in April 2026 with no visible reply
- Small stacks or embedded targets: issue #141 measured over 1 MB of stack because large switch blocks sum their frames, and the Windows ICCODEC build links with a 32 MB stack
- Pre-AVX x86 CPUs with the default makefile, which compiles the base objects with -march=corei7-avx (Sandy Bridge); riscv64 only gets the scalar generic path

## How it is fast

TurboPFor picks a base bit width per block from a histogram of value bit lengths and an estimated cost, packs all values at that width, and stores the high bits of exceptions separately behind a 64-bit-word bitmap (hybrid mode can store them as variable bytes); decode unpacks the block and then adds exceptions back with pshufb shuffle tables indexed by 4- or 8-bit bitmap slices. TurboPackV/TurboPack256V are SSE/AVX2/NEON vertical (lane-interleaved) bit packers with delta, delta-of-1, FOR and zigzag fused into the unpack loop, so no second pass over the output is needed. The x86 build compiles AVX2 copies of the hot files and selects them at run time (cpuini/cpuisa), and fixed-width data supports direct access to one element (bitgetx32) without decoding the block.

## Compared with alternatives

Pick TurboPFor when you want one library covering bit packing, PFor, varint, Elias-Fano and time-series transforms with the best size/speed points in its own tables (TurboPFor256 15.7% at 10.9 GB/s decode versus FP_SIMDOptPFor 16.3% at 2.7 GB/s) and GPL is acceptable; choose simdcomp or FastPFor for permissive licensing and conservative code, streamvbyte or MaskedVByte for a small, well-specified varint format, and ds2i for partitioned Elias-Fano indexes.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for libic.a (libm, librt on Linux for the benchmark); optional git submodules (zstd, lz4, Turbo-Range-Coder, bitshuffle and others) only for ICCODEC=1 and the icapp benchmark |
| **Minimum toolchain** | C99-style C with GCC &gt;= 4.6 or Clang &gt;= 3.2 on x86-64, GCC &gt;= 6.3 on aarch64, GCC &gt;= 8 on ppc64le, Visual C++ &gt;= VS2008 (makefile.vs) or the VS2022 project; GCC 14 build problems were reported in issue #134 |
| **Platforms** | x86-64 (default build needs AVX via -march=corei7-avx, AVX2 paths dispatched at run time), aarch64 NEON including Apple M1, POWER9 Altivec, riscv64 scalar generic path (added June 2026); Linux, macOS, Windows |
| **Thread safety** | README: 'All TurboPFor integer compression functions are thread safe' (stateless functions over caller buffers) |
| **Drop-in for the baseline** | no |

## Gotchas

- Size output buffers with the matching \*bound function and pad inputs; low-level p4enc32 and similar calls are limited to 128/256 integers per call, and only the 'n' array variants handle arbitrary lengths
- Scalar, 128v (SSE/NEON) and 256v (AVX2) variants are separate function families; decode with the same family and integer width that encoded the data
- The library defines no stream header: you must store the element count and choose the codec yourself, and the README benchmark tables (2019.11) predate many later code changes
- Debian Code Search, the best-known user, replaced its cgo binding with a pure-Go SIMD port of the TurboPFor format in August 2026 (Stapelberg blog, WebSearch snippet only)

## Known shortcomings

- Tier C: first-party README tables with no flags; the record's TurboPack scalar decode figure was 8876 (TurboFor) and is corrected to 10138. GPL-2.0.
- No documented bounds checks; #133 p4nbound16 under-sizes the encode buffer by 2 bytes; #122 reports the fix for #60 (uninitialized registers) silently reverted; #130 memory corruption in vlccomp32, #135 fpx32 decode bug and #141 1+ MB of stack were all bulk-closed in Apr 2026 with no visible reply; the default x86 build needs AVX (-march=corei7-avx). Debian Code Search dropped the C library in Aug 2026 for a pure-Go SIMD port (Stapelberg blog, snippet only).

## Caveats and trade-offs

First-party numbers from the TurboPFor README; tables give no CPU, compiler or flags, and linked issue #47 (October 2019) is a separate benchmark whose page lists the CPU but no compiler flags. Tables are labelled 2019.11 and the code has changed since. Self-reported 'No other Integer Compression compress/decompress faster' is marketing wording. FastPFor-family rows marked (\*) use 64Ki blocks. GPL-2.0 (commercial license offered), so copying imposes copyleft.

GPL-2.0 (commercial license offered by author), so copyleft; C library with C++ headers; SSE/AVX2/NEON/Power9 paths; direct access to bit-packed entries without decompression; no input validation promised beyond 'normally does not read outside buffers'.

## Maintenance

Actively changed (commits through 2026-09-21, riscv64 path merged June 2026) but by one author with mostly unlabelled commits and reports of reverted fixes; GPL-2.0 with a paid commercial license, so 'copyable' only under copyleft terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (2019.11) compare TurboPack/TurboPackV/TurboVByte against Simple-8b, FastPFor codecs and VByte variants via the public icapp benchmark, but state no CPU, compiler or flags beside the tables; linked issue #47 is a different benchmark with no compiler or flags. First-party with partial methodology: C.
- **Verifier notes:** Record mislabelled TurboPack scalar decode as 8876 (that is TurboFor); corrected to 10138 from the ZIPF table. Other numbers and ratios check out. Metadata confirmed: 848 stars, GPL-2.0, last commit 2026-09-21; Debian Code Search listed as user in README. The README links the ADCS 2016 paper 'In Vacuo and In Situ Evaluation of SIMD Codecs' (dl.acm.org, blocked), a possible B source for a later retier.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/powturbo/TurboPFor-Integer-Compression>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/commits>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
- **Sources the enricher read:**
  - <https://github.com/powturbo/TurboPFor-Integer-Compression>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/include/ic.h>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/makefile>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/lib/vp4c.c>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/lib/vp4d.c>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/lib/bitunpack.c>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/commits/master>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues?q=is%3Aissue>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/122>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/132>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/133>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/141>
  - <https://github.com/stapelberg/goturbopfor>
  - https://michael.stapelberg.ch/posts/2019-02-05-turbopfor-analysis/ (EGRESS_BLOCKED; WebSearch snippet only)
  - https://michael.stapelberg.ch/posts/2026-09-06-dcs-fast-turbopfor-go-simd/ (WebSearch snippet only)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/powturbo/turbopfor-integer-compression`) · [data/wave9/enrich/raw/github_com_powturbo_turbopfor_integer_compression.json](../../../data/wave9/enrich/raw/github_com_powturbo_turbopfor_integer_compression.json) (enrichment confidence 0.8)

</details>
