# Inflate++ (inflatecpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small C++ one-shot zlib/gzip/raw-deflate decoder; a port of em_inflate, about 1.1-1.3x faster than zlib 1.2.11 inflate.

| | |
|---|---|
| **Beats** | zlib inflate 1.2.11 |
| **Claimed result** | zlib bitstream: zlib inflate 1.2.11 134,245 us (100%); Inflate++ with checksum 118,399 us (91%); without checksum 110,238 us (85%). gzip bitstream: zlib 465,567 us (100%); Inflate++ with checksum 362,133 us (87%); without checksum 265,462 us (65%). About 1.13x (zlib) and 1.29x (gzip) faster with checksum, 1.22x and 1.75x without (derived from page data). |
| **Workload** | Decompress a zlib stream of a large raw texture (60,132,846 bytes compressed to 25,614,357) and a gzip archive (147,120,395 bytes compressed to 53,625,384), memory to memory; time in microseconds. |
| **Metric** | throughput |
| **Adoption** | 22 stars |
| **Last commit** | 2021-03-08 |
| **Links** | [repository](https://github.com/artexety/inflatecpp) · [benchmark](https://github.com/artexety/inflatecpp) |

## Verdict

First-party README timings, no CPU, compiler, flags or harness: on a 25.6 MB zlib stream, 118 ms with Adler-32 check versus 134 ms for zlib 1.2.11 inflate (1.13x), and on a 53.6 MB gzip file 362 ms versus 466 ms (1.29x), with the checksum-off rows not like-for-like. The README's percentage column does not match its own times, and em_inflate's README reports almost the same ratios (89%/82%, 84%/64%) on different files, so the numbers mostly characterize the em_inflate design.

## Use it when

- Unpacking whole zlib or gzip assets (textures, level data) that are already fully in memory, where the decompressed size is known or bounded.
- Builds that want a few hundred lines of C++ with no zlib dependency and only need decompression of trusted input.
- As a readable reference for how a table-driven one-shot inflate works, to study or adapt.

## Skip it when

- Any stream containing stored (type 0) blocks: CopyStored reads the length's low byte twice (GetInBlock()[0] in both halves), so most stored blocks fail the LEN/NLEN check and the call returns -1. em_inflate reads [0] and [1] correctly, so this bug was introduced by the port.
- Untrusted input: stored-block memcpy does not check the input end (inherited from em_inflate), literal/length symbols 286-287 index past the 29-entry kMatchLenCode table, and distance symbols 30-31 map to offset 0; no fuzzing or tests exist in the repo.
- Streaming, inputs or outputs of 4 GiB or more (sizes are unsigned int), multi-member gzip files, or zlib streams with a preset dictionary.
- When speed is the point: libdeflate, zlib-ng and Wuffs are maintained, fuzzed and faster than zlib 1.2.11 by wider margins than these numbers show.
- Projects that need clean licensing: see the gotchas about the zlib-licensed origin.

## How it is fast

The code is a near line-by-line C++ translation of Emmanuel Marty's em_inflate (2019, zlib license): a 64-bit LSB-first bit buffer, a 10-bit direct lookup table for short Huffman codes with a canonical-code walk for longer ones (the bit-reversal trick credited to Eric Biggers), and length/distance base-plus-extra-bits values folded into the decode tables so each symbol needs one table read. Matches with distance of at least 16 are copied in 16-byte memcpy chunks with overshoot into a reserved tail. Because the whole output is one flat buffer, there is no 32 KiB sliding window to manage, which is where most of the gain over zlib's streaming inflate comes from; skipping the Adler-32/CRC-32 check removes another 5-25% of the time in the README's numbers.

## Compared with alternatives

Rarely: for one-shot in-memory deflate decoding, libdeflate is faster and maintained, Wuffs is memory-safe by construction, and zlib-ng is a drop-in. Prefer the upstream emmanuel-marty/em_inflate (C, zlib license) if you specifically want this tiny decoder.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++11 (uses constexpr and = default); no standard flag set in the Makefile |
| **Platforms** | Little-endian targets; the 64-bit bit buffer is enabled on x86-64 and aarch64, 32-bit elsewhere. Build scripts are build.bat plus a Makefile that calls g++ with no -O flag. |
| **Thread safety** | Not documented; Feed keeps all state in locals and reads only constexpr tables, so separate calls on separate buffers look safe. |
| **Drop-in for the baseline** | partial: decodes the same zlib/gzip/deflate formats as zlib inflate, but through a different one-shot API with a caller-sized output buffer, and stored blocks currently fail |

## Gotchas

- Licensing: the source is a translation of em_inflate (Copyright 2019 Emmanuel Marty, zlib license) but ships under MIT, credits only Mark Adler and Stephen Brumme, and drops Marty's notice, which the zlib license says may not be removed. Treat the code as zlib-licensed em_inflate and keep Marty's notice if you vendor it, or use em_inflate itself.
- bit_reader.cc writes '#ifdef defined(_M_X64) || defined(__x86_64__)' where em_inflate has '#if defined(...)'; '#ifdef' takes only a macro name, so the intended 32-bit unaligned refill is not selected as written and compilers warn about extra tokens.
- Errors come back as (unsigned int)-1, so a test against -1 works but a test for a negative value does not; gzip's ISIZE trailer field is never checked, and the checksum is only verified when the fifth argument is true.
- crc32_4bytes and the x86 refill path cast byte pointers to unsigned int\*, which relies on unaligned loads and little-endian order.

## Known shortcomings

- Tier C: README numbers reproduce (1.13x zlib, 1.29x gzip with checksum, derived from page data) but the README's percent column disagrees with its own times (78% shown as 87%). Last commit 2021-03-08, abandoned.
- A near line-by-line C++ port of emmanuel-marty/em_inflate (zlib license) relabelled MIT with Marty's notice dropped, which the zlib license forbids; the README ratios (89/82%, 84/64%) match em_inflate's own, so the numbers describe em_inflate's design. Port bug: CopyStored reads GetInBlock()[0] twice for LEN, so most stored blocks fail with -1 (em_inflate reads [1]); bit_reader.cc has '#ifdef defined(...)' so the intended 32-bit refill path is never selected; no input bounds check on the stored memcpy; symbols 286-287 read past kMatchLenCode; the Makefile has no -O flag; no tests. Prefer em_inflate (seed candidate).

## Caveats and trade-offs

No CPU, compiler, flags or benchmark harness; two inputs only. The README's percentage column does not match its own times (e.g. 362,133/465,567 is 78%, not 87%; 265,462/465,567 is 57%, not 65%), so the table was edited carelessly. The 'without checksum' rows skip verification that zlib performs, so they are not like-for-like. Baseline zlib 1.2.11 is old; zlib-ng and libdeflate are far faster than both. Windows-only build script; no tests in repo.

Single-call, memory-to-memory decompressor under 1000 lines of C++ plus about 250 lines of Adler-32; no streaming API mentioned.

## Maintenance

Abandoned since March 2021 (54 commits, 1 closed issue, no tests); labeled MIT but derived from zlib-licensed em_inflate, and it carries a stored-block decoding bug that em_inflate does not have.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows first-party timings against zlib inflate 1.2.11 on two inputs, with no benchmark harness, CPU, compiler or flags stated, so C.
- **Verifier notes:** Numbers match the README times exactly; the record's derived 1.1-1.15x understated the gzip case, corrected. Metadata checked: MIT, 22 stars, not fork/archived, last commit 2021-03-08 (abandoned).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/artexety/inflatecpp>
  - <https://github.com/artexety/inflatecpp/commits>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/artexety/inflatecpp>
  - <https://github.com/artexety/inflatecpp/tree/main/source>
  - <https://github.com/artexety/inflatecpp/commits/main>
  - <https://github.com/artexety/inflatecpp/issues?q=is%3Aissue>
  - <https://github.com/artexety/inflatecpp/issues/1>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/build.bat>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/decompressor.h>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/decompressor.cc>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/bit_reader.h>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/bit_reader.cc>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/huffman_decoder.h>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/huffman_decoder.cc>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/adler32.h>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/adler32.cc>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/crc32.h>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/source/crc32.cc>
  - <https://raw.githubusercontent.com/artexety/inflatecpp/HEAD/example/Application.cc>
  - <https://github.com/emmanuel-marty/em_inflate>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/lib/em_inflate.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/artexety/inflatecpp`) · [data/wave9/enrich/raw/github_com_artexety_inflatecpp.json](../../../data/wave9/enrich/raw/github_com_artexety_inflatecpp.json) (enrichment confidence 0.8)

</details>
