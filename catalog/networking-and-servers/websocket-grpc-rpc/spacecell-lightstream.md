# Lightstream

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust/Python Arrow-table transport over raw TCP, QUIC, HTTP/2 and WebSocket; 1.06-1.71x Arrow Flight throughput between AWS hosts.

| | |
|---|---|
| **Beats** | Apache Arrow Flight (gRPC/HTTP2) |
| **Claimed result** | Warm-median throughput (median of 5 runs, GiB/s) is 1.06x-1.71x Arrow Flight in all 16 cells (4 schema shapes x 1/4/8/16 streams). For example, numeric with 1 stream: 1.109 vs 0.649 GiB/s (1.71x); numeric with 16 streams: 5.780 vs 5.434 (1.06x); string-heavy with 1 stream: 1.109 vs 0.828 (1.34x). The gap narrows toward the 50 Gbit/s link limit as stream count rises. No numeric latency comparison is given in text, only the claim that p99 is within 1% of p50. |
| **Workload** | Streaming RAM-resident Apache Arrow tables (numeric, mixed, string-heavy, wide schemas; 1M rows/batch from a 300GB pool) between two AWS instances over a 50 Gbit/s network, across multiple levels of connection parallelism |
| **Metric** | throughput, latency |
| **Hardware** | 2x AWS i3en.12xlarge instances in one placement group, 50 Gbit/s network |
| **Compiler and flags** | Rust nightly (rustlang/rust:nightly-bookworm-slim Docker image, version not pinned), cargo build --release, features bench_arrow_flight,protocol,tcp,mmap (rust/benches/ecs/Dockerfile) |
| **Adoption** | 41 stars; very new project |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/SpaceCell/lightstream) · [benchmark](https://github.com/SpaceCell/lightstream/blob/main/rust/README.md) |

## Verdict

The project's own ECS rig ran 2x AWS i3en.12xlarge in one cluster placement group (50 Gbit/s): RAM-resident 1M-row tables in 4 shapes, warm median of 5 runs, Lightstream's parallel protocol over plaintext TCP vs arrow-flight 59.2 DoGet over tonic/HTTP/2 (8 MiB windows, default 2 MiB slicing, dictionary Resend), built with unpinned Rust nightly --release. Lightstream led in all 16 cells by 1.06x-1.71x, but its 1-stream cells (1.108-1.109 GiB/s, about 9.5 Gbit/s) sit at AWS's \~10 Gbps per-flow cap and its 16-stream cells (5.75-5.79 GiB/s, about 49.4-49.7 Gbit/s) sit at the link limit, so the ratios mostly show how far Flight falls short of the network ceiling; Lightstream's timing also includes a global reorder that Flight does not do.

## Use it when

- Bulk transfer of multi-MiB Arrow batches between Rust or Python services on a LAN/cluster, especially over one connection, where the published gain is largest (1.18x-1.71x at 1 stream).
- You need one globally ordered table stream spread across several parallel TCP connections and do not want to write the merge yourself.
- You want Arrow tables and typed Protobuf/MessagePack side messages on the same connection instead of hand-rolled adjacent-bytes framing.
- You want one API to swap between TCP, UDS, QUIC, WebSocket, HTTP/2, stdio, Arrow IPC/Parquet files and mmap, and can build on nightly Rust or use the Python wheels.

## Skip it when

- You need Flight ecosystem interop (Flight SQL, DoPut/DoExchange, existing Flight clients/servers, GetFlightInfo endpoint discovery); Lightstream is not wire-compatible with Flight.
- Your build must use stable Rust: the crate needs nightly (allocator_api, portable_simd via minarrow/vec64), and rust-toolchain.toml pins only channel = "nightly", no date.
- The link is already the bottleneck: at 8-16 streams the published lead shrinks to 1.06x-1.26x, because both systems approach the 50 Gbit/s limit.
- Small request/response RPC or general service APIs; this is a bulk columnar transport, not an RPC framework.
- Production-critical paths that need a mature project: one maintainer, 41 stars, 0 issues ever filed, versions 0.1-0.4.x yanked on crates.io, and 0.7.0 cannot read Parquet files with nulls written by earlier releases.

## How it is fast

Each table goes on the wire as Arrow IPC inside a 5-byte TLV frame ([u8 tag][u32 LE length]) directly over TCP, skipping gRPC/HTTP/2 framing, protobuf FlightData wrapping and arrow-flight's default 2 MiB batch slicing. Buffers are minarrow 64-byte-aligned Vec64, and the receive path reads socket bytes straight into decoder-managed buffers from a reused per-stream arena, so steady-state decode does no per-batch allocation (per source comments). Parallel mode opens one TCP connection per stream, feeds them round-robin through bounded tokio channels (depth 8), decodes each connection on its own task, and restores global order by pulling connections in the same rotation, with no sort. The project publishes no profile that attributes the gain to any one of these parts.

## Compared with alternatives

The catalogued siblings (DRPC, fRPC, brpc, rpcx, cmd-stream) are general RPC frameworks benchmarked on small-message QPS against gRPC, and none carries Arrow tables natively. Pick Lightstream when the payload is bulk Arrow columnar data or you need ordered multi-connection streaming; pick DRPC, fRPC or brpc for many small request/response calls.

## Integration

| | |
|---|---|
| **Form** | crate (also Python package lightstream-io) |
| **Dependencies** | tokio, futures-\*, flatbuffers, minarrow 0.18, vec64, tracing, log; optional per feature: quinn, h2/http/bytes, tokio-tungstenite, wtransport, tokio-rustls (ring), prost, rmp-serde, zstd, snap, simd-json, tokio-uring |
| **Minimum toolchain** | Rust nightly (edition 2024; unpinned nightly channel); no stable MSRV. Python &gt;=3.9 for the wheels. |
| **Platforms** | CI runs Linux x86-64, macOS x86-64/arm64 and Windows x86-64 (Windows without uds/mmap); io_uring and vmap64 are Linux-only; PyPI also ships manylinux aarch64 wheels. Published benchmarks are Linux x86-64 only. |
| **Thread safety** | not documented; readers/writers are single-owner async objects driven with &mut self, and the parallel reader/writer spawn one tokio task per connection |
| **Drop-in for the baseline** | no |

## Gotchas

- Ordered mode stalls on the slowest connection: a lagging stream holds back every table behind it (documented on SortBehaviour::Ordered), with 8 buffered frames per connection.
- LightstreamParallelWriter caps at 256 connections (each connection announces its index as one byte), and each frame's payload length is a u32, so a single frame must stay under 4 GiB; split big tables into views.
- Each streaming decoder reserves 2 GiB of virtual address space (tunable via LIGHTSTREAM_ARENA_CAPACITY); many parallel streams add up under strict overcommit or ulimit -v.
- LightstreamParallelWriter::connect opens plain TcpStreams from a SocketAddr, and that file has no TLS variant; TLS exists on the single-connection TCP/WebSocket/HTTP/2 writers (tls feature) and in QUIC. The Rust README's 'cargo install lightstream' is wrong for a library crate; use cargo add.

## Known shortcomings

- Lightstream's results sit at the network ceilings (1 stream \~9.5 Gbit/s = AWS per-flow cap; 16 streams \~49.5 Gbit/s = the 50 Gbit/s link), so the ratios mostly show how far Flight falls short of the link; no CPU-per-byte data. Framing differs: run.sh defaults to 8 MiB batches (its header comment says 0) while Flight slices at 2 MiB; the table doesn't say which was used. The benchmark image patches minarrow to a sibling checkout and uses an unpinned nightly. Lightstream pays for a global reorder Flight doesn't; latency chart is single-stream only. Nightly-only (allocator_api, portable_simd). Not a Flight drop-in: minarrow Table API, no Flight wire compatibility, parallel writer is plaintext TCP only (max 256 connections, u32 frames, 2 GiB virtual reservation per decoder). One maintainer, 41 stars, 938 downloads, 0.1-0.4 yanked; 0.7.0 can't read back Parquet-with-nulls from earlier releases. Doc errors (missing benchmarks/ path, 'cargo install' for a library).

## Caveats and trade-offs

Baseline is Arrow Flight (the arrow-flight crate over gRPC/HTTP2), not bare gRPC, so this is a proxy comparison. First-party benchmark; the code is in rust/benches/ecs/. The README says 'see benchmarks/', but that root path does not exist. The CPU model is not stated (only the i3en.12xlarge instance type) and the nightly toolchain is not pinned. Gains shrink to 1.06x-1.17x at 16 streams, where both approach the 50 Gbit/s link. Lightstream's timing includes global ordered reconstruction, which Flight does not do. The project is very new and has no independent reproduction.

Purpose-built for bulk columnar Arrow-table transport, not a general RPC replacement; Lightstream reconstructs one globally-ordered stream across parallel connections, a cost the README says it 'wears' in its own reported numbers, while Arrow Flight orders only per-endpoint

## Maintenance

Active (v0.7.0 released 2026-09-19; one maintainer, 7 self-merged PRs, 0 issues) and MPL-2.0 with file-level copyleft, so it is fine to link as a dependency, but it is pre-1.0, nightly-only and still making format-breaking changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party results (a table image in rust/README.md) from the project's own cross-host benchmark code (rust/benches/ecs/source.rs, sink.rs, Dockerfile). The CPU model is not stated (only the AWS i3en.12xlarge instance type), and the compiler is an unpinned Rust nightly image with --release. It is not peer-reviewed or independent, so it is C, not B.
- **Verifier notes:** Numbers come from the full-results-table.png image embedded in rust/README.md; every cell shows a Lightstream lead but the margins are modest (1.06x-1.71x). Metadata was checked via github.com HTML and the commits atom feed because the API was rate-limited: 41 stars, last commit 2026-09-19, not archived, not a fork, LICENSE is MPL-2.0.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SpaceCell/lightstream>
  - <https://github.com/SpaceCell/lightstream/blob/main/rust/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/LICENSE>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/assets/full-results-table.png>
  - <https://github.com/SpaceCell/lightstream/tree/main/rust>
  - <https://github.com/SpaceCell/lightstream/tree/main/rust/benches>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/README.md>
  - <https://github.com/SpaceCell/lightstream/tree/main/rust/benches/ecs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/Dockerfile>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/rust-toolchain.toml>
  - <https://github.com/SpaceCell/lightstream/commits.atom>
- **Sources the enricher read:**
  - <https://github.com/SpaceCell/lightstream>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/writers/parallel/lightstream.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/readers/parallel/lightstream.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/writers/tcp.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/sinks/table_sink.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/streams/tcp.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/models/frames/lightstream_message.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/src/traits/parallel_transport_reader.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/Dockerfile>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/run.sh>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/source.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/ecs/sink.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/rust/benches/common/arrow_flight_bench.rs>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/python/README.md>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/assets/full-results-table.png>
  - <https://raw.githubusercontent.com/SpaceCell/lightstream/main/assets/delivery-consistency.png>
  - <https://crates.io/api/v1/crates/lightstream>
  - <https://pypi.org/pypi/lightstream-io/json>
  - <https://docs.rs/crate/lightstream/latest>
  - <https://docs.rs/crate/lightstream/latest/status.json>
  - <https://hn.algolia.com/api/v1/search?query=lightstream%20arrow&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=lightstream>
  - <https://hn.algolia.com/api/v1/search?query=spacecell>
  - <https://hn.algolia.com/api/v1/search?query=minarrow>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/spacecell/lightstream`) · [data/wave5/enrich/raw/github_com_spacecell_lightstream.json](../../../data/wave5/enrich/raw/github_com_spacecell_lightstream.json) (enrichment confidence 0.6)

</details>
