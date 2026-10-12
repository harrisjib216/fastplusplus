# ICU (ICU4C collation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Unicode-3.0` · 🟢 active

> ICU4C's RuleBasedCollator: locale-aware UCA/CLDR string comparison and sort keys, charted by its authors as faster than glibc strcoll.

| | |
|---|---|
| **Beats** | glibc strcoll (glibc 2.12.3 in the ICU4C 3.8 chart, glibc 2.13 in the ICU4C 4.8 chart) |
| **Claimed result** | SNIPPET ONLY, not re-confirmed: the record's en_US (Latin data) figures of strcoll 199%, keygen 77%, keylen 99% in ICU4C's favour and ja_JP strcoll 421% (chart convention: positive favours ICU4C; values are chart deltas, not ratios) came from WebSearch text; this verifier's snippets confirm only that the ICU4C 4.8 vs glibc 2.13-1 chart shows ICU4C 'significantly better' on en_US strcoll. Independent (snippet only, thebuild.com 'Talk fast: the speed of various collations', PostgreSQL 17.1 on Ubuntu 24.04, 4 GB Linode, 1,000,000 rows of 64 random 7-bit ASCII characters, SELECT \* ORDER BY): ICU de-AT 770 ms vs libc de_AT 3645 ms (about 4.7x, derived from snippet data); ICU und-x-icu 765 ms; byte-order collations builtin C.UTF8 486 ms and libc POSIX 470 ms beat ICU. |
| **Workload** | String comparison (strcoll), sort key generation (keygen) and sort key length (keylen) of an ICU4C RuleBasedCollator with default options against glibc, over a large list of language-specific names, each operation repeated 1000 times, per locale. |
| **Metric** | throughput |
| **Adoption** | 3.6k stars (unicode-org/icu) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/unicode-org/icu) · [benchmark](https://icu.unicode.org/charts/collation-icu4c-glibc) |

## Verdict

The ICU project's own collation charts (icu.unicode.org, egress-blocked here, so known only from search snippets) run an ICU4C RuleBasedCollator with default options against glibc 2.12.3/2.13 strcoll and strxfrm over per-language name lists, 1000 passes per locale, and report percentage deltas favouring ICU on en_US strcoll; hardware and compiler were not readable. Independent PostgreSQL measurements (thebuild.com, PostgreSQL 17.1 on a 4 GB Linode: ICU de-AT 770 ms vs libc de_AT 3645 ms; pgsql-hackers: ICU about 13 ms vs en_US.utf8 about 73 ms) are also snippet-only and go through PostgreSQL's sort code.

## Use it when

- Sorting, comparing or indexing human-language text in many locales where glibc locale collation is the alternative, especially on glibc 2.21+ where strcoll regressed badly for some inputs.
- Databases and search indexes that store sort keys (e.g. PostgreSQL ICU collations): ICU keys are compact, versioned through the collator version, and consistent with ucol_strcoll.
- You need the same collation order on Linux, macOS, Windows, Android and Java (ICU4J), rather than whatever each platform's C library ships.
- Repeated comparisons of the same strings (sorting millions of rows): generate sort keys once and memcmp them, as ICU's guide recommends.
- You need tailoring options glibc lacks: numeric collation, alternate=shifted (ignore punctuation), case-first, script reordering, custom rules.

## Skip it when

- Byte or code-point order is acceptable: C/POSIX and PostgreSQL's builtin C.UTF8 sorted 1M random ASCII strings in 470-486 ms against 765-770 ms for ICU (thebuild.com, PostgreSQL 17.1, snippet only).
- Binary size matters: the full ICU data file (icudt64l.dat) is 27 MiB uncompressed and 11 MiB gzipped unless trimmed with the ICU Data Build Tool.
- Your text is UTF-8 and you call the UTF-16 APIs: converting first adds a pass (use ucol_strcollUTF8); specialised libraries such as libutf benchmark themselves faster than ICU 78.3 on UTF-8 input.
- Sort-key generation is the hot path: ICU's guide says generating keys for two strings is 5-10x slower than comparing them directly, and the ICU 53 v2 rewrite made ucol_getSortKey slower than v1 (snippet of the ICU v2 perf page).
- Stored sort keys or indexes must survive library upgrades unchanged: ICU says to regenerate keys whenever any part of ICU is updated.

## How it is fast

Since the ICU 53 collation v2 rewrite, compare first skips the identical prefix of both strings, then takes a fast-Latin path (CollationFastLatin: a precomputed weight table for U+0000..U+017F and U+2000..U+203F) and otherwise walks collation elements incrementally through a code-point trie, stopping at the first primary difference instead of building full keys. Root data is shared read-only, and only small tailoring tables are per locale. Sort keys are compressed (primary-weight compression and run-length compression of common secondary/tertiary weights), which is what the 'keylen' chart column rewards.

## Compared with alternatives

Pick ICU4C when you need full CLDR locale coverage, tailorings and versioned sort keys from C or C++. libutf benchmarks faster collation and NFC than ICU 78.3 on UTF-8 input, and ICU4X is the Rust rewrite with smaller data, so consider them when DUCET-style ordering suffices or a Rust dependency is fine. ICU is also the baseline that most siblings (libutf, uni-algo, encoding_rs, Boost.Text) measure against, so it is the safe default rather than the fastest option.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libicuuc + libicui18n + libicudata (data can be filtered by locale and feature with the ICU Data Build Tool); usually already installed as a system library |
| **Minimum toolchain** | Building ICU4C requires C11 and C++17 (user guide); the C API (ucol_\*) is callable from C |
| **Platforms** | Linux, macOS, Windows (MSVC 2017/2019 project files, Cygwin), Android and others; portable C/C++ with no SIMD requirement |
| **Thread safety** | Const APIs of one collator can be used concurrently, and a frozen Collator can be shared across threads; for non-const use clone a collator per thread (ICU design guide). |
| **Drop-in for the baseline** | no |

## Gotchas

- Stale baseline behind the claim: the first-party charts compare ICU4C 3.8 with glibc 2.12.3 and ICU4C 4.8 with glibc 2.13 (about 2008-2011). Both sides changed afterwards: glibc's 2014 strcoll rewrite (bug 15884, cache removed, 22-42% faster in most locales per the patch thread, snippet only) and its later regression for strings that differ late in multibyte text, and ICU 53's collation v2 (compareUTF8 up to 4.7x faster than ICU 52, getSortKey slower). The chart percentages are deltas, not ratios, and the chart says strcoll swings about 10% with code alignment.
- The public harness (icu4c/source/test/perf/collationperf/collperf.cpp) feeds ICU UTF-16 strings and feeds glibc UTF-8 copies converted up front, times whole loops with gettimeofday at millisecond resolution, measures key length with strlen, and never checks that both libraries produce the same order. They do not: CLDR and glibc locale data sort differently, so the comparison is between two different collations, not one function done faster.
- PostgreSQL numbers mix library speed with PostgreSQL policy: per the verifier, PostgreSQL uses abbreviated sort keys for ICU collations but disables them for libc, so the 4.7x (thebuild.com, de-AT) is partly PostgreSQL's sort path. A pgsql-hackers thread, 'Slow performance of collate en_US.utf8' (snippet only), reports C about 4.8 ms, ICU about 13 ms and glibc en_US.utf8 about 73 ms, and says glibc 2.17 performed about the same as ICU, so ICU's lead depends heavily on glibc version and input shape.
- Sort keys and collation order change between ICU/CLDR versions; check the collator version and rebuild indexes after upgrades. Turning on normalization mode costs 10-40% in comparisons per ICU's guide; the C++ API has no stable ABI, so system libraries should expose only the C API (symbols carry a version suffix).

## Known shortcomings

- Tier C: ICU4C collation charts are first-party from 2008-2011 and seen only in search snippets (the 199% / 421% figures not re-confirmed; icu.unicode.org blocked). The independent thebuild.com number (ICU de-AT 770 ms vs libc de_AT 3645 ms, about 4.7x) is also snippet-only and confounded: PostgreSQL uses abbreviated keys for ICU but not for libc. Not a duplicate of icu4x.
- Enricher: the collation chart compares ICU 3.8/4.8 with glibc 2.12.3/2.13, before glibc's 2014 strcoll rewrite (bug 15884) and ICU 53's collation v2 (getSortKey got slower); collperf.cpp never checks that both sides produce the same order (CLDR vs ISO 14651 sort differently), uses a millisecond gettimeofday timer and feeds ICU UTF-16 but glibc UTF-8. Snippet-only newer evidence (pgsql-hackers 'Slow performance of collate en_US.utf8'): C 4.8 ms, ICU 13 ms, glibc en_US.utf8 73 ms; glibc 2.17 about equal to ICU, the regression is in glibc 2.21+; C/POSIX/C.UTF8 beat ICU.
- Domain set to parsing-and-text to match its unicode-utf8 category.

## Caveats and trade-offs

SNIPPET ONLY: icu.unicode.org (both https://icu.unicode.org/charts/collation-icu4c-glibc and the ICU4C 4.8 chart at https://icu.unicode.org/charts/collation-icu4c48-glibc), thebuild.com, the PostgreSQL mailing list and lists.gnupg.org were not opened (egress-blocked), so all numbers come from WebSearch result text; the exact percentages could not be re-confirmed and the chart's platform, CPU and compiler fields were not readable. Chart percentages are deltas, not ratios. Charts are old: ICU4C 3.8 versus glibc 2.12.3 and ICU4C 4.8 versus glibc 2.13 (about 2008 to 2011); both libraries have changed since. The chart page reportedly warns results vary with hardware and compiler and that strcoll is sensitive to code alignment (10% swings). The benchmark code is public (icu4c/source/test/perf/collationperf/collperf.cpp, which times ICU ucol_strcoll/sort keys against Unix strcoll/strxfrm with a -unix flag) but no committed results were found. The independent PostgreSQL measurement (thebuild.com, 2024) uses random ASCII strings rather than natural text and is confounded by PostgreSQL itself: abbreviated sort keys are used for ICU collations but disabled for libc collations, so part of the 4.7x is PostgreSQL's sort path, not raw strcoll speed. A second snippet-only claim: a PostgreSQL mailing-list message reports ICU normalization at 0.861 s and 0.651 s against PostgreSQL's built-in 4.024 s and 6.655 s on two conversions (hardware and method unknown). The guessed baseline 'standard UTF-8 processing' does not match any evidence; this is a collation and normalization claim. ICU is also the incumbent that other Unicode libraries benchmark against. [retier] First-party collperf charts (2008-2011, snippet-only; icu.unicode.org blocked) predate glibc's 2014 strcoll rewrite and ICU 53 collation v2; harness checks no order equality (CLDR vs ISO 14651), millisecond timer, UTF-16 vs UTF-8 inputs. pgsql-hackers snippet: C 4.8 ms, ICU 13 ms, glibc en_US.utf8 73 ms (glibc 2.21+ regression; glibc 2.17 about equal to ICU); PostgreSQL abbreviated keys confound the thebuild.com 4.7x.

Large library with its own data tables; UTF-16 is its native string form; ICU4C offers C and C++ APIs; Unicode-3.0 license (older releases used the ICU license).

## Maintenance

Actively maintained (last commit 2026-10-06, Unicode-3.0 licence) and installed on almost every OS, so adoption is easy; but the speed evidence is a 2008-2011 first-party chart against a pre-2014 glibc plus snippet-only PostgreSQL numbers, so treat it as the correct-and-usually-faster default for locale collation rather than a measured speed library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The ICU project's own collation charts (first-party) compare ICU4C against glibc, but icu.unicode.org is egress-blocked, so the page was not opened and the record's percentages remain snippet-only; the only independent number found (thebuild.com, PostgreSQL 17.1) is also snippet-only from a blocked blog, so the tier stays C. The benchmark program collperf.cpp is public but no CPU, compiler or flags were readable.
- **Retiered** C to D: The only numbers are first-party 2008-2011 charts seen in search snippets (ICU 3.8/4.8 vs glibc 2.12/2.13, both since rewritten), produced by a harness that never checks the two sides sort identically, times with a millisecond clock and feeds ICU UTF-16 against glibc UTF-8; newer evidence is snippet-only and confounded. Directional only.
- **Verifier notes:** Metadata confirmed (3.6k stars, LICENSE is Unicode License V3 = Unicode-3.0, last commit 2026-10-06, not archived); not a duplicate (wave 10 lists unicode-org/icu4x, a different project). Shortcomings: first-party 2008-2011 charts readable only through search snippets; the one independent number is snippet-only and confounded by PostgreSQL's abbreviated-key policy; ICU's byte-order rivals (C.UTF8, POSIX) are faster.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 1); enricher (wave 1); orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/unicode-org/icu>
  - <https://github.com/unicode-org/icu/commits>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/test/perf/collationperf/readme.html>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/test/perf/collationperf/collperf.cpp>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/README.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/readme.html>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/test/perf/collationperf/collperf.cpp>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/test/perf/collationperf/readme.html>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/collation/index.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/collation/concepts.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/collation/architecture.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/collation/api.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/icu/design.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/icu_data/buildtool.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/docs/userguide/icu4c/build.md>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/i18n/collationfastlatin.h>
  - <https://raw.githubusercontent.com/unicode-org/icu/HEAD/icu4c/source/i18n/rulebasedcollator.cpp>
  - https://icu.unicode.org/charts/collation-icu4c-glibc (EGRESS_BLOCKED; WebSearch snippets only)
  - https://icu.unicode.org/design/collation/v2/perf (WebSearch snippet only)
  - https://sourceware.org/ml/glibc-cvs/2014-q4/msg00058.html (WebSearch snippet only)
  - https://thebuild.com/blog/talk-fast-the-speed-of-various-collations/ (WebSearch snippet only)
  - https://www.postgresql.org/message-id/bc394bbb-c325-4b2b-b443-0fad58781b0f%40postgrespro.ru (EGRESS_BLOCKED; WebSearch snippets only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/unicode-org/icu`) · [data/wave1/enrich/raw/github_com_unicode_org_icu.json](../../../data/wave1/enrich/raw/github_com_unicode_org_icu.json) (enrichment confidence 0.6)

</details>
