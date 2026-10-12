# xcdat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 compressed double-array trie dictionary; about 2x faster key-to-ID lookup than marisa-trie, at about 1.1-2x its size.

| | |
|---|---|
| **Beats** | marisa-trie (LOUDS nested patricia trie, s-yata/marisa-trie); also compared against tx LOUDS trie, fst, pdt |
| **Claimed result** | Wiki dataset lookup: xcdat&lt;8&gt; 826 ns/key vs marisa 1818 ns/key (about 2.2x faster, derived from page data); xcdat&lt;15&gt; 619 ns/key vs 1818 (about 2.9x, derived). Decode: xcdat&lt;8&gt; 1173 ns/id vs marisa 1515 ns/id. Url dataset lookup: xcdat&lt;8&gt; 469 vs marisa 1789 ns/key. Memory cost: xcdat&lt;8&gt; 139 MiB vs marisa 69 MiB on Wiki. |
| **Workload** | Static string dictionary lookup (key to ID) and decode (ID to key) on English Wikipedia titles (14,130,439 keys, 285 MiB), IPAdic, Askitis Distinct and Url datasets; 1,000 random query keys, best of 10 runs. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 13-inch 2019, 2.4 GHz Quad-Core Intel Core i5, 16 GB 2133 MHz LPDDR3, macOS Catalina 10.15 |
| **Compiler and flags** | AppleClang 12.0.0, -O3 -march=native |
| **Adoption** | 73 stars, 17 forks |
| **Last commit** | 2024-09-10 |
| **Links** | [repository](https://github.com/kampersanda/xcdat) · [benchmark](https://github.com/kampersanda/xcdat#performance) |

## Verdict

The author's tables (fast_succinct_trie/bench, AppleClang 12 -O3 -march=native, MacBook Pro 13-inch 2019 2.4 GHz quad-core Core i5, 1,000 random queries, best of 10) show xcdat&lt;8&gt; lookups of 826 vs marisa's 1818 ns/key on 14.1M Wikipedia titles and 469 vs 1789 on URLs, at 139 vs 69 MiB on Wiki. An independent run in ilgrad/string-index-benchmarks (AMD Ryzen 7 5800HS, GCC 16.2.1, 2026-09-26, C2-style single shuffled pass) agrees on direction: XCDAT 8 259 vs MARISA 505 ns on 1M English titles (about 1.95x, derived from page data), 377 vs 581 ns on 1M URLs, at 15.0 vs 13.2 B/key.

## Use it when

- You use marisa-trie (or another LOUDS/succinct trie such as tx, fst or pdt) for a static key-to-ID map and lookups are the bottleneck: about 2x faster lookup on Wikipedia titles and up to 3.8x on URLs in the author's tables.
- Read-mostly dictionaries of millions of strings (titles, words, URLs, column-store domain encoding) where you also need ID-to-string decode, which darts-clone and hat-trie do not offer.
- Autocomplete, tokenizers or IME dictionaries that need common-prefix and predictive search over a compact, mmap-able file.
- When a double-array trie such as darts-clone is too big: xcdat&lt;8&gt; is 139 MiB vs darts-clone's 525 MiB on 14.1M Wikipedia titles.
- Pick trie_15_type for speed (619 ns/key on Wiki) and trie_8_type for size (139 MiB on Wiki).

## Skip it when

- Memory is the hard constraint: marisa is smaller on every published dataset (Wiki 69 vs 139 MiB; independent 1M-key runs 13.15 vs 15.03 B/key on English titles), and FM-index or front-coding dictionaries such as lexindex are smaller still.
- Raw lookup speed matters more than space: darts-clone (450 ns/key), cedar and hat-trie (368 ns/key) beat xcdat on Wiki at 2.5-8x the memory.
- The set changes: it is static, so any insert or delete means a full rebuild from sorted input.
- You need IDs in lexicographic order or chosen by you: IDs follow the trie layout (issue #3 is open and unanswered).
- Windows or exotic targets: tested only on macOS and Linux; 32-bit ARM support was asked about in issue #4 with no maintainer answer.

## How it is fast

It keeps the double-array trie's O(1) child transition (base XOR char-code, then a check comparison) and compresses the BASE/CHECK arrays with XCDA (Kanda, Morita, Fuketa, KAIS 2017): directly addressable codes (DACs, Brisaboa et al.) for the 8/16-bit types, or pointer-based DACs for the 7/15-bit types. A minimal-prefix trie moves single-path suffixes into a TAIL vector, cutting node hops and random accesses. IDs come from rank/select over a terminal-flag bitvector, using POPCNT and BMI2 PDEP/TZCNT when compiled with -msse4.2/-mbmi2 (portable fallbacks otherwise).

## Compared with alternatives

Pick xcdat over lexindex when exact-match lookup latency matters more than size and you can spend about 2-2.4x lexindex's bytes (independent 1M English titles: XCDAT 15 243 ns at 17.13 B/key vs lexindex's fastest exact search 324 ns and its smallest 7.21 B/key); pick it over darts-clone when you also need ID-to-key decode in a far smaller file. Pick lexindex or C2-MARISA when bytes per key dominate.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library; the CLI tools vendor cmd_line_parser, mm_file and tinyformat; optional pybind11 for Python |
| **Minimum toolchain** | C++17 (README: g++ &gt;= 7.0 or clang &gt;= 4.0); CMake &gt;= 3.0 only for the tools and tests |
| **Platforms** | UNIX-like (tested on macOS and Linux); needs std::uint64_t; x86-64 SSE4.2/BMI2 intrinsics used when enabled, portable fallbacks otherwise |
| **Thread safety** | not documented; lookup and decode are const and use no mutable members in trie.hpp, so concurrent read-only queries on a built trie look safe, but the README does not promise it |
| **Drop-in for the baseline** | partial — same operations as marisa (lookup, reverse lookup, prefix and predictive search) and similar CLI tools, but a different C++ API and file format, and input must be pre-sorted and deduplicated |

## Gotchas

- The constructor requires lexicographically sorted, unique keys; sort and deduplicate first.
- lookup returns std::optional&lt;uint64_t&gt;; IDs are not in lexicographic order.
- Copy is deleted (move-only), and errors in build or I/O throw xcdat::exception.
- Iterator decoded_view() points to storage that changes on the next next() call; copy it if you keep it.

## Known shortcomings

- Tier A (bench in fast_succinct_trie/bench, AppleClang 12 -O3 -march=native, 2019 MacBook Pro i5 2.4 GHz): Wiki lookup 826 vs marisa-trie 1818 ns/key, but darts-clone and hat-trie look up faster than xcdat; the win is against marisa at about 2x memory of marisa.
- About 2x marisa's memory on Wiki (139 vs 69 MiB); slower than darts-clone and hat-trie; static only; IDs are not in lexicographic order (issue #3, open, unanswered) and the 32-bit question (issue #4) was never answered.

## Caveats and trade-offs

The baseline is marisa-trie, not SDSL or sux, so this is a trie-dictionary win rather than a bitvector or wavelet-tree win. xcdat is faster than the succinct tries (marisa, tx, fst, pdt) but slower than the plain double-array tries (darts-clone 450 ns/key on Wiki) and hat-trie (368 ns/key), and it uses about twice marisa's memory (139 vs 69 MiB on Wiki). It ran on a laptop Core i5 with only the AppleClang toolchain; the SKU number is not printed, only 'MacBook Pro (13-inch, 2019), 2.4 GHz Quad-Core Intel Core i5'. The benchmark code is in the sibling repo kampersanda/fast_succinct_trie/bench, not in xcdat. dastrie did not complete its build on the Distinct dataset. xcdat was compared directly with a succinct-trie incumbent, not with std containers.

Faster than marisa but uses about 2x the memory on Wiki (139 vs 69 MiB) and up to 2x on other sets. Slower than darts-clone on lookup (450 ns/key on Wiki) but about 3.8x smaller (139 vs 525 MiB). Static dictionary only; header-only C++17; supports prefix and predictive search, 64-bit pointers and binary keys.

## Maintenance

Stale since September 2024 (last commit 2024-09-10) but MIT-licensed, header-only and small enough to vendor; open issues are questions and a vcpkg-port request, not bug reports against xcdat itself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance section has IPA/Wiki/Distinct/Url tables with xcdat&lt;8&gt; 826 vs marisa 1818 ns/key lookup and 1173 vs 1515 ns/id decode on Wiki, xcdat&lt;15&gt; 619 ns/key, and Url 469 vs 1789 ns/key, all matching the record. The benchmark code is public at kampersanda/fast_succinct_trie/bench (bench.cpp, CMakeLists.txt, marisa-trie and xcdat submodules), and the README states AppleClang 12.0.0, -O3 -march=native and a MacBook Pro 13-inch 2019 with a 2.4 GHz quad-core Core i5. That machine identifies the CPU closely enough, as with earlier 'MacBook Pro 16-inch 2019, 2.4 GHz Core i9' A precedents.
- **Verifier notes:** All numbers check out. The comparison table also shows that the double-array competitors look up faster but use 3-8x the memory, so the claim holds only within the compact-trie class; the caveats now say so. Last commit is 2024-09-10 (stale), MIT, and the repo is neither archived nor a fork.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; independent: ilgrad/string-index-benchmarks (Ryzen 7 5800HS, GCC 16.2.1, 1M English titles): XCDAT 8 259 ns vs MARISA 505 ns, about 1.95x (derived from page data), at 15.03 vs 13.15 bytes per key
- **Pages the verifier opened:**
  - <https://github.com/kampersanda/xcdat>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/README.md>
  - <https://github.com/kampersanda/xcdat/commits/master>
  - <https://github.com/kampersanda/fast_succinct_trie/tree/master/bench>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/README.md>
  - <https://github.com/kampersanda/xcdat/issues?q=is%3Aissue>
  - <https://github.com/kampersanda/xcdat/issues/3>
  - <https://github.com/kampersanda/xcdat/issues/4>
  - <https://github.com/kampersanda/xcdat/tree/master/include/xcdat>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/trie.hpp>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/bc_vector_8.hpp>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/bc_vector_15.hpp>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/tail_vector.hpp>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/bit_vector.hpp>
  - <https://raw.githubusercontent.com/kampersanda/xcdat/HEAD/include/xcdat/bit_tools.hpp>
  - <https://github.com/ilgrad/string-index-benchmarks>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/results/frontier-1m-2026-09-26-arz-be75a38.json>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/harness/xcdat_frontier.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kampersanda/xcdat`) · [data/wave9/enrich/raw/github_com_kampersanda_xcdat.json](../../../data/wave9/enrich/raw/github_com_kampersanda_xcdat.json) (enrichment confidence 0.85)

</details>
