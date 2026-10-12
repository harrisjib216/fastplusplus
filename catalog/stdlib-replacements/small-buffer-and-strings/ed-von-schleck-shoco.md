# shoco

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Tiny C entropy coder for short ASCII strings; first-party 2014 timings show about 2x smaz's speed on English words.

| | |
|---|---|
| **Beats** | smaz (short-string compressor); also gzip and xz command-line tools |
| **Claimed result** | README: shoco 'is typically faster by at least a factor of 2' than smaz; example 0.325s (smaz, 28% average compression) versus 0.145s (shoco, 33% average compression) for compress plus decompress of all words in /usr/dict/share/words (about 2.2x, derived from page data). Versus gzip and xz on /usr/share/dict/words: shoco 0.070s compress / 0.010s decompress / 3,393,975 bytes; gzip 0.470s / 0.048s / 1,476,083 bytes (6.7x and 4.8x faster, derived from page data); xz 3.300s / 0.148s / 1,229,980 bytes (47x and 15x faster, derived from page data). |
| **Workload** | Compress and decompress English words: all words in /usr/dict/share/words versus smaz, and /usr/share/dict/words (4,953,680 bytes) compressed as one file with the included shoco command-line tool versus gzip and xz. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the README timings; the repo Makefile builds with \$(CC) -std=c99 -O3 -Wall plus user CFLAGS, and the README says it was only tested with gcc/clang on x86_64 Linux. |
| **Adoption** | 390 stars, 67 forks |
| **Last commit** | 2026-02-16 |
| **Links** | [repository](https://github.com/Ed-von-Schleck/shoco) · [benchmark](https://github.com/Ed-von-Schleck/shoco/blob/master/README.md) |

## Verdict

The author's 2014 README timings, on an unstated machine and compiler: compress plus decompress of every word in /usr/share/dict/words took about 0.145 s user time for shoco (the test_input driver, which also counts fgets, strlen, strcmp and assert per line and is built by make's implicit rule without -O3; only shoco.o gets -O3) versus about 0.325 s for smaz with no published harness, about 2.2x (derived from page data). Whole-process runs of the shoco CLI on the 4.95 MB word list took 0.070 s to compress and 0.010 s to decompress versus 0.470 s and 0.048 s for gzip and 3.300 s and 0.148 s for xz at unstated levels, at a much worse ratio (3.39 MB versus 1.48 MB and 1.23 MB).

## Use it when

- Storing many short English or other ASCII strings (words, tags, names, keys in a key-value store or in-memory index) that must each be compressed independently, where gzip-style headers would make the output larger than the input.
- You control both compressor and decompressor and can train a model on your own corpus (file paths, URLs, identifiers) with generate_compressor_model.py, then compile it in.
- Per-string compression on a hot path: the README's driver run works out to about 0.3 microseconds per word for compress plus decompress plus line reading and comparison (0.145 s over 479,828 words, derived from page data).
- Embedded or freestanding C/C++ code that needs no allocation and no dependencies: three files, caller-owned buffers, an output buffer the size of the input suffices for ASCII.
- Data you produce and store yourself (trusted input), since the decompressor is not safe on hostile bytes.

## Skip it when

- Decompressing untrusted or possibly corrupted data: shoco_decompress reads out of bounds on crafted input (CVE-2017-11367, issue #28, fix PR #34 unmerged since 2017), and crafted pack codes can still index the successor table out of range even with that fix.
- Strings much longer than about 100 bytes or whole files: on /usr/share/dict/words shoco keeps 68.5% of the input versus 29.8% for gzip and 24.8% for xz (derived from page data). The author now recommends Zstandard; for columns of short strings FSST is the stronger, maintained option.
- Non-ASCII or UTF-8 text: every byte with the top bit set costs two bytes, so output can double. The default model also has no digits, spaces, punctuation other than hyphen and apostrophe, or most capitals, so codes, IDs and mixed alphanumeric strings get no gain (issue #35).
- Binary data or strings with embedded NUL bytes: compression stops at the first NUL even when len is given.
- Projects that need a maintained, packaged or versioned format: no releases, no model identifier in the stream, unmaintained since 2015, and the model generator only runs under Python 2.

## How it is fast

It is an order-1 (bigram) entropy coder with fixed bit packing rather than a dictionary or adaptive coder: a run of 2, 4 or 8 characters whose successor indices fit fixed bit budgets is packed into 1, 2 or 4 bytes, tagged by the high bits of the first byte (10, 110, 1110), while ASCII bytes pass through untouched because their top bit is 0. Encoding is lookups in a 256-entry char-to-id table and a 32x32 successor table plus one SSE2 compare (_mm_cmpgt_epi16 and movemask) to pick the largest pack that fits; decoding is a byte swap, shifts and masks into an [83][16] successor table. There is no allocation, hashing, match search or per-string header.

## Compared with alternatives

None of the catalogued siblings compress: to_static_string, bstring, buffet, FastString, MengRao/str and zuu_string_view speed up string building, conversion and search, while shoco shrinks stored short strings. Pick shoco only when bytes per stored short string are the constraint and the data is trusted; for columns of short strings with random access, FSST (wave 9, general-lossless) has peer-reviewed numbers and active maintenance.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at runtime (C standard headers; emmintrin.h on x86-64); Python 2 for the optional model generator, emscripten for the JS build |
| **Minimum toolchain** | C99 (Makefile: -std=c99 -O3); the author tested only gcc and clang on x86_64 Linux; MSVC 2013 and g++ build fixes were merged in 2014 |
| **Platforms** | any; SSE2 index check enabled automatically on x86-64, scalar fallback elsewhere (no NEON); big-endian handled by a byte-swap macro but untested per the README |
| **Thread safety** | Not documented; both functions only read static const tables and caller buffers, so concurrent calls are reentrant by construction. |
| **Drop-in for the baseline** | partial — replaces smaz conceptually (buffer-in, buffer-out C API for short strings) but the formats are incompatible and both ends must be built with the same compiled-in model |

## Gotchas

- Decompressor out-of-bounds reads (from code reading, not executed): decode_header() counts leading 1 bits, so lead bytes 0xF0-0xFF give mark 3-7 and index packs[] past PACK_COUNT 3 (CVE-2017-11367; issue #28's ASan report and a possible hang; PR #34 adds 'else if (mark &lt; 3)' but was never merged). Even with that check, a 4-byte pack such as E1 70 00 00 decodes 'i' then successor 14 = 'z', and the next lookup uses row 'z' - MIN_CHR = 83 of the 83-row chrs_by_chr_and_successor_id table (one past the end); EE 38 00 00 decodes 'x', 'q', then '\0' from the all-zero 'q' row, giving row index -39 before the table. A safe vendored copy needs a range check on last_chr too.
- shoco_compress reads one byte past len: the loop tests \*in != '\0' before in == in_end, so a buffer of exactly len bytes with no terminator is over-read by one byte (issues #15 and #16 still open; commit c112c4e of December 2015 stopped junk being encoded but kept the read). It also stops at any embedded NUL.
- shoco_decompress returns SIZE_MAX on truncated input, which the README does not document (it only describes bufsize and bufsize + 1); the bundled shoco CLI stores that result in an int and passes it to fwrite, so a malformed file makes it write from far beyond its buffer.
- The model is compiled in and the stream carries no model id: data compressed with one shoco_model.h decodes silently into wrong text with another. generate_compressor_model.py reads files as bytes and writes str with 'wb', so it fails under Python 3 (issues #38 and #39), and issues #27 and #42 report invalid or non-C-compliant generated headers.

## Known shortcomings

- Tier C: first-party 'on my computer' numbers with no CPU, compiler or run count; no smaz harness; the 0.145 s figure equals the user time of the README test_input example (fgets and strcmp included); the gzip/xz rows time the shoco-bin whole-file CLI against far stronger compressors at unstated levels; numbers predate the 2015 decompression overflow fix. Security: open issue #28 (2017, AFL/ASan) global-buffer-overflow read in shoco_decompress() on malformed input, unfixed; #35 some ASCII strings fail to compress. Unmaintained (last code 2015-12-08); MIT.
- Enricher: decode_header yields mark 3-7 for lead bytes 0xF0-0xFF, so packs[] is read past PACK_COUNT 3 (CVE-2017-11367, issue #28; fix PR #34 unmerged), and even with PR #34 crafted pack-2 bytes read outside chrs_by_chr_and_successor_id (E1 70 00 00 reaches row 83, EE 38 00 00 reaches row -39; index math checked in Python, not executed). shoco_compress reads in[len] before its end check (1-byte over-read, issues #15/#16 open; c112c4e fixed only the junk encoding); undocumented SIZE_MAX return on truncated input, which the CLI stores in an int and passes to fwrite. Harness: the test_input timing includes fgets/strlen/strcmp/assert per line and its driver is built by make's implicit rule without -O3 (only shoco.o gets -O3); gzip/xz rows time whole processes at unstated levels (shoco ratio 68.5% vs 29.8%/24.8%). Python 2-only model generator (#38/#39); default model lacks digits, spaces and most capitals (#35); stream carries no model id; stops at embedded NUL.

## Caveats and trade-offs

First-party numbers measured 'on my computer' (README, 2014): no CPU, compiler, flags or OS version stated, no run count. The smaz row has no committed harness; the shoco 0.145s figure equals the 'user' time of the README's own test_input example on /usr/share/dict/words (479,828 lines), and test_input.c times fgets input, compress, decompress and a strcmp check per line, so the two sides may not have been timed the same way. The gzip/xz table times whole processes of the shoco-bin command-line tool, which compresses the 4.95 MB file in one call including file I/O; the README calls whole-file use 'not a strong point of shoco', gzip/xz levels are not stated, and gzip/xz reach far better ratios (1.48 MB and 1.23 MB vs 3.39 MB), so that comparison is not like for like. The baseline is not a C++ standard facility. The numbers predate the March 2015 'Prevent buffer overflows in decompression' fix and the December 2015 end-of-string fix. Open issue #28 (2017, unanswered) reports an AFL/AddressSanitizer global-buffer-overflow read in shoco_decompress() on malformed input (24 bytes before chrs_by_chr_and_successor_id), so decompressing untrusted data is unsafe; open issue #35 reports some ASCII strings (e.g. 'My-Nam3-iZ-H@5eeB-M33R') failing to compress. The README begins 'This project is unmaintained. You should use ZStandard nowadays'; the last code change is the 2015-12-08 merge of pull request #17, and the 2026-02-16 commit only marks the project unmaintained. No independent speed benchmark of the C library against smaz was found (a search surfaced only ratio comparisons by Unishox2 and a third-party smaz speed-up blog). The README's '/usr/dict/share/words' path is the author's typo for /usr/share/dict/words. [retier] First-party 'on my computer' numbers: the test_input driver is built without -O3 and its timing includes fgets/strlen/strcmp per line; no smaz harness; gzip/xz rows time whole processes at unstated levels (shoco ratio 68.5% vs 29.8%/24.8%). Security: decoder reads packs[] past PACK_COUNT for lead bytes 0xF0-0xFF (CVE-2017-11367, #28, fix PR #34 unmerged) and crafted pack-2 bytes read outside the successor table; shoco_compress 1-byte over-read (#15/#16). Unmaintained since 2015; Python 2 model generator; default model lacks digits and spaces.

Entropy coder for short ASCII strings built on a compiled-in bigram model (default model tuned for English words; a Python script generates new models from your own data). Compression ratio is far worse than gzip or xz on larger inputs (3.39 MB versus 1.48 MB and 1.23 MB on the 4.95 MB word list); output never grows for plain ASCII input but non-ASCII input can; copy-in C files (shoco.c, shoco.h, shoco_model.h), no packaging.

## Maintenance

Unmaintained: the README says to use Zstandard instead, the last code change is the December 2015 merge of PR #17, the 2026-02-16 commit only adds that notice, and 20 issues and 12 PRs (including the CVE-2017-11367 fix) sit open; it is MIT-licensed and three small files, so it can be vendored for trusted data if you add bounds checks to shoco_decompress.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Comparisons With Other Compressors' section gives first-party timings against smaz (0.325s vs 0.145s) and gzip/xz (table) measured 'on my computer' with no CPU, compiler or run count; the committed test_input.c and shoco-bin.c cover only the shoco side and no smaz harness exists, so the evidence is first-party with partial methodology (tier C).
- **Verifier notes:** Numbers in claimed_speedup match the README exactly and the derived ratios are labelled correctly; tier C stands. Main shortcomings to record: no hardware/compiler for the timings, no smaz harness, gzip/xz row is a whole-file CLI comparison against much stronger compressors, and an open unfixed global-buffer-overflow read in shoco_decompress (issue #28) on malformed input. MIT license confirmed from LICENSE; not archived, not a fork; abandoned per the author's README note despite the 2026-02-16 notice commit.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/Ed-von-Schleck/shoco/blob/master/README.md>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/README.md>
  - <https://github.com/Ed-von-Schleck/shoco>
  - <https://github.com/Ed-von-Schleck/shoco/commits/master>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/test_input.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/shoco-bin.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/tests.c>
  - <https://github.com/Ed-von-Schleck/shoco/issues>
  - <https://github.com/Ed-von-Schleck/shoco/issues/28>
  - <https://github.com/Ed-von-Schleck/shoco/issues/35>
  - <https://github.com/Ed-von-Schleck/shoco/issues/15>
- **Sources the enricher read:**
  - <https://github.com/Ed-von-Schleck/shoco>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/shoco.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/shoco.h>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/shoco_model.h>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/test_input.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/shoco-bin.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/tests.c>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Ed-von-Schleck/shoco/HEAD/generate_compressor_model.py>
  - <https://github.com/Ed-von-Schleck/shoco/issues?q=is%3Aissue>
  - <https://github.com/Ed-von-Schleck/shoco/issues/28>
  - <https://github.com/Ed-von-Schleck/shoco/issues/15>
  - <https://github.com/Ed-von-Schleck/shoco/issues/16>
  - <https://github.com/Ed-von-Schleck/shoco/issues/35>
  - <https://github.com/Ed-von-Schleck/shoco/commits/master>
  - <https://github.com/Ed-von-Schleck/shoco/commit/c112c4e>
  - <https://github.com/Ed-von-Schleck/shoco/tree/master/models>
  - <https://github.com/Ed-von-Schleck/shoco/pulls>
  - <https://github.com/Ed-von-Schleck/shoco/pull/34>
  - <https://github.com/Ed-von-Schleck/shoco/pull/34/files>
  - <https://github.com/tmthrgd/shoco>
  - <https://raw.githubusercontent.com/siara-cc/Unishox2/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ed-von-schleck/shoco`) · [data/wave1/enrich/raw/github_com_ed_von_schleck_shoco.json](../../../data/wave1/enrich/raw/github_com_ed_von_schleck_shoco.json) (enrichment confidence 0.8)

</details>
