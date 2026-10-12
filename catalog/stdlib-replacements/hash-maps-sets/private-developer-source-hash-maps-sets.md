# fastcpp::flat_hash_map (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only SwissTable-style hash map: 1.8-5.5x faster than std::unordered_map on 1M uint64 keys, but slower than phmap on lookups.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | 5.52x faster to insert 1M uint64 keys into a new map (34.72ns vs 191.714ns per insert; one allocation for the table vs one node per entry). The row is labelled 'build from empty', but bench_vs_libraries calls reserve(1M) on both maps before inserting. 2.18x faster on 200k string-key lookups (33.947ns vs 73.922ns). \~1.78x faster hit lookups and \~4.59x faster miss lookups on 1M uint64 keys (18.911ns vs 33.687ns; 9.723ns vs 44.665ns, derived from page data). Caveat from the same file/README: phmap::flat_hash_map (vendored in the same repo) beats fastcpp::flat_hash_map on raw lookup by 1.29x (hits) and 1.39x (misses), which is why fastcpp's own map is kept only for its faster build path (34.72ns vs phmap 38.07ns). |
| **Workload** | 1M random uint64 keys from bench/bench_vs_libraries.cpp (all-hit lookup, all-miss lookup, and build = reserve(1M) then 1M operator[] inserts), plus 200k 'symbol_name_N' string keys, all hit, from bench/bench_hash_map.cpp (fastcpp uses find(string_view), std::unordered_map uses find(const std::string&)). All measured against std::unordered_map. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores; Ubuntu 24.04, Linux 6.18 (shared cloud VM) |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo). String row: run 2026-09-02-core, commit dfa74f2. 1M rows: re-measured with bench_vs_libraries at commit 2e21aae (run 2026-09-02-libraries, same flags), although the rows are tagged 2026-09-02-core. |
| **Adoption** | 0 stars (private repo) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](private:developer-source) · [benchmark](private:developer-source/blob/main/results/fastest.json) |

## Verdict

Against libstdc++ std::unordered_map (gcc 13.3.0, -O2 -march=native, minimum of 7 samples, on a 4-core Intel Xeon @ 2.10GHz shared cloud VM running Ubuntu 24.04), the author's own benchmarks measured 1M random uint64 keys: reserve(1M) plus 1M operator[] inserts, timed including teardown, at 34.7 vs 191.7 ns per insert (5.5x); hits at 18.9 vs 33.7 ns (1.78x); misses at 9.7 vs 44.7 ns (4.6x). 200k 'symbol_name_N' string-key hits measured 33.9 vs 73.9 ns (2.18x), with neither arm building a temporary string. These are first-party numbers from one machine, the repo says only within-row ratios are meaningful, and the same results file shows phmap beating this map on both lookup rows.

## Use it when

- Large maps (well beyond cache) of integer or pointer keys where many lookups miss: on 1M uint64 keys, misses took 9.7 vs 44.7 ns (4.6x) and hits 18.9 vs 33.7 ns (1.78x) against libstdc++ std::unordered_map.
- Build-heavy workloads where maps are filled and torn down often: 1M inserts after reserve() measured 34.7 vs 191.7 ns per insert (5.5x). This is the one path where it also edged the vendored phmap (1.07-1.10x).
- String-keyed symbol or lookup tables holding std::string keys and probed with std::string_view or string literals: 2.18x on 200k all-hit lookups. On the repo's 92-keyword set it measured 8.86 vs 23.2 ns.
- x86-64 builds: the 16-wide group match needs only SSE2, which is baseline on x86-64, so no -march flag is required.
- When you want a Swiss table you can read end to end and vendor: one 535-line header, MIT, standard library only.

## Skip it when

- Lookup-dominated workloads: phmap::flat_hash_map, vendored in the same repo because of this result, is 1.29x faster on hits and 1.39x faster on misses (VENDORING.md recorded 1.21x/1.55x in another run). It is also far more mature.
- Code that needs stable references or pointers to elements across inserts, or non-movable mapped types (e.g. std::mutex). Use std::unordered_map or a node-based map.
- Small, cache-resident tables and non-x86 targets. In CI smoke runs, which the repo says are not reliable for timing, 1,000-key hit lookups on x86 roughly tied libstdc++ (3.6 vs 3.7-4.2 ns). On macOS arm64 (SWAR path, libc++), std::unordered_map was about 2x faster on 1,000-key lookups and roughly even on 1M-key hits. There is no NEON path.
- Untrusted or adversarial keys: the default hashes are unseeded (fixed constants, and splitmix64 is an invertible bijection), so colliding keys can be precomputed.
- Memory-tight or allocator-controlled code: there is no allocator hook, the table never shrinks on erase, and capacity rounds up to a power of two at a 7/8 maximum load. 1M uint64-&gt;uint64 entries used 35.7 bytes/entry in a table about 48% full.

## How it is fast

It is an independent implementation of Google's SwissTable design (absl::flat_hash_map). Entries live in one power-of-two slot array, so the index is a mask rather than a prime modulo, and a parallel array holds one control byte per slot: 7 bits of the hash, or an empty/deleted tag. A 16-slot group is filtered with one SSE2 compare+movemask, with an 8-lane SWAR fallback on other targets, so a hit is usually one control-byte load plus one key compare and a miss usually ends at the first group with an empty lane. Slots and control bytes share a single allocation instead of one node per entry. Keys are mixed with splitmix64 (integers, pointers) or a wyhash-style 64x64-&gt;128 multiply-fold (strings), because std::hash on integers is the identity in libstdc++ and libc++, which a masked table cannot use.

## Compared with alternatives

No siblings catalogued yet. Inside its own repo the rival is the vendored phmap::flat_hash_map, which wins lookups by 1.29-1.39x while this map wins only the reserve+insert build path by 1.07-1.10x; choose it for build-heavy use or when you want a small dependency-free header rather than a mature library.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the standard library, but the header includes 5 sibling fastcpp headers (core/bits.hpp, core/cpu.hpp, core/macros.hpp, hash/hash.hpp, hash/mix.hpp). The repo's fastcpp::fastcpp CMake target also links all ten vendored third-party libraries, so copying the six headers is lighter than add_subdirectory. |
| **Minimum toolchain** | C++20 for this header (&lt;bit&gt; countr_zero/countl_zero, std::is_constant_evaluated); the benchmarks were built as -std=c++20. The repo itself now builds as C++23 and lists gcc 13+, clang 17+, MSVC 19.35+. CI covers gcc and clang on Linux and Apple clang on macOS; MSVC is not tested. |
| **Platforms** | x86-64 (SSE2 group match, no AVX needed); any other target, including aarch64, uses an 8-lane portable SWAR fallback that the header says is about half the speed on a miss. Container tests passed on a macOS arm64 CI runner. |
| **Thread safety** | Not documented. There is no internal locking; find/contains only read the table, but emplace, operator[], erase and rehash need external synchronization. |
| **Drop-in for the baseline** | partial — same value_type and core method names, but no allocator parameter, at(), try_emplace, insert_or_assign, initializer-list/range construction, swap or bucket API; erase(iterator) returns void; references are not stable; and the default hasher only covers integers, enums, pointers, std::string and std::string_view. |

## Gotchas

- Growth invalidates all references, pointers and iterators. emplace() and operator[] check the growth threshold before looking for the key, so m[k] on a key that already exists can still rehash the table.
- rehash(n) doubles an undersized request only once, then reinserts with no capacity check. If size() exceeds twice max(16, next_pow2(n)), it never returns: for example rehash(0), the usual std::unordered_map shrink idiom, on any map with more than 32 entries. This comes from reading rehash/insert_unchecked; no test covers it.
- Hash is default-constructed on every call (Hash{}(key)), so stateful or seeded hasher objects are not supported. It must return a well-mixed 64-bit value: the top 7 bits become the control tag and the low bits pick the group, so a 32-bit or identity hash degrades every probe. Floats, std::pair and user types need a custom Hash or the code does not compile.
- erase(iterator) returns void, so the it = m.erase(it) loop idiom does not compile. Erased slots can stay tombstones until the next rehash, and iteration scans every control byte, so iterating a sparse or heavily-reserved table costs O(capacity).

## Caveats and trade-offs

Repo private:developer-source is PRIVATE and readable only via authenticated gh CLI, so the benchmark code is not public; per orchestrator instruction this is capped below tier A despite full compiler/flags/CPU/commit disclosure. The results file's own caveat states absolute nanoseconds vary run to run on this shared cloud VM (elsewhere in the same file the same binary measured 3.42ns and 5.24ns for an identical lookup hours apart); only within-row ratios are meaningful. Provenance: the three 1M-key rows are tagged run 2026-09-02-core, but commit 2e21aae replaced their numbers with bench_vs_libraries figures, and that run's measured_at (2026-09-02T00:00:00Z) predates its own commit. The superseded core-run figures (bench_hash_map.cpp, build with no reserve) were 5.17x build (58.366 vs 301.889ns), 1.83x hits (13.514 vs 24.745ns) and 6.36x misses (6.253 vs 39.757ns). In the string benchmark the std::unordered_map arm also looks up an existing std::string, so neither arm builds a temporary. The 2.18x therefore comes from the hash function and the flat layout, not from heterogeneous lookup as the row's note suggests. Tradeoff: references are invalidated when the table grows. Since commit 6c81a90 the benchmarks are forced to -O3, so a rebuild at HEAD does not reproduce these -O2 flags.

Open addressing invalidates pointers/references on growth, unlike node-based std::unordered_map; elements must be movable. Uses a wyhash-style hash_bytes rather than std::hash. phmap::flat_hash_map, vendored in the same repo, already beats this component's raw lookup speed by 1.29-1.39x, so this component's only remaining edge is the from-empty build path.

## Maintenance

The repo (private:developer-source) is PRIVATE, so readers need access to see the code or benchmarks. It is young: the whole repo was written 2026-09-02..04, the header is unchanged since its first commit, there are no releases and 0 stars, and every CI run is red for reasons outside the map (an xsimd matmul bench build, a UBSan hit in string/parse.hpp), though the map's differential tests pass under ASan/UBSan. It is MIT-licensed and small enough to vendor as six headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** results/fastest.json rows flat_hash_map_hit_1m, _miss_1m, _build_1m and flat_hash_map_string give exact ns against std::unordered_map (libstdc++), and the run metadata states gcc 13.3.0, flags and the Xeon CPU. The code (bench/bench_vs_libraries.cpp for the 1M rows, bench/bench_hash_map.cpp for the string row) is in a PRIVATE repo, so this cannot be A. There is no paper or independent suite for B, so these are first-party numbers: C.
- **Verifier notes:** All figures (5.52x, 2.18x, 18.911/33.687, 9.723/44.665, phmap 1.29x/1.39x, 38.07ns) match results/fastest.json and README; the derived 1.78x/4.59x are correct. Git history shows the 1M rows came from bench_vs_libraries (which reserves before building), not bench_hash_map, so I reworded the build claim, workload and compiler_and_flags and added the superseded original figures to caveats. MIT, last commit 2026-09-04, 0 stars, private: confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <private:developer-source>
  - <private:developer-source/commits/main>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/b89b9dc/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_hash_map.cpp>
  - <private:developer-source/blob/main/bench/bench_vs_libraries.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/include/fastcpp/container/flat_hash_map.hpp>
  - <private:developer-source/blob/main/third_party/parallel-hashmap/VENDORING.md>
  - <private:developer-source/commit/2e21aae>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/commits/main/bench/bench_hash_map.cpp>
  - <private:developer-source/commits/main/bench/bench_vs_libraries.cpp>
  - <private:developer-source/commits/main/results/fastest.json>
- **Sources the enricher read:**
  - <private:developer-source>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/include/fastcpp/container/flat_hash_map.hpp>
  - <private:developer-source/blob/main/include/fastcpp/hash/hash.hpp>
  - <private:developer-source/blob/main/include/fastcpp/hash/hashers.hpp>
  - <private:developer-source/blob/main/include/fastcpp/hash/mix.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/cpu.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/bits.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/macros.hpp>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_hash_map.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/bench/bench_vs_libraries.cpp>
  - <private:developer-source/blob/main/bench/bench_phf.cpp>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/bench_ordered_map.cpp>
  - <private:developer-source/blob/main/bench/CMakeLists.txt>
  - <private:developer-source/blob/main/third_party/parallel-hashmap/VENDORING.md>
  - <private:developer-source/blob/main/.github/workflows/ci.yml>
  - <private:developer-source/blob/main/tests/test_containers.cpp>
  - <private:developer-source/commits/main>
  - <private:developer-source/commits/main/include/fastcpp/container/flat_hash_map.hpp>
  - <private:developer-source/commits/main/include/fastcpp/hash/hash.hpp>
  - <private:developer-source/issues>
  - <private:developer-source/pulls>
  - <private:developer-source/releases>
  - <private:developer-source/tags>
  - <private:developer-source/actions>
  - <private:developer-source/actions/runs/33828450197>
  - <private:developer-source/actions/runs/33699193714>
  - <private:developer-source/actions/runs/33687120995>
  - <private:developer-source/actions/runs/33691577660>
  - <private:developer-source/actions/runs/33697167443>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#hash-maps-sets`) · [data/wave1-phf/enrich/raw/private_developer_source_hash_maps_sets.json](../../../data/wave1-phf/enrich/raw/private_developer_source_hash_maps_sets.json) (enrichment confidence 0.82)

</details>
