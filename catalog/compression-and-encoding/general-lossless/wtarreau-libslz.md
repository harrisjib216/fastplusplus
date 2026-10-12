# libslz (SLZ)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `X11` · 🟢 active

> Stateless deflate/zlib/gzip compressor in C, about 3.5x faster than zlib -1 at a much lower ratio.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | lzbench 2.4 (EPYC 9555P, silesia.tar): slz_gzip 1.3.1 -1 compress 316 MB/s at 46.97% vs zlib 1.3.2 -1 89.0 MB/s at 36.45% (3.6x, derived from page data); also ahead of zlib-ng 2.3.3 -1 (196 MB/s, 44.41%) and libdeflate 1.26 -1 (202 MB/s, 34.68%). README (single core of Core i5-3320M, Silesia): slz 1.2.1 232 MB/s (gzip) to 293 MB/s (raw deflate) at ratio 2.12 vs zlib 1.2.8 -1 70 MB/s at 2.74 (about 3x; zlib's huffman-only and RLE modes reach 88 and 81 MB/s); output often 24-32% larger; 28-byte stream state vs zlib's 256 kB per stream. |
| **Workload** | Compress silesia.tar to gzip single thread (lzbench) and README per-file runs. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; README: Intel Core i5-3320M 3.3 GHz |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 34 stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/wtarreau/libslz) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In inikep's lzbench 2.4 (release binary built with gcc 15.2.0, one thread of an EPYC 9555P at 3.2 GHz, turbo off, silesia.tar), slz_gzip 1.3.1 -1 compresses at 316 MB/s to 46.97% vs zlib 1.3.2 -1 at 89.0 MB/s to 36.45%, about 3.6x faster for about 29% more output (derived from page data). The author's README measured slz 1.2.1 at 232 MB/s (gzip) and 293 MB/s (raw deflate) vs zlib 1.2.8 -1 at 70 MB/s on one core of a Core i5-3320M.

## Use it when

- HTTP servers, proxies and gateways compressing tens of thousands of concurrent responses, where zlib's per-stream memory (256 kB) is the real limit; the author's HAProxy test on a Core i5-3320M showed 23.7M/9.7M VSZ/RSS for slz vs 130M/101M for zlib and 3x the hits/s.
- Any producer that must emit gzip/deflate (browser Content-Encoding, gzip files, zlib-wrapped formats) and is CPU-bound, so trading roughly 30% larger output for about 3x less compression CPU is acceptable.
- Backups or streaming over a fast link where the compressor otherwise caps throughput (the bundled zenc tool is used this way).
- Compressing attacker-controlled and secret data in separate calls to avoid CRIME-style dictionary leaks, since no history persists between encode calls.
- Input fed in buffers of at least a few kB at a time (for example a per-thread linear buffer that collects a chunked HTTP response).

## Skip it when

- When ratio matters: on Silesia, lzbench 2.4 shows slz -1 at 46.97% vs zlib -1 36.45% and libdeflate -1 34.68%; the README states output is often 24-32% larger than zlib's.
- When the consumer does not need deflate compatibility: in the same lzbench table LZ4 1.10.0 compresses at 550 MB/s at 47.60% and zstd -1 at 411 MB/s at 34.53%, both beating slz on speed or ratio.
- Small writes: the stateless design means each call only matches within its own input, so feeding less than a few kB per call wastes ratio (the README asks for an input buffer in that case).
- Fast decompression: slz output decodes through zlib or another inflater, so decode speed is the inflater's (lzbench lists 329 MB/s, which is zlib's); uslz is a lightweight decoder and the README says zlib is fine if decode performance is the priority.
- Levels: only level 0 (stored) and level 1 (compress) are documented; the header warns other values give unpredictable behaviour, although the code clamps level to 0-15 and lzbench runs -1 to -3.

## How it is fast

LZ77 matching with a single-entry hash table (8192 entries, 13-bit hash of 4 bytes) that stores the position plus a copy of the hashed 32-bit word, so most non-matches are rejected without calling the match-length routine; the match length uses word-wide XOR plus count-trailing-zeros. It never builds dynamic Huffman trees: it encodes only with the fixed deflate Huffman table, with precomputed bit sequences for lengths and distances, and switches to stored (literal) blocks when fixed coding would expand the data, so there is no tree-building pass. Bits are written with unaligned 32/64-bit stores on little-endian x86-64 and ARM, and CRC-32 for gzip uses the ARMv8 CRC32 instruction when available.

## Compared with alternatives

Pick slz over zlib-ng, libdeflate or ISA-L igzip when the output must be deflate/gzip and memory per stream or compression CPU is the binding cost while ratio is secondary; libdeflate and zlib-ng give far better ratio at -1 (34.68% and 44.41% vs 46.97%) for about 60% of slz's speed in lzbench, and if gzip compatibility is not required, LZ4 or zstd -1 dominate it.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (Makefile builds libslz.a and libslz.so); also small enough to source-drop (src/slz.c, slz.h, slz-prv.h, tables.h) |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | C with GCC extensions (__builtin_ctz/clzll, __builtin_expect, __attribute__((constructor)), inline asm for CRC32); Makefile defaults to gcc -O3 |
| **Platforms** | any; fast paths for unaligned little-endian x86-64, i386, ARMv7-A and ARMv8, plus the ARMv8 CRC32 instruction; other targets use the byte-wise path. Makefile handles Linux and macOS (dylib). |
| **Thread safety** | Not documented explicitly; each slz_stream is independent and the encoder keeps no global mutable state after the constructor fills the distance table (or uses precomputed tables with -DPRECOMPUTE_TABLES), so separate streams on separate threads are safe by construction (inferred from source). |
| **Drop-in for the baseline** | partial: output is drop-in (standard zlib/deflate/gzip readable by zlib), but the API is not zlib's deflate()/z_stream interface, so callers must be rewritten (HAProxy has a build option for it). |

## Gotchas

- Encode functions take no output length: the caller must size the output buffer for the worst case (input plus about 5 bytes per 64 kB block plus header/trailer) and leave 3 extra bytes past the end (7 with SLZ_DIRECT_ENQUEUE56), since the direct-store paths write beyond the advanced pointer.
- Each encode call puts a 64 kB hash table (8192 x 8 bytes) on the stack and memsets it, so tiny calls pay a fixed reset cost and threads need enough stack.
- master moves fast: September 2026 commits fixed encoder edge cases (non-final 32 kB block emission, level 0 on blocks of 64 kB or more, the backward-match check when SLZ_BACKWARD_MATCH is 1) and uslz/zdec decoding bugs; pin a tagged release (v1.3.1 is what lzbench measured) rather than tracking master.
- v1.3.1 release notes mention fixes to adler32 on 32-bit systems, so zlib-format output from older releases on 32-bit targets deserves a check.

## Known shortcomings

- Tier B on lzbench (316 vs 89.0 MB/s for zlib -1); the README's 81/88 MB/s zlib figures are RLE and huffman-only modes, only 70 MB/s is zlib -1.
- In lzbench 2.4 both LZ4 (550 MB/s, 47.60%) and zstd -1 (411 MB/s, 34.53%) beat slz -1 (316 MB/s, 46.97%), so slz wins only where deflate/gzip output is required; v1.3.0+ ships a uslz decoder but the README says zlib still decodes faster. Encode takes no output length (the caller sizes the buffer plus 3-7 slack bytes); a 64 kB hash table sits on the stack and is memset each call. Sept 2026 master commits fix encoder edge cases (non-final 32 kB block, level 0 at 64 kB+, backward match with SLZ_BACKWARD_MATCH), so pin v1.3.1, the version lzbench measured.

## Caveats and trade-offs

Compressor only (decompression goes through zlib or another inflater; lzbench decompress figures are zlib's). Speed is bought with a much lower ratio (46.97% vs zlib -1 36.45% in lzbench), so it competes with zlib level 1 and LZ4-class use; stateless design suits many concurrent streams (HAProxy). X11 (MIT-style) license.

Stateless, no history window beyond a few bytes; much worse ratio than zlib; compression only (output is plain gzip/deflate/zlib readable by any inflater); 28 bytes per stream.

## Maintenance

Actively maintained by HAProxy's author (commits through 2026-09-27, tags v1.3.0 and v1.3.1 in July 2026); X11/MIT-style licence, one C file plus headers, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench suite (public code, gcc 15.2.0, single thread of an EPYC 9555P) lists slz_gzip 1.3.1 -1 at 316 MB/s, 46.97% vs zlib 1.3.2 -1 at 89.0 MB/s, 36.45%; compile flags are not on the page, so B, not A. The README's own Core i5-3320M table is first-party.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** Numbers verified on lzbench and the README; corrected the README zlib range (70 MB/s is zlib -1; 81/88 MB/s are RLE/huffman-only modes) and the memory claim to the README's wording. Metadata (34 stars, last commit 2026-09-27, X11 license) matches; widely used via HAProxy.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/wtarreau/libslz>
  - <https://github.com/wtarreau/libslz/commits/master>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/README>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/wtarreau/libslz>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/README>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/VERSION>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/src/slz.h>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/src/slz.c>
  - <https://raw.githubusercontent.com/wtarreau/libslz/HEAD/src/slz-prv.h>
  - <https://github.com/wtarreau/libslz/commits/master>
  - <https://github.com/wtarreau/libslz/tags>
  - <https://github.com/wtarreau/libslz/issues?q=is%3Aissue>
  - <https://github.com/wtarreau/libslz/issues/2>
  - <https://github.com/wtarreau/libslz/issues/3>
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/wtarreau/libslz`) · [data/wave9/enrich/raw/github_com_wtarreau_libslz.json](../../../data/wave9/enrich/raw/github_com_wtarreau_libslz.json) (enrichment confidence 0.85)

</details>
