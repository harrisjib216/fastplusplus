# libgrapheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `ISC` · 🟢 active

> Tiny freestanding C99 Unicode segmentation and case-mapping library; claims to beat libutf8proc, ICU and libunistring, with no published numbers.

| | |
|---|---|
| **Beats** | libutf8proc (the only library the repo's benchmark/ programs compare against: grapheme cluster break and UTF-8 decode); the README also names ICU and GNU libunistring, but no benchmark against them exists |
| **Claimed result** | No numbers. README: 'It is also way smaller and much faster than the other established Unicode string libraries (ICU, GNU's libunistring, libutf8proc).' |
| **Workload** | Repo benchmark/: character.c times grapheme_is_character_break against utf8proc_grapheme_break_stateful over the Unicode grapheme-break conformance test codepoints (100,000 iterations); utf8-decode.c times grapheme_decode_utf8 against utf8proc_iterate over the same strings encoded as UTF-8. word.c, sentence.c, line.c and case.c time libgrapheme alone (no comparison), and bidirectional.c is an empty stub. Timing uses clock() (CPU time) in benchmark/util.c, which prints the percentage faster or slower than the first run. |
| **Metric** | throughput |
| **Compiler and flags** | Repo default config.mk: CC=cc, CFLAGS=-std=c99 -Os -Wall -Wextra -Wpedantic; benchmark binaries link -lutf8proc; no published benchmark run |
| **Adoption** | 15 stars on the author's GitHub copy; canonical repo is git.suckless.org/libgrapheme (blocked here); suckless library |
| **Last commit** | 2025-12-24 |
| **Links** | [repository](https://github.com/FRIGN/libgrapheme) · [benchmark](https://github.com/FRIGN/libgrapheme) |

## Verdict

Nothing was measured on the record: the README says 'way smaller and much faster' than ICU, libunistring and libutf8proc with no numbers, and the repo's character and utf8-decode benchmarks (clock() CPU time, 100,000 passes over the GraphemeBreakTest codepoints, libgrapheme static at -Os against a dynamically linked libutf8proc) print run-time ratios that were never published. The benchmark's label that libutf8proc's decoder is 'unsafe (does not detect overlong encodings)' is stale: current utf8proc_iterate rejects overlong 2-, 3- and 4-byte forms and surrogates, and the generated input is valid UTF-8 anyway, so the decode comparison is like-for-like on validation.

## Use it when

- C or C++ code that needs correct grapheme-cluster counting or cursor movement (terminals, text editors, TUI widgets) without pulling in ICU.
- Bare-metal or libc-free builds: the library is freestanding and the shared object links with -nostdlib.
- Word and sentence segmentation or Unicode case conversion of short strings where a small ISC-licensed dependency matters more than measured peak throughput.
- Replacing utf8proc only for grapheme breaking and UTF-8 decoding, where the bundled benchmarks give you a ready comparison to run on your own hardware.

## Skip it when

- Line breaking or bidirectional layout on Unicode 16/17 text: the author's own 17.0.0 data-update commit says line-segmentation and bidi conformance tests fail, and src/line.c has no LB15a-d, LB19a, LB20a or LB28a rules.
- You need normalization (NFC/NFD), case folding for comparison, collation or locale-tailored breaking: use ICU, utf8proc or a sibling with those features.
- You need demonstrated speed: no benchmark result has ever been published, so measure with make benchmark before relying on the 'much faster' claim.
- Bulk UTF-8 validation or transcoding throughput: the decoder is scalar per codepoint with no SIMD, so SIMD validators in this category are far faster for that job.

## How it is fast

Property lookup is a two-stage table generated from the Unicode data (major[cp &gt;&gt; 8] + (cp & 0xFF) into a byte-sized minor table), and the UAX #29 pair rules are precomputed bitmask tables, so a break decision is a couple of loads and AND tests instead of utf8proc's branch chain over a larger property struct. The stateful break call caches the right-hand codepoint's property inside a 16-bit caller-held state, so a scan does one table lookup per codepoint where utf8proc_grapheme_break_stateful looks up both codepoints on every call. There is no SIMD and no ASCII fast path; the UTF-8 decoder is a scalar per-codepoint loop.

## Compared with alternatives

Pick libgrapheme over uni-algo or libutf when you want plain C99, zero dependencies, an ISC license and grapheme, word and sentence segmentation plus case mapping in a few hundred KB; pick uni-algo (C++) or libutf when you need normalization or collation or want numbers measured against ICU, which libgrapheme lacks.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (one POSIX Makefile plus ./configure; installs grapheme.h, man pages and a pkg-config file) |
| **Dependencies** | none at run time (freestanding); benchmarks link -lutf8proc |
| **Minimum toolchain** | any C99 compiler and POSIX make |
| **Platforms** | any (portable C99, no architecture-specific code) |
| **Thread safety** | Not documented; the code read keeps all state in caller-held variables (uint_least16_t for grapheme breaks) and only const lookup tables, so the functions are reentrant in practice. |
| **Drop-in for the baseline** | partial — grapheme_is_character_break and grapheme_decode_utf8 map one-to-one onto utf8proc_grapheme_break_stateful and utf8proc_iterate, but with different state and error conventions, and there is no equivalent of utf8proc's normalization or case folding |

## Gotchas

- Once the state has been used, grapheme_is_character_break ignores cp0 and reuses the property cached from the previous call's cp1; reset the state to 0 for each new string or after skipping codepoints.
- grapheme_decode_utf8 maps invalid sequences to U+FFFD and returns the bytes consumed, but returns a value larger than len for a truncated trailing sequence; callers must check ret &gt; len.
- The default config.mk builds with -Os and strips binaries (LDFLAGS -s); set CFLAGS to -O2 or -O3 for speed-sensitive builds, and expect make test to report failures for line and bidi on the shipped 17.0.0 data.
- src/character.c starts with a stray #include &lt;stdio.h&gt; ahead of the license header, which can break a truly libc-less freestanding toolchain despite the freestanding claim.

## Known shortcomings

- Category moved to unicode-utf8. No number in the repo: benchmark/character.c (grapheme_is_character_break) and utf8-decode.c compare libutf8proc only, the word, sentence, line and case benchmarks time libgrapheme alone, and bidirectional.c is empty; the 'twice as fast' claim against libutf8proc exists only in a search snippet of a blocked May 2022 suckless dev-list post, so the baseline narrows to libutf8proc and the tier is D.
- Enricher (2026-10-04): nothing is measured on the record; the README's 'way smaller and much faster' than ICU, libunistring and libutf8proc has no numbers, and the repo's benchmarks (clock() CPU time, 100,000 passes over GraphemeBreakTest codepoints, libgrapheme static at -Os against a dynamically linked libutf8proc) print ratios that were never published. Its label that libutf8proc's decoder is 'unsafe' is stale (current utf8proc_iterate rejects overlong forms and surrogates). Gotchas: grapheme_is_character_break reuses the cached cp1 property once state is non-zero (reset state per string); grapheme_decode_utf8 returns more than len for a truncated trailing sequence; default config.mk builds -Os and strips; make test fails line and bidi on the shipped 17.0.0 data (half-finished gen2 generator); stray #include &lt;stdio.h&gt; ahead of the license header in src/character.c. Single-maintainer, 3.0.0 on 2025-12-24 after a year idle. Tier D stands.
- Domain set to parsing-and-text to match its unicode-utf8 category.

## Caveats and trade-offs

Tier D slot: the claim is qualitative. The repo ships benchmark programs (make benchmark, links -lutf8proc) but publishes no results, hardware or flags; no ICU or libunistring benchmark exists. Benchmark asymmetries a reproducer should know: libgrapheme is linked statically (libgrapheme.a) while libutf8proc is linked dynamically; the wrapper functions are marked optnone under clang; the default config.mk builds with -Os; and the UTF-8 decode run itself labels libutf8proc 'unsafe (does not detect overlong encodings)', so the two decoders do different validation work. A search snippet of a blocked May 2022 suckless dev mailing-list post by the author says libgrapheme became 'twice as fast' as libutf8proc for grapheme cluster counting (snippet only, no methodology, code predating the 3.0.0 LUT rework). README conformance section still says Unicode 15.0.0 while the intro says 17.0.0 (version 3.0.0, 2025-12-24). The library is a grapheme, word, sentence and line-break segmenter plus case converter, not a shaper, so it belongs in unicode-utf8. Canonical repo is git.suckless.org/libgrapheme (blocked here); the GitHub copy has 15 stars.

Freestanding C99 library, no libc needed at runtime, heavily compressed lookup tables generated from Unicode 17.0.0 data, about 400 KB per the suckless page snippet. Scope is segmentation, case mapping and bidi only: no normalization, no shaping, no collation, no locale handling (ICU covers all of those).

## Maintenance

Single-maintainer suckless project, version 3.0.0 released 2025-12-24 after a year without commits, ISC-licensed and small enough to vendor; the half-finished move to a new table generator (gen2, wired only into a generator and not into src/) leaves line breaking and bidi below Unicode 17.0.0 conformance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README claims 'way smaller and much faster' than ICU, GNU libunistring and libutf8proc with no numbers, and no result, hardware or flags file exists in the repo; benchmark/character.c and benchmark/utf8-decode.c compare against libutf8proc only and print ratios at run time, never published. A 'twice as fast as libutf8proc' remark exists only in a search snippet of a blocked May 2022 suckless dev mailing-list post (no methodology, pre-3.0 code), which is not enough to lift the tier here.
- **Verifier notes:** No number exists in the repo; confirmed at D. Category should move from font-shaping-text-layout to unicode-utf8 (category is not a correctable field here, so set it through decisions.json). License ISC, last commit 2025-12-24 and 15 stars confirmed.
- **Fields the verifier corrected:** `baseline`, `workload`, `caveats`
- **Shortcomings recorded by:** none; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/FRIGN/libgrapheme>
  - <https://github.com/FRIGN/libgrapheme/commits>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/README>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/config.mk>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/Makefile>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/util.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/util.h>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/character.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/utf8-decode.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/word.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/sentence.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/line.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/case.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/bidirectional.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/README>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/grapheme.h>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/config.mk>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/Makefile>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/util.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/util.h>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/character.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/benchmark/utf8-decode.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/character.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/utf8.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/util.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/util.h>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/word.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/case.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/line.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/src/bidirectional.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/gen/line.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/gen/line-test.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/gen/util.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/test/line.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/test/util.c>
  - <https://raw.githubusercontent.com/FRIGN/libgrapheme/HEAD/data/LineBreakTest.txt>
  - <https://github.com/FRIGN/libgrapheme/commits>
  - <https://github.com/FRIGN/libgrapheme/commit/2f5fb9740e29dd344ec8fbbcde966b71fcd3ffcf>
  - <https://github.com/FRIGN/libgrapheme/commit/5c252ef6a4a7f82364bc59c2733d858c3c7927e0>
  - <https://github.com/FRIGN/libgrapheme/commit/40bc7dffb7a0ae319dba093809fc2f27a59ed8d1>
  - <https://raw.githubusercontent.com/JuliaStrings/utf8proc/HEAD/utf8proc.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/frign/libgrapheme`) · [data/wave10/enrich/raw/github_com_frign_libgrapheme.json](../../../data/wave10/enrich/raw/github_com_frign_libgrapheme.json) (enrichment confidence 0.75)

</details>
