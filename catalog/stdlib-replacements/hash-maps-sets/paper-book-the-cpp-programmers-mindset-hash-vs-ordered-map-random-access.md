# Hash maps versus ordered maps, random-access lookup (The C++ Programmer's Mindset, ch. 5, Table 5.1)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Book benchmark: hash maps find random int64 keys 6-9x faster than std::map and other ordered maps at 256-1,024 keys.

| | |
|---|---|
| **Beats** | std::map |
| **Claimed result** | Hash maps roughly 10x faster than ordered maps, lookup time nearly flat with size. CPU ns at 256/1024 keys: std::map 23.3/34.9, std::unordered_map 3.56/3.81, absl::btree_map 19.5/24.1, absl::flat_hash_map 3.81/3.89, absl::node_hash_map 3.95/4.29, boost::container::flat_map 25.9/31.4, boost::unordered_map 3.68/3.66, boost::unordered_flat_map 3.93/4.03 (std::unordered_map is about 6.5x and 9.2x faster than std::map, derived). Book figures as paraphrased in the seed lead, not on the repo page. |
| **Workload** | Random-key lookup via operator[] on a map holding int64 keys 0..n-1 (n = 256 and 1024), Google Benchmark CPU ns per lookup, including the per-iteration std::mt19937_64 draw; eight maps compared: std::map, std::unordered_map, absl::btree_map, absl::flat_hash_map, absl::node_hash_map, boost::container::flat_map, boost::unordered_map, boost::unordered_flat_map. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7900x (per the book as paraphrased in the lead; not recorded in the repo). |
| **Compiler and flags** | Not stated. Chapter-05/CMakeLists.txt sets C++20, no build type or optimisation flags; vcpkg.json pins abseil &gt;= 20240722.0 and boost-container/-container-hash/-unordered &gt;= 1.86.0. |
| **Adoption** | 20 stars (Packt companion repository for the 2025 book) |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset) · [benchmark](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-05/bench_map_random_access.cpp) |

## Verdict

The repository holds benchmark source only; the book's own run, relayed by the seed lead on an AMD Ryzen 7900X with compiler, flags and standard library unstated, put std::map at 23.3/34.9 ns per random operator[] lookup at 256/1,024 int64 keys against 3.56/3.81 ns for std::unordered_map (about 6.5x and 9.2x, derived). All five hash maps fell between 3.56 and 4.29 ns and the three ordered maps between 19.5 and 34.9 ns, every figure including the random-number draw.

## Use it when

- Point lookups (find, at, operator[]) by key where nothing needs sorted iteration, lower_bound/upper_bound or range scans: switching std::map to std::unordered_map is a near drop-in change inside the standard library.
- Small, cache-resident maps of hundreds to about a thousand entries with random access: in the relayed figures std::unordered_map (3.56/3.81 ns) was as fast as the Abseil and Boost hash maps (3.66-4.29 ns), so no third-party dependency is needed at this size.
- Integer keys that are dense or well spread, where the identity std::hash is adequate.
- Read-mostly lookup tables with random query keys, where the tree's mispredicted branches dominate std::map's cost.

## Skip it when

- You need sorted iteration, range queries, lower_bound/upper_bound or a deterministic iteration order: stay with std::map, absl::btree_map or boost::container::flat_map.
- Large (out-of-cache) maps or insert- and erase-heavy workloads: only 256 and 1,024 keys are measured here; at larger sizes the flat open-addressing maps in the sibling entries beat std::unordered_map itself (2.43x and 2.70x faster finds for absl::flat_hash_map and boost::unordered_flat_map in the sibling suite).
- Patterned or attacker-chosen integer keys with std::unordered_map's identity hash: keys that are multiples of the bucket count all land in one bucket; use a hash that mixes bits (absl::Hash, or a custom hasher).
- Code that keeps iterators across inserts or needs bounded worst-case latency: an insert that triggers a rehash invalidates all iterators of an unordered map and costs O(n) once, whereas std::map never invalidates on insert and stays O(log n).
- Keys without a good hash or equality but with a natural ordering (composite or floating-point keys with custom comparison), where writing a correct hash is the harder problem.

## How it is fast

A hash map turns a lookup into one hash computation plus a probe of roughly one bucket or slot (O(1) on average), while std::map descends a red-black tree about log2(n) levels deep (8 at 256 keys, 10 at 1,024), each step a dependent pointer load followed by a compare whose direction is random for random keys, so branch mispredictions and pointer chasing grow with depth. The B-tree (absl::btree_map) and sorted-vector (boost::container::flat_map) layouts cut pointer chasing but still binary-search with unpredictable branches, which is why they land within about 0.9-1.45x of std::map in the relayed figures (derived). std::hash&lt;int64_t&gt; is the identity in libstdc++ and libc++ (per the record), so with dense keys std::unordered_map pays almost nothing for hashing or collisions.

## Compared with alternatives

The sibling entries are hash-map libraries that beat std::unordered_map; this entry is the step before them: replace std::map with std::unordered_map when point lookups dominate and order is unused. At a few hundred to a thousand keys it showed no gain from absl::flat_hash_map or boost::unordered_flat_map, so reach for those (or ankerl::unordered_dense) once maps outgrow the cache or inserts dominate.

## Integration

| | |
|---|---|
| **Form** | header-only (std::unordered_map is standard library; the benchmark's Abseil maps link compiled Abseil targets such as absl::hash, and the Boost maps come from Boost.Container and Boost.Unordered) |
| **Dependencies** | none for std::unordered_map; the benchmark needs Abseil &gt;= 20240722.0 and boost-container, boost-container-hash and boost-unordered &gt;= 1.86.0 (Chapter-05/vcpkg.json), plus Google Benchmark and GTest, which CMakeLists.txt requires but the vcpkg manifest does not list |
| **Minimum toolchain** | C++20 (CMakeLists.txt), CMake 3.30+; the make_map&lt;Map&gt; helper takes template &lt;typename, typename&gt; class Map and passes std::map (four template parameters), which needs relaxed template-template matching (P0522): default in GCC's C++17 and later modes and in Clang 19+ (per the Clang 19.1.0 release notes, seen as a search snippet), so older Clang rejects it without -frelaxed-template-template-args |
| **Platforms** | any (portable C++); the relayed numbers come from an AMD Ryzen 7900X |
| **Thread safety** | Standard containers allow concurrent const access (find, at, iteration) with no writer; operator[], as the benchmark uses it, is not among the functions the standard treats as const for data races in associative and unordered containers, so concurrent lookups should use find or at, and any writer needs a lock. |
| **Drop-in for the baseline** | partial: std::unordered_map accepts the same find/at/operator[]/insert/erase calls as std::map, but needs std::hash and operator== instead of operator&lt;, drops ordered iteration and lower_bound/upper_bound, and invalidates iterators on rehash; the flat hash maps also move elements, so references are not stable. |

## Gotchas

- operator[] inserts a default-constructed value when the key is missing; the benchmark only queries keys it inserted, so it never pays for that, but lookup-only code should use find or at.
- The timed loop includes the std::mt19937_64 draw and uniform_int_distribution, and successive lookups are independent, so the CPU overlaps them: the 3.6-4.3 ns hash-map figures carry the RNG cost and reflect throughput rather than the latency of one dependent lookup, and the constant RNG cost compresses the 6.5x/9.2x ratios. There is no RNG-only baseline in this benchmark, and the generator is seeded from std::random_device, so key sequences differ between runs.
- Best case for std::unordered_map: dense keys 0..n-1 inserted in ascending order and an identity hash mean no collisions, and std::map's nodes are allocated in key order; at 256 and 1,024 entries everything fits in cache, so the flat versus node-based layouts cannot separate.
- Chapter-05/CMakeLists.txt sets no build type or optimisation flags, and these template-heavy containers are far slower in an unoptimised build, so pass -DCMAKE_BUILD_TYPE=Release; the code also relies on transitive includes for &lt;map&gt;, &lt;unordered_map&gt; and &lt;deque&gt;, which may break on another standard library.

## Known shortcomings

- Repo carries code only; numbers come from the book. std::hash&lt;int64_t&gt; is the identity in libstdc++/libc++ and keys are dense 0..n-1, so std::unordered_map gets a collision-free best case.
- Enricher: RNG draw inside the timed loop with independent lookups (throughput, not latency; ratios compressed, no RNG-only baseline); no build type in the chapter CMakeLists; transitive includes.

## Caveats and trade-offs

The numbers are the book's own figures as paraphrased in the seed lead; they are not printed anywhere on the repository pages opened (the repo holds the benchmark code and no results, and the Chapter-05 folder has no results files), and the book itself was deliberately not consulted. The data show absl::flat_hash_map and boost::unordered_flat_map are NOT faster than std::unordered_map at these sizes (3.81-4.03 ns versus 3.56-3.81 ns), so the win is hashing versus tree, not the third-party libraries; the book says flat and node variants did not differ because the data fit in cache. Only two tiny, cache-resident sizes; keys are the dense range 0..n-1 inserted in ascending order, and std::hash&lt;int64_t&gt; is the identity in libstdc++ and libc++, so std::unordered_map gets a collision-free best case (and std::map nodes are allocated in key order, which helps its locality). The timed region includes the std::mt19937_64 draw and uniform_int_distribution (a few ns), which compresses the ratios; the generator is seeded from std::random_device, so key sequences differ between runs. Standard library (libstdc++/libc++) and compiler flags not stated; Chapter-05/CMakeLists.txt sets no build type. Tier C: first-party book measurement with the CPU stated but not the flags. [retier] Enricher: the RNG draw sits inside the timed loop and the lookups are independent, so ns per lookup is overlapped throughput, not latency, and the RNG cost compresses the 6.5x and 9.2x ratios (no RNG-only baseline). No build type in the Chapter-05 CMakeLists. operator[] is not usable on const maps; the make_map template-template parameter needs P0522 (Clang 19+, or GCC in C++17 mode); the code relies on transitive includes for &lt;map&gt;, &lt;unordered_map&gt; and &lt;deque&gt;; vcpkg.json omits benchmark and gtest. Ordered alternatives land at 0.9-1.45x of std::map (derived).

Hash maps give no ordered iteration or range queries and need a hash function; std::unordered_map is node-based with stable references, absl/boost flat variants are not reference-stable. The comparison says ordered versus hashed, not which hash map is best.

## Maintenance

Packt companion repository, MIT-licensed, 20 stars and 8 forks; last commit 2026-01-22 (a README; code last changed in November 2025); the technique needs nothing beyond the standard library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter-05/bench_map_random_access.cpp benchmarks std::map against std::unordered_map, absl and boost maps at 256 and 1024 keys with Google Benchmark, but the repo holds code only; the ns figures are the book's own run relayed by the lead, with a CPU named but compiler, flags and standard library unstated, so first-party C.
- **Verifier notes:** Source matches the record: eight map types, Arg(256) and Arg(1024), operator[] lookups with the RNG draw inside the timed loop. Added the identity-hash, dense-key best case for std::unordered_map and the random_device seeding to caveats. Metadata confirmed: MIT, 20 stars, 8 forks, not a fork or archived, last commit 2026-01-22 (active).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-05/bench_map_random_access.cpp>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-05>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/bench_map_random_access.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/bench_containers.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/vcpkg.json>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-05>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/bench_map_random_access.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/bench_containers.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/benchmark_hash.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-05/vcpkg.json>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-cpp-programmers-mindset-hash-vs-ordered-map-random-access`) · [data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_hash_vs_ordered_map_random_access.json](../../../data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_hash_vs_ordered_map_random_access.json) (enrichment confidence 0.65)

</details>
