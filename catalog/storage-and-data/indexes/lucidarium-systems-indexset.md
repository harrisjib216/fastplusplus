# indexset

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust two-level B-tree (sorted Vec leaves) with positional indexing; beats std BTreeMap/BTreeSet on scans and Mutex-wrapped std under contention.

| | |
|---|---|
| **Beats** | std::collections::BTreeMap / BTreeSet (Rust) |
| **Claimed result** | Concurrent indexset (cap 256) is \~3.2x faster than a mutex-protected std::collections::BTreeMap at 50/50, 64 B, 12 threads (0.722 ms vs 2.314 ms), and \~3.5x faster than a mutex-protected BTreeSet for the set (0.728 ms vs 2.545 ms) (derived from page data). Single-threaded full traversal is \~2.5x faster for the 8 B set (37.3 us vs 92.5 us, cap 1024) and 1.5-1.8x for the other set/map traversals (derived from page data). Inserts are 1.08-1.17x faster at cap 256 for the u64 set and the 16 B/64 B map entries, but std wins 64 B set inserts. Map update-existing is 1.17-1.53x faster (derived from page data). std BTreeMap/BTreeSet wins single-threaded get, contains and remove (remove \~1.9-2.6x faster in std). |
| **Workload** | Single-threaded insert/contains/remove/get/update/get_index/full-traversal/128-entry range traversal over 100,000 existing entries (8 B or 64 B set values; 16 B or 64 B map entries). Concurrent runs do 10,000 operations over 12 worker threads (90/10 and 50/50 read/write). Criterion median estimates at commit 7e3ac23, measured 2026-08-26. |
| **Metric** | throughput |
| **Hardware** | 12-core Apple M2 Pro, 16GB RAM, macOS 26.5.2 |
| **Compiler and flags** | rustc 1.97.0-nightly (ad3a598ca 2026-05-03); cargo bench with Criterion 0.5.1; Cargo's default bench profile (opt-level=3), with no [profile] override in Cargo.toml and no .cargo/config |
| **Adoption** | 120 stars; \~196k crates.io downloads (indexset crate) |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/lucidarium-systems/indexset) · [benchmark](https://github.com/lucidarium-systems/indexset#benchmarks) |

## Verdict

The author's Criterion suite at master commit 7e3ac23 (rustc 1.97.0-nightly, default bench profile, 12-core Apple M2 Pro, macOS) measured 100k-entry trees. Against std::collections::BTreeSet/BTreeMap, full traversal was 1.5-2.5x faster and small-entry inserts and map updates were slightly faster at cap 256, but std won get/contains/remove. With 12 threads, the concurrent tree at cap 256 beat a Mutex-wrapped std tree by about 3.2x (map, 0.722 vs 2.314 ms) and about 3.5x (set, 0.728 vs 2.545 ms) at 50/50 read/write with 64-byte values. No one has reproduced this independently.

## Use it when

- Scan-heavy ordered data in Rust: full traversal of 100k entries was 1.5-2.5x faster than std, and 128-entry range scans were 1.1-1.4x faster.
- You need order statistics: the k-th element (get_index ran in about 11-13 ns at 100k), rank of a key, or slicing by position with range_idx. std BTreeMap cannot do these without an O(n) walk.
- A shared ordered set or map hit by many threads with random-position keys. At cap 256 and 12 threads the concurrent tree was about 3.2-3.5x faster than Mutex&lt;std BTree&gt; at 50/50 read/write, and about 2.8-3.2x faster at 90/10.
- Small keys and entries (u64, 16-byte map entries) inserted at random positions with node capacity near 256 (1.08-1.17x faster inserts), or maps that often overwrite existing keys (1.17-1.53x faster updates).

## Skip it when

- Workloads dominated by point lookups and deletes. std is faster on contains/get (map get 24.7 ns vs 38.7-46.5 ns) and on remove (1.9-2.6x faster at cap 256, about 5-6x faster for 64-byte records at cap 1024), because a remove shifts up to B elements.
- Large sets filled in descending or low-locality order. In issue #39, 100M reverse-order inserts took 34-61 s vs about 2 s for std, and the author agreed the flat design is less general than a normal B+tree.
- Code that calls range() with bounds that are absent from the collection. Open issue #56 (still in master's source) returns elements outside the range and drops elements inside it, and the concurrent BTreeMultiMap has an open wrong-keys-in-range bug (#68).
- 64-byte records at the default node capacity of 1024. Inserts are 1.9-2.5x slower than std, and the concurrent set at 50/50 (4.0 ms) loses to a plain Mutex&lt;std::BTreeSet&gt; (2.5 ms).
- You need serde or order statistics on the concurrent types (neither is supported), or evidence against real concurrent ordered maps. The only published concurrent baseline is a Mutex-wrapped std tree, and the comparison bench against congee, arctic and WorkTablesIndex has no results in the README.

## How it is fast

The tree is flat. A Vec holds sorted Vec leaves, 1024 slots each by default and set with with_maximum_node_size. A lookup is one binary search over the leaves' max elements and one unchecked binary search inside a leaf. Iteration is plain slice iteration over contiguous memory, which is why full scans are 1.5-2.5x faster. A Fenwick tree (the ftree crate) over the leaf lengths gives positional select/rank in O(log(n/B)). The concurrent variants index their leaves in a crossbeam lock-free SkipMap keyed by each leaf's max, and each leaf sits behind its own parking_lot Mutex. Ordinary operations take only a read guard on a global ShardedLock plus one leaf mutex. Splits, leaf-max changes and leaf removals take the global write lock, so threads that touch different leaves run in parallel instead of queuing on one Mutex&lt;std::BTreeMap&gt;.

## Compared with alternatives

Pick indexset when you need an in-process, in-memory ordered set/map in Rust with std-style ergonomics, positional indexing, or a simple multi-threaded replacement for Mutex&lt;BTreeMap&gt;. Bf-Tree, the other Rust sibling, is benchmarked as a storage engine against RocksDB and LeanStore. ALEX, PGM-index and the rafaelkallis ART are C++ indexes you would reach through FFI, and they are benchmarked against STX B+Tree or std::map rather than Rust's std.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ftree (always); optional: serde (serde feature); crossbeam-skiplist, crossbeam-utils, parking_lot (concurrent/cdc); fastrand (multimap) |
| **Minimum toolchain** | Not documented: no rust-version field, edition 2021 (so at least Rust 1.56). The benchmarks used rustc 1.97.0-nightly, and a migration to edition 2024 is an open PR (#62). |
| **Platforms** | Any (pure Rust, no arch-specific or SIMD code seen) |
| **Thread safety** | Single-threaded types have no interior mutability and mutate through &mut. The concurrent types are shared via &self: a crossbeam SkipMap indexes the leaves, each leaf has a parking_lot Mutex, and a global ShardedLock is write-locked for structural changes. Reads also lock the leaf mutex exclusively. |
| **Drop-in for the baseline** | partial — the single-threaded BTreeSet/BTreeMap mirror most of the std API and add get_index/rank. However, range() gives wrong results for absent bounds (#56). The concurrent types have a different, narrower API (&self methods, Ref guards, T: Clone + Debug + Send, no serde, no order statistics). |

## Gotchas

- The default node capacity is 1024, but most headline wins were measured at 256. At 1024, 64-byte inserts, removes and concurrent 50/50 runs lose badly to std, so call with_maximum_node_size and tune it for your record size and n.
- crates.io 0.16.0 (2026-04-14) is behind master: master's Cargo.toml still says 0.15.0 and the changelog lists the fixes as Unreleased. That release lacks the fix for the node-split panic at small node sizes (#57), the fix for replacing a key during a concurrent split, and the fix for immediate UB from an uninitialized sentinel in BTreeMultiMap::get (#55). The benchmarks ran on unreleased master (7e3ac23).
- From reading src/lib.rs: BTreeSet::get returns the element at the lower-bound position with no equality check, so a missing key that falls between two stored keys appears to return the next larger element. This is the same bug shape as the since-fixed BTreeMap::get/get_mut bugs (#25, #47), so prefer contains() plus a check.
- Concurrent internals, from reading src/concurrent/set.rs: get() returns a Ref that holds the leaf's exclusive mutex (up to B elements), blocking every other thread on that leaf while you hold it. Iterators extend slice lifetimes with unsafe transmute and drop the leaf guard when they move to the next leaf. Each leaf-to-leaf step rescans the skip list from the front, so a full concurrent iteration is quadratic in leaf count. len() locks every leaf. Inserts past the current maximum (monotonic keys) take the global write lock every time.

## Known shortcomings

- Inserts are only 1.08-1.17x faster (1.5x holds only for map updates); mixed single-thread results; license stated only in Cargo.toml.
- The headline wins need node capacity 256; at the default 1024, 64 B inserts/removes lose to std and concurrent 50/50 loses to Mutex&lt;std&gt; (4.0 vs 2.5 ms). Correctness bugs: range() wrong on absent bounds (#56), multimap range bug (#68), set get() skips the equality check (from source). 100M reverse-order inserts take 34-61 s vs std \~2 s (#39). crates.io 0.16.0 lacks the split-panic (#57) and UB (#55) fixes; the bench ran unreleased commit 7e3ac23. Concurrent iteration uses unsafe transmute and rescans per leaf (quadratic); monotonic inserts take a global write lock; only a Mutex-wrapped std baseline.

## Caveats and trade-offs

Single-vendor benchmark (the author's own Criterion suite on one machine); no independent reproduction. The concurrent baseline is a mutex-wrapped std BTreeMap/BTreeSet, a weak incumbent because std has no concurrent ordered map. std still wins single-threaded get/contains/remove. The license is declared only in Cargo.toml ('Apache-2.0 OR MIT'); the repo has no LICENSE files and GitHub reports no license.

Results are mixed rather than a uniform win: std::BTreeMap/BTreeSet is still faster for plain get/remove/contains, especially on larger 64-byte records; indexset wins full traversal, range scans, inserts, and concurrent-contention scenarios. Dense concurrent multimap workloads currently excluded pending an open issue.

## Maintenance

Actively maintained: master's last commit is 2026-08-27, and correctness fixes and a benchmark rework landed in July-August 2026. The newest crates.io release (0.16.0, April 2026, about 196k total downloads) predates those fixes, several range/multimap bugs are still open, and the Apache-2.0 OR MIT license is declared only in Cargo.toml with no LICENSE file in the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks section compares against std::collections::BTreeSet/BTreeMap (single-threaded) and against mutex-protected std trees (12 threads), using public Criterion code: benches/single_threaded.rs with single_threaded/set.rs and map.rs, and benches/concurrent.rs with concurrent/set.rs and map.rs (MutexStdBTreeSet/MutexStdBTreeMap). It states rustc 1.97.0-nightly (ad3a598ca 2026-05-03), the Apple M2 Pro, commit 7e3ac23 (verified) and the exact cargo bench commands. The flags are Cargo's default bench profile, because Cargo.toml has no [profile] override and the repo has no .cargo/config. That meets A under the hashify/simdutf8 precedent.
- **Verifier notes:** The record swapped the set's 0.728 ms into the map comparison; the map's figure is 0.722 ms. Its insert range '1.08-1.5x' overstated the inserts (1.08-1.17x); 1.5x only appears for map update-existing. The master branch's last commit is 2026-08-27; the 2026-09-09 pushed_at comes from an unreviewed 'rescue/worktree-20260909' branch.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `last_commit`, `stars_or_usage`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lucidarium-systems/indexset>
  - <https://github.com/lucidarium-systems/indexset#benchmarks>
  - <https://github.com/lucidarium-systems/indexset/blob/master/Cargo.toml>
  - <https://github.com/lucidarium-systems/indexset/tree/master/benches>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/concurrent.rs>
  - <https://github.com/lucidarium-systems/indexset/commit/7e3ac23>
  - <https://crates.io/api/v1/crates/indexset>
- **Sources the enricher read:**
  - <https://github.com/lucidarium-systems/indexset>
  - <https://github.com/lucidarium-systems/indexset#benchmarks>
  - <https://github.com/lucidarium-systems/indexset/blob/master/README.md>
  - <https://github.com/lucidarium-systems/indexset/blob/master/Cargo.toml>
  - <https://github.com/lucidarium-systems/indexset/blob/master/CHANGELOG.md>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/lib.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/core/node.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/core/constants.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/concurrent/set.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/concurrent/map.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/concurrent/ref.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/src/concurrent/operation.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/single_threaded.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/single_threaded/set.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/concurrent.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/concurrent/set.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/concurrent/workload.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/comparison.rs>
  - <https://github.com/lucidarium-systems/indexset/blob/master/benches/comparison/map.rs>
  - <https://github.com/lucidarium-systems/indexset/issues?q=is%3Aissue>
  - <https://github.com/lucidarium-systems/indexset/pulls?q=is%3Apr>
  - <https://github.com/lucidarium-systems/indexset/issues/1>
  - <https://github.com/lucidarium-systems/indexset/issues/25>
  - <https://github.com/lucidarium-systems/indexset/issues/39>
  - <https://github.com/lucidarium-systems/indexset/issues/47>
  - <https://github.com/lucidarium-systems/indexset/issues/55>
  - <https://github.com/lucidarium-systems/indexset/issues/56>
  - <https://github.com/lucidarium-systems/indexset/issues/57>
  - <https://github.com/lucidarium-systems/indexset/issues/68>
  - <https://github.com/lucidarium-systems/indexset/commit/7dd94a0>
  - <https://crates.io/api/v1/crates/indexset>
  - <https://crates.io/api/v1/crates/indexset/0.16.0>
  - <https://crates.io/api/v1/crates/indexset/reverse_dependencies>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/lucidarium-systems/indexset`) · [data/wave6/enrich/raw/github_com_lucidarium_systems_indexset.json](../../../data/wave6/enrich/raw/github_com_lucidarium_systems_indexset.json) (enrichment confidence 0.75)

</details>
