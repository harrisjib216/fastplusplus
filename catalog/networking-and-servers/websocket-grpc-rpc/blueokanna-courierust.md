# Courierust

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `PolyForm-Perimeter-1.0.1` · 🟢 active

> Zero-dependency Rust HTTP/WebSocket stack; its WebSocket codec encodes small masked frames \~2.5x faster than tungstenite.

| | |
|---|---|
| **Beats** | tokio-tungstenite / tungstenite |
| **Claimed result** | Codec vs tungstenite: 2.3-2.6x faster masked encode at 64B, \~10x faster masked encode at 256KiB, parity at 16KiB. Echo loop 64B: 26.5 us/msg vs 37.2 us/msg for tokio-tungstenite (page: 1.4-1.5x faster at 64B/1KiB; \~29% lower latency, derived from page data). The echo result is a tie with sync tungstenite (26.5 vs 26.5 us). Losses: 9% behind tungstenite at 16KiB echo, 2-3x behind at 256KiB with both ends courierust, and 1.9x slower UTF-8 validation than std::str::from_utf8. |
| **Workload** | WebSocket codec encode/decode (no sockets) and loopback-TCP echo round trips plus one-way push, at 64B-256KiB payloads; single cargo bench --release run in one process on a shared machine (the suite also runs in CI) |
| **Metric** | latency |
| **Hardware** | Windows; exact CPU model not stated |
| **Compiler and flags** | cargo bench --release |
| **Adoption** | 5 stars; benchmark suite runs in CI on every PR/push |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/blueokanna/Courierust) · [benchmark](https://github.com/blueokanna/Courierust/blob/main/benches/WS_BENCHMARK.md) |

## Verdict

WS_BENCHMARK.md reports one `cargo bench` release run (thin LTO, codegen-units=1) on a shared Windows machine with no CPU model or rustc version, against tungstenite 0.30 and tokio-tungstenite 0.30 in the same process: masked encode 15.2 vs 40.0 ns at 64 B, 9.5 vs 90-99 us at 256 KiB and parity at 16 KiB; loopback echo at 64 B is 26.5 us against 37.2 us for tokio-tungstenite (2 worker threads) and 26.5 us for sync tungstenite. The repo's own Linux CI report (commit d7d52b3, complexity bench) shows smaller or reversed codec gaps: 64 B masked encode 32.8 vs 40.8 ns (1.24x) and 256 KiB masked encode 100.0 vs 20.5 us (4.9x slower), in a noisy run.

## Use it when

- WebSocket clients that send many small masked frames (64 B-1 KiB) and where the CPU cost per frame matters: the page shows 15.2 vs 40.0 ns at 64 B and 1.3-1.5x at 1 KiB
- Client uploads of large masked messages where allocation churn matters: courierust allocates 0 bytes per masked frame, while tungstenite allocates a full copy of the payload (1 MiB per 1 MiB message)
- Threaded or blocking Rust programs outside Tokio that need lower small-message latency than tokio-tungstenite: 64 B echo 26.5 vs 37.2 us and 1 KiB echo 26.6 vs 39.0 us, the same as sync tungstenite
- Builds that need a dependency-free or no_std + alloc WebSocket framing core, with strict RFC 6455 validation and incremental UTF-8 checks across fragments
- Programs already on Courierust's HTTP server that need WebSocket on the same port; in the event-driven driver an idle socket costs a poller slot, not a thread

## Skip it when

- Async or Tokio code (axum, hyper, tokio-tungstenite users): there is no Future/Stream API, and the benchmark win against tokio-tungstenite is sync against async, not codec against codec
- Bulk transfers of 256 KiB or more with Courierust at both ends: echo is 297.6 vs 165.0 us for tungstenite, and 16 KiB echo is 9% behind (39.3 vs 35.8 us)
- Any product that could compete with Courierust: PolyForm Perimeter 1.0.1 has a noncompete clause and is not OSI-approved, so many OSS distributions and commercial networking products cannot ship it
- WebSocket over HTTP/2 (RFC 8441) is not implemented. The encoder never uses context takeover, so compression ratio is lower on streams of small repetitive messages
- Risk-averse production: the crate was first published 2026-08-21, has 5 stars, 990 crates.io downloads and no issues filed, and its TLS stack is from scratch with no documented third-party audit. Readiness uses select/poll only, and no epoll/kqueue/io_uring backend is documented

## How it is fast

Masking XORs 16-byte lanes against one precomputed u128 per key phase: 16 is a multiple of the 4-byte key, so every lane starts at the same phase and the loop autovectorizes in safe Rust (25-37 GB/s on the page). The per-byte `i & 3` key lookup does not vectorize. The masked writer masks in place into a reused staging buffer, while tungstenite 0.30's masked `format` allocates and masks a new copy of the payload for every frame. Other techniques: frames up to 64 KiB go out in one write syscall, payloads over 8 KiB are read straight into the message buffer, and the DEFLATE match-finder tables are reused for each message. The echo win over tokio-tungstenite comes from blocking threads against a 2-worker Tokio runtime, not from the codec, because sync tungstenite ties it (26.5 vs 26.5 us at 64 B).

## Compared with alternatives

Among the siblings, uWebSockets (C++) is the WebSocket server to pick for raw server throughput. monoio or ringline are the picks when the Tokio runtime itself is the bottleneck, which is most of the gap measured here against tokio-tungstenite. Pick Courierust only for a dependency-free, blocking Rust WebSocket client or server where masked-encode cost and allocation per frame matter and the PolyForm license is acceptable.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (zero third-party crates; tungstenite, tokio, hyper and other crates appear only in the separate, unpublished benches workspace) |
| **Minimum toolchain** | Rust 1.78 (rust-version), edition 2021; the benches workspace needs a newer stable toolchain |
| **Platforms** | Windows (Winsock select) and POSIX (poll) for the std networking layer; the protocol core is no_std + alloc. Masking is portable safe Rust (u128 lanes, no intrinsics); supported CPU architectures are not documented |
| **Thread safety** | The blocking Session and client WebSocket take &mut self. On the server, push from other threads goes through WsConn::sender() (WsSender) into a bounded send queue. The writer takes one lock per frame, and a shared close flag refuses writes that race a close. The crate root sets #![deny(unsafe_code)] |
| **Drop-in for the baseline** | no |

## Gotchas

- The echo and push benchmarks start the server with `event_driven: false`. The README calls this one-job-per-connection model deprecated for production, so the default event-driven server path was not measured
- On Windows, the client keeps `ClientConfig::read_timeout` (30 s by default) armed as SO_RCVTIMEO. The authors measured this at about 2x slower on 256 KiB bulk transfers; for bulk use, set `read_timeout: None` and rely on ping keepalive
- In the event-driven driver, a bulk push loop inside `on_message` blocks the reactor worker, and the bounded send queue then closes the connection. Push fan-out from another thread with `WsConn::sender()`
- The UTF-8 loss row in WS_BENCHMARK.md (1.9x slower than std) is stale. utf8.rs now hands the bulk scan to core::str::from_utf8, and COMPLEXITY.md reports 891.5 vs 890.3 ns (Windows); the Linux CI report gives a ratio of 1.04

## Known shortcomings

- The repo's own Linux CI run does not reproduce the codec claims: 64 B masked encode only 1.24x (claimed 2.6x) and 256 KiB masked encode 4.9x slower (claimed \~10x faster); headline speedups come from one Windows run. Echo and push benchmarks use the deprecated one-job-per-connection server path (event_driven: false), not the default. The echo win over tokio-tungstenite is sync vs async; sync tungstenite ties it. The UTF-8 loss row is stale (now at parity). The CI has no performance thresholds despite the README. Loses 256 KiB echo (297.6 vs 165.0 us) and 16 KiB echo (9%) to tungstenite. PolyForm Perimeter 1.0.1 licence (noncompete, not OSI) with an extra term. Blocking API only (select/poll), no RFC 8441. First published 2026-08, 5 stars. Filed under WebSocket: it is an HTTP/TLS/gRPC/WebSocket stack, not an event loop.

## Caveats and trade-offs

Licensed under PolyForm Perimeter 1.0.1 (LICENSE file; GitHub reports NOASSERTION), a source-available, non-OSI license. No CPU model or rustc version is given. The echo win is only against async tokio-tungstenite; sync tungstenite ties at 64B/1KiB and wins at 16KiB and 256KiB. The authors note that large-payload numbers varied 3-10x across repeated runs on shared hardware.

One row (UTF-8 validation of streamed text) is \~1.9x slower than std::str::from_utf8, reported honestly.

## Maintenance

Actively developed: last commit 2026-09-15, 1.0.7 on crates.io (main is at 1.0.8) and a CI bench/interop/fuzz suite. Its PolyForm Perimeter 1.0.1 license bars competing products, so treat it as reference code to study unless your use clearly does not compete.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** WS_BENCHMARK.md compares the project against tungstenite 0.30 and tokio-tungstenite 0.30 using public bench code (benches/, `cargo bench --bench ws`). The numbers come from a shared Windows machine with no CPU model or rustc version, so this is first-party evidence with partial methodology.
- **Verifier notes:** All claimed numbers appear in WS_BENCHMARK.md, but the record left out the ties and losses against sync tungstenite; claimed_speedup and caveats now include them. The page's numbers are not CI output: CI (Github_Action_Benchmark.md) runs on an unspecified Linux runner and gives no CPU model. Metadata checked: 5 stars, last commit 2026-09-15, not a fork, not archived.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/blueokanna/Courierust>
  - <https://github.com/blueokanna/Courierust/blob/main/benches/WS_BENCHMARK.md>
  - <https://github.com/blueokanna/Courierust/blob/main/LICENSE>
  - <https://github.com/blueokanna/Courierust/blob/main/Github_Action_Benchmark.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/README.md>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/Cargo.toml>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/benches/WS_BENCHMARK.md>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/benches/COMPLEXITY.md>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/benches/src/ws.rs>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/Github_Action_Benchmark.md>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/LICENSE>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/src/lib.rs>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/src/courierust_ws/README.md>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/src/courierust_ws/mod.rs>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/src/courierust_ws/frame.rs>
  - <https://raw.githubusercontent.com/blueokanna/Courierust/main/src/courierust_ws/utf8.rs>
  - <https://github.com/blueokanna/Courierust/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/courierust>
  - <https://hn.algolia.com/api/v1/search?query=%22courierust%22&typoTolerance=false>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/blueokanna/courierust`) · [data/wave5/enrich/raw/github_com_blueokanna_courierust.json](../../../data/wave5/enrich/raw/github_com_blueokanna_courierust.json) (enrichment confidence 0.45)

</details>
