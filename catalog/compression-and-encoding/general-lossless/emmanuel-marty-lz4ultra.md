# lz4ultra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib (src/matchfinder.c is CC0-1.0)` · 🔴 abandoned

> Offline optimal-parse LZ4 encoder whose standard LZ4 output decodes 1.45-1.54x faster than lz4 -12 output on enwik9.

| | |
|---|---|
| **Beats** | lz4 (lz4 1.9.2 -12 high-compression encoder, same LZ4 format) |
| **Claimed result** | README table (enwik9, Core i7-6700): lz4ultra 1.3.0 --favor-decSpeed output (376,118,079 bytes) decompresses in 296,972 microseconds versus 457,141 microseconds for lz4 1.9.2 -12 --favor-decSpeed output (377,175,400 bytes), 1.54x faster (derived from page data); favor-ratio output 347,936 versus 505,804 microseconds (1.45x, derived) with 371,680,323 versus 372,443,347 compressed bytes (lz4ultra versus lz4). |
| **Workload** | Decompression time for enwik9 (1,000,000,000 bytes) of LZ4-format streams produced by lz4 -12 versus lz4ultra's optimal packer. |
| **Metric** | throughput |
| **Hardware** | Core i7-6700 (as printed in the README table) |
| **Adoption** | 62 stars |
| **Last commit** | 2023-01-29 |
| **Links** | [repository](https://github.com/emmanuel-marty/lz4ultra) · [benchmark](https://github.com/emmanuel-marty/lz4ultra) |

## Verdict

The author's README measures enwik9 on a Core i7-6700 (compiler and decoder build not stated): lz4ultra 1.3.0 --favor-decSpeed output decodes in 296,972 us against 457,141 us for lz4 1.9.2 -12 --favor-decSpeed output (1.54x, derived from page data) while also being smaller (376.1 MB vs 377.2 MB); in favor-ratio mode 347,936 us vs 505,804 us (1.45x) at 371.7 MB vs 372.4 MB. These are first-party numbers on one file with no published harness.

## Use it when

- Compress-once, decompress-many assets (game data, firmware images, embedded or 8-bit platform payloads, read-only bundles) that are already read with a standard LZ4 decoder.
- When you want lz4hc -12's ratio or slightly better but faster decoding, and offline compression time is irrelevant.
- When the decoder cannot change (shipped hardware, third-party lz4 library) but you control the encoder.
- Building a decode-speed-tuned LZ4 stream with --favor-decSpeed, which on enwik9 gave both a smaller file and a 1.54x faster decode than lz4 1.9.2 -12 --favor-decSpeed.

## Skip it when

- Any online or latency-sensitive compression path: it is an optimal parser over a suffix array, far slower than lz4 fast or lz4hc low levels (a WebSearch snippet of the smalLZ4 page lists lz4ultra 1.2.2 at 291 s for enwik9, about 3.4 MB/s).
- Memory-tight encoders: the compressor allocates three 8-byte-per-position arrays over the block plus 64 KB of history (roughly 100 MB at the default 4 MB block) plus libdivsufsort working state.
- When you need the reported gains confirmed on current tools: the comparison is against lz4 1.9.2 (2019) on one dataset, and lz4 1.10.0's lz4hc -12 already decodes silesia.tar at 3813 MB/s in lzbench 2.4.
- When you only need ratio: smalLZ4 1.5 -9 reaches the same favor-ratio size (371,680,328 vs 371,680,323 bytes) and decode time on enwik9.
- If you need a maintained dependency: last commit 2023-01-29, no tagged library releases, and the Makefile builds only the CLI.

## How it is fast

The speedup comes from emitting fewer LZ4 tokens, not from a faster decoder: on enwik9 the favor-decSpeed output has 88.5 M tokens against 92.1 M for lz4 -12 --favor-decSpeed, and every token saved is one less branch-heavy step in the decoder. Matches are found with a suffix array (libdivsufsort) plus a wimlib-derived LCP-interval match finder, which enumerates all matches at each position. A backward dynamic-programming optimal parse then picks the cheapest token sequence, and a second pass merges or drops short matches to cut the command count. Favor-decSpeed mode adds a larger per-match penalty (5 instead of 1) so the parser prefers longer, fewer matches.

## Compared with alternatives

Pick it over LZ4's own lz4hc when files are compressed once and decoded many times by an existing LZ4 decoder; pick zstd or LZSSE instead if you can change the decoder and want more ratio or decode speed, and plain LZ4 if compression speed matters.

## Integration

| | |
|---|---|
| **Form** | source-drop (Makefile builds the lz4ultra CLI only; the library API in src/lib.h has to be compiled into your project with bundled libdivsufsort and xxhash) |
| **Dependencies** | none external; bundles libdivsufsort (MIT) and xxhash |
| **Minimum toolchain** | C99-era C; Makefile defaults to clang -O3 -fomit-frame-pointer; VS2017 and Xcode projects included |
| **Platforms** | any with a C compiler (POSIX, Windows via VS2017, macOS via Xcode); no SIMD requirement |
| **Thread safety** | Not documented; each compress call builds its own lz4ultra_compressor context and the source shows no global mutable state, so separate calls on separate buffers should be independent. |
| **Drop-in for the baseline** | partial — output is a drop-in for lz4 -12 output on the decode side, but the encoder API is lz4ultra's own, not LZ4_compress_HC() |

## Gotchas

- lz4ultra_compress_inmem() and lz4ultra_decompress_inmem() return size_t and signal errors with -1, so compare against (size_t)-1.
- The README's decompression times do not say which decoder produced them; the tool's -dbench mode times lz4ultra's own decoder (best of 50 runs), which the README itself says is less optimized than lz4's.
- Raw block mode (-r) is limited to 4 MB inputs and cannot store incompressible data (LZ4ULTRA_ERROR_RAW_UNCOMPRESSED).
- The default is favor-ratio; the bigger decode-speed win needs --favor-decSpeed (or clearing LZ4ULTRA_FLAG_FAVOR_RATIO), which costs about 1.2% more output on enwik9.

## Known shortcomings

- Tier C: an independent encoder for the lz4 format (not an lz4 fork); favour-ratio numbers are first-party; abandoned (last commit 2023-01-29).
- README decode timings are likely from its own -dbench decoder (best of 50 runs), not lz4 (likely, not proven). Baseline lz4 1.9.2 on one file (enwik9). Encoder needs about 100 MB at the default 4 MB block. Compression is slow, about 3.4 MB/s (291 s on enwik9 for 1.2.2, from a smalLZ4 page snippet only). Makefile builds the CLI only, no library target.

## Caveats and trade-offs

First-party numbers, one dataset, no compiler flags, and the README does not say which decoder produced the timings (it says files are meant to be decompressed with lz4 and that its own decompressor is not as optimized as lz4 proper). Compared against lz4 1.9.2 (2019), not the current 1.10.0. smalLZ4 1.5 -9 in the same table is essentially identical in favor-ratio mode (371,680,328 bytes, 348,018 microseconds). Last commit 2023-01-29, more than 3 years ago. CC0 matchfinder carries no patent grant; it bundles libdivsufsort (MIT).

Output is plain LZ4 format, readable by the standard lz4 decoder; the gain comes from fewer tokens, not from a faster decoder. Compression is an offline optimal parse and slower than lz4 -12 (no timing given).

## Maintenance

Abandoned since 2023-01-29 (last commits were cppcheck and memory-leak fixes), but it is a small Zlib-licensed codebase with a CC0 match finder, and its output stays readable by any standard LZ4 decoder, so the encoder can be vendored for offline use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Only first-party numbers: the README's enwik9 table (Core i7-6700) gives decompression times for lz4ultra 1.3.0 output vs lz4 1.9.2 -12 output, with no compiler, flags, decoder build or benchmark code.
- **Verifier notes:** Numbers match; the favor-ratio byte counts in claimed_speedup were in the wrong order and are fixed. lz4ultra is an independent optimal encoder producing standard LZ4 streams, not a fork, port or wrapper of lz4/lz4 (on the known list), so it does not fold; it is a complementary encoder for lz4's decoder. Zlib license (src/matchfinder.c CC0) confirmed from LICENSE; 62 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/emmanuel-marty/lz4ultra>
  - <https://github.com/emmanuel-marty/lz4ultra/commits>
- **Sources the enricher read:**
  - <https://github.com/emmanuel-marty/lz4ultra>
  - <https://github.com/emmanuel-marty/lz4ultra/tree/master/src>
  - <https://github.com/emmanuel-marty/lz4ultra/commits/master>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/Makefile>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/lib.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/format.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_inmem.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_inmem.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_streaming.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_streaming.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_context.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_context.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/shrink_block.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/matchfinder.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/expand_block.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/expand_inmem.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/lz4ultra.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lz4ultra/HEAD/src/frame.c>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - WebSearch snippet: https://create.stephan-brumme.com/smallz4/ (not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/emmanuel-marty/lz4ultra`) · [data/wave9/enrich/raw/github_com_emmanuel_marty_lz4ultra.json](../../../data/wave9/enrich/raw/github_com_emmanuel_marty_lz4ultra.json) (enrichment confidence 0.75)

</details>
