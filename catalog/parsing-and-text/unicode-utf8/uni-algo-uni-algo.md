# uni-algo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT OR Unlicense (LICENSE.md offers a 'Public Domain License' whose text is the Unlicense, or MIT)` · 🟡 stale

> Header-only C++17 Unicode library (UTF conversion, case, normalization, UAX #29 segmentation); its grapheme iteration runs 2.7-3.0x faster than ICU's.

| | |
|---|---|
| **Beats** | ICU (word break and extended grapheme cluster break iteration over UTF-16 text) |
| **Claimed result** | MSVC 19.12 x64, first of five runs, total ms for 50,000 strings (unit from the harness's std::chrono milliseconds): word breaks 2355.47 (uni-algo) vs 11379.4 (ICU), 4.83x; grapheme breaks 2067.16 vs 5600.95, 2.71x. MSVC 19.12 x86: word breaks 2544.55 vs 13137.1, 5.16x; grapheme breaks 2239.48 vs 6766.44, 3.02x (ratios derived from page data; the five runs agree within about 1%). GCC 7.3 -O3 rows show uni-algo alone (word 1467.2 ms x64, grapheme 1035.15 ms x64) because ICU was not built under MinGW. |
| **Workload** | Count UAX #29 word-break and extended-grapheme-cluster boundaries in 50,000 UTF-16 strings. Each string is three copies of the CC BY-SA 1.0 attribution paragraph in English, Latvian, Russian, Bengali, Chinese, Japanese and Korean (perf/perf_segment_utf16.h fill_1). uni-algo una::views::grapheme/word::utf16 with std::distance is compared against an ICU BreakIterator (createCharacterInstance/createWordInstance, US locale) first()/next() loop. Each figure is the total steady_clock time in milliseconds for all 50,000 strings (lower is better), repeated five times. |
| **Metric** | throughput |
| **Compiler and flags** | MSVC 19.12 (Visual Studio 2017 15.5.5), x64 and x86, flags not stated; GCC 7.3 x64/x86 '-03' (as written; presumably -O3) rows have the ICU column at 0; ICU version not stated |
| **Adoption** | 334 stars |
| **Last commit** | 2024-01-05 |
| **Links** | [repository](https://github.com/uni-algo/uni-algo) · [benchmark](https://github.com/uni-algo/uni-algo/blob/main/perf/result/segment_utf16.md) |

## Verdict

First-party perf/result/segment_utf16.md times 50,000 UTF-16 strings of 4,347 code units each (a seven-language CC BY-SA paragraph repeated three times) under MSVC 19.12 (VS 2017 15.5.5). ICU version, compiler flags and CPU are not stated. Grapheme breaks: 2067 vs 5601 ms on x64 (2.7x), about 210 vs 78 MB/s (derived from page and harness data), and 2239 vs 6766 ms on x86 (3.0x). Word breaks: 2355 vs 11379 ms on x64 (4.8x) and 2545 vs 13137 ms on x86 (5.2x), but that row compares different algorithms (see measurement_notes). GCC 7.3 rows time uni-algo alone.

## Use it when

- Counting or stepping through user-perceived characters (extended grapheme clusters) in UTF-8 or UTF-16 for cursor movement, truncation or text editing, where it measured about 2.7-3x faster than ICU's character BreakIterator.
- UAX #29 default word boundaries for space-delimited scripts (Latin, Cyrillic, Greek, Hebrew and similar), for example tokenizing with views::word_only.
- Builds that must avoid ICU: the only dependency is the C++ standard library, it compiles with -fno-exceptions and -fno-rtti, and UNI_ALGO_DISABLE_\* defines shrink the Unicode data that gets compiled.
- Untrusted text: ill-formed UTF sequences are replaced as The Unicode Standard recommends instead of causing errors or undefined behaviour.
- Projects that want public-domain (Unlicense text) or MIT licensing for vendoring.

## Skip it when

- Chinese, Japanese or Thai-style word segmentation where you need dictionary words: uni-algo returns one boundary per ideograph (UAX #29 default), while ICU's word iterator applies dictionary break engines.
- Line breaking (UAX #14), the bidirectional algorithm (UAX #9), full UCA collation or locale-tailored rules: none are implemented (the README lists them as future work).
- When you need current Unicode data: the library is at Unicode 15.1, the last commit was 2024-01-05, and issue #43 'Update to Unicode 17' is open.
- Word segmentation over single-pass input iterators or streams: the WB6/WB7b/WB12 lookahead needs at least forward iterators (stated in the source).
- Pre-C++17 toolchains: the CMake targets require cxx_std_17.

## How it is fast

Character properties come from generated two-stage lookup tables (stage2[(stage1[c &gt;&gt; 7] &lt;&lt; 7) + (c & 127)]). These feed a hand-written cascade of the UAX #29 rules (WB3 through WB999; grapheme rules including the Unicode 15.1 GB9c InCB states), whose small state struct keeps the previous one or two non-ignorable code points. Decoding is fused with segmentation: the view decodes UTF-16 or UTF-8, classifies and decides boundaries in one pass, with no copy into a library string type and no virtual call per boundary. Being templates in headers, the whole loop can be inlined; the perf harness even suggests __attribute__((flatten)). Word segmentation has no dictionary stage: CJK ideographs break at every code point under WB999. That avoids work ICU does, which inflates the word-break ratio (see measurement_notes).

## Compared with alternatives

Against libutf (brazilofmux/utf), which has a newer UTF-8 comparison with ICU 78.3 covering grapheme breaks, NFC and collation, pick uni-algo for C++17 range/view APIs over standard string types, a pure header-only option and dual public-domain/MIT licensing. fast-grapheme-segmenter and unicode-segmenter target Rust and JavaScript, not C++. For dictionary-based word segmentation or line breaking, ICU4X (catalogued for its line and word segmenters) or ICU itself is the better fit.

## Integration

| | |
|---|---|
| **Form** | header-only plus one compiled Unicode data .cpp by default (static or shared lib via CMake); UNI_ALGO_HEADER_ONLY gives a pure header-only, constexpr build; a single-include variant and a vcpkg port exist |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++17 (cxx_std_17), CMake 3.12+; the low-level functions also compile as C99 |
| **Platforms** | any; portable C++ with no SIMD or platform intrinsics (CI on Linux, Windows and macOS) |
| **Thread safety** | not documented (algorithms keep state in per-view or per-call structs and read constant tables) |
| **Drop-in for the baseline** | no |

## Gotchas

- views::word yields spaces and punctuation as words too (the README notes this); use views::word_only to get only words.
- Bounds-checked 'safe layer' iterators are on in debug builds and off in release unless UNI_ALGO_ENABLE_SAFE_LAYER is defined, so debug timings are not representative.
- Outside header-only mode the Unicode data .cpp must be compiled, and UNI_ALGO_DISABLE_\* config defines must be applied to that target (the README shows target_compile_definitions PUBLIC).
- views::nfc is only an input_range (open issue #45); the README says the one-call functions are faster than the ranges for single jobs.

## Known shortcomings

- Unicode segmentation (word and grapheme breaks), not shaping or layout; moved to wave 3's unicode-utf8 category (ICU baseline). Numbers come from perf/result/segment_utf16.md (ms total over 50,000 strings, perf/perf_segment_utf16.h), MSVC 2017 only, with no CPU model or ICU version. Licence is MIT OR Unlicense. Last commit 2024-01-05.
- The word-break 4.8x/5.2x rows are not like-for-like: ICU's word.txt rules send Han, Kana and Hangul to the dictionary engine while uni-algo applies plain UAX #29 (ideographs split by WB999), and CJK is about 15% of each test string (24% with Korean); the harness never compares break counts. The grapheme 2.7-3.0x rows are the fair headline. Numbers come from 2018 toolchains and older code; tables are stale at Unicode 15.1 (issue #43 open).

## Caveats and trade-offs

Category fit is weak: the benchmarked task is Unicode text segmentation, a pre-step of text layout, not font shaping or rasterization, and the baseline is ICU rather than HarfBuzz or FreeType. The result file states no units (the harness prints std::chrono milliseconds), no CPU model, no ICU version and no compiler flags for MSVC, and ICU was measured only under MSVC 2017. The results were committed in April 2023 ('Rename perf tests', 'Update perf tests') from a 2018-era toolchain, and the current harness has to be edited by hand (commented-out includes and defines, main5/generate_table) to reproduce them, so which library version produced the numbers is unclear. The ICU path copies each string into an icu::UnicodeString inside the timed loop; that is negligible next to about 228 microseconds per string for ICU word breaks (derived from page data). The author calls the perf tests 'a mess', and the README claims only performance 'at least the same as other implementations'. Only a UTF-16 test exists. The public-domain option carries no patent grant.

Header-only C++17 library with optional compiled Unicode data, UTF-8/16/32 support and safe iterators with bounds checks in debug. The README lists the Unicode Bidirectional Algorithm and the Line Breaking Algorithm as planned for future versions, so it does not yet cover bidi or line breaking, only word and grapheme segmentation (plus case, normalization and collation). Dual licensed Public Domain or MIT.

## Maintenance

Stale since 2024-01-05 (v1.2.0, Unicode 15.1; Unicode 17 update requested in open issue #43) but dual public-domain/MIT, dependency-free and easy to vendor, so it stays copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** perf/result/segment_utf16.md has five-run UNA vs ICU timings for MSVC 19.12 x64/x86, and the harness is public (perf/perf_segment_utf16.h), but no CPU model, flags or ICU version are given and the author calls the harness 'a mess', so it is first-party tier C.
- **Verifier notes:** The numbers match the result file exactly, and the units and workload are now filled in from the harness source. Category mismatch: this is Unicode segmentation (UAX #29), not shaping; the orchestrator should decide the category, for example text processing or Unicode. Metadata confirmed: 334 stars, last commit 2024-01-05 (stale), not archived, not a fork; the license is dual public-domain (Unlicense text)/MIT rather than MIT alone.
- **Fields the verifier corrected:** `license`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/uni-algo/uni-algo/blob/main/perf/result/segment_utf16.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/result/segment_utf16.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/perf_segment_utf16.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/main.cpp>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/README.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/LICENSE.md>
  - <https://github.com/uni-algo/uni-algo>
  - <https://github.com/uni-algo/uni-algo/tree/main/perf>
  - <https://github.com/uni-algo/uni-algo/commits/main>
  - <https://github.com/uni-algo/uni-algo/commits/main/perf/result/segment_utf16.md>
- **Sources the enricher read:**
  - <https://github.com/uni-algo/uni-algo>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/README.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/LICENSE.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/config.h>
  - <https://github.com/uni-algo/uni-algo/tree/main/include/uni_algo/impl>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/impl/impl_segment_word.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/impl/impl_segment_grapheme.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/impl/internal_stages.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/impl/impl_unicode_version.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/include/uni_algo/ranges_word.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/result/segment_utf16.md>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/perf_segment_utf16.h>
  - <https://raw.githubusercontent.com/uni-algo/uni-algo/main/perf/main.cpp>
  - <https://github.com/uni-algo/uni-algo/issues?q=is%3Aissue>
  - <https://github.com/uni-algo/uni-algo/issues/42>
  - <https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/data/brkitr/rules/word.txt>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/uni-algo/uni-algo`) · [data/wave10/enrich/raw/github_com_uni_algo_uni_algo.json](../../../data/wave10/enrich/raw/github_com_uni_algo_uni_algo.json) (enrichment confidence 0.75)

</details>
