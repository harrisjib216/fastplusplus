# Stream VByte (streamvbyte)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Small C99 library for byte-oriented uint32 compression (SIMD Group Varint variant) that decodes faster than VByte, MaskedVByte and varint-G8IU.

| | |
|---|---|
| **Beats** | varint-G8IU, Masked VByte and VByte (varint) |
| **Claimed result** | Paper (WebSearch snippets only): decoding up to twice as fast as varint-G8IU on real data, more than 4 billion differentially coded integers per second on a 3.4 GHz Haswell, at times exceeding memcpy speed. README (no baseline): Apple M4 Max mixed 1-4 byte data encode \~27 GB/s, decode \~41 GB/s. TurboPFor issue #47 (competitor-run, Skylake i7-6700 3.4GHz): StreamVByte docids decode 14,101.75 MB/s vs FastPFor 7,616.66 MB/s and MaskedVByte 6,507.48 MB/s. |
| **Workload** | Byte-oriented 32-bit integer compression with a separated control stream; decoding from RAM to L1 of differentially coded real posting-list data sets. |
| **Metric** | throughput |
| **Hardware** | Not stated for the TurboPFor 2019.11 tables; the README links issue #47 ('Skylake i7-6700 3.4GHz'), but that issue holds a different benchmark (test_collection docs/freqs) and does not tie the ZIPF/gov2 tables to that CPU. Repo's own numbers: Apple M4 Max. |
| **Adoption** | 419 stars; ported to Rust, Go, Java and others |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/lemire/streamvbyte) · [benchmark](https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47) |

## Verdict

The best-documented comparison is on a competitor's page: TurboPFor issue #47 (icapp harness, Skylake i7-6700 3.4 GHz, October 2019, no compiler or flags) gives StreamVByte delta 14,101.75 MB/s decode on doc IDs vs FastPFor 7,616.66, SimdFastPFor 13,818.59 and MaskedVByte 6,507.48 MB/s, while on term frequencies plain StreamVByte (16,825.56 MB/s) roughly ties MaskedVByte (16,846.15 MB/s) and compresses worse (31.30% vs 25.12% of input). The repo's own perf tool reports about 41 GB/s decode and 27 GB/s encode on an Apple M4 Max for 500,000 random integers, with no baseline; the paper's 2x-over-varint-G8IU claim could not be opened here.

## Use it when

- Decode-heavy 32-bit integer arrays (posting lists, doc IDs, column chunks, tile coordinates) where you want multi-GB/s decoding and can accept byte-granular compression.
- Sorted ID lists on x86-64: the delta codec has a fused SSE4.1 decode; issue #47 on the TurboPFor repo measured StreamVByte delta at 14,101.75 MB/s decode on doc IDs.
- Mixed-magnitude values where bit-packing per block wastes space on outliers but you still want branch-free SIMD decode.
- C or C++ projects that want a tiny, dependency-free, Apache-2.0 codec with runtime dispatch, already used by RediSearch, StarRocks, fbthrift and tilemaker per the README.

## Skip it when

- When compression ratio matters most: byte granularity costs bits versus bit-packing (the verifier's TurboPFor tables show about 10.00 vs 8.17 bits/integer against VByte on ZIPF and 11.50 vs 8.96 on gov2); FastPFor/simdcomp/TurboPFor pack tighter.
- 64-bit integers: the API is uint32_t only.
- Delta-coded or 0124 streams on ARM64: the differential decoder and the 0124 decoder have SSE4.1 paths only, so AArch64 falls back to scalar code (open issue #17, port differential coding to NEON, since 2017).
- Big-endian targets: unsupported per the README.
- Untrusted streams without validation: decode trusts the count and control bytes; call streamvbyte_validate_stream first (added in December 2024).

## How it is fast

Stream VByte separates the control bytes from the data bytes, so the decoder reads one control byte (four 2-bit lengths), looks up a 16-byte shuffle mask and a length in 256-entry tables, and expands four integers with a single PSHUFB (SSE4.1) or TBL (NEON) instruction, with no per-integer branches and no dependency of the next control byte on the data. Encoding is vectorized the same way in reverse. The x64 delta decoder fuses an in-register prefix sum (two shift-and-add steps per four integers) into the decode loop. CPU features are detected at runtime, so one binary picks SSE4.1 or the scalar fallback.

## Compared with alternatives

Pick it over MaskedVByte or varint-simd when you control the format and want the fastest byte-oriented decode with a simple C API (MaskedVByte keeps the standard VByte format, which is its reason to exist). Pick FastPFor, simdcomp or SIMDCompressionAndIntersection's S4-BP128 when you need better compression ratio or sorted-list intersection, and TurboPFor if its GPL license is acceptable and you want the widest codec menu.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library; the perf benchmark (tests enabled) links sea_counters fetched through CPM |
| **Minimum toolchain** | C99; GCC 9+, LLVM 10+, Visual Studio 2019+; CMake 3.10+ (a Linux-style Makefile is also provided) |
| **Platforms** | x86-64 (SSE4.1 path selected at runtime, scalar fallback otherwise), AArch64 (NEON), other little-endian CPUs via the scalar path; Linux, macOS, Windows; big-endian unsupported |
| **Thread safety** | Functions are stateless over caller buffers; the one shared state is the cached CPU-feature flag, which uses std::atomic in C++ and _Atomic in C11 (a plain static under MSVC C). Not otherwise documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Decoding may read up to STREAMVBYTE_PADDING (16) bytes past the end of the compressed data, so allocate that slack on the input buffer; streamvbyte_compressedbytes does not include it, streamvbyte_max_compressedbytes does.
- The number of integers is not stored in the stream; you must keep it yourself and pass it to decode, and the decoders cannot detect a wrong count unless you call streamvbyte_validate_stream.
- Delta and plain streams are not interchangeable, and 0124 streams need the _0124 decoder and validator; using the wrong one silently returns garbage.
- Version 3.0.0 (April 2026) followed a March 2026 fix to the SSE4.1 detection macro (PR #77); pin a recent release rather than an old vendored copy.

## Known shortcomings

- Tier C: numbers come from the competing TurboPFor README 2019.11 tables (CPU for those tables not tied to issue #47, which is a different benchmark); StreamVByte uses more bits per integer than the packed codecs it beats on speed.
- The delta and 0124 decoders are SSE4.1 only and AArch64 falls back to scalar (open issue #17); decode reads up to 16 bytes of padding past the input; the count is not stored in the stream and validate_stream exists only since Dec 2024; uint32 only, big-endian unsupported. In TurboPFor's issue #47 (its own icapp harness, no compiler or flags) plain StreamVByte decodes 16,825.56 MB/s vs MaskedVByte 16,846.15, a tie, while MaskedVByte compresses better (25.12% vs 31.30%).

## Caveats and trade-offs

Numbers come from the TurboPFor README, written by the author of a competing library (TurboPFor); the tables give no CPU, compiler or flags, and linked issue #47 (October 2019) is a different benchmark whose page states the CPU but no compiler or flags. The table is labelled 2019.11; StreamVByte 3.0.0 (April 2026) differs from the '2019' build. StreamVByte compresses worse than VByte in those tables (10.00 vs 8.17 bits/integer on ZIPF, 11.50 vs 8.96 on gov2). The competitor repo also claims TurboByte is faster than StreamVByte (issue #96). The repo's own M4 Max table (500,000 random integers) has no baseline.

Worse compression than bit-packing schemes (byte granularity, e.g. 9-10 bits/int in TurboPFor tables); SSE4.1 or NEON for speed, scalar fallback.

## Maintenance

Actively maintained (3.0.0 released April 2026, commits through June 2026, CI on GCC 9-14, LLVM 12-18, macOS and Visual Studio), Apache-2.0, a few C files with no dependencies, so easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** The TurboPFor README tables (labelled 2019.11) list 'StreamVbyte 2019' at 11197/11984 MB/s on ZIPF vs FP_VByte 5200/4268 and 8456/9476 on gov2 vs FP_Vbyte 1888/1980, but give no CPU, compiler or flags next to the tables; the icapp code is public. The repo's own perf table (Apple M4 Max) has no baseline. Numbers without full methodology: C.
- **Verifier notes:** All quoted numbers are on the TurboPFor README and belong to the 'StreamVbyte 2019' rows; derived ratios are correct. The peer-reviewed IPL 2018 paper (arXiv 1709.08990; abstract per search snippet: decoding up to twice as fast as varint-G8IU) could support B, but arXiv and the TELUQ mirror are blocked here; candidate for a paper-access retier. Metadata confirmed: 419 stars, Apache-2.0, last commit 2026-06-07; users list verified in README.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/powturbo/TurboPFor-Integer-Compression/HEAD/README.md>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
  - <https://github.com/lemire/streamvbyte>
  - <https://github.com/lemire/streamvbyte/commits>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/include/streamvbyte.h>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/include/streamvbytedelta.h>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/include/streamvbyte_zigzag.h>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbyte_decode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbyte_encode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbytedelta_decode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbyte_0124_decode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbytedelta_x64_decode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbyte_isadetection.h>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/src/streamvbyte_x64_decode.c>
  - <https://raw.githubusercontent.com/lemire/streamvbyte/HEAD/tests/perf.c>
  - <https://github.com/lemire/streamvbyte/issues>
  - <https://github.com/lemire/streamvbyte/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/lemire/streamvbyte/issues/41>
  - <https://github.com/lemire/streamvbyte/issues/46>
  - <https://github.com/lemire/streamvbyte/issues/81>
  - <https://github.com/lemire/streamvbyte/pull/77>
  - <https://github.com/lemire/streamvbyte/commits>
  - <https://github.com/powturbo/TurboPFor-Integer-Compression/issues/47>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/streamvbyte`) · [data/wave9/enrich/raw/github_com_lemire_streamvbyte.json](../../../data/wave9/enrich/raw/github_com_lemire_streamvbyte.json) (enrichment confidence 0.75)

</details>
