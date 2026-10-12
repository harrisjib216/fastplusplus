# StrangeQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Single-node Go AMQP 0.9.1 broker speaking RabbitMQ's wire protocol; author measures 1.1-4.5x RabbitMQ 4.3's durable, confirmed throughput.

| | |
|---|---|
| **Beats** | RabbitMQ |
| **Claimed result** | 1.10x-4.48x higher end-to-end consumed msg/s than RabbitMQ 4.3 across tested workloads (1 pub/1 con: 1.67x; 10 pub/10 con: 4.48x; 30 pub/30 con: 4.41x; 64 KB body: 1.10x) |
| **Workload** | Durable queues with persistent messages and publisher confirms (up to 1000 unconfirmed publishes in flight per producer, the perftest default), fsync enabled on both brokers, 1 KB bodies (plus one 64 KB run), 1/10/30 producers with the same number of consumers, 20-second runs, consumer prefetch 100, manual acks. Figures are steady-state medians of the per-second consumed rate. Both brokers were driven by the same amqp091-go-based perftest client, and the queue was declared with no x-arguments, so RabbitMQ used its default classic queue type. |
| **Metric** | throughput |
| **Hardware** | Apple Silicon, 16 cores (RabbitMQ run in an OrbStack ARM64-native container; StrangeQ run host-native) |
| **Adoption** | 5 stars |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/maxpert/strangeq) · [benchmark](https://github.com/maxpert/strangeq#performance) |

## Verdict

On one 16-core Apple Silicon Mac (chip model and Go version not stated), the author ran RabbitMQ 4.3 (default classic queue, in an OrbStack ARM64 Linux container; the README does not say whether the container's fsyncs reach the host disk) and host-native StrangeQ under the same amqp091-go perftest: one durable queue, persistent 1 KB messages, confirms with up to 1000 in flight per producer, fsync on, prefetch 100, 20 s runs, median per-second consumed rate. StrangeQ was 1.67x RabbitMQ at 1 producer/1 consumer and about 4.4x at 10/10 and 30/30, mostly because RabbitMQ fell from 64.5K to about 25K msg/s while StrangeQ stayed at 107-114K; with 64 KB bodies it was 1.10x.

## Use it when

- Go services or CI suites that need a real AMQP 0.9.1 broker without an Erlang runtime or Docker: embed it in the process or ship one static binary (release builds exist for linux-386/amd64/arm64 and darwin-amd64/arm64).
- Single-node, durable, publisher-confirm workloads where many producers feed one queue with small (\~1 KB) messages. In the author's table StrangeQ holds about 107-114K msg/s at 10-30 producers, while RabbitMQ's default classic queue drops to about 24-25K.
- Integration tests for code written against RabbitMQ clients, where a quick-starting in-process broker matters more than full RabbitMQ feature parity. The repo has a conformance target (make conformance-rabbitmq) that checks behavior against RabbitMQ 4.3.
- Teams that want to profile and debug the broker with standard Go tools (net/http/pprof, go tool pprof) and scrape Prometheus metrics, instead of using Erlang tooling.

## Skip it when

- Anything that needs clustering, replication or HA; the README lists these as not implemented. It does not mention quorum queues, streams, or plugins such as shovel or federation.
- Apps that depend on priority queues (x-max-priority), consumer priorities, lazy queues, global QoS, prefetch_size &gt; 0 (rejected with 540), SASL EXTERNAL, connection.secure, or the management UI/CLI.
- Large-message workloads: with 64 KB bodies the author's lead shrinks to 1.10x.
- Production systems where the durability track record matters. The Show HN says an LLM wrote the code; it has one maintainer, 5 stars and no third-party bug reports. Fixes for a WAL read-path deadlock and for acknowledged records being served again from the segment tier landed in August 2026, after the benchmark was run.
- Code that relies on RabbitMQ edge semantics the README lists as divergent. Zero-TTL messages are dropped when no consumer is ready. A malformed per-message expiration is treated as no TTL. reject-publish is not enforced inside a transaction. A mandatory publish to a full reject-publish queue is returned with code 312.

## How it is fast

All queues share one write-ahead log whose writer goroutine does drain-then-flush group commit: every record that queued up while the previous fsync ran (up to 1000) goes out in one write and one fdatasync (Linux) or os.File.Sync (other OSes), and a publish is confirmed only after its batch is synced. Confirms are batched too: each channel tracks a contiguous durable watermark with atomics, and a per-connection flusher sends a single basic.ack with multiple=true for the whole range. Each queue keeps an in-memory ring of message pointers where the slot is the delivery tag masked to the ring size, claimed with a per-slot CAS (64K slots by default); messages spill to the WAL at 80% full and are later checkpointed to segment files. On the connection side, separate reader/processor goroutines and a dedicated ack goroutine feed batched deliveries that go out as one write per batch (writev for bodies of 32 KB or more), with frames pooled via sync.Pool.

## Compared with alternatives

Pick StrangeQ when you want an AMQP 0.9.1 broker you can embed in a Go program; it is the only catalogued sibling benchmarked directly against RabbitMQ 4.3 on durable, confirmed traffic. Prefer LavinMQ (AMQP 0-9-1 plus MQTT, about 1K stars, actively developed) when maturity matters, and skip SocketPro if you must keep AMQP clients, since its RabbitMQ win comes from its own C++ framework (repo last pushed 2023).

## Integration

| | |
|---|---|
| **Form** | module (Go module github.com/maxpert/amqp-go in src/amqp-go of the strangeq repo; also prebuilt server binaries) |
| **Dependencies** | go.uber.org/zap, knadh/koanf (yaml/env/file), prometheus/client_golang, RoaringBitmap/roaring, fxamacker/cbor, HdrHistogram/hdrhistogram-go, golang.org/x/crypto, x/sys, x/sync, gopkg.in/yaml.v3 (plus rabbitmq/amqp091-go for perftest/tests and stretchr/testify for tests) |
| **Minimum toolchain** | Go 1.25.1 (go.mod directive) |
| **Platforms** | Linux (uses fdatasync) and macOS (uses os.File.Sync). Release binaries cover linux-386/amd64/arm64 and darwin-amd64/arm64. There are Windows-specific source files but no Windows release binary. |
| **Thread safety** | The broker is internally concurrent: separate reader and processor goroutines per connection, a dedicated ack goroutine, and one shared WAL writer goroutine. Thread-safety of the embedding API is not documented. |
| **Drop-in for the baseline** | partial — AMQP 0.9.1 clients connect unchanged to a single node, but there is no clustering/HA, priority queues, consumer priorities, lazy queues, global QoS, SASL EXTERNAL or management UI/CLI, and the README documents a few behavioral divergences |

## Gotchas

- The module path in go.mod (github.com/maxpert/amqp-go) does not match the repo, and proxy.golang.org returns 'not found' for it. So the README's `go install github.com/maxpert/amqp-go/cmd/amqp-server@latest` and plain library imports do not resolve: clone and build in src/amqp-go, or use a replace directive.
- The latest release, v0.10.0 (2026-07-02), predates both the benchmarked build (measured 2026-07-14) and the August 2026 data-loss and deadlock fixes. Build from main if you want the benchmarked and fixed code.
- The WAL format v4 is a deliberate clean break: files from older versions are rejected with ErrUnsupportedWALVersion. The --unsafe-recovery flag lets the broker start but discards the unparseable file, so drain queues before upgrading across formats.
- The README says a bare `amqp-server` runs 'in-memory', but DefaultConfig writes to ./data with fsync and per-record CRC32 turned on (the sample config puts the CRC cost at about 8% CPU; fsync:false is an opt-in that transactions ignore). Each queue keeps unacked messages in its RAM ring (64K slots by default, 262144 in the README's production example) and spills to the WAL at 80% full.

## Known shortcomings

- The 1.10-4.48x vs RabbitMQ 4.3 is the author's own README benchmark comparing classic queues with different fsync settings, container vs native; RabbitMQ is not a listed baseline; 5 stars, AI-assisted.
- Lopsided benchmark: RabbitMQ ran in an OrbStack Linux container while StrangeQ ran native; the \~4.4x comes mostly from RabbitMQ falling to \~25K msg/s at 10-30 producers on one queue (only 1.10x with 64 KB bodies). No clustering/HA, priority/lazy queues, global QoS or management UI. LLM-written, one maintainer; a WAL deadlock and acked-message redelivery were fixed in 2026-08, after the July bench and after the latest release v0.10.0; WAL v4 cannot read older WAL files (--unsafe-recovery discards them); the README's go install is broken (module path not resolvable).

## Caveats and trade-offs

First-party benchmark on one Apple Silicon Mac; no chip model or Go version is stated. There is an environment asymmetry: RabbitMQ 4.3 ran in an OrbStack ARM64 Linux container with in-container storage, while StrangeQ ran host-native on macOS. The disk and fsync paths therefore differ, which could favour StrangeQ. The comparison is single-node against a default-configured RabbitMQ classic queue; StrangeQ has no clustering or HA. Numbers were measured 2026-07-14. The 'I used AI to build StrangeQ' wording comes from the author's Show HN title (2025-10-31), not the README: the author says an LLM wrote the code. Adoption is very low (5 stars).

Only implements a subset of AMQP 0.9.1 (README describes it as AI-assisted, early-stage); RabbitMQ tested containerized (not emulated, but still an extra virtualization layer) while StrangeQ ran host-native, an asymmetry the author acknowledges; durability model (WAL fsync) differs in maturity/track record from RabbitMQ's.

## Maintenance

Actively developed by one maintainer (last commit 2026-08-29, many July-August commits fixing races, deadlocks and a data-loss path) and MIT-licensed, but it has 5 stars, no outside issues, and a latest release older than the fixes: fine for tests and experiments, unproven in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section has a head-to-head table against RabbitMQ 4.3: 64,532 vs 108,000 msg/s (1.67x), 25,381 vs 113,667 (4.48x), 24,232 vs 106,906 (4.41x), and 21,157 vs 23,217 at 64 KB (1.10x). The benchmark client is public (src/amqp-go/cmd/perftest/main.go) with reproduce commands, but the hardware is given only as 'Apple Silicon, 16 cores' with no chip model, and no Go toolchain version is stated, so this is first-party evidence with partial methodology: tier C.
- **Verifier notes:** The claimed_speedup numbers match the README exactly, and license (MIT), stars (5), last commit (2026-08-29), non-fork and non-archived status all check out. The only real correction is where the AI-built quote comes from: it is the HN Show HN title (item 45767055), not the README. Otherwise the record is accurate.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/maxpert/strangeq>
  - <https://github.com/maxpert/strangeq#performance>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/cmd/perftest/main.go>
  - <https://hn.algolia.com/api/v1/search?query=strangeq&tags=story>
- **Sources the enricher read:**
  - <https://github.com/maxpert/strangeq>
  - <https://github.com/maxpert/strangeq#performance>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/go.mod>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/storage/atomic_ring.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/storage/wal_manager.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/storage/fdatasync_linux.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/storage/fdatasync_other.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/storage/syncdir_other.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/server/confirm_batching.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/config/config.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/config.sample.yaml>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/cmd/perftest/main.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/examples/simple_server.go>
  - <https://github.com/maxpert/strangeq/blob/main/src/amqp-go/docs/rabbitmq-tests.md>
  - <https://github.com/maxpert/strangeq/blob/main/CHANGELOG.md>
  - <https://github.com/maxpert/strangeq/releases/tag/v0.10.0>
  - <https://github.com/maxpert/strangeq/pulls?q=is%3Apr>
  - <https://github.com/maxpert/strangeq/issues?q=>
  - <https://github.com/maxpert/strangeq/commits/main>
  - <https://github.com/maxpert/strangeq/commit/3e94de298a7d138f8b89050f4fd7adb0b516d24a>
  - <https://github.com/search?q=repo%3Amaxpert%2Fstrangeq+AvailableChannelBuffer&type=code>
  - <https://proxy.golang.org/github.com/maxpert/amqp-go/@v/list>
  - <https://proxy.golang.org/github.com/maxpert/amqp-go/@latest>
  - <https://hn.algolia.com/api/v1/items/45767055>
  - <https://hn.algolia.com/api/v1/search?query=strangeq>
  - <https://github.com/cloudamqp/lavinmq>
  - <https://github.com/udaparts/socketpro>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/maxpert/strangeq`) · [data/wave6/enrich/raw/github_com_maxpert_strangeq.json](../../../data/wave6/enrich/raw/github_com_maxpert_strangeq.json) (enrichment confidence 0.45)

</details>
