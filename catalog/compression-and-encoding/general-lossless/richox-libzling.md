# libzling

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Small C++ ROLZ + Huffman compressor (Baidu, archived) that compresses about 3x faster than zlib -6 with a better ratio.

| | |
|---|---|
| **Beats** | zlib (gzip) |
| **Claimed result** | README: libzling e0 encodes enwik8 in 2.208 s versus gzip 6.502 s (about 2.9x, derived from page data) with output 31,456,189 versus 36,518,322 bytes; README headline says 3 times as fast as gzip on compressing with much better ratio and decompression speed. lzbench 2.4: zling -0 86.1 MB/s compress at 29.72% versus zlib 1.3.2 -6 at 26.8 MB/s and 32.19% (about 3.2x, derived). |
| **Workload** | Compression of enwik8 (100,000,000 bytes) in the README, and silesia.tar in lzbench 2.4. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; README run on Intel Xeon E5-2620 v3 2.40 GHz, Linux 2.6.32 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 89 stars |
| **Last commit** | 2018-10-12 |
| **Links** | [repository](https://github.com/richox/libzling) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P at 3.2 GHz, silesia.tar) measures zling -0 at 86.1 MB/s compression and 183 MB/s decompression with output 29.72% of input, against zlib 1.3.2 -6 at 26.8 / 314 MB/s and 32.19%: about 3.2x faster compression and 0.58x the decode speed. The author's README run on a Xeon E5-2620 v3 shows enwik8 compressed by e0 in 2.208 s versus gzip's 6.502 s (31.46 MB versus 36.52 MB output), with decode at 1.043 s versus 1.089 s.

## Use it when

- Offline or batch compression of text-like data (logs, enwik-style text, tarballs) where compression speed matters more than decompression speed and you control both ends of the format.
- Replacing zlib -6 when you want roughly 3x faster compression and about 2.5 percentage points smaller output (29.72% vs 32.19% of silesia.tar in lzbench 2.4).
- Studying or vendoring a compact ROLZ implementation (about 1,000 lines of C++ in src/) under BSD-3-Clause terms.

## Skip it when

- Untrusted input: AFL fuzzing found decompression crashes (issue #10, disclosed 2015), the coder was rewritten in 2018 after the 2015 fuzz fixes, and Decode() never checks its read position against the block's stated compressed length.
- Big-endian targets: issue #12 reports round-trip data corruption on POWER8 ppc64, never fixed, and lzbench disables it on big-endian PowerPC.
- Decompression-heavy workloads: lzbench 2.4 measures 183 MB/s decode against zlib -6 at 314 MB/s; zstd 1.5.7 -3 reaches 31.37% with 240 MB/s compression and 1151 MB/s decompression in lzbench's 4 MB-block one-thread table, which beats zling on decode by about 6x for a ratio within 2 points.
- Anything needing gzip/zlib interoperability, streaming of small messages, or a maintained dependency: the repo is archived and the author points users to richox/orz.
- Memory-constrained use: the encoder allocates a 16 MB input block plus about 10 MB of ROLZ buckets (256 x \~40 KB), and the decoder about 16 MB plus 4 MB.

## How it is fast

It uses order-1 ROLZ (reduced-offset Lempel-Ziv): for each preceding byte it keeps a 4096-entry bucket of recent positions with an 8192-slot hash, so a match is coded as a short bucket index instead of a full offset. Levels 0-4 only change match-search depth (2 to 16) and lazy-matching depth. Literals pass through a per-context move-to-front transform, and 256 KB ROLZ chunks are entropy-coded with two length-limited static Huffman tables (15-bit and 8-bit) and a two-level decode table with a 10-bit fast path. Its speed advantage is on the compression side, where it avoids zlib's longer match-chain search.

## Compared with alternatives

Pick it over zlib-ng or libslz only if you can accept a non-deflate format and want a better ratio from a fast compressor; for most new work zstd (better decode speed and a maintained, fuzzed codebase) or bzip3/libbsc (better ratio) are safer choices, and libzling's successor richox/orz is not catalogued here.

## Integration

| | |
|---|---|
| **Form** | shared lib (build/CMakeLists.txt builds only a SHARED library plus the zling demo; the src/ files can also be dropped into a project) |
| **Dependencies** | none (bundles msinttypes headers for old MSVC) |
| **Minimum toolchain** | CMake 2.8; the CMake file passes -std=c++14 although the code is C++98-style; lzbench had to add a missing &lt;functional&gt; include to build it |
| **Platforms** | little-endian only in practice (data corruption reported on big-endian ppc64); x86-64 is what the benchmarks cover; MSVC support was added in 2015 |
| **Thread safety** | Not documented; each Encode/Decode call allocates its own buffers and coder state, so separate calls on separate Inputter/Outputter objects share nothing visible in the source. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README sample calls Encode(&inputter, &outputter, level), but the third parameter is ActionHandler\*; the real call is Encode(&in, &out, NULL, level).
- Corrupt input makes Decode() throw std::runtime_error (bad flag, bad Huffman code, invalid block size), and allocation failures throw std::bad_alloc, so callers need exception handling. There is no checksum in the format.
- A level outside 0-4 is not validated: the ROLZ encoder returns -1 and Encode() goes on writing a bogus block header.
- The encoder silently drops to level 0 for any 256 KB chunk whose Huffman output exceeds 95% of its input, so throughput varies with how compressible the data is.

## Known shortcomings

- Tier B on lzbench 2.4 (86.1 vs zlib -6 26.8 MB/s) and the README enwik8 run (2.208 s vs 6.502 s); archived, BSD-3-Clause only in headers.
- Issue #10: AFL-found decompression crashes disclosed in 2015, possible DoS; fuzz fixes landed Dec 2015 but the 2018 Huffman rewrite came after them. Issue #12: big-endian ppc64 round-trip corruption, never fixed. Decode() never checks the read position against the stated olen, so a crafted block likely reads past obuf (from source reading, not tested). Invalid level (not 0-4) is unchecked. README sample passes the level in the ActionHandler\* slot. lzbench notes 'not recommended for production use (per author)'.

## Caveats and trade-offs

Decompression in lzbench is slower than zlib (183 MB/s versus 314 MB/s at -6), though the README shows slightly faster decode than gzip on enwik8. Repo archived 2021-04-26 and points to richox/orz as successor. License is the BSD-3-Clause text in source headers; there is no LICENSE file.

Order-1 ROLZ with Huffman coding; 16 MB blocks. Compression ratio beats zlib and approaches bzip2.

## Maintenance

Abandoned: last commit 2018-10-12, archived 2021-04-26 with a pointer to richox/orz, and lzbench labels it 'not recommended for production use (per author)'. The BSD-3-Clause text sits in the source headers (there is no LICENSE file), so it can be copied, but it should be fuzzed and hardened before any use on external data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench 2.4 suite (public code, gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P, silesia.tar) lists zling 2018-10-12 -0 at 86.1 / 183 MB/s, 29.72% vs zlib 1.3.2 -6 at 26.8 / 314 MB/s, 32.19%; the README separately shows libzling e0 2.208 s vs gzip 6.502 s on enwik8 (Xeon E5-2620 v3). All quoted numbers match; flags of the release binary are not on the results page, so B.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** Numbers verified on both pages; archived 2021-04-26, last commit 2018-10-12 (abandoned), BSD-3-Clause text in source headers with no LICENSE file (confirmed LICENSE/LICENSE.txt/COPYING 404). lzbench marks zling as not recommended for production use (per author).
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; lzbench 2.4
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/richox/libzling>
  - <https://github.com/richox/libzling/commits>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/README.md>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/README.md>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling.h>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling.cpp>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling_lz.h>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling_lz.cpp>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling_utils.h>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/src/libzling_inc.h>
  - <https://raw.githubusercontent.com/richox/libzling/HEAD/build/CMakeLists.txt>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/richox/libzling/issues?q=is%3Aissue>
  - <https://github.com/richox/libzling/issues/10>
  - <https://github.com/richox/libzling/issues/11>
  - <https://github.com/richox/libzling/issues/12>
  - <https://github.com/richox/libzling/commits>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/richox/libzling`) · [data/wave9/enrich/raw/github_com_richox_libzling.json](../../../data/wave9/enrich/raw/github_com_richox_libzling.json) (enrichment confidence 0.8)

</details>
