# nexus-async-rt / nexus-async-web

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Sans-IO, zero-copy async WebSocket/REST library for Tokio; receives small TLS frames 2-3x faster than tokio-tungstenite.

| | |
|---|---|
| **Beats** | tokio-tungstenite (Tokio-based WebSocket library) |
| **Claimed result** | TLS loopback, median of 3 runs on the tls-0.7-refactor branch: nexus-async-web on the Tokio backend + TLS takes 54 ns/msg vs 177 ns/msg for tokio-tungstenite at 40B (\~3.3x) and 134 vs 280 ns/msg at 128B (\~2.1x) (ratios derived from page data). The page's 'Both nexus paths are 3–5× faster' holds only with the blocking nexus-net path (37/86 ns/msg, \~4.8x/\~3.3x derived). There is no nexus-async-rt row in the TLS table. |
| **Workload** | WebSocket message receive throughput over TLS loopback with real syscalls, 40B and 128B payloads, wall-clock ns/msg, client and server pinned to separate physical cores (taskset -c 0,2). The page's rdtscp cycle tables use an in-memory mock transport and do not include tokio-tungstenite. |
| **Metric** | latency |
| **Hardware** | Intel Core Ultra 7 165U (hybrid P+E cores), 2.69GHz base clock, Linux 6.18, taskset-pinned to physical P-cores, turbo on |
| **Compiler and flags** | cargo build --release (workspace edition 2024, MSRV 1.94); rustc version and RUSTFLAGS not stated |
| **Adoption** | 118 stars (nexus workspace) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/Abso1ut3Zer0/nexus) · [benchmark](https://github.com/Abso1ut3Zer0/nexus/blob/main/nexus-async-web/BENCHMARKS.md) |

## Verdict

BENCHMARKS.md (perf_async_ws TLS loopback section, median of 3 runs of 200,000 messages, tls-0.7-refactor branch) reports client-side receive at 54 vs 177 ns/msg at 40B (\~3.3x) and 134 vs 280 ns/msg at 128B (\~2.1x) for nexus-async-web on a current_thread Tokio runtime vs tokio-tungstenite 0.26. Both clients run over tokio-rustls against the same server, which pre-encodes all frames and writes them in one burst; the test ran on a Core Ultra 7 165U, Linux 6.18, turbo on, and rustc 1.94.0 appears only in the workspace README. The page's '3-5x' holds only for the blocking nexus-net path (37/86 ns/msg), whose server runs on its own OS thread, while in both async rows the server task shares one thread with the client.

## Use it when

- A Rust client that consumes high-rate wss:// feeds of small messages (tens to a few hundred bytes), such as exchange market data, where CPU cost per message matters.
- A Tokio application that can adopt the split WsReader/WsWriter API and finish with each borrowed message before the next recv.
- A service that also makes HTTP/1.1 REST calls to the same venue and wants pooled keep-alive connections (ClientPool, or AtomicClientPool across threads) sharing one request writer.
- A small number of long-lived connections, where a 1 MiB read buffer per connection costs nothing that matters.
- A dedicated-thread design that can use the blocking nexus-web/nexus-net client, which the page measures faster still (37/86 ns/msg over TLS).

## Skip it when

- Servers holding thousands of connections: the defaults allocate a 1 MiB read buffer and a 64 KiB write buffer per connection. Both can be shrunk, but no benchmark covers smaller buffers.
- Peers that require permessage-deflate, which nexus-web does not support.
- Code built around tokio-tungstenite's Stream/Sink and owned messages: nexus's WsStream adapter allocates per message, skips the recv-path tuning (max_read_size, compaction), and has no published TLS numbers.
- Production use of the `nexus` backend: nexus-async-rt is marked experimental and not under active development, and its own README says to use Tokio.
- Windows, which the workspace README lists as experimental; the nexus-async-rt backend is Unix-only.

## How it is fast

A single-frame message is parsed in place in a pre-allocated ReadBuf (1 MiB by default) and returned as a borrowed &str or &[u8], so the hot recv path does no per-message heap allocation. Only fragmented frames, or frames that span reads, are copied into a reusable assembly buffer. Unmasking uses SSE2/AVX2 XOR (runtime-detected on x86-64, a u64 scalar loop elsewhere), UTF-8 validation uses simdutf8, and handshake/HTTP parsing uses httparse. The benchmark's baseline loop calls tokio-tungstenite's StreamExt::next, which returns owned Message values, so part of the gap comes from a borrowed API versus an owned one, not from parsing alone; the nexus-async-rt executor plays no part in the cited TLS numbers, which run on Tokio.

## Compared with alternatives

sockudo-ws is the other Rust WebSocket entry and is benchmarked as a server against uWebSockets (\~1.02-1.03x); pick nexus-async-web when you are the client of a few high-rate wss:// feeds on Tokio and want borrowed zero-copy receives plus a REST client built the same way. The RPC siblings (wtx gRPC, brpc, Kitex, rpcx, eRPC) solve a different problem.

## Integration

| | |
|---|---|
| **Form** | crate (nexus-async-web 0.10.0 on crates.io, published 2026-06-02; main has moved on and depends on nexus-net-tokio, which is not on crates.io) |
| **Dependencies** | nexus-web, nexus-net, nexus-pool; tokio (io-util, net, rt, time), futures-core/futures-sink; default TLS via tokio-rustls/rustls with aws-lc-rs; optional socket2, bytes, nexus-async-rt |
| **Minimum toolchain** | Rust 1.94 (edition 2024) |
| **Platforms** | Linux primary, macOS supported, Windows experimental (workspace README); SIMD unmasking on x86-64 (SSE2, AVX2 runtime-detected), scalar fallback on other architectures; nexus backend is Unix-only |
| **Thread safety** | WsReader/WsWriter are per-connection types driven through &mut; Send/Sync guarantees are not documented. ClientPool is single-threaded, AtomicClientPool is thread-safe; nexus-async-rt JoinHandle is !Send. |
| **Drop-in for the baseline** | partial — both run on Tokio and speak RFC 6455 as client or server (517/517 Autobahn cases claimed for nexus-web), but the API is WsReader/WsWriter with borrowed Message instead of Stream&lt;Item = Message&gt;, there is no permessage-deflate, and the Stream/Sink compatibility adapter gives up the zero-copy path |

## Gotchas

- A Message&lt;'_&gt; returned by recv borrows the reader's buffer; convert it to OwnedMessage if you need to keep it past the next recv.
- WsReader::recv returns Ok(None) both on transport EOF and when the read buffer stays full after compaction, so an abnormal peer drop is not an error (open issue #614 tracks the same ambiguity in nexus-web's blocking stream).
- WsStreamBuilder leaves Nagle on by default (nodelay false); call disable_nagle() for latency-sensitive use.
- The tokio-rt and nexus features are mutually exclusive (compile_error!), and the nexus backend needs default-features = false plus an explicit nexus-\* feature.

## Known shortcomings

- The cited numbers are for nexus-async-web (a WebSocket library, running on Tokio) against tokio-tungstenite; the nexus-async-rt event loop is not in that table, so the entry is filed under WebSocket. '3-5x' holds only with the blocking path; the async path is \~3.3x at 40 B and \~2.1x at 128 B. The author marks nexus-async-rt experimental and no longer developed (verifier downgrade).
- Baseline is tokio-tungstenite 0.26 (current 0.30). nexus's borrowed zero-copy recv is compared with tokio-tungstenite's owned StreamExt::next, so part of the gap is API style; the owned WsStream adapter has no TLS numbers. Threading differs by row: async TLS rows run server and client on one current_thread runtime while the blocking row (behind the '3-5x' headline) uses a separate server thread, and the 'separate cores' claim doesn't hold for async rows. Client receive only, pre-encoded burst frames, numbers from a tls-0.7-refactor branch; the crate README gives different figures for the same test. Docs conflict on turbo (off vs on). recv returns Ok(None) both on EOF and on a full buffer (#614); no permessage-deflate; Nagle on by default; 1 MiB + 64 KiB buffers per connection. Published 0.10.0 (2026-06) lags main, which depends on the unpublished nexus-net-tokio.

## Caveats and trade-offs

The cited win is protocol/codec efficiency of nexus-async-web against the tokio-tungstenite library, measured on the Tokio backend, not the nexus-async-rt event loop. Same code on nexus-async-rt vs Tokio is close to parity on the page (p50 recv 64 vs 64 cycles, send 84 vs 96 cycles, in-memory). The nexus-async-rt README says the crate is 'Experimental — not under active development' and recommends Tokio for production. Numbers come from a branch state (tls-0.7-refactor), and the nexus-async-web README gives different TLS loopback figures (34 vs 120 ns at 40B = 3.5x; 81 vs 180 ns at 128B = 2.2x). Turbo was on. No rustc version is stated.

Ships two mutually-exclusive runtime backends (tokio-rt and its own nexus-async-rt); comparison is of a WebSocket/REST protocol layer, not a general-purpose reactor.

## Maintenance

Actively developed (last commit 2026-09-25, 118 workspace stars, \~2.9k crates.io downloads plus \~440 under the old nexus-async-net name) and dual MIT/Apache-2.0; the Tokio backend is the supported path, while the nexus-async-rt backend is experimental and gets no new features.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md is first-party. The bench code is public (nexus-async-web/benches/perf_async_ws.rs, which runs against tokio-tungstenite), and the CPU is stated (Core Ultra 7 165U, taskset-pinned). No rustc version or RUSTFLAGS are given, so this is C, not A.
- **Verifier notes:** The numbers exist, but they belong to the nexus-async-web Tokio backend, not nexus-async-rt, and '3-5x' overstates the async path (128B is \~2.1x). This is really a WebSocket library entry against tokio-tungstenite rather than event-loops-io, so consider recategorizing. The metric is throughput in ns/msg, not latency. License (MIT OR Apache-2.0), last commit 2026-09-25 and 118 stars all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Abso1ut3Zer0/nexus>
  - <https://github.com/Abso1ut3Zer0/nexus/blob/main/nexus-async-web/BENCHMARKS.md>
  - <https://github.com/Abso1ut3Zer0/nexus/blob/main/nexus-async-web/Cargo.toml>
  - <https://github.com/Abso1ut3Zer0/nexus/blob/main/Cargo.toml>
  - <https://github.com/Abso1ut3Zer0/nexus/blob/main/nexus-async-web/benches/perf_async_ws.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-rt/README.md>
- **Sources the enricher read:**
  - <https://github.com/Abso1ut3Zer0/nexus>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/Cargo.toml>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/benches/perf_async_ws.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/src/lib.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/src/ws/mod.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/src/ws/parts.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/src/ws/tokio/mod.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-web/src/ws/tokio/stream.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-async-rt/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-web/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-web/src/ws/mod.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-web/src/ws/frame_reader.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-web/src/ws/mask.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-web/src/ws/handshake.rs>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-net/README.md>
  - <https://raw.githubusercontent.com/Abso1ut3Zer0/nexus/main/nexus-net-tokio/README.md>
  - <https://github.com/Abso1ut3Zer0/nexus/issues?q=websocket>
  - <https://github.com/Abso1ut3Zer0/nexus/issues?q=tls>
  - <https://github.com/Abso1ut3Zer0/nexus/issues?q=tungstenite>
  - <https://github.com/Abso1ut3Zer0/nexus/issues?q=bench>
  - <https://github.com/Abso1ut3Zer0/nexus/issues/614>
  - <https://crates.io/api/v1/crates/nexus-async-web>
  - <https://crates.io/api/v1/crates/nexus-async-net>
  - <https://crates.io/api/v1/crates/nexus-web>
  - <https://crates.io/api/v1/crates/nexus-net>
  - <https://crates.io/api/v1/crates/nexus-net-tokio>
  - <https://crates.io/api/v1/crates/tokio-tungstenite>
  - <https://hn.algolia.com/api/v1/search?query=nexus-async-web>
  - <https://hn.algolia.com/api/v1/search?query=Abso1ut3Zer0>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/abso1ut3zer0/nexus`) · [data/wave5/enrich/raw/github_com_abso1ut3zer0_nexus.json](../../../data/wave5/enrich/raw/github_com_abso1ut3zer0_nexus.json) (enrichment confidence 0.75)

</details>
