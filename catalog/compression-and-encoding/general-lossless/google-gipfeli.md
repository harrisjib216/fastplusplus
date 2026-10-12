# Gipfeli

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Archived Google LZ77 compressor with a light static entropy stage, claimed about 5x faster than zlib.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | Compresses at about 180 MB/s or more and decompresses at about 300 MB/s, typically 5x faster than zlib, with about 30% fewer bytes than other high-speed libraries for text. |
| **Workload** | Single core of a Core i7 in 64-bit mode; workload not specified in the README. |
| **Metric** | throughput |
| **Hardware** | Core i7 (model not stated), single core |
| **Adoption** | 119 stars |
| **Last commit** | 2016-08-16 |
| **Links** | [repository](https://github.com/google/gipfeli) · [benchmark](https://raw.githubusercontent.com/google/gipfeli/HEAD/README) |

## Verdict

The only numbers are the README's first-party claim: about 180 MB/s compression and 300 MB/s decompression on one core of an unnamed Core i7 in 64-bit mode, 'typically 5x faster than zlib', with no workload, compiler, flags or zlib version; the bundled gipfeli_test.cc times Compress/Uncompress over Snappy's test corpus (html, urls.10K, fireworks.jpeg, paper-100k.pdf, Canterbury texts) but no results are published, and lzbench publishes no Gipfeli row.

## Use it when

- Research or comparison work on the speed/ratio space between Snappy/LZ4 and zlib, where Gipfeli is a historical reference point.
- Reading existing Gipfeli-compressed data that some legacy system produced.
- Text-like payloads under 2 GiB where you control both ends, accept an unmaintained format, and have your own round-trip tests on the exact compiler you ship with.

## Skip it when

- Any new production use: archived 2022-07-27, last commit 2016-08-16, and lzbench lists it with 'Decompression file mismatch when compiled with GCC 14.2 using -O3', so round trips fail on a current compiler at the Makefile's own -O3.
- Untrusted compressed input: the decoder has had no fuzzing or maintenance since 2016, and it reads up to 8 bytes past the end of a truncated buffer (see gotchas).
- When you need zlib/gzip/zip interoperability, a checksum, or a documented format: Gipfeli has none of these.
- Inputs of 2 GiB or more: Compress() accepts them and writes an up-to-8-byte length, but GetUncompressedLength() rejects lengths over 4 bytes or of 2^31 and above, so such output can never be decompressed.
- When you simply want speed over zlib: zstd -1 and LZ4 beat its claimed numbers with active maintenance.

## How it is fast

The LZ77 stage is Snappy's design: a 4-byte multiplicative hash (0x1e35a7bd) into a uint16 table of at most 2^15 entries, heuristic match skipping that widens the step after 32 misses, 8-byte word compares to extend matches, and 8/16-byte unaligned copies on decode. Commands are packed into a variable-length bit code (3-bit tag, then 2-6 bit length and 10-16 bit offset), and literals use a fixed per-block code: the 32 most frequent bytes get 6-bit codes, the next 64 get 8-bit codes and the rest 10 bits, with the encoder skipping entropy coding when it would not pay off. No Huffman tree building and no assembly.

## Compared with alternatives

Practically never for new code: Snappy (same LZ77 core, maintained, lzbench 457/976 MB/s vs zlib -1 89 MB/s) or LZ4 covers the speed end, and zstd -1 gives better ratio than Gipfeli's stated target at similar or higher speed. Pick Gipfeli only to decode legacy Gipfeli data or as a historical comparison point.

## Integration

| | |
|---|---|
| **Form** | source-drop (5 .cc files; the Makefile only builds the gipfeli_test benchmark binary, no library target) |
| **Dependencies** | none beyond the C++ standard library |
| **Minimum toolchain** | Pre-C++11-style C++ (uses std::string, NULL, try/catch); no minimum documented; the shipped Makefile uses g++ -O3 -Werror -Wno-strict-aliasing, and lzbench reports wrong output with GCC 14.2 -O3 |
| **Platforms** | Little-endian x86/x86-64 and PowerPC get raw unaligned pointer casts; ARMv7+ and other targets use memcpy-based loads; big-endian support is not documented and the 16-bit command count is read in native byte order |
| **Thread safety** | Documented as not safe for use from multiple threads per Compressor object (it caches LZ77 and command buffers); use one object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness on modern compilers is unresolved: lzbench (2026 README) reports decompression mismatches with GCC 14.2 -O3. The source type-puns char buffers through reinterpret_cast&lt;uint64\*&gt; on x86/PowerPC (UNALIGNED_LOAD64/STORE64), which is undefined behaviour, and the Makefile silences -Wstrict-aliasing; a plausible but untested workaround is -fno-strict-aliasing or -DGIPFELI_NO_UNALIGNED (selects the memcpy path). Issue #6 (decompressed random data of a few hundred KiB not matching the input) is closed with no linked fixing commit.
- Out-of-bounds read on malformed input: in the entropy-coded branch of InternalRawUncompress, ReadBits::Start() does an 8-byte load at ip before the 'ip_end - ip &lt; 8' check, so a truncated stream is over-read by up to 8 bytes before being rejected.
- Size asymmetry: the compressor writes lengths of any size but the decoder caps at 2 GiB - 1, so very large single buffers compress without error and then fail to decompress.
- The public header pulls 'using std::string;' into the global namespace (compression.h) and the benchmark (gipfeli_test.cc) expects Snappy's testdata/ files, which are not in the repository.

## Known shortcomings

- Tier C: usability copyable (the CC-BY testdata named in COPYING is not in the repo). lzbench notes a decompression file mismatch when compiled with GCC 14.2 at -O3.
- lzbench reports round trips fail with GCC 14.2 -O3. Code type-puns through reinterpret_cast uint64 loads and the Makefile hides -Wstrict-aliasing (possible untested fix: -fno-strict-aliasing or -DGIPFELI_NO_UNALIGNED). Issue #6 (random data does not round-trip) closed with no linked fix. Over-read in decompress.cc: ReadBits::Start loads 8 bytes before the ip_end - ip &lt; 8 check, so truncated input is over-read by up to 8 bytes. Compress accepts inputs of 2 GiB or more that the decoder rejects. Not zlib-compatible, no checksum, 16-bit command count in native byte order. Benchmark needs Snappy testdata missing from the repo. Archived 2022.

## Caveats and trade-offs

First-party README claim with no workload, compiler, flags or exact CPU; the README does not say whether the 5x refers to compression or decompression speed, and it concedes Gipfeli does not reach zlib's compression density. Archived by Google on 2022-07-27; last commit 2016-08-16. lzbench lists gipfeli 2016-07-13 under compressors with security issues or no maintenance, noting 'Decompression file mismatch when compiled with GCC 14.2 using -O3', so the code has a correctness problem on current compilers and lzbench publishes no numbers for it. COPYING grants BSD-3-Clause for all code; its note about CC-BY-3.0 and public-domain files refers to a testdata directory that is not in the repository.

Snappy-class speed with an entropy stage; does not reach zlib's density. Written in C++ with no assembly.

## Maintenance

Abandoned (last commit 2016-08-16, archived by Google 2022-07-27) and BSD-3-Clause; small enough to vendor, but known to round-trip incorrectly with GCC 14.2 -O3, so treat it as reference code only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README says Gipfeli compresses at about 180 MB/s or more and decompresses at about 300 MB/s on a single core of a Core i7, 'typically 5x faster than zlib', with no workload, compiler, flags, CPU model or benchmark code: first-party numbers without methodology, so C. lzbench carries Gipfeli only in its unmaintained/security-issues list with no results row.
- **Verifier notes:** Numbers match the README. Usability corrected from mixed to copyable: the repo's top-level file list has no testdata directory, so every shipped file is under the BSD-3-Clause COPYING text. Repo: 119 stars, 19 forks, 22 commits, archived 2022-07-27.
- **Fields the verifier corrected:** `usability`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/README>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/COPYING>
  - <https://github.com/google/gipfeli>
  - <https://github.com/google/gipfeli/commits>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/README>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/COPYING>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/Makefile>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/gipfeli.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/gipfeli-internal.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/gipfeli-internal.cc>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/decompress.cc>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/lz77.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/lz77.cc>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/entropy.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/entropy.cc>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/read_bits.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/stubs-internal.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/compression.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/stream.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/sinksource.h>
  - <https://raw.githubusercontent.com/google/gipfeli/HEAD/gipfeli_test.cc>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/google/gipfeli/issues?q=is%3Aissue>
  - <https://github.com/google/gipfeli/issues/6>
  - <https://github.com/google/gipfeli/issues/11>
  - <https://github.com/google/gipfeli/commits/master>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/google/gipfeli`) · [data/wave9/enrich/raw/github_com_google_gipfeli.json](../../../data/wave9/enrich/raw/github_com_google_gipfeli.json) (enrichment confidence 0.75)

</details>
