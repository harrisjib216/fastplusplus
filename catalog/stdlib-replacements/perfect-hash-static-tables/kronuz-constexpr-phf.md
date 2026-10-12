# constexpr-phf (Kronuz/phf)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 constexpr minimal perfect hash for fixed integer key sets; lookups \~2.5x faster than std::unordered_map in author benchmarks.

| | |
|---|---|
| **Beats** | std::unordered_map, std::set, if-ladder, switch (binary search), gperf |
| **Claimed result** | vs unordered_map/if-ladder/switch: 1.2-1.3 ns/lookup for phf at N=6..1000 vs 2.4-162 ns (if-ladder), 4.0-40 ns (switch), 3.1-3.2 ns (unordered_map). String dispatch (192 field-type names): gperf 14 ns, phf hash-only 18 ns, phf hash+verify 21 ns, compile-time trie 28 ns, std::unordered_map 29 ns, frozen::unordered_set 40 ns, std::set 82 ns/op |
| **Workload** | Integer-core find() at N=6..1000 keys; string dispatch benchmark hashing Xapiand's 192 field-type names, and a 570-word English stop-word filter over a 464K-word text, comparing hash-only and hash+verify constexpr-phf lookup against gperf, frozen::unordered_set, a compile-time trie, std::unordered_map and std::set. |
| **Metric** | latency |
| **Hardware** | x86_64 (no specific CPU model stated) |
| **Compiler and flags** | GCC 11, -O3 |
| **Adoption** | 37 stars |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/Kronuz/constexpr-phf) · [benchmark](https://github.com/Kronuz/constexpr-phf#benchmarks) |

## Verdict

In the author's harness (GCC 11, -O3, x86_64 with no CPU model, libstdc++ inferred), find() on runtime-built tables of 6-1000 random uint32 keys took 1.2-1.3 ns per lookup against 3.1-3.2 ns for std::unordered_map&lt;uint32_t,uint32_t&gt; (\~2.5x); this was an all-hit loop of independent lookups, and the 'if-ladder' and 'switch' columns are a runtime loop and std::lower_bound, not compiler-generated code. On 192 Xapiand field-type strings with a 50/50 hit/miss mix, hash+verify took 21 ns/op against 29 ns for std::unordered_map&lt;std::string,int&gt; and 82 ns for std::set, while gperf took 14 ns.

## Use it when

- Key set known at build time and already integral (enum values, opcodes, protocol or field IDs, precomputed string hashes), from a handful to about a thousand keys, where you need key to dense index for a parallel array.
- Replacing a sparse switch or if/else ladder: with a constexpr table, find(hash("...")) is a constant expression usable as a case label, so the dispatch compiles to a jump table.
- Hot lookups on small fixed sets where std::unordered_map's hash-plus-probe floor (about 3.1-3.2 ns in the author's runs) matters and a flat \~1.2-1.3 ns per find() is worth a custom API.
- Code that must avoid heap allocation or static-init work: a constexpr table is plain arrays in the binary, with no dependencies beyond the standard library.
- String keyword dispatch where you control the hash and can add one string compare, and do not want gperf's separate code-generation step.

## Skip it when

- Keys change at runtime: there is no insert, erase or rehash, and even runtime assign() rebuilds the whole table and needs the key count N as a template parameter.
- You want native string keys or mapped values out of the box: phf.hh is integer-only, the string wrapper exists only as benchmark code (bench/phf_dispatch.hh), and the `keywords` front-end that ARCHITECTURE.md and AGENTS.md point to returns 404.
- Raw string-lookup speed matters most and a codegen step is acceptable: gperf ran 14 ns/op against 21 ns for phf hash+verify in this repo's own 192-keyword benchmark.
- Large constexpr key sets: construction is a compile-time search, compile-time cost is not measured anywhere, and the repo only builds constexpr tables of 8 keys (test.cc, demo.cc); its 1000- and 5000-key runs use runtime assign().
- You need a proven dependency: 37 stars, one closed issue, no tags or releases (README pins GIT_TAG master), and the lookup was rewritten in July 2026, with a GCC 13 constexpr fix the next day; MSVC support is not documented.

## How it is fast

It uses a two-level CHD ("hash, displace, and compress", Belazzougui/Botelho/Dietzfelbinger, ESA 2009) scheme. The key's low bits select a bucket, and the bucket's stored multiplier and offset place the key with a division-free multiply-shift, ((k \* mul) &gt;&gt; shift) + off, into a power-of-two index table; this replaces the classic prime modulo. A lookup is therefore one mask, one multiply, one shift, two array reads and one key compare, with no probing, heap or pointer chasing, so the cost stays at about 1.2-1.3 ns from 6 to 1000 keys. The displacement search (largest buckets first, successive prime multipliers, rollback on collision) runs in constexpr, and key sets that defeat plain multiply-shift (such as distinct powers of two) fall back automatically to an xorshift-multiply pre-mix, which ARCHITECTURE.md says costs about half the multiply-shift speedup.

## Compared with alternatives

Pick it over frozen or ConstexprCore/perfect_hash when the keys are already integers and you want dense [0, N) slots usable as constexpr case labels; for strings, those libraries take string keys natively, and gperf beat it in its own harness (14 vs 21 ns). ConstexprCore's table showing kronuz::phf at 0.22 vs its own 1.08 billion queries/s pins constexpr-phf at 2019 commit 0776e93, before the multiply-shift rewrite, so that table does not measure the current lookup.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only; &lt;iostream&gt; only under PHF_DEBUG). The benchmarks alone fetch frozen and ctrie. |
| **Minimum toolchain** | C++17 (CMake target sets cxx_std_17; CMake 3.14 for the FetchContent path). Commit 55ac236 reports validation on Clang, GCC 11, g++-13.4 and g++-16; g++-13.3 needed that fix for find() as a case label. MSVC not documented. |
| **Platforms** | any C++17 target (portable integer code, no intrinsics); published numbers are x86_64 only |
| **Thread safety** | Not documented. Lookups are const member functions over immutable arrays with no internal mutable state, so concurrent reads of a built table are safe by construction; assign() and clear() mutate. |
| **Drop-in for the baseline** | partial — find()/count()/at() reuse std set/map names, but find() returns a dense slot index or phf::npos instead of an iterator, no values are stored, keys must be integral, and the set is fixed. Against a switch or if-ladder it replaces the comparisons, and the case labels become find(key) constants. |

## Gotchas

- Only lookup() skips the membership check. find(), count() and at() compare the stored integer key and reject non-members, despite the README's note that find() 'hands back whatever sits there'. The real risk is with strings: a non-member whose hash equals a member's hash is reported as a hit unless you compare the stored string.
- Key types: the correctness suite tests only uint32_t, uint64_t and int keys. By my reading of phf.hh (not tested), 8/16-bit key types are promoted to 32-bit before the multiply, so ((k \* mul) &gt;&gt; shift) can index past the table. Signed 64-bit keys use signed multiplication, so overflow is UB and negative results break the index. Prefer uint32_t or uint64_t.
- Build failures throw std::invalid_argument (duplicate keys, empty or oversized input, 'cannot find suitable table'), and in a constexpr context these become compile errors. at() and operator[] throw std::out_of_range. A -fno-exceptions mode is not documented.
- Memory is not compact: each index slot holds the key plus a size_t position (16 bytes for uint32_t keys on 64-bit targets), the index is the next power of two at or above 1.25N, and buckets add 8 bytes each. That is about 41 KB for 1000 uint32_t keys (derived from the phf.hh layout), while the benchmarks loop over a hot 4096-lookup work list.

## Caveats and trade-offs

First-party benchmark (README plus bench/), not independently reproduced. Hardware is stated only as x86_64, with no CPU model. In bench/compare.cc, the 'if-ladder' is a runtime loop over the key array, and the 'switch (binary search)' column is std::lower_bound over a sorted vector, not compiler-generated switch code. std::unordered_map&lt;uint32_t,uint32_t&gt; uses the default std::hash. The string-dispatch benchmark uses a 50/50 mix of members and non-members (200k lookups, best of 15) against std::unordered_map&lt;std::string,int&gt; and std::set&lt;std::string&gt;. The README does not say which hash (fnv1a or wordwise) produced its 21 ns 'hash + verify' row. The stop-word benchmark has no published numbers, only a claim that it 'edges ahead of gperf'. libstdc++ is inferred from GCC 11, which has no -stdlib option in this build. gperf, frozen and trie numbers come from the same first-party harness.

Integer keys only (strings must be pre-hashed by the caller, and hash-only lookups can misdispatch a non-member key unless verified). Fixed key set at build time, no insert/erase/rehash. Large key sets increase compile time since the perfect hash is searched at compile time.

## Maintenance

Active again since July 2026 (multiply-shift rewrite, GCC 13 fix, benchmarks, README) after a 2019-2026 gap; MIT-licensed, and the single \~1,500-line header (two-thirds of it a prime table) is easy to vendor, but it has a small user base and no tagged releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README numbers are first-party and come from public bench code (bench/bench.cc, bench/compare.cc, bench/dispatch_field_types.cc; CMakeLists.txt compiles them with -O3). GCC 11 is stated, but the hardware is given only as 'x86_64' with no CPU model, so the tier is C, not A.
- **Verifier notes:** All claimed numbers are verbatim in the README Benchmarks section. Derived ratios vs std::unordered_map: \~2.5-2.7x for integer keys; \~1.4x (hash+verify) or \~1.6x (hash-only) for strings; \~3.9x vs std::set. Metadata checked: MIT, 37 stars, last commit 2026-07-12 (the README rewrite that added these tables), not archived, not a fork.
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Kronuz/constexpr-phf>
  - <https://github.com/Kronuz/constexpr-phf#benchmarks>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/CMakeLists.txt>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/bench.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/compare.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/dispatch_field_types.cc>
- **Sources the enricher read:**
  - <https://github.com/Kronuz/constexpr-phf>
  - <https://github.com/Kronuz/constexpr-phf#benchmarks>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/README.md>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/ARCHITECTURE.md>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/AGENTS.md>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/CMakeLists.txt>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/phf.hh>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/test/correctness.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/test/test.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/examples/demo.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/bench.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/compare.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/dispatch_field_types.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/dispatch_stop_words.cc>
  - <https://github.com/Kronuz/constexpr-phf/blob/master/bench/phf_dispatch.hh>
  - <https://github.com/Kronuz/constexpr-phf/commits/master>
  - <https://github.com/Kronuz/constexpr-phf/commit/55ac236>
  - <https://github.com/Kronuz/constexpr-phf/issues?q=is%3Aissue>
  - <https://github.com/Kronuz/constexpr-phf/tags>
  - <https://github.com/Kronuz/constexpr-phf/releases>
  - <https://github.com/Kronuz/keywords>
  - <https://github.com/ConstexprCore/perfect_hash>
  - <https://github.com/ConstexprCore/perfect_hash/blob/HEAD/benchmarks/CMakeLists.txt>
  - <https://github.com/ConstexprCore/perfect_hash/blob/HEAD/benchmarks/bench_protocol.cpp>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/kronuz/constexpr-phf`) · [data/wave1-phf/enrich/raw/github_com_kronuz_constexpr_phf.json](../../../data/wave1-phf/enrich/raw/github_com_kronuz_constexpr_phf.json) (enrichment confidence 0.85)

</details>
