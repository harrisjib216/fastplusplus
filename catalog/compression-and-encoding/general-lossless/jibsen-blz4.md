# blz4

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟡 stale

> Experimental LZ4 legacy-format encoder using BriefLZ's optimal parser; output matches lz4 -12 or is a few bytes smaller, at much lower speed.

| | |
|---|---|
| **Beats** | lz4 (lz4 -12 -l, legacy format) |
| **Claimed result** | No speed claim; compressed-size comparison only. blz4 --optimal is equal to or slightly smaller than lz4 -12 -l on every Silesia file (7 of 12 identical; smaller on mozilla 22,025,940 vs 22,025,988, mr 4,190,675 vs 4,190,774, nci 3,621,482 vs 3,621,567, samba 6,100,521 vs 6,100,539, xml 759,868 vs 759,901) and matches lz4x -9 exactly on every file. The README calls --optimal 'very slow' and says LZ4 is 'very close to optimal, and much faster'. |
| **Workload** | Compressed size on the 12 Silesia corpus files using BriefLZ's optimal parser (--optimal) to write LZ4 legacy-format output, compared with lz4 -12 -l and lz4x -9. |
| **Metric** | other |
| **Adoption** | 28 stars |
| **Last commit** | 2023-11-01 |
| **Links** | [repository](https://github.com/jibsen/blz4) · [benchmark](https://raw.githubusercontent.com/jibsen/blz4/HEAD/README.md) |

## Verdict

First-party README table, size only: on the 12 Silesia files, blz4 --optimal output equals lz4 -12 -l on 7 files and is 18 to 99 bytes smaller on the other 5 (for example mr 4,190,675 vs 4,190,774), and it equals lz4x -9 on every file. No timings, versions, compiler, flags or hardware are given.

## Use it when

- Offline, write-once data (firmware images, game assets, embedded ROM blobs) where every byte saved matters and compression time is irrelevant.
- Checking how close lz4 -12 gets to an optimal LZ4 parse, as a reference encoder for research or encoder testing.
- Producing LZ4 legacy-format streams to feed an existing lz4 decoder, which keeps stock LZ4 decompression speed.

## Skip it when

- Any time compression speed matters: the README calls --optimal 'very slow' and says lz4 'is very close to optimal, and much faster'.
- When you need the modern LZ4 frame format (checksums, content size, block independence flags) or the liblz4 API; blz4 writes only legacy-format output.
- Decoding untrusted data with the bundled lz4_depack or 'blz4 -d': the decoder has no output-capacity parameter and no bounds or offset checks.
- Production use in general: the author says it 'is not production quality, and has not been properly tested'.
- Memory-constrained compression: btparse needs (5 x block size + 128 Ki + 3) 32-bit words of workmem, about 160 MiB for one 8 MiB block.

## How it is fast

It does not aim to be fast; it aims for smaller LZ4 output. Levels 5-7 use BriefLZ's 'leparse' (backwards dynamic-programming parse over hash chains) and levels 8-10 use 'btparse' (forwards dynamic-programming parse with a binary-tree match finder per hash bucket, Knuth multiplicative hash of 4 bytes, 64 KiB window). Level 10 searches without depth or length limits, which is how it reaches the true optimum for LZ4's cost model.

## Compared with alternatives

Pick it over LZ4's own lz4 -12 (LZ4 HC) only when you need the last few hundred bytes of an LZ4 stream and can spend far more CPU; for faster LZ4-compatible high-ratio encoding use LZ4 HC, and for better decode-speed-aware optimal parsing in the same format see lz4ultra.

## Integration

| | |
|---|---|
| **Form** | source-drop (Meson builds a static liblz4-named library and the blz4 CLI) |
| **Dependencies** | none (parg.c bundled for CLI option parsing) |
| **Minimum toolchain** | C99; Meson &gt;= 0.60.0 if using the bundled build |
| **Platforms** | any (portable C; uses __builtin_clzl or _BitScanReverse when available) |
| **Thread safety** | not documented; the pack functions keep all state in the caller-supplied workmem, so separate workmem buffers per thread should be safe (inferred from the code) |
| **Drop-in for the baseline** | partial — output is readable by lz4 tools (legacy format), but the API is not the liblz4 API and the frame format is legacy only |

## Gotchas

- lz4_depack(src, dst, packed_size) takes no destination size and does not validate offsets or lengths, so a crafted block can write past dst or read before it (the CLI decompresses into a fixed 8 MiB buffer); it also reads in[0] even when packed_size is 0.
- The header is named lz4.h and the library is built as 'lz4', which collide with the real liblz4 header and library name if both are on the include or link path.
- lz4_pack_level returns LZ4_ERROR for any level outside 5-10; there are no fast levels.
- lz4.h's LZ4_VER_MINOR is 1 while LZ4_VER_STRING and meson.build say 0.2.0.

## Known shortcomings

- Sizes only, no speed claim: against lz4 -12 -l, 7 of 12 files are identical and 5 smaller by a few bytes. README calls --optimal 'very slow' and says lz4 is 'much faster'. Seed record.
- lz4_depack takes no destination size and does no offset or length checks; blz4 -d decodes into a fixed 8 MiB buffer, so crafted input overflows the heap, and it reads in[0] when packed_size is 0. The header is named lz4.h and the library lz4, clashing with real liblz4. LZ4_VER_MINOR 1 vs the '0.2.0' version string. btparse work memory is about 160 MiB per 8 MiB block. Legacy frame only. Last code change Feb 2020 (2023 commits are CI only).

## Caveats and trade-offs

Not a speed win: the README itself says lz4 'does flexible parsing, is very close to optimal, and much faster', and calls the project 'a quick experiment ... not production quality, and has not been properly tested'. No timings, no compiler, flags, versions or hardware. smallz4 excluded from the table by the author because its output is not the legacy format. Included only because it is a listed niche (optimal-parsing lz4 encoder); the faster-than-baseline criterion is not met.

Produces lz4 legacy-format streams, so lz4 decoders read them. The --optimal mode is described as very slow. Output at best a few hundred bytes smaller than lz4 -12; the decoder is stock lz4, so decode speed is unchanged.

## Maintenance

Stale: the last code change was February 2020 (btparse added, version 0.2.0) and the November 2023 commit only updated CI; Zlib-licensed and small enough to vendor, but self-described as an untested experiment.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmark table gives first-party compressed sizes on the 12 Silesia files for blz4 --optimal, lz4 -12 -l and lz4x -9; no timings, no compiler, flags, versions or hardware, and no benchmark script. Size-only first-party numbers are C.
- **Verifier notes:** Numbers check out against the README table; the record's 'most files are byte-identical' is 7 of 12. Not a speed win, kept per the seed-record rule as a size-only optimal-parse LZ4 encoder; metadata (Zlib, 28 stars, last commit 2023-11-01, stale) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/README.md>
  - <https://github.com/jibsen/blz4>
  - <https://github.com/jibsen/blz4/commits>
- **Sources the enricher read:**
  - <https://github.com/jibsen/blz4>
  - <https://github.com/jibsen/blz4/commits>
  - <https://github.com/jibsen/blz4/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/README.md>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/meson.build>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/lz4.h>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/lz4.c>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/lz4_depack.c>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/lz4_btparse.h>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/lz4_leparse.h>
  - <https://raw.githubusercontent.com/jibsen/blz4/HEAD/blz4.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jibsen/blz4`) · [data/wave9/enrich/raw/github_com_jibsen_blz4.json](../../../data/wave9/enrich/raw/github_com_jibsen_blz4.json) (enrichment confidence 0.8)

</details>
