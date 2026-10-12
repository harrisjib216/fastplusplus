# quick-cache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Sharded concurrent Rust cache with S3-FIFO/CLOCK-Pro-style eviction; beats Mutex-guarded LRU mainly on hit ratio and thread scaling.

| | |
|---|---|
| **Beats** | LRU+Mutex (hashlink crate LruCache + std::sync::Mutex) |
| **Claimed result** | Trace 1 (ARC S3), capacity 100000: QuickCache 12.841% hit ratio in 2.196 s (1 client), 1.279 s (3 clients) and 0.798 s (6 clients), vs LRU+Mutex 2.327% hit ratio in 2.422 s (1 client only). That is about 5.5x the hit ratio and about 1.1x faster single-client wall time (derived from page data), not \~3x. Single-client wall time is mixed across the page: LRU+Mutex is faster at Trace 1 capacity 800000 (2.613 vs 3.207 s), Trace 2 (DS1) capacity 1000000 (8.901 vs 9.883 s) and Trace 3 (SPC1) capacity 2000000 (10.768 vs 14.611 s). The wall-time advantage comes from QuickCache's multi-client scaling, and LRU+Mutex was never run with more than one client. |
| **Workload** | mokabench (moka-rs/mokabench, third-party Rust cache benchmark harness) replaying the ARC-paper traces S3 (Trace 1), DS1 (Trace 2) and SPC1 (Trace 3) against QuickCache, LRU+Mutex (hashlink + std Mutex), TinyUFO and Mini Moka, at 1/3/6 clients (SPC1 1 client only) and three capacities per trace, on x64 Linux with an Intel i9-12900H CPU. |
| **Metric** | throughput |
| **Hardware** | x64 Linux, Intel i9-12900H CPU |
| **Compiler and flags** | rustc version not stated; mokabench README builds with `cargo build --release` (feature flags such as -F quick_cache,hashlink), exact invocation for the README tables not given. |
| **Adoption** | 362 stars; published on crates.io as quick_cache |
| **Last commit** | 2026-06-26 |
| **Links** | [repository](https://github.com/arthurprs/quick-cache) · [benchmark](https://github.com/arthurprs/quick-cache#benchmarks) |

## Verdict

The author ran mokabench (the Moka project's ARC-trace replay harness; both caches used an xxh3 hasher) on x64 Linux with an i9-12900H; rustc version and flags are not stated. On the ARC S3 trace at 100k capacity, QuickCache hit 12.84% in 2.196 s with one client, vs 2.33% in 2.422 s for hashlink LruCache behind a Mutex: about 1.1x faster and 5.5x the hit ratio. Across all traces the hit-ratio gain was 1.2-5.5x (equal at SPC1 30M), but LRU+Mutex was only ever run with one client and was faster in 3 of 9 configurations. Also, the README says LRU+Mutex used std::sync::Mutex, but mokabench's hashlink driver actually uses parking_lot::Mutex.

## Use it when

- Rust services where many threads share one cache on a hot path: in the README's mokabench runs on the ARC S3 trace at 100k capacity, QuickCache took 2.196 s with 1 client, 1.279 s with 3 and 0.798 s with 6.
- Traces with scans or one-hit wonders (storage block traces, buffer caches) where LRU hit ratio collapses: on ARC S3 at 100k entries QuickCache hit 12.8% vs 2.3% for LRU+Mutex, and on DS1 at 1M entries 14.9% vs 3.1%.
- Caches sized in bytes rather than item count, using a `Weighter` such as value length. Zero-weight items are kept apart from eviction and never evicted.
- Loaders that must compute each missing value only once (thundering-herd protection), sync or async, via `get_or_insert_with` / `get_or_insert_async` / `get_value_or_guard_async`.
- When you want a small dependency tree and no background threads. The README contrasts it with Moka, which has more features.

## Skip it when

- You need TTL/TTI expiry or time-based invalidation: the README says these are partially or not implemented and points to Moka. Eviction listeners exist only as a `Lifecycle::on_evict` hook that you write yourself.
- You need strict LRU order or a guarantee that a just-replaced item stays resident: the maintainer confirms replaced entries can still be evicted (issue #50), and `insert` vs guarded insert could pick different victims before fix #95 (issue #93).
- Tiny caches, or item weights that vary widely on high-core machines: capacity is divided per shard, so an item heavier than one shard's hot budget (about 97% of capacity/shards) is rejected outright, and a shard can evict while other shards still have room (issues #26, #55, #65).
- Single-threaded speed is the goal: single-client LRU+Mutex finished faster in 3 of the 9 README configurations (S3 800k: 2.613 vs 3.207 s; DS1 1M: 8.901 vs 9.883 s; SPC1 2M: 10.768 vs 14.611 s).
- Processes that must hand memory back after shrinking: evicting or draining drops the items but does not shrink the internal tables (issue #99), and the documented footprint (K+V+21)\*(len\*1.5).next_power_of_two() includes ghost slots.

## How it is fast

The eviction policy is a modified CLOCK-Pro that the crate docs call very similar to S3-FIFO. Resident entries live in hot and cold FIFO rings (the hot target defaults to 97% of weight) and carry a small reference counter capped at 2 (the source notes CLOCK-Pro uses 1 and S3-FIFO 3). A ghost ring holds hashes of recently evicted keys (sized at 50% of estimated items by default), and a key that returns while still in it is readmitted straight to hot. This scan resistance is where the hit-ratio gains over LRU come from. A hit only does a relaxed atomic increment of that counter under a shard read lock, and skips it when the counter is already saturated, so reads never need exclusive access or list relinking the way LRU does. The sync cache is split into power-of-two shards (default 4x detected cores). Each shard is a hashbrown HashTable of indices into a linked slab, behind a parking_lot RwLock. Per-entry overhead is 21 bytes, and the cache does not allocate once the table stops growing.

## Compared with alternatives

Pick it when you are in Rust and want an in-process S3-FIFO-style cache library. The closest siblings are Caffeine (JVM, W-TinyLFU with expiry and listeners) and otter or golang-fifo (Go); the S3-FIFO and SIEVE entries are libCacheSim research prototypes, not embeddable Rust crates.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | equivalent 1.0 and hashbrown 0.17 always. Default features add foldhash 0.2 (default hasher) and parking_lot 0.12. Optional: crossbeam-utils 0.8 (`sharded-lock`) and shuttle 0.8 (testing only). |
| **Minimum toolchain** | Rust 1.85 for 0.7.0 (rust-version in Cargo.toml, checked by cargo-msrv in CI). 0.6.x declared 1.71 but in practice needed 1.80 until fix #121 (issue #118). |
| **Platforms** | Any Rust std target with no architecture-specific code. CI builds and tests on Linux, macOS and Windows. wasm32 is not documented; an older version failed on wasm32-unknown-unknown through ahash/getrandom (issue #32). |
| **Thread safety** | `sync::Cache` is meant to be shared across threads through Arc, with an RwLock per shard (parking_lot by default; crossbeam ShardedLock or std RwLock via features). Gets take a read lock and writes take a write lock. `unsync::Cache` is not thread-safe. |
| **Drop-in for the baseline** | partial — it replaces the Mutex&lt;LruCache&gt; pattern with no external lock, but the constructor (estimated items plus weight capacity), clone-on-get semantics and approximate S3-FIFO-style eviction order all differ from a strict LRU, so call sites and any ordering assumptions have to change. |

## Gotchas

- The shard count defaults to 4x detected cores, so `capacity()` is rounded and can differ between machines. Keep `estimated_items_capacity` within about 1-2 orders of magnitude of reality, or set `shards()` explicitly (the maintainer suggests 0 estimated items in tests to force 1 shard).
- `Weighter::weight` must be cheap and stable: changing a resident item's weight is documented as undefined behavior (except inside `before_evict`), and so is overflowing the weight sum in release builds.
- `Lifecycle` hooks such as `on_evict` and `is_pinned` run inside the eviction path under the shard write lock, so keep them tiny (the eviction-listener example sends to a channel). 0.7.0 broke the Lifecycle API: `RequestState` must now implement Default and is passed by &mut.
- The README says it uses 'only trivially verifiable' unsafe, but the source has about 47 unsafe sites (unreachable_unchecked, unchecked slab access, raw pointers in the placeholder waiters). CI runs Miri, cargo-fuzz and shuttle. Recent fixes include a JoinFuture race (#104), a leak when a guard was dropped without inserting (#120) and weight_capacity=1 storing nothing (#106).

## Known shortcomings

- Single-client wall time is only \~1.1x (2.196 vs 2.422 s), not \~3x, and LRU+Mutex is faster in 3 configurations; the real wins are hit ratio and concurrency. Evidence is mokabench, a small suite (10 stars).
- The win is mostly hit ratio (1.2-5.5x); the LRU+Mutex baseline was never run multi-client and actually used parking_lot::Mutex (not std as the README says); author-run with rustc/flags unstated. Per-shard capacity (default 4x cores) rejects heavy items and evicts early (#26/#55/#65); tables never shrink (#99); no TTL. Pre-1.0 (0.7.0 broke the Lifecycle API), MSRV 1.85, \~47 unsafe sites despite the 'trivially verifiable' claim (Miri/fuzz/shuttle in CI).

## Caveats and trade-offs

The numbers were run and published by the quick-cache author, using mokabench, a harness from the competing Moka project that has only 10 stars (a niche suite). The rustc version and build flags are not stated. The main consistent win over LRU+Mutex is hit ratio (roughly 1.2-5.5x at small and medium capacities, equal at SPC1 capacity 30M). Single-client wall time is mixed, and LRU+Mutex is sometimes faster. The speed advantage shows up only with concurrency, and the LRU+Mutex baseline was not run concurrently.

quick-cache omits TTL and eviction-listener features present in fuller caches like Moka, trading feature completeness for lower per-op overhead; uses S3-FIFO-style scan-resistant policy rather than strict LRU ordering.

## Maintenance

Actively maintained: v0.7.0 shipped 2026-06-27, it is MIT-licensed, and crates.io shows about 27.2M downloads and 115 reverse dependencies. It is still pre-1.0, and minor releases have broken the API (0.7.0 Lifecycle reshape).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The README Benchmarks tables come from mokabench (moka-rs/mokabench, a competitor's public harness with quick_cache and hashlink features, built with `cargo build --release`). They compare QuickCache with LRU+Mutex (hashlink + std::sync::Mutex) on the ARC S3/DS1/SPC1 traces and name the CPU (i9-12900H). No rustc version or exact flags are given, so not A. B holds only as an independent third-party suite.
- **Verifier notes:** The record's '\~3x faster wall time at 1 client' is wrong: the page gives 2.196 vs 2.422 s, about 10%. The tier stays B only if mokabench counts as a 'well-known independent suite' (lzbench/smhasher precedent). Given its 10 stars and the author running it, the orchestrator may prefer C. MIT license, 362 stars and last commit 2026-06-26 all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/arthurprs/quick-cache>
  - <https://github.com/arthurprs/quick-cache#benchmarks>
  - <https://raw.githubusercontent.com/arthurprs/quick-cache/master/README.md>
  - <https://github.com/moka-rs/mokabench>
  - <https://raw.githubusercontent.com/moka-rs/mokabench/master/Cargo.toml>
  - <https://raw.githubusercontent.com/moka-rs/mokabench/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/arthurprs/quick-cache>
  - <https://github.com/arthurprs/quick-cache#benchmarks>
  - <https://github.com/arthurprs/quick-cache/blob/master/Cargo.toml>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/lib.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/options.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/shard.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/sync.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/unsync.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/rw_lock.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/linked_slab.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/src/sync_placeholder.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/examples/eviction_listener.rs>
  - <https://github.com/arthurprs/quick-cache/blob/master/.github/workflows/ci.yml>
  - <https://github.com/arthurprs/quick-cache/issues?q=is%3Aissue>
  - <https://github.com/arthurprs/quick-cache/issues/26>
  - <https://github.com/arthurprs/quick-cache/issues/32>
  - <https://github.com/arthurprs/quick-cache/issues/49>
  - <https://github.com/arthurprs/quick-cache/issues/50>
  - <https://github.com/arthurprs/quick-cache/issues/55>
  - <https://github.com/arthurprs/quick-cache/issues/65>
  - <https://github.com/arthurprs/quick-cache/issues/93>
  - <https://github.com/arthurprs/quick-cache/issues/94>
  - <https://github.com/arthurprs/quick-cache/issues/99>
  - <https://github.com/arthurprs/quick-cache/issues/108>
  - <https://github.com/arthurprs/quick-cache/issues/118>
  - <https://github.com/arthurprs/quick-cache/pull/120>
  - <https://github.com/arthurprs/quick-cache/pulls?q=is%3Apr+is%3Amerged>
  - <https://github.com/arthurprs/quick-cache/releases>
  - <https://crates.io/api/v1/crates/quick_cache>
  - <https://crates.io/api/v1/crates/quick_cache/reverse_dependencies>
  - <https://github.com/moka-rs/mokabench>
  - <https://github.com/moka-rs/mokabench/blob/master/src/cache/hashlink.rs>
  - <https://github.com/moka-rs/mokabench/blob/master/src/cache/quick_cache.rs>
  - <https://github.com/moka-rs/mokabench/blob/master/src/cache.rs>
  - <https://github.com/moka-rs/mokabench/blob/master/Cargo.toml>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/arthurprs/quick-cache`) · [data/wave6/enrich/raw/github_com_arthurprs_quick_cache.json](../../../data/wave6/enrich/raw/github_com_arthurprs_quick_cache.json) (enrichment confidence 0.85)

</details>
