# MaskedVByte

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> SIMD decoder for standard 32-bit VByte/varint streams; about 1.7-2.2x faster decode than scalar VByte in third-party tables.

| | |
|---|---|
| **Beats** | scalar VByte / varint (FP_VByte, PC_Vbyte) |
| **Claimed result** | Third-party table: ZIPF MaskedVByte 6689 MB/s encode / 9524 decode vs FP_VByte 5200 / 4268 and PC_Vbyte 2260 / 4208 (derived from page data: \~2.2x decode vs FP_VByte); gov2 MaskedVByte 2740 / 3384 vs FP_Vbyte 1888 / 1980 (\~1.7x decode, \~1.5x encode derived). |
| **Workload** | TurboPFor ZIPF and gov2.sorted decode of VByte-compressed integers, single thread |
| **Metric** | throughput |
| **Hardware** | Skylake i7-6700 3.4GHz (TurboPFor issue #47; table itself names no CPU) |
| **Adoption** | 131 stars; integrated into Apache Lucene experiments and PISA |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/lemire/MaskedVByte) · [benchmark](https://github.com/powturbo/TurboPFor-Integer-Compression) |

## Verdict

In the TurboPFor README tables (dated 2019.11, run by the TurboPFor author; issue #47 names a Skylake i7-6700 3.4 GHz and gcc 9.2 but no flags), MaskedVByte decoded 9524 MB/s vs FastPFor's scalar VByte 4268 MB/s on a 100M-integer Zipf set (about 2.2x), and 3384 vs 1980 MB/s on gov2.sorted with delta coding (about 1.7x), at identical compressed sizes. Encode speed in those tables (6689 and 2740 MB/s) comes from the benchmark harness, while this repository's own encoder is scalar.

## Use it when

- You must read existing VByte/varint-encoded 32-bit data (inverted-index postings, Lucene-style vInts, protobuf-style unsigned varints that fit in 5 bytes) and cannot change the format.
- Decode-heavy workloads on x86-64 with SSE4.1 where scalar varint decoding is the bottleneck, especially with many 1-2 byte values.
- Sorted docid or offset lists stored as delta-coded VByte, where the fused delta decode, select and search helpers avoid a separate prefix-sum pass.
- C or C++ projects that want a two-file, Apache-2.0 dependency with no third-party libraries.

## Skip it when

- Untrusted or possibly corrupted input: there is no validation; issue #6 (2025) reports segfaults when fuzzing libvbyte through this decoder and issue #7 (June 2026) reports an ASan-reproducible memory-safety bug reachable from the public decode API; both are closed with no visible fix.
- When you control the format: Stream VByte decodes faster in the same TurboPFor tables (ZIPF 11984 vs 9524 MB/s; gov2 9476 vs 3384 MB/s), and bit-packing codecs (simdcomp, TurboPack) are faster still and compress better.
- 64-bit integers or signed varints (zigzag): only 32-bit unsigned values, at most 5 bytes per value.
- Encode-heavy workloads: the encoder is a plain scalar loop; only decoding is vectorized.
- AArch64 builds: the README says NEON works through include/sse_to_neon.h, but that file was not present in include/ or src/ on 2026-10-03 (raw fetch 404), and CI runs only on ubuntu-latest x86-64.

## How it is fast

It gathers the continuation bits of 48 input bytes at a time with pmovmskb (_mm_movemask_epi8) into a 64-bit mask, then uses the low 12 bits of that mask to index a 4 KB-aligned lookup table that gives a pshufb shuffle pattern plus the number of bytes consumed. One shuffle and a few mask/shift/or operations then produce 2, 4, 6 or 16 integers per step (Masked VByte, Plaisance, Kurz and Lemire, 'Vectorized VByte Decoding', 2015). Delta variants fuse an SSE prefix sum into the same step; an AVX2 path is used for the mask scan when compiled with -mavx2.

## Compared with alternatives

Pick MaskedVByte over Stream VByte, simdcomp or TurboPFor when the data is already in standard VByte and must stay readable by other tools; if you can choose the format, Stream VByte (faster decode) or simdcomp/TurboPFor bit packing (faster and smaller) win. varint-simd covers the same niche for Rust with 64-bit support.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (two .c files; easy to vendor as source-drop); CMake package maskedvbyte::maskedvbyte or Makefile |
| **Dependencies** | none |
| **Minimum toolchain** | C99 compiler with SSE4.1 intrinsics (GCC, Clang; MSVC fixes merged in 2023); CMake 3.15 for the CMake build |
| **Platforms** | x86-64 with SSE4.1 (optional AVX2 path); AArch64 claimed in README but the NEON shim header is missing from the repository |
| **Thread safety** | not documented; functions are stateless and use only read-only static tables, so concurrent calls on separate buffers look safe from the code |
| **Drop-in for the baseline** | partial — same byte format as standard 32-bit VByte, so data is compatible, but you call its C functions instead of your existing decoder loop |

## Gotchas

- masked_vbyte_decode takes the number of integers, not bytes; pass a wrong count or a truncated buffer and it reads past the input, since there are no bounds checks on the scalar tail.
- From code reading (not tested): mask patterns implying a 6+ byte varint map to lookup entries with 0 bytes consumed, so a malformed stream can stall the byte cursor while the output cursor keeps advancing; treat this as the likely shape of the issue #7 report.
- The Makefile's benchmark target refers to benchmarks/benchmark.c, which is not in the repository; the repo has no benchmark of its own, so the numbers come from third parties.
- The \*_fromcompressedsize variants need an output buffer sized for the worst case (one integer per input byte).

## Known shortcomings

- Tier C: ZIPF and gov2 numbers come from the competing TurboPFor README (i7-6700, gcc 9.2, no flags).
- The arXiv paper abstract (blocked, snippet only) claims 2-4x over scalar VByte, not 3x.
- The decoder has no input validation: issue #6 (2025) fuzzing segfaults via libvbyte and issue #7 (2026-06-27) an ASan memory-safety bug reachable from the public decode API, both closed with no visible fix; by code reading a 6+ byte varint maps to lookup entries that consume 0 bytes. The README's AArch64 NEON path (include/sse_to_neon.h) 404s on master and CI runs only ubuntu x86-64; the encoder is scalar only; the Makefile benchmark target points at a missing benchmarks/benchmark.c. Stream VByte decodes faster in the same tables (gov2 9476 vs 3384 MB/s).

## Caveats and trade-offs

Numbers come from the TurboPFor README (tables labelled 2019.11), written by the author of a competing library; the table gives no CPU or flags, and the linked issue #47 ('Skylake i7-6700 3.4GHz gcc 9.2', dated 2019-10-16) names the CPU and compiler but no compiler flags. Issue #47's own data does include MaskedVByte rows but not the FP_VByte rows, so the comparison rests on the README tables. The repo README itself has no numbers; the paper (Plaisance, Kurz, Lemire, 'Vectorized VByte Decoding', 2015, arXiv 1503.07387) was not opened because arXiv is blocked.

Decodes the standard VByte format, so it is format-compatible with ordinary varint; needs SSE4.1 or NEON; 32-bit integers only.

## Maintenance

Maintained at low intensity by Daniel Lemire (moved to the fast-pack org; version 0.1.0 tagged in CMake on 2026-06-07 with a CMake package), Apache-2.0 and small enough to vendor, but unresolved memory-safety reports mean it should only see trusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** TurboPFor README shows MaskedVByte 6689 / 9524 MB/s vs FP_VByte 5200 / 4268 and PC_Vbyte 2260 / 4208 on ZIPF, and 2740 / 3384 vs FP_Vbyte 1888 / 1980 on gov2.sorted, matching the claim; benchmark code is public and issue #47 names the CPU and gcc 9.2 but no flags, and the run is by a competitor, so C.
- **Verifier notes:** Numbers match both TurboPFor README tables. Metadata confirmed: Apache-2.0, 131 stars, not archived, last commit 2026-06-07; README confirms Lucene (Greg Bowyer branch) and PISA usage.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/powturbo/TurboPFor-Integer-Compression>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
  - <https://github.com/lemire/MaskedVByte>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/LICENSE>
  - <https://github.com/lemire/MaskedVByte/commits/master>
- **Sources the enricher read:**
  - <https://github.com/lemire/MaskedVByte>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/include/varintdecode.h>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/include/varintencode.h>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/src/varintdecode.c>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/src/varintencode.c>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemire/MaskedVByte/HEAD/tests/unit.c>
  - <https://raw.githubusercontent.com/fast-pack/MaskedVByte/master/.github/workflows/ubuntu.yml>
  - <https://github.com/fast-pack/MaskedVByte/tree/master/include>
  - <https://github.com/fast-pack/MaskedVByte/tree/master/src>
  - <https://github.com/fast-pack/MaskedVByte/commits/master>
  - <https://github.com/lemire/MaskedVByte/issues?q=is%3Aissue>
  - <https://github.com/fast-pack/MaskedVByte/issues/6>
  - <https://github.com/fast-pack/MaskedVByte/issues/7>
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/maskedvbyte`) · [data/wave9/enrich/raw/github_com_lemire_maskedvbyte.json](../../../data/wave9/enrich/raw/github_com_lemire_maskedvbyte.json) (enrichment confidence 0.8)

</details>
