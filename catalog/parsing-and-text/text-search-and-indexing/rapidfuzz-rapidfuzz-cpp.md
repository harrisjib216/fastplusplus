# RapidFuzz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ FuzzyWuzzy-style string similarity scorers on bit-parallel LCS/Levenshtein; its Python package runs 13-28x more pairs/s than FuzzyWuzzy.

| | |
|---|---|
| **Beats** | FuzzyWuzzy (Python fuzzywuzzy package) |
| **Claimed result** | Scorer called directly from Python, pairs per second RapidFuzz vs FuzzyWuzzy: ratio 6,206,379 vs 480,115 (12.9x), partial_ratio 3,091,339 vs 212,794 (14.5x), token_sort_ratio 3,155,091 vs 151,101 (20.9x), token_set_ratio 1,590,972 vs 108,940 (14.6x), partial_token_sort_ratio 1,767,978 vs 105,151 (16.8x), partial_token_set_ratio 1,213,823 vs 81,875 (14.8x), QRatio 5,231,998 vs 184,591 (28.3x), WRatio 1,264,866 vs 59,436 (21.3x). RapidFuzz through cdist vs FuzzyWuzzy in a Python double loop: ratio 135,463,598 vs 525,021 (258x), partial_ratio 12,936,872 vs 183,338 (71x), token_sort_ratio 120,274,547 vs 167,720 (717x), token_set_ratio 3,253,260 vs 117,282 (27.7x), partial_token_sort_ratio 4,610,742 vs 96,626 (47.7x), partial_token_set_ratio 2,090,213 vs 76,227 (27.4x), QRatio 126,989,691 vs 204,064 (622x), WRatio 2,516,289 vs 63,982 (39x). Ratios derived from page data (chart labels). |
| **Workload** | Fuzzy string scorers (ratio, partial_ratio, token_sort_ratio, token_set_ratio, partial_token_sort_ratio, partial_token_set_ratio, QRatio, WRatio) over 10,000 random ASCII-letter-and-digit strings against 100 samples drawn from that list, reported as word pairs evaluated per second. Scorer chart (bench/benchmark_scorer.py): strings of length 10, both libraries called per pair from a Python list comprehension. cdist chart (bench/benchmark_cdist.py): strings of length 8, RapidFuzz timed as one process.cdist call (default workers=1, single-threaded) and FuzzyWuzzy timed as a Python double loop over inputs with the default processor applied before timing. Each measurement is a single timeit run (number=1). |
| **Metric** | throughput |
| **Adoption** | 377 stars (rapidfuzz-cpp); the Python package rapidfuzz/RapidFuzz that vendors it has 4.2k+ stars |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/rapidfuzz/rapidfuzz-cpp) · [benchmark](https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/docs/img/scorer.svg) |

## Verdict

First-party charts from the Python package that compiles this library: per-pair calls from a Python list comprehension over 100 x 10,000 random 10-character alphanumeric strings ran 12.9x (ratio) to 28.3x (QRatio) more pairs per second than FuzzyWuzzy, and one single-threaded cdist call on 8-character strings ran 27x to 717x more than a Python double loop over FuzzyWuzzy; each is a single timeit run with no CPU, compiler, flags, Python or FuzzyWuzzy version stated and no word on whether python-Levenshtein was installed, and the space-free strings make every token scorer a single-token case. No C++-to-C++ comparison exists; the C++ repo's Google Benchmark files (built with -march=native) time only RapidFuzz itself.

## Use it when

- Scoring short strings (names, product titles, addresses, OCR tokens up to about 64 characters) against thousands to millions of candidates in C++, with one Cached\* scorer per query and a score_cutoff to prune.
- Porting Python code that used FuzzyWuzzy, thefuzz or the RapidFuzz package to C++: the Python package compiles this exact library from its extern/rapidfuzz-cpp submodule, so scores match the Python package.
- You need FuzzyWuzzy-style scoring under MIT instead of FuzzyWuzzy's GPL.
- Batch scoring on x86-64 where queries are at most 64 characters and you can compile with -mavx2 (or at least SSE2): the experimental Multi\* classes give the cdist-style batched speedup.
- Edit-distance building blocks for generic sequences (wide strings, code points, integer token ids) that also need editops/opcodes alignments.

## Skip it when

- Searching a large corpus: there is no index, so every query is a linear scan over all candidates; put an inverted index, n-gram or BK-tree prefilter in front for large collections.
- Long strings: the SIMD multi-string path only covers queries up to 64 characters (longer ones fall back to one scorer per query), and partial_ratio cost grows with needle length times haystack windows. For batched plain Levenshtein on \~100-byte strings, StringZilla's README (competitor-run, one core) shows 15,680 MCUPS for its C kernel vs 4,970 for rapidfuzz.process.cdist on a Sapphire Rapids Xeon (3.2x, derived from page data) and 22,844 vs 18,370 on an Apple M5 Pro.
- Unicode-aware matching out of the box: the C++ library has no case folding or normalization and compares the elements it is given, so a UTF-8 std::string is compared byte by byte; decode to char32_t and preprocess yourself.
- Non-x86 SIMD: the SIMD layer is selected at compile time from __AVX2__ or __SSE2__ only, so aarch64 and other targets get the scalar bit-parallel code and no Multi\* classes.
- You need bit-identical FuzzyWuzzy output: partial_ratio searches for the optimal alignment where FuzzyWuzzy used a SequenceMatcher matching-block heuristic, and FuzzyWuzzy's ratio without python-Levenshtein is difflib's Ratcliff-Obershelp score, not Indel.

## How it is fast

ratio is an Indel (LCS-based) similarity computed with Hyyro's bit-parallel LCS, and Levenshtein uses the Hyyro 2003 bit-vector recurrence (Myers-style), 64 characters per machine word, blocked for longer strings and limited to an Ukkonen band when a score_cutoff is given; when only a few edits are allowed it switches to the mbleven model enumeration, and common prefixes and suffixes are stripped first. Cached\* scorers build the per-character bitmask table once per query (a 256-entry array for 8-bit characters, a 128-slot open-addressing hashmap otherwise). The experimental Multi\* scorers (MultiRatio, MultiTokenSortRatio, MultiQRatio, MultiIndel, MultiLCSseq, MultiLevenshtein, MultiJaro) pack many queries into one SSE2/AVX2 register (8-bit lanes for queries up to 8 characters, i.e. 32 per 256-bit vector; 16, 32 and 64-bit lanes up to 64 characters) and advance the bit-parallel recurrence for all of them per choice. score_cutoff lets scorers exit early, and partial_ratio skips alignment windows whose best possible score is below the current best.

## Compared with alternatives

None of the catalogued siblings scores string similarity: Tantivy, SeekStorm, PISA, IResearch, Manticore and Infinity rank documents from an inverted index, and ugrep, ngi, trigrep and frg find literal or regex matches in files. Pick RapidFuzz when you already have a candidate list and need an edit-distance score per pair, or to rerank the top hits such an engine returns.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target rapidfuzz::rapidfuzz; a single-file extras/rapidfuzz_amalgamated.hpp also exists but is stale) |
| **Dependencies** | none (Catch2 only for RAPIDFUZZ_BUILD_TESTING, Google Benchmark only for RAPIDFUZZ_BUILD_BENCHMARKS, both off by default) |
| **Minimum toolchain** | C++11 since 3.3.0 (2025-01-18; earlier releases needed C++17); CMake 3.5+; 3.3.2 fixed builds on old MSVC versions without proper if constexpr |
| **Platforms** | any C++11 target for the scalar bit-parallel code; SIMD Multi\* scorers only on x86/x86-64 with SSE2, or AVX2 when the translation unit is compiled with AVX2 enabled (compile-time choice, no runtime dispatch in the C++ library); a 32-bit SIMD scoring bug was fixed in 3.1.1 |
| **Thread safety** | not documented; scorer similarity() methods are const and the README's OpenMP example shares one CachedRatio across threads |
| **Drop-in for the baseline** | partial — same scorer names and FuzzyWuzzy-compatible scores, but it replaces a Python library with a C++ one; no extract/extractOne/cdist and no full_process/default_process cleaning in C++, and partial_ratio (optimal alignment) and ratio (Indel, not difflib) can differ from FuzzyWuzzy |

## Gotchas

- Harness flaw behind the 258x-717x cdist figures: the chart's strings are 8 characters, exactly the narrowest SIMD lane width, so RapidFuzz's cdist packs 32 queries (256/8) per AVX2 batch, and the batched Multi\* path exists only for ratio, token_sort_ratio and QRatio, the three biggest bars (258x, 717x, 622x); the README text says length 10, which would give 16 per batch. In the script as it ran for the chart (commit 69fc902, 2022-10-02) RapidFuzz's cdist applied default_process once per string while FuzzyWuzzy's token_\*, QRatio and WRatio scorers ran their own full_process inside each of the 1,000,000 timed calls, so preprocessing was hoisted only on the RapidFuzz side.
- Neither chart can be reproduced as published: commit 6925381 (2023-04-12, 'fix some linter warnings') made benchmark_cdist.py call processor(x) where processor is the bool True, which raises TypeError for 6 of the 8 scorers; RapidFuzz 3.0.0 (2023-04-16) removed boolean processors and made processor=None the default, so benchmark_scorer.py rerun today compares unpreprocessed RapidFuzz scorers with FuzzyWuzzy's per-call full_process; bench/requirements.txt lists thefuzz (built on rapidfuzz itself since 0.20.0) rather than fuzzywuzzy, whose last release is 0.18.0 from 2020.
- Both charts use only equal-length strings and predate the 1.10.2 fix (2022-12-01) that made partial_ratio symmetric when len(s1) == len(s2): current code runs a second, reversed pass in that case unless the first score is 100, so today's partial_ratio and partial_token_\* do up to twice the work that was measured. The cdist chart also ran SIMD code added the same day (rapidfuzz-cpp 1.8.0) before fixes for undefined behavior (1.10.2) and broken SSE2 support (1.10.1).
- Pin a recent release and use the rapidfuzz/ headers, not extras/rapidfuzz_amalgamated.hpp: the amalgamated file's banner still says 'RapidFuzz v1.0.2, Generated 2025-02-11' and it keeps the WRatio 'len_ratio &lt; 8.0' branch that 3.3.3 fixed to '&lt;= 8.0'; 3.0.5 fixed editops miscounts and crashes and 3.3.4 (2026-08-29) an out-of-bounds access in Editops::remove_subsequence. API reference docs are effectively absent (issue #130: the Doxygen output is empty).

## Known shortcomings

- The benchmark (RapidFuzz bench/benchmark_scorer.py and benchmark_cdist.py, single runs, no compiler, flags or CPU) tests the Python wrapper against FuzzyWuzzy called from Python, not C++ against C++; the cdist chart pits one batched single-threaded cdist call against a Python double loop on length-8 strings, so the 258x-717x is mostly removed interpreter overhead; whether FuzzyWuzzy had the python-Levenshtein speedup is unstated; charts from 2021-2022. Filed under parsing-and-text/text-search-and-indexing.
- Enricher: the cdist chart uses length-8 strings (the narrowest SIMD lane width) and only ratio, token_sort_ratio and QRatio have the batched Multi\* path, which are the biggest bars (258x, 717x, 622x); the chart-era script ran default_process once per string for RapidFuzz but FuzzyWuzzy's full_process inside all 1,000,000 timed calls; neither chart reproduces now (commit 6925381 passes processor=True, a TypeError on 6 of 8 scorers since RapidFuzz 3.0; requirements.txt lists thefuzz, built on rapidfuzz itself). Both charts predate the 1.10.2 partial_ratio equal-length symmetry fix (current code does up to 2x the measured work) and the cdist chart ran SIMD code before its UB and SSE2 fixes. The C++ library has no extract/cdist/default_process and no NEON; extras/rapidfuzz_amalgamated.hpp is stale (v1.0.2 banner, WRatio bug fixed in 3.3.3). StringZilla reports 15,680 vs 4,970 MCUPS over rapidfuzz cdist on DNA Levenshtein.

## Caveats and trade-offs

The numbers measure the Python package rapidfuzz/RapidFuzz (which builds rapidfuzz-cpp from its extern/rapidfuzz-cpp submodule) against pure-Python-called FuzzyWuzzy, not C++ against a C++ baseline; nothing compares rapidfuzz-cpp itself with hand-written std::string code, and the seed's guessed std::string baseline does not apply. Harness: bench/benchmark_scorer.py and bench/benchmark_cdist.py in rapidfuzz/RapidFuzz (public), single timeit run per scorer, no compiler, flags, CPU, Python version or FuzzyWuzzy version stated, and it is not stated whether FuzzyWuzzy had the python-Levenshtein C speedup installed (without it FuzzyWuzzy falls back to difflib, which inflates the ratio). The cdist chart (2022-10-02) uses length-8 strings while the README text says length 10, and it compares a single batched C++ call (cdist with workers=1, so no threading, but with SIMD multi-string scorers) against per-pair Python calls, so its 258x to 717x figures mostly measure removed interpreter overhead plus batching rather than per-pair algorithmic gain. The scorer chart dates from 2021-09-10 and the numbers are old. RapidFuzz also deliberately fixes partial_ratio bugs, so results are not bit-identical to FuzzyWuzzy for that scorer. rapidfuzz-cpp's own bench/ directory (bench-fuzz.cpp, bench-levenshtein.cpp, bench-lcs.cpp, bench-jarowinkler.cpp, Google Benchmark) times RapidFuzz only against itself; the README's Benchmarks.md link returns 404 and the detailed comparison pages on rapidfuzz.github.io (Levenshtein vs editdistance, edlib, polyleven and others via bench/benchmark.py) are blocked here. [retier] First-party charts (scorer.svg 2021-09-10, cdist.svg 2022-10-02) from RapidFuzz's Python bench scripts, single runs, no compiler, flags or CPU: the Python wrapper is timed against FuzzyWuzzy called from Python, not C++ against C++. The chart-era script (69fc902) ran default_process once per string for RapidFuzz but FuzzyWuzzy's full_process inside all 1,000,000 timed calls; whether FuzzyWuzzy had the python-Levenshtein speedup is unstated. The cdist chart pits one batched single-threaded cdist call against a Python double loop on length-8 strings (the narrowest SIMD lane width; 32 queries per AVX2 batch), and only ratio, token_sort_ratio and QRatio have the batched Multi\* path, which are the biggest bars (258x, 717x, 622x), so the gap is mostly removed interpreter overhead plus batching. Neither chart reproduces now: commit 6925381 passes processor=True (TypeError on 6 of 8 scorers since RapidFuzz 3.0) and requirements.txt lists thefuzz, which is built on rapidfuzz. Both charts predate the 1.10.2 partial_ratio equal-length symmetry fix (current code runs a second reversed pass, up to 2x the measured work) and the cdist chart ran SIMD code added the same day, before its UB and SSE2 fixes. The C++ library has no extract/cdist/default_process and no NEON; extras/rapidfuzz_amalgamated.hpp is stale (v1.0.2 banner, WRatio len_ratio bug fixed in 3.3.3). StringZilla's README reports 15,680 vs 4,970 MCUPS over rapidfuzz cdist on about 100-byte DNA Levenshtein (one core, Xeon 4).

Header-only C++ library (CMake target rapidfuzz::rapidfuzz) with Levenshtein, Indel, LCSseq, Jaro-Winkler and FuzzyWuzzy-style fuzz scorers plus cached scorers for one-query-many-choices use. The extract/extractOne/cdist 'process' layer exists only in the Python package; the C++ README shows a few lines to write the equivalents (and an OpenMP loop for parallelism). Results are meant to match FuzzyWuzzy's.

## Maintenance

Actively maintained (rapidfuzz-cpp 3.3.4 on 2026-08-29, Python package 3.14.6 on 2026-08-30), MIT and header-only so easy to vendor, but the headline numbers are Python-level, their scripts no longer run, and the cdist ratios hinge on 8-character strings hitting the 32-lane AVX2 path, so measure C++ speed with your own harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party charts (docs/img/scorer.svg dated 2021-09-10, docs/img/cdist.svg dated 2022-10-02) generated by the public scripts bench/benchmark_scorer.py and bench/benchmark_cdist.py in rapidfuzz/RapidFuzz; every label in claimed_speedup matches the SVG text, but compiler, flags, CPU model, Python version and FuzzyWuzzy version are not stated, so the evidence falls short of A and stays C.
- **Verifier notes:** Numbers on scorer.svg and cdist.svg match the record exactly (read from SVG text labels); metadata confirmed: MIT, 377 stars, 59 forks, not archived or a fork, last commit 2026-08-30 ('update changelog'), Python package 4.2k stars. Shortcomings: Python-wrapper vs pure-Python-called FuzzyWuzzy baseline (not a C++ baseline), no hardware/compiler/flags, single-run timings, cdist chart compares batched C++ against a Python loop and uses length-8 strings, old charts (2021/2022). Enrichment lead: bench/benchmark.py in rapidfuzz/RapidFuzz compares Levenshtein, Indel, Jaro and DamerauLevenshtein against C/C++ libraries (editdistance, edlib, polyleven, jellyfish) whose plots live on the blocked docs site.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party Python charts (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/docs/img/scorer.svg>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/docs/img/cdist.svg>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/README.md>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/README.md>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/commits>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main/bench>
  - <https://github.com/rapidfuzz/RapidFuzz>
  - <https://github.com/rapidfuzz/RapidFuzz/tree/main/bench>
  - <https://github.com/rapidfuzz/RapidFuzz/tree/main/docs/img>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/bench/benchmark_scorer.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/bench/benchmark.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/bench/requirements.txt>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/src/rapidfuzz/process.pyi>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/main/.gitmodules>
  - <https://github.com/rapidfuzz/rapidfuzz/blob/master/Benchmarks.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/bench/bench-fuzz.cpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/bench/bench-levenshtein.cpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/fuzz.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/fuzz_impl.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/rapidfuzz_all.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/details/simd.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/details/PatternMatchVector.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/distance/Levenshtein_impl.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/distance/Indel_impl.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/distance/LCSseq_impl.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/rapidfuzz/distance/LCSseq.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/rapidfuzz-cpp/HEAD/extras/rapidfuzz_amalgamated.hpp>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main/rapidfuzz>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main/rapidfuzz/distance>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main/rapidfuzz/details>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main/extras>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/commits/main/extras/rapidfuzz_amalgamated.hpp>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/issues?q=is%3Aissue>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/issues/129>
  - <https://github.com/rapidfuzz/rapidfuzz-cpp/issues/130>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/CHANGELOG.rst>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/bench/benchmark_scorer.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/bench/benchmark.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/bench/requirements.txt>
  - <https://github.com/rapidfuzz/RapidFuzz/commits/main/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/69fc902/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/f8a0c70/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/6925381/bench/benchmark_cdist.py>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/ca0aa4d/bench/benchmark_cdist.py>
  - <https://github.com/rapidfuzz/RapidFuzz/tree/main/src/rapidfuzz>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/src/rapidfuzz/process_cpp.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/src/rapidfuzz/fuzz_cpp.hpp>
  - <https://raw.githubusercontent.com/rapidfuzz/RapidFuzz/HEAD/src/rapidfuzz/_feature_detector.py>
  - <https://raw.githubusercontent.com/seatgeek/fuzzywuzzy/master/fuzzywuzzy/fuzz.py>
  - <https://pypi.org/pypi/thefuzz/json>
  - <https://pypi.org/pypi/fuzzywuzzy/json>
  - <https://pypi.org/pypi/rapidfuzz/json>
  - <https://raw.githubusercontent.com/ashvardanian/StringZilla/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rapidfuzz/rapidfuzz-cpp`) · [data/wave1/enrich/raw/github_com_rapidfuzz_rapidfuzz_cpp.json](../../../data/wave1/enrich/raw/github_com_rapidfuzz_rapidfuzz_cpp.json) (enrichment confidence 0.8)

</details>
