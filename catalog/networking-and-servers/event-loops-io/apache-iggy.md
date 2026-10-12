# Apache Iggy (thread-per-core io_uring backend, v0.7.0)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust message-streaming server whose v0.7.0 rewrite on thread-per-core io_uring (compio) cuts tail latency versus its Tokio/epoll build.

| | |
|---|---|
| **Beats** | epoll (via Tokio, as used in Iggy v0.5.0) |
| **Claimed result** | 32 producers x 32 streams (80 GB / 80M msgs, 1 GB/s rate limit): P95 3.77 -&gt; 1.62 ms (+57%), P99 4.52 -&gt; 1.82 ms (+60%), P999 5.43 -&gt; 2.38 ms (+56%), P9999 27.52 -&gt; 11.83 ms (+57%); 16x16: P95 2.52 -&gt; 1.82 ms (+28%), P9999 86.30 -&gt; 7.17 ms (+92%); 8x8: P95 1.36 -&gt; 1.47 ms (-8%, worse), P99 1.52 -&gt; 1.57 ms (-3%, worse), P9999 34.00 -&gt; 6.51 ms (+81%). fsync 32 partitions: throughput 931 -&gt; 1,102 MB/s (+18%), P95 33.98 -&gt; 18.49 ms (+46%); fsync 16 partitions: 843 -&gt; 992 MB/s (+18%), P95 18.00 -&gt; 9.98 ms (+45%). Non-fsync throughput stays \~1,000 MB/s because the runs are rate-limited. |
| **Workload** | iggy-bench pinned-producer over TCP, 1000-byte messages, 250 msgs/batch: 8x8 (20 GB), 16x16 (40 GB) and 32 producers x 32 streams (80 GB / 80M msgs) at a 1 GB/s rate limit, plus unthrottled fsync (strong consistency) runs at 16 and 32 partitions; compares Iggy v0.5.0 (Tokio) with v0.7.0 (thread-per-core io_uring via compio) |
| **Metric** | latency |
| **Hardware** | AWS i3en.3xlarge: Intel Xeon Platinum 8259CL @ 2.50GHz, 12 cores, \~93 GiB RAM, Ubuntu 24.04, kernel 6.17.0-1007-aws (from the linked benchmarks.iggy.apache.org report JSON) |
| **Adoption** | 4,954 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/apache/iggy) · [benchmark](https://iggy.apache.org/blogs/2026/02/27/thread-per-core-io_uring/) |

## Verdict

The maintainers compared Iggy v0.5.0 (Tokio: epoll for sockets, a blocking thread pool for files) with v0.7.0 (compio io_uring, thread-per-core) using iggy-bench pinned-producer over TCP (1000-byte messages, 250 per batch, 1 GB/s rate limit) on AWS i3en.3xlarge (Xeon Platinum 8259CL, 12 vCPU, Ubuntu 24.04, kernel 6.17), with client and server on separate hosts. At 32x32, P99 fell from 4.52 to 1.82 ms, at 16x16 P99.99 fell from 86.3 to 7.17 ms, and fsync runs gained 18% throughput; the percentiles are averages of per-producer percentiles, each version ran on a different EC2 server/client pair on the same day, the toolchain and flags are not stated, and the two versions differ in far more than the I/O backend.

## Use it when

- You run Iggy on Linux (kernel 5.19+) and care about P99.9/P99.99 write latency more than peak throughput.
- Many partitions and producers per node: the published gap grows from roughly even at 8 producers to 57-60% lower P95-P99 at 32 producers x 32 streams, with P50 also down from 2.21 to 0.77 ms there.
- Durable writes with fsync on every batch where throughput and P95+ matter: the fsync runs show about 18% more throughput and about 45% lower P95 than the Tokio build.
- Dedicated hosts where one pinned shard per core is acceptable and the kernel and seccomp policy allow io_uring.
- You are on Iggy 0.5.x or earlier (Tokio) and want a lower write tail without changing client code.

## Skip it when

- Small deployments of about 8 partitions or producers: P95 and P99 were 8% and 3% worse than the Tokio build there; only P99.9 and above improved.
- Median-sensitive fsync-per-batch writes: the dashboard reports show P50 rising from 1.53 to 3.54 ms (16 partitions) and from 2.66 to 6.25 ms (32 partitions) on v0.7.0, although mean and P95+ fell; the blog tables start at P95.
- You need more peak throughput: the non-fsync comparisons were capped at 1 GB/s by the benchmark's rate limit, so no throughput gain is shown outside the fsync runs.
- Skewed traffic with a few hot partitions: shards do not steal work, and the blog lists hot-shard balancing (e.g. splitting a partition across shards) as unsolved future work.
- Native Windows (the v0.7.0 server has compile_error!("iggy-server doesn't support windows."); use WSL or Docker), containers with Docker's default seccomp profile, or kernels older than 5.19.

## How it is fast

Completion-based io_uring replaces readiness-based epoll for sockets and, more importantly, replaces Tokio's blocking thread pool (up to 512 threads) for file writes and fsync. Each shard is a pinned thread that owns a set of partitions assigned by hash, so the data plane has no work stealing and no cross-thread locks; when a client writes to an explicit partition on the wrong shard, its TCP socket fd is handed to the owning shard. Stream and topic metadata has a single writer (shard 0) that publishes to the other shards through a left-right structure fed by flume channels (the 'shared something' design); the rings are created with IORING_SETUP_COOP_TASKRUN and no helper thread pool.

## Compared with alternatives

Pick Iggy when you want a finished message-log server that already applies the Seastar-style thread-per-core design in Rust; monoio or ringline are the runtimes to build your own io_uring server on, and Seastar is the C++ framework Iggy's design follows.

## Integration

| | |
|---|---|
| **Form** | built binary (iggy-server, Docker image apache/iggy); not a library |
| **Dependencies** | compio 0.18 with the io-uring driver (at tag server-0.7.0), left-right, flume, DashMap, mimalloc (default global allocator), hwlocality/hwloc for NUMA-aware core allocation |
| **Minimum toolchain** | Rust 1.93.0 pinned by rust-toolchain.toml at tag server-0.7.0 (edition 2024; current master pins 1.98.0 with rust-version 1.95); Linux kernel 5.19+ per the Docker docs |
| **Platforms** | Linux for io_uring; macOS builds use compio's non-io_uring driver and have had shard startup panics on some targets (Intel/Rosetta); native Windows unsupported at v0.7.0; CPU architecture requirements not documented |
| **Thread safety** | Server process: one pinned shard thread per core (sharding cpu_allocation, default numa:auto); each partition is owned by one shard; stream/topic metadata has a single writer (shard 0) with left-right readers on the other shards |
| **Drop-in for the baseline** | partial - a server upgrade from Iggy 0.5.x (Tokio) to 0.7.0, not a swappable event loop; the host kernel and container runtime must allow io_uring |

## Gotchas

- Docker needs --security-opt seccomp=unconfined (or a custom profile allowing io_uring_setup, io_uring_enter and io_uring_register) and --ulimit memlock=-1:-1; the README also lists --cap-add=SYS_NICE. The server prints these hints when ring creation fails with EPERM or ENOMEM.
- Idle servers can show IO pressure (PSI) and iowait near 100% because shards parked in io_uring_enter are counted as iowait on kernels 6.5+. Issue #3507 (open) calls it cosmetic, but it breaks iowait-based alerting.
- Socket migration only applies to explicit partition ids: Balanced and MessagesKey partitioning skip the fd handoff and are routed to the owning shard instead. The benchmark used pinned producers, which is the migration-friendly case.
- io_uring alone did not produce the tail gain: the intermediate v0.6.1 shared-nothing build on the dashboard had P99.99 of 208 ms at 32x32 (v0.5.0: 27.5 ms). The drop came with v0.7.0's shared-metadata redesign.

## Known shortcomings

- In the fsync runs v0.7.0's median is \~2.3x worse than v0.5.0 (P50 1.53 to 3.54 ms at 16 partitions, 2.66 to 6.25 ms at 32), hidden because the blog tables start at P95. Baseline and new version ran on different EC2 server/client pairs (same type, day and kernel); the recorded hardware is the client host. 'P95/P99' are averages of per-producer percentiles, not percentiles over all requests. io_uring alone didn't deliver the gain: the intermediate thread-per-core io_uring build (v0.6.1-edge.4) had P99.99 of 208 ms vs 27.5 ms for v0.5.0; the win came with v0.7.0's shared-metadata redesign, so this is whole-server v0.5 vs v0.7, not epoll vs io_uring (Tokio's file I/O/fsync used a blocking thread pool). Toolchain/flags unstated. Non-fsync runs capped at 1 GB/s show no throughput gain. The benchmark uses pinned producers, the easiest case (balanced/keyed partitioning routes across cores). Needs Linux 5.19+; Docker needs seccomp=unconfined, unlimited memlock, SYS_NICE; Windows build broken; macOS startup panics (#3047, #3788); idle iowait artifact on 6.5+ (#3507). Server 0.9.0 (2026-09-18) is current.

## Caveats and trade-offs

First-party engineering blog; hardware/OS/kernel/bench commands confirmed through the dashboard report API, but the Rust toolchain and build flags are unstated. The baseline is Iggy's own earlier Tokio build (epoll readiness model), not a standalone epoll loop. Latency is compared at a fixed 1 GB/s rate limit, so throughput is equal by construction outside the fsync runs. At 8 producers, P95/P99 are slightly worse on v0.7.0 (-8%/-3%); the gains grow with partition count.

Thread-per-core io_uring rewrite changes internal architecture; raw throughput similar to prior epoll version, gains are in tail latency not headline throughput

## Maintenance

Active Apache Software Foundation project (Apache-2.0) with daily commits; server 0.9.0 (September 2026) has since added VSR clustering on the same shard design, so v0.7.0 is no longer the latest release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party blog comparing v0.5.0 (Tokio, readiness/epoll-based) with v0.7.0 (compio thread-per-core io_uring). The linked dashboard reports (benchmarks.iggy.apache.org/api/benchmark/full/&lt;uuid&gt;) give the CPU (Intel Xeon Platinum 8259CL, AWS i3en.3xlarge), OS, kernel and exact iggy-bench commands, and the bench code is public in apache/iggy core/bench. Rust compiler version and build flags are stated nowhere, so it cannot be A, and being first-party it is not B.
- **Verifier notes:** All claimed numbers match the blog's 32x32 and fsync-32 tables exactly. The benchmark dashboard's JSON API (/api/benchmark/full/&lt;uuid&gt;) exposes hardware and params that the JS-rendered UI hid. The linked reports also include some 0.6.1-edge.4 runs.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compared_against_cpp_std_directly`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://iggy.apache.org/blogs/2026/02/27/thread-per-core-io_uring/>
  - <https://github.com/apache/iggy>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/0ac461f6-59b3-4822-8de0-3bd1a662966e>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/2c6a0f6a-fb4d-4e84-8ac0-bfca60c75b21>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/402df805-94f3-4a78-9a2d-a4bda9d51655>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/481c7504-177a-4df8-b771-cda1edbeeaa0>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/48343378-1052-44a4-b1a6-0b06b9436127>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/54142b7a-8dfd-4803-8ff1-adb5bce8d5df>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/5f056d32-4856-461d-92c8-439e406cc49e>
- **Sources the enricher read:**
  - <https://iggy.apache.org/blogs/2026/02/27/thread-per-core-io_uring/>
  - <https://github.com/apache/iggy>
  - <https://raw.githubusercontent.com/apache/iggy/master/README.md>
  - <https://raw.githubusercontent.com/apache/iggy/master/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/iggy/master/core/server/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/iggy/master/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/apache/iggy/master/core/server/config.toml>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/Cargo.toml>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/config.toml>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/lib.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/main.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/bootstrap.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/diagnostics.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/shard/mod.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/binary/handlers/messages/send_messages_handler.rs>
  - <https://raw.githubusercontent.com/apache/iggy/server-0.7.0/core/server/src/tcp/tcp_socket.rs>
  - <https://github.com/apache/iggy/releases>
  - <https://github.com/apache/iggy/issues/2562>
  - <https://github.com/apache/iggy/issues/3507>
  - <https://github.com/apache/iggy/issues/3047>
  - <https://github.com/apache/iggy/issues/3788>
  - <https://github.com/apache/iggy/issues/4178>
  - <https://iggy.apache.org/docs/server/docker>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/b983ec73-43cf-44c4-ab4e-2287c3706fb2>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/fb570d39-d6bb-4eb1-a960-c8e0d16cd5d9>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/0ac461f6-59b3-4822-8de0-3bd1a662966e>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/481c7504-177a-4df8-b771-cda1edbeeaa0>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/88eca6c0-6729-44b0-9843-28125d0ff44a>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/2c6a0f6a-fb4d-4e84-8ac0-bfca60c75b21>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/5f056d32-4856-461d-92c8-439e406cc49e>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/402df805-94f3-4a78-9a2d-a4bda9d51655>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/ddaca68e-8374-499c-bb08-53ad06b164ec>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/54142b7a-8dfd-4803-8ff1-adb5bce8d5df>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/48343378-1052-44a4-b1a6-0b06b9436127>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/6fc5936a-4134-45c4-b8d9-ba962bf47b98>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/cf933d06-8119-4d14-b2ce-7c398dfa0dbf>
  - <https://benchmarks.iggy.apache.org/api/benchmark/full/63607acc-5861-47c7-9673-5c1ce649ed0c>
  - <https://hn.algolia.com/api/v1/search?query=iggy%20io_uring&tags=story&hitsPerPage=10>
  - <https://hn.algolia.com/api/v1/search?query=iggy%20thread-per-core&hitsPerPage=10>
  - <https://hn.algolia.com/api/v1/items/47396417>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/apache/iggy`) · [data/wave5/enrich/raw/github_com_apache_iggy.json](../../../data/wave5/enrich/raw/github_com_apache_iggy.json) (enrichment confidence 0.7)

</details>
