# VTEnc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> C codec for sorted unsigned integer lists that beats Delta+FastPFor on compression ratio, and on speed only for clustered data.

| | |
|---|---|
| **Beats** | FastPFor (Delta+FastPFor128/256), Delta+BinaryPacking, Delta+VariableByte, Delta+VarIntGB |
| **Claimed result** | ts.txt: VTEnc/1 decode 7.32 G/s vs Delta+FastPFor128 3.88 G/s, Delta+FastPFor256 3.61 G/s, Delta+VariableByte 3.43 G/s; ratio 26,622 vs 250.2 for FastPFor128. gov2.sorted: VTEnc/1 ratio 8.29 vs Delta+FastPFor128 6.21, but decode 210.99 M/s vs 615.64 M/s (slower). |
| **Workload** | Compression ratio and encode/decode speed on sorted lists: ts.txt timestamps and gov2.sorted 32-bit docid lists, Core i7-6700HQ laptop. |
| **Metric** | other |
| **Compiler and flags** | GCC, version not stated; harness Makefile: g++ -Wall -O3 -std=c++11; VTEnc Makefile: gcc -std=c99 -DNDEBUG -O3 -march=native -mtune=native; SIMDCompressionAndIntersection built with its own makefile; Google Benchmark v1.6.1 in CMake Release |
| **Adoption** | 37 stars |
| **Last commit** | 2022-12-01 |
| **Links** | [repository](https://github.com/vteromero/VTEnc) · [benchmark](https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/README.md) |

## Verdict

The author's integer-compression-benchmarks repo (Google Benchmark, VTEnc v0.3.0 against Lemire's SIMDCompressionAndIntersection codecs, i7-6700HQ laptop, GCC -O3, compiler version unstated) reports VTEnc/1 decoding ts.txt timestamps at 7.32 G/s vs 3.88 G/s for Delta+FastPFor128, with a ratio of 26,622 vs 250. On gov2.sorted docids it gets the best ratio (8.29 vs 6.21) but decodes about 2.9x slower (211 vs 616 M/s, derived from page data); speeds are input bytes per second.

## Use it when

- Archiving or transmitting sorted 32/64-bit ID lists, timestamps or posting lists where compressed size matters more than decode speed (gov2 docids: ratio 8.29 vs 6.21 for Delta+FastPFor128).
- Sorted data with long runs, duplicates or dense clusters (timestamp logs), where it beat every baseline on both ratio and decode speed in the author's test.
- Cases where you can tune the ratio/speed trade-off: raising min_cluster_length to 16 or more moved gov2 decode from 211 M/s to 829 M/s and above at the cost of ratio.
- Small C or C++ projects that want a dependency-free, MIT-licensed codec with a few source files.

## Skip it when

- Decode-throughput-bound query processing over scattered docids: on gov2 VTEnc/1 decoded at 211 M/s vs 616 M/s for Delta+FastPFor128, 2.33 G/s for Delta+BinaryPacking and 2.97 G/s for Delta+VarIntGB.
- Unsorted data or random access into a compressed block: it only handles sorted input and decodes a whole block at once.
- Long-lived storage formats: the README says the format may change on any 0.x version, and the latest release is v0.3.0 (March 2022) with later fixes only on master.
- Untrusted compressed input: the decoder's bounds checks on the input buffer are assert() calls, which the default -DNDEBUG build removes.
- Windows: the README says it was tested only on Linux and macOS.

## How it is fast

It walks the values' binary trie top-down: for each cluster of values sharing the same high bits it finds, by branchless binary search over the sorted input, how many have a 0 at the next bit position and writes that count in ceil(log2(cluster length + 1)) bits, then descends into both halves with an explicit fixed-size stack (no recursion). Clusters no longer than min_cluster_length emit their remaining low bits directly, and for sets with no duplicates a full subtree can be skipped entirely. On highly regular data such as timestamps the high levels collapse into a few counts, so encode does O(log n) work per split rather than touching every element, which is why ts.txt shows extreme ratio and encode figures; on scattered docids it costs one bit-field read per trie node and is slower than SIMD bit-packing.

## Compared with alternatives

Pick VTEnc over FastPFor, SIMDCompressionAndIntersection or simdcomp when compressed size of sorted lists is the priority, or when the data is clustered like timestamps; for decode throughput on ordinary posting lists, FastPFor, Stream VByte or TurboPFor are faster. ds2i's partitioned Elias-Fano is the better-studied size/speed choice when you also need random access or skipping.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99; GCC builtins (__builtin_expect, __builtin_clz) used via compiler.h; Makefile defaults to gcc -O3 -march=native |
| **Platforms** | Linux and macOS tested per README; portable C with little-endian/big-endian handling in mem.h; no SIMD |
| **Thread safety** | not documented; each call keeps its state on the stack plus the handler's out_size, so one vtenc handler per thread is the safe assumption |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoder buffer: bswriter writes 8 bytes at a time and checks the end of the output buffer only with assert(), so in a -DNDEBUG build an out_cap below vtenc_max_encoded_sizeNN(n) can overflow the buffer (inferred from bitstream.h). Always size the output buffer with vtenc_max_encoded_sizeNN.
- Unsorted input is not checked: the header says you may still get VTENC_OK with a wrong stream. The decoder also needs the exact element count from the caller.
- Decoder stack: the decoder pushes clusters down to bit position 0 into a fixed 64-entry stack (DEC_STACK_MAX_SIZE 64). By my reading of decode_generic.h, a 64-bit sequence that splits at every bit level (for example 0, 1, 2, 4, ..., 2^63) needs 65 entries, which would overflow by one. This is inferred from the code and was not reproduced; 8/16/32-bit sequences stay well within the limit.
- PR #40 (Nov 2022, after the benchmarked v0.3.0) fixed a bitstream-writer corruption when more than 63 bits were buffered and cut the maximum single read/write from 57 to 56 bits. Writes that large only seem to arise with 64-bit values, so the 32-bit benchmark looks unaffected, but anyone on v0.3.0 should build from master.

## Known shortcomings

- Tier C: numbers come from the author's own integer-compression-benchmarks (i7-6700HQ, g++ -O3 harness, gcc -O3 -march=native for VTEnc, no compiler version). Speeds are input bytes per second and the ts.txt encode figure of 102.28 GB/s exceeds memory bandwidth (bisection skipping duplicate runs, specific to that data); on gov2.sorted only VTEnc/16+ beats FastPFor decode; the encode benchmark has no output check. Last commit 2022-12-01, abandoned.
- PR #40 (Nov 2022, after the benchmarked v0.3.0) fixed bitstream corruption past 63 buffered bits and cut the max read/write from 57 to 56 bits; the 32-bit benchmark looks unaffected, but no release carries the fix. Decoder input and encoder output bounds checks are assert() only (compiled out under -DNDEBUG), so it is unsafe on untrusted input or an undersized out_cap; a decoder stack overflow is possible (DEC_STACK_MAX_SIZE 64 where 65 is needed for a 64-bit sequence splitting at every bit level; inferred from code, not reproduced); unsorted input is unchecked.

## Caveats and trade-offs

Speed win holds only on the highly regular timestamp file (ts.txt). On gov2.sorted, VTEnc/1 is slower than every bit-packing and varint baseline but compresses best; only VTEnc/16+ approaches or beats FastPFor decode speed (VTEnc/16 829.11 M/s vs FastPFor256 621.17 M/s, at a slightly lower ratio of 6.10 vs 6.13), and Delta+BinaryPacking/VarIntGB remain faster. Speeds are bytes of uint32 input per second (Google Benchmark SetBytesProcessed), so the ts.txt encode at 102.28 G/s exceeds the laptop's memory bandwidth; VTEnc's bisection over sorted runs with many duplicates evidently skips most input, so this is an algorithmic effect specific to that data, not a general throughput figure (inference from the code, not stated by the author). The encode benchmark does not check output, though the decode benchmark checks equality after decoding. The author runs the shootout; numbers were taken with VTEnc v0.3.0 in 2022. The library is marked as early-stage with no format stability. Last commit 2022-12-01. Tangential to bit-packing, kept because it is compared directly to FastPFor/BinaryPacking/VByte.

Targets sorted unsigned lists (8/16/32/64-bit); wins on compression ratio and on clustered data like timestamps, loses decode speed on gov2 docids; README warns format may change between versions.

## Maintenance

Abandoned: last commit 2022-12-01 and last release v0.3.0 in March 2022, with no open issues. It is MIT-licensed, has no dependencies and consists of about 20 C source and header files at the repo root, so it is easy to vendor, but the format is not stable and the release lacks the later bitstream fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The integer-compression-benchmarks README tables, run by the VTEnc author, compare VTEnc against Delta+FastPFor128/256, BinaryPacking, VariableByte and VarIntGB from Lemire's SIMDCompressionAndIntersection on an i7-6700HQ. The harness code is public (timestamps.cc, gov2.cc, common.cc on Google Benchmark), and the Makefiles give g++ -O3 -std=c++11 for the harness and gcc -O3 -march=native for VTEnc, but no compiler version is stated anywhere. That is first-party code with partial methodology, so C (same precedent as other entries missing a compiler version).
- **Verifier notes:** All claimed_speedup numbers match the integer-compression-benchmarks README tables. MIT license and 37 stars confirmed on github.com; last commit 2022-12-01 is over 3 years old, so maintenance_status is changed from stale to abandoned. The benchmark repo (5 stars, MIT) was last updated 2022-03-18.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/vteromero/integer-compression-benchmarks>
  - <https://github.com/vteromero/integer-compression-benchmarks/commits>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/timestamps.cc>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/common.cc>
  - <https://github.com/vteromero/VTEnc>
  - <https://github.com/vteromero/VTEnc/commits>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/README.md>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/vteromero/VTEnc>
  - <https://github.com/vteromero/VTEnc/commits>
  - <https://github.com/vteromero/VTEnc/issues?q=is%3Aissue>
  - <https://github.com/vteromero/VTEnc/pull/40>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/README.md>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/vtenc.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/encode_generic.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/decode_generic.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/encode.c>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/decode.c>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/common.c>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/common.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/bitstream.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/countbits.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/internals.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/stack.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/mem.h>
  - <https://raw.githubusercontent.com/vteromero/VTEnc/HEAD/compiler.h>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/vteromero/vtenc`) · [data/wave9/enrich/raw/github_com_vteromero_vtenc.json](../../../data/wave9/enrich/raw/github_com_vteromero_vtenc.json) (enrichment confidence 0.75)

</details>
