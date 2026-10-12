# utf8lut

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> SSSE3 lookup-table UTF-8/UTF-16/UTF-32 transcoder, 7-13x faster than its own Hoehrmann-DFA scalar path on BMP-heavy text.

| | |
|---|---|
| **Beats** | scalar slow path of the same library (-b=0), a scalar UTF-8 to UTF-16 and UTF-16 to UTF-8 converter |
| **Claimed result** | Fast path (-b=3 -m=2) vs scalar slow path, cycles per byte (core conversion by rdtsc): random decode 1.65 vs 15.3 (about 9.3x), random encode 0.74 vs 9.9 (about 13x), fb2 decode 1.00 vs 9.10 (about 9.1x), fb2 encode 0.68 vs 4.89 (about 7.2x); ratios derived from page data. |
| **Workload** | Converting about 1 MB buffers from RAM to RAM, UTF-8 to UTF-16 (decode) and UTF-16 to UTF-8 (encode), on a random code-point dataset (33% each of 1, 2 and 3 byte) and the Russian novel 'War and Peace' in fb2 format; CPU cycles per byte. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 1600, single core, 3.4 GHz |
| **Compiler and flags** | Not stated for the table. The sample benchmark commands run FileConverter_msvc.exe, which scripts/build_msvc_file_conv.cmd builds with cl /O2 /Oi /EHsc /MD /D NDEBUG /D TIMING (MSVC version not given); non-MSVC builds need -mssse3 -std=c++11. |
| **Adoption** | 11 stars |
| **Last commit** | 2020-04-19 |
| **Links** | [repository](https://github.com/stgatilov/utf8lut) · [benchmark](https://github.com/stgatilov/utf8lut) |

## Verdict

The README's FileConverter run on a Ryzen 1600 (single core, 1 MB buffer converted RAM to RAM repeatedly, validating mode in both rows) measured the SSSE3 fast path at 1.65 vs 15.3 cycles/byte (random 1-3 byte code points, decode), 0.74 vs 9.9 (random, encode), 1.00 vs 9.10 (War and Peace fb2, decode) and 0.68 vs 4.89 (fb2, encode) against its own scalar path (Hoehrmann DFA decoder, branchy scalar encoder); the compiler is only implied as MSVC (/O2 /Oi), version not stated, and no incumbent such as ICU or iconv is in that table.

## Use it when

- Bulk conversion of large buffers (hundreds of KB and up) of BMP text dominated by 2- and 3-byte characters (Cyrillic, Greek, CJK) on x86 with SSSE3
- Validating UTF-8 to UTF-16 conversion at roughly 1-1.7 cycles per input byte (README, Ryzen 1600) where a scalar converter's 5-15 cycles per byte is the bottleneck
- Studying or borrowing the movemask-indexed pshufb lookup-table technique; core/DecoderProcess.h and core/EncoderProcess.h are compact and BSL-1.0
- Projects that need an iconv-shaped C API for UTF-8 to and from UTF-16LE/UTF-32LE only and can live with its documented deviations

## Skip it when

- ASCII-heavy or Latin-script text: there is no ASCII shortcut in the default 3-byte mode (each step emits at most 8 characters per 16-byte load), and Lemire and Mula's paper reports u8u16 and utf8sse4 beating it on English, French, German and other European-language files, utf8sse4 sometimes by 2x (search snippet only, paper blocked here)
- Text with many supplementary-plane characters (emoji, historic scripts): non-BMP code points always take the scalar slow path, and the README says over 99% of characters must stay on the fast path for good speed
- ARM, other non-x86 targets, or code that must use AVX2/AVX-512: SSSE3 only, no runtime dispatch, no portable fallback build
- Short strings: inputs under 16 bytes run entirely on the scalar path, and the 4-stream decoder only engages from 128 bytes; the first call also pays for building the 2 MiB lookup table
- Production code that needs maintenance: last commit 2020-04-19, no releases, no issues ever filed, one unmerged typo PR from 2022

## How it is fast

Decode takes the movemask of continuation bytes in a 16-byte SSSE3 register (15 bits after dropping bit 0) and uses it to index a 32768-entry table (10609 reachable entries) holding pshufb masks, the bytes consumed and the code units produced; pshufb + pmaddubsw then assemble up to 8 UTF-16 code units per step, and validation compares header bits, overlong minimums and the surrogate range against per-entry masks. Encode uses a 256-entry table indexed by a code-unit length mask. Anything the fast path cannot handle (non-BMP characters, invalid bytes) drops to Bjoern Hoehrmann's DFA decoder or a branchy scalar encoder for that 16-byte block. The benchmarked configuration (SpeedMult = 4) decodes 4 interleaved streams over quarters of the buffer to hide latency, then copies the 4 outputs into one buffer, and unrolls the encoder 4x.

## Compared with alternatives

Among the catalogued converters, encoding_rs (C API via encoding_c) has ASCII fast paths and is about 7x ICU on English UTF-8/UTF-16, and xutf and Parabix are measured against simdutf, the current reference SIMD transcoder; pick utf8lut only for SSSE3-era x86 targets with BMP-heavy non-Latin text, or to study the LUT method. For grapheme, normalization or collation work (ICU, ICU4X, uni-algo, libutf, ugrapheme) it is not a substitute.

## Integration

| | |
|---|---|
| **Form** | source-drop (add src/ to the include path and compile the core, buffer and message .cpp files; optional iconv shared library) |
| **Dependencies** | none (SSE2/SSSE3 intrinsics; scalar decoder embeds Hoehrmann's MIT-licensed DFA table) |
| **Minimum toolchain** | C++11 with -mssse3 on GCC/Clang/MinGW; MSVC build scripts use cl /O2 /Oi (version not documented); CMake 3.2.1 for tests and samples |
| **Platforms** | x86 and x86-64 with SSSE3 required; Windows and Linux build scripts |
| **Thread safety** | Not documented. One processor object per thread (processors hold buffers and state). The decoder and encoder LUT singletons are built lazily on first use with no synchronization, and the pointer is published before the table is filled, so warm them up from one thread before converting in parallel. |
| **Drop-in for the baseline** | partial — the iconv shared library mimics iconv for UTF-8 to and from UTF-16LE/UTF-32LE only, returns 1 instead of a character count, and may stop with E2BIG while up to about 64 KB of input remain unless the output buffer is sized with its extension call; the C++ API is its own |

## Gotchas

- The README table used FileConverter's default SpeedMult = 4 (4-stream decoder, 4x-unrolled encoder), but ProcessorSelector&lt;...&gt;::WithOptions&lt;&gt; and the README usage example default to SpeedMult = 1; pass SpeedMult = 4 explicitly to get the measured configuration (the multi-stream processor does not support error correction).
- Benchmark normalisation: the core rdtsc timer divides by input bytes, so encode cells are cycles per UTF-16 byte, not per UTF-8 byte as the README says; for the random set the two sizes match, but for the fb2 file (Cyrillic plus ASCII XML markup) encode and decode cells are not directly comparable, and rdtsc counts TSC reference ticks rather than core cycles. Both rows share the normalisation, so the fast-vs-scalar ratios stand.
- The README numbers date from 2018 (readme.md added 2018-04-09, never re-measured); the 4-stream decoder was changed on 2019-07-27 to keep multistreaming past supplementary characters, and that code reads the uninitialised ok1..ok3 flags if stream 0 fails on its first 16-byte block (undefined behaviour, normally harmless because the scalar fallback still decodes correctly).
- cmFast and cmFull skip validation, so invalid UTF-8 (or a non-BMP character in cmFast) is undefined behaviour; keep the default cmValidate for untrusted input. The validating decoder LUT is 32768 x 64 bytes = 2 MiB (1 MiB without validation), allocated with _mm_malloc on first use and never freed, and it competes for L2/L3 with the rest of the program.

## Known shortcomings

- Only baseline is its own scalar slow path (-b=0); compiler only implied (MSVC script, /O2 /Oi); 1 MB warm-cache loop; the Lemire-Mula SPE 2022 paper (snippet only) shows u8u16 and utf8sse4 often faster. Filed under unicode-utf8. Abandoned 2020.
- Ratios stand. Harness flaws: the encode cells are cycles per UTF-16 byte, not per UTF-8 byte as the README says (fb2 encode and decode are not comparable); the table ran FileConverter's SpeedMult = 4 while the library default and README example use SpeedMult = 1; the numbers date from 2018 and were never re-measured. Code defects: the LUT singleton is published before it is filled (a thread race on first use); the 4-stream decoder reads uninitialised ok1..ok3 flags (UB, benign). The scalar baseline is a Hoehrmann DFA; per the Lemire-Mula paper (snippet only) u8u16 and utf8sse4 beat it on European text and it has no ASCII fast path.

## Caveats and trade-offs

The comparison is against the library's own scalar slow path (-b=0, which forces validate mode), not against iconv, ICU or another incumbent; the fast-path row uses -m=2, which is cmValidate, so both rows validate. Each run converts one \~1 MB array from RAM to RAM repeatedly, so the large lookup table stays warm; the README warns it barely fits in cache and that performance depends on the code-point length mix. The compiler for the table is only implied (MSVC build of FileConverter, version unstated). The README's blog article with broader comparisons is on dirtyhandscoding.github.io, which is blocked here. Per search snippets only, Lemire and Mula's peer-reviewed 'Transcoding Billions of Unicode Characters per Second with SIMD Instructions' (Software: Practice and Experience 52(2), 2022; arXiv 2109.10433, blocked here) benchmarks utf8lut beside ICU, LLVM, u8u16 and utf8sse4 and reports that u8u16 and utf8sse4 often beat it on European-language text because utf8lut has no ASCII fast path; utf8lut-versus-ICU numbers were not seen. README calls it mainly a proof of concept. Repo migrated from Bitbucket and last changed in 2020. [retier] The comparison is against the library's own scalar slow path (-b=0, which forces validate mode), not iconv, ICU or another incumbent; the fast-path row uses -m=2 (cmValidate), so both rows validate. The table used FileConverter's SpeedMult = 4 (4-stream decoder, 4x-unrolled encoder) while ProcessorSelector&lt;...&gt;::WithOptions&lt;&gt; and the README usage example default to SpeedMult = 1, so pass SpeedMult = 4 explicitly to get the measured configuration (the multi-stream processor does not support error correction). Normalisation: the core rdtsc timer divides by input bytes, so the encode cells are cycles per UTF-16 byte, not per UTF-8 byte as the README says; for the random set the sizes match, but for the fb2 file (Cyrillic plus ASCII XML markup) the encode and decode cells are not directly comparable, and rdtsc counts TSC reference ticks; both rows share the normalisation, so the fast-vs-scalar ratios stand. Each run converts one \~1 MB array from RAM to RAM repeatedly, so the 2 MiB validating LUT (1 MiB without validation, allocated with _mm_malloc on first use and never freed) stays warm; the README warns it barely fits in cache and that performance depends on the code-point length mix. The numbers date from 2018 (readme.md added 2018-04-09, never re-measured); the 4-stream decoder was changed on 2019-07-27 and reads uninitialised ok1..ok3 flags if stream 0 fails on its first block (UB, normally harmless); the LUT singleton pointer is published before the table is filled (a race on first concurrent use). cmFast and cmFull skip validation, so invalid UTF-8 is undefined behaviour. Compiler only implied (MSVC build of FileConverter). The scalar baseline is a Hoehrmann DFA; the Lemire-Mula paper (snippet only) says u8u16 and utf8sse4 beat utf8lut on European text and it has no ASCII fast path.

x86 with SSSE3 only; a large lookup table that barely fits the CPU cache, so speed depends on the code-point length distribution (uniform random is the worst case); the fast path needs more than 99% of characters handled to pay off; non-BMP characters use the slow path; the iconv-style interface deviates from the spec.

## Maintenance

Abandoned since 2020 (migrated from Bitbucket, author calls it a proof of concept) but BSL-1.0 and about 20 source files with fuzz-style correctness tests, so it is easy to vendor or mine for the technique; for production pick a maintained SIMD transcoder with ASCII fast paths and runtime dispatch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (Ryzen 1600, rdtsc cycles per byte) compares the SSSE3 fast path against the library's own scalar slow path (-b=0) using the public FileConverter demo (src/tests/FileConverter.cpp); the compiler for the table is only implied by the FileConverter_msvc.exe sample commands, with no MSVC version, and the baseline is the project's own fallback rather than an incumbent, so it stays first-party C.
- **Verifier notes:** All four cycles-per-byte pairs match the README and the derived ratios (9.3x, 13x, 9.1x, 7.2x) are correct. Metadata checked on github.com: BSL-1.0, 11 stars, 2 forks, last commit 2020-04-19 (abandoned). It is a UTF-8/UTF-16 transcoder, so a category override to wave 3's unicode-utf8 (with the matching domain override) would fit better than simd-intrinsics-libraries; the Lemire-Mula SPE paper could support a retier against ICU if it can be opened.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/stgatilov/utf8lut>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/readme.md>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/scripts/build_msvc_file_conv.cmd>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/tests/FileConverter.cpp>
  - <https://github.com/stgatilov/utf8lut/commits/master>
- **Sources the enricher read:**
  - <https://github.com/stgatilov/utf8lut>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/readme.md>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/tests/FileConverter.cpp>
  - <https://github.com/stgatilov/utf8lut/tree/master/src>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/iconv/iconv.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/ProcessorSelector.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/DecoderLut.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/DecoderLut.cpp>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/DecoderProcess.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/EncoderLut.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/EncoderProcess.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/ProcessTrivial.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/core/Dfa.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/base/Timing.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/base/Timing.cpp>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/base/PerfDefs.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/BufferDecoder.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/BufferEncoder.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/BaseBufferProcessor.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/AllProcessors.cpp>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/buffer/ProcessorPlugins.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/message/MessageConverter.h>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/src/message/MessageConverter.cpp>
  - <https://github.com/stgatilov/utf8lut/tree/master/scripts>
  - <https://github.com/stgatilov/utf8lut/tree/master/data>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/scripts/measure.py>
  - <https://raw.githubusercontent.com/stgatilov/utf8lut/HEAD/scripts/build_gcc_file_conv.sh>
  - <https://github.com/stgatilov/utf8lut/pulls>
  - <https://github.com/stgatilov/utf8lut/issues?q=is%3Aissue>
  - <https://github.com/stgatilov/utf8lut/commits/master>
  - <https://github.com/stgatilov/utf8lut/commits/master/readme.md>
  - <https://github.com/stgatilov/utf8lut/commit/c47a8c7>
  - <https://raw.githubusercontent.com/simdutf/simdutf/HEAD/README.md>
  - WebSearch snippets for arXiv 2109.10433 (Lemire and Mula, Software: Practice and Experience 52(2), 2022); arxiv.org and r-libre.teluq.ca returned ENOTFOUND here
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/stgatilov/utf8lut`) · [data/wave13/enrich/raw/github_com_stgatilov_utf8lut.json](../../../data/wave13/enrich/raw/github_com_stgatilov_utf8lut.json) (enrichment confidence 0.75)

</details>
