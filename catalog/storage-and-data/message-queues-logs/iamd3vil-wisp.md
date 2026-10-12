# Wisp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Experimental Rust server speaking the NATS Core client protocol; about 3.7-4.4x nats-server throughput on 1,000-subscriber loopback fan-out.

| | |
|---|---|
| **Beats** | NATS |
| **Claimed result** | 4.37x higher median aggregate delivery throughput than NATS 2.14.6 (9,023,597 vs 2,066,099 deliveries/sec); 76.4% less server CPU time |
| **Workload** | NATS-Core-wire-protocol pub/sub fan-out: 1 publisher, 1,000 subscribers, 128-byte payloads, 100,000 publications (=100M aggregate deliveries per run), 3 repeated runs, CPU-pinned client/server |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 9700X, single Linux host over loopback TCP; server pinned to CPUs 0-3,8-11 and the Go benchmark client to 4-7,12-15 (4 physical cores/8 logical each); fd limit 1,048,576 |
| **Compiler and flags** | cargo build --release --locked, using the default release profile (opt-level 3) with debug=true in Cargo.toml, no custom RUSTFLAGS and Rust 2024 edition; the rustc version is not stated anywhere |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/iamd3vil/wisp) · [benchmark](https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/REPORT.md) |

## Verdict

Setup: a single shared Ryzen 7 9700X Linux host over loopback, with server and nats.go client pinned to disjoint 4-core sets, 1 publisher and 1,000 subscriber connections receiving 100,000 x 128 B messages (100M deliveries). Median of 3 runs: Wisp 9.02M deliveries/s vs 2.07M for nats-server 2.14.6 (4.37x), using 87 vs 371 server CPU-seconds; the rustc version is not stated. That build predates the slow-consumer limits, headers, auth/TLS and metrics. Later sessions on the same host measured 4.39x, 3.89x and 3.70x (9.21 vs 2.49M/s at commit 26d0376). The latest committed build (8.45M/s fan-out) has not been rerun against NATS.

## Use it when

- Your clients already speak NATS Core and the load is high fan-out transient pub/sub: one publisher to hundreds or thousands of subscriber connections on a subject, with small (64-128 B) payloads, where nats-server CPU is the limit. At 1,000 subscribers it measured 3.7-4.4x the deliveries/s with roughly a quarter of the server CPU-seconds (87 vs 371) and lower peak RSS (61 vs 93 MiB).
- Many-subject publishing where the hot subject set fits the dispatch cache (100,000 plans per account by default). The 5,000-subject wildcard case measured about 5.1M deliveries/s vs 1.9-2.0M for NATS, using about a third of the CPU.
- A single-node, at-most-once Core broker on Linux/Unix where you can live without clustering, for example in-host or in-rack telemetry fan-out, or a local stand-in for nats-server in tests.
- Idle request/reply over loopback: p50 about 17 us vs 19-20 us for NATS. The gain is small but it has held in every session.
- As a reference design for a NATS-protocol server in Rust. The harness is reproducible, and the reports keep failed runs and regressions.

## Skip it when

- You need clustering, leafnodes or gateways, JetStream or any persistence/replay, KV or object store, NKeys/JWT operator mode, auth callouts, account imports/exports, or queue-name-specific and dynamic response permissions. None of these are implemented.
- Any production or redistribution use. There is no LICENSE file, so default copyright applies. It is also a single-author 0.1.0 project with 2 stars, no releases or tags, no issue history, and 27 of its 48 commits landed on one day (2026-09-08).
- Many publishers into one subscriber under sustained load. Earlier builds disconnected the subscriber at the pending-message cap in 6 of 10 runs of 100M messages. The current batched build completed 5 of 5, but still uses about 1.35x NATS server CPU (50 vs 37 CPU-s per 100M) and 73 vs 21 MiB peak RSS.
- One publisher to one subscriber with small messages: this is roughly parity (0.97x-1.07x across sessions). Larger-payload results have swung between sessions, from -34% and -49% at 1 KiB and 8 KiB in the first run to +2% to +12% later.
- Workloads with subscription churn or cold subjects. Any SUB or UNSUB invalidates every cached plan in that account. Past the 100,000-subject cache it ran about 7.5% behind NATS (1.76 vs 1.90M msg/s). TLS- or auth-enabled throughput has never been measured.

## How it is fast

For each subject it builds a dispatch plan (the matching subscriptions plus a pre-encoded `MSG subject sid` header prefix per subscriber) and caches it in a bounded, sharded FIFO cache with generation-number invalidation. A per-connection last-subject cache sits in front of that, so hot publishes skip the submap subject trie entirely. Payloads are refcounted `bytes::Bytes` slices of the 64 KiB socket read buffer, shared by every recipient (zero-copy fan-out), and are parsed with a memchr line scan and a fast-path PUB parser. Each connection has its own Tokio writer task, which swaps the pending queue out from under the mutex in O(1), encodes up to 64 KiB or 1,024 messages into one contiguous buffer and writes it, flushing as soon as the queue drains with no idle timer. Single-subscriber subjects also get producer-side batching: up to 1,024 deliveries are pre-encoded into one wire frame and admitted with one lock acquisition. The global allocator is jemalloc and the hash maps use ahash.

## Compared with alternatives

Pick Wisp only if your clients already speak NATS Core and you need single-node, non-durable fan-out with far less broker CPU than nats-server. Zenoh is the closest sibling for transient pub/sub but has its own protocol and API. TCPSHM targets point-to-point RTT. Redpanda, FluxMQ and Woodpecker fit when you need a persistent, replayable log, which Wisp does not have.

## Integration

| | |
|---|---|
| **Form** | standalone server binary built from source with cargo build --release. It is not on crates.io (the crates.io name 'wisp' belongs to an unrelated tmux tool) and there are no prebuilt releases. |
| **Dependencies** | tokio (full), bytes, submap (subject trie), ahash, memchr, itoa, tikv-jemallocator, tokio-rustls (ring, tls12), rustls-pemfile, sha2, subtle, serde, serde_json, uuid, lazy_static, thiserror, tracing, tracing-subscriber. The benchmark harness also needs Go, Python 3, Linux taskset and a nats-server binary. |
| **Minimum toolchain** | The README only says 'a toolchain that supports the 2024 edition' (Rust 1.85+). The source uses if-let chains, which were stabilized in Rust 1.88, so 1.88+ in practice. There is no rust-toolchain file and the benchmarked rustc is not stated. |
| **Platforms** | Unix only (server.rs uses tokio::signal::unix unconditionally). It was benchmarked only on x86-64 Linux (Ryzen 7 9700X). There is no SIMD or architecture-specific code, and src/ contains no unsafe blocks. |
| **Thread safety** | Not applicable as an API, since clients connect over TCP. Internally it runs a multi-threaded Tokio runtime with one worker per logical CPU by default, a per-account RwLock routing table, a sharded Mutex dispatch cache, and per-connection Mutex output queues. TOKIO_WORKER_THREADS changes overload behavior: at one stage 1 worker completed stress runs that the default setting failed. |
| **Drop-in for the baseline** | partial — wire-compatible with NATS Core clients for pub/sub, queue groups, request/reply, headers, static auth and TLS (verified with nats.go). Not a replacement for clustering, JetStream, NKeys/JWT, leafnodes, or nats-server config files. An empty allow-list denies everything, unlike NATS. |

## Gotchas

- Slow consumers: a recipient that exceeds 64 MiB or 524,288 pending messages, or misses the 10 s write deadline, loses its whole connection and its queued output. If the 1 GiB aggregate output budget runs out, the recipient that cannot reserve space is closed, which can be a healthy peer rather than the largest backlog. In the stall test a subscriber survived a 400 ms read pause but was dropped at 550 ms; NATS lasted until 400-700 ms.
- Any SUB or UNSUB bumps a per-account generation counter, and that invalidates every cached dispatch plan in the account. Subscription churn therefore turns unrelated hot subjects cold.
- Batched single-subscriber deliveries wait in the publisher connection until a flush point and count against no pending limit until admitted. Prometheus publication and delivery counters can lag by up to 1,023 publications per publisher. Fan-out and queue-group paths skip batching and still admit each message separately.
- The WISP_WRITEV_FLUSH_THRESHOLD_BYTES setting does not use writev: the writer copies each batch into one contiguous buffer. On SIGHUP, any change to the security or client-CA file, even formatting only, disconnects every client. The monitoring HTTP listener has no authentication or TLS.

## Known shortcomings

- Numbers match (vs NATS 2.14.6, Ryzen 9700X, public harness) but rustc version unstated, 2 stars, no licence (reference only); Rust, not C++ (verifier downgrade from A).
- The 4.37x was measured before limits/TLS/auth/metrics were added; later same-host runs gave 4.39x/3.89x/3.70x and the latest build's fan-out wasn't re-run vs NATS. 8 publishers to 1 subscriber: older builds dropped the subscriber at the cap in 6/10 runs; the batched build passes but uses \~1.35x NATS's CPU and 73 vs 21 MiB RSS. Roughly parity on 1:1 small messages; \~7.5% behind NATS past 100k subjects; any SUB/UNSUB clears the account plan cache. No clustering, JetStream, NKeys or JWT; Unix only; needs rustc 1.88+ (unstated); TLS/auth throughput unmeasured. One author, v0.1.0, 27 of 48 commits in one day.

## Caveats and trade-offs

Very new, low-visibility repo (2 stars). It has no LICENSE file, so the code cannot legally be reused. The rustc version is not stated. The measurement is a single host over loopback with 3 runs per server, and the report says the host 'runs other services'. The runs are finite bursts, not steady state, and the author notes they do not establish performance on other hardware or over a real network. Wisp implements only part of NATS Core (no clustering, no JetStream), so the comparison covers only the core pub/sub fan-out path. The earlier 100-subscriber comparison in the same repo showed a smaller \~2.6x lead.

Experimental single-author project; not a full NATS Core replacement (no clustering, JetStream, or persistence); comparison is same-host loopback, not over a real network

## Maintenance

Actively developed as of 2026-09-08 but single-author and unlicensed. Treat it as reference-only: you can read and benchmark it, but there is no grant to reuse or redistribute the code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** REPORT.md matches the claim exactly: median 9,023,597 vs 2,066,099 deliveries/s against nats-server v2.14.6, 4.37x, and 76.4% less server CPU. The harness is public (profiling/bench/run.py driving the Go client profiling/bench/main.go), and the CPU (Ryzen 7 9700X) and affinity are stated. The rustc version is never stated (no rust-toolchain file; the README only says 'a toolchain that supports the 2024 edition'), so by the rustc-version precedent this is first-party with partial methodology: C, not A.
- **Verifier notes:** Language mismatch: this came from a search filtered to C++, but Wisp is a Rust NATS-protocol server. It is judged on its merits. The claimed tier A is not supported with only 2 stars and an unpinned toolchain. The numbers are real and well documented (env hashes, alternating server order, warmups), so keep it at C, tagged reference-only (no license).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/iamd3vil/wisp>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/REPORT.md>
  - <https://raw.githubusercontent.com/iamd3vil/wisp/main/profiling/compare/fanout1000/REPORT.md>
  - <https://raw.githubusercontent.com/iamd3vil/wisp/main/profiling/compare/fanout1000/environment.json>
  - <https://raw.githubusercontent.com/iamd3vil/wisp/main/profiling/bench/README.md>
  - <https://raw.githubusercontent.com/iamd3vil/wisp/main/Cargo.toml>
  - <https://raw.githubusercontent.com/iamd3vil/wisp/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/iamd3vil/wisp>
  - <https://github.com/iamd3vil/wisp/blob/main/README.md>
  - <https://github.com/iamd3vil/wisp/blob/main/Cargo.toml>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/environment.json>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/fanout1000/summary.json>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/operations/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/path-regression/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/multipublisher-contention/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/multipublisher-batching/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/2026-09-08/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/core-security/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/slow-consumer-policy/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/improvements/REPORT.md>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/compare/improvements/protocol.json>
  - <https://github.com/iamd3vil/wisp/blob/main/profiling/bench/README.md>
  - <https://github.com/iamd3vil/wisp/blob/main/MULTITHREADED_STRESS_HANDOFF.md>
  - <https://github.com/iamd3vil/wisp/blob/main/docs/operations.md>
  - <https://github.com/iamd3vil/wisp/blob/main/docs/security.md>
  - <https://github.com/iamd3vil/wisp/blob/main/src/main.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/handler.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/dispatch_cache.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/outbound.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/server.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/protocol.rs>
  - <https://github.com/iamd3vil/wisp/blob/main/src/command.rs>
  - <https://github.com/iamd3vil/wisp/commits/main>
  - <https://github.com/iamd3vil/wisp/issues?q=is%3Aissue>
  - <https://github.com/iamd3vil/wisp/releases>
  - <https://github.com/iamd3vil/wisp/tags>
  - <https://hn.algolia.com/api/v1/search?query=iamd3vil%2Fwisp&restrictSearchableAttributes=url>
  - <https://hn.algolia.com/api/v1/search?query=wisp%20nats%20rust>
  - <https://crates.io/api/v1/crates/submap>
  - <https://crates.io/api/v1/crates/wisp>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/iamd3vil/wisp`) · [data/wave6/enrich/raw/github_com_iamd3vil_wisp.json](../../../data/wave6/enrich/raw/github_com_iamd3vil_wisp.json) (enrichment confidence 0.6)

</details>
