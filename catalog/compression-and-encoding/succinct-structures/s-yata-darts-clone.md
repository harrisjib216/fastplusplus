# Darts-clone

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Single-header static double-array trie with 32-bit units; half the size of Darts and faster on cache-bound lookups.

| | |
|---|---|
| **Beats** | Darts (Double-ARray Trie System, original header library by Taku Kudo) |
| **Claimed result** | Random-order exactMatchSearch: JA1 170.4 vs 76.2 ns/key (about 2.2x faster, derived from page data), EN1 228.5 vs 111.3 ns/key (about 2.1x, derived from page data), EN3 545.3 vs 453.3 ns/key. Lexicographic exactMatchSearch: JA1 48.9 vs 33.1 ns/key. Dictionary size about halved (JA1 7,023 KB vs 3,336 KB; EN2 513,873 KB vs 240,634 KB). Build time lower when no values are given (JA1 828 vs 368 ns/key), but higher when every key has a unique value (JA1 1,196 ns/key, EN2 6,666 vs 2,518 ns/key). |
| **Workload** | Static double-array trie dictionaries built from 7 key sets (Japanese and English word lists, Wikipedia titles, Google unigram lists, 7-digit postal codes; 118k to 13.6M keys); average ns per key for exactMatchSearch(), commonPrefixSearch() and traverse(), keys queried in lexicographic and in random order, plus dictionary size and build time. |
| **Metric** | latency |
| **Hardware** | Dell Precision T3400, Core 2 Quad Q9550 2.83GHz, 64-bit Ubuntu 9.04 |
| **Compiler and flags** | gcc 4.3.3 (optimization flags not stated on the page); benchmark tool darts-benchmark ships with the repo |
| **Adoption** | 161 stars; packaged as a vcpkg port (darts-clone) |
| **Last commit** | 2025-05-11 |
| **Links** | [repository](https://github.com/s-yata/darts-clone) · [benchmark](https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/ja/Evaluation.md) |

## Verdict

The author's own darts-benchmark (Darts-clone 0.32g vs original Darts, gcc 4.3.3 with unstated optimisation flags, Core 2 Quad Q9550, Ubuntu 9.04) on seven key sets shows dictionaries about half the size and random-order exactMatchSearch about 2.2x faster on the small sets (JA1 76.2 vs 170.4 ns/key, EN1 111.3 vs 228.5), shrinking to about 1.2x on the large Wikipedia and n-gram sets (JA2 516.4 vs 620.8). Sorted-order lookups are close to parity and slower on the postal-code set; the results are about fifteen years old.

## Use it when

- Read-only dictionaries of 100k to tens of millions of byte-string keys (word lists, titles, n-grams) needing exact and longest/common-prefix lookups
- Tokenisers and morphological analysers that walk text byte by byte with commonPrefixSearch() or traverse()
- Dictionaries built once offline and memory-mapped at startup via set_array() to avoid load time
- Key sets with few distinct values (or no values), where the DAWG build merges subtrees and the file shrinks further (JA1: 1,272 KB with all-zero values vs 3,336 KB)
- Projects that want a dependency-free, BSD-2-Clause single header (also a vcpkg port)

## Skip it when

- Data that changes: there is no insert or delete; any update means a full rebuild
- Memory-critical dictionaries: LOUDS-based tries such as marisa-trie or xcdat are several times smaller (the verified record cites the marisa-trie README: about 377 MB for darts-clone vs 51 MB for marisa-trie on 9.8M Wikipedia titles)
- Untrusted dictionary files: open() validates only the first 256 units and set_array() validates nothing, so a corrupt or hostile file can drive searches out of bounds
- Unique value per key with tight build-time budgets: build is 2-3x slower than Darts on large sets (EN2 6,666 vs 2,518 ns/key)
- Very large key sets: offsets of 2^29 or more throw 'too large offset' (issue 1, closed wontfix); values are limited to non-negative 31-bit ints

## How it is fast

It is a double-array trie (Aoe 1989): each node is one 32-bit unit packing label, leaf flag and an offset, and the child for byte c is found at node_pos XOR offset XOR c, so a lookup is one dependent array load per key byte. Halving the unit from 8 to 4 bytes, and merging identical subtrees into a DAWG when values repeat, shrinks the array so more of it stays in cache; a has-leaf flag per node skips the explicit terminator transition, which mainly helps commonPrefixSearch(). The author attributes the gains to cache efficiency, which is why random-order lookups gain about 2x while in-cache, sorted-order lookups gain little.

## Compared with alternatives

Pick it over xcdat or lexindex when lookup latency and a tiny, dependency-free header matter more than dictionary size, since those compressed tries trade lookup speed for much smaller structures; pick xcdat, lexindex or C2 when the dictionary must fit in limited memory.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++98-era header (uses throw() specifications and NULL); vcpkg port builds it with current compilers |
| **Platforms** | any (portable C++, no intrinsics) |
| **Thread safety** | not documented; search methods are const and keep no mutable state, so concurrent reads look safe (per code reading); build() is not |
| **Drop-in for the baseline** | partial — same class name and method signatures as Darts, but dictionary files are incompatible and early versions before 0.32e had a different interface |

## Gotchas

- Keys must be sorted in unsigned byte order, non-empty and NUL-free, and values non-negative; violations throw Darts::Details::Exception (exceptions are used for bad input and bad_alloc, while open()/save() return non-zero on I/O errors).
- No bounds checks on lookup: exactMatchSearch()/traverse() index array_ directly, which is only safe for dictionaries you built; open PR 6 proposes a validate() helper taken from sentencepiece and OpenCC for exactly this reason.
- The template parameter T only casts at the API boundary; internal values are always int, so 64-bit values do not fit.
- Sorted-order traverse() is slower than Darts on every word list (JA2 144.6 vs 119.1 ns/key) because it is not inlined; small in-cache sets like 7-digit postal codes are also slower (24.2 vs 18.8 ns/key).

## Known shortcomings

- Tier C: Evaluation.md (Darts vs Darts-clone 0.32g, src/darts-benchmark.cc, gcc 4.3.3, Core 2 Q9550) states no -O flags; build is slower with unique values per key (EN2 6,666 vs 2,518 ns/key) and lexicographic traverse() is slower on all word lists. Loose category fit (compact trie, not rank/select). Last commit 2025-05-11 (doc edits), stale.
- No bounds checks: open() validates only the first 256 units and set_array() validates nothing, so a hostile dictionary reads out of bounds (open PR 6 adds validate() taken from sentencepiece/OpenCC). Offsets of 2^29 or more throw 'too large offset' (issue 1, wontfix). Values are int only, at most 31 bits. Sorted traverse() and the DIG set are slower than Darts. C++98-era header; benchmarks about 15 years old. Used inside sentencepiece and OpenCC.

## Caveats and trade-offs

Baseline is the original Darts, not SDSL or sux. Numbers are from a 2009-2011 era machine and compiler (gcc 4.3.3, Darts-clone 0.32g), on a Japanese-language page; optimization flags are not stated. Results are mixed: on the postal-code set (DIG) Darts-clone is slower for exactMatchSearch (24.2 vs 18.8 ns/key lexicographic, 43.9 vs 40.2 random), and lexicographic traverse() is slower on every word list (for example JA2 144.6 vs 119.1 ns/key); the page attributes this to traverse() not being inlined. Build time is lower only when no values are associated; with unique values per key, build is slower than Darts on every corpus (for example EN2 6,666 vs 2,518 ns/key). The page itself warns that search time depends heavily on cache sizes, inlining and key distribution. On the large Wikipedia and n-gram sets the random-order gain is smaller (JA2 516.4 vs 620.8 ns/key). Found as a registry hit, but it is a compact trie rather than a rank/select structure, so category fit is loose. Recent commits (May 2025) are documentation edits; the author does not state the project is finished.

Static dictionary (no updates). Not a true succinct structure: it is a compact double-array trie (32-bit units, DAWG-merged), so it is far larger than LOUDS or MARISA tries (marisa-trie README lists 376,613,888 bytes for darts-clone against 50,753,560 for marisa-trie on 9.8M Wikipedia titles). Build time grows when every key has a unique value (JA2 5,942 ns/key). Dictionary files are not compatible with Darts.

## Maintenance

Stale (last commit May 2025, mostly documentation; PR 6 with validation and warning fixes open since July 2026) but BSD-2-Clause, a single header, and embedded in sentencepiece and OpenCC, so it is easy and low-risk to vendor for trusted dictionaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Evaluation.md compares Darts-clone 0.32g with the original Darts using the repo's own src/darts-benchmark.cc, and names gcc 4.3.3 and a Core 2 Quad Q9550, but optimization flags are not stated (configure.ac sets only -Wall -Weffc++), so it falls short of A; no independent measurement found.
- **Verifier notes:** Every number in claimed_speedup checked against the page tables; all correct. maintenance_status changed from finished to stale: last commit 2025-05-11 is about 17 months before today and no completion statement was found. 161 stars and the vcpkg port (ports/darts-clone, BSD-2-Clause) confirmed.
- **Fields the verifier corrected:** `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/ja/Evaluation.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/README.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/COPYING.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/src/darts-benchmark.cc>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/ja/ChangeLog.md>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/HEAD/ports/darts-clone/vcpkg.json>
  - <https://github.com/s-yata/darts-clone>
  - <https://github.com/s-yata/darts-clone/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/README.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/include/darts.h>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/ja/Evaluation.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/en/Introduction.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/doc/ja/Introduction.md>
  - <https://raw.githubusercontent.com/s-yata/darts-clone/HEAD/src/darts.cc>
  - <https://github.com/s-yata/darts-clone/issues?q=is%3Aissue>
  - <https://github.com/s-yata/darts-clone/issues/1>
  - <https://github.com/s-yata/darts-clone/pulls?q=is%3Apr>
  - <https://github.com/s-yata/darts-clone/pull/6>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/s-yata/darts-clone`) · [data/wave9/enrich/raw/github_com_s_yata_darts_clone.json](../../../data/wave9/enrich/raw/github_com_s_yata_darts_clone.json) (enrichment confidence 0.8)

</details>
