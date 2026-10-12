# cmph / cxxmph (mph_map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-only OR MPL-1.1` · 🔴 abandoned

> C minimal-perfect-hash library (BDZ/CHD/BRZ) plus cxxmph::mph_map, claimed 10-50% faster than std::unordered_map on &gt;100k URLs.

| | |
|---|---|
| **Beats** | std::unordered_map (cxxmph's dense_hash_map / sparse_hash_map are its own flavors named after the sparsehash classes; cxxmph/bm_map.cc benchmarks only against std::unordered_map) |
| **Claimed result** | "about 10%-50% faster than unordered_map" for large (&gt;100k) URL key sets with expensive comparisons (verbatim from the header comment) |
| **Workload** | Header claim: lookups over large (&gt;100k) URL key sets. The repo harness cxxmph/bm_map.cc builds and searches \~100k URL keys (URLS100k file, not shipped) with 10M searches at 0% and 90% miss ratio, plus 100k uint64 keys with 10M searches. It compares cxxmph::mph_map (BDZ minimal perfect hash behind an unordered_map-compatible interface) with std::unordered_map&lt;StringPiece, StringPiece, Murmur3StringPiece&gt;. |
| **Metric** | latency |
| **Adoption** | 91 stars |
| **Last commit** | 2017-03-02 |
| **Links** | [repository](https://github.com/zvelo/cmph) · [benchmark](https://github.com/zvelo/cmph/blob/master/cxxmph/mph_map.h) |

## Verdict

The only figure is the author's prose in mph_map.h: on large (&gt;100k) URL sets the cxxmph maps were 'about 10%-50% faster than unordered_map'. The repo harness (bm_map.cc) runs 10M lookups over a 100k-URL file with StringPiece keys at 0% and 90% miss rates, plus 100k uint64 keys, against std::unordered_map with a Murmur3 hasher. The URL file is not shipped, no results are published, and neither compiler nor hardware is given; the header only advises -O3 -DNDEBUG.

## Use it when

- Read-mostly string-keyed maps with 100k+ long keys (URLs, paths) that are expensive to compare, especially with many lookup misses: the header's only stated win case. Bulk-load, call rehash(), then serve lookups.
- Assigning dense ids to a fixed set of 10^6 to 10^9 keys (URLs, words, n-grams) through the C API, with values stored in your own array indexed by the id.
- Key sets that do not fit in RAM: the BRZ algorithm builds in external memory with a memory budget (-M) and temp dir, producing functions under 8 bits/key.
- You need a compact, serializable static index: CHD \~2.07 bits/key or BDZ \~2.6 bits/key, dumped to a file or packed with cmph_pack into a blob that can be mmapped and queried with cmph_search_packed.

## Skip it when

- Insert-heavy or interleaved insert/lookup workloads: new keys go to a side std::unordered_map that every lookup checks first, and when the value vector fills the whole BDZ index is rebuilt in O(n).
- Small maps, integer keys or cheap comparisons: the author warns the classes 'are not necessarily faster than their existing counterparts' and gives a figure only for &gt;100k URLs; no numbers exist for other shapes.
- Code that relies on std::unordered_map guarantees: any insert can relocate every element (invalidating all iterators and references), value_type is pair&lt;Key, Data&gt; so keys are mutable through iterators, the Alloc parameter is unused, and count/at/emplace/equal_range/reserve are missing.
- Looking up keys that were not in the build set through the C API: cmph_search returns an arbitrary id for them (zvelo issue #4), so you must store and compare the keys yourself.
- Projects that need a maintained or MSVC-ready codebase from this URL: the zvelo copy is frozen at 2012, cxxmph uses __builtin_expect and POSIX random(), and in this copy every mph_map unit test except erase_iterator is commented out.

## How it is fast

The core is BDZ (Botelho, Pagh, Ziviani): each key hashes to one edge of a random 3-partite 3-uniform hypergraph; construction peels degree-1 vertices to prove the graph acyclic, then assigns 2-bit g values so that (g[v0]+g[v1]+g[v2]) mod 3 selects a slot unique to that key. In cxxmph a lookup is one MurmurHash3 x64_128 call, three 2-bit reads from a table of about 2.93 bits per bucket, a presence bit and at most one key comparison, with no chain walk or probe sequence; that is why the header says gains grow with key size, set size and miss rate. mph_map uses the non-minimal PHF (\~81% slot occupancy, modulo), dense_hash_map rounds partitions to a power of two so a mask replaces the modulo (\~50% occupancy), and sparse_hash_map adds a rank table for a minimal, 100%-occupied layout at extra lookup cost. The C library also offers CHD (\~2.07 bits/key, fastest build) and BRZ (external-memory build for billions of keys).

## Compared with alternatives

Pick cmph when the key set is built at run time and is far too large for compile-time tables such as frozen, constexpr-phf or ConstexprCore/perfect_hash: 10^6 to 10^9 keys, a serialized or mmapped function, or an external-memory build with BRZ. For a runtime std::unordered_map replacement, fph-table's dynamic perfect-hash map has published figures; cxxmph::mph_map has only an unquantified header claim.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools/libtool builds libcmph, and libcxxmph with --enable-cxxmph); cxxmph is 'header-mostly' and can be source-dropped as mph_map.h plus mph_index.cc, trigraph.cc, mph_bits.cc and MurmurHash3.cpp |
| **Dependencies** | none at runtime beyond libm; autotools to build; the check library only for the optional unit tests |
| **Minimum toolchain** | C library: portable C with autotools. cxxmph: C++11 (configure adds -std=c++0x or gnu++0x) on GCC or Clang |
| **Platforms** | C library: GNU/Linux and WIN32, reported to work on OpenBSD and Solaris (README). cxxmph: GCC/Clang on POSIX systems, because of __builtin_expect and random(). No SIMD or architecture requirements. |
| **Thread safety** | not documented; cxxmph's const find() does not modify state, so concurrent readers of a fully built map look safe, but any insert can rebuild the whole table and index construction calls the global random() |
| **Drop-in for the baseline** | partial — cxxmph::unordered_map/mph_map mirror find, insert, erase, operator[], begin/end, size, clear and rehash, but iterators are forward-only with no postfix ++, keys are not const, the allocator is ignored, several members are missing, and iterator/reference stability is much weaker than std::unordered_map |

## Gotchas

- In the zvelo copy, MPHIndex owns a raw new[] rank table and defines no copy constructor, so copying or assigning a populated map double-frees it; bonitao/cmph replaced it with std::vector.
- A failed build is fatal: if BDZ finds no acyclic hypergraph in 1000 random seeds, mph_map::pack() calls exit(-1). Keys other than strings and built-in integers are hashed through std::hash truncated to 32 bits, so two keys that share those 32 bits collide for every seed and trigger this; by the birthday bound that is a real risk from about 10^5 keys.
- Call rehash() after bulk loading (the benchmark does this before timing): until then pack() keeps twice the slot count reserved and recent inserts sit in the slack map. rehash() shrinks to fit, so the first insert after it triggers a full rebuild.
- C API input must be duplicate-free, or the build fails with 'Unable to create minimum perfect hashing function' (FAQ, zvelo issue #2). An open report (bonitao issue #5) describes a memcpy pointer-arithmetic bug in BRZ's buffer_entry.c; the same line is present in this copy.

## Caveats and trade-offs

The 10-50% figure is a prose claim in the mph_map.h header. No results, compiler, flags or hardware are published; the header only advises -O3 -DNDEBUG. The same header warns: 'Those classes are not necessarily faster than their existing counterparts. Benchmark your code before using it.' A benchmark harness exists (cxxmph/bm_map.cc, bm_common.cc, benchmark.cc), but the URLS100k dataset is not in the repo. zvelo/cmph is a 2012 import: its last code change is 2012-12-05, and the 2017 commit only deleted a config file. The author's own repo, github.com/bonitao/cmph (Davi de Castro Reis), has the same header and was last updated 2026-04-27. License: COPYING says dual 'LGPL version 2' / MPL 1.1, but the LGPL-2 file contains LGPL 2.1 text. GitHub reports NOASSERTION, and the files do not say whether the LGPL is '-only' or '-or-later'. In cxxmph, stringpiece.h is BSD and MurmurHash is MIT.

cxxmph containers are read-mostly: cheap lookups but the perfect hash is rebuilt on structural change, so it favors static/rarely-modified key sets. Author's own comment warns "those classes are not necessarily faster than their existing counterparts, benchmark your code before using it." Core cmph library targets very large (up to billions of) key sets, unlike gperf which targets small compile-time sets.

## Maintenance

zvelo/cmph is an abandoned 2012 import (last code change 2012-12-05; the 2017 commit only deleted a config file), so vendor the author's active repo github.com/bonitao/cmph instead: it has CI, recent commits (latest 2026-04-27, mostly tooling) and a fix for the rank-table copy bug, under the same LGPL-2.x / MPL-1.1 dual license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is a first-party prose claim in the mph_map.h header ('about 10%-50% faster than unordered_map' for &gt;100k URLs). No results, compiler, flags or hardware are published. A harness exists (cxxmph/bm_map.cc runs mph_map against std::unordered_map), but its URLS100k dataset is not in the repo and no output is given, so the claim stays at C.
- **Verifier notes:** The quote is verbatim on the page. Consider changing repo_url to the author's active upstream, https://github.com/bonitao/cmph (20 stars, last commit 2026-04-27). zvelo/cmph (91 stars) is a stale 2012 import, not a GitHub fork, so maintenance_status 'abandoned' is correct for this URL. Metadata checked: 91 stars, last commit 2017-03-02, not archived; license kept as recorded because the LGPL variant cannot be pinned down exactly.
- **Fields the verifier corrected:** `baseline`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zvelo/cmph>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_map.h>
  - <https://github.com/zvelo/cmph/tree/master/cxxmph>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/bm_map.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/bm_common.h>
  - <https://github.com/zvelo/cmph/blob/master/COPYING>
  - <https://github.com/zvelo/cmph/blob/master/LGPL-2>
  - <https://github.com/zvelo/cmph/blob/master/MPL-1.1>
  - <https://github.com/zvelo/cmph/blob/master/README>
  - <https://github.com/zvelo/cmph/blob/master/src/cmph.h>
  - <https://github.com/bonitao/cmph>
  - <https://github.com/bonitao/cmph/blob/master/README.md>
  - <https://github.com/bonitao/cmph/blob/master/COPYING>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/mph_map.h>
- **Sources the enricher read:**
  - <https://github.com/zvelo/cmph>
  - <https://github.com/zvelo/cmph/blob/master/README>
  - <https://github.com/zvelo/cmph/blob/master/COPYING>
  - <https://github.com/zvelo/cmph/blob/master/configure.ac>
  - <https://github.com/zvelo/cmph/tree/master>
  - <https://github.com/zvelo/cmph/commits/master>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_map.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_index.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_index.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_bits.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/seeded_hash.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/hollow_iterator.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/trigraph.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/stringpiece.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/bm_map.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/bm_common.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/bm_common.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/map_tester.h>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/mph_map_test.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/dense_hash_map_test.cc>
  - <https://github.com/zvelo/cmph/blob/master/cxxmph/Makefile.am>
  - <https://github.com/zvelo/cmph/blob/master/src/cmph.h>
  - <https://github.com/zvelo/cmph/blob/master/src/buffer_entry.c>
  - <https://github.com/zvelo/cmph/issues/2>
  - <https://github.com/zvelo/cmph/issues/3>
  - <https://github.com/zvelo/cmph/issues/4>
  - <https://github.com/zvelo/cmph/issues/5>
  - <https://github.com/zvelo/cmph/pulls?q=is%3Apr>
  - <https://github.com/bonitao/cmph>
  - <https://github.com/bonitao/cmph/blob/master/README.md>
  - <https://github.com/bonitao/cmph/tree/master>
  - <https://github.com/bonitao/cmph/commits/master>
  - <https://github.com/bonitao/cmph/commit/6e9f152f>
  - <https://github.com/bonitao/cmph/commit/a69bdded>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/mph_map.h>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/mph_index.h>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/mph_index.cc>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/bm_map.cc>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/seeded_hash.h>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/hollow_iterator.h>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/Makefile.am>
  - <https://github.com/bonitao/cmph/blob/master/cxxmph/mph_map_test.cc>
  - <https://github.com/bonitao/cmph/blob/master/docs/faq.html>
  - <https://github.com/bonitao/cmph/blob/master/docs/bdz.html>
  - <https://github.com/bonitao/cmph/blob/master/docs/comparison.html>
  - <https://github.com/bonitao/cmph/blob/master/.github/workflows/main.yml>
  - <https://github.com/bonitao/cmph/issues/1>
  - <https://github.com/bonitao/cmph/issues/3>
  - <https://github.com/bonitao/cmph/issues/5>
  - <https://github.com/bonitao/cmph/pulls?q=is%3Apr>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/zvelo/cmph`) · [data/wave1-phf/enrich/raw/github_com_zvelo_cmph.json](../../../data/wave1-phf/enrich/raw/github_com_zvelo_cmph.json) (enrichment confidence 0.75)

</details>
