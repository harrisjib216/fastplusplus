# Skytable

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0` · 🟢 active

> Multithreaded in-memory Rust NoSQL server with a SQL-like query language; one unaudited 2022 benchmark shows \~6x Redis GET/SET throughput.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | GET/SET ops/sec (30 threads, 1 client per thread): Skytable 619,992/676,091 vs Redis 112,100/99,892, about 5.5x GET and 6.8x SET (derived from page data); KeyDB 288,931/282,997 and Dragonfly 408,322/392,446 in the same post |
| **Workload** | GET/SET requests via redis-benchmark/memtier/sky-bench, 30 threads with 1 client per thread, run against Redis, KeyDB, Dragonfly and Skytable on two AWS m5.4xlarge instances (one server, one client) |
| **Metric** | throughput |
| **Hardware** | 2x AWS m5.4xlarge (one running the k/v store, one running the benchmark client) |
| **Adoption** | 2,659 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/skytable/skytable) · [benchmark](https://news.ycombinator.com/item?id=31796311) |

## Verdict

An anonymous June 2022 HN post ran GET/SET with 30 client threads at 1 connection each between two AWS m5.4xlarge instances and reported Skytable (0.7.x era) at 619,992/676,091 ops/s vs Redis at 112,100/99,892 (about 5.5x GET and 6.8x SET), with KeyDB and Dragonfly in between. It gives no payload size, server versions, build flags or scripts, and does not say which of redis-benchmark, memtier or sky-bench produced each number; Dragonfly's author replied with about 1.02M SET ops/s for Dragonfly on the same instance type at 560 connections, so the result mostly shows multi-threaded servers beating single-threaded Redis at 30 connections.

## Use it when

- Single-node, multi-core in-memory storage with typed schemas (ints, floats, strings, binary, nested lists) where every read and write is a point lookup or update by primary key.
- Write-heavy workloads that can lose the last few minutes of acknowledged writes on a crash in exchange for keeping disk I/O off the request path.
- Rust services: the official Apache-2.0 `skytable` crate is the only stable driver and offers sync and async APIs, TLS and connection pooling.
- Deployments that need the server to run natively on Windows: x86_64 MSVC is a Tier-1 CI target, and the 2022 poster noted it was the only one of the four stores to run on Windows natively.
- Cases where you will benchmark your own workload anyway: the bundled sky-bench tool reports throughput and latency distributions.

## Skip it when

- As a cache: no TTL/expiry, eviction policy or memory cap exists in 0.8 (docs issue #362 asking how to expire keys is unanswered), and the whole dataset must fit in RAM.
- As a Redis replacement: it has no RESP protocol, no Redis structures (sorted sets, streams, pub/sub) and no scripting; the 'fully compatible with Redis' request (#271) has been open since 2022.
- When writes must be durable: by default DML deltas are flushed every 300 s (rs_window; the example config uses 600), or sooner once a model's pending delta passes about 2% of free memory. A crash can lose minutes of acknowledged writes, and there are no multi-statement DML transactions (#331 is open).
- When you need HA, replication or sharding: 0.8.x is single-node only. Clustering (0.9) has been 'nearing completion' since 2025 on the crv1 branch and is unreleased.
- When you need range scans, secondary indexes or joins: DML is point queries on the primary key only, and the docs call multi-row ALL operations slow and discouraged.

## How it is fast

In 0.8, each model's primary index is a lock-free concurrent hash trie in the style of Bagwell's hash array mapped trie and Prokopec et al.'s Ctrie (the code also borrows from the contrie crate). It uses 16-way nodes with crossbeam-epoch memory reclamation, and each row sits behind its own parking_lot RwLock, so threads working on different keys do not share a global lock. Networking runs on a tokio multi-threaded runtime with 16 KiB buffered I/O; the release build uses fat LTO, codegen-units=1 and jemalloc. Durability stays off the request path: DML changes go into an in-memory delta that a background service batch-writes to the journal ('delayed durability'). The 2022 benchmark measured the older 0.7.x store (RwLock-sharded hashbrown tables with GET/SET actions), not this engine.

## Compared with alternatives

If you need Redis semantics on many cores, pick Valkey, KeyDB or Dragonfly: they speak RESP and support TTL and eviction. Pick Skytable only if you want a schema-based, SQL-like point-query store written in Rust that runs natively on Windows, and you can accept delayed durability and single-node operation. Its speed evidence is weaker than the scripted, versioned runs behind Pogocache.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (skyd; prebuilt bundles, .deb, multi-arch Docker images) plus a client crate/driver; not embeddable |
| **Dependencies** | Server: tokio, tokio-openssl + openssl (vendored, so it is compiled from source), crossbeam-epoch, parking_lot, jemallocator (non-MSVC), serde/serde_yaml, crc, uuid, chrono, rcrypt; windows crate on Windows, libc on Unix. Client: skytable crate (Apache-2.0). |
| **Minimum toolchain** | Server MSRV not documented. CI builds with the latest stable Rust (edition 2021), and the source uses `&raw mut`, which needs Rust 1.82 or newer. Building the vendored OpenSSL needs a C toolchain. The Rust client's MSRV is 1.75. |
| **Platforms** | Tier-1 in CI: x86_64 Linux, macOS and Windows (MSVC), aarch64 Linux, i686 Linux. aarch64 macOS is 'Tier-1X'. Tier-2: x86_64 musl and 32-bit Windows, and the changelog says 32-bit Windows will likely be deprecated. |
| **Thread safety** | Multi-threaded server: at least one worker thread per logical CPU (the docs say this cannot be limited), and a semaphore caps concurrent connections at 50,000. Each single DML statement is applied under a per-row RwLock; there are no multi-statement transactions. The Rust client supports concurrent sync and async use plus pooling. |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmarked version no longer exists. The June 2022 numbers came from 0.7.x GET/SET actions; 0.8.0 replaced the query API, protocol and in-memory index. The only Skytable-vs-Redis data for 0.8 is a first-party chart from one 6C/12T laptop-class machine, with no numbers in the text.
- BlueQL rejects inline string and numeric literals: values must be sent as parameters (the REPL fills them in for you). This breaks hand-written or string-concatenated queries.
- A source comment on the 0.8 hash trie warns that its full-size nodes cause 'significant memory blowup' and says the structure will be removed later, so budget RAM generously above your raw data size.
- At first start the root password must be at least 16 characters, and the default plaintext endpoint is 127.0.0.1:2003. Development of 0.9 happens partly in a private repo; the maintainer says 0.8 to 0.9 data migration is ready.

## Known shortcomings

- The only comparison is an anonymous HN post with no method, from an account that keeps promoting Skytable (its 'no affiliation' claim is false).
- The benchmarked 0.7.x GET/SET engine is gone; 0.8 has a new API, protocol and hash-trie index with only a first-party chart. Not a cache: no TTL/expiry/eviction/maxmemory (#362 unanswered), dataset must fit in RAM, and the source warns of significant trie memory blowup. Delayed durability (DML fsync every 300 s by default), no multi-statement transactions, no RESP, single-node; last tag v0.8.4 (2024-08). The HN post used only 30 connections with no payload/version details.

## Caveats and trade-offs

The post does NOT state that the benchmarker has no affiliation, and its independence is doubtful. The HN account johnwoods also submitted 'Skytable - A realtime NoSQL Database written in Rust' (2022-08-26), 'Skytable NoSQL Database: Even with BlueQL, Skytable Outperforms Redis and KeyDB' (2023-12-05, linking ohsayan/sky-benches) and 'Skytable's new NoSQL engine released' (2023-12-09). The post gives no payload size, server versions, build flags or scripts, and does not say which of redis-benchmark/memtier/sky-bench produced the table. The author says Skytable was 'a little inconsistent at times' and that they could not reproduce Dragonfly's claimed 25x. Dragonfly's author replied in the thread with his own m5.4xlarge memtier run (about 1.02M SET ops/s at 28 threads x 20 connections), and the poster objected to the differing connection count. The numbers are from June 2022, before Skytable 0.8 moved to BlueQL. Skytable's own sky-benches repo (first-party, chart only, Tiger Lake 6C/12T, no compiler or flags) is not stronger evidence.

Skytable answers queries in BlueQL (a small SQL-like language) rather than plain GET/SET, so it does strictly more parsing/validation work per request than Redis/KeyDB yet still came out ahead in this benchmark; this 0.8.x line is single-node only (clustering was still WIP at the time); Skytable is also the only one of the four that runs natively on Windows.

## Maintenance

Active but in maintenance mode: 0.8.x gets dependency and CLI fixes (a 0.8.5 changelog landed 2026-09-26; the last tagged release is v0.8.4 from 2024-08-07), while clustered 0.9 is still unreleased. It is an AGPL-3.0 server with an Apache-2.0 client and prebuilt binaries, so run it as a service rather than vendoring it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The HN Ask post (item 31796311, 2022-06-19) does list GET/SET ops/sec for Redis 112,100/99,892 and Skytable 619,992/676,091 at 30 threads x 1 client on 2x m5.4xlarge. It is not a well-known benchmark suite: it is one post by an anonymous account, with no payload size, no server versions, no statement of which tool produced which number, and no scripts. Commenters asked for the missing methodology. So these are numbers without methodology, which is C.
- **Verifier notes:** I downgraded B to C: an anonymous HN post with no methodology does not count as an independent third-party suite, and the poster's history is heavily Skytable-promotional. The record's 'states no affiliation' claim was unsupported, so I rewrote the caveats. I read the HN item through the Algolia items API mirror. The repo metadata matches: AGPL-3.0, not a fork, last commit 2026-09-26.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://hn.algolia.com/api/v1/items/31796311>
  - <https://hn.algolia.com/api/v1/users/johnwoods>
  - <https://hn.algolia.com/api/v1/search_by_date?tags=author_johnwoods&hitsPerPage=50>
  - <https://github.com/skytable/skytable>
  - <https://github.com/ohsayan/sky-benches>
- **Sources the enricher read:**
  - <https://github.com/skytable/skytable>
  - <https://github.com/skytable/skytable/blob/next/README.md>
  - <https://github.com/skytable/skytable/blob/next/CHANGELOG.md>
  - <https://github.com/skytable/skytable/blob/next/Cargo.toml>
  - <https://github.com/skytable/skytable/blob/next/server/Cargo.toml>
  - <https://github.com/skytable/skytable/blob/next/.cargo/config.toml>
  - <https://github.com/skytable/skytable/blob/next/server/src/main.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/idx/mtchm/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/idx/mtchm/meta.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/idx/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/core/index/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/core/index/row.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/core/model/delta.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/net/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/fractal/mod.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/fractal/mgr.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/config.rs>
  - <https://github.com/skytable/skytable/blob/next/server/src/engine/ql/lex/raw.rs>
  - <https://github.com/skytable/skytable/blob/next/examples/config-files/template.yaml>
  - <https://github.com/skytable/skytable/blob/next/.github/workflows/test-push.yml>
  - <https://github.com/skytable/skytable/blob/next/.github/workflows/release.yml>
  - <https://github.com/skytable/skytable/blob/v0.7.5/server/src/corestore/map/mod.rs>
  - <https://github.com/skytable/skytable/releases>
  - <https://github.com/skytable/skytable/tree/crv1>
  - <https://github.com/skytable/skytable/issues/362>
  - <https://github.com/skytable/skytable/issues/385>
  - <https://github.com/skytable/skytable/issues/271>
  - <https://github.com/skytable/skytable/issues/374>
  - <https://github.com/skytable/skytable/issues/331>
  - <https://github.com/skytable/skytable/issues/300>
  - <https://github.com/skytable/skytable/issues>
  - <https://github.com/skytable/client-rust>
  - <https://github.com/ohsayan/sky-benches>
  - <https://docs.skytable.io/architecture>
  - <https://docs.skytable.io/libraries>
  - <https://docs.skytable.io/blueql/overview>
  - <https://skytable.io/blog/2023/12/skytable-octave-is-here/>
  - <https://news.ycombinator.com/item?id=31796311>
  - <https://hn.algolia.com/api/v1/items/31796311>
  - <https://hn.algolia.com/api/v1/items/38593065>
  - <https://hn.algolia.com/api/v1/items/38537575>
  - <https://hn.algolia.com/api/v1/search?query=skytable&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/skytable/skytable`) · [data/wave6/enrich/raw/github_com_skytable_skytable.json](../../../data/wave6/enrich/raw/github_com_skytable_skytable.json) (enrichment confidence 0.8)

</details>
