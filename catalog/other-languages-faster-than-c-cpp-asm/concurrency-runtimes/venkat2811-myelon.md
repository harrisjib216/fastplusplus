# Myelon / disruptor-mp (shared-memory ring-buffer IPC transport, Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust LMAX-Disruptor-style shared-memory IPC ring for Linux and macOS; first-party 1 KB ping-pong chart beats Boost.Interprocess and Open MPI.

| | |
|---|---|
| **Beats** | Boost.Interprocess message_queue ('Boost-MQ', C++) and an Open MPI shared-memory ping-pong (C, built with mpicc); the same chart also holds Rust and Java-ecosystem peers (iceoryx2, Aeron through rusteron, shmipc-rs, crossbeam, ZeroMQ). |
| **Claimed result** | Chart labels in assets/bench-pingpong-throughput-1kb.png (1 KB, 1p1c, msgs/sec, log scale): Myelon-Raw mmap 4.9M and shm 4.4M, plus the project's own Disruptor (disruptor-mp) baselines at 4.8M (mmap) and 4.6M (shm). Peers: Crossbeam 2.6M, Rusteron (Aeron) 2.6M, OpenMPI 2.0M, Iceoryx2 1.4M, Boost-MQ 164K, Shmipc 60K, ZeroMQ-IPC 25K, ZeroMQ-IPC-abs 20K, ZeroMQ-TCP 14K. Against Boost-MQ this is about 27x to 30x and against Open MPI about 2.2x to 2.5x (both derived from page data). Against Aeron IPC through rusteron it is about 1.7x to 1.9x (derived from page data). |
| **Workload** | Two-process 1p1c ping-pong of 1 KB messages over shared memory or mmap, reported as messages per second, run by the project's competitive-bench harness (adapters for Boost message queue and Open MPI are small C++/C helper programs under third_party/). |
| **Metric** | throughput |
| **Hardware** | README headline tables: AMD Ryzen 7 5800X (8C/16T, 4.85 GHz boost), 64 GiB DDR4, Ubuntu 22.04, kernel 6.8, via crates/perf-bench; the chart's machine is not stated separately. |
| **Compiler and flags** | Boost-MQ helper (crates/competitive-bench/third_party/boost_pingpong/Makefile): g++ -O3 -std=c++17 -pthread -march=native -flto -DNDEBUG on Linux. Open MPI helper (crates/competitive-bench/third_party/ompi_pingpong/Makefile, pingpong.c): mpicc -O3 -std=c11 -march=native -flto -DNDEBUG. Rust side: workspace profile 'competitive' with opt-level 3, fat LTO, codegen-units 1, panic abort, overflow-checks off and no target-cpu, so only the C/C++ helpers get -march=native. Compiler versions are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: LMAX Disruptor design extended to cross-process IPC with lock-free atomics, no syscalls in the hot path, cache-aligned cursors and busy-spin waiting; the Boost-MQ peer waits on a mutex and condition variable instead of spinning. |
| **Adoption** | 20 stars, 1 fork; crates.io downloads: disruptor-mp about 358, myelon about 242 |
| **Last commit** | 2026-05-21 |
| **Links** | [repository](https://github.com/Venkat2811/myelon) · [benchmark](https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/assets/bench-pingpong-throughput-1kb.png) |

## Verdict

The first-party competitive-bench chart (1 KB, 1p1c ping-pong round trips per second, single run, machine and compiler versions not stated) shows Myelon-Raw at 4.9M (mmap) and 4.4M (shm). Against Open MPI's vader shared-memory path at 2.0M (mpicc -O3 -march=native -flto) that is 2.2-2.5x, and against Boost.Interprocess message_queue at 164K (g++ -O3 -march=native -flto) it is 27-30x. However, the raw client writes only a 64-byte header and reads back only the sequence while the C/C++ peers copy 1 KB each way. The comparable framed 1 KB path runs at 2.45M ops/s on a Ryzen 7 5800X (README), about 1.2x Open MPI (cross-run, derived).

## Use it when

- Rust processes on one Linux or macOS host exchanging small fixed-size messages with sub-microsecond round trips, such as an inference driver feeding worker ranks (the crate's broadcast plus per-rank ping-pong topology).
- One-to-N fan-out of the same data where each consumer must see every message (README perf-bench: 1p4c, 1 KB, mmap, 9.09M ops/s per consumer).
- Hosts where you can dedicate a spinning core to each waiting side and latency matters more than CPU time.
- Replacing Boost.Interprocess message_queue or ZeroMQ IPC between Rust processes, where blocking wakeups or socket syscalls dominate latency.

## Skip it when

- C or C++ endpoints: the roadmap leaves C/C++, Python and Zig bindings unchecked, so a C++ project would need its own FFI layer.
- Several producers writing one ring: only SPSC and SPMC exist; MPSC and MPMC are unchecked roadmap items.
- Windows, which is unsupported.
- CPU-constrained hosts or many mostly idle channels: the headline numbers use busy-spin (100% of a core per waiting side). Block, Sleep and SpinThenYield strategies exist but were not benchmarked against the peers.
- Production systems that need hardened code today. It is at 0.1.0-alpha.2, only 12 of 81 internal unsafe blocks carry SAFETY comments, there are no Miri, ASan or TSan lanes yet, and open issue #20 reports silent data corruption under the default producer configuration.

## How it is fast

It applies the LMAX Disruptor design across processes. A preallocated ring of cache-line-aligned slots lives in shared memory, producer and consumer cursors are atomics on separate cache lines, publishing is a sequence claim with no lock and no syscall, and consumers read the slot in place. The benchmarks run the BusySpin wait strategy, so a handoff costs about one cache-line transfer (README: 130 ns P50 round trip at 64 B on a Ryzen 7 5800X). The Boost peer instead takes an interprocess mutex and condition variable on every send and receive.

## Compared with alternatives

Cynosure RingBuf is an in-process async SPSC ring compared with rigtorp::SPSCQueue, and Tokio and the Go runtimes schedule tasks inside one process. Pick Myelon only when the two endpoints are separate OS processes on one host and you can spare a spinning core; otherwise those siblings, or an in-process channel, avoid the shared-memory setup.

## Integration

| | |
|---|---|
| **Form** | crate (disruptor-mp and myelon on crates.io) |
| **Dependencies** | metrics-rs facade by default; optional bincode, rkyv and flatbuffers codecs and Prometheus or OTLP exporters (feature list in the README; exact dependency trees not checked) |
| **Minimum toolchain** | Rust 1.86 (workspace rust-version), edition 2021 |
| **Platforms** | Linux and macOS (POSIX shm_open or mmap file backends; macOS 31-byte shm name limit enforced); Windows unsupported |
| **Thread safety** | cross-process single-producer rings (SPSC, SPMC); multi-producer modes not implemented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 1 KB chart: the raw path does not move 1 KB. In perf-bench's raw_myelon and raw_ring ping-pong, the client's write_event fills only sequence and two timestamps in the 64-byte header of PingPongEvent&lt;960&gt;, never writes the 960-byte payload, and reads back only response.sequence. The echo process copies the whole slot (\*slot = \*event), but the payload bytes never change and the client never reads them, so about one cache line crosses cores per direction. The Boost helper (message_queue send/receive memcpy), Open MPI (MPI_Send/MPI_Recv of a 1 KB buffer) and rusteron (offer, or try_claim plus copy_from_slice) move the full 1 KB each way. That is why the raw 1 KB result (4.4-4.9M) sits near the README's 64 B raw figure (5.58M).
- The like-for-like Myelon figure is the framed path, which publishes a real 1 KB payload and length-checks the echo: 2.45M ops/s in the README's perf-bench table. That is about 1.2x Open MPI's 2.0M and below rusteron/Aeron's 2.6M on the chart (cross-run comparison, derived from page data). The 27-30x over Boost is busy-spin against a mutex and condition-variable queue, not a language effect.
- Open issue #20 (2026-07-05, no maintainer response): build_shared_single_producer defaults to DiscoveryMode::Disabled, which removes backpressure. The producer laps the ring and the consumer silently returns stale payloads from a later lap. The benchmarks opt in with discover_consumer_with_prefix, so they are not affected, but default user code is. Issue #15 adds that FramedTransportProducer::discover_consumers is passive despite its docstring.
- The chart is a single unlabelled run, and its machine, compiler versions and date are not stated. The C/C++ helpers get -march=native -flto while the Rust 'competitive' profile has no target-cpu, and Open MPI is launched with --oversubscribe -n 2 over the vader,self BTLs.

## Known shortcomings

- Chart PNG only with the chart machine and compiler versions unstated, single run; the 27-30x over Boost.Interprocess message_queue is busy-spin vs a blocking mutex/condvar; fairer C peers are Open MPI (2.2-2.5x) and Aeron/rusteron (1.7-1.9x).
- Harness flaw: the raw 1 KB ping-pong moves only a 64-byte header; write_event never writes the 960-byte payload and the client reads only response.sequence, while Boost, Open MPI and rusteron copy 1 KB each way. The like-for-like framed 1 KB path is 2.45M ops/s, about 1.2x Open MPI's 2.0M and below rusteron's 2.6M (cross-run, derived). Open issue #20: the default DiscoveryMode::Disabled drops backpressure, so the producer laps the ring and the consumer silently reads stale data (the benchmark opts out of the default, so its numbers are unaffected).

## Caveats and trade-offs

The win over the C++ peer is a wait-strategy gap, not a language gap. The Boost helper (main.cpp) uses blocking boost::interprocess::message_queue send and receive, which wait on an interprocess mutex and condition variable, while Myelon busy-spins on atomics. The 27x to 30x therefore measures spinning against blocking, and same_algorithm is false. Comparisons against busy-polling peers are smaller: Open MPI's vader shared-memory path is about 2.2x to 2.5x behind, and Aeron IPC, whose rusteron crate is a Rust wrapper over the Aeron C client (not checked here), is about 1.7x to 1.9x behind. The numbers exist only as PNG chart labels; the repo has no results table. Single run, no variance, and the chart's machine, compiler versions and run date are not stated (the README's Ryzen 7 5800X belongs to the perf-bench headline tables). The C/C++ helpers are built with -march=native and the Rust side is not, so flags do not handicap the baseline. The harness is first party. This is an IPC transport rather than a general concurrency runtime, so the category fit is loose. Alpha release (0.1.0-alpha.2), last commit 2026-05-21, 106 commits. [retier] The raw 1 KB ping-pong moves only a 64-byte header (write_event never writes the 960-byte payload; the client reads only response.sequence) while Boost, Open MPI and rusteron copy 1 KB each way. The like-for-like framed 1 KB path is 2.45M ops/s, about 1.2x Open MPI's 2.0M and below rusteron's 2.6M (cross-run). Open issue #20: the default DiscoveryMode::Disabled drops backpressure (the benchmark opts out of the default).

Linux and macOS only. Fixed-size frames chosen at compile time (FixedFrame&lt;N&gt;), consumers busy-spin and burn a core each, and the crate does non-trivial unsafe work internally behind a safe API. Rust only: the README roadmap leaves 'C / C++' unchecked, so a C++ project would need FFI or a separate process. Framing, codecs and typed zero-copy cost throughput: the README's framed 1 KB ping-pong table gives 2.45M ops/s against the chart's 4.4M to 4.9M for the raw ring.

## Maintenance

An alpha (0.1.0-alpha.2) single-maintainer project with 20 stars and a last commit on 2026-05-21, dual MIT OR Apache-2.0. It is fine for Rust-only experiments, but its default producer path can silently corrupt data (issue #20) until that is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness and the C/C++ helpers are public (crates/competitive-bench with third_party/boost_pingpong/main.cpp and its Makefile, plus third_party/ompi_pingpong). The benchmark_url, however, is a PNG chart with no stated machine, no compiler versions and a single unlabelled run. The Ryzen 7 5800X in the README is stated for the perf-bench headline tables, not for this chart. First-party numbers with partial methodology are tier C.
- **Verifier notes:** Downgrade from A to C: the chart has no stated machine or compiler versions and is a single run. The headline 27-30x over Boost.Interprocess message_queue is busy-spin against a blocking mutex/condvar queue, so it is not a Rust-over-C++ result; the fairer C peers (Open MPI vader, Aeron C through rusteron) show about 1.7-2.5x. Metadata checked: MIT OR Apache-2.0, 20 stars, last commit 2026-05-21, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/assets/bench-pingpong-throughput-1kb.png>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/README.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/LICENSE-MIT>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/competitive-bench>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/README.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/Makefile>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/SETUP.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/boost_pingpong/Makefile>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/boost_pingpong/main.cpp>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/ompi_pingpong/Makefile>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/ompi_pingpong/pingpong.c>
  - <https://github.com/Venkat2811/myelon>
  - <https://github.com/Venkat2811/myelon/commits/main>
  - <https://crates.io/api/v1/crates/myelon>
  - <https://crates.io/api/v1/crates/disruptor-mp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/README.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/README.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/Makefile>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/SETUP.md>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/boost_pingpong/main.cpp>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/boost_pingpong/Makefile>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/ompi_pingpong/pingpong.c>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/third_party/ompi_pingpong/Makefile>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/competitive-bench/src/adapters>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/competitive-bench/src/adapters/internal>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/competitive-bench/src/runner>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/src/adapters/mod.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/src/adapters/internal/mod.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/src/runner/dispatch.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/src/runner/executor.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/competitive-bench/src/adapters/rusteron/pingpong.rs>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/perf-bench/src>
  - <https://github.com/Venkat2811/myelon/tree/main/crates/perf-bench/src/bin>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/bin/pingpong.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/layers/raw/myelon/pingpong_shm.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/layers/raw/myelon/mod.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/layers/raw/disruptor_mp/pingpong_shm.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/layers/framed_myelon/frag/pingpong_shm.rs>
  - <https://raw.githubusercontent.com/Venkat2811/myelon/HEAD/crates/perf-bench/src/infra/events.rs>
  - <https://github.com/Venkat2811/myelon/issues>
  - <https://github.com/Venkat2811/myelon/issues/20>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/venkat2811/myelon`) · [data/wave14/enrich/raw/github_com_venkat2811_myelon.json](../../../data/wave14/enrich/raw/github_com_venkat2811_myelon.json) (enrichment confidence 0.7)

</details>
