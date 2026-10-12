# Ferrous

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> AI-written Rust Redis/RESP2 server; self-reported 0-8% over Valkey 8.0.4 on single commands, \~2x slower pipelined SET.

| | |
|---|---|
| **Beats** | Valkey 8.0.4 |
| **Claimed result** | Ferrous \~5-8% faster than Valkey on single-command ops; PING pipeline +25% (833k vs 667k ops/s); but SET pipeline is 94% faster on Valkey's side (588k vs 303k ops/s) - a mixed, not uniform, win |
| **Workload** | Standardized redis-benchmark testing of core RESP commands (PING, SET, etc.) and pipelined operations, Ferrous vs Valkey 8.0.4 |
| **Metric** | throughput |
| **Adoption** | 18 stars |
| **Last commit** | 2025-11-05 |
| **Links** | [repository](https://github.com/iGentAI/ferrous) · [benchmark](https://github.com/iGentAI/ferrous/blob/main/README.md) |

## Verdict

The README table is a single first-party redis-benchmark run against Valkey 8.0.4 on the same unnamed machine: 10,000 requests per command with the tool's default client count and payload, logs to /dev/null, and no CPU, OS, Rust version or Valkey settings stated. The public script covers the PING pipeline but not the SET pipeline. Ferrous leads by 0-8% on single commands and by 25% on 10-deep PING pipelines, Valkey leads by 94% on 10-deep SET pipelines, and PR #42's post-fix run (Nov 2025, Rust 1.89) puts Ferrous GET at 73,529 ops/s, below the README's Valkey GET figure of 74,626.

## Use it when

- You want a compact pure-Rust reference implementation of RESP2, Streams consumer groups, WATCH and Redis-style Lua scripting to read, fork or teach from.
- Local development or CI tests that need a Redis-compatible endpoint on port 6379, where the dataset fits in RAM and nothing needs evicting.
- Non-pipelined request/response traffic with small values and modest connection counts. This is the only workload where the README shows it level with or slightly ahead of Valkey.
- Experiments on AI-generated systems code, using the bundled redis-benchmark scripts (tests/performance) to re-measure against Valkey yourself.

## Skip it when

- As a bounded cache. The config parser reads maxmemory, but the server builds its storage with StorageEngine::new(), which hard-codes MemoryManager::unlimited(), and eviction is marked 'TODO: implement eviction'. Memory grows without limit.
- Pipelined or batched writes: the README's own table has Valkey at 588,235 vs Ferrous 303,030 ops/s for SET with 10-command pipelines.
- Many connections or multi-core scaling. One thread issues a read on every connection each loop, so loop cost grows with connection count, and there is no parallel command execution to compete with Dragonfly or KeyDB.
- Slow clients or large replies. When a socket buffer is full, Connection::flush() sleeps 10+20+30+40 ms (up to 100 ms) inside the only event-loop thread, which stalls every other client.
- Production, or anything that needs cluster, modules, HyperLogLog, bit ops, RESP3 or partial resync. The code is AI-generated, the repo has 18 stars and no filed issues, and its docs contradict the code.

## How it is fast

There is no distinctive algorithm behind the numbers. The README says 'multi-threaded' and 'Tokio-based', but Cargo.toml enables only tokio's rt and time features, and server.rs spawns no threads: one loop polls every non-blocking std::net socket in turn (no epoll/kqueue), reads up to 8 KB per connection, runs all complete frames and flushes the replies with a single write (TCP_NODELAY on), then yields when busy or sleeps 10 us to 1 ms when idle. Data sits in 16 FNV-1a-sharded std HashMaps per database behind RwLocks; reads skip LRU access-time bookkeeping, WATCH tracking is skipped when nobody is watching, and the release build uses LTO with codegen-units=1. Each benchmark run is 10,000 requests, about 0.13 s at \~76k ops/s, which is too short to separate a 0-8% margin from noise.

## Compared with alternatives

Rarely. Valkey itself (catalogued) is more complete and far faster on pipelined writes, and Dragonfly or KeyDB are the choices when you need multi-core throughput from a Redis-compatible server. Pick Ferrous only when you specifically want a small pure-Rust RESP2 server with Streams and Lua to study or fork.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone server binary built with cargo build --release; not on crates.io, where the 'ferrous' name belongs to an unrelated 2016 test-matcher crate) |
| **Dependencies** | tokio (rt, time only), mlua 0.11 with vendored Lua 5.1 (needs a C compiler), crossbeam, crossbeam-epoch, futures, lazy_static, rand, uuid, sha1, hex, thiserror |
| **Minimum toolchain** | Rust edition 2021 with no rust-version or toolchain pin. Main builds on Rust 1.89.0 after PR #42; older commits fail there on the now deny-by-default dangerous_implicit_autorefs lint. A C toolchain is needed for the vendored Lua. |
| **Platforms** | Not documented. Networking uses only portable std::net non-blocking sockets; test scripts assume Linux with dnf (Fedora/RHEL). |
| **Thread safety** | It is a server process, so this does not apply to callers. Internally one thread does all client I/O and command execution. Background threads handle key expiry, RDB/AOF, replication and monitoring, and share RwLock-sharded storage with it. |
| **Drop-in for the baseline** | partial — it speaks RESP2 and works with redis-cli and redis-py for 140+ commands, but it lacks cluster, modules, HyperLogLog, bit operations and RESP3, it does not enforce maxmemory or eviction, and most config changes need a restart |

## Gotchas

- The docs disagree with each other and with the code. ARCHITECTURE.md describes edge-triggered epoll, I/O and worker thread pools and a custom allocator, none of which the code has. VALIDATION.md reports pipelined SET at 316k vs \~280k (Ferrous ahead), while the README reports 303k vs 588k (Valkey ahead), and RELEASE_NOTES claims equal 769k pipelined throughput.
- Every SCAN call copies and sorts all keys in the database before returning a page. A full keyspace iteration therefore costs O(N log N) per page, and each call blocks all clients on the single loop thread.
- GET and LRANGE take the shard's write lock and clone the returned data. The expiry thread walks every key that has a TTL once per second instead of sampling. Sorted sets use a hand-written unsafe raw-pointer skiplist, which needed 26 compile fixes for Rust 1.89 (PR #42).
- The idle loop backs off to 1 ms sleeps after \~100 empty cycles, so the first request after a quiet spell can wait up to \~1 ms. Under load the loop spins with yield_now and burns a core.

## Known shortcomings

- Mixed results vs Valkey (not a listed baseline): wins some operations and loses others.
- maxmemory is parsed but never applied (MemoryManager::unlimited, eviction TODO), so the cache is unbounded. The README's 'multi-threaded/Tokio' claim is false: one loop polls each std::net socket without epoll and a WouldBlock flush sleeps up to 100 ms, stalling all clients. Pipelined SET: Valkey 588k vs 303k; post-fix GET 73,529 is below the README's Valkey 74,626; runs are 10k requests (\~0.13 s, noise). Docs contradict each other; SCAN copies and sorts all keys every call; reads take a shard write lock; unsafe raw-pointer skiplist. No commits since 2025-11; not on crates.io; AI-written, 18 stars.

## Caveats and trade-offs

Results are mixed. The single-command wins are small (0-8%; SADD is equal, INCR is +2%), PING pipelining is +25%, and Valkey is 94% faster on SET pipelining (588k vs 303k ops/s). Each op runs only 10,000 requests, with 10-command pipelines. The baseline is Valkey (a Redis fork), not upstream Redis, so baseline_in_list=false. No hardware, compiler or flags are stated. The codebase was written by an AI assistant (Maestro, iGent AI), per the README. The HN submission title 'Outperforms Valkey' overstates the README's own mixed table.

No Redis module system, clustering incomplete; README states the project was developed entirely through AI-assisted programming; SET pipelining is notably slower than Valkey

## Maintenance

The record calls it active, but main has had no commits since 2025-11-05 (a Rust 1.89 build fix), about 11 months before this entry, and one bit-operations PR is still open. It is dual MIT/Apache-2.0 per Cargo.toml (GitHub shows MIT) and fine to borrow code from, but it is not a production Redis replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Performance section has a first-party redis-benchmark table against Valkey 8.0.4 (10,000 requests per op), and the script is public (tests/performance/test_benchmark.sh, run via ./run_tests.sh perf). No CPU model, compiler or build flags are stated, so it cannot be A.
- **Verifier notes:** Every number in claimed_speedup matches the README exactly. Cargo.toml declares 'MIT OR Apache-2.0' and the README says the project is dual licensed; GitHub reports only MIT because the repo has a single LICENSE file. The last commit on the default branch (main) is 2025-11-05; the record's 2025-11-28 date is from the non-default branch feature/bit-operations-implementation. The project is still active.
- **Fields the verifier corrected:** `license`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/iGentAI/ferrous>
  - <https://github.com/iGentAI/ferrous/blob/main/README.md>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/README.md>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/Cargo.toml>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/run_tests.sh>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/tests/performance/test_benchmark.sh>
  - <https://hn.algolia.com/api/v1/search?query=ferrous%20valkey&tags=story>
- **Sources the enricher read:**
  - <https://github.com/iGentAI/ferrous>
  - <https://github.com/iGentAI/ferrous/blob/main/README.md>
  - <https://github.com/iGentAI/ferrous/blob/main/Cargo.toml>
  - <https://github.com/iGentAI/ferrous/blob/main/src/main.rs>
  - <https://github.com/iGentAI/ferrous/blob/main/src/storage/engine.rs>
  - <https://github.com/iGentAI/ferrous/blob/main/src/storage/memory.rs>
  - <https://github.com/iGentAI/ferrous/blob/main/src/storage/value.rs>
  - <https://github.com/iGentAI/ferrous/blob/main/src/config/mod.rs>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/src/network/server.rs>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/src/network/listener.rs>
  - <https://raw.githubusercontent.com/iGentAI/ferrous/main/src/network/connection.rs>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/ARCHITECTURE.md>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/DESIGN.md>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/RELEASE_NOTES.md>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/ROADMAP.md>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/TEST_RESULTS.md>
  - <https://github.com/iGentAI/ferrous/blob/main/docs/VALIDATION.md>
  - <https://github.com/iGentAI/ferrous/blob/main/tests/performance/test_benchmark.sh>
  - <https://github.com/iGentAI/ferrous/blob/main/tests/performance/test_comprehensive_benchmarks.sh>
  - <https://github.com/iGentAI/ferrous/blob/main/run_tests.sh>
  - <https://github.com/iGentAI/ferrous/blob/main/master.conf>
  - <https://github.com/iGentAI/ferrous/pull/42>
  - <https://github.com/iGentAI/ferrous/pulls?q=is%3Apr>
  - <https://github.com/iGentAI/ferrous/issues>
  - <https://github.com/iGentAI/ferrous/commits/main>
  - <https://github.com/search?q=repo%3AiGentAI%2Fferrous+thread%3A%3Aspawn&type=code>
  - <https://github.com/search?q=repo%3AiGentAI%2Fferrous+set_nonblocking&type=code>
  - <https://github.com/search?q=repo%3AiGentAI%2Fferrous+MemoryManager%3A%3Anew&type=code>
  - <https://github.com/search?q=repo%3AiGentAI%2Fferrous+StorageEngine%3A%3Anew&type=code>
  - <https://hn.algolia.com/api/v1/search?query=ferrous%20valkey&tags=story>
  - <https://crates.io/api/v1/crates/ferrous>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/igentai/ferrous`) · [data/wave6/enrich/raw/github_com_igentai_ferrous.json](../../../data/wave6/enrich/raw/github_com_igentai_ferrous.json) (enrichment confidence 0.75)

</details>
