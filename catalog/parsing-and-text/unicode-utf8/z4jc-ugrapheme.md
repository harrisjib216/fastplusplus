# ugrapheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Cython (Python)` · `0BSD` · 🟡 stale

> Cython UAX #29 grapheme splitter for CPython; about 8x faster than ICU's BreakIterator driven through PyICU on a short string.

| | |
|---|---|
| **Beats** | ICU's character BreakIterator called through PyICU (the Python binding to ICU's C++ library), driven by a Python generator; also pyuegc, uniseg and grapheme (the other Python grapheme splitters) |
| **Claimed result** | README %%timeit means: ugrapheme grapheme_split 337 ns vs PyICU BreakIterator loop 2.84 us (8.4x, derived from page data; README says 8x); pyuegc EGC 8.19 us vs 337 ns (24x; the section heading says 25x); uniseg 14.6 us vs 340 ns (README says 45x; 43x derived from page data; wrong split of a Devanagari conjunct); grapheme 17.4 us vs 332 ns (52x; also wrong split). |
| **Workload** | Splitting one short string of 15 extended grapheme clusters ('Hello', '!', spaces, two emoji ZWJ sequences with skin-tone modifiers and the Devanagari word अनुच्छेद) into a list of grapheme strings (UAX #29), timed with IPython %%timeit (mean of 7 runs of 100,000 or 1,000,000 loops). |
| **Metric** | latency |
| **Adoption** | 40 stars, 2 forks; PyPI ugrapheme 0.8 with wheels for CPython 3.8+ |
| **Last commit** | 2024-10-28 |
| **Links** | [repository](https://github.com/Z4JC/ugrapheme) · [benchmark](https://github.com/Z4JC/ugrapheme) |

## Verdict

First-party IPython %%timeit means on one 15-cluster string: grapheme_split 337 ns against 2.84 us for ICU's character BreakIterator called through PyICU from a Python generator that converts to icu.UnicodeString and builds one str per cluster (8.4x), and against 8.19 us for pyuegc, 14.6 us for uniseg and 17.4 us for grapheme (the last two split wrongly). No CPU, OS or Python/PyICU/ICU versions are stated and there is no benchmark script, so the 8.4x is mostly binding overhead on a tiny input rather than ICU's C++ segmentation. In this session, on an Intel Xeon 2.1 GHz cloud VM with Python 3.11.15 and the 0.8 wheel, the same call took about 417 ns (best of 7) and passed all 1,093 Unicode 16.0 GraphemeBreakTest cases; PyICU was not installed, so the ICU ratio was not re-measured.

## Use it when

- CPython code that needs user-perceived character counts, indexing, truncation or reversal of emoji, Indic conjunct, Hangul or flag text.
- Hot paths over many short strings (chat messages, UI labels, terminal cells), where ICU via PyICU loses most of its time to binding calls and UnicodeString conversion.
- Replacing the pure-Python grapheme or uniseg packages, which the README shows splitting the Devanagari conjunct च्छे wrongly and running 43-52x slower.
- Cython projects that can cimport the provided .pxd files for typed grapheme operations without Python-call overhead.
- Long text: in this session grapheme_split did 31,000 mixed code points in about 0.37 ms, and grapheme_len did ASCII at about 4 GB/s (Xeon VM, Python 3.11, indicative only).

## Skip it when

- C or C++ code: this is a CPython-only extension, and the segmentation core is Cython cdef functions with no C API.
- Word, line or sentence breaking, locale tailoring, or Unicode 17 tables: it implements only extended grapheme clusters at Unicode 16.0 and has had no commits since 2024-10-28.
- Code that multiplies graphemes objects (g \* n): replication builds a wrong grapheme index in common edge cases (see gotchas).
- Platforms without a published wheel (CPython 3.14+, Linux aarch64, PyPy): pip has to build from the sdist with Cython and a C compiler.
- When you need the Python-side table generator: the generation scripts are not in the repository (issue #2, open since October 2024).

## How it is fast

Grapheme_Cluster_Break, InCB and Extended_Pictographic properties are stored as two-level sparse bitmaps, under 11 KB in total, so a lookup is two loads plus shifts after an unsigned range compare. The UAX #29 rules are a small hand-written state machine over (state, current, next) code points with an early exit for any pair below U+0300. Separate loops read CPython's PEP 393 1-, 2- and 4-byte string storage in place, so nothing is decoded or copied (Latin-1 strings only test for CR LF), and output slices are built straight from that buffer with PyUnicode_FromKindAndData.

## Compared with alternatives

Pick it when the caller is CPython. uni-algo and libutf are the catalogued choices for native C/C++ grapheme breaking against ICU4C, and fast-grapheme-segmenter (Rust) and unicode-segmenter (JavaScript) cover their own runtimes. The jquast wcwidth package (0.9.1) now ships iter_graphemes too, but it ran about 55x slower than grapheme_split on the README string in this session.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | uwcwidth (runtime); Cython, setuptools and a C compiler only when building from source |
| **Minimum toolchain** | CPython 3.8+ (0.8 wheels cover cp38-cp313 for manylinux x86-64/i686, musllinux, macOS arm64 and Windows; built with -O3 on non-MSVC compilers) |
| **Platforms** | CPython only; prebuilt wheels for x86-64 and i686 Linux, Windows and macOS arm64; other targets build from the sdist |
| **Thread safety** | Not documented. The standalone functions keep no mutable state and run while holding the GIL (no nogil sections); graphemes objects are immutable values (+= returns a new object). The module keeps a static cache of single-character Latin-1 strings that is filled at init time, and free-threaded CPython is not addressed. |
| **Drop-in for the baseline** | partial — it replaces the README's PyICU BreakIterator generator one-for-one for grapheme splitting of Python strings, but it has no BreakIterator API, no other boundary types, no locales and no UTF-16 offsets |

## Gotchas

- Correctness bug in replication (graphemes.__mul__), reproduced in this session with the PyPI 0.8 wheel; grapheme_split, grapheme_len, the constructor and + all agreed with each other in a 100,000-case fuzz. First, grapheme_calc_tran checks `upos >= len - upos` instead of `upos >= len`, so when the last grapheme starts in the second half of the string it returns state 0 and the seam check is skipped: len(graphemes('कखक्') \* 2) is 6, but grapheme_len('कखक्' \* 2) is 5. Second, the slow path for count &gt;= 3 assumes every seam merges the same way, so len(graphemes('🇭') \* 4) is 1 and iteration yields only '🇭🇭' although str() holds all four. About 10% of random short strings gave a wrong list(g \* 3); tests/test_graphemes.py covers replication only for CR LF and a split ZWJ emoji.
- Slicing a graphemes object returns a plain str, so further slicing counts code points again (README gotcha; also the cause of closed issue #5). Use gslice to stay in graphemes.
- Negative positions are inconsistent (open issue #7): grapheme_slice clamps a negative start to 0, so grapheme_slice('abcdef', -2) returns 'abcdef', while graphemes('abcdef').gslice(-2) returns 'ef'; grapheme_at returns '' for negative positions.
- graphemes objects are limited to 4,294,967,294 code points and add about 4 bytes per character for the offset table; the standalone grapheme_\* functions have no length limit and do not allocate an index.

## Known shortcomings

- Cython/Python grapheme splitter (language-filter mismatch). README %%timeit on one 15-grapheme string with no machine, Python or ICU version; the PyICU baseline is a Python generator plus binding overhead, so the 8.4x is not ICU's C++ speed. Unicode segmentation, moved to wave 3's unicode-utf8 category (ICU baseline).
- grapheme_split (the benchmarked path) passes all 1,093 GraphemeBreakTest-16.0 cases (417 ns on a Xeon 2.1 GHz VM against the README's 337 ns; the ICU ratio was not re-measured). Correctness bug outside the benchmark: graphemes.__mul__ builds a wrong grapheme index because grapheme_calc_tran checks upos &gt;= len-upos instead of upos &gt;= len (len(graphemes('कखक्')\*2) is 6, true value 5) and the count-of-3-or-more path assumes every seam merges the same way (len(graphemes('🇭')\*4) is 1 and iteration drops text; about 10% of random short strings fail g\*3); issue #7 confirmed (grapheme_slice clamps a negative start to 0). wcwidth 0.9.1 now ships iter_graphemes, about 55x slower, differing on one string (GB9c).

## Caveats and trade-offs

First-party IPython %%timeit sessions on a single 15-grapheme string; no CPU, OS, Python, Cython, PyICU or ICU version stated (a separate ASCII throughput remark cites only 'a fast 2024 laptop') and no benchmark script in the repo. The PyICU harness converts the input to icu.UnicodeString, calls nextBoundary() once per grapheme through the binding inside a Python generator and builds a Python str per slice, so the 8.4x gap mostly measures CPython and binding overhead on a tiny input, not ICU's C++ segmentation; there is no comparison against ICU from C or C++ or on long text. Unicode versions are not matched: ugrapheme passes the Unicode 16.0 GraphemeBreakTest, while the ICU and pyuegc versions used are not given; uniseg and grapheme produce wrong splits, so their ratios compare unequal output. CPython-only extension, not callable from C++. Belongs in Unicode segmentation (wave 3 unicode-utf8), not font shaping. Last commit and last release (0.8) on 2024-10-28.

Cython extension with sparse bitmap property tables (under 11 KB) and a small DFA; passes the Unicode 16.0 UAX #29 grapheme break tests; behaves like a Python str with grapheme indexing; needs a compiled wheel.

## Maintenance

Stale (last commit and release 0.8 on 2024-10-28, 40 stars, four open issues including the negative-slicing report #7), but 0BSD-licensed with wheels up to CPython 3.13; safe for the standalone split, length and slice functions, while g \* n should be avoided until the replication bug is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party IPython %%timeit sessions in the README, with the PyICU harness code shown, but no benchmark script in the repo and no CPU, OS, Python, PyICU or ICU version stated.
- **Verifier notes:** PyICU wraps ICU, a listed incumbent for the unicode-utf8 category, so baseline_in_list is set to true with the binding-overhead caveat; suggest a category override to unicode-utf8 (category is not correctable here) and language Cython. Minor README slip: it says PyICU boundaries index a UTF-8 representation, but ICU UnicodeString offsets are UTF-16 code units; this does not affect the timings. Metadata (0BSD, 40 stars, last commit 2024-10-28, stale) confirmed.
- **Fields the verifier corrected:** `baseline_in_list`, `baseline`, `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/README.md>
  - <https://github.com/Z4JC/ugrapheme>
  - <https://github.com/Z4JC/ugrapheme/commits>
  - <https://pypi.org/pypi/ugrapheme/json>
- **Sources the enricher read:**
  - <https://github.com/Z4JC/ugrapheme>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/README.md>
  - <https://github.com/Z4JC/ugrapheme/issues?q=is%3Aissue>
  - <https://github.com/Z4JC/ugrapheme/issues/1>
  - <https://github.com/Z4JC/ugrapheme/issues/2>
  - <https://github.com/Z4JC/ugrapheme/issues/5>
  - <https://github.com/Z4JC/ugrapheme/issues/7>
  - <https://github.com/Z4JC/ugrapheme/tree/main/ugrapheme>
  - <https://github.com/Z4JC/ugrapheme/tree/main/tests>
  - <https://github.com/Z4JC/ugrapheme/tree/main/ugrapheme_diag>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/ugrapheme.pyx>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/ugrapheme.pxd>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/graphemes.pyx>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/iterate.pyx>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/offsets.pyx>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/latin1.pxd>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/uprop.pxd>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme/__init__.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/tests/test_uax29.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/tests/test_props.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/tests/test_grapheme_fns.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/tests/test_graphemes.py>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/ugrapheme_ucd/data/GraphemeBreakTest.txt>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/.github/workflows/build_deploy.yml>
  - <https://raw.githubusercontent.com/Z4JC/ugrapheme/HEAD/.github/workflows/test.yml>
  - <https://pypi.org/pypi/ugrapheme/json>
  - https://pypi.org/project/ugrapheme/ (0.8 wheel installed into the scratch directory and run in this session)
  - https://pypi.org/project/wcwidth/ (0.9.1 wheel installed into the scratch directory for the iter_graphemes comparison)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/z4jc/ugrapheme`) · [data/wave10/enrich/raw/github_com_z4jc_ugrapheme.json](../../../data/wave10/enrich/raw/github_com_z4jc_ugrapheme.json) (enrichment confidence 0.8)

</details>
