# IKV (Inlined Key-Value Store)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Embedded, eventually consistent Rust key-value store for ML features that serves reads in-process instead of calling a remote Redis.

| | |
|---|---|
| **Beats** | Redis (AWS ElastiCache, Redis Cluster) |
| **Claimed result** | In-memory GET with 16 client threads over 1M docs (150 B values), at 100K QPS: IKV avg 3.13 us / p50 2.89 / p99 5.65 vs a 16-shard AWS ElastiCache Redis 7.1 cluster at avg 319 us / p50 305 / p99 514 (\~100x lower latency, derived from page data). IKV also held 1M and 3M QPS, which Redis could not reach from the single client. In the tiered test (1:4 memory:data, Zipfian), IKV averaged 118.25 us vs 225.06 us for in-memory 1-shard Redis (\~1.9x, derived from page data), but IKV's p99 was worse (747.65 us vs 348.88 us). The \~100x gap is mostly the network round trip that embedding removes (an in-process lookup vs a remote ElastiCache call over TCP), not a faster storage engine. |
| **Workload** | Custom Java multithreaded client (inlinedio/ikv-java-client benchmarks; JedisCluster for Redis) issuing blocking single-field GETs at fixed loads (25K/50K/100K/1M/3M QPS). It used 16 threads, 1M docs (\~15 B keys, 3x50 B fields) and a 30 s window, against IKV embedded in the client process and a 16-shard ElastiCache Redis 7.1 cluster in the same AZ. A second test used tiered storage with Zipfian keys, 6000 B values and 16 IKV threads, against a 1-thread, 1-shard ElastiCache Redis. |
| **Metric** | latency |
| **Hardware** | In-memory test: client and embedded IKV on AWS c5.4xlarge (16 vCPU, 32 GiB). Redis was AWS ElastiCache Redis 7.1 with 16 shards (1 primary, 0 replicas each) on cache.r5.xlarge nodes in the same AZ (us-west-2a). Tiered test: client on c5d.4xlarge (400 GiB local SSD) vs 1-shard ElastiCache cache.r6g.xlarge / cache.r6gd.xlarge. CPU model not stated. |
| **Adoption** | 227 stars |
| **Last commit** | 2024-05-14 |
| **Links** | [repository](https://github.com/inlinedio/ikv-store) · [benchmark](https://github.com/inlinedio/ikv-store#benchmarks--100x-faster-than-redis) |

## Verdict

In the in-memory test, 16 Java threads read from IKV embedded in a c5.4xlarge and, through JedisCluster HGET, from a 16-shard ElastiCache Redis 7.1 cluster (cache.r5.xlarge) in the same AZ, on 1M docs with three 50 B fields. IKV averaged about 3 us (p99 about 5-6 us) versus about 320 us (p99 about 515-530 us) for Redis at 25K-100K QPS, and it also held 1M and 3M QPS. The tiered test (c5d.4xlarge local SSD, Zipfian, 6000 B docs, 16 IKV threads vs 1 Redis thread, different dataset sizes per system) gave IKV avg 118 us / p99 748 us at 1:4 memory:data, versus avg 225 / p99 349 us for in-memory single-shard Redis. No CPU model, compiler or flags were given, and most of the gap is the removed network hop.

## Use it when

- Read-heavy online ML feature serving (recommendation, search, ranking), where every app host can hold its partition locally and a few milliseconds of staleness is fine.
- Per-lookup budgets in single-digit microseconds that a same-AZ network round trip (about 300 us to ElastiCache in the vendor's test) cannot meet.
- Feature sets 2-4x larger than RAM with skewed access, on hosts with local NVMe. The vendor measured avg 53 us (1:2) and 118 us (1:4 memory:data) with sub-millisecond p99.
- Java, Go or Python services that would otherwise put a remote Redis or DynamoDB in front of static or slowly changing features.
- As an MIT-licensed reference design for an embedded read replica: hash index, append-only mmap and stream replay from a snapshot plus Kafka.

## Skip it when

- You need read-after-write consistency, atomic updates, TTL or eviction, or Redis data structures. IKV has none of these; reads are eventually consistent.
- You cannot run its data plane. The hosted IKV Cloud is gone, self-hosting is still marked 'coming soon' in the README, and the ikv-cloud code expects Kafka, S3 and a DynamoDB-backed Java gateway with no setup docs.
- Memory is tight or the fleet is large. Every reader holds the whole key-to-offset hash table on heap and a full copy of its partition. Old values are only reclaimed by an offline index-build compaction.
- Tail latency matters on tiered data: at 1:4 memory:data, IKV's p99 was 747.65 us against 348.88 us for in-memory single-shard Redis.
- You want production maturity or a Rust API. It stopped at v0.0.36, nearly all commits are by one developer, and the core crate is built only as a cdylib behind C/JNI entry points, with no Rust-facing API.

## How it is fast

Reads never leave the process. The primary key is hashed with fxhash to one of 16 RwLock-guarded segments. There, an in-memory std HashMap maps the key to a per-field vector of offsets, and the value is sliced out of an append-only memory-mapped file (2-byte type tag, then fixed-width bytes or a varint length). When data exceeds RAM it spills through the OS page cache, which keeps skewed (Zipfian) reads on local SSD under a millisecond on average. Writes are applied asynchronously by a background Kafka consumer, so the read path pays nothing for replication or consensus.

## Compared with alternatives

Garnet, Dragonfly, KeyDB and Pogocache are shared network servers benchmarked on server throughput against Redis, and Caffeine is an in-process JVM heap cache you fill yourself. Pick IKV only if you want every app host to hold a stream-synced, disk-spillable read replica of a feature dataset and will run and maintain its Kafka/S3 data plane yourself. Otherwise a sibling is the safer choice.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Core (Rust): rdkafka (librdkafka with vendored OpenSSL), tokio, aws-sdk-s3, memmap2, protobuf, jni, fxhash, flate2/tar. Runtime: a Kafka topic per store, an S3 bucket for base-index snapshots, and a gRPC gateway for config and writes. Python SDK: boto3, cffi, grpcio, protobuf. |
| **Minimum toolchain** | Rust 2021 edition (MSRV not documented); Python SDK requires Python 3.8+; Go and Java minimums not documented. |
| **Platforms** | The SDK loaders only know prebuilt binaries for linux-x86_64, linux-aarch64 and macOS aarch64 (no Windows, no Intel Mac). 64-bit only: the offset table uses usize and is commented as 32-bit incompatible. The prebuilt binary bucket no longer exists, so you must build from source. |
| **Thread safety** | One reader handle is shared across threads. Lookups take read locks on the schema and on one of 16 RwLock segments. A background Kafka consumer thread takes per-segment write locks to apply each write. |
| **Drop-in for the baseline** | false. It is a different architecture and API: typed document/field getters in the Java/Go/Python SDKs, a separate writer that goes through the data plane, eventual consistency, and no Redis protocol. |

## Gotchas

- The 'no network calls' claim covers steady-state reads only. Opening a reader fetches config over gRPC from gateway.inlined.io, may download a base-index tarball from S3 (region hard-coded to us-west-2), and blocks until its Kafka partition is consumed to the high watermark. All vendor endpoints are now dead, so readers cannot start without code changes or a self-hosted data plane.
- Supply-chain risk: the Go and Python SDKs list a public S3 bucket named ikv-binaries, download the highest-versioned libikv from it, and dlopen it. That bucket now returns NoSuchBucket, so anyone who re-creates the name could serve the code the SDKs load. Pin and build your own binary. Also, the README's inlined.io links now redirect to an unrelated site flagged as potentially malicious.
- The Kafka consumer sets enable.ssl.certificate.verification=false while it authenticates with the account passkey over SASL/SCRAM. In a self-hosted setup, override this with the kafkaprop_ config prefix.
- Durability and robustness are thin. mmap.flush() is commented out ('TODO(critical): this fails on macos'), so value bytes are synced only when the OS writes pages back. The JNI and C entry points unwrap() or expect() on inputs and config. A comment warns that a panic in the consumer thread is not surfaced.

## Known shortcomings

- The \~100x is mostly the removed network hop: an embedded store on c5.4xlarge vs a remote 16-shard ElastiCache r5.xlarge cluster, not a faster engine. The tiered '2x' is average only; IKV's p99 is worse (748 vs 349 us) (verifier downgrade).
- SECURITY: the Go and Python SDKs download and dlopen libikv from the S3 bucket 'ikv-binaries', which no longer exists and whose name can be re-registered by anyone, so installing the SDKs could load an attacker's binary; do not use the published SDKs. The vendor is gone (inlined.io flagged as malicious; docs and gateway have no DNS), so readers can't start without self-hosting or patching. Kafka TLS certificate checks are off; the mmap flush is commented out; JNI unwraps inputs. Eventual consistency, no TTL/eviction/Redis API, full key-to-offset table on each reader's heap, append-only with offline compaction. Core is a cdylib (no Rust API); prebuilt for linux x64/arm64 and mac arm64 only; v0.0.36, stale since 2024-05.

## Caveats and trade-offs

The full report (Google Doc, readable through its txt export) gives instance types but no CPU model, compiler or flags. The comparison is embedded (in-process, no network) vs networked (remote ElastiCache over TCP through the Jedis client). That makes it a valid deployment-architecture comparison for read-heavy, eventually consistent ML feature serving, but not a like-for-like engine comparison. Most of Redis's \~300 us is network round trip plus client overhead. A fair engine test would use Redis over localhost or a Unix socket, or another embedded KV. The tiered '2x faster than Redis' holds for average latency only: p99 is worse for IKV (747.65 vs 348.88 us). The tiered test used 16 IKV threads vs 1 Redis thread, and the report's text and table disagree on thread counts. A single client machine drove the load. The repo is stale (last commit 2024-05-14).

IKV is an embedded/in-process library colocated with the application (no network hop) rather than a shared remote cache, so much of the 100x gap is network round-trip elimination rather than a faster core engine; eventual consistency instead of Redis's stronger read-after-write guarantees; requires a separate data-plane (streams/object storage) to keep embedded replicas in sync

## Maintenance

The project has been stale since v0.0.36 (2024-05-14) and is effectively orphaned. As of 2026-09-26, inlined.io redirects to an unrelated flagged site, docs.inlined.io and gateway.inlined.io do not resolve, and the SDKs' binary bucket is gone. Using it now means building libikv from source and self-hosting or patching out the data plane, though the MIT-licensed Rust index is small enough to study or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers. The README table and the linked Google Doc report give AWS instance types, dataset, thread counts and time windows. The benchmark tooling is public in inlinedio/ikv-java-client (src/main/java/io/inlined/benchmarks, MultiThreadedRunner, with a JedisCluster client for Redis), but no CPU model, compiler or flags are stated, so C.
- **Verifier notes:** Judgment on the embedded-vs-networked comparison: it is a legitimate real-use-case latency win, but '100x faster than Redis' mostly measures removing the network hop, not IKV's engine against Redis's engine. The claim is overstated as a library-speed claim. Tier stays C. I was able to read the Google Doc report, which fills in hardware and methodology. Metadata checks out: MIT, 227 stars, last commit 2024-05-14, stale, not a fork. Not notable (&lt;1k stars), but it has real numbers against a named baseline, so it is not a reject.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/inlinedio/ikv-store>
  - <https://github.com/inlinedio/ikv-store#benchmarks--100x-faster-than-redis>
  - <https://docs.google.com/document/d/1aDsS0V-AybpvXEwblBlahGLpKH5NmUmi6mTWGsbABGk/export?format=txt>
  - <https://github.com/inlinedio/ikv-java-client>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/README.md>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/clients/RedisSingleGetDBClient.java>
- **Sources the enricher read:**
  - <https://github.com/inlinedio/ikv-store>
  - <https://github.com/inlinedio/ikv-store#benchmarks--100x-faster-than-redis>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/Cargo.toml>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/build.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/lib.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/index/ckv.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/index/ckv_segment.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/index/schema_store.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/controller/main.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/controller/index_loader.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/controller/index_builder.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/kafka/consumer.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/kafka/processor.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/ffi/api.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/ffi/c_api.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv/src/ffi/jni_api.rs>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv-go-client/bin_manager.go>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv-go-client/native_reader_v2.go>
  - <https://github.com/inlinedio/ikv-store/blob/master/ikv-python-client/src/ikvpy/bin_manager.py>
  - <https://github.com/inlinedio/ikv-store/blob/master/docs/docs/main.md>
  - <https://github.com/inlinedio/ikv-store/blob/master/docs/docs/onboarding.md>
  - <https://github.com/inlinedio/ikv-store/blob/master/docs/docs/data-modeling.md>
  - <https://github.com/inlinedio/ikv-store/issues>
  - <https://github.com/inlinedio/ikv-store/issues/143>
  - <https://github.com/inlinedio/ikv-store/issues/126>
  - <https://github.com/inlinedio/ikv-store/pull/182>
  - <https://github.com/inlinedio/ikv-store/pull/186>
  - <https://github.com/inlinedio/ikv-store/releases>
  - <https://docs.google.com/document/d/1aDsS0V-AybpvXEwblBlahGLpKH5NmUmi6mTWGsbABGk/export?format=txt>
  - <https://github.com/inlinedio/ikv-java-client>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/README.md>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/clients/IKVSingleGetDBClient.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/clients/RedisSingleGetDBClient.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/benchmarks/runner/MultiThreadedRunner.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/clients/DirectJNIBenchmarkingClient.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/clients/IKVConstants.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/clients/IKVClientFactory.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/src/main/java/io/inlined/clients/ServerSuppliedConfigFetcher.java>
  - <https://github.com/inlinedio/ikv-java-client/blob/master/build.gradle>
  - <https://inlined.io>
  - <https://docs.inlined.io>
  - <https://ikv-binaries.s3.us-west-2.amazonaws.com/?list-type=2&prefix=release/>
  - <https://pypi.org/pypi/ikvpy/json>
  - <https://jitpack.io/api/builds/io.inlined/ikv-java-client/latest>
  - <https://hn.algolia.com/api/v1/items/39485921>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/inlinedio/ikv-store`) · [data/wave6/enrich/raw/github_com_inlinedio_ikv_store.json](../../../data/wave6/enrich/raw/github_com_inlinedio_ikv_store.json) (enrichment confidence 0.82)

</details>
