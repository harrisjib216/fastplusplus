# sserangecoding (SSE 4.1 interleaved range coder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Unlicense` · 🔴 abandoned

> SSE 4.1 16-stream interleaved 24-bit range decoder for order-0 bytes; on book1 it decodes about 1.6x faster than FSE tANS.

| | |
|---|---|
| **Beats** | Finite State Entropy (FSE) demo by Yann Collet (tANS) and its Huff0 mode; length-limited Huffman; Fabian Giesen's SSE 4.1 interleaved rANS (ryg_rans) |
| **Claimed result** | Decode 577.1-619.1 MiB/s (2.3-2.5 cycles/byte) vs Collet FSE 370.3 MB/s decode (about 1.6x, derived) and vs ryg_rans interleaved SIMD rANS 512.8-565.6 MB/s on the same machine (roughly 1.1x, derived). FSE Huffman mode (-h) decodes faster: 800.9 MB/s. Output 436,229 bytes vs FSE 437,232 and 16-bit length-limited Huffman 438,385. README: AVX-2 port with 64 streams 1,373 MiB/s. |
| **Workload** | Order-0 decode of book1 (Calgary corpus, 768,771 bytes), 8-bit alphabet, 16 interleaved 24-bit range-coder streams. |
| **Metric** | throughput |
| **Hardware** | Core i7 1065G7 (Ice Lake, about 3.9 GHz); also quotes 4 GHz Skylake and Ryzen 5 3450U |
| **Compiler and flags** | CMakeLists.txt sets -O3 -msse4.1; README says tested with clang v10 and gcc v9.3.0 on Linux and clang/MSVC 2019/2022 on Windows, but does not name the compiler for the Ice Lake run (FSE run says 'same compiler' with a Windows path; ryg_rans run was Linux clang) |
| **Adoption** | 30 stars |
| **Last commit** | 2023-05-12 |
| **Links** | [repository](https://github.com/richgel999/sserangecoding) · [benchmark](https://github.com/richgel999/sserangecoding) |

## Verdict

On book1 (768,771 bytes) on a Core i7 1065G7 Ice Lake laptop, the 16-stream SSE 4.1 decoder ran at 552-619 MiB/s (8 rounds of 100 warm-cache decodes, 2.3-2.6 cycles/byte), against 370.3 MB/s decode for Collet's FSE demo and 512.8-565.6 MB/s for ryg_rans exam_simd_sse41 run separately under Linux clang; the range coder's compiler is not named, output was 436,229 bytes versus FSE 437,232 and ryg SIMD rANS 435,626, and FSE's Huffman mode decoded faster at 800.9 MB/s.

## Use it when

- Decode-heavy order-0 byte entropy coding on x86-64 with SSE 4.1, where decode speed matters far more than encode speed (encode is 51.9 MiB/s on the vectorized path).
- You want a range coder rather than ANS because of patent concerns about ANS, the reason the author gives for the project.
- Inputs of tens of kilobytes or more, so the 48-byte stream header (16 lanes x 3 bytes) and the scalar tail are amortized.
- As a reference design for vectorized range decoding with float division and pshufb renormalization, small enough (about 700 lines) to vendor under the Unlicense.

## Skip it when

- Non-x86 targets: the decoder is written with SSE 4.1 intrinsics (_mm_insert_epi32, _mm_mullo_epi32, _mm_shuffle_epi8) and has no scalar or NEON fallback for the vectorized path.
- Encode-bound workloads: the encoder is scalar, buffers 16 std::vector streams plus a per-symbol byte-count array (about one extra byte per input byte) and then swizzles, and the author says it is not optimized.
- You need adaptive or higher-order models: probabilities are a single static 12-bit table per buffer.
- Maximum single-core decode speed: FSE's Huff0 mode decodes book1 faster (800.9 MB/s on the same machine) and SIMD rANS siblings run several times faster; the AVX-2 64-stream port quoted at 1,373 MiB/s is not in the repo.
- Untrusted input without your own bounds slack: the author writes that corruption safety is 'still testing', and the end-of-input guard is miscomputed (see gotchas).

## How it is fast

The decoder's per-symbol division (value / (range &gt;&gt; 12)) is done four lanes at a time with _mm_div_ps on floats, which is exact because state values are kept under 24 bits; the quotient indexes a 4096-entry table packing symbol, low and frequency. Renormalization is branchless: two compare masks per vector form an 8-bit index into precomputed pshufb tables that shift each lane's state and splice in 0, 1 or 2 bytes from one 8-byte load. The encoder runs 16 scalar range coders and then swizzles their bytes into decode order, using the per-symbol byte counts it recorded, so the decoder needs no stream offsets.

## Compared with alternatives

Pick it over ryg_rans or rans-tricks when you want a range coder (no ANS) with SSE 4.1 decode at about 580-620 MiB/s on book1; pick hypersonic-rANS, rans_static or htscodecs when ANS is acceptable and you have AVX2/AVX-512, since they decode several times faster, and FiniteStateEntropy's Huff0 when a slightly larger output is fine.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C++ standard library (std::vector) and x86 intrinsic headers; packagemerge.c is used only by the test app for Huffman size comparisons |
| **Minimum toolchain** | C++11 (CMakeLists sets CMAKE_CXX_STANDARD 11, -O3 -msse4.1); author tested clang 10 and gcc 9.3.0 on Linux and clang, MSVC 2019 and MSVC 2022 on Windows |
| **Platforms** | x86-64 with SSE 4.1 required |
| **Thread safety** | not documented; vrange_init() fills global shuffle tables and must run before any use, after which encode and decode keep their state on the stack or in caller buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- The lookup tables (g_shift_shuf, g_dist_shuf, g_num_bytes, g_byte_shuffle_mask) are declared static in sserangecoder.h, so each translation unit gets its own copy and vrange_init() only fills the copy in sserangecoder.cpp; calling the inline low-level vrange_decode/vrange_normalize helpers from your own .cpp, as the README suggests, would use zeroed tables.
- In vrange_decode(), pSrc_end is computed as pSrc + comp_size after the 48 initial state bytes have been consumed, so the end-of-input checks are 48 bytes too lax and comp_size &gt;= 48 is not checked; on corrupt input the decoder can read past the buffer (the test app's wrapper only checks comp_size &gt;= 48).
- The encoder appends 2 zero padding bytes and the vectorized loop does 8-byte loads, so streams produced elsewhere need the same padding; the output buffer is written through a uint32_t\* cast (4 symbols at a time).
- Frequencies are rescaled to a 4096 total, with every used symbol getting at least 1, so very skewed distributions lose some precision versus 15-16-bit-probability coders.

## Known shortcomings

- Tier C: numbers reproduce; CMakeLists sets -O3 -msse4.1 but the compiler for the Ice Lake run is not named and the baselines run as separate programs; README mixes MiB/s and MB/s.
- vrange_decode computes pSrc_end after consuming the 48 header bytes, so the end guard is 48 bytes too lax and corrupt input overreads despite the README's safety claim; the lookup tables are declared static in the header, so vrange_init fills only sserangecoder.cpp's copy and the inline helpers used from other translation units see zeroed tables; the AVX2 1,373 MiB/s port is not in the repo; 12-bit probabilities. powturbo/TurboBench carries a sserangecoding plugin (issue #2) that could give independent numbers.

## Caveats and trade-offs

Single file (book1), single machine, first-party. Baselines (FSE demo, ryg_rans exam_simd_sse41) were run as separate programs, ryg_rans under Linux/clang while the range coder's compiler is not named. Units differ: the range coder reports MiB/s, ryg_rans labels MiB/s-computed values as MB/s, FSE reports MB/s. The same README shows FSE Huffman mode (-h) decoding faster at 800.9 MB/s and its own AVX-2 port at 1,373 MiB/s, so the SSE 4.1 coder beats only FSE/tANS (about 1.6x) and ryg_rans SIMD rANS (about 1.1x). Encoder not optimized (51.9 MiB/s vectorized-path encode). Last commit 2023-05-12.

Decoder is SSE 4.1 and relies on fast vectorised single-precision division with 24-bit integers (precision loss under 1%). Encoder is slower (51.9 MiB/s vectorised, 137.5 MiB/s plain) because of a byte swizzle step and is not optimised. Order-0 only, 8-bit alphabet. Range coding avoids ANS patent concerns (author's argument).

## Maintenance

Abandoned since 2023-05-12 (85 commits, all three issues closed) but Unlicense and small enough to vendor; it is wired into powturbo's TurboBench as a plugin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows test.cpp output on book1 (577.1-619.1 MiB/s decode, Core i7 1065G7) next to separately run FSE (370.3 MB/s decode) and ryg_rans SIMD (512.8-565.6) outputs; CMakeLists sets -O3 -msse4.1, but the compiler for the headline run is not named and the baselines are not in the repo's harness, so first-party C.
- **Verifier notes:** All claimed numbers present on README; Unlicense LICENSE file confirmed, 30 stars, last commit 2023-05-12 (abandoned is correct at &gt;3 years).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/richgel999/sserangecoding>
  - <https://github.com/richgel999/sserangecoding/commits>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/test.cpp>
- **Sources the enricher read:**
  - <https://github.com/richgel999/sserangecoding>
  - <https://github.com/richgel999/sserangecoding/issues?q=is%3Aissue>
  - <https://github.com/richgel999/sserangecoding/issues/1>
  - <https://github.com/richgel999/sserangecoding/issues/2>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/sserangecoder.h>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/sserangecoder.cpp>
  - <https://raw.githubusercontent.com/richgel999/sserangecoding/HEAD/test.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/richgel999/sserangecoding`) · [data/wave9/enrich/raw/github_com_richgel999_sserangecoding.json](../../../data/wave9/enrich/raw/github_com_richgel999_sserangecoding.json) (enrichment confidence 0.75)

</details>
