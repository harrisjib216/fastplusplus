# zmph (Zig Minimal Perfect Hash Map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Zig` · `no license` · 🟢 active

> Pure-Zig minimal perfect hash map for fixed string key sets; about 1.7x faster average lookups than std.StringHashMap.

| | |
|---|---|
| **Beats** | Zig std.StringHashMap and std.StaticStringMap |
| **Claimed result** | Lookup (zBench average of single-call runs): zmph 26ns ± 4ns vs std.StringHashMap 45ns ± 152ns (README: StringHashMap is \~1.7x slower than zmph) and vs std.StaticStringMap 10.4us ± 7.359us (README: \~400x slower, which the README attributes to binary search). Build: zmph 28.872ms vs StringHashMap 6.1ms (\~5x slower to build) and StaticStringMap 2.029ms (\~14x slower to build). |
| **Workload** | A PerfectHashMap built at runtime (PerfectHashMap.init with an allocator, not the comptimeInit path) over the words in the host's /usr/share/dict/words (word count not stated), compared with Zig std.StringHashMap and std.StaticStringMap, both also built at runtime. zBench runs 100,000 lookups per structure and times each run individually. The build (construction) time of each structure is also measured. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-8750H @ 2.20GHz, Linux Debian |
| **Compiler and flags** | Zig 0.15.1; zig build benchmark --release=fast (ReleaseFast optimize mode) |
| **Adoption** | 8 stars |
| **Last commit** | 2026-01-31 |
| **Links** | [repository](https://github.com/PaNDa2code/zmph) · [benchmark](https://github.com/PaNDa2code/zmph/blob/master/README.md) |

## Verdict

The author's own zBench run (Zig 0.15.1, ReleaseFast, Core i7-8750H, Debian) built each map at runtime from /usr/share/dict/words and timed 100,000 single lookups, all hits, one timer per call: zmph averaged 26 ns (min 18, p99 38), std.StringHashMap 45 ns (min 22, p99 106), and std.StaticStringMap 10.4 us, because its lookup is a linear scan over keys of equal length. Build times were 28.9 ms, 6.1 ms and 2.0 ms. Timer overhead is included in every figure and the comptimeInit path was never measured, so the \~1.7x is an average of wall-clock samples, not an exact ratio of lookup costs.

## Use it when

- Zig code with a fixed string key set (a word list, command names, identifiers) that is built rarely and read very often. From the README averages, the extra \~23 ms of build time versus StringHashMap on a dictionary is paid back after roughly 1.2M lookups per build (derived: 22.8 ms / 19 ns).
- Read paths where tail latency matters on a large set: the README reports p99 38 ns vs 106 ns and max 96 ns vs 29.8 us against StringHashMap (all hits, dictionary-sized key set).
- Dictionary-sized string sets where you would otherwise use std.StaticStringMap. That map scans every key of the same length, which is why it is \~400x slower in this benchmark.
- Small key sets known at compile time, such as a tokenizer's keyword table (see examples/parser.zig). `comptimeInit` puts the table in the binary with no runtime build and no allocator. Note that this path is not benchmarked.

## Skip it when

- Maps that change after they are built. There is no put, remove or iteration, so any change means a full rebuild. `init` is documented as O(N^2), and the build took 28.9 ms vs 6.1 ms for StringHashMap on the same word list.
- Lookups where many keys are absent, on a map built with `init()` at runtime. See gotchas: from my reading of the source, a miss that lands on an empty bucket is illegal behavior. The benchmark and the tests only look up keys that are present.
- Non-string keys. K is generic, but getIndex compares with `std.mem.eql(u8, ...)`, so in practice only `[]const u8` keys compile.
- Small keyword sets where StaticStringMap is the incumbent. Nothing in the repo measures that size, which is the size StaticStringMap is designed for ('optimized for small sets of disparate string keys').
- Anything you need to ship or modify. There is no LICENSE file, it has 8 stars, and no CI run has ever been recorded (the test workflow only runs when triggered by hand).

## How it is fast

It uses hash-and-displace minimal perfect hashing, as in Steve Hanov's 'Throw away the keys' post (which cites CHD by Belazzougui, Botelho and Dietzfelbinger), and this is what the README links to. Keys are grouped into n buckets by Murmur3_32 with seed 0. Buckets are placed largest first by trying seeds d = 1, 2, ... until every key in the bucket lands in a free slot, and single-key buckets go straight into the leftover slots, stored as -slot-1. A lookup reads one displacement entry, computes a second Murmur3_32 only for keys from multi-key buckets, and does one key comparison, with no probing and no empty slots; std.StringHashMap is open addressing with linear probing (Wyhash, 80% max load), so its lookups can probe several slots.

## Compared with alternatives

It is the only Zig entry in this category, so choose it when you write Zig and want faster reads than StringHashMap on a large fixed string set. In C++ (frozen, qlibs mph, constexpr-phf), Rust (rust-phf, QuickPHF) or Go (constmap), use those siblings instead, and since zmph has no license, treat it as a reference for writing your own hash-and-displace table.

## Integration

| | |
|---|---|
| **Form** | module (a single-file Zig package, src/minimal_perfect_hash.zig, added with `zig fetch --save`) |
| **Dependencies** | none in the library (std only); build.zig.zon declares zBench as a non-lazy dependency for the benchmark step, so it gets fetched as well |
| **Minimum toolchain** | Zig 0.15.1, the stated and targeted version. The code uses the 0.15 std.ArrayList API that takes an allocator on each call, so older Zig will not compile it; newer Zig is not documented. |
| **Platforms** | any Zig target in principle (pure Zig, with no SIMD or architecture-specific code); only benchmarked on x86-64 Linux |
| **Thread safety** | Not documented. The map cannot be changed after it is built, and get/getIndex/has take \*const Self and only read, so from the source, concurrent readers look safe. |
| **Drop-in for the baseline** | partial — it covers read-only get/has, but it needs the full key list when built, has no put/remove/iterator, and its init argument order is (allocator, kv_list), not StaticStringMap.init(kv_list, allocator) |

## Gotchas

- On a map built with `init()`, empty buckets keep displacement maxInt(isize). getIndex then @intCasts that value to a u32 hash seed. The Zig 0.15.1 langref calls this safety-checked illegal behavior: a panic in Debug/ReleaseSafe, anything can happen in ReleaseFast. So misses can crash a map built this way. `comptimeInit` fills empty slots with 0 and avoids the problem.
- Duplicate keys are not detected. Two equal keys always hash to the same slot, so the seed search never succeeds. Keys are stored as borrowed slices, so the key bytes must outlive the map. Do not call `deinit` on a `comptimeInit` map, because its allocator field is left undefined.
- `comptimeInit` builds n buckets that each hold an n-slot fixed array and sets an n^2 eval branch quota, so compile-time memory and work grow quadratically. It suits keyword-sized tables, not dictionaries. It also failed to compile from the Aug 2025 port to Zig 0.15.1 until the v0.2.1 fix on 2026-01-31.
- build.zig.zon pins zBench by hash to a branch archive (refs/heads/zig-0.15.1). That branch changed zbench.zig in Dec 2025, after the pin, so a fresh fetch will likely fail the hash check, and because the dependency is not lazy, projects that depend on zmph may hit this too. examples/build.zig still passes the pre-0.15 addExecutable fields (root_source_file/target/optimize), which Zig 0.15.1 removed.

## Caveats and trade-offs

The repo has no LICENSE file (GitHub license is null), so it is reference-only. The benchmark is first-party and was run on one machine. Each zBench run wraps a single lookup (an indirect call) in std.time.Timer start/read, so fixed timer overhead is part of both the 26 ns and the 45 ns figures, and the true lookup-cost ratio is uncertain. StringHashMap's σ is 152 ns (max 29.795 us). The \~400x StaticStringMap gap is not a fair comparison: in Zig 0.15.1, StaticStringMap.getIndex scans all keys of the same length linearly (it does not do a binary search, as the README says), and it is designed for small keyword sets, not a large dictionary. The benchmark measures runtime init, not the compile-time comptimeInit path that the README headlines. The results have not been reproduced independently.

Much slower to build (compile-time construction cost) than the stdlib alternatives; only worthwhile when lookups vastly outnumber (re)builds. Requires Zig comptime and a fixed, known-at-build key set.

## Maintenance

Active but small: v0.2.1 was released 2026-01-31, it has one author and 8 stars, and no issues or CI runs have ever been recorded. With no LICENSE file it is reference-only, so read it to learn the technique rather than vendoring it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (src/benchmark.zig, run through the build.zig `benchmark` step with zBench). The README states the compiler (Zig 0.15.1), the flags (`zig build benchmark --release=fast`, i.e. ReleaseFast) and the CPU (Intel Core i7-8750H), so all A criteria are met.
- **Verifier notes:** The numbers match the README exactly, and tier A holds. For the catalog, the headline should be the \~1.7x win over std.StringHashMap. The 400x win over StaticStringMap comes from using a linear-scan structure on a dictionary-sized key set (checked in the Zig 0.15.1 static_string_map.zig source). The record left out the Zig version and wrongly called the benchmarked map 'comptime-built'; both are fixed. Metadata is correct: no license, 8 stars, last commit 2026-01-31, active, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PaNDa2code/zmph>
  - <https://github.com/PaNDa2code/zmph/blob/master/README.md>
  - <https://github.com/PaNDa2code/zmph/blob/master/src/benchmark.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/src/minimal_perfect_hash.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/build.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/build.zig.zon>
  - <https://github.com/PaNDa2code/zmph/commits/master>
  - <https://github.com/ziglang/zig/blob/0.15.1/lib/std/static_string_map.zig>
  - <https://github.com/hendriknielaender/zBench/blob/zig-0.15.1/zbench.zig>
- **Sources the enricher read:**
  - <https://github.com/PaNDa2code/zmph>
  - <https://github.com/PaNDa2code/zmph/blob/master/README.md>
  - <https://github.com/PaNDa2code/zmph/blob/master/src/minimal_perfect_hash.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/src/benchmark.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/build.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/build.zig.zon>
  - <https://github.com/PaNDa2code/zmph/blob/master/.github/workflows/test.yml>
  - <https://github.com/PaNDa2code/zmph/blob/master/examples/build.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/examples/comptime_hashmap.zig>
  - <https://github.com/PaNDa2code/zmph/blob/master/examples/parser.zig>
  - <https://github.com/PaNDa2code/zmph/commits/master>
  - <https://github.com/PaNDa2code/zmph/commit/7131e4e>
  - <https://github.com/PaNDa2code/zmph/commit/1a4807f>
  - <https://github.com/PaNDa2code/zmph/commit/89dddc8>
  - <https://github.com/PaNDa2code/zmph/issues?q=is%3Aissue>
  - <https://github.com/PaNDa2code/zmph/releases>
  - <https://github.com/PaNDa2code/zmph/actions>
  - <https://github.com/ziglang/zig/blob/0.15.1/lib/std/static_string_map.zig>
  - <https://github.com/ziglang/zig/blob/0.15.1/lib/std/hash_map.zig>
  - <https://github.com/ziglang/zig/blob/0.15.1/lib/std/hash/murmur.zig>
  - <https://github.com/ziglang/zig/blob/0.15.1/lib/std/Build.zig>
  - <https://github.com/ziglang/zig/blob/0.15.1/doc/langref.html.in>
  - <https://github.com/hendriknielaender/zBench/blob/zig-0.15.1/zbench.zig>
  - <https://github.com/hendriknielaender/zBench/blob/zig-0.15.1/build.zig.zon>
  - <https://github.com/hendriknielaender/zBench/commits/zig-0.15.1>
  - <https://github.com/hendriknielaender/zBench/commit/b95f294>
  - <https://stevehanov.ca/blog/?id=119>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/panda2code/zmph`) · [data/wave1-phf/enrich/raw/github_com_panda2code_zmph.json](../../../data/wave1-phf/enrich/raw/github_com_panda2code_zmph.json) (enrichment confidence 0.82)

</details>
