# sockudo-ws

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust WebSocket library (Tokio/Compio; HTTP/1.1, /2, /3) that self-reports 2-3% higher echo throughput than uWebSockets.

| | |
|---|---|
| **Beats** | uWebSockets |
| **Claimed result** | 1.02x-1.03x higher msg/s than uWebSockets v20.64 across the 4 tested cases (e.g. 232,712 vs 227,973 msg/s at 512B/100 conns; 232,072 vs 224,498 msg/s at 1024B/100 conns; 231,135 vs 222,493 msg/s at 512B/500 conns; 222,578 vs 216,833 msg/s at 1024B/500 conns) |
| **Workload** | Plaintext WebSocket echo server driven by the uSockets load_test client from the denoland/fastwebsockets benches harness. Payloads are 512 and 1024 bytes at 100 and 500 concurrent connections, measured in messages/sec. These cases are not in the published run.js, which uses 20B/100, 1KB/10 and 16KB at 10/200/500, so a locally modified harness was used. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, 32GB RAM, Linux 6.18 |
| **Compiler and flags** | README states Rust 1.82 and uWebSockets v20.64, but the crate has used edition = "2024" (needs Rust &gt;= 1.85) since its initial commit, so the stated toolchain is inconsistent. Build flags for sockudo-ws and the C++ compiler/flags for the uWebSockets EchoServer are not stated for this comparison. The harness load_test.c client is built with clang -flto -O3 per the fastwebsockets benches Makefile. |
| **Adoption** | 219 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/sockudo/sockudo-ws) · [benchmark](https://github.com/sockudo/sockudo-ws#vs-uwebsockets-c) |

## Verdict

The authors ran the uSockets `load_test` client from denoland/fastwebsockets (one C event loop, text echo with one message in flight per connection) on an AMD Ryzen 9 7950X with Linux 6.18. sockudo-ws reached 222-233k msg/s against 217-228k for the uWebSockets v20.64 EchoServer at 512/1024 B and 100/500 connections, 1.02-1.03x. Neither side's compiler or flags are stated, the stated Rust 1.82 cannot build the edition-2024 crate, the sockudo-ws server and the modified cases are unpublished, and the numbers predate v2. Both servers sit near 230k in every case, which suggests (inference, not measured) that the single-threaded load generator is the ceiling.

## Use it when

- Rust services (Tokio or Compio) that terminate many browser or mobile WebSocket connections and want uWS-style corking and pub/sub fan-out without calling C++ through FFI.
- Pipelined or bursty traffic with several messages in flight per connection, if you batch with `feed()` + `flush()`. The project's own harness showed about 2-15x the msg/s of tokio-tungstenite at depth 8-32 with 64-256 B messages (2x on one connection, 15x on 32 connections), but these are historical numbers from the older implicit-coalescing API and have not been re-run.
- You need WebSocket over HTTP/2 Extended CONNECT or over HTTP/3/QUIC behind the same stream API as HTTP/1.1, including several WebSockets multiplexed on one connection.
- Pusher-style realtime backends that need topic pub/sub with sender exclusion and Pusher socket IDs (Sockudo is built on it).
- Replacing tokio-tungstenite in an Axum app when you want permessage-deflate modes with shared or windowed compressors, and keepalive that closes on a missed Pong.

## Skip it when

- Choosing it over uWebSockets for raw throughput. The 2-3% edge is self-reported, cannot be reproduced from published code, and is smaller than the ±5% run-to-run noise the project measured in its own harness.
- Request/response traffic with one message in flight. The project's audit found it level with tokio-tungstenite there (158k vs 154-157k msg/s at 64 B with 8-32 connections), because syscalls and scheduler hops cost more than the codec.
- Connection storms or fan-out to many connections, where the audit says Tokio's work-stealing scheduler, not the codec, is the limit and a thread-per-core runtime wins. On Compio, write coalescing, zero-copy sends and the shared-sink split writer are not implemented.
- Conservative production use. It went from v1.0 to v2.1 in nine months and more breaking changes are waiting in Unreleased. Recent fixes include permessage-deflate stream corruption under context takeover (2.1.0), an O(n·k) UTF-8 re-check that let 4.5 MB of fragmented text pin a core for 30 s (2.0.2), and Pongs never flushed on read-only loops, which got clients dropped (2.0.0).

## How it is fast

It copies uWebSockets' corking: frames collect in a 16 KiB write buffer and go out in one vectored `writev`, and echo replies queued with `feed()` are flushed once per read batch. Server payloads of 8 KiB or more are queued by reference, not copied. Unmasking uses AVX-512/AVX2/SSE2 kernels picked at runtime on x86-64 and an auto-vectorised 64-byte word loop elsewhere. Text is checked by simdutf8 in one incremental pass that fails fast mid-frame, and frames of 125 B or less take a parser fast path whose payloads are `Bytes` views into a 64 KiB receive buffer, with no copy.

## Compared with alternatives

The catalogued siblings (Kitex, rpcx, brpc, SRPC, grpcxx, cmd-stream, Homa, and wtx's gRPC server) are RPC frameworks or transports for service-to-service calls. Pick sockudo-ws when the peer is a browser or any standard WebSocket client and you need pub/sub fan-out on Tokio or Compio. wtx is the nearest Rust sibling and has its own WebSocket implementation, but its catalogued evidence covers gRPC only.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Always: bytes, httparse, http, base64, sha1, simdutf8, socket2, parking_lot, pin-project-lite, futures-core/sink. Default features add tokio + tokio-util, flate2 (zlib-rs backend) + libz-rs-sys, and fastrand. Optional: compio 0.19, h2, quinn/h3/h3-quinn + rustls, tokio-uring, axum/hyper, native-tls or tokio-rustls, ring/aws-lc-rs/openssl/sha1_smol, getrandom/rand, mimalloc. |
| **Minimum toolchain** | Rust edition 2024, so rustc 1.85 or later. No rust-version is declared and CI uses latest stable. The bundled Autobahn run needs Rust 1.88+. The README's 'Rust 1.82' cannot build it. Nightly is needed only for extra SIMD targets and fuzzing. |
| **Platforms** | x86-64 (AVX-512/AVX2/SSE2 masking chosen at runtime; no build-time CPU requirement) and aarch64 (NEON) on stable. CI covers only Linux x86-64 and arm64, and the audit ran on macOS arm64. Windows is not documented. arm, LoongArch, PowerPC and s390x SIMD need nightly, with a portable fallback otherwise. io_uring needs Linux 5.10+. |
| **Thread safety** | One `WebSocketStream` per connection, owned by one task. `split()` gives a reader and a writer that can live in different tasks. The writer shares the transport through `Arc<tokio::sync::Mutex>` with a spawned control-driver task, so the Tokio transport must be `Send + 'static`. `PubSub` is shared across tasks (sharded topics, parking_lot locks). Compio `next()` is not cancellation-safe. |
| **Drop-in for the baseline** | false — uWebSockets is a C++ framework (also behind uWebSockets.js/Bun) that owns the event loop and dispatches to callbacks. sockudo-ws is a Rust crate you drive from Tokio or Compio. Only the concepts carry over: `Config::uws_defaults()`, corking, and uWS/Bun-style pub/sub. |

## Gotchas

- `send()` flushes every frame. To get the batching behind the speed claims, use `feed()` and then `flush()` at batch boundaries. This is a recent contract change in Unreleased. On a unified stream, a write waiting on a slow reader does not advance Pong or idle processing, so one stalled peer can block a sequential fan-out loop.
- The README's 'lock-free split streams, zero mutex contention' is out of date. The split writer now locks an `Arc<tokio::sync::Mutex>` shared with a per-connection driver task spawned by `split()`.
- The `mimalloc` feature sets a `#[global_allocator]` inside the library. That forces mimalloc on your whole binary and clashes with any other global allocator. The `rustls-*` features no longer choose a crypto provider, so you must enable ring or aws-lc-rs on your own rustls dependency.
- The repo builds with `-C target-cpu=native` (.cargo/config.toml) and a fat-LTO, codegen-units=1, panic=abort release profile. Dependents do not inherit these settings, so the published numbers may not match your build. Messages completed through the raw protocol API skip UTF-8 validation, and the repo's benchmark-shaped echo server (`examples/wtx_bench_echo.rs`) uses that path.

## Known shortcomings

- The 1.02-1.03x over uWebSockets is within noise and the comparison code is not public; the stated Rust 1.82 cannot build the crate (edition 2024 needs 1.85+), and the numbers have not changed since the first commit.
- The 1.02-1.03x edge over uWebSockets is inside the project's own +/-5% noise, dates from the initial commit (pre-v2), and the modified 512/1024 B cases and echo server were never published. Both servers sit near 217-233k msg/s in every case, suggesting the single-loop uSockets client is the ceiling. README says Rust 1.82 but edition 2024 needs 1.85+ (Autobahn 1.88+); repo builds use target-cpu=native and fat LTO, which dependents don't inherit. Its own audit shows parity with tokio-tungstenite at one message in flight; the 2-15x wins need feed()/flush() batching and predate the current API. README claims lock-free split streams but the writer uses Arc&lt;tokio::sync::Mutex&gt;. Recently fixed: permessage-deflate corruption (2.1.0), O(n\*k) UTF-8 recheck DoS (2.0.2), unflushed pongs (#8). High API churn; the mimalloc feature sets a global allocator from inside the library.

## Caveats and trade-offs

The margin over uWebSockets is only 2-3%, which is within plausible run-to-run noise for a single-machine run. No repeated runs or variance are reported. The numbers are self-reported and have not changed since the repo's initial commit (2025-12-29), while the library has since gone from v1.x to v2.1.0. The harness is third-party (denoland/fastwebsockets benches), but the sockudo-ws target, its echo server and the modified cases are not published, so the run cannot be reproduced as stated. The environment line (Ryzen 9 7950X, Linux 6.18, Rust 1.82) was added after the numbers. Rust 1.82 cannot compile this edition-2024 crate. No build flags for either side are given.

Rust safety/ergonomics vs uWebSockets' raw C++ API; sockudo-ws is a newer, much less battle-tested library than uWebSockets, which underpins many production Node.js/Bun stacks.

## Maintenance

Actively developed (commits through 2026-09-26; v2.1.0 on crates.io with about 116k downloads; reverse dependencies include the Sockudo server crates and nautilus-network) and MIT-licensed. API churn is high and more breaking changes are waiting, so pin the version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README table matches the record exactly: 232,712 vs 227,973, 232,072 vs 224,498, 231,135 vs 222,493 and 222,578 vs 216,833 msg/s. The run is first-party and not reproducible from public code. The published denoland/fastwebsockets benches/run.js has no sockudo-ws target and none of the 512B/1024B at 100/500-connection cases, so the modified harness and the sockudo-ws echo server used are not published. No build flags are given for sockudo-ws, and no C++ compiler or flags for the uWebSockets EchoServer. The stated Rust 1.82 cannot build the crate, which has used edition 2024 (Rust &gt;= 1.85) since its initial commit.
- **Verifier notes:** The comparison is against uWebSockets v20.64, and the numbers match the README. The tier drops from A to C because the benchmark code for this exact comparison is not public and compiler/flags are missing or inconsistent. Metadata checked: MIT, 219 stars, last commit 2026-09-26, active, not a fork. compared_against_cpp_std_directly=true left as is, since it follows the wave-5 convention of a direct C++ incumbent comparison; uWebSockets is not the C++ standard library.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sockudo/sockudo-ws>
  - <https://github.com/sockudo/sockudo-ws#vs-uwebsockets-c>
  - <https://github.com/sockudo/sockudo-ws/blob/master/Cargo.toml>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/bin/bench.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/docs/PERFORMANCE_AUDIT.md>
  - <https://github.com/sockudo/sockudo-ws/blob/72863fbac331b442b4dcce4e1cddb9da5be86eb7/README.md>
  - <https://github.com/denoland/fastwebsockets/tree/main/benches>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/README.md>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/Makefile>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/run.js>
- **Sources the enricher read:**
  - <https://github.com/sockudo/sockudo-ws>
  - <https://github.com/sockudo/sockudo-ws#vs-uwebsockets-c>
  - <https://github.com/sockudo/sockudo-ws/blob/master/Cargo.toml>
  - <https://github.com/sockudo/sockudo-ws/blob/master/.cargo/config.toml>
  - <https://github.com/sockudo/sockudo-ws/blob/master/.github/workflows/ci.yml>
  - <https://github.com/sockudo/sockudo-ws/blob/master/docs/PERFORMANCE_AUDIT.md>
  - <https://github.com/sockudo/sockudo-ws/blob/master/CHANGELOG.md>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/lib.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/simd.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/cork.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/frame.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/queue.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/stream/websocket.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/src/bin/bench.rs>
  - <https://github.com/sockudo/sockudo-ws/blob/master/examples/wtx_bench_echo.rs>
  - <https://github.com/sockudo/sockudo-ws/issues>
  - <https://github.com/sockudo/sockudo-ws/pulls>
  - <https://github.com/sockudo/sockudo-ws/issues/6>
  - <https://github.com/sockudo/sockudo-ws/issues/8>
  - <https://crates.io/api/v1/crates/sockudo-ws>
  - <https://crates.io/api/v1/crates/sockudo-ws/reverse_dependencies>
  - <https://github.com/sockudo/sockudo>
  - <https://github.com/denoland/fastwebsockets/tree/main/benches>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/README.md>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/run.js>
  - <https://github.com/denoland/fastwebsockets/blob/main/benches/load_test.c>
  - <https://github.com/uNetworking/uWebSockets/blob/master/examples/EchoServer.cpp>
  - <https://github.com/uNetworking/uWebSockets/releases/tag/v20.64.0>
  - <https://github.com/nurmohammed840/web-socket-benchmark>
  - <https://github.com/nurmohammed840/web-socket-benchmark/blob/main/Cargo.toml>
  - <https://github.com/c410-f3r/wtx>
  - https://hn.algolia.com/api/v1/search?query=sockudo&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/search?query=%22sockudo-ws%22>
  - <https://github.com/c410-f3r/wtx/tree/main/wtx/src>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/sockudo/sockudo-ws`) · [data/wave5/enrich/raw/github_com_sockudo_sockudo_ws.json](../../../data/wave5/enrich/raw/github_com_sockudo_sockudo_ws.json) (enrichment confidence 0.8)

</details>
