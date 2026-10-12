# libutf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small malloc-free C11 library for NFC, DUCET collation and grapheme clusters on raw UTF-8; first-party numbers beat ICU on short strings.

| | |
|---|---|
| **Beats** | ICU 78.3 (ICU4C: ubrk grapheme break iterator, unorm2 NFC, ucol DUCET collation) |
| **Claimed result** | README table (M5 Max, ICU 78.3), UTF-8 input with ICU paying u_strFromUTF8 conversion: NFC 28 ms vs 59 ms (2.1x), NFC quick-check 62 ms vs 237 ms (3.8x), collation 31 ms vs 40 ms (1.3x), grapheme segmentation 237 ms vs 337 ms (1.4x). Core-to-core (ICU on pre-converted UTF-16): NFC 28 ms vs 39 ms (libutf 1.4x), grapheme 237 ms vs 277 ms (libutf 1.2x), collation 31 ms vs 22 ms (ICU 1.4x faster). No core-to-core figure exists for quick-check. Numbers predate later correctness fixes to the grapheme, NFC and collation code. |
| **Workload** | Microbenchmarks on tiny fixed string sets, timed as totals with CLOCK_MONOTONIC: grapheme counting over 8 short strings x 200,000 iterations (bench_grapheme.c; ICU ubrk UBRK_CHARACTER iterator reused via ubrk_setText); NFC normalization of 10 short strings x 100,000 (bench_nfc.c; ICU unorm2_normalize into UTF-16); NFC quick-check of 9 already-NFC strings x 500,000 (bench_nfc_quickcheck.c; ICU u_strFromUTF8 plus unorm2_isNormalized); three-level comparison of 12 string pairs x 100,000 (bench_collate.c; ICU ucol_strcoll with ucol_open(""), i.e. CLDR root collation). The 'UTF-8 input' scenario times ICU including u_strFromUTF8 conversion; the 'core-to-core' scenario feeds ICU pre-converted UTF-16. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro, Apple M5 Max (stated in README) |
| **Compiler and flags** | Build lines in the bench/\*.c headers: gcc -O2 -I../include ... -L.. -lutf -lm \$(pkg-config --cflags --libs icu-uc [icu-i18n]); Makefile CFLAGS = -O2 -Wall -Wextra -std=c11 -g. Compiler version not stated (on macOS 'gcc' is normally an alias for Apple clang); ICU 78.3 origin and build flags not stated. |
| **Adoption** | 0 stars (new repo, first visible commit 2026-03-24); code extracted from TinyMUX, in production there since 2008 |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/brazilofmux/utf) · [benchmark](https://github.com/brazilofmux/utf) |

## Verdict

Author-run microbenchmarks on an Apple M5 Max against ICU 78.3 (gcc -O2 build lines, compiler version unstated) report, with ICU paying u_strFromUTF8 conversion, NFC 2.1x, NFC check 3.8x, collation 1.3x and grapheme counting 1.4x faster; with ICU on pre-converted UTF-16 the margins are NFC 1.4x and graphemes 1.2x for libutf, and ICU wins collation by 1.4x. Each figure is a single wall-clock total, with no warmup or repeats, over 8 to 12 short strings; outputs are never cross-checked between the libraries; the check benchmark pits a quick check against ICU's definitive isNormalized; the grapheme rules omit GB9c; and the numbers (2026-07-30) predate later changes to every measured path, including a rewrite of the NFC segment-boundary scan on 2026-08-13.

## Use it when

- C or C++ code that keeps text as UTF-8 and needs NFC normalization or an is-it-NFC check on short strings (identifiers, user names, keys, chat lines) without linking ICU.
- Root-order (DUCET) comparison or memcmp-able sort keys for short UTF-8 strings, including a case-insensitive comparison, when locale tailoring is not required.
- Footprint-constrained or dependency-free builds: about 702 KB static versus about 42 MB of ICU static libraries with full data (README), no malloc, no runtime dependencies.
- Terminal and MUD-style applications that need grapheme counting for Latin, CJK, Hangul and emoji, display width, and inline PUA color handling in one library.

## Skip it when

- Indic scripts or any text where grapheme clusters must follow Unicode 15.1+ rule GB9c: libutf has no InCB property, so a conjunct such as Devanagari 'स्ते' in the benchmark's 'नमस्ते' splits into two clusters where UAX #29 (and ICU 78) keeps one (by the rules; the benchmark never compares counts).
- Locale-sensitive sorting (tailorings such as Swedish or German phonebook), word, sentence or line breaking, bidi, NFD/NFKC/NFKD, case folding by locale, or Unicode 17 characters: use ICU.
- Long-document bulk throughput: all published numbers come from 8 to 12 short hand-written strings repeated 100,000 to 500,000 times, and the code is byte-at-a-time with no SIMD, so per-call overhead is what was measured.
- Projects that need a mature, widely reviewed dependency: single author, 0 stars, no CI, and the grapheme, NFC and collation code each received correctness fixes in August and September 2026 after the published numbers.
- Untrusted, possibly malformed UTF-8 for grapheme segmentation: utf_grapheme_next advances by the lead byte without validation, so malformed input is segmented arbitrarily.

## How it is fast

Unicode properties (CCC plus NFC_QC combined, decompositions, compositions, GCB, Extended_Pictographic, DUCET collation elements) are looked up through compressed byte-level DFAs generated from the UCD (state merging, column deduplication, RUN/COPY encoding), so UTF-8 is consumed directly with no UTF-16 conversion and no allocation. NFC copies already-normalized runs through and only decomposes, reorders and recomposes dirty segments, with an ASCII skip and algorithmic Hangul. Collation has a lazily built table for U+0000..U+017F that compares single-collation-element Latin characters inline, computed implicit weights for CJK, and bounded stack buffers for the general path. Grapheme segmentation is a hand-written UAX #29 rule loop that does two DFA property lookups per code point; it is not one fused DFA as the project article describes.

## Compared with alternatives

None of the catalogued siblings in font-shaping-text-layout does this job: displaywidth, uniwidth (Go) and uwcwidth (Python) only compute terminal display width, and HarfBuzz-style shapers do not normalize or collate. Pick libutf when a C program needs NFC, root collation and grapheme clusters on UTF-8 without ICU; the category fit is Unicode processing (ICU baseline), not shaping.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; ICU development headers only for the benchmarks and the tests/test_\*_icu.c differential tests; C++, Perl and the UCD files only to regenerate tables; Ragel only to regenerate color_ops.c |
| **Minimum toolchain** | C11 (Makefile: gcc -O2 -std=c11); &lt;stdatomic.h&gt; used unless __STDC_NO_ATOMICS__ or UTF_NO_ATOMICS is defined |
| **Platforms** | any (portable C, no SIMD or platform intrinsics); results published only for Apple M5 Max (macOS); Windows dllexport/dllimport macros exist but there is no CI for any platform |
| **Thread safety** | Functions are reentrant over const tables and caller buffers; the one piece of global state, the Latin collation cache, is initialised once with C11 atomics, but with UTF_NO_ATOMICS or a compiler without &lt;stdatomic.h&gt; it falls back to a plain flag that assumes a single thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- utf_nfc_is_nfc is a quick check: it returns 0 for NFC_QC=Maybe characters, so some text that is already NFC (a base letter plus a combining mark with no precomposed form) reports 'not NFC'; ICU's unorm2_isNormalized, which the benchmark compares against, gives a definitive answer.
- utf_nfc_normalize can expand text up to 3x: size dst with utf_nfc_normalize_bound() and check the returned status (UTF_NFC_TRUNCATED, or UTF_NFC_SEGMENT_TOO_LONG past 1024 code points in one combining sequence, raised with -DUTF_NFC_SEG_MAX).
- utf_collate_sortkey returns at most nKeyMax and gives no required-size answer when the key does not fit; a 16-bit weight that straddles the end is skipped, so the last byte of a truncated key can be left unwritten. Size key buffers generously. The final NFC tiebreak only considers the first 256 input bytes unless rebuilt with -DUTF_NFC_TIEBREAK_MAX.
- Collation is raw DUCET (allkeys.txt, Unicode 16.0) with no variable-weighting (shifted) option; ICU's ucol_open("") is CLDR root, which tailors DUCET, so results match ICU only where the two agree (33 tested pairs do).

## Known shortcomings

- Category moved to unicode-utf8 (ICU baseline), not font shaping. The NFC code changed after the numbers: commit c7537c0 (2026-08-13) rewrote the segment-boundary scan (HasBoundaryBefore, segment cap 128 to 1024) and the old code could drop text. The quick-check bench is not like-for-like: utf_nfc_is_nfc returns 0 on NFC_QC Maybe while ICU unorm2_isNormalized gives a definitive answer; the benches never cross-check outputs, and a Devanagari string yields 4 grapheme clusters against ICU's 3 (no GB9c). One wall-clock run, no warm-up. The article's single-pass DFA grapheme claim is false (a rule loop plus two DFA lookups per code point); sort-key truncation is unsignalled.
- Domain set to parsing-and-text to match its unicode-utf8 category.

## Caveats and trade-offs

First-party microbenchmark on 8 to 12 short hand-written strings repeated 100,000 to 500,000 times, so it measures per-call overhead, not bulk throughput; README reports totals only and no raw result files are checked in. The README numbers were refreshed on 2026-07-30, before correctness fixes to grapheme segmentation (GB4 after CR, GB11 single ZWJ, GB12/13 adjacent regional indicators, 2026-09-29), NFC (D115 blocked composition, 2026-08-01) and collation (NFC tiebreak buffer sizing, 2026-09-04); they have not been re-measured. Grapheme segmentation is not equivalent work: src/grapheme.c implements Unicode 16.0 rules GB3-GB13 without GB9c (Indic conjunct breaks, in UAX #29 since Unicode 15.1), so on the benchmark's Devanagari string it returns a different cluster count from ICU, which follows Unicode 17 in ICU 78.x; there is no GraphemeBreakTest conformance test in tests/ (only test_color_ops.c, test_nfc_icu.c, test_collate_icu.c). Unicode versions differ for all modules (libutf 16.0, ICU 78 is 17.0). The 'UTF-8 input' headline ratios charge ICU for u_strFromUTF8 even though ICU offers native UTF-8 paths that the benchmark does not use (ucol_strcollUTF8, UText via utext_openUTF8 with ubrk_setUText, C++ Normalizer2::normalizeUTF8 and isNormalizedUTF8); core-to-core the gaps shrink to 1.2x to 1.4x and ICU wins collation by 1.4x. ICU's collator is CLDR root collation (ucol_open("")), not raw DUCET. Compiler version and ICU 78.3 build configuration are not stated. NFC and collation are differentially tested against ICU (50 NFC cases plus a 100,000-input fuzz, 33 collation comparisons). Category fit: Unicode segmentation, normalization and collation (ICU baseline), not font shaping; HarfBuzz and FreeType do not apply.

Pure C11, no malloc, no dependencies, 702 KB static library versus about 42 MB for ICU static libraries (README). Works directly on UTF-8 with compressed DFAs, so its advantage is largest when the application holds UTF-8 and ICU has to convert to UTF-16. Covers only grapheme segmentation, NFC, collation (DUCET), classification and case/width tables; no word, sentence or line-break segmentation, no bidi, no locale-tailored collation, no shaping. Unicode 16.0.

## Maintenance

Active single-author project (48 commits, last 2026-09-29, issues #1 to #3 all closed), MIT-licensed and small enough to vendor, but young and unreviewed outside its author, so treat it as a compact ICU subset for UTF-8 C code and re-measure on your own strings.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness is public (bench/bench_grapheme.c, bench/bench_nfc.c, bench/bench_nfc_quickcheck.c, bench/bench_collate.c) with 'gcc -O2' build lines and an Apple M5 Max stated, but the README table (commit of 2026-07-30, 'Refresh benchmark numbers: MacBook Pro M5 Max, ICU 78.3') was measured on code later fixed for correctness (grapheme GB4, GB11 and GB12/13 fixes on 2026-09-29, NFC UAX #15 D115 fix on 2026-08-01, collation NFC tiebreak buffer fix on 2026-09-04). The grapheme comparison also does not do the same work as ICU: libutf implements Unicode 16.0 rules without GB9c (no InCB property at all), while ICU 78.x implements Unicode 17. The compiler version and the ICU build are unstated, so this is first-party evidence at C under the corrected-code precedent.
- **Verifier notes:** Downgraded A to C: harness is public and readable, but the published numbers predate correctness fixes to every benchmarked module, and the grapheme path skips GB9c and targets Unicode 16 against ICU's Unicode 17. NFC core-to-core 1.4x is the most like-for-like number (differentially tested against ICU). Category for the orchestrator: this is Unicode segmentation/normalization/collation and belongs in wave 3's unicode-utf8 category with the ICU baseline, not font-shaping-text-layout.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/README.md>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_grapheme.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_nfc.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_nfc_quickcheck.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_collate.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_collate_libutf.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/src/grapheme.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/grapheme.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/collate.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/tests/test_collate_icu.c>
  - <https://github.com/brazilofmux/utf/tree/main/bench>
  - <https://github.com/brazilofmux/utf/tree/main/tests>
  - <https://github.com/brazilofmux/utf/commits/main>
  - <https://github.com/brazilofmux/utf/commits/main/README.md>
  - <https://github.com/brazilofmux/utf/commits/main/src/grapheme.c>
  - <https://github.com/unicode-org/icu/releases>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/README.md>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/articles/beating-icu-at-unicode.md>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/src/collate.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/src/nfc.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/src/grapheme.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/src/classify.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/nfc.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/collate.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/grapheme.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/include/utf/utf_types.h>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_grapheme.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_nfc.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_nfc_quickcheck.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_collate.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/bench/bench_collate_libutf.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/tests/test_nfc_icu.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/tests/test_collate_icu.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/tests/test_color_ops.c>
  - <https://raw.githubusercontent.com/brazilofmux/utf/HEAD/gen/README.md>
  - <https://github.com/brazilofmux/utf>
  - <https://github.com/brazilofmux/utf/commits/main>
  - <https://github.com/brazilofmux/utf/commit/c7537c0>
  - <https://github.com/brazilofmux/utf/issues?q=is%3Aissue>
  - <https://github.com/brazilofmux/utf/tree/main/articles>
  - <https://github.com/brazilofmux/utf/tree/main/tests>
  - WebSearch: "Beating ICU at Unicode" libutf brazilofmux (no independent discussion found)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/brazilofmux/utf`) · [data/wave10/enrich/raw/github_com_brazilofmux_utf.json](../../../data/wave10/enrich/raw/github_com_brazilofmux_utf.json) (enrichment confidence 0.8)

</details>
