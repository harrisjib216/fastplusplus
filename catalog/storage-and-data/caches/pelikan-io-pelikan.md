# Pelikan / Segcache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust cache-server framework whose pelikan-segcache speaks memcached's text protocol over Segcache, a TTL-segmented store with 5-byte-per-item metadata.

| | |
|---|---|
| **Beats** | Memcached |
| **Claimed result** | NSDI'21 paper: close to 8x speedup over Memcached with 24 threads (Segcache over 70 MQPS vs Memcached 9 MQPS); up to 40% higher throughput than Memcached on a single thread; 5 bytes/object metadata vs Memcached's 56 bytes (91% less); 22-60% less memory than state-of-the-art designs (abstract), up to 60% less vs Memcached, and 42-88% less memory footprint vs Twitter's production PCache (slab) system |
| **Workload** | NSDI'21 paper evaluation of Segcache (Pelikan's TTL-segmented storage engine) on production-derived cache workloads, scaling to 24 threads, comparing per-object metadata overhead and multi-core throughput scaling vs Memcached's slab allocator |
| **Metric** | throughput |
| **Hardware** | Dual-socket Intel Xeon Gold 6230R, 384GB DRAM, one 100Gbps NIC (dedicated hosts in Twitter's production fleet); closed-loop trace replay of the storage subsystem only |
| **Adoption** | 295 stars (current Rust rewrite); legacy C implementation at github.com/twitter/pelikan has \~2k stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/pelikan-io/pelikan) · [benchmark](https://www.usenix.org/conference/nsdi21/presentation/yang-juncheng) |

## Verdict

The NSDI'21 paper replayed Twitter production traces against the storage layer only (no networking) on dual Xeon Gold 6230R hosts. The multi-thread test used trace c, with 7% writes. In it, the legacy C Segcache (twitter/pelikan, archived at thesys-lab/segcache) reached over 70 MQPS at 24 threads. Memcached 1.6.6 levelled off at 9 MQPS after 8 threads. On one thread, Segcache was up to 40% faster than Memcached. Compiler and flags are not stated. None of these numbers were measured on the current Rust code, which keeps the segment design and 5-byte metadata but not the per-thread write segments. The Rust engine's only published scaling data (i5-13500H E-cores, rustc 1.97.1, engine only) shows reads scaling 8.19x on 8 cores while writes do not scale.

## Use it when

- Memcached-style look-aside caches with many small objects (tens to a few hundred bytes), where per-item metadata is a large share of DRAM.
- Workloads where items carry TTLs and expired data should leave memory quickly (the paper's Twitter traces used TTLs from 2 minutes to 30 days).
- Read-heavy traffic: the current engine's reads scale almost linearly (8.19x on 8 cores for uniform gets in the maintainers' own harness).
- Teams that want to build a custom cache server in Rust from reusable protocol, storage and runtime crates, or embed the `segcache` crate directly.

## Skip it when

- Write-heavy traffic, or traffic that overwrites the same keys often, on many cores. The maintainers measured writes to one shared engine at 0.82x of single-thread throughput on 8 cores: every writer in one TTL bucket reserves space at one shared tail segment (cache-rs issue #85, open). The 2021 Segcache blog already lists a very high overwrite rate as a weak spot.
- Large objects, or data with no TTLs: the Segcache authors say these see limited benefit from the design.
- When you are counting on the paper's multi-core numbers. The paper's C engine gave each thread its own active write segments; the Rust engine does not do this yet, and nobody has published a Rust Pelikan versus Memcached throughput result.
- Code that uses `add` as a distributed lock or needs atomic add/replace: with more than one worker, two concurrent `add`s on one key can both return STORED (32.7% of hot-key races at 8 workers, in the maintainers' own test).
- Risk-averse production use, or clients that need the memcached meta or binary protocol, `touch`/`gat`, or stats on the data port. The concurrent engine is about a month old. Its rollout found seven engine bugs (lost increments, a deadlock, resurrected deletes, false misses), and some correctness issues are still open (for example cache-rs #101, a false NotFound on cas). The server wires only the text protocol: get, set, add, replace, append, prepend, cas, incr, decr, delete, flush_all, version and quit.

## How it is fast

Segcache appends items to fixed-size segments (1 MiB by default). Each segment holds only items with similar TTLs, grouped into 1024 TTL buckets. Per-item metadata is therefore a 5-byte header plus an 8-byte hash slot, instead of Memcached's roughly 56 bytes of pointers, LRU links and timestamps. A whole expired segment is freed in one step. Eviction uses merge-based eviction, which scans a run of segments and copies only frequently used items (1-byte approximate frequency counter) into a new segment; S3-FIFO and simpler policies are optional. The Rust engine uses a lock-free 2-choice hash table of 64-byte buckets with SIMD tag scans (AVX2/NEON), and since segcache 0.4 (August 2026) N worker threads share one engine through `Arc` with no storage thread in between.

## Compared with alternatives

Pick this over Garnet or KeyDB when you run a Memcached-protocol cache of many small TTL'd objects and memory per item costs more than the Redis data-structure features those two provide. Caffeine is an in-process JVM library rather than a network server, so it fits a different case.

## Integration

| | |
|---|---|
| **Form** | server binary built from a Cargo workspace (the Pelikan crates are not on crates.io); storage engine is the `segcache` crate (crates.io 0.4.x) |
| **Dependencies** | segcache 0.4.3 and keyvalue (pelikan-io/cache-rs), mio, rustls with AWS-LC (needs a C toolchain and cmake), metriken, clocksource, serde/toml |
| **Minimum toolchain** | Rust stable, edition 2021; no MSRV declared; CI uses dtolnay/rust-toolchain@stable; cmake and a C compiler for AWS-LC |
| **Platforms** | CI builds on ubuntu-latest and macos-latest; SIMD tag scan on x86-64 (AVX2) and aarch64 (NEON) with a scalar fallback; Windows not documented |
| **Thread safety** | Since segcache 0.4 the engine is Sync, and N worker threads share it through Arc and run requests in place. add/replace are check-then-act and can race; cas can fail with EXISTS when it races eviction relocation; flush_all runs as a single sweep on the admin thread before the reply. |
| **Drop-in for the baseline** | partial — existing memcached text-protocol clients work for the core commands, but admin commands use a separate port, configuration is TOML rather than memcached flags, there is no meta or binary protocol, add/replace are not atomic across workers, and numeric-looking values are stored typed (`set 007` reads back `7`). |

## Gotchas

- Rust Pelikan runs no periodic expiry. Expired items become invisible on access, and their memory comes back only under write pressure, so a lightly loaded server shows expired segments as used memory.
- The hash table has a fixed size (`hash_power`, default 16 in code, 22 in the sample config) with no overflow chains. Set it too low and you lose capacity with no warning (issue #29 asks for a log message). Segment ids are 18 bits, and segments over 8 MiB used to alias item locations silently in release builds (cache-rs #79, closed 2026-08-20).
- The engine metrics evict_time, expire_time and clear_time used a 1-second clock and reported 0 or exactly 1 s (cache-rs #75, fixed upstream). Check which segcache version you run before trusting them.
- Some cited evidence does not match the code. The README's p999 &lt; 5 ms at 1M QPS result (the Intel ADQ post, 2020) was measured on the C pelikan_twemcache slab server, not on Segcache or Rust. The segcache crate's docs/segcache.md still describes a single-threaded `&mut self` engine, although the 0.4 API takes `&self`.

## Known shortcomings

- Paper numbers (70 vs 9 MQPS at 24 threads) come from the legacy C Segcache; no Rust Pelikan vs Memcached benchmark exists. The Rust engine dropped the paper's per-thread write segments (one shared tail per TTL bucket), so writes run 0.82x on 8 cores while reads are 8.19x (cache-rs journal, #85 open). Multi-worker shared engine only since 2026-08 (segcache 0.4.0-0.4.2 yanked; 7 engine bugs found in rollout; false NotFound on cas, #101). add/replace not atomic across workers (32.7% double-win at 8 workers); data port text protocol only. The README's ADQ p999 claim measured C pelikan_twemcache (slab), not Segcache; cache-rs docs still say single-threaded.
- The NSDI'21 paper's C artifact is github.com/Thesys-lab/Segcache (folded into this entry).

## Caveats and trade-offs

Paper numbers are for the original C Segcache module in twitter/pelikan (archived at thesys-lab/segcache), not the current Rust rewrite at pelikan-io/pelikan; the Rust README repeats them as properties of 'the same architecture'. The evaluation covers the storage subsystem only (the networking stack was not modified), uses Twitter production traces, and was run by Twitter/CMU authors. The compiler and flags are not stated. The README's '40-90% vs Pelikan's own slab storage' rounds the paper's 42-88% vs PCache. Language of the current repo is Rust, not C++.

TTL-segmented design trades some flexibility (object grouping by expiry) for memory efficiency; original Segcache/legacy Pelikan was C, current pelikan-io/pelikan is a full Rust rewrite so the exact peer-reviewed binary is not what ships today

## Maintenance

Active (commits in September 2026, Apache-2.0) and buildable with stable Rust, but multi-worker storage only landed in August 2026 on a young concurrent engine, and the peer-reviewed numbers belong to the unmaintained C code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'21 paper (the abstract on the USENIX page and the full PDF) compares Segcache with Memcached 1.6.6: close to 8x speedup at 24 threads (over 70 vs 9 MQPS) and 5 vs 56 bytes of metadata per object. The CPU (dual Xeon Gold 6230R) and code (twitter/pelikan, thesys-lab/segcache) are given but the compiler and flags are not, so it is not A.
- **Verifier notes:** The numbers are now verified against the paper PDF (https://www.usenix.org/system/files/nsdi21-yang.pdf) rather than the blog, and hardware is filled in. Tier B holds, but the benchmarked code is the legacy C implementation (twitter/pelikan: 1,957 stars, last commit 2022-10-27), not the Rust repo. The C++-only search filter returned a Rust project.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/nsdi21/presentation/yang-juncheng>
  - <https://www.usenix.org/system/files/nsdi21-yang.pdf>
  - <https://www.usenix.org/system/files/nsdi21_errata_yang_juncheng-1.pdf>
  - <https://github.com/pelikan-io/pelikan>
  - <https://github.com/twitter/pelikan>
  - <https://github.com/pelikan-io/pelikan-c>
- **Sources the enricher read:**
  - <https://github.com/pelikan-io/pelikan>
  - <https://github.com/pelikan-io/pelikan/blob/main/Cargo.toml>
  - <https://github.com/pelikan-io/pelikan/blob/main/Cargo.lock>
  - <https://github.com/pelikan-io/pelikan/blob/main/config/segcache.toml>
  - <https://github.com/pelikan-io/pelikan/blob/main/src/config/src/seg.rs>
  - <https://github.com/pelikan-io/pelikan/blob/main/src/entrystore/src/segcache/mod.rs>
  - <https://github.com/pelikan-io/pelikan/blob/main/src/server/segcache/Cargo.toml>
  - <https://github.com/pelikan-io/pelikan/blob/main/src/server/segcache/src/lib.rs>
  - <https://github.com/pelikan-io/pelikan/blob/main/src/protocol/memcache/src/binary/mod.rs>
  - <https://github.com/pelikan-io/pelikan/blob/main/.github/workflows/cargo.yml>
  - <https://github.com/pelikan-io/pelikan/blob/main/docs/journal/2026-08-18-concurrent-segcache-conversion.md>
  - <https://github.com/pelikan-io/pelikan/blob/main/docs/superpowers/specs/2026-08-18-concurrent-segcache-conversion-design.md>
  - <https://github.com/pelikan-io/pelikan/issues/29>
  - <https://github.com/pelikan-io/pelikan/issues/127>
  - <https://github.com/pelikan-io/cache-rs>
  - <https://github.com/pelikan-io/cache-rs/blob/main/docs/segcache.md>
  - <https://github.com/pelikan-io/cache-rs/blob/main/crates/segcache/Cargo.toml>
  - <https://github.com/pelikan-io/cache-rs/blob/main/docs/journal/2026-08-25-segcache-read-write-scaling.md>
  - <https://github.com/pelikan-io/cache-rs/blob/main/benchmarks/segbench/README.md>
  - <https://github.com/pelikan-io/cache-rs/issues/85>
  - <https://github.com/pelikan-io/cache-rs/issues/91>
  - <https://github.com/pelikan-io/cache-rs/issues/101>
  - <https://github.com/pelikan-io/cache-rs/issues/79>
  - <https://crates.io/api/v1/crates/segcache>
  - <https://www.usenix.org/system/files/nsdi21-yang.pdf>
  - <https://github.com/Thesys-lab/Segcache>
  - <https://github.com/twitter/pelikan>
  - <https://pelikan.io/blog/segcache/>
  - <https://pelikan.io/blog/benchmark-adq/>
  - <https://www.usenix.org/conference/nsdi21/presentation/yang-juncheng>
  - <https://hn.algolia.com/api/v1/search?query=pelikan%20segcache&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/pelikan-io/pelikan`) · [data/wave6/enrich/raw/github_com_pelikan_io_pelikan.json](../../../data/wave6/enrich/raw/github_com_pelikan_io_pelikan.json) (enrichment confidence 0.8)

</details>
