# poplar-trie

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only dynamic path-decomposed trie string map; about 5.4x less memory than std::unordered_map, but 3-4x slower.

| | |
|---|---|
| **Beats** | std::unordered_map (also tsl::robin_map, tsl::htrie_map, google::dense_hash_map, cedar, libart, JudySL) |
| **Claimed result** | Memory only: compact_bonsai_map 0.24 GiB vs std::unordered_map 1.29 GiB on Wikipedia titles (about 5.4x smaller, derived from page data); 1.09 GiB vs 6.05 GiB on .uk URLs (about 5.5x smaller, derived from page data). It is slower: lookup 1.02 us/key vs 0.27 for std::unordered_map (titles), 1.44 vs 0.50 (URLs); insert 1.71 vs 0.50 us/key (titles). |
| **Workload** | Insert and lookup of string keys (14.1M English Wikipedia titles; 39.5M .uk URLs) into dynamic string-to-value maps; max resident set size, insert us/key, lookup us/key. |
| **Metric** | memory |
| **Hardware** | One core of quad-core Intel Xeon E5-2680 v2 2.80 GHz, 256 GB RAM, CentOS 6.10 |
| **Compiler and flags** | g++ 7.3.0 -O3 |
| **Adoption** | 58 stars |
| **Last commit** | 2021-09-07 |
| **Links** | [repository](https://github.com/kampersanda/poplar-trie) · [benchmark](https://github.com/kampersanda/poplar-trie) |

## Verdict

The README (via the public kampersanda/dictionary_bench driver) inserts 14.1M English Wikipedia titles and 39.5M .uk URLs in random order and looks up 1M random keys on one core of a Xeon E5-2680 v2, g++ 7.3.0: compact_bonsai_map max RSS 0.24 vs 1.29 GiB (titles) and 1.09 vs 6.05 GiB (URLs) for libstdc++ std::unordered_map (about 5.4-5.5x smaller, derived from page data) while being about 3-4x slower on lookup and insert. The README states only -O3, but dictionary_bench's Release flags are -O3 -DNDEBUG -march=native with -msse4.2 added when available.

## Use it when

- Very large dynamic string-key sets (tens of millions of titles, URLs, n-grams) built incrementally where RSS is the binding limit and about 1 us per lookup is acceptable.
- Keys with long shared prefixes (URLs, paths): the README shows compact_bonsai_map at 1.09 GiB vs 6.05 GiB for std::unordered_map on 39.5M .uk URLs.
- Small trivially copyable values (integers, IDs, counters) attached to each key.
- Insert-only or insert-mostly workloads with no need for ordered iteration or prefix queries.

## Skip it when

- Latency- or throughput-sensitive lookups: on the README's titles set, compact_bonsai_map lookup is 1.02 us/key vs 0.27 for std::unordered_map and 0.12 for tsl::robin_map; insert is 1.71 vs 0.50 us/key.
- You need deletion, iteration, prefix/predictive search, key-by-ID, or serialization: map.hpp offers only find, update and size (issues #3 iterate, #4 deletion, #6 key-by-index are unanswered); deletion can only be emulated by writing a sentinel value, and the memory is not reclaimed.
- Non-trivial value types such as std::string (issue #2, unanswered): values are written into raw byte buffers with reinterpret_cast and moved with byte copies, never constructed or destroyed.
- Binary keys containing NUL bytes (issue #1, open): keys are NUL-terminated, and an alphabet of 254 or more distinct byte values makes update throw.
- Projects that need maintenance: last commit 2021-09-07, and the README's Todo list still says code comments and an API document are missing.

## How it is fast

The gain is memory, not speed. Path decomposition stores each key's remaining suffix as one label in the node label map, so the trie holds only branching nodes; the trie itself is a compact hash-based trie (m-Bonsai with quotienting and displacement arrays, or Fischer-Koeppl HashTrie) where a child is found by hashing (parent, symbol) with a bijective hash and storing only the quotient. The compact NLMs pack the labels of ChunkSize (default 16) slots into one vbyte-length-prefixed byte buffer indexed by a popcount bitmap, removing per-node pointers and allocation overhead.

## Compared with alternatives

Pick poplar-trie when keys arrive incrementally and must stay queryable: marisa-trie and xcdat are static and must be rebuilt, though marisa is far smaller for a fixed set and xcdat faster. If you can afford about 1.8x more memory than compact_bonsai_map, tsl::htrie_map (0.43 GiB, 0.27 us/key on titles; not catalogued) is a maintained, faster dynamic alternative with iteration and prefix search.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++17 (g++ 7+ or clang 4+ per README); CMake 2.8 only for samples/tests/bench |
| **Platforms** | any 64-bit target in principle; uses SSE4.2 popcount when __SSE4_2__ is defined, table fallback otherwise; only Linux/macOS build logic in CMake, other OSes not documented |
| **Thread safety** | not documented; no internal synchronization in map.hpp, and find on a map being updated is unsafe because update can reallocate label buffers and rehash the whole trie |
| **Drop-in for the baseline** | no |

## Gotchas

- Pointers returned by update/find are invalidated by later inserts: each insert into a 16-slot chunk reallocates that chunk's byte buffer, and table growth (expand) rebuilds the trie and the whole NLM. Write the value immediately and do not keep the pointer.
- Values are stored unaligned right after the label bytes (reinterpret_cast&lt;value_type\*&gt;(ptr + length)) and initialised with static_cast&lt;value_type&gt;(0); this is undefined behavior for types with alignment above 1 and can fault on strict-alignment CPUs, and there is no static_assert restricting value_type.
- find("") and update("") throw poplar::exception (empty keys are rejected), so the map cannot hold an empty-string key.
- Growth doubles the hash table and rehashes every node at once (expand in compact_bonsai_trie.hpp), so individual inserts have large latency spikes; pre-size with map(capa_bits) when the key count is known. The bundled CMake and the dictionary_bench build also add -march=native, so binaries built that way are not portable.

## Known shortcomings

- Memory win only (0.24 vs 1.29 GiB against std::unordered_map); lookups are slower, with the slowdown ratios in the caveats. Driver code is public in kampersanda/dictionary_bench (g++ 7.3.0 -O3, Xeon E5-2680 v2).
- Values are stored unaligned via reinterpret_cast and never constructed (UB for alignment above 1; std::string values unusable, issue #2). Pointers from update/find are invalidated by later inserts. No delete, iteration, prefix search or serialisation (issues #3, #4, #6). NUL bytes in keys and empty keys unsupported; throws at 254+ distinct bytes. Thread safety undocumented. README says only -O3 but the dictionary_bench Release flags are -O3 -march=native (plus -msse4.2). Abandoned 2021.

## Caveats and trade-offs

Space win only, not a speed win: compact_bonsai_map lookup is about 2.9x-3.8x slower and insert about 3.4x-4.3x slower than std::unordered_map (derived from page data; .uk insert 2.87 vs 0.67 us/key). libstdc++ inferred from g++ on Linux (not stated). Benchmark driver is the separate repo kampersanda/dictionary_bench (README opened). Numbers are from 2018-2019 on an old Xeon. Method is peer-reviewed (Dynamic Path-decomposed Tries, ACM JEA 25(1), 2020). No deletion support.

Compact dynamic path-decomposed trie; no deletion; several-fold slower lookups and inserts than robin_map/unordered_map; C++17.

## Maintenance

Abandoned since September 2021, but MIT-licensed, header-only and small enough to vendor; treat it as research code and pin a commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README Benchmarks section compares poplar maps against std::unordered_map (and 10 other maps) with g++ 7.3.0 -O3 on an Intel Xeon E5-2680 v2; the driver code is public in kampersanda/dictionary_bench (bench executable, wrapper id 2 = std_unordered_map). Space numbers 0.24 vs 1.29 GiB and 1.09 vs 6.05 GiB, and the slower lookup/insert times, match the README tables.
- **Verifier notes:** All metadata checked on github.com: MIT, 58 stars, not archived, last commit 2021-09-07 (abandoned). Kept as a memory-only entry against std::unordered_map.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark with public harness, compiler, flags and CPU; first-party benchmark with public harness
- **Pages the verifier opened:**
  - <https://github.com/kampersanda/poplar-trie>
  - <https://github.com/kampersanda/poplar-trie/commits>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/kampersanda/dictionary_bench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/LICENSE>
  - <https://github.com/kampersanda/poplar-trie/tree/master/include/poplar>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/map.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/basics.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/poplar_config.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/bit_tools.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/compact_bonsai_trie.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/compact_bonsai_nlm.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/plain_bonsai_nlm.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/plain_bonsai_trie.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/exception.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/compact_vector.hpp>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/include/poplar/bijective_hash.hpp>
  - <https://raw.githubusercontent.com/kampersanda/dictionary_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/kampersanda/dictionary_bench/HEAD/CMakeLists.txt>
  - <https://github.com/kampersanda/poplar-trie/issues?q=is%3Aissue>
  - <https://github.com/kampersanda/poplar-trie/issues/2>
  - <https://github.com/kampersanda/poplar-trie/issues/3>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kampersanda/poplar-trie`) · [data/wave9/enrich/raw/github_com_kampersanda_poplar_trie.json](../../../data/wave9/enrich/raw/github_com_kampersanda_poplar_trie.json) (enrichment confidence 0.8)

</details>
