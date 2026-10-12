# smallz4

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small C++ optimal-parse LZ4 encoder: standard .lz4 output about 0.2-0.9% smaller than lz4 -9/-12, but slower to compress.

| | |
|---|---|
| **Beats** | lz4 (lz4 -9) |
| **Claimed result** | No compression-speed win; it is an optimal-parse LZ4 encoder for slightly smaller output. WebSearch snippets of the author's page and an encode.su thread give, on enwik9: lz4 r128 -9 at 374,905,570 bytes and smallz4 0.5 -9 at 371,681,075 bytes (derived from page data: 0.86% smaller). One snippet gives smallz4 1.3 -9 at 371,680,328 bytes in 262 s. The record's 33 s (lz4) and 242 s (smallz4 0.5) timings and the lz4ultra 1.3.0 figure of 371,680,323 bytes were not re-confirmed in this run. Decoding uses the standard lz4 format, so decode speed is unchanged. |
| **Workload** | Compression of enwik9 (1 GiB) to the lz4 format with optimal parsing, versus lz4 r128 level 9; sizes and times from the author's page as quoted in a search snippet. |
| **Metric** | other |
| **Hardware** | not available |
| **Compiler and flags** | Makefile: g++ -O2 (repo); benchmark compiler not seen |
| **Adoption** | 51 stars (GitHub mirror) |
| **Last commit** | 2020-04-13 |
| **Links** | [repository](https://github.com/stbrumme/smallz4) · [benchmark](https://create.stephan-brumme.com/smallz4/) |

## Verdict

First-party enwik9 (1 GiB English Wikipedia) numbers known only from WebSearch snippets of the author's egress-blocked page and encode.su: smallz4 0.5 -9 371,681,075 bytes in 224 s versus lz4 r128 -9 374,905,570 bytes (0.86% smaller) and lz4 -12 371,681,832 bytes in 144 s; smallz4 1.5 -9 371,680,328 bytes versus lz4 1.9.2 -12 372,443,347 bytes (0.2% smaller). Machine, compiler and flags are not stated, and decode speed is that of whichever LZ4 decoder you use.

## Use it when

- Compress-once, decompress-many LZ4 assets (firmware images, game data, embedded payloads) where every byte counts and encode time is irrelevant
- When the decoder is fixed to the LZ4 format and cannot be swapped for zstd or LZSA
- Vendoring a tiny, dependency-free MIT encoder (one header, about 800 lines) plus a few-hundred-line C decoder for small or static binaries
- Preset-dictionary LZ4 compression (-D) where both sides share the last 64 KB of a dictionary file

## Skip it when

- Any throughput-sensitive compression: snippet figures put level 9 at 224-262 s for enwik9 versus 33 s for lz4 r128 -9 and 144 s for lz4 1.8.2 -12
- If you already use modern lz4 -12: snippet data show lz4 1.8.2 -12 --no-frame-crc -BD at 371,680,440 bytes versus smallz4 1.1 at 371,680,428, a 12-byte difference on 1 GB
- Inputs with long repeats at a period above 1 byte (for example a short pattern or a small record repeated for megabytes) at levels 7-9: from reading the code, every position gets a match running to the block end and both the match finder and estimateCosts scan that length, so time grows roughly quadratically per 4 MB block (not measured); only single-byte runs are short-cut via MaxSameLetter
- Large or memory-tight inputs: per 4 MB block it allocates a 16-byte Match per input byte plus a 4-byte cost per byte and an 8 MB hash table, roughly 90 MB peak (from the code's vector sizes)
- Projects needing a maintained library with an in-memory API, multithreading or block-independent output

## How it is fast

It is not faster than the baseline; the gain is output size. Level 9 walks the full hash chain inside LZ4's 64 KB window for every position (findLongestMatch), then runs a backward dynamic-programming pass (estimateCosts) that picks, for each position, the match length or literal that minimises encoded bytes, including the extra length bytes at 15 and 15+255n. Levels 1-3 are greedy and 4-6 lazy with chain lengths 1-6, which skip the DP-heavy search.

## Compared with alternatives

Pick smallz4 over lz4 -12 only for the last few hundred bytes per gigabyte and a dependency-free single header; pick lz4ultra or blz4 for the same optimal-LZ4 goal with faster encoders or decode-speed tuning (lz4ultra's enwik9 size of 371,680,323 bytes is within 5 bytes of smallz4's), and plain LZ4 HC when compression speed matters at all.

## Integration

| | |
|---|---|
| **Form** | header-only (encoder) plus source-drop C decoder (smallz4cat.c) |
| **Dependencies** | none |
| **Minimum toolchain** | C++98-style code built with g++ -O2 in the Makefile (no -std set); smallz4cat needs C99. The Makefile says it was only tested on the author's Linux system. |
| **Platforms** | any in principle; the encoder reads 4 bytes through uint32_t\* casts at arbitrary offsets, so it relies on unaligned loads being tolerated (x86-64, ARMv8); strict-alignment targets are not documented |
| **Thread safety** | not documented; each lz4() call builds its own compressor object with no global state, so concurrent calls on separate streams look safe from the code |
| **Drop-in for the baseline** | partial: output is standard LZ4 frame or legacy format readable by lz4 and liblz4, but the encoder API is a callback interface, not LZ4_compress_HC() or the LZ4F API |

## Gotchas

- Frames are written with linked blocks (block-independence flag off), 4 MB max block size and no content or block checksum, so output cannot be decoded block-by-block in parallel and corruption is not detected; smallz4cat also reads and ignores any checksums in other files.
- With a dictionary (-D) the frame carries no dictionary ID, so decoders must be handed the same dictionary out of band (lz4 -D or smallz4cat -D).
- smallz4cat bugs from reading smallz4cat.c (not tested): with -D it opens argv[1] instead of the file argument, so 'smallz4cat -D dict file.lz4' tries to open '-D'; one-character file names are ignored; a legacy-format file whose size is an exact multiple of 8 MiB ends with 'ERROR: out of data' and exit code 1 after writing the full output; offsets reaching before the stream start copy uninitialised stack bytes from its 64 KB history buffer.
- The encoder reads 4 bytes through \*(uint32_t\*) casts (unaligned type-punning, undefined behaviour in C++ though fine on x86 and ARMv8), and the CLI never checks fwrite results or sets binary mode on stdin/stdout, so Windows pipes are text mode.

## Known shortcomings

- Size-only win, no speed win: the snippet gives 371,680,328 bytes for smallz4 1.3 in 262 s (about 7x slower than lz4 -9); the author's page is blocked so the other timings are unconfirmed.
- Does not beat modern lz4 -12 on size by more than bytes: snippets give lz4 1.8.2 -12 at 371,680,440 bytes in 144 s vs smallz4 1.1 at 371,680,428 bytes in 254 s, and lz4 1.9.2 -12 at 372,443,347 bytes vs smallz4 1.5 at 371,680,328 bytes. Levels 7-9 look quadratic per 4 MB block on long repeats with a period above 1 byte (only single-byte runs are short-cut); peak memory about 90 MB. Unaligned uint32_t\* type-punning (UB). Frames use linked blocks with no checksums, and -D carries no dictionary ID. smallz4cat bugs: -D opens argv[1] instead of the file; one-character file names ignored; a legacy file of an exact 8 MiB multiple ends with 'out of data'; offsets before the stream start copy uninitialised stack bytes into the output; no binary mode on Windows stdin/stdout.

## Caveats and trade-offs

Numbers come only from WebSearch snippets of the author's site (create.stephan-brumme.com) and an encode.su thread, both egress-blocked, so the machine, CPU and compiler are unknown. The version attached to the 371,680,328-byte result conflicts between sources: a snippet says smallz4 1.3, while the original record said 1.5. The GitHub readme is two lines and calls GitHub 'a mirror only'. The Makefile uses g++ -O2 (gcc -O2 -std=c99 for smallz4cat). Not faster than the baseline at compression (about 7-8x slower than lz4 -9 per the snippet figures); it gives slightly smaller LZ4 output and has a tiny standalone decoder (smallz4cat). The GitHub mirror's last commit is 2020-04-13 ('version 1.5'); the author's site may differ.

Optimal-parse lz4 encoder (smallz4.h library plus smallz4cat.c decoder). Output is valid lz4, but compression is far slower than lz4 -9 for a roughly 1% size gain. Produces lz4 frame format (not legacy) per blz4's README.

## Maintenance

Abandoned (GitHub mirror last commit 2020-04-13, version string 1.5, 3 issues, no pull requests; the author's site is the stated main repository) but MIT-licensed and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's page (create.stephan-brumme.com/smallz4) is egress-blocked. WebSearch snippets confirm an enwik9 comparison against lz4 -9, but the machine, compiler and method are unseen, so this is first-party data without methodology: C. The output-size gain is only 0.86% with no speed win, so it is a niche optimal-parse entry.
- **Verifier notes:** Kept as a size-only optimal-LZ4 niche entry under the seed rule. Metadata from github.com: 51 stars, 13 forks, MIT (LICENSE read), 12 commits, last 2020-04-13, so abandoned is correct. encode.su and mattmahoney.net (LTCB) are both EGRESS_BLOCKED.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party claim (snippet); first-party claim (snippets)
- **Pages the verifier opened:**
  - <https://github.com/stbrumme/smallz4>
  - <https://github.com/stbrumme/smallz4/commits/master>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/readme.md>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/readme.md>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/Makefile>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/smallz4.h>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/smallz4.cpp>
  - <https://raw.githubusercontent.com/stbrumme/smallz4/HEAD/smallz4cat.c>
  - <https://github.com/stbrumme/smallz4/issues?q=is%3Aissue>
  - <https://github.com/stbrumme/smallz4/pulls?q=is%3Apr>
  - WebSearch: smallz4 optimal LZ4 enwik9 lz4 -12 comparison (snippets of https://create.stephan-brumme.com/smallz4/ and https://encode.su/threads/2593-smallz4)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/stbrumme/smallz4`) · [data/wave9/enrich/raw/github_com_stbrumme_smallz4.json](../../../data/wave9/enrich/raw/github_com_stbrumme_smallz4.json) (enrichment confidence 0.6)

</details>
