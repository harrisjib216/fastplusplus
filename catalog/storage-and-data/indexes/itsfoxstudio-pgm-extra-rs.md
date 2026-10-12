# PGM Extra (pgm-extra-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust PGM learned index with BTreeSet/BTreeMap-style Set and Map; beats BTreeSet on u64 lookups, loses to binary search.

| | |
|---|---|
| **Beats** | std::collections::BTreeSet / BTreeMap (Rust) |
| **Claimed result** | PGM (eps=256) 1.7x faster point queries than BTreeSet (489.5us vs 851.6us), 3.2x smaller memory (7.7MB vs 25.0MB), range-scan 1.4x faster (verbatim from README benchmark tables) |
| **Workload** | Point-query and range-query benchmark over 1M random u64 keys (10K queries), comparing PGM-index variants (epsilon=16/64/256) against Rust's BTreeSet/BTreeMap and HashMap on an Apple M1 Pro |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro |
| **Compiler and flags** | rustc (version not stated); Cargo [profile.bench] lto=true, codegen-units=1 (opt-level=3 inherited from [profile.release]); Criterion harness benches/pgm_bench.rs |
| **Adoption** | 107 stars; crates.io: pgm-extra (v1.3.0, 536 downloads) |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/itsfoxstudio/pgm-extra-rs) · [benchmark](https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/README.md) |

## Verdict

In the author's Criterion benchmark on an Apple M1 Pro (rustc version not stated; bench profile LTO with codegen-units=1), 10K lookups (half hits) against 1M uniformly random u64 keys took 489.5 us with Static::lower_bound at epsilon 256 versus 851.6 us with std BTreeSet::contains (1.7x). Find-then-scan-100 range queries took 120.5 us versus 174.3 us with BTreeSet::range (1.4x). The same table shows slice binary search (266.8 us) and HashMap (68.2 us) beating PGM, and the 7.7 MB vs 25.0 MB memory figures count construction-time allocations, not resident size.

## Use it when

- Read-mostly sets or maps with up to millions of unique u64/i64 (or narrower integer) keys, built once from sorted data and then queried many times, where you would otherwise reach for BTreeSet/BTreeMap.
- Ordered queries a HashMap cannot serve (lower_bound, range, find-then-scan). There the README measured 1.3-1.7x faster point lookups and 1.4x faster 100-element range scans than BTreeSet at 1M keys.
- Memory-sensitive keyed data: the retained model is a small fraction of a byte per key on top of the sorted Vec, so storage is close to that of the raw sorted array.
- You already keep keys in a sorted Vec or memory-mapped slice and want an index that stores only segments (Static/OneLevel), persistable with serde or zero-copy rkyv, including no_std + alloc builds (CI checks --no-default-features).

## Skip it when

- Exact-match or even plain ordered lookups on a static sorted array. In the README's own table, HashMap (68.2 us) and binary search on the sorted Vec (266.8 us) both beat the best PGM variant (489.5 us) on 10K queries over 1M keys. That contradicts the README's 'speedup of 2-4x over binary search' line, and a sorted Vec with partition_point already gets most of the memory win.
- String or byte keys where many keys share their first 8 bytes (URLs, 'user_000...' IDs). All such keys map to the same numeric key, and the segment builder accepts equal keys without checking the error bound. A line-by-line Python port of the v1.3.0 build/search/Set::get code, run this session, returned 9,934 false negatives out of 10,000 lookups on 'https://example.com/itemNNNNN'.
- Dense integer keys above 2^53, such as consecutive nanosecond timestamps near 1.7e18. Keys are converted to f64, so neighbours collapse to the same value, and the same port broke the epsilon bound: 23,853 of 100,000 lookups missed. Random full-range u64 keys and small integers came out correct.
- Write-heavy or mixed workloads. Set::insert and Map::insert re-sort and rebuild the whole index on every call, and Dynamic::range filters the entire base Vec linearly instead of using the index.
- Where maturity matters: single author, 536 total crates.io downloads, zero reverse dependencies, and no issues or PRs ever filed. The property tests cover only deduplicated u64 keys below 1,000,000, with no strings, large keys or duplicates.

## How it is fast

Each bottom-level segment is a linear model (first key, slope, intercept) that predicts a key's position to within ±epsilon. Upper levels index the segment start keys recursively with epsilon_recursive (default 4), so a lookup is a few multiply-adds plus a search over about 2·epsilon+2 array slots, not a pointer walk through B-tree nodes. Segments come from a greedy shrinking-cone pass (a feasible-slope interval anchored at each segment's first key), not from the optimal convex-hull PLA (OptimalPiecewiseLinearModel) that the reference C++ PGM-index uses, so it can produce more segments for the same epsilon. The code is safe Rust with no hand-written SIMD; the `simd` feature is declared in Cargo.toml, but nothing in src/ checks it.

## Compared with alternatives

Pick it over the reference C++ PGM-index or PGM++ only when you need a pure-Rust, no_std-capable crate with serde/rkyv and BTreeSet-shaped wrappers, and can accept non-optimal segmentation and much thinner testing. Over indexset, pick it for read-mostly integer keys where memory matters; pick indexset for concurrent or frequent writes.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits (with libm); optional rayon (parallel feature), serde, rkyv 0.8 |
| **Minimum toolchain** | Rust edition 2024, so rustc 1.85+; no rust-version field is declared and CI tests only stable |
| **Platforms** | any: safe Rust with no architecture-specific code, and no_std + alloc supported (Dynamic needs std). CI runs only on ubuntu-latest, and published benchmarks exist only for an Apple M1 Pro. |
| **Thread safety** | By inspection, Static, OneLevel, Set, Map and Dynamic hold plain Vec/BTreeSet data with no interior mutability, so they are Send + Sync for shared reads, and mutation needs &mut. Cached keeps a Cell-based hot-key cache and is documented as !Sync. There is no concurrent-writer support. |
| **Drop-in for the baseline** | partial — Set/Map copy the common BTreeSet/BTreeMap read API (contains, get, range, iter, first/last, set operations, Index), but only for Indexable keys: integers up to 64-bit (no u128/i128, despite 'all integer types' in the README) and str/String/bytes. They have no remove, entry, retain or pop_\* methods, every insert rebuilds in O(n), and duplicate-key resolution differs (see gotchas). |

## Gotchas

- Map::build, FromIterator and Extend do a stable sort and then Vec::dedup_by, which keeps the first of equal keys. A duplicate key therefore keeps its earliest value, and extend() does not overwrite an existing key, even though the doc comments say 'last value wins (like BTreeMap::from_iter)'. No test covers duplicates. Map::insert does overwrite correctly.
- Dynamic::insert does not check the base data, and force_rebuild does not dedup. Inserting a key that is already indexed gives an inflated len() and a duplicated element after the next rebuild.
- Construction errors are swallowed. FromIterator/Extend fall back to an empty collection, and Set::insert on a set created with epsilon 0 returns true without storing anything.
- The published numbers are not measurements of the Set/Map wrappers. The benchmarks call Static::lower_bound on a Vec, while Set/Map get() scans the ±epsilon window linearly and is not benchmarked. The memory table uses stats_alloc bytes_allocated, which is cumulative bytes requested during construction. The PGM figure is mostly Static::new's temporary copy of the keys, and the BTreeSet figure includes from_iter's temporary Vec and sort, so it does not measure resident size.

## Known shortcomings

- In its own table binary search and HashMap beat PGM for lookups; rustc version unstated.
- NOT FASTER THAN BINARY SEARCH in its own README (266.8 vs 489.5 us for binary search; HashMap also wins), so the '2-4x over binary search' claim is wrong. Correctness bugs: strings sharing an 8-byte prefix give wrong answers (a port of v1.3.0 gave 9,934/10k false negatives on URLs) and dense u64 above 2^53 collapse in f64 (23,853/100k misses). The memory table counts total bytes allocated during build, not resident size.
- Map::build/extend keeps the first value on duplicate keys (docs and BTreeMap keep the last); Dynamic::insert can duplicate keys; Set/Map have no remove and each insert is an O(n) rebuild; the 'simd' feature does nothing; greedy shrinking-cone segments rather than optimal PLA. Code frozen since v1.3.0 (2025-12); 536 downloads, 0 reverse deps.

## Caveats and trade-offs

First-party Criterion micro-benchmark on a single machine (Apple M1 Pro) with no rustc version stated, not independently reproduced. The point-query workload is 10K queries at a 50% hit ratio over 1M random u64 keys. In the same table, a plain binary search over the sorted Vec (266.8 us) and HashMap (68.2 us) both beat every PGM variant (489.5 us at best), so the win is specific to BTreeSet/BTreeMap and to memory footprint. This is a from-scratch Rust reimplementation of the PGM-index idea, not a fork of the canonical gvinciguerra/PGM-index (already catalogued).

PGM must rebuild segments on mutation, so it favors read-mostly workloads; main claimed win is 2.7-3.2x smaller memory footprint alongside 1.3-1.7x faster point lookups than BTreeSet/BTreeMap.

## Maintenance

The metadata says active, but the last functional release is v1.3.0 (2025-12-29, rkyv support), with only CI and README commits since (latest 2026-07-28). It is MIT-licensed, safe Rust and small (about 4.8K lines under src/, including inline unit tests), so it is easy to vendor and patch, but there is no issue history to show how responsive the single maintainer is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark Results tables match the record: 489.5 vs 851.6 us (1.7x) on point queries, 7.7 vs 25.0 MB memory, and 120.5 vs 174.3 us on range scans against BTreeSet. The Criterion harness is public (benches/pgm_bench.rs) and Cargo.toml sets [profile.bench] lto=true, codegen-units=1, with opt-level=3 inherited from release. The CPU is named (Apple M1 Pro), but no rustc version is given, so under the convention earlier batches used for Rust this is first-party C, not A.
- **Verifier notes:** Metadata checks out: MIT, not a fork, not archived, 107 stars, last commit 2026-07-28. The default branch is main, so blob/master only redirects and the URL was changed to main. Worth noting when enriching: the README's own table shows binary search on a sorted array beating PGM at this size.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/itsfoxstudio/pgm-extra-rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/master/README.md>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/benches/pgm_bench.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/Cargo.toml>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/justfile>
  - <https://crates.io/api/v1/crates/pgm-extra>
- **Sources the enricher read:**
  - <https://github.com/itsfoxstudio/pgm-extra-rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/README.md>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/Cargo.toml>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/justfile>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/.github/workflows/ci.yml>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/lib.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/error.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/mod.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/key.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/segment.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/model.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/builder.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/external/static.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/external/one_level.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/external/cached.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/index/owned/dynamic.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/collections/set.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/collections/map.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/util/bytes.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/util/search.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/src/util/cache.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/benches/pgm_bench.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/blob/main/tests/proptest_index.rs>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/issues>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/commits/main>
  - <https://github.com/itsfoxstudio/pgm-extra-rs/releases>
  - <https://crates.io/api/v1/crates/pgm-extra>
  - <https://crates.io/api/v1/crates/pgm-extra/reverse_dependencies>
  - <https://docs.rs/crate/pgm-extra/1.3.0>
  - <https://hn.algolia.com/api/v1/search?query=pgm-extra&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=itsfoxstudio>
  - <https://raw.githubusercontent.com/gvinciguerra/PGM-index/master/README.md>
  - <https://raw.githubusercontent.com/gvinciguerra/PGM-index/master/include/pgm/piecewise_linear_model.hpp>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/alloc/src/vec/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/alloc/src/collections/btree/set.rs>
  - <https://raw.githubusercontent.com/neoeinstein/stats_alloc/master/src/lib.rs>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/itsfoxstudio/pgm-extra-rs`) · [data/wave6/enrich/raw/github_com_itsfoxstudio_pgm_extra_rs.json](../../../data/wave6/enrich/raw/github_com_itsfoxstudio_pgm_extra_rs.json) (enrichment confidence 0.8)

</details>
