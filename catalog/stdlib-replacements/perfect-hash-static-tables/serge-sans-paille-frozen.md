# frozen

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++14 constexpr immutable set/map/unordered_map built on compile-time perfect hashing; beats std::unordered_map on fixed key sets.

| | |
|---|---|
| **Beats** | std::unordered_map (arXiv 2602.22506 demos); std::set and std::unordered_set in the author's first-party 2018 Quarkslab microbenchmark |
| **Claimed result** | Construction+lookup runtime, frozen::unordered_map vs std::unordered_map: element-symbol-&gt;mass demo 44.9 us vs 89.6 us (\~2.0x), codon-&gt;amino-acid demo 1365.5 us vs 1746.8 us (\~1.28x), ticker-&gt;price update demo 15804.5 us vs 21228.1 us (\~1.34x) (ratios derived from page data, Figure 2 averages) |
| **Workload** | Three application demos from arXiv 2602.22506: 1,024 random lookups in an 84-key element-symbol-&gt;atomic-mass map (each lookup timed individually); translation of 65,536 random codons through a 64-key codon-&gt;amino-acid map; 64 x 4,042 random price updates in a 4,042-key ticker-&gt;price map. Reported time = runtime construction + lookup, averaged over repeated runs. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-1240P laptop (runs under nice -n -20, chrt -f 98, ASLR disabled) |
| **Compiler and flags** | g++ 15.2.1, -std=c++23 -O3 -march=native (plus raised -fconstexpr-ops-limit / -fconstexpr-loop-limit) |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/serge-sans-paille/frozen) · [benchmark](https://arxiv.org/pdf/2602.22506) |

## Verdict

The static_maps preprint (arXiv 2602.22506) timed construction plus lookup for frozen::unordered_map (frozen::basic_string keys, built at compile time) against std::unordered_map&lt;std::string_view&gt; (libstdc++, built at runtime inside the timed region). Setup: g++ 15.2.1 -O3 -march=native on a Core i5-1240P laptop. Results: 44.9 vs 89.6 us for 1,024 individually timed lookups in an 84-key map (\~2.0x); 1365.5 vs 1746.8 us translating 65,536 codons through a 64-key map (\~1.28x); 15804.5 vs 21228.1 us for 258,688 value updates in a 4,042-key map (\~1.34x).

## Use it when

- Lookup tables whose key set is fixed at build time: keyword/command/opcode dispatch, enum&lt;-&gt;string, symbol tables, HTML entities (all shipped as examples). Tens to a few thousand keys.
- You need lookups in constant expressions (static_assert, template arguments, constexpr functions), or want constant-key lookups folded away entirely.
- You want no static-initialization cost and no heap: declare constexpr or constinit and the table goes into the binary. FROZEN_NO_EXCEPTIONS (or -fno-exceptions) turns at()'s throw into std::abort for embedded builds.
- Keys are fixed but values change at runtime, like the preprint's 4,042-key ticker-&gt;price table (\~1.34x vs std::unordered_map). Use a constinit map and write through at() or find()-&gt;second.
- Ordered lookups (lower_bound/upper_bound, sorted iteration) over immutable data, where frozen::map/set replace a node-based std::map/std::set with a sorted array.

## Skip it when

- Keys are only known at runtime, or the set changes: there is no insert, erase or rehash. Use a runtime hash map, or a runtime-built PHF such as fph-table or cmph.
- Large key sets. In the preprint, frozen took 21.1 s to compile the 4,042-key demo vs 1.5 s for std::unordered_map. Big tables hit constexpr step limits (-fconstexpr-steps / -fconstexpr-ops-limit), and issue #76 (open) reports VS2017 failing at 500 entries.
- Raw lookup throughput is the goal. static_maps ran at 45-97% of frozen's time in the same preprint, and the ConstexprCore/perfect_hash benchmark shows frozen::unordered_map at 0.16 vs 1.08 billion queries/s.
- Long string keys on a hot path. The default string hash is a byte-at-a-time FNV-1a-style loop and can run twice per lookup (G then H), so cost grows with key length.
- MSVC with warnings-as-errors: the constexpr hash triggers C4307 'integral constant overflow' warnings (#68, #178). Also, wasm32 has an open, unreproduced report of failed lookups (#198).

## How it is fast

unordered_\* uses a two-level perfect hash (not minimal) in the hash-and-displace style of Steve Hanov's 'Throw away the keys', built entirely in constexpr. Keys are seed-hashed into M buckets, where M is the next power of two at or above N (doubled below 32 keys). Buckets are processed largest first. A singleton bucket stores its item index directly in table G. A larger bucket gets a per-bucket seed, found by random search with minstd_rand, that puts all its items into free slots of table H. A lookup is one hash into G, at most one more seeded hash into H, then a single key comparison: no probing, no chains, no heap. frozen::set and frozen::map are sorted arrays searched by a fully unrolled branchless binary search.

## Compared with alternatives

Pick frozen over ConstexprCore/perfect_hash or constexpr-phf (Kronuz) when you want the long-established, C++14-compatible option with a full std-like container family, including ordered map/set with lower_bound. Pick those (or static_maps) when lookup throughput matters most: ConstexprCore's benchmark has frozen::unordered_map at 0.16 vs 1.08 billion queries/s. Unlike the gperf-style generators (triehash, strager/perfect-hash-tables), frozen needs no external build step.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | C++14. README: Clang 5+, GCC 6+ (slow constexpr), VS2017; GCC 5 unsupported. CI builds GCC 10-13, Clang 13/14/16, AppleClang and MSVC at C++14/17/2a. std::string_view keys need C++17, constinit needs C++20. CMake 3.10+ for the optional install/find_package path. |
| **Platforms** | any (portable C++, no intrinsics). CI runs on Linux, macOS and Windows; the Windows job builds but does not run the tests. One open, unconfirmed wasm32 lookup bug report (#198). |
| **Thread safety** | not documented. Lookups are const member functions that write nothing, so concurrent reads of a const or constexpr container are safe, as with any const object. Value writes on a mutable (constinit) map need external synchronization. |
| **Drop-in for the baseline** | partial — the lookup API matches (find/at/count/contains/equal_range, pair&lt;const K, V&gt; iteration), but: N is a template parameter; there is no insert, erase, operator[], rehash or allocator; hashers are frozen's seeded elsa&lt;T&gt;(value, seed), not std::hash; string keys must be frozen::string, or std::string_view after including &lt;frozen/bits/elsa_std.h&gt;. |

## Gotchas

- Duplicate keys are not reliably caught. The Step 1.5 check in bits/pmh.h compares items[0] with items[i] rather than with the members of each bucket, so most duplicates make the seed search spin. Under constexpr that shows up as a constexpr step-limit error; a map built at runtime loops forever (#181).
- A map that is neither constexpr nor constinit may be built at runtime, with the seed search running at static-init or first use. Use constinit (C++20), as examples/value_modification.cpp does, to force compile-time construction and get an error when it fails.
- There is no operator[]. at() throws std::out_of_range, or calls std::abort when exceptions are off. Custom hashers must accept a seed and should be close to pairwise-independent; a weak hash does not break correctness but makes compiles slow or exceed constexpr limits.
- The default key type frozen::string is a non-owning pointer+length view. std::string_view keys work only if you include the internal header frozen/bits/elsa_std.h, which the README does not mention. The version macros read 1.1.1 and the CMake project reads 1.1.0, while the latest tag is 1.2.0.

## Caveats and trade-offs

arXiv 2602.22506 is a non-peer-reviewed preprint about a competing library (static_maps), which beats frozen in all three demos. The frozen-vs-std ratios are derived from its Figure 2 averages; the Figure 2 caption is misprinted as map vs std::map. The std::unordered_map timings include runtime construction, which frozen does at compile time. The element demo wraps every single lookup in high_resolution_clock calls, so its \~2.0x partly reflects construction and timer overhead; the lookup-dominated codon demo shows \~1.28x. Keys differ: std::unordered_map&lt;std::string_view,...&gt; with std::hash vs frozen::basic_string with frozen's own hash. The version of the frozen copy bundled in the artifact is not stated. libstdc++ is inferred from the g++ build with no -stdlib flag. The earlier first-party Quarkslab post (Serge Guelton, 20 Feb 2018) reports frozen::set/unordered_set vs std::set/unordered_set on 32 keys, where each reported time is one pass of 32 lookups: int unordered_set 173 vs 544 ns (\~3.1x), absent keys 131 vs 500 ns (\~3.8x); int set 58 vs 153 ns (\~2.6x); strings x1.7 (set) to x3.3 (unordered_set, absent key). That post states the CPU (i7-6600U) but not the benchmark compiler or flags, and its std string containers hold frozen::string keys hashed by frozen's own std::hash specialization.

Containers are immutable/fixed-capacity: no insert/erase/rehash after construction (constexpr keys are permanently fixed; without constexpr, values may be updated but keys cannot). Compile time and template-instantiation cost grow with key-set size. Header-only, no runtime dependency.

## Maintenance

The README says the library is in maintenance mode: it still merges cleanups (last commit 2026-09-23; 1.2.0 tagged 2024-06). It is Apache-2.0 and header-only, so you can copy include/frozen into your tree or install via CMake.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The cited Quarkslab post only supports C. Its clang++-5.0 -O3 line belongs to an assembly listing, not the benchmark, and the repo's Feb-2018 benchmarks/Makefile builds with \$(CXX) -O2. A is kept on stronger third-party evidence: arXiv 2602.22506 (Myhal & Serang, 2026) benchmarks frozen::unordered_map against std::unordered_map with public MIT code (figshare 10.6084/m9.figshare.31416038: main_frozen.cpp, main.cpp, codon_to_amino_acid.cpp, stock_to_price.cpp, Makefile), g++ 15.2.1 -std=c++23 -O3 -march=native, on an Intel Core i5-1240P.
- **Verifier notes:** The Quarkslab numbers are verbatim on the page, but the record misattributed the clang++-5.0 -O3 line: it belongs to the assembly listing, not the benchmark. I replaced benchmark_url with the independent arXiv 2602.22506 preprint and its public figshare artifact, which keeps tier A and compares directly against std::unordered_map. Metadata checked: Apache-2.0, 1,578 stars, last commit 2026-09-23, not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `hardware`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** On a 92-key C++ keyword set (200k words, 1:8 keyword:identifier) frozen::unordered_map took 18.888 ns per lookup vs 5.322 ns for developer source's compile-time perfect hash table (3.55x slower; 3.5-3.7x across runs) and 29.168 ns for std::unordered_map (frozen 1.54x faster, derived). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-libraries)
- **Pages the verifier opened:**
  - <https://blog.quarkslab.com/frozen-zero-cost-initialization-for-immutable-containers-and-various-algorithms.html>
  - <https://blog.quarkslab.com/frozen-an-header-only-constexpr-alternative-to-gperf-for-c14-users.html>
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/serge-sans-paille/frozen/tree/master/benchmarks>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/Makefile>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/bench_int_set.cpp>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/bench_str_set.cpp>
  - <https://github.com/serge-sans-paille/frozen/blob/9c7a44961f/benchmarks/Makefile>
  - <https://github.com/serge-sans-paille/frozen/blob/9c7a44961f/benchmarks/bench_int_set.cpp>
  - <https://github.com/serge-sans-paille/frozen/blob/9c7a44961f/include/frozen/string.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/string.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/README.rst>
  - <https://arxiv.org/pdf/2602.22506>
  - <https://arxiv.org/abs/2602.22506>
  - <https://api.figshare.com/v2/articles/31416038>
  - <https://ndownloader.figshare.com/files/62175938>
  - <https://ndownloader.figshare.com/files/62175947>
  - <https://ndownloader.figshare.com/files/62176169>
  - <https://ndownloader.figshare.com/files/62176151>
  - <https://ndownloader.figshare.com/files/62176136>
  - <https://ndownloader.figshare.com/files/62175950>
  - <https://ndownloader.figshare.com/files/62175941>
- **Sources the enricher read:**
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/serge-sans-paille/frozen/blob/master/README.rst>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/pmh.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/unordered_map.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/unordered_set.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/map.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/string.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/algorithm.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/random.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/algorithms.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/basic_types.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/elsa.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/elsa_std.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/hash_string.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/version.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/defines.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/exceptions.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/include/frozen/bits/constexpr_assert.h>
  - <https://github.com/serge-sans-paille/frozen/blob/master/CMakeLists.txt>
  - <https://github.com/serge-sans-paille/frozen/blob/master/cmake/detect_cxx_version.cmake>
  - <https://github.com/serge-sans-paille/frozen/blob/master/.github/workflows/linux.yml>
  - <https://github.com/serge-sans-paille/frozen/blob/master/.github/workflows/osx.yml>
  - <https://github.com/serge-sans-paille/frozen/blob/master/.github/workflows/windows.yml>
  - <https://github.com/serge-sans-paille/frozen/blob/master/examples/value_modification.cpp>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/bench_str_map.cpp>
  - <https://github.com/serge-sans-paille/frozen/blob/master/benchmarks/Makefile>
  - <https://github.com/serge-sans-paille/frozen/blob/master/tests/test_elsa_std.cpp>
  - <https://github.com/serge-sans-paille/frozen/commits/master>
  - <https://github.com/serge-sans-paille/frozen/commit/61dce5ae18ca59931e27675c468e64118aba8744>
  - <https://github.com/serge-sans-paille/frozen/commit/83a5604b>
  - <https://github.com/serge-sans-paille/frozen/tags>
  - <https://github.com/serge-sans-paille/frozen/issues>
  - <https://github.com/serge-sans-paille/frozen/issues/198>
  - <https://github.com/serge-sans-paille/frozen/issues/156>
  - <https://github.com/serge-sans-paille/frozen/issues/178>
  - <https://github.com/serge-sans-paille/frozen/issues/193>
  - <https://github.com/serge-sans-paille/frozen/issues/76>
  - <https://github.com/serge-sans-paille/frozen/issues/68>
  - <https://github.com/serge-sans-paille/frozen/issues/60>
  - <https://github.com/serge-sans-paille/frozen/issues/28>
  - <https://github.com/serge-sans-paille/frozen/issues/32>
  - <https://github.com/serge-sans-paille/frozen/issues/181>
  - <https://github.com/serge-sans-paille/frozen/issues/72>
  - <https://arxiv.org/abs/2602.22506>
  - <https://arxiv.org/pdf/2602.22506>
  - <https://api.figshare.com/v2/articles/31416038>
  - <https://ndownloader.figshare.com/files/62175938>
  - <https://ndownloader.figshare.com/files/62175947>
  - <https://ndownloader.figshare.com/files/62176136>
  - <https://ndownloader.figshare.com/files/62176151>
  - <https://ndownloader.figshare.com/files/62176004>
  - <https://ndownloader.figshare.com/files/62176169>
  - <https://blog.quarkslab.com/frozen-zero-cost-initialization-for-immutable-containers-and-various-algorithms.html>
  - <https://blog.quarkslab.com/frozen-an-header-only-constexpr-alternative-to-gperf-for-c14-users.html>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/serge-sans-paille/frozen`) · [data/wave1-phf/enrich/raw/github_com_serge_sans_paille_frozen.json](../../../data/wave1-phf/enrich/raw/github_com_serge_sans_paille_frozen.json) (enrichment confidence 0.85)

</details>
